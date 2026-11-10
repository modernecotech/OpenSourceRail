"""Reproducible body → axle → civil → service → fleet → cost research packet."""
from pathlib import Path
from copy import deepcopy
from math import fsum
import gzip,json,time,resource,subprocess,shutil
from engineering.station_rail.common import identity,encoded,digest
from engineering.station_cycle import native_bridge as cycle_bridge
from engineering.vehicle_installation import export
from engineering.pilot_civil import design as civil_design
from engineering.pilot_civil import assembly as civil_assembly,render as civil_render
from engineering.station_pair import coordinator as pair
from . import ROOT,FLAGS
from . import installed as installation,service,motion,bundle,fleet,fleet_bridge,cost,electrical,civil_reference

PARENT='engineering/railway_closure/data/frozen-installed-parent.json.gz'


def sources(root=ROOT):
    root=Path(root)
    value=pair.source_hashes(root)
    name='engineering/station_pair/native_products.py';value[name]=digest(root/name)
    for folder in ('engineering/railway_closure','engineering/vehicle_installation','engineering/pilot_civil','engineering/station_cycle','engineering/powered_bogie','engineering/recovery_search','engineering/pilot_delivery'):
        for p in (root/folder).rglob('*'):
            if p.is_file() and p.suffix in ('.py','.json','.gz','.html','.css','.js'):
                value[p.relative_to(root).as_posix()]=digest(p)
    value.update(civil_design.sources(root))
    return value


def write(folder,name,value):
    p=Path(folder)/name
    if p.exists():raise ValueError('Immutable run artifact already exists: '+name)
    raw=value if isinstance(value,bytes) else encoded(value)
    p.write_bytes(raw)


def _prune_unreferenced_native_reuse(output, copied_runs, used_receipt_ids):
    """Keep only copied native batches referenced by this study.

    The source publication remains untouched. Incompatible or unreferenced
    copies are not evidence for the new run and must not be included in its
    publication manifest.
    """
    discarded={'batches':0,'allocated_bytes':0,'by_group':{}}
    for group,build_name,runs_name in (
            ('serial','cycle-build.json','native-runs'),
            ('fleet','fleet-build.json','fleet-runs')):
        run_root=Path(output)/group/runs_name
        paths=copied_runs.get(group,set())
        if not paths:continue
        build=json.loads((Path(output)/group/build_name).read_bytes())
        build_id=build.get('receipt_id')
        if build_id!=identity({k:v for k,v in build.items() if k!='receipt_id'}):
            raise ValueError('Current native build identity differs during cache reconciliation')
        for path in sorted(paths):
            path=Path(path)
            if path.parent!=run_root:raise ValueError('Copied native cache escaped its run directory')
            if path.is_symlink():raise ValueError('Copied native cache cannot be a symlink')
            if not path.exists():continue
            if not path.is_dir() or not path.resolve().is_relative_to(run_root.resolve()):
                raise ValueError('Copied native cache must remain an ordinary in-run directory')
            receipt_path=path/'receipt.json'
            if receipt_path.is_symlink():raise ValueError('Copied native receipt cannot be a symlink')
            receipt_id=None
            if receipt_path.is_file():
                receipt=json.loads(receipt_path.read_bytes())
                if receipt.get('receipt_id')==identity(
                        {k:v for k,v in receipt.items() if k!='receipt_id'}):
                    receipt_id=receipt['receipt_id']
            if receipt_id in used_receipt_ids.get(group,set()):
                receipt=json.loads(receipt_path.read_bytes())
                if receipt.get('build_receipt_id')!=build_id:
                    raise ValueError('Referenced native cache belongs to a different build')
                continue
            entries=list(path.rglob('*'))
            if any(entry.is_symlink() for entry in entries):
                raise ValueError('Copied native cache contains a symlink')
            allocated=sum((entry.stat().st_blocks*512) or entry.stat().st_size
                          for entry in entries if entry.is_file())
            shutil.rmtree(path)
            discarded['batches']+=1;discarded['allocated_bytes']+=allocated
            group_result=discarded['by_group'].setdefault(
                group,{'batches':0,'allocated_bytes':0})
            group_result['batches']+=1;group_result['allocated_bytes']+=allocated
    return discarded


def run(output,*,root=ROOT,with_recovery=True,reuse_native=None,bogie_detail=False):
    from engineering.vehicle_installation import underframe
    root=Path(root).resolve();out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    before=sources(root);start=time.monotonic();timings={};p=service.brief(root)
    copied_native_runs={'serial':set(),'fleet':set()};prior_receipt_ids=set()
    if reuse_native is not None:
        from engineering.station_pair import native_bridge as bridge
        origin=Path(reuse_native).resolve()
        tools={name:subprocess.check_output([name,'--version'],text=True).strip() for name in ('cargo','rustc')}
        for group in ('serial','fleet'):
            source=origin/group;receipt=json.loads((source/'native-build.json').read_bytes())
            if (receipt['receipt_id']!=identity({k:v for k,v in receipt.items() if k!='receipt_id'})
                or receipt['source_sha256']!=bridge.sources(root) or receipt['tools']!=tools
                or any(q.is_symlink() for q in source.rglob('*'))):
                raise ValueError('Reuse requires exact ordinary native source/tool state; request a fresh run')
            # Independent CoW copies preserve old immutable evidence. Native
            # bridges still validate binary, input, resource and output hashes.
            subprocess.run(['cp','--archive','--reflink=auto',str(source),str(out/group)],check=True)
            runs_name='native-runs' if group=='serial' else 'fleet-runs'
            run_root=out/group/runs_name
            if run_root.is_dir():copied_native_runs[group]={q for q in run_root.iterdir() if q.is_dir()}
            prior_receipt_ids.update(json.loads(q.read_bytes())['receipt_id'] for q in (out/group).rglob('receipt.json'))
    write(out,'source-before.json',before)
    prepared=motion.prepare(root)
    parent=underframe.load_parent(root/PARENT)
    t=time.monotonic();body=underframe.build(parent,family_id=p['underframe_family_id'])
    if bogie_detail:
        from engineering.powered_bogie.design import build as revise_bogie
        body=revise_bogie(body,root=root)
    timings['body_s']=time.monotonic()-t
    export.write(body,out/'vehicle')
    i=installation.integrate(body,with_recovery=with_recovery,root=root);axles=installation.axle_packet(i)
    if bogie_detail:
        from engineering.powered_bogie.geometry import evaluate as bogie_geometry
        write(out,'powered-bogie-geometry.json',bogie_geometry(body))
    write(out,'installed.json',i);write(out,'axle-loads.json',axles)
    t=time.monotonic();civil=civil_design.evaluate_portfolio(axles,root=root,upstream_root=root)
    timings['civil_s']=time.monotonic()-t
    write(out,'civil-portfolio.json',civil)
    eligible=[c for c in civil if c['advisory_screen_passed'] and c['foundation']['soil_case']=='base']
    # An unsuccessful candidate still receives its complete calculated packet.
    leading=min(eligible or [c for c in civil if c['foundation']['soil_case']=='base'],
                key=lambda c:c['cost']['scoped_installed_usd']['base'])
    canonical=bundle.combine(i,leading)
    write(out,'bundle.json',canonical);write(out,'civil.json',leading)
    civil_native=civil_reference.applicable(leading,axles,root=root)
    write(out,'civil-native-reference.json',civil_native)
    write(out,'civil-assembly.json',civil_assembly.scene(leading))
    write(out,'civil-assembly.svg',civil_render.svg(leading).encode())
    t=time.monotonic()
    requests=[motion.controlled_cycle(i,candidate_bundle=canonical,count=4,dt=dt,enabled=enabled,prepared=prepared,root=root)
              for dt in (.05,.025,.0125) for enabled in (False,True)]
    serial=cycle_bridge.execute(requests,out/'serial',root=root)
    timings['serial_s']=time.monotonic()-t
    write(out,'serial-requests.json',requests)
    write(out,'serial-results.json.gz',gzip.compress(encoded(serial),mtime=0))
    durations=[l['journey']['elapsed_s'] for row in serial for l in row['legs'] if l['journey'] is not None]
    upper=max(durations) if durations else p['maximum_pair_journey_s']
    plans=service.explore(canonical['candidate_id'],{'A':upper,'B':upper},root=root)
    feasible=[s for s in plans if s['planned_service_complete']]
    if not feasible:
        feasible=[min(plans,key=lambda s:sum(not x for x in s['tests'].values()))]
    # Preserve several demand/headway alternatives and one extra-train control.
    choices=[]
    for h in (180.,200.,210.):
        candidates=[s for s in feasible if s['headway_s']==h]
        if candidates:choices.append(min(candidates,key=lambda s:(s['total_trainsets'],abs(s['opposite_phase_s']-90.))))
    if not choices:choices=[feasible[0]]
    # Explicit phase alternatives expose shared-store conflicts and counted
    # readiness margins rather than making90s a hidden operating default.
    for s in feasible:
        wanted=(s['headway_s']==210. and s['active_trainsets']==3 and s['opposite_phase_s']==60.)
        wanted|=(s['active_trainsets']==4 and s['headway_s'] in (200.,210.) and s['opposite_phase_s']==0.)
        wanted|=(s['active_trainsets']==4 and s['headway_s']==210. and s['opposite_phase_s']==90.)
        if wanted and s['evaluation_id'] not in {x['evaluation_id'] for x in choices}:choices.append(s)
    write(out,'service-plans.json',plans)
    meta=[]
    def add(s,experiment='nominal',enabled=True,dt=.05):
        meta.append(dict(service=s,experiment=experiment,enabled=enabled,dt_s=dt,
                         request=fleet.request(i,canonical,s,enabled=enabled,experiment=experiment,dt=dt,prepared=prepared,root=root)))
    for s in choices:
        add(s)
        if with_recovery:add(s,experiment='recovery-disabled',enabled=False)
    preferred=min(choices,key=lambda s:(s['total_trainsets'],-s['headway_s']))
    for dt in (.025,.0125):add(preferred,'timestep',dt=dt)
    for experiment in ('wet','power-loss','half-drive','emergency-stop','high-mass','low-mass',
                       'half-drive-unobserved','high-mass-low-force','down-2pct','headwind',
                       'compound-downhill-boundary','outside-brake-bound','outside-grade-bound',
                       'tailwind-unsupported','outside-position-bound','outside-response-bound',
                       'up-2pct','hot-hotel','capture-failed','release-failed','reset-failed',
                       'slow-reset','storage-leakage','initially-full','no-authority'):
        add(preferred,experiment)
    if len(meta)>64:raise ValueError('Declared fleet campaign exceeds64requests')
    write(out,'fleet-requests.json',meta)
    t=time.monotonic();results=fleet_bridge.execute([m['request'] for m in meta],out/'fleet',root=root)
    timings['fleet_s']=time.monotonic()-t
    records=[]
    for m,r in zip(meta,results):
        s=m['service'];assessment=fleet.screen(r,s)
        energy=None;energy_hold=None
        if m['experiment'] in ('nominal','recovery-disabled') and assessment['nominal_model_screen']:
            try:energy=fleet.energy(r,m['request'],s,root=root)
            except fleet.EnergyDomainHold as exc:energy_hold=str(exc)
        ledger=cost.evaluate(body,i,leading,s,energy=energy,root=root)
        records.append(dict(service=s,experiment=m['experiment'],enabled=m['enabled'],dt_s=m['dt_s'],
                            request=m['request'],result=r,assessment=assessment,
                            terminal_calendar=fleet.terminal_check(r,s),energy=energy,energy_hold=energy_hold,cost=ledger))
    t=time.monotonic();battery=[electrical.battery(name,n,root=root) for name in ('Type3-20','Type4-23') for n in (1,2,3)]
    thermal=[]
    ep,_=electrical.load(root)
    for b in battery:
        if b['modules_per_car'] not in (50,75):continue
        heat=b['thermal']['worst_ohmic_heat_W_hypothesis']
        thermal.append(dict(battery_evaluation_id=b['evaluation_id'],module=b['module_name'],modules=b['modules_per_car'],
            result=electrical.controlled_thermal([dict(duration_s=18*3600.,heat_W=heat)],
                initial_C=ep['conditioned_pack_target_C'],ambient_C=ep['external_ambient_C'],
                capacity_J_K=b['module_mass_kg_per_car']*ep['module_heat_capacity_J_kgK_hypothesis'],
                conductance_W_K=b['pod_outer_surface_m2_per_car']*max(ep['insulation_U_W_m2K_cases']),
                cooling_capacity_W=ep['conditioner_cooling_kw_hypothesis']*1000,target_C=ep['conditioned_pack_target_C'])))
    timings['battery_s']=time.monotonic()-t
    value=dict(schema='osr-railway-closure-study/1',bundle=canonical,body_candidate_id=body['candidate_id'],
               body_evaluation_id=body['evaluation_id'],installed=i,civil=leading,
               civil_native_reference=civil_native,
               body_summary={k:body[k] for k in ('source_component_types','proposed_component_types','total_occurrences',
                   'nominal_part_mass_kg','direct_parts_process_usd','mass_scenarios','structural_comparison','interface_screens')},
               civil_alternatives=[dict(candidate_id=c['civil_candidate_id'],evaluation_id=c['evaluation_id'],screens=c['screens'],cost=c['cost']) for c in civil],
               service_plans=plans,records=records,battery_alternatives=battery,battery_thermal_proxies=thermal,
               serial_requests=requests,serial_results=serial,source_sha256=before,
               priced_cities_replaced=False,integrated_selection=None,
               scope='Calculated research outline and disjoint manufacturing/cost records; exact native FEM applicability is reported per candidate and evaluation, without inherited physical qualification.',**FLAGS)
    value['study_id']=identity(value)
    write(out,'study.json.gz',gzip.compress(encoded(value),mtime=0))
    after=sources(root);write(out,'source-after.json',after)
    used_native_receipts={
        'serial':{r['native_receipt_id'] for r in serial},
        'fleet':{r['result']['native_receipt_id'] for r in records},
    }
    discarded_native_cache=_prune_unreferenced_native_reuse(
        out,copied_native_runs,used_native_receipts)
    used_receipt_ids=used_native_receipts['serial']|used_native_receipts['fleet']
    retained_prior_receipts=sum(
        json.loads(q.read_bytes())['receipt_id'] in prior_receipt_ids
        for q in out.rglob('receipt.json'))
    usage=dict(wall_s=time.monotonic()-start,phase_wall_s=timings,
               coordinator_peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               source_unchanged=before==after,fleet_requests=len(meta),serial_requests=len(requests),
               native_cache_origin=None if reuse_native is None else str(Path(reuse_native).resolve()),
               prior_native_batch_receipts_retained=retained_prior_receipts,
               unreferenced_native_cache_batches_discarded=discarded_native_cache['batches'],
               unreferenced_native_cache_allocated_bytes_discarded=discarded_native_cache['allocated_bytes'],
               unreferenced_native_cache_discarded_by_group=discarded_native_cache['by_group'],
               native_batches_used=len(used_receipt_ids),
               unchanged_native_batch_receipts_reused=len(used_receipt_ids & prior_receipt_ids),
               native_batches_executed=len(used_receipt_ids-prior_receipt_ids),
               run_bytes_before_manifest=sum(q.stat().st_size for q in out.rglob('*') if q.is_file()))
    write(out,'usage.json',usage)
    files={q.relative_to(out).as_posix():digest(q) for q in out.rglob('*') if q.is_file()}
    manifest=dict(schema='osr-railway-closure-run/1',study_id=value['study_id'],source_sha256=before,files_sha256=files,**FLAGS)
    manifest['manifest_id']=identity(manifest);write(out,'manifest.json',manifest)
    if before!=after:raise ValueError('Source drift: complete retained run held')
    return dict(study_id=value['study_id'],candidate_id=canonical['candidate_id'],output=str(out),usage=usage,
                nominal_model_passes=sum(r['assessment']['nominal_model_screen'] for r in records if r['experiment']=='nominal'),**FLAGS)
