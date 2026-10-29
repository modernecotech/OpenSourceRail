"""Small, source-linked material takeoffs derived from explicit design studies.

These hypotheses exercise the sourcing/digital-twin path without relabelling an
unfinished body registry as a complete, manufacturable vehicle.
"""
from copy import deepcopy

from .manufacturing import laminate_requirements
from .model import identity, is_id, record, validate_record


_RECIPES = (
    ("solid-600gsm", 4, "0.50", {"not_required": True, "reason": "Solid laminate hypothesis"}),
    ("sandwich-600gsm", 2, "0.50", {"thickness_m": "0.02", "density_kg_m3": "85", "product_key": "GURIT-CORECELL-M80"}),
    ("higher-fibre-sandwich-600gsm", 2, "0.60", {"thickness_m": "0.02", "density_kg_m3": "85", "product_key": "GURIT-CORECELL-M80"}),
)


def laminate_study_requirements(store, *, parent_candidate_id, source_input_id,
                                product_observations=None):
    """Return three proposal-bound sourcing inputs and their process records.

    The 10 m² basis is a comparative material hypothesis, not an actual roof
    geometry. The selected foam grade and density range are source-linked;
    fibre fractions, resin uptake and 10% scrap remain explicit assumptions.
    Unknown adhesives, inserts, consumables and labour
    stay unresolved. The parent digital-twin candidate is retained as ancestry;
    each alternative receives its own physical-proposal identity.
    """
    if not is_id(parent_candidate_id):
        raise ValueError("Exact parent physical candidate identity required")
    if not is_id(source_input_id):
        raise ValueError("Exact digital-twin input identity required")
    by_key = {}
    for item in store.all("product"):
        by_key.setdefault(item["product_key"], []).append(item)

    if product_observations is None:
        product_observations = {}
    allowed_product_keys = {"EC-GF-BA-600-127", "EC-EP-IN2-S-1", "GURIT-CORECELL-M80"}
    if (not isinstance(product_observations, dict) or set(product_observations) - allowed_product_keys or
            any(not is_id(value) for value in product_observations.values())):
        raise ValueError("Known product keys and exact immutable product record IDs required")

    def exact_product(product_key):
        matches = by_key.get(product_key, [])
        selected_id = product_observations.get(product_key)
        if selected_id is not None:
            selected = store.get(selected_id, "product")
            if selected["product_key"] != product_key:
                raise ValueError("Selected immutable product observation has a different product key")
            return selected
        if len(matches) != 1:
            raise ValueError("Unique immutable supplier product observation required for " + product_key +
                             "; select an exact product record ID")
        return matches[0]

    cloth = exact_product("EC-GF-BA-600-127")
    resin = exact_product("EC-EP-IN2-S-1")
    foam = exact_product("GURIT-CORECELL-M80")

    common_basis = identity({"functional_comparison": "declared-10m2-laminate-material-screen",
                             "parent_candidate_id": parent_candidate_id,
                             "loads": "unqualified", "fitout": "excluded"})
    output = []
    for name, ply_count, fibre_fraction, core_recipe in _RECIPES:
        core = deepcopy(core_recipe)
        foam_for_recipe = None if core.get("not_required") else foam
        if not core.get("not_required"):
            density = foam["specifications"].get("density_kg_m3", {}).get("value")
            density_range = foam["specifications"].get("density_range_kg_m3", {}).get("values")
            if density is None or density_range is None:
                raise ValueError("Exact nominal and bounded density observations required for the selected core grade")
            core["density_kg_m3"] = density
            core["density_range_kg_m3"] = deepcopy(density_range)
        physical_definition = dict(proposal_type="laminate-material-hypothesis/2",
            parent_candidate_id=parent_candidate_id, area_m2="10",
            ply=dict(areal_weight_g_m2="600", count=ply_count,
                     fabric_width_m="1.27", product_key=cloth["product_key"]),
            fibre_mass_fraction=fibre_fraction, mixed_resin_product_key=resin["product_key"],
            core=(dict(product_key=foam_for_recipe["product_key"], thickness_m=core["thickness_m"])
                  if foam_for_recipe is not None else dict(not_required=True)),
            adhesive="unresolved", inserts="unresolved")
        definition = dict(recipe=name, parent_candidate_id=parent_candidate_id,
                          source_input_id=source_input_id, area_m2="10",
                          ply=dict(areal_weight_g_m2="600", count=ply_count,
                                   fabric_width_m="1.27", product_key=cloth["product_key"]),
                          fibre_mass_fraction=fibre_fraction, scrap_fraction="0.10",
                          mixed_resin_product_key=resin["product_key"], core=deepcopy(core),
                          product_observations={product["product_key"]: product["record_id"] for product in
                              (cloth, resin) + (() if foam_for_recipe is None else (foam_for_recipe,))},
                          adhesive="unresolved", inserts="unresolved", labour="unresolved")
        candidate_id = identity(physical_definition)
        input_id = identity({"study_input": "laminate-material-hypothesis/2",
                             "candidate_id": candidate_id, "definition": definition})
        process = laminate_requirements(
            candidate_id, input_id, "10", [definition["ply"]], fibre_fraction, "0.10",
            source_ids=sorted(set(cloth["source_ids"] + resin["source_ids"] +
                                  ([] if foam_for_recipe is None else foam_for_recipe["source_ids"]))),
            part_id="research-roof-panel-material-screen",
            part_definition_id=identity({"parent": parent_candidate_id, "part": "roof-panel-hypothesis"}),
            cad_revision_id=source_input_id,
            resin_product_key=resin["product_key"], resin_includes_hardener=True,
            core=core, adhesive={}, functional_basis_id=common_basis)
        validate_record(process, "process")

        requirements = []
        for index, row in enumerate(process["material_rows"]):
            if row["scope"] in {"explicitly-inapplicable", "removed-process-consumable"}:
                continue
            key = row["material_key"]
            product_key = row.get("product_key")
            product = None if product_key is None else exact_product(product_key)
            if row.get("gross_length_m") is not None:
                quantity, unit = row["gross_length_m"], "m"
            elif row.get("gross_mass_kg") is not None:
                quantity, unit = row["gross_mass_kg"], "kg"
            else:
                quantity, unit = None, "kg"
            constraints = []
            identifiers = {}
            product_configuration = None
            if product is not None:
                identifiers = {"manufacturer": product["manufacturer"],
                               "part_number": product["part_number"]}
            if key == "glass-600":
                constraints = [
                    {"field": "areal_weight_g_m2", "unit": "g/m2", "minimum": "600", "maximum": "600", "scope": "dry-fabric-only"},
                    {"field": "fabric_width_m", "unit": "m", "minimum": "1.27", "maximum": "1.27", "scope": "dry-fabric-sale-width"},
                ]
            elif key == "mixed-resin-kit":
                constraints = [{"field": "hardener_included", "equals": True}]
            elif key == "core":
                constraints = [
                    {"field": "density_min_kg_m3", "unit": "kg/m3", "maximum": "85", "scope": "grade-specified-range"},
                    {"field": "density_max_kg_m3", "unit": "kg/m3", "minimum": "85", "scope": "grade-specified-range"},
                    {"field": "thickness_min_mm", "unit": "mm", "maximum": "20", "scope": "published-sheet-range"},
                    {"field": "thickness_max_mm", "unit": "mm", "minimum": "20", "scope": "published-sheet-range"},
                ]
                if product is not None:
                    identifiers = {"manufacturer": product["manufacturer"],
                                   "part_number": product["part_number"]}
                    observations = product["specifications"]["published_observations"]
                    product_configuration = dict(
                        product_record_id=product["record_id"],
                        material_product_key=product["product_key"],
                        reference_area_m2="10", target_thickness_mm="20",
                        nominal_density_kg_m3=product["specifications"]["density_kg_m3"]["value"],
                        published_density_range_kg_m3=product["specifications"]["density_range_kg_m3"]["values"],
                        published_thickness_range_mm=observations["thickness_range_mm"],
                        published_sheet_size_mm=observations["sheet_size_mm"],
                        sheet_count=None,
                        sheet_count_unknown_reason="No roof-panel nesting or cut plan is included in this 10 m² screening basis")
            requirement = record(
                "requirement", candidate_id=candidate_id, input_id=input_id,
                namespace="manufacturing-study", registry_id=None, body_candidate_id=None,
                requirement_key=f"{name}:{index}:{key}", description=f"{name} comparative material input: {key}",
                category="body-materials", priority=3, quantity=quantity, quantity_unit=unit,
                occurrence_ids=[], physical_scopes=[f"material-study/{candidate_id[:16]}/{index}/{key}"],
                procurement_scope="raw-material", identifiers=identifiers, constraints=constraints,
                process_id=process["record_id"], process_scope=row["scope"],
                process_material_key=key, net_quantity=row.get("net_length_m") if unit == "m" else row.get("net_mass_kg"),
                selected_product_record_id=None if product is None else product["record_id"],
                product_configuration=product_configuration,
                gross_quantity=quantity, unit=unit, parent_candidate_id=parent_candidate_id,
                study_basis_id=common_basis, source_ids=[] if product is None else product["source_ids"],
                evidence_status="catalogue-screen-only; not approved design or purchase")
            requirements.append(requirement)
        payload = {"schema": "osr-sourcing-declared-requirements/1",
                   "candidate_id": candidate_id, "parent_candidate_id": parent_candidate_id,
                   "source_input_id": source_input_id, "proposal": definition,
                   "physical_definition": physical_definition,
                   "process": process, "requirements": requirements,
                   "complete_installed_mass_kg": None, "complete_installed_cost": None,
                   "physical_qualification": None,
                   "limitations": [
                       "10 m² comparative material hypothesis; not taken from installed CAD roof area",
                       "No material allowables, joints, fire/smoke or hot-wet qualification inferred",
                       "The sandwich-study core is Gurit Corecell M80, a marine grade: its published 81–89 kg/m³ density and 3–53 mm sheet ranges bound a 20 mm, nominal 85 kg/m³ takeoff; the lot, rail allowables and fire/smoke qualification are unverified",
                       "Fibre fraction and scrap are explicit research assumptions",
                       "Adhesive, inserts, process consumables, labour, tooling, freight and installation unresolved",
                   ]}
        output.append(payload)
    return output
