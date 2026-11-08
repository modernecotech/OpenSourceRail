"""Source proposal and synthetic scalar controls; no actual candidate runs."""
from copy import deepcopy
from math import isclose,pi
import pytest
from engineering import terminal_enclosure_joint as j


def test_rigid_research_bindings_correct_post_header_and_glass_axes():
    p=j.recipe()
    for bind in p['terminal_bindings']:
        R=bind['rotation']
        assert all(sum(R[k][i]*R[k][q] for k in range(3))==(1 if i==q else 0) for i in range(3) for q in range(3))
        assert R[0][0]*R[1][1]*R[2][2]==1
    poses=p['local_part_poses']
    assert next(x for x in poses if x['part']=='post')['rotation']==j.ALONG_W
    assert next(x for x in poses if x['part']=='header')['rotation']==j.ALONG_V
    glass=next(x for x in poses if x['part']=='retained-glass')
    assert glass['unchanged_source_size_m']==[1.6,1.1,.012]
    assert [glass['rotation'][i][2] for i in range(3)]==[1.,0.,0.]


def test_exact_replacement_ownership_and_positive_unknowns():
    p=j.recipe();m={x['source_part_id']:x for x in p['source_replacement_ownership']}
    assert m['body/terminal-end-panel-bolt']['old_quantity_per_end']==m['body/terminal-end-panel-bolt']['new_quantity_per_end']==24
    assert m['body/terminal-end-skin']['old_quantity_per_end']==2 and m['body/terminal-end-skin']['new_quantity_per_end']==1
    assert all(not x['retired_source_added_again'] for x in m.values())
    assert p['other_source_ownership']['passage_seals']==dict(source_part_id='body/passage-end-seal',quantity_per_train=10,developed_each_m=7.,changed=False)
    assert p['other_source_ownership']['old_failure']['compression_interval_m']==[-.002,.006]
    assert all(p[k] is False for k in j.FLAGS)
    stocks={x['part_id'].split('/')[-1]:x for x in p['parts']}
    assert stocks['compression-limiter']['quantity_per_end']==24
    assert stocks['frame-crush-sleeve']['quantity_per_end']==24
    assert stocks['panel-crush-sleeve']['quantity_per_end']==24
    assert stocks['M8-body-bolt']['quantity_per_end']==8
    assert stocks['thread-guard']['quantity_per_end']==32
    assert sum(x['quantity_per_end'] for x in p['parts'] if x['stock_kind']=='rhs')==8
    assert p['weld_vent_pattern']['holes_per_RHS_piece']==2
    assert all(path[0]==[0.,0.,0.] for path in p['repair_path_local_m'].values())


def test_clamp_holes_and_body_mounts_have_finite_edge_and_gasket_separation():
    r=j.recipe();s=r['clamp_stations']
    assert len(s)==24 and len({tuple(x['vw_m']) for x in s})==24
    for x in s:
        radial=abs(x['vw_m'][0])-1.175 if x['row']=='post' else abs(x['vw_m'][1])-1.05
        assert isclose(radial,.025)
        assert radial>.012/2+.014/2
        assert .050-radial>.0142/2
    assert len(r['body_mounts'])==4
    holes=[tuple(x) for m in r['body_mounts'] for x in m['body_M8_holes_uvw_m']]
    assert len(holes)==len(set(holes))==8
    # Actual source beam top1.1095m, proposed holes1.07m; bracket lower flat1.03..1.11m.
    assert 1.1095-1.07>.0182/2
    assert min(1.07-1.03,1.11-1.07)>.0085/2


def test_synthetic_compression_necessary_bound_retains_unknown_material_rating():
    # Synthetic dimensions scaled by10; not an actual default assembly execution.
    x=j.compression_bounds(.18,.145,free_tolerance=.002,stop_tolerance=.0005,
        stop_end_parallelism=.0006,each_land_flatness=.001,interstop_deflection=.0015)
    assert x['positive_compression_necessary']
    assert isclose(x['compression_interval_m'][0],.0284)
    assert isclose(x['compression_interval_m'][1],.0416)
    assert x['upper_compression_limit'] is None
    assert not x['engineering_accepted']
    # Bad achieved flatness is a preserved failure, not edited away.
    bad=j.compression_bounds(.18,.145,free_tolerance=.002,stop_tolerance=.0005,
        stop_end_parallelism=.0006,each_land_flatness=.02,interstop_deflection=.0015)
    assert bad['compression_interval_m'][0]<0 and not bad['positive_compression_necessary']
    retained=j.compression_bounds(.18,.13,free_tolerance=.002,stop_tolerance=.0005,
        stop_end_parallelism=.0006,each_land_flatness=.001,interstop_deflection=.0015,
        keeper_thickness=.015,keeper_tolerance=.0005,retention_film=.001,retention_film_tolerance=.0005)
    assert isclose(retained['compression_interval_m'][0],.0284)
    assert isclose(retained['compression_interval_m'][1],.0436)
    assert not retained['engineering_accepted']


def test_synthetic_rib_and_preload_geometry_are_necessary_not_strength_evidence():
    q=j.rib_line_load_bound(.04,.02,.002,.3,.0002,60e9)
    assert q['maximum_line_load_for_allocation_N_m']>0 and q['imposed_line_load_N_m'] is None
    grip=j.clamp_grip([.003,.004,.02,.01],.06,.005,.003,stack_tolerance=.001)
    assert grip['geometric_length_necessary']
    short=j.clamp_grip([.003,.004,.02,.01],.04,.005,.003,stack_tolerance=.001)
    assert not short['geometric_length_necessary'] and short['residual_m']<0
    assert not grip['thread_grade_preload_and_retention_qualified']


def test_synthetic_stock_cut_and_bend_conservation():
    x=j.z_bracket_blank(.05,.05,.05,.008,.004)
    expected=.10+.05-2*.010+pi*.010
    assert isclose(x['net_developed_length_m'],expected)
    c=j.cut_allowance(.30,.34,kerf=.003,trim=.01,reserve=.02)
    assert isclose(c['additional_tail_m'],.007)
    with pytest.raises(ValueError):j.cut_allowance(.30,.31,kerf=.003,trim=.01,reserve=.02)
    plate=j.stock_spec('synthetic',1,'al','drilled-block',net_size_m=[.03,.04,.005],
        gross_blank_size_m=[.034,.044,.005],through_bore_m=.006)
    net=j.geometric_stock_volume(plate,gross=False);gross=j.geometric_stock_volume(plate,gross=True)
    assert 0<net<gross
    b=j.material_cost_bound(net,gross,2700,4,.1,10,.2)
    assert b['scrap_and_reserve_mass_kg']>0 and b['direct_usd']>0
    assert isclose(j.ring_volume(.3,.2,.02,.005),2*(.3+.2)*.02*.005)


def test_input_identity_separates_tools_prices_and_resources_from_physical_recipe():
    p=j.proposal();q=deepcopy(p)
    q['evaluation_inputs']['tool_socket_radius_m']=.030
    q['evaluation_inputs']['price_basis']='another evaluated price hypothesis'
    q['physical_recipe']['parts'][0]['gross_length_m']=3.
    next(x for x in q['physical_recipe']['parts'] if x['stock_kind']=='purchased-allowance')['direct_usd_each']=[100,200,300]
    assert j.identity(j.physical_projection(q))==p['physical_recipe_id']
    assert j.identity({k:v for k,v in q.items() if k!='proposal_input_id'})!=p['proposal_input_id']
    q['physical_recipe']['parts'][0]['material']='another-material'
    assert j.identity(j.physical_projection(q))!=p['physical_recipe_id']


def test_synthetic_positive_thread_loss_is_bounded_and_never_silently_zero():
    x=j.machining_volume_bounds([dict(quantity=2,kind='thread-bore',pilot_diameter_m=.002,
        thread_major_diameter_m=.0025,total_depth_m=.004,thread_depth_m=.002)])
    low,high=x['removed_volume_interval_m3']
    assert 0<low<high and x['unknown_thread_form']


@pytest.mark.parametrize('change',[
    lambda x:x['physical_recipe']['parts'][0].__setitem__('quantity_per_end',3),
    lambda x:x['physical_recipe']['parts'][0].__setitem__('net_length_m',2.1),
    lambda x:x['physical_recipe']['parts'][0]['additional_machining_per_piece'][0].__setitem__('diameter_m',.015),
])
def test_real_quantity_geometry_and_holes_change_physical_recipe(change):
    p=j.proposal();q=deepcopy(p);change(q)
    assert j.identity(j.physical_projection(q))!=p['physical_recipe_id']


def test_three_unexecuted_local_input_requests_have_exact_ids_and_completion_conditions():
    trials=j.trial_inputs()
    assert len(trials)==3
    assert sum(t['request']['cpu_s'] for t in trials)==105
    assert sum(t['request']['private_output_mib'] for t in trials)==30
    for t in trials:
        assert t['input_id']==j.identity({k:v for k,v in t.items() if k!='input_id'})
        assert t['request']['native_jobs']==t['request']['full_body_jobs']==0
        assert t['execution_status']=='proposed-not-run'
        assert t['required_artifacts'] and t['completion_conditions']


@pytest.mark.parametrize('call',[
    lambda:j.rhs_area(.02,.02,.011),lambda:j.sleeve_volume(.01,.012,.02),
    lambda:j.z_bracket_blank(.05,.05,.02,.02,.005),
    lambda:j.rib_line_load_bound(.04,.02,.002,0,.0002,60e9),
    lambda:j.compression_bounds(.018,.0145,free_tolerance=-.1,stop_tolerance=0,
        stop_end_parallelism=0,each_land_flatness=0,interstop_deflection=0),
])
def test_bad_definitions_preserved_as_failures(call):
    with pytest.raises(ValueError):call()
