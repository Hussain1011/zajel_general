# Copyright (c) 2025, Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class KitchenOrderTicket(Document):
	def validate(self):
		if not self.items or len(self.items) == 0:
			frappe.throw("KOT must have at least one item")
