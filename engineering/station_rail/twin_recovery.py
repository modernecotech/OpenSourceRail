"""Separate bounded verification recovery for completed native research exports.

Frozen twin generation and its original timeout remain unchanged. Recovery
reopens every IFC occurrence and checks its identity and volume against the
native BRep result before creating a new, explicitly recovered receipt.
"""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,os,shutil,subprocess,sys
from . import ROOT
from .common import encoded,identity,digest
from engineering.design_search import contracts as k,campaign,wheel_twin as old
PRODUCER='engineering/station_rail/twin_recovery.py'
TIMEOUT='Bounded60s IFC export/verification budget exhausted'
FLAGS=old.FLAGS


def _source(root):return {PRODUCER:digest(Path(root)/PRODUCER)}


def check_occurrences(candidate_id,parts,native,actual):
    """Check every native/IFC occurrence, including identity and volume limits."""
    expected={p['id']:p for p in parts};known={r['id']:r for r in native['rows']};seen={}
    if len(expected)!=len(parts) or len(known)!=len(native['rows']):raise ValueError('Duplicate expected/native occurrence')
    if native['candidate_id']!=candidate_id or native['part_count']!=len(parts) or set(known)!=set(expected):raise ValueError('Native candidate/occurrence inventory differs')
    for row in actual:
        name=row['id']
        if name in seen:raise ValueError('Duplicate IFC occurrence')
        if name not in expected:raise ValueError('Unexpected IFC occurrence')
        p=expected[name];n=known[name];v=n['native_volume_m3']
        k.finite(v,'native occurrence volume',True);k.finite(row['volume_m3'],'IFC occurrence volume',True)
        if row['candidate_id']!=candidate_id or row['occurrence_id']!=name or row['frame']!=p['twin_frame']:raise ValueError('IFC occurrence identity differs')
        if row['physical_accepted'] is not False or row['complete_installed_twin'] is not False:raise ValueError('IFC cannot grant release')
        if abs(v-p['volume_m3'])>max(1e-10,1e-6*p['volume_m3']):raise ValueError('Native BRep volume differs from counted physical occurrence')
        error=abs(row['volume_m3']-v)/v
        if error>.005:raise ValueError('IFC native BRep volume mismatch beyond0.5%: '+name)
        seen[name]=dict(row,native_volume_m3=v,relative_volume_error=error)
    if set(seen)!=set(expected):raise ValueError('IFC occurrence inventory incomplete')
    total=sum(r['native_volume_m3'] for r in native['rows'])
    for field in ('native_volume_m3','reopened_volume_m3','step_volume_m3'):
        if abs(native[field]-total)>max(1e-8,1e-7*total):raise ValueError('Native/reopened/STEP total volume differs')
    return dict(part_count=len(seen),maximum_relative_volume_error=max((r['relative_volume_error'] for r in seen.values()),default=0.),rows=[seen[n] for n in sorted(seen)])


AUDIT_SCRIPT=r'''
from pathlib import Path
import json,time
import ifcopenshell,ifcopenshell.geom
from ifcopenshell.util.element import get_pset
from ifcopenshell.util.shape import get_volume
from engineering.station_rail.twin_recovery import check_occurrences,FLAGS
from engineering.station_rail.common import encoded,identity
out=Path(__file__).parent;started=time.monotonic()
data=json.loads((out/'native-input.json').read_bytes());native=json.loads((out/'native-result.json').read_bytes())
f=ifcopenshell.open(str(out/'wheel-stock.ifc'));rows=[]
for obj in f.by_type('IfcBuildingElementProxy'):
    ps=get_pset(obj,'OSR_Research_Identity');shape=ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(),obj)
    rows.append(dict(id=obj.Name,candidate_id=ps.get('candidate_id'),occurrence_id=ps.get('occurrence_id'),frame=ps.get('frame'),
        physical_accepted=ps.get('physical_accepted'),complete_installed_twin=ps.get('complete_installed_twin'),volume_m3=abs(get_volume(shape.geometry))))
value=check_occurrences(data['candidate_id'],data['parts'],native,rows)
value.update(schema='osr-wheel-twin-recovery-IFC-audit/1',candidate_id=data['candidate_id'],execution='completed',
    method='Every occurrence reopened through IfcOpenShell geometry kernel; identity and native BRep-volume comparison',
    ifcopenshell_version=ifcopenshell.version,elapsed_s=time.monotonic()-started,native_reopened=True,**FLAGS)
value['audit_id']=identity(value);(out/'recovery-ifc-audit.json').write_bytes(encoded(value))
'''


def _check_existing(output,candidate=None,results=None):
    output=Path(output);stored=json.loads((output/'candidate.json').read_bytes());k.validate_candidate(stored)
    if candidate is not None and stored!=candidate:raise ValueError('Existing twin physical candidate differs')
    evaluations=json.loads((output/'evaluations.json').read_bytes())
    if results is not None and evaluations!=results:raise ValueError('Existing twin evaluations differ')
    for r in evaluations:
        k.validate_result(r)
        if r['candidate_id']!=stored['candidate_id'] or r['requirement_revision']!=stored['requirement_revision']:raise ValueError('Mixed existing evaluation/requirement identity')
    data=json.loads((output/'native-input.json').read_bytes());raw=json.loads((output/'native-result.json').read_bytes());bom=json.loads((output/'engineering-bom.json').read_bytes())
    for record in (data,bom):
        if record['candidate_id']!=stored['candidate_id'] or any(record.get(n) is not v for n,v in FLAGS.items()):raise ValueError('Existing native input/BOM identity or release differs')
    if data['parts']!=bom['known_geometric_occurrences']:raise ValueError('Native input and engineering BOM differ')
    expected={g['native_part']['id']:g['native_part'] for g in stored['geometry'] if g.get('native_part') is not None}
    frames={g['native_part']['id']:g['frame_id'] for g in stored['geometry'] if g.get('native_part') is not None}
    if len(expected)!=len(data['parts']):raise ValueError('Candidate native occurrence count differs')
    for p in data['parts']:
        if p['twin_frame']!=frames.get(p['id']):raise ValueError('Native occurrence frame differs from physical candidate')
        physical=deepcopy(p);physical.pop('twin_frame')
        if physical!=expected.get(p['id']):raise ValueError('Existing native occurrence differs from physical candidate')
    if (output/'worker.py').read_text()!=old.SCRIPT:raise ValueError('Existing native generation worker differs from frozen producer')
    for name in ('wheel-stock.FCStd','wheel-stock.step','wheel-stock.ifc','manufacturing-bom.json','assembly.json','qa.json','procurement.json','maintenance.json','stdout.log','stderr.log'):
        if not (output/name).is_file():raise ValueError('Incomplete native export: '+name)
    return stored,evaluations,data,raw


def recover(output,error,*,root=ROOT,timeout_s=240,reported_prior_timeout=False):
    """Recover only the exact frozen IFC timeout, without rewriting CAD/IFC."""
    output=Path(output);root=Path(root)
    if type(error) is not TimeoutError or str(error)!=TIMEOUT:raise ValueError('Only exact bounded IFC verification timeout is eligible')
    if type(timeout_s) is not int or not 1<=timeout_s<=240:raise ValueError('Separate recovery budget is at most240s')
    if (output/'manifest.json').exists():raise ValueError('Existing sealed package must be verified, never recovered over')
    if any((output/n).exists() for n in ('twin.json','README.md','recovery-timeout.json','recovery-ifc-audit.json')):raise ValueError('Preserve existing unsealed recovery attempt; coordinator must inspect it')
    c,results,data,raw=_check_existing(output);sources=old._sources(c);recovery_source=_source(root)
    before={p.name:digest(p) for p in output.iterdir() if p.is_file()}
    timeout_receipt=dict(schema='osr-wheel-twin-generation-timeout/1',candidate_id=c['candidate_id'],
        original_execution='failed',exception_type='TimeoutError',message=TIMEOUT,original_budget_s=60,
        prior_timeout_reported_by_coordinator=reported_prior_timeout,original_files_sha256=before,
        original_source_sha256=sources,recovery_source_sha256=recovery_source,**FLAGS)
    timeout_receipt['receipt_id']=identity(timeout_receipt);(output/'recovery-timeout.json').write_bytes(encoded(timeout_receipt))
    (output/'recovery-worker.py').write_text(AUDIT_SCRIPT)
    try:
        proc=subprocess.run([sys.executable,str((output/'recovery-worker.py').resolve())],cwd=output,capture_output=True,text=True,timeout=timeout_s,
            env={**os.environ,'PYTHONPATH':str(root)+os.pathsep+os.environ.get('PYTHONPATH',''),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        (output/'recovery-stdout.log').write_text(proc.stdout);(output/'recovery-stderr.log').write_text(proc.stderr)
        if proc.returncode:raise ValueError('Independent recovery IFC check failed; original and audit logs preserved')
    except subprocess.TimeoutExpired as error:
        (output/'recovery-stdout.log').write_bytes(error.stdout or b'');(output/'recovery-stderr.log').write_bytes(error.stderr or b'')
        raise TimeoutError('Separate240s IFC recovery did not complete; no manifest issued') from error
    audit=json.loads((output/'recovery-ifc-audit.json').read_bytes())
    if audit['audit_id']!=identity({n:v for n,v in audit.items() if n!='audit_id'}) or audit['execution']!='completed':raise ValueError('Recovery audit identity differs')
    if before!={n:digest(output/n) for n in before}:raise ValueError('Original export changed during recovery')
    if sources!=old._sources(c) or recovery_source!=_source(root):raise ValueError('Recovery producer changed')
    inventory=k.inventory_summary(c);unknown=[r['id'] for r in c['installed_inventory'] if r['status']=='unknown'];native_ids={g['id'] for g in c['geometry'] if g.get('native_part') is not None}
    unlocated=[r['id'] for r in c['installed_inventory'] if r['status']=='known' and r.get('cg_m') is None and r.get('geometry_id') not in native_ids]
    ident={n:data[n] for n in ('candidate_id','requirement_revision','component_ids')}
    native_status={n:v for n,v in raw.items() if n!='rows'};native_status.update(execution='completed',native_reopened=True,**FLAGS)
    ifc={n:v for n,v in audit.items() if n!='rows'};ifc.update(original_generation_execution='failed',separate_recovery_execution='completed',original_budget_s=60,recovery_budget_s=timeout_s)
    summary=dict(schema='osr-wheel-research-twin/1',**ident,known_geometric_occurrences=len(data['parts']),omitted_unknown_inventory_ids=unknown,
        omitted_unlocated_inventory_ids=unlocated,inventory=inventory,native=native_status,IFC=ifc,evaluation_ids=[r['evaluation_id'] for r in results],
        frames=dict(vehicle='Car reference',station='Separate wayside module reference; not an installed co-located assembly',guidebeam='Separate selected concrete/rail span reference'),
        vehicle_scope='One car known stock plus separate station module and selected guidebeam span',
        scope='Known-stock research twin only; complete installed mass/CG/inertia, priced costs, manufacturing and physical acceptance remain open',
        recovery=dict(original_timeout_receipt_id=timeout_receipt['receipt_id'],IFC_audit_id=audit['audit_id'],producer=PRODUCER,**FLAGS),**FLAGS)
    (output/'twin.json').write_bytes(encoded(summary))
    (output/'README.md').write_text('# Wheel-rail known-stock research twin\n\nOpenSourceRail pursues simple, locally repairable station-powered transport. This package connects candidate `'+c['candidate_id']+'` to counted stock and draft delivery records.\n\n[Native FreeCAD](wheel-stock.FCStd) · [STEP](wheel-stock.step) · [IFC](wheel-stock.ifc)\n\n[Engineering BOM](engineering-bom.json) · [Manufacturing takeoff](manufacturing-bom.json) · [Assembly](assembly.json) · [QA](qa.json) · [Procurement](procurement.json) · [Maintenance](maintenance.json) · [Evidence summary](twin.json)\n\nThe original generation failed its60second IFC verification budget. A separate bounded recovery reopened every IFC occurrence, checked its candidate/occurrence/frame identity and compared its volume with the native BRep result. The original CAD, STEP, IFC, inputs and logs remain unchanged; [timeout receipt](recovery-timeout.json) and [recovery audit](recovery-ifc-audit.json) record both stages.\n\nVehicle, station and guidebeam coordinate frames are separate. Unknown and unlocated equipment has no placeholder solid. Complete installed mass, CG, inertia, cost, joining and physical qualification remain open. All manufacturing and operating releases remain held.\n')
    manifest=dict(schema='osr-wheel-research-twin-manifest/1',**ident,source_sha256=sources,
        recovery_source_sha256=recovery_source,recovery_metadata=dict(original_execution='failed',recovery_execution='completed',timeout_receipt_id=timeout_receipt['receipt_id'],audit_id=audit['audit_id']),
        files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return verify(output,root=root)


def verify(output,*,root=ROOT):
    result=old.verify(output);output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if 'recovery_source_sha256' in m:
        if m['recovery_source_sha256']!=_source(root):raise ValueError('Recovery method differs')
        receipt=json.loads((output/'recovery-timeout.json').read_bytes());audit=json.loads((output/'recovery-ifc-audit.json').read_bytes())
        if receipt['receipt_id']!=identity({n:v for n,v in receipt.items() if n!='receipt_id'}) or receipt['message']!=TIMEOUT or receipt['original_execution']!='failed':raise ValueError('Original timeout receipt differs')
        if audit['audit_id']!=identity({n:v for n,v in audit.items() if n!='audit_id'}):raise ValueError('Recovery audit receipt differs')
        if receipt['original_files_sha256']!={n:digest(output/n) for n in receipt['original_files_sha256']}:raise ValueError('Original generated bytes changed')
        c,evaluations,data,raw=_check_existing(output)
        checked=check_occurrences(c['candidate_id'],data['parts'],raw,audit['rows'])
        if checked['part_count']!=audit['part_count'] or checked['maximum_relative_volume_error']!=audit['maximum_relative_volume_error']:raise ValueError('Recovery occurrence audit summary differs')
        if audit['candidate_id']!=c['candidate_id'] or any(record.get(n) is not v for record in (receipt,audit) for n,v in FLAGS.items()):raise ValueError('Recovery identity/disposition differs')
        if receipt['original_source_sha256']!=m['source_sha256'] or receipt['recovery_source_sha256']!=m['recovery_source_sha256']:raise ValueError('Recovery source receipts differ')
        if m['recovery_metadata']['timeout_receipt_id']!=receipt['receipt_id'] or m['recovery_metadata']['audit_id']!=audit['audit_id']:raise ValueError('Recovery metadata differs')
        result.update(recovered=True,original_generation_execution='failed',separate_recovery_execution='completed',recovery_audit_id=audit['audit_id'])
    else:result['recovered']=False
    return result


def ensure_all(campaign_id,*,root=ROOT,state=None,known_timeouts=None,timeout_s=240):
    root=Path(root);state=Path(state) if state is not None else root/'build/design-search';known_timeouts={} if known_timeouts is None else known_timeouts
    comparison=campaign.compare(campaign_id,state=state);rows=[]
    for c in comparison['candidates']:
        results=[r for r in comparison['results']+comparison['confirmations'] if r['candidate_id']==c['candidate_id']]
        output=root/'build/v06-loop/twins'/campaign_id/c['candidate_id']
        if (output/'manifest.json').is_file():result=verify(output,root=root)
        elif output.exists():
            _check_existing(output,c,results)
            message=known_timeouts.get(c['candidate_id'])
            if message!=TIMEOUT:raise ValueError('Unsealed prior export requires explicit coordinator termination report; no cause assumed')
            result=recover(output,TimeoutError(message),root=root,timeout_s=timeout_s,reported_prior_timeout=True)
        else:
            try:old.compile(c,results,output=output,export_native=True,allow_incomplete=True)
            except TimeoutError as error:
                result=recover(output,error,root=root,timeout_s=timeout_s)
            else:result=verify(output,root=root)
        rows.append(dict(candidate_id=c['candidate_id'],raw_package_path=str(output),manifest_id=result['manifest_id'],recovered=result['recovered'],verified=True))
    return dict(campaign_id=campaign_id,verified_twins=rows,physical_candidate_count=len(rows),**FLAGS)


def bind_publication(output,*,root=ROOT):
    """Bind separate recovery audits after the frozen publisher completes."""
    from engineering.design_search import wheel_publication as pub
    output=Path(output);root=Path(root);pub.verify(output)
    current=json.loads((output/'manifest.json').read_bytes());summary=json.loads((output/'summary.json').read_bytes())
    if 'recovery_source_sha256' in current:
        if current['recovery_source_sha256']!=_source(root):raise ValueError('Published recovery method differs')
        return pub.verify(output)
    original=(output/'manifest.json').read_bytes();dest=output/'export-recovery';dest.mkdir();rows=[]
    (dest/'original-publication-manifest.json').write_bytes(original)
    for twin in summary['twins']:
        raw=Path(twin['native_directory']);checked=verify(raw,root=root)
        if not checked['recovered']:continue
        target=dest/twin['candidate_id'];target.mkdir()
        for p in sorted(raw.glob('recovery-*')):
            if p.is_file():shutil.copyfile(p,target/p.name)
        rows.append(dict(candidate_id=twin['candidate_id'],native_manifest_id=checked['manifest_id'],recovery_audit_id=checked['recovery_audit_id']))
    receipt=dict(schema='osr-wheel-publication-recovery-binding/1',campaign_id=current['campaign_id'],original_publication_manifest_id=current['manifest_id'],
        recovery_source_sha256=_source(root),recovered_twins=rows,**FLAGS);receipt['receipt_id']=identity(receipt)
    (dest/'binding.json').write_bytes(encoded(receipt))
    current['source_sha256'].update(_source(root));current['recovery_source_sha256']=_source(root)
    current['files_sha256']={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.relative_to(output).as_posix()!='manifest.json'}
    current.pop('manifest_id');current['manifest_id']=identity(current);(output/'manifest.json').write_bytes(encoded(current));return pub.verify(output)
