const select = document.querySelector('#city');
const status = document.querySelector('#city-status');
const metrics = document.querySelector('#city-metrics');
const links = document.querySelector('#city-links');
const processes = document.querySelector('#city-processes');
const equipment = document.querySelector('#city-equipment');
const service = document.querySelector('#city-service');
const map = document.querySelector('#city-map');
let request = 0;
const headwayRange = values => {
  const minimum = Math.min(...values), maximum = Math.max(...values);
  const text = value => Number.isInteger(value) ? String(value) : value.toFixed(1);
  return minimum === maximum ? `${text(minimum)} s` : `${text(minimum)}–${text(maximum)} s`;
};
const costTerms = ['repeat_fleet_allowance_usd', 'ordinary_elevated_allowance_usd', 'terminal_civil_allowance_usd', 'station_electrical_allowance_usd', 'conditional_foundation_increment_usd', 'booster_electrical_allowance_usd', 'booster_mount_allowance_usd', 'rescue_kit_allowance_usd'];
const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
async function bytes(path, digest, unbound = false) {
  const response = await fetch(path);
  if (!response.ok) throw Error(`Planning data unavailable (${response.status})`);
  const value = await response.arrayBuffer();
  if (!unbound) {
    if (!/^[a-f0-9]{64}$/.test(digest)) throw Error('Missing source-bound city receipt');
    const actual = [...new Uint8Array(await crypto.subtle.digest('SHA-256', value))].map(v => v.toString(16).padStart(2, '0')).join('');
    if (actual !== digest) throw Error('City planning bytes differ from their receipt');
  }
  return value;
}
async function json(path, digest, unbound = false) {
  return JSON.parse(new TextDecoder().decode(await bytes(path, digest, unbound)));
}
function metric(label, value, name) {
  const dt = document.createElement('dt'), dd = document.createElement('dd');
  dt.textContent = label; dd.textContent = String(value);
  if (name) dd.dataset.metric = name;
  metrics.append(dt, dd);
}
function link(label, path, kind) {
  const node = document.createElement('a');
  node.textContent = label; node.href = path; node.dataset.kind = kind;
  links.append(node);
}
async function inflateInterchanges(compressed,expectedBytes) {
  const reader=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();
  const chunks=[];let total=0;
  try {
    while(true) {
      const {done,value}=await reader.read();
      if(done) break;
      if(value.byteLength>expectedBytes-total || value.byteLength>20*1024*1024-total) throw Error('Interchange raw size exceeds its budget');
      chunks.push(value);total+=value.byteLength;
    }
  } finally {
    await reader.cancel().catch(()=>{});reader.releaseLock();
  }
  if(total!==expectedBytes) throw Error('Interchange raw size differs');
  const raw=new Uint8Array(total);let offset=0;
  for(const chunk of chunks){raw.set(chunk,offset);offset+=chunk.byteLength;}
  return raw;
}
async function showInterchanges(index) {
  const status=document.querySelector('#hub-status'),image=document.querySelector('#hub-map');
  const path='/docs/design-engine/ferrite-maglev/interchange-hubs/';
  try {
    const manifest=await json(path+'manifest.json',null,true);
    const flags=['engineering_accepted','design_complete','physical_validation','manufacturing_release','physical_release'];
    const expected=['README.md','overview.svg','study.json.gz'];
    if(manifest.schema!=='osr-interchange-hub-investigation/1' || flags.some(flag=>manifest[flag]!==false) ||
       JSON.stringify(Object.keys(manifest.files_sha256).sort())!==JSON.stringify(expected) ||
       !Number.isInteger(manifest.raw_bytes) || manifest.raw_bytes<=0 || manifest.raw_bytes>20*1024*1024 ||
       !Number.isInteger(manifest.compressed_bytes) || manifest.compressed_bytes<=0 || manifest.compressed_bytes>4*1024*1024) throw Error('Unsupported interchange receipt');
    const baghdad=index.cities.find(row=>row.city==='baghdad');
    if(!baghdad || manifest.source_sha256[baghdad.package_path+'/summary.json']!==baghdad.summary_sha256) throw Error('Interchange study does not match the current Baghdad plan');
    const [compressed]=await Promise.all([bytes(path+'study.json.gz',manifest.files_sha256['study.json.gz']),bytes(path+'overview.svg',manifest.files_sha256['overview.svg'])]);
    if(compressed.byteLength!==manifest.compressed_bytes) throw Error('Interchange compressed size differs');
    const raw=await inflateInterchanges(compressed,manifest.raw_bytes);
    const study=JSON.parse(new TextDecoder().decode(raw));
    if(study.schema!==manifest.schema || study.city!=='Baghdad' || flags.some(flag=>study[flag]!==false) ||
       JSON.stringify(study.source_sha256)!==JSON.stringify(manifest.source_sha256) ||
       study.network_alternatives.some(row=>row.selected!==false) || study.coordinated_realignment_concepts.some(row=>row.selected!==false)) throw Error('Unsupported interchange selection or source claim');
    const conflicts=study.baseline.line_screens.reduce((sum,line)=>sum+line.spacing_conflicts.length,0);
    status.textContent=`Baghdad reference unchanged: ${study.baseline.operating_station_count} proposed stops and ${conflicts} spacing conflicts. ${study.variants.length} extended-transfer placements, ${study.network_alternatives.length} bounded network alternatives and ${study.coordinated_realignment_concepts.length} shared-site guideway concepts; none selected. ${study.true_compact_candidate_count} compact hub layouts demonstrated.`;
    image.src=path+'overview.svg';image.hidden=false;
  } catch(error) {
    image.hidden=true;image.removeAttribute('src');status.textContent=`Interchange investigation held: ${error.message}`;
  }
}
try {
  const index = await json('/engineering/ferrite_maglev/city-index.json', null, true);
  if (index.architecture !== 'ferrite-pm-maglev-study' || index.physical_release !== false) throw Error('Wrong architecture or unsupported release');
  void showInterchanges(index);
  const rows = [...index.cities].sort((a,b) => a.name.localeCompare(b.name));
  for (const row of rows) select.add(new Option(row.name, row.city));
  const initial = new URLSearchParams(location.search).get('city') || 'baghdad';
  select.value = rows.some(row => row.city === initial) ? initial : 'baghdad';
  select.disabled = false;
  async function show() {
    const token = ++request;
    for (const node of [metrics, links, processes, equipment, service]) node.replaceChildren();
    map.hidden = true; map.removeAttribute('src');
    status.textContent = 'Loading selected city…';
    try {
      const row = rows.find(row => row.city === select.value);
      const path = '/'+row.package_path+'/';
      if (!/^\/cities\/catalogue\/(?!.*\.\.)[^?#]+\/engineering\/maglev\/$/.test(path)) throw Error('Invalid city package');
      const summary = await json(path+'summary.json', row.summary_sha256);
      if (summary.architecture !== index.architecture || summary.city !== row.city ||
          ['design_complete', 'physical_validation', 'manufacturing_release', 'physical_release'].some(flag => summary[flag] !== false)) throw Error('City architecture, identity or release scope differs');
      if (summary.manufacturing_file !== 'manufacturing.json' || summary.network_file !== 'network.svg') throw Error('Missing current manufacturing or map record');
      const [bill] = await Promise.all([
        json(path+'manufacturing.json', summary.manufacturing_sha256),
        bytes(path+'network.svg', summary.network_sha256),
      ]);
      if (bill.schema !== 'osr-maglev-city-manufacturing/1' || bill.currency !== 'USD' ||
          ['design_complete', 'manufacturing_release', 'physical_release'].some(flag => bill[flag] !== false) ||
          bill.complete_city_programme_usd !== null) throw Error('Unsupported manufacturing bill or complete-price claim');
      const base = bill.scenarios.find(item => item.scenario === 'base');
      if (!base || [...costTerms, 'priced_scope_subtotal_usd'].some(key => !Number.isFinite(base[key]) || base[key] < 0) ||
          base.complete_city_programme_usd !== null || base.supplier_quotes !== false ||
          Math.abs(base.priced_scope_subtotal_usd-costTerms.reduce((sum,key) => sum+base[key],0)) > 0.01) throw Error('Inconsistent partial cost scope');
      if (!Array.isArray(summary.lines) || !summary.lines.length || summary.lines.some(line =>
          ['retained_peak_headway_seconds', 'selected_peak_headway_seconds', 'planning_minimum_headway_seconds'].some(key => !Number.isFinite(line[key]) || line[key] <= 0) ||
          line.selected_peak_headway_seconds < Math.max(line.retained_peak_headway_seconds, line.planning_minimum_headway_seconds) ||
          !Array.isArray(line.kinematic_holds) || typeof line.station_powered_kinematic_screen_pass !== 'boolean' ||
          line.station_powered_kinematic_screen_pass !== (line.kinematic_holds.length === 0) ||
          line.kinematic_holds.some(hold => !(Number.isInteger(hold.leg) && hold.leg > 0 || typeof hold.leg === 'string' && hold.leg.length > 0 && hold.leg.length <= 200) || !Number.isFinite(hold.distance_m) || hold.distance_m <= 0 || typeof hold.reason !== 'string' || !hold.reason))) throw Error('Inconsistent station headway or coasting hold records');
      if (['station_records', 'retained_station_records', 'added_terminal_service_zones', 'powered_top_up_zones', 'rescue_kits', 'transfer_spacing_conflicts'].some(key => !Number.isInteger(summary.totals[key]) || summary.totals[key] < 0) || summary.lines.some(line =>
          !line.operating_plan || ['retained_station_count', 'operating_station_count'].some(key => !Number.isInteger(line.operating_plan[key]) || line.operating_plan[key] < 2) ||
          !line.topology || !Number.isInteger(line.topology.terminal_service_zone_count) || line.topology.terminal_service_zone_count < 0 ||
          ['source_aw2_capacity_per_direction_hour', 'aw2_capacity_per_direction_hour'].some(key => !Number.isFinite(line[key]) || line[key] <= 0) ||
          typeof line.retained_capacity_target_met !== 'boolean' || line.retained_capacity_target_met !== (line.aw2_capacity_per_direction_hour >= line.source_aw2_capacity_per_direction_hour))) throw Error('Inconsistent operating stops or capacity targets');
      if (summary.lines.some(line => !Array.isArray(line.operating_plan.spacing_conflicts) || !Array.isArray(line.operating_plan.powered_top_up_zones) || !Array.isArray(line.operating_plan.rescue_nodes) || !Array.isArray(line.system_design_holds) || line.selected_eligible_operating_design !== null || typeof line.passenger_spacing_screen_pass !== 'boolean' || line.passenger_spacing_screen_pass !== (line.operating_plan.spacing_conflicts.length === 0))) throw Error('Inconsistent fixed-line design holds');
      if (token !== request) return;
      for (const [label,value] of [['Lines',summary.totals.lines],['Retained route km',(summary.totals.retained_route_length_m/1000).toFixed(1)],['Provisional trainsets',summary.totals.trainsets],['Open city gates',summary.gates.length]]) metric(label,value);
      metric('Original access records',summary.totals.retained_station_records,'retained-stops');
      metric('Proposed mainline stops',summary.totals.station_records,'operating-stops');
      metric('Additional terminal motor zones',summary.totals.added_terminal_service_zones,'terminal-zones');
      metric('Located midway accelerator zones',summary.totals.powered_top_up_zones,'booster-zones');
      metric('Independent one-way rescue kits',summary.totals.rescue_kits,'rescue-kits');
      metric('Transfer spacing conflicts',summary.totals.transfer_spacing_conflicts,'spacing-conflicts');
      metric('Eligible operating designs','0 — qualification and system holds remain','eligible-designs');
      metric('Lines below retained capacity target',summary.lines.filter(line => !line.retained_capacity_target_met).length,'capacity-shortfalls');
      metric('Base fleet allowance',usd.format(base.repeat_fleet_allowance_usd),'fleet');
      metric('Base ordinary civil allowance',usd.format(base.ordinary_elevated_allowance_usd),'civil');
      metric('Base terminal loop civil target',usd.format(base.terminal_civil_allowance_usd),'terminal-civil');
      metric('Conditional larger-footing increment',usd.format(base.conditional_foundation_increment_usd),'foundation-increment');
      metric('Base station electrical target',usd.format(base.station_electrical_allowance_usd),'station-electrical');
      metric('Located booster electrical target',usd.format(base.booster_electrical_allowance_usd),'booster-electrical');
      metric('Booster mount/cabinet stock target',usd.format(base.booster_mount_allowance_usd),'booster-mounts');
      metric('Independent rescue-kit target',usd.format(base.rescue_kit_allowance_usd),'rescue-cost');
      metric('Base priced-scope subtotal',usd.format(base.priced_scope_subtotal_usd),'partial-subtotal');
      metric('Complete installed programme cost','Unknown — unpriced scope remains','complete-cost');
      metric('Source peak headway',headwayRange(summary.lines.map(line => line.retained_peak_headway_seconds)),'source-headway');
      metric('Selected station-resource headway',headwayRange(summary.lines.map(line => line.selected_peak_headway_seconds)),'selected-headway');
      metric('Held coasting cases',summary.lines.reduce((sum,line) => sum+line.kinematic_holds.length,0),'coasting-holds');
      for (const line of summary.lines) {
        const item = document.createElement('li');
        item.dataset.line = line.line;
        item.textContent = `${line.line}: ${line.operating_plan.operating_station_count} proposed mainline stops versus ${line.operating_plan.retained_station_count} original access records; ${line.topology.terminal_service_zone_count} additional terminal motor zones. ${line.service_class} service; average proposed spacing ${(line.operating_plan.average_passenger_spacing_m/1000).toFixed(2)} km; ${line.operating_plan.powered_top_up_zones.length} midway zones and ${line.operating_plan.rescue_kit_count} one-way rescue kits. Source headway ${line.retained_peak_headway_seconds} s; selected ${line.selected_peak_headway_seconds} s; planning minimum ${line.planning_minimum_headway_seconds.toFixed(1)} s. AW2 capacity ${line.aw2_capacity_per_direction_hour.toFixed(0)} versus ${line.source_aw2_capacity_per_direction_hour.toFixed(0)} passengers/direction/hour required: ${line.retained_capacity_target_met ? 'numerical target met' : 'HOLD — capacity shortfall'}. ${line.kinematic_holds.length} held longitudinal cases. Sites, grade, curved magnetic guidance, receiver readiness and recovery remain unqualified.`;
        service.append(item);
        for (const hold of line.kinematic_holds.slice(0,8)) {
          const detail = document.createElement('li'); detail.dataset.hold = String(hold.leg);
          detail.textContent = `${line.line}, leg ${hold.leg} (${hold.distance_m.toFixed(0)} m): HOLD — ${hold.reason}`;
          service.append(detail);
        }
        for (const hold of line.system_design_holds.slice(0,5)) {
          const detail=document.createElement('li');detail.dataset.designHold=line.line;
          detail.textContent=`${line.line}: SYSTEM HOLD — ${hold.reason}`;service.append(detail);
        }
        for (const conflict of line.operating_plan.spacing_conflicts.slice(0,5)) {
          const detail=document.createElement('li');detail.dataset.spacingHold=line.line;
          detail.textContent=`${line.line}: retained transfer/terminal spacing ${conflict.distance_m.toFixed(0)} m versus ${conflict.minimum_m.toFixed(0)} m minimum. Passenger transfer/access solution unapproved; trains stay on their fixed lines.`;service.append(detail);
        }
        if (line.kinematic_holds.length>8 || line.system_design_holds.length>5 || line.operating_plan.spacing_conflicts.length>5) {
          const detail=document.createElement('li');detail.textContent=`${line.line}: additional holds are retained in the linked machine-readable plan.`;service.append(detail);
        }
      }
      link('City planning package',path+'README.md','package');
      link('Machine-readable plan',path+'summary.json','summary');
      link('Manufacturing processes and quantity bill',path+'manufacturing.json','manufacturing');
      link('Mapped network schematic',path+'network.svg','network');
      if(row.city==='baghdad') link('Unselected Baghdad interchange investigation','/docs/design-engine/ferrite-maglev/interchange-hubs/README.md','interchanges');
      for (const route of bill.process_routes) {
        const item = document.createElement('li'), title = document.createElement('strong'), text = document.createElement('span');
        title.textContent = route.id.replaceAll('-', ' ')+': ';
        text.textContent = route.operations.join(' → ')+'. Equipment: '+route.plant.join(', ')+'.';
        item.append(title,text); processes.append(item);
      }
      for (const candidate of bill.equipment_candidates) {
        const item = document.createElement('li');
        item.textContent = `${candidate.supplier} — ${candidate.process}. ${candidate.manufacture}. ${candidate.selection}.`;
        equipment.append(item);
      }
      map.alt = `${summary.name} network schematic from mapped planning geography; proposed maglev routes, not surveyed alignment`;
      map.src = path+'network.svg'; map.hidden = false;
      status.textContent = `${summary.name} · ${rows.length} primary maglev city packages · provisional`;
      const url = new URL(location.href); url.searchParams.set('city',row.city); history.replaceState(null,'',url);
    } catch (error) { if (token === request) status.textContent = error.message; }
  }
  select.onchange = show;
  await show();
} catch (error) { status.textContent = error.message; }
