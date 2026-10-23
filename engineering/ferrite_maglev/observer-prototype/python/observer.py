"""By-value binding to the standalone offline Rust observer; no device access.

Building/loading a library is explicit. State advances only after Rust success.
The caller owns the authenticated configuration, virtual clock and accepted
sample provenance; identity bytes are consistency checks, not authentication.
"""
from __future__ import annotations

import ctypes as C
from pathlib import Path

CARS, MODULES, MAX_GROUPS = 6, 24, 200
STEP_NS = 1_000_000
CarValues = C.c_double * CARS
ModuleValues = C.c_double * MODULES
Support = ModuleValues * CARS
Wrench = (C.c_double * 3) * CARS
Digest = C.c_uint8 * 32


class Config(C.Structure):
    _fields_ = [('abi_version', C.c_uint32), ('groups', C.c_uint32),
                ('configuration_sha256', Digest), ('wave_number_rad_per_m', C.c_double),
                ('estimator_scale', C.c_double), ('step_ns', C.c_uint64)]


class State(C.Structure):
    _fields_ = [('initialized', C.c_uint32), ('reserved', C.c_uint32),
                ('last_sequence', C.c_uint64), ('last_timestamp_ns', C.c_uint64), ('config', Config)]


class Group(C.Structure):
    _fields_ = [('flux_linkage_wb', CarValues), ('phase_rad', CarValues),
                ('normal_position_m', CarValues), ('current_alpha_a', C.c_double),
                ('current_beta_a', C.c_double)]


class Frame(C.Structure):
    _fields_ = [('sequence', C.c_uint64), ('timestamp_ns', C.c_uint64),
                ('sample_present', C.c_uint32), ('sample_groups', C.c_uint32),
                ('sample_sequence', C.c_uint64), ('sample_timestamp_ns', C.c_uint64),
                ('sample_configuration_sha256', Digest), ('speed_m_s', CarValues),
                ('centres_m', CarValues), ('groups', Group * MAX_GROUPS), ('desired_support_n', Support)]


class Input(C.Structure):
    _fields_ = [('config', Config), ('state', State), ('frame', Frame)]


class Output(C.Structure):
    _fields_ = [('status', C.c_uint32), ('physical_output_authorised', C.c_uint32), ('next_state', State),
                ('raw_wrench_up_roll_pitch', Wrench), ('scaled_wrench_up_roll_pitch', Wrench),
                ('correction_n', Support), ('requested_support_n', Support),
                ('maximum_abs_correction_n', C.c_double)]


STATUS = ('ok', 'invalid configuration', 'invalid state', 'sequence', 'clock', 'missing sample',
          'unexpected startup sample', 'configuration identity', 'sample sequence', 'sample age',
          'group count', 'nonfinite input', 'negative flux amplitude', 'arithmetic', 'support bounds')


class ObserverRefusal(ValueError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"Rust observer hold {status}: {STATUS[status] if status < len(STATUS) else 'unknown status'}")


def digest(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('configuration identity requires 64 lowercase hexadecimal characters')
    return Digest(*bytes.fromhex(value))


def uint64(value):
    # ctypes otherwise silently wraps negative or oversized Python integers.
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 2**64-1:
        raise ValueError('sequence and virtual time require unsigned 64-bit integers')
    return value


def row(value, size):
    if len(value) != size:
        raise ValueError(f'exactly {size} channels required')
    return [float(v) for v in value]


def matrix(value, rows, cols):
    if len(value) != rows:
        raise ValueError(f'exactly {rows} rows required')
    return [row(r, cols) for r in value]


class Observer:
    """Pure offline candidate computation with explicit delayed observation.

    ``step(..., sample=None)`` is permitted only for sequence 1. Subsequent
    ``sample`` is the Python reference tuple ``(fields, speed, currents, centres)``.
    Its exact prior sequence/time/config identity must be supplied separately.
    Every successful output still has physical_output_authorised == 0.
    """

    def __init__(self, library, configuration_sha256, groups, wave_number_rad_per_m, estimator_scale=1.0):
        if not isinstance(groups, int) or isinstance(groups, bool) or not 1 <= groups <= MAX_GROUPS:
            raise ValueError('bounded group count 1..200 required')
        self.library = C.CDLL(str(Path(library).resolve()))
        self.function = self.library.osr_research_normal_wrench_v1
        self.function.argtypes, self.function.restype = [Input], Output
        self.config = Config(1, groups, digest(configuration_sha256), wave_number_rad_per_m, estimator_scale, STEP_NS)
        self.state = State()

    def step(self, sequence, timestamp_ns, desired_support_n, sample=None, *,
             sample_sequence=None, sample_timestamp_ns=None, sample_configuration_sha256=None):
        request = Input(self.config, self.state, Frame())
        request.frame.sequence, request.frame.timestamp_ns = uint64(sequence), uint64(timestamp_ns)
        request.frame.desired_support_n = Support(*(ModuleValues(*r) for r in matrix(desired_support_n, CARS, MODULES)))
        if sample is not None:
            if len(sample) != 4:
                raise ValueError('sample requires fields, speed, alpha/beta currents and car centres')
            fields, speed, currents, centres = sample
            count = self.config.groups
            psi = matrix(fields['psi'], count, CARS)
            theta = matrix(fields['theta'], count, CARS)
            positions = matrix(fields['normal_positions_m'], count, CARS)
            currents = matrix(currents, count, 2)
            request.frame.sample_present, request.frame.sample_groups = 1, count
            request.frame.sample_sequence = uint64(sample_sequence)
            request.frame.sample_timestamp_ns = uint64(sample_timestamp_ns)
            request.frame.sample_configuration_sha256 = digest(sample_configuration_sha256)
            request.frame.speed_m_s, request.frame.centres_m = CarValues(*row(speed, CARS)), CarValues(*row(centres, CARS))
            for i in range(count):
                request.frame.groups[i] = Group(CarValues(*psi[i]), CarValues(*theta[i]), CarValues(*positions[i]), *currents[i])
        elif any(x is not None for x in (sample_sequence, sample_timestamp_ns, sample_configuration_sha256)):
            raise ValueError('metadata without a sample is ambiguous')
        result = self.function(request)
        if result.status:
            raise ObserverRefusal(result.status)
        if result.physical_output_authorised != 0:
            raise RuntimeError('offline observer ABI must never authorise hardware output')
        self.state = result.next_state
        return result
