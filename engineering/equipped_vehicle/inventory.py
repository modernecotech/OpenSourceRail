"""Disjoint equipped-car inventory and explicitly partial geometry properties.

An accounted residual is preserved as an allocation, never spread into a box to
manufacture a plausible equipped centre of gravity. New magnetic parts retain
their local properties but require an actual vehicle mounting transform.
"""
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np

from engineering.ferrite_maglev import candidate_magnetics as canonical,assembled_body
from engineering.halbach_scaling import candidates,vehicles
from . import ROOT,FLAGS
from .common import identity,sources

FRAME=dict(x='longitudinal',y='left',z='up',origin='car centre in x/y, retained floor top minus 0.300 m in z',
           handedness='right',position_unit='m',mass_unit='kg',inertia_unit='kg m²')

SYSTEMS=('body','frame-joints','doors','glazing','seating','solar','HVAC','ducting',
         'services-battery','wiring','support-cooling','protection','magnetics',
         'hardpoints','propulsion','couplers','capture-and-brake')


def combine(regions):
    """Full central tensor from each located primitive and parallel-axis shifts."""
    if not regions or len({p['id'] for p in regions})!=len(regions):raise ValueError('nonempty unique located region inventory required')
    if any(type(p['mass_kg']) not in (float,int) for p in regions):raise ValueError('ordinary numeric located masses required')
    masses=np.asarray([p['mass_kg'] for p in regions],dtype=float)
    positions=np.asarray([p['cg_m'] for p in regions],dtype=float)
    tensors=np.asarray([p['inertia_kg_m2'] for p in regions],dtype=float)
    if positions.shape!=(len(regions),3) or tensors.shape!=(len(regions),3,3) or not np.isfinite(masses).all() or not np.isfinite(positions).all() or not np.isfinite(tensors).all() or (masses<=0).any():
        raise ValueError('positive masses, located CGs and finite full tensors required')
    for matrix in tensors:
        eigen=np.linalg.eigvalsh(matrix)
        if (not np.allclose(matrix,matrix.T,atol=1e-10,rtol=1e-10) or eigen.min()<-1e-9
                or eigen[-1]>eigen[0]+eigen[1]+1e-9):
            raise ValueError('symmetric nonnegative central primitive inertia required')
    total=math.fsum(masses);cg=np.sum(masses[:,None]*positions,axis=0)/total
    delta=positions-cg
    inertia=np.sum(tensors,axis=0)+np.eye(3)*np.sum(masses*np.sum(delta*delta,axis=1))-np.einsum('n,ni,nj->ij',masses,delta,delta)
    return dict(mass_kg=float(total),cg_m=cg.tolist(),inertia_kg_m2=inertia.tolist(),region_count=len(regions),
        complete_equipped_vehicle=False,scope='Located defined material only; no unknown or allocated mass is assigned an invented distribution')


def _system(name,role=''):
    text=name+'/'+role
    if 'propulsion' in text:return 'propulsion'
    if 'glazing' in text:return 'glazing'
    if 'doors' in text:return 'doors'
    if 'protection' in text:return 'protection'
    if 'magnet' in text or 'module/' in text:return 'magnetics'
    if 'hardpoint' in text:return 'hardpoints'
    if 'frame-joint' in text or 'joint' in text:return 'frame-joints'
    return 'body'


def _functions(system,role):
    structural=system in ('body','frame-joints','hardpoints','magnetics')
    insertion={
        'body':'Locate panel/member in measured body jig; prepare bond or fastener interface before adjacent closure',
        'frame-joints':'Fit end detail with identified member ends, isolation and tool access; torque or bond in declared sequence',
        'hardpoints':'Locate magnetic hardpoint in restrained fixture; inspect complete load path before magnet installation',
        'magnetics':'Use restrained magnet cassette tooling and verify polarity; mounting transform and insertion path remain undesigned',
        'doors':'Install and adjust leaf/operator in its 1.4 × 2.1 m opening; adaptation and interlock geometry remain unqualified',
        'glazing':'Fit bonded/retained pane after frame survey; cure and retention inspection required',
        'HVAC':'Lift service package onto roof mounts; connect power, condensate and ducts after verified clearance',
        'propulsion':'Fit passive band in polarity/retention jig; inspect clearance to suspension and station motor',
        'protection':'Install independent protection assembly; segregate supply and inspect accessible restraint'}
    return dict(structural_participation=dict(intended=structural,demonstrated=None if structural else False,
        credited_in_global_model=False,basis='Intended source load path; no qualified equipped-body stiffness or attachment proof' if structural else 'Not credited to primary carbody stiffness'),
        assembly_function=dict(insertion=insertion.get(system,'Located installation sequence and interfaces remain required'),
            test='Dimensional/material identity and component functional checks; no authenticated acceptance record',
            removal='Isolate energy and support adjoining load paths; actual removal sweep and lifting tooling remain unknown',
            repair='Replacement or approved repair route requires material-specific procedure and reinspection',
            insertion_path_verified=False,removal_path_verified=False))


def _occurrence(name,mass,kind,system,*,source_id=None,geometry=None,local_geometry=None,role=''):
    if mass is not None and (type(mass) not in (float,int) or not math.isfinite(mass) or mass<0):raise ValueError('positive finite known mass or explicit unknown required')
    value=dict(id=name,source_part_id=source_id or name,system=system,evidence_class=kind,mass_kg=mass,
        occurrence_kind='material-region-or-stocked-assembly-reference',
        geometry=geometry,local_geometry=local_geometry,global_installation_location_known=geometry is not None,
        installed_location_qualified=False,material_properties_qualified=False,role=role,**_functions(system,role))
    value['occurrence_definition_id']=identity(value)
    return value


def _box(part,*,offset_z=0.):
    size=np.asarray(part['size_m'],float);at=np.asarray(part['at_m'],float)
    rho=float(part['density_kg_m3']);volume=float(np.prod(size))
    if size.shape!=(3,) or at.shape!=(3,) or min(size)<=0 or not np.isfinite(size).all() or not np.isfinite(at).all() or rho<=0:
        raise ValueError('positive finite physical box definition required')
    if not math.isclose(volume,part['volume_m3_each'],rel_tol=1e-10,abs_tol=1e-12):raise ValueError('new frame stock volume differs from located box')
    mass=volume*rho;cg=at+size/2;cg[2]+=offset_z
    tensor=np.diag(mass*(np.sum(size*size)-size*size)/12)
    return dict(id=part['id'],mass_kg=mass,cg_m=cg.tolist(),inertia_kg_m2=tensor.tolist(),
        primitive='box',size_m=size.tolist(),at_m=(at+np.array([0,0,offset_z])).tolist(),density_kg_m3=rho)


def build_inventory(body_variant,magnetic_bundle,*,root=ROOT):
    root=Path(root).resolve();before=sources(root)
    composition=vehicles.compose(body_variant,magnetic_bundle,root=root)
    base=canonical.definition();stock=json.loads((root/'engineering/ferrite_maglev/data/candidate-retained-body-stock.json').read_bytes())
    frame=body_variant['frame'];removed=set() if frame is None else set(frame['removed_stock_ids'])
    stock_ids={p['id'] for p in stock['parts']}
    if not removed<=stock_ids:raise ValueError('frame removal is not exact retained stock')
    rows=[];located=[]
    for part in stock['parts']:
        if part['id'] in removed:continue
        mass,cg,tensor=canonical._region_mass_properties(part);cg[2]-=.3
        region=dict(id='retained/'+part['id'],mass_kg=float(mass),cg_m=cg.tolist(),inertia_kg_m2=tensor.tolist(),
            primitive_source=deepcopy(part),source_coordinate_translation_m=[0.,0.,-.3])
        located.append(region);rows.append(_occurrence(region['id'],float(mass),'located-material',_system(part['id'],part['role']),
            source_id=part['id'],geometry=region,role=part['role']))
    if frame is not None:
        for part in frame['stock_parts']:
            quantity=part['quantity']
            if type(quantity) is not int or quantity<=0:raise ValueError('positive integer part occurrences required')
            for i in range(quantity):
                name='replacement-frame/'+part['id']+f'/{i:03d}'
                region=None
                if 'at_m' in part and part['kind']=='material-prism-in-one-extrusion':
                    if quantity!=1:raise ValueError('located member prism must have one occurrence')
                    region=_box(part,offset_z=-.3);region['id']=name;located.append(region)
                rows.append(_occurrence(name,part['unit_mass_kg'],'located-material' if region else 'unlocated-counted-material',
                    'body' if region else 'frame-joints',source_id=part['id'],geometry=region,role=part['kind']))
    # Existing dedicated passive-propulsion stock is retained. Its global pose
    # comes from the canonical model; compatibility with new support is held.
    for part in base['propulsion_band']['parts']:
        region=dict(id='retained/'+part['id'],mass_kg=part['mass_kg'],cg_m=deepcopy(part['cg_m']),
            inertia_kg_m2=deepcopy(part['inertia_kg_m2']),primitive_source=deepcopy(part))
        located.append(region);rows.append(_occurrence(region['id'],part['mass_kg'],'located-material','propulsion',geometry=region))
    # A local magnetic force-coupon pose is not a vehicle mounting transform.
    for module in range(24):
        for part in magnetic_bundle['stock_parts']:
            if part['group']!='train':continue
            rows.append(_occurrence(f'module/{module:02d}/'+part['id'],part['mass_kg'],'unlocated-counted-material','magnetics',
                source_id=part['id'],local_geometry=deepcopy(part),role=part['role']))
    fitout=body_variant['equipment']
    if fitout is not None:
        for part in fitout['stock_parts']:
            for i in range(part['quantity']):
                rows.append(_occurrence('fitout/'+part['id']+f'/{i:03d}',part['unit_mass_kg'],'unlocated-counted-material',
                    _system(part['id']),source_id=part['id'],local_geometry=deepcopy(part),role=part.get('kind','stock-takeoff')))
        for i in range(fitout['door']['mechanism_reference_count']):
            rows.append(_occurrence(f'door/operator-reference/{i:02d}',fitout['door']['mechanism_reference_mass_kg_each'],'supplier-reference','doors',
                source_id=fitout['door']['mechanism_source'],role='1300 mm reference operator; proposed1400 mm opening adaptation unqualified'))
    climate=body_variant['HVAC']
    if climate is not None:
        low,high=climate['package_hardware_mass_range_kg_per_car']
        if low!=high:raise ValueError('one explicit HVAC hardware mass point required; ranges need a separate scenario')
        for i in range(climate['units_per_car']):
            rows.append(_occurrence(f'HVAC/package-reference/{i:02d}',low/climate['units_per_car'],'supplier-reference','HVAC',
                source_id=climate['source_id'],role='Package hardware reference only; mounting, ducts and actual equipment mass unresolved'))
    protection=json.loads((root/'engineering/ferrite_maglev/data/candidate-protection-equipment.json').read_bytes())
    for part in protection['rows']:
        for i in range(part['quantity_per_car']):
            rows.append(_occurrence(part['id']+f'/{i:02d}',part['unit_mass_kg'],'located-envelope-allocation','protection',
                source_id=part['id'],local_geometry=dict(proposed_centre_m=part['positions_m'][i],envelope_m=part['envelope_m']),
                role='Allocated equipment and proposed envelope, not solid material or measured unit distribution'))
    removed_alloc=sum(change['removed_kg_per_car'] for change in body_variant['replacement_changes'] if change['removal_kind']=='inherited-allocation')
    residual=base['mass_accounting']['retained_unlocated_allocation_kg']-removed_alloc
    if residual<0:raise ValueError('negative residual allocation cannot provide an equipment mass saving')
    rows.append(_occurrence('retained/unlocated-equipment-residual',residual,'unlocated-allocation','body',
        role='Inherited residual includes unlocated services/interior/cooling/electronics and contingency; no invented uniform density'))
    # Required domains remain explicit, without adding their unknown mass to
    # an inherited allocation a second time or treating it as known hardware.
    missing=[]
    for system in SYSTEMS:
        reasons={
            'body':'Global shell, aperture reinforcement, joints, bracing, fatigue, crash and material correlation unresolved',
            'frame-joints':'New end details/bolts/isolation lack actual assembly poses, load transfer, torque and access proof',
            'doors':'Complete 1400×2100 mechanism, seals, guides, interlocks, emergency operation and insertion/removal geometry incomplete',
            'glazing':'Complete pane/frame/coating retention, impact/fire proof and installed positions incomplete',
            'seating':'Seat geometry, fixings, passenger-restraint loads and replacement operations not defined',
            'solar':'Flush roof panels, mounts, wiring, thermal movement and maintenance path not defined',
            'HVAC':'Actual50°C duty, five-unit roof fit, derating, electrical input, mounts, fan heat and redundancy unresolved',
            'ducting':'Occupied ventilation, ducts, diffusers, insulation and condensate routes missing',
            'services-battery':'Essential service storage geometry, restraint, isolation and emergency endurance unclosed',
            'wiring':'Harness routes, connectors, segregation, protection and installation stock unclosed',
            'support-cooling':'Coil insulation, actual thermal paths, cooling, protection and leadout stock unclosed',
            'protection':'Protection references/envelopes are allocated, with no calibrated installed material/inertia proof',
            'magnetics':'Component local geometry lacks a compatible global mounting transform, assembly fit and retained magnet force/fault map',
            'hardpoints':'Existing hardpoints/carriers retained; reaction moments, larger-array loads, local geometry and global fit unqualified',
            'propulsion':'Retained band requires same-candidate overlap, demagnetisation, drag/loss and retention compatibility',
            'couplers':'Inter-car coupler/articulation and rescue loads lack complete installed geometry',
            'capture-and-brake':'Capture, parking, emergency brake/contact loads and equipment geometry unclosed'}
        missing.append(dict(id='unclosed/'+system,system=system,mass_kg=None,geometry=None,reason=reasons[system],
            mass_accounting='May overlap retained allocations; no separate additive mass or zero credit assigned',**_functions(system,'unclosed')))
    ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate physical occurrence in equipped inventory')
    known=math.fsum(r['mass_kg'] for r in rows)
    if not math.isclose(known,composition['comparison_empty_kg_per_car'],abs_tol=1e-7):raise ValueError('disjoint equipped inventory does not reconcile to selected comparison mass')
    partial=combine(located);categories={}
    for row in rows:categories[row['evidence_class']]=categories.get(row['evidence_class'],0.)+row['mass_kg']
    system_coverage=[dict(system=system,known_occurrences=sum(r['system']==system for r in rows),
        accounted_known_mass_kg=math.fsum(r['mass_kg'] for r in rows if r['system']==system),
        complete_installed_inventory=False,global_location_complete=False,physical_qualified=False) for system in SYSTEMS]
    value=dict(schema='osr-equipped-vehicle-inventory/1',composition_id=composition['candidate_id'],
        body_candidate_id=body_variant['candidate_id'],magnet_component_id=magnetic_bundle['physical_id'],
        source_canonical_configuration_id=base['configuration_sha256'],body_name=body_variant['name'],magnetic_recipe_id=magnetic_bundle['recipe_id'],
        service=deepcopy(body_variant['service']),coordinate_frame=FRAME,occurrences=rows,missing_inventory=missing,
        located_material_properties=partial,accounted_mass_by_evidence_class_kg=categories,
        comparison_empty_kg_per_car=known,comparison_aw3_kg_per_car=known+12000.,
        comparison_mass_reconciles=True,located_share_of_accounted_comparison=partial['mass_kg']/known,
        installed_empty_kg_per_car=None,installed_aw3_kg_per_car=None,cg_m=None,inertia_kg_m2=None,modal_model=None,
        global_structural_model=None,system_coverage=system_coverage,
        structural_member_sensitivity=deepcopy(composition['support_requirements_by_unclosed_mass']),
        assembly_definition_id=identity(dict(composition_id=composition['candidate_id'],occurrences=rows,missing_inventory=missing,frame=FRAME)),
        readiness=dict(mass='unknown',structure='unknown',modal_import='unknown',native_equipped_assembly='unknown',
            reason='Source-bound located material is partial; supplier references, allocations, unlocated stock and missing equipment prevent complete equipped mass/CG/inertia'),
        source_sha256=before,scope='Disjoint inventory projection of the selected composition. Occurrence counts include material regions and stocked assemblies, not manufacturing operation counts. Native-equipment placement and a globally coupled assembly are not established',**FLAGS)
    value['evaluation_id']=identity(value)
    if sources(root)!=before:raise ValueError('equipped inventory sources changed')
    return value


def validate_inventory(value,body_variant,magnetic_bundle,*,root=ROOT):
    expected=build_inventory(body_variant,magnetic_bundle,root=root)
    if value!=expected:raise ValueError('equipped inventory geometry, mass, identity, source or disposition differs')
    return value


def gfrp_design_space():
    """A separately identified old native seed, never mixed into a new car."""
    definition=assembled_body.definition();parts=definition['parts']
    return dict(schema='osr-gfrp-equipped-design-space/1',
        seed_geometry_id=identity(parts),seed_definition_id=identity(definition),
        compatible_with_selected_halbach_composition=False,selected_composition_id=None,
        seed_scope='Retained assembledGFRP structural/cartridge geometry; not an equipped monocoque or newHalbach assembly',
        variables=[dict(id='regional-facing-plies',regions=['floor','roof','side','end'],ply_count=[3,4,5],ply_thickness_m=.0006,
                        orientations_deg=[0,90,45,-45],material_certified=False),
                   dict(id='regional-core-thickness',range_m=[.03,.07],density_grade_kg_m3=[80,100],material_certified=False),
                   dict(id='aperture-and-hardpoint-joints',alternatives=['bonded','bolted','bonded-and-bolted'],qualified=False)],
        fixed_interfaces=dict(length_m=17.,passenger_payload_aw3_kg=12000.,normal_passengers=120,doors=4,door_opening_m=[1.4,2.1]),
        required_regeneration=['all regional face/core geometry and compatible joints','opening-frame and retained mount clearances',
            'complete equipment stock with mass/CG/inertia','native mesh, laminate orientations, local supports and load paths',
            'prestressed modes for empty/AW3/asymmetric conditions','buckling, fatigue, thermal/wet/fire and crash evidence'],
        sampled_candidates=[],complete_installed_mass_kg=None,modal_model=None,**FLAGS)


def study(root=ROOT):
    root=Path(root).resolve();mags=candidates.candidates(root);bodies=vehicles.variants(root)
    pairs=[('6082-six-cell-deep-40kn/','HS-V012-W40-H8-P1-Y00-D'),
           ('6082-six-cell-deep-70kn/','HS-V012-W40-H8-P2-Y00-U')]
    rows=[build_inventory(next(b for b in bodies if b['name'].startswith(body)),next(m for m in mags if m['recipe_id']==mag),root=root)
          for body,mag in pairs]
    value=dict(schema='osr-equipped-vehicle-study/1',inventories=rows,gfrp_design_space=gfrp_design_space(),source_sha256=sources(root),**FLAGS)
    value['study_id']=identity(value);return value
