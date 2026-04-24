"""CLI: regenerate a scenario.toml from a design.toml.

Usage:
    python -m osr_scenario --design designs/.../design.toml \
                           --out scenarios/<slug>.toml

With no arguments, regenerates `scenarios/samawah.toml` from
`designs/middle-east/iraq/samawah/design.toml` relative to the
repo root.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import GeneratorError, generate_from_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="osr_scenario",
        description="Regenerate a sim scenario.toml from a city design.toml.",
    )
    ap.add_argument(
        "--design",
        type=Path,
        default=None,
        help="path to the design.toml (default: Samawah)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="path to write the scenario.toml (default: scenarios/<slug>.toml)",
    )
    ap.add_argument(
        "--templates",
        type=Path,
        default=None,
        help="path to designs/templates/ (auto-discovered from --design)",
    )
    args = ap.parse_args(argv)

    repo_root = _find_repo_root()
    if args.design is None:
        args.design = repo_root / "designs/middle-east/iraq/samawah/design.toml"
    if args.out is None:
        # Derive from design slug.
        import tomllib
        slug = tomllib.loads(args.design.read_text()).get("design", {}).get("id", "design")
        short = slug.rsplit("/", 1)[-1]
        args.out = repo_root / f"scenarios/{short}.toml"

    try:
        text = generate_from_path(args.design, args.templates)
    except GeneratorError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}  ({len(text)} bytes)")
    return 0


def _find_repo_root() -> Path:
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "Cargo.toml").exists():
            return parent
    return Path.cwd()


if __name__ == "__main__":
    raise SystemExit(main())
