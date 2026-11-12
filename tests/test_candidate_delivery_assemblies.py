"""Synthetic counted business graphs; no installed door, ERP or physical evidence.

74 types/694 pieces exercise count shape only. They are invented fixture parts,
not authenticated measurements or the current door's engineering definitions.
"""
from copy import deepcopy
from hashlib import sha256
import importlib,importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from engineering.pilot_delivery import review
from engineering.station_rail.common import identity
c=review.contract


@pytest.fixture
def source():
    binding={name:sha256(name.encode()).hexdigest() for name in c.IDENTITIES}
    parts=[]
    for i in range(74):
        q=621 if i==0 else 1
        parts.append(dict(id='synthetic/part-'+str(i),name='Synthetic fixture part '+str(i),identities=binding,
            component_definition_id=sha256(str(i).encode()).hexdigest(),unit='each',quantity_per_train=12*q,quantity_project=120*q,
            counted_direct_parts_process_usd_per_train={'base':float(12*q)},cost_basis='Synthetic USD1/workpiece fixture'))
    routes=[dict(id='synthetic/mechanical',occurrences_per_train=12,assembly_occurrence_ids=['M'+str(i) for i in range(12)],component_type_ids=[p['id'] for p in parts[:37]]),
            dict(id='synthetic/electrical',occurrences_per_train=12,assembly_occurrence_ids=['E'+str(i) for i in range(12)],component_type_ids=[p['id'] for p in parts[37:]])]
    proposal=dict(identities=binding,proposal_id='f'*64,items=parts,assembly_routes=routes)
    groups=[dict(id='synthetic/door-kit',assembly_ids=[r['id'] for r in routes])]
    return proposal,groups


def reseal(node):node['definition_id']=identity({k:v for k,v in node.items() if k!='definition_id'})


def test_counted_74_type_694_piece_hierarchy_is_source_derived(source):
    p,g=source;nodes=review.source_assemblies(p,g);order=c.validate_assemblies(list(nodes.values()),{x['id']:x for x in p['items']},p['identities'],p['proposal_id'])
    assert len(order)==3 and order[-1]['id']=='synthetic/door-kit'
    assert sum(edge['quantity'] for node in order for edge in node['children'] if edge['kind']=='part')==694
    assert all(node['quantity_per_train']==12 for node in order)
    assert all(node['source_reference']['physical_module_id'] is None for node in order)
    assert p['items'][0]['quantity_per_train']==7452 # only invented test counts


@pytest.mark.parametrize('fault',['candidate','cycle','count','missing','duplicate','hash','physical-module','wrong-proposal','edge-kind'])
def test_graph_refuses_mixed_or_unaccounted_source_even_if_resealed(source,fault):
    p,g=source;nodes=list(review.source_assemblies(p,g).values());n=nodes[0]
    if fault=='candidate':n['identities']=dict(n['identities'],candidate_id='0'*64)
    elif fault=='cycle':n['children'].append(dict(kind='assembly',id=nodes[-1]['id'],quantity=1))
    elif fault=='count':n['children'][0]['quantity']+=1
    elif fault=='missing':n['children'][0]['id']='unreviewed/part'
    elif fault=='duplicate':n['children'].append(deepcopy(n['children'][0]))
    elif fault=='hash':n['definition_id']='0'*64
    elif fault=='physical-module':n['source_reference']['physical_module_id']='0'*64
    elif fault=='wrong-proposal':n['source_reference']['proposal_id']='0'*64
    else:n['children'][0]['kind']='unknown-kind'
    if fault!='hash':reseal(n)
    with pytest.raises(ValueError):c.validate_assemblies(nodes,{x['id']:x for x in p['items']},p['identities'],p['proposal_id'])


def test_graph_depth_and_work_are_bounded(source,monkeypatch):
    p,g=source;nodes=list(review.source_assemblies(p,g).values());parts={x['id']:x for x in p['items']}
    monkeypatch.setattr(c,'MAX_ASSEMBLY_DEPTH',1)
    # Visit the root first so a previously visited child cannot hide graph depth.
    for order in (nodes,nodes[::-1]):
        with pytest.raises(ValueError,match='depth'):c.validate_assemblies(order,parts,p['identities'],p['proposal_id'])
    monkeypatch.setattr(c,'MAX_ASSEMBLY_DEPTH',8);monkeypatch.setattr(c,'MAX_ASSEMBLY_EDGES',2)
    with pytest.raises(ValueError,match='work'):c.validate_assemblies(nodes,parts,p['identities'],p['proposal_id'])


def test_context_rejects_client_assembly_even_when_self_consistent(source,monkeypatch):
    p,g=source;nodes=review.source_assemblies(p,g)
    context=c.seal(dict(schema='osr-wheel-delivery-project/1',environment='simulation',city='fixture',project='P',company='C',
        identities=p['identities'],proposal_id=p['proposal_id'],proposal_sha256='e'*64,project_trainsets=10,
        source_parts={x['id']:identity(x) for x in p['items']},source_patterns={x['id']:{'part_id':x['id'],'count_per_train':x['quantity_per_train']} for x in p['items']},
        source_assemblies=nodes,assembly_patterns=c.assembly_patterns(nodes),**c.FLAGS))
    pack=dict(identities=p['identities'],proposal_id=p['proposal_id'],proposal_sha256='e'*64,environment='simulation',city='fixture',
        components=[{'source_part':x,'source_part_sha256':identity(x)} for x in p['items']],coverage={'source_part_ids':sorted(context['source_parts'])},assemblies=list(nodes.values()))
    # Isolate the source-authority binding; complete document validation has its
    # own unchanged tests and is not bypassed by the production bind_pack path.
    monkeypatch.setattr(c,'validate_pack',lambda value:value)
    assert c.bind_pack(pack,context)
    pack['assemblies']=deepcopy(pack['assemblies']);pack['assemblies'][0]['research_holds']=['Client substitute'];reseal(pack['assemblies'][0])
    with pytest.raises(ValueError,match='authoritative'):c.bind_pack(pack,context)


@pytest.fixture
def native(tmp_path,monkeypatch,source):
    spec=importlib.util.spec_from_file_location('flat_adapter_test_double',Path(__file__).with_name('test_candidate_delivery_adapter.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    backend=helper.Backend(tmp_path/'site');monkeypatch.setitem(sys.modules,'frappe',backend)
    monkeypatch.syspath_prepend(str(review.ROOT/'deployment/erpnext/apps/osr_erpnext'))
    name='osr_erpnext.candidate_delivery';monkeypatch.delitem(sys.modules,name,raising=False);module=importlib.import_module(name)
    backend.add('Company','C',default_currency='USD')
    backend.add('Item Group','Products',is_group=0)
    p,g=source;components=[]
    for part in p['items']:
        docs={kind:{'definition':{'research_holds':['Synthetic contract fixture only']}} for kind in c.DOCUMENT_TYPES}
        docs['routing']['definition']['operations']=[dict(workstation='Fixture bench',operation='Synthetic preparation',setup_minutes=1,run_minutes_per_unit=1)]
        components.append(dict(source_part=part,source_part_sha256=identity(part),documents=docs,
            stock_lines=[dict(uom='Nos',quantity=1,rate=1)],conversion={'valuation_mode':'source-priced-workpiece'}))
    pack=dict(sha256='a'*64,identities=p['identities'],proposal_id=p['proposal_id'],components=components,assemblies=list(review.source_assemblies(p,g).values()))
    yield backend,module,pack
    monkeypatch.delitem(sys.modules,name,raising=False)


def test_parent_boms_reference_child_items_without_double_adding_cost(native):
    b,m,p=native;specs=m._specs(SimpleNamespace(name='P',company='C'),p,'Products')
    assert len(specs['components'])==74 and len(specs['assemblies'])==3 and len(specs['boms'])==77
    parent=specs['assemblies'][-1]
    assert parent['counted_child_direct_subtotal_usd']==694.
    assert specs['assembly_roots']==['synthetic/door-kit']
    assert parent['quantity_per_train']==12 and parent['quantity_project']==120
    assert parent['assembly_process_cost_usd'] is None and parent['complete_assembly_cost'] is False
    assert parent['child_items']==[x['finished_item'] for x in specs['assemblies'][:-1]]


def test_apply_resolves_child_bom_names_then_detects_parent_mutation(native,tmp_path,monkeypatch):
    b,m,p=native;project=SimpleNamespace(name='P',company='C');specs=m._specs(project,p,'Products')
    folder=tmp_path/'control';folder.mkdir();value={'specifications':specs}
    review_id='d'*64;context={'sha256':'e'*64}
    reviewed=c.seal(dict(context_sha256=context['sha256'],pack_sha256=p['sha256'],fingerprint=c.digest(value),item_group='Products',review_id=review_id))
    (folder/('review-'+review_id+'.json')).write_text(json.dumps(reviewed))
    monkeypatch.setattr(m,'_role',lambda *a:None);monkeypatch.setattr(m,'_required_permissions',lambda **kw:None)
    monkeypatch.setattr(m,'_pack',lambda *a,**kw:(project,context,folder,{'pack':p}))
    monkeypatch.setattr(m,'_review_record',lambda *a:None)
    monkeypatch.setattr(m,'_prepare',lambda *a,**kw:(project,context,folder,{},value))
    original_get_doc=b.get_doc
    def get_doc(values,name=None):
        if isinstance(values,dict) and values.get('doctype')=='BOM':
            for row in values.get('items',[]):
                if row.get('bom_no') and b.get_doc('BOM',row['bom_no']).docstatus!=1:
                    raise ValueError('ERPNext requires submitted child BOM')
        return original_get_doc(values,name)
    monkeypatch.setattr(b,'get_doc',get_doc)
    result=m.apply('P',p['sha256'],review_id)
    parent=result['applied']['assemblies'][-1];bom=b.get_doc('BOM',parent['bom'])
    children=result['applied']['assemblies'][:-1]
    assert all('bom_no' not in row and row['do_not_explode']==1 for row in bom.items)
    assert [x['bom'] for x in parent['child_bom_links']]==[x['bom'] for x in children]
    assert parent['native_bom_no_links_created'] is False
    assert all(x['docstatus']==0 for x in [dict(docstatus=b.get_doc(r['doctype'],r['name']).docstatus) for r in result['applied']['records']])
    assert not m.apply('P',p['sha256'],review_id)['created']
    bom.items[0]['qty']=2
    with pytest.raises(ValueError,match='fields changed'):m.apply('P',p['sha256'],review_id)


@pytest.mark.parametrize('count',[0,True,1.5,10**9])
def test_source_occurrence_budget_is_checked_before_range_synthesis(source,monkeypatch,count):
    p,g=source
    for route in p['assembly_routes']:route['occurrences_per_train']=count
    def forbidden(*args):raise AssertionError('Unbounded source count reached occurrence synthesis')
    monkeypatch.setattr(review,'range',forbidden,raising=False)
    with pytest.raises(ValueError,match='Bounded positive'):
        review.source_assemblies(p,g)


@pytest.mark.parametrize('value',[1e-10,float('inf'),float('nan'),0.])
def test_source_valuation_cannot_become_zero_or_nonfinite(value):
    with pytest.raises(ValueError):c.native_valuation_rate(value)


def test_usd_source_cannot_silently_become_local_currency(native):
    b,m,p=native;b.get_doc('Company','C').default_currency='IQD'
    with pytest.raises(ValueError,match='FX'):m._specs(SimpleNamespace(name='P',company='C'),p,'Products')
