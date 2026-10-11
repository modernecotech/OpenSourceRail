"""Extend the frozen reference variant with real OSR study geometry and ports.

Existing synthetic budgets remain explicit. New parts are extracted from those
budgets, never counted twice. Supplier and measured property slots stay empty.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import math
from pathlib import Path
import numpy as np
from osr_mech.automated_geometry import aggregate, primitive_volume, source, from_source
from osr_mech.engineering_definition import ROOT, fingerprint, load_definition, validate, model_mass_properties, verification_register
from osr_mech.joint_design import definitions
from engineering.civil_exploration.variant_compiler import compile_variant, _properties, _interfaces, _coverage, validate_interfaces
from engineering.civil_exploration.shared_demo import transform
from engineering.civil_exploration.spatial_demo import configuration
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
from .physics import precharge, closure_decision, thermal_study, rail_support
from .service_parts import install as install_service_parts

DATA=ROOT/'engineering/twin_design/data'


def validate_research_graph(graph, sources):
    """Validate reviewed traversal identity, depth and acyclic publisher links."""
    if graph.get('schema')!='osr-recursive-research-graph/1':raise ValueError('unknown research graph')
    known={s['id']:s for s in sources['sources']};nodes={n['source_id']:n for n in graph['nodes']}
    if len(nodes)!=len(graph['nodes']) or not 0 < len(nodes) <= 1000:raise ValueError('duplicate/unbounded research nodes')
    limit=graph['policy']['maximum_follow_depth']
    if type(limit) is not int or not 1 <= limit <= 4:raise ValueError('bounded research depth required')
    parents={id:[] for id in nodes};seen=set()
    for id,node in nodes.items():
        if id not in known or node['url']!=known[id]['url']:raise ValueError('research source identity differs')
        if type(node['depth']) is not int or not 0 <= node['depth'] <= limit:raise ValueError('research depth outside policy')
    for edge in graph['edges']:
        a,b=edge['parent'],edge['child']
        if a not in nodes or b not in nodes or (a,b) in seen or a==b:raise ValueError('unknown/duplicate research edge')
        seen.add((a,b));parents[b].append(a)
        if nodes[b]['depth']!=nodes[a]['depth']+1:raise ValueError('research traversal cycle or inconsistent depth')
    if any(not parents[id] and node['depth']!=0 for id,node in nodes.items()):raise ValueError('research traversal missing parent')
    return dict(reviewed_nodes=len(nodes),followed_publisher_links=len(seen),maximum_observed_depth=max(n['depth'] for n in nodes.values()))


def box(id, xyz, dimensions):
    return dict(id=id,kind='box',centre_m=list(xyz),dimensions_m=list(dimensions))


def plate(id, xyz, dimensions, holes, radius):
    return dict(id=id,kind='plate',centre_m=list(xyz),dimensions_m=list(dimensions),holes_xy_m=holes,hole_radius_m=radius)


def tube(id, xyz, r, bore, length):
    return dict(id=id,kind='tube',centre_m=list(xyz),radius_m=r,inner_radius_m=bore,length_m=length,axis='z')


def tray(id, length, width, height, thickness):
    return dict(role=id,primitives=[box('floor',[0,0,0],[length,width,thickness]),
        box('wall-left',[0,-width/2+thickness/2,(height+thickness)/2],[length,thickness,height]),
        box('wall-right',[0,width/2-thickness/2,(height+thickness)/2],[length,thickness,height])])


def cabinet(p):
    L,W,H=p['cabinet_dimensions_m'];t=p['cabinet_thickness_m']
    solids=[box('floor',[0,0,-H/2+t/2],[L,W,t]),box('removable-lid',[0,0,H/2-t/2],[L,W,t]),
        box('wall-front',[0,-W/2+t/2,0],[L,t,H-2*t]),box('wall-back',[0,W/2-t/2,0],[L,t,H-2*t]),
        box('wall-left',[-L/2+t/2,0,0],[t,W-2*t,H-2*t]),box('wall-right',[L/2-t/2,0,0],[t,W-2*t,H-2*t]),
        box('segregation-wall',[-.28,0,0],[t,W-2*t,H-2*t])]
    for i,x in enumerate((-.12,.05,.22)):
        solids.append(box('contactor-reservation-'+str(i+1),[x,0,-.02],[.10,.12,.10]))
    solids += [box('fuse-reservation',[.38,0,-.02],[.10,.08,.08]),
               box('precharge-resistor-reservation',[.10,.13,-.05],[.18,.04,.04]),
               box('LV-terminal-reservation',[-.39,0,-.02],[.12,.12,.08])]
    return dict(role='segregated-HV-service-panel',primitives=solids)


def infrastructure(p):
    items=[]
    def add(id, part, role, spec, position, densities, sources, **details):
        if isinstance(densities,(int,float)): densities=[densities]*len(spec['primitives'])
        masses=[primitive_volume(q)*rho for q,rho in zip(spec['primitives'],densities)]
        props=aggregate(spec['primitives'],masses)
        items.append(dict(id=id,part_id=part,role=role,geometry=spec,transform=transform(*position),
            properties=props,mass_basis='OSR assumed densities and original study geometry; no material certificate',
            source_ids=sources,details=details,production_released=False,physical_validation=False))
    L=p['length_m'];steel=p['steel_density_kg_m3'];rubber=p['pad_density_kg_m3']
    add('infra/slab','OSR-TYPE-D4376465ACD5','track-slab',dict(role='track-slab',primitives=[box('slab',[0,0,0],[L,2.6,.24])]),[L/2,0,-.12],2400.,['pci-tolerances'],reinforcement=None)
    add('infra/deck','OSR-TYPE-D36A7871D9B7','support-deck-envelope',dict(role='support-deck',primitives=[box('deck',[0,0,0],[L,2.6,.35])]),[L/2,0,-.415],2400.,['pci-tolerances'],structural_design=None)
    head_width=.072;rail_y=p['gauge_m']/2+head_width/2
    for side in (-1,1):
        rail=dict(role='rail-visualisation-surrogate',primitives=[box('foot',[0,0,.0085],[L,.15,.017]),
            box('web',[0,0,.077],[L,.016,.12]),box('head',[0,0,.1545],[L,head_width,.035])])
        add(f'infra/rail-{side}','OSR-TYPE-EACE63284F07','rail-surrogate',rail,[L/2,side*rail_y,.035],steel,['pandrol-baseplate-data'],contact_profile_released=False)
        for i in range(round(L/p['seat_spacing_m'])):
            x=(i+.5)*p['seat_spacing_m'];bp=p['baseplate_dimensions_m'];base=p['base_pad_thickness_m'];upper=p['rail_pad_thickness_m']
            zplate=base+bp[2]/2;zpad=base+bp[2]+upper/2;toe=base+bp[2]+upper+.017
            parts=[plate('under-pad',[0,0,base/2],[bp[0],bp[1],base],p['holes_xy_m'],p['hole_radius_m']),
                   plate('baseplate',[0,0,zplate],bp,p['holes_xy_m'],p['hole_radius_m']),
                   box('rail-pad',[0,0,zpad],[.30,.18,upper])]
            densities=[rubber,steel,rubber]
            for s in (-1,1):
                parts.append(box(f'toe-insulator-{s}',[0,s*.075,toe+.0015],[.28,.010,.003]));densities.append(1400.)
                parts.append(plate(f'toe-strap-{s}',[0,s*.14,toe+.011],[.28,.14,.016],[[-.07,0],[.07,0]],p['hole_radius_m']));densities.append(steel)
            for j,(a,b) in enumerate(p['holes_xy_m']):
                parts += [dict(id=f'anchor-{j+1}',kind='cylinder',centre_m=[a,b,.038],radius_m=.008,length_m=.066,axis='z'),
                    tube(f'isolator-{j+1}',[a,b,zplate],.0088,.00825,bp[2]),
                    tube(f'washer-{j+1}',[a,b,.0725],.018,.009,.003),
                    dict(id=f'head-{j+1}',kind='cylinder',centre_m=[a,b,.080],radius_m=.015,length_m=.012,axis='z')]
                densities += [steel,1400.,steel,steel]
            add(f'infra/seat-{side}-{i+1}','OSR-TYPE-EACE63284F07','replaceable-fastening-study',dict(role='open-bolted-rail-seat',primitives=parts),
                [x,side*rail_y,0],densities,['pandrol-baseplate-data','pandrol-vipa-data'],
                rail_restraint_qualified=False,anchor_embedment=None,pad_curves=None,
                boundary='original bolted OSR study; not a Pandrol clip copy or approved substitute')
    for end,x in enumerate((.6,L-.6),1):
        add(f'infra/cap-{end}','OSR-TYPE-3FD9673EF391','bearing-seat-cap-envelope',dict(role='pier-cap',primitives=[box('cap',[0,0,0],[.9,2.8,.40])]),[x,0,-.87],2400.,['freyssinet-bearings'],reinforcement=None)
        for side in (-1,1):
            mode='fixed' if end==1 and side==-1 else 'guided-y' if end==1 else 'guided-x' if side==-1 else 'free'
            add(f'infra/bearing-{end}-{side}','OSR-TYPE-C966BC7372EC','replaceable-bearing-interface',
                dict(role='bearing-interface-envelope',primitives=[box('base-plate',[0,0,-.03],[.4,.35,.02]),
                    box('bearing-reservation',[0,0,0],[.30,.25,.04]),box('top-plate',[0,0,.03],[.4,.35,.02])]),
                [x,side*.7,-.63],steel,['freyssinet-bearings','freyssinet-replacement'],mode=mode,
                rated_load_n=None,movement_capacity_m=None,interface_only=True)
            for offset in (-.30,.30):
                add(f'infra/jack-{end}-{side}-{offset}','OSR-TYPE-C966BC7372EC','jacking-pad-reservation',
                    dict(role='jacking-pad',primitives=[box('pad',[0,0,0],[.18,.20,.025])]),
                    [x+offset,side*.7,-.6575],steel,['freyssinet-replacement'],
                    rated_load_n=None,synchronized_jacking_procedure=None)
    return dict(schema='osr-twin-infrastructure-study/1',items=items,gauge_m=p['gauge_m'],
        measured_surrogate_gauge_m=2*rail_y-head_width,
        thermal_movement_study=dict(assumed_alpha_per_k=12e-6,assumed_delta_temperature_k=50.,
            required_longitudinal_movement_m=12e-6*50*L,approved_movement_capacity_m=None),
        support_study=rail_support(p),contact_model_crosswalk_status='open; visual surrogate is not a contact profile',
        structural_design_released=False,physical_validation=False)


def compile_design(inputs=None, *, variant_choices=None):
    inputs=deepcopy(inputs if inputs is not None else load_definition(DATA/'design-inputs.json'))
    if inputs.get('schema')!='osr-twin-design-inputs/1' or any(v is not False for v in inputs['gates'].values()):
        raise ValueError('study inputs cannot establish release or physical validation')
    sources=load_definition(ROOT/'engineering/best_practice/data/sources.json')
    research=validate_research_graph(load_definition(DATA/'research-graph.json'),sources)
    known_sources={s['id'] for s in sources['sources']}
    for category in ('hvac','doors','electrical','infrastructure'):
        if not set(inputs[category]['source_ids']) <= known_sources:raise ValueError('unknown design source')
    if inputs['hvac']['module_count_per_car'] != 4 or inputs['hvac']['baseline_allowance_modules_per_car']!=3:
        raise ValueError('four-module proposal with a three-module baseline allowance is the studied topology')
    base=compile_variant(variant_choices);model=deepcopy(base['model']);baseline_hash=fingerprint(model)
    rail_study=rail_support(inputs['infrastructure'])
    # SpatialStructure distributes this historical key by tributary length and
    # divides between two rails. Its dimensional meaning is N/m², despite the
    # inherited suffix. Convert per-seat N/m explicitly instead of assigning it.
    distributed_pad=2*rail_study['series_stiffness_n_m']/inputs['infrastructure']['seat_spacing_m']
    model['bridge']['track']['pad_stiffness_n_m']=distributed_pad
    model['bridge']['track']['basis']='OSR study: two pads in series per rail seat, two rails, stated spacing; distributed foundation modulus in N/m² stored in legacy pad_stiffness_n_m key. Actual curves, damping and restraint unqualified.'
    model['revision']='OSR-TWIN-STUDY-'+fingerprint(inputs)[:12]
    parts={r['id']:r for r in model['instances']};features=[];deductions=[];allocated={}
    def add(car,name,part_id,role,spec,position,density,refs,practices,mass=None,mass_public=False):
        id=car['id']+'/'+name
        if id in parts:raise ValueError('duplicate installed feature')
        if mass is None:masses=[primitive_volume(q)*density for q in spec['primitives']]
        else:
            volumes=[primitive_volume(q) for q in spec['primitives']];masses=[mass*v/sum(volumes) for v in volumes]
        props=_properties(aggregate(spec['primitives'],masses),
            'public nominal candidate mass; approximate/reference only' if mass_public else
            'OSR assumed equipment mass distributed over study solids' if mass is not None else
            'OSR assumed density and original reference solids; certificate open')
        host=parts[car['id']+'/body'];datum='design-'+name
        host['datums'][datum]=transform(*(position[i]-host['transform']['translation_m'][i] for i in range(3)))
        row=dict(id=id,part_id=part_id,revision=model['revision'],serial=None,batch=None,parent=host['id'],quantity=1,unit='ea',
            geometry=dict(kind='osr-parametric-reference',source=[source(spec)],material_regions=[],thickness_m=None,
                process='unissued OSR study; qualified manufacturing and supplier selection open'),
            transform=transform(*position),datums=dict(origin=transform()),body=car['id'],bogie=None,axle=None,scope=[id],
            property_source='design',properties=dict(design=props,supplier=None,measured=None),requirements=[],inspections=[])
        model['instances'].append(row);parts[id]=row
        model['joints'].append(dict(id=id+'/mount',revision=model['revision'],connection='fixed',type='bolted',
            endpoints=[dict(instance=host['id'],datum=datum),dict(instance=id,datum='origin')],permitted_motion=[],
            property_source='design',properties=dict(design=None,supplier=None,measured=None),
            definition=dict(physical_definition_status='installed study datums; fastener capacity/preload/fatigue open'),requirements=[],inspections=[]))
        inspection=id+'/datum'
        model['inspections'].append(dict(id=inspection,instance=id,characteristic='installed datum and removal/access envelope',unit='m',
            minimum=None,maximum=None,dependencies=['mass-properties','vehicle-model']))
        row['inspections'].append(inspection)
        features.append(dict(instance_id=id,part_id=part_id,role=role,source_ids=refs,practice_ids=practices,
            geometry=spec,position_m=position,mass_kg=props['mass_kg'],
            property_basis=props['basis'],material_certificate=None,installation_inspection=inspection,
            source_design_status='original OSR study with public candidate envelopes',
            production_released=False,physical_validation=False))
        return id
    for car in model['family_definition']['cars']:
        cid=car['id'];x=car['centre_x_m'];before=len(features);h=inputs['hvac'];d=inputs['doors'];e=inputs['electrical']
        modules=[]
        module_x=[(j-(h['module_count_per_car']-1)/2)*h['module_spacing_m'] for j in range(h['module_count_per_car'])]
        for j,offset in enumerate(module_x,1):
            modules.append(add(car,'hvac-module-'+str(j),'LM3-EXT-P040','replaceable-hvac-module',
                dict(role='public-HVAC-module-envelope',primitives=[box('module',[0,0,h['module_dimensions_m'][2]/2],h['module_dimensions_m'])]),
                [x+offset,0,h['roof_base_z_m']+.04],2700.,h['source_ids'],['hvac','maintenance'],mass=h['module_mass_kg'],mass_public=True))
        allocated.setdefault('LM3-EXT-P040',[]).append(modules)
        carrier_length=(h['module_count_per_car']-1)*h['module_spacing_m']+h['module_dimensions_m'][0]+.10
        support=tray('HVAC-drained-carrier',carrier_length,1.76,.03,h['carrier_thickness_m'])
        support['primitives'][0]=plate('mounting-base',[0,0,0],[carrier_length,1.76,h['carrier_thickness_m']],
            [[a,b] for a in (-carrier_length/2+.20,carrier_length/2-.20) for b in (-.75,.75)],.0065)
        for j,offset in enumerate(module_x):
            for a in (-.4,.4):
                for b in (-.65,.65):
                    support['primitives'].append(box(f'module-foot-{j}-{a}-{b}',
                        [offset+a,b,.021],[.06,.08,.038]))
        id=add(car,'hvac-carrier','LM3-ROOF-P010','removable-roof-carrier',support,[x,0,h['roof_base_z_m']],h['carrier_density_kg_m3'],h['source_ids'],['hvac','fasteners'])
        allocated.setdefault('LM3-ROOF-P010',[]).append([id])
        for side in (-1,1):
            for direction in (-1,1):
                suffix=f'{side}-{direction}';px=x+direction*car['length_m']*d['longitudinal_fraction']
                leaf=dict(role='door-installation-envelope',primitives=[box('leaf-left',[-.295,0,0],[.59,.05,2.18]),
                    box('leaf-right',[.295,0,0],[.59,.05,2.18]),box('drive-reservation',[0,0,1.135],[1.20,.05,.07])])
                id=add(car,'door-'+suffix,'LM3-EXT-P010','replaceable-door-cassette',leaf,[px,side*1.27,d['centre_z_m']],2700.,d['source_ids'],['doors','boarding-system'],mass=d['leaf_mass_kg'])
                allocated.setdefault('LM3-EXT-P010',[]).append([id])
                t=d['carrier_thickness_m'];header=d['opening_height_m']/2+.08;footer=-d['opening_height_m']/2
                stile_height=header-footer-t;stile_z=(header+footer)/2
                st=d['stile_thickness_m'];frame=dict(role='open-door-carrier',primitives=[
                    plate('datum-header',[0,0,header],[1.42,.12,t],[[a,b] for a in (-.55,.55) for b in (-.03,.03)],.0065),
                    box('threshold',[0,0,footer],[1.42,.12,t])])
                for sign in (-1,1):
                    frame['primitives'].append(box(f'stile-web-{sign}',
                        [sign*(d['opening_width_m']/2+.05-st/2),0,stile_z],[st,.12-2*st,stile_height]))
                    for flank in (-1,1):
                        frame['primitives'].append(box(f'stile-flange-{sign}-{flank}',
                            [sign*(d['opening_width_m']/2+.025),flank*(.06-st/2),stile_z],[.05,st,stile_height]))
                id=add(car,'door-carrier-'+suffix,'LM3-DOOR-P010','surveyed-door-carrier',frame,[px,side*d['lateral_m'],d['centre_z_m']],d['carrier_density_kg_m3'],d['source_ids'],['doors','fasteners'])
                allocated.setdefault('LM3-DOOR-P010',[]).append([id])
        pos=[x+e['cabinet_position_m'][0],*e['cabinet_position_m'][1:]]
        panel=add(car,'hv-service-panel','LM3-TRC-P070','segregated-hv-service-panel',cabinet(e),pos,e['density_kg_m3'],e['source_ids'],['hv-distribution','cybersecurity'])
        allocated.setdefault('LM3-TRC-P070',[]).append([panel])
        converter=add(car,'isolated-lv-converter','LM3-TRC-P030','isolated-lv-converter-reservation',
            dict(role='isolated-LV-converter-reservation',primitives=[box('converter',[0,0,0],[.30,.20,.10])]),
            [x,.85,.67],2700.,['harting-rail-guide','iec-insulation'],['hv-distribution'],mass=15.)
        allocated.setdefault('LM3-TRC-P030',[]).append([converter])
        hvgroup=[]
        for name,y,part in [('hv-cable-tray',e['hv_tray_y_m'],'LM3-HV-P020'),('lv-cable-tray',e['lv_tray_y_m'],'LM3-CTRL-P040')]:
            id=add(car,name,part,'segregated-cable-support',tray(name,e['tray_length_m'],e['tray_width_m'],e['tray_height_m'],e['tray_thickness_m']),
                [x,y,e['tray_z_m']],e['density_kg_m3'],e['source_ids'],['hv-distribution'])
            if part=='LM3-HV-P020':hvgroup.append(id)
            else:allocated.setdefault(part,[]).append([id])
        for sign in (-1,1):
            spec=dict(role='replaceable-transit-frame',primitives=[box('edge-top',[0,0,.085],[.008,.20,.03]),
                box('edge-bottom',[0,0,-.085],[.008,.20,.03]),box('edge-left',[0,-.085,0],[.008,.03,.14]),
                box('edge-right',[0,.085,0],[.008,.03,.14])])
            hvgroup.append(add(car,'transit-'+str(sign),'LM3-HV-P020','barrier-transit-frame',spec,[x+sign*4.55,e['hv_tray_y_m'],.89],e['density_kg_m3'],['roxtec-transit','roxtec-conduit'],['hv-distribution','fire-response']))
        allocated.setdefault('LM3-HV-P020',[]).append(hvgroup)
        sensors=[]
        for sign in (-1,1):
            sensors.append(add(car,'battery-sensor-'+str(sign),'LM3-SAF-P010','temperature-offgas-sensor-reservation',
                dict(role='battery-sensor-reservation',primitives=[box('pod',[0,0,0],[.08,.06,.04])]),
                [x+sign*4.8,0,.75],1400.,['roxtec-rolling','siemens-bogie-diagnostics'],['batteries','fire-response']))
        allocated.setdefault('LM3-SAF-P010',[]).append(sensors)
        install_service_parts(car,inputs,add,allocated)
        installed=sum(r['mass_kg'] for r in features[before:])
        additional=(h['module_count_per_car']-h['baseline_allowance_modules_per_car'])*h['module_mass_kg']
        extracted=installed-additional;body=parts[cid+'/body'];props=body['properties']['design'];old=props['mass_kg']
        if not 0 < extracted < old:raise ValueError('explicit features exceed synthetic residual mass budget')
        props['mass_kg']-=extracted;factor=props['mass_kg']/old
        props['inertia_tensor_kg_m2']=(np.asarray(props['inertia_tensor_kg_m2'])*factor).tolist()
        props['uncertainty_kg']*=factor;props['inertia_uncertainty_kg_m2']*=factor
        props['basis']+='; expanded HVAC/doors/HV/LV/barrier/sensor study masses removed from this uniform residual budget'
        deductions.append(dict(car=cid,original_residual_kg=old,extracted_explicit_kg=extracted,
            installed_feature_mass_kg=installed,additional_hvac_mass_kg=additional,remaining_residual_kg=props['mass_kg'],
            allowance_basis='OSR assumed three-module allowance inside original synthetic body budget; not a measured original HVAC mass'))
    for row in model['instances']:row['revision']=model['revision']
    for row in model['joints']:row['revision']=model['revision']
    model['notes']='Best-practice study variant: explicit modules, carriers, service panels, supports, routed harness sections, connector reservations, coolant pipe walls/clamps, seals and sensors. Material/process/load/supplier/physical release open. Original residual budget redistributed; CG/inertia recomputed. Service evidence is configuration-specific.'
    validate(model);interfaces=_interfaces(model,base['battery'])
    def interface(id,kind,left,right,ports,limits,refs):
        units={'electrical':dict(voltage='V',current='A',power='W'),'control':dict(timestamp='s',latency='s')}
        interfaces['interfaces'].append(dict(id=id,type=kind,
            endpoints=[dict(instance=instance,datum='origin',port=port,role='study interface owner') for instance,port in zip((left,right),ports)],
            joint=None,units=units[kind],sign_convention='power/commands from endpoint 1 to endpoint 2; observations return',limits=limits,
            evidence='original OSR study; sources '+', '.join(refs),
            model_limits=['operating targets only; physical connector, protection, latency and equipment ratings unqualified']))
    for car in model['family_definition']['cars']:
        cid=car['id'];panel=cid+'/hv-service-panel';converter=cid+'/isolated-lv-converter'
        interface(converter+'/input','electrical',panel,converter,['switched-HV-output','converter-HV-input'],
            dict(voltage_v=[600.,900.],current_a=[0.,6.]),['iec-insulation'])
        for row in interfaces['interfaces']:
            if row['id'] in (cid+'/battery/dc',cid+'/battery/bms'):
                row['endpoints'][1].update(instance=panel,datum='origin',role='explicit HV service-panel study')
        for f in [f for f in features if f['instance_id'].startswith(cid+'/')]:
            id=f['instance_id']
            if f['role'] in ('replaceable-hvac-module','replaceable-door-cassette'):
                door=f['role']=='replaceable-door-cassette'
                interface(id+'/power','electrical',converter if door else panel,id,
                    ['isolated-LV-output' if door else 'switched-HV-study-output','module-input'],
                    dict(voltage_v=[20.,28.] if door else [600.,900.],current_a=[0.,20.] if door else [0.,60.]),f['source_ids'])
                interfaces['interfaces'][-1]['model_limits'].append(
                    'isolated converter rating and isolation tests open' if door else
                    'HVAC supply voltage/conversion compatibility not established by public cooling/envelope data')
                interface(id+'/control','control',panel,id,['interlock-and-status','module-control'],dict(latency_s=None),f['source_ids'])
            if f['role']=='temperature-offgas-sensor-reservation':
                interface(id+'/status','control',id,panel,['sensor-observation','safety-input'],dict(latency_s=None),f['source_ids'])
    interfaces['configuration_sha256']=fingerprint(model);validate_interfaces(interfaces,model)
    allocations={}
    for row in base['coverage']['rows']:
        if row['instances']:allocations.setdefault(row['part_id'],[]).append(row['instances'])
    if set(allocations)&set(allocated):raise ValueError('new design would double-allocate an existing catalogue slot')
    allocations.update(allocated);coverage=_coverage(model,allocations,interfaces)
    for row in coverage['rows']:
        if row['part_id'] in allocated:
            row['representation']='partial-original-study-decomposition'
            row['limits'].append('selected features only; remaining kit contents, supplier internals and production piece-level decomposition open')
    cfg=configuration(model);vehicle=SpatialVehicle(model,cfg['joint_laws']);mass=model_mass_properties(model)
    additional_mass=sum(r['additional_hvac_mass_kg'] for r in deductions)
    expected_mass=base['review']['total_mass_kg']+additional_mass
    if not math.isclose(vehicle.total_mass,expected_mass,rel_tol=1e-12):raise ValueError('study feature masses counted twice')
    base_vehicle=SpatialVehicle(base['model'],base['spatial_configuration']['joint_laws'])
    reaction=sum(r['static_n'] for r in vehicle.contacts)
    hvac=inputs['hvac'];p=inputs['electrical']['precharge']
    nominal=dict(train_stopped=True,hvil_closed=True,insulation_ok=True,main_feedback_open=True,
        return_feedback_closed=True,precharge_feedback_closed=True,elapsed_s=3.5,link_voltage_ratio=.96)
    faults=[]
    for key in ('hvil_closed','insulation_ok','main_feedback_open','return_feedback_closed','precharge_feedback_closed','train_stopped'):
        changed=dict(nominal);changed[key]=False;faults.append(dict(case=key,decision=closure_decision(p,changed)))
    timeout=dict(nominal,elapsed_s=p['timeout_s']+.1);faults.append(dict(case='timeout',decision=closure_decision(p,timeout)))
    studies=dict(precharge=precharge(p,base['battery']['nominal_voltage_v']),
        nominal_closure=closure_decision(p,nominal),critical_faults=faults,
        hvac_three_module_baseline_one_out=thermal_study(hvac['thermal_assumptions'],2,hvac['module_cooling_w']),
        hvac_nominal=thermal_study(hvac['thermal_assumptions'],4,hvac['module_cooling_w']),
        hvac_one_module_out=thermal_study(hvac['thermal_assumptions'],3,hvac['module_cooling_w']))
    infra=infrastructure(inputs['infrastructure'])
    paths={**base['review']['sources_sha256']}
    for path in [*sorted((ROOT/'engineering/twin_design').rglob('*.py')),*sorted(DATA.glob('*.json')),
                 ROOT/'engineering/best_practice/data/practices.json',ROOT/'engineering/best_practice/data/sources.json',
                 ROOT/'tools/automation/design-best-practice-twin.py',ROOT/'tools/automation/design-twin-freecad.py']:
        paths[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    comparison=ROOT/'engineering/assurance/numerical_reproducibility.py'
    paths[str(comparison.relative_to(ROOT))]=hashlib.sha256(comparison.read_bytes()).hexdigest()
    dynamics=[dict(id=g['id'],mass_kg=g['mass'],cg_m=g['cg'].tolist(),inertia_kg_m2=g['inertia'].tolist(),
        cg_change_m=(g['cg']-base_vehicle.groups[g['id']]['cg']).tolist()) for g in vehicle.groups.values() if g['kind']=='carbody']
    report=dict(schema='osr-best-practice-twin-review/1',configuration_sha256=fingerprint(model),baseline_configuration_sha256=baseline_hash,
        inputs_sha256=fingerprint(inputs),source_sha256=paths,car_count=model['family_definition']['car_count'],
        instance_count=len(model['instances']),added_instance_count=len(features),joint_count=len(model['joints']),
        interface_count=len(interfaces['interfaces']),infrastructure_instance_count=len(infra['items']),
        total_train_mass_kg=vehicle.total_mass,additional_study_train_mass_kg=additional_mass,
        mass_reallocation_residual_kg=vehicle.total_mass-expected_mass,
        static_reaction_balance_n=reaction-vehicle.total_mass*9.81,minimum_static_contact_n=min(r['static_n'] for r in vehicle.contacts),
        carbody_dynamics=dynamics,residual_budget=deductions,
        track_support_mapping=dict(per_rail_seat_stiffness_n_m=rail_study['series_stiffness_n_m'],
            seat_spacing_m=inputs['infrastructure']['seat_spacing_m'],two_rail_foundation_modulus_n_m2=distributed_pad,
            adapter_key='bridge.track.pad_stiffness_n_m',adapter_dimensional_meaning='N/m²',supplier_curves_verified=False),
        explicit_reference_allocations=coverage['explicit_reference_allocation_count'],required_allocations=coverage['required_allocation_count'],
        remaining_allocations=coverage['unresolved_allocation_count'],new_allocation_semantics='partial selected feature decomposition; not whole kit qualification',
        research=research,design_generated=True,native_execution_required=True,complete_dynamic_passage_qualified=False,
        contact_domain_issue_resolved=False,one_module_out_comfort_screen_passed=studies['hvac_one_module_out']['within_declared_study_limit'],
        three_module_baseline_one_out_comfort_screen_passed=studies['hvac_three_module_baseline_one_out']['within_declared_study_limit'],
        design_deviations=[dict(part_id='LM3-EXT-P040',catalogue_basis='one 24 kW HVAC assembly per car',
            proposal='four public nominal 8 kW module envelopes, 32 kW total, one-module-out study capacity 24 kW',
            change_approval=None,supplier_voltage_and_capacity_compatibility=None,status='proposed-alternative-not-promoted-to-catalogue')],
        production_released=False,physical_validation=False,
        remaining_gates=['released profiles and complete six-car coupled passage','actual structural/joint/anchor/fixture capacities',
            'installed HVAC derating, airflow, fresh air and failed-module comfort','qualified precharge/contactor and protection ratings',
            'sealed cable penetrations and fire evidence; sensor/controller implementation',
            'physical kit decomposition, supplier freeze, tests and independent project acceptance'])
    return dict(inputs=inputs,model=model,battery=base['battery'],spatial_configuration=cfg,interfaces=interfaces,
        coverage=coverage,features=features,infrastructure=infra,studies=studies,mass_properties=mass,
        joint_register=definitions(model),verification=verification_register(model,implementation_hashes=paths),review=report)
