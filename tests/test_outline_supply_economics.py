from copy import deepcopy
from math import fsum
from pathlib import Path
import json
import pytest

from engineering.outline import coordinator, supply_economics as supply
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def study():return supply.benchmark()


def row(study,scenario,mode='cable-capstan'):
    return next(x for x in study['variants'] if (x['scenario'],x['mechanism'])==(scenario,mode))


def test_reference_is_reproduced_and_new_rates_do_not_change_service(study):
    original=json.loads((Path(ROOT)/'docs/design-engine/line30-benchmark/result.json').read_bytes())
    source=next(x for x in original['variants'] if x['mechanism']=='cable-capstan')
    assert row(study,'reference-rates')['installed_capital_usd']==source['installed_capital_usd']
    assert study['requirements_id']==original['requirements_id']
    assert study['service']['total_trainsets']==52 and study['service']['totalcars']==312
    assert len(study['variants'])==9
    assert all(study[k] is False for k in supply.FLAGS)


def test_complete_scenarios_have_all_scopes_and_independent_capital_sum(study):
    for variant in study['variants']:
        details=variant['details'];scopes={x['scope'] for x in details['capital']+details['lifecycle']}
        assert len(scopes)==14
        for case in supply.CASES:
            independent=fsum(x['costs_iqd'][case] for x in details['capital'])/1510
            assert variant['installed_capital_usd'][case]==independent
            assert variant['whole_life_npv_usd'][case]>=independent
    assert row(study,'project-make-buy')['installed_capital_usd']['base']<row(study,'reference-rates')['installed_capital_usd']['base']


def test_factory_cost_and_land_footprint_counted_once(study):
    details=row(study,'project-make-buy')['details'];factory=supply._row(details['capital'],'project-production-buildings-and-tooling')
    q=factory['quantity'];land=supply._row(details['capital'],'land-and-utility-relocation')['quantity']
    for case in supply.CASES:
        assert factory['costs_iqd'][case]==pytest.approx(q['vehicle_campaign_iqd'][case]+q['civil_campaign_iqd'][case])
    assert details['production']['moulds']==[11,27,54]
    # Civil yard already includes its covered casting floor: land is not floor+yard again.
    c=details['civil'];fast=c['assumptions']['fastener_floor_m2_charged_in_own_capital']
    assert land['precast_factory_yard_m2'][1]==max(c['precast_floor_m2'][1],c['precast_yard_m2'][1])+fast[1]
    assert supply._row(row(study,'china-bulk-buy')['details']['capital'],'project-production-buildings-and-tooling')['quantity']['precast_factory_building_m2']==[0.,0.,0.]


def test_future_fleet_includes_setup_but_no_unneeded_precast_renewal(study):
    d=row(study,'project-make-buy')['details'];fleet=supply._row(d['capital'],'delivered-and-assembled-fleet')
    renew=supply._row(d['lifecycle'],'scheduled-renewals')
    events=[e for e in renew['quantity']['events'] if e.get('vehicle_factory_setup_included_once') and e['case']=='base']
    assert len(events)==1 and events[0]['year']==20
    expected=(fleet['costs_iqd']['base']+d['production']['vehicle_campaign_capital_iqd']['base'])/1.04**20
    assert events[0]['present_value_iqd']==pytest.approx(expected)
    factory=supply._row(d['capital'],'project-production-buildings-and-tooling')
    assert not any(e['line_id']==factory['line_id'] for e in renew['quantity']['events'])


def test_landed_duty_is_not_applied_again_and_physical_work_reserves_stay(study):
    old=row(study,'reference-rates')['details'];new=row(study,'project-make-buy')['details']
    tax=supply._row(new['capital'],'tax-and-import-duty-provision')
    for i,c in enumerate(supply.CASES):
        assert tax['costs_iqd'][c]==pytest.approx(tax['quantity']['unallocated_equipment_base_iqd'][c]*tax['quantity']['fraction'][i],abs=.011)
    for key in ('routine-maintenance','decommissioning','annual-electricity','operations-staff'):
        assert supply._row(old['lifecycle'],key)['costs_iqd']==supply._row(new['lifecycle'],key)['costs_iqd']


def test_equipment_not_substituted_with_incompatible_teaser_and_copper_not_forced_lower(study):
    new=row(study,'project-make-buy')['details'];reference=coordinator.prepare()['vehicle_cost']
    by={x['line_key']:x for x in reference['lines']}
    for item in new['vehicle']['vehicle_cost']['lines']:
        if item['line_key']=='unlocated-account/retained-comfort/HVAC':assert item['cost_iqd']==by[item['line_key']]['cost_iqd']
    assert new['drive']['copper_usd_per_kg_before_wire_conversion']>12
    assert all(x['no_additional_bulk_discount'] for x in new['drive']['module_budget'])


def test_shared_cache_and_unsupported_context_cannot_reuse_a_wrong_currency_or_factory(study):
    context=coordinator.prepare();spec=deepcopy(context['spec']);civil=row(study,'project-make-buy')['details']['civil']['civil']
    # The API requires the original quantity record, not a previously revalued one.
    from engineering.design_search import line_benchmark_civil
    original=line_benchmark_civil.evaluate(spec['requirements'],spec['design'],context['vehicle'])
    spec['design']['production_years']=4
    with pytest.raises(ValueError,match='production domain'):
        supply.evaluate_case(spec,context['vehicle'],context['vehicle_cost'],study['service'],original,context['assumptions'],'cable-capstan','project-make-buy')
    spec=context['spec'];changed=deepcopy(spec);changed['currency']['iqd_per_usd']=1400
    with pytest.raises(ValueError,match='currency contexts differ'):
        supply.evaluate_case(changed,context['vehicle'],context['vehicle_cost'],study['service'],original,context['assumptions'],'cable-capstan','project-make-buy')


def test_compact_supply_publication_replays_without_committing_bulky_runs(tmp_path):
    state=tmp_path/'state';out=tmp_path/'compact'
    supply.publish(state);m=supply.publish_compact(state,out)
    assert supply.verify_compact(out)['manifest_id']==m['manifest_id']
    assert sum(p.stat().st_size for p in out.iterdir())<100000
    assert {p.name for p in out.iterdir()}=={'summary.json','manifest.json'}
    data=json.loads((out/'summary.json').read_bytes());data['variants'][0]['installed_capital_usd']['base']=0
    (out/'summary.json').write_text(json.dumps(data))
    with pytest.raises(ValueError,match='payload differs'):supply.verify_compact(out)
