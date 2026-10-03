"""Gap debt has a financing cost; labels and duplicate receipts are not money."""
import copy
import json
from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/automation'))
sys.path.insert(0, str(ROOT/'design/city-generation/src'))
from baghdad_funding_analysis import capital_projection, price_operating, simulate, validate_options
from osr_scenario.iraq_finance import city_funding_config


@pytest.fixture
def inputs():
    cfg = city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()), 'baghdad')
    cfg['model']['debt_service_reserve_months'] = 0
    for name in ('chinese_export_credit', 'domestic_bonds', 'bank_credit'):
        cfg[name].update(annual_rate=0., arrangement_fee=0., grace_months_from_draw=0, repayment_months=1)
    options = tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    options['additional_sources'].update(climate_capital_grant_usd=0., net_development_rights_usd=0., incremental_net_local_receipts_annual_usd=0.)
    rows = [{'month': month, 'revenue_usd': 2000. if month == 2 else 0., 'opex_usd': 0.,
             'factory_debt_service_usd': 0., 'factory_reserve_usd': 0., 'chinese_commitment_fee_usd': 0.} for month in range(3)]
    rows[0]['phases'] = [{'opening_month': 0, 'weight': 1.}]
    cap = {0: {'capex': 1000., 'imports': 0., 'candidate_capex': 1000., 'candidate_imports': 0.}}
    return cap, rows, cfg, options


def test_gap_draw_finances_its_own_fees_and_interest_then_sweeps_cash(inputs):
    cap, rows, cfg, options = inputs
    result = simulate(cap, rows, cfg, options, bridge_rate=.12, bridge_fee=.01)
    draw = 750/(1-.01-.12/24)
    assert result['monthly'][1]['liquidity_draw_iqd']/1300 == pytest.approx(draw)
    assert result['monthly'][1]['liquidity_draw_fee_iqd']/1300 == pytest.approx(draw*.01)
    assert result['monthly'][1]['liquidity_interest_iqd']/1300 == pytest.approx(draw*.12/24)
    assert result['metrics']['terminal_supplemental_balance_iqd'] == 0
    assert result['metrics']['terminal_cash_iqd']/1300 == pytest.approx(2000-draw-draw*.12/12)
    assert result['metrics']['uncovered_support_iqd'] == 0
    assert result['metrics']['maximum_cash_residual_usd'] < 1e-8


def test_facility_cap_is_visible_and_does_not_invent_another_loan(inputs):
    cap, rows, cfg, options = inputs
    options['liquidity']['illustrative_cap_iqd'] = 500*1300
    result = simulate(cap, rows, cfg, options, bridge_rate=.12, bridge_fee=.01)
    assert result['monthly'][1]['liquidity_draw_iqd'] == 500*1300
    assert result['monthly'][1]['uncovered_support_required_iqd']/1300 == pytest.approx(257.5)
    assert result['metrics']['maximum_cash_residual_usd'] < 1e-8
    assert result['metrics']['government_capital_share'] == .25


def test_green_label_is_not_an_extra_source_or_interest_saving(inputs):
    cap, rows, cfg, options = inputs
    reference = simulate(cap, rows, cfg, options)
    label = simulate(cap, rows, cfg, options, green='label')
    assert label['metrics']['green_bonds_iqd'] > 0
    assert label['metrics']['ordinary_bonds_iqd']+label['metrics']['green_bonds_iqd'] == reference['metrics']['ordinary_bonds_iqd']
    assert label['metrics']['uncovered_support_iqd'] == reference['metrics']['uncovered_support_iqd']
    assert label['metrics']['terminal_cash_iqd'] == reference['metrics']['terminal_cash_iqd']


def test_eligible_grant_replaces_domestic_debt_without_increasing_government(inputs):
    cap, rows, cfg, options = inputs
    options['additional_sources'].update(climate_capital_grant_usd=100., climate_grant_first_month=0)
    reference = simulate(cap, rows, cfg, options)
    funded = simulate(cap, rows, cfg, options, extras=True)
    assert funded['metrics']['climate_grant_iqd'] == 100*1300
    assert funded['metrics']['ordinary_bonds_iqd'] == reference['metrics']['ordinary_bonds_iqd']-75*1300
    assert funded['metrics']['bank_capital_iqd'] == reference['metrics']['bank_capital_iqd']-25*1300
    assert funded['metrics']['government_capital_share'] == .25
    options['additional_sources']['climate_capital_grant_usd'] = 2000.
    with pytest.raises(ValueError, match='exceeds'):
        simulate(cap, rows, cfg, options, extras=True)


def test_negative_or_boolean_options_and_usd_gap_credit_are_rejected(inputs):
    for group, key, value in [('green', 'blended_rate', -.1), ('green', 'share_of_candidate_bonds', True),
                              ('liquidity', 'currency', 'USD'), ('model', 'tranche_months', 0)]:
        options = copy.deepcopy(inputs[-1]); options[group][key] = value
        with pytest.raises(ValueError): validate_options(options)


def test_independent_capital_projection_preserves_cost_and_origin(inputs):
    cfg = inputs[2]
    rows = capital_projection([{'budget_usd': 1000., 'imported_share': .45, 'bucket': 'solar_plant',
                                'planned_start_day': 0, 'planned_finish_day': 260}], cfg, {'solar_plant'})
    assert set(rows) == {0, 7, 13, 17}
    assert sum(r['capex'] for r in rows.values()) == 1000
    assert sum(r['imports'] for r in rows.values()) == 450
    assert sum(r['candidate_capex'] for r in rows.values()) == 1000


def price_inputs(options):
    rows = [{'month': month, 'revenue_usd': 100., 'opex_usd': 50.} for month in range(13)]
    rows[0]['phases'] = [{'opening_month': 0, 'weight': .5}, {'opening_month': 12, 'weight': .5}]
    receipts = {'farebox_annual_usd': 80., 'total_annual_usd': 100., 'planning_monthly_income_iqd': 1000.}
    return rows, receipts, options


def test_matching_fare_and_income_inflation_preserves_real_price_and_inflates_opex(inputs):
    rows, receipts, options = price_inputs(inputs[-1])
    projected, prices = price_operating(rows, receipts, 10., 1300., options,
                                       annual_fare=.05, annual_income=.05, annual_opex=.05, elasticity=-.3)
    assert projected[12]['fare_revenue_usd'] == pytest.approx(84.)
    assert projected[12]['nonfare_revenue_usd'] == pytest.approx(20.)  # no invented lease indexation
    assert projected[12]['opex_usd'] == pytest.approx(52.5)
    assert prices['full_opening']['demand_multiplier'] == pytest.approx(1.)
    assert prices['full_opening']['forty_four_trips_income_share'] == pytest.approx(.44)


def test_fare_increase_reduces_demand_when_income_does_not_keep_up(inputs):
    rows, receipts, options = price_inputs(inputs[-1])
    projected, prices = price_operating(rows, receipts, 10., 1300., options, annual_fare=.05, elasticity=-.3)
    assert prices['full_opening']['demand_multiplier'] == pytest.approx(1.05**(-.3))
    assert projected[12]['fare_revenue_usd'] == pytest.approx(80*1.05**.7)
    assert projected[12]['opex_usd'] == 50.
    assert prices['full_opening']['forty_four_trips_income_share'] > .44


def test_peak_offpeak_prices_use_each_segments_demand_and_respect_capacity(inputs):
    rows, receipts, options = price_inputs(inputs[-1])
    projected, prices = price_operating(rows, receipts, 10., 1300., options,
                                       peak_share=.4, peak_multiplier=1.25, offpeak_multiplier=.9, elasticity=-.3)
    revenue_factor = .4*1.25**.7+.6*.9**.7
    demand = .4*1.25**(-.3)+.6*.9**(-.3)
    assert projected[0]['fare_revenue_usd'] == pytest.approx(80*revenue_factor)
    assert prices['first_opening']['average_paid_fare_iqd'] == pytest.approx(10*revenue_factor/demand)
    assert prices['first_opening']['peak_fare_iqd'] == 12.5
    assert prices['first_opening']['offpeak_fare_iqd'] == 9.
    _, discounted = price_operating(rows, receipts, 10., 1300., options, offpeak_multiplier=.01, elasticity=-1.)
    assert discounted['first_opening']['demand_multiplier'] == 2.


def test_delivered_reconciliation_and_each_six_month_envelope_balance():
    data = json.loads((ROOT/'cities/catalogue/west-asia/Iraq/finance/baghdad-finance-reconciliation.json').read_text())
    rec = data['reconciliation']; fx = data['iqd_per_usd']
    receipts = data['operating_receipts']
    assert receipts['total_annual_usd'] == pytest.approx(receipts['farebox_annual_usd'] + receipts['existing_nonfare_annual_usd'])
    assert receipts['existing_nonfare_annual_usd'] == pytest.approx(receipts['station_retail_annual_usd'] + receipts['station_advertising_annual_usd'])
    programme = json.loads((ROOT/'cities/catalogue/west-asia/Iraq/finance/baghdad-programme.json').read_text())
    city = json.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/summary.json').read_text())
    assert receipts['total_annual_usd'] == pytest.approx(city['cases']['low_capacity_use']['annual_revenue_usd'])
    assert rec['lifetime_revenue_usd'] == pytest.approx(sum(row['revenue_usd'] for row in programme['phased_opening']['cases']['low_demand']['monthly']))
    assert abs(rec['capital_difference_usd']) < .05
    assert rec['gross_additional_liquidity_usd']-rec['later_retained_cash_usd'] == pytest.approx(rec['net_lifetime_liquidity_gap_usd'])
    assert all(a['passed'] for a in rec['debt_audits'])
    for case in data['cases'].values():
        metrics = case['metrics']
        assert metrics['government_capital_share'] == pytest.approx(.25)
        assert metrics['maximum_cash_residual_usd'] < .02
        assert all(row['fare_receipts_iqd']+row['nonfare_receipts_iqd'] == pytest.approx(row['revenue_iqd']) for row in case['monthly'])
        assert max(metrics['core_final_balances_native'].values()) < .02
        assert metrics['peak_supplemental_balance_iqd'] <= data['assumptions']['liquidity']['illustrative_cap_iqd']+.02
        for tranche in case['semiannual']:
            assert tranche['end_month']-tranche['start_month'] <= 5
            assert abs(tranche['capital_reconciliation_usd']) < .05
        assert sum(r['liquidity_draw_iqd'] for r in case['semiannual']) == pytest.approx(metrics['total_supplemental_draw_iqd'])
        assert case['semiannual'][-1]['closing_liquidity_debt_iqd'] == metrics['terminal_supplemental_balance_iqd']
    assert data['cases']['blended_candidate']['metrics']['terminal_supplemental_balance_iqd'] > 0
    assert data['additional_receipts_threshold']['incremental_net_receipts_annual_usd'] > data['assumptions']['additional_sources']['incremental_net_local_receipts_annual_usd']
    if data['fare_uplift_threshold']['metrics']:
        solved = data['fare_uplift_threshold']['metrics']
        assert solved['terminal_supplemental_balance_iqd']+solved['uncovered_support_iqd'] <= fx
