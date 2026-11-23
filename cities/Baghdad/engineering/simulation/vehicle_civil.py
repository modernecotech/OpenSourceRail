"""Airport coupled vehicle, span, footing and passenger-interface planning screens."""
import csv
import hashlib
import io
import json
import math
import tomllib
from pathlib import Path
from zipfile import ZipFile

from cities.Baghdad.engineering.mechanical.civil.develop_civil import box_screen
from cities.Baghdad.engineering.prototype.weights import moving_span

CITY = Path(__file__).resolve().parents[2]
PROTOTYPE = CITY / "engineering/prototype"
STATES = ("low", "central", "high")
SPANS = (10, 20, 25, 30)
# kg per car, nominal mass-centre height above rail and longitudinal location.
# Study allowances for installed groups. No supplier has returned these weights.
GROUPS = {
    "wheelsets_drives_brakes_suspension": ((5200, 6400, 8100), .53, 0),
    "doors_glazing_floor_fitout_seats": ((4300, 5400, 6800), 1.65, 0),
    "roof_hvac_ducts_mounts": ((600, 900, 1450), 3.15, 1),
    "power_converters_cabling_collector_cooling": ((1500, 2100, 2900), .85, 2),
    "skin_finish_welds_fasteners_seals": ((1800, 2400, 3200), 1.85, 0),
    "couplers_gangways_lighting_plumbing_other": ((1300, 1800, 2700), 1.35, -.5),
}
# Released steel bogie frames retained for all options. Scale only body gross stock;
# changes allow extra section thickness, joints, inserts and metallic reinforcement.
MATERIAL = {"steel": (1., 1., 1.), "aluminium": (.60, .78, .97), "hybrid": (.55, .73, 1.03)}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def article_data():
    with ZipFile(PROTOTYPE / "airport-prototype.zip") as archive:
        checks = json.loads(archive.read("manifest.json"))["sha256"]
        def verified(name):
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != checks[name]:
                raise ValueError("Stale Airport prototype member " + name)
            return data
        record = json.loads(verified("mechanical.json"))
        cage = json.loads(verified("civil-article.json"))
        cuts = list(csv.DictReader(io.StringIO(verified("revised-cuts.csv").decode())))
    if cage["mechanical_evaluation_id"] != record["evaluation_id"] or cage["candidate_id"] != record["candidate_id"]:
        raise ValueError("Mixed Airport vehicle and cage")
    bogie = 2 * sum(float(r["gross_mass_kg"]) for r in cuts if r["assembly"] == "bogie")
    return record, cage, bogie


def load_case(record, bogie, service, cars, material, state):
    i = STATES.index(state)
    body = record["mass"]["cut_kg_per_car"] - bogie
    groups = {k: (m[i], z, x) for k, (m, z, x) in GROUPS.items()}
    groups.update(body_stock=(body * MATERIAL[material][i], 1.8, 0),
                  bogie_frame_stock=(bogie, .55, 0),
                  independent_service_pack=(service["battery_mass_allowance_t"]*1000/cars, .85, -2.0))
    passengers = 700 * cars // 6
    person_kg = (65, 75, 90)[i]
    passenger_x = (0, .8, 1.8)[i]
    tare = sum(m for m, _, _ in groups.values())
    loaded = tare + passengers * person_kg / cars
    items = list(groups.values()) + [(loaded-tare, 1.6, passenger_x)]
    x = sum(m * cx for m, _, cx in items) / loaded
    z = sum(m * cz for m, cz, _ in items) / loaded
    pivot = record["bogie_translations_m"][1]
    # Equal axle shares within each bogie, identical occupied cars. Moments about car centre.
    front = loaded * (.5 + x / (2*pivot))
    axles = [(loaded-front)/2]*2 + [front/2]*2
    g = 9.80665
    return dict(group_kg_per_car={k: v[0] for k, v in groups.items()}, people=passengers,
                passenger_kg_each=person_kg, passenger_centroid_x_m=passenger_x,
                tare_train_kg=tare*cars, loaded_train_kg=loaded*cars,
                loaded_car_cg_x_m=x, loaded_car_cg_z_m=z, axle_kg_per_car=axles,
                bogie_kg_per_car=[loaded-front, front], gravity_balance_kg=sum(axles)-loaded,
                moment_balance_kg_m=(2*front-loaded)*pivot-loaded*x,
                level_stop_from_72_kmh_no_regen_kwh=loaded*cars*20**2/2/3.6e6,
                service_brake_force_on_2pct_descent_kn=loaded*cars*(1.0+.02*g)/1000,
                required_adhesion_all_axles_at_1_m_s2_on_2pct=(1.0+.02*g)/g,
                static_roll_unloading_fraction_at_1_m_s2_and_1p435m_gauge=2*z/(1.435*g))


def span_case(length, case, cars, record, cfg, cage):
    overhang = .25
    span = length - 2*overhang
    offsets = record["interfaces"]["body_from_axle_x_m"]
    centres = record["interfaces"]["formation_body_from_car_x_m"][:cars]
    axles = [(f"C{i+1}-A{j+1}", cx+dx, mass*cfg["materials"]["gravity_m_s2"]/1000)
             for i, cx in enumerate(centres) for j, (dx, mass) in enumerate(zip(offsets,case["axle_kg_per_car"]))]
    live = moving_span(axles, span, overhang)
    track = dict(beam_stock_length_m=length, effective_span_m_hypothesis=span,
                 bearing_seat_xy_m_from_stock_end=[[x,y] for x in (overhang,length-overhang) for y in (-.65,.65)],
                 moving_gravity_only=dict(stock_overhang_per_end_m=overhang,
                    max_end_reaction_kn_sampled=live["max_reaction"]["value"],
                    max_live_moment_knm_sampled=live["max_moment"]["value"]))
    box = dict(cfg["box"], lift_pick_inset_m=length*.2)
    actions = box_screen(box, cfg["materials"], track, cfg["pier"])
    strand = cage["strand"]
    initial = strand["strand_count"] * strand["studied_initial_force_fraction"] * strand["catalogue_minimum_breaking_kn"]
    rows = {}
    for loss in strand["assumed_losses"]:
        effective = initial*(1-loss)
        rows[str(loss)] = effective-actions["effective_axial_force_for_zero_bottom_stress_kn"]
    placed = 2 * (1800//length)
    # Square footing rigid-contact sensitivity, eccentricity about one horizontal axis.
    footing = cfg["pier"]["footing_width_m"]
    pressure = actions["pier_gravity_screen"]["uniform_soil_contact_pressure_kpa"]
    eccentricity = .20
    return dict(stock_length_m=length, moving_load=live, span_actions=actions,
                effective_strand_margin_kn_by_loss=rows,
                original_cage_screen="compression target met" if min(rows.values()) >= 0 else "revise section or cage",
                eccentric_footing_max_kpa=pressure*(1+6*eccentricity/footing),
                eccentric_footing_min_kpa=pressure*(1-6*eccentricity/footing),
                trial_load_eccentricity_m=eccentricity,
                representative_route_m=1800, beams=placed, bearings=4*placed,
                supports_and_foundations=placed+2, beam_concrete_m3=placed*actions["gross_concrete_m3"],
                crane_chart_60t_stock_only_margin_t=60-actions["equivalent_stock_t"])


def evaluate(inputs=None):
    opt = {"cars": 6, "material": "steel", "span_m": 10, **(inputs or {})}
    cars, mat, length = opt["cars"], opt["material"], opt["span_m"]
    if cars not in (3,6) or mat not in MATERIAL or length not in SPANS:
        raise ValueError("Outside the 3/6-car, three-body, four-span Airport experiment")
    record, cage, bogie = article_data()
    cfg = tomllib.loads((CITY / "engineering/mechanical/civil/concept.toml").read_text())
    city = tomllib.loads((CITY / "system.toml").read_text())
    service = city["service_power"]
    cases = {material: {state: load_case(record, bogie, service, cars, material, state)
                        for state in STATES} for material in MATERIAL}
    selected = cases[mat]["central"]
    spans = {str(n): span_case(n, selected, cars, record, cfg, cage) for n in SPANS}
    active = spans[str(length)]
    edges = record["doorway"]["per_edge_allowances_m"]
    aperture = min(record["doorway"]["rough_widths_m"])
    demand = ((service["control_continuous_kw"]+service["other_essential_continuous_kw"])*service["protected_outage_hours"]
              +service["brake_event_kwh"]+service["door_egress_event_kwh"])*(1+service["energy_reserve_fraction"])
    battery = service["battery_nominal_kwh"]*service["usable_fraction"]
    # Linear gross-section reproduction uses the same distributed gravity pattern
    # and steel stiffness as the released two-dimensional sidewall.
    steel_vertical = {}
    if mat == "steel":
        reference_car_kg = 1000*record["planning_crowd_train_t"]/6
        for state, row in cases[mat].items():
            ratio = row["loaded_train_kg"]/cars/reference_car_kg
            steel_vertical[state] = {
                factor: dict(peak_vertical_mm=ratio*source["peak_nodal_vertical_mm"],
                             peak_section_stress_mpa=ratio*source["max_end_axial_plus_bending_mpa"],
                             nominal_yield_minus_peak_mpa=355-ratio*source["max_end_axial_plus_bending_mpa"],
                             deformed_width_loss_mm=ratio*source["door_width"]["worst_width_loss_mm"])
                for factor, source in record["body_vertical_screens"].items()}
    state_spans = {state: (active if state == "central" else
                   span_case(length, row, cars, record, cfg, cage)) for state, row in cases[mat].items()}
    ga = json.loads((PROTOTYPE/"vehicle-factory/installed-ga.json").read_bytes())
    if ga["candidate_id"] != record["candidate_id"] or ga["mechanical_evaluation_id"] != record["evaluation_id"]:
        raise ValueError("Vehicle arrangement and article ancestry differ")
    seat_gap = min(pad["stock_face_gap_mm"] for bogie_row in ga["geometry"]["bogies"]
                   for pad in bogie_row["pads"] if pad["type"] == "secondary_top")
    payload = (selected["loaded_train_kg"]-selected["tare_train_kg"])/cars
    # Passive incremental secondary compliance; level regulation/free stroke unknown.
    loaded_end_fraction = .5+selected["passenger_centroid_x_m"]/(2*record["bogie_translations_m"][1])
    passenger_force_per_secondary_kn = payload*9.80665*loaded_end_fraction/2000
    spring_cases = [dict(spring_kn_per_mm=k, extra_compression_mm=passenger_force_per_secondary_kn/k,
                         trial_40mm_travel_margin_mm=40-passenger_force_per_secondary_kn/k)
                    for k in (.6, 1.0, 1.6)]
    return dict(evaluation_id=digest([record["evaluation_id"], cage["evaluation_id"], ga["evaluation_id"], cfg, city["service_power"],
                                      cars, mat, length, hashlib.sha256(Path(__file__).read_bytes()).hexdigest()]),
                parent_candidate_id=record["candidate_id"], parent_mechanical_evaluation_id=record["evaluation_id"],
                physical_id=digest([record["candidate_id"], cage["physical_id"], cars, mat, length]),
                cases=cases, selected=selected, spans=spans, selected_span=active, selected_span_load_cases=state_spans,
                loaded_train_kg=selected["loaded_train_kg"], tare_train_kg=selected["tare_train_kg"],
                planning_parent_crowd_kg=record["planning_crowd_train_t"]*1000,
                equipment_mass_basis="Unweighed scenario groups. Each car shares the train service pack. Body alternatives require redesigned joints, fire and repair evidence.",
                structure=dict(body_vertical=steel_vertical or None,
                    scope="Steel linear gross sidewall response scaled by whole-car gravity under the released distribution; identical patterns at 1.0 and 1.3 gravity factors. New CG, alternative joints, fatigue, buff, twist, crash and drive-mount strength require evaluation.",
                    full_installed_cost_usd=None, physical_acceptance=False),
                interfaces=dict(secondary_stock_separation_mm=seat_gap,
                    trial_spring_stack_margin_mm={str(stack): seat_gap-stack for stack in (145,155,165)},
                    passive_spring_incremental_payload_cases=spring_cases,
                    bogie_stock_extraction_m=abs(ga["geometry"]["bogies"][0]["signed_outward_travel_m"]),
                    bare_bogie_service_lane_m=ga["geometry"]["bogies"][0]["service_lane_clear_width_m"],
                    fit_basis="Static stock stack trials exclude shims and tolerances. The 40 mm incremental travel is a study hypothesis. Wheel, motor, hoses, accessible floor step and dynamic limits await returns.",
                    allocated_door_clear_margin_mm=1000*(aperture-2*sum(edges.values())-record["doorway"]["required_fitted_m"]),
                    doubled_loaded_distortion_margin_mm=1000*(aperture-2*(sum(edges.values())+edges["loaded_distortion_per_edge_m"])-record["doorway"]["required_fitted_m"]),
                    service_battery_usable_kwh=battery, outage_brake_and_egress_demand_kwh=demand,
                    battery_margin_kwh=battery-demand, aged_80pct_capacity_margin_kwh=.8*battery-demand,
                    brake_adhesion_at_0p08_margin=.08-selected["required_adhesion_all_axles_at_1_m_s2_on_2pct"],
                    brake_heat_capacity_kwh=None, accessible_step_limit_mm=None,
                    static_platform_gap_m=cage["station_interfaces"]["static_level_horizontal_gap_m"]),
                station_bay=record["civil"]["station_bay"],
                disposition="Engineering screen only. Survey, measured running loads, transfer/loss/soil tests, emergency brake, fitted accessible boarding and independent approvals remain open.")
