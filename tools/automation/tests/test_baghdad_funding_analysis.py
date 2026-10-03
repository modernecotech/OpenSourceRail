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


def test_prepayment_uses_cash_for_principal_and_premium_and_shortens_maturity():
    from baghdad_funding_analysis import add_draw, debt_month, prepay_vintages
    terms = dict(annual_rate=.12, repayment_months=12, grace_months_from_draw=0)
    loans = []
    add_draw(loans, 0, 1200., terms)
    payment = loans[0]['payment']
    assert prepay_vintages(loans, 505., .01, month=5, minimum_age=6) == (0., 0.)
    for month in range(1, 7): debt_month(loans, month, terms)
    before = loans[0]['balance']
    principal, fee = prepay_vintages(loans, 505., .01, month=6, minimum_age=6)
    assert principal == 500.; assert fee == 5.
    assert loans[0]['balance'] == pytest.approx(before-500.); assert loans[0]['payment'] == payment
    interest, principal = debt_month(loans, 7, terms)
    assert interest == pytest.approx((before-500.)*.01)
    assert principal == pytest.approx(min(before-500., payment-interest))
    debt_month(loans, 8, terms)
    assert loans[0]['balance'] == 0.


def early_inputs(inputs):
    cap, rows, cfg, options = copy.deepcopy(inputs)
    for name in ('chinese_export_credit', 'domestic_bonds', 'bank_credit'):
        cfg[name].update(annual_rate=.06, repayment_months=24, grace_months_from_draw=0)
        options['prepayments']['minimum_age_months'][name] = 0
    cap[0]['imports'] = 400.
    for row in rows:
        row['revenue_usd'] = 2000. if row['month'] == 1 else 0.
        row['opex_usd'] = 10.
    return cap, rows, cfg, options


def test_native_early_payments_follow_obligations_and_buffers_without_borrowing(inputs):
    cap, rows, cfg, options = early_inputs(inputs)
    cfg['model']['debt_service_reserve_months'] = 2
    result = simulate(cap, rows, cfg, options, bridge_rate=.02, repayment_policy='loans_first')
    assert result['monthly'][0]['liquidity_draw_iqd'] > 0
    assert result['monthly'][0]['early_core_principal_usd_equivalent'] == 0
    month = result['monthly'][1]
    assert month['closing_operating_buffer_iqd'] == 30*1300
    assert month['closing_reserve_iqd_equivalent'] == pytest.approx(month['core_debt_service_usd_equivalent']*2*1300)
    assert month['liquidity_draw_iqd'] == 0
    for name, currency in (('bank_credit', 'IQD'), ('domestic_bonds', 'IQD'), ('chinese_export_credit', 'USD')):
        conversion = 1300 if currency == 'IQD' else 1
        assert month[name+'_early_principal_native'] > 0
        assert month[name+'_early_premium_native'] == pytest.approx(month[name+'_early_principal_native']*options['prepayments']['premium'][name])
        assert sum(r[name+'_draw_native']-r[name+'_principal_native']-r[name+'_early_principal_native'] for r in result['monthly'])/conversion == pytest.approx(result['metrics']['core_final_balances_native'][name]/conversion, abs=1e-8)
    assert result['metrics']['maximum_cash_residual_usd'] < 1e-8


def test_uncovered_conditional_cash_cannot_fund_discretionary_principal(inputs):
    cap, rows, cfg, options = early_inputs(inputs)
    options['liquidity']['illustrative_cap_iqd'] = 0
    rows[1]['revenue_usd'] = 0
    result = simulate(cap, rows, cfg, options, bridge_rate=.02, repayment_policy='cost_priority')
    assert result['metrics']['uncovered_support_iqd'] > 0
    assert result['metrics']['early_core_principal_usd_equivalent'] == 0


def test_noncallable_bonds_and_minimum_draw_ages_are_enforced(inputs):
    cap, rows, cfg, options = early_inputs(inputs)
    result = simulate(cap, rows, cfg, options, bridge_rate=.02, repayment_policy='cost_priority', noncallable_bonds=True)
    assert sum(r['domestic_bonds_early_principal_native'] for r in result['monthly']) == 0
    assert sum(r['bank_credit_early_principal_native'] for r in result['monthly']) > 0
    for name in ('bank_credit', 'chinese_export_credit', 'domestic_bonds'):
        options['prepayments']['minimum_age_months'][name] = 6
    locked = simulate(cap, rows, cfg, options, bridge_rate=.02, repayment_policy='cost_priority')
    assert locked['metrics']['early_core_principal_usd_equivalent'] == 0


def test_factory_reserve_uses_actual_remaining_debt_after_prepayment(inputs):
    cap, rows, cfg, options = early_inputs(inputs)
    cap[0].update(factory_capex=1000., factory_imports=400.)
    cfg['model']['debt_service_reserve_months'] = 2
    # Factory DSRA remains active; city opening is outside the projection.
    rows[0]['phases'][0]['opening_month'] = 12
    for r in rows: r.update(factory_reserve_usd=100., factory_debt_service_usd=50.)
    result = simulate(cap, rows, cfg, options, bridge_rate=.02, repayment_policy='loans_first')
    assert result['monthly'][1]['closing_reserve_iqd_equivalent'] > 0
    assert result['monthly'][2]['closing_reserve_iqd_equivalent'] == 0
    assert result['monthly'][2]['reserve_release_iqd_equivalent'] > 0


def test_delivered_early_repayment_cases_reconcile_native_principal_and_cash_savings():
    directory = ROOT/'cities/catalogue/west-asia/Iraq/finance'
    data = json.loads((directory/'baghdad-early-repayment.json').read_text())
    base = data['cases']['gap_only_buffered']; fx = 1300.
    for name, case in data['cases'].items():
        m = case['metrics']
        assert m['maximum_principal_balance_residual_usd'] < .02
        assert m['maximum_cash_residual_usd'] < .02
        assert m['uncovered_support_iqd'] < .02
        assert m['terminal_supplemental_balance_iqd'] == 0
        assert m['government_capital_share'] == pytest.approx(.25)
        assert m['terminal_operating_buffer_iqd'] == base['metrics']['terminal_operating_buffer_iqd']
        assert (m['terminal_cash_iqd']-base['metrics']['terminal_cash_iqd'])/fx == pytest.approx(m['net_finance_cost_saving_vs_buffered_gap_only_usd'], abs=.02)
        for field in ('capex_usd', 'government_usd_cash', 'government_iqd_cash', 'revenue_iqd', 'opex_iqd'):
            assert [r[field] for r in case['monthly']] == [r[field] for r in base['monthly']]
        for facility in ('bank_credit', 'chinese_export_credit', 'domestic_bonds', 'green_bonds'):
            balance = 0.
            rate = {'bank_credit': .09, 'chinese_export_credit': .05, 'domestic_bonds': .08, 'green_bonds': .04}[facility]/12
            for row in case['monthly']:
                expected_interest = balance*rate + row[facility+'_draw_native']*rate/2
                assert row[facility+'_interest_native'] == pytest.approx(expected_interest, abs=.02)
                balance += row[facility+'_draw_native']-row[facility+'_principal_native']-row[facility+'_early_principal_native']
                assert balance == pytest.approx(row[facility+'_closing_balance_native'], abs=.02)
                if row['liquidity_draw_iqd'] > .01 or row['uncovered_support_required_iqd'] > .01:
                    assert row[facility+'_early_principal_native'] == 0
            assert abs(balance) < .02
            for tranche in case['semiannual']:
                rows = [r for r in case['monthly'] if tranche['start_month'] <= r['month'] <= tranche['end_month']]
                assert tranche[facility+'_closing_balance_native'] == rows[-1][facility+'_closing_balance_native']
                for kind in ('principal', 'early_principal', 'early_premium', 'interest'):
                    field = facility+'_'+kind+'_native'
                    assert tranche[field] == pytest.approx(sum(r[field] for r in rows))
        if name == 'cost_priority_noncallable_bonds':
            assert all(r[n+'_early_principal_native'] == 0 for r in case['monthly'] for n in ('domestic_bonds', 'green_bonds'))
    assert data['cases']['cost_priority']['metrics']['all_debt_cleared_month'] < base['metrics']['all_debt_cleared_month']
    assert data['cases']['cost_priority']['metrics']['net_finance_cost_saving_vs_buffered_gap_only_usd'] > data['cases']['loans_then_bonds']['metrics']['net_finance_cost_saving_vs_buffered_gap_only_usd']
