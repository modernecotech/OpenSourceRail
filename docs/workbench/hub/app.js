const context = Object.fromEntries(new URLSearchParams(location.search));
const stages = [
  ['Plan','Generate the city delivery twin and review costs.','operations'],
  ['Design','Review geometry, engineering revisions and design evidence.','studio'],
  ['Procure','Use project-linked material requests and purchase orders.','procurement'],
  ['Manufacture','Track production orders, stock and quality inspections.','manufacturing'],
  ['Construct','Record installation works and inspections.','operations'],
  ['Commission','Review tests and independent railway handback.','operations'],
  ['Operate','Open OCC controls for this control workspace.','occ'],
  ['Maintain','Inspect alarms, ERP cases and maintenance evidence.','lifecycle'],
  ['Renew','Review asset history and plan replacement work.','maintenance'],
];
document.getElementById('scope').textContent = `${context.city} · ${context.mode} · ${context.selected_asset || 'No asset selected'}`;
for (const [title,description,module] of stages) {
  const card=document.createElement('article');card.className='metric';
  const h=document.createElement('h3');h.textContent=title;
  const p=document.createElement('p');p.textContent=description;
  const b=document.createElement('button');b.textContent='Open '+title.toLowerCase();b.dataset.module=module;
  card.append(h,p,b);document.getElementById('stages').append(card);
}
document.addEventListener('click',event=>{
  const module=event.target.closest('[data-module]')?.dataset.module;
  if(module) parent.postMessage({type:'osr:navigate',module,context},location.origin);
});
const query=new URLSearchParams({city:context.city,environment:context.environment || 'simulation'});
async function get(url){const r=await fetch(url);if(!r.ok)throw new Error('Not deployed for this city');return r.json();}
const [engineering, snapshot, twins, deployment]=await Promise.allSettled([
  get('/api/lifecycle/engineering?'+query),get('/api/lifecycle/snapshot?'+query),get('/api/operating/twins'),get('/api/workbench/city?'+query),
]);
const artifacts=document.getElementById('artifacts');
if(engineering.status==='fulfilled')for(const item of engineering.value.artifacts){
  const row=document.createElement('p');const a=document.createElement('a');
  a.textContent=`${item.tool} · ${item.path.split('/').pop()}`;
  a.href='/api/lifecycle/artifact?'+new URLSearchParams({city:context.city,sha256:item.sha256});
  row.append(a);artifacts.append(row);
}
if(!artifacts.children.length)artifacts.textContent='No reviewed engineering package for this city.';
const business=twins.status==='fulfilled' && twins.value.snapshots.find(t=>t.city===context.city);
const assets=snapshot.status==='fulfilled'?snapshot.value.assets:[];
const activeAssets=assets.filter(a=>a.configuration_status!=='retired');
const retiredAssets=assets.length-activeAssets.length;
document.getElementById('status').textContent=[
  snapshot.status==='fulfilled'?`${activeAssets.length} active equipment positions${retiredAssets?` · ${retiredAssets} retired`:''}`:'Supervision not deployed or unavailable',
  business?`ERP project ${business.project} · feedback ${business.observed_at}`:'ERP city feedback not available',
].join(' · ');

if(deployment.status==='fulfilled'){
  const d=deployment.value;
  for(const text of [
    `Control workspace: ${d.control_workspace}${d.control_available?' (this city)':' (choose its city to use controls)'}`,
    `ERP binding: ${d.erp.state}${d.erp.project?' · '+d.erp.project:''}${d.erp.stale?' · feedback unavailable or over one hour old':''}`,
    `Engineering package: ${d.engineering.state} · ${d.engineering.artifact_count} sources`,
    `Supervision package: ${d.supervision.state} · ${d.supervision.equipment_count} positions (preparation is separate from live connectivity)`,
    `City profiles: ${Object.entries(d.profiles).map(([k,v])=>k+': '+(v?'configured':'missing')).join(' · ')}`,
  ]){const p=document.createElement('p');p.className='record';p.textContent=text;document.getElementById('deploymentStatus').append(p);}
  if(!d.control_available)for(const button of document.querySelectorAll('[data-module=studio],[data-module=occ]')){
    button.disabled=true;button.title=`Control workspace belongs to ${d.control_workspace}`;
  }
}
const observed=snapshot.status==='fulfilled' && snapshot.value.observed_at ? new Date(snapshot.value.observed_at*1000).toLocaleString() : 'unknown time';
document.getElementById('refreshInventory').onclick=()=>location.reload();
function showAssets(){
  const search=document.getElementById('assetSearch').value.trim().toLowerCase();
  const matches=assets.filter(a=>[a.asset_id,a.name,a.equipment_type].some(v=>String(v).toLowerCase().includes(search)));
  document.getElementById('assetResults').replaceChildren();
  document.getElementById('assetStatus').textContent=snapshot.status==='fulfilled'?`${matches.length} equipment positions · ${context.environment || 'simulation'} · snapshot ${observed}. Open an asset for continuously refreshed readings.`:'Equipment service unavailable for this city and environment.';
  for(const a of matches){
    const card=document.createElement('article');card.className='metric';
    const button=document.createElement('button');button.textContent=a.asset_id;
    button.onclick=()=>parent.postMessage({type:'osr:navigate',module:'lifecycle',context:{city:a.city,environment:a.environment,selected_asset:a.asset_id}},location.origin);
    const p=document.createElement('p');const active=a.alarms.filter(r=>r.active).length;
    p.textContent=`${a.name} · ${a.configuration_status || 'active'} package · ${a.lifecycle_state} · ${active} active alarms · ${Object.values(a.readings).filter(r=>r.quality==='valid').length}/${Object.keys(a.readings).length} valid readings`;
    card.append(button,p);document.getElementById('assetResults').append(card);
  }
}
document.getElementById('assetSearch').oninput=showAssets;showAssets();
