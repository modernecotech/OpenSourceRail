"""Research geometry and exact section quantities; no catalogue promotion.

Regions are disjoint rectangles in transverse y / vertical z coordinates.
The same regions define CAD, section properties and solver input. Pier taper
uses explicit stepped segments, rather than claiming a smooth loft was built.
"""
from __future__ import annotations

import math

from osr_mech.cad import Box, Compound, Cylinder, Location
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


def deck_section(family: str, top_m=.16, bottom_m=.10, wall_m=.14, depth_m=None,
                 flange_width_m=.65, rib_count=3, rib_width_m=.18, *, diaphragm=False):
    width, depth = pi.DECK_WIDTH_MM/1000, pi.OVERALL_DEPTH_MM/1000
    depth = depth_m or depth
    if family not in ('pi', 'hollow-box', 'conventional-I', 'steel-composite-I', 'frp-composite-I', 'U-girder', 'ribbed-deck', 'uhpc-ribbed', 'hybrid-shell', 'segmental-box'):
        raise ValueError('unknown deck family')
    roles = []
    if diaphragm:
        regions = [rectangle(width, depth, z=depth/2)]
        shear_area = 5*width*depth/6
    elif family == 'pi':
        flange, stem, height = pi.FLANGE_THICKNESS_MM/1000, pi.STEM_WIDTH_MM/1000, pi.STEM_DEPTH_MM/1000
        regions = [rectangle(width, flange, z=height+flange/2)]
        regions += [rectangle(stem, height, y=side*pi.STEM_CENTRE_OFFSET_MM/1000, z=height/2) for side in (-1, 1)]
        shear_area = 5*2*stem*height/6
    elif family in ('hollow-box', 'hybrid-shell', 'segmental-box'):
        regions = hollow_regions(width, depth, top_m, bottom_m, wall_m)
        shear_area = 5*2*wall_m*(depth-top_m-bottom_m)/6
        roles = ['concrete']*4 if family != 'hybrid-shell' else ['concrete', 'frp', 'frp', 'frp']
    elif family in ('conventional-I', 'steel-composite-I', 'frp-composite-I'):
        if 2*flange_width_m >= 1.435 or top_m+bottom_m*2 >= depth:
            raise ValueError('conventional girders overlap or have no clear web')
        web_height = depth-top_m-2*bottom_m
        regions = [rectangle(width, top_m, z=depth-top_m/2)]
        for side in (-1., 1.):
            y = side*pi.STEM_CENTRE_OFFSET_MM/1000
            regions += [rectangle(flange_width_m, bottom_m, y, bottom_m/2),
                        rectangle(wall_m, web_height, y, bottom_m+web_height/2),
                        rectangle(flange_width_m, bottom_m, y, depth-top_m-bottom_m/2)]
        shear_area = 5*2*wall_m*web_height/6
        if family != 'conventional-I':
            roles = ['concrete']+['steel' if family == 'steel-composite-I' else 'frp']*6
    elif family == 'U-girder':
        if bottom_m >= depth or 2*wall_m >= width:
            raise ValueError('invalid U-girder clear opening')
        regions = [rectangle(width, bottom_m, z=bottom_m/2)]
        regions += [rectangle(wall_m, depth-bottom_m, side*(width-wall_m)/2, (depth+bottom_m)/2) for side in (-1., 1.)]
        shear_area = 5*2*wall_m*(depth-bottom_m)/6
    else:
        if type(rib_count) is not int or rib_count < 2 or rib_count*rib_width_m >= width or top_m >= depth:
            raise ValueError('invalid ribbed deck')
        regions = [rectangle(width, top_m, z=depth-top_m/2)]
        regions += [rectangle(rib_width_m, depth-top_m,
                              -width/2+rib_width_m/2+i*(width-rib_width_m)/(rib_count-1), (depth-top_m)/2)
                    for i in range(rib_count)]
        shear_area = 5*rib_count*rib_width_m*(depth-top_m)/6
        roles = ['concrete']+['uhpc']*rib_count if family == 'uhpc-ribbed' else []
    return dict(regions=regions, material_roles=roles or ['concrete']*len(regions),
                shear_area_m2=shear_area, **section_properties(regions))


def deck_segments(span_m: float, family: str, **parameters):
    if not 15 <= span_m <= 35:
        raise ValueError('research span outside 15–35 m envelope')
    end = pi.END_DIAPHRAGM_LENGTH_MM/1000
    return [dict(start_m=a, end_m=b, **deck_section(family, **parameters, diaphragm=d))
            for a, b, d in ((0., end, True), (end, span_m-end, False), (span_m-end, span_m, True))]


def pier_segments(family: str, height_m: float, wall_m=.25, top_scale=.85, count=8,
                  width_m=None, depth_m=None, skin_m=.012):
    if family not in ('solid', 'hollow-tapered', 'solid-tapered', 'hollow-prismatic', 'segmental-hollow', 'double-skin-hybrid') or not 5 <= height_m <= 12:
        raise ValueError('unsupported pier family/height')
    if type(count) is not int or not 2 <= count <= 64 or not .5 <= top_scale <= 1:
        raise ValueError('invalid taper discretisation')
    result = []
    for i in range(count):
        scale = 1. if family in ('solid', 'hollow-prismatic') else 1-(1-top_scale)*(i+.5)/count
        longitudinal = (depth_m or sub.PIER_COLUMN_X_MM/1000)*scale
        transverse = (width_m or sub.PIER_COLUMN_Y_MM/1000)*scale
        roles = None
        if family in ('solid', 'solid-tapered'):
            regions = [rectangle(transverse, longitudinal, z=longitudinal/2)]
        elif family == 'double-skin-hybrid':
            if not 0 < 2*skin_m < wall_m:
                raise ValueError('hybrid skins must leave a concrete core')
            regions = []; roles = []
            for inset, thickness, material in ((0.,skin_m,'frp'), (skin_m,wall_m-2*skin_m,'concrete'), (wall_m-skin_m,skin_m,'frp')):
                layer = hollow_regions(transverse-2*inset, longitudinal-2*inset, thickness, thickness, thickness)
                for r in layer:r['z_m']+=inset
                regions.extend(layer);roles.extend([material]*len(layer))
        else:
            regions = hollow_regions(transverse, longitudinal, wall_m, wall_m, wall_m)
        properties = section_properties(regions)
        result.append(dict(start_m=i*height_m/count, end_m=(i+1)*height_m/count,
                           regions=regions, shear_area_m2=5*properties['area_m2']/6, **properties))
        if roles is not None:result[-1]['material_roles']=roles
    return result


def geometry(definition: dict) -> dict:
    """Canonical geometry adapter consumed by takeoff, CAD and analysis."""
    deck, pier = definition['deck'], definition['pier']
    allowed={'pi':set(),'hollow-box':{'top_m','bottom_m','wall_m','depth_m'},
             'hybrid-shell':{'top_m','bottom_m','wall_m','depth_m'},'segmental-box':{'top_m','bottom_m','wall_m','depth_m'},
             'conventional-I':{'top_m','bottom_m','wall_m','depth_m','flange_width_m'},
             'steel-composite-I':{'top_m','bottom_m','wall_m','depth_m','flange_width_m'},
             'frp-composite-I':{'top_m','bottom_m','wall_m','depth_m','flange_width_m'},
             'U-girder':{'bottom_m','wall_m','depth_m'},
             'ribbed-deck':{'top_m','depth_m','rib_count','rib_width_m'},'uhpc-ribbed':{'top_m','depth_m','rib_count','rib_width_m'}}
    if deck['family'] not in allowed or set(deck['parameters'])-allowed[deck['family']]:
        raise ValueError('unknown or ignored family parameters')
    if pier['family']=='solid' and pier['parameters']:
        raise ValueError('solid pier parameters cannot be overridden')
    pier_allowed={'solid':set(),'hollow-tapered':{'wall_m','top_scale','count'},
                  'solid-tapered':{'top_scale','count','width_m','depth_m'},
                  'hollow-prismatic':{'wall_m','count','width_m','depth_m'},
                  'segmental-hollow':{'wall_m','top_scale','count','width_m','depth_m'},
                  'double-skin-hybrid':{'wall_m','top_scale','count','width_m','depth_m','skin_m'}}
    if pier['family'] not in pier_allowed or set(pier['parameters'])-pier_allowed[pier['family']]:
        raise ValueError('unknown or ignored pier parameters')
    return dict(deck=deck_segments(deck['span_m'], deck['family'], **deck['parameters']),
                pier=pier_segments(pier['family'], pier['height_m'], **pier['parameters']),
                cap_concrete_m3=(sub.PIER_CAP_X_MM*sub.PIER_CAP_Y_MM*sub.PIER_CAP_HEIGHT_MM-2000*6500*800)/1e9,
                cap_height_m=sub.PIER_CAP_HEIGHT_MM/1000,
                cap_width_m=sub.PIER_CAP_Y_MM/1000,
                track_centres_m=[-sub.GIRDER_CENTRE_SPACING_MM/2000, sub.GIRDER_CENTRE_SPACING_MM/2000],
                geometry_maturity='research-envelope', smooth_pier_taper=False)


def foundation_geometry(parameters: dict) -> dict:
    """Common authoritative pile-group geometry for takeoff, CAD and BIM."""
    count, diameter = parameters['pile_count'], parameters['pile_diameter_m']
    length, width = parameters['cap_length_m'], parameters['cap_width_m']
    kind=parameters.get('type','pile-group');shape=parameters.get('pile_shape','round');inner=parameters.get('pile_inner_diameter_m',0.)
    if kind not in ('pile-group','single-shaft','spread') or shape not in ('round','square'):
        raise ValueError('unknown foundation type or pile shape')
    if kind=='spread':
        if count!=0 or diameter!=0 or parameters['pile_length_m']!=0 or inner!=0:
            raise ValueError('spread footing cannot retain fictitious piles')
        return dict(piles=[],cap_dimensions_m=[length,width,parameters['cap_depth_m']],
                    cap_concrete_m3=length*width*parameters['cap_depth_m'],pile_concrete_m3=0.,layout_basis='research spread footing; site bearing/settlement qualification required')
    if type(count) is not int or count<1 or (kind=='single-shaft' and count!=1) or not 0<=inner<diameter or (shape=='square' and inner):
        raise ValueError('invalid foundation count or hollow pile section')
    nx = math.ceil(math.sqrt(count)); ny = math.ceil(count/nx)
    if min(length, width) <= diameter or (nx > 1 and length/nx <= diameter) or (ny > 1 and width/ny <= diameter):
        raise ValueError('pile arrangement does not fit the cap')
    centres = [[(i % nx+.5)*length/nx-length/2, (i//nx+.5)*width/ny-width/2] for i in range(count)]
    pile_area=(diameter**2 if shape=='square' else math.pi*(diameter**2-inner**2)/4)
    pile_volume = pile_area*parameters['pile_length_m']
    piles=[dict(id=f'pile-{i+1}', centre_xy_m=xy, diameter_m=diameter,
                length_m=parameters['pile_length_m'], concrete_m3=pile_volume) for i, xy in enumerate(centres)]
    if shape!='round' or inner:
        for p in piles:p.update(shape=shape,inner_diameter_m=inner)
    return dict(piles=piles,
                cap_dimensions_m=[length, width, parameters['cap_depth_m']],
                cap_concrete_m3=length*width*parameters['cap_depth_m'], pile_concrete_m3=count*pile_volume,
                layout_basis='illustrative regular grid; not a site or reinforcement design')


def assembly_parts(definition, foundation, route_length_m):
    """Whole corridor solids in metres, with stable product/type identifiers."""
    geo = geometry(definition); f = foundation_geometry(foundation)
    span = definition['deck']['span_m']; bays = round(route_length_m/span)
    height = definition['pier']['height_m']; parts = []
    def box(identifier, kind, dimensions, centre, material='concrete'):
        parts.append(dict(id=identifier, kind=kind, material=material, shape='box', dimensions_m=dimensions, centre_m=centre))
    for bay in range(bays):
        for track, track_y in enumerate(geo['track_centres_m'], 1):
            for j, segment in enumerate(geo['deck']):
                for k, r in enumerate(segment['regions']):
                    box(f'B{bay}-T{track}-S{j}-R{k}', 'deck',
                        [segment['end_m']-segment['start_m'], r['width_m'], r['height_m']],
                        [bay*span+(segment['start_m']+segment['end_m'])/2, track_y+r['y_m'], height+geo['cap_height_m']+r['z_m']],
                        segment['material_roles'][k])
    for support in range(bays+1):
        x = support*span
        for j, s in enumerate(geo['pier']):
            for k, r in enumerate(s['regions']):
                box(f'S{support}-P{j}-R{k}', 'pier', [r['height_m'], r['width_m'], s['end_m']-s['start_m']],
                    [x+r['z_m']-s['centroid_z_m'], r['y_m'], (s['end_m']+s['start_m'])/2],
                    s.get('material_roles',['concrete']*len(s['regions']))[k])
        # Disjoint cap shell plates reproduce the existing hollow cap net volume.
        for j, (dims, centre) in enumerate([
            ([2.5, 7., .2], [x, 0., height+.1]), ([2.5, 7., .2], [x, 0., height+1.1]),
            ([.25, 7., .8], [x-1.125, 0., height+.6]), ([.25, 7., .8], [x+1.125, 0., height+.6]),
            ([2., .25, .8], [x, -3.375, height+.6]), ([2., .25, .8], [x, 3.375, height+.6])]):
            box(f'S{support}-CAP{j}', 'cap', dims, centre)
        box(f'S{support}-FOUND-CAP', 'foundation', f['cap_dimensions_m'], [x, 0., -foundation['cap_depth_m']/2])
        for pile in f['piles']:
            centre=[x+pile['centre_xy_m'][0],pile['centre_xy_m'][1],-foundation['cap_depth_m']-pile['length_m']/2]
            if pile.get('shape')=='square':
                box(f'S{support}-{pile["id"]}','pile',[pile['diameter_m'],pile['diameter_m'],pile['length_m']],centre)
            else:
                description=dict(id=f'S{support}-{pile["id"]}',kind='pile',material='concrete',shape='cylinder',diameter_m=pile['diameter_m'],length_m=pile['length_m'],centre_m=centre)
                if pile.get('inner_diameter_m'):description.update(shape='annulus',inner_diameter_m=pile['inner_diameter_m'])
                parts.append(description)
    return parts


def assembly_cad(definition, foundation, route_length_m):
    parts = []
    for description in assembly_parts(definition, foundation, route_length_m):
        if description['shape'] == 'box':
            part = Box(*[1000*v for v in description['dimensions_m']])
        else:
            part = Cylinder(description['diameter_m']*500, description['length_m']*1000)
            if description['shape']=='annulus':part=part-Cylinder(description['inner_diameter_m']*500,description['length_m']*1000)
        part = part.locate(Location([1000*v for v in description['centre_m']]))
        part.label = description['id']; parts.append(part)
    return Compound(label='Unreleased complete civil research assembly', children=parts)


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
    upper=section['top_m']+.3;height=upper+.6
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.8 {-upper:.8g} 3.6 {height:.8g}">',
             '<title>Research midspan material section; capacity unresolved</title>',
             f'<rect x="-1.8" y="{-upper:.8g}" width="3.6" height="{height:.8g}" fill="white"/>']
    for r in section['regions']:
        parts.append(f'<rect x="{r["y_m"]-r["width_m"]/2:.8g}" y="{-r["z_m"]-r["height_m"]/2:.8g}" '
                     f'width="{r["width_m"]:.8g}" height="{r["height_m"]:.8g}" fill="#59859e" stroke="#25475a" stroke-width="0.008"/>')
    parts.append(f'<text x="0" y="0.25" text-anchor="middle" font-size="0.11" fill="#25475a">'
                 f'Area {section["area_m2"]:.4f} m² · I {section["inertia_y_m4"]:.5f} m⁴</text>')
    parts.append('<text x="0" y="0.43" text-anchor="middle" font-size="0.09">Research geometry · no structural approval</text></svg>')
    return '\n'.join(parts)+'\n'
