"""Keep exact-bound refusal and one1A-interior operating sample distinct."""
import json,math
from pathlib import Path
from hashlib import sha256
import numpy as np
import run as r
if __name__=='__main__':
 result=json.loads((r.OUT/'results.json').read_bytes());assert result['source_sha256']==r.SOURCE==r.m.sources()
 fine=next(x for x in result['rows'] if x['id']=='resolved8mm-256-40');related=[x for x in result['rows'] if x['hypothesis_sha256']==fine['hypothesis_sha256']]
 r.operating(fine,related)
 groups=result['resolved_corner_operating']['groups'];zero=r.m.propulsion_group_map([0.],[20.],[[.008,.008]],groups,np.zeros((4,2)),temperature_c=40.,copper_temperature_c=80.);phase=np.angle(zero['lambda_wb'].sum(axis=1));rows=[]
 for iq in (1350.,1349.):
  I=iq*np.exp(1j*(phase+math.pi/2));current=np.c_[I.real,I.imag];f=r.m.propulsion_group_map([0.],[20.],[[.008,.008]],groups,current,temperature_c=40.,copper_temperature_c=80.)
  row=dict(requested_q_current_a=iq,actual_max_phasor_magnitude_a=float(np.max(abs(I))),currents_alpha_beta_a=current.tolist(),source_current_limits_a=f['group_current_limit_a'].tolist(),
    accepted_for_conditional_numerical_map=bool(f['accepted_for_simulation']),domain_valid=bool(f['domain_valid']),field_numerically_converged=bool(f['field_numerically_converged']),configuration_sha256=f['configuration_sha256'],demag_margin_a_m=float(f['demag_margin_after_armature_bound_a_m']))
  if f['accepted_for_simulation']:
   emf=np.asarray(f['emf_wb_s']).sum(axis=1);V=np.asarray(f['group_R_ohm'])*I+1j*2*math.pi/.5*20*np.asarray(f['group_L_h'])*I+emf;p=1.5*np.asarray(f['group_R_ohm'])*abs(I)**2
   row.update(force_x_n_per_car=float(np.asarray(f['force_x_n']).sum()),normal_side_n=np.asarray(f['normal_side_n']).sum(axis=0).tolist(),emf_peak_v_per_group=abs(emf).tolist(),steady_voltage_peak_v_per_group=abs(V).tolist(),copper_heat_w_total=float(p.sum()),adiabatic_temperature_rise_10s_k=(10*p/np.asarray(f['group_thermal_capacity_j_k'])).tolist())
  rows.append(row)
 data=dict(schema='osr-ignored-propulsion-current-boundary/1',hypothesis_sha256=fine['hypothesis_sha256'],source_sha256=r.SOURCE,magnetic_temperature_c=40.,copper_temperature_c=80.,speed_m_s=20.,gap_m=.008,groups=groups,rows=rows,
  interpretation='Theexact1350Aphasormayexceeditslimitbyfloatingpointroundoff;retainrefusalnottreatasmaterialfailure.1349Aisaseparateexplicitinteriorrequest,notalimitrelaxation. Conditionalundamaged40C2Dfieldonly;notwholetemperature/gridconvergence/system/hardwareacceptance.',**r.FLAGS)
 r.write('current-boundary-diagnostic.json',data);result['resolved_corner_current_boundary_diagnostic_path']='current-boundary-diagnostic.json';r.write('results.json',result);print(json.dumps(rows,indent=2))
