"""Bounded complete-package search for cost, mass and construction time.

Baghdad missing axle records do not prevent geometry and explicitly static
planning sensitivities. They continue to prevent moving-load qualification.
"""
from __future__ import annotations
from copy import deepcopy
import gzip
import math
from pathlib import Path
import time
import tomllib
import subprocess

import numpy as np
from osr_mech.civil.exploration import geometry,foundation_geometry
from .contracts import ROOT,HERE,encoded,identity,load,sha,validate,dependencies
from .workflow import candidate,environment,validate_candidate
from .model import System,takeoff,pier_physics
from . import construction,foundations,system_economics,search,qualification,detailed,validation,bim,storage,space_frame,section_mechanics,nonlinear


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded(value))


def validate_options(config):
    required={'schema','deployment','route_length_m','tracks','pier_height_m','spans_m','materials','material_roles',
              'beams','piers','foundations','soil_scenarios','planning_load','research_constraints','unimplemented_options',
              'search','evidence_policy','connection_schemes','frp_variants'}
    if set(config)!=required or config['schema']!='osr-civil-system-options/1' or config['deployment']!='baghdad' or config['tracks']!=2:
        raise ValueError('system option contract incomplete or unknown fields')
    if type(config['route_length_m']) not in (int,float) or not 100<=config['route_length_m']<=2100:
        raise ValueError('system comparison length outside registered budget')
    if config['spans_m']!=sorted(set(config['spans_m'])) or any(type(s) not in (int,float) or not 15<=s<=35 or not math.isclose(config['route_length_m']/s,round(config['route_length_m']/s)) for s in config['spans_m']):
        raise ValueError('comparison scope must contain whole registered spans')
    if type(config['pier_height_m']) not in (int,float) or not 5<=config['pier_height_m']<=12:
        raise ValueError('pier height outside research domain')
    if set(config['materials'])!={'normal','high-performance','lightweight'} or set(config['material_roles'])!={'frp','uhpc','steel'}:
        raise ValueError('material matrix scope incomplete')
    schema=load(HERE/'schemas/candidate.json')
    for m in config['materials'].values():
        validate(m,schema['properties']['material'])
        if m['measured']:raise ValueError('research library cannot self-declare measured mixes')
    for m in config['material_roles'].values():
        validate(m,schema['properties']['material_records']['additionalProperties'])
        if m['measured']:raise ValueError('research library cannot self-declare measured composite/material properties')
    if set(config['frp_variants'])!={'gfrp','cfrp'}:raise ValueError('FRP property matrix coverage incomplete')
    for m in config['frp_variants'].values():
        validate(m,schema['properties']['material_records']['additionalProperties'])
        if m['measured']:raise ValueError('FRP property matrix cannot self-declare measured laminates')
    from .orthotropic import validate as validate_orthotropic
    for m in [*config['material_roles'].values(),*config['frp_variants'].values()]:
        if m.get('orthotropic'):
            validate_orthotropic(m['orthotropic'])
            if not math.isclose(m['youngs_modulus_pa'],m['orthotropic']['ex_pa']):raise ValueError('FRP longitudinal modulus/matrix mismatch')
    for name,field in (('beams','deck'),('piers','pier')):
        if not config[name] or len({r['id'] for r in config[name]})!=len(config[name]):raise ValueError('family IDs missing/duplicated')
        allowed=schema['properties']['definition']['properties'][field]['properties']['family']['enum']
        for row in config[name]:
            expected={'id','bounds','materials','construction','owner','maturity','uncovered'}
            if set(row)!=expected or row['id'] not in allowed or not row['owner'] or row['maturity']!='research' or not row['uncovered']:
                raise ValueError('option family ownership/domain incomplete')
            if not row['materials'] or set(row['materials'])-config['materials'].keys():raise ValueError('unregistered family material')
            for key,bounds in row['bounds'].items():
                if key not in schema['properties']['definition']['properties'][field]['properties']['parameters']['properties'] or type(bounds) is not list or len(bounds)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in bounds) or bounds[0]>bounds[1]:
                    raise ValueError('family bounds invalid: '+key)
    if len({r['id'] for r in config['foundations']})!=len(config['foundations']):raise ValueError('duplicated foundation IDs')
    for row in config['foundations']:
        if set(row)!={'id','parameters','bounds','owner','maturity','uncovered'} or not row['owner'] or row['maturity']!='research':raise ValueError('foundation option contract incomplete')
        validate(row['parameters'],schema['properties']['foundation']);foundation_geometry(row['parameters'])
        if row['parameters']['site_verified']:raise ValueError('option cannot self-declare a site foundation')
        for key,bounds in row['bounds'].items():
            if key not in {'pile_diameter_m','pile_length_m','cap_depth_m','cap_length_m','cap_width_m'} or type(bounds) is not list or len(bounds)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in bounds) or bounds[0]>bounds[1]:
                raise ValueError('foundation bounds invalid')
    if set(config['connection_schemes'])-{'simple-span','link-slab','continuous'} or not config['connection_schemes']:raise ValueError('unregistered continuity scheme')
    if len({r['id'] for r in config['soil_scenarios']})!=len(config['soil_scenarios']):raise ValueError('duplicate soil scenario')
    for soil in config['soil_scenarios']:foundations.validate_soil(soil)
    limits=config['research_constraints']
    if set(limits)!={'relative_deflection_span_ratio','settlement_m','max_lift_mass_kg','gross_elastic_stress_pa','pier_drift_ratio'} or any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for key,x in limits.items() if not (key=='gross_elastic_stress_pa' and x is None)):raise ValueError('research limit coverage incomplete')
    if set(config['planning_load'])!={'source','train_family','mass_field','basis'} or not config['planning_load']['basis']:raise ValueError('planning-load basis incomplete')
    budget=config['search']
    if set(budget)!={'seeds','evaluations_per_method','population','maximum_evaluations','wall_seconds','shortlist_count'} or any(type(budget[k]) is not int for k in set(budget)-{'seeds'}):raise ValueError('search budget contract invalid')
    if not 12<=budget['evaluations_per_method']<=1000 or not 4<=budget['population']<=64 or not 500<=budget['maximum_evaluations']<=2000 or not 10<=budget['wall_seconds']<=3600 or not 1<=budget['shortlist_count']<=40:raise ValueError('search budget outside bounds')


def planning_load(config):
    relative=config['planning_load']['source'];path=(ROOT/relative).resolve()
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.is_relative_to(ROOT):raise ValueError('planning load source must be controlled')
    record=tomllib.loads(path.read_text())['deployment_trains'][config['planning_load']['train_family']]
    if record['deployment']!='Baghdad' or record['cars']!=6 or record['axles']!=24:raise ValueError('planning load does not identify Baghdad')
    mass=record[config['planning_load']['mass_field']]
    return dict(basis=config['planning_load']['basis'],source=relative,source_sha256=sha(path),
                mass_t=mass,planning_train_length_m=record['length_m'],kn_m_per_track=mass*9.81/record['length_m'],
                actual_axle_positions_m=None,actual_axle_forces_kn=None,dynamic_qualification=False)


def base_study(config):
    study=load(HERE/'config/reference.json')
    del study['train']  # A static planning study must not contain a substituted LM3 train.
    study.update(name='Baghdad-complete-system-static-research',route_length_m=config['route_length_m'],
                 material_records=deepcopy(config['material_roles']),support_material=deepcopy(config['materials']['normal']),
                 foundation_material=deepcopy(config['materials']['normal']))
    study['analysis']['static_positions']=9
    return study


def study_for(choice,config):
    study=base_study(config)
    study['material']=deepcopy(config['materials'][choice['material']])
    study['material_records']['frp']=deepcopy(config['frp_variants'][choice.get('fibre_material','gfrp')])
    study['support_material']=deepcopy(config['materials'][choice['support_material']])
    study['foundation']=deepcopy(next(f['parameters'] for f in config['foundations'] if f['id']==choice['foundation']))
    f=study['foundation'];overrides=choice.get('foundation_parameters',{})
    if 'pile_diameter_m' in overrides and f['pile_diameter_m']:
        ratio=overrides['pile_diameter_m']/f['pile_diameter_m']
        f['cap_length_m']*=ratio;f['cap_width_m']*=ratio;f['pile_inner_diameter_m']=f.get('pile_inner_diameter_m',0.)*ratio
    f.update(overrides)
    study['connection_scheme']=choice['connection_scheme']
    if choice['beam'] in ('steel-composite-I','frp-composite-I'):
        study['mass_allowances']['prestress_kg_m']=0.
        study['mass_allowances']['basis']+=' No tendon mass assigned to the composite I research family; actual connector/tension detailing open.'
    definition=dict(deck=dict(family=choice['beam'],span_m=choice['span_m'],parameters=deepcopy(choice['beam_parameters'])),
                    pier=dict(family=choice['pier'],height_m=config['pier_height_m'],parameters=deepcopy(choice['pier_parameters'])))
    return study,definition


def sample(config,rng,index,parent=None):
    beam=config['beams'][index%len(config['beams'])] if parent is None else next(b for b in config['beams'] if b['id']==parent['choice']['beam'])
    pier=config['piers'][int(rng.integers(len(config['piers'])))]
    choice=dict(beam=beam['id'],pier=pier['id'],span_m=float(rng.choice(config['spans_m'])),
                material=str(rng.choice(beam['materials'])),support_material=str(rng.choice(pier['materials'])),
                foundation=config['foundations'][int(rng.integers(len(config['foundations'])))]['id'],
                beam_method=str(rng.choice(beam['construction'])),pier_method=pier['construction'],
                cap_method=str(rng.choice(['precast','cast-in-place'])),connection_scheme=str(rng.choice(config['connection_schemes'])),
                beam_parameters={},pier_parameters={},foundation_parameters={},fibre_material=str(rng.choice(['gfrp','cfrp'])))
    if parent is not None:
        old=parent['choice'];choice.update({k:deepcopy(old[k]) for k in choice if k not in ('beam_parameters','pier_parameters','foundation_parameters') and rng.random()>.2})
        pier=next(p for p in config['piers'] if p['id']==choice['pier']);choice['pier_method']=pier['construction']
        if choice['beam_method'] not in beam['construction']:choice['beam_method']=beam['construction'][0]
    for part,row in (('beam',beam),('pier',pier)):
        for key,(lo,hi) in row['bounds'].items():
            old=parent['choice'][part+'_parameters'].get(key) if parent is not None and parent['choice'][part]==row['id'] else None
            value=rng.uniform(lo,hi) if old is None else np.clip(old+rng.normal(0.,.12)*(hi-lo),lo,hi)
            choice[part+'_parameters'][key]=int(round(value)) if key=='rib_count' else round(float(value),8)
    foundation=next(f for f in config['foundations'] if f['id']==choice['foundation'])
    for key,(lo,hi) in foundation['bounds'].items():
        old=parent['choice'].get('foundation_parameters',{}).get(key) if parent is not None and parent['choice']['foundation']==foundation['id'] else None
        value=rng.uniform(lo,hi) if old is None else np.clip(old+rng.normal(0.,.12)*(hi-lo),lo,hi)
        choice['foundation_parameters'][key]=round(float(value),8)
    if choice['beam'] not in ('hybrid-shell','frp-composite-I') and choice['pier']!='double-skin-hybrid':choice['fibre_material']='gfrp'
    return choice


def engineering_seeds(config):
    rows=[]
    for i,beam in enumerate(config['beams']):
        params={k:(int(round((a+b)/2)) if k=='rib_count' else (a+b)/2) for k,(a,b) in beam['bounds'].items()}
        rows.append(dict(beam=beam['id'],pier='solid',span_m=20.,material='normal',support_material='normal',foundation='reference-four',
                         beam_method=beam['construction'][0],pier_method='cast-in-place',cap_method='precast',connection_scheme='simple-span',
                         beam_parameters=params,pier_parameters={},foundation_parameters={},fibre_material='gfrp'))
    rows.append({**deepcopy(rows[0]),'span_m':25.})
    return rows


def metrics_for(row,scenario):
    return [row['scenarios'][scenario]['installed_cost_usd'],row['quantities']['installed_study_mass_kg'],row['scenarios'][scenario]['working_days']]


def pareto(rows,scenario):
    eligible=[{**r,'objectives':metrics_for(r,scenario),'violation':0.} for r in rows if r['status']=='completed' and r['violation']==0.]
    return search.fronts(eligible)[0] if eligible else []


def leaders(rows,scenario):
    good=[r for r in rows if r['status']=='completed' and r['violation']==0.]
    if not good:return dict(cheapest=None,lightest=None,fastest=None,lowest_whole_life=None,pareto_ids=[])
    return dict(cheapest=min(good,key=lambda r:metrics_for(r,scenario)[0])['package_id'],
                lightest=min(good,key=lambda r:metrics_for(r,scenario)[1])['package_id'],
                fastest=min(good,key=lambda r:metrics_for(r,scenario)[2])['package_id'],
                lowest_whole_life=min(good,key=lambda r:r['scenarios'][scenario]['whole_life_cost_usd'])['package_id'],
                pareto_ids=[r['package_id'] for r in pareto(good,scenario)])


def choose_shortlist(rows,scenarios,number):
    good=[r for r in rows if r['status']=='completed' and r['violation']==0.];chosen=[]
    def keep(row):
        if row and row['package_id'] not in {r['package_id'] for r in chosen} and len(chosen)<number:chosen.append(row)
    for scenario in scenarios:
        for key,value in leaders(good,scenario).items():
            if key!='pareto_ids':keep(next((r for r in good if r['package_id']==value),None))
    for family in sorted({r['choice']['beam'] for r in good}):
        subset=[r for r in good if r['choice']['beam']==family]
        for objective in range(3):keep(min(subset,key=lambda r:metrics_for(r,scenarios[0])[objective]))
    for row in sorted(good,key=lambda r:(r['scenarios'][scenarios[0]]['installed_cost_usd'],r['package_id'])):keep(row)
    return chosen


def composite_diagnostics(c,span,kn_m):
    section=geometry(c['definition'])['deck'][1];roles=section['material_roles']
    other=set(roles)-{'concrete'}
    if len(other)!=1:return dict(status='not-a-two-material-composite',physical_validation=False)
    from osr_mech.civil.exploration import section_properties
    records={'concrete':c['material'],**c.get('material_records',{})};layers=[]
    for role in ('concrete',next(iter(other))):
        regions=[r for r,m in zip(section['regions'],roles) if m==role];s=section_properties(regions)
        layers.append(dict(E_pa=records[role]['youngs_modulus_pa']*records[role]['stiffness_factor'],area_m2=s['area_m2'],inertia_m4=s['inertia_y_m4'],centroid_z_m=s['centroid_z_m']))
    inputs=[0.,1e8,1e10]
    return dict(status='unmeasured-connector-sensitivity',layers=layers,
                stiffness_scenarios_n_m2=inputs,basis='synthetic distributed connector stiffness sweep, not a bond/connection capacity',
                responses=[section_mechanics.partial_interaction(span,*layers,k,kn_m*1000) for k in inputs],physical_validation=False)


def research_benchmarks(output):
    from .programme import component_campaign
    prior=component_campaign(output)
    top=dict(E_pa=30e9,area_m2=.1,inertia_m4=.1**3/12,centroid_z_m=.3)
    bottom=dict(E_pa=200e9,area_m2=.02,inertia_m4=.02**3/12,centroid_z_m=0.)
    slip=[section_mechanics.partial_interaction(10.,top,bottom,k,1000.,48) for k in (0.,1e7,1e12)]
    checks=[dict(name='Saint-Venant square series',passed=math.isclose(section_mechanics.rectangle_torsion(1.,1.),.140577014955,rel_tol=1e-8)),
            dict(name='noncomposite bending analytical limit',passed=math.isclose(slip[0]['peak_deflection_m'],slip[0]['noncomposite_limit_m'],rel_tol=1e-6)),
            dict(name='strong connector composite analytical limit',passed=math.isclose(slip[-1]['peak_deflection_m'],slip[-1]['perfect_bond_limit_m'],rel_tol=.002)),
            dict(name='connector stiffness reduces deflection and slip',passed=all(slip[i]['peak_deflection_m']>slip[i+1]['peak_deflection_m'] and slip[i]['maximum_interface_slip_m']>slip[i+1]['maximum_interface_slip_m'] for i in range(2)))]
    report=dict(existing_component_checks=prior,additional_checks=checks,slip_limit_results=slip,passed=prior['passed'] and all(c['passed'] for c in checks),physical_validation=False)
    write(output/'system-benchmarks.json',report);return report


def audit(report):
    scopes={1:('Baghdad input baseline','input.json',['actual train/soil/survey and adopted criteria']),
            2:('contracts, immutable IDs and modification history','events.json',['independent contract review and supplier detailing']),
            3:('bounded family/material/construction compatibility','input.json',['qualified manufacture/connection domains; optional model families remain open']),
            4:('shared CAD/IFC net quantities and material records','shortlist/',['reinforcement/tendon/fabrication drawings and measured lift CG']),
            5:('analytical/native domains and three-level refinements','benchmark-summary.json',['physical validation of applicability']),
            6:('native fields, parsers and output bindings','shortlist/',['reviewed project criteria/output specifications']),
            7:('nonlinear components and coupled pile-group stiffness','foundation-verification.json',['actual geotechnical calibration, cyclic/seismic/scour model selection']),
            8:('3D track/cap/bearing/braking and construction schedules','schedules/',['supplier moving/coupled train, stage locking and temporary stability']),
            9:('complete package/lifecycle and cost uncertainty','costs/',['actual quotes/charts/availability/productivity/maintenance and EPDs']),
            10:('bounded runner, checkpoint, archive and retrieval','checkpoint.json',['project compute/custody/retention agreement']),
            11:('seeded random/evolution Pareto and ranking reversals','report.json',['accepted constraints, prices and independent shortlist qualification']),
            12:('actual-section solids, 3D frames, orthotropy/torsion/slip','shortlist/',['calibrated failure/bond/contact/creep/fatigue/fire and prestress detailing']),
            13:('physical measurement/calibration/holdout workflow','physical-tests/test-programme.json',['actual laboratories, instrumented tests and independent validation']),
            14:('sealed proposal and existing controlled release boundary','promotion/proposal.json',['candidate-specific independent acceptance and existing authority release'])}
    return [dict(id=f'C{i:02d}',software_delivery=scope,evidence_path=path,
                 execution=('test templates generated; physical tests absent' if i==13 else 'blocked proposal generated; actual release receipt absent' if i==14 else 'research workflow executed' if report['budgets']['detailed'] else 'reduced-only; detailed confirmation omitted'),
                 engineering_acceptance='awaiting-external-evidence',remaining_acceptance=missing,complete=False) for i,(scope,path,missing) in scopes.items()]


def run(output,*,config_path=None,scenario_path=None,quotes_path=None,evaluations=None,seeds=None,shortlist_count=None,detail=True,resume=False):
    config_path=Path(config_path or HERE/'config/system-options.json').resolve();scenario_path=Path(scenario_path or HERE/'config/system-scenarios.json').resolve()
    quotes_path=Path(quotes_path or HERE/'config/commercial.json').resolve()
    config=load(config_path);validate_options(config);comparisons=load(scenario_path)
    if set(comparisons)!={'schema','scenarios','epd_factors','actual_supplier_prices_status'} or comparisons['schema']!='osr-civil-system-scenarios/1' or comparisons['epd_factors'] is not None:raise ValueError('commercial scenario contract invalid; measured EPD importer remains a separate evidence input')
    scenarios=comparisons['scenarios'];scenario_ids=[s['id'] for s in scenarios]
    if not scenarios or len(set(scenario_ids))!=len(scenario_ids):raise ValueError('duplicate/missing commercial scenarios')
    for s in scenarios:system_economics.validate_scenario(s);construction.validate_productivity(s['productivity'])
    limits=config['search'];evaluations=limits['evaluations_per_method'] if evaluations is None else evaluations
    seeds=limits['seeds'] if seeds is None else list(seeds);number=limits['shortlist_count'] if shortlist_count is None else shortlist_count
    controls=engineering_seeds(config)
    if type(evaluations) is not int or not 12<=evaluations<=1000 or not 1<=len(seeds)<=8 or len(set(seeds))!=len(seeds) or any(type(s) is not int for s in seeds) or not 1<=number<=40 or evaluations*len(seeds)*2+len(controls)>limits['maximum_evaluations']:
        raise ValueError('complete-system search budget outside registered bounds')
    if output.exists() and not resume:raise ValueError('system output exists; use --resume for matching inputs')
    if output.resolve().is_relative_to(ROOT) and not output.resolve().is_relative_to(ROOT/'build'):raise ValueError('system scratch outputs inside repository belong under build/')
    output.mkdir(parents=True,exist_ok=resume)
    source=dependencies();native=environment();load_case=planning_load(config);readiness=qualification.build()
    extra={}
    for path in (config_path,scenario_path,quotes_path,ROOT/'OpenSourceRail_Civil_Exploration_Plan.docx',
                 ROOT/'engineering/toolchain/tool-manifest.toml',ROOT/'docs/civil/complete-system-exploration.md',
                 ROOT/'engineering/analysis/structural_release.py',ROOT/'tools/automation/engineering-change.py'):
        path=path.resolve()
        if not path.is_relative_to(ROOT):raise ValueError('system configuration/quotation sources must be retained repository files')
        extra[path.relative_to(ROOT).as_posix()]=sha(path)
    source.update(extra);source.update(readiness['source_hashes']);source[load_case['source']]=load_case['source_sha256']
    frozen=dict(schema='osr-civil-complete-system-input/1',config=config,scenarios=comparisons,actual_quotes=load(quotes_path),
                repository_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                load_case=load_case,qualification_inputs=readiness,source_hashes=source,native_environment=native,
                budgets=dict(evaluations_per_method=evaluations,seeds=seeds,shortlist_count=number,detailed=detail,wall_seconds=limits['wall_seconds']))
    started=time.monotonic();cache={};events=[];file_hashes={};elapsed_before=0.
    if resume:
        if load(output/'input.json')!=frozen:raise ValueError('system resume source/environment/input mismatch')
        checkpoint=load(output/'checkpoint.json');elapsed_before=checkpoint['elapsed_s'];file_hashes=checkpoint['file_hashes']
        for relative,digest in file_hashes.items():
            path=(output/relative).resolve()
            if not path.is_relative_to(output.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('system checkpoint artifact mismatch')
        cache={r['package_id']:r for relative in file_hashes if relative.startswith('results/') for r in [load(output/relative)]}
        events=load(output/'events.json')
        if (output/'report.json').exists() and (output/'seal.json').exists():
            verify(output);return load(output/'report.json')
    else:
        write(output/'input.json',frozen)
        for relative,digest in source.items():
            target=output/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/relative).read_bytes())
            if sha(target)!=digest:raise ValueError('system source changed while preparing')
            file_hashes[target.relative_to(output).as_posix()]=digest
        file_hashes['input.json']=sha(output/'input.json')
        write(output/'events.json',events);file_hashes['events.json']=sha(output/'events.json')
        write(output/'checkpoint.json',dict(elapsed_s=0.,file_hashes=file_hashes))
    if 'benchmark-summary.json' in file_hashes:benchmarks=load(output/'benchmark-summary.json')
    else:
        attempts=output/'components';attempts.mkdir(exist_ok=True)
        folder=attempts/f'attempt-{len(list(attempts.iterdir()))+1}'
        benchmarks=research_benchmarks(folder)
        write(output/'benchmark-summary.json',benchmarks)
        for p in list(folder.rglob('*'))+[output/'benchmark-summary.json']:
            if p.is_file():file_hashes[p.relative_to(output).as_posix()]=sha(p)
        write(output/'checkpoint.json',dict(elapsed_s=elapsed_before+time.monotonic()-started,file_hashes=file_hashes))
    if not benchmarks['passed']:raise ValueError('system numerical benchmarks failed')
    foundation_cache={};foundation_records=[]
    for f in config['foundations']:
        for soil in config['soil_scenarios']:
            record=foundations.refinement(f['parameters'],config['materials']['normal'],soil)
            record.update(foundation_id=f['id'],soil_id=soil['id']);foundation_records.append(record)
            if not record['passed']:raise ValueError('foundation numerical refinement failed: '+f['id'])
            foundation_cache[f['id'],soil['id']]=record['selected']
    write(output/'foundation-verification.json',foundation_records);file_hashes['foundation-verification.json']=sha(output/'foundation-verification.json')
    prior={(e['seed'],e['method'],e['iteration']):e for e in events}
    def retain(path,value,compressed=False):
        path=output/path
        if compressed:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(encoded(value),mtime=0))
        else:write(path,value)
        file_hashes[path.relative_to(output).as_posix()]=sha(path)
    def checkpoint():
        retain(Path('events.json'),events)
        temporary=output/'checkpoint.tmp';write(temporary,dict(elapsed_s=elapsed_before+time.monotonic()-started,file_hashes=file_hashes))
        temporary.replace(output/'checkpoint.json')
    def evaluate(choice,seed,method,iteration,parents):
        if elapsed_before+time.monotonic()-started>limits['wall_seconds']:raise TimeoutError('registered system search wall budget exhausted')
        selected_study,_=study_for(choice,config)
        package_id=identity(dict(choice=choice,material=config['materials'][choice['material']],support_material=config['materials'][choice['support_material']],
                                 material_roles=selected_study['material_records'],foundation=selected_study['foundation']))
        event=dict(seed=seed,method=method,iteration=iteration,package_id=package_id,parents=list(parents))
        previous=prior.get((seed,method,iteration))
        if previous:
            if previous['package_id']!=package_id:raise ValueError('resumed system trajectory differs')
            return cache[package_id]
        if package_id in cache:row=cache[package_id];event['status']='verified-cache-hit'
        else:
            row=dict(package_id=package_id,choice=choice,status='failed',violation=1e30,objectives=[1e30]*3,
                     engineering_feasibility='unresolved',physical_release=False)
            phase='geometry-contract'
            try:
                study,definition=study_for(choice,config);c=candidate(definition,study,reason=f'{method} seed {seed} iteration {iteration}')
                validate_candidate(c);q=takeoff(c,study)
                units=construction.units(c,study,choice['beam_method'],choice['pier_method'],choice['cap_method'])
                responses=[];violations=[];lim=config['research_constraints']
                for soil in config['soil_scenarios']:
                    phase='foundation-verification'
                    key=(identity(c['foundation']),soil['id'])
                    if key not in foundation_cache:
                        fnd=foundations.refinement(c['foundation'],config['materials']['normal'],soil)
                        if not fnd['passed']:raise ValueError('variant foundation stiffness refinement failed')
                        foundation_cache[key]=fnd['selected'];retain(Path(f'foundation-variants/{key[0]}-{soil["id"]}.json'),fnd)
                    ground=foundation_cache[key];model=System(c,study,ground,8)
                    phase='native-planar'
                    for braking in (0.,study['analysis']['braking_fraction']):
                        response=model.uniform_service(load_case['kn_m_per_track'],braking_fraction=braking)
                        responses.append(dict(soil=soil['id'],foundation_response=ground,**response))
                        values=[('relative_deflection',response['response']['relative_deck_deflection_m'],choice['span_m']*lim['relative_deflection_span_ratio']),
                            ('settlement',response['response']['foundation_settlement_m'],lim['settlement_m']),
                            ('gross_elastic_stress',response['response']['gross_elastic_fibre_stress_pa'],lim['gross_elastic_stress_pa']),
                            ('pier_gross_elastic_stress',max(a['gross_elastic_fibre_stress_pa'] for a in response['pier_actions']),lim['gross_elastic_stress_pa']),
                            ('pier_drift',response['response']['pier_top_horizontal_m'],config['pier_height_m']*lim['pier_drift_ratio']),
                            ('planning_axial_resistance',max(a['vertical_n'] for a in response['support_actions']),ground['planning_axial_resistance_n'])]
                        for name,value,limit in values:
                            if limit is not None and value>limit:violations.append(dict(soil=soil['id'],braking_fraction=braking,metric=name,value=value,provisional_limit=limit,ratio=value/limit))
                if units['maximum_lift_mass_kg']>lim['max_lift_mass_kg']:
                    violations.append(dict(soil=None,metric='max_lift_mass',value=units['maximum_lift_mass_kg'],provisional_limit=lim['max_lift_mass_kg'],ratio=units['maximum_lift_mass_kg']/lim['max_lift_mass_kg']))
                costs={}
                for scenario in scenarios:
                    phase='construction-schedule'
                    schedule=construction.schedule(c,study,units,scenario['productivity'])
                    phase='complete-cost'
                    priced=system_economics.scenario_price(c,study,choice,units,schedule,scenario,scenario_path)
                    sid=scenario['id'];retain(Path(f'schedules/{package_id}/{sid}.json.gz'),schedule,True)
                    retain(Path(f'costs/{package_id}/{sid}.json'),priced)
                    costs[sid]=dict(installed_cost_usd=priced['installed_cost_usd'],whole_life_cost_usd=priced['whole_life_cost_usd'],working_days=schedule['programme_working_days'],
                                   critical_task_count=schedule['critical_task_count'],classification='synthetic-conditional-scenario',actual_supplier_price=False)
                actual=system_economics.actual_price(c,study,units,frozen['actual_quotes'])
                retain(Path(f'costs/{package_id}/supplier-pending.json'),actual)
                retain(Path(f'candidates/{c["id"]}.json'),c);retain(Path(f'studies/{c["id"]}.json'),study)
                row.update(candidate_id=c['id'],quantities=q,construction=units,native_responses=responses,scenarios=costs,
                           actual_installed_cost_usd=actual['installed_cost_usd'],actual_whole_life_cost_usd=actual['whole_life_cost_usd'],
                           actual_unpriced_scope=actual['unpriced_scope'],embodied_carbon_kg=None,carbon_status='source-bound EPD factors missing',
                           actual_supplier_costs_source_bound=actual['actual_baghdad_price'],
                           material_capacity_status='unresolved; gross stresses retained, no strength/fatigue/prestress acceptance inferred',
                           research_violations=violations,violation=sum(r['ratio']-1 for r in violations),status='completed',
                           objective_basis='first declared synthetic price/productivity scenario; not Baghdad quotations or approved feasibility')
                row['objectives']=metrics_for(row,scenario_ids[0])
            except (ValueError,RuntimeError) as error:
                row['error']=str(error);row['failure_kind']=phase
            cache[package_id]=row;event['status']=row['status'];retain(Path(f'results/{package_id}.json'),row)
        events.append(event);checkpoint()
        if len(events)%24==0:print(f'Complete systems: {len(events)} evaluations, {sum(r["status"]=="completed" and r["violation"]==0 for r in cache.values())} provisional passes',flush=True)
        return row
    control_rows=[evaluate(choice,0,'engineering-seed',i,[]) for i,choice in enumerate(controls)]
    summaries=[];timeout=False
    for seed in seeds:
        for method in ('random','pareto-evolution'):
            rng=np.random.default_rng(seed);rows=[];pool=[]
            try:
                for i in range(evaluations):
                    parent=None
                    if method=='pareto-evolution' and i>=limits['population']:
                        parent=pool[int(rng.integers(len(pool)))]
                    choice=sample(config,rng,i,parent);parents=[parent['package_id']] if parent else [control_rows[i%len(control_rows)]['package_id']]
                    row=evaluate(choice,seed,method,i,parents);rows.append(row);pool=search.select(pool+[row],min(limits['population'],len(pool)+1))
            except TimeoutError:timeout=True
            good=[r for r in rows if r['status']=='completed' and r['violation']==0.]
            summaries.append(dict(seed=seed,method=method,requested_evaluations=evaluations,completed_evaluations=len(rows),
                                  provisional_passes=len(good),best_synthetic_cost_usd=min((r['objectives'][0] for r in good),default=None),
                                  best_mass_kg=min((r['objectives'][1] for r in good),default=None),best_working_days=min((r['objectives'][2] for r in good),default=None)))
            if timeout:break
        if timeout:break
    rows=list(cache.values());shortlist=choose_shortlist(rows,scenario_ids,number);refinements=[]
    for row in shortlist:
        cid=row['candidate_id'];c=load(output/f'candidates/{cid}.json');study=load(output/f'studies/{cid}.json')
        refinement=dict(package_id=row['package_id'],candidate_id=cid,solid_meshes=[],physical_release=False)
        if detail:
            folder=output/'shortlist'/row['package_id']
            if resume and (folder/'refinement.json').exists():
                refinement=load(folder/'refinement.json')
                for relative,digest in load(folder/'refinement-seal.json')['files'].items():
                    p=(folder/relative).resolve()
                    if not p.is_relative_to(folder.resolve()) or sha(p)!=digest:raise ValueError('shortlist refinement artifact changed')
            else:
                folder.mkdir(parents=True,exist_ok=True)
                attempt=folder/f'attempt-{len(list(folder.glob("attempt-*")))+1}'
                try:
                    native_meshes=[detailed.run(c,study,h,attempt/f'solid-{h:g}',additional_service_kn_m=load_case['kn_m_per_track']) for h in (.8,.4,.2)]
                    error=abs(native_meshes[-1]['midspan_displacement_m']/native_meshes[-2]['midspan_displacement_m']-1)
                    refinement.update(solid_meshes=native_meshes,relative_displacement_change=error,convergence_passed=error<=.05)
                    frame_checks=[];fine_frames=[]
                    for soil in config['soil_scenarios']:
                        long=next(r['foundation_response'] for r in row['native_responses'] if r['soil']==soil['id'])
                        transverse_refinement=foundations.refinement(c['foundation'],config['materials']['normal'],soil,axis='transverse')
                        if not transverse_refinement['passed']:raise ValueError('transverse foundation refinement failed')
                        trans=transverse_refinement['selected']
                        for loaded,braking in ((2,0.),(1,0.),(2,study['analysis']['braking_fraction'])):
                            frames=[space_frame.run(c,study,long,trans,load_case['kn_m_per_track'],loaded,m,braking_fraction=braking) for m in (8,16,32)]
                            relative=abs(frames[-1]['peak_relative_deflection_m']/frames[-2]['peak_relative_deflection_m']-1)
                            path=attempt/f'frame-{soil["id"]}-{loaded}-track-braking-{braking:g}.json.gz';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(encoded(frames),mtime=0))
                            frame_checks.append(dict(soil=soil['id'],loaded_tracks=loaded,braking_fraction=braking,relative_deflection_change=relative,passed=relative<=.05,
                                                     peak_relative_deflection_m=frames[-1]['peak_relative_deflection_m'],peak_cap_bending_nm=frames[-1]['peak_cap_bending_nm'],
                                                     peak_deck_torsion_nm=frames[-1]['peak_deck_torsion_nm'],peak_deck_roll_rad=frames[-1]['peak_deck_roll_rad']))
                            fine_frames.append(frames[-1])
                    refinement['space_frame_checks']=frame_checks
                    refinement['composite_slip_diagnostic']=composite_diagnostics(c,row['choice']['span_m'],load_case['kn_m_per_track'])
                    sections=[pier_physics(c,s) for s in geometry(c['definition'])['pier']]
                    forces=[p['local_force'] for r in row['native_responses'] for p in r['pier_actions']]
                    axial=max(max(abs(p[0]),abs(p[3])) for p in forces);horizontal=max(max(abs(p[1]),abs(p[4])) for p in forces)
                    Eref=c['material']['youngs_modulus_pa']*c['material']['stiffness_factor']
                    pd=nonlinear.pier_pdelta(config['pier_height_m'],min(s['area_m2'] for s in sections),min(s['inertia_y_m4'] for s in sections),Eref,axial,horizontal)
                    pd['basis']='isolated prismatic minimum-section cantilever under worst reduced axial/shear actions; diagnostic only, not full flexible-base stability or candidate strength'
                    refinement['pier_pdelta_diagnostic']=pd
                    refinement['convergence_passed']=refinement['convergence_passed'] and all(r['passed'] for r in frame_checks) and pd['analytical_relative_error']<=.002
                    refinement['refined_research_deflection_passed']=all(r['peak_relative_deflection_m']<=row['choice']['span_m']*config['research_constraints']['relative_deflection_span_ratio'] for r in frame_checks)
                    # CAD/BIM checks cover complete piles, material regions and voids.
                    receipt=bim.export(c,study,attempt/'assembly.ifc')
                    from osr_mech.civil.exploration import assembly_cad
                    cad_volume=assembly_cad(c['definition'],c['foundation'],study['route_length_m']).volume/1e9
                    if not math.isclose(cad_volume,receipt['source_volume_m3'],rel_tol=1e-9):raise ValueError('complete-system CAD/IFC quantity mismatch')
                    refinement['cad_ifc_volume_m3']=cad_volume
                except (ValueError,RuntimeError) as error:
                    refinement.update(convergence_passed=False,error=str(error))
                write(folder/'refinement.json',refinement)
                write(folder/'refinement-seal.json',dict(files={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p!=folder/'refinement-seal.json'}))
                print(f'Detailed systems: {len(refinements)+1}/{len(shortlist)}; converged={refinement.get("convergence_passed",False)}',flush=True)
        refinements.append(refinement)
    if not (output/'physical-tests').exists():validation.protocols(output/'physical-tests',[r['candidate_id'] for r in shortlist[:5]])
    wins={sid:leaders(rows,sid) for sid in scenario_ids}
    confirmed_ids={r['package_id'] for r in refinements if r.get('convergence_passed') and r.get('refined_research_deflection_passed')}
    confirmed=[r for r in rows if r['package_id'] in confirmed_ids]
    acceptance=qualification.build()
    report=dict(schema='osr-civil-complete-system-report/1',deployment='baghdad',scope=dict(route_length_m=config['route_length_m'],tracks=2),
                repository_commit=frozen['repository_commit'],
                load_case=load_case,status='budget-exhausted' if timeout else 'completed',native_environment=native,
                budgets=frozen['budgets'],elapsed_s=elapsed_before+time.monotonic()-started,
                evaluated_attempts=len(events),distinct_packages=len(rows),native_completed=sum(r['status']=='completed' for r in rows),
                provisional_passes=sum(r['status']=='completed' and r['violation']==0 for r in rows),search_methods=summaries,
                objectives=['conditional installed/whole-life cost','installed study mass and maximum erection-unit mass','finite-resource working time'],
                screening_winners=wins,winners={sid:leaders(confirmed,sid) for sid in scenario_ids} if detail else wins,
                winner_basis='converged native shortlist and provisional deflection screen' if detail else 'reduced static planning screen only',
                shortlist=[r['package_id'] for r in shortlist],refinements=refinements,component_benchmarks=benchmarks,
                numerical_refinement_passed=bool(refinements) and detail and all(r.get('convergence_passed') for r in refinements),
                cheapest_qualified_design=None,qualified_feasible_pareto_set=[],global_optimum_proven=False,
                actual_supplier_costs_known=bool([r for r in rows if r['status']=='completed']) and all(r.get('actual_supplier_costs_source_bound') for r in rows if r['status']=='completed'),
                physical_release=False,operating_release=False,all_document_acceptance_complete=False,
                qualification_inputs=acceptance,unimplemented_options=config['unimplemented_options'],
                remaining_model_domains=['moving/coupled Baghdad train requires supplier records','nonlinear 3D cyclic/seismic and scour/group calibration',
                                         'reinforcement/prestress/joint/contact capacity and stage locking','physical fire/durability/fatigue and independent acceptance'],
                source_hashes=source,scenario_ranking_reversals=[sid for sid in scenario_ids[1:] if wins[sid]!=wins[scenario_ids[0]]])
    report['work_packages']=audit(report)
    if detail:
        store=output/'artifact-store';restored=output/'retrieved-shortlist'
        index=load(store/'index.json') if store.exists() else storage.pack(output/'shortlist',store)
        for relative,receipt in index['files'].items():
            if sha(output/'shortlist'/relative)!=receipt['sha256']:raise ValueError('shortlist archive source changed')
        if restored.exists():
            for relative,receipt in index['files'].items():
                if sha(restored/relative)!=receipt['sha256']:raise ValueError('retrieved shortlist artifact changed')
            retrieval=dict(integrity_verified=True,files_restored=len(index['files']))
        else:retrieval=storage.restore(store,restored)
        report['artifact_retrieval']=dict(integrity_verified=retrieval['integrity_verified'],file_count=retrieval['files_restored'])
    write(output/'report.json',report)
    from .system_report import render
    render(report,rows,config,output)
    proposal=dict(schema='osr-civil-system-change-proposal/1',status='blocked-awaiting-supplier-site-physical-and-independent-evidence',
                  packages=report['shortlist'],candidate_ids=[r['candidate_id'] for r in shortlist],
                  existing_change_workflow='tools/automation/engineering-change.py',existing_release_workflow='engineering/analysis/structural_release.py',
                  actual_gate_receipt=None,acceptance=False,physical_release=False,operating_release=False,
                  impacts=['catalogue/CAD/IFC/BOM','manufacturing/rigging/transport','foundation/ground tests','cost/schedule/maintenance','Baghdad structural qualification'])
    write(output/'promotion/proposal.json',proposal);write(output/'promotion/seal.json',dict(files={'proposal.json':sha(output/'promotion/proposal.json')},accepted=False,signature=None))
    current_sources=dependencies()
    if current_sources!={k:source[k] for k in current_sources if k in source} or any(sha(ROOT/p)!=h for p,h in source.items()):raise ValueError('system inputs changed during execution; outputs not accepted as current')
    inventory={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file() and p!=output/'seal.json' and p.name!='checkpoint.tmp'}
    write(output/'seal.json',dict(schema='osr-civil-system-seal/1',files=inventory,physical_release=False,accepted=False))
    return report


def verify(output,*,current=True):
    seal=load(output/'seal.json')
    for relative,digest in seal['files'].items():
        path=(output/relative).resolve()
        if not path.is_relative_to(output.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('system artifact hash mismatch: '+relative)
    report=load(output/'report.json')
    if current and any(sha(ROOT/p)!=h for p,h in report['source_hashes'].items()):raise ValueError('system sources are stale')
    if report['physical_release'] or report['qualified_feasible_pareto_set']:raise ValueError('research system report cannot claim acceptance')
    return report
