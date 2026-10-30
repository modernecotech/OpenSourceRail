const $=id=>document.getElementById(id), base='../../design-engine/ferrite-maglev/planning-platform/';
let manifest,index,original,plan,layers,edits=[],epoch=0;
const svgNS='http://www.w3.org/2000/svg', colours=['#14786d','#8754a0','#c58132','#337bb6','#ad4f5b'];
const clean=n=>{if(typeof n!=='number'||!Number.isFinite(n))throw Error('Finite numeric input required');return n;};
function status(text,error=false){$('status').textContent=text;$('status').dataset.error=String(error);}
function editStatus(text,error=false){$('edit-status').textContent=text;$('edit-status').dataset.error=String(error);}
async function bytes(name){
 const expected=manifest.files_sha256[name];if(!/^[0-9a-f]{64}$/.test(expected||''))throw Error('Missing payload digest');
 const response=await fetch(base+name);if(!response.ok)throw Error('Missing planning payload');
 const raw=new Uint8Array(await response.arrayBuffer());if(raw.length>32*1024*1024)throw Error('Planning payload exceeds byte budget');
 const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(x=>x.toString(16).padStart(2,'0')).join('');
 if(digest!==expected)throw Error('Planning payload differs from its receipt');
 if(!name.endsWith('.gz'))return raw;
 const reader=new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();let count=0,chunks=[];
 for(;;){const {done,value}=await reader.read();if(done)break;count+=value.length;if(count>64*1024*1024){await reader.cancel();throw Error('Inflated planning payload exceeds budget');}chunks.push(value);}
 const all=new Uint8Array(count);let offset=0;for(const c of chunks){all.set(c,offset);offset+=c.length;}return all;
}
async function json(name){return JSON.parse(new TextDecoder().decode(await bytes(name)));}
function option(parent,value,label){const e=document.createElement('option');e.value=value;e.textContent=label;parent.append(e);}
function point(line,s){let remaining=s;for(let i=1;i<line.coordinates.length;i++){const a=line.coordinates[i-1],b=line.coordinates[i],length=distance(a,b);if(remaining<=length||i===line.coordinates.length-1){const t=length?remaining/length:0;return a.map((v,j)=>v+t*(b[j]-v));}remaining-=length;}throw Error('Empty route');}
function distance(a,b){const r=Math.PI/180,x=a[1]*r,y=b[1]*r,h=Math.sin((y-x)/2)**2+Math.cos(x)*Math.cos(y)*Math.sin((b[0]-a[0])*r/2)**2;return 6371008.8*2*Math.atan2(Math.sqrt(h),Math.sqrt(Math.max(0,1-h)));}
function line(){return plan.lines.find(l=>l.id===$('line').value);}
function setStops(preferred){const l=line();if(!l)return;$('stop').replaceChildren();for(const s of l.stops)option($('stop'),s.id,s.id);$('headway').value=l.headway_s;const selected=l.stops.some(s=>s.id===preferred)?preferred:l.stops[0]?.id;$('stop').value=selected||'';setStop();}
function setStop(){const l=line(),s=l?.stops.find(x=>x.id===$('stop').value);if(!s)return;$('chainage').value=s.chainage_m.toFixed(3);$('chainage').max=l.length_m;$('dwell').value=s.dwell_s;}
function apply(edit){
 const trial=structuredClone(plan),l=trial.lines.find(x=>x.id===edit.line);
 if(edit.kind==='add-stop'){
  if(typeof edit.stop!=='string'||!/^[a-z0-9][a-z0-9-]{0,80}$/.test(edit.stop)||edits.some(e=>e.kind==='add-stop'&&e.stop===edit.stop)||trial.lines.some(r=>r.stops.some(s=>s.id===edit.stop)))throw Error('Unique bounded proposed stop ID required');
  const chainage=clean(edit.chainage_m),dwell=clean(edit.dwell_s);if(chainage<=0||chainage>=l.length_m)throw Error('New station must lie inside route endpoints');if(dwell<10||dwell>3600)throw Error('Dwell outside planning bounds');
  const [lon,lat]=point(l,chainage);l.stops.push({id:edit.stop,chainage_m:chainage,lon,lat,dwell_s:dwell,access_and_transfer_reassessment_required:true});l.stops.sort((a,b)=>a.chainage_m-b.chainage_m);
 }else if(edit.kind==='move-stop'){
  const s=l.stops.find(x=>x.id===edit.stop);if(!s)throw Error('Unknown stop');
  s.chainage_m=clean(edit.chainage_m);if(s.chainage_m<0||s.chainage_m>l.length_m)throw Error('Station outside route');
  [s.lon,s.lat]=point(l,s.chainage_m);
 }else if(edit.kind==='retire-stop'){
  if(!l.stops.some(s=>s.id===edit.stop))throw Error('Unknown stop');if(l.stops.length<=2)throw Error('At least two proposed stations must remain');
  if(trial.od.some(r=>r.origin===edit.stop||r.destination===edit.stop))throw Error('Revise OD rows before retiring a station');l.stops=l.stops.filter(s=>s.id!==edit.stop);
 }else if(edit.kind==='set-service'){
  l.headway_s=clean(edit.headway_s);if(l.headway_s<10||l.headway_s>86400)throw Error('Headway outside planning bounds');
  clean(edit.dwell_s);if(edit.dwell_s<10||edit.dwell_s>3600)throw Error('Dwell outside planning bounds');for(const s of l.stops)s.dwell_s=edit.dwell_s;
 }else if(edit.kind==='straighten-line'){
  const old=l.length_m;l.coordinates=[l.coordinates[0],l.coordinates.at(-1)];l.length_m=distance(...l.coordinates);
  if(l.length_m<1)throw Error('Collapsed alignment');for(const s of l.stops){s.chainage_m*=l.length_m/old;[s.lon,s.lat]=point(l,s.chainage_m);}
 }else if(edit.kind==='set-od'){
  if(!Array.isArray(edit.rows)||edit.rows.length>100000)throw Error('Bounded OD rows required');const ids=new Set(trial.lines.flatMap(l=>l.stops.map(s=>s.id))),seen=new Set();
  for(const r of edit.rows){const key=r.origin+'>'+r.destination;if(!ids.has(r.origin)||!ids.has(r.destination)||r.origin===r.destination||seen.has(key)||!['synthetic','observed-unaccepted'].includes(r.basis))throw Error('Invalid OD identity or basis');if(clean(r.trips_per_day)<0||r.trips_per_day>1e8)throw Error('Invalid demand');seen.add(key);}trial.od=structuredClone(edit.rows);
 }else throw Error('Unknown edit');
 for(const r of trial.lines)for(let i=1;i<r.stops.length;i++)if(r.stops[i].chainage_m<=r.stops[i-1].chainage_m)throw Error('Station order conflict; revise the neighbouring stops');
 plan=trial;edits.push(structuredClone(edit));render();setStops(edit.kind==='retire-stop'?$('stop').value:(edit.stop||$('stop').value));editStatus(`${edits.length} proposed changes. Access, demand, structures, controls and delivery require reassessment.`);
}
function nextStopId(){const ids=new Set([...plan.lines.flatMap(l=>l.stops.map(s=>s.id)),...edits.filter(e=>e.kind==='add-stop').map(e=>e.stop)]);for(let i=1;i<=100000;i++){const id=`proposal-stop-${String(i).padStart(3,'0')}`;if(!ids.has(id))return id;}throw Error('Proposed station identity range exhausted');}
function action(callback){try{callback();}catch(e){editStatus(e.message,true);}}
function render(){
 const all=plan.lines.flatMap(l=>l.coordinates),xs=all.map(p=>p[0]),ys=all.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
 const lonScale=111320*Math.cos((minY+maxY)/2*Math.PI/180),width=(maxX-minX)*lonScale,height=(maxY-minY)*111320;
 const scale=Math.min(920/(width||1),620/(height||1)),padX=(1000-width*scale)/2,padY=(700-height*scale)/2;
 const x=p=>padX+(p[0]-minX)*lonScale*scale,y=p=>700-padY-(p[1]-minY)*111320*scale;
 const svg=$('map');svg.replaceChildren();
 for(const [j,layer] of layers.layers.entries()){
  if(!document.querySelector(`[data-layer="${layer.id}"]`)?.checked)continue;
  let features=layer.features;
  if(layer.id==='alignments')features=plan.lines.map(l=>({geometry:{type:'LineString',coordinates:l.coordinates},properties:{id:l.id}}));
  if(layer.id==='operating-stops')features=plan.lines.flatMap(l=>l.stops.map(s=>({geometry:{type:'Point',coordinates:[s.lon,s.lat]},properties:{id:s.id}})));
  if(layer.id==='revision-changes')features=edits.filter(e=>e.line).map(e=>({geometry:{type:'LineString',coordinates:plan.lines.find(l=>l.id===e.line).coordinates},properties:{id:e.kind}}));
  for(const f of features){const g=f.geometry;if(!g)continue;let e;
   if(g.type==='Point'){e=document.createElementNS(svgNS,'circle');e.setAttribute('cx',x(g.coordinates));e.setAttribute('cy',y(g.coordinates));e.setAttribute('r',layer.id.startsWith('population')?Math.min(7,1+Math.sqrt(f.properties.population||0)/100):layer.id==='catchments'?12:layer.id==='operating-stops'?4:2.3);e.setAttribute('fill-opacity',layer.id==='catchments'?'.1':'.65');}
   else if(g.type==='LineString'){e=document.createElementNS(svgNS,'polyline');e.setAttribute('points',g.coordinates.map(p=>`${x(p)},${y(p)}`).join(' '));e.setAttribute('fill','none');e.setAttribute('stroke-width',layer.id==='alignments'?'2.5':'1');}
   else continue;
   e.setAttribute('stroke',colours[j%colours.length]);e.setAttribute('fill',g.type==='Point'?colours[j%colours.length]:'none');if(layer.id==='revision-changes')e.classList.add('proposed');
   if(layer.id==='alignments'&&f.properties.id===$('line').value){e.setAttribute('stroke','#bc4f32');e.setAttribute('stroke-width','4');}
   if(layer.id==='operating-stops')e.addEventListener('click',()=>{const l=plan.lines.find(l=>l.stops.some(s=>s.id===f.properties.id));$('line').value=l.id;setStops();$('stop').value=f.properties.id;setStop();render();});
   const title=document.createElementNS(svgNS,'title');title.textContent=String(f.id||f.properties?.id||layer.name);e.append(title);svg.append(e);
  }
 }
 $('issues').replaceChildren();for(const l of plan.lines){if(l.headway_s<l.planning_minimum_headway_s){const li=document.createElement('li');li.textContent=l.id+': below the retained packet’s earlier planning screen; not a v0.6 protection result';$('issues').append(li);}for(let i=1;i<l.stops.length;i++)if(l.stops[i].chainage_m-l.stops[i-1].chainage_m<1500){const li=document.createElement('li');li.textContent=l.id+': below the retained packet’s earlier 1,500 m comparison; access and transfer review required';$('issues').append(li);}}
 $('export').disabled=edits.length===0;$('reset').disabled=edits.length===0;
}
async function loadCity(){
 const current=++epoch;status('Verifying planning revision and GIS payload…');
 original=null;plan=null;layers=null;edits=[];for(const id of ['map','layers','line','stop','issues'])$(id).replaceChildren();$('map-caption').textContent='No verified city loaded.';$('revision').textContent='';$('import').disabled=true;$('reset').disabled=true;
 for(const id of ['line','stop','move','add-stop','retire-stop','service','straighten','set-od','export'])$(id).disabled=true;
 try{
  const row=index.cities.find(c=>c.city===$('city').value),p=await json(row.plan),g=await json(row.layers);if(current!==epoch)return;
  if(p.city!==row.city||g.city!==p.city||g.revision_sha256!==p.revision_sha256||p.physical_release!==false||g.physical_release!==false)throw Error('Incompatible planning identities');
  original=p;plan=structuredClone(p);layers=g;edits=[];$('revision').textContent=`Retained planning base ${p.revision_sha256}; v0.5 geography/service inputs, proposals remain local until compiled.`;
  $('line').replaceChildren();for(const l of p.lines)option($('line'),l.id,l.id);setStops();$('layers').replaceChildren();
  for(const l of layers.layers){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.dataset.layer=l.id;input.disabled=!l.available;input.checked=['alignments','operating-stops','transfers','revision-changes'].includes(l.id)&&l.available;input.addEventListener('change',render);label.append(input,document.createTextNode(` ${l.name} (${l.features.length}${l.display_sampling?', sampled':''}${!l.available?', unavailable':''})`));$('layers').append(label);}
  for(const id of ['line','stop','move','add-stop','retire-stop','service','straighten','set-od','import'])$(id).disabled=false;
  $('map-caption').textContent=`${p.city}: ${layers.layers.length} declared layers; retained source geography and new proposal remain distinct.`;$('od').value=JSON.stringify(plan.od,null,2);editStatus('No local changes.');render();status('Retained planning revision and GIS bytes verified.');
 }catch(e){if(current===epoch)status('Planning held: '+e.message,true);}
}
$('line').addEventListener('change',()=>{setStops();render();});$('stop').addEventListener('change',setStop);$('city').addEventListener('change',loadCity);
$('move').addEventListener('click',()=>action(()=>apply({kind:'move-stop',line:line().id,stop:$('stop').value,chainage_m:Number($('chainage').value)})));
$('add-stop').addEventListener('click',()=>action(()=>{apply({kind:'add-stop',line:line().id,stop:$('new-stop-id').value.trim()||nextStopId(),chainage_m:Number($('chainage').value),dwell_s:Number($('dwell').value)});$('new-stop-id').value='';}));
$('retire-stop').addEventListener('click',()=>action(()=>apply({kind:'retire-stop',line:line().id,stop:$('stop').value})));
$('service').addEventListener('click',()=>action(()=>apply({kind:'set-service',line:line().id,headway_s:Number($('headway').value),dwell_s:Number($('dwell').value)})));
$('straighten').addEventListener('click',()=>action(()=>apply({kind:'straighten-line',line:line().id})));
$('set-od').addEventListener('click',()=>action(()=>apply({kind:'set-od',rows:JSON.parse($('od').value)})));
$('reset').addEventListener('click',()=>{plan=structuredClone(original);edits=[];setStops();render();editStatus('Local proposal discarded.');});
$('export').addEventListener('click',()=>action(()=>{const actor=$('author').value.trim();if(!actor)throw Error('Named planning author required');const value={schema:'osr-planning-edit-bundle/1',city:original.city,base_revision_sha256:original.revision_sha256,actor,edits};const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=original.city+'-planning-edits.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}));
$('import').addEventListener('change',()=>action(async()=>{try{const file=$('import').files[0];if(!file||file.size>4*1024*1024)throw Error('Bounded edit file required');const v=JSON.parse(await file.text());if(v.schema!=='osr-planning-edit-bundle/1'||v.city!==original.city||v.base_revision_sha256!==original.revision_sha256||!Array.isArray(v.edits)||v.edits.length>1000)throw Error('Stale or incompatible edit bundle');const oldPlan=plan,oldEdits=edits;try{plan=structuredClone(original);edits=[];for(const e of v.edits)apply(e);$('author').value=String(v.actor||'');}catch(e){plan=oldPlan;edits=oldEdits;render();throw e;}}catch(e){editStatus(e.message,true);}}));
try{
 const response=await fetch(base+'manifest.json');if(!response.ok)throw Error('Planning publication unavailable');manifest=await response.json();if(manifest.physical_release!==false)throw Error('Unexpected release claim');
 index=await json('index.json');$('city').replaceChildren();for(const c of index.cities)option($('city'),c.city,c.label);$('city').value=index.cities.some(c=>c.city==='baghdad')?'baghdad':index.cities[0].city;$('city').disabled=false;
 for(const w of index.workspaces){const article=document.createElement('article'),h=document.createElement('h3'),a=document.createElement('a'),p=document.createElement('p');h.textContent=w.name;a.href=w.url;a.textContent=w.action;a.target='_blank';a.rel='noopener';p.textContent=w.scope;article.append(h,p,a);$('workspaces').append(article);}
 await loadCity();
}catch(e){status('Planning held: '+e.message,true);}
