"""Actual-candidate runner binding and post-supervisor acceptance gate.

No Docker, native services or supplier fixtures are executed here. The reviewed
supervisor remains unchanged. A native child can stage ERP evidence; joint
acceptance is read-only and possible only after the supervisor has exited.
"""
from hashlib import sha256
from pathlib import Path
import json
import math
import os
import signal

from contracts import FLAGS
import candidate_contracts
import resource_supervisor as supervisor

SUPERVISOR_PATH='tools/automation/native-v06/resource_supervisor.py'
ENV_KEYS=('OSR_NATIVE_OWNER','OSR_NATIVE_PRIVATE_DIR','OSR_NATIVE_BINDING')
APP_SERVICES=('configurator','backend','frontend','websocket','queue-short','queue-long','scheduler','create-site')


def digest(value):return sha256(supervisor.encoded(value)).hexdigest()


def flags(value):
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Resource/business evidence cannot accept physical equipment')


def ordinary(path,maximum=16*1024**2):
    path=Path(path).absolute()
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file() or not 0<path.stat().st_size<=maximum:
        raise ValueError('Ordinary bounded native binding/receipt file required')
    return path


def raw_file(path):
    with ordinary(path).open('rb') as stream:raw=stream.read(16*1024**2+1)
    if len(raw)>16*1024**2:raise ValueError('Native binding/receipt grew beyond its byte budget')
    return raw


def load(path):return json.loads(raw_file(path))


def seal(value):return dict(value,binding_id=digest(value))


def validate(binding,value,source):
    flags(binding)
    if binding.get('schema')!='osr-v06-native-candidate-run-binding/1' or binding.get('binding_id')!=digest({k:v for k,v in binding.items() if k!='binding_id'}):
        raise ValueError('Sealed candidate run binding required')
    supervisor.owner_id(binding['owner'])
    expected=dict(input_id=value['input_id'],identities=value['identities'],component_id=value['component_id'],
        proposal_file_sha256=value['proposal_file_sha256'],review_pack_sha256=value['review_pack']['sha256'],source_sha256=source,
        supervisor_source_sha256=source[SUPERVISOR_PATH])
    if any(binding.get(k)!=v for k,v in expected.items()):raise ValueError('Native run binding differs from exact input/candidate/source')
    control=Path(binding['control_dir'])
    if not control.is_absolute() or binding['fixture_dir']!=str(control/'fixture'):raise ValueError('Exact private fixture path required')
    return binding


def bind_run(value,source,output=None):
    """Acknowledge the exact supervisor before native fixture writes/calls."""
    environ=os.environ
    if value.get('schema')!='osr-v06-platform-fixture/2':
        if any(environ.get(k) for k in ENV_KEYS):raise ValueError('Supervisor binding requires actual-candidate v2; legacy kit cannot substitute')
        return None
    if not all(environ.get(k) for k in ENV_KEYS):raise ValueError('Actual-candidate run requires the reviewed resource supervisor')
    owner=supervisor.owner_id(environ['OSR_NATIVE_OWNER']);control=Path(environ['OSR_NATIVE_PRIVATE_DIR'])
    if not control.is_absolute() or not control.is_dir() or any(p.is_symlink() for p in (control,*control.parents)):
        raise ValueError('Existing ordinary bound supervisor directory required')
    fixture=control/'fixture'
    if output is not None and Path(output).absolute()!=fixture:raise ValueError('Actual candidate output must be exactly bound control_dir/fixture')
    if fixture.exists():raise ValueError('Fresh bound fixture directory required')
    # The reviewed API authenticates OSR_NATIVE_BINDING and writes only the
    # acknowledgement. It does not start resources or choose a candidate.
    request=supervisor.require_binding(owner,control);flags(request)
    command=load(control/'command.json');flags(command)
    if not isinstance(command.get('argv'),list) or not command['argv'] or not all(isinstance(v,str) and v for v in command['argv']):
        raise ValueError('Exact supervisor command argv required')
    binding=seal(dict(schema='osr-v06-native-candidate-run-binding/1',owner=owner,environment='simulation',
        control_dir=str(control),fixture_dir=str(fixture),input_id=value['input_id'],identities=value['identities'],
        component_id=value['component_id'],proposal_file_sha256=value['proposal_file_sha256'],review_pack_sha256=value['review_pack']['sha256'],
        source_sha256=source,supervisor_source_sha256=source[SUPERVISOR_PATH],
        supervisor_binding_sha256=digest(request),supervisor_command_sha256=digest(command['argv']),**FLAGS))
    validate(binding,value,source);target=control/'candidate-run-binding.json'
    if target.exists():
        if load(target)!=binding:raise ValueError('Bound candidate/source/command cannot be overwritten')
    else:
        with target.open('x') as stream:json.dump(binding,stream,sort_keys=True,separators=(',',':'),allow_nan=False)
        target.chmod(0o600)
    return binding


def compose_overlay(owner,root,cpu_quota,*,candidate=False):
    """Disposable override only; the retained v1 rendering stays byte-identical."""
    supervisor.owner_id(owner);root=Path(root)
    result='services:\n'
    for name in (*APP_SERVICES,'db','redis-cache','redis-queue'):
        result+='  '+name+':\n    labels:\n      '+supervisor.LABEL+': '+owner+'\n'
        if cpu_quota:result+='    cpus: 1.0\n'
        if name in APP_SERVICES:result+='    environment:\n      OPENBLAS_NUM_THREADS: "1"\n      OMP_NUM_THREADS: "1"\n      MKL_NUM_THREADS: "1"\n    volumes:\n      - '+str(root/'deployment/erpnext/apps/osr_erpnext')+':/home/frappe/frappe-bench/apps/osr_erpnext:ro\n'
        if candidate and name=='redis-cache':result+='    volumes:\n      - redis-cache-data:/data\n'
    volumes=('sites','logs','db-data','redis-data',*(['redis-cache-data'] if candidate else []))
    result+='volumes:\n'+''.join('  '+name+':\n    labels:\n      '+supervisor.LABEL+': '+owner+'\n' for name in volumes)
    if candidate:result+='networks:\n  default:\n    labels:\n      '+supervisor.LABEL+': '+owner+'\n'
    return result


def verify_supervision(evidence,value,source,result):
    """Return a small joint receipt only after real lifecycle validation upstream."""
    if value.get('schema')!='osr-v06-platform-fixture/2':raise ValueError('Actual-candidate v2 evidence required')
    candidate_contracts.verify_result(result,value,source)
    erp_raw=raw_file(Path(evidence)/'result.json')
    if json.loads(erp_raw)!=result:raise ValueError('Actual ERP lifecycle bytes differ from the verified result')
    if result.get('acceptance_state')!='awaiting-resource-supervision':raise ValueError('Exact staged actual-candidate lifecycle receipt required')
    binding=validate(result.get('run_binding',{}),value,source);control=Path(binding['control_dir'])
    if Path(evidence).absolute()!=Path(binding['fixture_dir'])/'evidence':raise ValueError('ERP evidence is outside its exact bound fixture directory')
    if result.get('namespace')!=binding['owner'] or load(control/'candidate-run-binding.json')!=binding:
        raise ValueError('ERP result belongs to another resource owner/binding')
    request=load(control/'supervisor-binding.json');flags(request)
    ack=load(control/'runner-binding.json');command=load(control/'command.json');flags(command)
    if (request.get('owner')!=binding['owner'] or request.get('private_dir')!=str(control) or digest(request)!=binding['supervisor_binding_sha256'] or
            ack!=dict(owner=binding['owner'],private_dir=str(control),binding_sha256=digest(request)) or
            digest(command['argv'])!=binding['supervisor_command_sha256']):raise ValueError('Supervisor request/acknowledgement/command binding differs')
    resource_raw=raw_file(control/'supervisor-result.json');resource=json.loads(resource_raw);flags(resource)
    zero=lambda value:type(value) is int and value==0
    if (resource.get('schema')!='osr-native-resource-supervision/1' or resource.get('execution')!='completed' or resource.get('owner')!=binding['owner'] or
            not zero(resource.get('child_exit')) or not zero(resource.get('reaper_exit')) or resource.get('failure') is not None or
            resource.get('supervisor_source_sha256')!=binding['supervisor_source_sha256'] or resource.get('binding_sha256')!=digest(request) or
            resource.get('command_sha256')!=binding['supervisor_command_sha256'] or resource.get('limits')!=request.get('limits')):
        raise ValueError('Completed exact-source resource supervision is required')
    final=resource.get('final_accounting',{});limits=resource['limits']
    comparisons=[(final.get('cpu_charged_s'),limits.get('cpu_seconds')),(resource.get('elapsed_s'),limits.get('elapsed_seconds')),
        (resource.get('observed_peak_rss_bytes'),limits.get('rss_bytes')),(resource.get('observed_peak_disk_bytes'),limits.get('disk_bytes'))]
    valid_number=lambda n:type(n) in (int,float) and math.isfinite(n) and n>=0
    if (final.get('violations')!=[] or any(not valid_number(n) or not valid_number(limit) or n>limit for n,limit in comparisons) or
            not valid_number(final.get('host_free_bytes')) or final['host_free_bytes']<limits['host_reserve_bytes']):
        raise ValueError('Completed resource accounting must remain within its bound allocation')
    cleanup=resource.get('cleanup',{});remaining=cleanup.get('remaining')
    if (cleanup.get('owner')!=binding['owner'] or cleanup.get('verified') is not True or cleanup.get('errors')!=[] or
            remaining!={'container':[],'volume':[],'network':[]} or cleanup.get('unaccounted_volume_mounts')!=[]):
        raise ValueError('Verified exact-owner Docker teardown required')
    host=resource.get('host_process_cleanup',{});adoption=host.get('adoption',{});flags(adoption);cap=adoption.get('capabilities') or {}
    if (host.get('verified') is not True or host.get('worker_reaped') is not True or not zero(host.get('worker_wait_status')) or
            adoption.get('verified') is not True or adoption.get('owner')!=binding['owner'] or adoption.get('source_sha256')!=binding['supervisor_source_sha256'] or
            not zero(adoption.get('native_exit')) or not zero(adoption.get('native_wait_status')) or adoption.get('native_reaped') is not True or
            adoption.get('remaining_direct_children')!=[] or cap.get('subreaper') is not True or cap.get('pidfd_verified') is not True or
            cap.get('parent_death_signal')!=signal.SIGTERM or cap.get('verified_before_launch') is not True or cap.get('waitability',{}).get('verified') is not True or
            cap['waitability'].get('worker_reset') is not True or cap['waitability'].get('probe_exit')!=73 or cap['waitability'].get('probe_wait_status')!=73<<8):
        raise ValueError('Verified actual-death/reap host cleanup required')
    native_cleanup=result.get('cleanup',{})
    if (native_cleanup.get('verified') is not True or native_cleanup.get('namespace')!=binding['owner'] or native_cleanup.get('errors')!=[] or
            any(native_cleanup.get(k)!=[] for k in ('remaining_containers','remaining_volumes','remaining_networks'))):
        raise ValueError('ERP fixture teardown must match the same owner')
    acceptance=dict(schema='osr-v06-native-candidate-acceptance/1',execution='verified-software-lifecycle',owner=binding['owner'],
        input_id=value['input_id'],identities=value['identities'],component_id=value['component_id'],run_binding_id=binding['binding_id'],
        source_sha256=source,erp_result_sha256=sha256(erp_raw).hexdigest(),supervisor_receipt_sha256=sha256(resource_raw).hexdigest(),
        docker_cleanup_verified=True,host_cleanup_verified=True,scope='Actual candidate-linked disposable software lifecycle; no physical railway release',**FLAGS)
    return dict(acceptance,acceptance_id=digest(acceptance))
