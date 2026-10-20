"""Qualified-runner companion for material comparison and owned-section CAD.

Native exhibits deliberately cover the defined skins/lands/bonds or sharp-corner
face/hats and optional rear insulation only. They cannot confirm the omitted
core/potting, complete fastenings, formed roof or installed manufacturing system.
"""
import math
from html import escape
from pathlib import Path
from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from engineering.continuous_design import study_confirmation
from engineering.continuous_design import beam_confirmation
from engineering.panel_materials import study


def section(config,baseline,ctx,row):
    if row!=study.candidate(config,baseline,ctx,row['route'],row['variables']):
        raise ValueError('panel candidate differs from controlled generator')
    w,L=ctx['width_m'],ctx['developed_length_m'];v=row['variables'];a=config['aluminium']
    mats=dict(skin=dict(density_kg_m3=a['density_kg_m3'] if row['route']!='gfrp-sandwich' else baseline['glass']['density_kg_m3']),
        bond=dict(density_kg_m3=baseline['bond']['density_kg_m3']),core=dict(density_kg_m3=row['core_grade']['density_kg_m3']))
    parts=[]
    def add(identity,x0,x1,y0,y1,z0,z1,material='skin'):
        if min(x1-x0,y1-y0,z1-z0)<=0:raise ValueError('manufacturable positive section dimensions required')
        p=contracts.part(identity,material,dict(role=identity,primitives=[contracts.box(identity,x1-x0,y1-y0,z1-z0,[(x0+x1)/2,(y0+y1)/2,(z0+z1)/2])]),mats,
            limits=dict(tolerance_m=None,tolerance_status='unissued',minimum_wall_m=None),
            inspections=['material identity','skin/section thickness','layer dimensions and datum','bond/formed-corner qualification remains open'])
        p.update(geometric_role='owned-research-solid',procurement=None,process_route='Cut/form or laminate to provisional section; bend radius, curing and tolerances unqualified',
            manufacturing_unit_id='panel/'+row['id'],datum_scheme=dict(A='outer-surface plane',B='developed longitudinal edge',C='module end'))
        parts.append(p)
    if row['route']=='stiffened-aluminium':
        skin=v['sheet_m'];depth=v['hat_depth_m'];hat=config['hat'];wall=hat['wall_m'];crown=hat['crown_width_m'];foot=hat['foot_width_each_m']
        add('face',0,w,0,L,0,skin)
        for i,x in enumerate(row['model']['hat_stations_x_m']):
            for sign in (-1,1):
                web=x+sign*(crown-wall)/2
                add(f'hat-{i}-web-{sign}',web-wall/2,web+wall/2,0,L,skin,skin+depth)
                f=x+sign*(crown/2+foot/2)
                add(f'hat-{i}-foot-{sign}',f-foot/2,f+foot/2,0,L,skin,skin+wall)
            add(f'hat-{i}-crown',x-crown/2,x+crown/2,0,L,skin+depth,skin+depth+wall)
        covered=['face','hats'];expected=row['mass_components_kg']['face']+row['mass_components_kg']['hats'];top=skin+depth+wall
    else:
        skin,depth,bond=v['skin_m'],v['core_m'],baseline['bond']['thickness_m_each'];land=baseline['panel']['edge_land_m']
        add('outer-skin',0,w,0,L,0,skin)
        add('outer-bond',0,w,0,L,skin,skin+bond,'bond')
        start=skin+bond;stop=start+depth
        for name,rect in [('near',(0,w,0,land)),('far',(0,w,L-land,L)),('left',(0,land,land,L-land)),('right',(w-land,w,land,L-land))]:
            add('edge-land-'+name,*rect,start,stop)
        add('inner-bond',0,w,0,L,stop,stop+bond,'bond')
        add('inner-skin',0,w,0,L,stop+bond,stop+bond+skin)
        covered=['skins_and_solid_edge_lands','bond'];expected=sum(row['mass_components_kg'][key] for key in covered);top=stop+bond+skin
    if v.get('thermal_backer_m'):
        add('continuous-rear-insulation',0,w,0,L,top,top+v['thermal_backer_m'],'core')
        covered.append('continuous_thermal_backer');expected+=row['mass_components_kg']['continuous_thermal_backer']
    revision=core.digest(dict(analytical_id=row['id'],context=ctx['revision'],parts=parts,materials=mats))
    for p in parts:p['revision']=revision
    contract=dict(schema='osr-engineering-representations/1',name='panel-owned-section',revision=revision,
        parts=parts,materials=mats,assembly_joints=[],construction_stages=[],
        mandatory_evidence=['Complete native panel reconstruction','Formed roof/bend, bond and mount qualification'],physical_validation=False,production_released=False)
    contracts.validate(contract);properties=contracts.summary(contract)
    if not math.isclose(properties['mass_kg'],expected,rel_tol=1e-10):raise ValueError('owned panel-section mass does not reconcile')
    candidate=dict(schema='osr-assembly-design-candidate/1',kind='panel-owned-section',revision=revision,variables=v,contract=contract,
        metadata=dict(architecture='panel-benchmark-unadopted',
            geometry_basis='Historical module research footprints; not adopted Baghdad six-car body dimensions'),
        analytical_candidate_id=row['id'],context_revision=ctx['revision'],represented_mass_components=covered,
        unrepresented_mass_components=sorted(set(row['mass_components_kg'])-set(covered)),
        complete_analytical_installed_mass_kg=row['installed_mass_kg'],full_native_reconstruction=False,
        assembly_steps=['Prepare and inspect provisional section layers','Form/laminate in fixture','Inspect section datums; complete mounts/QA remain open'],
        qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False) for p in parts],
        source_scope='Owned developed-coordinate section exhibit only; '+row['route']+' '+row['kind']+'; no complete installed panel or formed roof confirmation',
        open_requirements=list(study.OPEN),**core.FLAGS)
    checks=dict(owned_mass_inventory=True,positive_manufacturing_dimensions=True,**row['screening_checks'])
    checks.update({name:None for name in ('full-native-panel','bend-radii-and-tool-access','thermal-break-attachment-creep','complete-stack-temperature-fire','physical-and-commercial-evidence')})
    assessment=dict(candidate_revision=revision,checks=checks,failed_checks=[k for k,val in checks.items() if val is False],held_checks=[k for k,val in checks.items() if val is None],
        state='failed' if any(val is False for val in checks.values()) else 'hold',**core.FLAGS)
    return candidate,assessment


def independent_controls(config,ctx,row,candidate):
    if row['route']=='gfrp-sandwich':
        return dict(state='hold',scope='Native material quantities only; independent anisotropic whole-panel response remains open')
    names=('face','hat-') if row['route']=='stiffened-aluminium' else ('outer-skin','inner-skin')
    rectangles=[]
    for part in candidate['contract']['parts']:
        if not any(part['id']==name or part['id'].startswith(name) for name in names):continue
        for primitive in part['manufacturing']['primitives']:
            dx,dy,dz=primitive['dimensions_m'];rectangles.append((dx*dz,primitive['centre_m'][2],dx*dz**3/12))
    area=math.fsum(a for a,z,i in rectangles);centre=math.fsum(a*z for a,z,i in rectangles)/area
    inertia=math.fsum(i+a*(z-centre)**2 for a,z,i in rectangles)
    stiffness=inertia*config['aluminium']['young_pa']*config['aluminium']['stiffness_sensitivity_factor']
    span=ctx['ideal_simple_span_m'];uniform=ctx['pressure_pa']*ctx['width_m']
    meshes=[beam_confirmation.solve(span,[0.,span],stiffness,uniform=uniform,divisions=n) for n in (16,32)]
    adverse=beam_confirmation.solve(span,[0.,span],stiffness,uniform=2*uniform,divisions=32)
    target=row['model'].get('global_beam_deflection_m',row['model'].get('bending_deflection_m'))
    checks=dict(geometry_recovered_bending=abs(meshes[-1]['maximum_nodal_deflection_m']/target-1)<1e-7,
        refinement=abs(meshes[-1]['maximum_nodal_deflection_m']/meshes[0]['maximum_nodal_deflection_m']-1)<1e-7,
        adverse_scaling=abs(adverse['maximum_nodal_deflection_m']/meshes[-1]['maximum_nodal_deflection_m']-2)<1e-7,
        equilibrium=meshes[-1]['force_balance_relative_error']<1e-8)
    if not all(checks.values()):raise ValueError('independent panel beam control failed')
    return dict(state='passed-scoped-bending-controls',checks=checks,section_inertia_m4=inertia,
        meshes=meshes,adverse=adverse,scope='Independent Hermite FE using inertia recovered from the owned metal geometry; local skin, core shear, joints/contact and full panel remain unqualified')


def campaign(prepared,folder):
    from . import design_studies
    folder=Path(folder);folder.mkdir()
    config,base=core.read(study.CONFIG),core.read(study.BASELINE)
    contexts,rows=study.generate_cases(config,base);byid={r['id']:r for r in rows};byctx={c['revision']:c for c in contexts};models=[]
    for rep in study.representatives(rows):
        row=byid[rep['candidate_id']];name=row['kind']+'-'+row['route'];path=folder/name
        candidate,assessment=section(config,base,byctx[row['context_revision']],row)
        controls=independent_controls(config,byctx[row['context_revision']],row,candidate)
        model=design_studies._model(candidate,assessment,path)
        models.append(dict(path=name,analytical_candidate=row,selection=rep,model=model,
            independent_controls=controls,
            complete_installed_assembly_confirmed=False,engineering_eligible=False))
    result=dict(schema='osr-qualified-panel-companion/1',source_epoch=core.digest(prepared),candidate_count=len(rows),models=models,
        scope='Automatic bounded research adapter in the qualified assembly runner; six scoped native section exhibits, not full panel/vehicle manufacturing completion',**core.FLAGS)
    core.write(folder/'summary.json',result);(folder/'index.html').write_text(presentation(result));return result


def presentation(result):
    h=lambda value:escape(str(value),quote=True)
    lines=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Panel material research companion</title>',
        '<style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:1rem}img{max-width:100%;width:680px}code{overflow-wrap:anywhere}</style>',
        '<h1>Registered panel research companion</h1><p>'+h(result['candidate_count'])+' matched hypotheses; six retained section exhibits. These pictures show a subset of the installed panel geometry. Mounts, complete core/potting, formed roofs, process tolerances and physical qualification remain open.</p><p><a href="summary.json">Exact results and independent metal bending controls</a></p>']
    for item in result['models']:
        row=item['analytical_candidate'];base=item['path']+'/';model=item['model']
        lines+=['<h2>'+h(row['kind']+' / '+row['route'])+'</h2><p>Native state: '+h(model['native_state'])+'. Complete analytical installed mass '+h(round(row['installed_mass_kg'],3))+' kg; prices and complete-stack temperature/fire qualification remain unknown.</p>',
            '<p><a href="'+base+'candidate.json.gz">Exact owned subset and explicitly unrepresented mass components</a> | <a href="'+base+'assessment.json.gz">Failures and holds</a> | <a href="'+base+'manufacturing-bom.csv">Unissued subset BOM</a></p>']
        if model['native_state']=='passed':
            lines+=['<img alt="Native developed-coordinate owned-section subset; not a complete installed panel" src="'+base+'overview.png"><p><a href="'+base+'native/candidate.FCStd">Native section CAD</a> | <a href="'+base+'model.step.gz">Compressed STEP</a></p>']
    return '\n'.join(lines)+ '</html>'


def verify(prepared,folder):
    from . import design_studies
    result=core.read(Path(folder)/'summary.json',maximum=10_000_000)
    if any(result.get(flag) is not False for flag in core.FLAGS):raise ValueError('panel companion cannot grant release')
    config,base=core.read(study.CONFIG),core.read(study.BASELINE);contexts,rows=study.generate_cases(config,base)
    byid={r['id']:r for r in rows};byctx={c['revision']:c for c in contexts}
    if result['source_epoch']!=core.digest(prepared) or result['candidate_count']!=len(rows) or len(result['models'])!=6:
        raise ValueError('panel campaign epoch/domain differs')
    if (Path(folder)/'index.html').read_text()!=presentation(result):raise ValueError('panel companion presentation differs')
    expected_reps=study.representatives(rows)
    for record,rep in zip(result['models'],expected_reps):
        row=byid[rep['candidate_id']]
        if record['analytical_candidate']!=row or record['selection']!=rep or record['path']!=row['kind']+'-'+row['route']:
            raise ValueError('panel selection or analytical result differs')
        root=Path(folder)/record['path'];candidate,assessment=section(config,base,byctx[row['context_revision']],row)
        if record['independent_controls']!=independent_controls(config,byctx[row['context_revision']],row,candidate):
            raise ValueError('independent panel numerical evidence differs')
        if design_studies.read_record(root,'candidate.json')!=candidate or design_studies.read_record(root,'assessment.json')!=assessment:
            raise ValueError('panel CAD definition or check result differs')
        model=core.read(root/'result.json')
        if record['model']!=model or model['candidate_revision']!=candidate['revision']:
            raise ValueError('panel native model identity differs')
        if any(model.get(flag) is not False for flag in core.FLAGS):raise ValueError('panel native exhibit cannot grant release')
        if model['failed_checks']!=assessment['failed_checks'] or model['held_checks']!=assessment['held_checks']:
            raise ValueError('panel model failure/hold classification differs')
        if model['eligible_for_research']!=(model['native_state']=='passed' and not assessment['failed_checks']):
            raise ValueError('failed native panel exhibit cannot enter research shortlist')
        if model['native_state']=='passed':
            proof=core.read(root/'native/native-cad.json',maximum=10_000_000)
            if proof!=model['native_proof'] or proof['input_sha256']!=core.digest(candidate['contract']):
                raise ValueError('panel native correspondence differs')
            if any(proof.get(key) is not True for key in ('physical_ids_preserved','native_reopened','step_volume_reconciled','manufacturing_unit_ids_preserved')):
                raise ValueError('failed panel native correspondence cannot pass')
            if core.sha(root/'native/candidate.FCStd')!=proof['files_sha256']['candidate.FCStd']:
                raise ValueError('panel native CAD bytes differ')
            from hashlib import sha256
            import gzip
            if sha256(gzip.decompress((root/'model.step.gz').read_bytes())).hexdigest()!=proof['files_sha256']['candidate.step']:
                raise ValueError('panel native STEP bytes differ')
            from . import bim
            with design_studies.exchange_files(root/'bim') as paths:
                information=bim.verify(candidate,paths['assembly.ifc'],ids_path=paths['requirements.ids'])
                if information['state']!='information-pass' or information!=core.read(root/'bim/ids-report.json'):
                    raise ValueError('panel BIM information differs')
                design_studies.verify_exchange_mesh(candidate,root/'bim',paths=paths)
        if record['engineering_eligible'] is not False or record['complete_installed_assembly_confirmed'] is not False:
            raise ValueError('partial native geometry cannot confirm an installed panel')
    return result
