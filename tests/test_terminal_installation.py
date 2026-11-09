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
    physical=dict(schema='SYNTHETIC-terminal-source',parts=parts,patterns=patterns)
    b=t.seal(dict(candidate_id=identity(physical),physical_definition=physical,parts=parts,patterns=patterns,materials=[],policy=dict(layout=dict(body_width_m=2.65,floor_top_m=1.15))))
    r=t.recipe();r['parent']=dict(candidate_id=b['candidate_id'],evaluation_id=b['evaluation_id'],raw_sha256='SYNTHETIC')
    return b,r


def test_exact_source_counterparts_no_couponsegment_or_internal_beam_duplication():
    b,r=source_fixture();m=t.counterpart_map(b,r)
    assert len(m)==10 and len({x['id'] for x in m})==10
    assert sum(x['part_id']=='body/end-beam' for x in m)==2
    assert sum(x['part_id']=='body/cantrail' for x in m)==4
    assert sum(x['part_id']=='body/side-post' for x in m)==4
    assert all(x['part']['stock']['length_m']==2.29 for x in m if x['part_id']=='body/end-beam')


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
    assert paths[1]==[[.003,sign*.0045,-.010],[.003,sign*.0045,.010]]
    #Joint1 innerarm/crossarm atUV(.002,sign*1.221),joint2 crossarm/cap
    #atUV(.005,sign*1.2255); each finite arm is20mm high.
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
    assert d['recess_W_m']==[-.012,.002] and d['extractor_tip_path_m'][0][2]==-.014
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
    assert e['at_m']==pytest.approx([.0015,.00225,0.])
    assert [e['at_m'][i]+e['centroid_local_m'][i] for i in range(3)]==pytest.approx([.0015,.00225,0.])
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
