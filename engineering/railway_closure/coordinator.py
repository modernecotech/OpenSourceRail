"""Reproducible body → axle → civil → service → fleet → cost research packet."""
from pathlib import Path
from copy import deepcopy
from math import fsum
import gzip,json,time,resource,subprocess
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


def run(output,*,root=ROOT,with_recovery=True,reuse_native=None,bogie_detail=False):
    from engineering.vehicle_installation import underframe
    root=Path(root).resolve();out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    before=sources(root);start=time.monotonic();timings={};p=service.brief(root)
    reuse_groups={};origin_manifest_id=None;origin_manifest_files=None
    if reuse_native is not None:
        from engineering.station_pair import native_bridge as bridge
        origin=Path(reuse_native).resolve()
        manifest_path=origin.parent/'manifest.json'
        if manifest_path.is_file() and not manifest_path.is_symlink():
            origin_manifest=json.loads(manifest_path.read_bytes())
            if origin_manifest.get('manifest_id')!=identity(
                    {k:v for k,v in origin_manifest.items() if k!='manifest_id'}):
                raise ValueError('Native cache source publication manifest is not sealed')
            origin_manifest_id=origin_manifest['manifest_id']
            origin_manifest_files=origin_manifest.get('files_sha256')
            if not isinstance(origin_manifest_files,dict):
                raise ValueError('Native cache source publication lacks its file inventory')
        tools={name:subprocess.check_output([name,'--version'],text=True).strip() for name in ('cargo','rustc')}
        for group,build_name,runs_name,product,protocol in (
                ('serial','cycle-build.json','native-runs','osr-station-cycle','osr-station-cycle-request/1'),
                ('fleet','fleet-build.json','fleet-runs','osr-station-fleet','osr-station-fleet-request/1')):
            source=origin/group;build_path=source/build_name
            if (source.is_symlink() or not source.is_dir() or build_path.is_symlink()
                    or not build_path.is_file()):
                raise ValueError('Native cache source must contain ordinary sealed build records')
            previous_build=json.loads(build_path.read_bytes())
            if (previous_build.get('receipt_id')!=identity(
                    {k:v for k,v in previous_build.items() if k!='receipt_id'})
                    or previous_build.get('source_sha256')!=bridge.sources(root)
                    or previous_build.get('tools')!=tools
                    or previous_build.get('product')!=product
                    or previous_build.get('protocol')!=protocol):
                raise ValueError('Reuse requires exact ordinary native source/tool/product state; request a fresh run')
            if origin_manifest_files is not None:
                prefix=f'native/{group}'
                if origin_manifest_files.get(f'{prefix}/{build_name}')!=digest(build_path):
                    raise ValueError('Native cache build differs from its source publication manifest')
            source_runs=source/runs_name
            if source_runs.is_symlink() or not source_runs.is_dir():
                raise ValueError('Native cache source run directory must be ordinary')
            reuse_groups[group]=dict(source_runs=source_runs,previous_build=previous_build,
                manifest_files=origin_manifest_files,
                manifest_prefix=f'native/{group}',
                origin_manifest_id=origin_manifest_id)
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
    serial=cycle_bridge.execute(requests,out/'serial',root=root,
                                 reuse_cache=reuse_groups.get('serial'))
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
    t=time.monotonic();results=fleet_bridge.execute([m['request'] for m in meta],out/'fleet',root=root,
                                                    reuse_cache=reuse_groups.get('fleet'))
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
    used_receipt_ids=used_native_receipts['serial']|used_native_receipts['fleet']
    reused_native_receipts={group:{
        json.loads((path/'receipt.json').read_bytes())['receipt_id']
        for path in (out/group/('native-runs' if group=='serial' else 'fleet-runs')).iterdir()
        if json.loads((path/'receipt.json').read_bytes()).get('cache_reuse') is not None}
        for group in ('serial','fleet')}
    reused_receipt_ids=reused_native_receipts['serial']|reused_native_receipts['fleet']
    usage=dict(wall_s=time.monotonic()-start,phase_wall_s=timings,
               coordinator_peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               source_unchanged=before==after,fleet_requests=len(meta),serial_requests=len(requests),
               native_cache_origin=None if reuse_native is None else str(Path(reuse_native).resolve()),
               native_cache_origin_manifest_id=origin_manifest_id,
               native_cache_batches_reused_by_group={group:len(ids) for group,ids in reused_native_receipts.items()},
               native_batches_used=len(used_receipt_ids),
               unchanged_native_batch_receipts_reused=len(used_receipt_ids & reused_receipt_ids),
               native_batches_executed=len(used_receipt_ids-reused_receipt_ids),
               run_bytes_before_manifest=sum(q.stat().st_size for q in out.rglob('*') if q.is_file()))
    write(out,'usage.json',usage)
    files={q.relative_to(out).as_posix():digest(q) for q in out.rglob('*') if q.is_file()}
    manifest=dict(schema='osr-railway-closure-run/1',study_id=value['study_id'],source_sha256=before,files_sha256=files,**FLAGS)
    manifest['manifest_id']=identity(manifest);write(out,'manifest.json',manifest)
    if before!=after:raise ValueError('Source drift: complete retained run held')
    return dict(study_id=value['study_id'],candidate_id=canonical['candidate_id'],output=str(out),usage=usage,
                nominal_model_passes=sum(r['assessment']['nominal_model_screen'] for r in records if r['experiment']=='nominal'),**FLAGS)
