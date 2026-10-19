"""Revision-bound WP04/05/06 cassette chain: executable models, explicit holds.

This adapter extends the existing assembly programme. Static circuit and duct
balances are implemented research checks; assumed protection, fan curves and
access envelopes do not establish equipment or railway qualification.
"""
from copy import deepcopy
from math import exp, isfinite, pi, sqrt

from engineering.twin_workflow import core

FEMALE = 'M80-4000000F1-10-326-00-000'
MALE = 'M80-5000000M1-10-335-00-000'
SOURCE_CARDS = [
    dict(id='harwin-female', publisher='Harwin', exact_part=FEMALE,
         revision='product page retrieved 2026-10-19', locator='Kit description; technical details; related mating products',
         url='https://www.harwin.com/products/'+FEMALE,
         document_sha256='cfd043f736bd3e8e13dc2171c3348273faa71b1e939a665f1a3f7fbb15cf7ea6',
         operating_envelope='14 AWG M80-326 solder contacts; headline 15 A/contact, not simultaneous derating',
         units=['AWG','A'], uncertainty='Application derating and actual supplied revision unconfirmed'),
    dict(id='harwin-male', publisher='Harwin', exact_part=MALE,
         revision='product page retrieved 2026-10-19', locator='Kit description; related mating products includes exact female',
         url='https://www.harwin.com/products/'+MALE,
         document_sha256='3627635ba8a4e3aae9caa530a9804f4cfb9bf09961c7af920f0c2ea143c51ff6',
         operating_envelope='12 AWG M80-335 solder contacts, internally threaded jackscrews',
         units=['AWG'], uncertainty='Offered stock and system suitability unconfirmed'),
    dict(id='harwin-is52', publisher='Harwin', exact_part='M80-326/M80-335', revision='IS-52 issue 2, 2023-02-01',
         locator='pp2-5 cable assembly, insertion/removal, appendix 1',
         url='https://content.harwin.com/asset/e1364346-f61c-4492-9ac1-d501ed4f9674/IS-52-IS-52-Datamate-Mix-Tek-Assembly-and-Contact-Removal-Instruction-Sheet.pdf',
         document_sha256='7d073de0c992e7678bb866a86d4068ff451876e3c9fd89d1475478a8548b5698',
         operating_envelope='Minimum strip 5 mm; solder before insertion; Z80-290 removal tool',
         units=['mm'], uncertainty='Solder alloy, iron profile and rail workmanship qualification not supplied'),
    dict(id='harwin-c005', publisher='Harwin', exact_part='Datamate M80 power', revision='C00542, 2024-10-22',
         locator='p5 section2.3 power; p8 mating face numbering; appendix5 jackscrews',
         url='https://content.harwin.com/m/af82fc432c606a31/original/C005-C005XX-Component-Specification-Datamate-M80-and-M83-Series-2-00mm-4-00mm-pitch-High-Reliability.pdf',
         document_sha256='7f794408a92cd98f9b1e1b29b8e6c8f4809a8f63fff3253cddfc87bf94dded38',
         operating_envelope='Power contact maximum resistance 6 milliohm; female face numbering mirrored',
         units=['ohm'], uncertainty='Condition-specific operating resistance and installed life unconfirmed'),
    dict(id='harwin-c049', publisher='Harwin', exact_part='Datamate Power cable assemblies', revision='C04913 issue13',
         locator='Datamate Power column, materials and testing rows',
         url='https://content.harwin.com/asset/d8c6ba59-643e-4a53-a135-7db78cfadb90/C049-C049XX-Component-Specification-Cable-Assembly-Specifications-for-all-HRi-products.pdf',
         document_sha256='744a54d430e519ab93c8fb6f1ae91434f513bb62187314126688ab29255acea6',
         operating_envelope='FIT221-1/8-0 heat shrink reference for non-PM5/PF5 power contacts',
         units=[], uncertainty='Referenced sleeve is not an adopted OSR rail fire-qualified installation'),
]
for _card in SOURCE_CARDS:
    _card.update(retrieved='2026-10-19', licence='Public access; publisher copyright; linked, not redistributed',
                 applicability='Provisional cassette reference, not traction or safety authorisation', approved=False)


def awg_area(awg):
    """Geometric AWG nominal solid-equivalent area in SI, no ampacity claim."""
    if type(awg) is not int or not 0 <= awg <= 40:
        raise ValueError('AWG 0..40 integer required')
    return pi*(.005*.0254*92**((36-awg)/39))**2/4


def _numbers(values, positive=(), nonnegative=()):
    for k in positive:
        if type(values[k]) not in (float,int) or not isfinite(values[k]) or values[k]<=0:
            raise ValueError('positive finite '+k+' required')
    for k in nonnegative:
        if type(values[k]) not in (float,int) or not isfinite(values[k]) or values[k]<0:
            raise ValueError('nonnegative finite '+k+' required')


def electrical_case(*, voltage_v=24., ambient_c=50., female_length_m=.8,
                    male_length_m=1., fault='none', load_ohm=4.8,
                    source_ohm=.05, contact_ohm=.006, termination_ohm=.001):
    """DC Kirchhoff/heat balance with a separate *hypothetical* interlock model.

    Short-circuit demand is the prospective pre-trip current. The post-trip
    current is zero under an ideal monitored disconnect, not fuse coordination.
    Reverse and mis-mate detection are injected oracle inputs, not a proved
    hardware architecture. The unsuppressed demand is retained for sizing.
    """
    args=locals().copy();_numbers(args,positive=('voltage_v','load_ohm','female_length_m','male_length_m'),
                                nonnegative=('source_ohm','contact_ohm','termination_ohm'))
    if not isfinite(ambient_c) or not -55<=ambient_c<=125:raise ValueError('temperature outside research domain')
    if fault not in {'none','open-supply','open-return','open-bond','short','reversed','mis-mate','unlock'}:
        raise ValueError('unknown circuit fault')
    rho20=1.724e-8;alpha=.00393
    rf=rho20*(1+alpha*(ambient_c-20))*female_length_m/awg_area(14)
    rm=rho20*(1+alpha*(ambient_c-20))*male_length_m/awg_area(12)
    loop=2*(rf+rm)+2*contact_ohm+4*termination_ohm
    prospective=voltage_v/(source_ohm+loop) if fault=='short' else voltage_v/(source_ohm+loop+load_ohm)
    if fault in {'open-supply','open-return'}:prospective=0.
    if fault=='reversed':prospective=-prospective
    permit=fault=='none'
    current=prospective if permit else 0.
    load_voltage=current*load_ohm
    source_power=voltage_v*current
    load_power=current**2*load_ohm
    cable_heat=current**2*2*(rf+rm)
    contact_heat=current**2*2*contact_ohm
    termination_heat=current**2*4*termination_ohm
    source_heat=current**2*source_ohm
    # Thermal resistance is a declared sensitivity, not measured cable/connector data.
    rtheta_contact=20.;temperature=ambient_c+current**2*contact_ohm*rtheta_contact
    return dict(input=args,current_a=current,prospective_pretrip_current_a=prospective,
        permission=permit,load_voltage_v=load_voltage,voltage_drop_v=voltage_v-load_voltage if permit else None,
        female_wire_resistance_ohm=rf,male_wire_resistance_ohm=rm,external_loop_resistance_ohm=loop,
        power_w=dict(source=source_power,load=load_power,cable=cable_heat,contacts=contact_heat,
                     solder_terminations=termination_heat,source_internal=source_heat),
        power_balance_residual_w=source_power-load_power-cable_heat-contact_heat-termination_heat-source_heat,
        contact_temperature_hypothesis_c=temperature,contact_thermal_resistance_hypothesis_k_w=rtheta_contact,
        known_fault_detected=fault!='none',
        checks=dict(kirchhoff_balance=abs(source_power-load_power-cable_heat-contact_heat-termination_heat-source_heat)<1e-8,
                    disabled_on_injected_fault=permit or current==0.,
                    current_below_headline_maximum=current<=15.,simultaneous_derating=None,
                    wire_ampacity=None,protective_device_coordination=None,physical_fault_detection=None),
        scope='Steady DC resistor model; ideal injected interlocks. No fuse/I2t, arc, inrush hardware or safety claim')


def precharge(*, voltage_v=24., capacitance_f=.0047, resistance_ohm=10., time_s=.25):
    args=locals();_numbers(args,positive=('voltage_v','capacitance_f','resistance_ohm'),nonnegative=('time_s',))
    decay=exp(-time_s/(resistance_ohm*capacitance_f));v=voltage_v*(1-decay)
    energy_cap=.5*capacitance_f*v*v
    energy_source=capacitance_f*voltage_v*v
    heat=capacitance_f*voltage_v**2/2*(1-decay**2)
    return dict(capacitor_voltage_v=v,current_a=voltage_v/resistance_ohm*decay,
                capacitor_energy_j=energy_cap,source_energy_j=energy_source,resistor_heat_j=heat,
                energy_balance_residual_j=energy_source-energy_cap-heat,
                scope='Ideal RC benchmark only; selected converter capacitance/inrush and resistor ratings open')


def continuity_observation(mapping, *, shorts=()):
    """Independent contact graph test: opens, crossed pins and adjacent shorts.

    mapping contains observed male-pin -> female-pin pairs; shorts joins female
    pins. This verifies a simulated/recorded pin observation, not physical test
    execution or the safety integrity of detection electronics.
    """
    if not isinstance(mapping,dict) or any(type(k) is not int or type(v) is not int
            or not 1<=k<=10 or not 1<=v<=10 for k,v in mapping.items()):
        raise ValueError('integer observed contact pins 1..10 required')
    parent={side+str(i):side+str(i) for side in ('M','F') for i in range(1,11)}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    def union(a,b):parent[find(a)]=find(b)
    for male,female in mapping.items():union('M'+str(male),'F'+str(female))
    for pair in shorts:
        if len(pair)!=2 or any(type(p) is not int or not 1<=p<=10 for p in pair):
            raise ValueError('shorted pin pair 1..10 required')
        union('F'+str(pair[0]),'F'+str(pair[1]))
    open_pins=[i for i in range(1,9) if find('M'+str(i))!=find('F'+str(i))]
    unintended=[]
    for male in range(1,11):
        for female in range(1,11):
            if male!=female and find('M'+str(male))==find('F'+str(female)):
                unintended.append([male,female])
    return dict(passed=not open_pins and not unintended,open_or_misrouted_active_pins=open_pins,
                unintended_cross_connections=unintended,observed_mapping={str(k):v for k,v in mapping.items()},
                shorts=[list(s) for s in shorts],physical_execution=False,
                scope='Connectivity test oracle for supplied observations; no energisation or authenticated measurement')


def connectivity_faults():
    nominal={i:i for i in range(1,11)}
    opened=dict(nominal);opened.pop(1)
    reversed_map=dict(nominal);reversed_map.update({1:2,2:1})
    mismated={i:11-i for i in range(1,11)}
    return dict(nominal=continuity_observation(nominal),open=continuity_observation(opened),
                short=continuity_observation(nominal,shorts=[(1,2)]),
                reversed=continuity_observation(reversed_map),mis_mate=continuity_observation(mismated))


def harness(candidate_revision):
    """Both halves and every contact are counted once through kit decomposition."""
    nets=['24V-fused','LV-return','lock-sense','lock-return','data-A','data-B','temperature','temperature-return']
    pins=[];wires=[]
    for pin in range(1,11):
        net=nets[pin-1] if pin<=8 else 'reserved-'+str(pin)
        pins.append(dict(pin=pin,net=net,active=pin<=8,
                         endpoints=['vehicle-J1:'+str(pin),'cassette-J1:'+str(pin)],
                         numbering_basis='C00542: matching pin IDs; female mating-face view mirrored',
                         contacts=['M80-335','M80-326']))
        if pin<=8:
            for side,awg,length,contact in [('cassette',14,.8,'M80-326'),('vehicle',12,1.,'M80-335')]:
                wires.append(dict(id=side+'-W'+str(pin),net=net,pin=pin,awg=awg,area_m2=awg_area(awg),
                    cut_length_m=length,cut_length_tolerance_m=.005,length_basis='Proposed cut length; physical route requires regeneration',
                    connector_contact=contact,connector_termination='solder cup, IS-52 issue2',
                    minimum_strip_length_m=.005,other_endpoint=side+'-terminal-block:'+str(pin),
                    other_termination='selected screw/clamp terminal required; no unselected crimp assumed',
                    insulation_part=None,bend_radius_m=None,shield_or_pair_qualification=None,
                    wire_identification=side+'-W'+str(pin)+' / '+net,geometry_complete=False))
    bom=[dict(id='cassette-J1-kit',part=FEMALE,quantity=1,origin='GB supplier page',
              includes=[dict(part='female housing+floating jackscrews',quantity=1),dict(part='M80-326',quantity=10)],
              note='Ten included loose solder contacts; not ten additional purchased contacts'),
         dict(id='vehicle-J1-kit',part=MALE,quantity=1,origin='GB supplier page',
              includes=[dict(part='male housing+internal-thread jackscrews',quantity=1),dict(part='M80-335',quantity=10)],
              note='Mating list includes exact female kit; 12AWG on vehicle side'),
         dict(id='unused-contact-control',part='included M80-326/M80-335 contacts',quantity=4,
              procurement_quantity=0,note='Two reserved positions each half: retain unconnected contacts and cap solder cups; no spare wires'),
         dict(id='termination-sleeves',part='FIT221-1/8-0 supplier process reference',quantity=16,
              specification_qualified=False,cut_length_m=None),
         dict(id='female-wire',part='14 AWG selected rail cable required',quantity_m=6.4,exact_part=None),
         dict(id='male-wire',part='12 AWG selected rail cable required',quantity_m=8.,exact_part=None),
         dict(id='chassis-bond',part='proposed 10mm2 flexible bond, 150mm plus terminal allowance',quantity=1,
              terminals='two M8 ring terminals; exact lugs/tool/die and measured resistance required',
              exact_part=None,fault_current_a=None,clearing_time_s=None),
         dict(id='backshell',part=None,quantity=0,note='Both product kits list no backshell; designed strain relief and sleeve remain separate'),
         dict(id='clamp-linings',part=None,quantity=2,thickness_m=.001,qualification=False),
         dict(id='duct-flange-seals',part=None,quantity=2,thickness_m=.003,qualification=False),
         dict(id='inspection-cover',part='proposed folded sheet cover',quantity=1,dimensions_m=[1.2,.35,.0015],
              captive_fasteners=8,geometry_complete=False),
         dict(id='guided-retention-kit',part=None,quantity=1,note='Guides, captive fasteners and seat/lock switches not fully modelled'),
         dict(id='branch-protection',part=None,quantity=1,note='Rated protective disconnect/fuse, polarity protection and fault-return coordination open'),
         dict(id='terminal-blocks',part=None,quantity=2,note='Eight ways per side; current/fire/vibration/creepage selection open')]
    return dict(unit_revision=candidate_revision,pin_count=10,active_pin_count=8,reserved_pin_count=2,
                pins=pins,wires=wires,bom=bom,source_cards=deepcopy(SOURCE_CARDS),
                exact_mating_pair_documented=True,complete_manufacturing_harness=False,
                proposed_single_line=['vehicle 24V source','isolating/protective disconnect (unselected)',
                    'vehicle eight-way terminal block','12AWG loom + male335 solder contacts',
                    'mated J1','female326 solder contacts + 14AWG loom','cassette terminal block','load/controller'],
                isolation_boundary='LV functional circuit, separate protective chassis bond; HV isolation not represented',
                schematic=dict(power=['source+','disconnect','J1:1','load+'],return_path=['load-','J1:2','source-'],
                               lock_loop=['controller','J1:3','positive-lock-switch','J1:4','controller'],
                               data_pair=['J1:5','J1:6'],temperature_loop=['J1:7','sensor','J1:8'],
                               protective_bond=['vehicle-chassis','bond-conductor','cassette-earth-stud']),
                manufacturing_process=['verify kit/contact/wire identities','cut and identify cable','fit sleeve before termination',
                    'strip at least 5mm per IS-52; qualify strand damage and exposure upper limit',
                    'solder supported conductor into correct cup; controlled alloy/flux/iron profile remains open',
                    'clean and inspect; insert retained contact; verify mirrored pin mapping',
                    'fit sleeve and independent strain relief; leave four reserved contacts insulated',
                    'verify 16 live wires continuity, adjacent shorts and insulation with approved limits',
                    'record actual pin views, serial, operator, measured resistance and test fixture revision'])


def duct_case(area_m2, *, fault='none', ambient_c=50., supply_c=26., return_c=30.,
              humidity_in=.015,humidity_out=.010,flow_target_m3_s=.08):
    """Coupled quadratic fan/network and dry-air/water/enthalpy accounting.

    Fan curve, leak resistance and filter losses are hypotheses. Cooling and
    dehumidification demands are reported even when no refrigeration is selected.
    """
    vals=locals().copy();_numbers(vals,positive=('area_m2','flow_target_m3_s'),nonnegative=('humidity_in','humidity_out'))
    if not all(isfinite(x) for x in (ambient_c,supply_c,return_c)):raise ValueError('finite temperatures required')
    if fault not in {'none','blockage','leak','fan-fault','loaded-filter'}:raise ValueError('unknown duct fault')
    rho=1.1;cp=1005.;latent=2.45e6;width=.2;height=area_m2/width;dh=2*width*height/(width+height)
    friction=.025*.9/dh;local=3.;effective_area=area_m2*(.25 if fault=='blockage' else 1.)
    resistance=rho/2*(friction+local)/effective_area**2+120./.08**2*(3 if fault=='loaded-filter' else 1.)
    # A parallel leak path sees the same pressure as the useful downstream branch.
    leak_coefficient=.0003 if fault=='leak' else 0. # m3/s/Pa**.5, uncalibrated
    conductance=1/sqrt(resistance)+leak_coefficient
    fan_p0=300. if fault!='fan-fault' else 0.;fan_k=20000.
    pressure=fan_p0/(1+fan_k*conductance**2)
    useful=sqrt(pressure/resistance) if pressure else 0.;leak=leak_coefficient*sqrt(pressure)
    total=useful+leak;mdry=rho*useful
    sensible=mdry*cp*(ambient_c-supply_c)
    removed_water=mdry*max(humidity_in-humidity_out,0.)
    moisture_added=mdry*max(humidity_out-humidity_in,0.)
    latent_power=removed_water*latent
    entering_enthalpy=mdry*(cp*ambient_c+latent*humidity_in)
    leaving_enthalpy=mdry*(cp*supply_c+latent*humidity_out)
    conditioning=sensible+latent_power-moisture_added*latent
    air_power=pressure*total;fan_eff=.5
    fan_input=air_power/fan_eff if total else 0.
    return dict(inputs=vals,flow_m3_s=total,useful_flow_m3_s=useful,leak_flow_m3_s=leak,
        hydraulic_diameter_m=dh,pressure_pa=pressure,velocity_m_s=useful/effective_area,
        fan_curve_residual_pa=fan_p0-fan_k*total**2-pressure,
        branch_pressure_residual_pa=pressure-resistance*useful**2,
        dry_air_mass_kg_s=mdry,mass_balance_residual_m3_s=total-useful-leak,
        sensible_demand_w=sensible,latent_demand_w=latent_power,conditioning_demand_w=conditioning,
        entering_enthalpy_w=entering_enthalpy,leaving_enthalpy_w=leaving_enthalpy,
        heat_balance_residual_w=entering_enthalpy-leaving_enthalpy-conditioning,
        condensate_kg_s=removed_water,moisture_added_kg_s=moisture_added,
        water_balance_residual_kg_s=mdry*humidity_in+moisture_added-mdry*humidity_out-removed_water,
        fan_input_w=fan_input,air_power_w=air_power,fan_waste_heat_w=fan_input-air_power,
        return_sensible_transfer_w=mdry*cp*(return_c-supply_c),
        checks=dict(conservation=abs(entering_enthalpy-leaving_enthalpy-conditioning)<1e-7
                    and abs(total-useful-leak)<1e-10 and abs(mdry*humidity_in+moisture_added-mdry*humidity_out-removed_water)<1e-10,
                    proposed_flow_target=useful>=flow_target_m3_s,fan_supplier_map=None,
                    installed_leak_acceptance=None,refrigeration_capacity=None),
        scope='Idealised duct/fan and wet-air balance; no refrigerant circuit, comfort, noise or CO2 qualification')


def whole_car_duty():
    a=dict(passengers=100,passenger_sensible_w=75.,passenger_latent_w=55.,solar_w=7000.,
           equipment_w=3000.,fresh_air_m3_s=.5,infiltration_door_average_m3_s=.3,
           outdoor_c=50.,target_c=26.,outdoor_humidity_ratio=.015,indoor_humidity_ratio=.010,
           envelope_ua_w_k=250.,air_density_kg_m3=1.1,cp_j_kg_k=1005.,latent_j_kg=2.45e6)
    q=a['fresh_air_m3_s']+a['infiltration_door_average_m3_s'];m=q*a['air_density_kg_m3']
    delta=a['outdoor_c']-a['target_c']
    sensible=a['passengers']*a['passenger_sensible_w']+a['solar_w']+a['equipment_w']+(m*a['cp_j_kg_k']+a['envelope_ua_w_k'])*delta
    latent=a['passengers']*a['passenger_latent_w']+m*a['latent_j_kg']*(a['outdoor_humidity_ratio']-a['indoor_humidity_ratio'])
    return dict(assumptions=a,sensible_w=sensible,latent_w=latent,total_conditioning_w=sensible+latent,
                condensate_demand_kg_s=latent/a['latent_j_kg'],all_assumptions_provisional=True,
                hot_soak_time_history=None,co2_model=None,humidity_comfort_adopted=False,
                roof_surface_temperature_used_as_air=False,selected_refrigeration_module=None,
                scope='One-zone duty hypothesis; actual occupancy, solar, glazing, doors, humidity, fresh-air/CO2 and transient maps required')


def tolerance_stack(*, clearance_m=.003, manufacturing_m=.0005, counterpart_m=.0005,
                    weld_distortion_m=.001,survey_m=.001,length_m=1.2,
                    expansion_per_k=12e-6,delta_k=70.,connector_float_m=.001):
    vals=locals().copy();_numbers(vals,nonnegative=tuple(vals))
    thermal=length_m*expansion_per_k*delta_k
    worst=manufacturing_m+counterpart_m+weld_distortion_m+survey_m+thermal
    return dict(assumptions=vals,worst_case_offset_m=worst,thermal_movement_m=thermal,
                guide_margin_m=clearance_m-worst,connector_float_margin_m=connector_float_m-worst,
                checks=dict(guide_fit=clearance_m>=worst,connector_float=connector_float_m>=worst),
                statistical_yield=None,scope='Worst-case stack only; process distributions and actual vehicle survey absent')


def process_graph(revision):
    specs=[
        ('identity',[],['kit','tray-floor'],'inspection bench','documents',[],['identity/materials']),
        ('bench-harness',['identity'],['vehicle-J1','cassette-J1'],'solder fixture','solder/rework kit',[],['pin map','continuity','shorts']),
        ('bench-duct',['identity'],['duct','duct-flange-seals'],'sealed flow fixture','pressure/flow instruments',[],['leak','flow']),
        ('bench-cover-clamps',['identity'],['inspection-cover','clamp-linings'],'datum fixture','torque tool',[],['clamp pull','cover fit']),
        ('bench-tests',['bench-harness','bench-duct','bench-cover-clamps'],['cassette'],'bench test stand','test fixture',[],['electrical','bond','flow']),
        ('transport-restraint',['bench-tests'],['cassette','restraints'],'transport cradle','restraint tool',[],['identity','transport damage']),
        ('temporary-locate',['transport-restraint'],['cassette','vehicle-runner'],'lifting/support fixture','handling device',[[ -1.3,0,0],[0,0,0]],['datums','temporary support']),
        ('final-lock',['temporary-locate'],['mount-0','mount-1','mount-2','mount-3'],'retained module','torque tool',[],['four fasteners','positive lock','secondary retention']),
        ('bond',['final-lock'],['earth-stud','vehicle-earth'],'retained module','torque/resistance tool',[],['bare-metal contact','locking','bond resistance']),
        ('connect-services',['bond'],['cassette-J1','vehicle-J1','duct-ports'],'retained module','jackscrew driver',[],['polarisation','jackscrews','seals']),
        ('installed-test',['connect-services'],['cassette','vehicle'],'isolated test supply','test fixture',[],['lock','earth','continuity','leak','functional interface']),
        ('isolate',['installed-test'],['source','cassette'],'lockout fixture','voltage instrument',[],['zero energy']),
        ('disconnect-services',['isolate'],['cassette-J1','vehicle-J1','duct-ports'],'supported module','jackscrew driver',[],['disconnected/capped']),
        ('unbond',['disconnect-services'],['earth-stud','vehicle-earth'],'supported module','torque tool',[],['bond removed after services']),
        ('unlock',['unbond'],['mount-0','mount-1','mount-2','mount-3'],'temporary support','torque tool',[],['support before unlock']),
        ('withdraw',['unlock'],['cassette','vehicle-runner'],'handling fixture','handling device',[[0,0,0],[-1.3,0,0]],['removal clearance','damage'])]
    operations=[]
    for name,deps,ends,fixture,tool,path,qa in specs:
        operations.append(dict(id=name,unit_revision=revision,dependencies=deps,endpoints=ends,fixture=fixture,tool=tool,
            insertion_path_m=path,rotation_path_rad=[],tool_access_envelope_m=[.1,.1,.15],
            human_access_envelope_m=[.6,.6,.8],access_basis='Proposed; actual vehicle geometry and physical demonstration absent',
            duration_person_s=None,fastening_torque_nm=None,curing_time_s=None,qa_characteristics=qa,
            serial=None,executed=False,accepted=False))
    return operations


def sequence_check(operations, completed):
    """Validate symbolic dependency/order; missing or duplicate actions fail."""
    known={o['id']:o for o in operations};seen=set();errors=[]
    for name in completed:
        if name not in known:errors.append('unknown operation '+str(name));continue
        if name in seen:errors.append('duplicate operation '+name);continue
        missing=set(known[name]['dependencies'])-seen
        if missing:errors.append(name+' lacks '+','.join(sorted(missing)))
        seen.add(name)
    return dict(passed=not errors,errors=errors,completed=completed,
                installed_test_reached='installed-test' in seen and not errors,
                removal_reached='withdraw' in seen and not errors,
                scope='Symbolic planned sequence; no executed physical or collision test')


def swept_path(*, length_m=1.2,width_m=.35,height_m=.21,travel_m=1.3,obstacles=()):
    vals=locals().copy();_numbers(vals,positive=('length_m','width_m','height_m','travel_m'))
    swept=[[-travel_m-length_m/2,-width_m/2,-.06],[length_m/2,width_m/2,height_m-.06]]
    hits=[]
    for obs in obstacles:
        bounds=obs['bounds_m']
        if len(bounds)!=2 or any(len(row)!=3 for row in bounds):raise ValueError('3D obstacle bounds required')
        if not all(isfinite(v) for row in bounds for v in row) or any(bounds[0][i]>bounds[1][i] for i in range(3)):
            raise ValueError('ordered finite obstacle bounds required')
        if all(swept[0][i]<bounds[1][i] and bounds[0][i]<swept[1][i] for i in range(3)):hits.append(obs['id'])
    return dict(swept_bounds_m=swept,colliding_obstacles=hits,clear_in_supplied_aabb_scene=not hits,
                installed_vehicle_scene_supplied=bool(obstacles),actual_vehicle_access_verified=False,
                scope='Axis-aligned translational envelope; no fine collision, deflection, manipulation or human ergonomics proof')


def assembly_comparison(operations):
    changes=sum(a['tool']!=b['tool'] for a,b in zip(operations,operations[1:]))
    return [dict(architecture=name,operation_count=len(operations),tool_changes_for_reference_graph=changes,
        factory_person_hours=None,site_person_hours=None,critical_path_s=None,working_at_height_person_hours=None,
        first_pass_yield=None,misassembly_rate=None,rework_person_hours=None,repair_time_s=None,lifts=None,
        installed_cost=None,currency='GBP',production_volume=None,cost_calibrated=False,
        connection_details_complete=False,comparison_status='unranked; measured times, quoted hardware and complete architecture-specific graph required')
        for name in ('conventional-fasteners','guided-captive-fasteners','qualified-quick-lock-candidate')]


OPEN_GATES=[
    'Actual routed 14AWG cassette and 12AWG vehicle harness geometry, all terminal blocks, sleeves, shields and bend radii',
    'Offered connector/simultaneous temperature-current derating and selected cable insulation/ampacity/fire qualification',
    'Solder process/alloy/flux/thermal profile, workmanship acceptance, pull and vibration/environment testing',
    'Branch protective-device interruption/I2t/selectivity, fault return, reverse protection, insulation and EMC architecture',
    'Qualified bond terminals, tool/die, fault-current/clearing-time sizing and measured installed bond resistance',
    'Owned cover, compliant clamps, duct flange seals, guides, retained lock/secondary retention detailed CAD and manufacturing drawings',
    'Whole-car HVAC duty/CO2/humidity and climate histories, hot-soak transient, fan/filter/cooling supplier maps and refrigeration circuit',
    'Actual removal/tool/human access scene, qualified insertion/release/wear limits and demonstrated serial-specific assembly/removal',
    'Measured assembly time/yield/cost and intended-volume quotations for all three architectures',
    'Authenticated physical leak/flow/earth/pull/lock, vibration/environment/fire, factory and installed acceptance records',
]


def report(policy,candidate):
    from . import models
    if candidate.get('kind')!='service-cassette':raise ValueError('service cassette candidate required')
    if core.digest(candidate)!=core.digest(models.build(policy,candidate['kind'],candidate['variables'])):
        raise ValueError('stale or modified generator candidate')
    revision=candidate['revision'];a=policy['pilots']['service-cassette']['assumptions'];area=candidate['metadata']['duct_clear_area_m2']
    loom=harness(revision)
    load=a['lv_voltage_v']/a['branch_current_a']
    electrical=[electrical_case(voltage_v=a['lv_voltage_v']*ratio,ambient_c=t,load_ohm=load)
                for ratio in (.75,1.,1.25) for t in a['temperature_sensitivity_c']]
    faults=[electrical_case(fault=f,voltage_v=a['lv_voltage_v'],load_ohm=load)
            for f in ('open-supply','open-return','open-bond','short','reversed','mis-mate','unlock')]
    ducts=[duct_case(area,fault=f,flow_target_m3_s=a['duct_flow_m3_s'])
           for f in ('none','blockage','leak','fan-fault','loaded-filter')]
    graph=process_graph(revision);sequence=sequence_check(graph,[n['id'] for n in graph])
    stack=tolerance_stack(clearance_m=a['clearance_m'],manufacturing_m=a['dimensional_tolerance_m'],
                          counterpart_m=a['dimensional_tolerance_m'],length_m=a['length_m'])
    cad=candidate['metadata']['netlist']
    topology=dict(active_pin_count_matches=len([p for p in loom['pins'] if p['active']])==len(cad.get('active_pins',[])),
        conductor_count_matches=sum(p['id'].endswith('-conductor') and p['id'].startswith('wire-') for p in candidate['contract']['parts'])==8,
        conductor_area_matches=abs(cad.get('reference_conductor_area_m2',0)-awg_area(14))<1e-15,
        all_terminals_and_routes_in_native_geometry=False,mating_supplier_internal_geometry=False)
    checks=dict(electrical_power_conservation=all(abs(c['power_balance_residual_w'])<1e-8 for c in electrical+faults),
        injected_fault_disable=all(not c['permission'] and c['current_a']==0 for c in faults),
        wet_air_conservation=all(c['checks']['conservation'] for c in ducts),
        nominal_duct_flow_target=ducts[0]['checks']['proposed_flow_target'],
        process_dependencies=sequence['passed'],reference_harness_topology=all(topology[k] for k in ('active_pin_count_matches','conductor_count_matches','conductor_area_matches')),
        worst_case_guide_fit=stack['checks']['guide_fit'],worst_case_connector_float=stack['checks']['connector_float'],
        connector_derating=None,protection_coordination=None,actual_removal_access=None,physical_qualification=None)
    # Nominal useful-flow duty is mandatory. Fault-case flow loss is retained
    # separately, with degraded acceptance still open; do not silently promote
    # a nominally undersized duct because its conservation equations balance.
    checks.update({'nominal-duct/'+key:value for key,value in ducts[0]['checks'].items()})
    result=dict(schema='osr-service-cassette-chain/1',unit_revision=revision,policy_sha256=core.digest(policy),
        requirements=['baghdad:ME-10','baghdad:ME-11'],source_cards=deepcopy(SOURCE_CARDS),harness=loom,
        electrical_cases=electrical,electrical_faults=faults,connectivity_faults=connectivity_faults(),
        precharge_benchmark=precharge(),duct_cases=ducts,
        whole_car_duty=whole_car_duty(),process_graph=graph,planned_sequence_check=sequence,
        assembly_comparison=assembly_comparison(graph),tolerance_stack=stack,
        guided_clearance_sensitivity=tolerance_stack(clearance_m=.006,connector_float_m=.006),
        removal_envelope=swept_path(),cad_harness_correspondence=topology,checks=checks,
        failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        open_gates=OPEN_GATES,digital_specification_complete=False,physical_qualification=False,
        production_qualification=False,scope='Revision-bound coupled provisional service chain; exact supplier solder detail and executable conservation/fault/process screens; manufacturing and physical gates remain open',**core.FLAGS)
    result['revision']=core.digest(result)
    return result


def verify_report(policy,candidate,value):
    if core.digest(value)!=core.digest(report(policy,candidate)):raise ValueError('cassette chain or candidate revision differs')
    return True
