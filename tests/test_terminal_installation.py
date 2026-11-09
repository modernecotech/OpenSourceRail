"""Bounded pure interface/stock controls; no actual terminal/P1producer jobs."""
from copy import deepcopy
import pytest
from engineering import terminal_installation as t
from engineering.station_rail.common import identity


@pytest.fixture(autouse=True)
def no_actual_producers(monkeypatch):
    import subprocess
    from engineering import terminal_enclosure_joint as old
    from engineering.vehicle_installation import model
    def forbidden(*a,**k):raise AssertionError('Actual/upstream/native producer forbidden')
    monkeypatch.setattr(subprocess,'Popen',forbidden)
    for n in ('recipe','proposal','trial_inputs'):monkeypatch.setattr(old,n,forbidden)
    for n in ('build','load','policy','proposed_parts','geometry','placement'):monkeypatch.setattr(model,n,forbidden)


def cases(x):return dict.fromkeys(t.CASES,float(x))


def test_fixed_source_and_proper_end_bindings():
    r=t.recipe();assert r['fixed']['body_width_m']==2.65 and r['fixed']['seal_frame_width_m']==2.45
    assert r['fixed']['floor_Z_m']==1.15 and r['fixed']['roof_skin_bottom_Z_m']==3.55
    front,rear=r['bindings'];assert t.transform([-.1,0.,-1.2655],front['at_m'],front['rotation'])==pytest.approx([.1,0.,.9845])
    assert t.transform([-.1,0.,-1.2655],rear['at_m'],rear['rotation'])==pytest.approx([105.15,0.,.9845])
    for b in r['bindings']:
        R=b['rotation'];det=sum(R[0][j]*(R[1][(j+1)%3]*R[2][(j+2)%3]-R[1][(j+2)%3]*R[2][(j+1)%3]) for j in range(3));assert det==1


def test_price_hypothesis_does_not_change_physical_recipe_projection():
    r=t.recipe();x=identity(t.physical_projection(r));r['materials']['al5083']['rate_USD_kg']=[100.,200.,300.]
    r['hypotheses']['deflection_m']=.002;assert identity(t.physical_projection(r))==x
    r['geometry']['fixed_post_absV_m']=1.164;assert identity(t.physical_projection(r))!=x


def test_matched_140mm_beam_132mm_sleeve_is_intentionally_stepped():
    j=t.matched_lower_joint();assert j['sleeve_interval_from_beam_entry_m']==[0.,.132]
    assert j['rear_wall_bearing_m']==pytest.approx([.132,.140])
    assert j['grip_m']==pytest.approx(.160) and j['projection_m']==pytest.approx(.012)
    assert j['nominal_top_edge_ligament_m']==pytest.approx(.0304)
    assert j['radial_entry_clearance_m']>0 and j['radial_rear_clearance_m']>0


@pytest.mark.parametrize('kw',[dict(width=.120),dict(wall=.006),dict(sleeve=.130),dict(entry_bore=.017),dict(rear_bore=.019)])
def test_matched_joint_rejects_real_dimension_or_bearing_conflict(kw):
    with pytest.raises(ValueError):t.matched_lower_joint(**kw)


def test_all_ordered_stack_layers_close_and_projection_remains_positive():
    for j in (t.matched_lower_joint(),t.upper_joint(),t.post_joint()):
        assert j['layers'][0]['start_m']==0.
        assert all(a['end_m']==b['start_m'] for a,b in zip(j['layers'],j['layers'][1:]))
        assert j['layers'][-1]['end_m']==j['grip_m']
        assert j['bolt_tip_m']-j['nut_m'][1]>=j['minimum_projection_m']
    assert t.upper_joint()['grip_m']==pytest.approx(.0255)
    assert t.post_joint()['crush_sleeve_m']==pytest.approx(.054)


def test_short_bolt_does_not_get_a_free_thread_projection():
    with pytest.raises(ValueError):t.ordered_stack('bad',[('material',.020)],.024,.005,pitch=.001)


def test_failed40_and80mm_stock_controls_preserved_under_same_loads():
    r=t.recipe();b=t.necessary_bounds(r)
    assert b['retained_failed_40mm_stiffener']['tip_deflection_m']>.001
    assert b['retained_failed_80mm_stiffener']['tip_deflection_m']>.001
    assert b['side_stock_pass'] and b['side_stiffener']['tip_deflection_m']<.001
    assert b['floor_stock_pass'] and b['post_gap_after_source_finish_fixture_m']>.0005
    assert 'not a universal body' in b['deflection_allocation_domain']
    r['hypotheses']['side_pressure_Pa']=20000.;assert not t.necessary_bounds(r)['side_stock_pass']


def test_combined_seal_budget_adds_deformation_slip_and_fabrication():
    r=t.recipe();a=t.combined_seal_budget(r,support_deflection_m=.0006)
    b=t.combined_seal_budget(r,support_deflection_m=.0006,joint_slip_rotation_m=.004)
    assert a['positive_compression_bound'] and not b['positive_compression_bound']
    assert a['maximum_material_strain_limit'] is None and not a['physical_accepted']
    assert t.recipe()['old_compression_failure']['interval_m']==[-.002,.006]


def test_radial_RHS_hole_removes_only_two_actual_walls_and_gross_stays():
    r=t.recipe();s=t.Stock(r);a=s.rhs('plain',.2,.020,.040,.002,[0.,0.,0.])
    b=s.rhs('bored',.2,.020,.040,.002,[0.,0.,0.],holes=[t._hole(1,[0.,0.,0.],.006,.020)])
    ga,gb=s.groups
    assert ga['gross_m3']==gb['gross_m3']
    assert ga['net_m3']-gb['net_m3']==pytest.approx(3.141592653589793*.003**2*.004)
    assert gb['drill_swarf_m3']==pytest.approx(3.141592653589793*.003**2*.004)
    assert ga['net_mass_kg']['base']>gb['net_mass_kg']['base']


def test_sheet_gross_preserves_thickness_and_positive_inplane_cut_allowances():
    s=t.Stock(t.recipe());s.box('sheet',[.002,.100,1.],[0.,0.,0.],'al5754');g=s.groups[0]
    assert g['gross_m3']==pytest.approx(.002*.104*1.011)
    for c in t.CASES:assert g['gross_mass_kg'][c]==pytest.approx(g['net_mass_kg'][c]+g['scrap_mass_kg'][c])


def test_one_fastener_blank_owns_head_and_shank_once():
    s=t.Stock(t.recipe());st=t.ordered_stack('test',[('material',.010),('steel washer',.001)],.020,.004,pitch=.001)
    t._fastener(s,'fixture-M4',0,[0.,0.,0.],1,st,.004,head_height=.004)
    group=next(g for g in s.groups if g['id']=='stock/fixture-M4/onepiece-bolt')
    assert group['entity_ids']==['fixture-M4/bolt','fixture-M4/head'] and group['quantity']==1
    owned=[x for g in s.groups for x in g['entity_ids']];assert len(owned)==len(set(owned))
    assert set(owned)=={x['id'] for x in s.entities}


def test_fabricated_four_plate_gross_has_each_cut_and_keeps_material_once():
    s=t.Stock(t.recipe());e=s.rhs('fabricated',.5,.020,.120,.003,[0.,0.,0.],'al5083')
    cuts=[[.5,.120,.003],[.5,.120,.003],[.5,.014,.003],[.5,.014,.003]];s.fabricated(e,cuts)
    g=s.groups[0];assert g['gross_m3']==pytest.approx(sum((L+.011)*(w+.004)*z for L,w,z in cuts))
    assert g['net_m3']==pytest.approx(.5*(.020*.120-.014*.114)-4*.5*.002**2*.5)
    assert g['corner_bevel_removal_m3']==pytest.approx(4*.5*.002**2*.5)
    assert g['scrap_m3']>0


def test_blind_removable_panel_joint_has_actual_positive_thread_and_pilot():
    s=t.Stock(t.recipe());t.blind_panel_fixing(s,'tiny',0.,1.321,0.)
    j=s.joints[0];assert j['thread_engagement_m']==pytest.approx(.003)
    assert j['remaining_pilot_bound_m']>0 and j['remaining_web_m']>0
    assert min(e['mass_kg']['low'] for e in s.entities)>0
    assert next(e for e in s.entities if e['id']=='tiny/head-envelope')['physical_drawing']['kind']=='revolved-frustum'


def source_fixture():
    """Tiny synthetic catalogue; no actual P1body or builder is loaded."""
    parts=[];patterns=[]
    specs=[('body/end-beam',dict(kind='rhs',length_m=2.29,width_m=.14,depth_m=.25,wall_m=.008)),
           ('body/cantrail',dict(kind='rhs',length_m=17.,width_m=.10,depth_m=.25,wall_m=.0045)),
           ('body/side-post',dict(kind='rhs',length_m=2.35,width_m=.06,depth_m=.08,wall_m=.003))]
    for pid,stock in specs:
        for car in range(6):
            c=8.5+17.65*car
            positions=([[c-8.4,0.,.9845],[c+8.4,0.,.9845]] if pid=='body/end-beam' else [[c,-1.275,3.43],[c,1.275,3.43]] if pid=='body/cantrail' else
                       [[c-7.7,-1.275,2.325],[c-7.7,1.275,2.325],[c+7.7,-1.275,2.325],[c+7.7,1.275,2.325]])
            R=t.YAXIS if pid=='body/end-beam' else t.I if pid=='body/cantrail' else [[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
            patterns.append(dict(id=f'SYNTHETIC/{pid}/{car}',part_id=pid,count=len(positions),positions_m=positions,rotation=R,car_allocation=[[car,1.]]))
        parts.append(dict(id=pid,stock=stock,material_id='body/al6005a',quantity_per_train=12 if pid!='body/side-post' else 24,
          mass_each_kg=cases(100.),direct_cost_each_usd=cases(200.)))
    for pid in ('body/terminal-end-header','body/passage-end-seal'):
        count=2 if pid.endswith('header') else 10
        parts.append(dict(id=pid,stock=None,material_id='synthetic/retained',quantity_per_train=count,mass_each_kg=cases(1.),direct_cost_each_usd=cases(2.)))
        patterns.append(dict(id='SYNTHETIC/'+pid,part_id=pid,count=count,positions_m=[[j,0.,2.] for j in range(count)],rotation=t.I,car_allocation=[[0,1.]]))
    # The names/types/projection keys follow the actual P1 schema; this remains
    # a tiny invented catalogue with four posts/car rather than actual24.
    for p in parts:
        p['component_definition_id']=identity(dict(synthetic_part=p['id']))
        p['source_part_id']=p['id']
    for p in patterns:
        part=next(q for q in parts if q['id']==p['part_id'])
        p['bogie_index']=None
        p['geometry']=dict(kind='rhs',size_m=[part['stock'][k] for k in ('length_m','width_m','depth_m')],source_stock=deepcopy(part['stock'])) if part['stock'] else dict(kind='unknown-envelope')
    layout=dict(cars=6,car_length_m=17.,car_width_m=2.65,intercar_gap_m=.65,floor_top_m=1.15,roof_z_m=3.55,gauge_m=1.435)
    track=dict(schema='osr-wheel-rail-interface/1',inner_face_gauge_m=1.435,nominal_contact_centres_y_m=[-.7525,.7525],nominal_rail_head_width_m=.07,contact_datum='nominal rail head centres',real_profile_verified=False)
    part_keys=('component_definition_id','id','mass_each_kg','material_id','quantity_per_train','source_part_id','stock')
    pattern_keys=('bogie_index','car_allocation','count','geometry','id','part_id','positions_m','rotation')
    physical=dict(schema='SYNTHETIC-terminal-source',layout=deepcopy(layout),config=dict(body_lift_m=.15),track_interface=deepcopy(track),
        parts=[deepcopy({k:p[k] for k in part_keys}) for p in parts],occurrence_patterns=[deepcopy({k:p[k] for k in pattern_keys}) for p in patterns])
    b=t.seal(dict(schema='osr-vehicle-installation/1',candidate_id=identity(physical),physical_definition=physical,parts=parts,patterns=patterns,materials=[],policy=dict(layout=deepcopy(layout),track_interface=deepcopy(track),rates=dict(synthetic_rate=1.),evaluation=dict(advisory_only=True))))
    r=t.recipe();r['parent']=dict(candidate_id=b['candidate_id'],evaluation_id=b['evaluation_id'],raw_sha256='SYNTHETIC')
    return b,r


def test_exact_source_counterparts_no_couponsegment_or_internal_beam_duplication():
    b,r=source_fixture();m=t.counterpart_map(b,r)
    assert len(m)==10 and len({x['id'] for x in m})==10
    assert sum(x['part_id']=='body/end-beam' for x in m)==2
    assert sum(x['part_id']=='body/cantrail' for x in m)==4
    assert sum(x['part_id']=='body/side-post' for x in m)==4
    assert all(x['part']['stock']['length_m']==2.29 for x in m if x['part_id']=='body/end-beam')


def rebind_fixture(b,r):
    b['candidate_id']=identity(b['physical_definition']);b=t.seal(b)
    r['parent'].update(candidate_id=b['candidate_id'],evaluation_id=b['evaluation_id'])
    return b,r


def test_explicit_physical_width_binding_uses_real_key_without_alias_or_second_lift():
    b,r=source_fixture();old=deepcopy(b);c=t.source_dimension_contract(b,r)
    assert 'body_width_m' not in b['policy']['layout']
    assert c['physical_layout_fields']['car_width_m']==2.65
    assert c['authoritative_source_paths']['car_width_m']=='physical_definition.layout.car_width_m'
    assert c['declared_crosscheck_paths']['car_width_m']=='policy.layout.car_width_m'
    assert c['geometry_lift_to_apply_m']==0. and c['physical_accepted'] is False
    assert b==old


def test_lookup_only_fix_preserves_exact_frozen_recipe_identity():
    assert identity(t.recipe())=='66809a859c6c69154cf0ca05b81ae489c8c88bc302c3b8d5c79e619173fd04e4'


@pytest.mark.parametrize('where,mutation',[
    ('physical',lambda x:x.pop('car_width_m')),
    ('policy',lambda x:x.pop('car_width_m')),
    ('physical',lambda x:x.update(car_width_m=2.60)),
    ('policy',lambda x:x.update(car_width_m=2.60)),
    ('physical',lambda x:x.update(car_width_m=True)),
    ('physical',lambda x:x.update(cars=6.)),
    ('policy',lambda x:x.update(floor_top_m=float('inf'))),
    ('policy',lambda x:x.update(roof_z_m=3.70)),
    ('physical',lambda x:x.update(intercar_gap_m=.50)),
])
def test_missing_malformed_or_disagreeing_dimension_refuses_without_input_patch(where,mutation):
    b,r=source_fixture();layout=b['physical_definition']['layout'] if where=='physical' else b['policy']['layout']
    mutation(layout);before=deepcopy(b)
    with pytest.raises(ValueError):t.source_dimension_contract(b,r)
    assert b==before


def test_alias_only_source_refuses_instead_of_guessing_recipe_width():
    b,r=source_fixture()
    for x in (b['physical_definition']['layout'],b['policy']['layout']):x['body_width_m']=x.pop('car_width_m')
    with pytest.raises(ValueError,match='car_width_m'):t.source_dimension_contract(b,r)


@pytest.mark.parametrize('target',('source-lift','physical-track','policy-track','units'))
def test_lift_track_and_unit_contracts_are_explicit(target):
    b,r=source_fixture()
    if target=='source-lift':b['physical_definition']['config']['body_lift_m']=.30
    elif target=='units':r['units']='mm'
    elif target=='physical-track':b['physical_definition']['track_interface']['nominal_contact_centres_y_m']=[-.7175,.7175]
    else:b['policy']['track_interface']['inner_face_gauge_m']=1.50
    with pytest.raises(ValueError):t.source_dimension_contract(b,r)


def test_advisory_prices_evaluation_and_verification_do_not_change_dimension_identity():
    b,r=source_fixture();first=t.source_dimension_contract(b,r)
    b['policy']['rates']['synthetic_rate']=99.;b['policy']['evaluation']['advisory_only']='changed'
    b['policy']['track_interface']['real_profile_verified']=True
    b['parts'][0]['direct_cost_each_usd']=cases(999.)
    b,r=rebind_fixture(b,r);second=t.source_dimension_contract(b,r)
    assert first['physical_field_binding_id']==second['physical_field_binding_id']
    assert second['verification_flags_are_not_qualification'] and not second['physical_accepted']
    assert len(t.counterpart_map(b,r))==10


@pytest.mark.parametrize('mutation',[
    lambda b:b['patterns'][0]['positions_m'][0].__setitem__(2,1.1345),
    lambda b:b['patterns'][0]['geometry']['size_m'].__setitem__(1,.150),
    lambda b:b['parts'][0].update(quantity_per_train=13),
    lambda b:b['patterns'][0].update(count=True),
])
def test_outer_counterpart_schema_cannot_diverge_from_physical_identity(mutation):
    b,r=source_fixture();mutation(b);b,r=rebind_fixture(b,r)
    with pytest.raises(ValueError):t.counterpart_map(b,r)


@pytest.mark.parametrize('kind',('second-lift','reflection'))
def test_resealed_counterpart_placement_or_proper_rotation_failure_still_refuses(kind):
    b,r=source_fixture();p=b['patterns'][0]
    if kind=='second-lift':p['positions_m'][0][2]+=.150
    else:p['rotation']=[[-1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
    physical=next(q for q in b['physical_definition']['occurrence_patterns'] if q['id']==p['id'])
    physical.update(positions_m=deepcopy(p['positions_m']),rotation=deepcopy(p['rotation']))
    b,r=rebind_fixture(b,r)
    with pytest.raises(ValueError):t.counterpart_map(b,r)


def test_exact64wall_operations_conserve_net_removed_moments_by_case():
    b,r=source_fixture();old=deepcopy(b);cp=t.counterpart_map(b,r);groups=t.source_machining(cp,r)
    assert sum(len(g['operations']) for g in groups)==64
    assert sum(len(g['operations']) for g in groups if g['source_part_id']=='body/end-beam')==32
    assert sum(len(g['operations']) for g in groups if g['source_part_id']=='body/cantrail')==8
    assert sum(len(g['operations']) for g in groups if g['source_part_id']=='body/side-post')==24
    assert len({op['id'] for g in groups for op in g['operations']})==64
    for g in groups:
        for c in t.CASES:
            assert g['remaining_mass_kg'][c]+g['removed_mass_kg'][c]==pytest.approx(100.)
            assert all(g['remaining_mass_kg'][c]*g['remaining_centroid_world_m'][i]+g['removed_moment_kg_m'][c][i]==pytest.approx(100.*g['at_m'][i]) for i in range(3))
        assert min(op['nominal_minimum_edge_ligament_m'] for op in g['operations'])>0
        assert g['gross_paid_source_retained']
    assert b==old


def test_source_material_or_stock_mismatch_refuses_not_coupon_assumption():
    b,r=source_fixture();b['parts'][0]['material_id']='body/steel';b['candidate_id']=identity(b['physical_definition']);b=t.seal(b)
    r['parent'].update(candidate_id=b['candidate_id'],evaluation_id=b['evaluation_id'])
    with pytest.raises(ValueError,match='section/material'):t.counterpart_map(b,r)


def test_source_bore_edge_failure_is_not_a_qualification_only_hold():
    b,r=source_fixture();r['geometry']['lower']['mount_v_m']=[1.144]
    with pytest.raises(ValueError,match='exits actual source stock edge'):t.source_machining(t.counterpart_map(b,r),r)


def test_two_unexecuted_requests_and_synthetic_ancestor_cannot_be_requested():
    req=t.requests(t.recipe(),source_commit='f'*40,source_sha256={'SYNTHETIC':'a'*64})
    assert len(req)==2 and all(x['execution_authorized'] is False and x['body_jobs']==0 and x['native_jobs']==0 for x in req)
    assert all(x['physical_accepted'] is False for x in req)
    _,r=source_fixture()
    with pytest.raises(ValueError):t.requests(r,source_commit='f'*40,source_sha256={})


def test_removal_paths_start_installed_and_release_weather_before_panel():
    p=t.assembly_plan(t.recipe())
    assert all(x[0]==[0.,0.,0.] for x in p['paths'].values())
    assert 'before any main panel motion' in p['maintenance'][0]
    assert p['lifting']['shared_fixture_count']==1 and p['lifting']['payload_rating'] is None
    assert not p['tool_and_swept_acceptance']


@pytest.mark.parametrize('size',[[0.,1.,1.],[-.1,1.,1.],[float('nan'),1.,1.],[True,1.,1.]])
def test_bad_stock_cannot_silently_be_zero(size):
    with pytest.raises(ValueError):t.Stock(t.recipe()).box('bad',size,[0.,0.,0.])


def test_classification_uses_project_categories_and_keeps_1mm_revisable():
    from engineering.design_search.requirement_policy import CATEGORIES
    p=t.recipe()['requirement_policy']
    assert all(x['category'] in CATEGORIES for x in p.values() if isinstance(x,dict))
    assert p['stock_deflection_1mm']['category']=='revisable_assumption'


def tiny_local_inputs(r):
    geom=dict(kind='rhs',size_m=[2.25,.1,.1],wall_m=.004,at_m=[-.05,0.,1.05],rotation=t.YAXIS)
    physicalid=identity(dict(schema='SYNTHETIC-local-terminal',geometry=geom))
    local=t.seal(dict(schema='SYNTHETIC-local',physical_definition_id=physicalid,entities=[dict(id='header/0',part_id='research/terminal-enclosure-land-and-stop-r1/header',material='al6005a',geometry=geom,holes=[])]))
    row=dict(part_id=local['entities'][0]['part_id'],quantity=1,mass_kg=cases(10.),direct_usd=cases(100.),
        net_volume_interval_each_m3=[.003456,.003456],gross_each_m3=.004,density_cases_kg_m3=[2700.]*3)
    account=t.seal(dict(rows=[row],consumables=dict(scope='Synthetic positive source process allowance'),
        totals={c:dict(local_direct_scope_usd=200.) for c in t.CASES}))
    r['local'].update(physical_definition_id=physicalid,geometry_evaluation_id=local['evaluation_id'],accounting_evaluation_id=account['evaluation_id'])
    return local,account


def test_tiny_synthetic_typed_delta_is_executable_without_actual_end_materialization(monkeypatch):
    b,r=source_fixture();local,account=tiny_local_inputs(r)
    def tiny_added(rec):
        s=t.Stock(rec);s.box('SYNTHETIC-fixture',[.010,.020,.030],[0.,0.,0.]);return s
    monkeypatch.setattr(t,'added_stock',tiny_added)
    before=deepcopy((b,r,local,account));out=t.compile_proposal(r,b,local,account)
    assert (b,r,local,account)==before
    assert len(out['source_machining'])==10 and out['retained_passage_seals']['quantity']==10
    assert out['old_leaf_replacements'][0]['old_count']==2
    assert out['component_proposal']['composition_admitted'] is False
    assert out['selection_id'] is None and all(out[k] is False for k in t.FLAGS)
    assert out['component_proposal']['stock_groups'][0]['revised_net_material_delta_m3']<0
    assert out['consumables']['legacy_process_consumable_overhead_residual_USD']==cases(100.)


def test_source_epoch_change_refuses_tiny_definition(monkeypatch):
    b,r=source_fixture();local,account=tiny_local_inputs(r)
    def tiny_added(rec):
        s=t.Stock(rec);s.box('SYNTHETIC-fixture',[.010,.020,.030],[0.,0.,0.]);return s
    monkeypatch.setattr(t,'added_stock',tiny_added);epoch=t.sources();calls=[]
    def changed():calls.append(1);return epoch if len(calls)==1 else dict(epoch,changed='new')
    monkeypatch.setattr(t,'sources',changed)
    with pytest.raises(ValueError,match='Source epoch'):t.compile_proposal(r,b,local,account)


def test_lower_foot_outward_first_is_real_material_failure_and_lift_first_has_bounds():
    r=t.recipe();b=t.removal_bounds(r);w=b['failed_outward_first']
    assert w['screen']=='FAIL' and w['penetration_u_m']==.002
    assert all(a<w['witness_uvw_m'][0]<c for a,c in (w['moving_foot_u_m'],w['retained_beam_wall_u_m']))
    #Witnessv=.8 is30mm from each18.2mm bore; it is intact sourcewall.
    assert min(abs(.8-v) for v in r['geometry']['lower']['mount_v_m'])>.0182/2
    assert all(b[k]>.0005 for k in ('lower_vertical_clearance_bound_m','roof_clearance_bound_m','floor_support_rear_gap_bound_m','upper_land_vertical_clearance_bound_m'))
    assert t.assembly_plan(r)['paths']['frame']==[[0.,0.,0.],[0.,0.,.090],[.300,0.,.090]]


@pytest.mark.parametrize('joint,diameter,axis,origin,direction',[
    (t.upper_frame_joint,.006,1,[-.070,1.2235,1.020],-1),
    (t.side_frame_joint,.004,0,[-.0975,1.3095,.020],-1)])
def test_detachable_blind_joints_have_explicit_grip_pilot_web_and_owned_isolation(joint,diameter,axis,origin,direction):
    s=t.Stock(t.recipe());j=joint();t._blind_fastener(s,'SYNTHETIC-joint',axis,origin,direction,j,diameter)
    assert j['bolt_length_m']-j['layers'][-1]['end_m']==pytest.approx(j['thread_engagement_m'])
    assert j['pilot_depth_m']-j['thread_engagement_m']==pytest.approx(j['remaining_pilot_m'])
    assert j['remaining_pilot_bound_m']>0 and j['remaining_boss_web_m']>0
    liner=next(e for e in s.entities if e['id'].endswith('/liner'))
    assert liner['material_id']=='gfrp' and 2*liner['geometry']['outer_radius_m']<j['bore_m']
    assert all(g['gross_m3']>g['net_m3']>0 for g in s.groups)
    j['bolt_length_m']+=.001
    with pytest.raises(ValueError,match='grip/pilot/web'):t._blind_fastener(s,'bad',axis,origin,direction,j,diameter)


def test_weld_cutlength_is_not_fictitious_longitudinal_material_extent():
    s=t.Stock(t.recipe());e=s.weld('SYNTHETIC-perimeter',.28,[0.,0.,0.],leg=.002,axes=(1,2),profile=(.02,.12))
    assert e['geometry']['size_m']==pytest.approx([.004,.024,.124])
    assert len(e['physical_drawing']['local_segments_m'])==4
    assert s.groups[0]['net_m3']==pytest.approx(.5*.002**2*.28)
    with pytest.raises(ValueError,match='perimeter'):s.weld('bad',.30,[0.,0.,0.],profile=(.02,.12))


def test_extended_corner_relief_and_post_bores_are_new_owned_stock_not_P1_ops():
    p=dict(id='post/0',part_id='SYNTHETIC/post',geometry=dict(kind='rhs',at_m=[-.05,1.175,0.],size_m=[2.2,.1,.1],rotation=t.ZAXIS),holes=[])
    land=dict(id='frame-land-ring',part_id='SYNTHETIC/land',geometry=dict(kind='box',at_m=[.003,0.,0.],size_m=[.006,2.45,2.2],rotation=t.I),holes=[])
    old=deepcopy([p,land]);new=t.revise_local(dict(entities=[p,land]),t.recipe())
    assert [p,land]==old and len(new[0]['holes'])==2
    assert new[0]['geometry']['at_m'][1]==1.165
    assert new[1]['additional_voids'][0]['size_m']==[.006,.010,.150]
    assert t.necessary_bounds(t.recipe())['side_stiffener']['span_m']==pytest.approx(.651)


def test_unreviewed_reflection_or_geometry_cannot_silently_materialize():
    r=t.recipe();t.validate_fixed_recipe(r)
    r['bindings'][0]['rotation']=[[-1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
    with pytest.raises(ValueError,match='rotation'):t.validate_fixed_recipe(r)
    r=t.recipe();r['geometry']['floor']['support_X_m'][1]=.220
    with pytest.raises(ValueError,match='geometry'):t.validate_fixed_recipe(r)


def test_all_stock_remains_terminal_local_until_explicit_proper_binding():
    s=t.Stock(t.recipe());s.box('SYNTHETIC/local',[.1,.1,.1],[0.,0.,0.])
    assert s.entities[0]['frame']=='terminal-local-UVW'


def bounds(e):
    half=[sum(abs(e['rotation'][i][j])*e['geometry']['size_m'][j] for j in range(3))/2 for i in range(3)]
    return [[e['at_m'][i]-half[i] for i in range(3)],[e['at_m'][i]+half[i] for i in range(3)]]


@pytest.mark.parametrize('y',[0.,1.2,-1.2])
def test_TF1_old6mm_gap_and_real_hanger_contact_material(y):
    assert 1.190-.080/2-(1.129+.030/2)==pytest.approx(.006)
    s=t.Stock(t.recipe());d=t.floor_root_stock(s,'SYNTHETIC/hanger',y)
    block=next(e for e in s.entities if e['id']=='SYNTHETIC/hanger/block');b=bounds(block)
    assert b[0][0]==pytest.approx(-.100) and b[0][2]+2.25==pytest.approx(1.114)
    assert b[1][2]+2.25==pytest.approx(1.150)
    #The moving support touches the full block at U=-.100 over all30mm of
    #its root height; it cannot acquire a fixed boundary via a6mm airgap.
    assert d['tube_face_Z_m'][0]>=b[0][2]+2.25-1e-12 and d['tube_face_Z_m'][1]<=b[1][2]+2.25
    assert d['frame_contact']['Z_m']==1.150
    assert d['frame_contact']['owner']==('new10mm postbottom closure' if abs(y)>1.15 else 'fixed lowerrail4mm bottomwall')
    #The floorcover occupies U<=-.100,Z1.144..1.150. Boundary contact only.
    assert min(-.100,b[1][0])-max(-.220,b[0][0])<=1e-12
    assert len(s.joints)==1 and s.joints[0]['owned_members']==['SYNTHETIC/hanger/block']
    assert all(g['gross_m3']>g['net_m3']>0 for g in s.groups)


def test_TF1_actual_tube_end_welds_are_finite_on_root_and_inside_cover():
    s=t.Stock(t.recipe());e=t.floor_tube_root_weld(s,'SYNTHETIC/root',0.)
    paths=e['physical_drawing']['local_segments_m']
    total=sum(sum((a[i]-b[i])**2 for i in range(3))**.5 for a,b in paths)
    assert total==pytest.approx(.076)
    for line in paths:
        for p in line:
            q=t.transform(p,e['at_m'],e['rotation'])
            assert q[0]==pytest.approx(-.100)
            assert 1.114<q[2]+2.25<1.144
    b=bounds(e);assert b[1][0]==pytest.approx(-.100) and b[1][2]+2.25==pytest.approx(1.144)
    assert e['at_m'][0]+e['centroid_local_m'][0]==pytest.approx(-.101)
    assert s.welds[0]['leg_m']==.003


def test_TF1_unchanged_force_and_longer_span_with_root_stock_and_weld_bounds():
    b=t.necessary_bounds(t.recipe());f=b['floor_support'];root=b['floor_root']
    assert f['span_m']==pytest.approx(.116) and root['outer_hanger_reaction_N']==1000.
    assert f['tip_deflection_m']>t.section_bound(.020,.030,.003,.110,500.,69e9,60e6)['tip_deflection_m']
    assert 0<root['ideal_stock_deflection_sum_m']<.001
    assert root['root_end_weld_equivalent_Pa']<60e6 and root['root_end_weld_leg_m']==.003
    #At2mm the same real internal endseams exceed the declared60MPa
    #research comparison; the new3mm seam is real added material,not a limit change.
    old_equivalent=root['root_end_weld_equivalent_Pa']*3/2
    assert old_equivalent>60e6
    assert t.recipe()['hypotheses']['floor_point_force_N']==500.
    assert t.recipe()['hypotheses']['deflection_m']==.001


@pytest.mark.parametrize('sign',[-1,1])
def test_TF1_postbottom_closure_matches_shortened_actual_post_and_finite_seams(sign):
    s=t.Stock(t.recipe());e=t.post_bottom_stock(s,'SYNTHETIC/post',sign);bb=bounds(e)
    assert bb[0][2]+2.25==pytest.approx(1.150) and bb[1][2]+2.25==pytest.approx(1.160)
    assert t.recipe()['geometry']['floor']['post_bottom_Z_m']==1.160
    assert s.joints[0]['post_length_m']==pytest.approx(2.190)
    for line in s.welds[0]['local_segments_m']:
        for p in line:
            assert -.050<=p[0]<=.047 and abs(p[1])<=.050 and p[2]==0.
    assert s.welds[0]['length_m']==pytest.approx(.288)


def test_TF2_old_guard_cage_actual_point_conflict_is_preserved_and_new_regions_disjoint():
    old_point=(.0315,.0045)
    assert .0305<old_point[0]<.036 and .0033<old_point[1]<.0048 and old_point[1]>.0085/2
    s=t.Stock(t.recipe());d=t.upper_cage_stock(s,'SYNTHETIC/cage',[0.,0.,0.],1)
    plate,hood,cap=[next(e for e in s.entities if e['id'].endswith('/'+suffix)) for suffix in ('plate','hood','closed-end')]
    assert bounds(plate)[1][1]==pytest.approx(bounds(hood)[0][1])
    assert bounds(hood)[1][1]==pytest.approx(bounds(cap)[0][1])
    assert d['tip_clearance_bound_m']>0 and d['radial_clearance_bound_m']>0 and d['nut_retention_radial_bound_m']>0
    assert d['M3_tool_hood_radial_clearance_bound_m']>0
    assert all(e['material_id']=='gfrp' for e in s.entities)
    assert len(s.groups)==1 and s.groups[0]['quantity']==1
    assert s.groups[0]['net_m3']==pytest.approx(sum(e['mass_kg']['base']/1900. for e in s.entities))


def test_TF2_integral_rigid_hood_eliminates_upper_elastomer_guard_without_dropping_hardware():
    s=t.Stock(t.recipe());j=t.upper_joint()
    t._fastener(s,'SYNTHETIC/M6',1,[0.,0.,0.],1,j,.006,tip_guard=False)
    t.upper_cage_stock(s,'SYNTHETIC/cage',[0.,0.,0.],1)
    assert not any(e['id'].endswith('/tip-guard') for e in s.entities)
    assert len([e for e in s.entities if '/washer/' in e['id']])==4
    assert any(e['id']=='SYNTHETIC/M6/nut' for e in s.entities)
    assert any(e['id']=='SYNTHETIC/cage/closed-end' for e in s.entities)
    owned=[x for g in s.groups for x in g['entity_ids']];assert len(owned)==len(set(owned))


@pytest.mark.parametrize('sign',[-1,1])
def test_TF3_tab_paths_are_two40mm_mating_edges_not_one80mm_line(sign):
    paths=t.tab_weld_segments(sign);assert len(paths)==2
    for line in paths:
        assert sum((line[0][i]-line[1][i])**2 for i in range(3))**.5==pytest.approx(.040)
        for p in line:assert abs(p[0])==.002 and p[1]==-sign*.0015 and abs(p[2])==.020
    assert .080/2>.040/2 #Old single line exceeded each finite tab end20mm.
    s=t.Stock(t.recipe());s.weld('SYNTHETIC/tab',.080,[0.,0.,0.],leg=.002,segments=paths,process_h=.20,qa_h=.10)
    g=s.groups[0];assert g['net_m3']==pytest.approx(.5*.002**2*.080)
    assert g['process_h']==.20 and g['QA_h']==.10


@pytest.mark.parametrize('sign',[-1,1])
def test_TF3_cap_paths_are_two20mm_real_joint_edges(sign):
    paths=t.cap_connector_segments(sign);assert len(paths)==2
    assert paths[0]==[[0.,0.,-.010],[0.,0.,.010]]
    assert paths[1]==[[.006,sign*.0045,-.010],[.006,sign*.0045,.010]]
    #Joint1 innerarm/crossarm atUV(.002,sign*1.221),joint2 crossarm/cap
    #atUV(.008,sign*1.2255); each finite arm is20mm high.
    for line in paths:assert sum((line[0][i]-line[1][i])**2 for i in range(3))**.5==pytest.approx(.020)
    s=t.Stock(t.recipe());s.weld('SYNTHETIC/cap',.040,[0.,0.,0.],segments=paths,process_h=.20,qa_h=.10)
    assert s.groups[0]['net_m3']==pytest.approx(.5*.003**2*.040)


def test_TF4_collar_replaces_half_washer_without_changing_grip_or_pilot():
    j=t.upper_frame_joint();s=t.Stock(t.recipe())
    t._blind_fastener(s,'SYNTHETIC/M6',1,[0.,0.,0.],-1,j,.006)
    assert j['layers'][-1]['end_m']==pytest.approx(.0125)
    assert j['thread_engagement_m']==.0125 and j['remaining_pilot_bound_m']==.0012
    stem=next(e for e in s.entities if e['id'].endswith('/liner'))
    collar=next(e for e in s.entities if e['id'].endswith('/liner-collar'))
    assert bounds(stem)[1][1]==pytest.approx(bounds(collar)[0][1])
    assert len(next(g for g in s.groups if g['id'].endswith('/liner-kit'))['entity_ids'])==2
    assert next(e for e in s.entities if e['id'].endswith('/washer/1'))['geometry']['size_m'][0]==pytest.approx(.0005)


def test_TF4_pocket_material_is_finite_disjoint_from_bore_and_tool_has_pull_clearance():
    d=t.upper_liner_removal_contract();assert d['minimum_stem_clearance_after_pull_m']>.0005
    assert d['tool_gap_bound_m']>0 and d['collar_engagement_bound_m']>0 and d['cantrail_tool_vertical_clearance_bound_m']>0
    assert min(abs(x) for r in d['recess_U_from_bolt_axis_m'] for x in r)>.0082/2
    assert d['recess_W_m']==[-.030,.003] and d['extractor_tip_path_m'][0][2]==-.032
    assert d['extractor_tip_path_m'][-1][1]==.0202
    tool=d['workshop_extractor'];assert tool['quantity_per_train']==1 and not tool['installed']
    assert tool['gross_volume_m3']>tool['net_volume_m3']>0


def test_TF4_no_lift_with_one_missing_duplicate_or_unidentified_liner_kit():
    good=[f'upper-frame/{y}/{j}/M6/liner-kit' for y in (-1,1) for j in range(2)]
    assert t.assert_frame_lift_ready(good)
    for bad in ([],good[:-1],good+[good[0]],good[:-1]+['unidentified']):
        with pytest.raises(ValueError,match='four bridging'):t.assert_frame_lift_ready(bad)
    p=t.assembly_plan(t.recipe());assert p['paths']['floorcover']==[[0.,0.,0.],[0.,0.,.020],[.100,0.,.020]]
    assert any('all four integral10mm' in x for x in p['maintenance'])


def test_TF3_asymmetric_cap_seam_bounds_and_mass_moment_use_both_real_seams():
    s=t.Stock(t.recipe());e=s.weld('SYNTHETIC/cap',.040,[0.,0.,0.],segments=t.cap_connector_segments(1))
    assert e['at_m']==pytest.approx([.003,.00225,0.])
    assert [e['at_m'][i]+e['centroid_local_m'][i] for i in range(3)]==pytest.approx([.003,.00225,0.])
    assert s.welds[0]['local_segments_m']==t.cap_connector_segments(1)
    for line in e['physical_drawing']['local_segments_m']:
        for p in line:
            q=t.transform(p,e['at_m'],e['rotation']);assert all(bounds(e)[0][i]<=q[i]<=bounds(e)[1][i] for i in range(3))


def test_TF1_post_cut_and_new_closure_do_not_silently_move_top_datum():
    p=dict(id='post/0',part_id='SYNTHETIC/post',geometry=dict(kind='rhs',at_m=[-.05,1.175,0.],size_m=[2.2,.1,.1],rotation=t.ZAXIS),holes=[])
    out=t.revise_local(dict(entities=[p]),t.recipe())[0]['geometry']
    assert out['size_m'][0]==pytest.approx(2.190) and out['at_m'][2]==pytest.approx(.005)
    assert out['at_m'][2]+out['size_m'][0]/2==pytest.approx(1.10)
    assert out['at_m'][2]-out['size_m'][0]/2+2.25==pytest.approx(1.160)


@pytest.mark.parametrize('sign',[-1,1])
def test_residual_cap_bead_is_on_exposed_faces_and_triangles_avoid_actual_parents(sign):
    s=t.Stock(t.recipe());e=t.cap_connector_stock(s,'SYNTHETIC/cap',[.002,sign*1.221,0.],sign)
    profiles=e['physical_drawing']['profile_vertices_UV_from_station_m']
    #Source parent cross-sections, written independently from the emitter.
    parents=[((-.015,.002),(1.215,1.221)),((.002,.008),(1.221,1.2255)),((.002,.008),(1.2255,1.3245))]
    def inside(P):
        U,V=P[0],sign*P[1]
        return any(a[0]+1e-12<U<a[1]-1e-12 and b[0]+1e-12<V<b[1]-1e-12 for a,b in parents)
    area=[]
    for tri in profiles:
        A=abs(sum(tri[i][0]*tri[(i+1)%3][1]-tri[(i+1)%3][0]*tri[i][1] for i in range(3)))/2;area.append(A)
        for a in (.1,.3,.5):
            for b in (.1,.3):
                if a+b>=1:continue
                q=[.002+a*tri[0][0]+b*tri[1][0]+(1-a-b)*tri[2][0],sign*1.221+a*tri[0][1]+b*tri[1][1]+(1-a-b)*tri[2][1]]
                assert not inside(q)
    assert area==pytest.approx([.5*.003**2]*2)
    assert s.groups[0]['net_m3']==pytest.approx(sum(area)*.020)
    assert s.groups[0]['process_h']==.25 and s.groups[0]['QA_h']==.15
    assert e['at_m'][0]+e['centroid_local_m'][0]==pytest.approx(.005)
    assert e['at_m'][1]+e['centroid_local_m'][1]==pytest.approx(sign*1.22375)
    assert not s.joints[0]['added_groove_or_parentcut']
    assert e['physical_drawing']['penetration_runout_WPS_qualified'] is False


@pytest.mark.parametrize('sign',[-1,1])
def test_residual_open_slots_have_exact_cut_centroids_and_paid_blank_once(sign):
    s=t.Stock(t.recipe());e=t.upper_liner_tie_stock(s,'SYNTHETIC/tie',sign);g=s.groups[0];sp=t.upper_liner_slot_spec()
    original=.070*.006*.120
    bores=2*3.141592653589793*(.0082/2)**2*.006
    removal=4*(.003*.0315+.5*3.141592653589793*.0015**2)*.0024
    assert g['net_m3']==pytest.approx(original-bores-removal)
    assert g['gross_m3']>original and g['gross_m3']-g['net_m3']==pytest.approx(g['scrap_m3'])
    assert g['process_h']==pytest.approx(.05+4*.10) and g['QA_h']==pytest.approx(.03+4*.04)
    assert sp['removed_volume_m3']*4==pytest.approx(removal)
    assert sp['bottom_W_m']-.030==pytest.approx(-.060) #Actual tiebottom.
    assert sp['remaining_tie_depth_m']==pytest.approx(.0036)
    assert sp['source_bore_radial_ligament_m']==pytest.approx(.0004)
    assert e['mass_kg']['base']==pytest.approx(g['net_m3']*2660.)
    assert e['physical_drawing']['remaining_netsection_qualification'] is False
    assert e['additional_finish_surface_reference_m2']>0
    matcost=g['gross_m3']*2660.*5.
    assert g['direct_cost_usd']['base']==pytest.approx(matcost+(g['process_h']+g['QA_h'])*10.)
    #Cuts are lower than the original tieCG, so remaining centre rises.
    assert e['centroid_local_m'][2]>0


def tool_bounds(part,delta):
    return [[part['at_m'][i]+delta[i]-part['size_m'][i]/2 for i in range(3)],
            [part['at_m'][i]+delta[i]+part['size_m'][i]/2 for i in range(3)]]


def test_residual_complete_tool_entry_takeup_pull_uses_only_actual_open_slot_voids():
    d=t.upper_liner_removal_contract();parts=d['workshop_extractor']['parts_m'];sp=d['slot']
    #Tie relative tobolt hasW[-30,+90]mm,V[-6,0]mm. Slots meet bottom,
    #and full-width straightregion reachesW+1.5mm above every insertedpart.
    for phase in range(3):
        for j in range(33):
            if phase==0:delta=[0.,0.,-.032+j*.001]
            elif phase==1:delta=[0.,j/32*.0002,0.]
            else:delta=[0.,.0002+j/32*.020,0.]
            for part in parts:
                lo,hi=tool_bounds(part,delta)
                overlapW=max(lo[2],-.030)<min(hi[2],.090)-1e-12
                overlapV=max(lo[1],-.006)<min(hi[1],0.)-1e-12
                if overlapW and overlapV:
                    assert part['name']!='handle'
                    assert lo[1]>=-sp['depth_m']-1e-12
                    assert min(hi[2],.090)<=sp['round_end_centre_W_m']+1e-12
                    assert any(a<=lo[0]+1e-12 and hi[0]<=b+1e-12 for a,b in d['recess_U_from_bolt_axis_m'])
    #Two early material-crossing witnesses from4c8 now lie in real cutslot.
    assert d['extractor_tip_path_m'][0]==[0.,0.,-.032]
    assert all(tool_bounds(p,[0,0,-.032])[1][2]<=-.032+1e-12 for p in parts)
    assert d['tool_gap_bound_m']>0 and d['tool_U_side_clearance_bound_m']>0
    assert d['minimum_stem_clearance_after_pull_m']==pytest.approx(.010)


def test_residual_tool_onepiece_regions_have_real_contacts_no_double_material_and_positive_stock():
    d=t.upper_liner_removal_contract();tool=d['workshop_extractor'];parts=tool['parts_m']
    for i,a in enumerate(parts):
        A,B=tool_bounds(a,[0,0,0])
        for b in parts[i+1:]:
            C,D=tool_bounds(b,[0,0,0]);assert min(min(B[k],D[k])-max(A[k],C[k]) for k in range(3))<=1e-12
    for side in (-1,1):
        tip=next(x for x in parts if x['name']==f'tip/{side}');step=next(x for x in parts if x['name']==f'step/{side}');handle=parts[0]
        assert tool_bounds(tip,[0,0,0])[0][2]==pytest.approx(tool_bounds(step,[0,0,0])[1][2])
        assert tool_bounds(step,[0,0,0])[0][2]==pytest.approx(tool_bounds(handle,[0,0,0])[1][2])
    assert tool['net_volume_m3']==pytest.approx(sum(__import__('math').prod(x['size_m']) for x in parts))
    assert tool['gross_volume_m3']>tool['net_volume_m3']>0 and tool['quantity_per_train']==1 and not tool['installed']
    b=tool['necessary_tip_bound'];assert b['force_per_tip_N']==20 and not b['loadsharing_credit']
    assert b['stress_residual_Pa']>0 and b['deflection_m']<.0001
    assert not tool['pull_capability_measured']


def test_residual_paths_preserve_proper_handed_frames_and_capture_before_lift():
    d=t.upper_liner_removal_contract()
    assert d['tool_frame']['positive_rotation']==t.I and d['tool_frame']['negative_rotation']==t.RX180
    assert t.upper_frame_joint()['layers'][-1]['end_m']==.0125
    assert d['stem_OD_m']==.008 and d['bore_m']==.0082 and d['collar_OD_m']==.011
    ids=[f'upper-frame/{y}/{j}/M6/liner-kit' for y in (-1,1) for j in range(2)]
    assert t.assert_frame_lift_ready(ids)
    with pytest.raises(ValueError):t.assert_frame_lift_ready(ids[:-1])
    assert t.necessary_bounds(t.recipe())['floor_root']['outer_hanger_reaction_N']==1000.
