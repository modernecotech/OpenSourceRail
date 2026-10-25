from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil

import pytest

from engineering.trip_dynamics import vehicle


@pytest.fixture(scope='module')
def retained_root():
    root = Path(os.environ.get('OSR_SOURCE_ROOT', vehicle.ROOT))
    if not (root/'docs/design-engine/vehicle-optimisation/summary.json').is_file():
        pytest.skip('retained publication omitted in sparse worktree; set OSR_SOURCE_ROOT')
    return root


@pytest.fixture(scope='module')
def catalogue(retained_root):
    return vehicle.current_vehicle_definitions(retained_root)


def test_disjoint_canonical_mass_and_partial_cad_are_different_scopes(catalogue):
    c = catalogue['canonical']
    assert c['candidate_id'] == 'a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd'
    assert c['comparison_empty_kg_per_car'] == pytest.approx(25618.5915003343)
    assert c['comparison_aw3_kg_per_car']-c['comparison_empty_kg_per_car'] == pytest.approx(12000.)
    rows = c['disjoint_inventory']
    assert sum(x['mass_kg_per_car'] for x in rows) == pytest.approx(c['comparison_empty_kg_per_car'])
    assert len({x['id'] for x in rows}) == len(rows)
    assert next(x for x in rows if x['evidence_class']=='unlocated-allocation')['mass_kg_per_car'] == pytest.approx(7378.253763406856)
    actual = next(x for x in rows if x['id']=='retained/actual-stock')
    assert len(set(actual['part_ids'])) == len(actual['part_ids']) > 500
    assert c['modules_per_car'] == 24
    p = catalogue['partial_cad']
    assert p['defined_material_mass_kg'] == pytest.approx(9492.609052646612)
    assert p['whole_equipped_vehicle_mass_kg'] is None
    assert p['defined_material_mass_kg'] != c['comparison_empty_kg_per_car']
    assert 'never additive' in p['scope']


def test_both_material_directions_preserved_without_adoption(catalogue):
    rows = catalogue['alternatives']
    assert len(rows) == len({x['candidate_id'] for x in rows}) == 4
    assert {x['body_family'] for x in rows} == {'retained-frame', '6061-T6-envelope',
        '6082-T6-deep-stringers', '6005A-T5-wide-stringers'}
    selected = next(x for x in rows if x['next_experiment_only'])
    assert selected['candidate_id'].startswith('de9e5f82391f')
    assert selected['body_family']=='retained-frame'
    assert selected['comparison_aw3_mass_band_kg'] == pytest.approx([27911.715270147215, 28066.715270147215])
    assert catalogue['requested_gfrp_optimisation']['status']=='unknown'
    for row in [catalogue['canonical'], *rows]:
        assert row['installed_empty_kg_per_car'] is None
        assert row['cg_m'] is None and row['inertia_kg_m2'] is None
        assert not row['complete_equipped_vehicle'] and not row['configuration_adopted']
        assert row['unknown_installed_inventory']


def test_replacement_removals_are_disjoint(catalogue):
    for row in catalogue['alternatives']:
        changes = row['replacement_ledger']['changes']
        parts, budgets = [], []
        for x in changes:
            parts.extend(x.get('removed_part_ids', []))
            budgets.extend(x.get('removed_allocation_ids', []))
        assert len(parts)==len(set(parts))
        assert len(budgets)==len(set(budgets))
        assert row['replacement_ledger']['base_empty_kg'] == pytest.approx(catalogue['canonical']['comparison_empty_kg_per_car'])


def test_readiness_cannot_silently_combine_magnet_candidate_and_canonical_mass(catalogue):
    c = catalogue['canonical']
    scenario = dict(scenario_id='route-load-environment',candidate_id=c['candidate_id'],cars=6,car_length_m=17.,load_case='AW3')
    gates = {x['id']:x['state'] for x in vehicle.structural_readiness(c, scenario)}
    assert gates['body/scenario-identity']=='pass'
    assert gates['body/equipped-mass-inertia']=='unknown'
    assert gates['body/equipped-inventory']=='unknown'
    scenario['candidate_id']=catalogue['alternatives'][0]['candidate_id']
    assert next(x for x in vehicle.structural_readiness(c,scenario) if x['id']=='body/scenario-identity')['state']=='fail'


def test_missing_fields_do_not_match_through_none_equality():
    gates = {x['id']: x['state'] for x in vehicle.structural_readiness({}, {})}
    assert gates['body/scenario-identity'] == gates['body/formation'] == 'fail'


def test_nonfinite_claimed_equipped_mass_cannot_pass(catalogue):
    from copy import deepcopy
    c = deepcopy(catalogue['canonical'])
    c.update(installed_aw3_kg_per_car=float('nan'), cg_m=[0., 0., 0.], inertia_kg_m2=[[0.,0.,0.]]*3)
    case = dict(candidate_id=c['candidate_id'], cars=6, car_length_m=17., load_case='AW3')
    gates = {x['id']: x['state'] for x in vehicle.structural_readiness(c, case)}
    assert gates['body/equipped-mass-inertia'] == 'fail'


@pytest.mark.parametrize('corrupt', ['payload', 'manifest', 'bound-source'])
def test_pinned_publication_and_actual_source_mutation_refuse(tmp_path, retained_root, catalogue, corrupt):
    # Copy precisely the source closure used by this reader, not legacy native
    # binaries. This tests the public root API with real retained publication.
    bindings = catalogue['source_bindings']
    for name in bindings:
        dest = tmp_path/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(retained_root/name, dest)
    name = {'payload':'docs/design-engine/vehicle-optimisation/summary.json',
            'manifest':'docs/design-engine/vehicle-optimisation/manifest.json',
            'bound-source':'engineering/ferrite_maglev/candidate-magnetics.toml'}[corrupt]
    path = tmp_path/name
    path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(ValueError, match='digest changed'):
        vehicle.current_vehicle_definitions(tmp_path)


def test_symlink_and_escape_refused(tmp_path):
    with pytest.raises(ValueError, match='relative'):
        vehicle._checked(tmp_path, '../outside', '0'*64)
    source=tmp_path/'source'
    source.write_text('a')
    (tmp_path/'alias').symlink_to(source)
    with pytest.raises(ValueError, match='symlink'):
        vehicle._checked(tmp_path, 'alias', sha256(b'a').hexdigest())
