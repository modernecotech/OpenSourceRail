"""Reference quantities, electronics bounds and source joins, not fabricated release evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('baghdad_detail',ROOT/'engineering/baghdad_detail.py')
detail=importlib.util.module_from_spec(spec);spec.loader.exec_module(detail)


def test_family_quantities_and_nested_content_do_not_become_finance_or_release():
    r=detail.build_register();b=r['quantity_bases']
    assert (b['trainset'],b['car'],b['bogie'],b['station'],b['site'],b['plant']) == (831,4986,9972,182,158,1)
    assert r['family']=='metro-6car'
    assert not r['engineering_release'] and not r['cost_model_changed'] and not r['finance_model_changed']
    parts={p['id']:p for p in r['parts']}
    assert parts['ME-05']['quantity_network_reference']==19944
    assert parts['ME-06']['quantity_network_reference']==9972
    assert parts['EL-03']['quantity_network_reference']==1662
    assert parts['EL-04']['quantity_network_reference']==3324
    assert parts['TR-01']['quantity_network_reference']==pytest.approx(b['route-km']*4000)
    assert parts['TR-08']['quantity_network_reference'] is None
    assert parts['TR-03']['quantity_network_reference'] is None
    assert all(p['unit_cost'] is None and p['supplier_part_number'] is None for p in r['parts'])


def test_power_envelope_counts_startup_and_rejects_incomplete_converter_or_pin_plan():
    data=json.loads(detail.ELECTRONICS.read_text());r=detail.power_envelope(data)
    assert r['simultaneous_output_w']==71.5
    assert r['input_envelope_w']==pytest.approx(79.44444444)
    assert r['minimum_capacity_w']==pytest.approx(99.30555556)
    assert r['capacity_current_at_minimum_bus_a']==pytest.approx(5.516975309)
    for mutate in (lambda d:d.update(selected_reference_supply_capacity_w=40),
                   lambda d:d['bench_gpio'].update(permission_output=30),
                   lambda d:d['bench_gpio'].update(permission_output=15),
                   lambda d:d.update(conversion_efficiency=0),
                   lambda d:d.update(capacity_margin=float('nan')),
                   lambda d:d['loads'][0].update(power_w=float('nan'))):
        wrong=deepcopy(data);mutate(wrong)
        with pytest.raises(ValueError):detail.power_envelope(wrong)


def test_software_and_erp_coverage_preserves_prototype_and_deployment_boundaries():
    r=detail.build_register();software={s['name']:s for s in r['software_allocations']}
    assert len(software)==60
    assert software['osr-runtime']['hosts']==['design-tooling']
    assert software['osr-trainset-image']['disposition']=='deployable-endpoint'
    assert r['erp']['enabled_city_instances']==[dict(component='training',key='city-induction')]
    assert set(r['erp']['workflow_components']) >= {'manufacturing','quality','maintenance','budget','replenishment'}


def test_tracked_detail_outputs_are_bound_to_current_design_and_components():
    r=detail.build_register()
    assert json.loads((detail.OUT/'register.json').read_text())==r
    assert (detail.OUT/'parts.csv').read_text()==detail.parts_csv(r)
    assert (detail.OUT/'README.md').read_text()==detail.render(r)
    assert 'design/component-catalogue/src/osr_mech/civil/slab.py' in r['sources_sha256']


def test_database_has_independent_bounded_temporary_storage_and_persistent_data():
    import yaml
    config=yaml.safe_load((ROOT/'deployment/erpnext/compose.yaml').read_text())
    db=config['services']['db']
    assert 'db-data:/var/lib/mysql' in db['volumes']
    assert '/tmp:mode=1777,size=512m' in db['tmpfs']
    assert db['healthcheck']['test']==['CMD','healthcheck.sh','--connect','--innodb_initialized']
