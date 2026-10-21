"""Adaptive vehicle/beam/Rust-controller research with exact-revision evidence.

Generate -> analytical/manufacturing screens -> actual Rust/beam cases ->
Pareto-guided variation -> independent scenario confirmation. No claim of global
optimality, actual magnetic performance, qualified fabrication or physical release.
"""
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import random
import tomllib

from . import model,optimisation,coupled,geometry

INPUT=Path(__file__).with_suffix('.toml')
OUTPUT=model.ROOT/'docs/design-engine/ferrite-maglev/iterative'
STATE=model.ROOT/'build/maglev-iteration'
NAMES=('width_m','depth_m','web_m','flange_m','span_m','body_ratio','equipment_ratio','proportional_scale','damping_scale')
FILES={'result.json.gz','recommendation.json','progress.svg','README.md'}


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-adaptive-maglev-search/1':raise ValueError('adaptive schema required')
    for name,low,high in [('population',4,12),('max_generations',2,10),('stagnation_generations',1,10),('confirmation_budget',1,12)]:
        if type(a[name]) is not int or not low<=a[name]<=high:raise ValueError('bounded '+name+' required')
    if a['population']*a['max_generations']>80:raise ValueError('campaign exceeds evaluation budget')
    if type(a['seed']) is not int:raise ValueError('integer seed required')
    if len(a['bounds'])!=len(NAMES) or len(a['quantisation'])!=len(NAMES):raise ValueError('complete candidate axes required')
    for pair,step in zip(a['bounds'],a['quantisation']):
        if len(pair)!=2 or not all(type(v) in (int,float) and math.isfinite(v) for v in pair) or not 0<pair[0]<pair[1]:raise ValueError('finite ordered bounds required')
        model.positive(step,'quantisation')
    if len(a['weights'])!=5 or not math.isclose(sum(a['weights']),1):raise ValueError('five normalised weights required')
    for value in a['weights']:model.positive(value,'weight')
    for name in ('training_duration_s','confirmation_duration_s'):
        if not 1.5<=a[name]<=5:raise ValueError('bounded meaningful duration required')
    for name in ('minimum_gap_m','maximum_gap_m','maximum_final_heave_error_m','maximum_final_angle_rad','maximum_module_force_n'):model.positive(a[name],name)
    if not .003<=a['minimum_gap_m']<.008<a['maximum_gap_m']<=.013:raise ValueError('research gap cannot exceed Rust protection envelope')
    return a


def sources():
    paths={Path(__file__),INPUT,*optimisation.calculation_dependencies(),model.SPEC,
        model.ROOT/'engineering/factory_examples/native.py',model.ROOT/'engineering/factory_examples/models.py'}
    paths.update(model.ROOT/name for name in coupled.sources())
    return {p.relative_to(model.ROOT).as_posix():digest(p) for p in sorted(paths)}


def quantise(vector,a):
    if len(vector)!=len(NAMES):raise ValueError('complete candidate vector required')
    values=[]
    for v,(lo,hi),step in zip(vector,a['bounds'],a['quantisation']):
        if type(v) not in (int,float) or not math.isfinite(v):raise ValueError('finite candidate required')
        values.append(round(min(hi,max(lo,round(v/step)*step)),6))
    return values


def identity(vector):return sha256(encoded(vector)).hexdigest()


def case_pass(r,a):
    required=('minimum_relative_gap_m','maximum_relative_gap_m','final_fitted_relative_heave_error_m','final_roll_rad','final_pitch_rad','peak_station_force_n')
    if any(type(r.get(k)) not in (int,float) or not math.isfinite(r[k]) for k in required):return False
    return (r.get('physical_output_authorised') is False and r.get('structural_acceptance') is False
        and a['minimum_gap_m']<=r['minimum_relative_gap_m']<=r['maximum_relative_gap_m']<=a['maximum_gap_m']
        and abs(r['final_fitted_relative_heave_error_m'])<=a['maximum_final_heave_error_m']
        and max(abs(r['final_roll_rad']),abs(r['final_pitch_rad']))<=a['maximum_final_angle_rad']
        and 0<r['peak_station_force_n']<=a['maximum_module_force_n'])


def protection(executable,mass,p,d):
    import numpy as np
    def rejects(action):
        try:action()
        except RuntimeError as exc:
            if 'rejected frame' in str(exc):return True
            raise
        return False
    with coupled.RustController(executable,mass,proportional_scale=p,damping_scale=d) as controller:
        forces,_,_=controller.tick(1,np.full(24,.008))
        gravity=bool(abs(float(forces.sum())-mass*9.81)<1e-4)
        replay=rejects(lambda:controller.tick(1,np.full(24,.008)))
    with coupled.RustController(executable,mass,proportional_scale=p,damping_scale=d) as controller:
        excessive=rejects(lambda:controller.tick(1,np.full(24,.03)))
    return dict(gravity_equilibrium=gravity,replayed_frame_rejected=replay,excess_gap_rejected=excessive,
        passed=gravity and replay and excessive,physical_output_authorised=False)


def assess(vector,executable,c,costs,a,*,confirmation=False):
    values=dict(zip(NAMES,vector));profile=dict(id='adaptive-'+identity(vector)[:12],
        structure_ratio=values['body_ratio'],magnetic_equipment_ratio=values['equipment_ratio'],hvac_ratio=1.,auxiliary_ratio=1.,
        hardware_target='retain-process-rates',unqualified_change_count=sum(v<1 for v in vector[5:7]))
    target,vehicle=optimisation.vehicle(c,costs,profile)
    civil=optimisation.civil(target,costs,vehicle,*vector[:5],optimisation.load())
    base=dict(candidate_id=identity(vector),vector=vector,parameters=values,
        phase='confirmation' if confirmation else 'training',vehicle=vehicle,civil=civil,
        manufacturing_screen=dict(minimum_web_m=.12,minimum_flange_m=.15,
            basis='project search bounds only; cover, prestress, connections and strength remain unqualified'),
        protection=None,cases=[],screen_pass=False,**model.FLAGS)
    if not civil['numerical_screen_pass']:
        base['reason']='gross stiffness or bare lift screen rejected';return base
    section=civil['section'];line=geometry.guideway_quantities(*vector[4:5],width=vector[0],depth=vector[1],web=vector[2],flange=vector[3])['total_line_mass_kg_m']
    line+=optimisation.load()['civil']['reference_walkway_concrete_area_m2_per_direction']*geometry.MATERIALS['concrete']
    guard=protection(executable,vehicle['mass']['aw2_kg'],vector[7],vector[8]);base['protection']=guard
    if not guard['passed']:base['reason']='mandatory actual Rust protection check rejected';return base
    # Scenario coefficients are explicit research assumptions, not climatic or
    # device acceptance envelopes. Additional mass is never a verified chute mass.
    scenarios=[('aw2-normal','aw2_kg',1.,1.,.02,5000.,0.,.0005),
               ('aw3-load','aw3_kg',1.,1.,.02,8000.,0.,.0005),
               ('aw3-compliant','aw3_kg',.85,1.15,.01,10000.,250.,.0005)]
    if confirmation:scenarios=[('aw2-reverse-holdout','aw2_kg',.9,1.1,.015,-7500.,100.,-.0005),
        ('aw3-adverse-holdout','aw3_kg',.8,1.2,.01,12000.,500.,.0005)]
    for name,load,e_ratio,line_ratio,damping,pulse,added,error in scenarios:
        mass=vehicle['mass'][load]+added
        beam=coupled.BeamAssumptions(span_m=vector[4],second_moment_m4=section['vertical_i_m4'],
            young_pa=c['civil']['narrow_box_screen']['gross_uncracked_concrete_e_pa']*e_ratio,
            line_mass_kg_m=line*line_ratio,damping_ratio=damping)
        try:
            result=coupled.cosimulate(executable,duration_s=a['confirmation_duration_s' if confirmation else 'training_duration_s'],
                car_mass_kg=mass,assumptions=beam,initial_down_error_m=error,disturbance_n=pulse,
                proportional_scale=vector[7],damping_scale=vector[8],
                inertia_roll_kg_m2=20000*mass/27750,inertia_pitch_kg_m2=600000*mass/27750,record_trace=True)
            case=dict(name=name,added_unqualified_equipment_mass_kg=added,result=result,passed=case_pass(result,a))
        except RuntimeError as exc:
            if 'rejected frame' not in str(exc):raise
            case=dict(name=name,result=None,passed=False,reason=str(exc))
        base['cases'].append(case)
        if not case['passed']:base['reason']='candidate failed coupled case '+name;return base
    base['screen_pass']=True
    gaps=[min(case['result']['minimum_relative_gap_m']-a['minimum_gap_m'],a['maximum_gap_m']-case['result']['maximum_relative_gap_m']) for case in base['cases']]
    heave=max(abs(case['result']['final_fitted_relative_heave_error_m']) for case in base['cases'])
    terms=[civil['indexed_allowance_usd_dual_km']/5e6,vehicle['mass']['tare_kg']/18750,
        vehicle['matched_duty']['hot_aw3_no_regen_cycle_kwh_per_car']/20,heave/a['maximum_final_heave_error_m'],
        sum(1-v for v in vector[5:7])*10]
    base['metrics']=dict(score=sum(w*v for w,v in zip(a['weights'],terms)),objective_terms=terms,
        minimum_gap_margin_m=min(gaps),maximum_final_heave_error_m=heave,
        tare_kg=vehicle['mass']['tare_kg'],ordinary_civil_allowance_usd_dual_km=civil['indexed_allowance_usd_dual_km'],
        hot_cycle_kwh_per_car=vehicle['matched_duty']['hot_aw3_no_regen_cycle_kwh_per_car'])
    return base


def frontier(rows):
    passing=[r for r in rows if r['screen_pass']]
    def vector(r):
        m=r['metrics'];return [m['ordinary_civil_allowance_usd_dual_km'],m['tare_kg'],m['hot_cycle_kwh_per_car'],
            m['maximum_final_heave_error_m'],-m['minimum_gap_margin_m']]
    return [r for r in passing if not any(all(x<=y for x,y in zip(vector(o),vector(r))) and any(x<y for x,y in zip(vector(o),vector(r))) for o in passing)]


def search(a,evaluate,confirm,*,checkpoint=None):
    """Deterministic adaptive search; evaluators are injected only for unit tests."""
    rng=random.Random(a['seed']);seen={};history=[];best=None;stagnation=0
    seeds=[[.8,1.6,.15,.18,25,1,1,1,1],[.8,1.9,.15,.18,25,1,1,1,1],
        [.9,2.,.15,.18,25,.95,1,.9,1.1],[.8,1.9,.14,.17,22.5,1,.98,1.1,1.2]]
    population=[quantise(v,a) for v in seeds[:a['population']]]
    ancestry={identity(v):dict(method='declared-seed',parents=[]) for v in population}
    while len(population)<a['population']:
        v=quantise([rng.uniform(*p) for p in a['bounds']],a);population.append(v)
        ancestry[identity(v)]=dict(method='seeded-exploration',parents=[])
    reason='generation-budget'
    for generation in range(a['max_generations']):
        ids=[]
        for vector in population:
            key=identity(vector);ids.append(key)
            if key not in seen:
                row=evaluate(vector)
                if row['candidate_id']!=key or row['vector']!=vector:raise ValueError('candidate evaluator identity differs')
                seen[key]=dict(row,generation=generation,proposal=ancestry[key])
                if checkpoint:checkpoint(generation,list(seen.values()))
        passing=sorted((r for r in seen.values() if r['screen_pass']),key=lambda r:(r['metrics']['score'],r['candidate_id']))
        score=passing[0]['metrics']['score'] if passing else None
        improved=score is not None and (best is None or score<best-1e-6)
        stagnation=0 if improved else stagnation+1
        if improved:best=score
        history.append(dict(generation=generation,candidate_ids=ids,total_evaluated=len(seen),
            passing=len(passing),best_score=score,improved=improved,pareto_ids=[r['candidate_id'] for r in frontier(list(seen.values()))]))
        if stagnation>=a['stagnation_generations']:reason='bounded-stagnation';break
        if generation==a['max_generations']-1:break
        # Elites, Pareto diversity, differential mutation and shrinking local
        # variation. New proposals depend on measured previous-generation results.
        parents=[r['vector'] for r in passing[:3]]+[r['vector'] for r in frontier(list(seen.values()))[:3]]
        if not parents:parents=[r['vector'] for r in list(seen.values())[:3]]
        population=[];attempts=0
        while len(population)<a['population'] and attempts<1000:
            attempts+=1;p=parents[attempts%len(parents)];left=rng.choice(parents);right=rng.choice(parents)
            radius=.16/(generation+1)
            v=[x+.5*(l-r)+rng.gauss(0,radius*(hi-lo)) for x,l,r,(lo,hi) in zip(p,left,right,a['bounds'])]
            method='differential-and-local-mutation';parent_ids=list(dict.fromkeys(identity(x) for x in (p,left,right)))
            if attempts%5==0:
                v=[rng.uniform(*b) for b in a['bounds']];method='seeded-exploration';parent_ids=[]
            v=quantise(v,a)
            if identity(v) not in seen and v not in population:
                population.append(v);ancestry[identity(v)]=dict(method=method,parents=parent_ids)
        if not population:reason='quantised-space-exhausted';break
    contenders=sorted((r for r in seen.values() if r['screen_pass']),key=lambda r:(r['metrics']['score'],r['candidate_id']))
    confirmations=[];selected=None
    for row in contenders[:a['confirmation_budget']]:
        confirmation=confirm(row['vector'])
        if confirmation['candidate_id']!=row['candidate_id'] or confirmation['vector']!=row['vector']:raise ValueError('confirmation revision differs')
        confirmations.append(confirmation)
        if confirmation['screen_pass']:selected=row['candidate_id'];break
    failures={r['candidate_id'] for r in confirmations if not r['screen_pass']}
    confirmed={r['candidate_id'] for r in confirmations if r['screen_pass']}
    for row in seen.values():
        row['confirmation_state']='failed' if row['candidate_id'] in failures else 'passed' if row['candidate_id'] in confirmed else 'not-executed'
        row['eligible_for_research_recommendation']=row['screen_pass'] and row['candidate_id'] in confirmed
    return dict(schema='osr-adaptive-design-campaign/1',history=history,candidates=list(seen.values()),confirmations=confirmations,
        selected_candidate_id=selected,pareto_candidate_ids=[r['candidate_id'] for r in frontier(list(seen.values())) if r['candidate_id'] not in failures],
        termination_reason=reason,global_optimum_proven=False,accepted_engineering_items=0,**model.FLAGS)


def read_cache(path,vector,epoch):
    if not path.is_file():return None
    try:
        envelope=json.loads(path.read_text());result=envelope['result']
        if (envelope['epoch']==epoch and envelope['sha256']==sha256(encoded(result)).hexdigest()
                and result['candidate_id']==identity(vector) and result['vector']==vector
                and all(result.get(k) is False for k in model.FLAGS)):return result
    except (ValueError,KeyError,TypeError):pass
    return None


def chart(result):
    points=[(g['generation'],g['best_score']) for g in result['history'] if g['best_score'] is not None]
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420">',
        '<rect width="1000" height="420" fill="#f3f7fa"/><g font-family="sans-serif" fill="#173249">',
        '<text x="40" y="40" font-size="24">Adaptive mechanical, civil and Rust-control study</text>',
        '<text x="40" y="70">Best training score per generation (lower is preferred under declared weights)</text>']
    if points:
        lo=min(y for _,y in points);hi=max(y for _,y in points);span=max(hi-lo,.02)
        projected=[(70+x*850/max(1,len(result['history'])-1),300-(y-lo)*180/span) for x,y in points]
        coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in projected)
        rows.append(f'<polyline points="{coords}" fill="none" stroke="#087f8c" stroke-width="4"/>')
        for (generation,score),(x,y) in zip(points,projected):rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#087f8c"/><text x="{x-20:.2f}" y="{y-18:.2f}">{score:.5f}</text><text x="{x-10:.2f}" y="335">{generation}</text>')
    rows+=['<text x="40" y="375">Research screens only. Confirmation is required; no global optimum or physical acceptance established.</text></g></svg>']
    return ('\n'.join(rows)+'\n').encode()


def publish(output=OUTPUT):
    a=load();_,c,costs=model.load();before=sources();executable,execution=coupled._build_bridge()
    epoch=sha256(encoded([before,execution])).hexdigest();cache=STATE/epoch;cache.mkdir(parents=True,exist_ok=True)
    def evaluate(vector,confirmation=False):
        if sources()!=before:raise ValueError('iteration sources changed during execution')
        path=cache/(identity(vector)+('-confirmation' if confirmation else '')+'.json')
        result=read_cache(path,vector,epoch)
        phase='confirmation' if confirmation else 'training'
        if result is not None and result.get('phase')!=phase:result=None
        if result is None:
            result=assess(vector,executable,c,costs,a,confirmation=confirmation)
            envelope=dict(epoch=epoch,result=result,sha256=sha256(encoded(result)).hexdigest())
            temporary=path.with_suffix('.pending');temporary.write_bytes(encoded(envelope));temporary.replace(path)
        return result
    def progress(generation,rows):
        state=dict(epoch=epoch,generation=generation,evaluated=len(rows),passing=sum(r['screen_pass'] for r in rows),**model.FLAGS)
        path=STATE/'progress.json';temporary=path.with_suffix('.pending');temporary.write_bytes(encoded(state));temporary.replace(path)
    result=search(a,evaluate,lambda v:evaluate(v,True),checkpoint=progress)
    result.update(source_sha256=before,execution=execution,assumptions=a,source_epoch=epoch,
        runtime=coupled.platform.python_version(),evaluator='actual Rust coupled_bridge and Python modal beam',
        model_scope='Stationary single rigid car, vertical beam and three controlled body modes; mass/inertia allocations and ideal instantaneous magnetic forces. Full train, qualified field/loss maps, physical deadlines, soil/joints, strength/fatigue and production qualification remain open.')
    selected=next((r for r in result['candidates'] if r['candidate_id']==result['selected_candidate_id']),None)
    recommendation=dict(schema='osr-research-recommendation/1',source_epoch=epoch,
        candidate_id=result['selected_candidate_id'],selection_scope='Preferred among evaluated candidates under declared research bounds, weights and scenarios; not an accepted complete design',
        parameters=selected['parameters'] if selected else None,metrics=selected.get('metrics') if selected else None,
        automatic_reference_configuration_promotion=False,production_design_suitable=None,
        beam_only_option='held: full onboard evacuation mass, lifetime cost and route acceptance remain unknown',**model.FLAGS)
    rows=['# Adaptive mechanical, civil and software design study','','![Observed generation progress](progress.svg)','',
        f"{len(result['candidates'])} exact candidates evaluated over {len(result['history'])} generations; {sum(r['screen_pass'] for r in result['candidates'])} passed training screens. Termination: {result['termination_reason']}.",'',
        'The generator uses the preceding results to create differential and local mutations of beam sections/spans, body and equipment mass allocations, and actual Rust controller gains. Each viable proposal runs passenger-load and compliant-guideway scenarios plus replay/invalid-gap protection controls. Shortlisted candidates face separate three-second holdout scenarios; failed confirmation disqualifies that revision.','',
        'The selected study is identified in [recommendation.json](recommendation.json). [Full candidate, ancestry, scenario and confirmation evidence](result.json.gz) is source-bound by [manifest.json](manifest.json). Cache receipts permit exact-source restart; changed sources or binaries create another epoch.','',
        'Manufacturing screens are declared project bounds and bare-lift checks. Body mass reductions are unqualified allocations, with no automatic procurement or local-content credit. Required ferrite, batteries, passenger equipment, capture and reserves remain in the comparison. Inertias are assumed to scale with mass; they are not recovered from a complete body model.','',
        'The comparison retains fallback walkway scope. Removing it remains conditional on qualified onboard evacuation and route acceptance. Candidate beam geometry is not automatically promoted into city defaults.','',
        '**Engineering acceptance remains open.** This study does not prove a global optimum, complete manufacturability, actual magnetic performance, a whole-train dynamic model or hardware timing.','']
    payload={'result.json.gz':gzip.compress(encoded(result),mtime=0),'recommendation.json':encoded(recommendation),'progress.svg':chart(result),'README.md':'\n'.join(rows).encode()}
    if sources()!=before or digest(executable)!=execution['bridge_sha256']:raise ValueError('iteration sources or bridge changed')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if output.is_symlink() or any(p.is_symlink() for p in output.iterdir()):raise ValueError('ordinary owned iteration output required')
    if {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:raise ValueError('unexpected iterative publication file')
    for name,data in payload.items():
        path=output/name;temporary=path.with_suffix(path.suffix+'.pending');temporary.write_bytes(data);temporary.replace(path)
    manifest=dict(schema='osr-adaptive-publication/1',source_sha256=before,source_epoch=epoch,execution=execution,
        files_sha256={name:sha256(data).hexdigest() for name,data in payload.items()},**model.FLAGS)
    path=output/'manifest.json';temporary=path.with_suffix('.pending');temporary.write_bytes(encoded(manifest));temporary.replace(path)
    return verify(output)


def verify(output=OUTPUT):
    output=Path(output)
    if {p.name for p in output.iterdir()}!=FILES|{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):raise ValueError('exact iterative publication inventory required')
    manifest=json.loads((output/'manifest.json').read_text())
    if manifest['schema']!='osr-adaptive-publication/1' or manifest['source_sha256']!=sources():raise ValueError('iterative source identity differs')
    if set(manifest['files_sha256'])!=FILES:raise ValueError('complete iterative receipts required')
    for name,expected in manifest['files_sha256'].items():
        if digest(output/name)!=expected:raise ValueError('iterative payload differs: '+name)
    with gzip.open(output/'result.json.gz','rb') as stream:
        data=stream.read(64*1024*1024+1)
    if len(data)>64*1024*1024:raise ValueError('iteration payload exceeds bound')
    result=json.loads(data);recommendation=json.loads((output/'recommendation.json').read_text())
    if result['source_sha256']!=manifest['source_sha256'] or result['execution']!=manifest['execution']:raise ValueError('iterative result provenance differs')
    if (result['source_epoch']!=manifest['source_epoch'] or recommendation['source_epoch']!=manifest['source_epoch']
            or manifest['source_epoch']!=sha256(encoded([manifest['source_sha256'],manifest['execution']])).hexdigest()
            or result['assumptions']!=load()):raise ValueError('iteration epoch or assumptions differ')
    if any(r.get(k) is not False for r in (manifest,result,recommendation) for k in model.FLAGS):raise ValueError('iteration cannot release hardware')
    key=result['selected_candidate_id'];rows={r['candidate_id']:r for r in result['candidates']}
    if len(rows)!=len(result['candidates']):raise ValueError('duplicate candidate identities')
    if any(identity(r['vector'])!=r['candidate_id'] or quantise(r['vector'],result['assumptions'])!=r['vector'] for r in rows.values()):raise ValueError('candidate identity or bounds differ')
    for row in result['candidates']+result['confirmations']:
        if any(row.get(k) is not False for k in model.FLAGS):raise ValueError('candidate release flag differs')
        if row['parameters']!=dict(zip(NAMES,row['vector'])):raise ValueError('candidate parameters differ')
        if row['screen_pass']:
            expected=['aw2-normal','aw3-load','aw3-compliant'] if row['phase']=='training' else ['aw2-reverse-holdout','aw3-adverse-holdout']
            if (row['phase'] not in {'training','confirmation'} or [c['name'] for c in row['cases']]!=expected
                    or not row['protection'] or any(row['protection'].get(k) is not True for k in ('passed','gravity_equilibrium','replayed_frame_rejected','excess_gap_rejected'))
                    or row['protection'].get('physical_output_authorised') is not False
                    or any(c.get('passed') is not True or not case_pass(c['result'],result['assumptions']) for c in row['cases'])):
                raise ValueError('passing candidate lacks mandatory case/protection evidence')
    for row in rows.values():
        if any(parent not in rows or rows[parent]['generation']>=row['generation'] for parent in row['proposal']['parents']):raise ValueError('invalid candidate ancestry')
        confirmations=[r for r in result['confirmations'] if r['candidate_id']==row['candidate_id']]
        eligible=row['screen_pass'] and bool(confirmations) and all(r['screen_pass'] for r in confirmations)
        if row['eligible_for_research_recommendation']!=eligible:raise ValueError('confirmation failure/hold eligibility differs')
    if key:
        row=rows[key];confirmations=[r for r in result['confirmations'] if r['candidate_id']==key]
        if (not row['screen_pass'] or not row['eligible_for_research_recommendation'] or not confirmations or any(not r['screen_pass'] for r in confirmations)
                or any(not case_pass(case['result'],result['assumptions']) for r in [row,*confirmations] for case in r['cases'])
                or recommendation['candidate_id']!=key or recommendation['parameters']!=row['parameters'] or recommendation['metrics']!=row['metrics']):raise ValueError('research recommendation lacks applicable passing confirmation')
    elif recommendation['candidate_id'] is not None:raise ValueError('unconfirmed recommendation')
    return manifest
