"""Source-only research recipe for a replaceable terminal enclosure joint.

This module prepares immutable INPUT proposals and cheap synthetic controls.
It does not read/materialize a body, run CAD/FEM, produce an installed candidate,
or confer a material, load, compression, manufacturing or safety qualification.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite, pi, prod, sqrt

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
FAMILY = 'research/terminal-enclosure-land-and-stop-r1'
ANCESTRY = dict(
    source_commit='85d09e8b7b331226943abeb841367ce94a57e803',
    fitout_candidate_id='104972006cfeb390e8b191c26c103b57f8905997cf673ddf2f20141ccc8b01f3',
    fitout_evaluation_id='0b062be71b049dd8e3a9ee3f1b61456469642f2503cf8e5d0eb11f3959de6cbf',
    body_candidate_id='5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',
    body_evaluation_id='d1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea',
    body_gzip_sha256='f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23')
SOURCE_IDS = {
    'body/terminal-end-post':'a0f82df5f10b7513c8d35ba64c76345a1ec0e90734733086adce3b883bad9f0c',
    'body/terminal-end-header':'6884c83bca7ccc76f8419ad9cca74c26ab404a922bdc0672c619affd34ea7aaf',
    'body/terminal-end-skin':'22945178abfa71f1f613aa38b2f37ec3613c1bc2eee23b7e847b65dc76ea6c38',
    'body/terminal-end-interface-plate':'daca059894c033aff7496b9dd11e11772cb52fba9560fb3e14fc5724fd4a7427',
    'body/terminal-end-panel-bolt':'0f4e4d112db9fe7e9e94dedf78e80eb759d2cd85ea439f87058d28e6f7f8f52a',
    'body/terminal-end-panel-nut':'35ddf13659c9e3e62016ca3b6ee678e9c455a0cd607591071e1be65421d9dc9c',
    'body/terminal-end-panel-washer':'e7edad9f510504006ff4fbbaebe1ad7f2b079d4cdf280acd56c4a95c152cd987',
    'body/terminal-end-seal':'70dad861b9dc8f52aae1b839e7c59b6c7cdec86c97f0fd28bf079773b7962eb8',
    'body/end-beam':'4401eddbd25b6f3dc7acdcf522cc77aad0dd22552dcf99c53f6200a5a143fdbd',
    'body/terminal-window-glass':'b9c6d8a6a8f57dcebf3227ed0d8eb2f268c3844871c1db5ccef2355ca8dc46ba'}
I = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
RX180 = [[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]]
ALONG_V = [[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
ALONG_W = [[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
GLASS_TO_U = [[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]


def encoded(value):
    return ( __import__('json').dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _positive(*values):
    if any(type(x) not in (int,float) or not isfinite(x) or x<=0 for x in values):
        raise ValueError('Finite positive SI input required')


def rhs_area(width,depth,wall):
    _positive(width,depth,wall)
    if 2*wall>=min(width,depth):raise ValueError('Positive RHS interior required')
    return width*depth-(width-2*wall)*(depth-2*wall)


def sleeve_volume(outer,inner,length):
    _positive(outer,inner,length)
    if inner>=outer:raise ValueError('Positive sleeve wall required')
    return pi*(outer**2-inner**2)*length/4


def ring_volume(width,height,radial,axial):
    """Width/height are ring centreline dimensions; four disjoint mitres."""
    _positive(width,height,radial,axial)
    if radial>=min(width,height):raise ValueError('Positive ring opening required')
    return 2*(width+height)*radial*axial


def z_bracket_blank(lower_flat=.080,upper_flat=.080,offset=.070,inner_radius=.016,thickness=.008):
    """Constant-thickness, K=.5 ideal; actual bend allowance needs coupon QA."""
    _positive(lower_flat,upper_flat,offset,inner_radius,thickness)
    r=inner_radius+thickness/2
    straight=offset-2*r
    if straight<=0:raise ValueError('Bend radii consume the required offset')
    return dict(net_developed_length_m=lower_flat+upper_flat+straight+pi*r,
        horizontal_tangent_m=straight,neutral_radius_m=r,K_hypothesis=.5,
        actual_bend_allowance_qualified=False)


def compression_bounds(free_height,stop_length,*,free_tolerance,stop_tolerance,
                       stop_end_parallelism,each_land_flatness,interstop_deflection,
                       keeper_thickness=0.,keeper_tolerance=0.,retention_film=0.,retention_film_tolerance=0.):
    """Arithmetic necessary bound only; positive compression is not a rating."""
    _positive(free_height,stop_length)
    terms=(free_tolerance,stop_tolerance,stop_end_parallelism,each_land_flatness,interstop_deflection,
           keeper_thickness,keeper_tolerance,retention_film,retention_film_tolerance)
    if any(type(x) not in (int,float) or not isfinite(x) or x<0 for x in terms):
        raise ValueError('Explicit finite nonnegative tolerance terms required')
    gap_error=stop_tolerance+keeper_tolerance+stop_end_parallelism+2*each_land_flatness+interstop_deflection
    nominal=free_height+retention_film-stop_length-keeper_thickness
    interval=[nominal-gap_error-free_tolerance-retention_film_tolerance,
              nominal+gap_error+free_tolerance+retention_film_tolerance]
    return dict(compression_interval_m=interval,positive_compression_necessary=interval[0]>0,
        gap_interval_m=[stop_length+keeper_thickness-gap_error,stop_length+keeper_thickness+gap_error],
        upper_compression_limit=None,material_compression_creep_fire_qualified=False,
        engineering_screen='held: material limits, loads and achieved dimensions unknown',**FLAGS)


def rib_line_load_bound(width,depth,wall,span,deflection_allocation,youngs_modulus):
    """Simply-supported bare rib, uniform line load; no joint stiffness credit."""
    _positive(width,depth,wall,span,deflection_allocation,youngs_modulus)
    rhs_area(width,depth,wall)
    inertia=(width*depth**3-(width-2*wall)*(depth-2*wall)**3)/12
    q=384*youngs_modulus*inertia*deflection_allocation/(5*span**4)
    return dict(I_m4=inertia,maximum_line_load_for_allocation_N_m=q,
        imposed_line_load_N_m=None,maximum_deflection_allocation_m=deflection_allocation,
        validity='Straight interclamp rib ideal only; corners, plate coupling, gasket stiffness, WPS/HAZ and actual loads unqualified')


def clamp_grip(clamped_layers,bolt_length,nut_height,thread_protrusion,*,stack_tolerance):
    _positive(*clamped_layers,bolt_length,nut_height,thread_protrusion)
    if stack_tolerance<0 or not isfinite(stack_tolerance):raise ValueError('Explicit stack tolerance required')
    required=sum(clamped_layers)+nut_height+thread_protrusion+stack_tolerance
    return dict(maximum_required_underhead_length_m=required,residual_m=bolt_length-required,
                geometric_length_necessary=bolt_length>=required,
                thread_grade_preload_and_retention_qualified=False)


def cut_allowance(net,gross,*,kerf,trim,reserve):
    _positive(net,gross,kerf,trim,reserve)
    tail=gross-net-kerf-trim-reserve
    if tail < -1e-12:raise ValueError('Stock cannot cover net, kerf, trim and reserve')
    return dict(net_m=net,gross_m=gross,kerf_m=kerf,trim_m=trim,reserve_m=reserve,
                additional_tail_m=max(0.,tail),scrap_and_reserve_m=gross-net)


def stock_spec(part_id,quantity,material,kind,**dimensions):
    return dict(part_id=FAMILY+'/'+part_id,quantity_per_end=quantity,material=material,
                stock_kind=kind,**dimensions)


def recipe():
    """Proposed full local terminal INPUT recipe; never an evaluated candidate."""
    bracket=z_bracket_blank()
    parts=[
      stock_spec('post',2,'al6005a','rhs',net_length_m=2.2,gross_length_m=2.35,width_m=.1,depth_m=.1,wall_m=.004,
                 kerf_m=.003,trim_m=.010,reserve_m=.017,additional_tail_m=.120),
      stock_spec('header',1,'al6005a','rhs',net_length_m=2.25,gross_length_m=2.41,width_m=.1,depth_m=.1,wall_m=.004,
                 kerf_m=.003,trim_m=.010,reserve_m=.017,additional_tail_m=.130),
      stock_spec('lower-rail',1,'al6005a','rhs',net_length_m=2.25,gross_length_m=2.28,width_m=.1,depth_m=.1,wall_m=.004,
                 kerf_m=.003,trim_m=.010,reserve_m=.017),
      stock_spec('frame-land-ring',1,'al5083','mitred-ring',centerline_width_m=2.35,centerline_height_m=2.1,
                 radial_width_m=.1,axial_thickness_m=.006,strip_count=4,net_length_m=8.9,gross_length_m=9.392,
                 tip_allowance_each_m=.1,kerf_each_m=.003,trim_each_m=.010,reserve_each_m=.010),
      stock_spec('panel-land-ring',1,'al5083','mitred-ring',centerline_width_m=2.35,centerline_height_m=2.1,
                 radial_width_m=.1,axial_thickness_m=.006,strip_count=4,net_length_m=8.9,gross_length_m=9.392,
                 tip_allowance_each_m=.1,kerf_each_m=.003,trim_each_m=.010,reserve_each_m=.010),
      stock_spec('panel-rib-post',2,'al6005a','rhs',net_length_m=2.2,gross_length_m=2.23,width_m=.025,depth_m=.1,wall_m=.003,
                 kerf_m=.003,trim_m=.010,reserve_m=.017),
      stock_spec('panel-rib-cross',2,'al6005a','rhs',net_length_m=2.25,gross_length_m=2.28,width_m=.025,depth_m=.1,wall_m=.003,
                 kerf_m=.003,trim_m=.010,reserve_m=.017),
      stock_spec('one-piece-apertured-skin',1,'al5754','apertured-sheet',net_outer_size_m=[2.45,2.2,.002],
                 gross_blank_size_m=[2.46,2.21,.002],window_opening_size_m=[1.56,1.06],
                 kerf_and_trim_edge_each_m=.005,opening_slug_is_scrap=True,salvage_credit_usd=0),
      stock_spec('glazing-backing-ring',1,'al5083','mitred-ring',centerline_width_m=1.63,centerline_height_m=1.13,
                 radial_width_m=.07,axial_thickness_m=.006,strip_count=4,net_length_m=5.52,gross_length_m=5.892,
                 tip_allowance_each_m=.07,kerf_each_m=.003,trim_each_m=.010,reserve_each_m=.010),
      stock_spec('glazing-insert-hardpoint',12,'al5083','drilled-block',net_size_m=[.025,.025,.012],
                 gross_blank_size_m=[.029,.029,.012],pilot_bore_m=.006,
                 maximum_insert_pocket_diameter_m=.010,maximum_insert_pocket_depth_m=.009,
                 final_insert_pocket='unknown: match retainedM5insert supplier drawing before machining; blocks have positive mass, no automatic fit'),
      stock_spec('compression-limiter',24,'al5083','sleeve',outer_diameter_m=.014,inner_diameter_m=.0065,
                 net_length_m=.013,gross_length_m=.017,kerf_m=.002,trim_m=.001,reserve_m=.001),
      stock_spec('gasket-keeper',24,'al5083','one-bend-plate',width_m=.036,thickness_m=.0015,
                 base_flat_m=.028,lip_flat_m=.003,inner_radius_m=.0015,bend_degrees=[90],
                 net_developed_length_m=.028+.003+pi/2*.00225,
                 gross_developed_length_m=.028+.003+pi/2*.00225+.004,
                 gross_width_m=.040,M6_clearance_m=.0065,M3_clearance_m=.0035,
                 radial_lip_m=.007,radial_hole_m=.025,M3_tangential_offset_m=.014,
                 keeper_base_u_m=[.006,.0075],lip_top_u_m=.012),
      stock_spec('keeper-M3-screw',24,'stainless','purchased-bolt',nominal_diameter_m=.003,underhead_length_m=.004,
                 proposed_head_af_m=.0055,proposed_head_height_m=.002,
                 grade='proposed stainless locking-patch screw; supplier/grade/loosening qualification pending'),
      stock_spec('frame-crush-sleeve',24,'al5083','sleeve',outer_diameter_m=.014,inner_diameter_m=.0065,
                 net_length_m=.096,gross_length_m=.100,kerf_m=.002,trim_m=.001,reserve_m=.001),
      stock_spec('panel-crush-sleeve',24,'al5083','sleeve',outer_diameter_m=.014,inner_diameter_m=.0065,
                 net_length_m=.022,gross_length_m=.026,kerf_m=.002,trim_m=.001,reserve_m=.001),
      stock_spec('M6-rear-spreader',24,'al5083','drilled-block',net_size_m=[.040,.040,.008],
                 gross_blank_size_m=[.044,.044,.008],through_bore_m=.0065),
      stock_spec('M6-long-bolt',24,'stainless','purchased-bolt',nominal_diameter_m=.006,underhead_length_m=.180,
                 proposed_head_af_m=.010,proposed_head_height_m=.004,grade='proposedA4-70; unqualified drawing/procurement specification',
                 mass_model='Nominal solid cylinder+hexagon, thread loss not credited; no supplier measured mass'),
      stock_spec('body-Z-bracket',4,'al5083','two-bend-plate',width_m=.120,thickness_m=.008,
                 net_developed_length_m=bracket['net_developed_length_m'],gross_developed_length_m=bracket['net_developed_length_m']+.023,
                 kerf_m=.003,trim_m=.010,reserve_m=.010,inner_radius_m=.016,bend_degrees=[90,-90],
                 K_hypothesis=.5,lower_flat_m=.080,upper_flat_m=.080,offset_m=.070),
      stock_spec('M8-mount-crush-sleeve',8,'al5083','sleeve',outer_diameter_m=.018,inner_diameter_m=.0085,
                 net_length_m=.132,gross_length_m=.136,kerf_m=.002,trim_m=.001,reserve_m=.001),
      stock_spec('M8-front-spreader',8,'al5083','drilled-block',net_size_m=[.040,.040,.008],
                 gross_blank_size_m=[.044,.044,.008],through_bore_m=.0085),
      stock_spec('M8-body-bolt',8,'stainless','purchased-bolt',nominal_diameter_m=.008,underhead_length_m=.180,
                 proposed_head_af_m=.013,proposed_head_height_m=.0053,grade='proposedA4-70; unqualified drawing/procurement specification',
                 mass_model='Nominal solid cylinder+hexagon; no negative thread-volume credit'),
      stock_spec('M8-body-locknut',8,'stainless','purchased-allowance',mass_each_kg=[.005,.008,.012],
                 direct_usd_each=[.1,.2,.4],supplier_grade_and_geometry_qualified=False),
      stock_spec('M8-body-washer',16,'stainless','purchased-allowance',mass_each_kg=[.002,.003,.005],
                 direct_usd_each=[.04,.08,.15],supplier_grade_and_geometry_qualified=False),
      stock_spec('thread-guard',32,'qualified-polymer-required','purchased-allowance',mass_each_kg=[.001,.002,.004],
                 direct_usd_each=[.05,.1,.2],fire_and_retention_qualified=False),
      stock_spec('retained-main-gasket-material',1,'elastomer','retained-current-fitout-leaf',net_length_m=8.9,
                 gross_length_m=9.048,section_m=[.018,.012],source_part_id='research/terminal-perimeter-gasket-r1',
                 adhesive_joints=4,material_quantity_added_again=False),
    ]
    poses=[]
    # Holes belong to named pieces; no zero machining allowance or duplicate
    # sleeve-as-infill volume. Quantities here are PER piece, not per family.
    machining={
      'post':[dict(quantity=6,diameter_m=.0142,length_m=.004),dict(quantity=6,diameter_m=.0065,length_m=.004)],
      'header':[dict(quantity=6,diameter_m=.0142,length_m=.004),dict(quantity=6,diameter_m=.0065,length_m=.004)],
      'lower-rail':[dict(quantity=6,diameter_m=.0142,length_m=.004),dict(quantity=6,diameter_m=.0065,length_m=.004)],
      'frame-land-ring':[dict(quantity=24,diameter_m=.0065,length_m=.006),
          dict(quantity=24,kind='thread-bore',pilot_diameter_m=.0025,total_depth_m=.005,
               thread_major_diameter_m=.003,thread_depth_m=.003)],
      'panel-land-ring':[dict(quantity=24,diameter_m=.0065,length_m=.006)],
      'panel-rib-post':[dict(quantity=6,diameter_m=.0142,length_m=.003),dict(quantity=6,diameter_m=.0065,length_m=.003)],
      'panel-rib-cross':[dict(quantity=6,diameter_m=.0142,length_m=.003),dict(quantity=6,diameter_m=.0065,length_m=.003)],
      'one-piece-apertured-skin':[dict(quantity=24,diameter_m=.0065,length_m=.002),dict(quantity=12,diameter_m=.0055,length_m=.002)],
      'glazing-backing-ring':[dict(quantity=12,diameter_m=.0055,length_m=.006)],
      'body-Z-bracket':[dict(quantity=2,diameter_m=.0085,length_m=.008)]}
    for p in parts:
        p['additional_machining_per_piece']=machining.get(p['part_id'].split('/')[-1],[])
        if p['stock_kind']=='rhs':
            p['additional_machining_per_piece'].append(dict(quantity=2,diameter_m=.003,length_m=p['wall_m'],purpose='permanent weld vent into protected interior void'))
    for side in (-1,1):
        poses += [dict(part='post',index=side,at_uvw_m=[-.05,side*1.175,0.],rotation=ALONG_W),
                  dict(part='panel-rib-post',index=side,at_uvw_m=[.039,side*1.175,0.],rotation=ALONG_W)]
    for name,w in (('header',1.05),('lower-rail',-1.05)):
        poses.append(dict(part=name,index=0,at_uvw_m=[-.05,0.,w],rotation=ALONG_V))
        poses.append(dict(part='panel-rib-cross',index=name,at_uvw_m=[.039,0.,w],rotation=ALONG_V))
    poses += [dict(part='frame-land-ring',at_uvw_m=[.003,0.,0.],ring_normal='u'),
              dict(part='panel-land-ring',at_uvw_m=[.0235,0.,0.],ring_normal='u'),
              dict(part='one-piece-apertured-skin',at_uvw_m=[.0525,0.,0.],normal='u'),
              dict(part='glazing-backing-ring',at_uvw_m=[.0485,0.,0.],ring_normal='u'),
              dict(part='retained-glass',at_uvw_m=[.0635,0.,0.],rotation=GLASS_TO_U,
                   unchanged_source_size_m=[1.6,1.1,.012],sealing_gap_proposal_m=.004,
                   glazing_profile_fit_and_retention_qualified=False)]
    clamps=[]
    for side in (-1,1):
        clamps += [dict(vw_m=[v,side*1.075],axis_uvw=[1.,0.,0.],row='cross') for v in (-.95,-.57,-.19,.19,.57,.95)]
        clamps += [dict(vw_m=[side*1.20,w],axis_uvw=[1.,0.,0.],row='post') for w in (-.85,-.51,-.17,.17,.51,.85)]
    mounts=[]
    for v in (-.8,-.4,.4,.8):
        mounts.append(dict(bracket_center_v_m=v,
            lower_plate_midline_uw_m=[-.174,-1.18],upper_plate_midline_uw_m=[-.104,-1.06],
            bend_centres_uw_m=[[-.154,-1.14],[-.124,-1.10]],
            body_M8_holes_uvw_m=[[-.1,v-.030,-1.18],[-.1,v+.030,-1.18]],
            source_end_beam_center_uvw_m=[-.1,0.,-1.2655],source_end_beam_axis='v',
            source_end_beam_cross_uw_m=[.14,.25],
            upper_joint='two80mmAl-to-Al4mmfillet seams per bracket; no steel/aluminium weld',
            source_end_beam_scope='Drill only the two terminal beam occurrences; other10body/end-beam occurrences unchanged'))
    ownership=[]
    for source,old,new,target,mode in (
        ('body/terminal-end-post',2,2,'post','replace correctly oriented, trim declared2.35m stock'),
        ('body/terminal-end-header',1,1,'header','replace correctly oriented, trim declared2.41m stock'),
        ('body/terminal-end-skin',2,1,'one-piece-apertured-skin','replace two uncut proxies with one defined skin; no old sheet reuse claimed'),
        ('body/terminal-end-interface-plate',4,4,'body-Z-bracket','replace undersized0.2m flat stock; new0.252832m developed bent plate'),
        ('body/terminal-end-panel-bolt',24,24,'M6-long-bolt','replace unverified fastener allowance with proposed180mm underhead bolt;60mm source envelope is NOT a measured bolt length; never add24on top'),
        ('body/terminal-end-panel-nut',24,24,None,'retain once, grade/thread compatibility held'),
        ('body/terminal-end-panel-washer',48,48,None,'retain once, grade/bearing diameter held')):
        ownership.append(dict(source_part_id=source,source_component_definition_id=SOURCE_IDS[source],
            old_quantity_per_end=old,new_quantity_per_end=new,new_part_id=None if target is None else FAMILY+'/'+target,
            disposition=mode,retired_source_added_again=False))
    return dict(schema='osr-terminal-enclosure-recipe-input/1',family=FAMILY,ancestry=deepcopy(ANCESTRY),
      source_component_ids=deepcopy(SOURCE_IDS),parts=parts,local_part_poses=poses,
      terminal_bindings=[dict(source_occurrence='body/terminal-end/end-0',at_world_m=[0.,0.,2.25],rotation=RX180),
                         dict(source_occurrence='body/terminal-end/end-5',at_world_m=[105.25,0.,2.25],rotation=I)],
      frame=dict(axes='right-handed u=outward,v=lateral,w=up; first terminal flips u AND v',
                 world_equation='world=terminal.rotation@local+terminal.at_world_m',fixed_floor_top_world_m=1.15,
                 local_frame_outer_vw_m=[2.45,2.2],fixed_body_width_m=2.65),
      clamp_stations=clamps,body_mounts=mounts,source_replacement_ownership=ownership,
      main_stack_uvw_m=dict(frame_RHS=[-.100,0.],frame_land=[0.,.006],keeper_base=[.006,.0075],limiter=[.0075,.0205],
          panel_land=[.0205,.0265],panel_RHS=[.0265,.0515],panel_skin=[.0515,.0535],
          M6_rear_spreader=[-.108,-.100],frame_crush_sleeve=[-.096,0.],panel_crush_sleeve=[.0265,.0485]),
      holes=dict(M6_through_m=.0065,frame_front_entry_m=.0142,panel_inner_entry_m=.0142,
          frame_rear_through_m=.0065,panel_outer_through_m=.0065,
          body_front_entry_m=.0182,body_rear_through_m=.0085,Z_bracket_mount_through_m=.0085,
          keeper_frame_blind_pilot_m=.0025,keeper_frame_blind_depth_m=.005,
          keeper_frame_M3_thread_depth_m=.003,keeper_plate_M3_clearance_m=.0035,
          drilling_stock_losses='Subtract front/rear wall holes and land/skin/spreader holes once; sleeve stock is separate, not infill counted twice'),
      weld_vent_pattern=dict(holes_per_RHS_piece=2,diameter_m=.003,total_RHS_pieces_per_end=8,
          station_rule='150mm from each net member end; inner radial wall, tube axial-depth midplane',
          fixed_frame_depth_center_u_m=-.05,panel_rib_depth_center_u_m=.039,
          closure='Remain open to protected interior void after welding; finished drain/fire/corrosion behaviour and any added drain hardware are unqualified, not assumed zero'),
      welds=[dict(part='fixed-frame',joints=4,length_m=1.6,leg_m=.004,material='Al filler compatible with6005A/5083, WPS/HAZ unknown'),
             dict(part='panel-rib',joints=4,length_m=1.0,leg_m=.003,material='Al filler, WPS/HAZ unknown'),
             dict(part='land-corners-two-rings',joints=8,length_m=.8,leg_m=.004,material='Al filler'),
             dict(part='frame-land-to-RHS',joints=1,length_m=17.8,leg_m=.003,material='Al-to-Al only'),
             dict(part='panel-land-to-rib',joints=1,length_m=17.8,leg_m=.003,material='Al-to-Al only'),
             dict(part='panel-skin-outer-seam',joints=1,length_m=9.3,leg_m=.0015,material='5754to6005A; thin-sheet WPS/distortion control required'),
             dict(part='glazing-ring-to-skin',joints=1,length_m=5.8,leg_m=.0015,material='5083to5754; glazing retention qualification separate'),
             dict(part='glazing-ring-corners',joints=4,length_m=.28,leg_m=.003,material='Al filler'),
             dict(part='glazing-hardpoint',joints=24,length_m=.6,leg_m=.003,material='Al-to-Al'),
             dict(part='body-Z-bracket-upper',joints=8,length_m=.64,leg_m=.004,material='Al-to-Al only')],
      consumables=dict(weld_filler_procurement_factor=1.20,finish_dry_film_m=.000040,
          finish_density_hypothesis_kg_m3=1300,finish_procurement_factor=1.20,
          joint_sealant_installed_kg_per_end=[.020,.040,.080],sealant_procurement_factor=1.5,
          gasket_tack_film_thickness_m=.00010,gasket_tack_film_width_m=.012,gasket_tack_film_length_m=8.9,
          gasket_tack_film_density_hypothesis_kg_m3=1100,gasket_tack_film_procurement_factor=1.5,
          spare_M6_bolts_per_train=2,spare_M8_sets_per_train=1,
          spare_M3_screws_per_train=2,spare_thread_guards_per_train=2,spare_keeper_tabs_per_train=2,
          spare_sleeves_and_limiters_per_train=2,
          coating='Mask precision seal lands and all keeper/stop/sleeve bearing faces; protect remainingAl/stainless contacts by specified corrosion system/sealant; durability unqualified'),
      surface_spec=dict(dry_coating_m=.000040,coating_material_spec='unselected railway-compatible corrosion coating',
          mask='Precision gasket lands and keeper/limiter/sleeve bearing contacts',
          tack_material_spec='unselected elastomer-compatible railway adhesive',
          qualification='Unknown coating/tack chemistry, fire, strength and durability; selection requires a new physical recipe identity'),
      source_end_beam_drilling_per_terminal_occurrence=[
          dict(quantity=8,diameter_m=.0182,length_m=.008,face='outward entry'),
          dict(quantity=8,diameter_m=.0085,length_m=.008,face='inboard')],
      other_source_ownership=dict(main_gasket='Retain current8.9m/9.048m developed/gross material once from fitout104972; old P1seven-metre allocation remains failed ancestry',
          passage_seals=dict(source_part_id='body/passage-end-seal',quantity_per_train=10,developed_each_m=7.,changed=False),
          terminal_glazing='Retain all source glass/seal/retainer/bond/12M5bolt+insert+washer per end once; change glass orientation only under new assembly binding; actual profile/insert fit held',
          body_end_beam='Retain all12beams once; only terminal2occurrences receive new8mount bores/end and positive hardware; subtract drilling loss under future physical revision',
          excluded_changes='Doors, gangways, seat geometry/datums, wheels/gauge, floor/roof/civil and terminal crash obligations unchanged',
          old_failure=dict(compression_interval_m=[-.002,.006],screen_passed=False,preserved=True)),
      mechanism_inventory_per_end=dict(compression_stops=24,gasket_keepers=24,
          frame_crush_sleeves=24,panel_crush_sleeves=24,body_mount_crush_sleeves=8,
          replacement_M6_bolts=24,retained_M6_nuts=24,retained_M6_washers=48,
          new_M3_screws=24,new_M8_bolts=8,new_M8_nuts=8,new_M8_washers=16,
          retained_glazing_M5_sets=12,new_thread_guards=32,
          bearings=0,slides=0,added_wiring=0,added_cooling_flexes=0,
          exact_zero_scope='Passive terminal enclosure joint only; other train mechanisms/services retain separate ownership'),
      load_path=['Gasket pressure and terminal panel service loads enter skin/land/rib, through24retained-countM6clamps and24positive limiters',
          'Panel outer wall and fixed-frame rear wall supported by24crush sleeves each plus24rear spreaders; no bare hollow-wall preload shortcut',
          'Fixed100x100RHS frame transfers to4weldedAlZbrackets then8M8bolts/sleeves/spreaders into actual140x250x8body end beam',
          'Structural, crash and fatigue capacity remain unknown; full-body end-beam/support load propagation is a separate held task'],
      gasket_retention=dict(keeper_count=24,M3_screw_count=24,
          tack_film_thickness_m=.0001,tack_film_width_m=.012,tack_film_length_m=8.9,
          location='At eachM6station, radial keeper lip7mm from gasket centreline,1mm clear of nominal gasket edge; lip6mm above datumA',
          orientation='Local radial r points outwards inVW; t=(-r_w,r_v). M6at(r=.025,t=0), M3at(r=.025,t=.014); r/uformed profile is declared in keeper stock',
          hard_stop_chain='DatumA+1.5mm keeper base+13mm limiter=14.5mm land-to-land gap; keeper thickness is NOT omitted',
          tack='Positive100um specified tack film positions free gasket; closed panel and formed keepers provide mechanical capture. No adhesive strength credited for enclosure pressure.',
          unresolved='Keeper strength, gasket extrusion/bulge/pressure, screw loosening/fire and achieved adhesive film thickness require measurement/limits'),
      glazing_interface=dict(unchanged_glass_size_m=[1.6,1.1,.012],aperture_vw_m=[1.56,1.06],
          source_M5_count=12,hardpoint_center_u_m=.0395,
          hardpoint_vw_m=[[v,side*.555] for side in (-1,1) for v in (-.6,-.2,.2,.6)]+
                         [[side*.805,w] for side in (-1,1) for w in (-.25,.25)],
          qualified_insert_pocket=None,retainer_profile_fit_and_crash_protection=None,
          source_retainer_developed_length_m=5.4,
          hold='12new positive-mass blocks with bounded insert pockets support separately retained12M5inserts; supplier insert/retainer drawings and glass-edge loads must fit or trigger another physical revision'),
      assembly_sequence=['Cut, drill and deburrRHS/plates; identify stock certificates and each source/replacement part ID',
          'Install accessible sleeves before closure; jig fixed frame, lower rail and4Zbrackets; weld only compatibleAlwith approvedWPS',
          'Jig panelrib, skin, two land rings and glazing backing/hardpoints; weld in controlled balanced sequence; inspect vents/closures and NDT',
          'Face/lap gasket and limiter lands after all welds; measure datumsA/B and all24contact stations; qualify machining fixture capacity before release',
          'Fit24formed keepers with24M3screws into declared blind tapped land holes; apply measured tack film, fit gasket between locator lips',
          'Fit sleeves, rear spreaders and source-count24longM6bolts/nuts/washer pairs;13mm stops sit on1.5mmkeeper bases and are removable on bolt shanks',
          'Install4Zbrackets against measured end-beam face; drill only approved local patterns, fit8mount sleeves/spreaders/bolt sets; inspect edge distances and body load path',
          'Fit separately retained glazing only after supplier profile/insert/retention drawings match; support pane on rated fixtures',
          'Fit gasket; close to all24limiters using qualified preload procedure and verify feeler gap/contact/compression/leak checks before use'],
      repair_sequence=['Isolate/protect terminal work area; support panel plus separately counted52.8kg glass on rated fixture before releasing clamps',
          'Remove24M6clamps and guards; retain32sleeves/limiters by inventoried service kit; translate panel outward first150mm before any lift',
          'For frame removal, support complete module, remove8bodyM8mount clamps from accessible backside; withdraw outward with panel/glass removed',
          'Inspect all lands, threads, sleeves, brackets, welds, corrosion and profile; replace damaged parts by ID and remeasure full stack'],
      repair_path_local_m=dict(panel=[[0.,0.,0.],[.15,0.,0.],[.15,0.,.10]],
          frame=[[0.,0.,0.],[.30,0.,0.],[.30,0.,.10]]),
      access_and_handling=dict(proposed_socket_radius_m=.025,proposed_axial_insertion_m=.120,
          proposed_external_cradle_WLL_kg=500,cradle_load_factor=1.5,
          fixture_contact='Four padded support positions on lower rail; no uncounted permanent lifting eyes credited',
          complete_module_mass_and_lifting_rating_known=False,tool_and_lift_collision_free=False,
          production_fixture_cost_usd=None,vehicle_workshop_access_hours=None),
      drawing_schedule=[
          dict(id='TJ01',scope='GA and source disposition',required='All part IDs/quantities, right-handed source-to-local transforms, end-beam drill ownership and fixed global interfaces'),
          dict(id='TJ02',scope='Datum/land and complete clamp map',required='DatumA=frame-land outer faceu.006; datumB=panel-land inner faceu.0205; frame RVS fixed;24M6,24M3blindtap and vent coordinates; postweld flatness/contact inspection'),
          dict(id='TJ03',scope='Stops/sleeves/keepers',required='13mmlimiters,1.5mmkeeper stack,96/22mmcrush sleeves; end parallelism/finish, keeper bend/form/tack film and all hole/edge distances'),
          dict(id='TJ04',scope='Panel and glazing backing',required='One-piece aperture,12new bounded hardpoints and retained glass/M5components; insert/retainer fit remains hold point'),
          dict(id='TJ05',scope='BodyZmount and end-beam connection',required='8mmR16bends,K=.5proposal, welds,8M8holes,132mmsleeves and spreaders; actual body support/load review'),
          dict(id='TJ06',scope='WPS,QA and service',required='CompatibleAl WPS/HAZ,NDT, open weld-vent paths, final machining/jig capacity, material/corrosion/fire records, assembly torque/load procedure and rated external cradle')],
      holds=['No actual candidate generated. Recipe/input IDs are not installed physical candidate acceptance.',
          'Old wrong post/header/glass transforms are explicitly superseded; root body and receipts remain untouched until coordinated propagation.',
          'Source M6envelopes do not prove180mm availability or nut/washer grade; new specified bolts and retained nuts/washers need authenticated drawings/strength and preload review.',
          'Achieved land flatness, stop length, gasket height, bulge, compression-force/creep/fire, temperature movement and seal life remain unknown.',
          'Weld HAZ, corner/frame/skin strength, buckling, pressure/fatigue/crash loads and mount end-beam effects are unqualified.',
          'Monolithic skin removes opaque-panel seam; aperture/glazing profile retention and floor/roof/sideframe closure interfaces remain separate holds.',
          'Full machining tool capacity, bends/springback, lifting eyes, fixtureWLL, nut access and finite collision envelopes must be verified; no bolt socket plan establishes access.',
          'Fixed floor1.15m and accepted seat1.60vs1.45m datum/CGhold remain; no floor geometry or passenger load result reused.',
          'Unknown installation/finish/tether/retention details stay unknown or bounded; procurement and mass subcalculations are not complete installed mass/cost.'],
      **FLAGS)


def physical_projection(proposal):
    """Installed recipe specification; exclude stock loss, price and evidence.

    The unprojected input recipe retains procurement/QA/workflow instructions.
    Unknown installed interfaces remain unknown in that input, never zero.
    """
    raw=proposal['physical_recipe']
    part_keys=('part_id','quantity_per_end','material','stock_kind','net_length_m',
        'net_developed_length_m','width_m','depth_m','wall_m','thickness_m',
        'centerline_width_m','centerline_height_m','radial_width_m','axial_thickness_m',
        'net_outer_size_m','net_size_m','window_opening_size_m','pilot_bore_m','through_bore_m',
        'outer_diameter_m','inner_diameter_m','nominal_diameter_m','underhead_length_m',
        'proposed_head_af_m','proposed_head_height_m','grade','inner_radius_m',
        'bend_degrees','lower_flat_m','upper_flat_m','offset_m','section_m',
        'source_part_id','adhesive_joints','base_flat_m','lip_flat_m','M6_clearance_m',
        'M3_clearance_m','radial_lip_m','radial_hole_m','M3_tangential_offset_m',
        'keeper_base_u_m','lip_top_u_m','maximum_insert_pocket_diameter_m','maximum_insert_pocket_depth_m',
        'additional_machining_per_piece')
    pose_keys=('part','index','at_uvw_m','rotation','ring_normal','normal',
               'unchanged_source_size_m','sealing_gap_proposal_m')
    mount_keys=('bracket_center_v_m','lower_plate_midline_uw_m','upper_plate_midline_uw_m',
        'bend_centres_uw_m','body_M8_holes_uvw_m','source_end_beam_center_uvw_m',
        'source_end_beam_axis','source_end_beam_cross_uw_m')
    owner_keys=('source_part_id','source_component_definition_id','old_quantity_per_end',
                'new_quantity_per_end','new_part_id')
    subset=lambda row,keys:{k:deepcopy(row[k]) for k in keys if k in row}
    def project_part(row):
        p=subset(row,part_keys)
        p['additional_machining_per_piece']=[subset(op,('quantity','kind','diameter_m','length_m',
            'pilot_diameter_m','total_depth_m','thread_major_diameter_m','thread_depth_m'))
            for op in row.get('additional_machining_per_piece',[])]
        return p
    return dict(schema='osr-terminal-joint-physical-recipe-projection/1',family=raw['family'],
        parent_body_candidate_id=proposal['ancestry']['body_candidate_id'],
        parent_fitout_candidate_id=proposal['ancestry']['fitout_candidate_id'],
        parts=[project_part(x) for x in raw['parts']],
        local_part_poses=[subset(x,pose_keys) for x in raw['local_part_poses']],
        terminal_bindings=deepcopy(raw['terminal_bindings']),
        clamp_stations=deepcopy(raw['clamp_stations']),
        body_mounts=[subset(x,mount_keys) for x in raw['body_mounts']],
        main_stack_uvw_m=deepcopy(raw['main_stack_uvw_m']),
        gasket_retention=subset(raw['gasket_retention'],('keeper_count','M3_screw_count',
            'tack_film_thickness_m','tack_film_width_m','tack_film_length_m')),
        glazing_interface=subset(raw['glazing_interface'],('unchanged_glass_size_m','aperture_vw_m',
            'source_M5_count','hardpoint_center_u_m','hardpoint_vw_m','qualified_insert_pocket',
            'source_retainer_developed_length_m')),
        holes={k:v for k,v in raw['holes'].items() if type(v) in (int,float)},
        weld_vent_pattern=subset(raw['weld_vent_pattern'],('holes_per_RHS_piece','diameter_m','total_RHS_pieces_per_end',
            'station_rule','fixed_frame_depth_center_u_m','panel_rib_depth_center_u_m')),
        surface_spec=subset(raw['surface_spec'],('dry_coating_m','coating_material_spec','mask','tack_material_spec')),
        source_end_beam_drilling_per_terminal_occurrence=deepcopy(raw['source_end_beam_drilling_per_terminal_occurrence']),
        welds=[subset(x,('part','joints','length_m','leg_m','material')) for x in raw['welds']],
        source_replacement_ownership=[subset(x,owner_keys) for x in raw['source_replacement_ownership']])


def proposal():
    r=recipe()
    # Status, work instructions and provenance statements do not define solids.
    keep=('family','parts','local_part_poses','terminal_bindings','clamp_stations',
          'body_mounts','main_stack_uvw_m','holes','welds','source_replacement_ownership',
          'gasket_retention','glazing_interface','source_end_beam_drilling_per_terminal_occurrence','weld_vent_pattern','surface_spec')
    p=dict(schema='osr-terminal-joint-source-proposal/1',physical_recipe={k:deepcopy(r[k]) for k in keep},
        ancestry=deepcopy(ANCESTRY),source_only_recipe=r,
        evaluation_inputs=dict(
            free_gasket_height_tolerance_m=.00020,limiter_length_tolerance_m=.00005,
            keeper_thickness_tolerance_m=.00005,tack_film_thickness_tolerance_m=.00005,
            limiter_total_end_parallelism_m=.00006,each_land_flatness_m=.00010,
            interstop_deflection_allocation_m=.00015,largest_interclamp_span_hypothesis_m=.475,
            inherited_body_unresolved_position_uncertainty_m=.25,source_exact_stock_position_uncertainty_m=.002,
            youngs_modulus_hypothesis_Pa=69e9,actual_pressure_Pa=None,actual_gasket_line_force_N_m=None,
            material_compression_upper_limit=None,creep_life_limit=None,
            bolt_preload_N=None,proof_loads_N=None,
            source_aluminium_usd_kg=[2.5,4.,6.5],source_labour_usd_h=[6.,10.,16.],source_overhead_fraction=[.1,.2,.3],
            stainless_stock_usd_kg_hypothesis=[8.,12.,18.],
            complete_local_fabrication_hours_per_end_hypothesis=[8.,14.,24.],
            fabrication_hours_scope='Cut/form/drill, jigs,welding,postweld facing and routine dimensionalQA once; not added again per part',
            bought_bolt_process_usd_each_hypothesis=dict(M3=[.1,.2,.4],M6=[.5,1.,2.],M8=[.8,1.5,3.]),
            final_vehicle_integration_hours=None,qualification_cost_usd=None,delivery_and_tax_usd=None,
            tool_socket_radius_m=.025,tool_axial_insertion_m=.120,
            output_resource_budget=dict(cpu_s=105,memory_mib=1024,aggregate_mib=30),
            price_basis='Use pinned sourceAl/labour/overhead rates for explicit gross stock; stainless bought items/consumables/process are declared hypotheses or unknown; no country discount/quotation.'),
        required_status='Source proposal ready for review; no actual runs authorized by this file',**FLAGS)
    p['physical_recipe_id']=identity(physical_projection(p))
    p['proposal_input_id']=identity(p)
    return p


def trial_inputs(*,source_sha256=None,source_commit=None):
    """At most three immutable, unexecuted LOCAL input/resource requests."""
    p=proposal();out=[]
    for name,cpu,output,scope,variables,artifacts in (
      ('terminal-module-accounting',30,15,
       'One local terminal assembly only, no train/body occurrence expansion',
       dict(recipe=p['physical_recipe'],source_replacement_records_required=True),
       ['exact net/gross/cut/drill/weld/finish inventory and ownership delta, low/base/highmass+cost with unknowns',
        'all local coordinate matrices, material solids/holes and CAD-command INPUT only; no CAD execution',
        'nominal/uncertain/recovery/removal envelopes, datum/QA drawing schedule and unresolved interfaces']),
      ('seal-stop-corner-control',30,8,
       'One600x600mm local corner coupon plus declared straight interclamp necessary bound',
       dict(coupon_legs_m=[.6,.6],RHS_frame_m=[.1,.1,.004],RHS_panel_m=[.1,.025,.003],
            gasket_section_m=[.018,.012],stop_length_m=.013,stop_OD_ID_m=[.014,.0065],
            keeper_thickness_m=.0015,tack_film_thickness_m=.00010,
            synthetic_line_load_controls_N_m=[0.,250.,500.,1000.,2000.],
            synthetic_achieved_land_flatness_controls_m=[.0001,.002],
            load_line_force_N_m=None,tolerances=p['evaluation_inputs']),
       ['complete initial/removal sweep, corner/clamp/stop/sleeve drill map and contact stack',
        'positive-compression necessary interval and q-domain inversion; NOmaterial/rated pass',
        'weld/bend/flatness/creep/firemeasurement plan with acceptance limits held']),
      ('body-bracket-coupon',45,7,
       'One localZbracket, twoM8joints and140x250x8end-beam coupon; no full-body evaluation',
       dict(bracket=z_bracket_blank(),width_m=.12,thickness_m=.008,
            source_beam_cross_section_m=[.14,.25,.008],frame_section_m=[.1,.1,.004],
            bolt_diameter_m=.008,bolt_underhead_length_m=.180,
            sleeve_OD_ID_length_m=[.018,.0085,.132],
            synthetic_bolt_preload_controls_N=[500.,1000.,2000.],
            synthetic_mount_reaction_controls_N=[0.,1000.,3000.],
            source_beam_position_uvw_m=[-.1,0.,-1.2655],bracket_pose=recipe()['body_mounts'][0]),
       ['explicit formed profile, cut/form stock and volume residual; hole/edge-distance and accessible-tool necessary checks',
        'preload/crush/bearing/bolt-grip residuals at declared synthetic loads, with source strengths unknown',
        'install/removal/QA/refit sequence and body drill/mount propagation holds'])):
        t=dict(schema='osr-terminal-joint-local-trial-input-proposal/1',trial=name,
            family=FAMILY,physical_recipe_id=p['physical_recipe_id'],ancestry=deepcopy(ANCESTRY),
            source_commit=source_commit,source_sha256=deepcopy(source_sha256),
            scope=scope,variables=variables,permitted_execution='pure local analytic/CAD-command preparation; zero native/model/FEM/journey/fullbody',
            request=dict(cpu_s=cpu,address_space_mib=1024,private_output_mib=output,native_jobs=0,
                         full_body_jobs=0,trial_count=1),
            required_artifacts=artifacts,completion_conditions=[
                'Pin reviewed source commit/hash,Python tool identity and local worker script hash before execution; proposed inputs alone authorize no run',
                'Exact source/tool/input/request hashes, unchanged source/parent inputs and closed-file manifest',
                'Preserve failed/out-of-domain checks and explicit numerical/engineering/evidence/selection/release status',
                'No unspecified mass, price, stops, bolt grade, material bound, source ownership or physical release inferred',
                'Independent review before any full-body propagation; old[-2,6]mm failure retained'],
            execution_status='proposed-not-run',**FLAGS)
        t['input_id']=identity(t);out.append(t)
    return out


def geometric_stock_volume(part,*,gross):
    """Stock shape kernel before separately listed additional machining.

    Drilled blocks/keepers already include their basic bores. Additional drill
    and uncertain thread-volume bounds are returned by machining_volume_bounds.
    Neither function alone is a complete installed-mass producer.
    """
    k=part['stock_kind']
    if k=='rhs':return rhs_area(part['width_m'],part['depth_m'],part['wall_m'])*part['gross_length_m' if gross else 'net_length_m']
    if k=='sleeve':return sleeve_volume(part['outer_diameter_m'],part['inner_diameter_m'],part['gross_length_m' if gross else 'net_length_m'])
    if k=='mitred-ring':return part['radial_width_m']*part['axial_thickness_m']*part['gross_length_m' if gross else 'net_length_m']
    if k=='apertured-sheet':
        if gross:return prod(part['gross_blank_size_m'])
        w,h,t=part['net_outer_size_m'];return (w*h-prod(part['window_opening_size_m']))*t
    if k=='drilled-block':
        if gross:return prod(part['gross_blank_size_m'])
        size=part['net_size_m'];bore=part.get('through_bore_m',part.get('pilot_bore_m'))
        # All block dimension lists are in face-width, face-height, axial-depth order.
        return prod(size)-pi*(bore/2)**2*size[2]
    if k=='two-bend-plate':return part['width_m']*part['thickness_m']*part['gross_developed_length_m' if gross else 'net_developed_length_m']
    if k=='one-bend-plate':
        if gross:return part['gross_width_m']*part['thickness_m']*part['gross_developed_length_m']
        holes=pi/4*(part['M6_clearance_m']**2+part['M3_clearance_m']**2)*part['thickness_m']
        return part['width_m']*part['thickness_m']*part['net_developed_length_m']-holes
    if k=='purchased-bolt':
        return pi*(part['nominal_diameter_m']/2)**2*part['underhead_length_m']+sqrt(3)/2*part['proposed_head_af_m']**2*part['proposed_head_height_m']
    if k in ('purchased-allowance','retained-current-fitout-leaf'):return None
    raise ValueError('Declared stock kernel required')


def machining_volume_bounds(operations):
    """Positive material removal, with finite thread-form uncertainty."""
    low=high=0.
    for op in operations:
        n=op['quantity'];_positive(n)
        if op.get('kind')=='thread-bore':
            dp,dm,total,thread=(op[k] for k in ('pilot_diameter_m','thread_major_diameter_m','total_depth_m','thread_depth_m'))
            _positive(dp,dm,total,thread)
            if dm<dp or thread>total:raise ValueError('Bounded thread profile required')
            pilot=n*pi*dp**2/4*total
            low+=pilot;high+=pilot+n*pi*(dm**2-dp**2)/4*thread
        else:
            _positive(op['diameter_m'],op['length_m'])
            v=n*pi*op['diameter_m']**2/4*op['length_m'];low+=v;high+=v
    return dict(removed_volume_interval_m3=[low,high],unknown_thread_form=low!=high)


def material_cost_bound(net_volume,gross_volume,density,rate,process_hours,labour_rate,overhead):
    _positive(net_volume,gross_volume,density,rate,process_hours,labour_rate)
    if gross_volume<net_volume or not 0<=overhead<=1:raise ValueError('Positive scrap and explicit overhead required')
    return dict(net_material_mass_kg=net_volume*density,gross_procurement_mass_kg=gross_volume*density,
        scrap_and_reserve_mass_kg=(gross_volume-net_volume)*density,
        direct_usd=(gross_volume*density*rate+process_hours*labour_rate)*(1+overhead),
        excludes='Fasteners, drills, weld, finish, integration, QA/qualification, delivery and tax unless explicitly added; never complete installed cost')
