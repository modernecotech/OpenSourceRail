#!/usr/bin/env python3
"""Publish a city-order production requirement; shared national capital counted once."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]

def generate(path):
    d=tomllib.loads(path.read_text());slug=d['city']['slug'];city=path.parent
    manifest_path=city/f'operations/{slug}-operations-manifest.json'
    manifest=json.loads(manifest_path.read_text());payload=city/'operations'/manifest['file']
    if hashlib.sha256(payload.read_bytes()).hexdigest()!=manifest['compressed_sha256']:
        raise ValueError('Stale operations payload')
    b=json.loads(gzip.decompress(payload.read_bytes()));r=b['factory_sizing']
    for source in b['project_twin']['sources'].values():
        p=ROOT/source['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('Stale factory input: '+source['path'])
    profiles=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']
    families={line['rolling_stock'] for line in d['lines']}
    if families!={r['family']} or r['vehicle_modules']!=r['total_trainsets']*profiles[r['family']]['cars']:
        raise ValueError('Factory family/modules do not match the city order')
    rs=[t for t in b['manufacturing_tasks'] if t['asset_type']=='rolling-stock']
    finishes={line:max(t['planned_finish_day'] for t in rs if t['line']==line) for line in r['line_priority']}
    if finishes!=r['line_stock_finish_working_day']:raise ValueError('Factory delivery dates differ from CPM')
    r.update(schema='org.opensourcerail.city-factory.v1',capital_treatment='one national shared factory; independent city-order capacity screen, not simultaneous national commitments',
             sources_sha256={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest(),
                             manifest_path.relative_to(ROOT).as_posix():hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                             Path(__file__).relative_to(ROOT).as_posix():hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
             operations_payload_sha256=manifest['compressed_sha256'])
    r['sources_sha256'].update({s['path']:s['sha256'] for s in b['project_twin']['sources'].values()})
    out=city/'engineering/factory';out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    text=[f'# {city.name} city-order factory requirement','',
        f"**{r['total_trainsets']} {r['family']} trainsets / {r['vehicle_modules']} cars**. Facility readiness is **{r['readiness_months_from_ntp']} months from NTP**; fleet qualification and series manufacture follow it.",'',
        f"Planning output: {r['minimum_steady_output_trainsets_per_year']:.1f} trainsets/year, {r['test_tracks']} separate test paths, {r['direct_production_crew_fte']} direct production FTE. Plant reference envelope: **USD {r['plant_cost_envelope_usd']/1e6:.3f}m**.",'',
        'This is an independent city-order capacity requirement. Shared factory capital is counted once in the national brief. Concurrent cities, factory availability, national sequencing and suppliers remain uncommitted. Production wages/materials are within train prices, not repeated in the plant envelope. Reference cycles require measured family-specific qualification; smaller trains retain conservative reference cycles.', '',
        '| Line | Trainsets | Infrastructure working day | Fleet working day | Integrated working day |','|---|---:|---:|---:|---:|']
    for line in r['line_priority']:
        civil=r['infrastructure_deadlines'][line];stock=finishes[line]
        count=next(f['trainset_count'] for f in d['fleets'] if f['line']==line)
        text.append(f'| {line} | {count} | {civil} | {stock} | {max(civil,stock)} |')
    text.extend(['','All dates are conditional working days from NTP, not fare receipt dates or acceptance. Small-city civil work may finish before factory readiness; its integrated opening is delayed explicitly. National/pre-NTP finance, site release, recruitment, equipment delivery and type acceptance remain open.',''])
    (out/'README.md').write_text('\n'.join(text))
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--design',type=Path,required=True);a=p.parse_args();r=generate(a.design.resolve())
    print(f"{a.design.parent.name}: factory {r['total_trainsets']} trainsets, {r['readiness_months_from_ntp']} month readiness; national loading open")
if __name__=='__main__':main()
