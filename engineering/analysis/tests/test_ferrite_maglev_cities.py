"""Current city inputs, fixed topology, energy accounting and provenance."""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from engineering.ferrite_maglev import cities, model


@pytest.fixture(scope='module')
def context():
    return model.load()


@pytest.fixture(scope='module')
def assumptions():
    return tomllib.loads(cities.ASSUMPTIONS.read_text())


def source_consist(aw2=720, aw3=960):
    return dict(passenger_capacity=aw2, crush_capacity=aw3)


def test_baghdad_six_car_capacity_and_storage_are_preserved(context):
    f = cities.formation(context[1], source_consist(), [])
    assert (f['cars'], f['aw2_passengers'], f['aw3_passengers']) == (6, 720, 960)
    assert f['gross_storage_kwh'] == 6*30
    assert f['nominal_body_length_m'] == 102
    assert f['tare_mass_kg'] == 6*14200
    assert f['aw2_mass_kg'] == 6*23200 and f['aw3_mass_kg'] == 6*26200
    assert f['eol_normal_window_kwh'] == pytest.approx(6*30*.8*.6)
    assert f['overall_length_m'] is None and f['formation_qualified'] is False


def test_aw3_and_profile_each_independently_prevent_capacity_loss(context):
    assert cities.formation(context[1], source_consist(360, 641), [])['cars'] == 5
    assert cities.formation(context[1], source_consist(360, 480), [source_consist(720, 960)])['cars'] == 6
    assert cities.formation(context[1], source_consist(100, 130), [])['cars'] == 1


@pytest.mark.parametrize('aw2,aw3', [(0, 160), (True, 160), (120, -1), (120.0, 160)])
def test_capacity_fails_closed(context, aw2, aw3):
    with pytest.raises(ValueError):
        cities.formation(context[1], source_consist(aw2, aw3), [])


def stations(*chainages):
    return [dict(id=f's{i}', s_m=s, lat=33+i*.001, lon=44, platform_length_m=59.5) for i,s in enumerate(chainages)]


def test_ring_closure_is_reconciled_against_full_geographic_length():
    line = dict(name='r', shape='ring', length_m=10000, ring_wrap_length_m=500)
    ordered, legs, closure = cities.station_legs(line, stations(2000, 5000, 9500))
    assert legs == [3000, 4500, 2500]
    assert sum(legs) == line['length_m'] and closure == 2500
    assert [s['s_m'] for s in ordered] == [2000, 5000, 9500]


def test_radial_duty_keeps_unserved_geographic_ends():
    _, legs, closure = cities.station_legs(dict(name='x', shape='radial', length_m=10000), stations(500, 4000, 9500))
    assert sum(legs) == 10000 and closure is None


@pytest.mark.parametrize('points', [(0,0), (0,11000), (0,)])
def test_invalid_station_geometry_is_rejected(points):
    with pytest.raises(ValueError):
        cities.station_legs(dict(name='x', shape='radial', length_m=10000), stations(*points))


def simple_duty(distance, hot=False, regen=True, speed=80):
    # Independent test plant: 10 m/s and 1 kWh/km, with no hidden station energy.
    return dict(moving_seconds=distance/10, moving_energy_kwh=distance/1000,
                achieved_speed_kmh=36, hotel_kw=60 if hot else 40,
                pure_trajectory_screen_pass=True,station_zone_screen_pass=True,
                kinematic_screen_pass=True,kinematic_hold=None)


def test_radial_fleet_is_recomputed_with_explicit_slow_loops(context, assumptions):
    f = cities.formation(context[1], source_consist(360,480), [])
    result = cities.line_plan(context[1], assumptions, f, dict(name='x', shape='radial', length_m=2000),
                              stations(0,1000,2000), dict(schedule=[dict(headway_min=3)], trainset_count=809), simple_duty)
    assert result['topology']['mainline_switches'] == 0
    assert result['topology']['terminal_loop_count'] == 2
    assert result['topology']['added_single_direction_loop_beam_m'] == pytest.approx(400*math.pi)
    assert result['topology']['loop_speed_screen_kmh'] == 20
    assert result['topology']['loop_lateral_acceleration_screen_m_s2'] == pytest.approx((20/3.6)**2/100)
    assert result['duty']['conservative_cycle_seconds'] == pytest.approx(400+40*math.pi+4*result['charging']['dwell_seconds'])
    assert result['fleet']['peak'] == 5 and result['fleet']['total'] == 7
    assert result['depot']['storage_slots'] == 7
    assert result['depot']['minimum_total_storage_track_m'] == 7*62
    assert result['fleet']['source_fleet_inherited'] is False
    assert result['topology']['exclusive_shuttle_alternative']['minimum_independent_lanes'] == 4
    assert result['duty']['hot_aw3_no_regen_cycle_kwh'] == pytest.approx((4+0.4*math.pi+60*4*result['charging']['dwell_seconds']/3600)*3)


def test_loop_lateral_limit_rejects_mainline_speed(context, assumptions):
    a=deepcopy(assumptions); a['topology']['terminal_loop_speed_screen_kmh']=80
    f=cities.formation(context[1], source_consist(360,480), [])
    with pytest.raises(ValueError, match='lateral acceleration'):
        cities.line_plan(context[1], a, f, dict(name='x', shape='radial', length_m=2000),
                         stations(0,1000,2000), dict(schedule=[dict(headway_min=3)], trainset_count=1), simple_duty)


def test_ring_fleet_includes_both_independent_directions(context, assumptions):
    f=cities.formation(context[1], source_consist(360,480), [])
    r=cities.line_plan(context[1], assumptions, f, dict(name='r', shape='ring', length_m=2000, ring_wrap_length_m=100),
                       stations(0,1000), dict(schedule=[dict(headway_min=3)], trainset_count=1), simple_duty)
    assert r['fleet']['peak']==4 and r['fleet']['total']==6
    assert r['topology']['terminal_loop_count']==0
    assert r['topology']['ring_wrap_discrepancy_m']==900
    assert r['topology']['exclusive_shuttle_alternative'] is None


def test_long_gap_extends_charging_and_exposes_berth_pressure(context, assumptions):
    f=cities.formation(context[1], source_consist(720,960), [])
    r=cities.line_plan(context[1], assumptions, f, dict(name='x',shape='radial',length_m=10000),
                       stations(0,10000), dict(schedule=[dict(headway_min=.5)],trainset_count=1), simple_duty)
    charge=r['charging']; dwell=charge['dwell_seconds']
    assert dwell>60 and charge['candidate_kw_per_train']==6*200
    assert r['selected_peak_headway_seconds']>=r['planning_minimum_headway_seconds']>190
    assert not charge['dwell_exceeds_peak_headway']
    assert charge['minimum_parallel_platform_berths_per_direction']==math.ceil(dwell/r['selected_peak_headway_seconds'])
    # Charge covers incoming leg + loop + services during full dwell, DC only.
    received=200*(dwell-15)/3600
    required=10+0.2*math.pi+60*dwell/3600
    assert received >= required
    assert charge['grid_pv_storage_sizing_accepted'] is False


def test_real_city_package_preserves_demand_and_binds_sources(context, tmp_path):
    city=ROOT/'cities/catalogue/central-africa/Angola/Benguela'
    design_hash=cities.digest(city/'city.json')
    r=cities.generate(city, context=context, output_dir=tmp_path)
    records=json.loads((tmp_path/'retained-records.json').read_text())
    assert records['retained_station_demand_records']==json.loads((city/'benguela.stations.json').read_text())
    assert records['city']==json.loads((city/'city.json').read_text())['city']
    assert cities.digest(city/'city.json')==design_hash
    assert all(cities.digest(ROOT/p)==value for p,value in r['source_sha256'].items())
    assert r['retained_records_sha256']==cities.digest(tmp_path/'retained-records.json')
    assert r['costs']['city_total_usd'] is None and not r['costs']['old_city_costs_inherited']
    for case in r['costs']['scenarios']:
        assert case['complete_city_programme_usd'] is None
        assert not case['epc_included'] and not case['supplier_quotes']
        assert case['priced_scope_subtotal_usd']==case['repeat_fleet_allowance_usd']+case['ordinary_elevated_allowance_usd']+case['station_electrical_allowance_usd']
    assert all(not r[k] for k in model.FLAGS)
    assert all(g['state']=='open' and not g['accepted'] for g in r['gates'])


def replay_fixture(context, assumptions):
    f=cities.formation(context[1],source_consist(360,480),[])
    line=cities.line_plan(context[1],assumptions,f,dict(name='x',shape='radial',length_m=2000),
                          stations(0,1000,2000),dict(schedule=[dict(headway_min=3)],trainset_count=809),simple_duty)
    return dict(schema='osr-maglev-city-planning/1',city='fixture',physical_release=False,
                source_sha256={str(p.relative_to(ROOT)):cities.digest(p) for p in [Path(cities.__file__),*cities.calculation_dependencies()]},lines=[line])


def test_replay_missed_charge_losses_and_ledger_close(context, assumptions):
    plan=replay_fixture(context,assumptions)
    complete=cities.replay_city(plan,missed_charge_events=(),charger_efficiency=.9)['lines'][0]
    missing=cities.replay_city(plan,missed_charge_events=(1,),charger_efficiency=.9)['lines'][0]
    assert missing['events'][0]['missed_charge']
    assert missing['events'][0]['supply_dc_kwh']==0
    assert missing['events'][0]['departure_energy_kwh'] < complete['events'][0]['departure_energy_kwh']
    assert complete['energy_totals']['charger_loss_kwh']==pytest.approx(complete['energy_totals']['supply_dc_kwh']*.1)
    assert complete['energy_totals']['curtailed_pack_energy_kwh']>0
    assert complete['energy_ledger_residual_kwh']==pytest.approx(0,abs=1e-9)
    assert missing['energy_ledger_residual_kwh']==pytest.approx(0,abs=1e-9)
    assert missing['emergency_reserve_passed'] is None
    assert not missing['route_acceptance'] and not missing['force_acceptance']
    assert missing['elapsed_seconds']==pytest.approx(2*plan['lines'][0]['duty']['conservative_cycle_seconds'])


def test_replay_reveals_energy_failure_without_clipping_or_claiming_reserve(context,assumptions):
    plan=replay_fixture(context,assumptions)
    r=cities.replay_city(plan,cycles=5,start_soc=.21,charger_efficiency=.01,missed_charge_events=(1,))
    assert not r['normal_window_passed']
    line=r['lines'][0]
    assert line['breaches'] and line['energy_ledger_residual_kwh']==pytest.approx(0,abs=1e-9)
    assert line['final_energy_kwh'] < line['minimum_normal_energy_kwh']
    assert r['emergency_reserve_passed'] is None and r['protected_emergency_energy_kwh'] is None


def test_station_regeneration_never_credits_services_pack_with_same_compiled_events(context,assumptions):
    plan=replay_fixture(context,assumptions)
    a=cities.replay_city(plan,regen_available=False,missed_charge_events=(1,))
    b=cities.replay_city(plan,regen_available=True,missed_charge_events=(1,))
    assert a['lines'][0]['energy_totals']['motion_kwh']==pytest.approx(b['lines'][0]['energy_totals']['motion_kwh'])
    assert b['regeneration_available'] and not a['regeneration_available']
    assert a['lines'][0]['final_energy_kwh']==pytest.approx(b['lines'][0]['final_energy_kwh'])
    assert a['compiled_plan_sha256']==b['compiled_plan_sha256']


@pytest.mark.parametrize('options',[dict(charger_efficiency=0),dict(charger_efficiency=1.1),dict(start_soc=True),
                                   dict(cycles=0),dict(cycles=101),dict(missed_charge_events=(0,))])
def test_replay_invalid_inputs_fail_closed(context,assumptions,options):
    with pytest.raises(ValueError):
        cities.replay_city(replay_fixture(context,assumptions),**options)


def test_replay_rejects_changed_compiled_sources(context,assumptions):
    plan=replay_fixture(context,assumptions)
    key=next(iter(plan['source_sha256']));plan['source_sha256'][key]='0'*64
    with pytest.raises(ValueError,match='sources changed'):
        cities.replay_city(plan)


def test_primary_entry_notice_is_idempotent_and_replaces_stale_content(tmp_path):
    original=b'# Stale city output\r\n\r\nFleet 809; total $12345.\r\n'
    path=tmp_path/'README.md';path.write_bytes(original)
    (tmp_path/'city.json').write_text(json.dumps(dict(name='Example',city=dict(slug='example'))))
    cities.promote_city_readme(tmp_path)
    first=path.read_bytes()
    assert original not in first and b'$12345' not in first
    assert first.startswith(cities.NOTICE_START)
    assert b'engineering/maglev/README.md' in first
    assert b'Example' in first
    cities.promote_city_readme(tmp_path)
    assert path.read_bytes()==first
    assert first.count(cities.NOTICE_START)==1


def test_city_source_inventory_is_unique_complete_and_read_only():
    index_hash=cities.digest(cities.INDEX)
    paths=cities.source_paths()
    assert paths==sorted(set(paths))
    assert cities.INDEX in paths and cities.ASSUMPTIONS in paths and Path(cities.__file__) in paths
    for design in (ROOT/'cities/catalogue').glob('*/*/*/city.json'):
        assert design in paths
        for filename in ('summary.json','manufacturing.json','network.svg'):
            assert design.parent/'engineering/maglev'/filename in paths
        assert design.parent/'README.md' in paths
    assert cities.digest(cities.INDEX)==index_hash


def test_slug_cache_invalidates_same_size_edit_with_restored_mtime(tmp_path):
    path=tmp_path/'city.json';path.write_text(json.dumps(dict(city=dict(slug='alpha'),climate=dict(preset='hot'))))
    assert cities.city_slug(path)=='alpha'
    previous=path.stat();hits=cities._cached_city_slug.cache_info().hits
    assert cities.city_slug(path)=='alpha'
    assert cities._cached_city_slug.cache_info().hits==hits+1
    path.write_text(path.read_text().replace('alpha','bravo'))
    os.utime(path,ns=(previous.st_atime_ns,previous.st_mtime_ns))
    assert path.stat().st_size==previous.st_size and path.stat().st_mtime_ns==previous.st_mtime_ns
    assert cities.city_slug(path)=='bravo'


def test_cli_unknown_city_and_missing_design_exit_cleanly(capsys,tmp_path):
    for arguments in (['not-an-existing-city'],['--design',str(tmp_path/'missing/city.json')]):
        with pytest.raises(SystemExit) as result:
            cities.main(arguments)
        assert result.value.code==2
        error=capsys.readouterr().err
        assert 'error:' in error and 'Traceback' not in error


def test_index_preflight_rejects_changed_output_binding_and_missing_index(tmp_path):
    index=json.loads(cities.INDEX.read_text())
    index['cities'][0]['summary_sha256']='0'*64
    index['city_count']=1
    copied=tmp_path/'index.json';copied.write_text(json.dumps(index))
    r=cities.verify_index(copied)
    assert not r['current'] and any('SHA-256 differs' in e for e in r['errors'])
    assert any('exact current catalogue' in e for e in r['errors'])
    assert not cities.verify_index(tmp_path/'missing.json')['current']


def test_generated_index_covers_every_retained_city_and_package_bytes():
    preflight=cities.verify_index()
    assert preflight['current'],preflight['errors']
    assert preflight['checked_outputs']==5*preflight['expected_city_count']
    index=json.loads(cities.INDEX.read_text())
    designs=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'cities/catalogue').glob('*/*/*/city.json'))
    assert index['catalogue_design_paths']==designs
    assert index['city_count']==len(designs)==len(index['cities'])
    assert len({r['catalogue_path'] for r in index['cities']})==len(designs)
    current={}
    for city in index['cities']:
        output=ROOT/city['package_path']
        assert cities.digest(output/'summary.json')==city['summary_sha256']
        report=json.loads((output/'summary.json').read_text())
        for path,expected in report['source_sha256'].items():
            if path not in current:
                current[path]=cities.digest(ROOT/path)
            assert current[path]==expected, (city['city'],path)
        assert cities.digest(output/'retained-records.json')==city['retained_records_sha256']
        assert cities.digest(output/'README.md')==city['readme_sha256']
        for filename,key in (('manufacturing.json','manufacturing_sha256'),('network.svg','network_sha256')):
            assert cities.digest(output/filename)==city[key]==report[key]
        assert report['manufacturing_file']=='manufacturing.json' and report['network_file']=='network.svg'
        entry=(ROOT/city['catalogue_path']/'README.md').read_bytes()
        assert entry.startswith(cities.NOTICE_START) and b'engineering/maglev/README.md' in entry
        assert city['complete_city_programme_usd'] is None and not city['physical_release']


@pytest.mark.parametrize('filename,key', [('manufacturing.json','manufacturing_sha256'),('network.svg','network_sha256')])
def test_index_preflight_rejects_changed_manufacturing_or_map_receipt(tmp_path,filename,key):
    index=json.loads(cities.INDEX.read_text())
    index['cities'][0][key]='0'*64
    copied=tmp_path/'index.json';copied.write_text(json.dumps(index))
    result=cities.verify_index(copied)
    assert not result['current']
    assert any('SHA-256 differs' in error and filename in error for error in result['errors'])


@pytest.mark.parametrize('filename,key', [('manufacturing.json','manufacturing_sha256'),('network.svg','network_sha256')])
def test_index_preflight_rejects_missing_manufacturing_or_map_receipt(tmp_path,filename,key):
    index=json.loads(cities.INDEX.read_text())
    del index['cities'][0][key]
    copied=tmp_path/'index.json';copied.write_text(json.dumps(index))
    result=cities.verify_index(copied)
    assert not result['current']
    assert any('SHA-256 differs' in error and filename in error for error in result['errors'])


def test_city_platform_and_storage_follow_shared_coupling_configuration(context,assumptions,monkeypatch):
    from engineering.ferrite_maglev import configuration
    original=configuration.document
    def changed(path):
        result=original(path)
        if Path(path)==configuration.INPUT:result['formation']['coupling_gap_assumption_m']=.75
        return result
    baseline=cities.formation(context[1],source_consist(360,480),[])
    monkeypatch.setattr(configuration,'document',changed)
    f=cities.formation(context[1],source_consist(360,480),[])
    assert f['overall_length_assumption_m']-baseline['overall_length_assumption_m']==.5
    r=cities.line_plan(context[1],assumptions,f,dict(name='x',shape='radial',length_m=2000),
        stations(0,1000,2000),dict(schedule=[dict(headway_min=3)]),simple_duty)
    expected=51+2*.75+assumptions['formation']['platform_end_allowance_m']
    assert r['stations'][0]['provisional_platform_body_plus_allowance_m']==expected
    assert r['depot']['minimum_total_storage_track_m']==r['fleet']['total']*expected
    assert f['overall_length_m'] is None and f['formation_qualified'] is False
