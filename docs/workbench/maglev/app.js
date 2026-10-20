const select = document.querySelector('#city');
const status = document.querySelector('#city-status');
const metrics = document.querySelector('#city-metrics');
const links = document.querySelector('#city-links');
const processes = document.querySelector('#city-processes');
const equipment = document.querySelector('#city-equipment');
const map = document.querySelector('#city-map');
let request = 0;
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
try {
  const index = await json('/engineering/ferrite_maglev/city-index.json', null, true);
  if (index.architecture !== 'ferrite-pm-maglev-study' || index.physical_release !== false) throw Error('Wrong architecture or unsupported release');
  const rows = [...index.cities].sort((a,b) => a.name.localeCompare(b.name));
  for (const row of rows) select.add(new Option(row.name, row.city));
  const initial = new URLSearchParams(location.search).get('city') || 'baghdad';
  select.value = rows.some(row => row.city === initial) ? initial : 'baghdad';
  select.disabled = false;
  async function show() {
    const token = ++request;
    for (const node of [metrics, links, processes, equipment]) node.replaceChildren();
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
      if (!base || ['repeat_fleet_allowance_usd', 'ordinary_elevated_allowance_usd', 'priced_scope_subtotal_usd'].some(key => !Number.isFinite(base[key]) || base[key] < 0) ||
          base.complete_city_programme_usd !== null || base.supplier_quotes !== false ||
          Math.abs(base.priced_scope_subtotal_usd-base.repeat_fleet_allowance_usd-base.ordinary_elevated_allowance_usd) > 0.01) throw Error('Inconsistent partial cost scope');
      if (token !== request) return;
      for (const [label,value] of [['Lines',summary.totals.lines],['Mapped route km',(summary.totals.retained_route_length_m/1000).toFixed(1)],['Provisional trainsets',summary.totals.trainsets],['Open city gates',summary.gates.length]]) metric(label,value);
      metric('Base fleet allowance',usd.format(base.repeat_fleet_allowance_usd),'fleet');
      metric('Base ordinary civil allowance',usd.format(base.ordinary_elevated_allowance_usd),'civil');
      metric('Base priced-scope subtotal',usd.format(base.priced_scope_subtotal_usd),'partial-subtotal');
      metric('Complete installed programme cost','Unknown — unpriced scope remains','complete-cost');
      link('City planning package',path+'README.md','package');
      link('Machine-readable plan',path+'summary.json','summary');
      link('Manufacturing processes and quantity bill',path+'manufacturing.json','manufacturing');
      link('Mapped network schematic',path+'network.svg','network');
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
