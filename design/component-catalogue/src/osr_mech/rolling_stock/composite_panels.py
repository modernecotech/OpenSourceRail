"""Development-only hybrid panel mechanics, quantities and real layer geometry.

SI units throughout. One-way, simply supported pressure strips deliberately
give no membrane/curvature/rib credit. Strength, fatigue, debonding, thermal
allowables and rail qualification require material and assembly evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from osr_mech.provenance import stable_sum as sum


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return float(value)


def inverse3(matrix):
    work = [list(row) + [float(i == j) for j in range(3)] for i, row in enumerate(matrix)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(work[i][col]))
        work[col], work[pivot] = work[pivot], work[col]
        divisor = work[col][col]
        if abs(divisor) < 1e-15:
            raise ValueError('singular laminate stiffness')
        work[col] = [v / divisor for v in work[col]]
        for row in range(3):
            if row != col:
                factor = work[row][col]
                work[row] = [a - factor*b for a, b in zip(work[row], work[col])]
    return [row[3:] for row in work]


def transformed_q(material, angle):
    e1, e2, g = [positive(material[k], k) for k in ('e1_pa', 'e2_pa', 'g12_pa')]
    nu = material['poisson12']
    if not math.isfinite(nu) or not 0 <= nu < 0.5:
        raise ValueError('poisson12 must be in [0, 0.5)')
    denominator = 1 - nu*nu*e2/e1
    if denominator <= 0:
        raise ValueError('non-positive orthotropic stiffness')
    q11, q22, q12 = e1/denominator, e2/denominator, nu*e2/denominator
    m, n = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    a = q11*m**4 + 2*(q12+2*g)*m*m*n*n + q22*n**4
    b = q11*n**4 + 2*(q12+2*g)*m*m*n*n + q22*m**4
    c = (q11+q22-4*g)*m*m*n*n + q12*(m**4+n**4)
    d = (q11+q22-2*q12-2*g)*m*m*n*n + g*(m**4+n**4)
    e = (q11-q12-2*g)*m**3*n - (q22-q12-2*g)*m*n**3
    f = (q11-q12-2*g)*m*n**3 - (q22-q12-2*g)*m**3*n
    return [[a, c, e], [c, b, f], [e, f, d]]


@dataclass(frozen=True)
class Ply:
    thickness_m: float
    angle_deg: float

    def __post_init__(self):
        positive(self.thickness_m, 'ply thickness')
        if not math.isfinite(self.angle_deg):
            raise ValueError('non-finite fibre angle')


def balanced_skin(thickness):
    positive(thickness, 'skin thickness')
    return tuple(Ply(thickness/8, angle) for angle in (0, 45, -45, 90, 90, -45, 45, 0))


def laminate_abd(plies, core_depth, bond_depth, glass):
    """Face-ply ABD; core/bond extensional stiffness not credited."""
    positive(core_depth, 'core depth'); positive(bond_depth, 'bond depth')
    if not plies:
        raise ValueError('empty ply schedule')
    skin = sum(p.thickness_m for p in plies)
    depth = 2*skin + core_depth + 2*bond_depth
    layers = []
    z = -depth/2
    for ply in plies:
        layers.append((z, z+ply.thickness_m, transformed_q(glass, ply.angle_deg)))
        z += ply.thickness_m
    z += core_depth + 2*bond_depth
    for ply in reversed(plies):
        layers.append((z, z+ply.thickness_m, transformed_q(glass, ply.angle_deg)))
        z += ply.thickness_m
    matrices = [[[0.0]*3 for _ in range(3)] for _ in range(3)]
    for lower, upper, q in layers:
        for order, matrix in enumerate(matrices, start=1):
            for i in range(3):
                for j in range(3):
                    matrix[i][j] += q[i][j]*(upper**order-lower**order)/order
    return dict(A=matrices[0], B=matrices[1], D=matrices[2], thickness_m=depth)


def strip_response(abd, pressure, span, core_depth, core_shear, *, stiffness_factor=1, shear_factor=1):
    positive(pressure, 'pressure'); positive(span, 'span'); positive(core_shear, 'core shear')
    for value in (stiffness_factor, shear_factor):
        if not math.isfinite(value) or not 0 < value <= 1:
            raise ValueError('sensitivity factors must be in (0, 1]')
    ai = inverse3(abd['A'])
    effective = [[abd['D'][i][j]-sum(abd['B'][k][i]*ai[k][l]*abd['B'][l][j]
                 for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    # Unit-width uncoupled bending compliance in the longitudinal direction.
    stiffness = 1/inverse3(effective)[0][0]*stiffness_factor
    bending = 5*pressure*span**4/(384*stiffness)
    shear = pressure*span**2/(8*core_shear*core_depth*shear_factor)
    return dict(bending_stiffness_nm=stiffness, bending_deflection_m=bending,
                shear_deflection_m=shear, total_deflection_m=bending+shear,
                maximum_core_shear_stress_pa=pressure*span/(2*core_depth),
                small_deflection_screen=(bending+shear)/span <= 0.01,
                strength_passed=None, fatigue_passed=None, debonding_passed=None)


def fatigue_sensitivity(stress_range_pa, cycles, sn_curve):
    """Single-range Miner damage only with a named measured S-N input."""
    positive(stress_range_pa, 'stress range'); positive(cycles, 'cycle count')
    if sn_curve is None:
        return dict(damage=None,life_cycles=None,qualified=False)
    if not sn_curve.get('measured_evidence_sha256') or len(sn_curve['measured_evidence_sha256']) != 64:
        raise ValueError('A measured S-N curve evidence hash is required')
    reference=positive(sn_curve['reference_stress_range_pa'],'S-N stress')
    count=positive(sn_curve['reference_cycles'],'S-N cycles');slope=positive(sn_curve['slope'],'S-N slope')
    life=count*(reference/stress_range_pa)**slope
    return dict(damage=cycles/life,life_cycles=life,qualified=False,
                limitations='Constant-range sensitivity; joint effects, spectrum, mean stress and scatter unresolved')


def rib_quantities(length_m, depth_m, wall_m, crown_width_m, count, density):
    """Open hat rib: crown plus two webs; no joint/load-path stiffness credit."""
    positive(length_m,'rib length');positive(wall_m,'rib wall');positive(crown_width_m,'rib crown');positive(density,'rib density')
    if not math.isfinite(depth_m) or depth_m < 0 or isinstance(count,bool) or not isinstance(count,int) or count<0:
        raise ValueError('invalid rib definition')
    volume=0 if depth_m==0 else count*length_m*wall_m*(crown_width_m+2*depth_m)
    return dict(volume_m3=volume,mass_kg=volume*density,stiffness_credit=0,
                bond_line_qualified=False,tooling_cost_usd=None)


def remaining_rectangles(width, height, holes=()):
    """Exact disjoint rectangular partition, including aperture overlaps."""
    positive(width, 'width'); positive(height, 'height')
    clipped = []
    for x0, y0, x1, y1 in holes:
        if not all(math.isfinite(v) for v in (x0, y0, x1, y1)) or x1 <= x0 or y1 <= y0:
            raise ValueError('invalid aperture rectangle')
        a, b, c, d = max(0, x0), max(0, y0), min(width, x1), min(height, y1)
        if c > a and d > b:
            clipped.append((a, b, c, d))
    xs = sorted({0, width, *(v for h in clipped for v in (h[0], h[2]))})
    ys = sorted({0, height, *(v for h in clipped for v in (h[1], h[3]))})
    return [(x0, y0, x1, y1) for x0, x1 in zip(xs, xs[1:]) for y0, y1 in zip(ys, ys[1:])
            if not any(a < (x0+x1)/2 < c and b < (y0+y1)/2 < d for a, b, c, d in clipped)]


def area(rectangles):
    return sum((c-a)*(d-b) for a, b, c, d in rectangles)


def perimeter(rectangles):
    """Union boundary: subtract common edges, never count grid partitions."""
    total = sum(2*((c-a)+(d-b)) for a, b, c, d in rectangles)
    for i, (a, b, c, d) in enumerate(rectangles):
        for e, f, g, h in rectangles[i+1:]:
            if math.isclose(c, e, abs_tol=1e-12) or math.isclose(a, g, abs_tol=1e-12):
                total -= 2*max(0, min(d, h)-max(b, f))
            if math.isclose(d, f, abs_tol=1e-12) or math.isclose(b, h, abs_tol=1e-12):
                total -= 2*max(0, min(c, g)-max(a, e))
    return total


def roof_arc(chord, crown):
    positive(chord, 'roof chord')
    if not math.isfinite(crown) or not 0 <= crown < chord/2:
        raise ValueError('crown must be in [0, chord/2)')
    if crown == 0:
        return dict(radius_m=None, arc_length_m=chord, angle_rad=0)
    radius = chord*chord/(8*crown)+crown/2
    angle = 2*math.asin(chord/(2*radius))
    return dict(radius_m=radius, arc_length_m=radius*angle, angle_rad=angle)


def panel_quantities(config, width, height, skin, core, *, holes=(), crown=0, insert_count=None):
    """Skin/core/solid lands, potting, hardware and finish; actual cut area."""
    positive(skin, 'skin thickness'); positive(core, 'core depth')
    for group in ('glass', 'core', 'bond', 'finish'):
        positive(config[group]['density_kg_m3'], group+' density')
    for group in ('glass', 'core', 'bond'):
        positive(config[group]['thermal_conductivity_w_mk'], group+' thermal conductivity')
    p = config['panel']; arc = roof_arc(height, crown)
    if crown and holes:
        raise ValueError('curved apertures require a surveyed developed-coordinate trim map')
    developed = arc['arc_length_m']
    cells = remaining_rectangles(width, developed, holes)
    a = area(cells)
    land = positive(p['edge_land_m'], 'edge land')
    if 2*land >= min(width, developed):
        raise ValueError('edge lands consume the panel')
    # Solid laminate around both the outer boundary and cut apertures.
    foam_holes = [(x0-land, y0-land, x1+land, y1+land) for x0, y0, x1, y1 in holes]
    foam_holes += [(0, 0, width, land), (0, developed-land, width, developed),
                   (0, 0, land, developed), (width-land, 0, width, developed)]
    foam_a = area(remaining_rectangles(width, developed, foam_holes))
    count = p['insert_count'] if insert_count is None else insert_count
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError('insert count must be a nonnegative integer')
    r, ri = p['potting_radius_m'], p['insert_radius_m']
    if not 0 < ri < r or count*math.pi*r*r >= foam_a:
        raise ValueError('potting dimensions exceed available foam')
    # Actual insert placement is separately verified by the CAD builder.
    foam_volume = (foam_a-count*math.pi*r*r)*core
    masses = dict(glass=2*skin*a*config['glass']['density_kg_m3'] + (a-foam_a)*core*config['glass']['density_kg_m3'],
                  core=foam_volume*config['core']['density_kg_m3'],
                  bond=2*config['bond']['thickness_m_each']*a*config['bond']['density_kg_m3'],
                  finish=config['finish']['thickness_m']*a*config['finish']['density_kg_m3'],
                  potting=count*math.pi*(r*r-ri*ri)*core*config['hardware']['potting_density_kg_m3'],
                  insert=count*math.pi*ri*ri*core*config['hardware']['insert_density_kg_m3'])
    hardware = config['hardware']; length = perimeter(cells)
    # Crown is not a stiffness credit. Radial thin layers are integrated about
    # the mid-surface; symmetrical skins have exactly the same total volume.
    if arc['radius_m']:
        total_depth = 2*skin+core+2*config['bond']['thickness_m_each']
        masses['finish'] *= 1+(total_depth/2+config['finish']['thickness_m']/2)/arc['radius_m']
    masses.update(clips=count*hardware['clip_mass_kg_each'], retainer=hardware['retainer_mass_kg'],
                  seal=length*hardware['seal_mass_kg_per_m'])
    costs = config['unit_costs_usd']; missing = [k for k, v in costs.items() if v is None]
    for value in [*masses.values(), *[v for v in costs.values() if v is not None]]:
        if not math.isfinite(value) or value < 0:
            raise ValueError('negative/nonfinite quantity or cost')
    cost = None if missing else (sum(masses[k]*costs[k+'_per_kg'] for k in ('glass','core','bond','finish','potting','insert'))
            + count*costs['clip_each']+costs['retainer_each']+length*costs['seal_per_m']
            + sum(costs[k] for k in ('labour_per_panel','tooling_amortisation_per_panel','qualification_amortisation_per_panel','rejects_per_panel')))
    r_foam = 2*skin/config['glass']['thermal_conductivity_w_mk']+core/config['core']['thermal_conductivity_w_mk']+2*config['bond']['thickness_m_each']/config['bond']['thermal_conductivity_w_mk']
    r_land = (2*skin+core)/config['glass']['thermal_conductivity_w_mk']+2*config['bond']['thickness_m_each']/config['bond']['thermal_conductivity_w_mk']
    return dict(panel_area_m2=a, foam_area_m2=foam_a, solid_land_area_m2=a-foam_a,
                mass_kg=masses, installed_mass_kg=sum(masses.values()), seal_length_m=length,
                thermal_resistance_m2k_w=a/(foam_a/r_foam+(a-foam_a)/r_land) if a else None,
                thermal_boundary_basis='Parallel core/solid-edge conduction; metal fastener bridges, convection and PV radiation unresolved',
                roof_geometry=arc, cost_usd=cost, missing_cost_inputs=missing,
                structural_frame_mass_excluded=True, equipment_loads_to_frame=True,
                qualified=False)


def cad_layers(config, *, width, height, skin, core, crown=0, holes=(), insert_sites=None):
    """Native exact circular roof layers or flat layered side coupon/module.

    Apertures cut every layer and generate solid perimeter lands.
    Flat insert sites cut foam; curved local mounting lands remain open.
    """
    from osr_mech import cad
    arc = roof_arc(height, crown); developed = arc['arc_length_m']
    p = config['panel']; land = p['edge_land_m']
    bond = config['bond']['thickness_m_each']; depth = 2*skin+core+2*bond
    if crown and depth/2 >= arc['radius_m']:
        raise ValueError('layer thickness exceeds roof radius')
    parts=[]
    def layer(name, rect, z0, z1, color):
        x0,y0,x1,y1=rect; shape=None
        if cad.FreeCADPart is not None:
            if not crown:
                shape=cad.FreeCADPart.makeBox((x1-x0)*1000,(y1-y0)*1000,(z1-z0)*1000)
                shape.translate(cad.App.Vector(x0*1000,y0*1000,z0*1000))
            else:
                radius=arc['radius_m']; mid=developed/2
                def point(s,z):
                    theta=(s-mid)/radius
                    return cad.App.Vector(x0*1000,(radius+z)*math.sin(theta)*1000,((radius+z)*math.cos(theta)-radius+crown)*1000)
                inner=cad.FreeCADPart.Arc(point(y0,z0),point((y0+y1)/2,z0),point(y1,z0)).toShape()
                outer=cad.FreeCADPart.Arc(point(y1,z1),point((y0+y1)/2,z1),point(y0,z1)).toShape()
                edges=[inner,cad.FreeCADPart.makeLine(point(y1,z0),point(y1,z1)),outer,cad.FreeCADPart.makeLine(point(y0,z1),point(y0,z0))]
                shape=cad.FreeCADPart.Face(cad.FreeCADPart.Wire(edges)).extrude(cad.App.Vector((x1-x0)*1000,0,0))
        factor=1+(z0+z1)/2/arc['radius_m'] if crown else 1
        obj=cad.Part(shape,volume=(x1-x0)*(y1-y0)*(z1-z0)*factor*1e9,label=name,color=color)
        if shape is None:
            obj._bbox=cad._BoundingBox(cad._Point(x0*1000,y0*1000,z0*1000),cad._Point(x1*1000,y1*1000,(z1+crown)*1000))
        parts.append(obj); return obj
    rect=(0,0,width,developed); z=-depth/2
    for side in ('inner','outer'):
        if side=='outer': z=core/2+bond
        for i,ply in enumerate(balanced_skin(skin)):
            layer(f'{side} GFRP ply {i+1} {ply.angle_deg:g} degrees',rect,z,z+ply.thickness_m,cad.Color(.8,.9,.75));z+=ply.thickness_m
    for lower in (-core/2-bond,core/2):
        layer('skin/core adhesive',rect,lower,lower+bond,cad.Color(.7,.5,.2))
    edges=[(0,0,width,land),(0,developed-land,width,developed),(0,land,land,developed-land),(width-land,land,width,developed-land)]
    if holes:
        excluded=edges+[(a-land,b-land,c+land,d+land)for a,b,c,d in holes]
        foam_rects=remaining_rectangles(width,developed,excluded)
        old_count=len(parts)
        foam_parts=[layer('foam core region',rect,-core/2,core/2,cad.Color(.95,.85,.45))for rect in foam_rects]
        del parts[old_count:]
        foam=cad.Compound(children=foam_parts,label='trimmed foam core');parts.append(foam)
        for region in remaining_rectangles(width,developed,foam_rects):
            layer('reinforced GFRP edge/aperture land',region,-core/2,core/2,cad.Color(.2,.6,.5))
    else:
        foam=layer('foam core',(land,land,width-land,developed-land),-core/2,core/2,cad.Color(.95,.85,.45))
        for region in edges:
            layer('reinforced solid GFRP edge land',region,-core/2,core/2,cad.Color(.2,.6,.5))
    # Flat modules resolve cylindrical potting explicitly. Curved blank modules
    # retain the insert map for dedicated local flat mounting-land development.
    if not crown:
        r,ri=p['potting_radius_m'],p['insert_radius_m']
        sites=insert_sites if insert_sites is not None else [(width*.2,developed*.2),(width*.8,developed*.2),(width*.2,developed*.8),(width*.8,developed*.8)]
        for x,y in sites:
            if min(x,width-x,y,developed-y) <= land+r:
                raise ValueError('insert outside foam land')
            if any(a-land-r<x<c+land+r and b-land-r<y<d+land+r for a,b,c,d in holes):raise ValueError('insert intersects an aperture or its reinforced land')
            cylinder=cad.Cylinder(r*1000,core*1000).translate((x*1000,y*1000,0))
            insert=cad.Cylinder(ri*1000,core*1000).translate((x*1000,y*1000,0))
            cut=foam-cylinder; foam._shape=cut._shape;foam._volume=cut._volume
            pot=cylinder-insert;pot.label='potted insert annulus';pot.color=cad.Color(.6,.3,.2);parts.append(pot)
            insert.label='metal insert, load into frame clip';insert.color=cad.Color(.5,.5,.5);parts.append(insert)
    layer('outer finish',rect,depth/2,depth/2+config['finish']['thickness_m'],cad.Color(.9,.9,.9))
    if holes:
        if any(x0<0 or y0<0 or x1>width or y1>developed for x0,y0,x1,y1 in holes):raise ValueError('trim aperture outside panel')
        cutters=[]
        for rect in holes:
            before=len(parts)
            cutter=layer('aperture tooling solid',rect,-depth/2-.01,depth/2+config['finish']['thickness_m']+.01,cad.Color(1,0,0))
            del parts[before:]
            cutters.append(cutter)
        trimmed=[]
        for obj in parts:
            for cutter in cutters:obj=obj-cutter
            if obj.volume>1e-9:trimmed.append(obj)
        parts=trimmed
    return cad.Compound(children=parts,label='Development-only layered hybrid panel')


def coupled_core(config, density):
    """Select a complete grade, rather than varying density at fixed stiffness."""
    records=config.get('core_grades',{})
    if str(density) not in records:raise ValueError('Density requires an explicitly coupled core-grade record')
    grade=records[str(density)]
    for key in ('density_kg_m3','young_pa','shear_pa','compressive_strength_pa','shear_strength_pa'):
        positive(grade[key],key)
    if grade['density_kg_m3']!=density:raise ValueError('Core grade density mismatch')
    return dict(grade)


def support_network(config, width, height, span, *, holes=()):
    """Actual transverse frame rails, brackets and fasteners for each support pitch.

    Rails are split at apertures; missing attachment/edge support is reported,
    never credited as a realised shorter unsupported panel span.
    """
    from osr_mech.section_contract import rhs,geometry
    from osr_mech.automated_geometry import primitive_volume
    for value in (width,height,span):positive(value,'support geometry')
    s=config['supports'];section=rhs(s['rail_width_m'],s['rail_depth_m'],s['rail_wall_m'],density_kg_m3=s['rail_density_kg_m3'])
    margin=max(config['panel']['edge_land_m']+config['panel']['potting_radius_m']+.005,.06)
    if 2*margin>=height:raise ValueError('support attachment lands do not fit panel')
    count=max(1,math.ceil((height-2*margin)/span));stations=[margin+(height-2*margin)*i/count for i in range(count+1)]
    rails=[];broken=[]
    for i,y in enumerate(stations):
        exclusions=sorted((max(0,x0),min(width,x1))for x0,y0,x1,y1 in holes if y0<y<y1 and x1>0 and x0<width)
        cursor=0;segments=[]
        for a,b in exclusions:
            if a>cursor:segments.append((cursor,a))
            cursor=max(cursor,b)
        if cursor<width:segments.append((cursor,width))
        if exclusions:broken.append(i)
        for j,(a,b) in enumerate(segments):
            if b-a<s['rail_width_m']:continue
            spec=geometry(section,b-a,centre_m=((a+b)/2,y,-.045))
            rails.append(dict(id=f'support-{i}-{j}',station_m=y,interval_m=[a,b],geometry=spec,
                mass_kg=(b-a)*section['mass_kg_m'],brackets=s['brackets_per_rail'],
                fasteners=s['brackets_per_rail']*s['fasteners_per_bracket']))
    rail_mass=sum(r['mass_kg'] for r in rails)
    brackets=sum(r['brackets'] for r in rails);fasteners=sum(r['fasteners'] for r in rails)
    total=rail_mass+brackets*s['bracket_mass_kg_each']+fasteners*s['fastener_mass_kg_each']
    values=[s.get('rail_usd_kg'),s.get('bracket_usd_each'),s.get('fastener_usd_each')]
    cost=None if any(v is None for v in values)else rail_mass*values[0]+brackets*values[1]+fasteners*values[2]
    return dict(rails=rails,rail_count=len(rails),bracket_count=brackets,fastener_count=fasteners,
        mass_kg=total,rail_mass_kg=rail_mass,section=section,actual_max_pitch_m=(height-2*margin)/count,
        edge_overhang_m=margin,panel_attachment_count=2*len(rails),
        panel_attachment_sites_m=[[a+(b-a)*f,r['station_m']]for r in rails for a,b in [r['interval_m']]for f in (.2,.8)],
        aperture_interrupted_stations=broken,nominal_span_realised=not broken,
        installed_cost_usd=cost,joint_stiffness_qualified=False,physical_validation=False)
