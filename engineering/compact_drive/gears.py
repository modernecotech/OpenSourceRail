"""Explicit two-stage shaft, tooth-blank and capacity requirements, SI."""
from math import sqrt,pi

def train(config):
    teeth=config['teeth'];modules=config['modules_m'];faces=config['faces_m']
    distances=[(a+b)*m/2 for (a,b),m in zip(teeth,modules)]
    output=[-1.05,.50,.38]
    middle=[output[0]+sqrt(distances[1]**2-.03**2),.50,.41]
    input_axis=[middle[0]+sqrt(distances[0]**2-.02**2),.50,.43]
    gears=[dict(id='stage1-pinion',axis='input',teeth=teeth[0][0],module_m=modules[0],face_m=faces[0],bore_m=.045,y_m=.46),
           dict(id='stage1-wheel',axis='middle',teeth=teeth[0][1],module_m=modules[0],face_m=faces[0],bore_m=.065,y_m=.46),
           dict(id='stage2-pinion',axis='middle',teeth=teeth[1][0],module_m=modules[1],face_m=faces[1],bore_m=.065,y_m=.55),
           dict(id='stage2-wheel',axis='output',teeth=teeth[1][1],module_m=modules[1],face_m=faces[1],bore_m=.2001,y_m=.55)]
    for g in gears:
        g['pitch_diameter_m']=g['teeth']*g['module_m'];g['addendum_diameter_m']=(g['teeth']+2)*g['module_m'];g['root_diameter_m']=(g['teeth']-2.5)*g['module_m']
    return dict(ratio=teeth[0][1]/teeth[0][0]*teeth[1][1]/teeth[1][0],
        axes=dict(output=output,middle=middle,input=input_axis),gears=gears,centre_distances_m=distances,
        case_size_m=[.68,.26,.37],case_centre_m=[-.905,.50,.41],
        tooth_scope='Actual pitch/addendum/root circles and stock face widths; involute flanks, fillets, keys, hardening and contact-fatigue remain unverified. Gross tooth blanks are not finished gears.')

def requirements(definition,motor_torque=500.,efficiency=.90):
    ratio=definition['ratio'];output=motor_torque*ratio*efficiency
    rows=[]
    for stage in (0,1):
        pinion,wheel=definition['gears'][2*stage:2*stage+2]
        torque=motor_torque if stage==0 else motor_torque*definition['gears'][1]['teeth']/definition['gears'][0]['teeth']*.95
        force=torque/(pinion['pitch_diameter_m']/2)
        rows.append(dict(stage=stage+1,pinion_torque_Nm=torque,tangential_force_N=force,
            Lewis_factor_hypothesis=.30,nominal_bending_Pa=force/(pinion['face_m']*pinion['module_m']*.30),
            required_allowable_with_dynamic15_Pa=1.5*force/(pinion['face_m']*pinion['module_m']*.30),
            verified_allowable_Pa=None,contact_fatigue_and_scuffing_verified=False))
    return dict(peak_motor_torque_is_catalogue30s_condition_only=True,output_torque_requirement_Nm=output,
        peak_tractive_force_new_wheel_N=output/.38,maximum_vehicle_speed_at4500rpm_new_wheel_m_s=4500*2*pi/60/ratio*.38,
        maximum_vehicle_speed_at4500rpm_worn_wheel_m_s=4500*2*pi/60/ratio*.34,stages=rows,
        solid45mm_shaft_nominal_torsion_Pa=16*motor_torque/(pi*.045**3),
        fatigue_allowables_bearing_capacity_and_hot_duty_not_established=True)
