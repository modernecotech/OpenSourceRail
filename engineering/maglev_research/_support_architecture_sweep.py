"""Bounded architecture worker for an isolated retained-model reconstruction."""
from copy import deepcopy
import importlib.util
import inspect
import itertools
import math
from pathlib import Path


def cooler(cm, a):
    """Count a separate proposed guide-coil cooler; coefficients are test targets."""
    rho_al = 2700.
    rows = []
    def solid(identity, volume, density, material):
        rows.append(dict(id=identity, volume_m3=volume, density_kg_m3=density,
                         mass_kg=volume*density, material=material))
    fin_count, length, thickness, height = 24, .9, .002, .08
    solid('24-aluminium-fins', fin_count*length*thickness*height, rho_al, 'aluminium')
    outside = [.9, .8, .008]; inside = [.898, .798, .006]
    solid('closed-liquid-tank-shell', math.prod(outside)-math.prod(inside), rho_al, 'aluminium')
    solid('tank-dielectric-fluid', math.prod(inside), 850., 'dielectric-fluid')
    # Two actual material-volume fan/motor hypotheses, not purchased fan ratings.
    solid('fan-blades-and-hubs', 2*(8*.10*.04*.0015+math.pi*.02**2*.04), rho_al, 'aluminium')
    solid('fan-motor-steel', 2*math.pi*(.03**2-.015**2)*.04, a['materials']['steel']['density_kg_m3'], 'steel')
    solid('fan-motor-copper', 2*math.pi*(.045**2-.031**2)*.025*.4, 8960., 'copper')
    solid('fan-housings', 2*(.14*.14*.06-.136*.136*.056), 1900., 'GFRP')
    solid('pump-aluminium-shell', math.pi*(.03**2-.025**2)*.10, rho_al, 'aluminium')
    solid('pump-steel-rotor', math.pi*.012**2*.05, 7760., 'steel')
    solid('pump-copper-envelope', math.pi*(.025**2-.015**2)*.025*.4, 8960., 'copper')
    solid('two-one-metre-hoses', 2*math.pi/4*(.014**2-.010**2), 1200., 'polymer')
    solid('hose-fluid', 2*math.pi/4*.010**2, 850., 'dielectric-fluid')
    solid('fan-pump-wires', 8*2.5e-6, 8960., 'copper')
    # Each number below is an explicit unmeasured design target. In particular,
    # a counted motor envelope is not evidence it supplies the specified flow.
    h_air, h_fluid, k_al = 40., 600., 150.
    m = math.sqrt(2*h_air/(k_al*thickness))
    eta = math.tanh(m*height)/(m*height)
    area = fin_count*2*length*height*eta + .9*.8-fin_count*length*thickness
    air_g = h_air*area
    wall_g = k_al*.10/.001
    airflow_kg_s, cp_air = .20, 1005.
    auxiliary_w = (airflow_kg_s/1.13)*150/.4 + (.10/850)*30000/.45
    known_rates = dict(aluminium=a['procurement']['aluminium_usd_kg'],
                       copper=a['procurement']['copper_usd_kg'], steel=a['procurement']['steel_usd_kg'])
    return dict(parts=rows, mass_kg=sum(row['mass_kg'] for row in rows),
                priced_raw_stock_usd=sum(row['mass_kg']*known_rates.get(row['material'], 0.) for row in rows),
                unpriced_materials=sorted({row['material'] for row in rows}-known_rates.keys()),
                fin_count=fin_count, fin_size_m=[length, thickness, height],
                aluminium_conductivity_target_w_m_k=k_al, fin_efficiency=eta,
                effective_air_area_m2=area, air_conductance_w_k=air_g,
                wall_conductance_w_k=wall_g, air_h_target_w_m2_k=h_air,
                fluid_h_target_w_m2_k=h_fluid, wetted_fraction_target=.35,
                airflow_target_kg_s=airflow_kg_s, air_specific_heat_j_kg_k=cp_air,
                fluid_flow_target_kg_s=.10, air_pressure_target_pa=150., fluid_pressure_target_pa=30000.,
                auxiliary_power_target_w=auxiliary_w, qualified=False,
                holds=['Convection, wetted fraction, pressure/flow and fan/pump performance are unmeasured targets.',
                       'Tank pressure strength, seals, dielectric compatibility, fouling, noise, protection and installed fit remain open.',
                       'Raw material prices exclude fabrication, purchased motors/drives, piping, quotation and qualification.'])


def harness(a):
    copper_area, length = 25e-6, 16.
    diameter = math.sqrt(4*copper_area/math.pi)
    copper = copper_area*length*8960.
    insulation = math.pi/4*((diameter+.002)**2-diameter**2)*length*1400.
    hose = 8*math.pi/4*(.014**2-.010**2)*1200.
    fluid = 8*math.pi/4*.010**2*850.
    plate = 2*.10*.08*.01*1900.
    return dict(copper_kg=copper, insulation_kg=insulation, hose_kg=hose,
                fluid_kg=fluid, reinforcement_plate_kg=plate,
                mass_kg=copper+insulation+hose+fluid+plate,
                per_extra_module=dict(circuits=2, copper_conductors=4, conductor_length_m=4.,
                    conductor_area_mm2=25., radial_insulation_m=.001, hoses=2, hose_length_m=4.,
                    hose_inner_outer_m=[.010,.014], reinforcement_plates=2,
                    reinforcement_plate_m=[.10,.08,.01]), qualified=False,
                holds=['Routing lengths, current drives, protection, extra hardpoints and all thermal/electrical duty require installed design.'])


def extended_context(guidance, width, scale, outer_y, sensitive):
    # Generalise exactly one declared frozen winding-envelope input. All stock,
    # bobbin/enamel/fluid bookkeeping remains the retained implementation.
    original = inspect.getsource(guidance.winding_context)
    token = 'outer=[.72 if large else .62,.188]'
    if original.count(token) != 1:
        raise ValueError('unexpected frozen winding-envelope implementation')
    namespace = dict(guidance.__dict__)
    exec(compile(original.replace(token, f'outer=[.72 if large else .62,{outer_y!r}]'),
                 '<explicit-guidance-envelope-extension>', 'exec'), namespace)
    turns = 200.
    inner = [.16*scale+.02,.10]; outer = [.72,outer_y]
    pack_volume = (math.prod(outer)-math.prod(inner))*.073
    area = .549*pack_volume/(turns*(sum(inner)+sum(outer)))*1e6
    context, fit = namespace['winding_context'](width,scale,turns,area,True)
    cm = guidance.r.cm
    if not sensitive:
        context[2]['core_paths'] = deepcopy(guidance.r.context_for(width,scale,140.,23.5)[2]['core_paths'])
    # Preserve all existing cover/coldplate material and count new y-edge strips.
    if outer_y > .198:
        extra_y = (.6+outer_y+.002-.8)/2
        for side in (-1,1):
            for name,height,z in [('coldplate',.008,-.38),('cover',.002,-.372)]:
                context[2]['parts'].append(cm._box(f'extended-y-{name}/{side}',[.96,extra_y,height],
                    [-.48,-.4-extra_y if side<0 else .4,z], 'aluminium',2700.,'new-guidance-envelope'))
    context[2]['mass_kg'] = sum(p['mass_kg'] for p in context[2]['parts'])
    return context, fit, area


def thermal_metrics(point, context):
    a,v,module = context[:3]; cu=a['materials']['copper']; coils=module['coils']
    areas=[coils[0]['conductor_area_mm2'],coils[1]['conductor_area_mm2']]
    lengths=[coils[0]['conductor_length_m'],sum(c['conductor_length_m'] for c in coils[1:])]
    r20=[length/(area*1e-6)*cu['resistivity_20c_ohm_m'] for length,area in zip(lengths,areas)]
    needed=[i*i*r*(1+cu['resistance_temperature_coefficient_per_k']*(a['maximum_copper_c']-20))/(a['maximum_copper_c']-a['ambient_c'])
            for i,r in zip(point['required_current_a'],r20)]
    ratios=dict(current=max(abs(i) for i in point['required_current_a'])/a['current_limit_a'],
                density=max(point['current_density_a_mm2'])/a['continuous_current_density_a_mm2'],
                field=point['max_core_b_t']/2.2,
                thermal=max(required/available for required,available in zip(needed,v['cooling_w_k'])))
    return needed,ratios


def guidance_floor(car_mass, count, a):
    """Two opposed banks of unqualified U-core DC attraction coupons."""
    b=2.2;gap=.008;mu0=4e-7*math.pi;density=a['materials']['steel']['density_kg_m3'];fill=a['stack_fill']
    force=.1*car_mass*9.80665/(count/2)
    # Preserve the2.2T material limit inside laminated steel: the mean gap
    # field is fill*Bsteel over the gross physical pole face. Using Bsteel
    # directly in both gap pressure and a fill-reduced steel area overstates
    # available force. No fringing gain is credited.
    gap_b=fill*b
    face=mu0*force/(gap_b*gap_b)
    side=math.sqrt(face)
    leg_length=.20;leg_spacing=.40
    path=2*leg_length+leg_spacing+side
    steel_mass=path*face*density*fill
    mmf=2*gap_b*gap/mu0
    # A real annular winding envelope counts both opposed sides of each turn.
    # Derive radial build from the unchanged fill/current-density limits, rather
    # than assuming a mean turn length with an impossible winding window.
    coil_height=.16;inner=side+.02
    radial_build=mmf/(a['continuous_current_density_a_mm2']*1e6*.549*coil_height)
    outer=inner+2*radial_build
    mean_turn=2*inner+2*outer
    copper_volume=(mmf/(a['continuous_current_density_a_mm2']*1e6))*mean_turn
    copper_mass=copper_volume*8960.
    turns=math.ceil(mmf/a['current_limit_a']);current=mmf/turns
    conductor_area=current/a['continuous_current_density_a_mm2']
    wire_side=math.sqrt(conductor_area*1e-6);enamel=.0001
    length=turns*mean_turn
    enamel_volume=length*((wire_side+2*enamel)**2-wire_side**2)
    pack_volume=(outer**2-inner**2)*coil_height
    fluid_volume=pack_volume-copper_volume-enamel_volume
    enamel_mass=enamel_volume*1400.;fluid_mass=fluid_volume*850.
    bobbin_mass=((inner**2-(inner-.002)**2)*coil_height
                 +2*((outer+.002)**2-(inner-.002)**2)*.001)*1900.
    enclosure=2*(outer+.02)*(leg_spacing+2*side+.02)*.002*2700.
    hot_loss=copper_volume*a['materials']['copper']['resistivity_20c_ohm_m']*(a['continuous_current_density_a_mm2']*1e6)**2*(1+a['materials']['copper']['resistance_temperature_coefficient_per_k']*100)
    return dict(units_per_car=count, energised_units_per_direction=count//2,
                force_per_energised_unit_n=force, pole_faces_per_unit=2,
                area_per_face_m2=face, total_active_face_area_per_unit_m2=2*face,
                physical_steel_section_m2=face, effective_iron_section_m2=face*fill,
                approximate_path_length_m=path,
                gap_m=gap, field_t=b, gap_field_t=gap_b, airgap_ampere_turn_lower_bound=mmf,
                copper_turn_area_sum_mm2=mmf/a['continuous_current_density_a_mm2'],
                mean_turn_length_hypothesis_m=mean_turn,turns=turns,current_a=current,conductor_area_mm2=conductor_area,
                coil_height_m=coil_height,coil_inner_m=[inner,inner],coil_outer_m=[outer,outer],
                radial_winding_build_m=radial_build,copper_fill=copper_volume/pack_volume,
                guide_leg_spacing_m=leg_spacing,guide_leg_length_m=leg_length,
                enamel_kg_per_unit=enamel_mass,fluid_kg_per_unit=fluid_mass,bobbin_kg_per_unit=bobbin_mass,
                nominal_turn_envelope_fits=(outer/2+side/2+.005<=leg_spacing and coil_height+.002<=leg_length),
                steel_kg_per_unit=steel_mass,copper_kg_per_unit=copper_mass,
                enclosure_kg_per_unit=enclosure,
                mass_kg_per_unit=steel_mass+copper_mass+enclosure+enamel_mass+fluid_mass+bobbin_mass,
                hot_copper_loss_w_per_energised_unit=hot_loss,
                cooling_lower_bound_w_k_per_energised_unit=hot_loss/80,
                priced_raw_stock_usd_per_unit=steel_mass*a['procurement']['steel_usd_kg']+copper_mass*a['procurement']['copper_usd_kg']+enclosure*a['procurement']['aluminium_usd_kg'],
                field_map_validated=False,
                scope='Optimistic counted geometry/gap-MMF bound at unchanged2.2T/3.75Amm2 limits; winding envelope/enamel/fluid/bobbin are counted. Steel MMF, leakage, retention, real routing, protection and control remain unsolved; not a joint model survivor.')


def main():
    work=Path(__file__).resolve().parent
    if work.name!='pole-return-research':raise ValueError('isolated research reconstruction required')
    spec=importlib.util.spec_from_file_location('support_frozen_guidance',work/'run_guidance.py')
    guidance=importlib.util.module_from_spec(spec);spec.loader.exec_module(guidance)
    r=guidance.r;cm=r.cm;parent=cm.definition();a=cm.load();before=cm.sources()
    retained=parent['controlled_aw3_kg']-24*parent['module']['mass_kg']
    hardware=cooler(cm,a);new_harness=harness(a);rows=[];contexts={}
    plans=itertools.product((.0225,.025,.0275,.030),(2.2,2.4),(.188,.24),(False,True),(False,True))
    for width,scale,outer_y,cooled,sensitive in plans:
        context,fit,area=extended_context(guidance,width,scale,outer_y,sensitive)
        v,module=context[1:3];coils=module['coils']
        cooler_g=None
        if cooled:
            # Exterior pack area is an envelope: access and wetting are targets.
            wet_area=sum(2*sum(c['outer_m'])*c['height_m']+2*(math.prod(c['outer_m'])-math.prod(c['inner_m'])) for c in coils[1:])
            fluid_g=hardware['fluid_h_target_w_m2_k']*hardware['wetted_fraction_target']*wet_area
            cooler_g=1/(1/fluid_g+1/hardware['air_conductance_w_k']+1/hardware['wall_conductance_w_k']
                        +1/(2*hardware['airflow_target_kg_s']*hardware['air_specific_heat_j_kg_k']))
            v['cooling_w_k']=[v['cooling_w_k'][0],cooler_g]
        local_mass=module['mass_kg']+(hardware['mass_kg'] if cooled else 0.)
        lo=min(p['at_m'][0] for p in module['parts']);hi=max(p['at_m'][0]+p['size_m'][0] for p in module['parts'])
        length=hi-lo
        identity=f'w{width*1000:.1f}-s{scale:.1f}-y{outer_y:.3f}-cool{int(cooled)}-sensitive{int(sensitive)}'
        contexts[identity]=(context,fit,local_mass)
        for count in (24,28,30,32):
            extra=max(0,count-24)*new_harness['mass_kg']
            aw3=retained+count*local_mass+extra
            target=aw3*r.G/count
            with r.installed(context):
                nominal=guidance.ctrl.asymmetric(context,target,.1*target)
                adverse=guidance.ctrl.asymmetric(context,1.3*target,.1*target)
            needed,ratios=thermal_metrics(nominal,context)
            row_length=(count//2)*length+(count//2-1)*.05
            array_fit=row_length<=16.
            fill=max(c['fill_fraction'] for c in coils)<=a['coil_fill_limit']
            nominal_pass=bool(fit['nominal_aabb_clear'] and fill and nominal['map_valid'] and nominal['continuous_current_density_screen'] and nominal['constant_current_thermal_screen'])
            reserve_pass=bool(adverse['map_valid'])
            joint=bool(nominal_pass and reserve_pass and array_fit)
            # Necessary shared return/pole area bound, optimistic because it
            # ignores leakage and all winding/current/thermal restrictions.
            useful_area=min(module['lift_pole_area_m2'],.16*scale*.025)*a['stack_fill']
            maximum_aw3_by_return_field=count*(2.2*useful_area)**2/(cm.MU0*r.G*(1.3*module['lift_pole_area_m2']+.1*module['guide_pole_area_m2']))
            rows.append(dict(id=f'support-{len(rows):03d}',geometry_id=identity,
                hypothesis=dict(width_m=width,core_scale=scale,guide_outer_m=[.72,outer_y],guide_turns=200.,guide_conductor_area_mm2=area,
                    cooling='counted-fin-tank-fan-targets' if cooled else 'retained-unqualified-conductance',
                    topology='useful-only-poles-sensitivity' if sensitive else 'original-branch-flux',modules_per_car=count),
                module_stock_mass_kg=module['mass_kg'],added_cooler_mass_kg_per_module=hardware['mass_kg'] if cooled else 0.,
                local_module_plus_cooler_kg=local_mass,extra_harness_mass_kg_per_car=extra,
                retained_nonmodule_aw3_kg=retained,controlled_aw3_kg=aw3,controlled_tare_kg=aw3-a['passenger_payload_kg'],
                six_car_aw3_kg=6*aw3,fulltrain_module_count=6*count,
                module_longitudinal_envelope_m=length,array_row_length_m=row_length,
                available_row_length_m=16.,minimum_gap_between_modules_m=.05,array_nominal_fit=array_fit,
                module_nominal_fit=fit['nominal_aabb_clear'],copper_fill_fractions=[c['fill_fraction'] for c in coils],
                optimistic_total_aw3_mass_bound_kg=maximum_aw3_by_return_field,
                optimistic_nonmodule_aw3_mass_bound_kg=maximum_aw3_by_return_field-count*local_mass-extra,
                optimistic_nonmodule_tare_mass_bound_kg=maximum_aw3_by_return_field-count*local_mass-extra-12000.,
                guide_cooling_w_k=v['cooling_w_k'][1],cooler_auxiliary_power_target_w_per_car=count*hardware['auxiliary_power_target_w'] if cooled else 0.,
                cooler_priced_raw_stock_usd_per_car=count*hardware['priced_raw_stock_usd'] if cooled else 0.,
                nominal_joint=nominal,adverse_joint=adverse,required_cooling_at120c_w_k=needed,
                nominal_constraint_ratios=ratios,maximum_nominal_constraint_ratio=max(ratios.values()),
                conditional_nominal_joint_pass=nominal_pass,conditional_1_3_peak_pass=reserve_pass,
                conditional_joint_support_coupon_pass=joint,
                topology_independently_validated=False,complete_system_feasible=False,configuration_adopted=False))
    # Preserve all nondominated failures, with topology comparisons kept separate.
    pareto={}
    for topology in ('original-branch-flux','useful-only-poles-sensitivity'):
        candidates=[row for row in rows if row['hypothesis']['topology']==topology and row['array_nominal_fit']]
        def objectives(row):return (row['controlled_aw3_kg'],row['maximum_nominal_constraint_ratio'],row['hypothesis']['modules_per_car'])
        pareto[topology]=[row['id'] for row in candidates if not any(all(x<=y for x,y in zip(objectives(other),objectives(row))) and any(x<y for x,y in zip(objectives(other),objectives(row))) for other in candidates)]
    # A separate guidance material bound does not inherit the shared field map.
    separate=[]
    for topology in ('original-branch-flux','useful-only-poles-sensitivity'):
        reference=min([row for row in rows if row['hypothesis']['topology']==topology and row['array_nominal_fit']],key=lambda row:row['maximum_nominal_constraint_ratio'])
        context,fit,_=contexts[reference['geometry_id']]
        module=context[2]
        removed=[p for p in module['parts'] if p['id'].startswith(('winding/guide-','guide-bobbin/'))]
        support_mass=module['mass_kg']-sum(p['mass_kg'] for p in removed)
        for count,guide_count in itertools.product((24,30,32),(6,12,24)):
            car_mass=retained+count*support_mass+max(0,count-24)*new_harness['mass_kg']
            for _ in range(80):
                bound=guidance_floor(car_mass,guide_count,a)
                revised=retained+count*support_mass+guide_count*(bound['mass_kg_per_unit']+hardware['mass_kg'])+max(0,count-24)*new_harness['mass_kg']
                if abs(revised-car_mass)<1e-8:break
                car_mass=revised
            with r.installed(context):
                support=r.point(context,car_mass*r.G/count)
                reserve=r.point(context,1.3*car_mass*r.G/count)
                hot=r.thermal(context,car_mass*r.G/count)
            source_cooling=module['cooling']
            retained_pump_w=count*source_cooling['flow_kg_s']/source_cooling['fluid_density_kg_m3']*source_cooling['pressure_drop_pa']/source_cooling['pump_efficiency']
            nominal_copper=None if hot['equilibrium_c'] is None else count*hot['equilibrium_current_a']**2*hot['resistance20_ohm']*(1+a['materials']['copper']['resistance_temperature_coefficient_per_k']*(hot['equilibrium_c']-20))
            peak_copper=count*reserve['current_a']**2*hot['resistance20_ohm']*(1+a['materials']['copper']['resistance_temperature_coefficient_per_k']*20)
            guide_hot=(guide_count//2)*bound['hot_copper_loss_w_per_energised_unit']
            new_aux=guide_count*hardware['auxiliary_power_target_w']
            nominal_budget=None if nominal_copper is None else nominal_copper+retained_pump_w+guide_hot+new_aux
            power_budget=dict(existing_suspension_allocation_w_per_car=10000.,
                nominal_support_dc_copper_w_per_car=nominal_copper,
                guide_hot_copper_w_per_car=guide_hot,
                new_guide_cooler_auxiliary_target_w_per_car=new_aux,
                retained_support_pump_target_w_per_car=retained_pump_w,
                nominal_accounted_lower_bound_w_per_car=nominal_budget,
                nominal_allocation_headroom_w_per_car=None if nominal_budget is None else 10000.-nominal_budget,
                static_1_3_support_copper_at40c_w_per_car=peak_copper,
                static_1_3_accounted_lower_bound_w_per_car=peak_copper+retained_pump_w+guide_hot+new_aux,
                uniform_new_coolers_auxiliary_target_w_per_car=(count+guide_count)*hardware['auxiliary_power_target_w'],
                extra_stock_for_uniform_new_coolers_kg_per_car=count*hardware['mass_kg'],
                uniform_new_coolers_mass_feedback_executed=False,
                scope='Subset of existing10kW suspension budget, not an addition to it. Guide copper uses120C bound, support nominal usesconditional equilibrium. Core/PWM/rail/converter losses, peakduration and repeatedduty remain unknown. Uniformcoolers comparison requires all addedmass to be resolved again.')
            separate.append(dict(id=f'separate-guidance-{len(separate):02d}',support_topology=topology,
                reference_geometry_id=reference['geometry_id'],support_modules_per_car=count,
                guidance_units_per_car=guide_count,shared_guide_stock_removed_kg_per_module=sum(p['mass_kg'] for p in removed),
                support_module_mass_kg=support_mass,controlled_aw3_lower_bound_kg=car_mass,
                guide_cooler_mass_kg_per_unit=hardware['mass_kg'],
                guide_cooler_auxiliary_power_target_w_per_car=guide_count*hardware['auxiliary_power_target_w'],
                guide_copper_heat_w_per_car=(guide_count//2)*bound['hot_copper_loss_w_per_energised_unit'],
                total_wound_coils_per_car=count+guide_count,original_wound_coils_per_car=72,
                suspension_power_budget=power_budget,
                support_array_nominal_fit=(count//2)*.96+(count//2-1)*.05<=16.,
                guide_material_bound=bound,symmetric_support=support,symmetric_1_3_support=reserve,
                symmetric_hot_support=hot,
                conditional_symmetric_support_screen=bool(support['map_valid'] and reserve['map_valid'] and hot['static_continuous_symmetric_screen']),
                joint_guidance_model_executed=False,complete_system_feasible=False,configuration_adopted=False))
    assert before==cm.sources()
    survivors=[row for row in rows if row['conditional_joint_support_coupon_pass']]
    ranked=sorted(rows,key=lambda row:(not row['array_nominal_fit'],not row['conditional_joint_support_coupon_pass'],row['maximum_nominal_constraint_ratio'],row['six_car_aw3_kg']))
    separate_next=min([row for row in separate if row['support_topology']=='original-branch-flux'
        and row['support_array_nominal_fit'] and row['conditional_symmetric_support_screen']
        and row['guide_material_bound']['nominal_turn_envelope_fits']],key=lambda row:row['controlled_aw3_lower_bound_kg'])
    result=dict(schema='osr-support-architecture-research/1',parent_configuration_sha256=parent['configuration_sha256'],
        source_model_sha256=before,canonical=dict(modules_per_car=24,fulltrain_modules=144,controlled_aw3_kg=parent['controlled_aw3_kg'],
            module_mass_kg=parent['module']['mass_kg'],retained_nonmodule_aw3_kg=retained,
            module_max_sampled_force_n=3064.0009882082604,module_weight_n=parent['module']['mass_kg']*r.G,
            net_support_per_added_canonical_module_n=3064.0009882082604-parent['module']['mass_kg']*r.G,
            speed_cannot_resolve_static_support=True),
        executed_joint_model_cases=len(rows),simultaneous_survivor_count=len(survivors),
        original_topology_survivors=sum(row['hypothesis']['topology']=='original-branch-flux' for row in survivors),
        sensitivity_topology_survivors=sum(row['hypothesis']['topology']=='useful-only-poles-sensitivity' for row in survivors),
        nominal_joint_passes=sum(row['conditional_nominal_joint_pass'] for row in rows),
        pareto_case_ids=pareto,recommended_next_case_id=ranked[0]['id'],cases=rows,
        separate_guidance_bound_cases=separate,cooler_design=hardware,extra_module_harness=new_harness,
        fixed_constraints=dict(passenger_payload_kg_per_car=12000.,ambient_c=40.,maximum_copper_c=120.,
            current_limit_a=120.,current_density_limit_a_mm2=3.75,coil_fill_limit=.55,field_limit_t=2.2,
            nominal_lateral_aw3_fraction=.1,adverse_lift_aw3_factor=1.3,cars=6),
        geometry_assumptions=dict(body_length_m=17.,end_clearance_m=.5,module_rows=2,minimum_inter_module_gap_m=.05,
            scope='Longitudinal AABB research screen only; no accepted vehicle/guideway/curve clearance or installed routing.'),
        recommended_next_design_contract=dict(
            purpose='A stationary full-load lift/guidance coupon before any operating-speed or spacing selection.',
            proposed_case_id=separate_next['id'],architecture='Original-flux balanced support plus two opposed banks of separate U-core guidance coupons',
            support_modules_per_car=separate_next['support_modules_per_car'],guidance_units_per_car=separate_next['guidance_units_per_car'],
            controlled_aw3_material_lower_bound_kg_per_car=separate_next['controlled_aw3_lower_bound_kg'],
            six_car_aw3_material_lower_bound_kg=6*separate_next['controlled_aw3_lower_bound_kg'],
            total_wound_coils_per_car=separate_next['total_wound_coils_per_car'],
            guide_coupon_envelope=separate_next['guide_material_bound'],
            suspension_power_budget=separate_next['suspension_power_budget'],
            steel_mmf_and_operating_margin_resolved=False,
            scope='Next spatial/rig specification only; the2.2T field and airgap-only MMF are optimistic limits with no steel/leakage operating margin. Add those losses and all omitted installed stock before adoption.',
            required_evidence=['Independent3D force/linkage/leakage maps for original and sensitivity candidates.',
                'One exact counted support+copper+cooler+guide configuration; actual winding routing/bends and cover/manifold/structure clearances.',
                'Measured fan/pump flow/pressure and coil-fluid/fin heat transfer over repeated hot duty; auxiliary power and cooling failure response.',
                'Both-sign lateral demand with support preserved, current/voltage/protection/fault tests and measured hardpoint/civil loads.',
                'If separate guidance is pursued, nonlinear U-core spatial/current/thermal maps, two opposed banks and fully recounted retention/cooling/control stock.'],
            release_authorised=False),
        limitations=['Cooler h/flow/pressure/efficiency and material envelopes are declared research targets, not supplier or measured ratings.',
            'The altered guidance envelope retains the archived reluctance topology; independent spatial/fringing/eddy/hot-temperature maps remain open.',
            'Constant-required-current thermal screens omit coupled magnet-temperature feedback, PWM/core losses and installed bus/control dynamics.',
            'Extra-module stock adds wires/hoses/fluid/plates; complete current drives, protection, hardpoint redesign, pipe routes and manufacturing prices remain open.',
            'Separate-guidance results are optimistic material bounds and symmetric support coupons, never simultaneous-guide model survivors.'],
        complete_system_feasible=False,physical_validation=False,engineering_accepted=False,configuration_adopted=False)
    (work/'support-architecture.json').write_bytes(cm.encoded(result))


if __name__=='__main__':main()
