#!/usr/bin/env python3
"""Reject nearby stations that were not consolidated into one complex."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TRANSFER_ENVELOPE_M = 600.0
MINIMUM_INLINE_CHAINAGE_M = 1_180.0
PREFERRED_INLINE_CHAINAGE_M = 1_200.0
CITY_CENTRE_RADIUS_M = 3_000.0
CITY_CENTRE_CLUSTER_ENVELOPE_M = 600.0


def distance_m(a: dict, b: dict) -> float:
    lat1, lon1 = float(a["lat"]), float(a["lon"])
    lat2, lon2 = float(b["lat"]), float(b["lon"])
    radians = math.pi / 180.0
    x = (lon2 - lon1) * radians * math.cos((lat1 + lat2) * radians / 2)
    y = (lat2 - lat1) * radians
    return 6_371_000.0 * math.hypot(x, y)


def city_centre(design: dict) -> dict | None:
    city = design.get("city", {})
    location = design.get("location", {})
    lat = city.get("centroid_lat", location.get("center_lat"))
    lon = city.get("centroid_lon", location.get("center_lon"))
    bbox = city.get("bbox") or location.get("bbox")
    if lon is None and isinstance(bbox, dict):
        try:
            lon = (float(bbox["west"]) + float(bbox["east"])) / 2.0
        except (KeyError, TypeError, ValueError):
            lon = None
    if lat is None and isinstance(bbox, dict):
        try:
            lat = (float(bbox["south"]) + float(bbox["north"])) / 2.0
        except (KeyError, TypeError, ValueError):
            lat = None
    if lat is None or lon is None:
        return None
    return {"lat": float(lat), "lon": float(lon)}


def validate(path: Path) -> dict:
    design = tomllib.loads(path.read_text(encoding="utf-8"))
    stations = list(design.get("stations", []))
    interchanges = list(design.get("interchanges", []))
    centre = city_centre(design)
    findings: list[dict] = []
    review_findings: list[dict] = []
    station_ids: dict[str, int] = {}
    for station in stations:
        station_id = str(station["id"])
        station_ids[station_id] = station_ids.get(station_id, 0) + 1
    for station_id, count in sorted(station_ids.items()):
        if count > 1:
            findings.append(
                {
                    "code": "duplicate-station-id",
                    "station": station_id,
                    "record_count": count,
                    "severity": "fail",
                }
            )
    for index, first in enumerate(stations):
        for second in stations[index + 1 :]:
            separation = distance_m(first, second)
            if first["line"] != second["line"]:
                first_group = first.get("junction_group")
                second_group = second.get("junction_group")
                if separation > TRANSFER_ENVELOPE_M:
                    if (
                        centre is not None
                        and separation <= CITY_CENTRE_CLUSTER_ENVELOPE_M
                        and distance_m(first, centre) <= CITY_CENTRE_RADIUS_M
                        and distance_m(second, centre) <= CITY_CENTRE_RADIUS_M
                        and (first_group is None or first_group != second_group)
                    ):
                        findings.append(
                            {
                                "code": "city-centre-stations-not-consolidated",
                                "centre_radius_m": CITY_CENTRE_RADIUS_M,
                                "distance_m": round(separation, 1),
                                "first_station": first["id"],
                                "first_line": first["line"],
                                "second_station": second["id"],
                                "second_line": second["line"],
                                "severity": "fail",
                            }
                        )
                    continue
                if first_group is None or first_group != second_group:
                    findings.append(
                        {
                            "code": "nearby-cross-line-stations-not-one-interchange",
                            "distance_m": round(separation, 1),
                            "first_station": first["id"],
                            "first_line": first["line"],
                            "second_station": second["id"],
                            "second_line": second["line"],
                            "severity": "fail",
                        }
                    )
                continue

            # Same-line stops are not interchange candidates, but duplicate
            # or very short consecutive placements are equally undesirable.
            chainage_gap = abs(float(first.get("s_m", 0.0)) - float(second.get("s_m", 0.0)))
            finding = {
                "code": "same-line-stations-too-close",
                "chainage_gap_m": round(chainage_gap, 1),
                "distance_m": round(separation, 1),
                "first_station": first["id"],
                "line": first["line"],
                "second_station": second["id"],
            }
            if chainage_gap < MINIMUM_INLINE_CHAINAGE_M:
                findings.append({**finding, "severity": "fail"})
            elif chainage_gap < PREFERRED_INLINE_CHAINAGE_M:
                review_findings.append({**finding, "severity": "review"})

    grouped_platforms: dict[int, list[dict]] = {}
    for station in stations:
        group = station.get("junction_group")
        if group is not None:
            grouped_platforms.setdefault(int(group), []).append(station)
    interchange_by_group: dict[int, list[dict]] = {}
    for interchange in interchanges:
        group = int(interchange["junction_group"])
        interchange_by_group.setdefault(group, []).append(interchange)

    for group, members in sorted(grouped_platforms.items()):
        member_lines = sorted({str(member["line"]) for member in members})
        member_ids = sorted(str(member["id"]) for member in members)
        records = interchange_by_group.get(group, [])
        if len(member_lines) < 2:
            findings.append(
                {
                    "code": "junction-group-is-not-cross-line",
                    "junction_group": group,
                    "lines": member_lines,
                    "severity": "fail",
                }
            )
        if len(records) != 1:
            findings.append(
                {
                    "code": "junction-group-needs-one-interchange-record",
                    "junction_group": group,
                    "record_count": len(records),
                    "severity": "fail",
                }
            )
            continue
        record = records[0]
        if sorted(str(value) for value in record.get("lines", [])) != member_lines:
            findings.append(
                {
                    "code": "interchange-lines-do-not-match-platforms",
                    "interchange": record.get("id"),
                    "junction_group": group,
                    "severity": "fail",
                }
            )
        if sorted(str(value) for value in record.get("platforms", [])) != member_ids:
            findings.append(
                {
                    "code": "interchange-members-do-not-match-platforms",
                    "interchange": record.get("id"),
                    "junction_group": group,
                    "severity": "fail",
                }
            )

    for group, records in sorted(interchange_by_group.items()):
        if group not in grouped_platforms:
            findings.append(
                {
                    "code": "interchange-has-no-platform-group",
                    "junction_group": group,
                    "record_count": len(records),
                    "severity": "fail",
                }
            )

    return {
        "city": str(design.get("city", {}).get("slug", path.parent.name.lower())),
        "design_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "failures": findings,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "interchange_count": len(interchanges),
        "city_centre_cluster_envelope_m": CITY_CENTRE_CLUSTER_ENVELOPE_M,
        "city_centre_radius_m": CITY_CENTRE_RADIUS_M,
        "minimum_inline_chainage_m": MINIMUM_INLINE_CHAINAGE_M,
        "preferred_inline_chainage_m": PREFERRED_INLINE_CHAINAGE_M,
        "passed": not findings,
        "review_findings": review_findings,
        "station_count": len(stations),
        "transfer_envelope_m": TRANSFER_ENVELOPE_M,
    }


def _report_result(result: dict, *, include_review_findings: bool) -> dict:
    out = dict(result)
    review_findings = list(out.get("review_findings", []))
    out["review_finding_count"] = len(review_findings)
    if not include_review_findings:
        out.pop("review_findings", None)
    return out


def write_report(
    results: list[dict],
    output: Path,
    *,
    include_review_findings: bool = True,
) -> None:
    report_results = [
        _report_result(result, include_review_findings=include_review_findings)
        for result in results
    ]
    report = {
        "city_count": len(report_results),
        "failed_cities": [result["city"] for result in report_results if not result["passed"]],
        "failure_count": sum(len(result["failures"]) for result in report_results),
        "passed": all(result["passed"] for result in report_results),
        "results": report_results,
        "review_finding_count": sum(result["review_finding_count"] for result in report_results),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--design", type=Path, action="append")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = (
        sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
        if args.all
        else args.design
    )
    results = [validate(path.resolve()) for path in paths]
    output = args.output
    if output is None:
        output = (
            REPO_ROOT / "cities/catalogue/station-cluster-validation.json"
            if args.all or len(paths) != 1
            else paths[0].resolve().parent / "engineering/station-cluster-summary.json"
        )
    write_report(
        results,
        output,
        include_review_findings=(len(paths) == 1),
    )
    failed = [result["city"] for result in results if not result["passed"]]
    print(
        f"cities={len(results)} failed={len(failed)} "
        f"failures={sum(len(result['failures']) for result in results)} "
        f"review_findings={sum(len(result['review_findings']) for result in results)}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
