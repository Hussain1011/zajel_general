# custom_profit_and_loss.py

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data, parent_totals = get_data(filters)
    
    for row in data:
        parent = row.get("parent_account")
        amount = row.get("net_amount")
        if parent and parent_totals.get(parent):
            ratio = (amount / parent_totals[parent]) * 100
            row["ratio"] = f"{ratio:.2f}%"
        else:
            row["ratio"] = ""

    result = []
    for row in data:
        result.append([
            row["account"],
            row["debit"],
            row["credit"],
            row["net_amount"],
            row["ratio"]
        ])

    return columns, result


def get_columns():
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Data", "width": 250},
        {"label": _("Debit"), "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": _("Credit"), "fieldname": "credit", "fieldtype": "Currency", "width": 120},
        {"label": _("Net Amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("% of Parent"), "fieldname": "ratio", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    accounts = frappe.db.sql('''
        SELECT 
            account.name as account,
            account.parent_account,
            SUM(gl.debit) as debit,
            SUM(gl.credit) as credit,
            SUM(gl.debit - gl.credit) as net_amount
        FROM
            `tabGL Entry` gl
        JOIN
            `tabAccount` account ON account.name = gl.account
        WHERE
            gl.docstatus = 1 AND account.report_type IN ('Profit and Loss')
        GROUP BY
            account.name
    ''', as_dict=1)

    parent_totals = {}
    for row in accounts:
        parent = row.get("parent_account")
        parent_totals[parent] = parent_totals.get(parent, 0) + row["net_amount"]

    return accounts, parent_totals