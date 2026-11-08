"""Fresh-directory exports with original inputs, source receipts and read-only review."""
from copy import deepcopy
import gzip
import importlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from engineering.station_rail.common import encoded, identity, digest
from . import ROOT, FLAGS
from .model import SOURCE_FILES, compile_proposal, sealed, sources, validate_proposal


def load(path):
    path=Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())


def _write(out,name,value):
    target=out/name;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(value if isinstance(value,bytes) else encoded(value))


def _integration(root):
    location=str(Path(root)/'services/integration')
    if location not in sys.path:
        sys.path.insert(0,location)
    return importlib.import_module('osr_integration.engineering')


def frozen_source(root):
    """Refuse uncommitted compiler/input-adapter changes before fresh execution."""
    changed=subprocess.run(['git','status','--porcelain','--',*SOURCE_FILES],cwd=root,
        capture_output=True,text=True,check=True).stdout
    if changed.strip():
        raise ValueError('Commit compiler sources before fresh export: '+changed.strip())
    return subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()


def compile_run(study_path,body_path,service_id,output,*,root=ROOT):
    root=Path(root).resolve();out=Path(output).resolve()
    if out.exists():
        raise ValueError('Fresh output directory required; previous results are immutable')
    commit=frozen_source(root)
    before=sources(root);start=time.monotonic();out.mkdir(parents=True)
    stage='input loading'
    try:
        study=load(study_path);body=load(body_path)
        stage='same-candidate proposal compilation'
        proposal=compile_proposal(study,body,service_id,root=root)
        # Retain original bytes; compressed inputs are not rewritten to disguise provenance.
        originals=[]
        for name,path in (('study',Path(study_path)),('body',Path(body_path))):
            target='inputs/'+name+('.json.gz' if path.suffix=='.gz' else '.json')
            _write(out,target,path.read_bytes())
            originals.append(dict(path=target,origin=str(path.resolve()),sha256=digest(out/target),
                content_identity=study['study_id'] if name=='study' else body['evaluation_id']))
        _write(out,'proposal.json.gz',gzip.compress(encoded(proposal),mtime=0))
        _write(out,'summary.json',dict(proposal_id=proposal['proposal_id'],identities=proposal['identities'],
                                     summary=proposal['summary'],capacity=proposal['capacity'],limitations=proposal['limitations'],**FLAGS))
        stage='existing engineering evidence adapter'
        adapter=_integration(root)
        evidence=adapter.package(out,dict(city='synthetic-1500m-pilot',
            asset_id='research-railway-'+proposal['identities']['candidate_id'],
            engineering_revision=body['evaluation_id'],candidate_binding=proposal['identities'],
            assumptions=proposal['limitations'],
            artifacts=[dict(path=r['path'],tool='osr',tool_version=(root/'VERSION').read_text().strip()) for r in originals]))
        _write(out,'engineering-evidence.json',evidence)
        mapping=deepcopy(proposal['execution_mapping_draft']);mapping['engineering_sha256']=evidence['sha256']
        _write(out,'execution-mapping-draft.json',mapping)
        try:
            adapter.execution_proposal(evidence,mapping)
        except ValueError as exc:
            boundary=dict(status='held',reason=str(exc),review_reference=None,
                generic_adapter='services/integration/osr_integration/engineering.py:execution_proposal',
                mapping_is_native_ERP_import=False,**FLAGS)
        else:
            raise ValueError('Unreviewed mapping unexpectedly crossed business-review boundary')
        _write(out,'execution-boundary.json',boundary)
        after=sources(root)
        if before!=after:
            raise ValueError('Compiler source drift during export')
        for name,expected in proposal['source_sha256'].items():
            if digest(root/name)!=expected:
                raise ValueError('Upstream source drift during export: '+name)
        usage=dict(wall_s=time.monotonic()-start,peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            native_geometry_batches_executed=0,native_solver_batches_executed=0,
            observed_budget_met=time.monotonic()-start<=300 and resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=2*1024*1024,
            budget=dict(wall_s=300,peak_rss_KiB=2*1024*1024),
            isolation='Separate private run directory and source hash checks; no OS sandbox or hard resource enforcement claimed')
        _write(out,'usage.json',usage)
        _write(out,'README.md',_readme(proposal,usage).encode())
        files={p.relative_to(out).as_posix():digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
        manifest=dict(schema='osr-pilot-delivery-run/1',proposal_id=proposal['proposal_id'],identities=proposal['identities'],
            git_source_commit=commit,inputs=originals,source_sha256=proposal['source_sha256'],
            files_sha256=files,command=['python','-m','engineering.pilot_delivery','compile','--study',str(Path(study_path).resolve()),
                '--body',str(Path(body_path).resolve()),'--service-id',service_id,'--output',str(out)],
            completion='completed local draft export; release and engineering holds retained',**FLAGS)
        manifest['manifest_id']=identity(manifest);_write(out,'manifest.json',manifest)
        return manifest
    except Exception as exc:
        _write(out,'failure.json',dict(schema='osr-pilot-delivery-failure/1',stage=stage,
            exception=type(exc).__name__,reason=str(exc),git_source_commit=commit,source_sha256=before,
            wall_s=time.monotonic()-start,**FLAGS))
        raise


def _readme(proposal,usage):
    s=proposal['summary'];b=proposal['identities']
    return ('# Pilot manufacturing and delivery planning draft\n\n'
        f"Physical candidate: `{b['candidate_id']}`\n\n"
        f"Body engineering revision: `{b['engineering_revision']}`\n\n"
        f"Proposal: `{proposal['proposal_id']}`\n\n"
        f"{s['component_types']} body definitions, {s['occurrence_patterns']} occurrence patterns, "
        f"{s['body_occurrences_per_train']} counted occurrences per train and {s['project_trainsets']} proposed trainsets. "
        f"{s['assembly_types']} source assembly routes, {s['civil_requirement_types']} civil requirement types and "
        f"{s['cost_scopes']} existing cost scopes are retained.\n\n"
        f"Tasks: {s['task_status_counts']}. Ready means ready for planning review, never released work.\n\n"
        'Original compressed inputs and generic engineering-evidence metadata are retained. '
        'The existing execution adapter refuses the mapping until actual review and native Item/drawing/inspection references exist. '
        'No ERPNext, FUXA or gateway writes were made. No native format was fabricated.\n\n'
        '## Limits\n\n'+''.join('- '+s+'\n' for s in proposal['limitations'])+
        f"\nFresh compile: {usage['wall_s']:.3f} s; peak RSS {usage['peak_rss_KiB']/1024:.1f} MiB. "
        'No CAD/FEM batch was executed.\n')


def verify_run(output,*,root=ROOT,replay=True):
    """Check stored bytes/identities; optional deterministic cheap-model replay."""
    out=Path(output);root=Path(root);manifest=load(out/'manifest.json');sealed(manifest,'manifest_id')
    if manifest.get('schema')!='osr-pilot-delivery-run/1':
        raise ValueError('Unexpected delivery run schema')
    for relative,expected in manifest['files_sha256'].items():
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts or digest(out/path)!=expected:
            raise ValueError('Export file integrity differs: '+relative)
    for relative,expected in manifest['source_sha256'].items():
        if digest(root/relative)!=expected:
            raise ValueError('Export source is stale: '+relative)
    proposal=load(out/'proposal.json.gz');validate_proposal(proposal)
    if manifest['proposal_id']!=proposal['proposal_id'] or manifest['identities']!=proposal['identities']:
        raise ValueError('Manifest and proposal identity differ')
    inputs=manifest['inputs']
    if len(inputs)!=2:
        raise ValueError('Exact study and body inputs required')
    study,body=[load(out/r['path']) for r in inputs]
    if inputs[0]['content_identity']!=study['study_id'] or inputs[1]['content_identity']!=body['evaluation_id']:
        raise ValueError('Input identities differ')
    evidence=load(out/'engineering-evidence.json')
    if evidence.get('candidate_binding')!=proposal['identities'] or evidence.get('engineering_revision')!=body['evaluation_id']:
        raise ValueError('Evidence uses another candidate or revision')
    adapter=_integration(root);mapping=load(out/'execution-mapping-draft.json')
    if mapping.get('identities')!=proposal['identities']:
        raise ValueError('Execution mapping uses another identity')
    try:
        adapter.execution_proposal(evidence,mapping)
    except ValueError as exc:
        if str(exc)!=load(out/'execution-boundary.json')['reason']:
            raise ValueError('Recorded business hold differs') from exc
    else:
        raise ValueError('Unreviewed mapping accepted')
    if replay:
        replayed=compile_proposal(study,body,proposal['identities']['service_evaluation_id'],root=root,policy=proposal['policy'])
        if replayed!=proposal:
            raise ValueError('Deterministic replay differs')
    return dict(verified=True,proposal_id=proposal['proposal_id'],manifest_id=manifest['manifest_id'],
                deterministic_replay=replay,task_status_counts=proposal['summary']['task_status_counts'],**FLAGS)
