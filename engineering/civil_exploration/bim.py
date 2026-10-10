"""Whole-assembly IFC from the canonical catalogue solids, with stable IDs."""
from __future__ import annotations
import math
import uuid
from pathlib import Path

from osr_mech.civil.exploration import assembly_parts
from .contracts import encoded, sha


def export(candidate, study, output: Path):
    import ifcopenshell
    f = ifcopenshell.file(schema='IFC4X3')
    def guid(label):
        return ifcopenshell.guid.compress(uuid.uuid5(uuid.NAMESPACE_URL, candidate['id']+'/'+label).hex)
    def point(x): return f.create_entity('IfcCartesianPoint', Coordinates=[float(v) for v in x])
    def axis(x): return f.create_entity('IfcAxis2Placement3D', Location=point(x))
    context = f.create_entity('IfcGeometricRepresentationContext', ContextIdentifier='Body', ContextType='Model',
                              CoordinateSpaceDimension=3, Precision=1e-7, WorldCoordinateSystem=axis([0,0,0]))
    units = f.create_entity('IfcUnitAssignment', Units=[f.create_entity('IfcSIUnit', UnitType='LENGTHUNIT', Name='METRE')])
    project = f.create_entity('IfcProject', GlobalId=guid('project'), Name='Unreleased civil exploration', RepresentationContexts=[context], UnitsInContext=units)
    bridge = f.create_entity('IfcBridge', GlobalId=guid('bridge'), Name=study['name'], ObjectPlacement=f.create_entity('IfcLocalPlacement', RelativePlacement=axis([0,0,0])))
    f.create_entity('IfcRelAggregates', GlobalId=guid('project-bridge'), RelatingObject=project, RelatedObjects=[bridge])
    products, rows = [], [];material_cache={}
    descriptions = assembly_parts(candidate['definition'], candidate['foundation'], study['route_length_m'])
    for part in descriptions:
        centre = part['centre_m']
        if part['shape'] == 'box':
            length, width, height = part['dimensions_m']
            profile = f.create_entity('IfcRectangleProfileDef', ProfileType='AREA', XDim=length, YDim=width)
            volume = length*width*height
        else:
            height = part['length_m']
            if part['shape']=='annulus':
                profile=f.create_entity('IfcCircleHollowProfileDef',ProfileType='AREA',Radius=part['diameter_m']/2,WallThickness=(part['diameter_m']-part['inner_diameter_m'])/2)
                volume=math.pi*(part['diameter_m']**2-part['inner_diameter_m']**2)/4*height
            else:
                profile = f.create_entity('IfcCircleProfileDef', ProfileType='AREA', Radius=part['diameter_m']/2)
                volume = math.pi*part['diameter_m']**2/4*height
        solid = f.create_entity('IfcExtrudedAreaSolid', SweptArea=profile, Position=axis([0,0,-height/2]),
                                ExtrudedDirection=f.create_entity('IfcDirection', DirectionRatios=[0.,0.,1.]), Depth=height)
        representation = f.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body',
                                         RepresentationType='SweptSolid', Items=[solid])
        kind = {'deck':'IfcBeam','cap':'IfcBeam','pier':'IfcColumn','foundation':'IfcFooting','pile':'IfcPile'}[part['kind']]
        product = f.create_entity(kind, GlobalId=guid(part['id']), Name=part['id'], Description='Research envelope; no construction release',
                                  ObjectPlacement=f.create_entity('IfcLocalPlacement', RelativePlacement=axis(centre)),
                                  Representation=f.create_entity('IfcProductDefinitionShape', Representations=[representation]))
        q = f.create_entity('IfcQuantityVolume', Name='NetVolume', VolumeValue=volume)
        element_q = f.create_entity('IfcElementQuantity', GlobalId=guid(part['id']+'-quantity'), Name='ResearchNetQuantities', Quantities=[q])
        f.create_entity('IfcRelDefinesByProperties', GlobalId=guid(part['id']+'-qrel'), RelatedObjects=[product], RelatingPropertyDefinition=element_q)
        base=(candidate['material'] if part['kind']=='deck' else candidate.get('foundation_material',candidate.get('support_material',candidate['material'])) if part['kind'] in ('pile','foundation') else candidate.get('support_material',candidate['material']))
        record=base if part['material']=='concrete' else candidate['material_records'][part['material']]
        key=encoded(record)
        if key not in material_cache:
            material=f.create_entity('IfcMaterial',Name=record['name'],Description=record['basis'])
            properties=[]
            for name,value,kind in [('YoungsModulusPa',record['youngs_modulus_pa'],'IfcReal'),('DensityKgM3',record['density_kg_m3'],'IfcReal'),
                                    ('StiffnessFactor',record['stiffness_factor'],'IfcReal'),
                                    ('PoissonRatio',record['poisson_ratio'],'IfcReal'),('Measured',record['measured'],'IfcBoolean'),('Basis',record['basis'],'IfcText')]:
                properties.append(f.create_entity('IfcPropertySingleValue',Name=name,NominalValue=f.create_entity(kind,value)))
            for name,value in record.get('orthotropic',{}).items():
                properties.append(f.create_entity('IfcPropertySingleValue',Name=name,NominalValue=f.create_entity('IfcReal',value)))
            f.create_entity('IfcMaterialProperties',Name='UnqualifiedResearchMaterialRecord',Properties=properties,Material=material)
            material_cache[key]=material
        material=material_cache[key]
        f.create_entity('IfcRelAssociatesMaterial', GlobalId=guid(part['id']+'-material'), RelatedObjects=[product], RelatingMaterial=material)
        products.append(product); rows.append(dict(id=part['id'], ifc_guid=product.GlobalId, kind=part['kind'], material=part['material'], volume_m3=volume))
    f.create_entity('IfcRelContainedInSpatialStructure', GlobalId=guid('containment'), RelatedElements=products, RelatingStructure=bridge)
    # Stable header metadata rather than host timestamps or absolute paths.
    f.header.file_name.name='civil-research.ifc'; f.header.file_name.time_stamp='2026-10-09T00:00:00'
    f.header.file_name.author=('OpenSourceRail research generator',); f.header.file_name.organization=('OpenSourceRail',)
    f.header.file_name.preprocessor_version='civil-exploration-ifc/1'; f.header.file_name.originating_system='OSR'; f.header.file_name.authorization='Unreleased'
    output.parent.mkdir(parents=True, exist_ok=True); f.write(str(output))
    reopened = ifcopenshell.open(str(output))
    if len(reopened.by_type('IfcElement')) != len(products):
        raise ValueError('IFC product coverage differs from source solids')
    receipt = dict(schema='osr-civil-ifc/1', candidate_id=candidate['id'], ifc_sha256=sha(output),
                   ifcopenshell_version=ifcopenshell.version,
                   source_quantities=rows, source_volume_m3=math.fsum(r['volume_m3'] for r in rows),
                   geometry_authority='design/component-catalogue/src/osr_mech/civil/exploration.py', physical_release=False)
    output.with_suffix('.json').write_bytes(encoded(receipt))
    return receipt
