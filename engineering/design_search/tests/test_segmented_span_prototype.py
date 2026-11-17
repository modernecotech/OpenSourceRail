"""Controlled planning packet must preserve the civil source and open holds."""

from pathlib import Path
from hashlib import sha256
import json
import shutil

import pytest

from engineering.design_search import segmented_span_prototype as plan


def test_committed_packet_replays_from_source_evaluation():
    expected = (plan.ROOT / plan.OUTPUT).read_bytes()
    assert expected == plan.encoded(plan.build())
    value = json.loads(expected)
    assert value['plan_id'] == sha256(plan.encoded({k: v for k, v in value.items() if k != 'plan_id'})).hexdigest()
    assert value['physical_candidate_id'] == plan.CANDIDATE
    assert value['source_evaluation_id'] == '79b896dc9517a00414245af473411b675f8eb03898788897812fa2d949458367'
    assert value['selected_reference_changed'] is False


def test_span_interfaces_and_cost_remain_held():
    value = plan.build()
    assert value['physical_accepted'] is False
    assert value['manufacturing_release'] is False
    assert value['cost_status']['candidate_complete_installed_cost_iqd'] is None
    assert value['physical_scope']['joint_and_tendon_structural_design'] is None
    assert value['straight_span_quantities']['demonstrator_2km']['ten_m_segments'] == 400
    assert value['straight_span_quantities']['demonstrator_2km']['independent_supports'] == 202
    assert value['calculated_screens']['whole_beam_only']['maximum_live_moment_section_x_m'] == 10.5
    assert value['calculated_screens']['whole_beam_only']['nominal_joint_plane_local_envelope']['x_m'] == 10.0
    assert value['engineering_checks']['torsion']['status'] == 'held'
    assert [s['id'] for s in value['erection_stages']] == ['S0', 'S1', 'S2', 'S3', 'S4', 'S5']
    joint = next(x for x in value['interfaces'] if x['id'] == 'segment-joint')
    assert joint['controlled_shop_length_m'] is None
    assert joint['approved_tolerance_m'] is None
    assert all(x['unit_quote_iqd'] is None for x in value['supplier_quote_schedule_2km'])


def test_changed_source_result_is_refused(tmp_path: Path):
    folder = tmp_path / plan.SOURCE
    folder.parent.mkdir(parents=True)
    shutil.copytree(plan.ROOT / plan.SOURCE, folder)
    result = folder / 'result.json'
    value = json.loads(result.read_bytes())
    value['lifting_transport']['half_required_hook_kg_hypothesis'] = 1
    result.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='Civil source packet changed'):
        plan.build(tmp_path)


def test_resealed_source_manifest_is_not_silently_admitted(tmp_path: Path):
    folder = tmp_path / plan.SOURCE
    folder.parent.mkdir(parents=True)
    shutil.copytree(plan.ROOT / plan.SOURCE, folder)
    manifest = folder / 'manifest.json'
    value = json.loads(manifest.read_bytes())
    value['verification'] = 'changed assertion'
    manifest.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='source manifest differs'):
        plan.build(tmp_path)


def test_cost_handoff_replays_and_never_promotes_proxy_to_candidate_total():
    expected = (plan.ROOT / plan.COST_OUTPUT).read_bytes()
    assert expected == plan.encoded(plan.build_cost_handoff())
    value = json.loads(expected)
    assert value['physical_candidate_id'] == plan.CANDIDATE
    assert value['civil_plan_id'] == plan.build()['plan_id']
    assert value['comparison_only']['proxy_is_not_segmented_candidate_installed_cost'] is True
    assert value['comparison_only']['unsegmented_30km_class_C_civil_proxy_usd'] == pytest.approx(107702670.9707151)
    for key in ('candidate_installed_civil_cost_2km_iqd', 'candidate_installed_civil_cost_30km_iqd',
                'candidate_civil_delta_2km_iqd', 'candidate_civil_delta_30km_iqd'):
        assert value[key] is None
    rows = {r['item']: r for r in value['quote_rows']}
    assert rows['complete segmented beam factory package']['quantity_2km'] == 200
    assert rows['complete segmented beam factory package']['quantity_30km'] == 3000
    assert rows['segment stock breakdown only']['quantity_2km'] == 400
    assert rows['segment stock breakdown only']['quantity_30km'] == 6000
    assert rows['temporary tower placement and release']['quantity_2km'] == 200
    assert rows['bearing and restraint unit']['quantity_30km'] == 12000
    assert rows['joint and tendon breakdown only']['cost_treatment'] == 'breakdown_only'
    assert value['symbolic_cost_formula']['breakdown_only_rows_in_rollup'] is False
    assert value['symbolic_cost_formula']['formula_evaluable_with_current_inputs'] is False
    assert value['comparison_only']['unsegmented_2km_installed_civil_proxy_iqd'] is None
    assert all(r['unit_quote_iqd'] is None and r['delta_iqd'] is None for r in rows.values())
    assert value['comparison_only']['three_m_footing_material_delta_2km_by_support_ratio_iqd'] == pytest.approx(
        value['comparison_only']['three_m_footing_material_delta_30km_iqd'] * 202 / 3002)


def test_cost_handoff_refuses_stale_plan(tmp_path: Path):
    folder = tmp_path / plan.SOURCE
    folder.parent.mkdir(parents=True)
    shutil.copytree(plan.ROOT / plan.SOURCE, folder)
    target = tmp_path / plan.OUTPUT
    target.parent.mkdir(parents=True)
    target.write_bytes((plan.ROOT / plan.OUTPUT).read_bytes() + b'changed')
    with pytest.raises(ValueError, match='plan differs'):
        plan.build_cost_handoff(tmp_path)
