const $ = id => document.getElementById(id);
let baseline = null, result = null, selectedWork = null;
const closures = [];
const params = new URLSearchParams(location.search);
$('city').value = params.get('city') || 'samawah';
$('environment').value = params.get('environment') === 'physical' ? 'physical' : 'simulation';
const scope = () => ({city:$('city').value, environment:$('environment').value});
const sameScope = row => row.city === scope().city && row.environment === scope().environment;
const show = (message, error=false) => { $('status').textContent=message; $('status').className=error?'error':''; };
const dbReady = new Promise((resolve,reject) => {
  const request=indexedDB.open('osr-field-work-v1',1);
  request.onupgradeneeded=()=>{for(const name of ['packs','queue','settings'])request.result.createObjectStore(name,{keyPath:'id'});};
  request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);
});
async function db(name, action, value) {
  const database=await dbReady;
  return new Promise((resolve,reject)=>{
    const transaction=database.transaction(name, action==='getAll'?'readonly':'readwrite');
    const request=transaction.objectStore(name)[action](value);
    transaction.oncomplete=()=>resolve(request.result);transaction.onerror=()=>reject(transaction.error);
  });
}
async function api(endpoint, body=null) {
  const token=$('credential').value;
  if(!token)throw new Error('Enter a scoped credential to connect.');
  const response=await fetch('/api/operations/'+endpoint+(body===null?'?'+new URLSearchParams(scope()):''),{
    method:body===null?'GET':'POST',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},
    ...(body===null?{}:{body:JSON.stringify({...scope(),...body})})});
  const value=await response.json();
  if(!response.ok){const error=new Error(value.error||'Request failed');error.status=response.status;throw error;}
  return value;
}
async function readJson(input){if(!input.files[0])throw new Error('Choose an evidence file.');return JSON.parse(await input.files[0].text());}
function bind(id, action){$(id).onclick=async()=>{try{await action();}catch(error){show(error.message,true);}};}
function table(id, columns, rows){
  const table=document.createElement('table'),header=document.createElement('tr');
  for(const [label]of columns){const cell=document.createElement('th');cell.textContent=label;header.append(cell);}table.append(header);
  for(const row of rows){const tr=document.createElement('tr');for(const [,key]of columns){const td=document.createElement('td');td.textContent=Array.isArray(row[key])?row[key].join(', '):row[key]??'—';tr.append(td);}table.append(tr);}
  $(id).replaceChildren(table);
}
function choices(id, rows){$(id).replaceChildren();for(const row of rows){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=row.id;label.append(input,document.createTextNode(' '+row.id));$(id).append(label);}}
function loaded(){
  const p=baseline.package;result=null;closures.length=0;$('closures').replaceChildren();
  $('baseline').textContent=`Revision ${p.revision} · ${p.epoch} · ${p.services.length} services · ${p.trains.length} trains · ${baseline.sha256.slice(0,12)}`;
  choices('trains',p.trains);choices('workers',p.workers||[]);$('resource').replaceChildren();
  for(const r of p.resources){const option=document.createElement('option');option.value=r.id;option.textContent=`${r.id} (${r.kind})`;$('resource').append(option);}
  $('closureEnd').max=p.horizon_s;$('connection').textContent='Connected';
}
for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>{for(const section of document.querySelectorAll('.view'))section.hidden=section.id!==button.dataset.view;};
bind('connect',async()=>{baseline=await api('baseline');loaded();await renderWork();});
bind('register',async()=>{
  const packageValue=await readJson($('packageFile'));
  if(packageValue.city!==scope().city||packageValue.environment!==scope().environment)throw new Error('Package belongs to a different city or environment.');
  let expected=null;
  try{expected=(await api('baseline')).sha256;}catch(error){if(error.status!==400)throw error;}
  await api('baseline',{package:packageValue,expected});baseline=await api('baseline');loaded();show('Controlled package registered.');
});
bind('addClosure',async()=>{
  if(!baseline)throw new Error('Load a planning baseline first.');
  const start=Number($('closureStart').value),end=Number($('closureEnd').value);
  if(!Number.isInteger(start)||!Number.isInteger(end)||start<0||end<=start||end>baseline.package.horizon_s)throw new Error('Closure interval must lie within the planning horizon.');
  const row={id:'closure-'+crypto.randomUUID(),resources:[$('resource').value],start_s:start,end_s:end,reason:'Operator recovery scenario'};closures.push(row);
  const item=document.createElement('li');item.textContent=`${row.resources[0]}: ${start}–${end}s `;const remove=document.createElement('button');remove.textContent='Remove';remove.onclick=()=>{closures.splice(closures.indexOf(row),1);item.remove();};item.append(remove);$('closures').append(item);
});
bind('plan',async()=>{
  if(!baseline)throw new Error('Load a planning baseline first.');
  const unavailable=id=>[...$(id).querySelectorAll('input:checked')].map(input=>input.value);
  $('plan').disabled=true;
  try{result=await api('plan',{expected:baseline.sha256,disruptions:{unavailable_trains:unavailable('trains'),unavailable_workers:unavailable('workers'),possessions:closures}});
    $('planSummary').textContent=`${result.services.length} services retained · ${result.cancelled.length} cancelled · ${result.roster.uncovered.length} staff duties uncovered · ${result.search_exhausted?'search limit reached':'declared search completed'} · management proposal`;
    table('serviceTable',[['Service','id'],['Train','train_id'],['Route','route_id'],['Departure (s)','start_s'],['Arrival (s)','end_s']],result.services);
    table('fleetTable',[['Train','train_id'],['Work','kind'],['From','origin'],['To','destination'],['Start','start_s'],['End','end_s'],['Energy (kWh)','remaining_energy_kwh']],result.fleet_diagram);
    table('rosterTable',[['Duty','duty_id'],['Role','role'],['Worker','worker_id'],['Start','start_s'],['End','end_s']],result.roster.assignments);
    show(result.cancelled.length?'Cancelled services: '+result.cancelled.map(r=>r.id).join(', '):'Revised plan ready for review.');
  }finally{$('plan').disabled=false;}
});
async function renderWork(filter=''){
  const rows=(await db('packs','getAll')).filter(sameScope).filter(row=>!filter||row.id===filter||row.asset_id===filter);
  $('workList').replaceChildren();
  for(const work of rows){const card=document.createElement('div');card.className='work-card';const label=document.createElement('p');label.textContent=`${work.id} · ${work.asset_id} · ${work.state} · expires ${work.expires_at}`;card.append(label);
    if(work.state==='issued'){const button=document.createElement('button');button.textContent='Record work';button.onclick=()=>openWork(work);card.append(button);} $('workList').append(card);
  }
  if(!rows.length)$('workList').textContent='No downloaded work in this scope.';
  await renderQueue();
}
function openWork(work){
  selectedWork=work;$('workForm').hidden=false;$('workTitle').textContent=`${work.id} · ${work.asset_id}`;$('workRevision').textContent=`Method ${work.method_revision} · engineering ${work.engineering_revision} · assigned to ${work.assigned_to}`;$('workInstructions').textContent=work.instructions||'Follow the issued method referenced in this work pack.';$('readings').replaceChildren();$('photos').value='';$('notes').value='';
  for(const spec of work.readings){const label=document.createElement('label');label.textContent=spec.id+(spec.unit?' ('+spec.unit+')':'')+' ';const input=document.createElement('input');input.dataset.reading=spec.id;input.required=spec.required;
    if(spec.kind==='number'){input.type='number';input.step='any';input.min=spec.min;input.max=spec.max;}else if(spec.kind==='boolean'){input.type='checkbox';input.required=false;}else{input.type='text';input.maxLength=10000;}
    label.append(input);$('readings').append(label);
  }
}
bind('issueWork',async()=>{if(!baseline)throw new Error('Load a planning baseline first.');const work=await readJson($('workFile'));await api('work',{work,expected:baseline.sha256});show('Reviewed work pack issued.');});
bind('refreshWork',async()=>{const response=await api('work');for(const work of response.items)await db('packs','put',work);await renderWork();show(`${response.items.length} assigned work packs downloaded.`);});
bind('findWork',async()=>{
  let identity=$('lookup').value.trim();
  if(identity.startsWith('osr://')){const url=new URL(identity);if(url.hostname!=='asset'||url.searchParams.get('city')!==scope().city||url.searchParams.get('environment')!==scope().environment)throw new Error('Lookup QR belongs to another scope.');identity=url.searchParams.get('id');}
  await renderWork(identity);
});
async function photo(file){
  if(!['image/png','image/jpeg'].includes(file.type)||file.size>2000000)throw new Error('Use PNG or JPEG photos up to 2 MB.');
  const bytes=new Uint8Array(await file.arrayBuffer());const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  return{id:'photo-'+crypto.randomUUID(),mime:file.type,sha256:hash,base64:btoa(binary)};
}
$('workForm').onsubmit=async event=>{
  event.preventDefault();try{
    const work=selectedWork;if(!work||!sameScope(work))throw new Error('Select work in this scope.');
    const readings={};for(const spec of work.readings){const input=[...$('readings').querySelectorAll('input')].find(x=>x.dataset.reading===spec.id);
      if(spec.kind==='boolean')readings[spec.id]=input.checked;else if(input.value!=='')readings[spec.id]=spec.kind==='number'?{value:Number(input.value),unit:spec.unit}:input.value;
    }
    let settings=(await db('settings','getAll'))[0];if(!settings){settings={id:'device',device_id:'device-'+crypto.randomUUID()};await db('settings','put',settings);}
    const photos=await Promise.all([...$('photos').files].map(photo));
    const value={id:'event-'+crypto.randomUUID(),performed_at:new Date().toISOString(),device_id:settings.device_id,work_id:work.id,status:'performed-awaiting-inspection',readings,photos,notes:$('notes').value};
    if(JSON.stringify(value).length>3900000)throw new Error('Combined evidence exceeds upload limit; use fewer or smaller photos.');
    await db('queue','put',{id:value.id,...scope(),event:value,state:'queued'});work.state='queued-on-device';await db('packs','put',work);
    $('workForm').hidden=true;await renderWork();show('Work saved on this device for independent inspection.');
  }catch(error){show(error.message,true);}
};
async function renderQueue(){const rows=(await db('queue','getAll')).filter(sameScope);table('queue',[['Event','id'],['State','state'],['Details','error']],rows);}
async function synchronise(){
  for(const row of(await db('queue','getAll')).filter(sameScope).filter(r=>r.state==='queued')){
    try{const response=await api('complete',{event:row.event});row.state=response.state==='delivered'?'delivered':'accepted';row.error='';}
    catch(error){row.error=error.message;if([400,403,409,417,422].includes(error.status))row.state='conflict';}
    await db('queue','put',row);
  }
  const server=await api('field-events');
  for(const row of(await db('queue','getAll')).filter(sameScope)){const record=server.items.find(r=>r.id===row.id);if(record){row.state=record.state;row.error=record.error||'';await db('queue','put',row);}}
  await renderQueue();show('Synchronisation checked. Conflicts remain on this device for review.');
}
bind('sync',synchronise);
window.addEventListener('online',()=>{if($('credential').value)synchronise().catch(error=>show(error.message,true));});
bind('clearDevice',async()=>{for(const row of(await db('queue','getAll')).filter(sameScope).filter(r=>r.state==='delivered')){await db('queue','delete',row.id);await db('packs','delete',row.event.work_id);}await renderWork();});
bind('analyse',async()=>{$('reliabilityResult').textContent=JSON.stringify(await api($('analysis').value,{data:await readJson($('reliabilityFile'))}),null,2);});
function download(value,name,type='application/json'){
  const blob=new Blob([value],{type});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
}
bind('export',async()=>{
  if(!result)throw new Error('Generate a current plan first.');const format=$('format').value;
  const response=await fetch('/api/operations/export?'+new URLSearchParams({...scope(),id:result.sha256,format}),{headers:{Authorization:'Bearer '+$('credential').value}});const value=await response.json();if(!response.ok)throw new Error(value.error);
  if(value.base64)download(Uint8Array.from(atob(value.base64),c=>c.charCodeAt(0)),value.filename,value.content_type);else download(JSON.stringify(value,null,2),format+'.json');
});
bind('importGtfs',async()=>{const file=$('gtfsFile').files[0];if(!file||file.size>8000000)throw new Error('Choose a bounded GTFS ZIP.');const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));$('importResult').textContent=JSON.stringify(await api('import-gtfs',{base64:btoa(binary),operating_date:$('operatingDate').value}),null,2);});
bind('operatorExchange',async()=>{$('operatorResult').textContent=JSON.stringify(await api('operator-exchange',{adapter_id:$('adapter').value,records:await readJson($('operatorFile')),direction:$('direction').value}),null,2);});
window.addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==parent||event.data?.type!=='osr:context')return;const context=event.data.context;$('city').value=context.city;$('environment').value=context.environment;baseline=null;result=null;selectedWork=null;$('workForm').hidden=true;renderWork().catch(error=>show(error.message,true));});
for(const id of ['city','environment'])$(id).addEventListener('change',()=>{baseline=null;result=null;selectedWork=null;$('workForm').hidden=true;$('baseline').textContent='Load the selected city and environment.';for(const area of ['serviceTable','fleetTable','rosterTable'])$(area).replaceChildren();renderWork().catch(error=>show(error.message,true));});
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{});
await renderWork();
