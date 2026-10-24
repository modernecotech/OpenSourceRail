const data=JSON.parse(document.getElementById('data').textContent), $=id=>document.getElementById(id);
function node(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
$('disposition').textContent='Integrated baseline: '+data.integrated_baseline.status+'. Next experiment: '+(data.next_experiment.selected_candidate_id||'none')+'. Physical acceptance: open.';
$('policy').textContent=JSON.stringify(data.next_experiment.policy,null,2);
$('scope').textContent=data.confirmation_scope+' '+data.twin_scope;
for(const c of data.candidates){const o=node('option',c.label||c.candidate_id.slice(0,16),$('choice'));o.value=c.candidate_id;}
function show(){const c=data.candidates.find(c=>c.candidate_id===$('choice').value), p=$('candidate');p.replaceChildren();
node('h2',c.label||'Candidate',p);node('code',c.candidate_id,p);
node('h3','Architecture and mass',p);const a=c.architecture, carrier=a.carrier||{},beam=a.guidebeam||{};
const wall=carrier.mode==='rigid-existing-hardpoints'?'retained hardpoints, no added carrier walls':(1000*carrier.wall_m).toFixed(1)+' mm counted carrier wall';
node('p',a.cars+' cars; '+carrier.mode+', '+carrier.count_per_car+' carrier groups/car; '+wall+'; '+beam.section_id+', '+beam.span_m+' m span.',p);
node('p','Known AW3 stock subtotal: '+(c.mass.known_mass_subtotal_kg/1000).toFixed(3)+' t/car. Complete installed mass distribution: '+(c.mass.complete_installed_distribution?'defined':'unresolved')+'. Unknown stock: '+c.inventory.unknown_stock_ids.length+' entries; unlocated stock: '+c.inventory.unlocated_stock_ids.length+' entries.',p);
const inventory=node('details',undefined,p);node('summary','Dimensions, mass breakdown and unresolved inventory',inventory);node('pre',JSON.stringify({architecture:c.architecture,mass:c.mass,inventory:c.inventory},null,2),inventory);
node('h3','Evaluated constraints',p);const t=node('table',undefined,p),head=node('tr',undefined,t);for(const v of ['Evaluator','Execution','Numerical','Screen','Maturity'])node('th',v,head);
for(const r of c.evaluations){const tr=node('tr',undefined,t);for(const k of ['evaluator','execution_status','numerical_status','screen_status','maturity'])node('td',r[k],tr);const d=node('details',undefined,p);node('summary',r.evaluator+' — margins, assumptions and reasons',d);node('pre',JSON.stringify(r,null,2),d);}
node('h3','Why this is not an integrated baseline',p);const rejected=node('details',undefined,p);node('summary',c.baseline_rejections.length+' recorded selection rejection reasons',rejected);node('pre',JSON.stringify(c.baseline_rejections,null,2),rejected);
node('h3','Revision and assembly consequences',p);node('pre',JSON.stringify(c.lineage,null,2),p);
node('p','Yaw bearings, slides, retention, cooling and complete removal paths require installed detail. Partial stock drawings cannot establish a complete assembly sequence or a complete cost.',p);
const link=node('a','Research twin, when compiled',p);link.href='../design-search-twins/'+c.candidate_id+'/README.md';}
$('choice').value=data.next_experiment.selected_candidate_id||data.candidates[0].candidate_id;$('choice').onchange=show;show();
