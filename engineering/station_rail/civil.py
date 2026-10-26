"""Three conventional concrete guideways for the selected wheel train.

Every longitudinal section has its own maximum and minimum moving-load moment.
Prestress is sized from that section envelope, not one global critical train pose.
Quantities include explicitly sized analytical tendons; site design stays open.
"""
from pathlib import Path
import math
from . import ROOT,FLAGS
from .common import brief,identity,source_map

G=9.80665
RAIL_KG_M=60.21
RAIL_REFERENCE='https://www.britishsteel.co.uk/media/0ydpntdm/british-steel-product-brochure-14012025.pdf'
PRODUCER='engineering/station_rail/civil.py'


def section(family):
    if family=='box-beam':
        B,H,tw,tf=2.,1.4,.18,.18
        A=B*H-(B-2*tw)*(H-2*tf)
        I=(B*H**3-(B-2*tw)*(H-2*tf)**3)/12
        return dict(family=family,area_m2=A,I_m4=I,depth_m=H,c_top_m=H/2,c_bottom_m=H/2,
            dimensions=dict(outer_width_m=B,depth_m=H,wall_m=tw,flange_m=tf),closed_torsion=True,
            access='Internal inspection/ventilation and end closures not yet detailed',erection_pieces_per_span=1)
    if family=='twin-beam':
        b,h=.35,1.3;A=2*b*h;I=2*b*h**3/12
        return dict(family=family,area_m2=A,I_m4=I,depth_m=h,c_top_m=h/2,c_bottom_m=h/2,
            dimensions=dict(beam_width_m=b,depth_m=h,beam_centres_m=1.507),closed_torsion=False,
            access='Separate repeated transverse diaphragms and maintenance walkway interfaces required',erection_pieces_per_span=2)
    if family=='u-beam':
        B,H,tb,tw=1.807,1.5,.20,.30
        pieces=[(B*tb,tb/2,B*tb**3/12),(2*tw*(H-tb),tb+(H-tb)/2,2*tw*(H-tb)**3/12)]
        A=sum(a for a,z,i in pieces);zbar=sum(a*z for a,z,i in pieces)/A
        I=sum(i+a*(z-zbar)**2 for a,z,i in pieces)
        return dict(family=family,area_m2=A,I_m4=I,depth_m=H,c_top_m=H-zbar,c_bottom_m=zbar,
            dimensions=dict(outer_width_m=B,depth_m=H,bottom_m=tb,wall_m=tw,wall_centres_m=1.507),closed_torsion=False,
            access='Open trough requires drainage and cross-tie/torsional design; no running walkway credited',erection_pieces_per_span=1)
    raise ValueError('Unknown conventional guideway family')


def axle_train(vehicle,load='normal'):
    mass_key={'empty':'accounted_tare_kg_per_car','normal':'accounted_cap_loaded_kg_per_car','crowd_control':'accounted_160_control_kg_per_car'}[load]
    m=vehicle['mass'][mass_key];v=vehicle['physical_definition']['vehicle'];s=vehicle['physical_definition']['support']
    offsets=[car*(v['body_length_m']+v['coupling_gap_m'])+v['body_length_m']/2+c+dx
        for car in range(v['cars']) for c in s['bogie_centres_x_m'] for dx in (-s['bogie_wheelbase_m']/2,s['bogie_wheelbase_m']/2)]
    return offsets,m*G/4*1.3


def moving_envelope(span,offsets,axle_N,sections=41):
    if span<=0 or not offsets or axle_N<=0:raise ValueError('Positive beam and axle inputs required')
    rows=[]
    for i in range(sections):
        x=span*i/(sections-1)
        # Moment at a fixed section is piecewise linear in translation; its
        # extrema occur when an axle crosses a support or that section.
        translations=sorted({p-a for a in offsets for p in (0.,x,span)})
        maximum=0.;critical=translations[0]
        for trans in translations:
            loads=[a+trans for a in offsets if 0<=a+trans<=span]
            R=sum(axle_N*(span-a)/span for a in loads)
            M=R*x-sum(axle_N*(x-a) for a in loads if a<x)
            if M>maximum:maximum,critical=M,trans
        rows.append(dict(x_m=x,min_live_moment_Nm=0.,max_live_moment_Nm=maximum,critical_train_translation_m=critical))
    return rows


def interior_pier_train_reaction(span,offsets,axle_N):
    """Exact piecewise-linear influence extrema for two adjacent simple spans."""
    translations=sorted({point-a for a in offsets for point in (-span,0.,span)})
    reaction,pose=max((sum(axle_N*max(0.,1.-abs(a+t)/span) for a in offsets),t) for t in translations)
    return dict(maximum_live_reaction_N=reaction,critical_train_translation_m=pose,
        influence='triangular support influence over both adjacent equal simply supported spans',
        load_factor=1.3)


def alternative(vehicle,span,family,load='normal'):
    s=section(family);offsets,axle_N=axle_train(vehicle,load)
    env=moving_envelope(span,offsets,axle_N)
    # Track direct fastening every <=0.6m on each rail. A set has two anchors;
    # the 8kg/set account includes plate, clip, pad and bolts, not priced goods.
    sets=2*(math.ceil(span/.6)+1);fastener_kg=sets*8.
    diaphragm_count=math.ceil(span/2.5)+1 if family=='twin-beam' else 2
    diaphragm_m3=(diaphragm_count*.18*1.085*.65 if family=='twin-beam' else 2*.15*max(0.,s['dimensions']['outer_width_m']-2*.18)*.8)
    concrete_m3=s['area_m2']*span+diaphragm_m3
    concrete_kg=concrete_m3*2500
    rail=2*RAIL_KG_M*span
    reinforcement_kg=concrete_m3*120.
    # These are reference detailing rates, NOT a resolved bar bending schedule.
    q=(concrete_kg+rail+fastener_kg+reinforcement_kg)*G/span
    emax=s['depth_m']*.30;A=s['area_m2'];I=s['I_m4'];cb=s['c_bottom_m'];ct=s['c_top_m']
    for r in env:
        x=r['x_m'];r['self_moment_Nm']=q*x*(span-x)/2;r['e_m']=emax*4*x*(span-x)/span**2
        r['max_total_moment_Nm']=r['self_moment_Nm']+r['max_live_moment_Nm']
        r['required_effective_prestress_N']=r['max_total_moment_Nm']*cb/I/(1/A+r['e_m']*cb/I)
    effective_required=max(r['required_effective_prestress_N'] for r in env)
    strand_area=.00014;fpk=1860e6;initial_fraction=.70;loss_fraction=.20
    strands=math.ceil(effective_required/((1-loss_fraction)*initial_fraction*fpk*strand_area))
    initial=strands*strand_area*fpk*initial_fraction;effective=initial*(1-loss_fraction)
    prestress_kg=strands*strand_area*span*7850
    anchorage_kg=strands*2*4.5
    for r in env:
        e=r['e_m'];m=r['max_total_moment_Nm'];mmin=r['self_moment_Nm']
        # Compression negative, tension positive. Each section gets both train
        # extrema, including no train; release uses initial force/self weight.
        stresses=[]
        for mm in (mmin,m):
            stresses.extend((-effective/A-effective*e*cb/I+mm*cb/I,-effective/A+effective*e*ct/I-mm*ct/I))
        release=(-initial/A-initial*e*cb/I+r['self_moment_Nm']*cb/I,-initial/A+initial*e*ct/I-r['self_moment_Nm']*ct/I)
        r.update(max_service_tension_Pa=max(stresses),max_service_compression_Pa=-min(stresses),max_release_compression_Pa=-min(release),max_release_tension_Pa=max(release))
    max_tension=max(r['max_service_tension_Pa'] for r in env);max_compression=max(r['max_service_compression_Pa'] for r in env)
    max_release_compression=max(r['max_release_compression_Pa'] for r in env);max_release_tension=max(r['max_release_tension_Pa'] for r in env)
    # Unit-load integration at centre gives actual sampled moment envelope
    # upper-bound deflection; it may combine incompatible train positions and
    # is explicitly conservative rather than one realised dynamic trajectory.
    integral=0.
    for r0,r1 in zip(env,env[1:]):
        def val(r):
            x=r['x_m'];u=min(x,span-x)/2
            return r['max_total_moment_Nm']*u/(35e9*I)
        integral+=(val(r0)+val(r1))*.5*(r1['x_m']-r0['x_m'])
    pier_reaction=interior_pier_train_reaction(span,offsets,axle_N)
    allsteel=rail+fastener_kg+reinforcement_kg+prestress_kg+anchorage_kg
    maxlift=(concrete_kg+reinforcement_kg+prestress_kg+anchorage_kg)/s['erection_pieces_per_span']
    row=dict(family=family,span_m=span,load_case=load,section=s,concrete_m3=concrete_m3,concrete_mass_kg=concrete_kg,
        running_rail_kg=rail,rail_profile='60E1-reference',rail_reference_url=RAIL_REFERENCE,direct_fastener_sets=sets,direct_fastener_kg=fastener_kg,
        direct_fastener_anchors=sets*2,reinforcement_kg=reinforcement_kg,reinforcement_basis='120kg/m³ declared preliminary rate; detailed bar schedule unknown',
        prestress_kg=prestress_kg,prestress_strands=strands,prestress_initial_N=initial,prestress_effective_N=effective,
        prestress_reference=dict(strand_area_m2=strand_area,fpk_Pa_hypothesis=fpk,initial_fraction_hypothesis=initial_fraction,loss_fraction_hypothesis=loss_fraction,parabolic_eccentricity_max_m=emax),
        prestress_anchorage_kg=anchorage_kg,diaphragms=diaphragm_count,counted_steel_kg=allsteel,total_counted_span_mass_kg=concrete_kg+allsteel,
        quantities_maturity='Analytical section/tendon stock and declared detailing accounts; not a supplier or fabrication BOM',
        moving_load_envelope=env,maximum_live_moment_Nm=max(r['max_live_moment_Nm'] for r in env),
        max_service_tension_Pa=max_tension,max_service_compression_Pa=max_compression,max_release_compression_Pa=max_release_compression,max_release_tension_Pa=max_release_tension,
        service_tension_screen='pass' if max_tension<1.0 else 'fail',service_compression_screen='pass' if max_compression<=.45*50e6 else 'fail',
        release_tension_screen='pass' if max_release_tension<=1e6 else 'fail',release_compression_screen='pass' if max_release_compression<=.45*40e6 else 'fail',
        deflection_upper_bound_m=integral,deflection_limit_m_hypothesis=span/1000,deflection_screen='pass' if integral<=span/1000 else 'fail',
        torsion_and_unequal_rail_loading_qualified=False,
        construction=dict(erection_pieces_per_span=s['erection_pieces_per_span'],reference_max_piece_kg=maxlift,
            minimum_crane_hook_capacity_kg_hypothesis=maxlift*1.25,rigging_fraction_hypothesis=.25,crane_radius_capacity_confirmed=False,
            factory_labour_h=None,field_labour_h=None,temporary_stability_qualified=False),
        interior_pier_train_reaction=pier_reaction,
        foundation_scenarios=[dict(allowable_bearing_kPa_hypothesis=p,dead_plus_train_support_reaction_N=(concrete_kg+allsteel)*G+pier_reaction['maximum_live_reaction_N'],
            minimum_gravity_bearing_area_m2=((concrete_kg+allsteel)*G+pier_reaction['maximum_live_reaction_N'])/(p*1000),
            settlement_lateral_seismic_uplift_qualified=False,actual_footing_or_pile_quantity=None) for p in (100.,200.,300.)],
        actual_installed_cost_USD=None,engineering_screen='unknown',**FLAGS)
    row['necessary_longitudinal_screen']='pass' if all(row[k]=='pass' for k in ('service_tension_screen','service_compression_screen','release_tension_screen','release_compression_screen','deflection_screen')) else 'fail'
    row['alternative_id']=identity(row)
    return row


def evaluate(vehicle,root=ROOT):
    config=brief(root);rows=[alternative(vehicle,L,family) for family in ('twin-beam','box-beam','u-beam') for L in config['civil']['span_options_m']]
    controls={load:[alternative(vehicle,L,family,load) for family in ('twin-beam','box-beam','u-beam') for L in config['civil']['span_options_m']] for load in ('empty','crowd_control')}
    selected=next(r for r in rows if r['family']=='box-beam' and r['span_m']==config['civil']['reference_span_m'])
    quantities=('concrete_m3','concrete_mass_kg','running_rail_kg','direct_fastener_sets','direct_fastener_kg','direct_fastener_anchors','reinforcement_kg','prestress_kg','prestress_anchorage_kg','counted_steel_kg','total_counted_span_mass_kg')
    rates={k:selected[k]*1000/selected['span_m'] for k in quantities}
    v=dict(schema='osr-station-rail-civil/1',candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],support_component_id=vehicle['support_component_id'],propulsion_component_id=vehicle['propulsion_component_id'],
        civil_component_id=identity(dict(family='box-beam',physical_section=selected['section'],span_m=selected['span_m'],rails='60E1',fastener_spacing_m=.6,prestress_strands=selected['prestress_strands'],prestress_reference=selected['prestress_reference'],reinforcement_account_kg=selected['reinforcement_kg'])),
        selected_reference=selected,alternatives=rows,control_alternatives=controls,executed_case_count=len(rows)+sum(len(r) for r in controls.values()),reference_rates_per_directional_km=rates,
        magnetic_suspension_facings=False,powered_suspension_equipment=False,
        historical_maglev_reference=dict(span_m=25.,interface_steel_kg=21627.329,anchors=408,crossmembers=51,
            comparison_scope='Historic structural/interface steel versus new rail/fastener/reinforcement/tendon preliminary stock; boundaries differ and neither is complete installed infrastructure'),
        missing_evidence=['Wheel/rail contact and rail bending/fatigue','Fastener anchor fatigue and concrete breakout','Closed and open-section torsion/unequal wheel loads','Creep, shrinkage, long-term prestress losses, camber and alignment','Shear/end zones, bearing details and seismic restraint','Real foundation/site load cases and erection crane access','Guardrails, parapets, walkways, drainage and rescue access quantities','Actual supplier prices, construction labour and lifecycle maintenance'],
        source_sha256={**vehicle['source_sha256'],**source_map(root,(PRODUCER,))},**FLAGS)
    v['evaluation_id']=identity(v)
    return v
