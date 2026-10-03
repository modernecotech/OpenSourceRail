#!/usr/bin/env python3
"""Apply controlled operating policies after synthesis, before scenario emission."""
from __future__ import annotations

import argparse
import json
import re
import tempfile
import tomllib
from pathlib import Path


def apply(design_path: Path) -> bool:
    override_path = design_path.with_name("design-overrides.toml")
    if not override_path.is_file():
        return False
    override = tomllib.loads(override_path.read_text())
    if set(override) != {"operations"} or set(override["operations"]) != {"habd"}:
        raise ValueError("city overrides currently support operations.habd only; geometry and budgets must be regenerated")
    policy = override["operations"]["habd"]
    if set(policy) - {"enabled", "approach_distance_m"} or type(policy.get("enabled")) is not bool:
        raise ValueError("HABD override requires a boolean enabled policy and known keys")
    distance = policy.get("approach_distance_m", 500)
    if type(distance) is not int or distance <= 0:
        raise ValueError("HABD approach distance must be a positive integer")
    text = design_path.read_text()
    previous = tomllib.loads(text)
    if previous.get("operations", {}).get("habd", {}) == policy:
        return False
    block = "[operations.habd]\n" + "".join(f"{k} = {json.dumps(v)}\n" for k, v in sorted(policy.items()))
    pattern = r"(?ms)^\[operations\.habd\]\n.*?(?=^\[|\Z)"
    if re.search(pattern, text):
        updated = re.sub(pattern, block+"\n", text)
    else:
        # Insert before arrays so subsequent line properties remain in their
        # original table; trailing tables are also valid but less readable.
        marker = text.find("[[lines]]")
        if marker < 0:
            raise ValueError("synthesised design has no line array")
        updated = text[:marker]+block+"\n"+text[marker:]
    current = tomllib.loads(updated)
    expected = previous.copy()
    expected["operations"] = {**previous.get("operations", {}), "habd": policy}
    if current != expected:
        raise ValueError("override changed more than the controlled operating policy")
    with tempfile.NamedTemporaryFile("w", dir=design_path.parent, delete=False) as handle:
        handle.write(updated)
        temporary = Path(handle.name)
    temporary.replace(design_path)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args()
    print(f"city operating override {'applied' if apply(args.design) else 'current/absent'}: {args.design}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
