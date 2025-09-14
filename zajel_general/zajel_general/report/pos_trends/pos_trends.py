# file: erpnext/accounts/report/sales_invoice_trends_by_date/sales_invoice_trends_by_date.py

import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
	# force this clone to be Sales Invoice only
	trans = "Sales Invoice"
	conds = get_columns(filters, trans)
	data = get_data(filters, conds)
	return conds["columns"], data

def get_columns(filters, trans):
	validate_filters(filters)

	# based_on section (unchanged)
	based_on_details = based_wise_columns_query(filters.get("based_on"), trans)

	# *** minimal change: single date-range bucket instead of Periods/FY ***
	period_cols = [
		_("Qty") + ":Float:120",
		_("Amt") + ":Currency/currency:120",
	]
	# we still keep the same interface key name to avoid touching other code paths
	period_select = (
		"SUM(CASE WHEN t1.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN t2.stock_qty END),"
		"SUM(CASE WHEN t1.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN t2.base_net_amount END),"
	)

	# group-by header (unchanged)
	group_by_cols = group_wise_column(filters.get("group_by"))

	columns = (
		based_on_details["based_on_cols"]
		+ period_cols
		+ [_("Total(Qty)") + ":Float:120", _("Total(Amt)") + ":Currency/currency:120"]
	)
	if group_by_cols:
		columns = (
			based_on_details["based_on_cols"]
			+ group_by_cols
			+ period_cols
		)

	return {
		"based_on_select": based_on_details["based_on_select"],
		"period_wise_select": period_select + "SUM(t2.stock_qty), SUM(t2.base_net_amount)",
		"columns": columns,
		"group_by": based_on_details["based_on_group_by"],
		"grbc": group_by_cols,
		"trans": trans,
		"addl_tables": based_on_details["addl_tables"],
		"addl_tables_relational_cond": based_on_details.get("addl_tables_relational_cond", ""),
	}

def validate_filters(filters):
	# minimal: require company, based_on, from/to dates
	for f in ["Company", "Based On", "From Date", "To Date"]:
		key = f.lower().replace(" ", "_")
		if not filters.get(key):
			frappe.throw(_("{0} is mandatory").format(_(f)))
	if filters.get("based_on") == filters.get("group_by"):
		frappe.throw(_("'Based On' and 'Group By' cannot be the same"))

def get_data(filters, conditions):
	data = []
	posting_date = "t1.posting_date"

	# optional extra condition: only apply item_group filter when provided
	extra_cond = ""
	params = {
		"company": filters.get("company"),
		"from_date": filters.get("from_date"),
		"to_date": filters.get("to_date"),
	}

	# if you supply an Item Group filter, apply it (works regardless of Based On / Group By)
	if filters.get("item_group"):
		extra_cond += " and t2.item_group = %(item_group)s"
		params["item_group"] = filters.get("item_group")

	# handle group_by branch (kept identical to original, only date/params changed)
	if filters.get("group_by"):
		query_details = conditions["based_on_select"] + conditions["period_wise_select"]
		cond = ""
		if conditions["based_on_select"] in ["t1.project,", "t2.project,"]:
			cond = " and " + conditions["based_on_select"][:-1] + " IS NOT NULL"

		# the columns array position where group_by value is inserted
		ind = conditions["columns"].index(conditions["grbc"][0])

		# figure select column for the inner DISTINCT (unchanged)
		if filters.get("group_by") == "Item":
			sel_col = "t2.item_code"
		elif filters.get("group_by") == "Customer":
			sel_col = "t1.customer"
		elif filters.get("group_by") == "Supplier":
			sel_col = "t1.supplier"
		elif filters.get("group_by") == "Project":
			sel_col = "t1.project"
		elif filters.get("group_by") == "Territory":
			sel_col = "t1.territory"
		elif filters.get("group_by") == "Customer Group":
			sel_col = "t1.customer_group"
		elif filters.get("group_by") == "Item Group":
			sel_col = "t2.item_group"
		else:
			sel_col = conditions["group_by"]  # fallback

		# how many leading cols to skip when placing period/total values
		if filters.get("based_on") in ["Customer", "Supplier"]:
			inc = 3
		elif filters.get("based_on") in ["Item"]:
			inc = 2
		else:
			inc = 1

		# outer list by based_on_group
		data1 = frappe.db.sql(
			f"""
			select {query_details}
			from `tab{conditions['trans']}` t1, `tab{conditions['trans']} Item` t2 {conditions['addl_tables']}
			where t2.parent = t1.name
			  and t1.company = %(company)s
			  and t1.docstatus = 1
			  {conditions.get('addl_tables_relational_cond','')}
			  {cond}
			  {extra_cond}
			group by {conditions['group_by']}
			""",
			params,
			as_list=True,
		)

		for d in range(len(data1)):
			dt = list(data1[d])
			dt.insert(ind, "")  # blank column for group_by value
			data.append(dt)

			# distinct inner values for the requested group_by dimension under this based_on group
			row = frappe.db.sql(
			f"""
			select distinct({sel_col})
			from `tab{conditions['trans']}` t1, `tab{conditions['trans']} Item` t2 {conditions['addl_tables']}
			where t2.parent = t1.name
			and t1.company = %(company)s
			and t1.docstatus = 1
			{conditions.get('addl_tables_relational_cond','')}
			and {conditions['group_by']} = %(group_value)s
			and t1.posting_date between %(from_date)s and %(to_date)s
			{extra_cond}
			""",
			{
			**params,
			"group_value": data1[d][0],  # <- value for the based_on group you’re iterating
			},
			as_list=True,
			)

			for i in range(len(row)):
				des = ["" for _ in range(len(conditions["columns"]))]

				# pull metrics for this (based_on group, group_by item)
				row1 = frappe.db.sql(
				f"""
				select t4.default_currency as currency,
				{sel_col},
				{conditions['period_wise_select']}
				from `tab{conditions['trans']}` t1,
				`tab{conditions['trans']} Item` t2
				{conditions['addl_tables']}
				where t2.parent = t1.name
				and t1.company = %(company)s
				and t1.docstatus = 1
				and {sel_col} = %(sel_value)s
				and {conditions['group_by']} = %(group_value)s
				{conditions.get('addl_tables_relational_cond','')}
				and t1.posting_date between %(from_date)s and %(to_date)s
				{extra_cond}
				""",
				{
				**params,
				"sel_value": row[i][0],   # <- value from the distinct row
				"group_value": data1[d][0],
				},
				as_list=True,
				)

				des[ind] = row[i][0]                  # the group_by value
				des[ind - 1] = row1[0][0]            # currency

				# copy the numeric measures into the row in the same positions as original code
				for j in range(1, len(conditions["columns"]) - inc):
					des[j + inc] = row1[0][j]

				data.append(des)

	else:
		# non-group_by path: one row per based_on group
		query_details = conditions["based_on_select"] + conditions["period_wise_select"]
		cond = ""
		if conditions["based_on_select"] in ["t1.project,", "t2.project,"]:
			cond = " and " + conditions["based_on_select"][:-1] + " IS NOT NULL"

		data = frappe.db.sql(
			f"""
			select {query_details}
			from `tab{conditions['trans']}` t1, `tab{conditions['trans']} Item` t2 {conditions['addl_tables']}
			where t2.parent = t1.name
			  and t1.company = %(company)s
			  and t1.docstatus = 1
			  and t1.posting_date between %(from_date)s and %(to_date)s
			  {cond}
			  {conditions.get('addl_tables_relational_cond','')}
			  {extra_cond}
			group by {conditions['group_by']}
			""",
			params,
			as_list=True,
		)

	return data

# === Helpers copied from original, unchanged ===

def get_mon(dt):
	return getdate(dt).strftime("%b")

def based_wise_columns_query(based_on, trans):
	based_on_details = {}

	if based_on == "Item":
		based_on_details["based_on_cols"] = ["Item:Link/Item:120", "Item Name:Data:120"]
		based_on_details["based_on_select"] = "t2.item_code, t2.item_name,"
		based_on_details["based_on_group_by"] = "t2.item_code"
		based_on_details["addl_tables"] = ""
	elif based_on == "Item Group":
		based_on_details["based_on_cols"] = ["Item Group:Link/Item Group:120"]
		based_on_details["based_on_select"] = "t2.item_group,"
		based_on_details["based_on_group_by"] = "t2.item_group"
		based_on_details["addl_tables"] = ""
	elif based_on == "Customer":
		based_on_details["based_on_cols"] = ["Customer:Link/Customer:120","Customer Name:Data:120","Territory:Link/Territory:120"]
		based_on_details["based_on_select"] = "t1.customer, t1.customer_name, t1.territory,"
		based_on_details["based_on_group_by"] = "t1.customer"
		based_on_details["addl_tables"] = ""
	elif based_on == "Customer Group":
		based_on_details["based_on_cols"] = ["Customer Group:Link/Customer Group"]
		based_on_details["based_on_select"] = "t1.customer_group,"
		based_on_details["based_on_group_by"] = "t1.customer_group"
		based_on_details["addl_tables"] = ""
	elif based_on == "Territory":
		based_on_details["based_on_cols"] = ["Territory:Link/Territory:120"]
		based_on_details["based_on_select"] = "t1.territory,"
		based_on_details["based_on_group_by"] = "t1.territory"
		based_on_details["addl_tables"] = ""
	elif based_on == "Project":
		based_on_details["based_on_cols"] = ["Project:Link/Project:120"]
		based_on_details["based_on_select"] = "t1.project,"
		based_on_details["based_on_group_by"] = "t1.project"
		based_on_details["addl_tables"] = ""
	else:
		frappe.throw(_("Unsupported 'Based On' for this clone."))

	# currency join (unchanged)
	based_on_details["based_on_select"] += "t4.default_currency as currency,"
	based_on_details["based_on_cols"].append("Currency:Link/Currency:120")
	based_on_details["addl_tables"] += ", `tabCompany` t4"
	based_on_details["addl_tables_relational_cond"] = (
		based_on_details.get("addl_tables_relational_cond", "") + " and t1.company = t4.name"
	)

	return based_on_details

def group_wise_column(group_by):
	if group_by:
		return [group_by + ":Link/" + group_by + ":120"]
	else:
		return []