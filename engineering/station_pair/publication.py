"""Portable research dossier; native replay is separate from byte/source verification."""
from pathlib import Path
from math import isclose
import gzip,json
from copy import deepcopy
from engineering.station_rail.common import digest,encoded,identity
from engineering.design_search import requirement_policy
from . import ROOT,FLAGS,coordinator,economics,native_bridge,control_policy,history

OUTPUT='docs/design-engine/station-pair'


def sources(root=ROOT):
    root=Path(root)
    base=root/'engineering/station_pair'
    paths=[p for p in base.iterdir() if p.is_file() and p.suffix in ('.py','.json')]
    paths.extend(p for p in (base/'web').iterdir() if p.is_file() and p.suffix in ('.html','.js','.css'))
    return {**coordinator.source_hashes(root),'engineering/design_search/requirement_policy.py':digest(root/'engineering/design_search/requirement_policy.py'),
            **{p.relative_to(root).as_posix():digest(p) for p in sorted(paths)}}


def _sealed(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Station-pair record identity differs: '+key)


def _unreleased(value):
    if any(value.get(k) is not v for k,v in FLAGS.items()):
        raise ValueError('Station-pair research cannot grant release or change the reference')


def summary(study):
    result={k:study[k] for k in ('study_id','brief','body_candidate_id','body_bundle_id','mass_evaluation_id',
        'normal_case_count','conditional_arrivals','outline_screens','mass_summary','limitations',
        'execution_wall_s','native_build_id','native_binary_sha256',*FLAGS)}
    result['schema']='osr-station-pair-summary/2'
    result['control_comparison']=control_comparison(study)
    result['downloads']=dict(study='study.json.gz',mass='mass-reconciliation.json.gz',
        business='delivery-draft.json.gz',manufacturing='delivery-draft.json.gz')
    result['rows']=[]
    for c in study['cases']:
        result['rows'].append(dict(c['summary'],installed_capital_usd=c['cost']['methods'][0]['installed_capital_usd'],
            whole_life_NPV_usd=c['cost']['methods'][0]['whole_life_NPV_usd'],
            hotel_charging=c['cost']['hotel_charging']))
    result['finalists']=[]
    for f in study['finalists']:
        c=next(x for x in study['cases'] if x['variant']['candidate_id']==f['candidate_id']
               and x['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        checks=[dict(name=t['name'],state=t['result']['state'],
            final_position_m=t['result']['final_position_m'],normal_numerical_arrival=t['result']['normal_numerical_arrival'],
            fault_stop_in_route=t['result']['fault_stop_in_route'],hold_reason=t['result']['hold_reason'],
            maximum_absolute_jerk_m_s3=t['result']['maximum_absolute_jerk_m_s3'],
            bounds_supported=None if t['result'].get('control') is None else t['result']['control']['bounds_valid'],
            departure_held=False if t['result'].get('control') is None else t['result']['control']['departure_held'],
            end_of_authority_violated=None if t['result'].get('control') is None else t['result']['control']['end_of_authority_violated'],
            unpowered_route_energy_bound=t['unpowered_route_energy_bound']) for t in f['cases']]
        result['finalists'].append(dict(candidate_id=f['candidate_id'],speed_cap_km_h=f['speed_cap_km_h'],
            experiment_purpose=f['experiment_purpose'],
            family=c['variant']['family'],name=c['variant']['name'],trace=c['journey']['trace'],
            request=c['request'],cost=c['cost'],checks=checks,refinement=f['refinement'],
            controller_basis=f['controller_basis'],repeated_duty_proxy=f['repeated_duty_proxy'],
            terminal_jerk_resolved=c['journey']['terminal_jerk_resolved']))
    return result


def control_comparison(study):
    def normal(c):
        return dict(c['summary'],final_position_m=c['journey']['final_position_m'])
    def fault(t):
        r=t['result'];p=r.get('control')
        return dict(state=r['state'],final_position_m=r['final_position_m'],
            normal_numerical_arrival=r['normal_numerical_arrival'],fault_stop_in_route=r['fault_stop_in_route'],
            bounds_supported=None if p is None else p['bounds_valid'],
            departure_held=False if p is None else p['departure_held'],
            end_of_authority_violated=None if p is None else p['end_of_authority_violated'],
            hold_reason=r['hold_reason'])
    pairs=[];faults=[]
    for old,new in zip(study['fixed_control_cases'],study['cases']):
        if old['variant']['candidate_id']!=new['variant']['candidate_id'] or old['summary']['speed_cap_km_h']!=new['summary']['speed_cap_km_h']:
            raise ValueError('Controller comparison changed physical candidate or speed cap')
        row=new['summary'];pairs.append(dict(candidate_id=row['candidate_id'],name=row['name'],family=row['family'],
            distance_m=row['distance_m'],speed_cap_km_h=row['speed_cap_km_h'],fixed=normal(old),feedback=normal(new)))
    for f in study['finalists']:
        c=next(c for c in study['cases'] if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        for old,new in zip(f['fixed_control_cases'],f['cases']):
            if old['name']!=new['name']:raise ValueError('Fault comparison names differ')
            faults.append(dict(candidate_id=f['candidate_id'],name=new['name'],family=c['variant']['family'],
                design_name=c['variant']['name'],distance_m=c['request']['distance_m'],speed_cap_km_h=f['speed_cap_km_h'],
                fixed=fault(old),feedback=fault(new)))
    return dict(parent_study_id=study['parent_fixed_control']['study_id'],
        fixed_arrivals=sum(c['summary']['numerical_arrival'] for c in study['fixed_control_cases']),
        feedback_arrivals=study['conditional_arrivals'],normal_pairs=pairs,fault_pairs=faults,
        policy_note='Common bounded policy and simulated observations; no feedback brake-point fitting. The model boundary stays at D, independent of berth tolerance. Initial applied hold and fault notifications are explicit assumptions. No physical protection qualification.')


def delivery(study,bundle):
    candidates=[]
    for f in study['finalists']:
        c=next(x for x in study['cases'] if x['variant']['candidate_id']==f['candidate_id']
               and x['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        cost=c['cost'];counts={a['owner']:a['quantity'] for a in cost['accounts']}
        candidates.append(dict(candidate_id=f['candidate_id'],body_candidate_id=study['body_candidate_id'],
            body_bundle_id=study['body_bundle_id'],mass_evaluation_id=study['mass_evaluation_id'],
            journey_evaluation_id=c['journey']['evaluation_id'],cost_evaluation_id=cost['evaluation_id'],
            catalogue_items=[dict(part_id=p['id'],component_definition_id=p['component_definition_id'],
                material_id=p['material_id'],quantity_per_train=p['quantity_per_train'],
                fleet_quantity=p['quantity_per_train']*cost['service']['total_trainsets'],make_buy=p['make_buy']) for p in bundle['parts']],
            additional_equipment=c['variant']['inventory'],cost_accounts=cost['accounts'],
            construction=dict(two_track_route_m=c['request']['distance_m'],nominal_span_m=20.,
                nominal_beams=counts['civil-beam-factory'],shared_support_packages=counts['shared-pier-foundation-bearings'],
                beam_geometry=cost['civil_geometry_reference'],stations=2,
                sequence=['Survey utilities/ground and obtain approved alignment and foundation design',
                    'Qualify reusable moulds, reinforcement/prestress, lifting inserts and bearings',
                    'Establish site access and protected temporary works; build foundations and shared piers',
                    'Cast/cure/inspect spans; approve actual crane radius/capacity and erection stability',
                    'Install bearings/spans, rails, anchors, walkways, drainage and station access',
                    'Install candidate-specific launch/conductor, grid and service chargers',
                    'Test controls, independent brakes, rescue, evacuation and system interfaces'],
                construction_duration_days=None,capacity_and_ground_evidence_available=False),
            assembly_sequence=['Use the exact 605-type catalogue and its controlled assembly plan',
                'Resolve installed locations, interfaces, trim, inertia, axle reactions and access',
                'Detail architecture additions and qualify grip/drive/brake/charging interfaces',
                'Update structural, civil, electrical, production and cost calculations from the revised bundle',
                'Approve drawings, process/QA limits and prototype evidence before any release'],
            interface_holds=['105.25 m body-plus-gap length excludes unknown end coupling/platform margin',
                'Station launcher window is front-interface travel, not completed installation length or platform geometry',
                'Installed body CAD, joints, axle loads, clearances and dynamics remain open',
                'No old viaduct FEM, crane permission or old 112-bundle physical-journey acceptance transfers'],
            disabled=1,executable_work_order=False,transactions_performed=False,**FLAGS))
    return dict(schema='osr-station-pair-delivery-draft/1',study_id=study['study_id'],candidates=candidates,
        integrated_selection=None,disabled=1,transactions_performed=False,**FLAGS)


def requirements(study):
    # Retain every mandatory obligation. Bare numerical values can screen only
    # the declared advisory research targets, never supply approved evidence.
    criteria={k:deepcopy(v) for k,v in requirement_policy.catalogue()['criteria'].items()
              if v['category']=='mandatory_obligation'}
    criteria['target.station_pair_moving_jerk']=dict(id='target.station_pair_moving_jerk',
        category='project_preference',observable='moving_jerk_m_s3',unit='m/s3',operator='max',
        limit=study['brief']['comfort_jerk_target_m_s3'],provenance=None,obligation_kind=None,
        affected_interfaces=['ride-response','controls','contact'])
    criteria['model.feedback_contract']=dict(id='model.feedback_contract',category='numerical_validity_domain',
        observable='feedback_contract_supported',unit='1',operator='verified',limit=None,provenance=None,
        obligation_kind=None,affected_interfaces=['control-model','simulated-observations','braking','route-boundary'])
    return dict(schema='osr-station-pair-requirement-context/1',study_id=study['study_id'],
        criteria=criteria,assessments=[requirement_policy.assess(
            dict(moving_jerk_m_s3=next(c['journey']['maximum_absolute_jerk_m_s3'] for c in study['cases']
                if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h']),
                feedback_contract_supported=next(c['summary']['control_bounds_supported'] is True and c['summary']['model_route_boundary_exceeded'] is False
                for c in study['cases'] if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])),
            criteria,candidate_id=f['candidate_id']) for f in study['finalists']],
        scope='Moving-jerk target is advisory; safety, protected service, accessibility and physical limits remain unsupported obligations',**FLAGS)


def readme(study):
    s=summary(study);compare=s['control_comparison'];rows=[]
    for f in s['finalists']:
        r=next(x for x in s['rows'] if x['candidate_id']==f['candidate_id'] and x['speed_cap_km_h']==f['speed_cap_km_h'])
        prices=r['installed_capital_usd'];arrival=f"{r['journey_s']:.1f} s" if r['journey_s'] is not None else 'Held or missed berth'
        speed=f"{r['actual_peak_km_h']:.1f}" if r['actual_peak_km_h'] is not None else 'Not run'
        rows.append(f"| {r['name']} | {speed} / {r['speed_cap_km_h']:.0f} | {arrival} | ${prices['low']/1e6:.2f} / ${prices['base']/1e6:.2f} / ${prices['high']/1e6:.2f}m |")
    return f'''# Candidate-linked station-pair comparison

**[Open the interactive comparison](index.html)** · [Full results and traces](study.json.gz) ·
[Mass reconciliation](mass-reconciliation.json.gz) · [Delivery draft](delivery-draft.json.gz) ·
[Requirement/evidence assessment](requirement-assessments.json).

This executable research path connects the **605-type, six-car parts proposal** to
mass scenarios, source-rating force hypotheses, Rust motion and braking, fleet,
civil quantities, costs and disabled manufacturing/construction records. It
compares a fixed nominal braking point with a bounded feedback controller on the
same physical configurations. No reference adoption or operating authority follows.

## What changed

The original experiment is [retained with its exact source epoch](../../archives/station-pair-fixed-control-20261107/README.md).
Its fixed controller remains reproducible. The current packet adds simulated
position, speed and acceleration observations, explicit uncertainty and response
bounds, pre-applied holding brakes and continuous distance feedback.

**Feedback braking points are never fitted offline or separately per fault.**
All mass, wind, grade, force and sensor experiments retain the same policy bounds
for each architecture. Grade and drive-fault notifications are explicit assumed
observations. Tests include both notified and unobserved partial drive failure.
The actual plant values remain separate from the controller's declared bounds;
posthoc domain diagnostics expose disagreements without passing truth to control.

The model travel boundary is **D**, the declared station target. The existing
plus/minus 2 m berth accuracy does not grant extra travel beyond D. Histories are
not snapped to a station. Bounded low-speed docking is permitted only where the
candidate already has powered hardware at the destination; cable designs receive
no invented force after their launch window.

## Results under assumptions

There are **{study['normal_case_count']} nominal cases**: four propulsion families,
two station spacings and three speed caps. The fixed method gives
**{compare['fixed_arrivals']} conditional arrivals**; feedback gives
**{compare['feedback_arrivals']}**. The viewer shows every paired result, including
short stops, departure holds, authority overruns and out-of-domain assumptions.
Arrival counts alone do not measure physical feasibility or qualified protection.

The original fixed cohorts remain in the paired experiments. Additional nominees
come from the feedback nominal screens, before inspecting the common fault suite.
They are next experiments, not an integrated selection. These examples use a **1.5 km,
two-station, two-track pilot**, 276 passenger places, 4,000 peak passengers/hour/
direction and 85% planning occupancy. The demand-derived 200 s headway provides
4,222.8 planning places/hour/direction; timetable protection remains unverified.

| Paired experiment | Actual peak / cap km/h | Feedback berth result | Pilot installed USD low / base / high |
|---|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

Budgets include rolling stock, stations/access, reference-box concrete quantities,
rails/fasteners, shared supports, erection, propulsion, grid/hotel chargers,
protection, depot, assembly/test/setup, integration and contingency. Failed or
held journeys retain an explicit provisional runtime allowance; their energy and
whole-life operating totals stay unknown. **These are pilot budgets, not 30 km
city prices, quotations or demonstrated bulk-purchase discounts.** Local assembly
versus purchased-custom figures primarily vary setup allowances, not proven
productivity. Every cost account states its basis and exclusions.

## Findings that remain important

- A passive train can brake but cannot add energy after leaving its powered
  window. A short stop is retained as a performance failure; it is not corrected
  by moving the recorded position. Receiving-side positioning equipment would
  require its own physical definition, quantities, cost and dynamic evaluation.
- On a constant +2% climb, the base 6% rotating-mass hypothesis gives at most
  approximately **653 m coast from 60 km/h**, even ignoring air drag. The current
  200/350 m launch windows leave 1,150–1,800 m to travel. Better control cannot
  fix that energy deficit: change propulsion, speed or alignment.
- The 35.56 kN brake-force and 90% controller-floor assumptions leave little
  worst-case downhill authority at high mass. Slower running, conservative
  refusal or a separately engineered brake/architecture change can be necessary.
  No bound is weakened to make a candidate pass.
- Simulated sensor biases, weaker-than-assumed brakes, delayed response and
  unsupported tailwind remain explicit experiments. An arrival outside the
  declared controller domain never establishes protected operation.
- Final rolling-to-held-stop jerk, wheel-slide response, flexible-train dynamics,
  brake heating, engagement and rescue still need appropriate models and evidence.
  Emergency and supervisory discontinuities retain their calculated jerk.

## Same-candidate manufacture, mass and cost

The [parts catalogue](../vehicle-parts/index.html) supplies materials, quantities,
stock/process allowances, fixings, routes, QA and removal methods. Its 110,404 BOM
units are reconciled in grouped occurrences, with shared inter-car parts counted
once. Explicit 2/5/10 t installation reserves produce normal-loaded, before-drive-
addition scenarios of approximately 101.19 / 115.51 / 137.30 t. These are counted
stock and allowances, not measured installed weights. Driven-wheel additions are
separate; installed CG/inertia, actual axle loads, trim and complete CAD remain open.

The body-plus-gap length is 105.25 m. End coupler projection, usable platform
margin, installed equipment clashes and moving interfaces remain unknown. The
exact [20 m civil geometry](../viaduct-backends/README.md) feeds fresh quantities,
without inheriting earlier FEM loads, reinforcement, foundations or crane approval.
The base lifting reserve exceeds a nominal 60 t class; actual radius, rigging and
erection stability need a lifting study. Draft records are disabled: no purchasing,
work order or control transactions occur. Production capacity and construction
programme duration remain unverified.

Energy includes propulsion, cable return/reset, continuous 35 kW/car auxiliaries,
dwell, terminal turn and 90% charging efficiency; a 50 kW/car control is retained.
Charging power is distinct from propulsion peak. Battery/charger limits and
spare/depot conditioning remain open. No regeneration credit is invented.
The repeated-duty RC proxy is uncalibrated, excludes idle motor/copper losses,
and its reported journey peak excludes reset-transient peaks.

The controller uses braking-curve principles described in the
[ERA introduction, sections 3.1–3.3](https://www.era.europa.eu/system/files/2022-11/Introduction%20to%20ETCS%20braking%20curves.pdf):
state uncertainty, braking buildup and track characteristics must be explicit.
This research method is not an ETCS implementation or compliance claim.

## Reproduce and challenge

```bash
./osr design station-pair plan
./osr design station-pair run --output /path/to/private/station-pair-run
./osr design station-pair publish --run /path/to/private/station-pair-run --output /path/to/fresh/publication
./osr design station-pair verify
./osr design station-pair verify --replay --state /path/to/private/replay
./osr design station-pair history-verify
```

Verification checks source, physical/evaluation identities, identical controller
policies, mass, cost ownership and every generated artifact. `--replay` rebuilds
the locked Rust kernel and compares published fixed/feedback nominal, fault and
refined-timestep outputs. Requests, unsuccessful trials, errors and resource
receipts remain in the private run. Source development and numerical execution use
separate directories; the worker process has explicit resource limits, not a
claimed OS sandbox.

Outline comparison and scoped pricing: **complete under assumptions**.
Installed engineering, robust protected service, manufacturing and operation:
**open**. Resolve measured actuator/brake/charging characteristics, installed
geometry, axle reactions, receiving/positioning behaviour, civil moving loads and
prototype correlation before advancing an integrated design.

Study `{study['study_id']}` · body `{study['body_candidate_id']}`.
[Canonical source](../../../engineering/station_pair/).
'''


def artifacts(study,reconciliation,bundle,root=ROOT):
    root=Path(root)
    out={'README.md':readme(study).encode(),'summary.json':encoded(summary(study)),
        'study.json.gz':gzip.compress(encoded(study),mtime=0),
        'mass-reconciliation.json.gz':gzip.compress(encoded(reconciliation),mtime=0),
        'delivery-draft.json.gz':gzip.compress(encoded(delivery(study,bundle)),mtime=0),
        'requirement-assessments.json':encoded(requirements(study))}
    for n in ('index.html','app.js','app.css'):out[n]=(root/'engineering/station_pair/web'/n).read_bytes()
    return out


def publish(run,*,root=ROOT,output=None):
    root=Path(root);run=Path(run);output=root/OUTPUT if output is None else Path(output)
    if output.exists():raise ValueError('Fresh publication directory required')
    r=json.loads((run/'manifest.json').read_bytes());_sealed(r,'manifest_id');_unreleased(r)
    if any(digest(run/n)!=sha for n,sha in r['files_sha256'].items()):raise ValueError('Run packet changed')
    study=json.loads(gzip.decompress((run/'result.json.gz').read_bytes()))
    reconciliation=json.loads(gzip.decompress((run/'mass-reconciliation.json.gz').read_bytes()))
    _sealed(study,'study_id');_sealed(reconciliation,'evaluation_id')
    if study['source_sha256']!=coordinator.source_hashes(root):raise ValueError('Run source changed; rerun the study')
    brief,bundle,expected,_=coordinator.variants(root)
    if reconciliation!=expected:raise ValueError('Mass reconciliation differs')
    files=artifacts(study,reconciliation,bundle,root);output.mkdir(parents=True)
    for n,raw in files.items():(output/n).write_bytes(raw)
    m=dict(schema='osr-station-pair-publication/1',study_id=study['study_id'],
        source_sha256=sources(root),files_sha256={n:digest(output/n) for n in files},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m))
    return verify(root=root,output=output)


def _near(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,float):return isclose(a,b,rel_tol=1e-9,abs_tol=1e-7)
    if isinstance(a,dict):return a.keys()==b.keys() and all(_near(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(_near(x,y) for x,y in zip(a,b))
    return a==b


def verify(*,root=ROOT,output=None,replay=False,state=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if any(p.is_symlink() for p in (output,*output.parents)) or any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('Ordinary publication files required')
    m=json.loads((output/'manifest.json').read_bytes());_sealed(m,'manifest_id');_unreleased(m)
    got={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if got!=m['files_sha256'] or m['source_sha256']!=sources(root):raise ValueError('Station-pair publication source/artifact changed')
    study=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()));_sealed(study,'study_id');_unreleased(study)
    if study['study_id']!=m['study_id'] or study['source_sha256']!=coordinator.source_hashes(root):raise ValueError('Study source/identity changed')
    brief,bundle,reconciliation,variants=coordinator.variants(root)
    if study['brief']!=brief or study['mass_evaluation_id']!=reconciliation['evaluation_id']:
        raise ValueError('Study input or mass evaluation differs')
    if study.get('schema')!='osr-station-pair-study/2' or study.get('parent_fixed_control')!=history.verify(root):
        raise ValueError('Feedback study must retain the exact fixed-control source epoch')
    if study.get('feedback_brake_point_fits')!=0:raise ValueError('Feedback cannot fit per-case brake points')
    if (study.get('integrated_selection') is not None or study.get('available_operating_maps_added')!=0
        or study.get('priced_city_models_replaced')!=0 or study.get('regeneration_saving_credited') is not False):
        raise ValueError('Research control cannot select a railway, add force evidence or silently reprice cities')
    byid={v['candidate_id']:v for v in variants};requests=[];expected=[]
    def native_record(q,r):
        _sealed(q,'id');_sealed(r,'evaluation_id')
        if r['candidate_id']!=q['candidate_id'] or r['id']!=q['id'] or r['native_input_id']!=identity(q):
            raise ValueError('Mixed native physical/request identity')
        if any(r.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
            raise ValueError('Native conditional record cannot grant release')
        p=r.get('control');contract=q.get('control')
        if contract is None:
            if p is not None:raise ValueError('Fixed request acquired an undeclared feedback controller')
        else:
            if p is None or p['policy_id']!=contract['policy_id'] or p['protected_service_qualified'] is not False:
                raise ValueError('Feedback policy/qualification identity differs')
            outside=r['final_position_m']>contract['end_of_authority_m']+1e-8
            if outside and (not p['end_of_authority_violated'] or r['normal_numerical_arrival'] or r['fault_stop_in_route']):
                raise ValueError('Travel boundary overrun cannot become successful arrival or fault stop')
        requests.append(q);expected.append(r)
    def check_normal(c,mode):
        v=c['variant'];r=c['journey'];q=c['request']
        if v!=byid.get(v['candidate_id']) or q['candidate_id']!=v['candidate_id']:
            raise ValueError('Mixed journey physical/request identity')
        nominal=coordinator.case_for(v,bundle,reconciliation,brief,
            speed_km_h=c['summary']['speed_cap_km_h'],control_mode=mode,root=root)
        if mode=='fixed':
            if type(q['brake_start_m']) not in (int,float) or not 0<=q['brake_start_m']<=q['distance_m']:
                raise ValueError('Fixed nominal brake point outside route')
            nominal['brake_start_m']=q['brake_start_m']
        nominal['id']=identity({k:v for k,v in nominal.items() if k!='id'})
        if q!=nominal:raise ValueError('Nominal request differs from declared candidate, controller and brief')
        native_record(q,r)
        if c['cost']!=economics.evaluate(v,r,bundle,reconciliation,brief,root=root):raise ValueError('Cost replay differs')
        want=coordinator._brief_result(v,q,r,c['cost'],brief)
        if any(c['summary'].get(k)!=val for k,val in want.items()):raise ValueError('Comparison row differs')
    for c in study['cases']:check_normal(c,'feedback')
    for c in study['fixed_control_cases']:check_normal(c,'fixed')
    if study['rows']!=[c['summary'] for c in study['cases']]:raise ValueError('Study rows differ')
    case_count=len(variants)*len(brief['speed_caps_km_h'])
    for group in ('cases','fixed_control_cases'):
        if len(study[group])!=case_count or len({(c['variant']['candidate_id'],c['summary']['speed_cap_km_h']) for c in study[group]})!=case_count:
            raise ValueError('Controller comparison omitted or duplicated a nominal case')
    if study['normal_case_count']!=case_count or study['conditional_arrivals']!=sum(c['journey']['normal_numerical_arrival'] for c in study['cases']):
        raise ValueError('Nominal counters differ')
    if study['outline_screens']!=sum(r['outline_screen'] for r in study['rows']):raise ValueError('Outline counter differs')
    for row in study['rows']:
        cohort=[x for x in study['rows'] if x['distance_m']==row['distance_m'] and x['outline_screen']]
        objectives=('base_installed_usd','journey_s','full_grid_kwh')
        expected_front=row['outline_screen'] and not any(all(x[k]<=row[k] for k in objectives)
            and any(x[k]<row[k] for k in objectives) for x in cohort)
        if row['pareto_for_next_experiment'] is not expected_front:raise ValueError('Partial experiment front differs')
    choices=coordinator.choose_experiments(study['fixed_control_cases'],study['cases'])
    selected=[c for c,_ in choices]
    if study['next_experiment_candidate_ids']!=[c['variant']['candidate_id'] for c in selected]:
        raise ValueError('Experiment selection changed after seeing feedback fault results')
    if [(f['candidate_id'],f['speed_cap_km_h']) for f in study['finalists']]!=[(c['variant']['candidate_id'],c['summary']['speed_cap_km_h']) for c in selected]:
        raise ValueError('Selected paired fault experiment was omitted or changed')
    if [f['experiment_purpose'] for f in study['finalists']]!=[purpose for _,purpose in choices]:raise ValueError('Experiment selection purpose differs')
    for f in study['finalists']:
        nominal=next(c for c in study['cases'] if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        fixed=next(c for c in study['fixed_control_cases'] if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        for key,base in (('cases',nominal),('fixed_control_cases',fixed)):
            trials=coordinator.followup_requests(base['variant'],bundle,reconciliation,brief,base['request'],root=root)
            if len(trials)!=len(f[key]):raise ValueError('Fault comparison omitted a declared trial')
            for (name,q),t in zip(trials,f[key]):
                if name!=t['name'] or q!=t['request']:raise ValueError('Fault replay changed the common policy, observations or plant')
                if t['unpowered_route_energy_bound']!=coordinator.coast_bound(base['variant'],q):raise ValueError('Coast energy bound differs')
                native_record(q,t['result'])
                if q.get('control') is not None:
                    if not control_policy.same_policy(q['control'],nominal['request']['control']):raise ValueError('Fault controller bounds changed')
                    if (name.startswith('outside-') or name=='tailwind-unsupported') and t['result']['control']['bounds_valid'] is not False:
                        raise ValueError('Unsupported plant/observation cannot become an in-domain control result')
        q=dict(nominal['request'],dt_s=brief['refined_dt_s']);q['id']=identity({k:v for k,v in q.items() if k!='id'})
        r=f['refinement']['result'];native_record(q,r)
        change=r['final_position_m']-nominal['journey']['final_position_m']
        if f['refinement']['final_position_change_m']!=change:raise ValueError('Coupled timestep sensitivity differs')
    for n,raw in artifacts(study,reconciliation,bundle,root).items():
        got=(output/n).read_bytes()
        if n.endswith('.gz'):got=gzip.decompress(got);raw=gzip.decompress(raw)
        if got!=raw:raise ValueError('Generated station-pair artifact differs: '+n)
    if replay:
        if state is None:raise ValueError('Private replay state directory required')
        actual=native_bridge.execute(requests,Path(state),root=root)
        for a,b in zip(actual,expected):
            # Stored execution receipts differ from the replay's receipts.
            remove=('evaluation_id','native_receipt_id','native_input_id')
            if not _near({k:v for k,v in a.items() if k not in remove},{k:v for k,v in b.items() if k not in remove}):
                raise ValueError('Native replay differs: '+a['id'])
    return dict(verified=True,study_id=study['study_id'],manifest_id=m['manifest_id'],
        conditional_arrivals=study['conditional_arrivals'],normal_cases=study['normal_case_count'],
        fault_cases=sum(len(f['cases']) for f in study['finalists']),native_replayed=replay,
        native_replayed_cases=len(requests) if replay else 0,
        unique_native_replayed_cases=len({identity(q) for q in requests}) if replay else 0,**FLAGS)
