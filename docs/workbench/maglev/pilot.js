// Read-only evidence review; business execution retains native application roles.
const status = document.querySelector('#pilot-status');
const select = document.querySelector('#pilot-view');
const detail = document.querySelector('#pilot-detail');
const body = document.querySelector('#pilot-deliverables');
const base = '/docs/design-engine/ferrite-maglev/';
const number = value => new Intl.NumberFormat('en-GB', {maximumFractionDigits: 1}).format(value);
const usd = value => new Intl.NumberFormat('en-GB', {style:'currency',currency:'USD',maximumFractionDigits:0}).format(value);
let viewRequest = 0;
const objectURLs = [];
async function payload(path, digest, unbound=false) {
  if (!unbound && !/^[a-f0-9]{64}$/.test(digest || '')) throw Error('Missing pilot payload identity');
  const response = await fetch(path);
  if (!response.ok) throw Error(`Pilot evidence unavailable (${response.status})`);
  const data = await response.arrayBuffer();
  if (data.byteLength > 16*1024*1024) throw Error('Pilot presentation payload exceeds its budget');
  if (!unbound) {
    const actual = [...new Uint8Array(await crypto.subtle.digest('SHA-256', data))].map(v => v.toString(16).padStart(2,'0')).join('');
    if (actual !== digest) throw Error('Pilot evidence differs from its receipt');
  }
  return data;
}
async function read(path, digest, unbound=false) {
  return JSON.parse(new TextDecoder().decode(await payload(path,digest,unbound)));
}
function paragraph(text) {
  const p = document.createElement('p'); p.textContent = text; detail.append(p);
}
function table(rows) {
  const dl = document.createElement('dl');
  for (const [label, value] of rows) {
    const dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = label; dd.textContent = String(value); dd.style.overflowWrap='anywhere'; dl.append(dt, dd);
  }
  detail.append(dl);
}
async function picture(path, label, digest, token) {
  if (!digest) throw Error('Missing pilot image receipt');
  const data=await payload(path,digest);
  if (token !== viewRequest) return false;
  const url=URL.createObjectURL(new Blob([data],{type:path.endsWith('.svg')?'image/svg+xml':'image/png'}));
  const img=document.createElement('img');img.src=url;img.alt=label;
  try {
    await img.decode();
    if (!img.complete || img.naturalWidth<=0) throw Error('Pilot image could not be decoded');
  } catch (error) {
    URL.revokeObjectURL(url);throw Error('Pilot image could not be decoded');
  }
  if (token !== viewRequest) {URL.revokeObjectURL(url);return false;}
  objectURLs.push(url);detail.append(img);return true;
}
async function videoLink(path, label, digest, token) {
  const data=await payload(path,digest);
  if (token !== viewRequest) return false;
  const url=URL.createObjectURL(new Blob([data],{type:'video/mp4'}));objectURLs.push(url);
  const link=document.createElement('a');link.href=url;link.textContent=label;detail.append(link);
  return true;
}
try {
  const manifest = await read(base+'pilot-delivery/manifest.json',null,true);
  const pilot = await read(base+'pilot-delivery/study.json', manifest.files_sha256['study.json']);
  if (pilot.physical_release !== false || pilot.design_complete !== false) throw Error('Unexpected pilot release claim');
  for (const row of pilot.development_deliverables) {
    const tr = document.createElement('tr');
    for (const value of [row.id.replaceAll('-',' '), row.state.replaceAll('-',' ')]) {
      const td = document.createElement('td'); td.textContent = value; tr.append(td);
    }
    body.append(tr);
  }
  for (const row of pilot.components) {
    const option = document.createElement('option'); option.value = row.id; option.textContent = row.id.replaceAll('-',' '); select.append(option);
  }
  const successStatus=`${pilot.digital_packets_verified} connected digital packets verified. Development profiles ${pilot.digital_profiles_executed ? 'executed against current sources' : 'held pending current execution'}. Manufacturing and physical acceptance open.`;
  async function show() {
    const token = ++viewRequest;
    detail.replaceChildren();
    for (const url of objectURLs.splice(0)) URL.revokeObjectURL(url);
    status.textContent='Checking selected pilot evidence…';
    try {
    const row = pilot.components.find(r => r.id === select.value);
    if (!row) throw Error('Select a declared pilot component');
    const receipt = await read('/'+row.packet+'/manifest.json', row.manifest_sha256);
    if (token !== viewRequest) return;
    if (receipt.physical_release !== false) throw Error('Component release scope differs');
    paragraph(row.scope+'.');
    const s = row.summary;
    if (row.id === 'controlled-product') {
      for (let i=0;i<s.profiles.length;i++) {
        const p=s.profiles[i], m=s.mass_ledger[i];
        paragraph(`${p.id}: target tare ${number(m.original_target_tare_kg)} kg; component-accounted tare ${number(m.reconciled_tare_kg)} kg, AW3 ${number(m.reconciled_aw3_kg)} kg. Target overrun ${number(m.target_overrun_kg)} kg. Defined equipment replaces its same-scope allowance once.`);
      }
      const original=s.bay.path.conservative_swept_aabb_collisions.length;
      const redesign=s.bay.redesign.path.conservative_swept_aabb_collisions.length;
      table([['Original removal-path obstructions',original],['Redesigned removal-path obstructions',redesign],['Redesign selected for manufacture','No — splice/load path, handling and qualification holds remain']]);
      if (!await picture('/'+row.packet+'/bay-views.svg','Dimensioned equipped-bay and supported lateral-removal candidate',receipt.files_sha256['bay-views.svg'],token)) return;
      if (!await videoLink('/'+row.packet+'/bay-replacement.mp4','View reference-bay replacement translations (unqualified handling path)',receipt.files_sha256['bay-replacement.mp4'],token)) return;
    } else if (row.id === 'pilot-corridor') {
      table([['Pilot route',number(s.route_length_m/1000)+' km'],['Fleet including spare trains',s.fleet_total],
        ['Modelled walking catchment',number(s.walking_population)],['Synthetic daily potential trips',number(s.synthetic_daily_trips)],
        ['Unquoted capital sensitivity',usd(s.capital_usd)],['Annual operating allowance',usd(s.annual_opex_usd)],
        ['Protected minimum separation',number(s.protected_minimum_separation_s)+' s'],['Maximum observed nominal service gap',number(s.nominal_maximum_observed_gap_s)+' s']]);
      paragraph('The protected separation is a minimum dispatch constraint. It is not an achieved whole-line frequency. Population and demand are estimates, with no observed OD or verified accessible-route acceptance.');
      const f=s.financial_view;
      table([['Debt principal scenario',usd(f.debt_principal_usd)],['Annual debt service scenario',usd(f.annual_debt_service_usd)],
        ['Comparison-only rail capital',usd(f.comparison_capital_usd)],['Comparison-only rail annual operation',usd(f.comparison_annual_opex_usd)]]);
      for (const r of f.annual_cases) paragraph(`Fare $${r.fare_usd.toFixed(2)}, year ${r.year}: debt-service coverage ${number(r.dscr)}; annual additional funding gap ${usd(r.annual_funding_gap_usd)}. Fares, ramp-up and public support are declared scenarios.`);
      if (!await picture('/'+row.packet+'/access.svg','Current pilot stops, open-map walk network and destination centres',receipt.files_sha256['access.svg'],token)) return;
    } else if (row.id === 'launch-options') {
      const best=s.research_recommendation;
      if (best) table([['Research groups per direction',best.candidate.groups_per_direction],['Turns per coil',best.candidate.turns],
        ['Conductor area',number(best.candidate.conductor_area_mm2)+' mm²'],['DC bus',number(best.candidate.dc_bus_v)+' V'],
        ['Winding copper stock',number(best.winding_copper_kg/1000)+' tonnes'],['Winding heat per trip',number(best.copper_heat_kwh_per_trip)+' kWh']]);
      paragraph('The analytical lifetime comparison counts converters, copper, cooling, idle power, maintenance and renewal. Its cheapest instantaneous case has not passed moving local-phase and handover constraints. The coupled candidate uses its own section count and price; motor, converter, grid and regenerated-energy assumptions remain unqualified.');
    } else if (row.id === 'candidate-finance') {
      table([['Counted candidate',s.candidate_name],['Exact candidate configuration',s.configuration_sha256],
        ['Retained base configuration',s.base_configuration_sha256],['Candidate AW3 per car',number(s.controlled_aw3_kg)+' kg'],
        ['Full coupled profile confirmed',s.full_coupled_profile_confirmed],['Implemented candidate model/service screens',s.system_feasible],
        ['Selected for city defaults',s.selected_for_city_defaults]]);
      const changes=s.component_changes;
      paragraph(`Component changes add ${number(changes.incremental_mass_kg_per_car)} kg/car and ${usd(changes.additional_component_cost_usd_per_car)} per car in unquoted planning costs. Mass changes and price ledgers remain separate.`);
      table(changes.rows.map(r=>[r.id.replaceAll('-',' '),`${number(r.mass_change_kg_per_car)} kg/car; ${usd(r.additional_cost_usd_per_car)}/car`]));
      const energy=changes.energy;
      paragraph(`Retained hotel allowance ${number(energy.source_hotel_kw_per_car)} kW/car, with ${number(energy.source_hotel_removed_kw)} kW removed. The separate continuous winding heat ceiling and cooling auxiliaries add ${number(energy.additional_services_kw_per_car)} kW/car; this is an assumed planning ceiling, not measured duty or qualified cooling.`);
      table([['Separate retained base capital',usd(s.base_reference.capital_usd)],['Separate retained base annual operation',usd(s.base_reference.annual_opex_usd)]]);
      paragraph(s.base_reference.role+'.');
      const f=s.financial_view;
      if (f) {
        table([['Counted candidate capital sensitivity',usd(f.capital_usd)],['Standalone capital sensitivity',usd(f.standalone_capital_usd)],
          ['Candidate annual operating allowance',usd(f.annual_opex_usd)],['Capital change from retained base',usd(f.capital_delta_from_base_usd)],
          ['Annual operation change from retained base',usd(f.annual_opex_delta_from_base_usd)],['Candidate debt principal scenario',usd(f.debt_principal_usd)],
          ['Candidate annual debt service',usd(f.annual_debt_service_usd)]]);
        for (const r of f.annual_cases) paragraph(`Candidate fare $${r.fare_usd.toFixed(2)}, year ${r.year}: debt-service coverage ${number(r.dscr)}; annual additional funding gap ${usd(r.annual_funding_gap_usd)}.`);
      } else paragraph('Candidate finance remains held because no exact candidate launch passes its implemented electrical screens. No retained base price is substituted.');
      table(s.system_gates.map(g=>[g.id.replaceAll('-',' '),g.state]));
      paragraph('The retained base and counted candidate have separate identities and costs. Terminal/guidance motion, joined material/load paths, cooling hardware, site data and financial close remain open; no city-default adoption or physical qualification follows from these calculations.');
      if (!await picture('/'+row.packet+'/overview.svg','Separate counted candidate capital, operating cost and exact-configuration holds',receipt.files_sha256['overview.svg'],token)) return;
      const media=s.assembly_media;
      if (!media || media.configuration_sha256!==s.configuration_sha256 || media.physical_accepted!==false) throw Error('Current candidate media identity differs');
      const mediaPath=kind=>{
        const name=media.files[kind];
        if (typeof name!=='string' || !/^[a-z0-9][a-z0-9.-]*$/.test(name)) throw Error('Unsafe current candidate media path');
        return ['/'+row.packet+'/'+name,receipt.files_sha256[name]];
      };
      const [poster,posterDigest]=mediaPath('poster');
      if (!await picture(poster,'Exact larger-winding candidate, supported lateral replacement translation; handling acceptance open',posterDigest,token)) return;
      const [video,videoDigest]=mediaPath('video');
      if (!await videoLink(video,'View current-candidate replacement translations (unqualified handling path)',videoDigest,token)) return;
    } else if (row.id === 'coupled-actuators') {
      table([['Counted repair model feasibility',s.model_feasibility],['Full-length candidate satisfies all implemented screens',s.any_full_candidate_feasible],
        ['Fault controls held',s.all_negative_controls_held],['Independent actual module-force screen',pilot.coupled_actual_module_force.state],
        ['Actual module upward force',number(pilot.coupled_actual_module_force.observed_peak_n)+' N'],['Declared study force limit',number(pilot.coupled_actual_module_force.limit_n)+' N']]);
      if (!Array.isArray(s.holds) || !s.holds.length || !Array.isArray(s.repair_candidates) || !s.repair_candidates.length) throw Error('Coupled magnetic geometry holds are missing');
      paragraph('Open geometry and qualification holds:');
      const holds=document.createElement('ul');
      for (const hold of s.holds) {const li=document.createElement('li');li.textContent=hold;holds.append(li);}
      detail.append(holds);
      for (const repair of s.repair_candidates) {
        const geometry=repair.magnetic_geometry;
        if (!geometry || !Number.isFinite(geometry.assumed_gap_pole_area_m2) || !Number.isFinite(geometry.winding_inner_aperture_m2)) throw Error('Repair magnetic geometry identity is missing');
        paragraph(`Magnetic geometry for ${repair.body_variant} / ${repair.winding_variant}:`);
        table([['Geometry reconciliation',geometry.state],['Assumed gap pole area',number(geometry.assumed_gap_pole_area_m2*1e6)+' mm²'],
          ['Winding inner aperture',number(geometry.winding_inner_aperture_m2*1e6)+' mm²'],
          ['Core neck area',geometry.core_neck_area_m2==null?'Unreconciled':number(geometry.core_neck_area_m2*1e6)+' mm²'],
          ['Qualified flux split',geometry.qualified_flux_split==null?'Unqualified':geometry.qualified_flux_split]]);
        paragraph(geometry.reason);
      }
      paragraph('Current-loop execution is coupled to the declared magnetic plant and moving bodies. Failed reference cases and counted repair alternatives remain separate; measured maps, lateral dynamics and hardware timing remain open.');
      if (!await picture('/'+row.packet+'/overview.svg','Coupled current, gap and fault-study results',receipt.files_sha256['overview.svg'],token)) return;
      if (!await picture('/'+row.packet+'/candidate-bay.svg','Larger-winding candidate bay; its own calculated access bounds, separate from the reference-bay video',receipt.files_sha256['candidate-bay.svg'],token)) return;
    } else if (row.id === 'native-lifecycle') {
      table([['Current product positions',s.positions],['Recorded simulated serial events',s.events],['Native business campaign',s.native.state]]);
      if (s.native.state==='executed-current' && !await picture('/'+row.packet+'/native-workbench.png','Actual authenticated current-maglev pilot Workbench with three product histories',receipt.files_sha256['native-workbench.png'],token)) return;
      const native=document.createElement('a');native.href='http://127.0.0.1:18088/maglev-pilot';native.textContent='Open isolated authenticated native pilot (when running locally)';detail.append(native);
    } else if (row.id === 'resource-delivery') {
      if (!await picture('/'+row.packet+'/overview.svg','Resource-constrained delivery cases with actual task precedence and finite capacity',receipt.files_sha256['overview.svg'],token)) return;
    } else if (row.id === 'assurance-profiles') {
      table(s.profiles.map(r=>[r.id,r.digital_state.replaceAll('-',' ')]));
      paragraph('Formal checks cover declared symbolic refusal/time properties. All independent physical acceptance remains open.');
    } else if (row.id === 'capability-migration') {
      table(Object.entries(s.state_counts).map(([k,v])=>[k.replaceAll('-',' '),v]));
      paragraph('Each historical feature has an accountable function, disposition, current evidence and a stated acceptance test. Missing functions remain named.');
    } else {
      paragraph('The source-bound packet below contains the detailed results, adverse cases, quantities and outstanding gates for this part of the pilot.');
    }
    if (token !== viewRequest) return;
    const link=document.createElement('a'); link.href='/'+row.packet+'/README.md'; link.textContent='Inspect results, procedures and limitations'; detail.append(link);
    status.textContent=successStatus;
    } catch (error) {
      if (token !== viewRequest) return;
      detail.replaceChildren();
      for (const url of objectURLs.splice(0)) URL.revokeObjectURL(url);
      status.textContent=error.message;
    }
  }
  select.disabled=false;
  select.addEventListener('change',()=>{void show();});
  await show();
} catch (error) { status.textContent=error.message; select.disabled=true; }
