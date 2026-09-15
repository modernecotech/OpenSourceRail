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

doc_events = {"OSR Execution Mapping": {"validate": "osr_erpnext.integration.validate_execution_mapping"}}

app_include_js = ["/assets/osr_erpnext/js/workbench.js"]
