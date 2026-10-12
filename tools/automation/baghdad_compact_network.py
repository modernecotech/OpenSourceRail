"""Compact Baghdad corridor revision using retained nine-line inputs and spacing.

Population-circle gains guide bounded additions; no OD demand, walking access,
construction approval or operating acceptance is inferred.
"""
from copy import deepcopy
import gzip,hashlib,importlib.util,json,math
from pathlib import Path
import numpy as np
import residential_route_expansion as expansion
import baghdad_regional_network as regional
from mapping_evidence import load_population

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'design/network-planning/baghdad-compact-expansion.json'
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT=CITY/'engineering/alignment'


def run(check=False):
    spec=importlib.util.spec_from_file_location('compact_core_alignment',ROOT/'tools/automation/rework-baghdad-alignment.py')
    alignment=importlib.util.module_from_spec(spec);spec.loader.exec_module(alignment)
    seed=json.loads(gzip.decompress(alignment.SEED.read_bytes()));grid=json.loads(alignment.GRID.read_text())
    import tomllib
    core_policy=tomllib.loads(alignment.CONFIG.read_text());cfg=json.loads(CONFIG.read_text())
    receipt_path=OUT/'water-source-receipt.json';mask_path=OUT/'planning-water-mask.bin.gz';build_path=OUT/'planning-buildability-mask.bin.gz'
    raw=gzip.decompress(mask_path.read_bytes())
    if hashlib.sha256(raw).hexdigest()!=json.loads(receipt_path.read_text())['mask_sha256']:raise ValueError('Water evidence changed')
    mask=np.frombuffer(raw,dtype=np.uint8).reshape(grid['height'],grid['width'])
    buildable=np.frombuffer(gzip.decompress(build_path.read_bytes()),dtype=np.uint8).reshape(mask.shape).astype(bool)
    routing_cost,terrain_paths=expansion.terrain_cost(CITY,grid,check)
    routes,core=alignment.rework(seed,grid,core_policy,mask,buildable)
    original,archive=expansion.baseline(CITY/'design.toml',check)
    data,population_paths,reason=expansion.population_inputs(CITY,original)
    if data is None:raise ValueError('Compact network requires retained population evidence: '+reason)
    rings=[line for line in routes['lines'] if line['shape']=='Ring'];changes=[];reviews=[]
    for line in routes['lines']:
        if line['shape']!='Radial':continue
        before=list(map(tuple,line['cells']));protected=[expansion.lonlat_cell(s['lon'],s['lat'],grid) for s in original['stations'] if s['line']==line['name']]
        protected=[p for p in protected if p in set(before)]
        try:
            after=expansion.connect_nearby_rings(before,protected,rings,
                lambda a,b:expansion.route_between(a,b,mask,buildable,cfg,grid['cell_m'],routing_cost),grid['cell_m'],
                allow_proposed_terminal_crop=True,maximum_terminal_crop_m=cfg['maximum_proposed_terminal_route_crop_m'])
        except ValueError as error:
            after=before;reviews.append(dict(line=line['name'],reason=str(error),bounded_platform_complex_must_pass_native_validation=True,site_profile_structure_and_walking_access_accepted=False))
        if after!=before:
            line['cells']=[list(p) for p in after]
            changes.append(dict(line=line['name'],kind='continuous physical ring connection',original_station_cells_preserved=set(protected)<=set(after),profile_structure_and_site_release=False))
    mapping_path=ROOT/'design/network-planning/baghdad-mapping-sources.json'
    mapping_cfg=json.loads(mapping_path.read_text())
    population,receipt,mapping_inputs=load_population(CITY/'engineering/mapping',mapping_cfg['selected_population'])
    if receipt['bbox']!=original['city']['bbox']:raise ValueError('Wrong-bbox selected population')
    chosen=next(row for row in mapping_cfg['population'] if row['id']==mapping_cfg['selected_population'])
    if any(receipt.get(k)!=value for k,value in chosen.items()):raise ValueError('Selected population source or epoch differs from policy')
    if receipt.get('retainer_sha256')!=expansion.sha(ROOT/'tools/automation/mapping_evidence.py'):raise ValueError('Selected population requires crop reproduction')
    keep=population['valid']&(population['counts']>0)
    selected={k:population[k][keep].copy() for k in ('lat','lon','counts')}
    mapping_cfg['population_year']=receipt['year']
    revised,report=regional.plan(routes,original['stations'],grid,mask,buildable,selected,data,cfg,mapping_cfg,routing_cost)
    if not 9<len(revised['lines'])<=17:raise ValueError('Compact candidate does not meet the requested more-than-nine bounded line inventory')
    paths=[CONFIG,mapping_path,ROOT/'tools/automation/baghdad_regional_network.py',ROOT/'tools/automation/mapping_evidence.py',*mapping_inputs,Path(__file__),alignment.CONFIG,alignment.SEED,alignment.GRID,mask_path,receipt_path,build_path,archive,
           ROOT/'tools/automation/residential_route_expansion.py',ROOT/'tools/automation/rework-baghdad-alignment.py',expansion.BACKTRACK_VALIDATOR,ROOT/'tools/automation/city_access.py',ROOT/'docs/data/city-population-source-overrides.json',*population_paths,*terrain_paths]
    hashes={p.relative_to(ROOT).as_posix():expansion.sha(p) for p in paths}
    report.update(schema=cfg['schema'],as_of=cfg['as_of'],city='baghdad',status='compact-controlled-planning-layout',
        design_stage='Original trunk network plus bounded residential corridors; survey, structures, accessibility and operations remain open',
        base_line_junction_changes=changes,base_line_junction_reviews=reviews,physical_release=False,operating_release=False,
        population_is_current_census=False,accessible_walking_coverage_accepted=False,
        station_spacing_policy='Native defaults: 1.6 km core, 3 km urban, 7 km suburban/outer; genuine interchange exceptions',
        target_interpretation='Selected native population pixel union with northeast/west reserved investigation corridors; emitted station and pedestrian graph access evaluated separately',sources_sha256=hashes)
    old={r['line']:r for r in core['lines']};new=[]
    for line in revised['lines']:
        cells=line['cells'];length=math.fsum(math.dist(a,b)*grid['cell_m'] for a,b in zip(cells,cells[1:]))
        def inside(cell):
            lon,lat=expansion.cell_lonlat([cell],grid)[0];c=core_policy['core']
            return c['south']<=lat<=c['north'] and c['west']<=lon<=c['east']
        core_length=math.fsum(math.dist(a,b)*grid['cell_m'] for a,b in zip(cells,cells[1:]) if inside(a) and inside(b))
        row=deepcopy(old.get(line['name'],dict(line=line['name'],original_cells=0,original_route_m=0,core_runs=[],water_constraints=[],geometry_basis='bounded residential corridor; curve/profile/structural review open')))
        row.update(reworked_cells=len(cells),reworked_route_m=length,final_core_route_m=core_length)
        if any(r['line']==line['name'] for r in changes):
            for segment in row['core_runs']:
                segment['superseded_analytical_controls']=segment.get('controls',[]);segment['controls']=[];segment['geometry_basis']='continuous junction revision requires profile and structural review'
        new.append(row)
    core.update(lines=new,residential_line_expansion=report,core_final_route_length_m=sum(r['final_core_route_m'] for r in new),sources_sha256=hashes)
    def precision(value):
        if isinstance(value,float):return round(value,6)
        if isinstance(value,list):return [precision(v) for v in value]
        if isinstance(value,tuple):return [precision(v) for v in value]
        if isinstance(value,dict):return {k:precision(v) for k,v in value.items()}
        return value
    outputs={CITY/'corridors.json':(json.dumps(revised,indent=2)+'\n').encode(),OUT/'core-realignment.json':expansion.encoded(precision(core)),
             OUT/'residential-line-expansion.json':expansion.encoded(report),CITY/'alignment-policy.toml':alignment.CONFIG.read_bytes()}
    cap=CITY/'station-spacing-policy.toml'
    if check:
        if cap.exists():raise ValueError('Compact revision must restore native station spacing, with no expansion cap')
        for p,raw in outputs.items():
            if not p.exists() or p.read_bytes()!=raw:raise ValueError('Stale compact Baghdad output: '+str(p))
    else:
        if cap.exists():cap.unlink()
        for p,raw in outputs.items():p.write_bytes(raw)
    print(json.dumps(dict(lines=len(revised['lines']),added_lines=report['added_line_count'],route_km=sum(r['reworked_route_m'] for r in new)/1000,station_spacing='original native settings',physical_release=False)))
