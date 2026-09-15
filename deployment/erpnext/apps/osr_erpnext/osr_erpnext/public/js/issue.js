frappe.ui.form.on('Issue', {
  refresh(frm) {
    if (!frm.doc.custom_osr_city || !frm.doc.custom_osr_asset_id) return;
    frm.add_custom_button(__('Connected asset'), () => {
      osr_open_lifecycle({city:frm.doc.custom_osr_city,selected_asset:frm.doc.custom_osr_asset_id,environment:frm.doc.custom_osr_environment});
    }, __('OpenSourceRail'));
  },
});
