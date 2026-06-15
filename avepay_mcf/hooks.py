app_name = "avepay_mcf"
app_title = "AvePay MCF"
app_publisher = "AvePay"
app_description = "Certification fiscale MCF (DGI Burkina / SECEF) pour ERPNext"
app_email = "dev@avepay.net"
app_license = "mit"

# Apps
# ------------------

required_apps = ["frappe/erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "avepay_mcf",
# 		"logo": "/assets/avepay_mcf/logo.png",
# 		"title": "AvePay MCF",
# 		"route": "/avepay_mcf",
# 		"has_permission": "avepay_mcf.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/avepay_mcf/css/avepay_mcf.css"
# app_include_js = "/assets/avepay_mcf/js/avepay_mcf.js"

# include js, css files in header of web template
# web_include_css = "/assets/avepay_mcf/css/avepay_mcf.css"
# web_include_js = "/assets/avepay_mcf/js/avepay_mcf.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "avepay_mcf/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "avepay_mcf/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "avepay_mcf.utils.jinja_methods",
# 	"filters": "avepay_mcf.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "avepay_mcf.install.before_install"
# after_install = "avepay_mcf.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "avepay_mcf.uninstall.before_uninstall"
# after_uninstall = "avepay_mcf.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "avepay_mcf.utils.before_app_install"
# after_app_install = "avepay_mcf.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "avepay_mcf.utils.before_app_uninstall"
# after_app_uninstall = "avepay_mcf.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "avepay_mcf.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "avepay_mcf.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"avepay_mcf.tasks.all"
# 	],
# 	"daily": [
# 		"avepay_mcf.tasks.daily"
# 	],
# 	"hourly": [
# 		"avepay_mcf.tasks.hourly"
# 	],
# 	"weekly": [
# 		"avepay_mcf.tasks.weekly"
# 	],
# 	"monthly": [
# 		"avepay_mcf.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "avepay_mcf.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "avepay_mcf.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "avepay_mcf.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "avepay_mcf.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["avepay_mcf.utils.before_request"]
# after_request = ["avepay_mcf.utils.after_request"]

# Job Events
# ----------
# before_job = ["avepay_mcf.utils.before_job"]
# after_job = ["avepay_mcf.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"avepay_mcf.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# ----------------------------------------------------------------------
# AvePay MCF — certification fiscale des factures
# ----------------------------------------------------------------------
doc_events = {
    "Sales Invoice": {
        "validate": "avepay_mcf.certify.validate_certifiable",
        "on_submit": "avepay_mcf.certify.certify_invoice",
    },
}

# Auto-détection des mappings taxes/paiements à l'installation.
after_install = "avepay_mcf.install.after_install"

# Bouton « Auto-détecter les mappings » sur le formulaire AvePay Settings.
doctype_js = {"AvePay Settings": "public/js/avepay_settings.js"}

# Mode file d'attente : rattrapage des factures non certifiées toutes les 10 min.
scheduler_events = {
    "cron": {
        "*/10 * * * *": ["avepay_mcf.certify.retry_pending"],
    },
}

# Méthode QR SECEF disponible dans les Print Formats : {{ qr_data_uri(doc.avepay_qr) }}
jinja = {
    "methods": [
        "avepay_mcf.print_utils.qr_data_uri",
        "avepay_mcf.print_utils.secef_tax_label",
    ],
}

# Custom Fields + Print Format livrés avec l'app (export via `bench export-fixtures`).
fixtures = [
    {"dt": "Custom Field", "filters": [["fieldname", "like", "avepay_%"]]},
    {"dt": "Print Format", "filters": [["name", "=", "AvePay Facture Certifiee"]]},
    {"dt": "Workspace", "filters": [["name", "=", "AvePay MCF"]]},
]
