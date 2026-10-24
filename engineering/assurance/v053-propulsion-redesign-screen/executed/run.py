"""Ignored, isolated geometry hypotheses. Never mutates or promotes canonical design."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip,json,math,multiprocessing,os,signal,time,traceback
import numpy as np
from engineering.ferrite_maglev import candidate_magnetics as m

ROOT=m.ROOT;OUT=ROOT/'build/propulsion-redesign-screen';BASE=m.load();SOURCE=m.sources();PARENT=m.definition()['configuration_sha256']
FLAGS=dict(design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False,canonical_adoption=False)

def encoded(x):return m.encoded(x)
def h(x):return sha256(encoded(x)).hexdigest()
def write(name,value):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);temporary=p.with_suffix(p.suffix+'.tmp');temporary.write_bytes(encoded(value));temporary.replace(p)
def apply(change):
 a=deepcopy(BASE)
 for path,value in change.items():
  group,key=path.split('.');a[group][key]=value
 return a

def worker(job):
 start=time.monotonic();before=m.sources();a=apply(job['changes']);hyp=h(dict(schema='osr-exploratory-propulsion-hypothesis/1',parent=PARENT,input=a,source_sha256=SOURCE))
 # Process-local substitutions only. These are explicit new hypotheses, not a79.
 m.load=lambda:deepcopy(a);m._current_identity=lambda:hyp
 for name in ('_runtime_cached','_identity_cached','_propulsion_calibration'):
  fun=getattr(m,name,None)
  if hasattr(fun,'cache_clear'):fun.cache_clear()
 def expired(signum,frame):raise TimeoutError('bounded180s coupon budget exceeded')
 signal.signal(signal.SIGALRM,expired);signal.alarm(180)
 try:
  result=m.spatial_flux_shoe_coupon(job['nx'],job['depth_cells'],temperature_c=job['temperature_c'],margin_periods=job['margin_periods'])
  finite=all(math.isfinite(float(result[k])) for k in ('matrix_relative_residual','nonlinear_secant_mismatch','peak_core_b_t','conservative_demag_margin_a_m','nominal_gap_fundamental_peak_t'))
  armature=3*a['propulsion_band']['wayside_turns']*a['propulsion_band']['wayside_current_screen_a']/a['propulsion_flux_shoe']['period_m']
  coupon_valid=bool(finite and result['converged'] and result['matrix_relative_residual']<1e-8 and result['peak_core_b_t']<2.2)
  row=dict(id=job['id'],hypothesis_sha256=hyp,parent_configuration_sha256=PARENT,input_sha256=h(a),changes=job['changes'],grid={k:job[k] for k in ('nx','depth_cells','temperature_c','margin_periods')},
   state='executed',source_sha256=SOURCE,source_unchanged=before==m.sources(),coupon=result,coupon_numerically_valid=coupon_valid,
   declared_maximum_armature_bound_a_m=armature,demag_margin_after_declared_current_bound_a_m=result['conservative_demag_margin_a_m']-armature,
   material_current_screen_pass=bool(coupon_valid and result['conservative_demag_margin_a_m']>armature),
   box_only_band_mass_upper_bound_kg=m._propulsion_band(a)['mass_kg'],mass_note='Untrimmed sourcebox stock upper bound. PDE chamfer cells are removed, but revised3D native machining, retention and netmass are NOT issued. No fullvehiclemass/cost or localcontent claim.',elapsed_host_s=time.monotonic()-start,**FLAGS)
 except Exception as exc:
  row=dict(id=job['id'],hypothesis_sha256=hyp,parent_configuration_sha256=PARENT,input_sha256=h(a),changes=job['changes'],grid={k:job[k] for k in ('nx','depth_cells','temperature_c','margin_periods')},state='unknown-execution-error',error=type(exc).__name__+': '+str(exc),source_sha256=SOURCE,source_unchanged=before==m.sources(),elapsed_host_s=time.monotonic()-start,**FLAGS)
 finally:signal.alarm(0)
 write('inputs/'+job['id']+'.json',a);write('raw/'+job['id']+'.json',row)
 return row

def batch(jobs):
 rows=[]
 with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
  futures={pool.submit(worker,j):j for j in jobs}
  for future in as_completed(futures):
   row=future.result();rows.append(row);c=row.get('coupon',{});print(row['id'],row['state'],'converged',c.get('converged'),'B',c.get('nominal_gap_fundamental_peak_t'),'margin',row.get('demag_margin_after_declared_current_bound_a_m'),flush=True)
 return rows

def operating(row,related):
 # Only evaluate operating maps at the40C calibration temperature. Cold/hot
 # coupons separately constrain geometry eligibility; no double-temperature scaling.
 a=apply(row['changes']);m.load=lambda:deepcopy(a);hyp=row['hypothesis_sha256'];m._current_identity=lambda:hyp
 for name in ('_runtime_cached','_identity_cached'):
  fun=getattr(m,name,None)
  if hasattr(fun,'cache_clear'):fun.cache_clear()
 fine=row['coupon'];coarse=next(r['coupon'] for r in related if r['grid']['temperature_c']==40. and r['grid']['nx']<row['grid']['nx'])
 eligible=bool(all(r.get('material_current_screen_pass') for r in related))
 # Preserve every applicable sampled failure, including cold/refinement failures.
 calibration=dict(coarse=coarse,fine=fine,accepted=eligible,fundamental_refinement_relative=abs(fine['nominal_gap_fundamental_peak_t']-coarse['nominal_gap_fundamental_peak_t'])/fine['nominal_gap_fundamental_peak_t'])
 m._propulsion_calibration=lambda ignored:calibration
 groups=[dict(id=f'G{i}',start_m=-10+5*i,end_m=-5+5*i) for i in range(4)]
 zero=m.propulsion_group_map([0.],[0.],[[.008,.008]],groups,np.zeros((4,2)),temperature_c=40.,copper_temperature_c=80.)
 phase=np.angle(zero['lambda_wb'].sum(axis=1));w=m.propulsion_group_definition(5.);rows=[]
 for speed in (0.,10.,20.):
  for current in (337.5,675.,1350.):
   I=current*np.exp(1j*(phase+math.pi/2));field=m.propulsion_group_map([0.],[speed],[[.008,.008]],groups,np.c_[I.real,I.imag],temperature_c=40.,copper_temperature_c=80.)
   valid=bool(eligible and field['accepted_for_simulation'] and field['domain_valid'] and field['field_numerically_converged'])
   record=dict(speed_m_s=speed,q_current_a=current,map_valid_for_this_sample=valid,configuration_sha256=field['configuration_sha256'],demag_margin_after_armature_bound_a_m=float(field['demag_margin_after_armature_bound_a_m']))
   if valid:
    emf=np.asarray(field['emf_wb_s']).sum(axis=1);omega=2*math.pi/a['propulsion_flux_shoe']['period_m']*speed
    voltage=np.asarray(field['group_R_ohm'])*I+1j*omega*np.asarray(field['group_L_h'])*I+emf
    copper=1.5*np.asarray(field['group_R_ohm'])*abs(I)**2;capacity=np.asarray(field['group_thermal_capacity_j_k'])
    record.update(force_x_n_per_car=float(np.asarray(field['force_x_n']).sum()),normal_side_n=np.asarray(field['normal_side_n']).sum(axis=0).tolist(),net_leftward_n=float(np.asarray(field['leftward_n']).sum()),
     group_psi_wb=np.asarray(field['psi_wb']).ravel().tolist(),group_emf_peak_v=abs(emf).tolist(),group_voltage_peak_v=abs(voltage).tolist(),
     modulation_limit_v=w['dc_bus_v']/math.sqrt(3),voltage_fits=bool(np.all(abs(voltage)<=w['dc_bus_v']/math.sqrt(3))),
     copper_heat_w_total=float(copper.sum()),adiabatic_temperature_rise_10s_k=(10*copper/capacity).tolist(),
     group_R_ohm=np.asarray(field['group_R_ohm']).tolist(),group_L_h=np.asarray(field['group_L_h']).tolist(),group_copper_mass_kg=np.asarray(field['group_copper_mass_kg']).tolist())
   else:record['force_normal_emf_voltage_thermal_quantities']=None
   rows.append(record)
 return dict(hypothesis_sha256=hyp,geometry_eligible_over_all_retained_sampled_coupons=eligible,groups=groups,operating_samples=rows,
  scope='Single straight12m passiveband, actual finite overlap with4independent5m groups,40C magnetic calibration/80C copper. Steady rotating-current voltage estimate, not executed inverter/RL/control/wholetrain/route/hardware validation. Two exterior groups overlap only1m each; no3fullgroup-per-car credit.',**FLAGS)

def main():
 start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
 canonical=ROOT/'docs/design-engine/ferrite-maglev/candidate-magnetics';manifest=json.loads((canonical/'manifest.json').read_bytes());raw=(canonical/'study.json.gz').read_bytes()
 assert manifest['source_sha256']==SOURCE and sha256(raw).hexdigest()==manifest['files_sha256']['study.json.gz']
 prior=json.loads(gzip.decompress(raw))['spatial_field_coupons'];write('prior-failures.json',dict(configuration_sha256=PARENT,manifest_sha256=sha256((canonical/'manifest.json').read_bytes()).hexdigest(),coupons=prior))
 def change(depth=.04,period=.25,cham=.001):return {'propulsion_flux_shoe.depth_m':depth,'propulsion_flux_shoe.period_m':period,'propulsion_band.period_m':period,'propulsion_flux_shoe.corner_chamfer_m':cham}
 cases=[('reference-40',change(),40.,96,24,1.),('thin20-cold',change(.02),0.,96,24,.5),('thin20-40',change(.02),40.,96,24,.5),('thin30-cold',change(.03),0.,96,24,.5),
  ('pitch50-cold',change(.04,.5),0.,64,16,.5),('pitch50-40',change(.04,.5),40.,64,16,.5),('pitch50-deep60-cold',change(.06,.5),0.,64,16,.5),('chamfer4-cold',change(.04,.25,.004),0.,96,24,.5),('chamfer8-cold',change(.04,.25,.008),0.,96,24,.5)]
 jobs=[dict(id=i,changes=c,temperature_c=T,nx=nx,depth_cells=d,margin_periods=b) for i,c,T,nx,d,b in cases];rows=batch(jobs)
 candidates=[r for r in rows if r['grid']['temperature_c']==0. and r.get('material_current_screen_pass')]
 selected=max(candidates,key=lambda r:r['demag_margin_after_declared_current_bound_a_m'],default=None);operation=None
 if selected is not None:
  print('SELECTED',selected['id'],flush=True);c=selected['changes']
  refine=[dict(id='selected-'+tag,changes=c,temperature_c=T,nx=nx,depth_cells=d,margin_periods=b) for tag,T,nx,d,b in [('128-cold',0.,128,32,.5),('128-40',40.,128,32,.5),('192-cold',0.,192,48,.5),('192-40',40.,192,48,.5),('128-hot80',80.,128,32,.5),('128-boundary1',40.,128,32,1.)]]
  rows+=batch(refine);related=[r for r in rows if r['hypothesis_sha256']==selected['hypothesis_sha256']]
  if all(r.get('state')=='executed' and r.get('coupon_numerically_valid') for r in related):operation=operating(next(r for r in related if r['id']=='selected-192-40'),related)
 assert SOURCE==m.sources(),'production source changed; exploratory receipt held'
 result=dict(schema='osr-ignored-propulsion-redesign-screen/1',source_sha256=SOURCE,parent_configuration_sha256=PARENT,prior_failures_path='prior-failures.json',rows=rows,selected_geometry_hypothesis_sha256=selected['hypothesis_sha256'] if selected else None,
  operating=operation,all_failed_and_unknown_cases_retained=True,production_sources_unchanged=True,canonical_promoted=False,elapsed_host_s=time.monotonic()-start,
  limitations=['Independentperiodic2D coupons only; no finiteheight/ends/vehicleiron interaction or measuredmaterialmap.','Allapplicablesampledrefinement/boundary/temperaturefailures remain gating; no selectingawayfailedfinegrid.',
  'Hot/coldsampledtemperaturepoints do notprovecontinuoustemperaturerange; magneticfieldoperatingquantitiesareevaluatedonlyat40Ccalibration.',
  'PDEchamferstock isnotissuednativeCAD/netmass; no cheaper/noise/localcontent/fullvehicleclaim.','Canonicalcandidate remainsREJECTED forlift/guidance returnrail andpropulsion; thesehypothesesarenotintegrated.'],**FLAGS)
 write('results.json',result)
 files={p.relative_to(OUT).as_posix():sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and p.name not in ('manifest.json','run.log')}
 write('manifest.json',dict(schema='osr-ignored-propulsion-redesign-receipt/1',source_sha256=SOURCE,runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),files_sha256=files,production_sources_unchanged=SOURCE==m.sources(),**FLAGS))
 print('COMPLETE',len(rows),'coupons','elapsed',time.monotonic()-start,'operating',operation is not None,flush=True)

if __name__=='__main__':main()
