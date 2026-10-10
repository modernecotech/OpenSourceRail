#!/usr/bin/env python3
"""FreeCADCmd entry point: native shared assembly and unissued drawing package."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.freecad_engineering_definition import build_document
from osr_mech.engineering_definition import load_definition


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=build_document(load_definition(a.model),a.output)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
