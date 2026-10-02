const params = new URLSearchParams(location.search);
const city = params.get('city') || 'samawah';
const environment = params.get('environment') || 'simulation';
const subject = params.get('selected_asset') || params.get('subject') || '';
const element = (tag, text) => { const node = document.createElement(tag); node.textContent = text; return node; };
const labels = {requirements:'Requirements & RAMS allocation',design_verification:'Design verification',physical_qualification:'Physical qualification',integration:'Integration',independent_review:'Independent review',operating_conditions:'Operating conditions'};
const format = value => Number(value).toLocaleString('en-GB',{maximumSignificantDigits:3});
const range = (values, unit='') => Array.isArray(values) ? `${format(values[0])}–${format(values[1])}${unit ? ' '+unit : ''}` : 'Input evidence unresolved';
function study(title, value, limitation) {
  const card=element('article',''); card.append(element('h3',title),element('p',value));
  card.querySelector('p').className='value';
  const note=element('p',limitation);note.className='limit';card.append(note);
  document.querySelector('#quantitative').append(card);
}
try {
  const response=await fetch('/api/assurance/readiness?'+new URLSearchParams({city,environment,subject}));
  const payload=await response.json();
  if(!response.ok)throw Error(payload.error || 'Readiness evidence unavailable');
  if(payload.requested_context.city!==city || payload.requested_context.environment!==environment || payload.requested_context.subject!==subject)throw Error('Readiness evidence does not match the selected context');
  const report=payload.reference_package;
  const scope=document.querySelector('#scope');
  if(!report){scope.textContent=`No qualification package for ${city} / ${environment}${subject ? ' / '+subject : ''}.`;throw Error('Selected configuration has no decision-ready evidence package.');}
  const reference=report.scope.kind==='reference';
  if(!reference && (report.scope.city!==city || report.scope.environment!==environment || (subject && subject!==report.subject_id)))throw Error('Qualification package belongs to another configuration');
  scope.textContent=reference ? `Reference battery-cooling package · no deployment qualification for ${city} / ${environment}${subject ? ' / '+subject : ''}.` : `${city} / ${environment} · ${report.title}`;
  scope.classList.toggle('reference',reference);
  document.querySelector('#configuration').textContent=`${report.configuration_id} · ${report.configuration_fingerprint.slice(0,16)}`;
  document.querySelector('#acceptedUse').textContent=payload.deployment_accepted_use || 'No authenticated acceptance for this deployment';
  document.querySelector('#changes').textContent=report.changes_since_decision.replaceAll('-',' ');
  for(const [key,row] of Object.entries(report.stages)){
    const card=element('article','');card.dataset.stage=key;card.append(element('h2',labels[key] || key));
    const state=element('span',row.state==='blocked'?'Unresolved':'Evidence current for review');state.className='state';card.append(state);
    const details=element('details','');details.append(element('summary',`${row.blockers.length} unresolved findings`));
    const list=element('ul','');for(const value of row.blockers)list.append(element('li',value));details.append(list);card.append(details);
    document.querySelector('#stages').append(card);
  }
  const q=report.quantitative_analysis;
  document.querySelector('#basis').textContent=`Evidence basis: ${q.evidence_basis.replaceAll('-',' ')}. These ranges expose input uncertainty; they are not confidence intervals.`;
  study('Cooling-loss time to temperature limit',range(q.thermal.time_to_limit_s,'seconds')+(q.thermal.some_cases_do_not_reach_limit?' · some cases never reach the limit':''),q.thermal.limitations);
  study('Combined failure exposure',range(q.fault_tree.mission_top_event_probability),`${q.top_event} ${q.fault_tree.unknown_events?.length || 0} event inputs remain unknown. Shared events appear once in each Boolean combination.`);
  const availability=q.fault_tree.steady_state_availability;
  study('Steady-state function unavailability',range(Array.isArray(availability) ? [1-availability[1],1-availability[0]] : null),q.fault_tree.limitations);
  const inspectionLimit=q.inspection.maximum_interval_h_at_upper_rate;
  study('Average latent fault exposure',range(q.inspection.average_latent_exposure),
    (q.inspection.limitations || 'Inspection and diagnostic coverage inputs unresolved.')+
    (Number.isFinite(inspectionLimit) ? ` Screening inspection interval at the upper rate: ${format(inspectionLimit)} hours.` : ''));
  study('Maintenance capacity',`${range(q.maintenance.repair_crews,'concurrent crews')} · ${range(q.maintenance.minimum_spares,'spares')}`,q.maintenance.limitations || 'Repair and replenishment inputs unresolved.');
  study('One braking channel unavailable',range(q.degraded_braking.maximum_speed_km_h,'km/h'),q.degraded_braking.limitations || 'Validated braking envelope unresolved.');
  const comparison=element('table','');const heading=element('tr','');
  for(const label of ['Alternative','Illustrative cost units','Combined failure exposure','Cooling-loss time (s)'])heading.append(element('th',label));comparison.append(heading);
  for(const option of q.design_options){const row=element('tr','');row.append(element('td',option.title),element('td',format(option.illustrative_cost)),element('td',range(option.top_event_probability)),element('td',range(option.time_to_limit_s)));comparison.append(row);}
  document.querySelector('#alternatives').append(comparison);
  document.querySelector('#measurements').textContent=report.measurement_results.length ? `${report.measurement_results.length} recorded measurement runs; qualification requires calibration, configuration and review checks.` : 'No physical rig measurements supplied. Normal, pump-loss, leak, masked-sensor, charging and shared-supply tests remain planned.';
  for(const run of report.measurement_results){const card=element('article','');card.append(element('h3',run.run_id),element('p',`${run.state} · model discrepancy ${run.model_maximum_error_c===null?'unresolved':format(run.model_maximum_error_c)+' °C'}`));document.querySelector('#runs').append(card);}
  for(const finding of report.manufacturing_blockers)document.querySelector('#manufacturing').append(element('li',finding));
} catch(error) {
  document.querySelector('#scope').textContent=error.message;
  document.querySelector('#acceptedUse').textContent='Acceptance unavailable';
  document.querySelector('#stages').replaceChildren();document.querySelector('#quantitative').replaceChildren();document.querySelector('#alternatives').replaceChildren();
}
