"""Cash conservation, service cardinality and missing-evidence holds."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import affordability as a


def line(ring=False):
    return dict(line='test',retained_shape='ring' if ring else 'radial',
        retained_schedule=[dict(**{'from':'23:00','to':'01:00'},headway_min=1)],
        selected_peak_headway_seconds=120,
        duty=dict(cycle_distance_m=10000,hot_aw3_no_regen_cycle_kwh=20,
            fixed_station_and_booster_traction_input_kwh_per_train_circuit=10,
            arrival_events_per_circuit=[dict(station_traction_input_kwh=5)]*2),
        operating_plan=dict(powered_top_up_zones=[{}]))


def test_service_midnight_rings_and_protected_headway():
    radial=a.service([line()])['lines'][0]
    ring=a.service([line(True)])['lines'][0]
    assert radial['directional_departures_per_day']==60
    assert radial['train_km_per_day']==600
    assert radial['services_hot_kwh_per_day']==1200
    assert radial['positive_traction_kwh_per_day']==600
    assert radial['fixed_zone_events_per_day']==240
    assert ring['train_km_per_day']==1200
    assert ring['fixed_zone_events_per_day']==360


def test_overlapping_service_does_not_double_count():
    l=line();l['retained_schedule']*=2
    with pytest.raises(ValueError,match='overlapping'):a.service([l])


@pytest.mark.parametrize('rate',[0,.04,.1])
def test_loan_principal_closes_and_interest_matches_balance(rate):
    rows=a.loan(1000000,rate,20)
    assert sum(r['principal_usd'] for r in rows)==pytest.approx(1000000)
    assert rows[-1]['closing_usd']==0
    assert max(r['debt_service_usd'] for r in rows)==pytest.approx(min(r['debt_service_usd'] for r in rows))
    for r in rows:
        assert r['interest_usd']==pytest.approx(r['opening_usd']*rate)
        assert r['opening_usd']-r['principal_usd']==pytest.approx(r['closing_usd'])


def test_resource_and_borrower_cash_reconcile_without_counting_debt_twice():
    settings=a.load();case=settings['cases'][1]
    r=a.cashflow(1000000,20000,settings,case)
    assert len(r['rows'])==35
    assert r['debt_principal_usd']==700000
    assert r['foreign_currency_debt_usd']==350000
    assert sum(v['debt_draw_usd'] for v in r['rows'])==pytest.approx(700000)
    assert sum(v['principal_usd'] for v in r['rows'])==pytest.approx(700000)
    assert sum(v['renewal_usd'] for v in r['rows'])==160000
    assert r['undiscounted_resource_cost_usd']==1760000
    assert r['undiscounted_public_cash_usd']==pytest.approx(r['undiscounted_resource_cost_usd']+r['total_interest_usd']+r['finance_fees_usd'])
    construction_interest=sum(v['interest_usd'] for v in r['rows'] if v['phase']=='construction')
    assert construction_interest==pytest.approx(700000*.07*2.5)


def city():
    p=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
    return json.loads((p/'engineering/maglev/summary.json').read_text()),json.loads((p/'city.json').read_text())


def test_city_sensitivities_expose_added_scope_energy_and_equal_service_counterfactual():
    report,design=city();s=a.study(report,design)
    assert [r['id'] for r in s['cases']]==['low','base','high']
    totals=[]
    for r in s['cases']:
        assert r['budget_capex_sensitivity_usd']==pytest.approx(r['priced_scope_subtotal_usd']+sum(r['scope_additions_usd'].values()))
        assert r['annual_opex_sensitivity_usd']==sum(r['annual_opex_breakdown_usd'].values())
        assert all(v>0 for v in r['daily_energy_breakdown_kwh'].values())
        f=r['financing'];c=r['equal_service_procurement_sensitivity']
        assert c['debt_principal_usd']==pytest.approx(1.5*f['debt_principal_usd'])
        assert c['annual_level_debt_service_usd']==pytest.approx(1.5*f['annual_level_debt_service_usd'])
        totals.append(r['budget_capex_sensitivity_usd'])
    assert totals==sorted(totals)
    assert s['complete_project_estimate_usd'] is None
    assert s['localisation_fraction'] is None and s['economic_benefit_npv_usd'] is None
    assert s['physical_release'] is False


def test_missing_traction_cannot_produce_free_energy_or_debt_case():
    report,design=city()
    report['lines'][0]['duty']['arrival_events_per_circuit'][0]['station_traction_input_kwh']=None
    s=a.study(report,design)
    for r in s['cases']:
        assert r['annual_opex_sensitivity_usd'] is None
        assert r['financing'] is None
        assert r['equal_service_procurement_sensitivity'] is None


def test_tariff_stress_and_full_equity_do_not_imply_goa4_staff_saving():
    report,design=city();settings=a.load()
    before=a.study(report,design,settings)['cases'][1]
    changed=deepcopy(settings);changed['cases'][1]['electricity_usd_per_kwh']*=2
    changed['cases'][1]['debt_fraction']=0
    after=a.study(report,design,changed)['cases'][1]
    assert after['annual_opex_breakdown_usd']['energy']==2*before['annual_opex_breakdown_usd']['energy']
    assert after['staff_fte_sensitivity']==before['staff_fte_sensitivity']>0
    assert after['financing']['annual_level_debt_service_usd']==0
    assert after['financing']['total_interest_usd']==0


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-1,True])
def test_nonfinite_and_invalid_finance_inputs_rejected(bad):
    with pytest.raises(ValueError):a.loan(100,bad,20)
