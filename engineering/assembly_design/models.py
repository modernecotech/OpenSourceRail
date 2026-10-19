"""Manufacturing-unit generators with shared geometry, joints, datums and QA."""
from copy import deepcopy
import itertools
import math

from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from . import baseline


def candidates(policy,kind):
    domains=policy['pilots'][kind]['domains']
    for values in itertools.product(*domains.values()):yield dict(zip(domains,values))


def validate(policy,kind,variables):
    domains=policy['pilots'][kind]['domains']
    if set(variables)!=set(domains):raise ValueError('exact design variables required')
    if any(not any(type(v) is type(c) and v==c for c in domains[k]) for k,v in variables.items()):raise ValueError('unregistered design choice')


def build(policy,kind,variables):
    validate(policy,kind,variables);f=baseline.facts(policy);p=policy['pilots'][kind];a=p['assumptions'];parts=[];joints=[]
    materials=dict(steel=dict(density_kg_m3=f['steel.density'],young_pa=f['steel.elastic_modulus'],poisson=.3,basis='Nominal reference; heat, temperature, weld and fatigue qualification open'),
        grout=dict(density_kg_m3=2200.,basis='Unqualified grout mass hypothesis; strength and installation not inferred'),
        copper=dict(density_kg_m3=8960.,basis='Nominal copper mass hypothesis'),
        insulation=dict(density_kg_m3=1400.,basis='Unqualified mass/geometry hypothesis; not a selected rail insulation'),
        purchased=dict(density_kg_m3=1.,basis='Coordination envelope with explicit equivalent mass; no internal stiffness or supplier CAD claim'))
    def add(id,primitives,*,material='steel',route='cut/drill/deburr',role='manufactured-solid',supplier=None):
        value=contracts.part(id,material,dict(role=id,primitives=primitives),materials,
            limits=dict(tolerance_m=a['dimensional_tolerance_m'],tolerance_status='proposed-unqualified',minimum_wall_m=None),
            inspections=['material/part identity','dimensions and hole positions','edge condition','joint/interface inspection'])
        value.update(manufacturing_unit_id=id,geometric_role=role,procurement=supplier,
            process_route=route,datum_scheme={'A':'mounting plane z','B':'longitudinal centre plane y','C':'transverse centre plane x'})
        parts.append(value);return value
    def plate(id,L,W,t,c,holes=()):
        primitive=contracts.box(id,L,W,t,c)
        if holes:primitive.update(kind='perforated-plate',holes_xy_m=[list(h) for h in holes],hole_radius_m=d*.55)
        return add(id,[primitive])
    def block(id,L,W,H,c,**kw):return add(id,[contracts.box(id,L,W,H,c)],**kw)
    def cylinder(id,r,L,c,inner=None):
        primitive=dict(id=id,kind='cylinder' if inner is None else 'tube',centre_m=list(c),radius_m=r,length_m=L,axis='z')
        if inner is not None:primitive['inner_radius_m']=inner
        return primitive
    def joint(id,ends,mechanism,fasteners=()):
        joints.append(dict(id=id,endpoints=list(ends),mechanism=mechanism,fastener_ids=list(fasteners),
            datum='A/B/C',tolerance_m=a['dimensional_tolerance_m'],load_case_ids=['vertical','longitudinal','lateral/uplift'],
            inspection=['identity and fit','positive retention','independent inspection'],capacity_evidence=None,qualified=False))
    def bolts(positions,z_bottom,z_top,upper,lower):
        ids=[]
        for i,(x,y) in enumerate(positions):
            stem='mount-'+str(i);washer=.003;head=.6*d;nut=.8*d
            add(stem+'-bolt',[cylinder('shank',d/2,z_top-z_bottom+2*washer,[x,y,(z_top+washer+z_bottom-washer)/2]),
                cylinder('head',.9*d,head,[x,y,z_top+washer+head/2])],route='purchase class 8.8 reference; actual threads/head/grade/origin to confirm')
            add(stem+'-upper-washer',[cylinder('washer',d,washer,[x,y,z_top+washer/2],inner=d*.53)],route='purchase; washer class/dimensions to confirm')
            add(stem+'-lower-washer',[cylinder('washer',d,washer,[x,y,z_bottom-washer/2],inner=d*.53)],route='purchase; washer class/dimensions to confirm')
            add(stem+'-nut',[cylinder('nut-envelope',d,nut,[x,y,z_bottom-washer-nut/2],inner=d*.53)],route='purchase; thread engagement/locking and nut profile unresolved',role='hardware-envelope')
            ids.append(stem+'-bolt')
            ends=['tray-floor','vehicle-interface-'+str(i),'rail-'+str(-1 if y<0 else 1)+'-top','rail-'+str(-1 if y<0 else 1)+'-bottom'] if kind=='service-cassette' else upper+lower
            joint(stem,ends,'proposed through-bolt; preload/prying/threads unresolved',[stem+'-bolt',stem+'-upper-washer',stem+'-lower-washer',stem+'-nut'])
        return ids
    d=variables['bolt_diameter_m']
    if kind=='service-cassette':
        t=variables['rail_wall_m'];L=a['length_m'];W=a['width_m'];mounts=[(x,y) for x in (-a['mount_span_m']/2,a['mount_span_m']/2) for y in (-.12,.12)]
        plate('tray-floor',L,W,.003,[0,0,.0015],mounts)
        for side in (-1,1):
            y=side*.12
            plate('rail-'+str(side)+'-top',L,.04,t,[0,y,-t/2],[(-.5,0),(.5,0)])
            plate('rail-'+str(side)+'-bottom',L,.04,t,[0,y,-.06+t/2],[(-.5,0),(.5,0)])
            for face in (-1,1):
                name='rail-'+str(side)+'-web-'+str(face)
                block(name,L,t,.06-2*t,[0,y+face*(.04-t)/2,-.03])
                joint(name+'-weld',['rail-'+str(side)+'-top',name,'rail-'+str(side)+'-bottom'],'continuous seam weld; throat, fatigue and procedure open')
            block('tray-side-'+str(side),L,.003,.147,[0,side*(W-.003)/2,.0765])
            joint('tray-side-'+str(side)+'-seam',['tray-floor','tray-side-'+str(side)],'continuous folded/sealed seam reference')
        for i,(x,y) in enumerate(mounts):plate('vehicle-interface-'+str(i),.07,.07,.006,[x,y,.006],[(0,0)])
        bolts(mounts,-.06,.009,['tray-floor']+['vehicle-interface-'+str(i) for i in range(4)],['rail--1-top','rail--1-bottom','rail-1-top','rail-1-bottom'])
        area=variables['duct_area_m2'];dw=.2;dh=area/dw;z=.04;wall=.001
        plate('duct-bottom',.9,dw+2*wall,wall,[0,0,z+wall/2])
        plate('duct-top',.9,dw+2*wall,wall,[0,0,z+wall+dh+wall/2])
        for side in (-1,1):
            block('duct-side-'+str(side),.9,wall,dh,[0,side*(dw+wall)/2,z+wall+dh/2])
            joint('duct-seam-'+str(side),['duct-bottom','duct-side-'+str(side),'duct-top'],'sealed sheet seams; leak and fire tests required')
        for i,(x,y) in enumerate(itertools.product((-.35,.35),(-.105,.105))):
            block('duct-foot-'+str(i),.02,.015,z-.003,[x,y,(z+.003)/2])
            joint('duct-foot-'+str(i),['tray-floor','duct-foot-'+str(i),'duct-bottom'],'spot/fillet weld; detailed fatigue and sealing open')
        radius=math.sqrt(2.5e-6/math.pi)
        for i,y in enumerate(.124+.004*j for j in range(8)):
            primitive=dict(id='conductor',kind='cylinder',centre_m=[0,y,.07],radius_m=radius,length_m=.8,axis='x')
            add('wire-'+str(i)+'-conductor',[primitive],material='copper',route='cut/strip/terminate from selected 2.5mm2 cable; cable type open')
            shell=dict(primitive,id='insulation',kind='tube',radius_m=.0018,inner_radius_m=radius)
            add('wire-'+str(i)+'-jacket',[shell],material='insulation',route='purchase rail cable; bend/termination details open')
        # Two feed-through strain-relief bars, with eight actual drilled
        # passages and four floor standoffs. Cable grip/lining qualification
        # remains separate from geometric routing and nominal clearance.
        for end,x in enumerate((-.3,.3)):
            holes=[[0.,.124+.004*j-.138] for j in range(8)]
            primitive=contracts.box('clamp-bar',.012,.044,.008,[0,0,0])
            primitive.update(kind='perforated-plate',holes_xy_m=holes,hole_radius_m=.0019)
            clamp=add('cable-clamp-'+str(end),[primitive],route='machine/drill passage bar; feed unterminated cables; qualify compliant grip')
            # Rebuild with the same primitive definition and an explicit local
            # transformation so native geometry and mass/inertia use one datum.
            placement=dict(translation_m=[x,.138,.07],rotation=[[0,0,1],[0,1,0],[-1,0,0]])
            physical=contracts.part(clamp['id'],'steel',clamp['manufacturing'],materials,placement=placement,
                limits=clamp['manufacturing_limits'],inspections=clamp['inspection_characteristics']+['cable passage','pull retention after selected compliant lining'])
            physical.update({k:clamp[k] for k in ('manufacturing_unit_id','geometric_role','procurement','process_route','datum_scheme')})
            parts[-1]=physical
            for side,y in enumerate((.118,.158)):
                name='clamp-standoff-'+str(end)+'-'+str(side)
                block(name,.006,.004,.061,[x,y,.0335])
                joint(name,['tray-floor',name,clamp['id']],'welded standoff and retained clamp; local fatigue and fastening details open')
        add('earth-stud',[cylinder('stud',.004,.02,[-.52,0,.013])],route='welded earth stud; thread/coating and fault-current qualification open')
        add('earth-lug-envelope',[cylinder('lug',.01,.002,[-.52,0,.004],inner=.0045)],material='copper',route='select qualified crimp lug and bond conductor',role='hardware-envelope')
        add('earth-washer',[cylinder('washer',.008,.001,[-.52,0,.0055],inner=.0045)],route='purchase confirmed earth bond hardware')
        add('earth-locknut-envelope',[cylinder('nut',.007,.006,[-.52,0,.009],inner=.0045)],route='select locking nut; thread engagement and torque open',role='hardware-envelope')
        joint('earth-bond',['tray-floor','earth-stud','earth-lug-envelope','earth-washer','earth-locknut-envelope'],'dedicated bare-metal earth bond; conductor route, locking and measured resistance open')
        dimensions=f['connector.dimensions'];materials['connector-envelope']=dict(density_kg_m3=f['connector.mass']/math.prod(dimensions),basis='Published mass divided by coordination envelope; not actual material or supplier internal geometry')
        block('power-connector',*dimensions,[.52,.14,.07],material='connector-envelope',route='purchase exact reference part',role='supplier-coordination-envelope',
            supplier=dict(part=f['connector.part'],source='harwin-power',origin=f['connector.origin'],internal_geometry_defined=False))
        netlist=dict(voltage_v=a['lv_voltage_v'],current_a=a['branch_current_a'],connector=f['connector.part'],
            pins={'1':'24V-fused','2':'LV-return','3':'lock-sense','4':'lock-return','5':'data-A','6':'data-B','7':'temperature','8':'temperature-return','9':'spare','10':'spare'},
            protective_earth='Separate chassis earth stud and tested bond required; not inferred from signal return',
            termination_geometry_complete=False,wire_gauge_qualified=False,derating_qualified=False)
        metadata=dict(mount_positions_m=[[x,y,0] for x,y in mounts],duct_clear_area_m2=area,rail_section_m=[.04,.06,t],netlist=netlist)
    else:
        t=variables['plate_thickness_m'];L,W=a['plate_plan_m'];mounts=[(x,y) for x in (-.27,.27) for y in (-.22,.22)]
        plate('seat-base',L,W,t,[0,0,t/2],mounts)
        primitive=contracts.box('grout',L,W,a['grout_depth_m'],[0,0,-a['grout_depth_m']/2]);primitive.update(kind='perforated-plate',holes_xy_m=[list(v) for v in mounts],hole_radius_m=d*.55)
        add('grout-bed',[primitive],material='grout',route='qualified site grout and strength hold required')
        for side in (-1,1):
            block('guide-'+str(side),.48,.02,.08,[0,side*.163,t+.04])
            joint('guide-weld-'+str(side),['seat-base','guide-'+str(side)],'welded guide; weld throat/resistance and replacement scheme open')
        volume=.4*.3*.08;materials['bearing-envelope']=dict(density_kg_m3=80./volume,basis='80kg unqualified purchased-bearing mass allowance; geometry is a coordination envelope only')
        block('bearing-procurement-envelope',.4,.3,.08,[0,0,t+.04],material='bearing-envelope',route='request exact offered bearing configuration',role='supplier-coordination-envelope',
            supplier=dict(family=variables['bearing_family'],source='freyssinet' if variables['bearing_family']=='elastomeric-reference' else 'ekspan',exact_part=None,offered_rating=None))
        bolts(mounts,-.2,t,['seat-base'],['external-pier-cap-interface'])
        joint('bearing-seat-contact',['seat-base','bearing-procurement-envelope'],'compression seating and guided longitudinal travel; concrete, slip and uplift qualification open')
        metadata=dict(mount_positions_m=[[x,y,0] for x,y in mounts],bearing_family=variables['bearing_family'],
            procurement_envelope_m=[.4,.3,.08],bearing_mass_allowance_kg=80.)
    revision=core.digest(dict(kind=kind,variables=variables,baseline=policy,parts=parts,joints=joints,materials=materials,metadata=metadata))
    for value in parts:value['revision']=revision;value['joints']=[j['id'] for j in joints if value['id'] in j['endpoints']]
    contract=dict(schema='osr-engineering-representations/1',name=kind,revision=revision,parts=parts,materials=materials,
        assembly_joints=joints,construction_stages=[],mandatory_evidence=p['holds'],physical_validation=False,production_released=False)
    contracts.validate(contract)
    return dict(schema='osr-assembly-design-candidate/1',kind=kind,variables=deepcopy(variables),revision=revision,
        requirement_ids=p['requirement_ids'],contract=contract,metadata=metadata,
        assembly_steps=['verify identities/materials and fixture datums','fabricate and inspect owned parts','join frame/seat and inspect connections','fit purchased units and record serials','fit and retain services/fasteners','bench test','install and repeat interface tests'],
        qa_plan=[dict(unit_id=v['id'],unit_revision=revision,serial=None,required=v['inspection_characteristics'],records=[],accepted=False) for v in parts],
        source_scope=p['scope'],open_requirements=p['holds'],**core.FLAGS)
