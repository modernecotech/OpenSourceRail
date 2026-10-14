import { element as el, table, evidenceBadge, quantityText, scopeMatches } from './components.js';
import { translate as t, applyLanguage } from '../workbench/i18n.js';
applyLanguage();
document.querySelectorAll('[data-view],#run,#refresh,#recordForm>button').forEach(node=>node.textContent=t(node.textContent));
const params=new URLSearchParams(location.search);
let context={city:params.get('city')||'samawah',environment:params.get('environment')||'simulation',revision:params.get('revision')||'unselected',selected_asset:params.get('selected_asset')||null,selected_part:params.get('selected_part')||null};
let actor=null;let preflights={};let problems=[];let schemas={};let activeView=params.get('view')||'design';let selectionEpoch=0;let inspectedCandidate=null;let currentJob=null;
const status=document.querySelector('#status');
function scope(){return {schema:'osr-design-identity/1',city:context.city,project:context.city,environment:context.environment,
  configuration_revision:context.revision||'unselected',baseline_sha256:context.baseline_sha256||null,run_id:null,asset_id:context.selected_asset||null,part_id:context.selected_part||null};}
function query(){return new URLSearchParams({city:context.city,environment:context.environment});}
async function api(path,body){
  const epoch=selectionEpoch;
  const response=await fetch('/api/design/'+path+(body?'':'?'+query()),body?{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':actor?.csrf||''},body:JSON.stringify({...body,identity:scope()})}:{});
  const result=await response.json();if(epoch!==selectionEpoch)throw Error('Scope changed; older response discarded.');if(!response.ok)throw Error(result.error||'Local service unavailable');return result;
}
function show(view){activeView=view;document.querySelectorAll('[data-panel]').forEach(p=>p.hidden=p.dataset.panel!==view);document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{show(b.dataset.view);if(activeView==='jobs')loadJobs();if(activeView==='evidence')loadRecords();});
function draftKey(){return 'osr:design-draft:'+context.city+':'+context.environment+':'+context.revision;}
function recordValue(){
  if(document.querySelector('#kind').value!=='appointment')return JSON.parse(document.querySelector('#recordPayload').value);
  const value={};document.querySelectorAll('[data-appointment-field]').forEach(node=>{value[node.dataset.appointmentField]=node.value||null;});value.identity_reference=null;return value;
}
function saveDraft(){try{localStorage.setItem(draftKey(),JSON.stringify({problem:document.querySelector('#problem').value,values:values(),recordKind:document.querySelector('#kind').value,recordPayload:document.querySelector('#recordPayload').value,productionInput:document.querySelector('#productionInput').value,appointment:Object.fromEntries([...document.querySelectorAll('[data-appointment-field]')].map(n=>[n.dataset.appointmentField,n.value]))}));}catch(error){status.textContent='Draft could not be retained: '+error.message;}}
function selectedProblem(){return problems.find(p=>p.id===document.querySelector('#problem').value);}
function values(){const p=selectedProblem();if(!p)return {};return Object.fromEntries(Object.entries(p.variables).map(([key,spec])=>{const node=document.querySelector('[data-variable="'+key+'"]');return [key,spec.kind==='choice'?JSON.parse(node.value):Number(node.value)];}));}
function renderProblem(saved){
  const p=selectedProblem();if(!p)return;
  document.querySelector('#function').textContent=p.applicability.function;
  document.querySelector('#charter').textContent=JSON.stringify(p.applicability,null,2);
  document.querySelector('#budget').value=p.budget.evaluations;
  const fields=document.querySelector('#variables');fields.replaceChildren();
  for(const [key,spec]of Object.entries(p.variables)){
    const label=el('label',key+' ['+spec.unit+']');let node;
    if(spec.kind==='choice'){node=el('select');for(const value of spec.choices)node.append(new Option(String(value),JSON.stringify(value)));}
    else{node=el('input','',{type:'number',min:spec.bounds[0],max:spec.bounds[1],step:spec.kind==='integer'?1:'any'});node.value=spec.bounds[0];}
    node.dataset.variable=key;if(saved&&key in saved)node.value=spec.kind==='choice'?JSON.stringify(saved[key]):saved[key];
    node.onchange=saveDraft;label.append(node);fields.append(label);
  }
  const preflight=preflights[p.id];document.querySelector('#preflight').textContent=preflight?.available?'Local solver prerequisites are available. Declared model domains and physical gates still apply.':'Unavailable prerequisites: '+(preflight?.missing||['preflight unavailable']).join(', ');document.querySelector('#run').disabled=!preflight?.available;
}
document.querySelector('#problem').onchange=()=>{renderProblem();saveDraft();};
document.querySelector('#designForm').onsubmit=async event=>{
  event.preventDefault();saveDraft();const button=document.querySelector('#run');button.disabled=true;
  try{const result=await api('jobs',{problem:selectedProblem().id,candidates:[values()],refine:document.querySelector('#refine').checked,search:document.querySelector('#search').checked?{seeds:[11,29,47],evaluations:16}:null,budget:{evaluations:Number(document.querySelector('#budget').value)}});
    status.textContent='Local job queued: '+result.id;show('jobs');await loadJobs();
  }catch(error){status.textContent=error.message;}finally{button.disabled=!preflights[selectedProblem()?.id]?.available;}
};
async function loadJobs(){
  const epoch=selectionEpoch;try{const payload=await api('jobs');if(epoch!==selectionEpoch)return;const root=document.querySelector('#jobs');root.replaceChildren();
    const queue=await api('work-queue');document.querySelector('#workQueue').replaceChildren(table(['Work','Owner','State'],queue.entries.map(e=>[e.title,e.owner,e.state])));
    if(!payload.jobs.length){root.append(el('p','No design jobs in this city and environment.'));return;}
    for(const job of payload.jobs){if(!scopeMatches(job,scope()))continue;const section=el('section','',{'data-job':job.id});section.append(el('h3',job.id+' · '+job.request.problem.id),
      el('p','Execution '+job.status+' · '+job.phase+' · '+Number(job.progress).toFixed(0)+'% · source '+job.source_state),el('p',job.error||'No execution error'));
      const actions=el('div','',{class:'actions'});
      for(const [label,action,enabled]of [['Inspect results','comparison',job.status==='completed'],['Inspect logs and artifacts','artifacts',true],['Cancel','cancel',['queued','running','resuming'].includes(job.status)],['Resume','resume',['failed','cancelled','timeout','budget-exceeded','interrupted','unavailable'].includes(job.status)&&job.source_state==='current'],['Export review package','export',job.status==='completed'&&job.source_state==='current']]){
        const b=el('button',label,{type:'button'});b.disabled=!enabled;b.onclick=async()=>{try{if(action==='comparison'){currentJob=job.id;renderComparison(await api('jobs/'+job.id+'/comparison'));}else if(action==='artifacts'){const result=await api('jobs/'+job.id+'/artifacts');const list=el('div');list.append(el('p','Attempt artifacts and logs · execution '+result.execution_state+' · partial files do not establish a sealed result.'));for(const row of result.artifacts){const q=query();q.set('file',row.name);list.append(el('a',row.name+' · '+row.bytes+' bytes',{href:'/api/design/jobs/'+job.id+'/artifact?'+q,download:''}),el('br'));}document.querySelector('#comparison').replaceChildren(list);}else{const result=await api('jobs/'+job.id+'/'+action,{});status.textContent=result.local_output?'Review package written locally: '+result.local_output:job.id+' '+action+' requested';await loadJobs();if(result.download){const downloads=el('div');downloads.append(el('p',result.download.restore+' Archive SHA256: '+result.download.archive_sha256));for(const row of result.download.chunks){const q=query();q.set('export',result.download.export_id);q.set('file',row.name);downloads.append(el('a',row.name+' · SHA256 '+row.sha256,{href:'/api/design/jobs/'+job.id+'/download?'+q,download:''}),el('br'));}document.querySelector('#comparison').replaceChildren(downloads);}}}catch(error){status.textContent=error.message;}};actions.append(b);
      }section.append(actions);root.append(section);
    }
  }catch(error){status.textContent=error.message;}
}
function renderComparison(report){
  if(!scopeMatches(report,scope())){status.textContent='Result belongs to a different city, environment or revision.';return;}
  const root=document.querySelector('#comparison');root.replaceChildren(el('h2','Candidate comparison · '+(report.source_state||'historical source scope')));
  for(const candidate of report.candidates){const section=el('section');section.append(el('h3',candidate.id),evidenceBadge(candidate.evidence_state||'unknown'));
    section.append(table(['Quantity','Value'],[['Defined component mass',quantityText(candidate.metrics.defined_mass_kg,'kg')],['Complete installed mass',quantityText(candidate.complete_installed_mass_kg,'kg')],['Installed cost',quantityText(candidate.installed_cost)],['Detailed deflection',quantityText(candidate.metrics.detailed_deflection_m,'m')],['Combined pressure/fault deflection',quantityText(candidate.metrics.combined_holdout_deflection_m,'m')]]));
    section.append(table(['Mandatory check','Evidence state','Basis'],Object.entries(candidate.checks).map(([name,row])=>[name,evidenceBadge(row.state),row.basis])));
    const inspect=el('button','Inspect physical parts',{type:'button'});inspect.onclick=()=>{inspectCandidate(candidate);show('parts');};section.append(inspect);root.append(section);
  }
}
function inspectCandidate(candidate){
  inspectedCandidate=candidate;document.querySelector('#definitionReview').hidden=!candidate.definition?.contract;
  const root=document.querySelector('#inspector');root.replaceChildren(el('h2','Physical definition '+candidate.id));
  const data=candidate.definition||{};const parts=data.contract?.parts||data.model?.instances||[];
  if(!parts.length){root.append(el('p','No complete physical inventory is available for this candidate.'));return;}
  const select=el('select','',{'aria-label':'Physical part'});for(const part of parts)select.append(new Option(part.id,part.id));const detail=el('pre');
  select.onchange=()=>{const part=parts.find(p=>p.id===select.value);detail.textContent=JSON.stringify(part,null,2);};root.append(select,detail);select.onchange();
}
document.querySelector('#definitionReview').onsubmit=async event=>{event.preventDefault();try{const file=document.querySelector('#revisedDefinition').files[0];if(!file||file.size>4*1024*1024)throw Error('Choose a bounded revised physical definition JSON file.');const proposed=JSON.parse(await file.text());const result=await api('definition-diff',{job:currentJob,candidate:inspectedCandidate.id,proposed});document.querySelector('#definitionDiff').textContent=JSON.stringify({...result,candidate_draft:undefined},null,2);status.textContent='Definition diff prepared; dependent evidence is invalidated and the adopted baseline remains separate.';}catch(error){status.textContent=error.message;}};
async function loadParts(){
  try{const payload=await api('parts');const root=document.querySelector('#parts');root.replaceChildren();
    for(const part of payload.parts){const source=payload.sources[part.source_id];const details=el('details');details.append(el('summary',part.name+' · '+part.category));
      details.append(el('p','Public potential component. Price, availability, rights and project qualification: unknown.'),el('pre',JSON.stringify(part.properties,null,2)));
      for(const limit of part.applicability_limits)details.append(el('p',limit));
      const link=el('a',source.publisher+' source · '+source.version,{href:source.url,target:'_blank',rel:'noopener noreferrer'});details.append(link);root.append(details);
    }
  }catch(error){status.textContent=error.message;}
}
function renderRecordFields(){const kind=document.querySelector('#kind').value;const fields=schemas.kinds?.[kind]||[];document.querySelector('#recordFields').textContent='Required fields: '+fields.join(', ');document.querySelector('#recordPayload').value=JSON.stringify(Object.fromEntries(fields.map(k=>[k,null])),null,2);
  const root=document.querySelector('#appointmentFields');root.replaceChildren();root.hidden=kind!=='appointment';document.querySelector('#structuredFields').hidden=kind==='appointment';
  if(kind==='appointment')for(const [key,label]of [['person_name','Person name'],['organization','Organization'],['role','Appointed role'],['appointment_scope','Project, responsibility and limits'],['valid_until','Appointment valid until']]){
    const field=el('label',t(label));const input=el(key==='appointment_scope'?'textarea':'input','',key==='valid_until'?{type:'date'}:{});input.dataset.appointmentField=key;input.oninput=saveDraft;field.append(input);root.append(field);
  }
}
document.querySelector('#kind').onchange=()=>{renderRecordFields();saveDraft();};document.querySelector('#recordPayload').oninput=saveDraft;
document.querySelector('#recordForm').onsubmit=async event=>{
  event.preventDefault();saveDraft();const epoch=selectionEpoch;try{let payload=recordValue();const file=document.querySelector('#evidenceFile').files[0];
    if(file){const response=await fetch('/api/ops-core/'+context.city+'/evidence',{method:'POST',headers:{'X-CSRF-Token':actor?.csrf||'','X-OSR-Filename':encodeURIComponent(file.name),'X-OSR-Mime':file.type||'application/octet-stream'},body:file});const data=await response.json();if(!response.ok)throw Error(data.error);const e=data.evidence;
      payload[document.querySelector('#kind').value==='appointment'?'identity_reference':'source_reference']={path:context.city+'/'+e.sha256.slice(0,2)+'/'+e.sha256+'-'+e.file_name,sha256:e.sha256};}
    if(epoch!==selectionEpoch)throw Error('Scope changed; original draft and uploaded evidence remain in their original scope.');
    const keyName=draftKey()+':submission';const submitted=JSON.stringify({kind:document.querySelector('#kind').value,payload});let previous;try{previous=JSON.parse(localStorage.getItem(keyName)||'null');}catch{}const key=previous?.submitted===submitted?previous.key:crypto.randomUUID();localStorage.setItem(keyName,JSON.stringify({key,submitted}));
    const result=await api('records',{kind:document.querySelector('#kind').value,payload,idempotency_key:key});localStorage.removeItem(keyName);status.textContent='Draft record retained: '+result.id;await loadRecords();
  }catch(error){status.textContent='Draft remains available: '+error.message;}
};
async function loadRecords(){try{const payload=await api('records');const costs=await api('cost-objectives');document.querySelector('#costObjectives').textContent=JSON.stringify(costs,null,2);const root=document.querySelector('#records');root.replaceChildren();if(!payload.records.length)root.append(el('p','No named appointments or evidence records yet.'));
  for(const record of payload.records){const section=el('section');section.append(el('h3',record.kind+' · '+record.id),el('p','Record '+record.state+' · authored by '+record.creator),el('pre',JSON.stringify(record.payload,null,2)));
    const b=el('button','Verify exact record and evidence',{type:'button'});b.disabled=record.state!=='draft'||!schemas.accounts_configured;b.onclick=async()=>{try{const result=await api('records/verify',{record:record.id,revision:record.revision});status.textContent='Record verified by '+result.reviewer+'; technical applicability and physical release remain separate.';await loadRecords();}catch(error){status.textContent=error.message;}};section.append(b);root.append(section);}
  }catch(error){status.textContent=error.message;}}
document.querySelector('#login').onsubmit=async event=>{event.preventDefault();try{const form=new FormData(event.target);const response=await fetch('/api/ops-auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:form.get('username'),password:form.get('password')})});const result=await response.json();if(!response.ok)throw Error(result.error);event.target.reset();actor=result.actor;await initialize();}catch(error){status.textContent=error.message;}};
document.querySelector('#productionInput').oninput=saveDraft;
document.querySelector('#productionPlan').onsubmit=async event=>{event.preventDefault();try{const data=JSON.parse(document.querySelector('#productionInput').value);document.querySelector('#productionOutput').textContent=JSON.stringify(await api('production-plan',data),null,2);}catch(error){status.textContent=error.message;}};
document.querySelector('#refresh').onclick=loadJobs;
window.addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==parent||event.data?.type!=='osr:context')return;const next=event.data.context;
  const changed=next.city!==context.city||next.environment!==context.environment||(next.revision||'unselected')!==context.revision||next.baseline_sha256!==context.baseline_sha256;if(changed){saveDraft();selectionEpoch++;currentJob=null;inspectedCandidate=null;document.querySelector('#definitionReview').hidden=true;document.querySelector('#definitionDiff').textContent='';document.querySelector('#productionInput').value='{"tasks":[],"resources":[]}';document.querySelector('#productionOutput').textContent='';for(const id of ['comparison','inspector','jobs','records'])document.querySelector('#'+id).replaceChildren();}
  context={...next,revision:next.revision||'unselected'};if(changed)initialize();});
async function initialize(){
  const epoch=selectionEpoch;try{const session=await fetch('/api/ops-auth/session').then(r=>r.json());actor=session.actor||null;
    document.querySelector('#context').textContent=context.city+' · '+context.environment+' · '+(context.revision||'unselected');document.querySelector('#account').textContent=actor?'Account: '+actor.display_name:'No authenticated account';
    const [p,s]=await Promise.all([api('problems'),api('review-schema')]);if(epoch!==selectionEpoch)return;problems=p.problems;preflights=p.preflight;schemas=s;
    const chooser=document.querySelector('#problem');chooser.replaceChildren(...problems.map(p=>new Option(p.id,p.id)));const kind=document.querySelector('#kind');kind.replaceChildren(...Object.keys(s.kinds).map(k=>new Option(k,k)));
    const saved=JSON.parse(localStorage.getItem(draftKey())||'null');if(saved){chooser.value=saved.problem;kind.value=saved.recordKind||'appointment';}
    renderProblem(saved?.values);renderRecordFields();document.querySelector('#productionInput').value=saved?.productionInput||'{"tasks":[],"resources":[]}';if(saved?.recordPayload)document.querySelector('#recordPayload').value=saved.recordPayload;
    if(saved?.appointment)for(const node of document.querySelectorAll('[data-appointment-field]'))node.value=saved.appointment[node.dataset.appointmentField]||'';
    status.textContent='Local design tools ready. Missing supplier, site and physical data remain explicit.';show(activeView);await loadParts();if(activeView==='jobs')await loadJobs();if(activeView==='evidence')await loadRecords();
  }catch(error){if(epoch===selectionEpoch)status.textContent=error.message;}}
show(activeView);await initialize();
