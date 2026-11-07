"""Reproducible cycle evidence and disabled manufacturing/cost drafts."""
from pathlib import Path
from copy import deepcopy
from math import isclose
import gzip,json
from engineering.station_rail.common import identity,digest,encoded
from engineering.station_pair.publication import _near
from engineering.station_pair import native_bridge as journey_bridge
from engineering.design_search import requirement_policy
from . import ROOT,FLAGS,coordinator,native_bridge,history

OUTPUT='docs/design-engine/station-cycle'


def sealed(v,key='evaluation_id'):
    if v.get(key)!=identity({k:x for k,x in v.items() if k!=key}):raise ValueError('Cycle identity differs: '+key)


def frontier(study):
    """Nominal-only next experiments, never a whole-railway selection."""
    rows=[r['row'] for r in study['records'] if r['experiment']=='nominal'
        and r['row']['arrived_legs']==r['row']['scheduled_legs']]
    def obj(r):return (r['cost']['installed_capital_usd']['base'],r['energy_reconciliation']['known_grid_subtotal_j'],r['maximum_moving_jerk_m_s3'])
    keep=[r for r in rows if not any(all(x<=y for x,y in zip(obj(q),obj(r)))
        and any(x<y for x,y in zip(obj(q),obj(r))) for q in rows)]
    return dict(purpose='Nominal serial-cycle next experiments; requested concurrent service and physical acceptance remain open',
        objectives=['same-assumed-service capital allowance','scoped serial grid subtotal','actual moving jerk'],
        candidates=[dict(candidate_id=r['candidate_id'],advisory_screen=r['advisory_screen'],
            objectives=list(obj(r)),action='Resolve measured force laws, handoff jerk and concurrent service before any integrated adoption') for r in keep],
        fault_outcomes_used_for_ranking=False,integrated_selection=None,**FLAGS)


def requirements(study):
    criteria={k:deepcopy(v) for k,v in requirement_policy.catalogue()['criteria'].items() if v['category']=='mandatory_obligation'}
    criteria['target.station_cycle_moving_jerk']=dict(id='target.station_cycle_moving_jerk',category='project_preference',
        observable='moving_jerk_m_s3',unit='m/s3',operator='max',limit=study['brief']['comfort_jerk_target_m_s3'],
        provenance=None,obligation_kind=None,affected_interfaces=['passengers','launch-handoff','contact'])
    return dict(schema='osr-station-cycle-requirement-context/1',study_id=study['study_id'],criteria=criteria,
        assessments=[requirement_policy.assess(dict(moving_jerk_m_s3=r['row']['maximum_moving_jerk_m_s3']),criteria,
            candidate_id=r['row']['candidate_id']) for r in study['records'] if r['experiment']=='nominal'],
        scope='Moving jerk is a declared advisory target; missing authenticated safety/structural evidence remains mandatory and open',**FLAGS)


def summary(study):
    return dict(schema='osr-station-cycle-summary/1',study_id=study['study_id'],brief=study['brief'],policy=study['policy'],
        limitations=study['limitations'],rows=[r['row'] for r in study['records'] if r['nominal']],
        faults=[r['row'] for r in study['records'] if not r['nominal']],
        historical_feedback='../../archives/'+history.OUTPUT.split('/')[-1]+'/README.md',next_experiments=frontier(study),integrated_selection=None,**FLAGS)


def delivery(study):
    designs={r['design']['variant']['candidate_id']:r['design'] for r in study['records']}
    rows=[]
    for cid,d in designs.items():
        r=next(r for r in study['records'] if r['design']['variant']['candidate_id']==cid and r['experiment']=='nominal')
        rows.append(dict(candidate_id=cid,physical_definition=d['variant']['physical_definition'],
            parent_candidate_id=d['variant'].get('parent_candidate_id'),body_candidate_id=study['body_candidate_id'],
            body_bundle_id=study['body_bundle_id'],sizing=d['sizing'],
            new_component_cost_accounts=r['cost']['full_scope']['extra_accounts'],
            lifecycle=r['cost']['full_scope'],
            manufacture_sequence=['Resolve actual capture/launch attachments and load paths into the exact six-car assembly',
                'Detail spring force/stroke or accumulator pressure/flow and specify fatigue/containment and locks',
                'Create controlled part and mating drawings, materials, weld/fastener limits and inspection criteria',
                'Fabricate, inspect and independently test modular banks, transfer drums, clutches, guards and supports',
                'Verify installed clearances, access, foundations, independent braking and protected engagement',
                'Measure force, losses, jerk, failure response and reset; correlate model before release'],
            prototype_tests=['Instrument capture force×displacement and stage continuity',
                'Measure stored/returned energy, dwell retention and reset energy/time',
                'Test full/empty/failed store bypass and positive release authorization',
                'Test real force–stroke/pressure–flow, containment, cable/clutch/fixing fatigue and thermal duty'],
            joint_and_fixing_count=None,interface_coordinates_verified=False,
            detail_status='Calculated assembly reserves; controlled CAD and build authorization pending',
            disabled=1,transactions_performed=False,executable_work_order=False,**FLAGS))
    return dict(schema='osr-station-cycle-delivery-draft/1',study_id=study['study_id'],candidates=rows,
        integrated_selection=None,disabled=1,transactions_performed=False,**FLAGS)


def readme(study):
    s=summary(study);lines=[]
    for r in s['rows']:
        L=r['ledger'];price=r['cost']['installed_capital_usd']['base']
        jerk='Unknown' if r['maximum_moving_jerk_m_s3'] is None else f"{r['maximum_moving_jerk_m_s3']:.3f}"
        lines.append(f"| {r['name']} / {r['experiment']} | {r['arrived_legs']}/{r['scheduled_legs']} | {L['capture_work_j']/3.6e6:.3f} | {L['delivered_launch_work_j']/3.6e6:.3f} | {L['grid_traction_energy_j']/3.6e6:.3f} | {jerk} | ${price/1e6:.3f}m |")
    return f'''# Stateful station capture and relaunch

[Open the comparison](index.html) · [Original station-pair methods](../station-pair/README.md)

**Calculated research experiment.** Both station stores begin empty. Actual
braking work within five capture stages charges the receiving store; only a
later authorized departure from that station can use it. Capture/release losses,
leakage, finite force/power/window limits, locks, reset costs and failures are
explicit. Full or failed capture bypasses to the existing independent brakes
under an **ideal coordinated blending assumption**, without increasing their
total capability. Real spring force–stroke and hydraulic pressure–flow remain
unverified. Recovered force replaces part of the requested grid-driven launch;
it does not invent additional motor ratings or a successful journey.

## Same route, explicit hardware, retained failures

All designs use the 1.5 km two-station double-track pilot and exact 605-type body
catalogue. New vehicle-interface reserves add 300/600/1,200 kg per train, with
separate cost lines. Spring/accumulator bank mass is calculated from the declared
material/gas-work hypotheses; housing, transmissions, supports, guards, controls
and installation remain positive reserves. Hardware revisions get new candidate
IDs; faults and control hypotheses remain separate evaluations.

Eight nominal alternating movements carry the actual reversed stopping offset,
station energies and clocks. The single point-train departs every 260 s, hence
**520 s per direction**. This demonstrates only a serial storage-cycle model.
It does **not** establish the requested 200 s concurrent four-train service,
platform/crossover conflicts, real turnback or thermal duty. A restricted serial
model is not proof that the physical architecture cannot meet that service.
Complete annual energy and lifecycle NPV remain unknown; known account subtotals
are published. No city is repriced and propulsion remains unselected.

| Design / experiment | Berths | Captured kWh | Relaunched kWh | Grid traction kWh | Max moving jerk m/s³ | Expanded pilot base CAPEX |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(lines)+f'''

Arrival alone is not an advisory-screen pass: the 0.5 m/s³ moving-jerk target,
journey time and uncertainty domain remain separate checks. The
[requirement context](requirement-assessments.json) retains mandatory physical
obligations as open. The summary's next-experiment Pareto set uses nominal serial
cost/energy/jerk only, never fault outcomes or an automatic baseline selection.

These energy totals cover the modeled sequence, not annual savings. Grid traction
is separate from module reset, auxiliary charging and ordinary cable return.
Retained energy at the end is not delivered propulsion. Initially-full sensitivity
cases explicitly debit their initial energy; it is never called regeneration.
All common eighteen fault/environment recipes are retained for every physical
design. Recovery designs also test failed capture/release/reset, delayed reset,
leakage, transfer-power sensitivity, initial storage and authorization refusal.

## One fourteen-scope cost ledger

Original pilot accounts are assigned once. Active/reserve fleet are partitions,
not duplicate train purchases. Extra module material/process and equipment rows
carry the same candidate ID. Land/utilities, rescue, reliability, omitted station/
depot maintenance, component renewals with parent-age resets and disposal have
explicit scenarios. Financing, taxes, customs and FX remain separate excluded
project-finance layers. Low/base/high are assumptions, not quotations or confidence
quantiles. A missing or unsupported service-energy result is unknown, not zero.

The [disabled delivery draft](delivery-draft.json.gz) identifies material reserves,
assembly steps, prototype tests and all fourteen cost scopes. It is not a controlled
drawing package, purchase order, manufacture authorization or safety approval.

## Reproduce

```bash
./osr design station-cycle plan
./osr design station-cycle run --output /path/to/private/cycle-run
./osr design station-cycle publish --run /path/to/private/cycle-run --output /path/to/fresh/publication
./osr design station-cycle verify
./osr design station-cycle verify --replay --state /path/to/private/cycle-replay
./osr design station-cycle history-verify
```

The [prior feedback packet](../../archives/station-pair-feedback-20261107/README.md)
is preserved at its exact Git/source epoch. Verification reconstructs current
requests, physical identities, costs and generated files. Native replay rebuilds
the pinned Rust protocol under CPU/address-space/wall limits, retaining failures.
Source read-only instructions are not an OS sandbox.

Study `{study['study_id']}`. Outline experiment and accounting records are complete
under assumptions. Installed design, concurrent service, measured mechanisms,
physical acceptance and manufacturing/operating release remain open.
'''


def artifacts(study,root=ROOT):
    value={'summary.json':encoded(summary(study)),'study.json.gz':gzip.compress(encoded(study),mtime=0),
        'delivery-draft.json.gz':gzip.compress(encoded(delivery(study)),mtime=0),'README.md':readme(study).encode(),
        'requirement-assessments.json':encoded(requirements(study))}
    for name in ('index.html','app.js','app.css'):value[name]=(Path(root)/'engineering/station_cycle/web'/name).read_bytes()
    return value


def publish(run,*,root=ROOT,output=None):
    root=Path(root);run=Path(run);output=root/OUTPUT if output is None else Path(output)
    if output.exists():raise ValueError('Fresh publication directory required')
    m=json.loads((run/'manifest.json').read_bytes());sealed(m,'manifest_id')
    if any(digest(run/n)!=sha for n,sha in m['files_sha256'].items()):raise ValueError('Cycle run files changed')
    study=json.loads(gzip.decompress((run/'result.json.gz').read_bytes()));sealed(study,'study_id')
    if study['source_sha256']!=coordinator.sources(root) or m['study_id']!=study['study_id']:raise ValueError('Cycle run source differs')
    output.mkdir(parents=True)
    for n,raw in artifacts(study,root).items():(output/n).write_bytes(raw)
    manifest=dict(schema='osr-station-cycle-publication/1',study_id=study['study_id'],source_sha256=coordinator.sources(root),
        files_sha256={n:digest(output/n) for n in artifacts(study,root)},**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest))
    return verify(root=root,output=output)


def verify(*,root=ROOT,output=None,replay=False,state=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if any(p.is_symlink() for p in (output,*output.parents)) or any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('Ordinary cycle evidence files required')
    m=json.loads((output/'manifest.json').read_bytes());sealed(m,'manifest_id')
    inventory={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if m['source_sha256']!=coordinator.sources(root) or inventory!=m['files_sha256']:raise ValueError('Cycle source or artifact changed')
    study=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()));sealed(study,'study_id')
    if study['study_id']!=m['study_id'] or study['source_sha256']!=m['source_sha256'] or study['parent']!=history.verify(root):
        raise ValueError('Cycle study, source or parent differs')
    for value in (m,study):
        if any(value.get(k) is not x for k,x in FLAGS.items()):raise ValueError('Cycle research cannot grant release')
    if study['integrated_selection'] is not None or study['available_operating_maps_added'] or study['priced_city_models_replaced']:
        raise ValueError('Cycle experiment cannot adopt or reprice a baseline')
    brief,bundle,mass,p,expected=coordinator.requests(root)
    if study['brief']!=brief or study['policy']!=p or len(expected)!=len(study['records']):raise ValueError('Cycle inputs differ')
    baselines={r['candidate_id']:r for r in study['baseline_journeys']}
    qs=study['baseline_requests']
    if len(qs)!=len(baselines):raise ValueError('Baseline journey inventory differs')
    designs={m['design']['variant']['candidate_id']:m['design'] for m in expected}
    if set(baselines)!=set(designs):raise ValueError('Baseline physical inventory differs')
    for q in qs:
        d=designs[q['candidate_id']]
        want=coordinator.pair.case_for(d['variant'],bundle,mass,brief,speed_km_h=d['speed_cap_km_h'],control_mode='feedback',root=root)
        if q!=want:raise ValueError('Baseline request differs from declared hardware/brief')
        r=baselines[q['candidate_id']];sealed(r)
        if r['native_input_id']!=identity(q) or r['id']!=q['id']:raise ValueError('Baseline native request differs')
    costs={}
    for meta,record in zip(expected,study['records']):
        r=record['result'];sealed(r)
        if (record['design']!=meta['design'] or record['request']!=meta['request']
            or record['experiment']!=meta['experiment'] or record['nominal']!=meta['nominal']
            or record['storage_enabled']!=meta['storage_enabled'] or r['native_input_id']!=identity(meta['request'])
            or r['candidate_id']!=meta['design']['variant']['candidate_id'] or r['id']!=meta['request']['id']):
            raise ValueError('Mixed cycle request, hardware or result')
        if any(r.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
            raise ValueError('Cycle result cannot establish acceptance')
        L=r['ledger'];scale=max(1.,L['capture_work_j'],L['grid_traction_energy_j'],L['initial_store_j'])
        balance=L['initial_store_j']+L['stored_capture_j']-L['released_from_store_j']-L['storage_leakage_j']-L['final_store_j']
        if abs(balance)>1e-6*scale or abs(L['storage_balance_residual_j'])>1e-6*scale or abs(L['train_and_storage_balance_residual_j'])>1e-6*scale:
            raise ValueError('Cycle energy ledger does not close')
        previous=None
        for leg in r['legs']:
            j=leg['journey']
            if previous is not None and not isclose(leg['initial_position_m'],1500-previous['final_position_m'],abs_tol=1e-7):
                raise ValueError('Cycle position was reset between movements')
            if j is not None:
                if j['candidate_id']!=r['candidate_id']:raise ValueError('Mixed point-train identity')
                if j['control']['end_of_authority_violated'] and j['normal_numerical_arrival']:raise ValueError('Overrun cannot be an arrival')
                previous=j
        cid=r['candidate_id']
        if cid not in costs:
            if meta['experiment']!='nominal':raise ValueError('Financial scenario requires its declared nominal case first')
            costs[cid]=coordinator.evaluate_cost(meta,r,baselines[cid],brief,bundle,mass,p,root=root)
        cost=costs[cid]
        if record['cost']!=cost or record['row']!=coordinator.row(meta,r,cost,p,brief):raise ValueError('Cycle cost or presentation differs')
    if study.get('financial_evaluations')!=len(costs):raise ValueError('Financial dependency reuse count differs')
    for name,raw in artifacts(study,root).items():
        if (output/name).read_bytes()!=raw:raise ValueError('Generated cycle file differs: '+name)
    count=0
    if replay:
        if state is None:raise ValueError('Private replay directory required')
        actual=native_bridge.execute([x['request'] for x in expected],Path(state),root=root)
        for a,b in zip(actual,[x['result'] for x in study['records']]):
            remove=('native_receipt_id','evaluation_id')
            if not _near({k:v for k,v in a.items() if k not in remove},{k:v for k,v in b.items() if k not in remove}):raise ValueError('Cycle native replay differs')
        ordinary=journey_bridge.execute(qs,Path(state),root=root)
        for a,b in zip(ordinary,study['baseline_journeys']):
            remove=('native_receipt_id','evaluation_id')
            if not _near({k:v for k,v in a.items() if k not in remove},{k:v for k,v in b.items() if k not in remove}):raise ValueError('Ordinary baseline replay differs')
        count=len(actual)
    return dict(verified=True,study_id=study['study_id'],normal_cases=sum(r['nominal'] for r in study['records']),
        fault_cases=sum(not r['nominal'] for r in study['records']),native_replayed_cases=count,concurrent_service_verified=False,**FLAGS)
