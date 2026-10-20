"""Two-way numerical beam/rigid-car/Rust-control demonstrator.

Assumed Euler-Bernoulli concrete beam and ideal instantaneous force channels;
not a magnetic map, qualified structure, real-time plant or stability certificate.
Run the release Rust bridge first as documented by --help. Only incremental
car magnetic reaction loading is modelled, not beam dead load or its camber.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from hashlib import sha256
import os
import platform
import tempfile
import math
from pathlib import Path
import selectors
import subprocess

import numpy as np
import scipy
from scipy.linalg import eigh, expm

ROOT = Path(__file__).resolve().parents[2]
MODULE_X_M = np.repeat(np.arange(-5.5, 6.0, 1.0), 2)
MODULE_Y_M = np.tile([-0.88, 0.88], 12)
MODULES = 24
DT_S = 0.001


@dataclass(frozen=True)
class BeamAssumptions:
    young_pa: float = 30e9
    second_moment_m4: float = 0.193624
    span_m: float = 25.0
    # 0.660 m² concrete at an ASSUMED 2500 kg/m³, plus ASSUMED 100 kg/m
    # magnetic interfaces. This is a dynamic line-mass hypothesis, not an MBOM.
    line_mass_kg_m: float = 1750.0
    elements: int = 50
    retained_modes: int = 6
    damping_ratio: float = 0.02

    def validate(self) -> None:
        values = (self.young_pa, self.second_moment_m4, self.span_m, self.line_mass_kg_m)
        if not all(math.isfinite(v) and 1e-6 <= v <= 1e12 for v in values):
            raise ValueError("finite positive numerically bounded beam assumptions required")
        if type(self.elements) is not int or type(self.retained_modes) is not int:
            raise ValueError("integer mesh and modal count required")
        if not (4 <= self.elements <= 200 and 1 <= self.retained_modes <= 12):
            raise ValueError("bounded mesh and modal count required")
        if self.retained_modes >= 2*self.elements:
            raise ValueError("modal count exceeds free degrees of freedom")
        if not math.isfinite(self.damping_ratio) or not 0 <= self.damping_ratio <= 0.2:
            raise ValueError("damping assumption must be between zero and 0.2")
        if self.span_m <= 12:
            raise ValueError("span must contain the 12 m module footprint")


def point_load_deflection(x_m: np.ndarray, load_x_m: float, load_n: float,
                          assumptions: BeamAssumptions) -> np.ndarray:
    """Independent simply-supported point-load formula, positive down (m)."""
    assumptions.validate()
    x = np.asarray(x_m, dtype=float)
    length = assumptions.span_m
    if (not np.all(np.isfinite(x)) or np.any(x < 0) or np.any(x > length)
            or not math.isfinite(load_x_m) or not 0 <= load_x_m <= length
            or not math.isfinite(load_n)):
        raise ValueError("point load and query coordinates must be finite on span")
    a, b = load_x_m, length-load_x_m
    factor = load_n/(6*length*assumptions.young_pa*assumptions.second_moment_m4)
    return np.where(x <= a, factor*b*x*(length**2-b*b-x*x),
                    factor*a*(length-x)*(length**2-a*a-(length-x)**2))


class FlexibleGuideway:
    """Pinned Euler-Bernoulli FE beam, consistent mass, mass-normal modes.

    One shared vertical beam displacement serves both y rows. The 1.76 m force
    separation is used by car roll dynamics; guideway roll is constrained and
    its reaction torque is not dynamically resolved. Beam torsion, corbels, lateral
    bending, flexible car structure and individual reaction-surface flexibility
    are absent. Node rotations and slopes are small-angle quantities.
    """
    def __init__(self, assumptions: BeamAssumptions = BeamAssumptions()):
        assumptions.validate()
        self.assumptions = assumptions
        n = assumptions.elements
        length = assumptions.span_m/n
        self.nodes_m = np.linspace(0, assumptions.span_m, n+1)
        self.module_positions_m = assumptions.span_m/2+MODULE_X_M
        size = 2*(n+1)
        stiffness = np.zeros((size, size))
        mass = np.zeros_like(stiffness)
        k = assumptions.young_pa*assumptions.second_moment_m4/length**3*np.array([
            [12, 6*length, -12, 6*length],
            [6*length, 4*length**2, -6*length, 2*length**2],
            [-12, -6*length, 12, -6*length],
            [6*length, 2*length**2, -6*length, 4*length**2]])
        m = assumptions.line_mass_kg_m*length/420*np.array([
            [156, 22*length, 54, -13*length],
            [22*length, 4*length**2, 13*length, -3*length**2],
            [54, 13*length, 156, -22*length],
            [-13*length, -3*length**2, -22*length, 4*length**2]])
        for e in range(n):
            indices = np.arange(2*e, 2*e+4)
            stiffness[np.ix_(indices, indices)] += k
            mass[np.ix_(indices, indices)] += m
        # Displacements pinned at both ends; rotations remain free.
        self.free = np.delete(np.arange(size), [0, 2*n])
        self.stiffness = stiffness[np.ix_(self.free, self.free)]
        self.mass = mass[np.ix_(self.free, self.free)]
        self.local_shape = self.shape(self.module_positions_m)
        eigenvalues, self.phi = eigh(self.stiffness, self.mass,
                                    subset_by_index=[0, assumptions.retained_modes-1])
        self.omega_rad_s = np.sqrt(eigenvalues)
        self.local_modes = self.local_shape@self.phi
        self.q = np.zeros(assumptions.retained_modes)
        self.velocity = np.zeros_like(self.q)
        transitions, drives = [], []
        for omega in self.omega_rad_s:
            a = np.array([[0.0, 1.0], [-omega**2, -2*assumptions.damping_ratio*omega]])
            transition = expm(a*DT_S)
            transitions.append(transition)
            drives.append(np.linalg.solve(a, (transition-np.eye(2))@np.array([0.0, 1.0])))
        self.transition = np.asarray(transitions)
        self.drive = np.asarray(drives)

    def shape(self, x_m: np.ndarray) -> np.ndarray:
        """Cubic Hermite interpolation; transpose transfers point reaction loads."""
        x = np.asarray(x_m, dtype=float).reshape(-1)
        if not np.all(np.isfinite(x)) or np.any(x < 0) or np.any(x > self.assumptions.span_m):
            raise ValueError("evaluation coordinates must be on span")
        length = self.assumptions.span_m/self.assumptions.elements
        full = np.zeros((len(x), 2*(self.assumptions.elements+1)))
        for row, position in enumerate(x):
            e = min(int(position/length), self.assumptions.elements-1)
            r = (position-e*length)/length
            full[row, 2*e:2*e+4] = [1-3*r*r+2*r**3, length*(r-2*r*r+r**3),
                                   3*r*r-2*r**3, length*(-r*r+r**3)]
        return full[:, self.free]

    @staticmethod
    def forces(values: np.ndarray) -> np.ndarray:
        result = np.asarray(values, dtype=float)
        if result.shape != (MODULES,) or not np.all(np.isfinite(result)) or np.any(np.abs(result) > 1e6):
            raise ValueError("24 finite bounded forces required")
        return result

    def static(self, forces_n: np.ndarray) -> np.ndarray:
        return np.linalg.solve(self.stiffness, self.local_shape.T@self.forces(forces_n))

    def initialise_static(self, forces_n: np.ndarray) -> None:
        self.q = self.local_modes.T@self.forces(forces_n)/self.omega_rad_s**2
        self.velocity[:] = 0.0

    def local_displacement_m(self) -> np.ndarray:
        return self.local_modes@self.q

    def advance(self, forces_n: np.ndarray) -> None:
        force = self.local_modes.T@self.forces(forces_n)
        old = np.column_stack((self.q, self.velocity))
        new = np.einsum("nij,nj->ni", self.transition, old)+self.drive*force[:, None]
        self.q, self.velocity = new[:, 0], new[:, 1]


def static_benchmark(assumptions: BeamAssumptions = BeamAssumptions()) -> dict:
    beam = FlexibleGuideway(assumptions)
    # Independent exact centre point load: P L³/(48 E I).
    midpoint = np.array([assumptions.span_m/2])
    shape = beam.shape(midpoint)
    force_n = 100_000.0
    centre_fe = float((shape@np.linalg.solve(beam.stiffness, shape.T*force_n)).item())
    centre_exact = force_n*assumptions.span_m**3/(48*assumptions.young_pa*assumptions.second_moment_m4)
    loads = np.full(MODULES, 27_750.0*9.81/MODULES)
    static_local = beam.local_shape@beam.static(loads)
    closed = sum((point_load_deflection(beam.module_positions_m, float(x), float(f), assumptions)
                  for x, f in zip(beam.module_positions_m, loads)), np.zeros(MODULES))
    omega_exact = np.arange(1, assumptions.retained_modes+1)**2*math.pi**2*np.sqrt(
        assumptions.young_pa*assumptions.second_moment_m4/(assumptions.line_mass_kg_m*assumptions.span_m**4))
    beam.initialise_static(loads)
    return {"assumptions": asdict(assumptions), "centre_point_load_n": force_n, "centre_fe_m": centre_fe,
            "centre_closed_form_m": centre_exact,
            "centre_relative_error": abs(centre_fe-centre_exact)/centre_exact,
            "distributed_point_load_max_error_m": float(np.max(np.abs(static_local-closed))),
            "module_load_static_max_m": float(np.max(static_local)),
            "modal_static_truncation_max_m": float(np.max(np.abs(static_local-beam.local_displacement_m()))),
            "modal_frequency_hz": (beam.omega_rad_s/(2*math.pi)).tolist(),
            "modal_frequency_max_relative_error": float(np.max(np.abs(beam.omega_rad_s/omega_exact-1)))}


class RustController:
    """Synchronous offline IPC, bounded frame sizes, with a 10 s response timeout."""
    def __init__(self, executable: Path, car_mass_kg: float = 27750.):
        if not math.isfinite(car_mass_kg) or not 1000 <= car_mass_kg <= 100_000:
            raise ValueError("bounded finite car mass required")
        self.process = subprocess.Popen([str(executable.resolve()), format(car_mass_kg, '.17g')], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, text=True, bufsize=1)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def tick(self, sequence: int, gaps_m: np.ndarray) -> tuple[np.ndarray, np.ndarray, bool]:
        gaps = np.asarray(gaps_m, dtype=float)
        if gaps.shape != (24,) or not np.all(np.isfinite(gaps)) or not 1 <= sequence <= 20_000:
            raise ValueError("bounded finite input frame required")
        self.process.stdin.write(str(sequence)+" "+" ".join(format(v, ".16e") for v in gaps)+"\n")
        self.process.stdin.flush()
        if not self.selector.select(10):
            raise RuntimeError("offline Rust controller timeout; no physical fallback is implied")
        line = self.process.stdout.readline(8193)
        fields = line.split()
        if len(line) > 8192 or len(fields) != 51 or fields[0] != "true" or fields[2] != "false":
            raise RuntimeError("Rust controller rejected frame, lost force feasibility or violated study authority: "+line[:120])
        forces = np.asarray([float(v) for v in fields[3:]])
        if not np.all(np.isfinite(forces)):
            raise RuntimeError("nonfinite Rust force response")
        return forces[:24], forces[24:], fields[1] == "true"

    def close(self) -> None:
        self.selector.close()
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        if self.process.stdout:
            self.process.stdout.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def cosimulate(executable: Path, duration_s: float = 3.0, *, initial_down_error_m: float = 0.0005,
               disturbance_n: float = 5000.0, car_mass_kg: float = 27750., assumptions: BeamAssumptions = BeamAssumptions()) -> dict:
    """Two-way held-force partitioned co-simulation, fixed virtual 1 ms step.

    Beam reaction is downward and equals upward car support force. Sensor gap
    is target + car downward motion - LOCAL guideway downward deflection,
    including each station's roll and pitch lever arm. No physical time measured.
    The controller sees identical ideal duplicate channels. Beam/modal and car
    updates use each returned force frame over the same interval.
    """
    if not math.isfinite(duration_s) or not 0.02 <= duration_s <= 10:
        raise ValueError("duration must be between 0.02 and 10 virtual seconds")
    if (not math.isfinite(initial_down_error_m) or abs(initial_down_error_m) > 0.01
            or not math.isfinite(disturbance_n) or abs(disturbance_n) > 100_000):
        raise ValueError("perturbation exceeds bounded numerical study")
    beam = FlexibleGuideway(assumptions)
    if not math.isfinite(car_mass_kg) or not 1000 <= car_mass_kg <= 100_000:
        raise ValueError("bounded finite car mass required")
    mass, gravity = car_mass_kg, 9.81
    beam.initialise_static(np.full(MODULES, mass*gravity/MODULES))
    # Absolute downward car displacement relative to the unloaded beam geometry.
    car = np.array([np.mean(beam.local_displacement_m())+initial_down_error_m, 2e-5, -5e-5])
    velocity = np.zeros(3)
    inertia = np.array([mass, 20_000.0, 600_000.0])
    minimum, maximum = math.inf, -math.inf
    largest_beam, peak_car, force_peak = 0.0, 0.0, 0.0
    stop_seen = False
    relative_heave = []
    target = 0.008
    with RustController(executable,car_mass_kg=mass) as controller:
        for tick in range(1, round(duration_s/DT_S)+1):
            local = beam.local_displacement_m()
            gaps = target+car[0]-MODULE_Y_M*car[1]+MODULE_X_M*car[2]-local
            minimum, maximum = min(minimum, float(gaps.min())), max(maximum, float(gaps.max()))
            largest_beam = max(largest_beam, float(np.max(np.abs(local))))
            peak_car = max(peak_car, float(abs(car[0])))
            upward, lateral, stopped = controller.tick(tick, gaps)
            if np.max(np.abs(lateral)) > 1e-6:
                raise RuntimeError("lateral beam/car dynamics are outside this demonstrator")
            force_peak = max(force_peak, float(upward.max()))
            stop_seen |= stopped
            # Positive down, roll, pitch. A downward external pulse models a
            # declared disturbance, with equal magnitude independent of control.
            disturbance = disturbance_n if 0.2 <= (tick-1)*DT_S < 0.3 else 0.0
            generalized = np.array([mass*gravity+disturbance-upward.sum(),
                                    MODULE_Y_M@upward, -MODULE_X_M@upward])
            acceleration = generalized/inertia
            car += velocity*DT_S+0.5*acceleration*DT_S**2
            velocity += acceleration*DT_S
            beam.advance(upward)
            relative_heave.append(float(car[0]-np.mean(beam.local_displacement_m())))
    return {"schema": "osr-coupled-guideway-numerical/1", "status": "hypothetical-two-way-offline-cosimulation",
            "physical_output_authorised": False, "structural_acceptance": False,
            "car_mass_kg": car_mass_kg, "beam_assumptions": asdict(assumptions),
            "virtual_step_s": DT_S, "virtual_duration_s": round(duration_s/DT_S)*DT_S,
            "retained_vertical_beam_modes": assumptions.retained_modes,
            "minimum_relative_gap_m": minimum, "maximum_relative_gap_m": maximum,
            "peak_global_incremental_beam_displacement_m": largest_beam,
            "peak_global_car_down_m": peak_car, "peak_station_force_n": force_peak,
            "final_fitted_relative_heave_error_m": relative_heave[-1],
            "peak_fitted_relative_heave_error_m": max(abs(v) for v in relative_heave),
            "final_roll_rad": float(car[1]), "final_pitch_rad": float(car[2]),
            "stop_seen_in_study": stop_seen,
            "limitations": ["synthetic instantaneous force channels and controller gains; no field/current/thermal map",
                            "linear simply-supported beam with assumed line mass and modal damping",
                            "single stationary rigid car; no moving loads, train coupling, torsion/corbels or flexible body",
                            "no dead-load camber, soil, joints, fatigue, contact, braking or independent protection",
                            "offline held-force partitioned integration; no measured timing or stability certificate"]}



PUBLICATION_SCHEMA = "osr-coupled-guideway-publication/1"
BUILD_COMMAND = ["cargo", "build", "--locked", "--release", "-p", "osr-maglev-control",
                 "--example", "coupled_bridge", "--message-format=json"]
PUBLICATION_SOURCES = (
    "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "ferrite-maglev-study.toml",
    "crates/osr-maglev-control/Cargo.toml", "crates/osr-maglev-control/src/lib.rs",
    "crates/osr-maglev-control/src/array.rs", "crates/osr-maglev-control/src/ideal.rs",
    "crates/osr-maglev-control/src/io.rs", "crates/osr-maglev-control/src/egress.rs", "crates/osr-maglev-control/examples/coupled_bridge.rs",
    "crates/osr-maglev-control/examples/support/mod.rs", "engineering/ferrite_maglev/coupled.py",
    "engineering/ferrite_maglev/requirements.txt",
)


def sources() -> dict[str, str]:
    """Exact declared input/code identity; hashes are integrity, not authentication."""
    return {name: sha256((ROOT/name).read_bytes()).hexdigest() for name in PUBLICATION_SOURCES}


def _encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def _read_json(path: Path) -> dict:
    def nonfinite(value):
        raise ValueError("nonfinite JSON value: "+value)
    value = json.loads(path.read_text(), parse_constant=nonfinite)
    if not isinstance(value, dict):
        raise ValueError("publication object required: "+path.name)
    return value


def _build_bridge() -> tuple[Path, dict]:
    command = BUILD_COMMAND.copy()
    built = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=180)
    executable = None
    for line in built.stdout.splitlines():
        message = json.loads(line)
        if (message.get("reason") == "compiler-artifact"
                and message.get("target", {}).get("name") == "coupled_bridge"
                and message.get("executable")):
            executable = Path(message["executable"])
    if executable is None or not executable.is_file():
        raise ValueError("Cargo did not report the built coupled bridge executable")
    compiler = subprocess.run(["rustc", "--version"], cwd=ROOT, check=True,
                              capture_output=True, text=True, timeout=30).stdout.strip()
    return executable, {"build_command": command, "rustc": compiler,
                        "bridge_sha256": sha256(executable.read_bytes()).hexdigest()}


def publish(output: Path) -> dict:
    """Build/run the actual Rust bridge and publish a fixed three-second study.

    Writes deterministic result.json and receipt.json without timestamps. Source
    and binary identity are checked around computation. Numeric reproducibility
    is scoped to the recorded Python/NumPy/SciPy/compiler runtime, not all BLAS,
    CPU or OS implementations. Checksums do not authenticate physical evidence.
    """
    output = Path(output).resolve()
    if output.exists():
        if not output.is_dir() or any(p.is_symlink() for p in output.iterdir()):
            raise ValueError("publication destination must be an ordinary owned directory")
        if any(output.iterdir()):
            receipt_path = output/"receipt.json"
            if not receipt_path.is_file() or _read_json(receipt_path).get("schema") != PUBLICATION_SCHEMA:
                raise ValueError("nonempty output is not an owned coupled publication")
            if {p.name for p in output.iterdir()} != {"result.json", "receipt.json"}:
                raise ValueError("unexpected file in bounded coupled publication")
    identity = sources()
    executable, execution = _build_bridge()
    runtime = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    result = {"schema": "osr-coupled-guideway-result/1", "source_sha256": identity,
              "runtime": runtime, "execution": execution, "physical_output_authorised": False,
              "structural_acceptance": False, "static_benchmark": static_benchmark(),
              "coupled_replay": cosimulate(executable, duration_s=3.0)}
    if sources() != identity or sha256(executable.read_bytes()).hexdigest() != execution["bridge_sha256"]:
        raise ValueError("coupled study sources or binary changed during calculation")
    data = _encoded(result)
    receipt = {"schema": PUBLICATION_SCHEMA, "source_sha256": identity,
               "runtime": runtime, "execution": execution,
               "files_sha256": {"result.json": sha256(data).hexdigest()},
               "physical_output_authorised": False, "structural_acceptance": False}
    output.mkdir(parents=True, exist_ok=True)
    # Replace the receipt last: interrupted publication cannot verify as complete.
    for name, content in (("result.json", data), ("receipt.json", _encoded(receipt))):
        descriptor, temporary = tempfile.mkstemp(prefix=".coupled-", dir=output)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, output/name)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return receipt


def verify(output: Path) -> dict:
    """Check receipt, current source identity and exact payload without rerunning."""
    output = Path(output).resolve()
    if not output.is_dir() or {p.name for p in output.iterdir()} != {"result.json", "receipt.json"}:
        raise ValueError("exact coupled publication inventory required")
    if any(p.is_symlink() or not p.is_file() for p in output.iterdir()):
        raise ValueError("ordinary publication files required")
    receipt = _read_json(output/"receipt.json")
    if receipt.get("schema") != PUBLICATION_SCHEMA:
        raise ValueError("wrong coupled publication receipt schema")
    if receipt.get("source_sha256") != sources():
        raise ValueError("coupled publication sources changed")
    if not isinstance(receipt.get("files_sha256"), dict) or set(receipt["files_sha256"]) != {"result.json"}:
        raise ValueError("exact result checksum inventory required")
    if sha256((output/"result.json").read_bytes()).hexdigest() != receipt["files_sha256"]["result.json"]:
        raise ValueError("coupled publication result checksum differs")
    result = _read_json(output/"result.json")
    if result.get("schema") != "osr-coupled-guideway-result/1":
        raise ValueError("wrong coupled result schema")
    for key in ("source_sha256", "runtime", "execution"):
        if result.get(key) != receipt.get(key):
            raise ValueError("receipt/result identity differs: "+key)
    execution = receipt.get("execution", {})
    if not isinstance(execution, dict):
        raise ValueError("Rust execution identity object required")
    digest = execution.get("bridge_sha256", "")
    if (set(execution) != {"build_command", "rustc", "bridge_sha256"}
            or execution.get("build_command") != BUILD_COMMAND
            or not isinstance(execution.get("rustc"), str) or not execution["rustc"]
            or not isinstance(digest, str) or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)):
        raise ValueError("complete Rust execution identity required")
    runtime = receipt.get("runtime", {})
    if (not isinstance(runtime, dict) or set(runtime) != {"python", "numpy", "scipy"}
            or not all(isinstance(v, str) and v for v in runtime.values())):
        raise ValueError("complete numerical runtime identity required")
    replay = result.get("coupled_replay", {})
    if (not isinstance(replay, dict) or replay.get("status") != "hypothetical-two-way-offline-cosimulation"
            or replay.get("virtual_duration_s") != 3.0):
        raise ValueError("fixed three-second coupled replay required")
    for item in (receipt, result, replay):
        if item.get("physical_output_authorised") is not False or item.get("structural_acceptance") is not False:
            raise ValueError("physical and structural acceptance must remain false")
    return receipt

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, default=ROOT/"target/release/examples/coupled_bridge",
                        help="build with cargo build -p osr-maglev-control --release --example coupled_bridge")
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--output", type=Path, help="build/run fixed three-second study and publish result plus receipt")
    parser.add_argument("--verify", type=Path, help="verify an existing source-bound publication without recomputing")
    args = parser.parse_args()
    if args.output and args.verify:
        parser.error("choose publication or verification")
    if args.output or args.verify:
        if args.static_only or args.duration_s != 3.0:
            parser.error("publication uses the fixed complete three-second study")
        receipt = publish(args.output) if args.output else verify(args.verify)
        print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
        return
    result = {"static_benchmark": static_benchmark()}
    if not args.static_only:
        result["coupled_replay"] = cosimulate(args.bridge, args.duration_s)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
