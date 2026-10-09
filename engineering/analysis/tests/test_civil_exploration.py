"""Independent quantities, load conservation, native verification and tampering."""
from copy import deepcopy
import numpy as np
import pytest

from osr_mech.civil import decked_pi
from osr_mech.civil.exploration import deck_section, deck_cad, geometry, section_properties
from engineering.civil_exploration.contracts import HERE, encoded, load, validate_study
from engineering.civil_exploration.model import System, axle_nodal_loads, distributed_axle_loads, takeoff
from engineering.civil_exploration import workflow


def study():
    return load(HERE/'config/reference.json')


def control():
    s = study()
    return s, workflow.candidate(s['candidates'][1], s)


def test_pi_quantities_match_existing_manufacturing_reference():
    s, c = control()
    geo = geometry(c['definition'])
    bare = deck_section('pi')
    assert bare['area_m2'] == pytest.approx(decked_pi.section_area_m2())
    existing = decked_pi.manufacturing_specification(25.)
    q = takeoff(c, s)
    assert q['fabricated_beam_mass_kg'] == pytest.approx(existing['manufactured_study_mass_kg'])
    assert q['deck_concrete_m3'] == pytest.approx(existing['concrete_m3']*8)
    assert deck_cad(c['definition']).volume/1e9 == pytest.approx(existing['concrete_m3'])
    assert geo['deck'][0]['area_m2'] > geo['deck'][1]['area_m2']
    assert q['suspended_mass_kg'] > 75000
    assert q['installed_cost_usd'] is None and q['whole_life_cost_usd'] is None


def test_hollow_section_matches_outer_minus_void_independently():
    section = deck_section('hollow-box', top_m=.15, bottom_m=.15, wall_m=.15)
    width, depth, clear_width, clear_depth = 2.9, 1.155, 2.6, .855
    assert section['area_m2'] == pytest.approx(width*depth-clear_width*clear_depth)
    assert section['centroid_z_m'] == pytest.approx(depth/2)
    assert section['inertia_y_m4'] == pytest.approx((width*depth**3-clear_width*clear_depth**3)/12)
    assert section['inertia_z_m4'] == pytest.approx((depth*width**3-clear_depth*clear_width**3)/12)
    with pytest.raises(ValueError, match='overlapping'):
        section_properties(section['regions']+[section['regions'][0]])


def test_hollow_pier_changes_complete_package_and_preserves_deck():
    s, ref = control()
    alternative = workflow.candidate(s['candidates'][3], s)
    baseline, changed = takeoff(ref, s), takeoff(alternative, s)
    assert changed['pier_concrete_m3'] < baseline['pier_concrete_m3']
    for key in ('deck_concrete_m3', 'foundation_concrete_m3', 'bearing_count', 'suspended_mass_kg'):
        assert baseline[key] == changed[key]
    assert changed['installed_study_mass_kg'] < baseline['installed_study_mass_kg']


@pytest.mark.parametrize('front', [-1., 0., 3.14, 10., 12., 20.])
def test_axle_interpolation_conserves_force_and_moment(front):
    x = np.linspace(0, 10, 11)
    offsets, forces = [0., 2., 5.], [100., 200., 300.]
    values = axle_nodal_loads(x, front, offsets, forces)
    present = [(front-offset, force) for offset, force in zip(offsets, forces) if 0 <= front-offset <= 10]
    assert sum(values) == pytest.approx(sum(f for _, f in present))
    assert np.dot(values, x) == pytest.approx(sum(p*f for p, f in present))


def test_rail_footprint_conserves_force_moment_and_enters_smoothly():
    x = np.linspace(0., 10., 21)
    values = distributed_axle_loads(x, 5.14, [0.], [100.], 2.)
    assert sum(values) == pytest.approx(100.)
    assert np.dot(values, x) == pytest.approx(514.)
    assert sum(distributed_axle_loads(x, -1., [0.], [100.], 2.)) == 0
    assert sum(distributed_axle_loads(x, 0., [0.], [100.], 2.)) == pytest.approx(50.)
    assert 0 < sum(distributed_axle_loads(x, -.999, [0.], [100.], 2.)) < .001


def test_native_recorders_match_end_state_and_keep_units(tmp_path):
    pytest.importorskip('openseespy.opensees')
    s, c = control()
    model = System(c, s, s['ground_scenarios'][0], 8)
    result = model.transient(40, .02, tmp_path/'history.csv')
    import csv
    with (tmp_path/'history.csv').open() as stream:
        last = list(csv.DictReader(stream))[-1]
    actual = model.responses()
    for key in ('deck_displacement_m', 'bending_moment_nm', 'foundation_settlement_m'):
        assert float(last[key]) == pytest.approx(actual[key])
    assert result['native_recorders']['units']['moment'] == 'N*m'
    assert all((tmp_path/name).is_file() for name in result['native_recorders']['files'].values())
    graph = result['assembly']
    connected = {n for e in graph['elements'] for n in e['nodes']}
    connected |= {n for link in graph['rigid_links'] for n in (link['from_node'], link['to_node'])}
    assert connected == {int(n) for n in graph['coordinates_m']}
    assert len([e for e in graph['elements'] if e['type'] == 'foundation-spring']) == 5


@pytest.mark.parametrize('mutate', [
    lambda s: s.update(unregistered=1),
    lambda s: s['material'].update(youngs_modulus_pa=float('nan')),
    lambda s: s['material'].update(youngs_modulus_pa=True),
    lambda s: s['material'].update(youngs_modulus_mpa=30000),
    lambda s: s['foundation'].update(site_verified=True),
    lambda s: s['analysis'].update(meshes=[8, 8, 16]),
    lambda s: s['train'].update(axle_offsets_m=[0, 0]),
    lambda s: s['train'].update(supplier_verified=True),
    lambda s: s.update(route_length_m=101),
    lambda s: s['candidates'][0]['deck']['parameters'].update(top_m=.2),
])
def test_invalid_inputs_cannot_be_silently_ignored(mutate):
    s = study(); mutate(s)
    with pytest.raises(ValueError):
        validate_study(s)


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path/'bad.json'; path.write_text('{"mass": 1, "mass": 2}')
    with pytest.raises(ValueError, match='duplicate JSON'):
        load(path)


def test_identity_lineage_and_material_cache_invalidation(tmp_path):
    s, c = control()
    original_id = c['id']
    assert workflow.candidate(s['candidates'][1], s)['id'] == original_id
    changed = deepcopy(s); changed['material']['youngs_modulus_pa'] *= .9
    assert workflow.candidate(changed['candidates'][1], changed)['id'] != original_id
    parent = tmp_path/'parent.json'; parent.write_bytes(encoded(c))
    definition = tmp_path/'definition.json'
    definition.write_bytes(encoded({k: s['candidates'][2][k] for k in ('deck', 'pier')}))
    child = workflow.derive(parent, definition, tmp_path/'child.json')
    assert child['parents'] == [original_id] and child['id'] != original_id
    assert parent.read_bytes() == encoded(c)
    workflow.validate_candidate(child)
    child['definition']['deck']['span_m'] = 20
    with pytest.raises(ValueError, match='identity'):
        workflow.validate_candidate(child)


def test_modified_candidate_lineage_survives_new_campaign(tmp_path):
    pytest.importorskip('openseespy.opensees')
    s, parent = control()
    s['lineage_records'] = [parent]
    s['candidates'][2]['parents'] = [parent['id']]
    s['candidates'][2]['modification_reason'] = 'Investigate hollow deck material efficiency'
    profile = tmp_path/'profile.json'; profile.write_bytes(encoded(s))
    manifest = workflow.prepare(profile, tmp_path/'campaign')
    item = next(c for c in manifest['cases'] if c['name'] == 'hollow-deck25')
    child = load(tmp_path/'campaign/candidates'/f'{item["candidate_id"]}.json')
    assert child['parents'] == [parent['id']]
    assert child['modification_reason'] == s['candidates'][2]['modification_reason']
    assert load(tmp_path/'campaign/lineage'/f'{parent["id"]}.json') == parent
    workflow.verify(tmp_path/'campaign')
    s['lineage_records'] = []
    profile.write_bytes(encoded(s))
    with pytest.raises(ValueError, match='parent record missing'):
        workflow.prepare(profile, tmp_path/'missing-parent')


def test_derive_rejects_ignored_material_override(tmp_path):
    s, c = control()
    parent = tmp_path/'parent.json'; parent.write_bytes(encoded(c))
    definition = {k: s['candidates'][2][k] for k in ('deck', 'pier')}
    definition['ignored_material'] = 'UHPC'
    path = tmp_path/'definition.json'; path.write_bytes(encoded(definition))
    with pytest.raises(ValueError, match='unknown fields'):
        workflow.derive(parent, path, tmp_path/'child.json')


def test_native_benchmarks_verify_independent_analytical_responses():
    pytest.importorskip('openseespy.opensees')
    from engineering.analysis.benchmarks.civil.exploration import run
    result = run()
    assert result['passed'] and not result['physical_validation']
    fine = next(c for c in result['checks'] if c['name'].startswith('moving-force mesh 64'))
    assert fine['normalised_history_error'] < .01


def test_softer_foundation_increases_settlement_and_braking_drift():
    pytest.importorskip('openseespy.opensees')
    s, c = control()
    firm = System(c, s, s['ground_scenarios'][0], 8).braking()
    soft = System(c, s, s['ground_scenarios'][1], 8).braking()
    assert soft['foundation_settlement_m'] > firm['foundation_settlement_m']
    assert soft['pier_top_horizontal_m'] > firm['pier_top_horizontal_m']


def test_sealed_inputs_ledger_and_native_failures(tmp_path):
    pytest.importorskip('openseespy.opensees')
    output = tmp_path/'campaign'
    manifest = workflow.prepare(HERE/'config/reference.json', output)
    workflow.verify(output)
    c = load(output/'candidates'/f'{manifest["cases"][0]["candidate_id"]}.json')
    bad = study(); bad['train']['axle_loads_kn'][0] = float('inf')
    # Failure is generated by a real isolated worker and retained, never
    # interpreted as a successful native or engineering result.
    bad['train']['axle_loads_kn'][0] = -1
    job = dict(candidate=c, study=bad, ground=bad['ground_scenarios'][0],
               dependencies=manifest['dependency_hashes'], environment=manifest['environment'], timeout_s=10)
    entry = workflow.execute(output, job)
    manifest['evaluations'].append(entry); workflow.write(output/'manifest.json', manifest)
    rows = workflow.compare(output)
    assert rows[0]['execution'] == 'failed' and rows[0]['engineering_feasibility'] == 'unresolved'
    workflow.verify(output)
    record = load(output/entry['path'])
    stderr = (output/entry['path']).parent/'stderr.log'; stderr.write_text('fabricated pass')
    with pytest.raises(ValueError, match='artifact hash'):
        workflow.verify(output)
    stderr.write_text('')
    # The append-only lineage ledger is also sealed by the campaign manifest.
    (output/'ledger.jsonl').write_text('{}\n')
    with pytest.raises(ValueError, match='ledger hash'):
        workflow.verify(output)


def test_campaign_budget_rejected_before_writing_outputs(tmp_path):
    pytest.importorskip('openseespy.opensees')
    s = study(); s['analysis']['max_evaluations'] = 1
    config = tmp_path/'small.json'; config.write_bytes(encoded(s))
    with pytest.raises(ValueError, match='budget'):
        workflow.prepare(config, tmp_path/'output')
    assert not (tmp_path/'output').exists()
