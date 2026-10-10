"""Compile a complete reference family into consistent parts, CAD and physics.

Existing catalogue IDs remain the allocation authorities. Expanded kit pieces
are reference features of those allocations, not newly released supplier parts.
Residual masses stay explicit and every unresolved catalogue slot is reported.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import math
from pathlib import Path
from osr_mech.automated_geometry import aggregate, primitive_volume, source
from osr_mech.common import ConsistFamily
from osr_mech.engineering_definition import (ROOT, fingerprint, load_definition, number,
    validate, model_mass_properties, catalogue_template, verification_register)
from osr_mech.buildable_trainset import buildable_trainset_design
from osr_mech.joint_design import definitions
from .automated_battery import box, compile_pack, duty_cycle, operating_budget
from .shared_demo import demonstration, transform
from .spatial_demo import configuration
from .spatial_vehicle import SpatialVehicle

BASIS_PATH=ROOT/'engineering/reference-parts/industry-basis.json'
CHOICES_PATH=ROOT/'engineering/reference-parts/default-variant.json'


def _properties(values, basis):
    return dict(**values,uncertainty_kg=values['mass_kg']*.05,position_uncertainty_m=.01,
        inertia_uncertainty_kg_m2=max(values['inertia_tensor_kg_m2'][i][i] for i in range(3))*.05,
        basis=basis,evidence=None)


def _set_geometry(row,spec):
    row['geometry'].update(kind='osr-parametric-reference',source=[source(spec)],
        process='OSR parametric study; supplier/material/process release open')


def validate_interfaces(register,model):
    """Check endpoint identity, declared quantities and paired port compatibility."""
    if register.get('schema')!='osr-typed-interface-register/1' or register.get('configuration_sha256')!=fingerprint(model):
        raise ValueError('interface register targets another configuration')
    instances={r['id']:r for r in model['instances']};joints={j['id']:j for j in model['joints']};seen=set()
    expected={'mechanical':{'force':'N','moment':'N m','translation':'m','rotation':'rad'},
              'electrical':{'voltage':'V','current':'A','power':'W'},
              'thermal-fluid':{'temperature':'degC','heat_flow':'W','mass_flow':'kg/s','pressure_loss':'Pa'},
              'control':{'timestamp':'s','latency':'s'}}
    for row in register['interfaces']:
        if set(row)!={'id','type','endpoints','joint','units','sign_convention','limits','evidence','model_limits'}:
            raise ValueError('interface fields missing or unknown')
        if row['id'] in seen or row['type'] not in expected:raise ValueError('duplicate/unsupported typed interface')
        seen.add(row['id'])
        if row['units']!=expected[row['type']] or not row['sign_convention'] or not row['model_limits']:
            raise ValueError('interface units, signs and limitations required')
        if len(row['endpoints'])!=2 or row['endpoints'][0]['instance']==row['endpoints'][1]['instance']:
            raise ValueError('two different interface endpoints required')
        for endpoint in row['endpoints']:
            if set(endpoint)!={'instance','datum','port','role'} or endpoint['instance'] not in instances or endpoint['datum'] not in instances[endpoint['instance']]['datums']:
                raise ValueError('interface endpoint datum is unknown')
            if not endpoint['port'] or not endpoint['role']:raise ValueError('interface endpoint responsibility required')
        if row['type']=='mechanical':
            joint=joints.get(row['joint'])
            if joint is None or [{k:e[k] for k in ('instance','datum')} for e in row['endpoints']]!=joint['endpoints']:
                raise ValueError('mechanical interface must reconcile its physical joint endpoints')
        elif row['joint'] is not None:raise ValueError('nonmechanical interface cannot masquerade as a CAD joint')
        for key,bounds in row['limits'].items():
            if bounds is None:continue
            if not isinstance(bounds,list) or len(bounds)!=2:raise ValueError('ordered interface limit pair required')
            for v in bounds:number(v,'interface '+key)
            if bounds[0]>bounds[1]:raise ValueError('incompatible interface limits')
        # Voltage and current capabilities are declared in the same register,
        # so no implicit pairing of an unknown connector or incompatible bus.
        if row['type']=='electrical' and (row['limits'].get('voltage_v') is None or row['limits'].get('current_a') is None):
            raise ValueError('reference electrical bus needs explicit operating limits')
    if {r['joint'] for r in register['interfaces'] if r['type']=='mechanical'}!=set(joints):
        raise ValueError('every physical joint needs a typed interface')
    return register


def _interfaces(model,pack):
    rows=[]
    def add(identifier,kind,endpoints,joint,units,sign,limits,limitations,evidence):
        rows.append(dict(id=identifier,type=kind,endpoints=endpoints,joint=joint,units=units,
            sign_convention=sign,limits=limits,evidence=evidence,model_limits=limitations))
    for j in model['joints']:
        endpoints=[dict(**e,port=j['id'],role='attachment owner' if i==0 else 'installed component owner') for i,e in enumerate(j['endpoints'])]
        add(j['id']+'/mechanical','mechanical',endpoints,j['id'],
            dict(force='N',moment='N m',translation='m',rotation='rad'),
            'right-handed instance datum axes; positive resultant acts on endpoint 2, equal opposite on endpoint 1',
            dict(force_n=None,moment_nm=None),
            ['CAD constraints set placement; capacity, fits, preload and fatigue remain open',
             'springs share reduced six-DOF joint laws; geometry is not a supplier force curve'],
            'OSR synthetic mechanical model')
    for car in model['family_definition']['cars']:
        battery=car['id']+'/battery';body=car['id']+'/body'
        endpoints=[dict(instance=battery,datum='origin',port='pack-port',role='battery installation'),
                   dict(instance=body,datum='battery',port='residual-auxiliary-port',role='unresolved controller/cooling/control allocation')]
        prefix=car['id']+'/battery'
        add(prefix+'/dc','electrical',endpoints,None,dict(voltage='V',current='A',power='W'),
            'positive current/power leaves pack into the per-car DC bus',
            dict(voltage_v=[pack['nominal_voltage_v']-pack['discharge_current_limit_a']*pack['resistance_ohm'],
                pack['nominal_voltage_v']+pack['charge_current_limit_a']*pack['resistance_ohm']],
                current_a=[-pack['charge_current_limit_a'],pack['discharge_current_limit_a']]),
            ['constant nominal OCV minus I R; connector/fuse/contactor and inverter voltage compatibility unresolved'],
            'Toshiba nominal module voltage; OSR assumed resistance/current limits')
        add(prefix+'/cooling','thermal-fluid',endpoints,None,
            dict(temperature='degC',heat_flow='W',mass_flow='kg/s',pressure_loss='Pa'),
            'positive heat/flow exits pack; inlet/outlet hardware and hydraulic resistance unresolved',
            dict(temperature_c=None,mass_flow_kg_s=None,pressure_loss_pa=None),
            ['lumped Newton cooling to ambient; no solved coolant circuit; cold-temperature behavior unqualified'],
            'OSR research cooling assumption')
        add(prefix+'/bms','control',endpoints,None,dict(timestamp='s',latency='s'),
            'monotonic simulation seconds; commands to pack, SOC/temperature observations from pack',
            dict(latency_s=None),['BMS/CAN latency, protection thresholds and safe failure states require supplier definition'],
            'interface contract only; no executed BMS controller')
    return validate_interfaces(dict(schema='osr-typed-interface-register/1',configuration_sha256=fingerprint(model),
        interfaces=rows,production_released=False,physical_validation=False),model)


def _coverage(model,allocations,interfaces):
    design=buildable_trainset_design(ConsistFamily(model['family']));template=catalogue_template(design)
    products={p.id:p for p in design.product_items};instances={r['id']:r for r in model['instances']}
    by_product={}
    for row in model['instances']:by_product.setdefault(row['part_id'],[]).append(row['id'])
    rows=[];group_slots={}
    for row in template['instances']:group_slots.setdefault(row['part_id'],[]).append(row)
    for product,slots in group_slots.items():
        groups=allocations.get(product,[])
        if groups and len(groups)!=len(slots):raise ValueError('expanded allocation groups do not reconcile catalogue quantities: '+product)
        for index,slot in enumerate(slots):
            mapped=groups[index] if groups else []
            joint_ids=[j['id'] for j in model['joints'] if any(e['instance'] in mapped for e in j['endpoints'])]
            typed=[i['id'] for i in interfaces['interfaces'] if any(e['instance'] in mapped for e in i['endpoints'])]
            rows.append(dict(allocation_id=slot['id'],part_id=product,title=products[product].title,
                required_quantity=slot['quantity'],unit=slot['unit'],instances=mapped,
                representation='expanded-reference-parts' if mapped else 'unresolved-residual-allocation',
                mass_basis='explicit nonoverlapping component mass' if mapped else 'included only in planning residuals; physical mass/placement attribution open',
                evidence_status='public-reference-and/or-synthetic-design' if mapped else 'missing-part-properties',
                joints=joint_ids,interfaces=typed,requirements=slot['requirements'],
                limits=['no supplier release or physical validation'] if mapped else ['production decomposition, geometry, properties, interfaces and QA limits open'],
                engineering_released=False))
    explicit={r['allocation_id'] for r in rows if r['instances']}
    return dict(schema='osr-component-coverage/1',configuration_sha256=fingerprint(model),
        required_allocation_count=len(rows),explicit_reference_allocation_count=len(explicit),
        unresolved_allocation_count=len(rows)-len(explicit),physical_instance_count=len(instances),rows=rows,
        track_and_infrastructure=dict(basis='pandrol-fastening',representation='existing equivalent rail/pad/beam/support model',
            open_parts=['rail clips/shoulders/insulators','rail pad material and curves','diaphragms/reinforcement/tendons',
                        'bearing internals','pier/cap/foundation connection geometry','soil and erection-specific details']),
        full_production_component_coverage=False,physical_validation=False)


def compile_variant(choices=None, *, basis=None):
    choices=deepcopy(choices if choices is not None else load_definition(CHOICES_PATH))
    basis=deepcopy(basis if basis is not None else load_definition(BASIS_PATH))
    if set(choices)!={'schema','family','battery'} or choices['schema']!='osr-part-variant-choices/1':
        raise ValueError('variant choices missing or unknown')
    pack=compile_pack(choices['battery'],basis)
    model=demonstration(choices['family'],full_train=True);family=model['family_definition']
    L,W,H=pack['dimensions_m'];car_length=family['car_length_m']
    # Battery bay lies between the inner wheel envelopes, with 100 mm clearance.
    bay_length=car_length-2*(2.1+1.05+.38+.1)
    if L>bay_length or W>2.4 or H>.35:raise ValueError('battery overlaps reference bogie/wheel envelope or exceeds its installation bay')
    model['revision']='OSR-REFERENCE-'+fingerprint(dict(choices=choices,basis=basis))[:12]
    model['inspections']=[];allocations={};cutlist=[];qa=[]
    by_id={r['id']:r for r in model['instances']}
    def allocation(part,ids):allocations.setdefault(part,[]).append(ids)
    def inspection(identifier,instance,characteristic,unit,nominal,method,standard):
        model['inspections'].append(dict(id=identifier,instance=instance,characteristic=characteristic,unit=unit,
            minimum=None,maximum=None,dependencies=['mass-properties','vehicle-model']))
        qa.append(dict(id=identifier,instance=instance,characteristic=characteristic,unit=unit,nominal=nominal,
            acceptance_limits=None,method=method,standard_method_reference=standard,status='unexecuted; acceptance limits open'))
    def add_part(identifier,part,parent,mass,spec,position,*,body=None,bogie=None,axle=None):
        row=dict(id=identifier,part_id=part,revision=model['revision'],serial=None,batch=None,parent=parent,
            quantity=1,unit='ea',geometry=dict(kind='osr-parametric-reference',source=[source(spec)],material_regions=[],thickness_m=None,
                process='reference envelope; supplier/material release open'),transform=transform(*position),datums={'origin':transform()},
            body=body,bogie=bogie,axle=axle,scope=[identifier],property_source='design',
            properties=dict(design=_properties(aggregate(spec['primitives'],[mass/len(spec['primitives'])]*len(spec['primitives'])),
                'OSR assumed component mass and uniform reference geometry; no supplier mass/inertia'),supplier=None,measured=None),requirements=[],inspections=[])
        model['instances'].append(row);by_id[identifier]=row
        # Detached installed datum gives a real fixed placement constraint.
        host=by_id[parent];datum=identifier.rsplit('/',1)[-1]
        host['datums'][datum]=transform(*(position[i]-host['transform']['translation_m'][i] for i in range(3)))
        model['joints'].append(dict(id=identifier+'/mount',revision=model['revision'],connection='fixed',type='bolted',
            endpoints=[dict(instance=parent,datum=datum),dict(instance=identifier,datum='origin')],permitted_motion=[],
            property_source='design',properties=dict(design=None,supplier=None,measured=None),definition={'physical_definition_status':'reference attachment; supplier mounting open'},
            requirements=[],inspections=[]))
        inspection(identifier+'/installation',identifier,'installed datum position','m',position,'dimensional survey','ISO 1101:2017; OSR-ENG-001')
        return identifier
    for car in family['cars']:
        cid=car['id'];body=by_id[cid+'/body'];battery=by_id[cid+'/battery'];x=car['centre_x_m']
        body['datums']['battery']=transform(0.,0.,-.95)
        battery['transform']=transform(x,0.,.55);battery['revision']=model['revision']
        battery['properties']['design']=_properties(pack['properties'],
            'Toshiba Type3-23 public approximate module mass; OSR enclosure/hardware design densities; uniform primitive inertia; LTO research alternative to LFP EBOM')
        _set_geometry(battery,pack['geometry']);allocation(battery['part_id'],[battery['id']])
        joint=next(j for j in model['joints'] if j['id']==cid+'/battery-retention')
        joint['definition']['physical']=dict(hole_pattern_m=pack['hole_pattern_m'],grip_stack_m=[choices['battery']['enclosure_thickness_m'],.008,.003,.003],
            fastener_specification='8 reference M12 clearance/shank stacks; ISO 898-1 certificate/thread/locking selection open',
            clearance_m=.0005,preload_range_n=None,locking=None,contact_surfaces='perforated tray base / unresolved underframe mount plate',material_evidence=None)
        for piece in pack['cutlist']:cutlist.append(dict(instance=battery['id'],**piece))
        inspection(battery['id']+'/mass',battery['id'],'installed pack mass','kg',pack['properties']['mass_kg'],'weigh calibrated installation','OSR-ENG-001 / ISO 17025:2017')
        inspection(battery['id']+'/energy',battery['id'],'usable energy','kWh',pack['usable_energy_kwh'],'duty-cycle performance test; railway applicability review open','ISO 12405-4:2018 method reference; road-vehicle scope')
        inspection(battery['id']+'/retention',battery['id'],'combined retention load capacity','N',None,'assembly-specific six-resultant proof/fatigue test','OSR-ENG-001 / ISO 16047:2005 method reference')
        for bogie in (b for b in family['bogies'] if b['parent']==cid):
            bid=bogie['id'];frame=by_id[bid+'/frame'];powered=bogie['kind']=='powered';bx=bogie['pivot_x_m'];deduct_frame=0.
            allocation(frame['part_id'],[frame['id']])
            secondary=[];primary=[]
            for side in (-1,1):
                spec=dict(role='secondary-air-and-auxiliary-spring',primitives=[
                    dict(id='air-spring-envelope',kind='cylinder',centre_m=[0,0,0],radius_m=.19,length_m=.22,axis='z'),
                    dict(id='auxiliary-spring-envelope',kind='cylinder',centre_m=[0,0,-.14],radius_m=.11,length_m=.06,axis='z')])
                secondary.append(add_part(bid+f'/secondary-{side}', 'LM3-BOG-P046' if powered else 'LM3-BOG-P047',frame['id'],45.,spec,[bx,side*.85,1.],bogie=bid))
                deduct_frame+=45.
            allocation('LM3-BOG-P046' if powered else 'LM3-BOG-P047',secondary)
            for axle,ax in enumerate(bogie['axle_x_m'],1):
                wheel=by_id[bid+f'/wheelset-{axle}'];allocation(wheel['part_id'],[wheel['id']]);boxes=[]
                # Axlebox mass is unsprung; deduct the exact same allocation from
                # the old synthetic wheelset, preventing aggregate double count.
                old=wheel['properties']['design'];old['mass_kg']-=50.
                old['inertia_tensor_kg_m2']=[[v*.9 for v in row] for row in old['inertia_tensor_kg_m2']]
                old['basis']+='; axleboxes excluded and instantiated separately'
                for side in (-1,1):
                    spec=dict(role='axlebox-bearing-housing',primitives=[dict(id='housing-envelope',kind='tube',centre_m=[0,0,0],
                        radius_m=.14,inner_radius_m=.075,length_m=.16,axis='y')])
                    boxes.append(add_part(bid+f'/axle-{axle}/axlebox-{side}','LM3-BOG-P042' if powered else 'LM3-BOG-P043',
                        wheel['id'],25.,spec,[ax,side*.92,.38],bogie=bid,axle=axle))
                    spec=dict(role='primary-spring-guide',primitives=[dict(id='spring-guide-envelope',kind='tube',centre_m=[0,0,0],
                        radius_m=.10,inner_radius_m=.035,length_m=.20,axis='z')])
                    primary.append(add_part(bid+f'/primary-{axle}-{side}','LM3-BOG-P044' if powered else 'LM3-BOG-P045',frame['id'],
                        10.,spec,[ax,side*.92,.65],bogie=bid));deduct_frame+=10.
                allocation('LM3-BOG-P042' if powered else 'LM3-BOG-P043',boxes)
                if powered:
                    for name,part,mass,dx,dy,dz in [('motor','LM3-TRC-P010',180.,.65,.4,.4),('gearbox','LM3-TRC-P020',100.,.35,.32,.32)]:
                        spec=dict(role=name+'-installation-envelope',primitives=[box(name,[dx,dy,dz],[0,0,0])])
                        identifier=add_part(bid+f'/{name}-{axle}',part,frame['id'],mass,spec,[ax,-.35 if name=='motor' else .25,.65],bogie=bid)
                        allocation(part,[identifier]);deduct_frame+=mass
            allocation('LM3-BOG-P044' if powered else 'LM3-BOG-P045',primary)
            p=frame['properties']['design'];original=p['mass_kg'];p['mass_kg']-=deduct_frame
            if p['mass_kg']<=0:raise ValueError('expanded bogie parts exhaust the residual frame allocation')
            p['inertia_tensor_kg_m2']=[[v*p['mass_kg']/original for v in row] for row in p['inertia_tensor_kg_m2']]
            p['basis']+='; explicit primary/secondary spring and motor/gearbox masses excluded'
    for row in model['instances']:row['revision']=model['revision']
    for joint in model['joints']:joint['revision']=model['revision']
    model['notes']='Full authoritative planning family with expanded reference running gear and parameterised LTO battery alternative. Residual carbody/frame masses and suspension laws remain synthetic; baseline LFP EBOM is not released by this study.'
    validate(model);mass=model_mass_properties(model);cfg=configuration(model);vehicle=SpatialVehicle(model,cfg['joint_laws'])
    interfaces=_interfaces(model,pack);coverage=_coverage(model,allocations,interfaces)
    expected=family['profile']['tare_mass_t']*1000+family['car_count']*(pack['properties']['mass_kg']-2500.)
    if not math.isclose(vehicle.total_mass,expected,rel_tol=1e-12):raise ValueError('expanded train mass does not reconcile its original residual allocation')
    source_paths=[BASIS_PATH,CHOICES_PATH,ROOT/'lib/templates/rolling-stock.toml',
        ROOT/'design/component-catalogue/schemas/shared-engineering-model.json',
        *sorted((ROOT/'design/component-catalogue/src/osr_mech').rglob('*.py')),
        *sorted((ROOT/'engineering/civil_exploration').glob('*.py'))]
    provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    duty=duty_cycle(pack,[dict(duration_s=60.,terminal_power_w=200000.),dict(duration_s=60.,terminal_power_w=30000.),dict(duration_s=20.,terminal_power_w=-75000.)])
    summary=dict(schema='osr-automated-parts-review/1',variant_choices_sha256=fingerprint(choices),industry_basis_sha256=fingerprint(basis),
        configuration_sha256=fingerprint(model),sources_sha256=provenance,family=model['family'],car_count=family['car_count'],
        bogie_count=len(family['bogies']),wheelset_count=len([g for g in vehicle.groups.values() if g['wheel']]),
        wheel_contact_count=len(vehicle.contacts),instance_count=len(model['instances']),joint_count=len(model['joints']),
        typed_interface_count=len(interfaces['interfaces']),total_mass_kg=vehicle.total_mass,
        mass_balance_residual_kg=vehicle.total_mass-expected,
        battery_per_car={k:pack[k] for k in ('module_count','series_modules','parallel_strings','nominal_voltage_v','capacity_ah',
            'nominal_energy_kwh','usable_energy_kwh','dimensions_m','resistance_ohm','discharge_current_limit_a','charge_current_limit_a')},
        pack_mass_kg=pack['properties']['mass_kg'],battery_duty=duty,
        conditional_operating_budget=operating_budget(pack,family['car_count'],train_energy_kwh_km=20.,
            average_pack_power_w=200000.,train_charger_power_w=600000.),
        coverage={k:v for k,v in coverage.items() if k not in ('rows','configuration_sha256','schema')},
        qa_characteristic_count=len(qa),complete_family_geometry_generated=True,numerically_completed=True,
        research_packaging_and_mass_checks_passed=True,engineering_constraints_passed=None,
        remaining_gates=['unresolved catalogue allocations and geometry-specific joint capacities',
            'full-family operating matrix and time/mesh convergence','traction/braking maps and coupled coolant/control models',
            'supplier/physical measurements and ISO/railway applicability/conformity'],
        production_released=False,physical_validation=False)
    return dict(model=model,spatial_configuration=cfg,battery=pack,interfaces=interfaces,coverage=coverage,
        manufacturing=dict(schema='osr-reference-manufacturing/1',configuration_sha256=fingerprint(model),
            battery_cutlist=cutlist,reference_component_quantities={p:len(ids) for p,ids in sorted(by_product_ids(model).items())},
            qa_requirements=qa,production_released=False),
        mass_properties=mass,joint_register=definitions(model),verification=verification_register(model,implementation_hashes=provenance),review=summary)


def by_product_ids(model):
    groups={}
    for row in model['instances']:groups.setdefault(row['part_id'],[]).append(row['id'])
    return groups
