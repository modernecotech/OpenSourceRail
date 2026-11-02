"""Integration guards for broadened research without silent qualification."""
import pytest
import json
import shutil
from engineering.station_rail import design_space as s


@pytest.fixture(scope='module')
def comparison():
    return s.assemble()


def test_alternatives_use_normal_load_and_preserve_unknown_installed_data(comparison):
    v=comparison
    assert len(v['structural_proposals'])==11
    assert len({r['bundle']['candidate_id'] for r in v['structural_proposals']})==11
    assert sum(len(r.get('additional_lineage',[])) for r in v['structural_proposals'])==1
    assert v['propulsion_plan']['candidate_proposal_count']==12
    assert v['propulsion_plan']['proposals'][0]['screen']['required_launch_force_N_lower_bound']==pytest.approx(11757.524371344067)
    assert v['vehicle_context']['accounted_mass_kg_per_car']==pytest.approx(24214.29217645682)
    assert v['whole_system_winner'] is v['complete_installed_mass_kg'] is v['complete_installed_cost_USD'] is None
    assert not v['full_body_native_dispatch'] and not v['default_changed']
    assert v['parent_provenance']['previous_evaluations_used_as_current_evidence'] is False
    assert v['parent_provenance']['previous_evaluations_usage']=='historical-diagnostic-triggers-only'
    assert v['parent_provenance']['stale_evaluator_source_paths']
    for row in v['structural_proposals']:
        assert row['bundle']['installed_tare_kg_per_car'] is None
        assert not row['bundle']['full_body_ranking_eligible']


def test_temperature_failure_generates_new_material_path_without_erasing_ancestry(comparison):
    rows=comparison['structural_proposals']
    failed=[r for r in rows if r['bounds']['necessary_screens']['supplier_continuous_temperature']=='fail']
    assert failed and all(r['bundle']['parameters']['core_id']=='pvc_h80' for r in failed)
    linked={r['parent_proposal_id'] for r in rows if r['parent_proposal_id']}
    linked.update(l['parent_proposal_id'] for r in rows for l in r.get('additional_lineage',[]))
    assert any(r['bundle']['candidate_id'] in linked for r in failed)
    for joint in comparison['attachment_examples']:
        assert joint['complete_installed_joint_mass_kg'] is None
        assert joint['price_unknown_is_zero'] is False
    assert all(g['complete_window_mass_kg'] is None for g in comparison['glazing_examples'])


def test_publication_binds_current_bytes_for_every_historical_evaluator_input(comparison):
    _,_,results,provenance=s.parent()
    expected={name for result in results for name in result['request']['evaluator_sources']}
    assert len(expected)==26
    assert set(provenance['current_evaluator_source_paths'])==expected
    sources=s.publication_sources(s.ROOT,comparison)
    assert expected <= set(sources)
    for name in expected:assert sources[name]==s.digest(s.ROOT/name)
    assert sources['engineering/station_rail/vehicle.py']!=results[0]['request']['evaluator_sources']['engineering/station_rail/vehicle.py']
    assert provenance['previous_evaluations_used_as_current_evidence'] is False
    assert 'engineering/station_rail/vehicle.py' in provenance['stale_evaluator_source_paths']


def test_resealed_manifest_cannot_omit_historical_evaluator_source(tmp_path):
    output=tmp_path/'packet';shutil.copytree(s.ROOT/s.OUTPUT,output)
    path=output/'manifest.json';manifest=json.loads(path.read_bytes())
    del manifest['source_sha256']['engineering/station_rail/vehicle.py']
    del manifest['manifest_id'];manifest['manifest_id']=s.identity(manifest)
    path.write_bytes(s.encoded(manifest))
    with pytest.raises(ValueError,match='source coverage differs'):
        s.verify(root=s.ROOT,output=output)


def test_historical_hash_cannot_be_relabelled_as_current_source(tmp_path):
    output=tmp_path/'packet';shutil.copytree(s.ROOT/s.OUTPUT,output)
    path=output/'manifest.json';manifest=json.loads(path.read_bytes())
    manifest['source_sha256']['engineering/station_rail/vehicle.py']='4298e2107f9b7b00be9046a6794270a8b28946f025995cbded2a5511bd3f432b'
    del manifest['manifest_id'];manifest['manifest_id']=s.identity(manifest)
    path.write_bytes(s.encoded(manifest))
    with pytest.raises(ValueError,match='Design-space source differs'):
        s.verify(root=s.ROOT,output=output)


def test_missing_current_evaluator_input_is_not_silently_left_unbound(monkeypatch):
    original=s.Path.is_file;missing=s.ROOT/'engineering/station_rail/vehicle.py'
    monkeypatch.setattr(s.Path,'is_file',lambda path:False if path==missing else original(path))
    with pytest.raises(ValueError,match='Current historical evaluator source unavailable'):
        s.parent()
