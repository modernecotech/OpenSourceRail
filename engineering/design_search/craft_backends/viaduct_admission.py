"""Independent policy checks over immutable native CAD execution receipts.

The numerical producer remains pinned to its original source epoch. This
separate verifier recomputes summary claims; it grants no engineering release.
"""
import json
from pathlib import Path
from . import native, identity
from .cases import FLAGS

PRODUCER='engineering/design_search/craft_backends/viaduct_admission.py'


def _unreleased(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in FLAGS and item is not False:
                raise ValueError('CAD evidence cannot promote '+key)
            _unreleased(item)
    elif isinstance(value,list):
        for item in value:_unreleased(item)


def check_claims(manifest,request,executions,inventory):
    """Pure checks, separately testable without invoking a native tool."""
    _unreleased(manifest);_unreleased(request)
    for record,key in ((manifest,'result_id'),(request,'request_id')):
        if record.get(key)!=identity({k:v for k,v in record.items() if k!=key}):
            raise ValueError('CAD evidence seal differs')
    if manifest['request_id']!=request['request_id']:
        raise ValueError('CAD evidence request differs')
    records=request['cases'];by_id={c['case_id']:c for c in records}
    if (len(by_id)!=len(records) or not records or set(by_id)!=set(manifest['cases'])
            or manifest['case_count']!=len(records)):
        raise ValueError('CAD case coverage differs')
    evaluations={c['case_definition_id']:e for c,e in zip(records,request['evaluations'])}
    if len(request['evaluations'])!=len(records):raise ValueError('CAD evaluation coverage differs')
    for name,case in by_id.items():
        row=manifest['cases'][name]
        if any(row.get(k)!=case[k] for k in ('candidate_id','component_geometry_id')):
            raise ValueError('Mixed native CAD candidate')
        if row['execution']=='completed' and row['evaluation_id']!=evaluations[case['case_definition_id']]['evaluation_id']:
            raise ValueError('Mixed native CAD evaluation')
    expected=all(row.get('execution')=='completed'
        and row.get('diagnostic',{}).get('comparison_passed') is True
        and row.get('exact_step',{}).get('comparison_passed') is True
        for row in manifest['cases'].values())
    if manifest['nominal_geometry_comparison_passed'] is not expected:
        raise ValueError('CAD aggregate comparison claim differs')
    if expected and any(e.get('execution') not in ('executed','completed') or e.get('returncode')!=0 for e in executions):
        raise ValueError('Successful geometry requires successful recorded executions')
    actual_count=len(executions)
    if (manifest['native_processes']!=actual_count or manifest['fresh_native_processes']!=actual_count
            or manifest['cached_native_evaluations']!=0 or actual_count>request['limits']['maximum_native_processes']):
        raise ValueError('CAD native execution accounting differs')
    if manifest['default_backend_changed'] is not False or manifest['complete_bridge_analysis'] is not False:
        raise ValueError('CAD cannot select a default or complete a bridge analysis')
    if manifest['artifact_sha256']!=inventory:
        raise ValueError('Exact CAD inventory differs, including nested manifests')
    return expected


def verify(output,case=None,*,root=None):
    from . import viaduct_cad, solidcraft
    root=viaduct_cad.ROOT if root is None else Path(root)
    output=Path(output).absolute()
    if any(p.is_symlink() for p in (output,*output.parents)):raise ValueError('Ordinary immutable CAD directory required')
    # Existing source, per-body geometry and reference readback checks remain.
    manifest=viaduct_cad.verify(output,case,root=root)
    request=json.loads((output/'request.json').read_bytes())
    executions=[json.loads(p.read_bytes()) for p in sorted(output.glob('*/generate/execution.json'))]
    reference=output/'freecad-reference/execution.json'
    if reference.exists():executions.append(json.loads(reference.read_bytes()))
    inventory={p.relative_to(output).as_posix():native.digest(p) for p in output.rglob('*')
        if p.is_file() and p!=output/'manifest.json'}
    if any(p.is_symlink() for p in output.rglob('*')):raise ValueError('Linked CAD evidence is not immutable')
    passed=check_claims(manifest,request,executions,inventory)
    for c in request['cases']:
        folder=output/c['case_id']
        if json.loads((folder/'commands.json').read_bytes())!=solidcraft.script_for(c):
            raise ValueError('Native CAD commands do not reproduce from the physical case')
    value=dict(schema='osr-viaduct-cad-independent-admission/1',verified=True,
        source_result_id=manifest['result_id'],source_request_id=request['request_id'],
        verifier_sha256=native.digest(__file__),native_processes=len(executions),
        nominal_geometry_comparison_passed=passed,
        admission_scope='Exact nominal CAD comparison only; no generic native evaluator or physical approval',
        source_names_preserved_by_freecad=all(r.get('exact_step',{}).get('source_names_preserved') is True
            for r in manifest['cases'].values()),**FLAGS)
    value['verification_id']=identity(value)
    return value
