"""Matched NdFeB/hybrid operating points, derivative diagnostics and finite check.

The transverse model supplies Fz, Fy and Mx only. Pitch/yaw, end losses, useful
closed-loop control, repeated duty and complete installed mass remain unknown.
"""
from copy import deepcopy
from hashlib import sha256
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from engineering.design_search.storage import atomic_immutable
from engineering.halbach_scaling import candidates as old, finite
from engineering.passive_suspension import fields
from engineering.vehicle_optimisation import magnets
from engineering.magnetic_confirmation import analysis

ROOT=Path(__file__).resolve().parents[2]
SCHEMA='osr-suspension-operating-closure/1'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           installed_mass_complete=False,force_map_generated=False,hover_executed=False,
           stable_hover_established=False)
GAP=.035338
MASS_PUBLICATION='docs/design-engine/halbach-scaling/comparison.json'
SETTINGS=dict(mesh_size_m=.006,outer_margin_m=.25,max_nodes=120000,
    steel_model='nonlinear_repo_proxy',check_convergence=False,nonlinear_max_iterations=100,
    nonlinear_relaxation=.35,nonlinear_tolerance=2e-4,max_solves=1)
FINITE_SETTINGS=dict(margin_m=.15,near_mesh_size_m=.036,gap_mesh_size_m=.012)
GETDP_DOC='https://www.getdp.info/doc/texinfo/getdp.html#Resolution-operations'


def encoded(v):return old.encoded(v)
def identity(v):return old.identity(v)
def write(p,v):return atomic_immutable(Path(p),encoded(v))
def read(p):return json.loads(Path(p).read_bytes())
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()


def sources(root):
    value=old.source_snapshot(root)
    value.update(finite.source_snapshot(root))
    value[MASS_PUBLICATION]=digest(Path(root)/MASS_PUBLICATION)
    for path in sorted(Path(__file__).parent.rglob('*.py')):
        if path.is_symlink():raise ValueError('ordinary implementation sources required')
        value[path.relative_to(ROOT).as_posix()]=digest(path)
    return dict(sorted(value.items()))


def mass_context(root):
    value=read(Path(root)/MASS_PUBLICATION)
    chosen=next(r for r in value['selection']['selected'] if r['purpose']=='controlled')
    row=next(r for r in value['comparisons'] if r['comparison_id']==chosen['comparison_id'])
    return dict(parent_study_id=value['study_id'],body_candidate_id=chosen['body_candidate_id'],
        parent_composition_id=row['composition_id'],magnet_component_id=chosen['magnet_component_id'],
        parent_comparison_aw3_kg_per_car=row['comparison_aw3_kg_per_car'],
        source_publication=MASS_PUBLICATION,source_sha256=digest(Path(root)/MASS_PUBLICATION),
        installed_mass_complete=False)


def candidates(root=ROOT):
    values=old.candidates(root)
    twelve=next(v for v in values if v['recipe_id']=='HS-V012-W40-H8-P1-Y00-D')
    six=next(v for v in values if v['physical_id']==old.PARENT_ID)
    hybrid=deepcopy(twelve);ferrite=magnets.material_sources()['TDK-FB9B-recoil-proxy']
    nd=hybrid['materials'][hybrid['grade_id']]
    chosen=[]
    # Keep NdFeB in the four predominantly vertical cells; replace the four
    # predominantly transverse cells with actual ferrite of identical stock.
    for r in hybrid['regions']:
        if r['material']!=hybrid['grade_id']:continue
        if abs(r['Br_y_T'])>abs(r['Br_z_T']):
            chosen.append(r['id']);scale=ferrite['br_20c_t']/nd['br_20c_t']
            r['material']=ferrite['id'];r['Br_y_T']*=scale;r['Br_z_T']*=scale
    for p in hybrid['stock_parts']:
        if p['id'].split('/block-')[0] in chosen:
            p['material']=ferrite['id'];magnets._recompute_part(p,ferrite['density_kg_m3'])
            p['Br_y_T']*=ferrite['br_20c_t']/nd['br_20c_t'];p['Br_z_T']*=ferrite['br_20c_t']/nd['br_20c_t']
    hybrid['materials'][ferrite['id']]=ferrite
    hybrid['parameters']=dict(hybrid['parameters'],hybrid_ferrite_region_ids=chosen)
    active={hybrid['grade_id'],ferrite['id']};train=[p for p in hybrid['stock_parts'] if p['group']=='train']
    hybrid['stock'].update(train_known_mass_kg_per_module=math.fsum(p['mass_kg'] for p in train),
        train_known_mass_kg_per_car=24*math.fsum(p['mass_kg'] for p in train),
        magnet_volume_m3_per_module=math.fsum(p['volume_m3'] for p in train if p['material'] in active),
        magnet_mass_kg_per_module=math.fsum(p['mass_kg'] for p in train if p['material'] in active))
    hybrid['free_air_seed_80C_T']=None
    hybrid['seed_scope']='No one-grade free-air seed is transferred to mixed material stock'
    hybrid['physical_id']=identity(magnets.physical_definition(hybrid))
    hybrid['candidate_id']=hybrid['physical_id'];hybrid['recipe_id']='SC-12L-H8-N35UH-FB9B-mixed'
    hybrid.pop('bundle_sha256');hybrid['bundle_sha256']=identity(hybrid)
    answer=[];context=mass_context(root)
    if context['magnet_component_id']!=twelve['physical_id']:raise ValueError('published mass parent differs from exact12L component')
    for name,v in [('12L-differential-N35UH',twelve),('6L-retained-N35UH',six),('12L-mixed-N35UH-FB9B',hybrid)]:
        train=[p for p in v['stock_parts'] if p['group']=='train'];material_stock={}
        for p in train:
            a=material_stock.setdefault(p['material'],dict(volume_m3=0.,mass_kg=0.))
            a['volume_m3']+=p['volume_m3'];a['mass_kg']+=p['mass_kg']
        item=dict(schema=SCHEMA+'/candidate',name=name,component_id=v['physical_id'],value=v,
            known_stock_kg_per_module=math.fsum(p['mass_kg'] for p in train),stock_by_material=material_stock,
            mass_comparison_context=deepcopy(context),
            comparison_aw3_kg_per_car=context['parent_comparison_aw3_kg_per_car']+24*(
                math.fsum(p['mass_kg'] for p in train)-twelve['stock']['train_known_mass_kg_per_module']),
            parent_component_id=twelve['physical_id'] if v is hybrid else None,
            installed_mass_kg_per_module=None,cost_per_module=None,price_and_origin_evidence=None,**FLAGS)
        item['definition_id']=identity(item);answer.append(item)
    return answer


def validate_candidate(item,root):
    if item not in candidates(root):raise ValueError('candidate stock/material/identity differs')
    return item


def geometry(item):
    v=item['value'];mats=deepcopy(v['materials'])
    for key,mat in mats.items():
        if mat.get('chemistry') in ('sintered-NdFeB','hard-ferrite'):
            mat.update(kind='ferrite',relative_permeability=mat['recoil_relative_permeability'])
    # The old solver's aggregate demagnetisation check uses this one alias.
    # It is NOT used for hybrid admission; per-region checks below use the
    # actual material of each region, never the weakest/strongest global grade.
    mats['ferrite']=deepcopy(mats[v['grade_id']])
    return dict(length_x_m=v['length_x_m'],reference_gap_m=v['reference_gap_m'],
        origin_yz_m=deepcopy(v['origin_yz_m']),regions=deepcopy(v['regions']),circuits=deepcopy(v['circuits']),
        materials=mats,recoil_adapter=dict(computational_kind='per-region-linear-recoil-PM',
            actual_stock_materials_remain_named=True,aggregate_single_grade_check_not_used=True))


def scenario(item,*,temperature_C=80.,gap_m=GAP,lateral_m=0.,mode='common',current_A=0.):
    numbers=(temperature_C,gap_m,lateral_m,current_A)
    if any(type(v) not in (float,int) or not math.isfinite(v) for v in numbers):raise ValueError('finite operating state required')
    if not 20<=temperature_C<=80 or not .008<=gap_m<=.060 or abs(lateral_m)>.004 or abs(current_A)>15:
        raise ValueError('outside bounded operating state')
    circuits=item['value']['circuits']
    if mode not in ('common','opposed') or mode=='opposed' and len(circuits)!=2:raise ValueError('undeclared circuit connection')
    currents={c['id']:float(current_A)*(1 if mode=='common' or j==0 else -1) for j,c in enumerate(circuits)}
    return dict(gap_m=float(gap_m),lateral_m=float(lateral_m),roll_rad=0.,temperature_C=float(temperature_C),
                currents_A=currents,current_A=float(current_A),connection_mode=mode)


def comparisons(item,raw,state):
    value=item['value'];by_mat=value['materials'];rows=[]
    for region in value['regions']:
        mat=by_mat[region['material']]
        if mat.get('chemistry') not in ('sintered-NdFeB','hard-ferrite'):continue
        h=raw['region_diagnostics'][region['id']]['H_parallel_min_A_per_m']
        t=state['temperature_C'];limit=(mat['hcj_20c_a_m']-mat.get('hcj_tolerance_a_m',0.))*mat['demag_hcj_fraction_limit']*(1+mat['hcj_temperature_coefficient_per_k']*(t-20))
        rows.append(dict(region_id=region['id'],material_id=region['material'],H_parallel_min_A_per_m=h,
            demag_proxy_limit_A_per_m=limit,demag_proxy_margin_A_per_m=h+limit,
            temperature_domain_pass=mat['minimum_temperature_c']<=t<=mat['maximum_temperature_c'],demag_proxy_pass=h+limit>=0))
    contour=raw['diagnostics']['contour_forces'];circuits=value['circuits'];alpha=fields.material_reference()['copper']['resistance_temperature_coefficient_per_k']
    electrical=[]
    for c in circuits:
        current=state['currents_A'][c['id']];r=c['resistance_20c_ohm']*(1+alpha*(state['temperature_C']-20))
        electrical.append(dict(circuit_id=c['id'],current_A=current,J_A_per_mm2=abs(current)/c['conductor_area_m2']/1e6,
            R_ohm=r,DC_RI_V=current*r,DC_copper_loss_W=current*current*r))
    numerical=raw['numerical_status']=='converged'
    fill=max(c['turns']*c['conductor_area_m2']/(c['window_pack_width_m']*c['window_height_m']) for c in circuits)
    return dict(numerical_status=raw['numerical_status'],contour_Fz_N=[r['F_z_N'] for r in contour],
        contour_Fy_N=[r['F_y_N'] for r in contour],contour_Mx_Nm=[r['M_x_Nm'] for r in contour],
        conservative_Fz_N=None if not numerical else min(r['F_z_N'] for r in contour),
        unsupported_components=dict(Fx_N=None,My_Nm=None,Mz_Nm=None),per_region_demag=rows,
        per_region_material_screen_pass=all(r['temperature_domain_pass'] and r['demag_proxy_pass'] for r in rows),
        legacy_aggregate_material_screen_used=False,steel_B_peak_T=raw['steel_B_peak_T'],
        winding_fill=fill,
        necessary_point_screen_pass=numerical and all(r['temperature_domain_pass'] and r['demag_proxy_pass'] for r in rows)
            and raw['steel_B_peak_T']<=2.2 and fill<=.55 and all(r['J_A_per_mm2']<=3.75+1e-12 for r in electrical),
        electrical=electrical,DC_copper_loss_W_per_module=math.fsum(r['DC_copper_loss_W'] for r in electrical),
        net_series_resistance_ohm=math.fsum(r['R_ohm'] for r in electrical),
        dynamic_RMS_loss_W=None,thermal_equilibrium_C=None,continuous_cooling_capacity_W=None,
        control_qualified=False,mesh_domain_derivatives_qualified=False,**FLAGS)


def evaluate(item,state,root):
    validate_candidate(item,root);expected=scenario(item,temperature_C=state['temperature_C'],gap_m=state['gap_m'],
        lateral_m=state['lateral_m'],mode=state['connection_mode'],current_A=state['current_A'])
    if expected!=state:raise ValueError('state connection/units differs')
    before=sources(root);geo=geometry(item)
    request=dict(candidate_id=item['component_id'],definition_id=item['definition_id'],geometry_id=fields._digest(geo),
        state=state,settings=SETTINGS,source_sha256=before)
    raw=fields.solve(geo,**{k:state[k] for k in ('gap_m','lateral_m','roll_rad','temperature_C','currents_A')},settings=SETTINGS)
    if sources(root)!=before:raise ValueError('implementation changed during solve')
    return dict(schema=SCHEMA+'/point',evaluation_id=identity(request),request=request,raw_result=raw,
                comparison=comparisons(item,raw,state),**FLAGS)


def point_contract(point,item,state,root):
    geo=geometry(item);request=dict(candidate_id=item['component_id'],definition_id=item['definition_id'],
        geometry_id=fields._digest(geo),state=state,settings=SETTINGS,source_sha256=sources(root))
    raw=point['raw_result'];copy=deepcopy(raw);rid=copy.pop('result_id')
    if (point.get('schema')!=SCHEMA+'/point' or raw.get('schema')!=fields.SCHEMA
        or raw.get('physical_accepted') is not False or raw.get('material_correlated') is not False
        or point['evaluation_id']!=identity(request) or point['request']!=request or rid!=fields._digest(copy)
        or raw['source_sha256']!=fields.sources() or raw['geometry_id']!=request['geometry_id']
        or raw['declared_material_definitions']!=geo['materials']
        or raw['operating_point']!={k:state[k] for k in ('gap_m','lateral_m','roll_rad','temperature_C','currents_A')}
        or raw['settings']!=fields._settings(SETTINGS) or raw['interpolation_usable'] is not False
        or raw['diagnostics']['validation_solves']!=1
        or point['comparison']!=comparisons(item,raw,state)):
        raise ValueError('point field/material/state/derived result differs')
    for k in FLAGS:
        if point.get(k) is not False:raise ValueError('research acceptance differs')
    return point


def plan(items):
    rows=[]
    def add(item,tag,**kw):rows.append(dict(candidate_id=item['component_id'],tag=tag,state=scenario(item,**kw)))
    a,b,h=items
    for t in (20.,80.):
        for tag,kw in [('nominal',{}),('gap-minus',{'gap_m':GAP-.001}),('gap-plus',{'gap_m':GAP+.001}),
                       ('lateral-minus',{'lateral_m':-.002}),('lateral-plus',{'lateral_m':.002}),
                       ('current-minus',{'current_A':-15.}),('current-plus',{'current_A':15.}),
                       ('incremental-minus',{'current_A':-1.}),('incremental-plus',{'current_A':1.})]:
            add(a,f'{t:g}C/'+tag,temperature_C=t,**kw)
    for tag,kw in [('half-gap-minus',{'gap_m':GAP-.0005}),('half-gap-plus',{'gap_m':GAP+.0005}),
                   ('half-lateral-minus',{'lateral_m':-.001}),('half-lateral-plus',{'lateral_m':.001}),
                   ('opposed-minus',{'mode':'opposed','current_A':-15.}),('opposed-plus',{'mode':'opposed','current_A':15.})]:
        add(a,'80C/'+tag,**kw)
    for item in (b,h):
        add(item,'20C/nominal',temperature_C=20.)
        for tag,i in [('nominal',0.),('current-minus',-15.),('current-plus',15.)]:add(item,'80C/'+tag,current_A=i)
    assert len(rows)==32
    return rows


def _usable(row):
    if row.get('execution_status')!='completed':return False
    execution=row.get('execution')
    if not isinstance(execution,dict) or execution.get('returncode')!=0 or execution.get('timed_out') is not False:
        raise ValueError('completed point requires successful worker')
    return row['point']['raw_result']['numerical_status']=='converged'


def central_difference(positive,negative,width):
    if not width>0 or not math.isfinite(width):raise ValueError('positive finite difference width required')
    return [(float(a)-float(b))/width for a,b in zip(positive,negative)]


def summarize(items,rows):
    result=[]
    for item in items:
        by_tag={r['request']['tag']:r for r in rows if r['request']['candidate_id']==item['component_id']}
        temps=[]
        for t in (20.,80.):
            prefix=f'{t:g}C/'
            def got(tag):
                row=by_tag.get(prefix+tag)
                return row['point'] if row and _usable(row) else None
            nominal=got('nominal');minus=got('current-minus');plus=got('current-plus')
            aw3=item['comparison_aw3_kg_per_car']
            data=dict(temperature_C=t,AW3_comparison_kg_per_car=aw3,mean_AW3_N_per_module=aw3*9.80665/24,
                plus_2t_1_3_required_N_per_module=(aw3+2000)*9.80665*1.3/24,
                sampled_common_current_range_A=[-15.,15.],numerical_force_map_qualified=False,**FLAGS)
            if nominal:data['nominal']=nominal['comparison']
            if minus and plus:
                low=min(minus['comparison']['contour_Fz_N']+plus['comparison']['contour_Fz_N'])
                high=max(min(minus['comparison']['contour_Fz_N']),min(plus['comparison']['contour_Fz_N']))
                data.update(sampled_capacity_min_N=low,sampled_maximum_conservative_Fz_N=high,
                    actuator_sample_materials_pass=all(p['comparison']['per_region_material_screen_pass'] for p in (minus,plus)),
                    sampled_fixed_gap_1_3_plus_2t_capacity_pass=(high>=data['plus_2t_1_3_required_N_per_module']
                        if all(p['comparison']['necessary_point_screen_pass'] for p in (minus,plus)) else None),
                    common_30A_secant_dFz_dI_N_per_A=central_difference(plus['comparison']['contour_Fz_N'],minus['comparison']['contour_Fz_N'],30.),
                    sampled_common_DC_loss_W_per_module=max(minus['comparison']['DC_copper_loss_W_per_module'],plus['comparison']['DC_copper_loss_W_per_module']))
            derivatives={}
            for axis,tags,width in [('gap',('gap-plus','gap-minus'),.002),('lateral',('lateral-plus','lateral-minus'),.004),('current',('incremental-plus','incremental-minus'),2.)]:
                p,m=map(got,tags)
                if p and m:
                    derivatives[axis]={quantity:central_difference(p['comparison'][key],m['comparison'][key],width)
                        for quantity,key in [('Fz','contour_Fz_N'),('Fy','contour_Fy_N'),('Mx','contour_Mx_Nm')]}
                    if axis=='current':
                        ids=[c['id'] for c in item['value']['circuits']]
                        flux=lambda q:math.fsum(q['raw_result']['flux_linkage_Wb_turn'][c] for c in ids)
                        L=(flux(p)-flux(m))/2;R=nominal['comparison']['net_series_resistance_ohm'] if nominal else None
                        data['local_series_RL_diagnostic']=dict(L_H=L,R_ohm=R,tau_s=None if R is None or L<=0 else L/R,
                            inductance_positive=L>0,finite_x_end_inductance_included=False,dynamic_voltage_reserve_V=None)
            if t==80.:
                for axis,tags,width in [('gap',('half-gap-plus','half-gap-minus'),.001),('lateral',('half-lateral-plus','half-lateral-minus'),.002)]:
                    p,m=map(got,tags)
                    if p and m and axis in derivatives:
                        half={q:central_difference(p['comparison'][k],m['comparison'][k],width) for q,k in [('Fz','contour_Fz_N'),('Fy','contour_Fy_N'),('Mx','contour_Mx_Nm')]}
                        derivatives[axis]['half_step']=half
                        derivatives[axis]['half_step_absolute_difference']={q:[abs(a-b) for a,b in zip(derivatives[axis][q],half[q])] for q in half}
                p,m=got('opposed-plus'),got('opposed-minus')
                if p and m:data['opposed_30A_secant']={q:central_difference(p['comparison'][k],m['comparison'][k],30.) for q,k in [('Fz_N_per_A','contour_Fz_N'),('Fy_N_per_A','contour_Fy_N'),('Mx_Nm_per_A','contour_Mx_Nm')]}
            data['derivative_diagnostics']=derivatives
            if 'gap' in derivatives and 'current' in derivatives:
                kz=[-v for v in derivatives['gap']['Fz']];ki=derivatives['current']['Fz'];mass=aw3/24
                data['uncoupled_vertical_linearisation_diagnostic']=dict(
                    dFz_dvehicle_height_N_per_m=kz,dFz_dcommon_current_N_per_A=ki,
                    comparison_local_mass_kg=mass,
                    uncontrolled_growth_rate_rad_per_s=[math.sqrt(max(k,0.)/mass) for k in kz],
                    static_stiffness_cancel_current_gain_A_per_m=[None if abs(i)<1e-9 else -k/i for k,i in zip(kz,ki)],
                    scope='Independent rigid local module-mass approximation only; not a coupled closed-loop design or verified control bandwidth',
                    controller_gains_selected=False,multiaxis_stability_established=False)
            data['unavailable']=dict(dMx_droll=None,dMy_dpitch=None,dMz_dyaw=None,
                reason='2D axis-aligned material mesh does not establish rotation, pitch/yaw, finite ends or dynamic damping')
            temps.append(data)
        result.append(dict(candidate_id=item['component_id'],name=item['name'],temperatures=temps,
            known_stock_kg_per_module=item['known_stock_kg_per_module'],installed_mass_kg=None,cost=None,**FLAGS))
    return result


def _kill(p):
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    p.wait(timeout=5)


def _execute(command,directory,seconds):
    env=dict(os.environ,PYTHONPATH=str(ROOT)+os.pathsep+os.environ.get('PYTHONPATH',''),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    start=time.monotonic()
    with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
        p=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=p.wait(timeout=seconds);timed=False
        except subprocess.TimeoutExpired:_kill(p);code=p.returncode;timed=True
    return dict(command=command,elapsed_s=time.monotonic()-start,deadline_s=seconds,returncode=code,timed_out=timed)


def finite_worker(request,directory):
    item=request['candidate'];validate_candidate(item,request['root'])
    if item['name']!='12L-differential-N35UH' or request['gap_m']!=GAP or request['settings']!=FINITE_SETTINGS:raise ValueError('declared finite operating fixture required')
    if digest(request['getdp']['path'])!=request['getdp']['sha256']:raise ValueError('finite solver differs')
    posed=finite.pose(item['value'],GAP);mesh=finite.mesh_case(posed,directory,FINITE_SETTINGS)
    guard=finite.validate_mesh(directory/'coupon.msh',mesh,posed,FINITE_SETTINGS)
    boxes=finite.contours(posed);counts=(128,48,24)
    (directory/'coupon.pro').write_text(finite.formulation(posed,mesh,boxes,counts))
    command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh','-solve','Solve','-pos','Results']
    with (directory/'getdp.stdout.log').open('wb') as out,(directory/'getdp.stderr.log').open('wb') as err:
        code=subprocess.run(command,cwd=directory,stdout=out,stderr=err).returncode
    parsed=analysis.parse_stages((directory/'getdp.stdout.log').read_text())
    row=dict(schema=SCHEMA+'/finite',request_id=identity(request),candidate_id=item['component_id'],
        state_id=posed['evaluation_state_id'],gap_m=GAP,temperature_C=80.,currents_A={},mesh=mesh,
        mesh_verification=guard,contours_m=boxes,face_counts=list(counts),solver_returncode=code,
        continuation=parsed,force_credit=code==0 and parsed['full_source_converged'],**FLAGS)
    if row['force_credit']:row['analysis']=finite.analyze(directory,posed,mesh,boxes,counts)
    write(directory/'point.json',row)


def run(output,root=ROOT,getdp=None,*,seconds_total=720.,seconds_per_trial=300.):
    if not 0<seconds_total<=720 or not 0<seconds_per_trial<=300:raise ValueError('bounded campaign/trial budget required')
    root=Path(root).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();before=sources(root);items=candidates(root);plans=plan(items)
    request=dict(schema=SCHEMA,root=str(root),candidates=items,plan=plans,settings=SETTINGS,source_sha256=before,
        budget=dict(seconds_total=seconds_total,seconds_per_trial=seconds_per_trial,numerical_workers=1),**FLAGS)
    if getdp:
        tool=finite.previous._tool(getdp)
        request['finite_request']=dict(candidate=items[0],root=str(root),gap_m=GAP,settings=FINITE_SETTINGS,
            getdp=tool,source_sha256=before,method_documentation=GETDP_DOC)
    write(output/'request.json',request);rows=[]
    by_id={v['component_id']:v for v in items}
    for index,case in enumerate(plans):
        directory=output/f'point-{index:02d}';directory.mkdir();write(directory/'input.json',dict(candidate=by_id[case['candidate_id']],state=case['state'],root=str(root)))
        remaining=seconds_total-(time.monotonic()-start)
        row=dict(request=case,execution_status='not-run',**FLAGS)
        if remaining>0:
            command=[sys.executable,'-m','engineering.suspension_closure','worker','--input',str(directory/'input.json'),'--output',str(directory/'point.json')]
            ex=_execute(command,directory,min(seconds_per_trial,remaining));row['execution']=ex
            if ex['returncode']==0 and not ex['timed_out'] and (directory/'point.json').is_file():
                row.update(execution_status='completed',point=read(directory/'point.json'));point_contract(row['point'],by_id[case['candidate_id']],case['state'],root)
            else:row['execution_status']='interrupted' if ex['timed_out'] else 'tool-error'
        rows.append(row)
    finite_result=dict(execution_status='not-requested',**FLAGS)
    if getdp:
        directory=output/'finite';directory.mkdir();write(directory/'input.json',request['finite_request'])
        remaining=seconds_total-(time.monotonic()-start)
        finite_result=dict(execution_status='not-run',**FLAGS)
        if remaining>0:
            command=[sys.executable,'-m','engineering.suspension_closure','finite-worker','--input',str(directory/'input.json'),'--output',str(directory)]
            ex=_execute(command,directory,min(seconds_per_trial,remaining));finite_result['execution']=ex
            if ex['returncode']==0 and not ex['timed_out'] and (directory/'point.json').is_file():finite_result.update(execution_status='completed',point=read(directory/'point.json'))
            else:finite_result['execution_status']='interrupted' if ex['timed_out'] else 'tool-error'
    if sources(root)!=before:raise ValueError('campaign sources changed')
    result=dict(schema=SCHEMA,request_id=identity(request),rows=rows,finite=finite_result,
        comparisons=summarize(items,rows),elapsed_s=time.monotonic()-start,source_sha256=before,**FLAGS)
    result['result_id']=identity(result);write(output/'result.json',result)
    manifest=dict(request_id=identity(request),result_id=result['result_id'],source_sha256=before,
        files_sha256=finite.inventory(output,('manifest.json',)),**FLAGS);write(output/'manifest.json',manifest)
    return result


def verify(output,root=ROOT):
    directory=Path(output);request=read(directory/'request.json');result=read(directory/'result.json');manifest=read(directory/'manifest.json')
    if manifest['files_sha256']!=finite.inventory(directory,('manifest.json',)) or request['source_sha256']!=sources(root):raise ValueError('campaign payload/source differs')
    if request['candidates']!=candidates(root) or request['plan']!=plan(request['candidates']) or request['settings']!=SETTINGS:raise ValueError('campaign definition/plan differs')
    if request['budget']['numerical_workers']!=1 or not 0<request['budget']['seconds_total']<=720 or not 0<request['budget']['seconds_per_trial']<=300:raise ValueError('campaign budget differs')
    items={v['component_id']:v for v in request['candidates']}
    if len(result['rows'])!=len(request['plan']):raise ValueError('missing execution records')
    for index,(case,row) in enumerate(zip(request['plan'],result['rows'])):
        d=directory/f'point-{index:02d}'
        if row.get('execution_status') not in ('completed','not-run','interrupted','tool-error'):raise ValueError('unknown execution state')
        if row['execution_status']=='not-run' and 'execution' in row:raise ValueError('unrun point has execution metadata')
        if row['execution_status'] in ('interrupted','tool-error'):
            ex=row.get('execution',{})
            if (not isinstance(ex.get('returncode'),int) or ex.get('timed_out') is not (row['execution_status']=='interrupted')
                or row['execution_status']=='tool-error' and ex['returncode']==0):raise ValueError('unsuccessful execution metadata differs')
        if case!=row['request'] or read(d/'input.json')!=dict(candidate=items[case['candidate_id']],state=case['state'],root=request['root']):raise ValueError('point definition differs')
        if _usable(row) or row.get('execution_status')=='completed':
            if row['point']!=read(d/'point.json'):raise ValueError('point payload differs')
            point_contract(row['point'],items[case['candidate_id']],case['state'],root)
        elif 'point' in row:raise ValueError('incomplete worker cannot supply force')
    f=result['finite']
    fr=request.get('finite_request')
    if fr:
        expected=dict(candidate=request['candidates'][0],root=request['root'],gap_m=GAP,settings=FINITE_SETTINGS,
            getdp=finite.previous._tool(fr['getdp']['path']),source_sha256=sources(root),method_documentation=GETDP_DOC)
        if fr!=expected or read(directory/'finite/input.json')!=fr:raise ValueError('finite request differs')
        if f.get('execution_status') not in ('completed','not-run','interrupted','tool-error'):raise ValueError('unknown finite execution state')
        if f['execution_status'] in ('interrupted','tool-error'):
            ex=f.get('execution',{})
            if not isinstance(ex.get('returncode'),int) or ex.get('timed_out') is not (f['execution_status']=='interrupted'):
                raise ValueError('unsuccessful finite execution metadata differs')
    elif f.get('execution_status')!='not-requested':raise ValueError('unrequested finite worker has execution')
    if f['execution_status']=='completed':
        ex=f['execution']
        if ex['returncode']!=0 or ex['timed_out']:raise ValueError('completed finite worker execution differs')
        fr=request['finite_request'];d=directory/'finite';p=f['point'];posed=finite.pose(fr['candidate']['value'],GAP)
        if (fr['settings']!=FINITE_SETTINGS or fr['gap_m']!=GAP or fr['source_sha256']!=sources(root)
            or fr['getdp']!=finite.previous._tool(fr['getdp']['path']) or fr!=read(d/'input.json') or p!=read(d/'point.json')
            or p['candidate_id']!=fr['candidate']['component_id'] or p['state_id']!=posed['evaluation_state_id']
            or p['request_id']!=identity(fr) or p['temperature_C']!=80. or p['currents_A']!={}):raise ValueError('finite component/state/source differs')
        mesh=finite.validate_mesh(d/'coupon.msh',p['mesh'],posed,FINITE_SETTINGS);boxes=finite.contours(posed)
        parsed=analysis.parse_stages((d/'getdp.stdout.log').read_text())
        if (p['mesh_verification']!=mesh or p['contours_m']!=boxes or p['face_counts']!=[128,48,24]
            or (d/'coupon.pro').read_text()!=finite.formulation(posed,p['mesh'],boxes,(128,48,24))
            or p['continuation']!=parsed or p['force_credit']!=(p['solver_returncode']==0 and parsed['full_source_converged'])):raise ValueError('finite mesh/formulation/convergence differs')
        if p['force_credit']:
            if p.get('analysis')!=finite.analyze(d,posed,p['mesh'],boxes,(128,48,24)):raise ValueError('finite derived force differs')
        elif 'analysis' in p:raise ValueError('incomplete finite source cannot supply force')
    elif 'point' in f:raise ValueError('incomplete finite worker cannot supply force')
    if result['comparisons']!=summarize(request['candidates'],result['rows']):raise ValueError('derived controls comparison differs')
    rid=identity({k:v for k,v in result.items() if k!='result_id'})
    if result['request_id']!=identity(request) or result['source_sha256']!=sources(root) or result['result_id']!=rid or manifest['result_id']!=rid or manifest['request_id']!=identity(request) or manifest['source_sha256']!=sources(root):raise ValueError('campaign identities differ')
    def reject(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if k in FLAGS and x is not False:raise ValueError('research acceptance differs')
                reject(x)
        elif isinstance(v,list):
            for x in v:reject(x)
    reject(result);reject(request);reject(manifest)
    return dict(current=True,points=len(result['rows']),completed=sum(_usable(r) for r in result['rows']),
        finite_completed=f['execution_status']=='completed' and f.get('point',{}).get('force_credit',False),**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('run','verify','worker','finite-worker'))
    p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);p.add_argument('--input',type=Path);p.add_argument('--getdp',type=Path)
    args=p.parse_args()
    if args.action=='run':result=run(args.output,args.root,args.getdp)
    elif args.action=='verify':result=verify(args.output,args.root)
    else:
        request=read(args.input)
        if args.action=='worker':result=evaluate(request['candidate'],request['state'],request['root']);write(args.output,result)
        else:finite_worker(request,args.output);return
    print(json.dumps(result,sort_keys=True,allow_nan=False))
