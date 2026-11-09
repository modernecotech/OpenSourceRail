"""Installed terminal research family: source inputs and deterministic proposals.

No old terminal/body/catalogue producer or native evaluator is called. The two
unexecuted requests require explicit source/local/P1 inputs and separate review.
Known nominal failures, unknown supplier geometry and qualification stay distinct.
"""
from copy import deepcopy
import gzip
from math import fsum, pi, sqrt, isfinite
from pathlib import Path
import json

from engineering.station_rail.common import identity, digest

CASES=('low','base','high')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
RX180=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]]
YAXIS=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
ZAXIS=[[0.,0.,-1.],[0.,1.,0.],[1.,0.,0.]]
FAMILY='research/terminal-installed-end-r3'
SOURCE_ANCESTRY=dict(commit='dec0268f613480eb462f9229b86784b892eaa3d9',
 review_id='2818719424c557578457c7c735e59bb1a1e91c6cc04e009d0a5e5424c3119d87',
 held_source_report_id='08dc835abced822f993237a753ccbe73bc519fc2da2873d8ebf9ad9419f598f6')
PARENT=dict(candidate_id='5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',
 evaluation_id='d1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea',
 raw_sha256='f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23')
LOCAL=dict(physical_definition_id='1260c73b38176f79e6913c2323af538248df3ba9a1d0c0c53bcef4835bb44ebe',
 result_evaluation_id='d826397b3c85344a3ff0e1283b5f01579dab20030debbff069e8b1a22e3474a8',
 geometry_evaluation_id='edf0fc9ace4008cf5ad8d4eb61a5b2013a6d65bffcc9704f3917d8adabfaac08',
 accounting_evaluation_id='9f142abd32f70d7694f4a3debbebf4dfbbbc7618ec0a22f10d35142a74cb828d')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
 operating_release=False,selected_reference_changed=False,movement_authority=False,native_eligible=False)


def seal(x):
    x=deepcopy(x);x.pop('evaluation_id',None);x['evaluation_id']=identity(x);return x


def sources():
    root=Path(__file__).resolve().parents[1]
    return {n:digest(root/n) for n in ('engineering/terminal_installation.py','engineering/station_rail/common.py','engineering/design_search/requirement_policy.py')}


def _sealed(x,key='evaluation_id'):
    if x.get(key)!=identity({k:v for k,v in x.items() if k!=key}):raise ValueError('Input identity differs: '+key)


def read_authenticated(path,pin):
    if digest(path)!=pin['raw_sha256']:raise ValueError('Input rawSHA differs')
    p=Path(path);b=p.read_bytes();x=json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
    _sealed(x)
    if any(x[k]!=pin[k] for k in ('candidate_id','evaluation_id')) or identity(x['physical_definition'])!=x['candidate_id']:
        raise ValueError('Physical/evaluation source substitution')
    return x


def _cases(x):return {c:float(x[c]) for c in CASES} if isinstance(x,dict) else dict(zip(CASES,x)) if isinstance(x,(list,tuple)) else dict.fromkeys(CASES,float(x))
def _positive(xs):
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) or x<=0 for x in xs):raise ValueError('Finite positive physical inputs required')
def _add(a,b):return [a[i]+b[i] for i in range(3)]
def _mul(A,B):return [[fsum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def transform(p,at,R):return [at[i]+fsum(R[i][j]*p[j] for j in range(3)) for i in range(3)]
def inverse(p,at,R):return [fsum(R[i][j]*(p[i]-at[i]) for i in range(3)) for j in range(3)]


def recipe():
    """Input proposal only; does not read P1 or materialize a terminal."""
    return dict(schema='osr-terminal-installation-input/1',family=FAMILY,units='m',source_ancestry=dict(deepcopy(SOURCE_ANCESTRY),reviewfix_parent_commit='4c8d4a79ab680a9e01812cebdcfb051252bbdb9e',residual_review_id='a9e514ccf042f6f68e9b08614b41fb44209161a785bbc0c6e9d0c8400fe94f36'),parent=deepcopy(PARENT),local=deepcopy(LOCAL),
      fixed=dict(cars=6,car_length_m=17.,body_width_m=2.65,seal_frame_width_m=2.45,floor_Z_m=1.15,roof_skin_bottom_Z_m=3.55,
        formation_pitch_m=17.65,train_structural_length_m=105.25,body_lift_already_applied_m=.15),
      bindings=[dict(id='terminal/front',source_end='body/terminal-end/end-0',car=0,at_m=[0.,0.,2.25],rotation=RX180),
                dict(id='terminal/rear',source_end='body/terminal-end/end-5',car=5,at_m=[105.25,0.,2.25],rotation=I)],
      geometry=dict(fixed_post_absV_m=1.165,fixed_post_outer_absV_m=1.215,header_lower_length_m=2.23,
        land_upper_corner_notches=dict(absV_m=[1.215,1.225],w_m=[.95,1.10]),
        canopy=dict(fascia_u_m=.0785,fascia_bottom_Z_m=3.33,fascia_top_Z_m=3.55,fascia_width_m=2.45,
          roof_underlap_Z_m=3.547,roof_underlap_width_m=2.43,roof_underlap_u_m=[-.10,.0775],thickness_m=.002),
        side=dict(front_filler_u_m=.075,front_filler_absV_m=[1.225,1.325],front_filler_Z_m=[1.15,3.55],
          endbay_u_m=[-1.43,0.],endbay_panel_absV_center_m=1.321,endbay_panel_Z_m=[1.15,3.30],thickness_m=.002,
          source_first_post_X_m=.8,source_post_XY_m=[.060,.080],source_post_wall_m=.003,
          clamp_rows_Z_m=[1.40,2.30,3.15],stiffener_YZ_m=[.020,.120],stiffener_wall_m=.003,
          stiffener_front_X_m=[.110,.761],stiffener_rear_X_m=[.839,1.430],
          cantrail_weather_flange_Z_m=3.301,cantrail_weather_flange_absV_m=[1.241,1.321],
          sill_weather_flange_Z_m=1.113,sill_weather_flange_absV_m=[1.205,1.285]),
        floor=dict(bridge_X_m=[.100,.260],bridge_width_m=2.644,plate_gross_t_m=.006,
          gap_X_m=[.100,.220],rear_lap_X_m=[.220,.260],rear_lap_net_t_m=.00275,lap_sealant_m=.00025,
          support_X_m=[.100,.216],support_YZ_m=[.020,.030],support_wall_m=.003,
          support_top_Z_m=1.144,support_lanes_Y_m=[-1.30]+[j/5 for j in range(-6,7)]+[1.30],
          root_cap_U_m=[-.100,-.050],root_cap_Z_m=[1.138,1.150],root_web_U_m=[-.100,-.050],root_web_Z_m=[1.114,1.138],
          root_route='One solid Al5083 billet block50mmU x36mmZ;40mm/140mmV width,no web-cap weld or separate purchases',
          post_bottom_closure_t_m=.010,post_bottom_Z_m=1.160),
        upper=dict(cantrail_X_stations_m=[.050],cantrail_Z_stations_m=[3.390,3.490],cantrail_inner_absY_m=1.225,
          cantrail_wall_m=.0045,lug_absY_m=[1.215,1.221],spacer_m=.003,pad_m=.001,backer_m=.004,
          endcap_u_m=[.002,.008],endcap_YZ_m=[.099,.249],endcap_center_Z_m=3.430,
          tip_protection='one-piece machined GFRPcage with rigid hood',hood_outer_radius_m=.0066,hood_bore_m=.0085,
          hood_annular_V_from_underhead_m=[.0325,.0375],hood_closed_end_V_from_underhead_m=[.0375,.0385],
          detachable_liner_collar_t_m=.0005,detachable_liner_collar_OD_m=.011,pull_recess_depth_m=.0024,
          pull_entry='open-to-tie-bottom;3mmwide flatmill slot with1.5mm radiused closedend',pull_slot_W_from_bolt_m=[-.030,.003],pull_slot_radius_m=.0015,extractor_parts_UVW_m=upper_liner_tool_parts(),
          cap_connector='finite exposed U8mm edge bead; explicit two triangular crosssections,not buried U5mm fillet'),
        lower=dict(beam_size_m=[2.29,.14,.25],beam_wall_m=.008,beam_center_uvw_m=[-.1,0.,-1.2655],
          mount_v_m=[-.83,-.77,-.43,-.37,.37,.43,.77,.83],mount_w_m=-1.18,
          entry_u_m=-.170,entry_bore_m=.0182,rear_u_m=-.038,rear_bore_m=.0085,sleeve_length_m=.132)),
      hypotheses=dict(stock_position_m=.002,relative_fixture_position_m=.00030,drill_m=.00010,flatness_m=.00010,
        finish_m=.000040,minimum_clearance_m=.0005,seal_line_load_N_m=1000.,side_pressure_Pa=1000.,
        side_support_point_force_N=500.,floor_point_force_N=500.,Al_E_Pa=69e9,Al_stress_Pa=60e6,
        deflection_m=.001,body_profile_and_fixture_achieved=False),
      materials={k:dict(density_kg_m3=d,density_bounds_kg_m3=[d*.97,d*1.03],rate_USD_kg=r,basis='Calculated2026-11-09source research material/process hypotheses; no quotation or discount') for k,d,r in (
        ('al6005a',2700.,[3.,4.5,7.]),('al5083',2660.,[3.5,5.,8.]),('al5754',2680.,[3.2,4.8,7.5]),
        ('stainless',8000.,[4.,6.,10.]),('gfrp',1900.,[6.,12.,25.]),('elastomer',1200.,[4.,8.,15.]),('sealant',1100.,[8.,15.,30.]),('coating',1300.,[8.,15.,30.]))},
      process=dict(labour_USD_h=[6.,10.,16.],cut_kerf_m=.003,cut_trim_m=.004,cut_reserve_m=.004,
        plate_edge_allowance_m=.002,weld_procurement_factor=1.20,finish_procurement_factor=1.20,
        fixture_setup_h_per_end=8.,survey_QA_h_per_end=4.,land_face_lap_h_per_end=3.,
        shared_fixture_mass_kg=[20.,35.,60.],shared_fixture_cost_USD=[200.,500.,1200.],
        fixture_quantity='one separately owned workshop fixture for two ends, not installed'),
      fitted_weather_interfaces=dict(adjustment_m=[-.003,.003],mechanism='Survey source faces,cut-to-fit oversized closure/standoff stock before final weld/assembly; captured shim stock/positive trim reserve and QA retained; every actual cut dimension changes physicalID',
        fitted_gap_tolerance_m=.00030,free_seal_height_tolerance_m=.00010,shim_pack_mass_kg=[.20,.40,.80],shim_pack_cost_USD=[5.,12.,30.],
        as_built_fit_measured=False,unadjusted_source_zone_failure_preserved=True),
      old_compression_failure=dict(interval_m=[-.002,.006],preserved=True),
      requirement_policy=dict(reference='engineering/design_search/requirement_policy.py',
        physical_clearance=dict(category='mandatory_obligation',kind='physical-interface',limit='Derived from actual source contact/load/motion interfaces; no tolerance waiver'),
        positive_compression=dict(category='mandatory_obligation',kind='functional',limit='Positive fitted seal compression; material force/maximum strain/fire limits unqualified'),
        stock_deflection_1mm=dict(category='revisable_assumption',model_domain='Ideal closure support under declared500N/900Npermetre loads; combine joint/motion/tolerance/compression budgets,not universal body limit'),
        stock_stress_60MPa=dict(category='revisable_assumption',model_domain='UnmeasuredAlstock/HAZallowable,not material certification or fatigue limit')),
      wider_cladding_issue=dict(part_ids=['body/lower-side-skin','body/upper-side-skin','body/side-pillar-cap','body/aperture-corner-trim'],
        reason='Generic P1cladding blanks do not prove continuous weather coverage beyond the new endbay. Preserve unchanged source occurrences; no whole-body enclosure claim.'),
      holds=['Gasket force/creep/fire and all weatherstrip compounds/adhesive durability unknown',
        'Glass/retainer/insert drawings, edge loading and crash retention not qualified',
        'Weld WPS/HAZ/fatigue, source wall/cleat loads and actual pressure/crowd/crash limits open',
        'Machining/fixture/flatness/tolerance values are unmeasured achievable proposals, not acceptance',
        'Independent source/tool/motion/lifting/coat allowances and whole-body integration remain required'],**FLAGS)


def physical_projection(r):
    return dict(schema='osr-terminal-installed-input-physical/1',family=r['family'],source_ancestry=deepcopy(r['source_ancestry']),fixed=deepcopy(r['fixed']),
      bindings=deepcopy(r['bindings']),geometry=deepcopy(r['geometry']),
      materials={k:dict(material=k) for k in r['materials']},parent_candidate_id=r['parent']['candidate_id'],
      local_physical_definition_id=r['local']['physical_definition_id'])


def validate_fixed_recipe(r):
    """This bounded family is one recipe, not an unchecked parameter campaign."""
    baseline=recipe()
    if r['fixed']!=baseline['fixed'] or r['bindings']!=baseline['bindings'] or r['geometry']!=baseline['geometry']:
        raise ValueError('Unreviewed fixed interface/rotation/geometry recipe; define a new explicit revision')


def ordered_stack(name,layers,bolt_length,nut_height,*,pitch,minimum_threads=2):
    """Ordered actual boundary planes, not independent washer/nut nudges."""
    if any(t<=0 for _,t in layers) or min(bolt_length,nut_height,pitch)<=0:raise ValueError('Positive joint layers required')
    at=0.;planes=[]
    for part,t in layers:planes.append(dict(part=part,start_m=at,end_m=at+t));at+=t
    projection=bolt_length-at-nut_height
    if projection<minimum_threads*pitch:raise ValueError('Insufficient actual thread projection')
    return dict(id=name,layers=planes,grip_m=at,nut_m=[at,at+nut_height],bolt_tip_m=bolt_length,
        projection_m=projection,minimum_projection_m=minimum_threads*pitch,strength_qualified=False)


def matched_lower_joint(*,width=.140,wall=.008,sleeve=.132,entry_bore=.0182,rear_bore=.0085):
    """One proposed180mm M8 stack against actual140x250x8Al beam."""
    if width!=.140 or wall!=.008 or abs(sleeve-(width-wall))>1e-12:raise ValueError('P1beam/sleeve bearing mismatch')
    if entry_bore<.018 or rear_bore<.008 or rear_bore>=.018:raise ValueError('Bore continuity or sleeve bearing fails')
    st=ordered_stack('lower-M8',[('front washer',.002),('front spreader',.008),('Z bracket',.008),
        ('beam/sleeve outer depth',width),('rear washer',.002)],.180,.008,pitch=.00125)
    st.update(sleeve_interval_from_beam_entry_m=[0.,sleeve],rear_wall_bearing_m=[width-wall,width],
      entry_bore_m=entry_bore,rear_bore_m=rear_bore,radial_entry_clearance_m=(entry_bore-.018)/2,
      radial_rear_clearance_m=(rear_bore-.008)/2,nominal_top_edge_ligament_m=.125-.0855-entry_bore/2,
      retained_nut_washer_compatibility='Held: nominal source stack, authenticated supplier grade/profile still required')
    return st


def upper_joint():
    return ordered_stack('upper-M6',[('steel washer',.0015),('GFRPwasher',.002),('Al lug',.006),('Al spacer',.003),
      ('GFRPpad',.001),('cantrail wall',.0045),('Al backer',.004),('GFRPwasher',.002),('steel washer',.0015)],.035,.005,pitch=.001)


def post_joint(wall=.003):
    st=ordered_stack('side-post-M6',[('steel washer',.0015),('GFRPwasher',.001),('Al clamp',.004),('GFRPpad',.001),
      ('post outer widthX',.060),('GFRPpad',.001),('Al clamp',.004),('GFRPwasher',.001),('steel washer',.0015)],.085,.005,pitch=.001)
    st.update(crush_sleeve_m=.060-2*wall,through_GFRP_liner_m=.070,source_bore_m=.0182,
      liner_OD_m=.018,liner_ID_m=.0142,crush_OD_m=.014,crush_ID_m=.0065)
    if st['crush_sleeve_m']<=0:raise ValueError('Source post wall consumes sleeve void')
    return st


def upper_frame_joint():
    """Detachable tie into an owned internal Al boss; not a source-wall tap."""
    return dict(kind='blind-threaded-boss',bolt_length_m=.025,underhead_absV_m=1.2235,
      layers=[dict(part=n,start_m=a,end_m=b) for n,a,b in (
        ('steel washer',0.,.0015),('GFRPwasher',.0015,.002),('GFRPcollar',.002,.0025),('Al tie',.0025,.0085),('Al postwall',.0085,.0125))],
      liner_length_m=.010,liner_OD_m=.008,liner_ID_m=.0065,bore_m=.0082,
      liner_collar_t_m=.0005,liner_collar_OD_m=.011,liner_collar_from_underhead_m=[.002,.0025],
      boss_front_absV_m=1.211,boss_back_absV_m=1.191,bolt_tip_absV_m=1.1985,
      thread_engagement_m=.0125,pilot_depth_m=.014,remaining_pilot_m=.0015,remaining_boss_web_m=.006,
      combined_depth_length_tolerance_m=.0003,remaining_pilot_bound_m=.0012,strength_qualified=False)


def floor_root_spec(y):
    """One continuous hanger, behind the floorcover leading plane U=-.100."""
    outer=abs(y)>1.15;sign=1 if y>0 else -1;cy=sign*1.25 if outer else y;width=.140 if outer else .040
    return dict(outer=outer,centre_V_m=cy,width_m=width,
      block=dict(size_m=[.050,width,.036],at_m=[-.075,cy,1.132-2.25]),
      frame_contact=dict(U_m=[-.100,-.050],V_m=[sign*1.1975-.0175,sign*1.1975+.0175] if outer else [cy-.020,cy+.020],Z_m=1.150,
        owner='new10mm postbottom closure' if outer else 'fixed lowerrail4mm bottomwall'),
      tube_face_U_m=-.100,tube_face_Z_m=[1.114,1.144],
      floorcover_overlap_volume_m3=0.,post_endcap_required=outer,load_qualified=False)


def floor_root_stock(s,name,y):
    """Tiny leaf builder, also used by invented-fixture tests; no P1 builder."""
    d=floor_root_spec(y);cy=d['centre_V_m'];w=d['width_m'];fc=d['frame_contact']
    s.box(name+'/block',d['block']['size_m'],d['block']['at_m'],process=.25,qa=.12,
      basis='One solidAl5083billet with faced top/root planes,positive kerf/trim/reserve; upper/lower regions are continuous material,not welded sheet')
    v=sum(fc['V_m'])/2;vw=fc['V_m'][1]-fc['V_m'][0]
    s.weld(name+'/cap-frame-weld',2*(.050+vw),[-.075,v,1.150-2.25],axes=(0,1),profile=(.050,vw))
    s.joints.append(dict(id=name,kind='continuous underframe hanger',geometry=d,
      owned_members=[name+'/block'],counterpart='fixed-post-bottom closure' if d['outer'] else 'fixed-lowerrail bottomwall',
      sequence='Weld solidblock top to actual frame bottom material; weld RHS end internally through open side before closing fabricated tube',
      remaining_obligations=['Framewall/endplate/weld local loads,HAZ/fatigue/joint rotation','Actual coupled floor/service/crowd loads'],qualified=False))
    return d


def floor_tube_root_weld(s,name,y):
    #Internal end welds are applied through the open longitudinal wall BEFORE
    #closing the fabricated tube. They do not protrude into the floorcover.
    e=s.weld(name,2*(.014+.024),[-.100,y,1.129-2.25],leg=.003,axes=(1,2),profile=(.014,.024))
    e['at_m'][0]-=.0015;e['geometry']['size_m'][0]=.003;e['centroid_local_m'][0]=.0005
    #Rectangle vertices are shared by adjacent seam records. Rebuild points
    #instead of mutating each occurrence (which would shift corners twice).
    e['physical_drawing']['local_segments_m']=[[[p[0]+.0015,p[1],p[2]] for p in line] for line in e['physical_drawing']['local_segments_m']]
    a,b,c=e['geometry']['size_m'];e['shape_I_per_kg']=[[(b*b+c*c)/12,0.,0.],[0.,(a*a+c*c)/12,0.],[0.,0.,(a*a+b*b)/12]]
    e['physical_drawing'].update(fillet_axis=0,fillet_direction=-1,centroid_from_joint_plane_U_m=-.001,
      deposition='Inside RHS void before closing wall; no rootblock/plate material is added twice')
    s.joints.append(dict(id=name,kind='internal RHS-to-composite-root endweld',tube_end_U_m=-.100,
      root_block_Z_m=[1.114,1.150],tube_end_Z_m=[1.114,1.144],
      corner='Inner14x24mm perimeter at the end plane; deposited fillets lie in the tube void,not the floorcover',
      sequence='Apply before the last longitudinal plate closes access; inspect weld then close tube',strength_qualified=False))
    return e


def post_bottom_stock(s,name,sign):
    cy=sign*1.165
    e=s.box(name+'/closure',[.100,.100,.010],[-.050,cy,1.155-2.25])
    #Three external sides; stop3mm before the front land. These real paths
    #touch the postend/closure,not a fabricated full bottom of a hollow tube.
    paths=[[[-.050,-.047,0.],[-.050,.047,0.]],
      [[-.050,-.050,0.],[.047,-.050,0.]],[[.047,.050,0.],[-.050,.050,0.]]]
    s.weld(name+'/post-closure-weld',.288,[-.050,cy,1.160-2.25],segments=paths)
    s.joints.append(dict(id=name,kind='new closed postbottom',post_bottom_Z_m=1.160,post_top_Z_m=3.350,
      post_length_m=2.190,closure_Z_m=[1.150,1.160],closure_id=e['id'],post_stock_removed_m=.010,
      contact='Three finite outer postwall/endplate seams; no imaginary solid across the open RHS end',strength_qualified=False))
    return e


def tab_weld_segments(sign):
    return [[[u,-sign*.0015,-.020],[u,-sign*.0015,.020]] for u in (-.002,.002)]


def cap_connector_segments(sign):
    return [[[0.,0.,-.010],[0.,0.,.010]],[[.006,sign*.0045,-.010],[.006,sign*.0045,.010]]]


def cap_connector_stock(s,name,origin,sign):
    """Finite exposed-edge weld profiles with real parent-face contact.

    No invisible groove: seam1 joins exposed oppositequadrants; seam2 is an
    external reinforcement bead on U=.008 sidefaces of the touching parents.
    Exact WPS/penetration/runout/tool qualification remains explicitly held.
    """
    e=s.weld(name,.040,origin,segments=cap_connector_segments(sign),process_h=.25,qa_h=.15)
    profiles=[[[0.,0.],[-.003,0.],[0.,sign*.003]],
              [[.006,sign*.003],[.006,sign*.006],[.009,sign*.0045]]]
    #Botharea4.5mm2; centroid is length/areaweighted,not centrelineonly.
    centre=[fsum(p[k] for tri in profiles for p in tri)/6 for k in range(2)]
    e['centroid_local_m']=[origin[0]+centre[0]-e['at_m'][0],origin[1]+centre[1]-e['at_m'][1],origin[2]-e['at_m'][2]]
    e['physical_drawing'].update(kind='two-explicit-extruded-triangular-weld-profiles',
      profile_vertices_UV_from_station_m=profiles,W_from_station_m=[-.010,.010],
      triangle_orientation_defined=True,exact_triangle_orientation_and_runout_resolved=False,
      source_contacts=[dict(seam=0,faces='innerarm Vedge andcrossarm Uedge,finite3mmlegs'),
        dict(seam=1,faces='externalU8mm sidefaces,crossarmV1.224..1.2255,capV1.2255..1.227')],
      joint_preparation='Squarefinished parentedge cuts alreadyowned; deburr/degrease/fixture beforeweathercovers. No groove or extra parentmaterial removal assumed.',
      tool_access='Ownsubassembly open towardpositiveU; proposedtorchbody U20..60mm,radius6mm. Wholebody/fixture/arc/WPSaccess unresolved.',
      penetration_runout_WPS_qualified=False)
    e['centroid_basis']='Exact declared uniform finite triangularprism centroid; actualdeposition/HAZ/runout andinertiaadaptation remainunqualified'
    s.joints.append(dict(id=name,kind='finite exposedface connector weld',
      profile_origin_m=list(origin),profile_vertices_UV_m=profiles,W_m=[-.010,.010],
      added_groove_or_parentcut=False,process_h=.25,QA_h=.15,nominal_parent_material_nonoverlap=True,
      source_eligibility='Tiny ownsubassembly only;fullscene/WPS/strength/native held',qualified=False))
    return e


def side_frame_joint():
    return dict(kind='blind-threaded-endplate',bolt_length_m=.020,layers=[dict(part=n,start_m=a,end_m=b) for n,a,b in (
      ('steel washer',0.,.0015),('GFRPwasher',.0015,.0025),('frame outrigger',.0025,.0085),('GFRPpad',.0085,.0125))],
      liner_length_m=.010,liner_OD_m=.006,liner_ID_m=.0045,bore_m=.0062,
      thread_engagement_m=.0075,pilot_depth_m=.0085,remaining_pilot_m=.001,remaining_boss_web_m=.0035,
      combined_depth_length_tolerance_m=.0003,remaining_pilot_bound_m=.0007,strength_qualified=False)


def upper_cage_contract():
    st=upper_joint();nut_end=st['nut_m'][1];cage=[.0305,.0325];hood=[.0325,.0375];end=[.0375,.0385]
    radial=(.0085-.0001-(.006+.00005))/2
    axial=end[0]-st['bolt_tip_m']-.0007
    retention=(.006*.92*2-.0001-(.0085+.0001))/2
    if min(radial,axial,retention)<=0 or abs(nut_end-cage[0])>1e-12:raise ValueError('Upper rigid cap/retention interference')
    return dict(kind='rigid machined GFRPcage/hood',cage_V_from_underhead_m=cage,hood_V_from_underhead_m=hood,end_V_from_underhead_m=end,
      bore_m=.0085,hood_outer_radius_m=.0066,bolt_diameter_m=.006,
      tip_axial_clearance_m=end[0]-st['bolt_tip_m'],tip_clearance_bound_m=axial,radial_clearance_bound_m=radial,
      nut_retention_radial_bound_m=retention,M3_tool_radius_m=.0035,M3_tool_axis_U_m=[-.013,.013],
      M3_tool_hood_radial_clearance_bound_m=.013-.0035-.0066-.0002,
      tolerance_domain='Relative joint stack/bolt length/cap depth0.7mm axial; bores0.1mm diametral,bolt0.05mm,nutOD0.1mm. Proposed manufacturing values,not measurements or independent wholebody position errors.',
      retention='Rigid annular shoulder catches nut end after bolt release; two existing M3 retainers hold integral cage. Hood cap is positively closed,not compressed elastomer.',
      unknowns=['Exact nut hex/counterhold and GFRPcompound strength/fire/creep','Extraction forces and real tool capability'],physical_accepted=False)


def upper_liner_slot_spec():
    """Own open-bottom flat-milled recess; dimensions relative to a boltaxis."""
    width=.003;radius=width/2;bottom=-.030;centre=.0015;depth=.0024
    A=width*(centre-bottom)+pi*radius**2/2
    cw=(width*(centre-bottom)*(bottom+centre)/2+(pi*radius**2/2)*(centre+4*radius/(3*pi)))/A
    return dict(width_m=width,depth_m=depth,bottom_W_m=bottom,round_end_centre_W_m=centre,
      closed_end_W_m=centre+radius,end_radius_m=radius,section_area_m2=A,removed_volume_m3=A*depth,
      removed_centroid_W_m=cw,tool='3mm flat endmill, enter from existing tie bottom; blind2.4mm depth; no imaginary square closedcorners',
      remaining_tie_depth_m=.006-depth,source_bore_radial_ligament_m=.0045-.0082/2,
      local_wall_strength_qualified=False,slot_process_h_each=.10,slot_QA_h_each=.04,
      added_finish_surface_upper_reference_m2=A+(2*(centre-bottom)+pi*radius+width)*depth)


def upper_liner_tie_stock(s,name,sign):
    """One own tie and exact open/radiused cuts, not a terminal producer."""
    r=s.r;y=sign
    tie=s.box(name,[.070,.006,.120],[-.050,y*1.218,3.300-2.25],
      holes=[_hole(1,[du,0.,-.030],.0082,.006) for du in (-.020,.020)])
    slot=upper_liner_slot_spec()
    recesses=[(slot['removed_volume_m3'],[du+off,y*(.003-slot['depth_m']/2),-.030+slot['removed_centroid_W_m']]) for du in (-.020,.020) for off in (-.006,.006)]
    _remove_drawing_material(s,tie,recesses,dict(kind='tie-with-two-bores-and-four-open-roundended-extractor-slots',
      original_box_size_m=[.070,.006,.120],bores=deepcopy(tie['geometry']['holes']),
      slot_spec=slot,slot_U_centres_local_m=[du+off for du in (-.020,.020) for off in (-.006,.006)],
      bolt_W_local_m=-.030,opening='Eachslot meets actual tie bottomW=-.060; millfromoutsideexistingbottom',
      removed_centroids_local_m=[c for v,c in recesses],remaining_netsection_qualification=False))
    tg=next(a for a in s.groups if a['entity_ids']==[tie['id']]);tg['QA_h']+=4*slot['slot_QA_h_each'];tg['process_h']+=4*slot['slot_process_h_each']
    for i,c in enumerate(CASES):tg['direct_cost_usd'][c]+=4*slot['slot_QA_h_each']*r['process']['labour_USD_h'][i]
    tg['contour_process_basis']='Existing contour-removal helper charges0.10h/cut once; mirrored inprocess_h,not chargedagain. Extra0.04hQA/slot explicit.'
    tie['additional_finish_surface_reference_m2']=4*slot['added_finish_surface_upper_reference_m2']
    return tie


def upper_liner_tool_parts():
    """Disjoint regions of ONE machined stainless fork, never separatepurchases.

    Right-hand alpha=side*U,beta=side*V,gamma=W; beta0 is tieouterface.
    Proper side rotations I/RX180 preserve dimensions without a reflection.
    """
    rows=[dict(name='handle',size_m=[.016,.002,.048],at_m=[0.,.002,-.039])]
    for sign in (-1,1):
        rows.extend([dict(name=f'tip/{sign}',size_m=[.0026,.002,.012],at_m=[sign*.006,-.0012,-.006]),
          dict(name=f'step/{sign}',size_m=[.0026,.0052,.003],at_m=[sign*.006,.0004,-.0135])])
    return rows


def upper_liner_removal_contract():
    slot=upper_liner_slot_spec();parts=upper_liner_tool_parts()
    V=fsum(x['size_m'][0]*x['size_m'][1]*x['size_m'][2] for x in parts)
    #Worstcase all20N on either2mm-thick tip, with12mm momentarm.
    force=20.;E=190e9;allow=150e6;width=.0026;thick=.002;span=.012
    J=width*thick**3/12;stress=force*span/(J/(thick/2));deflect=force*span**3/(3*E*J)
    return dict(quantity_per_end=4,kit='upper-frame/{side}/{station}/M6/liner-kit',
      material_entities=['upper-frame/{side}/{station}/M6/liner','upper-frame/{side}/{station}/M6/liner-collar'],
      installed_stem_absV_m=[1.211,1.221],collar_absV_m=[1.221,1.2215],collar_OD_m=.011,stem_OD_m=.008,bore_m=.0082,
      stages=['Keep body-side cantrailM6 restraints/ties/caps engaged; support bareframe',
        'Remove/capture4blindM6 bolts and steel/GFRPwashers/end; remove endbay panels before toolentry',
        'Place complete steppedfork below tie bottom; insert32mm alongW through counted open-bottom slots at fixedbeta,then takeup0.2mm outward to collar',
        'Pull20mm outward along signedV; capture each integral collar/stem kit and inspect all8tie/postwall passages empty; log4kits before90mm frame lift'],
      relative_path_m=[[0.,0.,0.],[0.,.020,0.]],direction='sign(side) alongV using properI/RX180 toolframes,not reflection',
      tool_frame=dict(origin='eachbolt U andW, tieouterface absV1.221',positive_rotation=I,negative_rotation=RX180,axes='alpha=side*U,beta=side*V,gamma=W'),
      extractor_tip_path_m=[[0.,0.,-.032],[0.,0.,0.],[0.,.0002,0.],[0.,.0202,0.]],
      extractor_motion='Fulltool starts with tips2mm below tiebottom; insert alongW in actual openslots,then takeup andpull. Fulltool/wholebody/lifting evaluation remains held.',
      minimum_stem_clearance_after_pull_m=1.211+.020-1.221,
      recess_U_from_bolt_axis_m=[[-.0075,-.0045],[.0045,.0075]],recess_W_m=[slot['bottom_W_m'],slot['closed_end_W_m']],
      recess_absV_m=[1.221-slot['depth_m'],1.221],slot=slot,
      recess_depth_m=slot['depth_m'],extractor_tip_t_m=.002,tool_gap_bound_m=min(slot['depth_m']-.0022,.0002)-.0001-deflect,
      tool_U_side_clearance_bound_m=(.003-.0026)/2-.0001,
      collar_engagement_bound_m=.0055-.0047-.0002,cantrail_tool_vertical_clearance_bound_m=3.305-(3.270+.008)-.00234,
      capture_retention='Integral flange is clamped by washer inservice. Duringmanual service support/capture eachkit before logging; actual operator/tool/pull/retention validation remains held.',
      workshop_extractor=dict(quantity_per_train=1,installed=False,material='stainless',blank_size_m=[.063,.016,.0052],
        drawing='One machined fork; exact disjoint handle/two2mm-thicktips/two steppedweb regions inparts_m,all fromoneblank; no fictitious bodyentry',
        parts_m=parts,net_volume_m3=V,gross_volume_m3=.074*.020*.0052,process_h=.70,QA_h=.30,
        envelope_m=[.016,.0052,.063],envelope_at_m=[0.,.0004,-.0315],tip_nominal_V_clearance_m=.0002,maximum_proposed_pull_N=force,pull_capability_measured=False,
        necessary_tip_bound=dict(force_per_tip_N=force,loadsharing_credit=False,E_hypothesis_Pa=E,allowable_hypothesis_Pa=allow,
          span_m=span,stress_Pa=stress,deflection_m=deflect,stress_residual_Pa=allow-stress,
          scope='Unmeasured idealstock-only20N worsttip calculation; handle/step/stressconcentration/fatigue/operator capability stillunqualified')),
      lift_preconditions=['4 bolts captured','4 steel+GFRPwasher pairs captured','4 integral liner kits captured','all8tie/postwall passages inspected empty'],
      qualification='Tip/material/pullforce/collarstrength/wholetool andactualbody capability unqualified; explicit ownvoid path is not installedacceptance',physical_accepted=False)


def assert_frame_lift_ready(captured):
    expected={f'upper-frame/{y}/{j}/M6/liner-kit' for y in (-1,1) for j in range(2)}
    if set(captured)!=expected or len(captured)!=4:raise ValueError('All four bridging upper liner kits must be captured before frame lift')
    return True


def removal_bounds(r):
    """Exact cheap material witness and bounded lift-first stage, not a full sweep."""
    h=r['hypotheses'];allow=h['stock_position_m']+h['relative_fixture_position_m']+h['finish_m']
    return dict(failed_outward_first=dict(translation_uvw_m=[.002,0.,0.],witness_uvw_m=[-.169,.8,-1.18],
      moving_foot_u_m=[-.176,-.168],retained_beam_wall_u_m=[-.170,-.162],penetration_u_m=.002,
      reason='Foot lies behind intact entry-wall material between separate mounting holes; hardware removal does not remove beam material',screen='FAIL'),
      lift_first_m=.090,foot_after_lift_Z_m=[1.120,1.200],beam_top_Z_m=1.1095,
      lower_vertical_clearance_bound_m=1.120-1.1095-allow,
      roof_support_after_lift_top_Z_m=3.520,roof_bottom_Z_m=3.550,
      roof_clearance_bound_m=.030-allow,floor_support_rear_gap_bound_m=.220-r['geometry']['floor']['support_X_m'][1]-allow,
      land_unrelieved_after_lift_top_Z_m=3.290,cantrail_bottom_Z_m=3.305,
      upper_land_vertical_clearance_bound_m=.015-allow,
      mandatory_removed=['roof underlap and fascia','sidefront fillers','stepped floorcover','endbay sidepanels','upper-frame M6 blind bolts','side-frame M4 bolts','all lower M8 hardware and sleeves'],
      stays_with_body=['upper cantrail lugs/ties/caps/backers','sidepost Uclamps and longitudinal side stiffeners'],
      scope='Necessary cross-section/roof/floor bounds for staged bare-frame90mm lift then300mm outward. Continuous whole-assembly/tool/lifting sweep remains required; no installed acceptance',physical_accepted=False)


def section_bound(width,depth,wall,L,force,E,allowable,*,uniform_N_m=0.):
    if not 0<2*wall<min(width,depth) or min(L,force,E,allowable)<=0:raise ValueError('Positive section hypothesis required')
    J=(width*depth**3-(width-2*wall)*(depth-2*wall)**3)/12;Z=J/(depth/2)
    M=force*L+uniform_N_m*L*L/2
    return dict(I_m4=J,stress_Pa=M/Z,stress_residual_Pa=allowable-M/Z,
      tip_deflection_m=force*L**3/(3*E*J)+uniform_N_m*L**4/(8*E*J),
      scope='Conservative ideal stock cantilever under declared unmeasured point+line loads; joints/HAZ/fatigue/localwalls not qualified')


def necessary_bounds(r):
    g=r['geometry'];h=r['hypotheses'];postgap=1.225-g['fixed_post_outer_absV_m']
    source_and_new=h['stock_position_m']+h['relative_fixture_position_m']+h['finish_m']
    side=g['side'];L=max(b-a for a,b in (side['stiffener_front_X_m'],side['stiffener_rear_X_m']))
    current=section_bound(*side['stiffener_YZ_m'],side['stiffener_wall_m'],L,h['side_support_point_force_N'],h['Al_E_Pa'],h['Al_stress_Pa'],uniform_N_m=h['side_pressure_Pa']*.90)
    current['span_m']=L
    previous=section_bound(.020,.040,.003,.591,h['side_support_point_force_N'],h['Al_E_Pa'],h['Al_stress_Pa'],uniform_N_m=h['side_pressure_Pa']*.90)
    failed80=section_bound(.020,.080,.003,.591,h['side_support_point_force_N'],h['Al_E_Pa'],h['Al_stress_Pa'],uniform_N_m=h['side_pressure_Pa']*.90)
    span=g['floor']['support_X_m'][1]-g['floor']['support_X_m'][0]
    floor=section_bound(.020,.030,.003,span,h['floor_point_force_N'],h['Al_E_Pa'],h['Al_stress_Pa']);floor['span_m']=span
    #Outer widehanger carries two500N support reactions; only the outer500N
    #has85mm overhang beyond the postcap. Conservatively take no stiffness
    #credit for its continuous24mm lower billet region when screening only
    #the upper12mm wing. This is deliberately a conservative stock bound.
    capI=.050*.012**3/12;Lwing=1.300-1.215;F=h['floor_point_force_N']
    wing_def=F*Lwing**3/(3*h['Al_E_Pa']*capI);wing_stress=F*Lwing/(capI/(.012/2))
    #10mm postbottom closure,100mm simple span/50mm effective strip,
    #1000N centre load. Edge/weld flexibility remains an explicit extra hold.
    endI=.050*.010**3/12;end_def=(2*F)*.100**3/(48*h['Al_E_Pa']*endI)
    end_stress=((2*F)*.100/4)/(endI/(.010/2))
    root_leg=.003;throat=root_leg/sqrt(2);weld_L=2*(.014+.024)
    weld_I=throat*(2*.014*(.024/2)**2+2*.024**3/12)
    weld_bending=(F*span)*(.024/2)/weld_I;weld_shear=F/(weld_L*throat)
    # 200mm support pitch,120mm strip,6mm stepped plate; no credit to soft core.
    plate_I=.120*.006**3/12;plate_def=h['floor_point_force_N']*.2**3/(48*h['Al_E_Pa']*plate_I)
    plate_stress=(h['floor_point_force_N']*.2/4)/(.120*.006**2/6)
    return dict(post_cantrail_nominal_gap_m=postgap,post_gap_after_source_finish_fixture_m=postgap-source_and_new,
      source_gap_target_m=h['minimum_clearance_m'],side_stiffener=current,retained_failed_40mm_stiffener=previous,retained_failed_80mm_stiffener=failed80,
      side_stock_pass=current['stress_residual_Pa']>=0 and current['tip_deflection_m']<=h['deflection_m'],floor_support=floor,
      floor_plate_deflection_m=plate_def,floor_plate_stress_Pa=plate_stress,
      floor_root=dict(outer_hanger_reaction_N=2*F,outer_wing_load_N=F,overhang_m=Lwing,cap_thickness_m=.012,
        cap_wing_deflection_m=wing_def,cap_wing_stress_Pa=wing_stress,post_closure_deflection_m=end_def,post_closure_stress_Pa=end_stress,
        root_end_weld_leg_m=root_leg,root_end_weld_bending_Pa=weld_bending,root_end_weld_shear_Pa=weld_shear,
        root_end_weld_equivalent_Pa=sqrt(weld_bending**2+3*weld_shear**2),
        ideal_stock_deflection_sum_m=floor['tip_deflection_m']+plate_def+wing_def+end_def,
        model_domain='Ideal represented RHS/billet-upper12mm/closure stock only under unchanged500N point forces. Actual framewall,weld/slip/HAZ/localbearing and floor coupled loads remain unqualified; not installed acceptance'),
      floor_stock_pass=floor['stress_residual_Pa']>=0 and floor['tip_deflection_m']+plate_def+wing_def+end_def<=h['deflection_m'] and max(plate_stress,wing_stress,end_stress,sqrt(weld_bending**2+3*weld_shear**2))<=h['Al_stress_Pa'],
      deflection_allocation_domain='1mmideal-stock allocation for seal/closure support at1000Pa/500N hypotheses,not a universal body limit. Joint slip/rotation,source/finish errors and gasket compression remain additional budgets.',
      finished_side_panel_absY_with_bounds_m=1.322+source_and_new,
      body_halfwidth_m=r['fixed']['body_width_m']/2,geometry_screen_is_targeted_hypothesis=True,physical_accepted=False)


def combined_seal_budget(r,*,support_deflection_m,joint_slip_rotation_m=.0002):
    """Necessary positivecompression only; no supplier material strain approval."""
    h=r['hypotheses'];gap_error=support_deflection_m+joint_slip_rotation_m+2*h['flatness_m']+h['relative_fixture_position_m']
    free=.018;closed=.0144;free_error=.0003
    return dict(nominal_compression_m=free-closed,total_gap_error_m=gap_error,free_height_error_m=free_error,
      compression_interval_m=[free-free_error-closed-gap_error,free+free_error-closed+gap_error],
      positive_compression_bound=free-free_error>closed+gap_error,maximum_material_strain_limit=None,
      source_position_adjustment='Source survey/cut-to-fit before welding with positive trim/shim/fixture stock; achieved accuracy remains held',
      physical_accepted=False)


class Stock:
    """Owned discrete stock; signed bores/cuts are unioned upstream per member."""
    def __init__(self,r):self.r=r;self.entities=[];self.groups=[];self.joints=[];self.welds=[]
    def add(self,name,kind,size,at,material,*,R=I,wall=None,ri=0.,ro=None,net=None,gross=None,process=.05,qa=.03,scope='installed',holes=(),basis='New calculated gross stock/cut/process, no supplier quote'):
        _positive(size)
        g=dict(kind=kind,size_m=list(size))
        if kind=='rhs':g['wall_m']=wall;V=size[0]*(size[1]*size[2]-(size[1]-2*wall)*(size[2]-2*wall))
        elif kind=='annulus':g.update(outer_radius_m=ro,inner_radius_m=ri);V=pi*(ro*ro-ri*ri)*size[0]
        else:V=size[0]*size[1]*size[2]
        if holes:g['holes']=list(holes)
        def material_length(h):
            a=h['axis'];lo=h['centre_m'][a]-h['length_m']/2;hi=h['centre_m'][a]+h['length_m']/2
            overlap=lambda x,y:max(0.,min(hi,y)-max(lo,x))
            if kind=='rhs':
                if a==0:raise ValueError('Unsupported axialRHSdrill, explicit wall adapter required')
                return overlap(-size[a]/2,-size[a]/2+wall)+overlap(size[a]/2-wall,size[a]/2)
            return overlap(-size[a]/2,size[a]/2)
        rawV=V;removed=fsum(pi*h['radius_m']**2*material_length(h) for h in holes)
        V=V-removed if net is None else net
        if min(size)<=0 or V<=0:raise ValueError('Positive owned finished material required')
        # Positive edge/cut/trim/reserve stock, not an assumed reusable offcut.
        if gross is None:
            if kind=='box':
                a,b,t=sorted(size,reverse=True);gross=(a+.011)*(b+.004)*t
            else:gross=(size[0]+.011)*(rawV/size[0])
        if gross<V:raise ValueError('Net exceeds owned gross')
        mat=self.r['materials'][material];rho=_cases([mat['density_bounds_kg_m3'][0],mat['density_kg_m3'],mat['density_bounds_kg_m3'][1]])
        mass={c:V*rho[c] for c in CASES};cost={c:gross*rho[c]*mat['rate_USD_kg'][i]+(process+qa)*self.r['process']['labour_USD_h'][i] for i,c in enumerate(CASES)}
        # Uniform outer-box inertia is explicitly a proxy for complex/holed parts.
        a,b,c=size;S=[[(b*b+c*c)/12,0,0],[0,(a*a+c*c)/12,0],[0,0,(a*a+b*b)/12]]
        C=[-fsum(pi*h['radius_m']**2*material_length(h)*h['centre_m'][i] for h in holes)/V for i in range(3)]
        e=dict(id=name,part_id=FAMILY+'/'+name.split('/')[0],material_id=material,geometry=g,at_m=list(at),rotation=deepcopy(R),frame='terminal-local-UVW',scope=scope,
          functions=[name.split('/')[0]],mass_kg=mass,centroid_local_m=C,shape_I_per_kg=S,
          inertia_basis='Explicit uniform outer-box inertia bound/proxy; exact cut netmass, local hole centroid correction in machining ledger',mass_basis=basis,
          uncertainty_m=[self.r['hypotheses']['relative_fixture_position_m']]*3,cost_share=1.)
        self.entities.append(e);self.groups.append(dict(id='stock/'+name,entity_ids=[name],net_mass_kg=mass,gross_mass_kg={c:gross*rho[c] for c in CASES},
          scrap_mass_kg={c:(gross-V)*rho[c] for c in CASES},direct_cost_usd=cost,basis=basis,cost_basis='Gross material plus explicit process+QA only',
          net_m3=V,gross_m3=gross,scrap_m3=gross-V,drill_swarf_m3=removed,process_h=process,QA_h=qa,quantity=1,
          cutting=dict(kerf_m=.003,trim_m=.004,reserve_m=.004,plate_edge_m=.002)))
        return e
    def box(self,name,size,at,material='al5083',**kw):return self.add(name,'box',size,at,material,**kw)
    def rhs(self,name,L,w,h,t,at,material='al6005a',**kw):return self.add(name,'rhs',[L,w,h],at,material,wall=t,**kw)
    def ann(self,name,L,ro,ri,at,material='stainless',**kw):return self.add(name,'annulus',[L,2*ro,2*ro],at,material,ro=ro,ri=ri,**kw)
    def weld(self,name,L,at,leg=.003,*,axes=(0,),profile=None,in_groove=False,segments=None,process_h=.10,qa_h=.05):
        """Explicit centreline segments, positive deposited material and reserve.

        Triangle orientation/runout still needs drawing/CAD adaptation; the
        aggregate cut length is never used as a fictitious longitudinal solid.
        """
        paths=[]
        if segments is not None:
            paths=deepcopy(segments)
            if abs(fsum(sqrt(fsum((b[k]-a[k])**2 for k in range(3))) for a,b in paths)-L)>1e-9:raise ValueError('Weld path/length disagreement')
        elif profile is None:
            a=[0.,0.,0.];b=a.copy();a[axes[0]]=-L/2;b[axes[0]]=L/2;paths=[[a,b]]
        elif len(profile)==2:
            a,b=profile
            if abs(2*(a+b)-L)>1e-9:raise ValueError('Weld perimeter/length disagreement')
            pts=[]
            for x,y in ((-a/2,-b/2),(a/2,-b/2),(a/2,b/2),(-a/2,b/2)):
                p=[0.,0.,0.];p[axes[0]]=x;p[axes[1]]=y;pts.append(p)
            paths=[[pts[j],pts[(j+1)%4]] for j in range(4)]
        else:
            length,w,h=profile
            if abs(4*length-L)>1e-9:raise ValueError('Four-seam/length disagreement')
            paths=[[[-length/2,y*w/2,z*h/2],[length/2,y*w/2,z*h/2]] for y in (-1,1) for z in (-1,1)]
        lo=[min(p[i] for line in paths for p in line) for i in range(3)];hi=[max(p[i] for line in paths for p in line) for i in range(3)]
        centre=[(lo[i]+hi[i])/2 for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
        line_lengths=[sqrt(fsum((b[i]-a[i])**2 for i in range(3))) for a,b in paths]
        centroid=[fsum(length*(a[i]+b[i])/2 for (a,b),length in zip(paths,line_lengths))/L for i in range(3)]
        size=[max(leg,x+(0. if in_groove else 2*leg)) for x in size];V=.5*leg*leg*L
        e=self.add(name,'box',size,_add(at,centre),'al5083',net=V,gross=V*self.r['process']['weld_procurement_factor'],process=process_h,qa=qa_h,
          basis='Declared triangular depositedAlweld; separate positive filler/trim reserve, exact seam paths retained')
        e['centroid_local_m']=[centroid[i]-centre[i] for i in range(3)]
        localpaths=[[[p[i]-centre[i] for i in range(3)] for p in line] for line in paths]
        e['geometry']['kind']='envelope';e['physical_drawing']=dict(kind='triangular-weld-seams',local_segments_m=localpaths,leg_m=leg,
          in_prepared_grooves=in_groove,exact_triangle_orientation_and_runout_resolved=False)
        e['uncertainty_m']=[.0003]*3;e['centroid_model_uncertainty_m']=[leg]*3
        e['centroid_basis']='Length-weighted real seam centroid with explicit +/-leg cross-section model uncertainty; exact triangular orientation/runout requires normalizing adapter'
        self.welds.append(dict(id=name,length_m=L,leg_m=leg,volume_m3=V,at_uvw_m=list(at),local_segments_m=paths,
          centreline_centroid_from_station_m=centroid,process_h=process_h,QA_h=qa_h,
          geometry_scope='Exact centreline paths/deposited volume; triangle orientation/runout and WPS/HAZ remain explicit drawing/adapter qualification holds',WPS_HAZ_fatigue_qualified=False));return e
    def one_fastener_blank(self,name,ids,length,ro):
        selected=[g for g in self.groups if set(g['entity_ids'])&set(ids)]
        if {x for g in selected for x in g['entity_ids']}!=set(ids):raise ValueError('Fastener stock owner mismatch')
        es=[e for e in self.entities if e['id'] in ids];V=fsum(g['net_m3'] for g in selected);gross=pi*ro*ro*(length+.011)
        if gross<V:raise ValueError('Onepiecefastenerblank inadequate')
        material=es[0]['material_id'];mat=self.r['materials'][material];rho=_cases([mat['density_bounds_kg_m3'][0],mat['density_kg_m3'],mat['density_bounds_kg_m3'][1]])
        group=dict(id='stock/'+name,entity_ids=list(ids),net_m3=V,gross_m3=gross,scrap_m3=gross-V,
          net_mass_kg={c:fsum(e['mass_kg'][c] for e in es) for c in CASES},gross_mass_kg={c:gross*rho[c] for c in CASES},
          scrap_mass_kg={c:(gross-V)*rho[c] for c in CASES},direct_cost_usd={c:gross*rho[c]*mat['rate_USD_kg'][i]+.15*self.r['process']['labour_USD_h'][i] for i,c in enumerate(CASES)},
          basis='Oneproposed turned/threadedblank or onepurchasedfinishedallowance; split head/shank are analytical material entities,never separate purchases',
          cost_basis='Calculated oneblank/process/QA, no quotation; supplier shape/grade and alternate finished procurement remain unknown',quantity=1,
          cutting=dict(net_envelope_length_m=length,kerf_m=.003,trim_m=.004,reserve_m=.004))
        for e in es:e['cost_share']=e['mass_kg']['base']/group['net_mass_kg']['base']
        self.groups=[g for g in self.groups if g not in selected]+[group]
    def one_machined_blank(self,name,ids,size,process=.35,qa=.15):
        """One purchased blank owns every disjoint material piece exactly once."""
        selected=[g for g in self.groups if set(g['entity_ids'])&set(ids)]
        if {x for g in selected for x in g['entity_ids']}!=set(ids):raise ValueError('Machined blank ownership mismatch')
        es=[e for e in self.entities if e['id'] in ids]
        if len({e['material_id'] for e in es})!=1:raise ValueError('One blank cannot silently join dissimilar materials')
        V=fsum(g['net_m3'] for g in selected);a,b,t=sorted(size,reverse=True);gross=(a+.011)*(b+.004)*t
        if gross<=V:raise ValueError('Insufficient positive machined blank/scrap allowance')
        mat=self.r['materials'][es[0]['material_id']];rho=_cases([mat['density_bounds_kg_m3'][0],mat['density_kg_m3'],mat['density_bounds_kg_m3'][1]])
        group=dict(id='stock/'+name,quantity=1,entity_ids=list(ids),net_m3=V,gross_m3=gross,scrap_m3=gross-V,
          net_mass_kg={c:V*rho[c] for c in CASES},gross_mass_kg={c:gross*rho[c] for c in CASES},scrap_mass_kg={c:(gross-V)*rho[c] for c in CASES},
          direct_cost_usd={c:gross*rho[c]*mat['rate_USD_kg'][i]+(process+qa)*self.r['process']['labour_USD_h'][i] for i,c in enumerate(CASES)},
          blank_size_m=list(size),process_h=process,QA_h=qa,basis='One machined integral blank; separate analytical material regions are not separate purchases',
          cost_basis='Positive calculated material/process/QA hypothesis,not a supplier quote',cutting=dict(kerf_m=.003,trim_m=.004,reserve_m=.004,edge_m=.002))
        for e in es:e['cost_share']=e['mass_kg']['base']/group['net_mass_kg']['base']
        self.groups=[g for g in self.groups if g not in selected]+[group]
    def fabricated(self,e,cuts):
        g=next(x for x in self.groups if x['entity_ids']==[e['id']]);gross=fsum((L+.011)*(w+.004)*t for L,w,t in cuts)
        if gross<g['net_m3']:raise ValueError('Fabricated cut stock insufficient')
        mat=self.r['materials'][e['material_id']]
        for i,c in enumerate(CASES):
            rho=e['mass_kg'][c]/g['net_m3'];delta=gross*rho-g['gross_mass_kg'][c]
            g['gross_mass_kg'][c]=gross*rho;g['scrap_mass_kg'][c]=gross*rho-g['net_mass_kg'][c]
            g['direct_cost_usd'][c]+=delta*mat['rate_USD_kg'][i]
        g.update(gross_m3=gross,scrap_m3=gross-g['net_m3'],individual_plate_cuts_m=deepcopy(cuts),material_route='Fourcutplates plus separatelyowned weld filler,not presumedextrusion')
        #Four symmetric2mm corner bevels receive the separately counted filler.
        #Without this preparation, adding filler to an ideal fullRHS would
        #charge overlapping material twice. Exact seam solids need the adapter.
        loss=4*.5*.002**2*e['geometry']['size_m'][0];old=g['net_m3'];new=old-loss
        if new<=0:raise ValueError('Corner bevel consumes fabricated member')
        for c in CASES:
            rho=e['mass_kg'][c]/old;e['mass_kg'][c]=new*rho;g['net_mass_kg'][c]=new*rho;g['scrap_mass_kg'][c]=g['gross_mass_kg'][c]-new*rho
        g.update(net_m3=new,scrap_m3=gross-new,corner_bevel_removal_m3=loss)
        e['geometry']['corner_bevels']=dict(count=4,leg_m=.002,length_m=e['geometry']['size_m'][0],separately_owned_filler=True)


def _hole(axis,at,D,L):return dict(axis=axis,centre_m=list(at),radius_m=D/2,length_m=L)


def _fastener(s,name,axis,origin,sign,stack,diameter,*,head_height=.006,tip_guard=True):
    """Count every layer and derive poses from ordered planes."""
    R=I if axis==0 else YAXIS if axis==1 else ZAXIS
    def at(t):
        p=list(origin);p[axis]+=sign*t;return p
    L=stack['bolt_tip_m'];s.ann(name+'/bolt',L,diameter/2,0.,at(L/2),R=R)
    s.ann(name+'/head',head_height,diameter*.85,0.,at(-head_height/2),R=R)
    s.one_fastener_blank(name+'/onepiece-bolt',[name+'/bolt',name+'/head'],L+head_height,diameter*.85)
    nut_start,nut_end=stack['nut_m'];s.ann(name+'/nut',nut_end-nut_start,diameter*.92,diameter*.5,at((nut_start+nut_end)/2),R=R)
    for j,layer in enumerate(stack['layers']):
        text=layer['part'];t=layer['end_m']-layer['start_m'];mid=(layer['start_m']+layer['end_m'])/2
        if 'washer' in text:
            material='gfrp' if 'GFRP' in text else 'stainless'
            s.ann(name+'/washer/'+str(j),t,diameter*1.25,diameter*.55,at(mid),material,R=R)
    if tip_guard:s.ann(name+'/tip-guard',stack['projection_m']+.001,diameter*.8,diameter*.55,at(nut_end+(stack['projection_m']+.001)/2),'elastomer',R=R)
    s.joints.append(dict(id=name,kind='ordered-through-stack',axis=axis,origin_m=list(origin),direction=sign,stack=deepcopy(stack),supplier_geometry_grade_load_unknown=True))


def _blind_fastener(s,name,axis,origin,sign,j,diameter):
    """Owned blind thread with explicit pilot/web; no invisible nut or clamp."""
    grip=j['layers'][-1]['end_m'];engage=j['bolt_length_m']-grip
    if abs(engage-j['thread_engagement_m'])>1e-12 or engage<=0 or j['remaining_pilot_bound_m']<=0 or j['remaining_boss_web_m']<=0:
        raise ValueError('Blind fixing grip/pilot/web failure')
    R=I if axis==0 else YAXIS
    def at(t):
        p=list(origin);p[axis]+=sign*t;return p
    s.ann(name+'/shaft',j['bolt_length_m'],diameter/2,0.,at(j['bolt_length_m']/2),R=R)
    s.ann(name+'/head',diameter,diameter*.85,0.,at(-diameter/2),R=R)
    s.one_fastener_blank(name+'/onepiece',[name+'/shaft',name+'/head'],j['bolt_length_m']+diameter,diameter*.85)
    for k,x in enumerate(j['layers'][:2]):
        s.ann(name+'/washer/'+str(k),x['end_m']-x['start_m'],diameter*1.25,diameter*.55,at((x['start_m']+x['end_m'])/2),
          'stainless' if k==0 else 'gfrp',R=R)
    s.ann(name+'/liner',j['liner_length_m'],j['liner_OD_m']/2,j['liner_ID_m']/2,at(.0025+j['liner_length_m']/2),'gfrp',R=R)
    if 'liner_collar_t_m' in j:
        collar=j['liner_collar_from_underhead_m'];e=s.ann(name+'/liner-collar',j['liner_collar_t_m'],j['liner_collar_OD_m']/2,j['liner_ID_m']/2,at(sum(collar)/2),'gfrp',R=R)
        s.one_machined_blank(name+'/liner-kit',[name+'/liner',e['id']],[.011,.011,.0105],process=.12,qa=.08)
    s.joints.append(dict(id=name,kind=j['kind'],axis=axis,origin_m=list(origin),direction=sign,stack=deepcopy(j),
      tool=dict(insertion_m=.080 if diameter==.004 else .100,radius_m=.010 if diameter==.004 else .015),
      all_fixings_front_accessible=True,thread_compound_and_creep_qualified=False))


def upper_cage_stock(s,name,origin,sign):
    """One rigid, disjoint GFRP cage/hood blank, at an arbitrary joint origin."""
    d=upper_cage_contract()
    def at(v):
        p=list(origin);p[1]+=sign*v;return p
    hs=[_hole(1,[0.,0.,0.],.0085,.002)]
    for u in (-.013,.013):hs.extend([_hole(1,[u,sign*.0002,0.],.0062,.0016),_hole(1,[u,-sign*.0008,0.],.0034,.0004)])
    plate=s.box(name+'/plate',[.040,.002,.024],at(.0315),'gfrp',holes=hs)
    hood=s.ann(name+'/hood',.005,.0066,.00425,at(.035),'gfrp',R=YAXIS)
    cap=s.ann(name+'/closed-end',.001,.0066,0.,at(.038),'gfrp',R=YAXIS)
    s.one_machined_blank(name+'/integral-blank',[plate['id'],hood['id'],cap['id']],[.040,.024,.008],process=.45,qa=.20)
    s.joints.append(dict(id=name,kind='rigid nut-retaining cage/closed tip hood',origin_m=list(origin),direction=sign,contract=d,
      removal='Release existing two M3 cage retainers only after bolt unloading; withdraw/capture integral cage/hood. Main bolt is serviced from its other head; hood is not a socket-access opening.'))
    return d


def blind_panel_fixing(s,name,u,v,w):
    """One locallyproposed5.5mmoverall M4recessed screw, not a supplier claim."""
    sign=1 if v>0 else -1
    shaft=s.ann(name+'/shaft',.0031,.002,0.,[u,sign*1.31805,w],'stainless',R=YAXIS,process=.08,qa=.06)
    V=.0024*pi*(.002**2+.002*.00425+.00425**2)/3
    head=s.box(name+'/head-envelope',[.0085,.0024,.0085],[u,sign*1.3208,w],'stainless',net=V)
    head['geometry']['kind']='envelope';head['physical_drawing']=dict(kind='revolved-frustum',axis=1,small_radius_m=.002,large_radius_m=.00425,height_m=.0024,
      face_planes_absV_m=[1.3196,1.322],drive_geometry='Unselected supplier drive profile; bounded top drive/tool space,not native supplier head')
    s.one_fastener_blank(name+'/onepiece',[shaft['id'],head['id']],.0055,.0046)
    Viso=.0024*pi*((.00235**2+.00235*.0046+.0046**2)-(.002**2+.002*.00425+.00425**2))/3
    iso=s.box(name+'/GFRPcone-envelope',[.0092,.0024,.0092],[u,sign*1.3208,w],'gfrp',net=Viso)
    iso['geometry']['kind']='envelope';iso['physical_drawing']=dict(kind='nested-revolved-frusta',height_m=.0024,
      outer_radius_ends_m=[.00235,.0046],inner_radius_ends_m=[.002,.00425],compound_and_creep_qualified=False)
    s.joints.append(dict(id=name,kind='blind tapped removablepanel joint',overall_length_m=.0055,shaft_underhead_m=.0031,
      head_m=[1.3196,1.322],source_web_entry_m=1.3195,thread_tip_m=1.3165,thread_engagement_m=.003,
      pilot_bottom_m=1.316,remaining_pilot_m=.0005,source_web_inner_m=1.3155,remaining_web_m=.0005,
      combined_depth_length_tolerance_m=.0003,remaining_pilot_bound_m=.0002,tool_insertion_m=.080,tool_radius_m=.010,
      physical_geometry_adapter='Explicit frustum/profile required; envelopes are not finished supplier geometry',supplier_or_strength_qualified=False))


def _frustum(r0,r1,h):
    A=r0*r0+r0*r1+r1*r1;V=pi*h*A/3
    return V,h*(r0*r0+2*r0*r1+3*r1*r1)/(4*A)


def _remove_drawing_material(s,e,cuts,drawing):
    group=next(x for x in s.groups if x['entity_ids']==[e['id']]);oldV=group['net_m3'];loss=fsum(v for v,c in cuts);newV=oldV-loss
    if not 0<newV<oldV:raise ValueError('Invalid explicit contour removal')
    e['centroid_local_m']=[(oldV*e['centroid_local_m'][i]-fsum(v*c[i] for v,c in cuts))/newV for i in range(3)]
    for i,c in enumerate(CASES):
        rho=e['mass_kg'][c]/oldV;e['mass_kg'][c]=newV*rho;group['net_mass_kg'][c]=newV*rho;group['scrap_mass_kg'][c]=group['gross_mass_kg'][c]-newV*rho
        group['direct_cost_usd'][c]+=.10*len(cuts)*s.r['process']['labour_USD_h'][i]
    group.update(net_m3=newV,scrap_m3=group['gross_m3']-newV,contour_swarf_m3=loss)
    e['physical_drawing']=drawing;e['geometry']['kind']='envelope'
    e['inertia_basis']='Explicit contour-defined finished part; plain envelope inertia retained as bounded proxy,not filled material'


def added_stock(r):
    """Actual definition entry: do not call before a reviewed local request."""
    validate_fixed_recipe(r)
    b=necessary_bounds(r)
    if not b['side_stock_pass'] or not b['floor_stock_pass'] or b['post_gap_after_source_finish_fixture_m']<r['hypotheses']['minimum_clearance_m']:
        raise ValueError('Cheap necessary bound failed; revise source before trial')
    s=Stock(r);g=r['geometry'];h=r['hypotheses'];side=g['side'];floor=g['floor']
    # Detachable weather caps. Individual panels meet on separate counted lands;
    # they are not an added unowned span of the main compression gasket.
    s.box('fascia/central',[.002,2.45,.220],[.0785,0.,3.44-2.25],'al5754')
    s.box('roof/underlap',[.1775,2.43,.002],[-.01125,0.,3.547-2.25],'al5754')
    s.weld('roof/fascia-underlap-seam',2.43,[.0775,0.,3.547-2.25],leg=.0015,axes=(1,))
    s.box('roof/weather-strip',[.060,2.43,.002],[-.070,0.,3.549-2.25],'elastomer',process=.05,qa=.10)
    for j,v in enumerate((-1.,-.5,0.,.5,1.)):
        s.rhs(f'roof/standoff/{j}',.080,.030,.020,.003,[-.050,v,3.390-2.25],R=ZAXIS)
        s.rhs(f'roof/outrigger/{j}',.094,.030,.060,.003,[.007,v,3.400-2.25])
        s.weld(f'roof/standoff-weld/{j}',.100,[-.050,v,3.350-2.25],axes=(0,1),profile=(.020,.030))
        s.weld(f'roof/outrigger-weld/{j}',.180,[-.040,v,3.400-2.25],axes=(1,2),profile=(.030,.060))
    roof_holes=[_hole(1,[v,0.,0.],.0122,.020) for v in (-.95,-.45,.05,.55,1.05)]
    s.rhs('roof/fascia-stiffener',2.430,.020,.040,.002,[.064,0.,3.400-2.25],R=YAXIS,holes=roof_holes)
    roof_stack=ordered_stack('roof-M4',[('steel washer',.001),('GFRPwasher',.0005),('fascia',.002),('GFRPpad',.0035),
      ('RHS outerdepth',.020),('GFRPwasher',.001),('steel washer',.001)],.035,.0032,pitch=.0007)
    for j,v in enumerate((-.95,-.45,.05,.55,1.05)):
        s.box(f'roof/fascia-pad/{j}',[.0035,.040,.040],[.07575,v,3.400-2.25],'gfrp',holes=[_hole(0,[0.,0.,0.],.0122,.0035)])
        s.ann(f'roof/crush/{j}',.016,.004,.00225,[.064,v,3.400-2.25],'al5083')
        s.ann(f'roof/liner/{j}',.0255,.006,.0041,[.06675,v,3.400-2.25],'gfrp')
        _fastener(s,f'roof/M4/{j}',0,[.081,v,3.400-2.25],-1,roof_stack,.004,head_height=.004)
    for j,v in enumerate((-1.,-.5,0.,.5,1.)):
        s.weld(f'roof/outrigger-fascia-joint/{j}',.140,[.054,v,3.400-2.25],axes=(1,2),profile=(.030,.040))
    for side_sign in (-1,1):
        y=side_sign
        s.box(f'side/front/{y}',[.002,.097,2.400],[.075,y*1.2735,.10],'al5754',basis='100mmdeveloped side closure strip,97mmfinished metal and3mmtrim/setback to surveyed endbay outerface; no free gasket span')
        panel=s.box(f'side/endbay/{y}',[1.430,.002,2.150],[-.715,y*1.321,(1.15+3.30)/2-2.25],'al5754')
        s.box(f'side/top-flange/{y}',[1.430,.080,.002],[-.715,y*1.281,3.301-2.25],'al5754')
        s.box(f'side/top-seal/{y}',[1.430,.080,.003],[-.715,y*1.281,3.3035-2.25],'elastomer')
        s.box(f'side/sill-flange/{y}',[1.430,.080,.002],[-.715,y*1.245,1.113-2.25],'al5754')
        s.box(f'side/sill-seal/{y}',[1.430,.080,.0025],[-.715,y*1.245,1.11075-2.25],'elastomer')
        s.box(f'side/rear-lap-seal/{y}',[.030,.001,2.150],[-1.415,y*1.3195,(1.15+3.30)/2-2.25],'sealant')
        # Sidepost Uclamps: bolts alongX stay within the fixed lateral envelope.
        for row,z in enumerate(side['clamp_rows_Z_m']):
            for q,x in (('front',-.767),('rear',-.833)):
                s.box(f'post-clamp/{y}/{row}/{q}',[.004,.0705,.040],[x,y*1.28025,z-2.25],holes=[_hole(0,[0.,-y*.00525,0.],.0182,.004)])
                px=-.7695 if q=='front' else -.8305
                s.box(f'post-clamp/{y}/{row}/{q}-pad',[.001,.0705,.040],[px,y*1.28025,z-2.25],'gfrp',
                  holes=[_hole(0,[0.,-y*.00525,0.],.0182,.001)])
                s.weld(f'post-clamp/{y}/{row}/{q}-web-weld',.040,[x,y*1.3155,z-2.25],leg=.002,axes=(2,))
            webholes=[]
            for du in (-.020,.020):
                webholes.extend([_hole(1,[du,y*.0005,0.],.004,.003),_hole(1,[du,-y*.00125,0.],.0033,.0005)])
            s.box(f'post-clamp/{y}/{row}/outer-web',[.070,.004,.040],[-.800,y*1.3175,z-2.25],holes=webholes)
            s.box(f'post-clamp/{y}/{row}/outer-pad',[.060,.0005,.040],[-.800,y*1.31525,z-2.25],'gfrp')
            pad=s.box(f'post-clamp/{y}/{row}/panel-pad',[.070,.0005,.040],[-.800,y*1.31975,z-2.25],'gfrp')
            pcuts=[]
            for du in (-.020,.020):
                Vc,dc=_frustum(.00235,.002725,.0004);Vcyl=pi*.00235**2*.0001
                pcuts.extend([(Vc,[du,y*(1.3196+dc-1.31975),0.]),(Vcyl,[du,y*(1.31955-1.31975),0.])])
            _remove_drawing_material(s,pad,pcuts,dict(kind='box-minus-2revolvedcounterbores',axis=1,nominal_head_planes_absV_m=[1.3196,1.322],
              outer_cone_radius_ends_m=[.00235,.0046],height_m=.0024,thread_axis_U_m=[-.820,-.780]))
            s.ann(f'post-clamp/{y}/{row}/crush',.054,.007,.00325,[-.800,y*1.275,z-2.25],'al6005a')
            s.ann(f'post-clamp/{y}/{row}/liner',.070,.009,.0071,[-.800,y*1.275,z-2.25],'gfrp')
            _fastener(s,f'post-clamp/{y}/{row}/M6',0,[-.7625,y*1.275,z-2.25],-1,post_joint(),.006)
            for du in (-.020,.020):blind_panel_fixing(s,f'endbay-M4/{y}/{row}/{du}',-.800+du,y*1.321,z-2.25)
            for label,(a,c) in (('front',side['stiffener_front_X_m']),('rear',side['stiffener_rear_X_m'])):
                #12mm front endplate carries7.5mm blind M4 threads; all other
                #endplates4mm. No socket/nut is trapped inside the closed box.
                ft=.012 if label=='front' else .004;L=c-a-ft-.004;H=side['stiffener_YZ_m'][1]
                cu=-(a+ft+c-.004)/2
                e=s.rhs(f'side-stiffener/{y}/{row}/{label}',L,.020,H,.003,[cu,y*1.3095,z-2.25],'al5083')
                e['fabrication']=dict(route='FourdisjointAl5083plates buttassembled; no assumedavailable custom extrusion',cuts_m=[[L,.120,.003],[L,.120,.003],[L,.014,.003],[L,.014,.003]])
                s.fabricated(e,e['fabrication']['cuts_m'])
                s.weld(f'side-stiffener/{y}/{row}/{label}/long-seams',4*L,[cu,y*1.3095,z-2.25],leg=.002,profile=(L,.020,H),in_groove=True)
                for j,x in enumerate((a,c)):
                    t=ft if j==0 else .004;xx=x+(t/2 if j==0 else -t/2);hs=[]
                    if label=='front' and j==0:
                        for dz in (-.020,.020):
                            hs.extend([_hole(0,[t/2-.00375,0.,dz],.004,.0075),_hole(0,[t/2-.008,0.,dz],.0033,.001)])
                    s.box(f'side-stiffener/{y}/{row}/{label}/endplate{j}',[t,.020,H],[-xx,y*1.3095,z-2.25],holes=hs)
                    s.weld(f'side-stiffener/{y}/{row}/{label}/weld{j}',2*(.014+H-.006),[-(a+ft if j==0 else c-.004),y*1.3095,z-2.25],leg=.002,axes=(1,2),profile=(.014,H-.006),in_groove=True)
            for label,x in (('front',.763),('rear',.837)):
                s.box(f'side-stiffener/{y}/{row}/{label}/clamp-weld-tab',[.004,.003,.040],[-x,y*1.318,z-2.25])
                s.weld(f'side-stiffener/{y}/{row}/{label}/tab-weld',.080,[-x,y*1.318,z-2.25],leg=.002,
                  segments=tab_weld_segments(y),process_h=.20,qa_h=.10)
            s.box(f'side-outrigger/{y}/{row}',[.006,.111,.080],[-.103,y*1.2645,z-2.25],
              holes=[_hole(0,[0.,y*.045,dz],.0062,.006) for dz in (-.020,.020)])
            s.box(f'side-outrigger/{y}/{row}/isolation-pad',[.004,.020,.080],[-.108,y*1.3095,z-2.25],'gfrp',
              holes=[_hole(0,[0.,0.,dz],.0062,.004) for dz in (-.020,.020)])
            for k,dz in enumerate((-.020,.020)):
                _blind_fastener(s,f'side-frame/{y}/{row}/{k}/M4',0,[-.0975,y*1.3095,z+dz-2.25],-1,side_frame_joint(),.004)
            s.weld(f'side-outrigger/{y}/{row}/weld',.220,[-.100,y*1.215,z-2.25],axes=(0,2),profile=(.030,.080))
        cuts=[];locations=[]
        for z in side['clamp_rows_Z_m']:
            for du in (-.020,.020):
                Vc,dc=_frustum(.002725,.0046,.002);cu=-.800+du
                cuts.append((Vc,[cu+.715,y*(1.320+dc-1.321),z-(1.15+3.30)/2]));locations.append([cu,y*1.321,z-2.25])
        _remove_drawing_material(s,panel,cuts,dict(kind='box-minus-6revolvedcounterbores',axis=1,centres_uvw_m=locations,
          outer_cone_radius_ends_m=[.00235,.0046],height_m=.0024,finished_box_size_m=[1.430,.002,2.150],supplier_profile_qualified=False))
        # Two upperbolts per real cantrail; backer/retention installed before cap.
        for j,z in enumerate(g['upper']['cantrail_Z_stations_m']):
            s.box(f'upper/{y}/{j}/lug',[.070,.006,.060],[-.050,y*1.218,z-2.25],holes=[_hole(1,[0.,0.,0.],.0082,.006)])
            s.box(f'upper/{y}/{j}/spacer',[.040,.003,.040],[-.050,y*1.2225,z-2.25],holes=[_hole(1,[0.,0.,0.],.0082,.003)])
            s.box(f'upper/{y}/{j}/pad',[.040,.001,.040],[-.050,y*1.2245,z-2.25],'gfrp',holes=[_hole(1,[0.,0.,0.],.0082,.001)])
            bh=[_hole(1,[0.,0.,0.],.0082,.004)]
            for xx in (-.013,.013):bh.extend([_hole(1,[xx,y*.00045,0.],.003,.0031),_hole(1,[xx,-y*.0013,0.],.0025,.0004)])
            s.box(f'upper/{y}/{j}/backer',[.040,.004,.040],[-.050,y*1.2315,z-2.25],holes=bh)
            s.ann(f'upper/{y}/{j}/liner',.0185,.004,.00325,[-.050,y*1.22425,z-2.25],'gfrp',R=YAXIS)
            _fastener(s,f'upper/{y}/{j}/M6',1,[-.050,y*1.2115,z-2.25],y,upper_joint(),.006,tip_guard=False)
            upper_cage_stock(s,f'upper/{y}/{j}/captive-nut-cage',[-.050,y*1.2115,z-2.25],y)
            for xx in (-.013,.013):
                s.box(f'upper/{y}/{j}/cage-leg/{xx}',[.008,.0085,.020],[-.050+xx,y*1.23775,z-2.25],'gfrp',holes=[_hole(1,[0.,0.,0.],.0034,.0085)])
                s.ann(f'upper/{y}/{j}/cage-M3/{xx}',.012,.0015,0.,[-.050+xx,y*1.2364,z-2.25],'stainless',R=YAXIS,process=.05,qa=.04)
                s.ann(f'upper/{y}/{j}/cage-M3-head/{xx}',.0016,.00275,0.,[-.050+xx,y*1.2432,z-2.25],'stainless',R=YAXIS)
        tie=upper_liner_tie_stock(s,f'upper/{y}/frame-tie',y)
        s.box(f'upper/{y}/backbone',[.070,.006,.040],[-.050,y*1.218,3.440-2.25])
        # Thetie/lugs/backbone/cap stay with the body when these four/end
        #blind bolts are removed. No dissimilar metal weld or hidden nut.
        for k,u in enumerate((-.070,-.030)):
            s.box(f'upper-frame/{y}/{k}/boss',[.030,.020,.030],[u,y*1.201,3.270-2.25],
              holes=[_hole(1,[0.,y*(.010-.00625),0.],.006,.0125),_hole(1,[0.,y*(.010-.01325),0.],.005,.0015)])
            s.weld(f'upper-frame/{y}/{k}/boss-weld',.120,[u,y*1.211,3.270-2.25],leg=.002,axes=(0,2),profile=(.030,.030))
            _blind_fastener(s,f'upper-frame/{y}/{k}/M6',1,[u,y*1.2235,3.270-2.25],-y,upper_frame_joint(),.006)
        s.weld(f'upper/{y}/tie-lug-seams',.152,[-.050,y*1.218,3.360-2.25],leg=.002,axes=(0,1),profile=(.070,.006))
        for k,z in enumerate((3.420,3.460)):
            s.weld(f'upper/{y}/backbone-lug-seams/{k}',.152,[-.050,y*1.218,z-2.25],leg=.002,axes=(0,1),profile=(.070,.006))
        s.box(f'upper/{y}/cantrail-endcap',[.006,.099,.249],[.005,y*1.275,3.430-2.25])
        s.box(f'upper/{y}/cap-inner-arm',[.017,.006,.020],[-.0065,y*1.218,3.440-2.25])
        s.box(f'upper/{y}/cap-cross-arm',[.006,.0045,.020],[.005,y*1.22325,3.440-2.25])
        cap_connector_stock(s,f'upper/{y}/cap-connector-weld',[.002,y*1.221,3.440-2.25],y)
        s.weld(f'upper/{y}/cap-backbone-weld',.052,[-.015,y*1.218,3.440-2.25],leg=.002,axes=(1,2),profile=(.006,.020))
        for k,(dv,dz,w,h0) in enumerate(((0.,-.12275,.099,.0035),(0.,.12275,.099,.0035),(-.04775,0.,.0035,.242),(.04775,0.,.0035,.242))):
            s.box(f'upper/{y}/cap-seal/{k}',[.002,w,h0],[.001,y*1.275+dv,3.430-2.25+dz],'elastomer')
    # Stepped floorblank: its rear40mm is milled to2.75mm, paid6mm gross retained.
    W=floor['bridge_width_m'];net=W*(.120*.006+.040*.00275)
    floor_e=s.box('floor/stepped-cover',[.160,W,.006],[-.180,0.,1.147-2.25],'al5083',net=net,gross=(.171*(W+.004)*.006),process=1.5,qa=.5)
    floor_e['geometry']=dict(kind='poly-prism',size_m=[.160,W,.006],finished_profile_xz_m=[[-.080,.00025],[-.040,.00025],[-.040,-.003],[.080,-.003],[.080,.003],[-.080,.003]])
    floor_e['centroid_local_m']=[(.120*.006*.020+.040*.00275*(-.060))/(.120*.006+.040*.00275),0.,(.040*.00275*.001625)/(.120*.006+.040*.00275)]
    s.box('floor/lap-film',[.040,2.41,.00025],[-.240,0.,1.147125-2.25],'sealant')
    for y in (-1,1):post_bottom_stock(s,f'floor/post-bottom/{y}',y)
    for j,y in enumerate(floor['support_lanes_Y_m']):
        tube=s.rhs(f'floor/support/{j}',.116,.020,.030,.003,[-.158,y,1.129-2.25],'al5083',
          holes=[_hole(2,[.158-x,0.,.0135],.0045,.003) for x in (.14,.20)])
        tube['fabrication']=dict(route='Fourdisjoint5083plates; weld threadedbosses to upperplate BEFORE closing box; open tube ends prevent trappedweld pressure',
          cuts_m=[[.116,.030,.003],[.116,.030,.003],[.116,.014,.003],[.116,.014,.003]])
        s.fabricated(tube,tube['fabrication']['cuts_m'])
        s.weld(f'floor/support/{j}/long-seams',4*.116,[-.158,y,1.129-2.25],leg=.002,profile=(.116,.020,.030),in_groove=True)
        floor_tube_root_weld(s,f'floor/support/{j}/root-end-weld',y)
        if abs(y)<1.25:
            floor_root_stock(s,f'floor/hanger/{j}',y)
        for x in (.14,.20):
            s.box(f'floor/boss/{j}/{x}',[.020,.014,.006],[-x,y,1.138-2.25],holes=[_hole(2,[0.,0.,.000575],.004,.00485),_hole(2,[0.,0.,-.002175],.0033,.00065)])
            s.weld(f'floor/boss/{j}/{x}/weld',.068,[-x,y,1.141-2.25],leg=.002,axes=(0,1),profile=(.020,.014))
            s.ann(f'floor/cover-M4/{j}/{x}',.0112,.002,0.,[-x,y,1.14175-2.25],'stainless',R=ZAXIS,process=.08,qa=.05)
            s.ann(f'floor/cover-M4-head/{j}/{x}',.0024,.004,0.,[-x,y,1.1488-2.25],'stainless',R=ZAXIS)
            s.ann(f'floor/head-isolator/{j}/{x}',.00025,.0042,.00225,[-x,y,1.147475-2.25],'gfrp',R=ZAXIS)
    cover_holes=[]
    for y in floor['support_lanes_Y_m']:
        for x in (.14,.20):
            cover_holes.extend([_hole(2,[.18-x,y,.001675],.009,.00265),_hole(2,[.18-x,y,-.001325],.0045,.00335)])
    floor_e['geometry']['holes']=cover_holes
    loss=fsum(pi*x['radius_m']**2*x['length_m'] for x in cover_holes);newnet=net-loss
    oldC=floor_e['centroid_local_m'];floor_e['centroid_local_m']=[(net*oldC[i]-fsum(pi*x['radius_m']**2*x['length_m']*x['centre_m'][i] for x in cover_holes))/newnet for i in range(3)]
    fg=next(x for x in s.groups if x['id']=='stock/floor/stepped-cover')
    for i,c in enumerate(CASES):
        rho=floor_e['mass_kg'][c]/net;floor_e['mass_kg'][c]=newnet*rho;fg['net_mass_kg'][c]=newnet*rho
        fg['scrap_mass_kg'][c]=fg['gross_mass_kg'][c]-fg['net_mass_kg'][c];fg['direct_cost_usd'][c]+=len(cover_holes)*.03*r['process']['labour_USD_h'][i]
    fg.update(net_m3=newnet,scrap_m3=fg['gross_m3']-newnet,drill_swarf_m3=loss,process_h=fg['process_h']+len(cover_holes)*.03)
    # Sidefiller verticalstiffeners and inboard-access cover fixings, no bolt
    # protrudes beyond the fixed2.65m lateral envelope.
    for y in (-1,1):
        zs=(1.25,1.80,2.40,3.00,3.45)
        holes=[_hole(2,[z-2.35,0.,0.],.0122,.020) for z in zs]
        s.rhs(f'side-front-stiffener/{y}',2.400,.040,.020,.002,[.0605,y*1.275,.100],R=ZAXIS,holes=holes)
        for z in side['clamp_rows_Z_m']:
            s.box(f'side-front-root/{y}/{z}',[.1505,.070,.006],[-.02475,y*1.2845,z-2.25])
            s.weld(f'side-front-root/{y}/{z}/weld',.100,[-.100,y*1.3095,z-2.25],axes=(1,))
            s.weld(f'side-front-root/{y}/{z}/stiffener-weld',.092,[.0505,y*1.275,z-2.25],leg=.002,axes=(1,2),profile=(.040,.006))
        s.rhs(f'side-front-cap-root/{y}',.040,.040,.040,.003,[.0305,y*1.275,3.45-2.25],'al5083')
        s.weld(f'side-front-cap-root/{y}/stiffener-weld',.160,[.0505,y*1.275,3.45-2.25],leg=.002,axes=(1,2),profile=(.040,.040))
        #2.5mm nominal gap to body-owned cantrailcap; no weld to that cap.
        for j,z in enumerate(zs):
            s.box(f'side-front-pad/{y}/{j}',[.0035,.040,.040],[.07225,y*1.275,z-2.25],'gfrp',holes=[_hole(0,[0.,0.,0.],.0122,.0035)])
            s.ann(f'side-front-crush/{y}/{j}',.016,.004,.00225,[.0605,y*1.275,z-2.25],'al5083')
            s.ann(f'side-front-liner/{y}/{j}',.0255,.006,.0041,[.06325,y*1.275,z-2.25],'gfrp')
            _fastener(s,f'side-front-M4/{y}/{j}',0,[.0775,y*1.275,z-2.25],-1,roof_stack,.004,head_height=.004)
    return s


def source_key(cid,pid,index):return 'source/'+identity([cid,pid,index])


def source_dimension_contract(body,r):
    """Physical source dimensions, cross-checked against policy; no aliases.

    P1 names the width ``car_width_m`` in both records. The old terminal
    recipe's ``body_width_m`` is a consumer requirement, not a source key.
    Rates, evaluation settings and verification flags confer no dimensions or
    qualification. Already-applied source lift is ancestry, never a transform.
    """
    physical=body.get('physical_definition',{});layout=physical.get('layout')
    declared=body.get('policy',{}).get('layout');config=physical.get('config')
    if not all(isinstance(v,dict) for v in (layout,declared,config)):
        raise ValueError('Explicit physical layout/config and policy layout required')
    if r.get('units')!='m':raise ValueError('Source dimension contract uses explicit metres')
    expected=dict(cars=r['fixed']['cars'],car_length_m=r['fixed']['car_length_m'],
        car_width_m=r['fixed']['body_width_m'],intercar_gap_m=.65,
        floor_top_m=r['fixed']['floor_Z_m'],roof_z_m=r['fixed']['roof_skin_bottom_Z_m'],gauge_m=1.435)
    for key,wanted in expected.items():
        if key not in layout or key not in declared:
            raise ValueError('Missing exact physical/policy source field: '+key)
        values=[layout[key],declared[key]]
        if any(type(v) not in (int,float) or not isfinite(v) for v in values):
            raise ValueError('Finite nonboolean source dimension required: '+key)
        if key=='cars' and any(type(v) is not int for v in values):
            raise ValueError('Integer physical/policy source car count required')
        if values[0]!=values[1] or any(abs(v-wanted)>1e-10 for v in values):
            raise ValueError('Physical/policy source dimension disagreement: '+key)
    if abs(layout['car_length_m']+layout['intercar_gap_m']-r['fixed']['formation_pitch_m'])>1e-10 or abs(layout['cars']*layout['car_length_m']+(layout['cars']-1)*layout['intercar_gap_m']-r['fixed']['train_structural_length_m'])>1e-10:
        raise ValueError('Source formation/datum differs from terminal binding')
    lift=config.get('body_lift_m')
    if type(lift) not in (int,float) or not isfinite(lift) or abs(lift-r['fixed']['body_lift_already_applied_m'])>1e-10:
        raise ValueError('Explicit already-applied physical source lift required')
    track=physical.get('track_interface');policy_track=body.get('policy',{}).get('track_interface')
    if not isinstance(track,dict) or not isinstance(policy_track,dict):raise ValueError('Explicit physical/policy track datums required')
    required=dict(schema='osr-wheel-rail-interface/1',inner_face_gauge_m=1.435,
        nominal_contact_centres_y_m=[-.7525,.7525],nominal_rail_head_width_m=.070,contact_datum='nominal rail head centres')
    for key,wanted in required.items():
        for actual in (track,policy_track):
            if key not in actual or actual[key]!=wanted:raise ValueError('Physical/policy track datum differs: '+key)
            if isinstance(wanted,(int,float)) and type(actual[key]) not in (int,float):raise ValueError('Nonboolean SI track datum required')
            if isinstance(wanted,list) and any(type(v) not in (int,float) or not isfinite(v) for v in actual[key]):raise ValueError('Finite SI contact datums required')
    return dict(schema='osr-terminal-source-dimension-contract/1',physical_layout_fields={k:layout[k] for k in expected},
        authoritative_source_paths={k:'physical_definition.layout.'+k for k in expected},
        declared_crosscheck_paths={k:'policy.layout.'+k for k in expected},
        physical_field_binding_id=identity(dict(layout={k:layout[k] for k in expected},track=required,body_lift_already_applied_m=lift)),
        geometry_lift_to_apply_m=0.,verification_flags_are_not_qualification=True,physical_accepted=False)


def source_occurrences(body,part_id):
    parts={p['id']:p for p in body['parts']};p=parts[part_id];out=[]
    if len(parts)!=len(body['parts']):raise ValueError('Duplicate source part identity')
    physical=body['physical_definition']
    source_parts=[x for x in physical.get('parts',[]) if x['id']==part_id]
    part_keys=('component_definition_id','id','mass_each_kg','material_id','quantity_per_train','source_part_id','stock')
    if len(source_parts)!=1 or any(k not in p for k in part_keys) or source_parts[0]!={k:p[k] for k in part_keys}:
        raise ValueError('Source section/material/quantity differs from physical part identity')
    patterns={x['id']:x for x in physical.get('occurrence_patterns',[])}
    if len(patterns)!=len(physical.get('occurrence_patterns',[])):raise ValueError('Duplicate physical occurrence pattern')
    pattern_keys=('bogie_index','car_allocation','count','geometry','id','part_id','positions_m','rotation')
    for pat in body['patterns']:
        if pat['part_id']!=part_id:continue
        if any(k not in pat for k in pattern_keys) or patterns.get(pat['id'])!={k:pat[k] for k in pattern_keys}:
            raise ValueError('Source pattern geometry/placement differs from physical identity')
        if type(pat['count']) is not int or pat['count']!=len(pat['positions_m']):raise ValueError('Source count/pose differs')
        if any(len(at)!=3 or any(type(v) not in (int,float) or not isfinite(v) for v in at) for at in pat['positions_m']):raise ValueError('Finite nonboolean source positions required')
        for j,at in enumerate(pat['positions_m']):
            out.append(dict(id=source_key(body['candidate_id'],pat['id'],j),part_id=part_id,part=p,
              pattern_id=pat['id'],position_index=j,at_m=at,rotation=pat['rotation'],car_allocation=pat['car_allocation'],
              source_pattern_sha256=identity(pat),source_part_sha256=identity(p)))
    if len(out)!=p['quantity_per_train']:raise ValueError('Source ownership count differs')
    return out


def counterpart_map(body,r):
    """Actual source poses/sections, never coupon length or a reflected copy."""
    _sealed(body)
    if body['candidate_id']!=r['parent']['candidate_id'] or body['evaluation_id']!=r['parent']['evaluation_id'] or identity(body['physical_definition'])!=body['candidate_id']:
        raise ValueError('Exact source parent required')
    source_dimension_contract(body,r)
    sets={p:source_occurrences(body,p) for p in ('body/end-beam','body/cantrail','body/side-post')}
    expected={'body/end-beam':dict(kind='rhs',length_m=2.29,width_m=.14,depth_m=.25,wall_m=.008),
      'body/cantrail':dict(kind='rhs',length_m=17.,width_m=.10,depth_m=.25,wall_m=.0045),
      'body/side-post':dict(kind='rhs',length_m=2.35,width_m=.06,depth_m=.08,wall_m=.003)}
    out=[]
    for binding in r['bindings']:
        at=binding['at_m'];R=binding['rotation'];car=binding['car']
        for pid,rows in sets.items():
            for row in rows:
                if row['car_allocation']!=[[car,1.]]:continue
                local=inverse(row['at_m'],at,R)
                relevant=abs(local[0]+.1)<1e-8 if pid=='body/end-beam' else abs(local[0]+8.5)<1e-8 if pid=='body/cantrail' else abs(local[0]+.8)<1e-8
                if not relevant:continue
                if row['part']['stock']!=expected[pid] or row['part']['material_id']!='body/al6005a':
                    raise ValueError('Actual source counterpart section/material differs: '+pid)
                expected_R=YAXIS if pid=='body/end-beam' else I if pid=='body/cantrail' else [[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
                if row['rotation']!=expected_R or any(type(v) not in (int,float) or not isfinite(v) for rr in row['rotation'] for v in rr):raise ValueError('Actual source counterpart proper rotation differs')
                target=([-.1,0.,-1.2655] if pid=='body/end-beam' else [-8.5,(-1 if local[1]<0 else 1)*1.275,1.18] if pid=='body/cantrail' else [-.8,(-1 if local[1]<0 else 1)*1.275,.075])
                if any(abs(a-b)>1e-8 for a,b in zip(local,target)):raise ValueError('Actual source counterpart full placement/datum differs')
                out.append(dict(row,terminal_id=binding['id'],binding=binding,local_center_m=local))
    if len(out)!=10 or len({x['id'] for x in out})!=10:raise ValueError('Exactly2beams+4cantrails+4firstposts required')
    return out


def source_machining(counterparts,r):
    """One paid source owner/member;64wall operations including32beam holes."""
    groups=[]
    for cp in counterparts:
        pid=cp['part_id'];b=cp['binding'];sign=1 if cp['local_center_m'][1]>0 else -1;cuts=[]
        if pid=='body/end-beam':
            for v in r['geometry']['lower']['mount_v_m']:
                cuts.extend([(0,[-.166,v,-1.18],.0182,.008),(0,[-.034,v,-1.18],.0085,.008)])
        elif pid=='body/cantrail':
            for z in r['geometry']['upper']['cantrail_Z_stations_m']:
                cuts.append((1,[-.05,sign*1.22725,z-2.25],.0082,.0045))
        else:
            for z in r['geometry']['side']['clamp_rows_Z_m']:
                cuts.extend([(0,[-.8285,sign*1.275,z-2.25],.0182,.003),(0,[-.7715,sign*1.275,z-2.25],.0182,.003)])
        operations=[]
        for j,(axis,p,D,L) in enumerate(cuts):
            wp=transform(p,b['at_m'],b['rotation']);local=inverse(wp,cp['at_m'],cp['rotation'])
            direction=[b['rotation'][i][axis] for i in range(3)];intrinsic=[fsum(cp['rotation'][i][k]*direction[i] for i in range(3)) for k in range(3)]
            a=next((k for k,x in enumerate(intrinsic) if abs(abs(x)-1.)<1e-10),None)
            if a is None:raise ValueError('Unsupported source bore axis')
            V=pi*(D/2)**2*L
            ss=cp['part']['stock'];dims=[ss['length_m'],ss['width_m'],ss['depth_m']];t=ss['wall_m']
            if a not in (1,2) or abs(abs(local[a])-(dims[a]/2-t/2))>1e-8 or abs(L-t)>1e-12:
                raise ValueError('Source bore does not bind one real RHSwall')
            edges=[dims[k]/2-abs(local[k])-D/2 for k in range(3) if k!=a]
            if min(edges)<=0:raise ValueError('Bore exits actual source stock edge')
            operations.append(dict(id=cp['id']+'/wall-bore/'+str(j),source_id=cp['id'],axis=a,centre_m=local,radius_m=D/2,length_m=L,
              centre_world_m=wp,removed_volume_m3=V,material='body/al6005a',source_stock_retained=True,nominal_minimum_edge_ligament_m=min(edges),edge_strength_qualified=False))
        # No duplicate / crossing loss can be hidden in a summed subtraction.
        for i,a in enumerate(operations):
            for d in operations[i+1:]:
                if a['axis']==d['axis']:
                    axis=a['axis'];radial=sqrt(fsum((a['centre_m'][k]-d['centre_m'][k])**2 for k in range(3) if k!=axis))
                    if radial<a['radius_m']+d['radius_m'] and abs(a['centre_m'][axis]-d['centre_m'][axis])<(a['length_m']+d['length_m'])/2:
                        raise ValueError('Overlapping source bores need union adapter')
        stock=cp['part']['stock'];Vstock=stock['length_m']*(stock['width_m']*stock['depth_m']-(stock['width_m']-2*stock['wall_m'])*(stock['depth_m']-2*stock['wall_m']))
        loss=fsum(x['removed_volume_m3'] for x in operations)
        if not 0<loss<Vstock:raise ValueError('Invalid retained source net removal')
        rho={c:cp['part']['mass_each_kg'][c]/Vstock for c in CASES}
        removed={c:loss*rho[c] for c in CASES}
        moment={c:[fsum(x['removed_volume_m3']*rho[c]*x['centre_world_m'][k] for x in operations) for k in range(3)] for c in CASES}
        C=[(Vstock*cp['at_m'][k]-fsum(x['removed_volume_m3']*x['centre_world_m'][k] for x in operations))/(Vstock-loss) for k in range(3)]
        groups.append(dict(source_id=cp['id'],source_part_id=pid,source_pattern_id=cp['pattern_id'],source_position_index=cp['position_index'],
          source_pattern_sha256=cp['source_pattern_sha256'],source_part_sha256=cp['source_part_sha256'],terminal_id=cp['terminal_id'],
          kind='machine_in_place',operations=operations,gross_paid_source_retained=True,removed_material_m3=loss,
          removed_mass_kg=removed,removed_moment_kg_m=moment,remaining_mass_kg={c:cp['part']['mass_each_kg'][c]-removed[c] for c in CASES},
          remaining_centroid_world_m=C,remaining_geometry=dict(kind='rhs',size_m=[stock['length_m'],stock['width_m'],stock['depth_m']],wall_m=stock['wall_m'],
            holes=[{k:x[k] for k in ('axis','centre_m','radius_m','length_m')} for x in operations]),at_m=cp['at_m'],rotation=cp['rotation'],car_allocation=cp['car_allocation'],
          paid_source_cost_usd=deepcopy(cp['part']['direct_cost_each_usd']),additional_process_USD={c:len(operations)*.05*r['process']['labour_USD_h'][i] for i,c in enumerate(CASES)},
          density_basis='Effective source allowance density for proportional removal, not measured material or an installed saving',
          hole_QA='Survey actual source position/wall/old bores first; fixture and drill from accessible face; capture swarf; inspect diameter/location and coating repair'))
    return groups


def revise_local(local,r):
    """New physical ancestry; retain the390-entity input unchanged."""
    out=deepcopy(local['entities'])
    for e in out:
        g=e.get('geometry');name=e['id']
        if name=='source-body-end-beam':e['scope']='context';continue
        if name.startswith('post/'):
            sign=1 if g['at_m'][1]>0 else -1;g['at_m'][1]=sign*r['geometry']['fixed_post_absV_m']
            g['size_m'][0]-=.010;g['at_m'][2]+=.005
            for h in e.get('holes',[]):
                if 'vent' in h.get('purpose',''):h['at_m'][1]-=sign*.010
            e.setdefault('holes',[]).extend(dict(kind='cylinder-cut',diameter_m=.0082,length_m=.004,
              at_m=[u,sign*1.213,1.020],axis=[0.,float(sign),0.],purpose='owned detachable upper-frame bore,outer postwall only') for u in (-.070,-.030))
        if name in ('header/0','lower-rail/0'):
            g['size_m'][0]=r['geometry']['header_lower_length_m']
            for h in e.get('holes',[]):
                if 'vent' in h.get('purpose',''):h['at_m'][1]=(.965 if h['at_m'][1]>0 else -.965)
        if name=='frame-land-ring':
            e['additional_voids']=[dict(kind='box',size_m=[.006,.010,.150],at_m=[.003,s*1.220,1.025],rotation=I) for s in (-1,1)]
        e['old_entity_sha256']=identity(next(x for x in local['entities'] if x['id']==name))
    return out


def _raw_bounds(g):
    if g['kind']=='difference':return _raw_bounds(g['outer'])
    if g['kind']=='union-material':
        bs=[_raw_bounds(x) for x in g['pieces']];return [[min(x[0][i] for x in bs) for i in range(3)],[max(x[1][i] for x in bs) for i in range(3)]]
    if g['kind']=='annulus':size=[g['length_m'],g['outer_diameter_m'],g['outer_diameter_m']]
    elif g['kind']=='profile-prism':
        pts=[[s*g['length_m']/2,*p] for s in (-1,1) for p in g['points_yz_m']]
        pts=[transform(x,g['at_m'],g['rotation']) for x in pts]
        return [[min(x[i] for x in pts) for i in range(3)],[max(x[i] for x in pts) for i in range(3)]]
    else:size=g['size_m']
    half=[fsum(abs(g['rotation'][i][j])*size[j] for j in range(3))/2 for i in range(3)]
    return [[g['at_m'][i]-half[i] for i in range(3)],[g['at_m'][i]+half[i] for i in range(3)]]


def _unknown_envelope(e):
    """Explicit proposed packaging bounds, never recovered supplier CAD."""
    name=e['id'];at=e.get('required_interface_uvw_m',[0.,0.,0.])
    if 'washer' in name:size=[.003,.024,.024]
    elif 'nut' in name:size=[.010,.022,.022]
    elif 'guard' in name:size=[.018,.020,.020]
    elif 'glazing' in name and any(t in name for t in ('seal','retainer','bond')):size=[.025,1.66,1.16];at=[.069,0.,0.]
    elif 'insert' in name:size=[.012,.016,.016]
    else:size=[.060,.024,.024]
    return dict(kind='envelope',size_m=size),at,'Proposed maximum packaging hypothesis; supplier profile/grade/fit unknown, not a finished solid'


def _legacy_geometry(e):
    """Preserve exact source CSG alongside a bounded plain component envelope.

    CSG to primitive/net-inertia conversion remains explicit adapter work; no
    supplier geometry or filled material is inferred from this envelope.
    """
    g=e.get('geometry')
    if g is None:return _unknown_envelope(e)
    bb=_raw_bounds(g);size=[bb[1][i]-bb[0][i] for i in range(3)];at=[(bb[0][i]+bb[1][i])/2 for i in range(3)]
    return dict(kind='envelope',size_m=size),at,'Known source CSG retained separately; plain-envelope inertia/clearance proxy only'


def component_export(legacy,added,account,r,*,retained_source_parts=None):
    """Local typed draft with complete positive stock ownership and CSG ancestry.

    Known exact CSG is not erased: it remains the physical definition and CAD
    source. The plain component exposes conservative packaging/proxy inertia;
    unsupported fitted joint schemas explicitly prevent automatic composition.
    """
    rows={x['part_id']:x for x in account['rows']};es=[];groups=[];by={}
    for e in legacy:
        if e['id']=='source-body-end-beam':continue
        by.setdefault(e['part_id'],[]).append(e)
    for pid,members in by.items():
        row=rows[pid];mass=_cases(row['mass_kg']);cost=_cases(row['direct_usd']);q=len(members)
        if q!=row['quantity']:raise ValueError('Local source part/physical count differs')
        if min(mass.values())<=0:raise ValueError('Unknown legacy mass cannot become zero')
        if retained_source_parts is not None and pid in retained_source_parts:
            source=retained_source_parts[pid];mass={c:q*source['mass_each_kg'][c] for c in CASES};cost={c:q*source['direct_cost_each_usd'][c] for c in CASES}
        deltaV=0.
        if pid.endswith(('/header','/lower-rail')):deltaV=-.020*(.100*.100-.092*.092)
        if pid.endswith('/frame-land-ring'):deltaV=-2*.006*.010*.150
        post_group=any(e['id'].startswith('post/') for e in members)
        if post_group:deltaV=-2*pi*(.0082/2)**2*.004-.010*(.100*.100-.092*.092)
        source_net=row.get('net_volume_interval_each_m3')
        if source_net:
            lo,hi=source_net;volumes=[lo,(lo+hi)/2,hi]
            density=_cases(row['density_cases_kg_m3'])
            mass={c:mass[c]+deltaV*q*density[c] for c in CASES}
            grossmass={c:row['gross_each_m3']*q*density[c] for c in CASES}
            scrap={c:grossmass[c]-mass[c] for c in CASES}
            if min(mass.values())<=0 or min(scrap.values())<0:raise ValueError('Revised local stock inadequate; newgross required')
        else:
            grossmass=deepcopy(mass);scrap=_cases(0.)
        if deltaV:
            cost={c:cost[c]+(.25+(.15 if post_group else 0.))*r['process']['labour_USD_h'][i] for i,c in enumerate(CASES)}
        ids=[]
        for x in members:
            g,at,basis=_legacy_geometry(x);a,b,c=g['size_m'];name='legacy/'+x['id'];ids.append(name)
            es.append(dict(id=name,part_id=pid,material_id=x.get('material','retained-unselected-source-material'),geometry=g,at_m=at,rotation=I,frame='terminal-local-UVW',scope='installed',
              functions=[pid],mass_kg={k:mass[k]/q for k in CASES},centroid_local_m=[0.,0.,0.],
              shape_I_per_kg=[[(b*b+c*c)/12,0.,0.],[0.,(a*a+c*c)/12,0.],[0.,0.,(a*a+b*b)/12]],
              inertia_basis=basis,mass_basis='Retained authenticated local part-account interval, not derived from an envelope',
              uncertainty_m=[.020]*3,cost_share=1/q,exact_CSG_entity=x,unknown_finished_geometry=x.get('geometry') is None))
        # Existing finished estimated price is carried once. No second raw price.
        groups.append(dict(id='legacy-account/'+pid,entity_ids=ids,net_mass_kg=mass,gross_mass_kg=grossmass,scrap_mass_kg=scrap,direct_cost_usd=cost,
          basis='Source complete estimated part-group allowance retained once; raw cut/scrap intervals remain in source_account, not fabricated zero loss',
          cost_basis='Authenticated local finished direct allowance once, no added raw-material charge or discount',source_account=deepcopy(row),
          revised_net_material_delta_m3=deltaV*q,
          additional_post_cut=dict(length_m=.010,section_area_m2=.100*.100-.092*.092,cut_centroid_w_m=-1.095,
            cut_first_moment_per_member_uw_m4=[-.010*(.100*.100-.092*.092)*(-.050),-.010*(.100*.100-.092*.092)*(-1.095)],
            true_CSG_centroid_adapter_required=True) if post_group else None,
          procurement_scope='Known stock uses exact retained gross/cut source; purchased rows use finished-item gross=installed mass,no raw scrap claimed. Packaging/spares remain separate unknowns,not zero allocations.'))
    es.extend(added.entities);groups.extend(added.groups)
    out=dict(schema='osr-terminal-component-proposal/1',target_schema='osr-composition-component/1',units='m',quantity_scope='one terminal-local module; install once at each of the two explicit proper bindings,never as already global body coordinates',
      local_axes=['u outward','v lateral','w up'],required_bindings=deepcopy(r['bindings']),entities=es,stock_groups=groups,physical_interfaces=[],required_counterpart_ids=[],
      actual_joint_contracts=deepcopy(added.joints),source_csg_and_unknown_preserved=True,
      unsupported_counterpart_schemas=['osr-stepped-RHS-bearing-sleeve/1','osr-one-wall-backed-liner/1','terminal glazing retention/blind insert supplier profile'],
      composition_admitted=False,capability_hold='A reviewed exact CSG/joint/consumable/canonical ownership adapter is still required; this draft does not claim final installed fit.')
    out['definition_id']=identity(dict(entities=[{k:e[k] for k in ('id','part_id','material_id','geometry','at_m','rotation','frame','functions')} for e in es],
      exact_legacy=[dict(id=e['id'],geometry=e.get('geometry'),holes=e.get('holes'),additional_voids=e.get('additional_voids')) for e in legacy],
      added_drawings=[dict(id=e['id'],drawing=e.get('physical_drawing')) for e in added.entities if e.get('physical_drawing')],joints=added.joints))
    return seal(out)


def consumable_accounting(added,account,r):
    """Separate source baseline residual and positive newfinish/sealant scope."""
    area=0.
    for e in added.entities:
        if e['material_id'] not in ('al5083','al6005a','al5754'):continue
        a,b,c=e['geometry']['size_m'];area+=2*(a*b+a*c+b*c)+e.get('additional_finish_surface_reference_m2',0.)
    # The declared upper/lower/side laps have finite supported lengths; material
    # volumes are source allowances and remain separate from directpart prices.
    finishV=area*r['hypotheses']['finish_m'];sealV=(2*2.4+2*1.43+2.43)*.020*.00025
    new_mass={};new_cost={};legacy_residual={}
    rowcost={c:fsum(_cases(x['direct_usd'])[c] for x in account['rows']) for c in CASES}
    for i,c in enumerate(CASES):
        coatfactor=(.5,.8,1.15)[i];rhoCoat=r['materials']['coating']['density_kg_m3'];rhoSeal=r['materials']['sealant']['density_kg_m3']
        #Local32P1bore edge repair/end and captured fitting-shim allowance are
        #positive separately owned consumables,never anonymous zero reserves.
        repairV=32*.020*.020*r['hypotheses']['finish_m']
        new_mass[c]=finishV*coatfactor*rhoCoat+sealV*rhoSeal+repairV*rhoCoat+r['fitted_weather_interfaces']['shim_pack_mass_kg'][i]
        new_cost[c]=finishV*coatfactor*rhoCoat*r['materials']['coating']['rate_USD_kg'][i]*1.2+sealV*rhoSeal*r['materials']['sealant']['rate_USD_kg'][i]*1.5+repairV*rhoCoat*r['materials']['coating']['rate_USD_kg'][i]*1.2+r['fitted_weather_interfaces']['shim_pack_cost_USD'][i]
        legacy_residual[c]=account['totals'][c]['local_direct_scope_usd']-rowcost[c]
        if min(new_mass[c],new_cost[c])<=0 or legacy_residual[c]<0:raise ValueError('Consumable/process coverage inconsistent')
    return dict(quantity_scope='per terminal end except the one train workshop fixture; retained-source machining ledger separately covers two ends once',legacy_consumables=deepcopy(account['consumables']),legacy_process_consumable_overhead_residual_USD=legacy_residual,
      residual_basis='Authenticated legacy local_directscope minus its complete row prices; preserves consumable/process/overhead once, no secondmaterial charge',
      new_finish_surface_reference_m2=area,new_finish_volume_reference_m3=finishV,new_sealant_volume_m3=sealV,
      new_installed_mass_kg=new_mass,new_procurement_cost_USD=new_cost,
      fitting_shims=dict(mass_kg=r['fitted_weather_interfaces']['shim_pack_mass_kg'],cost_USD=r['fitted_weather_interfaces']['shim_pack_cost_USD'],basis='Separate captured source fitting reserve; actual shim geometry must be resolved before composition,not physical acceptance'),
      source_bore_repair_volume_m3=32*.020*.020*r['hypotheses']['finish_m'],
      mask='Precision seal/stop/sleeve bearing surfaces uncoated; corrosion compound at stainless/Althreads and repaired source holes is unqualified but positive counted coverage',
      coat_chemistry_fire_creep_qualified=False,exact_coated_area_known=False,
      shared_extractor=dict(upper_liner_removal_contract()['workshop_extractor'],
        net_mass_kg={c:upper_liner_removal_contract()['workshop_extractor']['net_volume_m3']*rho for c,rho in zip(CASES,[7760.,8000.,8240.])},
        gross_cost_USD={c:upper_liner_removal_contract()['workshop_extractor']['gross_volume_m3']*rho*r['materials']['stainless']['rate_USD_kg'][i]+(upper_liner_removal_contract()['workshop_extractor']['process_h']+upper_liner_removal_contract()['workshop_extractor']['QA_h'])*r['process']['labour_USD_h'][i] for i,(c,rho) in enumerate(zip(CASES,[7760.,8000.,8240.]))}),
      shared_fixture=dict(quantity=1,installed=False,mass_bounds_kg=r['process']['shared_fixture_mass_kg'],cost_bounds_USD=r['process']['shared_fixture_cost_USD']))


def assembly_plan(r):
    return dict(sequence=[
      'Survey exact terminal beam,cantrail,firstpost,roof/floor surfaces; verify source identity/walls and existing bores before cutting',
      'Machine32terminal beam wall bores plus8cantrail/24sidepostwall bores using supported jigs; capture swarf,deburr,inspect and repair finish',
      'Fabricate revised frame with10mm post setback,shorterheader/lowerrail and150mm uppercorner reliefs; shorten postbottoms10mm for counted closureplates,topunchanged; weld internal upperblind bosses before closing post; weld solid billet hangers below frame; install roof standoffs; weld AltoAl only',
      'Fit each116mm floorRHS end to the real hanger face atU-.100,Z1.114..1.144; apply counted internal endseams through the open longitudinalwall before closing the fabricated tube; install threaded bosses then close remaining wall',
      'Face/lap existing seal/stop lands after welding; verify all24station datums against declared hypotheses,not assumed achieved accuracy',
      'Fit lower M8sets,upperM6backers/liners/captive cages and sidepost Uclamps before weathercapsclose the accessible source tube ends',
      'Install side stiffeners/endbay panels and steppedfloorplate with shared wear-layer recess mapping; source body stock is owned once',
      'Support panel/glass,fit retained source hardware once,close on limiters; install removablefascia/sidereturns/roofunderlap and weatherstrips last'],
      maintenance=[
        'Support exterior covers; release counted weather fixings,remove fascia/sidefront fillers and underlap before any main panel motion',
        'Fit rated glass/panel support; remove/capture24M6clamps,washers,nuts,guards,stops and service parts; keep unknown glazing hardware with panel',
        'Panel path starts installed: outward150mm then up100mm; no lift while trapped behind fascia',
        'For frame service,remove floorbridge by20mm lift before100mm outward movement,then remove both sideendbay panels; release four upper-frame blind M6 and12side-frame blind M4 bolts/end; upper cantrail ties/caps and sidepost clamps/stiffeners stay on body',
        'Remove/capture upperM6steel+GFRPwashers; insert complete steppedfork frombelowtie through counted openbottom radiusedslots,takeup thenwithdraw all four integral10mm stem/collar liner kits20mm outward along signedV and capture them; inspect all eight tie/postwall passages empty before frame lift',
        'Capture all lowerM8 hardware and sleeves; support bareframe, lift90mm first then withdraw300mm outward; outward-first failed beam-wall witness remains ancestry',
        'For separate body-side framework repair,remove cantrail caps/backers through open ends; remove firstpost M6 hardware/sleeves, then dismantle owned clamp plates/tabs with counted cut/weld/coat repair; no wholeframe extraction assumed for body-side stock'],
      paths=dict(covers=[[0.,0.,0.],[.100,0.,0.],[.100,0.,.250]],panel=[[0.,0.,0.],[.150,0.,0.],[.150,0.,.100]],
        frame=[[0.,0.,0.],[0.,0.,.090],[.300,0.,.090]],floorcover=[[0.,0.,0.],[0.,0.,.020],[.100,0.,.020]],sidepanel_positive=[[0.,0.,0.],[0.,.100,0.]],sidepanel_negative=[[0.,0.,0.],[0.,-.100,0.]]),
      necessary_removal_bounds=removal_bounds(r),
      upper_liner_detachment=upper_liner_removal_contract(),frame_lift_guard='assert_frame_lift_ready(exact four captured kit IDs)',
      repair_consumables='Body-side welded tabs are replaceable: each repair uses new owned tab blanks,positive80mmAlweld/tab and coat/QA; recurring quantities/cost separate from initial installed stock',
      tools=dict(M8_socket_radius_m=.025,M8_insertion_m=.120,M8_withdrawal_m=.200,M6_socket_radius_m=.015,
        M6_insertion_m=.100,M4_socket_radius_m=.010,M4_insertion_m=.080,source_cantrail_end_access_m=[.091,.241]),
      lifting=dict(shared_fixture_count=1,fixture_mass_bounds_kg=r['process']['shared_fixture_mass_kg'],fixture_price_bounds_USD=r['process']['shared_fixture_cost_USD'],
        payload_rating=None,basis='Positive separate workshop fixture allowance; actual moved state mass,fixing and WLL require later definition/review'),
      all_states_start_installed=True,tool_and_swept_acceptance=False)


def compile_proposal(r,body,local,account):
    """Unexecuted fulltwoends entry; callable only under a separate review/run."""
    before=sources();validate_fixed_recipe(r);_sealed(local);_sealed(account)
    if local['evaluation_id']!=r['local']['geometry_evaluation_id'] or local['physical_definition_id']!=r['local']['physical_definition_id'] or account['evaluation_id']!=r['local']['accounting_evaluation_id']:
        raise ValueError('Exact retained local inputs required')
    cp=counterpart_map(body,r);machining=source_machining(cp,r);legacy=revise_local(local,r);added=added_stock(r)
    component=component_export(legacy,added,account,r,retained_source_parts={p['id']:p for p in body['parts']})
    consumables=consumable_accounting(added,account,r)
    replacements=[]
    for p in body['parts']:
        if not p['id'].startswith('body/terminal-'):continue
        source=source_occurrences(body,p['id'])
        replacements.append(dict(source_part_id=p['id'],source_part_sha256=identity(p),source_ids=[x['id'] for x in source],
          source_occurrence_hashes=[dict(id=x['id'],pattern_sha256=x['source_pattern_sha256']) for x in source],
          operation='replace-or-relocate-once',old_count=len(source),new_owner=FAMILY,
          retained_original_price_once=p['id'] not in ('body/terminal-end-post','body/terminal-end-header','body/terminal-end-skin','body/terminal-end-interface-plate','body/terminal-end-panel-bolt','body/terminal-end-seal'),
          function=p['id'],reason='Explicit new terminal family; original held proxies and failed seven-metre gasket stay ancestry,never an extra live leaf'))
    cladding=[dict(part_id=p['part_id'],pattern_id=p['id'],pattern_sha256=identity(p),disposition='retain source context once; wider finished coverage/actionable issue') for p in body['patterns']
      if p['part_id'] in r['wider_cladding_issue']['part_ids'] and p['car_allocation'] in ([[0,1.]],[[5,1.]])]
    physical=dict(schema='osr-terminal-installed-family-physical/1',input=physical_projection(r),local_definition_id=component['definition_id'],
      exact_legacy_CSG=[{k:e[k] for k in ('id','part_id','geometry','holes','additional_voids') if k in e} for e in legacy],
      added_entities=[{k:e[k] for k in ('id','part_id','material_id','geometry','at_m','rotation','physical_drawing') if k in e} for e in added.entities],
      source_machining=[dict(source_id=x['source_id'],source_part_id=x['source_part_id'],operations=x['operations']) for x in machining])
    if sources()!=before:raise ValueError('Source epoch changed')
    return seal(dict(schema='osr-terminal-installation-definition-proposal/1',candidate_id=identity(physical),physical_definition=physical,
      parent=deepcopy(r['parent']),local=deepcopy(r['local']),source_sha256=before,selection_id=None,
      component_proposal=component,component_bindings=deepcopy(r['bindings']),stock_scope='Local component/newstock/consumables are per end; instantiate two proper bindings. Source machining/replacements cover the train once. Shared workshop fixture one off vehicle.',composer_automatically_applicable=False,source_machining=machining,old_leaf_replacements=replacements,
      source_counterparts=[{k:v for k,v in c.items() if k not in ('part',)} for c in cp],
      retained_passage_seals=dict(quantity=10,part_id='body/passage-end-seal',source_patterns=[dict(id=p['id'],sha256=identity(p)) for p in body['patterns'] if p['part_id']=='body/passage-end-seal'],changed=False),
      wider_cladding_context=cladding,source_accounting_retained=deepcopy(account),new_stock_groups=added.groups,new_welds=added.welds,
      consumables=consumables,materials=deepcopy(r['materials']),source_materials=deepcopy(body['materials']),
      new_material_cost_coverage='Positive newgrossmaterial/process/QA only; legacy finished account once. Sharedfixture/finish/sealant and installation coverage explicitly held below.',
      process_and_QA=deepcopy(r['process']),old_compression_failure=r['old_compression_failure'],bounds=necessary_bounds(r),
      combined_seal_budget=combined_seal_budget(r,support_deflection_m=necessary_bounds(r)['side_stiffener']['tip_deflection_m']),assembly=assembly_plan(r),
      floor_wear_patch=dict(kind='merge with R4wearrecesses once',front_X_m=[.220,.260],rear_X_m=[104.990,105.030],Y_m=[-1.205,1.205],
        net_layer_removed_m=.003,paid_gross_retained=True,precondition='R4finishedwear placement1.147..1.15,not staleP1wear1.1285..1.1315',automatically_applied=False),
      holds=deepcopy(r['holds'])+['Main research physicaldefinition contains exact CSG; plain composer envelope export is explicitly not finished CAD or final same-body admission',
        'Source consumable/material/process scopes are preserved; exact new coated geometry,fixture rating and complete installed/delivery cost remain held,not zero'],**FLAGS))


def requests(r,*,source_commit,source_sha256):
    """At most2unexecuted analytical definition requests, no actual run here."""
    validate_fixed_recipe(r)
    if r['parent']!=PARENT or r['local']!=LOCAL:raise ValueError('Only exact actual source ancestors may be requested')
    common=dict(execution_authorized=False,source_commit=source_commit,source_sha256=source_sha256,
      parent=deepcopy(PARENT),local=deepcopy(LOCAL),recipe_input_id=identity(r),native_jobs=0,body_jobs=0,price_business_jobs=0,independent_review_required=True,**FLAGS)
    return [seal(dict(common,id='terminal-installed-r3-matched-joints',entry_point='engineering.terminal_installation.matched_joint_proposal',CPU_s=30,address_space_bytes=int(1.5*1024**3),wall_s=45,output_bytes=15*1024**2,
      scope='One matched lowerM8/upperM6/sidepostM6/upper-frameM6/side-frameM4 analytical contract packet and closure necessary controls; exact source wall/bore/grip/bearing/edge/tolerance failures preserved',
      completion=['Exact source/geometry/stock IDs','Ordered layers,actual sleeve/bore/remainingwall checks','Net/Gross/Scrap/process and offvehiclefixture scopes','Known failures and unknown qualification separated'])),
      seal(dict(common,id='terminal-installed-r3-two-ends',entry_point='engineering.terminal_installation.compile_proposal',CPU_s=90,address_space_bytes=int(1.5*1024**3),wall_s=120,output_bytes=40*1024**2,
      scope='One two-outer-end definition/typed ownership proposal only, not a vehicle body or native gate',
      completion=['Exactly2retained beams/4cantrails/4firstposts machined once','32+8+24sourcewall operations and removed moments','Oldcomplete leaves/newstock/legacyprices/consumables once','All closure/support/tool/removal/datum/cost-coverage artifacts','Widercladding and supplier/load/fire/creep/WPS/fit holds explicit']))]


def matched_joint_proposal(r,body):
    """Future analytical matched-interface packet, not a body or gate run."""
    before=sources();validate_fixed_recipe(r);cp=counterpart_map(body,r)
    out=seal(dict(schema='osr-terminal-installed-matched-contract-proposal/1',parent=deepcopy(r['parent']),source_sha256=before,
      physical_input_id=identity(physical_projection(r)),counterparts=[{k:v for k,v in x.items() if k!='part'} for x in cp],
      lower_M8=matched_lower_joint(),cantrail_M6=upper_joint(),sidepost_M6=post_joint(),
      detachable_upper_M6=upper_frame_joint(),detachable_side_M4=side_frame_joint(),upper_cage=upper_cage_contract(),upper_liner_removal=upper_liner_removal_contract(),
      bounds=necessary_bounds(r),removal=removal_bounds(r),physical_accepted=False,definition_only=True))
    if before!=sources():raise ValueError('Source epoch changed')
    return out
