# Copyright (c) 2025, Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, now_datetime, getdate, nowdate
from frappe.model.document import Document


class CertificateRequest(Document):

    def validate(self):
        """
        Keep derived fields consistent whenever the doc is saved.
        """
        # Ensure default validity
        # if not self.validity_days:
        validity_days = 10
        
        """Auto-assign letterhead based on selected company in custom doctype"""

        # Skip if letter_head is already set manually
        if getattr(self, "letter_head", None):
            return

        # Ensure company exists
        if not getattr(self, "company", None):
            return

        # Fetch default letterhead for that company
        default_letterhead = frappe.db.get_value("Company", self.company, "default_letter_head")

        if default_letterhead:
            self.letter_head = default_letterhead
        else:
            frappe.logger().info(f"No default letterhead found for {self.company}")

        if self.status == "Approved":
            # Stamp approver/time once
            if not self.approved_on:
                self.approved_on = now_datetime()
            if not self.approved_by:
                self.approved_by = frappe.session.user

            # Compute validity window
            self.valid_till = add_days(self.approved_on, validity_days)

            # Still valid?
            self.show_signature = 1 if getdate(self.valid_till) >= getdate(nowdate()) else 0

        else:
            # Any non-approved status → hide signature
            self.show_signature = 0
            # (optional) clear stamps if not approved
            if self.status in ("Draft", "Pending CEO Approval", "Rejected"):
                self.approved_on = None
                self.approved_by = None
                self.valid_till = None