frappe.ui.form.on("Salary Structure", {
	refresh: function(frm) {
        // alert(frappe.db.get_value("User",{"name":frappe.session.user},"name"))
        console.log(frappe.user_roles.includes("System Manager"))
        if(frm.doc.docstatus === 1 && frappe.user_roles.includes("System Manager")) {
            frm.add_custom_button(__("Update to Draft"), function() {
                frm.trigger('update_draft');
            });
        }
    },

	update_draft: function(frm) {
		frappe.call({
			method: "zajel_general.custom.salary_structure_custom.update_draft",
			args: {
				salary_structure: frm.doc.name
			},
			callback: function(r) {
				frm.refresh();
                window.location.reload();
			}
		});
	},

});