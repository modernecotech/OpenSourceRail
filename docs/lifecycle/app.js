const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
let selected, snapshot, engineering, business, lastScope;
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
  if(!selected) { $('overview').textContent='No equipment deployed for this city and environment.';return; }
  const a=selected;
  $('overview').innerHTML=[['Equipment',a.name],['OSR identity',a.asset_id],['Engineering revision',a.engineering_revision],['Configuration state',a.lifecycle_state],['Physical serial',a.installations.find(i=>!i.removed)?.serial || 'Not installed']].map(([k,v])=>`<span><small>${esc(k)}</small><b>${esc(v)}</b></span>`).join('');
  $('measurements').innerHTML=Object.entries(a.readings).map(([key,r])=>`<article class="metric"><small>${esc(key)}</small><strong>${r.quality==='valid'?esc(r.value):'—'} <small>${esc(r.unit)}</small></strong><div class="quality ${r.quality==='valid'?'':'bad'}">${esc(r.quality)}</div><small>${esc(timestamp(r.source_time))}</small></article>`).join('');
  $('alarms').innerHTML=a.alarms.length?a.alarms.map(r=>record(`<b class="${r.active?'bad':''}">${esc(r.rule)} · ${r.active?'Active':'Condition clear'}</b><br>${r.case_id?`<a href="http://127.0.0.1:8080/app/issue/${encodeURIComponent(r.case_id)}" target="_blank" rel="noopener">ERP ${esc(r.case_id)}</a> · ${esc(r.erp_status)}`:r.occurrences?'Maintenance case not delivered':'No actionable fault'} · ${r.occurrences} occurrence(s)<br>Acknowledged: ${esc(r.acknowledged_by || 'No')}`)).join(''):'No alarm occurrences.';
  const links=[['FUXA supervision','http://127.0.0.1:1881/home'],['ERP project',`http://127.0.0.1:8080/app/project/${encodeURIComponent(a.erp_project)}`],['City execution',`/docs/operating/?city=${encodeURIComponent(a.city)}`],['OSR assurance',`/docs/operations-portal/?city=${encodeURIComponent(a.city)}&asset=${encodeURIComponent(a.asset_id)}`]];
  if(a.erp_asset_id) links.push(['ERP Asset',`http://127.0.0.1:8080/app/asset/${encodeURIComponent(a.erp_asset_id)}`]);
  $('links').innerHTML=links.map(([label,url])=>`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`).join('');
  $('engineering').innerHTML=engineering?.artifacts?.map(r=>record(`<b>${esc(r.tool)}</b> · ${esc(r.tool_version)}<br><a href="/api/lifecycle/artifact?${esc(query({sha256:r.sha256}))}">${esc(r.path.split('/').pop())}</a><br><code>${esc(r.sha256.slice(0,24))}…</code>${r.ifc_objects?` · ${r.ifc_objects.length} IFC identities`:''}`)).join('') || 'Engineering package not linked for this city.';
  const execution=business?.snapshots?.find(s=>s.project===a.erp_project)?.execution;
  $('execution').innerHTML=execution?Object.entries(execution.by_currency).map(([currency,v])=>record(`${esc(currency)} · Ordered ${Number(v.ordered).toLocaleString()} · Unbilled commitment ${Number(v.unbilled_commitment).toLocaleString()} · Invoiced ${Number(v.invoiced).toLocaleString()}`)).join('')+record(`${execution.receipts.length} receipt lines · ${execution.production.length} production records. Installed and engineering-accepted quantities require OSR evidence.`):'Execution feedback not yet available.';
  $('assurance').innerHTML=a.evidence.map(r=>record(`<b>${esc(r.kind)}</b> · ${esc(r.actor)}<br>${esc(timestamp(r.created))}`)).join('') || 'No installation or acceptance evidence recorded.';
  if(a.osr_assurance){const s=a.osr_assurance;$('assurance').innerHTML+=record(`Existing OSR records: ${s.work_orders.length} works · ${s.inspections.length} inspections · ${s.approvals.length} handback records · ${s.defects.length} defects. These are separate from simulation rehearsal evidence.`);}
  $('queue').innerHTML=snapshot.outbox.filter(r=>a.alarms.some(al=>al.incident===r.incident)).map(r=>record(`<b>${esc(r.state)}</b> · ${r.attempts} retries${r.error?`<br><span class="bad">${esc(r.error)}</span>`:''}`)).join('') || 'No queued maintenance events for this asset.';
  $('commands').innerHTML=a.commands_audit.map(r=>record(`<b>${esc(r.state)}</b> · ${esc(r.actor)}<br>${esc(r.result || r.id)}`)).join('') || 'No supervisory requests.';
  const old=$('trendMeasurement').value; $('trendMeasurement').replaceChildren(...Object.keys(a.readings).map(k=>new Option(k,k)));if(old in a.readings)$('trendMeasurement').value=old;
  history.replaceState(null,'','?'+query({asset:a.asset_id}));
}
async function refresh() {
  const scope=query().toString();
  if(lastScope!==scope){snapshot=null;selected=null;$('asset').replaceChildren();for(const id of ['overview','measurements','alarms','links','engineering','execution','assurance','queue','commands','trend'])$(id).innerHTML='';}
  lastScope=scope;
  $('connection').textContent='Refreshing…';$('mode').textContent=$('environment').value==='simulation'?'SIMULATION · Existing OSR controller model with explicit sensor fixtures. Cases are labelled simulation.':'PHYSICAL · Supplier bindings and OSR commissioning evidence are required.';
  try {
    [snapshot,engineering,business]=await Promise.all([get('/api/lifecycle/snapshot?'+query()),get('/api/lifecycle/engineering?'+query()).catch(()=>null),get('/api/operating/twins').catch(()=>null)]);
    const old=$('asset').value||params.get('asset');$('asset').replaceChildren(...snapshot.assets.map(a=>new Option(a.asset_id+' · '+a.equipment_type,a.asset_id)));
    if(snapshot.assets.some(a=>a.asset_id===old))$('asset').value=old;
    $('connection').textContent='Connected · '+new Date().toLocaleTimeString();render();
  } catch(e) {
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
