"""Bounded candidate campaigns with immutable inputs and restartable workers."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import tomllib
import uuid

from . import contracts, families, registry, selection
from .storage import atomic_immutable, ImmutableConflict
from . import resource_limits

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'build/design-search'
ROLES = ('coordinator', 'magnetics', 'electrical', 'mechanical', 'civil', 'twin', 'service', 'verifier')
SCHEMA = 'osr-design-campaign/1'
COMPARISON_MAX_BYTES = 256*1024**2


def _write(path, value):
    from engineering.ferrite_maglev.workflow import write_json
    write_json(Path(path), value)


def _exclusive(path,value):
    try:return atomic_immutable(path,contracts.encoded(value))
    except ImmutableConflict as exc:raise registry.IdentityCollision(str(exc)) from exc


def _id(value):
    if not isinstance(value, str) or len(value) != 64 or any(ch not in '0123456789abcdef' for ch in value):
        raise ValueError('SHA256 campaign/candidate identity required')
    return value


def catalogue():
    from . import evaluators
    rows = evaluators.evaluator_catalogue()
    return {row['id']: row for row in rows}


def source_epoch():
    from . import evaluators
    paths = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
             for path in Path(__file__).parent.rglob('*.py') if 'tests' not in path.parts}
    for name in catalogue(): paths.update(evaluators.source_snapshot(name))
    return paths


def load_spec(path):
    spec = tomllib.loads(Path(path).read_text())
    if spec.get('schema') != SCHEMA or not spec.get('requirement_revision'):
        raise ValueError('versioned campaign and requirements required')
    budget = spec['budget']
    for name, maximum in (('max_candidates', 32), ('max_generations', 8), ('max_workers', 3),
                          ('job_timeout_s', 3600), ('total_runtime_s', 14400), ('memory_mb', 16384)):
        if type(budget.get(name)) is not int or not 1 <= budget[name] <= maximum:
            raise ValueError('bounded positive campaign budget required: ' + name)
    if budget['memory_mb'] < 256: raise ValueError('at least 256MB per numerical worker required')
    if spec.get('purpose') != 'next-experiment':
        raise ValueError('first campaign selects next experiments; integrated-baseline comparison is separate')
    available = catalogue()
    requested = spec['evaluators']
    if not requested or len(set(requested)) != len(requested) or any(name not in available for name in requested):
        raise ValueError('unique registered evaluator capabilities required')
    for name in requested:
        if not set(available[name].get('dependencies', [])) <= set(requested):
            raise ValueError('missing evaluator dependency')
    if not spec.get('requirement_ids') or not spec.get('policy', {}).get('objectives'):
        raise ValueError('requirement links and explicit selection policy required')
    contracts.encoded(spec)
    return spec


def create(spec_path, *, state=STATE):
    spec = load_spec(spec_path)
    before=source_epoch()
    candidates = families.initial_families(requirement_revision=spec['requirement_revision'])
    if len(candidates) > spec['budget']['max_candidates']: raise ValueError('initial family exceeds trial budget')
    epoch = source_epoch()
    if epoch!=before:raise ValueError('campaign sources changed during definition')
    contexts = [contracts.identity(candidate) for candidate in candidates]
    definition = dict(schema=SCHEMA, specification=spec, source_sha256=epoch,
        candidate_context_ids=contexts, physical_candidate_ids=[candidate['candidate_id'] for candidate in candidates],
        physical_accepted=False, engineering_accepted=False, configuration_adopted=False)
    definition['campaign_id'] = contracts.identity(definition)
    folder = Path(state) / 'campaigns' / definition['campaign_id']
    _exclusive(folder / 'definition.json', definition)
    store = registry.ImmutableRegistry(Path(state) / 'registry')
    for candidate, context in zip(candidates, contexts):
        store.store('candidate', candidate)
        _exclusive(folder / 'candidates' / (context + '.json'), candidate)
    tasks = [dict(role=role, campaign_id=definition['campaign_id'], requirement_revision=spec['requirement_revision'],
        parent_candidate_ids=definition['physical_candidate_ids'], engineering_question=question,
        allowed_variables=spec.get('allowed_variables', []), fixed_interfaces=spec.get('fixed_interfaces', []),
        required_artifacts=['candidate bundle or exact evaluator revision', 'result package', 'failure reasons'],
        trial_budget=spec['budget']['max_candidates'], runtime_budget_s=spec['budget']['total_runtime_s'],
        state='prepared-for-specialist', execution_is_not_physical_acceptance=True)
        for role, question in (
            ('magnetics', 'Explain net useful support and independent flux-map requirements.'),
            ('mechanical', 'Compare finite carrier geometry, added installed stock and removal paths.'),
            ('civil', 'Compare exact selected sections, moving stresses, deflection and erection scope.'),
            ('electrical', 'Identify current, cooling, power and repeated-duty consequences.'),
            ('service', 'Preserve six-car capacity context and expose service/cost consequences.'),
            ('twin', 'Compile one consistent selected research package.'),
            ('verifier', 'Independently check identities, stock arithmetic and reported failures.'))]
    _exclusive(folder / 'agent-tasks.json', tasks)
    return definition


def definition(campaign_id, *, state=STATE):
    path = Path(state) / 'campaigns' / _id(campaign_id) / 'definition.json'
    value = json.loads(path.read_bytes())
    check = {key: item for key, item in value.items() if key != 'campaign_id'}
    if value['campaign_id'] != campaign_id or contracts.identity(check) != campaign_id:
        raise ValueError('campaign definition identity differs')
    if value['source_sha256'] != source_epoch():
        raise ValueError('campaign implementation changed; create a new campaign instead of mixing revisions')
    return value


def sandbox_available():
    binary = shutil.which('bwrap')
    if not binary: return False
    result = subprocess.run([binary, '--ro-bind', '/', '/', '--proc', '/proc', '--dev', '/dev',
        '--unshare-net', '--unshare-pid', '--die-with-parent', '--', '/usr/bin/true'], capture_output=True, timeout=10)
    return result.returncode == 0


def _json(path,maximum=64*1024**2):
    path=Path(path)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents) or not path.is_file() or path.stat().st_size>maximum:
        raise ValueError('bounded ordinary JSON record required: '+str(path))
    return json.loads(path.read_bytes())


def _payload_hashes(attempt):
    hashes={};total=0
    for path in sorted(Path(attempt).rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):raise ValueError('ordinary attempt inventory required')
        if path.is_file() and path!=Path(attempt)/'attempt.json':
            size=path.stat().st_size;total+=size
            if size>64*1024**2 or total>256*1024**2:raise ValueError('worker package exceeds byte budget')
            hashes[path.relative_to(attempt).as_posix()]=sha256(path.read_bytes()).hexdigest()
    return hashes


def _terminal(execution_status):
    if execution_status in {'executed','refused'}:return 'completed'
    return 'interrupted' if execution_status=='interrupted' else 'tool-error'


def _seal(attempt,candidate,request,result,*,duration_s,sandbox,error=None,recovered=False):
    receipt=Path(attempt)/'output/resource-limits.json'
    resources=_json(receipt) if receipt.is_file() else {}
    actual_sandbox=bool(sandbox and resources)
    record=dict(state=_terminal(result['execution_status']),evaluation_id=request['evaluation_id'],candidate_id=candidate['candidate_id'],
        duration_s=duration_s,os_read_only_input_enforced=actual_sandbox,network_isolated=actual_sandbox,
        immutable_input_unchanged=error!='immutable worker input changed',resource_limits=resources,
        recovered_after_coordinator_interruption=recovered,error=error,
        result_file='output/failure.json' if (Path(attempt)/'output/failure.json').is_file() else 'output/result.json',
        result_sha256=result['result_sha256'],payload_sha256={})
    try:record['payload_sha256']=_payload_hashes(attempt);record['payload_inventory_valid']=True
    except ValueError:record['payload_inventory_valid']=False
    record['attempt_sha256']=contracts.identity(record);_exclusive(Path(attempt)/'attempt.json',record)
    return record


def _worker_command(inputs,outputs,budget,sandbox):
    command=[sys.executable,'-m','engineering.design_search.worker','--input',str(inputs/'job.json'),'--output',str(outputs/'result.json'),
        '--memory-mb',str(budget['memory_mb']),'--timeout-s',str(budget['job_timeout_s'])]
    if not sandbox:command+=['--parent-pid',str(os.getpid()),'--parent-start',str(resource_limits.process_start(os.getpid()))]
    if sandbox:
        command=['bwrap','--ro-bind','/','/','--proc','/proc','--dev','/dev','--unshare-net','--unshare-pid',
            '--die-with-parent','--tmpfs','/tmp','--ro-bind',str(ROOT),str(ROOT),
            '--ro-bind',str(inputs),str(inputs),'--bind',str(outputs),str(outputs),'--chdir',str(outputs),'--',*command]
    return command


def execute(candidate,request,attempt,budget,*,mode='evaluate',primary=None,sandbox=False):
    """One detached worker group, cleaned before any output is sealed."""
    attempt=Path(attempt).resolve();inputs=attempt/'input';outputs=attempt/'output'
    inputs.mkdir(parents=True);outputs.mkdir()
    descriptor=dict(candidate=candidate,request=request,mode=mode,primary=primary,
        worker_limits=dict(memory_mb=budget['memory_mb'],timeout_s=budget['job_timeout_s']))
    _exclusive(inputs/'job.json',descriptor);before=sha256((inputs/'job.json').read_bytes()).hexdigest()
    environment=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    started=time.monotonic();error=None;execution='error';process=None;token=None
    try:
        with (attempt/'stdout.txt').open('wb') as stdout,(attempt/'stderr.txt').open('wb') as stderr:
            command=_worker_command(inputs,outputs,budget,sandbox)
            process=subprocess.Popen(command,cwd=outputs,env=environment,
                stdout=stdout,stderr=stderr,start_new_session=True)
            token=resource_limits.process_start(process.pid)
            _exclusive(attempt/'launch.json',dict(pid=process.pid,start_token=token,coordinator_pid=os.getpid(),
                started_wall_s=time.time(),timeout_s=budget['job_timeout_s'],sandbox_requested=sandbox,command=command))
            try:
                code=process.wait(timeout=budget['job_timeout_s'])
                if code:raise RuntimeError('worker exit code '+str(code))
            finally:
                resource_limits.stop_group(process.pid,expected_start=token)
                process.wait(timeout=2)
        _resource_receipt(attempt,descriptor)
        result=contracts.validate_result(_json(outputs/'result.json'))
        if result['request']!=request:raise ValueError('worker result does not match the exact evaluation request')
        execution=result['execution_status']
        if execution not in {'executed','refused','interrupted','error'}:raise ValueError('worker returned a nonterminal execution state')
    except subprocess.TimeoutExpired:
        error='worker wall-clock budget exceeded';execution='interrupted'
    except (ValueError,RuntimeError,OSError,KeyError) as exc:
        error=str(exc);execution='error'
    finally:
        if process is not None:
            try:
                resource_limits.stop_group(process.pid,expected_start=token);process.wait(timeout=2)
            except (ValueError,RuntimeError,OSError,subprocess.TimeoutExpired) as exc:error='process-tree cleanup failed: '+str(exc);execution='error'
    if not (inputs/'job.json').is_file() or sha256((inputs/'job.json').read_bytes()).hexdigest()!=before:
        error='immutable worker input changed';execution='error'
    try:_payload_hashes(attempt)
    except ValueError as exc:error=str(exc);execution='error'
    if error is not None:
        result=contracts.make_result(request,execution_status=execution,numerical_status='unknown',screen_status='unknown',diagnostics=[error])
        _exclusive(outputs/'failure.json',result)
    record=_seal(attempt,candidate,request,result,duration_s=time.monotonic()-started,sandbox=sandbox,error=error)
    return result,record


def _resource_receipt(attempt,descriptor):
    value=_json(Path(attempt)/'output/resource-limits.json');limits=descriptor['worker_limits']
    if (value.get('memory_limit_bytes')!=limits['memory_mb']*1024**2 or value.get('file_limit_bytes')!=64*1024**2 or
            value.get('cpu_limit_s')!=max(1,__import__('math').ceil(limits['timeout_s']))+1 or value.get('limits_before_domain_import') is not True):
        raise ValueError('worker OS-limit receipt differs from declared resource budget')
    return value


def _validate_attempt(attempt,request):
    attempt=Path(attempt);record=_json(attempt/'attempt.json')
    if record.get('attempt_sha256')!=contracts.identity({key:value for key,value in record.items() if key!='attempt_sha256'}):raise ValueError('attempt receipt payload digest differs')
    if record['evaluation_id']!=request['evaluation_id'] or record['candidate_id']!=request['candidate_id']:raise ValueError('mixed attempt identity')
    if record.get('payload_inventory_valid') is not True or record['payload_sha256']!=_payload_hashes(attempt):raise ValueError('attempt payload bytes or inventory differ')
    descriptor=_json(attempt/'input/job.json');contracts.validate_candidate(descriptor['candidate'])
    if descriptor['request']!=request or descriptor['candidate']['candidate_id']!=request['candidate_id']:raise ValueError('attempt input context differs')
    name=record['result_file']
    if name not in {'output/result.json','output/failure.json'}:raise ValueError('ordinary attempt result path required')
    result=contracts.validate_result(_json(attempt/name))
    if record['state']=='completed' and record['resource_limits']!=_resource_receipt(attempt,descriptor):raise ValueError('attempt resource-limit evidence differs')
    if result['request']!=request or result['result_sha256']!=record['result_sha256'] or record['state']!=_terminal(result['execution_status']):raise ValueError('attempt/result state or context differs')
    return result,record


def _relative_attempt(state,name):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='campaigns':raise ValueError('owned campaign attempt path required')
    return Path(state)/path


def _cache_receipt(state,result,attempt,record):
    value=dict(schema='osr-design-cache-receipt/1',evaluation_id=result['evaluation_id'],result_sha256=result['result_sha256'],
        attempt_path=Path(attempt).resolve().relative_to(Path(state).resolve()).as_posix(),attempt_sha256=record['attempt_sha256'])
    value['receipt_sha256']=contracts.identity(value)
    _exclusive(Path(state)/'cache-receipts'/(result['evaluation_id']+'.json'),value)


def _store_result(store,state,result,attempt,record):
    if record['state']!='completed':raise ValueError('only completed scientific executions may enter result cache')
    _validate_attempt(attempt,result['request']);store.store('evaluation',result);_cache_receipt(state,result,attempt,record)


def _cached(store,state,request):
    result=store.cached(request)
    if result is None:return None
    path=Path(state)/'cache-receipts'/(request['evaluation_id']+'.json')
    if not path.is_file():
        # A coordinator can die between immutable result and cache-receipt writes.
        for receipt in sorted((Path(state)/'campaigns').glob('*/attempts/'+request['evaluation_id']+'/*/attempt.json')):
            found,record=_validate_attempt(receipt.parent,request)
            if found==result and record['state']=='completed':_cache_receipt(state,result,receipt.parent,record);break
        if not path.is_file():raise ValueError('cached result has no verified execution attempt')
    receipt=_json(path)
    if receipt.get('receipt_sha256')!=contracts.identity({key:value for key,value in receipt.items() if key!='receipt_sha256'}):raise ValueError('cache receipt digest differs')
    actual,record=_validate_attempt(_relative_attempt(state,receipt['attempt_path']),request)
    if (actual!=result or receipt['result_sha256']!=result['result_sha256'] or receipt['attempt_sha256']!=record['attempt_sha256'] or record['state']!='completed'):
        raise ValueError('cached result differs from its sealed execution')
    return result


def _recover(attempt,candidate,request):
    """Finish sealing a complete orphan result; incomplete outputs remain evidence."""
    attempt=Path(attempt)
    if (attempt/'attempt.json').is_file():return _validate_attempt(attempt,request)
    if not (attempt/'output/result.json').is_file() or not (attempt/'output/resource-limits.json').is_file():return None
    descriptor=_json(attempt/'input/job.json')
    if descriptor['request']!=request or descriptor['candidate']['candidate_id']!=candidate['candidate_id']:raise ValueError('orphan attempt context differs')
    launch=_json(attempt/'launch.json')
    resource_limits.stop_group(launch['pid'],expected_start=launch['start_token'])
    _resource_receipt(attempt,descriptor)
    result=contracts.validate_result(_json(attempt/'output/result.json'))
    if result['request']!=request or _terminal(result['execution_status'])!='completed':return None
    record=_seal(attempt,candidate,request,result,duration_s=None,sandbox=launch.get('sandbox_requested',False),recovered=True)
    return result,record


class _RuntimeBudget:
    def __init__(self,journal,definition,save):
        self.journal=journal;self.limit=definition['total_runtime_s'];self.save=save
        used=journal.get('runtime_used_s',0.)
        if type(used) not in (int,float) or not 0<=used<1e12:raise ValueError('finite persisted campaign runtime required')
        lease=journal.get('active_runtime_lease')
        if lease:
            reserved=lease['reserved_s']
            if type(reserved) not in (int,float) or not 0<reserved<=self.limit:raise ValueError('bounded persisted runtime lease required')
            used+=reserved;journal.setdefault('abandoned_runtime_leases',[]).append(dict(lease,charged_s=reserved))
        journal['active_runtime_lease']=None;self.base=float(used);self.started=time.monotonic();self.checkpoint()
    def remaining(self):return max(0.,self.limit-self.base-(time.monotonic()-self.started))
    def checkpoint(self):
        self.journal['runtime_used_s']=self.base+time.monotonic()-self.started;self.save()
    def reserve(self,timeout_s):
        remaining=self.remaining();timeout=min(timeout_s,int(remaining))
        if timeout<1:return None
        self.journal['active_runtime_lease']=dict(id=uuid.uuid4().hex,reserved_s=timeout,started_wall_s=time.time())
        self.checkpoint();return timeout
    def settle(self):self.journal['active_runtime_lease']=None;self.checkpoint()


def _baseline_policy(spec,results,confirmed):
    return dict(spec['policy'],critical_evaluators=list(spec['evaluators']),minimum_maturity='coupled-numerical',require_confirmation=True,
        required_confirmation_scope='independent-domain',confirmation_links={primary['evaluation_id']:[row['evaluation_id'] for row in confirmed
            if row['request']['settings'].get('confirmation_of')==primary['evaluation_id'] and row['request']['settings'].get('primary_result_sha256')==primary['result_sha256']] for primary in results})


def _candidate_membership(definition,candidates,contexts):
    spec=definition['specification']
    if (len(contexts)!=len(set(contexts)) or not set(definition['candidate_context_ids'])<=set(contexts)
            or len(contexts)>spec['budget']['max_candidates']
            or len({row['candidate_id'] for row in candidates})!=len(candidates)
            or any(row['requirement_revision']!=spec['requirement_revision'] for row in candidates)):
        raise ValueError('campaign candidate membership, requirements or trial budget differs')


def run(campaign_id,*,state=STATE,max_jobs=None):
    """Resume immutable contexts with cumulative budgets and recoverable attempts."""
    from engineering.ferrite_maglev.workflow import locked
    from . import evaluators,verification
    if max_jobs is not None and (type(max_jobs) is not int or max_jobs<1):raise ValueError('positive max_jobs required')
    campaign=definition(campaign_id,state=state);spec=campaign['specification'];folder=Path(state)/'campaigns'/campaign_id
    store=registry.ImmutableRegistry(Path(state)/'registry');budget=spec['budget'];completed=0
    with locked(folder):
        path=folder/'journal.json'
        journal=_json(path) if path.exists() else dict(schema='osr-digital-execution-graph/1',campaign_id=campaign_id,state='planned',candidate_context_ids=list(campaign['candidate_context_ids']),
            generations=[],jobs={},physical_requirement_dispositions_changed=False,physical_accepted=False)
        if journal['campaign_id']!=campaign_id or journal.get('physical_accepted') is not False or journal.get('physical_requirement_dispositions_changed') is not False:raise ValueError('mixed or accepted campaign journal')
        runtime=_RuntimeBudget(journal,budget,lambda:_write(path,journal));journal['state']='running'
        for job in journal['jobs'].values():
            if job['state']=='running':job['state']='interrupted'
        runtime.checkpoint();candidates=[]
        for context in journal['candidate_context_ids']:
            candidate=contracts.validate_candidate(_json(folder/'candidates'/(_id(context)+'.json')))
            if contracts.identity(candidate)!=context:raise ValueError('candidate context filename/content differs')
            candidates.append(candidate)
        _candidate_membership(campaign,candidates,journal['candidate_context_ids'])
        results={};available=catalogue()
        def stop(reason):
            journal['state']='interrupted';journal['stop_reason']=reason;runtime.settle();return journal
        def register(candidate,request,role):
            store.store('evaluation-request',request);key=request['evaluation_id']
            job=journal['jobs'].setdefault(key,dict(candidate_id=candidate['candidate_id'],evaluation_id=key,evaluator_id=request['evaluator_id'],purpose=request['purpose'],role=role,state='planned',attempts=[]))
            cached=_cached(store,state,request)
            if cached is not None:
                job['state']='completed'
                return cached
            for name in reversed(job['attempts']):
                attempt=folder/name
                recovered=_recover(attempt,candidate,request)
                if recovered is not None:
                    result,record=recovered;job.update(state=record['state'],last_attempt=record)
                    if record['state']=='completed':_store_result(store,state,result,attempt,record);return result
            return None
        def execute_batch(rows):
            nonlocal completed
            timeout=runtime.reserve(budget['job_timeout_s'])
            if timeout is None:return False
            try:
                with ThreadPoolExecutor(max_workers=len(rows)) as pool:
                    pending={}
                    for candidate,request,mode,primary,sandbox in rows:
                        key=request['evaluation_id'];attempt=folder/'attempts'/key/uuid.uuid4().hex;job=journal['jobs'][key]
                        job['state']='running';job['attempts'].append(attempt.relative_to(folder).as_posix())
                        pending[pool.submit(execute,candidate,request,attempt,dict(budget,job_timeout_s=timeout),mode=mode,primary=primary,sandbox=sandbox)]=(candidate,request,attempt)
                    runtime.checkpoint()
                    for future in as_completed(pending):
                        candidate,request,attempt=pending[future];result,record=future.result();completed+=1
                        journal['jobs'][request['evaluation_id']].update(state=record['state'],last_attempt=record)
                        if record['state']=='completed':_store_result(store,state,result,attempt,record);results[request['evaluation_id']]=result
                        runtime.checkpoint()
            finally:runtime.settle()
            if source_epoch()!=campaign['source_sha256']:raise ValueError('campaign sources changed during execution')
            return all(journal['jobs'][request['evaluation_id']]['state']=='completed' for _,request,_,_,_ in rows)
        try:
            for generation in range(budget['max_generations']):
                current=[c for c in candidates if c.get('lineage',{}).get('generation',0)==generation]
                if not current:break
                requests=[]
                for candidate in current:
                    for name in spec['evaluators']:
                        request=evaluators.request_for(candidate,name,purpose='diagnostic',hypothesis=spec.get('hypothesis',{}),scenario=spec.get('scenario',{}),
                            settings=dict(coupling_context_id=contracts.identity(dict(candidate_id=candidate['candidate_id'],requirements=spec['requirement_revision'],scenario=spec.get('scenario',{})))))
                        requests.append((candidate,request));cached=register(candidate,request,available[name].get('role',name))
                        if cached is not None:results[request['evaluation_id']]=cached;journal['jobs'][request['evaluation_id']]['state']='completed'
                pending=[(c,r) for c,r in requests if r['evaluation_id'] not in results]
                while pending:
                    if runtime.remaining()<1:return stop('campaign-runtime-budget-exhausted')
                    if max_jobs is not None and completed>=max_jobs:return stop('invocation-job-limit')
                    ready=[]
                    for candidate,request in pending:
                        names={row['request']['evaluator_id'] for row in results.values() if row['candidate_id']==candidate['candidate_id'] and row['purpose']!='confirmation'}
                        if set(available[request['evaluator_id']].get('dependencies',[]))<=names:ready.append((candidate,request))
                    if not ready:journal['state']='blocked-tool-dependency';runtime.settle();return journal
                    count=min(budget['max_workers'],len(ready),max_jobs-completed if max_jobs is not None else budget['max_workers'])
                    batch=ready[:count]
                    if not execute_batch([(c,r,'evaluate',None,False) for c,r in batch]):return stop('worker-interruption-or-tool-error')
                    finished={r['evaluation_id'] for c,r in batch};pending=[(c,r) for c,r in pending if r['evaluation_id'] not in finished]
                if generation+1<budget['max_generations']:
                    for candidate in current:
                        if len(candidates)>=budget['max_candidates']:break
                        revised=families.propose_revision(candidate,[r for r in results.values() if r['candidate_id']==candidate['candidate_id']],trial_index=generation)
                        if revised is None or any(c['candidate_id']==revised['candidate_id'] for c in candidates):continue
                        revised['lineage']['generation']=generation+1;context=contracts.identity(revised);store.store('candidate',revised)
                        _exclusive(folder/'candidates'/(context+'.json'),revised);journal['candidate_context_ids'].append(context);candidates.append(revised)
                entry=dict(generation=generation,candidate_ids=[c['candidate_id'] for c in current])
                journal['generations']=[r for r in journal['generations'] if r['generation']!=generation]+[entry];runtime.checkpoint()
            primary=[r for r in results.values() if r['purpose']!='confirmation']
            next_choice=selection.select(candidates,primary,purpose='next-experiment',policy=spec['policy']);store.store('selection',next_choice);confirmed=[]
            if next_choice['selected_candidate_id']:
                chosen=next(c for c in candidates if c['candidate_id']==next_choice['selected_candidate_id']);sandbox=sandbox_available()
                for original in primary:
                    if original['candidate_id']!=chosen['candidate_id']:continue
                    request=verification.request_for(chosen,original);cached=register(chosen,request,'verifier')
                    if cached is not None:confirmed.append(cached);continue
                    if runtime.remaining()<1:return stop('campaign-runtime-budget-exhausted')
                    if max_jobs is not None and completed>=max_jobs:return stop('invocation-job-limit')
                    if not execute_batch([(chosen,request,'verify',original,sandbox)]):return stop('verifier-interruption-or-tool-error')
                    confirmed.append(results[request['evaluation_id']])
            if source_epoch()!=campaign['source_sha256']:raise ValueError('campaign sources changed before publication')
            if any(job['state']!='completed' for job in journal['jobs'].values()):
                raise ValueError('campaign still contains unfinished digital jobs')
            baseline=selection.select(candidates,primary+confirmed,purpose='integrated-baseline',policy=_baseline_policy(spec,primary,confirmed));store.store('selection',baseline)
            comparison=dict(schema='osr-design-campaign-comparison/1',campaign_id=campaign_id,candidates=candidates,results=primary,confirmations=confirmed,
                next_experiment=next_choice,integrated_baseline=baseline,qualification=dict(linked_requirement_ids=spec['requirement_ids'],physical_accepted=False,dispositions_changed=False),**contracts.FLAGS)
            comparison['comparison_sha256']=contracts.identity(comparison);_write(folder/'comparison.json',comparison)
            journal.update(state='completed',next_experiment_selection_id=next_choice['selection_id'],integrated_baseline_selection_id=baseline['selection_id'],
                completed_engineering_failures=sum(r['screen_status']=='fail' for r in primary),unknown_screens=sum(r['screen_status']=='unknown' for r in primary))
            runtime.settle();return journal
        except BaseException:
            journal['state']='interrupted-tool-error';runtime.settle();raise


def compare(campaign_id,*,state=STATE):
    campaign=definition(campaign_id,state=state);folder=Path(state)/'campaigns'/campaign_id;spec=campaign['specification']
    value=_json(folder/'comparison.json',maximum=COMPARISON_MAX_BYTES);journal=_json(folder/'journal.json');store=registry.ImmutableRegistry(Path(state)/'registry')
    if (value.get('schema')!='osr-design-campaign-comparison/1' or value.get('campaign_id')!=campaign_id or journal['campaign_id']!=campaign_id or journal['state']!='completed' or
        value.get('comparison_sha256')!=contracts.identity({k:v for k,v in value.items() if k!='comparison_sha256'}) or any(value.get(flag) is not False for flag in contracts.FLAGS)):
        raise ValueError('campaign comparison identity/state differs')
    candidates=value['candidates'];contexts=[contracts.identity(contracts.validate_candidate(c)) for c in candidates]
    _candidate_membership(campaign,candidates,contexts)
    if contexts!=journal['candidate_context_ids']:raise ValueError('comparison candidate contexts differ from immutable campaign journal')
    for candidate,context in zip(candidates,contexts):
        if _json(folder/'candidates'/(context+'.json'))!=candidate or store.read_context(context)!=candidate:raise ValueError('comparison candidate registry/context differs')
    expected_qualification=dict(linked_requirement_ids=spec['requirement_ids'],physical_accepted=False,dispositions_changed=False)
    if value.get('qualification')!=expected_qualification or journal.get('physical_accepted') is not False or journal.get('physical_requirement_dispositions_changed') is not False:raise ValueError('campaign cannot alter physical requirement dispositions')
    results=value['results'];confirmed=value['confirmations']
    for result in results+confirmed:
        contracts.validate_result(result)
        if _cached(store,state,result['request'])!=result:raise ValueError('comparison result differs from sealed cache/attempt')
    expected={key for key,job in journal['jobs'].items() if job['state']=='completed'}
    if {r['evaluation_id'] for r in results+confirmed}!=expected or len(results+confirmed)!=len(expected):raise ValueError('comparison result inventory differs from journal')
    next_choice=selection.select(candidates,results,purpose='next-experiment',policy=spec['policy'])
    baseline=selection.select(candidates,results+confirmed,purpose='integrated-baseline',policy=_baseline_policy(spec,results,confirmed))
    if value['next_experiment']!=next_choice or value['integrated_baseline']!=baseline:raise ValueError('comparison selection differs from independent recomputation')
    if journal['next_experiment_selection_id']!=next_choice['selection_id'] or journal['integrated_baseline_selection_id']!=baseline['selection_id']:raise ValueError('journal selection identity differs')
    if source_epoch()!=campaign['source_sha256']:raise ValueError('campaign sources changed during comparison')
    return value
