app_name = "osr_erpnext"
app_title = "OpenSourceRail"
app_publisher = "OpenSourceRail contributors"
app_description = "Business operations on ERPNext; railway authority stays in OSR"
app_email = "opensource-rail@example.invalid"
app_license = "Apache-2.0"
required_apps = ["erpnext", "hrms"]
after_install = "osr_erpnext.setup.install"
after_migrate = "osr_erpnext.setup.install"
doctype_js = {"Project": "public/js/project.js", "Task": "public/js/task.js", "Issue": "public/js/issue.js"}

doc_events = {
    "OSR Field Execution": {"validate": "osr_erpnext.field_operations.validate_receipt"},
    "Task": {"validate": "osr_erpnext.construction_execution.validate_task"},
    "ToDo": {"validate": "osr_erpnext.construction_execution.validate_assignment"},
    "Asset": {"validate": "osr_erpnext.construction_execution.validate_controlled_evidence",
              "before_update_after_submit": "osr_erpnext.construction_execution.validate_controlled_evidence"},
    "Employee": {"validate": "osr_erpnext.construction_execution.validate_controlled_evidence"},
    "OSR Construction Release": {"before_submit": "osr_erpnext.construction_execution.submit_review", "on_submit": "osr_erpnext.construction_execution.attach_review"},
    "Material Request": {"before_validate": "osr_erpnext.replenishment.assign_city_scope"},
    "Request for Quotation": {
        "validate": "osr_erpnext.sourcing.validate_rfq",
        "before_update_after_submit": "osr_erpnext.sourcing.validate_rfq",
        "before_rename": "osr_erpnext.sourcing.preserve_sourcing_record",
        "on_trash": "osr_erpnext.sourcing.preserve_sourcing_record",
    },
    "Supplier Quotation": {
        "before_insert": "osr_erpnext.sourcing.assign_supplier_owner",
        "validate": "osr_erpnext.sourcing.validate_quotation",
        "before_update_after_submit": "osr_erpnext.sourcing.validate_quotation",
        "before_rename": "osr_erpnext.sourcing.preserve_sourcing_record",
        "on_trash": "osr_erpnext.sourcing.preserve_sourcing_record",
    },
    "Note": {
        "validate": "osr_erpnext.sourcing.protect_sourcing_note",
        "before_rename": "osr_erpnext.sourcing.preserve_sourcing_record",
        "on_trash": "osr_erpnext.sourcing.preserve_sourcing_record",
    },
    "DocShare": {"validate": "osr_erpnext.sourcing.protect_sourcing_share"},
    "OSR Disposition Execution": {"validate": "osr_erpnext.disposition.validate", "on_trash": "osr_erpnext.disposition.prevent_delete"},
    "OSR Revision Disposition": {"validate": "osr_erpnext.disposition.validate", "on_trash": "osr_erpnext.disposition.prevent_delete"},
    "OSR Disposition Decision": {"validate": "osr_erpnext.disposition.validate", "on_trash": "osr_erpnext.disposition.prevent_delete"},
    "OSR Execution Mapping": {"validate": "osr_erpnext.integration.validate_execution_mapping"},
    "Asset Repair": {"validate": "osr_erpnext.integration.validate_condition_repair"},
}

app_include_js = ["/assets/osr_erpnext/js/workbench.js", "/assets/osr_erpnext/js/dispositions.js"]

boot_session = "osr_erpnext.integration_boot.boot_session"

has_website_permission = {
    "Supplier Quotation": "osr_erpnext.sourcing.protect_website_quotation",
}

website_redirects = [
    {"source": r"/rfq/(OSR-RFQ-[a-f0-9]{64})(?:\.html)?", "target": r"/airport-sourcing?rfq=\1",
     "redirect_http_status": 302},
]

override_whitelisted_methods = {
    "frappe.www.list.get": "osr_erpnext.sourcing.website_list",
    "frappe.www.list.get_list_data": "osr_erpnext.sourcing.website_list_data",
    "erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_rfq_containing_supplier":
        "osr_erpnext.sourcing.desk_rfq_lookup",
}
