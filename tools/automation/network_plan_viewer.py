"""Standalone, offline inspection of line/support/junction planning records."""
import csv
import gzip
import io
import json


def viewer(outputs, routes, stations):
    core=json.loads(outputs['network-integration.json'])
    foundations=list(csv.DictReader(io.StringIO(gzip.decompress(outputs['foundation-register.csv.gz']).decode())))
    payload=dict(routes={k:[list(p) for p in r.coords] for k,r in routes.items()},stations=stations,
                 foundations=[dict(id=f['id'],line=f['line'],chainage_m=f['chainage_m'],xy=[float(f['x_m']),float(f['y_m'])],
                                   adjacent_span_ids=f['adjacent_span_ids'],soil_sample=f['nearest_desktop_soil_sample'],
                                   foundation_type='unselected — field ground/load design required',depth='unknown',
                                   junction_interfaces=f['junction_interface_ids']) for f in foundations],
                 interfaces=core['interfaces'],complexes=core['bounded_complexes'],infill=core['infill_stations'],gaps=core['residential_priority_areas'])
    raw=json.dumps(payload,separators=(',',':')).replace('<','\\u003c')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Baghdad line, foundation and junction planning</title>
<style>body{margin:0;font:15px system-ui;background:#f5f7fa;color:#14243a}header{padding:16px 24px;background:#14243a;color:white}main{display:grid;grid-template-columns:1fr 350px;height:82vh}svg{width:100%;height:100%;background:white;touch-action:none}aside{padding:18px;overflow:auto}button,select{padding:8px}pre{font:13px monospace;white-space:pre-wrap;overflow-wrap:anywhere}footer{padding:12px 24px}label{display:block;margin:8px 0}</style>
<header><strong>Baghdad — connected line / foundation / junction plan</strong><br>Concept geometry. Inspect every support and cross-line interface; field design and construction release remain open.</header>
<main><svg id="map" xmlns="http://www.w3.org/2000/svg"></svg><aside><label>Line <select id="line"><option value="all">All lines</option></select></label><button id="reset">Reset view</button>
<label><input type="checkbox" id="supports" checked>Support packets (visible when zoomed in)</label><label><input type="checkbox" id="junctions" checked>Crossings and bounded complexes</label><label><input type="checkbox" id="residential" checked>Residential / infill candidates</label>
<p>Scroll to zoom; drag to pan. Choose a line, then click its supports, stations or junctions. Coordinates are planning datums, not surveyed construction points.</p><pre id="info">Select an asset. Grey foundations do not imply an approved type, dimension, depth or bearing capacity.</pre></aside></main>
<footer>Red: unresolved crossing/overlap interfaces. Green: bounded interchange concepts / infill. Purple: underserved residential priorities. No new paid journeys, accepted walking routes or field approvals are inferred.</footer>
<script id="data" type="application/json">PAYLOAD</script><script>
const d=JSON.parse(document.getElementById('data').textContent),s=document.getElementById('map'),info=document.getElementById('info');
const ns='http://www.w3.org/2000/svg',colors=['#1769aa','#ef6c00','#388e3c','#d32f2f','#7b1fa2','#795548','#d81b60','#616161','#827717'];
const names=Object.keys(d.routes).sort();for(const n of names){let o=document.createElement('option');o.value=n;o.textContent=n;document.getElementById('line').append(o)}
let v=[0,0,55000,55000],down=null;
function el(tag,a,record){const x=document.createElementNS(ns,tag);for(const [k,val] of Object.entries(a))x.setAttribute(k,val);if(record){x.style.cursor='pointer';x.addEventListener('click',e=>{e.stopPropagation();info.textContent=JSON.stringify(record,null,2)})}s.append(x);return x}
function fit(){let k=document.getElementById('line').value;let p=(k==='all'?names:[k]).flatMap(n=>d.routes[n]);let xs=p.map(p=>p[0]),ys=p.map(p=>p[1]);let cx=(Math.max(...xs)+Math.min(...xs))/2,cy=(Math.max(...ys)+Math.min(...ys))/2,w=Math.max(Math.max(...xs)-Math.min(...xs),500)*1.08,h=Math.max(Math.max(...ys)-Math.min(...ys),500)*1.08,b=s.getBoundingClientRect(),a=b.width/b.height;if(w/h<a)w=h*a;else h=w/a;v=[cx-w/2,cy-h/2,w,h];draw()}
function draw(){s.replaceChildren();s.setAttribute('viewBox',v.join(' '));let k=document.getElementById('line').value,active=n=>k==='all'||n===k,r=v[2]/500;
for(const [i,n] of names.entries()){if(!active(n))continue;el('polyline',{points:d.routes[n].map(p=>p.join(',')).join(' '),fill:'none',stroke:colors[i], 'stroke-width':r/2}, {line:n,geometry:'retained planning corridor'})}
for(const a of d.stations){if(active(a.line))el('circle',{cx:a.xy[0],cy:a.xy[1],r:r,fill:'#14243a'},a)}
if(document.getElementById('supports').checked&&v[2]<10000)for(const a of d.foundations){if(active(a.line))el('circle',{cx:a.xy[0],cy:a.xy[1],r:r*1.5,fill:'#64748b',stroke:'white','stroke-width':r/3},a)}
if(document.getElementById('junctions').checked){for(const a of d.interfaces){if(!a.lines.some(active))continue;el('path',{d:`M ${a.xy[0]-r*2} ${a.xy[1]-r*2} l ${r*4} ${r*4} m 0 ${-r*4} l ${-r*4} ${r*4}`,stroke:'#dc2626','stroke-width':r,fill:'none'},a)}for(const a of d.complexes){if(a.lines.some(active))el('circle',{cx:a.centre_xy[0],cy:a.centre_xy[1],r:r*2,fill:'none',stroke:'#16a34a','stroke-width':r/2},a)}}
if(document.getElementById('residential').checked){for(const a of d.infill){if(active(a.line))el('circle',{cx:a.xy[0],cy:a.xy[1],r:r*1.7,fill:'#16a34a'},a)}for(const a of d.gaps){el('circle',{cx:a.xy[0],cy:a.xy[1],r:r*4,fill:'none',stroke:'#9333ea','stroke-width':r/2},a)}}}
s.addEventListener('wheel',e=>{e.preventDefault();let b=s.getBoundingClientRect(),x=(e.clientX-b.left)/b.width,y=(e.clientY-b.top)/b.height,f=e.deltaY>0?1.18:1/1.18;let w=v[2]*f,h=v[3]*f;if(w<50||w>150000)return;v=[v[0]+(v[2]-w)*x,v[1]+(v[3]-h)*y,w,h];draw()},{passive:false});
s.addEventListener('pointerdown',e=>{if(e.target!==s)return;down=[e.clientX,e.clientY,...v];s.setPointerCapture(e.pointerId)});s.addEventListener('pointermove',e=>{if(!down)return;let b=s.getBoundingClientRect();v=[down[2]-(e.clientX-down[0])/b.width*down[4],down[3]-(e.clientY-down[1])/b.height*down[5],down[4],down[5]];draw()});s.addEventListener('pointerup',()=>down=null);
for(const id of ['supports','junctions','residential'])document.getElementById(id).addEventListener('change',draw);document.getElementById('line').addEventListener('change',fit);document.getElementById('reset').addEventListener('click',fit);fit();
</script></html>'''
    return page.replace('PAYLOAD',raw).encode()
