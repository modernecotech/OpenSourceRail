#!/usr/bin/env python3
"""Compile connected junction, residential-gap and line-specific civil planning."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import sys
import tomllib
import zipfile

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/automation'))
from network_integration import complete_link_groups, geometry_interfaces, legs_at_interface, line_at_chainage
from city_access import xyz, EARTH_RADIUS_M

CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
OUT = ROOT / 'engineering/network-planning/baghdad'
CONFIG = ROOT / 'design/network-planning/integrated-plan.json'
CONTEXT = OUT / 'retained-network-context.json.gz'


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(raw):
    result = bytearray(gzip.compress(raw, mtime=0))
    result[9] = 255
    return bytes(result)


def csv_data(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def retain_context():
    source = ROOT / '.cache/osr-pipeline/osm/baghdad.json'
    data = json.loads(source.read_text())
    body = dict(arterials=data['arterials'], area_anchors=[a for a in data['anchors'] if a['kind'].startswith('place:')],
                source=dict(dataset='Retained OpenStreetMap extraction', original_sha256=sha(source), bbox=data['bbox'],
                            fetched_utc=datetime.fromtimestamp(data['fetched_at'], tz=timezone.utc).isoformat(),
                            attribution='OpenStreetMap contributors, ODbL', source_url='https://www.openstreetmap.org/copyright',
                            traffic_directions_and_route_permissions_verified=False))
    OUT.mkdir(parents=True, exist_ok=True)
    raw = packed(encode(body))
    if CONTEXT.exists() and CONTEXT.read_bytes() != raw:
        raise ValueError('retained context differs; preserve it and review a new source revision')
    CONTEXT.write_bytes(raw)


def coordinates(design, geojson, grid=None):
    box = design['city']['bbox']
    grid = grid or dict(bbox_west=box['west'], bbox_north=box['north'], m_per_deg_lat=111132.,
                        m_per_deg_lon=111132. * math.cos(math.radians((box['north'] + box['south']) / 2)))
    def project(lon, lat):
        return [round((lon - grid['bbox_west']) * grid['m_per_deg_lon'], 3),
                round((grid['bbox_north'] - lat) * grid['m_per_deg_lat'], 3)]
    def unproject(x, y):
        return [round(grid['bbox_west'] + x / grid['m_per_deg_lon'], 8),
                round(grid['bbox_north'] - y / grid['m_per_deg_lat'], 8)]
    lines = {f['properties']['name']: LineString([project(*p) for p in f['geometry']['coordinates']])
             for f in geojson['features'] if f['geometry']['type'] == 'LineString'}
    if set(lines) != {l['name'] for l in design['lines']}:
        raise ValueError('line geometry and design identities differ')
    stations = [{**s, 'xy': project(s['lon'], s['lat'])} for s in design['stations']]
    return lines, stations, project, unproject


def catalogue_audit():
    rows = []
    sources = {}
    for path in sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml')):
        design = tomllib.loads(path.read_text())
        geo = path.parent / (design['city']['slug'] + '.corridor.geojson')
        access = path.parent / 'engineering/access/summary.json'
        sources[path.relative_to(ROOT).as_posix()] = sha(path)
        item = dict(city=design['city']['slug'], country=design['city']['country'], line_count=len(design['lines']),
                    station_count=len(design['stations']), declared_transfer_components=None,
                    radial_population_fraction_1000m=None, self_intersecting_lines=None,
                    cross_line_overlap_pairs=None, oversized_declared_interchange_groups=None, construction_released=False)
        if access.is_file():
            report = json.loads(access.read_text())
            item['declared_transfer_components'] = len(report['transfers']['components'])
            for row in report['population'].get('catchments', []):
                if row['radius_m'] == 1000:
                    item['radial_population_fraction_1000m'] = round(row['fraction_of_raster_population'], 6)
            sources[access.relative_to(ROOT).as_posix()] = sha(access)
        if geo.is_file():
            try:
                lines, stations, _, _ = coordinates(design, json.loads(geo.read_text()))
                item['self_intersecting_lines'] = sum(not line.is_simple for line in lines.values())
                item['cross_line_overlap_pairs'] = sum(a.intersection(b).length > .001 for a, b in itertools.combinations(lines.values(), 2))
                byid = {s['id']: s for s in stations}
                oversized = 0
                for complex_ in design.get('interchanges', []):
                    members = [byid[s] for s in complex_['platforms'] if s in byid]
                    diameter = max((math.dist(a['xy'], b['xy']) for a, b in itertools.combinations(members, 2)), default=0.)
                    oversized += diameter > 600.
                item['oversized_declared_interchange_groups'] = oversized
                item['geometry_status'] = 'screened'
            except ValueError as error:
                item['geometry_status'] = 'unavailable: ' + str(error)
            sources[geo.relative_to(ROOT).as_posix()] = sha(geo)
        else:
            item['geometry_status'] = 'missing'
        rows.append(item)
    return rows, sources


def residential_plan(design, routes, stations, project, unproject, cfg, context):
    path = CITY / 'engineering/access/population-pixels.npz.gz'
    with np.load(io.BytesIO(gzip.decompress(path.read_bytes())), allow_pickle=False) as data:
        selected = data['valid'] & (data['counts'] > 0)
        lat, lon, counts = data['lat'][selected], data['lon'][selected], data['counts'][selected]
    points = xyz(lat, lon)
    tree = cKDTree(points)
    radius = cfg['station_radius_m']
    chord_radius = 2 * math.sin(radius / (2 * EARTH_RADIUS_M))
    native_stations = xyz([s['lat'] for s in stations], [s['lon'] for s in stations])
    distance, _ = cKDTree(native_stations).query(points)
    covered = distance <= chord_radius
    original = covered.copy()
    total = math.fsum(float(p) for p in counts)
    route_vertices = [unproject(*xy) for route in routes.values() for xy in route.coords]
    corridor_chord, _ = cKDTree(xyz([p[1] for p in route_vertices], [p[0] for p in route_vertices])).query(points)
    outside = (corridor_chord > chord_radius) & ~covered
    lengths = {l['name']: l['length_m'] for l in design['lines']}
    ring_names={l['name'] for l in design['lines'] if l['shape']=='ring'}
    def inline_distance(name,a,b):
        delta=abs(a-b)
        return min(delta,lengths[name]-delta) if name in ring_names else delta
    positions = defaultdict(list)
    for s in stations:
        positions[s['line']].append(s['s_m'])
    candidate_rows = []
    for name, route in sorted(routes.items()):
        length = lengths[name]
        for chainage in np.arange(cfg['candidate_spacing_m'], length, cfg['candidate_spacing_m']):
            if min(inline_distance(name,float(chainage),s) for s in positions[name]) < cfg['minimum_inline_spacing_m']:
                continue
            xy = line_at_chainage(route, float(chainage), length)
            ll = unproject(*xy)
            members = tree.query_ball_point(xyz([ll[1]], [ll[0]])[0], chord_radius)
            candidate_rows.append(dict(line=name, chainage_m=float(chainage), xy=xy, lon=ll[0], lat=ll[1], members=np.asarray(members, dtype=int)))
    infill = []
    while candidate_rows and len(infill) < cfg['maximum_infill_stations']:
        ranked = [(round(math.fsum(float(counts[i]) for i in c['members'] if not covered[i]), 3), c['line'], c['chainage_m'], index)
                  for index, c in enumerate(candidate_rows)]
        gain, _, _, index = min(ranked, key=lambda row: (-row[0], row[1], row[2]))
        if gain < cfg['minimum_incremental_residents_2020']:
            break
        candidate = candidate_rows.pop(index)
        covered[candidate['members']] = True
        positions[candidate['line']].append(candidate['chainage_m'])
        infill.append({k: v for k, v in candidate.items() if k != 'members'} | dict(
            id=f"infill-{candidate['line']}-{int(candidate['chainage_m']):06d}", incremental_residents_2020=gain,
            actual_walking_coverage_accepted=False, station_site_design_accepted=False,
            civil_package='new station/approaches/access structure and timetable/energy/fleet reassessment'))
        candidate_rows = [c for c in candidate_rows if c['line'] != candidate['line'] or
                          inline_distance(c['line'],c['chainage_m'],candidate['chainage_m']) >= cfg['minimum_inline_spacing_m']]
    bins = defaultdict(list)
    for i in np.flatnonzero(~covered):
        p = project(float(lon[i]), float(lat[i]))
        bins[(math.floor(p[0] / cfg['gap_bin_m']), math.floor(p[1] / cfg['gap_bin_m']))].append(int(i))
    gap_candidates = []
    for key, members in bins.items():
        weight = math.fsum(float(counts[i]) for i in members)
        if weight <= 0:
            continue
        centroid = [math.fsum(project(float(lon[i]), float(lat[i]))[axis] * float(counts[i]) for i in members) / weight for axis in (0, 1)]
        ll = unproject(*centroid)
        neighbourhood = tree.query_ball_point(xyz([ll[1]], [ll[0]])[0], chord_radius)
        population = round(math.fsum(float(counts[i]) for i in neighbourhood if not covered[i]), 3)
        gap_candidates.append((population, key, centroid, ll))
    areas = []
    for population, key, centroid, ll in sorted(gap_candidates, key=lambda v: (-v[0], v[1])):
        if len(areas) >= cfg['maximum_gap_areas']:
            break
        if any(math.dist(centroid, a['xy']) < cfg['minimum_gap_centre_separation_m'] for a in areas):
            continue
        anchors = [(math.dist(centroid, project(a['lon'], a['lat'])), a) for a in context['area_anchors'] if a.get('name')]
        nearest = min(anchors, key=lambda p: (p[0], p[1]['id'])) if anchors else None
        station = min(stations, key=lambda s: (math.dist(centroid, s['xy']), s['id']))
        road = min(context['arterials'], key=lambda r: min(math.dist(centroid, project(lon_, lat_)) for lat_, lon_ in r['nodes']))
        areas.append(dict(id=f'residential-gap-{len(areas)+1:02d}', xy=[round(v, 3) for v in centroid], lon=ll[0], lat=ll[1],
                          nearby_named_area=nearest[1]['name'] if nearest and nearest[0] <= 2500 else None,
                          name_source_osm_id=nearest[1]['id'] if nearest and nearest[0] <= 2500 else None,
                          unserved_residents_2020_within_1000m=population,
                          nearest_existing_station=station['id'], nearest_line=station['line'],
                          straight_station_distance_m=round(math.dist(centroid, station['xy']), 3),
                          nearby_arterial_osm_id=road['id'], nearby_arterial_name=road.get('name'),
                          intervention='compare new rail branch/extension and frequent feeder with accessible station connection',
                          route_geometry=None, service_funded=False, corridor_design_accepted=False))
    # Existing road coordinates define investigation corridors, not validated
    # bus movements or rail curvature. Common-coordinate joins, directions,
    # grades, bridge limits and the final station connection need survey.
    import networkx as nx
    graph = nx.Graph()
    node_xy = {}
    for road in context['arterials']:
        nodes = [tuple(round(v, 8) for v in pair) for pair in road['nodes']]
        for left, right in zip(nodes, nodes[1:]):
            if left == right:
                continue
            a, b = project(left[1], left[0]), project(right[1], right[0])
            node_xy[left], node_xy[right] = a, b
            length = round(math.dist(a, b), 3)
            if length <= 0:
                continue
            if not graph.has_edge(left, right) or length < graph[left][right]['length_m']:
                graph.add_edge(left, right, length_m=length, osm_way_id=road['id'], road_class=road['class'])
    ordered_nodes = sorted(graph.nodes)
    road_tree = cKDTree(np.asarray([node_xy[n] for n in ordered_nodes]))
    station_road_node = {s['id']: ordered_nodes[int(road_tree.query(s['xy'])[1])] for s in stations}
    feeder_covered = covered.copy()
    rail_covered = covered.copy()
    shared_edges = {}
    expansion_routes = []
    for area in areas:
        start = ordered_nodes[int(road_tree.query(area['xy'])[1])]
        possible_stations = sorted(stations, key=lambda s: (math.dist(area['xy'], s['xy']), s['id']))
        results = []
        for station in possible_stations[:12]:
            end = station_road_node[station['id']]
            try:
                path_nodes = nx.shortest_path(graph, start, end, weight='length_m')
            except nx.NetworkXNoPath:
                continue
            if len(path_nodes) < 2:
                continue
            path_length=math.fsum(graph[a][b]['length_m'] for a,b in zip(path_nodes,path_nodes[1:]))
            direct=math.dist(area['xy'],station['xy'])
            if path_length>15000 or path_length>max(2000,direct*3):
                continue
            if math.dist(station['xy'],node_xy[end])>1000:
                continue
            results.append((round(path_length+math.dist(station['xy'],node_xy[end]),3),station['id'],station,path_nodes))
        if not results:
            area['route_status'] = 'no retained-road connection; new corridor/feeder access design required'
            continue
        _,_,station,path_nodes=min(results,key=lambda row:(row[0],row[1]))
        route_points = [node_xy[n] for n in path_nodes]
        route = LineString(route_points)
        proposal_stops = []
        for distance_m in np.arange(0., route.length + .1, 500.):
            point = route.interpolate(float(distance_m))
            ll = unproject(point.x, point.y)
            chord = xyz([ll[1]], [ll[0]])[0]
            for radius_m, state in [(500., feeder_covered), (cfg['station_radius_m'], rail_covered)]:
                indices = tree.query_ball_point(chord, 2 * math.sin(radius_m / (2 * EARTH_RADIUS_M)))
                state[indices] = True
            proposal_stops.append(dict(chainage_m=round(float(distance_m), 3), lon=ll[0], lat=ll[1],
                                       stopping_site_and_access_accepted=False))
        for left, right in zip(path_nodes, path_nodes[1:]):
            key = tuple(sorted((left, right)))
            shared_edges.setdefault(key, dict(coordinates=[[n[1], n[0]] for n in key],
                                              length_m=graph[left][right]['length_m'],
                                              osm_way_id=graph[left][right]['osm_way_id'], corridor_ids=[]))['corridor_ids'].append(area['id'])
        proposal = dict(id='expansion-' + area['id'].split('-')[-1], residential_priority_area=area['id'],
                        existing_station_connection=station['id'], existing_line_connection=station['line'],
                        geometry_lonlat=[[n[1], n[0]] for n in path_nodes], route_length_m=round(route.length, 3),
                        proposed_stop_sites=proposal_stops,
                        start_access_connector_m=round(math.dist(area['xy'], route_points[0]), 3),
                        station_access_connector_m=round(math.dist(station['xy'], route_points[-1]), 3),
                        mode_choice='compare frequent feeder versus engineered rail branch along/near the corridor',
                        road_graph_basis='undirected common-coordinate retained OSM arterial graph; no one-way/grade/permission acceptance',
                        bridge_traffic_rail_geometry_and_access_validated=False, full_installed_price_usd=None,
                        native_timetable_and_fares_modified=False)
        expansion_routes.append(proposal)
        area['route_status'] = 'retained-road investigation corridor generated'
        area['route_geometry'] = proposal['id']
    # These separated area circles can still overlap; never sum them as unique people.
    summary = dict(population_year=2020, population_is_current_census=False, bbox_population_2020=round(total, 3),
                   baseline_radial_residents_1000m=round(math.fsum(float(p) for p in counts[original]), 3),
                   baseline_radial_fraction_1000m=round(math.fsum(float(p) for p in counts[original]) / total, 8),
                   infill_conditional_radial_residents_1000m=round(math.fsum(float(p) for p in counts[covered]), 3),
                   infill_conditional_radial_fraction_1000m=round(math.fsum(float(p) for p in counts[covered]) / total, 8),
                   baseline_unserved_outside_existing_corridor_vertex_screen_1000m=round(math.fsum(float(p) for p in counts[outside]), 3),
                   candidate_infill_count=len(infill), gap_priority_areas=len(areas), gap_areas_are_not_additive=True,
                   expansion_corridor_candidates=len(expansion_routes),
                   infill_and_feeder_500m_stop_circle_sensitivity=round(math.fsum(float(p) for p in counts[feeder_covered]) / total, 8),
                   infill_and_rail_1000m_station_circle_sensitivity=round(math.fsum(float(p) for p in counts[rail_covered]) / total, 8),
                   shared_expansion_corridor_edge_m=round(math.fsum(r['length_m'] for r in shared_edges.values()), 3),
                   route_stop_circles_are_not_accepted_walking_access=True,
                   actual_walkshed_accepted=False, additional_paid_journeys=None, adopted_new_station_count=0)
    # Compact native-pixel heat layer, without inventing/resampling resident counts.
    heat_bins = defaultdict(lambda: [0., 0.])
    for i in range(len(counts)):
        p = project(float(lon[i]), float(lat[i]))
        key = (math.floor(p[0] / cfg['gap_bin_m']), math.floor(p[1] / cfg['gap_bin_m']))
        heat_bins[key][0] += float(counts[i])
        if not original[i]:
            heat_bins[key][1] += float(counts[i])
    heat = [dict(x=key[0] * cfg['gap_bin_m'], y=key[1] * cfg['gap_bin_m'],
                 residents_2020=round(value[0], 3), unserved_2020=round(value[1], 3)) for key, value in sorted(heat_bins.items())]
    return summary, infill, areas, heat, expansion_routes, list(shared_edges.values())


def foundation_assembly(design, routes, unproject, interfaces):
    directory = CITY / 'engineering/connected-build'
    layout = json.loads((directory / 'span-layout.json').read_text())
    civil = json.loads((directory / 'civil.json').read_text())
    soils = json.loads((CITY / 'engineering/soil/sample-locations.geojson').read_text())['features']
    lengths = {l['name']: l['length_m'] for l in design['lines']}
    soil_by_line = defaultdict(list)
    for f in soils:
        soil_by_line[f['properties']['line']].append(f['properties'])
    fronts = civil['conditional_scenarios']['initial-accelerated']['deployments']
    front_span = {}
    order = {}
    front_rows = []
    for front in fronts:
        previous = None
        directed_spans=sorted(front['planned_spans'],key=lambda s:(s['start_chainage_m'],s['id']),reverse=front['direction']<0)
        for index, span in enumerate(directed_spans, 1):
            if span['id'] in front_span:
                raise ValueError('one span assigned to two launchers')
            front_span[span['id']] = front['id']
            order[span['id']] = (index, previous)
            previous = span['id']
        front_rows.append(dict(id=front['id'], line=front['line'], launcher=front['launcher'], direction=front['direction'],
                               span_ids=[s['id'] for s in directed_spans],
                               initial_assembly_chainage_m=(directed_spans[0]['start_chainage_m'] if front['direction']>0 else directed_spans[0]['end_chainage_m']),
                               work_intervals_m=front['work_intervals_m'],
                               delivery_access_accepted=False, foundations_released=0, actual_start_date=None,
                               run_boundary_relocation_method='passage or dismantle/transport/recommission package required'))
    proposed = {}
    spans = []
    for span in layout['spans']:
        for field, chainage_field in [('pier_a', 'start_chainage_m'), ('pier_b', 'end_chainage_m')]:
            key = span[field]
            proposed.setdefault(key, dict(id=key, line=span['line'], chainage_m=span[chainage_field], spans=[]))['spans'].append(span['id'])
        index, prior = order.get(span['id'], (None, None))
        affected_junctions=[i['id'] for i in interfaces for chainage in i['line_chainage_legs_m'].get(span['line'],[])
                            if span['start_chainage_m']-.05<=chainage<=span['end_chainage_m']+.05]
        spans.append(dict(id=span['id'], line=span['line'], from_m=span['start_chainage_m'], to_m=span['end_chainage_m'],
                          run=span['run'], classification=span['classification'], beam_variant=span['beam_variant'],
                          track_1_component=span['component_ids'][0] if span['component_ids'] else None,
                          track_2_component=span['component_ids'][1] if span['component_ids'] else None,
                          foundation_a='FND:' + span['pier_a'], foundation_b='FND:' + span['pier_b'],
                          front=front_span.get(span['id']), sequence=index, previous_front_span=prior,
                          junction_interface_ids=';'.join(sorted(set(affected_junctions))),
                          order_release_status='junction-design-hold' if affected_junctions else 'supplier-and-site-release-hold',
                          assembly_template='paired-full-span-bay' if span['component_ids'] else 'special-structure',
                          first_beam_restraint_required=True, second_beam_securing_before_advance=True,
                          stage_load_design_accepted=False, site_release_accepted=False))
    expected = {s['id'] for s in layout['spans'] if s['classification'] == 'catalogue-planning-span'}
    if set(front_span) != expected:
        raise ValueError('front assembly assignment must cover every catalogue span exactly once')
    aliases={}
    for line in design['lines']:
        if line['shape']!='ring' or not routes[line['name']].is_closed:continue
        boundary=[r for r in proposed.values() if r['line']==line['name'] and
                  (abs(r['chainage_m'])<=.002 or abs(r['chainage_m']-lengths[line['name']])<=.002)]
        if len(boundary)!=2:continue
        low,high=sorted(boundary,key=lambda r:r['chainage_m'])
        if low['chainage_m']>.002 or abs(high['chainage_m']-lengths[line['name']])>.002:continue
        low['spans']=sorted(set(low['spans']+high['spans']))
        low['cyclic_boundary_alias']=high['id']
        aliases['FND:'+high['id']]='FND:'+low['id']
        del proposed[high['id']]
    for span in spans:
        span['foundation_a']=aliases.get(span['foundation_a'],span['foundation_a'])
        span['foundation_b']=aliases.get(span['foundation_b'],span['foundation_b'])
    foundations = []
    beam_by_variant={b['id']:b for b in civil['beams']}
    span_by_id={s['id']:s for s in layout['spans']}
    for key, record in sorted(proposed.items()):
        xy = line_at_chainage(routes[record['line']], record['chainage_m'], lengths[record['line']])
        ll = unproject(*xy)
        samples = soil_by_line[record['line']]
        nearest = min(samples, key=lambda s: (abs(s.get('chainage_m', 0.) - record['chainage_m']), s['sample_id'])) if samples else None
        affected = [x['id'] for x in interfaces if record['line'] in x['lines'] and math.dist(xy, x['xy']) <= 50]
        ordinary=[span_by_id[s] for s in record['spans'] if span_by_id[s]['beam_variant']]
        # Two beams per bay, each with half its gravity load at each end.
        # This is a simple-span study only; continuity, caps/columns, trains,
        # construction stages and lateral/environmental actions stay unknown.
        gravity_screen=math.fsum(beam_by_variant[s['beam_variant']]['manufactured_study_mass_kg']*9.81/1000 for s in ordinary)
        foundations.append(dict(id='FND:' + key, support_id=key, line=record['line'], chainage_m=record['chainage_m'],
                                 lon=ll[0], lat=ll[1], x_m=xy[0], y_m=xy[1], adjacent_span_ids=';'.join(record['spans']),
                                 nearest_desktop_soil_sample=nearest['sample_id'] if nearest else None,
                                 desktop_sample_chainage_offset_m=round(abs(nearest.get('chainage_m', 0.) - record['chainage_m']), 3) if nearest else None,
                                 soil_investigation_flags=';'.join(nearest.get('investigation_flags', [])) if nearest else '',
                                 cyclic_boundary_alias_support_id=record.get('cyclic_boundary_alias'),
                                 shared_front_stage_coordination_required=len({front_span[s] for s in record['spans'] if s in front_span})>1,
                                 simply_supported_beam_deadload_screen_kn=round(gravity_screen,3),
                                 adjacent_special_loads_unknown=len(ordinary)!=len(record['spans']),
                                 complete_foundation_design_axial_kn=None,foundation_design_lateral_kn=None,
                                 foundation_design_moment_knm=None,load_combination_accepted=False,
                                 junction_interface_ids=';'.join(affected),
                                 candidate_family_review='bored shaft / driven bent / shallow footing / pile group by verified ground and loads',
                                 selected_foundation_type=None, pile_count=None, installed_depth_m=None,
                                 allowable_bearing_kpa=None, groundwater_depth_m=None,
                                 required_load_cases='permanent/train; asymmetric beam; launcher/advance; delivery; braking/wind/seismic/scour',
                                 foundation_design_accepted=False, construction_method='foundation-and-substructure',
                                 accepted_support_packet=None))
    coincident = defaultdict(list)
    for f in foundations:
        coincident[(f['x_m'], f['y_m'])].append(f['id'])
    colliding = [dict(xy=list(k), foundation_ids=v, treatment='coordinated shared/offset support design required; no implicit duplicate footing')
                 for k, v in sorted(coincident.items()) if len(v) > 1]
    if aliases:
        colliding.append(dict(kind='resolved-closed-ring-boundary-alias',alias_to_canonical=aliases,
                              treatment='one physical foundation packet for both chainage boundaries; combined/shared launcher stages require release',
                              physical_quantity_or_cost_saving_adopted=False))
    return foundations, spans, front_rows, colliding


def build(geometry_only=False):
    cfg = json.loads(CONFIG.read_text())
    if cfg['native_service_and_finance_baseline_replaced'] or any(cfg['evidence'].values()):
        # year is metadata, all adoption/acceptance flags must remain false.
        if cfg['native_service_and_finance_baseline_replaced'] or any(v for k, v in cfg['evidence'].items() if k != 'population_year'):
            raise ValueError('planning compiler cannot create field or operating acceptance')
    context = json.loads(gzip.decompress(CONTEXT.read_bytes()))
    design_path = CITY / 'design.toml'
    design = tomllib.loads(design_path.read_text())
    geometry_path = CITY / 'baghdad.corridor.geojson'
    grid_path = CITY / 'engineering/alignment/planning-grid.json'
    routes, stations, project, unproject = coordinates(design, json.loads(geometry_path.read_text()), json.loads(grid_path.read_text()))
    interfaces = geometry_interfaces(routes)
    lengths = {l['name']: l['length_m'] for l in design['lines']}
    for interface in interfaces:
        interface['lon'], interface['lat'] = unproject(*interface['xy'])
        interface['line_chainage_legs_m'] = {name: legs_at_interface(routes[name], interface['xy'], lengths[name]) for name in interface['lines']}
        interface['foundation_and_station_coordination_required'] = True
        interface['construction_design_accepted'] = False
    complexes = complete_link_groups(stations, cfg['geometry']['interchange_diameter_limit_m'])
    by_id = {s['id']: s for s in stations}
    declared = []
    for item in design['interchanges']:
        members = [by_id[i] for i in item['platforms']]
        diameter = round(max((math.dist(a['xy'], b['xy']) for a, b in itertools.combinations(members, 2)), default=0), 3)
        declared.append(dict(id=item['id'], platform_ids=item['platforms'], lines=item['lines'], maximum_separation_m=diameter,
                             oversized=diameter > cfg['geometry']['interchange_diameter_limit_m'],
                             proposed_complex_ids=[g['id'] for g in complexes if set(g['platform_ids']) & set(item['platforms'])],
                             native_operating_topology_replaced=False))
    for group in complexes:
        group['lon'], group['lat'] = unproject(*group['centre_xy'])
        group['station_structure_package'] = 'integrated multi-line platforms/concourse/street access with reviewed loads and clearances'
        group['walk_connector_segments_xy'] = [[by_id[a]['xy'], by_id[b]['xy']] for a, b in itertools.combinations(group['platform_ids'], 2)
                                              if by_id[a]['line'] != by_id[b]['line']]
    population, infill, gaps, heat, expansion_routes, expansion_edges = residential_plan(design, routes, stations, project, unproject, cfg['coverage'], context)
    templates = {
        'foundation-and-substructure': [
            dict(stage='F0', name='support-specific survey, utilities, ground/water and load design', predecessors=[]),
            dict(stage='F1', name='trial/verification and temporary working platform release', predecessors=['F0']),
            dict(stage='F2', name='selected foundation installation, actual geometry and material logs', predecessors=['F1']),
            dict(stage='F3', name='integrity/load/settlement/dimension tests and accepted foundation packet', predecessors=['F2']),
            dict(stage='P0', name='column/cap, connection strength, bearing seats and temporary restraint', predecessors=['F3']),
            dict(stage='B0', name='bearing survey plus actual next launcher/beam/delivery stage-load release', predecessors=['P0'])],
        'paired-full-span-bay': [
            dict(stage='E0', name='both B0 support packets, both accepted beam travellers, delivery and predecessor/relocation release', predecessors=['support_a:B0', 'support_b:B0', 'track1:H1', 'track2:H1']),
            dict(stage='E1', name='first beam controlled lift, seating and required lateral/torsional restraint', predecessors=['E0']),
            dict(stage='E2', name='second beam controlled lift and paired securing/survey', predecessors=['E1']),
            dict(stage='E3', name='selected connections/strength, bearings, joints, dimensional and NCR acceptance', predecessors=['E2']),
            dict(stage='E4', name='checked advance loads, next supports and safe launcher move', predecessors=['E3']),
            dict(stage='E5', name='walkway/barrier, waterproofing/drainage, track interface and following-trade handover', predecessors=['E4'])],
        'beam-production-and-delivery': [
            dict(stage='M0', name='supplier drawing/reinforcement/prestress/lifting/support configuration freeze', predecessors=[]),
            dict(stage='M1', name='mould/cage/inserts, stressing, cast/curing and batch traceability', predecessors=['M0']),
            dict(stage='M2', name='distinct strength gates for transfer/demould/lift/storage/install and inspection', predecessors=['M1']),
            dict(stage='M3', name='accepted serialised beam, complete mass/CG and traveller', predecessors=['M2']),
            dict(stage='H0', name='permitted vehicle/route/loading, appointment and receiving release', predecessors=['M3']),
            dict(stage='H1', name='receipt/damage survey, supported storage and install-sequence reservation', predecessors=['H0'])],
        'special-structure': [dict(stage='SP0', name='independent special geometry/stage/foundation design', predecessors=[]),
                              dict(stage='SP1', name='supplier-specific staged construction and tests', predecessors=['SP0']),
                              dict(stage='SP2', name='structural/track/interface handover', predecessors=['SP1'])],
        'junction-interface': [dict(stage='J0', name='select crossing/shared-corridor/reroute and accessible interchange arrangement', predecessors=[]),
                               dict(stage='J1', name='freeze levels, gradients, clearances, cap/support and station load paths', predecessors=['J0']),
                               dict(stage='J2', name='site/foundation/temporary works, utility/access and stage design release', predecessors=['J1']),
                               dict(stage='J3', name='coordinated construction, as-built structure/access and railway qualification', predecessors=['J2'])]}
    core_sources = [CONFIG, design_path, geometry_path, grid_path, CONTEXT,
                    CITY / 'engineering/access/population-pixels.npz.gz', CITY / 'engineering/access/population-source.json',
                    Path(__file__), ROOT / 'tools/automation/network_integration.py', ROOT / 'tools/automation/city_access.py']
    sources = {p.relative_to(ROOT).as_posix(): sha(p) for p in core_sources}
    # The core content revision describes inputs and geometry transformation.
    # Publication/assembly edits to this compiler remain locked by the final
    # parent manifest without creating a connected-package dependency cycle.
    geometry_sources={k:v for k,v in sources.items() if k!=Path(__file__).relative_to(ROOT).as_posix()}
    core = dict(schema='osr-network-integration/1', status=cfg['status'], source_revision=hashlib.sha256(encode(geometry_sources)).hexdigest(),
                baseline_native_design_sha256=sha(design_path), native_service_and_finance_baseline_replaced=False,
                interfaces=interfaces, bounded_complexes=complexes, original_complex_review=declared,
                population=population, infill_stations=infill, residential_priority_areas=gaps, expansion_corridor_candidates=expansion_routes,
                geometry_is_surveyed=False, population_is_current_census=False, physical_acceptance=False)
    if geometry_only:
        return {'network-integration.json':encode(core)},sources,None,None,None,None
    foundations, spans, fronts, collisions = foundation_assembly(design, routes, unproject, interfaces)
    audit_rows, audit_sources = catalogue_audit()
    line_summary = []
    for line in design['lines']:
        name = line['name']
        line_summary.append(dict(line=name, length_m=line['length_m'],
                                 foundation_records=sum(f['line'] == name for f in foundations),
                                 catalogue_bays=sum(s['line'] == name and s['classification'] == 'catalogue-planning-span' for s in spans),
                                 special_spans=sum(s['line'] == name and s['classification'] == 'special-design-required' for s in spans),
                                 fronts=[f['id'] for f in fronts if f['line'] == name],
                                 junction_interface_ids=[i['id'] for i in interfaces if name in i['lines']],
                                 proposed_infill_station_ids=[s['id'] for s in infill if s['line'] == name],
                                 selected_foundation_quantities=None, accepted_complete_opening_date=None))
    summary = dict(schema='osr-line-assembly-planning/1', as_of=cfg['as_of'], lines=line_summary,
                   proposed_foundation_records=len(foundations), identified_catalogue_bays=len(front_span_ids := [s for s in spans if s['front']]),
                   special_structure_packages=sum(s['assembly_template'] == 'special-structure' for s in spans),
                   uniquely_assigned_catalogue_spans=len(front_span_ids), geometry_interfaces=len(interfaces),
                   oversized_original_interchange_groups=sum(c['oversized'] for c in declared),
                   coordinated_bounded_interchange_complexes=len(complexes),
                   foundation_location_conflicts=sum(row.get('kind')!='resolved-closed-ring-boundary-alias' for row in collisions),
                   resolved_cyclic_boundary_aliases=sum(row.get('kind')=='resolved-closed-ring-boundary-alias' for row in collisions),
                   initial_launcher_fronts=len(fronts), population=population, construction_released=False,
                   desktop_soil_does_not_select_foundation_type=True, complete_installed_capital_usd=None)
    geo_features = []
    for item in interfaces:
        geo_features.append(dict(type='Feature', geometry=dict(type='Point', coordinates=[item['lon'], item['lat']]),
                                 properties={k: v for k, v in item.items() if k not in ('xy', 'geometry_xy')}))
    for item in infill + gaps:
        geo_features.append(dict(type='Feature', geometry=dict(type='Point', coordinates=[item['lon'], item['lat']]),
                                 properties={k: v for k, v in item.items() if k != 'xy'}))
    extra_scopes=[]
    for station in stations:
        extra_scopes.append(dict(id='STN-FND:'+station['id'],line=station['line'],kind='station-foundation-and-structure',
                                 station_id=station['id'],lon=station['lon'],lat=station['lat'],
                                 support_count=None,foundation_geometry=None,
                                 requirements=['platform/concourse/roof/shaft/stair loads and geometry','ground and groundwater',
                                               'spreading-approach/shared-running-support ownership','lift/fire/rescue/street access'],
                                 construction_released=False))
    for i,segment in enumerate(design['civil_segments'],1):
        if segment['class']!='bridge':continue
        midpoint=(segment['from_station_m']+segment['to_station_m'])/2
        ll=unproject(*line_at_chainage(routes[segment['line']],midpoint,lengths[segment['line']]))
        extra_scopes.append(dict(id=f"BRIDGE-FND:{segment['line']}:{i:04d}",line=segment['line'],kind='water-and-special-bridge-foundations',
                                 from_m=segment['from_station_m'],to_m=segment['to_station_m'],lon=ll[0],lat=ll[1],
                                 support_count=None,foundation_geometry=None,
                                 requirements=['ground/deep stratigraphy','hydrology flood scour and navigation',
                                               'bridge span/foundation/temporary works and installation access','authority permissions'],construction_released=False))
    for i,depot in enumerate(design['depots'],1):
        station=by_id[depot['station']]
        extra_scopes.append(dict(id=f'DEPOT-FND:{i:03d}',line=station['line'],kind='depot-yard-workshop-and-energy-foundations',
                                 station_id=station['id'],lon=station['lon'],lat=station['lat'],support_count=None,foundation_geometry=None,
                                 requirements=['usable yard and berth plan','buildings/pits/jacking/cranes equipment loads','ground drainage and contaminated water',
                                               'PV/battery/charging foundations fire and replacement access'],construction_released=False))
    for station in stations:
        extra_scopes.append(dict(id='ENERGY-FND:'+station['id'],line=station['line'],kind='declared-station-energy-civil-interface',
                                 station_id=station['id'],lon=station['lon'],lat=station['lat'],support_count=None,foundation_geometry=None,
                                 requirements=['selected power/storage equipment and load/thermal/fire data','foundations ducts earthing and drainage',
                                               'safe equipment/replacement/inspection access'],construction_released=False))
    junction_packages=[]
    for interface in interfaces:
        affected_spans=[s['id'] for s in spans if interface['id'] in s['junction_interface_ids'].split(';')]
        affected_foundations=[f['id'] for f in foundations if interface['id'] in f['junction_interface_ids'].split(';')]
        alternatives=(['separate laterally coordinated guideways and common station/access footprint','separate vertical levels with reviewed ramps and foundations']
                      if interface['kind']=='shared-corridor' else ['grade-separated decks with accessible interchange where useful','reviewed route adjustment preserving residential catchments'])
        junction_packages.append(dict(id='JUNCTION:'+interface['id'],interface_id=interface['id'],kind=interface['kind'],
                                      lines=interface['lines'],line_chainage_legs_m=interface['line_chainage_legs_m'],
                                      affected_span_ids=affected_spans,affected_foundation_ids=affected_foundations,
                                      design_alternatives=alternatives,selected_alternative=None,
                                      lower_rail_level_m=None,upper_rail_level_m=None,required_vertical_clearance_m=None,
                                      gradient_transition_and_support_geometry_accepted=False,
                                      release_sequence=['J0 arrangement and land/utility/access options','J1 actual levels/grades/clearances/load paths',
                                                        'J2 independently checked site/stage design and permits','J3 construction and integrated handover'],
                                      catalogue_orders_held_until_J2=True,track_switch_implied=False))
    outputs = {'network-integration.json': encode(core), 'line-assembly-summary.json': encode(summary),
               'foundation-register.csv.gz': packed(csv_data(foundations, list(foundations[0]))),
               'span-assembly-register.csv.gz': packed(csv_data(spans, list(spans[0]))),
               'launcher-fronts.json': encode(fronts), 'assembly-stage-library.json': encode(templates),
               'foundation-location-conflicts.json': encode(collisions),
               'junction-design-packages.json':encode(junction_packages),
               'other-structure-foundation-scopes.json':encode(extra_scopes),
               'expansion-corridors.json': encode(expansion_routes),
               'shared-expansion-corridor-edges.json': encode(expansion_edges),
               'residential-heat.json.gz': packed(encode(heat)),
               'junctions-and-residential-plan.geojson': encode(dict(type='FeatureCollection', features=geo_features)),
               'catalogue-audit.csv': csv_data(audit_rows, list(audit_rows[0])),
               'catalogue-audit-summary.json': encode(dict(cities=len(audit_rows),
                   disconnected_declared_networks=sum(r['declared_transfer_components'] is not None and r['declared_transfer_components'] > 1 for r in audit_rows),
                   cities_with_self_intersecting_lines=sum(bool(r['self_intersecting_lines']) for r in audit_rows),
                   cities_with_overlapping_lines=sum(bool(r['cross_line_overlap_pairs']) for r in audit_rows),
                   cities_with_oversized_interchanges=sum(bool(r['oversized_declared_interchange_groups']) for r in audit_rows),
                   geometry_release=False, sources_sha256=audit_sources))}
    source_more = [CITY / 'engineering/connected-build/span-layout.json', CITY / 'engineering/connected-build/civil.json',
                   CITY / 'engineering/soil/sample-locations.geojson', CITY / 'engineering/soil/civil-investigation-plan.json',
                   ROOT/'docs/civil/line-based-foundation-and-assembly-planning.md',ROOT/'docs/civil/network-junction-and-residential-integration.md']
    correction_snapshot=OUT/'corrected-alignment-sources.json.gz'
    if correction_snapshot.is_file():source_more.append(correction_snapshot)
    sources.update({p.relative_to(ROOT).as_posix(): sha(p) for p in source_more})
    return outputs, sources, routes, stations, heat, summary


def render_map(routes, stations, heat, summary, core):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(15, 9), constrained_layout=True)
    for ax in axes:
        for name, route in sorted(routes.items()):
            x, y = np.asarray(route.coords).T
            ax.plot(x/1000, y/1000, lw=1.4, label=name)
        ax.scatter([s['xy'][0]/1000 for s in stations], [s['xy'][1]/1000 for s in stations], s=6, c='#171717')
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set(xlabel='Local planning east km', ylabel='Local planning south km')
    uncovered = [h for h in heat if h['unserved_2020'] >= 100]
    axes[0].scatter([(h['x']+250)/1000 for h in uncovered], [(h['y']+250)/1000 for h in uncovered],
                    s=[min(50, h['unserved_2020']/100) for h in uncovered], c='#dc2626', alpha=.3, zorder=0)
    axes[0].set_title('Current stations and unserved 2020 residential pixels')
    for item in core['interfaces']:
        axes[1].scatter(item['xy'][0]/1000, item['xy'][1]/1000, s=30, marker='x', c='#dc2626')
    axes[1].scatter([s['xy'][0]/1000 for s in core['infill_stations']], [s['xy'][1]/1000 for s in core['infill_stations']],
                    s=35, marker='+', c='#16a34a', label='infill candidates')
    for area in core['residential_priority_areas']:
        axes[1].scatter(area['xy'][0]/1000, area['xy'][1]/1000, s=90, facecolors='none', edgecolors='#9333ea')
        axes[1].annotate(area['id'].split('-')[-1], (area['xy'][0]/1000, area['xy'][1]/1000), fontsize=8)
    grid=json.loads((CITY/'engineering/alignment/planning-grid.json').read_text())
    for proposal in core['expansion_corridor_candidates']:
        xs=[(c[0]-grid['bbox_west'])*grid['m_per_deg_lon']/1000 for c in proposal['geometry_lonlat']]
        ys=[(grid['bbox_north']-c[1])*grid['m_per_deg_lat']/1000 for c in proposal['geometry_lonlat']]
        axes[1].plot(xs,ys,color='#9333ea',lw=1,linestyle='--',alpha=.8)
    axes[1].set_title('Coordinated crossing/overlap interfaces and coverage priorities')
    axes[1].legend(fontsize=7, loc='lower left')
    fig.suptitle('Baghdad — integrated network and line-specific civil planning', fontsize=15)
    fig.supxlabel('Concept geometry. Red: unresolved structures / residents outside 1 km station circles. Green: infill study. Purple: branch/feeder study areas. No accepted walking coverage or construction release.', fontsize=8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=105)
    plt.close(fig)
    return buffer.getvalue()


def finish(outputs, sources, routes, stations, heat, summary):
    core = json.loads(outputs['network-integration.json'])
    outputs['network-and-residential-review.png'] = render_map(routes, stations, heat, summary, core)
    from network_plan_viewer import viewer
    outputs['network-foundation-viewer.html']=viewer(outputs,routes,stations)
    sources['tools/automation/network_plan_viewer.py']=sha(ROOT/'tools/automation/network_plan_viewer.py')
    span_rows=list(csv.DictReader(io.StringIO(gzip.decompress(outputs['span-assembly-register.csv.gz']).decode())))
    front_rows=json.loads(outputs['launcher-fronts.json'])
    for line in summary['lines']:
        name=line['line'];selected=[s for s in span_rows if s['line']==name];fronts=[f for f in front_rows if f['line']==name]
        doc=[f"# {name} — foundation and assembly construction plan",'',
             'Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.','',
             f"Route length {line['length_m']/1000:.3f} km. {line['foundation_records']:,} unique proposed support packets; {line['catalogue_bays']:,} identified catalogue bay assemblies and {line['special_spans']:,} special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.",'',
             '| Front | Launcher | Direction | Initial assembly chainage m | Bay assemblies |','|---|---|---:|---:|---:|']
        for f in fronts:doc.append(f"| {f['id']} | {f['launcher']} | {f['direction']} | {f['initial_assembly_chainage_m']:.1f} | {len(f['span_ids'])} |")
        doc+=['','## Foundation workface plan','',
              f"Filter [the foundation register](foundation-register.csv.gz) by `{name}`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.",'',
              'Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.','',
              '## Directed assembly and logistics sequence','',
              'The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.','',
              'For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.','',
              'Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.','',
              'Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.','',
              '## Initial bay packages','',
              '| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |','|---|---:|---|---|---|---|---|']
        for f in fronts:
            first=sorted([s for s in selected if s['front']==f['id']],key=lambda s:int(s['sequence']))[:6]
            for s in first:doc.append(f"| {s['front']} | {s['sequence']} | {s['id']} | {s['beam_variant']} | {s['foundation_a']} | {s['foundation_b']} | {s['previous_front_span'] or 'mobilisation'} |")
        doc+=['','The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.','',
              '## Junctions, stations and residential interfaces','',
              'Coordinated structural interface IDs on this line: '+(', '.join(line['junction_interface_ids']) or 'none found in the retained geometry screen')+'.','',
              'Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.','',
              'Candidate infill IDs: '+(', '.join(line['proposed_infill_station_ids']) or 'no qualifying candidate under this screen')+'.','',
              '## Inspection, handover and programme','',
              'Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.','',
              '[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).','']
        outputs[name+'-construction-plan.md']='\n'.join(doc).encode()
    rows = ['# Baghdad integrated network, foundations and assembly plan', '',
            '**Coordinated design-development concept; field construction and operating adoption remain open.**', '',
            '![Network interfaces and residential gaps](network-and-residential-review.png)', '',
            '[Interactive line / support / junction viewer](network-foundation-viewer.html) lets reviewers zoom, select a line and inspect individual support packets and interface records offline.', '',
            'One source-bound asset graph connects each line, actual span, shared support, beam, launcher front, junction interface, station complex and residential intervention. The current native timetable/finance remains a comparator; this package does not claim new operating service or accepted structural profiles.', '',
            f"The plan assigns **{summary['proposed_foundation_records']:,} support-specific foundation packets**, **{summary['identified_catalogue_bays']:,} catalogue bay assemblies**, **{summary['special_structure_packages']:,} specials** and **{summary['initial_launcher_fronts']} launcher fronts**. Support packets have coordinates, chainage, adjacent spans, desktop-soil investigation references and required loads/tests. Pile type/count/depth, groundwater and bearing capacity remain unselected until field design.", '',
            '| Line | Foundation packets | Catalogue bay assemblies | Special packages | Candidate infill |',
            '|---|---:|---:|---:|---:|']
    for line in summary['lines']:
        rows.append(f"| [{line['line']}]({line['line']}-construction-plan.md) | {line['foundation_records']} | {line['catalogue_bays']} | {line['special_spans']} | {len(line['proposed_infill_station_ids'])} |")
    p = summary['population']
    rows += ['', '## Junction and overlap coordination', '',
             f"{summary['geometry_interfaces']} crossing/shared-corridor/self-crossing interfaces need explicit structural treatment. {summary['oversized_original_interchange_groups']} original interchange groups exceed the 600 m full-diameter screen. The new bounded grouping prevents transitive long-distance complexes and preserves platform coordinates. It does not create a track switch, measured walking path or accepted vertical profile.", '',
             '[Integrated geometry and complex register](network-integration.json) · [GIS junction/residential layer](junctions-and-residential-plan.geojson) · [Foundation coordinate conflicts](foundation-location-conflicts.json).', '',
             '## Residential coverage and expansion', '',
             f"Retained 2020 population within 1 km station circles is **{p['baseline_radial_fraction_1000m']:.1%}**. {p['candidate_infill_count']} population-ranked infill candidates give a conditional radial sensitivity of **{p['infill_conditional_radial_fraction_1000m']:.1%}**. **{p['baseline_unserved_outside_existing_corridor_vertex_screen_1000m']:,.0f}** currently unserved retained residents are also over 1 km from sampled existing corridors; infill cannot close those gaps. {p['gap_priority_areas']} named/located priority areas therefore require branch/extension or funded feeder/access studies. Area circles can overlap and are never summed as unique residents.", '',
             'These are native population-count and distance screens, not current census, surveyed walksheds, ridership or funded service. Candidate sites need water/footprint/property/access, station structure, timetable, fleet, energy and full installed cost review.', '',
             f"[Expansion corridor plans](expansion-corridors.json) provide {p['expansion_corridor_candidates']} source-bound routes along the retained arterial graph, tied to existing station connections, with access gaps and proposed stopping sites. Compare rail branches with frequent feeders; traffic direction, bridge grades/loads, railway curvature and walk routes are unverified. The combined infill/feeder 500 m stop-circle sensitivity is {p['infill_and_feeder_500m_stop_circle_sensitivity']:.1%}; the rail 1 km sensitivity is {p['infill_and_rail_1000m_station_circle_sensitivity']:.1%}. [Shared corridor edges](shared-expansion-corridor-edges.json) count overlapping candidate road segments once. No corridor is adopted or funded.", '',
             '## Foundation and assembly execution', '',
             '[Foundation register](foundation-register.csv.gz) has one row per unique proposed support. [Span assembly register](span-assembly-register.csv.gz) has identified component pairs and both foundation parents, actual line/run, unique front assignment, sequence and predecessor. [Launcher fronts](launcher-fronts.json) preserve disconnected runs and relocation gates. [Stage library](assembly-stage-library.json) defines foundation/column/cap/bearing, factory/delivery, first/second beam securing, advance and handover dependencies. Specials and junctions use their own design/erection chains.', '',
             'Decode compressed CSV using `python -c "import gzip; print(gzip.open(\'foundation-register.csv.gz\',\'rt\').read())"`. Coordinates are interpolated from the retained planning route; desktop soil does not select a foundation, and no pile depth or allowable bearing value is invented.', '',
             '[Complete per-line summary](line-assembly-summary.json) · [Wider catalogue audit](catalogue-audit.csv) · [Catalogue findings and provenance](catalogue-audit-summary.json).', '',
             '[Companion data archive](Baghdad-Network-and-Foundation-Planning.zip) contains this planning package and new controlled inputs. The original Baghdad proposal archive retains the baseline city/engineering input evidence. Use both for the full planning review; the companion does not imply physical release.', '',
             'Run `python tools/automation/integrated-network-plan.py`; `--check` validates source/output hashes. `--retain-context` creates the immutable retained OSM road/name input from the cached extraction. Native route and financial assumptions change only through a subsequent fully regenerated, validated adoption revision.', '']
    outputs['README.md'] = '\n'.join(rows).encode()
    # Keep the added planning dataset in a separate bounded archive, preserving
    # the original 49.6 MiB supporting archive and all its existing access.
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_LZMA) as z:
        for name, raw in sorted(outputs.items()):
            item = zipfile.ZipInfo((OUT.relative_to(ROOT)/name).as_posix(), date_time=(2026, 10, 8, 0, 0, 0))
            item.compress_type = zipfile.ZIP_LZMA
            item.external_attr = 0o644 << 16
            z.writestr(item, raw)
        companion_inputs=[CONFIG, CONTEXT, Path(__file__), ROOT / 'tools/automation/network_integration.py',ROOT/'tools/automation/network_plan_viewer.py']
        if (OUT/'corrected-alignment-sources.json.gz').is_file():companion_inputs.append(OUT/'corrected-alignment-sources.json.gz')
        for path in companion_inputs:
            item = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 10, 8, 0, 0, 0))
            item.compress_type = zipfile.ZIP_LZMA
            item.external_attr = 0o644 << 16
            z.writestr(item, path.read_bytes())
    outputs['Baghdad-Network-and-Foundation-Planning.zip'] = archive.getvalue()
    outputs['manifest.json'] = encode(dict(schema='osr-integrated-planning-manifest/1', sources_sha256=sources,
        source_revision=hashlib.sha256(encode(sources)).hexdigest(),
        outputs_sha256={k: hashlib.sha256(v).hexdigest() for k, v in sorted(outputs.items())},
        construction_released=False, original_city_archive_preserved=True))
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retain-context', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--geometry-only', action='store_true',help='prepare independent network input before regenerating connected construction')
    args = parser.parse_args()
    if args.retain_context:
        retain_context()
    if args.check:
        manifest = json.loads((OUT / 'manifest.json').read_text())
        for path, expected in manifest['sources_sha256'].items():
            if sha(ROOT / path) != expected:
                raise SystemExit('stale network/foundation source: ' + path)
        for name, expected in manifest['outputs_sha256'].items():
            if sha(OUT / name) != expected:
                raise SystemExit('changed network/foundation output: ' + name)
        audit = json.loads((OUT / 'catalogue-audit-summary.json').read_text())
        for path, expected in audit['sources_sha256'].items():
            if sha(ROOT / path) != expected:
                raise SystemExit('stale catalogue integration source: ' + path)
        with zipfile.ZipFile(OUT / 'Baghdad-Network-and-Foundation-Planning.zip') as archive:
            if archive.testzip() is not None:
                raise SystemExit('invalid companion archive')
        print('Integrated junction/residential/foundation/assembly package current; field and operating adoption open')
        return
    outputs, sources, routes, stations, heat, summary = build(geometry_only=args.geometry_only)
    if args.geometry_only:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'network-integration.json').write_bytes(outputs['network-integration.json'])
        print('Prepared coordinated network input; foundation/assembly export follows connected regeneration')
        return
    outputs = finish(outputs, sources, routes, stations, heat, summary)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, raw in outputs.items():
        if len(raw) > 50 * 1024**2:
            raise ValueError('planning artifact exceeds repository file limit: ' + name)
        (OUT / name).write_bytes(raw)
    print(f'Published {len(outputs)} integrated network and line-specific civil planning artifacts')


if __name__ == '__main__':
    main()
