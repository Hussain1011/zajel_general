import frappe
from frappe.utils import getdate, add_days
from frappe.utils import flt

@frappe.whitelist()
def get_entity_dashboard(company: str, date: str = None, pos_profile: str = None):
    """Return KPI + comparisons + chart datasets for a company and date."""
    if not company:
        frappe.throw("Company is required")

    d = getdate(date) if date else getdate()
    y = add_days(d, -1)

    # --- Helper: sales/tx/visitors from Sales Invoice ---
    def kpi_for(day):
        filters = {
            "docstatus": 1,
            "company": company,
            "posting_date": day,
        }
        if pos_profile:
            filters["pos_profile"] = pos_profile

        row = frappe.db.get_all(
            "Sales Invoice",
            filters=filters,
            fields=[
                "count(name) as tx",
                "sum(base_net_total) as net_sales",
                # if you use pax/cover on invoice, replace custom_cover with your fieldname
                "sum(IFNULL(cover, 0)) as visitors"
            ],
            limit=1
        )[0]

        return {
            "tx": flt(row.tx),
            "net_sales": flt(row.net_sales),
            "visitors": flt(row.visitors),
        }

    today_k = kpi_for(d)
    yday_k = kpi_for(y)

    def diff(a, b):
        change = flt(a) - flt(b)
        pct = (change / flt(b) * 100) if flt(b) else (100 if flt(a) else 0)
        return {"value": flt(a), "yday": flt(b), "change": change, "pct": pct}

    # --- Profit (simple GL-based daily profit/loss) ---
    # NOTE: This is the correct direction for GL:
    # Income increases on credit; Expense increases on debit.
    def profit_for(day):
        # Income
        income = frappe.db.sql("""
            SELECT SUM(credit - debit) AS v
            FROM `tabGL Entry`
            WHERE is_cancelled=0 AND company=%s AND posting_date=%s
              AND account IN (SELECT name FROM `tabAccount` WHERE company=%s AND root_type='Income')
        """, (company, day, company))[0][0] or 0

        # Expense
        expense = frappe.db.sql("""
            SELECT SUM(debit - credit) AS v
            FROM `tabGL Entry`
            WHERE is_cancelled=0 AND company=%s AND posting_date=%s
              AND account IN (SELECT name FROM `tabAccount` WHERE company=%s AND root_type='Expense')
        """, (company, day, company))[0][0] or 0

        return flt(income) - flt(expense)

    profit_today = profit_for(d)
    profit_yday = profit_for(y)
    profit_block = diff(profit_today, profit_yday)

    # --- Chart 1: Hourly net sales for selected day ---
    hourly = frappe.db.sql("""
        SELECT HOUR(posting_time) AS hr, SUM(base_net_total) AS amt
        FROM `tabSales Invoice`
        WHERE docstatus=1 AND company=%s AND posting_date=%s
        {pos_filter}
        GROUP BY HOUR(posting_time)
        ORDER BY hr
    """.format(pos_filter=("AND pos_profile=%s" if pos_profile else "")),
    tuple([company, d] + ([pos_profile] if pos_profile else [])), as_dict=1)

    hourly_labels = [f"{int(r.hr):02d}:00" for r in hourly]
    hourly_values = [flt(r.amt) for r in hourly]

    # --- Chart 2: Last 7 days net sales ---
    start = add_days(d, -6)
    daily = frappe.db.sql("""
        SELECT posting_date AS dt, SUM(base_net_total) AS amt
        FROM `tabSales Invoice`
        WHERE docstatus=1 AND company=%s AND posting_date BETWEEN %s AND %s
        {pos_filter}
        GROUP BY posting_date
        ORDER BY posting_date
    """.format(pos_filter=("AND pos_profile=%s" if pos_profile else "")),
    tuple([company, start, d] + ([pos_profile] if pos_profile else [])), as_dict=1)

    daily_labels = [str(r.dt) for r in daily]
    daily_values = [flt(r.amt) for r in daily]

    return {
        "kpis": {
            "sales": diff(today_k["net_sales"], yday_k["net_sales"]),
            "visitors": diff(today_k["visitors"], yday_k["visitors"]),
            "transactions": diff(today_k["tx"], yday_k["tx"]),
            "profit": profit_block,
        },
        "charts": {
            "hourly_sales": {"labels": hourly_labels, "values": hourly_values},
            "weekly_sales": {"labels": daily_labels, "values": daily_values},
        },
        "meta": {"date": str(d), "yesterday": str(y), "company": company}
    }