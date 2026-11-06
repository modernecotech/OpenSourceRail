from pathlib import Path
import pytest
from engineering.outline.city_cost_inputs import resolve


def test_independent_country_city_and_request_scopes(tmp_path):
    folder=tmp_path/'engineering/outline';folder.mkdir(parents=True)
    (folder/'city_cost_inputs.py').write_text('fixture')
    (folder/'city-cost-inputs.toml').write_text('''schema="osr-city-local-cost-inputs/1"
revision="test"
physical_reference_changed=false
local_rates_verified=false
reference_origin="Declared reference"
[countries.IQ]
basis="Country tariff estimate"
electricity_usd_per_kwh=[0.1,0.2,0.3]
[cities.baghdad]
basis="City wage estimate"
operations_loaded_paid_wage_usd_h=[1.0,2.0,3.0]
''')
    defaults=dict(electricity_usd_per_kwh=[.3,.4,.5],operations_loaded_paid_wage_usd_h=[4.,5.,6.])
    v=resolve(dict(slug='baghdad',country='IQ'),defaults,dict(local_costs=dict(basis='Scenario tariff',electricity_usd_per_kwh=[.2,.25,.4])),root=tmp_path)
    assert v['values']==dict(electricity_usd_per_kwh=[.2,.25,.4],operations_loaded_paid_wage_usd_h=[1.,2.,3.])
    assert [r['level'] for r in v['overrides']]==['country','city','request']
    assert v['local_rates_verified'] is False
    with pytest.raises(ValueError,match='scoped local cost'):
        resolve(dict(slug='baghdad',country='IQ'),defaults,dict(local_costs=dict(basis='Unscoped discount',all_cost_multiplier=.5)),root=tmp_path)
