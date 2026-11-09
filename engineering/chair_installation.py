"""Source-only research recipe for a direct-floor chair and structural hardpoints.

No import-time producer, native execution, canonical-body mutation or selection.
``compile_proposal`` is a future, explicitly requested *definition* trial; its
output is a typed patch proposal, never an installed or qualified body receipt.
Lengths are metres; local u points to the aisle, v follows the parent's stored
rotation, w points up. All fabrication geometry and properties are hypotheses.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from math import acos, isclose, isfinite, pi, prod, sqrt
from pathlib import Path
import gzip
import json


SCHEMA = "osr.chair-installation-proposal/1"
PARENT = {
    "candidate_id": "5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3",
    "evaluation_id": "d1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea",
    "raw_sha256": "f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23",
    "decoded_canonical_sha256": "8e83b928b18042a727aa1c45e75c43da1313bbd230db1ba3c6bd8d9925626833",
}
R1 = {
    "fitout_candidate_id": "104972006cfeb390e8b191c26c103b57f8905997cf673ddf2f20141ccc8b01f3",
    "geometry_id": "b6d9b03015c733d5101d0569248ae12f57c26cd25a8a389ff16e1bd9f5661673",
    "independent_datum_review_id": "e62ce6db3d48b36d70ed6efccbf47a23defd3fba68dc23337cddf3ed3bbb9918",
    "native_evidence_inherited": False,
    "r2_frozen_source_commit": "f0f72a38aaf28399b2af7aaf23d25d0d22727539",
    "r2_band_source_commit": "2f90439e79596b9dd07ca8611ad23e619f3b29cb",
    "r2_failed_band_evaluation_id": "7810c5bd7c8fc0e33bf2ec46008993c98b46f4d88081363d496e782e74c6f9eb",
    "r3_frozen_source_commit": "1eb05e4e10f2f2029d881c65d43e6f758fcb3dbb",
    "r3_independent_review_id": "62a1cbd9772962107dbd96fd154793e97cb8e74681eb9529ad64c06dd87a4ef8",
    "r3_cap_overlap_witness_sha256": "4bf888e07e76deb771f140c4a1fe398705e439c3a9ac2029ca2b2f7e73448046",
}
P6_COUNTERPART = dict(candidate_id="ce1b8b222b06a6479f7738d9409d74a5333514b79b7baf5dffc7c8510b73e044",
    evaluation_id="3202ebbf3b6ca827bde78466c5047734fdc3b53fb8a70330744026b9f280467a",
    raw_sha256="b8637bce668ff07ab5b1c7378cbfc308981c1d91d2a07c6a41e1a7b4dde00d40",
    admitted=False)
I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
CASES = ("low", "base", "high")
OLD_PARTS = tuple("body/chair-" + n for n in (
    "base", "frame", "pan", "back", "cushion", "upholstery", "armrest",
    "anchor-track", "anchor-bolt", "anchor-nut", "anchor-washer",
    "shell-bolt", "shell-nut", "shell-washer"))
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False,
             native_evaluator_admitted=False, installed_mass_complete=False)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _positive(values):
    if not all(isfinite(x) and x > 0 for x in values):
        raise ValueError("finite positive dimension required")


def transform(point, origin, rotation):
    """Explicit rigid transform; reflection/scaling are not chair handedness."""
    for i in range(3):
        for j in range(3):
            if not isclose(sum(rotation[k][i] * rotation[k][j] for k in range(3)),
                           float(i == j), abs_tol=1e-10):
                raise ValueError("rotation must be orthonormal")
    a = rotation
    det = (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
           - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
           + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))
    if not isclose(det, 1., abs_tol=1e-10):
        raise ValueError("reflection is not a rigid chair rotation")
    return [origin[i] + sum(a[i][j]*point[j] for j in range(3)) for i in range(3)]


def box(name, center, size, material, bores=()):
    """Bores are through the named axis, with absolute component-local centres."""
    _positive(size)
    for h in bores:
        _positive([h["diameter_m"]])
        if not 0 < h.get("depth_m", size[h["axis"]]) <= size[h["axis"]]+1e-12:
            raise ValueError("blind bore exceeds material depth")
        q = [i for i in range(3) if i != h["axis"]]
        if any(abs(h["center_m"][i]-center[i])+h["diameter_m"]/2 > size[i]/2+1e-12 for i in q):
            raise ValueError("bore breaks a blank edge; use a controlled open cutout instead")
    return dict(id=name, shape="box", center_m=list(center), size_m=list(size),
                material=material, bores=deepcopy(list(bores)))


def bore(axis, center, diameter):
    if axis not in (0, 1, 2):
        raise ValueError("bore axis")
    return dict(axis=axis, center_m=list(center), diameter_m=diameter)


def tube(name, axis, center, length, widths, wall, material, bores=()):
    """Four disjoint RHS walls. Paired wall holes remove real material.

    Widths follow the two increasing transverse axes. Sharp corners are a
    declared stock hypothesis; purchased radii and weld HAZ are not validated.
    """
    _positive([length, *widths, wall])
    if 2*wall >= min(widths):
        raise ValueError("RHS wall consumes void")
    q, out = [i for i in range(3) if i != axis], []
    for k in (0, 1):
        normal, other = q[k], q[1-k]
        for sign in (-1, 1):
            c, size = list(center), [0., 0., 0.]
            c[normal] += sign*(widths[k]-wall)/2
            size[axis], size[normal] = length, wall
            size[other] = widths[1-k] if k == 0 else widths[1-k]-2*wall
            holes = [h for h in bores if h["axis"] == normal]
            out.append(box(f"{name}/wall-{normal}-{sign}", c, size, material, holes))
    return out


def cylinder(name, axis, start, length, radius, material, inner_radius=0.):
    _positive([length, radius])
    if not 0 <= inner_radius < radius:
        raise ValueError("invalid annulus")
    return dict(id=name, shape="cylinder", axis=axis, start_m=list(start),
                length_m=length, radius_m=radius, inner_radius_m=inner_radius,
                material=material)


def volume_centroid(entity):
    if entity["shape"] == "box":
        v = prod(entity["size_m"])
        moment = [v*x for x in entity["center_m"]]
        for h in entity["bores"]:
            depth = h.get("depth_m", entity["size_m"][h["axis"]])
            removed = pi*(h["diameter_m"]/2)**2*depth
            hc = list(h["center_m"]); hc[h["axis"]] = entity["center_m"][h["axis"]]
            if "depth_m" in h:
                hc[h["axis"]] += h["entry_face"]*(entity["size_m"][h["axis"]]-depth)/2
            v -= removed
            moment = [moment[i]-removed*hc[i] for i in range(3)]
        if v <= 0:
            raise ValueError("nonpositive net material")
        return v, [x/v for x in moment]
    if entity["shape"] == "cylinder":
        v = pi*(entity["radius_m"]**2-entity["inner_radius_m"]**2)*entity["length_m"]
        c = list(entity["start_m"]); c[entity["axis"]] += entity["length_m"]/2
        return v, c
    raise ValueError("unknown material primitive")


def bounds(entity):
    if entity["shape"] == "box":
        return [[entity["center_m"][i] + s*entity["size_m"][i]/2 for i in range(3)] for s in (-1, 1)]
    a, c = entity["axis"], entity["start_m"]
    return [[c[i] + (0 if s < 0 else entity["length_m"]) if i == a
             else c[i] + s*entity["radius_m"] for i in range(3)] for s in (-1, 1)]


def stock_row(piece, entities, gross_volume_m3, process_hours, qa_hours, basis):
    """Named stock owns exactly these solids; procurement includes trim/drill loss."""
    if not entities or len({e["material"] for e in entities}) != 1:
        raise ValueError("one material and positive named stock required")
    net = sum(volume_centroid(e)[0] for e in entities)
    if gross_volume_m3 < net-1e-12 or min(process_hours, qa_hours) < 0:
        raise ValueError("negative scrap or labour")
    return dict(id=piece, material=entities[0]["material"], entity_ids=[e["id"] for e in entities],
                net_volume_m3=net, gross_volume_m3=gross_volume_m3,
                scrap_volume_m3=gross_volume_m3-net, process_hours=process_hours,
                qa_hours=qa_hours, basis=basis, tooling_allocation_usd=None)


def hardware_stack(name, axis, center, direction, layers, bolt_length, diameter,
                   head_thickness, nut_thickness, washer_thickness=.0016):
    """Signed washer/bolt/nut geometry. ``center`` is bearing face under head.

    Layers run from the head-side joint face to the nut-side joint face. Threads
    and hex flats are unmodelled; cylindrical blanks bound material/clearance.
    This checks nominal stack, not preload, thread strength or fatigue.
    """
    if direction not in (-1, 1) or axis not in (0, 1, 2):
        raise ValueError("signed fastener axis")
    _positive([bolt_length, diameter, head_thickness, nut_thickness, washer_thickness])
    if not layers or any(x[1] <= 0 for x in layers):
        raise ValueError("positive named grip layers required")
    grip = sum(x[1] for x in layers)
    projection = bolt_length - washer_thickness - grip - washer_thickness - nut_thickness
    if projection < .002-1e-12:
        raise ValueError("bolt does not project through complete nut")
    def solid(label, start_distance, length, radius, inner=0.):
        p = list(center)
        # cylinder is always stored along positive component axis
        p[axis] += direction*start_distance + (0 if direction > 0 else -length)
        return cylinder(name+"/"+label, axis, p, length, radius, "steel", inner)
    washer_radius = .008 if diameter >= .008 else .006
    entities = [solid("head-blank", -head_thickness, head_thickness, diameter*.94),
                solid("shank-thread-blank", 0, bolt_length, diameter/2),
                solid("head-washer", 0, washer_thickness, washer_radius, diameter*.54),
                solid("nut-washer", washer_thickness+grip, washer_thickness, washer_radius, diameter*.54),
                solid("nut-blank", 2*washer_thickness+grip, nut_thickness, diameter*.94, diameter/2)]
    return dict(id=name, axis=axis, direction=direction, head_bearing_face_m=list(center),
                grip_layers_m=[dict(id=k, length_m=v) for k, v in layers],
                bolt_underhead_length_m=bolt_length, nominal_thread_projection_m=projection,
                entities=entities, pieces=dict(bolts=1, nuts=1, washers=2),
                qualification="thread profile, grade authentication, torque/preload, locking, corrosion and fatigue pending",
                tool_envelope=dict(socket_radius_m=.025, insertion_m=.10,
                                   head_axis=axis, head_direction=-direction, nut_direction=direction,
                                   finite_sweep_required=True, accepted=False))


def beam_bound(span, point_loads, E, width, depth, wall, allowable_stress):
    """Conservative all-load-at-midspan bound for a simply supported elastic RHS.

    It intentionally omits support fixity, shear/local buckling, openings, welds,
    prying, endplate flexibility, dynamic amplification beyond supplied loads,
    fatigue and parent stub/cleat strength. A pass is not structural acceptance.
    """
    _positive([span, E, width, depth, wall, allowable_stress])
    if 2*wall >= min(width, depth) or any(x < 0 for x in point_loads):
        raise ValueError("invalid section/load domain")
    second = (width*depth**3-(width-2*wall)*(depth-2*wall)**3)/12
    force = sum(point_loads)
    return dict(span_m=span, total_vertical_load_N=force, second_m4=second,
                stress_bound_Pa=force*span/4*depth/2/second,
                deflection_bound_m=force*span**3/(48*E*second),
                stress_residual_Pa=allowable_stress-force*span/4*depth/2/second,
                qualified=False, domain="linear-elastic simply-supported necessary bound only")


def chair_support_bounds(loads, row_v, E=69e9, allowable_stress=60e6,
                         foot_thickness=.004, leg_length=.3935, foot_band_width=.110):
    """Fixture screening hypotheses, not an authenticated chair load standard.

    Compression/tension is forced through counted anchor sleeves, not a free
    skin/core foundation. A conservative cantilever *band hypothesis* diagnoses
    the eccentric flat foot; an actual two-dimensional plate/contact model may
    differ. Do not promote a negative residual to a universal seating rule.
    """
    _positive([E,allowable_stress,foot_thickness,leg_length,foot_band_width,
               loads["occupant_kg"],loads["provisional_chair_kg"],
               loads["gravity_m_s2"],loads["vertical_factor"]])
    mass=loads["occupant_kg"]+loads["provisional_chair_kg"]
    gravity=loads["gravity_m_s2"]
    compression=mass*gravity*loads["vertical_factor"]/4
    horizon=mass*gravity*max(loads["longitudinal_factor"],loads["lateral_factor"])
    moment=horizon*loads["overturning_height_above_floor_m"]
    spacing=min(.265,abs(row_v[1]-row_v[0]))
    _positive([spacing])
    uplift=moment/(2*spacing)  # no beneficial weight credited
    eccentricity=(.055**2+max(abs(v-s*.12) for v,s in zip(row_v,(-1,1)))**2)**.5
    foot_stress=6*max(compression,uplift)*eccentricity/(foot_band_width*foot_thickness**2)
    area=.025**2-.021**2
    second=(.025**4-.021**4)/12
    euler=pi*pi*E*second/leg_length**2  # pin-pin idealisation; no HAZ/joints
    return dict(leg_compression_each_N=compression, no_weight_credit_uplift_each_N=uplift,
        leg_axial_stress_Pa=compression/area, ideal_pin_column_euler_N=euler,
        foot_eccentricity_m=eccentricity, foot_thickness_m=foot_thickness,leg_length_m=leg_length,
        foot_band_stress_Pa=foot_stress,
        foot_band_stress_residual_Pa=allowable_stress-foot_stress,
        fixture_band_screen_passed=foot_stress <= allowable_stress,
        constructive_followup="if band residual is negative, design counted ribs/thicker foot and update continuous leg/bolt stack, or independently substantiate actual plate/contact load sharing; do not credit unknown floor core",
        model_domain="proposed preliminary load/elastic strip and pin-column fixture screens only; no joint, plate-contact, fatigue, crash or strength qualification",
        qualified=False)


def owner_map(seats, pitch=.48):
    """One shared rest for each adjacent pair, owned by lower *global X* seat.

    Large gaps are retained as door/WC/row-end openings; no terminal rest is
    inserted into a wheelchair bay. Count changes must be explicit replacements.
    """
    out, seen = [], set()
    for car, side in sorted({(s["car"], s["side"]) for s in seats}):
        row = sorted((s for s in seats if (s["car"], s["side"]) == (car, side)),
                     key=lambda s: s["origin_m"][0])
        for left, right in zip(row, row[1:]):
            dx = right["origin_m"][0]-left["origin_m"][0]
            if isclose(dx, pitch, abs_tol=1e-8):
                key = (left["id"], right["id"])
                if key in seen:
                    raise ValueError("duplicate shared armrest")
                seen.add(key)
                out.append(dict(id="rest@"+left["id"], owner=left["id"], neighbour=right["id"],
                                local_v_sign=side, reason="same contiguous row, one physical shared rest"))
            elif dx < pitch-1e-8:
                raise ValueError("seat pitch smaller than retained envelope")
    return out


def choose_anchor_rows(origin, rotation, stub_x, pad_half_x=.010, margin=.005):
    """Two deterministic drilling alternatives per row; stubs are actual 100mm X.

    Checks only backing pad versus stub plan geometry, including a proposed
    margin. It does not waive finite tools, P6 movement, actual joints or strength.
    """
    selected = []
    for row in (-1, 1):
        options = []
        for local_v in (row*.12-.07, row*.12+.07):
            local = [[u, local_v, -.45] for u in (-.1325, .1325)]
            world = [transform(p, origin, rotation) for p in local]
            gap = min(abs(p[0]-x)-.05-pad_half_x for p in world for x in stub_x)
            options.append((gap, local_v, world))
        gap, local_v, world = max(options, key=lambda x: (x[0], -x[1]))
        if gap < margin-1e-10:
            raise ValueError("no floor-anchor drilling option clears actual stub plus pad margin")
        selected.append(dict(row=row, local_v_m=local_v, axes_world_m=world,
                             pad_stub_gap_m=gap, claimed_scope="nominal necessary plan bound"))
    return selected


def node_interface(lane_y, counterpart_depth_m=.100):
    """Typed100/120mm interface recipe; no body or geometry producer.

    The bolt column is40mm inboard of the rail. Node hardware is accessible
    beside the closed RHS rather than penetrating its bottom wall/nearby floor
    backers. A120mm P6 counterpart does NOT inherit100mm sleeve/stack geometry.
    """
    if counterpart_depth_m not in (.100,.120) or lane_y == 0:
        raise ValueError("explicit100/120mm paired floor counterpart required")
    sign=1 if lane_y > 0 else -1
    relief=counterpart_depth_m == .120 and abs(lane_y)+.030 > 1.080
    inner=lane_y-sign*.070
    outer=sign*1.080 if relief else lane_y+sign*.030
    width=abs(outer-inner);center=(inner+outer)/2
    return dict(counterpart_depth_m=counterpart_depth_m,
        counterpart_wall_m=.006 if counterpart_depth_m == .100 else .008,
        counterpart_source=deepcopy(PARENT if counterpart_depth_m == .100 else P6_COUNTERPART),
        counterpart_mating_resolved=True,
        counterpart_weld_relief_required=relief,
        counterpart_weld_detail="full-through outboard edge notch at absY1.080,6mm clear of actual radius4mm weld; counted internal12mm diaphragm restores outer-wall transfer before partial end weld" if relief else "outside actual P6 endcap weld Yrange or retained P1 counterpart",
        bridge_lane_y_m=lane_y,bolt_column_y_m=lane_y-sign*.040,
        plate_center_y_m=center,plate_size_m=[.010,width,.080],
        plate_gross_blank_size_m=[.010,.104,.084],
        plate_outboard_notch_width_m=.100-width,
        weld_to_plate_y_gap_m=.006 if relief else None,
        internal_diaphragm_required=relief,
        plate_thickness_m=.010,bolt_z_m=[1.0535,1.0855],
        sleeve_length_m=counterpart_depth_m,
        bolt_underhead_length_m=counterpart_depth_m+.040,
        grip_m=counterpart_depth_m+.021,
        thread_projection_m=.0093,cap_wall_length_m=.016,
        dimensional_hypotheses=dict(bolt_length_m=.001,counterpart_depth_m=.001,
            two_plates_m=.0005,two_isolators_m=.0001,two_washers_m=.0002,nut_m=.0002,
            total_projection_m=.003,cap_length_m=.0005,cap_installation_m=.00025),
        minimum_thread_projection_m=.0063,minimum_cap_tip_space_m=.00295,
        node_tool=dict(head_radius_m=.010,head_length_m=.040,hex_across_flats_m=.0132,
            stem_radius_m=.005,stem_length_m=.050,workshop_quantity=2,
            positive_procurement_allowance_usd=[10.,24.,60.],
            interface="source-sized socket hypothesis, tool strength/torque and supplier dimensions unverified; not installed mass"),
        qualified=False)


def endplate_band_bound(vertical_N, longitudinal_N, lateral_N, thickness_m,
                       offset_m=.040, allowable_Pa=60e6):
    """Necessary elastic net-band/bolt-group comparison at unchanged loads.

    Actual simple-support reaction envelopes must be supplied. Both9mm plate
    bores are deducted from the80mm band. The rail/bolt-group10mm Z eccentricity
    is taken as an axial bolt-group moment, not discarded or replaced by a load
    reduction. Local prying/contact/HAZ/fatigue remain outside this model.
    """
    _positive([thickness_m,offset_m,allowable_Pa])
    if min(vertical_N,longitudinal_N,lateral_N) < 0:
        raise ValueError("nonnegative reaction envelope required")
    h=.080-2*.009; z_ecc=.010; spacing=.032
    plane=6*vertical_N*offset_m/(thickness_m*h*h)
    normal=6*longitudinal_N*offset_m/(h*thickness_m**2)
    direct=(longitudinal_N+lateral_N)/(h*thickness_m)
    shear=(vertical_N**2+lateral_N**2)**.5/(h*thickness_m)
    equivalent=((plane+normal+direct)**2+3*shear**2)**.5
    couple=(vertical_N*offset_m+lateral_N*z_ecc)/spacing
    bolt_shear=((vertical_N/2)**2+(lateral_N/2+couple)**2)**.5
    bolt_axial=longitudinal_N/2+longitudinal_N*z_ecc/spacing
    bolt_shear_stress=bolt_shear/36.6e-6;bolt_axial_stress=bolt_axial/36.6e-6
    interaction=(bolt_shear_stress/160e6)**2+(bolt_axial_stress/240e6)**2
    plate_bearing=bolt_shear/(.009*thickness_m)
    return dict(vertical_reaction_N=vertical_N,longitudinal_reaction_N=longitudinal_N,
        lateral_reaction_N=lateral_N,offset_m=offset_m,net_band_height_m=h,thickness_m=thickness_m,
        in_plane_bending_Pa=plane,normal_bending_Pa=normal,direct_Pa=direct,
        equivalent_comparison_Pa=equivalent,stress_residual_Pa=allowable_Pa-equivalent,
        bolt_shear_each_N=bolt_shear,bolt_axial_each_N=bolt_axial,
        bolt_interaction_ratio=interaction,plate_bearing_Pa=plate_bearing,
        necessary_screen_passed=equivalent <= allowable_Pa and plate_bearing <= allowable_Pa and interaction <= 1.,
        bolt_allowable_hypothesis="160MPa shear/240MPa axial on36.6mm2root area, not authenticated8.8hardware or railway qualification",
        model_domain="net-band elastic plate plus declared bolt-group equilibrium; local stress/plate contact/prying/HAZ/crash/fatigue not qualified",qualified=False)


def circle_segment_area(radius_m, height_m):
    """Exact circular segment; used to retain the positive R3 failure witness."""
    _positive([radius_m])
    if not 0 <= height_m <= 2*radius_m:
        raise ValueError("segment outside circle")
    return radius_m**2*acos((radius_m-height_m)/radius_m)-(radius_m-height_m)*sqrt(max(0.,2*radius_m*height_m-height_m**2))


def node_neighbor_bounds(interface, anchor_from_node_m):
    """Necessary nominal intervals; no mate exemption or installed acceptance."""
    half=interface["counterpart_depth_m"]/2;t=interface["plate_thickness_m"]
    return dict(node_column_inboard_m=.040,
        largest_node_ring_to_floor_backer_y_gap_m=.040-.009-.025,
        cap_to_floor_sleeve_y_gap_m=.040-.006-.007,
        largest_node_ring_to_rail_y_gap_m=.040-.009-.020,
        node_socket_to_rail_y_gap_m=.040-interface["node_tool"]["head_radius_m"]-.020,
        endplate_to_floor_backer_x_gap_m=anchor_from_node_m-.010-half-t,
        source_endcap_to_rail_x_gap_m=t,
        P6_actual_endcap_weld_to_endplate_nominal_residual_m=interface["weld_to_plate_y_gap_m"],
        frame_relative_proposed_margin_m=.005,
        zero_acceptance=True,
        external_weld_halo_m=.003,
        weld_floor_gap_at_85mm_anchor_m=.085-.010-half-t-.003,
        tolerance_domain="5mm proposed global sum retained; local weld/anchor shared-jig tolerances and actual bead/tool/removal geometry require explicit downstream verification, no clearance waiver")


def diaphragm_station(span, side, occupied=()):
    """A single necessary gap placement, not an architecture/parameter search."""
    a,b=span["support_face_x_m"]
    intervals=[(a+.020,b-.020)]
    blocked=[(h["at_m"][0]-.024,h["at_m"][0]+.024) for h in span["anchors"]]
    blocked += [(x-.020,x+.020) for x in occupied]
    for left,right in sorted(blocked):
        remaining=[]
        for lo,hi in intervals:
            if right <= lo or left >= hi:remaining.append((lo,hi))
            else:
                if lo < left:remaining.append((lo,min(hi,left)))
                if right < hi:remaining.append((max(lo,right),hi))
        intervals=remaining
    intervals=[(lo,hi) for lo,hi in intervals if hi-lo>.000002]
    if not intervals:raise ValueError("no12mmdiaphragm gap clears actual floor sleeves,weld halo and end tools")
    target=a+.050 if side < 0 else b-.050
    choices=[max(lo+.000001,min(hi-.000001,target)) for lo,hi in intervals]
    at=min(choices,key=lambda x:(abs(x-target),x))
    return dict(x_m=at,thickness_m=.012,
        min_sleeve_weld_gap_m=min(abs(at-h["at_m"][0])-.006-.003-.0071 for h in span["anchors"]),
        min_backer_weld_plan_gap_m=min(abs(at-h["at_m"][0])-.006-.003-.010 for h in span["anchors"]),
        source_anchor_ids=[h["id"] for h in span["anchors"]],
        datum="actual rail faces; avoid actual anchor sleeve/backer plus6mmhalfplate+3mmweld+5mmmargin")


def diaphragm_band_bound(vertical_N,longitudinal_N,lateral_N):
    """Conservative full node reaction assigned to each added12mm diaphragm."""
    width,height,t=.034,.054,.012
    inplane=6*vertical_N*width/(t*height**2)
    normal=6*longitudinal_N*width/(height*t*t)
    direct=(longitudinal_N+lateral_N)/(width*t)
    shear=vertical_N/(width*t)
    eq=((inplane+normal+direct)**2+3*shear**2)**.5
    return dict(thickness_m=t,equivalent_comparison_Pa=eq,residual_Pa=60e6-eq,
        necessary_screen_passed=eq<=60e6,qualified=False,
        model_domain="full node reaction on simple34x54mm net plate band, no local contact/HAZ/fatigue qualification")


def bridge_reactions(plans, vertical_per_anchor_N, longitudinal_per_anchor_N, lateral_per_anchor_N):
    """Exact statics in the declared pin-support domain at source anchor poses."""
    out={}
    for plan in plans:
        for span in plan["spans"]:
            a,b=span["support_face_x_m"]
            for h in span["anchors"]:
                x=h["at_m"][0]
                if not a <= x <= b:
                    raise ValueError("anchor outside actual counterpart/plate support faces")
                for node_x,fraction in ((span["left_stub_x_m"],(b-x)/(b-a)),
                                        (span["right_stub_x_m"],(x-a)/(b-a))):
                    key=(span["lane_y_m"],node_x)
                    row=out.setdefault(key,dict(lane_y_m=key[0],node_x_m=key[1],vertical_N=0.,longitudinal_N=0.,lateral_N=0.))
                    for name,force in (("vertical_N",vertical_per_anchor_N),("longitudinal_N",longitudinal_per_anchor_N),("lateral_N",lateral_per_anchor_N)):
                        row[name]+=force*fraction
    return [out[k] for k in sorted(out)]


def bridge_plan(anchors, stub_x, lane_y, counterpart_depths=None):
    """Source-owned span/node plan. Nodes share two bolts across adjacent spans.

    ``stub_x`` are centres of the source 100mm-wide members. An anchor above a
    stub needs a separately designed direct insert; this family rejects it.
    """
    stations = sorted(set(stub_x))
    depths={x:.100 for x in stations}
    for x,d in (counterpart_depths or {}).items():
        if x not in depths or d not in (.100,.120):
            raise ValueError("counterpart depth requires exact reviewed station binding")
        depths[x]=d
    if len(stations) < 2:
        raise ValueError("two physical supports required")
    spans = {}
    for anchor in anchors:
        x = anchor["at_m"][0]
        left = [p for p in stations if p+depths[p]/2 < x-.010-.005]
        right = [p for p in stations if p-depths[p]/2 > x+.010+.005]
        if not left or not right:
            raise ValueError("anchor has no adjacent supported bridge bay")
        a, b = max(left), min(right)
        if stations.index(b) != stations.index(a)+1:
            raise ValueError("anchor overlaps an actual intermediate stub")
        key = (a, b)
        spans.setdefault(key, []).append(anchor)
    nodes = {}
    out = []
    for (a, b), loads in sorted(spans.items()):
        a_face=a+depths[a]/2+.010;b_face=b-depths[b]/2-.010
        length = b_face-a_face
        if length <= .05:
            raise ValueError("bridge bay cannot fit two10mm endplates")
        if any(min(h["at_m"][0]-a_face,b_face-h["at_m"][0]) < .0121-1e-10 for h in loads):
            raise ValueError("anchor bore lacks proposed bridge-end ligament")
        out.append(dict(id=f"bridge/{lane_y:.7f}/{a:.7f}/{b:.7f}", lane_y_m=lane_y,
                        left_stub_x_m=a, right_stub_x_m=b, rail_length_m=length,
                        rail_center_m=[(a_face+b_face)/2, lane_y, 1.0795],
                        support_face_x_m=[a_face,b_face],left_counterpart_depth_m=depths[a],right_counterpart_depth_m=depths[b],
                        anchors=loads, section_m=[.040, .060, .003]))
        nodes.setdefault(a, set()).add("right")
        nodes.setdefault(b, set()).add("left")
    return dict(spans=out, nodes=[dict(stub_x_m=x, lane_y_m=lane_y,interface=node_interface(lane_y,depths[x]),
                connected_sides=sorted(sides), through_bolt_sets=2,
                backing_plate_count=2-len(sides), compression_sleeves=2,
                bore_diameter_m=.0142, sleeve_outer_m=.014, sleeve_inner_m=.009,
                sleeve_length_m=depths[x], hole_world_z_m=[1.0535, 1.0855])
                for x, sides in sorted(nodes.items())])


def recipe_input():
    """Frozen input proposal only; returning it performs no candidate definition."""
    return dict(schema=SCHEMA, family="research/direct-floor-chair-r4", parent=deepcopy(PARENT),
                ancestry=deepcopy(R1), units="m, kg, N, Pa, person-hour, USD",
                fixed=dict(cars=6, car_length_m=17., chairs=264, wheelchair_places=12,
                    floor_top_m=1.15, chair_origin_m=1.60, extra_body_lift_m=0.,
                    passenger_cg_z_m=1.70, passenger_cg_uncertainty_z_m=.15,
                    passenger_loading_meaning="retained normal-minus-tare point-mass hypothesis, already lifted; not measured seated anatomy",
                    seat_xy_handing="unchanged actual P1 chair-frame patterns", doors_and_wc="retained without new end armrests"),
                geometry=dict(leg_length_m=.3775, leg_bottom_local_m=-.430,
                    foot_size_m=[.110, .170, .020], foot_center_u_m=.1625,
                    floor_bolt_underhead_length_m=.140,
                    anchor_strip_size_m=[.455, .190, .003], anchor_strip_v_m=.12,
                    side_rhs_length_m=.4575, side_rhs_center_u_m=-.02875,
                    backpost_u_m=-.245, pan_skin_m=.0015, pan_core_m=.0116,
                    skin_core_bondline_m=.0002,
                    sandwich_thickness_m=.015, seat_foam_m=.045, back_foam_m=.045,
                    seat_foam_depth_m=.4365, back_foam_height_m=.558,
                    foam_gross_cutset_m=[.460, 1.050, .045], trim_thickness_m=.001,
                    trim_retaining_strap_width_m=.025, trim_retaining_strap_u_m=.080,
                    bridge_section_m=[.040, .060, .003],node_column_inboard_m=.040,
                    node_plate_size_m=[.010,.100,.080],P6_weld_relief_abs_y_m=1.080,
                    P6_internal_diaphragm_size_m=[.012,.034,.054]),
                counterpart_variants=dict(P1_depth_m=.100,P6_depth_m=.120,P6_source=deepcopy(P6_COUNTERPART),
                    P6_header_ids="header/{ysign}/{hx}, hx=-0.4/+0.5; exact48counterpart mapping required",
                    P6_header_endcap_y_abs_m=[1.090,1.098],P6_header_z_m=[.9295,1.1095],
                    P6_transform="front T; rear T@diag(-1,-1,1); no additional body lift; source-local gate not admitted"),
                materials=dict(
                    al6005a=dict(density_kg_m3=2710., E_Pa=69e9, allowable_Pa=60e6,
                        rate_usd_kg=[2.5, 4., 6.5], basis="parent aluminium rates; 60MPa provisional welded necessary screen, not certified HAZ allowable"),
                    al5083=dict(density_kg_m3=2660., rate_usd_kg=[2.5, 4., 6.5], basis="parent aluminium rate hypothesis"),
                    steel=dict(density_kg_m3=7850., rate_usd_kg=[.5, .8, 1.2], basis="parent S355/fastener stock rates, authentication and purchased finishing held"),
                    gfrp=dict(density_kg_m3=1800., rate_usd_kg=[5., 9., 16.], basis="new calculated outline allowance; laminate/FR grade unknown"),
                    pet=dict(density_kg_m3=80., rate_usd_kg=[4., 8., 16.], basis="new closed-cell core hypothesis; creep/fire unknown"),
                    foam=dict(density_kg_m3=1.2/(.46*1.05*.045), density_bounds_kg_m3=[.8/(.46*1.05*.045), 1.8/(.46*1.05*.045)],
                        rate_usd_kg=[8., 15., 30.], basis="density inferred from retained cutset mass allowance, not measured upholstery foam"),
                    fabric=dict(density_kg_m3=600., rate_usd_kg=[8., 16., 30.], basis="1mm FR-cover hypothesis, compound and wear/fire evidence pending"),
                    elastomer=dict(density_kg_m3=1200., rate_usd_kg=[4., 8., 16.], basis="isolation/seal/cap hypothesis"),
                    adhesive=dict(density_kg_m3=1100., rate_usd_kg=[8., 16., 30.], basis="bond/seal consumable hypothesis")),
                preliminary_loads=dict(occupant_kg=100., provisional_chair_kg=15., gravity_m_s2=9.81,
                    vertical_factor=3., longitudinal_factor=1., lateral_factor=1.,
                    overturning_height_above_floor_m=.55,
                    scope="revisable fixture/load-path screening hypotheses; crowd/crash/certification loads not replaced"),
                tolerance=dict(cut_m=.001, weld_m=.002, installation_m=.002,
                    local_sum_m=.005, inherited_body_position_uncertainty_m=.25,
                    nominal_post_pan_gap_m=.0075, fitted_acceptance=False),
                accounting=dict(source_parts_replaced_once=list(OLD_PARTS),
                    extra_r1_base_bolts_in_parent=False, tooling_usd=None,
                    labour_usd_h=[6., 10., 16.], overhead_fraction=[.10, .20, .30],
                    complete_installed_mass_or_saving_claim=False),
                holds=["P6 actual moving geometry, tool and removal sweep integration",
                    "parent stub/cleat strength, bridge endplate prying, weld HAZ, fatigue and crash loads",
                    "core/skin bonds, insert pullout, foam compression, FR/smoke, creep and laminate strength",
                    "occupant loading hypothesis with actual cushion/back interfaces and accessibility review",
                    "supplier fastener threads/locking/torques, closed-joint sealing and maintenance validation"],
                status=deepcopy(FLAGS))


def validate_recipe(recipe):
    if recipe["schema"] != SCHEMA or recipe["parent"] != PARENT:
        raise ValueError("wrong source family")
    fixed, g = recipe["fixed"], recipe["geometry"]
    required = dict(cars=6, car_length_m=17., chairs=264, wheelchair_places=12,
                    floor_top_m=1.15, chair_origin_m=1.60, extra_body_lift_m=0., passenger_cg_z_m=1.70)
    if any(fixed[k] != v for k, v in required.items()):
        raise ValueError("unassigned fixed interface or second chair/passenger lift")
    if not isclose(g["leg_bottom_local_m"]+fixed["chair_origin_m"]-g["foot_size_m"][2], fixed["floor_top_m"], abs_tol=1e-10):
        raise ValueError("foot does not land on finished floor")
    if not isclose(g["leg_bottom_local_m"]+g["leg_length_m"],-.0525,abs_tol=1e-10):
        raise ValueError("continuous leg does not mate to retained frame underside")
    if not isclose(2*g["pan_skin_m"]+g["pan_core_m"]+2*g["skin_core_bondline_m"],
                   g["sandwich_thickness_m"], abs_tol=1e-10):
        raise ValueError("sandwich skins/core do not sum to installed thickness")
    if g["seat_foam_depth_m"]+g["back_foam_height_m"]+.004 > g["foam_gross_cutset_m"][1]:
        raise ValueError("two foam pieces exceed retained gross cutset including kerf")
    if recipe["status"] != FLAGS or recipe["accounting"]["extra_r1_base_bolts_in_parent"]:
        raise ValueError("unexecuted family cannot inherit acceptance or nonexistent R1 extras")
    if len(set(recipe["accounting"]["source_parts_replaced_once"])) != len(OLD_PARTS):
        raise ValueError("duplicate/incomplete replacement ownership")
    if set(recipe["accounting"]["source_parts_replaced_once"]) != set(OLD_PARTS):
        raise ValueError("different source credit ownership")
    if recipe["geometry"] != recipe_input()["geometry"]:
        raise ValueError("frozen geometry recipe changed; revise source family explicitly")
    return True


def _sandwich(name, center, size, normal, holes):
    """Three physical layers, including real bores in each layer, not a box fill."""
    out = []
    for label, thickness, offset, material in (
        ("rear-skin", .0015, -.00675, "gfrp"),
        ("core", .012, 0., "pet"), ("front-skin", .0015, .00675, "gfrp")):
        c, s = list(center), list(size); c[normal] += offset; s[normal] = thickness
        out.append(box(name+"/"+label, c, s, material, holes))
    return out


def _cover(name, minimum, maximum, normal):
    """Open-back five-panel slipcover, stitched to two removable retaining straps.

    Geometry is installed fabric thickness, not filled foam. Seam allowances,
    two zipper halves/slider and thread are additional counted stock. Covers
    remove after the straps' four M4 sets are released; qualification is pending.
    """
    q = [i for i in range(3) if i != normal]
    center = [(a+b)/2 for a, b in zip(minimum, maximum)]
    size = [b-a for a, b in zip(minimum, maximum)]
    top_c, top_s = list(center), list(size)
    top_c[normal] = maximum[normal]+.0005; top_s[normal] = .001
    out = [box(name+"/face", top_c, top_s, "fabric")]
    for a in q:
        for sign in (-1, 1):
            c, s = list(center), list(size)
            c[a] += sign*(size[a]+.001)/2; s[a] = .001
            out.append(box(f"{name}/return-{a}-{sign}", c, s, "fabric"))
    # 10mm seam allowance on every panel edge; no optimistic nesting credit.
    gross = 0.
    for e in out:
        dimensions = sorted(e["size_m"])
        gross += (dimensions[1]+.020)*(dimensions[2]+.020)*.001
    return out, gross


def chair_coupon(recipe, row_v=(-.05, .05), armrest_sign=0):
    """Future local-definition trial: one physical chair, never run at import.

    Material primitives, stock, bores, joint stacks and finite service paths are
    proposals. The caller must independently inspect intersections, tolerance
    residuals, attachment strength, operation and accessibility before admission.
    """
    validate_recipe(recipe)
    if armrest_sign not in (-1, 0, 1) or len(row_v) != 2:
        raise ValueError("one-owner armrest sign/two anchor rows")
    if any(not any(isclose(v, s*.12+t, abs_tol=1e-10) for t in (-.07, .07))
           for v, s in zip(row_v, (-1, 1))):
        raise ValueError("anchor pattern outside frozen four drilling alternatives")
    entities, stock, stacks, joints = [], [], [], []

    def add(name, solids, gross=None, process=.04, qa=.01, basis="named drilled/trimmed blank"):
        if isinstance(solids, dict):
            solids = [solids]
        entities.extend(solids)
        if gross is None:
            # Each gross rectangular blank is separately procured; cylinders
            # receive 4mm positive cut/trim allowance along their axis.
            gross = sum(prod(e["size_m"]) if e["shape"] == "box"
                        else pi*(e["radius_m"]**2-e["inner_radius_m"]**2)*(e["length_m"]+.004)
                        for e in solids)
        stock.append(stock_row(name, solids, gross, process, qa, basis))

    foot_t=recipe["geometry"]["foot_size_m"][2]
    leg_bottom=recipe["geometry"]["leg_bottom_local_m"]
    foot_center=leg_bottom-foot_t/2
    members = []
    for sign in (-1, 1):
        holes = [bore(2, [u, sign*.1875, -.04], .0102) for u in (-.12, .12)]
        if sign == armrest_sign:
            holes += [bore(1, [u, sign*.1875, -.04], .0102) for u in (-.08, .08)]
        members.append((f"side-{sign}", 0, [-.02875, sign*.1875, -.04], .4575, holes))
        members.append((f"cross-{sign}", 1, [sign*.1875, 0., -.04], .350, []))
        members.append((f"backpost-{sign}", 2, [-.245, sign*.1875, .1725], .400,
                        [bore(0, [-.245, sign*.1875, z], .0102) for z in (.10, .30)]))
    members.append(("back-tie", 1, [-.245, 0., .360], .350, []))
    for i, (u, v) in enumerate(product((-.1875, .1875), (-.12, .12))):
        members.append((f"leg-{i}", 2, [u, v, (leg_bottom-.0525)/2], recipe["geometry"]["leg_length_m"], []))
    rhs_area = .025**2-.021**2
    for name, axis, center, length, holes in members:
        add(name, tube(name, axis, center, length, [.025, .025], .002, "al6005a", holes),
            rhs_area*(length+.003+.010+.030/len(members)), .065, .015,
            "continuous 25x25x2 sharp-corner RHS; 3mm kerf +10mm trim + allocated30mm reserve; no splice")
    for i, (u, v) in enumerate(product((-.1875, .1875), (-.12, .12))):
        row = 0 if v < 0 else 1
        hole = bore(2, [.1325*(1 if u > 0 else -1), row_v[row], foot_center], .009)
        add(f"foot-{i}", box(f"foot-{i}", [.1625*(1 if u > 0 else -1), v, foot_center],
                            [.110, .170, foot_t], "al5083", [hole]), .114*.174*foot_t, .10, .025,
            "20mm5083plate blank, controlled cut/drill/deburr; replaces failed4mm R2 foot; no free doubler or splice")
    for sign in (-1, 1):
        add(f"back-cap-{sign}", box(f"back-cap-{sign}", [-.245, sign*.1875, .3735],
                                   [.025, .025, .002], "al6005a"), .029*.029*.002)
    for i, (u, v) in enumerate(product((-.12, .12), (-.1875, .1875))):
        add(f"pan-pad-{i}", box(f"pan-pad-{i}", [u, v, -.02375], [.040, .040, .0075],
                                "elastomer", [bore(2, [u, v, -.02375], .0065)]), .044*.044*.0075)
    for i, (v, w) in enumerate(product((-.1875, .1875), (.10, .30))):
        add(f"back-pad-{i}", box(f"back-pad-{i}", [-.230, v, w], [.005, .040, .040],
                                 "elastomer", [bore(0, [-.230, v, w], .0065)]), .005*.044*.044)

    pan_axes = [[u, v, -.0125] for u, v in product((-.12, .12), (-.1875, .1875))]
    back_axes = [[-.220, v, w] for v, w in product((-.1875, .1875), (.10, .30))]
    pan_trim_axes = [[u, v, -.0125] for u, v in product((-.08, .08), (-.13, .13))]
    back_trim_axes = [[-.220, v, w] for v, w in product((-.13, .13), (.18, .48))]
    for label, axis, c, size, shell_axes, trim_axes in (
        ("pan", 2, [0., 0., -.0125], [.450, .460, .015], pan_axes, pan_trim_axes),
        ("back", 0, [-.220, 0., .300], [.015, .460, .600], back_axes, back_trim_axes)):
        holes = [bore(axis, p, .0102) for p in shell_axes] + [bore(axis, p, .0072) for p in trim_axes]
        for layer in _sandwich(label, c, size, axis, holes):
            layer_size = list(layer["size_m"])
            for k in range(3):
                if k != axis:
                    layer_size[k] += .004
            add(layer["id"], layer, prod(layer_size), .06, .02,
                "separate real skin/core stock, 2mm trimming each edge; cure tooling/laminate/bond evidence pending")
        for i, p in enumerate(shell_axes):
            start = list(p); start[axis] -= .0075
            add(f"{label}-insert-{i}", cylinder(f"{label}-insert-{i}", axis, start, .015, .005,
                                               "al6005a", .00325))
        for i, p in enumerate(trim_axes):
            start = list(p); start[axis] -= .0075
            add(f"{label}-trim-insert-{i}", cylinder(f"{label}-trim-insert-{i}", axis, start, .015,
                                                    .0035, "al6005a", .00225))
        # Two 0.2mm bondlines need actual material and positive stock. They
        # replace 0.4mm of the core, preserving the fixed15mm installed shell.
        core = next(e for e in entities if e["id"] == label+"/core")
        old = next(s for s in stock if s["id"] == label+"/core")
        core["size_m"][axis] = .0116
        replacement = stock_row(old["id"], [core], old["gross_volume_m3"], old["process_hours"], old["qa_hours"], old["basis"])
        stock[stock.index(old)] = replacement
        for sign in (-1, 1):
            bc, bs = list(c), list(size); bc[axis] += sign*.0059; bs[axis] = .0002
            add(f"{label}-bond-{sign}", box(f"{label}-bond-{sign}", bc, bs, "adhesive", holes),
                prod(bs)*1.3, .04, .025, "finite0.2mm bondline each skin, 30percent mixing/edge reserve; qualification held")

    # 1mm side-cover thickness and a2mm cushion junction separate actual
    # fabric from shell/foam; filled allocation envelopes are not used.
    foam_specs = [("seat-foam", 2, [.00675, 0., .0175], [.4365, .460, .045], pan_trim_axes),
                  ("back-foam", 0, [-.190, 0., .321], [.045, .460, .558], back_trim_axes)]
    foam_total_net_blank = sum(prod(s) for _, _, _, s, _ in foam_specs)
    for label, axis, center, size, fixings in foam_specs:
        cavities = []
        for p in fixings:
            h = bore(axis, p, .014); h.update(depth_m=.010, entry_face=-1)
            cavities.append(h)
        for p in pan_axes if axis == 2 else back_axes:
            h = bore(axis, p, .018)
            h.update(depth_m=.014 if axis == 2 else .016, entry_face=-1)
            cavities.append(h)
        e = box(label, center, size, "foam", cavities)
        share = prod(size)/foam_total_net_blank
        add(label, e, prod(recipe["geometry"]["foam_gross_cutset_m"])*share, .10, .02,
            "two actual foam shapes from one retained460x1050x45mm gross cutset; kerf/trim and blind nut reliefs remain paid stock")
        lo, hi = bounds(e)
        cover, gross = _cover(label+"-cover", lo, hi, axis)
        add(label+"-cover", cover, gross, .22, .035,
            "five fabric panels; 10mm seam allowances each edge, no filled envelope or free bought cover")

    # Shell bolts: all eight axes, eight real25mm RHS wall pairs and sleeves.
    for label, axis, positions, rhs_center, pad, bearing in (
        ("pan", 2, pan_axes, -.04, .0075, -.0541),
        ("back", 0, back_axes, -.245, .005, -.2591)):
        for i, p in enumerate(positions):
            start = list(p); start[axis] = rhs_center-.0105
            add(f"{label}-rhs-sleeve-{i}", cylinder(f"{label}-rhs-sleeve-{i}", axis, start,
                                                  .021, .005, "al6005a", .00325))
            hp = list(p); hp[axis] = bearing
            st = hardware_stack(f"{label}-M6-{i}", axis, hp, 1,
                [("rhs", .025), ("isolation-pad", pad), ("shell", .015)], .060, .006, .004, .005)
            stacks.append(st); add(st["id"], st["entities"], process=.025, qa=.025)
    # Cover straps below the pan / behind the back. Foam blind pockets clear
    # each nut/bolt tip; these are8additional M4 sets, never hidden in old8M6.
    for label, axis, axes, strap_normal in (("seat", 2, pan_trim_axes, -.0205),
                                           ("back", 0, back_trim_axes, -.2280)):
        for index in (0, 1):
            if axis == 2:
                c, size = [[-.08, .08][index], 0., strap_normal], [.025, .460, .001]
            else:
                c, size = [strap_normal, 0., [.18, .48][index]], [.001, .460, .025]
            assigned = [p for p in axes if abs(p[0 if axis == 2 else 2]-c[0 if axis == 2 else 2]) < 1e-8]
            add(f"{label}-retaining-strap-{index}", box(f"{label}-retaining-strap-{index}", c, size,
                "fabric", [bore(axis, p, .0045) for p in assigned]), prod(size)*1.15, .06, .01)
        for i, p in enumerate(axes):
            at = list(p); at[axis] = -.022 if axis == 2 else -.2295
            st = hardware_stack(f"{label}-trim-M4-{i}", axis, at, 1,
                [("fabric-strap", .001), ("shell", .015)], .025, .004, .003, .0032, .001)
            stacks.append(st); add(st["id"], st["entities"], process=.018, qa=.015)

    for row, sign in enumerate((-1, 1)):
        holes = [bore(2, [u, row_v[row], -.4515], .009) for u in (-.1325, .1325)]
        add(f"anchor-strip-{row}", box(f"anchor-strip-{row}", [0., sign*.12, -.4515],
            [.455, .190, .003], "al5083", holes), .459*.194*.003, .08, .02,
            "replaces source track once; recessed into3mm wear, not added above floor")
        for col, u in enumerate((-.1325, .1325)):
            head_z=1.15+foot_t+.0005+.0016
            p = [u, row_v[row], head_z-1.60]
            st = hardware_stack(f"floor-M8-{row}-{col}", 2, p, -1,
                [("head-isolation", .0005), ("foot", foot_t), ("anchor-strip", .003), ("structural-floor", .0375),
                 ("bridge-rhs", .060), ("isolation", .001), ("backing-pad", .004)],
                recipe["geometry"]["floor_bolt_underhead_length_m"], .008, .0053, .0065)
            stacks.append(st); add(st["id"], st["entities"], process=.03, qa=.025)
            add(f"floor-sleeve-{row}-{col}", cylinder(f"floor-sleeve-{row}-{col}", 2,
                [u, row_v[row], 1.0495-1.60], .0975, .007, "al6005a", .0045))
            add(f"head-isolation-{row}-{col}", cylinder(f"head-isolation-{row}-{col}", 2,
                [u, row_v[row], 1.15+foot_t-1.60], .0005, .009, "gfrp", .0045))
            add(f"dielectric-liner-{row}-{col}", cylinder(f"dielectric-liner-{row}-{col}", 2,
                [u, row_v[row], 1.0495-1.60], 1.15+foot_t-1.0495, .0044, "gfrp", .0041),
                process=.05, qa=.025, basis="rolled0.3mm dielectric sleeve; compound, creep, bore tolerances and fire qualification pending")
            for label, center_z, thickness, material in (("isolation", 1.0490, .001, "gfrp"),
                                                       ("backing", 1.0465, .004, "steel")):
                add(f"{label}-{row}-{col}", box(f"{label}-{row}-{col}", [u, row_v[row], center_z-1.60],
                    [.050, .020, thickness], material, [bore(2, [u, row_v[row], 0.], .009)]),
                    .054*.024*thickness)
            # Nut retention cage and soft tip cap are separate positive stock;
            # actual stamped locking shape is not assumed from a generic nut.
            add(f"nut-cage-{row}-{col}", tube(f"nut-cage-{row}-{col}", 2,
                [u, row_v[row], 1.0390-1.60], .010, [.020, .020], .001, "steel"),
                (.020**2-.018**2)*.014, .03, .015)
            cap = [cylinder(f"tip-cap-{row}-{col}/wall", 2,
                    [u, row_v[row], 1.0274-1.60], .009, .006, "elastomer", .0045),
                   cylinder(f"tip-cap-{row}-{col}/closed-end", 2,
                    [u, row_v[row], 1.0264-1.60], .001, .006, "elastomer")]
            add(f"tip-cap-{row}-{col}", cap)
    if armrest_sign:
        s = armrest_sign
        rest = tube("shared-rest", 0, [0., s*.24, .18], .300, [.020, .040], .002, "al6005a")
        add("shared-rest", rest, (.020*.040-.016*.036)*.313, .08, .02)
        for sign in (-1, 1):
            add(f"rest-cap-{sign}", box(f"rest-cap-{sign}", [sign*.151, s*.24, .18],
                [.002, .020, .040], "al6005a"), .002*.024*.044)
        mount_holes = [bore(1, [u, s*.202, -.04], .0065) for u in (-.08, .08)]
        add("rest-mount", box("rest-mount", [0., s*.202, -.044], [.18, .004, .032], "al5083", mount_holes), .184*.004*.036)
        add("rest-bridge", box("rest-bridge", [0., s*.224, -.058], [.18, .040, .004], "al5083"), .184*.044*.004)
        add("rest-mast", box("rest-mast", [0., s*.242, .052], [.18, .004, .216], "al5083"), .184*.004*.220)
        for i, u in enumerate((-.08, .08)):
            start = [u, s*.1875-.0105, -.04]
            add(f"rest-rhs-sleeve-{i}", cylinder(f"rest-rhs-sleeve-{i}", 1, start,
                .021, .005, "al6005a", .00325))
            st = hardware_stack(f"rest-M6-{i}", 1, [u, s*.2056, -.04], -s,
                [("rest-mount", .004), ("side-rhs", .025)], .045, .006, .004, .005)
            stacks.append(st); add(st["id"], st["entities"], process=.025, qa=.02)
        joints.append(dict(id="shared-rest-welds", count=5, fillet_m=.003,
            net_length_m=.18*3+2*(.020+.040)*2, centroid_m=[0., s*.24, .06],
            qualification="local cantilever, lateral load, weld and repair access pending"))
    joints.append(dict(id="frame-welds", count=18, fillet_m=.003, net_length_m=1.8,
                       centroid_m=[-.05, 0., -.10], qualification="HAZ, distortion, fatigue and seat attachment loads pending"))
    consumables = dict(welds=joints,
        weld_basis="triangular3mm fillets at declared lengths, 20percent procurement reserve; geometry intersection/actual bead drawings pending",
        powder_coating=dict(net_mass_kg=[.040, .060, .100], gross_mass_kg=[.048, .072, .120],
            centroid_hypothesis_m=[-.04, 0., -.10], process_hours=.15, qa_hours=.04),
        cover_seams=dict(covers=2, zipper_halves=4, sliders=2, stitched_length_m=4.5,
            net_mass_kg=[.015, .025, .045], gross_mass_kg=[.02, .035, .06],
            process_hours=.20, qa_hours=.04, centroid_hypothesis_m=[-.10, 0., .10]),
        anchor_sealant=dict(net_mass_kg=[.012, .020, .035], gross_mass_kg=[.016, .027, .047],
            process_hours=.12, qa_hours=.03, centroid_hypothesis_m=[0., 0., -.45],
            basis="two strips and4sleeves sealed at penetrations; no adhesive structural capacity credited"),
        r3_added_foot_finish=dict(net_mass_kg=[.0015,.00186368,.0030],gross_mass_kg=[.0018,.002236416,.0036],
            centroid_hypothesis_m=[0.,0.,foot_center],process_hours=.02,qa_hours=.005,
            basis="four feet gain0.03584m2edge area vsR2; base40um x1300kg/m3,20percent procurement reserve; actual qualified finish pending"))
    return dict(schema=SCHEMA, recipe_id=identity(recipe), frame=dict(origin="actual P1 pan/frame pattern, no additional lift", axes="u/v/w", transform="world=R@local+origin"),
        row_v_m=list(row_v), armrest_sign=armrest_sign, entities=entities, stock=stock, fastener_stacks=stacks,
        consumables=consumables, hardware_counts=dict(floor_M8_sets=4, shell_M6_sets=8,
            trim_M4_sets=8, armrest_M6_sets=2*bool(armrest_sign), floor_sleeves=4,
            shell_inserts=8, shell_rhs_sleeves=8, trim_inserts=8,
            armrest_rhs_sleeves=2*bool(armrest_sign), joints=18+5*bool(armrest_sign),
            bearings=0, slides=0, powered_stops=0, wiring=0, cooling_flexes=0,
            zero_basis="passive fixed chair only; vehicle wiring/cooling, doors and wheelchair interfaces remain parent-owned"),
        support_bounds=chair_support_bounds(recipe["preliminary_loads"],row_v,
            foot_thickness=foot_t,leg_length=recipe["geometry"]["leg_length_m"]),
        occupied_interfaces=dict(pan_bottom_world_m=1.580, foam_surface_world_m=1.640,
            fabric_surface_world_m=1.641, old_load_cg_world_m=1.700,
            cg_above_uncompressed_foam_m=.060, anthropometry_and_compression_verified=False,
            post_pan_nominal_gap_m=.0075, proposed_tolerance_residual_m=.0025,
            armrests_between_contiguous_seats_only=True, universal_ergonomic_limit_claim=False),
        service=dict(sequence=["support and remove cover/foam after releasing8M4 sets; inspect inserts",
            "release8M6 shell sets; lift pan/back clear without loading foam as a handle",
            "support frame, release4M8 floor sets; captive cages retain inaccessible nuts",
            "lift frame100mm then translate650mm towards aisle in isolated car; finite sweep must be verified",
            "remove floor panels for bridge inspection; do not extract structural node bolts while bridge is loaded"],
            frame_removal_path_local_m=[[0., 0., 0.], [0., 0., .100], [.650, 0., .100]],
            shell_removal_paths_local_m=dict(pan=[[0.,0.,0.],[0.,0.,.100]], back=[[0.,0.,0.],[.100,0.,0.]]),
            lift="support at four frame corners; rated aid or manual handling plan pending known assembled mass",
            socket_radius_m=.025, insertion_m=.10, accepted=False), status=deepcopy(FLAGS))


def bridge_definition(plans, recipe):
    """Future actual bridge definition: world-frame solids + typed source bores."""
    if any(not n["interface"]["counterpart_mating_resolved"] for p in plans for n in p["nodes"]):
        raise ValueError("P6 actual endcap weld/endplate mating is unresolved; typed120mm statics do not admit geometry generation")
    entities, stock, stacks, source_bores, welds, diaphragms = [], [], [], [], [], []
    def add(name, solids, gross=None, process=.06, qa=.02):
        if isinstance(solids, dict):
            solids = [solids]
        entities.extend(solids)
        if gross is None:
            gross = sum(prod(e["size_m"]) if e["shape"] == "box" else
                        pi*(e["radius_m"]**2-e["inner_radius_m"]**2)*(e["length_m"]+.004)
                        for e in solids)
        stock.append(stock_row(name, solids, gross, process, qa,
                               "separate named bridge/joint material; positive cut/drill scrap and person-hour allowance"))
    beam_results = []
    load = recipe["preliminary_loads"]
    chair_vertical = (load["occupant_kg"]+load["provisional_chair_kg"])*load["gravity_m_s2"]*load["vertical_factor"]
    for plan in plans:
        for span in plan["spans"]:
            name, length, center = span["id"], span["rail_length_m"], span["rail_center_m"]
            holes = [bore(2, h["at_m"], .0142) for h in span["anchors"]]
            add(name, tube(name, 0, center, length, [.040, .060], .003, "al6005a", holes),
                (.040*.060-.034*.054)*(length+.013), .12, .035)
            occupied_diaphragms=[]
            for sign in (-1, 1):
                depth=span["left_counterpart_depth_m"] if sign < 0 else span["right_counterpart_depth_m"]
                interface=node_interface(span["lane_y_m"],depth);t=interface["plate_thickness_m"]
                x = span["left_stub_x_m"]+depth/2+t/2 if sign < 0 else span["right_stub_x_m"]-depth/2-t/2
                c = [x, interface["plate_center_y_m"], 1.0695]
                holes = [bore(0, [x, interface["bolt_column_y_m"], z], .009) for z in (1.0535, 1.0855)]
                add(f"{name}/endplate-{sign}", box(f"{name}/endplate-{sign}", c,
                    interface["plate_size_m"], "al5083", holes), t*.104*.084,
                    .18 if interface["counterpart_weld_relief_required"] else .10,
                    .055 if interface["counterpart_weld_relief_required"] else .03)
                overlap=min(span["lane_y_m"]+.020,c[1]+interface["plate_size_m"][1]/2)-max(span["lane_y_m"]-.020,c[1]-interface["plate_size_m"][1]/2)
                seam=.060+2*overlap if interface["counterpart_weld_relief_required"] else .200
                wy=span["lane_y_m"]
                if interface["counterpart_weld_relief_required"]:
                    ysign=1 if wy>0 else -1
                    edge=(c[1]+ysign*interface["plate_size_m"][1]/2)
                    rail_inner=wy-ysign*.020
                    wy=(.060*rail_inner+2*overlap*(rail_inner+edge)/2)/seam
                wx=span["support_face_x_m"][0]+.001 if sign<0 else span["support_face_x_m"][1]-.001
                welds.append(dict(id=f"{name}/end-weld-{sign}", count=1, length_m=seam,
                                  fillet_m=.003, centroid_m=[wx, wy, 1.0795],
                                  centroid_basis="declared3mmtriangular joint bead; proposed path, not recovered weld geometry"))
                if interface["internal_diaphragm_required"]:
                    location=diaphragm_station(span,sign,occupied_diaphragms)
                    occupied_diaphragms.append(location["x_m"])
                    dname=f"{name}/relief-diaphragm-{sign}"
                    add(dname,box(dname,[location["x_m"],span["lane_y_m"],1.0795],
                        [.012,.034,.054],"al5083"),.012*.038*.058,.15,.04)
                    welds.append(dict(id=dname+"/internal-weld",count=1,length_m=2*(.034+.054),
                        fillet_m=.003,centroid_m=[location["x_m"]+(-.007 if sign<0 else .007),span["lane_y_m"],1.0795],
                        centroid_basis="one accessible face of12mmplate plus1mmtriangular bead centroid; inspect before endplate attachment"))
                    diaphragms.append(dict(id=dname,span_id=span["id"],lane_y_m=span["lane_y_m"],
                        node_x_m=span["left_stub_x_m"] if sign < 0 else span["right_stub_x_m"],
                        location=location,sequence="fit and weld diaphragm through open end before partial endplate weld; inspect internal full perimeter; open outboard end pocket remains drained/inspectable",qualified=False))
            # Each chair supplies two anchors/lane; assigning each a quarter
            # full vertical load is deliberately conservative for this bound.
            beam_results.append(dict(bridge=name, **beam_bound(length, [chair_vertical/4]*len(span["anchors"]),
                recipe["materials"]["al6005a"]["E_Pa"], .040, .060, .003,
                recipe["materials"]["al6005a"]["allowable_Pa"])))
        for node in plan["nodes"]:
            x, lane = node["stub_x_m"], node["lane_y_m"]
            interface=node["interface"];y=interface["bolt_column_y_m"]
            depth=interface["counterpart_depth_m"];half=depth/2;t=interface["plate_thickness_m"]
            name = f"node/{lane:.7f}/{x:.7f}"
            for side in ("left", "right"):
                sign = -1 if side == "left" else 1
                if side not in node["connected_sides"]:
                    c = [x+sign*(half+t/2), interface["plate_center_y_m"], 1.0695]
                    add(name+"/backing-"+side, box(name+"/backing-"+side, c,
                        interface["plate_size_m"], "al5083",
                        [bore(0, [c[0], y, z], .009) for z in node["hole_world_z_m"]]), t*.104*.084,
                        .18 if interface["counterpart_weld_relief_required"] else .10,
                        .055 if interface["counterpart_weld_relief_required"] else .03)
            for j, z in enumerate(node["hole_world_z_m"]):
                add(f"{name}/sleeve-{j}", cylinder(f"{name}/sleeve-{j}", 0,
                    [x-half, y, z], depth, .007, "al6005a", .0045))
                source_bores.append(dict(part_id="underframe/floor-crossmember-stub" if depth == .100 else "compact-joint/header",
                    counterpart_source=interface["counterpart_source"],source_stub_x_m=x, bridge_lane_y_m=lane,
                    actual_bore_y_m=y,axis=0, center_m=[x, y, z],
                    diameter_m=.0142, actual_wall_planes_x_m=[x-half, x+half],
                    wall_thickness_m=interface["counterpart_wall_m"], sleeve_length_m=depth,
                    note="two actual counterpart walls bored; sleeve spans full reviewed100/120mm, no inner-only sleeve"))
                for s in (-1, 1):
                    at = [x+s*(half+t), y, z]
                    if s < 0:
                        at[0] -= .0005
                    add(f"{name}/isolation-{j}-{s}", cylinder(f"{name}/isolation-{j}-{s}",
                        0, at, .0005, .009, "gfrp", .0045))
                st = hardware_stack(f"{name}/M8-{j}", 0, [x-half-t-.0021, y, z], 1,
                    [("left-isolation", .0005), ("left-endplate-or-backer", t),
                     ("source-counterpart", depth), ("right-endplate-or-backer", t),
                     ("right-isolation", .0005)], interface["bolt_underhead_length_m"], .008, .0053, .0065)
                st["tool_envelope"]["socket_radius_m"]=interface["node_tool"]["head_radius_m"]
                st["tool_envelope"]["insertion_m"]=interface["node_tool"]["head_length_m"]
                st["stack_tolerance_hypotheses"]=interface["dimensional_hypotheses"]
                stacks.append(st); add(st["id"], st["entities"], process=.035, qa=.03)
                nut_end=x+half+t+.0086
                cap_length=interface["cap_wall_length_m"]
                add(f"{name}/tip-cap-{j}", [cylinder(f"{name}/tip-cap-{j}/wall", 0,
                    [nut_end, y, z], cap_length, .006, "elastomer", .0045),
                    cylinder(f"{name}/tip-cap-{j}/closed-end", 0,
                    [nut_end+cap_length, y, z], .001, .006, "elastomer")])
                add(f"{name}/cap-retention-bond-{j}",cylinder(f"{name}/cap-retention-bond-{j}",0,
                    [nut_end,y,z],.002,.0045,"adhesive",.004),process=.04,qa=.02)
    reactions=bridge_reactions(plans,chair_vertical/4,
        (load["occupant_kg"]+load["provisional_chair_kg"])*load["gravity_m_s2"]*load["longitudinal_factor"]/4,
        (load["occupant_kg"]+load["provisional_chair_kg"])*load["gravity_m_s2"]*load["lateral_factor"]/4)
    plate_bounds=[dict(node=dict(lane_y_m=r["lane_y_m"],x_m=r["node_x_m"]),
        failed_6mm_control=endplate_band_bound(r["vertical_N"],r["longitudinal_N"],r["lateral_N"],.006),
        counted_10mm_revision=endplate_band_bound(r["vertical_N"],r["longitudinal_N"],r["lateral_N"],.010)) for r in reactions]
    by_node={(r["lane_y_m"],r["node_x_m"]):r for r in reactions}
    for diaphragm in diaphragms:
        r=by_node[(diaphragm["lane_y_m"],diaphragm["node_x_m"])]
        diaphragm["necessary_bound"]=diaphragm_band_bound(r["vertical_N"],r["longitudinal_N"],r["lateral_N"])
    return dict(frame="body world; identity rigid transform", entities=entities, stock=stock,
        stacks=stacks, source_stub_bores=source_bores, welds=welds, beam_bounds=beam_results,
        node_reactions=reactions,eccentric_endplate_bounds=plate_bounds,
        internal_relief_diaphragms=diaphragms,
        structural_load_path=["foot/strip", "97.5mm isolated compression sleeve through structural floor and bridge RHS",
            "backing pad and retained M8", "bridge rail walls", "welded10mm offset endplates",
            "two shared M8/full-width sleeves per actual100/120mm counterpart node", "actual counterpart walls",
            "parent stub cleat and primary load path; additional loads must be verified"],
        preliminary_joint_domains=dict(bolt_shear_grade="8.8 hypothesis, not authenticated", stub_bearing_model="use actual6/8mmcounterpart walls and eccentric bolt-group loads; local wall/contact model pending",
            prying=False, fatigue=False, weld_HAZ=False, floor_skin_or_core_strength_credited=False),
        hardware_counts=dict(shared_node_count=sum(len(p["nodes"]) for p in plans),
            through_node_M8_sets=2*sum(len(p["nodes"]) for p in plans),
            compression_sleeves=2*sum(len(p["nodes"]) for p in plans),
            endplates=2*sum(len(p["spans"]) for p in plans),
            backing_plates=sum(n["backing_plate_count"] for p in plans for n in p["nodes"])),
        shared_node_tools=node_interface(1.,.100)["node_tool"],
        finite_service=dict(node_socket_radius_m=.010, insertion_m=.040,
            bridge_removal="unload and support floor/chairs; remove panels, release shared nodes, lower rail60mm then translate to hatch",
            rail_removal_path_world_delta_m=[[0.,0.,0.],[0.,0.,-.060],[.200,0.,-.060]],
            underside_projection_min_z_m=1.0264, P6_header_endcap_interface="explicitly pending actual P6 geometry and swept tools; no R1 inheritance",
            accepted=False), status=deepcopy(FLAGS))


def stock_accounting(entities, stock, materials, origin=(0., 0., 0.), rotation=I):
    """Exact nominal primitive material moments + provisional calculated costs.

    Shared tooling, qualification, purchased hardware finishing, assembly to the
    vehicle and unknown reserves remain separately open; this is partial scope.
    """
    by_id = {e["id"]: e for e in entities}
    owned = [x for s in stock for x in s["entity_ids"]]
    if len(by_id) != len(entities) or len(owned) != len(set(owned)) or set(owned) != set(by_id):
        raise ValueError("material stock ownership is not exactly once")
    net_mass, gross_mass, moment = 0., 0., [0., 0., 0.]
    mass_cases = {c:0. for c in CASES}
    moment_cases = {c:[0.,0.,0.] for c in CASES}
    costs = [0., 0., 0.]
    for s in stock:
        mat = materials[s["material"]]
        density = mat["density_kg_m3"]
        db = mat.get("density_bounds_kg_m3", [density, density])
        densities = dict(zip(CASES, [db[0], density, db[1]]))
        net_mass += s["net_volume_m3"]*density
        gross_mass += s["gross_volume_m3"]*density
        for case in CASES:
            mass_cases[case] += s["net_volume_m3"]*densities[case]
        for eid in s["entity_ids"]:
            volume, c = volume_centroid(by_id[eid])
            world = transform(c, origin, rotation)
            moment = [moment[k]+volume*density*world[k] for k in range(3)]
            for case in CASES:
                moment_cases[case] = [moment_cases[case][k]+volume*densities[case]*world[k] for k in range(3)]
        for k, labour_rate in enumerate((6., 10., 16.)):
            costs[k] += s["gross_volume_m3"]*density*mat["rate_usd_kg"][k] + (s["process_hours"]+s["qa_hours"])*labour_rate
    return dict(net_nominal_material_mass_kg=net_mass, gross_procurement_mass_kg=gross_mass,
                net_material_mass_kg=mass_cases, net_material_moment_kg_m=moment_cases,
                nominal_material_moment_kg_m=moment,
                nominal_material_cg_m=[x/net_mass for x in moment],
                direct_material_process_QA_usd=dict(zip(CASES, costs)),
                exclusions=["non-primitive consumables/reserves", "shared tooling/plant allocation",
                    "complete final installation, qualification, delivery and tax"], complete_installed=False)


def consumable_accounting(consumables, materials, origin=(0.,0.,0.), rotation=I):
    """Positive bounded weld/finish/seam/seal masses; not unearned solid geometry."""
    masses = {c:0. for c in CASES}; moments = {c:[0.,0.,0.] for c in CASES}
    cost = {c:0. for c in CASES}
    for w in consumables.get("welds", []):
        net = .5*w["fillet_m"]**2*w.get("net_length_m", w.get("length_m",0.))*2710.
        at = transform(w["centroid_m"], origin, rotation)
        for j,c in enumerate(CASES):
            # Centroid is a declared weld grouping hypothesis; actual weld
            # paths and individual bead material remain CAD/detail holds.
            m = net*[.9,1.,1.3][j]
            masses[c] += m; moments[c] = [moments[c][k]+m*at[k] for k in range(3)]
            cost[c] += net*1.20*materials["al6005a"]["rate_usd_kg"][j] + w.get("net_length_m",w.get("length_m",0.))*[.2,.35,.6][j]*[6,10,16][j]
    for label in ("powder_coating","cover_seams","anchor_sealant","r3_added_foot_finish"):
        if label not in consumables:
            continue
        row = consumables[label]
        at = transform(row["centroid_hypothesis_m"], origin, rotation)
        for j,c in enumerate(CASES):
            masses[c] += row["net_mass_kg"][j]
            moments[c] = [moments[c][k]+row["net_mass_kg"][j]*at[k] for k in range(3)]
            cost[c] += row["gross_mass_kg"][j]*[8.,16.,30.][j] + (row["process_hours"]+row["qa_hours"])*[6.,10.,16.][j]
    return dict(bounded_nonprimitive_mass_kg=masses, bounded_nonprimitive_moment_kg_m=moments,
                calculated_partial_cost_usd=cost, actual_bead_cover_trim_geometry_complete=False,
                centroid_basis="explicit group hypotheses, not measured installed CG")


def rectangle_intersection(a_center, a_size, b_center, b_size):
    """Plan-area clipping for axis-aligned floor stock/cutouts, no GIS dependency."""
    lo = [max(a_center[k]-a_size[k]/2,b_center[k]-b_size[k]/2) for k in (0,1)]
    hi = [min(a_center[k]+a_size[k]/2,b_center[k]+b_size[k]/2) for k in (0,1)]
    if any(hi[k] <= lo[k] for k in (0,1)):
        return None
    return dict(area_m2=prod(hi[k]-lo[k] for k in (0,1)),
                centroid_xy_m=[(hi[k]+lo[k])/2 for k in (0,1)])


def floor_wear_patch(patterns, cutouts):
    """Future necessary stock bound: exact nominal tile clipping, unchanged gross.

    Source wear is still an equipment/covering envelope with mass allowances.
    Effective densities translate those allowances only; they are not measured
    fire-qualified material properties. Coupon/native work must not upgrade it.
    """
    tiles, clips = [], []
    for p in patterns:
        if p["rotation"] != I:
            raise ValueError("floor tile rotation requires explicit polygon clipping")
        size = p["geometry"]["size_m"]
        if not isclose(size[2],.003,abs_tol=1e-10):
            raise ValueError("source wear is not3mm")
        for index, at in enumerate(p["positions_m"]):
            if not isclose(at[2],1.13,abs_tol=1e-10):
                raise ValueError("source wear placement is not the reviewed stale datum")
            tiles.append(dict(id=p["id"]+f"/{index}", center=[at[0],at[1],1.1485],size=size,
                mass_kg={c:p["mass_kg"][c]/p["count"] for c in CASES}))
    if len(tiles) != 108:
        raise ValueError("108nominal source tiles required")
    removed = {c:0. for c in CASES}; moments={c:[0.,0.,0.] for c in CASES}
    for cut in cutouts:
        area = 0.
        for tile in tiles:
            clip = rectangle_intersection(tile["center"],tile["size"],cut["center_world_m"],cut["size_world_m"])
            if clip:
                area += clip["area_m2"]
                clips.append(dict(tile_id=tile["id"],chair_owner=cut["owner"],**clip))
                for c in CASES:
                    m=tile["mass_kg"][c]*clip["area_m2"]/(tile["size"][0]*tile["size"][1])
                    removed[c] += m
                    at=[*clip["centroid_xy_m"],1.1485]
                    moments[c]=[moments[c][k]+m*at[k] for k in range(3)]
        if not isclose(area,cut["size_world_m"][0]*cut["size_world_m"][1],abs_tol=1e-8):
            raise ValueError("recessed strip is not fully contained in actual source wear tiles")
    for i,a in enumerate(cutouts):
        for b in cutouts[i+1:]:
            if rectangle_intersection(a["center_world_m"],a["size_world_m"],b["center_world_m"],b["size_world_m"]):
                raise ValueError("overlapping recessed strips would double-credit wear material")
    return dict(translate_z_m=.0185,new_center_m=1.1485,clips=clips,source_pieces=108,
                net_allowance_material_removed_kg=removed,removed_moment_kg_m=moments,
                gross_stock_and_cost_retained=True,
                meaning="cutout of nominal allowance material; no paid gross-stock cost saving or measured mass claim")


def coupon_geometry_projection(coupon):
    """Exclude prices, test status, QA and load metadata from geometry identity."""
    cons = coupon["consumables"]
    return dict(entities=coupon["entities"],
        bounded_welds=[{f:w[f] for f in ("fillet_m","net_length_m","centroid_m")} for w in cons["welds"]],
        bounded_consumables={n:{f:cons[n][f] for f in ("net_mass_kg","centroid_hypothesis_m")}
                             for n in ("powder_coating","cover_seams","anchor_sealant","r3_added_foot_finish") if n in cons})


def read_parent(path):
    """Read exactly one pinned source receipt; never generate or rewrite it."""
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != PARENT["raw_sha256"]:
        raise ValueError("P1 raw source receipt mismatch")
    body = json.loads(gzip.decompress(raw))
    if any(body[k] != PARENT[k] for k in ("candidate_id", "evaluation_id")):
        raise ValueError("P1 candidate/evaluation mismatch")
    return body


def source_layout(body):
    """Future all-placement trial derives coordinates from actual source patterns."""
    if identity(body) != PARENT["decoded_canonical_sha256"]:
        raise ValueError("source contents changed without a new authorized ancestor")
    if any(body[k] != PARENT[k] for k in ("candidate_id", "evaluation_id")):
        raise ValueError("mixed source candidate")
    seats, stubs = [], {}
    for p in body["patterns"]:
        if p["part_id"] == "body/chair-frame":
            if len(p["positions_m"]) != 1 or p["count"] != 1:
                raise ValueError("one source occurrence per chair frame required")
            origin = p["positions_m"][0]
            if not isclose(origin[2], 1.60, abs_tol=1e-10):
                raise ValueError("source pan/frame datum changed; no automatic body lift")
            side = 1 if origin[1] > 0 else -1
            if not isclose(abs(origin[1]), .94, abs_tol=1e-10):
                raise ValueError("source seat lateral datum changed")
            expected = [[0., float(side), 0.], [-float(side), 0., 0.], [0., 0., 1.]]
            if p["rotation"] != expected:
                raise ValueError("unexpected retained chair handedness")
            seats.append(dict(id=p["assembly_occurrence_id"], car=p["car_allocation"][0][0],
                side=side, origin_m=origin, rotation=p["rotation"], source_pattern_id=p["id"], source_pattern_hash=identity(p)))
        elif p["part_id"] == "underframe/floor-crossmember-stub":
            g = p["geometry"]["source_stock"]
            if any(not isclose(g[k], v, abs_tol=1e-10) for k, v in
                   (("width_m", .100), ("depth_m", .180), ("wall_m", .006), ("length_m", .7835))):
                raise ValueError("actual source stub is not100x180x6x783.5mm")
            car = p["car_allocation"][0][0]
            stubs.setdefault(car, set()).update(x[0] for x in p["positions_m"])
    if len(seats) != 264 or len({s["id"] for s in seats}) != 264 or set(stubs) != set(range(6)):
        raise ValueError("full264/six-car source layout required")
    if any(sum(s["car"] == car for s in seats) != 44 or len(stubs[car]) != 24 for car in range(6)):
        raise ValueError("retained44chairs/24stub-stations per car changed")
    return seats, {k: sorted(v) for k, v in stubs.items()}


def replacement_credits(body):
    """Typed source ownership; the old14leaves go once, R1extras do not exist here."""
    parts = {p["id"]: p for p in body["parts"]}
    out = []
    for part_id in OLD_PARTS:
        if part_id not in parts:
            raise ValueError("required source credit missing")
        p = parts[part_id]
        patterns = [x for x in body["patterns"] if x["part_id"] == part_id]
        if sum(x["count"] for x in patterns) != p["quantity_per_train"]:
            raise ValueError("credit quantity/source pattern mismatch")
        out.append(dict(operation="replace_source_leaf_once", source_part_id=part_id,
            source_component_definition_id=p["component_definition_id"], source_part_hash=identity(p),
            source_pattern_hashes=[dict(id=x["id"], hash=identity(x)) for x in patterns],
            quantity=p["quantity_per_train"], removed_mass_kg={c:p["mass_each_kg"][c]*p["quantity_per_train"] for c in CASES},
            removed_direct_cost_usd={c:p["direct_cost_each_usd"][c]*p["quantity_per_train"] for c in CASES},
            removed_mass_moment_kg_m={c:[sum(x["mass_kg"][c]*x["centroid_m"][k] for x in patterns) for k in range(3)] for c in CASES},
            replacement_owner="research/direct-floor-chair-r4; detailed stock and shared structural bridges, no parent purchased kit"))
    return out


def compile_proposal(recipe, body):
    """Future definition-only trial. It deliberately cannot mutate/accept a body.

    The caller first authenticates the pinned receipt with ``read_parent``.
    Source/evaluation/physical-definition identities remain distinct. Rebase to
    a P6 descendant requires an explicit coordinator patch and independent check.
    """
    validate_recipe(recipe)
    seats, stubs = source_layout(body)
    rests = owner_map(seats)
    if len(rests) != 228:
        raise ValueError("retained36row-segments require228one-owner shared rests")
    rest_owner = {r["owner"]: r for r in rests}
    variants, occurrences, all_anchors, cutouts = {}, [], {}, []
    for seat in sorted(seats, key=lambda x:x["id"]):
        rows = choose_anchor_rows(seat["origin_m"], seat["rotation"], stubs[seat["car"]])
        row_v = tuple(r["local_v_m"] for r in rows)
        arm_sign = rest_owner.get(seat["id"], {}).get("local_v_sign", 0)
        key = str(row_v)+":"+str(arm_sign)
        if key not in variants:
            coupon = chair_coupon(recipe, row_v, arm_sign)
            coupon["definition_id"] = identity(coupon_geometry_projection(coupon))
            variants[key] = coupon
        occurrences.append(dict(id=seat["id"], definition_id=variants[key]["definition_id"],
            origin_m=seat["origin_m"], rotation=seat["rotation"], source_pattern_hash=seat["source_pattern_hash"],
            floor_drilling_rows=rows, armrest_owner=seat["id"] if arm_sign else None))
        for row in rows:
            for col, at in enumerate(row["axes_world_m"]):
                lane = round(at[1], 8)
                all_anchors.setdefault((seat["car"], lane), []).append(dict(id=seat["id"]+f"/{row['row']}/{col}", at_m=at))
        for side in (-1, 1):
            c = transform([0., side*.12, -.4515], seat["origin_m"], seat["rotation"])
            cutouts.append(dict(owner=seat["id"], center_world_m=c,
                size_world_m=[.190, .455, .003], correction="replace wear material by counted recessed anchor strip; preserve paid gross cut stock"))
    plans = [bridge_plan(anchors, stubs[car], lane) for (car, lane), anchors in sorted(all_anchors.items())]
    bridges = bridge_definition(plans, recipe)
    part_hashes = {p["id"]:identity(p) for p in body["parts"]}
    wear = [p for p in body["patterns"] if p["part_id"] == "body/floor-wear-layer"]
    # A different source spelling must be explicitly reviewed, never guessed.
    if sum(p["count"] for p in wear) != 108:
        raise ValueError("expected108source floor-wear-layer pieces; source name/count must be reviewed")
    wear_delta = floor_wear_patch(wear, cutouts)
    by_definition = {v["definition_id"]:v for v in variants.values()}
    accounting = []
    for occurrence in occurrences:
        coupon = by_definition[occurrence["definition_id"]]
        accounting.append(dict(occurrence=occurrence["id"],
            material=stock_accounting(coupon["entities"],coupon["stock"],recipe["materials"],
                                     occurrence["origin_m"],occurrence["rotation"]),
            bounded_consumables=consumable_accounting(coupon["consumables"],recipe["materials"],
                                     occurrence["origin_m"],occurrence["rotation"])))
    bridge_accounts = stock_accounting(bridges["entities"],bridges["stock"],recipe["materials"])
    bridge_welds = consumable_accounting(dict(welds=bridges["welds"]),recipe["materials"])
    # A physical-definition fingerprint excludes cost, QA, selection and load
    # metadata. It is not the canonical full-body physical candidate identity.
    variant_physical = {k:coupon_geometry_projection(v) for k,v in variants.items()}
    physical = dict(recipe_geometry=recipe["geometry"], materials={k:{"density_kg_m3":v["density_kg_m3"]}
                    for k,v in recipe["materials"].items()},
        variants=variant_physical, occurrences=[{f:v[f] for f in ("definition_id","origin_m","rotation")} for v in occurrences],
        bridge_geometry=bridges["entities"],
        floor_cutouts=cutouts, floor_wear_delta_z_m=.0185)
    return dict(schema=SCHEMA, recipe_id=identity(recipe), source=deepcopy(PARENT),
        physical_definition_id=identity(physical), evaluation_request_id=identity(dict(recipe_id=identity(recipe), loads=recipe["preliminary_loads"],
             tolerances=recipe["tolerance"], source=deepcopy(PARENT))), selection_id=None,
        ancestry=deepcopy(R1), variants=variants, occurrences=occurrences, shared_armrest_ownership=rests,
        bridges=bridges, bridge_plans=plans,
        partial_accounting=dict(chair_material_and_group_moments=accounting,
            bridge_material=bridge_accounts, bridge_bounded_welds=bridge_welds,
            source_credit_scope="source catalogue allowances, not measured installed mass",
            source_stub_drill_credit=dict(hole_count=len(bridges["source_stub_bores"]),
                nominal_removed_al_volume_each_m3=2*.006*pi*(.0142/2)**2,
                actual_intersection_and_existing_bores_verified=False),
            full_body_mass_or_saving_claim=False, tooling_allocation_usd=None,
            prices="calculated dated recipe allowances, no quoted or assumed bulk discount; no complete purchase-price claim"),
        typed_fullbody_delta_proposal=dict(apply_automatically=False,
            preconditions=dict(exact_parent=deepcopy(PARENT), source_part_hashes=part_hashes,
                unchanged_chair_xy_handing=True, wheelchair_places=12,
                P6_actual_header_endcap_and_underbody_coupling="pending; cannot apply to a new candidate by identity substitution"),
            source_leaf_replacements=replacement_credits(body),
            source_stub_bores=bridges["source_stub_bores"],
            floor_through_bores=[dict(owner=h["id"], axis=2, center_world_m=h["at_m"], diameter_m=.0142,
                layers_z_m=[[1.1095,1.1105],[1.1105,1.1455],[1.1455,1.147]],
                sleeve_is_structural_load_path=True, skin_or_core_capacity_credited=False)
                for a in all_anchors.values() for h in a],
            floor_wear=dict(source_pattern_hashes=[dict(id=p["id"],hash=identity(p)) for p in wear],
                cutouts=cutouts, **wear_delta),
            datums=dict(policy_seat_pan_z_m=dict(from_m=1.45,to_m=1.60,geometry_translation_m=0.),
                assembly_occurrence_z_m=dict(from_m=1.45,to_m=1.60,geometry_translation_m=0.),
                passenger_loading_cg_z_m=dict(retain_m=1.70,translation_m=0.,physical_meaning="unresolved already-lifted loading hypothesis, not actual occupant anatomy")),
            removed_nonexistent_R1_extra_floor_bolts=0, retained_old_pedestal_or_track_count=0,
            costs_and_loads="invalidate/recompute from new canonical installed bundle; no inherited R1/native/body/cost result",
            installed_vehicle_dependency="MUST re-evaluate passenger loading CG against actual1.640m uncompressed cushion surface; old1.700m is ancestry only. No inherited stability/axle/body/civil result and no invented anatomical CG"),
        status=deepcopy(FLAGS), holds=recipe["holds"])


def trial_requests():
    """At most two local definition requests, neither scheduled nor admitted."""
    recipe = recipe_input()
    common = dict(source=PARENT, recipe_id=identity(recipe), module_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  execution="NOT EXECUTED; independent review and coordinator authorization required",
                  native_CAD=False, FEM=False, body_producer=False, city=False, pricing_run=False,
                  business=False, automatic_admission=False, max_memory_bytes=1024**3,
                  preserve_all_failures=True, physical_acceptance=False)
    return [dict(id="chair-r4-one-coupon-definition", entrypoint="chair_coupon", max_cpu_s=45, max_output_bytes=8*1024**2,
                 parameters=dict(row_v=[-.05,.05], armrest_sign=1),
                 outputs=["named material solids, gross/net stock,8shell/8trim/4floor/2armrest bolt stacks", "nominal interfaces, mass moments and partial cost basis"], **common),
            dict(id="chair-r4-all264-necessary-definition", entrypoint="compile_proposal", max_cpu_s=75, max_output_bytes=22*1024**2,
                 outputs=["actual264pose/stock necessary bounds,228rest owners, bridge/stub ownership", "typed fullbody patch proposal, failures/holds and partial mass moments"],
                 checks=["one coupon material/stock ownership first", "all floor hardpoints and source stub bores", "door/WC/aisle/wall and P6 actual swept interfaces remain separate acceptance gate"], **common)]
