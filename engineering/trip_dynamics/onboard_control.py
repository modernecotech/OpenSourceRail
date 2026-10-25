"""Actual existing Rust current-loop ABI, without invented magnetic forces."""
import ctypes as C
from hashlib import sha256
import math
from pathlib import Path
import subprocess

from engineering.design_search.contracts import identity

from engineering.ferrite_maglev.full_dynamics import ElectricalInput, ElectricalOutput, F2, F4


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def build_current_kernel(root):
    root = Path(root).resolve()
    kernel = root/'engineering/ferrite_maglev/full-dynamics-kernel'
    paths = [kernel/'Cargo.toml', kernel/'Cargo.lock', *kernel.glob('src/*.rs'),
             root/'Cargo.toml', root/'Cargo.lock', root/'rust-toolchain.toml',
             root/'engineering/ferrite_maglev/full_dynamics.py',
             root/'crates/osr-maglev-control/Cargo.toml',
             *(root/'crates/osr-maglev-control/src').glob('*.rs')]
    before = {p.relative_to(root).as_posix(): file_hash(p) for p in paths}
    target = root/'build/trip-dynamics/rust'
    command = ['cargo', 'build', '--locked', '--release', '--manifest-path', str(kernel/'Cargo.toml'),
               '--target-dir', str(target)]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise RuntimeError('Rust current kernel failed: '+result.stderr[-4000:])
    if before != {p.relative_to(root).as_posix(): file_hash(p) for p in paths}:
        raise ValueError('current-controller source changed during compilation')
    binary = target/'release/libosr_full_dynamics_kernel.so'
    return binary, dict(command=command, exit_code=0, source_sha256=before,
                        binary_sha256=file_hash(binary), compiler=subprocess.check_output(['rustc', '--version'], text=True).strip(),
                        stdout=result.stdout, stderr=result.stderr, physical_output_authorised=False)


class CurrentLoop:
    """Two electrical ports on one local support module; no force extrapolation."""
    def __init__(self, binary, candidate_id, *, resistance_ohm=(2., 2.), inductance_H=(.02, 0., 0., .02),
                 ambient_C=20., bus_V=100., current_limit_A=60., copper_mass_kg=(1., 1.),
                 cooling_W_K=(0., 0.), mechanical_step_s=.001):
        if not isinstance(candidate_id, str) or len(candidate_id) != 64 or candidate_id == '0'*64:
            raise ValueError('nonzero physical candidate SHA256 required')
        configuration = bytes.fromhex(candidate_id)
        if len(resistance_ohm) != 2 or len(inductance_H) != 4 or len(copper_mass_kg) != 2 or len(cooling_W_K) != 2:
            raise ValueError('two winding ports and 2x2 incremental inductance required')
        positive = [*resistance_ohm, *copper_mass_kg, bus_V, current_limit_A, inductance_H[0], inductance_H[3]]
        if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in positive):
            raise ValueError('positive finite winding parameters required')
        if any(not math.isfinite(x) for x in inductance_H) or abs(inductance_H[1]-inductance_H[2]) > 1e-12 or inductance_H[0]*inductance_H[3] <= inductance_H[1]**2:
            raise ValueError('symmetric positive definite incremental inductance required')
        if any(not math.isfinite(x) or x < 0 for x in cooling_W_K) or not math.isfinite(ambient_C):
            raise ValueError('finite thermal parameters required')
        ticks = round(mechanical_step_s/.00005)
        if not 1 <= ticks <= 100 or abs(ticks*.00005-mechanical_step_s) > 1e-12:
            raise ValueError('mechanical period must contain 1–100 exact 50us current ticks')
        self.lib = C.CDLL(str(binary))
        self.fn = self.lib.osr_full_dynamics_electrical_v1
        self.fn.argtypes = [ElectricalInput]; self.fn.restype = ElectricalOutput
        self.input = i = ElectricalInput()
        i.configuration = (C.c_uint8*32)(*configuration)
        i.step_ns = 50000; i.substeps = ticks; i.count = 1
        i.primary_bus_v = i.reserve_bus_v = bus_V
        i.maximum_current_a = current_limit_A
        i.kp_v_per_a = 10.; i.ki_v_per_a_s = 200.
        i.maximum_temperature_c = 120.; i.ambient_c = ambient_C
        i.copper_cp_j_kg_k = 385.; i.reserve_efficiency = .9
        m = i.modules[0]
        m.resistance_ohm = F2(*resistance_ohm); m.inductance_h = F4(*inductance_H)
        m.copper_mass_kg = F2(*copper_mass_kg); m.cooling_w_k = F2(*cooling_W_K)
        m.temperature_c = F2(ambient_C, ambient_C)
        self.sequence = 1

    def step(self, target_A, *, emf_V=(0., 0.), faults=0):
        if len(target_A) != 2 or len(emf_V) != 2 or any(not math.isfinite(v) for v in [*target_A, *emf_V]):
            raise ValueError('finite two-port current demand and motional EMF required')
        if type(faults) is not int or not 0 <= faults <= 1023:
            raise ValueError('declared existing fault bitmask required')
        i = self.input; i.first_sequence = self.sequence
        i.modules[0].primary_target_a = F2(*target_A)
        i.modules[0].reserve_target_a = F2(0., 0.)
        i.modules[0].motional_emf_v = F2(*emf_V)
        i.modules[0].faults = faults
        out = self.fn(i)
        if out.status or out.physical_output_authorised:
            raise ValueError('current kernel refused frame or asserted hardware output: '+str(out.status))
        self.sequence += i.substeps
        i.modules = out.modules
        m = out.modules[0]
        return dict(current_A=list(m.current_a), temperature_C=list(m.temperature_c),
                    applied_voltage_V=list(out.last_voltage_v[0]),
                    dc_input_J=out.primary_dc_j+out.reserve_dc_j, copper_heat_J=out.copper_heat_j,
                    emf_work_J=out.emf_work_j, magnetic_field_change_J=out.field_change_j,
                    rejected_heat_J=out.rejected_cooling_j, maximum_RL_residual_J=out.maximum_rl_residual_j,
                    primary_fault_channels=out.primary_fault_channels,
                    reserve_used_channels=out.reserve_used_channels,
                    physical_output_authorised=False)


def current_fixture(binary):
    definition = dict(schema='osr-synthetic-current-coupon/1', resistance_ohm=[2.,2.],
                      inductance_H=[.02,0.,0.,.02], ambient_C=20., bus_V=100., current_limit_A=60.,
                      copper_mass_kg=[1.,1.], cooling_W_K=[0.,0.], mechanical_step_s=.001,
                      current_step_s=.00005, target_A=[10.,0.], healthy_steps=100, sensor_loss_fault_mask=2)
    fixture_id = identity(definition)
    loop = CurrentLoop(binary, fixture_id)
    rows = [loop.step((10., 0.)) for _ in range(100)]
    fault = loop.step((10., 0.), faults=2)
    peak = max(abs(x) for r in rows for x in r['current_A'])
    if not 0 < rows[0]['current_A'][0] < rows[-1]['current_A'][0] < 10.5:
        raise ValueError('Rust current fixture did not establish bounded rising current')
    if not fault['primary_fault_channels']:
        raise ValueError('Rust sensor-loss refusal did not execute')
    return dict(schema='osr-trip-rust-current-fixture/1', execution='executed', numerical_check='pass',
                fixture_configuration_id=fixture_id, fixture_definition=definition,
                scope='Two-winding constant-R/L electrical fixture; no candidate magnetic-force or vehicle motion credit',
                mechanical_step_s=.001, current_step_s=.00005, steps=100, peak_current_A=peak,
                final=rows[-1], sensor_loss=fault,
                maximum_RL_residual_J=max(r['maximum_RL_residual_J'] for r in rows),
                summed_dc_input_J=sum(r['dc_input_J'] for r in rows),
                summed_copper_heat_J=sum(r['copper_heat_J'] for r in rows),
                summed_field_change_J=sum(r['magnetic_field_change_J'] for r in rows),
                force_map_coupled=False, physical_output_authorised=False)
