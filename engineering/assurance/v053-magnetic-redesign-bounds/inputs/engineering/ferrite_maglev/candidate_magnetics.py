"""Dimensioned, two-circuit PM magnetic candidate; unqualified research maps.

Three physical coils: one shared-stem lift winding and two series-opposed
return-leg guidance windings. Each useful branch crosses a vertical lift gap
and a horizontal guidance gap through a stationary L-shaped reaction rail.
The shared stem and independent permanent-magnet branches couple both circuits.
The convex reluctance network is not a measured map or a 3-D field solution.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('candidate-magnetics.toml')
DATA=Path(__file__).with_name('data')
PARENT=DATA/'candidate-parent-94ad.json'
REPLACED=DATA/'candidate-replaced-cartridges.json'
RETAINED=DATA/'candidate-retained-body-stock.json'
PROTECTION=DATA/'candidate-protection-equipment.json'
ATTACHMENT=DATA/'candidate-attachment-equipment.json'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_magnetics.py'
SCHEMA='osr-candidate-magnetics/1'
MU0=4e-7*math.pi
FLAGS=dict(design_complete=False,physical_validation=False,manufacturing_release=False,
           physical_release=False,physical_output_authorised=False,engineering_accepted=False)


def encoded(value):
    def convert(obj):
        if isinstance(obj,np.generic):return obj.item()
        if isinstance(obj,np.ndarray):return obj.tolist()
        raise TypeError('non-JSON magnetic evidence value: '+type(obj).__name__)
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False,default=convert)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def source_paths():return [Path(__file__),INPUT,PARENT,REPLACED,RETAINED,PROTECTION,ATTACHMENT,TEST]
def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-candidate-magnetics/1' or len(a['variants'])<3:raise ValueError('three explicit magnetic variants required')
    if len({v['id'] for v in a['variants']})!=len(a['variants']):raise ValueError('unique variant identities required')
    for v in a['variants']:
        if any(type(v[k]) not in (int,float) or not math.isfinite(v[k]) or v[k]<=0 for k in ('turns_lift','turns_guide','copper_lift_mm2','copper_guide_mm2','pm_length_m','core_scale')):raise ValueError('finite positive winding/core geometry required')
    return a


def _variant(a,identity):
    return next(v for v in a['variants'] if v['id']==(identity or a['selected_variant']))


def _box(identity,size,at,material,density,scope,**extra):
    sz=np.asarray(size,float);pos=np.asarray(at,float);mass=float(np.prod(sz)*density)
    return dict(id=identity,kind='box',size_m=sz.tolist(),at_m=pos.tolist(),material=material,
        volume_m3=float(np.prod(sz)),mass_kg=mass,cg_m=(pos+sz/2).tolist(),
        inertia_kg_m2=np.diag(mass/12*np.array([sz[1]**2+sz[2]**2,sz[0]**2+sz[2]**2,sz[0]**2+sz[1]**2])).tolist(),
        component_scope=scope,**extra)


def _coil(identity,inner,outer,height,turns,area_mm2,z,centre_y,a):
    # Four disjoint rectangular packs; copper fill is computed, not envelope mass.
    mean=inner[0]+inner[1]+outer[0]+outer[1]
    length=turns*mean;volume=length*area_mm2*1e-6
    pack_volume=(np.prod(outer)-np.prod(inner))*height
    density=a['materials']['copper']['density_kg_m3']*volume/pack_volume
    at=[-outer[0]/2,centre_y-outer[1]/2,z]
    rings=[];tx=(outer[0]-inner[0])/2;ty=(outer[1]-inner[1])/2
    for s in (-1,1):
        rings.append(_box(identity+f'/x-{s}',[tx,outer[1],height],
            [at[0] if s<0 else inner[0]/2,at[1],z],'copper-pack',density,'new-winding'))
        rings.append(_box(identity+f'/y-{s}',[inner[0],ty,height],
            [-inner[0]/2,at[1] if s<0 else centre_y+inner[1]/2,z],'copper-pack',density,'new-winding'))
    return dict(id=identity,turns=turns,conductor_area_mm2=area_mm2,inner_m=inner,outer_m=outer,
        height_m=height,mean_turn_length_m=mean,conductor_length_m=length,copper_volume_m3=volume,
        copper_mass_kg=volume*a['materials']['copper']['density_kg_m3'],fill_fraction=volume/pack_volume,
        insulation_m=a['coil_insulation_m'],parts=rings)


def _module(a,v):
    # YZ-plane magnetic topology extruded in x. All adjacent core stock is
    # disjoint; shoulders provide real connected changes in flux cross section.
    s=v['core_scale'];x=.16*s;rho=a['materials']['steel']['density_kg_m3']*a['stack_fill']
    parts=[]
    def core(key,size,at):parts.append(_box(key,size,at,'M400-50A-stack',rho,'new-core',lamination_plane='yz',stack_axis='x'))
    stem_bottom=-.19-v['pm_length_m']
    core('core/shared-stem',[x,.16,.08-stem_bottom],[-x/2,-.08,stem_bottom])
    core('core/top-fork',[x,.40,.08],[-x/2,-.20,.08])
    core('core/bottom-return',[.32*s,.80,.04],[-.16*s,-.40,-.29-v['pm_length_m']+.06])
    # Bottom face follows PM thickness without overlapping the shared stem.
    for side in (-1,1):
        yc=.30*side
        core(f'core/lift-pole-{side}',[x,.10,.04],[-x/2,side*.15-.05,.16])
        core(f'core/return-leg-{side}',[x,.08,.08],[-x/2,yc-.04,-.08])
        # Horizontal guidance pole and the outer return remain separate from
        # the upper fork: 60mm of actual air between their inner edges.
        core(f'core/guide-pole-{side}',[x,.14,.10],[-x/2,.26 if side>0 else -.40,0.])
        for k,(xx,yy,zz,z0) in enumerate(((.32*s,.20,.04,-.19),(.24*s,.14,.04,-.15),(x,.08,.03,-.11))):
            core(f'core/pm-spreader-{side}-{k}',[xx,yy,zz],[-xx/2,yc-yy/2,z0])
        pmz=-.19-v['pm_length_m']
        parts.append(_box(f'ferrite/bank-{side}',[.32*s,.20,v['pm_length_m']],[-.16*s,yc-.10,pmz],
            'TDK-FB9B',a['materials']['ferrite']['density_kg_m3'],'new-ferrite',magnetization_axis='z',
            magnetization_direction=-1,block_cut_plan=dict(x_count=4,y_count=4,blocks=16,individual_m=[.08*s,.05,v['pm_length_m']])))
    # Main coil clears central stem by10mm in x/y. Guidance coils clear their
    # return legs by10mm. Height is axial winding length, not face aperture.
    main=_coil('winding/lift',[x+.02,.18],[x+.12,.28],.12,v['turns_lift'],v['copper_lift_mm2'],-.16,0,a)
    guides=[_coil(f'winding/guide-{side}',[x+.02,.10],[x+.10,.18],.075,v['turns_guide'],v['copper_guide_mm2'],-.08,.30*side,a) for side in (-1,1)]
    # Guidance coil protrudes to z=-5mm, below pole base0; does not occupy pole.
    coils=[main,*guides]
    for c in coils:parts.extend(c['parts'])
    # Concrete interface allocations are replaced by real counted hardware;
    # existing parent cooling/mount/electronics allowances remain conservative.
    parts.append(_box('cooling/aluminium-coldplate',[.90,.80,.008],[-.45,-.40,-.38],
        'aluminium',2700.,'new-cooling',coolant_channels_qualified=False))
    ix=x+.01;iy=.17
    for side in (-1,1):
        parts.append(_box(f'insulation/coil-support-x-{side}',[(.40-ix)/2,.36,.006],
            [-.20 if side<0 else ix/2,-.18,-.175],'glass-epoxy',1900.,'new-insulation'))
        parts.append(_box(f'insulation/coil-support-y-{side}',[ix,(.36-iy)/2,.006],
            [-ix/2,-.18 if side<0 else iy/2,-.175],'glass-epoxy',1900.,'new-insulation'))
    for side in (-1,1):
        parts.append(_box(f'connector/isolated-{side}',[.10,.06,.05],[.32,.34*side-.03,-.05],
            'connector-allocation',1600.,'new-connectors',rated_current_a=120.,origin_confirmed=False))
    parts.append(_box('housing/nonmagnetic-cover',[.90,.80,.002],[-.45,-.40,-.372],
        'aluminium',2700.,'new-housing'))
    # Two real50mm square rod penetrations,5mm clear of40mm RHS, cut from
    # both plate and cover. Disjoint material boxes retain actual net mass.
    cut=[]
    for part in parts:
        if part['id'] not in {'cooling/aluminium-coldplate','housing/nonmagnetic-cover'}:cut.append(part);continue
        xs=[-.45,-.425,-.375,.375,.425,.45];ys=[-.40,-.025,.025,.40]
        for j in range(len(xs)-1):
            for k in range(len(ys)-1):
                if j in (1,3) and k==1:continue
                cut.append(_box(part['id']+f'/region-{j}-{k}',[xs[j+1]-xs[j],ys[k+1]-ys[k],part['size_m'][2]],
                    [xs[j],ys[k],part['at_m'][2]],part['material'],2700.,part['component_scope'],
                    rod_passage_m=.05,passage_seal_and_cooling_channels_qualified=False))
    parts=cut
    parts.append(_box('assembly/bolts-and-clamps',[.12,.08,.06],[.15,.42,-.18],
        'steel-fastener-equivalent',7850.,'new-fasteners',equivalent_box=True,fasteners=16,thread='M8'))
    parts.append(_box('cooling/dielectric-fluid-manifold',[.40,.20,.025],[-.20,-.10,-.35],
        'fluid-and-manifold-allocation',1400.,'new-cooling',fluid_volume_m3=.002,service_loop_mass_included=True))
    attachment=json.loads(ATTACHMENT.read_text())
    if attachment['module_mount_z_m']!=a['module_mount_z_m']:raise ValueError('exact shared lowered attachment datum required')
    parts.extend(deepcopy(attachment['parts']))
    # Length and area of every network element are tied to the above stock.
    common=[dict(id='core/shared-stem',length_m=.27+v['pm_length_m'],area_m2=x*.16)]
    branch=[dict(id='core/top-fork-half',length_m=.15,area_m2=x*.08),
        dict(id='core/bottom-return-half',length_m=.30,area_m2=.32*s*.04),
        dict(id='core/return-leg',length_m=.08,area_m2=x*.08),
        dict(id='core/guide-pole',length_m=.10,area_m2=x*.10),
        dict(id='core/lift-pole',length_m=.04,area_m2=x*.10),
        *[dict(id=f'core/pm-spreader-{k}',length_m=l,area_m2=area) for k,(l,area) in enumerate(((.04,.32*s*.20),(.04,.24*s*.14),(.03,x*.08)))]]
    return dict(parts=parts,coils=coils,mass_kg=sum(p['mass_kg'] for p in parts),
        lift_pole_area_m2=x*.10,guide_pole_area_m2=x*.10,pole_half_spacing_m=.15,
        guide_pole_half_spacing_m=.40,lift_force_z_m=.20,guide_force_z_m=.05,
        core_paths=dict(common=common,branch=branch,stationary_return=[dict(id='stationary/flange-entry',length_m=.0125,area_m2=x*.10),dict(id='stationary/flange-run',length_m=.2705,area_m2=x*.025),dict(id='stationary/web-run',length_m=.1705,area_m2=x*.025),dict(id='stationary/guide-exit',length_m=.0125,area_m2=x*.10)]),
        permanent_magnet=dict(area_m2=.32*s*.20,length_m=v['pm_length_m'],branches=2),
        stationary_return_rail=dict(count_per_module_slice=2,section_m=[.12,.24],wall_m=.025,extrusion_m=x,
            scope='L-shaped reaction-rail geometry/interface required; not vehicle mass. Continuous guideway mass, joints and local cross-field behavior require independent design.'),
        electrical_topology=dict(circuits=2,physical_coils=3,lift='one coil links sum of both branch fluxes',
            guidance='two series-opposed return-leg coils link difference of branch fluxes',
            useful_flux_path='shared stem -> top fork -> vertical lift gap -> stationary L rail -> horizontal guide gap -> return leg -> PM bank -> bottom return -> shared stem',
            winding_connection_test_required=True),
        nominal_internal_clearance_m=.005,
        leakage=dict(path_length_m=.06,path_area_m2=x*.02,basis='Actual60mm fork-end to return-pole clearance;20mm facing vertical overlap.3D end leakage and cornerfringing remain unqualified.'),
        cooling=dict(method='enamelled winding flooded with isolated dielectric fluid',fluid_volume_m3=.002,fluid_density_kg_m3=850.,
            fluid_specific_heat_j_kg_k=1800.,parallel_passages=10,flow_kg_s=.05,pressure_drop_pa=60000.,pump_efficiency=.4,
            assumed_fluid_film_w_m2_k=250.,wetted_fraction=.5,enamel_thickness_m=.00015,enamel_conductivity_w_m_k=.2,
            thermal_conductance_w_k=v['cooling_w_k'],qualified=False,hold='Dielectric fluid compatibility, exact channels, heat exchanger/pump routing and tested thermal conductance required.'),
        geometry_holds=['Complete3D lamination joint insulation/fringing requires native interference and field verification.',
            'Guide-coil axial height75mm overlaps available80mm leg with5mm axial total margin; support/tolerance stack and coldplate routing unqualified.',
            'The common lift coil needs a split/bobbin assembly before yoke closure; PM assembly needs a restrained fixture.',
            'Cooling channels,120A connector derating, clamp fasteners and dielectric tolerances are allocated, not production drawings.'])


def _region_mass_properties(p):
    """Integrate signed zeroth/first/raw-second volume moments of actual cuts."""
    if 'cg_m' in p and 'inertia_kg_m2' in p:
        return p['mass_kg'],np.array(p['cg_m']),np.array(p['inertia_kg_m2'])
    size=np.array(p['size_m'],float);at=np.array(p['at_m'],float);pieces=[]
    def cylinder(d,length,start,axis):
        volume=math.pi*(d/2)**2*length;centre=np.array(start,float);centre[axis]+=length/2
        covariance=np.full(3,(d/2)**2/4);covariance[axis]=length*length/12
        return volume,centre,np.diag(covariance)
    if p.get('kind')=='cylinder':
        axis='xyz'.index(p.get('cylinder_axis','z'));start=at.copy()
        for k in range(3):
            if k!=axis:start[k]+=size[0]/2
        pieces.append((1,cylinder(size[0],size[2],start,axis)))
    else:pieces.append((1,(float(np.prod(size)),at+size/2,np.diag(size*size/12))))
    for h in p.get('holes',[]):
        axis='xyz'.index(h.get('axis','z'));start=at.copy()
        for k in range(3):start[k]+=h.get('start_m',0.) if k==axis else h['xyz'[k]+'_m']
        length=h.get('length_m',size[axis] if p.get('kind')!='cylinder' else size[2])
        pieces.append((-1,cylinder(h['diameter_m'],length,start,axis)))
    volume=sum(sign*item[0] for sign,item in pieces)
    if not math.isclose(volume,p['volume_m3'],rel_tol=1e-9,abs_tol=1e-12):raise ValueError('signed stock volume differs from exact snapshot')
    cg=sum(sign*vol*c for sign,(vol,c,cov) in pieces)/volume
    raw=sum(sign*vol*(cov+np.outer(c,c)) for sign,(vol,c,cov) in pieces)
    centred=raw-volume*np.outer(cg,cg);rho=p['density_assumption_kg_m3']
    inertia=rho*(np.trace(centred)*np.eye(3)-centred)
    return volume*rho,cg,inertia


def _combine(regions):
    total=sum(r['mass_kg'] for r in regions);cg=sum(r['mass_kg']*np.array(r['cg_m']) for r in regions)/total
    inertia=np.zeros((3,3))
    for r in regions:
        d=np.array(r['cg_m'])-cg
        inertia+=np.array(r['inertia_kg_m2'])+r['mass_kg']*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    return dict(mass_kg=total,cg_m=cg.tolist(),inertia_kg_m2=inertia.tolist(),roll_kg_m2=float(inertia[0,0]),
        pitch_kg_m2=float(inertia[1,1]),yaw_kg_m2=float(inertia[2,2]),regions=regions,
        complete_installed_distribution=False,scope='Exact signed stock box/cylinder/void integrals and actual added magnetic boxes/packs. Residual equipment/passenger placement is declared allocation, not surveyed equipment layout.')


def _bom(a,m):
    rows=[];prices=a['procurement']
    for p in m['parts']:
        mat=p['material'];rate=prices['steel_usd_kg'];waste=prices['core_waste_fraction'];process='cut,coat,stack,insulate,clamp; measured stack joint and magnetic QA required'
        if mat=='TDK-FB9B':rate=prices['ferrite_usd_kg'];waste=prices['ferrite_waste_fraction'];process='16 individually magnetized blocks/bank; restrained fixture and polarity/flux inspection'
        elif mat=='copper-pack':rate=prices['copper_usd_kg'];waste=prices['copper_waste_fraction'];process='rectangular enamelled conductor, wound bobbin, impregnation and hipot'
        elif mat in {'aluminium','glass-epoxy'}:rate=prices['aluminium_usd_kg'];waste=.10;process='cut,machine,deburr; leak/dielectric QA as applicable'
        purchase=p['mass_kg']/(1-waste)
        rows.append(dict(id=p['id'],component_scope=p['component_scope'],quantity_per_module=1,quantity_per_car=24,
            unit='kg',net_material_quantity=p['mass_kg'],purchase_quantity=purchase,waste_fraction=waste,
            unit_rate_usd=rate,extended_cost_usd=purchase*rate,mass_kg=p['mass_kg'],geometry_part_ids=[p['id']],
            process=process,lead_time_days=prices['lead_time_days'],origin_basis=prices['origin_basis'],
            tolerance=dict(drawing_tolerance_m=None,stack_fill=a['stack_fill'] if mat=='M400-50A-stack' else None),
            qa_requirements=['approved dimensional/tolerance drawing','material certificate and serial/batch trace','independent acceptance unexecuted']))
    rows.append(dict(id='process/core-cut-and-stack',component_scope='new-core',quantity_per_module=1,quantity_per_car=24,
        unit='kg-processed',net_material_quantity=sum(p['mass_kg'] for p in m['parts'] if p['component_scope']=='new-core'),
        purchase_quantity=sum(p['mass_kg'] for p in m['parts'] if p['component_scope']=='new-core'),waste_fraction=0.,
        unit_rate_usd=prices['lamination_process_usd_kg'],extended_cost_usd=sum(p['mass_kg'] for p in m['parts'] if p['component_scope']=='new-core')*prices['lamination_process_usd_kg'],
        mass_kg=0.,geometry_part_ids=[p['id'] for p in m['parts'] if p['component_scope']=='new-core'],process='UK custom lamination cut/stack planning allowance',
        lead_time_days=60,origin_basis=prices['uk_core_supplier'],tolerance=None,qa_requirements=['supplier quotation','cut-edge magnetic loss','joint reluctance']))
    for c in m['coils']:
        rows.append(dict(id='process/'+c['id'],component_scope='new-winding',quantity_per_module=1,quantity_per_car=24,unit='coil',net_material_quantity=1,purchase_quantity=1,waste_fraction=0.,unit_rate_usd=prices['winding_process_usd_coil'],extended_cost_usd=prices['winding_process_usd_coil'],mass_kg=0.,geometry_part_ids=[p['id'] for p in c['parts']],process='UK wound-component planning allowance',lead_time_days=60,origin_basis=prices['uk_winding_supplier'],tolerance=None,qa_requirements=['resistance/turn/polarity test','hipot and thermal cycling','quotation']))
    return rows


def definition(variant_id=None):
    a=load();v=_variant(a,variant_id);m=_module(a,v)
    band=_propulsion_band(a)
    parent=json.loads(PARENT.read_text())['configuration'];replaced=json.loads(REPLACED.read_text());retained=json.loads(RETAINED.read_text());protection=json.loads(PROTECTION.read_text())
    removed_cu=parent['magnetic']['winding_copper_kg_per_car'];old_removed=replaced['mass_kg_per_car']+removed_cu
    remainder=parent['controlled_tare_kg']-old_removed-retained['mass_kg_per_car']
    if remainder<0:raise ValueError('retained parent stock exceeds retained tare; no negative allocation credit')
    positions=[[float(x),float(y),a['module_mount_z_m']] for y in (-.88,.88) for x in np.arange(-5.5,6.,1.)]
    regions=[]
    for p in retained['parts']:
        mass,cg,I=_region_mass_properties(p);cg[2]-=.3;regions.append(dict(id='retained/'+p['id'],mass_kg=mass,cg_m=cg.tolist(),inertia_kg_m2=I.tolist(),basis='signed exact box/cylinder/void integral at retained floor datum minus0.3m'))
    for i,pos in enumerate(positions):
        for p in m['parts']:
            regions.append(dict(id=f'module/{i:02d}/'+p['id'],mass_kg=p['mass_kg'],cg_m=(np.array(pos)+p['cg_m']).tolist(),inertia_kg_m2=p['inertia_kg_m2'],basis='new dimensioned stock'))
    for p in band['parts']:
        regions.append(dict(id=p['id'],mass_kg=p['mass_kg'],cg_m=p['cg_m'],inertia_kg_m2=p['inertia_kg_m2'],basis='actual dedicated passive propulsion-band stock'))
    allocation=_box('retained/unlocated-equipment-allocation',[17.,2.65,2.5],[-8.5,-1.325,-.25], 'allocation',remainder/(17*2.65*2.5),'retained-allocation')
    regions.append(dict(id=allocation['id'],mass_kg=remainder,cg_m=allocation['cg_m'],inertia_kg_m2=allocation['inertia_kg_m2'],basis='retained tare residual; placement assumed and CG sensitivity remains open'))
    for row in protection['rows']:
        for i,pos in enumerate(row['positions_m']):
            p=_box(row['id']+f'/{i}',row['envelope_m'],np.array(pos)-np.array(row['envelope_m'])/2,'allocation',row['unit_mass_kg']/np.prod(row['envelope_m']),'protection')
            regions.append(dict(id=p['id'],mass_kg=p['mass_kg'],cg_m=p['cg_m'],inertia_kg_m2=p['inertia_kg_m2'],basis='supplemental allocated equipment; ratings unqualified'))
    passengers=_box('passengers/aw3',[17.,2.65,1.2],[-8.5,-1.325,.7], 'passenger-allocation',a['passenger_payload_kg']/(17*2.65*1.2),'payload')
    regions.append(dict(id=passengers['id'],mass_kg=passengers['mass_kg'],cg_m=passengers['cg_m'],inertia_kg_m2=passengers['inertia_kg_m2'],basis='uniform passenger allocation; crowd distribution sensitivity open'))
    props=_combine(regions);supplemental=sum(r['unit_mass_kg']*r['quantity_per_car'] for r in protection['rows']);tare=parent['controlled_tare_kg']-old_removed+24*m['mass_kg']+supplemental+band['mass_kg']
    if not math.isclose(props['mass_kg'],tare+a['passenger_payload_kg'],abs_tol=1e-6):raise ValueError('common candidate mass ledger does not close')
    identity=dict(schema=a['schema'],revision=a['revision'],variant=v,parent_configuration_sha256=parent['configuration_sha256'],inputs_sha256={p.name:digest(p) for p in (INPUT,PARENT,REPLACED,RETAINED,PROTECTION,ATTACHMENT)},module=m,propulsion_band=band,module_placements_m=positions)
    cfg=sha256(encoded(identity)).hexdigest()
    return dict(schema=a['schema'],id='OSR-DIMENSIONED-MAGNETICS/'+v['id'],revision=a['revision'],variant_id=v['id'],configuration_sha256=cfg,
        parent_configuration_sha256=parent['configuration_sha256'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),INPUT,PARENT,REPLACED,RETAINED,PROTECTION,ATTACHMENT)},cars=6,
        controlled_tare_kg=tare,controlled_aw3_kg=tare+a['passenger_payload_kg'],passenger_payload_kg=a['passenger_payload_kg'],
        mass_accounting=dict(parent_tare_kg=parent['controlled_tare_kg'],retained_parent_tare_kg=parent['controlled_tare_kg']-old_removed,
            removed_defined_components=[dict(id='retained/cartridges-528',mass_kg_per_car=replaced['mass_kg_per_car'],source=REPLACED.relative_to(ROOT).as_posix(),part_ids=[p['id'] for p in replaced['parts']]),dict(id='retained/three-coil-winding-copper',mass_kg_per_car=removed_cu,source=PARENT.relative_to(ROOT).as_posix())],
            added_defined_components=[dict(id='new/dimensioned-magnetic-module',quantity_per_car=24,mass_kg_each=m['mass_kg'],mass_kg_per_car=24*m['mass_kg']),dict(id='new/protection-equipment',mass_kg_per_car=supplemental,source=PROTECTION.relative_to(ROOT).as_posix()),dict(id='new/passive-propulsion-band',mass_kg_per_car=band['mass_kg'])],
            retained_actual_stock_kg=retained['mass_kg_per_car'],retained_unlocated_allocation_kg=remainder,residual_ferrite_allocation_kg=3000-replaced['ferrite_mass_kg_per_car'],
            basis='Only exact528oldcartridge stock and full prior physical3coil copper removed; all carriers, hardpoints, residual ferrite, cooling/mount/electronics and contingency remain counted.'),
        mass_properties=props,mass_properties_per_car=props,module=m,propulsion_band=band,module_placements_m=positions,
        module_placements=[dict(id=f'module/{i:02d}',centre_m=p,rotation_matrix=np.eye(3).tolist(),axes=dict(x='longitudinal',y='left',z='up')) for i,p in enumerate(positions)],
        circuits=dict(copper_mass_kg=[m['coils'][0]['copper_mass_kg'],sum(c['copper_mass_kg'] for c in m['coils'][1:])],thermal_conductance_w_k=v['cooling_w_k'],current_limit_a=a['current_limit_a'],
            thermal_specific_heat_j_kg_k=a['materials']['copper']['specific_heat_j_kg_k'],continuous_current_density_a_mm2=a['continuous_current_density_a_mm2']),
        pole_half_spacing_m=.15,nominal_gap_m=a['nominal_gap_m'],protection_equipment_sha256=digest(PROTECTION),
        force_convention=dict(upward='world +z',leftward='world +y',gap_order=['lift_left','lift_right','guide_left','guide_right'],
            positive_y='closes guide-left; opens guide-right',positive_z='closes both lift gaps',local_force_points_m=[[-0.,.15,.20],[0.,-.15,.20],[0.,.40,.05],[0.,-.40,.05]]),
        manufacturing_bom=_bom(a,m)+_band_bom(a,band),variants=[x['id'] for x in a['variants']],
        holds=['Nonlinear reluctance map uses a typical50Hz steel curve as a reversible DC proxy; measured3D force/linkage/loss/demag maps remain required.',
            'Corrected stationary return path uses actual25mmweb/flange cross-section, not100mmpole-face width. Requested AW3 support may be infeasible; vehicleANDrail BH saturation must both pass.',
            'Allocated cooling, retained equipment positions, joint flux gaps, dielectric design, tolerances and supplier quotes are not qualified.',
            'Retained stock dimensions/holes are integrated exactly; unlocated equipment and crowd placements remain assumptions. Full equipped native CG/inertia is not accepted.',
            *m['geometry_holds']],**FLAGS)


@lru_cache(maxsize=8)
def _context(variant_id,input_hash):
    a=load();v=_variant(a,variant_id);m=_module(a,v);steel=a['materials']['steel']
    H=np.array(steel['h_a_m']);B=np.array(steel['j_t'])+MU0*H
    slopes=np.diff(H)/np.diff(B);integral=np.r_[0.,np.cumsum((H[1:]+H[:-1])/2*np.diff(B))]
    return a,v,m,H,B,slopes,integral


@lru_cache(maxsize=8)
def _runtime_cached(variant_id,mtime_ns,size):
    return _context(variant_id,digest(INPUT))


def _runtime(variant_id):
    st=INPUT.stat()
    return _runtime_cached(variant_id,st.st_mtime_ns,st.st_size)


def _steel(phi,paths,context):
    a,v,m,H,B,slopes,integral=context
    mmf=np.zeros_like(phi);dmmf=np.zeros_like(phi);energy=np.zeros_like(phi);peak=np.zeros_like(phi)
    for p in paths:
        area=p['area_m2']*a['stack_fill'];b=phi/area;ab=np.abs(b);idx=np.clip(np.searchsorted(B,ab,side='right')-1,0,len(slopes)-1)
        # Beyond published last point, incremental permeability is vacuum.
        high=ab>B[-1];slope=np.where(high,1/MU0,slopes[idx]);baseb=np.where(high,B[-1],B[idx]);baseh=np.where(high,H[-1],H[idx]);baseu=np.where(high,integral[-1],integral[idx]);delta=ab-baseb
        h=baseh+slope*delta;u=baseu+baseh*delta+.5*slope*delta*delta
        mmf+=p['length_m']*np.sign(b)*h;dmmf+=p['length_m']/area*slope;energy+=p['length_m']*area*u;peak=np.maximum(peak,ab)
    return mmf,dmmf,energy,peak


def _solve(gaps,cur,T,context,initial=None,pm_enabled=True):
    a,v,m,*_=context;n=len(gaps);C=np.array([[v['turns_lift']]*4,[v['turns_guide'],-v['turns_guide'],v['turns_guide'],-v['turns_guide']]],float)
    # q=[useful_left,useful_right,leak_left,leak_right].
    M=np.array([[1,0,1,0],[0,1,0,1]],float);common=np.ones(4)
    pm=m['permanent_magnet'];f=a['materials']['ferrite'];br=f['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(T-20))*(1 if pm_enabled else 0)
    Rm=pm['length_m']/(MU0*f['recoil_relative_permeability']*pm['area_m2']);Fpm=br*pm['length_m']/(MU0*f['recoil_relative_permeability'])
    rg=np.column_stack([(gaps[:,0]/m['lift_pole_area_m2']+gaps[:,2]/m['guide_pole_area_m2'])/MU0,(gaps[:,1]/m['lift_pole_area_m2']+gaps[:,3]/m['guide_pole_area_m2'])/MU0])
    rleak=m['leakage']['path_length_m']/(MU0*m['leakage']['path_area_m2'])
    q=np.full((n,4),.0001) if initial is None else np.array(initial,float,copy=True)
    if q.shape!=(n,4) or not np.isfinite(q).all():raise ValueError('finite N×4 warm flux state required')
    q[:,:2]=.012 if initial is None else q[:,:2]
    drive=cur@C
    def state(q):
        psi=q@M.T;S=np.sum(psi,axis=1);hs,ds,us,bs=_steel(S,m['core_paths']['common'],context)
        hb,db,ub,bb=_steel(psi,m['core_paths']['branch'],context);hr,dr,ur,brl=_steel(q[:,:2],m['core_paths']['stationary_return'],context)
        grad=hs[:,None]*common+((hb+Rm*psi-Fpm[:,None])@M)-drive
        grad[:,:2]+=rg*q[:,:2]+hr;grad[:,2:]+=rleak*q[:,2:]
        hess=ds[:,None,None]*np.ones((1,4,4))+np.einsum('nj,jk,jl->nkl',db+Rm,M,M)
        for k in range(4):hess[:,k,k]+=rg[:,k]+dr[:,k] if k<2 else rleak
        energy=us+np.sum(ub+.5*Rm*(psi-br[:,None]*pm['area_m2'])**2,axis=1)+np.sum(.5*rg*q[:,:2]**2+ur,axis=1)+.5*rleak*np.sum(q[:,2:]**2,axis=1)
        return grad,hess,energy,np.maximum(bs,np.max(bb,axis=1)),psi,brl
    converged=np.zeros(n,bool)
    # Stop at the SAME1e-3At residual used by the returned convergence gate.
    # A tighter internal1e-5target caused Armijo stagnation at float roundoff.
    for _ in range(35):
        grad,hess,energy,peak,psi,brl=state(q);converged=np.max(np.abs(grad),axis=1)<1e-3
        if converged.all():break
        step=np.linalg.solve(hess,grad[...,None])[...,0]
        potential=energy-np.sum(drive*q,axis=1);alpha=np.ones(n)
        # Global energy line search protects extreme current/cold/saturated cases.
        for _ in range(18):
            trial=q-alpha[:,None]*step;et=state(trial)[2]-np.sum(drive*trial,axis=1)
            bad=(et>potential-1e-4*alpha*np.sum(grad*step,axis=1)) & ~converged
            if not bad.any():break
            alpha[bad]*=.5
        q-=alpha[:,None]*step
    grad,hess,energy,peak,psi,brl=state(q);converged=np.max(np.abs(grad),axis=1)<1e-3
    linkage=q@C.T;L=np.einsum('ik,nkj->nij',C,np.linalg.solve(hess,np.broadcast_to(C.T,(n,4,2))))
    return q,psi,linkage,L,energy,hess,peak,brl,br,converged,C


def evaluate_batch(gaps_m,current_a,temperature_c=40.,*,variant_id=None,initial_flux_wb=None,pm_enabled=True):
    """Batched map, no force/current/gap clipping. Invalid domain is explicit.

    Returned dflux/dgap differentiates lambda against the four positive gap
    lengths. PM recoil is reversible only above the conservative demag knee;
    failed rows may be inspected, but cannot be treated as valid dynamics maps.
    """
    context=_runtime(variant_id);a,v,m=context[:3]
    g=np.asarray(gaps_m,float);i=np.asarray(current_a,float)
    if g.ndim==1:g=g[None,:]
    if i.ndim==1:i=i[None,:]
    if g.shape!=(len(i),4) or i.shape[1:]!=(2,):raise ValueError('N×4 gaps and N×2 circuit currents required')
    if not np.isfinite(g).all() or not np.isfinite(i).all() or (g<=0).any():raise ValueError('finite positive gaps and finite currents required')
    temp=np.asarray(temperature_c,float)
    if temp.ndim==0:temp=np.full((len(i),2),temp)
    elif temp.shape==(len(i),):temp=np.repeat(temp[:,None],2,axis=1)
    if temp.shape!=(len(i),2) or not np.isfinite(temp).all():raise ValueError('temperature must be finite scalar,N or N×2')
    T=np.mean(temp,axis=1);q,psi,lam,L,W,H,peak,railpeak,br,converged,C=_solve(g,i,T,context,initial_flux_wb,pm_enabled)
    force=q[:,:2]**2/(2*MU0*m['lift_pole_area_m2']);side=q[:,:2]**2/(2*MU0*m['guide_pole_area_m2'])
    up=np.sum(force,axis=1);left=side[:,0]-side[:,1]
    moment=np.zeros((len(i),3));moment[:,0]=.15*(force[:,0]-force[:,1])-.05*left
    pm=m['permanent_magnet'];f=a['materials']['ferrite'];hpm=(psi/pm['area_m2']-br[:,None])/(MU0*f['recoil_relative_permeability'])
    hcj=(f['hcj_20c_a_m']-f['hcj_tolerance_a_m'])*(1+f['hcj_temperature_coefficient_per_k']*(T-20))
    demag_margin=hpm+f['demag_hcj_fraction_limit']*hcj[:,None]
    cu=a['materials']['copper'];res=np.array([m['coils'][0]['conductor_length_m']/(v['copper_lift_mm2']*1e-6),sum(c['conductor_length_m'] for c in m['coils'][1:])/(v['copper_guide_mm2']*1e-6)])*cu['resistivity_20c_ohm_m']
    R=res[None,:]*(1+cu['resistance_temperature_coefficient_per_k']*(temp-20))
    dg=np.zeros((len(i),4,4))
    for k in range(4):dg[:,0 if k in (0,2) else 1,k]=q[:,0 if k in (0,2) else 1]/(MU0*(m['lift_pole_area_m2'] if k<2 else m['guide_pole_area_m2']))
    dlam=-np.einsum('ik,nkj->nij',C,np.linalg.solve(H,dg))
    domain=np.all((g>=a['minimum_gap_m'])&(g<=a['maximum_gap_m']),axis=1)&np.all(np.abs(i)<=a['current_limit_a'],axis=1)&np.all((temp>=f['minimum_temperature_c'])&(temp<=f['maximum_temperature_c']),axis=1)&(T>=f['minimum_temperature_c'])&(T<=f['maximum_temperature_c'])
    valid=domain&converged&np.all(demag_margin>0,axis=1)&(np.maximum(peak,np.max(railpeak,axis=1))<2.2)
    # Static fields dissipate no steel hysteresis/eddy power; ripple loss has a
    # separate explicit API and must not use DC bias as AC amplitude.
    return dict(upward_n=up,leftward_n=left,local_moments_nm=moment,flux_linkage_wb=lam,
        incremental_inductance_h=L,stored_energy_j=W,stored_field_energy_j=W,
        coenergy_j=np.sum(i*lam,axis=1)-W,resistance_ohm=R,copper_loss_w=i*i*R,
        steel_loss_w=np.zeros(len(i)),dflux_dgap_wb_m=dlam,valid=valid,converged=converged,
        branch_flux_wb=q[:,:2],leakage_flux_wb=q[:,2:],total_branch_flux_wb=psi,
        flux_state_wb=q,branch_lift_force_n=force,branch_guidance_force_n=side,
        pm_h_a_m=hpm,pm_b_t=psi/pm['area_m2'],demag_margin_a_m=demag_margin,
        peak_core_b_t=np.maximum(peak,np.max(railpeak,axis=1)),peak_vehicle_core_b_t=peak,peak_return_rail_b_t=railpeak,domain_valid=domain,thermal_capacity_j_k=np.array([m['coils'][0]['copper_mass_kg'],sum(c['copper_mass_kg'] for c in m['coils'][1:])])*cu['specific_heat_j_kg_k'])


def evaluate(gap_m,lift_current_a,guidance_current_a=0.,temperature_c=40.,*,lateral_displacement_m=0.,variant_id=None,pm_enabled=True):
    if isinstance(gap_m,dict):g=[gap_m[k] for k in ('lift_left_m','lift_right_m','guide_left_m','guide_right_m')]
    elif np.asarray(gap_m).ndim==0:g=[gap_m,gap_m,gap_m-lateral_displacement_m,gap_m+lateral_displacement_m]
    else:g=gap_m
    r=evaluate_batch([g],[[lift_current_a,guidance_current_a]],temperature_c,variant_id=variant_id,pm_enabled=pm_enabled)
    out={k:(bool(v[0]) if v.dtype==bool and v.shape==(1,) else v[0].tolist() if v.ndim>0 and len(v)==1 else v.tolist()) for k,v in r.items()}
    out.update(configuration_sha256=definition(variant_id)['configuration_sha256'],scope='Unqualified nonlinear reluctance network; geometry-based, not measured or3D FE qualified',**FLAGS)
    return out


def inverse_current(upward_n,leftward_n,gaps_m,temperature_c=40.,initial_a=None,*,variant_id=None,initial_flux_wb=None):
    """Warm-started two-force Newton solve. No current or target-force clamp."""
    g=np.asarray(gaps_m,float);target=np.column_stack([np.atleast_1d(upward_n),np.atleast_1d(leftward_n)])
    if g.ndim==1:g=g[None,:]
    current=np.zeros((len(g),2)) if initial_a is None else np.array(initial_a,float,copy=True)
    if current.shape!=(len(g),2) or target.shape!=current.shape or not np.isfinite(target).all():raise ValueError('finite matching force/current rows required')
    flux=initial_flux_wb
    for _ in range(16):
        r=evaluate_batch(g,current,temperature_c,variant_id=variant_id,initial_flux_wb=flux);flux=r['flux_state_wb'];actual=np.column_stack([r['upward_n'],r['leftward_n']]);error=actual-target
        if np.max(np.abs(error))<.01:break
        # Maxwell force derivative through the exact network Hessian can be
        # recovered using reciprocity dF/dI=-dλ/dgap (both guide signs explicit).
        D=r['dflux_dgap_wb_m'];J=np.stack([-D[:,:,0]-D[:,:,1],-D[:,:,2]+D[:,:,3]],axis=1)
        try:step=np.linalg.solve(J,error[...,None])[...,0]
        except np.linalg.LinAlgError:break
        step_norm=np.max(np.abs(step),axis=1);step*=np.minimum(1.,30/np.maximum(step_norm,1e-12))[:,None]
        current-=step
        if np.any(np.abs(current)>240):break
    r=evaluate_batch(g,current,temperature_c,variant_id=variant_id,initial_flux_wb=flux)
    residual=np.column_stack([r['upward_n'],r['leftward_n']])-target
    return dict(current_a=current,converged=np.max(np.abs(residual),axis=1)<.1,force_residual_n=residual,valid=r['valid']&(np.max(np.abs(residual),axis=1)<.1),flux_state_wb=r['flux_state_wb'])


def ripple_loss(flux_density_amplitude_t,frequency_hz,*,variant_id=None):
    """Geometry-lamination classical eddy plus two-point50Hz hysteresis proxy.

    Only AC ripple amplitude is input. Bias/minor loops, joints, PWM and3D eddy
    paths require measured losses; no steady-cooling qualification is claimed.
    """
    if min(flux_density_amplitude_t,frequency_hz)<0 or not math.isfinite(flux_density_amplitude_t+frequency_hz):raise ValueError('finite nonnegative ripple required')
    a=load();v=_variant(a,variant_id);m=_module(a,v);s=a['materials']['steel'];b=flux_density_amplitude_t;f=frequency_hz
    e=lambda B,F:math.pi**2*s['lamination_m']**2*F**2*B**2/(6*s['resistivity_ohm_m']*s['density_kg_m3'])
    h1=s['loss_50hz_1t_w_kg']-e(1,50);h15=s['loss_50hz_1_5t_w_kg']-e(1.5,50);exponent=math.log(h15/h1)/math.log(1.5)
    perkg=h1*(f/50)*b**exponent+e(b,f)
    kg=sum(p['mass_kg'] for p in m['parts'] if p['component_scope']=='new-core')
    return dict(core_mass_kg=kg,loss_w=kg*perkg,specific_loss_w_kg=perkg,hysteresis_exponent=exponent,qualified=False)


def field_map(*,variant_id=None,gaps_m=(.004,.008,.013,.021,.030),currents_a=(-60.,0.,60.),temperature_c=40.):
    rows=[]
    for gap in gaps_m:
        for lift in currents_a:
            for guide in (-20.,0.,20.):
                r=evaluate_batch([[gap]*4],[[lift,guide]],temperature_c,variant_id=variant_id)
                rows.append(dict(gap_m=gap,current_a=[lift,guide],upward_n=float(r['upward_n'][0]),leftward_n=float(r['leftward_n'][0]),valid=bool(r['valid'][0]),linkage_wb=r['flux_linkage_wb'][0].tolist(),incremental_inductance_h=r['incremental_inductance_h'][0].tolist(),stored_energy_j=float(r['stored_energy_j'][0])))
    return dict(configuration_sha256=definition(variant_id)['configuration_sha256'],rows=rows,scope='Reluctance network samples only; not measured/FE validated',**FLAGS)


def guideway_definition(span_m=25.,*,variant_id=None):
    """Four connected L-return sections per track; brackets are separate.

    Axis convention matches definition(): each module's two useful magnetic
    loops require their own L-return. These are not four extra running beams.
    Their actual steel/insulation mass and additional transverse support loads
    must be included by the civil designer; no inherited7.51t rail allowance.
    """
    if not isinstance(span_m,(int,float)) or not math.isfinite(span_m) or not 0<span_m<=100:raise ValueError('bounded positive guideway length required')
    a=load();parts=[];faces=[];rho=a['materials']['steel']['density_kg_m3']*a['stack_fill'];z0=a['module_mount_z_m'];gap=a['nominal_gap_m']
    for line in (-1,1):
        module_y=.88*line
        for branch in (-1,1):
            prefix=f'return/{line}/{branch}'
            inner=.40+gap
            yweb=module_y+inner if branch>0 else module_y-inner-.025
            # Disjoint web+top-flange regions. Web inner face is0.408m from
            # module centre; flange underside is z=0.208m above module datum.
            parts.append(_box(prefix+'/web',[span_m,.025,.233],[-span_m/2,yweb,z0], 'M400-50A-stack',rho,'guideway-return'))
            yflange=module_y+.10 if branch>0 else module_y-inner
            parts.append(_box(prefix+'/flange',[span_m,inner-.10,.025],[-span_m/2,yflange,z0+.20+gap], 'M400-50A-stack',rho,'guideway-return'))
            faces.append(dict(id=prefix,lift_plane_z_m=z0+.20+gap,lift_face_y_interval_m=[module_y+branch*.15-.05,module_y+branch*.15+.05],
                guide_plane_y_m=module_y+branch*inner,guide_face_z_interval_m=[z0,z0+.10],
                attachment_line_m=[module_y+branch*(inner+.0125),z0+.1165],
                attachment_scope='Actual bracket/crossmember, insulation and fastener design to concrete webs required; not implicitly supported.'))
    protection=json.loads(PROTECTION.read_text())
    for row in protection.get('guideway_rows',[]):
        for j,y in enumerate(row['centres_y_m']):
            parts.append(_box(row['id']+f'/{j}',[span_m,row['section_m'][0],row['section_m'][1]],[-span_m/2,y-row['section_m'][0]/2,row['centre_z_m']-row['section_m'][1]/2],row['material'],row['density_kg_m3'],'guideway-protection-wear-strip'))
    mass=sum(p['mass_kg'] for p in parts)
    return dict(schema='osr-dimensioned-magnetic-return-guideway/1',configuration_sha256=definition(variant_id)['configuration_sha256'],span_m=span_m,parts=parts,faces=faces,mass_kg=mass,linear_mass_kg_m=mass/span_m,
        lamination=dict(thickness_m=.0005,stack_fill=a['stack_fill'],plane='yz',stack_axis='x',sheets_per_m=a['stack_fill']/.0005,stock_joint_and_insulation_qualified=False),
        brackets_counted_here=False,scope='Magnetic return stock only; civil module must add actual crossmembers, fasteners, rail joints and maintainability. No beam, prestress or foundation acceptance.',**FLAGS)


def wayside_field(variant_id=None,wavelength_m=.5):
    """PM-source Fourier sensitivity; explicitly NOT a wayside useful-field map.

    Steel return paths, pole shoes, actual coil placement and excitation change
    the useful harmonic and normal force. A PM magnetization transform alone
    cannot establish propulsion. The old0.5m traveling-wave law stays held.
    """
    if not math.isfinite(wavelength_m) or wavelength_m<=0:raise ValueError('positive electrical wavelength required')
    d=definition(variant_id);banks=[p for p in d['module']['parts'] if p['material']=='TDK-FB9B'];k=2*math.pi/wavelength_m
    spatial=[]
    for position in d['module_placements_m']:
        for p in banks:
            centre=np.array(position)+p['cg_m'];length=p['size_m'][0]
            spatial.append(dict(id=f"{position[0]}/{position[1]}/"+p['id'],centre_m=centre.tolist(),size_m=p['size_m'],magnetization_axis='z',magnetization_direction=-1,
                source_transform_m3=[float(-p['volume_m3']*np.sinc(length/wavelength_m)*math.cos(k*centre[0])),float(p['volume_m3']*np.sinc(length/wavelength_m)*math.sin(k*centre[0]))]))
    return dict(configuration_sha256=d['configuration_sha256'],pm_banks=spatial,source_module_pitch_m=1.,parent_electrical_wavelength_m=.5,requested_wavelength_m=wavelength_m,
        summed_source_transform_m3=np.sum([x['source_transform_m3'] for x in spatial],axis=0).tolist(),
        useful_field_map_verified=False,useful_flux_density_t=None,longitudinal_force_map=None,normal_force_map=None,
        compatible_with_parent=False,applicable_hold='Closed-core/return-rail geometry changes external field. Actual periodic3D field plus station coil geometry and force/normal/linkage maps are mandatory before propulsion/control adoption.',**FLAGS)


def thermal_study(current_a,*,variant_id=None,duty_fraction=1.,period_s=180.,cycles=40,ambient_c=40.):
    """Repeated lumped copper/fluid duty with explicit, unqualified heat path."""
    a=load();v=_variant(a,variant_id);m=_module(a,v);i=np.asarray(current_a,float)
    if i.shape!=(2,) or not np.isfinite(i).all() or not 0<duty_fraction<=1 or not 0<period_s<=3600 or type(cycles)is not int or not 1<=cycles<=1000:raise ValueError('bounded two-circuit thermal duty required')
    cu=a['materials']['copper'];copper=np.array([m['coils'][0]['copper_mass_kg'],sum(c['copper_mass_kg'] for c in m['coils'][1:])]);capacity=copper*cu['specific_heat_j_kg_k']
    G=np.array(v['cooling_w_k']);base=np.array([m['coils'][0]['conductor_length_m']/(v['copper_lift_mm2']*1e-6),sum(c['conductor_length_m'] for c in m['coils'][1:])/(v['copper_guide_mm2']*1e-6)])*cu['resistivity_20c_ohm_m']
    T=np.full(2,ambient_c);peak=T.copy();energy=np.zeros(2);step=min(.5,period_s/200)
    for n in range(math.ceil(cycles*period_s/step)):
        time=n*step;dt=min(step,cycles*period_s-time);on=(time%period_s)<duty_fraction*period_s
        power=i*i*base*(1+cu['resistance_temperature_coefficient_per_k']*(T-20))*(1 if on else 0)
        T+=dt*(power-G*(T-ambient_c))/capacity;energy+=power*dt;peak=np.maximum(peak,T)
    density=np.abs(i)/[v['copper_lift_mm2'],v['copper_guide_mm2']]
    # Continuous equilibrium has no finite stable solution if positive copper
    # resistance feedback exceeds the declared heat-removal conductance.
    hotgain=i*i*base*cu['resistance_temperature_coefficient_per_k']*duty_fraction
    equilibrium=np.where(G>hotgain,ambient_c+(i*i*base*(1+cu['resistance_temperature_coefficient_per_k']*(ambient_c-20))*duty_fraction)/(G-hotgain),np.inf)
    return dict(current_a=i.tolist(),duty_fraction=duty_fraction,period_s=period_s,cycles=cycles,peak_copper_c=peak.tolist(),final_copper_c=T.tolist(),
        steady_duty_c=[float(t) if math.isfinite(t) else None for t in equilibrium],steady_duty_defined=bool(np.isfinite(equilibrium).all()),copper_heat_j=energy.tolist(),current_density_a_mm2=density.tolist(),
        thermal_screen_pass=bool(np.all(peak<=a['maximum_copper_c']) and np.all(equilibrium<=a['maximum_copper_c']) and np.all(density<=a['continuous_current_density_a_mm2'])),
        cooling_heat_path=m['cooling'],pump_power_w=m['cooling']['flow_kg_s']/m['cooling']['fluid_density_kg_m3']*m['cooling']['pressure_drop_pa']/m['cooling']['pump_efficiency'],
        scope='Repeated copper/fluid lumped model and asymptotic equilibrium, conditional on unmeasured conductance/flow. No continuous-duty hardware rating.',**FLAGS)


def variant_study():
    """Equal-function mass/force/core/demag/continuous-heat comparison."""
    rows=[];a=load()
    for v in a['variants']:
        d=definition(v['id']);target=d['controlled_aw3_kg']*9.80665/24
        temperature=np.array([[40.,40.]])
        for _ in range(16):
            current=inverse_current([target],[0.],[[.008]*4],temperature,variant_id=v['id'])
            thermal=thermal_study(current['current_a'][0],variant_id=v['id'],cycles=1)
            next_temperature=np.array([[float('inf') if t is None else t for t in thermal['steady_duty_c']]])
            if not np.isfinite(next_temperature).all():break
            temperature=.5*temperature+.5*next_temperature
        r=evaluate_batch([[.008]*4],current['current_a'],temperature,variant_id=v['id'])
        thermal=thermal_study(current['current_a'][0],variant_id=v['id']);pack=bool(max(c['fill_fraction'] for c in d['module']['coils'])<=a['coil_fill_limit'])
        masscost=sum(x['extended_cost_usd']*x['quantity_per_car'] for x in d['manufacturing_bom'])
        peak_sample=evaluate_batch([[.008]*4],[[a['current_limit_a'],0.]],40.,variant_id=v['id'])
        eligible=bool(current['valid'][0] and thermal['thermal_screen_pass'] and pack)
        rows.append(dict(id=v['id'],configuration_sha256=d['configuration_sha256'],controlled_aw3_kg=d['controlled_aw3_kg'],module_mass_kg=d['module']['mass_kg'],
            installed_module_mass_kg=24*d['module']['mass_kg'],module_material_and_process_unquoted_usd_per_car=masscost,
            reaction_rail_kg_per_m=guideway_definition(1.,variant_id=v['id'])['mass_kg'],static_target_n_per_module=target,current_a=current['current_a'][0].tolist(),
            positive_peak_current_sample=dict(lift_current_a=a['current_limit_a'],guidance_current_a=0.,upward_n=float(peak_sample['upward_n'][0]),peak_return_rail_b_t=peak_sample['peak_return_rail_b_t'][0].tolist(),required_aw3_upward_n=target,support_fraction=float(peak_sample['upward_n'][0])/target),
            maximum_core_b_t=float(r['peak_core_b_t'][0]),minimum_demag_margin_a_m=float(np.min(r['demag_margin_a_m'])),
            pack_fit=pack,static_map_valid=bool(current['valid'][0]),thermal=thermal,screen_pass=eligible,
            complete_system_feasible=False,wayside_field_verified=False,physical_accepted=False))
    eligible=[r for r in rows if r['screen_pass']]
    choice=min(eligible,key=lambda r:(r['controlled_aw3_kg'],r['module_material_and_process_unquoted_usd_per_car']))['id'] if eligible else None
    return dict(variants=rows,provisional_mass_first_screen_choice=choice,configured_variant=a['selected_variant'],
        objective='Minimise actual total AW3 mass then counted unquoted module cost, subject to equal static support, BH/demag/current/coil-fill and conditional continuous-cooling screens. Civil return steel explicitly counted; propulsion/guidance/dynamics/manufacturing/site acceptance remain gates.',
        no_automatic_selection=True,**FLAGS)


def _halbach_band(a):
    b=a['propulsion_band'];parts=[];count=round(b['length_m']/b['period_m'])*4;dx=b['period_m']/4
    if not math.isclose(count*dx,b['length_m'],abs_tol=1e-12):raise ValueError('whole periodic propulsion blocks required')
    for side in (-1,1):
        inner=b['inner_cover_face_abs_y_m']+b['front_cover_m'];yc=side*(inner+b['thickness_m']/2)
        for j in range(count):
            angle=(j%4)*math.pi/2;vector=[round(math.cos(angle),12),round(-side*math.sin(angle),12),0.]
            p=_box(f'propulsion/{side}/ferrite-{j:03d}',[dx,b['thickness_m'],b['height_m']],
                [-b['length_m']/2+j*dx,yc-b['thickness_m']/2,b['top_z_m']-b['height_m']],
                b['material'],a['materials']['ferrite']['density_kg_m3'],'new-passive-propulsion-ferrite',magnetization_vector=vector)
            parts.append(p)
        cover_y=side*b['inner_cover_face_abs_y_m'] if side>0 else -b['inner_cover_face_abs_y_m']-b['front_cover_m']
        parts.append(_box(f'propulsion/{side}/front-cover',[b['length_m'],b['front_cover_m'],b['height_m']],[-b['length_m']/2,cover_y,b['top_z_m']-b['height_m']], 'aluminium',2700.,'new-passive-propulsion-cover'))
        back_y=side*(inner+b['thickness_m']) if side>0 else -inner-b['thickness_m']-b['backplate_m']
        parts.append(_box(f'propulsion/{side}/backplate',[b['length_m'],b['backplate_m'],b['height_m']],[-b['length_m']/2,back_y,b['top_z_m']-b['height_m']], 'aluminium',2700.,'new-passive-propulsion-backing'))
        for z in (b['top_z_m']+.001,b['top_z_m']-b['height_m']-.004):
            parts.append(_box(f'propulsion/{side}/retaining-strip/{z}',[b['length_m'],b['thickness_m']+.008,.003],[-b['length_m']/2,side*(inner+b['thickness_m']/2)-(b['thickness_m']+.008)/2,z], 'aluminium',2700.,'new-passive-propulsion-retention'))
    return dict(parts=parts,mass_kg=sum(p['mass_kg'] for p in parts),period_m=b['period_m'],pole_pitch_m=b['period_m']/2,
        length_m=b['length_m'],active_height_m=b['height_m'],thickness_m=b['thickness_m'],bands=2,
        manufacturing_block_count=count*2,magnetization='four uniform cardinal directions in x/local-inward-normal; repeat1/4period blocks',
        attachment_hold='Band-to-cradle transverse webs, clips, adhesive, bolts, endcaps and service clearances require explicit structural definition; zero mass credit for inherited ferrite allocation.',
        physical_accepted=False)


def _band_bom(a,band):
    p=a['procurement'];rows=[]
    for part in band['parts']:
        ferrite='ferrite' in part['id'];waste=p['ferrite_waste_fraction'] if ferrite else .10;rate=p['ferrite_usd_kg'] if ferrite else p['steel_usd_kg'] if part['material']=='M400-50A-stack' else p['aluminium_usd_kg'];purchase=part['mass_kg']/(1-waste)
        rows.append(dict(id=part['id'],component_scope=part['component_scope'],quantity_per_car=1,quantity_per_module=0,unit='kg',net_material_quantity=part['mass_kg'],purchase_quantity=purchase,waste_fraction=waste,unit_rate_usd=rate,extended_cost_usd=purchase*rate,mass_kg=part['mass_kg'],geometry_part_ids=[part['id']],process='locally jigged passive magnet bank; no rotating or onboard traction motor',lead_time_days=60,origin_basis='Raw FB12H ferrite origin unconfirmed; UK/local assembly possible, not asserted British-made magnet.',tolerance=None,qa_requirements=['block material/demag certificate','orientation/pitch/retention and gap survey','serialized pull test and approved drawing unexecuted']))
    return rows


def _halbach_coefficients(a,temperature_c=40.,harmonics=None):
    """Independent-interface exact Fourier boundary solve for finite-thickness PM.

    Scalar potential is continuous; normal B is continuous at both interfaces.
    Four constant magnetization vectors perperiod, recoil permeability1.05.
    Coefficients Bn are complex positive Fourier terms; peak=2abs(coefficient).
    """
    b=a['propulsion_band'];f=a['materials']['ferrite'];br=b['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature_c-20))
    out=[];mu=b['recoil_relative_permeability']
    for n in range(1,(harmonics or b['harmonics'])+1):
        k=2*math.pi*n/b['period_m'];mx=0j;mn=0j
        for j in range(4):
            integral=(np.exp(-2j*math.pi*n*j/4)-np.exp(-2j*math.pi*n*(j+1)/4))/(2j*math.pi*n)
            mx+=br*math.cos(j*math.pi/2)*integral;mn+=br*math.sin(j*math.pi/2)*integral
        e=math.exp(-k*b['thickness_m']);part=-1j*mx/(MU0*mu*k)
        A=np.array([[1,e,-1,0],[e,1,0,-1],[-mu,mu*e,-1,0],[-mu*e,mu,0,1]],complex)
        rhs=np.array([-part,-part,-mn/(MU0*k),-mn/(MU0*k)])
        inside1,inside2,upper,lower=np.linalg.solve(A,rhs)
        out.append(dict(n=n,k=k,normal_surface_t=MU0*k*upper,weak_surface_t=-MU0*k*lower,
            inside1=inside1,inside2=inside2,particular=part,br_tangent=mx,br_normal=mn))
    return out


def propulsion_field(relative_x_m,gap_m,temperature_c=40.,*,a=None):
    """Strong-side infinite-height2D air field, all explicit periodic harmonics."""
    a=load() if a is None else a;x=np.asarray(relative_x_m,float);gap=np.asarray(gap_m,float)
    if not np.isfinite(x).all() or not np.isfinite(gap).all() or np.any(gap<0):raise ValueError('finite nonnegative external field coordinates required')
    x,gap=np.broadcast_arrays(x,gap);normal=np.zeros_like(x);tangent=np.zeros_like(x)
    for h in _halbach_coefficients(a,float(temperature_c)):
        value=h['normal_surface_t']*np.exp(-h['k']*gap+1j*h['k']*x)
        normal+=2*np.real(value);tangent+=2*np.real(-1j*value)
    return dict(normal_t=normal,tangent_t=tangent,scope='2D infinite-height periodic linear-recoil field; finite-height/ends/core interaction and measured map remain open')


def spatial_band_coupon(nx=128,pm_cells=24,gap_m=.009,temperature_c=40.,current_sheet_a_m=10000.,phase_rad=.3,margin_periods=1.):
    """Independent2D FFT/finite-volume A_z magnetostatic boundary-value coupon.

    This solver discretizes the actual four-segment magnetization and recoil
    region on a2D grid. It does not call the analytical harmonic boundary solve.
    x is periodic, A=0 at finite external boundaries. Grid/boundary sensitivity,
    Lorentz force, mutual-coenergy derivatives and air-gap cross-Maxwell stress
    are retained. Infinite transverse height and reversible material limits
    remain explicit; this is not a whole-vehicle3D field confirmation.
    """
    from scipy.linalg import solve_banded
    a=load();b=a['propulsion_band'];f=a['materials']['ferrite']
    if type(nx)is not int or nx%4 or not 32<=nx<=1024 or type(pm_cells)is not int or not 8<=pm_cells<=128 or not .5<=margin_periods<=3:raise ValueError('bounded resolved spatial coupon grid required')
    if not 0<gap_m<.1 or not math.isfinite(temperature_c+current_sheet_a_m+phase_rad):raise ValueError('finite coupon excitation required')
    L=b['period_m'];dx=L/nx;dy=b['thickness_m']/pm_cells;air=math.ceil(margin_periods*L/dy);ny=2*air+pm_cells
    x=(np.arange(nx)+.5)*dx;y=(np.arange(ny)-air-pm_cells+.5)*dy;pm=(y<0)&(y>-b['thickness_m']);mur=np.where(pm,b['recoil_relative_permeability'],1.);nu=1/(MU0*mur)
    br=b['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature_c-20));angle=(np.arange(nx)//(nx//4))*math.pi/2
    Bt=np.zeros((ny,nx));Bn=np.zeros_like(Bt);Bt[pm]=br*np.cos(angle);Bn[pm]=br*np.sin(angle)
    # Source currents form an actual finite-thickness sinusoidal winding layer.
    layer=np.abs(y-gap_m)<max(dy/2,.001);J=np.zeros_like(Bt)
    if not layer.any():layer[np.argmin(abs(y-gap_m))]=True
    J[layer]=current_sheet_a_m*np.cos(2*math.pi*x/L+phase_rad)/(np.count_nonzero(layer)*dy)
    source_pm=-np.gradient(nu[:,None]*Bt,dy,axis=0)+np.fft.ifft(1j*(2*math.pi*np.fft.fftfreq(nx,dx))[None,:]*np.fft.fft(nu[:,None]*Bn,axis=1),axis=1).real
    def solve(source):
        rhs=np.fft.fft(source,axis=1)/nx;potential=np.zeros((ny,nx),complex);face=2*nu[:-1]*nu[1:]/(nu[:-1]+nu[1:])
        for n in range(nx):
            k=2*math.pi*np.fft.fftfreq(nx,dx)[n];k2=4*math.sin(k*dx/2)**2/dx**2
            diag=nu*k2;diag=diag.copy();diag[:-1]+=face/dy**2;diag[1:]+=face/dy**2;diag[[0,-1]]+=2*nu[[0,-1]]/dy**2
            band=np.zeros((3,ny),complex);band[1]=diag;band[0,1:]=-face/dy**2;band[2,:-1]=-face/dy**2
            potential[:,n]=solve_banded((1,1),band,rhs[:,n],check_finite=False)
        return np.fft.ifft(potential*nx,axis=1).real
    Ap=solve(source_pm);Ac=solve(J)
    kgrid=2*math.pi*np.fft.fftfreq(nx,dx)
    def fields(A):return np.gradient(A,dy,axis=0),-np.fft.ifft(1j*kgrid[None,:]*np.fft.fft(A,axis=1),axis=1).real
    Bxp,Bnp=fields(Ap);Bxc,Bnc=fields(Ac)
    iy=int(np.argmin(abs(y-gap_m)));fund=np.fft.fft(Bnp[iy])/nx;actual=2*abs(fund[1]);effective_gap=float(y[iy])
    # Force on magnets is opposite the source winding's Lorentz reaction.
    fx=float(np.sum(J*Bnp)*dx*dy);fn=float(-np.sum(J*Bxp)*dx*dy);W=float(np.sum(J*Ap)*dx*dy)
    shift=1e-5
    Apfft=np.fft.fft(Ap,axis=1)
    def energy_shift(s):return float(np.sum(J*np.fft.ifft(Apfft*np.exp(-1j*kgrid[None,:]*s),axis=1).real)*dx*dy)
    fx_energy=(energy_shift(shift)-energy_shift(-shift))/(2*shift)
    fn_energy=float(np.sum(J*(-np.gradient(Ap,dy,axis=0)))*dx*dy)
    imid=int(np.argmin(abs(y-gap_m/2)));maxwell_x=float(np.sum(Bxp[imid]*Bnc[imid]+Bxc[imid]*Bnp[imid])/MU0*dx)
    maxwell_normal=float(np.sum(Bnp[imid]*Bnc[imid]-Bxp[imid]*Bxc[imid])/MU0*dx)
    predicted=2*abs(_halbach_coefficients(a,temperature_c,1)[0]['normal_surface_t'])*math.exp(-2*math.pi*effective_gap/L)
    Hx=(Bxp-Bt)/(MU0*mur[:,None]);Hn=(Bnp-Bn)/(MU0*mur[:,None]);opp=-(Hx*np.cos(angle)+Hn*np.sin(angle))
    opp_pm=float(np.max(opp[pm]));hcj=(b['hcj_20c_a_m']-b['hcj_tolerance_a_m'])*(1+f['hcj_temperature_coefficient_per_k']*(temperature_c-20))
    return dict(method='independent2D FFT/finite-volume vector-potential PDE',nx=nx,pm_cells=pm_cells,dx_m=dx,dy_m=dy,finite_boundary_margin_periods=margin_periods,
        requested_gap_m=gap_m,sampled_gap_m=effective_gap,fundamental_normal_peak_t=float(actual),analytical_boundary_peak_t=float(predicted),field_relative_difference=abs(actual-predicted)/predicted,
        force_x_n_per_m_height=fx,force_normal_n_per_m_height=fn,force_x_coenergy_n_per_m_height=fx_energy,force_normal_coenergy_n_per_m_height=fn_energy,
        force_x_cross_maxwell_n_per_m_height=maxwell_x,force_normal_cross_maxwell_n_per_m_height=maxwell_normal,mutual_coenergy_j_per_m_height=W,
        peak_opposing_pm_field_a_m=opp_pm,lower_bound_hcj_a_m=hcj,conservative_demag_margin_a_m=.8*hcj-opp_pm,
        PM_self_field_only_in_demag_sample=True,armature_demag_still_to_add=True,
        x_m=x.tolist(),sample_normal_t=Bnp[iy].tolist(),sample_tangent_t=Bxp[iy].tolist(),
        scope='Periodic2D coupon; no finite-height/end/core interaction, irreversible hysteresis, corner rounding or physical qualification',**FLAGS)


def _propulsion_band(a):
    if not a['propulsion_flux_shoe']['selected']:return _halbach_band(a)
    if a['propulsion_flux_shoe'].get('pm_shape')=='round-transverse':return _round_propulsion_band(a)
    b=a['propulsion_band'];q=a['propulsion_flux_shoe'];parts=[];dx=q['period_m']/4;count=round(q['length_m']/dx)
    inner=b['inner_cover_face_abs_y_m']+b['front_cover_m']
    for side in (-1,1):
        for j in range(count):
            shoe=j%2==0;mat='M400-50A-stack' if shoe else q['material'];rho=a['materials']['steel']['density_kg_m3']*a['stack_fill'] if shoe else a['materials']['ferrite']['density_kg_m3']
            yc=side*(inner+q['depth_m']/2)
            parts.append(_box(f'propulsion/{side}/'+('shoe-' if shoe else 'ferrite-')+f'{j:03d}',[dx,q['depth_m'],q['height_m']],
                [-q['length_m']/2+j*dx,yc-q['depth_m']/2,b['top_z_m']-q['height_m']],mat,rho,
                'new-passive-propulsion-core' if shoe else 'new-passive-propulsion-ferrite',
                magnetization_vector=None if shoe else [1. if j%4==1 else -1.,0.,0.],
                lamination_plane='xy' if shoe else None,stack_axis='z' if shoe else None))
    # Same actual covers/trays around the shallower, shoe-filled array.
    base=deepcopy(a);base['propulsion_band']['thickness_m']=q['depth_m']
    parts.extend(p for p in _halbach_band(base)['parts'] if not p['id'].split('/')[-1].startswith('ferrite-'))
    return dict(parts=parts,mass_kg=sum(p['mass_kg'] for p in parts),period_m=q['period_m'],pole_pitch_m=q['period_m']/2,
        length_m=q['length_m'],active_height_m=q['height_m'],thickness_m=q['depth_m'],bands=2,
        manufacturing_block_count=count,magnetization='Tangential+x PM between negative/positive shoes then−x PM; two PM and two laminated shoes perperiod',
        topology='Both broad faces free; no uncounted backiron or assumed fluxgain. Nonlinear2D field solved independently of lift/guidance circuit.',
        attachment_hold='Propulsion band retention/dropinterface and transverse bracing unqualified; all magnet/core/cover/tray mass counted.',physical_accepted=False)


def spatial_flux_shoe_coupon(nx=96,depth_cells=16,temperature_c=40.,margin_periods=1.,max_iterations=60,depth_m=None,pm_shape=None):
    """Nonlinear independent periodic2D finite-volume magnetic vector potential.

    Actual tangential PM blocks alternate with steel shoes; every cell uses
    either air, recoil PM or source-curve secant steel reluctivity. Unlike the
    Halbach solver, x-varying nonlinear permeability prevents separation of
    variables. Sparse5-point flux continuity is iterated to a stated residual.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    a=load();b=a['propulsion_band'];q=deepcopy(a['propulsion_flux_shoe']);f=a['materials']['ferrite'];steel=a['materials']['steel']
    if pm_shape is not None:q['pm_shape']=pm_shape
    if depth_m is not None:
        if not .02<=depth_m<=.10:raise ValueError('bounded explicit array-depth variant required')
        q['depth_m']=depth_m
    if nx%4 or not 32<=nx<=256 or not 8<=depth_cells<=48 or not .5<=margin_periods<=2:raise ValueError('bounded resolved flux-shoe grid required')
    L=q['period_m'];dx=L/nx;dy=q['depth_m']/depth_cells;air=math.ceil(margin_periods*L/dy);ny=2*air+depth_cells
    x=(np.arange(nx)+.5)*dx;y=(np.arange(ny)-air-depth_cells+.5)*dy;inside=(y<0)&(y>-q['depth_m']);quarter=np.arange(nx)//(nx//4)
    pm=inside[:,None]&np.isin(quarter,[1,3])[None,:];core=inside[:,None]&np.isin(quarter,[0,2])[None,:]
    if q.get('pm_shape')=='round-transverse':
        delta=(x-L/4+L/4)%(L/2)-L/4
        pm=(delta[None,:]**2+(y[:,None]+q['depth_m']/2)**2)<(q['depth_m']/2)**2
        core=inside[:,None]&~pm
    br=b['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature_c-20));direction=np.where(x<L/2,1.,-1.) if q.get('pm_shape')=='round-transverse' else np.where(quarter==1,1.,-1.)
    brx=pm*br*direction[None,:];brn=np.zeros_like(brx)
    # A1mm corner chamfer is represented by actual removed corner cells on
    # the PM pieces, not omission of their demagnetization sample afterwards.
    cham=q['corner_chamfer_m'];px=np.mod(x,dx*(nx//4));edge_distance=np.minimum(px,L/4-px)
    py=np.minimum(abs(y),abs(y+q['depth_m']))
    removed=pm & ((edge_distance[None,:]+py[:,None])<cham) if q.get('pm_shape')!='round-transverse' else np.zeros_like(pm)
    pm[removed]=False;brx[removed]=0.
    Hcurve=np.array(steel['h_a_m']);Bcurve=np.array(steel['j_t'])+MU0*Hcurve
    nu=np.full((ny,nx),1/MU0);nu[pm]=1/(MU0*b['recoil_relative_permeability']);nu[core]=400.
    pmnu=np.where(pm,1/(MU0*b['recoil_relative_permeability']),0.)
    source=-np.gradient(pmnu*brx,dy,axis=0)
    ids=np.arange(ny*nx).reshape(ny,nx);A=np.zeros_like(nu);last=math.inf;converged=False
    for iteration in range(max_iterations):
        fx=2*nu*np.roll(nu,-1,axis=1)/(nu+np.roll(nu,-1,axis=1));fy=2*nu[:-1]*nu[1:]/(nu[:-1]+nu[1:])
        diag=(fx+np.roll(fx,1,axis=1))/dx**2;diag[:-1]+=fy/dy**2;diag[1:]+=fy/dy**2;diag[[0,-1]]+=2*nu[[0,-1]]/dy**2
        rows=[ids.ravel(),ids.ravel(),ids.ravel(),ids[:-1].ravel(),ids[1:].ravel()]
        cols=[ids.ravel(),np.roll(ids,-1,axis=1).ravel(),np.roll(ids,1,axis=1).ravel(),ids[1:].ravel(),ids[:-1].ravel()]
        data=[diag.ravel(),(-fx/dx**2).ravel(),(-np.roll(fx,1,axis=1)/dx**2).ravel(),(-fy/dy**2).ravel(),(-fy/dy**2).ravel()]
        matrix=coo_matrix((np.concatenate(data),(np.concatenate(rows),np.concatenate(cols))),shape=(ny*nx,ny*nx)).tocsc()
        solved=spsolve(matrix,source.ravel()).reshape(ny,nx)
        Bx=np.gradient(solved,dy,axis=0);Bn=-(np.roll(solved,-1,axis=1)-np.roll(solved,1,axis=1))/(2*dx);mag=np.sqrt(Bx*Bx+Bn*Bn)
        h=np.interp(mag,Bcurve,Hcurve);high=mag>Bcurve[-1];h[high]=Hcurve[-1]+(mag[high]-Bcurve[-1])/MU0
        wanted=np.maximum(100.,h/np.maximum(mag,1e-12));change=float(np.max(np.abs(solved-A))/max(np.max(np.abs(solved)),1e-12));A=solved
        mismatch=float(np.max(abs(np.log(np.maximum(wanted[core],1e-9)/nu[core]))))
        if change<2e-6 and mismatch<2e-3:converged=True;break
        nu[core]=np.exp(.55*np.log(nu[core])+.45*np.log(wanted[core]));last=change
    residual=float(np.linalg.norm(matrix@A.ravel()-source.ravel())/max(np.linalg.norm(source.ravel()),1e-12))
    first_air=int(np.where(y>0)[0][0]);coeff=np.fft.fft(Bn[first_air])/nx;surface=[coeff[n]*np.exp(2*math.pi*n*y[first_air]/L) for n in range(1,min(31,nx//2-1)+1)]
    Hx=(Bx-brx)/(MU0*b['recoil_relative_permeability']);Hn=(Bn-brn)/(MU0*b['recoil_relative_permeability']);opp=-Hx*direction[None,:]
    hcj=(b['hcj_20c_a_m']-b['hcj_tolerance_a_m'])*(1+f['hcj_temperature_coefficient_per_k']*(temperature_c-20));peakopp=float(np.max(opp[pm]))
    return dict(method='nonlinear2D periodic sparse finite-volume vectorpotential',pm_shape=q.get('pm_shape','rectangular'),depth_m=q['depth_m'],nx=nx,depth_cells=depth_cells,dx_m=dx,dy_m=dy,iterations=iteration+1,converged=converged,
        matrix_relative_residual=residual,nonlinear_secant_mismatch=mismatch,finite_boundary_margin_periods=margin_periods,temperature_c=temperature_c,
        first_air_sample_y_m=float(y[first_air]),surface_normal_fourier_t=[[float(z.real),float(z.imag)] for z in surface],
        peak_core_b_t=float(np.max(mag[core])),peak_opposing_pm_field_a_m=peakopp,lower_bound_hcj_a_m=hcj,conservative_demag_margin_a_m=.8*hcj-peakopp,
        nominal_gap_fundamental_peak_t=float(2*abs(surface[0])*math.exp(-2*math.pi*(a['nominal_gap_m']+b['front_cover_m'])/L)),
        removed_corner_cell_volume_fraction=float(np.count_nonzero(removed)/max(1,np.count_nonzero(pm)+np.count_nonzero(removed))),
        scope='2D finite-height assumption; actual1mm chamfer geometry/netmass/native machining,3D leakage/end/interactions and measured material maps remain open.',**FLAGS)


def _round_propulsion_band(a):
    b=a['propulsion_band'];q=a['propulsion_flux_shoe'];L=q['length_m'];radius=q['depth_m']/2;h=q['height_m'];parts=[]
    centrexs=np.arange(-L/2+q['period_m']/4,L/2,q['period_m']/2)
    inner=b['inner_cover_face_abs_y_m']+b['front_cover_m'];rho=a['materials']['steel']['density_kg_m3']*a['stack_fill']
    for side in (-1,1):
        yc=side*(inner+radius);z=b['top_z_m']-h
        for j,cx in enumerate(centrexs):
            mass=math.pi*radius**2*h*a['materials']['ferrite']['density_kg_m3'];I=np.diag([mass*(3*radius**2+h*h)/12]*2+[mass*radius**2/2])
            parts.append(dict(id=f'propulsion/{side}/round-ferrite-{j:03d}',kind='cylinder',cylinder_axis='z',size_m=[2*radius,2*radius,h],at_m=[float(cx-radius),yc-radius,z],
                volume_m3=math.pi*radius**2*h,mass_kg=mass,cg_m=[float(cx),yc,z+h/2],inertia_kg_m2=I.tolist(),material=q['material'],
                component_scope='new-passive-propulsion-ferrite',magnetization_vector=[1. if j%2==0 else -1.,0.,0.],
                manufacturing_disc_count=round(h/q['magnet_disc_height_m']),disc_height_m=q['magnet_disc_height_m']))
        bounds=np.r_[-L/2,centrexs,L/2]
        for j,(start,end) in enumerate(zip(bounds[:-1],bounds[1:])):
            size=[float(end-start),2*radius,h];box=_box(f'propulsion/{side}/concave-shoe-{j:03d}',size,[float(start),yc-radius,z],'M400-50A-stack',rho,'new-passive-propulsion-core')
            # Exact signed moments of half-cylinder pockets at the two ends.
            terms=[(box['mass_kg'],np.array(box['cg_m']),np.array(box['inertia_kg_m2']))];holes=[]
            for cx,positive in ((start,True),(end,False)):
                if (positive and j==0) or (not positive and j==len(bounds)-2):continue
                vol=.5*math.pi*radius**2*h;mass=vol*rho;off=4*radius/(3*math.pi);c=np.array([cx+(off if positive else -off),yc,z+h/2]);var=np.array([radius**2/4-off**2,radius**2/4,h*h/12]);I=mass*(np.eye(3)*sum(var)-np.diag(var));terms.append((-mass,c,I))
                holes.append(dict(axis='z',diameter_m=2*radius,x_m=float(cx-start),y_m=radius,length_m=h,partial_intersection_fraction=.5))
            mass=sum(v[0] for v in terms);cg=sum(m*c for m,c,I in terms)/mass;inertia=np.zeros((3,3))
            for mm,c,I in terms:
                delta=c-cg;inertia+=(1 if mm>0 else -1)*I+mm*(np.eye(3)*np.dot(delta,delta)-np.outer(delta,delta))
            box.update(mass_kg=mass,volume_m3=mass/rho,cg_m=cg.tolist(),inertia_kg_m2=inertia.tolist(),holes=holes,
                geometry_note='Two actual half-cylinder boundary pockets. Native Boolean intersection required; subtracting whole cylinder volume twice is incorrect.')
            parts.append(box)
    base=deepcopy(a);base['propulsion_band']['thickness_m']=q['depth_m']
    parts.extend(p for p in _halbach_band(base)['parts'] if not p['id'].split('/')[-1].startswith('ferrite-'))
    return dict(parts=parts,mass_kg=sum(p['mass_kg'] for p in parts),period_m=q['period_m'],pole_pitch_m=q['period_m']/2,length_m=L,
        active_height_m=h,thickness_m=q['depth_m'],bands=2,manufacturing_disc_count=len(centrexs)*2*round(h/q['magnet_disc_height_m']),
        magnetization='Alternating tangential+x/−x diametrically magnetized round ferrite discs between concave laminated shoes',
        topology='Round40mm ferrite cross sections eliminate unmodeled PM corner singularities; actual half-circle shoe pockets. Both broad faces included in nonlinear2D solver.',
        attachment_hold='Propulsion-to-cradle transverse webs, end retention, adhesive, clamp fasteners and approved tolerances remain design/physical gates.',physical_accepted=False)


@lru_cache(maxsize=8)
def _identity_cached(tokens):return definition()['configuration_sha256']

def _current_identity():
    return _identity_cached(tuple((str(p),p.stat().st_mtime_ns,p.stat().st_size) for p in (INPUT,PARENT,REPLACED,RETAINED,PROTECTION,ATTACHMENT)))


@lru_cache(maxsize=4)
def _propulsion_calibration(input_sha256):
    coarse=spatial_flux_shoe_coupon(96,24)
    fine=spatial_flux_shoe_coupon(192,48)
    # The failed refinement is applicable evidence and cannot be discarded
    # behind the attractive converged fundamental or a previous passing point.
    return dict(coarse=coarse,fine=fine,accepted=bool(coarse['converged'] and fine['converged'] and fine['conservative_demag_margin_a_m']>0),
        fundamental_refinement_relative=abs(fine['nominal_gap_fundamental_peak_t']-coarse['nominal_gap_fundamental_peak_t'])/fine['nominal_gap_fundamental_peak_t'])


def _propulsion_group_base(group_length_m=5.,*,turns=None,conductor_area_mm2=None):
    """Counted air-core3phase winding specification; end routing remains held.

    Four-turn high-current variant fits actual slot copper. 3D dogleg endturns
    retreat behind the common active face, rather than giving each phase a
    different magnetic gap. Mean length includes the extra end routing.
    """
    a=load();b=a['propulsion_band'];q=a['propulsion_flux_shoe'];N=b['wayside_turns'] if turns is None else turns;area=b['wayside_conductor_area_mm2'] if conductor_area_mm2 is None else conductor_area_mm2
    if type(N)is not int or not 1<=N<=24 or not math.isfinite(area) or not 20<=area<=500 or not 0<group_length_m<=25:raise ValueError('bounded actual group winding required')
    period=q['period_m'];coils_per_phase_per_side=group_length_m/period;H=q['height_m'];mean=2*H+period+.12+.12
    phase_length=2*coils_per_phase_per_side*N*mean;cu=a['materials']['copper'];copper_mass=3*phase_length*area*1e-6*cu['density_kg_m3']
    slot_width=.035;active_depth=.030;slot_fill=N*area*1e-6/(slot_width*active_depth)
    packfit=slot_fill<=a['coil_fill_limit'] and b['wayside_coil_depth_m']>=.10
    k=2*math.pi/period;shape=lambda x:2*(x-1+math.exp(-x))/(x*x)
    # All spatial harmonics of an insulated finite-width current slot contribute
    # stored armature field energy; no arbitrary borrowed old inductance.
    harmonic_energy=sum(float(np.sinc(n*slot_width/period))**2/n*shape(n*k*active_depth) for n in range(1,64) if n%2 and n%3)
    inductance=2*MU0*(6*N/period)**2*group_length_m*H/(6*k)*harmonic_energy
    return dict(schema='osr-dimensioned-wayside-winding/1',configuration_sha256=_current_identity(),group_length_m=group_length_m,
        period_m=period,pole_pitch_m=period/2,physical_sides=2,phases=3,turns=N,conductor_area_mm2=area,
        coils_per_phase_per_side=coils_per_phase_per_side,physical_coil_count=6*coils_per_phase_per_side,
        conductor_length_m_per_phase=phase_length,total_conductor_length_m=3*phase_length,copper_mass_kg=copper_mass,
        coil_mean_turn_length_m=mean,active_height_m=H,active_slot_width_m=slot_width,active_normal_depth_m=active_depth,
        full_pack_normal_depth_m=b['wayside_coil_depth_m'],slot_copper_fill=slot_fill,pack_fit=packfit,
        face_abs_y_m=b['wayside_coil_face_abs_y_m'],active_normal_mid_abs_y_m=b['wayside_coil_face_abs_y_m']-active_depth/2,
        band_force_z_m=b['top_z_m']-H/2,coil_inner_m=[period/2,H],coil_outer_m=[period/2+.06,H+.06],
        phase_resistance_20c_ohm=phase_length*cu['resistivity_20c_ohm_m']/(area*1e-6),dq_inductance_h=inductance,
        maximum_phase_peak_current_a=b['wayside_current_screen_a'],dc_bus_v=b['wayside_bus_v'],
        geometry_ids=[f'wayside/phase-{phase}/side-{side}/coil-{j}' for side in (-1,1) for phase in range(3) for j in range(math.ceil(coils_per_phase_per_side))],
        winding_model='Balanced distributed3phase full-pitch coils; finite slot width/depth Fourier armature field energy.3D phase endturns/leakage and measured impedance remain held.',
        manufacturing_holds=['Exact3D dogleg endturn/lead/insulation routing and mutual impedance require native clearance and prototype tests.',
            'Non-whole-period end groups need explicit cut-coil/endturn schedule; fractional coil count is an allocation, never a manufactured fractional coil.',
            '1350A current stage, cooling and2400V insulation are priced/rated allocations requiring actual supplier design.'],**FLAGS)


def propulsion_group_map(car_centres_m,car_speeds_m_s,gap_m,groups,currents_alpha_beta_a,temperature_c=40.,*,copper_temperature_c=80.):
    """Reciprocal source-linked fundamental/harmonic group/car map.

    λcomplex=λalpha+iλbeta; coenergy=1.5Re(I*conj(λ)). Forcex and
    side-normal force use exact derivatives of this SAMEcoenergy, including
    finite-band overlap derivatives. Gaps are clear-air mechanical gaps; the1mm front cover is added inside. Side0=worldleft
    (+yband), side1=worldright. Normalpositive pulls that band towardbeam.
    """
    a,v,m,*_=_runtime(None);b=a['propulsion_band'];q=a['propulsion_flux_shoe'];x=np.asarray(car_centres_m,float);speed=np.asarray(car_speeds_m_s,float);g=np.asarray(gap_m,float);current=np.asarray(currents_alpha_beta_a,float)
    if x.ndim!=1 or speed.shape!=x.shape or not 1<=len(x)<=6 or not np.isfinite(x).all() or not np.isfinite(speed).all():raise ValueError('one through six finite car poses required')
    if g.shape==(len(x),):g=np.repeat(g[:,None],2,axis=1)
    if g.shape!=(len(x),2) or not np.isfinite(g).all() or np.any(g<=0):raise ValueError('positive per-car two-side magnetic gaps required')
    if not 1<=len(groups)<=200 or current.shape!=(len(groups),2) or not np.isfinite(current).all():raise ValueError('bounded actual group currents required')
    temp=np.asarray(temperature_c,float)
    if temp.ndim==0:temp=np.full(len(x),temp)
    if temp.shape!=x.shape or not np.isfinite(temp).all():raise ValueError('finite scalar/per-car magnet temperature required')
    g=g+b['front_cover_m']
    source=_propulsion_calibration(digest(INPUT));fine=source['fine'];coeff=np.array([complex(*z) for z in fine['surface_normal_fourier_t']]);period=q['period_m'];k0=2*math.pi/period
    scale=(1+a['materials']['ferrite']['br_temperature_coefficient_per_k']*(temp-20))/(1+a['materials']['ferrite']['br_temperature_coefficient_per_k']*20)
    G=len(groups);C=len(x);lam=np.zeros((G,C,2),complex);dxlam=lam.copy();dglam=lam.copy();R=[];L=[];kg=[];caps=[];limits=[];pack=[]
    for j,group in enumerate(groups):
        start=float(group['start_m']);end=float(group['end_m'])
        if not math.isfinite(start+end) or not 0<end-start<=25:raise ValueError('bounded finite powered group extent required')
        wind=_group_cached(end-start,INPUT.stat().st_mtime_ns);N=wind['turns'];H=wind['active_height_m'];depth=wind['active_normal_depth_m'];R.append(wind['phase_resistance_20c_ohm']*(1+a['materials']['copper']['resistance_temperature_coefficient_per_k']*(copper_temperature_c-20)));L.append(wind['dq_inductance_h']);kg.append(wind['copper_mass_kg']);caps.append(wind['copper_mass_kg']*a['materials']['copper']['specific_heat_j_kg_k']);limits.append(wind['maximum_phase_peak_current_a']);pack.append(wind['pack_fit'])
        left=np.maximum(start,x-q['length_m']/2);right=np.minimum(end,x+q['length_m']/2);overlap=np.maximum(0.,right-left)
        dlength=np.where(overlap>0,(x+q['length_m']/2<end).astype(float)-(x-q['length_m']/2>start).astype(float),0.)
    starts=np.array([v['start_m'] for v in groups],float);ends=np.array([v['end_m'] for v in groups],float)
    left=np.maximum(starts[:,None],x[None,:]-q['length_m']/2);right=np.minimum(ends[:,None],x[None,:]+q['length_m']/2)
    overlap=np.maximum(0.,right-left)
    dlength=np.where(overlap>0,(x[None,:]+q['length_m']/2<ends[:,None]).astype(float)-(x[None,:]-q['length_m']/2>starts[:,None]).astype(float),0.)
    indices=np.array([n for n in range(1,len(coeff)+1) if n%2 and n%3]);k=indices*k0;sense=np.where(indices%3==1,1.,-1.)
    factor=4*b['wayside_turns']*q['height_m']*np.sin(indices*math.pi/2)/(k*period)*coeff[indices-1]*np.exp(1j*k*period/4)*np.sinc(indices*.035/period)
    factor=np.where(sense>0,np.conj(factor),factor);depth=.030
    attenuation=np.exp(-k[:,None,None]*g[None,:,:])*((1-np.exp(-k*depth))/(k*depth))[:,None,None]
    phase=np.exp((sense*1j*k)[None,:,None]*(x[None,None,:]-starts[:,None,None]))
    wave=factor[None,:,None,None]*scale[None,None,:,None]*attenuation[None,:,:,:]*phase[:,:,:,None]
    term=overlap[:,None,:,None]*wave
    lam=np.sum(term,axis=1)
    dxlam=np.sum((dlength[:,None,:,None]+(sense*1j*k)[None,:,None,None]*overlap[:,None,:,None])*wave,axis=1)
    dglam=np.sum(-k[None,:,None,None]*term,axis=1)
    total=lam.sum(axis=2);derivative=dxlam.sum(axis=2);I=current[:,0]+1j*current[:,1]
    fx=1.5*np.real(I[:,None]*np.conj(derivative));normal=-1.5*np.real(I[:,None,None]*np.conj(dglam));forceleft=normal[:,:,1]-normal[:,:,0]
    coenergy=1.5*np.real(I[:,None]*np.conj(total));emf=derivative*speed[None,:]
    # Mandatory known finest-grid demagnetization failure disqualifies EVERY
    # downstream adoption; it cannot be hidden behind a converged force map.
    NI=np.max(np.abs(I))*b['wayside_turns'];armature_h_bound=3*NI/period
    margin=fine['conservative_demag_margin_a_m']-armature_h_bound
    domain=bool(np.all((g>=.002)&(g<=.030)) and np.all((temp>=0)&(temp<=80)))
    numeric=bool(fine['converged'] and all(pack));accepted=bool(source['accepted'] and numeric and domain and margin>0 and np.all(np.abs(I)<=limits))
    return dict(configuration_sha256=_current_identity(),psi_wb=np.abs(total),theta_rad=np.angle(total),lambda_wb=total,lambda_side_wb=lam,
        dpsi_dx_wb_m=derivative,dpsi_dgap_wb_m=dglam.sum(axis=2),dpsi_dgap_side_wb_m=dglam,
        emf_wb_s=emf,force_x_n=fx,normal_side_n=normal,leftward_n=forceleft,coenergy_j=coenergy,
        group_R_ohm=np.array(R),group_L_h=np.array(L),group_copper_mass_kg=np.array(kg),group_thermal_capacity_j_k=np.array(caps),group_current_limit_a=np.array(limits),
        electrical_wavelength_m=period,band_force_z_m=b['top_z_m']-q['height_m']/2,nominal_air_gap_m=a['nominal_gap_m'],cover_m=b['front_cover_m'],
        field_numerically_converged=numeric,accepted_for_simulation=accepted,domain_valid=domain,demag_margin_after_armature_bound_a_m=margin,
        applicability_hold='Known finest-grid opposing-field/demagnetization failure prevents propulsion adoption. Force values are conditional undamaged linear-recoil diagnostic maps, not qualified operating capacity.',
        source_field_refinement_relative=source['fundamental_refinement_relative'],**FLAGS)


@lru_cache(maxsize=256)
def _group_cached(length,input_mtime):return propulsion_group_definition(length)


def numerical_controls():
    gaps=np.array([[.007,.010,.009,.012]]);current=np.array([[35.,9.]])
    r=evaluate_batch(gaps,current);L=r['incremental_inductance_h'][0];epsilon=1e-7;force_errors=[]
    for axis in range(4):
        delta=np.zeros((1,4));delta[0,axis]=epsilon
        numeric=-(evaluate_batch(gaps+delta,current)['coenergy_j'][0]-evaluate_batch(gaps-delta,current)['coenergy_j'][0])/(2*epsilon)
        force=r['branch_lift_force_n'][0,axis%2] if axis<2 else r['branch_guidance_force_n'][0,axis%2]
        force_errors.append(abs(numeric-force)/max(1.,force))
    zero=evaluate_batch([[.008]*4],[[0,0]],pm_enabled=False);pm=evaluate_batch([[.008]*4],[[0,0]])
    displaced=evaluate_batch([[.008,.008,.007,.009]],[[40,0]])
    return dict(zero_excitation_force_n=float(zero['upward_n'][0]),zero_excitation_energy_j=float(zero['stored_energy_j'][0]),pm_bias_force_n=float(pm['upward_n'][0]),
        maxwell_vs_coenergy_relative_errors=force_errors,inductance_symmetric=bool(np.allclose(L,L.T,atol=1e-12)),minimum_incremental_inductance_eigenvalue_h=float(np.linalg.eigvalsh(L).min()),
        passive_lateral_displacement_destabilizes=bool(displaced['leftward_n'][0]>0),
        passed=bool(max(force_errors)<1e-4 and zero['upward_n'][0]<1e-9 and zero['stored_energy_j'][0]<1e-9 and np.linalg.eigvalsh(L).min()>0 and np.allclose(L,L.T,atol=1e-12)))


def study():
    before=sources();d=definition();variants=variant_study();controls=numerical_controls();calibration=_propulsion_calibration(digest(INPUT))
    halbach=[spatial_band_coupon(64,16),spatial_band_coupon(128,32)]
    round_cases=[spatial_flux_shoe_coupon(64,16,pm_shape='round-transverse'),spatial_flux_shoe_coupon(128,32,pm_shape='round-transverse')]
    value=dict(schema='osr-candidate-magnetic-study/1',configuration_sha256=d['configuration_sha256'],parent_configuration_sha256=d['parent_configuration_sha256'],
        selected_variant=d['variant_id'],controlled_tare_kg=d['controlled_tare_kg'],controlled_aw3_kg=d['controlled_aw3_kg'],mass_properties=d['mass_properties'],
        variant_comparison=variants,numerical_controls=controls,network_field_map=field_map(),
        spatial_field_coupons=dict(halbach=halbach,rectangular_flux_shoe=[calibration['coarse'],calibration['fine']],round_flux_shoe=round_cases),
        propulsion=dict(accepted_for_simulation=calibration['accepted'],field_refinement_relative=calibration['fundamental_refinement_relative'],
            known_mandatory_failure='Finest applicable PM opposing-field/demag screen fails. Round repair also fails nonlinear convergence. No current/force/thermal result can erase these failures.',
            current_geometry='rectangular alternating ferrite/laminated shoes',halback_alternative_rejected=True,round_alternative_rejected=True),
        guideway=guideway_definition(),wayside_group=propulsion_group_definition(),
        propulsion_alternative_geometry=dict(halbach=_halbach_band(load()),rectangular_flux_shoe=d['propulsion_band'],round_flux_shoe=_round_propulsion_band(load())),
        complete_system_feasible=False,study_pass=False,open_gates=d['holds']+['Known stationary-rail saturation/support infeasibility and propulsion demagnetization failures must be redesigned and retested before adoption.','Lift/guidance reluctance network has energy/reciprocity controls; independent full3D spatial/physical force maps are not yet available.'],
        stationary_return_area_correction=dict(previous_incorrect_area_basis='pole face x×100mm',actual_flux_cross_section='laminated flange/web x×25mm',incorrect_to_actual_area_ratio=4,rail_b_included_in_validity=True),
        scope='Defined geometry and counted common candidate; provisional numerical studies with retained failed alternatives. No manufacturing/site/operating release.',source_sha256=before,**FLAGS)
    if sources()!=before:raise ValueError('magnetic study sources changed during execution')
    return value


def module_drawing(d):
    """Code-native orthographic drawing from actual stock, never AI geometry."""
    from html import escape
    parts=d['module']['parts'];out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="690" viewBox="0 0 1100 690"><rect width="1100" height="690" fill="#101827"/><g font-family="sans-serif" fill="#eef4fc"><text x="24" y="30" font-size="22">Dimensioned two-circuit magnetic module · transverse Y/Z</text><text x="24" y="54" font-size="14">Actual defined stock; contacts, tolerances and manufacturing acceptance remain open.</text>']
    scale=600.;origin=np.array([420.,365.]);colours={'new-core':'#9aa8be','new-ferrite':'#d28162','new-winding':'#e1ae4c','new-cooling':'#6aa6c7','new-housing':'#5a9e97','new-insulation':'#c4b981','new-lowered-module-attachment':'#8e96a5'}
    for p in sorted(parts,key=lambda v:v['at_m'][0]):
        at=np.array(p['at_m']);sz=p['size_m'];y=origin[0]+at[1]*scale;z=origin[1]-(at[2]+sz[2])*scale
        out.append(f'<rect x="{y:.3f}" y="{z:.3f}" width="{sz[1]*scale:.3f}" height="{sz[2]*scale:.3f}" fill="{colours.get(p["component_scope"],"#a7b9c6")}" fill-opacity=".60" stroke="#e9eef6" stroke-width=".45"><title>{escape(p["id"])}</title></rect>')
    out+=['<path d="M180 630 H660 M180 623 V637 M660 623 V637" fill="none" stroke="white"/><text x="340" y="653" font-size="15">800 mm core-return width</text>',
        '<text x="755" y="107" font-size="18">Defined interfaces</text>',f'<text x="755" y="138" font-size="14">Pole face {d["module"]["lift_pole_area_m2"]*1e6:.0f} mm² each</text>',
        '<text x="755" y="166" font-size="14">Lift pole centres y = ±150 mm</text><text x="755" y="194" font-size="14">Guidance faces y = ±400 mm</text><text x="755" y="222" font-size="14">Nominal mechanical gaps 8 mm</text>',
        f'<text x="755" y="250" font-size="14">Datum z = {d["module_placements_m"][0][2]*1000:.0f} mm below floor</text>',
        f'<text x="755" y="278" font-size="14">Module incl. attachment {d["module"]["mass_kg"]:.2f} kg</text>',
        '<text x="755" y="320" font-size="14">One lift coil, two opposed guide coils</text><text x="755" y="348" font-size="14">Two PM banks; actual shared stem</text><text x="755" y="392" font-size="13">Colour: steel / ferrite / winding / cooling</text>',
        '<text x="24" y="680" font-size="12">Orthographic projection can hide x separation; inspect exact model and independent3D interference evidence.</text></g></svg>']
    return ''.join(out).encode()


def band_drawing(d):
    band=d['propulsion_band'];out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="420" viewBox="0 0 1100 420"><rect width="1100" height="420" fill="#101827"/><g font-family="sans-serif" fill="#eef4fc"><text x="25" y="35" font-size="22">Dedicated passive propulsion band · four explicit periods</text><text x="25" y="62" font-size="14">Alternating tangentially magnetized ferrite and laminated shoes; current geometry fails demag screen.</text>']
    for p in band['parts']:
        if not p['id'].startswith('propulsion/1/') or not ('shoe-' in p['id'] or 'ferrite-' in p['id']):continue
        x=p['at_m'][0]+band['length_m']/2
        if x>=1:continue
        colour='#d28162' if 'ferrite-' in p['id'] else '#94a5be'
        out.append(f'<rect x="{40+x*950:.2f}" y="105" width="{p["size_m"][0]*950:.2f}" height="120" fill="{colour}" stroke="#fff" stroke-width=".6"/>')
        vector=p.get('magnetization_vector')
        if vector:
            cx=40+(x+p['size_m'][0]/2)*950;direction=vector[0];out.append(f'<path d="M{cx-15*direction} 165 H{cx+15*direction} l{-7*direction} -5 m{7*direction} 5 l{-7*direction} 5" stroke="#101827" stroke-width="2" fill="none"/>')
    out+=['<text x="40" y="255" font-size="15">250 mm electrical period · 125 mm pole pitch · 40 mm depth · 200 mm active height</text>',f'<text x="40" y="286" font-size="15">Two ×12 m bands: counted material {band["mass_kg"]:.1f} kg/car. No inherited ferrite credit.</text>',
        '<text x="40" y="325" font-size="14">Field coupons: Halbach rejected; rectangular shoes demag hold; round repair convergence/demag hold.</text>',
        '<text x="40" y="359" font-size="14">This drawing is a geometric design record. It does not demonstrate safe retention or useful operating capacity.</text></g></svg>']
    return ''.join(out).encode()


def assembly_drawing(d):
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="350" viewBox="0 0 1100 350"><rect width="1100" height="350" fill="#101827"/><g fill="#eef4fc" font-family="sans-serif"><text x="22" y="32" font-size="21">Proposed assembly order · final-position stock illustration</text>']
    steps=[('1 Core+PM restraint',['new-core','new-ferrite']),('2 Bobbins+guide winding',['new-winding']),('3 Cooling+insulation',['new-cooling','new-insulation']),('4 Cradle+serial QA',['new-lowered-module-attachment'])]
    for i,(label,scopes) in enumerate(steps):
        ox=135+i*270;scale=210
        for p in d['module']['parts']:
            if p['component_scope'] not in scopes:continue
            at=p['at_m'];size=p['size_m'];out.append(f'<rect x="{ox+at[1]*scale:.2f}" y="{180-(at[2]+size[2])*scale:.2f}" width="{size[1]*scale:.2f}" height="{size[2]*scale:.2f}" fill="#87a8bd" stroke="#e9f3ff" stroke-width=".4"/>')
        out.append(f'<text x="{i*270+22}" y="285" font-size="14">{label}</text>')
    out.append('<text x="22" y="326" font-size="13">Sequence illustration only; not a continuous-motion, collision, tolerance, magnet-handling or lifting simulation.</text></g></svg>')
    return ''.join(out).encode()


OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/candidate-magnetics'
FILES={'definition.json.gz','study.json.gz','module.svg','propulsion-band.svg','assembly-sequence.svg','manufacturing-bom.csv','README.md'}
MAX_FILE=32*1024*1024
MAX_RAW=128*1024*1024


def _read(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary magnetic evidence required')
    return p.read_bytes()


def _inflate(raw):
    import gzip,io
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:value=stream.read(MAX_RAW+1)
    if len(value)>MAX_RAW:raise ValueError('bounded magnetic payload required')
    return json.loads(value)


def _readme(s):
    return ('# Dimensioned magnetic circuits and passive propulsion alternatives\n\n'
        'Provisional common candidate '+s['configuration_sha256']+'. Parent94ad remains historical evidence.\n\n'
        f"Counted tare {s['controlled_tare_kg']:.3f} kg/car; AW3 {s['controlled_aw3_kg']:.3f} kg/car, six cars. "
        'Only exact old cartridge/winding scopes are removed. New cores, ferrite, windings, cradle, protection and propulsion stock are counted.\n\n'
        'Lift/guidance: four actual air gaps, shared nonlinear steel stem, two PM branches and three physical coils/two electrical circuits. '
        'Typical manufacturer material curves, PM recoil/operating points, differential mutual inductance, force/coenergy reciprocity and conditional repeated cooling are implemented. '
        'Independent complete3D lift/guidance maps remain open.\n\n'
        'Propulsion: executed independent2D magnetostatic coupons retain Halbach, rectangular-shoe and round-PM alternatives. '
        '**The corrected25mmreturn-rail cross-section prevents the assumed AW3 support; no propulsion alternative passes all applicable field/demagnetization/convergence screens.** '
        'The group map returns conditional undamaged-field diagnostics and refuses adoption. New slot/turn/current/copper/thermal quantities are counted; phase end routing and impedance remain unqualified.\n\n'
        '[Common geometry/mass/CG/inertia](definition.json.gz) · [Executed studies and failures](study.json.gz) · [Module](module.svg) · '
        '[Propulsion band](propulsion-band.svg) · [Assembly illustration](assembly-sequence.svg) · [Cut/material/process BOM](manufacturing-bom.csv) · [Receipt](manifest.json)\n\n'
        'Core curve: [SIJ](https://cms.sij.si/storage/1399/SIWATT-M400-50A-HP.pdf). Ferrite: '
        '[TDK FB9B/recoil guide](https://product.tdk.com/info/en/catalog/datasheets/magnet_fb_summary_en.pdf) and '
        '[FB12H](https://product.tdk.com/en/search/magnet/magnet/ferrite/info?part_no=FB12H). '
        'UK cut/stack and winding candidates: [H V Wooding](https://www.hvwooding.co.uk/services/motor-stator-laminations/), '
        '[Brandauer](https://brandauer.co.uk/services/electrical-steel-laminations/), [Trans-Tronic](https://trans-tronic.co.uk/). '
        'UK manufacture of those processes does not establish British origin of steel/ferrite/conductor or a supplier quotation.\n\n'
        'No manufacturing, engineering, physical, site or operating release is claimed.\n').encode()


def publish(output=OUTPUT):
    import csv,gzip,io
    before=sources();s=study();d=definition();stream=io.StringIO();rows=d['manufacturing_bom'];columns=['id','component_scope','quantity_per_module','quantity_per_car','unit','net_material_quantity','purchase_quantity','waste_fraction','unit_rate_usd','extended_cost_usd','mass_kg','process','lead_time_days','origin_basis'];writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    payload={'definition.json.gz':gzip.compress(encoded(d),mtime=0),'study.json.gz':gzip.compress(encoded(s),mtime=0),'module.svg':module_drawing(d),'propulsion-band.svg':band_drawing(d),'assembly-sequence.svg':assembly_drawing(d),'manufacturing-bom.csv':_bom_csv(d),'README.md':_readme(s)}
    if sources()!=before:raise ValueError('magnetic sources changed before publication')
    out=Path(output)
    if out.is_symlink():raise ValueError('owned ordinary magnetic packet required')
    out.mkdir(parents=True,exist_ok=True)
    if set(p.name for p in out.iterdir())-FILES-{'manifest.json'} or any(p.is_symlink() for p in out.iterdir()):raise ValueError('magnetic packet inventory differs')
    for name,raw in payload.items():
        if len(raw)>MAX_FILE:raise ValueError('bounded magnetic packet file required')
        pending=out/(name+'.pending');pending.write_bytes(raw);pending.replace(out/name)
    manifest=dict(schema='osr-candidate-magnetics-publication/1',configuration_sha256=d['configuration_sha256'],source_sha256=before,files_sha256={k:sha256(v).hexdigest() for k,v in payload.items()},**FLAGS)
    (out/'manifest.json').write_bytes(encoded(manifest));return verify(out)


def verify(output=OUTPUT):
    out=Path(output)
    if out.is_symlink() or set(p.name for p in out.iterdir())!=FILES|{'manifest.json'}:raise ValueError('magnetic evidence inventory differs')
    manifest=json.loads(_read(out/'manifest.json'))
    if manifest.get('schema')!='osr-candidate-magnetics-publication/1' or manifest['source_sha256']!=sources() or set(manifest['files_sha256'])!=FILES or any(manifest.get(k)is not False for k in FLAGS):raise ValueError('magnetic evidence sources/schema/release flags differ')
    for name,h in manifest['files_sha256'].items():
        if sha256(_read(out/name)).hexdigest()!=h:raise ValueError('magnetic evidence checksum differs')
    d=_inflate(_read(out/'definition.json.gz'));s=_inflate(_read(out/'study.json.gz'))
    if d!=definition() or d['configuration_sha256']!=manifest['configuration_sha256'] or s['configuration_sha256']!=d['configuration_sha256'] or s['source_sha256']!=sources():raise ValueError('magnetic candidate identity/definition differs')
    if any(s.get(k)is not False for k in FLAGS) or s.get('complete_system_feasible')is not False or s.get('study_pass')is not False or s['propulsion'].get('accepted_for_simulation')is not False:raise ValueError('known-failed magnetic candidate cannot be promoted')
    for key in ('controlled_tare_kg','controlled_aw3_kg','parent_configuration_sha256'):
        if s.get(key)!=d[key]:raise ValueError('magnetic report mass/parent claim differs')
    if s['selected_variant']!=d['variant_id'] or s['mass_properties']!=d['mass_properties']:raise ValueError('magnetic report selected geometry/mass properties differ')
    if s['open_gates']!=d['holds']+['Known stationary-rail saturation/support infeasibility and propulsion demagnetization failures must be redesigned and retested before adoption.','Lift/guidance reluctance network has energy/reciprocity controls; independent full3D spatial/physical force maps are not yet available.']:raise ValueError('magnetic outstanding gates differ')
    if _read(out/'manufacturing-bom.csv')!=_bom_csv(d):raise ValueError('magnetic purchasing schedule differs from definition')
    if s['network_field_map']!=field_map():raise ValueError('magnetic network field map differs')
    controls=numerical_controls()
    if s['numerical_controls']!=controls or not controls['passed']:raise ValueError('magnetic energy/reciprocity controls differ')
    # Recompute the decisive independent spatial field, not only its hash.
    current=_propulsion_calibration(digest(INPUT));expected=[current['coarse'],current['fine']]
    if s['spatial_field_coupons']['rectangular_flux_shoe']!=expected:raise ValueError('retained selected spatial field differs from actual execution')
    if s['variant_comparison']!=variant_study():raise ValueError('magnetic variant/mass/cost/thermal comparison differs')
    if s['guideway']!=guideway_definition() or s['wayside_group']!=propulsion_group_definition():raise ValueError('magnetic rail/drive quantities differ')
    if _read(out/'module.svg')!=module_drawing(d) or _read(out/'propulsion-band.svg')!=band_drawing(d) or _read(out/'assembly-sequence.svg')!=assembly_drawing(d) or _read(out/'README.md')!=_readme(s):raise ValueError('magnetic presentation differs from retained geometry/studies')
    return dict(verified=True,configuration_sha256=d['configuration_sha256'],files=len(FILES),sources=len(manifest['source_sha256']),complete_system_feasible=False,**FLAGS)


def read_summary(output=OUTPUT):
    verified=verify(output);s=_inflate(_read(Path(output)/'study.json.gz'))
    return dict(**verified,selected_variant=s['selected_variant'],controlled_tare_kg=s['controlled_tare_kg'],controlled_aw3_kg=s['controlled_aw3_kg'],
        static_comparison_pass=s['variant_comparison']['configured_variant']==s['variant_comparison']['provisional_mass_first_screen_choice'],
        propulsion_accepted_for_simulation=False,propulsion_state='failed-applicable-demagnetization-evidence',
        spatial_alternatives=3,geometry_variants=len(s['variant_comparison']['variants']),numerical_controls_passed=s['numerical_controls']['passed'],
        open_gates=s['open_gates'],scope=s['scope'])


def _bom_csv(d):
    import csv,io
    stream=io.StringIO();columns=['id','component_scope','quantity_per_module','quantity_per_car','unit','net_material_quantity','purchase_quantity','waste_fraction','unit_rate_usd','extended_cost_usd','mass_kg','process','lead_time_days','origin_basis']
    writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(d['manufacturing_bom']);return stream.getvalue().encode()


def propulsion_group_definition(group_length_m=5.,*,turns=None,conductor_area_mm2=None):
    w=_propulsion_group_base(group_length_m,turns=turns,conductor_area_mm2=conductor_area_mm2);a=load();N=w['turns'];area=w['conductor_area_mm2'];H=w['active_height_m'];period=w['period_m'];count=round(group_length_m/period);whole=math.isclose(count*period,group_length_m,abs_tol=1e-9)
    paths=[];phase_lengths=[]
    for phase in range(3):
        total=0.
        for j in range(count if whole else math.ceil(group_length_m/period)):
            centre=(j+.25+phase/3)*period;retreat=((j+phase)%3)*.03;zmid=w['band_force_z_m'];face=w['active_normal_mid_abs_y_m'];lo=centre-period/4;hi=centre+period/4
            nodes=[[lo,face,zmid-H/2],[lo,face,zmid+H/2+.03],[lo,face-retreat,zmid+H/2+.03],[hi,face-retreat,zmid+H/2+.03],[hi,face,zmid+H/2+.03],[hi,face,zmid-H/2-.03],[hi,face-retreat,zmid-H/2-.03],[lo,face-retreat,zmid-H/2-.03],[lo,face,zmid-H/2-.03],[lo,face,zmid-H/2]]
            length=sum(float(np.linalg.norm(np.array(q)-p)) for p,q in zip(nodes,nodes[1:]));total+=length*N*2
            paths.append(dict(id=f'wayside/phase-{phase}/coil-{j}',phase=phase,turns=N,conductor_area_mm2=area,path_one_turn_right_m=nodes,path_one_turn_left_m=[[p[0],-p[1],p[2]] for p in nodes],one_turn_length_m=length,geometry_qualified=False))
        phase_lengths.append(total)
    # Equalize phase resistance using counted extra same-section copper leads.
    equal=max(phase_lengths);extra=[equal-x for x in phase_lengths];cu=a['materials']['copper'];mass=3*equal*area*1e-6*cu['density_kg_m3'];old=w['copper_mass_kg']
    w.update(coils=paths,whole_period_group=whole,phase_active_path_lengths_m=phase_lengths,phase_equalization_lead_lengths_m=extra,conductor_length_m_per_phase=equal,total_conductor_length_m=3*equal,copper_mass_kg=mass,
        phase_resistance_20c_ohm=equal*cu['resistivity_20c_ohm_m']/(area*1e-6),phase_resistance_equalization='Extra same-section copper lead loops counted; routing/inductance remains held.')
    rows=[]
    rows.append(dict(id='wayside/winding-conductor',component_scope='wayside-defined-winding',quantity_per_group=1,unit='metre',net_material_quantity=3*equal,purchase_quantity=3*equal/(1-.08),waste_fraction=.08,unit_rate_usd=area*1e-6*cu['density_kg_m3']*a['procurement']['copper_usd_kg'],extended_cost_usd=3*equal/(1-.08)*area*1e-6*cu['density_kg_m3']*a['procurement']['copper_usd_kg'],mass_kg=mass,geometry_part_ids=[p['id'] for p in paths],process='4turn local insulated copper winding; actual one-turn paths and equalization leads',lead_time_days=60,origin_basis='Raw conductor origin and UK/local winding quote unconfirmed',qa_requirements=['approved conductor/enamel','turn/polarity/hipot/impedance/thermal inspection unexecuted']))
    allocated=[('insulation',.05*mass,10.),('housing',6*group_length_m,5.),('attachment',10*group_length_m,4.5),('coolant',3*group_length_m,5.),('current-stage',45.,100.)]
    for identity,kg,rate in allocated:
        rows.append(dict(id='wayside/'+identity,component_scope='wayside-allocated-'+identity,quantity_per_group=1,unit='kg allocation',net_material_quantity=kg,purchase_quantity=kg,waste_fraction=0.,unit_rate_usd=rate,extended_cost_usd=kg*rate,mass_kg=kg,geometry_part_ids=[],process='Explicit allocated equipment; production configuration and placement missing',lead_time_days=60,origin_basis='Unquoted provisional allowance, not a supplier product',qa_requirements=['detailed part/specification','supplier quotation and qualification']))
    w.update(manufacturing_bom=rows,total_mass_kg=sum(r['mass_kg'] for r in rows),defined_mass_kg=mass,allocated_mass_kg=sum(r['mass_kg'] for r in rows)-mass,
        unquoted_cost_usd=sum(r['extended_cost_usd'] for r in rows),electronic_and_cooling_specification_qualified=False,
        geometry_scope='Actual conductor centrelines and counted cut lengths; turn offsets/bend radii/end routing collisions and cooling remain explicit manufacturing holds. Allocations are not CAD solids or quantity1 fixtures.')
    return w
