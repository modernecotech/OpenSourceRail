"""Bounded Protomaps PMTiles range cutouts; rendering never needs a network.

Acquisition uses the official PMTiles reader and MVT decoder. Stored per-city
gzip packets contain clipped WGS84 GeoJSON and source/tile/range receipts.
The whole139GB archive is never downloaded or claimed fully checksum-verified.
"""
from __future__ import annotations

import gzip
from hashlib import sha256
import importlib.metadata
import io
import json
import math
from pathlib import Path
import re
import urllib.request

PINNED = "https://build.protomaps.com/20261024.pmtiles"
ARCHIVE_SIZE = 139134051681
HEADER_SHA256 = "7d9a45aba294019889cb0b587f8c3feb2989c563ef63fee48f5acb297a6c2632"
METADATA_SHA256 = "f73df33b7437af448c5385817503bdaec0a3597a76347371fe1df86ef05d5b73"
SCHEMA = "osr-city-basemap-context/1"
LAYERS = frozenset(("earth", "water", "landcover", "landuse", "natural", "roads", "buildings", "places", "boundaries"))
ATTRIBUTION = [dict(name="OpenStreetMap contributors",url="https://www.openstreetmap.org/copyright",license="ODbL Produced Work"),
               dict(name="Natural Earth",url="https://www.naturalearthdata.com/about/terms-of-use/",license="Public domain"),
               dict(name="Protomaps",url="https://protomaps.com",license="Basemap compilation; source attribution retained")]
MAX_RANGE = 4*1024*1024
MAX_BYTES = 32*1024*1024
MAX_REQUESTS = 512
MAX_TILES = 64
MAX_FEATURES = 250000
MAX_COORDINATES = 2000000
MAX_RAW_PACKET = 96*1024*1024


class BasemapError(ValueError):pass
class BudgetExceeded(BasemapError):pass


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def digest(v):return sha256(v).hexdigest()


def _inflate(data, limit):
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        value=stream.read(limit+1)
    if len(value)>limit:raise BudgetExceeded("decompressed payload exceeds budget")
    return value


def tiles_for_bounds(bounds_wsen, zoom):
    if type(zoom) is not int or not 0<=zoom<=15:raise BasemapError("integer zoom0..15 required")
    if len(bounds_wsen)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in bounds_wsen):
        raise BasemapError("finite WGS84 west,south,east,north bounds required")
    w,s,e,n=map(float,bounds_wsen)
    if not -180<=w<e<=180 or not -85.05112878<=s<n<=85.05112878:
        raise BasemapError("non-antimeridian Web Mercator bounds required")
    count=2**zoom
    def index(v):return max(0,min(count-1,int(math.floor(v))))
    def fx(lon):return (lon+180)/360*count
    def fy(lat):return (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*count
    x0,x1=index(fx(w)),index(math.nextafter(fx(e),-math.inf))
    y0,y1=index(fy(n)),index(math.nextafter(fy(s),-math.inf))
    total=(x1-x0+1)*(y1-y0+1)
    if total>MAX_TILES:raise BudgetExceeded(f"viewport requests{total} tiles; limit{MAX_TILES}")
    return [(zoom,x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]


def tile_point(lon_x,top_down_y,z,x,y,extent):
    """MVT raw y grows down; convert via global Web Mercator tile coordinates."""
    if not extent>0:raise BasemapError("positive MVT extent required")
    scale=2**z
    lon=((x+lon_x/extent)/scale)*360-180
    lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+top_down_y/extent)/scale))))
    return [lon,lat]


class RangeSource:
    """Exact206 byte ranges and validated shared cache; no whole-file fallback."""
    def __init__(self,cache_dir,archive_url=PINNED,*,opener=None,offline=False):
        if archive_url!=PINNED:raise BasemapError("only the pinned immutable daily archive is admitted")
        self.url=archive_url;self.cache=Path(cache_dir)/digest(archive_url.encode());self.cache.mkdir(parents=True,exist_ok=True)
        self.opener=opener or urllib.request.urlopen;self.offline=offline
        self.requests=0;self.network_bytes=0;self.used={};self.total_bytes=0;self.etag=None

    def __call__(self,offset,length):
        if type(offset) is not int or type(length) is not int or offset<0 or not 0<length<=MAX_RANGE or offset+length>ARCHIVE_SIZE:
            raise BudgetExceeded("invalid or excessive archive byte range")
        key=f"{offset}-{length}";path=self.cache/(key+'.bin');receipt=self.cache/(key+'.json')
        if key in self.used:
            data=path.read_bytes()
            if len(data)!=length or digest(data)!=self.used[key]['sha256']:raise BasemapError("range cache changed during extraction")
            return data
        if len(self.used)>=MAX_REQUESTS or self.total_bytes+length>MAX_BYTES:raise BudgetExceeded("city range/request budget exceeded")
        if path.exists() or receipt.exists():
            if not path.is_file() or not receipt.is_file():raise BasemapError("incomplete range cache")
            data=path.read_bytes();record=json.loads(receipt.read_bytes())
            if record.get('url')!=self.url or record.get('offset')!=offset or record.get('length')!=length or record.get('sha256')!=digest(data) or len(data)!=length or record.get('archive_size')!=ARCHIVE_SIZE:
                raise BasemapError("range cache provenance/digest differs")
        else:
            if self.offline:raise BasemapError("required byte range absent from offline cache")
            if self.requests>=MAX_REQUESTS:raise BudgetExceeded("network request budget exceeded")
            request=urllib.request.Request(self.url,headers={'Range':f'bytes={offset}-{offset+length-1}',
                'Accept-Encoding':'identity','User-Agent':'OpenSourceRail-city-context/1'})
            with self.opener(request,timeout=30) as response:
                expected=f"bytes {offset}-{offset+length-1}/{ARCHIVE_SIZE}"
                if response.status!=206 or response.headers.get('Content-Range')!=expected:
                    raise BasemapError("server did not honour exact HTTP206/content-range; full GET refused")
                if response.headers.get('Content-Encoding','identity') not in ('identity',''):
                    raise BasemapError("range response content encoding differs")
                declared=response.headers.get('Content-Length')
                if declared is not None and declared!=str(length):raise BasemapError("range content-length differs")
                etag=response.headers.get('ETag')
                data=response.read(length+1)
                if len(data)!=length:raise BasemapError("truncated or oversized range response")
            self.requests+=1;self.network_bytes+=len(data)
            record=dict(url=self.url,offset=offset,length=length,archive_size=ARCHIVE_SIZE,
                        sha256=digest(data),etag=etag,http_status=206,content_range=expected)
            # Identical shared ranges may be written by two bounded workers.
            # Atomic replacement never exposes a partial cache payload.
            import os,tempfile
            for dest,raw in ((path,data),(receipt,encoded(record))):
                fd,name=tempfile.mkstemp(dir=self.cache,prefix='.range-')
                with os.fdopen(fd,'wb') as f:f.write(raw)
                Path(name).replace(dest)
        if record.get('http_status')!=206 or record.get('content_range')!=f"bytes {offset}-{offset+length-1}/{ARCHIVE_SIZE}":
            raise BasemapError("cached range lacks206 evidence")
        if self.etag and record.get('etag') and self.etag!=record['etag']:raise BasemapError("archive ETag changed between ranges")
        self.etag=self.etag or record.get('etag');self.used[key]=record;self.total_bytes+=length
        return data


def _coordinates(value,transform,counter):
    if isinstance(value,(list,tuple)) and len(value)>=2 and isinstance(value[0],(int,float)):
        counter[0]+=1
        if counter[0]>MAX_COORDINATES:raise BudgetExceeded("coordinate budget exceeded")
        return transform(value[0],value[1])
    return [_coordinates(item,transform,counter) for item in value]


def extract(bounds_wsen,zoom,output_gz,cache_dir,archive_url=PINNED,*,offline=False):
    """Acquire at most64 tiles; layers maps names to GeoJSON Feature lists.

    Missing PMTiles entries are retained as missing. HTTP, archive, decoding or
    budget errors propagate and never become an apparently empty city context.
    """
    from pmtiles.reader import Reader
    from pmtiles.tile import Compression,TileType
    import mapbox_vector_tile
    from shapely.geometry import shape,mapping,box
    tiles=tiles_for_bounds(bounds_wsen,zoom)
    source=RangeSource(cache_dir,archive_url,offline=offline);reader=Reader(source)
    raw_header=source(0,127)
    if digest(raw_header)!=HEADER_SHA256:raise BasemapError("pinned archive header differs")
    header=reader.header()
    if header['tile_type']!=TileType.MVT or not header['min_zoom']<=zoom<=header['max_zoom']:
        raise BasemapError("archive tile type or zoom differs")
    raw_meta=source(header['metadata_offset'],header['metadata_length'])
    if METADATA_SHA256 is None or digest(raw_meta)!=METADATA_SHA256:raise BasemapError("pinned archive metadata differs or is not pinned")
    meta=json.loads(_inflate(raw_meta,MAX_RANGE) if header['internal_compression']==Compression.GZIP else raw_meta)
    layers={};records=[];seen=set();counter=[0];clip=box(*bounds_wsen);feature_count=0
    for z,x,y in tiles:
        raw=reader.get(z,x,y)
        if raw is None:
            records.append(dict(z=z,x=x,y=y,status='missing',sha256=None,bytes=0));continue
        if len(raw)>MAX_RANGE:raise BudgetExceeded("tile size budget exceeded")
        records.append(dict(z=z,x=x,y=y,status='present',sha256=digest(raw),bytes=len(raw)))
        if header['tile_compression']==Compression.GZIP:payload=_inflate(raw,16*1024*1024)
        elif header['tile_compression']==Compression.NONE:payload=raw
        else:raise BasemapError("unsupported tile compression")
        decoded=mapbox_vector_tile.decode(payload,default_options={'y_coord_down':True,'geojson':True})
        for name,layer in decoded.items():
            if name not in LAYERS:continue
            extent=layer['extent'];transform=lambda a,b:tile_point(a,b,z,x,y,extent)
            for f in layer['features']:
                feature_count+=1
                if feature_count>MAX_FEATURES:raise BudgetExceeded("feature budget exceeded")
                geom=f['geometry']
                if geom['type']=='GeometryCollection':raise BasemapError("unexpected vector geometry collection")
                projected=dict(type=geom['type'],coordinates=_coordinates(geom['coordinates'],transform,counter))
                geographic=shape(projected)
                if not geographic.is_valid:raise BasemapError("invalid decoded source feature geometry")
                clipped=geographic.intersection(clip)
                if clipped.is_empty:continue
                # A polygon touching the viewport only at a point/edge is not
                # area context, and line fragments touching only at a point
                # must not become spurious point icons.
                if geographic.geom_type in ('Polygon','MultiPolygon') and clipped.area==0:continue
                if geographic.geom_type in ('LineString','MultiLineString') and clipped.length==0:continue
                feature=dict(type='Feature',geometry=mapping(clipped),properties=f.get('properties',{}))
                if 'id' in f:feature['id']=f['id']
                key=(name,digest(encoded(feature)))
                if key in seen:continue
                seen.add(key);layers.setdefault(name,[]).append(feature)
    packet=dict(schema=SCHEMA,bounds_wsen=list(map(float,bounds_wsen)),zoom=zoom,layers=layers,
        source=dict(provider='Protomaps daily basemap v4',url=archive_url,build='20261024',basemap_version=meta.get('version'),archive_size_bytes=ARCHIVE_SIZE,
                    header_sha256=HEADER_SHA256,metadata_sha256=METADATA_SHA256,
                    metadata=meta,whole_archive_checksum_verified=False),
        attribution=ATTRIBUTION,
        receipt=dict(tiles=records,ranges=sorted(source.used.values(),key=lambda r:r['offset']),
                     feature_counts={k:len(v) for k,v in sorted(layers.items())},
                     network_requests=source.requests,network_bytes=source.network_bytes,
                     retained_range_bytes=source.total_bytes,coordinates_decoded=counter[0],
                     packages={k:importlib.metadata.version(k) for k in ('pmtiles','mapbox-vector-tile')},
                     extraction_method='Exact206 range read; official PMTiles/MVT; clipped WGS84 GeoJSON',
                     extractor_sha256=digest(Path(__file__).read_bytes()),
                     no_hidden_renderer_network=True))
    packet['context_sha256']=digest(encoded(packet));raw=encoded(packet)
    if len(raw)>MAX_RAW_PACKET:raise BudgetExceeded("context packet size budget exceeded")
    output=Path(output_gz);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(gzip.compress(raw,mtime=0));return load(output)


def load(path):
    """Standard-library-only offline content/provenance/coordinate verifier."""
    path=Path(path)
    if path.stat().st_size>MAX_BYTES:raise BudgetExceeded("compressed context size budget exceeded")
    packet=json.loads(_inflate(path.read_bytes(),MAX_RAW_PACKET))
    if packet.get('schema')!=SCHEMA or packet.get('context_sha256')!=digest(encoded({k:v for k,v in packet.items() if k!='context_sha256'})):
        raise BasemapError("context content digest differs")
    tiles=tiles_for_bounds(packet['bounds_wsen'],packet['zoom'])
    src=packet['source']
    if src.get('url')!=PINNED or src.get('header_sha256')!=HEADER_SHA256 or src.get('metadata_sha256')!=METADATA_SHA256 or src.get('archive_size_bytes')!=ARCHIVE_SIZE:
        raise BasemapError("context archive pin differs")
    receipt=packet['receipt']
    if [(r['z'],r['x'],r['y']) for r in receipt['tiles']]!=tiles:raise BasemapError("context viewport tile inventory differs")
    if any(r['status'] not in ('present','missing') or (r['status']=='missing' and (r['sha256'] is not None or r['bytes']!=0)) for r in receipt['tiles']):
        raise BasemapError("tile disposition differs")
    for row in receipt['tiles']:
        if row['status']=='present' and (type(row['bytes']) is not int or not 0<row['bytes']<=MAX_RANGE or not re.fullmatch('[0-9a-f]{64}',row.get('sha256',''))):
            raise BasemapError("present tile digest/size invalid")
    if packet['layers'] and not any(r['status']=='present' for r in receipt['tiles']):
        raise BasemapError("features cannot originate from an entirely missing viewport")
    if sum(map(len,packet['layers'].values()))>MAX_FEATURES:raise BudgetExceeded("offline feature budget exceeded")
    if set(packet['layers'])-LAYERS or receipt['feature_counts']!={k:len(v) for k,v in packet['layers'].items()}:
        raise BasemapError("context layers/counts differ")
    if packet['attribution']!=ATTRIBUTION:raise BasemapError("required map attribution differs")
    w,s,e,n=packet['bounds_wsen'];count=[0]
    def check(x,y):
        if not math.isfinite(x) or not math.isfinite(y) or not w-1e-9<=x<=e+1e-9 or not s-1e-9<=y<=n+1e-9:
            raise BasemapError("feature coordinates outside WGS84 viewport")
        return [x,y]
    for features in packet['layers'].values():
        for f in features:
            if f.get('type')!='Feature':raise BasemapError("GeoJSON Feature required")
            geom=f['geometry']
            if geom['type']=='GeometryCollection':
                for child in geom['geometries']:_coordinates(child['coordinates'],check,count)
            else:_coordinates(geom['coordinates'],check,count)
    return packet


verify=load
