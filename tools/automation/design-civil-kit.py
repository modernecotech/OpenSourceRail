#!/usr/bin/env python3
"""Reproduce three equal-scope civil manufacturing/erection research scenarios."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.continuous_design.civil_kit_evaluation import benchmark


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New directory; existing evidence is not overwritten')
    args=parser.parse_args();result=benchmark(args.output)
    print(json.dumps(dict(output=str(args.output.resolve()),
        alternatives=[dict(architecture=r['architecture'],study_pass=r['study_pass'],metrics=r['metrics']) for r in result['alternatives']],
        cheapest=result['cheapest'],scope=result['scope']),indent=2))


if __name__=='__main__':main()
