#!/usr/bin/env python3
"""Historical v0.5 capability directory; reproduce in its pinned checkout."""
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
    args = parser.parse_args()
    from engineering.ferrite_maglev import navigation
    data = navigation.publish(args.output or navigation.OUTPUT, check=args.check)
    print(json.dumps(data['inventory'], sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, FileNotFoundError) as exc:
        raise SystemExit('Capability directory held: '+str(exc))
