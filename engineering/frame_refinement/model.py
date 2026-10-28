"""Two fabricated closed side-sills with actual copes and bounded joining stock.

This is a next-experiment physical revision, not a spring multiplier or a body
release. Material stiffness is room-temperature typical; HAZ/strength/fatigue,
actual weld procedures, dynamic clearances and installed bores remain open.
"""
from copy import deepcopy
from pathlib import Path
from math import pi,ceil
import numpy as np
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from engineering.component_registry import make_part,make_occurrence,make_registry,summary
from engineering.component_registry.materials import catalogue
from engineering.reference_cell.vehicles import _mass_properties
from engineering.sourced_case import layered_structure as layer

PRODUCER='engineering/frame_refinement/model.py'
EXPECTED_PARENT='4fd7a56ff432b4a6e86c9722b5677a6b34893e9ac840b7e1dff5148ba09aad8b'
FLAGS=layer.FLAGS
PARAMETERS=dict(length_start_m=.11,length_end_m=16.89,side_centres_y_m=[-1.32,1.32],width_m=.12,depth_m=.45,wall_m=.005,top_z_m=.94,
    room_temperature_E_Pa=70e9,room_temperature_G_Pa=26e9,advisory_added_mass_budget_kg_per_car=800.)


def section(width=.12,depth=.45,wall=.005,E=70e9):
    if min(width,depth,wall,E)<=0 or 2*wall>=min(width,depth):raise ValueError('Positive closed rectangular section required')
    A=width*depth-(width-2*wall)*(depth-2*wall);I=(width*depth**3-(width-2*wall)*(depth-2*wall)**3)/12
    return dict(area_m2=A,I_vertical_m4=I,EI_vertical_Nm2=E*I,shear_web_area_m2=2*wall*(depth-2*wall),
        stiffness_source='Hulamin6082 typical70GPa; not a weld/HAZ/fatigue allowable',strength_allowable_Pa=None)


def necessary_bound(body_upper_mass_kg,added_upper_mass_kg):
    s=section();L=11.2;length=PARAMETERS['length_end_m']-PARAMETERS['length_start_m'];a=(length-L)/2
    q=(body_upper_mass_kg+added_upper_mass_kg+160*75)*9.80665/length;EI=2*s['EI_vertical_Nm2']
    d=q/EI*(5*L**4/384-a*a*L*L/16);slope=q/EI*(L**3/24-a*a*L/4)
    return dict(scope='Uniform vertical crowd load on two perfectly joined side-sills with actual symmetric overhang/support spacing; necessary sizing control, not full-body prediction',
        crowd_people=160,passenger_mass_kg=75.,distributed_load_N_m=q,support_span_m=L,overhang_each_m=a,
        two_sill_EI_Nm2=EI,conditional_midspan_deflection_m=d,conditional_support_slope_rad=slope,
        model_domain_translation_reference_m=.17,model_domain_rotation_reference_rad=.1,
        domain_budget_from_this_bound=bool(d<.17 and abs(slope)<.1),approved_functional_deflection_limit_m=None,physical_qualified=False)


def sources(vehicle,root):
    out=dict(vehicle['source_sha256'])
    for name,sha in out.items():
        if digest(Path(root)/name)!=sha:raise ValueError('Stale parent source '+name)
    for name in (PRODUCER,'engineering/frame_refinement/__init__.py'):out[name]=digest(Path(root)/name)
    if out[PRODUCER]!=digest(__file__):raise ValueError('Executing frame producer differs')
    return dict(sorted(out.items()))


def preflight(vehicle):
    layer._vehicle(vehicle);rows=layer._rows(vehicle);half=vehicle['requirements']['car_width_m']/2
    if 1.38+.006>half:raise ValueError('Side-sill plus declared joining envelope exceeds fixed vehicle width; explicit gauge revision required')
    protected={'running-gear','doors','auxiliary-power','control-safety','HVAC','LIM-interface','glazing','seating','solar-roof','coupling-articulation'};checks=[]
    for side in (-1,1):
        lo=np.array([.11,side*1.32-.06,.49]);hi=np.array([16.89,side*1.32+.06,.94])
        for r in rows:
            if not set(r['part']['functions'])&protected:continue
            if 'lower' not in r:
                g=r['part']['geometry'];d=g['dimensions_m'];radius=d.get('outer_radius',d.get('radius'));extent=np.abs(r['rotation'])@np.array([2*radius,2*radius,d['length']]);a=r['position']-extent/2;b=r['position']+extent/2
            else:a,b=r['lower'],r['upper']
            gap=np.maximum(np.maximum(lo-b,a-hi),0.);distance=float(np.linalg.norm(gap));overlap=np.minimum(hi,b)-np.maximum(lo,a)
            if np.all(overlap>1e-9):raise ValueError('Actual service/bogie/door envelope intersects proposed sill: '+r['occurrence']['occurrence_id'])
            if distance<.10:checks.append(dict(side=side,occurrence_id=r['occurrence']['occurrence_id'],static_AABB_separation_m=distance,kind=r['part']['geometry']['kind'],dynamic_or_maintenance_clearance_accepted=False))
    return dict(declared_vehicle_half_width_m=half,proposed_stock_outer_y_m=1.38,joining_envelope_outer_y_m=1.386,static_to_declared_width_margin_m=half-1.386,
        fixed_interfaces_changed=False,close_static_envelopes=checks,dynamic_gauge_proved=False,door_bogie_suspension_sweeps_proved=False,maintenance_access_proved=False)


def revision(vehicle,*,root=ROOT):
    layer._vehicle(vehicle)
    if vehicle['candidate_id']!=EXPECTED_PARENT:raise ValueError('Exact recorded bolstered V4 parent required')
    fit=preflight(vehicle);rows=layer._rows(vehicle);materials={m['grade_id']:m for m in catalogue()['materials']};parts={p['physical_definition_id']:deepcopy(p) for p in vehicle['registry']['parts']};replace={};added=[];changes=[]
    def newpart(name,dims,material_id,grade_mass,*,kind='box',bounds=None,assembly=None,manufacturing=None):
        if kind=='box':volume=float(np.prod(dims))
        elif kind=='cylinder':volume=pi*dims['radius']**2*dims['length']
        else:volume=pi*(dims['outer_radius']**2-dims['inner_radius']**2)*dims['length']
        m=grade_mass;mass=dict(calculated_kg=volume*m['nominal'],lower_bound_kg=volume*m['lower'],upper_bound_kg=volume*m['upper'],evidence_state='calculated') if bounds is None else dict(calculated_kg=None,lower_bound_kg=bounds[0],upper_bound_kg=bounds[1],evidence_state='bounded-estimate')
        p=make_part('OSR-V4-FRAME-'+name.upper(),'A',['primary-body'],dict(kind='envelope' if bounds else kind,dimensions_m=dims,net_volume_m3=None if bounds else volume),None if bounds else material_id,mass,
            manufacturing or dict(method='local-cut-cope-fit-weld-and-inspect',cycle_hours=None,tooling_id='side-sill-jig-A',net_bore_cuts_qualified=False),
            assembly=assembly or dict(attachment='counted finite plate contacts and retention; no infinite joint',net_bores_defined=False,qualified_joint=False),
            evidence=dict(source=PRODUCER,state='prototype-geometry-and-typical-stiffness-hypothesis',physical_test_ids=[],HAZ_allowable=None),
            lifecycle=dict(inspection_interval=None,repair_method='Unload and support body; inspect weld/bolted interfaces; replace approved segment under a reviewed procedure',qualified=False))
        parts[p['physical_definition_id']]=p;return p
    al=materials['AL-6082-T651-SHEET'];fast=materials['STEEL-FASTENER-HYPOTHESIS']
    def add(name,dims,position,*,kind='box',axis=2,bounds=None,manufacturing=None):
        material=fast if kind!='box' else al;p=newpart(name,dims,material['material_id'],material['density_kg_m3'],kind=kind,bounds=bounds,manufacturing=manufacturing);T=np.eye(4);T[:3,3]=position
        if kind!='box' and axis!=2:T[:3,:3]=np.array([[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]]) if axis==0 else np.array([[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]])
        added.append(dict(name=name,part=p,transform=T.tolist()));return p
    # Existing members end at the new inner sill faces; exact parent stock is
    # trimmed and resealed rather than hidden inside new solids.
    for r in rows:
        oid=r['occurrence']['occurrence_id'];name=oid.split('/',1)[1];p=r['part'];d=r.get('dimensions');pos=r['position'].copy();newdims=None
        if layer._is(r,'transverse-floor-member'):newdims=d.copy();newdims[1]=2.52
        elif '/bolster-' in oid and p['geometry']['kind']=='box':
            if name.endswith('-bottom-plate') or '-top-lip-' in name:
                newdims=d.copy();newdims[1]=2.52
            elif '-side-web-' in name and min(abs(r['lower'][1]),abs(r['upper'][1]))>=1.20-1e-8:
                newdims=d.copy();newdims[1]=.06;pos[1]=np.sign(pos[1])*1.23
        if '/bolster-' in oid and p['geometry']['kind']=='envelope' and '-bounded-weld-deposition' in name:
            newdims=d.copy();newdims[1]=2.52
            replacement=make_part('OSR-V4-FRAME-RETAINED-'+name.upper(),'A',p['functions'],dict(kind='envelope',dimensions_m=newdims.tolist(),net_volume_m3=None),None,p['mass'],p['manufacturing'],assembly=dict(parent_part_definition_id=p['physical_definition_id'],actual_filler_and_profile_unresolved=True,qualified_joint=False),evidence=dict(source=PRODUCER,state='conservative-retained-weld-mass-bounds'))
            parts[replacement['physical_definition_id']]=replacement;replace[name]=(replacement,deepcopy(r['occurrence']['transform']))
            changes.append(dict(occurrence_local_name=name,parent_part_definition_id=p['physical_definition_id'],new_part_definition_id=replacement['physical_definition_id'],before_dimensions_m=d.tolist(),after_dimensions_m=newdims.tolist(),new_position_m=pos.tolist()));continue
        if newdims is None:continue
        if np.any(newdims<=0):raise ValueError('Invalid actual cope')
        m=next(m for m in vehicle['registry']['materials'] if m['material_id']==p['material_id'])
        replacement=newpart('retained-'+name.replace('/','-'),newdims.tolist(),p['material_id'],m['density_kg_m3'],assembly=dict(attachment='Original route with exact outer end cope to side-sill face',parent_part_definition_id=p['physical_definition_id'],qualified_joint=False,net_bores_defined=False))
        T=deepcopy(r['occurrence']['transform']);T[1][3]=float(pos[1]);replace[name]=(replacement,T)
        changes.append(dict(occurrence_local_name=name,parent_part_definition_id=p['physical_definition_id'],new_part_definition_id=replacement['physical_definition_id'],before_dimensions_m=d.tolist(),after_dimensions_m=newdims.tolist(),new_position_m=pos.tolist()))
    def coped_bearing(name,dimensions,position):
        lo=np.asarray(position)-np.asarray(dimensions)/2;hi=np.asarray(position)+np.asarray(dimensions)/2;pieces=[(lo,hi)];witness=[]
        for row in rows:
            if row['part']['geometry']['kind']!='box' or not set(row['part']['functions'])&{'primary-body','bogie-interfaces'}:continue
            localname=row['occurrence']['occurrence_id'].split('/',1)[1]
            if localname in replace:
                part,T=replace[localname];d=np.array(part['geometry']['dimensions_m']);R=np.array(T)[:3,:3];extent=np.abs(R)@d;centre=np.array(T)[:3,3];a,b=centre-extent/2,centre+extent/2
            else:a,b=row['lower'],row['upper']
            remaining=[]
            for low,high in pieces:
                ia=np.maximum(low,a);ib=np.minimum(high,b)
                if not np.all(ib-ia>1e-10):remaining.append((low,high));continue
                witness.append(row['occurrence']['occurrence_id'])
                # Six disjoint slabs exactly partition the box difference.
                for axis in range(3):
                    for side in (-1,1):
                        ll=low.copy();hh=high.copy()
                        for previous in range(axis):ll[previous]=ia[previous];hh[previous]=ib[previous]
                        if side<0:hh[axis]=ia[axis]
                        else:ll[axis]=ib[axis]
                        if np.all(hh-ll>1e-10):remaining.append((ll,hh))
            pieces=remaining
        if not pieces:raise ValueError('Retained bracket occupies complete proposed bearing; new interface design required')
        for i,(a,b) in enumerate(pieces):add(name+'-cope-'+str(i),(b-a).tolist(),((a+b)/2).tolist(),manufacturing=dict(method='net-rectangular-cope-plate; retained-bracket-pocket-definition',obstacle_occurrence_ids=sorted(set(witness)),cycle_hours=None,qualified_tooling=None))
        return sorted(set(witness))
    length=16.78;bottom=.49;top=.94;wall=.005;inner=1.26;outer=1.38;interface_records=[];cope_records=[]
    for side in (-1,1):
        y=side*1.32;prefix='sill-'+str(side)
        route=dict(method='fabricated-continuous-plate-strip; full-penetration-butt-weld-three-blanks-then-closed-section-longitudinal-weld',
            blank_segments=3,maximum_hypothetical_blank_length_m=6.,butt_seam_positions_x_m=[.11+length/3,.11+2*length/3],
            weld_procedure_id=None,HAZ_properties=None,cycle_hours=None,qualified_tooling=None,origin=None)
        for name,z in (('top',top-wall/2),('bottom',bottom+wall/2)):add(prefix+'-'+name,[length,.12,wall],[8.5,y,z],manufacturing=route)
        for name,yy in (('inner',side*(inner+wall/2)),('outer',side*(outer-wall/2))):add(prefix+'-'+name,[length,wall,.44],[8.5,yy,.715],manufacturing=route)
        weld_length=4*length+2*2*(.12+.45);bounds=(weld_length*.5*.004**2*2680,weld_length*.5*.006**2*2720)
        add(prefix+'-bounded-weld-deposition',[length,.12,.45],[8.5,y,.715],bounds=bounds,
            manufacturing=dict(method='bounded4-to6mm-deposition-profile; actual-filler-geometry-alloy-procedure-and-HAZ-unresolved',joint_length_m=weld_length,cycle_hours=None))
        for r in [r for r in rows if layer._is(r,'transverse-floor-member')]:
            x=float(r['position'][0])
            caps=[q for q in rows if q['occurrence']['occurrence_id'].split('/')[1].startswith('floor-rib-cap-') and q.get('grade') and q['grade'].startswith('AL-') and abs(q['position'][0]-x)<1e-8]
            if not caps:continue
            a=max(.11,float(r['lower'][0]));b=min(16.89,float(r['upper'][0]))
            if b-a<=1e-9:continue
            # Supports retained65mm cap overhang without intersecting its lower adhesive.
            witness=coped_bearing(prefix+'-cap-bearing-'+str(len(added)),[b-a,.065,.0075],[(a+b)/2,side*1.2925,.94375]);cope_records.append(dict(frame_x_m=x,side=side,retained_brackets=witness,net_stock_subtraction_executed=True))
        for bogie,x in enumerate(vehicle['interfaces']['bogie_centres_per_car_m']):
            # Five net end-diaphragm pieces clear the retained central rib/cap.
            yy=side*1.256;add(prefix+'-end-diaphragm-low-'+str(bogie),[.224,.008,.0715],[x,yy,.83675])
            for sign in (-1,1):add(prefix+'-end-diaphragm-side-'+str(bogie)+'-'+str(sign),[.082,.008,.0625],[x+sign*.071,yy,.90375])
            # Four countedM8 fasteners per finite bolster/sill end interface.
            for dx in (-.07,.07):
                for z in (.83,.91):
                    bolt=prefix+'-tie-'+str(bogie)+'-'+str(dx)+'-'+str(z);centre=[x+dx,side*1.26,z]
                    add(bolt+'-shaft',dict(length=.045,radius=.004),centre,kind='cylinder',axis=1)
                    for suffix,offset,thick,radius,rin in (('head',.026,.006,.007,0.),('nut',-.026,.007,.007,.004),('washer-a',.021,.0015,.009,.0045),('washer-b',-.021,.0015,.009,.0045)):
                        pos=list(centre);pos[1]+=offset;dim=dict(length=thick,radius=radius) if not rin else dict(length=thick,outer_radius=radius,inner_radius=rin)
                        add(bolt+'-'+suffix,dim,pos,kind='cylinder' if not rin else 'tube',axis=1)
            interface_records.append(dict(bogie_x_m=x,side=side,sill_inner_y_m=side*inner,bolster_outer_end_y_m=side*inner,
                diaphragm_regions=3,counted_M8_bolts=4,qualified_joint=False,plate_clearance_to_central_corridor_m=.0))
    occurrences=[]
    for o in vehicle['registry']['occurrences']:
        local=o['occurrence_id'].split('/',1)[1];car=int(o['occurrence_id'].split('/')[0].split('-')[1])
        if local in replace:
            p,T=replace[local];pose=deepcopy(T);pose[0][3]+=17.5*(car-1)
            occurrences.append(make_occurrence(o['occurrence_id'],p,parent_id=o['parent_id'],transform=pose,scope=o['scope']))
        else:occurrences.append(deepcopy(o))
    for car in range(1,7):
        for a in added:
            T=deepcopy(a['transform']);T[0][3]+=17.5*(car-1);occurrences.append(make_occurrence('car-'+str(car)+'/frame-'+a['name'],a['part'],parent_id='car-'+str(car)+'/primary-body',transform=T,scope='vehicle/primary-body'))
    used={o['part_definition_id'] for o in occurrences};partlist=[p for pid,p in parts.items() if pid in used]
    reg=make_registry(vehicle['label']+'; closed side-sill experiment',partlist,occurrences,vehicle['functional_requirements'],parent_candidate_id=vehicle['candidate_id'],assemblies=vehicle['registry']['assemblies'])
    result=deepcopy(vehicle);result.pop('evaluation_id');result.update(candidate_id=reg['candidate_id'],registry=reg,summary=summary(reg),label=vehicle['label']+'; closed side-sill experiment')
    pmap={p['physical_definition_id']:p for p in partlist};allmass=[]
    for o in reg['occurrences']:
        T=np.array(o['transform']);axis='x' if abs(T[0,2])>.9 else 'y' if abs(T[1,2])>.9 else 'z';allmass.append(dict(part=pmap[o['part_definition_id']],xyz=T[:3,3].tolist(),axis=axis,car=o['occurrence_id'].split('/')[0]))
    local=[r for r in allmass if r['car']=='car-1'];result['per_car_mass_properties']=_mass_properties(local);result['train_mass_properties']=_mass_properties(allmass)
    result['per_car_occurrences']=len(local);result['per_car_part_definitions']=len(partlist);result['per_car_functional_occurrences']={f:sum(f in r['part']['functions'] for r in local) for f in result['functional_requirements']}
    result['manufacturing_plan']=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],part_id=p['part_id'],process=p['manufacturing'],approved_work_instruction=None,qualified_tooling=None,required_inspections=['net-cope','weld-procedure-and-HAZ','dimensional','retention','NDT','load-test']) for p in partlist]
    delta=result['per_car_mass_properties']['mass_upper_bound_kg']-vehicle['per_car_mass_properties']['mass_upper_bound_kg'];supported= sum(r['part']['mass']['upper_bound_kg'] for r in rows if 'running-gear' not in r['part']['functions']);bound=necessary_bound(supported,delta)
    if delta>PARAMETERS['advisory_added_mass_budget_kg_per_car'] or not bound['domain_budget_from_this_bound']:raise ValueError('Advisory stock/resource sizing frontier failed; do not dispatch field solve')
    result['frame_refinement']=dict(parent_candidate_id=vehicle['candidate_id'],parent_vehicle_evaluation_id=vehicle['evaluation_id'],parameters=PARAMETERS,section=section(),necessary_bound=bound,preflight=fit,supported_parent_upper_mass_kg=supported,
        changed_stock=changes,bearing_cope_records=cope_records,new_occurrences_per_car=len(added),added_upper_mass_per_car_kg=delta,interfaces=interface_records,
        selection_purpose='next-experiment-only',stock_geometry_and_typical_stiffness_only=True,physical_strength_allowables=None,installed_clearance_accepted=False,
        material_property_class='B: published typical stiffness; geometry/process/joining and cost inputs remainC hypotheses',
        unresolved=['Actual full-body/contact response and refinement','HAZ, plate buckling, weld fatigue and local joint/bore allowables','Dynamic suspension/body/door/service and tool/lifting sweeps','Actual weld filler/profile and process qualification','Quoted installed and whole-life cost'])
    for side in (-1,1):
        T=np.eye(4);T[:3,3]=[8.5,side*1.32,.715];end=T.copy();end[1,3]+=side*1.0
        result['assembly_access'].append(dict(id='side-sill-install-'+str(side),function='primary-body',envelope_dimensions_m=[16.98,.30,.65],start_transform=T.tolist(),end_transform=end.tolist(),
            motion=dict(kind='linear-translation',sample_count=33,translation_m=[0.,side*1.0,0.]),tool_access_radius_m=.15,lifting_device='rated-two-point-assembly-cradle',
            required_tools=['body-trestles','weld-fixture','torque-tool','NDT'],sequence=['isolate-and-support-body','remove-bogies-and-conflicting-service-modules','fit-trimmed-transverse-members','lift-side-sill','fit-diaphragms-and-retention','weld-and-inspect','check-installed-sweeps'],
            clearance_and_lifting_verified=False,interference_resolution='Assembly requires open workshop access; continuous installed sweep and maintenance strategy unqualified'))
    result['source_sha256']=sources(vehicle,root);result['evaluation_id']=identity(result);layer._vehicle(result);return result
