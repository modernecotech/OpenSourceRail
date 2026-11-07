'use strict';
const $=s=>document.querySelector(s);
const number=(n,d=1)=>n==null?'—':Number(n).toLocaleString(undefined,{maximumFractionDigits:d});
const money=n=>n==null?'Not annualised':'$'+number(n/1e6,2)+'m';
function el(tag,text,cls){const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;}
fetch('summary.json',{cache:'no-store'}).then(async response=>{
  if(!response.ok)throw new Error('The current source-bound dossier is unavailable.');
  const data=await response.json();
  if(data.schema!=='osr-railway-closure-summary/1'||data.physical_accepted!==false||data.integrated_selection!==null)throw new Error('Unexpected research evidence contract.');
  const base=data.installed_load_cases.find(r=>r.name==='normal-base');
  for(const [value,label] of [[number(data.route_km)+' km','Double-track pilot · two stations'],['276','Normal passenger places / train'],[number(base.train_mass_kg/1000)+' t','Loaded model · counted stock and reserves'],[data.body.proposed_component_types,'Proposed component types']]){
    const n=el('div',null,'metric');n.append(el('b',value),el('span',label));$('#metrics').append(n);
  }
  const render=()=>{
    $('#comparison').replaceChildren();
    for(const r of data.rows){
      if(!$('#faults').checked&&!['nominal','recovery-disabled'].includes(r.experiment))continue;
      const tr=el('tr');
      for(const value of [r.experiment,`${r.headway_s}s / ${r.opposite_phase_s}s`,`${r.active_trainsets} + ${r.spare_trainsets}`,`${r.arrivals}/${r.requested}`,number(r.maximum_journey_s)+' s',number(r.maximum_moving_jerk_m_s3,3)+' m/s³',money(r.cost.installed_capital_usd.base),money(r.cost.whole_life_NPV_usd.base)])tr.append(el('td',value));
      tr.append(el('td',r.model_screen?'Pass under assumptions':'Held',r.model_screen?'pass':'held'));$('#comparison').append(tr);
    }
  };
  $('#faults').addEventListener('change',render);render();
  for(const [value,label] of [[number(data.body.total_occurrences,0),'located proposed occurrences'],[number(data.body.nominal_part_mass_kg.base/1000)+' t','body stock and equipment subtotal; installation and drive reserves separate'],[money(data.body.direct_parts_process_usd.base),'direct body parts/process estimate; delivered train cost is separate']])$('#body').append(el('p',value+' — '+label));
  for(const t of data.frontier.tasks){const n=el('div',null,'task');n.append(el('b',t.id.replaceAll('-',' ')),el('p',t.task),el('small',t.dependency));$('#frontier').append(n);}
  $('#identity').textContent='Physical bundle '+data.bundle.candidate_id+' · Study '+data.study_id;
  $('#loading').hidden=true;$('#content').hidden=false;
}).catch(error=>{$('#loading').textContent=error.message;});
