"""Whole-module geometry, real apertures, shared packaging and adverse controls."""
from copy import deepcopy
import shutil
import subprocess
import pytest

from engineering.twin_workflow import core
from engineering.design_consistency import contracts as geometry
from engineering.assembly_design import baseline, carbody_assembly as body, contracts as configuration


@pytest.fixture(scope='module')
def policy():
    return core.read(baseline.DATA)


@pytest.fixture(scope='module')
def candidate(policy):
    return body.build(policy)


def test_same_controlled_six_car_length_and_explicit_unadopted_transverse_floor(candidate):
    prototype=configuration.prototype_configuration();m=candidate['metadata']
    assert m['dimensions_m']['length']==prototype['values']['car_length']['value']==18.5
    assert m['car_count']==6 and m['prototype_revision']==prototype['revision']
    assert m['dimensions_m']['width']==2.85 and m['dimensions_m']['height']==3.45
    assert m['dimensions_m']['floor_above_rail']==1.
    assert 'UNADOPTED' in m['transverse_basis'] and 'not an adopted' in m['floor_basis']
    assert prototype['door_layout']['state']==prototype['low_floor_layout']['state']=='hold'
    assert not m['complete_carbody_accepted']
    assert m['complete_installed_vehicle_mass_kg'] is None


def test_registered_stock_alternatives_preserve_function_and_bounded_parts(policy):
    variants=list(body.candidates(policy));assert len(variants)==6
    models=[body.build(policy,v) for v in variants]
    assert len({c['revision'] for c in models})==6
    assert all(c['metadata']['openings']==models[0]['metadata']['openings'] for c in models)
    assert len({len(c['contract']['parts']) for c in models})==1
    masses=[geometry.summary(c['contract'])['mass_kg'] for c in models]
    assert masses==sorted(masses) and len(set(masses))==6
    assert all(150<len(c['contract']['parts'])<225 for c in models)
    for c in models:
        assert c['metadata']['module_limit_m']['primary_rail_stock']<12.2
        assert c['metadata']['module_limit_m']['side_sheet_longitudinal']<2.
        # Eight serial stock halves are four continuous rails, not eight
        # parallel contributions to bending stiffness or installed lengths.
        longitudinal=[p for p in c['contract']['parts'] if p['id'].startswith('sill-') or p['id'].startswith('roof-rail-')]
        assert len(longitudinal)==8
        assert max(body.bounds(p)[1][0]-body.bounds(p)[0][0] for p in longitudinal)<12.2


def test_real_voids_sheet_area_and_infill_clearances(candidate):
    assert not body.opening_interferences(candidate)
    m=candidate['metadata'];d=m['dimensions_m'];floor=m['floor_thickness_m']
    full=(d['length']-.004)*((d['height']-.003)-(d['floor_above_rail']-floor-.24))
    openings=m['openings'];expected=2*full-sum(o['clear_width_m']*o['clear_height_m'] for o in openings)
    actual=sum(p['properties']['mass_kg']/2700/.002 for p in candidate['contract']['parts'] if m['part_groups'][p['id']]=='side-skin')
    assert actual==pytest.approx(expected,abs=1e-10)
    assert sum(o['type']=='door' for o in openings)==4
    assert sum(o['type']=='window' for o in openings)==6
    parts={p['id']:p for p in candidate['contract']['parts']}
    for opening in openings:
        if opening['type']=='window':
            glass=parts[opening['id'].replace('-window-','-window-glass-')]
            a,b=body.bounds(glass)
            assert a[0]>opening['x_bounds_m'][0] and b[0]<opening['x_bounds_m'][1]
            assert a[2]>opening['z_bounds_m'][0] and b[2]<opening['z_bounds_m'][1]
    assert not any('equipment-test-block' in p['id'] or 'mount-leg' in p['id'] for p in parts.values())


def test_jamb_shift_and_added_opaque_sheet_are_detected(candidate):
    changed=deepcopy(candidate);opening=changed['metadata']['openings'][0]
    first=next(p for p in changed['contract']['parts'] if changed['metadata']['part_groups'][p['id']]=='side-frame')
    first['placement']['translation_m']=[sum(opening['x_bounds_m'])/2,opening['side_sign']*1.383,2.]
    assert body.opening_interferences(changed)
    changed=deepcopy(candidate)
    target=next(p for p in changed['contract']['parts'] if changed['metadata']['part_groups'][p['id']]=='side-skin')
    target['manufacturing']['primitives']=[geometry.box('bad-fill',1.4,.002,2.,[-4.4,-1.424,2.])]
    assert body.opening_interferences(changed)


def test_each_physical_unit_in_one_dependency_stage_and_actual_joint_ids(candidate):
    stages=body.stage_plan(candidate);seen=set();parts=[]
    for stage in stages:
        assert set(stage['requires'])<=seen
        assert stage['supports'] and stage['loads']
        parts.extend(stage['parts']);seen.add(stage['id'])
    ids={p['id'] for p in candidate['contract']['parts']}
    assert len(parts)==len(set(parts)) and set(parts)==ids
    assert {p['unit_id'] for p in candidate['qa_plan']}==ids
    assert all(set(j['endpoints'])<=ids and j['capacity_evidence'] is None and not j['qualified'] for j in candidate['contract']['assembly_joints'])
    assert len([j for j in candidate['contract']['assembly_joints'] if 'butt-splice' in j['id']])==4
    sequence=candidate['metadata']['assembly_sequence']
    assert [s['id'] for s in sequence]==[s['id'] for s in stages]
    assert [s['part_ids'] for s in sequence]==[s['parts'] for s in stages]


def test_reference_profile_mass_and_independent_beam_controls(candidate):
    result=body.beam_diagnostic(candidate);adverse=body.beam_diagnostic(candidate,load_scale=2.)
    prototype=configuration.prototype_configuration();a=result['assumptions'];count=prototype['values']['car_count']['value']
    assert a['planning_tare_reference_kg']==prototype['values']['tare_mass']['value']/count
    assert result['mass_kg']==pytest.approx(a['planning_tare_reference_kg']+a['planning_crush_passengers']*75.)
    assert not a['actual_vehicle_tare_reconciled']
    assert result['closed_form_relative_error']<1e-7
    assert result['solutions'][-1]['force_balance_relative_error']<1e-8
    assert sum(result['independent_support_reactions_n'])==pytest.approx(result['mass_kg']*9.80665)
    assert adverse['maximum_nodal_deflection_m']==pytest.approx(2*result['maximum_nodal_deflection_m'])
    assert adverse['maximum_sill_fibre_stress_pa']==pytest.approx(2*result['maximum_sill_fibre_stress_pa'])
    assert result['adopted_deflection_limit_m'] is None and result['adopted_stress_allowable_pa'] is None
    sections={p['placement']['translation_m'][1]:p['analysis']['section'] for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['primary_sill_ids']}
    assert len(sections)==2
    ei=sum(section['iy_m4'] for section in sections.values())*candidate['contract']['materials']['steel']['young_pa']
    assert result['ei_nm2']==pytest.approx(ei)
    assert body.beam_diagnostic(candidate,mass_basis='represented-shell')['mass_kg']==pytest.approx(geometry.summary(candidate['contract'])['mass_kg'])


def test_door_circulation_conflicts_are_retained_without_fake_supplier_fit(candidate):
    packaging=body.equipment_conflicts(candidate)
    assert packaging['cassette_count']==8 and packaging['cooling_boundary_count']==3
    assert len(packaging['issues'])==4
    assert {i['instance_id'] for i in packaging['issues']}=={'cooling-module-01','cooling-module-03'}
    assert packaging['complete_solid_interference_checked'] is False
    assert packaging['geometry_and_maintenance_envelope']=='hold'
    layout=body.installed_equipment.layout()
    equipment=dict(architecture='baghdad-six-car',layout_sha256=core.sha(body.installed_equipment.DATA),
        instances=[dict(id=f'cassette-{i}',body_id='car-1',local_position_m=p) for i,p in enumerate(layout['cassette_local_positions_m'])],
        purchased_boundaries=[dict(id=f'cooling-{i}',body_id='car-1',local_position_m=p) for i,p in enumerate(layout['cooling_module_local_positions_m'])])
    equipment['revision']=core.digest(equipment)
    result=body.equipment_conflicts(candidate,equipment)
    assert result['provided_exact_equipment_revision']==equipment['revision']
    assert result['cassette_count']==8 and result['cooling_boundary_count']==3
    equipment['instances'][0]['local_position_m']=[0,0,0]
    with pytest.raises(ValueError,match='stale equipment'):body.equipment_conflicts(candidate,equipment)


def test_implemented_geometry_controls_do_not_promote_whole_vehicle_acceptance(policy,candidate):
    result=body.evaluate(policy,candidate)
    assert result['checks']['owned_shell_within_provisional_outer_envelope']
    assert 'frame/provisional_nominal_S355_elastic_guardrail' in result['failed_checks']
    assert not result['implemented_checks_pass']
    assert result['held_checks'] and result['state']=='failed' and not result['screen_pass']
    assert result['supplemental_evidence']['carbody-frame']['candidate_revision']==candidate['revision']
    assert result['measurements']['mass_kg']==pytest.approx(geometry.summary(candidate['contract'])['mass_kg'])
    assert result['measurements']['represented_six_car_gross_mass_kg']==pytest.approx(6*result['measurements']['mass_kg'])
    assert result['measurements']['complete_installed_vehicle_mass_kg'] is None
    assert not result['digital_specification_complete'] and not result['connection_resistance_qualified']
    assert all(result[k] is False for k in core.FLAGS)


def test_stale_or_unknown_geometry_and_invalid_mass_cases_rejected(policy,candidate):
    altered=deepcopy(candidate);altered['metadata']['dimensions_m']['floor_above_rail']=.35
    with pytest.raises(ValueError,match='controlled generator'):body.evaluate(policy,altered)
    altered=deepcopy(candidate);altered['contract']['parts'][0]['properties']['mass_kg']+=1
    with pytest.raises(ValueError,match='controlled generator'):body.evaluate(policy,altered)
    for variables in ({'frame_wall_m':.002,'floor_m':.006},{'frame_wall_m':float('nan'),'floor_m':.006},{'frame_wall_m':.004,'floor_m':.006,'extra':1}):
        with pytest.raises(ValueError):body.build(policy,variables)
    bad=deepcopy(policy);bad['architecture']='legacy-lm3'
    with pytest.raises(ValueError):body.build(bad)
    bad=deepcopy(policy);next(f for f in bad['facts'] if f['id']=='train.car_length')['value']=16.5
    with pytest.raises(ValueError,match='length differ'):body.build(bad)
    for kwargs in ({'load_scale':0},{'passenger_mass_kg':float('inf')},{'planning_crush_passengers':-1},{'mass_basis':'hidden-total'}):
        with pytest.raises(ValueError):body.beam_diagnostic(candidate,**kwargs)


def test_disconnected_cutting_remnants_are_separate_manufacturing_units():
    cells=body._subtract([(0.,3.,0.,3.)],(1.,2.,0.,3.))
    assert len(body._connected(cells))==2
    assert sum((b-a)*(d-c) for a,b,c,d in cells)==pytest.approx(6.)
    assert len(body._connected([(0,1,0,1),(1,2,1,2)]))==2  # Point contact is not a sheet bridge.


def test_native_whole_shell_mass_identity_contact_and_step_reopen(tmp_path,candidate):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:
            pytest.skip('native FreeCAD unavailable')
    from engineering.continuous_design import study_confirmation
    definition=tmp_path/'definition.json';core.write(definition,candidate['contract'])
    proof,state,error=study_confirmation.native(definition,tmp_path/'native')
    assert state=='passed',error
    assert proof['physical_ids_preserved'] and proof['manufacturing_unit_ids_preserved']
    assert proof['native_reopened'] and proof['step_volume_reconciled']
    assert len(proof['checks'])==len(candidate['contract']['parts'])
    assert max(row['mass_relative_error'] for row in proof['checks'])<1e-7
