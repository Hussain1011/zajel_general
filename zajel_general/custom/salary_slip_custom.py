import frappe
from frappe.utils import flt, getdate

# You can change these to match your component names
ALLOWED_EARNINGS = {"Basic Salary", "Housing Allowance"}  # components you still pay during annual leave
ANNUAL_LEAVE_TYPE = "Annual Leave"                    # the exact Leave Type name
DEDUCTION_COMPONENT = "Annual Leave"        # make sure a Deduction-type Salary Component exists with this name


def apply_annual_leave_deduction(doc, method=None):
    # 1) Figure out annual leave days from Leave Details if present
    custom_annual_leave_days = 0.0
    for lr in (doc.get("leave_details") or []):
        if (lr.leave_type or "").strip().lower() == ANNUAL_LEAVE_TYPE.lower():
            custom_annual_leave_days += flt(lr.days)

    # 2) Fallback: if Leave Details is empty, pull from approved Leave Applications overlapping slip period
    if not custom_annual_leave_days:
        custom_annual_leave_days = get_custom_annual_leave_days_from_leave_applications(
            employee=doc.employee,
            start_date=doc.start_date,
            end_date=doc.end_date,
            leave_type=ANNUAL_LEAVE_TYPE,
        )

    # store for visibility (optional, add a custom field if you want)
    doc.custom_annual_leave_days = custom_annual_leave_days

    if custom_annual_leave_days <= 0:
        # no deduction needed; if an old row exists, you can zero it out
        zero_or_remove_deduction_row(doc)
        return

    # 3) Compute how much of earnings are allowed vs. not allowed
    total_earnings = sum(flt(e.amount) for e in (doc.get("earnings") or []))
    allowed_during_annual = sum(
        flt(e.amount)
        for e in (doc.get("earnings") or [])
        if (e.salary_component or "").strip().lower() in ALLOWED_EARNINGS
    )
    custom_non_allowed_monthly = total_earnings - allowed_during_annual
    if custom_non_allowed_monthly <= 0:
        zero_or_remove_deduction_row(doc)
        return

    # 4) Pro-rate by days (use payment_days first; fallback to total_working_days; else 30)
    denom = flt(doc.payment_days) or flt(doc.total_working_days) or 30.0
    daily_non_allowed = custom_non_allowed_monthly / denom if denom else 0.0
    amount = round(daily_non_allowed * custom_annual_leave_days, 2)

    # 5) Upsert the deduction row
    row = None
    for d in (doc.get("deductions") or []):
        if (d.salary_component or "").strip().lower() == DED_COMP.lower():
            row = d
            break

    if not row:
        row = doc.append("deductions", {})
        row.salary_component = DED_COMP

    row.amount = amount


def get_custom_annual_leave_days_from_leave_applications(employee, start_date, end_date, leave_type):
    """Sum overlapping days from approved Leave Applications within the slip period."""
    apps = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "leave_type": leave_type,
            "from_date": ("<=", end_date),
            "to_date": (">=", start_date),
        },
        fields=["from_date", "to_date", "total_leave_days", "half_day", "half_day_date"],
    )

    if not apps:
        return 0.0

    start = getdate(start_date)
    end = getdate(end_date)

    total = 0.0
    for a in apps:
        a_from = getdate(a.from_date)
        a_to = getdate(a.to_date)
        # overlap window
        o_start = max(start, a_from)
        o_end = min(end, a_to)
        if o_start > o_end:
            continue
        days = (o_end - o_start).days + 1

        # basic half-day handling (if half-day date lies in overlap)
        if a.get("half_day") and a.get("half_day_date"):
            hd = getdate(a.half_day_date)
            if o_start <= hd <= o_end:
                days -= 0.5

        total += days

    return total


def zero_or_remove_deduction_row(doc):
    """Optional helper to clear the deduction if no annual leave found."""
    for d in (doc.get("deductions") or []):
        if (d.salary_component or "").strip().lower() == DED_COMP.lower():
            d.amount = 0.0