"""Receipt-bound selection, whole-system completion ledger and portable evidence."""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import gzip
import io
import json
import sqlite3
import tarfile
import time

from engineering.twin_workflow import core
from engineering.continuous_design import service,eligibility,tasks,runtime

SCHEMA='osr-continuous-delivery/1'
MAX_BYTES=64*1024*1024
MAX_RAW=256*1024*1024
PHYSICAL={'mechanical-detail','mechanical-equipment-study','civil-kit-study'}
QUALIFICATION_TESTS=[
    'engineering/analysis/tests/'+name+'.py' for name in (
    'test_continuous_publication','test_process_expansion','test_civil_kit_delivery',
    'test_civil_construction_reliability','test_continuous_eligibility',
    'test_continuous_reliability','test_protocol_receiver','test_protocol_system')]
QUALIFICATION_TESTS+=['tools/automation/tests/test_design_progress.py']


def safe(name):
    if not isinstance(name,str):raise ValueError('unsafe package path')
    p=PurePosixPath(name)
    if not isinstance(name,str) or not name or p.is_absolute() or '..' in p.parts or p.as_posix()!=name:
        raise ValueError('unsafe package path')
    return name


def sources():
    values=service.source_snapshot()
    for path in [*Path(__file__).parent.glob('*.py'),core.ROOT/'tools/automation/design-publish.py',
                 core.ROOT/'tools/automation/design-progress.py',core.ROOT/'tools/automation/design-progress-mesh.py',
                 *(core.ROOT/name for name in QUALIFICATION_TESTS)]:
        values[path.relative_to(core.ROOT).as_posix()]=core.sha(path)
    return values


@contextmanager
def snapshot(workspace):
    workspace=Path(workspace).resolve();active=core.read(workspace/'active.json')
    db=sqlite3.connect((workspace/'queue.sqlite').as_uri()+'?mode=ro',uri=True,timeout=10)
    db.row_factory=sqlite3.Row;db.execute('BEGIN')
    try:
        store=SimpleNamespace(workspace=workspace,db=db,result=lambda row:service.Store.result(None,row))
        yield store,active
    finally:db.close()


def verified_job(store,row,baseline):
    folder=Path(row['folder']).resolve();epoch=store.workspace/'epochs'/baseline
    if row['baseline']!=baseline or row['status']!='completed' or not folder.is_relative_to(epoch.resolve()):
        raise ValueError('candidate outside its completed source epoch')
    result=store.result(row);receipt=core.read(folder/'receipt.json',maximum=20_000_000)
    task=json.loads(row['task'])
    if receipt['key']!=row['key'] or receipt['baseline_sha256']!=baseline or receipt['task']!=task:
        raise ValueError('candidate receipt identity differs')
    if tasks.identity(task,baseline)!=row['key'] or any(result.get(k) is not False for k in core.FLAGS):
        raise ValueError('candidate identity or release flags differ')
    for name in receipt['files_sha256']:safe(name)
    return result,receipt


def select(store,baseline):
    """Bounded representatives, never a failed/held candidate or old epoch."""
    resolver=eligibility.Resolver(store,baseline);choices={}
    rows=sorted(resolver.observations.values(),key=lambda r:(r['kind']!='integration-protocol',r['mass'] if r['mass'] is not None else float('inf'),r['key']))
    for observation in rows:
        kind=observation['kind']
        if kind not in PHYSICAL|{'software-logic','software-receiver','integration-protocol','integration-coupling'} or not observation['study_pass']:continue
        if kind in PHYSICAL and not observation['native_confirmed']:continue
        row=resolver.rows[observation['key']];task=json.loads(row['task']);state=resolver.state(row['key'])
        if not state['eligible'] or (kind in PHYSICAL and state['analytical_only']):continue
        if kind.startswith('integration-') and any(
            json.loads(resolver.rows[key]['task'])['kind'] in tasks.CONFIRMABLE and resolver.state(key)['analytical_only']
            for key in task['parameters'].get('children',[])):continue
        group=kind
        if kind=='civil-kit-study':
            v=task['parameters']['variables'];group=kind+'/'+v['architecture']+('/station' if v['station_package'] else '/bay')
        if kind.startswith('integration-'):group='integration'
        if group in choices:continue
        result,receipt=verified_job(store,row,baseline)
        confirmation=None
        if kind in PHYSICAL:
            candidates=[c for c in state['confirmations'] if c['state']=='passed']
            if not candidates:continue
            confirmation=resolver.rows[sorted(candidates,key=lambda c:c['key'])[-1]['key']]
            verified_job(store,confirmation,baseline)
        choices[group]=dict(row=dict(row),result=result,receipt=receipt,confirmation=dict(confirmation) if confirmation else None,
            group=group,kind=kind,task=task,eligibility=state)
    return list(choices.values()),resolver


def completion(graph,selected,needs):
    """Every authoritative item remains open until exact accepted evidence exists.

    Research result flags and package counts are never inferred as acceptance.
    No item-to-candidate mapping is invented from a vaguely similar title.
    """
    items=[dict(id=item['id'],title=item['title'],packages=item['package_ids'],
        required_detail_sections=item['required_detail_sections'],state='open',
        reason='Exact item-to-candidate allocation and accepted detail/verification evidence remain unbound') for item in graph['items']]
    packages=[dict(id=p['id'],domain=p['domain'],state='open',required_gates=p['required_gates'],
        completion_artifacts=p['completion_artifacts'],dependencies=p['dependencies']) for p in graph['packages']]
    kinds={c['kind'] for c in selected};families={c['group'] for c in selected}
    required={'mechanical-detail','mechanical-equipment-study','software-logic','software-receiver','integration'}
    required|={'civil-kit-study/'+a+'/bay' for a in ('large-span','segmental','light-ribbed')}
    required.add('civil-kit-study/large-span/station')
    return dict(schema='osr-completion-ledger/1',items=items,packages=packages,open_needs=needs,
        missing_research_representatives=sorted(required-families),
        accepted_components=0,required_components=len(items),required_packages=len(packages),
        state='provisional-research-package',
        release_gates=['Accepted six-car Baghdad loads, duty and site/ground baseline',
            'Complete revision-bound component/interface allocation and detailed drawings',
            'Qualified materials/processes, connections, fatigue, soil, dynamics and staged resistance',
            'Exact full-system integration, software target timing and SIL/HIL/physical correlation',
            'Authenticated supplier/first-article/installed acceptance and independent design authority'],**core.FLAGS)


def identity(choices,binding):
    return core.digest(dict(baseline=binding['baseline_sha256'],sources=sources(),
        selected=[dict(group=c['group'],key=c['row']['key'],receipt=c['row']['receipt_sha'],
            confirmation=c['confirmation']['receipt_sha'] if c['confirmation'] else None) for c in choices]))


def inspect(workspace):
    with snapshot(workspace) as (store,active):
        binding=core.read(store.workspace/'epochs'/active['baseline_sha256']/'baseline.json')
        if not service.unchanged(binding['source_sha256']):raise ValueError('runner source epoch is stale')
        if runtime.digest(runtime.capture())!=runtime.digest(binding['runtime_identity']):raise ValueError('runner numerical runtime changed')
        choices,resolver=select(store,active['baseline_sha256'])
        needs=[dict(r) for r in store.db.execute("SELECT lane,item_id,required FROM needs WHERE baseline=? AND state='open' ORDER BY lane,item_id LIMIT 256",(active['baseline_sha256'],))]
        graph=json.loads(gzip.decompress((core.PACKET/'specifications.json.gz').read_bytes()))
        ledger=completion(graph,choices,needs)
        return dict(active=active,binding=binding,choices=choices,ledger=ledger,signature=identity(choices,binding))


def archive_jobs(store,baseline,choices,destination):
    rows={};pending=[c['row']['key'] for c in choices]+[c['confirmation']['key'] for c in choices if c['confirmation']]
    while pending:
        key=pending.pop()
        if key in rows:continue
        if len(rows)>=32:raise ValueError('evidence dependency budget exceeded')
        row=store.db.execute('SELECT * FROM jobs WHERE key=?',(key,)).fetchone();result,receipt=verified_job(store,row,baseline)
        rows[key]=(row,result,receipt);task=json.loads(row['task']);pending+=task.get('parameters',{}).get('children',[])
        if task['kind'] in tasks.CONFIRMABLE:
            pending += [r[0] for r in store.db.execute("SELECT key FROM jobs WHERE baseline=? AND status='completed' AND json_extract(task,'$.parameters.child')=? AND json_extract(task,'$.kind') LIKE '%-confirmation'",(baseline,key))]
        if task['kind'].endswith('-confirmation'):pending.append(task['parameters']['child'])
    raw=0;index={}
    with destination.open('wb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as zipped,tarfile.open(fileobj=zipped,mode='w|') as tar:
        for key,(row,result,receipt) in sorted(rows.items()):
            folder=Path(row['folder']);names=['receipt.json',*sorted(receipt['files_sha256'])]
            for name in names:
                safe(name);path=(folder/name).resolve()
                if not path.is_relative_to(folder.resolve()) or path.is_symlink():raise ValueError('evidence path escape')
                data=path.read_bytes();raw+=len(data)
                if raw>MAX_RAW:raise ValueError('uncompressed evidence budget exceeded')
                info=tarfile.TarInfo(key+'/'+name);info.size=len(data);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(data))
            index[key]=dict(receipt_sha256=row['receipt_sha'],task=json.loads(row['task']))
    if destination.stat().st_size>MAX_BYTES:raise ValueError('compressed evidence budget exceeded')
    return index


def archive_members(path):
    members={};size=0
    with tarfile.open(path,'r:gz') as tar:
        for entry in tar:
            safe(entry.name)
            if not entry.isfile() or entry.name in members:raise ValueError('non-file or duplicate evidence member')
            size+=entry.size
            if size>MAX_RAW or len(members)>8192:raise ValueError('evidence expansion budget exceeded')
            members[entry.name]=tar.extractfile(entry).read()
    return members


def verify(package,*,media=False):
    package=Path(package).resolve();m=core.read(package/'manifest.json',maximum=20_000_000)
    if m['schema']!=SCHEMA or any(m.get(k) is not False for k in core.FLAGS):raise ValueError('publication release/scope changed')
    actual={p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
    if actual!={'manifest.json',*m['files_sha256']}:raise ValueError('unsealed or missing package member')
    size=0
    for name,digest in m['files_sha256'].items():
        path=package/safe(name)
        if path.is_symlink() or not path.resolve().is_relative_to(package) or core.sha(path)!=digest:raise ValueError('package artifact changed: '+name)
        size+=path.stat().st_size
    if size>MAX_BYTES:raise ValueError('publication size budget exceeded')
    binding=core.read(package/'baseline.json',maximum=20_000_000)
    if core.digest(dict(sources=binding['source_sha256'],runtime=binding['runtime_identity']))!=m['baseline']:
        raise ValueError('portable source/runtime epoch differs')
    qualification=core.read(package/'qualification.json',maximum=20_000_000)
    if not qualification['passed'] or qualification['sources']!=m['publisher_sources'] or qualification['log_sha256']!=core.sha(package/'tests.log'):
        raise ValueError('publication qualification differs')
    members=archive_members(package/'evidence.tar.gz');expected=set()
    for key,record in m['jobs'].items():
        prefix=key+'/';receipt_bytes=members[prefix+'receipt.json'];receipt=json.loads(receipt_bytes)
        if sha256(receipt_bytes).hexdigest()!=record['receipt_sha256'] or receipt['key']!=key or receipt['task']!=record['task'] or receipt['baseline_sha256']!=m['baseline']:
            raise ValueError('archived receipt identity differs')
        if tasks.identity(receipt['task'],m['baseline'])!=key:raise ValueError('archived task identity differs')
        expected.add(prefix+'receipt.json')
        for name,digest in receipt['files_sha256'].items():
            name=prefix+safe(name);expected.add(name)
            if sha256(members[name]).hexdigest()!=digest:raise ValueError('archived evidence changed')
        result=json.loads(members[prefix+'result.json'])
        if any(result.get(k) is not False for k in core.FLAGS):raise ValueError('archived result release changed')
        if result.get('runtime_sha256')!=runtime.digest(binding['runtime_identity']):raise ValueError('archived runtime differs')
    if set(members)!=expected:raise ValueError('unreceipted archived evidence')
    ledger=core.read(package/'completion.json',maximum=20_000_000)
    if ledger['accepted_components']!=0 or ledger['design_complete'] is not False:raise ValueError('unsupported completion claim')
    selected=core.read(package/'selection.json',maximum=20_000_000)
    for candidate in selected:
        key=candidate['key'];record=m['jobs'][key];result=json.loads(members[key+'/result.json'])
        if candidate['task']!=record['task'] or candidate['receipt_sha256']!=record['receipt_sha256'] or not result['study_pass']:
            raise ValueError('selected candidate evidence differs')
        if candidate['kind'] in PHYSICAL:
            confirmation=candidate['confirmation_key'];task=m['jobs'][confirmation]['task']
            if task['parameters']['child']!=key:raise ValueError('native confirmation targets another candidate')
            checked=json.loads(members[confirmation+'/result.json'])
            if not checked['study_pass'] or any(checked['verification']['levels'].get(level,{}).get('state')!='passed' for level in eligibility.MANDATORY):
                raise ValueError('selected native/numerical evidence is incomplete')
            folder=package/'models'/safe(candidate['id']);visual=candidate['visualisation']
            if core.sha(folder/'model.FCStd')!=visual['cad_sha256'] or core.sha(folder/'sequence.json')!=visual['sequence_sha256']:
                raise ValueError('visualisation native/sequence inputs differ')
            common=candidate['kind']!='mechanical-detail';raw_prefix=confirmation+'/output/'
            definition='physical-contract.json' if common else 'model-definition.json'
            cad_name='candidate.FCStd' if common else 'model.FCStd'
            if sha256(members[raw_prefix+'cad/'+cad_name]).hexdigest()!=visual['cad_sha256'] or sha256(members[raw_prefix+definition]).hexdigest()!=visual['native_definition_sha256']:
                raise ValueError('published geometry differs from archived native evidence')
            step_names=sorted(n for n in members if n.startswith(raw_prefix+'cad/') and n.endswith('.step'))
            if not step_names or gzip.decompress((folder/'model.step.gz').read_bytes())!=members[step_names[0]]:
                raise ValueError('published STEP differs from archived interchange')
            # Rebuild only the event description from the archived planning
            # inputs. No geometry regeneration or physics solver is invoked.
            import tempfile
            from . import visuals
            with tempfile.TemporaryDirectory(prefix='osr-sequence-verify-') as temporary:
                temporary=Path(temporary);(temporary/'output').mkdir()
                for name in ('civil-kit.json','delivery-schedule.json','delivery-tasks.json','operation-graph.json'):
                    original=key+'/output/'+name
                    if original in members:(temporary/'output'/name).write_bytes(members[original])
                expected_plan=visuals.sequence(dict(kind=candidate['kind'],row={'folder':str(temporary)}),json.loads(members[raw_prefix+definition]))
            if core.digest(expected_plan)!=core.digest(core.read(folder/'sequence.json',maximum=20_000_000)):
                raise ValueError('published sequence differs from archived evaluated events')
            if visual['motion_path_verified'] is not False or visual['physical_release'] is not False:raise ValueError('unsupported animation acceptance')
            if media:
                import subprocess
                subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(folder/safe(visual['video'])),'-f','null','-'],check=True,capture_output=True,timeout=60)
    return dict(verified=True,files=len(m['files_sha256']),jobs=len(m['jobs']),bytes=size,design_complete=False)


def build(workspace,output,qualification):
    from . import visuals
    output=Path(output).resolve()
    if output.exists():raise ValueError('new publication output directory required')
    prepared=inspect(workspace);before=sources();q=core.read(qualification,maximum=20_000_000)
    if not q['passed'] or q['sources']!=before:raise ValueError('passing exact-source publication qualification required')
    if q['log_sha256']!=core.sha(Path(qualification).with_name('tests.log')):raise ValueError('qualification log changed')
    output.mkdir(parents=True);core.write(output/'baseline.json',prepared['binding']);core.write(output/'completion.json',prepared['ledger'])
    core.write(output/'qualification.json',q);(output/'tests.log').write_bytes(Path(qualification).with_name('tests.log').read_bytes())
    with snapshot(workspace) as (store,active):
        if active!=prepared['active']:raise ValueError('source epoch changed during publication')
        resolver=eligibility.Resolver(store,active['baseline_sha256'])
        if not all(resolver.state(c['row']['key'])['eligible'] for c in prepared['choices']):raise ValueError('selected evidence eligibility changed')
        jobs=archive_jobs(store,active['baseline_sha256'],prepared['choices'],output/'evidence.tar.gz')
    selected=[]
    for i,c in enumerate(prepared['choices']):
        name=c['group'].replace('/','-');folder=output/'models'/name;folder.mkdir(parents=True)
        entry=dict(id=name,group=c['group'],kind=c['kind'],task=c['task'],key=c['row']['key'],
            receipt_sha256=c['row']['receipt_sha'],metrics=c['result'].get('metrics',{}),scope=c['result'].get('scope'),
            verification=c['result'].get('verification'),outstanding=c['result'].get('open_evidence',c['result'].get('needs',[])),
            confirmation_key=c['confirmation']['key'] if c['confirmation'] else None)
        if c['kind'] in PHYSICAL:entry['visualisation']=visuals.generate(c,folder)
        core.write(folder/'result.json',c['result'])
        original=Path(c['row']['folder'])/'output'
        for source_name in ('generated-controller.py','generated-receiver.py','manufacturing-units.csv'):
            if (original/source_name).is_file():(folder/source_name).write_bytes((original/source_name).read_bytes())
        for source_name in ('delivery-schedule.json','qa-travellers.json'):
            if (original/source_name).is_file():(folder/(source_name+'.gz')).write_bytes(gzip.compress((original/source_name).read_bytes(),mtime=0))
        if c['kind'].startswith('software-'):visuals.software(c,folder)
        core.write(folder/'summary.json',entry);selected.append(entry)
    core.write(output/'selection.json',selected)
    if sources()!=before or inspect(workspace)['signature']!=prepared['signature']:raise ValueError('sources or selected evidence changed during publication')
    visuals.report(output,selected,prepared['ledger'])
    manifest=dict(schema=SCHEMA,created_unix=time.time(),baseline=prepared['active']['baseline_sha256'],signature=prepared['signature'],
        publisher_sources=before,jobs=jobs,files_sha256={p.relative_to(output).as_posix():core.sha(p) for p in sorted(output.rglob('*')) if p.is_file()},**core.FLAGS)
    core.write(output/'manifest.json',manifest,exclusive=True);verify(output,media=True)
    return manifest
