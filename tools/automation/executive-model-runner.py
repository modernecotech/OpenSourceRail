#!/usr/bin/env python3
"""Run one isolated AI executive identity against an OSR model-adapter endpoint."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.model_runner import run_once, validate_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--once', action='store_true', help='Process currently collecting proposals and exit')
    args = parser.parse_args()
    config = validate_config(json.loads(args.config.read_text()))
    while True:
        try:
            results = run_once(config)
            if results:
                print(json.dumps({'processed': results}, separators=(',', ':')), flush=True)
        except (OSError, ValueError, KeyError) as exc:
            # Never print proposal/context bodies or credentials.
            print(json.dumps({'error': type(exc).__name__, 'message': str(exc)[:300]}), flush=True)
            if args.once:
                raise SystemExit(1)
        if args.once:
            return
        time.sleep(config['poll_seconds'])


if __name__ == '__main__':
    main()
