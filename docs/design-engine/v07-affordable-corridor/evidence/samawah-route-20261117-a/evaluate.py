import gzip, hashlib, json, math, subprocess, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[3]
RAW=Path('/home/hayder/.local/state/opensourcerail/v07-samawah-20261112/run-02/city-studies/fe6565fc139649b4a1d1b81fd3191765/artifacts')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def seal(v,key):
 v[key]=hashlib.sha256(canon(v)).hexdigest();return v
def write(n,v):
 (HERE/n).write_bytes(canon(v)+b'\n')
start=time.monotonic()
manifest=json.loads((RAW/'manifest.json').read_text())
for n,h in manifest['files_sha256'].items():
 assert sha(RAW/n)==h,('payload mismatch',n)
milestone_blob=subprocess.check_output(['git','show','HEAD:docs/design-engine/v07-project-continuity/samawah-milestone.json'],cwd=ROOT)
milestone=json.loads(milestone_blob)
assert milestone['identities']['after']['manifest_id']==manifest['manifest_id']
planning=json.loads((RAW/'planning.json').read_text())
summary=json.loads((RAW/'summary.json').read_text())
record=json.load(gzip.open(RAW/'result.json.gz','rt'))['cases'][0]['record']
ident=milestone['identities']['after']
assert ident['planning_revision_id']==planning['source_alignment_id']
assert ident['reference_candidate_ids']['candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
assert sum(len(l['stops']) for l in planning['lines'])==25
changed=[]
for n,h in manifest['source_sha256'].items():
 p=ROOT/n
 if not p.exists() or sha(p)!=h:changed.append(n)
source={
 'milestone_git_blob_sha256':hashlib.sha256(milestone_blob).hexdigest(),
 'raw_after_manifest_sha256':sha(RAW/'manifest.json'),
 'raw_after_planning_sha256':sha(RAW/'planning.json'),
 'raw_after_result_sha256':sha(RAW/'result.json.gz'),
 'raw_after_summary_sha256':sha(RAW/'summary.json'),
 'current_selected_samawah_sha256':sha(ROOT/'docs/design-engine/current/planning/cities/samawah.json.gz'),
 'current_line30_manifest_sha256':sha(ROOT/'docs/design-engine/line30-current-20261117/manifest.json'),
 'v07_project_continuity_readme_sha256':sha(ROOT/'docs/design-engine/v07-project-continuity/README.md'),
}
input=seal(dict(schema='osr-v07-samawah-gap-screen-input/1',physical_candidate_id=ident['reference_candidate_ids']['candidate_id'],selection_id=ident['selection_id'],planning_revision_id=ident['planning_revision_id'],city_evaluation_id=ident['city_evaluation_id'],service_evaluation_id=ident['service_evaluation_id'],cost_evaluation_id=ident['cost_evaluation_id'],civil_quantity_id=ident['civil_quantity_id'],raw_manifest_id=ident['manifest_id'],raw_source_commit=milestone['source_commit'],raw_source_epoch_mismatches=changed,source_sha256=source,scope='retained after-edit Samawah line gaps, conditional necessary energy and zone screen; no actual grade assignment',speed_cap_m_s=20.,launch_zone_m=500.,receiving_zone_m=350.,grade_hypotheses=[0.,.01,.02],gravity_m_s2=9.81,execution_limit_s=120,memory_limit_bytes=512*1024**2,disk_limit_bytes=20*1024**2,free_space_floor_bytes=20*1024**3),'input_id')
write('input.json',input)
height=20.**2/(2*9.81)
rows=[]
for line in planning['lines']:
 stops=line['stops']
 for j,(a,b) in enumerate(zip(stops,stops[1:])):
  gap=b['chainage_m']-a['chainage_m']
  coast=max(0.,gap-850.)
  overlap=gap<850.
  screens={}
  for grade in (0.,.01,.02):
   if overlap:status='zone-overlap-needs-distinct-dynamics'
   elif grade*coast>height:status='necessary-energy-fail'
   else:status='necessary-energy-pass-only'
   screens[str(grade)]={'status':status,'uphill_height_m_if_grade_applies':grade*coast}
  rows.append(dict(line_id=line['id'],leg_index=j,from_stop_id=a['id'],to_stop_id=b['id'],from_chainage_m=a['chainage_m'],to_chainage_m=b['chainage_m'],gap_m=gap,optimistic_remaining_coast_m=coast,fixed_500m_launch_350m_receiving_zones_overlap=overlap,screens=screens,actual_grade=None))
assert len(rows)==20
lines=[]
capital=record['cost']['capital_lines']
for line in planning['lines']:
 s=next(x for x in record['service_evaluation']['line_services'] if x['line_id']==line['id'])
 v=s['service'];p=s['propulsion_hypothesis']
 cost_sites=0
 if p['kind']=='station-launch-reference':
  cs=next(x for x in capital if x['key']==line['id']+'/launch-converters')
  cost_sites=cs['quantity']['capacities'][1]['sites']
 lines.append(dict(line_id=line['id'],length_m=line['length_m'],operational_stops=len(line['stops']),max_gap_m=max(x['gap_m'] for x in rows if x['line_id']==line['id']),headway_s=v['requirements']['headway_s'],normal_places_per_train=v['normal_places_per_train'],offered_capacity_pphpd=v['capacity_pphpd'],planning_usable_capacity_pphpd=v['planning_usable_capacity_pphpd'],requested_dwell_s=s['requested_service']['dwell_s'],active_trainsets=v['active_trainsets'],spare_trainsets=v['spare_trainsets'],total_trainsets=v['total_trainsets'],boarding_edges=v['boarding_edges'],departure_site_count_kinematic=v['departure_sites'],costed_station_launch_converter_sites=cost_sites,propulsion_hypothesis=p['kind'],powered_axle_motors_per_car=p['traction_motors_per_car'],added_traction_mass_hypothesis_kg_per_car=p['added_traction_mass_kg_per_car'],line_1_continuous_feed_m=p['continuous_feed_route_m'],known_reference_coast_failures=len(s['known_reference_failures']),full_train_fin_launch_envelope_m=v['jerk_full_train_fin_launch_envelope_m'],tail_clearance_s=v['tail_clearance_s_jerk_bound'],accounted_reference_mass_kg_per_car=v['accounted_reference_mass_kg_per_car'],installed_mass_complete=v.get('installed_mass_complete',False),actual_available_force_map=v.get('actual_available_force_map'),auxiliary_energy_balance_screen=v['auxiliary']['energy_balance_screen']))
assert sum(x['total_trainsets'] for x in lines)==81
counts={str(g):{'necessary_energy_fail':sum(r['screens'][str(g)]['status']=='necessary-energy-fail' for r in rows),'zone_overlap':sum(r['screens'][str(g)]['status']=='zone-overlap-needs-distinct-dynamics' for r in rows),'necessary_energy_pass_only':sum(r['screens'][str(g)]['status']=='necessary-energy-pass-only' for r in rows)} for g in (0.,.01,.02)}
result=seal(dict(schema='osr-v07-samawah-gap-screen-result/1',input_id=input['input_id'],physical_candidate_id=input['physical_candidate_id'],selection_id=input['selection_id'],new_physical_selection=None,planning_revision_id=input['planning_revision_id'],raw_manifest_id=input['raw_manifest_id'],raw_payload_integrity_verified=True,raw_current_source_match=False,raw_source_epoch_mismatches=changed,city_service_scope='five-line retained city model: declared 4000 peak pphpd each line, 200 s headway, not the 30 km 8280 pphpd control',route_length_m=sum(x['length_m'] for x in lines),line_count=5,operational_stop_count=sum(x['operational_stops'] for x in lines),line_services=lines,leg_count=len(rows),rows=rows,conditional_screen_counts=counts,conditional_height_cap_m=height,conditional_1pct_max_gap_m=850+height/.01,conditional_2pct_max_gap_m=850+height/.02,grade_observed=False,level_drag_model_failure_line_1_last_leg_m=next(x['gap_m'] for x in rows if x['line_id']=='line-1' and x['leg_index']==7),retained_city_model_cost_usd_base=summary['installed_capital_usd']['base'],retained_city_model_npv_usd_base=summary['whole_life_npv_usd']['base'],retained_city_cost_is_current_source_verified=False,retained_costed_station_launch_sites=sum(x['costed_station_launch_converter_sites'] for x in lines),retained_continuous_feed_substations=next(x for x in capital if x['key']=='line-1/continuous-feed-and-substations')['quantity']['substations'],retained_charging_boarding_edges=next(x for x in capital if x['key']=='network-auxiliary-charging')['quantity']['boarding_edges'],retained_charging_total_kw_hypothesis=next(x for x in capital if x['key']=='network-auxiliary-charging')['quantity']['kw'],retained_recovery_units=next(x for x in capital if x['key']=='network-protected-recovery-assets')['quantity']['units'],unknowns=['Actual route vertical profile/grades and speed restrictions are not surveyed in this packet','After-edit city calculation belongs to a retained source epoch with four changed current files','Station drive and braking force/current/thermal availability, full-tail protected conflicts and 200 s reliability are not measured','Line-1 powered-axle fallback is a research configuration and changes installed train/guideway/grid consequences','Complete installed mass, platform/catchment/soil, local manufacturing and city prices remain unqualified'],ranked_next_evidence=['Survey line-1 5.738 km and line-2 5.528 km longest legs first for continuous grade, curves, speed and access; survey all twenty gaps and platform/turnback constraints','Replay the after-edit city calculation against current sources with a declared candidate and service policy, preserving prior source epoch','Test station launch/receiving force and independent brake at actual worst gap/grade with full tail, 200 s duty, recovery and measured installed mass','Reprice station-launch versus powered-wheel alternatives with site/grid/fleet/civil/local manufacture and actual occupancy on the same Samawah service'],physical_accepted=False,engineering_accepted=False,operating_release=False),'evaluation_id')
write('result.json',result)
log={'command':'python3 build/v07-ethos/samawah-route-20261117-a/evaluate.py','wall_s':time.monotonic()-start,'raw_manifest_files_verified':len(manifest['files_sha256']),'raw_manifest_source_entries':len(manifest['source_sha256']),'current_source_mismatches':changed,'rows':len(rows),'disk_bytes_before_receipt':sum(p.stat().st_size for p in HERE.iterdir() if p.is_file())}
write('run.log',log)
receipt=seal(dict(schema='osr-v07-samawah-gap-screen-receipt/1',input_id=input['input_id'],evaluation_id=result['evaluation_id'],files_sha256={p.name:sha(p) for p in HERE.iterdir() if p.is_file()},physical_accepted=False),'receipt_id')
write('receipt.json',receipt)
assert sum(p.stat().st_size for p in HERE.iterdir() if p.is_file())<20*1024**2
print(json.dumps({'output':str(HERE),'input_id':input['input_id'],'evaluation_id':result['evaluation_id'],'receipt_id':receipt['receipt_id'],'counts':counts,'max_gap_m':max(x['gap_m'] for x in rows),'bytes':sum(p.stat().st_size for p in HERE.iterdir() if p.is_file())},sort_keys=True))
