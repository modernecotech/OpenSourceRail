"""Isolated propulsion research coupons; never a configuration adoption gate.

The retained 8 mm chamfer field supplies conditional coefficients. The electrical
coupon is a scalar phase-amplitude RL fixture with ideal model feedforward. It
does not execute the installed inverter, Rust current controller or moving train.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path("engineering/assurance/v053-propulsion-redesign-screen")
FLAGS = dict(configuration_adopted=False, design_complete=False,
             physical_validation=False, physical_release=False)


def finite(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"finite {name} required")
    if positive and value <= 0:
        raise ValueError(f"positive {name} required")
    return float(value)


def terminal_rl_coupon(*, resistance_ohm, inductance_h, emf_v,
                       command_a=1349., current_limit_a=1350., voltage_limit_v=1385.640646055102,
                       response_s=.01, step_s=.0001, on_s=.2, tail_s=.1):
    """Execute a fixed-coefficient phase-amplitude RL coupon by implicit midpoint.

    v=e+Ri+L(Icommand-i)/tau is ideal model-feedforward feedback, clipped to
    the declared terminal voltage. Three-phase amplitude power uses 3/2. EMF
    is a constant external energy sink, not an executed moving magnetic field.
    """
    R = finite(resistance_ohm, "resistance", positive=True)
    L = finite(inductance_h, "inductance", positive=True)
    e = finite(emf_v, "EMF")
    command = finite(command_a, "current command")
    limit = finite(current_limit_a, "current limit", positive=True)
    voltage = finite(voltage_limit_v, "voltage limit", positive=True)
    tau = finite(response_s, "response time", positive=True)
    dt = finite(step_s, "step", positive=True)
    on = finite(on_s, "on duration", positive=True)
    tail = finite(tail_s, "tail duration", positive=True)
    count = round((on + tail) / dt)
    # Midpoint is energy-conserving but can oscillate around the physical RL
    # equilibrium if a voltage-clipped step does not resolve L/R. Resolve both
    # feedback and electrical poles before interpreting any current peak.
    if abs(command) > limit or dt > min(tau, L/R) / 2 or not 1 <= count <= 100000:
        raise ValueError("bounded command, resolved controller/electrical response and step count required")
    if not math.isclose(count * dt, on + tail, abs_tol=1e-12) or not math.isclose(round(on/dt)*dt, on, abs_tol=1e-12):
        raise ValueError("on and total durations must contain whole steps")
    current = terminal = copper = sink = peak = peak_v = 0.
    clipped = 0
    on_end = 0.
    for index in range(count):
        target = command if index < round(on / dt) else 0.
        trial = (current * (1 - dt/(2*tau)) + dt*target/tau) / (1 + dt/(2*tau))
        middle = (current + trial) / 2
        requested_v = e + R*middle + L*(target-middle)/tau
        applied_v = min(voltage, max(-voltage, requested_v))
        if applied_v != requested_v:
            clipped += 1
            trial = (current * (1-R*dt/(2*L)) + dt*(applied_v-e)/L) / (1+R*dt/(2*L))
            middle = (current + trial) / 2
        terminal += 1.5 * applied_v * middle * dt
        copper += 1.5 * R * middle**2 * dt
        sink += 1.5 * e * middle * dt
        peak = max(peak, abs(trial))
        peak_v = max(peak_v, abs(applied_v))
        current = trial
        if index + 1 == round(on / dt):
            on_end = current
    stored = .75 * L * current**2
    residual = terminal - copper - sink - stored
    return dict(steps=count, on_end_current_a=on_end, final_current_a=current,
                peak_current_a=peak, peak_applied_voltage_v=peak_v,
                voltage_limited_steps=clipped, terminal_energy_j=terminal,
                copper_energy_j=copper, external_emf_energy_j=sink,
                final_inductive_energy_j=stored, energy_residual_j=residual,
                current_limit_pass=peak <= limit,
                requested_waveform_unclipped=clipped == 0,
                scope="Ideal feedforward scalar RL fixture at frozen coefficients; no actual inverter/controller, magnetic motion or route validation.",
                **FLAGS)


def adiabatic_duty(*, current_a, resistance_80c_ohm, copper_mass_kg,
                   specific_heat_j_kg_k, alpha_per_k, pulse_s, period_s=180.,
                   cycles=40, initial_c=40., screen_c=120.):
    """Exact no-cooling copper ODE with the declared linear resistance proxy.

    This fixture retains copper heat only. Off time supplies zero cooling;
    reaching the temperature screen stops the applicable calculation there.
    """
    current = finite(current_a, "duty current")
    R80 = finite(resistance_80c_ohm, "80C resistance", positive=True)
    capacity = finite(copper_mass_kg, "copper mass", positive=True) * finite(specific_heat_j_kg_k, "specific heat", positive=True)
    alpha = finite(alpha_per_k, "copper temperature coefficient", positive=True)
    pulse = finite(pulse_s, "pulse duration", positive=True)
    period = finite(period_s, "period", positive=True)
    initial = finite(initial_c, "initial temperature")
    screen = finite(screen_c, "temperature screen")
    if type(cycles) is not int or not 1 <= cycles <= 1000 or pulse > period or not 20 <= initial < screen <= 120:
        raise ValueError("bounded duty and 20C <= initial < screen <= 120C required")
    coefficient = 1.5 * R80 * current**2 / (capacity * (1+60*alpha))
    requested_on = cycles * pulse
    time_to_screen = math.inf if coefficient == 0 else math.log((1+alpha*(screen-20))/(1+alpha*(initial-20))) / (alpha*coefficient)
    evaluated_on = min(requested_on, time_to_screen)
    final = initial + (1+alpha*(initial-20)) * math.expm1(alpha*coefficient*evaluated_on) / alpha
    return dict(requested_energised_s=requested_on, evaluated_energised_s=evaluated_on,
                initial_c=initial, final_c=min(final, screen), temperature_screen_c=screen,
                adiabatic_temperature_screen_pass=requested_on <= time_to_screen,
                time_to_temperature_screen_energised_s=None if math.isinf(time_to_screen) else time_to_screen,
                accumulated_copper_heat_j=capacity*(final-initial),
                duty_fraction=pulse/period, period_s=period, cycles=cycles,
                cooling_assumed_w=0., thermal_equilibrium_established=False,
                scope="Copper-only no-cooling fixture with declared linear R(T), truncated at temperature screen; no measured thermal model or magnetic temperature-range credit.",
                **FLAGS)


def mesh_diagnostics(rows, hypothesis):
    """Retain all applicable samples; two nonuniform refinements prove no order."""
    related = [r for r in rows if r["hypothesis_sha256"] == hypothesis]
    temperatures = sorted({r["grid"]["temperature_c"] for r in related})
    diagnostics = []
    for temperature in temperatures:
        samples = sorted((r for r in related if r["state"] == "executed" and r["grid"]["temperature_c"] == temperature), key=lambda r: r["grid"]["nx"])
        finest = samples[-1] if samples else None
        coarse = samples[-2] if len(samples) > 1 else None
        diagnostics.append(dict(temperature_c=temperature, sample_ids=[r["id"] for r in samples],
            executed_meshes=len(samples), all_sampled_material_screens_pass=bool(samples) and all(r["material_current_screen_pass"] for r in samples),
            finest_margin_a_m=finest["demag_margin_after_declared_current_bound_a_m"] if finest else None,
            last_margin_change_a_m=(finest["demag_margin_after_declared_current_bound_a_m"]-coarse["demag_margin_after_declared_current_bound_a_m"]) if coarse else None,
            independent_peak_convergence_established=False,
            hold="Only two meshes with changing longitudinal and depth resolution; no observed asymptotic order, independent axis refinement, full temperature sweep or rig correlation."))
    return diagnostics


def study(root=ROOT):
    root = Path(root)
    base = root / ARCHIVE
    verifier = runpy.run_path(str(base / "verify.py"))
    verification = verifier["verify"](check_current_sources=True)
    result = json.loads((base / "executed/results.json").read_text())
    boundary = json.loads((base / "executed/current-boundary-diagnostic.json").read_text())
    comparison = json.loads((base / "acceleration-comparison.json").read_text())
    hypothesis = result["resolved_corner_alternative"]["hypothesis_sha256"]
    selected = next(r for r in boundary["rows"] if r["requested_q_current_a"] == 1349.)
    sample = next(r for r in result["resolved_corner_operating"]["operating_samples"] if r.get("map_valid_for_this_sample") and r["speed_m_s"] == 20.)
    inputs = json.loads((base / "executed/inputs/resolved8mm-256-40.json").read_text())
    copper = inputs["materials"]["copper"]
    current_limit = min(selected["source_current_limits_a"])
    voltage_limit = sample["modulation_limit_v"]
    omega = 2 * math.pi * boundary["speed_m_s"] / inputs["propulsion_flux_shoe"]["period_m"]
    force_per_a = selected["force_x_n_per_car"] / selected["requested_q_current_a"]
    # Every group retains its own EMF; no full-overlap substitution at the ends.
    transient = [dict(group_id=group["id"], result=terminal_rl_coupon(
        resistance_ohm=R, inductance_h=L, emf_v=e, current_limit_a=current_limit,
        voltage_limit_v=voltage_limit)) for group, R, L, e in zip(
            boundary["groups"], sample["group_R_ohm"], sample["group_L_h"], selected["emf_peak_v_per_group"])]
    variants = []
    # Explicitly includes the refused exact-limit phasor and an excessive request.
    for current in (337.5, 675., 1000., 1200., 1349., 1350., 1400.):
        for pulse in (1., 2., 5., 10.):
            interior = 0 < current < current_limit
            duty = adiabatic_duty(current_a=current, resistance_80c_ohm=sample["group_R_ohm"][0],
                copper_mass_kg=sample["group_copper_mass_kg"][0], specific_heat_j_kg_k=copper["specific_heat_j_kg_k"],
                alpha_per_k=copper["resistance_temperature_coefficient_per_k"], pulse_s=pulse)
            force = force_per_a*current if interior else None
            # Triangle bound includes rotating-current inductive voltage. The
            # scalar terminal coupon above does not model this dq rotation.
            voltage_bound = max(selected["emf_peak_v_per_group"]) + max(sample["group_R_ohm"])*current + omega*max(sample["group_L_h"])*current
            eligible = interior and duty["adiabatic_temperature_screen_pass"] and voltage_bound <= voltage_limit
            variants.append(dict(id=f"I{current:g}-pulse{pulse:g}", current_a=current, pulse_s=pulse,
                current_request_interior=interior, fixed_pose_force_n=force,
                force_duty_proxy_n=force*pulse/180 if force is not None else None,
                steady_voltage_triangle_bound_v=voltage_bound, voltage_bound_pass=voltage_bound <= voltage_limit,
                adiabatic_duty=duty, conditional_coupon_screens_pass=eligible,
                refusal=None if interior else ("Exact-limit phasor remains refused in retained evidence" if current == current_limit else "Current exceeds declared limit"),
                system_eligible=False, **FLAGS))
    ranked = sorted((v for v in variants if v["conditional_coupon_screens_pass"]), key=lambda v: (-v["force_duty_proxy_n"], v["adiabatic_duty"]["final_c"], v["id"]))
    source_paths = [ARCHIVE/"archive-receipt.json", ARCHIVE/"executed/results.json",
        ARCHIVE/"executed/current-boundary-diagnostic.json", ARCHIVE/"acceleration-comparison.json",
        Path("engineering/maglev_research/propulsion_research.py")]
    force = selected["force_x_n_per_car"]
    mass = comparison["current_candidate_aw3_mass_kg_per_car"]
    resistance = comparison["inherited_resistance_proxy_at_20m_s_n_per_car"]
    return dict(schema="osr-propulsion-research-closure/1", parent_configuration_sha256=result["parent_configuration_sha256"],
        hypothesis_sha256=hypothesis, archive_verification=verification,
        source_sha256={str(p): sha256((root/p).read_bytes()).hexdigest() for p in source_paths},
        mesh_diagnostics=mesh_diagnostics(result["rows"], hypothesis),
        transient_coupons=transient, transient_energy_balance_pass=all(abs(v["result"]["energy_residual_j"]) < 1e-6 for v in transient),
        search=dict(variants=variants, cases=len(variants), conditional_coupon_passes=len(ranked),
            ranked_case_ids=[v["id"] for v in ranked], recommended_next_coupon_id=ranked[0]["id"] if ranked else None,
            ranking_basis="Descending fixed-pose force times pulse/180s; provisional 40-cycle copper-only no-cooling screen, strictly interior current and steady EMF+RI+omegaLI triangle voltage bound. Fixed-field force scales linearly with current. No average route thrust or operating recommendation."),
        comparison=dict(canonical_comparison_mass_kg=mass, changed_hypothesis_installed_mass_reconciled=False,
            ideal_acceleration_upper_bound_m_s2=force/mass,
            acceleration_after_inherited_resistance_m_s2=(force-resistance)/mass,
            maximum_grade_fraction_at_0_2_m_s2_with_inherited_resistance=(force-resistance-.2*mass)/(mass*9.81),
            scope="Single 20m/s finite-overlap sample at canonical comparison mass; necessary arithmetic only, no grade/route acceptance."),
        open_gates=["Independent local-peak mesh and boundary convergence", "Full magnetic temperature range and measured 3D/material correlation",
            "Native installed mass, CG, inertia, retention and manufacturing", "Actual inverter/Rust control with changing overlap and phase",
            "Measured losses/cooling and repeated duty including all heat sources", "Whole-train group sharing and supported four-stop route integration"],
        **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    answer = study()
    rendered = json.dumps(answer, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
        print(json.dumps(dict(output=str(args.output), cases=answer["search"]["cases"],
            conditional_coupon_passes=answer["search"]["conditional_coupon_passes"],
            recommended_next_coupon_id=answer["search"]["recommended_next_coupon_id"], **FLAGS)))
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
