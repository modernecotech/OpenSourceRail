"""Portable saved-state review, using small analytic controls rather than jobs."""
from copy import deepcopy
import numpy as np
import pytest

from engineering.railway_progress import structures as frozen
from engineering.railway_progress import structural_review as review
from engineering.railway_progress.tests.test_structures import cantilever


def test_equal_numpy_and_json_scalars_are_normalized_without_changing_values():
    original=dict(A=np.float64(.0014133333333333333),E=np.float64(70e9))
    saved=dict(A=.0014133333333333333,E=70e9)
    assert frozen._close(saved,original) is False
    assert review._same(saved,original) is True
    assert review.normalize(original)==saved
    assert review._same(dict(saved,E=35e9),original) is False


def test_normalization_does_not_turn_boolean_into_number_or_nan_into_evidence():
    assert review._same(True,1) is False
    with pytest.raises(ValueError):review.normalize(dict(A=float('nan')))


@pytest.fixture
def control(monkeypatch):
    model=cantilever();model['elements'][0]['A']=np.float64(model['elements'][0]['A'])
    F=np.zeros(12);F[8]=-1000.;cases=[('beam',F,{})];loads=dict(upper_mass_kg=10.)
    response=frozen.solve(model,cases)
    request=dict(vehicle={},mesh_sizes_m=[1.],joint_translation_N_m=1e9,joint_rotation_Nm_rad=1e6,material_scale=1.,contact_gap_hypothesis_m=.04)
    worker=dict(results=[dict(mesh_m=1.,model=review.normalize(model),loads=deepcopy(loads),response=review.normalize(response))])
    monkeypatch.setattr(frozen,'build_model',lambda *a,**kw:(model,[]))
    monkeypatch.setattr(frozen,'load_cases',lambda *a,**kw:(cases,loads))
    return request,worker


def test_saved_state_passes_only_after_identical_numeric_representation_is_canonicalized(control):
    request,worker=control
    with pytest.raises(ValueError,match='semantic'):frozen._verify_responses(request,worker)
    actual=review.review_responses(request,worker)
    assert actual[0]['cases'][0]['free_relative_residual']<1e-10
    assert actual[0]['cases'][0]['approved_strength_margin'] is None


@pytest.mark.parametrize('mutation',[
    lambda sample:sample['model']['elements'][0].update(E=35e9),
    lambda sample:sample['loads'].update(upper_mass_kg=1.),
    lambda sample:sample['response']['cases'][0]['support_reactions'][0].update(reaction=999.),
    lambda sample:sample['response']['cases'][0]['elements'][0].update(maximum_normal_stress_proxy_Pa=0.),
    lambda sample:sample['response']['cases'][0].update(strain_energy_J=0.),
])
def test_normalization_does_not_admit_changed_physics_or_derived_results(control,mutation):
    request,worker=control;mutation(worker['results'][0])
    with pytest.raises(ValueError):review.review_responses(request,worker)


def test_saved_support_displacement_cannot_be_overwritten(control):
    request,worker=control
    worker['results'][0]['response']['cases'][0]['displacements_m_rad'][0][0]=.001
    with pytest.raises(ValueError,match='support'):review.review_responses(request,worker)


def test_upstream_identity_cannot_silently_change(monkeypatch):
    assert review.sources()[review.UPSTREAM]==review.UPSTREAM_SHA256
    monkeypatch.setattr(review,'UPSTREAM_SHA256','0'*64)
    with pytest.raises(ValueError,match='Frozen'):review.sources()


def test_portable_diagnostics_keep_recorded_values_after_reader_rounding_passes_checks(control,monkeypatch):
    request,worker=control
    baseline=review.review_responses(request,worker)
    original=frozen._response
    def reader_rounding(*args,**kwargs):
        value=original(*args,**kwargs)
        value['relative_energy_residual']+=1e-16
        value['free_relative_residual']+=1e-25
        return value
    monkeypatch.setattr(frozen,'_response',reader_rounding)
    changed_reader=review.review_responses(request,worker)
    assert changed_reader==baseline
    assert review.identity(changed_reader)==review.identity(baseline)
    assert changed_reader[0]['cases'][0]['relative_energy_residual']==worker['results'][0]['response']['cases'][0]['relative_energy_residual']


def test_persisting_saved_diagnostics_does_not_bypass_independent_numerical_checks(control,monkeypatch):
    request,worker=control;original=frozen._response
    def excessive_difference(*args,**kwargs):
        value=original(*args,**kwargs);value['relative_energy_residual']+=1e-5
        return value
    monkeypatch.setattr(frozen,'_response',excessive_difference)
    with pytest.raises(ValueError,match='arithmetic'):review.review_responses(request,worker)
