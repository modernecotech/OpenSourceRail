"""Portable integrity and independently recomputed motor refinement diagnostics.

Recorded execution integrity is distinct from fresh native replay, an approved
convergence screen, physical correlation or operating-map admission.
"""
from pathlib import Path
from math import fsum, sqrt, isfinite
import gzip
import io
import json
import tarfile
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from . import motor_refinement as motor

PRODUCER='engineering/reference_cell/native_evidence.py'
MANIFEST='native-motor-refinement-manifest.json'
ARCHIVE='native-motor-refinement.tar.gz'
KINDS=('coarse','fine')
FILES={'input.json','input-sources.tar.gz','preflight.json','partial-trace.jsonl',
       'worker-result.json','stdout.log','stderr.log','result.json','manifest.json'}
MAX_BYTES=256*1024**2
FLAGS=dict(motor.FLAGS)


def _parse(raw):
    def distinct(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError('Duplicate JSON key')
            value[key]=item
        return value
    def nonfinite(value):raise ValueError('Finite JSON values required')
    return json.loads(raw,object_pairs_hook=distinct,parse_constant=nonfinite)


def sources(root=ROOT):
    source=motor.sources(root);path=Path(root)/PRODUCER
    if digest(path)!=digest(__file__):raise ValueError('Executing publication source differs')
    return dict(sorted({**source,PRODUCER:digest(path)}.items()))


def _ordinary(folder):
    folder=Path(folder)
    if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):
        raise ValueError('Ordinary native evidence directory required')
    return folder


def _read_pair(state,root):
    state=_ordinary(state);rows=[]
    for name in KINDS:
        folder=_ordinary(state/name)
        if {p.name for p in folder.iterdir()}!=FILES or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):
            raise ValueError('Exact ordinary retained native package inventory required')
        if sum(p.stat().st_size for p in folder.iterdir())>MAX_BYTES/2:
            raise ValueError('Bounded retained native package required')
        verified=motor.verify(folder,root=root,require_current_tool=False)
        if verified.get('verified') is not True:raise ValueError('Recorded native integrity not verified')
        request=_parse((folder/'input.json').read_bytes())['request']
        result=_parse((folder/'result.json').read_bytes())
        rows.append((name,request,result,verified))
    return rows


def _relative(a,b):
    numerator=fsum((x-y)**2 for x,y in zip(a,b));denominator=fsum(y*y for y in b)
    return 0. if denominator==0 and numerator==0 else None if denominator==0 else sqrt(numerator/denominator)


def _weighted(rows,dt,start,end):
    """Clip the actual backward-Euler numerical cells to a declared interval."""
    weights=[max(0.,min(r['time_s'],end)-max(r['time_s']-dt,start)) for r in rows]
    duration=fsum(weights)
    if abs(duration-(end-start))>1e-10 or duration<=0:raise ValueError('Weighted interval is not fully covered')
    def integral(key):return fsum(r[key]*w for r,w in zip(rows,weights))
    currents=[r['path_currents_A'] for r in rows];count=len(currents[0])
    if any(len(v)!=count or any(not isfinite(x) for x in v) for v in currents):raise ValueError('Complete finite branch-current traces required')
    magnetic=leakage=0.;old_m=old_l=0.
    for row,w in zip(rows,weights):
        magnetic+=(row['magnetic_energy_J']-old_m)*w/dt
        leakage+=(row['external_leakage_energy_J']-old_l)*w/dt
        old_m=row['magnetic_energy_J'];old_l=row['external_leakage_energy_J']
    terminal=integral('terminal_W');copper=integral('primary_copper_W');secondary=integral('secondary_Joule_W')
    mechanical=integral('mechanical_W');algorithmic=integral('backward_Euler_dissipation_W')
    leakage_numerical=integral('external_leakage_BE_dissipation_W');stabilization=integral('stabilization_work_W')
    balance=terminal-copper-secondary-mechanical-magnetic-leakage-algorithmic-leakage_numerical-stabilization
    reported=integral('discrete_power_residual_W')
    if abs(balance-reported)>1e-7*max(1.,abs(terminal)):raise ValueError('Integrated discrete energy arithmetic differs')
    return dict(start_s=start,end_s=end,duration_s=duration,
        mean_thrust_N=integral('thrust_N')/duration,
        thrust_RMS_N=sqrt(fsum(r['thrust_N']**2*w for r,w in zip(rows,weights))/duration),
        path_RMS_currents_A=[sqrt(fsum(v[j]**2*w for v,w in zip(currents,weights))/duration) for j in range(count)],
        mean_terminal_power_W=terminal/duration,terminal_energy_J=terminal,
        primary_copper_energy_J=copper,secondary_Joule_energy_J=secondary,mechanical_work_J=mechanical,
        weighted_magnetic_storage_increment_J=magnetic,weighted_leakage_storage_increment_J=leakage,
        backward_Euler_numerical_energy_J=algorithmic,leakage_backward_Euler_numerical_energy_J=leakage_numerical,
        stabilization_work_J=stabilization,stabilization_work_is_physical_heat=False,
        recomputed_discrete_energy_residual_J=balance,reported_discrete_energy_residual_J=reported,
        quadrature='Time-weighted right-endpoint backward-Euler cells; clipped storage increments weighted by cell overlap. Not validated physical waveform or thermal duty.')


def assess(state,*,root=ROOT):
    epoch=sources(root);rows=_read_pair(state,root)
    coarse,fine=rows
    drop={'dt_s','steps','maximum_seconds','request_id'}
    common=lambda r:{k:v for k,v in r.items() if k not in drop}
    if common(coarse[1])!=common(fine[1]) or not coarse[1]['dt_s']>fine[1]['dt_s']:
        raise ValueError('Matched physical/mesh/model/electrical request and coarse/fine ordering required')
    horizon=coarse[1]['dt_s']*coarse[1]['steps']
    if abs(horizon-fine[1]['dt_s']*fine[1]['steps'])>1e-12:raise ValueError('Requested horizons differ')
    if coarse[3]['recorded_tool_identity']!=fine[3]['recorded_tool_identity']:
        raise ValueError('Refinement must retain the actual recorded numerical toolchain')
    completed=all(r[2].get('execution')=='completed' and r[2].get('state')=='completed'
        and len(r[2].get('trace',[]))==r[1]['steps'] for r in rows)
    value=dict(schema='osr-recorded-motor-refinement/1',candidate_id=coarse[1]['bundle_id'],
        motor_component_id=coarse[1]['motor_component_id'],body_candidate_id=coarse[1]['body_candidate_id'],
        requested_horizon_s=horizon,time_steps_s=[r[1]['dt_s'] for r in rows],
        evaluations=[r[2]['evaluation_id'] for r in rows],requests=[r[1]['request_id'] for r in rows],
        execution_states=[r[2]['execution'] for r in rows],completed_same_horizon=completed,
        recorded_tool_identity=coarse[3]['recorded_tool_identity'],
        verification_mode='recorded-execution-integrity',current_tool_identity_asserted=False,
        numerical_replayed=False,native_reuse_eligible=False,matched_points=0,
        relative_matched_thrust_RMS_change=None,relative_matched_current_RMS_change=None,
        last_thrust_N=None,full_horizon_statistics=None,tail_cycle_statistics=None,
        approved_convergence_limit=None,numerical_time_convergence='unconfirmed',spatial_convergence='unconfirmed',
        physical_correlation='missing',available_operating_map=None,operating_map_admitted=False,
        new_vehicle_candidate_inheritance_allowed=False,whole_vehicle_candidate_ids_admitted=[],
        source_sha256=epoch,**FLAGS)
    if completed:
        for _,request,result,_ in rows:
            if any(abs(row['time_s']-(i+1)*request['dt_s'])>1e-12 for i,row in enumerate(result['trace'])):
                raise ValueError('Completed trace timestamps differ from the numerical request')
        if coarse[2]['actual_mesh']!=fine[2]['actual_mesh']:raise ValueError('Actual refinement mesh differs')
        fine_by_time={round(row['time_s'],12):row for row in fine[2]['trace']}
        if len(fine_by_time)!=len(fine[2]['trace']):raise ValueError('Duplicate fine trace times')
        pairs=[]
        for row in coarse[2]['trace']:
            key=round(row['time_s'],12)
            if key not in fine_by_time:raise ValueError('Fine trace does not cover every matched coarse time')
            pairs.append((row,fine_by_time[key]))
        tail_start=max(0.,horizon-2/coarse[1]['frequency_Hz'])
        value.update(matched_points=len(pairs),
            relative_matched_thrust_RMS_change=_relative([a['thrust_N'] for a,b in pairs],[b['thrust_N'] for a,b in pairs]),
            relative_matched_current_RMS_change=_relative([x for a,b in pairs for x in a['path_currents_A']],[x for a,b in pairs for x in b['path_currents_A']]),
            last_thrust_N=[r[2]['trace'][-1]['thrust_N'] for r in rows],
            full_horizon_statistics=[_weighted(r[2]['trace'],r[1]['dt_s'],0.,horizon) for r in rows],
            tail_cycle_statistics=[_weighted(r[2]['trace'],r[1]['dt_s'],tail_start,horizon) for r in rows])
    if sources(root)!=epoch:raise ValueError('Publication source changed during assessment')
    value['evaluation_id']=identity(value);return value


def publish(state,output,*,root=ROOT):
    state=_ordinary(state);target=_ordinary(output);value=assess(state,root=root)
    target.mkdir(parents=True,exist_ok=True)
    if (target/ARCHIVE).exists() or (target/MANIFEST).exists():raise ValueError('Fresh immutable native publication required')
    files={};stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for kind in KINDS:
            for name in sorted(FILES):
                p=state/kind/name;relative=kind+'/'+name;raw=p.read_bytes();files[relative]=digest(p)
                item=tarfile.TarInfo(relative);item.size=len(raw);item.mode=0o644;item.mtime=0
                archive.addfile(item,io.BytesIO(raw))
    if len(stream.getvalue())>MAX_BYTES:raise ValueError('Bounded native archive required')
    path=target/ARCHIVE;path.write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    manifest=dict(schema='osr-recorded-motor-refinement-publication/1',archive=ARCHIVE,
        archive_sha256=digest(path),archive_files_sha256=files,source_sha256=sources(root),
        comparison=value,physical_qualification=False,**FLAGS)
    if sources(root)!=value['source_sha256']:raise ValueError('Publication source changed during input retention')
    manifest['publication_id']=identity(manifest);(target/MANIFEST).write_bytes(encoded(manifest))
    verify_publication(target,root=root)
    return manifest


def verify_publication(output,*,root=ROOT):
    target=_ordinary(output)
    for name in (MANIFEST,ARCHIVE):
        if (target/name).is_symlink() or not (target/name).is_file():raise ValueError('Ordinary native publication files required')
    if (target/MANIFEST).stat().st_size>4*1024**2 or (target/ARCHIVE).stat().st_size>MAX_BYTES:raise ValueError('Bounded publication required')
    m=_parse((target/MANIFEST).read_bytes());expected={k+'/'+f for k in KINDS for f in FILES}
    if (m.get('schema')!='osr-recorded-motor-refinement-publication/1'
        or m.get('publication_id')!=identity({k:v for k,v in m.items() if k!='publication_id'})
        or m.get('archive')!=ARCHIVE or m.get('archive_sha256')!=digest(target/ARCHIVE)
        or m.get('source_sha256')!=sources(root) or set(m.get('archive_files_sha256',{}))!=expected
        or m.get('physical_qualification') is not False or any(m.get(k) is not False for k in FLAGS)):
        raise ValueError('Native publication source/payload/identity/disposition differs')
    with tempfile.TemporaryDirectory(prefix='osr-recorded-refinement-') as temporary:
        with gzip.open(target/ARCHIVE,'rb') as compressed:
            raw=compressed.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError('Expanded native archive exceeds its budget')
        with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
            members=[];total=0
            for member in archive:
                members.append(member);total+=member.size
                if len(members)>len(expected) or total>MAX_BYTES:
                    raise ValueError('Native archive member count/size exceeds its budget')
            names=[r.name for r in members]
            if (len(names)!=len(set(names)) or len(names)!=len(expected) or set(names)!=expected
                or sum(r.size for r in members)>MAX_BYTES or any(not r.isfile() or r.size<0
                    or Path(r.name).is_absolute() or '..' in Path(r.name).parts for r in members)):
                raise ValueError('Bounded unique ordinary native archive inventory required')
            archive.extractall(temporary,filter='data')
        folder=Path(temporary)
        if {p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}!=m['archive_files_sha256']:
            raise ValueError('Extracted native package bytes differ')
        value=assess(folder,root=root)
        if value!=m['comparison']:raise ValueError('Native refinement diagnostics semantic replay differs')
    return dict(verified=True,publication_id=m['publication_id'],comparison_evaluation_id=value['evaluation_id'],
        candidate_id=value['candidate_id'],completed_same_horizon=value['completed_same_horizon'],
        matched_points=value['matched_points'],numerical_replayed=False,operating_map_admitted=False,
        native_reuse_eligible=False,physical_qualification=False,**FLAGS)
