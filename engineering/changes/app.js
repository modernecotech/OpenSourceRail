const city=new URLSearchParams(location.search).get('city')||'samawah';
const environment=new URLSearchParams(location.search).get('environment')||'simulation';
const root=document.querySelector('#changes');
const element=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e;};
const get=async url=>{const r=await fetch(url);if(!r.ok)throw Error('Evidence unavailable: '+url);return r.json();};
try{
 const catalogue=await get('catalogue.json');
 const entries=catalogue.entries.filter(e=>e.city===city&&e.environment===environment);
 document.querySelector('#status').textContent=entries.length?`${city} · ${environment} · ${entries.length} recorded change`:`No recorded engineering change for ${city} / ${environment}.`;
 let services={};try{services=await get('/api/workbench/services');}catch{}
 for(const entry of entries){
  const [manifest,cad,before,after,assurance,native]=await Promise.all([
   get(entry.bundle+'/manifest.json'),get(entry.bundle+'/cad-results.json'),get(entry.bundle+'/baseline-analysis/summary.json'),
   get(entry.bundle+'/candidate-analysis/summary.json'),get(entry.bundle+'/assurance.json'),get(entry.native_report)]);
  if(native.manifest_sha256!==manifest.sha256)throw Error('Native report refers to a different engineering bundle');
  if(manifest.city!==city||manifest.environment!==environment||native.city!==city)throw Error('Evidence does not match the selected city and environment');
  const section=element('section','');section.append(element('h2',entry.title));
  section.append(element('p',`${manifest.component} · ${manifest.asset_id}`));
  const table=element('table','');const header=element('tr','');for(const t of ['Measured / calculated quantity','Baseline','Candidate'])header.append(element('th',t));table.append(header);
  const number=v=>Number(v).toLocaleString(undefined,{maximumFractionDigits:6});
  for(const [label,a,b] of [['Native solid depth (mm)',cad.baseline.depth_mm,cad.candidate.depth_mm],['Gross member purchase equivalent (kg)',cad.baseline.member_purchase_kg,cad.candidate.member_purchase_kg],['Midspan displacement (mm)',before.meshes.at(-1).midspan_displacement_mm,after.meshes.at(-1).midspan_displacement_mm],['Analytical discrepancy (%)',100*before.analytical_relative_error,100*after.analytical_relative_error]]){
   const row=element('tr','');row.append(element('td',label),element('td',number(a)),element('td',number(b)));table.append(row);
  }section.append(table);
  section.append(element('p',`Assurance: baseline ${assurance.records[0].status}; candidate ${assurance.records[1].status}. Formal impact assessment and independent acceptance remain required.`));
  section.append(element('p',`${native.checks.length} native ERP checks ${native.passed?'passed':'failed'}; old production held, candidate production consumed ${number(native.consumed_kg)} kg of the simulation material equivalent.`));
  section.append(element('p','CAD geometry is a gross solid design reference. Material quantities are not measured mass or an accepted fabrication bill.'));
  const links=element('ul','');
  for(const [label,path] of [['Native candidate CAD',entry.bundle+'/candidate.FCStd'],['Checksummed dependency manifest',entry.bundle+'/manifest.json'],['Native ERP result',entry.native_report],['Screening and superseded evidence',entry.bundle+'/assurance.json']]){
   const li=element('li','');const a=element('a',label);a.href=path;li.append(a);links.append(li);
  }section.append(links);
  if(services.erp===entry.erp_origin){
   const nativeLinks=element('ul','');nativeLinks.id='nativeLinks';
   // A fresh database can reuse sequential document IDs at the same origin.
   // Bind searches to this run's unique project/item identity as well as IDs.
   for(const [label,path,filters] of [
    ['Find recorded project','project',{project_name:'OSR simulation CAD change '+native.run,custom_osr_city:city}],
    ['Find held baseline work order','work-order',{name:native.work_orders.baseline,production_item:'CAD-KIT-'+native.run}],
    ['Find produced candidate work order','work-order',{name:native.work_orders.candidate,production_item:'CAD-KIT-'+native.run}],
    ['Find revised BOM','bom',{name:native.boms.candidate.kit,item:'CAD-KIT-'+native.run}]]){
    const li=element('li','');const a=element('a',label);a.href=services.erp+'/app/'+path+'?'+new URLSearchParams(filters);
    a.addEventListener('click',event=>{if(parent!==window){event.preventDefault();parent.postMessage({type:'osr:open-link',url:a.href},location.origin);}});li.append(a);nativeLinks.append(li);
   }section.append(element('p','Search native records by this run’s unique identity (authentication required). A fresh deployment may contain no matches; records may change after this run.'),nativeLinks);
  }else section.append(element('p','The native records belong to another recorded deployment; this view retains their evidence without linking to unrelated local record IDs.'));
  root.append(section);
 }
}catch(error){document.querySelector('#status').textContent=error.message;root.replaceChildren();}
