const data=JSON.parse(document.querySelector('#diagrams').textContent);
const el=id=>document.getElementById(id);
const put=(id,value)=>{el(id).textContent=value};
function options(id,values){el(id).replaceChildren(...values.map(value=>new Option(value,value)))}
function time(seconds){return [Math.floor(seconds/3600),Math.floor(seconds/60)%60,seconds%60].map(n=>String(n).padStart(2,'0')).join(':')}
function showGroup(){
  const network=data[el('network').value], name=el('group').value, group=network.groups[name];
  el('working').hidden=!group;el('set-label').hidden=!group;
  put('title',name+' · '+(group?'Daily train working':'Service path on hold'));
  if(!group){
    put('summary',network.holds[name].join(' '));
    put('caveat','The cost ledger includes this service allowance. A connected stopping pattern and a feasible junction timetable still need an operator decision.');
    return;
  }
  const sample=group.samples[el('set').value], trips=sample.trips;
  put('summary',group.count+' daily departures in both directions · '+group.sets+' diagrammed trains · '+group.km.toFixed(1)+(group.loop?' km per lap':' km one way'));
  put('journey',group.loop?sample.train+' returns to '+sample.stops[0].label+' after each lap in the same direction.':sample.train+' begins at '+sample.stops[0].label+' and reverses at '+sample.stops.at(-1).label+'.');
  put('leg-one',trips[0].id+' ↓');put('leg-two',trips[1].id+(group.loop?' ↓':' ↑'));
  put('reading',group.loop?'Read each lap from top to bottom. The first and last rows refer to the same control stop.':'Each cell shows arrival / departure where both apply. Read the return from bottom to top.');
  const rows=sample.stops.map(s=>{
    const tr=document.createElement('tr'),th=document.createElement('th');
    th.scope='row';th.textContent=s.label;tr.append(th);
    for(const events of s.times){const td=tr.insertCell();td.textContent=events.map(time).join(' / ')}
    return tr;
  });el('calls').replaceChildren(...rows);
  put('turn','Arrives '+time(trips[0].arrival)+' and departs at '+time(trips[1].departure)+'. The '+(trips[1].departure-trips[0].arrival)+' s interval includes a minimum of '+group.layover+' s. Keeping every linked set at a platform throughout its wait would occupy up to '+group.platforms.join(' / ')+(group.loop?' berths in the two directions.':' berths at the two ends.'));
  put('separation','A single exclusive block between '+group.from+' and '+group.to+' has '+(group.margin<0?(-group.margin)+' s less clearance than required':group.margin+' s of clearance margin')+' at the peak interval. The slowest station pair needs at least '+group.blocks+' exclusive time sections under this screen. The signalling layout still needs braking and rear-clearance checks.');
  put('connection',group.connection||'This group has no paired intermediate transfer in the diagrammed routes. Terminal and street connections require a site plan.');
  put('caveat',network.caveat);
}
function chooseGroup(){const g=data[el('network').value].groups[el('group').value];options('set',g?Object.keys(g.samples):[]);showGroup()}
function chooseNetwork(){const n=data[el('network').value];options('group',[...Object.keys(n.groups),...Object.keys(n.holds)].sort());chooseGroup()}
el('network').addEventListener('change',chooseNetwork);el('group').addEventListener('change',chooseGroup);el('set').addEventListener('change',showGroup);chooseNetwork();
