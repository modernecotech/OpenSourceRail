#!/usr/bin/env python3
"""Refresh a controlled city budget without changing its network topology."""
import argparse
import importlib.util
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args()
    path = Path(__file__).with_name("recalculate-city-capex.py")
    spec = importlib.util.spec_from_file_location("city_capex_refresh", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    changed = module.recalculate(args.design)
    print(f"controlled layout preserved; CAPEX {'refreshed' if changed else 'current'}: {args.design}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
