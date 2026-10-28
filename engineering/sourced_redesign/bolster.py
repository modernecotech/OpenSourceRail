"""Counted full-depth bogie load-introduction revision of the exact V4 body.

Net primitive plates are coped around the retained rail flanges and central
floor-member/cap corridor. Bolt bore cuts and joint strength remain pending;
counted stock and finite contacts never establish installed acceptance.
"""
from copy import deepcopy
from pathlib import Path
from math import pi
import numpy as np
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from engineering.component_registry import make_part,make_occurrence,make_registry,summary
from engineering.component_registry.materials import catalogue
from engineering.reference_cell.vehicles import _mass_properties
from engineering.sourced_case import layered_structure as layer

PRODUCER='engineering/sourced_redesign/bolster.py'
EXPECTED_PARENT='d1b97ba718ff687336a4cdfa828cd3e39cb689544fd37f524eca05491165e710'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)


def sources(vehicle,root=ROOT):
    result=dict(vehicle['source_sha256'])
    for name,expected in result.items():
        if digest(Path(root)/name)!=expected:raise ValueError('Stale parent source '+name)
    for name in (PRODUCER,'engineering/sourced_redesign/__init__.py'):
        result[name]=digest(Path(root)/name)
    if result[PRODUCER]!=digest(__file__):raise ValueError('Executing bolster source differs')
    return dict(sorted(result.items()))


def revision(vehicle,*,root=ROOT):
    layer._vehicle(vehicle)
    if vehicle['candidate_id']!=EXPECTED_PARENT or vehicle['vehicle_id']!='V4':raise ValueError('Exact recorded V4 distributed-contact parent required')
    rows=layer._rows(vehicle);byname={r['occurrence']['occurrence_id']:r for r in rows};materials={m['grade_id']:m for m in catalogue()['materials']}
    definitions={p['physical_definition_id']:deepcopy(p) for p in vehicle['registry']['parts']};new=[];interfaces=[];clearance=[];remove=set()
    plans=vehicle['whole_body_revision_ancestry']['counted_splice_plans']
    obsolete=[]
    for i,plan in enumerate(plans):
        if any('/hardpoint-local-doubler/' in name or '/body-bogie-hardpoint/' in name for name in plan['source_pair']):obsolete.append('body-splice-'+str(i)+'-')
    for row in rows:
        name=row['occurrence']['occurrence_id'].split('/',1)[1]
        if layer._is(row,'hardpoint-local-doubler') or any(name.startswith(prefix) for prefix in obsolete):remove.add(name)

    def add(name,dims,xyz,grade='AL-6082-T651-SHEET',kind='box',axis=2,function='bogie-interfaces',method='plate-cut-cope-drill-fit-and-retain',bounds=None):
        mat=materials[grade];rho=mat['density_kg_m3']
        if kind=='box':volume=float(np.prod(dims))
        elif kind=='cylinder':volume=pi*dims['radius']**2*dims['length']
        else:volume=pi*(dims['outer_radius']**2-dims['inner_radius']**2)*dims['length']
        p=make_part('OSR-V4-BOLSTER-'+name.upper(),'A',[function],dict(kind='envelope' if bounds else kind,dimensions_m=dims,net_volume_m3=None if bounds else volume),None if bounds else mat['material_id'],
            dict(calculated_kg=None if bounds else volume*rho['nominal'],lower_bound_kg=bounds[0] if bounds else volume*rho['lower'],upper_bound_kg=bounds[1] if bounds else volume*rho['upper'],evidence_state='bounded-estimate' if bounds else 'calculated'),
            dict(method=method,process=method,cycle_hours=None,tooling_id='prototype-bolster-jig-A',gross_to_net_yield_hypothesis=None,
                bore_cut_mass_kg=None,manufacturing_release=False),
            assembly=dict(attachment='finite coped plate interfaces and separately counted M8 retention',approved_strength_margin=None,
                net_bores_and_counterbores_defined=False,fitup_tolerance_m=None,qualified_joint=False,
                joining_process='prototype welded plate seams plus counted pad/web mechanical retention; filler alloy, weld procedure, HAZ and damage-tolerant transfer remain unqualified'),
            evidence=dict(state='physical-prototype-hypothesis',source=PRODUCER,physical_test_ids=[],supplier_configuration_id=None),
            lifecycle=dict(inspection_interval=None,repair_method='Support body, remove retained connections and replace individual plate; inspect bores and mating stock',qualified=False))
        definitions[p['physical_definition_id']]=p;T=np.eye(4);T[:3,3]=xyz
        if kind!='box' and axis!=2:T[:3,:3]=np.array([[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]]) if axis==0 else np.array([[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]])
        new.append(dict(name=name,part=p,transform=T.tolist()))
        return name

    def bolt(prefix,centre,axis,length=.06):
        add(prefix+'-shaft',dict(length=length,radius=.004),centre,'STEEL-FASTENER-HYPOTHESIS','cylinder',axis,method='purchased-M8-shaft-hypothesis')
        for name,offset,thick,outer,inner in (('head',length/2+.003,.006,.007,0.),('nut',-length/2-.0035,.007,.007,.004),('washer-a',length/2-.001,.0015,.009,.0045),('washer-b',-length/2+.001,.0015,.009,.0045)):
            xyz=list(centre);xyz[axis]+=offset
            dimensions=dict(length=thick,radius=outer) if not inner else dict(length=thick,outer_radius=outer,inner_radius=inner)
            add(prefix+'-'+name,dimensions,xyz,'STEEL-FASTENER-HYPOTHESIS','cylinder' if not inner else 'tube',axis,method='purchased-counted-M8-retention-hypothesis')

    for index,x in enumerate(vehicle['interfaces']['bogie_centres_per_car_m']):
        pads=[r for r in rows if layer._is(r,'body-bogie-hardpoint') and abs(r['position'][0]-x)<1e-8]
        if len(pads)!=2:raise ValueError('Two actual secondary pads per bogie required')
        oldrib=[r for r in rows if layer._is(r,'transverse-floor-member') and abs(r['position'][0]-x)<1e-8]
        if len(oldrib)!=1:raise ValueError('Actual coincident floor member required for exact cope')
        rib=oldrib[0];padtop=max(float(p['upper'][2]) for p in pads);base_top=padtop+.006;riblo=float(rib['lower'][2]);ribhi=float(rib['upper'][2]);top_lower=.957;top_upper=.965
        if not np.isclose(padtop,.795) or not np.isclose(ribhi,.9475):raise ValueError('Parent support geometry changed')
        prefix='bogie-'+str(index+1)
        add(prefix+'-bottom-plate',[.24,2.65,.006],[x,0.,padtop+.003])
        # Two lipped channels leave the actual60mm central rib/cap corridor open.
        for sign in (-1,1):add(prefix+'-top-lip-'+str(sign),[.09,2.65,.008],[x+sign*.075,0.,top_lower+.004])
        for side in (-1,1):
            xx=x+side*.116
            for segment,(a,b) in enumerate(((-1.10,1.10),(-1.325,-1.20),(1.20,1.325))):add(prefix+'-side-web-'+str(side)+'-'+str(segment),[.008,b-a,top_lower-base_top],[xx,(a+b)/2,(base_top+top_lower)/2])
            # At rail crossings the flanges and added web spreaders occupy their real space.
            for ysign in (-1,1):
                for segment,(a,b) in enumerate(((1.10,1.138),(1.162,1.20))):add(prefix+'-rail-cope-'+str(side)+'-'+str(ysign)+'-'+str(segment),[.008,b-a,.12],[xx,ysign*(a+b)/2,.87])
        weld_length_hypothesis=4*2.65+2*(2*.224+2*.156)+8*(.30+.12)
        weld_bounds=(weld_length_hypothesis*.5*.005**2*2680,weld_length_hypothesis*.5*.008**2*2720)
        add(prefix+'-bounded-weld-deposition',[.24,2.65,top_upper-padtop],[x,0.,(top_upper+padtop)/2],bounds=weld_bounds,
            method='bounded5-to8mm-fillet-profile-deposition-hypothesis; actual-filler-alloy-procedure-and-net-bead-geometry-unresolved')
        for ysign in (-1,1):
            web=[r for r in rows if layer._is(r,'underframe-web') and abs(r['position'][1]-ysign*1.15)<1e-8]
            if len(web)!=1:raise ValueError('Both actual longitudinal webs required')
            web=web[0]
            for face in (-1,1):
                yy=ysign*1.15+face*.008
                add(prefix+'-web-spreader-low-'+str(ysign)+'-'+str(face),[.30,.008,riblo-.81],[x,yy,(riblo+.81)/2])
                for sign in (-1,1):add(prefix+'-web-spreader-side-'+str(ysign)+'-'+str(face)+'-'+str(sign),[.12,.008,.93-riblo],[x+sign*.09,yy,(riblo+.93)/2])
            # Saddles reach the actual top flange; their central slot avoids the retained rib and cap.
            for sign in (-1,1):add(prefix+'-upper-saddle-'+str(ysign)+'-'+str(sign),[.12,.10,top_lower-.938],[x+sign*.09,ysign*1.15,(top_lower+.938)/2])
            for dx in (-.10,.10):
                for z in (.835,.905):bolt(prefix+'-web-bolt-'+str(ysign)+'-'+str(dx)+'-'+str(z),[x+dx,ysign*1.15,z],1)
            for pad in pads:
                if np.sign(pad['position'][1])!=ysign:continue
                py=float(pad['position'][1])
                # Five net diaphragm regions avoid the retained longitudinal60mm rib/cap corridor.
                add(prefix+'-pad-diaphragm-low-'+str(ysign),[.224,.008,riblo-base_top],[x,py,(riblo+base_top)/2])
                for sign in (-1,1):
                    add(prefix+'-pad-diaphragm-side-'+str(ysign)+'-'+str(sign),[.082,.008,ribhi-riblo],[x+sign*.071,py,(ribhi+riblo)/2])
                    add(prefix+'-pad-diaphragm-upper-'+str(ysign)+'-'+str(sign),[.082,.008,top_lower-ribhi],[x+sign*.071,py,(top_lower+ribhi)/2])
                for dx in (-.08,.08):
                    for dy in (-.06,.06):bolt(prefix+'-pad-bolt-'+str(ysign)+'-'+str(dx)+'-'+str(dy),[x+dx,py+dy,.790],2)
                springs=[r for r in rows if layer._is(r,'secondary-air-spring') and abs(r['position'][0]-x)<1e-8 and abs(r['position'][1]-py)<1e-8]
                spring_top=max((float(r['upper'][2]) for r in springs),default=None)
                interfaces.append(dict(pad_occurrence_id=pad['occurrence']['occurrence_id'],pad_top_z_m=padtop,bolster_bottom_z_m=padtop,
                    pad_center_m=pad['position'].tolist(),pad_bearing_footprint_m=[.24,.24],bolts=4,
                    static_secondary_spring_top_z_m=spring_top,new_pad_nut_lowest_z_m=.753,static_nut_to_spring_envelope_clearance_m=None if spring_top is None else .753-spring_top,
                    dynamic_suspension_stroke_clearance_verified=False,load_path=['pad','bottom-plate','pad-diaphragm','coped-bolster-webs-and-top-lips','web-spreaders-and-flange-saddles','both-longitudinal-rails'],qualified=False))
            clearance.append(dict(bogie_x_m=x,rail_web_occurrence_id=web['occurrence']['occurrence_id'],web_y_m=float(web['position'][1]),
                existing_web_region_m=[float(web['lower'][1]),float(web['upper'][1])],spreader_outer_region_m=[ysign*1.15-.012,ysign*1.15+.012],
                flange_copes_y_m=[1.10,1.20],mid_web_copes_y_m=[1.138,1.162],central_rib_cap_corridor_x_m=[x-.03,x+.03],
                end_to_end_fitup_qualified=False))
    occ=[]
    for o in vehicle['registry']['occurrences']:
        if o['occurrence_id'].split('/',1)[1] not in remove:occ.append(deepcopy(o))
    for car in range(1,7):
        for row in new:
            T=deepcopy(row['transform']);T[0][3]+=17.5*(car-1)
            occ.append(make_occurrence('car-'+str(car)+'/bolster-'+row['name'],row['part'],parent_id='car-'+str(car)+'/bogie-interfaces',transform=T,scope='vehicle/bogie-interfaces'))
    used={o['part_definition_id'] for o in occ};partlist=[p for key,p in definitions.items() if key in used]
    registry=make_registry(vehicle['label']+'; full-depth load-introduction bolsters',partlist,occ,vehicle['functional_requirements'],parent_candidate_id=vehicle['candidate_id'],assemblies=vehicle['registry']['assemblies'])
    result=deepcopy(vehicle);result.pop('evaluation_id');result.update(candidate_id=registry['candidate_id'],registry=registry,summary=summary(registry),label=vehicle['label']+'; full-depth load-introduction bolsters')
    pmap={p['physical_definition_id']:p for p in partlist};allmass=[]
    for o in registry['occurrences']:
        T=np.asarray(o['transform']);axis='x' if abs(T[0,2])>.9 else 'y' if abs(T[1,2])>.9 else 'z';allmass.append(dict(part=pmap[o['part_definition_id']],xyz=T[:3,3].tolist(),axis=axis,car=o['occurrence_id'].split('/')[0]))
    local=[r for r in allmass if r['car']=='car-1'];result['per_car_mass_properties']=_mass_properties(local);result['train_mass_properties']=_mass_properties(allmass)
    result['per_car_occurrences']=len(local);result['per_car_part_definitions']=len(partlist);result['per_car_functional_occurrences']={f:sum(f in r['part']['functions'] for r in local) for f in result['functional_requirements']}
    result['manufacturing_plan']=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],part_id=p['part_id'],process=p['manufacturing'],approved_work_instruction=None,qualified_tooling=None,required_inspections=['net-cope','material-lot','joint-fitup','bore-and-retention','load-test']) for p in partlist]
    result['bolster_revision']=dict(parent_candidate_id=vehicle['candidate_id'],parent_vehicle_evaluation_id=vehicle['evaluation_id'],purpose='next-experiment; remove eccentric thin-flange load introduction',
        interfaces=interfaces,rail_clearance_definitions=clearance,removed_occurrences_per_car=len(remove),removed_local_names=sorted(remove),added_occurrences_per_car=len(new),
        before_mass_upper_per_car_kg=vehicle['per_car_mass_properties']['mass_upper_bound_kg'],after_mass_upper_per_car_kg=result['per_car_mass_properties']['mass_upper_bound_kg'],
        upper_mass_delta_per_car_kg=result['per_car_mass_properties']['mass_upper_bound_kg']-vehicle['per_car_mass_properties']['mass_upper_bound_kg'],
        rigid_connection_assumed=False,physical_joint_allowables=None,closed_torsion_box=False,
        unresolved=['Net bolt bore/counterbore cuts and fastening preloads','Plate-joint retention, fatigue, local bearing and damage tolerance','Actual support/secondary-suspension envelope sweeps and service access','Same-candidate3D/contact numerical response and coupled service effects','Supplier prices, tooling labour and full-life cost'])
    for x in vehicle['interfaces']['bogie_centres_per_car_m']:
        T=np.eye(4);T[:3,3]=[x,0.,.88];end=T.copy();end[1,3]=3.4
        result['assembly_access'].append(dict(id='bolster-service-'+str(x),function='bogie-interfaces',envelope_dimensions_m=[.50,2.85,.35],start_transform=T.tolist(),end_transform=end.tolist(),
            motion=dict(kind='linear-translation',sample_count=17,translation_m=[0.,3.4,0.]),swept_AABB_m=dict(min=[x-.25,-1.425,.705],max=[x+.25,4.825,1.055]),
            tool_access_radius_m=.12,required_tools=['rated-body-trestles','secondary-suspension-isolation','torque-tool','bolster-lifting-cradle'],lifting_device='rated-bolster-cradle',
            sequence=['isolate-services-and-suspension','lift-and-support-body','remove-bogie','support-bolster','remove-counted-retention','remove-modular-plates-through-reviewed-path','inspect-and-replace'],
            flexible_service_reserve_m=None,clearance_and_lifting_verified=False,interference_resolution='Bogie removal and full installed swept-envelope/tool access review required'))
    result['source_sha256']=sources(vehicle,root);result['evaluation_id']=identity(result);layer._vehicle(result);return result
