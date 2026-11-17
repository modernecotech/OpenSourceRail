"""Join bounded powered-car, supply and service research without physical approval.

The native IFC is a nominal interface-box model. It is neither detailed CAD
nor an installed mass, clearance or structural qualification.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from engineering.station_rail.common import encoded, identity
from engineering.vehicle_parts import powered_bogie_prototype
from engineering.design_search import powered_bogie_screen, equal_service_handoff


ROOT = Path(__file__).resolve().parents[2]
VEHICLE = "docs/design-engine/v07-powered-vehicle/plan.json"
ELECTRICAL = "docs/design-engine/v07-powered-bogie/screen.json"
ELECTRICAL_INPUT = "docs/design-engine/v07-powered-bogie/input.json"
SERVICE = "docs/design-engine/v07-architecture-decision/result.json"
SERVICE_INPUT = "docs/design-engine/v07-architecture-decision/input.json"
SELECTED = "docs/design-engine/current/summary.json"
SELECTED_MANIFEST = "docs/design-engine/current/manifest.json"
SOURCES = (VEHICLE, ELECTRICAL, ELECTRICAL_INPUT, SERVICE, SERVICE_INPUT,
           SELECTED, SELECTED_MANIFEST,
           "engineering/design_search/v07_prototype_bundle.py")
G = 9.81


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(root: Path):
    root = Path(root)
    v = json.loads((root / VEHICLE).read_bytes())
    e = json.loads((root / ELECTRICAL).read_bytes())
    s = json.loads((root / SERVICE).read_bytes())
    electrical_input = json.loads((root / ELECTRICAL_INPUT).read_bytes())
    service_input = json.loads((root / SERVICE_INPUT).read_bytes())
    selected = json.loads((root / SELECTED).read_bytes())
    if encoded(powered_bogie_prototype.build(root)) != (root / VEHICLE).read_bytes():
        raise ValueError("Mechanical child differs from current authenticated sources")
    if encoded(powered_bogie_screen.evaluate(electrical_input, root)) != (root / ELECTRICAL).read_bytes():
        raise ValueError("Electrical child differs from current authenticated sources")
    if encoded(equal_service_handoff.evaluate(service_input, root)) != (root / SERVICE).read_bytes():
        raise ValueError("Equal-service screen differs from current authenticated sources")
    parent = selected["candidate_id"]
    if (parent != v["selected_parent_candidate_id"]
            or parent != e["parent_selected_vehicle_candidate_id"]
            or parent != s["selected_reference_vehicle_candidate_id"]):
        raise ValueError("Mixed selected-parent identities")
    if (v["physical_candidate_id"] != identity(v["physical_definition"])
            or v["evaluation_id"] == e["evaluation_id"]
            or s["physical_candidate_id"] is not None):
        raise ValueError("Mechanical, electrical or service identity differs")
    supply = next((r for r in e["supply_research_configurations"]
                   if r["name"] == "rigid-overhead-dc"), None)
    if supply is None or supply["research_physical_candidate_id"] != identity(supply["definition"]):
        raise ValueError("Overhead supply component definition differs")
    mech = v["physical_definition"]
    power = supply["definition"]
    if (mech["cars"] != 6 or mech["driven_axles_per_train"] != 24
            or mech["driven_axles_per_car"] != 4 or power["driven_axles"] != 24
            or power["motorized_bogies"] != 12 or mech["rail_gauge_m"] != 1.435
            or power["conductor_nominal_V"] != 1500
            or "roof collector" not in mech["electrical_pickup"]
            or "overhead" not in mech["electrical_pickup"]
            or mech["parent_candidate_id"] != parent
            or mech["traction_store"] != "none selected; retained 82.8 kWh/car service battery remains service-only"):
        raise ValueError("Mechanical and supply definitions do not mate")
    if (service_input["design"]["speed_cap_m_s"] != 20
            or service_input["design"]["acceleration_command_m_s2"] != .4
            or service_input["design"]["headway_s"] != 120
            or service_input["powered_wheel_added_mass_sensitivity_kg_per_car"] != 2400
            or electrical_input["added_traction_equipment_mass_sensitivity_kg_per_car_hypothesis"][-1] != 2400):
        raise ValueError("Service or equipment-mass envelope differs")
    return v, e, s, selected, supply, electrical_input, service_input


def nominal_boxes(vehicle_definition: dict, candidate_id: str) -> list[dict]:
    """Equivalent bounding boxes for interface review, never equipment solids."""
    rows = []
    bogie = vehicle_definition["bogie_module"]
    brake = vehicle_definition["track_brake_module"]
    collector = vehicle_definition["roof_collector"]
    for car in range(vehicle_definition["cars"]):
        x0 = car * vehicle_definition["body_length_m"]
        for axle, centre in enumerate(bogie["motor_box_centres_car_m"]):
            rows.append(dict(id=f"car-{car+1}/motor-envelope-{axle+1}",
                             kind="motor-envelope", candidate_id=candidate_id,
                             centre_m=[centre[0] + x0, centre[1], centre[2]],
                             size_m=bogie["motor_box_size_m"]))
        for bogie_index, centre in enumerate(brake["centres_car_m"]):
            for rail_index, y in enumerate(brake["shoe_centres_y_m"]):
                rows.append(dict(id=f"car-{car+1}/bogie-{bogie_index+1}/shoe-envelope-{rail_index+1}",
                                 kind="rail-brake-shoe-envelope", candidate_id=candidate_id,
                                 centre_m=[centre[0] + x0, y, centre[2]],
                                 size_m=brake["shoe_reference_size_m"]))
        rows.append(dict(id=f"car-{car+1}/collector-stowed-envelope",
                         kind="collector-stowed-envelope", candidate_id=candidate_id,
                         centre_m=[x0 + collector["base_centre_car_m"][0],
                                   collector["base_centre_car_m"][1],
                                   collector["base_centre_car_m"][2] + collector["stowed_box_size_m"][2] / 2],
                         size_m=collector["stowed_box_size_m"]))
    if len(rows) != 54 or len({r["id"] for r in rows}) != 54:
        raise ValueError("Six-car interface occurrence count differs")
    for row in rows:
        row["digital_occurrence_id"] = identity(dict(candidate_id=candidate_id,
                                                      part_id=row["id"],
                                                      scope="nominal-ifc-interface"))
        row["physical_serial_id"] = None
    return rows


def _write_ifc(path: Path, rows: list[dict], candidate_id: str, design_revision_id: str) -> str:
    import ifcopenshell
    import ifcopenshell.api

    api = ifcopenshell.api.run
    file = api("project.create_file", version="IFC4")
    project = api("root.create_entity", file, ifc_class="IfcProject", name="OSR v0.7 nominal prototype interfaces")
    api("unit.assign_unit", file, units=[api("unit.add_si_unit", file, unit_type="LENGTHUNIT")])
    model = api("context.add_context", file, context_type="Model")
    body = api("context.add_context", file, context_type="Model", context_identifier="Body",
               target_view="MODEL_VIEW", parent=model)
    site = api("root.create_entity", file, ifc_class="IfcSite", name="Unsurveyed research corridor")
    api("aggregate.assign_object", file, products=[site], relating_object=project)
    for row in rows:
        obj = api("root.create_entity", file, ifc_class="IfcBuildingElementProxy", name=row["id"])
        api("spatial.assign_container", file, products=[obj], relating_structure=site)
        cx, cy, cz = row["centre_m"]
        sx, sy, sz = row["size_m"]
        x, y, z = cx - sx / 2, cy - sy / 2, cz - sz / 2
        vertices = [(x + dx * sx, y + dy * sy, z + dz * sz)
                    for dz in (0, 1) for dy in (0, 1) for dx in (0, 1)]
        faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
                 (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
        representation = api("geometry.add_mesh_representation", file, context=body,
                             vertices=[vertices], faces=[faces], unit_scale=1.)
        api("geometry.assign_representation", file, product=obj, representation=representation)
        pset = api("pset.add_pset", file, product=obj, name="OSR_Prototype_Identity")
        api("pset.edit_pset", file, pset=pset, properties={
            "candidate_id": candidate_id, "component_kind": row["kind"],
            "engineering_design_revision_id": design_revision_id,
            "digital_occurrence_id": row["digital_occurrence_id"],
            "nominal_interface_envelope": True, "physical_accepted": False,
            "installed_mass_from_geometry": False,
        })
    for entity in file.by_type("IfcRoot"):
        key = candidate_id + entity.is_a() + str(entity.id())
        entity.GlobalId = ifcopenshell.guid.compress(sha256(key.encode()).hexdigest()[:32])
    for relation in file.by_type("IfcRelContainedInSpatialStructure"):
        relation.RelatedElements = sorted(relation.RelatedElements, key=lambda entity: entity.GlobalId)
    file.header.file_name.name = "nominal-prototype-interface.ifc"
    file.header.file_name.time_stamp = "2026-11-17T00:00:00"
    file.write(str(path))
    return ifcopenshell.version


def _verify_ifc(path: Path, rows: list[dict], candidate_id: str, design_revision_id: str) -> None:
    import ifcopenshell
    import ifcopenshell.geom
    from ifcopenshell.util.element import get_pset
    from ifcopenshell.util.shape import get_volume

    file = ifcopenshell.open(str(path))
    by_name = {row["id"]: row for row in rows}
    elements = file.by_type("IfcBuildingElementProxy")
    if len(elements) != len(rows) or len({obj.Name for obj in elements}) != len(rows):
        raise ValueError("Native IFC occurrence count differs")
    for obj in elements:
        row = by_name.get(obj.Name)
        props = get_pset(obj, "OSR_Prototype_Identity")
        if (row is None or props.get("candidate_id") != candidate_id
                or props.get("engineering_design_revision_id") != design_revision_id
                or props.get("digital_occurrence_id") != row["digital_occurrence_id"]
                or props.get("component_kind") != row["kind"]):
            raise ValueError("Native IFC mixed candidate or part identity")
        if props.get("nominal_interface_envelope") is not True or props.get("physical_accepted") is not False:
            raise ValueError("Native IFC research scope differs")
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), obj)
        expected = row["size_m"][0] * row["size_m"][1] * row["size_m"][2]
        if abs(get_volume(shape.geometry) - expected) > 1e-6:
            raise ValueError("Native IFC envelope volume differs")


def build(root=ROOT, *, ifc_path: Path):
    root = Path(root)
    v, e, s, selected, supply, electrical_input, service_input = _load(root)
    definition = dict(schema="osr-v07-powered-prototype-physical-definition/1",
                      parent_selected_candidate_id=selected["candidate_id"],
                      mechanical_vehicle_component_id=v["physical_candidate_id"],
                      electrical_supply_component_id=supply["research_physical_candidate_id"],
                      mechanical_definition=v["physical_definition"],
                      electrical_definition=supply["definition"],
                      inherited_rail_support_component_id=selected["support_component_id"],
                      overhead_mounts_and_site_alignment_defined=False)
    candidate_id = identity(definition)
    design_revision_id = identity(dict(schema="osr-v07-prototype-design-revision/1",
        candidate_id=candidate_id, mechanical_evaluation_id=v["evaluation_id"],
        electrical_evaluation_id=e["evaluation_id"], service_evaluation_id=s["evaluation_id"],
        purpose="nominal-interface-and-quotation-revision"))
    rows = nominal_boxes(v["physical_definition"], candidate_id)
    ifc_version = _write_ifc(ifc_path, rows, candidate_id, design_revision_id)
    _verify_ifc(ifc_path, rows, candidate_id, design_revision_id)
    net_low, net_high = [m - v["mass_budget"]["counted_removed_secondary_kg_per_car"]
                         for m in v["mass_budget"]["provisional_equipment_allocation_kg_per_car"]]
    high_sensitivity = service_input["powered_wheel_added_mass_sensitivity_kg_per_car"]
    if not net_low <= high_sensitivity or high_sensitivity < net_high or high_sensitivity - net_high > 10:
        raise ValueError("Service mass sensitivity does not cover mechanical quote allocation")
    mass = selected["mass"]
    normal = mass["accounted_cap_loaded_kg_per_car"] + high_sensitivity
    crowd = mass["accounted_160_control_kg_per_car"] + high_sensitivity
    if normal <= mass["accounted_cap_loaded_kg_per_car"] or crowd <= mass["accounted_160_control_kg_per_car"]:
        raise ValueError("Powered equipment was not propagated to load controls")
    high_rows = [r for r in s["powered_wheel_mass_sensitivity"]["rows"]
                 if r["direction"] == "uphill" and r["grade_magnitude"] == .02]
    if len(high_rows) != 1 or not high_rows[0]["analytical_target_reached"]:
        raise ValueError("Unique high-mass 2% uphill demand required")
    high = high_rows[0]
    train_mass = normal * 6
    mechanical_rating_kw = high["peak_required_mechanical_power_MW"] * 1000 * (1 + electrical_input["motor_peak_rating_margin_fraction_hypothesis"])
    electrical_rating_kw = mechanical_rating_kw / electrical_input["drive_motoring_efficiency_hypothesis"] + electrical_input["auxiliary_draw_kW_train_hypothesis"]
    brake_force = train_mass * (.6 + .02 * G)
    active_brakes = 11  # One of twelve bogie modules unavailable.
    source_map = {name: digest(root / name) for name in SOURCES}
    evaluation = dict(schema="osr-v07-powered-prototype-research-evaluation/1",
        physical_candidate_id=candidate_id,
        engineering_design_revision_id=design_revision_id,
        mechanical_component_evaluation_id=v["evaluation_id"],
        electrical_component_evaluation_id=e["evaluation_id"],
        equal_service_evaluation_id=s["evaluation_id"],
        source_sha256=source_map,
        numerical_validity="completed-bounded-arithmetic",
        engineering_screen="held-on-unverified-drive-brake-and-installed-integration",
        evidence_maturity="source-bound-analytical-and-nominal-native-interface",
        mass_account=dict(
            conditional_net_equipment_kg_per_car=[net_low, net_high],
            conservative_analytical_addition_kg_per_car=high_sensitivity,
            normal_accounted_upper_kg_per_car=normal,
            crowd_160_accounted_upper_kg_per_car=crowd,
            installed_tare_kg_per_car=None, installed_normal_kg_per_car=None,
            installed_CG_m=None, installed_axle_reactions_N=None),
        service_demand=dict(
            route_scope="Synthetic 30 km/12 stations, 2.727 km spacing, 2% whole-leg sensitivity",
            normal_places_per_train=276,
            peak_required_force_kN=high["peak_required_force_kN"],
            peak_required_mechanical_power_MW=high["peak_required_mechanical_power_MW"],
            mechanical_motoring_kWh_train=high["mechanical_traction_kwh"],
            minimum_peak_mechanical_rating_kW_hypothesis=mechanical_rating_kw,
            minimum_train_DC_input_kW_hypothesis=electrical_rating_kw,
            minimum_six_group_1C4M_each_kW_hypothesis=electrical_rating_kw / 6,
            ideal_line_current_A_at_1500V_hypothesis=electrical_rating_kw * 1000 / 1500,
            actual_available_drive_output_kW=None,
            traction_mu_required_24_axles_optimistic=high["peak_required_force_kN"] * 1000 / (train_mass * G),
            actual_wet_rail_mu=None, rated_hot_120s_duty=None),
        independent_brake=dict(
            high_normal_2pct_downgrade_train_force_N_with_wheel_brakes_unavailable=brake_force,
            required_per_active_module_N_one_of_twelve_unavailable=brake_force / active_brakes,
            peak_heat_W_per_active_module_at_20_m_s=brake_force / active_brakes * 20,
            brake_coil_power_W=None, protected_OLE_loss_brake_energy_J=None,
            actuator_drop_stow_behavior=None, independent_parking_force_N=None,
            measured_longitudinal_rail_brake_force_N=None),
        civil_load_handoff=dict(
            inherited_rail_support_geometry_id=selected["support_component_id"],
            normal_static_mean_N_per_axle_if_equal_load=normal * G / 4,
            crowd_160_static_mean_N_per_axle_if_equal_load=crowd * G / 4,
            design_max_axle_reaction_N=None, dynamic_amplification=None,
            candidate_beam_id=None, span_length_m=None, span_count=None,
            foundation_count=None, rail_length_m=None,
            overhead_support_load_N=None, civil_geometry_and_cost_recalculated=False),
        capital_14_scopes=[dict(scope=r["scope"], candidate_installed_USD=None,
                                base_other_candidate_proxy_USD=r["line30_base_proxy_usd"])
                           for r in s["capital_14_scope_bridge"]],
        candidate_installed_capital_USD=None, candidate_30_year_NPV_USD=None,
        engineering_BOM=dict(candidate_id=candidate_id,
            design_revision_id=design_revision_id,
            quote_rows=[dict(item=r["id"], count_per_car=r["count_per_car"],
                             count_six_car_train=r["count_per_car"] * 6,
                             mass_each_budget_kg=r["mass_each_budget_kg"],
                             make_buy=r["make_buy"], quoted_unit_price_usd=None,
                             actual_supplier=None, physical_serial_id=None)
                        for r in v["mass_budget"]["rows"]],
            whole_train_installed_mass_complete=False),
        manufacturing_BOM=dict(candidate_id=candidate_id,
            design_revision_id=design_revision_id,
            counted_quote_interfaces_per_car=v["provisional_quote_interface_counts_per_car"],
            gearbox_motor_axle_bearing_count=None, qualified_fastener_class=None,
            approved_routing_hours=None, physical_lot_ids=None, complete=False),
        assembly_route=dict(candidate_id=candidate_id,
            design_revision_id=design_revision_id,
            proposed_sequence=v["assembly_and_repair"]["sequence"],
            QA_holds=v["assembly_and_repair"]["qa_hold_points"],
            removal=v["assembly_and_repair"]["removal"],
            approved_lifting_points=None, measured_hours=None,
            work_order_id=None, released=False),
        procurement_draft=dict(candidate_id=candidate_id,
            design_revision_id=design_revision_id,
            electrical_quote_items=e["hardware_quote_items"],
            all_supplier_quotations_received=False,
            installed_price_USD=None, approved_purchase_order_id=None),
        construction_draft=dict(candidate_id=candidate_id,
            design_revision_id=design_revision_id,
            inherited_support_geometry_id=selected["support_component_id"],
            candidate_beam_id=None, span_length_m=None, span_count=None,
            overhead_mount_geometry=None, site_ground_capacity_kPa=None,
            rail_and_bearing_design_load_N=None,
            erection_method_approved=False, installed_cost_USD=None),
        native_ifc=dict(path="nominal-prototype-interface.ifc", sha256=digest(ifc_path),
                        ifcopenshell_version=ifc_version, part_count=len(rows),
                        real_native_IFC_reopened=True, equivalent_interface_boxes_only=True,
                        complete_vehicle_IFC=False, complete_civil_IFC=False),
        native_CAD_STEP=None,
        physical_definition_complete=False, complete_installed_BOM=False,
        physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False,
        selected_reference_changed=False,
        required_next_inputs=[
            "Approved motor/gear/axle, inverter, brake and collector drawings with actual dimensions, mass and CG",
            "Measured wet-rail force/current/thermal duty, one-brake-module-out hot stop and protected OLE-loss energy",
            "Brake coil power, fail-safe actuator drop/stow, independent parking and tow; no service-battery credit",
            "Surveyed alignment, overhead and rail clearances, support and ground conditions",
            "Complete vehicle and civil load recalculation plus fourteen matched installed and renewal quotations",
        ])
    evaluation["evaluation_id"] = identity(evaluation)
    selection = dict(schema="osr-v07-prototype-next-evaluator-selection/1",
        purpose="next full-scale prototype quotation and measurement",
        candidate_id=candidate_id, evaluation_id=evaluation["evaluation_id"],
        status="provisional-next-experiment", selected_installed_reference=False,
        parent_v06_selection_id=selected["selection_id"],
        physical_accepted=False, manufacturing_release=False, operating_release=False)
    selection["selection_id"] = identity(selection)
    result = dict(schema="osr-v07-prototype-bundle-package/1",
                  candidate=dict(physical_definition=definition, candidate_id=candidate_id),
                  evaluation=evaluation, selection=selection,
                  nominal_ifc_parts=rows)
    result["package_id"] = identity(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("write", "check"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.output
    if args.action == "write" and out.exists():
        raise ValueError("Fresh output directory required")
    if args.action == "check" and not out.is_dir():
        raise ValueError("Published output directory missing")
    if args.action == "write":
        out.mkdir(parents=True)
        result = build(ifc_path=out / "nominal-prototype-interface.ifc")
        (out / "result.json").write_bytes(encoded(result))
    else:
        with TemporaryDirectory(prefix="osr-v07-prototype-check-") as directory:
            fresh = Path(directory)
            result = build(ifc_path=fresh / "nominal-prototype-interface.ifc")
            if (out / "result.json").read_bytes() != encoded(result):
                raise ValueError("Prototype research bundle differs from current sources")
            if (out / "nominal-prototype-interface.ifc").read_bytes() != (fresh / "nominal-prototype-interface.ifc").read_bytes():
                raise ValueError("Native IFC differs from current candidate and tool")
        _verify_ifc(out / "nominal-prototype-interface.ifc", result["nominal_ifc_parts"],
                    result["candidate"]["candidate_id"],
                    result["evaluation"]["engineering_design_revision_id"])
    print(json.dumps(dict(verified=True, candidate_id=result["candidate"]["candidate_id"],
                          evaluation_id=result["evaluation"]["evaluation_id"],
                          selection_id=result["selection"]["selection_id"],
                          native_ifc_parts=len(result["nominal_ifc_parts"]),
                          physical_accepted=False), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
