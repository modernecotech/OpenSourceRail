"""Small, repeatable extensions to standard ERPNext records; no parallel ERP."""
import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def install():
    fields = []
    for name, label, fieldtype in [
        ("source_key", "OSR source key", "Data"),
        ("city", "OSR city", "Data"),
        ("revision", "OSR planning revision", "Data"),
        ("asset_id", "OSR railway asset ID", "Data"),
        ("source_sha256", "OSR source SHA-256", "Data"),
        ("source_record", "OSR source record (planning evidence)", "Code"),
    ]:
        fields.append(dict(fieldname="custom_osr_" + name, label=label,
                           fieldtype=fieldtype, read_only=1, no_copy=1,
                           unique=1 if name == "source_key" else 0))
    create_custom_fields({doctype: fields for doctype in ["Project", "Task"]})
    create_custom_fields({"Project": [
        dict(fieldname="custom_osr_config_sha256", label="OSR configuration SHA-256", fieldtype="Data", read_only=1),
        dict(fieldname="custom_osr_package_sha256", label="OSR operating package SHA-256", fieldtype="Data", read_only=1),
        dict(fieldname="custom_osr_config", label="OSR effective city configuration", fieldtype="Code", options="JSON", read_only=1),
        dict(fieldname="custom_osr_release", label="OSR operating release", fieldtype="Data", read_only=1),
        dict(fieldname="custom_osr_component_profile", label="Operating component profile", fieldtype="Code", options="JSON", read_only=1),
    ], "Task": [
        dict(fieldname="custom_osr_kind", label="OSR work category", fieldtype="Data", read_only=1, in_standard_filter=1),
        dict(fieldname="custom_osr_plan_start_day", label="OSR baseline start day", fieldtype="Int", read_only=1),
        dict(fieldname="custom_osr_plan_finish_day", label="OSR baseline finish day", fieldtype="Int", read_only=1),
        dict(fieldname="custom_osr_enriched", label="OSR city configuration applied", fieldtype="Check", read_only=1),
    ]})
    create_custom_fields({dt: [dict(fieldname="custom_osr_master_key", label="OSR master key",
        fieldtype="Data", read_only=1, unique=1, no_copy=1, hidden=1)] for dt in ["Department", "Warehouse", "Cost Center"]})
    # Asset identity is a reference, not authority to commission or release an asset.
    create_custom_fields({"Asset": [dict(fieldname="custom_osr_asset_id",
        label="OSR railway asset ID", fieldtype="Data", unique=1, insert_after="asset_name")]})
    create_custom_fields({"Material Request": [
        dict(fieldname="custom_osr_" + name, label=label, fieldtype=kind,
             options=options, read_only=1, no_copy=1, unique=1 if name == "request_key" else 0)
        for name, label, kind, options in [
            ("request_key", "OSR request identity", "Data", None),
            ("request_sha256", "OSR request input checksum", "Data", None),
            ("procurement_task", "OSR procurement task", "Link", "Task"),
            ("requirement_id", "OSR requirement", "Data", None),
            ("requirement_source", "OSR planning requirement", "Code", "JSON"),
        ]]})
    from osr_erpnext.components import META_TYPES
    for target in META_TYPES:
        previous = frappe.get_doc('DocType', target).fields[-1].fieldname
        extension = []
        if target != 'Item Reorder':
            previous = 'custom_osr_components_tab'
            extension.append(dict(fieldname=previous, label='Operating component', fieldtype='Tab Break',
                insert_after=frappe.get_doc('DocType', target).fields[-1].fieldname))
        for name, label, kind, options in [
            ('component_project', 'City project', 'Link', 'Project'),
            ('component', 'Component', 'Data', None), ('instance', 'Instance', 'Data', None),
            ('component_key', 'Component identity', 'Data', None),
            ('component_sha256', 'Component input checksum', 'Data', None),
        ]:
            fieldname = 'custom_osr_' + name
            extension.append(dict(fieldname=fieldname, label=label, fieldtype=kind, options=options,
                read_only=1, no_copy=1, unique=1 if name == 'component_key' else 0,
                hidden=1 if target == 'Item Reorder' else 0, insert_after=previous))
            previous = fieldname
        create_custom_fields({target: extension})
    # Keep provenance available for review without displacing native daily work.
    for doctype in ["Project", "Task", "Material Request"]:
        reference_tab = "custom_osr_reference_tab"
        last_native_field = frappe.get_doc("DocType", doctype).fields[-1].fieldname
        create_custom_fields({doctype: [dict(fieldname=reference_tab,
            label="OpenSourceRail reference", fieldtype="Tab Break", insert_after=last_native_field)]})
        previous = reference_tab
        for row in frappe.get_all("Custom Field", filters={"dt": doctype,
                "fieldname": ["like", "custom_osr_%"]}, fields=["name", "fieldname"], order_by="creation asc, name asc"):
            if row.fieldname == reference_tab:
                continue
            field = frappe.get_doc("Custom Field", row.name)
            if field.insert_after != previous:
                field.insert_after = previous
                field.save()
            previous = row.fieldname
    if not frappe.db.exists("Workspace", "OpenSourceRail"):
        links = [("Projects", "Project"), ("Tasks", "Task"),
                 ("Purchasing", "Purchase Order"), ("Stock", "Stock Entry"),
                 ("Assets", "Asset"), ("Maintenance", "Asset Maintenance"),
                 ("Repairs", "Asset Repair"), ("Manufacturing", "Work Order"),
                 ("Invoices", "Purchase Invoice"), ("Payments", "Payment Entry"),
                 ("Employees", "Employee"), ("Payroll", "Payroll Entry")]
        content = [{"id": "osr-heading", "type": "header", "data": {
            "text": "OpenSourceRail business operations", "col": 12}}]
        content += [{"id": "osr-" + str(i), "type": "shortcut", "data": {
            "shortcut_name": label, "col": 3}} for i, (label, _) in enumerate(links)]
        frappe.get_doc(dict(doctype="Workspace", name="OpenSourceRail",
            label="OpenSourceRail", title="OpenSourceRail", public=1,
            module="OpenSourceRail", icon="organization", content=json.dumps(content),
            shortcuts=[dict(label=label, type="DocType", link_to=dt,
                            doc_view="List") for label, dt in links])).insert()


def create_evaluation_company():
    """Explicit local evaluation fixture. Never used by site installation."""
    name = "OpenSourceRail Evaluation"
    if not frappe.is_setup_complete():
        from datetime import date
        from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
        year = date.today().year
        setup_complete(dict(language="English", country="Iraq", currency="USD",
            timezone="Asia/Baghdad", time_zone="Asia/Baghdad",
            company_name=name, company_abbr="OSRE", chart_of_accounts="Standard",
            fy_start_date=f"{year}-01-01", fy_end_date=f"{year}-12-31"))
    if not frappe.db.exists("Company", name):
        frappe.get_doc(dict(doctype="Company", company_name=name, abbr="OSRE",
            default_currency="USD", country="Iraq",
            chart_of_accounts="Standard", create_chart_of_accounts_based_on="Standard Template")).insert()
    return name
