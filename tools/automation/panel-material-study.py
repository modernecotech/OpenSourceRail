#!/usr/bin/env python3
"""Reproduce matched side/roof cladding material hypotheses; no release."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from engineering.panel_materials.study import OUTPUT, publish

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = publish(args.output, check=args.check)
    print(f'{result["candidate_count"]} panel hypotheses; {result["conditional_pass_count"]} conditional screens; 0 engineering releases')
