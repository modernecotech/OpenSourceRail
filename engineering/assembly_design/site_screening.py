"""Actual-source Baghdad GIS investigation screening, never soil qualification.

``analyse`` optionally uses Shapely/pyproj to derive retained estimates. Runtime
``snapshot`` and portable ``build`` use the standard library and frozen results.
OSM data is incomplete; no empty map cell implies vacant or suitable land.
"""
from collections import Counter
from datetime import datetime,timezone
from html import escape
import gzip
import json
import math
from pathlib import Path

from engineering.twin_workflow import core

DATA=Path(__file__).with_name('data')
REPORT=DATA/'baghdad-site-screening.json'
RAW=DATA/'baghdad-site-osm.json.gz'
GEOMETRY=DATA/'baghdad-site-geometry.geojson.gz'
CITY=core.ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
BBOX=[44.1,33.1,44.6,33.5]
QUERY='[out:json][timeout:45];(way["waterway"~"^(river|canal|drain)$"](33.1,44.1,33.5,44.6);way["natural"="water"](33.1,44.1,33.5,44.6);way["landuse"~"^(industrial|brownfield|construction|farmland|grass|meadow|railway|military|cemetery)$"](33.1,44.1,33.5,44.6);way["railway"~"^(rail|tram|light_rail)$"](33.1,44.1,33.5,44.6);way["power"~"^(line|minor_line|substation)$"](33.1,44.1,33.5,44.6););out meta geom;'


def _load(path):
    with gzip.open(path,'rt') if str(path).endswith('.gz') else Path(path).open() as stream:return json.load(stream)


def _path(path):return Path(path).relative_to(core.ROOT).as_posix()


def analyse():
    """Recompute bounded metric measurements from retained actual source data.

    Install Shapely and pyproj only for this extraction step. No network request
    or whole-country download is performed when reports/services are replayed.
    """
    try:
        from shapely.geometry import shape,Polygon,LineString,box,mapping,Point
        from shapely.ops import transform,unary_union
        from shapely.strtree import STRtree
        from pyproj import Transformer
    except ImportError as exc:raise RuntimeError('GIS recomputation requires Shapely and pyproj; frozen snapshot/build remain available') from exc
    forward=Transformer.from_crs(4326,32638,always_xy=True).transform
    backward=Transformer.from_crs(32638,4326,always_xy=True).transform
    clip=transform(forward,box(*BBOX));raw=_load(RAW)
    if raw.get('remark') or not raw.get('osm3s',{}).get('timestamp_osm_base') or not raw.get('elements'):
        raise ValueError('complete timestamped Overpass response required')
    paths=[RAW,CITY/'baghdad.corridor.geojson',CITY/'engineering/mapping/walking-streets.geojson.gz',
        CITY/'engineering/mapping/street-source.json',CITY/'engineering/clearance/building-footprints.json.gz',CITY/'engineering/clearance/building-source.json']
    features=[];skipped=[]
    def add(identifier,category,geometry,properties):
        if not geometry.is_valid:geometry=geometry.buffer(0) if geometry.geom_type=='Polygon' else geometry
        geometry=geometry.intersection(clip)
        if geometry.is_empty:return
        features.append(dict(id=str(identifier),category=category,geometry=geometry,properties=properties))
    for element in raw['elements']:
        tags=element.get('tags',{});points=[[p['lon'],p['lat']] for p in element.get('geometry',[]) if p and 'lat' in p and 'lon' in p]
        if len(points)<2:skipped.append(str(element['id']));continue
        closed=points[0]==points[-1] and len(points)>=4
        area=closed and (tags.get('natural')=='water' or 'landuse' in tags or tags.get('power')=='substation')
        geom=Polygon(points) if area else LineString(points)
        if tags.get('natural')=='water':category='water-area'
        elif tags.get('waterway'):category='waterway'
        elif tags.get('landuse'):category='landuse'
        elif tags.get('railway'):category='rail'
        elif tags.get('power'):category='power'
        else:continue
        add('osm-way-'+str(element['id']),category,transform(forward,geom),dict(tags=tags,version=element.get('version'),timestamp=element.get('timestamp'),source='fresh-osm'))
    routes=[]
    for feature in _load(paths[1])['features']:
        if feature['properties'].get('kind')!='line':continue
        geometry=transform(forward,shape(feature['geometry'])).intersection(clip)
        if not geometry.is_empty:routes.append(dict(id=feature['properties']['name'],geometry=geometry,properties=dict(feature['properties'],source='repository-proposed-alignment',status='concept; not surveyed or adopted')))
    if not routes:raise ValueError('existing proposed route geometry required')
    streets=_load(paths[2]);major={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link'}
    roads=[]
    for feature in streets['features']:
        if feature['properties'].get('highway') not in major:continue
        geom=transform(forward,shape(feature['geometry'])).intersection(clip)
        if not geom.is_empty:roads.append(dict(id='road-'+str(feature.get('id')),geometry=geom,properties=feature['properties']))
    waterareas=unary_union([f['geometry'] for f in features if f['category']=='water-area'])
    waterways=unary_union([f['geometry'] for f in features if f['category']=='waterway'])
    river=unary_union([f['geometry'] for f in features if f['category']=='waterway' and f['properties']['tags'].get('waterway')=='river'])
    allwater=unary_union([waterareas,waterways]);allroutes=unary_union([r['geometry'] for r in routes]);allroads=unary_union([r['geometry'] for r in roads])
    rails=unary_union([f['geometry'] for f in features if f['category']=='rail']);power=unary_union([f['geometry'] for f in features if f['category']=='power'])
    # Exact nearest mapped-feature distance at <=50m chainage subsegment
    # midpoints. A distance function is 1-Lipschitz, so half-subsegment length
    # supplies conservative chainage inclusion bounds without massive buffers.
    water_tree=STRtree([f['geometry'] for f in features if f['category'] in {'water-area','waterway'}])
    road_tree=STRtree([f['geometry'] for f in roads])
    def proximity(geometry,tree,radii):
        distances=[]
        lines=list(geometry.geoms) if hasattr(geometry,'geoms') else [geometry]
        for line in lines:
            if line.geom_type!='LineString' or not line.length:continue
            count=max(1,math.ceil(line.length/50.));step=line.length/count
            for i in range(count):
                point=line.interpolate((i+.5)*step);index=tree.nearest(point)
                distances.append((point.distance(tree.geometries[index]),step))
        return {str(radius):dict(estimate_m=round(sum(step for d,step in distances if d<=radius),2),
            lower_m=round(sum(step for d,step in distances if d+step/2<=radius),2),
            upper_m=round(sum(step for d,step in distances if d-step/2<=radius),2)) for radius in radii}
    forbidden=unary_union([f['geometry'] for f in features if f['category']=='landuse' and f['properties']['tags'].get('landuse') in ('military','cemetery')])
    buildings=[]
    for feature in _load(paths[4]):
        points=[[lon,lat] for lat,lon in feature['nodes']]
        if len(points)<4:continue
        polygon=Polygon(points)
        if not polygon.is_valid:polygon=polygon.buffer(0)
        geom=transform(forward,polygon).intersection(clip)
        if not geom.is_empty:buildings.append(dict(id='building-'+str(feature['id']),geometry=geom,properties=dict(source='retained-osm-near-existing-corridor',status='incomplete mapped inventory')))
    crossing_features=[]
    def intersections(geometry,other):
        result=geometry.intersection(other);points=[]
        def walk(g):
            if g.is_empty:return
            if g.geom_type=='Point':points.append(g)
            elif hasattr(g,'geoms'):
                for part in g.geoms:walk(part)
            # Linear overlaps are separately recorded, never counted as crossings.
        walk(result);unique=[]
        for point in points:
            if not any(point.distance(old)<30. for old in unique):unique.append(point)
        return unique
    route_rows=[]
    for route in routes:
        geom=route['geometry'];crossings=intersections(geom,river)
        water_proximity=proximity(geom,water_tree,(100,250,500,1000));road_proximity=proximity(geom,road_tree,(10,))
        for i,point in enumerate(crossings):crossing_features.append(dict(id=route['id']+'-river-crossing-'+str(i+1),category='river-crossing',geometry=point,
            properties=dict(route_id=route['id'],status='Geometric centreline intersection; surveyed banks, flood levels, navigation and crossing design unresolved')))
        conflicts=sum(f['geometry'].intersects(geom.buffer(10.)) for f in buildings)
        route_rows.append(dict(id=route['id'],length_m=round(geom.length,2),river_centreline_crossings=len(crossings),
            mapped_water_overlap_m=round(geom.intersection(waterareas).length,2),
            water_proximity_length_m={radius:row['estimate_m'] for radius,row in water_proximity.items()},
            water_proximity_chainage_bounds_m=water_proximity,
            within_10m_of_mapped_major_roads_m=road_proximity['10']['estimate_m'],road_proximity_chainage_bounds_m=road_proximity['10'],
            retained_building_footprints_within_10m=conflicts,
            investigation_quantity_scenarios=[dict(spacing_m=spacing,nominal_chainage_locations=math.ceil(geom.length/spacing)+1,
                basis='Proposed uniform desktop investigation quantities only; shared alignments/endpoints may duplicate locations; engineer must design risk-zoned programme') for spacing in (250,500)]))
    candidates=[]
    for feature in features:
        if feature['category']!='landuse' or feature['properties']['tags'].get('landuse') not in ('brownfield','construction','farmland'):continue
        geom=feature['geometry'];area=geom.area
        if area<20000 or geom.distance(allroutes)>2000 or geom.distance(allroads)>500 or geom.intersects(forbidden):continue
        if geom.distance(allwater)<100:continue
        point=geom.representative_point();lon,lat=backward(point.x,point.y)
        candidates.append(dict(id=feature['id'],landuse=feature['properties']['tags']['landuse'],area_m2=round(area,1),
            representative_lonlat=[round(lon,7),round(lat,7)],distance_to_proposed_route_m=round(geom.distance(allroutes),1),
            distance_to_mapped_major_road_m=round(geom.distance(allroads),1),distance_to_mapped_water_m=round(geom.distance(allwater),1),
            distance_to_mapped_rail_m=round(geom.distance(rails),1) if not rails.is_empty else None,
            distance_to_mapped_power_m=round(geom.distance(power),1) if not power.is_empty else None,
            land_availability=None,ownership=None,soil_bearing_capacity_pa=None,groundwater_depth_m=None,
            status='Mapped landuse investigation candidate; not available/suitable land or a selected factory parcel'))
    candidates=sorted(candidates,key=lambda r:(r['distance_to_proposed_route_m'], -r['area_m2']))[:12]
    landuse={}
    for kind in sorted({f['properties']['tags']['landuse'] for f in features if f['category']=='landuse'}):
        selected=[f['geometry'] for f in features if f['category']=='landuse' and f['properties']['tags']['landuse']==kind]
        landuse[kind]=round(unary_union(selected).area/1e6,4)
    # One bounded map preserves complete retrieved OSM features, simplified in
    # metric coordinates only for display. Numeric measurements use full detail.
    display=[]
    context_path=DATA/'site-context.geojson'
    if context_path.is_file():
        paths.append(context_path)
        for feature in _load(context_path)['features']:
            display.append(dict(type='Feature',id=feature['id'],geometry=feature['geometry'],properties=dict(category='population-context',
                modelled_persons=feature['properties']['worldpop_2026']['persons'],year=2026,source='WorldPop2026 native population cells',status='Modelled counts; not census or ridership')))
    for f in features+[{**r,'category':'proposed-route'} for r in routes]+crossing_features+[{**r,'category':'major-road'} for r in roads]+[{**r,'category':'building'} for r in buildings]:
        tolerance=10. if f['category'] in {'landuse','water-area'} else 5.
        geometry=transform(backward,f['geometry'].simplify(tolerance,preserve_topology=True))
        display.append(dict(type='Feature',id=f['id'],geometry=mapping(geometry),properties=dict(category=f['category'],**f['properties'])))
    report=dict(schema='osr-baghdad-site-screening/1',bbox_lonlat=BBOX,metric_crs='EPSG:32638',analysis_code_sha256=core.sha(Path(__file__)),
        retrieved_utc=datetime.now(timezone.utc).isoformat(),osm_snapshot_utc=raw['osm3s']['timestamp_osm_base'],query=QUERY,
        source_sha256={_path(p):core.sha(p) for p in paths},
        source_descriptions=dict(fresh_osm=dict(url='https://overpass-api.de/api/interpreter',documentation='https://wiki.openstreetmap.org/wiki/Overpass_API',
            parsed_response_features=len(raw['elements']),license='ODbL-1.0',attribution='© OpenStreetMap contributors',retention='Lossless gzip of parsed JSON response; original HTTP whitespace not retained'),
            proposed_routes=dict(path=_path(paths[1]),status='Existing repository concept alternatives; not operating, funded or surveyed routes'),
            roads=_load(paths[3]),buildings=_load(paths[5])),
        coverage=dict(requested_area_km2=round(clip.area/1e6,3),fresh_osm_bbox=BBOX,roads_bbox=[44.2,33.05,44.75,33.5],
            osm_water_geometry='Ways only; multipolygon relations not retrieved. Water polygon area is an incomplete mapped subset; main rivers also have centrelines. Use independent WorldCover for surface-class area; no mapped shoreline completeness or bank-distance guarantee',
            roads_missing_requested_western_strip=[44.1,33.1,44.2,33.5],building_scope='Only retained footprints intersecting original routes buffered 10m; omissions do not imply open ground',
            osm_completeness='Unknown; feature presence supports investigation, absence is not evidence of clearance'),
        source_feature_counts=dict(Counter(f['category'] for f in features)),skipped_missing_geometry_ids=skipped,
        estimates=dict(route_length_sum_m=round(sum(r['length_m'] for r in route_rows),2),route_union_length_m=round(allroutes.length,2),
            mapped_water_polygon_area_km2=round(waterareas.area/1e6,4),mapped_river_canal_drain_centreline_length_km=round(waterways.length/1000,3),
            mapped_landuse_area_km2=landuse,mapped_rail_length_km=round(rails.length/1000,3),mapped_power_geometry_length_km=round(power.length/1000,3)),
        routes=route_rows,landuse_investigation_candidates=candidates,geojson=dict(type='FeatureCollection',features=display),
        uncertainty=dict(map_position_m=None,measurement_scope='Metric calculations from mapped geometry; unknown source positional/completeness error dominates rounding',
            water_proxy='Distance to mapped water is an investigation priority proxy, not flood probability, groundwater level or depth-to-water estimate; <=50m midpoint subsegments retain conservative inclusion bounds using distance +/-half-step',
            open_land='Landuse polygons and satellite land classes do not establish vacancy, legal access, services or foundation suitability'),
        open_acceptance=['Cadastral ownership and permission','Topographic/utility and bank surveys','Hydrological flood levels and scour/navigation assessment',
            'Risk-zoned boreholes/CPT and groundwater monitoring','Laboratory strength/aggressivity, settlement and pile-group/site response','Road/rail/power capacity and permit confirmation'],
        site_investigation_complete=False,soil_parameters_adopted=False,**core.FLAGS)
    report['revision']=core.digest(report)
    return report


def freeze(report):
    """Retain bounded display geometry separately from the small numeric ledger."""
    report=dict(report);report.pop('revision',None)
    geometry=report.pop('geojson')
    GEOMETRY.write_bytes(gzip.compress(json.dumps(geometry,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
    report['geometry_path']=_path(GEOMETRY);report['source_sha256']=dict(report['source_sha256'],**{_path(GEOMETRY):core.sha(GEOMETRY)})
    report['revision']=core.digest(report);core.write(REPORT,report)
    return report


def source_paths():
    report=core.read(REPORT,maximum=2_000_000)
    if any(Path(name).is_absolute() or '..' in Path(name).parts for name in report['source_sha256']):raise ValueError('unsafe site source path')
    return sorted({_path(REPORT),*report['source_sha256']})


def verify(data_dir=DATA,*,root=core.ROOT):
    """Verify a portable source bundle without installing any GIS packages."""
    root=Path(root);report=core.read(Path(data_dir)/REPORT.name,maximum=2_000_000)
    if report.get('revision')!=core.digest({k:v for k,v in report.items() if k!='revision'}):raise ValueError('site report revision differs')
    if report['analysis_code_sha256']!=core.sha(Path(__file__)):raise ValueError('site analysis code changed; regenerate evidence')
    for name,digest in report['source_sha256'].items():
        path=root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or not path.is_file() or core.sha(path)!=digest:raise ValueError('site source changed or missing')
    if any(report.get(k) is not False for k in core.FLAGS) or report['site_investigation_complete'] or report['soil_parameters_adopted']:
        raise ValueError('desktop GIS cannot issue physical/site acceptance')
    return report


def snapshot():
    """Verify frozen raw evidence and expose estimates without GIS dependencies."""
    return verify()


def build(report,*,root=core.ROOT):
    """Portable map strings; display-only equirectangular projection and km scale."""
    west,south,east,north=report['bbox_lonlat'];width=1100;height=1040
    mid=(north+south)/2;sx=111320*math.cos(math.radians(mid));sy=111320.
    scale=min(980/((east-west)*sx),780/((north-south)*sy))
    def xy(point):return 60+(point[0]-west)*sx*scale,90+(north-point[1])*sy*scale
    styles={'population-context':('#eb9f50','none',0.),'landuse':('#e8ecd6','#d2d8be',.3),'major-road':('none','#aab1b7',.55),'water-area':('#a8d6f0','#4691bd',.5),
        'waterway':('none','#4691bd',.8),'rail':('none','#5d5550',.8),'power':('none','#b88dc1',.6),
        'building':('#9e9993','none',0.),'proposed-route':('none','#da492a',1.7),'river-crossing':('#ecaf1b','#674600',.5)}
    def paths(geometry):
        kind=geometry['type'];coordinates=geometry['coordinates']
        if kind=='Point':
            x,y=xy(coordinates);return [f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2"/>']
        if kind=='LineString':coordinates=[coordinates]
        elif kind=='MultiPolygon':coordinates=[ring for polygon in coordinates for ring in polygon]
        elif kind not in ('Polygon','MultiLineString'):return []
        result=[]
        for row in coordinates:
            values=[xy(p) for p in row];result.append('<path d="'+' '.join(('M' if i==0 else 'L')+f'{x:.2f},{y:.2f}' for i,(x,y) in enumerate(values))+(' Z' if kind in ('Polygon','MultiPolygon') else '')+'"/>')
        return result
    content=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#faf9f4"/>','<g font-family="sans-serif" fill="#17252c">',
        '<text x="45" y="32" font-size="21">Baghdad: actual mapped context and proposed OSR corridors</text>',
        f'<text x="45" y="57" font-size="13">OSM snapshot {escape(report["osm_snapshot_utc"])} · corridor alternatives require survey</text>']
    geojson=report.get('geojson') or _load(Path(root)/report['geometry_path']);features=geojson['features']
    population_max=max((f['properties'].get('modelled_persons',0.) for f in features),default=1.)
    for category,(fill,stroke,stroke_width) in styles.items():
        content.append(f'<g fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" fill-rule="evenodd">')
        for feature in features:
            if feature['properties']['category']==category:
                if category=='population-context':content.append(f'<g opacity="{.06+.55*math.sqrt(feature["properties"]["modelled_persons"]/max(1.,population_max)):.3f}">')
                content.extend(paths(feature['geometry']))
                if category=='population-context':content.append('</g>')
        content.append('</g>')
    for lon,lat,label in ((44.28,33.34,'Karkh / west bank'),(44.47,33.34,'Rusafa / east bank'),(44.385,33.30,'Tigris / Dijla')):
        x,y=xy([lon,lat]);content.append(f'<rect x="{x-3:.1f}" y="{y-15:.1f}" width="{len(label)*8.1:.1f}" height="21" fill="#faf9f4" opacity=".88"/><text x="{x:.1f}" y="{y:.1f}" font-size="15" fill="#17252c">{escape(label)}</text>')
    content += ['<text x="45" y="902" font-size="13">Orange: proposed routes · blue: mapped water · yellow dots: river centreline intersections</text>',
        '<text x="45" y="926" font-size="13">Orange shading: WorldPop2026 modelled population · grey: roads/buildings · purple: power · black: rail</text>',
        '<text x="45" y="950" font-size="12">OpenStreetMap contributors / ODbL. Western road coverage and building completeness are limited.</text>',
        '<text x="45" y="974" font-size="12">Water proximity guides investigations; it supplies no flood return period, groundwater depth or soil strength.</text>',
        f'<path d="M60,1000 h{5000*scale:.2f}" stroke="#17252c" stroke-width="3"/><text x="60" y="1023" font-size="13">5 km · display scale near 33.3°N</text>',
        '<text x="1010" y="92" font-size="18">N</text><path d="M1020,125 V100 l-5,9 m5,-9 l5,9" fill="none" stroke="#17252c" stroke-width="2"/></g></svg>']
    return dict(geojson=json.dumps(geojson,separators=(',',':'),ensure_ascii=False),svg='\n'.join(content))
