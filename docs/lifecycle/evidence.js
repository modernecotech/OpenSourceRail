export async function setupEvidence({getSelected, send, refresh}) {
  const $=id=>document.getElementById(id);
  const response=await fetch('/docs/lifecycle/evidence-types.json');
  if(!response.ok) throw new Error('Evidence catalogue unavailable');
  const catalogue=(await response.json()).types;
  let pending=null, target='';
  $('evidenceKind').replaceChildren(...catalogue.map(t=>new Option(t.label,t.id)));
  function clearPreview(){pending=null;$('evidenceReview').hidden=true;$('saveEvidence').disabled=false;}
  function fields(){
    clearPreview();const type=catalogue.find(t=>t.id===$('evidenceKind').value);
    $('evidenceAuthority').textContent=`Required credential role: ${type.role}. The gateway checks prerequisites and city/environment scope.`;
    $('evidenceFields').replaceChildren();
    for(const field of type.fields){
      const label=document.createElement('label');label.textContent=field.label;
      const input=document.createElement(field.options?'select':'input');
      if(field.options)input.replaceChildren(...field.options.map(v=>new Option(v,v)));
      else {input.type='text';input.maxLength=160;}
      input.name=field.name;input.required=Boolean(field.required);label.append(input);$('evidenceFields').append(label);
    }
  }
  function sync(){
    const a=getSelected();const scope=a ? `${a.city}|${a.environment}|${a.asset_id}|${a.engineering_revision}` : '';
    if(scope!==target){target=scope;clearPreview();$('evidenceToken').value='';$('evidenceReferences').value='';$('evidenceStatus').textContent='';fields();}
    const type=catalogue.find(t=>t.id===$('evidenceKind').value);
    $('previewEvidence').disabled=!a||(type.simulation_only && a.environment!=='simulation');
    $('evidenceTarget').textContent=a?`${a.city} / ${a.environment} / ${a.asset_id} / ${a.engineering_revision}`:'Select a connected asset.';
  }
  $('evidenceKind').onchange=()=>{fields();sync();};
  $('evidenceForm').oninput=clearPreview;
  $('forgetEvidenceToken').onclick=()=>{$('evidenceToken').value='';};
  $('evidenceForm').onsubmit=event=>{
    event.preventDefault();sync();const a=getSelected();if(!a||$('previewEvidence').disabled)return;
    const references=$('evidenceReferences').value.split('\n').map(r=>r.trim()).filter(Boolean);
    if(!references.length){$('evidenceStatus').textContent='Provide at least one versioned evidence reference.';return;}
    pending={id:crypto.randomUUID(),city:a.city,environment:a.environment,asset_id:a.asset_id,engineering_revision:a.engineering_revision,kind:$('evidenceKind').value,references};
    for(const input of $('evidenceFields').querySelectorAll('[name]'))if(input.value.trim())pending[input.name]=input.value.trim();
    $('evidencePayload').textContent=JSON.stringify(pending,null,2);$('evidenceReview').hidden=false;
    $('evidenceStatus').textContent='Review the exact asset, revision and references before recording.';
  };
  $('saveEvidence').onclick=async()=>{
    sync();if(!pending)return;
    const payload=pending;$('saveEvidence').disabled=true;
    try{
      const result=await send('evidence',payload,$('evidenceToken').value.trim());
      if(pending===payload){clearPreview();$('evidenceToken').value='';$('evidenceStatus').textContent=`Evidence ${result.id} ${result.created?'recorded':'already recorded'}.`;}
      await refresh();
    }catch(error){if(pending===payload)$('evidenceStatus').textContent=error.message+' Retry this reviewed record to reuse the same evidence ID.';}
    finally{$('saveEvidence').disabled=false;}
  };
  fields();sync();return sync;
}
