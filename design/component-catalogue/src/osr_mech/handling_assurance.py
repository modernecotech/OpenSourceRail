"""Gross-section and construction-stage statics; no prestress or lifting release."""
import math
from osr_mech.provenance import stable_sum as sum
from .civil.decked_pi import (manufacturing_specification,construction_stage_reactions,
    DECK_WIDTH_MM,FLANGE_THICKNESS_MM,STEM_WIDTH_MM,STEM_DEPTH_MM,OVERALL_DEPTH_MM)


def gross_section():
    # Canonical Pi geometry in metres: full flange and two longitudinal stems.
    b=DECK_WIDTH_MM/1000;flange=FLANGE_THICKNESS_MM/1000;stem=STEM_WIDTH_MM/1000;depth=STEM_DEPTH_MM/1000
    rectangles=[(b,flange,depth+flange/2),(stem,depth,depth/2),(stem,depth,depth/2)]
    area=sum(b*h for b,h,z in rectangles)
    centroid=sum(b*h*z for b,h,z in rectangles)/area
    inertia=sum(b*h**3/12+b*h*(z-centroid)**2 for b,h,z in rectangles)
    return dict(area_m2=area,centroid_z_m=centroid,inertia_y_m4=inertia,
        lower_modulus_m3=inertia/centroid,upper_modulus_m3=inertia/(OVERALL_DEPTH_MM/1000-centroid),
        basis='bare uncracked gross section; inserts, cracking and prestress are not represented')


def support_screen(mass_kg,span_m,supports_m,*,dynamic_factor=1):
    a,b=supports_m
    if any(not math.isfinite(v) for v in (mass_kg,span_m,a,b,dynamic_factor)) or mass_kg<=0 or span_m<=0 or not 0<=a<b<=span_m or dynamic_factor<1:
        raise ValueError('invalid handling mass, span, supports or dynamic factor')
    weight=mass_kg*9.81/1000*dynamic_factor;uniform=weight/span_m
    rb=weight*(span_m/2-a)/(b-a);ra=weight-rb
    if min(ra,rb)<0:raise ValueError('support arrangement requires an unresolved hold-down reaction')
    points={0.,a,b,span_m,min(b,max(a,ra/uniform))}
    moments={x:ra*max(0,x-a)+rb*max(0,x-b)-uniform*x*x/2 for x in points}
    return dict(supports_m=[a,b],reaction_a_kn=ra,reaction_b_kn=rb,
        maximum_positive_moment_knm=max(moments.values()),maximum_negative_moment_knm=min(moments.values()),
        assumed_dynamic_factor=dynamic_factor,load_basis='complete manufactured study mass treated as uniform gravity load',
        strength_or_stability_accepted=False)


def beam_stage_assurance(span_m,arrangement=None):
    spec=manufacturing_specification(span_m);mass=spec['manufactured_study_mass_kg'];section=gross_section()
    data=arrangement or {};supports=tuple(data.get('support_positions_m',(span_m*.2,span_m*.8)))
    angle=data.get('sling_angle_degrees',60);factor=data.get('dynamic_factor',1.3)
    if not math.isfinite(angle) or not 0<angle<=90:raise ValueError('sling angle must be in (0,90]')
    lifting=support_screen(mass,span_m,supports,dynamic_factor=factor)
    leg_force=max(lifting['reaction_a_kn'],lifting['reaction_b_kn'])/(2*math.sin(math.radians(angle)))
    lifting.update(assumed_legs_each_pick=2,assumed_sling_angle_degrees=angle,
        maximum_leg_tension_kn=leg_force,horizontal_leg_component_kn=leg_force*math.cos(math.radians(angle)))
    service=support_screen(mass,span_m,(0,span_m))
    service['gross_lower_fibre_selfweight_tension_mpa']=service['maximum_positive_moment_knm']/section['lower_modulus_m3']/1000
    gear=data.get('lifting_gear_kg',4000)
    if not math.isfinite(gear) or gear<0:raise ValueError('invalid lifting gear mass')
    reaction_cases=[dict(load_chainage_m=x,**construction_stage_reactions(mass+gear,120000,span_m,x,2,120000)) for x in (0,span_m/2,span_m)]
    return dict(beam_variant=f'OSR-Pi{span_m:g}',gross_section=section,manufactured_study_mass_kg=mass,
        suspended_study_mass_kg=mass+gear,permanent_selfweight_screen=service,lifting_screen=lifting,
        storage_screen=support_screen(mass,span_m,supports),transport_screen=support_screen(mass,span_m,supports),
        launcher_reaction_envelope=reaction_cases,arrangement_source=data.get('source_record'),
        qualification='computed statics screens; not an accepted structural or lifting design',
        unknown=['prestress/tendon/reinforcement and loss design','rail/live/derailment/fatigue/vibration loading',
            'strength at transfer/lifting and supplier-approved pick/support details','anchor/bearing/restraint design',
            'vehicle axle loads and dynamic stability','supplier-confirmed launcher load charts and operating envelope'],
        independently_checked=False,construction_release=False)
