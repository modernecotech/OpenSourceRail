"""Current publications own their outputs and preserve the quantity-cost boundary."""
import importlib.util
from pathlib import Path
import sys

from engineering.ferrite_maglev import delivery, manufacturing

ROOT=Path(__file__).resolve().parents[3]


def load(name):
    spec=importlib.util.spec_from_file_location('osr_test_'+name,ROOT/'tools/automation'/name)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def test_overview_generate_and_readonly_check_detect_output_drift(monkeypatch,tmp_path):
    module=load('generate-public-overview.py')
    root=tmp_path/'README.md';root.write_text('# Current design\n')
    monkeypatch.setattr(module,'REPO_ROOT',tmp_path)
    monkeypatch.setattr(module,'MARKDOWN_OUTPUT',tmp_path/'docs/overview.md')
    monkeypatch.setattr(module,'HTML_OUTPUT',tmp_path/'docs/overview.html')
    monkeypatch.setattr(module,'primary_markdown',lambda:'# Source-bound primary design\n')
    monkeypatch.setattr(sys,'argv',['generator'])
    assert module.main()==0
    assert root.read_text()=='# Current design\n'
    assert module.MARKDOWN_OUTPUT.read_text()=='# Source-bound primary design\n'
    assert '<h1>Source-bound primary design</h1>' in module.HTML_OUTPUT.read_text()
    monkeypatch.setattr(sys,'argv',['generator','--check'])
    assert module.main()==0
    module.HTML_OUTPUT.write_text('corrupt')
    before=module.HTML_OUTPUT.stat().st_mtime_ns
    assert module.main()==1
    assert module.HTML_OUTPUT.read_text()=='corrupt'
    assert module.HTML_OUTPUT.stat().st_mtime_ns==before


def test_vehicle_process_quantities_keep_shared_train_costs_distinct():
    rates=manufacturing.load()
    c={'vehicle':{'cars_per_train':6}}
    six=manufacturing.vehicle(c,rates,3000,225)
    three=manufacturing.vehicle(c,rates,3000,225,cars=3)
    rows={row['id']:row for row in six['rows']}
    assert rows['ferrite']['quantity']==18000
    assert rows['battery-pack']['quantity']==1350
    assert rows['coupling-and-gangway']['quantity']==5
    assert rows['train-control-and-protection']['quantity']==1
    # A shared train system and a coupling interface cannot be scaled per car.
    assert six['total_allowance_usd']!=2*three['total_allowance_usd']
    assert six['costs_are_quotes'] is False
    assert six['complete_factory_gate_price_usd'] is None
    assert six['local_value_added_fraction'] is None
    assert all(row['accepted'] is False and row['imported_input_usd'] is None for row in rows.values())


def test_unpriced_programme_scope_is_never_formatted_as_zero():
    assert delivery.money(None)=='unpriced'
    assert delivery.money(0)=='$0'
    assert delivery.money(1234)=='$1,234'
