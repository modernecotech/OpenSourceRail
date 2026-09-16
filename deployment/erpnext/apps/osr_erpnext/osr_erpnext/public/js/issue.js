frappe.ui.form.on('Issue', {
  refresh(frm) {
    if (!frm.doc.custom_osr_city || !frm.doc.custom_osr_asset_id) return;
    frm.add_custom_button(__('Connected asset'), () => {
      osr_open_lifecycle({city:frm.doc.custom_osr_city,selected_asset:frm.doc.custom_osr_asset_id,environment:frm.doc.custom_osr_environment});
    }, __('OpenSourceRail'));
    if (!frm.doc.custom_osr_erp_asset || frm.is_new()) return;
    frappe.call({method:'osr_erpnext.integration.repairs_for_issue',args:{issue:frm.doc.name}}).then(response => {
      const repairs=response.message || [];
      if (repairs.length) {
        frm.add_custom_button(__('Open repair'), () => {
          if (repairs.length===1) frappe.set_route('Form','Asset Repair',repairs[0].name);
          else frappe.set_route('List','Asset Repair',{custom_osr_issue:frm.doc.name});
        }, __('OpenSourceRail'));
        return;
      }
      if (frappe.model.can_create('Asset Repair') && !['Closed','Resolved'].includes(frm.doc.status))
        frm.add_custom_button(__('Prepare repair'), () => osr_prepare_repair(frm), __('OpenSourceRail'));
    });
  },
});

function osr_prepare_repair(frm) {
  const dialog=new frappe.ui.Dialog({
    title:__('Review condition repair'),size:'large',
    fields:[
      {fieldname:'failure_date',label:__('Failure date'),fieldtype:'Datetime',reqd:1,default:frm.doc.creation},
      {fieldname:'expected_downtime_hours',label:__('Expected downtime (hours)'),fieldtype:'Float',reqd:1},
      {fieldname:'technician',label:__('Technician'),fieldtype:'Link',options:'User',reqd:1,
        get_query:() => ({filters:{enabled:1,user_type:'System User'}})},
      {fieldname:'description',label:__('Repair scope'),fieldtype:'Small Text',reqd:1,default:frm.doc.subject},
      {fieldname:'parts',label:__('Required parts'),fieldtype:'Table',cannot_add_rows:false,in_place_edit:true,fields:[
        {fieldname:'item',label:__('Item'),fieldtype:'Link',options:'Item',reqd:1,in_list_view:1,
          get_query:() => ({filters:{disabled:0,is_stock_item:1}})},
        {fieldname:'warehouse',label:__('Warehouse'),fieldtype:'Link',options:'Warehouse',reqd:1,in_list_view:1,
          get_query:() => ({filters:{disabled:0,is_group:0}})},
        {fieldname:'quantity',label:__('Quantity'),fieldtype:'Float',reqd:1,in_list_view:1},
        {fieldname:'serial_and_batch_bundle',label:__('Serial / batch bundle'),fieldtype:'Link',options:'Serial and Batch Bundle',in_list_view:1},
      ]},
      {fieldname:'evidence_references',label:__('Additional evidence references (one per line)'),fieldtype:'Small Text'},
    ],
    primary_action_label:__('Preview draft'),
    primary_action(values) {
      const proposal={schema:'osr-condition-repair/1',key:'primary',failure_date:values.failure_date,
        expected_downtime_hours:values.expected_downtime_hours,technician:values.technician,
        description:values.description,parts:(values.parts || []).map(row => ({item:row.item,
          warehouse:row.warehouse,quantity:row.quantity,
          ...(row.serial_and_batch_bundle ? {serial_and_batch_bundle:row.serial_and_batch_bundle} : {})})),
        evidence_references:(values.evidence_references || '').split('\n').map(row => row.trim()).filter(Boolean)};
      frappe.call({method:'osr_erpnext.integration.preview_repair',args:{issue:frm.doc.name,proposal}}).then(preview => {
        const plan=preview.message;
        const shortages=plan.availability.filter(row => row.shortage_qty>0);
        const warning=shortages.length ? '<br><b>'+__('Stock shortages:')+'</b> '+shortages.map(row =>
          `${frappe.utils.escape_html(row.item)} (${row.shortage_qty})`).join(', ') : '';
        frappe.confirm(__('Create an unsubmitted Asset Repair assigned to {0}? ERP completion will not grant railway handback.{1}',
          [frappe.utils.escape_html(values.technician),warning]), () => {
          frappe.call({method:'osr_erpnext.integration.apply_repair',args:{issue:frm.doc.name,
            proposal,fingerprint:plan.fingerprint},freeze:true,freeze_message:__('Creating repair…')}).then(created => {
            dialog.hide();
            frappe.set_route('Form','Asset Repair',created.message.name);
          });
        });
      });
    },
  });
  dialog.show();
}
