app_name = "zajel_general"
app_title = "Zajel General"
app_publisher = "Hussain"
app_description = "Zajel General"
app_email = "hussain@tabrah-holding.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "zajel_general",
# 		"logo": "/assets/zajel_general/logo.png",
# 		"title": "Zajel General",
# 		"route": "/zajel_general",
# 		"has_permission": "zajel_general.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/zajel_general/css/zajel_general.css"
# app_include_js = "/assets/zajel_general/js/zajel_general.js"

# include js, css files in header of web template
# web_include_css = "/assets/zajel_general/css/zajel_general.css"
# web_include_js = "/assets/zajel_general/js/zajel_general.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "zajel_general/public/scss/website"

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
# app_include_icons = "zajel_general/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "zajel_general.utils.jinja_methods",
# 	"filters": "zajel_general.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "zajel_general.install.before_install"
# after_install = "zajel_general.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "zajel_general.uninstall.before_uninstall"
# after_uninstall = "zajel_general.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "zajel_general.utils.before_app_install"
# after_app_install = "zajel_general.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "zajel_general.utils.before_app_uninstall"
# after_app_uninstall = "zajel_general.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "zajel_general.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Purchase Order": {
        "validate": "zajel_general.custom.purchase_order_custom.validate"
    },
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"zajel_general.tasks.all"
# 	],
# 	"daily": [
# 		"zajel_general.tasks.daily"
# 	],
# 	"hourly": [
# 		"zajel_general.tasks.hourly"
# 	],
# 	"weekly": [
# 		"zajel_general.tasks.weekly"
# 	],
# 	"monthly": [
# 		"zajel_general.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "zajel_general.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "zajel_general.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "zajel_general.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["zajel_general.utils.before_request"]
# after_request = ["zajel_general.utils.after_request"]

# Job Events
# ----------
# before_job = ["zajel_general.utils.before_job"]
# after_job = ["zajel_general.utils.after_job"]

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
# 	"zajel_general.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

