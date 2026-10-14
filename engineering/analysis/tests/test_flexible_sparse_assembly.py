"""Compact joint updates equal independent full-vehicle energy assembly."""

from copy import deepcopy
import math

import numpy as np
import pytest

from engineering.civil_exploration.variant_compiler import compile_variant
from engineering.civil_exploration.spatial_structure import Route
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
from engineering.integration_programme.flexible_vehicle import FlexibleVehicle


@pytest.fixture(scope="module")
def package():
    return compile_variant()


@pytest.mark.parametrize("curved", [False, True])
@pytest.mark.parametrize("mode_count", [2, 6])
def test_compact_matrices_equal_dense_joint_energy_form(package, curved, mode_count):
    cfg = deepcopy(package["spatial_configuration"])
    if curved:
        cfg["route"].update(radius_m=800., cant_rad=.04)
    route = Route(cfg["route"])
    vehicle = FlexibleVehicle(package["model"], cfg["joint_laws"], mode_count=mode_count)
    actual_k, actual_c, actual_m, (_, expanded) = vehicle.matrices(route, 17., 2.)
    dense_k, dense_c, dense_m, (_, rigid) = SpatialVehicle.matrices(vehicle, route, 17., 2.)
    for record in vehicle.modal.values():
        i = record["index"]
        basis = record["basis"]
        n = len(basis["frequencies_hz"])
        dense_m[i:i+n, i:i+n] += basis["modal_mass"]
        dense_k[i:i+n, i:i+n] += basis["modal_stiffness"]
        dense_c[i:i+n, i:i+n] += np.diag(2*vehicle.damping_ratio*2*math.pi*np.asarray(basis["frequencies_hz"]))
    for flexible_plan, rigid_plan in zip(expanded, rigid, strict=True):
        assert flexible_plan["joint"]["id"] == rigid_plan["joint"]["id"]
        j = flexible_plan["J"]
        old = rigid_plan["J"]
        law = flexible_plan["joint"]
        # Full dense virtual-work products form the independent reference.
        dense_k += j.T @ law["K"] @ j - old.T @ law["K"] @ old
        dense_c += j.T @ law["C"] @ j - old.T @ law["C"] @ old
    np.testing.assert_allclose(actual_k, (dense_k+dense_k.T)/2, rtol=1e-13, atol=1e-7)
    np.testing.assert_allclose(actual_c, (dense_c+dense_c.T)/2, rtol=1e-13, atol=1e-9)
    np.testing.assert_allclose(actual_m, (dense_m+dense_m.T)/2, rtol=1e-13, atol=1e-9)
