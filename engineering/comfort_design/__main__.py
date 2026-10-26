import argparse
import json
from pathlib import Path
from . import ROOT
from .publication import OUTPUT,publish,verify

def main():
    p=argparse.ArgumentParser(description='Matched comfort vehicle and two-minute service design')
    p.add_argument('action',choices=('publish','verify'))
    p.add_argument('--output',type=Path,default=Path(OUTPUT));p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--vehicle-native',type=Path);p.add_argument('--service-native',type=Path)
    a=p.parse_args()
    if a.action=='publish':
        if a.vehicle_native is None or a.service_native is None:p.error('publish requires both executed native packages')
        value=publish(a.output,root=a.root,vehicle_native=a.vehicle_native,service_native=a.service_native)
    else:value=verify(a.output,root=a.root)
    print(json.dumps(value,indent=2))

if __name__=='__main__':main()
