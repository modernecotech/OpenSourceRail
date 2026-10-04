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
    if set(override) - {"operations", "charging"} or set(override.get("operations", {})) - {"habd"}:
        raise ValueError("city overrides support operations.habd and repeated charging cabinets only")
    if "charging" in override:
        charging = override["charging"]
        if set(charging) != {"station_cabinet_count", "basis"}:
            raise ValueError("charging override requires station_cabinet_count and an engineering basis")
        count = charging["station_cabinet_count"]
        if type(count) is not int or not 1 <= count <= 8 or not str(charging["basis"]).strip():
            raise ValueError("charging override requires 1–8 repeated cabinets and a nonempty basis")
    policy = override.get("operations", {}).get("habd")
    if policy is None:
        return apply_charging(design_path, override.get("charging"))
    if set(policy) - {"enabled", "approach_distance_m"} or type(policy.get("enabled")) is not bool:
        raise ValueError("HABD override requires a boolean enabled policy and known keys")
    distance = policy.get("approach_distance_m", 500)
    if type(distance) is not int or distance <= 0:
        raise ValueError("HABD approach distance must be a positive integer")
    text = design_path.read_text()
    previous = tomllib.loads(text)
    if previous.get("operations", {}).get("habd", {}) == policy:
        return apply_charging(design_path, override.get("charging"))
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
    apply_charging(design_path, override.get("charging"))
    return True


def apply_charging(design_path: Path, policy: dict | None) -> bool:
    """Price identical cabinets and their repeated station-site equipment once.

    The scenario generator expands each declared cabinet into power, storage,
    contacts and site supply. Depot-main PV/storage stays in the depot ledger.
    Timetable dwell and fleet are retained conservatively; no capacity credit is
    inferred without rerunning the complete nominal and degraded screens.
    """
    if policy is None:
        return False
    text = design_path.read_text()
    design = tomllib.loads(text)
    old_count = design["costs"]["technology_basis"]["station_charging_cabinet_count"]
    count = policy["station_cabinet_count"]
    if count == old_count:
        return False
    root = Path(__file__).resolve().parents[2]
    capex = tomllib.loads((root / "lib/templates/capex-costs.toml").read_text())
    costs = design["costs"]
    charging = round(costs["charging_microgrid_usd"] * count / old_count)
    net = costs["total_usd"] - costs["epc_overhead_usd"] + charging - costs["charging_microgrid_usd"]
    overhead = round(net * capex["overhead"]["epc_fraction"])
    values = {"station_charging_cabinet_count": count}
    for key, value in [("charging_microgrid_usd", charging), ("epc_overhead_usd", overhead), ("total_usd", round(net + overhead))]:
        values[key] = value
        values[key.replace("_usd", "_eur")] = round(value * capex["schema"]["usd_to_eur"])
    for key, value in values.items():
        text, n = re.subn(r"^(" + re.escape(key) + r"\s*=\s*)[^\s#]+", lambda m: m[1] + str(value), text, count=1, flags=re.M)
        if n != 1:
            raise ValueError("missing charging capital field " + key)
    current = tomllib.loads(text)
    before = {k: v for k, v in design.items() if k != "costs"}
    after = {k: v for k, v in current.items() if k != "costs"}
    if before != after:
        raise ValueError("charging equipment override changed topology or timetable")
    design_path.write_text(text)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args()
    print(f"city operating override {'applied' if apply(args.design) else 'current/absent'}: {args.design}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
