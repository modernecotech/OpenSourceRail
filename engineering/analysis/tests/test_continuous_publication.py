"""Publication must preserve exact evidence and never promote research to release."""
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path
import sqlite3
import tarfile

import pytest

from engineering.twin_workflow import core
from engineering.continuous_design import service,tasks,eligibility,operation_graph,runtime
from engineering.design_delivery import pipeline,visuals,automation
from engineering.analysis.tests.test_continuous_planning import FRAME


def completed(store,baseline,value,*,passed=True,native=False,mass=100,observe=True):
    key=tasks.identity(value,baseline);folder=store.workspace/'epochs'/baseline/'attempts'/key/'001';folder.mkdir(parents=True)
    result=dict(study_pass=passed,runtime_sha256=runtime.digest({'fixture':True}),metrics={'mass_kg':mass},verification=dict(levels={name:dict(state='passed' if passed else 'failed') for name in eligibility.MANDATORY}),**core.FLAGS)
    core.write(folder/'result.json',result)
    receipt=dict(key=key,baseline_sha256=baseline,task=value,files_sha256={'result.json':core.sha(folder/'result.json')})
    core.write(folder/'receipt.json',receipt)
    store.db.execute('INSERT INTO jobs(key,baseline,lane,task,status,created,finished,folder,receipt_sha) VALUES(?,?,?,?,?,?,?,?,?)',
        (key,baseline,'mechanical',json.dumps(value),'completed',1,2,str(folder),core.sha(folder/'receipt.json')))
    if observe:store.db.execute('''INSERT INTO observations(key,baseline,lane,kind,context,concept,study_pass,level,mass,objectives,failures,native_confirmed,finished)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(key,baseline,'mechanical',value['kind'],'metro','fixture',int(passed),'analytical_screening',mass,'{}','[]',int(native),2))
    store.db.commit();return store.db.execute('SELECT * FROM jobs WHERE key=?',(key,)).fetchone()


def physical(store,baseline='a'*64,*,pitch=1.8,native=True,mass=100):
    value=tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,crossbearer_pitch_m=pitch)))
    row=completed(store,baseline,value,native=native,mass=mass)
    if native:completed(store,baseline,tasks.task('mechanical-confirmation',dict(child=row['key'])),observe=False)
    return row


def test_selection_requires_native_and_uses_next_eligible_after_failure(tmp_path):
    store=service.Store(tmp_path);unconfirmed=physical(store,native=False,pitch=.6,mass=1)
    failed=physical(store,pitch=1.2,mass=2);alternative=physical(store,pitch=1.8,mass=3)
    # A second applicable confirmation with a distinct identity fails. The
    # selector must not rely on the original passing analytical/native flags.
    value=tasks.task('mechanical-confirmation',dict(child=failed['key']),rationale='same identity')
    row=store.db.execute("SELECT * FROM jobs WHERE json_extract(task,'$.parameters.child')=?",(failed['key'],)).fetchone()
    f=Path(row['folder']);result=core.read(f/'result.json');result['study_pass']=False;result['verification']['levels']['native_geometry']['state']='failed';core.write(f/'result.json',result)
    receipt=core.read(f/'receipt.json');receipt['files_sha256']['result.json']=core.sha(f/'result.json');core.write(f/'receipt.json',receipt)
    with store.db:store.db.execute('UPDATE jobs SET receipt_sha=? WHERE key=?',(core.sha(f/'receipt.json'),row['key']))
    selected,_=pipeline.select(store,'a'*64)
    assert [c['row']['key'] for c in selected]==[alternative['key']]
    store.db.close()


def test_old_epoch_and_tampered_artifacts_are_not_publishable(tmp_path):
    store=service.Store(tmp_path);old=physical(store,'b'*64);current=physical(store)
    with pytest.raises(ValueError,match='epoch'):pipeline.verified_job(store,old,'a'*64)
    (Path(current['folder'])/'result.json').write_text('{}')
    selected,_=pipeline.select(store,'a'*64);assert not selected
    store.db.close()


def test_completion_does_not_infer_component_acceptance_from_passing_counts():
    graph=dict(items=[dict(id='bogie',title='Bogie',package_ids=['vehicle'],required_detail_sections=['fatigue','joints'])],
        packages=[dict(id='vehicle',domain='mechanical',required_gates={'physical':['test']},completion_artifacts=['drawings'],dependencies=[])])
    record=pipeline.completion(graph,[{'kind':k,'group':k} for k in ('mechanical-detail','software-logic')],[])
    assert record['accepted_components']==0 and record['items'][0]['state']=='open'
    assert record['design_complete'] is False and 'integration' in record['missing_research_representatives']


@pytest.mark.parametrize('name',['../secret','/absolute','a/../../b','a//b','./a'])
def test_archive_path_escape_is_rejected(name):
    with pytest.raises(ValueError):pipeline.safe(name)


def test_archive_rejects_symlinks_and_duplicate_members(tmp_path):
    for link in (True,False):
        path=tmp_path/('link.tar.gz' if link else 'duplicate.tar.gz')
        with tarfile.open(path,'w:gz') as tar:
            t=tarfile.TarInfo('same');t.size=1
            if link:t.type=tarfile.SYMTYPE;t.linkname='/etc/passwd';t.size=0;tar.addfile(t)
            else:tar.addfile(t,io.BytesIO(b'a'));tar.addfile(t,io.BytesIO(b'b'))
        with pytest.raises(ValueError):pipeline.archive_members(path)


def test_archive_expansion_is_bounded(tmp_path,monkeypatch):
    path=tmp_path/'large.tar.gz'
    with tarfile.open(path,'w:gz') as tar:
        t=tarfile.TarInfo('large');t.size=100;tar.addfile(t,io.BytesIO(b'x'*100))
    monkeypatch.setattr(pipeline,'MAX_RAW',10)
    with pytest.raises(ValueError,match='budget'):pipeline.archive_members(path)


def test_archive_preserves_original_receipt_and_all_retained_bytes(tmp_path):
    store=service.Store(tmp_path/'workspace');row=physical(store)
    selected,_=pipeline.select(store,'a'*64);archive=tmp_path/'evidence.tar.gz'
    index=pipeline.archive_jobs(store,'a'*64,selected,archive);members=pipeline.archive_members(archive)
    assert len(index)==2 and members[row['key']+'/result.json']==(Path(row['folder'])/'result.json').read_bytes()
    assert core.digest(json.loads(members[row['key']+'/receipt.json']))==core.digest(core.read(Path(row['folder'])/'receipt.json'))
    store.db.close()


def portable_fixture(tmp_path):
    package=tmp_path/'package';package.mkdir();binding=dict(source_sha256={'fixture.py':'f'*64},runtime_identity={'fixture':True})
    baseline=core.digest(dict(sources=binding['source_sha256'],runtime=binding['runtime_identity']));binding['baseline_sha256']=baseline
    store=service.Store(tmp_path/'workspace');row=completed(store,baseline,tasks.task('software-logic',dict(expression='train_stopped')))
    choices,_=pipeline.select(store,baseline);jobs=pipeline.archive_jobs(store,baseline,choices,package/'evidence.tar.gz')
    core.write(package/'baseline.json',binding);core.write(package/'completion.json',dict(accepted_components=0,**core.FLAGS))
    (package/'tests.log').write_text('synthetic unit-test fixture only; no engineering evidence\n')
    source={'fixture.py':'f'*64};core.write(package/'qualification.json',dict(passed=True,sources=source,log_sha256=core.sha(package/'tests.log')))
    core.write(package/'selection.json',[dict(key=row['key'],kind='software-logic',task=json.loads(row['task']),receipt_sha256=row['receipt_sha'])])
    manifest=dict(schema=pipeline.SCHEMA,baseline=baseline,jobs=jobs,publisher_sources=source,**core.FLAGS)
    reseal(package,manifest);store.db.close();return package


def reseal(package,manifest=None):
    manifest=manifest or core.read(package/'manifest.json')
    manifest['files_sha256']={p.relative_to(package).as_posix():core.sha(p) for p in package.rglob('*') if p.is_file() and p.name!='manifest.json'}
    core.write(package/'manifest.json',manifest)


def test_portable_package_verifies_without_original_workspace(tmp_path):
    package=portable_fixture(tmp_path)
    import shutil
    shutil.rmtree(tmp_path/'workspace')
    assert pipeline.verify(package)['verified']


def test_deep_archive_tampering_is_detected_even_after_outer_reseal(tmp_path):
    package=portable_fixture(tmp_path);members=pipeline.archive_members(package/'evidence.tar.gz')
    name=next(n for n in members if n.endswith('/result.json'));record=json.loads(members[name]);record['study_pass']=False;members[name]=json.dumps(record).encode()
    with tarfile.open(package/'evidence.tar.gz','w:gz') as tar:
        for name,data in members.items():
            t=tarfile.TarInfo(name);t.size=len(data);tar.addfile(t,io.BytesIO(data))
    reseal(package)
    with pytest.raises(ValueError,match='archived evidence changed'):pipeline.verify(package)


def test_publication_cannot_claim_acceptance_or_unqualified_test_source(tmp_path):
    package=portable_fixture(tmp_path);record=core.read(package/'completion.json');record['accepted_components']=1;core.write(package/'completion.json',record);reseal(package)
    with pytest.raises(ValueError,match='completion'):pipeline.verify(package)
    record['accepted_components']=0;core.write(package/'completion.json',record)
    q=core.read(package/'qualification.json');q['sources']={'different.py':'a'*64};core.write(package/'qualification.json',q);reseal(package)
    with pytest.raises(ValueError,match='qualification'):pipeline.verify(package)


def test_unsealed_files_missing_files_and_package_budget_veto(tmp_path,monkeypatch):
    package=portable_fixture(tmp_path);(package/'extra.txt').write_text('unsealed')
    with pytest.raises(ValueError,match='member'):pipeline.verify(package)
    (package/'extra.txt').unlink();monkeypatch.setattr(pipeline,'MAX_BYTES',1)
    with pytest.raises(ValueError,match='budget'):pipeline.verify(package)


def test_assembly_sequence_is_derived_from_evaluated_graph_and_rejects_missing_lock(tmp_path):
    folder=tmp_path/'output';folder.mkdir();parts=[dict(id='part',mass_kg=10.,bounds_m=[[0.,0.,0.],[1.,1.,1.]])]
    graph=operation_graph.simple(parts);core.write(folder/'operation-graph.json',graph)
    choice=dict(kind='mechanical-equipment-study',row={'folder':str(tmp_path)})
    sequence=visuals.sequence(choice,dict(parts=parts))
    assert sequence['kind']=='assembly-sequence' and sequence['events'][-1]['visible_parts']==['part']
    assert not sequence['motion_path_verified']
    graph['operations']=[r for r in graph['operations'] if r['id']!='join-0']
    for r in graph['operations']:r['after']=[i for i in r['after'] if i!='join-0']
    core.write(folder/'operation-graph.json',graph)
    with pytest.raises(ValueError):visuals.sequence(choice,dict(parts=parts))


def test_missing_assembly_graph_is_labelled_inspection_not_assembly(tmp_path):
    (tmp_path/'output').mkdir()
    seq=visuals.sequence(dict(kind='mechanical-detail',row={'folder':str(tmp_path)}),dict(parts=[{'id':'part'}]))
    assert seq['kind']=='geometry-inspection' and not seq['collision_simulation']


def test_git_publication_refuses_dirty_repository_without_staging_other_work(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,'verify',lambda package:True)
    calls=[]
    def fake(repo,*args):
        calls.append(args)
        return 'main' if args==('rev-parse','--abbrev-ref','HEAD') else 'head' if args==('rev-parse','HEAD') else ' M unrelated.py'
    monkeypatch.setattr(automation,'git',fake)
    with pytest.raises(ValueError,match='unrelated'):automation.commit_package(tmp_path,tmp_path/'stage',expected_head='head')
    assert not any('add' in c or 'commit' in c or 'push' in c for c in calls)


def test_commit_refuses_stale_head(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,'verify',lambda package:True)
    monkeypatch.setattr(automation,'git',lambda repo,*args:'main' if args==('rev-parse','--abbrev-ref','HEAD') else 'new-head')
    with pytest.raises(ValueError,match='changed'):automation.commit_package(tmp_path,tmp_path/'stage',expected_head='old-head')


def test_family_coverage_preserves_lane_cap_and_old_epochs(tmp_path):
    store=service.Store(tmp_path);baseline='a'*64;core.write(tmp_path/'active.json',dict(baseline_sha256=baseline))
    with store.db:
        for i in range(64):
            store.db.execute('INSERT INTO jobs(key,baseline,lane,task,status,created,priority) VALUES(?,?,?,?,?,?,?)',
                (f'other-{i}',baseline,'civil',json.dumps({'kind':'civil-architecture-study'}),'queued',1,10))
        for key,b in (('starved',baseline),('old-epoch','b'*64)):
            store.db.execute('INSERT INTO jobs(key,baseline,lane,task,status,created,priority) VALUES(?,?,?,?,?,?,?)',
                (key,b,'civil',json.dumps({'kind':'civil-kit-study'}),'deferred',0,10))
    result=automation.maintain(tmp_path,now=10000)
    assert result['deleted_jobs']==0 and result['prioritised']==2
    assert store.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND status IN ('queued','running')",(baseline,)).fetchone()[0]==64
    assert store.db.execute("SELECT status,priority FROM jobs WHERE key='starved'").fetchone()[:]==('queued',-45)
    assert store.db.execute("SELECT status,priority FROM jobs WHERE key='old-epoch'").fetchone()[:]==('deferred',10)
    assert store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]==66
    assert automation.maintain(tmp_path,now=10001)['prioritised']==0
    store.db.close()


def test_scheduled_publisher_is_bounded_and_pushes_only_qualified_package(tmp_path):
    import importlib.util
    path=core.ROOT/'tools/automation/design-publish.py';spec=importlib.util.spec_from_file_location('delivery_cli',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    units=module.unit_text(tmp_path/'100% workspace',tmp_path/'qualification.json')
    assert 'OnCalendar=daily' in units['osr-design-publication.timer']
    assert 'OnUnitActiveSec=15min' in units['osr-design-coverage.timer']
    assert '100%% workspace' in units['osr-design-publication.service'] and '--push' in units['osr-design-publication.service']
    assert 'MemoryMax=2G' in units['osr-design-publication.service'] and 'TimeoutStartSec=30min' in units['osr-design-publication.service']


def test_real_native_short_video_and_units(tmp_path):
    import shutil,subprocess
    from engineering.continuous_design import civil_kit,construction_stage,delivery_simulation,study_confirmation
    if not shutil.which('ffmpeg'):pytest.skip('ffmpeg unavailable')
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:pytest.skip('native FreeCAD unavailable')
    kit=civil_kit.build(civil_kit.defaults());child=tmp_path/'child';out=child/'output';out.mkdir(parents=True)
    core.write(out/'civil-kit.json',kit);rows=construction_stage.tasks(kit);s=delivery_simulation.schedule(rows,kit['basis']['capacities'])
    core.write(out/'delivery-tasks.json',rows);core.write(out/'delivery-schedule.json',s)
    confirm=tmp_path/'confirm';cout=confirm/'output';cout.mkdir(parents=True);core.write(cout/'physical-contract.json',kit['physical_contract'])
    proof,state,error=study_confirmation.native(cout/'physical-contract.json',cout/'cad');assert state=='passed',error
    output=tmp_path/'visuals';output.mkdir()
    result=visuals.generate(dict(kind='civil-kit-study',group='test native civil kit',row={'folder':str(child)},confirmation={'folder':str(confirm)}),output)
    assert result['kind']=='construction-sequence' and 7.5<=float(result['video_probe']['format']['duration'])<=8.5
    assert (output/'overview.png').stat().st_size>1000 and (output/'model.step.gz').stat().st_size>1000
    seq=core.read(output/'sequence.json');assert len(seq['events'])==len(kit['units'])
    assert result['physical_release'] is False and result['motion_path_verified'] is False
