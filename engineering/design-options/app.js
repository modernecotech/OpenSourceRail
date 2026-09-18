const query=new URLSearchParams(location.search);
const city=query.get('city')||'samawah', environment=query.get('environment')||'simulation';
const root=document.querySelector('#options');
const element=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e;};
const get=async url=>{const r=await fetch(url);if(!r.ok)throw Error('Evidence unavailable: '+url);return r;};
const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
const number=v=>Number(v).toLocaleString(undefined,{maximumFractionDigits:2});
try {
 const catalogue=await (await get('catalogue.json')).json();
 const entries=catalogue.entries.filter(e=>e.city===city&&e.environment===environment);
 document.querySelector('#status').textContent=entries.length?`${city} · ${environment} · ${entries.length} recorded options`:`No recorded design options for ${city} / ${environment}.`;
 for(const entry of entries){
  if(!/^examples\/[a-z0-9-]+$/.test(entry.bundle))throw Error('Invalid option location');
  const base=entry.bundle+'/';
  const manifestBytes=await (await get(base+'manifest.json')).arrayBuffer();
  const manifest=JSON.parse(new TextDecoder().decode(manifestBytes));
  const result=await (await get(base+'result.json')).json();
  if(manifest.city!==city||manifest.environment!==environment||result.city!==city||result.id!==manifest.id||result.environment!==environment||result.operating_release!==false)throw Error('Evidence does not match the selected city and environment');
  if(result.manifest_sha256!==await digest(manifestBytes))throw Error('Changed option manifest');
  const records={};
  for(const [name,hash] of Object.entries({...manifest.files,'qualification.json':result.qualification_sha256})){
   if(!/^[a-z0-9.-]+$/.test(name))throw Error('Invalid option file');
   const bytes=await (await get(base+name)).arrayBuffer();
   if(await digest(bytes)!==hash)throw Error('Changed option evidence: '+name);
   if(name.endsWith('.json'))records[name]=JSON.parse(new TextDecoder().decode(bytes));
  }
  const report=records['qualification.json'], changes=records['changes.json'];
  if(report.scenario_sha256!==manifest.files[city+'.toml']||report.design_sha256!==manifest.files['design.toml']||report.service_acceptance_schema!=='osr-city-service-qualification/1'||result.passed!==Boolean(report.passed&&report.qualification_inputs_unchanged&&report.resilience_required&&report.full_window_passed))throw Error('Qualification does not match this option');
  const section=element('section','');section.append(element('h2',entry.title));
  const outcome=element('p',result.passed?'Full-window simulation qualification passed.':'Simulation qualification failed; further design changes required.');
  outcome.className=result.passed?'pass':'fail';section.append(outcome);
  const labels={charging_dwell_seconds:'Charging dwell (seconds)',additional_trainsets:'Additional trainsets',additional_storage_modules:'Additional modules per site',additional_pv_kw:'Additional solar per site (kWp)'};
  for(const [line,settings] of Object.entries(records['profile.json'].lines))section.append(element('p',line+': '+Object.entries(settings).map(([key,value])=>labels[key]+' = '+number(value)).join('; ')));
  const delta=changes.resource_delta;
  section.append(element('p',`Resource change: ${number(delta.additional_trainsets)} trainsets; ${number(delta.additional_storage_modules)} storage modules (${number(delta.additional_storage_kwh)} kWh); ${number(delta.additional_pv_kw)} kWp solar across ${delta.affected_energy_sites} sites. Costs have not been recalculated.`));
  if(!manifest.canonical_scenario_matches_generator)section.append(element('p','Generator baseline differs from the canonical scenario. Review both before attributing all differences to this option.'));
  const table=element('table','');const header=element('tr','');for(const t of ['Test case','Per-line result','Lowest delivered / scheduled mileage'])header.append(element('th',t));table.append(header);
  for(const c of [report.runs.at(-1),...report.resilience_cases]){
   const row=element('tr','');const screen=c.line_service;
   const low=Math.min(...screen.lines.map(l=>l.raw_completion_ratio??0));
   row.append(element('td',c.label||c.name),element('td',screen.passed?'Pass':'Failed: '+screen.lines.filter(l=>!l.passed).map(l=>l.line_id).join(', ')),element('td',number(low*100)+'%'));table.append(row);
  }section.append(table);
  const links=element('p','');
  for(const [label,path] of [['City profile','profile.json'],['Change ledger','changes.json'],['Full result','qualification.json'],['Generated scenario',city+'.toml'],['Dependency manifest','manifest.json']]){
   const a=element('a',label);a.href=base+path;links.append(a,document.createTextNode(' · '));
  }section.append(links);
  section.append(element('p','Recorded artifact hashes verified. Current source currency is checked by the CLI. Passing simulation does not grant operating release.'));
  root.append(section);
 }
}catch(error){root.replaceChildren();document.querySelector('#status').textContent=error.message;}
