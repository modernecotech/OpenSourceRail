from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest
from engineering.rustgis import adapter, api


def collection(geometry=None, **properties):
    return dict(type='FeatureCollection', features=[dict(type='Feature', id='original-string-id',
        geometry=geometry, properties=properties)])


def native_ready():
    try:adapter.executable();return True
    except ValueError:return False


def test_correspondence_preserves_source_and_nested_values():
    source = collection(dict(type='Point', coordinates=[44.4,33.3]), nested={'x':[1,None]}, empty=None)
    original = deepcopy(source);out = adapter.prepared(source)
    assert source == original and out['features'][0]['properties'][adapter.INDEX] == 0
    out['features'][0]['id'] = 1
    out['features'][0]['properties']['nested'] = '{"x":[1,null]}'
    assert adapter.check_roundtrip(source,out)['all_properties_checked']
    with pytest.raises(ValueError, match='Reserved'):
        adapter.prepared(out)


@pytest.mark.parametrize('change', ['coordinate','missing','null-location','nested','duplicate','new-attribute'])
def test_roundtrip_rejects_information_loss(change):
    source = collection(dict(type='Point',coordinates=[44.4,33.3]), nested={'a':1})
    out = adapter.prepared(source)
    if change=='coordinate':out['features'][0]['geometry']['coordinates'][0] += .0001
    elif change=='missing':out['features'].clear()
    elif change=='null-location':out['features'][0]['geometry'] = None
    elif change=='nested':out['features'][0]['properties']['nested'] = '{"a":2}'
    elif change=='duplicate':out['features'].append(deepcopy(out['features'][0]))
    else:out['features'][0]['properties']['extra'] = 'not-in-source'
    with pytest.raises(ValueError):adapter.check_roundtrip(source,out)


def test_water_lines_never_become_filled_polygons_and_holes_survive():
    rings = [[[0,0],[2,0],[2,2],[0,0]], [[.5,.5],[1,.5],[1,1],[.5,.5]]]
    line = collection(dict(type='LineString',coordinates=[[0,0],[1,0],[1,1]]))['features'][0]
    area = collection(dict(type='Polygon',coordinates=rings))['features'][0]
    groups = adapter.context_layers({'layers':{'water':[line,area]}})
    assert groups['context_water_lines']['features'][0]['geometry']['type']=='LineString'
    assert groups['context_water_areas']['features'][0]['geometry']['coordinates']==rings
    null = collection(None, location_status='unlocated')
    out = adapter.prepared(null)
    assert adapter.check_roundtrip(null,out)['unlocated']==1


def test_native_commands_are_offline_and_do_not_style_unknown_locations():
    data = {n:collection(None) for n in adapter.LAYERS}
    for name in ['routes','platforms','stations','interchanges']:
        data[name]=collection(dict(type='Point',coordinates=[44,33]), label='A')
    args=adapter.commands(data,{})
    assert '--no-plugins' in args
    assert 'map.basemap={"name":"blank"}' in args
    assert not any('https://' in a for a in args)
    assert not any('layer.visibility=' in a and 'unlocated_requirements' in a for a in args)
    data['interchanges']['features']=[]
    assert not any('layer.move=' in a and 'interchanges' in a for a in adapter.commands(data,{}))


def test_relative_paths_and_zip_preserve_exact_bytes(tmp_path):
    with pytest.raises(ValueError):adapter._local(tmp_path,'../escape')
    outside=tmp_path.parent/'outside.txt';outside.write_text('x')
    (tmp_path/'link').symlink_to(outside)
    with pytest.raises(ValueError):adapter._local(tmp_path,'link')
    raw=adapter.zip_bytes({'x.json':b'{"number":1.0000}\n','nested/source':b'raw'})
    assert raw==adapter.zip_bytes({'nested/source':b'raw','x.json':b'{"number":1.0000}\n'})
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:assert z.read('x.json')==b'{"number":1.0000}\n'


def test_gis_route_requires_matching_loopback_and_packet(monkeypatch):
    class Handler:
        path='/api/rustgis/baghdad/'+'a'*64+'.zip';command='GET';root=Path('.')
        def respond(self,*values):self.result=values
    h=Handler();monkeypatch.setattr(api,'_loopback',lambda *a,**k:False)
    assert api.handle_api(h) and h.result[0]==403
    monkeypatch.setattr(api,'_loopback',lambda *a,**k:True)
    h.path='/api/rustgis/../../secret';assert api.handle_api(h) and h.result[0]==404
    h.path='/api/rustgis/baghdad/'+'a'*64+'.zip'
    monkeypatch.setattr(adapter,'inputs',lambda *a:())
    monkeypatch.setattr(adapter,'city_input',lambda *a:({'packet_id':'b'*64},))
    assert api.handle_api(h) and h.result[0]==409
    h.command='POST';assert api.handle_api(h) and h.result[0]==405


@pytest.mark.parametrize('a,b',[(False,0),(True,1),({'approved':False},{'approved':0}),([True],[1])])
def test_boolean_attributes_are_not_numeric_aliases(a,b):
    assert not adapter._same_numbers(a,b)


@pytest.mark.parametrize('change', ['none','candidate','city','source-bytes','recalculated','request-key'])
def test_cache_cannot_reseal_mixed_candidate_or_source(tmp_path,change):
    # Deliberately synthetic cache contract, not native or physical evidence.
    from engineering.station_rail.common import identity, encoded
    from hashlib import sha256
    root=Path(__file__).resolve().parents[1]
    files={'sources/exact.geojson':b'original-source','demo.rgis':b'example'}
    source_hash=sha256(files['sources/exact.geojson']).hexdigest()
    expected=dict(packet_id='a'*64,city={'slug':'demo','name':'Demo'},identity={'candidate_id':'original'},
                  dossier_manifest_id='b'*64,input_sha256={'sources/exact.geojson':source_hash})
    sources=adapter.source_hashes(root);tool=adapter.lock_record()
    key=identity(dict(packet_id=expected['packet_id'],dossier=expected['dossier_manifest_id'],
        sources=sources,tool=tool,original_sha256=expected['input_sha256'],preview=False))
    folder=tmp_path/key;folder.mkdir()
    m=dict(schema=adapter.SCHEMA,**deepcopy(expected),source_sha256=sources,tool=tool,
        key=key,features=0,background_features=0,roundtrip={},railway_calculations_changed=False,
        selected_reference_changed=False,**adapter.FLAGS)
    if change=='candidate':m['identity']['candidate_id']='other'
    elif change=='city':m['city']['name']='Other'
    elif change=='source-bytes':files['sources/exact.geojson']=b'changed-but-resealed'
    elif change=='recalculated':m['railway_calculations_changed']=True
    elif change=='request-key':m['key']='c'*64
    m['files_sha256']={n:sha256(raw).hexdigest() for n,raw in files.items()}
    m['manifest_id']=identity(m);files['manifest.json']=encoded(m)
    raw=adapter.zip_bytes(files);(folder/'demo.zip').write_bytes(raw)
    (folder/'manifest.json').write_bytes(encoded(dict(manifest=m,archive_sha256=sha256(raw).hexdigest(),preview_sha256=None)))
    if change=='none':assert adapter.verify(folder,root=root,expected_inputs=expected)['verified']
    else:
        with pytest.raises(ValueError):adapter.verify(folder,root=root,expected_inputs=expected)


def test_cache_eviction_keeps_current_archive_and_failed_evidence(tmp_path,monkeypatch):
    from hashlib import sha256
    from engineering.station_rail.common import encoded
    monkeypatch.setattr(adapter,'cache_root',lambda:tmp_path)
    for name in ['old','active']:
        folder=tmp_path/name/'key';folder.mkdir(parents=True)
        raw=b'reproducible bytes'*10;(folder/(name+'.zip')).write_bytes(raw)
        (folder/'manifest.json').write_bytes(encoded(dict(schema=adapter.SCHEMA+'/cache',
            archive_sha256=sha256(raw).hexdigest(),manifest={'manifest_id':name})))
        (folder/'build.stderr').write_text('retained log')
    failure=tmp_path/'failed/key';failure.mkdir(parents=True);(failure/'input.geojson').write_bytes(b'failed-input')
    result=adapter.prune_cache(budget=1,keep=[tmp_path/'active/key'])
    assert result['evicted']==1
    assert not (tmp_path/'old/key/old.zip').exists()
    assert (tmp_path/'active/key/active.zip').exists()
    assert (tmp_path/'old/key/build.stderr').exists() and (failure/'input.geojson').exists()


@pytest.mark.skipif(not native_ready(),reason='Pinned native RustGIS not installed')
def test_actual_native_import_save_reopen_holes_and_null_table(tmp_path):
    (tmp_path/'layers').mkdir();(tmp_path/'roundtrip').mkdir()
    rings=[[[0,0],[2,0],[2,2],[0,2],[0,0]],[[.5,.5],[.5,1],[1,1],[1,.5],[.5,.5]]]
    data={'areas':collection(dict(type='Polygon',coordinates=rings), nested={'v':[2,3]}),
          'unknown':collection(None, site_count=None)}
    args=['run','--no-plugins']
    for name,value in data.items():
        (tmp_path/'layers'/str(name+'.geojson')).write_text(json.dumps(adapter.prepared(value)))
        args+=adapter._cmd('layer.addData',path='layers/'+name+'.geojson',name=name)
    adapter.native([*args,'--save','test.rgis'],tmp_path,'test-build')
    args=['run','--no-plugins','--project','test.rgis']
    args+=adapter._cmd('share.exportLayer',layer='areas',path='roundtrip/areas.geojson')
    args+=adapter._cmd('share.exportTable',table='unknown',path='roundtrip/unknown.geojson')
    adapter.native(args,tmp_path,'test-reopen')
    for name,value in data.items():
        assert adapter.check_roundtrip(value,json.loads((tmp_path/'roundtrip'/str(name+'.geojson')).read_bytes()))['features']==1
    # The business adapter reads metadata only and needs neither QGIS nor RustGIS running.
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('osr_integration',root/'services/integration/osr_integration/__init__.py',submodule_search_locations=[str(root/'services/integration/osr_integration')])
    import sys
    module=importlib.util.module_from_spec(spec);sys.modules['osr_integration']=module;spec.loader.exec_module(module)
    from osr_integration.engineering import artifact
    result=artifact(tmp_path,'test.rgis','rustgis','0.5.0')
    assert result['maps'][0]['layers'][0]['features']==1
    assert result['tables'][0]['name']=='unknown' and result['tables'][0]['rows']==1
