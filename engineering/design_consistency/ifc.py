"""Exact civil primitive solids plus an explicit, separately scoped IFC analysis model."""
from __future__ import annotations
import numpy as np
from osr_mech.engineering_definition import fingerprint
from .contracts import validate


def export(contract,path):
    import ifcopenshell
    from ifcopenshell.api import root,context,unit,aggregate,geometry,pset,material,structural,group,spatial
    model=ifcopenshell.file(schema='IFC4X3');project=root.create_entity(model,ifc_class='IfcProject',name='OSR shared-definition research bay')
    unit.assign_unit(model,units=[unit.add_si_unit(model,unit_type='LENGTHUNIT'),unit.add_si_unit(model,unit_type='AREAUNIT'),unit.add_si_unit(model,unit_type='VOLUMEUNIT'),unit.add_si_unit(model,unit_type='MASSUNIT',prefix='KILO')])
    world=context.add_context(model,context_type='Model');body=context.add_context(model,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=world)
    reference=context.add_context(model,context_type='Model',context_identifier='Reference',target_view='GRAPH_VIEW',parent=world)
    site=root.create_entity(model,ifc_class='IfcSite',name='Uncalibrated research site');aggregate.assign_object(model,products=[site],relating_object=project)
    def point(x):return model.create_entity('IfcCartesianPoint',Coordinates=tuple(float(v)for v in x))
    def direction(x):return model.create_entity('IfcDirection',DirectionRatios=tuple(float(v)for v in x))
    def position(x,axis=(0,0,1),ref=(1,0,0)):return model.create_entity('IfcAxis2Placement3D',Location=point(x),Axis=direction(axis),RefDirection=direction(ref))
    def circle(radius,xy=(0,0)):return model.create_entity('IfcCircle',Position=model.create_entity('IfcAxis2Placement2D',Location=point(xy)),Radius=float(radius))
    def solid(p):
        kind=p['kind'];c=np.array(p['centre_m'],float)
        if kind in ('box','plate','perforated-plate'):
            x,y,l=p['dimensions_m'];c[2]-=l/2
            if kind=='box':profile=model.create_entity('IfcRectangleProfileDef',ProfileType='AREA',XDim=float(x),YDim=float(y))
            else:
                coords=[(-x/2,-y/2),(x/2,-y/2),(x/2,y/2),(-x/2,y/2),(-x/2,-y/2)]
                outer=model.create_entity('IfcPolyline',Points=[point(q)for q in coords])
                profile=model.create_entity('IfcArbitraryProfileDefWithVoids',ProfileType='AREA',OuterCurve=outer,InnerCurves=[circle(p['hole_radius_m'],q)for q in p['holes_xy_m']])
            axis=(0,0,1);ref=(1,0,0)
        else:
            l=p['length_m'];axis={'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[p['axis']];ref=(0,1,0)if p['axis']=='x'else(1,0,0);c-=np.array(axis)*l/2
            if kind=='perforated-cylinder':profile=model.create_entity('IfcArbitraryProfileDefWithVoids',ProfileType='AREA',OuterCurve=circle(p['radius_m']),InnerCurves=[circle(p['hole_radius_m'],q)for q in p['holes_xy_m']])
            elif kind=='tube':profile=model.create_entity('IfcCircleHollowProfileDef',ProfileType='AREA',Radius=float(p['radius_m']),WallThickness=float(p['radius_m']-p['inner_radius_m']))
            elif kind=='cylinder':profile=model.create_entity('IfcCircleProfileDef',ProfileType='AREA',Radius=float(p['radius_m']))
            else:raise ValueError('IFC civil exporter only accepts supported exact extrusions')
        return model.create_entity('IfcExtrudedAreaSolid',SweptArea=profile,Position=position(c,axis,ref),ExtrudedDirection=direction((0,0,1)),Depth=float(l))
    validate(contract);objects={}
    for p in contract['parts']:
        cls='IfcReinforcingBar'if '-rebar-'in p['id']else 'IfcTendon'if p['id'].startswith('tendon-')else 'IfcPile'if p['id'].startswith('pile-')else 'IfcBearing'if p['id'].startswith('bearing-')else 'IfcBuildingElementProxy'
        obj=root.create_entity(model,ifc_class=cls,name=p['id']);objects[p['id']]=obj;spatial.assign_container(model,products=[obj],relating_structure=site)
        representation=model.create_entity('IfcShapeRepresentation',ContextOfItems=body,RepresentationIdentifier='Body',RepresentationType='SweptSolid',Items=[solid(q)for q in p['manufacturing']['primitives']])
        geometry.assign_representation(model,product=obj,representation=representation)
        matrix=np.eye(4);matrix[:3,:3]=p['placement']['rotation'];matrix[:3,3]=p['placement']['translation_m'];geometry.edit_object_placement(model,product=obj,matrix=matrix,is_si=True)
        mat=material.add_material(model,name=p['material']);material.assign_material(model,products=[obj],material=mat)
        props=pset.add_pset(model,product=obj,name='OSR_SharedRepresentation')
        pset.edit_pset(model,pset=props,properties={'PhysicalPartId':p['id'],'Revision':p['revision'],'GeometrySHA256':fingerprint(p['manufacturing']),'MassKg':p['properties']['mass_kg'],'DensityKgM3':contract['materials'][p['material']]['density_kg_m3'],'ProductionReleased':False,'PhysicalValidation':False})
    analysis=structural.add_structural_analysis_model(model);analysis.Name='Gross elastic deck model; foundations and detailed resistance unresolved';analysis.PredefinedType='LOADING_3D'
    deck=objects['deck'];definition=next(p for p in contract['parts']if p['id']=='deck');length=max(q['dimensions_m'][2]for q in definition['manufacturing']['primitives']);z=definition['properties']['cg_m'][2]
    member=root.create_entity(model,ifc_class='IfcStructuralCurveMember',name='deck-centreline');member.PredefinedType='RIGID_JOINED_MEMBER';member.Axis=direction((0,0,1))
    edge=model.create_entity('IfcEdge',EdgeStart=model.create_entity('IfcVertexPoint',VertexGeometry=point((0,0,z))),EdgeEnd=model.create_entity('IfcVertexPoint',VertexGeometry=point((length,0,z))))
    geometry.assign_representation(model,product=member,representation=model.create_entity('IfcShapeRepresentation',ContextOfItems=reference,RepresentationIdentifier='Reference',RepresentationType='Edge',Items=[edge]))
    relation=root.create_entity(model,ifc_class='IfcRelAssignsToProduct');relation.RelatedObjects=[member];relation.RelatingProduct=deck
    connections=[]
    for i,x in enumerate((0,length)):
        obj=root.create_entity(model,ifc_class='IfcStructuralPointConnection',name=f'idealised-support-{i}')
        obj.AppliedCondition=model.create_entity('IfcBoundaryNodeCondition',Name='pin/roller; bearing foundation compliance excluded',TranslationalStiffnessX=model.create_entity('IfcBoolean',i==0),TranslationalStiffnessY=model.create_entity('IfcBoolean',True),TranslationalStiffnessZ=model.create_entity('IfcBoolean',True))
        vertex=model.create_entity('IfcVertexPoint',VertexGeometry=point((x,0,z)))
        geometry.assign_representation(model,product=obj,representation=model.create_entity('IfcShapeRepresentation',ContextOfItems=reference,RepresentationIdentifier='Reference',RepresentationType='Vertex',Items=[vertex]))
        rel=root.create_entity(model,ifc_class='IfcRelConnectsStructuralMember');rel.RelatingStructuralMember=member;rel.RelatedStructuralConnection=obj;connections.append(obj)
    structural.assign_structural_analysis_model(model,products=[member,*connections],structural_analysis_model=analysis)
    load=structural.add_structural_load(model,name='Deck self weight',ifc_class='IfcStructuralLoadLinearForce');load.LinearForceZ=-sum(p['properties']['mass_kg']for p in contract['parts']if p['id']=='deck'or p['id'].startswith(('deck-rebar-','tendon-')))*9.80665/length
    activity=structural.add_structural_activity(model,applied_load=load,structural_member=member,ifc_class='IfcStructuralCurveAction')
    loads=structural.add_structural_load_group(model,name='Dead-load elastic case',action_type='PERMANENT_G',action_source='DEAD_LOAD_G');group.assign_group(model,products=[activity],group=loads);analysis.LoadedBy=[loads]
    model.write(str(path))
    # Reopen the IFC, assert identifiers and material-volume correspondence.
    restored=ifcopenshell.open(str(path));import ifcopenshell.geom,ifcopenshell.util.shape
    settings=ifcopenshell.geom.settings();settings.set('mesher-linear-deflection',1e-5);settings.set('mesher-angular-deflection',.02)
    errors=[]
    for identity,obj in objects.items():
        shape=ifcopenshell.geom.create_shape(settings,restored.by_guid(obj.GlobalId));volume=ifcopenshell.util.shape.get_volume(shape.geometry)
        physical=next(p for p in contract['parts']if p['id']==identity);expected=physical['properties']['mass_kg']/contract['materials'][physical['material']]['density_kg_m3'];error=abs(volume/expected-1)
        if error>5e-4:raise ValueError('IFC solid volume differs: '+identity)
        errors.append(error)
    return dict(schema='osr-ifc-analysis-correspondence/1',configuration_sha256=fingerprint(contract),ifcopenshell_version=ifcopenshell.version,
        physical_part_count=len(objects),maximum_tessellation_volume_relative_error=max(errors),explicit_structural_members=1,explicit_connections=2,explicit_loads=1,
        analytical_scope='gross elastic deck on pin/roller supports; pier/bearing/pile capacity and ground compliance unresolved',analysis_executed=False,physical_validation=False,production_released=False)
