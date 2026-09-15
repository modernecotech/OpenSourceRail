"""Idempotent operating baseline import into native ERPNext records."""
import html
import json

import frappe
from osr_erpnext.planning import digest, source_key, validate_plan
from osr_erpnext.city_config import CITY_SCHEMA, record_id, validate_city_plan


@frappe.whitelist(methods=["POST"])
def import_plan(plan, company):
    if isinstance(plan, str):
        plan = json.loads(plan)
    city_package = plan.get("schema") == CITY_SCHEMA
    (validate_city_plan if city_package else validate_plan)(plan)
    if city_package and plan["config"]["organisation"]["company"] != company:
        frappe.throw("Effective configuration must name the target company")
    frappe.get_doc("Company", company).check_permission("read")
    for doctype in ["Project", "Task"]:
        frappe.has_permission(doctype, "create", throw=True)
    project_key = source_key(company, plan, "project", plan["city"])
    project = frappe.db.get_value("Project", {"custom_osr_source_key": project_key}, "name")
    if project:
        project_doc = frappe.get_doc("Project", project)
        project_doc.check_permission("write")
        if project_doc.custom_osr_source_sha256 != plan["source_sha256"]:
            frappe.throw("Source changed under an existing planning revision; prepare a new operating release.")
        if city_package and project_doc.custom_osr_package_sha256 and project_doc.custom_osr_package_sha256 != plan["package_sha256"]:
            frappe.throw("Operating baseline is immutable. Increment release in the city profile to prepare a new baseline.")
    else:
        project_doc = frappe.get_doc(dict(doctype="Project", company=company,
            project_name=f'{plan["city"][:60]} / {plan["revision"][:32]} / {plan.get("release", "1")} / {project_key[:10]}', status="Open",
            custom_osr_source_key=project_key, custom_osr_city=plan["city"],
            custom_osr_revision=plan["revision"], custom_osr_source_sha256=plan["source_sha256"],
            notes="OSR planning baseline. Business completion cannot release railway assets.")).insert()
        project = project_doc.name
    masters = None
    if city_package:
        from osr_erpnext.city_runtime import configure_masters
        masters = configure_masters(company, plan["config"])
    # One permission-filtered read replaces one database lookup per imported task.
    existing = {r.custom_osr_source_key: r for r in frappe.get_list("Task", filters={"project": project},
        fields=["name", "custom_osr_source_key", "custom_osr_source_sha256", "custom_osr_enriched"], limit_page_length=0)}
    created = skipped = enriched = 0
    names = {}
    link_dependencies = []
    for row in plan["records"]:
        key = source_key(company, plan, row["kind"], row["uid"])
        record_sha = digest(row["source"])
        previous = existing.get(key)
        if previous and previous.custom_osr_source_sha256 != record_sha:
            frappe.throw("Source record conflicts with an existing task: " + row["uid"])
        if previous and (not city_package or previous.custom_osr_enriched):
            names[record_id(row)] = previous.name
            skipped += 1
            continue
        source = row["source"]
        if previous:
            task = frappe.get_doc("Task", previous.name)
            task.check_permission("write")
            enriched += 1
        else:
            title = source.get("work_order_title") or source.get("title") or source.get("scope") or source.get("stage") or row["uid"]
            task = frappe.get_doc(dict(doctype="Task", project=project, status="Open",
                subject=f'[{row["kind"]}] {title}'[:140],
                description=task_description(row, title),
                custom_osr_source_key=key, custom_osr_city=plan["city"],
                custom_osr_revision=plan["revision"], custom_osr_asset_id=source.get("asset_id", ""),
                custom_osr_source_sha256=record_sha,
                custom_osr_source_record=json.dumps(source, sort_keys=True, ensure_ascii=False)))
            created += 1
        if city_package:
            # First enrichment fills empty planning fields; existing operator values survive.
            for field, value in dict(type=row["task_type"], department=masters["departments"][row["department"]],
                    exp_start_date=row["start_date"], exp_end_date=row["finish_date"]).items():
                if not task.get(field):
                    task.set(field, value)
            if not previous:
                task.priority = row["priority"]
            task.custom_osr_kind = row["kind"]
            task.custom_osr_plan_start_day = row["start_day"]
            task.custom_osr_plan_finish_day = row["finish_day"]
            task.custom_osr_enriched = 1
            if not task.depends_on:
                link_dependencies.append((task, row["depends_on"]))
        # ERPNext's native bulk-update flag avoids recalculating the whole project for every task.
        task.flags.from_project = True
        task.save() if previous else task.insert()
        names[record_id(row)] = task.name
    for task, dependencies in link_dependencies:
        if dependencies:
            for key in dependencies:
                task.append("depends_on", {"task": names[key], "project": project})
            task.flags.from_project = True
            task.save()
    if city_package:
        project_doc.custom_osr_config_sha256 = plan["config_sha256"]
        project_doc.custom_osr_package_sha256 = plan["package_sha256"]
        project_doc.custom_osr_config = json.dumps(plan["config"], sort_keys=True)
        project_doc.custom_osr_release = plan["release"]
        if not project_doc.cost_center:
            project_doc.cost_center = masters["cost_center"]
        project_doc.save()
    project_doc.update_project()
    return dict(project=project, created=created, enriched=enriched, skipped=skipped, masters=masters)


def task_description(row, title):
    """Keep rich text small: full source tables live in the structured Code field."""
    source = row["source"]
    sections = [title, source.get("work_order_detail") or source.get("scope") or source.get("hold_point", ""),
                source.get("evidence_required", ""),
                "Planning reference. Complete requirements are in OSR source record; railway evidence and handback remain in OSR."]
    if row["kind"] == "procurement":
        sections.insert(1, f'{len(source.get("requirements", []))} procurement requirements. Resolve item, quantity, supplier and approvals before issuing orders.')
    return "".join("<p>" + html.escape(str(text)[:4000]) + "</p>" for text in sections if text)


def import_file(path, company):
    """Local bench-only entry point; never exposed through HTTP."""
    with open(path, encoding="utf-8") as stream:
        result = import_plan(json.load(stream), company)
    frappe.db.commit()
    return result
