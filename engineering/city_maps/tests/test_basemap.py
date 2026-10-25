import gzip
import io
import json
import math

import pytest

from engineering.city_maps import basemap as b


class Response:
    def __init__(self,data,start=0,status=206,content_range=None):
        self.data=data;self.status=status;self.reads=0
        self.headers={'Content-Range':content_range or f'bytes {start}-{start+len(data)-1}/{b.ARCHIVE_SIZE}',
                      'Content-Length':str(len(data)),'ETag':'"fixed-build"'}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):self.reads+=1;return self.data[:n]


def test_exact_ranges_cached_and_offline(tmp_path):
    response=Response(b'abcdefgh')
    def opener(request,timeout):
        assert request.get_header('Range')=='bytes=0-7'
        assert request.get_header('Accept-encoding')=='identity'
        return response
    src=b.RangeSource(tmp_path,opener=opener)
    assert src(0,8)==b'abcdefgh' and src(0,8)==b'abcdefgh'
    assert response.reads==1 and src.network_bytes==8
    offline=b.RangeSource(tmp_path,offline=True)
    assert offline(0,8)==b'abcdefgh' and offline.requests==0
    path=next(tmp_path.rglob('*.bin'));path.write_bytes(b'corrupt!')
    with pytest.raises(b.BasemapError,match='cache'):offline(0,8)


@pytest.mark.parametrize('status,content_range',[(200,None),(206,'bytes 1-8/139134051681'),(206,'bytes 0-7/999')])
def test_wholesale_get_or_inexact_range_rejected_before_body(tmp_path,status,content_range):
    response=Response(b'abcdefgh',status=status,content_range=content_range)
    src=b.RangeSource(tmp_path,opener=lambda *a,**kw:response)
    with pytest.raises(b.BasemapError,match='HTTP206'):src(0,8)
    assert response.reads==0
    assert not list(tmp_path.rglob('*.bin'))


def test_truncated_response_and_missing_cache_are_errors(tmp_path):
    response=Response(b'abc');response.headers.update({'Content-Range':f'bytes 0-7/{b.ARCHIVE_SIZE}','Content-Length':'8'})
    with pytest.raises(b.BasemapError,match='truncated'):
        b.RangeSource(tmp_path,opener=lambda *a,**k:response)(0,8)
    with pytest.raises(b.BasemapError,match='absent'):
        b.RangeSource(tmp_path,offline=True)(0,8)


def test_tile_orientation_is_top_down_and_wgs84():
    assert b.tile_point(0,0,1,1,0,4096)==pytest.approx([0,85.0511287798066])
    assert b.tile_point(4096,4096,1,1,0,4096)==pytest.approx([180,0])
    north=b.tile_point(1000,1000,12,2968,1733,4096)
    south=b.tile_point(1000,3000,12,2968,1733,4096)
    assert north[1]>south[1] and -180<=north[0]<=180


def test_tile_count_and_geographic_bounds_budget():
    assert b.tiles_for_bounds([0,0,180,85.05112878],1)==[(1,1,0)]
    assert len(b.tiles_for_bounds([80.85,26.75,81.05,26.95],12))<=64
    for bbox,z in [([-180,-80,180,80],15),([170,-1,-170,1],4),([1,2,1,3],2),([0,0,1,90],3)]:
        with pytest.raises(b.BasemapError):b.tiles_for_bounds(bbox,z)
    with pytest.raises(b.BudgetExceeded):b.RangeSource('/tmp/basemap-test-unused',offline=True)(0,b.MAX_RANGE+1)


def test_real_mvt_decode_y_orientation():
    import mapbox_vector_tile
    raw=mapbox_vector_tile.encode({'name':'places','features':[{'geometry':{'type':'Point','coordinates':[256,512]},'properties':{'name':'North point'}}]},
        default_options={'y_coord_down':True,'extents':4096})
    decoded=mapbox_vector_tile.decode(raw,default_options={'y_coord_down':True,'geojson':True})
    assert decoded['places']['features'][0]['geometry']['coordinates']==[256,512]


def test_gzip_decompression_budget():
    with pytest.raises(b.BudgetExceeded):b._inflate(gzip.compress(b'a'*1000),100)


def test_invalid_bowtie_polygon_is_repaired_with_explicit_provenance():
    source=dict(type='Polygon',coordinates=[[[0,0],[2,2],[0,2],[2,0],[0,0]]])
    fixed,record=b._background_geometry(source,source,z=1,x=1,y=0,layer='landuse',feature_id=42)
    assert fixed.is_valid and not fixed.is_empty
    assert fixed.geom_type=='MultiPolygon' and fixed.area==pytest.approx(2.)
    assert record['original_geometry_sha256']==b.digest(b.encoded(source))
    assert record['feature_id']==42 and (record['z'],record['x'],record['y'])==(1,1,0)
    assert 'Self-intersection' in record['explain_validity']
    assert record['original_planar_area_deg2']==0
    assert record['result_planar_area_deg2']==pytest.approx(2.)
    assert record['relative_area_change'] is None
    assert record['result_geometry_type']=='MultiPolygon'
    assert record['scope']==b.REPAIR_SCOPE
    assert record['original_invalid_area_is_not_authoritative']


def test_valid_polygon_not_changed_and_invalid_nonpolygon_fails():
    polygon=dict(type='Polygon',coordinates=[[[0,0],[2,0],[2,2],[0,2],[0,0]]])
    fixed,record=b._background_geometry(polygon,polygon,z=1,x=1,y=0,layer='landuse',feature_id=None)
    assert fixed.area==pytest.approx(4.) and record is None
    invalid=dict(type='LineString',coordinates=[[1,1],[1,1]])
    with pytest.raises(b.BasemapError,match='nonpolygon'):
        b._background_geometry(invalid,invalid,z=1,x=1,y=0,layer='roads',feature_id=3)


def test_missing_pmtiles_entry_is_different_from_io_error(tmp_path):
    from pmtiles.writer import Writer
    from pmtiles.reader import Reader,MemorySource
    from pmtiles.tile import Compression,TileType,zxy_to_tileid
    stream=io.BytesIO();writer=Writer(stream)
    writer.write_tile(zxy_to_tileid(1,1,0),b'present')
    writer.finalize(dict(tile_type=TileType.MVT,tile_compression=Compression.NONE,min_zoom=1,max_zoom=1),{})
    reader=Reader(MemorySource(stream.getvalue()))
    assert reader.get(1,1,0)==b'present'
    assert reader.get(1,0,0) is None
    def broken(offset,length):raise OSError('source transport failed')
    with pytest.raises(OSError):Reader(broken).get(1,0,0)


def test_offline_context_digests_and_attribution(tmp_path):
    bbox=[0.,0.,1.,1.];tiles=b.tiles_for_bounds(bbox,0)
    packet=dict(schema=b.SCHEMA,bounds_wsen=bbox,zoom=0,
        source=dict(url=b.PINNED,header_sha256=b.HEADER_SHA256,metadata_sha256=b.METADATA_SHA256,archive_size_bytes=b.ARCHIVE_SIZE,whole_archive_checksum_verified=False),
        attribution=b.ATTRIBUTION,layers={'places':[dict(type='Feature',geometry=dict(type='Point',coordinates=[.5,.5]),properties={'name':'Fixture'})]},
        receipt=dict(extractor_sha256='b'*64,packages={'pmtiles':'3.8.1','mapbox-vector-tile':'2.2.0'},tiles=[dict(z=z,x=x,y=y,status='present',sha256='a'*64,bytes=8) for z,x,y in tiles],feature_counts={'places':1},retained_range_bytes=1307,
            ranges=[dict(url=b.PINNED,archive_size=b.ARCHIVE_SIZE,offset=o,length=n,http_status=206,
                         content_range=f'bytes {o}-{o+n-1}/{b.ARCHIVE_SIZE}',sha256=h)
                    for o,n,h in ((0,127,b.HEADER_SHA256),(138780946777,1180,b.METADATA_SHA256))]))
    packet['context_sha256']=b.digest(b.encoded(packet));path=tmp_path/'context.json.gz';path.write_bytes(gzip.compress(b.encoded(packet),mtime=0))
    assert b.load(path)['layers']['places'][0]['properties']['name']=='Fixture'
    packet['source']['whole_archive_checksum_verified']=True
    packet['context_sha256']=b.digest(b.encoded({k:v for k,v in packet.items() if k!='context_sha256'}))
    path.write_bytes(gzip.compress(b.encoded(packet)))
    with pytest.raises(b.BasemapError,match='whole-archive'):b.load(path)
    packet['source']['whole_archive_checksum_verified']=False
    packet['receipt']['ranges']=[]
    packet['context_sha256']=b.digest(b.encoded({k:v for k,v in packet.items() if k!='context_sha256'}))
    path.write_bytes(gzip.compress(b.encoded(packet)))
    with pytest.raises(b.BasemapError,match='range evidence'):b.load(path)
    packet['layers']['places'][0]['properties']['name']='Changed'
    path.write_bytes(gzip.compress(b.encoded(packet)))
    with pytest.raises(b.BasemapError,match='digest'):b.load(path)
