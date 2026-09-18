import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('city_collection',ROOT/'tools/automation/collect-city-validation.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


@pytest.fixture
def evidence(tmp_path,monkeypatch):
    source=tmp_path/'source';source.mkdir()
    design=source/'design.toml';design.write_text('design')
    canonical=source/'sample.toml';canonical.write_text('canonical')
    root=tmp_path/'artifacts';folder=root/'partition-0/sample';folder.mkdir(parents=True)
    (folder/'sample.toml').write_text('generated')
    (folder/'design.toml').write_bytes(design.read_bytes())
    inputs={'source/design.toml':c.batch.sha(design)}
    monkeypatch.setattr(c.batch,'source_inputs',lambda *_:inputs)
    report=dict(passed=True,trainset_contract=dict(passed=True),runs=[dict(duration_s=90000)],
        resilience_required=False,scenario_sha256=c.batch.sha(folder/'sample.toml'),design_sha256=c.batch.sha(design))
    record=dict(schema='osr-city-simulation-execution/1',city='sample',commit='candidate',
        exit_code=0,inputs_unchanged=True,passed=True,scenario_basis='generator-candidate',resilience_required=False,
        inputs=inputs.copy(),canonical_scenario_sha256=c.batch.sha(canonical),
        tested_scenario_sha256=c.batch.sha(folder/'sample.toml'),design_sha256=c.batch.sha(design))
    def save():
        (folder/'validation.json').write_text(json.dumps(report))
        record['report_sha256']=c.batch.sha(folder/'validation.json')
        (folder/'execution.json').write_text(json.dumps(record))
    save()
    return dict(root=root,folder=folder,catalogue={'sample':(design,{})},record=record,report=report,save=save)


def test_complete_current_catalogue_remains_software_only(evidence):
    result=c.collect(evidence['root'],evidence['catalogue'],'candidate')
    assert result['passed'] and result['passed_cities']==result['selected']==1
    assert not result['physical_release'] and not result['operating_release']


@pytest.mark.parametrize('change',['commit','inputs','exit','changed','report','scenario','design','empty','malformed','short','resilience','missing','duplicate','escape'])
def test_collection_rejects_incomplete_or_stale_evidence(evidence,tmp_path,change):
    e=evidence;r=e['record'];report=e['report'];folder=e['folder']
    if change=='commit':r['commit']='old'
    elif change=='inputs':r['inputs']={}
    elif change=='exit':r['exit_code']=124
    elif change=='changed':r['inputs_unchanged']=False
    elif change=='empty':report['runs']=[]
    elif change=='malformed':report['runs']=[None]
    elif change=='short':report['runs'][0]['duration_s']=60
    elif change=='resilience':report['resilience_required']=True
    e['save']()
    if change=='report':(folder/'validation.json').write_text('{}')
    elif change=='scenario':(folder/'sample.toml').write_text('tampered')
    elif change=='design':(folder/'design.toml').write_text('tampered')
    elif change=='missing':(folder/'execution.json').unlink()
    elif change=='duplicate':shutil.copytree(folder,e['root']/'partition-1/sample')
    elif change=='escape':
        outside=tmp_path/'outside.json';outside.write_text((folder/'validation.json').read_text())
        (folder/'validation.json').unlink();(folder/'validation.json').symlink_to(outside)
    result=c.collect(e['root'],e['catalogue'],'candidate')
    assert not result['passed']
    assert result['errors'] or result['missing']
