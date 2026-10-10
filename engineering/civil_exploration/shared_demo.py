"""Explicit synthetic car-pair inputs for equation and change-propagation checks."""
from copy import deepcopy
import json
from pathlib import Path

from osr_mech.family_definition import family_definition, BOGIE_WHEELBASE_MM


IDENTITY = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]


def transform(x=0., y=0., z=0.):
    return dict(translation_m=[x,y,z], rotation=deepcopy(IDENTITY))


def cuboid_inertia(mass, dimensions):
    x,y,z=dimensions
    return [[mass*(y*y+z*z)/12,0.,0.],[0.,mass*(x*x+z*z)/12,0.],[0.,0.,mass*(x*x+y*y)/12]]


def demonstration(family='metro-6car'):
    from .contracts import HERE, load
    from .workflow import candidate
    definition=family_definition(family);instances=[];joints=[];length=definition['car_length_m']
    if definition['car_count']<2:raise ValueError('articulated demonstration needs a two-car family')
    def instance(identifier,part,parent,mass,dimensions,placement,body=None,bogie=None,axle=None,datums=None):
        record=dict(mass_kg=mass,cg_m=[0.,0.,0.],inertia_tensor_kg_m2=cuboid_inertia(mass,dimensions),
            uncertainty_kg=mass*.02,position_uncertainty_m=.01,inertia_uncertainty_kg_m2=mass*.01,
            basis='synthetic uniform-mass verification body; mass declared independently of CAD/envelope volume',evidence=None)
        result=dict(id=identifier,part_id=part,revision='SYNTHETIC-1',serial=None,batch=None,parent=parent,
            quantity=1,unit='ea',geometry=dict(kind='synthetic-verification',source=[part],material_regions=[],thickness_m=None,process=None),
            transform=placement,datums=datums or {'origin':transform()},body=body,bogie=bogie,axle=axle,scope=[identifier],
            property_source='design',properties=dict(design=record,supplier=None,measured=None),requirements=[],inspections=[])
        instances.append(result);return result
    def joint(identifier,connection,kind,a,da,b,db,k,c):
        props=None if connection=='fixed' else dict(stiffness_n_m=k,damping_ns_m=c,friction_coefficient=0.,lower_stop_m=-.1,upper_stop_m=.1,
            basis='synthetic equivalent vertical joint; no supplier or measured curve',evidence=None)
        joints.append(dict(id=identifier,revision='SYNTHETIC-1',connection=connection,type=kind,
            endpoints=[dict(instance=a,datum=da),dict(instance=b,datum=db)],permitted_motion=['yaw'] if kind=='articulation' else [],
            property_source='design',properties=dict(design=props,supplier=None,measured=None),
            definition={'physical_definition_status':'open-supplier/production-data'},requirements=[],inspections=[]))
    tare=definition['profile']['tare_mass_t']*1000/definition['car_count']
    for car in definition['cars'][:2]:
        cid=car['id'];body=cid+'/body';centre=car['centre_x_m'];inset=BOGIE_WHEELBASE_MM/1000
        body_datums={'secondary-A':transform(-length/2+inset,0.,-.7),'secondary-B':transform(length/2-inset,0.,-.7),
                     'end-A':transform(-length/2),'end-B':transform(length/2),'battery':transform(-2.,.45,-1.05)}
        body_instance=instance(body,'LM3-CAR-A900',cid,tare-7500.,[length,2.7,2.],transform(centre,0.,1.5),body=cid,datums=body_datums)
        body_instance['properties']['design']['basis']+='; remaining sprung-body allocation excludes the separately instantiated battery, frames and wheelsets'
        battery=cid+'/battery'
        instance(battery,'LM3-TRC-P040',body,2500.,[3.,.5,.5],transform(centre-2.,.45,.45),body=cid)
        joint(cid+'/battery-retention','fixed','bolted',body,'battery',battery,'origin',0.,0.)
        for index,bogie in enumerate(b for b in definition['bogies'] if b['parent']==cid):
            bid=bogie['id'];frame=bid+'/frame';powered=bogie['kind']=='powered'
            instance(frame,'LM3-BOG-P010' if powered else 'LM3-BOG-P020',body,1500.,[2.7,2.2,.6],transform(bogie['pivot_x_m'],0.,.8),
                bogie=bid,datums={'origin':transform(),'axle-1':transform(-inset/2,0.,-.42),'axle-2':transform(inset/2,0.,-.42)})
            joint(bid+'/secondary','secondary','suspension',body,'secondary-A' if index==0 else 'secondary-B',frame,'origin',7e5,4e4)
            for axle,x in enumerate(bogie['axle_x_m'],1):
                wheel=bid+f'/wheelset-{axle}'
                instance(wheel,'LM3-BOG-P040' if powered else 'LM3-BOG-P041',frame,500.,[2.,.4,.4],transform(x,0.,.38),bogie=bid,axle=axle)
                joint(wheel+'/primary','primary','suspension',frame,f'axle-{axle}',wheel,'origin',1.2e6,1.2e4)
    joint('car-1-2/articulation','articulation','articulation','car-1/body','end-B','car-2/body','end-A',3e5,1.5e4)
    study=load(HERE/'config/reference.json');c=candidate(study['candidates'][1],study)
    study['route_length_m']=75.
    bridge=dict(candidate=c,study=study,span_count=3,
        track=dict(EI_nm2=12.8e6,mass_kg_m=120.,pad_stiffness_n_m=80e6,pad_damping_ns_m=4e4,
                   basis='synthetic two-rail equivalent on distributed pads; no measured track calibration'),contact_n_m=80e6)
    return dict(schema='osr-shared-engineering/1',revision='SYNTHETIC-1',state='as-designed',asset_id=None,family=family,family_definition=definition,
        instances=instances,joints=joints,bridge=bridge,requirements=[],inspections=[
            dict(id='battery-mass-car-1',instance='car-1/battery',characteristic='installed battery mass',unit='kg',minimum=2400.,maximum=2600.,dependencies=['mass-properties']),
            dict(id='car-1-running-correlation',instance='car-1/body',characteristic='ride acceleration',unit='m/s2',minimum=None,maximum=None,dependencies=['bridge-demand'])],
        notes='Two representative planning cars; every mass, inertia and mechanical property is synthetic. Not a supplier train or Baghdad qualification.')


def variants(model):
    cases={}
    battery=deepcopy(model);row=next(r for r in battery['instances'] if r['id']=='car-1/battery');p=row['properties']['design']
    p['mass_kg']*=1.1;p['inertia_tensor_kg_m2']=[[v*1.1 for v in line] for line in p['inertia_tensor_kg_m2']]
    p['uncertainty_kg']*=1.1;p['inertia_uncertainty_kg_m2']*=1.1;row['revision']='SYNTHETIC-2';cases['battery-plus-10-percent']=battery
    suspension=deepcopy(model)
    for j in suspension['joints']:
        if j['connection']=='secondary':j['properties']['design']['stiffness_n_m']*=.8;j['revision']='SYNTHETIC-2'
    cases['secondary-minus-20-percent']=suspension
    articulation=deepcopy(model)
    next(j for j in articulation['joints'] if j['connection']=='articulation')['properties']['design']['stiffness_n_m']*=2
    cases['articulation-stiffness-doubled']=articulation
    deck=deepcopy(model);deck['bridge']['candidate']['material']['youngs_modulus_pa']*=.9
    cases['deck-modulus-minus-10-percent']=deck
    return cases
