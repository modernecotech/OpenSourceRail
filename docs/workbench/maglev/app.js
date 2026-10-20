const select = document.querySelector('#city');
const status = document.querySelector('#city-status');
let request = 0;
async function json(path) {
  const response = await fetch(path);
  if (!response.ok) throw Error(`Planning data unavailable (${response.status})`);
  return response.json();
}
try {
  const index = await json('/engineering/ferrite_maglev/city-index.json');
  if (index.architecture !== 'ferrite-pm-maglev-study' || index.physical_release !== false) throw Error('Wrong architecture or unsupported release');
  const rows = [...index.cities].sort((a,b) => a.name.localeCompare(b.name));
  for (const row of rows) select.add(new Option(row.name, row.city));
  const initial = new URLSearchParams(location.search).get('city') || 'baghdad';
  select.value = rows.some(row => row.city === initial) ? initial : 'baghdad';
  select.disabled = false;
  async function show() {
    const token = ++request;
    document.querySelector('#city-metrics').replaceChildren();
    document.querySelector('#city-links').replaceChildren();
    status.textContent = 'Loading selected city…';
    try {
      const row = rows.find(row => row.city === select.value);
      const path = '/'+row.package_path+'/';
      if (!/^\/cities\/catalogue\/(?!.*\.\.)[^?#]+\/engineering\/maglev\/$/.test(path)) throw Error('Invalid city package');
      const summary = await json(path+'summary.json');
      if (token !== request) return;
      if (summary.architecture !== index.architecture || summary.physical_release !== false || summary.city !== row.city) throw Error('City architecture or identity differs');
      for (const [label,value] of [['Lines',summary.totals.lines],['Retained route km',(summary.totals.retained_route_length_m/1000).toFixed(1)],['Provisional trainsets',summary.totals.trainsets],['Open city gates',summary.gates.length]]) {
        const dt = document.createElement('dt'), dd = document.createElement('dd');
        dt.textContent = label; dd.textContent = String(value);
        document.querySelector('#city-metrics').append(dt,dd);
      }
      for (const [label,target] of [['City planning package','README.md'],['Machine-readable plan','summary.json']]) {
        const link = document.createElement('a'); link.textContent = label; link.href = path+target;
        document.querySelector('#city-links').append(link);
      }
      status.textContent = `${summary.name} · ${rows.length} primary maglev city packages · provisional`;
      const url = new URL(location.href); url.searchParams.set('city',row.city); history.replaceState(null,'',url);
    } catch (error) { if (token === request) status.textContent = error.message; }
  }
  select.onchange = show;
  await show();
} catch (error) { status.textContent = error.message; }
