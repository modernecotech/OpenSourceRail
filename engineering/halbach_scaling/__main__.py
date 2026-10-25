"""Run bounded larger-array, gap, mass and finite-field research stages."""
import argparse
import json
from pathlib import Path
from . import ROOT
from . import screen,publication,operating,coupling,finite
from .common import write,source_snapshot


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('screen','compare','operating','finite','publish','verify'):
        parser=sub.add_parser(name);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,required=True)
        if name in ('compare','operating','finite','publish'):parser.add_argument('--transverse',type=Path,required=True)
        if name in ('finite','publish'):parser.add_argument('--operating',type=Path,required=True)
        if name=='compare':parser.add_argument('--operating',type=Path)
        if name=='finite':parser.add_argument('--getdp',type=Path,required=True)
        if name=='publish':
            parser.add_argument('--finite',type=Path,required=True);parser.add_argument('--quadrature',type=Path,required=True)
    args=p.parse_args();root=args.root;out=args.output
    if args.command=='screen':result=screen.run(out,root)
    elif args.command=='compare':
        value=publication.compare(args.transverse,root,operating_dir=args.operating);out.mkdir(parents=True,exist_ok=False);write(out/'comparison.json',value)
        result={'comparisons':len(value['comparisons']),'selection':value['selection']}
    elif args.command in ('operating','finite'):
        value=publication.compare(args.transverse,root,operating_dir=args.operating if args.command=='finite' else None);by_m={m['physical_id']:m for m in value['magnetic_candidates']}
        if args.command=='operating':
            raw=json.loads((args.transverse/'result.json').read_bytes())
            result=operating.run(out,root=root,bundles=[by_m[s['magnet_component_id']] for s in value['selection']['selected']],baseline_rows=raw['rows'])
        else:
            operating.verify(args.operating,root=root);op=json.loads((args.operating/'result.json').read_bytes())
            profiles=coupling.gap_profiles(op,value['selection'],value['comparisons'])
            plan=coupling.finite_plan(value['magnetic_candidates'],value['selection'],value['comparisons'],profiles)
            result=finite.run(out,root,args.getdp,[r['candidate'] for r in plan],gap_m=[r['gap_m'] for r in plan])
    elif args.command=='publish':result=publication.publish(out,transverse=args.transverse,operating_dir=args.operating,finite_dir=args.finite,quadrature_dir=args.quadrature,root=root)
    else:result=publication.verify_publication(out,root)
    print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False))


if __name__=='__main__':main()
