#!/usr/bin/env python3
"""Render recorded JSON only. No CAD/FEM imports, replays or native execution."""
import argparse, hashlib, json, platform
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
P=Path(__file__).resolve().parent
B=P.parent
W=Path('/home/hayder/.local/state/opensourcerail/worktrees/craft-viaduct-20261107')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def write(name,v): (P/name).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n')
request=read(B/'cad/run01/request.json'); cad=read(B/'cad/run01/manifest.json')
portfolio_path=W/'docs/design-engine/civil-shape-portfolio/result.json'
portfolio=read(portfolio_path); priced={r['candidate_id']:r for r in portfolio['evaluations']}
rows=[]
for case in request['cases']:
 r=priced[case['candidate_id']]; assert r['quantities']==case['canonical_quantities']
 m=cad['cases'][case['case_id']]; assert m['candidate_id']==case['candidate_id'] and m['exact_step']['comparison_passed']
 c=r['cost_estimate']; base=next(x for x in c['cases'] if x['case']=='base')
 rows.append(dict(case_id=case['case_id'],candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],cad_evaluation_id=m['evaluation_id'],cost_evaluation_id=r['evaluation_id'],family=case['family'],profile=case['profile'],nominal_stock_mass_kg=r['quantities']['total_nominal_stock_mass_kg'],structural_factory_base_iqd=base['factory_gate_iqd'],rail_interface_base_iqd=c['line_items_iqd']['rails_and_fastenings']['base'],scoped_installed_base_iqd=base['scoped_installed_iqd']))
assert len(rows)==12 and {r['rail_interface_base_iqd'] for r in rows}=={52084000.0}
colors=['#245c99','#009e73','#8c564b','#a14998','#d88900','#258e9b']
families=['reference_box','ribbed_u','variable_depth_box','folded_plate','hybrid_steel_concrete','load_following_ribs']
names=['Box','Ribbed U','Variable-depth box','Folded plate','Steel–concrete hybrid','Load-following ribs']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#253347','text.color':'#253347','axes.edgecolor':'#aab4c1','savefig.facecolor':'white'})
fig,ax=plt.subplots(figsize=(13.6,8.2)); fig.subplots_adjust(left=.09,right=.97,top=.83,bottom=.23)
fig.suptitle('Twelve exact span geometries: mass and structural factory cost',x=.09,ha='left',y=.97,fontsize=21,fontweight='bold')
fig.text(.09,.90,'20 m single-track nominal stock • dated Iraqi benchmarks + Class C process assumptions',fontsize=12)
fig.text(.09,.86,'No China quotation, procurement approval or complete installed bridge cost is implied.',fontsize=11,color='#59677a')
offsets={('reference_box','reference'):(-72,-24),('reference_box','robust'):(-90,12),('ribbed_u','reference'):(-4,-34),('ribbed_u','robust'):(8,-12),('variable_depth_box','reference'):(-60,17),('variable_depth_box','robust'):(-23,18),('folded_plate','reference'):(12,-31),('folded_plate','robust'):(-100,5),('load_following_ribs','reference'):(-7,24),('load_following_ribs','robust'):(-30,-32),('hybrid_steel_concrete','reference'):(15,-12),('hybrid_steel_concrete','robust'):(15,6)}
for fam,col,name in zip(families,colors,names):
 group=[r for r in rows if r['family']==fam]; group.sort(key=lambda r:r['nominal_stock_mass_kg'])
 ax.plot([r['nominal_stock_mass_kg']/1000 for r in group],[r['structural_factory_base_iqd']/1e6 for r in group],color=col,alpha=.35,lw=1.3)
 for r in group:
  x,y=r['nominal_stock_mass_kg']/1000,r['structural_factory_base_iqd']/1e6
  ax.scatter(x,y,s=110,marker='o' if r['profile']=='reference' else 'D',facecolor=col if r['profile']=='reference' else 'white',edgecolor=col,lw=1.8,zorder=3)
  ax.annotate(name+'\n'+r['profile'],(x,y),xytext=offsets[(fam,r['profile'])],textcoords='offset points',fontsize=9,color=col,arrowprops=dict(arrowstyle='-',color=col,alpha=.4,lw=.7))
ax.set_yscale('log'); ax.set_yticks([12,16,20,40,80,160,220]);ax.yaxis.set_major_formatter(ScalarFormatter());ax.set_ylim(10,260);ax.set_xlim(25,75)
ax.set_xlabel('Nominal concrete + structural steel stock (tonnes)');ax.set_ylabel('Structural factory-gate estimate (million IQD, base; logarithmic scale)');ax.grid(axis='y',which='major',color='#e5eaf0');ax.set_axisbelow(True)
fig.text(.09,.14,'Separate common rail interface: IQD 52.084m per 20 m span',fontsize=13,fontweight='bold',bbox=dict(boxstyle='round,pad=.6',facecolor='#edf3f8',edgecolor='none'))
fig.text(.09,.082,'Factory estimate includes provisional reinforcement/prestress, processes, QA, tooling allocation and one overhead uplift.\nNominal stock omits those unresolved installed items. Circle: reference profile; hollow diamond: robust profile.',fontsize=10,color='#59677a')
fig.savefig(P/'mass-factory-cost.png',dpi=180);plt.close(fig)
fem=[];sources={}
for fam in ['reference_box','folded_plate']:
 folder=B/f'fem/epoch04-{fam}'; top=read(folder/'result.json'); inp=read(folder/'input.json');sources[str((folder/'result.json').relative_to(B))]=sha(folder/'result.json');sources[str((folder/'input.json').relative_to(B))]=sha(folder/'input.json')
 for level,l in top['levels'].items():
  r=l['results']
  for solver in ['fieldcraft','calculix']:
   d=r.get(solver,{}).get('displacement_m')
   fem.append(dict(family=fam,level=level,solver=solver,vertical_deflection_m=None if d is None else -d[2],candidate_id=top['candidate_id'],evaluation_id=top['evaluation_id'],result_id=top['result_id'],mesh_id=l['mesh_id'],elements=l['element_count'],nodes=l['node_count'],resource_memory_MiB=2048,state='held-no-valid-displacement' if d is None else 'recorded-displacement',source_result=str((folder/'result.json').relative_to(B))))
 resource=None
 if fam=='reference_box':
  rp=B/'fem/resource01-box-fine-3072MiB/result.json';resource=read(rp);assert resource['candidate_id']==top['candidate_id']
  sources[str(rp.relative_to(B))]=sha(rp)
  fem.append(dict(family=fam,level='fine',solver='fieldcraft',vertical_deflection_m=-resource['fieldcraft']['displacement_m'][2],candidate_id=resource['candidate_id'],evaluation_id=resource['evaluation_id'],result_id=resource['result_id'],resource_memory_MiB=3072,state=resource['state'],source_result=str(rp.relative_to(B))))
write('plot-data.json',dict(schema='osr-viaduct-presentation/1',cad_request_id=request['request_id'],cad_result_id=cad['result_id'],cost_basis='2026-10-31 Class C assumptions using 2026-07 Iraqi material/wage benchmarks; not China procurement prices',cost_portfolio_sha256=sha(portfolio_path),cad_request_sha256=sha(B/'cad/run01/request.json'),cad_manifest_sha256=sha(B/'cad/run01/manifest.json'),cad_cases=rows,fem_cases=fem,raw_fem_source_sha256=sources,structural_hypotheses='20 m uncracked linear elastic perfectly bonded nominal concrete; bilateral restrained bearing patches, not unilateral contact; common crowd_control live-load context with 1.3 dynamic factor once; declared dead-load accounts; no resistance or qualification',selected_reference_six_part_mass_kg=55704,portfolio_box_four_wall_mass_kg=54720,selected_mass_comparison='Different physical candidates/scopes; never interchangeable'))
fig,axes=plt.subplots(1,2,figsize=(13.6,7.4));fig.subplots_adjust(left=.075,right=.97,top=.76,bottom=.26,wspace=.24)
fig.suptitle('Actual 20 m span FEM: coarse and fine displacement comparisons',x=.075,ha='left',y=.97,fontsize=20,fontweight='bold')
fig.text(.075,.90,'SolidCraft geometry → Gmsh solid mesh → FieldCraft / CalculiX',fontsize=12)
fig.text(.075,.85,'Bilateral bearing restraints • uncracked, perfectly bonded elastic research models',fontsize=11,color='#59677a')
for ax,fam,title in zip(axes,['reference_box','folded_plate'],['Reference box — 54.720 t nominal','Folded plate — 32.480 t nominal']):
 group=[r for r in fem if r['family']==fam and r['vertical_deflection_m'] is not None]
 for solver,col,mark,dx in [('fieldcraft','#245c99','o',-.035),('calculix','#d06a28','s',.035)]:
  g=sorted([r for r in group if r['solver']==solver],key=lambda r:r['level']=='fine')
  xs=[(r['level']=='fine')+dx for r in g];ys=[r['vertical_deflection_m']*1000 for r in g]
  ax.plot(xs,ys,color=col,ls='-' if solver=='fieldcraft' else '--',marker=mark,ms=8,lw=1.8,label='FieldCraft' if solver=='fieldcraft' else 'CalculiX')
 for level in ['coarse','fine']:
  r=next(r for r in group if r['solver']=='fieldcraft' and r['level']==level)
  ax.annotate(f"{r['vertical_deflection_m']*1000:.4f} mm",((level=='fine')-.035,r['vertical_deflection_m']*1000),xytext=(0,13),textcoords='offset points',ha='center',fontsize=11,fontweight='bold',color='#245c99')
 ax.set_title(title,loc='left',fontsize=13,pad=16);ax.set_xticks([0,1],['Coarse mesh','Fine mesh']);ax.set_xlim(-.28,1.28);ax.grid(axis='y',color='#e5eaf0');ax.set_ylabel('Downward vertical displacement at observation node (mm)');ax.legend(loc='lower left',frameon=False,fontsize=10);ax.margins(y=.5)
 if fam=='reference_box':
  ax.text(.5,.06,'2 GiB fine FieldCraft: held\nFine blue point: separate fresh 3 GiB evaluation',transform=ax.transAxes,ha='center',va='bottom',fontsize=9,color='#8b4f20',bbox=dict(facecolor='#fff4e8',edgecolor='none',pad=6))
fig.text(.075,.15,'Values from immutable recorded results; nearly coincident solver points are offset horizontally for visibility.',fontsize=10)
fig.text(.075,.09,'Two mesh levels are a sensitivity check, not established mesh independence. Bearing contact, cracking, prestress,\nreinforcement resistance, construction stages and complete installed mass remain open. No physical qualification.',fontsize=10,color='#59677a')
fig.savefig(P/'fem-deflection.png',dpi=180);plt.close(fig)
images={str(p.relative_to(B)):sha(p) for p in [B/'cad/reference_box-snapshot01/assembly.png',B/'cad/folded_plate-snapshot01/assembly.png']}
(P/'README.md').write_text('''# Twelve viaduct outlines, with traceable CAD, quantities and costs\n\nTwelve 20 m outline geometries across six structural families now have exact native CAD and joined provisional material/process costs. Two reference-profile geometries also have actual solid-element FEM results compared between FieldCraft and CalculiX. This is useful outline and numerical evidence; the selected railway reference is unchanged.\n\n![Nominal stock and structural factory costs](mass-factory-cost.png)\n\nThese are dated IQD estimates, not new Chinese supplier quotations or corridor budgets. The common rail/fastener allowance is shown separately so it cannot hide the structural comparison or be charged twice. Manufacturing allowances do not establish a bar schedule, prestress design, removable mould, lifting plan or assembly acceptance.\n\n![Recorded coarse/fine FEM displacement](fem-deflection.png)\n\nThe box changes from 11.8253 to 11.5231 mm downward displacement; the folded plate from 19.0331 to 18.9079 mm under their declared load and elastic hypotheses. The original 2 GiB fine box FieldCraft execution remains held. Its plotted fine point comes from a separate successful 3 GiB resource evaluation; no original receipt was changed. Two mesh levels do not establish mesh independence.\n\nThe models use bilateral restrained bearing patches and uncracked, perfectly bonded elasticity. Tensile support reactions require real contact/restraint resolution; these are not validated bearings. Cracking, reinforcement/prestress resistance, fatigue, construction stages, installed connections and manufacturing access remain open.\n\n**Mass scopes differ:** the selected six-part reference assembly is 55.704 t; the four-wall portfolio reference box is 54.720 t. They are different physical definitions, not two measurements of the same assembly. Neither is complete installed mass.\n\nNative CAD images remain unmodified at `cad/reference_box-snapshot01/assembly.png` and `cad/folded_plate-snapshot01/assembly.png` in the private run. Their hashes are recorded in this presentation manifest.\n\nNext: develop removable/reusable moulds and reinforcement/anchorage layouts; resolve actual bearing contact and temporary lifting stability; then refine load cases and manufacturing routes. Detailed acceptance and physical qualification remain pending.\n\n`plot-data.json` preserves exact plotted values, physical/evaluation identities and raw-result hashes. `plot-script.py` only reads recorded JSON and renders plots; it does not replay FEM.\n''')
files={p.name:sha(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='manifest.json'}
write('manifest.json',dict(schema='osr-viaduct-presentation-manifest/1',artifact_sha256=files,unaltered_native_cad_image_sha256=images,python=platform.python_version(),matplotlib=matplotlib.__version__,source_evaluations_replayed=False,native_jobs=0,physical_accepted=False,engineering_accepted=False,selected_reference_changed=False))
print(json.dumps({'output':str(P),'files':len(files),'bytes':sum(p.stat().st_size for p in P.iterdir() if p.is_file()),'manifest_sha256':sha(P/'manifest.json')}))
