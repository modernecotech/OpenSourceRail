frappe.ui.form.on('Task', {
  refresh(frm) {
    if (frm.is_new() || frm.doc.custom_osr_kind !== 'procurement') return;
    frm.add_custom_button(__('Material request'), () => {
      let requirements = [];
      let warehouses = [];
      let generation = 0;
      const escape = frappe.utils.escape_html;
      const preview = () => {
        const row = requirements.find(r => r.purchase_order_id === dialog.get_value('requirement_id'));
        dialog.fields_dict.preview.$wrapper.html(row ?
          `<p>${escape(row.description)} · ${escape(row.asset_id)}</p><p>Planning quantity: ${escape(String(row.quantity_basis))}. Enter the verified quantity in the Item's stock unit.</p>` : 'Search and select an OSR requirement.');
      };
      const search = async () => {
        const current = ++generation;
        const result = await frappe.call({type: 'GET', method: 'osr_erpnext.procurement.candidates',
          args: {task: frm.doc.name, search: dialog.get_value('search') || ''}});
        if (current !== generation) return;
        requirements = result.message.requirements;
        warehouses = result.message.warehouses;
        dialog.set_df_property('requirement_id', 'options', [''].concat(requirements.map(r => r.purchase_order_id)));
        dialog.set_value('requirement_id', '');
        dialog.set_df_property('search', 'description', `Showing ${requirements.length} of ${result.message.total}. Narrow by description, asset or requirement ID.`);
        preview();
      };
      const dialog = new frappe.ui.Dialog({title: __('Prepare material request'), fields: [
        {fieldname: 'search', label: __('Find requirement'), fieldtype: 'Data', onchange: search},
        {fieldname: 'requirement_id', label: __('Requirement'), fieldtype: 'Select', reqd: 1, options: [], onchange: preview},
        {fieldname: 'preview', fieldtype: 'HTML'},
        {fieldname: 'item_code', label: __('Purchasable Item'), fieldtype: 'Link', options: 'Item', reqd: 1,
          get_query: () => ({filters: {disabled: 0, is_purchase_item: 1}}),
          async onchange() {
            const code = dialog.get_value('item_code');
            dialog.set_value('stock_unit', '');
            if (!code) return;
            const result = await frappe.db.get_value('Item', code, 'stock_uom');
            if (dialog.get_value('item_code') === code) dialog.set_value('stock_unit', result.message.stock_uom);
          }},
        {fieldname: 'stock_unit', label: __('Stock unit'), fieldtype: 'Data', read_only: 1},
        {fieldname: 'quantity', label: __('Quantity in stock unit'), fieldtype: 'Float', reqd: 1},
        {fieldname: 'schedule_date', label: __('Required date'), fieldtype: 'Date', reqd: 1},
        {fieldname: 'warehouse', label: __('City warehouse'), fieldtype: 'Link', options: 'Warehouse', reqd: 1,
          get_query: () => ({filters: {name: ['in', warehouses], disabled: 0, is_group: 0}})},
      ], primary_action_label: __('Create draft'),
      async primary_action(values) {
        const {search: ignored, stock_unit: unit, ...mapping} = values;
        const result = await frappe.call({method: 'osr_erpnext.procurement.create_material_request',
          args: {task: frm.doc.name, ...mapping}, freeze: true});
        dialog.hide();
        frappe.set_route('Form', 'Material Request', result.message.name);
      }});
      dialog.show();
      search();
    }, __('OpenSourceRail'));
  },
});
