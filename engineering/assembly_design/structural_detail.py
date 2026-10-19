"""Local joint, weld, modal and manufacturing adapters for the 1.2 m pilot.

All resistance thresholds, preload and material strengths below are explicitly
proposed engineering sensitivities. NASA RP-1228 is an implementation reference,
not railway acceptance; no licensed detail category, measured duty or WPS is
invented. Local elastic models are useful before shell/contact correlation.
"""
import math
import numpy as np

from engineering.twin_workflow import core
from engineering.integration_programme import joints

SOURCES=[dict(publisher='NASA',document='NASA RP-1228 Fastener Design Manual',revision='1990-03-01',
    url='https://ntrs.nasa.gov/citations/19900009424',locator='Fastener group, grip, preload, torque, locking and fatigue design topics',
    licence='US government public use permitted',applicability='Method reference; no railway adoption or physical qualification'),
    dict(publisher='Steel Construction Institute',document='P364 Worked Examples — Open Sections',revision='2009',
    url='https://www.steelconstruction.info/images/5/50/Sci_p364.pdf',locator='Connection worked examples; independent implementation reference',
    licence='Copyright SCI; facts/links only',applicability='Building examples; project rail criteria not adopted')]


def _positive(value,name):
    if type(value) not in (int,float) or not math.isfinite(value) or value<=0:raise ValueError('finite positive '+name+' required')
    return float(value)


def fastener_stack(floor_m):
    floor=_positive(floor_m,'floor thickness');foot=.006;washer=.002;nut=.008;pitch=.0015
    lengths=[v for v in (.025,.030,.035,.040,.045,.050) if 2*pitch-1e-12<=v-(2*washer+floor+foot+nut)<=4*pitch+1e-12]
    if not lengths:raise ValueError('no proposed catalogue-length stack with required projection')
    length=min(lengths)
    grip=floor+foot
    projection=length-(2*washer+grip+nut)
    return dict(schema='osr-proposed-fastener-stack/1',thread='M10x1.5',nominal_diameter_m=.010,pitch_m=pitch,
        nominal_underhead_length_m=length,head_bearing_z_m=-washer,
        lower_washer_z_m=[-washer,0.],floor_z_m=[0.,floor],foot_z_m=[floor,floor+foot],
        upper_washer_z_m=[grip,grip+washer],nut_z_m=[grip+washer,grip+washer+nut],
        bolt_tip_z_m=-washer+length,grip_m=grip,nut_height_m=nut,projection_m=projection,
        projected_threads=projection/pitch,engagement_m=nut,
        proposed_strength_class='8.8 reference; exact purchased certification required',
        thread_geometry='Controlled thread specification; smooth envelope in CAD, not modelled thread contact',
        locking='All-metal prevailing-torque candidate; qualified reuse, temperature, preload and inspection required',
        checks=dict(stack_contact=projection>=0.,projection_two_to_four_pitches=2*pitch-1e-12<=projection<=4*pitch+1e-12),
        qualified=False,**core.FLAGS)


def thread_area(diameter_m=.010,pitch_m=.0015):
    """Nominal metric-thread tensile-area approximation; not certified resistance."""
    d=_positive(diameter_m,'diameter');p=_positive(pitch_m,'pitch')
    if d<=.9382*p:raise ValueError('thread dimensions close the tensile section')
    return math.pi/4*(d-.9382*p)**2


def local_mount(*,positions_m,mass_kg,cg_height_m,floor_m,gravity=9.80665,load_scale=1.,missing_bolt=None,young_pa=210e9,yield_pa=355e6):
    """Full six-resultant elastic demand + explicit local member hypotheses."""
    for value,name in ((mass_kg,'mass'),(cg_height_m,'CG height'),(floor_m,'floor'),(gravity,'gravity'),(load_scale,'load scale')):_positive(value,name)
    positions=[list(v) for i,v in enumerate(positions_m) if i!=missing_bolt]
    _positive(young_pa,'material modulus');_positive(yield_pa,'yield hypothesis')
    group=joints.bolt_group(positions,.010,floor_m+.006,young_pa)
    cases=[];fy=yield_pa;area=thread_area();preload=.7*800e6*area
    for uplift in (-3.,3.):
        force=np.asarray([5.,3.,uplift])*mass_kg*gravity*load_scale
        moment=np.cross([0.,0.,cg_height_m],force)
        demand=joints.assess(group,[*force,*moment],preload_n=preload,friction=.15)
        tension=max(max(0.,f[2]) for f in demand['bolt_forces_n']);shear=max(math.hypot(f[0],f[1]) for f in demand['bolt_forces_n'])
        equivalent=math.sqrt(tension**2+3*shear**2)/area
        combined_preload=math.sqrt((preload+tension)**2+3*shear**2)/area
        # A 60 mm-wide foot, 11 mm hole, centre-to-end edge 18 mm.
        # Stress resultants are separately exposed; no hidden EC resistance.
        edge_ligament=.018-.011/2;net_area=(.060-.011)*.006
        bearing=shear/(.010*min(.006,floor_m));net_stress=shear/net_area
        tearout=shear/(2*edge_ligament*min(.006,floor_m))
        block_shear=shear/(2*edge_ligament*.006)
        # Uplift at a leg 40 mm from the bolt gives a lower-bound foot-strip
        # bending demand; actual contact/prying needs nonlinear analysis/test.
        prying_moment=tension*.040;foot_bending=6*prying_moment/(.060*.006**2)
        row=dict(acceleration_vector_g=[5.,3.,uplift],resultants_si=[*force.tolist(),*moment.tolist()],
            bolt_group=demand,thread_area_m2=area,peak_tension_n=tension,peak_shear_n=shear,equivalent_thread_stress_pa=equivalent,combined_preload_stress_pa=combined_preload,
            bearing_stress_pa=bearing,net_section_stress_pa=net_stress,edge_tearout_shear_pa=tearout,
            block_shear_average_pa=block_shear,foot_strip_bending_stress_pa=foot_bending,
            preload_hypothesis_n=preload,friction_hypothesis=.15,torque_sensitivity_nm=[k*preload*.010 for k in (.12,.25)],
            checks=dict(thread_elastic_stress=equivalent<=.6*640e6,
                full_external_tension_plus_preload_hypothesis=combined_preload<=.9*640e6,
                plate_bearing_stress_hypothesis=bearing<=.6*fy,net_section_hypothesis=net_stress<=.6*fy,
                edge_tearout_hypothesis=tearout<=.6*fy/math.sqrt(3),block_shear_hypothesis=block_shear<=.6*fy/math.sqrt(3),
                foot_strip_bending_hypothesis=foot_bending<=.6*fy,
                no_separation_at_hypothesised_preload=not demand['separation_screen_failed'],
                no_slip_at_hypothesised_friction=not demand['slip_screen_failed']))
        cases.append(row)
    return dict(cases=cases,removed_bolt_index=missing_bolt,represented_bolt_count=len(positions),
        scope='Elastic bolt group and simplified local stress hypotheses; no certified connection resistance, contact/prying solution or torque instruction',
        criteria_status='Proposed test-domain sensitivities; approved loads/material/preload/friction and fatigue remain open',**core.FLAGS)


def floor_strip(*,force_n,span_m,width_m,thickness_m,young_pa=210e9,uniform_n_m=0.):
    """Conservative central-load simple strip; point patch/2D action not inferred."""
    for v,n in ((force_n,'force'),(span_m,'span'),(width_m,'width'),(thickness_m,'thickness'),(young_pa,'modulus')):_positive(v,n)
    if type(uniform_n_m) not in (int,float) or not math.isfinite(uniform_n_m) or uniform_n_m<0:raise ValueError('finite nonnegative uniform load required')
    inertia=width_m*thickness_m**3/12
    moment=force_n*span_m/4+uniform_n_m*span_m**2/8
    return dict(force_n=force_n,span_m=span_m,width_m=width_m,thickness_m=thickness_m,
        uniform_n_m=uniform_n_m,inertia_m4=inertia,stress_pa=6*moment/(width_m*thickness_m**2),
        deflection_m=force_n*span_m**3/(48*young_pa*inertia)+5*uniform_n_m*span_m**4/(384*young_pa*inertia),
        scope='Central point force on a simply supported one-way floor strip; no plate membrane or composite credit')


def plate_buckling(*,width_m,thickness_m,young_pa=210e9,poisson=.3,k=4.):
    for v,n in ((width_m,'plate width'),(thickness_m,'plate thickness'),(young_pa,'modulus'),(k,'buckling coefficient')):_positive(v,n)
    if type(poisson) not in (int,float) or not math.isfinite(poisson) or not 0<=poisson<.5:raise ValueError('supported Poisson ratio required')
    return k*math.pi**2*young_pa/(12*(1-poisson**2))*(thickness_m/width_m)**2


def modal_beam(length_m,ei_nm2,mass_per_m,*,elements=8,modes=3):
    """Independent Euler-Bernoulli consistent-mass eigenproblem, pinned ends."""
    for v,n in ((length_m,'length'),(ei_nm2,'stiffness'),(mass_per_m,'line mass')):_positive(v,n)
    if type(elements) is not int or not 2<=elements<=64:raise ValueError('bounded integer mesh required')
    n=2*(elements+1);K=np.zeros((n,n));M=np.zeros((n,n));h=length_m/elements
    ke=ei_nm2/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
    me=mass_per_m*h/420*np.array([[156,22*h,54,-13*h],[22*h,4*h*h,13*h,-3*h*h],[54,13*h,156,-22*h],[-13*h,-3*h*h,-22*h,4*h*h]])
    for i in range(elements):K[2*i:2*i+4,2*i:2*i+4]+=ke;M[2*i:2*i+4,2*i:2*i+4]+=me
    free=[i for i in range(n) if i not in (0,n-2)];K=K[np.ix_(free,free)];M=M[np.ix_(free,free)]
    C=np.linalg.cholesky(M);inverse=np.linalg.inv(C);normal=inverse@K@inverse.T
    eigenvalues=np.linalg.eigvalsh((normal+normal.T)/2)
    if eigenvalues.min()<=0:raise ValueError('unstable modal eigenproblem')
    frequencies=np.sqrt(eigenvalues[:modes])/(2*math.pi)
    analytic=[j*j*math.pi/(2*length_m**2)*math.sqrt(ei_nm2/mass_per_m) for j in range(1,modes+1)]
    return dict(elements=elements,frequencies_hz=frequencies.tolist(),analytical_hz=analytic,
        relative_errors=[float(abs(x/y-1)) for x,y in zip(frequencies,analytic)],
        scope='Uniform equivalent beam only; actual floor/equipment contact, mode shapes, damping and vehicle transfer not represented')


def fatigue_damage(stress_ranges_pa,cycles,*,reference_range_pa,reference_cycles,slope):
    """Explicit S-N/Miner evaluator. Caller supplies its applicable measured curve."""
    if len(stress_ranges_pa)!=len(cycles) or not stress_ranges_pa:raise ValueError('paired nonempty fatigue spectrum required')
    for v,n in ((reference_range_pa,'reference range'),(reference_cycles,'reference cycles'),(slope,'S-N slope')):_positive(v,n)
    rows=[]
    for stress,count in zip(stress_ranges_pa,cycles):
        if type(stress) not in (int,float) or not math.isfinite(stress) or stress<0 or type(count) not in (int,float) or not math.isfinite(count) or count<0:raise ValueError('nonnegative finite stress range/cycles required')
        life=reference_cycles*(reference_range_pa/stress)**slope if stress else None
        damage=count/life if life else 0.
        rows.append(dict(stress_range_pa=stress,cycles=count,life_cycles=life,damage=damage))
    return dict(damage=sum(r['damage'] for r in rows),bins=rows,scope='Linear Miner accumulation on explicitly supplied S-N curve; no cutoff, mean stress, multiaxial or sequence effect model',qualified=False)


def weld_register(candidate):
    """Proposed dimensions and work instructions; never fabricated WPS/test data."""
    rows=[];floor=candidate['variables']['floor_thickness_m']
    for joint in candidate['contract']['assembly_joints']:
        identity=joint['id'];length=None
        if identity.startswith('crossmember-'):length=2*(.05+.08)
        elif identity.startswith('floor-rail-'):length=.60 # alternating six 50 mm stitches per side
        elif identity.startswith('floor-cross-'):length=.30 # six 50 mm stitches, distributed symmetrically
        elif identity.startswith('equipment-leg-'):length=.12 # 60 mm perimeter at foot and block
        if length is None:continue
        segments=[]
        if identity.startswith('floor-rail-'):
            side=-1 if identity.endswith('--1') else 1
            y=side*(candidate['metadata']['rail_spacing_m']/2+.030)
            segments=[dict(start_m=[x-.025,y,0.],end_m=[x+.025,y,0.],face='accessible underside floor lap to outer rail web') for x in (-.5,-.3,-.1,.1,.3,.5)]
            length=.30
        elif identity.startswith('floor-cross-'):
            index=int(identity.rsplit('-',1)[1]);x=candidate['metadata']['crossmember_positions_m'][index]
            segments=[dict(start_m=[x+side*.025,y-.025,0.],end_m=[x+side*.025,y+.025,0.],face='underside floor to crossmember side web') for side in (-1,1) for y in (-.3,0.,.3)]
        leg=.003;throat=leg/math.sqrt(2);density=candidate['contract']['materials']['steel']['density_kg_m3']
        rows.append(dict(joint_id=identity,physical_part_ids=joint['endpoints'],process='Proposed GMAW/MAG; qualified WPS required',
            weld_leg_m=leg,effective_throat_m=throat,total_proposed_length_m=length,
            effective_throat_area_m2=throat*length,bead_mass_allowance_kg=.5*leg**2*length*density,
            pattern='Symmetric balanced opposite-side progression',proposed_segments=segments,
            geometry_status='Straight stitch coordinates specified where applicable; weld bead is an explicit mass allowance, not a CAD solid',
            root_gap_target_m=0.,root_gap_acceptance_m=None,distortion_allowance_m=.0005,
            detail_category=None,WPS=None,welder_qualification=None,NDT_acceptance=None,
            inspection=['100% visual and dimensional planning','qualified surface/NDT method and acceptance to be adopted'],
            corrosion='Clean/inspect before compatible coating; mask dedicated earth/bearing surfaces',
            state='proposed; not issued or qualified'))
    return rows


def manufacturing_pack(candidate):
    from engineering.design_consistency import contracts
    summary=contracts.summary(candidate['contract']);welds=weld_register(candidate);stack=fastener_stack(candidate['variables']['floor_thickness_m'])
    parts=candidate['contract']['parts'];rows=[]
    for part in parts:
        rows.append(dict(id=part['id'],revision=candidate['revision'],material=part['material'],process=part['process_route'],
            primitives=part['manufacturing']['primitives'],placement=part['placement'],mass_kg=part['properties']['mass_kg'],
            dimensional_tolerance_m=.0005,inspection=part['inspection_characteristics'],drawing_state='unissued-provisional'))
    operations=[dict(id='cut',after=[],parts=[p['id'] for p in parts if p['geometric_role']=='manufactured-solid'],
        instruction='Saw RHS square, cut/drill plates and deburr; preserve part/material/heat trace'),
        dict(id='fixture-frame',after=['cut'],parts=[p['id'] for p in parts if p['id'].startswith(('longitudinal','crossmember'))],
             instruction='Set rail top datum A, centre B, bay centre C; inspect diagonals and end contact before welding'),
        dict(id='weld-frame',after=['fixture-frame'],parts=[p['id'] for p in parts if p['id'].startswith(('longitudinal','crossmember'))],
             instruction='Balanced opposite end progression; qualified WPS/tacks/heat input and distortion controls required'),
        dict(id='inspect-frame',after=['weld-frame'],parts=[],instruction='Verify datums, rail spacing, diagonals, surface condition and qualified NDT'),
        dict(id='floor',after=['inspect-frame'],parts=['floor-panel'],instruction='Locate through common drill jig; balanced floor stitch sequence; inspect distortion'),
        dict(id='equipment-subassembly',after=['cut'],parts=[p['id'] for p in parts if p['id'].startswith(('mount-foot','mount-leg'))]+['equipment-test-block'],
             instruction='Fixture feet and dummy block, weld/inspect; compare all four holes to gauge'),
        dict(id='mount',after=['floor','equipment-subassembly'],parts=[p['id'] for p in parts if p['id'].startswith('mount-')],
             instruction='Support dummy block; insert bolts from below, fit both washers and specified locking nuts. Do not issue torque from illustrative K-factor range'),
        dict(id='inspect-mounted',after=['mount'],parts=[],instruction='Inspect stack/projection, qualified preload, locking and witness identification'),
        dict(id='bench-test',after=['inspect-mounted'],parts=[],instruction='Measure actual mass/CG, control-load response, joint slip/strain and modes with calibrated apparatus'),
        dict(id='remove',after=['bench-test'],parts=[],instruction='Isolate and support dummy block; access nuts laterally under block, restrain lower heads, remove four bolts and lift supported subassembly. Lifting fixture/rating required')]
    return dict(schema='osr-structural-manufacturing-pack/1',candidate_revision=candidate['revision'],parts=rows,
        fastener_stack=stack,welds=welds,operations=operations,
        mass_ledger=dict(represented_solid_mass_kg=summary['mass_kg'],proposed_weld_allowance_kg=sum(w['bead_mass_allowance_kg'] for w in welds),
            coating_services_mass_kg=None,complete_installed_mass_kg=None,scope='CAD solids plus separately stated bead allowance; no hidden omission or complete mass claim'),
        fixtures=['Rail/end datum and diagonal fixture','Common floor/foot hole gauge','Supported dummy-block welding fixture','Rated bench and removal support'],
        tool_access=dict(lower_head='Vertical underside access proposed; verify actual fixture and lower supports',
            upper_nut='Lateral open/ring spanner under dummy block; vertical socket shaft intersects block and is not claimed',
            demonstrated=False),repair=dict(fasteners='Replace/inspect per qualified locking and preload procedure',
            welds='Approved defect/removal/repair WPS and reinspection required',floor='Replace with frame supported and requalify heat/distortion/attachments'),
        release_state='unissued-provisional; loads, WPS, metrology and independent engineering acceptance open',**core.FLAGS)


def report(policy,candidate):
    from engineering.design_consistency import contracts
    summary=contracts.summary(candidate['contract']);mass=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts'] if p['id'].startswith('mount-') or p['id']=='equipment-test-block')
    material=candidate['contract']['materials']['steel'];young=material['young_pa'];density=material['density_kg_m3'];fy=material['yield_reference_pa']
    floor=candidate['variables']['floor_thickness_m'];wall=candidate['variables']['rail_wall_m'];L=candidate['metadata']['length_m']
    mount=local_mount(positions_m=candidate['metadata']['mount_positions_m'],mass_kg=mass,cg_height_m=.11-floor,
        floor_m=floor,young_pa=young,yield_pa=fy)
    adverse=local_mount(positions_m=candidate['metadata']['mount_positions_m'],mass_kg=mass,cg_height_m=.11-floor,
        floor_m=floor,load_scale=1.1,young_pa=young,yield_pa=fy)
    degraded=[local_mount(positions_m=candidate['metadata']['mount_positions_m'],mass_kg=mass,cg_height_m=.11-floor,
        floor_m=floor,missing_bolt=i,young_pa=young,yield_pa=fy) for i in range(4)]
    # One-way strips intentionally provide no 2D floor/diaphragm credit.
    strip=floor_strip(force_n=mass*9.80665*3/4,span_m=candidate['metadata']['rail_spacing_m']-.06,width_m=.08,thickness_m=floor,young_pa=young,uniform_n_m=.08*floor*density*9.80665*3)
    from engineering.continuous_design import beam_confirmation
    strip_fem=beam_confirmation.solve(strip['span_m'],[0.,strip['span_m']],young*strip['inertia_m4'],
        points=[(strip['span_m']/2,strip['force_n'])],uniform=strip['uniform_n_m'],divisions=16)
    rail=candidate['contract']['parts'][0]['analysis']['section'];ei=young*rail['iy_m4']
    modes=[modal_beam(L,ei,summary['mass_kg']/(2*L),elements=n) for n in (8,16)]
    plate_critical=plate_buckling(width_m=.1-2*wall,thickness_m=wall,young_pa=young)
    welds=weld_register(candidate);weld_cases=[]
    maximum_reaction=summary['mass_kg']*9.80665*3/4
    for weld in welds:
        if weld['joint_id'].startswith('crossmember'):force=maximum_reaction
        elif weld['joint_id'].startswith('floor-'):
            floor_mass=next(p['properties']['mass_kg'] for p in candidate['contract']['parts'] if p['id']=='floor-panel')
            force=(floor_mass+mass)*9.80665*3/2
        else:force=mass*9.80665*3/4
        weld_cases.append(dict(joint_id=weld['joint_id'],load_n=force,average_throat_shear_pa=force/weld['effective_throat_area_m2'],
            proposed_limit_pa=.6*fy/math.sqrt(3),scope='Conservative apportioned gravity direct-average throat shear only; actual load sharing, eccentric stress, fatigue, HAZ and end effects remain open'))
    checks={}
    checks.update({'stack/'+name:value for name,value in fastener_stack(floor)['checks'].items()})
    for i,row in enumerate(mount['cases']):checks.update({'mount/'+str(i)+'/'+k:v for k,v in row['checks'].items()})
    checks['floor-strip/independent-fem']=abs(strip_fem['maximum_nodal_deflection_m']/strip['deflection_m']-1)<1e-7
    checks['floor-strip/equilibrium']=strip_fem['force_balance_relative_error']<1e-8
    checks['floor-strip/stress-provisional']=strip['stress_pa']<=.6*fy
    checks['floor-strip/deflection-provisional']=strip['deflection_m']<=.002
    checks['modal/closed-form-first-three']=max(modes[1]['relative_errors'])<.001
    checks['modal/mesh-refinement']=max(abs(x/y-1) for x,y in zip(modes[1]['frequencies_hz'],modes[0]['frequencies_hz']))<.002
    checks['weld/direct-shear-provisional']=all(c['average_throat_shear_pa']<=c['proposed_limit_pa'] for c in weld_cases)
    checks['mount/adverse-load-scaling']=all(abs(b['equivalent_thread_stress_pa']/a['equivalent_thread_stress_pa']-1.1)<1e-10 for a,b in zip(mount['cases'],adverse['cases']))
    for name in ('thread-stripping-and-selected-nut','nonlinear-contact-and-prying','local-shell-buckling-resistance','actual-modal-transfer-acceptance',
        'fatigue-duty-and-qualified-SN','qualified-preload-locking-and-WPS','physical-joint-panel-correlation'):
        checks[name]=None
    result=dict(schema='osr-structural-detail-screen/1',candidate_revision=candidate['revision'],checks=checks,
        failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        mount=mount,adverse_mount=adverse,one_bolt_missing=degraded,floor_strip=strip,floor_fem=strip_fem,
        modal=modes,rail_web_elastic_buckling_stress_pa=plate_critical,
        buckling_scope='Ideal simply supported internal plate elastic eigenstress, k=4; no welded RHS imperfections/postbuckling or rail design resistance',
        weld_register=welds,weld_shear_cases=weld_cases,
        fatigue=dict(state='hold',spectrum=None,SN_curve=None,damage=None,
            evaluator='engineering.assembly_design.structural_detail.fatigue_damage; explicit compatible curve and measured duty required'),
        manufacturing_pack=manufacturing_pack(candidate),sources=SOURCES,
        scope='Configuration-specific local elastic/detail/manufacturing research; no full-body, crash, fatigue life or qualified joint claim',**core.FLAGS)
    result['revision']=core.digest(result);return result
