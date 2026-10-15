"""Physical inertia limits are invariant under rotation and SI magnitude."""

import numpy as np
import pytest

from osr_mech.vehicle_mass_properties import inertia_tensor


@pytest.mark.parametrize("scale", [1e-24, 1., 1e24])
@pytest.mark.parametrize("tensor", [
    [[1., 2., 0.], [2., 1., 0.], [0., 0., 1.]],  # negative principal inertia
    np.diag([1., 1., 3.]),  # positive but impossible principal moments
    [[2., 0., 1.], [0., 1., 0.], [1., 0., 2.]],  # same violation, rotated
    [[1., 1e-6, 0.], [0., 1., 0.], [0., 0., 1.]],
])
def test_impossible_tensors_rejected_at_every_scale(tensor, scale):
    with pytest.raises(ValueError):
        inertia_tensor((np.asarray(tensor) * scale).tolist())


@pytest.mark.parametrize("scale", [1e-24, 1., 1e24])
@pytest.mark.parametrize("moments", [[0., 0., 0.], [0., 2., 2.], [1., 1., 2.], [2., 3., 4.]])
def test_point_line_lamina_and_solid_limits_accept_rotated_tensors(moments, scale):
    rotation = np.array([[1., -2., 2.], [2., 2., 1.], [-2., 1., 2.]]) / 3
    tensor = rotation @ np.diag(moments) @ rotation.T * scale
    assert np.array_equal(inertia_tensor(tensor.tolist()), tensor)


@pytest.mark.parametrize("value", [
    [[True, 0., 0.], [0., 1., 0.], [0., 0., 1.]],
    [[1., 0., 0.], [0., float('nan'), 0.], [0., 0., 1.]],
    [[1., 0., 0.], [0., float('inf'), 0.], [0., 0., 1.]],
    [[1., 0.], [0., 1.]], [[1.], [1., 2.]],
])
def test_invalid_numbers_and_shapes_rejected(value):
    with pytest.raises(ValueError):
        inertia_tensor(value)
