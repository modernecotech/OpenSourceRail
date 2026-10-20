#!/usr/bin/env python3
"""Generate/check the primary maglev directory; legacy inventory is explicit."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    if not args.legacy:
        from engineering.ferrite_maglev import navigation
        data = navigation.publish(args.output or navigation.OUTPUT, check=args.check)
        print(json.dumps(data['inventory'], sort_keys=True))
        return 0
    from engineering.design_engine.capabilities import build, render
    data = build()
    output = args.output or ROOT/'build/legacy-capabilities'
    files = {'ledger.json':json.dumps(data, indent=2, sort_keys=True)+'\n', 'directory.md':render(data),
        'README.md':'# Retained Capability Directory\n\nExplicit wheel/rail and shared-platform comparator inventory. Engineering acceptance does not transfer to maglev.\n\n[Entry points](directory.md) · [Ledger](ledger.json).\n'}
    for name, value in files.items():
        path = output/name
        if args.check:
            if not path.is_file() or path.read_text()!=value:
                raise ValueError('stale legacy capability directory: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value)
    print(json.dumps(data['inventory'], sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, FileNotFoundError) as exc:
        raise SystemExit('Capability directory held: '+str(exc))
