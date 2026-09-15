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
const [engineering, snapshot, twins]=await Promise.allSettled([
  get('/api/lifecycle/engineering?'+query),get('/api/lifecycle/snapshot?'+query),get('/api/operating/twins'),
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
document.getElementById('status').textContent=[
  snapshot.status==='fulfilled'?`${snapshot.value.assets.length} connected equipment positions`:'Supervision not deployed or unavailable',
  business?`ERP project ${business.project} · feedback ${business.observed_at}`:'ERP city feedback not available',
].join(' · ');
