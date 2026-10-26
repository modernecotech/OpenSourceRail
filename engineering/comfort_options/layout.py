"""Bounded, source-bound seating alternatives; no accessibility or vehicle release.

All dimensions below are declared research design hypotheses, not standards.
Rectangles are occupied plan envelopes (including knee space), not just pans.
The generator maximises 2+2 rows in each unobstructed interval, leaves door
vestibules clear, and uses opposite-wall benches only with one-sided doors.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'osr-comfort-layout/1'
SOURCE_FILES = (
    'engineering/ferrite_maglev/station-structure.toml',
    'engineering/ferrite_maglev/station_structure.py',
    'engineering/ferrite_maglev/closure.py',
    'engineering/ferrite_maglev/data/candidate-parent-94ad.json',
    'engineering/ferrite_maglev/data/candidate-retained-body-stock.json',
    'engineering/ferrite_maglev/data/candidate-replaced-cartridges.json',
    'engineering/ferrite_maglev/reference-configuration.toml',
)
TOPOLOGIES = ('two-sided-2plus2', 'one-sided-2', 'one-sided-3', 'one-sided-4')
SEAT_OPTIONS = (
    dict(id='pan450-pitch800', seat_width_m=.45, module_width_m=.47, pitch_m=.80),
    dict(id='pan450-pitch850', seat_width_m=.45, module_width_m=.47, pitch_m=.85),
    dict(id='pan480-pitch900-width-control', seat_width_m=.48, module_width_m=.50, pitch_m=.90),
)
FALSE_FLAGS = dict(design_complete=False, engineering_accepted=False,
                   accessibility_approved=False, physical_validation=False,
                   manufacturing_release=False, physical_release=False)


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode()).hexdigest()


def _sources(root):
    return {name: sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def _rect(identity, kind, x0, x1, y0, y1, **extra):
    return dict(id=identity, kind=kind, x0_m=float(x0), x1_m=float(x1),
                y0_m=float(y0), y1_m=float(y1), **extra)


def _overlap(a, b):
    return (min(a['x1_m'], b['x1_m']) - max(a['x0_m'], b['x0_m']) > 1e-9
            and min(a['y1_m'], b['y1_m']) - max(a['y0_m'], b['y0_m']) > 1e-9)


def _area(r):
    return (r['x1_m'] - r['x0_m']) * (r['y1_m'] - r['y0_m'])


def _subtract(intervals, cuts):
    for a, b in cuts:
        out = []
        for low, high in intervals:
            if b <= low or a >= high:
                out.append((low, high))
            else:
                if low < a:
                    out.append((low, a))
                if b < high:
                    out.append((b, high))
        intervals = out
    return intervals


def _audit(root):
    parent = json.loads((root / SOURCE_FILES[3]).read_text())['configuration']
    sources = _sources(root)
    for name in SOURCE_FILES[:3]:
        if parent['source_sha256'].get(name) != sources[name]:
            raise ValueError('historical interior allocation source chain differs')
    a = tomllib.loads((root / SOURCE_FILES[0]).read_text())
    reference = tomllib.loads((root / SOURCE_FILES[6]).read_text())
    if reference['formation']['doors_per_side_x_m'] != [-4.5, 4.5]:
        raise ValueError('retained aperture centres changed; regenerate geometry contract')
    body = a['body']; central = body['cases']['central']
    if central['interior_kg'] != 800 or (body['length_m'], body['width_m']) != (17., 2.65):
        raise ValueError('interior allowance or body reference changed')
    retained = json.loads((root / SOURCE_FILES[4]).read_text())
    replaced = json.loads((root / SOURCE_FILES[5]).read_text())
    residual = (parent['controlled_tare_kg'] - replaced['mass_kg_per_car']
                - parent['magnetic']['winding_copper_kg_per_car'] - retained['mass_kg_per_car'])
    if residual < central['interior_kg']:
        raise ValueError('retained unlocated allowance cannot cover ancestral interior account')
    # Shell-side layers provide the actual inside faces, rather than treating
    # the exterior2.65m width as a clear cabin. Posts remain separate obstacles.
    sides = [p for p in retained['parts'] if p['role'] == 'panel-side']
    lower = max(p['at_m'][1] + p['size_m'][1] for p in sides if p['at_m'][1] < 0)
    upper = min(p['at_m'][1] for p in sides if p['at_m'][1] > 0)
    groups = {}
    for p in retained['parts']:
        if p['id'].startswith('frame/side-') and '-post-' in p['id']:
            name = p['id'].split('/wall-')[0]
            r = _rect(name, 'retained-side-post', p['at_m'][0], p['at_m'][0]+p['size_m'][0],
                      p['at_m'][1], p['at_m'][1]+p['size_m'][1])
            if name in groups:
                old = groups[name]
                for k in ('x0_m', 'y0_m'):
                    r[k] = min(old[k], r[k])
                for k in ('x1_m', 'y1_m'):
                    r[k] = max(old[k], r[k])
            groups[name] = r
    return dict(parent_configuration_sha256=parent['configuration_sha256'],
                retained_unlocated_allocation_kg=residual, interior_allowance_kg=800.,
                interior_account='body.cases.central.interior_kg',
                source_chain_sha_matches={k: True for k in SOURCE_FILES[:3]},
                sources=sources, body=body, cabin_y0_m=lower, cabin_y1_m=upper,
                retained_side_posts=list(groups.values()))


def _stock(identity, quantity, volume_each, density, **extra):
    return dict(id=identity, quantity=quantity, volume_m3_each=volume_each,
                density_kg_m3=density, unit_mass_kg=volume_each*density,
                mass_kg=quantity*volume_each*density, **extra)


def _seating_stock(seats, option):
    rows = []
    # Explicitly counted lightweight GFRP pans/backs, pads, Al mounting stock
    # and four stock M8 fasteners per place. These are material proposals,
    # without restraint/fatigue/fire qualification or an installed seat mass.
    for kind in ('transverse-seat', 'wall-bench-seat'):
        count = sum(r['kind'] == kind for r in seats)
        width = option['seat_width_m']
        rows += [
            _stock(kind+'/GFRP-pan-back', count, width*(.48+.60)*.002, 1900.,
                   dimensions_m=dict(clear_pan_width=width, pan_depth=.48, back_height=.60, thickness=.002)),
            _stock(kind+'/foam-pad', count, width*.48*.03, 50.,
                   dimensions_m=dict(width=width, depth=.48, thickness=.03)),
            _stock(kind+'/Al-RHS-mounts', count, (.03*.03-.026*.026)*.9, 2700.,
                   dimensions_m=dict(outer_width=.03, wall=.002, total_length=.9)),
            _stock(kind+'/M8-stock-fasteners', count*4,
                   math.pi*(.008/2)**2*.05 + math.pi*(.014/2)**2*.01, 7850.,
                   dimensions_m=dict(shank_diameter=.008, shank_length=.05,
                                     head_nut_equivalent_diameter=.014, head_nut_equivalent_length=.01)),
        ]
    return dict(total_mass_kg=math.fsum(r['mass_kg'] for r in rows), stock_parts=rows,
                installed_mass_kg=None, evidence='dimensioned research material proposal',
                bench_mass_is_counted=True,
                unknown=['Upholstery/fire treatment and qualified restraint loads',
                         'Body hardpoint reinforcement, isolation and complete retention details'],
                **FALSE_FLAGS)


def _infill_stock(audit, topology):
    body = audit['body']; central = body['cases']['central']
    count = 0 if topology == TOPOLOGIES[0] else 2
    area = body['door_width_m'] * body['door_height_m']
    rows = [_stock('infill/GFRP-skins', count, area*2*central['upper_face_each_m'], body['face_density_kg_m3']),
            _stock('infill/H80-core', count, area*central['upper_core_m'], central['upper_core_density_kg_m3'])]
    finish = count*area*central['upper_bond_finish_kg_m2']
    return dict(blanked_original_openings=count, area_m2=count*area,
                stock_parts=rows, bond_finish_allowance_kg=finish,
                total_mass_kg=math.fsum(r['mass_kg'] for r in rows)+finish,
                installed_mass_kg=None, retained_original_opening_frames=True,
                new_openings=max(0, int(topology.rsplit('-', 1)[-1])-2) if topology != TOPOLOGIES[0] else 0,
                cut_material_removal_credit_kg=0.,
                unknown=['Infill joints, edge closure, sealing and exact attachment mass',
                         'Added openings require verified aperture reinforcement and installation geometry'],
                basis='Two deleted original opposite-side doors are filled even when new doors are added on boarding side; no net-door-count shortcut',
                **FALSE_FLAGS)


def _arrangement(centres, one_side, option, audit, vestibule_length, location):
    """Deterministic row offsets and three explicit wheelchair arrangements."""
    y0, y1 = audit['cabin_y0_m'], audit['cabin_y1_m']
    half = .325; pitch = option['pitch_m']; module = option['module_width_m']
    vh = vestibule_length/2
    vestibules = [_rect(f'vestibule/{i}', 'vestibule', x-vh, x+vh, y0, y1)
                  for i, x in enumerate(centres)]
    intervals = _subtract([(-7.5, 7.5)], [(r['x0_m'], r['x1_m']) for r in vestibules])
    if location == 'outer-ends':
        bx = [(-7.5, -6.2), (6.2, 7.5)]
    elif location == 'opposite-door':
        bx = [(-5.15, -3.85), (3.85, 5.15)]
    elif location == 'adjacent-doors':
        bx = [(-4.5+vh, -4.5+vh+1.3), (4.5-vh-1.3, 4.5-vh)]
    else:
        raise ValueError('unknown wheelchair arrangement')
    wheelchairs = [_rect(f'wheelchair/{i}', 'wheelchair', low, high, y0+.0303, y0+.8303)
                   for i, (low, high) in enumerate(bx)]
    paths = [_rect('aisle', 'shared-standing-and-circulation', -7.5, 7.5, -half, half)]
    for i, centre in enumerate(centres):
        paths.append(_rect(f'boarding/left/{i}', 'door-to-aisle', centre-.4, centre+.4, -half, y1))
        if not one_side:
            paths.append(_rect(f'boarding/right/{i}', 'door-to-aisle', centre-.4, centre+.4, y0, half))
    for i, sign in enumerate((-1, 1)):
        centre = sign*4.5
        if location == 'opposite-door':
            paths.append(_rect(f'wheelchair-route/{i}/longitudinal', 'assigned-bay-access',
                               centre-.4, centre+.4, y0+.0303, .4))
        else:
            # A0.8m corridor at the appropriate vestibule end joins a free
            # longitudinal bay route to the free aisle/boarding rectangle.
            corner = centre+sign*(vh-.8) if location=='outer-ends' else centre-sign*(vh-.8)
            low, high = sorted((corner, corner+sign*.8 if location=='outer-ends' else corner-sign*.8))
            a, b = min(low, bx[i][0]), max(high, bx[i][1])
            paths.append(_rect(f'wheelchair-route/{i}/longitudinal', 'assigned-bay-access', a, b, y0+.0303, y0+.8303))
            paths.append(_rect(f'wheelchair-route/{i}/lateral', 'assigned-bay-access', low, high, y0+.0303, .4))
            paths.append(_rect(f'wheelchair-route/{i}/link', 'assigned-bay-access',
                               min(low, centre-.4), max(high, centre+.4), -.4, .4))
        paths.append(_rect(f'turning/{i}', 'research-clear-turn-square', centre-.75,
                           centre+.75, -.40 if location=='opposite-door' else -.60,
                           1.10 if location=='opposite-door' else .90))
    benches = []; omissions = []
    for i, centre in enumerate(centres):
        outer = abs(centre)==4.5
        if not one_side or (outer and location=='opposite-door'):
            omissions.append(dict(door=i, reason='Wheelchair users occupy opposite-door bay' if one_side
                                  else 'Both sides have door apertures; no fixed bench across a boarding opening'))
            continue
        available = vestibule_length-(.85 if outer else 0.)
        count = max(0, int(math.floor((available+1e-9)/module)))
        length = count*module
        # Leave the free0.85m end towards the assigned bay.
        inward = location=='outer-ends'
        bench_at_high_end = (centre < 0) == inward
        low = centre+vh-length if outer and bench_at_high_end else centre-vh if outer else centre-length/2
        for j in range(count):
            benches.append(_rect(f'bench/{i}/{j}', 'wall-bench-seat', low+j*module,
                                  low+(j+1)*module, y0+.0153, y0+.6153,
                                  direction='+y', clear_pan_width_m=option['seat_width_m'],
                                  fixture_module_width_m=module, occupant_depth_m=.60))
    seats = list(benches); offset_trials = []
    obstacles = wheelchairs+paths[1:]+audit['retained_side_posts']+benches
    for segment, (low, high) in enumerate(intervals):
        count = int(math.floor((high-low+1e-9)/pitch))
        slack = max(0., high-low-count*pitch)
        # A bounded10mm row-origin grid plus exactendpoints. A projecting
        # post removes only the colliding individual place, never a whole row.
        offsets = sorted(set([0., slack]+[i*.01 for i in range(int(slack/.01)+1)]))
        options = []
        for offset in offsets:
            stock = []
            for row in range(count):
                x = low+offset+row*pitch
                for bank in (-1, 1):
                    for place in range(2):
                        a, b = half+place*module, half+(place+1)*module
                        lower, upper = (a,b) if bank==1 else (-b,-a)
                        rect = _rect(f'seat/{segment}/{row}/{bank}/{place}', 'transverse-seat',
                                     x,x+pitch,lower,upper,direction='+x',
                                     clear_pan_width_m=option['seat_width_m'],fixture_module_width_m=module,row_pitch_m=pitch)
                        if not any(_overlap(rect, obstruction) for obstruction in obstacles):
                            stock.append(rect)
            options.append((len(stock), offset, stock))
        best = max(options, key=lambda x: (x[0], -abs(x[1]-slack/2), -x[1]))
        seats += best[2]
        offset_trials.append(dict(interval_m=[low,high], row_origins_tested=len(offsets),
                                  chosen_offset_m=best[1], retained_transverse_places=best[0]))
    # Opposite-door bays on a two-sided vehicle block that side's aperture.
    conflicts = []
    if not one_side:
        conflicts = [[bay['id'], p['id']] for bay in wheelchairs for p in paths
                     if p['id'].startswith('boarding/right/') and _overlap(bay,p)]
    objects=seats+wheelchairs
    violations = conflicts+[[a['id'],b['id']] for i,a in enumerate(objects)
                             for b in objects[i+1:] if _overlap(a,b)]
    violations += [[bay['id'],post['id']] for bay in wheelchairs
                   for post in audit['retained_side_posts'] if _overlap(bay,post)]
    violations += [[path['id'],seat['id']] for path in paths for seat in seats if _overlap(path,seat)]
    return dict(seats=seats,wheelchairs=wheelchairs,paths=paths,vestibules=vestibules,
                open_intervals=intervals,bench_reasons=omissions,offset_trials=offset_trials,
                wheelchair_location=location,blocked_door_bays=conflicts,packing_violations=violations)


def _generate(topology, option, standing_count, audit, vestibule_length=1.8, wheelchair_location='benches-first'):
    if topology not in TOPOLOGIES:
        raise ValueError('unknown door topology')
    if type(standing_count) is not int or not 0 <= standing_count <= 160:
        raise ValueError('standing count outside bounded0..160 layout domain')
    if any(not math.isfinite(option[k]) or option[k] <= 0 for k in ('seat_width_m', 'module_width_m', 'pitch_m')):
        raise ValueError('finite positive seating dimensions required')
    if not (.5 <= option['pitch_m'] <= 1.2 and .35 <= option['seat_width_m'] <= .55
            and .35 <= option['module_width_m'] <= .60):
        raise ValueError('seating dimensions outside bounded research domain')
    if vestibule_length not in (1.5,1.8,2.4):
        raise ValueError('vestibule length outside bounded1.5/1.8/2.4m research family')
    one_side = topology != TOPOLOGIES[0]
    centres = [-4.5, 4.5]
    if topology == 'one-sided-3':
        centres = [-4.5, 0., 4.5]
    if topology == 'one-sided-4':
        centres = [-4.5, -1.5, 1.5, 4.5]
    y0, y1 = audit['cabin_y0_m'], audit['cabin_y1_m']
    aisle=.65; pitch=option['pitch_m']; module=option['module_width_m']
    locations = ('outer-ends','adjacent-doors','opposite-door') if wheelchair_location in ('best-fit','benches-first') else (wheelchair_location,)
    trials = [_arrangement(centres,one_side,option,audit,vestibule_length,location) for location in locations]
    arranged = max(trials,key=lambda a: (not a['packing_violations'],
                  wheelchair_location=='benches-first' and one_side and a['wheelchair_location']!='opposite-door',
                  len(a['seats'])))
    seats=arranged['seats']; wheelchairs=arranged['wheelchairs']; paths=arranged['paths']
    vestibules=arranged['vestibules']; open_intervals=arranged['open_intervals']; bench_reasons=arranged['bench_reasons']
    standing_slots = []
    for segment, (low, high) in enumerate(open_intervals):
        count = int(math.floor((high-low+1e-9)/.40))
        start = (low+high-count*.40)/2
        for i in range(count):
            standing_slots.append(_rect(f'standing/{segment}/{i}', 'standing',
                                        start+i*.40, start+(i+1)*.40, -.25, .25))
    standing = standing_slots[:standing_count]
    occupants = seats+wheelchairs+standing
    bounds = _rect('clear-envelope', 'cabin', -7.5, 7.5, y0, y1)
    out_of_bounds = [r['id'] for r in occupants if any((r['x0_m'] < bounds['x0_m']-1e-9,
                                                       r['x1_m'] > bounds['x1_m']+1e-9,
                                                       r['y0_m'] < bounds['y0_m']-1e-9,
                                                       r['y1_m'] > bounds['y1_m']+1e-9))]
    collisions = [[a['id'], b['id']] for i, a in enumerate(occupants)
                  for b in occupants[i+1:] if _overlap(a, b)]
    post_collisions = [[r['id'], post['id']] for r in occupants
                       for post in audit['retained_side_posts'] if _overlap(r, post)]
    blocked_paths = [[path['id'], seat['id']] for path in paths for seat in seats if _overlap(path, seat)]
    edges = [[a['id'], b['id']] for i, a in enumerate(paths) for b in paths[i+1:] if _overlap(a, b)]
    adjacent = {p['id']: set() for p in paths}
    for a, b in edges:
        adjacent[a].add(b); adjacent[b].add(a)
    route_checks = []
    for i, bay in enumerate(wheelchairs):
        start = f'wheelchair-route/{i}/longitudinal'
        target = 'boarding/left/0' if i == 0 else f'boarding/left/{len(centres)-1}'
        seen = {start}; queue = [start]
        while queue:
            node = queue.pop()
            for other in adjacent[node]-seen:
                seen.add(other); queue.append(other)
        route_checks.append(dict(wheelchair_bay=bay['id'], assigned_door=target,
                                 rectangle_union_connected=target in seen,
                                 swept_route_approved=False))
    standing_area = math.fsum((high-low)*aisle for low, high in open_intervals)
    density = standing_count/standing_area if standing_area else math.inf
    failures = []
    if pitch < .80-1e-9:
        failures.append('row-pitch-below-declared-800mm-comfort-screen')
    if option['seat_width_m'] < .45-1e-9:
        failures.append('clear-seat-pan-below-declared-450mm-screen')
    if module-option['seat_width_m'] < .02-1e-9:
        failures.append('seat-module-lacks-declared-shared-fixture-allowance')
    if out_of_bounds:
        failures.append('seat-module-or-occupant-exceeds-clear-cabin')
    if collisions or post_collisions:
        failures.append('occupied-envelope-collision')
    if blocked_paths:
        failures.append('fixed-seating-obstructs-declared-access-path')
    if arranged['blocked_door_bays']:
        failures.append('wheelchair-bay-blocks-opposite-side-door')
    if not all(r['rectangle_union_connected'] for r in route_checks):
        failures.append('assigned-wheelchair-bay-has-no-connected-access-path')
    if standing_count > len(standing_slots):
        failures.append('insufficient-nonoverlapping-standing-slots')
    if density > 3.5+1e-9:
        failures.append('standing-density-exceeds-declared-3.5-persons-per-m2-screen')
    count = len(seats); passenger_limit = count+2+standing_count
    seat_stock = _seating_stock(seats, option); infill = _infill_stock(audit, topology)
    known = seat_stock['total_mass_kg']; allowance = audit['interior_allowance_kg']
    doors = len(centres)*(1 if one_side else 2)
    controls = []
    for limit in (80, 100, 120):
        required = max(0, limit-count-2)
        reasons = []
        if required > len(standing_slots):
            reasons.append('insufficient-standing-contact-slots')
        if required/standing_area > 3.5:
            reasons.append('standing-density-above-declared-comfort-screen')
        if limit < count+2:
            reasons.append('cap-lower-than-installed-seats-plus-wheelchair-users')
        controls.append(dict(proposed_passenger_limit=limit, required_standing=required,
                             standing_density_persons_m2=required/standing_area,
                             engineering_screen='fail' if reasons or failures else 'pass',
                             failure_reasons=reasons+failures,
                             scope='Demand-control comparison, not the capacity selected by fitted seating'))
    geometry = dict(schema=SCHEMA, coordinate_frame=dict(x='car-longitudinal,centre0', y='left', units='m'),
                    door_topology=topology, seating_hypothesis=option,
                    vestibule_length_m=vestibule_length, wheelchair_location=arranged['wheelchair_location'],
                    clear_envelope=bounds, vestibules=vestibules, seats=seats,
                    wheelchairs=wheelchairs, paths=paths,
                    access_path_graph=dict(nodes=list(adjacent), edges=edges, assigned_bay_routes=route_checks,
                                           scope='Axis-aligned free-space connectivity only; turn/vehicle swept clearance not established'),
                    retained_post_obstacles=audit['retained_side_posts'],
                    source_sha256=audit['sources'])
    physical_id = _hash(geometry)
    record = dict(schema=SCHEMA, physical_geometry_id=physical_id,
        input_parameters=dict(door_topology=topology, seating_hypothesis=deepcopy(option), standing_passengers=standing_count,
                              vestibule_length_m=vestibule_length, wheelchair_location=wheelchair_location),
        source_sha256={**audit['sources'], 'engineering/comfort_options/layout.py': sha256(Path(__file__).read_bytes()).hexdigest()},
        parent_configuration_sha256=audit['parent_configuration_sha256'],
        geometry=geometry, door_topology=topology, doors_total=doors,
        active_doors_per_platform=len(centres), one_side=one_side, boarding_side='+y' if one_side else 'either side',
        door_centres_x_m=centres, door_width_m=1.4, door_height_m=2.1,
        passenger_limit=passenger_limit, normal_passengers=passenger_limit,
        seats_total=count, transverse_seats=sum(s['kind']=='transverse-seat' for s in seats),
        bench_seats=sum(s['kind']=='wall-bench-seat' for s in seats), wheelchair_places=2,
        geometrically_placed_passengers=len(occupants),
        standing_passengers=standing_count, passenger_mass_kg=75.,
        payload_kg=passenger_limit*75., wheelchair_device_additional_mass_kg=None,
        fixed_seat_share=count/passenger_limit, seated_or_wheelchair_share=(count+2)/passenger_limit,
        standing_area_m2=standing_area, standing_slots_available=len(standing_slots),
        standing_density_persons_m2=density, geometric_occupants=occupants,
        packing_trials=[dict(wheelchair_location=a['wheelchair_location'], seats_total=len(a['seats']),
                             bench_seats=sum(s['kind']=='wall-bench-seat' for s in a['seats']),
                             packing_violations=a['packing_violations'],
                             blocked_opposite_door_bays=a['blocked_door_bays'], row_offset_search=a['offset_trials']) for a in trials],
        layout_selection_policy=('Preserve usable doorway wall benches before maximising seats among valid packing trials'
             if wheelchair_location=='benches-first' else 'Maximise seats among valid declared packing trials'),
        infill_stock=infill, seating_stock=seat_stock,
        seating_budget=dict(retained_interior_allowance_kg=allowance, identified_seating_stock_kg=known,
                            retained_unlocated_remainder_kg=max(0., allowance-known),
                            known_stock_excess_kg=max(0., known-allowance),
                            retained_unlocated_parent_allocation_kg=audit['retained_unlocated_allocation_kg'],
                            interior_account=audit['interior_account'], source_chain_sha_matches=audit['source_chain_sha_matches'],
                            mass_delta_kg=max(0., known-allowance),
                            treatment='Allocate known seat stock within retained800kg interior account; keep all unlocated remainder; claim no tare saving'),
        glazing=dict(fixed_side_area_m2=24., door_area_m2=float(doors), total_area_m2=24.+doors,
                     door_leaf_count=2*doors, door_pane_area_m2_each=.5,
                     interface='New extra-door openings versus retained fixed windows require exact pane positions; area assumption alone does not establish fit'),
        proposal_demand_controls=controls,
        overload_sensitivity=dict(research_crowd_density_persons_m2=4.,
             geometric_crowd_passengers=count+2+math.floor(4.*standing_area),
             geometric_crowd_payload_kg=75.*(count+2+math.floor(4.*standing_area)),
             retained_AW3_passengers=160, retained_AW3_payload_kg=12000.,
             service_limit_is_enforced=False, structural_load_reduction_authorised=False,
             note='Proposed hard cap needs boarding control; geometry does not prevent additional passengers. Preserve AW3 and asymmetric/crowd load cases until qualification approves revised loads.'),
        comfort_claims=dict(permitted_for_geometric_screen_pass_only=True,
            scope='Full2+2 seating, opposite-door wall benches where compatible, and minimal standing; reduced passenger cap is explicit',
            full_car_width_wheelchair_through_route=False,
            boarding_aisle_occupancy='Standing slots share circulation aisle; door vestibules and bay routes stay free of fixed furniture; operating passenger movement unverified',
            declared_targets=dict(clear_seat_pan_m=.45, row_pitch_m=.80, aisle_m=.65, standing_density_persons_m2=3.5),
            bench_omissions=bench_reasons),
        necessary_definition_checks=dict(out_of_bounds=out_of_bounds, occupant_collisions=collisions,
                                         retained_post_collisions=post_collisions, fixed_seat_path_collisions=blocked_paths,
                                         blocked_opposite_door_bays=arranged['blocked_door_bays']),
        execution='completed', numerical_validity='valid-analytic-definition-check',
        engineering_screen='fail' if failures else 'pass', failure_reasons=failures,
        evidence_maturity='analytical-layout-and-material-proposal', selection_purpose='research-comparison',
        physical_acceptance='hold', installed_tare_kg=None,
        unknown=['Platform compatibility on same physical side, return loops and degraded rescue/egress',
                 'Accessible swept routes, occupied turning, door flow, evacuation and installation tolerances',
                 'Complete seat/bench restraint structure and fire performance',
                 'Extra door apertures conflict with unlocated glazing and structural details until native model rebuilt',
                 'Equipment/gangway end envelopes reserved1m each but not clash-qualified'],
        dense_pitch_negative_control=dict(pitch_m=.65, declared_minimum_m=.80, engineering_screen='fail',
                                          reason='More rows obtained with650mm pitch are outside the declared comfort family'),
        **FALSE_FLAGS)
    record['layout_id'] = _hash(record)
    return record


def make_layout(door_topology='one-sided-2', *, seat_option=None, standing_passengers=0,
                vestibule_length_m=1.8, wheelchair_location='benches-first', root=ROOT):
    """Build one explicit research layout; accepts failing negative controls."""
    return _generate(door_topology, deepcopy(seat_option or SEAT_OPTIONS[0]), standing_passengers,
                     _audit(Path(root)), vestibule_length_m, wheelchair_location)


def family(*, root=ROOT):
    """Exactly72 bounded variants; primary capacity follows actual seating."""
    audit = _audit(Path(root))
    # Replace two redundant widest-pan/long-vestibule rejection records with
    # the maximum-seating door-bay option, keeping exactly72 ordinary outputs.
    rows = [_generate(topology, deepcopy(option), standing, audit, vestibule)
            for topology in TOPOLOGIES for option in SEAT_OPTIONS
            for vestibule in (1.5,1.8,2.4) for standing in (0,4)
            if not (topology=='one-sided-2' and option['seat_width_m']==.48 and vestibule==2.4)]
    return rows+[_generate('one-sided-2',deepcopy(SEAT_OPTIONS[0]),standing,audit,1.5,'best-fit') for standing in (0,4)]


def primary_options(*, root=ROOT):
    """Explicit bench default, maximum-seating tradeoff and generous control."""
    return dict(bench_default=make_layout(root=root),
                maximum_seating_door_bays=make_layout(vestibule_length_m=1.5,wheelchair_location='best-fit',root=root),
                generous_bench_control=make_layout(vestibule_length_m=2.4,root=root))


def validate_layout(value, *, root=ROOT):
    """Rebuild every field, rejecting stale/mixed geometry or edited results."""
    try:
        params = value['input_parameters']
        expected = make_layout(params['door_topology'], seat_option=params['seating_hypothesis'],
                               standing_passengers=params['standing_passengers'],
                               vestibule_length_m=params['vestibule_length_m'],
                               wheelchair_location=params['wheelchair_location'], root=root)
    except (KeyError, TypeError, OSError) as exc:
        raise ValueError('layout definition cannot be rebuilt') from exc
    if value != expected:
        raise ValueError('layout identity, source, geometry or derived result differs')
    return True


def render_svg(value):
    """Readable plan for geometric review; no visual acceptance claim."""
    from html import escape
    g=value['geometry']; scale=80.; margin=35.; top=90.
    def rectangle(r, fill, stroke='none', opacity=1):
        return (f'<rect x="{margin+(r["x0_m"]+8.5)*scale:.2f}" y="{top+(1.325-r["y1_m"])*scale:.2f}" '
                f'width="{(r["x1_m"]-r["x0_m"])*scale:.2f}" height="{(r["y1_m"]-r["y0_m"])*scale:.2f}" '
                f'fill="{fill}" stroke="{stroke}" opacity="{opacity}"><title>{escape(r["id"])}</title></rect>')
    result=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="390" viewBox="0 0 1440 390">',
            '<rect width="1440" height="390" fill="white"/>',
            '<style>text{font-family:Arial,sans-serif;fill:#17202a} .title{font-size:21px;font-weight:bold}.sub{font-size:15px}</style>',
            f'<text class="title" x="35" y="31">17m research seating plan: {value["seats_total"]} seats +2 wheelchair users +{value["standing_passengers"]} standing</text>',
            f'<text class="sub" x="35" y="58">{escape(value["door_topology"])}; {g["vestibule_length_m"]:.1f}m vestibules; {escape(g["wheelchair_location"])}; definition screen: {value["engineering_screen"]}</text>',
            rectangle(_rect('17m body','body',-8.5,8.5,-1.325,1.325),'#f6f6f6','#17202a'),
            rectangle(g['clear_envelope'],'white','#94a3b8')]
    for r in g['vestibules']:
        result.append(rectangle(r,'#eaf4fa'))
    for r in g['paths']:
        result.append(rectangle(r,'#cfe9ef',opacity=.25))
    for r in g['retained_post_obstacles']:
        result.append(rectangle(r,'#475569'))
    colors={'transverse-seat':'#3b82c4','wall-bench-seat':'#31976d','wheelchair':'#9661ac','standing':'#e89b30'}
    for r in value['geometric_occupants']:
        result.append(rectangle(r,colors[r['kind']],'white',.85))
    for centre in value['door_centres_x_m']:
        for sign in ([1] if value['one_side'] else [-1,1]):
            y=top+(1.325-sign*1.325)*scale
            x=margin+(centre+8.5-.7)*scale
            result.append(f'<line x1="{x}" y1="{y}" x2="{x+1.4*scale}" y2="{y}" stroke="#e85d3f" stroke-width="7"/>')
    result += ['<text class="sub" x="35" y="338">Blue: 2+2 seat envelopes | Green: benches | Purple: wheelchair bays | Orange: standing | Gray: posts | Red: passenger doors</text>',
               '<text class="sub" x="35" y="364">Clear paths may overlap other clear regions. Seating avoids retained posts. Accessibility, evacuation and installed fit remain unapproved.</text>', '</svg>']
    return '\n'.join(result)+'\n'
