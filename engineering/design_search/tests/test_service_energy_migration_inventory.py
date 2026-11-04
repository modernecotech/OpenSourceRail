import hashlib
import ast
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from engineering.design_search import service_energy_migration_inventory as migration


def unavailable(reason):
    if os.environ.get('OSR_MIGRATION_REQUIRE_REAL') == '1':
        pytest.fail(reason)
    pytest.skip(reason)


def test_required_real_inputs_fail_instead_of_skipping(monkeypatch):
    monkeypatch.setenv('OSR_MIGRATION_REQUIRE_REAL', '1')
    with pytest.raises(pytest.fail.Exception, match='missing history'):
        unavailable('missing history')


def encoded(value):
    return migration.old._encoded(value)


def manifest(source=None):
    value={'schema':'test/1','source_sha256':{} if source is None else {migration.SOURCE:source}}
    value['manifest_id']=migration.old._id(value)
    raw=encoded(value)
    return raw,value['manifest_id'],hashlib.sha256(raw).hexdigest()


def record(name,raw,identity,sha,linked=False):
    return migration._record(name,raw,'test/1','manifest_id','source_sha256',identity,sha,migration.OLD_ARCHIVE,linked)


def test_external_source_and_archive_pins_are_exact():
    fixed=[migration.OLD_SHA,migration.FIX_SHA,migration.OLD_ARCHIVE,migration.EXTRA_ARCHIVE,migration.EXTRA_PINS]
    migration._fixed(*fixed)
    for i in range(len(fixed)):
        wrong=fixed.copy();wrong[i]='0'*64
        with pytest.raises(ValueError,match='pinned'):migration._fixed(*wrong)


def test_direct_source_marks_current_regeneration_and_retains_no_replay():
    raw,identity,sha=manifest(migration.OLD_SHA)
    item=record('case/manifest.json',raw,identity,sha,True)
    assert item['disposition']=='current-regeneration-required'
    assert item['dependency']=='direct-source' and item['linked_current_publication']
    assert not item['packet_payload_verified'] and not item['current_replay_completed']


def test_missing_direct_dependency_stays_historical_and_linked_missing_fails():
    raw,identity,sha=manifest()
    item=record('case/manifest.json',raw,identity,sha)
    assert item['disposition']=='historical-only' and item['dependency']=='no-direct-source-review-required'
    linked=record('case/manifest.json',raw,identity,sha,True)
    assert linked['disposition']=='current-dependency-review-required'
    assert linked['retained_disposition']=='historical-only'


def test_physical_followup_keeps_distinct_original_producer_epoch():
    raw,identity,sha=manifest(migration.OLD_SHA)
    item=record(migration.FOLLOWUP,raw,identity,sha)
    assert item['disposition']=='historical-only'
    assert item['dependency']=='historical-wrapper-current-context'


def test_rejects_tampered_manifest_and_conflicting_source():
    raw,identity,sha=manifest(migration.OLD_SHA)
    with pytest.raises(ValueError,match='manifest bytes'):
        record('x',raw+b' ',identity,sha)
    with pytest.raises(ValueError,match='manifest identity'):
        record('x',raw,'0'*64,sha)
    raw,identity,sha=manifest('0'*64)
    with pytest.raises(ValueError,match='Conflicting electrical source'):
        record('x',raw,identity,sha)


def test_archive_rejects_extra_files_and_symlink(tmp_path):
    (tmp_path/'manifest.json').write_text('{}');(tmp_path/'sources.tar.gz').write_bytes(b'')
    (tmp_path/'extra').write_text('x')
    with pytest.raises(ValueError,match='Exact source archive inventory'):
        migration._archive(tmp_path,migration.OLD_ARCHIVE,'old',{})
    link=tmp_path.parent/(tmp_path.name+'-link');link.symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(ValueError,match='Symlink'):
        migration._archive(link,migration.OLD_ARCHIVE,'old',{})


def test_real_pinned_inventory_if_git_history_is_available():
    root=Path(__file__).resolve().parents[3]
    old_archive=root/'docs/design-engine/retained-battery-source-epoch/archive'
    extra_archive=root/'docs/design-engine/retained-service-energy-extra/original/worker-v7/archive'
    if not (old_archive/'manifest.json').is_file() or not (extra_archive/'manifest.json').is_file():
        unavailable('historical source archives not in checkout')
    for commit in (migration.OLD_COMMIT,migration.EXTRA_COMMIT,migration.FIX_COMMIT):
        if subprocess.run(['git','cat-file','-e',commit+'^{commit}'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
            unavailable('pinned historical Git commit unavailable')
    result=migration.inventory(root,old_archive,old_archive.parent/'pins.json',extra_archive,extra_archive.parent/'pins.json',
        old_sha=migration.OLD_SHA,fix_sha=migration.FIX_SHA,old_archive=migration.OLD_ARCHIVE,
        extra_archive=migration.EXTRA_ARCHIVE,expected_extra_pins=migration.EXTRA_PINS)
    assert len(result['records'])==29 and sum(x['linked_current_publication'] for x in result['records'])==17
    assert sum(x['disposition']=='current-regeneration-required' for x in result['records'])==26
    assert result['archive_source_bytes_verified'] and result['git_manifest_bytes_verified']
    for name in (*migration.FLAGS,'packet_payloads_verified','archive_materialization_verified','current_replay_completed'):
        assert result[name] is False
    assert result['reference_candidate_id']==migration.REFERENCE and result['selection_id']==migration.SELECTION
    assert result['inventory_id']==migration.old._id({k:v for k,v in result.items() if k!='inventory_id'})
    mass=next(x for x in result['records'] if x['manifest']=='installed-mass-support/manifest.json')
    assert mass['linked_current_publication'] and mass['disposition']=='current-dependency-review-required'
    assert 'not full transitive' in result['scope']


def test_linked_membership_matches_publication_contract():
    root=Path(__file__).resolve().parents[3]
    raw=subprocess.run(['git','show','HEAD:engineering/station_rail/publication.py'],cwd=root,
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    tree=ast.parse(raw)
    definitions=[n.value for n in tree.body if isinstance(n,ast.Assign) and
                 any(isinstance(target,ast.Name) and target.id=='LINKED_PUBLICATIONS' for target in n.targets)]
    assert len(definitions)==1
    linked=set(ast.literal_eval(definitions[0]))
    recorded=set(migration.old.CATALOG)|{name.removesuffix('/manifest.json') for name in migration.LINKED_EXTRA}
    # The migration inventory preserves its original linked membership. The
    # periodic packet now has a separately authenticated retained-source route;
    # do not rewrite those historical records or present its old sources as live.
    scopes=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='linked_publication_scope')
    returns=[n.value for n in ast.walk(scopes) if isinstance(n,ast.Return)]
    assert len(returns)==1 and isinstance(returns[0],ast.Call)
    original=next(k.value for k in returns[0].keywords if k.arg=='original_packet_and_producer_bytes_only')
    retained=recorded.intersection(ast.literal_eval(original))
    assert retained=={'periodic-thermal-research'}
    assert not retained.intersection(linked)
    assert recorded|set(migration.LINKED_NOT_COVERED)==linked|retained
    assert not recorded.intersection(migration.LINKED_NOT_COVERED)
    for name in migration.extra.CATALOG:
        folder=name.removesuffix('/manifest.json')
        assert (folder in linked|retained)==(name in migration.LINKED_EXTRA)
    linker=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='linked_publication_sources')
    calls=[n for n in ast.walk(linker) if isinstance(n,ast.Call)
        and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)
        and (n.func.value.id,n.func.attr)==('retained_periodic_thermal','verify')]
    assert len(calls)==1
    assert any(isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name)
        and n.value.id=='thermal' and ast.literal_eval(n.slice)=='dependency_sha256' for n in ast.walk(linker))


def test_retained_periodic_membership_keeps_all_authenticated_sources():
    from engineering.design_search import retained_periodic_thermal
    proof=retained_periodic_thermal.verify()
    assert proof['verified'] is True
    assert proof['original_source_count']==55
    assert proof['original_manifest_id']=='e2ac8e01ac36eaa19d8f5c59c0dcfc28de6acd7759065a0a7b122cd8d7c3d66d'
    assert proof['numerical_reexecuted'] is False
    assert proof['current_evaluator_admission'] is False
    assert proof['physical_accepted'] is False


def test_git_input_environment_is_sanitized_and_read_has_timeout(monkeypatch,tmp_path):
    for key in ('GIT_DIR','GIT_OBJECT_DIRECTORY','GIT_CONFIG_COUNT','GIT_CONFIG_KEY_0',
                'GIT_CONFIG_VALUE_0','GIT_NAMESPACE','GIT_EXEC_PATH'):
        monkeypatch.setenv(key,'hostile')
    monkeypatch.setattr(migration.shutil,'which',lambda *args,**kwargs:'/usr/bin/git')
    calls=[]
    def run(command,**kwargs):
        calls.append((command,kwargs))
        return SimpleNamespace(returncode=0,stdout=b'3\n' if '-s' in command else b'abc')
    monkeypatch.setattr(migration.subprocess,'run',run)
    assert migration._git(tmp_path,migration.FIX_COMMIT,migration.SOURCE)==b'abc'
    assert len(calls)==2 and all(kw['timeout']==30 for _,kw in calls)
    for _,kw in calls:
        assert all(key not in kw['env'] for key in ('GIT_DIR','GIT_OBJECT_DIRECTORY','GIT_CONFIG_COUNT',
                   'GIT_CONFIG_KEY_0','GIT_CONFIG_VALUE_0','GIT_NAMESPACE','GIT_EXEC_PATH'))
        assert kw['env']['GIT_NO_LAZY_FETCH']=='1'
    def stall(command,**kwargs):raise subprocess.TimeoutExpired(command,kwargs['timeout'])
    monkeypatch.setattr(migration.subprocess,'run',stall)
    with pytest.raises(ValueError,match='exceeded timeout'):
        migration._git(tmp_path,migration.FIX_COMMIT,migration.SOURCE)


def test_pinned_archive_rejects_false_promotion_and_changed_source_tar(monkeypatch,tmp_path):
    root=Path(__file__).resolve().parents[3]
    location=root/'docs/design-engine/retained-battery-source-epoch'
    manifest_path=location/'archive/manifest.json'
    if not manifest_path.is_file():pytest.skip('historical source archive metadata not in checkout')
    original=json.loads(manifest_path.read_bytes());pins=json.loads((location/'pins.json').read_bytes())
    (tmp_path/'manifest.json').write_text('{}');(tmp_path/'sources.tar.gz').write_bytes(b'')
    bad=dict(original,physical_accepted=True)
    monkeypatch.setattr(migration,'_read',lambda path,limit=0: encoded(bad) if path.name=='manifest.json' else b'bad')
    with pytest.raises(ValueError,match='identity, reference or non-promotion'):
        migration._archive(tmp_path,migration.OLD_ARCHIVE,'old',pins)
    monkeypatch.setattr(migration,'_read',lambda path,limit=0: encoded(original) if path.name=='manifest.json' else b'bad')
    with pytest.raises(ValueError,match='Source archive bytes differ'):
        migration._archive(tmp_path,migration.OLD_ARCHIVE,'old',pins)
