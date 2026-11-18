"""Passenger information uses selected identities and refuses stale departure times."""
from copy import deepcopy
import json
from pathlib import Path
import tomllib

import pytest

from services.integration.osr_integration.signage import project, render_html


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sources():
    selection = tomllib.loads((ROOT / "docs/reference-v07/digital/selected.toml").read_text())
    handoff = json.loads((ROOT / "docs/reference-v07/digital/production/handoff.json").read_text())
    return selection, handoff


def snapshot(selection, handoff):
    line = handoff["configuration_id"]
    return {"schema": "osr-passenger-service-snapshot/1", "source": "simulation",
            "physical_candidate_id": selection["physical_candidate_id"],
            "evaluation_id": handoff["evaluation_id"],
            "selection_evaluation_id": selection["evaluation_id"],
            "selection_id": selection["selection_id"],
            "line_id": line, "station_index": 3, "station_id": f"{line}:S03",
            "observed_at_utc": "2026-11-18T12:00:00Z",
            "departures": [{"service_id": "run-12", "destination_station_index": 8,
                            "departure_at_utc": "2026-11-18T12:04:00Z"}]}


def test_selected_simulation_departure_is_accessible_and_read_only(sources):
    selection, handoff = sources
    result = project(selection, handoff, snapshot(selection, handoff),
                     at_utc="2026-11-18T12:00:30Z")
    assert result["physical_candidate_id"] == handoff["physical_candidate_id"]
    assert result["data_status"] == "fresh"
    assert result["departures"][0]["destination_station_id"].endswith(":S08")
    assert "Station 3" in result["accessible_text"]
    assert "Station 8" in result["accessible_text"]
    assert result["read_only"] is True
    assert result["movement_authority"] is False
    assert result["control_output"] is False
    assert "commands" not in result


def test_stale_snapshot_hides_departure_times(sources):
    selection, handoff = sources
    result = project(selection, handoff, snapshot(selection, handoff),
                     at_utc="2026-11-18T12:01:01Z")
    assert result["data_status"] == "stale"
    assert result["departures"] == []
    assert "Service information unavailable" in result["accessible_text"]
    assert "12:04" not in result["accessible_text"]


def test_changed_handoff_content_requires_new_evaluation(sources):
    selection, handoff = sources
    changed = deepcopy(handoff)
    changed["control_electronics"]["equipment"]["station-dispatch-controller"]["quantity"] = 13
    with pytest.raises(ValueError, match="content differs"):
        project(selection, changed, snapshot(selection, handoff),
                at_utc="2026-11-18T12:00:30Z")


@pytest.mark.parametrize("change", [
    {"physical_candidate_id": "other-candidate"},
    {"evaluation_id": "other-evaluation"},
    {"line_id": "other-line"},
    {"station_id": "wrong-station"},
    {"station_index": 13},
    {"source": "physical"},
])
def test_mixed_or_unselected_source_is_rejected(sources, change):
    selection, handoff = sources
    feed = snapshot(selection, handoff)
    feed.update(change)
    with pytest.raises(ValueError):
        project(selection, handoff, feed, at_utc="2026-11-18T12:00:30Z")


def test_future_or_unzoned_time_and_invented_departures_are_rejected(sources):
    selection, handoff = sources
    feed = snapshot(selection, handoff)
    with pytest.raises(ValueError, match="Future"):
        project(selection, handoff, feed, at_utc="2026-11-18T11:59:59Z")
    with pytest.raises(ValueError, match="Timezone"):
        project(selection, handoff, feed, at_utc="2026-11-18T12:00:30")
    altered = deepcopy(feed)
    altered["departures"][0]["departure_at_utc"] = "2026-11-18T11:59:00Z"
    with pytest.raises(ValueError, match="Invalid source departure"):
        project(selection, handoff, altered, at_utc="2026-11-18T12:00:30Z")


def test_static_display_escapes_source_text_and_has_no_controls(sources):
    selection, handoff = sources
    display = project(selection, handoff, snapshot(selection, handoff),
                      at_utc="2026-11-18T12:00:30Z")
    display["station_label"] = '<img src=x onerror=alert(1)>'
    display["departures"][0]["service_id"] = '<script>alert(1)</script>'
    html = render_html(display)
    assert '<h1 id="osr-signage-heading">&lt;img' in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<script' not in html and '<button' not in html and '<form' not in html
    assert 'role="status"' in html and 'scope="col"' in html


def test_stale_display_never_renders_departure_rows(sources):
    selection, handoff = sources
    display = project(selection, handoff, snapshot(selection, handoff),
                      at_utc="2026-11-18T12:01:01Z")
    display["departures"] = [{"service_id": "must-not-show",
                              "destination_station_id": "S08",
                              "departure_at_utc": "2026-11-18T12:04:00Z"}]
    html = render_html(display)
    assert 'data-status="stale"' in html
    assert 'Service information unavailable' in html
    assert 'must-not-show' not in html and '<table>' not in html
