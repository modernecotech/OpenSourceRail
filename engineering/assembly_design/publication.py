"""Portable assembly evidence; displayed data must match sealed original results."""
from hashlib import sha256
from html import escape
from pathlib import Path
import gzip
import io
import json
import shutil
import tarfile

from engineering.twin_workflow import core
from engineering.design_delivery.pipeline import safe,archive_members
from . import workflow

MAX_BYTES=32*1024**2


def report(data,policy):
    h=lambda value:escape(str(value),quote=True)
    counts=data['counts'];lines=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Baghdad assembly design programme</title>',
        '<style>body{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:1rem;color:#18384c}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:.4rem;text-align:left}img{max-width:100%}code{overflow-wrap:anywhere}</style>',
        '<h1>Baghdad — sourced requirements and automatic assembly design</h1>',
        '<p>Provisional engineering development. No complete train, civil system, manufacturing qualification or physical release is claimed.</p>',
        '<p>'+h(counts['requirement_records'])+' scoped requirement records: '+h(counts['baghdad_records'])+' Baghdad reference parts plus '+h(counts['legacy_or_unreconciled_records'])+' legacy/unreconciled records. '+h(counts['facts'])+' sourced facts. '+h(counts['completed_trials'])+' completed trials; '+h(counts['qualified_components'])+' qualified components.</p>',
        '<p>'+h(data['controller_scope'])+'</p><p><a href="baseline.json.gz">Baseline and requirement inventory</a> | <a href="progress.json">Full progress and open work</a> | <a href="qualification.json">Executed test receipt</a> | <a href="tests.log">Test log</a> | <a href="evidence.tar.gz">Original evidence</a> | <a href="manifest.json">Checksums</a></p>']
    for c in data['selected']:
        base='models/'+c['kind']+'/'
        lines+=['<h2>'+h(c['kind'])+'</h2><p>Exact candidate <code>'+h(c['key'])+'</code>. Native state: '+h(c['native'])+'. '+h(c['scope'])+'</p>',
            '<p><a href="'+base+'candidate.json.gz">Part/joint definition</a> | <a href="'+base+'result.json">Checks and unresolved requirements</a> | <a href="'+base+'manufacturing-bom.csv">Manufacturing BOM and dimensions</a> | <a href="'+base+'qa-plan.json">Unexecuted QA plan</a></p>',
            '<img alt="Unissued inspection layout from generated definitions" src="'+base+'inspection.svg">']
        if c['native']=='completed':lines+=['<img alt="Retained native model, with purchased coordination envelopes" src="'+base+'overview.png"><p><a href="'+base+'model.FCStd">Native FreeCAD</a> | <a href="'+base+'model.step.gz">Compressed STEP</a> — correspondence/static overlap checks only; bought-out items may be coordination envelopes.</p>']
    lines+=['<h2>Evaluated alternatives</h2><table><tr><th>Family</th><th>Variables</th><th>State</th><th>Represented mass kg</th><th>Failed / held checks</th></tr>']
    for trial in data['trials']:lines+=['<tr><td>'+h(trial['kind'])+'</td><td>'+h(json.dumps(trial['variables'],sort_keys=True))+'</td><td>'+h(trial.get('state',trial['status']))+'</td><td>'+h(trial.get('mass_kg'))+'</td><td>'+h(', '.join(trial.get('failed_checks',[])+trial.get('held_checks',[])))+'</td></tr>']
    lines+=['</table><h2>Reference facts and applicability</h2><table><tr><th>Fact</th><th>Value / unit</th><th>Source and scope</th></tr>']
    for fact in policy['facts']:
        source=policy['sources'].get(fact['source']);reference='<a href="'+h(source['url'])+'">'+h(fact['source'])+'</a>' if source else h(fact['source'])
        lines+=['<tr><td>'+h(fact['id'])+'</td><td>'+h(json.dumps(fact['value']))+' '+h(fact['unit'])+'</td><td>'+reference+'; '+h(fact['locator'])+'; '+h(fact['applicability'])+'</td></tr>']
    lines+=['</table><h2>Open design work</h2>']
    for kind,needs in data['pilot_open_requirements'].items():lines+=['<h3>'+h(kind)+'</h3><ul>']+['<li>'+h(n)+'</li>' for n in needs]+['</ul>']
    lines+=['<p>'+h(counts['component_records_needing_adapter'])+' scoped component records still need component-specific generators/evaluators. Work orders retain all seven design/acceptance stages as open.</p></html>']
    return '\n'.join(lines)


def export(workspace,output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('new export directory required')
    with workflow.locked(workspace) as (workspace,db):
        epoch=core.read(workspace/'active.json')['epoch'];epoch_path=workspace/'epochs'/epoch;prepared=core.read(epoch_path/'baseline.json',maximum=30_000_000)
        data=workflow.summary(workspace,db,epoch,prepared);output.mkdir(parents=True)
        (output/'baseline.json.gz').write_bytes(gzip.compress((epoch_path/'baseline.json').read_bytes(),mtime=0))
        for name in ('qualification.json','tests.log','work-orders.json'):shutil.copyfile(epoch_path/name,output/name)
        folders={}
        for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND status='completed'",(epoch,)):
            workflow.verify_folder(row['folder']);folders[row['key']]=Path(row['folder'])
        for row in db.execute('SELECT n.* FROM native n JOIN jobs j ON j.key=n.child WHERE j.epoch=?',(epoch,)):
            if (Path(row['folder'])/'receipt.json').exists():workflow.verify_folder(row['folder']);folders[row['child']+'-native']=Path(row['folder'])
        raw=0;index={}
        with (output/'evidence.tar.gz').open('wb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as zipped,tarfile.open(fileobj=zipped,mode='w|') as archive:
            for key,folder in sorted(folders.items()):
                receipt=workflow.verify_folder(folder);index[key]=core.sha(folder/'receipt.json')
                for name in ('receipt.json',*sorted(receipt['files_sha256'])):
                    content=(folder/name).read_bytes();raw+=len(content)
                    if raw>128*1024**2:raise ValueError('assembly raw evidence budget exceeded')
                    info=tarfile.TarInfo(key+'/'+name);info.size=len(content);info.mtime=0;archive.addfile(info,io.BytesIO(content))
        for entry in data['selected']:
            row=db.execute('SELECT * FROM jobs WHERE key=?',(entry['key'],)).fetchone();destination=output/'models'/entry['kind'];destination.mkdir(parents=True)
            folder=Path(row['folder'])
            for name in ('candidate.json.gz','result.json','manufacturing-bom.csv','qa-plan.json','inspection.svg','netlist.json','controller.py','software-tests.json'):
                if (folder/name).exists():shutil.copyfile(folder/name,destination/name)
            if entry['native']=='completed':
                native=db.execute('SELECT * FROM native WHERE child=?',(entry['key'],)).fetchone();nf=Path(native['folder']);workflow.verify_folder(nf)
                shutil.copyfile(nf/'cad/candidate.FCStd',destination/'model.FCStd')
                (destination/'model.step.gz').write_bytes(gzip.compress((nf/'cad/candidate.step').read_bytes(),mtime=0))
                shutil.copyfile(nf/'result.json',destination/'native-result.json');shutil.copyfile(nf/'overview.png',destination/'overview.png')
        for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND kind='cassette-control' AND status='completed'",(epoch,)):
            destination=output/'software'/json.loads(row['variables'])['variant'];destination.mkdir(parents=True)
            for name in ('controller.py','result.json'):shutil.copyfile(Path(row['folder'])/name,destination/name)
        core.write(output/'progress.json',data);(output/'index.html').write_text(report(data,prepared['policy']))
        manifest=dict(schema='osr-assembly-publication/1',epoch=epoch,progress_digest=core.digest(data),evidence_receipts=index,
            files_sha256={p.relative_to(output).as_posix():core.sha(p) for p in output.rglob('*') if p.is_file()},**core.FLAGS)
        core.write(output/'manifest.json',manifest);verify(output)
        return manifest


def verify(output):
    output=Path(output).resolve();m=core.read(output/'manifest.json',maximum=20_000_000)
    if m['schema']!='osr-assembly-publication/1' or any(m.get(k) is not False for k in core.FLAGS):raise ValueError('assembly publication scope changed')
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if actual!={'manifest.json',*m['files_sha256']}:raise ValueError('unsealed assembly export')
    total=0
    for name,digest in m['files_sha256'].items():
        path=output/safe(name);total+=path.stat().st_size
        if path.is_symlink() or not path.resolve().is_relative_to(output) or core.sha(path)!=digest:raise ValueError('assembly export bytes changed')
    if total>MAX_BYTES:raise ValueError('assembly export budget exceeded')
    raw=gzip.decompress((output/'baseline.json.gz').read_bytes());prepared=json.loads(raw)
    if core.digest(prepared)!=m['epoch']:raise ValueError('assembly source epoch differs')
    q=core.read(output/'qualification.json',maximum=20_000_000)
    if not q['passed'] or q['sources']!=prepared['source_sha256'] or q['runtime_identity']!=prepared['runtime_identity'] or q['log_sha256']!=core.sha(output/'tests.log'):raise ValueError('assembly qualification differs')
    members=archive_members(output/'evidence.tar.gz');expected=set()
    for key,digest in m['evidence_receipts'].items():
        receipt_bytes=members[key+'/receipt.json'];receipt=json.loads(receipt_bytes)
        if sha256(receipt_bytes).hexdigest()!=digest or receipt['key']!=key or receipt['epoch']!=m['epoch']:raise ValueError('assembly receipt identity differs')
        expected.add(key+'/receipt.json')
        for name,digest in receipt['files_sha256'].items():
            path=key+'/'+safe(name);expected.add(path)
            if sha256(members[path]).hexdigest()!=digest:raise ValueError('archived assembly evidence changed')
        if any(receipt.get(k) is not False for k in core.FLAGS):raise ValueError('assembly receipt cannot grant release')
        if key.endswith('-native'):
            if receipt['child']+'-native'!=key:raise ValueError('native confirmation child differs')
        else:
            if receipt['baseline_sha256']!=sha256(raw).hexdigest() or core.digest(dict(epoch=m['epoch'],kind=receipt['kind'],variables=receipt['variables']))!=key:raise ValueError('assembly task identity differs')
    if set(members)!=expected:raise ValueError('unreceipted assembly evidence')
    data=core.read(output/'progress.json',maximum=20_000_000)
    if data['epoch']!=m['epoch'] or any(data.get(k) is not False for k in core.FLAGS) or data['counts']['qualified_components']!=0:raise ValueError('assembly progress scope differs')
    if data['source_sha256']!=prepared['source_sha256'] or core.read(output/'work-orders.json',maximum=20_000_000)!=workflow.work_orders(prepared):raise ValueError('requirement/work-order allocation differs')
    inv=prepared['inventory']
    expected_counts=dict(requirement_records=len(inv['items']),baghdad_records=inv['baghdad_reference_items'],legacy_or_unreconciled_records=inv['existing_items'],component_records_with_pilot=sum(i['pilot'] is not None for i in inv['items']),component_records_needing_adapter=sum(i['pilot'] is None for i in inv['items']),facts=len(prepared['policy']['facts']),completed_trials=sum(not k.endswith('-native') for k in m['evidence_receipts']),qualified_components=0)
    if data['counts']!=expected_counts:raise ValueError('displayed assembly counts differ from evidence')
    if {t['key'] for t in data['trials'] if t['status']=='completed'}!={k for k in m['evidence_receipts'] if not k.endswith('-native')}:raise ValueError('trial membership differs from evidence')
    for trial in data['trials']:
        if trial['status']!='completed':continue
        r=json.loads(members[trial['key']+'/result.json']);receipt=json.loads(members[trial['key']+'/receipt.json'])
        if trial['kind']!=receipt['kind'] or trial['variables']!=receipt['variables']:raise ValueError('exported trial differs from original')
        expected_fields=dict(state=r.get('state','offline-tests'),mass_kg=r.get('measurements',{}).get('mass_kg'),failed_checks=r.get('failed_checks',[]),held_checks=r.get('held_checks',[]))
        if any(trial.get(k)!=v for k,v in expected_fields.items()):raise ValueError('displayed trial differs from original')
        if trial['kind']=='cassette-control':
            folder=output/'software'/receipt['variables']['variant']
            for name in ('controller.py','result.json'):
                if (folder/name).read_bytes()!=members[trial['key']+'/'+name]:raise ValueError('exported software differs from original')
    for entry in data['selected']:
        key=entry['key'];folder=output/'models'/safe(entry['kind'])
        receipt=json.loads(members[key+'/receipt.json']);result=json.loads(members[key+'/result.json'])
        if entry['kind']!=receipt['kind'] or result['failed_checks'] or entry.get('design_complete') is not False or entry['scope']!='Provisional research representative; all assembly closure and qualification holds remain applicable':raise ValueError('selected assembly scope or eligibility differs')
        native_key=key+'-native/result.json'
        state=json.loads(members[native_key])['state'] if native_key in members else 'not-run'
        if state=='failed' or entry['native']!=('completed' if state=='passed' else state):raise ValueError('selected native eligibility differs')

        for name in ('candidate.json.gz','result.json','manufacturing-bom.csv','qa-plan.json','inspection.svg','netlist.json','controller.py','software-tests.json'):
            original=members.get(key+'/'+name)
            if original is not None and (folder/name).read_bytes()!=original:raise ValueError('exported assembly copy differs from original')
        if entry['native']=='completed':
            for name in ('native-result.json','overview.png'):
                original='result.json' if name=='native-result.json' else name
                if (folder/name).read_bytes()!=members[key+'-native/'+original]:raise ValueError('exported native record/picture differs from original')
            nr=json.loads(members[key+'-native/result.json'])
            if nr['child']!=key or nr['state']!='passed':raise ValueError('failed native evidence cannot support a selected confirmation')
            if (folder/'model.FCStd').read_bytes()!=members[key+'-native/cad/candidate.FCStd'] or gzip.decompress((folder/'model.step.gz').read_bytes())!=members[key+'-native/cad/candidate.step']:raise ValueError('exported native geometry differs from original')
    if core.digest(data)!=m['progress_digest']:raise ValueError('assembly progress digest differs')
    if (output/'index.html').read_text()!=report(data,prepared['policy']):raise ValueError('displayed assembly report differs from originals')
    return dict(verified=True,files=len(m['files_sha256']),evidence_jobs=len(m['evidence_receipts']),bytes=total,**core.FLAGS)
