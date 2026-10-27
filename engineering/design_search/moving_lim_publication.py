"""Publish immutable actual moving-component experiments without resealing them.

The archived evaluator sources are separate from this current publication
generator and the latest model implementation. This checks byte identities and
independent accounting invariants; it never reruns or qualifies the motor.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from math import isclose,isfinite
import argparse,gzip,io,json,tarfile
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import encoded,identity,digest

CODE='engineering/design_search/moving_lim_publication.py'
OUTPUT='docs/design-engine/moving-lim-method'
SOURCE_BASE='8a8e82a0cb8abf962f747269746d9d01e6650137'
CASES=(('entry-coarse','source-epoch-1'),('entry-final-coarse','source-epoch-2'),
       ('entry-time-half','source-epoch-2'),('entry-mesh-refined','source-epoch-2'),
       ('highspeed-domain-control','source-epoch-2'))
REFERENCE='https://github.com/getdp-project/getdp/blob/master/templates/Lib_Magnetodynamics2D_av_Cir.pro'


def _read(path):return json.loads(Path(path).read_bytes())
def _id(record,key):
    if record.get(key)!=identity({k:v for k,v in record.items() if k!=key}):raise ValueError('Archived identity differs: '+key)


def _ordinary(root,name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('Ordinary archived path required')
    current=Path(root)
    for part in p.parts:
        current=current/part
        if current.is_symlink():raise ValueError('Archived symlink refused')
    if not current.is_file():raise ValueError('Archived file missing: '+name)
    return current


def audit(run,epoch):
    run=Path(run);data=_read(run/'input.json');r=data['request'];v=_read(run/'result.json');m=_read(run/'manifest.json')
    _id(r,'request_id');_id(v,'evaluation_id');_id(m,'manifest_id')
    if m['evaluation_id']!=v['evaluation_id']:raise ValueError('Archived manifest/result identity differs')
    inventory={p.name:digest(p) for p in run.iterdir() if p.is_file() and p.name!='manifest.json'}
    if inventory!=m['files_sha256']:raise ValueError('Archived payload inventory differs')
    source=m['source_sha256']
    if data['source_sha256']!=source or v['source_sha256']!=source:raise ValueError('Archived source maps differ')
    actual={p.relative_to(epoch).as_posix():digest(p) for p in Path(epoch).rglob('*') if p.is_file()}
    if actual!=source:raise ValueError('Exact archived evaluator source epoch differs')
    for name in source:_ordinary(epoch,name)
    b=r['bundle_definition'];_id(b,'definition_id')
    if (r['bundle_id']!=b['candidate_id'] or r['body_candidate_id']!=b['body_candidate_id']
        or r['motor_component_id']!=b['propulsion_component_id'] or r['motor_definition']!=b['motor_definition']
        or r['physical_geometry']!=b['motor_parameters']['physical']):raise ValueError('Archived component/parent physical identity differs')
    p=r['physical_geometry']
    if (p['primary_length_m'],p['secondary_length_m'],p['parallel_paths_per_phase'])!=(12.5,9.,10):raise ValueError('Unexpected component geometry')
    if v['request_id']!=r['request_id'] or v['bundle_id']!=r['bundle_id'] or v['motor_component_id']!=r['motor_component_id']:raise ValueError('Archived evaluation context differs')
    if v.get('operating_map_admitted') is not False or any(v.get(k) is not value or r.get(k) is not value for k,value in FLAGS.items()):raise ValueError('Component evidence cannot claim acceptance')
    trace=v.get('trace',[]);partial=run/'partial-trace.jsonl'
    if partial.is_file() and [json.loads(line) for line in partial.read_text().splitlines()]!=trace:raise ValueError('Archived partial/full trace differs')
    energy=0.;maximum_residual=0.
    for k,row in enumerate(trace,1):
        dt=r['dt_s'];time=k*dt;start=r['start_m']+r['speed_m_s']*time;area=p['secondary_length_m']*p['secondary_thickness_m']
        expected=(('time_s',time),('secondary_start_m',start),('secondary_end_m',start+p['secondary_length_m']),
            ('conductor_area_m2',area),('conductor_first_moment_x_m3',area*(start+p['secondary_length_m']/2)),
            ('mechanical_W',r['speed_m_s']*row['thrust_N']))
        if any(not isfinite(row[key]) or not isclose(row[key],value,rel_tol=1e-9,abs_tol=1e-9) for key,value in expected):raise ValueError('Archived moving geometry or mechanical work differs')
        currents=row['path_currents_A'];voltage=row['phase_voltage_commands_V'];resistance=v['wire_resistance_ohm_per_path']
        if len(currents)!=30 or abs(sum(currents))>1e-8:raise ValueError('Archived winding current closure differs')
        if not isclose(sum(i*i*q for i,q in zip(currents,resistance)),row['primary_copper_W'],rel_tol=1e-9,abs_tol=1e-9):raise ValueError('Archived copper work differs')
        if not isclose(sum(voltage[j//10]*i for j,i in enumerate(currents)),row['terminal_W'],rel_tol=1e-9,abs_tol=1e-9):raise ValueError('Archived terminal work differs')
        field=(row['magnetic_energy_J']-energy)/dt+row['backward_Euler_dissipation_W']
        residual=row['terminal_W']-row['primary_copper_W']-row['secondary_Joule_W']-row['mechanical_W']-field
        if not isclose(residual,row['discrete_power_residual_W'],rel_tol=1e-5,abs_tol=1e-9):raise ValueError('Archived discrete energy accounting differs')
        maximum_residual=max(maximum_residual,abs(residual));energy=row['magnetic_energy_J']
    if v['execution']=='completed' and v['state']=='completed' and len(trace)!=r['steps']:raise ValueError('Archived time inventory incomplete')
    result=dict(name=run.name,execution=v['execution'],state=v.get('state'),reason=v.get('reason'),
        evaluation_id=v['evaluation_id'],request_id=r['request_id'],bundle_id=r['bundle_id'],body_candidate_id=r['body_candidate_id'],
        motor_component_id=r['motor_component_id'],source_epoch=Path(epoch).name,source_sha256=source,
        dt_s=r['dt_s'],steps=r['steps'],speed_m_s=r['speed_m_s'],mesh_m=r['mesh_m'],voltage_peak_V=r['voltage_peak_V'],
        trace_rows=len(trace),numerical_validity=v.get('numerical_validity','held'),maximum_power_residual_W=maximum_residual,
        elapsed_worker_timeout_s=90,memory_limit_bytes=r['memory_bytes'],physical_accepted=False)
    if trace:result.update(nodes=v['nodes'],elements=v['elements'],Peclet_max=v['Peclet_max'],last=trace[-1],
        peak_path_current_A=max(abs(i) for row in trace for i in row['path_currents_A']))
    return result


def sources(root=ROOT):
    return {name:digest(Path(root)/name) for name in (CODE,'engineering/design_search/moving_lim.py',
        'engineering/design_search/tests/test_moving_lim.py','engineering/station_rail/common.py','engineering/station_rail/__init__.py')}


def collect(runs):
    runs=Path(runs);rows=[audit(runs/name,runs/epoch) for name,epoch in CASES]
    if len({row['bundle_id'] for row in rows})!=1 or len({row['motor_component_id'] for row in rows})!=1:raise ValueError('Mixed component campaign')
    zero=_read(runs/'initial-zero-smoke.json')
    if zero.get('exact_source_epoch_recorded') is not False or zero.get('admitted_validation_evidence') is not False:raise ValueError('Unsealed zero smoke cannot become qualified evidence')
    coarse,half,fine=rows[1:4]
    comparisons=dict(time_final_thrust_relative_change=abs(half['last']['thrust_N']-coarse['last']['thrust_N'])/abs(coarse['last']['thrust_N']),
        mesh_final_thrust_relative_change=abs(fine['last']['thrust_N']-coarse['last']['thrust_N'])/abs(coarse['last']['thrust_N']),
        spatial_time_convergence_established=False)
    return rows,zero,comparisons


def _archive(runs):
    runs=Path(runs);names={'initial-zero-smoke.json'}
    for name,epoch in CASES:
        for folder in (name,epoch):names.update(p.relative_to(runs).as_posix() for p in (runs/folder).rglob('*') if p.is_file())
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w',format=tarfile.PAX_FORMAT) as tar:
        for name in sorted(names):
            raw=_ordinary(runs,name).read_bytes();entry=tarfile.TarInfo(name);entry.size=len(raw);entry.mtime=0;entry.mode=0o644
            tar.addfile(entry,io.BytesIO(raw))
    return gzip.compress(stream.getvalue(),mtime=0)


def _readme(report):
    c=report['comparisons'];lines=['# Finite moving LIM component method','',
        'Actual bounded component calculations with a translating finite aluminium secondary and voltage-coupled winding currents. **No available operating map, qualified launch, complete journey or physical release.** The selected v0.6 reference is unchanged.','',
        'The P1 research parent is `'+report['bundle_id']+'`; its exact motor geometry is `'+report['motor_component_id']+'`. A declared, unverified wiring hypothesis adds 30 separately solved paths, five coils per path and a floating neutral. No result is transferred to a different motor, vehicle or installed wiring arrangement.','',
        '[Immutable input/output/log and evaluator-source archive](native-runs.tar.gz) · [Assessment](assessment.json) · [Publication receipt](manifest.json)','',
        '| Case | Execution | Mesh nodes | Final force, N | Archived source |','|---|---|---:|---:|---|']
    for r in report['rows']:
        lines.append('| '+r['name']+' | '+r['execution']+' | '+str(r.get('nodes','—'))+' | '+(f"{r['last']['thrust_N']:.8f}" if 'last' in r else '—')+' | '+r['source_epoch']+' |')
    lines+=['',f"Final force changes {100*c['time_final_thrust_relative_change']:.2f}% when the time step is halved and {100*c['mesh_final_thrust_relative_change']:.2f}% under the tested 2D mesh refinement. Convergence is **not established**. The 20 m/s request retains its Peclet-domain hold. The 2 V, 0.5 m/s startup samples are not operating thrust or an insufficient-thrust verdict for the reference railway.",'',
        'Six attempts comprise five sealed worker packages and one interactive zero-field smoke. The smoke lacked an exact saved source epoch; it is retained explicitly as unqualified and does not satisfy the source-bound zero-excitation obligation. Native runs retain their original source epochs. Current validation/verifier changes are bound separately by this publication; the old runs are never resealed as executions of current code.','',
        '## Method and independent controls','',
        'The fixed mesh conforms to the exact 12.5 m primary, teeth, slots and 15 mm gaps. The 9 m aluminium rectangle translates through it. Exact degree-two triangle/polygon moments update conductor mass, transport and floating-current operators at each position; forces are integrated from current and field, without overlap multiplication.','',
        'The coupled equations are `K(A)+M(x) A_dot+C(x,v) A+b(x)u=W I`, floating secondary-current closure, and `R I+height W^T A_dot+neutral=voltage`, with `sum(I)=0`. Here `Jz=-sigma(A_dot+u+v A_x)` and `Fx=integral(Jz A_x) dV`. Terminal work balances copper loss, secondary Joule loss, mechanical work, stored magnetic energy and explicit backward-Euler numerical dissipation. Tiny residuals establish the discrete accounting only.','',
        'The A/u and stranded-circuit formulation follows the class documented in the [official GetDP magnetodynamics/circuit template]('+REFERENCE+'). The translating cut-cell integration is implemented separately. Focused tests independently integrate manufactured polynomials, check closed winding turns and compare the actual coupled Jacobian against the closed-form RL response and its energy balance. An independent same-geometry field benchmark remains open.','',
        '## Remaining obligations','',
        'The steel law is a generic reversible numerical hypothesis; hysteresis/core loss, finite-height current return, end-turn leakage, physical winding grouping, converter switching/loss, protection, hardware current control and supplier correlation remain unresolved. Temperatures, cooling, repeated duty and complete installed equipment/mass/cost remain unknown. There is no coupled train-motion model in this component packet.','',
        'Next work requires a source-qualified zero control, further mesh/time/outer-boundary refinement, independent linear field/circuit and reversal benchmarks, a validated high-speed transport discretization, supplier magnetic/loss data, actual winding/inverter/protection definitions and authenticated measurements. Physical requirements stay open.','']
    return '\n'.join(lines)


def _assessment(rows,zero,comparisons,source,archive):
    report=dict(schema='osr-moving-LIM-method-publication/1',source_base_revision=SOURCE_BASE,
        bundle_id=rows[0]['bundle_id'],motor_component_id=rows[0]['motor_component_id'],rows=rows,comparisons=comparisons,
        attempted_cases=6,sealed_packages=5,unqualified_zero_smoke=zero,source_sha256=source,
        archive_sha256=sha256(archive).hexdigest(),references=[REFERENCE],
        operating_map_admitted=False,complete_installed_mass_kg=None,reference_changed=False,**FLAGS)
    report['publication_id']=identity(report);return report


def publish(runs,output=None,*,root=ROOT,replace=False):
    root=Path(root);output=Path(output) if output else root/OUTPUT
    if output.exists():
        if not replace:raise ValueError('Fresh moving-method publication required; use explicit replace for generated current files')
        previous=_read(output/'manifest.json');_id(previous,'manifest_id')
        if set(p.name for p in output.iterdir())!={'README.md','assessment.json','native-runs.tar.gz','manifest.json'} or {p.name:digest(p) for p in output.iterdir() if p.name!='manifest.json'}!=previous['files_sha256']:
            raise ValueError('Refuse replacing unrelated or edited publication files')
    source=sources(root);rows,zero,comparisons=collect(runs);archive=_archive(runs)
    report=_assessment(rows,zero,comparisons,source,archive);readme=_readme(report)
    if source!=sources(root):raise ValueError('Moving publisher source changed')
    output.mkdir(parents=True,exist_ok=replace);(output/'assessment.json').write_bytes(encoded(report));(output/'README.md').write_text(readme);(output/'native-runs.tar.gz').write_bytes(archive)
    manifest=dict(schema=report['schema'],publication_id=report['publication_id'],source_sha256=source,
        files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'},**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return verify(output,root=root)


def verify(output=None,*,root=ROOT):
    import tempfile
    output=Path(output) if output else Path(root)/OUTPUT;m=_read(output/'manifest.json');r=_read(output/'assessment.json')
    _id(m,'manifest_id');_id(r,'publication_id')
    if m['publication_id']!=r['publication_id'] or m['source_sha256']!=sources(root) or r['source_sha256']!=m['source_sha256']:raise ValueError('Moving publication source or identity differs')
    if {p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Moving publication payload differs')
    if any(r.get(k) is not value or m.get(k) is not value for k,value in FLAGS.items()) or r.get('operating_map_admitted') is not False:raise ValueError('Method publication cannot grant acceptance')
    if r.get('attempted_cases')!=6 or r.get('sealed_packages')!=5 or r.get('source_base_revision')!=SOURCE_BASE or r.get('reference_changed') is not False or r.get('complete_installed_mass_kg') is not None:raise ValueError('Moving publication scope differs')
    if (output/'README.md').read_text()!=_readme(r):raise ValueError('Moving publication explanation differs')
    archive=(output/'native-runs.tar.gz').read_bytes()
    if sha256(archive).hexdigest()!=r['archive_sha256']:raise ValueError('Moving native archive differs')
    with tempfile.TemporaryDirectory(prefix='osr-moving-publication-check-') as name:
        temp=Path(name)
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
            seen=set();size=0
            for member in tar:
                p=PurePosixPath(member.name)
                size+=member.size
                if not member.isfile() or member.size>8*1024*1024 or size>20*1024*1024 or p.is_absolute() or '..' in p.parts or p.as_posix()!=member.name or member.name in seen:raise ValueError('Ordinary unique bounded moving archive members required')
                if len(p.parts)==1:
                    if p.name!='initial-zero-smoke.json':raise ValueError('Unknown moving archive member')
                elif p.parts[0] not in {part for pair in CASES for part in pair}:raise ValueError('Unknown moving archive subtree')
                seen.add(member.name)
                target=temp/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tar.extractfile(member).read())
        rows,zero,comparisons=collect(temp)
        if _assessment(rows,zero,comparisons,m['source_sha256'],archive)!=r:raise ValueError('Moving publication assessment differs from immutable runs')
        if r['bundle_id']!=rows[0]['bundle_id'] or r['motor_component_id']!=rows[0]['motor_component_id']:raise ValueError('Moving publication parent physical identity differs')
    return dict(verified=True,publication_id=r['publication_id'],sealed_packages=5,operating_map_admitted=False,physical_accepted=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('publish','verify'));p.add_argument('--runs',type=Path);p.add_argument('--output',type=Path);p.add_argument('--replace',action='store_true');a=p.parse_args()
    if a.action=='publish' and a.runs is None:p.error('publish requires explicit --runs containing immutable component packages')
    value=publish(a.runs,a.output,replace=a.replace) if a.action=='publish' else verify(a.output);print(json.dumps(value,sort_keys=True))


if __name__=='__main__':main()
