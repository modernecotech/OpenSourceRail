"""Modular station geometry, load paths, actual plant positions and scope holds."""
from copy import deepcopy
from math import fsum
import pytest
from engineering.railway_progress import civil as c,identity
from engineering.railway_progress import alternatives as a
from engineering.railway_progress.tests.test_alternatives import vehicle as base_vehicle


@pytest.fixture(scope='module')
def definition(base_vehicle):
    v=deepcopy(base_vehicle);v['interfaces']=dict(floor_top_above_rail_m=1.0257,door_side_y_m=-1.41)
    v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    alt=a.evaluate(v,distance_m=1500.)
    return c.geometry_definition(v,1500.,alt)


def test_platforms_are_transportable_separate_net_components_not_monoliths(definition):
    decks=[p for p in definition['stock'] if p['role']=='station-cassette']
    assert len(decks)==40
    assert all(p['dimensions_m']==[5.5,4.5,.18] for p in decks)
    assert all(p['dimensions_m'][0]<20. for p in decks)
    assert not any(p['dimensions_m'][0]==110. for p in decks)
    for station in definition['station_records']:
        assert station['platform_side']==-1 and station['platform_top_above_declared_rail_m']==1.0257
        assert len(station['cassettes'])==20 and len(station['girders'])==20 and len(station['supports'])==22
        for deck in station['cassettes']:
            assert deck['concrete_net_volume_m3']+deck['steel_volume_m3']==pytest.approx(deck['gross_outer_volume_m3'])
    assert len([p for p in definition['stock'] if p['role']=='cassette-rebar'])==40*134


def test_station_dead_and_crowd_loads_reach_columns_and_ground_conservatively(definition):
    r=c.generate('a'*64,definition)
    assert abs(r['station_dead_force_residual_N'])<1e-5
    assert r['station_crowd_weight_N']==pytest.approx(2*110*4.5*5000.)
    assert r['station_known_to_ground_N']==pytest.approx(r['station_known_dead_weight_N'])
    assert r['station_support_count']==44
    for station in r['stations']:
        assert abs(station['dead_force_residual_N'])<1e-5 and abs(station['crowd_force_residual_N'])<1e-5
        assert fsum(s['crowd_N'] for s in station['supports'])==pytest.approx(station['crowd_N'])
        assert all(s['known_superstructure_dead_N']>0 and s['crowd_N']>0 for s in station['supports'])
        assert all(s['complete_service_pressure_Pa'] is None and not s['bearing_accepted'] for s in station['supports'])
    assert r['complete_installed_mass_kg'] is None and r['unknown_mass_items'] and r['unknown_plant_mass_items']
    assert not r['physical_accepted'] and not r['actual_dynamic_wheel_rail_or_plant_forces_validated']


def test_pinch_plant_masses_are_located_and_reconciled_without_global_averaging(definition):
    r=c.generate('a'*64,definition)
    assert r['known_plant_mass_kg']>80400.
    assert abs(r['known_plant_assignment_residual_N'])<1e-6
    assert abs(r['known_guideway_force_residual_N'])<1e-4
    p=definition['known_plant_loads'];assert all('x_m' in x for x in p)
    assert max(x['x_m'] for x in p)<420.
    assert r['guideway_supports_with_unknown_plant_mass'] and max(r['guideway_supports_with_unknown_plant_mass'])<40


def test_halfspan_uniform_load_reactions_preserve_exact_longitudinal_application():
    assert c.uniform_reactions(2.,8.,100.,0.,10.)==pytest.approx([50.,50.])
    assert c.uniform_reactions(8.,12.,100.,0.,10.)==pytest.approx([5.,45.])
    assert c.uniform_reactions(8.,12.,100.,10.,20.)==pytest.approx([45.,5.])


def test_evaluation_pressure_changes_loads_without_changing_hardware_geometry(base_vehicle):
    v=deepcopy(base_vehicle);v['interfaces']=dict(floor_top_above_rail_m=1.0257,door_side_y_m=-1.41);v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    alt=a.evaluate(v,distance_m=1500.)
    one=c.geometry_definition(v,1500.,alt,platform_crowd_pressure_Pa=3000.)
    two=c.geometry_definition(v,1500.,alt,platform_crowd_pressure_Pa=5000.)
    assert one['physical_geometry_id']==two['physical_geometry_id'] and one['definition_id']!=two['definition_id']
    assert c.generate('a'*64,two)['station_crowd_weight_N']>c.generate('a'*64,one)['station_crowd_weight_N']


def test_hardware_placement_revision_changes_physical_civil_definition(base_vehicle):
    v=deepcopy(base_vehicle);v['interfaces']=dict(floor_top_above_rail_m=1.0257,door_side_y_m=-1.41);v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    first=a.evaluate(v,distance_m=1500.);second=a.revise(v,first,{'bank_starts_m':[-12.,90.,192.,294.,396.]})
    assert c.geometry_definition(v,1500.,first)['physical_geometry_id']!=c.geometry_definition(v,1500.,second)['physical_geometry_id']


def test_construction_counts_moulds_joints_bearings_and_unknown_rigging(definition):
    r=c.generate('a'*64,definition)
    assert len(r['construction_sequence'])==40
    assert len([p for p in r['stock'] if p['role']=='cassette-joint-and-retention'])==80
    assert len([p for p in r['stock'] if p['role']=='station-girder-bearing'])==80
    assert all(p['complete_hook_mass_kg'] is None and p['rigging_mass_kg'] is None and p['QA_certificate'] is None for p in r['construction_sequence'])
    assert all(p['candidate_id']=='a'*64 for p in r['stock'])


def test_candidate_and_resealed_geometry_mismatch_cannot_be_published(definition):
    with pytest.raises(ValueError):c.generate('g'*64,definition)
    forged=deepcopy(definition);forged['stock'][0]['dimensions_m'][0]=1.
    forged['definition_id']=identity({k:x for k,x in forged.items() if k!='definition_id'})
    with pytest.raises(ValueError,match='geometry'):c.generate('a'*64,forged)


def test_station_column_capital_bearing_girder_and_deck_have_no_floating_vertical_gaps(definition):
    parts={p['id']:p for p in definition['stock']};station='station/0'
    column=parts[station+'/support/0/0/column'];capital=parts[station+'/support/0/0/capital']
    bearing=parts[station+'/girder/0/0/bearing/0'];girder=parts[station+'/girder/0/0/concrete'];deck=parts[station+'/cassette/0/concrete']
    assert column['at_m'][2]+column['dimensions_m'][2]==pytest.approx(capital['at_m'][2])
    assert capital['at_m'][2]+capital['dimensions_m'][2]==pytest.approx(bearing['at_m'][2])
    assert bearing['at_m'][2]+bearing['dimensions_m'][2]==pytest.approx(girder['at_m'][2])
    assert girder['at_m'][2]+girder['dimensions_m'][2]+.02==pytest.approx(deck['at_m'][2])
    rail=next(p for p in definition['stock'] if p['role']=='rail')
    assert rail['at_m'][2]+rail['dimensions_m'][2]==pytest.approx(definition['geometry']['rail_top_global_z_m'])


def test_guideway_duct_concrete_strand_and_grout_do_not_double_count_volume(definition):
    parts={p['id']:p for p in definition['stock']};base='guideway/span/0';beam=parts[base+'/box'];grout=parts[base+'/strand-duct-grout']
    duct=beam['geometry']['ducts']['net_void_volume_m3'];strand=sum(p['net_volume_m3'] for p in parts.values() if p['assembly']==base and p['role']=='prestressing-strand')
    assert beam['net_volume_m3']+duct==pytest.approx(20*(1.8*.8-1.5*.5))
    assert grout['net_volume_m3']+strand==pytest.approx(duct)
