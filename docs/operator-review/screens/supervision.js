const get = id => document.getElementById(id);
const select = get('event');
for (const [index, frame] of supervisionReplay.frames.entries()) select.add(new Option(frame.name,index));
get('candidate').textContent = supervisionReplay.candidate;
function showFrame(){
  const frame = supervisionReplay.frames[Number(select.value)];
  const active = frame.rows.filter(row => row.active);
  get('clock').textContent = frame.time;
  get('count').textContent = frame.rows.length;
  get('alarms').textContent = active.length;
  get('stale').textContent = frame.rows.filter(row => row.quality === 'stale').length;
  get('sites').replaceChildren();
  for (const row of frame.rows) {
    const tr = get('sites').insertRow();
    tr.classList.toggle('alarm',row.active);
    const title = document.createElement('b'), subtitle = document.createElement('span');
    title.textContent = row.asset.replace('-', ' ').replace(/^./, c => c.toUpperCase());
    subtitle.textContent = row.role.replaceAll('-', ' ');
    tr.insertCell().append(title, subtitle);
    for (const value of [row.value ?? 'Unavailable', row.quality, row.source_time]) tr.insertCell().textContent = value;
    const state = document.createElement('strong');
    state.textContent = row.active ? 'Active' : 'Clear';
    tr.insertCell().append(state);
  }
  get('response').textContent = active.length ? active[0].response + '.' : 'Gateway reports no active protection trip at these three sites.';
}
select.value='1'; select.addEventListener('change',showFrame); showFrame();
