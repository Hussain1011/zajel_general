frappe.listview_settings['Kitchen Order Ticket'] = {
    get_indicator: function(doc) {
        const colors = {
            "Pending": "orange",
            "Accepted": "blue",
            "Preparing": "purple",
            "Ready": "green",
            "Served": "gray",
            "Cancelled": "red"
        };
        return [doc.status, colors[doc.status] || "blue", "status,=," + doc.status];
    }
};