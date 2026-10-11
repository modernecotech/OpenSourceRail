"""Reproducible native population and OSM topology screens for city planning.

Count grids stay separate by source and epoch. A graph screen never establishes
station entrances, permissions, measured traffic or passenger demand.
"""
from __future__ import annotations
import gzip, hashlib, io, json, math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from city_access import EARTH_RADIUS_M, xyz


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def pack_arrays(**arrays):
    memory=io.BytesIO();np.savez(memory, **arrays)
    packed=bytearray(gzip.compress(memory.getvalue(),mtime=0));packed[9]=255
    return bytes(packed)


def load_population(directory, identity):
    directory=Path(directory);receipt_path=directory/f'{identity}-source.json'
    pixels=directory/f'{identity}-pixels.npz.gz';receipt=json.loads(receipt_path.read_text())
    if sha(pixels)!=receipt['retained_sha256']:
        raise ValueError('Population evidence hash mismatch: '+identity)
    with np.load(io.BytesIO(gzip.decompress(pixels.read_bytes())),allow_pickle=False) as data:
        arrays={k:data[k].copy() for k in ('lat','lon','counts','valid')}
    validate_population(arrays)
    return arrays,receipt,[pixels,receipt_path]


def validate_population(arrays):
    if len({np.asarray(a).shape for a in arrays.values()})!=1:
        raise ValueError('Population array dimensions differ')
    if not np.all(np.isfinite(arrays['lat'])&np.isfinite(arrays['lon'])):
        raise ValueError('Population coordinates invalid')
    valid=arrays['valid'];counts=arrays['counts']
    if np.any(valid&(~np.isfinite(counts)|(counts<0))):
        raise ValueError('Population counts invalid')


def retain_population(raster, spec, bbox, directory):
    """Retain source pixel centres and counts; never interpolate count values."""
    import rasterio
    from rasterio.windows import Window,from_bounds
    with rasterio.open(raster) as source:
        if source.crs.to_epsg()!=4326 or source.count!=1 or source.transform.b or source.transform.d:
            raise ValueError('Expected one-band north-up EPSG:4326 native count raster')
        requested=from_bounds(bbox['west'],bbox['south'],bbox['east'],bbox['north'],source.transform)
        col,row=math.floor(requested.col_off),math.floor(requested.row_off)
        window=Window(col,row,math.ceil(requested.col_off+requested.width)-col,math.ceil(requested.row_off+requested.height)-row)
        data=source.read(1,window=window,boundless=True,masked=True);transform=source.window_transform(window)
        yy,xx=np.indices(data.shape)
        lon=transform.c+(xx+.5)*transform.a;lat=transform.f+(yy+.5)*transform.e
        inside=(lon>=bbox['west'])&(lon<bbox['east'])&(lat>=bbox['south'])&(lat<bbox['north'])
        counts=np.asarray(data.filled(0),dtype=np.float32)[inside]
        valid=(~np.ma.getmaskarray(data))[inside]&np.isfinite(counts)&(counts>=0)
        counts[~valid]=0
        arrays=dict(lat=lat[inside],lon=lon[inside],counts=counts,valid=valid)
        validate_population(arrays)
        raw=pack_arrays(**arrays);path=Path(directory)/f"{spec['id']}-pixels.npz.gz";path.write_bytes(raw)
        receipt=dict(spec,retainer_sha256=sha(Path(__file__)),source_sha256=sha(raster),retained_sha256=sha(path),bbox=bbox,
                     source_resolution_degrees=[abs(transform.a),abs(transform.e)],units='persons per native pixel',
                     selection='Native pixel centres inside city bbox; no count resampling, scaling or dataset averaging',
                     nodata='Excluded explicitly; never filled with people')
        (Path(directory)/f"{spec['id']}-source.json").write_bytes(encoded(receipt))


def sector_members(population, sector):
    return (population['lat']>=sector['south'])&(population['lat']<sector['north'])&(population['lon']>=sector['west'])&(population['lon']<sector['east'])


def radial_distances(population, stations):
    if not stations:return np.full(len(population['lat']),np.inf)
    positions=sorted({(float(s['lat']),float(s['lon'])) for s in stations})
    coords=np.asarray(positions);distance,_=cKDTree(xyz(coords[:,0],coords[:,1])).query(xyz(population['lat'],population['lon']))
    return 2*EARTH_RADIUS_M*np.arcsin(np.minimum(1.,distance/2))


def coverage(population, stations, sectors, radius_m=1000):
    validate_population(population)
    distances=radial_distances(population,stations);counts=population['counts'];known=population['valid']
    rows=[]
    for sector in [dict(id='city',label='Whole retained city bbox'),*sectors]:
        region=known if sector['id']=='city' else known&sector_members(population,sector)
        total=math.fsum(map(float,counts[region]));served=math.fsum(map(float,counts[region&(distances<=radius_m+1e-7)]))
        rows.append(dict(sector=sector['id'],population=round(total,3),radial_covered_population=round(served,3),
                         radial_unserved_population=round(total-served,3),radial_fraction=round(served/total,8) if total else None))
    return dict(radius_m=radius_m,sectors=rows,valid_pixels=int(known.sum()),missing_pixels=int((~known).sum()),
                validated_walking_access=False,basis='Spherical native pixel-centre union; each resident counted at most once per sector')


WALK_ROADS={'residential','living_street','pedestrian','footway','path','steps','unclassified','service','tertiary','secondary','primary','tertiary_link','secondary_link','primary_link','track'}


def allows_walk(tags):
    if tags.get('highway') not in WALK_ROADS:return False
    # Explicit foot permission overrides general access, never the reverse.
    foot=tags.get('foot');access=foot if foot is not None else tags.get('access','yes')
    return access not in {'no','private','use_sidepath'} and tags.get('construction') is None


def extract_streets(pbf, bbox, directory, spec):
    """Keep actual OSM node topology; grade-separated crossings never join by XY."""
    import osmium
    nodes={};edges={};features=[];counts={};buildings=0
    def inside(lon,lat):return bbox['west']<=lon<bbox['east'] and bbox['south']<=lat<bbox['north']
    class Handler(osmium.SimpleHandler):
        def way(self,way):
            nonlocal buildings
            tags=dict(way.tags)
            if not any(k in tags for k in ('highway','building','amenity','shop','landuse')):return
            coords=[(n.ref,n.lon,n.lat) for n in way.nodes if n.location.valid()]
            if len(coords)<2 or not any(inside(lon,lat) for _,lon,lat in coords):return
            if 'building' in tags:buildings+=1
            highway=tags.get('highway')
            if not highway:return
            counts[highway]=counts.get(highway,0)+1
            if not allows_walk(tags):return
            for (a,alon,alat),(b,blon,blat) in zip(coords,coords[1:]):
                # Endpoint clipping exposes a boundary limitation. No paths outside bbox are credited.
                if a==b or not (inside(alon,alat) and inside(blon,blat)):continue
                distance=2*EARTH_RADIUS_M*math.asin(min(1.,float(np.linalg.norm(xyz([alat],[alon])[0]-xyz([blat],[blon])[0]))/2))
                if distance<=0:continue
                nodes[a]=(alat,alon);nodes[b]=(blat,blon);edges[tuple(sorted((a,b)))]=distance
            features.append(dict(type='Feature',id=way.id,properties=dict(highway=highway,name=tags.get('name'),bridge=tags.get('bridge'),tunnel=tags.get('tunnel'),layer=tags.get('layer'),foot=tags.get('foot'),access=tags.get('access')),
                                 geometry=dict(type='LineString',coordinates=[[lon,lat] for _,lon,lat in coords])))
    Handler().apply_file(str(pbf),locations=True,idx='flex_mem')
    ids=sorted(nodes);index={node:i for i,node in enumerate(ids)};coordinates=np.asarray([nodes[n] for n in ids],dtype=float).reshape(-1,2)
    ordered=sorted(edges.items());first=np.asarray([index[a] for (a,b),d in ordered],dtype=np.int64);second=np.asarray([index[b] for (a,b),d in ordered],dtype=np.int64)
    path=Path(directory)/'walking-graph.npz.gz';path.write_bytes(pack_arrays(node_ids=np.asarray(ids,dtype=np.int64),lat=coordinates[:,0],lon=coordinates[:,1],first=first,second=second,length_m=np.asarray([d for e,d in ordered])))
    geometry=Path(directory)/'walking-streets.geojson.gz';geometry.write_bytes(gzip.compress(encoded(dict(type='FeatureCollection',features=features)),mtime=0))
    receipt=dict(spec,extractor_sha256=sha(Path(__file__)),osmium_version=osmium.__version__ if hasattr(osmium,'__version__') else __import__('importlib.metadata').metadata.version('osmium'),bbox=bbox,source_sha256=sha(pbf),graph_sha256=sha(path),geometry_sha256=sha(geometry),
                 highway_way_counts=counts,building_way_count=buildings,node_count=len(ids),edge_count=len(edges),
                 traffic_counts_measured=False,construction_accepted=False,
                 limitations=['OSM completeness, sidewalks, gates, accessibility and station entrances unverified','Graph clipped to city bbox; paths outside boundary unavailable','Only shared OSM node IDs connect roads; geometric crossings alone never connect','OSM building inventory is incomplete; absence does not imply no residents'])
    (Path(directory)/'street-source.json').write_bytes(encoded(receipt))


def walking_screen(population, stations, graph, station_snap_m=150,pixel_snap_m=150,radius_m=1000):
    """Potential graph access with bounded snaps; no invented river shortcuts.

    Snaps themselves are unverified connections. Keep this visible, and never
    call results validated walksheds or use them to establish paid rail demand.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    lat,lon=graph['lat'],graph['lon'];points=xyz(lat,lon);n=len(lat)
    if n==0:return dict(status='no-walking-graph',validated_walking_access=False)
    first,second,length=(graph[k] for k in ('first','second','length_m'))
    # Duplicate edges would sum in scipy: reject them rather than change length.
    if len(set(zip(first.tolist(),second.tolist())))!=len(first):raise ValueError('Duplicate graph edges')
    matrix=coo_matrix((np.r_[length,length],(np.r_[first,second],np.r_[second,first])),shape=(n,n)).tocsr()
    positions=sorted({(float(s['lat']),float(s['lon'])) for s in stations})
    tree=cKDTree(points)
    if positions:
        coords=np.asarray(positions);chord,indices=tree.query(xyz(coords[:,0],coords[:,1]));snaps=2*EARTH_RADIUS_M*np.arcsin(np.minimum(1.,chord/2));accepted=snaps<=station_snap_m
    else:indices=np.array([],dtype=int);snaps=np.array([]);accepted=np.array([],dtype=bool)
    # A virtual source preserves each station's own snap cost (min graph
    # distance followed by a different station snap would be incorrect).
    start=indices[accepted];cost=snaps[accepted];unique={}
    for i,c in zip(start,cost):unique[int(i)]=min(float(c),unique.get(int(i),math.inf))
    super_source=n
    extended=coo_matrix((np.r_[matrix.data,list(unique.values())],(np.r_[matrix.tocoo().row,np.full(len(unique),super_source)],np.r_[matrix.tocoo().col,list(unique)])),shape=(n+1,n+1)).tocsr()
    distance=dijkstra(extended,directed=True,indices=super_source)[:n]
    chord,index=tree.query(xyz(population['lat'],population['lon']));snaps_to_graph=2*EARTH_RADIUS_M*np.arcsin(np.minimum(1.,chord/2))
    known=population['valid'];reachable=known&(snaps_to_graph<=pixel_snap_m)&(distance[index]+snaps_to_graph<=radius_m)
    covered=math.fsum(map(float,population['counts'][reachable]));total=math.fsum(map(float,population['counts'][known]))
    return dict(status='screen-only',radius_m=radius_m,potential_graph_covered_population=round(covered,3),
                fraction=round(covered/total,8) if total else None,unique_stations=len(positions),stations_with_bounded_snap=int(accepted.sum()),
                station_snap_limit_m=station_snap_m,pixel_snap_limit_m=pixel_snap_m,validated_walking_access=False,
                snap_connections_surveyed=False,traffic_or_passenger_demand_inferred=False)
