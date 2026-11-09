"""Necessary drive geometry and conservative rigid-box arithmetic only."""
from math import prod


def stage_result(module_m, teeth, face_width_m, centre_distance_m):
    pinion, gear = teeth
    pitch = module_m * (pinion + gear) / 2
    return {"module_m": module_m, "teeth": list(teeth), "face_width_m": face_width_m,
            "nominal_centre_distance_m": centre_distance_m,
            "pitch_centre_distance_m": pitch,
            "centre_residual_m": pitch-centre_distance_m,
            "pitch_diameters_m": [module_m*pinion, module_m*gear],
            "geometry_status": "necessary pitch geometry only; tooth form, backlash, root/contact stress and tolerances unknown"}


def compact_drive(ratio=7.37):
    stages = [stage_result(.005, (20, 67), .06, .2175),
              stage_result(.006, (20, 44), .10, .192)]
    ratio_calc = prod(max(s["teeth"])/min(s["teeth"]) for s in stages)
    motor_torque = 205.0
    stage1_ratio = 67/20
    stage2_ratio = 44/20
    return {"stages": stages, "declared_ratio": ratio, "calculated_ratio": ratio_calc,
            "ratio_residual": ratio_calc-ratio,
            "axes": {"direction": [0, 1, 0],
                     "front_motor_axis_point_m": [-.6437797247430153, -.38, .43],
                     "front_intermediate_axis_point_m": [-.8603582324486507, .5, .41],
                     "front_output_axis_point_m": [-1.05, .5, .38]},
            "case_box_m": {"centre": [-.905, .5, .41], "size": [.68, .26, .37]},
            "counts_per_bogie": {"motors": 2, "gears": 4, "new_shafts": 2,
                "gear_bearings_positive_allowance": 6, "retained_wheelset_shafts": 1,
                "couplings": 2, "case_halves": 2, "seals": 4,
                "retained_fasteners": 12, "torque_reaction_bolts": 4},
            "ground_force": {"input": "official motor continuous torque 205 Nm, ratio 7.37, efficiency unknown",
                "per_motor_ideal_output_torque_Nm": motor_torque*ratio_calc,
                "wheel_radius_domain_m": [.34, .38],
                "ideal_per_motor_tractive_force_N": [motor_torque*ratio_calc/.38, motor_torque*ratio_calc/.34],
                "status": "ideal kinematic conversion only; gear losses, adhesion, duty, axle and wheel limits unknown"},
            "shaft_speed": {"motor_max_rpm": 4500,
                "intermediate_max_rpm_ideal": 4500/stage1_ratio,
                "wheelset_max_rpm_ideal": 4500/ratio_calc,
                "continuous_205Nm_stage1_pinion_tangential_force_N": motor_torque/(.005*20/2),
                "continuous_ideal_stage2_pinion_tangential_force_N": motor_torque*stage1_ratio/(.006*20/2),
                "status": "kinematic and ideal static force arithmetic; transient duty, tooth strength, shafts, keys, bearings, lubrication and thermal limits open"}}


def axis_aligned_sweep(center, size, angular_radius, translation_radius):
    """Conservative full-angle box using a radius bound, including translation."""
    if len(center) != 3 or len(size) != 3 or min(size) <= 0:
        raise ValueError("positive 3D box required")
    radius = sum(x*x for x in center) ** .5 + sum((x/2)**2 for x in size) ** .5
    d = radius * angular_radius + translation_radius
    return [[center[i]-size[i]/2-d, center[i]+size[i]/2+d] for i in range(3)]
