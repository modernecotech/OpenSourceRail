"""Python integration contracts; no native build, solver or research campaign.

Synthetic journey rows below exercise accounting only and never constitute
motion evidence. The real pinned605-type parts/mass inputs are session-scoped.
"""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.station_pair import coordinator,profiles,economics,native_bridge,FLAGS
from engineering.station_rail.common import identity,digest

@pytest.fixture(autouse=True)
def prohibit_native(monkeypatch):
 def forbidden(*args,**kwargs):raise AssertionError('Unit suite must not compile or execute native workloads')
 monkeypatch.setattr(native_bridge,'build',forbidden)
 monkeypatch.setattr(native_bridge,'execute',forbidden)

@pytest.fixture(scope='session')
def data():return coordinator.variants()

def variant(data,family='cable',distance=1500.,index=0):
 return [v for v in data[3] if v['family']==family and v['physical_definition']['station_spacing_m']==distance][index]

def cost(data,v=None,journey=None,**kwargs):
 brief,bundle,reconciliation,_=data
 return economics.evaluate(v or variant(data),journey,bundle,reconciliation,brief,**kwargs)

def fake_journey(v,**changes):
 r=dict(candidate_id=v['candidate_id'],normal_numerical_arrival=True,elapsed_s=120.,grid_energy_j=18e6,
        auxiliary_energy_j=32.55e6,journey_plus_dwell_s=155.,evidence_kind='synthetic-unit-test-accounting-fixture-not-motion-evidence')
 r.update(changes);r['evaluation_id']=identity(r);return r

def test_breadth_is_candidate_specific_and_unselected(data):
 rows=data[3]
 assert {v['family'] for v in rows}=={'cable','powered-wheel','compact-LIM','hybrid'}
 assert len({v['candidate_id'] for v in rows})==len(rows)
 for v in rows:
  assert v['candidate_id']==identity(v['physical_definition'])
  assert v['body_candidate_id']==data[1]['candidate_id'] and v['body_bundle_id']==data[1]['bundle_id']
  assert v['admitted_operating_map'] is False
  for k in FLAGS:assert v[k] is False

@pytest.mark.parametrize('change',['candidate','physical-definition'])
def test_profiles_reject_mixed_physical_candidate(data,change):
 b=deepcopy(data[1])
 if change=='candidate':b['candidate_id']='0'*64
 else:b['physical_definition']['reference_interfaces']['body_length_m']=18
 with pytest.raises(ValueError,match='physical candidate'):profiles.build(b,1500)

def test_real_leaf_interfaces_not_old_brake_or_wheel_defaults(data):
 parts={p['id']:p for p in data[1]['parts']}
 assert len(parts)==605
 assert parts['running/service-actuator']['quantity_per_train']==24
 assert parts['running/brake-disc']['quantity_per_train']==48
 assert parts['running/wheel']['stock']['size_m'][0]==.76
 c=coordinator.case_for(variant(data),data[1],data[2],data[0],speed_km_h=50)
 assert c['brake_force_cap_n']>0 and c['mass_kg']>data[2]['mass_scenarios'][1]['conditional_accounted_train_mass_kg']
 assert data[2]['individual_axle_loads_N'] is None

@pytest.mark.parametrize('family',['cable','powered-wheel'])
def test_force_envelopes_have_source_and_power_limits(data,family):
 v=variant(data,family);brief=data[0]
 p=profiles.force_profile(v,mass_kg=120000,case='base',adhesion=.12,brief=brief)
 assert v['source_ids'] and all(len(h)==64 for h in v['source_sha256'].values())
 assert 0<p['electrical_efficiency']<1 and p['points'][0]['speed_m_s']==0
 assert p['points'][0]['force_n']>0 and p['maximum_speed_m_s']>0
 assert all(b['speed_m_s']>a['speed_m_s'] for a,b in zip(p['points'],p['points'][1:]))
 for q in p['points']:
  assert q['force_n']>=0
  assert q['force_n']*q['speed_m_s']<=p['mechanical_power_w']*(1+1e-12)
  assert q['force_n']<=v['rated_force_ceiling_N']
 assert p['mechanical_power_w']<=p['grid_power_w']*p['electrical_efficiency']

@pytest.mark.parametrize('family',['compact-LIM','hybrid'])
def test_unresolved_architecture_is_held_without_free_force_or_mass(data,family):
 v=variant(data,family)
 assert v['rated_force_ceiling_N'] is None and v['rated_mechanical_power_W'] is None
 assert v['onboard_added_mass_kg'] is None and v['external_mass_kg'] is None
 assert profiles.force_profile(v,mass_kg=120000,case='base',adhesion=.12,brief=data[0]) is None
 c=coordinator.case_for(v,data[1],data[2],data[0],speed_km_h=40)
 assert c['drive'] is None and c['mass_kg']>0


def test_mass_sensitivity_does_not_improve_drive_rating(data):
 v=variant(data);b=data[1];r=data[2];brief=data[0]
 low=coordinator.case_for(v,b,r,brief,speed_km_h=50,mass_case='low')
 high=coordinator.case_for(v,b,r,brief,speed_km_h=50,mass_case='high')
 assert high['mass_kg']>low['mass_kg']
 assert high['drive']['points']==low['drive']['points']
 assert high['drive']['mechanical_power_w']==low['drive']['mechanical_power_w']


def test_force_sensitivity_does_not_change_vehicle_mass(data):
 v=variant(data);b=data[1];r=data[2];brief=data[0]
 low=coordinator.case_for(v,b,r,brief,speed_km_h=50,force_case='low')
 high=coordinator.case_for(v,b,r,brief,speed_km_h=50,force_case='high')
 assert low['mass_kg']==high['mass_kg']
 assert low['drive']['mechanical_power_w']<high['drive']['mechanical_power_w']


def test_wet_adhesion_changes_contact_not_catalogue_torque(data):
 v=variant(data,'powered-wheel');args=(v,data[1],data[2],data[0])
 normal=coordinator.case_for(*args,speed_km_h=50)
 wet=coordinator.case_for(*args,speed_km_h=50,fault='wet')
 assert wet['mass_kg']==normal['mass_kg']
 assert wet['drive']['points']==normal['drive']['points']
 assert 0<wet['drive']['contact_force_cap_n']<normal['drive']['contact_force_cap_n']
 assert wet['brake_adhesion_force_cap_n']<normal['brake_adhesion_force_cap_n']


def test_fault_requests_do_not_edit_nominal_variant(data):
 v=variant(data);before=deepcopy(v)
 c=coordinator.case_for(v,data[1],data[2],data[0],speed_km_h=50,fault='power-loss')
 assert c['fault']['power_loss_at_s']==10 and v==before
 c=coordinator.case_for(v,data[1],data[2],data[0],speed_km_h=50,fault='half-drive')
 assert c['fault']['failed_drive_fraction']==.5 and v==before


def test_hotel_controls_cover_named_compressors_and_do_not_resize_pack(data):
 brief,bundle,reconciliation,_=data
 connected=sum(p.get('proposed_electrical_W_each',0)*p['quantity_per_train'] for p in bundle['parts'] if p['id'].startswith('services/') and 'pv-' not in p['id'])
 c=coordinator.case_for(variant(data),bundle,reconciliation,brief,speed_km_h=50)
 hot=coordinator.case_for(variant(data),bundle,reconciliation,brief,speed_km_h=50,hotel_W_per_car=brief['hot_hotel_control_W_per_car'])
 assert c['auxiliary_power_w']>=connected
 assert hot['auxiliary_power_w']>c['auxiliary_power_w'] and hot['mass_kg']==c['mass_kg']
 assert bundle['physical_definition']['service_battery_topology']['modules_per_car']==75

@pytest.mark.parametrize('change',['vehicle','vehicle-bundle','mass-candidate','mass-payload','variant-geometry'])
def test_cost_rejects_mixed_or_tampered_candidate(data,change):
 brief,bundle,reconciliation,_=data;v=deepcopy(variant(data));r=deepcopy(reconciliation)
 if change=='vehicle':v['body_candidate_id']='0'*64
 elif change=='vehicle-bundle':v['body_bundle_id']='0'*64
 elif change=='mass-candidate':r['candidate_id']='0'*64
 elif change=='mass-payload':r['mass_scenarios'][0]['conditional_accounted_train_mass_kg']+=1
 else:v['physical_definition']['station_spacing_m']+=1
 with pytest.raises(ValueError,match='exact same'):economics.evaluate(v,None,bundle,r,brief)

@pytest.mark.parametrize('change',['candidate','unsealed-energy'])
def test_cost_cannot_inherit_wrong_journey(data,change):
 v=variant(data);j=fake_journey(v)
 if change=='candidate':j['candidate_id']='0'*64
 else:j['grid_energy_j']+=1
 with pytest.raises(ValueError,match='another journey'):cost(data,v,j)


def test_cost_ownership_has_one_shared_support_and_no_parent_price(data):
 c=cost(data);accounts=c['accounts'];owners=[r['owner'] for r in accounts]
 assert len(owners)==len(set(owners))
 rows={r['owner']:r for r in accounts}
 assert rows['shared-pier-foundation-bearings']['quantity']*2==rows['civil-beam-factory']['quantity']+2
 assert rows['wayside-propulsion']['quantity']==2 and rows['station-hotel-battery-chargers']['quantity']==2
 assert rows['rolling-stock-delivered']['quantity']==c['service']['total_trainsets']
 assert all(r['cost_usd']['base']>0 for r in accounts)
 assert 'parent' not in owners and not any('rails_and_fastenings'==r['owner'] for r in accounts)


def test_route_extension_scales_track_not_station_count(data):
 short=cost(data,variant(data,distance=1500));long=cost(data,variant(data,distance=2000))
 a={r['owner']:r for r in short['accounts']};b={r['owner']:r for r in long['accounts']}
 assert b['running-rails']['quantity']>a['running-rails']['quantity']
 assert b['civil-beam-factory']['quantity']>a['civil-beam-factory']['quantity']
 assert a['station-civil-accessibility']['quantity']==b['station-civil-accessibility']['quantity']==2
 assert a['station-common-grid-feed']['cost_usd']==b['station-common-grid-feed']['cost_usd']


def test_civil_quantity_reuse_never_inherits_old_response(data):
 c=cost(data);civil=c['civil_geometry_reference']
 assert civil['numerical_load_case_inherited'] is False
 assert civil['new_axle_moving_loads_required'] is True
 assert civil['crane_capacity_at_actual_radius_known'] is False
 assert civil['required_lifting_mass_base_kg']>civil['nominal_stock_mass_kg']


def test_wrong_civil_geometry_refused(data):
 with pytest.raises(ValueError,match='Civil cost geometry'):cost(data,civil_case='folded_plate--reference')


def test_hybrid_material_mass_not_treated_as_concrete(data):
 with pytest.raises(ValueError,match='all-concrete'):cost(data,civil_case='hybrid_steel_concrete--reference')

@pytest.mark.parametrize('family',['compact-LIM','hybrid'])
def test_unknown_journey_still_has_positive_cost_but_no_zero_energy(data,family):
 c=cost(data,variant(data,family));row=next(r for r in c['accounts'] if r['owner']=='wayside-propulsion')
 assert row['confidence']=='provisional-equipment-reserve' and row['cost_usd']['low']>0
 assert c['service']['runtime_basis']=='explicit provisional maximum-runtime allowance'
 for mode in c['methods']:
  assert mode['whole_life_NPV_usd']['base'] is None
  assert mode['annual_operating']['base']['energy_usd'] is None
 assert c['hotel_charging']['required_average_grid_power_W'] is None


def test_hybrid_booster_budget_not_free(data):
 lim=cost(data,variant(data,'compact-LIM'));hybrid=cost(data,variant(data,'hybrid'))
 a=next(x for x in lim['accounts'] if x['owner']=='wayside-propulsion')
 b=next(x for x in hybrid['accounts'] if x['owner']=='wayside-propulsion')
 assert b['cost_usd']['base']>a['cost_usd']['base']


def test_demand_led_headway_respects_capacity_and_wait(data):
 c=cost(data);brief=data[0];s=c['service']
 assert s['headway_s'] in brief['headway_options_s'] and s['headway_s']<=brief['maximum_wait_s']
 assert s['planning_capacity_pphpd']>=brief['peak_demand_pphpd']
 slower=[h for h in brief['headway_options_s'] if h>s['headway_s'] and h<=brief['maximum_wait_s']]
 assert all(brief['normal_people']*3600/h*brief['planning_occupancy']<brief['peak_demand_pphpd'] for h in slower)
 assert s['total_trainsets']==s['active_trainsets']+s['spare_trainsets'] and s['spare_trainsets']>=1
 assert s['operating_timetable_verified'] is False


def test_capital_components_close_and_setup_not_per_train(data):
 c=cost(data)
 for mode in c['methods']:
  for case in economics.CASES:
   parts=mode['capital_components'][case]
   assert sum(parts.values())==pytest.approx(mode['installed_capital_usd'][case])
   assert mode['capital_per_route_km_usd'][case]*1.5==pytest.approx(mode['installed_capital_usd'][case])
  assert mode['future_order_or_resale_credit'] is False
 assert len({m['capital_components']['base']['direct_accounts'] for m in c['methods']})==1


def test_accounting_journey_is_sealed_without_claiming_motion_evidence(data):
 v=variant(data);j=fake_journey(v);c=cost(data,v,j)
 assert c['journey_evaluation_id']==j['evaluation_id']
 assert c['evaluation_id']==identity({k:v for k,v in c.items() if k!='evaluation_id'})
 assert c['hotel_charging']['required_average_grid_power_W']>0
 assert c['hotel_charging']['actual_charger_map_available'] is False
 for k in FLAGS:assert c[k] is False
 for mode in c['methods']:assert mode['whole_life_NPV_usd']['base']>mode['installed_capital_usd']['base']


def test_sources_are_bound_without_running_native(data):
 hashes=coordinator.source_hashes()
 assert hashes[profiles.ABB]==digest(coordinator.ROOT/profiles.ABB)
 assert hashes[economics.CIVIL]==digest(coordinator.ROOT/economics.CIVIL)
 assert any(n.endswith('.rs') for n in hashes)


def full_fake_native(v,brief,*,complete=True,case=None):
 """Deliberately synthetic coordinator record; never native/physical evidence."""
 elapsed=120. if complete else 0.
 power=6*brief['hotel_W_per_car_hypothesis'] if case is None else case['auxiliary_power_w']
 r=dict(candidate_id=v['candidate_id'],id='unit-accounting-fixture',normal_numerical_arrival=complete,
     elapsed_s=elapsed,journey_plus_dwell_s=elapsed+brief['dwell_s'] if complete else 0.,
     grid_energy_j=18e6 if complete else 0.,auxiliary_energy_j=power*(elapsed+brief['dwell_s']) if complete else 0.,
     state='arrived' if complete else 'held',standstill_holding=complete,energy_residual_j=0.,
     traction_work_j=16e6 if complete else 0.,grade_work_j=0.,maximum_absolute_jerk_m_s3=.2 if complete else 0.,
     maximum_speed_m_s=12. if complete else 0.,berth_error_m=0. if complete else -1500.,
     maximum_acceleration_m_s2=.5 if complete else 0.,terminal_jerk_resolved=False,
     terminal_acceleration_step_m_s2=.1 if complete else 0.,maximum_grid_power_w=400000. if complete else 0.,
     final_position_m=1500. if complete else 0.,
     evidence_kind='synthetic-unit-test-accounting-fixture-not-motion-evidence')
 r['evaluation_id']=identity(r);return r


def test_turnaround_hotel_and_charge_loss_reach_full_grid_summary(data):
 brief,bundle,reconciliation,_=data;v=variant(data,'powered-wheel')
 c=coordinator.case_for(v,bundle,reconciliation,brief,speed_km_h=50)
 j=full_fake_native(v,brief,case=c);priced=cost(data,v,j)
 summary=coordinator._brief_result(v,c,j,priced,brief)
 turn_j=c['auxiliary_power_w']*brief['terminal_turnaround_s']
 assert turn_j==pytest.approx(9.45e6)  #45s at210kW, beyond journey+dwell.
 expected_hotel_grid=(j['auxiliary_energy_j']+turn_j)/brief['hotel_charge_efficiency_hypothesis']/3.6e6
 assert summary['hotel_grid_kwh']==pytest.approx(expected_hotel_grid)
 assert summary['full_grid_kwh']==pytest.approx(j['grid_energy_j']/3.6e6+expected_hotel_grid)
 assert summary['full_grid_kwh']>j['grid_energy_j']/3.6e6+j['auxiliary_energy_j']/3.6e6
 assert summary['reset_grid_kwh']==0  #Wheel variant has no detached tug.
 assert summary['propulsion_peak_grid_MW']==pytest.approx(.4)
 assert 'peak_grid_MW' not in summary


def test_turnaround_increment_is_priced_and_dwell_charger_includes_loss(data):
 brief,bundle,reconciliation,_=data;v=variant(data,'powered-wheel');j=full_fake_native(v,brief)
 zero=deepcopy(brief);zero['terminal_turnaround_s']=0.
 before=economics.evaluate(v,j,bundle,reconciliation,zero)
 after=economics.evaluate(v,j,bundle,reconciliation,brief)
 power=j['auxiliary_energy_j']/j['journey_plus_dwell_s']
 turn_grid_j=power*brief['terminal_turnaround_s']/brief['hotel_charge_efficiency_hypothesis']
 assert after['hotel_charging']['required_average_grid_power_W']-before['hotel_charging']['required_average_grid_power_W']==pytest.approx(turn_grid_j/brief['dwell_s'])
 assert after['hotel_charging']['required_average_grid_power_W']==pytest.approx(6*35000*(120+35+45)/35/.9)
 departures=2*3600/after['service']['headway_s']*brief['operation_hours_day']*brief['operation_days_year']
 for a,b in zip(after['methods'],before['methods']):
  for case in economics.CASES:
   increase=a['annual_operating'][case]['energy_usd']-b['annual_operating'][case]['energy_usd']
   assert increase==pytest.approx(departures*turn_grid_j/3.6e6*brief['tariff_usd_kwh'][case])
 lossy=deepcopy(brief);lossy['hotel_charge_efficiency_hypothesis']=.8
 lower_efficiency=economics.evaluate(v,j,bundle,reconciliation,lossy)
 assert lower_efficiency['hotel_charging']['required_average_grid_power_W']>after['hotel_charging']['required_average_grid_power_W']
 assert lower_efficiency['methods'][0]['annual_operating']['base']['energy_usd']>after['methods'][0]['annual_operating']['base']['energy_usd']

@pytest.mark.parametrize('family',['compact-LIM','hybrid'])
def test_held_summary_retains_unknown_mass_power_and_energy(data,family):
 brief,bundle,reconciliation,_=data;v=variant(data,family)
 c=coordinator.case_for(v,bundle,reconciliation,brief,speed_km_h=50)
 j=full_fake_native(v,brief,complete=False);priced=cost(data,v,j)
 r=coordinator._brief_result(v,c,j,priced,brief)
 for key in ['mass_kg','installed_mass_kg','propulsion_peak_grid_MW','grid_propulsion_kwh','hotel_grid_kwh','reset_grid_kwh','full_grid_kwh','journey_s','actual_peak_km_h']:
  assert r[key] is None
 assert r['accounted_mass_subtotal_kg']>0
 assert r['unquantified_architecture_additions'] is True and r['outline_screen'] is False
 assert r['operating_map_admitted'] is False and r['physical_journey_completed'] is False


def test_fault_followups_replay_nominal_brake_point_without_refitting(data,monkeypatch,tmp_path):
 """Exercise Python orchestration with explicit mocks, not a native campaign."""
 brief=deepcopy(data[0]);brief['speed_caps_km_h']=[50.]
 bundle,reconciliation=data[1:3];v=variant(data,'powered-wheel');nominal_brake=613.25
 captured=[];fit_calls=[]
 def record(c):
  r=full_fake_native(v,brief,case=c);r['id']=c['id'];r['final_position_m']=c['distance_m']
  r['evaluation_id']=identity({k:w for k,w in r.items() if k!='evaluation_id'});return r
 def fit(cases,*args,**kwargs):
  fit_calls.append(len(cases));out=[]
  for c in cases:
   q=deepcopy(c);q['brake_start_m']=nominal_brake;q['id']=identity({k:w for k,w in q.items() if k!='id'})
   out.append((q,record(q)))
  return out
 def execute(cases,*args,**kwargs):
  captured.extend(deepcopy(cases));return [record(c) for c in cases]
 monkeypatch.setattr(coordinator,'variants',lambda root:(brief,bundle,reconciliation,[v]))
 monkeypatch.setattr(coordinator,'source_hashes',lambda root:{'unit-test':'stable-mocked-source'})
 monkeypatch.setattr(coordinator,'fit_brake',fit)
 monkeypatch.setattr(coordinator,'repeated_proxy',lambda *a,**k:dict(state='mock-not-executed',qualified=False))
 monkeypatch.setattr(native_bridge,'build',lambda *a,**k:(None,dict(receipt_id='mock-build-not-executed',binary_sha256='0'*64)))
 monkeypatch.setattr(native_bridge,'execute',execute)
 result=coordinator._run(tmp_path,coordinator.ROOT)
 assert fit_calls==[1]  #Only the nominal controller is fitted.
 fault_requests=[c for c in captured if c['fault']['power_loss_at_s'] is not None or c['fault']['failed_drive_fraction'] or c['fault']['emergency_at_m'] is not None]
 assert len(fault_requests)>=3
 assert all(c['brake_start_m']==nominal_brake for c in fault_requests)
 assert result['finalists'][0]['controller_basis']=='Fixed nominal brake point; no per-fault berth refit'
 assert all(x['request']['brake_start_m']==nominal_brake for x in result['finalists'][0]['cases'])
 assert result['available_operating_maps_added']==0 and result['regeneration_saving_credited'] is False
