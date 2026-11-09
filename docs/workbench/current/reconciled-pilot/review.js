'use strict';
const $ = (selector) => document.querySelector(selector);
const node = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined && text !== null) n.textContent = text; if (cls) n.className = cls; return n; };
const money = (value) => value == null ? 'Unknown / not annualised' : '$' + (Number(value) / 1e6).toLocaleString(undefined, {maximumFractionDigits: 2}) + 'm';
const number = (value, digits=1) => value == null ? 'Unknown' : Number(value).toLocaleString(undefined, {maximumFractionDigits: digits});
function requireFalseFlags(data) {
  for (const key of ['engineering_accepted','physical_accepted','manufacturing_release','operating_release','movement_authority'])
    if (data.status[key] !== false) throw new Error('The display cannot grant or imply ' + key.replaceAll('_',' ') + '.');
  for (const variant of [data.recovery_comparison.with_store,data.recovery_comparison.without_store])
    for (const [key,value] of Object.entries(variant.release_flags)) if (value !== false) throw new Error('Unexpected release state: ' + key);
  if (data.project_scope.city_corridor_integration !== false) throw new Error('Pilot and city corridor identities must remain separate.');
  if (data.recovery_comparison.with_store.physical_candidate_id === data.recovery_comparison.without_store.physical_candidate_id)
    throw new Error('The separate no-store physical candidate identity is missing.');
  if (data.journeys.some(row => row.candidate_id !== data.identity.physical_candidate_id))
    throw new Error('A journey row belongs to a different physical candidate.');
}
function show(data) {
  if (data.schema !== 'osr-reconciled-pilot-workbench/1') throw new Error('Unexpected Workbench evidence format.');
  requireFalseFlags(data);
  for (const [id,value] of [['status-outline',data.status.outline],['status-engineering',data.status.engineering],['status-prototype',data.status.prototype],['status-release',data.status.release]]) $('#'+id).textContent = value;
  const identityRows = [
    ['Reconciled physical bundle candidate',data.identity.physical_candidate_id],
    ['Bundle evaluation',data.identity.bundle_evaluation_id],
    ['Study',data.identity.study_id],
    ['Body candidate / evaluation',data.identity.body_candidate_id+' / '+data.identity.body_evaluation_id],
    ['Civil candidate / evaluation',data.identity.civil_candidate_id+' / '+data.identity.civil_evaluation_id],
    ['Installed component candidate',data.identity.installed_component_candidate_id],
    ['Installed mass evaluation',data.identity.installed_mass_evaluation_id],
  ];
  const identityList=$('#identities');
  for(const [label,value] of identityRows){const item=node('div');item.append(node('dt',label),node('dd',value));identityList.append(item);}
  $('#source-identity').textContent=`Published packet manifest ${data.source.manifest_id} · study ${data.source.study_id}. The body and civil component IDs above remain separately identified parts of this physical bundle.`;
  function renderJourneys(){
    const body=$('#journeys');body.replaceChildren();
    for(const row of data.journeys){
      if(!$('#faults').checked&&!['nominal','recovery-disabled'].includes(row.experiment))continue;
      const tr=node('tr');
      for(const value of [row.experiment,`${number(row.headway_s,0)} s / ${number(row.opposite_phase_s,0)} s`,`${row.active_trainsets} + ${row.spare_trainsets}`,`${row.arrivals}/${row.requested}`,number(row.maximum_journey_s)+' s',number(row.grid_traction_kwh,2)+' kWh',money(row.cost.installed_capital_usd?.base),money(row.cost.known_lifecycle_subtotal_usd?.base),money(row.cost.whole_life_NPV_usd?.base)])tr.append(node('td',value));
      tr.append(node('td',row.model_screen?'Pass under model assumptions':'Held',row.model_screen?'pass':'held'),node('td',row.service_id),node('td',row.cost_evaluation_id));body.append(tr);
    }
  }
  $('#faults').addEventListener('change',renderJourneys);renderJourneys();
  $('#recovery-description').textContent=data.recovery_comparison.description;
  const recovery=$('#recovery');
  for(const [label,row] of [['With-store physical pilot',data.recovery_comparison.with_store],['Separate no-store physical control',data.recovery_comparison.without_store]]){
    const c=row.case,tr=node('tr');
    const identity=`${row.physical_candidate_id} · ${row.bundle_evaluation_id}`;
    const energy=`${number(c.capture_kwh,2)} / ${number(c.relaunch_kwh,2)} kWh`;
    for(const value of [label,identity,c.service_evaluation_id,c.cost_evaluation_id,number(c.grid_traction_kwh,2)+' kWh',energy,money(c.installed_capital_usd.base),money(c.known_lifecycle_subtotal_usd.base)])tr.append(node('td',value));
    recovery.append(tr);
  }
  const figure=node('figure'),img=node('img');img.src='/docs/design-engine/reconciled-pilot/civil-assembly.svg';img.alt='Source-published civil assembly drawing';figure.append(img,node('figcaption','Civil assembly drawing from the pinned two-station pilot packet.'));$('#gallery').append(figure);
  const cad=node('p');cad.append(node('span','Vehicle gallery: '));const glb=node('a','open installed vehicle assembly (GLB)');glb.href='/docs/design-engine/reconciled-pilot/vehicle/assembly.glb';cad.append(glb);$('#gallery').append(cad);
  const step=node('p');const stepA=node('a','open verified stock STEP');stepA.href='/docs/design-engine/reconciled-pilot/native-cad/solidcraft/assembly.step';step.append(stepA,node('span',' · research stock model; not production CAD approval'));$('#gallery').append(step);
  const m=data.manufacturing;
  $('#manufacturing-state').textContent=`Vehicle manifest ${m.vehicle_manifest_id}; delivery manifest ${m.delivery_manifest_id}. ${m.task_status_counts['ready-for-planning-review'] ?? 0} tasks are ready for planning review and ${m.task_status_counts.held ?? 0} remain held. Installed mass complete: ${m.installed_mass_complete}. Engineering accepted: ${m.engineering_accepted}. Manufacturing release: ${m.manufacturing_release}.`;
  $('#mass').append(node('p',`${data.body_summary.proposed_component_types} proposed body component types in ${number(data.body_summary.total_occurrences,0)} located occurrences. Nominal body stock subtotal: ${number(data.body_summary.nominal_part_mass_kg.base/1000,3)} t. This is not complete loaded-train mass.`));
  $('#mass').append(node('p','Direct body parts/process estimate, base: '+money(data.body_summary.direct_parts_process_usd.base)+'.'));
  const scope=data.mass_scopes.find(row=>row.load_case==='normal-base');
  if(scope){for(const [key,label] of [['body_stock_and_equipment_kg','Body stock and equipment subtotal'],['body_with_payload_and_installation_reserve_kg','Body with normal payload and installation reserve'],['external_known_drives_kg','External known drives'],['remaining_external_drive_reserve_kg','Remaining external drive reserve'],['capture_interface_reserve_kg','Capture interface reserve'],['integrated_mass_kg','Integrated loaded model mass']])$('#mass').append(node('p',`${number(scope[key]/1000,3)} t — ${label}`));}
  $('#price-maturity').textContent='Price basis: '+data.assumptions.price_maturity+'. '+data.assumptions.requirement_interpretation+' Calculated scenarios are not supplier offers.';
  const downloads=$('#downloads');for(const item of data.downloads){const li=node('li'),a=node('a',item.label);a.href=item.href;li.append(a,node('small','Published payload SHA-256: '+item.sha256));downloads.append(li);}
  const packets=$('#packet-links');
  for(const packet of [data.recovery_comparison.with_store,data.recovery_comparison.without_store])for(const item of packet.source_links){const li=node('li'),a=node('a',packet.physical_candidate_id.slice(0,12)+'… · '+item.label);a.href=item.href;li.append(a,node('small','Candidate '+packet.physical_candidate_id+' · SHA-256 '+item.sha256));packets.append(li);}
  $('#producer-pins').textContent=JSON.stringify({with_store:data.source.producer_source_sha256,without_store:data.recovery_comparison.without_store.producer_source_sha256},null,2);
  const unresolved=$('#unresolved');for(const item of data.unresolved){const li=node('li');li.append(node('strong',item.id.replaceAll('-',' ')+': '),node('span',item.task+' '),node('small','Dependency: '+item.dependency+'. Status: '+item.status+'.'));unresolved.append(li);}
  $('#city-brief').href=data.project_scope.city_brief;
  const cityA=$('#city-atlas');cityA.href=data.project_scope.city_atlas;
  $('#footer').textContent=`Pilot source: ${data.source.manifest}. Baghdad city outline evaluation ${data.project_scope.city_outline_evaluation_id} is a separate larger-corridor planning record.`;
  $('#loading').hidden=true;$('#content').hidden=false;
}
fetch('data.json',{cache:'no-store'}).then(response=>{if(!response.ok)throw new Error('The generated source-bound pilot review is unavailable.');return response.json();}).then(show).catch(error=>{const box=$('#error');box.textContent=error.message;box.hidden=false;$('#loading').hidden=true;});
