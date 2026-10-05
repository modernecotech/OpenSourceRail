#!/usr/bin/env python3
"""Independent catalogue audit of water placement and actual line intersections."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tomllib

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('geography_water_routes',ROOT/'tools/automation/water-route-constraints.py')
water=importlib.util.module_from_spec(spec);spec.loader.exec_module(water)
evidence_spec=importlib.util.spec_from_file_location('geography_water_evidence',ROOT/'tools/automation/refresh-city-water-evidence.py')
water_evidence=importlib.util.module_from_spec(evidence_spec);evidence_spec.loader.exec_module(water_evidence)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def check_design(design,features,grid,mask):
    def rc(lon,lat):
        values=((grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m']-.5,
                (lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m']-.5)
        # Recover exact controlled cell centres after the inverse geographic
        # transform. Sub-micrometre floating noise must not split a common
        # raster trunk into hundreds of artificial transverse intersections.
        return tuple(float(round(v)) if abs(v-round(v))<1e-6 else v for v in values)
    stations=[];wet=[];unknown=[]
    for station in design['stations']:
        row,col=rc(station['lon'],station['lat']);cell=(math.floor(row+.5),math.floor(col+.5))
        if not 0<=cell[0]<mask.shape[0] or not 0<=cell[1]<mask.shape[1]:
            unknown.append(station['id']);continue
        value=int(mask[cell]);stations.append((station,Point(row,col)))
        if value==255:unknown.append(station['id'])
        elif value>0:wet.append(station['id'])
    lines={f['properties']['name']:[rc(lon,lat) for lon,lat,*_ in f['geometry']['coordinates']]
           for f in features['features'] if f['geometry']['type']=='LineString'}
    long_runs=[];unknown_runs=[];crossings=[]
    for name,cells in lines.items():
        _,runs=water.water_runs(cells,mask,grid['cell_m'])
        for run in runs:
            if run['unknown']:unknown_runs.append(dict(line=name,water_run_m=round(run['length_m'],3)))
            elif run['length_m']>1000:long_runs.append(dict(line=name,water_run_m=round(run['length_m'],3)))
    names=sorted(lines)
    for i,first in enumerate(names):
        for second in names[i+1:]:
            intersection=LineString(lines[first]).intersection(LineString(lines[second]))
            def pieces(geometry):
                if geometry.geom_type in {'Point','LineString'}:return [geometry]
                return [part for child in getattr(geometry,'geoms',[]) for part in pieces(child)]
            parts=pieces(intersection)
            points=[part for part in parts if part.geom_type=='Point']
            shared=[part for part in parts if part.geom_type=='LineString' and not part.is_empty]
            if shared:
                merged=linemerge(shared)
                for run in pieces(merged):
                    if run.geom_type=='LineString' and not run.is_ring:
                        points.extend([Point(run.coords[0]),Point(run.coords[-1])])
            for point in points:
                if point.geom_type!='Point':continue
                # Match the native solver's nonnegative half-up cell choice,
                # including crossings halfway between diagonal cells.
                row,col=math.floor(point.x+.5),math.floor(point.y+.5)
                if mask[row,col]>0:continue  # no platforms on a projected bridge crossing
                candidates={line:[s for s,p in stations if s['line']==line and p.distance(point)*grid['cell_m']<=60.0001]
                            for line in [first,second]}
                grouped=any(a.get('junction_group') is not None and a.get('junction_group')==b.get('junction_group')
                            for a in candidates[first] for b in candidates[second])
                crossings.append(dict(lines=[first,second],cell=[round(point.x,6),round(point.y,6)],
                                      platforms_grouped_at_crossing=grouped))
    missing=[c for c in crossings if not c['platforms_grouped_at_crossing']]
    unsupported=[s['id'] for s,p in stations if s.get('mandatory_crossing') and not any(
        s['line'] in c['lines'] and p.distance(Point(*c['cell']))*grid['cell_m']<=60.0001
        for c in crossings)]
    return dict(passed=not(wet or unknown or long_runs or unknown_runs or missing or unsupported),
                platforms_checked=len(design['stations']),wet_platforms=wet,unknown_platforms=unknown,
                long_unapproved_water_runs=long_runs,unknown_route_runs=unknown_runs,
                dry_geometric_crossings=len(crossings),missing_crossing_platforms=missing,
                unsupported_mandatory_platforms=unsupported)


def audit(baseline_ref=None):
    commit=subprocess.check_output(['git','rev-parse',baseline_ref],cwd=ROOT,text=True).strip() if baseline_ref else None
    rows=[];missing_sources=[]
    for design_path in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        out=design_path.parent/'engineering/alignment'
        if not (out/'water-source-receipt.json').is_file():missing_sources.append(design_path.parent.name);continue
        water_evidence.refresh(design_path,check=True)
        current=tomllib.loads(design_path.read_text());slug=current['city']['slug']
        grid=json.loads((out/'planning-grid.json').read_text())
        mask_path=out/'planning-water-mask.bin.gz';raw_mask=gzip.decompress(mask_path.read_bytes())
        receipt=json.loads((out/'water-source-receipt.json').read_text())
        if sha(raw_mask)!=receipt['mask_sha256']:raise ValueError('Altered water source: '+slug)
        mask=np.frombuffer(raw_mask,dtype=np.uint8).reshape(grid['height'],grid['width'])
        corridor=design_path.parent/(slug+'.corridor.geojson')
        if commit:
            raw=subprocess.check_output(['git','show',commit+':'+design_path.relative_to(ROOT).as_posix()],cwd=ROOT)
            raw_corridor=subprocess.check_output(['git','show',commit+':'+corridor.relative_to(ROOT).as_posix()],cwd=ROOT)
        else:raw=design_path.read_bytes();raw_corridor=corridor.read_bytes()
        design=tomllib.loads(raw.decode());features=json.loads(raw_corridor)
        result=check_design(design,features,grid,mask)
        result.update(city=slug,design_sha256=sha(raw),corridor_sha256=sha(raw_corridor),water_mask_sha256=sha(raw_mask),
                      water_source_receipt_sha256=sha((out/'water-source-receipt.json').read_bytes()))
        rows.append(result)
    return dict(schema_version=1,baseline_commit=commit,cities_checked=len(rows),missing_independent_sources=missing_sources,
        passed=not missing_sources and all(r['passed'] for r in rows),
        cities_with_findings=sum(not r['passed'] for r in rows),wet_platform_count=sum(len(r['wet_platforms']) for r in rows),
        missing_crossing_platform_count=sum(len(r['missing_crossing_platforms']) for r in rows),
        long_unapproved_water_run_count=sum(len(r['long_unapproved_water_runs']) for r in rows),
        physical_release=False,operating_release=False,
        source_documentation='https://esa-worldcover.org/en/data-access',
        limitations=['Historical satellite classification is a planning check; survey, bank access and platform footprints remain open.',
                    'Projected dry crossings use platforms within 60 m at grid precision; transfer routes and levels require independent site release.',
                    'Short water runs are bridge candidates with separate structural/shoreline approvals, not released crossings.'],
        generator_sha256=sha(Path(__file__).read_bytes()),water_constraint_generator_sha256=sha(Path(water.__file__).read_bytes()),cities=rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--baseline-ref')
    parser.add_argument('--out',type=Path,default=ROOT/'engineering/assurance/catalogue-geography/summary.json')
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report=audit(args.baseline_ref);encoded=(json.dumps(report,sort_keys=True,indent=2)+'\n').encode()
    if args.check:
        if args.out.read_bytes()!=encoded:raise ValueError('Stale catalogue geographic audit')
    else:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(encoded)
    print({k:report[k] for k in ['cities_checked','cities_with_findings','wet_platform_count','missing_crossing_platform_count','long_unapproved_water_run_count']})
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
