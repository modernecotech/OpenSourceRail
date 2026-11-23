"""Airport opening workings, with one depot at the Airport end and one turnback face at each end."""
from collections import defaultdict
from hashlib import sha256
from html import escape
from itertools import pairwise
from math import ceil, sqrt
from pathlib import Path
import json
import tomllib

from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system

OPENING_TPH = 4
TRIAL = Path(__file__).parent / 'engineering/mechanical/vehicle/section-trial.toml'


def leg_profiles(patterns, route_km, cfg):
    """Solve accelerate–cruise–brake distance and time for each pair of booked stops."""
    accel = cfg['power_assumptions']['required_net_accel_m_s2']
    brake = tomllib.loads(TRIAL.read_text())['braking_deceleration_m_s2']
    profiles = []
    for side, pattern in enumerate(patterns):
        legs = []
        for a, b in pairwise(pattern):
            start, end = (route_km * (1 - stop['fraction'] if side else stop['fraction']) for stop in (a, b))
            distance = abs(end - start) * 1000
            duration = b['arrival_s'] - a['departure_s']
            disc = duration**2 - 2 * distance * (1 / accel + 1 / brake)
            if disc < 0:
                raise ValueError(f"Insufficient booked run time at {a['id']}")
            speed = 2 * distance / (duration + sqrt(disc))
            if speed > cfg['vehicle']['speed_cap_kmh'] / 3.6:
                raise ValueError(f"Booked run requires excess speed at {a['id']}")
            legs.append({'start_km': start, 'end_km': end, 'departure_s': a['departure_s'],
                         'arrival_s': b['arrival_s'], 'acceleration_m_s2': accel, 'deceleration_m_s2': brake,
                         'cruise_m_s': speed, 'acceleration_s': speed / accel, 'braking_s': speed / brake,
                         'cruise_s': duration - speed / accel - speed / brake})
        profiles.append(legs)
    return profiles


def positioning_trips(trips, group):
    """Reach every first origin from the Airport depot and bring the sets back there."""
    paths = defaultdict(list)
    for train, side, dep, arr in trips:
        paths[train].append((side, dep, arr))
    empty = []
    duration, turn = group['one_way_s_including_dwell'], group['minimum_turn_s']
    for train, path in paths.items():
        if path[0][0] == 1:
            arrival = path[0][1] - turn
            empty.append((train, 0, arrival - duration, arrival))
        if path[-1][0] == 0:
            depart = path[-1][2] + turn
            empty.append((train, 1, depart, depart + duration))
    return sorted(empty, key=lambda row: row[2])


def terminal_screen(cfg, group, trips, patterns, profiles):
    # All intervals are half open. Each throat is exclusive to every direction and to depot moves.
    train_m = cfg['vehicle_geometry']['train_length_m']
    platform_m = cfg['station_geometry']['platform_clear_length_m']
    yard_km, yard_kmh = 0.25, 10.0
    route_lock_s = 15
    # A low-speed approach allowance covers 100 m from the fouling point plus the entire train.
    # Require a single complete train between the fouling point and the platform stopping mark.
    traverse_s = ceil((100 + train_m) / (yard_kmh / 3.6)) + route_lock_s
    yard_move_s = ceil((1000 * yard_km + train_m) / (yard_kmh / 3.6)) + 2 * route_lock_s
    resources = defaultdict(list)
    paths = defaultdict(list)
    yard = []
    def occupy(key, start, end, train, kind):
        resources[key].append({'start_s': start, 'end_s': end, 'train': train, 'kind': kind})

    for train, side, dep, arr in trips:
        paths[train].append((side, dep, arr))
        occupy(f'throat-{side}', dep - route_lock_s, dep + traverse_s, train, 'departure')
        occupy(f'throat-{1-side}', arr - traverse_s, arr + route_lock_s, train, 'arrival')
        for i, (a, b) in enumerate(pairwise(patterns[side])):
            if i + 1 == len(profiles[side]):
                clear = route_lock_s  # on berth, beyond the turnout fouling point
            else:
                # Time for the head to travel another full train length after downstream dwell.
                after = profiles[side][i+1]
                accel, speed = after['acceleration_m_s2'], after['cruise_m_s']
                accel_distance = 0.5 * speed**2 / accel
                tail_s = (sqrt(2 * train_m / accel) if train_m <= accel_distance
                          else speed / accel + (train_m - accel_distance) / speed)
                if train_m > accel_distance + speed * after['cruise_s']:
                    raise ValueError('Station separation too short for assumed tail release')
                clear = ceil(tail_s) + route_lock_s
            occupy(f"block-{a['id']}-{b['id']}", dep + a['departure_s'] - route_lock_s,
                   dep + b['departure_s'] + clear, train, 'run')

    turn = group['minimum_turn_s']
    for train, path in paths.items():
        path.sort(key=lambda row: row[1])
        first, last = path[0], path[-1]
        if first[0] != 0 or last[0] != 1:
            raise ValueError('Working must start and finish at the Airport depot')
        into_platform = first[1] - turn
        to_depot = last[2] + turn
        for start, kind in [(into_platform - yard_move_s, 'depot to platform'), (to_depot, 'platform to depot')]:
            yard.append({'train': train, 'kind': kind, 'start_s': start, 'end_s': start + yard_move_s,
                         'distance_km': yard_km})
            occupy('throat-0', start, start + yard_move_s, train, kind)
        occupy('platform-0', into_platform - yard_move_s, first[1] + traverse_s, train, 'first boarding')
        occupy('platform-0', last[2] - traverse_s, to_depot + yard_move_s, train, 'last arrival')
        for (side, _, arr), (next_side, dep, _) in pairwise(path):
            if side == next_side or dep - arr < turn:
                raise ValueError('Disconnected train working or insufficient turn')
            occupy(f'platform-{next_side}', arr - traverse_s, dep + traverse_s, train, 'turnback')

    clearance = {}
    clashes = []
    for key, intervals in resources.items():
        intervals.sort(key=lambda x: x['start_s'])
        margins = []
        for a, b in pairwise(intervals):
            gap = b['start_s'] - a['end_s']
            margins.append(gap)
            if gap < 0:
                clashes.append({'resource': key, 'first': a, 'next': b, 'margin_s': gap})
        clearance[key] = min(margins) if margins else None
    return {'open_platform_faces_each_end': [1, 1], 'platform_clear_length_m': platform_m,
            'train_length_m': train_m, 'train_fits': train_m <= platform_m,
            'directional_interstation_blocks': sum(k.startswith('block-') for k in resources),
            'common_throats_each_end': [1, 1], 'depot_end': 'Airport', 'yard_track_km_assumed': yard_km,
            'yard_move_seconds': yard_move_s, 'yard_moves': sorted(yard, key=lambda x: x['start_s']),
            'approach_traverse_s': traverse_s, 'route_lock_release_s': route_lock_s,
            'throat_speed_kmh_assumed': yard_kmh, 'throat_length_m_assumed': 100,
            'resources': dict(resources), 'minimum_margin_s_by_resource': clearance,
            'conflicts': clashes, 'schedule_screen_passed': not clashes and train_m <= platform_m}


def build_service(cfg, reference_group):
    """Return group, hourly offer, passenger/empty trip tuples, stop patterns, leg profiles and resource intervals.

    Trip tuples are (set, direction, departure, arrival). All trip times and resource intervals use
    local seconds since midnight. Pattern and profile times are relative to departure. Side 0
    runs Airport to Al Qadisiya. Profile chainages in both directions use the Airport origin.
    """
    v = cfg['vehicle']
    stops, route = reference_group['outward_stops'], reference_group['one_way_km']
    if (route != 12 or [s['id'] for s in stops] != [f'Airport-{n:02}' for n in range(6)]
            or v['cars_per_train'] != 6 or cfg['track_count'] != 2):
        raise ValueError('Opening diagram requires the six-car double-track 12 km Airport corridor')
    hourly = [OPENING_TPH] * v['service_hours_per_day']
    headway = 3600 // hourly[0]
    vehicle = dict(v, peak_headway_s=headway)
    plan = dict(cfg['service_plan'], departures_per_hour_direction=hourly)
    group, trips, patterns = diagrams.group_diagram('Airport', stops, route, dict(cfg, vehicle=vehicle, service_plan=plan))
    profiles = leg_profiles(patterns, route, cfg)
    empty = positioning_trips(trips, group)
    terminal = terminal_screen(cfg, group, trips + empty, patterns, profiles)
    service = {'group': group, 'hourly': hourly, 'peak_headway_s': headway,
               'trips': trips, 'positioning_trips': empty, 'patterns': patterns, 'leg_profiles': profiles,
               'terminal': terminal, 'scheduled_places_per_hour_direction': hourly[0] * v['normal_places_per_train'],
               'non_revenue_km_per_day': len(empty) * route + sum(x['distance_km'] for x in terminal['yard_moves']),
               'physical_accepted': False, 'source_sha256': {
                   str(p.relative_to(system.ROOT)): sha256(p.read_bytes()).hexdigest()
                   for p in (Path(__file__).resolve(), Path(diagrams.__file__).resolve(), TRIAL.resolve())},
               'engineering_holds': ['Survey stop positions, depot lead length and terminal crossover fouling points.',
                                     'Prove grade, low-adhesion braking, full-tail detection, turnout locks and failure recovery.',
                                     'Measure dwell, depot shunting, route release and passenger demand by time and direction.']}
    service['evaluation_id'] = system._id(service)
    return service


def time_distance_svg(service):
    """Plot every passenger and positioning working in successive three-hour windows on one service-day sheet."""
    trips = [(row, False) for row in service['trips']] + [(row, True) for row in service['positioning_trips']]
    yard = service['terminal']['yard_moves']
    start = min(row['start_s'] for row in yard) // 3600 * 3600
    end = max(row['end_s'] for row in yard)
    paths = defaultdict(list)
    for (train, side, dep, arr), _ in trips:
        paths[train].append((side, dep, arr))
    waits = []
    for train, path in paths.items():
        path.sort(key=lambda row: row[1])
        for (_, _, arrival), (side, depart, _) in pairwise(path):
            waits.append((train, side, arrival, depart))
        moves = [move for move in yard if move['train'] == train]
        waits.extend([(train, 0, moves[0]['end_s'], path[0][1]),
                      (train, 0, path[-1][2], moves[-1]['start_s'])])
    window = 3 * 3600
    panels = ceil((end - start) / window)
    width, step = 1140, 210
    height = 68 + panels * step
    left, right = 165, width - 25
    route = service['group']['one_way_km']
    y = lambda km, top: top + 130 * (1 - km / route)
    def hour(t):
        return f'{int(t//3600)%24:02}:00' + ('+1' if t >= 86400 else '')
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="max-width:100%;height:auto" role="img" aria-labelledby="title desc">',
            '<title id="title">Baghdad Airport opening timetable</title>',
            '<desc id="desc">All passenger workings and empty mainline moves. Time progresses to the right. Dwell is horizontal. Stop distances use planning chainages.</desc>',
            '<rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#172738">',
            '<text x="15" y="25" font-size="20" font-weight="bold">Baghdad Airport · Full operating day</text>',
            '<text x="15" y="47" font-size="13">Airport departures in blue · Al Qadisiya departures in green · Dashed lines show empty moves · Grey lines show turns · Local hours</text>']
    for panel in range(panels):
        t0, top = start + panel * window, 70 + panel * step
        x = lambda t: left + (t - t0) * (right - left) / window
        for stop in service['patterns'][0]:
            sy = y(stop['fraction'] * route, top)
            rows.append(f'<path d="M{left} {sy:.1f}H{right}" stroke="#becbd1"/><text x="10" y="{sy+4:.1f}" font-size="12">{escape(stop["label"])}</text>')
        depot_y = top + 146  # Fan the short depot lead out for legibility.
        rows.append(f'<text x="10" y="{depot_y+4}" font-size="12">Airport depot</text>')
        for offset in range(4):
            tick = t0 + 3600 * offset
            rows.append(f'<path d="M{x(tick):.1f} {top}v146" stroke="#d9dfe3"/><text x="{x(tick):.1f}" y="{top+165}" text-anchor="middle" font-size="12">{hour(tick)}</text>')
        rows.append(f'<clipPath id="w{panel}"><rect x="{left}" y="{top-2}" width="{right-left}" height="150"/></clipPath><g clip-path="url(#w{panel})">')
        for (train, side, dep, arr), empty in trips:
            if arr < t0 or dep > t0 + window:
                continue
            points = []
            for stop in service['patterns'][side]:
                km = route * (1-stop['fraction'] if side else stop['fraction'])
                for time_key in ('arrival_s', 'departure_s'):
                    points.append(f"{x(dep + stop[time_key]):.2f},{y(km, top):.2f}")
            dash = ' stroke-dasharray="5 4"' if empty else ''
            colour = '#197358' if side else '#13569a'
            rows.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{colour}" stroke-width="1.5"{dash}><title>{escape(train)} · {"empty" if empty else "passenger"}</title></polyline>')
        for train, side, begin, finish in waits:
            if begin <= t0 + window and finish >= t0:
                stationary_y = y(route if side else 0, top)
                rows.append(f'<path d="M{x(begin):.2f},{stationary_y:.2f}H{x(finish):.2f}" stroke="#667781" stroke-width="1.5"><title>{escape(train)} at platform</title></path>')
        for move in yard:
            if move['start_s'] > t0 + window or move['end_s'] < t0:
                continue
            platform_y = y(0, top)
            ys = (depot_y, platform_y) if move['kind'] == 'depot to platform' else (platform_y, depot_y)
            rows.append(f'<path d="M{x(move["start_s"]):.2f},{ys[0]:.2f}L{x(move["end_s"]):.2f},{ys[1]:.2f}" stroke="#496172" stroke-width="1.5" stroke-dasharray="4 3"><title>{escape(move["train"])} · {move["kind"]}</title></path>')
        rows.append('</g>')
    return '\n'.join(rows + ['</g></svg>'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--svg', action='store_true', help='Emit the full-day time–distance diagram on stdout')
    args = parser.parse_args()
    group = json.loads(diagrams.PUBLICATION.read_bytes())['networks']['first']['groups']['Airport']
    service = build_service(system.load(), group)
    print(time_distance_svg(service) if args.svg else json.dumps(service, indent=2, allow_nan=False))
