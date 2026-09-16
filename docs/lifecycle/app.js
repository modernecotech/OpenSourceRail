import {setupEvidence} from './evidence.js';
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const services = await fetch('/api/workbench/services').then(r=>r.ok?r.json():null).catch(()=>null) || {erp:'http://127.0.0.1:8080',fuxa:'http://127.0.0.1:1881'};
let selected, snapshot, engineering, business, lastScope;
let refreshId=0;
let syncEvidence=()=>{};
let traceId=0;
const esc = text => String(text ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const timestamp = t => t ? new Date(t * 1000).toLocaleString() : 'No measurement received';
const record = text => `<div class="record">${text}</div>`;
for (const id of ['city','environment']) if (params.get(id)) {
  if (![...$(id).options].some(o=>o.value===params.get(id))) $(id).add(new Option(params.get(id),params.get(id)));
  $(id).value = params.get(id);
}
function query(extra = {}) {return new URLSearchParams({city:$('city').value,environment:$('environment').value,...extra});}
async function get(path) {const r=await fetch(path);if(!r.ok) throw new Error(`Service unavailable (${r.status})`);return r.json();}
function render() {
  selected=snapshot.assets.find(a=>a.asset_id===$('asset').value);
  for(const id of ['overview','measurements','alarms','links','engineering','execution','assurance','queue','commands','trend']) $(id).innerHTML='';
  $('commandForm').hidden=true;
  syncEvidence();
  if(!selected) { $('overview').textContent='No equipment deployed for this city and environment.';return; }
  const a=selected;
  const commandOptions=Object.keys(a.commands || {});
  const oldCommand=$('commandName').value;
  $('commandName').replaceChildren(...commandOptions.map(k=>new Option(k,k)));
  if(commandOptions.includes(oldCommand))$('commandName').value=oldCommand;
  $('commandForm').hidden=a.environment!=='simulation'||!commandOptions.length;
  setCommandRange();
  $('overview').innerHTML=[['Equipment',a.name],['OSR source crates',(a.source_crates || []).join(', ') || 'See engineering package'],['OSR identity',a.asset_id],['Engineering revision',a.engineering_revision],['Configuration state',a.lifecycle_state],['Physical serial',a.installations.find(i=>!i.removed)?.serial || 'Not installed']].map(([k,v])=>`<span><small>${esc(k)}</small><b>${esc(v)}</b></span>`).join('');
  $('measurements').innerHTML=Object.entries(a.readings).map(([key,r])=>`<article class="metric"><small>${esc(key)}</small><strong>${r.quality==='valid'?esc(r.value):'—'} <small>${esc(r.unit)}</small></strong><div class="quality ${r.quality==='valid'?'':'bad'}">${esc(r.quality)}</div><small>${esc(timestamp(r.source_time))}</small></article>`).join('');
  $('alarms').innerHTML=a.alarms.length?a.alarms.map(r=>record(`<b class="${r.active?'bad':''}">${esc(r.rule)} · ${r.active?'Active':'Condition clear'}</b><br>${r.case_id?`<a href="${esc(services.erp)}/app/issue/${encodeURIComponent(r.case_id)}" target="_blank" rel="noopener">ERP ${esc(r.case_id)}</a> · ${esc(r.erp_status)}`:r.occurrences?'Maintenance case not delivered':'No actionable fault'} · ${r.occurrences} occurrence(s)<br>Acknowledged: ${esc(r.acknowledged_by || 'No')}${!r.acknowledged_by && r.occurrences ? ` <button type="button" data-ack="${esc(r.rule)}">Acknowledge</button>` : ''}`)).join(''):'No alarm occurrences.';
  const links=[['FUXA supervision',services.fuxa+'/home/'],['ERP project',`${services.erp}/app/project/${encodeURIComponent(a.erp_project)}`],['City execution',`/docs/operating/?city=${encodeURIComponent(a.city)}`],['OSR assurance',`/docs/operations-portal/?city=${encodeURIComponent(a.city)}&asset=${encodeURIComponent(a.asset_id)}`]];
  if(a.erp_asset_id) links.push(['ERP Asset',`${services.erp}/app/asset/${encodeURIComponent(a.erp_asset_id)}`]);
  $('links').innerHTML=links.map(([label,url])=>`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`).join('');
  const engineeringApplies=engineering && [a.asset_id,a.parent_asset_id,...(a.source_asset_ids || [])].includes(engineering.asset_id);
  $('engineering').innerHTML=(engineeringApplies ? engineering.artifacts : null)?.map(r=>record(`<b>${esc(r.tool)}</b> · ${esc(r.tool_version)}<br><a href="/api/lifecycle/artifact?${esc(query({sha256:r.sha256}))}">${esc(r.path.split('/').pop())}</a><br><code>${esc(r.sha256.slice(0,24))}…</code>${r.ifc_objects?` · ${r.ifc_objects.length} IFC identities`:''}`)).join('') || 'No reviewed engineering package linked to this equipment position.';
  const execution=business?.snapshots?.find(s=>s.project===a.erp_project)?.execution;
  $('execution').innerHTML=execution?Object.entries(execution.by_currency).map(([currency,v])=>record(`${esc(currency)} · Ordered ${Number(v.ordered).toLocaleString()} · Unbilled commitment ${Number(v.unbilled_commitment).toLocaleString()} · Invoiced ${Number(v.invoiced).toLocaleString()}`)).join('')+record(`${execution.receipts.length} receipt lines · ${execution.production.length} production records. Installed and engineering-accepted quantities require OSR evidence.`):'Execution feedback not yet available.';
  $('assurance').innerHTML=a.evidence.map(r=>{let body;try{body=JSON.parse(r.body || '{}');}catch{body={};}return record(`<b>${esc(r.kind)}</b> · ${esc(r.actor)}<br><code>${esc(r.id)}</code> · ${esc(timestamp(r.created))}${body.result?` · ${esc(body.result)}`:''}<br>${(body.references || []).map(esc).join('<br>')}`);}).join('') || 'No installation or acceptance evidence recorded.';
  if(a.osr_assurance){const s=a.osr_assurance;$('assurance').innerHTML+=record(`Existing OSR records: ${s.work_orders.length} works · ${s.inspections.length} inspections · ${s.approvals.length} handback records · ${s.defects.length} defects. These are separate from simulation rehearsal evidence.`);}
  $('queue').innerHTML=snapshot.outbox.filter(r=>a.alarms.some(al=>al.incident===r.incident)).map(r=>record(`<b>${esc(r.state)}</b> · ${r.attempts} retries${r.error?`<br><span class="bad">${esc(r.error)}</span>`:''}`)).join('') || 'No queued maintenance events for this asset.';
  $('commands').innerHTML=a.commands_audit.map(r=>record(`<b>${esc(r.state)}</b> · ${esc(r.actor)}<br><code>${esc(r.id)}</code>${r.result?`<br>${esc(r.result)}`:''}`)).join('') || 'No supervisory requests.';
  const old=$('trendMeasurement').value; $('trendMeasurement').replaceChildren(...Object.keys(a.readings).map(k=>new Option(k,k)));if(old in a.readings)$('trendMeasurement').value=old;
  history.replaceState(null,'','?'+query({asset:a.asset_id}));
  if(parent!==window)parent.postMessage({type:'osr:context',context:{city:a.city,selected_asset:a.asset_id,environment:a.environment}},location.origin);
}
async function refresh() {
  const requestId=++refreshId;
  const scope=query().toString();
  if(lastScope!==scope){snapshot=null;selected=null;syncEvidence();traceId++;$('traceResults').replaceChildren();$('asset').replaceChildren();for(const id of ['overview','measurements','alarms','links','engineering','execution','assurance','queue','commands','trend'])$(id).innerHTML='';}
  lastScope=scope;
  $('connection').textContent='Refreshing…';$('mode').textContent=$('environment').value==='simulation'?'SIMULATION · Existing OSR controller model with explicit sensor fixtures. Cases are labelled simulation.':'PHYSICAL · Supplier bindings and OSR commissioning evidence are required.';
  try {
    const result=await Promise.all([get('/api/lifecycle/snapshot?'+query()),get('/api/lifecycle/engineering?'+query()).catch(()=>null),get('/api/operating/twins').catch(()=>null)]);
    if(requestId!==refreshId)return;
    [snapshot,engineering,business]=result;
    const old=$('asset').value||params.get('asset');$('asset').replaceChildren(...snapshot.assets.map(a=>new Option(a.asset_id+' · '+a.equipment_type,a.asset_id)));
    if(snapshot.assets.some(a=>a.asset_id===old))$('asset').value=old;
    $('connection').textContent='Connected · '+new Date().toLocaleTimeString();render();
  } catch(e) {
    if(requestId!==refreshId)return;
    $('connection').textContent=e.message;
    // Remove last-known values on transport loss; never show them as current.
    if(snapshot){for(const a of snapshot.assets)for(const r of Object.values(a.readings))r.quality='disconnected';render();}
  }
}
$('loadTrend').onclick=async()=>{
  if(!selected)return;
  try {const rows=await get('/api/lifecycle/history?'+query({asset_id:selected.asset_id,measurement:$('trendMeasurement').value}));
    const valid=rows.filter(r=>r.quality==='valid'&&Number.isFinite(r.value)).reverse();
    if(!valid.length){$('trend').textContent='No valid samples.';return;}
    const low=Math.min(...valid.map(r=>r.value)),high=Math.max(...valid.map(r=>r.value));
    const points=valid.map((r,i)=>`${10+i*580/Math.max(1,valid.length-1)},${135-(r.value-low)*120/Math.max(.01,high-low)}`).join(' ');
    $('trend').innerHTML=`<svg viewBox="0 0 600 150" role="img" aria-label="Valid measurement history"><polyline points="${points}" fill="none" stroke="#168477" stroke-width="2"/></svg><p class="muted">${valid.length} valid samples · ${low}–${high} ${esc(valid[0].unit)} · ${esc(timestamp(valid[0].source_time))} to ${esc(timestamp(valid.at(-1).source_time))}. Invalid and disconnected samples omitted.</p>`;
  }catch(e){$('trend').textContent=e.message;}
};
$('refresh').onclick=refresh;$('city').onchange=refresh;$('environment').onchange=refresh;$('asset').onchange=render;
refresh();setInterval(refresh,5000);

function setCommandRange(){
  const rule=selected?.commands?.[$('commandName').value];if(!rule)return;
  $('commandValue').min=rule.min;$('commandValue').max=rule.max;
}
$('commandName').onchange=setCommandRange;
$('forgetToken').onclick=()=>{$('operatorToken').value='';$('actionStatus').textContent='Credential forgotten.';};
async function action(endpoint,payload,token=$('operatorToken').value.trim()){if(!token)throw new Error('Enter your scoped integration credential.');
  const response=await fetch('/api/lifecycle/'+endpoint,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:JSON.stringify(payload)});
  const result=await response.json();if(!response.ok)throw new Error(result.error || 'Action failed');return result;
}
$('commandForm').onsubmit=async event=>{
  event.preventDefault();if(!selected)return;
  const rule=selected.commands[$('commandName').value],now=Date.now();
  const request={request_id:crypto.randomUUID(),city:selected.city,environment:selected.environment,asset_id:selected.asset_id,
    command:$('commandName').value,parameters:{[rule.parameter]:Number($('commandValue').value)},
    required_conditions:rule.required_conditions,created_at:new Date(now).toISOString(),expires_at:new Date(now+Math.min(rule.max_ttl_seconds,25)*1000).toISOString()};
  const button=event.submitter;button.disabled=true;$('actionStatus').textContent='Sending request…';
  try{const result=await action('commands',request);$('actionStatus').textContent=`${result.state}: ${result.reason || request.request_id}. Controller completion is shown in history.`;await refresh();}
  catch(error){$('actionStatus').textContent=error.message+' Check history before retrying.';}
  finally{button.disabled=false;}
};
$('alarms').onclick=async event=>{
  const rule=event.target.closest('[data-ack]')?.dataset.ack;if(!rule||!selected)return;
  try{await action('alarms/acknowledge',{city:selected.city,environment:selected.environment,asset_id:selected.asset_id,rule});$('actionStatus').textContent='Alarm acknowledged. Maintenance case and railway release are unchanged.';await refresh();}
  catch(error){$('actionStatus').textContent=error.message;}
};

try {syncEvidence=await setupEvidence({getSelected:()=>selected,send:action,refresh});}
catch(error){$('evidenceStatus').textContent=error.message;}
$('traceForm').onsubmit=async event=>{
  event.preventDefault();const id=++traceId;
  const serial=$('traceSerial').value.trim(),batch=$('traceBatch').value.trim();
  if(!serial&&!batch){$('traceResults').textContent='Enter a serial or batch.';return;}
  const scope=query().toString();$('traceResults').textContent='Searching this city and environment…';
  try{
    const rows=await get('/api/lifecycle/affected?'+query({...serial?{serial}:{},...batch?{batch}:{}}));
    if(id!==traceId||scope!==query().toString())return;
    $('traceResults').replaceChildren();
    for(const row of rows){
      const entry=document.createElement('div');entry.className='record';
      const asset=row.scope.split('|')[2];const button=document.createElement('button');button.type='button';button.textContent=asset;
      button.disabled=!snapshot?.assets.some(a=>a.asset_id===asset);
      button.onclick=()=>{$('asset').value=asset;render();};
      const detail=document.createElement('p');detail.textContent=`Serial ${row.serial} · Batch ${row.batch || 'none'} · ${row.removed?'Removed '+timestamp(row.removed):'Currently installed'} · revision ${row.revision || ''}`;
      entry.append(button,detail);$('traceResults').append(entry);
    }
    if(!rows.length)$('traceResults').textContent='No matching installations in this city and environment.';
  }catch(error){if(id===traceId)$('traceResults').textContent=error.message;}
};
