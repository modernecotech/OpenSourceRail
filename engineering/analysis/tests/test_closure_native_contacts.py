"""Exact contact remains distinct from positive material penetration."""
from types import SimpleNamespace
import pytest
from engineering.design_engine.native_cad import bbox_overlap_volume
from engineering.design_consistency import contracts
from engineering.continuous_design import study_confirmation
from engineering.twin_workflow import core


def box(lo, hi):
    return SimpleNamespace(**{axis+suffix: point[i] for suffix, point in (('Min', lo), ('Max', hi)) for i, axis in enumerate('XYZ')})


def test_bbox_upper_bound_keeps_contact_zero_and_positive_overlap_positive():
    a = box([0, 0, 0], [100, 100, 100])
    assert bbox_overlap_volume(a, box([100, 0, 0], [200, 100, 100])) == 0.
    assert bbox_overlap_volume(a, box([101, 0, 0], [200, 100, 100])) == 0.
    assert bbox_overlap_volume(a, box([99, 0, 0], [200, 100, 100])) == 10000.
    assert bbox_overlap_volume(a, box([10, 10, 10], [20, 20, 20])) == 1000.


@pytest.mark.parametrize('centre,expected', ((.1, 'passed'), (.099, 'failed')))
def test_native_face_contact_passes_and_one_mm_penetration_still_fails(tmp_path, centre, expected):
    materials = {'steel': dict(density_kg_m3=7850.)}
    parts = [contracts.part(name, 'steel', dict(role=name,
        primitives=[contracts.box(name, .1, .1, .1, [x, 0., 0.])]), materials)
        for name, x in (('a', 0.), ('b', centre))]
    for part in parts:
        part['manufacturing_unit_id'] = part['id']
    model = dict(schema='osr-engineering-representations/1', name='contact-control', revision='fixture',
        materials=materials, parts=parts, assembly_joints=[], construction_stages=[],
        mandatory_evidence=['Fixture control only'], physical_validation=False, production_released=False)
    path = tmp_path/'definition.json'
    core.write(path, model)
    proof, state, error = study_confirmation.native(path, tmp_path/'native')
    assert state == expected, error
    if state == 'passed': assert proof['native_reopened'] and proof['step_volume_reconciled']
