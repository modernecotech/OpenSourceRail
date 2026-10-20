"""Retained publications own their outputs without rewriting the primary README."""
import importlib.util
from pathlib import Path
import sys
import json
ROOT=Path(__file__).resolve().parents[3]


def load(name):
    spec=importlib.util.spec_from_file_location('osr_test_'+name,ROOT/'tools/automation'/name)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def test_portfolio_generate_and_check_own_comparator_without_readme_block(monkeypatch,tmp_path):
    module=load('generate-portfolio-summary.py');data=module._portfolio_data()
    root=tmp_path/'README.md';root.write_text('# Primary maglev\n')
    monkeypatch.setattr(module,'REPO_ROOT',tmp_path)
    monkeypatch.setattr(module,'MARKDOWN_OUTPUT',tmp_path/'docs/portfolio-summary.md')
    monkeypatch.setattr(module,'JSON_OUTPUT',tmp_path/'docs/portfolio-summary.json')
    monkeypatch.setattr(module,'_portfolio_data',lambda:data)
    monkeypatch.setattr(sys,'argv',['generator'])
    assert module.main()==0
    assert root.read_text()=='# Primary maglev\n'
    payload=json.loads(module.JSON_OUTPUT.read_text())
    assert payload['architecture']=='wheel-rail-reference' and payload['publication_role']=='retained-comparator'
    comparator=tmp_path/'docs/portfolio-economics-comparator.md'
    assert 'retained LM3' in comparator.read_text()
    monkeypatch.setattr(sys,'argv',['generator','--check']);assert module.main()==0
    comparator.write_text('corrupt');assert module.main()==1
