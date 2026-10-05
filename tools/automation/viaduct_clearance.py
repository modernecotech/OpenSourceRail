"""Exact footprint intersections and conditional vertical viaduct screening.

No footprint or unknown height is evidence of obstacle clearance. This screen
does not turn terrain-following height assumptions into a vertical design.
"""
from __future__ import annotations

import math
import re

import numpy as np
from shapely.geometry import LineString, Point, Polygon, shape
from shapely import get_coordinates
from shapely.ops import substring
from shapely.strtree import STRtree

DEFAULT_POLICY = dict(twin_track_envelope_m=9.0, lateral_clearance_m=2.0,
                      foundation_radius_m=3.0, foundation_setback_m=2.0,
                      reference_rail_height_m=12.0, beam_depth_m=1.6,
                      roof_clearance_m=2.0, span_m=25.0,
                      maximum_gradient_percent=3.5, terrain_sample_m=5.0)


def height_metres(value):
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(value) and value >= 0 else None
    match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(m|metres?|meters?|ft|feet|\')?\s*', str(value), re.I)
    if not match:
        return None
    return float(match[1]) * (.3048 if match[2] and match[2].lower() in {'ft', 'feet', "'"} else 1)


def projected_buildings(features, project):
    polygons, records, invalid = [], [], []
    for feature in features:
        try:
            if feature.get('type') == 'Feature':
                from shapely.ops import transform
                polygon = transform(project, shape(feature['geometry']))
                props = feature.get('properties', {})
            else:
                polygon = Polygon([project(lon, lat) for lat, lon in feature['nodes']])
                props = {**feature, **feature.get('tags', {})}
            if polygon.is_empty or not polygon.is_valid or polygon.geom_type not in {'Polygon', 'MultiPolygon'}:
                raise ValueError('Invalid footprint')
            height = height_metres(props.get('height', props.get('height_m')))
            # Levels are only an uncertain estimate, never a measured height.
            floors = height_metres(props.get('building:levels', props.get('num_floors')))
            estimate = floors * 3.5 if floors is not None else None
            records.append(dict(id=str(props.get('id', feature.get('id', len(records)))),
                                height_m=height, floor_based_estimate_m=estimate,
                                height_basis='source-height-tag' if height is not None else 'unknown',
                                properties=props))
            polygons.append(polygon)
        except (ValueError, TypeError, KeyError):
            invalid.append(str(feature.get('id', 'unknown')))
    return polygons, records, invalid


def screen_line(route, civil, polygons, records, elevation=None, policy=None):
    """Beam swept envelope + separate ground support envelope at 25 m pitch.

    Terrain is sampled along the route; straight 25 m beam soffits interpolate
    ground-height-plus-reference-height at their supports, so a crest between
    supports cannot be hidden by following every terrain sample.
    """
    policy = {**DEFAULT_POLICY, **(policy or {})}
    if any(not math.isfinite(value) or value <= 0 for value in policy.values()):
        raise ValueError('Positive finite clearance policy required')
    tree = STRtree(polygons)
    coordinates=np.asarray(route.coords,dtype=float)[:,:2]
    chainages=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(coordinates,axis=0),axis=1))]
    def interpolate(at):
        at=min(float(chainages[-1]),max(0.,float(at)))
        index=min(len(coordinates)-2,max(0,int(np.searchsorted(chainages,at,side='right'))-1))
        length=chainages[index+1]-chainages[index]
        fraction=(at-chainages[index])/length if length else 0.
        point=coordinates[index]+fraction*(coordinates[index+1]-coordinates[index])
        return Point(float(point[0]),float(point[1]))
    conflicts, supports, terrain, gaps = [], [], [], []
    gradient = policy['maximum_gradient_percent']
    for segment_index, segment in enumerate(civil):
        start = max(0., float(segment['from_station_m']))
        end = min(route.length, float(segment['to_station_m']))
        if end <= start:
            continue
        centre = substring(route, start, end)
        if centre.geom_type != 'LineString':
            continue
        elevated = segment['class'] in {'elevated', 'bridge'}
        sweep = centre.buffer(policy['twin_track_envelope_m'] / 2 + policy['lateral_clearance_m'])
        structural_sweep = centre.buffer(policy['twin_track_envelope_m'] / 2)
        depth_resolved = segment.get('viaduct_product') in {'OSR-Pi20', 'OSR-Pi25'}
        for index in tree.query(sweep, predicate='intersects'):
            polygon, record = polygons[index], records[index]
            intersection = polygon.intersection(sweep)
            direct_intersection = polygon.intersects(structural_sweep)
            point = intersection.representative_point()
            chainage = route.project(point)
            footprint_points = get_coordinates(intersection)
            ground_samples = [elevation(x, y) for x, y in footprint_points] if elevation and record['height_m'] is not None else []
            ground = max(ground_samples) if ground_samples and all(value is not None for value in ground_samples) else None
            roof = ground + record['height_m'] if ground is not None and record['height_m'] is not None else None
            soffit = None
            if elevated and elevation and depth_resolved and roof is not None:
                projected = [min(end, max(start, route.project(Point(x, y)))) for x, y in footprint_points]
                lo, hi = min(projected), max(projected)
                pitch = 20. if segment.get('viaduct_product') == 'OSR-Pi20' else policy['span_m']
                checks = [lo, hi, *np.arange(start, end, pitch)[
                    (np.arange(start, end, pitch) >= lo) & (np.arange(start, end, pitch) <= hi)]]
                soffits = []
                for at in checks:
                    left = start + math.floor((at-start)/pitch) * pitch
                    # The endpoint belongs to the preceding span.
                    if left >= end: left = max(start, left-pitch)
                    right = min(end, left+pitch)
                    a, b = interpolate(left), interpolate(right)
                    za, zb = elevation(a.x, a.y), elevation(b.x, b.y)
                    if za is None or zb is None or right <= left:
                        soffits=[];break
                    soffits.append(za+(zb-za)*(at-left)/(right-left)+policy['reference_rail_height_m']-policy['beam_depth_m'])
                if soffits:soffit=min(soffits)
            status = (('ground-collision' if direct_intersection else 'ground-lateral-clearance-conflict') if not elevated else 'product-depth-unresolved'
                      if not depth_resolved else 'height-unresolved'
                      if roof is None or soffit is None else ('beam-roof-collision' if direct_intersection else 'lateral-clearance-conflict')
                      if roof + policy['roof_clearance_m'] > soffit else 'conditional-roof-overflight')
            conflicts.append(dict(segment_index=segment_index, building=record['id'],
                                  chainage_m=round(chainage, 3), status=status,
                                  intersects_structural_envelope=direct_intersection,
                                  product_depth_reference_available=depth_resolved,
                                  source_height_m=record['height_m'], estimated_height_m=record['floor_based_estimate_m'],
                                  ground_elevation_m=ground, roof_elevation_m=roof,
                                  reference_soffit_elevation_m=soffit,
                                  minimum_reference_rail_height_m=(record['height_m'] + policy['roof_clearance_m'] + policy['beam_depth_m'])
                                  if record['height_m'] is not None else None,
                                  minimum_extra_height_approach_each_side_m=(
                                      max(0., roof+policy['roof_clearance_m']-soffit)/(policy['maximum_gradient_percent']/100))
                                      if roof is not None and soffit is not None else None,
                                  conservative_height_basis='Highest sampled footprint ground/roof against lowest reference soffit across its projected interval.',
                                  physical_release=False))
        if not elevated:
            continue
        if segment['class'] == 'bridge' or segment.get('viaduct_product') not in {'OSR-Pi20', 'OSR-Pi25'}:
            gaps.append(dict(segment_index=segment_index, kind='special-product-depth-and-support-layout-unresolved',
                             from_m=start, to_m=end))
        span = 20. if segment.get('viaduct_product') == 'OSR-Pi20' else policy['span_m']
        positions = [float(at) for at in np.arange(start, end, span) if at < end - 1e-6] + [end]
        for chainage in positions:
            point = interpolate(chainage)
            envelope = point.buffer(policy['foundation_radius_m'] + policy['foundation_setback_m'])
            hits = tree.query(envelope, predicate='intersects')
            direct_hits = tree.query(point.buffer(policy['foundation_radius_m']), predicate='intersects')
            supports.append(dict(segment_index=segment_index, chainage_m=round(float(chainage), 3),
                                 x_m=round(point.x, 3), y_m=round(point.y, 3),
                                 buildings=[records[index]['id'] for index in hits],
                                 status='foundation-footprint-conflict' if len(direct_hits) else 'foundation-setback-conflict' if len(hits) else 'mapped-footprints-only-clear',
                                 physical_release=False))
        if end - positions[-2] < span - .05:
            gaps.append(dict(segment_index=segment_index, kind='boundary-span-layout-unresolved',
                             from_m=positions[-2], to_m=end))
        if elevation is None:
            gaps.append(dict(segment_index=segment_index, kind='terrain-unavailable', from_m=start, to_m=end))
            continue
        for left, right in zip(positions, positions[1:]):
            a, b = interpolate(left), interpolate(right)
            za, zb = elevation(a.x, a.y), elevation(b.x, b.y)
            if za is None or zb is None:
                gaps.append(dict(segment_index=segment_index, kind='terrain-void', from_m=left, to_m=right))
                continue
            grade = abs(zb - za) / (right - left) * 100
            terrain.append(dict(segment_index=segment_index, from_m=float(left), to_m=float(right),
                                status='reference-gradient-exceeded' if grade > gradient else 'reference-gradient-within-policy',
                                gradient_percent=grade,
                                gradient_basis='Unsurveyed DEM difference between provisional supports',
                                designed_rail_gradient_percent=None,
                                vertical_alignment_status='unresolved',
                                terrain_noise_attribution='unresolved: DEM roof/canopy/quantisation and ground slope not separated'))
            for chainage in np.linspace(left, right, max(2, math.ceil((right-left)/policy['terrain_sample_m']) + 1)):
                point = interpolate(chainage)
                ground = elevation(point.x, point.y)
                if ground is None:
                    gaps.append(dict(segment_index=segment_index, kind='terrain-void', from_m=float(chainage), to_m=float(chainage)))
                    continue
                soffit = za + (zb - za) * (chainage-left) / (right-left) + policy['reference_rail_height_m'] - policy['beam_depth_m']
                if ground >= soffit:
                    terrain.append(dict(segment_index=segment_index, chainage_m=float(chainage),
                                        status='beam-terrain-collision', ground_elevation_m=ground,
                                        reference_soffit_elevation_m=soffit))
    return dict(beam_building_checks=conflicts, reference_supports=supports,
                terrain_checks=terrain, unresolved=gaps, policy=policy, physical_release=False)
