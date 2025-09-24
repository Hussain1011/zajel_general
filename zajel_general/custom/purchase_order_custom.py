import frappe
from frappe import _

def validate(doc, method):
    """Restrict UOM to only those defined in Item UOM Conversion."""
    for row in doc.items:
        # Get allowed UOMs for the Item
        allowed_uoms = [
            d.uom for d in frappe.get_all(
                "UOM Conversion Detail", 
                filters={"parent": row.item_code}, 
                fields=["uom"]
            )
        ]

        # If UOM list exists and selected UOM not in it → block
        if allowed_uoms and row.uom not in allowed_uoms:
            frappe.throw(_(
                "UOM <b>{0}</b> is not allowed for Item <b>{1}</b>. Allowed: {2}"
            ).format(row.uom, row.item_code, ", ".join(allowed_uoms)))

        
        allowed_suppliers = frappe.get_all(
            "Item Supplier",
            filters={"parent": row.item_code},
            pluck="supplier"
        )

        # if no suppliers are set, allow all
        if allowed_suppliers and doc.supplier not in allowed_suppliers:
            frappe.throw(
                _("Row #{0}: Supplier {1} is not allowed for Item {2}. Allowed suppliers: {3}").format(
                    row.idx, doc.supplier, row.item_code, ", ".join(allowed_suppliers)
                )
            )
        
        stock_uom = frappe.db.get_value("Item", row.item_code, "stock_uom")
        if stock_uom and row.stock_uom != stock_uom:
            row.stock_uom = stock_uom

        # Always refresh conversion_factor
        if row.uom:
            conversion_factor = frappe.db.get_value(
                "UOM Conversion Detail",
                {"parent": row.item_code, "uom": row.uom},
                "conversion_factor"
            )
            if not conversion_factor:
                # fallback: if UOM is same as stock_uom, factor=1
                if row.uom == stock_uom:
                    conversion_factor = 1
                else:
                    frappe.throw(
                        _("Row #{0}: UOM {1} not valid for Item {2}")
                        .format(row.idx, row.uom, row.item_code)
                    )

            row.conversion_factor = conversion_factor