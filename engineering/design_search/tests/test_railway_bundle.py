from copy import deepcopy
import pytest
from engineering.design_search import railway_bundle as bundles,design_grammar as grammar


def test_body_revision_automatically_changes_architecture_mass_force_and_civil_reactions():
    parent=grammar.build(grammar.parameters());child=grammar.rewrite(parent,'triangulate-underfloor',reason='Real physical revision')
    a,b=bundles.materialize(parent),bundles.materialize(child)
    assert a['candidate_id']!=b['candidate_id'] and a['body_candidate_id']!=b['body_candidate_id']
    assert a['mass']!=b['mass']
    ar,br=bundles.assess_architecture(a),bundles.assess_architecture(b)
    assert ar['trajectory']['peak_required_force_N_per_car']!=br['trajectory']['peak_required_force_N_per_car']
    ac,bc=bundles.assess_civil(a),bundles.assess_civil(b)
    assert ac['alternatives'][0]['maximum_live_moment_Nm']!=bc['alternatives'][0]['maximum_live_moment_Nm']
    assert ac['candidate_id']==a['candidate_id'] and bc['candidate_id']==b['candidate_id']


def test_primary_alternatives_change_geometry_identity_and_wayside_stock_with_same_onboard_mass():
    body=grammar.build(grammar.parameters());x,y=bundles.motor_options()
    a,b=bundles.materialize(body,motor_parameters=x),bundles.materialize(body,motor_parameters=y)
    assert a['mass']==b['mass'] and a['propulsion_component_id']!=b['propulsion_component_id']
    assert a['motor_definition']['bare_primary_stock_kg_per_m']!=b['motor_definition']['bare_primary_stock_kg_per_m']
    assert a['candidate_id']!=b['candidate_id']


def test_new_architecture_equipment_stays_unknown_and_removed_secondary_is_not_still_counted():
    body=grammar.build(grammar.parameters());a=bundles.materialize(body);b=bundles.materialize(body,family='P6')
    old=next(q['mass_kg'] for q in body['retained_equipment_accounts'] if q['id']=='passive-secondary')
    assert a['mass']['accounted_tare_kg_per_car']-b['mass']['accounted_tare_kg_per_car']==pytest.approx(old)
    assert b['unweighed_architecture_equipment'] and b['complete_installed_mass_kg'] is None
    assert b['motor_parameters'] is None and b['motor_definition']['physical_geometry'] is None
    assert all(q['id']!='passive-secondary' for q in b['retained_equipment_accounts'])
    assert all(q['id']!='passive-secondary' for q in b['physical_definition']['equipment_inventory'])
    assert b['physical_definition']['source_body_candidate_id']==body['candidate_id']
    assert 'PVC60' not in str(b['physical_definition'])


def test_bundle_tampering_or_changed_fin_is_refused_before_evaluation():
    body=grammar.build(grammar.parameters());b=bundles.materialize(body);b['mass']['accounted_tare_kg_per_car']+=1
    with pytest.raises(ValueError,match='Modified'):bundles.validate(b)
    m=bundles.motor_options()[0];m['physical']['active_height_m']=.18
    with pytest.raises(ValueError,match='changed onboard secondary'):bundles.materialize(body,motor_parameters=m)


def test_forward_evaluator_cannot_reuse_stale_identity_after_mass_is_changed():
    from engineering.design_search import system_motion
    body=grammar.build(grammar.parameters());b=bundles.materialize(body);b['mass']['accounted_tare_kg_per_car']+=1
    with pytest.raises(ValueError,match='Modified'):system_motion.evaluate(b)


def test_changed_route_materializes_new_bundle_without_changing_vehicle_stock():
    from engineering.design_search import system_motion,route_bundle
    body=grammar.build(grammar.parameters())
    short=route_bundle.materialize(body,distance_m=1500.)
    long=route_bundle.materialize(body,distance_m=2000.)
    assert short['candidate_id']!=long['candidate_id']
    assert short['body_candidate_id']==long['body_candidate_id']
    assert short['propulsion_component_id']==long['propulsion_component_id']
    assert short['mass']==long['mass']
    a,b=system_motion.scenario(short),system_motion.scenario(long)
    assert (a['distance_m'],b['distance_m'])==(1500.,2000.)
    assert a['scenario_id']!=b['scenario_id']
    # Reusing even a correctly formed old scenario/map is not an identity alias.
    stale=dict(schema='osr-station-available-force-map/1',candidate_id=long['candidate_id'],
               motor_component_id=long['propulsion_component_id'],scenario_id=b['scenario_id'])
    assert 'Force map mismatches candidate_id' in system_motion.admit_map(short,stale,a)['reasons']


@pytest.mark.parametrize('distance',[False,0,-1,float('inf'),float('nan')])
def test_invalid_route_distance_is_rejected(distance):
    from engineering.design_search import route_bundle
    body=grammar.build(grammar.parameters())
    with pytest.raises(ValueError,match='positive finite'):route_bundle.materialize(body,distance_m=distance)
