"""Fixed-service capacity/dispatch comparison; no automatic physical selection."""
from collections import Counter
from pathlib import Path
from math import fsum
import csv,gzip,json,resource,subprocess,time
from engineering.station_rail.common import identity,encoded,digest
from engineering.railway_closure import coordinator,installed,bundle,service,motion,fleet,fleet_bridge,cost
from engineering.vehicle_installation import underframe
from engineering.pilot_civil import design as civil_design
from . import ROOT,FLAGS
from . import configuration

BODY='c89556f453e39448a8f3e9bf2d0d4d008f97cd20d252ac417284e40965e261b3'
TRAVEL_BOUND=190.
BUDGET=dict(maximum_cases=32,departures_per_case=16,maximum_run_bytes=512*1024**2,
            maximum_run_wall_s=900,coordinator_target_peak_rss_KiB=2*1024**2,
            native_batch_cases=2,native_address_space_bytes=1024**3,native_cpu_s=60,native_wall_s=75)


def sources(root=ROOT):
    values=coordinator.sources(root)
    for p in (Path(root)/'engineering/recovery_search').glob('*.py'):
        values[p.relative_to(root).as_posix()]=digest(p)
    return values


def specifications():
    values=[dict(key='no-store',technology=None,capacity_j=0.,release_share=.8,enabled=False)]
    for technology in ('steel','hydraulic'):
        for capacity in (.25,.5,1.,2.,4.):
            for share in (.2,.5,.8):
                values.append(dict(key=f'{technology}-{capacity:g}MJ-share{share:g}',technology=technology,
                                   capacity_j=capacity*1e6,release_share=share,enabled=True))
    values.append(dict(key='hydraulic-4MJ-recovery-disabled',technology='hydraulic',capacity_j=4e6,
                       release_share=.8,enabled=False))
    assert len(values)==BUDGET['maximum_cases']
    return values


def write(out,name,value):
    path=Path(out)/name;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('Immutable artifact exists: '+name)
    raw=value if isinstance(value,bytes) else encoded(value)
    path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)


def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def seal(value,key='evaluation_id'):
    value[key]=identity(value);return value


def assessment(result,plan):
    value=fleet.screen(result,plan)
    journeys=[d['journey'] for d in result['departures'] if d['journey'] is not None]
    value['tests']['common_travel_planning_bound']=bool(journeys) and all(j['elapsed_s']<=TRAVEL_BOUND for j in journeys)
    value['nominal_model_screen']=all(value['tests'].values())
    return value


def residual_occupancy(result,request):
    """Account retained energy; do not invent a bank-emptying mechanism."""
    ledger=result['ledger'];states=result['station_states'];reasons=Counter()
    for d in result['departures']:reasons.update(d['recovery_reasons'])
    return dict(initial_store_j=ledger['initial_store_j'],final_store_j=ledger['final_store_j'],
        total_capacity_j=fsum(s['store']['capacity_j'] for s in request['stations']),
        stored_capture_j=ledger['stored_capture_j'],released_from_store_j=ledger['released_from_store_j'],
        storage_leakage_j=ledger['storage_leakage_j'],station_states=states,
        capture_bypassed_departures=sum(d['capture_bypassed'] for d in result['departures']),
        release_bypassed_departures=sum(d['release_bypassed'] for d in result['departures']),
        recovery_reasons=dict(reasons),unspent_energy_credit_j=0.,free_dump_or_reset_to_empty=False,
        next_experiment='Rank controlled residual-bank discharge/dispatch or smaller interfaces only after explicit mechanism, losses, reset, duty and cost modelling; not admitted here')


def row(record,physical):
    r=record['result'];ledger=r['ledger'];method=record['cost']['full_scope']['methods'][0]
    installed_value=physical['installed'];design=installed_value['recovery_design']
    normal=next(x for x in installed_value['load_cases'] if x['name']=='normal-base')
    return dict(**record['specification'],candidate_id=physical['bundle']['candidate_id'],
        body_candidate_id=installed_value['vehicle_candidate_id'],installed_mass_evaluation_id=installed_value['evaluation_id'],
        service_evaluation_id=physical['service']['evaluation_id'],native_evaluation_id=r['evaluation_id'],
        normal_mass_kg=normal['train_mass_kg'],normal_arrivals=r['normal_arrivals'],
        model_screen=record['assessment']['nominal_model_screen'],
        failed_screens=','.join(k for k,v in record['assessment']['tests'].items() if not v),
        traction_grid_kwh=ledger['grid_traction_energy_j']/3.6e6,reset_grid_kwh=ledger['reset_grid_energy_j']/3.6e6,
        captured_MJ=ledger['capture_work_j']/1e6,released_store_MJ=ledger['released_from_store_j']/1e6,
        final_store_MJ=ledger['final_store_j']/1e6,
        bank_loss_heat_MJ=(ledger['capture_loss_j']+ledger['release_loss_j']+ledger['storage_leakage_j']+ledger['reset_grid_energy_j'])/1e6,
        annual_grid_kwh_base=None if record['energy'] is None else record['energy']['annual_grid_kwh']['base'],
        installed_capital_usd_base=method['installed_capital_usd']['base'],
        whole_life_NPV_usd_base=method['whole_life_NPV_usd']['base'],
        active_stock_kg_each=0. if design['sizing'] is None else design['sizing']['active_mass_kg'],
        envelope_m3_each=0. if design['sizing'] is None else design['sizing']['reserve_envelope_m3'],
        energy_hold=record['energy_hold'],packaging_hold=installed_value['packaging_screen'],
        physical_accepted=False,selected_reference_changed=False)


def pareto(rows):
    """Economic alternatives only, conditioned on the complete common model screen."""
    eligible=[r for r in rows if r['model_screen'] and r['whole_life_NPV_usd_base'] is not None]
    fields=('installed_capital_usd_base','whole_life_NPV_usd_base','annual_grid_kwh_base')
    return [r['key'] for r in eligible if not any(
        all(q[f]<=r[f] for f in fields) and any(q[f]<r[f] for f in fields)
        for q in eligible if q is not r)]


def report(study):
    lines=['# Fixed-service station recovery economics','',
        'Calculated research comparison; powered-bogie packaging and physical force/duty evidence remain held. No installed selection or passenger-operation approval.',
        '',f"Study `{study['evaluation_id']}`; source `{study['source_commit']}`.",
        f"Exact body `{study['body_candidate_id']}`; {study['physical_cases']} physical variants / {study['numerical_cases']} evaluations.",
        '', 'All cases retain 276 normal places, 85% planning occupancy, 4,000 pphpd demand, 200 s headway, 90 s opposing phase, 3 active + 1 spare trains, 35 s dwell, 45 s turnback and counted full-tail terminal geometry. Nominal grade is zero. All stores start empty. Hardware windows, five capture stages, force/power ceilings, grid equipment, independent brakes, service batteries and charging provision remain counted.',
        '', '| Case | Arrivals | Model screen | Grid traction kWh / 16 | Annual grid MWh | Base capital $m | 30-year NPV $m |',
        '|---|---:|---|---:|---:|---:|---:|']
    for r in study['rows']:
        annual='held' if r['annual_grid_kwh_base'] is None else f"{r['annual_grid_kwh_base']/1000:.2f}"
        npv='held' if r['whole_life_NPV_usd_base'] is None else f"{r['whole_life_NPV_usd_base']/1e6:.4f}"
        lines.append(f"| {r['key']} | {r['normal_arrivals']}/16 | {'pass' if r['model_screen'] else r['failed_screens']} | {r['traction_grid_kwh']:.5f} | {annual} | {r['installed_capital_usd_base']/1e6:.4f} | {npv} |")
    lines.extend(['','Economic Pareto alternatives: '+', '.join(study['pareto_economic_alternatives'])+'.',
        '', 'The disabled hydraulic 4 MJ case has identical hardware and mass to its enabled counterpart. The no-store control removes the interface kit and station packages and therefore has a different physical identity. Residual bank energy is retained, with no invented dump or credit. Station standby, cooling, reset, losses, interface mass, stock, renewals and all fourteen lifecycle scopes remain included.',
        '', 'These prices are calculated low/base/high outline assumptions. Supplier/site prices, equipment duty, availability and lifetimes are not verified. Complete per-case accounts, request/result identities, retained failures and native resource receipts are in this package.',
        '', 'Commands: `python -m engineering.recovery_search plan`; `python -m engineering.recovery_search run --output <new-private-directory>`; `python -m engineering.recovery_search verify --output <directory>`. Verification checks recorded integrity and derivations; it does not independently rerun physical solvers.',''])
    return '\n'.join(lines).encode()


def run(output,*,root=ROOT):
    root=Path(root).resolve();out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    before=sources(root);started=time.monotonic();timings={}
    command=['python','-m','engineering.recovery_search','run','--output',str(out)]
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    write(out,'contract.json',dict(schema='osr-recovery-economics-contract/1',budget=BUDGET,
        command=command,source_commit=commit,specifications=specifications(),
        fixed_service=dict(route_m=1500.,tracks=2,stations=2,boarding_faces=4,normal_places=276,
            planning_occupancy=.85,demand_pphpd=4000.,headway_s=200.,opposite_phase_s=90.,active=3,reserve=1,
            dwell_s=35.,turnaround_s=45.,travel_planning_upper_s=TRAVEL_BOUND,nominal_grade_fraction=0.),
        control=dict(force_slew_n_s=10000.,reserve_factor=2.,mode='grid-substitution-slew/2'),
        purpose='Economic comparison and next-experiment ranking only; no integrated physical selection',**FLAGS))
    write(out,'source-before.json',before)
    t=time.monotonic();p=service.brief(root)
    body=underframe.build(underframe.load_parent(root/coordinator.PARENT),family_id=p['underframe_family_id'])
    if body['candidate_id']!=BODY:raise ValueError('Exact parent body control changed')
    write(out,'body.json.gz',body);timings['body_s']=time.monotonic()-t
    context=configuration.prepare(root);motion_context=motion.prepare(root)
    physical={};meta=[];t=time.monotonic()
    for spec in specifications():
        physical_key=f"{spec['technology'] or 'none'}-{spec['capacity_j']:g}"
        if physical_key not in physical:
            d=configuration.build(spec['technology'],spec['capacity_j'],root=root,prepared=context)
            i=installed.integrate(body,with_recovery=spec['technology'] is not None,recovery_design=d,root=root)
            axles=installed.axle_packet(i)
            civil=civil_design.evaluate(axles,family='folded_plate',revision='thick-web',soil_case='base',root=root,upstream_root=root)
            canonical=bundle.combine(i,civil)
            s=service.plan(canonical['candidate_id'],dict(A=TRAVEL_BOUND,B=TRAVEL_BOUND),p,
                           headway_s=200.,phase_b_s=90.,active_trainsets=3)
            value=dict(installed=i,axle_loads=axles,civil=civil,bundle=canonical,service=s,
                native_civil=dict(state='not requested',reason='Cost-only common civil calculation; source/candidate-bound FEM must be checked separately',inherited_proof=False),**FLAGS)
            physical[physical_key]=value;write(out,'physical/'+physical_key+'.json.gz',value)
        value=physical[physical_key]
        request=fleet.request(value['installed'],value['bundle'],value['service'],enabled=spec['enabled'],
            experiment='nominal' if spec['enabled'] else 'recovery-disabled',dt=.05,
            prepared=motion_context,root=root,release_control=configuration.release_control(spec['release_share']))
        if len(request['departures'])!=16:raise ValueError('Fixed 16-departure contract changed')
        if any(s['initial_energy_j']!=0 for s in request['stations']):raise ValueError('No free initial bank energy')
        meta.append(dict(specification=spec,physical_key=physical_key,request=request))
    timings['physical_and_requests_s']=time.monotonic()-t
    write(out,'requests.json.gz',meta)
    t=time.monotonic();results=fleet_bridge.execute([m['request'] for m in meta],out/'native',root=root)
    timings['native_s']=time.monotonic()-t
    records=[];rows=[];t=time.monotonic()
    for m,r in zip(meta,results):
        value=physical[m['physical_key']];s=value['service'];a=assessment(r,s);energy=None;hold=None
        if a['nominal_model_screen']:
            try:energy=fleet.energy(r,m['request'],s,root=root)
            except fleet.EnergyDomainHold as exc:hold=str(exc)
        else:hold='Common-service model screen failed: '+','.join(k for k,v in a['tests'].items() if not v)
        ledger=cost.evaluate(body,value['installed'],value['civil'],s,energy=energy,root=root)
        record=seal(dict(schema='osr-recovery-economics-case/1',**m,result=r,assessment=a,energy=energy,
            energy_hold=hold,cost=ledger,residual_occupancy=residual_occupancy(r,m['request']),**FLAGS))
        rows.append(row(record,value));records.append(record)
        write(out,'cases/'+m['specification']['key']+'.json.gz',record)
    timings['cost_s']=time.monotonic()-t
    control=rows[0]
    for r in rows:
        r['delta_capital_usd_base_vs_no_store']=r['installed_capital_usd_base']-control['installed_capital_usd_base']
        r['delta_NPV_usd_base_vs_no_store']=None if r['whole_life_NPV_usd_base'] is None or control['whole_life_NPV_usd_base'] is None else r['whole_life_NPV_usd_base']-control['whole_life_NPV_usd_base']
        r['delta_annual_grid_kwh_base_vs_no_store']=None if r['annual_grid_kwh_base'] is None or control['annual_grid_kwh_base'] is None else r['annual_grid_kwh_base']-control['annual_grid_kwh_base']
    study=seal(dict(schema='osr-recovery-economics-study/1',body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],
        case_evaluation_ids=[r['evaluation_id'] for r in records],rows=rows,pareto_economic_alternatives=pareto(rows),
        source_sha256=before,source_commit=commit,physical_cases=len(physical),numerical_cases=len(records),
        integrated_selection=None,prices_verified=False,price_maturity='Calculated low/base/high outline rates; full package counts retained, supplier and site evidence unavailable',
        limitations=['Same parent powered-bogie packaging hold; not a mechanically admissible installed design',
            'Vessel/spring stock sizing and all force-speed-duty/efficiency maps remain unmeasured hypotheses',
            'No additional FEM, CAD, fatigue, certified braking or hot-weather qualification performed',
            'Finite sixteen-departure annualization; residual energy and cold starts are reported, not credited',
            'Common nominal zero grade only; no new fault qualification. Earlier fault evidence is not silently inherited',
            'Finance, taxes, customs and exchange policy remain explicitly excluded project-finance layers'],**FLAGS))
    write(out,'study.json',study)
    write(out,'README.md',report(study))
    with (out/'comparison.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    after=sources(root);write(out,'source-after.json',after)
    usage=dict(wall_s=time.monotonic()-started,phase_wall_s=timings,source_unchanged=before==after,
        coordinator_peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        native_batches=len(list((out/'native/fleet-runs').glob('*/receipt.json'))),
        run_bytes_before_manifest=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()))
    usage['budget_tests']=dict(wall=usage['wall_s']<=BUDGET['maximum_run_wall_s'],
        disk=usage['run_bytes_before_manifest']<=BUDGET['maximum_run_bytes'],
        coordinator_memory_target=usage['coordinator_peak_rss_KiB']<=BUDGET['coordinator_target_peak_rss_KiB'])
    write(out,'usage.json',usage)
    files={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}
    manifest=seal(dict(schema='osr-recovery-economics-run/1',study_id=study['evaluation_id'],source_sha256=before,
        source_commit=commit,files_sha256=files,**FLAGS),'manifest_id')
    write(out,'manifest.json',manifest)
    if before!=after:raise ValueError('Source drift; retained results held')
    if not all(usage['budget_tests'].values()):raise ValueError('Run exceeds declared budget; retained results held')
    return dict(output=str(out),study_id=study['evaluation_id'],manifest_id=manifest['manifest_id'],
        physical_cases=len(physical),numerical_cases=len(records),model_passes=sum(r['model_screen'] for r in rows),
        pareto=study['pareto_economic_alternatives'],usage=usage,**FLAGS)


def verify(output,*,root=ROOT):
    out=Path(output).resolve();manifest=read(out/'manifest.json');study=read(out/'study.json')
    if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Manifest changed')
    if any(p.is_symlink() for p in out.rglob('*')):raise ValueError('Ordinary immutable artifact files required')
    actual={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if actual!=manifest['files_sha256']:raise ValueError('Run artifacts changed')
    if manifest['source_sha256']!=sources(root) or read(out/'source-after.json')!=manifest['source_sha256']:raise ValueError('Source differs')
    if study['evaluation_id']!=manifest['study_id'] or study['evaluation_id']!=identity({k:v for k,v in study.items() if k!='evaluation_id'}):raise ValueError('Study changed')
    receipts={read(p)['receipt_id']:read(p) for p in (out/'native/fleet-runs').glob('*/receipt.json')}
    raw_cases={}
    for path in (out/'native/fleet-runs').glob('*/receipt.json'):
        r=read(path)
        if r['receipt_id']!=identity({k:v for k,v in r.items() if k!='receipt_id'}) or r['input_sha256']!=digest(path.parent/'input.json.gz') or r['output_sha256']!=digest(path.parent/'output.json.gz'):raise ValueError('Native receipt changed')
        qs=read(path.parent/'input.json.gz')['cases'];rs=read(path.parent/'output.json.gz')['cases']
        if len(qs)!=len(rs):raise ValueError('Native recorded shape differs')
        for q,v in zip(qs,rs):raw_cases[(r['receipt_id'],identity(q))]=(q,v)
    records=[read(out/'cases'/f"{s['key']}.json.gz") for s in specifications()]
    physical={}
    reconstructed=[]
    for r in records:
        if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Case changed')
        value=physical.setdefault(r['physical_key'],read(out/'physical'/f"{r['physical_key']}.json.gz"))
        if bundle.combine(value['installed'],value['civil'])!=value['bundle']:raise ValueError('Physical bundle changed')
        result=r['result'];request=r['request'];receipt=receipts[result['native_receipt_id']]
        if result['native_input_id']!=identity(request) or request['candidate_id']!=value['bundle']['candidate_id']:raise ValueError('Native candidate/input differs')
        q,raw=raw_cases[(result['native_receipt_id'],result['native_input_id'])]
        if q!=request or raw!={k:v for k,v in result.items() if k not in ('evaluation_id','native_receipt_id','native_input_id')}:raise ValueError('Native result not from exact receipt')
        if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Native annotated result changed')
        if assessment(result,value['service'])!=r['assessment'] or residual_occupancy(result,request)!=r['residual_occupancy']:raise ValueError('Derived assessment differs')
        full=r['cost']['full_scope']
        if full['evaluation_id']!=identity({k:v for k,v in full.items() if k!='evaluation_id'}) or len(full['required_cost_scopes'])!=14:raise ValueError('Cost ledger/scopes differ')
        if full['candidate_id']!=value['bundle']['candidate_id'] or full['mass_evaluation_id']!=value['installed']['evaluation_id']:raise ValueError('Cost candidate differs')
        reconstructed.append(row(r,value))
    # Comparative deltas are checked against their own exact no-store control.
    for a,b in zip(reconstructed,study['rows']):
        for k,v in a.items():
            if b[k]!=v:raise ValueError('Comparison row differs: '+k)
        c=study['rows'][0]
        for field,delta in [('installed_capital_usd_base','delta_capital_usd_base_vs_no_store'),('whole_life_NPV_usd_base','delta_NPV_usd_base_vs_no_store'),('annual_grid_kwh_base','delta_annual_grid_kwh_base_vs_no_store')]:
            expected=None if b[field] is None or c[field] is None else b[field]-c[field]
            if b[delta]!=expected:raise ValueError('Comparative delta differs')
    if study['pareto_economic_alternatives']!=pareto(study['rows']):raise ValueError('Economic frontier differs')
    if study['case_evaluation_ids']!=[r['evaluation_id'] for r in records]:raise ValueError('Case identities differ')
    return dict(study_id=study['evaluation_id'],manifest_id=manifest['manifest_id'],cases=len(records),verified=True,**FLAGS)
