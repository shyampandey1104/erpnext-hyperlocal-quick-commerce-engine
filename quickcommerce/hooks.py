# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "quickcommerce"
app_title = "Erpnext Hyperlocal Quick Commerce Engine"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Hyperlocal Quick Commerce Engine for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/quickcommerce/css/quickcommerce.bundle.css"
app_include_js = "/assets/quickcommerce/js/quickcommerce.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "quickcommerce.engine.on_document_submit",
        "on_cancel": "quickcommerce.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "quickcommerce.engine.daily_scheduled_sync"
    ]
}
