import frappe
from frappe.utils import flt

# You can change these to match your component names
ALLOWED_EARNINGS = {"Basic Salary", "Housing Allowance"}  # components you still pay during annual leave
ANNUAL_LEAVE_TYPE = "Annual Leave"                    # the exact Leave Type name
DEDUCTION_COMPONENT = "Annual Leave"        # make sure a Deduction-type Salary Component exists with this name

def apply_annual_leave_deduction(doc, method=None):
    """
    Called on Salary Slip before_save.
    - Computes custom_annual_leave_days (from Salary Slip Leave rows with 'Annual Leave')
    - Computes custom_non_allowed_monthly (sum of earnings excluding ALLOWED_EARNINGS)
    - Calculates deduction = custom_non_allowed_monthly * (custom_annual_leave_days / total_working_days)
    - Ensures a Deduction row 'Annual Leave Deduction' exists/updated with that amount
    - Writes helper fields back on the slip
    """

    # 0) Safety: nothing to do if totals are missing
    total_working_days = flt(getattr(doc, "total_working_days", 0))
    if total_working_days <= 0:
        _remove_annual_leave_deduction_row(doc)
        _write_helpers(doc, custom_annual_leave_days=0.0, custom_non_allowed_monthly=0.0)
        return

    # 1) Count Annual Leave days from the child table shown on Salary Slip
    #    (This table is populated when you create the slip; no DB query needed.)
    custom_annual_leave_days = 0.0
    for lr in (doc.get("leave_details") or []):
        if (lr.leave_type or "").strip() == ANNUAL_LEAVE_TYPE:
            custom_annual_leave_days += flt(lr.days)

    # If no annual leave, remove the deduction row and reset helpers
    if custom_annual_leave_days <= 0:
        _remove_annual_leave_deduction_row(doc)
        _write_helpers(doc, custom_annual_leave_days=0.0, custom_non_allowed_monthly=0.0)
        return
    
    if not custom_annual_leave_days:
    # fallback: compute from approved Leave Applications
        apps = frappe.get_all(
            "Leave Application",
            filters={
                "employee": doc.employee,
                "status": "Approved",
                "leave_type": ANNUAL_LEAVE_TYPE,
                "from_date": ("<=", doc.end_date),
                "to_date": (">=", doc.start_date),
            },
        fields=["from_date","to_date","total_leave_days"]
        )
        # You can do overlap math; simplest is sum total_leave_days of overlaps
        for a in apps:
            custom_annual_leave_days += flt(a.total_leave_days)
        doc.custom_annual_leave_days = custom_annual_leave_days
    # 2) Sum earnings that are NOT allowed during Annual Leave
    custom_non_allowed_monthly = 0.0
    for er in (doc.get("earnings") or []):
        comp = (er.salary_component or "").strip()
        if comp and comp not in ALLOWED_EARNINGS:
            custom_non_allowed_monthly += flt(er.amount)

    # If nothing to deduct, clean up and exit
    if custom_non_allowed_monthly <= 0:
        _remove_annual_leave_deduction_row(doc)
        _write_helpers(doc, custom_annual_leave_days=custom_annual_leave_days, custom_non_allowed_monthly=0.0)
        return

    # 3) Pro-rate the deduction by the fraction of annual-leave days
    ratio = custom_annual_leave_days / total_working_days
    deduction_amount = flt(custom_non_allowed_monthly * ratio, 2)

    # 4) Ensure the deduction row exists / is updated
    _upsert_annual_leave_deduction_row(doc, deduction_amount)

    # 5) Persist helper fields on the slip (custom fields we add via patch below)
    _write_helpers(doc, custom_annual_leave_days=custom_annual_leave_days, custom_non_allowed_monthly=custom_non_allowed_monthly)


def _write_helpers(doc, *, custom_annual_leave_days=0.0, custom_non_allowed_monthly=0.0):
    # These are custom fields we’ll add via patch
    doc.custom_annual_leave_days = flt(custom_annual_leave_days)
    doc.custom_non_allowed_monthly = flt(custom_non_allowed_monthly)


def _find_deduction_row(doc):
    for row in (doc.get("deductions") or []):
        if (row.salary_component or "").strip() == DEDUCTION_COMPONENT:
            return row
    return None


def _upsert_annual_leave_deduction_row(doc, amount):
    row = _find_deduction_row(doc)
    if row:
        row.amount = flt(amount, 2)
        row.description = "Auto: Annual Leave pro-rata of non-allowed earnings"
    else:
        doc.append("deductions", {
            "salary_component": DEDUCTION_COMPONENT,
            "amount": flt(amount, 2),
            "description": "Auto: Annual Leave pro-rata of non-allowed earnings",
        })


def _remove_annual_leave_deduction_row(doc):
    rows = doc.get("deductions") or []
    keep = []
    for r in rows:
        if (r.salary_component or "").strip() != DEDUCTION_COMPONENT:
            keep.append(r)
    doc.set("deductions", keep)