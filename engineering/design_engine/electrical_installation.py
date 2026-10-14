"""Bounded auxiliary-power, PV and mount demands; never supplier qualification.

Published component facts stay separate from scenario assumptions. Candidate
hardware is a procurement/installation preview, not an installed physical part;
its output is never credited against the retained vehicle duty or residual mass.
"""

from copy import deepcopy
import math

from osr_mech.engineering_definition import number


SOURCES = {
    "abb-m40-b": {
        "url": "https://library.e.abb.com/public/3ade265d028245cb91b97353a515581c/NEW%20PDS%20BORDLINE_M40_DC_750V_U_.pdf",
        "publisher": "ABB",
        "retrieved": "2026-10-14",
        "input_range_v": [400.0, 900.0],
        "ac_voltage_v": 415.0,
        "ac_phases": 3,
        "ac_frequency_hz": 50.0,
        "apparent_power_va": 25000.0,
        "control_voltage_v": 110.0,
        "control_power_w": 18900.0,
        "mass_kg": 350.0,
        "dimensions_m": [1.694, .873, .593],
        "ambient_range_c": [-25.0, 50.0],
        "efficiency": None,
        "basis": "version B public nominal data; catenary application, battery-fed qualification open",
    },
    "liebherr-macs8": {
        "url": "https://www.liebherr.com/shared/media/aerospace-and-transportation/transportation/downloads/products/liebherr-modular-air-conditioning-system.pdf",
        "publisher": "Liebherr",
        "retrieved": "2026-10-14",
        "ac_voltage_v": 400.0,
        "ac_phases": 3,
        "ac_frequency_hz": 50.0,
        "control_voltage_v": 110.0,
        "published_component_input_sum_w": 5500.0,
        "voltage_tolerance_v": None,
        "power_factor": None,
        "starting_current_a": None,
        "control_input_w": None,
        "basis": "2016 MACS 8.0 candidate; component inputs exclude controls and heating",
    },
    "renogy-rsp200db-72-g1": {
        "url": "https://www.renogy.com/content/RSP200DB-72-US/RSP200DB-72-G1%20Datasheet.pdf",
        "publisher": "Renogy",
        "retrieved": "2026-10-14",
        "stc_power_w": 200.0,
        "vmp_v": 20.1,
        "voc_v": 23.9,
        "mass_kg": 4.9,
        "dimensions_m": [1.605, .748, .003],
        "maximum_system_voltage_v": 600.0,
        "power_temperature_coefficient_per_k": -.0038,
        "voc_temperature_coefficient_per_k": -.0029,
        "basis": "specific US G1 datasheet variant; stationary/RV product, rail and complete roof-stack fire qualification absent",
    },
}


def _count(value, name, maximum=64, minimum=1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be a bounded integer")
    return value


def auxiliary_power_screen(pack, module_count, *, ambient_c=45.0, efficiency=None):
    """Check known incompatibilities and calculate a conditional DC penalty.

    A kW lower bound can reject a kVA limit since power factor cannot exceed
    one. It cannot prove adequate capacity without PF and starting current.
    The nominal battery voltage is not a qualified minimum/maximum bus range.
    """
    count = _count(module_count, "HVAC module count", maximum=6)
    ambient = number(ambient_c, "ambient temperature")
    voltage = number(pack["nominal_voltage_v"], "nominal DC bus", minimum=1e-9)
    converter = SOURCES["abb-m40-b"]
    load = SOURCES["liebherr-macs8"]
    ac_lower = count * load["published_component_input_sum_w"]
    nominal_in_range = converter["input_range_v"][0] <= voltage <= converter["input_range_v"][1]
    apparent_lower = ac_lower  # VA at PF=1; real requirement cannot be smaller.
    checks = {
        "direct_dc_to_ac_load": "failed",
        "nominal_converter_input_voltage": "passed" if nominal_in_range else "failed",
        "operating_bus_voltage_range": "unknown",
        "output_voltage_tolerance": "unknown",
        "phases_and_frequency": "passed",
        "control_voltage": "passed",
        "continuous_apparent_capacity": "failed" if apparent_lower > converter["apparent_power_va"] else "unknown",
        "starting_and_transient_current": "unknown",
        "controls_and_heating_load": "unknown",
        "ambient_rating": "passed" if converter["ambient_range_c"][0] <= ambient <= converter["ambient_range_c"][1] else "failed",
        "cooling_mounts_harness_protection_fire": "unknown",
    }
    dc_input = heat = current = None
    if efficiency is not None:
        eta = number(efficiency, "scenario conversion efficiency", minimum=1e-9)
        if eta > 1:
            raise ValueError("conversion efficiency cannot exceed one")
        dc_input = ac_lower / eta
        heat = dc_input - ac_lower
        current = dc_input / voltage
    return {
        "schema": "osr-auxiliary-power-screen/1",
        "source_facts": {key: deepcopy(SOURCES[key]) for key in ("abb-m40-b", "liebherr-macs8")},
        "candidate_installed": False,
        "module_count_per_car": count,
        "ac_component_input_lower_bound_w": ac_lower,
        "apparent_power_lower_bound_va": apparent_lower,
        "candidate_nameplate_apparent_power_va": converter["apparent_power_va"],
        "voltage_difference_v": converter["ac_voltage_v"] - load["ac_voltage_v"],
        "conditional_dc_input_lower_bound_w": dc_input,
        "conditional_conversion_heat_w": heat,
        "conditional_dc_bus_current_a": current,
        "scenario_efficiency": efficiency,
        "additional_equipment_mass_lower_bound_kg_per_car": converter["mass_kg"],
        "additional_mount_coolant_harness_mass_kg": None,
        "checks": checks,
        "engineering_constraints_passed": None,
        "physical_validation": False,
        "basis": "potential converter preview only; no mass or energy removed from the physical vehicle; nominal matches do not qualify electrical interfaces",
    }


def pv_screen(series_modules, parallel_strings, *, irradiance_w_m2, cell_temperature_c,
              cold_cell_temperature_c, duration_s, shaded_fraction=0.0,
              mppt_efficiency=None, exposed_area_m2=None, additional_hardware_mass_kg=None):
    """Source-backed PV energy preview with explicit mounting/conversion gaps.

    Linear STC and temperature scaling is a screening assumption, not an IV,
    shading or route/weather model. It earns no vehicle energy credit.
    """
    ns = _count(series_modules, "PV series modules", 32)
    np = _count(parallel_strings, "PV parallel strings", 8)
    if ns * np > 64:
        raise ValueError("PV module count outside bounded installation preview")
    G = number(irradiance_w_m2, "irradiance", minimum=0)
    T = number(cell_temperature_c, "cell temperature")
    cold = number(cold_cell_temperature_c, "cold cell temperature")
    duration = number(duration_s, "PV scenario duration", minimum=0)
    shade = number(shaded_fraction, "shaded fraction", minimum=0)
    if G > 1500 or not -40 <= cold <= T <= 85 or shade > 1 or duration > 86400:
        raise ValueError("PV scenario outside bounded source/screen domain")
    p = SOURCES["renogy-rsp200db-72-g1"]
    n = ns * np
    area = n * p["dimensions_m"][0] * p["dimensions_m"][1]
    cold_voc = ns * p["voc_v"] * (1 + p["voc_temperature_coefficient_per_k"] * (cold - 25))
    power = n * p["stc_power_w"] * G / 1000 * max(0, 1 + p["power_temperature_coefficient_per_k"] * (T - 25)) * (1 - shade)
    delivered = None
    if mppt_efficiency is not None:
        eta = number(mppt_efficiency, "scenario MPPT efficiency", minimum=1e-9)
        if eta > 1:
            raise ValueError("MPPT efficiency cannot exceed one")
        delivered = power * eta
    fit = "unknown"
    if exposed_area_m2 is not None:
        available = number(exposed_area_m2, "exposed roof area", minimum=0)
        fit = "failed" if area > available else "unknown"
    installed_mass = None
    if additional_hardware_mass_kg is not None:
        hardware = number(additional_hardware_mass_kg, "PV hardware mass", minimum=1e-9)
        installed_mass = n * p["mass_kg"] + hardware
    return {
        "schema": "osr-pv-installation-preview/1", "source_facts": deepcopy(p),
        "candidate_installed": False, "module_count": n,
        "source_module_mass_kg": n * p["mass_kg"],
        "conditional_installed_mass_kg": installed_mass,
        "module_area_m2": area, "cold_open_circuit_voltage_v": cold_voc,
        "nominal_mpp_voltage_v": ns * p["vmp_v"],
        "conditional_module_power_w": power,
        "conditional_delivered_power_w": delivered,
        "conditional_delivered_energy_j": None if delivered is None else delivered * duration,
        "vehicle_energy_credit_j": 0.0,
        "scenario": dict(series_modules=ns, parallel_strings=np, irradiance_w_m2=G,
                         cell_temperature_c=T, cold_cell_temperature_c=cold,
                         duration_s=duration, shaded_fraction=shade, mppt_efficiency=mppt_efficiency),
        "checks": {
            "cold_string_insulation_voltage": "failed" if cold_voc > p["maximum_system_voltage_v"] else "passed",
            "roof_area_lower_bound": fit, "roof_layout_and_clearance": "unknown",
            "battery_bus_and_mppt_compatibility": "unknown", "shade_bypass_and_protection": "unknown",
            "retention_mounting_and_roof_temperature": "unknown", "complete_roof_stack_fire": "unknown",
            "installed_inventory": "unknown", "rail_environment_and_route_yield": "unknown",
        },
        "engineering_constraints_passed": None, "physical_validation": False,
    }


def mount_demand(mass_kg, mount_xy_m, *, cg_m=(0., 0., 0.), acceleration_m_s2=(0., 0., 9.81)):
    """Rigid symmetric equal-stiffness mount demand and independent equilibrium.

    This computes demand, not capacity. Positive z is a supporting reaction;
    negative z requires retention. No bolt grade, plate bearing, prying or
    fatigue resistance is inferred from a physical hole pattern.
    """
    mass = number(mass_kg, "installed equipment mass", minimum=1e-9)
    if not 3 <= len(mount_xy_m) <= 64:
        raise ValueError("bounded noncollinear mount pattern required")
    points = [tuple(number(v, "mount coordinate") for v in xy) for xy in mount_xy_m]
    if any(len(xy) != 2 for xy in points) or len(set(points)) != len(points):
        raise ValueError("mount pattern dimensions/duplicates invalid")
    if len(cg_m) != 3 or len(acceleration_m_s2) != 3:
        raise ValueError("three-dimensional CG and acceleration required")
    cg = [number(v, "equipment CG") for v in cg_m]
    a = [number(v, "mount acceleration") for v in acceleration_m_s2]
    if any(abs(v) > 100 for v in a):
        raise ValueError("acceleration outside bounded rigid demand screen")
    n = len(points)
    # The generated battery and carrier patterns are centered and symmetric.
    sx2 = sum(x*x for x, y in points); sy2 = sum(y*y for x, y in points)
    if min(sx2, sy2) <= 1e-12 or abs(sum(x for x, y in points)) > 1e-9 or abs(sum(y for x, y in points)) > 1e-9 or abs(sum(x*y for x, y in points)) > 1e-9:
        raise ValueError("centered orthogonal mount pattern required by equal-stiffness formulation")
    force = [mass*v for v in a]
    moment = [cg[1]*force[2]-cg[2]*force[1], cg[2]*force[0]-cg[0]*force[2], cg[0]*force[1]-cg[1]*force[0]]
    rows = []
    for x, y in points:
        # Torsion divides tangential shear in proportion to radius.
        fx = force[0]/n - moment[2]*y/(sx2+sy2)
        fy = force[1]/n + moment[2]*x/(sx2+sy2)
        fz = force[2]/n + moment[0]*y/sy2 - moment[1]*x/sx2
        rows.append(dict(position_m=[x,y,0.], reaction_n=[fx,fy,fz], shear_n=math.hypot(fx,fy), retention_required=fz<0))
    sums = [sum(row["reaction_n"][i] for row in rows) for i in range(3)]
    moments = [sum(y*r["reaction_n"][2] for (x,y),r in zip(points,rows)),
               sum(-x*r["reaction_n"][2] for (x,y),r in zip(points,rows)),
               sum(x*r["reaction_n"][1]-y*r["reaction_n"][0] for (x,y),r in zip(points,rows))]
    return dict(schema="osr-rigid-mount-demand/1", mass_kg=mass, cg_m=list(cg), acceleration_m_s2=list(a),
                load_force_n=force, load_moment_nm=moment, mounts=rows,
                force_balance_residual_n=[u-v for u,v in zip(sums,force)],
                moment_balance_residual_nm=[u-v for u,v in zip(moments,moment)],
                engineering_constraints_passed=None, physical_validation=False,
                resistance_state="unknown", basis="rigid centered equal-stiffness demand; scenario accelerations, no capacity or vibration acceptance")


def cooling_loss_duty(pack, segments, *, initial_soc=.8, initial_temperature_c=45.,
                      ambient_temperature_c=45., auxiliary_power_w=0.):
    """Adiabatic pump-loss holdout, including auxiliary demand during braking.

    The independent constant-OCV quadratic and zero-heat-removal balance make
    total cooling loss representable without dividing by a zero conductance.
    This is deliberately a synthetic worst-case screen, not cell propagation.
    """
    if not segments or len(segments) > 10000:
        raise ValueError("nonempty bounded battery duty required")
    V = number(pack["nominal_voltage_v"], "DC voltage", minimum=1e-9)
    R = number(pack["resistance_ohm"], "DC resistance", minimum=1e-12)
    C = number(pack["thermal_capacity_j_k"], "thermal capacity", minimum=1e-9)
    capacity = number(pack["capacity_ah"], "battery capacity", minimum=1e-9)
    aux = number(auxiliary_power_w, "auxiliary power", minimum=0)
    soc = number(initial_soc, "initial SOC", minimum=0)
    temperature = number(initial_temperature_c, "initial temperature")
    ambient = number(ambient_temperature_c, "ambient temperature")
    if not pack["soc_min"] <= soc <= pack["soc_max"]:
        raise ValueError("initial SOC outside battery bounds")
    history = []; chemical = terminal = heat = 0.
    for segment in segments:
        if set(segment) != {"duration_s", "terminal_power_w"}:
            raise ValueError("duration and terminal power required")
        dt = number(segment["duration_s"], "duty duration", minimum=1e-9)
        if dt > 86400:
            raise ValueError("duty duration outside bounded screen")
        P = number(segment["terminal_power_w"], "base terminal power") + aux
        discriminant = V*V-4*R*P
        if discriminant < 0:
            return dict(schema="osr-adiabatic-battery-duty/1", state="outside-domain",
                        reason="power exceeds constant-OCV maximum", history=history,
                        engineering_constraints_passed=None, physical_validation=False)
        # Numerically stable lower-current branch of R I² - V I + P = 0.
        current = 2*P/(V+math.sqrt(discriminant))
        loss = current*current*R
        temperature += loss*dt/C
        soc -= current*dt/(3600*capacity)
        chemical += V*current*dt; terminal += P*dt; heat += loss*dt
        limit = pack["discharge_current_limit_a"] if current >= 0 else pack["charge_current_limit_a"]
        history.append(dict(duration_s=dt, base_terminal_power_w=segment["terminal_power_w"],
                            combined_terminal_power_w=P, current_a=current,
                            temperature_c=temperature, soc=soc,
                            checks=dict(current=abs(current)<=limit,
                                        soc=pack["soc_min"]<=soc<=pack["soc_max"],
                                        temperature=temperature<=pack["temperature_limit_c"])))
    return dict(schema="osr-adiabatic-battery-duty/1", state="completed", history=history,
                terminal_energy_j=terminal, chemical_energy_j=chemical, heat_generated_j=heat,
                heat_removed_j=0., stored_thermal_energy_change_j=C*(temperature-initial_temperature_c),
                electrical_balance_residual_j=chemical-terminal-heat,
                thermal_balance_residual_j=heat-C*(temperature-initial_temperature_c),
                auxiliary_energy_j=aux*sum(row["duration_s"] for row in history),
                ambient_temperature_c=ambient, cooling_conductance_w_k=0.,
                research_constraints_passed=all(all(row["checks"].values()) for row in history),
                engineering_constraints_passed=None, physical_validation=False,
                basis="synthetic total cooling loss; constant nominal OCV, equal string sharing, lumped mass unchanged; no calibrated cells or thermal propagation")


def installation_report(data, *, kind):
    """Attach source compatibility and actual inventory-derived mount demands."""
    if kind not in {"battery", "twin"}:
        raise ValueError("battery or twin installation required")
    pack = data["battery"]
    mass = pack["properties"]["mass_kg"]
    hole_plane = pack["hole_pattern_m"][0][2]
    if any(abs(p[2]-hole_plane) > 1e-12 for p in pack["hole_pattern_m"]):
        raise ValueError("battery mounting holes must share the demand reference plane")
    cg = list(pack["properties"]["cg_m"])
    cg[2] -= hole_plane
    battery_mounts = mount_demand(mass, [p[:2] for p in pack["hole_pattern_m"]],
                                 cg_m=cg, acceleration_m_s2=(4.905,4.905,9.81))
    battery_mounts["reference_hole_plane_z_m"] = hole_plane
    report = dict(schema="osr-subsystem-installation/1", kind=kind,
                  battery_mount_demand=battery_mounts,
                  battery_cooling=dict(assumed_conductance_w_k=pack["cooling_conductance_w_k"],
                                       supplier_curve=None, coolant_mass_kg=None, pump_power_w=None,
                                       cooling_loss_case_required=True, engineering_constraints_passed=None),
                  fire_interfaces=dict(complete_stack_evidence=None, propagation_test=None,
                                       vent_route=None, passenger_isolation=None, state="unknown"),
                  pv=dict(installed=False, energy_credit_j=0., potential_source=deepcopy(SOURCES["renogy-rsp200db-72-g1"]),
                          state="not-installed; roof layout, MPPT, retention, heat and fire qualification required"),
                  complete_installed_inventory=False, physical_validation=False)
    segments = [dict(duration_s=60.,terminal_power_w=200000.),
                dict(duration_s=60.,terminal_power_w=30000.),
                dict(duration_s=20.,terminal_power_w=-75000.)]
    report["battery_cooling_loss_holdout"] = cooling_loss_duty(pack,segments)
    if kind == "twin":
        inputs = data["inputs"]["hvac"]
        report["auxiliary_power"] = auxiliary_power_screen(pack, inputs["module_count_per_car"],
                                                           ambient_c=inputs["thermal_assumptions"]["ambient_c"])
        report["candidate_converter_train_mass_lower_bound_kg"] = data["model"]["family_definition"]["car_count"] * SOURCES["abb-m40-b"]["mass_kg"]
        report["hvac_mount_demands"] = []
        for feature in data["features"]:
            if feature["role"] == "replaceable-hvac-module":
                height = inputs["module_dimensions_m"][2]/2
                demand = mount_demand(feature["mass_kg"], [(x,y) for x in (-.4,.4) for y in (-.65,.65)],
                                      cg_m=(0.,0.,height), acceleration_m_s2=(4.905,4.905,9.81))
                report["hvac_mount_demands"].append(dict(instance_id=feature["instance_id"], demand=demand,
                                                        basis="actual OSR module-foot centers; accelerations are unqualified screening assumptions"))
    return report
