"""Pure tiny ownership/frame/conservation controls; no actual body/leaf jobs."""
from copy import deepcopy
import gzip
import json

import pytest

from engineering.railway_project import vehicle_composition as v
from engineering.station_rail.common import identity, encoded


@pytest.fixture(autouse=True)
def prohibit_producers(monkeypatch):
    """No shell/native launch or historical body/catalogue producer in fixtures."""
    import subprocess
    from engineering.vehicle_installation import model
    def forbidden(*args,**kwargs):raise AssertionError('Producer/external process forbidden in pure tests')
    monkeypatch.setattr(subprocess,'Popen',forbidden)
    for name in ('build','load','policy','proposed_parts','geometry','placement','_scenario_rows'):
        monkeypatch.setattr(model,name,forbidden)


def cs(x):
    return dict.fromkeys(v.CASES, float(x))


def diag(x, y=None, z=None):
    return [[x,0.,0.],[0.,x if y is None else y,0.],[0.,0.,x if z is None else z]]


def parent():
    parts=[dict(id='support',quantity_per_train=2,material_id='synthetic/al',mass_basis='synthetic primitive',cost_basis='synthetic bounds'),
           dict(id='floor',quantity_per_train=1,material_id='synthetic/al',mass_basis='synthetic primitive',cost_basis='synthetic bounds')]
    g=dict(kind='box',size_m=[.2,.2,.2],source_stock=None)
    patterns=[]
    for name,positions,m,c,S in [('support',[[-1.,0.,1.],[1.,0.,1.]],4.,20.,diag(.01,1.01,1.01)),
                               ('floor',[[0.,0.,1.]],1.,3.,diag(.01))]:
        patterns.append(dict(id=name+'@car0',part_id=name,count=len(positions),positions_m=positions,rotation=deepcopy(v.I),
            geometry=deepcopy(g),centroid_m=[0.,0.,1.],shape_I_per_kg=S,mass_kg=cs(m),direct_cost_usd=cs(c),
            uncertainty_m=[.001]*3,car_allocation=[[0,1.]],bogie_index=None))
    physical=dict(schema='SYNTHETIC/1',parts=parts,patterns=patterns,track_interface=dict(gauge_m=1.435))
    layout=dict(cars=6,car_length_m=17.,intercar_gap_m=.65,bogie_centres_local_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1,floor_top_m=1.15)
    return v.seal(dict(schema='osr-vehicle-installation/1',candidate_id=identity(physical),physical_definition=physical,
        parts=parts,patterns=patterns,policy=dict(layout=layout,evaluation=dict(gravity_m_s2=9.81)),
        fit_validation='OLD-RESULT-MUST-NOT-SURVIVE',journey_validation='OLD-JOURNEY'))


def entity(name='new', *, scope='installed', mass=2.):
    e=dict(id=name,part_id='new-support',material_id='synthetic/al',geometry=dict(kind='box',size_m=[.2,.2,.2],source_stock=None),
        at_m=[0.,0.,0.],rotation=deepcopy(v.I),frame='body',scope=scope,functions=['support'])
    if scope!='context':
        e.update(mass_kg=cs(mass),centroid_local_m=[0.,0.,0.],shape_I_per_kg=diag(.01),uncertainty_m=[.002]*3,
            inertia_basis='synthetic primitive exact moment',mass_basis='synthetic material',cost_share=1.)
    return e


def stock(e, *, cost=4.):
    m=e['mass_kg']['base']
    return dict(id='stock/'+e['id'],entity_ids=[e['id']],net_mass_kg=cs(m),gross_mass_kg=cs(m+.2),scrap_mass_kg=cs(.2),
        direct_cost_usd=cs(cost),basis='synthetic gross/net/cut-reserve',cost_basis='synthetic gross stock+process')


def definition(entities=None):
    entities=[entity()] if entities is None else entities
    d=dict(schema='osr-composition-component/1',units='m',entities=entities,stock_groups=[stock(e) for e in entities if e['scope']!='context'],physical_interfaces=[])
    return freeze_definition(d)


def freeze_definition(d):
    d=deepcopy(d);d['definition_id']=identity(v.definition_physical(d));return v.seal(d)


def inputs(entities=None):
    b=parent();d=definition(entities)
    pin={k:b[k] for k in ('candidate_id','evaluation_id')}
    frames={p['id']:'car0/body' for p in b['patterns']};functions={p['id']:[p['id']] for p in b['parts']}
    original=v.parent_occurrences(b,frames,functions);old=v.source_key(b['candidate_id'],'support@car0',0)
    inst=dict(id='module/0',definition_id=d['definition_id'],at_m=[-1.,0.,1.],rotation=deepcopy(v.I),
        frames=dict(body=dict(name='car0/body',role='body',car_allocation=[[0,1.]],bogie_index=None)))
    m=dict(schema='osr-vehicle-integration-map/1',units='m',parent=pin,definitions={d['definition_id']:d['evaluation_id']},
        source_frames=frames,functions_by_part=functions,installations=[inst],operations=[dict(kind='replace',source_ids=[old],
            source_hashes={old:identity(original[old]['source_ref'])},successor_ids=['module/0/new'],reason='synthetic exact replacement')],
        context_bindings=[],counterparts=[],required_counterpart_ids=[],unresolved_interfaces=[],holds=['Synthetic fixture, no engineering result'])
    return b,[d],v.seal(m),pin


def run(data=None):
    b,ds,m,pin=inputs() if data is None else data
    return v.compose(b,ds,m,parent_pin=pin,reviewed_map_id=m['evaluation_id'])


def change_map(data, fn):
    b,ds,m,p=data;fn(m);return b,ds,v.seal(m),p


def change_definition(data, fn):
    b,ds,m,p=data;old=ds[0]['definition_id'];d=deepcopy(ds[0]);fn(d);d=freeze_definition(d)
    m['definitions']={d['definition_id']:d['evaluation_id']}
    for inst in m['installations']:
        if inst['definition_id']==old:inst['definition_id']=d['definition_id']
    return b,[d],v.seal(m),p


def test_one_piece_retirement_new_stock_and_old_results_not_inherited():
    r=run()
    assert r['schema']=='osr-vehicle-installation/1'
    assert r['nominal_part_mass_kg']==cs(5.)
    assert r['direct_parts_process_usd']==cs(17.)
    assert len(r['patterns'])==3 and len(r['retained_source_ids'])==2
    assert r['stock_groups'][0]['entity_ids']==['module/0/new']
    assert sum(p['quantity_per_train'] for p in r['parts'])==3
    assert r['fit_validation'] is r['journey_validation'] is r['native_validation'] is None
    assert r['selection_id'] is None and not r['inherited_validations']
    assert all(r[k] is False for k in v.FLAGS)


def test_expansion_conserves_centroid_inertia_not_pattern_covariance_twice():
    b=parent();rows=v.parent_occurrences(b,{p['id']:'body' for p in b['patterns']},{p['id']:[p['id']] for p in b['parts']})
    support=[r for r in rows.values() if r['part_id']=='support']
    assert support[0]['shape_I_per_kg'][1][1]==pytest.approx(.01)
    a=v.mass_properties(support,'base');p=b['patterns'][0]
    assert a['mass_kg']==4. and a['CG_m']==p['centroid_m']
    assert a['inertia_about_CG_kg_m2'][1][1]==pytest.approx(4.04)


@pytest.mark.parametrize('field,value',[('rotation',[[-1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),('rotation',[[1.,0.,0.],[0.,2.,0.],[0.,0.,1.]]),('at_m',[0.,float('inf'),0.])])
def test_improper_and_nonfinite_placement_refused(field,value):
    data=inputs()
    with pytest.raises(ValueError):
        data=change_map(data,lambda m:m['installations'][0].update({field:value}));run(data)


def test_rear_proper_rotation_moves_points_and_centroid_and_keeps_lift_once():
    data=change_map(inputs(),lambda m:m['installations'][0].update(rotation=diag(-1.,-1.,1.),at_m=[14.9,0.,0.]))
    data=change_definition(data,lambda d:d['entities'][0].update(at_m=[.5,.75,1.0195],centroid_local_m=[.01,0.,0.]))
    r=run(data);e=next(x for x in r['patterns'] if x['id']=='module/0/new')
    assert e['at_m']==pytest.approx([14.4,-.75,1.0195])
    assert e['centroid_m']==pytest.approx([14.39,-.75,1.0195])
    assert e['bogie_index'] is None and e['car_allocation']==[[0,1.]]


@pytest.mark.parametrize('mutation',[
    lambda m:m['operations'].append(deepcopy(m['operations'][0])),
    lambda m:m['operations'][0].update(successor_ids=[]),
    lambda m:m['operations'][0].update(successor_ids=['invented']),
    lambda m:m['operations'][0]['source_hashes'].update({m['operations'][0]['source_ids'][0]:'bad'}),
    lambda m:m['installations'].append(deepcopy(m['installations'][0])),
    lambda m:m['unresolved_interfaces'].append('chair/header120mm unresolved'),
    lambda m:m['installations'][0]['frames']['body'].update(bogie_index=0),
])
def test_invalid_ownership_and_unresolved_interfaces_refused(mutation):
    with pytest.raises(ValueError):run(change_map(inputs(),mutation))


def test_missing_function_successor_refused():
    with pytest.raises(ValueError,match='function successor'):
        run(change_definition(inputs(),lambda d:d['entities'][0].update(functions=['unrelated'])))


@pytest.mark.parametrize('mutation',[
    lambda d:d['stock_groups'].append(deepcopy(d['stock_groups'][0])),
    lambda d:d['stock_groups'][0].update(gross_mass_kg=cs(9.)),
    lambda d:d['stock_groups'][0].update(net_mass_kg=cs(1.)),
    lambda d:d['entities'][0].update(cost_share=2.),
    lambda d:d['entities'][0].update(mass_kg=cs(0.)),
    lambda d:d['entities'][0].update(uncertainty_m=[-.1,0.,0.]),
    lambda d:d['entities'][0]['geometry'].update(size_m=[1.,1.,-1.]),
    lambda d:d.update(units='mm'),
])
def test_stock_material_unit_and_cost_conservation_refusals(mutation):
    with pytest.raises(ValueError):run(change_definition(inputs(),mutation))


def test_continuous_stock_group_can_own_three_physical_sections_once():
    es=[entity('new',mass=1.),entity('tailA',mass=.5),entity('tailB',mass=.5)]
    for e in es:e['cost_share']={'new':.8,'tailA':.1,'tailB':.1}[e['id']]
    data=inputs(es)
    def joint(d):
        d['stock_groups']=[dict(stock(es[0]),entity_ids=['new','tailA','tailB'],net_mass_kg=cs(2.),gross_mass_kg=cs(2.2),scrap_mass_kg=cs(.2))]
    r=run(change_definition(data,joint))
    assert r['nominal_part_mass_kg']==cs(5.) and r['direct_parts_process_usd']==cs(17.)
    assert len(r['stock_groups'])==1


def test_workshop_and_spares_preserved_without_train_multiplier():
    e=entity('tool',scope='lifecycle',mass=7.)
    r=run(inputs([entity(),e]))
    assert r['nominal_part_mass_kg']==cs(5.)
    assert r['lifecycle_definitions'][0]['entities'][0]['mass_kg']==cs(7.)
    assert 'unresolved' in r['lifecycle_definitions'][0]['multiplicity']
    assert len(r['stock_groups'])==1


def context_inputs():
    c=entity('context',scope='context');c.update(at_m=[1.,0.,0.],part_id='floor',functions=['floor'])
    data=inputs([entity(),c]);b,ds,m,pin=data
    key=v.source_key(b['candidate_id'],'floor@car0',0)
    old=v.parent_occurrences(b,m['source_frames'],m['functions_by_part'])[key]
    m['context_bindings']=[dict(installation_id='module/0',local_id='context',source_id=key,source_ref_hash=identity(old['source_ref']))]
    return b,ds,v.seal(m),pin


def test_context_is_preserved_and_not_installed_twice():
    r=run(context_inputs());assert r['nominal_part_mass_kg']==cs(5.) and len(r['patterns'])==3


def test_changed_or_unmapped_context_refused():
    with pytest.raises(ValueError,match='context-only'):
        run(change_definition(context_inputs(),lambda d:d['entities'][1].update(at_m=[2.,0.,0.])))
    with pytest.raises(ValueError,match='context/source'):
        run(change_map(context_inputs(),lambda m:m.update(context_bindings=[])))


def test_raw_authentication_and_substituted_parent_rejected(tmp_path):
    b=parent();p=tmp_path/'body.json.gz';p.write_bytes(gzip.compress(encoded(b),mtime=0))
    pin={k:b[k] for k in ('candidate_id','evaluation_id')};pin['raw_sha256']=v.digest(p)
    assert v.read_authenticated(p,pin)==b
    with pytest.raises(ValueError,match='Raw'):v.read_authenticated(p,dict(pin,raw_sha256='0'*64))
    b['candidate_id']='0'*64;b=v.seal(b)
    with pytest.raises(ValueError,match='Physical'):v.authenticated(b,dict(candidate_id=b['candidate_id'],evaluation_id=b['evaluation_id']))


def test_price_and_tool_inputs_change_evaluation_not_physical_candidate():
    data=inputs();a=run(data)
    b=run(change_definition(data,lambda d:d['stock_groups'][0].update(direct_cost_usd=cs(8.))))
    c=run(change_map(inputs(),lambda m:m.update(tool_socket_radius_m=.030)))
    assert a['candidate_id']==b['candidate_id']==c['candidate_id']
    assert a['evaluation_id']!=b['evaluation_id'] and a['evaluation_id']!=c['evaluation_id']
    g=run(change_definition(inputs(),lambda d:d['entities'][0]['geometry'].update(size_m=[.3,.2,.2])))
    assert a['candidate_id']!=g['candidate_id']


def stack_inputs(sleeve_L=.120,hole_radius=.0071):
    plate=entity();plate['geometry']=dict(kind='box',size_m=[.12,.08,.08],holes=[dict(axis=0,centre_m=[0.,0.,0.],radius_m=hole_radius,length_m=.120)])
    sleeve=entity('sleeve',mass=.2);sleeve.update(geometry=dict(kind='annulus',size_m=[sleeve_L,.014,.014],outer_radius_m=.007,inner_radius_m=.0045))
    data=inputs([plate,sleeve])
    def m(c):
        c['required_counterpart_ids']=['module/0/node']
        c['counterparts']=[dict(id='module/0/node',schema='osr-coaxial-through-stack/1',units='m',axis_world=0,sleeve_id='module/0/sleeve',
            layers=[dict(entity_id='module/0/new',bore_index=0,expected_depth_m=.120)])]
    return change_map(data,m)


def test_actual_120mm_counterpart_accepts_120mm_sleeve_and_bore():
    assert run(stack_inputs())['definition_complete']


def test_exact_100mm_sleeve_in_120mm_counterpart_counterexample():
    with pytest.raises(ValueError,match='span actual counterpart'):run(stack_inputs(.100))


def test_bush_radius_cannot_ignore_actual_bore_diameter():
    with pytest.raises(ValueError,match='diameter'):run(stack_inputs(hole_radius=.0045))


def test_counterpart_width_substitution_and_unknown_schema_refused():
    with pytest.raises(ValueError,match='width/identity'):
        run(change_map(stack_inputs(),lambda m:m['counterparts'][0]['layers'][0].update(expected_depth_m=.100)))
    with pytest.raises(ValueError,match='Unsupported/unresolved'):
        run(change_map(stack_inputs(),lambda m:m['counterparts'][0].update(schema='unreviewed-R4-joint')))


def test_incomplete_or_omitted_counterpart_obligation_refused():
    with pytest.raises(ValueError,match='counterpart'):
        run(change_map(stack_inputs(),lambda m:m.update(counterparts=[])))
    with pytest.raises(ValueError,match='obligation omitted'):
        run(change_definition(inputs(),lambda d:d.update(required_counterpart_ids=['new-joint'])))


def test_in_place_requires_features_and_single_old_new_owner():
    data=change_map(inputs(),lambda m:m['operations'][0].update(kind='machine_in_place'))
    with pytest.raises(ValueError,match='machining'):run(data)
    data=change_map(data,lambda m:m['operations'][0].update(machining_features=[dict(schema='osr-composition-machining/1',kind='bore',bore_index=0)]))
    data=change_definition(data,lambda d:d['entities'][0]['geometry'].update(holes=[dict(axis=0,centre_m=[0.,0.,0.],radius_m=.0071,length_m=.2)]))
    with pytest.raises(ValueError,match='procurement'):run(data)
    source_id=data[2]['operations'][0]['source_ids'][0]
    data=change_definition(data,lambda d:d['stock_groups'][0].update(procurement_disposition='retain-paid-source',
        predecessor_source_id=source_id,parent_paid_cost_usd=cs(10.),additional_process_usd=cs(1.),direct_cost_usd=cs(11.)))
    assert run(data)['definition_complete']


def test_machining_cannot_claim_an_unmaterialized_or_duplicate_bore():
    data=change_map(inputs(),lambda m:m['operations'][0].update(kind='machine_in_place',
        machining_features=[dict(schema='osr-composition-machining/1',kind='bore',bore_index=0)]))
    with pytest.raises(ValueError,match='not in actual'):run(data)


def test_relocation_cannot_hide_material_or_stock_change():
    data=change_map(inputs(),lambda m:m['operations'][0].update(kind='relocate'))
    assert run(data)['definition_complete']
    with pytest.raises(ValueError,match='physical stock'):
        run(change_definition(data,lambda d:d['entities'][0]['geometry'].update(size_m=[.3,.2,.2])))


def test_runtime_rejects_frame_role_substitution():
    with pytest.raises(ValueError,match='frame differs'):
        run(change_map(inputs(),lambda m:m['installations'][0]['frames']['body'].update(role='bogie')))


def test_counterpart_tool_choice_is_not_physical_identity():
    a=run(stack_inputs());b=run(change_map(stack_inputs(),lambda m:m['counterparts'][0].update(tool_radius_m=.030)))
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']


def test_static_load_recompute_is_separate_and_force_moment_close():
    b=run();extra=dict(id='explicit-reserve',mass_kg=cs(1.),centroid_m=[8.5,0.,1.7],shape_I_per_kg=diag(0.),
        car_allocation=[[0,1.]],bogie_index=None,basis='Synthetic positive reserve; no anatomical passenger claim')
    r=v.evaluate_static_loads(b,[extra],scenario_id='synthetic-load',policy=b['policy'])
    assert r['candidate_id']==b['candidate_id'] and r['body_evaluation_id']==b['evaluation_id']
    for case in v.CASES:
        assert r['cases'][case]['reactions']['force_residual_N']==pytest.approx(0.,abs=1e-10)
        assert r['cases'][case]['reactions']['moment_residual_Nm']==pytest.approx(0.,abs=1e-10)
    with pytest.raises(ValueError,match='scenario'):v.evaluate_static_loads(b,[],scenario_id='',policy=b['policy'])


def test_p6_adapter_requires_complete_explicit_map_and_preserves_geometry():
    c=entity();c.update(quantity=1,mass_each_kg=c['mass_kg'])
    physical=dict(schema='SYNTHETIC-P6',components=[dict(id=c['id'],geometry=c['geometry'])])
    p=v.seal(dict(candidate_id=identity(physical),physical_definition=physical,components=[c]))
    pin={k:p[k] for k in ('candidate_id','evaluation_id')}
    fields=('scope','functions','mass_basis','centroid_local_m','shape_I_per_kg','inertia_basis','uncertainty_m','cost_share')
    m=dict(units='m',entities={c['id']:{k:c[k] for k in fields}},stock_groups=[stock(c)],physical_interfaces=[],geometry_status='interrupted; no gate result')
    d=v.adapt_p6_export(p,pin,m)
    assert d['entities'][0]['geometry']==c['geometry'] and d['geometry_status'].startswith('interrupted')
    m['entities']={}
    with pytest.raises(ValueError,match='complete|Complete'):v.adapt_p6_export(p,pin,m)


def test_no_catalogue_or_placement_producer_called(monkeypatch):
    from engineering.vehicle_installation import model
    def forbidden(*args,**kwargs):raise AssertionError('Historical producer invoked')
    for name in ('build','load','policy','proposed_parts','geometry','placement','_scenario_rows'):
        monkeypatch.setattr(model,name,forbidden)
    assert run()['definition_complete']


def test_inputs_are_not_mutated():
    data=inputs();before=deepcopy(data);run(data);assert data==before


@pytest.mark.parametrize('bad',[diag(-.1),[[.1,.2,0.],[.2,.1,0.],[0.,0.,.1]],diag(1.,.1,.1)])
def test_nonphysical_inertia_refused(bad):
    with pytest.raises(ValueError):run(change_definition(inputs(),lambda d:d['entities'][0].update(shape_I_per_kg=bad)))


def p6_hardware_input():
    c=entity();c.update(quantity=1,mass_each_kg=c['mass_kg'])
    hw=dict(motor=dict(manufacturer='SYNTHETIC',model='motor',mechanical_revision='A',unmeasured_rating=None))
    physical=dict(schema='SYNTHETIC-P6',components=[c['geometry']],hardware=hw)
    p=v.seal(dict(candidate_id=identity(physical),physical_definition=physical,hardware=hw,components=[c],
        typed_fixing_joints=[dict(id='joint0')]))
    pin={k:p[k] for k in ('candidate_id','evaluation_id')}
    fields=('scope','functions','mass_basis','centroid_local_m','shape_I_per_kg','inertia_basis','uncertainty_m','cost_share')
    m=dict(units='m',entities={c['id']:{k:c[k] for k in fields}},stock_groups=[stock(c)],physical_interfaces=[],geometry_status='unknown',
        hardware_bindings=dict(motor=['new']),joint_dispositions=dict(joint0=dict(status='qualification-hold-only',reason='Synthetic nominal joint, no force proof')))
    return p,pin,m


def test_p6_hardware_choice_and_joint_obligations_cannot_disappear():
    p,pin,m=p6_hardware_input();d=v.adapt_p6_export(p,pin,m)
    assert d['entities'][0]['hardware_choice']==dict(manufacturer='SYNTHETIC',model='motor',mechanical_revision='A')
    for field in ('hardware_bindings','joint_dispositions'):
        broken=deepcopy(m);broken[field]={}
        with pytest.raises(ValueError):v.adapt_p6_export(p,pin,broken)


def test_p6_adapter_refuses_workshop_as_installed():
    p,pin,m=p6_hardware_input();p['components'][0]['frame']='workshop';p=v.seal(p);pin['evaluation_id']=p['evaluation_id']
    with pytest.raises(ValueError,match='Workshop'):v.adapt_p6_export(p,pin,m)


def test_continuous_carrier_adapter_does_not_split_procurement():
    es=[entity('new',mass=1.),entity('tailA',mass=.5),entity('tailB',mass=.5)]
    for e in es:e['quantity']=1;e['mass_each_kg']=e['mass_kg'];e['cost_share']=1/3
    physical=dict(schema='SYNTHETIC-P6',components=[e['geometry'] for e in es])
    cut=dict(id='carrier',section_occurrence_ids=['new','tailA','tailB'],owned_material_length_m=1.455,
        free_bend_length_m=1.395,tail_length_each_m=.030,gripped_length_each_m=.020,exposed_projection_each_m=.010)
    p=v.seal(dict(candidate_id=identity(physical),physical_definition=physical,components=es,P6_continuous_carrier_cut_groups=[cut]))
    pin={k:p[k] for k in ('candidate_id','evaluation_id')}
    fields=('scope','functions','mass_basis','centroid_local_m','shape_I_per_kg','inertia_basis','uncertainty_m','cost_share')
    m=dict(units='m',entities={e['id']:{k:e[k] for k in fields} for e in es},stock_groups=[stock(e) for e in es],physical_interfaces=[],geometry_status='unknown')
    with pytest.raises(ValueError,match='Continuous P6'):v.adapt_p6_export(p,pin,m)
    m['stock_groups']=[dict(stock(es[0]),entity_ids=['new','tailA','tailB'],net_mass_kg=cs(2.),gross_mass_kg=cs(2.2),
        source_cut_group_id='carrier',procurement_quantity=1,physical_splice_count=0,cut_length_m=1.455)]
    assert v.adapt_p6_export(p,pin,m)['definition_id']
    m['stock_groups'][0]['cut_length_m']=1.395
    with pytest.raises(ValueError,match='cut/tail/grip'):v.adapt_p6_export(p,pin,m)


def test_static_helper_refuses_changed_geometry_domain():
    b=run();b['policy']['layout']['car_length_m']=18.;b=v.seal(b)
    with pytest.raises(ValueError,match='six-car'):v.evaluate_static_loads(b,[],scenario_id='load',policy=b['policy'])
