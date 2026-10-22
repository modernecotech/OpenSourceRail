"""Independent path, stock, flow, outage and publication controls."""
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
import shutil

import pytest

from engineering.ferrite_maglev import hub_access as access


def straight(identity,length,start=0.):
    return dict(id=identity,points_xyz_m=[[start,0.,8.],[start+length,0.,8.]],chainages_m=[0.,length],length_m=length)


def test_overlapping_intervals_are_unioned_and_duplicates_are_rejected():
    values=access.canonical_intervals([dict(id='a',alignment_id='trunk',interval_m=[0.,100.]),
        dict(id='b',alignment_id='trunk',interval_m=[40.,150.]),dict(id='c',alignment_id='other-level',interval_m=[0.,100.])])
    assert [(v['alignment_id'],v['interval_m']) for v in values]==[('other-level',[0.,100.]),('trunk',[0.,150.])]
    with pytest.raises(ValueError,match='duplicate component'):
        access.canonical_intervals([dict(id='x',alignment_id='trunk',interval_m=[0.,100.])]*2)


def test_continuous_routes_share_exact_support_position_but_keep_bearing_seats():
    g=access.kit_geometry([straight('left',50.,-50.),straight('right',50.)],3.,access.load())
    assert (g['horizontal_length_m'],g['deck_bays'],g['unique_support_positions'],g['independent_bearing_seats'])==(100.,4,5,8)
    common=next(p for p in g['supports'] if p['coordinate_xyz_m']==[0.,0.,8.])
    assert common['bearing_seats']==2
    assert not g['shared_foundation_cost_credit'] and not common['foundation_accepted']
    assert sum(u['length_m'] for u in g['units'])==100.
    assert all(u['length_m']<=25. for u in g['units'])


def test_bend_gets_support_and_polyline_length_is_not_shortened_to_chord():
    points=[[0.,0.,8.],[20.,0.,8.],[20.,20.,8.]];points,lengths=access.polyline(points)
    g=access.kit_geometry([dict(id='bend',points_xyz_m=points,chainages_m=lengths,length_m=40.)],3.,access.load())
    assert g['horizontal_length_m']==40. and g['deck_bays']==2 and g['unique_support_positions']==3
    assert math.dist(points[0],points[-1])<g['horizontal_length_m']
    assert any(p['coordinate_xyz_m']==[20.,0.,8.] for p in g['supports'])


def test_duplicate_physical_routes_and_spans_are_rejected_instead_of_double_counted():
    a=access.load()
    with pytest.raises(ValueError,match='duplicate physical route'):
        access.kit_geometry([straight('one',25.),straight('one',25.)],3.,a)
    with pytest.raises(ValueError,match='duplicate physical span'):
        access.kit_geometry([straight('one',25.),straight('same-place-other-name',25.)],3.,a)


def test_segment_intersections_and_collinear_overlaps_do_not_pass_clearance():
    assert access.segment_distance([0.,0.],[10.,10.],[0.,10.],[10.,0.])==0.
    assert access.segment_distance([0.,0.],[10.,0.],[5.,0.],[20.,0.])==0.
    assert access.segment_distance([0.,0.],[10.,0.],[0.,4.],[10.,4.])==4.


def transfer_geometry():
    routes=[]
    for identity,end,line in [('south',-80.,'outer-a'),('north',80.,'outer-b')]:
        routes.append(dict(id=identity,kind='offset-corridor',points_xyz_m=[[12.,0.,8.],[12.,end,8.]],
            chainages_m=[0.,80.],length_m=80.,source_line=line))
    for identity,y,line in [('middle',0.,'middle'),('south',-80.,'outer-a'),('north',80.,'outer-b')]:
        routes.append(dict(id=identity+'-spur',kind='platform-interface-spur',points_xyz_m=[[0.,y,8.],[12.,y,8.]],
            chainages_m=[0.,12.],length_m=12.,source_line=line))
    return access.kit_geometry(routes,3.,access.load())


def test_all_platform_pairs_use_exact_graph_and_crossbranch_skips_middle_spur():
    a=access.load();geometry=transfer_geometry();matrix=access.walking_matrix(geometry,a)
    assert matrix['platform_pair_count']==3
    outer=next(p for p in matrix['pairs'] if {p['from_line'],p['to_line']}=={'outer-a','outer-b'})
    arms=[p for p in matrix['pairs'] if 'middle' in {p['from_line'],p['to_line']}]
    assert outer['horizontal_walk_m']==184. # 80+80 corridor and two 12 m outer spurs.
    assert outer['reference_corridor_edges_m']==160. and outer['platform_interface_spurs_m']==24.
    assert outer['platform_spurs_used']==['north-spur','south-spur']
    assert all(p['horizontal_walk_m']==104. for p in arms)
    assert outer['horizontal_walk_m']==sum(p['horizontal_walk_m'] for p in arms)-24.
    assert outer['walk_minutes']['1.0']==pytest.approx(184/60)
    assert outer['walk_minutes']['0.6']==pytest.approx(184/.6/60)
    assert len(outer['physical_unit_path'])==len(set(outer['physical_unit_path']))
    assert outer['rest_bays_on_path']==3 and outer['maximum_distance_between_rest_or_endpoint_m']==50.
    assert matrix['all_pairs_rest_spacing_screen_pass']
    assert all(not p['vertical_movements_lifts_queues_heat_and_service_wait_included'] for p in matrix['pairs'])


def test_connected_arm_patterns_need_counted_middle_rest_bay():
    geometry=transfer_geometry();junction=[r for r in geometry['rest_bays'] if r.get('junction_rest_bay')]
    assert len(junction)==1 and junction[0]['additional_deck_area_m2']==3.
    original_area=geometry['total_deck_area_m2']
    geometry['rest_bays']=[r for r in geometry['rest_bays'] if not r.get('junction_rest_bay')]
    matrix=access.walking_matrix(geometry,access.load())
    outer=next(p for p in matrix['pairs'] if {p['from_line'],p['to_line']}=={'outer-a','outer-b'})
    assert outer['maximum_distance_between_rest_or_endpoint_m']==100.
    assert not outer['adopted_rest_spacing_screen_pass'] and not matrix['all_pairs_rest_spacing_screen_pass']
    assert original_area==pytest.approx((80.*2+12.*3)*3.+3*3.)


def test_disconnected_platform_interface_is_rejected_as_a_route():
    geometry=transfer_geometry();geometry['units']=[u for u in geometry['units'] if u['route_id']!='middle-spur']
    with pytest.raises(ValueError,match='disconnected proposed transfer graph'):
        access.walking_matrix(geometry,access.load())


def test_rhs_area_inertia_recovered_independently_and_no_composite_plate_credit():
    a=access.load();s=access.section('steel-twin-rhs',3.,a);b=.4;h=.8;t=.016
    expected_area=2*(b*h-(b-2*t)*(h-2*t))+3*.008
    expected_i=2*(b*h**3-(b-2*t)*(h-2*t)**3)/12
    assert s['stock_area_m2']==pytest.approx(expected_area)
    assert s['gross_inertia_m4']==pytest.approx(expected_i)
    assert s['structural_mass_kg_m']==pytest.approx(expected_area*7850.)


def test_unfactored_beam_equilibrium_and_handling_load_are_explicit():
    a=access.load();g=access.kit_geometry([straight('test',25.)],3.,a);r=access.structure(g,'steel-twin-rhs',a);bay=r['bays'][0]
    total=(bay['dead_load_kn_m']+bay['pedestrian_load_kn_m'])*25.
    assert 2*bay['unfactored_shear_kn']==pytest.approx(total)
    assert bay['unfactored_moment_kn_m']==pytest.approx(total*25./8)
    assert r['largest_complete_span_stock_lift_kg']==pytest.approx(r['total_structural_stock_kg'])
    assert not bay['handling_and_erection_verified']
    assert not r['reference_load_combinations_implemented'] and not r['rest_bay_cantilevers_analysed']


def test_concrete_gross_section_never_implies_tensile_or_cracked_design_pass():
    a=access.load();r=access.structure(access.kit_geometry([straight('test',25.)],3.,a),'concrete-twin-i',a)
    assert r['section']['cracked_stiffness_and_reinforcement_design_open']
    assert r['section']['stress_limit_pa'] is None
    assert all(row['steel_reference_elastic_stress_screen_pass'] is None for row in r['bays'])
    assert r['reinforcement_stock_kg']>0 and not r['engineering_accepted']


def test_accessible_ramp_accounts_for_landings_rise_and_nonoverlap():
    a=access.load();r=access.ramp(8.,3.,a)
    assert len(r['runs'])==16 and r['intermediate_landings']==15 and r['end_landings']==2
    assert sum(run['rise_m'] for run in r['runs'])==8.
    assert all(run['gradient']==pytest.approx(.05) and run['horizontal_run_m']==10. for run in r['runs'])
    assert r['surface_length_m']==pytest.approx(16*math.hypot(10.,.5)+15*3.6+6.)
    assert r['footprint_area_m2']==pytest.approx(16.*57.)
    assert r['parallel_lanes_do_not_overlap']
    assert r['independent_step_free_route_after_total_lift_power_loss']
    assert not r['obstacles_and_ground_levels_accepted']


def test_queue_conserves_people_and_repeated_pulses_expose_narrow_bottleneck():
    a=access.load();narrow=access.queue(480,3.,180.,a);wide=access.queue(480,6.6,180.,a)
    for row in (narrow,wide):
        assert row['arrivals_people']==pytest.approx(1920.)
        assert row['arrivals_people']==pytest.approx(row['departures_people']+row['final_queue_people'])
        assert abs(row['conservation_residual_people'])<1e-8
        assert row['separate_waiting_area_m2']==pytest.approx(row['maximum_queue_people']*.93)
    assert narrow['final_queue_people']>700 and not narrow['clears_each_headway']
    assert wide['final_queue_people']<1e-7 and wide['clears_each_headway']
    assert wide['maximum_queue_people']<narrow['maximum_queue_people']


def test_one_lift_outage_can_destroy_step_free_access_and_twin_lifts_can_queue():
    a=access.load();single=access.lift_queue(240,8.,1,1,360.,a)
    assert not single['assumed_step_free_route_available']
    assert single['unserved_or_after_horizon_parties']==single['total_parties']
    twin=access.lift_queue(480,8.,2,1,180.,a)
    assert twin['assumed_step_free_route_available'] and not twin['clears_before_repeated_service_horizon']
    assert twin['unserved_or_after_horizon_parties']>0
    assert not twin['independent_fire_evacuation_route']


def test_even_four_lifts_have_common_power_failure_without_qualified_backup():
    a=access.load();row=access.lift_queue(120,8.,4,0,360.,a,total_power_loss=True)
    assert row['lifts_available']==0 and not row['assumed_step_free_route_available']
    assert row['unserved_or_after_horizon_parties']==row['total_parties']


@pytest.mark.parametrize('key,value',[('rest_interval_m',51.),('clear_widths_m',[1.]),('selected_hub',True)])
def test_unapproved_or_inaccessible_policy_rejected(tmp_path,monkeypatch,key,value):
    import re
    text=access.INPUT.read_text();replacement=json.dumps(value)
    text=re.sub(r'^'+key+r'\s*=.*$',key+' = '+replacement,text,flags=re.M)
    path=tmp_path/'invalid.toml';path.write_text(text);monkeypatch.setattr(access,'INPUT',path)
    with pytest.raises(ValueError):access.load()


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    folder=tmp_path_factory.mktemp('hub-access-packet');access.publish(folder);return folder


def test_source_bound_baghdad_packet_contains_geometry_and_remains_unselected(packet):
    access.verify(packet);value=access.study();g=value['alternatives'][0]['geometry']
    assert value['focused_variant_id']=='pair-031-040/line-9/midpoint'
    assert value['physical_local_projection_length_m']==pytest.approx(941.8289573,abs=.1)
    assert value['additional_counted_platform_interface_length_m']==36.
    assert value['complete_access_horizontal_length_m']==pytest.approx(value['physical_local_projection_length_m']+36.)
    assert len(value['alternatives'])==3 and value['core_count']==3
    assert len(value['flow_scenarios'])==18 and len(value['lift_scenarios'])==36
    assert len(value['shared_site_circulation_alternatives'])==7
    assert g['bend_supports_counted'] and g['unique_support_positions']>39
    assert len(g['rest_bays'])==19
    assert all(not value[key] for key in access.FLAGS)
    assert value['decisions']['hub_merge_selected'] is False
    assert value['decisions']['default_city_modified'] is False
    assert value['decisions']['engineering_closure_complete'] is False
    assert all(not row['selected'] for row in value['alternatives'])
    assert all(not row['selected'] for row in value['shared_site_circulation_alternatives'])
    assert sum(u['length_m'] for u in g['units'])==pytest.approx(g['horizontal_length_m'])
    assert all(row['computed_internal_walks'] for row in value['shared_site_circulation_alternatives'])
    matrix=value['platform_transfer_walk_matrix'];outer=next(p for p in matrix['pairs'] if {p['from_line'],p['to_line']}=={'line-4','line-7'})
    assert matrix['platform_pair_count']==3
    assert outer['horizontal_walk_m']==pytest.approx(value['physical_local_projection_length_m']+24.,abs=1e-6)
    assert matrix['maximum_horizontal_walk_m']==pytest.approx(965.828926,abs=1e-5)
    assert matrix['minimum_horizontal_walk_m']==pytest.approx(494.91390758,abs=1e-6)
    assert outer['walk_minutes']['1.0']==pytest.approx(16.09714877,abs=1e-7)
    assert outer['walk_minutes']['0.6']==pytest.approx(26.82858128,abs=1e-7)
    assert outer['rest_bays_on_path']==19 and matrix['all_pairs_rest_spacing_screen_pass']
    assert all(p['maximum_distance_between_rest_or_endpoint_m']<=50.000001 for p in matrix['pairs'])
    text=(packet/'README.md').read_text();svg=(packet/'overview.svg').read_text()
    assert '16.10 minutes' in text and '26.83 minutes' in text and 'outer-to-outer walk' in text
    assert '16.10 min' in svg and '26.83 min' in svg and '495 to 966 m' in svg
    for row in value['alternatives']:
        assert row['guideway_clearance']['station_interface_spurs_excluded_from_mainline_screen']
        assert not row['guideway_clearance']['actual_vehicle_guideway_swept_envelope_qualified']
        assert all(unit['revision']==unit['qa_traveller']['unit_revision'] and unit['qa_traveller']['records']==[] for unit in row['geometry']['units'])


def test_cost_sensitivities_do_not_omit_supports_or_claim_complete_savings(packet):
    row=access.study()['alternatives'][0];g=row['geometry'];s=row['cost_sensitivities']['scenarios'][0]
    assert s['deck_canopy_target_usd']==pytest.approx(g['total_deck_area_m2']*300.)
    assert s['support_foundation_target_usd']==g['unique_support_positions']*10000.
    assert s['lift_target_usd']==3*75000.
    assert s['station_electrical_credit_usd']==3075000.
    assert s['complete_capex_usd'] is None and not s['savings_proved']
    assert not row['cost_sensitivities']['rates_are_quotes'] and row['cost_sensitivities']['excludes']


def test_all_assembly_acceptance_holds_are_unexecuted(packet):
    row=access.study()['alternatives'][0]
    assert row['schedule']['complete_programme_days'] is None
    assert all(not phase['executed'] and phase['hold_points'] for phase in row['schedule']['phases'])
    text=(packet/'README.md').read_text()
    assert 'not an observed Baghdad demand' in text and 'Iraqi accessibility' in text
    assert 'no qualified foundation or cost credit' in text


def test_rehashed_tampering_is_rejected_by_independent_recalculation(packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(packet,folder)
    value=json.loads(gzip.decompress((folder/'study.json.gz').read_bytes()))
    value['flow_scenarios'][0]['maximum_queue_people']=0.
    value.pop('content_sha256');value['content_sha256']=sha256(access.encoded(value)).hexdigest()
    raw=access.encoded(value);compressed=gzip.compress(raw,mtime=0);(folder/'study.json.gz').write_bytes(compressed)
    manifest=json.loads((folder/'manifest.json').read_text());manifest.update(content_sha256=value['content_sha256'],raw_bytes=len(raw),compressed_bytes=len(compressed))
    manifest['files_sha256']['study.json.gz']=access.digest(folder/'study.json.gz');(folder/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='recalculated content'):access.verify(folder)


def test_rehashed_geometry_tampering_is_rejected(packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(packet,folder);value=json.loads((folder/'geometry.json').read_text())
    value['alternatives'][0]['unique_support_positions']=1;(folder/'geometry.json').write_text(json.dumps(value))
    manifest=json.loads((folder/'manifest.json').read_text());manifest['files_sha256']['geometry.json']=access.digest(folder/'geometry.json')
    (folder/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='presentation differs'):access.verify(folder)


def test_extra_files_and_symlinks_are_rejected(packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(packet,folder);(folder/'unowned.txt').write_text('unowned')
    with pytest.raises(ValueError,match='inventory differs'):access.verify(folder)
    (folder/'unowned.txt').unlink();(folder/'assembly.svg').unlink();(folder/'assembly.svg').symlink_to(packet/'assembly.svg')
    with pytest.raises(ValueError,match='inventory differs'):access.verify(folder)
