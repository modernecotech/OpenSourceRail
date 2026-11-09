"""Invented local source fixtures only; never adapt the actual P1/P6/R4 bundle."""
from copy import deepcopy
import gzip
from math import pi,prod
import subprocess

import pytest

from engineering import chair_p6_counterparts as c


@pytest.fixture(autouse=True)
def no_producers(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('Actual/native/body producer forbidden')
    monkeypatch.setattr(subprocess,'Popen',forbidden)


def component(name,g,at,*,R=None,material='body/al5083',meta=None):
    return dict(id=name,geometry=g,at_m=at,rotation=deepcopy(c.I if R is None else R),frame='body',material_id=material,metadata=meta or {},cost_usd=1.)


def interfaces():
    out=[]
    for hx in (-.4,.5):
        out.append(component(f'retained/underframe/internal-diaphragm/{hx}',dict(kind='box',size_m=[.008,.63,.32]),[hx,0.,.9395]))
        for side in (-1,1):
            header=f'header/{side}/{hx}';cap=f'p6/endcap/{side}/{hx}'
            out.append(component(header,dict(kind='rhs',size_m=[.7285,.12,.18],wall_m=.008),[hx,side*.72575,1.0195],R=c.HEADER_R))
            out.append(component(cap,dict(kind='box',size_m=[.12,.008,.18]),[hx,side*1.094,1.0195]))
            path=[[hx-.06,side*1.09,.9295],[hx+.06,side*1.09,.9295],[hx+.06,side*1.09,1.1095],[hx-.06,side*1.09,1.1095],[hx-.06,side*1.09,.9295]]
            out.append(component(f'p6/endcap-weld/{side}/{hx}',dict(kind='route',path_m=path,radius_m=.004),[0.,0.,0.],meta=dict(declared_parent_ids=[cap,header])))
            out.append(component(f'retained/underframe/crossmember-joint-cleat/{side}/{hx}',dict(kind='box',size_m=[.2,.01,.18]),[hx,side*.33,1.0195],material='body/al6005a'))
    return out


def mapping():
    layout=dict(cars=1,car_length_m=17.,intercar_gap_m=.65,bogie_centres_local_x_m=[-6.4,6.4])
    stubs=[dict(id='invented/stubs/car0',part_id='underframe/floor-crossmember-stub',material_id='body/al6005a',
        count=8,rotation=deepcopy(c.HEADER_R),geometry=dict(kind='rhs',size_m=[.7835,.100,.180],source_stock=dict(wall_m=.006)),
        car_allocation=[[0,1.]],positions_m=[[x,y,1.0195] for x in (1.7,2.6,14.4,15.3) for y in (-.75325,.75325)])]
    return c.map_headers(c.header_templates(interfaces()),layout,stubs,p1_physical_id=c.P1['physical_id'],p6_pin=c.P6)


def test_exact_front_and_proper_rear_mapping_has_no_second_lift():
    rows=mapping();assert len(rows)==8 and len({x['old_stub']['source_key'] for x in rows})==8
    for row in rows:
        assert row['additional_lift_m']==0. and row['placement']['translation_m'][2]==0.
        h=row['template']['header'];world=row['world_header_center_m'];front=row['placement']['bogie']=='front'
        assert world[0]==pytest.approx((2.1 if front else 14.9)+(1 if front else -1)*h['at_m'][0])
        assert world[1]==pytest.approx((1 if front else -1)*h['at_m'][1])
        assert world[2]==1.0195
        assert row['placement']['rotation']==(c.I if front else c.REAR)


def test_frozen_same_physical_but_wrong_evaluation_does_not_authenticate():
    physical=dict(synthetic=True);record=dict(candidate_id=c.identity(physical),physical_definition=physical,evaluation_id='a'*64)
    raw=gzip.compress(c.encoded(record),mtime=0);pin=dict(physical_id=record['candidate_id'],evaluation_id='a'*64,raw_sha256=c.sha256(raw).hexdigest())
    assert c.authenticated_record(raw,pin)==record
    with pytest.raises(ValueError):c.authenticated_record(raw,dict(pin,evaluation_id='b'*64))
    with pytest.raises(ValueError):c.authenticated_record(raw+b'x',pin)
    bad=dict(c.P6,evaluation_id='3202ebbf3b6ca827bde78466c5047734fdc3b53fb8a70330744026b9f280467a')
    with pytest.raises(ValueError):c.map_headers(c.header_templates(interfaces()),dict(cars=1,car_length_m=17.,intercar_gap_m=.65,bogie_centres_local_x_m=[-6.4,6.4]),[],p1_physical_id=c.P1['physical_id'],p6_pin=bad)


@pytest.mark.parametrize('mutate',[
    lambda x:x.pop(),
    lambda x:x[0]['geometry']['size_m'].__setitem__(0,.010),
    lambda x:next(v for v in x if v['id'].startswith('header/'))['rotation'][0].__setitem__(1,1.),
    lambda x:next(v for v in x if v['id'].startswith('header/'))['at_m'].__setitem__(2,1.1695),
    lambda x:next(v for v in x if v['id'].startswith('p6/endcap-weld/'))['geometry'].update(radius_m=.003),
    lambda x:next(v for v in x if v['id'].startswith('p6/endcap-weld/'))['at_m'].__setitem__(2,.150),
])
def test_changed_or_missing_actual_mates_refused(mutate):
    x=interfaces();mutate(x)
    with pytest.raises(ValueError):c.header_templates(x)


def test_mixed_template_epoch_and_double_stub_disposition_refused():
    rows=mapping();templates=c.header_templates(interfaces());templates[0]['header']['cost_usd']=999.
    with pytest.raises(ValueError):c.map_headers(templates,dict(cars=1,car_length_m=17.,intercar_gap_m=.65,bogie_centres_local_x_m=[-6.4,6.4]),[],p1_physical_id=c.P1['physical_id'],p6_pin=c.P6)
    with pytest.raises(ValueError):c.transform([0.,0.,0.],[0.,0.,0.],[[-1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])


def test_original120mm_gap_hold_and_revised_rows_keep_5mm_requirement():
    a=c.necessary_anchor_gap(.120,.085);assert a['gap_m']==pytest.approx(.002) and not a['necessary_passed']
    b=c.necessary_anchor_gap(.120,.090);assert b['gap_m']==pytest.approx(.007) and b['necessary_passed']
    assert c.necessary_anchor_gap(.100,.085)['gap_m']==pytest.approx(.012)
    row=mapping()[0];lane=-1.0725
    with pytest.raises(ValueError):c.node_proposal(row,lane,.085,connected_sides=['left','right'],reviewed_joint_id='c'*64,unresolved_interfaces=[])
    with pytest.raises(ValueError):c.node_proposal(row,lane,.09,connected_sides=['left'],reviewed_joint_id='c'*64,unresolved_interfaces=['mate pending'])


@pytest.mark.parametrize('depth,bolt,grip',[(.100,.140,.121),(.120,.160,.141)])
def test_two_hardware_depths_keep_full_width_sleeves_and_closed_grip(depth,bolt,grip):
    h=c.node_hardware(depth);assert h['sleeve_length_m']==depth
    assert h['M8_underhead_length_m']==pytest.approx(bolt) and h['grip_m']==pytest.approx(grip)
    assert h['nominal_thread_projection_m']==pytest.approx(.0093) and h['bolt_count']==h['sleeve_count']==2
    assert h['qualified'] is False


def test_node_bores_are_contained_in_both_transformed120mm_walls():
    for row in mapping():
        sign=1 if row['world_header_center_m'][1]>0 else -1
        node=c.node_proposal(row,sign*1.0725,.09,connected_sides=['left','right'],reviewed_joint_id='c'*64,unresolved_interfaces=[])
        assert len(node['bores'])==2 and node['plates']['internal_12mm_bridge_diaphragms']==2
        assert node['plates']['notch_width_m']==pytest.approx(.0225)
        assert node['hardware_dimensions']['M8_underhead_length_m']==pytest.approx(.160)
        assert node['apply_automatically'] is False and node['actual_source_machining_applied'] is False
        for b in node['bores']:
            assert b['header_local_axis']==1 and b['header_local_wall_planes_m']==[-.060,.060]
            assert b['removed_wall_volume_m3']==pytest.approx(2*.008*pi*.0071**2)
            assert abs(b['header_local_center_m'][0])+.0071<.7285/2
            assert abs(b['header_local_center_m'][2])+.0071<.18/2
    bad=mapping()[0];bad['world_header_center_m'][2]+=.15
    with pytest.raises(ValueError):c.node_proposal(bad,-1.0725,.09,connected_sides=['left'],reviewed_joint_id='c'*64,unresolved_interfaces=[])


def test_spacer_shoe_is_counted_and_does_not_claim_central_diaphragm_contact():
    templates=c.header_templates(interfaces())
    for t in templates:
        shoe=c.spacer_shoe_proposal(t);assert t['header_to_cleat_gap_m']==pytest.approx(.0265)
        assert shoe['geometry']['size_m']==[.120,.0265,.180]
        assert shoe['gross_volume_m3']>shoe['net_volume_m3']>0 and shoe['quantity_per_header']==1
        assert shoe['nominal_mass_kg']==pytest.approx(1.522584)
        assert shoe['joint_welds']['nominal_floor_gap_after_4mm_halo_m']==.006
        assert shoe['main_girder_and_cleat_joint_qualification'] is False
        assert shoe['actual_mating_and_tool_evaluation'] is False


def legacy_volume(e):
    if e['shape']=='cylinder':return pi*(e['radius_m']**2-e['inner_radius_m']**2)*e['length_m']
    return prod(e['size_m'])-sum(pi*(h['diameter_m']/2)**2*e['size_m'][h['axis']] for h in e['bores'])


def coupon_fixture(rows=(-.05,.19)):
    es=[];stacks=[]
    def box(name,center,size,holes=()):es.append(dict(id=name,shape='box',material='al5083',center_m=center,size_m=size,bores=list(holes)))
    def bore(u,v):return dict(axis=2,center_m=[u,v,0.],diameter_m=.009)
    for i,(u,v) in enumerate([(-.1625,-.12),(-.1625,.12),(.1625,-.12),(.1625,.12)]):box(f'foot-{i}',[u,v,-.44],[.11,.17,.02],[bore(-.1325 if u<0 else .1325,rows[i%2])])
    for row in (0,1):
        box(f'anchor-strip-{row}',[0.,(-1 if row==0 else 1)*.12,-.4515],[.455,.19,.003],[bore(u,rows[row]) for u in (-.1325,.1325)])
        for col,u in enumerate((-.1325,.1325)):
            for prefix in ('floor-M8','floor-sleeve','head-isolation','dielectric-liner','tip-cap'):
                name=f'{prefix}-{row}-{col}'+('/shank-thread-blank' if prefix=='floor-M8' else '')
                es.append(dict(id=name,shape='cylinder',material='steel',axis=2,start_m=[u,rows[row],-.55],length_m=.140 if prefix=='floor-M8' else .005,radius_m=.007 if prefix=='floor-sleeve' else .004,inner_radius_m=0.))
            for prefix in ('isolation','backing','nut-cage'):box(f'{prefix}-{row}-{col}',[u,rows[row],-.55],[.05,.02,.004])
            e=next(e for e in es if e['id']==f'floor-M8-{row}-{col}/shank-thread-blank')
            stacks.append(dict(id=f'floor-M8-{row}-{col}',head_bearing_face_m=[u,rows[row],-.429],entities=[deepcopy(e)],bolt_underhead_length_m=.140))
    stocks=[dict(id=e['id'],material=e['material'],entity_ids=[e['id']],net_volume_m3=legacy_volume(e),gross_volume_m3=legacy_volume(e)+1e-6,process_hours=.1,qa_hours=.01) for e in es]
    recipe=dict(geometry=dict(foot_size_m=[.110,.170,.020],leg_length_m=.3775),preliminary_loads=dict(occupant_kg=100.,provisional_chair_kg=15.,gravity_m_s2=9.81,vertical_factor=3.,longitudinal_factor=1.,lateral_factor=1.,overturning_height_above_floor_m=.6),rate_usd_kg=[2.,4.,8.])
    coupon=dict(schema='osr.chair-installation-proposal/1',entities=es,stock=stocks,row_v_m=list(rows),recipe_id=c.identity(recipe),fastener_stacks=stacks,consumables=dict(welds=[],anchor_sealant=dict(net_mass_kg=[.01,.02,.03],centroid_hypothesis_m=[0.,0.,-.45])),status=deepcopy(c.FLAGS))
    return coupon,recipe


def revise(coupon,recipe,rows):return c.revised_coupon_rows(coupon,recipe,rows,expected_physical_id=c.identity(c.coupon_projection(coupon)),manufacturing_state='new-design-unfabricated')


def test_new_5mm_rows_replace_bores_and_move_all_ancillaries_without_lifting():
    old,recipe=coupon_fixture();before=deepcopy(old);new=revise(old,recipe,[-.045,.19]);assert old==before
    by={e['id']:e for e in new['entities']};oldby={e['id']:e for e in old['entities']}
    for i in (0,2):assert by[f'foot-{i}']['bores'][0]['center_m'][1]==-.045 and by[f'foot-{i}']['center_m']==oldby[f'foot-{i}']['center_m']
    assert len(by['foot-0']['bores'])==1 and by['floor-sleeve-0-0']['start_m'][1]==-.045
    assert by['floor-M8-0-0/shank-thread-blank']['length_m']==.140
    assert by['floor-M8-0-0/shank-thread-blank']['start_m'][2]==oldby['floor-M8-0-0/shank-thread-blank']['start_m'][2]
    assert new['row_revision']['extra_process_person_hours']==pytest.approx(.045)
    assert new['row_revision']['extra_QA_person_hours']==pytest.approx(.015)
    assert [s['gross_volume_m3'] for s in new['stock']]==[s['gross_volume_m3'] for s in old['stock']]
    assert new['support_bounds']['fixture_band_screen_passed'] and not new['support_bounds']['qualified']
    assert new['definition_id']!=c.identity(c.coupon_projection(old)) and new['recipe_id']!=old['recipe_id']
    assert new['recipe_id']==c.identity(new['definition_recipe'])
    assert new['definition_recipe']['anchor_row_revision']['new_rows_m']==[-.045,.19]
    assert new['row_revision']['prior_moments_and_native_and_body_results_inherited'] is False
    assert all(v is False for v in new['status'].values())


@pytest.mark.parametrize('bad',[-.04,-.047,True,float('nan')])
def test_unreviewed_row_steps_refused(bad):
    a,r=coupon_fixture()
    with pytest.raises(ValueError):revise(a,r,[bad,.19])


def test_existing_parts_cannot_be_redrilled_and_missing_row_ownership_refused():
    a,r=coupon_fixture()
    with pytest.raises(ValueError):c.revised_coupon_rows(a,r,[-.045,.19],expected_physical_id=c.identity(c.coupon_projection(a)),manufacturing_state='already-fabricated')
    a['entities']=[e for e in a['entities'] if e['id']!='tip-cap-0-0']
    with pytest.raises(ValueError):revise(a,r,[-.045,.19])


def test_prices_and_QA_do_not_become_new_physical_geometry():
    a,r=coupon_fixture();x=revise(a,r,[-.045,.19]);a['stock'][0]['quote_usd']=999.;r['rate_usd_kg']=[3.,6.,12.];a['recipe_id']=c.identity(r)
    y=revise(a,r,[-.045,.19]);assert x['definition_id']==y['definition_id'] and x['evaluation_id']!=y['evaluation_id']


def credit_fixture():
    rows=[dict(source_part_id=k,source_hash='c'*64,quantity=264) for k in c.OLD_PARTS]
    wear=dict(translate_z_m=.0185,source_pieces=108,gross_stock_and_cost_retained=True)
    return rows,wear


def credits(rows,wear,**kw):return c.floor_and_credit_guard(rows,wear,expected_credit_record_ids=[c.identity(r) for r in rows],expected_wear_record_id=c.identity(wear),already_applied_credit_ids=kw.get('already',[]),wear_translation_already_applied=kw.get('translated',False))


def test_allowances_and_wear_global_correction_are_once_only():
    rows,wear=credit_fixture();out=credits(rows,wear)
    assert out['wear_global_delta_z_m']==.0185 and out['geometry_seat_lift_m']==0.
    assert out['apply_automatically'] is False
    with pytest.raises(ValueError):credits(rows,wear,already=[rows[0]['source_part_id']])
    with pytest.raises(ValueError):credits(rows,wear,translated=True)
    rows[0]['source_part_id']='body/chair-unrelated'
    with pytest.raises(ValueError):credits(rows,wear)


def test_stale_credit_epoch_and_wear_datum_are_refused():
    rows,wear=credit_fixture();before=[c.identity(r) for r in rows];rows[0]['quantity']=265
    with pytest.raises(ValueError):c.floor_and_credit_guard(rows,wear,expected_credit_record_ids=before,expected_wear_record_id=c.identity(wear),already_applied_credit_ids=[],wear_translation_already_applied=False)
    wear['translate_z_m']=.150
    with pytest.raises(ValueError):credits(rows,wear)


@pytest.mark.parametrize('mutate',[
    lambda r:r['preliminary_loads'].update(gravity_m_s2=True),
    lambda r:r['geometry']['foot_size_m'].__setitem__(2,.004),
    lambda r:r['geometry'].update(leg_length_m=.3935),
])
def test_new_rows_cannot_inherit_changed_load_or_stock_hypotheses(mutate):
    a,r=coupon_fixture();mutate(r);a['recipe_id']=c.identity(r)
    with pytest.raises(ValueError):revise(a,r,[-.045,.19])
