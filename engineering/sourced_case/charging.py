"""Source-rated charging proposals and conditional SOC time integration.

Every proposal is separate hardware identity. It does not install extra converters
in the input train or authenticate a CCS/QCC interface, SOC curve or thermal duty.
"""
from copy import deepcopy
from math import ceil,isfinite
from pathlib import Path
from engineering.component_registry import make_part,make_occurrence
from . import ROOT,FLAGS,identity,digest
from . import commerce

PRODUCER='engineering/sourced_case/charging.py'
SUPPLY_SOURCE=dict(url='https://cache.industry.siemens.com/dl/files/320/109796320/att_1334746/v4/sicharge_d_300_operating_instructions_en-US_en-US.pdf',sha256='ac2ea90fc033e3bc4c0ccb7615c813b9a802dd7190994214b56d918b77a812b3',bytes=37051287,retrieved_date='2026-10-28',source_class='B',scope='SICHARGE D300 manual10/2025 pp210–212;500A liquid-cooled CCS2, nonERK variant')
QCC_SOURCE=dict(url='https://www.staubli.com/content/dam/ecs/catalogs-brochures/EMOB/APP-QCC-Quick-Guide-11014055-en.pdf',sha256='1ab6cb4dc3f522e279cf8c57310f4ac00ea1e95ddecdbc6b87f37b2f95ddc02d',bytes=1478451,retrieved_date='2026-10-28',source_class='B',scope='QCC quickguide:650/1500 actuator/counterpart and minimum2.3×.8×1m enclosure; complete masses absent')
QCC_RATING_SOURCE=dict(url='https://www.staubli.com/us/en/electrical-connectors/products/multi-pole-connectors/qcc.html',sha256=None,retrieved_via='primary-web-tool-2026-10-28; direct-byte retrieval403',source_class='B',scope='QCC family up1500V,670Acontinuous; exact delivered model/drawing/current derating pending')


def _seal(x):x['evaluation_id']=identity(x);return x


def _number(x,name,positive=False):
    if type(x) not in (float,int) or not isfinite(x) or x<0 or positive and x<=0:raise ValueError('Finite '+name+' required')
    return float(x)


def _sealcheck(x):
    if x.get('evaluation_id')!=identity({k:v for k,v in x.items() if k!='evaluation_id'}):raise ValueError('Charging input evaluation identity differs')


def design(equipment_result,journey,terminal_layover_s,*,initial_SOC=.60,charge_policy='recommended',
           converter_efficiency=.90,station_supply_fraction=1.,station_ambient_C=50.,
           converter_air_C=40.,soc_taper_start=.80,soc_taper_factor=.5,dt_s=.25,root=ROOT):
    """Size additional onboard converters against actual model journey energy.

    Uses energy_J.auxiliary for the entire six-car train and its sealed scenario.
    All SOC/voltage/taper/efficiency assumptions are explicit evaluation inputs.
    Source supply caps apply at reference conditions; hot-site output is unknown.
    """
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executing charging source differs')
    commerce._check_equipment(equipment_result);_sealcheck(journey)
    if journey['body_candidate_id']!=equipment_result['candidate_id']:raise ValueError('Mixed journey/equipment body candidate')
    for value,name in ((terminal_layover_s,'layover'),(initial_SOC,'SOC'),(converter_efficiency,'efficiency'),(station_supply_fraction,'supplyfraction'),(soc_taper_start,'taperstart'),(soc_taper_factor,'taperfactor'),(dt_s,'time step')):_number(value,name,True)
    if not 0<initial_SOC<=1 or not 0<converter_efficiency<=.98 or not 0<station_supply_fraction<=1 or not 0<soc_taper_start<1 or not 0<soc_taper_factor<=1 or not .05<=dt_s<=1 or terminal_layover_s>1800:raise ValueError('Bounded physical charging hypotheses required')
    if charge_policy not in ('recommended','maximum'):raise ValueError('Explicit recommended ormaximum charge policy required')
    for value in (station_ambient_C,converter_air_C):
        if type(value) not in (int,float) or not isfinite(value):raise ValueError('Finite source temperature required')
    cars=equipment_result['vehicle']['requirements']['cars'];time=_number(journey['journey_time_s'],'journey duration',True)
    energy=_number(journey['energy_J']['auxiliary'],'recorded auxiliary energy')/cars
    aux=_number(journey['scenario']['auxiliary_W_per_car'],'auxiliary power')
    if abs(energy-aux*time)>max(.01,1e-5*energy):raise ValueError('Journey auxiliary energy/time conservation differs')
    a=equipment_result['architecture'];np=a['battery_parallel_strings']
    if a['battery_series_modules']!=2 or not 2<=np<=25:raise ValueError('SourcedNG2s2–25p configuration required')
    capacity_Wh=2*np*5120.;lowV=44.8;highV=600.;bms=1000.
    current=np*(100. if charge_policy=='recommended' else 200.)
    # In charging direction115A is LV OUTPUT current, not input current.
    each_out=min(5500.*converter_efficiency,600.*10.*converter_efficiency,lowV*115.)
    needed_out=energy/terminal_layover_s+aux
    required=max(1,ceil(needed_out/each_out));existing=a.get('converter_units_per_car',3)
    battery_only_charge_cap=lowV*min(current,bms)
    total_LV_cap=lowV*bms # conservative common1000A trunk assumption
    supplycap=300000.*station_supply_fraction
    temp_ok=-10<=converter_air_C<=40
    source_reference=dict(EPC_nominal_W=5500.,EPC_LV_continuous_A=115.,EPC_HV_continuous_A=10.,
       EPC_LV_range_V=[38,59],EPC_HV_range_V=[510,848],EPC_air_range_C=[-10,40],
       supply_voltage_range_V=[150,1000],supply_total_W=300000.,supply_cable_current_A=500.,supply_current_reference_C=35.,
       supply_reference_current_known_at_selected_ambient=station_ambient_C<=35,
       supply_at_selected_hot_ambient_W=None if station_ambient_C>35 else 300000.,QCC_family_max_voltage_V=1500.,QCC_family_continuous_A=670.)
    proposal=dict(parent_body_candidate_id=equipment_result['candidate_id'],station_supply_model='SiemensSICHARGE D300 nonERK500AcooledCCS2',
       nominal_station_voltage_V=600.,required_total_EPC_per_car=required,existing_EPC_per_car=existing,
       additional_EPC_per_car=max(0,required-existing),QCC_family='1500V/670A-family; exact delivered variant pending',
       station_connector_count=cars,train_socket_count=cars,station_supply_count=1,
       station_actuator_minimum_enclosure_m=[1.,2.3,.8],sixcar_pitch_m=17.5)
    # Actual BOM and rigid placements belong to this new proposal identity.
    def part(name,dims,bounds,scope,source,role):
        return make_part('OSR-CHARGING-'+name,'H1',['auxiliary-power'],dict(kind='envelope',dimensions_m=dims,net_volume_m3=None),None,
          dict(calculated_kg=None,lower_bound_kg=bounds[0],upper_bound_kg=bounds[1],evidence_state='bounded-estimate',bounds_basis=role,bounds_source_class='B' if name=='SIEMENS300' else 'C'),
          dict(method='purchase-fabricate-install-inspect',cycle_hours=None,scrap_fraction=None),
          assembly=dict(scope=scope,role=role,fastener_grade_and_retention_approved=False),
          evidence=dict(source_record_id=identity(source),source_class='B' if source else 'C',installation_accepted=False))
    supply=part('SIEMENS300',[1.251,.825,2.4],[540.,820.],'station',SUPPLY_SOURCE,'Published cabinet range depending onconfiguration, inclcable management; selectedvariant weight unconfirmed')
    actuator=part('QCC-ACD-ASSEMBLY',[1.,2.3,.8],[60.,160.],'station',QCC_SOURCE,'Minservice enclosure fromsource; massClassC actuator/structure allowance, notmanufacturer weight')
    socket=part('QCC-SOCKET',[.4,.4,.30],[15.,50.],'train',QCC_SOURCE,'Socket/funnel/retention researchenvelope andmass; delivered drawing required')
    protection=part('STATION-DC-BRANCH-CABINET',[1.,.5,1.5],[80.,200.],'station',{},'600Vsix-branch fuses/contactors/isolationcontroller/cooling wiring allowance')
    mounting=part('STATION-FOOTING-ANCHOR-COOLING',[1.8,1.4,.35],[400.,1000.],'station',{},'Foundation/anchors/mounting/cooling allowance; geotechnics/rebar/duct geometrypending')
    contact_wire=part('BRANCH-CABLE-LOOM',[17.5,.08,.08],[15.,35.],'station',{},'One17.5m six-conductor shielded600Vbranch inclPE/signals; crosssections/bends/heat unqualified')
    epcs=[p for p in equipment_result['vehicle']['registry']['parts'] if p['part_id']=='OSR-SOURCED-EPC5K5648I']
    if len(epcs)!=1:raise ValueError('Actual source-bound existing EPC definition required')
    epc=deepcopy(epcs[0]);parts=[supply,actuator,socket,protection,mounting,contact_wire]+([epc] if required>existing else [])
    occ=[]
    def put(name,p,x,y,z,scope,parent):
        pose=[[1.,0.,0.,float(x)],[0.,1.,0.,float(y)],[0.,0.,1.,float(z)],[0.,0.,0.,1.]]
        occ.append(make_occurrence(name,p,parent,pose,scope))
    put('station/supply',supply,-3.,4.,1.2,'station','station')
    put('station/protection',protection,-1.,4.,.75,'station','station')
    put('station/foundation',mounting,-3.,4.,-.175,'station','station')
    for car in range(cars):
        x=8.5+17.5*car
        put(f'station/ACD-{car+1}',actuator,x,3.,.6,'station','station')
        put(f'station/cable-{car+1}',contact_wire,x,3.,.2,'station','station')
        put(f'train/socket-{car+1}',socket,x,1.4,.6,'train',f'car-{car+1}')
        for n in range(max(0,required-existing)):
            put(f'train/extra-EPC-{car+1}-{n+1}',epc,4.1+.27*n+17.5*car,-1.05,.62,'train',f'car-{car+1}')
    physical=dict(proposal=proposal,part_definition_ids=[p['physical_definition_id'] for p in parts],
       occurrences=[{k:o[k] for k in ('occurrence_id','part_definition_id','parent_id','transform','scope','pose_frame')} for o in occ])
    assemblies=[dict(id='station',parent_id=None),dict(id='train',parent_id=None)]+[dict(id=f'car-{n+1}',parent_id='train') for n in range(cars)]
    physical['assemblies']=assemblies
    cid=identity(physical)
    for o in occ:o['candidate_id']=cid
    def run(failed):
        stored=initial_SOC*capacity_Wh*3600-energy;start=stored;trace=[dict(time_s=0.,SOC=stored/(capacity_Wh*3600),phase='post-journey')]
        supplied=losses=0.;t=0.;target=initial_SOC*capacity_Wh*3600
        if stored<0:return dict(execution='fail-initial-energy',trace=trace,restored=False)
        while t<terminal_layover_s-1e-10:
            dt=min(dt_s,terminal_layover_s-t);soc=stored/(capacity_Wh*3600)
            taper=soc_taper_factor if soc>=soc_taper_start else 1.
            cap=min(max(0,required-failed)*each_out,total_LV_cap,supplycap*converter_efficiency/cars)
            if not temp_ok:cap=0. # specified source domain denies energization; not missingforce setzero
            netcap=min(max(0.,cap-aux),battery_only_charge_cap*taper)
            desired=min(netcap,max(0.,target-stored)/dt)
            actual_out=min(cap,aux+desired)
            stored+=(actual_out-aux)*dt
            supplied+=actual_out/converter_efficiency*dt;losses+=actual_out*(1/converter_efficiency-1)*dt;t+=dt
            if len(trace)<2 or t-trace[-1]['time_s']>=1.-1e-8 or t>=terminal_layover_s-1e-8:
                trace.append(dict(time_s=t,SOC=stored/(capacity_Wh*3600),LV_current_A=actual_out/lowV,
                  net_battery_charge_current_A=(actual_out-aux)/lowV,HV_current_A=actual_out/converter_efficiency/highV,
                  converter_output_W=actual_out,phase='charging' if desired else 'auxiliary-only',taper_hypothesis_active=soc>=soc_taper_start))
        return dict(execution='conditional-reference-cap-integration',trace=trace,restored=stored>=target-.1,
           end_SOC=stored/(capacity_Wh*3600),restoration_deficit_Wh=max(0,target-stored)/3600,
           delivered_LV_energy_J=supplied*converter_efficiency,HV_source_energy_J=supplied,
           converter_heat_J=losses,energy_residual_J=(stored-start)-(supplied*converter_efficiency-aux*terminal_layover_s),
           actual_taper_curve_authenticated=False)
    nominal=run(0);fault=run(1)
    bypart={p['physical_definition_id']:p for p in parts};mass_bounds={}
    for scope in ('station','train'):
        rows=[o for o in occ if o['scope']==scope]
        mass_bounds[scope]=dict(lower_kg=sum(bypart[o['part_definition_id']]['mass']['lower_bound_kg'] for o in rows),
           upper_kg=sum(bypart[o['part_definition_id']]['mass']['upper_bound_kg'] for o in rows),scope='Counted source/C-bound proposal only; incomplete installed scope')
    knownprice=commerce.price_subtotal(cid,[dict(candidate_id=cid,SKU='EPC5k5648i',occurrence_ids=[o['occurrence_id'] for o in occ if 'extra-EPC' in o['occurrence_id']])],root) if required>existing else None
    return _seal(dict(schema='osr-source-station-charging-proposal/1',candidate_id=cid,body_candidate_id=equipment_result['candidate_id'],
       equipment_evaluation_id=equipment_result['evaluation_id'],journey_candidate_id=journey['candidate_id'],journey_evaluation_id=journey['evaluation_id'],
       physical_definition=physical,physical_definition_id=identity(physical),parts=parts,occurrences=occ,assemblies=assemblies,
       coordinate_frame=dict(origin='train firstnosex0;rail-topz0;platformdoorsnegativey;newchargerledgepositivey',length_unit='m',mass_unit='kg'),
       counted_mass_bounds_by_scope=mass_bounds,
       source_sha256={PRODUCER:digest(root/PRODUCER),**commerce.catalogue(root)['source_sha256']},
       sources=dict(supply=SUPPLY_SOURCE,QCC_layout=QCC_SOURCE,QCC_family_rating=QCC_RATING_SOURCE),
       source_caps=source_reference,assumptions=dict(converter_efficiency=converter_efficiency,efficiency_is_guaranteed_minimum=False,
         initial_SOC=initial_SOC,charge_policy=charge_policy,station_supply_fraction=station_supply_fraction,
         station_ambient_C=station_ambient_C,converter_air_C=converter_air_C,
         energized_window_hypothesis_s=terminal_layover_s,
         actual_connection_isolation_disconnect_time_s=None,actual_energized_window_s=None,
         reference_timing_scope='Best-case full-layover energization necessarybound; actual interface overhead unknown, notzero',
         SOC_taper_start=soc_taper_start,SOC_taper_factor=soc_taper_factor,dt_s=dt_s),
       sizing=dict(journey_s=time,terminal_layover_s=terminal_layover_s,recorded_auxiliary_Wh_per_car=energy/3600,
         auxiliary_power_W_per_car=aux,required_output_W_per_car=needed_out,source_limited_output_W_per_EPC=each_out,
         required_total_EPC_per_car=required,additional_EPC_per_car=max(0,required-existing),BMS_common_trunk_limit_A=bms,
         recommended_battery_charge_A=np*100,maximum_battery_charge_A=np*200,
         train_peak_HV_supply_W=cars*required*each_out/converter_efficiency,
         train_peak_supply_current_A=cars*required*each_out/converter_efficiency/highV,
         percar_QCC_peak_current_A=required*each_out/converter_efficiency/highV,
         maximum_total_connection_disconnect_overhead_s=terminal_layover_s-energy/max(1e-12,min(required*each_out,total_LV_cap,supplycap*converter_efficiency/cars)-aux)),
       nominal=nominal,one_EPC_failure_per_car=fault,partial_public_price=knownprice,
       complete_installed_price_USD=None,complete_installed_mass_kg=None,
       source_ratings_and_soc_model_are_qualified=False,existing_body_silently_modified=False,
       actual_terminal_cycle_restored=None,actual_protected_charging_window_s=None,
       required_onboard_revision=proposal,
       assembly=dict(ACD_fixation_points_per_unit=8,socket_fastener_pattern=None,
         new_EPC_mounting_fasteners_per_car=4*max(0,required-existing),
         power_and_signal_contacts_per_connector='DC+/DC-/PE+5–6signals; exactmodelpending',
         service_envelope_m=[1.,2.3,.8],minimum_bend_radius_m=None,
         proposed_mating_extension_m=.45,mating_stroke_and_alignment_verified=False,
         charging_zone='opposite passengerdoor side; requiresnewprotectedstructuralequipmentledge',
         dedicated_support_ledge_structurally_defined=False,
         installation_sequence=['isolate-and-prove-dead','anchor-charger-and-ACD-enclosures','install-protected-cable-trunk','mount-counterparts-and-retainers','verify-contact-sequence-and-emergency-isolation','commission-CCS/QCCcontroller-with-no-motion-interlock'],
         removal_sequence=['isolate-and-prove-dead','support-module-with-rated-lifting-device','disconnect-labelled-cables-cooling','remove-retainers','withdraw-within-maintenance-enclosure'],
         actual_swept_clearance_proved=False,approved_lifting_points=False),
       open_items=['CCS2toQCCsix-car distribution/vehicle communication is an unqualified integration, notplug-compatiblevendorrelease',
         'Actual SOC/open-circuit-voltage/internal-resistance/temperature/taper curves and repeatedlayover charge tests',
         'Manufacturerhot-site supply derating and converter≤40C conditioned enclosure/cooling proof',
         'Actual connectorvariant masses/drawings/mating delay/cycles/contactresistance/arc/PE/interlock tests',
         'No dispatch before disconnected/proved-safe; GoA4/HIL and independent safety review remainopen',
         'New onboard converters/socket mass must revise canonical vehicle/structures/journeys beforeselection'],**FLAGS))
