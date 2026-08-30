"""Drift test: RFC 0003 §3.4 totals must match design.toml values.

If anyone edits design.toml without updating the RFC (or vice versa),
this test fails loudly. Regenerate the RFC table with:

    python -m osr_scenario.stats --format markdown
"""

from __future__ import annotations

import re
from pathlib import Path

from osr_scenario.stats import compute_stats

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMAWAH_DESIGN = REPO_ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml"
RFC_0003 = REPO_ROOT / "docs/rfcs/0003-samawah-reference-deployment.md"


def _find_first_int(text: str, pattern: str) -> int:
    m = re.search(pattern, text)
    assert m, f"pattern not found: {pattern}"
    return int(m.group(1))


def test_rfc_station_count_matches_design() -> None:
    rfc = RFC_0003.read_text()
    s = compute_stats(SAMAWAH_DESIGN)
    n = _find_first_int(rfc, r"Stations\s*\(unique[^)]*\)\s*\|\s*(\d+)\s*\|")
    assert n == s.unique_station_count, (
        f"RFC says {n} stations but design.toml has {s.unique_station_count}. "
        f"Regenerate the §3.4 table with `python -m osr_scenario.stats --format markdown`."
    )


def test_rfc_line_count_matches_design() -> None:
    rfc = RFC_0003.read_text()
    s = compute_stats(SAMAWAH_DESIGN)
    # Row: | Lines | 3 ... |
    m = re.search(r"\|\s*Lines\s*\|\s*(\d+)", rfc)
    assert m, "RFC 0003 §3.4 'Lines' row not found"
    n = int(m.group(1))
    assert n == s.line_count


def test_rfc_revenue_fleet_count_matches_design() -> None:
    rfc = RFC_0003.read_text()
    s = compute_stats(SAMAWAH_DESIGN)
    n = _find_first_int(rfc, r"Fleet \(revenue\)\s*\|\s*(\d+)")
    assert n == s.revenue_fleet


def test_rfc_route_km_matches_design_within_1km() -> None:
    rfc = RFC_0003.read_text()
    s = compute_stats(SAMAWAH_DESIGN)
    m = re.search(r"Route-km[^|]*\|[^0-9]*(\d+(?:\.\d+)?)\s*km", rfc)
    assert m, "RFC 0003 §3.4 'Route-km' row not found"
    n = float(m.group(1))
    assert abs(n - s.route_km) <= 1.0, (
        f"RFC route-km {n} vs design {s.route_km:.1f}; "
        f"drift tolerance is 1 km."
    )
