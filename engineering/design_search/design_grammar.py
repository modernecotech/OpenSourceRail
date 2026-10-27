"""Construct component, structural and assembly graphs from production rules.

Five starting recipes exercise shared rules, not five immutable meshes. Layout,
bracing, segmentation, materials and function integration change actual members
and solids. Numerical applicability remains separate from geometry generation.
"""
from copy import deepcopy
from math import ceil,sqrt,isfinite
from functools import lru_cache
from engineering.station_rail.common import encoded,identity,digest
from . import remit

PRODUCER='engineering/design_search/design_grammar.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,manufacturing_release=False,operating_release=False)
RECIPES=('aluminium_spaceframe','gfrp_semimonocoque','hybrid_structural_panels','pultruded_gfrp_frame','modular_segments')


def recipe_registry():
    return {'aluminium_spaceframe':dict(frame='aluminium_reference',shell='skin',ribs='full'),
        'gfrp_semimonocoque':dict(frame='gfrp_axial_research',shell='sandwich',ribs='sparse'),
        'hybrid_structural_panels':dict(frame='aluminium_reference',shell='honeycomb-sandwich',ribs='full'),
        'pultruded_gfrp_frame':dict(frame='gfrp_axial_research',shell='skin',ribs='full'),
        'modular_segments':dict(frame='aluminium_reference',shell='sandwich',ribs='modular')}


def register_recipe(name,productions,registry=None):
    """Compose existing productions without changing the initial family list."""
    registry=deepcopy(recipe_registry() if registry is None else registry)
    if not name or name in registry or set(productions)!=set(('frame','shell','ribs')):raise ValueError('New named explicit production composition required')
    if productions['frame'] not in ('aluminium_reference','gfrp_axial_research') or productions['shell'] not in ('skin','sandwich','honeycomb-sandwich') or productions['ribs'] not in ('full','sparse','modular'):raise ValueError('New production needs geometry/material/assembly and appropriate evaluator implementation')
    registry[name]=deepcopy(productions);return registry


@lru_cache(maxsize=1)
def _reference_equipment():
    from engineering.station_rail import vehicle
    v=vehicle.build();rows=[]
    for r in v['inventory']:
        if r['system'] in ('body','frame-joints','wheel-underframe'):continue
        rows.append(dict(id=r['id'],system=r['system'],mass_kg=r['mass_kg'],component_definition_id=identity(r),basis=r.get('evidence_class','unknown')))
    return v['candidate_id'],rows,v['source_sha256']


def materials():
    return {
        'aluminium_reference':dict(E_Pa=69e9,density_kg_m3=2710.,source_basis='Declared aluminium reference, no lot/HAZ/fatigue allowables',form='RHS/extrusion',full_orthotropic_law=False),
        'gfrp_axial_research':dict(E_Pa=25e9,density_kg_m3=1900.,source_basis='Synthetic axial-only research assumption, not supplier-certified pultrusion',form='pultruded RHS',full_orthotropic_law=False),
        'gfrp_skin_research':dict(E_Pa=None,density_kg_m3=1900.,source_basis='Declared geometry takeoff density only; laminate/ABD and hot/wet/fire/strength absent',form='laminated skin',full_orthotropic_law=False),
        'pet_core_reference':dict(E_Pa=None,density_kg_m3=85.,source_basis='AIREX T92.80 supplier-typical density, not complete material law or allowable',form='foam core',full_orthotropic_law=False),
        'aluminium_core_reference':dict(E_Pa=None,density_kg_m3=49.657238279276,source_basis='HexWeb nominal3.1pcf density only; directional core properties must come from source table',form='honeycomb',full_orthotropic_law=False)}


def parameters(family='aluminium_spaceframe'):
    if family not in RECIPES:raise ValueError('Register a recipe of compatible productions before generation')
    return dict(family=family,length_m=17.,width_m=2.65,cars=6,bay_pitch_m=1.8,frame_depth_m=.55,
        chord_width_m=.10,chord_height_m=.18,chord_wall_m=.006,
        braced=False,integrated_roof=False,modular_length_m=2.5,skin_thickness_m=.002,core_thickness_m=.025)


def _rectangles(x0,x1,z0,z1,cut):
    a,b,c,d=cut;a=max(a,x0);b=min(b,x1);c=max(c,z0);d=min(d,z1)
    if a>=b or c>=d:return [(x0,x1,z0,z1)]
    return [r for r in [(x0,a,z0,z1),(b,x1,z0,z1),(a,b,z0,c),(a,b,d,z1)] if r[1]-r[0]>1e-8 and r[3]-r[2]>1e-8]


def build(p,*,parent_ids=(),reason='Initial grammar expansion',recipes=None):
    p=deepcopy(p);required=set(parameters());recipes=recipe_registry() if recipes is None else deepcopy(recipes)
    if set(p)!=required or p['family'] not in recipes:raise ValueError('Explicit supported grammar recipe and parameters required')
    recipe=recipes[p['family']]
    for name,value in p.items():
        if name not in ('family','braced','integrated_roof') and (isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value)):raise ValueError('Finite dimensional and formation parameters required')
    if type(p['braced']) is not bool or type(p['integrated_roof']) is not bool:raise ValueError('Explicit production toggles required')
    if not 8<=p['length_m']<=24 or not 2<=p['width_m']<=3.2 or not .8<=p['bay_pitch_m']<=3 or not .25<=p['frame_depth_m']<=.55:raise ValueError('Outside current construction domain; produce a new geometry adapter')
    if min(p['chord_width_m'],p['chord_height_m'])<=2*p['chord_wall_m'] or min(p['skin_thickness_m'],p['core_thickness_m'],p['modular_length_m'])<=0:raise ValueError('Positive manufacturable stock primitives required; actual process limits still need evidence')
    if not .04<=p['chord_width_m']<=.18 or not .06<=p['chord_height_m']<=.25 or not .002<=p['chord_wall_m']<=.012:raise ValueError('Current gross RHS construction domain exceeded; extend geometry/clearance model explicitly')
    brief=remit.context(length_m=p['length_m'],width_m=p['width_m'],cars=p['cars']);demo=brief['demonstration'];L=p['length_m'];W=p['width_m'];H=3.7
    mats=materials();nodes=[];members=[];parts=[];joins=[];components=[];operations=[]
    openings=[]
    for x in (-.265*L,.265*L):openings.append(dict(id=f'door-{x:g}',side=-1,xz_m=[x-.7,x+.7,1.,3.1],kind='door'))
    for side in (-1,1):
        for x in [-.4*L,-.125*L,.125*L,.4*L]:
            rect=[x-.65,x+.65,1.65,2.85]
            if side==-1 and any(not(rect[1]<=d['xz_m'][0] or rect[0]>=d['xz_m'][1]) for d in openings if d['kind']=='door'):continue
            openings.append(dict(id=f'window-{side}-{x:g}',side=side,xz_m=rect,kind='window'))
    def box(uid,at,size,mat,functions=(),role='non-primary',process='cut-and-fit-panel',occurrence=None):
        if min(size)<=0:raise ValueError('Positive actual stock required')
        volume=size[0]*size[1]*size[2]
        parts.append(dict(id=uid,kind='box',at_m=list(at),size_m=list(size),material_id=mat,volume_m3=volume,
            mass_kg=volume*mats[mat]['density_kg_m3'],functions=list(functions),load_roles=[role],
            form=mats[mat]['form'],process=process,manufacturing_occurrence_id=occurrence or uid,removable=role!='primary',access='not-designed'))
        if mat=='gfrp_skin_research':parts[-1]['laminate']=dict(ply_angles_deg=[0,90,90,0],ply_thickness_m=size[1]/4 if uid.startswith('side/') else size[2]/4,properties='Full orthotropic/ABD, hot-wet, fatigue and joint data required; no isotropic stiffness substituted')
    def rhs(uid,a,b,mat,role='primary'):
        d=[b[i]-a[i] for i in range(3)];length=sqrt(sum(v*v for v in d));axis=[v/length for v in d]
        width,height,wall=(p['chord_width_m'],p['chord_height_m'],p['chord_wall_m']) if uid.startswith('chassis/') else (.06,.10,.004)
        area=width*height-(width-2*wall)*(height-2*wall)
        parts.append(dict(id=uid,kind='oriented-RHS',start_m=list(a),end_m=list(b),width_m=width,height_m=height,wall_m=wall,
            material_id=mat,volume_m3=area*length,mass_kg=area*length*mats[mat]['density_kg_m3'],functions=['support-loads'],
            load_roles=[role],form=mats[mat]['form'],process='cut-drill-and-join',manufacturing_occurrence_id=uid,
            joint_end_detail='Nominal cut-stock centreline ends; joint mitres/clevises and net installed joint geometry unresolved',removable=False,access='not-designed'))
        return dict(width_m=width,height_m=height,wall_m=wall,area_m2=area,material_id=mat)
    # Underfloor spatial cells avoid all passenger door/window apertures. They
    # are an axial necessary load-path model, not the entire vehicle body FEA.
    stations=sorted(set([-L/2,L/2,*demo['bogie_centres_x_m'],*[round(-L/2+L*i/ceil(L/p['bay_pitch_m']),9) for i in range(1,ceil(L/p['bay_pitch_m']))]]))
    low=.85-p['frame_depth_m'];ys=(-W/2+.225,W/2-.225);zs=(low,.85)
    for i,x in enumerate(stations):
        for j,y in enumerate(ys):
            for k,z in enumerate(zs):nodes.append(dict(id=f'n-{i}-{j}-{k}',at_m=[x,y,z]))
    lookup={n['id']:n['at_m'] for n in nodes};pairs=set();frame_mat=recipe['frame']
    def edge(a,b,role):
        key=tuple(sorted((a,b)))
        if key in pairs:return
        pairs.add(key);uid='chassis/'+str(len(members));section=rhs(uid,lookup[a],lookup[b],frame_mat)
        members.append(dict(id=uid,start_node=a,end_node=b,section=section,role=role,part_id=uid))
    for i in range(len(stations)):
        for j in (0,1):edge(f'n-{i}-{j}-0',f'n-{i}-{j}-1','cell-post')
        for k in (0,1):edge(f'n-{i}-0-{k}',f'n-{i}-1-{k}','cross-tie')
        if p['braced']:edge(f'n-{i}-0-0',f'n-{i}-1-1','crossframe-diagonal')
        if i==len(stations)-1:continue
        for j in (0,1):
            for k in (0,1):edge(f'n-{i}-{j}-{k}',f'n-{i+1}-{j}-{k}','longitudinal-chord')
        if p['braced']:
            for j in (0,1):edge(f'n-{i}-{j}-0',f'n-{i+1}-{j}-1','side-diagonal')
            for k in (0,1):edge(f'n-{i}-0-{k}',f'n-{i+1}-1-{k}','floor-roof-diagonal')
    supports=[]
    for end,x in enumerate(demo['bogie_centres_x_m']):
        i=stations.index(x)
        for j in (0,1):supports.append(dict(node_id=f'n-{i}-{j}-0',dofs=([1,2,3] if end==0 else [2,3]) if j==0 else [3]))
    # Envelope stock is generated around, rather than across, actual apertures.
    sandwich=recipe['shell']!='skin'
    skin=p['skin_thickness_m'];layers=[('outer',skin,'gfrp_skin_research')]
    if sandwich:layers += [('core',p['core_thickness_m'],'aluminium_core_reference' if recipe['shell']=='honeycomb-sandwich' else 'pet_core_reference'),('inner',skin,'gfrp_skin_research')]
    for side in (-1,1):
        segments=ceil(L/p['modular_length_m']) if recipe['ribs']=='modular' else 1
        rects=[(-L/2+L*i/segments,-L/2+L*(i+1)/segments,1.,H-sum(t for label,t,mat in layers)) for i in range(segments)]
        for aperture in openings:
            if aperture['side']==side:rects=[r for old in rects for r in _rectangles(*old,aperture['xz_m'])]
        offset=0.
        for label,t,mat in layers:
            for idx,(a,b,c,d) in enumerate(rects):box(f'side/{side}/{label}/{idx}',(a,side*W/2-offset-t if side>0 else -W/2+offset,c),(b-a,t,d-c),mat,['enclosure'],role='primary' if sandwich else 'non-primary',process='infuse-or-bond-panel',occurrence=f'side/{side}/panel/{idx}')
            offset+=t
    for place,z in [('floor',1.),('roof',H)]:
        offset=0.
        for label,t,mat in layers:
            segments=ceil(L/p['modular_length_m']) if recipe['ribs']=='modular' else 1
            for i in range(segments):box(f'{place}/{label}/{i}',(-L/2+L*i/segments,-W/2,z-offset-t),(L/segments,W,t),mat,['support-passengers' if place=='floor' else 'roof-structure'],role='primary',process='infuse-or-bond-panel',occurrence=place+'/panel/'+str(i))
            offset+=t
    # Recipe expansion changes real upper frame/rib count and joint operations.
    spacing=2.5 if recipe['ribs']=='sparse' else p['modular_length_m'] if recipe['ribs']=='modular' else p['bay_pitch_m']
    ribs=sorted(set([-L/2,L/2,*[-L/2+L*i/ceil(L/spacing) for i in range(1,ceil(L/spacing))]]))
    for i,x in enumerate(ribs):
        for side in (-1,1):
            if any(a['side']==side and a['xz_m'][0]-.04<x<a['xz_m'][1]+.04 for a in openings):continue
            rhs(f'upper/post/{i}/{side}',[x,side*(W/2-.10),1.05],[x,side*(W/2-.10),H-.08],frame_mat)
        rhs(f'upper/roof-rib/{i}',[x,-W/2+.07,H-.08],[x,W/2-.07,H-.08],frame_mat)
    for n in nodes:joins.append(dict(id='joint/'+n['id'],part_ids=[m['part_id'] for m in members if n['id'] in (m['start_node'],m['end_node'])],method='pin/clevis-underfloor-hypothesis',net_hardware_mass_kg=None,preload_slip_strength='unknown'))
    if p['integrated_roof']:
        for i,y in enumerate((-.8,.8)):
            box('roof/integral/PV-rebate/'+str(i),(-L/2,y,H),(L,.04,.012),'gfrp_skin_research',['solar-mount'],process='co-mould-rebate',occurrence='roof/panel/0')
    else:
        for i,y in enumerate((-.8,.8)):box('roof/separate/PV-rail/'+str(i),(-L/2,y,H+.005),(L,.04,.02),'aluminium_reference',['solar-mount'],process='extrude-cut-drill')
    bottom=H-sum(t for label,t,mat in layers)-.02;channel_mat='gfrp_skin_research' if p['integrated_roof'] else 'aluminium_reference'
    group='roof/panel/0' if p['integrated_roof'] else 'roof/separate/cable-channel'
    channel_label='integral' if p['integrated_roof'] else 'separate'
    for i,(at,size) in enumerate([((-L/2,-.04,bottom),(L,.08,.001)),((-L/2,-.04,bottom+.001),(L,.001,.019)),((-L/2,.039,bottom+.001),(L,.001,.019))]):
        box(f'roof/{channel_label}/cable-channel/{i}',at,size,channel_mat,['cable-route','drainage'],process='co-mould-channel' if p['integrated_roof'] else 'form-and-fasten',occurrence=group)
    # Mark the boundary honestly: functioning doors/glazing/HVAC are required,
    # not fabricated as zero-mass boxes merely to make an assembly look complete.
    required_functions=['support-loads','enclosure','support-passengers','roof-structure','solar-mount','cable-route','drainage','accessible-doors','glazing-retention','HVAC','seating','wheel-support','essential-power']
    physical=dict(schema='osr-generative-body-physical/1',architecture=dict(cars=p['cars'],car_length_m=L,width_m=W),
        envelope=dict(floor_z_m=1.,roof_z_m=H,width_m=W,length_m=L),apertures=openings,nodes=nodes,members=members,
        geometry=[{k:v for k,v in q.items() if k not in ('mass_kg','access','process','joint_end_detail')} for q in parts],
        joins=joins,required_functions=required_functions)
    reference_id,retained,reference_sources=_reference_equipment();retained=deepcopy(retained)
    physical['retained_equipment']=[{k:r[k] for k in ('id','component_definition_id')} for r in retained]
    cid=identity(physical);known=sum(q['mass_kg'] for q in parts)
    # Named inherited account excludes the former body/underframe/frame joints;
    # missing interfaces/services remain unknown, never a complete tare claim.
    load_mass=known+sum(q['mass_kg'] for q in retained if q['system']!='bogies')+demo['normal_people']*demo['person_mass_kg']
    loads=[]
    for i,x in enumerate(stations):
        a=-L/2 if i==0 else (stations[i-1]+x)/2;b=L/2 if i==len(stations)-1 else (x+stations[i+1])/2
        for j in (0,1):loads.append(dict(node_id=f'n-{i}-{j}-1',force_N=[0.,0.,-load_mass*9.80665*(b-a)/L/2]))
    structure=dict(schema='osr-axial-structure-graph/1',candidate_id=cid,nodes=nodes,members=members,materials={k:v for k,v in mats.items() if v['E_Pa'] is not None},supports=supports,loads=loads,
        source_sha256={**reference_sources,PRODUCER:digest(__file__)},
        scope='Underfloor pin/axial necessary model only; excludes upper shell participation, joint compliance, buckling and complete body modes',load_basis=dict(known_body_stock_kg=known,retained_equipment_accounts=retained,normal_people=demo['normal_people'],sprung_mass_hypothesis_kg=load_mass,missing_installed_mass_kg=None))
    assembly=[dict(id='cut',occurrences=[q['id'] for q in parts],requires=[]),dict(id='chassis',occurrences=[q['id'] for q in parts if q['id'].startswith('chassis/')],requires=['cut']),dict(id='shell',occurrences=[q['id'] for q in parts if not q['id'].startswith('chassis/')],requires=['chassis']),dict(id='inspect',occurrences=[q['id'] for q in parts],requires=['shell'])]
    for q in parts:
        components.append(dict(occurrence_id=q['id'],part_id=q['id'],component_definition_id=identity(physical['geometry'][parts.index(q)]),functions=q['functions'],ports=[],mass_kg=q['mass_kg'],stock={'mass_kg':q['mass_kg']},inventory_status='located'))
    by_component={c['occurrence_id']:c for c in components};connections=[]
    for n in nodes:
        joint_id='joint/'+n['id'];ports=[dict(id='load-transfer',kind='mechanical',unit='N',frame_id='vehicle',direction='bidirectional',connector='pin-node-hypothesis',dofs=['Fx','Fy','Fz'],data_validity={'validity':'unknown'})]
        components.append(dict(occurrence_id=joint_id,part_id=joint_id,component_definition_id=identity(next(j for j in joins if j['id']==joint_id)),functions=['transfer-loads'],ports=ports,stock={'mass_kg':None},inventory_status='unknown'))
    for m in members:
        for end,key in enumerate(('start_node','end_node')):
            port_id='end-'+str(end);by_component[m['part_id']]['ports'].append(dict(id=port_id,kind='mechanical',unit='N',frame_id='vehicle',direction='bidirectional',connector='pin-node-hypothesis',dofs=['Fx','Fy','Fz'],data_validity={'validity':'unknown'}))
            connections.append({'id':m['id']+'/'+port_id,'from':[m['part_id'],port_id],'to':['joint/'+m[key],'load-transfer']})
    functions={'HVAC':['HVAC'],'doors':['accessible-doors'],'glazing':['glazing-retention'],'seating':['seating'],'bogies':['wheel-support'],'services':['essential-power']}
    for r in retained:
        components.append(dict(occurrence_id=r['id'],part_id=r['id'],component_definition_id=r['component_definition_id'],functions=functions.get(r['system'],[]),ports=[],mass_kg=r['mass_kg'],stock={'mass_kg':r['mass_kg']},inventory_status='unlocated',geometry_status='unlocated-reference-account',performance_evidence='unknown'))
    assembly.insert(-1,dict(id='services',occurrences=[r['id'] for r in retained],requires=['shell']));assembly[-1]['requires']=['services']
    assembly[1]['occurrences'] += ['joint/'+n['id'] for n in nodes]
    result=dict(schema='osr-generative-body-candidate/1',candidate_id=cid,physical=physical,parameters=p,label=p['family'],parent_candidate_ids=list(parent_ids),revision_reason=reason,
        requirement_revision=brief['requirement_revision'],parts=parts,components=components,connections=connections,required_functions=required_functions,assembly=assembly,
        structure=structure,materials=mats,joins=joins,known_structure_stock_kg=known,retained_equipment_accounts=retained,complete_installed_mass_kg=None,
        sources={**reference_sources,PRODUCER:digest(__file__)},retained_reference_candidate_id=reference_id,recipe_registry=recipes,
        full_body_evaluator='unavailable-for-new-topology',complete_cost_USD=None,**FLAGS)
    result['definition_id']=identity(result);return result


def rewrite(candidate,operator,*,reason):
    p=deepcopy(candidate['parameters'])
    if operator=='triangulate-underfloor':p['braced']=True
    elif operator=='integrate-roof-functions':p['integrated_roof']=not p['integrated_roof']
    elif operator=='redistribute-rib-layout':p['bay_pitch_m']=max(.8,p['bay_pitch_m']*.75)
    elif operator=='change-body-length':p['length_m']=max(8.,p['length_m']-2.)
    else:raise ValueError('Register an executable production and its compatibility/evaluator requirements')
    return build(p,parent_ids=[candidate['candidate_id']],reason=reason,recipes=candidate['recipe_registry'])


def initial_candidates():
    return [build(parameters(family)) for family in RECIPES]


def validate(candidate):
    if candidate.get('candidate_id')!=identity(candidate['physical']) or candidate.get('definition_id')!=identity({k:v for k,v in candidate.items() if k!='definition_id'}):raise ValueError('Mixed or modified generated candidate identity')
    if candidate['structure']['candidate_id']!=candidate['candidate_id'] or candidate['structure']['members']!=candidate['physical']['members'] or candidate['structure']['nodes']!=candidate['physical']['nodes']:raise ValueError('Structural projection differs from physical graph')
    actual=[{k:v for k,v in q.items() if k not in ('mass_kg','access','process','joint_end_detail')} for q in candidate['parts']]
    if actual!=candidate['physical']['geometry']:raise ValueError('Geometry differs from physical graph')
    for p in candidate['parts']:
        if abs(p['mass_kg']-p['volume_m3']*candidate['materials'][p['material_id']]['density_kg_m3'])>1e-8:raise ValueError('Mass differs from explicit geometry/material')
    return candidate
