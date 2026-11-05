"""Compact launch demand and cost break-even research; no available drive map.

One selected vehicle supplies the accounted mass/rotating-stock lower bound.
Alternative hardware is not materialized and never inherits acceptance or a
complete installed mass. Fifteen analytic profiles need no new solver framework.
"""
from itertools import product
from math import ceil, isfinite, pi, sqrt
from pathlib import Path
import argparse
import json
import tomllib

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, operations, braking, vehicle
from engineering.station_rail.common import brief, digest, encoded, identity

PRODUCER = "engineering/design_search/compact_launch.py"
SPEC = "campaigns/compact-affordable-launch.toml"
EXECUTING = {Path(module.__file__):digest(module.__file__) for module in (selection,operations,braking,vehicle)}
EXECUTING[Path(__file__)]=digest(__file__)
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
    manufacturing_release=False, operating_release=False, selected_reference_changed=False,
    physical_journey_completed=False, native_evaluator_admission=False, installed_mass_complete=False)
PRINCIPLES = [dict(source_id="intamin-friction-launch-principle",url="https://www.intamin.com/category/news/",
    detail_url="https://www.intamin.com/project/quantum-accelerator/",
    claim="A manufacturer documents friction-wheel launch on an amusement ride.",
    transfer="Passenger railway duty, accessibility, wear, costs and qualification are not established by that example."),
    dict(source_id="doppelmayr-cable-apm-principle",url="https://www.doppelmayr.com/en/systems/automated-people-mover/",
    claim="A manufacturer documents rope-propelled, rail-based automated people movers.",
    transfer="A short-stroke detachable launch winch is a different configuration; no supplier performance or price is inherited.")]
UNRESOLVED = ["Available thrust/torque versus speed, contact position and temperature",
    "Added hardware mass, structure, couplers, suspension and installed CG/axle loads",
    "Repeated thermal duty, electrical peak demand, cooling and protection",
    "Wear, contamination, failed release, inspection, maintenance and renewal",
    "Independent service/emergency/parking brakes, degraded stops, rescue and evacuation",
    "Passenger acceleration/jerk limits, wheelchair securement and accessibility",
    "Complete factory, delivery, installation and whole-life costs"]


def positive(x):
    return type(x) in (int,float) and isfinite(x) and x > 0


def specification(root=ROOT):
    value=tomllib.loads((Path(root)/SPEC).read_text())
    if (value.get("schema")!="osr-compact-launch-research/1" or value.get("purpose")!="next-experiment"
            or value.get("reference_changes_allowed") is not False or value.get("native_dispatch") is not False):
        raise ValueError("Explicit non-promoting compact-launch contract required")
    c,s=value["service"],value["sizing"]
    if (c["distance_m"],c["headway_s"],c["dwell_s"],c["service_deceleration_m_s2"])!=(2000.,120.,35.,.6):
        raise ValueError("This comparison requires the declared common route/service")
    for name,limit,high in (("acceleration_m_s2",8,3.),("speed_m_s",5,40.),("jerk_m_s3",3,3.)):
        items=c[name]
        if (not isinstance(items,list) or not 1<=len(items)<=limit or len(set(items))!=len(items)
                or any(not positive(x) or x>high for x in items)):
            raise ValueError("Bounded positive unique research samples required: "+name)
    count=len(c["acceleration_m_s2"])*len(c["speed_m_s"])
    if type(value["maximum_cases"]) is not int or not count<=value["maximum_cases"]<=100:
        raise ValueError("Bounded analytic comparison required")
    for name in ("transmission_efficiency","motor_efficiency","vfd_efficiency","lim_electrical_to_mechanical_efficiency"):
        if not positive(s[name]) or s[name]>1:raise ValueError("Declared efficiency must lie in (0,1]")
    for name in ("rotary_motor_shaft_rating_W","roller_radius_m","winch_drum_radius_m","winch_return_speed_m_s","winch_coupling_reset_s"):
        if not positive(s[name]):raise ValueError("Positive sizing hypothesis required")
    for name in ("roller_friction_coefficients","wheel_adhesion_coefficients","winch_available_strokes_m"):
        if not 1<=len(s[name])<=4 or any(not positive(x) for x in s[name]):raise ValueError("Bounded contact/stroke hypotheses required")
    if (s["production_shifts_per_day"],s["construction_shifts_per_day"],s["operation_shift_scenarios"])!=(2,2,[2,3]):
        raise ValueError("Two-shift production/construction and two/three-shift operation scenarios required")
    return value


def jerk_bound(speed,acceleration,jerk):
    """Rest-to-speed symmetric S-curve with zero initial/final acceleration."""
    if not all(positive(x) for x in (speed,acceleration,jerk)):raise ValueError("Positive finite jerk inputs required")
    triangular=speed<acceleration*acceleration/jerk
    peak=sqrt(speed*jerk) if triangular else acceleration
    ramp=peak/jerk
    plateau=0. if triangular else speed/acceleration-ramp
    duration=2*ramp+plateau
    return dict(jerk_m_s3=jerk,peak_acceleration_m_s2=peak,ramp_time_s=ramp,plateau_time_s=plateau,
        total_time_s=duration,distance_m=.5*speed*duration,triangular_acceleration=triangular,
        passenger_comfort_qualified=False,integrated_jerk_journey=None,
        scope="Necessary launch stroke only; not substituted into the constant-acceleration journey")


def _mechanisms(profile,jerks,train_length,fin_offset,mass_train,cars,sizing,reference_length):
    force=profile["peak_launch_force_N_per_car"]*cars
    power=profile["peak_launch_power_W_per_car"]*cars
    stroke=profile["launch_distance_m"]
    shaft=power/sizing["transmission_efficiency"]
    rotary=dict(required_shaft_power_W=shaft,required_electrical_power_W=shaft/sizing["motor_efficiency"]/sizing["vfd_efficiency"],
        assumed_motor_shaft_rating_W=sizing["rotary_motor_shaft_rating_W"],
        minimum_motor_count=ceil(shaft/sizing["rotary_motor_shaft_rating_W"]),
        redundancy_derating_and_duty_verified=False)
    rows=[]
    def add(name,quantities,scopes):
        value=dict(mechanism=name,reference_profile_id=profile["profile_id"],required_train_force_N=force,
            required_train_mechanical_power_W=power,quantities=quantities,cost_scopes=scopes,
            added_installed_mass_kg=None,complete_installed_cost=None,available_force_map_id=None,
            materialized_candidate_id=None,integrated_selection=None,**FLAGS)
        value["research_option_id"]=identity(dict(mechanism=name,quantities=quantities))
        rows.append(value)
    shared=operations.station_zone(profile,reference_length,train_length_m=train_length)
    full_launch=max(0.,stroke+train_length-2*fin_offset)
    add("current-shared-LIM",dict(shared_winding_m=reference_length,required_shared_winding_m=shared["required_shared_winding_m"],
        electrical_power_W=power/sizing["lim_electrical_to_mechanical_efficiency"],geometry_full_engagement=shared["geometry_full_engagement"]),
        ["Primary copper/steel, supports, converters, switching, cooling, cables, civil works", "Independent brakes and maintenance; receiving-energy recovery remains unverified"])
    add("compact-launch-LIM",dict(commanded_travel_m=stroke,outgoing_reach_beyond_initial_nose_m=stroke-fin_offset,
        full_train_fin_launch_envelope_m=full_launch,
        jerk_full_train_fin_envelopes_m=[dict(jerk_m_s3=j["jerk_m_s3"],length_m=j["distance_m"]+train_length-2*fin_offset) for j in jerks],
        electrical_power_W=power/sizing["lim_electrical_to_mechanical_efficiency"]),
        ["Higher thrust per active metre, current, cooling, commutation and protection", "All initial train fins plus launch travel; independent receiving brake retained"])
    add("station-pinch-rollers",dict(**rotary,roller_radius_m=sizing["roller_radius_m"],
        total_contact_normal_force_N=[dict(mu=mu,total_N=force/mu) for mu in sizing["roller_friction_coefficients"]],
        equivalent_total_roller_shaft_torque_Nm=force*sizing["roller_radius_m"],
        roller_speed_rpm_at_cap=profile["peak_speed_m_s"]*60/(2*pi*sizing["roller_radius_m"]),
        optimistic_bank_length_lower_bound_m=max(2*sizing["roller_radius_m"],stroke-train_length),
        continuous_strip_across_couplers_verified=False,actual_contact_geometry=None),
        ["Rotary motors/VFD, tyres, bearings, opposing clamps, guards and failed-release protection", "Reaction strips, mounts/coupler load paths, contamination, wear and replacement"])
    cycle=profile["launch_time_s"]+stroke/sizing["winch_return_speed_m_s"]+sizing["winch_coupling_reset_s"]
    add("short-stroke-winch-capstan",dict(**rotary,minimum_line_tension_N=force,
        minimum_drum_torque_Nm=force*sizing["winch_drum_radius_m"],required_stroke_m=stroke,
        stroke_screens=[dict(available_stroke_m=x,constant_acceleration_fits=stroke<=x,
            jerk_cases_fit=[j["distance_m"]<=x for j in jerks]) for x in sizing["winch_available_strokes_m"]],
        ideal_launch_return_reset_cycle_s=cycle,minimum_parallel_launch_resources=ceil(cycle/120.),
        jerk_cycle_bounds_s=[dict(jerk_m_s3=j["jerk_m_s3"],cycle_s=j["total_time_s"]+j["distance_m"]/sizing["winch_return_speed_m_s"]+sizing["winch_coupling_reset_s"]) for j in jerks],
        coupling_reset_and_train_release_verified=False),
        ["Winch/motor/VFD, drum, rope, trolley/grip, return and tensioning path", "Anchors, coupling loads, reset capacity, rope inspection and independent braking"])
    add("rotary-wheel-traction-short-feed",dict(**rotary,
        required_driven_weight_fractions=[dict(mu=mu,fraction=force/(mu*mass_train*operations.G),
            two_of_twelve_bogies_equal_load_fraction=2/12,
            two_bogies_necessary_bound_fits=force/(mu*mass_train*operations.G)<=2/12) for mu in sizing["wheel_adhesion_coefficients"]],
        minimum_continuously_fed_travel_m=stroke,feed_contact_geometry=None,
        powered_bogie_mass_and_axle_loading=None,onboard_traction_store_assumed=False),
        ["Powered axles/bogies, motors/gears/VFD, collectors, protected short feed, switching and cooling", "Added vehicle mass changes civil/force/energy; wet adhesion, recovery and maintenance"])
    return rows


def evaluate(root=ROOT):
    if any(digest(path)!=sha for path,sha in EXECUTING.items()):raise ValueError("Loaded compact-launch producer changed")
    root=Path(root);spec=specification(root);selected=selection.load(root);car=selected["vehicle"]
    b=brief(root);c,s=spec["service"],spec["sizing"];cars=b["vehicle"]["cars"]
    rotor=braking.rotating_stock(car);mass=car["mass"]["accounted_cap_loaded_kg_per_car"]
    train_length=cars*b["vehicle"]["body_length_m"]+(cars-1)*b["vehicle"]["coupling_gap_m"]
    fin_offset=(b["vehicle"]["body_length_m"]-b["propulsion"]["secondary_length_m"])/2
    names=[PRODUCER,SPEC,"engineering/development_baseline/selection.py","engineering/development-baseline.toml",
        "engineering/station_rail/operations.py","engineering/station_rail/braking.py","engineering/station_rail/vehicle.py",
        "engineering/station_rail/common.py","engineering/station_rail/brief.toml"]
    sources={**car["source_sha256"],**selected["source_sha256"],**{n:digest(root/n) for n in names}}
    baseline=operations.profile(c["distance_m"],mass,rotating_equivalent_mass_kg_per_car=rotor["equivalent_inertial_mass_kg_per_car"])
    zones=[operations.station_zone(baseline,x,train_length_m=train_length) for x in b["service"]["retired_station_winding_library_m"]]
    feasible=[z for z in zones if z["nominal_resource_screen"]=="pass"]
    if not feasible:raise ValueError("Reference winding catalogue has no necessary-screen survivor")
    reference=min(feasible,key=lambda z:z["length_m"])
    rows=[]
    for acceleration,speed in product(c["acceleration_m_s2"],c["speed_m_s"]):
        p=operations.profile(c["distance_m"],mass,speed_cap_m_s=speed,acceleration_m_s2=acceleration,
            rotating_equivalent_mass_kg_per_car=rotor["equivalent_inertial_mass_kg_per_car"],cars=cars,loading="normal-accounted-reference")
        jerks=[jerk_bound(speed,acceleration,j) for j in c["jerk_m_s3"]]
        row=dict(acceleration_m_s2=acceleration,speed_m_s=speed,constant_acceleration_distance_m=speed*speed/(2*acceleration),
            constant_acceleration_time_s=speed/acceleration,profile=p,jerk_bounds=jerks,mechanisms=[],cost_break_even=None)
        if p["reachable"]:
            row["mechanisms"]=_mechanisms(p,jerks,train_length,fin_offset,mass*cars,cars,s,reference["length_m"])
            length=row["mechanisms"][1]["quantities"]["full_train_fin_launch_envelope_m"]
            row["cost_break_even"]=dict(reference_shared_length_m=reference["length_m"],compact_launch_length_m=length,
                saved_length_m=reference["length_m"]-length,
                maximum_compact_per_m_cost_ratio_if_other_costs_equal=reference["length_m"]/length,
                equation="L_compact*c_compact + delta_fixed + delta_braking + PV(delta_energy+wear+maintenance+renewal) < L_reference*c_reference",
                allowance_for_alternative_hardware="Alternative total installed + lifecycle increment must be below avoided reference costs; no unit rates assumed",
                complete_cost_winner=None)
        row["case_id"]=identity(row);rows.append(row)
    value=dict(schema="osr-compact-launch-comparison/1",requirement_revision=spec["requirement_revision"],purpose="next-experiment",
        reference_vehicle_candidate_id=car["candidate_id"],selection_id=selected["selection_id"],source_sha256=sources,
        configuration=spec,normal_accounted_mass_kg_per_car=mass,rotating_stock=rotor,train_length_m=train_length,
        reference_profile=baseline,reference_station=reference,
        reference_zone_decomposition=dict(outgoing_m=reference["launch_zone_m"],receiving_m=reference["receiving_zone_m"],
            exact_shared_m=reference["required_shared_winding_m"],catalogue_m=reference["length_m"],
            explanation="Rounded825m=496m+329m;900m is a catalogue allocation. Receiving propulsion is optional; qualified independent braking is mandatory."),
        cases=rows,principle_sources=PRINCIPLES,unresolved=UNRESOLVED,
        complete_installed_mass_kg=None,complete_installed_cost=None,integrated_selection=None,
        native_solver_jobs=0,execution="completed-analytic-research",numerical_validity="analytic-target-requirements",
        engineering_screen="unvalidated-drive-brake-contact-and-passenger-domains",**FLAGS)
    if (any(digest(root/name)!=sha for name,sha in sources.items())
            or any(digest(path)!=sha for path,sha in EXECUTING.items())):raise ValueError("Compact-launch source epoch changed")
    value["comparison_id"]=identity(value);return value


def markdown(result):
    z=result["reference_zone_decomposition"]
    lines=["# Compact acceleration and alternative launch mechanisms", "",
        f"Reference vehicle `{result['reference_vehicle_candidate_id']}`; six 17 m cars, 276 normal places, 2 km and 120 s target headway.",
        f"Normal accounted mass is {result['normal_accounted_mass_kg_per_car']/1000:.3f} t/car; complete installed mass remains unknown.","",
        f"The reference's **{z['exact_shared_m']:.3f} m shared envelope = {z['outgoing_m']:.0f} m outgoing + {z['receiving_m']:.3f} m receiving**, rounded 825 m; catalogue 900 m.",
        "Launch-only hardware is compared separately. Receiving motors are optional; independent qualified brakes remain mandatory.","",
        "|Speed km/h|Acceleration m/s²|Constant-a travel m|Time s|Jerk 0.5 travel m|Peak train force kN|Peak train mechanical MW|",
        "|---:|---:|---:|---:|---:|---:|---:|"]
    for row in result["cases"]:
        p=row["profile"]
        force=p["peak_launch_force_N_per_car"]*6/1000 if p["reachable"] else None
        power=p["peak_launch_power_W_per_car"]*6/1e6 if p["reachable"] else None
        lines.append(f"|{row['speed_m_s']*3.6:.1f}|{row['acceleration_m_s2']:.1f}|{row['constant_acceleration_distance_m']:.1f}|{row['constant_acceleration_time_s']:.1f}|{row['jerk_bounds'][0]['distance_m']:.1f}|{force:.1f}|{power:.3f}|" if force is not None else f"|{row['speed_m_s']*3.6:.1f}|{row['acceleration_m_s2']:.1f}|—|—|—|unreachable|—|")
    example=next((r for r in result["cases"] if r["speed_m_s"]==20. and r["acceleration_m_s2"]==1. and r["profile"]["reachable"]),None)
    if example:
        p=example["profile"];rotary=example["mechanisms"][2]["quantities"]
        jerk=next((j for j in example["jerk_bounds"] if j["jerk_m_s3"]==.5),None)
        lines += ["", f"At **72 km/h and 1.0 m/s²**, constant-acceleration launch travel falls from 500 m to **200 m**, and launch time from 50 s to **20 s**. Required train force is **{p['peak_launch_force_N_per_car']*6/1000:.1f} kN** and peak mechanical power **{p['peak_launch_power_W_per_car']*6/1e6:.3f} MW**.",
            f"The complete launch-only fin envelope is **{example['mechanisms'][1]['quantities']['full_train_fin_launch_envelope_m']:.1f} m**. Rotary options need at least **{rotary['minimum_motor_count']} × 250 kW shaft units** under the declared transmission assumption; this is demand sizing, not a product approval."]
        if jerk:lines.append(f"Adding the assumed 0.5 m/s³ jerk ramps gives **{jerk['distance_m']:.1f} m travel and {jerk['total_time_s']:.1f} s** before engagement margins. Passenger comfort, wheelchair protection and the integrated jerk journey remain unverified.")
    lines += ["", "Higher acceleration shortens the launch but raises force, peak power and passenger-interface demands. Jerk columns are launch bounds, not rerun journeys.",
        "Full-train LIM launch coverage also includes initially occupied fins: travel + 104.5 − 8 m. Outgoing reach alone is not installed winding length.","",
        "|Mechanism|Useful quantitative comparison|Missing engineering and cost scope|", "|---|---|---|"]
    explanations=[("Shared LIM","900m retained comparator","Launch/receiving maps, converters, cooling and all installed works"),
        ("Compact launch LIM","Travel+train fin span; higher per-metre cost break-even ratio","Higher thrust/current/heat per metre; independent brake and renewal effects"),
        ("Pinch rollers","Sum of contact normal forces ≥F/μ; rotary shaft power and 250 kW unit counts","Clamp/strip attachments, contact gaps, coupling loads, failed release and tyre wear"),
        ("Winch/capstan","Line tension ≥F, drum torque ≥F×radius; 100/200 m stroke and reset-cycle bounds","Grip/trolley/return path, anchors, rope wear, coupling release and parallel resource count"),
        ("Wheel traction with short feed","Driven weight fraction ≥F/(μmg); two of 12 bogies explicitly screened","New powered bogies/vehicle mass, collectors, live-feed protection, adhesion and recovery")]
    lines += ["|"+"|".join(row)+"|" for row in explanations]
    lines += ["", "The 250 kW shaft motor is a sizing hypothesis, not a supplier product selection. Transmission/motor/VFD efficiencies and friction are explicit assumptions in result.json.",
        "No unit prices are invented. Break-even requires `Lcompact*ccompact + extra fixed/braking/lifecycle costs < 900*creference`; all omitted scope remains open.",
        "Two-shift production/construction and two/three-shift operating scenarios are retained; workforce and availability require a delivery model.","",
        "Intamin documents a [friction-wheel launch example](https://www.intamin.com/project/quantum-accelerator/); Doppelmayr documents [rope-propelled rail APMs](https://www.doppelmayr.com/en/systems/automated-people-mover/). These establish principles, not this railway's cost, performance or approval.","",
        "Every available-force, thermal, wear, braking, coupler, maintenance, accessibility and physical-acceptance gate remains open.",
        f"Comparison `{result['comparison_id']}`.",""]
    return "\n".join(lines)


def run(output,root=ROOT):
    output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError("Fresh immutable output directory required")
    result=evaluate(root);output.mkdir(parents=True,exist_ok=False)
    (output/"inputs.json").write_bytes(encoded(dict(configuration=result["configuration"],source_sha256=result["source_sha256"],reference_vehicle_candidate_id=result["reference_vehicle_candidate_id"])))
    (output/"result.json").write_bytes(encoded(result));(output/"README.md").write_text(markdown(result))
    manifest=dict(schema="osr-compact-launch-package/1",comparison_id=result["comparison_id"],files={name:digest(output/name) for name in ("inputs.json","result.json","README.md")})
    manifest["package_id"]=identity(manifest);(output/"manifest.json").write_bytes(encoded(manifest))
    return dict(output=str(output),comparison_id=result["comparison_id"],package_id=manifest["package_id"],cases=len(result["cases"]),**FLAGS)


def verify(output,root=ROOT):
    """Read-only full analytic replay, with no native solver dispatch."""
    output=Path(output)
    manifest=json.loads((output/"manifest.json").read_bytes())
    expected=manifest.pop("package_id")
    if (manifest.get("schema")!="osr-compact-launch-package/1" or expected!=identity(manifest)
            or set(manifest["files"])!={"inputs.json","result.json","README.md"}):
        raise ValueError("Compact-launch package identity differs")
    if any(digest(output/name)!=sha for name,sha in manifest["files"].items()):raise ValueError("Compact-launch package payload differs")
    result=evaluate(root)
    inputs=dict(configuration=result["configuration"],source_sha256=result["source_sha256"],reference_vehicle_candidate_id=result["reference_vehicle_candidate_id"])
    if ((output/"result.json").read_bytes()!=encoded(result) or (output/"inputs.json").read_bytes()!=encoded(inputs)
            or (output/"README.md").read_text()!=markdown(result) or manifest["comparison_id"]!=result["comparison_id"]):
        raise ValueError("Compact-launch package does not replay from current sources")
    return dict(verified=True,package_id=expected,comparison_id=result["comparison_id"],native_solver_jobs=0,**FLAGS)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args();print(json.dumps(verify(args.output) if args.verify else run(args.output)))


if __name__=="__main__":main()
