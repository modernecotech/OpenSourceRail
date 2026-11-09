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
    a=dict(header_force_N=[None,None,None],header_moment_Nm=[None,None,None],one_fastener_shear_N=None,one_fastener_tension_N=None,preload_each_N=None)
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
