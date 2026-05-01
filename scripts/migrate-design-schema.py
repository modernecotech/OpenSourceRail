#!/usr/bin/env python3
"""Idempotent migration helper for generated city `design.toml` files.

Currently migrates designs to schema version 2:

- adds `[schema] version = 2`
- introduces `charging_microgrid_eur`
- keeps `power_eur` as a deprecated compatibility alias
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def migrate(path: Path) -> bool:
    text = path.read_text()
    data = tomllib.loads(text)
    changed = False

    if "schema" not in data and "[costs]\n" in text:
        schema = (
            "[schema]\n"
            "version = 2\n"
            'cost_power_eur_alias = "deprecated; use costs.charging_microgrid_eur"\n\n'
        )
        text = text.replace("[costs]\n", schema + "[costs]\n", 1)
        changed = True

    data = tomllib.loads(text)
    costs = data.get("costs", {})
    if "charging_microgrid_eur" not in costs and "power_eur" in costs:
        text = re.sub(
            r"(?m)^power_eur\s*=\s*([0-9]+)(.*)$",
            lambda m: (
                f"charging_microgrid_eur = {m.group(1)}\n"
                f"power_eur            = {m.group(1)}  # deprecated alias for charging_microgrid_eur"
            ),
            text,
            count=1,
        )
        changed = True

    if changed:
        path.write_text(text)
    return changed


def main() -> int:
    count = 0
    for path in sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml")):
        count += int(migrate(path))
    print(f"migrated {count} design.toml file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
