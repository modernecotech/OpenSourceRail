"""Changed CAD/solver dependencies cannot retain current screening evidence."""
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('change_workflow',ROOT/'engineering/changes/workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

@pytest.fixture
def config():
    c=json.loads((ROOT/'engineering/changes/config/generic.json').read_text())
    c.update(json.loads((ROOT/'engineering/changes/config/samawah.json').read_text()));return c

@pytest.mark.parametrize('key,value',[('environment','physical'),('candidate_depth_mm',0),('density_kg_m3',True),('screening_point_load_n',float('nan')),('mesh_elements',[8,8,32]),('mesh_elements',[8,16]),('mesh_elements',[8,15,32]),('analytical_relative_tolerance',1),('release_blockers',[]),('source_cad','../outside')])
def test_invalid_or_unbounded_config_rejected(config,key,value):
    config[key]=value
    with pytest.raises(ValueError):w.validate_config(ROOT,config)


def test_evidence_cannot_follow_changed_dependencies():
    inputs=dict(cad='a',quantities='b',configuration='c');record=dict(passed=True,input_sha256=inputs)
    assert w.evidence_status(record,inputs)=='screening-current'
    for key in inputs:
        assert w.evidence_status(record,{**inputs,key:'changed'})=='superseded'
    assert w.evidence_status({**record,'passed':False},inputs)=='failed'


@pytest.mark.parametrize('city',['samawah','mosul'])
def test_retained_native_bundle_is_current(city):
    result=w.verify(ROOT,ROOT/f'engineering/changes/examples/{city}-cross-bearer')
    assert result['physical_release'] is False and result['engineering_release'] is False
    report=json.loads((ROOT/f'engineering/changes/examples/{city}-native-erp.json').read_text())
    assert report['manifest_sha256']==result['sha256'] and report['city']==city
    assert report['passed'] and len(report['checks'])==11 and all(r['passed'] for r in report['checks'])
    assert report['physical_release'] is False and report['engineering_acceptance'] is False
    assert all(w.sha(ROOT/path)==value for path,value in report['source_sha256'].items())


@pytest.mark.parametrize('mutation',['bytes','missing','extra','source','release'])
def test_altered_bundle_rejected(tmp_path,mutation):
    import shutil
    source=ROOT/'engineering/changes/examples/samawah-cross-bearer';target=tmp_path/'bundle';shutil.copytree(source,target)
    manifest=json.loads((target/'manifest.json').read_text())
    if mutation=='bytes':(target/'candidate.FCStd').write_bytes(b'changed')
    elif mutation=='missing':(target/'candidate-quantities.json').unlink()
    elif mutation=='extra':(target/'unreviewed').write_text('extra')
    else:
        if mutation=='source':manifest['source_sha256'][next(iter(manifest['source_sha256']))]='0'*64
        else:manifest['physical_release']=True
        manifest['sha256']=w.digest({k:v for k,v in manifest.items() if k!='sha256'});w.write(target/'manifest.json',manifest)
    with pytest.raises(ValueError):w.verify(ROOT,target)


def test_ignored_interpreter_cache_is_not_required_for_reproduction(tmp_path):
    import shutil
    source=ROOT/'engineering/changes/examples/samawah-cross-bearer';target=tmp_path/'bundle';shutil.copytree(source,target)
    shutil.rmtree(target/'__pycache__',ignore_errors=True)
    manifest=w.verify(ROOT,target)
    assert not any('__pycache__' in path for path in manifest['files'])
    (target/'__pycache__').mkdir();(target/'__pycache__/run-freecad.cpython-313.pyc').write_bytes(b'interpreter cache')
    assert w.verify(ROOT,target)==manifest
