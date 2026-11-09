"""Invented fixed-dimension material/part fixtures only, never actual P6joint."""
from copy import deepcopy
from math import pi
import pytest
from engineering import header_steel_joint as j


def fixture(side=1,hx=-.4):
    def c(name,kind,size,at,mat,R=None):
        out=dict(id='SYNTHETIC/'+name,geometry=dict(kind=kind,size_m=size),at_m=at,material_id=mat,frame='body',rotation=deepcopy(j.I if R is None else R),source_note='invented values,not realP6parts')
        if kind=='rhs':out['geometry']['wall_m']=.008
        return out
    ctx=dict(source_p6=deepcopy(j.P6),source_kind='SYNTHETIC',
      header=c('header','rhs',[.7285,.12,.18],[hx,side*.72575,1.0195],'body/al5083',j.HEADER_R),
      endplate=c('endplate','box',[.2,.025,.18],[hx,side*.349,1.0195],'body/al5083'),
      cleat=c('cleat','box',[.2,.01,.18],[hx,side*.33,1.0195],'body/steel'),
      main_wall=c('wall','box',[3.3,.01,.32],[-.45,side*.32,.9395],'body/steel'),
      diaphragm=c('diaphragm','box',[.008,.63,.32],[hx,0.,.9395],'body/steel'))
    ctx['source_record_ids']={ctx[k]['id']:j.identity(ctx[k]) for k in ('header','endplate','cleat','main_wall','diaphragm')}
    existing={ctx[k]['id']:[] for k in ('endplate','cleat')}
    a=dict(frame='joint-local-UVW',reference_point_m=[0.,.0265,0.],header_force_N=[None,None,None],header_moment_Nm=[None,None,None],one_fastener_shear_N=None,one_fastener_tension_N=None,preload_each_N=None)
    s={k:None for k in ('effective_bolt_thread_area_m2','minimum_receiver_thread_shear_area_m2','bolt_shear_Pa','bolt_tension_Pa','steel_thread_shear_Pa','Al_bearing_Pa','GFRP_bearing_Pa','Al_shear_Pa','steel_shear_Pa','steel_bearing_Pa','GFRP_compression_Pa','Al_weld_Pa','steel_weld_Pa')}
    binding=dict(base_commit=j.BASE,context_id=j.identity(ctx),finding_id=j.FINDING,request_id='b'*64)
    return ctx,dict(existing_cuts=existing,actions=a,strengths=s,material_policy=None,source_binding=binding)


@pytest.mark.parametrize('side,hx',[(s,x) for s in (-1,1) for x in (-.4,.5)])
def test_allfour_fixed_material_frames_and_retained_endplate_are_preserved(side,hx):
    ctx,kw=fixture(side,hx);old=deepcopy(ctx);out=j.outline(ctx,**kw)
    assert ctx==old and out['source_ownership']['retained_endplate_once']
    assert out['source_preservation']['mainwall_new_bores']==out['source_preservation']['header_new_bores']==0
    assert out['physical_definition']['frame']['rotation']==(j.I if side==1 else [[-1,0,0],[0,-1,0],[0,0,1]])
    assert out['alternatives']['failed_retained']['existing_endplate_obstruction']['prior_shoe_nominal_gross_overlap_m3']==pytest.approx(.00054)
    assert not out['physical_accepted'] and not out['native_evaluator_admitted']
    assert out['source_ownership']['no_new_Alshoe']


def test_steel_cannot_be_relabelled_and_stale_source_refuses():
    ctx,kw=fixture();ctx['cleat']['material_id']='body/al5083';ctx['source_record_ids'][ctx['cleat']['id']]=j.identity(ctx['cleat']);kw['source_binding']['context_id']=j.identity(ctx)
    with pytest.raises(ValueError,match='material'):j.outline(ctx,**kw)
    ctx,kw=fixture();ctx['header']['at_m'][2]+=.15
    with pytest.raises(ValueError):j.outline(ctx,**kw)


def test_1p5mm_pad_and_bushing_stack_prevents_direct_metal_contact_withoutphantomnut():
    ctx,kw=fixture();o=j.outline(ctx,**kw);p={x['id']:x for x in o['parts']}
    pad=p['isolation-pad'];assert pad['geometry']['size_m'][1]==.0015 and pad['at_m'][1]==.00075
    assert o['stack']['grip_m']==.034 and o['stack']['bolt_underhead_m']==.040
    assert o['stack']['nominal_engagement_m']==pytest.approx(.006)
    assert o['stack']['nut_count']==0 and 'blind' in o['stack']['nut_absence_reason']
    assert sum(x['id'].startswith(('lock0/','lock1/')) for x in o['parts'])==8
    assert sum(x['id'].startswith('bush/') for x in o['parts'])==4
    for x in o['parts']:
        if x['id'].startswith('bush/'):
            assert x['geometry']['length_m']==.0265 and x['geometry']['inner_radius_m']>.004
    assert o['stack']['locking_function_qualified'] is False


@pytest.mark.parametrize('side',[-1,1])
def test_real_source_wallcuts_pilot_backweb_and_far_xz_edges(side):
    ctx,kw=fixture(side);o=j.outline(ctx,**kw);al,steel=o['machining']
    assert len(al['new_pilots_or_through_cuts'])==len(steel['new_pilots_or_through_cuts'])==4
    for c in al['new_pilots_or_through_cuts']:
        assert abs(c['at_m'][0])+.0061<.100 and abs(c['at_m'][2])+.0061<.090
        assert c['length_m']==.025
    for c in steel['new_pilots_or_through_cuts']:
        assert c['length_m']==.009 and abs(c['at_m'][1])+c['length_m']/2<=.005+1e-10
        #Remainingrootwall1mm,no bore reaches actualmainwall behindcleat.
        assert min(abs(side*.005-(c['at_m'][1]+s*c['length_m']/2)) for s in (-1,1))==pytest.approx(0.)
    assert o['stack']['backweb_m']==pytest.approx(.001) and o['stack']['backweb_after_0p3mm_budget_m']>0
    assert al['incremental_removed_volume_bounds_m3']==pytest.approx([4*pi*.0061**2*.025]*2)
    assert steel['incremental_removed_volume_bounds_m3'][0]==pytest.approx(4*pi*.0034**2*.009)
    assert steel['incremental_removed_volume_bounds_m3'][1]>steel['incremental_removed_volume_bounds_m3'][0]
    assert not steel['exact_helix_or_full_major_removal_claimed']


def test_priorcuts_are_unioned_and_sourcegross_or_credit_is_not_applied_twice():
    ctx,kw=fixture();frame=j.validate_context(ctx);rows=j.machining(ctx,frame,kw['existing_cuts']);old=deepcopy(kw['existing_cuts'])
    old[ctx['endplate']['id']]=deepcopy(rows[0]['new_pilots_or_through_cuts'])
    out=j.machining(ctx,frame,old);assert out[0]['incremental_removed_volume_bounds_m3']==pytest.approx([0,0])
    assert out[0]['paid_source_gross_retained'] and not out[0]['source_mass_cost_credit_applied']
    old[ctx['cleat']['id']]=None;out=j.machining(ctx,frame,old)
    assert out[1]['incremental_removed_volume_bounds_m3'] is None


def test_unmodelled_bore_union_and_near_coaxial_roundoff_failclosed():
    a=dict(axis=1,at_m=[0.,0.,0.],radius_m=.004,length_m=.010)
    for dx in (.001,1e-16):
        b=deepcopy(a);b['at_m'][0]=dx
        with pytest.raises(ValueError,match='Noncoaxial'):j.cylinder_union([a,b])
    b=deepcopy(a);b['radius_m']=.005
    assert j.cylinder_union([a,b])==pytest.approx(pi*.005**2*.010)
    assert j.cylinder_union([a,a])==pytest.approx(pi*.004**2*.010)


def test_ordinary_dissimilarweld_is_replaced_by_two_explicit_compatible_parent_pairs():
    ctx,kw=fixture();o=j.outline(ctx,**kw);a,b=o['welds']
    assert a['parents']==[ctx['header']['id'],ctx['endplate']['id']]
    assert b['parents']==[ctx['cleat']['id'],ctx['main_wall']['id']]
    assert a['material']=='Al5356-hypothesis' and b['material']=='steel-filler-hypothesis'
    assert a['length_m']==pytest.approx(.460) and b['length_m']==pytest.approx(.540)
    for w in o['welds']:
        assert not w['ordinary_dissimilar_weld'] and w['top_omitted']
        assert max(P[2] for line in w['paths_m'] for P in line)==.080
        assert w['gross_volume_m3']>w['net_volume_m3']>0


def test_missing_actions_and_rates_are_unknown_not_zero_or_complete():
    ctx,kw=fixture();o=j.outline(ctx,**kw)
    assert all(x['capacity_N'] is None and x['residual_N'] is None for x in o['capacity']['fastener_checks'])
    assert all(x['mass_bounds_kg'] is None and x['gross_material_USD'] is None for x in o['materials']['rows'])
    assert not o['capacity']['actual_header_demands_known'] and o['capacity']['engineering_screen']=='held'
    assert not o['complete_factory_or_installed_cost']


def test_declared_capacity_has_no_free_bolt_loadsharing_or_friction():
    ctx,kw=fixture();kw['actions'].update(header_force_N=[1000,2000,3000],header_moment_Nm=[100,200,300],one_fastener_shear_N=5000,one_fastener_tension_N=5000,preload_each_N=8000)
    kw['strengths']={k:100e6 for k in kw['strengths']};kw['strengths']['effective_bolt_thread_area_m2']=30e-6;kw['strengths']['minimum_receiver_thread_shear_area_m2']=80e-6
    o=j.outline(ctx,**kw);c=o['capacity'];assert c['fastener_load_divisor']==1 and c['friction_credit']==0
    assert c['fastener_checks'][0]['demand_N']==5000
    assert c['fastener_checks'][0]['capacity_N']==pytest.approx(3000)
    assert c['fastener_checks'][0]['residual_N']==pytest.approx(-2000)
    assert all(x['stress_bound_Pa']>0 for x in c['weld_bounds']) and c['engineering_screen']=='held'
    kw['actions']['one_fastener_shear_N']=500
    with pytest.raises(ValueError,match='load sharing'):j.outline(ctx,**kw)


def test_actual_weld_centroid_adds_force_eccentricity_even_without_input_moment():
    ctx,kw=fixture();kw['actions'].update(header_force_N=[1000,2000,3000],header_moment_Nm=[0,0,0],one_fastener_shear_N=4000,one_fastener_tension_N=2000,preload_each_N=8000)
    o=j.outline(ctx,**kw);a=o['capacity']['weld_bounds'][0]
    assert a['centroid_m'][2]<0 and any(abs(x)>1 for x in a['moments_at_group_centroid_Nm'])
    assert not o['capacity']['caller_fastener_moment_reaction_bound_validated']


def test_demand_price_changes_evaluation_not_physical_geometry_and_never_mutates_inputs():
    ctx,kw=fixture();before=deepcopy((ctx,kw));a=j.outline(ctx,**kw);assert (ctx,kw)==before
    kw['material_policy']={'labour_USD_h':[6,10,16]}
    for key in ('GFRP','steel','elastomer','Al5356-hypothesis','steel-filler-hypothesis','sealant','coating','compound'):
        kw['material_policy'][key]=dict(density_kg_m3=[1000,2000,8000],USD_kg=[2,5,12])
    b=j.outline(ctx,**kw);assert a['physical_definition_id']==b['physical_definition_id'] and a['evaluation_id']!=b['evaluation_id']
    assert all(min(x['mass_bounds_kg'])>0 and min(x['gross_material_USD'])>0 for x in b['materials']['rows'])
    assert not b['materials']['complete_factory_installed_cost']


def test_full_screw_and_service_path_is_front_access_and_whole_group_held():
    ctx,kw=fixture();o=j.outline(ctx,**kw);d=o['tools_and_sequence']
    assert d['bolt_fullwithdrawal_path_m']==[[0,0,0],[0,.060,0]]
    assert d['header_group_path_m']==[[0,0,0],[0,.150,0]]
    assert d['nominal_tool_header_gap_m']>0
    assert d['shared_fixture']['mass_bounds_kg'][0]>0 and d['shared_fixture']['WLL_N'] is None
    assert not d['continuous_fullbody_tool_lifting_or_translational_acceptance']
    assert o['source_preservation']['header_R4_P7_interfaces_moved'] is False


def test_failed_drilltip_and_unsupported_bypass_transition_are_preserved_not_zeroed():
    ctx,kw=fixture();o=j.outline(ctx,**kw);a=o['alternatives'];bad=a['failed_retained']
    assert bad['failed_twistdrill']['wall_breakthrough_m']>0
    assert not bad['ordinary_Alshoe_route_supported'] and not a['baseline_selected']
    fork=a['alternatives'][1];assert fork['steel_net_volume_before_bores_m3']>0 and fork['cost_USD'] is None
    assert fork['installed_mass_kg'] is None and not fork['bolts_sleeves_isolation_welds_andtooling_complete']


def test_nonfinite_material_demand_or_missing_cut_roster_failsclosed():
    ctx,kw=fixture();kw['actions']['header_force_N'][0]=float('nan')
    with pytest.raises(ValueError):j.outline(ctx,**kw)
    ctx,kw=fixture();kw['existing_cuts']={}
    with pytest.raises(ValueError,match='rosters'):j.outline(ctx,**kw)
    ctx,kw=fixture();kw['strengths']['bolt_shear_Pa']=0
    with pytest.raises(ValueError):j.outline(ctx,**kw)


def test_weld_triangle_sections_are_on_actual_parent_faces_not_buried_or_missing_backing():
    ctx,kw=fixture();o=j.outline(ctx,**kw)
    for index,weld in enumerate(o['welds']):
        for prof in weld['profiles']:
            tri=prof['vertices_m'];a,b=prof['section_axes'];axis=prof['extrusion_axis']
            for wa,wb in ((.2,.3),(.3,.4),(.5,.2)):
                pt=[0.,0.,0.];pt[axis]=sum(prof['interval_m'])/2
                pt[a]=wa*tri[0][0]+wb*tri[1][0]+(1-wa-wb)*tri[2][0]
                pt[b]=wa*tri[0][1]+wb*tri[1][1]+(1-wa-wb)*tri[2][1]
                u,v,z=pt
                if index==0:
                    plate=abs(u)<.100 and .0015<v<.0265 and abs(z)<.090
                    header=.0265<v<.755 and abs(u)<.060 and abs(z)<.090 and (abs(u)>.052 or abs(z)>.082)
                    assert not plate and not header
                else:
                    cleat=abs(u)<.100 and -.010<v<0 and abs(z)<.090
                    wall=-.020<v<-.010 and -.24<z<.080
                    assert not cleat and not wall
    assert o['welds'][0]['profiles'][0]['vertices_m'][0][0]<.0265


def test_thread_stock_depth_runout_and_source_joinery_credits_remain_explicit():
    ctx,kw=fixture();o=j.outline(ctx,**kw);s=o['stack'];owner=o['source_ownership']
    assert s['pilot_depth_m']-s['usable_thread_m']==pytest.approx(.002)
    assert s['usable_thread_m']-s['nominal_engagement_m']==pytest.approx(.001)
    assert s['thread_bottom_clearance_after_0p3mm_budget_m']==pytest.approx(.0007)
    assert owner['old_joinery_mass_credit'] is None and owner['old_joinery_overlap_amount'] is None
    assert len(owner['retained_P6_joinery_ids'])==4 and owner['all_retained_joinery_mass_cost_unchanged']
    assert o['source_machining_process']['hours']>0 and o['source_machining_process']['cost_USD'] is None


def test_geometrically_impossible_strength_areas_are_not_accepted_as_hypotheses():
    ctx,kw=fixture();kw['strengths']['effective_bolt_thread_area_m2']=.001
    with pytest.raises(ValueError,match='majorstock'):j.outline(ctx,**kw)


def test_unordered_material_bounds_do_not_publish_false_low_high_quantities():
    ctx,kw=fixture();kw['material_policy']={'labour_USD_h':[16,10,6]}
    with pytest.raises(ValueError,match='Ordered'):j.outline(ctx,**kw)


def test_declared_actions_are_not_authenticated_real_header_demands():
    ctx,kw=fixture();kw['actions'].update(header_force_N=[1,2,3],header_moment_Nm=[0,0,0],one_fastener_shear_N=4,one_fastener_tension_N=2,preload_each_N=10)
    o=j.outline(ctx,**kw)
    assert o['capacity']['declared_action_vectors_complete'] and not o['capacity']['actual_header_demands_known']


@pytest.mark.parametrize('key,value',[('frame','body-world'),('reference_point_m',[0.,0.,0.])])
def test_force_frame_and_eccentricity_reference_cannot_be_silently_inferred(key,value):
    ctx,kw=fixture();kw['actions'][key]=value
    with pytest.raises(ValueError,match='joint-local'):j.outline(ctx,**kw)


def test_nominal_sixmm_thread_area_cannot_be_used_as_toleranced_minimum():
    ctx,kw=fixture()
    kw['strengths']['minimum_receiver_thread_shear_area_m2']=pi*.008*.00585
    assert pi*.008*.0057<kw['strengths']['minimum_receiver_thread_shear_area_m2']<pi*.008*.006
    with pytest.raises(ValueError,match='minimum engagement'):j.outline(ctx,**kw)


def test_receiver_bearing_and_strip_envelope_use_same_5p7mm_minimum_hypothesis():
    ctx,kw=fixture();kw['strengths']['minimum_receiver_thread_shear_area_m2']=pi*.008*(.006-.0003)
    out=j.outline(ctx,**kw);cap=out['capacity']
    assert out['stack']['minimum_engagement_after_0p3mm_budget_m']==pytest.approx(.0057)
    assert cap['minimum_receiver_engagement_hypothesis_m']==pytest.approx(.0057)
    bearing=next(r for r in cap['fastener_checks'] if r['name']=='steelreceiver projectedbearing')
    strip=next(r for r in cap['fastener_checks'] if r['name'].startswith('steel blindthread strip'))
    assert bearing['area_m2']==pytest.approx(.008*.0057)
    assert strip['area_m2']==pytest.approx(pi*.008*.0057)
    assert cap['minimum_engagement_physically_verified'] is False


def new_build_fixture(side=1,hx=-.4):
    ctx,kw=fixture(side,hx)
    for key,rho,cost in [('endplate',2660.,[8.,19.,43.]),('cleat',7850.,[4.,11.,29.])]:
        c=ctx[key];V=__import__('math').prod(c['geometry']['size_m']);c.update(quantity=1,mass_each_kg={k:V*rho for k in ('low','base','high')},direct_cost_each_usd=dict(zip(('low','base','high'),cost)),uncertainty_m=.01)
    ctx['source_record_ids']={ctx[k]['id']:j.identity(ctx[k]) for k in ('header','endplate','cleat','main_wall','diaphragm')};kw['source_binding']['context_id']=j.identity(ctx)
    kw['existing_cuts']={ctx[k]['id']:None for k in ('endplate','cleat')}
    kw['material_policy']={'labour_USD_h':[6.,10.,16.]}
    kw['manufacturing']=dict(mode='new-build-drawing',state='budget-only, unmanufactured',prior_physical_cut_roster=None,measured_hole_free=False,thread_specification=j.thread_drawing(),
        targets={ctx[k]['id']:dict(source_record_id=ctx['source_record_ids'][ctx[k]['id']],gross_geometry_id=j.identity(ctx[k]['geometry']),complete_future_roster=True,base_voids=[],base_void_process_h=0.,base_void_QA_h=0.) for k in ('endplate','cleat')})
    return ctx,kw


def test_existing_cut_identity_defect_is_fixed_without_claiming_inventory_authentication():
    ctx,kw=fixture();before=deepcopy((ctx,kw));empty=j.outline(ctx,**kw)
    name=ctx['endplate']['id'];kw['existing_cuts'][name]=[dict(axis=1,at_m=[0.,0.,0.],radius_m=.001,length_m=.025)]
    cut=j.outline(ctx,**kw)
    assert empty['physical_definition_id']!=cut['physical_definition_id']
    a=empty['source_finished_successors'][0]['material_properties'];b=cut['source_finished_successors'][0]['material_properties']
    assert a['net_volume_interval_m3'][0]-b['net_volume_interval_m3'][0]==pytest.approx(pi*.001**2*.025)
    assert not cut['manufacturing_definition']['prior_inventory_authenticated']
    assert 'held' in cut['manufacturing_definition']['state']
    assert before[0]==ctx and before[1]['existing_cuts'][name]==[]


@pytest.mark.parametrize('side,hx',[(s,x) for s in (-1,1) for x in (-.4,.5)])
def test_new_build_completes_future_voids_without_surveying_old_hardware(side,hx):
    ctx,kw=new_build_fixture(side,hx);before=deepcopy((ctx,kw));out=j.outline(ctx,**kw)
    assert (ctx,kw)==before and len(out['parts'])==38 and len(out['source_finished_successors'])==2
    m=out['manufacturing_definition'];assert m['mode']=='new-build-drawing' and m['prior_physical_cut_roster'] is None and m['measured_hole_free'] is False
    for row in out['source_finished_successors']:
        assert row['complete_future_drawing'] and row['geometry']['complete_void_model']
        assert row['prior_physical_cut_roster'] is None and not row['measured_hole_free']
        assert row['disposition']=='finish-new-source-blank-once' and not row['canonical_composition_applied']
        assert row['gross_budget']['quantity_transferred']==1 and row['gross_budget']['additional_raw_material_purchase_USD']==0
        assert row['material_properties']['placement_uncertainty_m']==.01
        assert not row['native_geometry_supported']
    assert out['stack']['minimum_engagement_after_0p3mm_budget_m']==pytest.approx(.0057)
    assert out['stack']['backweb_after_0p3mm_budget_m']==pytest.approx(.0007)
    assert out['source_machining_process']['hours']==pytest.approx(1.1)
    assert out['source_machining_process']['cost_USD']==pytest.approx([6.6,11.,17.6])


def test_new_build_transfers_source_blank_and_direct_budget_once_and_only_adds_process():
    ctx,kw=new_build_fixture();out=j.outline(ctx,**kw)
    for row,key,V,m in zip(out['source_finished_successors'],('endplate','cleat'),(.0009,.00036),(2.394,2.826)):
        b=row['gross_budget'];assert b['volume_m3']==pytest.approx(V);assert b['mass_kg']['base']==pytest.approx(m)
        assert b['direct_allowance_USD']==ctx[key]['direct_cost_each_usd']
        assert b['physical_refund_or_salvage_credit_USD']==0 and not b['transfer_applied_to_live_body']
        assert b['total_successor_direct_USD']=={k:ctx[key]['direct_cost_each_usd'][k]+b['additional_process_QA_USD'][i] for i,k in enumerate(('low','base','high'))}
    assert set(x['part_id'] for x in out['materials']['rows'])==set(x['id'] for x in out['parts'])
    assert all(x['id'] not in {ctx['endplate']['id'],ctx['cleat']['id']} for x in out['parts'])
    assert out['source_ownership']['old_joinery_mass_credit'] is None


def test_complete_new_base_feature_requires_its_positive_process_and_changes_physical_identity():
    ctx,kw=new_build_fixture();a=j.outline(ctx,**kw);name=ctx['endplate']['id'];t=kw['manufacturing']['targets'][name]
    t['base_voids']=[dict(axis=1,at_m=[.020,0.,.010],radius_m=.001,length_m=.025)]
    with pytest.raises(ValueError,match='positive'):j.outline(ctx,**kw)
    t.update(base_void_process_h=.05,base_void_QA_h=.02);b=j.outline(ctx,**kw)
    assert a['physical_definition_id']!=b['physical_definition_id'] and a['manufacturing_definition_id']!=b['manufacturing_definition_id']
    V=pi*.001**2*.025;m=b['source_finished_successors'][0]['material_properties']
    assert m['local_volume_first_moment_interval_m4'][0]==pytest.approx([-V*.020]*2)
    assert m['local_volume_first_moment_interval_m4'][2]==pytest.approx([-V*.010]*2)
    assert b['source_machining_process']['hours']-a['source_machining_process']['hours']==pytest.approx(.07)


def test_void_union_order_duplicates_and_redundant_coaxial_cuts_have_one_physical_identity():
    ctx,kw=new_build_fixture();t=kw['manufacturing']['targets'][ctx['endplate']['id']]
    a=dict(axis=1,at_m=[.020,0.,.010],radius_m=.002,length_m=.025);small=deepcopy(a);small['radius_m']=.001
    t.update(base_voids=[a,small,a],base_void_process_h=.05,base_void_QA_h=.02);x=j.outline(ctx,**kw)
    t['base_voids']=[small,a];y=j.outline(ctx,**kw)
    assert x['physical_definition_id']==y['physical_definition_id']
    assert j.normalize_void_union([a,small,a],[.2,.025,.18])==j.normalize_void_union([small,a],[.2,.025,.18])
    assert j.normalize_void_union(j.normalize_void_union([a,small,a],[.2,.025,.18]),[.2,.025,.18])==j.normalize_void_union([a],[.2,.025,.18])


def test_unknown_existing_roster_is_distinct_from_complete_future_drawing():
    ctx,kw=new_build_fixture();future=j.outline(ctx,**kw);kw.pop('manufacturing');old=j.outline(ctx,**kw)
    assert old['physical_definition_id']!=future['physical_definition_id']
    assert all(r['material_properties'] is None and not r['geometry']['complete_void_model'] for r in old['source_finished_successors'])
    assert all(r['prior_physical_cut_roster'] is None for r in future['source_finished_successors'])
    assert old['source_machining_process']['hours']==future['source_machining_process']['hours']


def test_new_build_finite_corner_is_not_inherited_by_existing_hardware_mode():
    ctx,kw=new_build_fixture();new=j.outline(ctx,**kw)
    kw['existing_cuts']={ctx[k]['id']:[] for k in ('endplate','cleat')}
    inventory={n:dict(source_record_id=ctx['source_record_ids'][n],prior_void_union_id=j.identity([]),inventory_revision_id='a'*64,evidence_origin_id='c'*64,complete=True) for n in kw['existing_cuts']}
    kw['manufacturing']=dict(mode='modify-authenticated-existing',prior_inventory_binding=inventory,thread_specification=j.thread_drawing());existing=j.outline(ctx,**kw)
    assert existing['manufacturing_definition']['prior_inventory_authenticated']
    assert existing['physical_definition_id']!=new['physical_definition_id']
    assert existing['source_finished_successors'][1]['material_properties']['finite_corner_hypothesis_applied'] is False
    assert existing['manufacturing_definition_id']!=new['manufacturing_definition_id'] and existing['evaluation_id']!=new['evaluation_id']
    assert not existing['physical_accepted'] and not new['physical_accepted']


@pytest.mark.parametrize('change',['state','measured','prior','target','stale','incomplete','pitch','fit','runout','extra','oldroster','mass','quantity','price'])
def test_new_drawing_contract_mismatch_refuses_without_input_mutation(change):
    ctx,kw=new_build_fixture();m=kw['manufacturing'];t=m['targets'][ctx['endplate']['id']]
    if change=='state':m['state']='installed'
    elif change=='measured':m['measured_hole_free']=True
    elif change=='prior':m['prior_physical_cut_roster']=[]
    elif change=='target':m['targets']['phantom']=deepcopy(t)
    elif change=='stale':t['source_record_id']='a'*64
    elif change=='incomplete':t['complete_future_roster']=False
    elif change=='pitch':m['thread_specification']['pitch_m']=.001
    elif change=='fit':m['thread_specification']['internal_fit_hypothesis']='unknown'
    elif change=='runout':m['thread_specification']['runout_depth_interval_m']=[.007,.009]
    elif change=='extra':m['waive_old_holes']=True
    elif change=='oldroster':kw['existing_cuts'][ctx['endplate']['id']]=[]
    else:
        c=ctx['endplate']
        if change=='mass':c['mass_each_kg']['base']+=1
        elif change=='quantity':c['quantity']=2
        else:c['direct_cost_each_usd']['base']=0
        ctx['source_record_ids'][c['id']]=j.identity(c);kw['source_binding']['context_id']=j.identity(ctx);t['source_record_id']=ctx['source_record_ids'][c['id']]
    before=deepcopy((ctx,kw))
    with pytest.raises(ValueError):j.outline(ctx,**kw)
    assert (ctx,kw)==before


@pytest.mark.parametrize('change',['missing','unknown','stale','revision','extra'])
def test_existing_inventory_binding_cannot_be_replaced_by_new_build_evidence(change):
    ctx,kw=new_build_fixture();kw['existing_cuts']={ctx[k]['id']:[] for k in ('endplate','cleat')}
    inv={n:dict(source_record_id=ctx['source_record_ids'][n],prior_void_union_id=j.identity([]),inventory_revision_id='a'*64,evidence_origin_id='b'*64,complete=True) for n in kw['existing_cuts']}
    kw['manufacturing']=dict(mode='modify-authenticated-existing',prior_inventory_binding=inv,thread_specification=j.thread_drawing());name=ctx['endplate']['id']
    if change=='missing':inv.pop(name)
    elif change=='unknown':kw['existing_cuts'][name]=None
    elif change=='stale':inv[name]['prior_void_union_id']='0'*64
    elif change=='revision':inv[name]['inventory_revision_id']='assumed'
    else:kw['manufacturing']['state']='budget-only, unmanufactured'
    before=deepcopy((ctx,kw))
    with pytest.raises(ValueError):j.outline(ctx,**kw)
    assert (ctx,kw)==before


@pytest.mark.parametrize('cut',[dict(axis=True,at_m=[0.,0.,0.],radius_m=.001,length_m=.01),dict(axis=1,at_m=[True,0.,0.],radius_m=.001,length_m=.01),dict(axis=1,at_m=[0.,0.,0.],radius_m=float('nan'),length_m=.01),dict(axis=1,at_m=[.100,0.,0.],radius_m=.001,length_m=.025),dict(axis=0,at_m=[0.,0.,0.],radius_m=.001,length_m=.01)])
def test_future_void_domain_bool_nonfinite_escape_and_wrong_axis_fail(cut):
    before=deepcopy(cut)
    with pytest.raises(ValueError):j.normalize_void_union([cut],[.2,.025,.18])
    #NaN equality is not an integrity test; serialised representation is.
    assert repr(cut)==repr(before)


def test_complete_material_union_and_moment_bounds_use_pilot_plus_nonoverlapping_major_region():
    ctx,kw=new_build_fixture(-1);out=j.outline(ctx,**kw);al,steel=out['source_finished_successors'];g=steel['geometry'];m=steel['material_properties']
    vp=4*pi*.0034**2*.009;corner=.00005;vlow=4*pi*(.0034**2*(.009-corner)+(.0034-corner)**2*corner);extra=4*pi*(.004**2-.0034**2)*.007
    assert m['minimum_void_volume_m3']==pytest.approx(vlow) and m['maximum_void_volume_m3']==pytest.approx(vp+extra)
    assert m['net_volume_interval_m3']==pytest.approx([.00036-vp-extra,.00036-vlow])
    assert m['mass_interval_kg']==pytest.approx([(.00036-vp-extra)*7850,(.00036-vlow)*7850])
    assert m['minimum_void_volume_m3']<sum(pi*c['radius_m']**2*c['length_m'] for c in g['minimum_void_union']+g['maximum_void_union'])
    assert 'not independent realizable' in m['interval_method'] and not m['exact_helix_or_thread_centroid_claimed']
    assert all(a<=b for a,b in m['local_volume_first_moment_interval_m4'])
    assert m['source_frame_centroid_interval_m'][1][0]<ctx['cleat']['at_m'][1]<m['source_frame_centroid_interval_m'][1][1]
    assert 'not exact finished tensor' in m['inertia_proxy_about_source_origin']['method']


def test_pure_rates_qualifications_and_inventory_origins_do_not_change_physical_identity():
    ctx,kw=new_build_fixture();a=j.outline(ctx,**kw);kw['material_policy']['labour_USD_h']=[7.,11.,17.];b=j.outline(ctx,**kw)
    assert a['physical_definition_id']==b['physical_definition_id'] and a['evaluation_id']!=b['evaluation_id']
    assert a['manufacturing_definition_id']==b['manufacturing_definition_id']
    assert all(not x['canonical_composition_applied'] for x in b['source_finished_successors'])


@pytest.mark.parametrize('side',[-1,1])
def test_finite_corner_lower_steps_and_unchanged_upper_cylinder_conserve_both_moments(side):
    ctx,kw=new_build_fixture(side);out=j.outline(ctx,**kw);r=out['source_finished_successors'][1];m=r['material_properties'];g=r['geometry'];rho=7850.
    assert g['thread_specification']['flat_bottom_corner_radius_hypothesis_m']==.00005
    assert len(g['minimum_void_union'])==8 and len(out['machining'][1]['new_pilots_or_through_cuts'])==4
    assert out['machining'][1]['new_pilots_or_through_cuts'][0]['length_m']==.009
    assert m['finite_corner_hypothesis_applied'] and not m['tool_corner_authenticated']
    for bound,cuts in zip(m['bounding_shape_conservation'],(g['minimum_void_union'],g['maximum_void_union'])):
        volume=sum(pi*c['radius_m']**2*c['length_m'] for c in cuts)
        moment=[sum(pi*c['radius_m']**2*c['length_m']*c['at_m'][k] for c in cuts) for k in range(3)]
        assert bound['void_volume_m3']==pytest.approx(volume)
        assert bound['net_volume_m3']+volume==pytest.approx(.00036)
        assert bound['net_local_first_moment_m4']==pytest.approx([-x for x in moment])
        assert bound['net_local_mass_first_moment_kg_m']==pytest.approx([-rho*x for x in moment])
        assert bound['mass_kg']==pytest.approx(bound['net_volume_m3']*rho)
    assert m['minimum_void_volume_m3']<out['machining'][1]['nominal_ideal_cylinder_incremental_removed_bounds_m3'][0]
    for row in out['machining']:assert sum(row['process_breakdown_h'].values())==pytest.approx(row['process_h'])


def test_provenance_only_inventory_evidence_change_preserves_geometry_identity():
    ctx,kw=new_build_fixture();kw['existing_cuts']={ctx[k]['id']:[] for k in ('endplate','cleat')}
    inv={n:dict(source_record_id=ctx['source_record_ids'][n],prior_void_union_id=j.identity([]),inventory_revision_id='a'*64,evidence_origin_id='b'*64,complete=True) for n in kw['existing_cuts']}
    kw['manufacturing']=dict(mode='modify-authenticated-existing',prior_inventory_binding=inv,thread_specification=j.thread_drawing())
    a=j.outline(ctx,**kw);inv[ctx['endplate']['id']]['evidence_origin_id']='c'*64;b=j.outline(ctx,**kw)
    assert a['physical_definition_id']==b['physical_definition_id']
    assert a['manufacturing_definition_id']!=b['manufacturing_definition_id'] and a['evaluation_id']!=b['evaluation_id']


def test_unrecognised_gross_geometry_features_and_unordered_budget_refuse_new_build():
    for what in ('unknown-feature','source-stock','unordered-budget'):
        ctx,kw=new_build_fixture();c=ctx['endplate']
        if what=='unknown-feature':c['geometry']['hidden_void']=dict(radius_m=.001)
        elif what=='source-stock':c['geometry']['source_stock']=dict(kind='box',size_m=[.2,.01,.18])
        else:c['direct_cost_each_usd']={'low':43.,'base':19.,'high':8.}
        ctx['source_record_ids'][c['id']]=j.identity(c);kw['source_binding']['context_id']=j.identity(ctx)
        t=kw['manufacturing']['targets'][c['id']];t.update(source_record_id=ctx['source_record_ids'][c['id']],gross_geometry_id=j.identity(c['geometry']))
        with pytest.raises(ValueError):j.outline(ctx,**kw)


def test_QA_method_is_not_physical_geometry_and_nominal_tolerance_scope_is_explicit(monkeypatch):
    ctx,kw=new_build_fixture();a=j.outline(ctx,**kw);spec=deepcopy(j.THREAD_DRAWING);spec['inspection']['method']='Different research QA documentation; no shape change'
    monkeypatch.setattr(j,'THREAD_DRAWING',spec);kw['manufacturing']['thread_specification']=deepcopy(spec);b=j.outline(ctx,**kw)
    assert a['physical_definition_id']==b['physical_definition_id']
    assert a['manufacturing_definition_id']!=b['manufacturing_definition_id']
    for x in b['source_finished_successors']:
        assert x['material_properties']['nominal_dimensions_only']
        assert x['material_properties']['manufacturing_dimensional_tolerances_in_material_interval'] is False
