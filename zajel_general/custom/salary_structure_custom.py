# Copyright (c) 2015, Lucrumerp Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def update_draft(salary_structure):
    if salary_structure:
        frappe.db.sql(f""" update `tabSalary Structure` set docstatus = 0 where name = '{salary_structure}' and docstatus = 1 """)
        frappe.db.sql(f""" update `tabSalary Detail` set docstatus = 0 where parent = '{salary_structure}' and docstatus = 1 """)
        
