"""Rail profile volume ↔ published linear mass."""

from __future__ import annotations

import pytest

from osr_mech.common import RAIL_GEOMETRY, RailProfile
from osr_mech.track.rail import linear_mass_kg_per_m, rail_bar, rail_section

STEEL_DENSITY_KG_PER_M3 = 7850.0


@pytest.mark.parametrize("profile", list(RailProfile))
def test_rail_linear_mass_within_published_tolerance(profile: RailProfile) -> None:
    """Extruded model volume × steel density should match published linear
    mass within ± 5 %.

    The 5 % margin absorbs the polygon approximation of the rail section
    (no fillets, no head-foot radii) plus the UIC tolerance on the
    profile itself.
    """
    bar = rail_bar(profile=profile, length_mm=1000.0)
    volume_mm3 = bar.volume
    volume_m3 = volume_mm3 / 1_000_000_000
    implied_mass_kg = volume_m3 * STEEL_DENSITY_KG_PER_M3
    published_mass_kg = linear_mass_kg_per_m(profile)

    ratio = implied_mass_kg / published_mass_kg
    assert 0.95 <= ratio <= 1.05, (
        f"{profile.value}: implied {implied_mass_kg:.1f} kg/m vs "
        f"published {published_mass_kg:.1f} kg/m (ratio {ratio:.3f})"
    )


def test_rail_section_shortcut_equals_1m_bar() -> None:
    a = rail_section(RailProfile.UIC_60E1).volume
    b = rail_bar(RailProfile.UIC_60E1, length_mm=1000.0).volume
    assert a == pytest.approx(b, rel=1e-9)
