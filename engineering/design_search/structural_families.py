"""Hierarchical body-family proposals, supplier-bound cores and model tasks.

Dormant research generators: no existing wheel_body method/default is changed.
Stock is counted; unresolved placement, joining, fire, hot/wet allowables and
new-topology native support are explicit holds. Supplier room-temperature data
are not a rail approval or a complete orthotropic constitutive matrix.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil,pi,prod,isfinite
import json,re,os,subprocess,time,resource
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import encoded,identity,digest

PRODUCER='engineering/design_search/structural_families.py'
PSI=6894.757293168;PCF=16.01846337396
SOURCES={
 'pet':dict(url='https://www.3accorematerials.com/uploads/pdf/TDS-AIREX-T92-E-01.2026-EMEA.pdf',sha256='e020c695b038027bc2370433b7b4c3a1f8f2b6593cc9a8ffce8d0e4c85e48fe6',revision='01.2026 EMEA, GM-TDS-115',pages=[1,2]),
 'pvc':dict(url='https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf',sha256='d4a108dd3be35da9fef378037ddbe92133a7e24b991f5098a3ed0a2882c6e4a4',revision='May2026 rev26 SI',pages=[1,2]),
 'hexweb':dict(url='https://www.hexcel.com/wp-content/uploads/2026/01/HexWebHoneycombAttributesandProperties.pdf',sha256='cecf9aadb972fddcb296f534dea37f5bfabf6273217ba4343be2a3ae17bb65c3',revision='Manufacturer attributes/properties guide',pages=[12,13,14,15,21,26]),
 'aramid':dict(url='https://www.hexcel.com/wp-content/uploads/2025/12/HexWeb_HRH10_DataSheet_eu1.pdf',sha256='2494051ced71e0e533d45cca0b13230447165269a39a7300c823a1bf90192b54',revision='EU product sheet,2017 copyright; current manufacturer download',pages=[3,4]),
}


def material_catalogue():
    def record(grade,rho,ET,GL,GW,sigma,tauL,tauW,temp,source,minimum=None,**extra):
        return dict(grade=grade,density_kg_m3=rho,compression_modulus_T_Pa=ET,shear_modulus_LT_Pa=GL,shear_modulus_WT_Pa=GW,
            compression_strength_bare_Pa=sigma,shear_strength_LT_Pa=tauL,shear_strength_WT_Pa=tauW,
            continuous_temperature_claim_C=temp,properties_basis='Room-temperature nominal/typical supplier values; not structural design allowables',
            minimum_properties_Pa=minimum or {},source_ids=source,price_USD_per_kg=None,rail_fire_acceptance='unknown',
            complete_orthotropic_matrix_available=False,source_test_temperature_C=23.,**extra)
    cores={
      'pet_t92_80':record('AIREX T92.80',85.,75e6,22e6,22e6,1.3e6,.72e6,.72e6,100.,['pet'],
          dict(compression_strength_T=1.1e6,compression_modulus_T=60e6,shear_strength_LT=.65e6,shear_strength_WT=.65e6,shear_modulus_LT=16e6,shear_modulus_WT=16e6),
          chemistry='PET foam',density_range_kg_m3=[80.,90.],cell_size_m=None,test_thickness_m=.020,compression_test='ASTM C365; ISO844 modulus differs and is not substituted',processing_temperature_claim_C=150.),
      'pvc_h80':record('Divinycell H80',80.,90e6,27e6,27e6,1.4e6,1.15e6,1.15e6,70.,['pvc'],
          dict(compression_strength_T=1.15e6,compression_modulus_T=80e6,shear_strength_LT=.95e6,shear_strength_WT=.95e6,shear_modulus_LT=23e6,shear_modulus_WT=23e6),
          chemistry='PVC foam',density_range_kg_m3=[67.,87.],cell_size_m=None,test_thickness_m=None,heat_distortion_temperature_C=125.,processing_temperature_claim_C=90.),
      'al_5052_criii_31':record('HexWeb CR III 1/8-5052-3.1',3.1*PCF,75e3*PSI,45e3*PSI,22e3*PSI,285*PSI,210*PSI,130*PSI,(350-32)*5/9,['hexweb'],
          dict(compression_strength_T=200*PSI,shear_strength_LT=155*PSI,shear_strength_WT=90*PSI),
          chemistry='5052 aluminium honeycomb',density_tolerance_fraction=.10,cell_size_m=.125*.0254,test_thickness_m=.625*.0254,
          raw_source_units=dict(density_pcf=3.1,E_T_ksi=75.,G_LT_ksi=45.,G_WT_ksi=22.,compression_typ_psi=285.,compression_min_psi=200.,shear_LT_typ_psi=210.,shear_LT_min_psi=155.,shear_WT_typ_psi=130.,shear_WT_min_psi=90.,temperature_F=350.)),
      'aramid_hrh10_48':record('HexWeb HRH-10-3.2-48',48.,138e6,41e6,24e6,2.07e6,1.21e6,.69e6,(350-32)*5/9,['aramid','hexweb'],
          chemistry='Aramid paper/phenolic honeycomb',density_tolerance_fraction=.10,cell_size_m=.0032,test_thickness_m=.0127,
          minimum_value_note='Selected EU table is typical only; do not invent guaranteed minima from another grade'),
    }
    return dict(schema='osr-structural-material-catalogue/1',sources=deepcopy(SOURCES),cores=cores,
        axes=dict(L='ribbon/selected panel longitudinal direction',W='in-plane direction perpendicular toL',T='cell/thickness direction normal to skins'),
        warnings=['Honeycomb G_LT and G_WT must not be replaced by isotropic E/(2(1+nu))','Published temperature claims do not validate adhesive or hot-load strength','Honeycomb shear strength depends on specimen thickness; selected coupons do not transfer to arbitrary panel thickness','Price, complete face/joint properties and rail fire/smoke/toxicity evidence remain unknown'])


def default_parameters(family='participating_gfrp_sandwich'):
    if family not in ('aluminium_spaceframe','participating_gfrp_sandwich','hybrid_integral_panels','gfrp_semimonocoque'):raise ValueError('Explicit structural family required')
    return dict(family=family,core_id='pet_t92_80',core_thickness_m=.04,cell_L_axis='x',face_material='balanced_gfrp',
        face_ply_angles_deg=[0,90,90,0],face_ply_thickness_m=.0005,al_face_thickness_m=.001,
        lower_section_m=[.18,.35,.008],roof_section_m=[.10,.25,.0045],floor_crossmember_section_m=[.06,.14,.004],
        crossmember_pitch_m=1.,aperture_frame_wall_m=.004,joint='four_bolt_clamp',joint_overlap_m=.08,bond_thickness_m=.00025,
        hardpoint_insert_size_m=[.15,.12,.04])


def initial_parameters():
    rows=[]
    for family,core in [('aluminium_spaceframe','pvc_h80'),('participating_gfrp_sandwich','pet_t92_80'),('hybrid_integral_panels','al_5052_criii_31'),('gfrp_semimonocoque','aramid_hrh10_48')]:
        p=default_parameters(family);p['core_id']=core
        if family=='aluminium_spaceframe':p['face_material']='aluminium';p['core_thickness_m']=.025
        if core.startswith(('al_','aramid_')):p['core_thickness_m']=.025
        rows.append(p)
    return rows


def campaign_plan():
    return dict(schema='osr-expanded-structural-campaign-plan/1',maximum_candidates=12,maximum_generations=3,initial_families=initial_parameters(),
        hierarchy=['Repair and independently benchmark current lateral/joint model','Select architecture and core/face family','Size members, core, plies, joint pads and hardpoints','Native confirmation and common-mass comparison'],
        candidate_budget_by_generation=[4,4,4],native_dispatch='Only candidates passing definition and conditional necessary bounds, and whose topology adapter/model tasks are ready',
        material_choices=list(material_catalogue()['cores']),native_full_body_ranking_permitted=False,
        objectives=['Complete counted material mass','Installed cost with price coverage explicit','Assembly operations and repair access','All-axis displacement/mode/stress/buckling margins'],**FLAGS)


def _box(name,at,size,rho,material,frame='vehicle'):
    if min(size)<=0:raise ValueError('Positive stock required')
    return dict(id=name,kind='box',at_m=list(at),size_m=list(size),volume_m3=prod(size),mass_kg=prod(size)*rho,density_kg_m3=rho,material=material,frame_id=frame)


def _tube(name,at,length,section,rho=2710.,material='proposed-6082-T6',along='x'):
    b,h,t=section
    if min(b,h,length,t)<=0 or 2*t>=min(b,h):raise ValueError('Positive hollow tube stock required')
    sizes=[(length,t,h),(length,t,h),(length,b-2*t,t),(length,b-2*t,t)];offsets=[(0,0,0),(0,b-t,0),(0,t,0),(0,t,h-t)]
    rows=[]
    for i,(size,off) in enumerate(zip(sizes,offsets)):
        if along=='y':size=(size[1],size[0],size[2]);off=(off[1],off[0],off[2])
        rows.append(_box(name+'/'+str(i),[a+b for a,b in zip(at,off)],size,rho,material))
    return rows


def _validate(p):
    if set(p)!=set(default_parameters()):raise ValueError('Missing or extraneous physical family parameters')
    default_parameters(p['family']);catalogue=material_catalogue()
    if p['core_id'] not in catalogue['cores']:raise ValueError('Unknown supplier grade')
    if p['cell_L_axis'] not in ('x','transverse'):raise ValueError('Explicit cell orientation required')
    if p['face_material'] not in ('balanced_gfrp','aluminium'):raise ValueError('Unknown face construction')
    if p['joint'] not in ('four_bolt_clamp','bonded_edge_splice','co_cured_flange'):raise ValueError('Unknown joint architecture')
    if not .015<=p['core_thickness_m']<=.08 or not .5<=p['crossmember_pitch_m']<=2.:raise ValueError('Outside bounded component family')
    if not p['face_ply_angles_deg'] or min(p['face_ply_thickness_m'],p['al_face_thickness_m'],p['bond_thickness_m'],p['joint_overlap_m'],p['aperture_frame_wall_m'])<=0:raise ValueError('Positive faces/joints required')
    return catalogue['cores'][p['core_id']]


def generate(base_vehicle,parameters):
    """Count proposed replacement stock while retaining real aperture regions.

    This is a candidate definition, not a new accepted vehicle or an adapter for
    unimplemented constitutive models. Hardpoint stock has a local stock frame;
    its installed position/load bypass must be designed before assembly export.
    """
    p=deepcopy(parameters);core=_validate(p);parts=[];removed=set();panels=[]
    face_t=len(p['face_ply_angles_deg'])*p['face_ply_thickness_m'] if p['face_material']=='balanced_gfrp' else p['al_face_thickness_m']
    face_rho=1900. if p['face_material']=='balanced_gfrp' else 2710.
    face_grade='proposed-E-glass-epoxy-'+','.join(map(str,p['face_ply_angles_deg'])) if face_rho==1900 else 'proposed-6082-T6-face'
    thickness=2*face_t+p['core_thickness_m']+2*p['bond_thickness_m']
    source_parts=base_vehicle['geometry_parts']
    regions=[q for q in source_parts if q.get('role')=='panel-side' and '/layer-0/' in q['id']]
    if not regions:raise ValueError('Actual source side-panel aperture regions required')
    for i,q in enumerate(regions):
        side=1 if q['at_m'][1]>0 else -1;x,z=q['at_m'][0],q['at_m'][2];length,height=q['size_m'][0],q['size_m'][2]
        inner=side*1.2803;low=inner if side>0 else inner-thickness;offset=0.;assembly=[]
        for layer,t,rho,grade in [('inner-face',face_t,face_rho,face_grade),('inner-bond',p['bond_thickness_m'],1200.,'proposed-structural-epoxy-density-1200'),('core',p['core_thickness_m'],core['density_kg_m3'],core['grade']),('outer-bond',p['bond_thickness_m'],1200.,'proposed-structural-epoxy-density-1200'),('outer-face',face_t,face_rho,face_grade)]:
            # Mirroring layer ordering does not turn ribbon into thickness axis.
            yy=low+offset if side>0 else inner-offset-t
            stock=_box(f'structural/side/{i}/{layer}',(x,yy,z),(length,t,height),rho,grade);stock['role']='panel-side';stock['cell_axes']=dict(T='y',L=p['cell_L_axis'],W='transverse' if p['cell_L_axis']=='x' else 'x');parts.append(stock);assembly.append(stock['id']);offset+=t
        panels.append(dict(id=f'side/{i}',source_region=q['id'],length_m=length,width_m=height,thickness_m=thickness,part_ids=assembly,aperture_preserved=True))
    removed.update(q['id'] for q in source_parts if q.get('role')=='panel-side')
    # Size the actual lower chord family; four disjoint walls count hollow stock.
    for side in (-1,1):
        b,h,t=p['lower_section_m'];parts.extend(_tube(f'structural/lower/{side}',(-8.5,side*1.1-b/2,.7945-h),17.,[b,h,t]))
    removed.update(q['id'] for q in source_parts if q['id'].startswith('wheel-underframe/sill/'))
    for side in (-1,1):
        b,h,t=p['roof_section_m'];parts.extend(_tube(f'structural/roof-longitudinal/{side}',(-8.4543,side*1.2303-b/2,3.7543-h),16.9086,[b,h,t]))
    removed.update(q['id'] for q in source_parts if '/roof-longitudinal-' in q['id'] and q['id'].startswith('comfort-shell/replacement-frame/'))
    # Count floor crossmembers and preserve all other source assemblies.
    width,depth,wall=p['floor_crossmember_section_m'];count=ceil((17-width)/p['crossmember_pitch_m'])+1
    for i in range(count):
        x=-8.5+width/2+i*(17-width)/(count-1);parts.extend(_tube(f'structural/floor-rib/{i}',(x-width/2,-1.17,.9345-depth),2.34,[width,depth,wall],along='y'))
    removed.update(q['id'] for q in source_parts if '/floor-rib-' in q['id'] and q['id'].startswith('comfort-shell/replacement-frame/'))
    if p['family']=='gfrp_semimonocoque':
        for q in source_parts:
            if q['id'].startswith('comfort-shell/replacement-frame/') and q['id'] not in removed:
                replacement=deepcopy(q);replacement['id']='structural/gfrp-frame/'+q['id'];replacement['source_part_id']=q['id'];replacement['frame_id']='vehicle';replacement['material']='proposed-pultruded-GFRP';replacement['density_kg_m3']=1900.;replacement['mass_kg']=q['volume_m3']*1900.;parts.append(replacement);removed.add(q['id'])
    if p['family'] in ('hybrid_integral_panels','gfrp_semimonocoque'):
        # New repeated floor/roof sandwich cassettes, with counted longitudinal
        # closure members. Their joints and existing-equipment fit are not solved.
        for surface,bottom in [('floor',1.-thickness),('roof',3.7548)]:
            for i in range(8):
                for j in range(3):
                    at=[-8.5+i*2.125,-1.325+j*2.65/3,bottom];offset=0.
                    for layer,t,rho,grade in [('lower-face',face_t,face_rho,face_grade),('bond1',p['bond_thickness_m'],1200.,'proposed-structural-epoxy-density-1200'),('core',p['core_thickness_m'],core['density_kg_m3'],core['grade']),('bond2',p['bond_thickness_m'],1200.,'proposed-structural-epoxy-density-1200'),('upper-face',face_t,face_rho,face_grade)]:
                        q=_box(f'structural/{surface}/{i}/{j}/{layer}',(at[0],at[1],bottom+offset),(2.125,2.65/3,t),rho,grade);q['cell_axes']=dict(T='z',L='x' if p['cell_L_axis']=='x' else 'y',W='y' if p['cell_L_axis']=='x' else 'x');parts.append(q);offset+=t
            for side in (-1,1):parts.extend(_tube(f'structural/{surface}-edge/{side}',(-8.5,side*1.20-.025,bottom-.05),17.,[.05,.05,.003]))
        removed.update(q['id'] for q in source_parts if q['id'].startswith(('comfort-shell/floor/','comfort-shell/roof/')))
    # Stock for inserts, aperture edge closures and joining: counted locally,
    # not silently installed through skins or existing frame material.
    local=[]
    for i in range(4):local.append(_box(f'structural/hardpoint-stock/{i}',(0.,0.,0.),p['hardpoint_insert_size_m'],2710.,'proposed-6082-T6-insert',frame=f'hardpoint-stock/{i}'))
    perimeter=sum(2*(r['length_m']+r['width_m']) for r in panels)
    local.append(_box('structural/panel-edge-closure-stock',(0,0,0),(perimeter,thickness,p['aperture_frame_wall_m']),face_rho,face_grade,frame='edge-stock'))
    bond_area=perimeter*p['joint_overlap_m'];local.append(_box('structural/splice-adhesive-stock',(0,0,0),(bond_area,1.,p['bond_thickness_m']),1200.,'proposed-structural-epoxy-density-1200',frame='joint-stock'))
    # A four-bolt clamp can resist a moment about both panel axes; the previous
    # two-collinear-point idealisation must be diagnosed before using it again.
    pad_count=40;bolt_count=4*pad_count if p['joint']=='four_bolt_clamp' else 0
    if bolt_count:local.append(dict(id='structural/bolt-stock',kind='cylinder-stock',quantity=bolt_count,radius_m=.004,length_m=.12,volume_m3=bolt_count*pi*.004**2*.12,density_kg_m3=7850.,mass_kg=bolt_count*pi*.004**2*.12*7850.,material='proposed-steel-bolt-shanks-only',frame_id='joint-stock'))
    retained=[deepcopy(q) for q in source_parts if q['id'] not in removed];allstock=parts+local
    removed_mass=sum(q['mass_kg'] for q in source_parts if q['id'] in removed);newmass=sum(q['mass_kg'] for q in allstock)
    physical=dict(parent_candidate_id=base_vehicle['candidate_id'],parameters=p,retained_part_ids=[q['id'] for q in retained],replacement_parts=allstock,removed_part_ids=sorted(removed),source_aperture_regions=[r['source_region'] for r in panels])
    candidate=dict(schema='osr-structural-family-proposal/1',candidate_id=identity(physical),physical_definition=physical,parameters=p,retained_geometry_parts=retained,replacement_stock=allstock,
        material_id=p['core_id'],panels=panels,counted_new_material_kg=newmass,counted_removed_material_kg=removed_mass,counted_material_delta_kg=newmass-removed_mass,
        accounted_tare_comparison_kg_per_car=base_vehicle['mass']['accounted_tare_kg_per_car']+newmass-removed_mass,installed_tare_kg_per_car=None,
        local_stock_placement_complete=False,native_topology_adapter_available=False,full_body_ranking_eligible=False,
        missing_stock=['Bolt heads, nuts, washers, preload/retention details and corrosion isolation','Hardpoint load spreaders and skin/core cutouts/closed inserts','Qualified adhesive application, fillets, trim, seals and repairs','Manufacturing waste/tooling/labour and supplier prices'],
        fixed_interfaces=dict(cars=6,body_length_m=17.,normal_people_per_car=46,crowd_control_people_per_car=160,doors_one_side=True,bogie_centres_x_m=[-6.4,6.4]),
        unknowns=['New stock-local frames are not installed CAD; no assembly/clash claim','Generic face/pultrusion and epoxy densities are declared design assumptions, not supplier guarantees','New-family support, aperture stress, buckling, hot/wet/fire, joints and flexible modes unresolved'],
        material_catalogue=material_catalogue(),source_sha256={PRODUCER:digest(__file__)},**FLAGS)
    candidate['definition_id']=identity(candidate);return candidate


def panel_bound(core_id,*,face_E_Pa=69e9,face_thickness_m=.001,core_thickness_m=.025,width_m=.5,span_m=1.,pressure_Pa=5000.,direction='L'):
    c=material_catalogue()['cores'][core_id]
    if direction not in ('L','W') or min(face_E_Pa,face_thickness_m,core_thickness_m,width_m,span_m,pressure_Pa)<=0:raise ValueError('Positive declared beam inputs and cell direction required')
    f=face_thickness_m;t=core_thickness_m;b=width_m;L=span_m;q=pressure_Pa*b
    EI=2*face_E_Pa*b*(f**3/12+f*((t+f)/2)**2)
    G=c['shear_modulus_LT_Pa' if direction=='L' else 'shear_modulus_WT_Pa'];K=G*b*t
    bend=5*q*L**4/(384*EI);shear=q*L**2/(8*K);tau=q*L/(2*b*t)
    strength_key='shear_strength_LT' if direction=='L' else 'shear_strength_WT';strength=c['minimum_properties_Pa'].get(strength_key)
    return dict(EI_faces_N_m2=EI,core_shear_stiffness_N=K,bending_deflection_m=bend,shear_deflection_m=shear,total_deflection_estimate_m=bend+shear,
        core_shear_stress_Pa=tau,guaranteed_shear_strength_Pa=strength,typical_shear_strength_Pa=c['shear_strength_LT_Pa' if direction=='L' else 'shear_strength_WT_Pa'],
        conditional_shear_screen='unknown' if strength is None else 'pass' if tau<=strength/2 else 'fail',
        scope='Perfectly bonded, simply supported uniform-load panel estimate; core in-plane bending ignored and no strength/thickness/temperature transfer accepted')


def necessary_bounds(candidate,*,maximum_core_temperature_C=80.,pressure_Pa=5000.):
    p=candidate['parameters'];c=material_catalogue()['cores'][p['core_id']];face_t=len(p['face_ply_angles_deg'])*p['face_ply_thickness_m'] if p['face_material']=='balanced_gfrp' else p['al_face_thickness_m']
    supported_layup=p['face_material']=='aluminium' or p['face_ply_angles_deg']==[0,90,90,0]
    beam=panel_bound(p['core_id'],face_E_Pa=16.589363017934446e9 if p['face_material']=='balanced_gfrp' else 69e9,face_thickness_m=face_t,core_thickness_m=p['core_thickness_m'],span_m=p['crossmember_pitch_m'],pressure_Pa=pressure_Pa,direction='L' if p['cell_L_axis']=='x' else 'W') if supported_layup else None
    outside=2*(1.2803+2*face_t+p['core_thickness_m']+2*p['bond_thickness_m'])
    limits=dict(side_envelope='pass' if outside<=2.65+1e-9 else 'fail',supplier_continuous_temperature='pass' if maximum_core_temperature_C<=c['continuous_temperature_claim_C'] else 'fail',
        room_temperature_shear=beam['conditional_shear_screen'] if beam else 'unknown',hot_mechanical_properties='unknown',joint_load_transfer='unknown',installed_hardpoints='unknown',full_body_numerical_model='unknown',rail_fire='unknown',price='unknown')
    result=dict(candidate_id=candidate['candidate_id'],execution='completed',necessary_screens=limits,panel_estimate=beam,outer_side_width_m=outside,
        evaluation_inputs=dict(maximum_core_temperature_C=maximum_core_temperature_C,pressure_Pa=pressure_Pa,
            face_constitutive_basis='Reference69GPa aluminium or synthetic25/8GPa balanced crossply; not face material qualification' if supported_layup else 'Unsupported layup: obtain full laminate ABD/coupling before stiffness screen',
            source_sha256={PRODUCER:digest(__file__)},material_sources={name:SOURCES[name]['sha256'] for name in c['source_ids']}),
        price_USD_per_kg=None,next_jobs=['Register topology-specific body adapter','Resolve stock-local hardpoint and splice placements','Correlate face/adhesive properties and core temperature','Close all-axis model tasks before ranking']+([] if supported_layup else ['Calculate and validate full laminate ABD including coupling for proposed layup']),dispatch_native_full_body=False,
        reason='Close current lateral model, install counted local stock and register topology-specific native adapter first',**FLAGS)
    result['evaluation_id']=identity(result);return result


def _read_deck(raw):
    nodes={};elements=[];equations=[];boundaries=[];mode=None;pending=[];terms=None
    for line in raw.splitlines():
        if not line.strip() or line.startswith('**'):continue
        if line.startswith('*'):
            mode='node' if line.upper()=='*NODE' else 'element' if line.upper().startswith('*ELEMENT,TYPE=C3D20,') else 'equation' if line.upper()=='*EQUATION' else 'boundary' if line.upper()=='*BOUNDARY' else None
            pending=[];terms=None;continue
        f=[a.strip() for a in line.split(',') if a.strip()]
        if mode=='node':nodes[int(f[0])]=list(map(float,f[1:4]))
        elif mode=='element':
            pending+=list(map(int,f))
            if len(pending)==21:elements.append(pending);pending=[]
        elif mode=='equation':
            if terms is None:terms=int(f[0])
            else:
                pending+=f
                if len(pending)==3*terms:equations.append([(int(pending[i]),int(pending[i+1]),float(pending[i+2])) for i in range(0,len(pending),3)]);pending=[];terms=None
        elif mode=='boundary':boundaries.append(f)
    return nodes,elements,equations,boundaries


def rigid_pad_rank(points):
    import numpy as np
    p=np.asarray(points,dtype=float);p=p-p.mean(axis=0);rows=[]
    for x,y,z in p:rows.extend([[1,0,0,0,z,-y],[0,1,0,-z,0,x],[0,0,1,y,-x,0]])
    matrix=np.asarray(rows);rank=int(np.linalg.matrix_rank(matrix,tol=1e-10))
    return dict(rank=rank,rigid_body_dofs=6,unconstrained_dofs=6-rank,
        scope='Kinematic rank of ideal point transfers only; no bolt/washer/bond stiffness or capacity')


def model_tasks():
    return [dict(id='SF-MODEL-LOCATE',question='Locate maximum displacement nodes, exact source stock/voids, connected components and supports',completion='Source-bound coordinates/parts and graph/restraint report'),
        dict(id='SF-MODEL-PAD',question='Does each clamp transfer all six rigid motions or behave as a hinge?',completion='Independent two-/four-bolt and finite washer-pad unit-moment fixtures; calibrated stiffness remains separate'),
        dict(id='SF-MODEL-ENERGY',question='Is the lateral mode physical, a restraint issue or a discretisation instability?',completion='All-axis load scaling, strain energy, eigenmode and refinement checks; no ranking on unconverged fields'),
        dict(id='SF-MODEL-COUPON',question='Do known core G_LT/G_WT and sandwich EI/shear responses reproduce independent fields?',completion='Four bounded full-integration native coupons and analytical comparisons'),
        dict(id='SF-MODEL-APERTURE',question='Can finite aperture/edge joints carry shear and torsion without unstable skin compression?',completion='Ply/core/adhesive and geometric-nonlinear aperture subassembly, then whole-body mesh confirmation')]


def diagnose_native(run_directory):
    """Read-only diagnosis of a retained wheel-body case; never repairs receipts."""
    import numpy as np
    folder=Path(run_directory)
    if not(folder/'body.inp').is_file() and(folder/'normal-fine/body.inp').is_file():folder=folder/'normal-fine'
    input_path=folder/'body.inp';dat_path=folder/'body.dat';raw=input_path.read_text();nodes,elements,equations,bc=_read_deck(raw)
    u={};mode=None
    for line in dat_path.read_text().splitlines():
        if 'displacements' in line.lower():mode='u'
        elif 'forces' in line.lower():mode=None
        f=line.split()
        if mode=='u' and len(f)==4 and f[0].isdigit():u[int(f[0])]=list(map(float,f[1:]))
    candidate_path=next((p for p in (folder/'candidate.json',folder.parent/'candidate.json') if p.is_file()),None)
    vehicle=json.loads(candidate_path.read_text()) if candidate_path else None;maxima={}
    for axis,label in enumerate(('longitudinal','lateral','vertical')):
        nid=max(u,key=lambda n:abs(u[n][axis]));xyz=nodes[nid];hits=[]
        for p in vehicle['geometry_parts'] if vehicle else []:
            if p.get('kind') not in ('box','box-with-rectangular-cutouts'):continue
            if all(p['at_m'][j]-1e-8<=xyz[j]<=p['at_m'][j]+p['size_m'][j]+1e-8 for j in range(3)):hits.append(p['id'])
        maxima[label]=dict(node_id=nid,coordinate_m=xyz,displacement_m=u[nid],source_stock_envelope_matches=hits)
    parent={n:n for n in nodes};physical=set()
    def find(n):
        while parent[n]!=n:parent[n]=parent[parent[n]];n=parent[n]
        return n
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    for e in elements:
        physical.update(e[1:])
        for n in e[2:]:join(e[1],n)
    for eq in equations:
        active=[n for n,d,c in eq if abs(c)>1e-12]
        for n in active[1:]:join(active[0],n)
    components={}
    for n in physical:components.setdefault(find(n),0);components[find(n)]+=1
    pads=[]
    for pad in vehicle.get('wheel_body',{}).get('pads',[]) if vehicle else []:
        points=[[x,0.,z] for x,z in pad['bolt_axes']];pads.append(dict(post_id=pad['post_id'],end=pad['end'],**rigid_pad_rank(points)))
    constraints=[]
    for row in bc:
        if row[0].isdigit():constraints.append(dict(node_id=int(row[0]),coordinate_m=nodes[int(row[0])],dofs=[int(row[1]),int(row[2]) if len(row)>2 else int(row[1])],value=float(row[3]) if len(row)>3 else 0.))
    return dict(schema='osr-body-model-diagnosis/1',input_sha256=digest(input_path),dat_sha256=digest(dat_path),
        candidate_id=vehicle.get('candidate_id') if vehicle else None,maxima=maxima,
        graph=dict(physical_solid_nodes=len(physical),solid_elements=len(elements),physical_components=len(components),component_sizes=sorted(components.values(),reverse=True),
            warning='A connected graph is not proof of stiffness rank, stability or correct joint transfer; unused virtual nodes excluded'),
        boundary_conditions=constraints,ideal_pad_rank_histogram={str(rank):sum(p['rank']==rank for p in pads) for rank in sorted({p['rank'] for p in pads})},
        example_pads=pads[:4],local_defect='Two collinear bolt-axis transfers have rank5 and leave local rotation about their line free' if any(p['rank']<6 for p in pads) else None,
        causal_diagnosis_complete=False,reason='Local hinge deficiency is proved, but its causal share of the full-body lateral mode needs unit-moment/eigenmode/energy isolation',
        strain_energy_J=None,full_body_ranking_eligible=False,next_jobs=model_tasks(),**FLAGS)


def _coupon_mesh(xs,ys,zs):
    nodes={};lookup={};elements=[];edges=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))
    def node(p):
        key=tuple(round(x,12) for x in p)
        if key not in lookup:lookup[key]=len(nodes)+1;nodes[lookup[key]]=list(p)
        return lookup[key]
    for i,(a,b) in enumerate(zip(xs,xs[1:])):
        for j,(c,d) in enumerate(zip(ys,ys[1:])):
            for k,(e,f) in enumerate(zip(zs,zs[1:])):
                p=[[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]]
                p += [[(p[a][q]+p[b][q])/2 for q in range(3)] for a,b in edges]
                elements.append(dict(id=len(elements)+1,nodes=[node(q) for q in p],i=i,j=j,k=k,face_area_m2=(d-c)*(f-e)))
    return nodes,elements


def coupon_deck(kind='bending',mesh=20,core_id='al_5052_criii_31'):
    """Four numerical method fixtures; not measured honeycomb or body evidence."""
    core=material_catalogue()['cores'][core_id];shear=kind in ('shear_L','shear_W')
    if kind not in ('bending','shear_L','shear_W'):raise ValueError('Known bounded coupon required')
    if shear:
        L,B,T=.1,.05,core['test_thickness_m'] or .02;xs=[0,L/2,L];ys=[0,B/2,B];zs=[0,T/2,T]
    else:
        if mesh not in (20,40):raise ValueError('Bounded20/40 bending meshes required')
        L,B,T=.4,.05,.02;face=.0005;xs=[L*i/mesh for i in range(mesh+1)];ys=[0,B/2,B];zs=[-.0005,0.,T/2,T,T+.0005]
    nodes,elements=_coupon_mesh(xs,ys,zs);lines=['*HEADING','Source-bound honeycomb constitutive method coupon; SI N-m-Pa','*NODE']+[str(n)+','+','.join(f'{x:.14g}' for x in p) for n,p in nodes.items()]
    groups={}
    for e in elements:
        mat='CORE' if shear or e['k'] in (1,2) else 'FACE';groups.setdefault(mat,[]).append(e)
    for mat,es in groups.items():
        lines.append('*ELEMENT,TYPE=C3D20,ELSET='+mat)
        for e in es:lines += [str(e['id'])+','+','.join(map(str,e['nodes'][:15]))+',',','.join(map(str,e['nodes'][15:]))]
    GL=core['shear_modulus_LT_Pa'];GW=core['shear_modulus_WT_Pa']
    gx,gy=(GW,GL) if kind=='shear_W' else (GL,GW)
    # Unreported E_L/E_W/G_LW and Poisson terms are numerical regularisation,
    # not a supplier property. Shear patches do not depend on these values.
    lines += ['*MATERIAL,NAME=CORE','*ELASTIC,TYPE=ENGINEERING CONSTANTS',f'1000000.,1000000.,{core["compression_modulus_T_Pa"]},0.,0.,0.,1000000.,{gx}',str(gy),
        '*MATERIAL,NAME=FACE','*ELASTIC','69000000000.,.33']
    for mat in groups:lines += [f'*SOLID SECTION,ELSET={mat},MATERIAL={mat}']
    loads={};weights={};boundary=[];force=10.;gamma=1e-4
    if shear:
        for n,(x,y,z) in nodes.items():
            if x in (0.,L) or y in (0.,B) or z in (0.,T):boundary += [f'{n},1,1,{gamma*z:.14g}',f'{n},2,3']
        analytical=dict(expected_top_shear_force_N=gx*L*B*gamma,expected_shear_stress_Pa=gx*gamma,imposed_gamma=gamma,expected_top_displacement_m=gamma*T)
    else:
        clamp=[n for n,p in nodes.items() if p[0]==0.];boundary=[f'{n},1,3' for n in clamp]
        A=B*(T+2*face);face_indices=(1,2,6,5,9,18,13,17)
        for e in elements:
            if e['i']!=mesh-1:continue
            share=e['face_area_m2']/A
            for index,w in zip(face_indices,(-1/12,)*4+(1/3,)*4):
                n=e['nodes'][index];weights[n]=weights.get(n,0.)+share*w;loads[n]=loads.get(n,0.)-force*share*w
        EI=2*69e9*B*(face**3/12+face*((T+face)/2)**2)+1e6*B*T**3/12
        bending=force*L**3/(3*EI);shear_def=force*L/(GL*B*T)
        analytical=dict(EI_N_m2=EI,core_shear_stiffness_N=GL*B*T,expected_bending_m=bending,expected_shear_m=shear_def,expected_tip_work_displacement_m=bending+shear_def,applied_force_N=force,tip_weights=weights)
    lines += ['*BOUNDARY',*boundary,'*NSET,NSET=ALLN']
    ids=sorted(nodes);lines += [','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]+['*STEP','*STATIC']
    if loads:lines += ['*CLOAD']+[f'{n},3,{f:.14g}' for n,f in sorted(loads.items())]
    lines += ['*NODE PRINT,NSET=ALLN','U','*NODE PRINT,NSET=ALLN','RF','*END STEP','']
    definition=dict(kind=kind,core_id=core_id,nodes=nodes,solid_elements=len(elements),mesh_axial=mesh,analytical=analytical,
        source_ids=core['source_ids'],core_axes=dict(L='x' if kind!='shear_W' else 'y',W='y' if kind!='shear_W' else 'x',T='z'),
        unresolved_constitutive_regularisation=dict(E_L_Pa=1e6,E_W_Pa=1e6,G_LW_Pa=1e6,Poisson=0.),
        scope='Independent affine shear or perfect-bond slender sandwich bending/shear fixture; regularised unreported in-plane properties are not a full honeycomb constitutive validation')
    return '\n'.join(lines),definition


def _parse_coupon(path):
    u={};rf={};mode=None
    for line in Path(path).read_text().splitlines():
        if 'displacements' in line.lower():mode=u
        elif 'forces' in line.lower():mode=rf
        f=line.split()
        if mode is not None and len(f)==4 and f[0].isdigit():mode[int(f[0])]=list(map(float,f[1:]))
    if not u or any(not isfinite(x) for row in list(u.values())+list(rf.values()) for x in row):raise ValueError('Missing/nonfinite coupon response')
    return u,rf


def run_coupon_benchmarks(output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable coupon package required')
    output.mkdir(parents=True);source=digest(__file__);results=[]
    for name,mesh in [('shear_L',2),('shear_W',2),('bending',20),('bending',40)]:
        raw,definition=coupon_deck(name,mesh);folder=output/(name+'-'+str(mesh));folder.mkdir();(folder/'coupon.inp').write_text(raw);(folder/'definition.json').write_bytes(encoded(definition))
        def bounded():
            finite=[n for n in resource.getrlimit(resource.RLIMIT_AS) if n!=resource.RLIM_INFINITY];limit=min([1024**3,*finite]);resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
        started=time.monotonic()
        try:
            proc=subprocess.run(['/usr/bin/ccx','coupon'],cwd=folder,capture_output=True,text=True,timeout=55,preexec_fn=bounded,env={**os.environ,'OMP_NUM_THREADS':'1'})
        except subprocess.TimeoutExpired as e:
            (folder/'stdout.log').write_bytes(e.stdout or b'');(folder/'stderr.log').write_bytes(e.stderr or b'');results.append(dict(case=folder.name,execution='interrupted',reason='55second native limit',runtime_s=time.monotonic()-started));continue
        except (OSError,subprocess.SubprocessError) as e:
            (folder/'launch-error.log').write_text(str(e));results.append(dict(case=folder.name,execution='tool_error',reason=str(e),runtime_s=time.monotonic()-started));continue
        (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
        r=dict(case=folder.name,execution='tool_error',returncode=proc.returncode,runtime_s=time.monotonic()-started)
        if not proc.returncode and(folder/'coupon.dat').is_file():
            try:
                u,rf=_parse_coupon(folder/'coupon.dat');ns=definition['nodes'];a=definition['analytical']
                if name.startswith('shear'):
                    top=max(p[2] for p in ns.values());actual=sum(row[0] for n,row in rf.items() if abs(ns[n][2]-top)<1e-10);expected=a['expected_top_shear_force_N'];error=abs(actual-expected)/expected
                    r.update(execution='completed',top_shear_reaction_N=actual,expected_top_shear_reaction_N=expected,relative_error=error,numerical_screen='pass' if error<1e-5 else 'fail',global_force_residual_N=[sum(row[j] for row in rf.values()) for j in range(3)])
                else:
                    actual=-sum(u[int(n)][2]*weight for n,weight in a['tip_weights'].items());expected=a['expected_tip_work_displacement_m'];error=abs(actual-expected)/expected
                    clamp=sum(row[2] for n,row in rf.items() if ns[n][0]==0.);r.update(execution='completed',tip_work_displacement_m=actual,expected_tip_work_displacement_m=expected,relative_error=error,clamp_reaction_z_N=clamp,numerical_screen='pass' if error<.05 and abs(clamp-10)<1e-4 else 'fail')
            except ValueError as e:r.update(execution='numerical_error',reason=str(e))
        results.append(r)
    if source!=digest(__file__):raise ValueError('Coupon producer changed during execution')
    value=dict(schema='osr-structural-core-coupons/1',execution='completed' if all(r['execution']=='completed' for r in results) else 'completed_with_errors',native_cases=4,cases=results,source_sha256={PRODUCER:source},sources=SOURCES,
        scope='Method benchmarks with manufacturer G_LT/G_WT and E_T, synthetic unreported regularisation and reference metal faces; no physical coupon or whole-body acceptance',**FLAGS)
    value['evaluation_id']=identity(value);(output/'result.json').write_bytes(encoded(value));manifest=dict(schema='osr-structural-core-coupon-manifest/1',evaluation_id=value['evaluation_id'],files_sha256={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()},source_sha256=value['source_sha256'],**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return value


def concept_leads():
    """Primary-source leads needing section data, geometry and new adapters."""
    return [dict(id='corrugated-aluminium-sandwich',status='concept-lead',supplier='Metawell',
        url='https://www.metawell.com/en/applications/rail-vehicles/',archived_html_sha256='23cb2c3f1d9b1cb799c5ab189599e62a940c3619e2c836be05b62e4a52d67cc6',
        possible_parts=['floor cassettes','roof/ceiling panels','ducts and access covers'],core_moduli_Pa=None,price_USD_per_m2=None,native_adapter_available=False,
        next_jobs=['Obtain selected corrugation/face geometry and directional EI/shear data','Count adhesive/edge closures/attachments and evaluate hot/wet/fire evidence','Develop orientation-specific corrugated unit cell and panel-joint benchmark']),
        dict(id='hollow-double-skin-aluminium-extrusion',status='concept-lead',supplier='Hydro',
        url='https://www.hydro.com/gb/global/aluminium/products/extruded-profiles/aluminium-extrusions-in-use/modern-trains-and-rail/',archived_html_sha256='c94df907520f2ffc81e68d09b857059e02e03ba50292b43869c743ee46e02cbe',
        possible_parts=['integral roof/floor extrusions','sidewall/cant rails'],core_moduli_Pa=None,price_USD_per_kg=None,native_adapter_available=False,
        next_jobs=['Obtain manufacturable hollow extrusion cross-section, alloy/temper and die limits','Count weld/FSW seams, heat-affected properties, tooling and local repair','Compare whole-panel buckling/torsion and aperture/hardpoint interfaces'])]
