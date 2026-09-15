"""Native ERP configuration and permission-filtered feedback to the OSR twin."""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

import frappe
from osr_erpnext.city_config import TASK_TYPES
from osr_erpnext.planning import digest
from osr_erpnext.automation_rules import task_readiness
from osr_erpnext.components import feedback as component_feedback


def configure_masters(company, config):
    city = config["city"]["slug"]
    masters = {"departments": {}, "warehouses": {}}
    def ensure(doctype, role, values):
        key = digest([company, city, doctype, role])
        name = frappe.db.get_value(doctype, {"custom_osr_master_key": key}, "name")
        if name:
            doc = frappe.get_doc(doctype, name)
            doc.check_permission("read")
            if doc.company != company:
                frappe.throw("City master belongs to another company")
            return name
        return frappe.get_doc(dict(doctype=doctype, company=company,
            custom_osr_master_key=key, **values)).insert().name
    root = frappe.db.get_value("Cost Center", {"company": company, "is_group": 1,
        "parent_cost_center": ["is", "not set"]}, "name")
    if not root:
        frappe.throw("Configure the company's root cost centre before applying a city")
    masters["cost_center"] = ensure("Cost Center", "city", dict(
        cost_center_name=f"OSR {city}", parent_cost_center=root, is_group=0))
    for label in config["organisation"]["departments"]:
        masters["departments"][label] = ensure("Department", label, dict(
            department_name=f"OSR {city} {label}", is_group=0))
    for label in config["organisation"]["warehouses"]:
        masters["warehouses"][label] = ensure("Warehouse", label, dict(
            warehouse_name=f"OSR {city} {label}", is_group=0))
    for label in TASK_TYPES.values():
        if not frappe.db.exists("Task Type", label):
            frappe.get_doc(dict(doctype="Task Type", name=label)).insert()
    return masters


@frappe.whitelist(methods=["GET"])
def city_status(project):
    """Business execution view; never a railway release/approval verdict."""
    doc = frappe.get_doc("Project", project)
    doc.check_permission("read")
    if not doc.custom_osr_city:
        frappe.throw("Select an OSR-linked project")
    tasks = frappe.get_list("Task", filters={"project": project}, fields=[
        "name", "status", "progress", "custom_osr_kind", "custom_osr_asset_id",
        "exp_start_date", "exp_end_date", "actual_time", "total_costing_amount", "_assign"], limit_page_length=0)
    kinds = defaultdict(Counter)
    assets = defaultdict(Counter)
    for row in tasks:
        kinds[row.custom_osr_kind or "legacy"][row.status] += 1
        if row.custom_osr_asset_id:
            assets[row.custom_osr_asset_id][row.status] += 1
    documents = {}
    for doctype in ["Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Work Order", "Budget"]:
        if not frappe.has_permission(doctype, "read"):
            documents[doctype] = {"available": False}
            continue
        meta = frappe.get_meta(doctype)
        rows = {}
        if meta.has_field("project"):
            rows.update({r.name: r for r in frappe.get_list(doctype,
                filters={"project": project, "company": doc.company}, fields=["name", "docstatus"], limit_page_length=0)})
        child = meta.get_field("items")
        if child and frappe.get_meta(child.options).has_field("project"):
            # Query through the parent so native document permissions still apply.
            rows.update({r.name: r for r in frappe.get_list(doctype,
                filters=[[child.options, "project", "=", project], [doctype, "company", "=", doc.company]],
                fields=["name", "docstatus"], distinct=True, limit_page_length=0)})
        elif not meta.has_field("project"):
            documents[doctype] = {"available": False, "reason": "no-project-link"}
            continue
        rows = list(rows.values())
        documents[doctype] = {"available": True, "draft": sum(r.docstatus == 0 for r in rows),
                              "submitted": sum(r.docstatus == 1 for r in rows),
                              "cancelled": sum(r.docstatus == 2 for r in rows)}
    return dict(schema="osr-operating-snapshot/1", observed_at=datetime.now(timezone.utc).isoformat(),
        city=doc.custom_osr_city, company=doc.company, project=doc.name,
        engineering_revision=doc.custom_osr_revision, operating_release=doc.custom_osr_release or "legacy",
        config_sha256=doc.custom_osr_config_sha256, package_sha256=doc.custom_osr_package_sha256,
        currency=frappe.db.get_value("Company", doc.company, "default_currency"),
        task_count=len(tasks), task_status=dict(Counter(r.status for r in tasks)),
        readiness=task_readiness(tasks, frappe.utils.today()),
        components=component_feedback(project),
        categories={key: dict(value) for key, value in sorted(kinds.items())},
        asset_work={key: dict(value) for key, value in sorted(assets.items())},
        actual_hours=sum(float(r.actual_time or 0) for r in tasks),
        task_cost=sum(float(r.total_costing_amount or 0) for r in tasks),
        business_documents=documents, visibility="records-visible-to-current-ERP-user",
        authority="business-execution-only; railway assurance and handback remain in OSR")


def export_snapshots(path):
    """Bench-only private export, never a public file-serving endpoint."""
    projects = frappe.get_list("Project", filters={"custom_osr_city": ["!=", ""]},
                               fields=["name"], limit_page_length=0)
    result = dict(schema="osr-operating-portfolio/1", snapshots=[city_status(p.name) for p in projects])
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, default=str)
    return {"projects": len(projects)}
