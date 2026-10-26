"""Delivery records must follow the selection without manufacturing acceptance."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import os

import pytest

from engineering.development_baseline import ROOT, FLAGS, evaluate, exports


@pytest.fixture(scope='module')
def root():
    return Path(os.environ.get('OSR_EVIDENCE_ROOT', str(ROOT)))


@pytest.fixture(scope='module')
def current(root):
    return evaluate.build(root)


@pytest.fixture(scope='module')
def compiled(current, root):
    return exports.compile(current, root=root)


def test_every_delivery_record_matches_selected_identity(compiled, current):
    for name in ('bom', 'manufacturing', 'procurement', 'assembly', 'civil', 'controls'):
        row = compiled[name]
        assert all(row[k] == current[k] for k in ('selection_id', 'candidate_id', 'body_candidate_id', 'magnet_component_id'))
        assert row['station_id'] == current['service']['selected_station']['station_id']
        assert row['civil_interface_id'] == current['interfaces']['civil']['civil_interface_id']
        assert all(row[k] is v for k, v in FLAGS.items())


def test_current_control_counts_do_not_inherit_450m_or_virtual_gap(compiled):
    c = compiled['controls']
    assert (c['launch_speed_cap_m_s'], c['target_headway_s'], c['normal_capacity_pphpd']) == (20., 120., 8280.)
    assert c['shared_station_winding_m'] == 800.
    assert c['addressed_sections_per_direction'] == 64
    assert c['addressed_sections_both_directions'] == 128
    assert c['minimum_concurrent_train_phase_current_branches_both_directions'] == 4
    assert c['magnetic_operating_gap_m'] is None
    assert c['coupon_drawing_reference_gap_m'] == .012
    assert c['coupon_gap_is_selected_operating_gap'] is False
    assert c['fixture_gap_is_physical_evidence'] is False
    assert c['physical_converter_rating'] is None


def test_unknowns_and_all_city_scope_are_explicit(compiled):
    assert compiled['bom']['mass']['installed_tare_kg_per_car'] is None
    assert compiled['procurement']['total_price_USD'] is None
    assert compiled['manufacturing']['production_labour_hours_per_car'] is None
    assert compiled['assembly']['scheduled_start_dates'] is None
    assert compiled['civil']['fully_installed_route_quantities'] is None
    assert compiled['procurement']['baghdad_trainsets_analytical'] == 906
    assert compiled['procurement']['city_scope']['city_count'] is None
    assert compiled['procurement']['city_scope']['whole_repository_city_delivery_complete'] is False


def test_city_index_must_have_same_candidate(current, root):
    index = {k: current[k] for k in ('selection_id', 'candidate_id', 'body_candidate_id', 'magnet_component_id')}
    index.update(city_count=266, index_id='a' * 64)
    assert exports.compile(current, root=root, city_index=index)['procurement']['city_scope']['city_count'] == 266
    index['candidate_id'] = 'f' * 64
    with pytest.raises(ValueError, match='city index belongs'):
        exports.compile(current, root=root, city_index=index)


def test_selected_primitive_export_reopens_and_payload_tampering_fails(tmp_path, current, root):
    target = tmp_path / 'selected'
    exports.write(target, current, root=root)
    assert exports.verify(target, current, root=root)['current'] is True
    assert not (target / 'procurement.json').exists()
    procurement_bytes = gzip.decompress((target / 'procurement.json.gz').read_bytes())
    assert (target / 'procurement.json.gz').read_bytes() == gzip.compress(procurement_bytes, mtime=0)
    procurement = json.loads(procurement_bytes)
    assert procurement['stock_inventory_per_car'] == current['vehicle']['inventory']
    assert procurement['baghdad_trainsets_analytical'] == 906
    bim = json.loads((target / 'bim.json').read_bytes())
    if bim['execution'] == 'completed':
        assert bim['native_reopened'] is True
        assert bim['identity_and_volume_checks_pass'] is True
        assert len(bim['parts']) == 8
        assert bim['complete_vehicle_IFC'] is False
    else:
        assert bim['execution'] == 'not-run'
    cad = json.loads((target / 'cad.json').read_bytes())
    assert cad['execution'] == 'not-run'
    changed = json.loads((target / 'controls.json').read_bytes())
    changed['launch_speed_cap_m_s'] = 15.
    (target / 'controls.json').write_bytes(evaluate.encoded(changed))
    with pytest.raises(ValueError, match='payload differs'):
        exports.verify(target, current, root=root)


def test_primitive_definition_uses_selected_civil_dimensions(current):
    revised = deepcopy(current)
    revised['interfaces']['civil']['span_m'] = 20.
    revised['interfaces']['civil']['reference_prismatic_concrete_volume_m3'] *= .8
    parts = exports._bim_parts(revised)
    assert parts[0]['size_m'][0] == 20.
    assert parts[1]['size_m'][0] == 20.
    assert parts[1]['size_m'][1:] == [.5, .035]
    assert all('selected-' in p['id'] for p in parts)


def test_portable_native_cad_verifies_without_private_build_folder(current, root):
    # This deliberately supplies no private build directory. The authenticated
    # published archive contains the original native reopen receipt and geometry.
    portable = exports._verify_cad_archive(current, root)
    assert portable['source_archive'] == 'docs/design-engine/ferrite-maglev/comfort-design/vehicle-artifacts.tar.gz'
    assert portable['verification']['native_reopen_established'] is True
    assert portable['verification']['candidate_id'] == current['candidate_id']
    assert len(portable['geometry_sha256']) == 64
    assert len(portable['source_archive_sha256']) == 64
    assert 'source_package' not in portable
