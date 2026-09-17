#!/usr/bin/env python3
"""Generate/check safety-case inventory counts; never infer proof acceptance."""
import argparse
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
START = '<!-- safety-case-counts:start -->'
END = '<!-- safety-case-counts:end -->'


def render(root=ROOT):
    counts = {key: 0 for key in ('goal', 'strategy', 'solution')}
    for path in sorted((root / 'docs/safety-case/gsn').glob('*.toml')):
        case = tomllib.loads(path.read_text())
        for key in counts:
            counts[key] += len(case.get(key, []))
    return (f"{START}\nGenerated case inventory: **{counts['goal']} goals, "
            f"{counts['strategy']} strategies, {counts['solution']} solutions**. "
            "These counts describe traceability, not successful or accepted proofs.\n"
            f"{END}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name in ['docs/safety-case/README.md', 'docs/certification/evidence-register.md']:
        path = ROOT / name
        text = path.read_text()
        start, end = text.index(START), text.index(END) + len(END)
        updated = text[:start] + render() + text[end:]
        if args.check:
            if text != updated:
                raise SystemExit(f'Stale safety-case inventory: {name}')
        else:
            path.write_text(updated)
    print('Safety-case inventory: current')


if __name__ == '__main__':
    main()
