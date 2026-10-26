'use strict';
const byId = id => document.getElementById(id);
const format = n => Number(n).toLocaleString('en-GB', {maximumFractionDigits: 2});
const identityKeys = ['selection_id', 'candidate_id', 'body_candidate_id', 'magnet_component_id'];
const qualificationKeys = ['engineering_accepted','physical_accepted','installed_mass_complete','manufacturing_release','operating_release'];
function validated(value, expected) {
  if(value.development_default !== true) throw Error('This record is not the selected development default.');
  for(const key of qualificationKeys) if(value[key] !== false) throw Error('Unexpected qualification disposition: '+key);
  for(const key of identityKeys) {
    if(!/^[a-f0-9]{64}$/.test(value[key] || '')) throw Error('Missing selected identity: '+key);
    if(expected && value[key] !== expected[key]) throw Error('Mixed candidate identity: '+key);
  }
  return value;
}
async function request(url) {
  const response = await fetch(url, {cache:'no-store'});
  const value = await response.json();
  if(!response.ok) throw Error(value.reason || 'Current record unavailable');
  return value;
}
function fact(container, label, value) {
  const dt=document.createElement('dt'),dd=document.createElement('dd');
  dt.textContent=label;dd.textContent=value ?? 'Unknown';container.append(dt,dd);
}
function readable(value) {
  if(value === null || value === undefined) return 'Unknown';
  return typeof value === 'object' ? JSON.stringify(value) : String(value);
}
function renderGates(gates) {
  const rows=Array.isArray(gates) ? gates : Object.entries(gates || {}).map(([id,g]) => typeof g==='object' ? {id,...g} : {id,screen:g});
  for(const gate of rows) {
    const tr=document.createElement('tr'),name=document.createElement('td'),screen=document.createElement('td'),detail=document.createElement('td'),badge=document.createElement('span');
    name.textContent=gate.title || gate.name || gate.id || gate.requirement || 'Engineering gate';
    const state=String(gate.engineering_screen || gate.screen || gate.status || gate.disposition || 'unknown').toLowerCase();
    badge.textContent=state;badge.className='screen '+(state==='pass'?'pass':state==='fail'?'fail':'unknown');screen.append(badge);
    detail.textContent=readable(gate.reason || gate.basis || gate.limitation || gate.note || gate.scope || gate.evidence || gate);
    tr.append(name,screen,detail);byId('gates').append(tr);
  }
  if(!rows.length){const tr=document.createElement('tr');const td=document.createElement('td');td.colSpan=3;td.textContent='Unknown — no current readiness gates supplied.';tr.append(td);byId('gates').append(tr);}
}
let current;
async function showCity(slug) {
  byId('city-status').textContent='Checking current city record…';byId('city-details').textContent='';
  try {
    const city=validated(await request('/api/city/'+encodeURIComponent(slug)),current);
    byId('city-status').textContent=(city.name || city.city_name || slug)+' · selected-design analytical planning';
    byId('city-details').textContent=JSON.stringify(city.planning || city.network || city.service || city.summary || city,null,2);
    const path=city.summary_path || city.current_summary_path;
    if(path)byId('city-link').href='/'+path;
  } catch(error) {byId('city-status').textContent='Held: '+error.message;}
}
async function start() {
  try {
    current=validated(await request('/api/default-design'));
    if(current.publication_state !== 'current') throw Error('The selected publication is not current.');
    const packet=validated(current.publication,current),v=current.vehicle,s=current.service;
    const speed=s.launch_speed_cap_m_s*3.6,capacity=v.cars*v.normal_passengers_per_car*3600/s.headway_s;
    if(speed!==72 || s.headway_s!==120 || capacity!==8280 || v.normal_passengers_per_car!==46 || v.standing_passengers_per_car!==0) throw Error('Selected service specification differs.');
    byId('speed').textContent=format(speed);byId('headway').textContent=format(s.headway_s);byId('capacity').textContent=format(capacity);
    const vf=byId('vehicle-facts');
    fact(vf,'Formation',v.cars+' × '+v.body_length_m+' m');fact(vf,'Passengers',v.normal_passengers_per_car+' / car; '+v.cars*v.normal_passengers_per_car+' / train');
    fact(vf,'Standing passengers','0');fact(vf,'Passenger doors',v.passenger_doors_total_per_car+' / car, one side');
    const mass=packet.mass || current.mass;
    fact(vf,'Accounted tare / car',readable(mass.accounted_tare_kg_per_car ? format(mass.accounted_tare_kg_per_car/1000)+' t' : mass.accounted_empty_mass_kg ? format(mass.accounted_empty_mass_kg/1000)+' t' : mass));
    const nf=byId('network-facts');fact(nf,'Retained stop spacing','Existing city stops retained');fact(nf,'2 km station example',s.prototype_shared_winding_m+' m shared winding');fact(nf,'Sections / direction',s.prototype_shared_winding_m/s.station_section_m);fact(nf,'Independent branches','At least '+s.minimum_phase_branches_per_direction+' / direction');
    fact(vf,'Accounted cap-loaded / car',mass.accounted_cap_loaded_kg_per_car ? format(mass.accounted_cap_loaded_kg_per_car/1000)+' t' : 'Unknown');
    const cities=packet.cities || {};const baghdad=cities.Baghdad || cities.baghdad || {};
    fact(nf,'Baghdad fleet',readable(baghdad.total_trainsets || baghdad.fleet || baghdad.trainsets || 'See current city record'));
    renderGates(packet.gates || packet.readiness?.gates);
    for(const key of identityKeys)fact(byId('identities'),key.replaceAll('_',' '),current[key]);
    byId('native-scope').textContent='Native evidence scope: '+readable(packet.native?.methodscope || packet.native?.method_scope || packet.native?.scope || packet.native || 'See the current engineering report.');
    byId('loading').hidden=true;byId('design').hidden=false;
    try {
      const catalogue=await request('/api/cities');
      const rows=Array.isArray(catalogue)?catalogue:(catalogue.cities || catalogue.entries || []);
      byId('city').replaceChildren();
      for(const row of rows){const option=document.createElement('option');option.value=row.slug;option.textContent=row.name || row.slug;byId('city').append(option);}
      byId('city').value='baghdad';byId('city').addEventListener('change',()=>showCity(byId('city').value));
      await showCity('baghdad');
    } catch(error) {byId('city-status').textContent='Held: '+error.message;}
  } catch(error) {
    byId('loading').hidden=true;byId('design').hidden=true;byId('error').hidden=false;
    byId('error').textContent='Current design held: '+error.message+' Rebuild and verify the selected publication; no historical fallback was loaded.';
  }
}
start();
