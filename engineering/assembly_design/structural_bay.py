"""Provisional 1.2 m structural-floor bay, not a complete vehicle body.

Owned RHS steel frame, cut/drilled floor, bolted feet and a steel test mass.
This third pilot joins physical geometry to an independent elastic beam check.
Rail/bogie loads, shell buckling, fatigue, fire and qualified joints stay open.
"""
from copy import deepcopy
import itertools
import math

from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from engineering.continuous_design import beam_confirmation
from engineering.assembly_design import baseline
from . import structural_detail

PILOT=dict(requirement_ids=['baghdad:ME-01'],
    domains=dict(rail_wall_m=[.003,.004,.005],crossmember_count=[2,3],floor_thickness_m=[.003,.004,.012,.016]),
    assumptions=dict(length_m=1.2,width_between_rail_centres_m=1.,rail_width_m=.06,rail_height_m=.1,
        crossmember_width_m=.05,crossmember_height_m=.08,gravity_m_s2=9.80665,
        vertical_acceleration_factors=[1.,3.],stress_fraction=.6,deflection_limit_m=.002,
        proposed_yield_pa=355e6,dimensional_tolerance_m=.0005),
    holds=['Approved six-car local/global loads, equipment/axle/CG map and emergency conditions',
        'Local holes/inserts, weld throat/procedure/NDT, bolt preload/prying/slip/fatigue and loss-of-fastener checks',
        'Floor plate local bending, global torsion and shell/local buckling with mesh/boundary sensitivity',
        'Modal acceptance and vehicle frequency transfer, measured damping and equipment maps',
        'Fatigue duty/spectra, crash/lifting/jacking/recovery and degraded configurations',
        'Material heat/process/hot-wet/fire, corrosion, panel/joint physical correlation and independent acceptance',
        'Complete structural bay enclosure, panels/inserts, repairs, removal access and qualified vehicle integration',
        'Weld-bead/coating/service mass and actual equipment fixture replacement remain unrepresented'],
    scope='Proposed isolated 1.2 m steel floor/rail bay with a represented steel test block; no whole-car or manufacturing acceptance')


def candidates(policy):
    domains=policy['pilots']['structural-bay']['domains']
    for values in itertools.product(*domains.values()): yield dict(zip(domains,values))


def _validate(policy,variables):
    if policy['architecture']!='baghdad-six-car':raise ValueError('structural pilot requires Baghdad architecture')
    domains=policy['pilots']['structural-bay']['domains']
    if set(variables)!=set(domains) or any(not any(type(v) is type(x) and v==x for x in domains[k]) for k,v in variables.items()):
        raise ValueError('unregistered structural-bay variables')
    if any(type(x) is float and not math.isfinite(x) for x in variables.values()):raise ValueError('nonfinite structural variables')


def build(policy,variables):
    _validate(policy,variables);p=policy['pilots']['structural-bay'];a=p['assumptions'];f=baseline.facts(policy)
    L=a['length_m'];spacing=a['width_between_rail_centres_m'];rw=a['rail_width_m'];rh=a['rail_height_m']
    wall=variables['rail_wall_m'];floor=variables['floor_thickness_m'];count=variables['crossmember_count']
    materials={'steel':dict(density_kg_m3=f['steel.density'],young_pa=f['steel.elastic_modulus'],poisson=.3,yield_reference_pa=a['proposed_yield_pa'],
        basis='Nominal reference steel; proposed 355 MPa screen, actual section/product/heat/process qualification open')}
    parts=[];joints=[]
    def add(value,process='cut/drill/deburr',role='manufactured-solid'):
        value.update(geometric_role=role,procurement=None,process_route=process,manufacturing_unit_id=value['id'],
            datum_scheme={'A':'rail top z=0','B':'longitudinal centre y=0','C':'bay centre x=0'})
        parts.append(value);return value
    def solid(identity,primitives,process='cut/drill/deburr',role='manufactured-solid'):
        return add(contracts.part(identity,'steel',dict(role=identity,primitives=primitives),materials,
            inspections=['material trace','dimensions and interface holes','burrs/coating','joint inspection'],
            limits={'tolerance_m':a['dimensional_tolerance_m'],'tolerance_status':'proposed-unqualified','minimum_wall_m':None}),process,role)
    def join(identity,endpoints,mechanism):
        joints.append(dict(id=identity,endpoints=endpoints,mechanism=mechanism,fastener_ids=[],
            datum='A/B/C',tolerance_m=a['dimensional_tolerance_m'],load_case_ids=['gravity','vertical-3g'],
            inspection=['identity','fit','retention'],capacity_evidence=None,qualified=False))
    for side in (-1,1):
        identity='longitudinal-'+str(side)
        add(contracts.member(identity,L,rw,rh,wall,'steel',materials,centre=(0,side*spacing/2,-rh/2),
            inspections=['wall and section dimensions','material trace','weld/joint interfaces']))
    cross_length=spacing-rw
    positions=[-.55,.55] if count==2 else [-.55,0.,.55]
    for i,x in enumerate(positions):
        identity='crossmember-'+str(i)
        value=contracts.member(identity,cross_length,a['crossmember_width_m'],a['crossmember_height_m'],wall,'steel',materials,
            placement={'translation_m':[x,0,-a['crossmember_height_m']/2], 'rotation':[[0,-1,0],[1,0,0],[0,0,1]]},
            inspections=['end square and fit','wall dimensions','end weld inspection'])
        add(value)
        for side in (-1,1):join(identity+'-end-'+str(side),[identity,'longitudinal-'+str(side)],
            'RHS square-cut end contacts rail inner face; weld throat, access and fatigue design required')
    mounts=[(x,y) for x in (-.18,.18) for y in (-.12,.12)]
    holes=[(x+math.copysign(.022,x),y) for x,y in mounts]
    # 10 mm overhang each side exposes the underside lap-weld corner;
    # a flush floor edge would obstruct the proposed longitudinal fillet.
    primitive=contracts.box('floor',L,spacing+rw+.020,floor,[0,0,floor/2])
    primitive.update(kind='perforated-plate',holes_xy_m=[list(p) for p in holes],hole_radius_m=.0055)
    solid('floor-panel',[primitive])
    for side in (-1,1):join('floor-rail-'+str(side),['floor-panel','longitudinal-'+str(side)],
        'Contact on rail top; controlled intermittent weld pattern and local floor resistance remain open')
    for i in range(count):join('floor-cross-'+str(i),['floor-panel','crossmember-'+str(i)],'Contacted floor support; welded attachment qualification open')
    def cylinder(identity,radius,length,centre,inner=None):
        result=dict(id=identity,kind='cylinder' if inner is None else 'tube',radius_m=radius,length_m=length,centre_m=centre,axis='z')
        if inner is not None:result['inner_radius_m']=inner
        return result
    for i,((x,y),(hx,hy)) in enumerate(zip(mounts,holes)):
        plate=contracts.box('plate',.08,.06,.006,[x,y,floor+.003])
        plate.update(kind='perforated-plate',holes_xy_m=[[hx-x,0]],hole_radius_m=.0055)
        # Hole offsets are relative to the primitive centre, matching
        # the existing perforated-plate geometry contract.
        solid('mount-foot-'+str(i),[plate])
        legx=x-math.copysign(.018,x);z0=floor+.006
        solid('mount-leg-'+str(i),[contracts.box('leg',.015,.015,.09-z0,[legx,y,(.09+z0)/2])])
        stack=structural_detail.fastener_stack(floor)
        solid('mount-bolt-'+str(i),[cylinder('shank',.005,stack['nominal_underhead_length_m'],[hx,hy,stack['nominal_underhead_length_m']/2-.002]),cylinder('head',.009,.008,[hx,hy,-.006])],
            process='Purchase M10x'+str(round(stack['nominal_underhead_length_m']*1000))+' coarse 1.5 mm pitch, class 8.8 reference; exact part/certificate/preload to qualify',role='hardware-envelope')
        solid('mount-lower-washer-'+str(i),[cylinder('washer',.010,.002,[hx,hy,-.001],inner=.0055)],process='Purchase lower bearing washer; exact class and dimensions to confirm',role='hardware-envelope')
        solid('mount-washer-'+str(i),[cylinder('washer',.010,.002,[hx,hy,floor+.007],inner=.0055)],process='Purchase washer class/dimensions to specify',role='hardware-envelope')
        solid('mount-nut-'+str(i),[cylinder('nut-envelope',.009,.008,[hx,hy,floor+.012],inner=.0055)],process='Purchase retained M10 nut; thread/engagement not verified',role='hardware-envelope')
        join('equipment-foot-'+str(i),['floor-panel','mount-foot-'+str(i),'mount-bolt-'+str(i),'mount-washer-'+str(i),'mount-lower-washer-'+str(i),'mount-nut-'+str(i)],
            'Through-bolted floor attachment; bolt stack represented; thread engagement, local plate/prying/preload and vibration open')
        join('equipment-leg-'+str(i),['mount-foot-'+str(i),'mount-leg-'+str(i),'equipment-test-block'],
            'Steel dummy test block on welded legs; actual equipment mount supplier/dynamics and weld qualification open')
    solid('equipment-test-block',[contracts.box('test-block',.4,.3,.04,[0,0,.11])],process='Cut steel dummy block for geometry/load-path study; not actual vehicle equipment')
    revision=core.digest(dict(kind='structural-bay',variables=variables,baseline=policy,parts=parts,joints=joints,materials=materials))
    for part in parts:
        part['revision']=revision;part['joints']=[j['id'] for j in joints if part['id'] in j['endpoints']]
    contract=dict(schema='osr-engineering-representations/1',name='structural-bay',revision=revision,parts=parts,materials=materials,
        assembly_joints=joints,construction_stages=[],mandatory_evidence=p['holds'],physical_validation=False,production_released=False)
    contracts.validate(contract)
    return dict(schema='osr-assembly-design-candidate/1',kind='structural-bay',variables=deepcopy(variables),revision=revision,
        requirement_ids=p['requirement_ids'],contract=contract,
        metadata=dict(architecture=policy['architecture'],length_m=L,rail_spacing_m=spacing,crossmember_positions_m=positions,
            mount_positions_m=[[x,y,0] for x,y in holes],steel_test_block_mass_kg=.4*.3*.04*f['steel.density'],
            section_m=[rw,rh,wall],floor_thickness_m=floor,floor_edge_overhang_m=.010,fastener_stack=structural_detail.fastener_stack(floor),
            load_path=['equipment test block','four mount legs and feet','drilled floor','crossmembers and longitudinal rails','four declared end supports'],
            unsupported_scope=['side and roof panels','bogie connection','whole-car load transfer','weld beads/coatings','actual service equipment']),
        assembly_steps=['Verify material/section identities and cut datums','Fixture RHS rails and touching crossmember ends',
            'Weld frame to qualified sequence; inspect','Fit/drill floor and qualify floor weld pattern',
            'Bench weld four dummy supports and steel test block','Install M10 mount fastener sets and inspect',
            'Measure bay mass/CG; perform controlled bench load cases; independent acceptance remains open'],
        qa_plan=[dict(unit_id=v['id'],unit_revision=revision,serial=None,required=v['inspection_characteristics'],records=[],accepted=False) for v in parts],
        source_scope=p['scope'],open_requirements=p['holds'],**core.FLAGS)


def evaluate(policy,candidate):
    _validate(policy,candidate['variables'])
    expected=build(policy,candidate['variables'])
    if core.digest(candidate)!=core.digest(expected):raise ValueError('candidate differs from controlled structural generator')
    contract=candidate['contract'];summary=contracts.summary(contract);a=policy['pilots']['structural-bay']['assumptions']
    facts=baseline.facts(policy);L=a['length_m'];section=contract['parts'][0]['analysis']['section']
    # The section contract names bending about the horizontal section axis.
    inertia=section['iy_m4'];ei=facts['steel.elastic_modulus']*inertia;mass=summary['mass_kg']
    checks={};cases=[]
    for acceleration in a['vertical_acceleration_factors']:
        q=mass*a['gravity_m_s2']*acceleration/(2*L)
        analytical=5*q*L**4/(384*ei);moment=q*L*L/8;stress=moment*a['rail_height_m']/2/inertia
        solutions=[beam_confirmation.solve(L,[0.,L],ei,uniform=q,divisions=n) for n in (8,16)]
        coarse,fine=solutions;deflection=fine['maximum_nodal_deflection_m']
        identifier='vertical-'+str(acceleration)+'g'
        agreement=abs(deflection/analytical-1);refinement=abs(deflection/coarse['maximum_nodal_deflection_m']-1)
        checks[identifier+'/closed-form-agreement']=agreement<1e-7
        checks[identifier+'/mesh-refinement']=refinement<1e-7
        checks[identifier+'/equilibrium']=fine['force_balance_relative_error']<1e-8
        checks[identifier+'/rail-stress-provisional']=stress<=a['proposed_yield_pa']*a['stress_fraction']
        checks[identifier+'/rail-deflection-provisional']=deflection<=a['deflection_limit_m']
        reactions=[dict(rail=side,x_m=r['x_m']-L/2,force_z_n=r['value']) for side in (-1,1) for r in fine['reactions']]
        checks[identifier+'/whole-bay-force-balance']=abs(sum(r['force_z_n'] for r in reactions)-mass*a['gravity_m_s2']*acceleration)<1e-6
        clamped=beam_confirmation.solve(L,[0.,L],ei,uniform=q,divisions=16,clamp=True)
        clamp_expected=q*L**4/(384*ei)
        checks[identifier+'/clamped-boundary-control']=abs(clamped['maximum_nodal_deflection_m']/clamp_expected-1)<1e-7
        cases.append(dict(id=identifier,acceleration_factor=acceleration,represented_mass_kg=mass,load_per_rail_n_m=q,
            stiffness_ei_nm2=ei,analytical_deflection_m=analytical,deflection_m=deflection,stress_pa=stress,
            analytical_agreement_relative_error=agreement,refinement_relative_change=refinement,
            support_reactions=reactions,numerical_meshes=solutions,
            boundary_sensitivity=dict(pinned_deflection_m=deflection,clamped_deflection_m=clamped['maximum_nodal_deflection_m'],
                ratio=deflection/clamped['maximum_nodal_deflection_m'],
                scope='Two ideal boundary-condition formulations only; actual attachment fixity requires local model/test'),
            assumption='Symmetric uniform gravity apportionment to two simply supported longitudinal RHS; no composite floor stiffness or qualified local joint transfer'))
    for key in ('local-floor-resistance','bolt-and-weld-resistance','shell-buckling','modal-acceptance','fatigue-spectrum',
                'actual-equipment-loads','whole-car-bogie-interface','physical-joint-panel-correlation'):
        checks[key]=None
    detail=structural_detail.report(policy,candidate)
    checks.update({'detail/'+name:value for name,value in detail['checks'].items()})
    failures=[k for k,v in checks.items() if v is False];held=[k for k,v in checks.items() if v is None]
    measurements=dict(mass_kg=mass,cg_m=summary['cg_m'],inertia_tensor_kg_m2=summary['inertia_tensor_kg_m2'],
        part_count=len(contract['parts']),owned_part_count=sum(p['geometric_role']=='manufactured-solid' for p in contract['parts']),
        beam_cases=cases,load_path=candidate['metadata']['load_path'],mass_scope='All represented steel bay and fastener/test-block geometry only; omitted weld/coating/services listed as open',
        section_inertia_m4=inertia,geometry_revision=candidate['revision'],structural_detail_revision=detail['revision'])
    return dict(schema='osr-assembly-screening/1',candidate_revision=candidate['revision'],kind='structural-bay',checks=checks,
        failed_checks=failures,held_checks=held,screen_pass=not failures and not held,implemented_checks_pass=not failures,
        state='failed' if failures else 'hold',measurements=measurements,supplemental_evidence={'structural-detail':detail},open_requirements=candidate['open_requirements'],
        digital_specification_complete=False,connection_resistance_qualified=False,
        scope=PILOT['scope']+'; equivalent rail, local mount/floor, weld direct-shear and modal research screens only',**core.FLAGS)
