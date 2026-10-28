"""Local read-only explorer over saved sourced-design records."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
from pathlib import Path
import json
from . import ROOT,FLAGS
from . import coordinator

PAGE='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>OpenSourceRail — sourced design explorer</title>
<style>body{font:16px system-ui;background:#eef3f5;color:#17303c;max-width:1200px;margin:2rem auto;padding:0 1rem}button,select{font:inherit;padding:.6rem;margin:.3rem}button[aria-selected=true]{background:#17303c;color:white}pre{background:white;padding:1rem;overflow:auto;max-height:68vh;white-space:pre-wrap;word-break:break-word}small{color:#465f6b}h1{font-size:1.7rem}</style>
<h1>OpenSourceRail · sourced design explorer</h1><p>Research alternatives using published component specifications. Physical acceptance, operating release and whole-life cost selection remain open.</p>
<label>Candidate <select id="candidate"></select></label><nav id="views"></nav><p id="status">Loading saved evidence…</p><canvas id="plot" width="1100" height="280" style="max-width:100%;background:white" hidden></canvas><div id="parts" hidden><label>Find a part <input id="search" placeholder="HVAC, battery, door, joint…"></label><button id="find">Find</button><pre id="partdata"></pre></div><pre id="data"></pre>
<script>
let rows=[],selected=null,view='Design';const views=['Design','Mass and cost','Simulation','Closure','Manufacturing'];
const data=document.getElementById('data'),status=document.getElementById('status'),choose=document.getElementById('candidate');
function render(){document.querySelectorAll('nav button').forEach(b=>b.setAttribute('aria-selected',b.textContent===view));if(!selected)return;let x=selected;
let content=view==='Design'?{candidate_id:x.candidate_id,body_candidate_id:x.body_candidate_id,vehicle:x.vehicle_id,variant:x.variant,distance_m:x.distance_m,distributed:x.distributed,ambient_C:x.ambient_C,drive:x.drive_configuration}:view==='Mass and cost'?{mass:x.vehicle_summary,public_price_subtotal:x.partial_public_price,auxiliary_power:x.auxiliary_power,charging:x.charging,whole_life_cost:null}:view==='Simulation'?x.journeys:view==='Closure'?x.closure:x.manufacturing;
document.getElementById('plot').hidden=view!=='Simulation';document.getElementById('parts').hidden=view!=='Mass and cost';
if(view==='Simulation'){draw(x.journeys);content=x.journeys.map(j=>({name:j.name,...Object.fromEntries(Object.entries(j.result).filter(([k,v])=>!['trajectory','electrical_duty','source_sha256'].includes(k)))}))}
data.textContent=JSON.stringify(content,null,2);status.textContent=x.candidate_id+' · '+x.conditional_arrivals+' conditional numerical arrivals · 0 qualified journeys';}
function draw(journeys){let c=document.getElementById('plot').getContext('2d');c.clearRect(0,0,1100,280);c.font='14px system-ui';c.fillStyle='#17303c';c.fillText('Conditional velocity against position · source caps and unvalidated contact assumptions',45,22);c.fillText('m/s',8,42);c.fillText('Position (m)',930,270);c.strokeStyle='#bbb';for(let v=0;v<=25;v+=5){let y=240-v*7.8;c.beginPath();c.moveTo(45,y);c.lineTo(1060,y);c.stroke();c.fillText(v,12,y)}journeys.forEach((j,i)=>{let points=j.result.trajectory||[];c.strokeStyle=['#087e8b','#ad4d37','#6546a1','#9b7c00','#286f3b','#df5c8f','#4967bf','#6d6d6d','#008c7a'][i];c.beginPath();points.forEach((p,n)=>{let x=45+1000*p.front_m/selected.distance_m,y=240-7.8*p.speed_m_s;n?c.lineTo(x,y):c.moveTo(x,y)});c.stroke();c.fillStyle=c.strokeStyle;c.fillText(j.name,48+(i%5)*200,258+Math.floor(i/5)*17)})}
views.forEach(v=>{let b=document.createElement('button');b.textContent=v;b.onclick=()=>{view=v;render()};document.getElementById('views').append(b)});
async function load(){selected=await(await fetch('/api/case?index='+choose.value)).json();render()}
choose.onchange=load;fetch('/api/index').then(r=>r.json()).then(x=>{rows=x.cases;rows.forEach((r,i)=>{let o=document.createElement('option');o.value=i;o.textContent=r.request.vehicle_id+' · '+r.request.distance_m+'m · '+r.request.variant+(r.request.distributed?' · distributed':'');choose.append(o)});if(rows.length)load();else status.textContent='No executed cases; run ./osr design sourced run first.'}).catch(e=>status.textContent=e.message);
document.getElementById('find').onclick=async()=>{let q=encodeURIComponent(document.getElementById('search').value);let x=await(await fetch('/api/parts?index='+choose.value+'&search='+q)).json();document.getElementById('partdata').textContent=JSON.stringify(x,null,2)};
</script></html>'''


def index_view(state,root=ROOT):
    folder=Path(state)
    if folder.is_symlink():raise ValueError('Ordinary run required')
    run=coordinator.read(folder/'latest.json')
    if run['run_id']!=coordinator.identity({k:v for k,v in run.items() if k!='run_id'}) or run['source_sha256']!=coordinator.sources(root) or any(run.get(k) is not False for k in FLAGS):raise ValueError('Saved run differs')
    from engineering.railway_progress.coordinator import _unreleased
    _unreleased(run)
    return run


def case_view(state,index,root=ROOT):
    folder=Path(state);run=index_view(state,root)
    if type(index) is not int or not 0<=index<len(run['cases']):raise ValueError('Bounded case index required')
    row=run['cases'][index]
    expected='cases/'+coordinator.identity(dict(request=row['request'],source=run['source_sha256']))+'.json.gz'
    if row['path']!=expected:raise ValueError('Canonical case path required')
    r=coordinator.read(folder/expected)
    if r['evaluation_id']!=coordinator.identity({k:v for k,v in r.items() if k!='evaluation_id'}) or r['evaluation_id']!=row['evaluation_id'] or r['candidate_id']!=row['candidate_id'] or r['source_sha256']!=run['source_sha256'] or any(r.get(k) is not False for k in FLAGS):raise ValueError('Saved case differs')
    from engineering.railway_progress.coordinator import _unreleased
    _unreleased(r)
    return dict(candidate_id=r['candidate_id'],body_candidate_id=r['body_candidate_id'],vehicle_id=r['vehicle_id'],variant=r['variant'],distance_m=r['distance_m'],distributed=r['distributed'],ambient_C=r['ambient_C'],
        drive_configuration=r['drive']['drive_configuration'],vehicle_summary=r['vehicle_summary'],partial_public_price=r['partial_public_price'],auxiliary_power=r['auxiliary_power_case'],charging=dict(budget=r['charging'],separate_hardware_proposal=r['charging_proposal']),
        journeys=[dict(name=j['name'],result=j['result']) for j in r['journeys']],conditional_arrivals=r['conditional_arrivals'],
        manufacturing=r['manufacturing'],closure=dict(next_tasks=r['next_tasks'],qualified_journeys=0,whole_life_cost=None,**FLAGS),**FLAGS)


def part_view(state,index,search='',root=ROOT):
    from engineering.component_registry import validate_registry
    run=index_view(state,root)
    if type(index) is not int or not 0<=index<len(run['cases']) or not isinstance(search,str) or len(search)>200:raise ValueError('Bounded part query required')
    row=run['cases'][index];vid=row['request']['vehicle_id']
    if vid not in ('V1','V2','V3','V4','V5'):raise ValueError('Known vehicle required')
    e=coordinator.read(Path(state)/'vehicles'/(vid+'.json.gz'));v=e['vehicle'];reg=v['registry'];validate_registry(reg)
    if e['candidate_id']!=v['candidate_id'] or reg['candidate_id']!=v['candidate_id']:raise ValueError('Part candidate differs')
    parts=[];matching=[p for p in reg['parts'] if search.lower() in (p['part_id']+' '+' '.join(p['functions'])).lower()]
    for p in matching[:100]:
        occurrences=[o for o in reg['occurrences'] if o['part_definition_id']==p['physical_definition_id']]
        parts.append(dict(part=p,train_quantity=len(occurrences),first_occurrences=occurrences[:6]))
    return dict(body_candidate_id=v['candidate_id'],registry_id=reg['registry_id'],matching_definitions=len(matching),returned_definitions=len(parts),parts=parts,**FLAGS)


def handler(state,root=ROOT):
    class ReadOnly(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            try:
                path=urlsplit(self.path)
                if path.path=='/':raw=PAGE.encode();kind='text/html; charset=utf-8'
                elif path.path=='/api/index':raw=json.dumps(index_view(state,root)).encode();kind='application/json'
                elif path.path=='/api/case':
                    q=parse_qs(path.query)
                    if set(q)!={'index'} or len(q['index'])!=1:raise ValueError('One case index required')
                    raw=json.dumps(case_view(state,int(q['index'][0]),root)).encode();kind='application/json'
                elif path.path=='/api/parts':
                    q=parse_qs(path.query,keep_blank_values=True)
                    if set(q)!={'index','search'} or any(len(v)!=1 for v in q.values()):raise ValueError('One index and search required')
                    raw=json.dumps(part_view(state,int(q['index'][0]),q['search'][0],root)).encode();kind='application/json'
                else:self.send_error(404);return
                self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)))
                self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
            except (ValueError,KeyError,OSError):self.send_error(400,'Saved evidence unavailable or invalid')
    return ReadOnly


def serve(state,port=8772,root=ROOT):
    if type(port) is not int or not 1<=port<=65535:raise ValueError('Valid local port required')
    if Path(state).is_symlink():raise ValueError('Ordinary run directory required')
    print('Read-only sourced design explorer: http://127.0.0.1:'+str(port),flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),handler(state,root)).serve_forever()
