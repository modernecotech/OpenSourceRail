"""Research geometry and exact section quantities; no catalogue promotion.

Regions are disjoint rectangles in transverse y / vertical z coordinates.
The same regions define CAD, section properties and solver input. Pier taper
uses explicit stepped segments, rather than claiming a smooth loft was built.
"""
from __future__ import annotations

import math

from osr_mech.cad import Box, Compound, Location
from . import decked_pi as pi, substructure as sub


def section_properties(regions: list[dict]) -> dict:
    if not regions:
        raise ValueError("section has no material")
    for i, r in enumerate(regions):
        if set(r) != {"width_m", "height_m", "y_m", "z_m"}:
            raise ValueError("unknown section region field")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in r.values()):
            raise ValueError("section measurements must be finite")
        if min(r['width_m'], r['height_m']) <= 0:
            raise ValueError("section dimensions must be positive")
        for other in regions[:i]:
            if (abs(r['y_m']-other['y_m'])*2 < r['width_m']+other['width_m']-1e-12
                    and abs(r['z_m']-other['z_m'])*2 < r['height_m']+other['height_m']-1e-12):
                raise ValueError("overlapping section material")
    areas = [r['width_m']*r['height_m'] for r in regions]
    area = math.fsum(areas)
    y = math.fsum(a*r['y_m'] for a, r in zip(areas, regions))/area
    z = math.fsum(a*r['z_m'] for a, r in zip(areas, regions))/area
    return dict(area_m2=area, centroid_y_m=y, centroid_z_m=z,
                inertia_y_m4=math.fsum(a*(r['height_m']**2/12+(r['z_m']-z)**2) for a, r in zip(areas, regions)),
                inertia_z_m4=math.fsum(a*(r['width_m']**2/12+(r['y_m']-y)**2) for a, r in zip(areas, regions)),
                bottom_m=min(r['z_m']-r['height_m']/2 for r in regions),
                top_m=max(r['z_m']+r['height_m']/2 for r in regions))


def rectangle(width, height, y=0., z=0.):
    return dict(width_m=width, height_m=height, y_m=y, z_m=z)


def hollow_regions(width, depth, top, bottom, wall):
    if min(width, depth, top, bottom, wall) <= 0 or 2*wall >= width or top+bottom >= depth:
        raise ValueError("hollow section has no clear internal void")
    clear = depth-top-bottom
    return [rectangle(width, top, z=depth-top/2), rectangle(width, bottom, z=bottom/2),
            rectangle(wall, clear, y=-(width-wall)/2, z=bottom+clear/2),
            rectangle(wall, clear, y=(width-wall)/2, z=bottom+clear/2)]


def deck_section(family: str, top_m=.16, bottom_m=.10, wall_m=.14, *, diaphragm=False):
    width, depth = pi.DECK_WIDTH_MM/1000, pi.OVERALL_DEPTH_MM/1000
    if family not in ('pi', 'hollow-box'):
        raise ValueError('unknown deck family')
    if diaphragm:
        regions = [rectangle(width, depth, z=depth/2)]
        shear_area = 5*width*depth/6
    elif family == 'pi':
        flange, stem, height = pi.FLANGE_THICKNESS_MM/1000, pi.STEM_WIDTH_MM/1000, pi.STEM_DEPTH_MM/1000
        regions = [rectangle(width, flange, z=height+flange/2)]
        regions += [rectangle(stem, height, y=side*pi.STEM_CENTRE_OFFSET_MM/1000, z=height/2) for side in (-1, 1)]
        shear_area = 5*2*stem*height/6
    else:
        regions = hollow_regions(width, depth, top_m, bottom_m, wall_m)
        shear_area = 5*2*wall_m*(depth-top_m-bottom_m)/6
    return dict(regions=regions, shear_area_m2=shear_area, **section_properties(regions))


def deck_segments(span_m: float, family: str, **parameters):
    if not 15 <= span_m <= 35:
        raise ValueError('research span outside 15–35 m envelope')
    end = pi.END_DIAPHRAGM_LENGTH_MM/1000
    return [dict(start_m=a, end_m=b, **deck_section(family, **parameters, diaphragm=d))
            for a, b, d in ((0., end, True), (end, span_m-end, False), (span_m-end, span_m, True))]


def pier_segments(family: str, height_m: float, wall_m=.25, top_scale=.85, count=8):
    if family not in ('solid', 'hollow-tapered') or not 5 <= height_m <= 12:
        raise ValueError('unsupported pier family/height')
    if type(count) is not int or not 2 <= count <= 64 or not .5 <= top_scale <= 1:
        raise ValueError('invalid taper discretisation')
    result = []
    for i in range(count):
        scale = 1. if family == 'solid' else 1-(1-top_scale)*(i+.5)/count
        longitudinal = sub.PIER_COLUMN_X_MM/1000*scale
        transverse = sub.PIER_COLUMN_Y_MM/1000*scale
        regions = ([rectangle(transverse, longitudinal, z=longitudinal/2)] if family == 'solid'
                   else hollow_regions(transverse, longitudinal, wall_m, wall_m, wall_m))
        properties = section_properties(regions)
        result.append(dict(start_m=i*height_m/count, end_m=(i+1)*height_m/count,
                           regions=regions, shear_area_m2=5*properties['area_m2']/6, **properties))
    return result


def geometry(definition: dict) -> dict:
    """Canonical geometry adapter consumed by takeoff, CAD and analysis."""
    deck, pier = definition['deck'], definition['pier']
    return dict(deck=deck_segments(deck['span_m'], deck['family'], **deck['parameters']),
                pier=pier_segments(pier['family'], pier['height_m'], **pier['parameters']),
                cap_concrete_m3=(sub.PIER_CAP_X_MM*sub.PIER_CAP_Y_MM*sub.PIER_CAP_HEIGHT_MM-2000*6500*800)/1e9,
                cap_height_m=sub.PIER_CAP_HEIGHT_MM/1000,
                cap_width_m=sub.PIER_CAP_Y_MM/1000,
                track_centres_m=[-sub.GIRDER_CENTRE_SPACING_MM/2000, sub.GIRDER_CENTRE_SPACING_MM/2000],
                geometry_maturity='research-envelope', smooth_pier_taper=False)


def deck_cad(definition: dict) -> Compound:
    parts = []
    for segment in geometry(definition)['deck']:
        for region in segment['regions']:
            part = Box((segment['end_m']-segment['start_m'])*1000, region['width_m']*1000, region['height_m']*1000)
            part = part.locate(Location(((segment['start_m']+segment['end_m'])*500, region['y_m']*1000, region['z_m']*1000)))
            part.label = 'Research deck concrete region'
            parts.append(part)
    return Compound(label='Unreleased research deck', children=parts)


def section_svg(definition: dict) -> str:
    """Review diagram of the actual midspan material regions, not a stress plot."""
    section = geometry(definition)['deck'][1]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.8 -1.5 3.6 2.1">',
             '<title>Research midspan material section; capacity unresolved</title>',
             '<rect x="-1.8" y="-1.5" width="3.6" height="2.1" fill="white"/>']
    for r in section['regions']:
        parts.append(f'<rect x="{r["y_m"]-r["width_m"]/2:.8g}" y="{-r["z_m"]-r["height_m"]/2:.8g}" '
                     f'width="{r["width_m"]:.8g}" height="{r["height_m"]:.8g}" fill="#59859e" stroke="#25475a" stroke-width="0.008"/>')
    parts.append(f'<text x="0" y="0.25" text-anchor="middle" font-size="0.11" fill="#25475a">'
                 f'Area {section["area_m2"]:.4f} m² · I {section["inertia_y_m4"]:.5f} m⁴</text>')
    parts.append('<text x="0" y="0.43" text-anchor="middle" font-size="0.09">Research geometry · no structural approval</text></svg>')
    return '\n'.join(parts)+'\n'
