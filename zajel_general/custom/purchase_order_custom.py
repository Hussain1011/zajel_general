import frappe

def validate(self, method):
            
    for item in self.items:
        if not item.material_request:
            frappe.throw("Material Request is mandatory for creating Purchase Order")