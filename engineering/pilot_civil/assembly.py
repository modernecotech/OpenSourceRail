"""Located outline civil parts, cutting patterns and construction stages.

CAD solids, bar centreline definitions and positive quantity reserves are separate.
Neither a model nor a successful screen releases a bridge for construction.
"""
from math import ceil, cos, fsum, pi, sqrt
from . import FLAGS
from .design import G, identity, seal


def construction(result):
    p=result['policy'];q=result['quantities'];s=result['section'];lift=result['lifting']
    length=10. if result['physical_definition']['segment_count']==2 else 20.
    m=lift['segmented_piece_kg'] if length==10 else lift['whole_lift_piece_kg']
    w=m*G/length*p['lifting']['lifting_factor'];a=.2*length;b=.8*length
    # Two lifting stations, two positively attached legs at each station.
    R=w*length/2;M=max(w*a*a/2,abs(R*(length/2-a)-w*(length/2)**2/2))
    stress=M*max(s['top_distance_m'],s['bottom_distance_m'])/s['I_y_m4']
    tension_target=2e6  # Explicit temporary uncracked research target, not an allowable.
    phi=pi/4;sling=R/(2*cos(phi))
    # Reusable four-leg braced midspan tower, one per track. Steel capacity and
    # concrete-pad pressure are hypotheses; connection design remains open.
    height=p['support']['column_height_m']+p['support']['cap_size_m'][2]
    diameter=.25;wall=.012;A=pi/4*(diameter**2-(diameter-2*wall)**2);I=pi/64*(diameter**4-(diameter-2*wall)**4)
    N=lift['whole_lift_piece_kg']*G*1.3
    capacity=min(A*235e6,pi*pi*200e9*I/height**2)/3
    pad=ceil(sqrt(N/4/result['foundation']['soil_target_Pa'])*4)/4
    tower_mass=4*A*height*7850+400  # Bracing, jacks and caps positive reserve.
    return seal(dict(schema='osr-pilot-civil-construction/1',civil_candidate_id=result['civil_candidate_id'],
        handling=dict(piece_length_m=length,lifting_station_x_local_m=[a,b],sling_legs=4,sling_angle_from_vertical_rad=phi,
            peak_station_reaction_N=R,each_sling_required_N=sling,temporary_gross_stress_Pa=stress,
            temporary_tension_target_Pa=tension_target,gross_handling_target_met=stress<=tension_target,
            attachment_design_verified=False,required_hook_kg=lift['segmented_required_hook_kg'] if length==10 else lift['whole_required_hook_kg'],
            actual_crane_chart_verified=False,wind_and_transport_stability_verified=False),
        midspan_tower=dict(sets=p['lifting']['temporary_support_reused_sets'],legs_each=4,height_m=height,
            tube_outer_diameter_m=diameter,wall_m=wall,steel_stock_and_hardware_reserve_kg=tower_mass,
            factored_required_N=N,capacity_hypothesis_N=4*capacity,elastic_capacity_screen=4*capacity>=N,
            each_sole_pad_width_m=pad,pad_thickness_m=.30,soil_pressure_Pa=N/4/pad**2,
            braced_length_hypothesis_m=height,connection_buckling_and_settlement_verified=False),
        erection_sequence=[
            'Survey utilities, bearing level and ground; approve crane chart, access and temporary foundations.',
            'Cast footing, pier and cap; cure to independently demonstrated release strength.',
            'Place bearings with surveyed seat heights; install and level a braced midspan tower.',
            'Lift first 10 m segment on four designed attachments at 20/80% length; set onto end bearing and tower.',
            'Set matching second segment; survey fit and apply controlled 2 mm epoxy joint layer.',
            'Thread continuous tendons, stress in symmetric increments and grout under controlled QA.',
            'Gradually unload tower while measuring camber, joint closure and bearing reactions.',
            'Install rails, pads, fasteners, drainage, guard and inspection walkway; survey and inspect.',
            'Proof, monitor and independently review the complete civil assembly before any release.'],
        idealised_final_two_support_prestress_only=True,prop_restrained_secondary_prestress_verified=False,
        construction_release=False,**FLAGS))


def scene(result,*,gross_beam_only=False):
    """One exact gross beam for FEM, or a located two-track assembly projection.

    Gross concrete stock includes reinforcement/duct space; CAD overlaps are
    explicitly retained gross-stock idealisations and never summed as mass.
    """
    p=result['policy'];s=result['section'];cid=result['civil_candidate_id'];entities=[]
    def add(id,shape,material,**g):entities.append(dict(id=id,shape=shape,material=material,geometry=g))
    tracks=[0.] if gross_beam_only else p['track_centres_y_m']
    pieces=[(0.,20.)] if gross_beam_only else [(0.,9.999),(10.001,9.999)]
    for track,y in enumerate(tracks):
        for piece,(x,L) in enumerate(pieces):
            for c in s['physical']['cells']:
                for part in c['sections']:
                    add(f'track-{track+1}/piece-{piece+1}/{part["id"]}','profile','research_concrete',at_m=[x,y,0.],points_yz_m=part['polygon_yz_m'],length_m=L)
    definitions=[]
    if not gross_beam_only:
        depth=-s['zmin_m'];foot=result['foundation'];cap=p['support']['cap_size_m'];bh=p['support']['bearing_size_m'][2]
        column_top=-depth-bh-cap[2];column_bottom=column_top-p['support']['column_height_m'];B=foot['width_m']
        for end,x in enumerate((0.,20.)):
            add(f'bent-{end+1}/footing','box','research_concrete',at_m=[x-B/2,-B/2,column_bottom-foot['thickness_m']],size_m=[B,B,foot['thickness_m']])
            add(f'bent-{end+1}/pier','cylinder','research_concrete',at_m=[x,0.,column_bottom],axis=[0.,0.,1.],radius_m=foot['column_diameter_m']/2,length_m=p['support']['column_height_m'])
            add(f'bent-{end+1}/cap','box','research_concrete',at_m=[x-cap[0]/2,-cap[1]/2,column_top],size_m=cap)
        for track,y in enumerate(tracks):
            line=result['physical_definition'].get('wayside_conductor_and_supports')
            if line:
                cy=y+line['lateral_offset_from_track_centre_m'];width=.10
                add(f'track-{track+1}/conductor','box','aluminium-stock-hypothesis',
                    at_m=[0.,cy-width/2,.22],size_m=[20.,width,line['cross_section_m2']/width])
                for j in range(20):
                    add(f'track-{track+1}/conductor-bracket-{j}','box','steel-stock-proxy',
                        at_m=[j+.43,cy-.06,.02],size_m=[.14,.12,.02])
                    add(f'track-{track+1}/conductor-insulator-{j}','box','insulator-envelope',
                        at_m=[j+.45,cy-.06,.04],size_m=[.12,.12,.18])
            for end,x in enumerate(p['support']['bearing_lines_x_m']):
                for side,dy in enumerate(p['support']['bearing_lateral_offsets_m']):
                    bx,by,bz=p['support']['bearing_size_m']
                    add(f'track-{track+1}/end-{end+1}/bearing-{side+1}','box','bearing-assembly-envelope',at_m=[x-bx/2,y+dy-by/2,-depth-bz],size_m=[bx,by,bz])
            for side,dy in enumerate(p['track_interface']['nominal_contact_centres_y_m']):
                # Approximate rail profile is geometric, explicitly not a 60E1
                # manufacturing definition or independent rail-mass evidence.
                for label,w,h,z in [('foot',.15,.02,.02),('web',.016,.11,.04),('head',p['track_interface']['nominal_rail_head_width_m'],.05,.15)]:
                    add(f'track-{track+1}/rail-{side+1}/{label}','box','rail-steel-envelope',at_m=[0.,y+dy-w/2,z],size_m=[20.,w,h])
            for side,dy in enumerate((-.91,.91)):
                add(f'track-{track+1}/drain-{side+1}','tube','HDPE',at_m=[0.,y+dy,-.21],axis=[1.,0.,0.],radius_m=.05,inner_radius_m=.045,length_m=20.)
            for i in range(ceil(20/p['fastener_pitch_m'])):
                for side,dy in enumerate(p['track_interface']['nominal_contact_centres_y_m']):
                    plate=p['fastener_plate_size_m']
                    x=i*(20-plate[0])/(ceil(20/p['fastener_pitch_m'])-1)
                    add(f'track-{track+1}/fastener-{i+1}-{side+1}/plate','box','steel',at_m=[x,y+dy-plate[1]/2,0.],size_m=plate)
            cage=result['reinforcement']['cage_path_yz_m']
            for i in range(result['reinforcement']['stirrup_count']):
                definitions.append(dict(id=f'track-{track+1}/stirrup-{i+1}',kind='bending-centreline',x_m=.06+i*result['reinforcement']['stirrup_pitch_m'],path_yz_m=[[yy+y,z] for yy,z in cage],diameter_m=.012,
                    cut_length_m=result['reinforcement']['stirrup_cut_length_m'],placement_verified=False))
            bottom_z=s['zmin_m']+.08
            bar_locations=[(yy,-.08) for yy in (-.75,-.25,.25,.75)]+[(yy,bottom_z) for yy in (-.22,-.07,.07,.22)]
            for side in (-1,1):
                for z in (-.35,-.60,-.85,-1.10):
                    yy=side*.91 if s['physical']['family']=='reference_box' else side*(.7-.45*((-z-.16)/1.08))
                    bar_locations.append((yy,z))
            for line,(yy,z) in enumerate(bar_locations):
                for piece,(lo,hi) in enumerate(((.06,5.4),(4.6,9.94),(10.06,15.4),(14.6,19.94))):
                    definitions.append(dict(id=f'track-{track+1}/longitudinal-{line+1}/cut-{piece+1}',kind='straight-bar-centreline',path_xyz_m=[[lo,y+yy,z],[hi,y+yy,z]],diameter_m=.02,placement_verified=False,
                        no_bar_crosses_segment_joint=True,cut_length_m=hi-lo))
            for duct in range(6):
                side=-1 if duct<3 else 1;dz=((duct%3)-1)*.12;path=[]
                for i in range(21):
                    x=i;z=s['centroid_z_m']-.4*4*x*(20-x)/400+dz
                    yy=side*.91 if s['physical']['family']=='reference_box' else side*(.7-.45*((-z-.16)/1.08))
                    path.append([x,y+yy,z])
                definitions.append(dict(id=f'track-{track+1}/duct-{duct+1}',kind='tendon-duct-centreline',path_xyz_m=path,outer_diameter_m=.06,
                    strands=result['prestress']['strands']//6,placement_verified=False,clash_and_bursting_check_pending=True))
        add('central-inspection-walkway','box','grating-envelope',at_m=[0.,-.5,-.08],size_m=[20.,1.,.04])
    projection=dict(schema='osr-pilot-civil-scene/1',civil_candidate_id=cid,system_candidate_id=result['system_candidate_id'],entities=entities,definition_paths=definitions,
        gross_beam_only=gross_beam_only,concrete_duct_and_rebar_voids_subtracted=False,installed_mass_from_cad_permitted=False,
        geometric_scope='Gross material stock, bearing envelopes and rail-envelope projection; bar/tendon definitions are not proven fit. Joint keys, anchors, guards and support reinforcement remain positive BOM/definition reserves.',**FLAGS)
    projection['component_geometry_id']=identity(dict(schema='osr-pilot-civil-component-geometry/1',units='m',entities=entities,definition_paths=definitions,gross_beam_only=gross_beam_only))
    return seal(projection)


def cad_case(result,*,gross_beam_only=False):
    a=scene(result,gross_beam_only=gross_beam_only)
    return dict(case_id='pilot-civil-gross' if gross_beam_only else 'pilot-civil-assembly',candidate_id=result['civil_candidate_id'],component_geometry_id=a['component_geometry_id'],entities=a['entities'],
        source_evaluation_id=result['evaluation_id'],materials={'research_concrete':dict(density_kg_m3=2500.),'steel':dict(density_kg_m3=7850.)},**FLAGS)


def parts(result):
    """Non-additive fabrication and installation schedule tied to cost owners."""
    r=result['reinforcement'];t=result['prestress'];q=result['quantities'];foot=result['foundation'];cost=result['cost']
    def part(id,qty,unit,material,process,inspection,**fields):
        return dict(id=id,quantity_each_beam_or_bent=qty,unit=unit,material=material,process=process,inspection=inspection,**fields)
    items=[
        part('beam/precast-segment',2,'pieces','Research C50-class concrete; certificate and release strength pending','Reusable match-cast mould; place cage and ducts; pour/vibrate/cure; survey and inspect before release','Geometry, cover, voids, batch and measured release strength',scope='each beam',gross_concrete_m3=q['concrete_beam_m3'],cost_owner='civil/precast-factory'),
        part('beam/longitudinal-bar-cut',r['longitudinal_cut_pieces'],'pieces','B500-class steel hypothesis','Cut; two overlapping pieces per line in each segment. No rebar crosses match-cast joint.','Bar identity, cut length, lap/cover and engineer-approved anchorage',cut_length_m=r['longitudinal_cut_length_m'],diameter_m=r['longitudinal_diameter_m'],scope='each beam',cost_owner='civil/precast-factory'),
        part('beam/stirrup',r['stirrup_count'],'pieces','B500-class steel hypothesis','Cut/bend closed rectangular or trapezoidal hoops; attach to cage.','Bend radius, tails, pitch, cover and congestion',cut_length_m=r['stirrup_cut_length_m'],diameter_m=r['stirrup_diameter_m'],scope='each beam',cost_owner='civil/precast-factory'),
        part('beam/prestress-strand',t['strands'],'pieces','1860 MPa-class strand hypothesis','Cut with 0.6 m working tail each end; thread, symmetric jack, anchor, trim and grout.','Strand identity, jack calibration, elongation, locking loss, grout coverage',cut_length_m=t['strand_stock_cut_length_m_each'],installed_length_m=t['tendon_length_m_each'],scope='each beam',cost_owner='civil/precast-factory'),
        part('beam/duct',6,'20 m paths','Corrugated sealed duct candidate','Form curved route, support at 1 m, join and pressure/leak inspect.','Geometry, cover, continuity and tendon clearance',outer_diameter_m=.06,scope='each beam',cost_owner='civil/ducts-grout-chairs-endzone'),
        part('beam/anchor-group',12,'end groups','Steel wedge/anchor plate system hypothesis','Recess, install plate and local bursting cage; jack and lock strands.','Anchor bearing, bursting, fatigue and cover require independent detailed design',total_mass_reserve_kg=t['anchorage_mass_kg'],scope='each beam',cost_owner='civil/precast-factory'),
        part('beam/matchcast-joint',1,'interface','Controlled 2 mm epoxy candidate','Matched female/male shear keys, surface preparation, fit and controlled epoxy layer; continuously post-tension.','Fit, key bearing/shear, epoxy cure and joint opening; geometry/detail remains unverified',positive_local_detail_reserve=True,scope='each beam',cost_owner='civil/segment-joints'),
        part('beam/bearing',4,'assemblies','Elastomer/steel bearing candidate','Prepare level seat, place guided/free/fixed arrangement only after detailed movement study.','Pressure, rotation, shear, restraint and replacement access',size_m=result['physical_definition']['bearing_layout']['size_m'],scope='each beam',cost_owner='civil/bearings'),
        part('track/fastener',result['physical_definition']['rail_interface']['fastenings'],'sets','Steel plate/anchors; spring clips, elastomer pad, nuts/washers','Drill/place anchors; level rail; torque and mark.','Gauge, alignment, clamp force, torque and pull-out',anchors_each=4,plate_size_m=result['policy']['fastener_plate_size_m'],scope='each beam',cost_owner=['civil/fastening-steel','civil/fastening-clips-pads-nuts-washers']),
        part('track/rail',2,'20 m runs','60.21 kg/m rail stock hypothesis','Cut, join with independently designed thermal-movement and electrical-continuity interfaces.','Profile, straightness, rail stress, weld/bolted joint and gauge',scope='each beam',cost_owner='civil/rails'),
        part('support/footing',1,'cast assembly','Reinforced concrete with unlocated 90/130/190 kg/m3 steel reserve','Excavate, verify ground, blinding, cage, cast and cure.','Ground, groundwater, reinforcement, punching, settlement and concrete strength',size_m=[foot['width_m'],foot['width_m'],foot['thickness_m']],scope='each shared bent',cost_owner='civil/shared-pier-foundation'),
        part('support/pier-cap',1,'assembly','Reinforced concrete with positive bar reserve','Reusable formwork; cage, cast/cure and survey.','Connections, local bearing, cracking, lateral/seismic and access',pier_diameter_m=foot['column_diameter_m'],pier_height_m=result['policy']['support']['column_height_m'],cap_size_m=result['policy']['support']['cap_size_m'],scope='each shared bent',cost_owner='civil/shared-pier-foundation')]
    line=result['physical_definition'].get('wayside_conductor_and_supports')
    if line:
        items.append(part('track/wayside-conductor',20,'track-m','Aluminium conductor + positive steel/insulator/guard reserve',
            'Cut, support on isolated brackets, provide engineered expansion/bonding, guards and sectional isolation.',
            'Contact clearance, dielectric, bond continuity, ampacity and touch protection remain unverified',
            conductor_area_m2=line['cross_section_m2'],mass_kg_each_track_m=line['cross_section_m2']*line['density_kg_m3_hypothesis']+line['insulators_brackets_guards_mass_kg_track_m_hypothesis'],
            scope='each beam; included in civil dead load once',cost_owner='wayside-propulsion in whole-system ledger'))
    return dict(schema='osr-pilot-civil-parts/1',civil_candidate_id=result['civil_candidate_id'],beam_instances=cost['beams'],shared_bent_instances=cost['shared_bents'],items=items,
        additive_mass_or_cost_ledger=False,reason='Manufacturing decomposition references existing quantity and cost owners; adding these rows again would double-count.',controlled_drawings_complete=False,**FLAGS)
