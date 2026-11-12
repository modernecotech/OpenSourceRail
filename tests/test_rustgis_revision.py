"""Synthetic format/identity controls; these fixtures are not city evidence."""
from copy import deepcopy
from pathlib import Path
import json

import pytest
from engineering.rustgis import adapter,revision
from engineering.outline import city_workflow
from engineering.station_rail.common import encoded
from engineering.development_baseline import planning


def native_value(value):
    if value is None:return 'Null'
    if type(value) is bool:return {'Bool':value}
    if type(value) is int:return {'Int':value}
    if type(value) is float:return {'Float':value}
    return {'Text':value if isinstance(value,str) else json.dumps(value,sort_keys=True)}


def native_geometry(g):
    if g is None:return None
    c=g['coordinates'];point=lambda p:dict(x=p[0],y=p[1])
    if g['type']=='Point':return {'Point':point(c)}
    if g['type']=='LineString':return {'Line':[[point(p) for p in c]]}
    if g['type']=='Polygon':return {'Polygon':[[[point(p) for p in ring] for ring in c]]}
    raise ValueError(g['type'])


def project(layers):
    values=[];tables=[]
    for name,features in layers.items():
        keys=sorted(set().union(*(set(f['properties']) for f in features)))
        dataset=dict(name=name,geometry_type='Unknown',fields=[dict(name=k,ty='Text') for k in keys],
            source='not-followed/'+name+'.geojson',features=[dict(id=i+1,geometry=native_geometry(f['geometry']),
                attrs=[native_value(f['properties'].get(k)) for k in keys]) for i,f in enumerate(features)])
        if all(f['geometry'] is None for f in features):tables.append(dataset)
        else:values.append(dict(name=name,dataset=dataset))
    return dict(format=1,maps=[dict(name='Map',projection='WebMercator',layers=values)],tables=tables,tasks=[])


@pytest.fixture
def scene():
    coords=[[0.,0.],[.01,0.],[.02,0.]];chain=planning._chainages(coords)
    refs={'candidate_id':'a'*64};seed=dict(seed_id='b'*64,reference_candidate_ids=refs)
    stops=[dict(id=x,lon=p[0],lat=p[1],chainage_m=c,dwell_s=35.) for x,p,c in zip(('a','b','c'),coords,chain)]
    base=dict(city='fixture',revision_sha256='c'*64,source_outline_evaluation_id='d'*64,
        outline_context={'seed':seed},lines=[dict(id='L',shape='radial',coordinates=coords,length_m=chain[-1],
            headway_s=200.,design_speed_cap_m_s=20.,stops=stops)])
    binding=dict(kind='published',city_slug='fixture',packet_id='e'*64,base_seed_id=seed['seed_id'],
        source_outline_evaluation_id=base['source_outline_evaluation_id'],reference_candidate_ids=refs)
    props=dict(line_id='L',packet_id=binding['packet_id'],service_evaluation_id='f'*64)
    route=dict(geometry=dict(type='LineString',coordinates=coords),properties=dict(props,**{
        adapter.INDEX:0,'shape':'radial','headway_s':200.,'design_speed_cap_m_s':20.}))
    stations=[dict(geometry=dict(type='Point',coordinates=[s['lon'],s['lat']]),
        properties=dict(props,**s,**{adapter.INDEX:i})) for i,s in enumerate(stops)]
    context=dict(geometry=None,properties={adapter.INDEX:0,'binding_json':encoded(binding).decode().strip(),
        'export_key':'1'*64,'data_crs':'EPSG:4326'})
    derived=dict(geometry=dict(type='Point',coordinates=coords[1]),properties={adapter.INDEX:0,'source_id':'marker'})
    p=project({'routes':[route],'stations':stations,'original_access_markers':[derived],revision.CONTEXT:[context]})
    return p,base,binding


def dataset(p,name):
    return next((l['dataset'] for m in p['maps'] for l in m['layers'] if l['name']==name),None) or next(d for d in p['tables'] if d['name']==name)


def set_value(p,name,row,key,value):
    d=dataset(p,name);index=next(i for i,f in enumerate(d['fields']) if f['name']==key)
    d['features'][row]['attrs'][index]=native_value(value)


def build(scene,p=None,**kwargs):
    original,base,binding=scene
    return revision.build_request(encoded(p or original),encoded(original),base,binding,
        actor='Fixture planner',reason='Explicit native geometry study',**kwargs)


def test_style_camera_field_order_and_local_ids_do_not_create_physical_revision(scene):
    p=deepcopy(scene[0]);p['maps'][0]['camera']={'center':{'x':1e6,'y':2e6}}
    d=dataset(p,'routes');d['features'][0]['id']=999
    d['fields'].reverse();d['features'][0]['attrs'].reverse()
    request,check=build(scene,p)
    assert check['no_op'] and not request['edit_bundle']['edits']
    assert request['base_seed_id']==scene[2]['base_seed_id'] and 'base_plan' not in request
    assert all(check[k] is False for k in revision.FLAGS)


def test_real_route_and_station_coordinates_become_explicit_canonical_edits(scene):
    p=deepcopy(scene[0]);d=dataset(p,'routes');d['features'][0]['geometry']={'Line':[[dict(x=0.,y=0.),dict(x=.01,y=.005),dict(x=.02,y=0.)]]}
    dataset(p,'stations')['features'][1]['geometry']={'Point':dict(x=.01,y=.005)}
    request,check=build(scene,p);edit=request['edit_bundle']['edits'][0]
    assert check['changed_lines']==['L'] and edit['coordinates']==[[0.,0.],[.01,.005],[.02,0.]]
    assert edit['stops'][1]['chainage_m']==pytest.approx(planning._distance([0.,0.],[.01,.005]))
    assert edit['shape']=='radial' and edit['design_speed_cap_m_s']==20.
    assert request['edit_bundle']['seed_id']==scene[2]['base_seed_id']


def test_station_retire_add_and_dwell_remain_typed_geometry_edits(scene):
    p=deepcopy(scene[0]);d=dataset(p,'stations');old=d['features'].pop(1);old['id']=90
    d['features'].append(old)
    set_value(p,'stations',2,adapter.INDEX,None);set_value(p,'stations',2,'id','new-platform')
    set_value(p,'stations',2,'service_evaluation_id',None);set_value(p,'stations',2,'dwell_s',42.)
    request,_=build(scene,p);stops=request['edit_bundle']['edits'][0]['stops']
    assert [s['id'] for s in stops]==['a','new-platform','c'] and stops[1]['dwell_s']==42.


def test_native_service_edit_preserves_each_explicit_station_dwell(scene):
    p=deepcopy(scene[0]);set_value(p,'routes',0,'headway_s',150.);set_value(p,'routes',0,'design_speed_cap_m_s',15.)
    set_value(p,'stations',1,'dwell_s',50.)
    request,_=build(scene,p);first,last=request['edit_bundle']['edits']
    assert first==dict(kind='set-service',line='L',headway_s=150.,dwell_s=35.)
    assert last['design_speed_cap_m_s']==15. and last['stops'][1]['dwell_s']==50.


def test_service_only_numeric_geometry_noop_cannot_add_whole_line_civil_risk(scene):
    p=deepcopy(scene[0]);set_value(p,'routes',0,'headway_s',180.)
    dataset(p,'routes')['features'][0]['geometry']['Line'][0][0]['x']+=5e-13
    dataset(p,'stations')['features'][1]['geometry']['Point']['x']+=5e-13
    set_value(p,'stations',1,'lon',.01+5e-13)
    request,check=build(scene,p);edits=request['edit_bundle']['edits'];old=scene[1]['lines'][0]
    assert edits[0]['kind']=='set-service' and edits[0]['headway_s']==180.
    replacement=edits[1]
    assert replacement['coordinates']==old['coordinates']
    assert [s['chainage_m'] for s in replacement['stops']]==[s['chainage_m'] for s in old['stops']]
    # This is the exact predicate used by planning_adapter.apply_edits to count
    # changed_route_m / ROW and crossing risk. A translated service edit has0.
    changed_route_m=old['length_m'] if (replacement['coordinates']!=old['coordinates'] or replacement['shape']!=old['shape']) else 0.
    assert changed_route_m==0. and check['changed_lines']==['L']


def test_real_geometry_edit_still_triggers_exact_civil_reassessment(scene):
    p=deepcopy(scene[0]);set_value(p,'routes',0,'headway_s',180.)
    dataset(p,'routes')['features'][0]['geometry']['Line'][0][0]['x']+=2e-12
    request,_=build(scene,p)
    replacement=request['edit_bundle']['edits'][1]
    assert replacement['coordinates']!=scene[1]['lines'][0]['coordinates']


def test_native_upload_cannot_bypass_existing_city_job_request_budget(scene,monkeypatch):
    from engineering.outline import city_jobs
    monkeypatch.setattr(city_jobs,'MAX_REQUEST',1)
    with pytest.raises(ValueError,match='bounded city request'):
        build(scene)


@pytest.mark.parametrize('fault',['off-route','duplicate-index','changed-id','derived-layer','source-context','price','wrong-crs','map-metres','bad-ring','bad-attribute','coordinate-proxy','missing-layer'])
def test_native_edits_cannot_silently_cross_source_units_or_evidence_boundaries(scene,fault):
    p=deepcopy(scene[0]);kwargs={}
    if fault=='off-route':dataset(p,'stations')['features'][1]['geometry']['Point']['y']=.001
    elif fault=='duplicate-index':set_value(p,'stations',1,adapter.INDEX,0)
    elif fault=='changed-id':set_value(p,'stations',1,'id','forged')
    elif fault=='derived-layer':dataset(p,'original_access_markers')['features'][0]['geometry']['Point']['x']=.015
    elif fault=='source-context':set_value(p,revision.CONTEXT,0,'binding_json','{}')
    elif fault=='price':dataset(p,'routes')['fields'][0]['name']='price'
    elif fault=='wrong-crs':kwargs['data_crs']='EPSG:3857'
    elif fault=='map-metres':dataset(p,'stations')['features'][0]['geometry']['Point']['x']=1e6
    elif fault=='bad-ring':set_value(p,'routes',0,'shape','ring')
    elif fault=='bad-attribute':set_value(p,'routes',0,'service_evaluation_id','0'*64)
    elif fault=='coordinate-proxy':set_value(p,'stations',1,'chainage_m',123.)
    else:p['maps'][0]['layers'].pop(0)
    with pytest.raises((ValueError,planning.PlanningError)):build(scene,p,**kwargs)


def test_duplicate_json_nonfinite_bool_and_size_are_refused(scene,monkeypatch):
    with pytest.raises(ValueError,match='Duplicate'):revision.read_json(b'{"format":1,"format":1}')
    with pytest.raises(ValueError,match='Finite'):revision.read_json(b'{"x":NaN}')
    p=deepcopy(scene[0]);dataset(p,'stations')['features'][0]['geometry']['Point']['x']=True
    with pytest.raises(ValueError,match='Finite'):build(scene,p)
    monkeypatch.setattr(revision,'MAX_PROJECT',10)
    with pytest.raises(ValueError,match='Bounded'):revision.read_json(encoded(scene[0]))


def test_seed_base_is_small_and_mutually_exclusive(scene):
    request,_=build(scene);request['base_study_id']='1'*32
    with pytest.raises(ValueError,match='one planning base'):city_workflow.normalize(request)
    request.pop('base_study_id');request['base_seed_id']='not-an-id'
    with pytest.raises(ValueError,match='seed'):city_workflow.normalize(request)


def test_empty_native_table_remains_empty_without_inventing_a_row(scene):
    p=deepcopy(scene[0]);p['tables'].append(dict(name='empty-derived',fields=[],features=[],geometry_type='Unknown'))
    decoded=revision.decode(encoded(p),data_crs='EPSG:4326')
    assert decoded['empty-derived']['features']==[]


def test_ring_origin_chainage_is_not_false_ambiguity_but_crossing_is():
    ring=[[0.,0.],[.01,0.],[.01,.01],[0.,0.]]
    assert revision.chainage([0.,0.],ring,'ring')==0
    with pytest.raises(ValueError,match='Ambiguous'):
        revision.chainage([.005,.005],[[0.,0.],[.01,.01],[0.,.01],[.01,0.]],'radial')


def test_import_retains_exact_raw_and_reproduces_typed_request(scene,tmp_path,monkeypatch):
    p,base,binding=scene;source=Path(__file__).resolve().parents[1]
    for name in ['engineering/rustgis/revision.py','engineering/rustgis/adapter.py','engineering/outline/city_workflow.py']:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((source/name).read_bytes())
    monkeypatch.setattr(revision,'authoritative',lambda *a,**k:(base,binding,encoded(p),{'manifest_id':'2'*64}))
    result=revision.import_project(encoded(p),'fixture',binding['packet_id'],actor='Planner',reason='Native style control',data_crs='EPSG:4326',root=tmp_path,store=tmp_path.parent/(tmp_path.name+'-imports'))
    folder=revision.import_directory(result['import_id'],root=tmp_path,store=tmp_path.parent/(tmp_path.name+'-imports'))
    assert (folder/'project.rgis').read_bytes()==encoded(p) and result['job'] is None
    assert not (tmp_path/'build').exists()
    assert revision.verify_import(folder,root=tmp_path)['verified']
    (folder/'project.rgis').write_bytes(b'{}')
    with pytest.raises(ValueError,match='inventory'):revision.verify_import(folder,root=tmp_path)


def test_failed_import_input_is_retained_with_identity(scene,tmp_path,monkeypatch):
    p,base,binding=scene
    monkeypatch.setattr(revision,'authoritative',lambda *a,**k:(base,binding,encoded(p),{'manifest_id':'2'*64}))
    with pytest.raises(revision.RetainedImportError) as error:
        revision.import_project(b'{"format":1,"maps":[]}', 'fixture',binding['packet_id'],actor='Planner',reason='Fail control',data_crs='EPSG:4326',root=tmp_path,store=tmp_path.parent/(tmp_path.name+'-imports'))
    folder=revision.import_directory(error.value.import_id,root=tmp_path,store=tmp_path.parent/(tmp_path.name+'-imports'))
    assert (folder/'failure.json').is_file() and (folder/'project.rgis').read_bytes()==b'{"format":1,"maps":[]}'



def test_import_api_requires_post_origin_typed_metadata_and_bounded_file(scene,tmp_path,monkeypatch):
    from io import BytesIO
    from types import SimpleNamespace
    from urllib.parse import urlencode
    from engineering.rustgis import api
    raw=encoded(scene[0])
    class Handler:
        root=tmp_path;command='POST'
        server=SimpleNamespace(city_studies=object())
        headers={'Content-Type':'application/json','Content-Length':str(len(raw))}
        rfile=BytesIO(raw)
        path='/api/rustgis/import/fixture/'+'e'*64+'?'+urlencode(dict(actor='Planner',reason='Native edit',data_crs='EPSG:4326'))
        def respond(self,*args):self.response=args
    h=Handler();seen=[]
    monkeypatch.setattr(api,'_loopback',lambda *a,**k:seen.append(k['post']) or False)
    assert api.handle_api(h) and h.response[0]==403 and seen==[True]
    monkeypatch.setattr(api,'_loopback',lambda *a,**k:True)
    def accept(body,*args,**kwargs):
        assert body==raw and kwargs['service'] is h.server.city_studies
        return dict(import_id='1'*32,evaluation_id='2'*64,execution='no-op',comparison={'no_op':True},job=None)
    monkeypatch.setattr(revision,'import_project',accept)
    assert api.handle_api(h) and h.response[0]==200 and h.response[1]['state']=='no-op'
    h.headers=dict(h.headers,**{'Content-Length':str(revision.MAX_PROJECT+1)})
    assert api.handle_api(h) and h.response[0]==413
    h.headers={'Content-Type':'application/json','Content-Length':str(len(raw))}
    h.path=h.path.split('?')[0]+'?actor=x&reason=y&data_crs=EPSG%3A4326&approval=true'
    assert api.handle_api(h) and h.response[0]==400
    assert h.response[1]['input_retained'] is False


def test_study_export_route_uses_exact_verified_job_instead_of_published_city(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from engineering.rustgis import api
    archive=tmp_path/'project.zip';archive.write_bytes(b'zip fixture')
    class Handler:
        root=tmp_path;command='GET';server=SimpleNamespace(city_studies=object())
        path='/api/rustgis/study/'+'1'*32+'/'+'2'*64+'.zip'
        def respond(self,*args):self.response=args
    h=Handler();monkeypatch.setattr(api,'_loopback',lambda *a,**k:True)
    monkeypatch.setattr(adapter,'study_input',lambda *a,**k:({'packet_id':'2'*64},))
    monkeypatch.setattr(adapter,'export_study',lambda *a,**k:{'archive':str(archive)})
    monkeypatch.setattr(adapter,'city_input',lambda *a,**k:(_ for _ in ()).throw(AssertionError('published resolver must not be used')))
    assert api.handle_api(h) and h.response==(200,b'zip fixture','application/zip')
    monkeypatch.setattr(adapter,'study_input',lambda *a,**k:({'packet_id':'3'*64},))
    assert api.handle_api(h) and h.response[0]==409

