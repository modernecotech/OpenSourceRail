"""Physical consistency and fail-closed requirements for the v0.6 reference."""
from copy import deepcopy
from pathlib import Path
import pytest
from engineering.development_baseline import ROOT,INPUT,selection,evaluate,FLAGS
from engineering.station_rail import vehicle,comparison
from engineering.station_rail.common import identity

@pytest.fixture(scope='module')
def current():return evaluate.build(ROOT)

def test_selected_physical_identity_roundtrips_and_keeps_services(current):
    v=current['vehicle'];d=v['physical_definition']
    assert v['candidate_id']==identity(dict(physical_definition=d,**{k:v[k] for k in ('body_candidate_id','support_component_id','propulsion_component_id')}))
    assert v['support_counts']['wheels_per_train']==48
    assert d['vehicle']['onboard_traction_motors']==0
    assert d['vehicle']['onboard_traction_battery_kWh']==0
    assert d['vehicle']['onboard_permanent_magnets']==0
    assert current['service']['electrical']['battery']['gross_energy_kWh']==pytest.approx(82.8)
    assert v['mass']['accounted_cap_loaded_kg_per_car']-v['mass']['accounted_tare_kg_per_car']==3450.
    assert v['mass']['installed_tare_kg_per_car'] is None
    assert v['residual_overlap_unresolved']['overlap_amount_kg'] is None
    assert all(current[k] is val for k,val in FLAGS.items())

def test_physical_limitations_do_not_become_successful_journeys(current):
    s=current['service'];p=s['selected_scenario']['profile']
    assert p['actual_traction_force_available_N'] is None
    assert not p['physical_journey_completed']
    assert s['selected_station']['length_m']>=s['selected_station']['required_shared_winding_m']
    assert s['station_drive_bound_map']['available_force_N_per_car'] is None
    assert any(not row['reachable'] for row in s['longest_retained_gap_cases'])
    assert current['vehicle']['underframe_screens']['normal']['deflection_screen']=='fail'
    assert current['service']['service']['normal_capacity_pphpd_arithmetic']==8280.
    assert not current['service']['service']['physical_headway_qualified']
    assert next(g for g in current['gates'] if g['gate']=='city-regeneration')['state']=='hold'

def test_same_actual_civil_tendons_under_all_selected_loads(current):
    c=current['civil'];assert c['executed_case_count']==39
    reference=c['selected_reference'];assert reference['span_m']==20.
    cases=list(c['selected_physical_load_checks'].values())
    assert len(cases)==3
    assert {r['prestress_strands'] for r in cases}=={reference['prestress_strands']}
    assert all(r['physical_civil_component_id']==c['civil_component_id'] for r in cases)
    assert all(r['necessary_longitudinal_screen']=='pass' for r in cases)
    assert {r['load_case'] for r in cases}=={'empty','normal','crowd_control'}

def test_mixed_evaluation_and_unpriced_superiority_are_rejected(current):
    wrong=deepcopy(current);wrong['service']['selected_station']['length_m']=350.
    with pytest.raises(ValueError,match='differs'):evaluate.validate(wrong)
    result=comparison.evaluate(current)
    assert result['mass_change_from_v05_kg_per_car']>0
    assert result['economics_acceptance']=='unknown'
    assert all(r['whole_life_cost_USD'] is None for r in result['alternatives'])

@pytest.mark.parametrize('old,new',[('launch_speed_cap_m_s = 20.0','launch_speed_cap_m_s = 30.0'),
    ('floor_top_above_rail_m = 1.0','floor_top_above_rail_m = 0.35'),
    ('passenger_doors_total_per_car = 2','passenger_doors_total_per_car = 4')])
def test_selector_cannot_relabel_unchanged_physics(tmp_path,monkeypatch,current,old,new):
    (tmp_path/'engineering/station_rail').mkdir(parents=True)
    for name in (INPUT,'engineering/station_rail/brief.toml'):
        (tmp_path/name).write_bytes((ROOT/name).read_bytes())
    monkeypatch.setattr(vehicle,'build',lambda root:current['vehicle'])
    assert selection.load(tmp_path)['vehicle']['candidate_id']==current['candidate_id']
    text=(tmp_path/INPUT).read_text();assert old in text;(tmp_path/INPUT).write_text(text.replace(old,new))
    with pytest.raises(ValueError,match='mirrors'):selection.load(tmp_path)
