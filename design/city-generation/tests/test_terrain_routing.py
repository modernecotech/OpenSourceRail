from __future__ import annotations

import numpy as np

from osr_geo.terrain import terrain_slope_percent


def test_terrain_slope_uses_a_stable_baseline_for_resampled_dem() -> None:
    flat = np.full((9, 9), 12.0, dtype=np.float32)
    assert np.allclose(terrain_slope_percent(flat, 20.0), 0.0)

    # Six metres of rise over 120 m is a 5% ground slope. The calculation
    # should not amplify each quantised 20 m sample into a false cliff.
    ramp = np.tile(np.arange(9, dtype=np.float32), (9, 1))
    slope = terrain_slope_percent(ramp, 20.0)
    assert 2.0 < float(slope[4, 4]) < 6.0


def test_terrain_slope_preserves_missing_elevation_cells() -> None:
    elevation = np.full((5, 5), 20.0, dtype=np.float32)
    elevation[2, 2] = np.nan
    slope = terrain_slope_percent(elevation, 100.0)
    assert np.isnan(slope[2, 2])
