import gzip,json,hashlib,traceback
from pathlib import Path
from engineering.station_rail.common import digest,identity
from engineering.compact_drive import design
from engineering.railway_project import route,alignment,bundle,station_tracks,civil,drive,motion,compact_drive_corridor as probe
from engineering.pilot_civil import design as pilot_civil
repo=Path('.').resolve(); root=Path('/home/hayder/.local/state/opensourcerail/runs/mapped-corridor-v06-20261109/packages/compact-drive-source-overlay').resolve()
base=Path('/home/hayder/.local/state/opensourcerail/runs/mapped-corridor-v06-20261109/packages');prior=base/'compact-drive-corridor-01';out=base/'compact-drive-corridor-02';out.mkdir(exist_ok=True)
if any(out.iterdir()):raise RuntimeError('Immutable output already exists')
body=json.load(gzip.open(prior/'body.json.gz','rt'));(out/'body.json.gz').write_bytes((prior/'body.json.gz').read_bytes())
source_map={p:digest(root/p) for p in body['source_sha256']};stages=[];routes=[];holds=[];artifacts=[];compile_diags=[]
service_cases={'baghdad':dict(peak_demand_pphpd=8000,maximum_headway_s=180,planning_occupancy=.8,planning_availability_assumption=.9,operating_hours_per_day=18,operating_days_per_year=330),'samawah':dict(peak_demand_pphpd=1200,maximum_headway_s=300,planning_occupancy=.8,planning_availability_assumption=.9,operating_hours_per_day=16,operating_days_per_year=300)}
scopes={'baghdad':('line-1','line-1-2500-0775-s000000','line-1-2180-0774-s007014'),'samawah':('line-3','line-3-0459-0690-s000000','line-3-0484-0261-s008799')}
lay=body['policy']['layout'];L=lay['cars']*lay['car_length_m']+(lay['cars']-1)*lay['intercar_gap_m']
params=dict(platform_straight_m=300.,train_length_m=L,platform_end_margin_m=6.,requested_speed_m_s=16.6666666667,lateral_acceleration_target_m_s2=.6,lateral_jerk_target_m_s3=.5,longitudinal_acceleration_bound_m_s2=.8,maximum_deviation_m=205.)
for city,(line,first,last) in scopes.items():
 r={'city_slug':city,'source_line_id':line,'endpoint_ids':[first,last],'scope':'Baghdad first three stops' if city=='baghdad' else 'Samawah first-to-last with all stops'}
 try:
  c=route.from_catalogue(city,line,first,last,root=root)
  r.update(city_input_id=c['source_city_input_id'],planning_revision_id=c['source_planning_revision'],source_stop_ids=[s['id'] for s in c['source_stops']],corridor_evaluation_id=c['evaluation_id'],corridor_geometry_id=c['corridor_geometry_id'],route_m=c['route_m'])
  for p,h in c['source_sha256'].items():
   if digest(root/p)!=h:raise ValueError('route source mismatch: '+p)
   source_map[p]=h
  a=alignment.generate(c,root=root,**params)
  for p,h in a['source_sha256'].items():
   if digest(root/p)!=h:raise ValueError('alignment source mismatch: '+p)
   source_map[p]=h
  r.update(alignment_candidate_id=a['candidate_id'],alignment_evaluation_id=a['evaluation_id'],alignment_screen_passed=a['calculated_alignment_screen_passed'],alignment_route_m=a['route_m'])
  (out/f'route-{city}.json').write_text(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n');(out/f'alignment-{city}.json').write_text(json.dumps(a,sort_keys=True,separators=(',',':'))+'\n');artifacts += [f'route-{city}.json',f'alignment-{city}.json']
  s=bundle.stations(body,a,platform_width_m=3.,track_centres_y_m=[-3.,3.],nominal_boarding_gap_m=.075,stopping_tolerance_m=2.,boarding_length_m=125.,root=root)
  (out/f'station-{city}.json').write_text(json.dumps(s,sort_keys=True,separators=(',',':'))+'\n');artifacts.append(f'station-{city}.json')
  spec=pilot_civil.specification(root)
  t=station_tracks.generate(a,s,running_track_centres_y_m=spec['track_centres_y_m'],transition_length_m=80.,lateral_sway_bound_m=.05,requested_speed_m_s=16.6666666667,longitudinal_acceleration_bound_m_s2=.8,lateral_acceleration_target_m_s2=.6,lateral_jerk_target_m_s3=.5,root=root)
  (out/f'track-{city}.json').write_text(json.dumps(t,sort_keys=True,separators=(',',':'))+'\n');artifacts.append(f'track-{city}.json')
  ax=civil.axle_packet(body,line_equipment=None,root=root)
  span=pilot_civil.evaluate(ax,family='reference_box',revision='source',soil_case='base',root=root)
  sc=service_cases[city]
  cp=civil.count_corridor(span,a,headway_s=sc['maximum_headway_s'],operation_hours_day=sc['operating_hours_per_day'],operation_days_year=sc['operating_days_per_year'],design_life_years=30.,root=root)
  (out/f'civil-span-{city}.json').write_text(json.dumps(span,sort_keys=True,separators=(',',':'))+'\n');(out/f'civil-layout-{city}.json').write_text(json.dumps(cp,sort_keys=True,separators=(',',':'))+'\n');artifacts += [f'civil-span-{city}.json',f'civil-layout-{city}.json']
  p=bundle.combine(body,a,cp,s,station_tracks=t,root=root)
  (out/f'project-{city}.json').write_text(json.dumps(p,sort_keys=True,separators=(',',':'))+'\n');artifacts.append(f'project-{city}.json')
  d=drive.evaluate(body,{},root=root)
  (out/f'drive-{city}.json').write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n');artifacts.append(f'drive-{city}.json')
  places=276;cap=places*sc['planning_occupancy']*3600/sc['maximum_headway_s']
  r.update(station_candidate_id=s['candidate_id'],station_evaluation_id=s['evaluation_id'],station_count=s['quantities']['stations'],boarding_faces=s['quantities']['boarding_faces'],track_candidate_id=t['candidate_id'],track_evaluation_id=t['evaluation_id'],track_quantities=t['quantities'],civil_candidate_id=cp['candidate_id'],civil_evaluation_id=cp['evaluation_id'],civil_quantities=cp['quantities'],project_candidate_id=p['candidate_id'],project_evaluation_id=p['evaluation_id'],drive_evaluation_id=d['evaluation_id'],drive_simulation_definition=d['simulation_definition'],drive_unknown_inputs=[h.get('field') for h in d['definition_holds'] if h.get('kind')=='unknown-sizing-input'],service_assumption=dict(normal_places_per_train=places,demand_pphpd=sc['peak_demand_pphpd'],max_headway_s=sc['maximum_headway_s'],occupancy=sc['planning_occupancy'],nominal_capacity_pphpd=cap,capacity_screen_pass=cap>=sc['peak_demand_pphpd'],dwell_s=None,full_tail_clearance_m=None,grade_profile=None,charging_duty=None,reserve_fleet=None,assumption_only=True))
  stages.extend([{'kind':'project-bundle','city_slug':city,'packet':p},{'kind':'drive-duty','city_slug':city,'candidate_id':d['candidate_id'],'evaluation_id':d['evaluation_id'],'simulation_definition':d['simulation_definition'],'definition_holds':d['definition_holds']}])
  scenario=dict(load_state='normal',mass_case='base',grade_fraction=0.,grade_observation_fraction=0.,headwind_m_s=0.,speed_cap_m_s=16.6666666667,rolling_coefficient=.003,air_density_kg_m3=1.2,cd_a_m2=10.,acceleration_request_m_s2=.8,comfort_jerk_m_s3=.5,non_motor_rotating_mass_fraction=.04,brake_force_cap_n=180000.,brake_lower_fraction=.9,adhesion_fraction=.15,adhesion_lower_fraction=.06,brake_latency_s=.3,brake_rise_s=1.,berth_tolerance_m=1.,dt_s=.05,max_time_s=1800.,dwell_s=35.,headway_s=sc['maximum_headway_s'],hotel_power_w_per_car=50000.,train_total_supply_limit_w=3.3e6,assumption_reference='hypothetical zero-grade compile probe; not surveyed route grade',brake_independence_hypothesis='independent-stored-brake-energy-hypothesis',power_loss_at_s=None,failed_drive_fraction=0.,emergency_at_m=None)
  try:motion.compile_case(p,body,a,d,0,scenario,root=root);compile_diags.append({'city_slug':city,'status':'compiled'})
  except Exception as e:compile_diags.append({'city_slug':city,'status':'held','error_type':type(e).__name__,'reason':str(e)})
 except Exception as e:
  r.update(failed_stage='source-route/alignment/station/track/civil/bundle/drive',failure_type=type(e).__name__,failure_reason=str(e));holds.append(f'{city}: {type(e).__name__}: {e}')
 routes.append(r)
if not any(x.get('kind')=='drive-duty' and x.get('simulation_definition')=='ready-under-explicit-hypotheses' for x in stages):holds.append('drive.evaluate returned held with unknown continuous force/electrical/cooling inputs; no route-specific force map is available')
if compile_diags and not any(x['status']=='compiled' for x in compile_diags):holds.append('motion.compile_case failed on exact project/body/drive binding or held drive model; no native input exists')
if not any(x['status']=='compiled' for x in compile_diags):holds.append('Rust native journey/fleet batch skipped because no compiled force-driven motion cases exist')
holds.append('No exact network-service packet exists; 14-scope cost evaluator was not invoked. Cost prices, site utilities, platform power, fleet and recovery remain unknown.')
for p,h in body['source_sha256'].items(): source_map[p]=h
for path in ('engineering/railway_project/compact_drive_corridor.py','engineering/railway_project/drive.py','engineering/railway_project/motion.py','engineering/station_pair/native_bridge.py','engineering/railway_project/cost.py'):source_map[path]=digest(repo/path)
source_map['run-input/baghdad.json']=digest('/home/hayder/.local/state/opensourcerail/runs/mapped-corridor-v06-20261109/requests/baghdad.json');source_map['run-input/samawah.json']=digest('/home/hayder/.local/state/opensourcerail/runs/mapped-corridor-v06-20261109/packages/mapped-corridor-gap-audit/requests/samawah.json')
req={'schema':'osr-source-compact-drive-corridor-request/1','source_commit':'0b32f51f03cba52b2e5cca1aa3892c5f42bf40dd','source_overlay':'compact-drive-source-overlay is git archive at the assigned source commit','body_config_id':'compact-737-h100','candidate_id':body['candidate_id'],'body_evaluation_id':body['evaluation_id'],'parent_candidate_id':body['parent_candidate_id'],'parent_evaluation_id':body['parent_evaluation_id'],'corridors':scopes,'geometry_parameters':params,'service_assumptions':service_cases,'site_facts':{'grade':None,'utilities':None,'ground':None,'land':None},'execution_limits':{'geometry_trials_used':2,'geometry_trial_limit':2,'max_cpu_s_per_geometry_trial':60,'address_space_bytes':1073741824,'native_fleet_batches':0,'max_native_cpu_s':60,'max_native_wall_s':75,'native_skipped':'no compiled force-driven motion cases'},'motion_compile_diagnostics':compile_diags}
req['request_id']=identity(req)
result=probe.packet(body,route_records=routes,stage_records=stages,holds=holds,source_sha256=source_map,service_assumptions=[r['service_assumption'] for r in routes if 'service_assumption' in r]);result['request_id']=req['request_id'];result['motion_compile_diagnostics']=compile_diags;result['evaluation_id']=identity({k:v for k,v in result.items() if k!='evaluation_id'})
(out/'request.json').write_text(json.dumps(req,sort_keys=True,separators=(',',':'))+'\n');(out/'result.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
manifest={'schema':'osr-source-compact-drive-corridor-manifest/1','request_id':req['request_id'],'evaluation_id':result['evaluation_id'],'candidate_id':body['candidate_id'],'body_sha256':digest(out/'body.json.gz'),'request_sha256':digest(out/'request.json'),'result_sha256':digest(out/'result.json'),'artifact_sha256':{n:digest(out/n) for n in artifacts+['body.json.gz']},'source_sha256':source_map,'geometry_trial_count':2,'native_fleet_batch_count':0,'service_complete':False,'cost_complete':False,'engineering_accepted':False,'physical_accepted':False,'selected_reference_changed':False,'manufacturing_release':False,'operating_release':False,'movement_authority':False};manifest['manifest_id']=identity(manifest);(out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(json.dumps({'candidate_id':body['candidate_id'],'body_evaluation_id':body['evaluation_id'],'mass_complete':body['installed_mass_complete'],'route_records':routes,'motion_compile_diagnostics':compile_diags,'holds':holds,'artifact_names':artifacts,'request_id':req['request_id'],'evaluation_id':result['evaluation_id'],'manifest_id':manifest['manifest_id']},indent=2))
