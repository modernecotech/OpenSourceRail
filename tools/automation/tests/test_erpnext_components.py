import copy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.component_catalogue import CATALOGUE, validate_inputs, merge_profiles, make_package, validate_package, instance_key


def test_catalogue_has_eight_typed_components_and_rejects_injected_fields():
    assert len(CATALOGUE)==8
    with pytest.raises(ValueError,match='Unknown component inputs'):
        validate_inputs('training',dict(title='A',description='B',docstatus=1))
    with pytest.raises(ValueError):
        validate_inputs('arbitrary-doctype',{})


@pytest.mark.parametrize('value',[True,'NaN','Infinity',-1,1e20])
def test_replenishment_rejects_invalid_numbers(value):
    with pytest.raises(ValueError):
        validate_inputs('replenishment',dict(item='i',warehouse='w',level=1,quantity=value))


def test_nested_rows_are_validated_and_cannot_override_native_fields():
    good=dict(fiscal_year='2026',action='Stop',accounts=[dict(account='Expense',amount=100)])
    assert validate_inputs('budget',good)['accounts'][0]['amount']==100
    bad=copy.deepcopy(good);bad['accounts'][0]['company']='another'
    with pytest.raises(ValueError):validate_inputs('budget',bad)
    with pytest.raises(ValueError):validate_inputs('budget',dict(good,accounts=[]))


def test_merge_replace_instance_disable_and_deterministic_city_substitution():
    base=json.loads((ROOT/'deployment/erpnext/config/components.json').read_text())
    city=dict(schema='osr-components/1',city='samawah',defaults={'training':{'title':'Local induction'}},instances=[])
    merged=merge_profiles(base,city)
    assert merged['defaults']['training']['title']=='Local induction'
    assert base['defaults']['training']['title']=='City operating induction'
    package=make_package(merged,'PROJ-1');validate_package(package)
    assert 'samawah' in package['instances'][0]['inputs']['description']
    assert package==make_package(merged,'PROJ-1')
    city['instances']=[dict(component='training',key='city-induction',enabled=False,inputs={})]
    assert make_package(merge_profiles(base,city),'PROJ-1')['instances']==[]
    package['city']='wrong'
    with pytest.raises(ValueError,match='checksum'):validate_package(package)


def test_duplicate_unknown_defaults_and_key_validation():
    base=dict(schema='osr-components/1',defaults={},instances=[])
    city=dict(schema='osr-components/1',city='a',defaults={'unknown':{}},instances=[])
    with pytest.raises(ValueError):merge_profiles(base,city)
    for key in ['','../escape','mixed Case','x'*65]:
        with pytest.raises(ValueError):instance_key(key)
