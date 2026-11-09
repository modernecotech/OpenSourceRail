"""One mapped-city outline: requirements, editing, re-costing and delivery drafts."""
from copy import deepcopy
import json
import gzip
from math import isfinite
from pathlib import Path
import re
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,encoded,identity
from . import coordinator,completion,city_inputs,city_alignment,city_service,city_project_cost
from . import publication_cache

PRODUCER='engineering/outline/city_workflow.py'
_SELF_SHA=digest(__file__)
FLAGS=completion.FLAGS
SELECTIONS=('auto','original','anchor-preserving-chord-research','rounded-four-edge-ring-research')
SERVICE_BOUNDS=dict(peak_demand_pphpd=(1.,100000.),maximum_headway_s=(10.,3600.),
    planning_occupancy=(.1,1.),planning_availability_assumption=(.1,1.),
    operating_hours_per_day=(1.,24.),operating_days_per_year=(1.,366.))
ALIGNMENT_BOUNDS=dict(maximum_chord_deviation_m=(.1,500.),minimum_saving_m=(.1,1000.),
    minimum_relative_saving=(.00001,.2),maximum_added_walk_m=(50.,5000.),
    walk_detour_factor=(1.,3.),row_width_m=(5.,100.),square_scale=(.4,1.),
    corner_radius_m=(25.,2000.),lateral_acceleration_m_s2=(.1,.65),
    corner_samples=(4,32),unverified_square_crossing_fraction=(.01,.5))
ARTIFACTS={'request.json','result.json','summary.json','planning.json','delivery-plan.json',
           'business-drafts.json','alignments.geojson','performance.json','manifest.json'}
GZIP_ARTIFACTS={'result.json','delivery-plan.json','business-drafts.json'}


def stored_name(name):
    return name+'.gz' if name in GZIP_ARTIFACTS else name


def read_json(output,name,maximum=96*1024**2):
    path=completion._ordinary(Path(output)/stored_name(name))
    if name in GZIP_ARTIFACTS:
        with gzip.open(path,'rb') as stream:raw=stream.read(maximum+1)
    else:raw=path.read_bytes()
    if len(raw)>maximum:raise ValueError('City study artifact exceeds its read budget')
    return json.loads(raw)


def _numeric(value,name,bounds):
    if type(value) not in (int,float) or not isfinite(value) or not bounds[0]<=value<=bounds[1]:
        raise ValueError('Bounded finite '+name+' required')
    return value


def normalize(value):
    if not isinstance(value,dict) or set(value)-{'schema','city_slug','expected_outline_evaluation_id',
            'service','alignment','project','selection','base_plan','base_study_id','base_seed_id','edit_bundle'}:
        raise ValueError('Typed city study request required')
    v=deepcopy(value)
    if v.get('schema','osr-city-workflow-request/1')!='osr-city-workflow-request/1':
        raise ValueError('Unknown city study request schema')
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',v.get('city_slug','')):
        raise ValueError('Known city slug required')
    expected=v.get('expected_outline_evaluation_id')
    if expected is not None and not re.fullmatch('[0-9a-f]{64}',expected):
        raise ValueError('Expected outline evaluation identity required')
    for group,bounds in (('service',SERVICE_BOUNDS),('alignment',ALIGNMENT_BOUNDS)):
        values=v.setdefault(group,{})
        if not isinstance(values,dict):raise ValueError('Unknown '+group+' option')
        if group=='service' and 'line_peak_demand_pphpd' in values:
            demand_map=values['line_peak_demand_pphpd']
            if not isinstance(demand_map,dict) or not demand_map:
                raise ValueError('Nonempty line peak demand mapping required')
            for line_id,demand in demand_map.items():
                if not isinstance(line_id,str) or not line_id:
                    raise ValueError('Exact line IDs required for line peak demand')
                _numeric(demand,'line peak demand',SERVICE_BOUNDS['peak_demand_pphpd'])
        allowed=set(bounds)|({'line_peak_demand_pphpd'} if group=='service' else set())
        if set(values)-allowed:raise ValueError('Unknown '+group+' option')
        for key,number in values.items():
            if key!='line_peak_demand_pphpd':_numeric(number,key,bounds[key])
    if 'corner_samples' in v['alignment'] and type(v['alignment']['corner_samples']) is not int:
        raise ValueError('Integer corner sampling budget required')
    p=v.setdefault('project',{})
    if not isinstance(p,dict) or set(p)-{'pricing_scenario','station_launch_mode','foreign_local_rate_transfer'}:
        raise ValueError('Unknown project pricing option')
    if p.get('pricing_scenario','project-make-buy') not in ('project-make-buy','china-bulk-buy'):
        raise ValueError('Supported project supply basis required')
    if p.get('station_launch_mode','cable-capstan') not in coordinator.budget.MODES:
        raise ValueError('Supported station launch evaluator required')
    if 'foreign_local_rate_transfer' in p:
        factors=p['foreign_local_rate_transfer']
        if not isinstance(factors,list) or len(factors)!=3:raise ValueError('Three local-rate cases required')
        for number in factors:_numeric(number,'local-rate transfer',(.25,5.))
        if factors!=sorted(factors):raise ValueError('Ordered local-rate sensitivity cases required')
    v.setdefault('selection','auto')
    if v['selection'] not in SELECTIONS:raise ValueError('Supported alignment evaluator required')
    bases=set(v)&{'base_plan','base_study_id','base_seed_id'}
    if len(bases)>1:raise ValueError('Use one planning base source')
    if 'base_study_id' in v and not re.fullmatch('[0-9a-f]{32}',v['base_study_id']):
        raise ValueError('Known immutable base study required')
    if 'base_seed_id' in v and not re.fullmatch('[0-9a-f]{64}',v['base_seed_id']):
        raise ValueError('Known published planning seed required')
    if (bool(bases)!=('edit_bundle' in v)):
        raise ValueError('Planning base and edit bundle are required together')
    if len(encoded(v))>2*1024**2:raise ValueError('City study request exceeds its byte budget')
    v['schema']='osr-city-workflow-request/1'
    return v


def _sources(root):
    if digest(Path(root)/PRODUCER)!=_SELF_SHA:raise ValueError('Loaded city workflow changed; restart its worker')
    names=(PRODUCER,'engineering/outline/planning_adapter.py','engineering/outline/planning_geometry.py',
        'engineering/outline/revision_service.py','engineering/outline/delivery_plan.py',
        'services/integration/osr_integration/city_outline.py','engineering/outline/city_worker.py')
    return {n:digest(Path(root)/n) for n in names}


def _rules(previous,request):
    rules=deepcopy(previous);rules.update(request['service'])
    if request['service']:
        rules['demand_source']='User-defined mapped-city planning scenario; authenticated forecast not attached'
    for group in ('alignment','project'):
        if request[group]:rules[group]={**rules.get(group,{}),**request[group]}
    if request['project']:
        rules['pricing_basis']=rules['project'].get('pricing_scenario',rules['pricing_basis'])
    rules['operations_shifts_per_day']=2 if rules['operating_hours_per_day']<=18 else 3
    return rules


def _validate_line_demand_mapping(rules,city_input):
    if 'line_peak_demand_pphpd' not in rules:return
    expected={line['line_id'] for line in city_input['lines']}
    actual=set(rules['line_peak_demand_pphpd'])
    if actual!=expected:
        raise ValueError('Line peak demand mapping must match exact city line IDs; missing='+
            repr(sorted(expected-actual))+' extra='+repr(sorted(actual-expected)))


def _functional(record,access):
    failures=[]
    if not record['outline_complete']:failures.append('A necessary braking, interface or nominal energy bound fails')
    if access.get('status') in ('hold','fail') or access.get('access_screen')=='fail':failures.append('Declared geographic access screen fails')
    for row in record['service_evaluation']['line_services']:
        checks=row.get('functional_checks',{})
        if row.get('functional_pass') is False:
            failures.append(row['line_id']+': '+json.dumps(checks,sort_keys=True))
        service=row['service'];req=row['requirements']
        if service['planning_usable_capacity_pphpd']+1e-8<req['peak_demand_pphpd']:
            failures.append(row['line_id']+': proposed headway cannot carry the declared demand')
        if req['headway_s']>req['maximum_headway_s']+1e-8:
            failures.append(row['line_id']+': proposed headway exceeds the declared maximum')
    return dict(pass_for_outline=not failures,failures=failures,
        actual_performance_qualified=False,unknown_physical_requirements=record['qualification_requirements'])


def evaluate(request,root=ROOT):
    from . import planning_adapter,revision_service,delivery_plan
    from services.integration.osr_integration import city_outline
    root=Path(root);start=time.perf_counter();v=normalize(request)
    detail=publication_cache.json_member('cities/'+v['city_slug']+'.json.gz',root)
    if v.get('expected_outline_evaluation_id',detail['evaluation_id'])!=detail['evaluation_id']:
        raise ValueError('The selected published outline changed; reload the city before recalculating')
    seed=detail['planning_seed'];context=coordinator.prepare(root)
    baseline=planning_adapter.export_plan(seed,root=root)
    revision=None;base_sources={};trusted_base=None;base=v.get('base_plan')
    if 'base_seed_id' in v:
        if v['base_seed_id']!=seed['seed_id']:raise ValueError('Published planning seed changed; reload before editing')
        base=baseline
    if 'base_study_id' in v:
        folder=completion._ordinary(root/'build/city-studies'/v['base_study_id']/'artifacts')
        parent=verify(folder,root=root)
        base=json.loads((folder/'planning.json').read_bytes())
        trusted_base=parent['files_sha256']['planning.json']
        base_sources={p.relative_to(root).as_posix():digest(p) for p in
            (folder/'planning.json',folder/'manifest.json')}
    if base is not None:
        if base['city']!=v['city_slug']:raise ValueError('Planning base belongs to another city')
        planning_adapter.verify_base(base,root=root,trusted_base_sha256=trusted_base)
    # An iterative edit inherits the verified study's demand, pricing and
    # operating policy; an empty request must not revert it to the seed defaults.
    rules=_rules(base['outline_context']['study_rules'] if base is not None else seed['rules'],v)
    if 'line_peak_demand_pphpd' in rules:
        mapped_input=(base['outline_context']['city_input_template'] if base is not None
            else city_inputs.load(v['city_slug'],root=root))
        _validate_line_demand_mapping(rules,mapped_input)
    if base is not None:
        revision=planning_adapter.apply_edits(base,v['edit_bundle'],root=root,trusted_base_sha256=trusted_base)
        revision=deepcopy(revision);revision['requirements']=rules
        revision['source_sha256']=coordinator.merge_sources(revision['source_sha256'],_sources(root))
        revision['evaluation_id']=identity({k:x for k,x in revision.items() if k!='evaluation_id'})
        proposals=[dict(kind='priced-planning-revision',city_input=revision['city_input'],
            alignment_id=revision['planning_revision_id'],selection_eligibility=revision['access_screen'])]
    else:
        inputs=city_inputs.load(v['city_slug'],root=root)
        proposals=city_alignment.propose(inputs,root=root,policy=rules)['variants']
        if v['selection']!='auto':proposals=[p for p in proposals if p['kind']==v['selection']]
        if not proposals:raise ValueError('This city has no requested alignment family to evaluate')
    cases=[]
    for proposal in proposals:
        inputs=proposal['city_input']
        service=(revision_service.evaluate(revision,context['spec']['design'],context['vehicle'],root=root)
                 if revision else city_service.evaluate(inputs,rules,context['spec']['design'],context['vehicle'],root=root))
        cost=city_project_cost.evaluate_city_cost(inputs,service['line_services'],context,policy=rules,root=root)
        record=completion._assemble_city(inputs,service,cost,context,rules)
        screen=_functional(record,proposal.get('selection_eligibility',{}))
        cases.append(dict(kind=proposal['kind'],alignment_id=proposal['alignment_id'],
            record=record,functional_screen=screen,
            selection_eligibility=proposal.get('selection_eligibility',{})))
    passing=[i for i,c in enumerate(cases) if c['functional_screen']['pass_for_outline']]
    chosen=min(passing or range(len(cases)),key=lambda i:(cases[i]['record']['cost']['whole_life_npv_usd']['base'],cases[i]['alignment_id']))
    selected=deepcopy(cases[chosen]['record'])
    # Project configuration includes the actual fleet and platform/civil resource
    # quantities; prices and evidence identities remain separate.
    config=dict(source_research_configuration_id=selected['research_configuration_id'],
        reference_candidate_ids=selected['reference_candidate_ids'],
        city_input_id=selected['input_id'],line_configurations=[dict(line_id=r['line_id'],
            propulsion=r['propulsion_hypothesis'],trainsets=r['service']['total_trainsets'],
            headway_s=r['requirements']['headway_s']) for r in selected['service_evaluation']['line_services']],
        civil_quantity_id=selected['cost']['civil']['quantities']['quantity_id'],
        platform_resources={k:x for k,x in selected['cost']['resources'].items() if k in
            ('boarding_edges','additional_berth_edges','access_sites','interchanges','totalcars')})
    selected['source_research_configuration_id']=selected['research_configuration_id']
    selected['research_configuration_id']=identity(config);selected['research_configuration']=config
    selected['delivery_draft']['research_configuration_id']=selected['research_configuration_id']
    selected['delivery_draft']['draft_id']=identity({k:x for k,x in selected['delivery_draft'].items() if k!='draft_id'})
    selected['planning_revision_id']=(revision['planning_revision_id'] if revision else
        identity(dict(city_input_id=selected['input_id'],request=v,seed_id=seed['seed_id'])))
    selected['selected_alignment_id']=cases[chosen]['alignment_id']
    selected['selected_alignment_kind']=cases[chosen]['kind']
    selected['source_sha256']=coordinator.merge_sources(selected['source_sha256'],_sources(root),base_sources)
    selected['evaluation_id']=identity({k:x for k,x in selected.items() if k!='evaluation_id'})
    # This record was calculated by this worker, not supplied by the client.
    # Its exact sealed bytes become the rebasing custody hash and are persisted
    # in result.json before the run manifest is exposed to another request.
    plan=planning_adapter.plan_from_record(seed,selected,root=root,
        trusted_record_sha256=identity(selected),design=context['spec']['design'])
    delivery=delivery_plan.evaluate(selected,root=root)
    business=city_outline.delivery_drafts(delivery,root=root)
    sources=coordinator.merge_sources(selected['source_sha256'],delivery['source_sha256'],
        business.get('source_sha256',{}),_sources(root))
    value=completion.seal(dict(schema='osr-mapped-city-workflow/1',request=v,city=selected['city'],
        source_outline_evaluation_id=seed['source_outline_evaluation_id'],planning_seed_id=seed['seed_id'],
        planning_base=baseline,planning_revision=plan,city_outline=selected,
        cases=cases,examined_alignment_id=cases[chosen]['alignment_id'],
        recommended_alignment_id=cases[chosen]['alignment_id'] if passing else None,
        outline_acceptance='accepted' if passing else 'requires-revision',
        calculation_complete=True,delivery_plan=delivery,business_drafts=business,
        source_sha256=sources,**FLAGS))
    if any(digest(root/n)!=sha for n,sha in sources.items()):raise ValueError('City study inputs changed during execution')
    return value,dict(elapsed_s=time.perf_counter()-start,native_solver_jobs=0,CAD_jobs=0,
        cases=len(cases),external_transactions=0)


def summary(value):
    city=value['city_outline'];cost=city['cost'];services=city['service_evaluation']['line_services']
    return dict(schema='osr-mapped-city-workflow-summary/1',evaluation_id=value['evaluation_id'],
        city=value['city'],source_outline_evaluation_id=value['source_outline_evaluation_id'],
        research_configuration_id=city['research_configuration_id'],planning_seed_id=value['planning_seed_id'],
        planning_revision_sha256=value['planning_revision']['revision_sha256'],
        calculation_complete=value['calculation_complete'],outline_acceptance=value['outline_acceptance'],
        installed_capital_usd=cost['installed_capital_usd'],whole_life_npv_usd=cost['whole_life_npv_usd'],
        price_per_route_km_usd=cost['price_per_route_km_usd'],scope_totals_usd=cost['scope_totals_usd'],
        trainsets=sum(r['service']['total_trainsets'] for r in services),
        service_lines=[dict(line_id=r['line_id'],headway_s=r['requirements']['headway_s'],
            trainsets=r['service']['total_trainsets'],propulsion=r['propulsion_hypothesis']['kind']) for r in services],
        cases=[dict(kind=c['kind'],alignment_id=c['alignment_id'],functional_screen=c['functional_screen'],
            installed_capital_usd=c['record']['cost']['installed_capital_usd'],
            whole_life_npv_usd=c['record']['cost']['whole_life_npv_usd']) for c in value['cases']],
        delivery_plan_id=value['delivery_plan']['plan_id'],business_draft_id=value['business_drafts']['draft_id'],
        delivery=dict(task_count=len(value['delivery_plan']['tasks']),
            cases={k:{f:v[f] for f in ('finish_workday','target_workdays','target_met','capacity_pass')}
                   for k,v in value['delivery_plan']['schedule']['cases'].items()},
            workforce=value['delivery_plan']['workforce'],
            cost_reconciliation=value['delivery_plan']['cost_reconciliation']),
        recommended_alignment_id=value['recommended_alignment_id'],**FLAGS)


def run(request,output,root=ROOT):
    root=Path(root).resolve();output=Path(output)
    output=completion._ordinary(output if output.is_absolute() else root/output)
    if output.exists():raise ValueError('Fresh immutable mapped-city study output required')
    value,timing=evaluate(request,root=root);output.mkdir(parents=True)
    records={'request.json':value['request'],'result.json':value,'summary.json':summary(value),
        'planning.json':value['planning_revision'],'delivery-plan.json':value['delivery_plan'],
        'business-drafts.json':value['business_drafts'],'performance.json':timing}
    variants=dict(variants=[dict(kind=c['kind'],alignment_id=c['alignment_id'],
        geometry_geojson=dict(type='FeatureCollection',features=[dict(type='Feature',
            properties=dict(line_id=line['line_id']),geometry=dict(type='LineString',coordinates=line['coordinates']))
            for line in c['record']['geometry_and_service']['lines']])) for c in value['cases']])
    records['alignments.geojson']=completion._alignment_geometry(variants,[c['record'] for c in value['cases']])
    from engineering.development_baseline.planning import _gzip_member
    for name,record in records.items():
        raw=encoded(record)
        (output/stored_name(name)).write_bytes(_gzip_member(raw) if name in GZIP_ARTIFACTS else raw)
    from services.integration.osr_integration import city_outline
    city_outline.export_drafts(value['business_drafts'],output/'business',root=Path(root).resolve())
    files={stored_name(n):digest(output/stored_name(n)) for n in records}
    files.update({p.relative_to(output).as_posix():digest(p) for p in (output/'business').iterdir() if p.is_file()})
    manifest=completion.seal(dict(schema='osr-mapped-city-workflow-publication/1',
        evaluation_id=value['evaluation_id'],source_sha256=value['source_sha256'],
        files_sha256=files,artifact_paths={n:stored_name(n) for n in records},**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(manifest));return manifest


def verify(output,root=ROOT,*,replay=False):
    output=completion._ordinary(Path(output));m=json.loads(completion._ordinary(output/'manifest.json').read_bytes())
    if (m.get('schema')!='osr-mapped-city-workflow-publication/1'
            or m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'})
            or any(m.get(k) is not False for k in FLAGS)):
        raise ValueError('City study manifest or release disposition differs')
    from services.integration.osr_integration import city_outline
    expected={stored_name(n) for n in ARTIFACTS-{'manifest.json'}}
    expected.update('business/'+kind.lower().replace(' ','-')+'.json' for kind in city_outline.DOCTYPES)
    expected.update({'business/drafts.json','business/manifest.json'})
    if set(m['files_sha256'])!=expected:raise ValueError('Unexpected city study artifacts')
    if m.get('artifact_paths')!={n:stored_name(n) for n in ARTIFACTS-{'manifest.json'}}:
        raise ValueError('City study logical artifact paths differ')
    for n,sha in m['files_sha256'].items():
        if digest(completion._ordinary(output/n))!=sha:raise ValueError('City study artifact differs')
    completion._check_sources(root,m['source_sha256'])
    value=read_json(output,'result.json')
    if (value['evaluation_id']!=m['evaluation_id']
            or value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'})
            or encoded(summary(value))!=(output/'summary.json').read_bytes()):
        raise ValueError('City study identity or summary differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('City study cannot grant release')
    from . import delivery_plan
    city=value['city_outline'];plan=value['delivery_plan'];business=value['business_drafts']
    for record,key,flags in ((city,'evaluation_id',FLAGS),(plan,'plan_id',delivery_plan.FLAGS),
                             (business,'draft_id',city_outline.FLAGS)):
        if record.get(key)!=identity({k:v for k,v in record.items() if k!=key}):
            raise ValueError('City study child identity differs: '+key)
        if any(record.get(k) is not False for k in flags):
            raise ValueError('City study child cannot grant release')
    completion._check_costs(city['cost'])
    if (plan['city_record_evaluation_id']!=city['evaluation_id']
            or plan['city_input_id']!=city['input_id']
            or plan['cost_evaluation_id']!=city['cost']['evaluation_id']
            or plan['research_configuration_id']!=city['research_configuration_id']):
        raise ValueError('City study delivery binding differs')
    for name,record in (('request.json',value['request']),('planning.json',value['planning_revision']),
                        ('delivery-plan.json',plan),('business-drafts.json',business)):
        if encoded(read_json(output,name))!=encoded(record):
            raise ValueError('City study standalone child differs: '+name)
    from . import planning_adapter
    planning_adapter.verify_base(value['planning_revision'],root=root,
        trusted_base_sha256=m['files_sha256']['planning.json'])
    if business['source_plan_id']!=plan['plan_id']:
        raise ValueError('City study business plan binding differs')
    _,business=city_outline.verify_export(output/'business',root=root)
    if encoded(business)!=encoded(value['business_drafts']):raise ValueError('Business draft scope differs')
    if replay:
        actual,_=evaluate(json.loads((output/'request.json').read_bytes()),root=root)
        if encoded(actual)!=encoded(value):raise ValueError('Mapped-city study does not replay')
    return m
