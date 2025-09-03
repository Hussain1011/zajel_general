// your_app/doctype/certificate_request/certificate_request.js
frappe.ui.form.on('Certificate Request', {
    refresh(frm) {
      // if (frm.doc.name && !frm.is_new()) {
      //   frm.add_custom_button(__('Print Certificate'), () => {
      //     const vt = frm.doc.valid_till;
      //     const valid = frm.doc.status === 'Approved'
      //       && vt
      //       && frappe.datetime.obj_to_str(vt) >= frappe.datetime.get_today();
  
      //     if (!valid) {
      //       frappe.msgprint(__('Approval is missing or expired. Please re-submit for approval.'));
      //       return;
      //     }
  
      //     // open print dialog (use a preferred print format if stored)
      //     const pf = frm.doc.print_format || null;
      //     frappe.ui.get_print_settings(false, print_settings => {
      //       frappe.print_doc(frm.doc.doctype, frm.doc.name, pf, print_settings.default_letter_head, print_settings);
      //     });
      //   });
      // }
    }
  });