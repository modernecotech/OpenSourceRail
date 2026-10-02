import json
from tools.automation.tacs_cost import compare
from tools.automation.tacs_assurance import ROOT
import pytest

def model():return json.loads((ROOT/'engineering/assurance/tacs/cost-model.json').read_text())
def test_missing_costs_never_become_zero_or_savings():
    r=compare(model());assert r['state']=='incomplete-inputs';assert r['savings'] is None;assert not r['city_cost_export_authorised']
def test_equivalent_service_discounted_maintenance_and_equipment_are_counted():
    m=model();m['service_basis']=dict(route_length_km=1,fleet=2,headway_seconds=120,availability=0.99,years=2,discount_rate=0)
    for row in m['equipment']:row['unit_costs']=[10,10];row['quantities']=[2,1]
    for v in m['lifecycle'].values():
        for k in v:v[k]=0
        v.update(local_content_fraction=0.5,import_content_fraction=0.5,maintenance_hours_per_year=2,labour_cost_per_hour=5)
    r=compare(m);assert r['lifecycle_npv']=={'sectional-pilot':120,'distributed-target':70};assert r['savings']==50
    assert not r['city_cost_export_authorised']
    m['equipment'][0]['unit_costs'][0]=-1
    with pytest.raises(ValueError):compare(m)
