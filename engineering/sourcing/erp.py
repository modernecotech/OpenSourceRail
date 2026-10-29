"""Disabled research procurement exports. No network or active-order mutation."""
from collections import defaultdict
from .model import record, validate_record, identity
from .requirements import validate_requirements


def build_rfq_drafts(requirements, assessments=()):
    candidate = validate_requirements(requirements)
    leads = defaultdict(set)
    for assessment in assessments:
        validate_record(assessment, "assessment")
        if assessment["candidate_id"] != candidate:
            raise ValueError("Mixed RFQ assessment candidate")
        if assessment.get("product_id"):
            leads[assessment["requirement_id"]].add(assessment["product_id"])
    groups = defaultdict(list)
    for requirement in requirements:
        groups[requirement.get("category", "other")].append(requirement)
    return [record("rfq", candidate_id=candidate, category=category,
        requirement_ids=[r["record_id"] for r in sorted(rows, key=lambda r:r["record_id"])],
        requested_items=[dict(requirement_id=r["record_id"], namespace=r["namespace"],
            part_definition_id=r.get("part_definition_id"), part_revision_id=r.get("part_revision_id"),
            registry_id=r.get("registry_id"), description=r["description"], quantity=r["quantity"],
            quantity_unit=r["quantity_unit"], occurrence_ids=r["occurrence_ids"],
            input_id=r["input_id"], scope_kind=r.get("scope_kind"), required_supply_scope=r.get("procurement_scope"),
            geometry=r.get("geometry"), material_id=r.get("material_id"),
            technical_constraints=r.get("constraints", []), functions=r.get("functions", []),
            selected_product_record_id=r.get("selected_product_record_id"),
            product_configuration=r.get("product_configuration"),
            reference_mass_per_unit_kg=r.get("mass_per_unit_kg"),
            reference_accounted_mass_kg_per_car=r.get("accounted_mass_kg_per_car"),
            source_manufacturing_group_id=r.get("source_manufacturing_group_id"),
            source_manufacturing_group=r.get("source_manufacturing_group"),
            engineering_occurrence_count=r.get("engineering_occurrence_count", len(r["occurrence_ids"])),
            source_gross_stock_mass_kg=r.get("accounted_mass_kg"),
            scene_component_definition_ids=r.get("scene_component_definition_ids", []),
            scene_geometry_ids=r.get("scene_geometry_ids", []),
            system=r.get("system"), material=r.get("material"), stock_scope=r.get("stock_scope"),
            procurement_unit_status=r.get("procurement_unit_status"),
            complete_installed_definition=False,
            product_lead_ids=sorted(leads[r["record_id"]]),
            unresolved_definition=r["quantity"] is None,
            requested_evidence=["configured dimensions and installed scope", "mass and operating domain", "purchasing unit, conversion and usable quantity", "dated quantity price and currency", "MOQ/order multiples", "lead time, delivery terms and origin", "qualification and maintenance records"])
            for r in sorted(rows, key=lambda r:r["record_id"])],
        supplier=None, docstatus=0, submission_allowed=False, send_supplier_emails=False,
        purchase_authorized=False, ready_for_production_import=False)
        for category, rows in sorted(groups.items())]


def delivery_drafts(requirements, assessments=(), *, existing_orders=()):
    candidate = validate_requirements(requirements)
    requirements = sorted(requirements, key=lambda r:r["record_id"])
    rfqs = build_rfq_drafts(requirements, assessments)
    items = []
    for requirement in requirements:
        items.append(dict(doctype="Item", item_code="OSR-SOURCING-"+requirement["record_id"],
            item_name=requirement["description"], candidate_id=candidate,
            requirement_id=requirement["record_id"], registry_id=requirement.get("registry_id"),
            part_definition_id=requirement.get("part_definition_id"), part_revision_id=requirement.get("part_revision_id"),
            source_manufacturing_group_id=requirement.get("source_manufacturing_group_id"),
            engineering_occurrence_ids=requirement["occurrence_ids"],
            source_gross_stock_mass_kg=requirement.get("accounted_mass_kg"),
            procurement_unit_status=requirement.get("procurement_unit_status"),
            disabled=1, is_stock_item=0, docstatus=0, procurement_approved=False,
            submission_allowed=False, source_observation_ids=[]))
    bom = dict(doctype="BOM", item="OSR-SOURCING-CANDIDATE-"+candidate,
        candidate_id=candidate, docstatus=0, is_active=0, is_default=0,
        submission_allowed=False, manufacturing_release=False, total_cost=None,
        scope="Engineering quantity draft; not a manufacturing routing or released MBOM",
        items=[dict(item_code="OSR-SOURCING-"+r["record_id"], qty=r["quantity"], uom=r["quantity_unit"],
                    namespace=r["namespace"], occurrence_ids=r["occurrence_ids"],
                    source_manufacturing_group_id=r.get("source_manufacturing_group_id"),
                    procurement_unit_status=r.get("procurement_unit_status"))
               for r in requirements if r["quantity"] is not None],
        unresolved_requirement_ids=[r["record_id"] for r in requirements if r["quantity"] is None])
    # Existing orders are referenced for review, never patched or resubmitted.
    reviews = []
    for order in existing_orders:
        if not isinstance(order, dict) or not order.get("order_id"):
            raise ValueError("Explicit existing-order identity required")
        reviews.append(dict(order_id=order["order_id"], active_order_unchanged=True,
            requested_candidate_id=candidate, action="operator-change-review-required",
            mutation_allowed=False))
    value = dict(schema="osr-sourcing-erpnext-drafts/1", candidate_id=candidate,
        items=items, BOM=bom, RFQs=rfqs, existing_order_reviews=reviews,
        posted=False, ready_for_import=False, send_supplier_emails=False,
        active_order_mutations=0, procurement_approved=False, manufacturing_release=False)
    value["draft_id"] = identity(value)
    return value
