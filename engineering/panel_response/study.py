"""Source-bound refinement and holdout study for installed clipped side bays."""
from pathlib import Path
import hashlib,json
import numpy as np
from osr_mech.engineering_definition import fingerprint
from engineering.design_consistency.demonstrators import panel_bay
from engineering.design_consistency.contracts import summary,part,validate
from osr_mech.section_contract import rhs,geometry
from copy import deepcopy
from .plate import solve,single_clip_envelope,regions
from .verification import native
ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'engineering/composite_panels/config/development.json'


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sources():
    paths=sorted((ROOT/'engineering/panel_response').glob('*.py'))+[CONFIG,ROOT/'tools/automation/panel-response-study.py',ROOT/'tools/automation/verify-panel-response-cad.py']
    paths += [ROOT/'engineering/design_consistency'/p for p in ('demonstrators.py','contracts.py')]
    paths += [ROOT/'design/component-catalogue/src/osr_mech'/p for p in ('automated_geometry.py','engineering_definition.py','section_contract.py','rolling_stock/composite_panels.py')]
    return {p.relative_to(ROOT).as_posix():sha(p)for p in paths}


def deeper_rails(contract,depth=.04):
    """Keep the clip contact plane; regenerate deeper walls and bracket/frame datums."""
    model=deepcopy(contract);network=model['support_network'];old=network['section'];section=rhs(old['width_m'],depth,old['wall_m'],density_kg_m3=old['density_kg_m3'])
    shift=-(depth-old['height_m'])/2;network['section']=section
    for rail in network['rails']:
        a,b=rail['interval_m'];y=rail['station_m'];spec=geometry(section,b-a,centre_m=((a+b)/2,y,-.045+shift));rail['geometry']=deepcopy(spec)
        rail['mass_kg']=(b-a)*section['mass_kg_m']
        top=spec['primitives'][0];top.update(kind='plate',holes_xy_m=[[-.3*(b-a),0],[.3*(b-a),0]],hole_radius_m=.00325)
        index=next(i for i,p in enumerate(model['parts'])if p['id']==rail['id']);original=model['parts'][index]
        model['parts'][index]=part(rail['id'],original['material'],spec,model['materials'],section=section,inspections=original['inspection_characteristics'])
    for i,p in enumerate(model['parts']):
        # Frame remains behind the deepest rail, instead of overlapping new walls.
        delta=2*shift if p['id'].startswith('aperture-')else shift if '-bracket-'in p['id']or '-fastener-'in p['id']else 0
        if delta:
            spec=deepcopy(p['manufacturing'])
            for primitive in spec['primitives']:primitive['centre_m'][2]+=delta
            model['parts'][i]=part(p['id'],p['material'],spec,model['materials'],inspections=p['inspection_characteristics'])
    network['rail_mass_kg']=sum(p['properties']['mass_kg']for p in model['parts']if p['id']in {r['id']for r in network['rails']})
    network['mass_kg']=network['rail_mass_kg']+sum(p['properties']['mass_kg']for p in model['parts']if '-bracket-'in p['id']or '-fastener-'in p['id'])
    model['support_variation']=dict(rail_depth_m=depth,clip_contact_plane_unchanged=True,frame_shift_m=2*shift,bracket_shift_m=shift)
    validate(model);return model


def contracts():
    config=json.loads(CONFIG.read_text());models={name:panel_bay(config,span=span)for name,span in [('baseline',1),('closer-supports',.5),('dense-supports',.33),('tight-supports',.2)]}
    models['deeper-rails']=deeper_rails(models['baseline']);return models


def generate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);models=contracts();results={};rows=[]
    rejected=panel_bay(json.loads(CONFIG.read_text()),span=.35)
    try:regions(rejected)
    except ValueError as error:reason=str(error)
    else:raise ValueError('expected unsafe potting regression was not rejected')
    (output/'rejected-035-contract.json').write_bytes(encoded(rejected))
    (output/'manufacturing-rejection.json').write_bytes(encoded(dict(schema='osr-panel-manufacturing-rejection/1',
        contract_sha256=fingerprint(rejected),nominal_span_m=.35,reason=reason,manufacturing_geometry='failed',
        eligible_for_ranking=False,physical_validation=False,production_released=False)))
    for name,contract in models.items():
        (output/(name+'.json')).write_bytes(encoded(contract));pair=[]
        for level,mesh in [('coarse',.08),('refined',.04)]:
            result=solve(contract,mesh_size=mesh);(output/(name+'-'+level+'.json')).write_bytes(encoded(result));results[(name,level)]=result;pair.append(result)
        coarse,fine=pair;difference=abs(coarse['maximum_deflection_m']/fine['maximum_deflection_m']-1)
        envelope=single_clip_envelope(contract);(output/(name+'-clip-loss-envelope.json')).write_bytes(encoded(envelope))
        if envelope['worst']['status']=='unstable':raise ValueError('instability requires an explicitly blocked candidate, not a plotted finite response')
        failure=envelope['worst']['failed_clip']
        degraded=solve(contract,mesh_size=.04,failed_clip=failure);(output/(name+'-failed-clip.json')).write_bytes(encoded(degraded))
        holdout=solve(contract,mesh_size=.04,pressure_pa=3500);(output/(name+'-holdout.json')).write_bytes(encoded(holdout))
        combined=solve(contract,mesh_size=.04,pressure_pa=3500,failed_clip=failure);(output/(name+'-combined-holdout.json')).write_bytes(encoded(combined))
        softened=solve(contract,mesh_size=.04,clip_stiffness_factor=.1);(output/(name+'-soft-joints.json')).write_bytes(encoded(softened))
        rows.append(dict(name=name,contract_sha256=fingerprint(contract),defined_mass_kg=summary(contract)['mass_kg'],
            actual_maximum_support_pitch_m=contract['support_network']['actual_max_pitch_m'],rail_count=contract['support_network']['rail_count'],clip_count=len(fine['attachments']),
            strip_deflection_m=contract['response']['total_deflection_m'],plate_rail_deflection_m=fine['maximum_deflection_m'],
            pressure_pa=2000,deflection_screen=fine['deflection_screen'],refinement_relative_difference=difference,
            numerical_refinement_screen='passed'if difference<.03 else'failed',
            single_clip_case_count=envelope['case_count'],failed_clip=failure,failed_clip_maximum_deflection_m=degraded['maximum_deflection_m'],failed_clip_deflection_screen=degraded['deflection_screen'],
            holdout_pressure_pa=3500,holdout_maximum_deflection_m=holdout['maximum_deflection_m'],holdout_deflection_screen=holdout['deflection_screen'],
            combined_holdout_maximum_deflection_m=combined['maximum_deflection_m'],combined_holdout_deflection_screen=combined['deflection_screen'],
            soft_joint_maximum_deflection_m=softened['maximum_deflection_m'],
            maximum_clip_force_n=fine['maximum_clip_force_n'],clip_strength_qualified=False,
            joint_fire_fatigue_and_physical_status='unknown',qualified=False))
        print(name,'deflection mm',round(fine['maximum_deflection_m']*1000,3),'mass kg',round(rows[-1]['defined_mass_kg'],3),flush=True)
    check=native(output/'native-benchmark')
    report=dict(schema='osr-panel-response-study/1',cases=rows,formulation='rectangular MITC4 plate + discrete series clip/insert springs + hollow Euler-Bernoulli rails',
        native_formulation_screen_passed=check['numerical_screen_passed'],verified_designs=[],
        manufacturing_mapping='shared part IDs, ply angles/thickness, trimmed footprint, solid lands, core/insert regions, rail sections and clip locations',
        scope='dry nominal elastic global deflection/load sharing; not local 3D contact, pull-out, debonding, fatigue, fire or roof-shell qualification',
        physical_validation=False,production_released=False)
    (output/'summary.json').write_bytes(encoded(report));plot(output,models,results,rows)
    paths=[p for p in output.rglob('*')if p.is_file()and(p.suffix in ('.json','.inp','.dat','.log','.png'))and p.name not in ('manifest.json','verification.json')and 'cad'not in p.relative_to(output).parts]
    paths.append(output/'native-benchmark/verification.json')
    manifest=dict(schema='osr-panel-response-manifest/1',source_sha256=sources(),
        output_sha256={p.relative_to(output).as_posix():sha(p)for p in sorted(paths)},physical_validation=False,production_released=False)
    (output/'manifest.json').write_bytes(encoded(manifest));return report


def plot(output,models,results,rows):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes=plt.subplots(1,len(rows),figsize=(3*len(rows),8),layout='constrained')
    scale=max(r['plate_rail_deflection_m']for r in rows)*1000
    for ax,row in zip(axes,rows):
        result=results[(row['name'],'refined')];xy=np.array(result['nodes_m']);u=np.array(result['displacement_m'])*1000
        polygons=[xy[cell]for cell in result['elements']];colours=[float(np.mean(u[cell]))for cell in result['elements']]
        collection=PolyCollection(polygons,array=np.array(colours),cmap='viridis',clim=(0,scale));ax.add_collection(collection)
        locations=xy[[a['plate_node']for a in result['attachments']]];ax.scatter(locations[:,0],locations[:,1],s=10,c='red')
        ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Module width (m)');ax.set_title(row['name']+'\n'+f"{row['plate_rail_deflection_m']*1000:.2f} mm · {row['defined_mass_kg']:.1f} kg")
    axes[0].set_ylabel('Developed height (m)');fig.colorbar(collection,ax=axes,label='Dry elastic deflection (mm)',shrink=.5)
    fig.suptitle('Trimmed bay and actual attachments/rails — unqualified research response')
    fig.savefig(output/'deflection-comparison.png',dpi=160);plt.close(fig)


def verify(output):
    output=Path(output);manifest=json.loads((output/'manifest.json').read_text())
    if manifest['source_sha256']!=sources():raise ValueError('panel-response source drift')
    for relative,digest in manifest['output_sha256'].items():
        path=(output/relative).resolve()
        if not path.is_relative_to(output.resolve())or sha(path)!=digest:raise ValueError('changed/unsafe panel-response output: '+relative)
    for name,model in contracts().items():
        if fingerprint(json.loads((output/(name+'.json')).read_text()))!=fingerprint(model):raise ValueError('panel contract no longer reproduces')
    path=output/'cad/verification.json'
    if path.is_file():
        receipt=json.loads(path.read_text())
        if receipt['source_sha256']!=sources():raise ValueError('native panel source drift')
        for relative,digest in receipt['output_sha256'].items():
            target=(output/relative).resolve()
            if not target.is_relative_to(output.resolve())or sha(target)!=digest:raise ValueError('changed native panel output')
    return manifest
