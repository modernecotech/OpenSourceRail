#!/usr/bin/env python3
"""Reproduce development sandwich-panel comparisons without adopting train mass."""
from pathlib import Path
import argparse,copy,csv,hashlib,io,itertools,json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from osr_mech.rolling_stock import composite_panels as panel
from osr_mech.provenance import stable_sum as sum
OUT=ROOT/'engineering/composite_panels/reference'
CONFIG=ROOT/'engineering/composite_panels/config/development.json'
EVIDENCE=ROOT/'engineering/composite_panels/evidence/register.json'

def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def candidate(config,skin,core,density,pitch,span,crown,kind,rib_depth=0):
 c=copy.deepcopy(config);c['core']['density_kg_m3']=density
 width=pitch-.006;height=c['panel']['roof_chord_m'] if kind=='roof' else c['panel']['side_height_m']
 qty=panel.panel_quantities(c,width,height,skin,core,crown=crown)
 rib=panel.rib_quantities(width,rib_depth,c['ribs']['wall_thickness_m'],c['ribs']['crown_width_m'],c['ribs']['count'],c['glass']['density_kg_m3'])
 qty['mass_kg']['ribs']=rib['mass_kg'];qty['installed_mass_kg']+=rib['mass_kg']
 if rib_depth:qty['cost_usd']=None;qty['missing_cost_inputs'].append('rib manufacturing/joint/tooling quote')
 abd=panel.laminate_abd(panel.balanced_skin(skin),core,c['bond']['thickness_m_each'],c['glass'])
 screen=c['screen'];dry=panel.strip_response(abd,screen['pressure_pa'],span,core,c['core']['shear_pa'])
 aged=panel.strip_response(abd,screen['pressure_pa'],span,core,c['core']['shear_pa'],stiffness_factor=screen['hot_wet_modulus_factor'],shear_factor=screen['hot_wet_shear_factor'])
 params=dict(kind=kind,skin_m=skin,core_m=core,core_density_kg_m3=density,pitch_m=pitch,support_span_m=span,crown_m=crown,rib_depth_m=rib_depth)
 identity=hashlib.sha256(encoded(dict(parameters=params,inputs=c))).hexdigest()[:16]
 return dict(candidate_id=identity,parameters=params,quantities=qty,ribs=rib,uniform_share_clip_force_n=screen['pressure_pa']*qty['panel_area_m2']/c['panel']['insert_count'],single_failed_clip_uniform_share_force_n=screen['pressure_pa']*qty['panel_area_m2']/(c['panel']['insert_count']-1),fatigue=panel.fatigue_sensitivity(max(1,aged['maximum_core_shear_stress_pa']),1000000,None),ply_schedule=[dict(thickness_m=p.thickness_m,angle_deg=p.angle_deg) for p in panel.balanced_skin(skin)],abd=abd,dry=dry,hot_wet=aged,
   pressure_basis='Editable 2 kPa development load; railway design pressure and clip support conditions unfrozen',
   conditional_deflection_screen=aged['total_deflection_m']<=screen['deflection_review_limit_m'] and aged['small_deflection_screen'],
   thermal_service_margin_c=None if screen['allowable_panel_service_temperature_c'] is None else screen['allowable_panel_service_temperature_c']-screen['hot_roof_temperature_c'],
   fatigue_qualified=False,fire_qualified=False,clip_failure_qualified=False,actual_quote=False,replacement_minutes=c['replacement_minutes'],qualified=False)

def trainset_inventory(config):
 from osr_mech.rolling_stock.car_body import CarDimensions,_door_centres_x,_window_zones,DOOR_WIDTH_MM,DOOR_SILL_HEIGHT_MM,DOOR_HEIGHT_MM,WINDOW_SILL_MM,WINDOW_HEIGHT_MM
 from osr_mech.rolling_stock.modular_fiberglass_body import cladding_bays
 dims=CarDimensions();records=[];totals={}
 for bay in cladding_bays(dims.body_length_mm):
  w=(bay.width_mm-.006*1000)/1000;left=(bay.x_center_mm-(bay.width_mm-6)/2)/1000;holes=[]
  for x in _door_centres_x(dims):holes.append((x/1000-DOOR_WIDTH_MM/2000-left,DOOR_SILL_HEIGHT_MM/1000,x/1000+DOOR_WIDTH_MM/2000-left,(DOOR_SILL_HEIGHT_MM+DOOR_HEIGHT_MM)/1000))
  for x,width in _window_zones(dims):holes.append((x/1000-width/2000-left,WINDOW_SILL_MM/1000,x/1000+width/2000-left,(WINDOW_SILL_MM+WINDOW_HEIGHT_MM)/1000))
  # Apertures may remove clip sites: this inventory is a mass sensitivity,
  # with four inserts as an explicit allowance, not an accepted trim/clip map.
  q=panel.panel_quantities(config,w,dims.body_height_mm/1000,.0015,.0246,holes=holes)
  records.append(dict(bay=bay.index,kind='side',trainset_count=6,quantities=q,aperture_map=holes,insert_placement_qualified=False))
  roof=panel.panel_quantities(config,w,(dims.body_width_mm-500)/1000,.0015,.0246,crown=config['panel']['roof_crown_m'])
  records.append(dict(bay=bay.index,kind='roof',trainset_count=3,quantities=roof,roof_crown_status='development assumption; coordination drawing unfrozen'))
 for r in records:
  for key,value in r['quantities']['mass_kg'].items():totals[key]=totals.get(key,0)+r['trainset_count']*value
 # Module quantities above each carry a perimeter seal allowance. Shared dry
 # joints are not purchased twice: publish the gross allowance and that gap.
 return dict(records=records,mass_components_kg=totals,gross_installed_mass_allowance_kg=sum(totals.values()),
  module_count=sum(r['trainset_count'] for r in records),shared_joint_seal_takeoff_qualified=False,
  excluded_scope=['structural frame','glazing','doors','end cowls','HVAC/PV equipment','walkways','aperture-specific mounting changes'],
  adopted_train_mass_changed=False,cost_allowance_usd=11000,quotation_confirmed=False)

def evidence_report(register,candidates,root):
 lookup={c['candidate_id']:c for c in candidates};rows=[]
 for test in register['tests']:
  c=lookup.get(test['candidate_id'])
  if c is None:raise ValueError('Unknown current candidate: '+test['candidate_id'])
  path=root/test['source_path']
  if not path.is_file() or sha(path)!=test['source_sha256']:raise ValueError('Missing/changed measured evidence')
  if test['condition'] not in ('dry','hot_wet') or test['measurement']!='strip_deflection_m':raise ValueError('Unsupported correlation; no fabricated prediction')
  value=panel.positive(test['measured_value'],'measurement');uncertainty=panel.positive(test['uncertainty_m'],'measurement uncertainty')
  if test['units']!='m':raise ValueError('Measured deflection units must be m')
  prediction=c[test['condition']]['total_deflection_m']
  rows.append(dict(candidate_id=c['candidate_id'],condition=test['condition'],predicted_m=prediction,measured_m=value,uncertainty_m=uncertainty,
   residual_m=prediction-value,relative_error=(prediction-value)/value,source_sha256=sha(path),accepted=False))
 quotes=[]
 for quote in register['quotes']:
  path=root/quote['source_path']
  if not path.is_file() or sha(path)!=quote['source_sha256']:raise ValueError('Missing/changed quotation')
  missing=sorted(set(register['required_quote_scope'])-set(quote['covered_scope']))
  quotes.append(dict(source_path=quote['source_path'],source_sha256=sha(path),missing_scope=missing,complete_scope=not missing,adopted=False))
 return dict(correlations=rows,quotation_reviews=quotes,missing_tests=register['required_tests'],
  fire_requirement_set=register['fire_requirement_set'],fire_hazard_level=register['fire_hazard_level'],
  supplier_frozen_material_stack=register['supplier_frozen_material_stack'],release_accepted=False)

def section_svg(config):
 # True thickness scale: 28 mm sandwich + 0.3 mm finish, with ply directions.
 scale=12;z=50;parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="440" viewBox="0 0 1050 440">','<rect width="1050" height="440" fill="white"/>','<text x="25" y="25" font-family="sans-serif" font-size="18">Development section: layered sandwich and reinforced clip lands</text>']
 layers=[('finish',.3,'#ddd'),('outer skin: 8 plies [0/+45/-45/90]s',1.5,'#63a996'),('adhesive',.2,'#bd8856'),('24.6 mm foam core',24.6,'#f1cf74'),('adhesive',.2,'#bd8856'),('inner skin: mirrored 8-ply schedule',1.5,'#63a996')]
 for name,thickness,color in layers:
  h=thickness*scale;parts.append(f'<rect x="30" y="{z}" width="480" height="{h}" fill="{color}" stroke="#333" stroke-width="0.5"/><text x="540" y="{z+h/2+5}" font-family="sans-serif" font-size="14">{name}</text>');z+=h
 parts += ['<rect x="30" y="74" width="30" height="300" fill="#378374"/>','<text x="30" y="410" font-family="sans-serif" font-size="14">25 mm solid edge lands; potted inserts carry clip loads into the metal frame.</text>','<text x="30" y="430" font-family="sans-serif" font-size="14">Curved roof layers are parametric CAD; HVAC, PV and worker loads bypass the skin.</text>','</svg>']
 return '\n'.join(parts).encode()

def interactive_report(cases, reference_pressure):
 data=json.dumps(cases,separators=(',',':')).replace('<','\\u003c')
 return ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hybrid exterior panel development</title><style>body{font:16px system-ui;color:#18333b;background:#f4f7f5;max-width:1100px;margin:auto;padding:24px}h1{font-size:30px}label{display:inline-block;margin:10px}select,input{padding:8px}svg{background:white;max-width:100%;border:1px solid #abc}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}button{cursor:pointer;padding:7px}pre{white-space:pre-wrap}circle{cursor:pointer}</style>
<h1>Hybrid exterior panel development</h1><p>Explore assumed mass and pressure-strip response. Material, joint, fire, fatigue and roof-temperature qualification remain open. Steel-frame and roof-equipment loads stay separate.</p>
<label>Panel <select id="kind"><option value="side">Side</option><option value="roof">Roof</option></select></label>
<label>Pressure sensitivity <input id="pressure" type="range" min="500" max="6000" step="250" value="2000"><output id="pa"></output> Pa</label>
<label>Support span <select id="span"><option value="all">All</option><option>0.5</option><option>0.75</option><option>1</option></select> m</label>
<label>Skin <select id="skin"><option value="all">All</option><option value="0.001">1 mm</option><option value="0.0015">1.5 mm</option><option value="0.002">2 mm</option></select></label>
<p id="count"></p><svg id="plot" viewBox="0 0 1000 420" role="img" aria-label="Installed mass versus hot-wet deflection"></svg>
<p>Blue points are conditional bending/shear screens, not accepted designs. Rib mass is included but rib stiffness is uncredited. Select a point or a row to inspect the measured-evidence candidate identity.</p>
<button id="all">Show all filtered rows</button><table><thead><tr><th>Candidate</th><th>Mass kg/m²</th><th>Hot-wet δ mm</th><th>Skin/core mm</th><th>Rib mm</th><th>Quote</th></tr></thead><tbody id="rows"></tbody></table><pre id="details"></pre>
<p><a href="comparison.csv">All comparison rows</a> · <a href="prototype-and-quotation-status.json">Prototype and quotation status</a> · <a href="rfq.json">Complete-scope quotation request</a> · <a href="cad/side-layered-panel.FCStd">Layered side CAD</a> · <a href="cad/roof-layered-panel.FCStd">Curved roof CAD</a></p>
<script>const data='''+data+''';const REFERENCE_PRESSURE='''+str(reference_pressure)+''';const el=id=>document.getElementById(id);const ns='http://www.w3.org/2000/svg';
function node(tag,attrs,text){const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text)n.textContent=text;return n}
let showAll=false;function details(c){el('details').textContent=JSON.stringify({candidate:c,displayed_pressure_sensitivity_pa:Number(el('pressure').value),qualification:'Open; measured tests must reproduce the candidate nominal input configuration'},null,2)}
function render(){const pressure=Number(el('pressure').value),factor=pressure/REFERENCE_PRESSURE;el('pa').value=pressure;
const rows=data.filter(c=>c.parameters.kind===el('kind').value&&(el('span').value==='all'||c.parameters.support_span_m===Number(el('span').value))&&(el('skin').value==='all'||c.parameters.skin_m===Number(el('skin').value)));
el('count').textContent=`${rows.length} development combinations. Cost and fatigue life are unquoted/unmeasured; pressure scaling is linear and requires small-deflection validation.`;
const plot=el('plot');plot.replaceChildren();const masses=rows.map(c=>c.quantities.installed_mass_kg/c.quantities.panel_area_m2),dy=rows.map(c=>c.hot_wet.total_deflection_m*1000*factor),xmin=Math.min(...masses),xmax=Math.max(...masses),ymax=Math.max(6,...dy);const x=v=>70+(v-xmin)/Math.max(1,xmax-xmin)*880,y=v=>350-v/ymax*290;
plot.append(node('line',{x1:70,y1:350,x2:950,y2:350,stroke:'#345'}),node('line',{x1:70,y1:60,x2:70,y2:350,stroke:'#345'}),node('text',{x:350,y:400},'Installed panel mass per area (kg/m²)'),node('text',{x:85,y:30},'Hot-wet strip deflection (mm), hypothetical ageing'),node('line',{x1:70,y1:y(5),x2:950,y2:y(5),stroke:'#a54','stroke-dasharray':'5 4'}));
for(let i=0;i<=4;i++){const v=xmin+(xmax-xmin)*i/4,w=ymax*i/4;plot.append(node('text',{x:x(v),y:373,'text-anchor':'middle'},v.toFixed(1)),node('text',{x:60,y:y(w)+4,'text-anchor':'end'},w.toFixed(1)))}
rows.forEach((c,i)=>{const ok=dy[i]<=5&&dy[i]/1000/c.parameters.support_span_m<=.01,n=node('circle',{cx:x(masses[i]),cy:y(dy[i]),r:3,fill:ok?'#227ca2':'#ae7756',opacity:.55,tabindex:0,role:'button','aria-label':`Inspect candidate ${c.candidate_id}`});n.append(node('title',{},`${c.candidate_id}: ${masses[i].toFixed(2)} kg/m²; ${dy[i].toFixed(2)} mm`));n.onclick=()=>details(c);n.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();details(c)}};plot.append(n)});
const sorted=[...rows].sort((a,b)=>a.quantities.installed_mass_kg/a.quantities.panel_area_m2-b.quantities.installed_mass_kg/b.quantities.panel_area_m2);el('rows').replaceChildren();sorted.slice(0,showAll?sorted.length:30).forEach(c=>{const tr=document.createElement('tr');[c.candidate_id,(c.quantities.installed_mass_kg/c.quantities.panel_area_m2).toFixed(2),(c.hot_wet.total_deflection_m*1000*factor).toFixed(2),`${c.parameters.skin_m*1000}/${c.parameters.core_m*1000}`,c.parameters.rib_depth_m*1000,'Pending'].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td)});tr.onclick=()=>details(c);el('rows').append(tr)});}
['kind','pressure','span','skin'].forEach(id=>el(id).oninput=render);el('all').onclick=()=>{showAll=!showAll;el('all').textContent=showAll?'Show first 30 rows':'Show all filtered rows';render()};render();</script></html>''').encode()

def build(config_path=CONFIG,evidence_path=EVIDENCE):
 config=json.loads(config_path.read_text());register=json.loads(evidence_path.read_text());cases=[]
 cad_dir=OUT/'cad';receipt_path=cad_dir/'verification.json'
 receipt=json.loads(receipt_path.read_text())
 if receipt.get('passed') is not True or receipt.get('physical_release') is not False:raise ValueError('Native CAD verification missing or invalid')
 for relative,digest in receipt['sources_sha256'].items():
  if sha(ROOT/relative)!=digest:raise ValueError('Native CAD source drift; rerun the FreeCAD verifier: '+relative)
 for record in receipt['records']:
  if sha(cad_dir/record['output'])!=record['sha256']:raise ValueError('Changed native CAD output')
 grid=config['sweep']
 for kind in ('side','roof'):
  crowns=[0] if kind=='side' else grid['roof_crown_m']
  for skin,core,density,pitch,span,crown,rib_depth in itertools.product(grid['skin_thickness_m'],grid['core_depth_m'],grid['core_density_kg_m3'],grid['module_pitch_m'],config['screen']['support_span_candidates_m'],crowns,grid['rib_depth_m']):
   if span>pitch:continue
   cases.append(candidate(config,skin,core,density,pitch,span,crown,kind,rib_depth))
 base=[candidate(config,.0015,.0246,80,1,1,crown,kind) for kind,crown in [('side',0),('roof',config['panel']['roof_crown_m'])]]
 # Equal panel footprints/support/load, comparing mass per area and compliance.
 # Metal sheets have no assumed ribs: they are explicitly unequal performance.
 metals=[]
 for m in config['metal_comparators']:
  t=panel.positive(m['thickness_m'],'metal thickness');d=m['young_pa']*t**3/12
  delta=5*config['screen']['pressure_pa']*config['screen']['support_span_m']**4/(384*d)
  # Also size an unstiffened complete panel to the same hypothetical hot-wet
  # modulus factor and deflection target. This is one valid comparison route,
  # not an optimum metal rib design or demonstrated equivalent rail behaviour.
  screen=config['screen'];factor=screen['hot_wet_modulus_factor']
  required_t=(5*screen['pressure_pa']*screen['support_span_m']**4*12/(384*m['young_pa']*factor*screen['deflection_review_limit_m']))**(1/3)
  assemblies=[]
  for ref in base:
   q=ref['quantities'];a=q['panel_area_m2'];hardware=sum(q['mass_kg'][k] for k in ('clips','retainer','seal','insert'))
   conductivity=45 if m['name']=='steel sheet' else 200
   # Insulation is a non-load-bearing development allowance, with no bridge
   # or adhesive qualification credit, to match the stated conduction screen.
   insulation=max(0,(q['thermal_resistance_m2k_w']-required_t/conductivity)*config['core']['thermal_conductivity_w_mk'])
   mass=required_t*a*m['density_kg_m3']+insulation*a*config['core']['density_kg_m3']+q['mass_kg']['finish']+hardware
   assemblies.append(dict(kind=ref['parameters']['kind'],plate_thickness_m=required_t,insulation_thickness_m=insulation,installed_mass_kg=mass,
    attachment_basis='Same assumed clips/retainer/seals/insert quantities; metal edge/attachment detail unqualified',
    hot_wet_surrogate_deflection_m=5*screen['pressure_pa']*screen['support_span_m']**4*12/(384*m['young_pa']*factor*required_t**3),
    shared_modulus_factor_is_hypothetical=True,thermal_bridge_qualification=False,qualified=False))
  metals.append(dict(name=m['name'],material_mass_kg_m2=m['density_kg_m3']*t,strip_deflection_m=delta,small_deflection_screen=delta/config['screen']['support_span_m']<=.01,
   reinforcement_mass_kg=None,equivalent_performance_demonstrated=False,installed_cost_usd=None,matched_target_plate_assemblies=assemblies))
 fronts=[]
 for kind in ('side','roof'):
  eligible=[c for c in cases if c['parameters']['kind']==kind and c['conditional_deflection_screen']]
  # Normalize per area: a narrower panel is not an automatic train-level saving.
  metric=lambda c:(c['quantities']['installed_mass_kg']/c['quantities']['panel_area_m2'],c['hot_wet']['total_deflection_m'])
  for c in eligible:
   a,b=metric(c)
   if not any(x<=a and y<=b and (x<a or y<b) for x,y in map(metric,eligible)):fronts.append(c['candidate_id'])
 evidence=evidence_report(register,cases,ROOT)
 outputs={'candidates.json':encoded(cases),'reference-panels.json':encoded(base),'trainset-takeoff.json':encoded(trainset_inventory(config)),
  'prototype-and-quotation-status.json':encoded(evidence),'metal-comparators.json':encoded(metals),'section.svg':section_svg(config)}
 outputs['report.html']=interactive_report(cases,config['screen']['pressure_pa'])
 outputs['rfq.json']=encoded(dict(schema='osr-composite-panel-rfq/1',status='prepared-not-sent',scope='144 three-car side/roof modules plus attachment/retention/seal kits; trim schedules and final roof coordination require supplier review',
  baseline_material_stack='Development 8-ply skins/core/bond/finish; exact resin/glass/core grade unselected',required_quote_scope=register['required_quote_scope'],
  required_technical_evidence=register['required_tests'],requested_fields=['supplier','quote date','valid through','currency','unit and complete installed kit price','annual quantities','tooling/cure/qualification amortisation','rejects/rework','replacement supply','lead time','configuration drawings','test methods and evidence references'],
  target_hazard_level=None,target_requirement_set=None,purchase_approved=False))
 table=io.StringIO();fields=['candidate_id','kind','skin_m','core_m','core_density_kg_m3','pitch_m','support_span_m','crown_m','rib_depth_m','mass_kg_m2','dry_deflection_mm','hot_wet_deflection_mm','thermal_resistance_m2k_w','conditional_screen','pareto','installed_cost_usd','qualified']
 writer=csv.DictWriter(table,fieldnames=fields,lineterminator='\n');writer.writeheader()
 for c in cases:
  q=c['quantities'];writer.writerow(dict(candidate_id=c['candidate_id'],**c['parameters'],mass_kg_m2=q['installed_mass_kg']/q['panel_area_m2'],dry_deflection_mm=c['dry']['total_deflection_m']*1000,hot_wet_deflection_mm=c['hot_wet']['total_deflection_m']*1000,thermal_resistance_m2k_w=q['thermal_resistance_m2k_w'],conditional_screen=c['conditional_deflection_screen'],pareto=c['candidate_id'] in fronts,installed_cost_usd=q['cost_usd'],qualified=False))
 outputs['comparison.csv']=table.getvalue().encode()
 summary=dict(schema='osr-composite-panel-study/1',candidate_count=len(cases),conditional_pareto_candidate_ids=fronts,
  optimisation_status='mass/compliance development frontier; thermal, fatigue, repair and commercial selection incomplete',
  qualified_candidates=0,selected_released_design=None,missing_properties=['measured hot/wet allowables','fatigue/S-N curves','joint/insert allowables','complete-stack fire tests','roof service-temperature allowable','supplier costs','timed replacement'],
  baseline_train_mass_or_bom_price_changed=False,physical_release=False)
 outputs['summary.json']=encoded(summary)
 text=['# Hybrid GFRP exterior-panel development','',f"{len(cases)} conditional panel/support combinations; no candidate is released or changes the train mass/BOM.",'',
  '![Layered development section](section.svg)','', '[Interactive comparison](report.html) · [Complete-scope RFQ prepared for review](rfq.json).','',
  'The metal frame remains the main structural load path. HVAC, PV, lifting and personnel loads pass into its dedicated supports. The reference section has two 1.5 mm eight-ply skins, two 0.2 mm bonds, 24.6 mm core and a separate 0.3 mm finish. Material values, pressure, ageing factors and roof crown are explicit development assumptions.','',
  '[Complete comparison](comparison.csv) varies skin, core depth/density, module width, clip/support span, roof crown and hat-rib depth. Rib mass is counted; rib stiffness and bond benefits await evidence. Mass includes solid edge lands, potting, inserts, clips, retention, seals and finish. Curvature earns no stiffness credit. Classical laminate ABD and one-way pressure-strip bending plus core shear are numerical screens, not plate/clip fatigue or debonding qualification. Density variants retain a hypothetical common core stiffness: supplier-grade property curves are required before selection.','',
  '[Reference panels](reference-panels.json) · [Actual aperture-based 144-module inventory](trainset-takeoff.json) · [Steel/aluminium comparisons](metal-comparators.json) · [All candidates](candidates.json). Shared-joint seal quantities remain a gross allowance; the cutout clip map and final roof crown remain unreleased. Bare 2 mm metal sheets are unequal-performance comparators. Separate metal plate assemblies are thickness-sized to the same pressure/support/deflection surrogate and include common attachment, finish and insulation allowances. This is not an optimum metal stiffener design or demonstrated equivalent rail behaviour. No whole-train saving is claimed.','',
  '[Prototype/quotation status](prototype-and-quotation-status.json) derives from the editable [evidence register](../evidence/register.json). Record candidate ID, dry/hot-wet condition, metre-valued measured deflection, uncertainty and original-file SHA-256 for correlation. Tests must reproduce the candidate pressure/support/material configuration. Quotations require the complete named scope. Empty records stay unknown; the $11,000 B6/B7 allowance is a comparator, not a quote.','',
  'Coupon tests precede a clipped side module and an equipment-adjacent roof bay. The register covers aged stiffness/bond/pull-out, pressure, clip loss, vibration/fatigue, impact, heat beneath PV, ingress, UV/sand/wash, bonding and measured replacement. Fire requirement set/hazard level and the exact complete stack remain unfrozen.','',
  'Regenerate: `.venv/bin/python tools/automation/composite-panel-study.py`; use `--check` for source/output drift. [Native layered side and curved roof CAD](cad/verification.json) validates nonoverlapping solids and independent volumes; curved roof insert lands remain separate development. Native CAD export/volume verification uses `tools/automation/verify-composite-panel-cad.py` in FreeCAD. Native exports do not establish physical performance.','',
  'Supplier and standards references: [BSI EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2), [Sicomin SR1124](https://sicomin.com/en/epoxy-products/epoxy/contact-vacuum-lamination/sr-1124/), [its datasheet](https://sicomin.com/datasheets/sr1124_sr477x.pdf), [AIREX T90](https://www.3accorematerials.com/en/markets-and-products/airex-foam/airex-t90-fire-resistant-foam), [Mat4Rail results](https://cordis.europa.eu/project/id/777595/reporting). Supplier resin Tg and core thermal stability are separate from allowable panel service temperature.','']
 outputs['README.md']='\n'.join(text).encode()
 sources=[Path(__file__),config_path,evidence_path,ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/composite_panels.py',ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/car_body.py',ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/modular_fiberglass_body.py',ROOT/'docs/rolling-stock/light-metro-3car/bom-skeleton.md',*[ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('common.py','family_definition.py','provenance.py')]]
 for record in [*register['tests'],*register['quotes']]:sources.append(ROOT/record['source_path'])
 sources.extend([receipt_path,*[cad_dir/r['output'] for r in receipt['records']]])
 outputs['manifest.json']=encoded(dict(schema='osr-composite-panel-study-manifest/1',sources_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},outputs_sha256={n:hashlib.sha256(v).hexdigest() for n,v in outputs.items()},physical_release=False))
 return outputs

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
 outputs=build();OUT.mkdir(parents=True,exist_ok=True)
 for name,data in outputs.items():
  path=OUT/name
  if args.check:
   if not path.exists() or path.read_bytes()!=data:raise ValueError('Stale composite-panel artifact: '+name)
  else:path.write_bytes(data)
 print('Hybrid panel development:',json.loads(outputs['summary.json'])['candidate_count'],'conditional candidates; qualification open')
if __name__=='__main__':main()
