"""Synthetic geometry/contract controls; never actual railway engineering evidence."""
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import pytest
from engineering.railway_project import drawings as d
from engineering.station_rail.common import identity,digest


def seal(v,key='evaluation_id'):
    v.pop(key,None);v[key]=identity(v);return v


def fixture_data(stocks=None):
    stocks=stocks or [dict(kind='box',size_m=[.26,.24,.025]),dict(kind='rhs',length_m=2.1,width_m=.22,depth_m=.25,wall_m=.014),dict(kind='annulus',length_m=.06,outer_radius_m=.38,inner_radius_m=.05),dict(kind='envelope',size_m=[.8,.5,.6])]
    parts=[];patterns=[];physical=[]
    for i,stock in enumerate(stocks):
        pid='synthetic/p'+str(i);definition=identity(dict(part_id=pid,stock=stock));part=dict(id=pid,component_definition_id=definition,name='Synthetic '+str(stock['kind'])+' research specimen',assembly_id='synthetic/assembly',material_id='synthetic/steel',quantity_per_train=1,unit='each',stock=stock,manufacturing=['Inspect traceable source stock','Cut/form stated workpiece'])
        parts.append(part);g=dict(kind=stock['kind'],source_stock=deepcopy(stock),size_m=[.01,.01,.01],exact_stock=stock['kind']!='envelope',definition_basis='synthetic-test',finished_geometry_verified=False);p=dict(id='pattern-'+str(i),part_id=pid,count=1,geometry=g,positions_m=[[i,0,0]],rotation=[[1,0,0],[0,1,0],[0,0,1]],car_allocation=[[0,1.]],bogie_index=None);physical.append(deepcopy(p));patterns.append(dict(p,material_id='synthetic/steel',assembly_occurrence_id='A'))
    pd=dict(schema='synthetic-physical-fixture',occurrence_patterns=physical);body=dict(schema='osr-vehicle-installation/1',candidate_id=identity(pd),parent_bundle_id='a'*64,physical_definition=pd,parts=parts,patterns=patterns,materials=[dict(id='synthetic/steel',specification='Synthetic steel material hypothesis; no certificate')],source_sha256={},engineering_accepted=False,physical_accepted=False,manufacturing_release=False,operating_release=False,movement_authority=False,selected_reference_changed=False);seal(body)
    ids={k:identity(k) for k in d.review.contract.IDENTITIES};ids.update(body_candidate_id=body['candidate_id'],engineering_revision=body['evaluation_id'],source_body_bundle_id=body['parent_bundle_id']);items=[];occ=[]
    for p in parts:
        items.append(dict(p,identities=ids,quantity_project=1,project_fleet=1,serial_plan=dict(serial_number=None,lot_number=None),make_buy='local-fabricate',make_buy_mapping=d.model._make_buy_mapping('local-fabricate'),capacity=dict(provisional_person_h=None,validated_person_h=None,hold_reason='Synthetic unknown validated hours'),counted_direct_parts_process_usd_per_train=dict(low=5.,base=10.,high=15.)))
    for p in patterns:occ.append(dict(id=p['id'],identities=ids,part_id=p['part_id'],component_definition_id=parts[int(p['id'].split('-')[1])]['component_definition_id'],count_per_train=p['count'],assembly_occurrence_id=p['assembly_occurrence_id']))
    proposal=dict(schema='osr-pilot-delivery-proposal/1',status='DRAFT',identities=ids,items=items,occurrence_patterns=occ,material_requirements=[],assembly_routes=[],external_inventory=[],civil_requirements=[],tasks=[],cost_views=[],construction_route=dict(identities=ids),execution_mapping_draft=dict(identities=ids),planning_selection=dict(selected_service_evaluation_id=ids['service_evaluation_id']),summary=dict(project_trainsets=1,task_status_counts={}),capacity=dict(unknown_part_process_hour_ids=[p['id'] for p in parts],provisional_vehicle_person_h=None),source_sha256={});seal(proposal,'proposal_id');return body,proposal


def declare(scope):
    out={}
    for row in scope['selected']:
        variants={}
        for v in row['variants']:
            if not v['shape']:continue
            chars=[dict(id='dim-'+str(i),dimension=k,name=k,unit='mm',minimum=value*1000-.1,maximum=value*1000+.1,method='Explicit synthetic calliper test limit; not physical evidence',evidence_maturity='calculated-research-limit') for i,(k,value) in enumerate(v['shape']['dimensions_m'].items())]
            ops=[dict(source_operation_index=0,sequence=1,operation=row['part']['manufacturing'][0],workstation='Synthetic research bench',tools=['Synthetic dimensional gauge'],setup_minutes=2.,run_minutes_per_unit=3.,time_basis='Explicit synthetic declared process times, not measured',inspection_ids=[x['id'] for x in chars])]
            variants[v['variant_id']]=dict(characteristics=chars,operations=ops)
        out[row['part']['id']]=dict(revision='SYNTHETIC-1',research_holds=['Synthetic unit fixture only; material/process/fit qualification open'],variants=variants)
    return out


def test_stock_cross_sections_source_nominals_and_real_review_payloads(tmp_path):
    body,proposal=fixture_data();scope=d.describe(body,proposal,[p['id'] for p in body['parts']]);out=tmp_path/'drawings';m=d.export(body,proposal,out,[p['id'] for p in body['parts']],declare(scope))
    assert len(m['coverage']['documented_part_ids'])==3
    assert not m['coverage']['all_selected_stock_documents_complete'] and not m['coverage']['whole_vehicle_finished_drawing_coverage_complete']
    assert all(m[k] is False for k in d.FLAGS)
    index=json.loads((out/'documents.json').read_bytes());conversion=json.loads((out/'conversions.json').read_bytes())
    pack=d.review.compile_review_pack(proposal,index,conversion,artifact_root=out,city='synthetic',selected_part_ids=list(conversion));assert len(pack['components'])==3 and not pack['coverage']['complete']
    for row in scope['selected']:
        v=row['variants'][0];folder=out/'parts'/identity(row['part']['id'])[:16];svg=(folder/(v['variant_id'][:16]+'.svg')).read_text();root=ET.fromstring(svg)
        assert root.attrib['width']=='420mm' and '<metadata>' in svg
        if v['shape']['kind']=='box':assert '260 mm' in svg and '10 mm' not in svg
        if v['shape']['kind']=='rhs':assert 'fill-rule="evenodd"' in svg and '14 mm' in svg
        if v['shape']['kind']=='annulus':assert svg.count('<circle')==2 and '100 mm' in svg
        if v['shape']['kind']=='envelope':assert 'BOUNDED INSTALLATION ENVELOPE' in svg and row['part']['id'] not in conversion


def test_all_source_geometry_variants_covered_or_held(tmp_path):
    body,proposal=fixture_data([dict(kind='box',size_m=[1.,.2,.01])]);p=deepcopy(body['patterns'][0]);p.update(id='second-pattern');p['geometry']['source_stock']['size_m'][0]=1.2;body['patterns'].append(p);physical={k:v for k,v in p.items() if k not in ('material_id','assembly_occurrence_id')};body['physical_definition']['occurrence_patterns'].append(physical);body['parts'][0]['quantity_per_train']=2;body['candidate_id']=identity(body['physical_definition']);seal(body);proposal['identities'].update(body_candidate_id=body['candidate_id'],engineering_revision=body['evaluation_id']);item=proposal['items'][0];item.update(quantity_per_train=2,quantity_project=2);o=deepcopy(proposal['occurrence_patterns'][0]);o['id']='second-pattern';proposal['occurrence_patterns'].append(o);seal(proposal,'proposal_id')
    selected=[item['id']];scope=d.describe(body,proposal,selected);assert len(scope['selected'][0]['variants'])==2
    declared=declare(scope);removed=next(iter(declared[item['id']]['variants']));declared[item['id']]['variants'].pop(removed)
    m=d.export(body,proposal,tmp_path/'partial',selected,declared);assert not m['coverage']['all_selected_stock_documents_complete'];assert len(list((tmp_path/'partial').rglob('*.svg')))==2;assert json.loads((tmp_path/'partial/documents.json').read_bytes())['components']==[]
    m=d.export(body,proposal,tmp_path/'complete',selected,declare(scope));assert m['coverage']['all_selected_stock_documents_complete'];side=json.loads(next((tmp_path/'complete').rglob('drawing-metadata.json')).read_bytes());assert len(side['payloads'])==2


@pytest.mark.parametrize('fault',['body-seal','candidate','part-stock','pattern-count','physical-pattern','unknown-part','duplicate-selection','source-changed'])
def test_mixed_or_modified_source_is_rejected(tmp_path,fault):
    b,p=fixture_data();selected=[b['parts'][0]['id']]
    if fault=='body-seal':b['parts'][0]['name']='changed'
    elif fault=='candidate':p['identities']['engineering_revision']='0'*64;seal(p,'proposal_id')
    elif fault=='part-stock':p['items'][0]['stock']['size_m'][0]=99;seal(p,'proposal_id')
    elif fault=='pattern-count':p['occurrence_patterns'][0]['count_per_train']=2;seal(p,'proposal_id')
    elif fault=='physical-pattern':b['patterns'][0]['geometry']['source_stock']['size_m'][0]=99;seal(b);p['identities']['engineering_revision']=b['evaluation_id'];seal(p,'proposal_id')
    elif fault=='unknown-part':selected=['does-not-exist']
    elif fault=='duplicate-selection':selected*=2
    else:b['source_sha256']={'does-not-exist':'0'*64};seal(b);p['identities']['engineering_revision']=b['evaluation_id'];seal(p,'proposal_id')
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):d.describe(b,p,selected)


def test_unsupported_stock_and_missing_limits_remain_held(tmp_path):
    b,p=fixture_data([dict(kind='cut-length',length_m=10.)]);scope=d.describe(b,p,[b['parts'][0]['id']]);assert scope['selected'][0]['variants'][0]['geometry_hold'];m=d.export(b,p,tmp_path/'unsupported',[b['parts'][0]['id']],{});assert not list((tmp_path/'unsupported').rglob('*.svg')) and not m['coverage']['documented_part_ids']
    b,p=fixture_data([dict(kind='cylinder',length_m=.5,radius_m=.08)]);m=d.export(b,p,tmp_path/'no-limits',[b['parts'][0]['id']],{});assert list((tmp_path/'no-limits').rglob('*.svg')) and not m['coverage']['documented_part_ids']


@pytest.mark.parametrize('fault',['wrong-dimension','wrong-unit','exclude-nominal','unknown-variant','unknown-operation','invent-operation','missing-time','dangling-inspection'])
def test_declared_limits_and_routes_are_source_bound(tmp_path,fault):
    b,p=fixture_data([dict(kind='rhs',length_m=1.,width_m=.1,depth_m=.2,wall_m=.005)]);ids=[b['parts'][0]['id']];s=d.describe(b,p,ids);a=declare(s);decl=next(iter(a[ids[0]]['variants'].values()));char=decl['characteristics'][0];op=decl['operations'][0]
    if fault=='wrong-dimension':char['dimension']='unprovided-hole-diameter'
    elif fault=='wrong-unit':char['unit']='inches'
    elif fault=='exclude-nominal':char['minimum']=1e9
    elif fault=='unknown-variant':a[ids[0]]['variants']['f'*64]=deepcopy(decl)
    elif fault=='unknown-operation':op['source_operation_index']=999
    elif fault=='invent-operation':op['operation']='Machine undocumented supplier housing and drill unknown holes'
    elif fault=='missing-time':op.pop('run_minutes_per_unit')
    else:op['inspection_ids']=['missing']
    with pytest.raises((ValueError,KeyError)):d.export(b,p,tmp_path/fault,ids,a)


def test_supported_u_channel_and_polygon_prism_geometry(tmp_path):
    stocks=[dict(kind='u_channel',length_m=1.5,width_m=.035,depth_m=.015,wall_m=.0015),dict(kind='polygon-prism',points_xz_m=[[1.,0.],[2.,0.],[2.,.5],[1.,.25]],thickness_m=.02)]
    b,p=fixture_data(stocks);ids=[x['id'] for x in b['parts']];scope=d.describe(b,p,ids);m=d.export(b,p,tmp_path/'shapes',ids,declare(scope));assert m['coverage']['all_selected_stock_documents_complete'];svg=next(f.read_text() for f in (tmp_path/'shapes').rglob('*.svg') if 'source-polygon-prism' in f.read_text());assert 'END PROJECTION' in svg and '<polygon' in svg


def test_existing_output_and_path_escape_symlink_refused(tmp_path):
    b,p=fixture_data();out=tmp_path/'old';out.mkdir()
    with pytest.raises(ValueError):d.export(b,p,out,[b['parts'][0]['id']],{})
    link=tmp_path/'link';link.symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(ValueError):d.export(b,p,link/'new',[b['parts'][0]['id']],{})
