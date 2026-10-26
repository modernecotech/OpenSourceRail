'use strict';
const base='../../../design-engine/ferrite-maglev/engineering-readiness/';
const $=id=>document.getElementById(id);
let register=null,index=null;
function node(tag,text,className){const n=document.createElement(tag);n.textContent=text;if(className)n.className=className;return n;}
async function bytes(name){const r=await fetch(base+name,{cache:'no-store'});if(!r.ok)throw new Error(name+': HTTP '+r.status);const data=await r.arrayBuffer();if(data.byteLength>40*1024*1024)throw new Error('Published record exceeded the display budget');return data;}
async function hash(data){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',data))].map(n=>n.toString(16).padStart(2,'0')).join('');}
async function verified(name,manifest){const data=await bytes(name);if(await hash(data)!==manifest.files_sha256[name])throw new Error('Published payload hash differs: '+name);return data;}
function choose(){
 const id=$('candidate').value,r=register.candidates.find(r=>r.candidate_id===id);if(!r)return;
 const facts=$('identity');facts.replaceChildren();
 for(const [label,value] of [['Configuration',r.candidate_id],['Magnetic component',r.magnet_component_id],['Body revision',r.body_candidate_id],['Accounted AW3 comparison',r.comparison_aw3_kg_per_car.toFixed(1)+' kg/car; complete installed mass unknown'],['Physical acceptance',r.physical_acceptance]])facts.append(node('dt',label),node('dd',value));
 $('gates').replaceChildren(...r.gates.map(g=>{const tr=node('tr','');const state=node('td','');state.append(node('span',g.state,'badge '+g.state));tr.append(node('td',g.id),state,node('td',g.reason),node('td',g.evidence_maturity));return tr;}));
 const trips=register.preflights_by_candidate[id];
 $('journeys').replaceChildren(...(trips?trips.map(j=>{const tr=node('tr','');tr.append(node('td',j.case_id),node('td',j.dynamic_execution),node('td',[...j.failed_gates,...j.unknown_gates].join(', ')));return tr;}):[(()=>{const tr=node('tr','');const td=node('td','No journey preflight was executed for this comparison. Its incomplete evidence remains unknown.');td.colSpan=3;tr.append(td);return tr;})()]));
}
function options(){
 const prior=$('candidate').value,query=$('filter').value.trim().toLowerCase();
 const rows=index.candidates.filter(r=>(r.name+' '+r.candidate_id+' '+r.magnet_component_id).toLowerCase().includes(query));
 $('candidate').replaceChildren(...rows.map(r=>{const o=node('option',r.name);o.value=r.candidate_id;return o;}));
 $('count').textContent=rows.length+' of '+index.candidates.length+' retained physical comparisons';
 if(rows.some(r=>r.candidate_id===prior))$('candidate').value=prior;
 else if(rows.some(r=>r.candidate_id===index.default_candidate_id))$('candidate').value=index.default_candidate_id;
 $('candidate').disabled=rows.length===0;
 if(rows.length)choose();else{$('gates').replaceChildren();$('identity').replaceChildren();$('journeys').replaceChildren();}
}
async function load(){
 $('integrity').textContent='Checking retained payload identities…';$('refresh').disabled=true;
 try{
  const manifest=JSON.parse(new TextDecoder().decode(await bytes('manifest.json')));
  index=JSON.parse(new TextDecoder().decode(await verified('index.json',manifest)));
  if(typeof DecompressionStream!=='function')throw new Error('This browser cannot decompress the register. Download the compressed records or use the verification CLI.');
  const compressed=await verified('status.json.gz',manifest);
  const data=await new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  if(data.byteLength>40*1024*1024)throw new Error('Expanded register exceeded the display budget');
  register=JSON.parse(new TextDecoder().decode(data));
  if(register.register_id!==index.register_id||register.physical_accepted!==false)throw new Error('Readiness identity or scope differs');
  options();$('methods').replaceChildren(...register.native_methods.rows.map(r=>{const item=node('div','','method');item.append(node('strong',r.method+' '),node('span',r.state,'badge '+r.state),node('p',r.assessment?.scope||r.reason||r.execution));return item;}));
  $('integrity').className='';$('integrity').textContent='Retained payload hashes verified. Live source freshness is checked by the readiness verification command; hardware acceptance remains unknown.';
 }catch(error){register=null;index=null;$('candidate').disabled=true;$('gates').replaceChildren();$('identity').replaceChildren();$('journeys').replaceChildren();$('methods').replaceChildren();$('integrity').className='error';$('integrity').textContent='Evidence unavailable: '+error.message;}
 finally{$('refresh').disabled=false;}
}
$('candidate').addEventListener('change',choose);$('filter').addEventListener('input',()=>{if(register)options();});$('refresh').addEventListener('click',load);load();
