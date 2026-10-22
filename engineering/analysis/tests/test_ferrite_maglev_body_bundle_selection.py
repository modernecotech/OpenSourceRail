"""Current source identity selects body evidence without rewriting older runs."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import pytest
from engineering.ferrite_maglev import assembled_body, moving_train, body_stiffness, model

ROOT=Path(__file__).resolve().parents[3]


@pytest.fixture
def package(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location('body_bundle_selection',ROOT/'tools/automation/package-maglev-release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'ROOT',tmp_path)
    data=tmp_path/'input.toml';data.write_text('current')
    current={'input.toml':sha256(data.read_bytes()).hexdigest()}
    for mod in (assembled_body,moving_train,body_stiffness):monkeypatch.setattr(mod,'sources',lambda:current)
    def make(name,stale=False):
        base=tmp_path/'engineering/assurance'/name;base.mkdir(parents=True)
        files={}
        for key in ('run.py','summary.json','reference-100MN.json.gz','gross-series.json.gz','drilled-series.json.gz'):
            path=base/('body-axial-'+key);path.write_bytes(key.encode());files[key]=sha256(path.read_bytes()).hexdigest()
        (base/'body-axial-reproduction.txt').write_text('Reproduce the exact ignored driver path from the source map.')
        original='build/current-axial/run.py'
        receipt=dict(schema='osr-body-axial-sensitivity-receipt/1',original_driver_path=original,
            files_sha256=files,source_sha256={**current,original:files['run.py']},
            accepted_body_or_plant=False,city_default_changed=False,**model.FLAGS)
        if stale:receipt['source_sha256']['input.toml']='0'*64
        path=base/'body-axial-receipt.json';path.write_text(json.dumps(receipt))
        return base
    return module,make


def test_new_current_run_is_selected_and_history_is_unchanged(package):
    module,make=package;old=make('old',stale=True);new=make('new')
    before={p:p.read_bytes() for p in old.iterdir()}
    paths=module.body_evidence_paths()
    assert 'input.toml' in paths
    assert all('assurance/old/' not in p for p in paths)
    assert 'engineering/assurance/new/body-axial-run.py' in paths
    assert all(p.read_bytes()==raw for p,raw in before.items())
    assert len(list(new.iterdir()))==7


def test_stale_only_run_is_rejected(package):
    module,make=package;make('old',stale=True)
    with pytest.raises(ValueError,match='no current'):module.body_evidence_paths()


@pytest.mark.parametrize('fault',['payload','release','symlink','driver-path'])
def test_current_evidence_still_requires_exact_payloads_and_scope(package,fault):
    module,make=package;base=make('new')
    if fault=='payload':(base/'body-axial-drilled-series.json.gz').write_bytes(b'changed')
    elif fault=='symlink':
        target=base/'body-axial-run.py';target.unlink();target.symlink_to(base/'body-axial-summary.json')
    else:
        path=base/'body-axial-receipt.json';value=json.loads(path.read_text())
        if fault=='release':value['manufacturing_release']=True
        else:value['original_driver_path']='../run.py'
        path.write_text(json.dumps(value))
    with pytest.raises(ValueError):module.body_evidence_paths()
