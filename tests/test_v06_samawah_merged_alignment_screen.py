import gzip
import hashlib
import json
from pathlib import Path

import pytest

from engineering.outline import planning_geometry
from engineering.railway_project.city_recalculation import verify as verify_city
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/design-engine/v06-design-closure/samawah-merged-alignment-screen-current-source-attempt-03"
RUNNER = ROOT / "docs/design-engine/v06-design-closure/samawah-merged-alignment-runner-01"
MERGE_PACKET = ROOT / "docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_packet_files(packet, manifest, *, packet_key="packet_id"):
    assert manifest[packet_key] == identity({k: v for k, v in manifest.items() if k != packet_key})
    actual = {
        path.relative_to(packet).as_posix(): digest(path)
        for path in packet.rglob("*") if path.is_file() and path.relative_to(packet).as_posix() != "manifest.json"
    }
    assert actual == manifest["files_sha256"]
    assert len(actual) == manifest["file_count"]


def test_merged_stop_alignment_screen_is_sealed_and_preserves_candidate_ancestry():
    manifest = read_json(PACKET / "manifest.json")
    assert manifest["schema"] == "osr-samawah-merged-stop-straightening-packet/1"
    assert_packet_files(PACKET, manifest)
    assert manifest["selected"] is False
    assert manifest["physical_accepted"] is False
    assert manifest["gate_closed"] is False

    request = read_json(PACKET / "request.json")
    execution = read_json(PACKET / "execution.json")
    summary = read_json(PACKET / "summary.json")
    assert request["request_id"] == identity({k: v for k, v in request.items() if k != "request_id"})
    assert request["runner_sha256"] == digest(RUNNER / "run.py")
    assert request["worker_sha256"] == digest(RUNNER / "worker.py")
    assert execution["request_id"] == request["request_id"]
    assert execution["source_commit"] == manifest["source_commit"] == summary["source_commit"]
    assert execution["returncode"] == 0
    assert execution["preserved_packets_unchanged"] is True
    assert execution["execution_boundary"]["os_sandbox_enforced"] is False

    merge_manifest = read_json(MERGE_PACKET / "manifest.json")
    assert_packet_files(MERGE_PACKET, merge_manifest)
    assert request["station_merge_packet_id"] == merge_manifest["packet_id"]
    assert request["station_merge_candidate_id"] == merge_manifest["candidate_id"]
    merged_city_path = ROOT / request["city_input_source_path"]
    assert digest(merged_city_path) == merge_manifest["files_sha256"]["derived-city.json"]
    merged_city = read_json(merged_city_path)
    assert merged_city["input_id"] == request["city_input_id"]
    assert merged_city["input_id"] == identity({k: v for k, v in merged_city.items() if k != "input_id"})
    assert merged_city["parent_city_input_id"] == "dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de"

    baseline = read_json(PACKET / "baseline.json")
    assert verify_city(baseline)
    assert baseline["candidate_id"] == manifest["baseline_candidate_id"] == request["station_merge_candidate_id"]
    assert baseline["evaluation_id"] == summary["baseline_evaluation_id"]
    assert baseline["quantities"]["station_markers"] == 25
    assert baseline["definition_failures"] == []
    assert summary["baseline"]["fleet_low_base_high"] == [42, 59, 87]

    expected_holds = [
        "Exact-body service and available force/braking/thermal/charging evidence absent.",
        "Exact-body mapped civil and station/terminal assemblies not evaluated.",
        "All fourteen complete scope prices and the complete whole-life NPV remain unknown.",
        "The declared 18.0-hour service day exceeds 2 shifts of 8.0 hours; extended coverage needs an explicit workforce/relief roster.",
    ]
    assert summary["baseline"]["holds"] == expected_holds
    expected = [
        (25.0, 54.513761329707485, [39, 57, 84], 1858.8480101408227,
         {"standard_beams": 5456, "standard_shared_bents": 2733,
          "running_rail_m": 218055.04531882994, "running_fastening_sets": 363427}),
        (50.0, 54.173288985535144, [39, 56, 84], 1852.2493135281968,
         {"standard_beams": 5422, "standard_shared_bents": 2716,
          "running_rail_m": 216693.15594214058, "running_fastening_sets": 361157}),
        (100.0, 53.96316571655054, [39, 56, 84], 1851.57179039559,
         {"standard_beams": 5402, "standard_shared_bents": 2706,
          "running_rail_m": 215852.66286620215, "running_fastening_sets": 359756}),
    ]
    parent_lines = {row["line_id"]: row for row in merged_city["lines"]}
    assert len(summary["scenarios"]) == 3
    for index, (tolerance, route_km, fleet, runtime, quantities) in enumerate(expected):
        row = summary["scenarios"][index]
        assert row["tolerance_m"] == tolerance
        assert row["route_km"] == pytest.approx(route_km, abs=1e-9)
        assert row["fleet_low_base_high"] == fleet
        assert row["line1_runtime_s"] == pytest.approx(runtime, abs=1e-8)
        assert row["definition_failure_count"] == 0
        assert row["holds"] == expected_holds
        assert row["all_station_coordinates_fixed"] is True
        assert row["all_cost_scopes_unknown"] is True
        assert row["selected"] is False
        assert row["guideway_quantity_screen"] == quantities

        name = f"tolerance-{int(tolerance):03d}m"
        derived = read_json(PACKET / "scenarios" / name / "derived-city.json")
        result = read_json(PACKET / "scenarios" / name / "evaluation.json")
        details = read_json(PACKET / "scenarios" / name / "line-details.json")
        assert derived["parent_city_input_id"] == merged_city["input_id"]
        assert derived["input_id"] == identity({k: v for k, v in derived.items() if k != "input_id"})
        assert result["candidate_id"] == row["candidate_id"] == manifest["scenario_candidate_ids"][str(tolerance)]
        assert result["evaluation_id"] == row["evaluation_id"] == manifest["scenario_evaluation_ids"][str(tolerance)]
        assert verify_city(result)
        assert result["definition_failures"] == []
        assert result["scope_totals_usd"] == {scope: {case: None for case in ("low", "base", "high")}
                                               for scope in result["scope_totals_usd"]}
        assert result["quantities"]["standard_beams"] == quantities["standard_beams"]
        assert result["quantities"]["standard_shared_bents"] == quantities["standard_shared_bents"]
        assert result["quantities"]["running_rail_m"] == pytest.approx(quantities["running_rail_m"], abs=1e-8)
        assert result["quantities"]["running_fastening_sets"] == quantities["running_fastening_sets"]
        assert len(details) == 5
        assert max(row["max_deviation_m_by_line"].values()) <= tolerance + 0.05

        output_lines = {item["line_id"]: item for item in result["physical_definition"]["mapped_lines"]}
        for line_id, line in output_lines.items():
            source = parent_lines[line_id]
            assert [(s["id"], s["lon"], s["lat"]) for s in line["stops"]] == [
                (s["id"], s["lon"], s["lat"]) for s in source["stops"]
            ]
            chain = planning_geometry.route(line["coordinates"], line["shape"])
            for stop in line["stops"]:
                point = planning_geometry.point(line["coordinates"], chain, stop["chainage_m"])
                assert point == pytest.approx((stop["lon"], stop["lat"]), abs=1e-10)

    prior = PACKET / "attempt-history/attempt-02-verified-baseline"
    prior_manifest = read_json(prior / "manifest.json")
    assert_packet_files(prior, prior_manifest)
    assert prior_manifest["scenario_candidate_ids"] == manifest["scenario_candidate_ids"]
    assert prior_manifest["scenario_evaluation_ids"] == manifest["scenario_evaluation_ids"]
    assert "attempt-history/attempt-02-verified-baseline/manifest.json" in manifest["files_sha256"]
    review = (PACKET / "independent-review.md").read_text(encoding="utf-8")
    assert "No OS-level read-only sandbox was enforced" in review
    assert "zero 120 m platform-envelope definition failures" in review
