# your_app/tasks.py
import frappe
from frappe.utils import nowdate, getdate

def expire_old_signatures():
    rows = frappe.get_all(
        "Certificate Request",
        filters={"status": "Approved"},
        fields=["name", "valid_till"]
    )
    today = getdate(nowdate())
    for r in rows:
        if r.valid_till and getdate(r.valid_till) < today:
            doc = frappe.get_doc("Certificate Request", r.name)
            doc.show_signature = 0
            # (Optional) flip to “Rejected” or “Expired” if you add such state
            # doc.status = "Expired"
            doc.save(ignore_permissions=True)