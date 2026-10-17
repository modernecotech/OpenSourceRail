#!/usr/bin/env python3
"""Build the compact unified configuration, candidate and acceptance review."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design.review_flow import write


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output", type=Path, default=ROOT / "docs/design-engine/campaign-review"
    )
    p.add_argument("--architecture", type=Path)
    args = p.parse_args()
    print(write(args.output, architecture=args.architecture))


if __name__ == "__main__":
    main()
