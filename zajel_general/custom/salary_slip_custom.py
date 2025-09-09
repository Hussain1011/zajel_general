import frappe
from frappe.utils import flt, getdate

# 1) Keep these exactly as your *labels*, but we normalize to lower-case once.
ALLOWED_EARNINGS = {s.lower() for s in ["Basic Salary", "Housing Allowance", "Sales Commission", "Arrear", "Reimbursement", "Advance Salary Paid", "Overtime", "Sales Tips", "Bonus", "Leave Encashment"]}   # fully paid during annual leave
ANNUAL_LEAVE_TYPE = "Annual Leave"                                              # exact Leave Type name
DEDUCTION_COMPONENT = "Annual Leave"                                            # existing Deduction-type Salary Component

def apply_annual_leave_deduction(doc, method=None):
    # --- 1) Annual leave days from Leave Details, if present -----------------
    custom_annual_leave_days = 0.0
    for lr in (doc.get("leave_details") or []):
        if (lr.leave_type or "").strip().lower() == ANNUAL_LEAVE_TYPE.lower():
            custom_annual_leave_days += flt(lr.days)

    # --- 2) Fallback to Leave Applications overlap ---------------------------
    if not custom_annual_leave_days:
        custom_annual_leave_days = get_custom_annual_leave_days_from_leave_applications(
            employee=doc.employee,
            start_date=doc.start_date,
            end_date=doc.end_date,
            leave_type=ANNUAL_LEAVE_TYPE,
        )

    # Optional: store for visibility only if field exists
    if hasattr(doc, "custom_annual_leave_days"):
        doc.custom_annual_leave_days = custom_annual_leave_days

    if custom_annual_leave_days <= 0:
        zero_or_remove_deduction_row(doc)
        return

    # --- 3) Sum earnings NOT paid during annual leave ------------------------
    total_earnings = sum(flt(e.amount) for e in (doc.get("earnings") or []))

    allowed_during_annual = 0.0
    for e in (doc.get("earnings") or []):
        comp_name = (e.salary_component or "").strip().lower()
        if comp_name in ALLOWED_EARNINGS:
            allowed_during_annual += flt(e.amount)

    non_allowed_monthly = total_earnings - allowed_during_annual
    if non_allowed_monthly <= 0:
        zero_or_remove_deduction_row(doc)
        return

    # --- 4) Pro-rate by days (prefer payment_days, fallback to total_working_days, else 30) ---
    denom = flt(getattr(doc, "payment_days", 0)) or flt(getattr(doc, "total_working_days", 0)) or 30.0
    daily_non_allowed = non_allowed_monthly / denom if denom else 0.0
    amount = round(daily_non_allowed * custom_annual_leave_days, 2)

    # --- 5) Upsert the deduction row ----------------------------------------
    target = DEDUCTION_COMPONENT.strip().lower()
    row = None
    for d in (doc.get("deductions") or []):
        if (d.salary_component or "").strip().lower() == target:
            row = d
            break

    if not row:
        row = doc.append("deductions", {"salary_component": DEDUCTION_COMPONENT})

    row.amount = amount


def get_custom_annual_leave_days_from_leave_applications(employee, start_date, end_date, leave_type):
    """Sum overlapping days from Approved Leave Applications within the slip period."""
    apps = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "leave_type": leave_type,
            "from_date": ("<=", end_date),
            "to_date": (">=", start_date),
        },
        fields=["from_date", "to_date", "half_day", "half_day_date"],
    )

    if not apps:
        return 0.0

    start = getdate(start_date)
    end = getdate(end_date)

    total = 0.0
    for a in apps:
        a_from = getdate(a.from_date)
        a_to = getdate(a.to_date)
        o_start = max(start, a_from)
        o_end = min(end, a_to)
        if o_start > o_end:
            continue

        days = (o_end - o_start).days + 1
        # half-day handling if it falls within the overlap window
        if a.get("half_day") and a.get("half_day_date"):
            hd = getdate(a.half_day_date)
            if o_start <= hd <= o_end:
                days -= 0.5

        total += days

    return float(total)


def zero_or_remove_deduction_row(doc):
    """If deduction row exists for our component, zero it (or remove if you prefer)."""
    target = DEDUCTION_COMPONENT.strip().lower()
    for d in (doc.get("deductions") or []):
        if (d.salary_component or "").strip().lower() == target:
            d.amount = 0.0