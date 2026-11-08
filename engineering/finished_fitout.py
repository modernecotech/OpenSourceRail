"""Two source-bound fitout research definitions; no body or native execution.

Coordinates are metres. Generated solids are inspectable proposed material
geometry, not recovered supplier shapes or proof of an installed assembly.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from math import isfinite, pi, prod
from pathlib import Path
import argparse
import csv
import gzip
import json

from engineering.design_search.craft_backends import solidcraft

BODY_ID = '5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3'
BODY_EVAL = 'd1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea'
BODY_SHA = 'f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23'
OWNERSHIP_ID = '2cdb128f329772b18cdc0e32aa51dc2aa95736ef190c28f431fcbe4c1bc54f98'
OWNERSHIP_MANIFEST_SHA = '5ff46d01d35aaddb8ddefceb327b939642167309952e73783dfdcf62318662b7'
CASES = ('low', 'base', 'high')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
CHAIR = 'research/finished-chair-frame-r1'
SEAL = 'research/terminal-perimeter-gasket-r1'
I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
HARDWARE = {
    'body/chair-anchor-bolt': (4, 'base to anchor track; not frame to base'),
    'body/chair-anchor-nut': (4, 'base to anchor track'),
    'body/chair-anchor-washer': (8, 'base to anchor track'),
    'body/chair-shell-bolt': (8, 'four pan and four back interfaces, proposed M6 compatibility held'),
    'body/chair-shell-nut': (8, 'four pan and four back interfaces'),
    'body/chair-shell-washer': (16, 'two per shell bolt'),
    'body/terminal-end-panel-bolt': (24, 'existing terminal panel clamping; gasket adds none'),
    'body/terminal-end-panel-nut': (24, 'existing terminal panel clamping'),
    'body/terminal-end-panel-washer': (48, 'existing terminal panel clamping'),
}


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _box(name, center, size, material='al6005a', holes=None):
    e = dict(id=name, shape='box', at_m=[c-s/2 for c, s in zip(center, size)],
             size_m=size, material=material)
    if holes:
        e['holes'] = holes
    return e


def _tube(name, axis, center, length, hole_centers=()):
    """Disjoint sharp-corner RHS walls, with real paired wall holes.

    The extrusion's corner radius is unknown. Sharp corners are a new section
    hypothesis, not a claim about purchased 6005A tube or its actual bendability.
    """
    q = [k for k in range(3) if k != axis]
    out = []
    for transverse, width, depth in ((q[0], .002, .025), (q[1], .021, .002)):
        other = q[1] if transverse == q[0] else q[0]
        for sign in (-1, 1):
            c = list(center); c[transverse] += sign*.0115
            size = [0., 0., 0.]; size[axis] = length
            size[transverse] = .002
            size[other] = .025 if transverse == q[0] else .021
            holes = []
            for haxis, at in hole_centers:
                if haxis != transverse:
                    continue
                hole = dict(axis='xyz'[haxis], diameter_m=.0065)
                for k in range(3):
                    if k != haxis:
                        hole['xyz'[k]+'_m'] = at[k]-(c[k]-size[k]/2)
                holes.append(hole)
            out.append(_box(name+f'/wall-{transverse}-{sign}', c, size, holes=holes))
    return out


def chair_definition():
    """Welded frame, four legs/feet, eight crush sleeves and isolation pads."""
    members = []
    def member(name, axis, c, length, holes=()):
        members.append(dict(id=name, axis=axis, center_m=c, net_length_m=length,
                            shell_holes=[dict(axis=a, at_m=p) for a, p in holes]))
    for sign in (-1, 1):
        # Local +u points towards aisle on both sides; +v follows stored rotation.
        pan = [(2, [u, sign*.1875, -.04]) for u in (-.12, .12)]
        member(f'side-{sign}', 0, [0., sign*.1875, -.04], .4, pan)
        member(f'cross-{sign}', 1, [sign*.1875, 0., -.04], .35)
        back = [(0, [-.1875, sign*.1875, z]) for z in (.10, .30)]
        member(f'back-upright-{sign}', 2, [-.1875, sign*.1875, .1725], .4, back)
    member('back-tie', 1, [-.1875, 0., .36], .35)
    for u, v in product((-.1875, .1875), (-.12, .12)):
        member(f'leg-{u}-{v}', 2, [u, v, (-.236-.0525)/2], .1835)
    entities = []
    for m in members:
        entities.extend(_tube(m['id'], m['axis'], m['center_m'], m['net_length_m'],
                              [(h['axis'], h['at_m']) for h in m['shell_holes']]))
    for i, (u, v) in enumerate(product((-.1875, .1875), (-.12, .12))):
        sign = 1 if u > 0 else -1
        # Offset the bolt55mm inboard of the leg, leaving a real socket lane.
        entities.append(_box(f'base-flange-{i}', [sign*.1625, v, -.238], [.11, .06, .004],
                             holes=[dict(axis='z', diameter_m=.009, x_m=.025 if sign>0 else .085, y_m=.03)]))
    for sign in (-1, 1):
        entities.append(_box(f'closed-back-cap-{sign}', [-.1875, sign*.1875, .3735], [.025, .025, .002]))
    pads = []
    for i, (u, v) in enumerate(product((-.12, .12), (-.1875, .1875))):
        pads.append(_box(f'pan-isolation-pad-{i}', [u, v, -.02375], [.04, .04, .0075], 'elastomer',
                         [dict(axis='z', diameter_m=.0065, x_m=.02, y_m=.02)]))
    for i, (v, z) in enumerate(product((-.1875, .1875), (.10, .30))):
        pads.append(_box(f'back-isolation-pad-{i}', [-.2025, v, z], [.005, .04, .04], 'elastomer',
                         [dict(axis='x', diameter_m=.0065, y_m=.02, z_m=.02)]))
    entities += pads
    for m in members:
        for j, h in enumerate(m['shell_holes']):
            a = h['axis']; base = h['at_m'][:]; base[a] -= .0105
            axis = [0., 0., 0.]; axis[a] = 1.
            entities.append(dict(id=f"{m['id']}/crush-sleeve-{j}", shape='tube', at_m=base,
                                 radius_m=.005, inner_radius_m=.00325, length_m=.021,
                                 axis=axis, material='al6005a'))
    cuts = [dict(piece=m['id'], quantity=1, net_m=m['net_length_m'], kerf_m=.003,
                 trim_m=.010, reserve_m=.030/len(members), section='25x25x2mm sharp-corner RHS') for m in members]
    ancillary = []
    for prefix, qty, net_size, gross_size, material in (
        ('base-flange',4,[.11,.06,.004],[.114,.064,.004],'al6005a'),
        ('closed-back-cap',2,[.025,.025,.002],[.029,.029,.002],'al6005a'),
        ('pan-isolation-pad',4,[.04,.04,.0075],[.044,.044,.0075],'elastomer'),
        ('back-isolation-pad',4,[.005,.04,.04],[.005,.044,.044],'elastomer')):
        net_volume = sum(_volume(e) for e in entities if e['id'].startswith(prefix))
        gross_volume = qty*prod(gross_size)
        ancillary.append(dict(piece=prefix, quantity=qty, material=material, net_rect_size_m=net_size,
            gross_rect_blank_size_m=gross_size, net_material_volume_m3=net_volume,
            gross_procurement_volume_m3=gross_volume, trim_and_drill_scrap_volume_m3=gross_volume-net_volume,
            basis='2mm trimming/kerf allowance per edge; holes removed in material geometry; no negative scrap credit'))
    sleeve_area = pi*(.005**2-.00325**2)
    ancillary.append(dict(piece='crush-sleeve',quantity=8,material='al6005a',outer_diameter_m=.010,
        inner_diameter_m=.0065,net_length_each_m=.021,gross_length_each_m=.025,
        kerf_each_m=.002,trim_each_m=.001,reserve_each_m=.001,
        net_material_volume_m3=8*sleeve_area*.021,gross_procurement_volume_m3=8*sleeve_area*.025,
        trim_and_drill_scrap_volume_m3=8*sleeve_area*.004))
    return dict(part_id=CHAIR, replaces='body/chair-frame', quantity=264,
                frame=dict(origin='actual stored chair-frame pattern position',
                           axes='u=stored local X (towards aisle), v=stored local Y, w=up',
                           transform='world = stored_pattern.rotation @ local + stored_pattern.positions_m[0]',
                           extra_body_lift_m=0.),
                tube_members=members, entities=entities, cuts=cuts, ancillary_cut_stock=ancillary,
                net_tube_length_m=sum(m['net_length_m'] for m in members),
                source_length_m=2.4, new_base_flange_count=4, new_cap_count=2,
                new_crush_sleeves=8, new_isolation_pads=8,
                new_base_bolt_sets=dict(bolts=4, nuts=4, washers=8, proposed='M8; grade, grip, torque and locking held'),
                new_fastener_procurement=dict(installed_sets_per_train=1056, spare_sets_per_train=22,
                    ordered_bolts=1078, ordered_nuts=1078, ordered_washers=2156,
                    basis='22complete spare sets, rounded up from2percent; spares priced but not installed mass'),
                welds=dict(joints=18, perimeter_m_each=.1, total_length_m=1.8, fillet_leg_m=.003,
                           basis='4 ring,2 upright,2 tie,8 leg/foot,2 cap; vent and weld closure drawing required'),
                material_solids_local_bounds_m=[[-.2175, -.2075, -.24], [.2175, .2075, .3745]],
                local_bounds_m=[[-.22054, -.21054, -.28004], [.22054, .21054, .37754]],
                finished_bound_basis='Material solids plus3mm weld and40um finish allowance; proposed base bolt/nut envelope extends to w=-0.28m. Threads and actual weld contours need controlled CAD.',
                finish=dict(dry_film_m=.000040, density_hypothesis_kg_m3=1300, reserve_fraction=.20),
                installation=dict(base_face_proposal_z_local_m=-.24, base_face_world_at_first_m=1.36,
                    existing_base_proxy_top_m=1.36, base_foot_overhang_beyond_proxy_m=.0075,
                    shell_interface='4 vertical pan bolts at u=+-0.12,v=+-0.1875;4 back bolts along u at v=+-0.1875,z=0.10/0.30',
                    base_interface='4 flange bolt axes along w at u=+-0.1325,v=+-0.12;55mm inboard of leg axes; pedestal holes, underside nut access and strength undefined',
                    tool_access=dict(socket_radius_m=.025, insertion_m=.10, verified=False),
                    removal_translation_local_m=[[0., 0., .10], [.65, 0., .10]],
                    handling='Remove shells first, support frame; two-hand lift or small rated aid; fixture rating pending',
                    sequence=['Cut11members; deburr and drill8paired shell-wall holes; inspect stock and sleeves',
                        'Jig ring, uprights, tie and4legs/feet; install sleeves before shell fitting; vent closed tubes before welding',
                        'Weld18declared joints, inspect distortion and welds; close2caps using approved vent/closure drawing',
                        'Prepare/coating, inspect dimensions; install8isolation pads,4new base bolt sets,8retained shell bolt sets',
                        'Verify base land, retained anchor access and shell compatibility before installation; proof/fatigue/fire tests held']),
                tolerance=dict(terms_m=dict(cut=.001, weld_distortion=.002, mounting=.002),
                    local_worst_case_m=.005, inherited_body_position_uncertainty_m=.25,
                    terms_are_proposals=True, fitted_interface_accepted=False),
                hardware_counts=dict(joints=18, bearings=0, slides=0, stops=0, new_fastener_pieces=16,
                    wiring=0, cooling_flexes=0, exact_zero_basis='passive fixed frame; separate chair/base/vehicle equipment retained'))


def seal_definition():
    # Four non-overlapping 45-degree mitred strips. Net volume=A_section*perimeter.
    w, h, t, axial = 2.35, 2.10, .012, .018
    yo, zo, yi, zi = (w+t)/2, (h+t)/2, (w-t)/2, (h-t)/2
    polygons = [
        ('top', [[-yo, zo], [yo, zo], [yi, zi], [-yi, zi]], w),
        ('right', [[yo, zo], [yo, -zo], [yi, -zi], [yi, zi]], h),
        ('bottom', [[yo, -zo], [-yo, -zo], [-yi, -zi], [yi, -zi]], w),
        ('left', [[-yo, -zo], [-yo, zo], [-yi, zi], [-yi, -zi]], h),
    ]
    entities = [dict(id=name, shape='profile', at_m=[-axial/2, 0., 0.],
                     points_yz_m=pts, length_m=axial, material='elastomer') for name, pts, _ in polygons]
    # Centreline length is neither the outside longest mitre cut nor purchased stock.
    cuts = [dict(piece=name, quantity=1, net_m=length, kerf_m=.002, trim_m=.010,
                 reserve_m=.025, section='12mm radial x18mm axial solid rectangular elastomer',
                 longest_mitre_tip_to_tip_m=length+t) for name, _, length in polygons]
    return dict(part_id=SEAL, replaces='body/terminal-end-seal', quantity=2,
                frame=dict(origin='actual stored terminal seal centre', axes='x=train X,y=train Y,z=up',
                    transform='world = stored_pattern.rotation @ local + stored_pattern.positions_m[0]', extra_body_lift_m=0.),
                entities=entities, cuts=cuts, centerline_width_m=w, centerline_height_m=h,
                section_m=[axial, t], net_profile_length_m=2*(w+h), source_length_m=7.,
                joins=dict(count=4, kind='45degree adhesive butt joints, validated compound/cure unknown',
                    adhesive_net_volume_m3=4*(axial*t*2**.5)*.0002,
                    adhesive_procurement_reserve_fraction=.5, adhesive_density_hypothesis_kg_m3=1100),
                material_solids_local_bounds_m=[[-.009, -yo, -zo], [.009, yo, zo]],
                local_bounds_m=[[-.011, -yo-.002, -zo-.002], [.011, yo+.002, zo+.002]],
                finished_bound_basis='Uncompressed manufactured loop plus2mm proposed compression-bulge allowance on all axes; not a qualified compressed shape',
                installation=dict(enclosure_gasket_only=True, gangway_bellows=False,
                    nominal_face_gap_m=.016, nominal_compression_m=.002,
                    possible_compression_bulge_allowance_m=.002, bulge_qualified=False,
                    retention='Captured between terminal panel and enclosure land by existing24panel bolt sets/end; land and compression stops undefined',
                    required_new_compression_stops='unknown; no invented zero mass or cost',
                    tool_access=dict(pick_radius_m=.02, axial_access_m=.15, verified=False),
                    removal_translation_local_m=[[0., 0., 0.], [.15, 0., 0.]],
                    handling='Support/remove terminal panel separately; peel strips with non-damaging tool; no personnel load credited',
                    sequence=['Cut4strips with45degree mitres; inspect net and longest-tip dimensions',
                        'Dry fit on flat2.35x2.10centreline jig; bond4mitres with qualified compatible adhesive; cure and inspect',
                        'Capture seal between approved mating lands; refit existing24panel bolt sets; check compression and leak/fire requirements',
                        'Replace damaged loop; retain panel supports and vehicle isolation during service']),
                tolerance=dict(terms_m=dict(profile=.001, mating_frame=.002, installation=.001),
                    face_gap_worst_case_m=.004, nominal_compression_m=.002,
                    resulting_compression_interval_m=[-.002, .006], compression_screen_passed=False,
                    inherited_body_position_uncertainty_m=.25, terms_are_proposals=True,
                    fitted_interface_accepted=False),
                hardware_counts=dict(joints=4, bearings=0, slides=0, stops=None, new_fastener_pieces=0,
                    wiring=0, cooling_flexes=0, exact_zero_basis='passive gasket;24existing panel bolt sets/end retained',
                    unknown_stop_reason='No mating land or compression-stop drawing; unresolved hardware is not zero'))


def _volume(entity):
    if entity['shape'] == 'box':
        v = prod(entity['size_m'])
        for hole in entity.get('holes', []):
            v -= pi*(hole['diameter_m']/2)**2*entity['size_m']['xyz'.index(hole['axis'])]
        return v
    if entity['shape'] == 'tube':
        return pi*(entity['radius_m']**2-entity['inner_radius_m']**2)*entity['length_m']
    p = entity['points_yz_m']
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(p, p[1:]+p[:1])))/2*entity['length_m']


def _bounds(box, rotation, at, padding=0.):
    corners = [[at[i]+sum(rotation[i][j]*p[j] for j in range(3)) for i in range(3)]
               for p in product(*zip(*box))]
    return [[min(c[i] for c in corners)-padding for i in range(3)],
            [max(c[i] for c in corners)+padding for i in range(3)]]


def _swept_bounds(part):
    # Piecewise linear translation of a rigid part: endpoint AABBs bound all t.
    boxes = [_bounds(part['local_bounds_m'], I, p) for p in part['installation']['removal_translation_local_m']]
    return [[min(b[0][i] for b in boxes) for i in range(3)],
            [max(b[1][i] for b in boxes) for i in range(3)]]


def verify_inputs(body, ownership):
    if (body.get('candidate_id'), body.get('evaluation_id')) != (BODY_ID, BODY_EVAL):
        raise ValueError('Only the explicitly held P1 body/evaluation is in scope')
    if (ownership.get('body_candidate_id'), ownership.get('body_evaluation_id'), ownership.get('evaluation_id')) != (BODY_ID, BODY_EVAL, OWNERSHIP_ID):
        raise ValueError('Sealed ownership identity differs')
    rows = {r['id']: r for r in body['parts']}
    patterns = body['patterns']
    for source, count, length in (('body/chair-frame', 264, 2.4), ('body/terminal-end-seal', 2, 7.), ('body/passage-end-seal', 10, 7.)):
        row = rows[source]
        if row['quantity_per_train'] != count or row['stock']['length_m'] != length:
            raise ValueError('Source stock ownership differs: '+source)
        if sum(p['count'] for p in patterns if p['part_id'] == source) != count:
            raise ValueError('Source occurrence count differs: '+source)
        for p in (p for p in patterns if p['part_id'] == source):
            R = p['rotation']
            if (len(R)!=3 or any(len(row)!=3 for row in R)
                or any(not isfinite(x) for row in R for x in row)
                or any(abs(sum(R[k][i]*R[k][j] for k in range(3))-(1 if i==j else 0))>1e-9 for i in range(3) for j in range(3))):
                raise ValueError('Rigid orthonormal source transform required')
            det = (R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])
                   -R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])
                   +R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0]))
            if abs(det-1)>1e-9 or any(len(at)!=3 or any(not isfinite(x) for x in at) for at in p['positions_m']):
                raise ValueError('Proper finite rigid source transform required')
    source_ownership = {r['part_id']: r for r in ownership['parts']}
    for source in ('body/chair-frame', 'body/terminal-end-seal'):
        if source_ownership[source]['component_definition_id'] != rows[source]['component_definition_id']:
            raise ValueError('Source component identity differs')
    for source, (n, _) in HARDWARE.items():
        row = rows[source]; qty = 264 if source.startswith('body/chair') else 2
        if row['quantity_per_train'] != n*qty or row['quantity_per_assembly'] != n:
            raise ValueError('Hardware count differs: '+source)
    return rows


def evaluate(body, ownership, *, input_sha256, source_sha256):
    rows = verify_inputs(body, ownership)
    parts = [chair_definition(), seal_definition()]
    bindings = []
    for part in parts:
        part['component_geometry_id'] = identity(dict(entities=part['entities'], bounds=part['local_bounds_m']))
        part['component_definition_id'] = identity(part)
        part['removal_swept_local_bounds_m'] = _swept_bounds(part)
        for p in body['patterns']:
            if p['part_id'] == part['replaces']:
                if p['count'] != 1 or len(p['positions_m']) != 1:
                    raise ValueError('Explicit single source leaf transform required')
                bindings.append(dict(part_id=part['part_id'], source_pattern_id=p['id'],
                    source_assembly_occurrence_id=p['assembly_occurrence_id'],
                    rotation=deepcopy(p['rotation']), translation_m=p['positions_m'][0][:],
                    local_proposed_tolerance_m=.005 if part['part_id'] == CHAIR else .004,
                    inherited_position_uncertainty_m=p['uncertainty_m'][:],
                    finished_nominal_bounds_m=_bounds(part['local_bounds_m'], p['rotation'], p['positions_m'][0])))
                binding = bindings[-1]
                strokes = deepcopy(part['installation']['removal_translation_local_m'])
                if part['part_id'] == SEAL:
                    sign = -1 if p['positions_m'][0][0] < 1 else 1
                    for stroke in strokes:
                        stroke[0] *= sign
                    binding['terminal_outward_world_x_sign'] = sign
                swept = [_bounds(part['local_bounds_m'], p['rotation'],
                    [p['positions_m'][0][i]+sum(p['rotation'][i][j]*s[j] for j in range(3)) for i in range(3)]) for s in strokes]
                binding['finished_removal_swept_bounds_m'] = [[min(b[0][i] for b in swept) for i in range(3)],
                                                            [max(b[1][i] for b in swept) for i in range(3)]]
    physical = dict(schema='osr-finished-fitout-physical/1', parent_body_candidate_id=BODY_ID,
        parts=parts, installed_bindings=bindings, revisions='Replace two leaf families only; research draft; not full-body propagation')
    candidate = identity(physical)
    hardware = []
    for source, (n, use) in HARDWARE.items():
        row = rows[source]
        hardware.append(dict(source_part_id=source, component_definition_id=row['component_definition_id'],
            use=use, retained_quantity_per_train=row['quantity_per_train'], quantity_per_assembly=n,
            retained_mass_each_kg=row['mass_each_kg'], retained_direct_cost_each_usd=row['direct_cost_each_usd'],
            added_again_mass_kg=0., added_again_cost_usd=0., position_and_grade_qualified=False))
    changes = []
    for part in parts:
        source = rows[part['replaces']]
        volumes = {m: sum(_volume(e) for e in part['entities'] if e['material'] == m) for m in ('al6005a', 'elastomer')}
        net = part.get('net_tube_length_m', part.get('net_profile_length_m'))
        gross = sum(c['net_m']+c['kerf_m']+c['trim_m']+c['reserve_m'] for c in part['cuts'])
        part['stock_summary'] = dict(net_centerline_length_m=net, gross_procurement_length_m=gross,
            kerf_m=sum(c['kerf_m'] for c in part['cuts']), trim_scrap_m=sum(c['trim_m'] for c in part['cuts']),
            reserve_m=sum(c['reserve_m'] for c in part['cuts']), gross_minus_net_m=gross-net,
            source_length_m=part['source_length_m'], source_stock_shortfall_m=max(0., gross-part['source_length_m']),
            longest_tip_allowance_accounting='Seal trim0.010m +reserve0.025m perpiece exceed 0.012m mitre-tip addition; no double counting')
        masses = {}; costs = {}; components = {}
        for i, c in enumerate(CASES):
            if part['part_id'] == CHAIR:
                # Density sensitivity is an evaluation hypothesis, not three geometries.
                rho = (2600., 2710., 2800.)[i]
                weld = 18*.1*(.003**2/2)*rho
                area = .1*net + 4*(2*.11*.06+2*(.11+.06)*.004) + 2*.025*.025*2
                finish = area*.000040*1300
                new_hardware = 4*(.028, .040, .060)[i]+4*(.005, .008, .012)[i]+8*(.002, .003, .005)[i]
                mass = volumes['al6005a']*rho+volumes['elastomer']*1200+weld+finish+new_hardware
                ancillary_al = sum(s['gross_procurement_volume_m3'] for s in part['ancillary_cut_stock'] if s['material']=='al6005a')*rho
                gross_metal = gross*.000184*rho + ancillary_al
                stock_cost = (gross_metal+weld*1.2)*body['policy']['rates']['aluminium_usd_kg'][i]
                labour_h = (.8, 1.2, 2.)[i]
                consumables = (1.5, 3., 6.)[i] + finish*1.2*(10., 16., 25.)[i]
                hardware_cost = (4*(.35, .65, 1.2)[i]+4*(.1, .2, .4)[i]+8*(.04, .08, .15)[i])*(1078/1056)
                pad_cost = (1., 2., 4.)[i]
                direct = stock_cost+labour_h*body['policy']['rates']['labour_usd_h'][i]+consumables+hardware_cost+pad_cost
                cost = direct*(1+body['policy']['rates']['overhead_fraction'][i])
                components[c] = dict(material_solids_kg=volumes['al6005a']*rho,
                    isolation_pads_kg=volumes['elastomer']*1200, weld_kg=weld, finish_kg=finish,
                    new_fastener_pieces_kg=new_hardware, process_hours=labour_h,
                    gross_tube_mass_kg=gross*.000184*rho, gross_ancillary_al_stock_kg=ancillary_al,
                    gross_isolation_pad_volume_m3=sum(s['gross_procurement_volume_m3'] for s in part['ancillary_cut_stock'] if s['material']=='elastomer'),
                    weld_filler_procurement_kg=weld*1.2, finish_procurement_kg=finish*1.2,
                    stock_cost_usd=stock_cost)
            else:
                adhesive = part['joins']['adhesive_net_volume_m3']*1100
                mass = volumes['elastomer']*(1100., 1200., 1300.)[i]+adhesive
                rate = source['direct_cost_each_usd'][c]/7.
                # Retained all-in profile rate already contains routine process:
                # only new four mitre-bond labour/adhesive is added here.
                joint_hours = (.12, .25, .5)[i]
                cost = gross*rate+joint_hours*body['policy']['rates']['labour_usd_h'][i]+(1., 2., 5.)[i]
                components[c] = dict(material_solids_kg=volumes['elastomer']*(1100.,1200.,1300.)[i],
                    adhesive_installed_kg=adhesive, adhesive_procurement_kg=adhesive*1.5,
                    retained_source_composite_rate_usd_m=rate, added_joint_process_hours=joint_hours)
            masses[c] = mass; costs[c] = cost
        qty = part['quantity']
        changes.append(dict(part_id=part['part_id'], quantity_per_train=qty,
            source_component_definition_id=source['component_definition_id'], stock=part['stock_summary'],
            source_net_allowance_mass_each_kg=source['mass_each_kg'], proposed_component_mass_each_kg=masses,
            proposed_component_direct_cost_each_usd=costs, evaluation_components=components,
            train_mass_delta_kg={c: qty*(masses[c]-source['mass_each_kg'][c]) for c in CASES},
            train_direct_cost_delta_usd={c: qty*(costs[c]-source['direct_cost_each_usd'][c]) for c in CASES},
            complete_installed_mass=False, complete_installed_cost=False))
    # Physical identity includes stock accounting, so seal it after completing it.
    for p in parts:
        p['component_definition_id'] = identity({k:v for k,v in p.items() if k != 'component_definition_id'})
    candidate = identity(physical)
    for change, p in zip(changes, parts):
        change['proposed_component_definition_id'] = p['component_definition_id']
    result = dict(schema='osr-finished-fitout-evaluation/1', physical_definition=physical, candidate_id=candidate,
        parent_body_candidate_id=BODY_ID, parent_body_evaluation_id=BODY_EVAL, selection_id=None,
        input_sha256=input_sha256, source_sha256=source_sha256, changes=changes, retained_hardware=hardware,
        retained_passage_gaskets=dict(source_part_id='body/passage-end-seal', quantity=10, developed_length_each_m=7.,
            mass_each_kg=rows['body/passage-end-seal']['mass_each_kg'], direct_cost_each_usd=rows['body/passage-end-seal']['direct_cost_each_usd'],
            component_definition_id=rows['body/passage-end-seal']['component_definition_id'], removed=False, added_again=False),
        source_datums=dict(stored_floor_top_m=body['policy']['layout']['floor_top_m'],
            stored_policy_seat_pan_m=body['policy']['layout']['seat_pan_z_m'], actual_chair_frame_pattern_z_m=1.6,
            assembly_anchor_seat_pan_m=1.45, discrepancy_m=.15, added_lift_m=0.,
            reconciliation='Future full-body revision must reconcile seat/passenger datums before reusing mass,CG,axle and lateral-load results'),
        execution=dict(kind='analytical two-component definition only', native_jobs=0, full_body_materializations=0,
            numerical_validity='deterministic geometry/accounting; physical input hypotheses unqualified',
            engineering_screen='held: base/end lands, tolerances, hardware and physical qualification incomplete',
            evidence_maturity='research definition; no authenticated physical measurements', selection_purpose='independent review only'),
        total_train_delta_kg={c:sum(x['train_mass_delta_kg'][c] for x in changes) for c in CASES},
        total_train_direct_cost_delta_usd={c:sum(x['train_direct_cost_delta_usd'][c] for x in changes) for c in CASES},
        price_basis='Calculated source-policy aluminium/labour/overhead; explicit research process/consumable/hardware hypotheses. Seal source composite$/m retained; new mitre joining added once. No supplier quote or country discount. Qualification, delivery, tax and unresolved integration excluded and unknown.',
        limitations=[
            'Two new leaf definitions do not propagate or select a full vehicle. P1 ancestors remain unchanged; no P4 identity is inherited.',
            'Tube sharp corners/densities and solid rectangular elastomer are proposed specifications, not supplier measurements or fire certificates.',
            'CAD commands cover declared material solids and holes; weld beads,coating and purchased fastener thread shapes remain unmodelled with positive mass/cost allowances.',
            'Existing source fixing quantities/masses/costs are retained once; grade/grip/locations,8shell bolt compatibility and base/end lands need controlled drawings.',
            'Local removal sweeps are finite translated rigid envelopes; collisions, adjacent shells/pedestal/panel handling, lifting capacity and tool paths remain unverified.',
            'Gasket compression2mm +/-4mm fails positive-compression screen. Stops or revised lands may add unknown hardware,mass,cost; no acceptance.',
            'Source0.25m position uncertainty is preserved; proposed5/4mm manufacturing stack cannot replace it.',
            'Train yaw,pitch,gangway,articulation,couplers,terminal crash protection and passenger/evacuation/fire/accessibility obligations remain separate and open.',
            'Source unlocated installation reserve remains positive and unlocated; delta is a partial component subtotal, not complete installed mass or cost.'],
        **FLAGS)
    result['evaluation_id'] = identity(result)
    return result


def cad_case(result, part):
    return dict(case_id=part['part_id'], candidate_id=result['candidate_id'],
        component_geometry_id=part['component_geometry_id'], source_evaluation_id=result['evaluation_id'],
        entities=deepcopy(part['entities']), materials=dict(al6005a=dict(density_kg_m3=2710),elastomer=dict(density_kg_m3=1200)),
        scope='Local proposed material solids, not full installed body; explicit non-CAD weld/finish/fastener allowances', **FLAGS)


def svg(part):
    """Small local orthographic vector drawing, dimension text stays in SI."""
    if part['part_id'] == CHAIR:
        lines = []
        for m in part['tube_members']:
            a = m['center_m'][:]; b = a[:]
            a[m['axis']] -= m['net_length_m']/2; b[m['axis']] += m['net_length_m']/2
            lines.append(f'<line x1="{250+a[0]*600}" y1="{330-a[2]*600}" x2="{250+b[0]*600}" y2="{330-b[2]*600}"/>')
        content = '<g stroke="#15566c" stroke-width="15">'+''.join(lines)+'</g>'
        text = 'Chair local u-w; material envelope0.435u x0.415v x0.6145w m; transverse rails project to points'
    else:
        content = '<rect x="113" y="68" width="282" height="252" fill="none" stroke="#15566c" stroke-width="2"/>'
        text = 'Terminal gasket local y-z; centreline2.35 x2.10m; section12radial x18axial mm;4mitres'
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="450" viewBox="0 0 760 450">'
        '<rect width="760" height="450" fill="white"/>'+content+
        '<g font-family="sans-serif" font-size="12" fill="#202b30"><text x="20" y="25">RESEARCH PROPOSAL — NOT MANUFACTURING RELEASE</text>'+
        f'<text x="20" y="400">{text}</text><text x="20" y="425">Source transforms, cutlist, holes and holds: report.json / CAD command definitions. Native CAD not run.</text></g></svg>').encode()


def write_outputs(result, output):
    out = Path(output); out.mkdir(exist_ok=False)
    (out/'report.json').write_bytes(encoded(result))
    with (out/'cutlist.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['part_id','piece','quantity_per_part','net_centerline_m','kerf_m','trim_m','reserve_m','gross_m','section'])
        for p in result['physical_definition']['parts']:
            for c in p['cuts']:
                w.writerow([p['part_id'],c['piece'],1,c['net_m'],c['kerf_m'],c['trim_m'],c['reserve_m'],
                            sum(c[k] for k in ('net_m','kerf_m','trim_m','reserve_m')),c['section']])
    for p, stem in zip(result['physical_definition']['parts'], ('chair','terminal-seal')):
        case = cad_case(result,p)
        (out/(stem+'-case.json')).write_bytes(encoded(case))
        (out/(stem+'-commands.json')).write_bytes(encoded(solidcraft.script_for(case)))
        (out/(stem+'.svg')).write_bytes(svg(p))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--body', required=True, type=Path); ap.add_argument('--ownership', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    if digest(args.body) != BODY_SHA:
        raise ValueError('Held body gzip hash differs')
    manifest_path = args.ownership.parent/'final-manifest.json'
    if digest(manifest_path) != OWNERSHIP_MANIFEST_SHA:
        raise ValueError('Authoritative ownership manifest hash differs')
    manifest = json.loads(manifest_path.read_bytes())
    required = ['README.md', 'OWNERSHIP.md', args.ownership.name]
    declared = {r['path']:r['sha256'] for r in manifest['files']}
    for name in required:
        if digest(args.ownership.parent/name) != declared[name]:
            raise ValueError('Sealed ownership packet changed: '+name)
    root = Path(__file__).resolve().parents[1]
    source_names = ['AGENTS.md','engineering/finished_fitout.py','tests/test_finished_fitout.py',
                    'engineering/design_search/craft_backends/solidcraft.py']
    sources = {n:digest(root/n) for n in source_names}
    input_paths = [args.body, manifest_path]+[args.ownership.parent/n for n in required]
    inputs = {str(p):digest(p) for p in input_paths}
    body = json.loads(gzip.decompress(args.body.read_bytes()))
    if identity(body['physical_definition']) != BODY_ID:
        raise ValueError('Held body canonical physical identity differs')
    ownership = json.loads(args.ownership.read_bytes())
    result = evaluate(body,ownership,input_sha256=inputs,source_sha256=sources)
    write_outputs(result,args.output)
    if inputs != {str(p):digest(p) for p in input_paths} or sources != {n:digest(root/n) for n in source_names}:
        raise ValueError('Input/source drift; retain run as failed')
    print(json.dumps(dict(candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],
        output=str(args.output), **FLAGS),sort_keys=True))


if __name__ == '__main__':
    main()
