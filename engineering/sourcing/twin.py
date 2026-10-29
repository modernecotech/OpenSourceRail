"""Explicit supplier/property revisions and dependent-evaluation invalidation."""
from copy import deepcopy
from .model import record, validate_record, decimal, identity


def invalidation_plan(changes):
    affected = {"procurement", "cost", "manufacturing", "electrical-interfaces", "thermal-cooling", "maintenance-repair"}
    if any(key in changes for key in ("mass_per_unit_kg", "geometry", "material_id")):
        affected.update(("mass-CG-inertia", "structure-joints", "propulsion", "braking", "civil-loads", "energy", "protected-stopping"))
    if "geometry" in changes:
        affected.update(("CAD-IFC", "interference", "dynamic-clearance", "assembly-access"))
    if "material_id" in changes:
        affected.update(("buckling", "fatigue", "fire-thermal", "joining-process"))
    return [dict(evaluator=name, status="pending-recomputation", accepted=False) for name in sorted(affected)]


def discovery_task(requirement, product, assessment):
    validate_record(requirement, "requirement")
    validate_record(product, "product")
    validate_record(assessment, "assessment")
    if assessment.get("candidate_id") != requirement["candidate_id"] or assessment.get("requirement_id") != requirement["record_id"] or assessment.get("product_id") != product["record_id"]:
        raise ValueError("Mixed discovery candidate or product")
    return record("redesign", candidate_id=requirement["candidate_id"], task_type="supplier-specification-review",
        requirement_id=requirement["record_id"], product_id=product["record_id"], assessment_id=assessment["record_id"],
        reason_codes=assessment.get("holds", []), source_ids=product["source_ids"],
        proposed_candidate_id=None, physical_revision_executed=False,
        action="Resolve supplier configuration and interfaces, then explicitly generate a revised candidate",
        required_rechecks=invalidation_plan({"mass_per_unit_kg": None, "geometry": None}),
        selection_purpose="next-experiment-only", operating_map_admitted=False)


def propose_revision(registry, requirement, product, *, changes, reason, mode="supplier-substitution"):
    """Return {proposal, registry}; the large registry is not an observation row.

    Property-only evidence updates keep the physical identity and ancestry. A new
    product, material or actual geometry creates a distinct physical candidate.
    Poses are retained; fitment remains invalidated rather than silently passed.
    """
    from engineering.component_registry import validate_registry, make_part, make_registry, summary
    validate_registry(registry)
    validate_record(requirement, "requirement")
    validate_record(product, "product")
    if requirement["namespace"] != "component_registry" or requirement.get("registry_id") != registry["registry_id"] or requirement.get("body_candidate_id") != registry["candidate_id"]:
        raise ValueError("Exact current registry-bound requirement required")
    if mode not in ("supplier-substitution", "property-evidence") or not isinstance(changes, dict) or not changes:
        raise ValueError("Explicit physical/property revision required; price discoveries use an overlay")
    allowed = {"mass_per_unit_kg", "geometry", "material_id", "material_evaluation_id"}
    if set(changes) - allowed:
        raise ValueError("Unsupported revision field; commercial changes must not rewrite a registry")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Revision reason required")
    old = next((p for p in registry["parts"] if p["physical_definition_id"] == requirement.get("part_definition_id")), None)
    if old is None or old["revision_id"] != requirement.get("part_revision_id"):
        raise ValueError("Stale physical part revision")
    expected = {o["occurrence_id"] for o in registry["occurrences"] if o["part_definition_id"] == old["physical_definition_id"]}
    if set(requirement["occurrence_ids"]) != expected:
        raise ValueError("Substitution must bind the actual complete occurrence group")
    supply_scope = product.get("supply_scope", product.get("scope"))
    if supply_scope is None or supply_scope != requirement.get("procurement_scope"):
        raise ValueError("Configured supplier scope must match the actual replaced part")
    if mode == "property-evidence":
        from .matching import _exact_identifier
        if not _exact_identifier(requirement, product) or set(changes) != {"mass_per_unit_kg"}:
            raise ValueError("Property-only update requires the identical manufacturer/part and mass evidence")
    geometry = deepcopy(changes.get("geometry", old["geometry"]))
    if "geometry" in changes:
        dimensions = product["specifications"].get("dimensions_m")
        if isinstance(dimensions, dict) and dimensions.get("unit") != "m":
            raise ValueError("Configured supplier dimensions must explicitly use metres")
        dims = dimensions.get("value") if isinstance(dimensions, dict) else dimensions
        supplied_dims = geometry.get("dimensions_m")
        if not isinstance(dims, list) or len(dims) != 3 or not isinstance(supplied_dims, list) or len(supplied_dims) != 3 or geometry.get("kind") != "envelope" or any(decimal(a,positive=True)!=decimal(b,positive=True) for a,b in zip(dims,supplied_dims)):
            raise ValueError("New purchased geometry needs exact configured supplier envelope dimensions")
        geometry["dimensions_m"] = [float(decimal(d,positive=True)) for d in dims]
        geometry["net_volume_m3"] = None
    mass = (deepcopy(old["mass"]) if mode == "property-evidence" else
            dict(calculated_kg=None, lower_bound_kg=None, upper_bound_kg=None, evidence_state="unresolved"))
    if "mass_per_unit_kg" in changes:
        supplied = product["specifications"].get("mass_kg")
        if not isinstance(supplied, dict) or supplied.get("unit") != "kg" or supplied.get("scope") not in (supply_scope, "one-part", "configured-product"):
            raise ValueError("Supplier mass must cover the same physical product")
        proposed = decimal(changes["mass_per_unit_kg"], "supplier mass", positive=True)
        if proposed != decimal(supplied.get("value"), "observed supplier mass", positive=True):
            raise ValueError("Mass revision differs from its source observation")
        mass = dict(calculated_kg=float(proposed), lower_bound_kg=None, upper_bound_kg=None,
                    evidence_state="supplier-typical", source_record_ids=product["source_ids"],
                    catalogue_mass_is_measured_installed_mass=False)
    material_id = changes.get("material_id", old["material_id"])
    material_eval = changes.get("material_evaluation_id", old.get("material_evaluation_id"))
    if material_id != old["material_id"]:
        material = next((m for m in registry["materials"] if m["material_id"] == material_id), None)
        if material is None or material_eval != material["material_evaluation_id"]:
            raise ValueError("Material substitution requires a complete existing matching grade evaluation")
    assembly = deepcopy(old["assembly"])
    if mode == "supplier-substitution":
        assembly["sourcing_product_key"] = product["product_key"]
    evidence = deepcopy(old["evidence"])
    evidence.update(sourcing_product_evaluation_id=product["record_id"], sourcing_source_ids=product["source_ids"],
                    prior_part_revision_id=old["revision_id"], installed_fitment_accepted=False)
    manufacturing = deepcopy(old["manufacturing"])
    electrical = deepcopy(old["electrical_thermal"])
    lifecycle = deepcopy(old["lifecycle"])
    if mode == "supplier-substitution":
        evidence.update(prior_manufacturing=manufacturing, prior_electrical_thermal=electrical, prior_lifecycle=lifecycle)
        manufacturing = dict(method="configured-supplier-receiving-and-installation-process-unresolved", cycle_hours=None,
                             scrap_fraction=None, approved_work_instruction=None)
        electrical = dict(installed_interface_definition="unresolved", power_W=None, cooling_duty_W=None)
        lifecycle = dict(inspection_interval=None, replacement=None, repair_method=None, recycling=None)
    replacement = make_part(old["part_id"] if mode == "property-evidence" else old["part_id"]+"/supplier-"+identity(product["product_key"])[:12],
        "SOURCING-"+identity(dict(product=product["record_id"], changes=changes))[:12], old["functions"], geometry,
        material_id, mass, manufacturing, assembly=assembly, electrical_thermal=electrical,
        procurement=dict(supplier=None, manufacturer=product["manufacturer"], manufacturer_part_number=product["part_number"],
                         country_of_origin=product.get("country_of_origin"), quote_id=None, MOQ=None, lead_days=None),
        evidence=evidence, lifecycle=lifecycle, material_evaluation_id=material_eval)
    occurrences = deepcopy(registry["occurrences"])
    for occurrence in occurrences:
        if occurrence["part_definition_id"] == old["physical_definition_id"]:
            occurrence.update(part_definition_id=replacement["physical_definition_id"], part_revision_id=replacement["revision_id"])
    parts = [replacement if p["physical_definition_id"] == old["physical_definition_id"] else deepcopy(p) for p in registry["parts"]]
    revised = make_registry(registry["label"], parts, occurrences, registry["required_functions"],
        parent_candidate_id=registry.get("parent_candidate_id") if mode == "property-evidence" else registry["candidate_id"],
        assemblies=registry["assemblies"], materials=registry["materials"])
    if mode == "property-evidence" and revised["candidate_id"] != registry["candidate_id"]:
        raise ValueError("A property evaluation must not mutate physical identity")
    proposal = record("redesign", candidate_id=requirement["candidate_id"], task_type="explicit-registry-revision",
        mode=mode, reason=reason, parent_body_candidate_id=registry["candidate_id"], parent_registry_id=registry["registry_id"],
        proposed_body_candidate_id=revised["candidate_id"], proposed_registry_id=revised["registry_id"],
        proposed_integrated_candidate_id=None, integration_state="requires-explicit-whole-candidate-rematerialization",
        requirement_id=requirement["record_id"], product_id=product["record_id"], source_ids=product["source_ids"],
        changed_occurrence_ids=sorted(expected), changes=deepcopy(changes), mass_coverage=summary(revised),
        dependent_evaluations=invalidation_plan(changes), operating_map_admitted=False,
        inherited_envelope_is_configured_supplier_geometry="geometry" in changes,
        supplier_installation_and_thermal_definitions_pending=mode=="supplier-substitution",
        automatic_manufacturing_or_operating_release=False, physical_qualification=None)
    return dict(schema="osr-sourcing-proposed-revision/1", proposal=proposal, registry=revised)
