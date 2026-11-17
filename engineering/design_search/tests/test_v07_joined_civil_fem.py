"""Native joined 10 m civil beam and its source-bound artifact."""
from pathlib import Path
import tempfile

import pytest

from engineering.design_search import v07_joined_civil_fem as fem


def test_joined_civil_native_crowd_pose_and_integrity():
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / "civil"
        result = fem.build(output)
        assert result == fem.check(output)
        assert result["physical_candidate_id"] == "osr-v07-joined-prototype-20261117"
        assert result["cases"]["equal-share"]["vertical_force_relative_residual"] < 1e-6
        assert 0.0005 < -result["cases"]["equal-share"]["midspan_displacement_m"][2] < 0.002
        assert result["cases"]["cg-bound-original"]["vertical_force_relative_residual"] < 1e-6
        assert result["cases"]["cg-bound-revised-one-rail"]["rail_to_rail_vertical_difference_m"] > 0
        revision = result["digital_civil_revision_option"]
        assert revision["revised_strands"] == 13
        assert revision["original_gross_longitudinal_screens"]["service_tension_N_per_m2"] > 0
        assert revision["gross_longitudinal_screens"]["service_tension_N_per_m2"] <= 0
        assert result["cases"]["cg-bound-revised"]["physical_candidate_id"] != result["physical_candidate_id"]
        assert result["site_or_physical_accepted"] is False
        (output / "cg-bound-revised-one-rail.inp").write_text("changed\n")
        with pytest.raises(ValueError, match="Native artifact differs"):
            fem.check(output)
