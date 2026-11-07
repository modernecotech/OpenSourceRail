"""Portable research dossier; native replay is separate from byte/source verification."""
from pathlib import Path
from math import isclose
import gzip,json
from copy import deepcopy
from engineering.station_rail.common import digest,encoded,identity
from engineering.design_search import requirement_policy
from . import ROOT,FLAGS,coordinator,economics,native_bridge

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
    result['schema']='osr-station-pair-summary/1'
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
            unpowered_route_energy_bound=t['unpowered_route_energy_bound']) for t in f['cases']]
        result['finalists'].append(dict(candidate_id=f['candidate_id'],speed_cap_km_h=f['speed_cap_km_h'],
            family=c['variant']['family'],name=c['variant']['name'],trace=c['journey']['trace'],
            request=c['request'],cost=c['cost'],checks=checks,refinement=f['refinement'],
            controller_basis=f['controller_basis'],repeated_duty_proxy=f['repeated_duty_proxy'],
            terminal_jerk_resolved=c['journey']['terminal_jerk_resolved']))
    return result


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
    return dict(schema='osr-station-pair-requirement-context/1',study_id=study['study_id'],
        criteria=criteria,assessments=[requirement_policy.assess(
            dict(moving_jerk_m_s3=next(c['journey']['maximum_absolute_jerk_m_s3'] for c in study['cases']
                if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])),
            criteria,candidate_id=f['candidate_id']) for f in study['finalists']],
        scope='Moving-jerk target is advisory; safety, protected service, accessibility and physical limits remain unsupported obligations',**FLAGS)


def readme(study):
    s=summary(study);rows=[]
    for f in s['finalists']:
        r=next(x for x in s['rows'] if x['candidate_id']==f['candidate_id'] and x['speed_cap_km_h']==f['speed_cap_km_h'])
        p=r['installed_capital_usd']
        rows.append(f"| {r['name']} | {r['actual_peak_km_h']:.1f} / {r['speed_cap_km_h']:.0f} | {r['journey_s']:.1f} s | {r['mass_kg']/1000:.2f} t | {r['full_grid_kwh']:.2f} | ${p['low']/1e6:.2f} / ${p['base']/1e6:.2f} / ${p['high']/1e6:.2f}m |")
    return f'''# Candidate-linked station-pair comparison

**[Open the interactive comparison](index.html)** · [Results and traces](study.json.gz) ·
[Mass reconciliation](mass-reconciliation.json.gz) · [Manufacturing/construction draft](delivery-draft.json.gz)
· [Requirement/evidence assessment](requirement-assessments.json)

This is one executable path from the **605-type, six-car parts proposal** through
mass scenarios, available-rating hypotheses, Rust force-driven motion, independent
braking, fleet, civil quantities and a complete scoped budget. It creates no
movement authority, reference adoption or engineering approval.

## Results under the declared assumptions

The bounded study evaluates **{study['normal_case_count']} cases**, from 16 physical
system definitions across four architecture families, two spacings and three speed
caps. **{study['conditional_arrivals']} nominal conditional runs arrive**; {study['outline_screens']}
also meet the declared time, moving-jerk, energy-residual, static-hold and demand
screens. These are numerical research results, not the missing authenticated
physical journeys in the historical 112-bundle portfolio.

The next-experiment examples below both use a **1.5 km, two-station, two-track pilot**,
276 normal passenger places, 4,000 peak passengers/hour/direction and 85% planning
occupancy. The demand-led headway is **200 s**, providing **4,222.8 planning
places/hour/direction**. This is capacity arithmetic, not protected timetable proof.

| Next experiment | Actual peak / cap km/h | Moving time | Conditional loaded mass | Full grid kWh/departure | Pilot installed USD low / base / high |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

Prices include four trainsets for these pilot examples, two accessible stations,
two-track reference-box concrete quantities, rails/fasteners, shared supports,
erection allowances, candidate propulsion, grid and hotel chargers, protection,
depot, assembly/test/setup, integration and contingency. **These are not 30 km city
prices, supplier quotations or demonstrated mass-purchase discounts.** Purchased
custom and local-assembly scenarios primarily vary setup allowances; they do not
establish a make-versus-buy productivity advantage. The report provides all cost
accounts and 30-year discounted scenarios, including renewal and operating costs.

## What the comparison revealed

- **Mass is reconciled, not measured:** the exact counted catalogue plus explicit
  2/5/10 t installation reserves gives loaded, architecture-before-additions
  scenarios of approximately 101.19 / 115.51 / 137.30 t. Driven-wheel equipment is
  added separately. The 105.25 m body-plus-gap length, 24 service actuators and
  760 mm wheels belong to this new proposal. Actual installed CG, inertia, axle
  loads, trim, service access and full CAD assembly remain unresolved.
- **A speed cap is not a speed requirement.** The cheap six-motor, 200 m cable
  example peaks near 44 km/h under its 50 km/h cap. Its acceleration is force-limited
  despite requesting 1 m/s². Longer windows and larger drives remain visible
  alternatives; neither 72 km/h nor 900 m is prescribed.
- **Fault replay exposes failure:** mass and wind changes miss the berth with the
  nominal brake point. The ±2% grade controls expose missing hill-start protection
  and substantial downhill overrun. Power-loss and emergency-stop examples on
  level track use independent assumed pneumatic braking. They do not prove safe
  recovery, wheel-slide protection, brake temperature or an operational controller.
- **Jerk has two distinct results:** nominal moving jerk is calculated and screened;
  the final rolling-to-held-stop acceleration transition remains unresolved. The
  replay does not conceal emergency discontinuities or refit braking per fault.
- **Auxiliaries matter:** continuous 35 kW/car, a 50 kW/car control, dwell and
  terminal turn are accounted for, with 90% charging efficiency. Required dwell-only
  recharge power is shown separately from propulsion peak power; charger curves,
  battery SOC/temperature and depot/spare conditioning remain open.
- **No regeneration saving is credited.** Detached tug/rope kinetic energy is
  exported to a disposal/reset account, never silently donated to coasting. Return
  energy and reset-time/force allowances are counted. The eight-cycle thermal RC
  proxy is uncalibrated; reported journey peaks exclude reset-transient peaks and
  idle motor/copper losses. It is not a thermal qualification.
- **LIM and hybrid remain in the comparison:** absent candidate-specific available
  force maps produce explicit holds, unknown energy/power/mass additions and
  positive provisional cost reserves. They do not become zero-cost failures.

## From source to manufacture

The [parts catalogue](../vehicle-parts/index.html) supplies materials, multiplicity,
stock/process allowances, joint/fixing proposals, QA and repair methods. The
candidate-linked delivery draft scales those same parts to the pilot fleet, adds
architecture equipment, and lists construction quantities and assembly dependencies.
Its ERPNext-style records are **disabled**; no purchasing, work order or control
transaction is performed. Production capacity and construction duration remain
unknown until actual processes, drawings, sites and crews are sized.

The [civil geometry dossier](../viaduct-backends/README.md) provides the exact
20 m reference-box geometry for fresh quantity calculations. Earlier FEM loads,
prestress/reinforcement design, bearings, foundations and crane approval do not
transfer to this heavier/different candidate. The base lift reserve exceeds a
nominal 60 t class: configured radius/capacity, rigging and temporary stages need
an actual lifting study.

The standalone Rust kernel retains finite drive windows, force/power/contact caps,
external rope/tug mass, grade, wind, drag, independent brakes, event transitions,
temperature budget and work-energy residuals. Position is never reset to the berth.
Native requests, failed trials and resource receipts remain in the private run;
the portable packet contains all nominal/fault inputs and outputs for replay.
All source hashes, physical/evaluation identities and cost ownership are checked.

## Reproduce

```bash
./osr design station-pair plan
./osr design station-pair run --output /path/to/private/station-pair-run
./osr design station-pair publish --run /path/to/private/station-pair-run --output /path/to/fresh/publication
./osr design station-pair verify
./osr design station-pair verify --replay --state /path/to/private/replay
```

Verification checks current source, candidate, mass, accounting and artifact
identities. `--replay` separately rebuilds the locked Rust kernel and compares all
published nominal, fault and timestep-refinement outputs. It requires Cargo's
locked dependencies to be locally available. Independent tests cover numerical
energy closure, cap/transition handling, faults and cache integrity. Verification
does not grant physical acceptance.

### Evidence and next action

Outline comparison and scoped pricing: **complete under stated assumptions**.
Installed engineering, robust protected journey, manufacturing release and
operation: **open**. There is no integrated selection. Resolve measured hot-duty
force/brake/charger characteristics, installed equipment and axle reactions,
adaptive protected stopping/hill starts, coupling/reset/rescue, civil moving loads
and prototype correlation before advancing a candidate.

Study `{study['study_id']}` · body `{study['body_candidate_id']}`.
Canonical source: [engineering/station_pair](../../../engineering/station_pair/).
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
    byid={v['candidate_id']:v for v in variants};requests=[];expected=[]
    for c in study['cases']:
        v=c['variant'];r=c['journey'];q=c['request'];_sealed(r,'evaluation_id')
        if v!=byid.get(v['candidate_id']) or q['candidate_id']!=v['candidate_id'] or r['native_input_id']!=identity(q):
            raise ValueError('Mixed journey physical/request identity')
        nominal=coordinator.case_for(v,bundle,reconciliation,brief,speed_km_h=c['summary']['speed_cap_km_h'])
        nominal['brake_start_m']=q['brake_start_m'];nominal['id']=identity({k:v for k,v in nominal.items() if k!='id'})
        if q!=nominal:raise ValueError('Nominal request differs from declared candidate and brief')
        if any(r.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
            raise ValueError('Native conditional record cannot grant release')
        if c['cost']!=economics.evaluate(v,r,bundle,reconciliation,brief,root=root):raise ValueError('Cost replay differs')
        want=coordinator._brief_result(v,q,r,c['cost'],brief)
        if any(c['summary'].get(k)!=val for k,val in want.items()):raise ValueError('Comparison row differs')
        requests.append(q);expected.append(r)
    if study['rows']!=[c['summary'] for c in study['cases']]:raise ValueError('Study rows differ')
    for f in study['finalists']:
        nominal=next(c for c in study['cases'] if c['variant']['candidate_id']==f['candidate_id'] and c['summary']['speed_cap_km_h']==f['speed_cap_km_h'])
        for t in f['cases']:
            q=t['request'];r=t['result'];_sealed(r,'evaluation_id')
            _sealed(q,'id')
            if (q['candidate_id']!=f['candidate_id'] or q['brake_start_m']!=nominal['request']['brake_start_m']
                    or r['candidate_id']!=q['candidate_id'] or r['native_input_id']!=identity(q)):
                raise ValueError('Fault replay changed candidate or nominal braking setting')
            requests.append(q);expected.append(r)
        q=dict(nominal['request'],dt_s=brief['refined_dt_s']);q['id']=identity({k:v for k,v in q.items() if k!='id'})
        r=f['refinement']['result'];_sealed(r,'evaluation_id')
        if r['native_input_id']!=identity(q):raise ValueError('Refined request differs')
        requests.append(q);expected.append(r)
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
        native_replayed_cases=len(requests) if replay else 0,**FLAGS)
