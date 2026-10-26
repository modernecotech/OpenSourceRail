import argparse
import json
from pathlib import Path
from . import ROOT
from .publication import OUTPUT, publish, verify

def main():
    p=argparse.ArgumentParser(description='Seat-led comfort research with explicit capacity and qualification holds')
    p.add_argument('action',choices=('publish','verify'))
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output',type=Path,default=Path(OUTPUT))
    a=p.parse_args()
    print(json.dumps((publish if a.action=='publish' else verify)(a.output,a.root),indent=2))

if __name__=='__main__':main()
