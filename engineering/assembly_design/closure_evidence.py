"""Consume original reviewed evidence at exact task/component/input revisions.

Trust comes from a separately controlled pinned-key register, never from an
evidence submission. Digital scope review, physical correlation and production
authority are independent. Generated checks alone cannot appoint a reviewer.
"""
from pathlib import Path
from engineering.twin_workflow import core
from . import acceptance

DATA=Path(__file__).parent/'data'
DIGITAL=('specification','interfaces','analysis','drawings','inspection-plan','assembly-process')


def task_contract(task,prepared,subjects):
    configuration=prepared['prototype']
    pilot={'WP03':'structural-bay','WP04':'service-cassette','WP05':'service-cassette',
           'WP06':'service-cassette','WP07':'viaduct-bay','WP08':'viaduct-bay'}.get(task['wp'])
    subject=subjects.get(pilot) if pilot else None
    if subject is None:
        subject=dict(component_id=pilot or configuration['id'],component_revision=None if pilot else configuration['revision'],
            interface_revision=None if pilot else configuration['revision'],serial=None,full_pilot_scope=False)
    categories=list(DIGITAL)
    if task['kind']=='software':categories.remove('drawings');categories.remove('assembly-process')
    if task['kind']=='external':categories=['specification','applicability-review']
    value=dict(schema='osr-task-completion-contract/1',task_id=task['id'],pilot=pilot,
        requirement=task['required_evidence'],required_categories=categories,
        component_id=subject['component_id'],component_revision=subject['component_revision'],
        interface_revision=subject['interface_revision'],prototype_revision=configuration['revision'],
        # The submission index contains signatures of this contract. Including
        # its own bytes would create an impossible self-referential signature.
        # All engineering inputs and the separately controlled trust pins stay
        # bound; index bytes are bound independently in the source epoch.
        input_revision=core.digest({name:digest for name,digest in prepared['source_sha256'].items()
            if name!='engineering/assembly_design/data/closure-evidence.json'}),
        physical_expected=task.get('physical_expected') or subject.get('physical_expected'),full_pilot_scope=subject.get('full_pilot_scope') is True,
        pilot_characteristics=subject.get('pilot_characteristics',{}),known_failures=subject.get('known_failures',[]),
        native_required=subject.get('native_required',False),native_state=subject.get('native_state'))
    value['revision']=core.digest(value);return value


def _digital(submission,contract,trust,root,today):
    authored=acceptance.signed(submission['author'],trust,'digital-evidence',today=today)
    review=acceptance.signed(submission['review'],trust,'digital-review',today=today)
    if submission['author']['key_id']==submission['review']['key_id']:
        raise ValueError('independent digital reviewer required')
    if not contract['component_revision'] or not contract['interface_revision']:
        raise ValueError('component/interface revision not yet defined')
    if authored.get('contract_revision')!=contract['revision'] or authored.get('task_id')!=contract['task_id']:
        raise ValueError('stale task/component/interface/input/requirement contract')
    if review.get('authored_sha256')!=acceptance.digest(authored) or review.get('contract_revision')!=contract['revision']:
        raise ValueError('review targets different evidence or contract')
    if review.get('decision') not in ('accepted-record','rejected','retest') or not review.get('reasons'):
        raise ValueError('explicit digital disposition and scope review required')
    artifacts=authored.get('artifacts',[])
    if not artifacts:raise ValueError('original digital artifacts required')
    for artifact in artifacts:
        acceptance._artifact(root,artifact)
        if artifact.get('category') not in contract['required_categories']:raise ValueError('unknown digital evidence category')
    coverage=authored.get('coverage',{})
    if set(coverage)!=set(contract['required_categories']):raise ValueError('complete frozen digital coverage required')
    if any(state not in ('passed','failed','held','skipped') for state in coverage.values()):raise ValueError('typed digital coverage required')
    if {a['category'] for a in artifacts}!=set(coverage):raise ValueError('coverage lacks original artifacts')
    if (contract['known_failures'] or contract['native_required'] and contract['native_state']=='failed'
        or 'failed' in coverage.values() or review['decision']=='rejected'):state='failed'
    elif contract['native_required'] and contract['native_state']!='passed':state='hold'
    elif review['decision']=='accepted-record' and all(s=='passed' for s in coverage.values()):state='passed'
    else:state='hold'
    return dict(state=state,coverage=coverage,authored_sha256=acceptance.digest(authored),
        review_sha256=acceptance.digest(review),review_key_id=submission['review']['key_id'],
        contract_revision=contract['revision'],receipt_verified=True)


def evaluate(tasks,prepared,*,subjects=None,index=None,trust=None,root=None,today=None):
    root=Path(root or core.ROOT);subjects=subjects or {}
    if index is None:index=prepared.get('completion_evidence') or core.read(DATA/'closure-evidence.json')
    if trust is None:trust=prepared['completion_trust'] if 'completion_trust' in prepared else core.read(DATA/'closure-trust.json')
    if index.get('schema')!='osr-closure-evidence-index/1':raise ValueError('controlled closure evidence index required')
    contracts={t['id']:task_contract(t,prepared,subjects) for t in tasks}
    evidence={key:[] for key in contracts};invalid=[]
    for position,submission in enumerate(index['submissions']):
        task_id=submission.get('task_id');level=submission.get('level')
        if task_id not in contracts or level not in ('digital','physical'):
            raise ValueError('registered task and digital/physical evidence level required')
        contract=contracts[task_id]
        submitted_revision=(submission.get('author',{}).get('payload',{}).get('contract_revision')
                            if level=='digital' else submission.get('contract_revision'))
        if submitted_revision and submitted_revision!=contract['revision']:
            historical=dict(task_id=task_id,level=level,index=position,state='stale',
                reason='Historical evidence targets a superseded task/component/input contract; preserved, excluded from current coverage')
            invalid.append(historical);evidence[task_id].append(historical);continue
        try:
            if level=='digital':result=_digital(submission,contract,trust,root,today)
            else:
                expected=contract['physical_expected']
                if not expected:raise ValueError('controlled physical serial/method/interface/standard not yet defined')
                if expected['unit_revision']!=contract['component_revision'] or expected['interface_revision']!=contract['interface_revision']:
                    raise ValueError('physical subject revision differs')
                if submission.get('contract_revision')!=contract['revision']:raise ValueError('stale physical completion contract')
                raw=acceptance.ingest(submission['record'],submission['calibration'],submission['review'],trust,root,expected,today=today)
                result=dict(state={'accepted-record':'passed','rejected':'failed','retest':'hold'}[raw['state']],
                    receipt_verified=True,contract_revision=contract['revision'],authenticated_record=raw)
            evidence[task_id].append(dict(level=level,**result))
        except (ValueError,KeyError,TypeError,FileNotFoundError) as exc:
            # Stale/tampered entries stay visible and block this task's gate.
            result=dict(task_id=task_id,level=level,index=position,reason=str(exc),state='invalid')
            invalid.append(result);evidence[task_id].append(result)
    states={};pilot_records={}
    for task_id,contract in contracts.items():
        rows=evidence[task_id]
        def state(level):
            values=[r['state'] for r in rows if r['level']==level and r['state']!='stale']
            if any(v in ('failed','invalid') for v in values):return 'failed' if 'failed' in values else 'stale-or-invalid'
            if not values and any(r['level']==level and r['state']=='stale' for r in rows):return 'stale-or-invalid'
            return 'complete-reviewed-records' if values and all(v=='passed' for v in values) else 'hold'
        digital,physical=state('digital'),state('physical')
        states[task_id]=dict(contract=contract,evidence=rows,digital_state=digital,physical_state=physical,
            digital_specification_complete=digital=='complete-reviewed-records',
            physical_validation_records_complete=physical=='complete-reviewed-records',
            engineering_evidence_complete=digital=='complete-reviewed-records' and physical=='complete-reviewed-records',
            manufacturing_release=False,
            engineering_exit=('evidence-complete; authority-release-open' if digital==physical=='complete-reviewed-records'
                else 'digital-complete; physical/release-open' if digital=='complete-reviewed-records' else 'open'))
        # Full-pilot coverage is never inferred from a cap cage or isolated bay.
        pilot_tasks=[c['task_id'] for c in contracts.values() if c['pilot']==contract['pilot']]
        all_pilot_tasks_pass=all(any(r.get('level')=='digital' and r.get('state')=='passed' for r in evidence[k]) and
            not any(r.get('state') in ('failed','invalid','hold') for r in evidence[k] if r.get('level')=='digital') for k in pilot_tasks)
        if contract['pilot'] and contract['full_pilot_scope'] and digital=='complete-reviewed-records' and all_pilot_tasks_pass:
            records=pilot_records.setdefault(contract['pilot'],{})
            for group,items in contract['pilot_characteristics'].items():
                if group=='physical' and physical!='complete-reviewed-records':continue
                for name in items:
                    current=records.setdefault(group,{}).get(name)
                    record=dict(revision=contract['component_revision'],receipt_verified=True,state='passed')
                    if current and current!=record:raise ValueError('conflicting pilot coverage revisions')
                    records[group][name]=record
    return dict(tasks=states,pilot_records=pilot_records,invalid_records=invalid,
        trust_revision=core.digest(trust),index_revision=core.digest(index),
        authority_scope='Reviewed evidence coverage only; no manufacturing or physical release authority',**core.FLAGS)


def export_raw(prepared,output,*,root=None):
    """Retain original referenced bytes; invalid submissions remain inspectable.

    The frozen baseline already contains signed envelopes and the operator's
    source-bound trust register. No key is inferred from an artifact/submission.
    """
    root=Path(root or core.ROOT).resolve();output=Path(output);output.mkdir()
    index=prepared.get('completion_evidence') or core.read(DATA/'closure-evidence.json')
    files={};omitted=[];total=0
    for submission in index['submissions']:
        if submission.get('level')=='digital':descriptors=submission.get('author',{}).get('payload',{}).get('artifacts',[])
        else:
            descriptors=submission.get('record',{}).get('payload',{}).get('raw_files',[])
            certificate=submission.get('calibration',{}).get('payload',{}).get('certificate')
            if certificate:descriptors=[*descriptors,certificate]
        for descriptor in descriptors:
            name=descriptor.get('path')
            if not isinstance(name,str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
                omitted.append(dict(path=name,reason='unsafe descriptor'));continue
            source=root/name
            if source.is_symlink() or not source.resolve().is_relative_to(root) or not source.is_file():
                omitted.append(dict(path=name,reason='missing or escaping artifact'));continue
            if name in files:continue
            total+=source.stat().st_size
            if total>16*1024**2:raise ValueError('closure original evidence exceeds portable budget')
            dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes());files[name]=core.sha(dest)
    core.write(output/'raw-manifest.json',dict(files_sha256=files,omitted=omitted,**core.FLAGS))


def verify_raw(folder):
    folder=Path(folder);manifest=core.read(folder/'raw-manifest.json')
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual!={'raw-manifest.json',*manifest['files_sha256']}:raise ValueError('closure original membership differs')
    for name,digest in manifest['files_sha256'].items():acceptance._artifact(folder,dict(path=name,sha256=digest))
