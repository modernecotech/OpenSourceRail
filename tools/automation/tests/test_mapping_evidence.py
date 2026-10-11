"""Native-count conservation, source integrity and real pedestrian topology."""
import gzip,io,json,sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from mapping_evidence import allows_walk,coverage,load_population,retain_population,walking_screen


def population(lat,lon,counts,valid=None):
    return dict(lat=np.asarray(lat,dtype=float),lon=np.asarray(lon,dtype=float),counts=np.asarray(counts,dtype=float),valid=np.asarray(valid if valid is not None else [True]*len(counts),dtype=bool))


def test_native_count_crop_and_tamper_rejection(tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    raster=tmp_path/'population.tif'
    with rasterio.open(raster,'w',driver='GTiff',height=2,width=3,count=1,dtype='float32',crs='EPSG:4326',transform=from_origin(0,2,1,1),nodata=-999) as dst:
        dst.write(np.array([[10,20,900],[30,-999,900]],dtype=np.float32),1)
    spec=dict(id='test-2026',year=2026,dataset='test count raster',url='https://example.org/population.tif')
    retain_population(raster,spec,dict(west=0,south=0,east=2,north=2),tmp_path)
    data,receipt,paths=load_population(tmp_path,'test-2026')
    assert data['counts'].sum()==60 and data['valid'].sum()==3
    assert receipt['year']==2026 and 'no count resampling' in receipt['selection']
    paths[0].write_bytes(paths[0].read_bytes()+b'changed')
    with pytest.raises(ValueError,match='hash mismatch'):load_population(tmp_path,'test-2026')


def test_sector_native_union_and_missing_pixels():
    data=population([0,0,0,0],[0,.001,.02,.001],[10,20,70,1000],[True,True,True,False])
    sector=dict(id='west',south=-1,north=1,west=-1,east=.002)
    report=coverage(data,[dict(lat=0,lon=0),dict(lat=0,lon=.001)],[sector],500)
    whole,west=report['sectors']
    assert whole['population']==100 and whole['radial_covered_population']==30
    assert west['population']==30 and west['radial_fraction']==1
    assert report['missing_pixels']==1 and not report['validated_walking_access']


def test_disconnected_nearby_streets_cannot_teleport():
    data=population([0,0],[.001,.005],[10,90])
    graph=dict(lat=np.array([0.,0.,0.,0.]),lon=np.array([0.,.001,.004,.005]),first=np.array([0,2]),second=np.array([1,3]),length_m=np.array([111.2,111.2]))
    result=walking_screen(data,[dict(lat=0,lon=0)],graph,station_snap_m=10,pixel_snap_m=10)
    assert result['potential_graph_covered_population']==10
    assert result['fraction']==.1 and not result['validated_walking_access']


def test_station_specific_snap_cost_in_shortest_path():
    # A station 111 m off node 0 cannot borrow node 2's zero snap cost.
    data=population([0],[.007],[10])
    graph=dict(lat=np.array([0.,0.,0.]),lon=np.array([0.,.007,.02]),first=np.array([0,1]),second=np.array([1,2]),length_m=np.array([950.,1445.]))
    result=walking_screen(data,[dict(lat=.001,lon=0),dict(lat=0,lon=.02)],graph,station_snap_m=150,pixel_snap_m=10)
    assert result['stations_with_bounded_snap']==2
    assert result['potential_graph_covered_population']==0
    assert walking_screen(data,[],graph)['potential_graph_covered_population']==0


def test_foot_access_precedence_and_unsupported_roads():
    assert not allows_walk(dict(highway='residential',access='private'))
    assert allows_walk(dict(highway='residential',access='private',foot='yes'))
    assert not allows_walk(dict(highway='residential',access='yes',foot='no'))
    assert not allows_walk(dict(highway='motorway'))
    assert not allows_walk(dict(highway='footway',construction='yes'))
