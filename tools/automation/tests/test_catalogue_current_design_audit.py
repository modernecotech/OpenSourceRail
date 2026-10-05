"""The catalogue census rejects mismatched physical inventories and payroll."""
import importlib.util
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('current_catalogue_audit',ROOT/'tools/automation/generate-catalogue-current-design-report.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def test_regeneration_cannot_drop_a_controlled_charging_configuration():
    design={'costs':{'technology_basis':{'station_charging_cabinet_count':1}}}
    policy={'charging':{'station_cabinet_count':4}}
    with pytest.raises(ValueError,match='charging requirement mismatch'):
        audit.check_charging_requirement(design,policy,'example')
    design['costs']['technology_basis']['station_charging_cabinet_count']=4
    audit.check_charging_requirement(design,policy,'example')


def test_current_city_reconciles_inventory_depots_payroll_and_publication():
    r=audit.audit({'aba-ng'})
    city=r['cities'][0]
    assert city['lines']==city['depots']
    assert city['storage_slots']==city['trainsets']
    assert city['cars']==city['trainsets']*3
    assert city['station_fte']>4*city['stations']  # service, weekends, leave and training cover
    assert city['planning_example_complete'] and not r['operational_release']
    assert city['shared_factory_envelope_usd']>0 and city['annual_payroll_usd']>0
    assert 'Baghdad' in r['excluded_baghdad_reason']


def test_factory_cannot_change_the_controlled_number_of_cars(monkeypatch):
    original=audit.read
    def corrupt(path):
        r=original(path)
        if path.as_posix().endswith('/factory/summary.json'):r['vehicle_modules']+=1
        return r
    monkeypatch.setattr(audit,'read',corrupt)
    with pytest.raises(ValueError,match='car count'):
        audit.audit({'aba-ng'})


def test_payroll_must_reconcile_to_the_opex_ledger(monkeypatch):
    original=audit.read
    def corrupt(path):
        r=original(path)
        if path.as_posix().endswith('/finance/summary.json'):r['annual_opex_usd']['components']['labour']+=1000
        return r
    monkeypatch.setattr(audit,'read',corrupt)
    with pytest.raises(ValueError,match='payroll mismatch'):
        audit.audit({'aba-ng'})
