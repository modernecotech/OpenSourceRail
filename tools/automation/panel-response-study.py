#!/usr/bin/env python3
"""Generate or verify trimmed plate/attachment/rail research responses."""
from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.panel_response.study import generate,verify
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'engineering/panel_response/examples');p.add_argument('--check',action='store_true');a=p.parse_args()
if a.check:verify(a.output);print('Panel response sources, contracts and retained outputs are current')
else:generate(a.output)
