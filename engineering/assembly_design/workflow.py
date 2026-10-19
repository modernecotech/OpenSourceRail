"""Durable, bounded assembly experiments driven by sourced Baghdad requirements."""
from contextlib import contextmanager
from hashlib import sha256
from html import escape
from pathlib import Path
import csv
import fcntl
import gzip
import io
import json
import itertools
import os
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import time

from engineering.twin_workflow import core
from engineering.continuous_design import study_confirmation
from engineering.design_delivery.pipeline import safe,archive_members
from . import baseline,models,evaluate,numerical_runtime as runtime

DEFAULT=Path.home()/'.local/state/opensourcerail/assembly-design'
TEST='engineering/analysis/tests/test_assembly_design.py'
MAX_WORKSPACE=2*1024**3
RESERVE=20*1024**3


def qualify(workspace):
    workspace=Path(workspace).resolve();before=baseline.sources();identity=runtime.capture();key=core.digest(dict(sources=before,runtime=identity));folder=workspace/'qualifications'/key
    folder.mkdir(parents=True,exist_ok=True)
    tests=[TEST,*sorted(str(p.relative_to(core.ROOT)) for p in (core.ROOT/'engineering/analysis/tests').glob('test_closure_*.py'))]
    command=[sys.executable,'-m','pytest',*tests,'-q']
    call=subprocess.run(command,cwd=core.ROOT,capture_output=True,text=True,timeout=600,
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONPATH':str(core.ROOT)+':'+str(core.ROOT/'design/component-catalogue/src')})
    (folder/'tests.log').write_text(call.stdout+call.stderr)
    receipt=dict(schema='osr-assembly-qualification/1',sources=before,runtime_identity=identity,command=command,returncode=call.returncode,
        passed=call.returncode==0 and before==baseline.sources() and identity==runtime.capture(),log_sha256=core.sha(folder/'tests.log'),tested_unix=time.time(),source_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=core.ROOT,check=True,capture_output=True,text=True).stdout.strip(),**core.FLAGS)
    core.write(folder/'qualification.json',receipt)
    # A zero exit code with skipped required native checks is not qualification.
    if ' skipped' in call.stdout:
        receipt['passed']=False;core.write(folder/'qualification.json',receipt)
    if not receipt['passed']:raise ValueError('assembly qualification failed or required check skipped: '+str(folder/'tests.log'))
    return folder/'qualification.json'


def qualification(workspace):
    key=core.digest(dict(sources=baseline.sources(),runtime=runtime.capture()));path=Path(workspace)/'qualifications'/key/'qualification.json'
    q=core.read(path,maximum=20_000_000)
    if not q['passed'] or q['sources']!=baseline.sources() or q['runtime_identity']!=runtime.capture() or q['log_sha256']!=core.sha(path.with_name('tests.log')):raise ValueError('exact-source assembly qualification required')
    return path,q


@contextmanager
def locked(workspace):
    workspace=Path(workspace).resolve();workspace.mkdir(parents=True,exist_ok=True)
    with (workspace/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        db=sqlite3.connect(workspace/'queue.sqlite',timeout=30);db.row_factory=sqlite3.Row
        db.executescript('''CREATE TABLE IF NOT EXISTS jobs(key TEXT PRIMARY KEY,epoch TEXT,kind TEXT,variables TEXT,status TEXT DEFAULT 'queued',attempts INTEGER DEFAULT 0,folder TEXT,error TEXT);
            CREATE TABLE IF NOT EXISTS native(child TEXT PRIMARY KEY,status TEXT,folder TEXT,error TEXT);
            CREATE TABLE IF NOT EXISTS events(at REAL,kind TEXT,payload TEXT);''')
        try:yield workspace,db
        finally:db.close()


def initialise(workspace,db):
    path,q=qualification(workspace);prepared=baseline.build();prepared['runtime_identity']=runtime.capture();epoch=core.digest(prepared)
    folder=workspace/'epochs'/epoch;folder.mkdir(parents=True,exist_ok=True)
    if not (folder/'baseline.json').exists():
        core.write(folder/'baseline.json',prepared,exclusive=True)
        core.write(folder/'qualification.json',q,exclusive=True);(folder/'tests.log').write_bytes(path.with_name('tests.log').read_bytes())
        orders=work_orders(prepared)
        core.write(folder/'work-orders.json',orders)
    core.write(workspace/'active.json',dict(epoch=epoch,qualification=str(path),**core.FLAGS))
    with db:
        for kind in prepared['policy']['pilots']:
            for variables in models.candidates(prepared['policy'],kind):
                key=core.digest(dict(epoch=epoch,kind=kind,variables=variables))
                db.execute('INSERT OR IGNORE INTO jobs(key,epoch,kind,variables) VALUES(?,?,?,?)',(key,epoch,kind,json.dumps(variables,sort_keys=True)))
        for variant in ('branch','bitmask'):
            variables={'variant':variant};key=core.digest(dict(epoch=epoch,kind='cassette-control',variables=variables))
            db.execute('INSERT OR IGNORE INTO jobs(key,epoch,kind,variables) VALUES(?,?,?,?)',(key,epoch,'cassette-control',json.dumps(variables)))
    return epoch,prepared


def work_orders(prepared):
    from . import closure
    orders=[]
    for item in prepared['inventory']['items']:
        orders.append(dict(item_id=item['id'],architecture=item['architecture'],source=item['source'],source_sha256=item['source_sha256'],
            pilot=item['pilot'],adopted_fact_ids=item['adopted_fact_ids'],
            stages={k:'open' for k in ('requirements','parts-and-connections','manufacturing','independent-analysis','system-integration','physical-correlation','acceptance')},
            next_action='execute available assembly generator and screens' if item['pilot'] else 'develop component-specific generator/evaluator from exact source records',
            expected_evidence=item['required_detail_sections'],state='open',**core.FLAGS))
        if prepared.get('closure_plan'):
            orders[-1]['closure_task_ids']=closure.tasks_for(item,prepared['closure_plan'])
    return orders


def seal(folder,identity):
    if (folder/'receipt.json').exists():raise ValueError('immutable receipt already exists')
    record=dict(**identity,files_sha256={p.relative_to(folder).as_posix():core.sha(p) for p in sorted(folder.rglob('*')) if p.is_file()},**core.FLAGS)
    core.write(folder/'receipt.json',record,exclusive=True);return record


def verify_folder(folder,expected=None):
    folder=Path(folder);receipt=core.read(folder/'receipt.json',maximum=20_000_000)
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual!={'receipt.json',*receipt['files_sha256']}:raise ValueError('unsealed experiment file')
    for name,digest in receipt['files_sha256'].items():
        p=folder/safe(name)
        if p.is_symlink() or not p.resolve().is_relative_to(folder.resolve()) or core.sha(p)!=digest:raise ValueError('changed experiment evidence')
    if any(receipt.get(k) is not False for k in core.FLAGS):raise ValueError('unsupported experiment release')
    if expected and any(receipt.get(k)!=v for k,v in expected.items()):raise ValueError('experiment receipt identity differs')
    return receipt


def tables(candidate,folder):
    rows=[]
    for part in candidate['contract']['parts']:
        rows.append(dict(id=part['id'],revision=part['revision'],quantity=1,material=part['material'],mass_kg=part['properties']['mass_kg'],
            geometric_role=part['geometric_role'],process=part['process_route'],supplier_part=(part.get('procurement') or {}).get('part'),
            tolerance_m=part['manufacturing_limits']['tolerance_m'],primitives_json=json.dumps(part['manufacturing']['primitives'],sort_keys=True),
            placement_json=json.dumps(part['placement'],sort_keys=True),joint_ids=';'.join(part['joints']),inspection=';'.join(part['inspection_characteristics'])))
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (folder/'manufacturing-bom.csv').write_text(stream.getvalue())
    # Dimensioned XY inspection layout from the same primitives; purchase
    # envelopes are orange. This is not an issued detail drawing.
    primitives=[(p,b) for p in candidate['contract']['parts'] for b in p['manufacturing']['primitives'] if b['kind'] in {'box','plate','perforated-plate'}]
    def world(part,point):
        return [sum(part['placement']['rotation'][i][j]*point[j] for j in range(3))+part['placement']['translation_m'][i] for i in range(3)]
    def bounds(part,b):
        corners=[world(part,[b['centre_m'][i]+sign[i]*b['dimensions_m'][i]/2 for i in range(3)]) for sign in itertools.product((-1,1),repeat=3)]
        return [min(c[i] for c in corners) for i in range(2)],[max(c[i] for c in corners) for i in range(2)]
    envelopes=[bounds(part,b) for part,b in primitives];xs=[p[0] for pair in envelopes for p in pair];ys=[p[1] for pair in envelopes for p in pair]
    scale=700/max(max(xs)-min(xs),max(ys)-min(ys));cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620"><rect width="900" height="620" fill="#f5f7fa"/>',
        '<text x="35" y="35" font-family="sans-serif" font-size="20">'+escape(candidate['kind'])+' — unissued XY inspection layout</text>']
    for part,b in primitives:
        lo,hi=bounds(part,b);x,y=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2;L,W=hi[0]-lo[0],hi[1]-lo[1];color='#d58c43' if part['geometric_role']=='supplier-coordination-envelope' else '#46748c'
        svg.append(f'<rect x="{450+(x-L/2-cx)*scale:.3f}" y="{300-(y+W/2-cy)*scale:.3f}" width="{L*scale:.3f}" height="{W*scale:.3f}" fill="none" stroke="{color}"><title>'+escape(part['id'])+'</title></rect>')
        if abs(part['placement']['rotation'][2][2])>.999:
            for hx,hy in b.get('holes_xy_m',[]):
                point=world(part,[b['centre_m'][0]+hx,b['centre_m'][1]+hy,b['centre_m'][2]])
                svg.append(f'<circle cx="{450+(point[0]-cx)*scale:.3f}" cy="{300-(point[1]-cy)*scale:.3f}" r="{b["hole_radius_m"]*scale:.3f}" fill="none" stroke="#b34e41"/>')
    svg+=['<text x="35" y="550" font-family="sans-serif">Overall XY: %.1f × %.1f mm; primitive/hole dimensions and datums in manufacturing-bom.csv</text>'%((max(xs)-min(xs))*1000,(max(ys)-min(ys))*1000),
        '<text x="35" y="580" font-family="sans-serif">Box/plate XY projection; cylinders/wires and drilled axes in CAD/BOM. Unissued, provisional.</text></svg>']
    (folder/'inspection.svg').write_text('\n'.join(svg))


def execute(workspace,db,epoch,prepared,row):
    attempt=row['attempts']+1;folder=workspace/'epochs'/epoch/'attempts'/row['key']/str(attempt);folder.mkdir(parents=True,exist_ok=False)
    with db:db.execute("UPDATE jobs SET status='running',attempts=?,folder=?,error=NULL WHERE key=?",(attempt,str(folder),row['key']))
    try:
        variables=json.loads(row['variables']);kind=row['kind']
        if kind=='cassette-control':
            source=evaluate.control_source(variables['variant']);(folder/'controller.py').write_text(source)
            result=evaluate.control_trial(variables['variant']);core.write(folder/'result.json',result)
        else:
            candidate=models.build(prepared['policy'],kind,variables);result=evaluate.evaluate(prepared['policy'],candidate)
            (folder/'candidate.json.gz').write_bytes(gzip.compress(core.encoded(candidate),mtime=0));core.write(folder/'result.json',result)
            tables(candidate,folder);core.write(folder/'qa-plan.json',candidate['qa_plan'])
            if kind=='service-cassette':
                from . import cassette_system
                system=result['supplemental_evidence']['cassette-system']
                cassette_system.verify_report(prepared['policy'],candidate,system)
                core.write(folder/'cassette-system.json',system)
                core.write(folder/'netlist.json',candidate['metadata']['netlist']);(folder/'controller.py').write_text(evaluate.control_source('branch'))
                core.write(folder/'software-tests.json',evaluate.control_trial())
        if prepared['source_sha256']!=baseline.sources():raise ValueError('design sources changed during execution')
        seal(folder,dict(key=row['key'],epoch=epoch,kind=kind,variables=variables,baseline_sha256=core.sha(workspace/'epochs'/epoch/'baseline.json')))
        with db:db.execute("UPDATE jobs SET status='completed' WHERE key=?",(row['key'],))
    except Exception as exc:
        with db:db.execute("UPDATE jobs SET status='error',error=? WHERE key=?",(str(exc)[:2000],row['key']))
        raise


def recover(db,epoch):
    for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND status='running'",(epoch,)).fetchall():
        try:verify_folder(row['folder'],dict(key=row['key'],epoch=epoch,kind=row['kind'],variables=json.loads(row['variables'])));status='completed';error=None
        except (ValueError,OSError):status='queued' if row['attempts']<2 else 'error';error='interrupted; partial attempt preserved'
        with db:db.execute('UPDATE jobs SET status=?,error=? WHERE key=?',(status,error,row['key']))


def representatives(db,epoch):
    groups={}
    for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND status='completed' AND kind!='cassette-control'",(epoch,)):
        verify_folder(row['folder']);r=core.read(Path(row['folder'])/'result.json');native=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
        if r['failed_checks'] or (native and native['status']=='failed'):continue
        rank=(len(r['held_checks']),r['measurements']['mass_kg'],row['key'])
        if row['kind'] not in groups or rank<groups[row['kind']][0]:groups[row['kind']]=(rank,dict(row))
    return [r for _,r in groups.values()]


DIAGNOSTIC_SCOPE='Excluded diagnostic exhibit; known mandatory failure or failed native geometry; never a research or integration shortlist'


def diagnostics(db,epoch):
    """Retain one bounded failure exhibit for families with no eligible representative."""
    represented={r['kind'] for r in representatives(db,epoch)};groups={}
    for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND status='completed' AND kind!='cassette-control'",(epoch,)):
        if row['kind'] in represented:continue
        verify_folder(row['folder']);r=core.read(Path(row['folder'])/'result.json')
        n=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
        if not r['failed_checks'] and not (n and n['status']=='failed'):continue
        rank=(len(r['failed_checks']),len(r['held_checks']),r['measurements']['mass_kg'],row['key'])
        if row['kind'] not in groups or rank<groups[row['kind']][0]:groups[row['kind']]=(rank,dict(row))
    return [r for _,r in groups.values()]


def confirm(workspace,db,epoch,row):
    existing=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
    if existing:
        if existing['status']=='completed':verify_folder(existing['folder'])
        return
    folder=workspace/'epochs'/epoch/'native'/row['key']
    if folder.exists():
        if (folder/'receipt.json').exists():
            verify_folder(folder)
            state=core.read(folder/'result.json')['state']
            with db:db.execute('INSERT INTO native VALUES(?,?,?,?)',(row['key'],'completed' if state=='passed' else state,str(folder),None))
            return
        # Interrupted native output stays as evidence; one bounded retry.
        previous=folder.with_name(folder.name+'-interrupted')
        if previous.exists():
            with db:db.execute('INSERT INTO native VALUES(?,?,?,?)',(row['key'],'hold',str(folder),'native interrupted twice; inspect retained attempts'))
            return
        folder.rename(previous)
    folder.mkdir(parents=True);candidate=json.loads(gzip.decompress((Path(row['folder'])/'candidate.json.gz').read_bytes()));core.write(folder/'definition.json',candidate['contract'])
    proof,state,error=study_confirmation.native(folder/'definition.json',folder/'cad')
    if state=='passed':
        from . import bim
        bim.export(candidate,folder/'cad/candidate.FCStd',folder/'bim')
        from .presentation import preview
        preview(folder/'cad/candidate.FCStd',folder/'overview.png',row['kind'])
    result=dict(child=row['key'],state=state,error=error,proof=proof,
        scope='Native correspondence, static material-overlap screen and reopen only; purchased envelopes, moving paths and resistance remain unqualified',**core.FLAGS)
    core.write(folder/'result.json',result);seal(folder,dict(key=row['key']+'-native',child=row['key'],epoch=epoch))
    with db:db.execute('INSERT INTO native VALUES(?,?,?,?)',(row['key'],'completed' if state=='passed' else state,str(folder),error))


def summary(workspace,db,epoch,prepared):
    rows=[]
    for row in db.execute('SELECT * FROM jobs WHERE epoch=? ORDER BY kind,key',(epoch,)):
        item={k:row[k] for k in ('key','kind','status','error')};item['variables']=json.loads(row['variables'])
        if row['status']=='completed':
            verify_folder(row['folder']);r=core.read(Path(row['folder'])/'result.json')
            item.update(state=r.get('state','offline-tests'),mass_kg=r.get('measurements',{}).get('mass_kg'),failed_checks=r.get('failed_checks',[]),held_checks=r.get('held_checks',[]))
        rows.append(item)
    selected=[]
    for row in representatives(db,epoch):
        n=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
        selected.append(dict(key=row['key'],kind=row['kind'],native=n['status'] if n else 'not-run',
            design_complete=False,scope='Provisional research representative; all assembly closure and qualification holds remain applicable'))
    diagnostic_entries=[]
    for row in diagnostics(db,epoch):
        n=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
        diagnostic_entries.append(dict(key=row['key'],kind=row['kind'],native=n['status'] if n else 'not-run',
            design_complete=False,selection_eligible=False,scope=DIAGNOSTIC_SCOPE))
    inventory=prepared['inventory'];remaining=sum(i['pilot'] is None for i in inventory['items'])
    report=dict(schema='osr-assembly-progress/1',epoch=epoch,source_sha256=prepared['source_sha256'],trials=rows,selected=selected,diagnostics=diagnostic_entries,
        counts=dict(requirement_records=len(inventory['items']),baghdad_records=inventory['baghdad_reference_items'],legacy_or_unreconciled_records=inventory['existing_items'],
            component_records_with_pilot=sum(i['pilot'] is not None for i in inventory['items']),component_records_needing_adapter=remaining,
            facts=len(prepared['policy']['facts']),completed_trials=sum(r['status']=='completed' for r in rows),qualified_components=0),
        unresolved=prepared['policy']['external_holds'],pilot_open_requirements={k:v['holds'] for k,v in prepared['policy']['pilots'].items()},
        controller_scope='Automatic parameter/design generation and scoped verification for registered provisional pilot families plus executable cassette software; remaining families require generator/evaluator development',**core.FLAGS)
    if prepared.get('closure_plan'):
        from . import closure,families
        report['closure']=closure.snapshot(prepared)
        report['families']=families.registry(prepared['policy'])
    if prepared.get('site'):
        from . import site_bundle
        report['site_summary']=site_bundle.metrics(prepared['site'])
    companion=workspace/'epochs'/epoch/'closure-studies'
    if companion.exists():
        from . import design_studies
        executed=design_studies.verify(companion,prepared)
        report['additional_design_studies']=dict(revision=core.digest(executed),models=executed['models'],
            duty_cases=len(executed['duty_cases']),scope='Additional provisional detail and coupled duty; full PDF engineering exits remain open')
    return report


def run(workspace=DEFAULT,*,budget=6,native=True):
    if type(budget) is not int or not 1<=budget<=64:raise ValueError('cycle budget must be 1..64')
    with locked(workspace) as (workspace,db):
        epoch,prepared=initialise(workspace,db);recover(db,epoch)
        mode='running';executed=0
        for _ in range(budget):
            if core._size(workspace)>=MAX_WORKSPACE or shutil.disk_usage(workspace).free<RESERVE:mode='waiting-for-disk';break
            row=db.execute("SELECT j.* FROM jobs j WHERE j.epoch=? AND j.status='queued' ORDER BY (SELECT COUNT(*) FROM jobs k WHERE k.epoch=j.epoch AND k.kind=j.kind AND k.status='completed'),j.kind,j.key LIMIT 1",(epoch,)).fetchone()
            if row is None:mode='waiting-for-new-requirements-or-capabilities';break
            execute(workspace,db,epoch,prepared,row);executed+=1
        if native and mode!='waiting-for-disk':
            for row in [*representatives(db,epoch),*diagnostics(db,epoch)]:
                if core._size(workspace)>=MAX_WORKSPACE or shutil.disk_usage(workspace).free<RESERVE:mode='waiting-for-disk';break
                confirm(workspace,db,epoch,row)
            if prepared.get('closure_plan') and mode!='waiting-for-disk' and not db.execute(
                    "SELECT 1 FROM jobs WHERE epoch=? AND status!='completed' LIMIT 1",(epoch,)).fetchone():
                from . import design_studies
                design_studies.run(workspace,epoch,prepared)
        report=summary(workspace,db,epoch,prepared);report.update(controller_state=mode,executed_this_cycle=executed,heartbeat_unix=time.time())
        core.write(workspace/'status.json',report)
        return report
