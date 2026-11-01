"""Exact stepped-prism research geometries for a common 20 m civil span.

Polygons are convex sections in the y-z plane, extruded along x. Their union is
the physical stock definition; it is not a BREP, reinforcement design or an
organic/topology optimisation result. All centroids and inertias are geometric
properties of the stated stock, with no cracked-concrete/composite-action credit.
"""
from copy import deepcopy
from math import fsum, isfinite

from engineering.station_rail.common import identity

FAMILIES = ("reference_box", "ribbed_u", "variable_depth_box", "folded_plate",
    "hybrid_steel_concrete", "load_following_ribs")
PROFILES = ("lean", "reference", "robust")
MATERIALS = {"research_concrete": dict(density_kg_m3=2500.0),
    "structural_steel": dict(density_kg_m3=7850.0)}
EPS = 1e-10


def _cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _polygon(points):
    p = [tuple(float(x) for x in point) for point in points]
    if len(p) < 3 or any(len(point) != 2 or not all(isfinite(x) for x in point) for point in p):
        raise ValueError("Finite y-z polygon vertices required")
    # Permit a conventional final closing vertex once. Every other repeated
    # vertex is invalid: a twice-traversed convex ring otherwise passes the
    # half-plane test while its shoelace area double counts the same stock.
    def coincident(a,b):
        return max(abs(a[0]-b[0]),abs(a[1]-b[1])) <= EPS
    if coincident(p[0],p[-1]):
        p.pop()
    if len(p)<3 or any(coincident(a,b) for i,a in enumerate(p) for b in p[i+1:]):
        raise ValueError("Distinct polygon vertices and a singly traversed ring required")
    def intersects(a,b,c,d):
        ab_c,ab_d,cd_a,cd_b = _cross(a,b,c),_cross(a,b,d),_cross(c,d,a),_cross(c,d,b)
        def on_segment(a,b,c,cross):
            return (abs(cross)<=EPS and min(a[0],b[0])-EPS<=c[0]<=max(a[0],b[0])+EPS
                and min(a[1],b[1])-EPS<=c[1]<=max(a[1],b[1])+EPS)
        return ((ab_c>EPS and ab_d < -EPS or ab_c < -EPS and ab_d>EPS)
            and (cd_a>EPS and cd_b < -EPS or cd_a < -EPS and cd_b>EPS)
            or on_segment(a,b,c,ab_c) or on_segment(a,b,d,ab_d)
            or on_segment(c,d,a,cd_a) or on_segment(c,d,b,cd_b))
    edges = list(zip(p,p[1:]+p[:1]))
    for i,(a,b) in enumerate(edges):
        for j,(c,d) in enumerate(edges[i+1:],i+1):
            if j==i+1 or i==0 and j==len(edges)-1:
                continue
            if intersects(a,b,c,d):
                raise ValueError("A simple non-self-overlapping polygon ring required")
    signed = fsum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2
    if abs(signed) <= EPS:
        raise ValueError("Positive polygon area required")
    if signed < 0:
        p.reverse()
    if any(_cross(a,b,c) < -EPS for a,b in zip(p,p[1:]+p[:1]) for c in p):
        raise ValueError("Convex non-self-intersecting polygon required")
    return p


def _properties(points):
    p = _polygon(points)
    cross = [a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])]
    area = fsum(cross)/2
    cy = fsum((a[0]+b[0])*q for a,b,q in zip(p,p[1:]+p[:1],cross))/(6*area)
    cz = fsum((a[1]+b[1])*q for a,b,q in zip(p,p[1:]+p[:1],cross))/(6*area)
    iy0 = fsum((a[1]**2+a[1]*b[1]+b[1]**2)*q
        for a,b,q in zip(p,p[1:]+p[:1],cross))/12
    iz0 = fsum((a[0]**2+a[0]*b[0]+b[0]**2)*q
        for a,b,q in zip(p,p[1:]+p[:1],cross))/12
    perimeter = fsum(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
        for a,b in zip(p,p[1:]+p[:1]))
    return dict(area_m2=area, centroid_yz_m=[cy,cz],
        I_y_m4=max(0.,iy0-area*cz**2), I_z_m4=max(0.,iz0-area*cy**2),
        perimeter_m=perimeter)


def _intersection_area(subject, clip):
    out = list(subject)
    for a,b in zip(clip,clip[1:]+clip[:1]):
        original,out = out,[]
        if not original:
            return 0.
        for start,end in zip(original[-1:]+original[:-1],original):
            ds,de = _cross(a,b,start),_cross(a,b,end)
            ins,ine = ds >= -EPS,de >= -EPS
            if ins != ine:
                t = ds/(ds-de)
                out.append((start[0]+t*(end[0]-start[0]),start[1]+t*(end[1]-start[1])))
            if ine:
                out.append(end)
    return abs(fsum(a[0]*b[1]-b[0]*a[1] for a,b in zip(out,out[1:]+out[:1]))/2) if out else 0.


def _shared_edge(a, b):
    total = 0.
    for p,q in zip(a,a[1:]+a[:1]):
        length = ((q[0]-p[0])**2+(q[1]-p[1])**2)**.5
        if length <= EPS:
            continue
        for r,s in zip(b,b[1:]+b[:1]):
            if abs(_cross(p,q,r)) > EPS or abs(_cross(p,q,s)) > EPS:
                continue
            dr = ((r[0]-p[0])*(q[0]-p[0])+(r[1]-p[1])*(q[1]-p[1]))/length
            ds = ((s[0]-p[0])*(q[0]-p[0])+(s[1]-p[1])*(q[1]-p[1]))/length
            total += max(0.,min(length,max(dr,ds))-max(0.,min(dr,ds)))
    return total


def _rectangle(y0,y1,z0,z1):
    if not y1 > y0 or not z1 > z0:
        raise ValueError("Positive rectangular stock dimensions required")
    return [[y0,z0],[y1,z0],[y1,z1],[y0,z1]]


def _section(name,polygon,material="research_concrete"):
    return dict(id=name, material=material, polygon_yz_m=[list(p) for p in _polygon(polygon)])


def _box(depth,thickness):
    t = thickness
    return [_section("deck",_rectangle(-1,1,-t,0)),
        _section("bottom",_rectangle(-1,1,-depth,-depth+t)),
        _section("left-web",_rectangle(-1,-1+t,-depth+t,-t)),
        _section("right-web",_rectangle(1-t,1,-depth+t,-t))]


def generate(family, profile="reference"):
    """Return one immutable nominal-stock physical definition, not an evaluation."""
    if family not in FAMILIES or profile not in PROFILES:
        raise ValueError("Registered family and named physical profile required")
    scale = {"lean":(.85,.8),"reference":(1.,1.),"robust":(1.15,1.2)}[profile]
    depth_scale,wall_scale = scale
    cells = []
    def add(x0,x1,sections):
        cells.append(dict(id=f"cell-{len(cells):03d}",x_start_m=x0,x_end_m=x1,sections=sections))
    if family == "reference_box":
        add(0.,20.,_box(1.4*depth_scale,.18*wall_scale))
        method = "constant closed rectangular box assembled from four disjoint concrete polygons"
    elif family == "ribbed_u":
        # Open-bottom inverted U deck; short transverse webs join the two ribs.
        d,t,web = 1.25*depth_scale,.16*wall_scale,.22*wall_scale
        pitch = {"lean":5.,"reference":2.5,"robust":2.}[profile]
        rib_width = .16*wall_scale
        centers = [pitch*i for i in range(1,int(20/pitch))]
        boundaries = sorted({0.,20.,*(x+offset for x in centers for offset in (-rib_width/2,rib_width/2))})
        for x0,x1 in zip(boundaries,boundaries[1:]):
            sections = [_section("deck",_rectangle(-1,1,-t,0)),
                _section("left-longitudinal-rib",_rectangle(-.8,-.8+web,-d,-t)),
                _section("right-longitudinal-rib",_rectangle(.8-web,.8,-d,-t))]
            if any(abs((x0+x1)/2-x)<rib_width/2+EPS for x in centers):
                sections.append(_section("transverse-rib",_rectangle(-.8+web,.8-web,-d*.75,-t)))
            add(x0,x1,sections)
        method = "open-bottom inverted-U deck with explicit transverse rib stations; no hollow-box substitution"
    elif family == "variable_depth_box":
        for i in range(20):
            u = (i+.5)/20
            d = (.85+.55*4*u*(1-u))*depth_scale
            add(float(i),float(i+1),_box(d,.16*wall_scale))
        method = "20 exact one-metre stepped box prisms; midpoint-sampled parabolic depth, not a smooth loft"
    elif family == "folded_plate":
        d,t,web = 1.25*depth_scale,.14*wall_scale,.14*wall_scale
        # Sloping webs use horizontal web thickness, not normal thickness.
        left = [[-.8,-t],[-.35,-d+t],[-.35+web,-d+t],[-.8+web,-t]]
        right = [[-y,z] for y,z in left]
        add(0.,20.,[_section("deck",_rectangle(-1,1,-t,0)),
            _section("bottom-fold",_rectangle(-.35,.35,-d,-d+t)),
            _section("inclined-left-web",left),_section("inclined-right-web",right)])
        method = "four actual polygonal plates, including inclined parallelogram webs; horizontal web-thickness parameter"
    elif family == "hybrid_steel_concrete":
        slab,d = .18*wall_scale,1.2*depth_scale
        tf,web = .025*wall_scale,.016*wall_scale
        sections = [_section("concrete-deck",_rectangle(-1,1,-slab,0))]
        for side,center in (("left",-.65),("right",.65)):
            for name,polygon in (("top-flange",_rectangle(center-.15,center+.15,-slab-tf,-slab)),
                    ("bottom-flange",_rectangle(center-.2,center+.2,-d,-d+tf)),
                    ("web",_rectangle(center-web/2,center+web/2,-d+tf,-slab-tf))):
                sections.append(_section(side+"-"+name,polygon,"structural_steel"))
        add(0.,20.,sections)
        method = "concrete slab and two disjoint three-polygon steel I-girders; shear connectors and composite action unresolved"
    else:
        t,web = .14*wall_scale,.18*wall_scale
        for i in range(20):
            u = (i+.5)/20
            shape = 4*u*(1-u)
            d = (.55+.75*shape)*depth_scale
            center = .75-.4*shape
            add(float(i),float(i+1),[_section("deck",_rectangle(-1,1,-t,0)),
                _section("left-load-following-rib",_rectangle(-center-web/2,-center+web/2,-d,-t)),
                _section("right-load-following-rib",_rectangle(center-web/2,center+web/2,-d,-t))])
        method = "20 exact stepped cells with prescribed parabolic depth and converging twin ribs; no principal-stress optimisation claimed"
    result = dict(schema="osr-civil-shape-physical/1",family=family,profile=profile,
        span_m=20.,deck_width_m=2.,coordinate_frame=dict(x="longitudinal",y="transverse",z="up",deck_top_z_m=0.),
        materials=deepcopy(MATERIALS),cells=cells,
        provenance=dict(representation="convex polygon sections extruded as exact piecewise prisms",
            method=method,cell_count=len(cells),BREP_generated=False,
            discretisation_is_physical_stepping=True,smooth_surface_equivalence_claimed=False),
        unresolved_installed_items=["reinforcement/prestress and anchorages", "rail/fastener interfaces", "bearings and restraints",
            "joints and fasteners", "hybrid shear connectors where applicable", "drainage and maintenance access", "lifting points and rigging"],
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    result["candidate_id"] = identity(result)
    validate(result)
    return result


def validate(definition):
    if (definition.get("schema") != "osr-civil-shape-physical/1"
            or definition.get("candidate_id") != identity({k:v for k,v in definition.items() if k!="candidate_id"})
            or definition.get("span_m") != 20. or definition.get("deck_width_m") != 2.
            or definition.get("coordinate_frame") != dict(x="longitudinal",y="transverse",z="up",deck_top_z_m=0.)):
        raise ValueError("Canonical common-interface physical definition required")
    materials = definition["materials"]
    if not materials or any(type(m.get("density_kg_m3")) not in (int,float)
            or not isfinite(m["density_kg_m3"]) or m["density_kg_m3"]<=0 for m in materials.values()):
        raise ValueError("Finite positive material densities required")
    cells = definition.get("cells",[])
    previous = 0.
    for cell in cells:
        start,end = cell["x_start_m"],cell["x_end_m"]
        if (type(start) not in (int,float) or type(end) not in (int,float)
                or not isfinite(start) or not isfinite(end) or abs(start-previous)>EPS or end<=start or end>20.+EPS):
            raise ValueError("Contiguous finite positive prism intervals required")
        previous = end
        sections = cell["sections"]
        if not sections or len({s["id"] for s in sections})!=len(sections):
            raise ValueError("Unique nonempty cell section identities required")
        polygons = []
        for section in sections:
            if section["material"] not in materials:
                raise ValueError("Declared material required")
            p = _polygon(section["polygon_yz_m"])
            if any(abs(y)>1.+EPS or z>EPS for y,z in p):
                raise ValueError("Stock exceeds common deck width or top plane")
            if any(_intersection_area(p,q)>EPS for q in polygons):
                raise ValueError("Overlapping stock interiors would double count mass")
            polygons.append(p)
    if not cells or abs(previous-20.)>EPS:
        raise ValueError("Physical cells must cover the 20 m span")
    if any(definition.get(k) is not False for k in ("physical_accepted","engineering_accepted","manufacturing_release","operating_release")):
        raise ValueError("Nominal geometry cannot grant engineering or physical acceptance")
    return True


def quantities(definition):
    """Calculate exact declared stock and union surface, never installed mass.

    I_y/I_z by material are length-averaged cross-sectional geometric inertias
    about that material's volume centroid. Gross section station I has no E
    weighting and cannot claim steel-concrete composite bending stiffness.
    """
    validate(definition)
    stocks = []
    surfaces = {m:0. for m in definition["materials"]}
    stations = []
    previous = []
    for cell in definition["cells"]:
        length = cell["x_end_m"]-cell["x_start_m"]
        entries = []
        for section in cell["sections"]:
            p = _polygon(section["polygon_yz_m"])
            prop = _properties(p)
            material = section["material"]
            volume = prop["area_m2"]*length
            row = dict(material=material,volume=volume,
                center=[(cell["x_start_m"]+cell["x_end_m"])/2,*prop["centroid_yz_m"]],
                iy_volume=prop["I_y_m4"]*length,iz_volume=prop["I_z_m4"]*length)
            stocks.append(row)
            surfaces[material] += 2*prop["area_m2"]+length*prop["perimeter_m"]
            for other in entries:
                if material==other["material"]:
                    surfaces[material] -= 2*length*_shared_edge(p,other["polygon"])
            for other in previous:
                if material==other["material"]:
                    surfaces[material] -= 2*_intersection_area(p,other["polygon"])
            entries.append(dict(material=material,polygon=p,properties=prop))
        total_area = fsum(r["properties"]["area_m2"] for r in entries)
        cy = fsum(r["properties"]["area_m2"]*r["properties"]["centroid_yz_m"][0] for r in entries)/total_area
        cz = fsum(r["properties"]["area_m2"]*r["properties"]["centroid_yz_m"][1] for r in entries)/total_area
        iy = fsum(r["properties"]["I_y_m4"]+r["properties"]["area_m2"]*(r["properties"]["centroid_yz_m"][1]-cz)**2 for r in entries)
        stations.append(dict(x_start_m=cell["x_start_m"],x_end_m=cell["x_end_m"],
            gross_area_m2=total_area,gross_centroid_yz_m=[cy,cz],gross_I_y_m4=iy,
            composite_stiffness_credit=False))
        previous = entries
    by_material = {}
    for material in sorted(definition["materials"]):
        selected = [r for r in stocks if r["material"]==material]
        volume = fsum(r["volume"] for r in selected)
        if not selected:
            continue
        center = [fsum(r["volume"]*r["center"][i] for r in selected)/volume for i in range(3)]
        by_material[material] = dict(volume_m3=volume,
            mass_kg=volume*definition["materials"][material]["density_kg_m3"],centroid_m=center,
            I_y_m4=fsum(r["iy_volume"]+r["volume"]*(r["center"][2]-center[2])**2 for r in selected)/20.,
            I_z_m4=fsum(r["iz_volume"]+r["volume"]*(r["center"][1]-center[1])**2 for r in selected)/20.,
            material_boundary_surface_m2=surfaces[material])
    total_mass = fsum(row["mass_kg"] for row in by_material.values())
    mass_center = [fsum(row["mass_kg"]*row["centroid_m"][i] for row in by_material.values())/total_mass for i in range(3)]
    result = dict(schema="osr-civil-shape-quantities/1",candidate_id=definition["candidate_id"],
        by_material=by_material,total_nominal_volume_m3=fsum(r["volume_m3"] for r in by_material.values()),
        total_nominal_stock_mass_kg=total_mass,centroid_m=mass_center,
        concrete_contact_surface_m2=surfaces.get("research_concrete",0.),steel_surface_m2=surfaces.get("structural_steel",0.),
        minimum_gross_bending_I_y_m4=min(r["gross_I_y_m4"] for r in stations),section_stations=stations,
        lifting_mass_kg=total_mass,lifting_mass_scope="nominal stock only; excludes unresolved installed items, lifting points and rigging",
        surface_scope="exact same-material union boundary; interfaces with another material retained; no formwork access/reuse/removal feasibility claimed",
        inertia_scope="gross uncracked geometric section only; no E transformation, steel-concrete bond, reinforcement or structural acceptance",
        discretisation_provenance=deepcopy(definition["provenance"]),
        complete_installed_mass_kg=None,physical_accepted=False,engineering_accepted=False,
        manufacturing_release=False,operating_release=False)
    result["evaluation_id"] = identity(result)
    return result
