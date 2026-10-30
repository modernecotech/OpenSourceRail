"""Build unsent, candidate-bound station-LIM bank RFQ scope drafts.

The package combines each located primary-material bank with hierarchy-only
links to that bank's missing converter, protection, cooling, support and access
scope. Context links never become package membership or priced quantity.
"""
from hashlib import sha256
import gzip
import json
from math import isfinite
from pathlib import Path
import tomllib

from engineering.station_rail import ROOT as REPOSITORY_ROOT
from .catalogue import load_catalogue
from .model import encoded, identity


PROCUREMENT = Path(
    "docs/design-engine/sourcing/procurement-bom/"
    "federated-v06-research-packages-v24.json.gz")
INPUT = Path(
    "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13/"
    "input.json.gz")
SOURCE_SEED = Path("engineering/sourcing/data/iraq-domestic-material-leads-2026-10.json")
FABRICATION_SEED = Path("engineering/sourcing/data/iraq-domestic-fabrication-discovery-2026-10.json")
BASELINE = Path("engineering/development-baseline.toml")
MOTION_ADAPTER = Path("engineering/design_search/system_motion.py")
COUPLED_SPEC = Path("campaigns/coupled-railway-design.toml")
ARCHITECTURE_SPEC = Path("campaigns/whole-railway-architecture-search.toml")
CLOSURE_SPEC = Path("campaigns/end-to-end-railway-closure.toml")
OUTPUT_DIR = Path("docs/design-engine/sourcing/rfq-drafts/station-drive-banks-2026-10")
OUTPUT_FILE = "station-drive-rfq-scope.json"

ADDITIONAL_LEAD_ROLES = {
    "supplier.abb-acs880-single-html": "industrial drive-family technical comparator; no station-LIM compatibility or price",
    "digikey-v4-schema": "distributor API/schema source for selected standard electronics only; not a traction converter offer",
    "iraq.diwan-electrical-industries": "local cables/transformers capability lead; no candidate product or quote",
    "iraq.rs-alnajaf-electrical-factory": "local cabinet/substation/panel capability lead; no candidate product or quote",
    "iraq.ibn-majid-heavy-engineering": "local heavy fabrication capability lead; no magnetic-steel or bank assembly match",
    "iraq.ms-cable-busbar": "local bare-copper conductor lead; no winding-stock specification, insulation system or LIM match",
}


def _read(path, *, compressed=False):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if compressed else raw)


def _hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _source_records(root):
    root = Path(root)
    records = list(load_catalogue())
    records.extend(load_catalogue([root / SOURCE_SEED, root / FABRICATION_SEED]))
    sources = {row["source_key"]: row for row in records if row["kind"] == "source"}
    return sources


def _lead(row, source_records, role):
    key = row["source_key"]
    source = source_records.get(key)
    if source is None:
        raise ValueError("RFQ source lead is absent from the current registry: " + key)
    return {
        "source_key": key,
        "source_record_id": source["record_id"],
        "source_url": source["url"],
        "role": role,
        "discovery_only": True,
        "technical_compatibility": None,
        "supplier_offer": False,
        "price": None,
    }


def _service_matrix(root):
    root = Path(root)
    baseline = tomllib.loads((root / BASELINE).read_text())
    coupled = tomllib.loads((root / COUPLED_SPEC).read_text())
    architecture = tomllib.loads((root / ARCHITECTURE_SPEC).read_text())
    closure = tomllib.loads((root / CLOSURE_SPEC).read_text())
    adverse = closure["adverse_hypothesis"]
    vehicle = baseline["vehicle"]
    service = baseline["service"]
    routes = list(closure["distances_m"])
    loads = [
        {"case": "empty", "passengers_per_car": 0, "basis": "candidate accounted-tare case; complete installed mass remains unresolved"},
        {"case": "normal", "passengers_per_car": vehicle["normal_passengers_per_car"],
         "fixed_seats_per_car": vehicle["fixed_seats_per_car"],
         "wheelchair_places_per_car": vehicle["wheelchair_places_per_car"],
         "basis": "normal seated service comparator"},
        {"case": "crowd-control", "passengers_per_car": architecture["requirements"]["crowd_control_per_car"],
         "basis": "structural/service adverse control; not planned standing capacity"},
        {"case": "adverse-normal", "passengers_per_car": vehicle["normal_passengers_per_car"],
         "grade_up_fraction": adverse["grade_up_fraction"],
         "headwind_m_s": adverse["headwind_m_s"],
         "rail_adhesion": adverse["rail_adhesion"],
         "basis": "declared closure research hypothesis; adhesion applies to wheel/brake interaction and does not create LIM thrust"},
    ]
    return {
        "shared_service_context": {
            "cars": vehicle["cars"],
            "car_length_m": vehicle["body_length_m"],
            "normal_passengers_per_car": vehicle["normal_passengers_per_car"],
            "fixed_seats_per_car": vehicle["fixed_seats_per_car"],
            "wheelchair_places_per_car": vehicle["wheelchair_places_per_car"],
            "speed_cap_m_s": service["launch_speed_cap_m_s"],
            "headway_s": service["headway_s"],
            "dwell_s": service["dwell_s"],
            "acceleration_target_m_s2": service["acceleration_m_s2"],
            "capacity_arithmetic_pphpd": service["normal_capacity_pphpd_arithmetic"],
            "scope": "common-service request inputs; they do not replace this research candidate's exact mass, interfaces or physical definition",
        },
        "route_distance_m": routes,
        "load_cases": loads,
        "scenario_count": len(routes) * len(loads),
        "repeated_duty": {
            "target_headway_s": service["headway_s"],
            "requirement": "Supplier shall state available force and losses across the start, powered window, handoff, coast and receiving/braking phases at repeated headway; include recovery only as a separate non-safety-credit option.",
        },
        "campaign_revisions": {
            "coupled_railway": coupled["revision"],
            "whole_railway_architecture": architecture["revision"],
            "end_to_end_closure": closure["revision"],
        },
    }


def _existing_copper_sensitivities(bom, material_lines):
    """Carry the candidate-level material + labour + 20% screen forward.

    The screen applies to the entire five-bank copper stock line. It cannot be
    allocated to individual bank RFQs because commercial bank quantities and
    measured bank-specific labour routes are not available.
    """
    lines = [row for row in material_lines if row.get("material") == "copper-conductor"]
    if len(lines) != 1:
        raise ValueError("Exactly one candidate-level LIM copper demand line is required")
    line = lines[0]
    scenarios = line.get("copper_imported_raw_stock_sensitivity_scenarios", [])
    by_hours = {str(row.get("labour_hours_per_gross_stock_tonne")): row for row in scenarios}
    if set(by_hours) != {"8", "16", "32"} or len(scenarios) != 3:
        raise ValueError("The current copper estimate must retain its 8/16/32 hour cases")
    result = []
    for hours in ("8", "16", "32"):
        row = by_hours[hours]
        if (row.get("candidate_id") != bom["candidate_id"]
                or row.get("source_input_id") != bom["source_input_id"]
                or row.get("supplier_quote") is not False
                or row.get("compatible_product_match") is not False
                or row.get("uplift_fraction") != "0.20"
                or row.get("commercial_order_quantity") is not None
                or row.get("complete_process_cost") is not None
                or row.get("complete_installed_cost") is not None
                or row.get("unknown_is_zero") is not False):
            raise ValueError("Copper estimate lost its candidate or incomplete-cost boundary")
        result.append({
            "material_line_id": line["material_line_id"],
            "material": line["material"],
            "scope": "whole five-bank candidate primary copper stock; not allocated to a bank",
            "hours_per_gross_stock_tonne": int(hours),
            "gross_stock_mass_kg": row["gross_stock_mass_kg"],
            "currency": "IQD",
            "direct_material_cost": row["direct_material_cost_iqd"],
            "direct_labour_cost": row["direct_labour_cost_iqd"],
            "uplift_fraction": row["uplift_fraction"],
            "uplift_amount": row["uplift_amount_iqd"],
            "estimated_total": row["estimated_total_iqd"],
            "material_benchmark_id": row["material_benchmark_id"],
            "wage_benchmark_id": row["wage_benchmark_id"],
            "estimate_basis": row["estimate_basis"],
            "supplier_quote": False,
            "compatible_product_match": False,
            "commercial_order_quantity": None,
            "complete_process_cost": None,
            "complete_installed_cost": None,
            "engineering_accepted": False,
            "procurement_approved": False,
            "physical_accepted": False,
            "unknown_is_zero": False,
        })
    return result


def build_packet(root=REPOSITORY_ROOT):
    root = Path(root).resolve()
    bom_path = root / PROCUREMENT
    bom = _read(bom_path, compressed=True)
    source_input = _read(root / INPUT, compressed=True)
    if (bom.get("schema") != "osr-procurement-package-bom/1"
            or bom.get("packet_id") != identity({key: val for key, val in bom.items() if key != "packet_id"})
            or bom.get("candidate_id") != source_input.get("payload", {}).get("candidate_id")
            or bom.get("evaluation_id") != source_input.get("payload", {}).get("evaluation_id")
            or bom.get("source_input_id") != source_input.get("payload_id")
            or bom.get("selected_reference_changed") is not False
            or bom.get("commercial_order_quantities_known") is not False
            or bom.get("unknown_is_zero") is not False):
        raise ValueError("RFQ draft requires the exact current non-promoting research procurement packet")

    banks = [row for row in bom.get("packages", [])
             if row.get("package_family") == "wayside-lim-primary-material-set"]
    bank_by_key = {row.get("package_key"): row for row in banks}
    expected_keys = {f"bank/{index}" for index in range(5)}
    if len(banks) != 5 or set(bank_by_key) != expected_keys:
        raise ValueError("Current station-LIM procurement input must contain exactly five identified bank sets")

    material_lines = [row for row in bom.get("material_purchasing_lines", [])
                       if row.get("system") == "wayside/primary"]
    if len(material_lines) != 2:
        raise ValueError("Current candidate must retain the separate copper and magnetic-steel primary lines")
    if len({line.get("material_line_id") for line in material_lines}) != 2 or any(
            not isinstance(line.get("material_line_id"), str)
            or len(line["material_line_id"]) != 64 for line in material_lines):
        raise ValueError("Station primary material lines must retain distinct source identities")
    copper_sensitivities = _existing_copper_sensitivities(bom, material_lines)

    obligations = set(bom.get("unlocated_obligation_ids", []))
    hierarchy = bom.get("unlocated_obligation_links", {})
    links = hierarchy.get("links", [])
    leads = _source_records(root)
    all_link_ids = set()
    scopes = []
    for index in range(5):
        key = f"bank/{index}"
        bank = bank_by_key[key]
        bank_package_id = bank["package_id"]
        occurrences = list(bank.get("engineering_occurrence_ids", []))
        try:
            bank_mass = float(bank.get("modeled_gross_stock_mass_kg"))
        except (TypeError, ValueError):
            raise ValueError("Every station bank must have an explicit located primary-stock mass") from None
        if (bank_package_id != identity({k: v for k, v in bank.items() if k != "package_id"})
                or bank.get("candidate_id") != bom["candidate_id"]
                or len(occurrences) != 486
                or any(not occurrence.startswith(key + "/station-lim/primary/") for occurrence in occurrences)
                or not isfinite(bank_mass) or bank_mass <= 0
                or bank.get("assembly_complete") is not False
                or bank.get("commercial_order_quantity") is not None
                or bank.get("complete_procurement_cost") is not None
                or bank.get("complete_installed_cost") is not None):
            raise ValueError("Station bank stock/package scope is incomplete or changed")
        related_lines = [line for line in material_lines
                         if bank_package_id in line.get("related_package_ids", [])]
        if len(related_lines) != 2:
            raise ValueError("Each station bank must trace to both primary material demand lines")
        related_line_ids = {line["material_line_id"] for line in related_lines}
        bank_links = [row for row in links
                      if row.get("scope_key", "").startswith(key + "/")
                      and bank_package_id in row.get("related_package_ids", [])]
        if len(bank_links) != 4:
            raise ValueError("Each station bank must expose four separate open completion accounts")
        open_accounts = []
        for link in sorted(bank_links, key=lambda row: row["scope_key"]):
            ids = link.get("unlocated_obligation_ids", [])
            if (link.get("allocated_to_package_mass_or_quantity") is not False
                    or link.get("association_is_package_membership") is not False
                    or link.get("priced") is not False
                    or link.get("quantity") is not None
                    or not ids or not set(ids) <= obligations):
                raise ValueError("Completion account must remain an unpriced, non-additive context link")
            all_link_ids.add(link["link_id"])
            open_accounts.append({
                "scope_key": link["scope_key"],
                "unlocated_obligation_ids": ids,
                "hierarchy_link_id": link["link_id"],
                "relationship": link["relationship"],
                "quantity": None,
                "allocated_to_bank_mass_or_quantity": False,
                "package_membership": False,
                "price": None,
            })
        bank_leads = []
        seen = set()
        for line in related_lines:
            for row in line.get("domestic_fabrication_lead_sources", []):
                if row["source_key"] not in seen:
                    bank_leads.append(_lead(row, leads,
                        "local material/fabrication discovery lead for " + line["material"]))
                    seen.add(row["source_key"])
        package = {
            "scope_key": key,
            "bank_package_id": bank_package_id,
            "candidate_id": bom["candidate_id"],
            "evaluation_id": bom["evaluation_id"],
            "engineering_group_ids": bank.get("manufacturing_group_ids", []),
            "engineering_occurrence_ids": occurrences,
            "engineering_occurrence_count": len(occurrences),
            "source_material_line_ids": sorted(related_line_ids),
            "source_materials": [{
                "material_line_id": line["material_line_id"],
                "material": line["material"],
                "stock_scope": line["stock_scope"],
                "bank_related_occurrence_ids": [occ for occ in line.get("engineering_occurrence_ids", [])
                                                  if occ.startswith(key + "/station-lim/primary/")],
                "modeled_gross_stock_mass_kg_for_network_line": line.get("modeled_gross_stock_mass_kg"),
                "bank_specific_price": None,
                "purchase_quantity": None,
                "supplier_product_match": False,
            } for line in sorted(related_lines, key=lambda row: row["material"])],
            "located_primary_stock_mass_kg": bank_mass,
            "mass_scope": "located gross primary stock only; not complete bank/drive installed mass",
            "open_completion_accounts": open_accounts,
            "domestic_discovery_leads": bank_leads,
            "commercial_order_quantity": None,
            "supplier_quotation": None,
            "complete_primary_assembly_cost": None,
            "complete_drive_installed_cost": None,
            "rfq_sent": False,
            "engineering_accepted": False,
            "procurement_approved": False,
            "physical_accepted": False,
        }
        package["rfq_scope_id"] = identity(package)
        scopes.append(package)

    if len(all_link_ids) != 20 or len({occ for row in scopes for occ in row["engineering_occurrence_ids"]}) != 2430:
        raise ValueError("Five bank scopes must preserve each located primary occurrence and all open account links")

    extra_leads = []
    for key, role in ADDITIONAL_LEAD_ROLES.items():
        source = leads.get(key)
        if source is None:
            raise ValueError("Expected technical or local electrical lead absent: " + key)
        extra_leads.append({
            "source_key": key,
            "source_record_id": source["record_id"],
            "source_url": source["url"],
            "role": role,
            "discovery_only": True,
            "technical_compatibility": None,
            "supplier_offer": False,
            "price": None,
        })

    from engineering.design_search.system_motion import AXES, FIELDS
    service_matrix = _service_matrix(root)
    electrical_maps = {
        "required_schema_for_future_map": "osr-station-available-force-map/1",
        "current_adapter_path": MOTION_ADAPTER.as_posix(),
        "required_axes_consumed_by_current_adapter": list(AXES),
        "required_sample_fields_consumed_by_current_adapter": list(FIELDS),
        "required_axes_to_add_before_air_gap_sensitivity_can_be_admitted": ["air_gap_m"],
        "required_outputs_to_record_outside_current_map_schema": ["electrical_frequency_hz", "phase_sequence_and_connection"],
        "supplier_to_return": [
            "Available thrust versus position, speed, current and temperature, with exact bank and train branch identities",
            "Measured or independently validated air-gap sensitivity at declared minimum/nominal/maximum gaps",
            "Terminal voltage, frequency, current waveform and phase/branch allocation at every operating point",
            "Copper, core, converter, feeder and cooling losses with heat paths and temperatures",
            "Vertical/normal force and wheel-load interaction, including installation tolerances and secondary offsets",
            "Entry/exit, bank handoff, overlap, zero-force outside powered windows, and current slew/control limits",
            "Repeated 120-second headway thermal/electrical duty with start temperature, recovery interval and degradation limits",
            "Proposed material grades, conductor insulation/thermal class, joints, support loads, fasteners and maintenance access",
            "Independent benchmark, mesh/time convergence, finite-height/return-current method and raw test/model evidence",
        ],
        "admission_boundary": "Supplier response, catalogue data or a converged numerical map is not admitted by this RFQ packet. It must match this exact candidate/component, include approved limits and independent evidence, pass the current map gate, and close the additional air-gap/frequency adapter gaps before it can support a physical journey.",
    }
    local_scope = {
        "local_assembly_or_fabrication_variants_to_quote_separately": [
            "Imported complete bank assembly, delivered to a named destination",
            "Imported core/converter modules with local supports, wiring and assembly",
            "Locally fabricated primary steel/supports with imported qualified winding/converter modules",
        ],
        "must_separate": ["imported content", "local material", "local fabrication labour", "tooling", "QA/testing", "transport", "installation/commissioning", "spares/renewals"],
        "no_local_content_or_price_claim": True,
    }
    source_paths = [
        "engineering/sourcing/station_drive_rfq.py",
        "engineering/sourcing/cli.py",
        "engineering/sourcing/model.py",
        "engineering/sourcing/catalogue.py",
        "engineering/design_search/system_motion.py",
        PROCUREMENT.as_posix(), INPUT.as_posix(), SOURCE_SEED.as_posix(), FABRICATION_SEED.as_posix(),
        BASELINE.as_posix(), COUPLED_SPEC.as_posix(), ARCHITECTURE_SPEC.as_posix(), CLOSURE_SPEC.as_posix(),
        "engineering/sourcing/data/supplier-catalogue.json",
        "engineering/sourcing/data/public-feeds.json",
        "engineering/sourcing/data/iraq-domestic-2026-july.json",
    ]
    payload = {
        "schema": "osr-station-drive-banked-rfq-scope/1",
        "candidate_id": bom["candidate_id"],
        "evaluation_id": bom["evaluation_id"],
        "selection_id": None,
        "source_input_id": bom["source_input_id"],
        "procurement_bom_packet_id": bom["packet_id"],
        "source_registry_record_set_id": bom.get("source_registry_record_set_id"),
        "purpose": "Unsent supplier-ready technical/commercial scope drafts for five candidate bank groups; not an order or selected propulsion design.",
        "bank_scope_count": len(scopes),
        "bank_scopes": scopes,
        "total_located_primary_occurrence_count": 2430,
        "total_located_primary_gross_stock_mass_kg": sum(
            row["located_primary_stock_mass_kg"] for row in scopes),
        "non_additive_open_account_link_count": len(all_link_ids),
        "service_test_matrix": service_matrix,
        "available_force_map_response_contract": electrical_maps,
        "local_fabrication_variants": local_scope,
        "existing_candidate_level_copper_material_labour_sensitivities": copper_sensitivities,
        "additional_electrical_and_local_fabrication_leads": extra_leads,
        "supplier_offers": 0,
        "supplier_quotes_received": 0,
        "supplier_communications_sent": 0,
        "commercial_order_quantities_known": False,
        "complete_primary_assembly_cost": None,
        "complete_drive_installed_cost": None,
        "whole_life_cost": None,
        "selected_reference_changed": False,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
        "unknown_is_zero": False,
        "source_sha256": {name: _hash(root / name) for name in source_paths},
    }
    payload["packet_id"] = identity(payload)
    return payload


def render_readme(packet):
    service = packet["service_test_matrix"]
    crowd = next(row for row in service["load_cases"] if row["case"] == "crowd-control")
    adverse = next(row for row in service["load_cases"] if row["case"] == "adverse-normal")
    route_labels = ", ".join("{:g} km".format(distance / 1000)
                              for distance in service["route_distance_m"])
    copper = packet["existing_candidate_level_copper_material_labour_sensitivities"]
    copper_costs = "; ".join(
        "{hours} h/t: IQD {total:,.2f}".format(
            hours=row["hours_per_gross_stock_tonne"], total=float(row["estimated_total"]))
        for row in copper)
    lines = [
        "# Station-LIM bank RFQ scope drafts — October 2026",
        "",
        f"This unsent package contains five research-candidate bank scopes for candidate `{packet['candidate_id']}` and evaluation `{packet['evaluation_id']}`. It retains {packet['total_located_primary_occurrence_count']:,} exact located primary-material occurrences and links {packet['non_additive_open_account_link_count']} unresolved completion accounts without turning them into priced package members.",
        "",
        "## Bank scopes",
        "",
        "| Bank | Scope ID | Located occurrences | Primary gross stock (kg) | Source material lines | Open completion accounts | Order qty | Complete bank price |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in packet["bank_scopes"]:
        lines.append("| {bank} | `{scope}` | {occ} | {mass:.3f} | {materials} | {open} | unknown | unknown |".format(
            bank=row["scope_key"], scope=row["rfq_scope_id"], occ=row["engineering_occurrence_count"],
            mass=float(row["located_primary_stock_mass_kg"]),
            materials=", ".join(line["material"] for line in row["source_materials"]),
            open=len(row["open_completion_accounts"])))
    lines += [
        "",
        "Each bank scope requests a separate unit response and an optional five-bank total. Internal bank grouping is not a commercial order quantity. The included mass is located gross copper/steel primary stock only; windings, converter, feeders, supports, cooling, controls, protection, access, installation and maintenance do not become zero because they are not present in the stock subtotal.",
        "",
        "## Existing domestic fabrication estimate",
        "",
        "The candidate-level copper line already carries an indicative raw-material + assumed labour + 20% uplift screen for all five banks: " + copper_costs + ". Material uses the 2025 Iraqi HS 74081100 national CIF import unit value and labour uses the September 2026 Baghdad skilled-worker base-wage proxy. These are not per-bank allocations, winding-grade prices, supplier quotations or complete drive costs. Insulation, winding/impregnation, tooling, yield, QA, equipment, employer burden, cooling, converter, protection, installation and renewals remain unpriced.",
        "",
        "## Required duty and test response",
        "",
        ("Return separate performance for {count} common-service cases: {routes} routes crossed with empty, normal, crowd-control and adverse-normal loads. The normal comparator uses {normal} people/car ({seats} seats plus {wheelchairs} wheelchair places); the {crowd} people/car case is a control, not planned standing service. The adverse-normal case uses the closure campaign's declared {grade:.1%} grade, {headwind:g} m/s headwind and {adhesion:g} rail-adhesion hypothesis; adhesion remains in the independent wheel/brake model and is not available LIM thrust.".format(
            count=service["scenario_count"], routes=route_labels,
            normal=service["shared_service_context"]["normal_passengers_per_car"],
            seats=service["shared_service_context"]["fixed_seats_per_car"],
            wheelchairs=service["shared_service_context"]["wheelchair_places_per_car"],
            crowd=crowd["passengers_per_car"], grade=adverse["grade_up_fraction"],
            headwind=adverse["headwind_m_s"], adhesion=adverse["rail_adhesion"])),
        "",
        "The response asks for the current software map fields (position, speed, current and temperature axes; thrust, electrical input, loss, voltage and vertical force), plus explicit gap sensitivity and electrical frequency/phase data. The current map adapter does not consume air-gap as an axis or frequency as a field. Those adapter gaps are stated in the packet and must be resolved before a supplier map can support a physical journey.",
        "",
        "## Quote structure and evidence",
        "",
        "Quote imported-complete, imported-modules/local-assembly and local-fabrication/imported-modules alternatives separately. Break out imported and local content, raw material, labour, tooling, QA/testing, delivery, installation/commissioning, spares and renewals. Return dimensions, masses, bill of materials, material grades/certificates, exact operating limits, available-force map evidence, lead time, MOQ, currency, delivery terms, warranty and maintenance requirements. No local-content percentage is assumed.",
        "",
        "The listed Iraqi and international sources are discovery/technical leads, not compatible products, supplier offers or endorsements. No RFQ was sent. The five-bank research candidate is separate from the selected reference's approximately 900 m shared winding allocation; prices, force maps, electrical duties or civil requirements do not transfer between them.",
        "",
        "RFQ drafts remain disabled until an authorized operator selects a supplier, approves the technical package and sends the request. Candidate selection, engineering/procurement approval, physical acceptance, complete installed cost and whole-life cost remain open.",
        "",
        f"Machine-readable bank details, exact IDs, source hashes and response fields are in [{OUTPUT_FILE}]({OUTPUT_FILE}); the sealed source/output hashes are in [manifest.json](manifest.json).",
        "",
    ]
    return "\n".join(lines)


def _write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_bytes(payload)
    temporary.replace(path)


def publish_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    if target.is_symlink():
        raise ValueError("Station-drive RFQ output must not be a symlink")
    if target.exists() and any(target.iterdir()):
        old_path = target / "manifest.json"
        if not old_path.is_file():
            raise ValueError("Existing output is not an owned RFQ-scope publication")
        old = _read(old_path)
        if (old.get("schema") != "osr-station-drive-rfq-publication/1"
                or old.get("publication_id") != identity({k: v for k, v in old.items()
                                                          if k != "publication_id"})):
            raise ValueError("Existing station-drive RFQ publication identity differs")
    packet = build_packet(root)
    readme = render_readme(packet)
    packet_bytes = encoded(packet)
    manifest = {
        "schema": "osr-station-drive-rfq-publication/1",
        "packet_id": packet["packet_id"],
        "source_sha256": packet["source_sha256"],
        "files_sha256": {
            "README.md": sha256(readme.encode("utf-8")).hexdigest(),
            OUTPUT_FILE: sha256(packet_bytes).hexdigest(),
        },
        "rfq_sent": False,
        "supplier_communications_sent": 0,
        "complete_drive_installed_cost": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
        "unknown_is_zero": False,
    }
    manifest["publication_id"] = identity(manifest)
    _write(target / "README.md", readme.encode("utf-8"))
    _write(target / OUTPUT_FILE, packet_bytes)
    _write(target / "manifest.json", encoded(manifest))
    return verify_packet(root=root, output=target)


def verify_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    manifest = _read(target / "manifest.json")
    if (manifest.get("schema") != "osr-station-drive-rfq-publication/1"
            or manifest.get("publication_id") != identity({k: v for k, v in manifest.items()
                                                          if k != "publication_id"})):
        raise ValueError("Station-drive RFQ publication identity differs")
    packet = build_packet(root)
    if (_read(target / OUTPUT_FILE) != packet
            or (target / "README.md").read_text() != render_readme(packet)
            or manifest.get("packet_id") != packet["packet_id"]
            or manifest.get("source_sha256") != packet["source_sha256"]
            or manifest.get("files_sha256") != {
                "README.md": _hash(target / "README.md"),
                OUTPUT_FILE: _hash(target / OUTPUT_FILE)}
            or manifest.get("rfq_sent") is not False
            or manifest.get("supplier_communications_sent") != 0
            or any(manifest.get(key) is not False for key in
                   ("engineering_accepted", "procurement_approved", "physical_accepted"))):
        raise ValueError("Station-drive RFQ draft does not reproduce or has changed release boundary")
    if (packet.get("supplier_communications_sent") != 0
            or packet.get("supplier_quotes_received") != 0
            or packet.get("commercial_order_quantities_known") is not False
            or packet.get("selected_reference_changed") is not False
            or packet.get("complete_drive_installed_cost") is not None):
        raise ValueError("Station-drive RFQ draft cannot send messages, set prices or change selection")
    return {
        "verified": True,
        "publication_id": manifest["publication_id"],
        "packet_id": packet["packet_id"],
        "candidate_id": packet["candidate_id"],
        "bank_scope_count": packet["bank_scope_count"],
        "primary_occurrence_count": packet["total_located_primary_occurrence_count"],
        "open_account_link_count": packet["non_additive_open_account_link_count"],
        "service_scenario_count": packet["service_test_matrix"]["scenario_count"],
        "supplier_communications_sent": 0,
        "complete_drive_installed_cost": None,
        "physical_accepted": False,
    }
