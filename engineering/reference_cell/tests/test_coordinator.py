"""Independent actual one-cell replay/cache/publication and forgery controls."""
from copy import deepcopy
from pathlib import Path
import gzip,io,json,shutil,tarfile,subprocess,sys,fcntl
import pytest
from engineering.reference_cell import coordinator as c,identity,encoded,digest,FLAGS
from engineering.railway_twin.pipeline import IncompleteDesign


def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def write(path,value):
    raw=encoded(value);Path(path).write_bytes(gzip.compress(raw,mtime=0) if str(path).endswith('.gz') else raw)


def index_seal(v):
    v['run_id']=identity({k:x for k,x in v.items() if k not in ('new_cases','run_id')});return v


@pytest.fixture(scope='module')
def actual_cell(tmp_path_factory):
    state=tmp_path_factory.mktemp('actual-one-cell')/'state'
    result=c.run(state,max_cases=1)
    assert len(result['cases'])==1 and len(result['pending'])==9
    return state,result


def copy_state(actual_cell,tmp_path):
    folder=tmp_path/'copy';shutil.copytree(actual_cell[0],folder);return folder


def test_actual_one_cell_and_nine_pending_verify_without_operating_or_economic_release(actual_cell):
    folder,index=actual_cell;result=c.verify(folder)
    assert result['verified'] and result['cases']==1 and result['pending']==9
    assert result['completed_production_journeys']==0 and result['available_operating_maps']==0 and not result['engineering_complete']
    report=read(folder/index['cases'][0]['path'])
    assert report['candidate_id']==index['cases'][0]['summary']['candidate_id']
    assert report['civil']['candidate_id']==report['manufacturing']['candidate_id']==report['candidate_id']
    assert report['manufacturing']['actual_quote_occurrence_coverage']==0
    assert report['economics']['whole_life_cost_usd'] is None
    assert all(not result[k] for k in FLAGS)


def test_exact_cached_run_does_not_dispatch_new_cases_or_change_run_identity(actual_cell):
    folder,index=actual_cell;r=c.run(folder,max_cases=0)
    assert r['run_id']==index['run_id'] and r['new_cases']==0
    assert r['cases']==index['cases'] and r['pending']==index['pending']


def test_strict_completion_returns_physical_open_domains_not_a_pass(actual_cell):
    with pytest.raises(IncompleteDesign) as error:c.verify(actual_cell[0],strict=True)
    assert {x['id'] for x in error.value.blockers}>={'vehicle','structure','propulsion','journey','civil','economics','GoA4-and-HIL','commissioning-and-pilot'}


@pytest.mark.parametrize('mode',['verify','cached-run'])
def test_resealed_cached_mass_forgery_rejected_by_replay_not_only_selfhash(actual_cell,tmp_path,mode):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');row=index['cases'][0]
    report=read(folder/row['path']);report['vehicle_summary']['mass_upper_bound_kg']=1.
    report['evaluation_id']=identity({k:v for k,v in report.items() if k!='evaluation_id'});write(folder/row['path'],report)
    row['summary']=c.compact(report);write(folder/'latest.json',index_seal(index))
    with pytest.raises(ValueError,match='semantic|Cached|cache|replay'):
        (c.verify(folder) if mode=='verify' else c.run(folder,max_cases=0))


def test_resealed_claim_of_arrival_or_known_operating_map_is_rejected(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');row=index['cases'][0]
    report=read(folder/row['path']);report['completed_production_journeys']=1;report['available_operating_maps']=1
    report['evaluation_id']=identity({k:v for k,v in report.items() if k!='evaluation_id'});write(folder/row['path'],report)
    row['summary']=c.compact(report);write(folder/'latest.json',index_seal(index))
    with pytest.raises(ValueError,match='semantic|replay'):c.verify(folder)


def test_resealed_mixed_case_candidate_cannot_become_current_cell(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');index['cases'][0]['summary']['candidate_id']='f'*64
    write(folder/'latest.json',index_seal(index))
    with pytest.raises(ValueError,match='semantic|replay'):c.verify(folder)


@pytest.mark.parametrize('path',['../outside.json.gz','/tmp/outside.json.gz','cases/unrequested.json.gz'])
def test_case_path_cannot_be_rebound_even_after_index_reseal(actual_cell,tmp_path,path):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');index['cases'][0]['path']=path
    write(folder/'latest.json',index_seal(index))
    with pytest.raises(ValueError,match='path'):c.verify(folder)


def test_pending_request_coverage_cannot_hide_failed_or_missing_vehicle_design(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');index['pending'].pop()
    write(folder/'latest.json',index_seal(index))
    with pytest.raises(ValueError,match='coverage'):c.verify(folder)


def test_source_snapshot_and_closed_payload_inventory_are_enforced(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);(folder/'input-sources.tar.gz').write_bytes(gzip.compress(b'forged retained bytes'))
    with pytest.raises(ValueError,match='source snapshot'):c.verify(folder)
    folder=tmp_path/'extra';shutil.copytree(actual_cell[0],folder);(folder/'unrequested.txt').write_text('not declared')
    with pytest.raises(ValueError,match='artifact'):c.verify(folder)


def test_symlinked_cell_payload_is_not_a_valid_ordinary_package(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);index=read(folder/'latest.json');p=folder/index['cases'][0]['path'];raw=p.read_bytes();p.unlink()
    outside=tmp_path/'outside.json.gz';outside.write_bytes(raw);p.symlink_to(outside)
    with pytest.raises(ValueError,match='linked|ordinary'):c.verify(folder)


def test_active_coordinator_lock_refuses_concurrent_mutation(actual_cell):
    folder=actual_cell[0]
    with (folder/'.coordinator.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='already running'):c.run(folder,max_cases=0)


def test_budget_zero_keeps_all_work_pending_and_strict_hold(tmp_path):
    folder=tmp_path/'pending';index=c.run(folder,max_cases=0)
    assert not index['cases'] and len(index['pending'])==10
    assert c.verify(folder)['pending']==10
    with pytest.raises(IncompleteDesign):c.verify(folder,strict=True)


def test_required_complete_cli_exit_is_three_with_actual_open_domains(actual_cell):
    p=subprocess.run([sys.executable,'-m','engineering.reference_cell','verify',str(actual_cell[0]),'--require-complete'],cwd=c.ROOT,capture_output=True,text=True,timeout=120)
    assert p.returncode==3,p.stdout+p.stderr
    assert json.loads(p.stdout)['complete'] is False


@pytest.fixture(scope='module')
def publication(actual_cell,tmp_path_factory):
    output=tmp_path_factory.mktemp('one-cell-publication');result=c.publish(actual_cell[0],output=output)
    return output,result


def test_actual_publication_recomputes_archive_and_summary(publication):
    folder,index=publication;r=c.verify_publication(output=folder)
    assert r['verified'] and r['cases']==1 and r['pending']==9
    assert r['publication_id']==index['publication_id'] and not r['engineering_complete']


def test_resealed_workbench_summary_forgery_does_not_hide_unsupported_mass(publication,tmp_path):
    folder=tmp_path/'pub';shutil.copytree(publication[0],folder)
    summary=read(folder/'summary.json');summary['cases'][0]['mass']['mass_upper_bound_kg']=1.;write(folder/'summary.json',summary)
    manifest=read(folder/'manifest.json');manifest['files_sha256']['summary.json']=digest(folder/'summary.json')
    manifest['publication_id']=identity({k:v for k,v in manifest.items() if k!='publication_id'});write(folder/'manifest.json',manifest)
    with pytest.raises(ValueError,match='summary'):c.verify_publication(output=folder)


@pytest.mark.parametrize('name,kind',[('../escape','file'),('/absolute','file'),('linked','link')])
def test_publication_archive_refuses_traversal_absolute_paths_and_links(publication,tmp_path,name,kind):
    folder=tmp_path/'pub';shutil.copytree(publication[0],folder);blob=io.BytesIO()
    with tarfile.open(fileobj=blob,mode='w') as archive:
        item=tarfile.TarInfo(name)
        if kind=='link':item.type=tarfile.SYMTYPE;item.linkname='/tmp/escape';archive.addfile(item)
        else:item.size=1;archive.addfile(item,io.BytesIO(b'x'))
    target=folder/'reference-cell.tar.gz';target.write_bytes(gzip.compress(blob.getvalue(),mtime=0))
    manifest=read(folder/'manifest.json');manifest['files_sha256']['reference-cell.tar.gz']=digest(target)
    manifest['publication_id']=identity({k:v for k,v in manifest.items() if k!='publication_id'});write(folder/'manifest.json',manifest)
    with pytest.raises(ValueError,match='ordinary|archive'):c.verify_publication(output=folder)


def test_nested_lock_named_file_is_not_an_exempt_undeclared_artifact(actual_cell,tmp_path):
    folder=copy_state(actual_cell,tmp_path);(folder/'unrequested').mkdir();(folder/'unrequested/.coordinator.lock').write_text('unrequested bytes')
    with pytest.raises(ValueError,match='artifact'):c.verify(folder)


def test_symlinked_top_level_state_is_not_an_ordinary_immutable_packet(actual_cell,tmp_path):
    link=tmp_path/'linked-state';link.symlink_to(actual_cell[0],target_is_directory=True)
    with pytest.raises(ValueError,match='(?i)linked|ordinary'):c.verify(link)


def test_executing_coordinator_must_match_source_snapshot_not_merely_claim_another_root(monkeypatch,tmp_path):
    changed=tmp_path/'different-coordinator.py';changed.write_bytes(Path(c.__file__).read_bytes()+b'\n# different source\n')
    monkeypatch.setattr(c,'__file__',str(changed))
    with pytest.raises(ValueError,match='source|coordinator|executing'):c.sources()


@pytest.mark.parametrize('change',[{'physical_accepted':True},{'manufacturing_release':True},{'selected_reference_changed':True},{'schema':'wrong-publication-interface'}])
def test_resealed_publication_manifest_cannot_claim_release_or_another_schema(publication,tmp_path,change):
    folder=tmp_path/'pub';shutil.copytree(publication[0],folder);v=read(folder/'manifest.json');v.update(change)
    v['publication_id']=identity({k:x for k,x in v.items() if k!='publication_id'});write(folder/'manifest.json',v)
    with pytest.raises(ValueError,match='schema|release|disposition|identity'):c.verify_publication(output=folder)
