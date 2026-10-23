"""Counted variant identity, replacement costs, energy and finance boundaries."""
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import subprocess

import pytest
from engineering.ferrite_maglev import pilot_variants as v,pilot_actuators as a,pilot_corridor as p,model

@pytest.fixture(scope='module')
def candidate():
    values=v.load();return a.variant_configuration(values['body_variant'],values['winding_variant'])

def test_exact_component_mass_and_cost_changes_reconcile(candidate):
    cfg,drive=candidate;r=v.component_changes(cfg,drive);rows={row['id']:row for row in r['rows']}
    assert r['incremental_mass_kg_per_car']==pytest.approx(1565.324752132813)
    winding_copper=72*140*(.120+.080+.300+.200)*20e-6*8960
    assert winding_copper==pytest.approx(1264.4352)
    assert rows['additional-winding-copper']['mass_change_kg_per_car']==pytest.approx(winding_copper-262.176768)
    assert rows['additional-cooling']['mass_change_kg_per_car']==120 and rows['additional-cooling']['additional_cost_usd_per_car']==7200
    assert rows['detachable-collector-splices']['mass_change_kg_per_car']==pytest.approx(106.01367954281218)
    assert rows['detachable-collector-splices']['hardware_counts_per_car']['new_splice_plates']==96
    assert rows['detachable-collector-splices']['hardware_counts_per_car']['new_m8_bolts']==384
    assert r['additional_non_vehicle_tooling_usd']==3000 and not r['tooling']['fixture_is_onboard_mass']
    stage_rows,aux=v.power_stage_changes(cfg)
    assert sorted((r['priced_quantity_per_car'],r['unit_mass_kg'],r['unit_rate_usd']) for r in stage_rows)==[(24,.25,100.),(24,2.,1000.)]
    assert sum(r['mass_change_kg_per_car'] for r in stage_rows)==54
    assert sum(r['additional_cost_usd_per_car'] for r in stage_rows)==26400 and aux==1.
    assert r['removed_gfrp_cost_credit_usd']==0 and r['mass_and_cost_are_distinct_ledgers']
    cfg=deepcopy(cfg);cfg['controlled_aw3_kg']+=1
    with pytest.raises(ValueError,match='mass changes'):v.component_changes(cfg,drive)

def test_energy_is_component_i_squared_r_and_not_mixed_rust_heat(candidate):
    cfg,drive=candidate;r=v.component_changes(cfg,drive)['energy'];coil=v.drive_design.support(drive)['coil']
    assert r['support_continuous_copper_ceiling_kw_per_car']==pytest.approx(72*60**2*coil['resistance_hot_ohm']/1000)
    assert r['cooling_auxiliary_kw_per_car']==pytest.approx(24*15/1000)
    assert r['power_stage_auxiliary_kw_per_car']==1.
    assert r['additional_services_kw_per_car']==pytest.approx(r['support_continuous_copper_ceiling_kw_per_car']+24*15/1000+1.)
    assert r['additional_services_kw_per_car']>19 and r['source_hotel_removed_kw']==0
    assert not r['base_hotel_support_split_known']

def test_power_stage_rows_reject_missing_or_inconsistent_equipment(candidate):
    cfg,_=candidate;broken=deepcopy(cfg);broken['support_power_stage']['components'][0]['count_per_car']-=1
    with pytest.raises(ValueError,match='component totals'):v.power_stage_changes(broken)
    broken=deepcopy(cfg);del broken['support_power_stage']['components']
    with pytest.raises(ValueError,match='component split'):v.power_stage_changes(broken)
    broken=deepcopy(cfg);broken['support_power_stage']['additional_auxiliary_kw_per_car']=float('nan')
    with pytest.raises(ValueError,match='auxiliary power'):v.power_stage_changes(broken)

def test_cost_rate_changes_do_not_modify_physical_candidate_mass(candidate):
    cfg,drive=candidate;a=v.load();original=v.component_changes(cfg,drive,a);a['fabricated_steel_usd_per_kg']*=2;changed=v.component_changes(cfg,drive,a)
    assert changed['incremental_mass_kg_per_car']==original['incremental_mass_kg_per_car']
    assert changed['additional_component_cost_usd_per_car']-original['additional_component_cost_usd_per_car']==pytest.approx(original['rows'][0]['additional_cost_usd_per_car'])

def test_exact_executed_groups_are_priced_without_cheaper_substitution(candidate,monkeypatch):
    cfg,drive=candidate;captured={}
    def loss(profile,**values):
        captured.update(values);return dict(feasible=False,controlled_mass_matches=True,candidate={k:values[k] for k in cfg['wayside_drive']},limits=dict(voltage=False))
    monkeypatch.setattr(v.launch,'loss_model',loss);result=v.selected_launch({},cfg,drive)
    assert {k:captured[k] for k in cfg['wayside_drive']}==cfg['wayside_drive']
    assert captured['_context'][2]['configuration_sha256']==cfg['configuration_sha256']
    assert result['candidate_count']==1 and result['selected'] is None
    assert not result['independent_optimum_substituted']

def test_component_addition_reprices_procurement_cash_and_repayment():
    a=p.load();monthly=[dict(month=i+1,capex_usd=1e8/12) for i in range(12)];base=dict(vehicle_fleet_allowance_usd=1e7,capital_with_reserve_usd=1e8,annual_opex_usd=4e6,synthetic_daily_paid_trips=10000.,finance=p.finance(1e8,4e6,10000,monthly,a=a),platform_budget=dict(compact_capital_sensitivity_usd=9e7),factory_startup_funding=dict(pooled_budget_usd=1e8,standalone_budget_usd=1.02e8))
    changes=dict(additional_component_cost_usd_per_car=1000.,rows=[]);r=v.apply_component_costs(base,changes,10,a);rates=model.load()[2]['rates'];delta=1000*60*(1+rates['vehicle_integration_reserve_fraction'])*1.3
    assert base['capital_with_reserve_usd']==1e8 and r['capital_with_reserve_usd']==pytest.approx(1e8+delta)
    assert sum(row['capex_usd'] for row in r['finance']['monthly_construction_cash'])==pytest.approx(1e8+delta)
    assert r['finance']['debt_principal_usd']==pytest.approx((1e8+delta)*.6)
    assert r['annual_opex_usd']==pytest.approx(4e6+delta*.02)

def test_independent_service_screen_rejects_unsafe_window_and_dispatch():
    run=p.service(line=p.city_line());assert all(v.service_screens(run).values())
    broken=deepcopy(run);broken['events'][0]['battery_after_kwh']=0
    assert not v.service_screens(broken)['battery_window']
    broken=deepcopy(run);broken['events'][0]['start_s']=run['horizon_s']
    assert not v.service_screens(broken)['finite_dispatch']

def test_failed_control_or_different_control_identity_holds_candidate():
    cfg=dict(configuration_sha256='exact-candidate');execution=dict(all_negative_controls_held=True,qualified_configuration_sha256='exact-candidate',control_configuration_sha256='exact-candidate')
    assert v.exact_controls_held(execution,cfg)
    execution['all_negative_controls_held']=False;assert not v.exact_controls_held(execution,cfg)
    execution['all_negative_controls_held']=True;execution['control_configuration_sha256']='cheaper-old-case';assert not v.exact_controls_held(execution,cfg)

def test_actual_force_limit_and_unknown_block_full_profile_confirmation():
    profile=dict(exact_tested_profile=True);execution=dict(study_pass=True,any_full_candidate_feasible=True,full_duration=True,completed_moving_steps=10,planned_moving_steps=10,profile=profile,profile_sha256=sha256(v.encoded(profile)).hexdigest())
    execution['actual_module_force']=v.pilot_limits.actual_module_force(dict(extrema=dict(peak_module_force_n=20000.)))
    assert v.confirmed_profile(execution,profile)
    execution['actual_module_force']=v.pilot_limits.actual_module_force(dict(extrema=dict(peak_module_force_n=20000.01)))
    assert execution['actual_module_force']['state']=='failed' and not v.confirmed_profile(execution,profile)
    execution['actual_module_force']=v.pilot_limits.actual_module_force({})
    assert execution['actual_module_force']['state']=='hold' and not v.confirmed_profile(execution,profile)

def test_nominal_pass_cannot_override_failed_or_missing_full_profile_sensitivity():
    profile=dict(exact_tested_profile=True);execution=dict(study_pass=True,any_full_candidate_feasible=True,full_duration=True,completed_moving_steps=10,planned_moving_steps=10,profile=profile,profile_sha256=sha256(v.encoded(profile)).hexdigest(),actual_module_force=v.pilot_limits.actual_module_force(dict(extrema=dict(peak_module_force_n=19000.))))
    assert v.confirmed_profile(execution,profile)
    for state in (False,None,1):
        execution['any_full_candidate_feasible']=state
        assert not v.confirmed_profile(execution,profile)
    del execution['any_full_candidate_feasible']
    assert not v.confirmed_profile(execution,profile)

def test_executed_candidate_retains_producer_full_profile_gate(monkeypatch):
    cfg=dict(configuration_sha256='exact');profile=dict(inputs=dict(runtime_s=1.))
    run=dict(configuration_sha256='exact',profile=profile,profile_sha256=sha256(v.encoded(profile)).hexdigest(),study_pass=True,failure=None,screens=dict(gap=True),completed_moving_steps=1000,planned_moving_steps=1000,requested_duration_s=1.,extrema=dict(peak_module_force_n=19000.),scope='test')
    cases=[dict(estimator_scale=.9,study_pass=False),dict(estimator_scale=1.,study_pass=True),dict(estimator_scale=1.1,study_pass=True)]
    status=dict(any_full_candidate_feasible=False,applicable_full_cases=cases,all_negative_controls_held=True,qualified_configuration_sha256='exact',control_configuration_sha256='exact')
    monkeypatch.setattr(a,'verify',lambda:status);monkeypatch.setattr(a,'validate_run',lambda _:None)
    monkeypatch.setattr(v.product,'verify_packet',lambda *args:({},dict(repair_candidates=[run])))
    result=v.current_actuator_candidate(cfg)
    assert result['study_pass'] and result['applicable_full_cases']==cases and result['any_full_candidate_feasible'] is False
    assert not v.confirmed_profile(result,profile)

def test_gross_box_audit_rejects_inherited_volume_without_claiming_net_material():
    definition=dict(retained_parts=[dict(id='segmented-collector',kind='box',size_m=[.99,.006,.08],at_m=[10.,20.,30.],volume_m3=12*.006*.08),dict(id='drilled-part',kind='box',size_m=[1.,.1,.1],volume_m3=.009)],fixed_parts=[],equipment=[dict(id='packaging',kind='box',size_m=[1.,.2,.1])])
    before=deepcopy(definition);audit=v.part_volume_audit(definition);rows={r['id']:r for r in audit['rows']}
    assert definition==before and audit['inherited_volume_exceeds_bound_ids']==['segmented-collector']
    assert rows['segmented-collector']['gross_bound_volume_m3']==pytest.approx(.0004752)
    assert rows['segmented-collector']['inherited_reported_net_volume_m3']==pytest.approx(.00576)
    assert not rows['drilled-part']['inherited_net_exceeds_placed_gross']
    assert all(r['net_manufactured_volume_m3'] is None and not r['net_solid_reconciled'] for r in rows.values())
    assert audit['state']=='hold' and not audit['mass_or_cost_removal_credit_applied']

def test_current_candidate_volume_audit_preserves_independent_net_solid_hold():
    definition=a.candidate_packaging(v.load()['winding_variant'])['definition'];audit=v.part_volume_audit(definition)
    collector_rows=[row for row in audit['rows'] if 'collector' in row['id']]
    assert collector_rows and all(row['gross_bound_volume_m3']>0 for row in collector_rows)
    assert all(row['net_manufactured_volume_m3'] is None for row in collector_rows)
    assert audit['state']=='hold' and not audit['mass_or_cost_removal_credit_applied']
    assert not v.volume_audit_summary(audit)['net_manufacturing_quantities_reconciled']

def test_actual_larger_candidate_animation_is_bound_to_geometry_and_events(candidate,tmp_path):
    from PIL import Image
    import io
    cfg,_=candidate;definition=a.candidate_packaging(v.load()['winding_variant'])['definition'];compressed=gzip.compress(v.encoded(definition),mtime=0)
    coils=[part for part in definition['equipment'] if part['id'].startswith('bay/coil-')]
    assert len(coils)==3 and all(part['size_m']==[.300,.200,.075] for part in coils)
    payload=v.render_candidate_media(cfg,definition,compressed)
    for name,data in payload.items():(tmp_path/name).write_bytes(data)
    v.verify_candidate_media(tmp_path,cfg,definition,compressed)
    events=json.loads(payload[v.MEDIA['events']]);receipt=json.loads(payload[v.MEDIA['receipt']]);description=v.media_description(cfg,definition,compressed)
    assert events['definition_sha256']==sha256(v.encoded(definition)).hexdigest()==receipt['source_geometry_sha256']==description['definition_sha256']
    assert receipt['configuration_sha256']==cfg['configuration_sha256'] and receipt['canonical_definition_gzip_sha256']==sha256(compressed).hexdigest()
    assert len(events['frames'])==receipt['frames']==description['frames']==41
    assert events['frames'][0]['translation_m']==[0.,0.,0.] and events['frames'][-1]['translation_m']==[0.,.9,0.]
    assert events['physical_motion_measurements'] is False and all(receipt[key] is False for key in v.FLAGS)
    assert description['physical_accepted'] is False
    poster=Image.open(io.BytesIO(payload[v.MEDIA['poster']])).convert('RGB');background=(16,28,43)
    assert poster.getpixel((453,0))==background
    assert all(poster.getpixel((0,y))==background and poster.getpixel((1099,y))==background for y in range(650))
    assert receipt['viewport']['pixel_clip_bounds']==[40.,90.,1060.,520.]
    probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames','-of','json',str(tmp_path/v.MEDIA['video'])],capture_output=True,text=True,timeout=30,check=True)
    stream=json.loads(probe.stdout)['streams'][0]
    assert (stream['codec_name'],stream['width'],stream['height'],stream['r_frame_rate'],stream['nb_read_frames'])==('h264',1100,650,'12/1','41')

def test_same_viewport_smaller_coil_poster_and_video_are_rejected(candidate,tmp_path):
    cfg,_=candidate;definition=a.candidate_packaging(v.load()['winding_variant'])['definition'];compressed=gzip.compress(v.encoded(definition),mtime=0)
    smaller=deepcopy(definition);coils=[part for part in smaller['equipment'] if part['id'].startswith('bay/coil-')]
    assert len(coils)==3
    for part in coils:part['size_m']=[.174,.134,.060]
    assert [part['at_m'] for part in coils]==[part['at_m'] for part in definition['equipment'] if part['id'].startswith('bay/coil-')]
    # Identical renderer, viewport, positions, fixed body and annotation font:
    # the smaller physical coil bounds are the only changed scene definition.
    payload=v.render_candidate_media(cfg,definition,compressed);wrong=v.render_stock_bound_animation(smaller,cfg['configuration_sha256'])
    for role,forgery in [('poster',wrong['bay-poster.png']),('video',wrong['bay-replacement.mp4'])]:
        for name,data in payload.items():(tmp_path/name).write_bytes(data)
        assert forgery!=payload[v.MEDIA[role]]
        (tmp_path/v.MEDIA[role]).write_bytes(forgery)
        receipt=v.visual_receipt(cfg,definition,compressed,(tmp_path/v.MEDIA['poster']).read_bytes(),(tmp_path/v.MEDIA['video']).read_bytes());(tmp_path/v.MEDIA['receipt']).write_bytes(v.encoded(receipt))
        # The video case retains the correct full-size poster. Current source,
        # events and newly refreshed hashes cannot hide either wrong footprint.
        if role=='video':assert (tmp_path/v.MEDIA['poster']).read_bytes()==payload[v.MEDIA['poster']]
        assert receipt['configuration_sha256']==cfg['configuration_sha256']
        with pytest.raises(ValueError,match='geometry/material footprint'):v.verify_candidate_media(tmp_path,cfg,definition,compressed)

def test_media_semantics_survive_different_fonts_and_encoder_and_reject_long_movie(candidate,tmp_path,monkeypatch):
    from PIL import Image,ImageDraw
    import io
    cfg,_=candidate;definition=a.candidate_packaging(v.load()['winding_variant'])['definition'];compressed=gzip.compress(v.encoded(definition),mtime=0)
    payload=v.render_candidate_media(cfg,definition,compressed)
    for name,data in payload.items():(tmp_path/name).write_bytes(data)
    # A different platform/font may alter annotations but not the declared
    # physical viewport. Different H264 encoding must not alter qualification.
    image=Image.open(io.BytesIO(payload[v.MEDIA['poster']])).convert('RGB');draw=ImageDraw.Draw(image);draw.rectangle([0,0,1099,79],fill='#101c2b');draw.text((25,20),'Different available platform font',fill='white');image.save(tmp_path/v.MEDIA['poster'],compress_level=1)
    reencoded=tmp_path/'alternate-encoder.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp_path/v.MEDIA['video']),'-vf','drawbox=x=0:y=0:w=iw:h=80:color=0x101c2b:t=80','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','28',str(reencoded)],capture_output=True,timeout=30,check=True)
    (tmp_path/v.MEDIA['video']).write_bytes(reencoded.read_bytes())
    receipt=v.visual_receipt(cfg,definition,compressed,(tmp_path/v.MEDIA['poster']).read_bytes(),reencoded.read_bytes());(tmp_path/v.MEDIA['receipt']).write_bytes(v.encoded(receipt))
    assert receipt['poster_sha256']!=sha256(payload[v.MEDIA['poster']]).hexdigest() and receipt['video_sha256']!=sha256(payload[v.MEDIA['video']]).hexdigest()
    v.verify_candidate_media(tmp_path,cfg,definition,compressed)
    too_long=tmp_path/'42frames.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-framerate','12','-i',str(tmp_path/v.MEDIA['poster']),'-frames:v','42','-an','-c:v','libx264','-threads','2','-pix_fmt','yuv420p',str(too_long)],capture_output=True,timeout=30,check=True)
    (tmp_path/v.MEDIA['video']).write_bytes(too_long.read_bytes());(tmp_path/v.MEDIA['receipt']).write_bytes(v.encoded(v.visual_receipt(cfg,definition,compressed,(tmp_path/v.MEDIA['poster']).read_bytes(),too_long.read_bytes())))
    with pytest.raises(ValueError,match='metadata exceeds'):v.verify_candidate_media(tmp_path,cfg,definition,compressed)
    # Metadata alone is insufficient. Even a lying frame-count/duration claim
    # cannot hide42real frames or lift the fixed90,090,000byte decoder cap.
    real_run=subprocess.run;decoded=[]
    def lying_metadata(command,*args,**kwargs):
        result=real_run(command,*args,**kwargs)
        if command[0]=='ffprobe':
            metadata=json.loads(result.stdout);metadata['streams'][0].update(nb_frames='41',duration=str(41/12));result.stdout=json.dumps(metadata)
        elif command[0]=='ffmpeg':decoded.append(command)
        return result
    monkeypatch.setattr(subprocess,'run',lying_metadata)
    with pytest.raises(ValueError,match='decoded frame count'):v.verify_candidate_media(tmp_path,cfg,definition,compressed)
    assert decoded and decoded[0][decoded[0].index('-frames:v')+1]=='42' and 'scale=1100:650' in decoded[0]

def test_smaller_reference_cannot_be_used_as_canonical_candidate_geometry(candidate,tmp_path,monkeypatch):
    cfg,_=candidate;monkeypatch.setattr(a,'OUTPUT',tmp_path)
    (tmp_path/'candidate-bay.json.gz').write_bytes(gzip.compress(v.encoded(v.product.redesigned_bay()),mtime=0))
    with pytest.raises(ValueError,match='exact candidate geometry'):v.canonical_bay(cfg)

def test_published_current_candidate_binds_full_profile_and_rejects_rehashed_price(tmp_path,monkeypatch):
    v.publish(tmp_path);value=v.study();original=v.study;calls=[]
    def counted():calls.append(True);return original()
    monkeypatch.setattr(v,'study',counted);summary=v.read_summary(tmp_path)
    assert len(calls)==1
    assert summary['configuration_sha256']==value['actuator_execution']['configuration_sha256']
    assert summary['base_configuration_sha256']!=summary['configuration_sha256']
    assert not summary['automatic_adoption'] and not summary['system_qualified']
    if summary['full_coupled_profile_confirmed']:
        assert value['actuator_execution']['profile_sha256']==value['launch_search']['selected']['profile_sha256']
        assert value['actuator_execution']['completed_moving_steps']==value['actuator_execution']['planned_moving_steps']
    if value['economics'] is not None:value['economics']['capital_with_reserve_usd']=1.
    else:value['system_feasible']=True
    (tmp_path/'study.json.gz').write_bytes(gzip.compress(v.encoded(value),mtime=0));m=json.loads((tmp_path/'manifest.json').read_bytes());m['files_sha256']['study.json.gz']=v.digest(tmp_path/'study.json.gz');(tmp_path/'manifest.json').write_bytes(v.encoded(m))
    with pytest.raises(ValueError,match='recalculation'):v.verify(tmp_path)
