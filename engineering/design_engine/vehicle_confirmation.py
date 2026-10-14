"""Assembly-bound passage coverage, modal conservation and joint demand evidence.

These checks exercise the existing research models. They do not supply missing
shell load paths, supplier joint laws, fatigue curves or measured modal evidence.
"""

from copy import deepcopy
import math

from .contracts import fingerprint


def finite(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("finite " + name + " required")
    return float(value)


def passage_plan(model, configuration, *, dt=0.002):
    """Start the whole assembly before the approach and solve exact exit times.

    Positive travel follows the native adapter's v*t + a*t*t/2 law, with
    braking clamped at its stopping time. Relative initial train positions and
    arrival times survive the common coordinate shift. A stopped train is never
    represented by a shorter, supposedly complete passage.
    """
    dt = finite(dt, "time step")
    if not 0.0000625 <= dt <= 0.005:
        raise ValueError("passage time step outside native domain")
    cars = model["family_definition"]["cars"]
    if not cars:
        raise ValueError("actual car extents required")
    lower = min(finite(c["start_x_m"], "car start") for c in cars)
    upper = max(
        finite(c["start_x_m"], "car start") + finite(c["length_m"], "car length")
        for c in cars
    )
    if upper <= lower or any(c["length_m"] <= 0 for c in cars):
        raise ValueError("positive assembly extents required")
    bridge = model["bridge"]
    length = (
        finite(bridge["candidate"]["definition"]["deck"]["span_m"], "span")
        * bridge["span_count"]
    )
    if length <= 0:
        raise ValueError("positive bridge extent required")
    cfg = deepcopy(configuration)
    traffic = cfg["traffic"]
    if not 1 <= len(traffic) <= 4 or len({t["id"] for t in traffic}) != len(traffic):
        raise ValueError("unique bounded train identities required")
    # SpatialStructure uses a fixed five metre approach at either end. The extra
    # metre places the complete body clear of that approach at entry and exit.
    approach = 5.0
    clearance = 1.0
    shift = (
        -approach
        - clearance
        - upper
        - max(finite(t["initial_advance_m"], "initial advance") for t in traffic)
    )
    rows = []
    for entry in traffic:
        speed = finite(entry["speed_m_s"], "speed")
        acceleration = finite(entry["acceleration_m_s2"], "acceleration")
        arrival = finite(entry["arrival_time_s"], "arrival time")
        if speed < 0 or arrival < 0:
            raise ValueError("nonnegative arrival and forward speed required")
        if arrival > 0 and acceleration != 0:
            raise ValueError(
                "outside domain: native pre-arrival acceleration is not clamped; delayed accelerating traffic requires a dedicated motion adapter"
            )
        entry["initial_advance_m"] += shift
        distance = length + approach + clearance - lower - entry["initial_advance_m"]
        if acceleration == 0:
            elapsed = distance / speed if speed > 0 else None
        else:
            discriminant = speed * speed + 2 * acceleration * distance
            # A stable positive quadratic root also handles acceleration from rest.
            elapsed = (
                2 * distance / (speed + math.sqrt(discriminant))
                if discriminant >= 0 and speed + math.sqrt(discriminant) > 0
                else None
            )
        rows.append(
            dict(
                train=entry["id"],
                required_travel_m=distance,
                front_at_arrival_m=entry["initial_advance_m"] + upper,
                rear_at_arrival_m=entry["initial_advance_m"] + lower,
                elapsed_to_exit_s=elapsed,
                exit_time_s=None if elapsed is None else arrival + elapsed,
                stopping_distance_m=(
                    None if acceleration >= 0 else speed * speed / (-2 * acceleration)
                ),
                state="non-passing" if elapsed is None else "planned",
            )
        )
    duration = (
        None
        if any(r["exit_time_s"] is None for r in rows)
        else math.ceil(max(r["exit_time_s"] for r in rows) / dt) * dt
    )
    steps = None if duration is None else math.ceil(duration / dt)
    within = duration is not None and 0 < duration <= 120 and steps <= 200000
    return dict(
        schema="osr-complete-passage-plan/1",
        configuration=cfg,
        original_configuration_sha256=fingerprint(configuration),
        configuration_sha256=fingerprint(cfg),
        assembly_extent_m=[lower, upper],
        bridge_extent_m=[0.0, length],
        approach_m=approach,
        clearance_m=clearance,
        common_coordinate_shift_m=shift,
        trains=rows,
        duration_s=duration,
        steps=steps,
        within_adapter_domain=within,
        state="planned" if within else "outside-domain",
        physical_validation=False,
    )


def assembly_diagnostics(package, *, mode_count=2):
    """Actual rigid/modal/equipment mass and reaction reconciliation.

    The inherited uniform beam uses explicitly synthetic EI and shank stiffness;
    it cannot substitute for an actual underframe/shell or approved mount design.
    """
    import numpy as np
    from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
    from engineering.integration_programme.flexible_vehicle import FlexibleVehicle
    from engineering.integration_programme.joints import battery_mount
    from engineering.civil_exploration.spatial_structure import Route

    if type(mode_count) is not int or mode_count not in (2, 4, 6):
        raise ValueError("declared bounded modal count required")
    model = package["model"]
    configuration = package["spatial_configuration"]
    group = battery_mount(
        package["battery"], dict(diameter_m=0.012, grip_m=0.018, youngs_pa=210e9)
    )
    mounts = {
        c["id"]
        + "/battery": dict(
            stiffness_si=group["stiffness_si"],
            damping_si=np.zeros((6, 6)).tolist(),
            motion_bounds_si=[[-0.01, 0.01]] * 6,
            basis="synthetic engaged 12 mm elastic shank; preload, threads, members and fatigue unqualified",
        )
        for c in model["family_definition"]["cars"]
    }
    rigid = SpatialVehicle(model, configuration["joint_laws"])
    flexible = FlexibleVehicle(
        model,
        configuration["joint_laws"],
        equipment_mounts=mounts,
        mode_count=mode_count,
        ei_nm2=3e8,
        damping_ratio=0.02,
    )
    _, _, _, (_, plans) = flexible.matrices(Route(configuration["route"]), 0.0, 0.0)
    forces = flexible.intrinsic_preload.copy()
    for plan in plans:
        forces += plan["J"].T @ plan["joint"]["K"] @ plan["joint"]["preload_extension"]
    weight = flexible.total_mass * 9.81
    reaction = sum(c["static_n"] for c in flexible.contacts)
    return dict(
        schema="osr-vehicle-assembly-diagnostics/1",
        model_sha256=fingerprint(model),
        rigid_mass_kg=rigid.total_mass,
        flexible_mass_kg=flexible.total_mass,
        mass_relative_error=abs(flexible.total_mass - rigid.total_mass)
        / rigid.total_mass,
        gravity_force_n=weight,
        static_contact_force_n=reaction,
        reaction_relative_error=abs(reaction - weight) / weight,
        minimum_static_contact_n=min(c["static_n"] for c in flexible.contacts),
        modal_preload_residual_n=float(np.max(np.abs(forces[flexible.rigid_size :]))),
        mode_count_per_body=mode_count,
        actual_mount_group_sha256=fingerprint(group),
        equipment_instance_ids=sorted(mounts),
        equipment_mount_laws=mounts,
        flexible_vehicle_parameters=dict(
            ei_nm2=3e8, mode_count=mode_count, damping_ratio=0.02
        ),
        modal_frequencies_hz={
            key: value["basis"]["frequencies_hz"]
            for key, value in flexible.modal.items()
        },
        stiffness_basis="synthetic uniform Euler-Bernoulli body; no shell-to-modal correlation",
        physical_validation=False,
        production_released=False,
        open_domains=[
            "actual underframe/shell load paths",
            "supplier mounting and joint laws",
            "correlated modal shapes and damping",
            "fatigue stress transfer and S-N curves",
        ],
    )


def complete_coverage(model, configuration, plan, result):
    """Check actual converged coverage and the native compiler's hash format."""
    from osr_mech.engineering_definition import fingerprint as native_hash

    duration = plan["duration_s"]
    progress = result.get("numerical_progress", {})
    return bool(
        plan["within_adapter_domain"]
        and duration is not None
        and result.get("state") == "completed"
        and result.get("within_adapter_domain") is True
        and result.get("configuration_sha256") == native_hash(configuration)
        and result.get("hardware_definition_sha256") == native_hash(model)
        and result.get("steps", 0) >= plan["steps"]
        and progress.get("converged_steps", 0) >= plan["steps"]
        and progress.get("last_converged_time_s", 0) + 1e-10 >= duration
    )


def joint_cycles(history, *, complete=False):
    """Rainflow on every converged six-resultant history, without inventing life."""
    from engineering.civil_exploration.constitutive import rainflow

    series = {}
    last_time = -1.0
    for sample in history:
        time = finite(sample["time_s"], "sample time")
        if time <= last_time:
            raise ValueError("strictly increasing sample times required")
        last_time = time
        seen = set()
        for row in sample["joints"]:
            key = (row["train"], row["joint"])
            if key in seen:
                raise ValueError("duplicate joint sample")
            seen.add(key)
            force = row["force_moment_si"]
            if len(force) != 6:
                raise ValueError("complete six-resultant joint load required")
            arrays = series.setdefault(key, [[] for _ in range(6)])
            for i, value in enumerate(force):
                arrays[i].append(finite(value, "joint resultant"))
        if seen != set(series):
            raise ValueError("every joint required at every sample")
    rows = []
    for (train, joint), arrays in sorted(series.items()):
        for axis, values in enumerate(arrays):
            if len(values) != len(history):
                raise ValueError("missing joint sample")
            cycles = [] if len(values) < 2 else rainflow(values)
            rows.append(
                dict(
                    train=train,
                    joint=joint,
                    axis=axis,
                    unit="N" if axis < 3 else "N m",
                    peak_absolute=max(map(abs, values)),
                    cycles=[
                        dict(range=r["range_pa"], count=r["count"]) for r in cycles
                    ],
                    damage=None,
                    fatigue_life_cycles=None,
                    state="unknown",
                )
            )
    return dict(
        schema="osr-joint-resultant-cycles/1",
        samples=len(history),
        complete_requested_history=complete,
        full_passage_history=False,
        rows=rows,
        stress_transfer=None,
        sn_curve=None,
        physical_validation=False,
        basis="resultant ranges only; no stress conversion, cycle-life extrapolation or fatigue acceptance",
        reference="https://www.nrel.gov/docs/fy15osti/63679.pdf",
    )
