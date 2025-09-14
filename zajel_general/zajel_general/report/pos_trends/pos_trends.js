// Copyright (c) 2025, Hussain and contributors
// For license information, please see license.txt

frappe.query_reports["POS Trends"] = {

	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1
		},
		{
			fieldname: "based_on",
			label: __("Based On"),
			fieldtype: "Select",
			options: ["Item","Item Group","Customer"],
			default: "Item",
			reqd: 1
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: ["", "Item","Customer"],
			default: ""
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "item_group",
			label: __("Item Group (Optional)"),
			fieldtype: "Link",
			options: "Item Group",
			depends_on: "eval: doc.based_on == 'Item Group'"
		}
	]
};
