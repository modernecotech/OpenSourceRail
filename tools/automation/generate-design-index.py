#!/usr/bin/env python3
"""Generate the historical v0.5 city catalogue in its pinned checkout."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
DESIGNS=REPO_ROOT/'cities/catalogue'
OUT=DESIGNS/'README.md'
FLAGS=('design_complete','physical_validation','manufacturing_release','physical_release')


def generate():
    rows=[]
    for source in sorted(DESIGNS.glob('*/*/*/city.json')):
        inputs=json.loads(source.read_text())
        if inputs.get('schema')!='osr-maglev-city-input/1':
            raise ValueError('unsupported city input: '+str(source))
        city=inputs['city']
        lines=inputs['lines']
        relative=source.parent.relative_to(DESIGNS).as_posix()
        package=source.parent/'engineering/maglev/summary.json'
        state='not generated'
        trains='—'
        if package.is_file():
            data=json.loads(package.read_text())
            if data.get('architecture')!='ferrite-pm-maglev-study' or any(data.get(flag) is not False for flag in FLAGS):
                raise ValueError('city package architecture/release differs: '+str(package))
            state='provisional; acceptance open'
            trains=str(data.get('totals',{}).get('trainsets','—'))
        route_km=sum(float(line['length_m']) for line in lines)/1000
        name=str(city.get('name',source.parent.name)).replace('|','\\|')
        rows.append(f'| [{name}]({relative}/README.md) | {len(lines)} | {route_km:.1f} | {trains} | [{state}]({relative}/engineering/maglev/README.md) |')
    return '\n'.join([
        '# Maglev city design catalogue','',
        f'{len(rows)} city inputs use the ferrite-PM maglev planning architecture. Each package reports formation, service, charging, manufacturing processes and provisional cost quantities.','',
        'Route geography and demand are planning inputs. Ground investigations, alignments, detailed engineering, supplier quotations and acceptance remain open. No complete programme cost or physical release is claimed.','',
        '[Current cost and process method](../../engineering/ferrite_maglev/README.md) · [City planning index](../../engineering/ferrite_maglev/city-index.md)','',
        '| City | Lines | Route km | Trainsets | Planning package |','|---|---:|---:|---:|---|',*rows,''])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    text=generate()
    if args.check:
        if not OUT.is_file() or OUT.read_text()!=text:
            raise SystemExit('stale city design catalogue')
    else:
        OUT.write_text(text)
    print(('current: ' if args.check else 'wrote ')+str(OUT.relative_to(REPO_ROOT)))


if __name__=='__main__':main()
