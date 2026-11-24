"""Run the Rust workforce model and retain the costed shift plan and its sources."""

import argparse
from hashlib import file_digest
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import mkdtemp
from time import perf_counter

from engineering.performance import run_reserved_command
from engineering.outline import workforce_plan

ROOT = Path(__file__).resolve().parents[2]
CRATE = ROOT / "crates/osr-workforce"


def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def evaluator_sources():
    paths = [CRATE / "Cargo.toml", CRATE / "Cargo.lock", *sorted((CRATE / "src").glob("*.rs")),
             Path(__file__), Path(workforce_plan.__file__), ROOT / "rust-toolchain.toml"]
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}


def json_file(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


def dollars(cents):
    return f"${cents // 100:,}.{cents % 100:02d}"


def hours(minutes):
    return f"{minutes / 60:,.1f}"


def accounted_hours(group, amount, missing):
    value = hours(group[amount])
    unknown = group[missing]
    if unknown == group["row_count"]:
        return "Open"
    return f"{value} + open" if unknown else value


def workplan_markdown(summary):
    scope = summary["scope"]
    if isinstance(scope, str):
        scope = {"label": scope}
    label = " · ".join(str(scope.get(field, "")) for field in ("network", "label")).strip(" ·")
    detail = [scope[key] for key in ("calendar_basis", "cost_basis", "scope_boundaries")
              if scope.get(key)]
    lines = [
        "# Costed workforce and shift workplan",
        "",
        f"Scope **{label or summary['plan_id']}**",
        "",
        f"Plan `{summary['plan_id']}` · {summary['row_count']:,} work rows · "
        f"{summary['availability_bps'] / 100:g}% capacity in the availability test.",
        "",
        "Amounts are planning estimates in US dollars. Each account has its own purchase, "
        "construction, training or operating period. Where a contract already includes "
        "labour, use the account to test or replace the allowance.",
        "",
        "| Phase and account | Required hours¹ | Paid hours¹ | Available hours¹ | "
        "Uncovered hours¹ · base → stress | Low | Base | High | Unpriced rows |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in summary["groups"]:
        amount = ([dollars(c) for c in group["known_cost_cents"]]
                  if group["unpriced_rows"] < group["row_count"] else ["Open"] * 3)
        required = accounted_hours(group, "known_required_minutes", "unknown_required_rows")
        paid = accounted_hours(group, "known_paid_minutes", "unknown_paid_rows")
        available = accounted_hours(group, "known_capacity_minutes", "unknown_capacity_rows")
        shortage = accounted_hours(group, "known_shortage_minutes", "unknown_shortage_rows")
        stress = accounted_hours(group, "known_stressed_shortage_minutes", "unknown_shortage_rows")
        lines.append(f"| {group['phase']} · {group['cost_account']} | {required} | {paid} | "
                     f"{available} | {shortage} → {stress} | {' | '.join(amount)} | "
                     f"{group['unpriced_rows']} |")
    lines.extend([
        "",
        "¹ Known subtotals. Unresolved hours are blank in the detailed rows and counted "
        "in the JSON report. Capacity in one shift or trade cannot cover a shortage in "
        "another. The availability test reduces productive capacity with payroll held fixed.",
        "",
        *[line for text in detail for line in (text, "")],
        "## Work awaiting quantities, quotations or deployment evidence",
        "",
        "| Phase | Work or evidence | Accountable role | Estimate basis or next input |",
        "|---|---|---|---|",
    ])
    for gap in summary["gaps"]:
        lines.append(f"| {gap['phase']} | {gap['work']} | {gap['owner']} | {gap['cost_basis']} |")
    lines.extend([
        "",
        "Use `workforce.csv` for each shift, role, requirement, cost and allowance. "
        "`workforce.parquet` carries the same rows in typed columns for subsequent queries. "
        "`plan.json` and `run-receipt.json` identify the input and recorded output bytes.",
        "",
    ])
    return "\n".join(lines)


def plan_input(args, target):
    if args.plan:
        if not args.plan.is_file() or args.plan.stat().st_size > 64 * 1024**2:
            raise ValueError("Supply an ordinary workplan JSON file of no more than 64 MiB")
        shutil.copyfile(args.plan, target)
        return
    json_file(target, workforce_plan.build_plan(args.network or "first", args.mode or "goa4"))


def execute(args, output):
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    attempt = Path(mkdtemp(prefix=".osr-workplan-", dir=output.parent))
    try:
        run_and_publish(args, attempt, output)
    except Exception as error:
        raise ValueError(f"{error}. Attempt retained at {attempt}") from error


def run_and_publish(args, attempt, output):
    source = attempt / "plan.json"
    plan_input(args, source)
    produced = attempt / "result"
    target = ROOT / "target"
    if target.is_symlink():
        raise ValueError("Use an ordinary repository target directory for the Rust build")
    sources = evaluator_sources()
    command = [
        "env", f"CARGO_TARGET_DIR={target}", f"CARGO_BUILD_JOBS={os.environ.get('OSR_CARGO_JOBS', '2')}",
        "cargo", "build", "--locked", "--release", "--manifest-path", str(CRATE / "Cargo.toml"),
    ]
    build_receipt, code = run_reserved_command(
        ROOT, ROOT, "workforce-rust-build", 3 * 1024**3,
        ["bash", "-c", 'log=$1; shift; exec "$@" > "$log" 2>&1',
         "osr-workforce-build", str(attempt / "build.log"), *command],
    )
    if code:
        json_file(attempt / "disk-receipt.json", build_receipt)
        raise ValueError(f"Rust build returned {code}")
    binary = target / "release/osr-workforce"
    binary_sha256 = digest(binary)
    started = perf_counter()
    simulation = [str(binary), str(source), str(produced), "--availability-bps", str(args.availability_bps)]
    run_receipt, code = run_reserved_command(
        ROOT, output.parent, "workforce-shift-simulation", 128 * 1024**2, simulation,
    )
    elapsed = perf_counter() - started
    if code:
        json_file(attempt / "disk-receipt.json", run_receipt)
        raise ValueError(f"Rust simulation returned {code}")

    summary = json.loads((produced / "summary.json").read_text())
    if (summary["input_sha256"] != digest(source) or digest(binary) != binary_sha256
            or evaluator_sources() != sources):
        raise ValueError("The input or evaluator changed during the run")
    (produced / "summary.md").write_text(workplan_markdown(summary))
    shutil.copyfile(source, produced / "plan.json")
    json_file(produced / "run-receipt.json", {
        "schema": "osr-workforce-run/1",
        "input_sha256": summary["input_sha256"],
        "binary_sha256": binary_sha256,
        "evaluator_source_sha256": sources,
        "availability_bps": args.availability_bps,
        "simulation_wall_seconds_including_reservation": elapsed,
        "file_sha256": {path.name: digest(path) for path in sorted(produced.iterdir())},
    })
    # The directory reservation prevents two simultaneous publishers from
    # replacing each other's results.
    output.mkdir()
    try:
        produced.rename(output)
    except OSError:
        output.rmdir()
        raise
    shutil.rmtree(attempt)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", choices=workforce_plan.NETWORKS, help="published workforce case (default first)")
    parser.add_argument("--mode", choices=workforce_plan.MODES, help="operating duty case (default goa4)")
    parser.add_argument("--plan", type=Path, help="edit or replace the published inputs with your own workplan JSON")
    parser.add_argument("--output", type=Path, required=True, help="new output directory for the complete workplan")
    parser.add_argument("--availability-bps", type=int, default=10_000,
                        help="stress capacity in basis points (default 10000, full planned capacity)")
    args = parser.parse_args(argv)
    if args.plan and (args.network or args.mode):
        parser.error("--plan supplies its own network and mode")
    if not 0 <= args.availability_bps <= 10_000:
        parser.error("--availability-bps must be between 0 and 10000")
    try:
        execute(args, args.output)
    except (OSError, ValueError) as error:
        print(f"Workplan: {error}", file=sys.stderr)
        return 1
    print(args.output / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
