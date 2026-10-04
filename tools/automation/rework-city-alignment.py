#!/usr/bin/env python3
"""Create city-specific elevated-core concepts from controlled route geometry.

Immutable seeds preserve the actual catalogue line inventory, including rings
missing from older local caches. Baghdad retains its separately controlled plan.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'lib/templates/city-core-alignment.toml'
spec = importlib.util.spec_from_file_location('core_geometry', ROOT / 'tools/automation/rework-baghdad-alignment.py')
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)


def encoded(value):
    def precision(v):
        if isinstance(v, float): return round(v, 6)
        if isinstance(v, (list, tuple)): return [precision(x) for x in v]
        if isinstance(v, dict): return {k: precision(x) for k, x in v.items()}
        return v
    return (json.dumps(precision(value), indent=2, sort_keys=True) + '\n').encode()


def study_area(design, config):
    box = design['city']['bbox']; fraction = config['core_selection']['centred_bbox_fraction']
    if not 0 < fraction < 1: raise ValueError('Core fraction must be between zero and one')
    lat = design['city']['centroid_lat']; lon = design['city']['centroid_lon']
    half_lat = (box['north'] - box['south']) * fraction / 2
    half_lon = (box['east'] - box['west']) * fraction / 2
    lat = min(box['north'] - half_lat, max(box['south'] + half_lat, lat))
    lon = min(box['east'] - half_lon, max(box['west'] + half_lon, lon))
    return dict(south=lat-half_lat, north=lat+half_lat, west=lon-half_lon, east=lon+half_lon)


def seed_from_geometry(design, features, grid, cached):
    """Use tracked geometry, never let an old cache silently remove a line."""
    routes = {f['properties']['name']: f['geometry']['coordinates'] for f in features['features']
              if f['geometry']['type'] == 'LineString'}
    old = {r['name']: r for r in cached['lines']}
    result = {k: v for k, v in cached.items() if k != 'lines'}
    result.update(slug=design['city']['slug'], population=design['city']['population'],
                  grid_height=grid['height'], grid_width=grid['width'], grid_cell_m=grid['cell_m'], coordinate_basis='cell-centre-index-v1')
    result['lines'] = []
    for line in design['lines']:
        name = line['name']; cells = []
        for lon, lat, *_ in routes[name]:
            rc = [round((grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m'] - 0.5),
                  round((lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m'] - 0.5)]
            if not (0 <= rc[0] < grid['height'] and 0 <= rc[1] < grid['width']):
                raise ValueError(f'{name}: controlled geometry is outside its grid')
            if not cells or cells[-1] != rc: cells.append(rc)
        if len(cells) < 2: raise ValueError(f'{name}: empty controlled route')
        result['lines'].append(dict(name=name, shape=line['shape'].capitalize(), cells=cells,
                                   anchor_ids=old.get(name, {}).get('anchor_ids', [])))
    return result


def samples_for_controls(controls, spacing):
    samples = [controls[0]['start']]
    for c in controls:
        n = max(1, math.ceil(c['length_m']/spacing))
        if c['kind'] == 'tangent':
            a, b = c['start'], c['end']
            samples.extend((a[0]+(b[0]-a[0])*i/n, a[1]+(b[1]-a[1])*i/n) for i in range(1,n+1))
        else:
            x,y = c['center']; theta = math.atan2(c['start'][1]-y, c['start'][0]-x)
            samples.extend((x+c['radius_m']*math.cos(theta+c['turn']*c['angle_rad']*i/n),
                            y+c['radius_m']*math.sin(theta+c['turn']*c['angle_rad']*i/n)) for i in range(1,n+1))
        samples[-1] = c['end']
    return samples


def smooth_run(points, radial, config):
    g = config['geometry']; closed = points[0] == points[-1]
    tolerance = g['simplification_tolerance_m']
    while tolerance <= g['maximum_simplification_tolerance_m'] + 1e-6:
        waypoints = [points[0], points[-1]] if radial else geometry.simplify(points, tolerance)
        try:
            if closed:
                polygon = waypoints[:-1]
                if len(polygon) < 3: raise ValueError('Cannot collapse a closed ring')
                _, controls = geometry.fillet([polygon[-1], *polygon, polygon[0], polygon[1]],
                                              g['preferred_fillet_radius_m'], g['sample_spacing_m'])
                # A complete lap from the exit of the first rounded corner.
                controls = controls[2:-1]
                samples = samples_for_controls(controls, g['sample_spacing_m'])
                if geometry.distance(samples[0], samples[-1]) > 1e-5:
                    raise ValueError('Rounded ring is not closed')
            else:
                samples, controls = geometry.fillet(waypoints, g['preferred_fillet_radius_m'], g['sample_spacing_m'])
            if any(c.get('radius_m', math.inf) < g['minimum_analytical_radius_m'] for c in controls):
                raise ValueError('Fillet below normal product radius')
            return samples, controls, waypoints, tolerance
        except ValueError:
            if radial: break
            tolerance *= 1.5
    return None


def rework(seed, grid, config):
    cell=seed['grid_cell_m']; core=config['core']; result=deepcopy(seed); rows=[]
    def inside(rc):
        lat=grid['bbox_north']-(rc[0]+0.5)*cell/grid['m_per_deg_lat']
        lon=grid['bbox_west']+(rc[1]+0.5)*cell/grid['m_per_deg_lon']
        return core['south']<=lat<=core['north'] and core['west']<=lon<=core['east']
    for line in result['lines']:
        original=line['cells']; new=[]; runs=[]; i=0
        while i<len(original):
            if not inside(original[i]): new.append(original[i]); i+=1; continue
            end=i+1
            while end<len(original) and inside(original[end]): end+=1
            points=[(r*cell,c*cell) for r,c in original[i:end]]
            candidate=smooth_run(points,line['shape']=='Radial',config) if len(points)>=3 else None
            if candidate is None:
                new.extend(original[i:end]); controls=[]; waypoints=points; tolerance=None
                basis='retained-raster-requires-geometry-review'
            else:
                samples,controls,waypoints,tolerance=candidate
                for r,c in samples:
                    rc=[round(r/cell),round(c/cell)]
                    if not (0<=rc[0]<seed['grid_height'] and 0<=rc[1]<seed['grid_width']):
                        raise ValueError('Candidate outside grid')
                    if not new or new[-1]!=rc:new.append(rc)
                basis='analytical-tangents-and-circular-fillets'
            before=math.fsum(geometry.distance(a,b) for a,b in zip(points,points[1:]))
            runs.append(dict(seed_from_index=i,seed_to_index=end-1,geometry_basis=basis,controls=controls,
                control_points=waypoints,simplification_tolerance_m=tolerance,original_length_m=before,
                analytical_length_m=math.fsum(c['length_m'] for c in controls) if candidate else before))
            i=end
        # Outside fragments are retained exactly. Rings must stay closed.
        if original[0]==original[-1] and new[0]!=new[-1]:new.append(new[0])
        line['cells']=new
        rows.append(dict(line=line['name'],original_cells=len(original),reworked_cells=len(new),core_runs=runs,
            original_route_m=math.fsum(geometry.distance(a,b)*cell for a,b in zip(original,original[1:])),
            reworked_route_m=math.fsum(geometry.distance(a,b)*cell for a,b in zip(new,new[1:]))))
    report=dict(schema_version=2,status=config['release']['status'],core=core,core_selection=config['core_selection'],lines=rows,
        core_original_length_m=math.fsum(r['original_length_m'] for line in rows for r in line['core_runs']),
        core_analytical_length_m=math.fsum(r['analytical_length_m'] for line in rows for r in line['core_runs']),
        limitations=['The centroid-centred rectangle is an explicit planning study area, not a verified city-centre boundary.',
            'Elevation does not grant property/air rights or clear buildings, protected sites, terrain, utilities or obstacles.',
            'Water crossings remain bridges. Survey, vertical alignment, transitions, cant, structures and independent checking remain open.',
            'Unacceptable ring fillets retain raster geometry and special-product/realignment gates; they are never labelled straight tangents.',
            'Coverage, stations, fleet, energy, depots, staffing, cost and delivery evidence must be regenerated for the actual candidate.'])
    return result,report


def generate(design_path, check=False):
    city=design_path.parent; d=tomllib.loads(design_path.read_text()); slug=d['city']['slug']
    if slug=='baghdad':raise ValueError('Baghdad retains rework-baghdad-alignment.py and its controlled boundary')
    out=city/'engineering/alignment'; out.mkdir(parents=True,exist_ok=True)
    seed_path=out/'pre-rework-corridors.json.gz';grid_path=out/'planning-grid.json'
    if not seed_path.is_file() or not grid_path.is_file():
        if check:raise ValueError('Missing immutable alignment inputs: '+slug)
        grid=json.loads((ROOT/'.cache/osr-pipeline/rasters'/f'{slug}.grid.json').read_text())['grid']
        seed=seed_from_geometry(d,json.loads((city/f'{slug}.corridor.geojson').read_text()),grid,
                                json.loads((city/'corridors.json').read_text()))
        if seed_path.exists() or grid_path.exists():raise ValueError('Partial immutable seed; inspect before replacement')
        seed_path.write_bytes(gzip.compress(encoded(seed),mtime=0));grid_path.write_bytes(encoded(grid))
    seed=json.loads(gzip.decompress(seed_path.read_bytes()));grid=json.loads(grid_path.read_text())
    if seed.get('coordinate_basis') != 'cell-centre-index-v1':raise ValueError('Unversioned seed coordinate basis; migrate from original controlled geometry before regeneration')
    config=tomllib.loads(CONFIG.read_text());config['core']=study_area(d,config)
    # Subsequent design centroids can move with the new stations. The boundary
    # is fixed on first adoption and subsequently controlled by its policy.
    policy_path=city/'alignment-policy.toml'
    if policy_path.is_file():config['core']=tomllib.loads(policy_path.read_text())['core']
    config['core']={k:round(v,10) for k,v in config['core'].items()}
    routes,report=rework(seed,grid,config)
    report['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [Path(__file__),CONFIG,seed_path,grid_path,Path(geometry.__file__)]}
    policy='\n'.join(['# Controlled elevated-core concept; property and engineering approvals remain open.','[core]',
        *[f'{k} = {v:.10f}' for k,v in config['core'].items()],'[release]',f'status = "{config["release"]["status"]}"',''])
    report['sources_sha256'][policy_path.relative_to(ROOT).as_posix()]=hashlib.sha256(policy.encode()).hexdigest()
    outputs={city/'corridors.json':encoded(routes),out/'core-realignment.json':encoded(report),policy_path:policy.encode()}
    for path,raw in outputs.items():
        if check:
            if not path.is_file() or path.read_bytes()!=raw:raise ValueError('Stale alignment: '+str(path))
        else:path.write_bytes(raw)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--design',type=Path,required=True);p.add_argument('--check',action='store_true')
    a=p.parse_args();r=generate(a.design.resolve(),a.check)
    print(f"{a.design.parent.name}: core {r['core_original_length_m']/1000:.3f} → {r['core_analytical_length_m']/1000:.3f} km; elevated land / bridge water")
if __name__=='__main__':main()
