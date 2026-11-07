'use strict';

(() => {
  const $ = (id) => document.getElementById(id);
  const families = [
    {id: 'cable', name: 'Cable / mechanical launch', description: 'Station drive, finite launch window and explicit reset energy.'},
    {id: 'compact-LIM', name: 'Compact linear motor', description: 'Retained proposal; an attainable operating force map is required.'},
    {id: 'hybrid', name: 'Mechanical + LIM', description: 'Retained proposal; combined force and engagement evidence is required.'},
    {id: 'powered-wheel', name: 'Powered wheels', description: 'Onboard-traction research control; reference remains passive.'}
  ];
  const releaseKeys = ['physical_accepted', 'engineering_accepted', 'manufacturing_release', 'operating_release', 'movement_authority', 'selected_reference_changed'];
  let study = null;
  let finalists = [];
  const number = (value) => typeof value === 'number' && Number.isFinite(value);
  const sameNumber = (a, b) => number(a) && number(b) && Math.abs(a - b) <= 1e-8;
  const fmt = (value, digits = 1) => number(value) ? value.toLocaleString('en', {maximumFractionDigits: digits, minimumFractionDigits: digits}) : 'Unknown';
  const unit = (value, suffix, digits = 1) => number(value) ? `${fmt(value, digits)} ${suffix}` : 'Not evaluated';
  const usd = (value) => number(value) ? `$${fmt(value / 1e6, 2)}m` : 'Unknown';
  const familyName = (id) => families.find((f) => f.id === id)?.name || String(id || 'Unknown family');
  const short = (id) => typeof id === 'string' ? `${id.slice(0, 12)}…` : 'Unknown';
  const label = (key) => String(key).replaceAll('_', ' ').replaceAll('-', ' ');
  function node(tag, text, className) {
    const e = document.createElement(tag);
    if (text !== undefined && text !== null) e.textContent = String(text);
    if (className) e.className = className;
    return e;
  }
  function replace(id, children) { $(id).replaceChildren(...children); }
  function dl(entries, className) {
    const e = node('dl', null, className);
    for (const [key, value] of entries) e.append(node('dt', key), node('dd', value));
    return e;
  }
  function pill(text, state) { return node('span', text, `pill ${state || ''}`); }
  function outcome(row) {
    if (row.outline_screen) return ['Outline screens met', 'calculated'];
    if (row.numerical_arrival) return ['Numerical arrival · screen open', 'held'];
    if (row.numerical_state?.startsWith('held')) return ['Held · evidence required', 'held'];
    return [row.numerical_state || 'Not evaluated', 'held'];
  }
  function cell(primary, secondary, className) {
    const td = node('td');
    td.append(node('span', primary, className || 'cell-number'));
    if (secondary) td.append(node('span', secondary, 'cell-secondary'));
    return td;
  }
  function normalTrace(finalist) {
    const trace = finalist?.trace;
    const points = Array.isArray(trace) ? trace : trace?.points;
    return Array.isArray(points) ? points.filter((p) => number(p.position_m) && number(p.speed_m_s)) : [];
  }
  function requestOf(f) { return f?.request || {}; }
  function rowOf(f) {
    return study.rows.find((r) => r.candidate_id === f?.candidate_id && sameNumber(r.speed_cap_km_h, f?.speed_cap_km_h) && (!number(requestOf(f).distance_m) || sameNumber(r.distance_m, requestOf(f).distance_m)));
  }
  function finalName(f) {
    const row = rowOf(f);
    return `${f.name || row?.name || familyName(f.family || row?.family)} · ${fmt(f.speed_cap_km_h, 0)} km/h cap · ${fmt((requestOf(f).distance_m || row?.distance_m) / 1000)} km`;
  }
  function finiteMin(values) { const v = values.filter(number); return v.length ? Math.min(...v) : null; }
  function finiteMax(values) { const v = values.filter(number); return v.length ? Math.max(...v) : null; }

  function validate(data) {
    if (!data || typeof data.study_id !== 'string' || !Array.isArray(data.rows) || !data.brief) throw new Error('The exported study does not match the station-pair summary contract.');
    for (const row of data.rows) {
      if (!row || typeof row.candidate_id !== 'string' || typeof row.family !== 'string') throw new Error('A comparison row is missing its physical candidate or family identity.');
      if (releaseKeys.some((key) => row[key] === true)) throw new Error('The supplied record claims a release or reference change outside this research viewer’s scope. Inspect the source record.');
    }
  }
  async function load() {
    $('loading').hidden = false;
    $('load-error').hidden = true;
    $('study-content').hidden = true;
    try {
      const response = await fetch('summary.json', {cache: 'no-cache', credentials: 'same-origin'});
      if (!response.ok) throw new Error(`summary.json returned HTTP ${response.status}.`);
      const data = await response.json();
      validate(data);
      study = data;
      finalists = (Array.isArray(data.finalists) ? data.finalists : []).filter((f) => f && typeof f.candidate_id === 'string');
      renderBrief(); renderFamilies(); renderTable(); renderControlComparison(); populateFinalists(); renderMass(); renderLimitations(); renderDownloads();
      $('study-id').textContent = study.study_id;
      $('study-content').hidden = false;
    } catch (error) {
      $('error-message').textContent = error instanceof Error ? error.message : 'The study could not be read.';
      $('load-error').hidden = false;
    } finally { $('loading').hidden = true; }
  }
  function renderBrief() {
    const b = study.brief;
    const spacings = [...new Set(study.rows.map((r) => r.distance_m).filter(number))].sort((a, z) => a - z);
    $('brief-distance').textContent = spacings.map((v) => fmt(v / 1000, v % 1000 ? 1 : 0)).join(' / ') + ' km';
    $('brief-demand').textContent = fmt(b.peak_demand_pphpd, 0);
    const headways = [...new Set(study.rows.map((r) => r.headway_s).filter(number))];
    $('brief-headway').textContent = headways.length ? headways.map((v) => fmt(v, 0)).join(' / ') + ' s' : 'Unknown';
    $('brief-occupancy').textContent = `${fmt(b.planning_occupancy * 100, 0)}% planning occupancy · calculated`;
    $('brief-people').textContent = `${fmt(b.normal_people, 0)} places`;
  }
  function renderFamilies() {
    replace('families', families.map((f) => {
      const rows = study.rows.filter((r) => r.family === f.id);
      const arrivals = rows.filter((r) => r.numerical_arrival).length;
      const article = node('article', null, 'family-card');
      article.append(node('h3', f.name), node('p', f.description));
      const status = node('p', null, 'family-state');
      status.append(pill(rows.length ? `${arrivals} / ${rows.length} numerical arrivals` : 'No evaluated rows', arrivals ? 'calculated' : 'held'));
      article.append(status); return article;
    }));
  }
  function selectedRows() {
    return study.rows.filter((r) =>
      ($('distance-filter').value === 'all' || sameNumber(r.distance_m, Number($('distance-filter').value))) &&
      ($('speed-filter').value === 'all' || sameNumber(r.speed_cap_km_h, Number($('speed-filter').value))) &&
      ($('family-filter').value === 'all' || r.family === $('family-filter').value) &&
      ($('state-filter').value === 'all' || ($('state-filter').value === 'arrived' && r.numerical_arrival) || ($('state-filter').value === 'screen' && r.outline_screen) || ($('state-filter').value === 'held' && !r.numerical_arrival)));
  }
  function renderTable() {
    const rows = selectedRows();
    $('results-count').textContent = `${rows.length} of ${study.rows.length} calculated scenarios`;
    replace('comparison-body', rows.map((r) => {
      const tr = node('tr');
      const design = node('td');
      design.append(node('strong', r.name || familyName(r.family)), node('span', `${fmt(r.distance_m / 1000)} km · ${unit(r.headway_s, 's headway', 0)} · ${unit(r.trainsets, 'trainsets', 0)}`, 'cell-secondary'));
      design.append(pill(...outcome(r)));
      const inspect = node('button', 'Inspect identities and screens', 'inspect-button');
      inspect.type = 'button'; inspect.addEventListener('click', () => inspectRow(r)); design.append(node('br'), inspect);
      const cost = node('td');
      const range = r.installed_capital_usd;
      cost.append(node('span', usd(range?.base ?? r.base_installed_usd), 'cost-base'), node('span', `${usd(range?.low)} / base / ${usd(range?.high)}`, 'range'));
      cost.append(node('span', 'Pilot total · estimated', 'cell-secondary'));
      tr.append(design, cost,
        cell(`${number(r.actual_peak_km_h) ? fmt(r.actual_peak_km_h) : 'Not evaluated'} / ${fmt(r.speed_cap_km_h, 0)} km/h`, 'Actual peak / speed cap'),
        cell(unit(r.journey_s, 's'), !r.numerical_arrival && number(r.partial_elapsed_s) ? `${fmt(r.partial_elapsed_s)} s partial calculation` : 'Motion time; dwell separate'),
        cell(`${number(r.peak_acceleration_m_s2) ? fmt(r.peak_acceleration_m_s2, 3) : 'Not evaluated'} / ${fmt(r.acceleration_request_m_s2 ?? study.brief.acceleration_request_m_s2, 2)} m/s²`, 'Achieved peak / requested'),
        cell(unit(r.propulsion_peak_grid_MW, 'MW', 3), 'Propulsion only; hotel load separate'),
        cell(unit(number(r.mass_kg) ? r.mass_kg / 1000 : null, 't', 2), r.unquantified_architecture_additions ? `Accounted subtotal ${fmt(r.accounted_mass_subtotal_kg / 1000, 2)} t; additions unknown` : 'Conditional loaded account; installed mass open'),
        cell(unit(r.maximum_actual_jerk_m_s3, 'm/s³', 3), `Target ${fmt(study.brief.comfort_jerk_target_m_s3, 2)}; final stop unresolved`));
      return tr;
    }));
    if (!rows.length) {
      const tr = node('tr'); const td = node('td', 'No scenarios match these filters. Reset filters to retain all four propulsion families.', 'empty-state'); td.colSpan = 8; tr.append(td); $('comparison-body').append(tr);
    }
  }
  function controlResult(value, distance) {
    const v = value || {};
    const state = v.state || v.numerical_state || 'Not evaluated';
    const arrived = v.numerical_arrival === true || v.normal_numerical_arrival === true;
    const overrun = number(distance) && number(v.final_position_m) && v.final_position_m > distance + (study.brief.berth_tolerance_m || 0);
    if (overrun) return {text: 'Overran route boundary', state, issue: true};
    if (v.departure_held === true) return {text: 'Departure held', state, issue: false};
    if (arrived) return {text: 'Numerical berth arrival', state, issue: false};
    if (v.fault_stop_in_route === true) return {text: 'Conditional fault stop in route', state, issue: false};
    return {text: state, state: v.hold_reason || 'Berth arrival not established', issue: true};
  }
  function controllerBounds(value) {
    const supported = value?.control_bounds_supported ?? value?.bounds_supported;
    return supported === true ? 'Within declared numerical bounds' : supported === false ? 'Outside declared bounds' : 'Bounds not established';
  }
  function renderControlComparison() {
    const comparison = study.control_comparison;
    const available = comparison && typeof comparison === 'object';
    $('control-comparison').hidden = !available;
    $('stopping-nav').hidden = !available;
    $('control-method-note').textContent = available ? 'Primary design rows use the feedback evaluation. Compare the original fixed-brake calculations below; physical candidate identities remain unchanged.' : 'This retained packet uses a nominal fixed brake point. Its fault cases are replayed without separate berth fitting.';
    if (!available) return;
    $('fixed-arrivals').textContent = unit(comparison.fixed_arrivals, 'arrivals', 0);
    $('feedback-arrivals').textContent = unit(comparison.feedback_arrivals, 'arrivals', 0);
    const faultPairs = Array.isArray(comparison.fault_pairs) ? comparison.fault_pairs : [];
    $('control-fault-count').textContent = fmt(faultPairs.length, 0);
    $('control-policy-note').textContent = comparison.policy_note || 'A common policy uses explicitly simulated position, speed and acceleration observations with declared uncertainty and response bounds. No separate brake-point fit is performed for each fault.';
    const kind = $('control-kind').value;
    const all = kind === 'normal' ? (comparison.normal_pairs || []) : faultPairs;
    const pairs = all.filter((p) =>
      ($('distance-filter').value === 'all' || sameNumber(p.distance_m, Number($('distance-filter').value))) &&
      ($('speed-filter').value === 'all' || sameNumber(p.speed_cap_km_h, Number($('speed-filter').value))) &&
      ($('family-filter').value === 'all' || p.family === $('family-filter').value));
    $('control-pair-count').textContent = `${pairs.length} of ${all.length} paired ${kind === 'normal' ? 'nominal' : 'adverse'} cases · spacing, speed and family filters also apply here`;
    replace('control-pairs', pairs.map((p) => {
      const before = controlResult(p.fixed, p.distance_m), after = controlResult(p.feedback, p.distance_m);
      const bounds = controllerBounds(p.feedback);
      const tr = node('tr', null, after.issue || bounds === 'Outside declared bounds' ? 'problem-row' : '');
      const design = node('td');
      design.append(node('strong', p.design_name || (kind === 'normal' ? p.name : familyName(p.family))), node('span', `${fmt(p.distance_m / 1000)} km · ${fmt(p.speed_cap_km_h, 0)} km/h cap`, 'cell-secondary'));
      if (kind !== 'normal') design.append(node('span', label(p.name || 'Unnamed case'), 'case-label'));
      design.append(node('span', `Candidate ${short(p.candidate_id)}`, 'cell-secondary'));
      tr.append(design,
        cell(before.text, `${unit(p.fixed?.final_position_m, 'm', 2)} · ${before.state}`),
        cell(after.text, `${unit(p.feedback?.final_position_m, 'm', 2)} · ${after.state}`),
        cell(bounds, p.feedback?.hold_reason || 'Simulated observations; physical performance not established'));
      return tr;
    }));
    if (!pairs.length) {
      const tr = node('tr'), td = node('td', 'No paired cases match these filters. Reset the design filters or choose the other comparison.', 'empty-state');
      td.colSpan = 4; tr.append(td); $('control-pairs').append(tr);
    }
  }
  function inspectRow(r) {
    const content = $('candidate-detail-content');
    const range = r.installed_capital_usd || {};
    content.replaceChildren(node('h3', r.name || familyName(r.family)), dl([
      ['Scope', `${fmt(r.distance_m / 1000)} km, two-station pilot`], ['Numerical outcome', outcome(r)[0]],
      ['Capital low / base / high', `${usd(range.low)} / ${usd(range.base ?? r.base_installed_usd)} / ${usd(range.high)}`],
      ['Energy from grid', unit(r.full_grid_kwh, 'kWh / journey', 2)],
      ['Propulsion / hotel grid', `${unit(r.grid_propulsion_kwh, 'kWh', 2)} / ${unit(r.hotel_grid_kwh, 'kWh', 2)}`],
      ['Reset energy', unit(r.reset_grid_kwh, 'kWh', 3)],
      ['Berth error', unit(r.berth_error_m, 'm', 3)],
      ['Final-stop acceleration step', unit(r.terminal_acceleration_step_m_s2, 'm/s²', 4)],
      ['Terminal jerk', r.terminal_jerk_resolved === true ? 'Resolution recorded; inspect source scope' : 'Unresolved'],
      ['Controller bounds', controllerBounds(r)],
      ['Next-experiment Pareto frontier', r.pareto_for_next_experiment ? 'Retained; not an integrated selection' : 'Not on declared frontier']
    ]), dl([
      ['Physical candidate', r.candidate_id], ['Body candidate', r.body_candidate_id || 'Unknown'],
      ['Journey evaluation', r.journey_evaluation_id || 'Unknown'], ['Cost evaluation', r.cost_evaluation_id || 'Unknown']
    ], 'identity-list'));
    const screens = node('div', null, 'screen-list');
    for (const [key, value] of Object.entries(r.criteria || {})) screens.append(node('span', `${label(key)}: ${value === true ? 'met in this model' : 'not met / unknown'}`, `screen-tag${value === true ? '' : ' issue'}`));
    content.append(screens, node('p', 'These are declared research screens. They do not establish physical acceptance, validated passenger comfort or operating release.', 'table-footnote'));
    $('candidate-details').open = true;
    $('candidate-details').scrollIntoView({behavior: 'smooth', block: 'nearest'});
  }

  function populateFinalists() {
    for (const id of ['trace-a', 'trace-b', 'checks-finalist']) {
      const select = $(id); select.replaceChildren();
      if (!finalists.length) select.append(node('option', 'No finalist admitted to follow-up'));
      finalists.forEach((f, index) => { const option = node('option', finalName(f)); option.value = String(index); select.append(option); });
      select.disabled = !finalists.length;
    }
    if (finalists.length > 1) $('trace-b').value = '1';
    renderChart(); renderChecks();
  }
  function selectedFinalist(id) { return finalists[Number($(id).value)] || null; }
  function svg(tag, attrs, text) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attrs || {})) e.setAttribute(key, String(value));
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function legend(text, cls) {
    const e = node('span', null, 'legend-item'); e.append(node('span', null, `legend-line ${cls || ''}`), node('span', text)); return e;
  }
  function renderChart() {
    const selections = [selectedFinalist('trace-a'), selectedFinalist('trace-b')];
    const metric = $('trace-metric').value;
    const allPoints = selections.flatMap(normalTrace);
    replace('chart-legend', selections.filter(Boolean).map((f, i) => legend(`${i ? 'B' : 'A'} · ${finalName(f)}`, i ? 'trace-b' : '')));
    if (metric === 'force') $('chart-legend').append(legend('Dashed = braking force', 'dashed'));
    if (!allPoints.length) {
      replace('trace-chart', [node('p', 'No source-linked trace is available for these selections.', 'empty-state')]);
      $('chart-description').textContent = 'Held designs are retained in the comparison above; a requested force is never substituted for an available force trace.';
      replace('trace-summaries', []); return;
    }
    const value = (p) => metric === 'speed' ? p.speed_m_s * 3.6 : metric === 'acceleration' ? p.acceleration_m_s2 : p.traction_n / 1000;
    const values = allPoints.map(value).filter(number);
    if (metric === 'force') values.push(...allPoints.map((p) => p.brake_n / 1000).filter(number));
    const xMax = Math.max(1, finiteMax(allPoints.map((p) => p.position_m)) || 1, ...selections.map((f) => requestOf(f).distance_m || 0));
    let yMin = Math.min(0, finiteMin(values) || 0), yMax = Math.max(0.1, finiteMax(values) || 0.1);
    const padding = (yMax - yMin) * .1; yMax += padding; if (yMin < 0) yMin -= padding;
    const w = 1000, h = 350, left = 65, right = 22, top = 20, bottom = 55;
    const X = (x) => left + x / xMax * (w - left - right);
    const Y = (y) => h - bottom - (y - yMin) / (yMax - yMin) * (h - bottom - top);
    const chart = svg('svg', {viewBox: `0 0 ${w} ${h}`, class: 'trace-svg', role: 'img', 'aria-labelledby': 'trace-svg-title trace-svg-description'});
    chart.append(svg('title', {id: 'trace-svg-title'}, `${metric === 'speed' ? 'Speed' : metric === 'acceleration' ? 'Acceleration' : 'Applied force'} along the station pair`), svg('desc', {id: 'trace-svg-description'}, 'Source-linked point-train integrations. A is teal; B is blue. The textual summaries following the chart report the main values. The chart does not establish physical performance.'));
    for (let i = 0; i <= 5; i++) {
      const x = xMax * i / 5, y = yMin + (yMax - yMin) * i / 5;
      chart.append(svg('line', {x1: X(x), y1: top, x2: X(x), y2: h - bottom, class: 'grid-line'}), svg('text', {x: X(x), y: h - bottom + 24, 'text-anchor': 'middle'}, fmt(x / 1000, 2)));
      chart.append(svg('line', {x1: left, y1: Y(y), x2: w - right, y2: Y(y), class: 'grid-line'}), svg('text', {x: left - 10, y: Y(y) + 4, 'text-anchor': 'end'}, fmt(y, metric === 'acceleration' ? 2 : 0)));
    }
    chart.append(svg('line', {x1: left, y1: h - bottom, x2: w - right, y2: h - bottom, class: 'axis-line'}), svg('text', {x: (left + w - right) / 2, y: h - 6, 'text-anchor': 'middle'}, 'Distance from departure station (km)'), svg('text', {x: left, y: 12}, metric === 'speed' ? 'km/h' : metric === 'acceleration' ? 'm/s²' : 'kN'));
    selections.forEach((f, i) => {
      const points = normalTrace(f);
      if (!points.length) return;
      const path = (fn) => points.filter((p) => number(fn(p))).map((p, index) => `${index ? 'L' : 'M'}${X(p.position_m).toFixed(2)},${Y(fn(p)).toFixed(2)}`).join(' ');
      chart.append(svg('path', {d: path(value), class: `curve${i ? ' trace-b' : ''}`}));
      if (metric === 'force') chart.append(svg('path', {d: path((p) => p.brake_n / 1000), class: `curve brake${i ? ' trace-b' : ''}`}));
    });
    replace('trace-chart', [chart]);
    $('chart-description').textContent = 'Actual integrated values, sampled from the exported trace. Speed caps and requested acceleration are inputs; they do not imply the train attains them. Final-stop and fault discontinuities remain separately reported.';
    replace('trace-summaries', selections.filter(Boolean).map((f, i) => {
      const r = rowOf(f) || {}, article = node('article', null, `trace-summary${i ? ' trace-b' : ''}`), points = normalTrace(f);
      article.append(node('h3', `${i ? 'B' : 'A'} · ${finalName(f)}`), dl([
        ['Actual peak / speed cap', `${unit(r.actual_peak_km_h ?? finiteMax(points.map((p) => p.speed_m_s * 3.6)), 'km/h')} / ${unit(f.speed_cap_km_h, 'km/h', 0)}`],
        ['Actual / requested acceleration', `${unit(r.peak_acceleration_m_s2, 'm/s²', 3)} / ${unit(requestOf(f).acceleration_request_m_s2 ?? study.brief.acceleration_request_m_s2, 'm/s²', 2)}`],
        ['Motion time', unit(r.journey_s, 's')], ['Loaded accounted mass', unit(number(r.mass_kg) ? r.mass_kg / 1000 : null, 't', 2)],
        ['Grid energy / journey', unit(r.full_grid_kwh, 'kWh', 2)], ['Moving jerk peak', unit(r.maximum_actual_jerk_m_s3, 'm/s³', 3)]
      ]), node('p', `Candidate ${short(f.candidate_id)} · terminal jerk unresolved`, 'table-footnote')); return article;
    }));
  }
  function checksOf(f) {
    if (Array.isArray(f?.checks)) return f.checks;
    // Preserve the shape used by full, unabridged campaign exports as well.
    return (f?.cases || []).map((c) => ({name: c.name, ...c.result}));
  }
  function renderChecks() {
    const f = selectedFinalist('checks-finalist'), r = rowOf(f) || {}, request = requestOf(f);
    const distance = request.distance_m ?? r.distance_m, tolerance = request.berth_tolerance_m ?? study.brief.berth_tolerance_m;
    const checks = checksOf(f);
    let overruns = 0, missed = 0;
    replace('checks-body', checks.map((c) => {
      const overrun = number(distance) && number(c.final_position_m) && c.final_position_m > distance + (number(tolerance) ? tolerance : 0);
      const fault = /power.loss|emergency|half.drive/.test(c.name || '');
      const miss = !fault && !c.normal_numerical_arrival;
      if (overrun) overruns++; else if (miss) missed++;
      const tr = node('tr', null, overrun || miss ? 'problem-row' : '');
      const outcomeText = overrun ? 'Overran station-pair boundary' : c.normal_numerical_arrival ? 'Numerical berth arrival' : c.fault_stop_in_route ? 'Fault stop within route' : c.state || 'Not evaluated';
      const interpretation = overrun ? `${unit(c.final_position_m - distance, 'm', 1)} beyond route end; declared control does not meet this case.` : miss ? 'Missed berth / incomplete under the declared policy.' : c.fault_stop_in_route ? 'Conditional stopping calculation only; no safety approval.' : 'Inspect the declared model and control assumptions.';
      tr.append(cell(label(c.name || 'Unnamed case')), cell(outcomeText, c.state), cell(unit(c.final_position_m, 'm', 2), number(distance) ? `Route ends at ${fmt(distance, 0)} m` : ''), cell(unit(c.maximum_absolute_jerk_m_s3, 'm/s³', 3)), cell(c.hold_reason || interpretation, c.hold_reason ? interpretation : ''));
      return tr;
    }));
    if (!checks.length) {
      const tr = node('tr'), td = node('td', 'No finalist robustness records exported.', 'empty-state'); td.colSpan = 5; tr.append(td); $('checks-body').append(tr);
    }
    $('checks-summary').textContent = f ? `${overruns} route overrun${overruns === 1 ? '' : 's'}; ${missed} other missed or incomplete berth case${missed === 1 ? '' : 's'}. ${study.control_comparison ? 'Feedback-policy' : 'Fixed-controller'} results expose remaining control and physical limits. Grade, mass, wind, failed drive and braking cases must be resolved before operating claims.` : 'No finalist was admitted to the follow-up calculation. Held alternatives remain available above.';
    renderDuty(f);
  }
  function renderMass() {
    const m = study.mass_summary || {};
    const cases = m.conditional_mass_scenarios || [];
    const entries = cases.map((c) => [`${label(c.case)} conditional tare account`, unit(number(c.conditional_accounted_train_mass_kg) ? c.conditional_accounted_train_mass_kg / 1000 : null, 't', 2)]);
    if (!entries.length) entries.push(['Conditional tare account', 'See mass reconciliation download']);
    entries.push(['Passenger load', unit(number(study.brief.normal_people) && number(study.brief.passenger_mass_kg) ? study.brief.normal_people * study.brief.passenger_mass_kg / 1000 : null, 't', 2)], ['Located CG / axle loads', m.located_CG_complete === true && m.axle_loads_complete === true ? 'Inspect source scope' : 'Not complete']);
    replace('mass-summary', [dl(entries)]);
  }
  function renderDuty(f) {
    if (!f) { replace('duty-summary', [node('p', 'No finalist refinement or repeated-duty record exported.')]); return; }
    const refinement = f.refinement || {}, duty = f.repeated_duty_proxy || {};
    const cycles = duty.cycles || [];
    replace('duty-summary', [dl([
      ['Coarse / refined timestep', `${unit(refinement.coarse_dt_s, 's', 3)} / ${unit(refinement.fine_dt_s, 's', 3)}`],
      ['Final-position change', unit(refinement.final_position_change_m, 'm', 4)],
      ['Declared berth refinement screen', refinement.berth_comparison_within_declared_tolerance === true ? 'Met in this comparison' : 'Not met / not reported'],
      ['Repeated-duty proxy', duty.state || 'Not evaluated'], ['Cycles evaluated', String(cycles.length)],
      ['Thermal qualification', 'Not established'], ['Recovery energy credit', 'None; performance unverified']
    ])]);
  }
  function renderLimitations() {
    const defaults = [
      'Complete installed geometry, CG, axle loads and architecture-specific equipment mass.',
      'Measured motor, inverter, gearbox and engagement force / duty envelopes.',
      'Validated brakes, charger sizing, independent recovery and rescue between stations.',
      'Terminal jerk, cable elasticity, coupling loads and contact / multibody dynamics.',
      'Control robustness, departure holds, missed berths and actual out-of-bound inputs.',
      'Site-specific civil engineering, installation, utilities and cost calibration.'
    ];
    const supplied = Array.isArray(study.limitations) ? study.limitations.filter((v) => typeof v === 'string') : [];
    replace('limitations', [...new Set([...defaults, ...supplied])].map((text) => node('li', text)));
  }
  function relativeHref(value) {
    if (typeof value !== 'string' || !value || value.startsWith('/') || value.includes('\\') || /^[a-z][a-z0-9+.-]*:/i.test(value) || value.split('/').includes('..')) return null;
    return value;
  }
  function renderDownloads() {
    const defaults = [
      {label: 'Complete study', path: 'study.json.gz', description: 'Requests, traces, sensitivity and cost evidence · gzip JSON'},
      {label: 'Mass reconciliation', path: 'mass-reconciliation.json.gz', description: 'Counted stock, explicit reserves and open installed mass · gzip JSON'},
      {label: 'Delivery draft', path: 'delivery-draft.json.gz', description: 'Manufacturing, assembly and disabled business records · gzip JSON'},
      {label: 'Comparison summary', path: 'summary.json', description: 'The data displayed on this page · JSON'}
    ];
    const supplied = study.downloads;
    let links = defaults;
    if (Array.isArray(supplied)) links = supplied.map((v) => ({label: v.label || v.name || 'Study record', path: v.path || v.href, description: v.description || 'Source-linked record'}));
    else if (supplied && typeof supplied === 'object') links = Object.entries(supplied).map(([key, value]) => {
      if (typeof value === 'string') { const original = defaults.find((d) => d.path === value); return {label: original?.label || label(key), path: value, description: original?.description || 'Source-linked record'}; }
      return {label: value.label || label(key), path: value.path || value.href, description: value.description || 'Source-linked record'};
    });
    // Business and manufacturing may name the same candidate-linked packet.
    links = [...new Map(links.filter((l) => relativeHref(l.path)).map((l) => [l.path, l])).values()];
    replace('download-links', links.map((l) => {
      const a = node('a', null, 'download-link'); a.href = relativeHref(l.path); a.setAttribute('download', ''); a.append(node('span', l.label), node('small', l.description)); return a;
    }));
  }
  $('retry').addEventListener('click', load);
  $('filters').addEventListener('submit', (event) => event.preventDefault());
  $('filters').addEventListener('change', () => { if (study) { renderTable(); renderControlComparison(); } });
  $('filters').addEventListener('reset', () => setTimeout(() => { if (study) { renderTable(); renderControlComparison(); } }, 0));
  $('control-kind').addEventListener('change', () => study && renderControlComparison());
  for (const id of ['trace-a', 'trace-b', 'trace-metric']) $(id).addEventListener('change', renderChart);
  $('checks-finalist').addEventListener('change', renderChecks);
  load();
})();
