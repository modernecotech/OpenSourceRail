"""Compile disjoint leaf parts into a candidate-bound manufacturing proposal.

Physical geometry/material choices and evaluation assumptions have separate
identities. Parent category allowances are never added to this new leaf BOM.
Stock masses and engineering allowances do not become measured installed mass.
"""
from copy import deepcopy
from math import prod,pi,isfinite,fsum,isclose
from pathlib import Path
import json
from engineering.station_rail.common import digest,identity
from engineering.development_baseline import selection
from . import ROOT,FLAGS

SOURCE='engineering/vehicle_parts/catalogue.py'
SECTIONS=('running_gear','body','services')
CASES=('low','base','high')
REQUIRED_PART=('id','assembly_id','name','quantity_per_assembly','unit','material_id','make_buy','stock',
    'mass_each_kg','mass_basis','direct_cost_each_usd','cost_basis','manufacturing','joining','finish',
    'tolerance_and_fits','inspection','mounting','maintenance_removal','open_tasks','source_ids')
COUNTS={'bogie':12,'wheelset':24,'axlebox':48,'intercar-coupler':5,'end-coupler':2,'gangway':5,
    'carbody-frame':6,'floor':6,'side-panels':6,'roof':6,'fixed-seat':264,'wheelchair-place':12,
    'passenger-door':12,'door-leaf':24,'door-window':24,'terminal-window':2,'passage-end':10,'terminal-end':2,'fixed-glazing':6,'lighting':6,'door-electrical':12,'hvac':12,
    'service-battery':6,'gangway-lighting':5,'pneumatics':6,'train-control':6,'intercar-electrical':5,'passive-secondary':6}


def number(value,*,positive=False):
    if type(value) not in (int,float) or not isfinite(value) or (value<=0 if positive else value<0):
        raise ValueError('Finite '+('positive' if positive else 'nonnegative')+' dimensional number required')
    return value


def interval(value,label):
    if not isinstance(value,dict) or set(value)!=set(CASES):raise ValueError(label+' needs low/base/high')
    if all(v is None for v in value.values()):return False
    if any(v is None for v in value.values()):raise ValueError(label+' partial unknown interval is ambiguous')
    values=[number(value[k],positive=True) for k in CASES]
    if values!=sorted(values):raise ValueError(label+' bounds must enclose base')
    return True


def stock_volume(stock):
    if stock is None:return None
    if not isinstance(stock,dict):raise ValueError('Typed stock or explicit unknown required')
    kind=stock.get('kind')
    if kind in ('box','envelope'):
        sizes=stock['size_m']
        if not isinstance(sizes,list) or len(sizes)!=3:raise ValueError('Three explicit SI stock dimensions required')
        for n in sizes:number(n,positive=True)
        return prod(sizes) if kind=='box' else None
    if kind=='u_channel':
        L,b,h,t=[number(stock[k],positive=True) for k in ('length_m','width_m','depth_m','wall_m')]
        if 2*t>=b or t>=h:raise ValueError('U-channel needs positive internal dimensions')
        return L*(b*t+2*(h-t)*t)
    if kind=='rhs':
        L,b,h,t=[number(stock[k],positive=True) for k in ('length_m','width_m','depth_m','wall_m')]
        if 2*t>=min(b,h):raise ValueError('Hollow stock needs positive internal dimensions')
        return L*(b*h-(b-2*t)*(h-2*t))
    if kind in ('cylinder','annulus'):
        L=number(stock['length_m'],positive=True)
        R=number(stock['radius_m'] if kind=='cylinder' else stock['outer_radius_m'],positive=True)
        r=0. if kind=='cylinder' else number(stock['inner_radius_m'])
        if r>=R:raise ValueError('Annulus needs positive wall')
        return pi*(R*R-r*r)*L
    if kind=='cut-length':number(stock['length_m'],positive=True);return None
    raise ValueError('Unsupported dimensional stock representation')


def _unreleased(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k in FLAGS and v is not False:raise ValueError('Part catalogue cannot grant '+k)
            _unreleased(v)
    elif isinstance(value,list):
        for v in value:_unreleased(v)


def load_sections(root=ROOT):
    return [json.loads((Path(root)/'engineering/vehicle_parts/data'/(n+'.json')).read_bytes()) for n in SECTIONS]


def validate_sections(sections,parent_candidate_id):
    if len(sections)!=3 or {s['section_id'] for s in sections}!={'running','body','services'}:raise ValueError('All three independent vehicle sections required')
    materials={};assemblies={};parts={};sources={}
    for section in sections:
        _unreleased(section)
        if section.get('schema')!='osr-vehicle-parts-section/1' or section['parent_candidate_id']!=parent_candidate_id:
            raise ValueError('Vehicle parts have a different parent/schema')
        for collection,rows in ((materials,section['materials']),(assemblies,section['assemblies']),
                                (parts,section['parts']),(sources,section['sources'])):
            for row in rows:
                if not isinstance(row.get('id'),str) or not row['id'] or row['id'] in collection:
                    raise ValueError('Unique nonempty section-qualified definitions required')
                collection[row['id']]=row
    for material in materials.values():
        if not material.get('specification') or not material.get('form') or not material.get('basis'):
            raise ValueError('Proposed material specification, form and basis required')
        if material['density_kg_m3'] is not None:number(material['density_kg_m3'],positive=True)
        if not material.get('qualification_required'):raise ValueError('Material qualification dependencies required')
    for source in sources.values():
        if not source.get('url') or not source.get('title') or not source.get('supports') or not source.get('limits'):
            raise ValueError('Scoped technical provenance required')
    roles={}
    for assembly in assemblies.values():
        if type(assembly['quantity_per_train']) is not int or assembly['quantity_per_train']<1:
            raise ValueError('Explicit expanded train assembly count required')
        if not assembly.get('function') or not assembly.get('interfaces') or not assembly.get('assembly_steps'):
            raise ValueError('Assembly function, interfaces and practical routing required')
        role=assembly.get('role')
        if role:roles[role]=roles.get(role,0)+assembly['quantity_per_train']
        if [s['sequence'] for s in assembly['assembly_steps']]!=list(range(1,len(assembly['assembly_steps'])+1)):
            raise ValueError('Contiguous assembly operation order required')
        owned={p['id'] for p in parts.values() if p['assembly_id']==assembly['id']}
        used=set()
        for step in assembly['assembly_steps']:
            if not step['operation'] or not step['tools'] or not step['inspection'] or not step['part_ids']:
                raise ValueError('Assembly operations need parts, tools and inspection')
            used.update(step['part_ids'])
            if any(p not in parts or parts[p]['assembly_id']!=assembly['id'] for p in step['part_ids']):
                raise ValueError('Assembly operation names a different/unowned part')
        if used!=owned:raise ValueError('Assembly route omits a counted leaf')
    if any(roles.get(k)!=v for k,v in COUNTS.items()):raise ValueError('Required six-car subsystem coverage/counts differ: '+str({k:(roles.get(k),v) for k,v in COUNTS.items() if roles.get(k)!=v}))
    for part in parts.values():
        if any(k not in part for k in REQUIRED_PART):raise ValueError('Incomplete part definition: '+part['id'])
        if part['assembly_id'] not in assemblies or part['material_id'] not in materials:raise ValueError('Unbound part assembly/material')
        if type(part['quantity_per_assembly']) is not int or part['quantity_per_assembly']<1 or part['unit']!='each':
            raise ValueError('Positive integral counted leaf pieces required')
        if part['make_buy'] not in ('local-fabricate','buy-standard','buy-qualified'):raise ValueError('Explicit manufacture/purchase responsibility required')
        for key in ('name','joining','finish','tolerance_and_fits','mounting','maintenance_removal','cost_basis'):
            if not isinstance(part[key],str) or not part[key].strip():raise ValueError('Explicit part '+key+' required')
        if not part['manufacturing'] or not part['inspection'] or not isinstance(part['open_tasks'],list):
            raise ValueError('Manufacturing and inspection route required')
        if any(s not in sources for s in part['source_ids']) or not part['source_ids']:raise ValueError('Part technical evidence is unbound')
        known=interval(part['mass_each_kg'],part['id']+' mass');interval(part['direct_cost_each_usd'],part['id']+' cost')
        volume=stock_volume(part['stock']);rho=materials[part['material_id']]['density_kg_m3']
        kind=part['mass_basis'].get('kind')
        if kind not in ('calculated-stock','engineering-allowance','unknown') or not part['mass_basis'].get('description'):
            raise ValueError('Explicit stock/allowance/unknown mass basis required')
        if kind=='calculated-stock':
            if not known or volume is None or rho is None or any(not isclose(v,volume*rho,rel_tol=1e-10,abs_tol=1e-8) for v in part['mass_each_kg'].values()):
                raise ValueError('Calculated stock mass does not reproduce from dimensions/density')
        if kind=='unknown' and known:raise ValueError('Unknown mass cannot become a numerical allowance')
        if not known and kind!='unknown':raise ValueError('Missing mass must remain explicitly unknown')
    if any(not any(p['assembly_id']==a for p in parts.values()) for a in assemblies):raise ValueError('Empty assembly is not a completed breakdown')
    return materials,assemblies,parts,sources,roles


def component_projection(part,material):
    keys=('id','assembly_id','quantity_per_assembly','unit','material_id','stock','joining','finish','tolerance_and_fits','mounting')
    return {**{k:part[k] for k in keys},'nominal_electrical_W':part.get('proposed_electrical_W_each'),
        'electrical_rating':part.get('electrical_rating'),
        'material_specification':{k:material[k] for k in ('id','specification','form')}}


def physical_projection(sections,parent_id,reference,policy):
    materials=[{k:m[k] for k in ('id','specification','form')} for s in sections for m in s['materials']]
    assemblies=[]
    for section in sections:
        for a in section['assemblies']:
            # A new check outcome is evaluation evidence, not new hardware.
            interfaces=[{k:v for k,v in i.items() if k not in ('verification','evidence','source_ids')} for i in a['interfaces']]
            assemblies.append(dict(id=a['id'],quantity_per_train=a['quantity_per_train'],role=a.get('role'),interfaces=sorted(interfaces,key=lambda i:i['id'])))
    material_map={m['id']:m for s in sections for m in s['materials']}
    parts=[component_projection(p,material_map[p['material_id']]) for s in sections for p in s['parts']]
    electrical=next(s for s in sections if s['section_id']=='services')['electrical_assumptions']
    battery={k:electrical['battery'][k] for k in ('modules_per_car','series_modules','parallel_strings','nominal_module_V','module_Ah')}
    formation={k:policy['formation'][k] for k in ('cars','body_length_m','proposed_intercar_gap_m','terminal_coupler_projection_m')}
    return dict(schema='osr-vehicle-manufacturing-physical/1',parent_candidate_id=parent_id,
        reference_interfaces=reference,proposed_formation=formation,service_battery_topology=battery,
        electrical_contract=policy['physical_electrical_contract'],
        integration_interfaces=[{k:i[k] for k in ('id','owners','physical_contract')} for i in policy['integration_interfaces']],
        coolant_topology={k:v for k,v in policy['coolant_topology'].items() if k!='hydraulic_design_verified'},
        materials=sorted(materials,key=lambda m:m['id']),assemblies=sorted(assemblies,key=lambda a:a['id']),parts=sorted(parts,key=lambda p:p['id']))


def electrical_checks(sections,parts,policy):
    data=next(s for s in sections if s['section_id']=='services')['electrical_assumptions']
    light=data['lighting'];battery=data['battery'];wanted=policy['physical_electrical_contract']
    def count(key):return parts['services/'+key]['quantity_per_assembly']
    pairs=(('led-board','normal_LED_boards_per_car','cabin_boards_per_car'),
           ('vestibule-led','vestibule_lamps_per_car','vestibule_lamps_per_car'),
           ('emergency-led','emergency_lamps_per_car','emergency_lamps_per_car'))
    for pid,pkey,lkey in pairs:
        if count(pid)!=wanted[pkey] or light[lkey]!=wanted[pkey]:raise ValueError('Lighting physical count differs')
    for pid,lkey in (('led-board','board_W'),('vestibule-led','vestibule_W'),('emergency-led','emergency_W')):
        if parts['services/'+pid]['proposed_electrical_W_each']!=light[lkey]:raise ValueError('LED module rating differs')
    if (count('battery-module')!=battery['modules_per_car'] or battery['modules_per_car']!=battery['series_modules']*battery['parallel_strings']
            or battery['modules_per_car']!=wanted['service_battery_modules_per_car']
            or battery['series_modules']!=wanted['service_battery_series_modules'] or battery['parallel_strings']!=wanted['service_battery_parallel_strings']
            or battery['nominal_module_V']!=wanted['nominal_module_voltage_V'] or battery['module_Ah']!=wanted['nominal_module_capacity_Ah']):
        raise ValueError('Service battery topology/count differs')
    energy=battery['modules_per_car']*battery['nominal_module_V']*battery['module_Ah']/1000
    if not isclose(energy,wanted['gross_service_energy_kWh_per_car'],rel_tol=1e-12):raise ValueError('Service energy rating differs')
    if count('battery-busbar')!=battery['parallel_strings']*(battery['series_modules']-1) or count('battery-string-lug')!=2*battery['parallel_strings']:
        raise ValueError('Battery series links/end terminals are not disaggregated consistently')
    if count('battery-terminal-screw')!=2*battery['modules_per_car']:raise ValueError('Module terminal fixing count differs')
    cold=policy['coolant_topology']
    required={'battery-cold-plate':'cold_plates_per_car','battery-cooling-manifold':'supply_and_return_headers',
        'battery-plate-hose':'short_hose_cuts','battery-plate-hose-end':'short_hose_end_fittings',
        'battery-plate-port':'plate_port_adaptors','battery-manifold-port':'header_port_adaptors','battery-cooling-hose':'trunk_hose_cuts'}
    if any(count(k)!=cold[v] for k,v in required.items()):raise ValueError('Cooling leaf count differs from connection topology')
    if cold['parallel_plate_branches']*cold['series_plates_per_branch']!=cold['cold_plates_per_car'] or cold['cold_plates_per_car']*cold['modules_per_cold_plate']!=battery['modules_per_car']:
        raise ValueError('Cold plate/module branch topology differs')
    if parts['services/gangway-led']['proposed_electrical_W_each']!=wanted['gangway_lamp_W']:raise ValueError('Gangway lamp rating differs')
    if parts['services/led-driver']['electrical_rating']['output_capacity_W']!=light['driver_output_W']:raise ValueError('Lighting feeder capacity differs')
    if count('gangway-led')!=wanted['gangway_lamps_per_connection']:raise ValueError('Gangway lighting count differs')
    for key in ('low_voltage_V','driver_efficiency_hypothesis','driver_output_W','half_route_m','conductor_area_mm2'):
        number(light[key],positive=True)
    if not 0<light['driver_efficiency_hypothesis']<=1:raise ValueError('Driver efficiency must be positive and <=1')
    output=light['cabin_boards_per_car']*light['board_W']+light['vestibule_lamps_per_car']*light['vestibule_W']
    emergency=light['emergency_lamps_per_car']*light['emergency_W']
    if count('led-driver')!=light['normal_drivers_per_car'] or count('led-half-loom')!=light['protected_half_circuits_per_car']:
        raise ValueError('Protected lighting branch count differs')
    capacity=light['normal_drivers_per_car']*light['driver_output_W'];current=output/light['protected_half_circuits_per_car']/light['low_voltage_V']
    resistance=2*light['half_route_m']*light['copper_resistivity_ohm_mm2_m_at20C']/light['conductor_area_mm2']*(1+light['resistance_coefficient_per_K']*(light['copper_temperature_C']-20))
    if output>capacity:raise ValueError('Declared LED loads exceed proposed driver output ratings')
    gangway=5*count('gangway-led')*wanted['gangway_lamp_W']
    return dict(normal_light_output_W_per_car=output,normal_light_input_W_per_car_hypothesis=output/light['driver_efficiency_hypothesis'],
        emergency_light_output_W_per_car=emergency,normal_driver_capacity_W_per_car=capacity,
        half_branch_current_A=current,worst_declared_loop_resistance_ohm=resistance,
        half_branch_voltage_drop_V=current*resistance,half_branch_voltage_drop_fraction=current*resistance/light['low_voltage_V'],
        gangway_lighting_output_W_per_train=gangway,total_lighting_input_W_per_train_hypothesis=(6*(output+emergency)+gangway)/light['driver_efficiency_hypothesis'],
        emergency_lighting_energy_Wh_per_train_hypothesis=(6*emergency+gangway)/light['driver_efficiency_hypothesis']*light['emergency_endurance_s']/3600,
        gross_service_energy_kWh_per_car=energy,nominal_service_bus_V=battery['series_modules']*battery['nominal_module_V'],
        capacity_or_hotel_target_changed=False,scope='Necessary declared load/copper/nominal-energy arithmetic; no photometric, protection, hot-derating, charge or actual endurance acceptance')


def _sum(rows,field):
    missing=[r['id'] for r in rows if r[field]['base'] is None]
    return dict(known_leaf_subtotal={k:fsum(r[field][k]*r['quantity_per_train'] for r in rows if r[field][k] is not None) for k in CASES},
        unknown_leaf_ids=missing,all_catalogued_leaves_bounded=not missing,
        complete_installed_quantity=None)


def validate_formation(formation,vehicle):
    if formation['cars']!=vehicle['cars'] or formation['body_length_m']!=vehicle['body_length_m']:
        raise ValueError('Parts formation differs from six-car parent/counts')
    number(formation['proposed_intercar_gap_m'],positive=True)
    expected=formation['cars']*formation['body_length_m']+(formation['cars']-1)*formation['proposed_intercar_gap_m']
    if expected!=formation['body_and_intercar_gap_length_m']:raise ValueError('Proposed body/gap train length differs')
    if formation['complete_overall_train_length_m'] is not None or formation['minimum_usable_platform_length_m'] is not None:
        raise ValueError('End projection and stopping/access margins remain unresolved in this recipe')
    return expected


def build(root=ROOT,*,sections=None):
    root=Path(root);baseline=selection.load(root);parent=baseline['vehicle'];pid=parent['candidate_id']
    sections=load_sections(root) if sections is None else deepcopy(sections)
    section_ids={s['section_id']:identity(s) for s in sections}
    materials,assemblies,parts,sources,roles=validate_sections(sections,pid)
    policy=json.loads((root/'engineering/vehicle_parts/policy.json').read_bytes());_unreleased(policy)
    if policy['parent_candidate_id']!=pid:raise ValueError('Manufacturing policy has a different parent')
    formation=policy['formation']
    expected_length=validate_formation(formation,parent['physical_definition']['vehicle'])
    electrical=electrical_checks(sections,parts,policy)
    v=parent['physical_definition']['vehicle'];support=parent['physical_definition']['support']
    reference=dict(cars=v['cars'],body_length_m=v['body_length_m'],body_width_m=v['body_width_m'],
        fixed_seats_per_car=v['fixed_seats_per_car'],wheelchair_places_per_car=v['wheelchair_places_per_car'],
        passenger_door_openings_per_car=v['passenger_doors_per_car'],passenger_door_sides=v['passenger_door_sides'],
        floor_top_above_rail_m=v['floor_top_above_rail_m'],gauge_m=support['track_gauge_m'],
        bogie_centres_x_m=support['bogie_centres_x_m'],bogie_wheelbase_m=support['bogie_wheelbase_m'],
        wheel_new_diameter_m=support['wheel_new_diameter_m'],onboard_traction=False)
    physical=physical_projection(sections,pid,reference,policy);candidate_id=identity(physical)
    rows=[]
    for p in parts.values():
        row=deepcopy(p);a=assemblies[p['assembly_id']]
        row['quantity_per_train']=p['quantity_per_assembly']*a['quantity_per_train']
        row['component_definition_id']=identity(component_projection(p,materials[p['material_id']]))
        row['candidate_id']=candidate_id;rows.append(row)
    local_sources=(SOURCE,'engineering/vehicle_parts/__init__.py','engineering/vehicle_parts/policy.json',*[f'engineering/vehicle_parts/data/{n}.json' for n in SECTIONS])
    source_sha256={**baseline['source_sha256'],**{n:digest(root/n) for n in local_sources}}
    # Pin any locally present retained geometry payload as an explicit input.
    from engineering.station_rail import vehicle
    for name in (vehicle.PARENT,vehicle.PARENT_MANIFEST):
        if (root/name).is_file():source_sha256[name]=digest(root/name)
    mass=_sum(rows,'mass_each_kg');cost=_sum(rows,'direct_cost_each_usd')
    groups=[]
    for aid,a in assemblies.items():
        owned=[r for r in rows if r['assembly_id']==aid]
        groups.append(dict(id=aid,name=a['name'],role=a.get('role'),quantity_per_train=a['quantity_per_train'],
            unique_leaf_types=len(owned),counted_leaf_pieces=sum(r['quantity_per_train'] for r in owned),
            nominal_mass_kg=_sum(owned,'mass_each_kg'),direct_parts_process_usd=_sum(owned,'direct_cost_each_usd')))
    value=dict(schema='osr-vehicle-manufacturing-bundle/1',candidate_id=candidate_id,parent_candidate_id=pid,
        parent_selection_id=baseline['selection_id'],parent_evaluation_id=parent['evaluation_id'],
        physical_definition=physical,input_section_ids=section_ids,input_scope='Canonical source recipe' if sections==load_sections(root) else 'Explicit in-memory proposal payload; section identities retained separately from source-file context',parts=rows,materials=list(materials.values()),assemblies=list(assemblies.values()),
        technical_sources=list(sources.values()),sections=deepcopy(sections),source_sha256=source_sha256,
        integration_policy=policy,electrical_checks=electrical,
        counted=dict(assembly_types=len(assemblies),unique_leaf_types=len(rows),leaf_pieces_per_train=sum(r['quantity_per_train'] for r in rows),roles=roles),
        assembly_summaries=groups,nominal_mass_kg=mass,direct_parts_process_usd=cost,
        parent_account_comparison=dict(reference_accounted_tare_kg_per_train=parent['mass']['accounted_tare_kg_six_cars'],
            reference_unlocated_or_accounted_kg_per_car=parent['mass']['unlocated_or_reference_account_kg'],
            added_to_new_leaf_sum=False,replaced_in_selected_reference=False,
            scope='Different physical definitions and maturity; numerical difference is not a demonstrated weight or cost saving'),
        design_stage=dict(part_breakdown='outline-complete',assembly_methods='proposed',detailed_drawings='pending',
            installed_locations='partial/proposed',prototype='not-validated',manufacturing_release='not-approved'),
        installed_mass_kg=None,installed_CG_m=None,installed_inertia_kg_m2=None,complete_vehicle_factory_cost_usd=None,
        costing_policy=dict(currency='USD',class_='engineering part/process allowances',supplier_quotes=False,
            automatic_bulk_discount=False,parent_accounts_added=False,assembly_parent_costs_added=False,
            exclusions=['Final vehicle assembly labour and commissioning unless explicitly in a leaf scope',
                'Shared tooling/plant capital, taxes/duties, final delivery/installation, warranty and qualification',
                'Complete whole-life cost and unlisted redesign after interface/analysis review']),
        downstream=dict(CAD=dict(candidate_id=candidate_id,stock_definition_available=True,complete_assembly_transforms=None,installed_interference_checked=False),
            BIM=dict(candidate_id=candidate_id,component_definition_ids=[r['component_definition_id'] for r in rows],IFC_generated=False),
            procurement=dict(candidate_id=candidate_id,leaf_make_buy_count=len(rows),supplier_quotes_approved=False,transactions_performed=False),
            installation=dict(candidate_id=candidate_id,proposed_assembly_routes=list(assemblies),released_work_instructions=False),
            controls=dict(candidate_id=candidate_id,door_openings=12,closed_leaf_channels=24,locked_leaf_channels=24,WSP_axle_encoders=24,axlebox_temperature_probes=48,movement_authority=False,independent_interlock_validation='pending'),
            operations=dict(candidate_id=candidate_id,normal_places=276,fixed_seats=264,wheelchair_places=12,body_and_gap_length_m=expected_length,headway_s=None,route_fleet_and_platform_results_inherited=False),
            geometry=dict(candidate_id=candidate_id,body_and_gap_length_m=expected_length,complete_overall_length_m=None,minimum_usable_platform_length_m=None,state='stock dimensions; no complete installed CAD interference check'),
            inventory=dict(candidate_id=candidate_id,nominal_mass_kg=mass,installed_CG_m=None),
            interfaces=dict(candidate_id=candidate_id,state='proposed mating interfaces; load transfer and movement verification pending'),
            propulsion=dict(candidate_id=candidate_id,available_force_map=None,journey_accepted=False),
            braking=dict(candidate_id=candidate_id,certified_degraded_stopping_curve=None,stopping_accepted=False),
            civil=dict(candidate_id=candidate_id,normal_passenger_payload_kg=6*46*75,crowd_control_payload_kg=6*160*75,
                design_axle_loads_N=None,reason='Requires actual per-car locations, inertia, dynamic loads and interfaces'),
            manufacturing=dict(candidate_id=candidate_id,routes_proposed=True,release=False),
            economics=dict(candidate_id=candidate_id,direct_parts_process_usd=cost,installed_and_lifecycle_cost=None)),
        integrated_selection_id=None,**FLAGS)
    value['evaluation_id']=identity(value);value['bundle_id']=identity(dict(candidate_id=candidate_id,evaluation_id=value['evaluation_id']))
    return value


def verify(value,root=ROOT):
    _unreleased(value)
    if value!=build(root):raise ValueError('Vehicle manufacturing catalogue differs from canonical sources or identities')
    return dict(verified=True,candidate_id=value['candidate_id'],evaluation_id=value['evaluation_id'],bundle_id=value['bundle_id'],**FLAGS)
