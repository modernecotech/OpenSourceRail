// Runs inside authenticated ERP Desk, including its Workbench iframe.
window.osr_revision_dispositions = async function(frm) {
  const method = 'osr_erpnext.disposition.';
  const call = async (name, args, type='POST') => (await frappe.call({method:method+name,args,type,freeze:true})).message;
  const escape = frappe.utils.escape_html;
  const data = await call('catalogue',{project:frm.doc.name},'GET');
  const panel = new frappe.ui.Dialog({title:__('Revision dispositions'),size:'extra-large',fields:[
    {fieldname:'records',fieldtype:'HTML'},
  ]});
  const container=panel.fields_dict.records.$wrapper;
  container.append($('<p>').text('Record a proposed action and independent review. Native orders, stock and railway release remain separate.'));
  if(data.can_propose) $('<button class="btn btn-primary">').text('Propose disposition').appendTo(container).on('click',propose);
  for(const row of data.dispositions) {
    const box=$('<div class="well">').appendTo(container);
    $('<p>').text(`${row.proposal.action} · ${row.proposal.target.document} · ${row.responsible} · due ${row.due_date}`).appendTo(box);
    $('<p>').text(`${row.decision?.outcome || 'Awaiting independent review'} · ${row.current?'Exposure current':'Exposure changed or unavailable'} · execution unverified`).appendTo(box);
    $('<p>').text(row.proposal.rationale).appendTo(box);
    $('<button class="btn btn-default btn-xs">').text('Open proposal').appendTo(box).on('click',()=>{panel.hide();frappe.set_route('Form','OSR Revision Disposition',row.name);});
    if(!row.decision && data.can_review) $('<button class="btn btn-default btn-xs">').text('Review plan').appendTo(box).on('click',()=>review(row));
  }
  if(!data.dispositions.length) $('<p>').text('No recorded disposition plans for this project.').appendTo(container);
  show(panel);

  function propose() {
    if(!data.reviews.some(r=>r.targets.length)) {frappe.msgprint('No visible mapped business records. Prepare a reviewed Item/BOM mapping and ERP exposure first.');return;}
    const key=crypto.randomUUID();
    const dialog=new frappe.ui.Dialog({title:__('Propose revision disposition'),size:'large',fields:[
      {fieldname:'mapping',label:'Engineering mapping',fieldtype:'Select',reqd:1,
        options:[{value:'',label:''},...data.reviews.filter(r=>r.targets.length).map(r=>({value:r.mapping.name,label:`${r.mapping.component_type_id} · ${r.mapping.engineering_revision}`}))],onchange:()=>{
          const selected=data.reviews.find(r=>r.mapping.name===dialog.get_value('mapping'));
          dialog.set_df_property('target','options',[{value:'',label:''},...(selected?.targets || []).map(r=>({value:JSON.stringify(r.target),label:`${r.target.kind} · ${r.target.document}${r.target.line?' · '+r.target.line:''}`}))]);
          dialog.set_value('target','');dialog.set_value('action','');
        }},
      {fieldname:'target',label:'Affected record',fieldtype:'Select',reqd:1,options:[''],onchange:()=>{
        const value=dialog.get_value('target');
        dialog.set_df_property('action','options',value?data.actions[JSON.parse(value).kind]:['']);
      }},
      {fieldname:'action',label:'Requested action',fieldtype:'Select',reqd:1,options:['']},
      {fieldname:'responsible',label:'Responsible person',fieldtype:'Link',options:'User',reqd:1,
        get_query:()=>({filters:{enabled:1,user_type:'System User'}})},
      {fieldname:'due_date',label:'Review due date',fieldtype:'Date',reqd:1},
      {fieldname:'rationale',label:'Reason and proposed handling',fieldtype:'Small Text',reqd:1},
      {fieldname:'references',label:'Versioned evidence references (one per line)',fieldtype:'Small Text',reqd:1},
    ],primary_action_label:'Preview proposal',async primary_action(values) {
      const proposal={...values,key,target:JSON.parse(values.target),references:references(values.references)};
      const args={project:frm.doc.name,proposal};
      const plan=await call('preview',args);
      const confirm=new frappe.ui.Dialog({title:'Review proposal before recording',size:'large',fields:[
        {fieldtype:'HTML',options:`<p>${escape(plan.proposal.action)} · ${escape(plan.proposal.target.document)} · ${escape(plan.proposal.responsible)}</p><p>Exposure: <code>${escape(plan.exposure_sha256)}</code></p><p>${plan.warnings.map(escape).join('<br>')}</p><pre>${escape(JSON.stringify(plan.target_record,null,2))}</pre><p>This records a plan and assignment. It does not execute the requested action.</p>`},
      ],primary_action_label:'Record proposal',async primary_action(){
        await call('record',{...args,fingerprint:plan.fingerprint});confirm.hide();dialog.hide();panel.hide();window.osr_revision_dispositions(frm);
      }});show(confirm);
    }});show(dialog);
  }
  function review(row) {
    const dialog=new frappe.ui.Dialog({title:'Independent disposition review',size:'large',fields:[
      {fieldtype:'HTML',options:`<p>${escape(row.proposal.action)} · ${escape(row.proposal.target.document)}</p><p>${escape(row.proposal.rationale)}</p><pre>${escape(JSON.stringify(row.proposal,null,2))}</pre>`},
      {fieldname:'outcome',label:'Decision',fieldtype:'Select',options:['Reject plan','Endorse plan'],reqd:1},
      {fieldname:'rationale',label:'Review rationale',fieldtype:'Small Text',reqd:1},
      {fieldname:'references',label:'Review evidence references (one per line)',fieldtype:'Small Text',reqd:1},
    ],primary_action_label:'Preview decision',async primary_action(values){
      const decision={...values,references:references(values.references)},args={disposition:row.name,decision};
      const plan=await call('preview_decision',args);
      const confirm=new frappe.ui.Dialog({title:'Record independent decision',fields:[
        {fieldtype:'HTML',options:`<p>${escape(plan.decision.outcome)} · ${escape(plan.reviewer)}</p><p>Current exposure: <code>${escape(plan.current_exposure_sha256 || 'unavailable')}</code></p><p>Originally reviewed record:</p><pre>${escape(JSON.stringify(plan.original_target,null,2))}</pre><p>A plan endorsement does not verify execution or authorise railway release.</p>`},
      ],primary_action_label:'Record decision',async primary_action(){
        await call('record_decision',{...args,fingerprint:plan.fingerprint});confirm.hide();dialog.hide();panel.hide();window.osr_revision_dispositions(frm);
      }});show(confirm);
    }});show(dialog);
  }
  function show(dialog){
    dialog.$wrapper.find('.modal-body').css({maxHeight:'calc(100vh - 190px)',overflowY:'auto'});
    dialog.show();
  }
  function references(value){return value.split('\n').map(r=>r.trim()).filter(Boolean);}
};
