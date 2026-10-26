"""Integration guards for broadened research without silent qualification."""
import pytest
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
