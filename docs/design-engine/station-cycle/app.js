'use strict';

(() => {
  const $ = id => document.getElementById(id);
  const finite = x => typeof x === 'number' && Number.isFinite(x);
  const fmt = (x, digits = 1) => finite(x) ? x.toLocaleString('en', {minimumFractionDigits: digits, maximumFractionDigits: digits}) : 'Unknown';
  const unit = (x, suffix, digits = 1) => finite(x) ? `${fmt(x, digits)} ${suffix}` : 'Unknown';
  const mj = x => finite(x) ? `${fmt(x / 1e6, 2)} MJ` : 'Unknown';
  const usd = x => finite(x) ? `$${fmt(x / 1e6, 2)}m` : 'Unknown';
  const words = x => String(x || 'Not evaluated').replaceAll('_', ' ').replaceAll('-', ' ');
  const typeName = x => ({steel:'Steel spring',hydraulic:'Hydraulic accumulator'})[x] || 'Bare launcher';
  const releaseKeys = ['physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority','selected_reference_changed'];
  const scopes = ['rolling-stock','guideway','stations-power','factory-tooling','construction','land-utilities-depot','fleet','energy','operations','maintenance','renewals','recovery','reliability','disposal'];
  let study = null;
  let selected = 0;
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }
  function replace(id, nodes) { $(id).replaceChildren(...nodes); }
  function secondary(parent, text) { parent.append(el('span', text, 'secondary')); }
  function cell(value, detail, className = 'amount') {
    const node = el('td'); node.append(el('span', value, className));
    if (detail) secondary(node, detail);
    return node;
  }
  function pill(text, style = '') { return el('span', text, `pill ${style}`); }
  function details(id, rows) { replace(id, rows.flatMap(([name,value]) => [el('dt',name),el('dd',value)])); }
  function empty(body, message, count) { const td = el('td',message,'empty');td.colSpan=count;const tr=el('tr');tr.append(td);body.append(tr); }
  function range(amounts) { return amounts ? `${usd(amounts.low)} / ${usd(amounts.high)}` : 'Unknown / Unknown'; }
  function title(row) { return `${row.name} · ${fmt(row.speed_cap_km_h,0)} km/h cap · ${row.storage_enabled ? 'recovery on' : 'recovery off'}`; }
  function verdict(row) {
    if (row.scheduled_legs > 0 && row.arrived_legs === row.scheduled_legs) return ['All scheduled legs berthed','calculated'];
    if (String(row.state).includes('held')) return ['Held · unresolved journey',''];
    return [words(row.state),''];
  }
  function maxJerk(row) {
    const values = (row.legs || []).map(x => x.journey?.maximum_absolute_jerk_m_s3).filter(finite);
    return values.length ? Math.max(...values) : null;
  }
  function validate(data) {
    if (data?.schema !== 'osr-station-cycle-summary/1' || !/^[a-f0-9]{64}$/.test(data.study_id)
      || !Array.isArray(data.rows) || !Array.isArray(data.faults) || !data.brief) throw new Error('The exported record does not match the station-cycle summary contract.');
    if (releaseKeys.some(key => data[key] === true)) throw new Error('This research viewer cannot display an approved or selected operating design. Inspect the original record.');
    for (const row of [...data.rows,...data.faults]) {
      if (!row || !/^[a-f0-9]{64}$/.test(row.candidate_id) || typeof row.name !== 'string'
        || !Array.isArray(row.legs) || !row.ledger
        || !(row.cold_start_zero_energy === true && row.ledger.initial_store_j === 0
             || row.experiment === 'initially-full' && row.cold_start_zero_energy === false && row.ledger.initial_store_j > 0 && data.faults.includes(row))
        || releaseKeys.some(key => row[key] === true)) {
        throw new Error('A cycle lacks its candidate identity, declared initial energy or research-only evidence scope.');
      }
    }
  }
  async function load() {
    $('loading').hidden=false;$('load-error').hidden=true;$('study-content').hidden=true;
    try {
      const response = await fetch('summary.json',{cache:'no-cache',credentials:'same-origin'});
      if (!response.ok) throw new Error(`summary.json returned HTTP ${response.status}.`);
      const data = await response.json();validate(data);study=data;selected=0;
      renderBrief();populate();renderTable();renderSelected();renderLimitations();
      $('study-id').textContent=study.study_id;$('study-content').hidden=false;
    } catch (error) {
      $('error-message').textContent=error instanceof Error ? error.message : 'The study could not be loaded.';
      $('load-error').hidden=false;
    } finally { $('loading').hidden=true; }
  }
  function renderBrief() {
    const b=study.brief;
    const distance=b.station_spacing_m ?? b.distance_m ?? b.route_m;
    $('metric-distance').textContent=finite(distance) ? `${fmt(distance/1000,1)} km` : 'Declared pilot';
    $('metric-people').textContent=unit(b.normal_people ?? b.passengers,'places',0);
    const counts=[...new Set(study.rows.map(x=>x.scheduled_legs).filter(finite))];
    $('metric-legs').textContent=counts.length ? `${counts.join(' / ')} legs` : 'Not evaluated';
    const request=study.rows.find(x=>finite(x.service?.requested_headway_s))?.service?.requested_headway_s;
    $('service-warning').replaceChildren(el('strong','Requested service is not yet demonstrated. '),
      document.createTextNode(`The comparison runs a serial shuttle${finite(request) ? ` against a ${fmt(request,0)} s full-fleet headway target` : ''}. Serial journey completion does not establish parallel fleet operations, charging capacity or passenger throughput.`));
  }
  function populate() {
    replace('candidate-picker',study.rows.map((row,i)=>{const option=el('option',title(row));option.value=String(i);return option;}));
    const speeds=[...new Set(study.rows.map(row=>row.speed_cap_km_h).filter(finite))].sort((a,b)=>a-b);
    replace('speed-filter',[el('option','All caps'),...speeds.map(speed=>{const option=el('option',`${fmt(speed,0)} km/h`);option.value=String(speed);return option;})]);
    $('speed-filter').firstElementChild.value='all';
  }
  function matches(row) {
    const technology=$('technology-filter').value;const recovery=$('recovery-filter').value;const speed=$('speed-filter').value;
    return (technology==='all' || (technology==='baseline' ? row.technology===null : row.technology===technology))
      && (recovery==='all' || row.storage_enabled===(recovery==='on'))
      && (speed==='all' || Math.abs(row.speed_cap_km_h-Number(speed))<1e-8);
  }
  function renderTable() {
    const body=$('comparison-body');body.replaceChildren();
    const rows=study.rows.map((row,i)=>({row,i})).filter(x=>matches(x.row));
    $('results-count').textContent=`${rows.length} of ${study.rows.length} nominal configurations`;
    for (const {row,i} of rows) {
      const tr=el('tr');if(i===selected)tr.className='selected-row';
      const first=el('td');first.append(el('strong',row.name));
      secondary(first,`${typeName(row.technology)} · ${row.storage_enabled ? 'Recovery on' : 'Recovery off'} · ${unit(row.speed_cap_km_h,'km/h cap',0)}`);
      secondary(first,`${mj(row.capacity_j)} store capacity`);
      const button=el('button','Inspect cycle','inspect');button.type='button';button.dataset.index=String(i);
      button.addEventListener('click',()=>select(i));first.append(button);
      const outcome=el('td');outcome.append(pill(...verdict(row)));
      secondary(outcome,`${fmt(row.arrived_legs,0)} / ${fmt(row.scheduled_legs,0)} calculated berths · ${fmt(row.executed_legs,0)} executed`);
      secondary(outcome,`${unit(maxJerk(row),'m/s³',3)} maximum reported moving jerk`);
      const ledger=row.ledger;const cost=row.cost || {};
      const cap=cell(usd(cost.installed_capital_usd?.base),range(cost.installed_capital_usd),'cost-base');
      const whole=cell(usd(cost.whole_life_NPV_usd?.base),range(cost.whole_life_NPV_usd),'cost-base');
      if (!finite(cost.whole_life_NPV_usd?.base)) secondary(whole,`${usd(cost.known_lifecycle_NPV_usd?.base)} known subtotal; complete NPV unknown`);
      tr.append(first,outcome,cell(mj(ledger.capture_work_j),`${mj(ledger.delivered_launch_work_j)} returned to train`),
        cell(mj(ledger.grid_traction_energy_j),`${mj(ledger.reset_grid_energy_j)} reset electricity`),cap,whole);body.append(tr);
    }
    if (!rows.length) empty(body,'No nominal configuration matches these filters. Other designs and held cases remain in the source.',6);
  }
  function select(index) {
    if (!Number.isInteger(index) || !study.rows[index]) return;
    selected=index;$('candidate-picker').value=String(index);renderTable();renderSelected();
  }
  function renderSelected() {
    const row=study.rows[selected];
    if (!row) { replace('energy-flow',[el('p','No nominal source-linked cycle is available.','empty')]);return; }
    replace('selected-heading',[el('h3',title(row)),pill(...verdict(row))]);
    const e=row.ledger;
    const steps=[['Train to collector',e.capture_work_j,'Actual allocated capture work'],
      ['Into the store',e.stored_capture_j,`${mj(e.capture_loss_j)} capture loss`],
      ['Back to the train',e.delivered_launch_work_j,`${mj(e.release_loss_j)} release loss`],
      ['Held at cycle end',e.final_store_j,`${mj(e.storage_leakage_j)} storage leakage`]];
    replace('energy-flow',steps.map(([name,value,note])=>{const card=el('article',null,'flow-step');card.append(el('span',name),el('strong',mj(value)),el('p',note));return card;}));
    details('storage-details',[
      ['Technology',typeName(row.technology)],['Recovery',row.storage_enabled ? 'Enabled under declared bounds' : 'Disabled; no capture or release credit'],
      ['Capacity',mj(row.capacity_j)],['Initial energy',mj(e.initial_store_j)],
      ['Active material mass',unit(row.sizing?.active_mass_kg,'kg',0)],
      ['Reserved storage envelope',unit(row.sizing?.reserve_envelope_m3 ?? row.sizing?.envelope_volume_m3 ?? row.sizing?.volume_m3,'m³',2)],
      ['Reset electricity',mj(e.reset_grid_energy_j)],['Grid traction',mj(e.grid_traction_energy_j)],
      ['Scoped grid subtotal incl. HVAC/charging and return allowance',mj(row.energy_reconciliation?.known_grid_subtotal_j)]]);
    const balances=[['Moving-jerk target screen',row.advisory_screen===true ? 'Meets declared nominal targets' : 'Target or journey unresolved'],['Capture loss',mj(e.capture_loss_j)],['Release loss',mj(e.release_loss_j)],
      ['Storage leakage',mj(e.storage_leakage_j)],['Independent friction-brake heat',mj(e.friction_brake_heat_j)],
      ['Storage balance residual',unit(e.storage_balance_residual_j,'J',3)],
      ['Train + store balance residual',unit(e.train_and_storage_balance_residual_j,'J',3)]];
    if (finite(e.spill_j ?? e.capture_spill_j)) balances.splice(3,0,['Unstored/spilled capture',mj(e.spill_j ?? e.capture_spill_j)]);
    details('balance-details',balances);
    $('station-states').textContent=Array.isArray(row.station_states) && row.station_states.length ? JSON.stringify(row.station_states,null,2) : 'Station end states are unavailable in this summary; inspect the complete study.';
    details('identities',[['Physical candidate',row.candidate_id],['Study',study.study_id],
      ['Experiment',row.experiment || 'Nominal sequence'],['Cycle evaluation',row.evaluation_id || 'See complete study']]);
    renderLegs(row);renderCosts(row);renderFaults();
  }
  function renderLegs(row) {
    const service=row.service || {};
    $('service-details').replaceChildren(el('strong',`${unit(service.modeled_direction_headway_s,'s',0)} modeled serial direction headway. `),
      document.createTextNode(`${unit(service.requested_headway_s,'s',0)} requested full-fleet headway. ${service.concurrent_service_verified===true ? 'Inspect separate supporting service evidence.' : 'Concurrent service is not verified; no complete passenger-service verdict follows.'} Captured energy belongs to its actual station and clock.`));
    const body=$('legs-body');body.replaceChildren();
    for (const [i,leg] of row.legs.entries()) {
      const tr=el('tr');const first=el('td');first.append(el('strong',`Leg ${i+1}`));
      secondary(first,`${leg.departure_station_id} → ${leg.arrival_station_id}`);
      const journey=leg.journey;const outcome=el('td');outcome.append(pill(words(leg.state)));
      if (leg.hold_reason) secondary(outcome,leg.hold_reason);
      tr.append(first,cell(unit(leg.departure_time_s,'s'),`${unit(leg.initial_position_m,'m',3)} actual starting coordinate`),outcome,
        cell(unit(journey?.elapsed_s,'s'),`${unit(journey?.final_position_m,'m',3)} actual stop coordinate`),
        cell(unit(journey?.maximum_absolute_jerk_m_s3,'m/s³',3)),
        cell(mj(leg.energy?.capture_work_j),`${mj(leg.energy?.delivered_launch_work_j)} returned`));body.append(tr);
    }
    if (!row.legs.length) empty(body,'No leg was executed. The hold is preserved; no motion trace is invented.',6);
    replace('leg-picker',row.legs.map((leg,i)=>{const option=el('option',`Leg ${i+1} · ${leg.departure_station_id} → ${leg.arrival_station_id} · ${words(leg.state)}`);option.value=String(i);return option;}));
    const available=row.legs.findIndex(leg=>Array.isArray(leg.journey?.trace) && leg.journey.trace.length>1);
    if (available>=0) $('leg-picker').value=String(available);
    renderChart();
  }
  function renderChart() {
    const row=study.rows[selected];const leg=row?.legs[Number($('leg-picker').value)];
    const trace=leg?.journey?.trace;
    const points=(Array.isArray(trace) ? trace : []).filter(p=>finite(p.position_m) && finite(p.speed_m_s));
    if (points.length<2) {
      replace('motion-chart',[el('p','No source-linked motion trace is available for this leg. Held and unexecuted legs do not become invented curves.','empty')]);
      $('chart-description').textContent=leg?.hold_reason || 'Inspect the retained leg result in the complete study.';return;
    }
    const ns='http://www.w3.org/2000/svg';const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox','0 0 850 290');svg.classList.add('chart-svg');svg.setAttribute('role','img');
    svg.setAttribute('aria-label','Source-linked train speed versus route position');
    const titleNode=document.createElementNS(ns,'title');titleNode.textContent='Actual integrated speed versus route position';svg.append(titleNode);
    const x0=Math.min(0,...points.map(p=>p.position_m));const x1=Math.max(x0+1,...points.map(p=>p.position_m));
    const ymax=Math.max(10,...points.map(p=>p.speed_m_s*3.6))*1.12;
    const x=value=>65+(value-x0)/(x1-x0)*755;const y=value=>240-value/ymax*215;
    function shape(tag,attrs,text) {const node=document.createElementNS(ns,tag);for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));if(text)node.textContent=text;svg.append(node);return node;}
    for(let i=0;i<=4;i++) {
      const yp=ymax*i/4;shape('line',{x1:65,x2:820,y1:y(yp),y2:y(yp),class:'chart-grid'});
      shape('text',{x:55,y:y(yp)+4,'text-anchor':'end'},fmt(yp,0));
      const xp=x0+(x1-x0)*i/4;shape('text',{x:x(xp),y:260,'text-anchor':'middle'},fmt(xp,0));
    }
    shape('line',{x1:65,x2:820,y1:240,y2:240,class:'chart-axis'});
    shape('text',{x:65,y:15},'Speed (km/h)');shape('text',{x:820,y:282,'text-anchor':'end'},'Route position (m)');
    shape('path',{class:'motion-line',d:points.map((p,i)=>`${i?'L':'M'}${x(p.position_m).toFixed(2)},${y(p.speed_m_s*3.6).toFixed(2)}`).join(' ')});
    replace('motion-chart',[svg]);
    $('chart-description').textContent=`${points.length} retained source points. ${unit(leg.initial_position_m,'m',3)} starting coordinate; ${unit(leg.journey.final_position_m,'m',3)} final coordinate. The trace is not a measured run or contact-dynamics validation.`;
  }
  function renderCosts(row) {
    const cost=row.cost || {};
    const cards=[['Installed capital',cost.installed_capital_usd,'Pilot total'],
      ['Complete whole-life NPV',cost.whole_life_NPV_usd,'Unknown if required service energy is unresolved'],
      ['Known lifecycle subtotal',cost.known_lifecycle_NPV_usd,'Includes only priced declared accounts']];
    replace('cost-cards',cards.map(([name,values,note])=>{const card=el('article',null,'cost-card');card.append(el('span',name),el('strong',usd(values?.base)),el('span',range(values),'range'),el('span',note));return card;}));
    const rows=Array.isArray(cost.scopes) ? cost.scopes : [];
    const byscope=new Map(rows.map(r=>[r.scope,r]));
    $('cost-coverage').textContent=`${byscope.size} of 14 account scopes supplied. Capital and lifecycle figures are the selected candidate’s calculated scope; a known subtotal is not a complete investment price.`;
    const body=$('cost-body');body.replaceChildren();
    for (const scope of scopes) {
      const source=byscope.get(scope);const tr=el('tr');tr.append(cell(words(scope),null,''));
      for(const c of ['low','base','high'])tr.append(cell(usd(source?.total_NPV_usd?.[c])));
      tr.append(cell(source ? usd(source.known_NPV_usd?.base) : 'Not supplied',source ? 'Base scenario known amount' : 'Missing scope remains unknown'));body.append(tr);
    }
  }
  function renderFaults() {
    const chosen=study.rows[selected];const all=$('fault-filter').value==='all';
    const faults=study.faults.filter(row=>all || row.candidate_id===chosen?.candidate_id);
    $('fault-count').textContent=`${faults.length} retained fault/sensitivity cycles${all ? ' across all configurations' : ' for this physical configuration'}. Failures remain part of the comparison.`;
    const body=$('fault-body');body.replaceChildren();
    for(const row of faults) {
      const first=el('td');first.append(el('strong',row.name));secondary(first,words(row.experiment));
      secondary(first,`${row.storage_enabled ? 'Recovery on' : 'Recovery off'} · ${unit(row.speed_cap_km_h,'km/h cap',0)}`);
      const state=el('td');state.append(pill(words(row.state)));
      const hold=row.legs.find(leg=>leg.hold_reason)?.hold_reason;
      const tr=el('tr');tr.append(first,state,cell(`${fmt(row.arrived_legs,0)} / ${fmt(row.scheduled_legs,0)}`),
        cell(mj(row.ledger.reset_grid_energy_j)),cell(hold || 'Conditional result; inspect full fault inputs and sequence.',null,''));body.append(tr);
    }
    if(!faults.length)empty(body,'No matching fault results are supplied. Missing tests do not count as passed.',5);
  }
  function renderLimitations() { replace('limitations',(study.limitations || []).map(text=>el('li',text))); }
  $('filters').addEventListener('change',()=>study&&renderTable());
  $('filters').addEventListener('reset',()=>setTimeout(()=>study&&renderTable(),0));
  $('candidate-picker').addEventListener('change',()=>select(Number($('candidate-picker').value)));
  $('leg-picker').addEventListener('change',renderChart);
  $('fault-filter').addEventListener('change',()=>study&&renderFaults());
  $('retry').addEventListener('click',load);
  load();
})();
