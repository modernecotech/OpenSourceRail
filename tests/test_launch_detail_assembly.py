"""Dimensional and identity controls for a real research mechanism assembly."""
from copy import deepcopy
from math import pi
import pytest
from engineering.design_search.craft_backends import launch_assembly as a
from engineering.design_search.craft_backends.cases import identity


def test_actual_hollow_frame_and_bores_are_not_solid_envelopes():
    v=a.build();assert len(v['entities'])==122
    rhs=next(p for p in v['entities'] if p['id']=='frame/longitudinal/0')
    expected=(1.2*.06*.10-1.2*.048*.088)-2*pi*(.018/2)**2*.012
    assert a.measures(rhs)['volume_m3']==pytest.approx(expected)
    assert a.measures(rhs)['volume_m3']<.4*(1.2*.06*.10)
    assert len(rhs['holes'])==2


def test_clevis_geometry_and_fem_contract_share_exact_candidate_identity():
    v=a.build();f=v['fem_interface'];d=v['dimensions']
    assert f['candidate_id']==v['candidate_id'] and f['component_geometry_id']==v['component_geometry_id']
    assert d['ear_length_m']==.22 and d['ear_thickness_m']==.025 and d['ear_height_m']==.16
    assert d['bore_diameter_m']==.06 and d['bore_center_local_xz_m']==[.14,.08]
    assert f['force_per_ear_N']*2==f['total_force_N']==160000
    assert v['requirements']['available_thrust_N'] is None
    assert v['requirements']['powered_length_m'] is None and v['requirements']['launch_speed_m_s'] is None
    assert v['component_geometry_id']!=v['candidate_id']


def test_deck_fasteners_and_crush_sleeves_are_located_on_actual_rhs_centres():
    v=a.build();parts={p['id']:p for p in v['entities']}
    for i,x in enumerate((-.16,.26)):
        for j,y in enumerate((-.28,.28)):
            sleeve=parts[f'fasteners/deck-crush-sleeve/{i}/{j}']
            stud=parts[f'fasteners/deck-stud/{i}/{j}']
            assert sleeve['at_m']==[x,y,.126] and sleeve['length_m']==.088
            assert sleeve['at_m'][:2]==stud['at_m'][:2]
            assert sleeve['inner_radius_m']>stud['radius_m']
    assert v['joints']['deck_studs']==4 and v['joints']['deck_crush_sleeves']==4


def test_pin_has_real_end_bores_end_caps_screws_and_bushes():
    v=a.build();parts={p['id']:p for p in v['entities']}
    pin=parts['clevis/pin'];assert len(pin['blind_bores'])==2
    assert a.measures(pin)['volume_m3']==pytest.approx(pi*.03**2*.2-2*pi*.006**2*.024)
    assert len([p for p in parts if p.startswith('clevis/pin-end-cap/')])==2
    assert len([p for p in parts if p.startswith('clevis/retaining-screw-shank/')])==2
    assert len([p for p in parts if p.endswith('/bush')])==8
    assert v['joints']['running_wheels']==4 and v['joints']['capture_wheels']==4


def test_mass_account_is_nonzero_bounded_and_never_installed_acceptance():
    v=a.build();assert 185<v['nominal_located_material_mass_kg']<195
    assert v['installed_mass_bound_kg'][0]<v['nominal_located_material_mass_kg']<v['installed_mass_bound_kg'][1]
    assert all(r['low_kg']>0 and r['high_kg']>=r['low_kg'] for r in v['unresolved_mass_accounts'])
    assert all(v[k] is False for k in a.FLAGS)
    assert len(v['manufacturing']['bom'])==len(v['entities'])
    assert v['manufacturing']['costs']['estimated_factory_cost'] is None


def test_swept_envelope_contains_all_nominal_parts_at_both_travel_limits():
    v=a.build();s=v['access']['travel'];lower,upper=s['swept_bounds_m']
    for p in v['entities']:
        lo,hi=a.measures(p)['bounds_m']
        for travel in s['range_m']:
            assert all(lower[i]-1e-12<=lo[i]+(travel if i==0 else 0) and
                       hi[i]+(travel if i==0 else 0)<=upper[i]+1e-12 for i in range(3)),p['id']
    assert v['access']['retention']['pitch_reaction_delta_N']==51200
    assert v['access']['lifting']['rated_capacity_kg'] is None


@pytest.mark.parametrize('change',['geometry','material','force','zero-mass','release'])
def test_resealed_but_modified_definition_is_refused(change):
    v=a.build()
    if change=='geometry':v['entities'][0]['size_m'][0]+=.1
    if change=='material':v['materials'][a.STEEL]['density_kg_m3']=1
    if change=='force':v['fem_interface']['force_per_ear_N']=1
    if change=='zero-mass':v['unresolved_mass_accounts'][0]['low_kg']=0
    if change=='release':v['physical_accepted']=True
    v['assembly_definition_id']=identity({k:x for k,x in v.items() if k!='assembly_definition_id'})
    with pytest.raises(ValueError):a.validate(v)


def test_cad_records_real_hollow_cuts_bores_and_stable_si_conversion():
    v=a.build();script=a.cad_script(v);commands=script['commands']
    cuts=[c for c in commands if c['command']=='solid.box' and c['params'].get('operation')=='cut']
    assert len(cuts)==5
    assert all(c['params']['targets'][0].startswith('frame/') for c in cuts)
    pin_bores=[c for c in commands if c['command']=='solid.cylinder' and c['params'].get('targets')==['clevis/pin']]
    assert len(pin_bores)==2 and all(c['params']['radius']==6 for c in pin_bores)
    assert a.build()==v and script==a.cad_script(deepcopy(v))


def test_pin_bending_rejects_old_40mm_hypothesis_and_r3_keeps_retention_open():
    v=a.build();s=v['necessary_screens']
    assert s['necessary_pin_screen_passed'] and max(c['proof_combined_Pa'] for c in s['pin_cases'])<355e6
    assert max(c['combined_nominal_von_mises_Pa'] for c in s['pin_cases'])==pytest.approx(167656305.38400763)
    old=deepcopy(v);old['dimensions']['pin_diameter_m']=.040
    assert not a.pin_ear_screens(old)['necessary_pin_screen_passed']
    assert s['ear_two_plane_tearout_shear_Pa']==pytest.approx(32e6)
    assert s['retaining_screw']['cap_plate_bending_qualified'] is False
    assert s['retaining_screw']['thread_engagement_qualified'] is False
    assert v['revision_history'][0]['parent_candidate_id']=='60d6ea6ca295803262e7bd6da93e8a14e5ebc802c69467b89a08f03d8e2d0eb8'


def test_returned_material_mutation_cannot_change_canonical_generator():
    original=a.build();mass=original['nominal_located_material_mass_kg']
    original['materials'][a.STEEL]['density_kg_m3']=1.
    original['physical_definition']['materials'][a.BRONZE]['density_kg_m3']=1.
    assert a.build()['nominal_located_material_mass_kg']==mass
    assert a.build()['materials'][a.STEEL]['density_kg_m3']==7850.


def test_cad_regions_are_not_duplicate_purchased_retaining_screws():
    v=a.build();m=v['manufacturing']
    assert m['nominal_material_region_count']==122 and m['nominal_component_count']==120
    screws=[r for r in m['component_bom'] if r['component_id'].startswith('clevis/retaining-screw/')]
    assert len(screws)==2 and all(len(r['material_region_ids'])==2 and r['quantity']==1 for r in screws)
