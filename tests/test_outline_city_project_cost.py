from copy import deepcopy
from math import fsum
import pytest
from engineering.outline import coordinator, city_project_cost, city_civil
from engineering.design_search import line_benchmark_service
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def context():return coordinator.prepare()


def inputs(context,shape='radial',fallback=False):
    c=dict(input_id='synthetic-city-input',city=dict(slug='fixture',country='XX'),
        lines=[dict(line_id='A',shape=shape,route_m=6000.,stops=[dict(id='a',chainage_m=0.),dict(id='b',chainage_m=3000.),dict(id='c',chainage_m=6000.)])],
        civil_segments=[dict(line_id='A',**{'class':'elevated'},from_m=0.,to_m=6000.)],interchanges=[],source_sha256={})
    r=deepcopy(context['spec']['requirements']);d=deepcopy(context['spec']['design']);r.update(route_km=6.,stations=3,headway_s=200.)
    s=line_benchmark_service.evaluate(r,d,context['vehicle'])
    if shape=='ring':s.update(minimum_turnback_positions_per_end=0,departure_sites=6)
    h=dict(kind='powered-axle-continuous-research',traction_rated_kw_per_car=150.,added_traction_mass_kg_per_car=1000.) if fallback else dict(kind='station-launch-reference')
    return c,[dict(line_id='A',shape=shape,requirements=r,design=d,service=s,propulsion_hypothesis=h)]


def test_complete_city_all_fourteen_scopes_and_accounting_identity(context):
    c,s=inputs(context);original=deepcopy((c,s));v=city_project_cost.evaluate_city_cost(c,s,context)
    assert (c,s)==original
    assert len(v['scope_totals_usd'])==14
    assert all(z['base']>0 for z in v['scope_totals_usd'].values())
    for case in ('low','base','high'):
        assert v['installed_capital_usd'][case]==pytest.approx(fsum(z['costs_usd'][case] for z in v['capital_lines']))
        assert v['whole_life_npv_usd'][case]==pytest.approx(fsum(z['costs_usd'][case] for z in v['capital_lines']+v['lifecycle_lines']))
        assert v['price_per_route_km_usd'][case]==pytest.approx(v['installed_capital_usd'][case]/6.)
    assert v['evaluation_id']==identity({k:z for k,z in v.items() if k!='evaluation_id'})
    assert all(v[k] is False for k in city_project_cost.FLAGS)
    assert v['assumptions']['local_rates_verified'] is False


def test_ring_terminal_quantities_not_copied_from_radial_default(context):
    c,s=inputs(context,'ring');v=city_project_cost.evaluate_city_cost(c,s,context)
    row=next(z for z in v['capital_lines'] if z['key']=='A/terminal-and-line-controls')
    assert row['quantity']['terminals']==0
    assert v['resources']['ring_lines']==1 and v['resources']['radial_lines']==0


def test_powered_axle_fallback_has_vehicle_mass_drive_and_route_power_budget(context):
    c,s=inputs(context,fallback=True);v=city_project_cost.evaluate_city_cost(c,s,context)
    a=next(z for z in v['capital_lines'] if z['key']=='A/powered-axle-traction-collector-protection')
    b=next(z for z in v['capital_lines'] if z['key']=='A/continuous-feed-and-substations')
    assert a['quantity']['added_mass_kg_per_car']==1000 and a['costs_usd']['base']>0
    assert b['quantity']['substations']==2 and b['costs_usd']['base']>0
    assert v['assumptions']['powered_axle_research_lines']==['A']
    assert not any(z['key']=='A/launch-converters' for z in v['capital_lines'])


def test_network_factory_once_at_total_committed_fleet_and_shared_station_access(context):
    c,s=inputs(context);line=deepcopy(c['lines'][0]);line['line_id']='B'
    for x in line['stops']:x['id']='B'+x['id']
    c['lines'].append(line);c['civil_segments'].append(dict(line_id='B',**{'class':'elevated'},from_m=0.,to_m=6000.))
    b=deepcopy(s[0]);b['line_id']='B';s.append(b)
    c['interchanges']=[dict(id='X',platforms=['a','Ba'])]
    v=city_project_cost.evaluate_city_cost(c,s,context)
    assert v['resources']['line_stop_records']==6 and v['resources']['access_sites']==5
    assert sum(z['scope']=='factory-tooling' for z in v['capital_lines'])==1
    row=next(z for z in v['capital_lines'] if z['scope']=='factory-tooling')
    assert row['quantity']['committed_cars']==sum(z['service']['totalcars'] for z in s)
    assert v['resources']['total_trainsets']==2*s[0]['service']['total_trainsets']


def test_mixed_civil_costs_are_positive_without_charging_elevated_deck_at_grade(context):
    c,s=inputs(context);c['civil_segments']=[dict(line_id='A',**{'class':k},from_m=a,to_m=b) for k,a,b in [('at-grade',0,2000),('bridge',2000,4000),('tunnel',4000,6000)]]
    v=city_project_cost.evaluate_city_cost(c,s,context);rows={z['key']:z for z in v['capital_lines']}
    assert rows['repeat-box-beams']['quantity']['spans']==200
    for key in ('surface-formation-drainage-crossings','bridge-special-foundations-deck-temporary','tunnels-portals-lining-ventilation-egress'):
        assert rows[key]['costs_usd']['base']>0


def test_all_surface_city_has_no_free_required_factory_or_empty_cost_scope(context):
    c,s=inputs(context);c['civil_segments'][0]['class']='at-grade'
    v=city_project_cost.evaluate_city_cost(c,s,context)
    assert v['civil']['quantities']['span_count']==0
    assert v['civil']['owned_factory_capital_usd']['base']==0
    assert all(z['base']>0 for z in v['scope_totals_usd'].values())


def test_missing_or_mixed_line_service_cannot_inherit_other_city_result(context):
    c,s=inputs(context)
    with pytest.raises(ValueError):city_project_cost.evaluate_city_cost(c,[],context)
    s[0]['city_input_id']='different'
    with pytest.raises(ValueError):city_project_cost.evaluate_city_cost(c,s,context)


def test_shared_interchange_unknown_platform_rejected(context):
    c,s=inputs(context);c['interchanges']=[dict(id='X',platforms=['a','missing'])]
    with pytest.raises(ValueError):city_project_cost.evaluate_city_cost(c,s,context)
