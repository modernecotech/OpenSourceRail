"""Electrical quantities, adverse controls and independently rederived receipts."""
from copy import deepcopy
import gzip
import json
import math
import shutil
import pytest
from engineering.ferrite_maglev import drive_design as d


def test_winding_covers_every_slot_once_and_scales_actual_material():
    a=d.load();w=d.winding(a)
    assert sorted([n for c in w['schedule'] for n in (c['start_slot'],c['return_slot'])])==list(range(1,31))
    assert all(c['return_slot']-c['start_slot']==3 for c in w['schedule'])
    assert {p:sum(c['phase']==p for c in w['schedule']) for p in 'ABC'}==dict(A=5,B=5,C=5)
    assert (w['face_cassettes_per_station'],w['coils_per_station'],w['electrical_sections_per_station'])==(560,8400,56)
    assert w['copper_kg_per_station']==pytest.approx(8400*1.5*350e-6*8960)
    assert d.winding(a,turns=4)['copper_kg_per_station']==pytest.approx(4*w['copper_kg_per_station'])
    assert d.winding(a,bar_area=500.)['resistance_hot_per_phase_group_ohm']==pytest.approx(w['resistance_hot_per_phase_group_ohm']*350/500)
    assert d.winding(a,zone=200.)['face_cassettes_per_station']==320


def test_support_counts_real_copper_and_does_not_hide_failed_fit_or_adopt_mass():
    v=d.support();coil=v['coil']
    assert (v['physical_coils_per_car'],v['circuits_per_car'])==(72,48)
    assert coil['length_m']==pytest.approx(50*.508)
    assert v['copper_kg_per_train']==pytest.approx(coil['copper_kg']*432)
    assert v['packing_screen'] and v['legacy_depth_fit']
    alternatives=d.support_alternatives(d.load())
    assert [r['provisional_screens_pass'] for r in alternatives]==[True,False,False]
    assert not alternatives[1]['result']['legacy_depth_fit']
    assert not alternatives[2]['result']['loads'][-1]['continuous_current_screen']
    assert not v['added_to_existing_mass_ledger'] and not v['magnetic_map_qualified']
    assert all(not v[k] for k in d.model.FLAGS)


def test_phase_budget_is_worst_case_and_fails_excess_time_error():
    a=d.load();v=d.phase_budget(a)
    assert v['total_mdeg']==pytest.approx(sum(v['contributions_mdeg'].values()))
    assert v['screen_pass']
    a['launch']['time_uncertainty_ns']=1_000_000
    assert not d.phase_budget(a)['screen_pass']


@pytest.fixture(scope='module')
def profile():
    _,c,_=d.model.load();mass=d.model.mass(c,c['mass']['ferrite_base'],50.)['aw3_kg']
    return d.corridor.profile(distance_m=2000.,runtime_s=140.,cars=6,car_mass_kg=mass)


def test_dc_energy_is_not_a_complete_braking_sink_and_1700v_device_is_rejected(profile):
    v=d.dc_system(d.load(),profile)
    assert v['nominal_capacitor_energy_j']==pytest.approx(.5*.08*2400**2)
    assert v['voltage_headroom_energy_j']==pytest.approx(.5*.08*(2550**2-2400**2))
    assert v['mechanical_arrival_energy_j']>100*v['voltage_headroom_energy_j']
    assert not v['capacitor_covers_assumed_clearance']
    assert not v['lone_1700v_two_level_switch_eligible']
    assert v['two_simultaneous_arrivals_peak_w']==2*v['mechanical_arrival_peak_w']
    assert not v['qualified']
    assert v['services_charger_input_w_per_train']==2400000.
    suburban=d.corridor.profile(distance_m=5000.,runtime_s=375.,cars=6,car_mass_kg=profile['inputs']['car_mass_kg'],mode='suburban')
    assert d.dc_system(d.load(),suburban)['services_charger_input_w_per_train']==3600000.


def test_electrical_screen_retains_voltage_failures_and_power_identity(profile):
    a=d.load();one=d.electrical_screen(a,profile,turns=1,inductance=.000025)
    four=d.electrical_screen(a,profile,turns=4,inductance=.0015)
    assert one['force_power_identity_residual_w']<1e-6
    assert four['force_power_identity_residual_w']<1e-6
    assert max(g['peak_current_a'] for g in four['groups'])==pytest.approx(max(g['peak_current_a'] for g in one['groups'])/4)
    assert not four['current_voltage_screen']
    assert one['omitted_powered_samples']==0
    assert not one['qualified']


def test_bom_counts_parents_and_explicit_imported_unselected_parts():
    rows={r['id']:r for r in d.bom()}
    assert rows['SUP-BRIDGE']['per_six_car_train']==288
    assert rows['SUP-COIL']['per_six_car_train']==432
    assert rows['SUP-SWITCH']['per_six_car_train']==288*4
    assert rows['LSM-IGBT']['per_two_direction_station']==96
    assert rows['LSM-COPPER']['accounting_parent']=='LSM-COIL'
    assert all(r['unit_price_usd'] is None and r['ordered_part'] is None and not r['accepted'] for r in rows.values())


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    path=tmp_path_factory.mktemp('drive-design')/'packet';d.publish(path);return path


def test_retained_actual_execution_has_positive_tracking_and_adverse_controls(packet):
    v=d.read_json(packet/'study.json.gz',True)
    assert len(v['software_replays'])==17
    assert all(r['control_pass']=='true' and r['physical_output_authorised']=='false' for r in v['software_replays'])
    assert all(len(r)==9 for r in v['profiles'].values())
    assert v['profiles']['suburban'][0]['omitted_powered_samples']>0
    assert all(not v[k] for k in d.model.FLAGS)


@pytest.mark.parametrize('field',['coil-mass','phase','hold','release','execution','api-stream'])
def test_rehashed_forged_design_and_execution_are_rejected(packet,tmp_path,field):
    out=tmp_path/'packet';shutil.copytree(packet,out)
    name='execution.json.gz' if field in {'execution','api-stream'} else 'study.json.gz';v=d.read_json(out/name,True)
    if field=='coil-mass':v['support']['copper_kg_per_train']=0.
    elif field=='phase':v['phase_budget']['screen_pass']=False
    elif field=='hold':v['open_gates']=[]
    elif field=='release':v['physical_release']=True
    elif field=='api-stream':v['api']['stdout']=v['api']['stdout'].replace(' ... ok',' ... ignored',1)
    else:v['replay']['stdout']=v['replay']['stdout'].replace('true','false',1)
    (out/name).write_bytes(gzip.compress(d.encoded(v),mtime=0))
    m=json.loads((out/'manifest.json').read_text());m['files_sha256'][name]=d.digest((out/name).read_bytes());(out/'manifest.json').write_bytes(d.encoded(m))
    with pytest.raises(ValueError):d.verify(out)


def test_stale_source_symlink_extra_and_inflate_bounds(packet,tmp_path,monkeypatch):
    out=tmp_path/'packet';shutil.copytree(packet,out)
    m=json.loads((out/'manifest.json').read_text());m['source_sha256']['invented']='0'*64;(out/'manifest.json').write_bytes(d.encoded(m))
    with pytest.raises(ValueError,match='source'):d.verify(out)
    (out/'extra').write_text('unowned')
    with pytest.raises(ValueError,match='inventory'):d.verify(out)
    monkeypatch.setattr(d,'MAX_RAW',10)
    with pytest.raises(ValueError,match='inflate'):d.read_json(packet/'study.json.gz',True)
