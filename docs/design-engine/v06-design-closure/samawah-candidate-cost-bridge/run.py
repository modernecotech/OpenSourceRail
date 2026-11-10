#!/usr/bin/env python3
"""Reproduce and seal the limited Samawah candidate cost bridge."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

from engineering.railway_project.city_cost_bridge import (  # noqa: E402
    CITY_RESULT, RATE_PACKET, _read_json, _verify_packet, build,
)
from engineering.station_rail.common import encoded, identity  # noqa: E402

CASES = ("low", "base", "high")
SOURCE = ROOT / "engineering/railway_project/city_cost_bridge.py"


def tri(values):
    return " / ".join(f"${values[c]:,.0f}" for c in CASES)


def render_readme(result: dict, run: dict) -> str:
    lines = [
        "# Samawah detailed-candidate cost bridge",
        "",
        "This packet prices selected, physically matched quantity fragments for the exact package-07 detailed body and five-line Samawah planning case. It is **not** a complete city CAPEX or whole-life estimate.",
        "",
        "## Candidate identity",
        "",
        f"- City candidate/evaluation: `{result['city_candidate_id']}` / `{result['source_city_recalculation_evaluation_id']}`",
        f"- Body candidate/evaluation: `{result['body_candidate_id']}` / `{result['body_evaluation_id']}`",
        f"- Authenticated city input: `{result['city_input_id']}`; route quantity: {result['quantity_basis']['route_m']/1000:,.3f} km.",
        f"- Ratebook packet: `{result['ratebook_packet_id']}`; ratebook candidate/body: `{result['ratebook_source_candidate_id']}` / `{result['ratebook_source_body_candidate_id']}`.",
        "- The ratebook candidate is a different historical physical design. Its geometry, body, quantities, fleet, service, totals and NPV were not copied into this candidate. Only the named Class-C unit-cost ratios below were carried as explicit rate assumptions.",
        "",
        "## Candidate-linked fragments (USD, low / base / high)",
        "",
        "| Item | Candidate quantity | Rate basis | Cost fragment |",
        "| --- | ---: | --- | ---: |",
    ]
    for row in result["matched_rate_lines"]:
        lines.append(f"| `{row['key']}` | {row['quantity']:,.3f} {row['unit']} | Historical Class-C rate from {row['rate_source_line_id'][:8]} | {tri(row['cost_usd'])} |")
    lines += [
        f"| Candidate counted BOM and process subtotal | {result['quantity_basis']['trainsets_by_case']['low']} / {result['quantity_basis']['trainsets_by_case']['base']} / {result['quantity_basis']['trainsets_by_case']['high']} low/base/high trainsets | Candidate body’s own counted parts/process ledger | {tri(result['known_candidate_bom_subtotal_usd'])} |",
        f"| **Partial priced-fragment sum** | | The items above only | **{tri(result['partial_priced_fragment_sum_usd'])}** |",
        "",
        "The partial sum covers the detailed body’s counted BOM/process subtotal plus five matched rail, fastening, repeat-beam, bearing-pad and joint/drain/lifting fragments. It is not an installed price. Construction haul, crane and erection cost is not transferred because the historical unit line mixes in station track absent from this candidate quantity set. The source beam’s load basis has not been checked against this candidate, and the beam quantity remains a reference geometry request pending a detailed civil load evaluation.",
        "",
        "## Chinese supply and mass-purchase treatment",
        "",
        "Rail mass uses the retained 60E1 profile coefficient of 60.21 kg/m from `engineering/outline/city_civil.py`. The retained Samawah make/buy and China-bulk cost packets have identical low/base/high rates for these five infrastructure rows. The current detailed body’s own BOM is not re-priced from the older vehicle’s China scenario. No China supplier quotation, project volume tier, negotiated discount, import contract or local market validation is available in this candidate packet, so no additional mass-purchase discount is assumed.",
        "",
        "## Explicitly unpriced",
        "",
    ]
    lines += [f"- {item}" for item in result["unpriced_or_unresolved"]]
    lines += [
        "- The remaining cost scopes (construction/erection, stations/power, foundations/site, factory and tooling, land/utilities/depot, traction energy, operations, maintenance, renewals, recovery, reliability, disposal, finance/tax and full delivery) do not have candidate-matched scope totals.",
        "- `installed_capex_usd` and `whole_life_npv_usd` therefore remain null. `cost_complete`, `service_complete` and every physical/release flag remain false.",
        "",
        "## Reproduction and integrity",
        "",
        "Run from the repository root:",
        "",
        "```sh",
        "tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge/run.py --output-dir /tmp/osr-samawah-cost-bridge-replay",
        "```",
        "",
        f"Execution ID: `{run['execution_id']}`. Packet integrity ID is in `manifest.json`. The run used the repository Python process; it did not invoke CAD, FEM, GIS, ERPNext, a network client or a supplier lookup. No OS sandbox or process resource limit is claimed. See `execution.json` for measured wall time and peak RSS. `bridge.json` contains exact source hashes and line calculations.",
        "",
        "This is a priced outline fragment under unverified Class-C rates. It does not select propulsion, validate the train or guideway, approve procurement, or establish an investment estimate.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE.with_name("samawah-candidate-cost-bridge-current-source"))
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    expected_names = ("bridge.json", "request.json", "execution.json", "README.md", "manifest.json")
    if any((out / name).exists() for name in expected_names):
        raise SystemExit("Refusing to overwrite an existing evidence packet")

    start = time.monotonic()
    city = _read_json(ROOT / CITY_RESULT)
    rate_dir = ROOT / RATE_PACKET
    rate_manifest = _verify_packet(rate_dir)
    cost = _read_json(rate_dir / "cost-project-make-buy.json")
    china_cost = _read_json(rate_dir / "cost-china-bulk-buy.json")
    bridge_sources = {
        CITY_RESULT.as_posix(): hashlib.sha256((ROOT / CITY_RESULT).read_bytes()).hexdigest(),
        (RATE_PACKET / "manifest.json").as_posix(): hashlib.sha256((rate_dir / "manifest.json").read_bytes()).hexdigest(),
        (RATE_PACKET / "cost-project-make-buy.json").as_posix(): hashlib.sha256((rate_dir / "cost-project-make-buy.json").read_bytes()).hexdigest(),
        "docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz": hashlib.sha256((ROOT / "docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz").read_bytes()).hexdigest(),
        "engineering/outline/city_civil.py": hashlib.sha256((ROOT / "engineering/outline/city_civil.py").read_bytes()).hexdigest(),
        "engineering/railway_project/city_cost_bridge.py": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "engineering/railway_project/city_recalculation.py": hashlib.sha256((ROOT / "engineering/railway_project/city_recalculation.py").read_bytes()).hexdigest(),
        "engineering/station_rail/common.py": hashlib.sha256((ROOT / "engineering/station_rail/common.py").read_bytes()).hexdigest(),
    }
    bridge_sources[(RATE_PACKET / "cost-china-bulk-buy.json").as_posix()] = hashlib.sha256((rate_dir / "cost-china-bulk-buy.json").read_bytes()).hexdigest()
    result = build(city, cost, china_cost, rate_manifest, source_sha256=bridge_sources)
    (out / "bridge.json").write_bytes(encoded(result))
    request = {
        "schema": "osr-samawah-candidate-cost-bridge-request/1",
        "city_candidate_id": result["city_candidate_id"],
        "source_city_recalculation_evaluation_id": result["source_city_recalculation_evaluation_id"],
        "body_candidate_id": result["body_candidate_id"],
        "body_evaluation_id": result["body_evaluation_id"],
        "ratebook_packet_id": rate_manifest["manifest_id"],
        "ratebook_scenario": "project-make-buy Class-C unit rates for five matching infrastructure quantities",
        "request_id": identity({"city_candidate_id": result["city_candidate_id"], "body_candidate_id": result["body_candidate_id"], "body_evaluation_id": result["body_evaluation_id"], "ratebook_packet_id": rate_manifest["manifest_id"], "ratebook_scenario": "project-make-buy Class-C unit rates for five matching infrastructure quantities"}),
    }
    (out / "request.json").write_bytes(encoded(request))
    source_commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    execution = {
        "schema": "osr-samawah-candidate-cost-bridge-execution/1",
        "executed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": source_commit,
        "request_id": request["request_id"],
        "candidate_id": result["city_candidate_id"],
        "body_candidate_id": result["body_candidate_id"],
        "evaluation_id": result["evaluation_id"],
        "resources": {"wall_seconds": time.monotonic() - start, "max_rss_kib": usage.ru_maxrss,
            "cpu_user_seconds": usage.ru_utime, "cpu_system_seconds": usage.ru_stime,
            "hard_limits_applied": False},
        "execution_boundary": {"cad": False, "fem": False, "gis": False, "erpnext": False,
            "network_client_invoked": False, "external_supplier_lookup": False,
            "os_sandbox_enforced": False, "source_tree_writable": True},
    }
    execution["execution_id"] = identity(execution)
    (out / "execution.json").write_bytes(encoded(execution))
    (out / "README.md").write_text(render_readme(result, execution), encoding="utf-8")
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
    manifest = {"schema": "osr-samawah-candidate-cost-bridge-packet/1", "request_id": request["request_id"],
        "execution_id": execution["execution_id"], "evaluation_id": result["evaluation_id"],
        "candidate_id": result["city_candidate_id"], "body_candidate_id": result["body_candidate_id"],
        "source_commit": source_commit, "files_sha256": files, "file_count": len(files)}
    manifest["manifest_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    print(json.dumps({"evaluation_id": result["evaluation_id"], "execution_id": execution["execution_id"],
        "manifest_id": manifest["manifest_id"], "partial_priced_fragment_sum_usd": result["partial_priced_fragment_sum_usd"]}, sort_keys=True))


if __name__ == "__main__":
    main()
