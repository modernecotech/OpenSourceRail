"""Portable generated geometry viewer, component schedule and original circuit."""
from __future__ import annotations
import csv
import io
import json
from osr_mech.engineering_definition import fingerprint


def netlist(result):
    p=result['inputs']['electrical']['precharge']
    return dict(schema='osr-study-precharge-circuit/1',configuration_sha256=fingerprint(result['model']),
        topology='original OSR resistive precharge study; no supplier schematic copied',
        components=[dict(id=id,type=kind,nodes=nodes,design_value=value,qualified_rating=None)
            for id,kind,nodes,value in [('F1','fuse',['PACK+','FUSED+'],None),
                ('KPOS','main-contactor',['FUSED+','DC+'],None),('KPRE','precharge-contactor',['FUSED+','PRE+'],None),
                ('RPRE','resistor',['PRE+','DC+'],dict(resistance_ohm=p['resistance_ohm'],tolerance=p['resistance_tolerance'])),
                ('KNEG','return-contactor',['PACK-','DC-'],None),('CBUS','capacitor',['DC+','DC-'],dict(capacitance_f=p['capacitance_f'])),
                ('RBLEED','bleeder-resistor',['DC+','DC-'],None),('LOAD','unresolved-inverter-input',['DC+','DC-'],None)]],
        observations=['pack voltage','link voltage','current','HVIL','insulation status','contactor feedback'],
        control_policy='physics.closure_decision; offline study only',protection_coordination=None,
        bleeder_discharge_time_verified=False,production_released=False,physical_validation=False)


def circuit_svg(result):
    p=result['inputs']['electrical']['precharge']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="480" viewBox="0 0 1100 480" role="img" aria-label="Original OSR resistive precharge study">
<rect width="1100" height="480" fill="#fff"/><style>text{{font-family:Arial,sans-serif;fill:#183345}}.wire{{fill:none;stroke:#183345;stroke-width:3}}.part{{fill:#eef5fa;stroke:#183345;stroke-width:2}}</style>
<text x="35" y="38" font-size="25">OSR HV service panel — circuit topology study</text>
<text x="35" y="65" font-size="15">UNISSUED · ratings, isolation, fusing, discharge and railway qualification remain open</text>
<path class="wire" d="M90 150H190 M260 150H425 M535 150H920 M90 340H425 M535 340H920 M330 150V240H425 M535 240H650V150 M740 150V215 M740 265V340 M865 150V215 M865 265V340"/>
<rect class="part" x="190" y="133" width="70" height="34"/><text x="210" y="125">F1</text>
<rect class="part" x="425" y="130" width="110" height="40"/><text x="440" y="154">KPOS</text>
<rect class="part" x="425" y="220" width="50" height="40"/><text x="423" y="212">KPRE</text>
<rect class="part" x="485" y="220" width="50" height="40"/><path class="wire" d="M475 240H485"/>
<text x="500" y="212">RPRE</text><text x="405" y="290">{p['resistance_ohm']:g} Ω study value</text>
<rect class="part" x="425" y="320" width="110" height="40"/><text x="440" y="345">KNEG</text>
<path class="wire" d="M718 215H762 M718 265H762"/><text x="765" y="244">CBUS {p['capacitance_f']*1000:g} mF</text>
<rect class="part" x="850" y="215" width="30" height="50"/><text x="885" y="244">RBLEED</text>
<text x="35" y="155">PACK+</text><text x="35" y="345">PACK−</text><text x="945" y="155">DC+</text><text x="945" y="345">DC−</text>
<text x="35" y="407">Observe HVIL, insulation, link/pack voltage and all contactor feedback before a close request.</text>
<text x="35" y="435">RC study assumes a closed return, discharged capacitor and no load, inductance or switching transients.</text>
<text x="35" y="461">Source methods: Texas Instruments precharge guidance · design and topology: OpenSourceRail</text></svg>'''


def component_csv(result):
    groups={}
    for row in result['features']:
        key=(row['part_id'],row['role'],fingerprint(row['geometry']))
        entry=groups.setdefault(key,dict(part_id=row['part_id'],role=row['role'],quantity=0,
            mass_per_unit_kg=row['mass_kg'],source_ids=';'.join(row['source_ids']),mass_basis=row['property_basis'],status='unissued-study'))
        entry['quantity']+=1
    buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=['part_id','role','quantity','mass_per_unit_kg','source_ids','mass_basis','status'])
    writer.writeheader();writer.writerows(groups.values());return buffer.getvalue()


def html(result,sources):
    payload=dict(features=result['features'],infrastructure=result['infrastructure']['items'],
        cars=result['model']['family_definition']['cars'],studies=result['studies'],review=result['review'],
        sources={s['id']:dict(publisher=s['publisher'],title=s['title'],url=s['url']) for s in sources['sources']})
    data=json.dumps(payload,separators=(',',':'),ensure_ascii=False,allow_nan=False).replace('</','<\\/')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenSourceRail · best-practice design twin</title><style>
:root{font-family:system-ui,sans-serif;color:#153749;background:#f0f4f6}body{margin:0}header{padding:24px 30px;background:#fff;border-bottom:1px solid #cad8df}h1{font-size:26px;margin:0 0 8px}p{line-height:1.5}header p{margin:6px 0;max-width:1100px}.badge{padding:4px 8px;background:#fff0c5;border-radius:4px;font-size:13px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:20px;padding:20px}.panel{background:#fff;padding:18px;border:1px solid #ccd9e0;border-radius:10px}label{margin-right:20px;font-size:14px}select,input,button{font:inherit}svg{width:100%;height:530px;background:#fafcfd;border-radius:6px}button{border:1px solid #adbfca;background:#fff;padding:6px;border-radius:4px}aside h2{font-size:19px}#stats{font-size:14px;color:#416173;margin:10px 0}#sources a{display:block;padding:8px 0;font-size:14px}dl{font-size:14px}dt{font-weight:600;padding-top:10px}dd{margin:4px 0;overflow-wrap:anywhere}#component-list{max-height:220px;overflow:auto;margin-top:12px}#component-list button{display:block;text-align:left;width:100%;margin:4px 0;font-size:12px}.study{padding-top:20px;display:grid;grid-template-columns:1fr 1fr;gap:15px}.study svg{height:190px}small{color:#506874}a{color:#12679b}@media(max-width:950px){.layout{grid-template-columns:1fr}.study{grid-template-columns:1fr}}</style>
<header><h1>OpenSourceRail · best-practice design twin</h1><p>Original installed study designs with shared catalogue identity, geometry, mass and interface records.</p><span class="badge">Study configuration · supplier selection and physical qualification open</span><p><a href="reference-twin.FCStd">Native FreeCAD assembly</a> · <a href="reference-twin.step">Design detail STEP</a> · <a href="reference-twin.json">Complete twin data</a> · <a href="precharge.svg">Circuit study</a> · <a href="component-schedule.csv">Component schedule</a> · <a href="../../../../docs/best-practice/digital-twin-design-expansion.md">Research and design review</a></p></header>
<main class="layout"><section class="panel"><div><label>Scope <select id="scope"></select></label><label>View <select id="view"><option value="iso">Isometric</option><option value="side">Elevation</option><option value="top">Plan</option></select></label><label>Explode <input id="explode" type="range" min="0" max="1" step=".05" value="0"></label></div><div id="stats"></div><svg id="geometry" viewBox="0 0 1000 530" aria-label="Selectable component geometry"></svg><small>Derived review envelopes; exact holes, solid checks and joint constraints are in the native CAD audit. Body portal fit, fire integrity and load capacities remain open.</small><div class="study"><div><h3>DC-link precharge</h3><svg id="precharge" viewBox="0 0 480 190"></svg><div id="precharge-text"></div></div><div><h3>HVAC: healthy and one module out</h3><svg id="hvac" viewBox="0 0 480 190"></svg><div id="hvac-text"></div></div></div></section>
<aside class="panel"><h2 id="name">Select a component</h2><dl id="details"></dl><div id="sources"></div><h3>Components</h3><div id="component-list"></div></aside></main>
<script id="data" type="application/json">''' + data + '''</script><script>
const D=JSON.parse(document.getElementById('data').textContent), NS='http://www.w3.org/2000/svg';
const scope=document.getElementById('scope'),view=document.getElementById('view'),explode=document.getElementById('explode'),canvas=document.getElementById('geometry');
D.cars.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=c.id+' · design additions';scope.append(o)});let opt=document.createElement('option');opt.value='infra';opt.textContent='Rail seats and bearing interfaces';scope.append(opt);
const colors={'replaceable-hvac-module':'#67bca1','removable-roof-carrier':'#86a4b8','replaceable-door-cassette':'#71a8d1','surveyed-door-carrier':'#bac4cd','segregated-hv-service-panel':'#e5a94d','isolated-lv-converter-reservation':'#cfa1df','segregated-cable-support':'#db9257','barrier-transit-frame':'#d67c78','temperature-offgas-sensor-reservation':'#edc65d','rail-surrogate':'#8ba0b2','replaceable-fastening-study':'#5da58b','replaceable-bearing-interface':'#be924e'};
function el(tag,attrs,parent){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs||{}))e.setAttribute(k,v);if(parent)parent.append(e);return e}
function selected(){return scope.value==='infra'?D.infrastructure:D.features.filter(f=>f.instance_id.startsWith(scope.value+'/'))}
function details(f){document.getElementById('name').textContent=f.role;const dl=document.getElementById('details');dl.replaceChildren();for(const[k,v]of Object.entries({'Identity':f.instance_id||f.id,'Catalogue':f.part_id,'Study mass':(f.mass_kg??f.properties.mass_kg).toFixed(2)+' kg','Basis':f.property_basis||f.mass_basis,'Status':'Unissued study; no physical qualification'})){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=k;dd.textContent=v;dl.append(dt,dd)}const refs=document.getElementById('sources');refs.replaceChildren();for(const id of f.source_ids){const s=D.sources[id];const a=document.createElement('a');a.textContent=s.publisher+': '+s.title;a.href=s.url;a.target='_blank';a.rel='noopener';refs.append(a)}}
function projection(p){if(view.value==='top')return[p[0],-p[1]];if(view.value==='side')return[p[0],-p[2]];return[p[0]+.45*p[1],-.75*p[2]+.28*p[1]]}
function render(){canvas.replaceChildren();const fs=selected(),shapes=[],all=[];for(const f of fs){const pos=f.position_m||f.transform.translation_m;let dz=Number(explode.value)*(f.role.includes('hvac')?1.6:f.role.includes('carrier')?-.3:f.role.includes('bearing')?-.7:.4);for(const p of f.geometry.primitives){let dims=p.dimensions_m;if(!dims){dims=[2*p.radius_m,2*p.radius_m,2*p.radius_m];dims['xyz'.indexOf(p.axis)]=p.length_m}const points=[];for(let a of[-1,1])for(let b of[-1,1])for(let c of[-1,1]){const q=[pos[0]+p.centre_m[0]+a*dims[0]/2,pos[1]+p.centre_m[1]+b*dims[1]/2,pos[2]+p.centre_m[2]+c*dims[2]/2+dz];points.push(projection(q))}all.push(...points);shapes.push({f,p,points,depth:pos[1]+p.centre_m[1]+.01*(pos[2]+p.centre_m[2])})}}
const lo=[Math.min(...all.map(p=>p[0])),Math.min(...all.map(p=>p[1]))],hi=[Math.max(...all.map(p=>p[0])),Math.max(...all.map(p=>p[1]))],scale=Math.min(900/Math.max(.1,hi[0]-lo[0]),430/Math.max(.1,hi[1]-lo[1]));const map=p=>[50+(p[0]-lo[0])*scale,50+(p[1]-lo[1])*scale];
shapes.sort((a,b)=>a.depth-b.depth);for(const s of shapes){for(const face of[[0,2,6,4],[0,1,5,4],[4,5,7,6],[0,1,3,2],[2,3,7,6],[1,3,7,5]]){const e=el('polygon',{points:face.map(i=>map(s.points[i]).join(',')).join(' '),fill:colors[s.f.role]||'#b3c2ce',stroke:'#355063','stroke-width':.55,'fill-opacity':.82},canvas);e.style.cursor='pointer';e.addEventListener('click',()=>details(s.f))}}
const list=document.getElementById('component-list');list.replaceChildren();for(const f of fs){const b=document.createElement('button');b.textContent=(f.instance_id||f.id)+' · '+f.role;b.addEventListener('click',()=>details(f));list.append(b)}document.getElementById('stats').textContent=fs.length+' installed study objects · '+D.review.instance_count+' train instances · '+D.review.infrastructure_instance_count+' infrastructure objects · mass budget reconciled';details(fs[0]);}
function chart(id,series,xmax,ymin,ymax,label){const svg=document.getElementById(id);el('rect',{x:0,y:0,width:480,height:190,fill:'#f4f8fa'},svg);const X=x=>42+x/xmax*410,Y=y=>160-(y-ymin)/(ymax-ymin)*130;el('path',{d:'M42 20V160H455',fill:'none',stroke:'#8095a2'},svg);for(const s of series)el('polyline',{points:s.points.map(p=>[X(p[0]),Y(p[1])].join(',')).join(' '),fill:'none',stroke:s.color,'stroke-width':2.4},svg);const t=el('text',{x:48,y:183,'font-size':12,fill:'#426071'},svg);t.textContent=label;}
const P=D.studies.precharge,H=D.studies.hvac_nominal,F=D.studies.hvac_one_module_out,B=D.studies.hvac_three_module_baseline_one_out;chart('precharge',[{color:'#237b8b',points:P.samples.map(s=>[s.time_s,s.link_voltage_v])}],P.nominal_ready_time_s,0,900,'Time (s) → link voltage (V)');document.getElementById('precharge-text').textContent='95% at '+P.nominal_ready_time_s.toFixed(2)+' s; tolerance corner '+P.worst_tolerance_ready_time_s.toFixed(2)+' s. Required pulse-energy study: '+P.required_resistor_pulse_energy_j.toFixed(0)+' J; rating unverified.';
chart('hvac',[{color:'#278765',points:H.samples.map(s=>[s.time_s,s.temperature_c])},{color:'#c66147',points:B.samples.map(s=>[s.time_s,s.temperature_c])},{color:'#287ab2',points:F.samples.map(s=>[s.time_s,s.temperature_c])},{color:'#a38737',points:[[0,27],[1800,27]]}],1800,25,31,'Time (s) → temperature (°C), amber study limit');document.getElementById('hvac-text').textContent='Red: three-module baseline loses one, '+B.final_temperature_c.toFixed(2)+' °C and fails the screen. Blue: four-module proposal loses one, '+F.final_temperature_c.toFixed(2)+' °C. Extra study mass: '+D.review.additional_study_train_mass_kg+' kg/train. Actual climate/HVAC validation remains open.';
for(const e of[scope,view,explode])e.addEventListener('input',render);render();
</script></html>'''
