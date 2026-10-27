"""Counted complete metallic load-path children of generated body proposals.

Net disjoint stock uses intact, finite-face autogenous weld hypotheses. Weld
strength/HAZ/fatigue, panel retention, installed services and qualification stay
unknown. Two real physical alternatives precede any numerical comparison.
"""
from copy import deepcopy
from math import prod,ceil
from pathlib import Path
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import identity,digest
from engineering.design_search import design_grammar
PRODUCER='engineering/design_search/system_body.py'


def _subtract(box,cut):
    lo=[max(box[i],cut[i]) for i in (0,2,4)];hi=[min(box[i+1],cut[i+1]) for i in (0,2,4)]
    if min(b-a for a,b in zip(lo,hi))<=1e-10:return [box]
    x0,x1,y0,y1,z0,z1=box;a,c,e=lo;b,d,f=hi
    return [p for p in ((x0,a,y0,y1,z0,z1),(b,x1,y0,y1,z0,z1),(a,b,y0,c,z0,z1),(a,b,d,y1,z0,z1),(a,b,c,d,z0,e),(a,b,c,d,f,z1)) if min(p[1]-p[0],p[3]-p[2],p[5]-p[4])>1e-10]


def _interfaces(parts):
    planes={};contacts={}
    for p in parts:
        if p.get('structural_role')=='nonstructural-cover':continue
        for d in range(3):
            u,w=[i for i in range(3) if i!=d];rect=[p['at_m'][u],p['at_m'][u]+p['size_m'][u],p['at_m'][w],p['at_m'][w]+p['size_m'][w]]
            for side in (0,1):planes.setdefault((d,round(p['at_m'][d]+side*p['size_m'][d],10)),{0:[],1:[]})[side].append((p['manufacturing_occurrence_id'],rect))
    for group in planes.values():
        for a,r in group[0]:
            for b,s in group[1]:
                if a==b:continue
                area=max(0.,min(r[1],s[1])-max(r[0],s[0]))*max(0.,min(r[3],s[3])-max(r[2],s[2]))
                if area>1e-12:
                    pair=tuple(sorted((a,b)));contacts[pair]=contacts.get(pair,0.)+area
    return [dict(id='weld-interface/'+identity(pair)[:14],occurrences=list(pair),contact_area_m2=area,method='Proposed welded cut-face interface; weld strength/HAZ/fatigue not qualified',net_hardware_mass_kg=None) for pair,area in sorted(contacts.items())]


def build(parent,topology='aluminium_frame',root=ROOT):
    design_grammar.validate(parent)
    if topology not in ('aluminium_frame','aluminium_stressed_skin'):raise ValueError('Explicit supported physical child topology required')
    L=parent['physical']['architecture']['car_length_m'];W=parent['physical']['architecture']['width_m'];H=3.7;apertures=deepcopy(parent['physical']['apertures']);raw=[]
    if abs(L-17.)>1e-8 or abs(W-2.65)>1e-8:raise ValueError('Current connected-body generator domain is17×2.65m; new sizes need explicit support/assembly geometry, not a new project requirement')
    def add(name,at,size,role='frame',occurrence=None):
        if min(size)<=0:raise ValueError('Positive stock required')
        raw.append(dict(id=name,at_m=list(at),size_m=list(size),role=role,occurrence=occurrence or name))
    def tube(name,at,length,width,height,wall,axis):
        sizes=[(length,wall,height),(length,wall,height),(length,width-2*wall,wall),(length,width-2*wall,wall)];offsets=[(0,0,0),(0,width-wall,0),(0,wall,0),(0,wall,height-wall)]
        for i,(s,o) in enumerate(zip(sizes,offsets)):
            if axis==1:s=(s[1],s[0],s[2]);o=(o[1],o[0],o[2])
            if axis==2:s=(s[1],s[2],s[0]);o=(o[1],o[2],o[0])
            add(name+'/'+str(i),[a+b for a,b in zip(at,o)],s,occurrence=name)
    # Plates first: net members are trimmed around finite welded interfaces.
    add('floor/structural',(-L/2,-W/2+.002,.997),(L,W-.004,.003),'floor')
    add('roof/structural',(-L/2,-W/2+.002,3.697),(L,W-.004,.003),'roof')
    for x,name in ((-L/2,'left'),(L/2-.003,'right')):add('end/diaphragm/'+name,(x,-W/2+.002,1.),(.003,W-.004,2.697),'diaphragm')
    for side in (-1,1):
        y=side*1.1-.07;tube('underframe/rail/'+str(side),(-L/2,y,.55),L,.14,.35,.008,0)
        for x in (-6.4,6.4):add(f'bogie-pad/{side}/{x}',(x-.1,side*1.1-.09,.53),(.2,.18,.02),'support-pad')
    stations=sorted({-L/2+.04,L/2-.04,*[-L/2+L*i/ceil(L/1.7) for i in range(1,ceil(L/1.7))],-6.4,6.4})
    for i,x in enumerate(stations):tube('floor/rib/'+str(i),(x-.04,-W/2+.002,.847),W-.004,.08,.15,.006,1)
    # Counted close-pitch floor/roof ribs avoid crediting a flat3mm sheet with
    # the unsupported bending span of the complete frame bay.
    for i in range(11):
        y=-W/2+.08+(W-.16)*i/10;tube('floor/longitudinal/'+str(i),(-L/2,y-.02,.927),L,.04,.07,.003,0)
    for i in range(7):
        y=-W/2+.08+(W-.16)*i/6;tube('roof/longitudinal/'+str(i),(-L/2,y-.02,3.657),L,.04,.04,.003,0)
    for side in (-1,1):
        y=-W/2+.002 if side<0 else W/2-.062
        for z,name in ((.997,'lower'),(3.637,'roof')):tube(f'side/frame/{side}/{name}',(-L/2,y,z),L,.06,.06,.004,0)
        for i,x in enumerate(stations):
            if topology=='aluminium_frame' or i in (0,len(stations)-1):tube(f'side/post/{side}/{i}',(x-.03,y,.997),2.7,.06,.06,.004,2)
        if topology=='aluminium_frame':
            for z in (1.59,2.85,3.1):tube(f'side/stringer/{side}/{z}',(-L/2,y,z),L,.06,.06,.004,0)
        for a in apertures:
            if a['side']!=side:continue
            x0,x1,z0,z1=a['xz_m'];name='side/aperture/'+a['id']
            for x,label in ((x0-.06,'a'),(x1,'b')):tube(name+'/'+label,(x,y,z0-.06),z1-z0+.12,.06,.06,.004,2)
            for z,label in ((z0-.06,'lower'),(z1,'upper')):tube(name+'/'+label,(x0-.06,y,z),x1-x0+.12,.06,.06,.004,0)
        if topology=='aluminium_stressed_skin':add('side/structural/'+str(side),(-L/2,-W/2+.002 if side<0 else W/2-.005,1.),(L,.003,2.697),'side-shear')
    for i,x in enumerate(stations):tube('roof/rib/'+str(i),(x-.03,-W/2+.002,3.637),W-.004,.06,.06,.004,1)
    # Cut every side member around the actual passenger apertures.
    clipped=[]
    for p in raw:
        b=tuple(v for a,s in zip(p['at_m'],p['size_m']) for v in (a,a+s));pieces=[b]
        if p['id'].startswith('side/'):
            side=-1 if p['at_m'][1]<0 else 1
            for a in apertures:
                if a['side']==side:
                    x0,x1,z0,z1=a['xz_m'];pieces=[q for old in pieces for q in _subtract(old,(x0,x1,-W,W,z0,z1))]
        for q in pieces:clipped.append((p,q))
    parts=[];bounds=[];gross=sum(prod(p['size_m']) for p in raw)
    for origin,b in clipped:
        remaining=[b]
        for existing in bounds:remaining=[q for old in remaining for q in _subtract(old,existing)]
        for i,q in enumerate(remaining):
            at=[q[0],q[2],q[4]];size=[q[1]-q[0],q[3]-q[2],q[5]-q[4]];volume=prod(size);uid=origin['id']+'/net/'+str(i)+'-'+identity(q)[:8]
            functions=['support-loads']+(['support-passengers'] if origin['role']=='floor' else ['roof-structure'] if origin['role']=='roof' else ['enclosure'] if origin['role'] in ('diaphragm','side-shear') else [])
            parts.append(dict(id=uid,kind='box',at_m=at,size_m=size,material_id='aluminium_reference',volume_m3=volume,mass_kg=volume*2710.,functions=functions,load_roles=['primary'],form='net-trimmed-metal-stock',process='cut-fit-autogenous-weld',manufacturing_occurrence_id=origin['occurrence'],removable=False,access='not-designed',structural_role=origin['role']));bounds.append(q)
    # Keep only the parent outer side covers as nonstructural, counted stock.
    for old in parent['parts']:
        if old['id'].startswith('side/') and '/outer/' in old['id']:
            q=deepcopy(old);q['id']='retained-cover/'+old['id'];q['load_roles']=['non-primary'];q['structural_role']='nonstructural-cover';parts.append(q)
    mats=deepcopy(parent['materials']);mats['aluminium_reference'].update(nu=.33,constitutive_kind='isotropic',source_basis='Retained declared E69GPa/nu.33 research law from body_solid_frame; no supplier/HAZ/fatigue qualification',source_ref=dict(path='engineering/station_rail/body_solid_frame.py',sha256=digest(Path(root)/'engineering/station_rail/body_solid_frame.py')))
    known=sum(p['mass_kg'] for p in parts);retained=deepcopy(parent['retained_equipment_accounts']);other=sum(r['mass_kg'] for r in retained if r['system']!='bogies');people=parent['structure']['load_basis']['normal_people'];load_cases={name:dict(sprung_mass_hypothesis_kg=known+other+n*75.,people=n,person_mass_kg=75.,complete_installed_mass=False) for name,n in [('empty',0),('normal',people),('crowd',160)]}
    geometry=[{k:v for k,v in p.items() if k not in ('mass_kg','access','process','joint_end_detail')} for p in parts]
    joins=_interfaces(parts);physical=dict(schema='osr-generative-body-physical/1',architecture=deepcopy(parent['physical']['architecture']),envelope=deepcopy(parent['physical']['envelope']),apertures=apertures,nodes=[],members=[],geometry=geometry,joins=joins,required_functions=parent['required_functions'],retained_equipment=deepcopy(parent['physical']['retained_equipment']),topology=topology)
    cid=identity(physical);law_source='engineering/station_rail/body_solid_frame.py';sources={**parent['sources'],PRODUCER:digest(__file__),law_source:digest(Path(root)/law_source)}
    result=dict(schema='osr-generative-body-candidate/1',candidate_id=cid,physical=physical,parameters={**parent['parameters'],'family':topology},label=topology,parent_candidate_ids=[parent['candidate_id']],revision_reason='Counted gap-free finite-face metallic frame and structural panel alternatives',requirement_revision=parent['requirement_revision'],parts=parts,materials=mats,retained_equipment_accounts=retained,known_structure_stock_kg=known,complete_installed_mass_kg=None,complete_cost_USD=None,required_functions=parent['required_functions'],components=[],connections=[],assembly=[],joins=physical['joins'],sources=sources,structure=dict(schema='osr-solid-body-structure/1',candidate_id=cid,nodes=[],members=[]),load_cases=load_cases,
        shell_model=dict(structural_part_ids=[p['id'] for p in parts if p.get('structural_role')!='nonstructural-cover'],joint_assumption='Coincident finite faces are intact autogenous weld/continuous material; no hidden gap ties or rigid offsets',support_z_m=.53,support_x_m=[-6.4,6.4],support_y_m=[-1.1,1.1],gross_raw_metal_stock_m3=gross,net_metal_stock_m3=sum(p['volume_m3'] for p in parts if p['material_id']=='aluminium_reference'),cut_loss_procurement_allowance_kg=None),**FLAGS)
    result['components']=[dict(occurrence_id=p['id'],part_id=p['id'],component_definition_id=identity(geometry[i]),functions=p['functions'],ports=[],mass_kg=p['mass_kg'],stock={'mass_kg':p['mass_kg']},inventory_status='located',manufacturing_occurrence_id=p['manufacturing_occurrence_id']) for i,p in enumerate(parts)]
    retained_ids={r['id'] for r in retained};result['components'] += [deepcopy(c) for c in parent['components'] if c['occurrence_id'] in retained_ids]
    result['assembly']=[dict(id='cut-and-fit',occurrences=[p['id'] for p in parts],requires=[]),dict(id='weld-and-inspect',occurrences=[j['id'] for j in joins],requires=['cut-and-fit'],qualification='Weld procedure, access, inspection and strength release remain unknown')]
    result['definition_id']=identity(result);return result
