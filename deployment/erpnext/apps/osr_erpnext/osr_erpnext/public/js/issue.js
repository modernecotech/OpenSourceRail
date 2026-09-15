frappe.ui.form.on('Issue', {
  refresh(frm) {
    if (!frm.doc.custom_osr_city || !frm.doc.custom_osr_asset_id) return;
    frm.add_custom_button(__('Connected asset'), () => {
      const query = new URLSearchParams({city:frm.doc.custom_osr_city,asset:frm.doc.custom_osr_asset_id,environment:frm.doc.custom_osr_environment});
      window.open('http://127.0.0.1:8090/docs/lifecycle/?' + query, '_blank', 'noopener');
    }, __('OpenSourceRail'));
  },
});
