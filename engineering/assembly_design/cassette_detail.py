"""Manufactured cassette detail variant and an explicit assembly test fixture.

Geometry is owned/proposed except exact purchased connector kit identities.
Supplier internal contacts/latches, qualification and actual vehicle host remain
open. Every added solid enters the same mass/BOM/QA contract and native verifier.
"""
from copy import deepcopy
import itertools
import math
import numpy as np

from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from . import models,cassette_system


def _cylinder(identity,radius,length,centre,axis='z',inner=None):
    p=dict(id=identity,kind='cylinder' if inner is None else 'tube',radius_m=radius,length_m=length,centre_m=list(centre),axis=axis)
    if inner is not None:p['inner_radius_m']=inner
    return p


def _plate(identity,L,W,t,centre,holes,radius):
    p=contracts.box(identity,L,W,t,centre)
    p.update(kind='perforated-plate',holes_xy_m=[list(v)for v in holes],hole_radius_m=radius)
    return p


def build(policy,base_candidate,*,guide_clearance_m=.009,connector_float_m=.006,seal_compression=.25):
    if base_candidate.get('kind')!='service-cassette' or core.digest(base_candidate)!=core.digest(models.build(policy,'service-cassette',base_candidate['variables'])):
        raise ValueError('exact controlled base cassette required')
    if guide_clearance_m not in (.003,.006,.009) or connector_float_m not in (.001,.006) or seal_compression not in (.15,.25,.35):
        raise ValueError('registered detailed assembly choices required')
    base=deepcopy(base_candidate);contract=base['contract'];parts=contract['parts'];materials=contract['materials'];joints=contract['assembly_joints']
    materials.update(seal=dict(density_kg_m3=1200.,basis='Unselected compliant seal/lining mass hypothesis; fire, ageing and compression-set unqualified'),
        brass=dict(density_kg_m3=8500.,basis='Equivalent solder-cup envelope mass hypothesis, not exact contact alloy/shape'))
    groups={p['id']:'host-fixed' if p['id'].startswith('vehicle-interface-') else 'cassette-moving' for p in parts}
    for p in parts:
        if p['id'].startswith('mount-'):groups[p['id']]='retention-removable'
    def add(identity,primitives,material='steel',*,placement=None,group='cassette-moving',process='cut/form/drill/deburr to controlled proposed dimensions',role='owned-manufactured-solid'):
        p=contracts.part(identity,material,dict(role=identity,primitives=primitives),materials,placement=placement,
            limits=dict(tolerance_m=.0005,tolerance_status='proposed; capability unmeasured'),
            inspections=['material/part identity','dimensions/datums','surface/edge condition','assembly interface and retention'])
        p.update(manufacturing_unit_id=identity,geometric_role=role,process_route=process,
            datum_scheme={'A':'tray mounting plane z=0','B':'cassette centre plane y=0','C':'front stop x=0.6'},procurement=None)
        parts.append(p);groups[identity]=group;return p
    def replace(identity,primitives,material=None,**kw):
        old=next(p for p in parts if p['id']==identity);parts.remove(old)
        return add(identity,primitives,material or old['material'],group=groups[identity],**kw)
    def box(identity,L,W,H,c,**kw):return add(identity,[contracts.box(identity,L,W,H,c)],**kw)
    def joint(identity,endpoints,mechanism,fasteners=()):
        joints.append(dict(id=identity,endpoints=list(endpoints),mechanism=mechanism,fastener_ids=list(fasteners),
            tolerance_m=.0005,load_case_ids=['vertical','longitudinal','lateral'],qualified=False,capacity_evidence=None,
            inspection=['identity','fit','retention/locking','measured interface function']))
    # The original top-mounted host pads obstruct the prefabricated duct feet
    # during sliding. Relocate the proposed host pads below the rail and bind a
    # new complete bolt stack; this is an explicit interface change, not a claim
    # that the previous host was installable.
    d=base['variables']['bolt_diameter_m']
    for i,(x,y)in enumerate(( (x,y)for x in (-.5,.5)for y in (-.12,.12))):
        replace('vehicle-interface-'+str(i),[_plate('lower-host-pad',.07,.07,.006,[x,y,-.063],[(0,0)],d*.55)])
        replace('mount-'+str(i)+'-bolt',[_cylinder('shank',d/2,.075,[x,y,-.0315]),
            _cylinder('head',.9*d,.6*d,[x,y,.006+.3*d])],role='hardware-envelope')
        replace('mount-'+str(i)+'-upper-washer',[_cylinder('washer',d,.003,[x,y,.0045],inner=d*.53)])
        replace('mount-'+str(i)+'-lower-washer',[_cylinder('washer',d,.003,[x,y,-.0675],inner=d*.53)])
        replace('mount-'+str(i)+'-nut',[_cylinder('nut',d,.8*d,[x,y,-.069-.4*d],inner=d*.53)],role='hardware-envelope')
    # An actual removable cover, drilled tabs, controlled seal strips and hardware.
    holes=[(x,y)for x in (-.48,-.16,.16,.48)for y in (-.165,.165)]
    cover=add('inspection-cover',[_plate('cover',1.2,.35,.0015,[0,0,.15275],holes,.0022)])
    for side in (-1,1):
        box('cover-side-seal-'+str(side),1.194,.003,.002,[0,side*.1735,.151],material='seal')
    for i,(x,y)in enumerate(holes):
        add('cover-tab-'+str(i),[_plate('tab',.02,.014,.003,[x,y,.1485],[(0,0)],.0022)])
        add('cover-screw-'+str(i),[_cylinder('M4-shank',.002,.0115,[x,y,.14875]),
            _cylinder('head-envelope',.0035,.003,[x,y,.156])],group='cover-removable',process='M4 captive screw envelope; grade/thread/captivity/torque qualification open',role='hardware-envelope')
        add('cover-washer-'+str(i),[_cylinder('washer',.004,.001,[x,y,.154],inner=.0022)],group='cover-removable')
        add('cover-nut-'+str(i),[_cylinder('nut-envelope',.004,.003,[x,y,.1455],inner=.0022)],process='M4 nut envelope; engagement/locking/preload qualification open',role='hardware-envelope')
        joint('cover-fastener-'+str(i),['inspection-cover','cover-tab-'+str(i),'cover-screw-'+str(i),'cover-washer-'+str(i),'cover-nut-'+str(i)],'removable cover fastening, proposed M4; torque and capture qualification open',['cover-screw-'+str(i)])
    groups['inspection-cover']='cover-removable'
    # Straight cut/stripped paths have exact terminals and no invented wire bends.
    # Contact cup and kit housing envelopes are intentionally distinguished.
    pitch_y=[.122+.004*i for i in range(10)];wire_start=-.4;female_body_rear=.5635;male_body_rear=.58935
    female_cup_start=female_body_rear-.005;male_cup_end=male_body_rear+.005
    route_records=[]
    for i in range(8):
        y=pitch_y[i];radius=math.sqrt(cassette_system.awg_area(14)/math.pi)
        replace('wire-'+str(i)+'-conductor',[_cylinder('conductor',radius,female_body_rear-wire_start,[(female_body_rear+wire_start)/2,y,.07],'x')],material='copper')
        replace('wire-'+str(i)+'-jacket',[_cylinder('jacket',.0018,female_cup_start-wire_start,[(female_cup_start+wire_start)/2,y,.07],'x',inner=radius)],material='insulation')
        mr=math.sqrt(cassette_system.awg_area(12)/math.pi);end=male_body_rear+1.
        add('host-wire-'+str(i)+'-conductor',[_cylinder('conductor',mr,1.,[(end+male_body_rear)/2,y,.07],'x')],material='copper',group='service-removable')
        add('host-wire-'+str(i)+'-jacket',[_cylinder('jacket',.002,1.-.005,[(end+male_cup_end)/2,y,.07],'x',inner=mr)],material='insulation',group='service-removable')
        for side,awg,start,finish,strip,part in [('cassette',14,wire_start,female_body_rear,female_cup_start,'M80-326'),('vehicle',12,male_body_rear,end,male_cup_end,'M80-335')]:
            route_records.append(dict(id=side+'-W'+str(i+1),pin=i+1,awg=awg,area_m2=cassette_system.awg_area(awg),
                centreline_m=[[start,y,.07],[finish,y,.07]],cut_length_m=finish-start,strip_length_m=.005,
                terminal=part,termination='solder, IS-52 issue2',wire_type=None,minimum_bend_radius_m=None,
                topology='straight proposed routing; no bend exists in this represented path',
                source_role='owned routing hypothesis; source-specific contact mating internals remain purchased'))
    for end in range(2):
        old=next(p for p in parts if p['id']=='cable-clamp-'+str(end));primitive=deepcopy(old['manufacturing']['primitives'][0])
        primitive['holes_xy_m']=[[0.,pitch_y[i]-.138]for i in range(8)]
        placement=old['placement'];replace(old['id'],[primitive],placement=placement)
        for i in range(8):
            add('clamp-lining-'+str(end)+'-'+str(i),[_cylinder('assembled-lining',.0019,.008,[(-.3,.3)[end],pitch_y[i],.07],'x',inner=.0018)],material='seal')
            joint('lined-clamp-'+str(end)+'-'+str(i),['cable-clamp-'+str(end),'clamp-lining-'+str(end)+'-'+str(i),'wire-'+str(i)+'-jacket'],'compliant cable retention; nominal assembled fit only, measured pull/wear required')
    # Equivalent supplier mass is conserved after explicit cup envelopes are split
    # out of each kit. These envelopes are not vendor cavity/contact CAD.
    cup_volumes={}
    for side,start,finish,inner,group in [('female',female_cup_start,female_body_rear,.00095,'cassette-moving'),('male',male_body_rear,male_cup_end,.0011,'service-removable')]:
        cup_volumes[side]=10*math.pi*(.0015**2-inner**2)*.005
        for i,y in enumerate(pitch_y):
            add(side+'-solder-cup-'+str(i+1),[_cylinder('solder-cup-envelope',.0015,.005,[(start+finish)/2,y,.07],'x',inner=inner)],material='brass',group=group,
                process='purchased exact contact supplied loose; envelope only; actual cup, retention and solder geometry supplier-controlled',role='supplier-terminal-envelope')
    female_mass=.005722-cup_volumes['female']*materials['brass']['density_kg_m3']
    male_mass=.005449-cup_volumes['male']*materials['brass']['density_kg_m3']
    materials['female-kit-remainder']=dict(density_kg_m3=female_mass/(.013*.05*.0055),basis='Published5.722g complete kit less represented10cup envelope mass; remainder is coordination allowance')
    materials['male-kit-remainder']=dict(density_kg_m3=male_mass/(.0127*.05*.006),basis='Published5.449g complete kit less represented10cup envelope mass; remainder is coordination allowance')
    replace('power-connector',[contracts.box('female-kit-remainder',.013,.05,.0055,[.57,.14,.07])],material='female-kit-remainder',role='supplier-coordination-envelope')
    add('mating-power-connector',[contracts.box('male-kit-remainder',.0127,.05,.006,[.583,.14,.07])],material='male-kit-remainder',group='service-removable',role='supplier-coordination-envelope')
    for p in parts:
        if p['id']in('power-connector','mating-power-connector'):
            p['procurement']=dict(part=cassette_system.FEMALE if p['id']=='power-connector'else cassette_system.MALE,
                origin='GB supplier page',internal_geometry_defined=False,kit_mass_includes_cups=True)
    joint('exact-connector-pair',['power-connector','mating-power-connector'],
          'Documented mating kits;0.15mm envelope separation is a coordination hypothesis, not actual insertion/contact wipe or jackscrew qualification')
    # Raised and replaceable dedicated bond; rectangular ring/neck and barrel
    # envelope are now physically represented. Delivered lug/tool remains open.
    replace('earth-stud',[_cylinder('M8-stud',.004,.03,[-.52,0,.018])])
    replace('earth-lug-envelope',[_plate('ring-land',.02,.02,.002,[-.52,0,.021],[(0,0)],.0045),
        contracts.box('lug-neck',.006,.015,.002,[-.52,-.0175,.021]),
        _cylinder('lug-barrel',.0025,.01,[-.52,-.03,.021],'y',inner=.0018)],material='copper',role='terminal-envelope')
    replace('earth-washer',[_cylinder('washer',.008,.001,[-.52,0,.0225],inner=.0045)])
    replace('earth-locknut-envelope',[_cylinder('nut-envelope',.007,.006,[-.52,0,.026],inner=.0045)])
    br=math.sqrt(10e-6/math.pi)
    add('earth-conductor',[_cylinder('10mm2-core',br,.19,[-.52,-.12,.021],'y')],material='copper',group='service-removable')
    add('earth-conductor-insulation',[_cylinder('insulation',.003,.17,[-.52,-.12,.021],'y',inner=br)],material='insulation',group='service-removable')
    add('host-earth-terminal',[_cylinder('host-barrel-envelope',.0025,.01,[-.52,-.21,.021],'y',inner=.0018)],material='copper',group='service-removable',role='terminal-envelope')
    joint('routed-protective-bond',['earth-lug-envelope','earth-conductor','host-earth-terminal'],
          'Explicit straight bond core/strip/barrel envelopes; crimp tool/die/strain relief, fault-current and installed resistance remain unqualified')
    # Open framed duct ends, seal compression and separable host port faces.
    area=base['metadata']['duct_clear_area_m2'];w=.2;h=area/w;zc=.041+h/2;compressed=.003*(1-seal_compression)
    def frame(identity,x,depth,material,group):
        # Four touching strips, no overcounted corner volumes.
        primitives=[contracts.box('bottom',depth,w+.02,.01,[x,0,zc-h/2-.005]),
                    contracts.box('top',depth,w+.02,.01,[x,0,zc+h/2+.005]),
                    contracts.box('side--1',depth,.01,h,[x,-w/2-.005,zc]),
                    contracts.box('side-1',depth,.01,h,[x,w/2+.005,zc])]
        return add(identity,primitives,material=material,group=group)
    for sign in (-1,1):
        frame('duct-flange-'+str(sign),sign*.4525,.005,'steel','cassette-moving')
        frame('duct-end-seal-'+str(sign),sign*(.455+compressed/2),compressed,'seal','cassette-moving')
        frame('host-duct-face-'+str(sign),sign*(.455+compressed+.0025),.005,'steel','service-removable')
        joint('duct-port-'+str(sign),['duct-flange-'+str(sign),'duct-end-seal-'+str(sign),'host-duct-face-'+str(sign)],
              'Proposed compressed3mm seal and removable flat host face; flange fastening/clamping force and measured leak/fire performance open')
    # The host fixture is an explicit proposed mating interface, not the actual
    # six-car underframe. Its stops, guide bores and pin ears are real solids.
    guide_y=.175+guide_clearance_m+.006
    ry=[[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]]
    # A real insulated passage avoids routing the bond through solid tray steel.
    replace('tray-side--1',[_plate('bond-passage-sidewall',1.2,.147,.003,[0,0,0],[(-.52,.0555)],.0045)],
        placement=dict(translation_m=[0,-.1735,.0765],rotation=ry))
    add('bond-tray-grommet',[_cylinder('grommet',.0045,.003,[-.52,-.1735,.021],'y',inner=.003)],material='seal')
    for sign in (-1,1):
        add('host-support-'+str(sign),[_plate('support-with-nut-access',1.35,.08,.004,[0,sign*.12,-.068],[(-.5,0),(.5,0)],.0275)],group='host-fixed')
        hole_positions=[(x,.07)for x in (-.55,.55)]
        if sign==-1:hole_positions.append((-.52,.019))
        add('host-guide-'+str(sign),[_plate('guide-web',1.35,.23,.012,[0,0,0],hole_positions,.0045)],
            placement=dict(translation_m=[0,sign*guide_y,.04],rotation=ry),group='host-fixed')
        if sign==-1:add('bond-host-grommet',[_cylinder('grommet',.0045,.012,[-.52,-guide_y,.021],'y',inner=.003)],material='seal',group='host-fixed')
        for end,x in enumerate((-.55,.55)):
            eid='pin-ear-'+str(sign)+'-'+str(end)
            add(eid,[_plate('ear',.02,.02,.03,[0,0,0],[(0,0)],.0045)],
                placement=dict(translation_m=[x,sign*.16,-.03],rotation=ry))
            add(eid+'-bridge',[_plate('bridge-with-pin-bore',.02,.02,.005,[0,0,0],[(0,0)],.0045)],
                placement=dict(translation_m=[x,sign*.1425,-.03],rotation=ry))
            # Pin ends at0.14; it does not penetrate the existing rail web.
            pin_end=guide_y+.012
            add('positive-pin-'+str(sign)+'-'+str(end),[_cylinder('pin',.004,pin_end-.14,[x,sign*(pin_end+.14)/2,-.03],'y'),
                _cylinder('head',.007,.003,[x,sign*(pin_end+.0015),-.03],'y')],group='retention-removable',role='hardware-envelope',
                process='8mm locating/retention pin envelope; secondary retention, wear and material qualification open')
            joint('pin-lock-'+str(sign)+'-'+str(end),[eid,'host-guide-'+str(sign),'positive-pin-'+str(sign)+'-'+str(end)],
                'Positive through-pin in two bores; captive/secondary lock, wear and load sharing require qualification',['positive-pin-'+str(sign)+'-'+str(end)])
        box('host-end-stop-'+str(sign),.01,.04,.04,[.605,sign*.12,-.03],group='host-fixed')
    box('seat-indicator-envelope',.015,.02,.012,[.628,0,.018],group='host-fixed',role='supplier-coordination-envelope')
    route_lengths={side:sum(r['cut_length_m']for r in route_records if r['id'].startswith(side))for side in ('cassette','vehicle')}
    installed_ids=[p['id']for p in parts if groups[p['id']]!='host-fixed' and
        (groups[p['id']]!='service-removable' or p['id']in ('earth-conductor','earth-conductor-insulation'))]
    data=dict(base_candidate_revision=base_candidate['revision'],base_variables=base_candidate['variables'],
        detailed_choices=dict(guide_clearance_m=guide_clearance_m,connector_float_m=connector_float_m,seal_compression=seal_compression),
        ownership_groups=groups,harness_routes=route_records,harness_cut_totals_m=route_lengths,
        connector_kit_masses_kg={'female':.005722,'male':.005449},
        host_fixture='Proposed cassette mating fixture, not adopted vehicle geometry',
        seal_free_thickness_m=.003,seal_installed_thickness_m=compressed,duct_clear_area_m2=area,
        cassette_installed_part_ids=installed_ids,
        base_known_failures_preserved=True)
    revision=core.digest(dict(base=base_candidate['revision'],parts=parts,materials=materials,joints=joints,metadata=data))
    for part in parts:part['revision']=revision;part['joints']=[j['id']for j in joints if part['id']in j['endpoints']]
    contract.update(name='service-cassette-detail',revision=revision,parts=parts,mandatory_evidence=list(cassette_system.OPEN_GATES))
    contracts.validate(contract)
    return dict(schema='osr-assembly-design-candidate/1',kind='service-cassette-detail',variables=data['detailed_choices'],revision=revision,
        requirement_ids=base['requirement_ids'],contract=contract,metadata=data,
        assembly_steps=['bench fabricate and inspect','fit routed harness/duct/bond','remove cover and transport restraints',
            'support and slide through proposed host guides','insert four positive pins and four secondary mounting bolts',
            'torque and inspect with cover removed','connect earth before services','connect exact mating kits and duct faces',
            'installed bond/electrical/leak/function tests','fit cover','isolate, remove cover, disconnect services, remove bond, support, unlock and withdraw'],
        qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False)for p in parts],
        source_scope='Detailed owned solids plus declared bought-out envelopes and proposed host assembly fixture; physical acceptance absent',
        open_requirements=list(cassette_system.OPEN_GATES),**core.FLAGS)


def primitive_bounds(part,primitive):
    c=np.asarray(primitive['centre_m']);kind=primitive['kind']
    if kind in ('box','plate','perforated-plate'):extent=np.asarray(primitive['dimensions_m'])/2
    elif kind in ('cylinder','tube','perforated-cylinder'):
        extent=np.full(3,primitive['radius_m']);extent['xyz'.index(primitive['axis'])]=primitive['length_m']/2
    else:raise ValueError('unsupported assembly clearance primitive')
    rotation=np.asarray(part['placement']['rotation']);centre=rotation@c+part['placement']['translation_m'];radius=np.abs(rotation)@extent
    return [centre-radius,centre+radius]


def _overlap(a,b,tolerance=1e-9):return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>tolerance))


def path_check(candidate,*,offset_m=(0.,0.,0.),travel_m=1.3,extra_obstacles=()):
    """Conservative continuous translation sweep of every moving primitive.

    Exact AABBs for the represented fixed-axis boxes and swept primitive bounds
    are checked. Positive hits are conservative potential collisions, including
    holes; a clear result proves only the stated rigid translational fixture.
    Detached pins, cover and service tails are excluded by operation state.
    """
    if not math.isfinite(travel_m) or travel_m<=0 or len(offset_m)!=3 or not all(math.isfinite(v)for v in offset_m):raise ValueError('finite rigid travel and offset required')
    parts=candidate['contract']['parts'];groups=candidate['metadata']['ownership_groups'];fixed=[];moving=[]
    for part in parts:
        dest=fixed if groups[part['id']]=='host-fixed' else moving if groups[part['id']]=='cassette-moving' else None
        if dest is not None:
            for primitive in part['manufacturing']['primitives']:dest.append((part['id'],primitive_bounds(part,primitive)))
    for obstacle in extra_obstacles:
        bounds=np.asarray(obstacle['bounds_m'],float)
        if not obstacle.get('id')or bounds.shape!=(2,3)or not np.isfinite(bounds).all()or np.any(bounds[0]>bounds[1]):raise ValueError('named finite ordered3D obstacle bounds required')
        fixed.append((obstacle['id'],[bounds[0],bounds[1]]))
    hits=[];shift=np.asarray(offset_m)
    for identity,bounds in moving:
        swept=[bounds[0]+shift-np.array([travel_m,0,0]),bounds[1]+shift]
        for obstacle,other in fixed:
            if _overlap(swept,other):hits.append(dict(moving_part=identity,fixed_part=obstacle))
    complete=travel_m>=1.3
    return dict(passed=not hits and complete,potential_collisions=hits,moving_primitive_count=len(moving),fixed_primitive_count=len(fixed),
        complete_withdrawal=complete,required_withdrawal_m=1.3,
        travel_m=travel_m,offset_m=list(offset_m),method='Continuous swept primitive AABB, rigid negative-x withdrawal/positive-x insertion',
        state='cover/pins/mount bolts/bond/plug/host duct faces removed before motion; fixture carries temporary support',
        actual_vehicle_verified=False,compliant_contact_or_human_ergonomics_verified=False)


def tool_check(candidate,*,cover_installed=False,approach='underside-nut-and-short-head-wrench'):
    if approach not in ('underside-nut-and-short-head-wrench','top-socket'):raise ValueError('registered tool approach required')
    parts=candidate['contract']['parts'];groups=candidate['metadata']['ownership_groups'];collisions=[]
    for i,(x,y)in enumerate(( (x,y)for x in (-.5,.5)for y in (-.12,.12))):
        d=candidate['metadata']['base_variables']['bolt_diameter_m'];head_top=.006+.6*d
        if approach=='top-socket':tools=[('top-socket',[np.array([x-.025,y-.025,head_top]),np.array([x+.025,y+.025,head_top+.15])])]
        else:
            nut_bottom=-.069-.8*d
            tools=[('underside-socket',[np.array([x-.025,y-.025,nut_bottom-.15]),np.array([x+.025,y+.025,-.069])]),
                   ('short-head-wrench',[np.array([x-.02,y-.02,head_top-.006]),np.array([x+.02,y+.02,head_top])])]
        for name,tool in tools:
            for part in parts:
                if part['id'].startswith('mount-')or groups[part['id']]in ('service-removable','cover-removable')and not cover_installed:continue
                if part['id'].startswith('cover-')and not cover_installed:continue
                hit=False
                for primitive in part['manufacturing']['primitives']:
                    if not _overlap(tool,primitive_bounds(part,primitive)):continue
                    # Exact circular socket within an unrotated through-hole:
                    # its square bounding box corners are not physical material.
                    if name=='underside-socket' and primitive['kind']=='perforated-plate' and np.allclose(part['placement']['rotation'],np.eye(3)):
                        c=np.asarray(primitive['centre_m'])+part['placement']['translation_m']
                        if any(math.hypot(x-c[0]-hx,y-c[1]-hy)+.025<=primitive['hole_radius_m']for hx,hy in primitive['holes_xy_m']):continue
                    hit=True
                if hit:
                    collisions.append(dict(tool='mount-'+name+'-'+str(i),part=part['id']))
    return dict(passed=not collisions,potential_collisions=collisions,cover_installed=cover_installed,
        approach=approach,socket_envelope_m=[.05,.05,.15],scope='Conservative socket and short holding-wrench AABBs for four mount bolts, not every service tool or human access')


def retention_screen(candidate,*,missing_pin=False):
    mass=sum(p['properties']['mass_kg']for p in candidate['contract']['parts']if p['id']in candidate['metadata']['cassette_installed_part_ids'])
    demand=(mass+100.)*9.81*5.;pins=3 if missing_pin else 4;area=math.pi*.008**2/4
    shear=demand/(pins*area);bearing=demand/(pins*.008*.03)
    return dict(suspended_cassette_mass_kg=mass,payload_hypothesis_kg=100.,longitudinal_factor_hypothesis=5.,
        longitudinal_force_n=demand,pin_count=pins,single_shear_pa=shear,ear_bearing_pa=bearing,
        nominal_reference_shear_limit_pa=120e6,nominal_reference_bearing_limit_pa=200e6,
        checks=dict(nominal_pin_shear=shear<=120e6,nominal_ear_bearing=bearing<=200e6,all_required_pins=not missing_pin),
        pin_material_qualified=False,secondary_bolt_capacity_qualified=False,fatigue_wear_and_load_sharing_qualified=False)


def carrier_structure(policy,candidate):
    """Existing independent beam/bolt adapters with the actual installed mass.

    All cassette covers, fasteners, pin and bond allocations are retained. Host
    fixture and detached vehicle loom mass are separately scoped. No credit is
    taken for load sharing between the new pins and the secondary bolt group.
    """
    from . import baseline,evaluate
    from engineering.continuous_design import beam_confirmation
    from engineering.integration_programme import joints
    a=policy['pilots']['service-cassette']['assumptions'];facts=baseline.facts(policy)
    rows=[p for p in candidate['contract']['parts']if p['id']in candidate['metadata']['cassette_installed_part_ids']]
    mass=sum(p['properties']['mass_kg']for p in rows)
    cg=[sum(p['properties']['mass_kg']*p['properties']['cg_m'][i]for p in rows)/mass for i in range(3)]
    width,height=.04,.06;t=candidate['metadata']['base_variables']['rail_wall_m']
    inertia=(width*height**3-(width-2*t)*(height-2*t)**3)/12;ei=2*facts['steel.elastic_modulus']*inertia
    length=a['length_m'];supports=[(length-a['mount_span_m'])/2,(length+a['mount_span_m'])/2];cases=[];checks={}
    for payload in a['payload_kg']:
        force=(mass+payload)*a['gravity_m_s2']*a['vertical_factor']
        analytical=evaluate.overhang_beam(length,supports,ei,force/length)
        numerical=beam_confirmation.solve(length,supports,ei,uniform=force/length,divisions=32)
        stress=analytical['maximum_moment_nm']*(height/2)/(2*inertia)
        checks['gross-beam-stress-'+str(payload)]=stress<=355e6*a['steel_stress_fraction']
        checks['gross-beam-deflection-'+str(payload)]=analytical['maximum_deflection_m']<=a['deflection_limit_m']
        checks['gross-beam-independent-refinement-'+str(payload)]=abs(numerical['maximum_nodal_deflection_m']/analytical['maximum_deflection_m']-1)<.01
        checks['gross-beam-equilibrium-'+str(payload)]=numerical['force_balance_relative_error']<1e-7
        cases.append(dict(payload_kg=payload,applied_force_n=force,stress_pa=stress,analytical=analytical,numerical=numerical))
    diameter=candidate['metadata']['base_variables']['bolt_diameter_m']
    area=next(v for k,v in facts['bolts.stress_areas'].items()if float(k)==diameter)
    positions=[[x,y,0.]for x in (-.5,.5)for y in (-.12,.12)]
    group=joints.bolt_group(positions,diameter,.069,facts['steel.elastic_modulus']);bolt_cases=[]
    gross=mass+max(a['payload_kg']);lever=np.asarray(cg)+np.array([0.,0.,.0315])
    for signs in itertools.product((-1,1),repeat=3):
        force=np.asarray([gross*a['gravity_m_s2']*a[name]*sign for name,sign in zip(('longitudinal_factor','lateral_factor','vertical_factor'),signs)])
        moments=np.cross(lever,force);solved=joints.assess(group,[*force.tolist(),*moments.tolist()])
        equivalent=max(math.sqrt(max(0.,z)**2+3*(x*x+y*y))/area for x,y,z in solved['bolt_forces_n'])
        bolt_cases.append(dict(signs=list(signs),peak_equivalent_stress_pa=equivalent,result=solved))
    peak=max(v['peak_equivalent_stress_pa']for v in bolt_cases)
    checks['mount-thread-area-elastic-demand']=peak<=a['bolt_equivalent_stress_limit_pa']
    checks['mount-six-resultant-equilibrium']=all(v['result']['resultant_relative_error']<1e-10 for v in bolt_cases)
    return dict(candidate_revision=candidate['revision'],cassette_installed_mass_kg=mass,cassette_installed_cg_m=cg,
        included_part_ids=[p['id']for p in rows],beam_cases=cases,bolt_cases=bolt_cases,bolt_stress_area_m2=area,
        peak_mount_equivalent_stress_pa=peak,checks=checks,qualified_strength=False,
        scope='Gross equivalent two-rail beam and full-demand six-resultant elastic bolt group on actual defined cassette installed mass; local weld/holes/prying/preload/buckling/fatigue/shock/physical strength remain held')


def evaluate(policy,candidate):
    base=models.build(policy,'service-cassette',candidate['metadata']['base_variables'])
    expected=build(policy,base,**candidate['variables'])
    if core.digest(candidate)!=core.digest(expected):raise ValueError('detailed cassette differs from controlled definition')
    path=path_check(candidate);tools=tool_check(candidate);closed=tool_check(candidate,cover_installed=True,approach='top-socket')
    stack=cassette_system.tolerance_stack(clearance_m=candidate['variables']['guide_clearance_m'],connector_float_m=candidate['variables']['connector_float_m'])
    base_result=cassette_system.report(policy,base);seal=seal_stack(candidate)
    lengths=candidate['metadata']['harness_cut_totals_m'];electrical=cassette_system.electrical_case(female_length_m=lengths['cassette']/8,male_length_m=lengths['vehicle']/8)
    retention=retention_screen(candidate);properties=contracts.summary(candidate['contract'])
    carrier=carrier_structure(policy,candidate)
    top=float(max(primitive_bounds(p,primitive)[1][2]for p in candidate['contract']['parts']if p['id']=='duct-top'for primitive in p['manufacturing']['primitives']))
    checks=dict(clear_host_insertion_removal=path['passed'],mount_tool_access_cover_removed=tools['passed'],
        cover_blocks_mount_tool_as_negative_control=not closed['passed'],guide_tolerance=stack['checks']['guide_fit'],
        connector_float_tolerance=stack['checks']['connector_float'],seal_compression_range=seal['within_proposed_range'],
        nominal_pin_shear=retention['checks']['nominal_pin_shear'],nominal_ear_bearing=retention['checks']['nominal_ear_bearing'],
        routed_harness_power_balance=electrical['checks']['kirchhoff_balance'],
        duct_below_inspection_cover=top<=.15,
        exact_supplier_mating_geometry=None,actual_vehicle_interface=None,protective_devices_and_derating=None,
        qualified_seal_clamping_force=None,physical_environment_and_assembly=None,
        qualified_frame_weld_local_buckling_fatigue=None,mount_preload_prying_member_resistance=None,
        adopted_shock_and_vibration_qualification=None)
    checks.update(carrier['checks'])
    superseded={'worst_case_guide_fit':'guide_tolerance','worst_case_connector_float':'connector_float_tolerance'}
    for failure in base_result['failed_checks']:
        if failure not in superseded:checks['inherited/'+failure]=False
    checks={key:None if value is None else bool(value)for key,value in checks.items()}
    return dict(schema='osr-service-cassette-detail-evaluation/1',candidate_revision=candidate['revision'],checks=checks,
        failed_checks=[k for k,v in checks.items()if v is False],held_checks=[k for k,v in checks.items()if v is None],
        insertion_removal=path,mount_tools=tools,cover_on_tool_negative_control=closed,tolerance_stack=stack,
        seal_stack=seal,retention=retention,routed_electrical=electrical,represented_properties=properties,
        carrier_structure=carrier,
        baseline_constraint_replacements=[dict(original_check=old,original_candidate_revision=base['revision'],
            replacement_check=new,revised_candidate_revision=candidate['revision'],replacement_passed=checks[new])
            for old,new in superseded.items()],
        original_baseline_failed_checks=base_result['failed_checks'],original_baseline_held_checks=base_result['held_checks'],
        state='failed'if any(v is False for v in checks.values())else'hold',digital_specification_complete=False,
        exact_supplier_contacts='Explicit cups are solder-process envelopes; actual housing internals, mating wipe and jackscrew profiles remain supplier-controlled',
        scope='Owned detail geometry and controlled host fixture rigid sweeps/tool/nominal pin/seal/routed DC screens; no actual vehicle fit or qualification',**core.FLAGS)


def seal_stack(candidate,*,free_tolerance_m=.00015,gap_tolerance_m=.0001):
    free=candidate['metadata']['seal_free_thickness_m'];gap=candidate['metadata']['seal_installed_thickness_m']
    if free_tolerance_m<0 or gap_tolerance_m<0 or free_tolerance_m>=free:raise ValueError('physical seal tolerance required')
    minimum=1-(gap+gap_tolerance_m)/(free-free_tolerance_m)
    maximum=1-(gap-gap_tolerance_m)/(free+free_tolerance_m)
    return dict(nominal_fraction=1-gap/free,minimum_fraction=minimum,maximum_fraction=maximum,
        proposed_range=[.1,.4],within_proposed_range=minimum>=.1 and maximum<=.4,
        supplier_compression_force_map=None,clamping_force_n=None,compression_set_qualified=False,
        scope='Worst-case geometric squeeze only; range hypothesis is not supplier seal performance')
