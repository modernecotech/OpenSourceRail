"""Independent measurements of reopened B-rep solids, not parameter formulas."""
import json


def measure(fcstd, specification, destination):
    import FreeCAD as App
    import Part

    spec=json.loads(open(specification).read())
    doc=App.openDocument(str(fcstd))
    try:
        objects={getattr(o,'DesignId') if 'DesignId' in o.PropertiesList else getattr(o,'PhysicalPartId'):o for o in doc.Objects if 'DesignId' in o.PropertiesList or 'PhysicalPartId' in o.PropertiesList}
        volumes={name:o.Shape.Volume*1e-9 for name,o in objects.items()}
        samples=[]
        thickness=2.0  # mm; prismatic intervals only, no end blocks or joints
        for group in spec['groups']:
            for station in spec['stations_m']:
                slab=Part.makeBox(thickness,200000.,200000.,App.Vector(station*1000-thickness/2,-100000.,-100000.))
                pieces=[]
                for name in group['ids']:
                    for shape in objects[name].Shape.common(slab).Solids:
                        if shape.Volume<=1e-9:
                            continue
                        area=shape.Volume/thickness*1e-6
                        z=shape.CenterOfMass.z/1000
                        inertia=(shape.MatrixOfInertia.A22/thickness-(shape.Volume/thickness)*thickness**2/12)*1e-12
                        pieces.append((area,z,inertia))
                area=sum(p[0] for p in pieces)
                if area<=0:
                    raise ValueError('native section contains no material')
                centroid=sum(a*z for a,z,i in pieces)/area
                inertia=sum(i+a*(z-centroid)**2 for a,z,i in pieces)
                samples.append(dict(group=group['name'],station_m=station,area_m2=area,
                    centroid_z_m=centroid,inertia_vertical_bending_m4=inertia))
        # Independent control of B-rep units and centroidal inertia convention.
        control=Part.makeBox(4000.,2000.,3000.)
        controls=dict(box_volume_m3=control.Volume*1e-9,
            box_centroid_z_m=control.CenterOfMass.z/1000,
            box_inertia_yy_m5=control.MatrixOfInertia.A22*1e-15)
        report=dict(schema='osr-native-section-measurements/1',samples=samples,parts_volume_m3=volumes,
            strand_lengths_m={name:o.Shape.BoundBox.XLength/1000 for name,o in objects.items() if name.startswith('strand-')},
            controls=controls,method='Reopened B-rep volume, centroid and inertia of 2mm prismatic slabs; no analytical section formulas imported',
            physical_release=False)
        with open(destination,'w') as stream:json.dump(report,stream,indent=2)
    finally:
        App.closeDocument(doc.Name)


def specification(kind,assessment,model):
    from . import tasks
    from engineering.twin_workflow import core
    module,mapping=tasks.contexts(kind)
    ids=[p['id'] for p in model['parts']]
    if kind=='mechanical-detail':
        context=mapping[assessment['configuration_id']]
        variables=assessment['variables'];material=assessment['materials']['assumed_properties']
        side=module.i_section(context['side_member_width_m'],variables['side_depth_m'],variables['plate_thickness_m'],variables['web_thickness_m'])
        spine=module.box_section(context['centre_member_width_m'],context['centre_member_depth_m'],variables['spine_wall_m'])
        groups=[]
        for name,section,depth in [('side-left',side,variables['side_depth_m']),('spine',spine,context['centre_member_depth_m']),('side-right',side,variables['side_depth_m'])]:
            groups.append(dict(name=name,ids=[i for i in ids if any(i.startswith(name+'-'+s+'-') for s in ('lower','upper','web'))],
                expected=dict(area_m2=section['area_m2'],centroid_z_m=depth/2,inertia_vertical_bending_m4=section['inertia_m4'])))
        return dict(groups=groups,stations_m=[context['body_length_m']*.37,context['body_length_m']*.63],
            modulus_pa=material['young_modulus_pa'],density_kg_m3=material['density_kg_m3'],
            expected_mass_kg=assessment['objectives']['mass_kg'],kind=kind)
    assumptions=core.read(core.ROOT/'engineering/generative_design/data/civil-detail-space.json')['assumptions']
    basis=core.read(core.ROOT/'engineering/factory_examples/data/basis.json')['assumptions']
    section=assessment['geometry']['beam_section'];length=assessment['context_record']['span_m']
    return dict(kind=kind,groups=[dict(name='gross-concrete-beam',ids=[i for i in ids if i=='flange' or i.startswith('stem-')],
        expected=dict(area_m2=section['area_m2'],centroid_z_m=section['centroid_z_m'],inertia_vertical_bending_m4=section['inertia_x_m4']))],
        stations_m=[.37*length,.63*length],modulus_pa=assumptions['concrete_modulus_pa'],density_kg_m3=assumptions['concrete_density_kg_m3'],
        strand_metallic_area_m2=basis['strand_area_m2'],steel_density_kg_m3=basis['steel_density_kg_m3'],
        unrepresented_links_mass_kg=assessment['metrics']['added_links_mass_kg'],
        expected_mass_kg=assessment['objectives']['mass_kg']-assessment['metrics']['added_links_mass_kg'])


def compare(measured,spec):
    import math
    checks={};comparisons=[]
    for name,expected in dict(box_volume_m3=24.,box_centroid_z_m=1.5,box_inertia_yy_m5=50.).items():
        checks['native-properties-control/'+name]=math.isclose(measured['controls'][name],expected,rel_tol=1e-7,abs_tol=1e-10)
    groups={g['name']:g for g in spec['groups']}
    for sample in measured['samples']:
        for quantity,expected in groups[sample['group']]['expected'].items():
            actual=sample[quantity]
            passed=math.isclose(actual,expected,rel_tol=1e-6,abs_tol=1e-10)
            name=f"native-section/{sample['group']}/{sample['station_m']:g}/{quantity}"
            checks[name]=passed
            comparisons.append(dict(check=name,measured=actual,analytical=expected,passed=passed))
    volumes=measured['parts_volume_m3']
    if spec['kind']=='mechanical-detail':
        mass=sum(volumes.values())*spec['density_kg_m3']
    else:
        concrete=sum(v for name,v in volumes.items() if name=='flange' or name.startswith(('stem-','end-fill-')) or name in {'cap-concrete-envelope','column-concrete-envelope','footing-concrete-envelope'})
        mass=concrete*spec['density_kg_m3']+sum(measured['strand_lengths_m'].values())*spec['strand_metallic_area_m2']*(spec['steel_density_kg_m3']-spec['density_kg_m3'])
    checks['native-represented-mass-agrees']=math.isclose(mass,spec['expected_mass_kg'],rel_tol=1e-6,abs_tol=1e-7)
    inertias={sample['group']:sample['inertia_vertical_bending_m4'] for sample in measured['samples']}
    return dict(checks=checks,comparisons=comparisons,measured=measured,native_represented_mass_kg=mass,
        expected_represented_mass_kg=spec['expected_mass_kg'],native_ei_nm2=sum(inertias.values())*spec['modulus_pa'],
        unrepresented_mass_kg=spec.get('unrepresented_links_mass_kg',0.),
        scope='Native volume and prismatic section properties; mechanical EI sums individual member centroidal inertias under the existing rigid compatibility hypothesis. Civil strand metallic area is a declared material input; clearance envelopes are not metallic solids. Civil links remain an unrepresented analytical allowance.',
        accepted_materials=False,physical_release=False)
