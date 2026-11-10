"""Installed-layout arithmetic and evidence boundaries, independent of GUI CAD."""
from copy import deepcopy
from math import isclose,fsum,prod
import json,struct
import pytest
from engineering.vehicle_installation import model,export,FLAGS
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def result():return model.build()


def test_pinned_source_and_new_ancestry(result):
    assert result['source_component_types']==605
    assert result['candidate_id']!=result['parent_candidate_id']
    assert result['candidate_id']==identity(result['physical_definition'])
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})
    assert all(result[k] is False for k in FLAGS)


def test_inner_face_gauge_contact_datum_and_wheel_axle_orientation(result):
    t=result['physical_definition']['track_interface']
    assert t['inner_face_gauge_m']==pytest.approx(1.435)
    centres=t['nominal_contact_centres_y_m'];w=t['nominal_rail_head_width_m']
    assert centres[1]-w/2-(centres[0]+w/2)==pytest.approx(1.435)
    assert t['real_profile_verified'] is False
    for p in result['patterns']:
        if p['part_id']=='running/wheel':
            assert p['rotation']==model.I
            assert [q[1] for q in p['positions_m']]==centres
            assert model.transformed_size(p['geometry']['size_m'],p['rotation'])==[.76,.135,.76]
        elif p['part_id']=='running/axle':assert p['rotation']==model.RZ90
    axleboxes=result['assembly_occurrences']['running/axlebox']
    assert set(a['at_m'][1] for a in axleboxes)=={-.98,.98}
    bad=deepcopy(result['policy']);bad['track_interface']['nominal_contact_centres_y_m']=[-.6,.6]
    with pytest.raises(ValueError,match='gauge'):model.track_interface(bad)


def test_exact_source_origins_counted_once(result):
    original=model.load()['parts'];new=result['parts'];patterns=result['patterns']
    assert len([p for p in new if p['source_part_id']])==605
    assert {p['source_part_id'] for p in new if p['source_part_id']}=={p['id'] for p in original}
    for p in new:
        assert sum(x['count'] for x in patterns if x['part_id']==p['id'])==p['quantity_per_train']
    assert result['total_occurrences']==sum(r['count'] for r in patterns)
    assert len(result['assembly_plans']['plans'])==40


def test_no_parent_subtotal_or_old_cassette_double_count(result):
    for c in model.CASES:
        expected=result['source_part_mass_kg'][c]+fsum(r['new_mass_per_train_kg'][c]-r['old_mass_per_train_kg'][c] for r in result['revisions'])
        expected+=fsum(p['quantity_per_train']*p['mass_each_kg'][c] for p in result['parts'] if p['source_part_id'] is None)
        assert isclose(expected,result['nominal_part_mass_kg'][c],abs_tol=1e-7)
    assert not any(p['id']=='services/battery-side-panel' for p in result['parts'])
    assert len([p for p in result['parts'] if p['source_part_id'] is None])==4
    assert {p['material_id'] for p in result['parts']} <= {m['id'] for m in result['materials']}
    assert 'overhead included once' in next(p for p in result['parts'] if p['id']=='installation/services/battery-lid-panel')['cost_basis']


def test_static_reactions_conserve_force_and_first_moment(result):
    for r in result['mass_scenarios']:
        assert len(r['axles'])==24
        assert r['axles'][0]['x_m']==pytest.approx(1.05)
        assert r['axles'][-1]['x_m']==pytest.approx(104.20)
        assert fsum(a['vertical_force_N'] for a in r['axles'])==pytest.approx(r['train_mass_kg']*9.80665,abs=1e-7)
        assert fsum(a['vertical_force_N']*a['x_m'] for a in r['axles'])==pytest.approx(r['train_mass_kg']*9.80665*r['CG_m'][0],abs=1e-6)
        assert min(a['vertical_force_N'] for a in r['axles'])>0
        assert abs(r['force_residual_N'])<1e-6 and abs(r['moment_residual_Nm'])<1e-6
        assert fsum(c['mass_kg'] for c in r['cars'])==pytest.approx(r['train_mass_kg'])


def test_reserve_and_passengers_are_disjoint_positive_cases(result):
    by={r['name']:r for r in result['mass_scenarios']}
    for c,reserve in zip(model.CASES,(2000,5000,10000)):
        assert by['tare-'+c]['train_mass_kg']-result['nominal_part_mass_kg'][c]==pytest.approx(reserve)
        assert by['normal-'+c]['train_mass_kg']-by['tare-'+c]['train_mass_kg']==pytest.approx(276*75)
        assert by['crowd-control-'+c]['train_mass_kg']-by['tare-'+c]['train_mass_kg']==pytest.approx(960*75)
    for kind in ('tare','normal','crowd-control'):
        bound=result['mass_uncertainty'][kind]
        for c in model.CASES:
            r=by[kind+'-'+c]
            for a in range(3):assert bound['CG_outer_box_m'][a][0]<=r['CG_m'][a]<=bound['CG_outer_box_m'][a][1]


def test_proper_explicit_rotations_and_symmetric_inertia(result):
    for p in result['patterns']:
        R=p['rotation']
        for a in range(3):
            for b in range(3):assert sum(R[a][j]*R[b][j] for j in range(3))==pytest.approx(1 if a==b else 0)
        assert len(p['positions_m'])==p['count']
    for r in result['mass_scenarios']:
        J=r['inertia_about_CG_kg_m2']
        for a in range(3):
            assert J[a][a]>0
            for b in range(3):assert J[a][b]==pytest.approx(J[b][a])


def test_battery_replacement_packaging_and_retention(result):
    p={p['id']:p for p in result['parts']}
    assert p['services/battery-module']['quantity_per_train']==450
    assert p['installation/services/battery-rack-support']['quantity_per_train']==360
    assert p['installation/services/battery-enclosure-fixing-bolt']['quantity_per_train']==1080
    assert p['installation/battery-flexible-link']['quantity_per_train']==72
    assert sum(x['quantity_per_train'] for x in p.values() if 'thermal-barrier-' in x['id'])==540
    checks=result['interface_screens'];assert len(checks['battery_pod_checks'])==15
    for check in checks['battery_pod_checks']:
        assert check['bogie_zone_longitudinal_margin_m']>0
        assert check['sill_vertical_margin_m']>0
        assert check['central_corridor_margin_m']>=-1e-12
        assert check['removable_after_isolation_and_outer_pods']
        assert check['complete_lateral_exit_margin_m']>0
        assert check['tool_access_verified'] is False
    assert any(check['removal_before_inner_pods'] for check in checks['battery_pod_checks'])
    for key in ('internal_length_margin_m','internal_width_margin_m','remaining_height_after_terminal_allowance_m'):assert checks['module_packaging'][key]>0


def test_seating_and_door_sweeps_are_proposals(result):
    i=result['interface_screens'];assert (i['fixed_seats_per_car'],i['wheelchair_places_per_car'],i['doors_per_car'],i['door_sides'])==(44,2,2,1)
    assert i['aisle_target_passed'] and i['access_and_swept_envelopes_verified'] is False
    doors=result['assembly_plans']['door_motion'];assert len(doors)==24
    assert all(d['header_end_margin_m']>0 for d in doors)
    slide=model.policy()['layout']['door_slide_m']
    for door in doors:
        closed=door['closed_center_m'];opened=door['open_center_m'];travel=door['travel_m'];axis=door['axis']
        side=1 if door['id'].endswith('/leaf-1') else -1
        assert door['motion_vector_frame']=='vehicle-global-xyz'
        assert len(travel)==len(axis)==3
        assert opened==pytest.approx([closed[j]+travel[j] for j in range(3)])
        assert travel==pytest.approx([side*slide,0.,0.])
        assert travel[1]==pytest.approx(0.) and travel[2]==pytest.approx(0.)
        bounds=door['swept_zone_m']
        leaf_half_width=.38
        assert bounds[0][0]==pytest.approx(min(closed[0],opened[0])-leaf_half_width)
        assert bounds[1][0]==pytest.approx(max(closed[0],opened[0])+leaf_half_width)
    assert all(d['entrapment_and_emergency_release_verified'] is False for d in doors)
    assert 'retained once' in i['passive_aluminium_secondary']


def test_prices_are_evaluation_inputs_without_geometry_change():
    b=model.load();p=model.policy();changed=deepcopy(p);changed['rates']['aluminium_usd_kg'][1]*=2
    a,_=model.proposed_parts(b,p);d,_=model.proposed_parts(b,changed)
    assert [r['component_definition_id'] for r in a]==[r['component_definition_id'] for r in d]
    assert next(r for r in a if r['id']=='installation/services/battery-lid-panel')['direct_cost_each_usd']!=next(r for r in d if r['id']=='installation/services/battery-lid-panel')['direct_cost_each_usd']


def test_control_does_not_claim_thin_underfloor_clearances():
    p=model.policy();i=model.interfaces(p,'above-floor-control')
    assert not i['battery_pod_checks'] and 'not fully packed' in i['battery_control_scope']


def test_common_civil_packet_is_sealed_and_rejects_mutation(result):
    packet=model.axle_loads(result,system_candidate_id='f'*64)
    assert packet['candidate_id']=='f'*64 and packet['vehicle_candidate_id']==result['candidate_id']
    assert packet['evaluation_id']==identity({k:v for k,v in packet.items() if k!='evaluation_id'})
    corrupt=dict(result,evaluation_id='0'*64)
    with pytest.raises(ValueError,match='Sealed'):model.axle_loads(corrupt)


def test_instanced_preview_has_all_occurrences_without_mass_claim(tmp_path,result):
    meta=export.preview_glb(result,tmp_path/'assembly.glb');raw=(tmp_path/'assembly.glb').read_bytes()
    magic,version,length=struct.unpack('<4sII',raw[:12]);assert (magic,version,length)==(b'glTF',2,len(raw))
    n,kind=struct.unpack('<I4s',raw[12:20]);doc=json.loads(raw[20:20+n]);assert kind==b'JSON'
    assert sum(node.get('extras',{}).get('occurrence_count',0) for node in doc['nodes'])==result['total_occurrences']
    assert meta['instance_count']==result['total_occurrences'] and meta['installed_mass_complete'] is False
    assert len(doc['meshes'])==609


def test_representative_cad_disjoint_wall_volumes(result):
    case=export.representative_case(result)
    assert 1<len(case['entities'])<5000 and case['candidate_id']==result['candidate_id']
    expected=fsum(prod(e['size_m']) for e in case['entities'])
    frame=[p for p in result['patterns'] if p['assembly_id']=='running/bogie-frame' and p['bogie_index']==0 and p['geometry']['exact_stock']]
    volume=0
    for p in frame:
        s=p['geometry']['source_stock'];L,b,h=p['geometry']['size_m']
        volume+=p['count']*(L*(b*h-(b-2*s['wall_m'])*(h-2*s['wall_m'])) if s['kind']=='rhs' else L*b*h)
    assert expected==pytest.approx(volume)
    assert case['physical_accepted'] is False



def test_declared_source_context_is_generic_contained_and_verified(tmp_path):
    from engineering.station_rail.common import digest
    (tmp_path/'owned.py').write_text('value=1\n');declared={'owned.py':digest(tmp_path/'owned.py')}
    (tmp_path/'unrelated.py').write_text('value=2\n')
    assert export.validate_declared_sources(declared,tmp_path)==declared
    with pytest.raises(ValueError,match='SHA differs'):export.validate_declared_sources({'owned.py':'0'*64},tmp_path)
    with pytest.raises(ValueError,match='root-relative'):export.validate_declared_sources({'../escape.py':'0'*64},tmp_path)
    (tmp_path/'alias.py').symlink_to(tmp_path/'owned.py')
    with pytest.raises(ValueError,match='ordinary'):export.validate_declared_sources({'alias.py':declared['owned.py']},tmp_path)
