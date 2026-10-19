"""Manufactured cap cage, embedded lift cores and actual-section stage research.

The editable steel/spacer solids form a subassembly, not a released precast cap.
Source concrete regions and unresolved mass allowances remain authoritative; no
mass saving or qualified anchorage is inferred from the new reinforcement.
"""
import itertools
import math

from engineering.twin_workflow import core
from engineering.design_consistency import contracts,demonstrators
from engineering.continuous_design import civil_kit,beam_confirmation
from . import baseline,reactions

DOMAINS=dict(bar_diameter_m=[.016,.020,.025],bars_per_layer=[8,10,12],link_spacing_m=[.20,.25,.30])
DEFAULTS=dict(bar_diameter_m=.020,bars_per_layer=10,link_spacing_m=.25)
SOURCES=[
    dict(url='https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Concrete01.html',
        scope='Reference for no-tension/parabolic compression modelling; this small monotonic evaluator is not OpenSees Concrete01 or cyclic validation'),
    dict(url='https://www.fhwa.dot.gov/bridge/abc/docs/abcmanual.pdf',
        scope='Prefabricated-element handling and embedded lifting attachments require explicit checks; railway/project acceptance not supplied'),
]


def candidates():
    return [dict(zip(DOMAINS,values)) for values in itertools.product(*DOMAINS.values())]


def _positive(value,label):
    if type(value) not in (int,float) or not math.isfinite(value) or value<=0:raise ValueError('positive finite '+label+' required')


def _section(kit,unit,station):
    """Recover actual x/z concrete rectangles at a cap y station, including voids."""
    parts={p['id']:p for p in kit['physical_contract']['parts']};rectangles=[]
    for pid in unit['physical_part_ids']:
        part=parts[pid]
        for p in part['manufacturing']['primitives']:
            if p['kind']!='box':raise ValueError('rectangular retained cap material regions required')
            x,y,z=p['centre_m'];dx,dy,dz=p['dimensions_m']
            if y-dy/2+1e-8<station<y+dy/2-1e-8:
                rectangles.append(dict(part_id=pid,x_lower_m=x-dx/2,x_upper_m=x+dx/2,z_lower_m=z-dz/2,z_upper_m=z+dz/2))
    if not rectangles:raise ValueError('section plane outside retained cap material')
    for i,a in enumerate(rectangles):
        for b in rectangles[:i]:
            if min(a['x_upper_m'],b['x_upper_m'])-max(a['x_lower_m'],b['x_lower_m'])>1e-8 and min(a['z_upper_m'],b['z_upper_m'])-max(a['z_lower_m'],b['z_lower_m'])>1e-8:
                raise ValueError('overlapping concrete section regions')
    return rectangles


def section_properties(rectangles):
    if not isinstance(rectangles,list) or not 1<=len(rectangles)<=32:raise ValueError('bounded nonempty concrete section regions required')
    for region in rectangles:
        for key in ('x_lower_m','x_upper_m','z_lower_m','z_upper_m'):
            if type(region.get(key)) not in (int,float) or not math.isfinite(region[key]):raise ValueError('finite concrete section bounds required')
        if region['x_lower_m']>=region['x_upper_m'] or region['z_lower_m']>=region['z_upper_m']:raise ValueError('positive concrete section region required')
    areas=[(r['x_upper_m']-r['x_lower_m'])*(r['z_upper_m']-r['z_lower_m']) for r in rectangles]
    area=sum(areas);cg=sum(a*(r['z_lower_m']+r['z_upper_m'])/2 for a,r in zip(areas,rectangles))/area
    inertia=sum((r['x_upper_m']-r['x_lower_m'])*(r['z_upper_m']-r['z_lower_m'])**3/12+a*((r['z_lower_m']+r['z_upper_m'])/2-cg)**2 for a,r in zip(areas,rectangles))
    return dict(area_m2=area,centroid_z_m=cg,inertia_x_m4=inertia)


def patch_beam(length,supports,ei,patches):
    """Independent Macaulay integral for actual piecewise-constant gravity loads."""
    _positive(length,'beam length');_positive(ei,'beam rigidity')
    if len(supports)!=2 or not 0<=supports[0]<supports[1]<=length:raise ValueError('two stable support stations required')
    for patch in patches:
        if len(patch)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in patch) or not 0<=patch[0]<patch[1]<=length+1e-8 or patch[2]<0:raise ValueError('finite in-span distributed load patches required')
    force=sum(q*(b-a) for a,b,q in patches);first_moment=sum(q*(b-a)*(a+b)/2 for a,b,q in patches)
    second=(first_moment-force*supports[0])/(supports[1]-supports[0]);first=force-second
    def base(x):return (sum(q*(max(0.,x-a)**4-max(0.,x-b)**4)/24 for a,b,q in patches)-first*max(0.,x-supports[0])**3/6-second*max(0.,x-supports[1])**3/6)/ei
    slope=-(base(supports[1])-base(supports[0]))/(supports[1]-supports[0]);offset=-base(supports[0])-slope*supports[0]
    def moment(x):return sum(q*(max(0.,x-a)**2-max(0.,x-b)**2)/2 for a,b,q in patches)-first*max(0.,x-supports[0])-second*max(0.,x-supports[1])
    xs=sorted({*(length*i/2000 for i in range(2001)),*supports,*(p[0] for p in patches),*(p[1] for p in patches)})
    return dict(reactions_n=[first,second],total_force_n=force,first_moment_n_m=first_moment,
        maximum_moment_nm=max(abs(moment(x)) for x in xs),maximum_deflection_m=max(abs(base(x)+slope*x+offset) for x in xs),
        scope='Exact patch-load equilibrium/integrated constant-EI beam; extrema bounded by retained2001point sampling, no shell/contact model')


def build(policy,kit,unit_id='S0-pier-cap-U0',variables=None):
    variables=dict(DEFAULTS if variables is None else variables)
    if set(variables)!=set(DOMAINS) or any(not any(type(v) is type(c) and v==c for c in DOMAINS[k]) for k,v in variables.items()):raise ValueError('controlled civil cage variables required')
    if policy['architecture']!='baghdad-six-car' or not all(civil_kit.validate_kit(kit).values()):raise ValueError('valid exact Baghdad civil kit required')
    unit=next((u for u in kit['units'] if u['id']==unit_id),None)
    if not unit or unit['category']!='pier-cap':raise ValueError('exact retained pier-cap unit required')
    lo,hi=unit['bounds_m'];W,L,H=[b-a for a,b in zip(lo,hi)];xc,yc,zc=[(a+b)/2 for a,b in zip(lo,hi)]
    cover=.05;link=.012;diameter=variables['bar_diameter_m'];r=diameter/2
    cw,ch=W-2*cover,H-2*cover
    if min(cw,ch)<=2*(link+diameter):raise ValueError('cover/cage packaging infeasible')
    material=kit['candidate']['support_material'];E=material['youngs_modulus_pa']*material['stiffness_factor']
    mats=dict(reinforcement=dict(density_kg_m3=7850.,young_pa=200e9,poisson=.3,basis='Proposed round steel geometry and 500MPa monotonic screen; product, weldability and certificates unqualified'),
        steel=dict(density_kg_m3=7850.,young_pa=210e9,poisson=.3,basis='Proposed 355MPa steel gross-section screen; heat, weld and threaded inserts unqualified'),
        spacer=dict(density_kg_m3=2400.,basis='Proposed concrete cover spacer geometry; mix, support strength and durability unqualified'))
    parts=[];joints=[];schedule=[]
    def add(identity,material,primitives,process,role='manufactured-solid',placement=None):
        part=contracts.part(identity,material,dict(role=identity,primitives=primitives),mats,placement=placement,
            limits=dict(tolerance_m=.002,tolerance_status='proposed; process capability unmeasured',minimum_wall_m=None),
            inspections=['material trace','cut dimensions','cover and interfaces','weld/attachment inspection'])
        part.update(manufacturing_unit_id=unit_id+'/cage-embedded-kit',geometric_role=role,procurement=None,process_route=process,
            datum_scheme=dict(A='retained cap underside',B='cap centre x',C='segment end y'))
        parts.append(part);return part
    def cylinder(identity,radius,length,centre,axis='z',inner=None):
        value=dict(id=identity,kind='tube' if inner else 'cylinder',radius_m=radius,length_m=length,centre_m=list(centre),axis=axis)
        if inner:value['inner_radius_m']=inner
        return value
    def joint(identity,ends,mechanism,access):
        joints.append(dict(id=identity,endpoints=ends,mechanism=mechanism,fastener_ids=[],access=access,
            tolerance_m=.002,load_case_ids=['handling','service','replacement'],inspection=['position','retention','independent disposition'],capacity_evidence=None,qualified=False))
    positions=[]
    for layer,z in (('bottom',zc-ch/2+link+r),('top',zc+ch/2-link-r)):
        for i in range(variables['bars_per_layer']):
            x=xc+(-cw/2+link+r)+(cw-2*(link+r))*i/(variables['bars_per_layer']-1)
            identity='cap-bar-'+layer+'-'+str(i);length=L-2*cover
            add(identity,'reinforcement',[cylinder('straight-bar',r,length,[x,yc,z],'y')],'Cut straight bar; end-development/coupler and steel weldability to qualify')
            positions.append(dict(id=identity,x_m=x,z_m=z,area_m2=math.pi*r*r))
            schedule.append(dict(id=identity,stock='round reinforcement',diameter_m=diameter,cut_length_m=length,quantity=1,end_condition='straight; development into end/joint remains open'))
    link_span=L-2*cover-link;nlinks=math.ceil(link_span/variables['link_spacing_m'])+1;ys=[lo[1]+cover+link/2+link_span*i/(nlinks-1) for i in range(nlinks)]
    for i,y in enumerate(ys):
        identity='cap-closed-link-'+str(i)
        part=contracts.member(identity,link,cw,ch,link,'reinforcement',mats,
            placement=dict(translation_m=[xc,y,zc],rotation=[[0,1,0],[1,0,0],[0,0,-1]]))
        add(identity,'reinforcement',part['manufacturing']['primitives'],'Fabricate closed square-section link from four cut legs; corner weld procedure/ductility/confinement unqualified',placement=part['placement'])
        schedule.append(dict(id=identity,stock='12mm square bar closed fabricated link',quantity=1,
            cut_legs=[dict(length_m=cw,quantity=2),dict(length_m=ch-2*link,quantity=2)],
            corner_joints=4,connection='Controlled corner welds, not a bent reinforcing link; weldability, effective throat and fatigue/ductility require qualification'))
        joint(identity+'-tie',[identity,*[p['id'] for p in positions]],'Tie-wire positioning, no assumed structural weld to main bars',dict(factory='outside cage before concrete',installed='embedded; inaccessible'))
    # Anchor cores lie in actual side-wall concrete and between adjacent links.
    first_gap=max(0,int((nlinks-1)*.2));gap_indices=[first_gap,nlinks-2-first_gap]
    picks=sorted({(ys[i]+ys[i+1])/2 for i in gap_indices})
    lifting=[]
    for end,y in enumerate(picks):
        for side in (-1,1):
            x=xc+side*(W/2-.125);identity='lift-core-'+str(end)+'-'+str(side)
            add(identity,'steel',[cylinder('core',.024,.3,[x,y,hi[2]-.15],inner=.013)],
                'Machine hollow steel core; thread form, engagement, mating lifting clutch and exact rated system unselected')
            plate=identity+'-anchor-plate';add(plate,'steel',[contracts.box('anchor',.15,.15,.012,[x,y,hi[2]-.306])],
                'Cut anchor plate; core-to-plate weld and concrete breakout/pullout unqualified')
            joint(identity+'-weld',[identity,plate],'Proposed all-round core/anchor-plate weld; throat/access/certification open',dict(factory='prior to cage closure',installed='recess at top face; matching lifting clutch required'))
            lifting.append(dict(id=identity,point_m=[x,y,hi[2]],embedment_m=.3,mating_device=None,rated_capacity_n=None))
    for side in (-1,1):
        identity='jacking-seat-'+str(side);x=xc+side*.8
        add(identity,'steel',[contracts.box('pad',.3,.3,.025,[x,yc,hi[2]+.0125])],
            'Cut and surface-grind replaceable jacking pad; bed, lateral retention and fixing details open')
        joint(identity+'-bed',[identity],'Compression pad on cap top; local flange punching/spreading and jack head compatibility unqualified',dict(installed='top-face access after deck clearance established',replacement_clearance_m=None))
    for side,y in itertools.product((-1,1),(ys[2],ys[-3])):
        identity='cover-spacer-'+str(side)+'-'+str(y)
        add(identity,'spacer',[contracts.box('spacer',.06,.06,cover,[xc+side*(cw/2-.006),y,lo[2]+cover/2])],
            'Cast purchased/made concrete cover spacer; actual material and cage fixing to qualify')
    # A cage/embedded-only native assembly avoids fictitious overlapping steel
    # and gross concrete. Concrete void subtraction/drawings remain a gate.
    rects=_section(kit,unit,yc);mass_line=[]
    from osr_mech.automated_geometry import primitive_volume
    for p in kit['physical_contract']['parts']:
        if p['id'] not in unit['physical_part_ids']:continue
        primitives=p['manufacturing']['primitives'];total_volume=sum(primitive_volume(v) for v in primitives)
        for primitive in primitives:
            if primitive['kind']!='box':raise ValueError('cap mass patch requires retained box material regions')
            centre=primitive['centre_m'][1];extent=primitive['dimensions_m'][1]
            mass_line.append(dict(id=p['id']+'/'+primitive['id'],start_m=centre-extent/2-lo[1],end_m=centre+extent/2-lo[1],
                mass_kg=p['properties']['mass_kg']*primitive_volume(primitive)/total_volume,basis='Exact retained material region mass and longitudinal extent'))
    mass_line.append(dict(id='retained-unmodeled-allowance',start_m=0.,end_m=L,mass_kg=unit['allocated_mass_kg'],basis='Uniform unresolved source allowance hypothesis; no deleted mass credit'))
    revision=core.digest(dict(kind='civil-cap-detail',variables=variables,policy_revision=core.digest(policy),kit_revision=core.digest(kit),unit_revision=unit['revision'],parts=parts,joints=joints))
    for part in parts:
        part['revision']=revision;part['joints']=[j['id'] for j in joints if part['id'] in j['endpoints']]
    contract=demonstrators.contract('Manufactured cap reinforcement/embedded subassembly; concrete matrix separate',parts,mats)
    contract.update(revision=revision,assembly_joints=joints,mandatory_evidence=['Adopted reinforcement/detailing and weldability','Development, confinement, shear and fatigue','Qualified lifting device/insert concrete resistance and early-age strength','Actual cap joint and jacking stages','Ground/site and independent acceptance'])
    value=dict(schema='osr-civil-cap-detail/1',kind='civil-cap-detail',revision=revision,variables=variables,contract=contract,
        source_kit_revision=core.digest(kit),source_unit=unit,source_material=material,bar_schedule=schedule,joints=joints,
        metadata=dict(architecture='baghdad-six-car',bars=positions,link_positions_y_m=ys,lifting= lifting,
            source_concrete_section=rects,section_plane_y_m=yc,concrete_modulus_pa=E,proposed_concrete_strength_pa=40e6,
            column_supports=[dict(id=u['id'],revision=u['revision'],bounds_m=u['bounds_m']) for u in kit['units'] if u['id'] in unit['support_ids']],
            mass_line_segments=mass_line,
            proposed_steel_yield_pa=500e6,proposed_concrete_ultimate_strain=.0035,proposed_steel_strain_limit=.02,
            source_concrete_geometry_retained=True,native_contains_concrete_matrix=False,full_manufactured_unit_complete=False),
        qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False) for p in parts],
        source_scope='Actual reinforcement/embedded steel subassembly for one hollow reference cap segment; concrete matrix, confinement/anchorage, stage and physical acceptance remain open',
        sources=SOURCES,open_requirements=contract['mandatory_evidence']+['Issued concrete matrix void/cover drawings','Bar couplers/development, ties and spacer fixing','Actual creep/shrinkage/prestress, torsion, fire/durability and rail fatigue'],**core.FLAGS)
    value['process_graph']=process_graph(value)
    value['assembly_steps']=[row['instruction'] for row in value['process_graph']['operations']]
    value['definition_sha256']=core.digest(value)
    return value


def process_graph(candidate):
    """Part-specific factory, casting, lifting, transport and replacement holds.

    Fabricated links close around positioned longitudinal bars; a final tangent
    fit is not misrepresented as clearance to thread bars through closed links.
    """
    parts=[p['id'] for p in candidate['contract']['parts']];bars=[p for p in parts if p.startswith('cap-bar-')]
    links=[p for p in parts if p.startswith('cap-closed-link-')];cores=[p for p in parts if p.startswith('lift-core-')]
    pads=[p for p in parts if p.startswith('jacking-seat-')];spacers=[p for p in parts if p.startswith('cover-spacer-')]
    operations=[]
    def add(identity,after,ids,instruction,tools,*,hold=None,access=None,stage='factory'):
        operations.append(dict(id=identity,after=after,part_ids=ids,instruction=instruction,tools=tools,
            measured_duration_h=None,person_hours=None,required_evidence=hold or [],access=access,
            stage=stage,executed=False,accepted=False))
    add('material-and-jig',[],parts,'Verify steel heat/weldability, cut dimensions and datumed assembly jig before fabrication',
        ['bar saw','jig','dimensional metrology'],hold=['actual steel product/heat and weldability','jig calibration'])
    add('cut-main-bars',['material-and-jig'],bars,'Cut and deburr straight longitudinal bars from the generated bar schedule',
        ['bar saw','end deburring'],access=dict(cut_stock_length_m=max(r.get('cut_length_m',0.) for r in candidate['bar_schedule'])))
    add('cut-link-legs',['material-and-jig'],links,'Cut four square-bar legs per closed-link schedule; keep corners open for radial placement',
        ['cold saw','link fixture'],hold=['corner preparation and weld procedure'])
    add('place-main-bars',['cut-main-bars'],bars,'Locate both longitudinal layers in the open jig; verify cover datums and end development reservations',
        ['cage jig','spacers/gauges'],access=dict(insertion='side placement into open jig',end_insertion_of_closed_links=False))
    add('close-links',['place-main-bars','cut-link-legs'],links,'Place individual link legs around bars, clamp and weld four corners; do not weld main bars without a qualified detail',
        ['link clamps','controlled weld set','weld inspection'],hold=['weld procedure/ductility and actual clear tool paths'],
        access=dict(placement_axes=['x','z'],contact='Longitudinal bars tangent to link inner faces; closed-link threading clearance is zero'))
    add('fabricate-lift-cores',['material-and-jig'],cores,'Machine hollow cores and weld anchor plates before embedment; match a qualified lifting system',
        ['lathe','weld set','bore/thread gauge'],hold=['mating clutch/thread definition','core weld and concrete pullout resistance'])
    add('install-embedded-kit',['close-links','fabricate-lift-cores'],cores+spacers+pads,'Install lift cores between links, cover spacers and jacking pads with surveyable datums',
        ['positioning template','tie tooling','metrology'],hold=['tie and spacer fixing','jacking-pad fixing/bed design'],
        access=dict(lift_points_m=[p['point_m'] for p in candidate['metadata']['lifting']],replacement_access_verified=False))
    add('prepour-inspection',['install-embedded-kit'],parts,'Inspect reinforcement, corner welds, cover, lifting interfaces and concrete-matrix void/penetration drawings',
        ['independent inspection'],hold=['issued cap reinforcement/connection detail','accepted prepour traveller'],stage='factory-casting')
    add('cast-and-cure',['prepour-inspection'],parts,'Cast/vibrate and record concrete batch, curing history and stage-specific measured strength',
        ['mould','concrete plant','curing system'],hold=['mix/process qualification','measured strength and modulus'],stage='factory-casting')
    add('demould',['cast-and-cure'],cores,'Connect the exact rated lifting devices and demould only after applicable strength, geometry and insert acceptance',
        ['certified lifting device','crane at radius'],hold=['demould strength record','qualified insert system','approved lift plan'],stage='handling')
    add('transport',['demould'],parts,'Transport the complete cap on the declared support stations with designed dunnage and positive restraint',
        ['transport vehicle','dunnage/restraints'],hold=['route/permits','dunnage/contact design','braking/roll restraint'],stage='transport')
    add('erect-and-complete-joint',['transport'],parts,'Stabilise the segment before crane release and complete the engineered cap/column and cap-segment joints',
        ['crane','survey','temporary restraint'],hold=['temporary works','joint resistance/strength and tolerance','as-installed survey'],stage='installed')
    add('bearing-replacement',['erect-and-complete-joint'],pads,'Isolate loads and access jacking pads; verify jack stroke, synchronisation and cap flange spreading before bearing removal',
        ['synchronised rated jacks','displacement monitoring'],hold=['jacking stage load path','deck access/clearance','jack compatibility'],stage='maintenance')
    return dict(schema='osr-civil-detail-process/1',operations=operations,unit_revision=candidate['revision'],
        full_assembly_motion_verified=False,schedule_and_cost_measured=False,**core.FLAGS)


def fibre_response(rectangles,bars,curvature,*,concrete_modulus_pa=30e9,concrete_strength_pa=40e6,steel_modulus_pa=200e9,steel_yield_pa=500e6,divisions=60):
    """Monotonic no-tension parabolic concrete + elastic-perfectly-plastic steel.

    Plane sections, perfect bond, no confinement/softening/cyclic/creep law.
    Concrete displaced by each explicit bar is removed from the stress integral.
    """
    for name,value in (('Ec',concrete_modulus_pa),('fc',concrete_strength_pa),('Es',steel_modulus_pa),('fy',steel_yield_pa)):_positive(value,name)
    if not math.isfinite(curvature) or not isinstance(divisions,int) or not 8<=divisions<=240:raise ValueError('bounded finite section request required')
    zref=section_properties(rectangles)['centroid_z_m'];fibres=[]
    if not isinstance(bars,list) or not 1<=len(bars)<=128 or len({b.get('id') for b in bars})!=len(bars):raise ValueError('unique nonempty reinforcement area records required')
    for bar in bars:
        _positive(bar.get('area_m2'),'bar area')
        if not bar.get('id') or any(type(bar.get(k)) not in (int,float) or not math.isfinite(bar[k]) for k in ('x_m','z_m')):raise ValueError('finite reinforcement position required')
        if not any(r['x_lower_m']<bar['x_m']<r['x_upper_m'] and r['z_lower_m']<bar['z_m']<r['z_upper_m'] for r in rectangles):raise ValueError('reinforcement centre outside actual concrete material')
    for region in rectangles:
        dz=(region['z_upper_m']-region['z_lower_m'])/divisions
        for i in range(divisions):fibres.append((region['z_lower_m']+(i+.5)*dz,(region['x_upper_m']-region['x_lower_m'])*dz))
    peak=2*concrete_strength_pa/concrete_modulus_pa
    def concrete(eps):
        if eps<=0:return 0.
        ratio=eps/peak
        return concrete_strength_pa*(2*ratio-ratio*ratio) if ratio<=1 else concrete_strength_pa
    def integrate(offset):
        N=M=0.
        for z,area in fibres:
            stress=concrete(offset+curvature*(z-zref));force=area*stress;N+=force;M+=force*(z-zref)
        steel=[]
        for bar in bars:
            strain=offset+curvature*(bar['z_m']-zref);stress=max(-steel_yield_pa,min(steel_yield_pa,steel_modulus_pa*strain))
            force=bar['area_m2']*(stress-concrete(strain));N+=force;M+=force*(bar['z_m']-zref);steel.append(strain)
        return N,M,steel
    lower,upper=-.2,.2
    if integrate(lower)[0]>0 or integrate(upper)[0]<0:raise ValueError('section axial equilibrium not bracketed')
    for _ in range(80):
        middle=(lower+upper)/2;normal,_,_=integrate(middle)
        if normal>0:upper=middle
        else:lower=middle
    offset=(lower+upper)/2;normal,moment,steel=integrate(offset)
    strains=[offset+curvature*(z-zref) for region in rectangles for z in (region['z_lower_m'],region['z_upper_m'])]
    return dict(curvature_per_m=curvature,axial_strain=offset,normal_force_residual_n=normal,moment_nm=moment,
        maximum_concrete_compression_strain=max(0.,*strains),maximum_steel_strain=max(abs(x) for x in steel),
        steel_yield_reached=any(abs(x)>=steel_yield_pa/steel_modulus_pa for x in steel),divisions_per_rectangle=divisions)


def _curve(candidate,divisions,curvature_sign=-1):
    m=candidate['metadata'];rows=[]
    for value in [i*.00025 for i in range(1,81)]:
        row=fibre_response(m['source_concrete_section'],m['bars'],curvature_sign*value,concrete_modulus_pa=m['concrete_modulus_pa'],
            concrete_strength_pa=m['proposed_concrete_strength_pa'],steel_yield_pa=m['proposed_steel_yield_pa'],divisions=divisions)
        row['inside_strain_hypotheses']=row['maximum_concrete_compression_strain']<=m['proposed_concrete_ultimate_strain'] and row['maximum_steel_strain']<=m['proposed_steel_strain_limit']
        rows.append(row)
        if not row['inside_strain_hypotheses']:break
    feasible=[r for r in rows if r['inside_strain_hypotheses']]
    return dict(points=rows,maximum_sampled_moment_nm=max((abs(r['moment_nm']) for r in feasible),default=0.),
        bending_direction='top reinforcement tension' if curvature_sign<0 else 'bottom reinforcement tension',
        terminal_strain_reached=bool(rows and not rows[-1]['inside_strain_hypotheses']),
        scope='Sampled monotonic research section envelope; no shear, bond/development, confinement, fatigue or code resistance')


def evaluate(candidate,reaction_envelope):
    if candidate.get('definition_sha256')!=core.digest({k:v for k,v in candidate.items() if k!='definition_sha256'}):raise ValueError('civil detail definition changed')
    if candidate['source_kit_revision']!=reaction_envelope['kit_revision'] or candidate['source_unit']['revision']!=reaction_envelope['unit_revisions'].get(candidate['source_unit']['id']):raise ValueError('exact kit/unit reaction revision required')
    if reaction_envelope['revision']!=core.digest({k:v for k,v in reaction_envelope.items() if k!='revision'}):raise ValueError('reaction envelope changed')
    contracts.validate(candidate['contract']);unit=candidate['source_unit'];m=candidate['metadata'];lo,hi=unit['bounds_m'];L=hi[1]-lo[1]
    if unit['revision']!=core.digest({k:v for k,v in unit.items() if k!='revision'}):raise ValueError('retained unit definition changed')
    section=section_properties(m['source_concrete_section']);checks={};stages=[];cases=[]
    represented=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts'])
    checks['detail-within-retained-unmodeled-mass-budget']=represented<=unit['allocated_mass_kg']
    # Full source mass remains; no source allowance is deleted as a saving.
    E=m['concrete_modulus_pa'];EI=E*section['inertia_x_m4'];picks=sorted({a['point_m'][1]-lo[1] for a in m['lifting']})
    if len(picks)!=2:raise ValueError('two distinct lifting stations required')
    for stage,factor,modulus_factor in (('demould',1.3,.6),('transport',1.2,1.),('lifting',1.3,1.),('temporary-placement',1.1,1.)):
        patches=[(r['start_m'],r['end_m'],r['mass_kg']*9.81*factor/(r['end_m']-r['start_m'])) for r in m['mass_line_segments']]
        analytic=patch_beam(L,picks,EI*modulus_factor,patches)
        # Independent Hermite FE is fed a20-point midpoint quadrature for each
        # constant patch; it does not reuse the analytic reaction/integral code.
        points=[(a+(i+.5)*(b-a)/20,q*(b-a)/20) for a,b,q in patches for i in range(20)]
        native=beam_confirmation.solve(L,picks,EI*modulus_factor,points=points,divisions=64)
        checks[stage+'/force-equilibrium']=native['force_balance_relative_error']<1e-6
        checks[stage+'/independent-reactions']=all(abs(a-b['value'])/max(1.,abs(a))<1e-6 for a,b in zip(analytic['reactions_n'],native['reactions']))
        checks[stage+'/independent-beam']=abs(native['maximum_nodal_deflection_m']/analytic['maximum_deflection_m']-1)<.015
        tensile_stress=analytic['maximum_moment_nm']*max(abs(z-section['centroid_z_m']) for z in (lo[2],hi[2]))/section['inertia_x_m4']
        demand=max(analytic['reactions_n'])/math.cos(math.radians(30.))
        checks[stage+'/early-age-cracking-strength']=None
        checks[stage+'/qualified-insert-and-breakout']=None
        stages.append(dict(stage=stage,unit_revision=unit['revision'],complete_retained_unit_mass_kg=unit['mass_kg'],
            dynamic_factor=factor,modulus_factor=modulus_factor,picks_m=picks,analytical=analytic,numerical=native,
            gross_tensile_stress_pa=tensile_stress,required_early_tensile_strength_pa=tensile_stress,
            mass_line_patches_n_per_m=patches,peak_lifting_core_tension_n=demand,lifting_basis='Four points represented; research per-core demand assigns entire more heavily loaded station reaction to one device at30deg from vertical. Eccentricity/equalisation and rigging acceptance remain open',
            release_strength_evidence=None,qualified_lifting_device=None))
    # Column face is recovered from the actual connected column envelope, not
    # a full-solid cap simplification. This prototype segment is the left half.
    columns=m['column_supports']
    if len(columns)!=1 or columns[0]['revision']!=reaction_envelope['unit_revisions'].get(columns[0]['id']):raise ValueError('exact connected column definition required')
    face=columns[0]['bounds_m'][0][1]
    if not (lo[1]<face<hi[1] and abs(hi[1])<1e-8):raise ValueError('left half-cap cantilever prototype applicability differs')
    cantilever=face-lo[1]
    for combination in reaction_envelope['combinations']:
        bearings=[r for r in combination['bearing_reactions'] if r['bearing_id'].startswith(unit['id'].split('-')[0]+'-') and r['position_m'][1]<face]
        if not bearings:raise ValueError('cap-bearing load allocation absent')
        self_force=self_moment=0.
        for row in m['mass_line_segments']:
            left,right=max(0.,row['start_m']),min(cantilever,row['end_m'])
            if right<=left:continue
            q=row['mass_kg']*9.81*combination['G']/(row['end_m']-row['start_m']);self_force+=q*(right-left);self_moment+=q*(right-left)*(cantilever-(left+right)/2)
        force=sum(r['force_n'][2] for r in bearings)+self_force
        moment=sum(r['force_n'][2]*(face-r['position_m'][1]) for r in bearings)+self_moment
        cases.append(dict(id=combination['id'],reaction_revision=reaction_envelope['revision'],column_face_y_m=face,
            bearing_ids=[r['bearing_id'] for r in bearings],shear_demand_n=force,cantilever_moment_nm=moment,
            included_cap_self_weight_n=self_force,included_cap_self_weight_moment_nm=self_moment,scope='Global cantilever cut with actual material-region gravity patches; three-dimensional cap/column joint, shear and torsion require local models'))
    coarse=_curve(candidate,40);fine=_curve(candidate,80)
    capacity=fine['maximum_sampled_moment_nm'];demand=max(abs(c['cantilever_moment_nm']) for c in cases)
    checks['section-mesh-sensitivity']=abs(capacity-coarse['maximum_sampled_moment_nm'])/max(capacity,1.)<.02
    checks['section-equilibrium']=max(abs(r['normal_force_residual_n']) for r in fine['points'])<.1
    checks['proposed-monotonic-flexure-only']=demand<=capacity
    checks.update({name:None for name in ('bar-development-and-cap-segment-joint','welded-link-ductility-and-confinement','shear-torsion-fatigue','crack-width-creep-shrinkage','jacking-head-flange-spreading','wind-seismic-ground-and-corridor')})
    failures=[name for name,v in checks.items() if v is False];holds=[name for name,v in checks.items() if v is None]
    return dict(schema='osr-civil-cap-detail-assessment/1',candidate_revision=candidate['revision'],reaction_revision=reaction_envelope['revision'],
        checks=checks,failed_checks=failures,held_checks=holds,state='failed' if failures else 'hold',
        represented_detail_mass_kg=represented,retained_source_unit_mass_kg=unit['mass_kg'],retained_unresolved_allowance_kg=max(0.,unit['allocated_mass_kg']-represented),
        no_mass_saving_claim=True,actual_concrete_section=section,construction_stages=stages,service_cases=cases,
        monotonic_section=fine,reverse_bending_section=_curve(candidate,80,1),maximum_reference_flexural_demand_nm=demand,proposed_sampled_section_moment_nm=capacity,
        net_manufactured_unit_mass_verified=False,full_manufactured_unit_complete=False,**core.FLAGS)


def snapshot(policy=None):
    from . import models
    policy=policy or baseline.validate(core.read(baseline.DATA));kit=civil_kit.build(civil_kit.defaults());f=baseline.facts(policy);a=policy['pilots']['bearing-seat']['assumptions']
    v={key:values[0] for key,values in policy['pilots']['bearing-seat']['domains'].items()};v['bearing_family']='uk-spherical-candidate';seat_candidate=models.build(policy,'bearing-seat',v)
    train=reactions.revisioned(dict(architecture='baghdad-six-car',mass_cases_kg=f['train.mass_cases'],cars=6,car_length_m=f['train.car_length'],tracks=2,span_m=20.,gravity_m_s2=a['gravity_m_s2'],permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
    seat=reactions.revisioned(dict(candidate_revision=seat_candidate['revision'],mass_kg=sum(p['properties']['mass_kg'] for p in seat_candidate['contract']['parts'])))
    envelope=reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision']);candidate=build(policy,kit)
    return dict(candidate=candidate,assessment=evaluate(candidate,envelope),kit=kit,reaction_envelope=envelope,variables_available=candidates(),**core.FLAGS)
