"""Source-car assembly and proposed local rail/running-gear fabrication layouts.

The selected stock is reproduced without changing its engineering coordinates.
Exploded offsets affect presentation only. Shop fixtures, fasteners and process
machines are declared proposals; none is released production tooling.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from math import ceil, cos, pi, sin
from pathlib import Path

PRODUCER = 'engineering/visual_models/fabrication.py'
EVALUATION = 'docs/design-engine/current/evaluation.json.gz'
RAIL_DRAWING = 'https://www.voestalpine.com/highperformancemetals/argentina/app/uploads/sites/264/2024/09/voestalpine-60E1.pdf'
RAIL_TABLE = 'https://rails.arcelormittal.com/profiles/transport-rails/european-standards/'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, installed_mass_complete=False)


class _Parts:
    def __init__(self):
        self.entities = []

    def add(self, ident, shape, at, material, group, basis, source, **fields):
        value = dict(id=ident, shape=shape, at_m=list(at), material=material,
                     group=group, basis=basis, source=source,
                     render_offset_m=[0., 0., 0.], **fields)
        self.entities.append(value)
        return value

    def box(self, ident, at, size, material='steel', group='tooling', **kw):
        return self.add(ident, 'box', at, material, group,
            kw.pop('basis', 'illustrative-tooling'),
            kw.pop('source', 'Explicit proposed fabrication fixture dimensions; capacity and procedures unqualified'),
            size_m=list(size), **kw)

    def cyl(self, ident, at, radius, length, axis=(0, 0, 1), material='steel', group='tooling', **kw):
        return self.add(ident, 'cylinder', at, material, group,
            kw.pop('basis', 'illustrative-tooling'),
            kw.pop('source', 'Explicit proposed tooling envelope; bearings, retention and load capacity unqualified'),
            radius_m=radius, length_m=length, axis=list(axis), **kw)

    def tube(self, ident, at, radius, inner, length, axis=(0, 0, 1), material='steel', group='tooling', **kw):
        return self.add(ident, 'tube', at, material, group,
            kw.pop('basis', 'illustrative-tooling'),
            kw.pop('source', 'Explicit proposed housing/fastener envelope; internal design unqualified'),
            radius_m=radius, inner_radius_m=inner, length_m=length, axis=list(axis), **kw)

    def pipe(self, ident, points, radius=.012, material='dark_steel', group='routing'):
        return self.add(ident, 'pipe', (0,0,0), material, group, 'proposed-envelope',
            'Illustrative flexible hose/cable centreline and routing envelope; bend radius and fatigue unqualified',
            path_m=[list(p) for p in points], radius_m=radius)


def _context(record):
    v = record['vehicle']
    return dict(reference_candidate_id=v['candidate_id'],
        reference_body_candidate_id=v['body_candidate_id'],
        reference_support_component_id=v['support_component_id'],
        source_evaluation_id=record['evaluation_id'],
        geometry_adopted=False, complete_installed_geometry=False,
        coordinate_frame='x-forward, y-left, z-up; rail running surface z=0', **FLAGS)


def _material(part):
    name = part['id']
    if 'window' in name:
        return 'glass'
    if 'seat-unit' in name:
        return 'teal' if ('skin' in name or 'pad' in name) else 'aluminium'
    if part['system'] == 'bogies':
        return 'steel' if '/wheel/' in name or '/axle/' in name else 'dark_steel'
    if part['system'] == 'passive-secondary':
        return 'aluminium'
    if part.get('material') == 'bond-surface':
        return 'orange'
    if part['system'] == 'underframe' or 'replacement-frame' in name:
        return 'aluminium'
    return 'white'


def _explode(part):
    """Named assembly groups, not arbitrary displacement of individual parts."""
    name, at = part['id'], part['at_m']
    if part['system'] == 'bogies':
        # Both complete source bogie groups move together to the foreground
        # inspection lane for the exploded image. Installed CAD stays exact.
        return [0.,-3.2,0.], 'bogies'
    if name.startswith('comfort-shell/roof/') or name.endswith('/roof'):
        return [0.,0.,2.6], 'roof'
    if name.startswith('comfort-shell/seat-unit/'):
        return [0.,0.,1.55], 'seating'
    if name.startswith('comfort-shell/floor/'):
        return [0.,0.,.65], 'floor'
    if name.startswith(('comfort-shell/door/', 'comfort-shell/door-window/')):
        return [0.,-2.25,.35], 'doors'
    if name.startswith('comfort-shell/fixed-window/'):
        return [0.,-1.65 if at[1] < 0 else 1.65,0.], 'glazing'
    if name.startswith(('comfort-shell/retained/panel/', 'comfort-shell/retained/lap/')):
        if part.get('role') == 'panel-end' or '/end' in name:
            return [-.8 if at[0] < 0 else .8,0.,0.], 'end-covers'
        return [0.,-1.65 if at[1] < 0 else 1.65,0.], 'side-covers'
    return [0.,0.,0.], part['system']


def _source_part(parts, part, *, prefix='source/', translation=(0.,0.,0.), explode=False):
    shape = 'tube' if part['kind'] == 'annular-cylinder' else part['kind']
    if shape not in ('box','cylinder','tube'):
        raise ValueError('Unsupported selected-car primitive: '+part['kind'])
    fields = {k:deepcopy(part[k]) for k in ('size_m','axis','radius_m','inner_radius_m','length_m','holes') if k in part}
    if shape == 'cylinder' and part.get('inner_radius_m',0.) > 0:
        shape = 'tube'
    fields.update(source_part_id=part['id'], source_at_m=list(part['at_m']),
        source_volume_m3=part['volume_m3'], source_mass_kg=part['mass_kg'],
        source_material=part.get('material'),
        source_rigid_transform=dict(rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]], translation_m=list(translation)))
    offset, group = _explode(part) if explode else ([0.,0.,0.],part['system'])
    value = parts.add(prefix+part['id'], shape,
        [a+b for a,b in zip(part['at_m'],translation)], _material(part), group,
        'source-geometry', EVALUATION+'#vehicle.geometry_parts/'+part['id'], **fields)
    value['render_offset_m'] = offset
    return value


def _bolt(parts, ident, x, y, z, axis=(0,0,1), radius=.01, length=.07, group='fixture-fasteners'):
    parts.cyl(ident+'/shank',(x,y,z),radius,length,axis,group=group)
    end=[q+u*(length-.012) for q,u in zip((x,y,z),axis)]
    parts.cyl(ident+'/head',end,radius*1.7,.012,axis,material='dark_steel',group=group)


def _vehicle(record):
    source = record['vehicle']; parts = _Parts()
    for part in source['geometry_parts']:
        _source_part(parts,part,explode=True)
    # Exact source bodies remain in their installed coordinate frame. Only the
    # proposed fixture is below/alongside them. Pads meet known side-sill bases.
    parts.box('shop/floor',(-11.,-6.,-.85),(22.,12.,.12),'ground')
    xs = (-5.,-2.,2.,5.)
    for i,x in enumerate(xs):
        parts.box(f'fixture/crossbeam/{i}',(x-.12,-1.55,-.60),(.24,3.1,.18),'teal')
        for side in (-1,1):
            y=side*1.10; key=f'fixture/{i}/{side}'
            parts.box(key+'/foot',(x-.23,y-.23,-.73),(.46,.46,.08),'dark_steel')
            parts.box(key+'/column',(x-.075,y-.075,-.65),(.15,.15,1.0495),'teal')
            parts.box(key+'/pad',(x-.125,y-.10,.3995),(.25,.20,.045),'rubber',group='datum-pads')
            # External clamps sit outside the source sill rather than covering
            # the axle or passive fin envelope. Clamp loads remain unspecified.
            cy=side*1.34
            parts.box(key+'/clamp-bracket',(x-.09,cy-.055,.40),(.18,.11,.30),'orange',group='alignment-clamps')
            for j,dx in enumerate((-.14,.14)):
                _bolt(parts,key+f'/anchor/{j}',x+dx,y,-.73,length=.16)
    # Two shop rails use the same explicit simplified display profile as the
    # rail-fabrication scene. They are separate tooling, not extra vehicle mass.
    for side in (-1,1):
        _rail(parts,f'fixture/shop-rail/{side}',-9.,side*.7535,18.,group='shop-track')
    # Grounded inspection skids support the render-only bogie explosion.
    # They are proposed shop tooling, not additional vehicle stock. Their rails
    # have running surface z=0, matching the source wheel contact datum.
    for bogie,centre in enumerate((-6.4,6.4)):
        key=f'inspection-dolly/{bogie}';lane_y=-3.2
        for side in (-1,1):
            yy=lane_y+side*.7535
            _rail(parts,key+f'/rail/{side}',centre-1.65,yy,3.3,group='bogie-inspection-dollies')
            for direction in (-1,1):
                parts.box(key+f'/stop/{side}/{direction}',
                    (centre+direction*1.56-.055,yy-.08,0.),(.11,.16,.13),
                    'orange',group='bogie-inspection-dollies')
        for row,dx in enumerate((-1.25,0.,1.25)):
            x=centre+dx
            parts.box(key+f'/crossbeam/{row}',(x-.075,lane_y-1.,-.23),
                (.15,2.,.058),'teal',group='bogie-inspection-dollies')
            for side in (-1,1):
                y=lane_y+side*.8; support=key+f'/support/{row}/{side}'
                parts.box(support+'/foot',(x-.20,y-.20,-.73),(.40,.40,.04),
                    'dark_steel',group='bogie-inspection-dollies')
                parts.box(support+'/post',(x-.05,y-.05,-.69),(.10,.10,.46),
                    'teal',group='bogie-inspection-dollies')
                for anchor,offset in enumerate((-.13,.13)):
                    _bolt(parts,support+f'/anchor/{anchor}',x+offset,y,-.73,
                        radius=.01,length=.12,group='bogie-dolly-fasteners')
    # Small process bench and hose/cable support are kept outside the car.
    # Park it farther outboard than the exploded bogie and its inspection skid.
    parts.box('bench/worktop',(4.8,-5.70,.05),(3.5,.9,.08),'wood')
    for i,x in enumerate((4.95,8.0)):
        for j,y in enumerate((-5.60,-4.95)):
            parts.box(f'bench/leg/{i}/{j}',(x,y,-.73),(.09,.09,.78),'teal')
    for i in range(8):
        parts.box(f'bench/joint-coupon/{i}',(5.+i*.36,-5.50,.13),(.26,.18,.04),'aluminium')
    parts.box('services/retracting-trolley',(-7.,-5.5,-.73),(.9,.7,1.0),'teal',group='shop-services')
    parts.pipe('services/flexible-hose',[(-6.6,-5.1,.2),(-6.4,-4.6,.5),(-6.1,-4.4,.8),(-5.9,-4.3,.9)],.018)
    counts=Counter(p['system'] for p in source['geometry_parts'])
    mass=source['mass']
    return dict(id='vehicle-fabrication',title='Build a repairable vehicle',
        subtitle='Source geometry, exploded for assembly; fixtures are proposed',
        entities=parts.entities,
        labels=[
            dict(text='17 m frame and underfloor stock',anchor_m=[0.,-1.1,.62],side='left',order=0),
            dict(text='Bonded roof and removable covers',anchor_m=[0.,0.,6.38],side='right',order=0),
            dict(text='44 seats + 2 wheelchair places',anchor_m=[1.,-.8,3.1],side='right',order=1),
            dict(text='Two boarding-side doors',anchor_m=[-4.5,-3.55,2.3],side='left',order=1),
            dict(text='Passive bogies; independent brakes',anchor_m=[7.45,-3.9475,.38],side='right',order=2),
            dict(text='Reusable alignment fixture and QA',anchor_m=[-5.,-1.34,.55],side='left',order=2)],
        camera=dict(direction=[1.,-1.25,.8],target_m=[0.,-.6,2.5],ortho_scale_m=24.5),
        metrics=dict(source_parts=len(source['geometry_parts']),source_system_counts=dict(counts),
            body_length_m=17.,body_width_m=2.65,fixed_seats_per_car=44,wheelchair_places_per_car=2,
            bogies_per_car=2,axles_per_car=4,wheels_per_car=8,passenger_doors_per_car=2,
            source_located_material_kg=mass['located_material_kg'],
            accounted_tare_kg=mass['accounted_tare_kg_per_car'],
            unlocated_reference_accounts_kg=mass['unlocated_or_reference_account_kg'],
            complete_installed_mass_kg=None,render_offsets_are_presentation_only=True,
            bogie_render_offset_m=[0.,-3.2,0.],
            source_bogie_installation_coordinates_unchanged=True,
            proposed_bogie_inspection_dollies=2,dolly_rail_segments=4,
            dolly_floor_supports=12,dolly_retention_stops=8,
            dolly_floor_anchor_assemblies=24,
            fixture_posts=8,datum_pads=8,alignment_clamps=8,fixture_anchor_assemblies=16,
            complete_joint_and_fastener_inventory=False,
            production_shifts_per_day=2,hours_per_shift=8),
        assumptions=[
            'All2482 source primitives, including raw drilling-hole lists, retain exact source coordinates/dimensions. Exploded offsets are presentation transforms only.',
            'No suspension, HVAC, battery, wiring or attachment residual has been converted into a fictitious installed solid. Remaining accounts are not zero.',
            'Fixture pad coordinates target the source sill underside at z0.4445m; stability, support pressure and tooling tolerances are unverified.',
            'Proposed clamps/jack columns/anchors and shop service route are counted illustrative tooling; no lifting, workholding or weld process release is implied.',
            'Both complete source bogies are displaced 3.2 m toward negative y for presentation only. Proposed grounded inspection skids align their railhead with source z=0; native bogie installation coordinates remain unchanged.',
            'Inspection-skid strength, anchorage, wheel-stop capacity and handling stability remain unqualified. The bench is parked outboard with 0.6 m geometric separation from the skid-foot envelope; that is not a verified human/tool working aisle.',
            'A staged assembly requires joint preparation, welding/bonding qualification, fixture metrology, cure records, fastening torque and dimensional inspection.',
            'Moving roof/cover/seat/door/bogie groups form an exploded diagram; no collision-free handling sweep or retention/repair qualification is claimed.'],
        manufacturing_steps=[
            'Cut and machine source metal stock; identify material lots and prepare joint coupons.',
            'Align underframe on eight padded datum positions; check diagonal, twist and interfaces before joining.',
            'Join and inspect frame under a qualified process; complete first-article dimensional check.',
            'Produce composite floor/roof/covers in controlled moulds; inspect layup, cure and bonded joints.',
            'Install source seating, doors and glazing; resolve all remaining service/equipment accounts and access envelopes.',
            'Fit passive running gear and independent brakes; weigh, survey and test the installed assembly before any release.'],
        reference_context=_context(record),**FLAGS)


def _polygon_area(points):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2


def _rail(parts,ident,x,y,length,group='rail-stock',z=0.):
    return parts.add(ident,'profile',(x,y,z),'steel',group,'proposed-envelope',
        '60E1 display contour derived from '+RAIL_DRAWING+'; nominal manufacturer dimensions/rate from '+RAIL_TABLE+'; not a contact/rolling tolerance model',
        points_yz_m=deepcopy(_RAIL_PROFILE),length_m=length,
        nominal_reference_mass_kg_m=60.21,profile_qualified=False,
        volume_is_nominal_rail_mass_basis=False)


def _rail_set(parts,ident,x,y):
    parts.box(ident+'/plate',(x-.09,y-.12,-.205),(.18,.24,.025),'dark_steel',group='rail-fastening')
    parts.box(ident+'/pad',(x-.08,y-.09,-.180),(.16,.18,.008),'rubber',group='rail-fastening')
    for side in (-1,1):
        yy=y+side*.105
        _bolt(parts,ident+f'/anchor/{side}',x,yy,-.265,radius=.012,length=.12,group='rail-fastening')
        parts.tube(ident+f'/washer/{side}',(x,yy,-.149),.024,.0125,.005,material='steel',group='rail-fastening')
        parts.pipe(ident+f'/clip/{side}',[(x-.035,yy,-.138),(x+.035,yy,-.126),
            (x+.052,y+side*.082,-.120),(x+.035,y+side*.063,-.148)],.011,'steel','rail-fastening')


def _shop(record):
    parts=_Parts();vehicle=record['vehicle']
    parts.box('shop/floor',(-8.,-6.5,-.85),(17.,13.,.12),'ground')
    # A12m prefabrication/inspection jig. It is not an unqualified assertion that
    # a12m rail panel can be transported, thermally fixed or lifted at every site.
    pitch=.6;rail_y=3.0
    for side in (-1,1):
        y=rail_y+side*.7535
        _rail(parts,f'rail-jig/stock/{side}',-6.,y,12.)
        for i in range(21):
            x=-6.+i*pitch
            parts.box(f'rail-jig/support/{side}/{i}',(x-.20,y-.20,-.73),(.4,.4,.525),'concrete',group='inspection-jig')
            _rail_set(parts,f'rail-jig/set/{side}/{i}',x,y)
    # Open clamp/welding-machine envelope alongside, not around the completed
    # panel. These work samples are not additional installed track quantities.
    wz=.65;wy=5.3
    for j,(x,length) in enumerate(((-5.5,1.497),(-3.997,1.497))):
        _rail(parts,f'weld/rail-sample/{j}',x,wy,length,'weld-work-samples',z=wz)
    parts.box('weld/bed',(-5.7,4.9,-.73),(3.5,.8,1.18),'teal',group='rail-welder-envelope')
    for i,x in enumerate((-4.45,-3.55)):
        for side in (-1,1):
            parts.box(f'weld/clamp/{i}/{side}',(x-.16,wy+side*.10-.05,.55),(.32,.10,.24),'copper',group='rail-welder-envelope')
            parts.cyl(f'weld/clamp-cylinder/{i}/{side}',(x,wy+side*.32,.61),.07,.15,(0,-side,0),'dark_steel','rail-welder-envelope')
    parts.box('weld/supply-cabinet',(-1.8,4.9,-.73),(.85,.85,1.45),'teal',group='rail-welder-envelope')
    parts.pipe('weld/lead-a',[(-1.8,5.2,.3),(-2.6,5.7,.2),(-3.55,5.55,.55)],.026,'copper')
    parts.pipe('weld/lead-b',[(-1.8,5.4,.3),(-3.0,5.9,.2),(-4.45,5.55,.55)],.026,'copper')
    parts.box('inspection/cart',(4.5,4.7,-.73),(.85,.65,1.05),'teal',group='rail-inspection')
    parts.pipe('inspection/probe-lead',[(4.9,4.8,.1),(5.3,4.1,.4),(5.5,3.75,.12)],.009)
    parts.box('inspection/profile-gauge',(5.28,3.62,.06),(.42,.27,.10),'orange',group='rail-inspection')
    # Reproduce one actual selected bogie, rigidly translated from its vehicle
    # location to an assembly bay. Bearings/calipers remain explicit proposals.
    bogie_translation=(6.4,-2.5,0.)
    for part in vehicle['geometry_parts']:
        if part['id'].startswith('bogie/0/'):
            _source_part(parts,part,prefix='bogie-bay/',translation=bogie_translation)
    for side in (-1,1):
        yy=-2.5+side*.7535
        _rail(parts,f'bogie-bay/inspection-track/{side}',-1.65,yy,3.3,'inspection-track')
        for i,x in enumerate((-1.3,0.,1.3)):
            parts.box(f'bogie-bay/track-support/{side}/{i}',(x-.15,yy-.15,-.73),(.3,.3,.558),'teal',group='inspection-track')
        for direction in (-1,1):
            parts.box(f'bogie-bay/end-stop/{side}/{direction}',(direction*1.56-.055,yy-.08,0.),(.11,.16,.13),'orange',group='inspection-track')
    for x in (-1.05,1.05):
        # A calliper-envelope is parked beside each source disc; no exact clamp
        # load, pad shape, friction law, actuator or safe stopping is inferred.
        for side in (-1,1):
            yy=-2.5+side*.38
            key=f'bogie/caliper/{x}/{side}'
            parts.box(key+'/bridge',(x+.31,yy-.09,.26),(.12,.18,.27),'orange',group='proposed-brake-interfaces',basis='proposed-envelope')
            for face in (-1,1):
                parts.box(key+f'/arm/{face}',(x+.20,yy+face*.0675-.0225,.29),(.17,.045,.24),'orange',group='proposed-brake-interfaces',basis='proposed-envelope')
                parts.box(key+f'/pad/{face}',(x+.20,yy+face*.028-.009,.30),(.08,.018,.18),'rubber',group='proposed-brake-interfaces',basis='proposed-envelope')
            _bolt(parts,f'bogie/caliper-fastener/{x}/{side}/a',x+.25,yy-.04,.29,radius=.008,length=.09,group='proposed-brake-interfaces')
            _bolt(parts,f'bogie/caliper-fastener/{x}/{side}/b',x+.34,yy+.04,.29,radius=.008,length=.09,group='proposed-brake-interfaces')
    parts.pipe('bogie/brake-flexible-route',[(-1.5,-3.6,.5),(-.9,-3.5,.85),(.4,-3.5,.82),(1.4,-2.9,.6)],.011,'dark_steel','proposed-brake-interfaces')
    # Separate wheelset press-fit demonstration. Its duplicated source parts are
    # process samples, not another bogie or an addition to installed train mass.
    press_translation=(11.45,-2.6,.82)
    for part in vehicle['geometry_parts']:
        if part['id'].startswith(('bogie/0/axle/0','bogie/0/wheel/0/')):
            _source_part(parts,part,prefix='press-sample/',translation=press_translation)
    px,py,pz=4.,-2.6,1.20
    parts.box('press/bed',(3.3,-4.5,-.73),(1.4,4.0,.30),'teal',group='wheelset-press')
    for i,y in enumerate((-4.1,-1.3)):
        for side in (-1,1):
            parts.box(f'press/column/{i}/{side}',(px+side*.60-.07,y-.07,-.43),(.14,.14,1.95),'teal',group='wheelset-press')
        parts.box(f'press/crosshead/{i}',(px-.70,y-.12,1.52),(1.4,.24,.24),'dark_steel',group='wheelset-press')
    for i,y in enumerate((-3.53,-1.67)):
        parts.box(f'press/axle-support/{i}',(px-.15,y-.04,.80),(.3,.08,.325),'steel',group='wheelset-press')
    # Annular ram and pusher clear the source75mm axle radius. A solid ram
    # through the axle would be a false press-fit layout.
    parts.tube('press/ram-barrel',(px,-4.1,pz),.17,.09,.50,(0,1,0),'dark_steel','wheelset-press')
    parts.tube('press/ram-rod',(px,-3.60,pz),.11,.081,.1325,(0,1,0),'steel','wheelset-press')
    parts.tube('press/pusher-collar',(px,-3.4675,pz),.14,.081,.03,(0,1,0),'orange','wheelset-press')
    parts.tube('press/fixed-reaction-collar',(px,-1.7625,pz),.15,.081,.12,(0,1,0),'steel','wheelset-press')
    parts.tube('press/fixed-reaction-spacer',(px,-1.6425,pz),.15,.081,.3425,(0,1,0),'dark_steel','wheelset-press')
    parts.box('press/pressure-and-curve-logging',(5.1,-4.2,-.73),(.65,.7,1.2),'teal',group='wheelset-press')
    parts.pipe('press/hose-supply',[(5.1,-4.,.1),(4.9,-4.5,.4),(4.,-4.1,1.2)],.02)
    # A small parts bench represents replacement modules, not installed spring
    # or suspension geometry absent from the source stock.
    parts.box('service-bench/top',(-5.7,-4.6,.02),(2.6,.8,.09),'wood',group='inspection-and-repair')
    for i,x in enumerate((-5.6,-3.35)):
        for j,y in enumerate((-4.5,-3.95)):
            parts.box(f'service-bench/leg/{i}/{j}',(x,y,-.73),(.09,.09,.75),'teal',group='inspection-and-repair')
    for i in range(4):
        bx=-5.35+i*.55
        parts.tube(f'service-bench/bearing-cartridge/{i}',(bx,-4.2,.11),.14,.078,.16,material='steel',group='proposed-bearing-interfaces',basis='proposed-envelope')
        for j in range(4):
            a=j*pi/2
            _bolt(parts,f'service-bench/bearing-fastener/{i}/{j}',bx+.118*cos(a),-4.2+.118*sin(a),.11,radius=.008,length=.05,group='proposed-bearing-interfaces')
    return dict(id='rail-running-gear',title='Fabricate, fit and inspect locally',
        subtitle='Bought rolled rail; local finishing, jigs and passive running gear',
        entities=parts.entities,
        labels=[
            dict(text='Bought 60E1 stock; local weld and QA',anchor_m=[-4.,5.3,.65],side='left',order=0),
            dict(text='1,435 mm gauge; fastening jigs',anchor_m=[1.,3.,0.],side='right',order=0),
            dict(text='Rail profile and ultrasonic inspection',anchor_m=[5.35,3.7,.12],side='right',order=1),
            dict(text='Passive bogie and brake fit-up',anchor_m=[0.,-2.5,.55],side='left',order=1),
            dict(text='Wheelset press-fit and force logging',anchor_m=[4.,-2.6,1.2],side='right',order=2),
            dict(text='Repairable bearing and wear modules',anchor_m=[-4.5,-4.2,.25],side='left',order=2)],
        camera=dict(direction=[1.,-1.25,1.0],target_m=[0.,.6,.15],ortho_scale_m=20.5),
        metrics=dict(rail_panel_length_m=12.,rail_centres_m=1.507,nominal_track_gauge_m=1.435,
            maximum_fastening_pitch_m=.6,fastening_sets=42,fastening_anchors=84,clips=84,rail_pads=42,
            rail_profile_name='60E1-reference',nominal_rail_mass_kg_m=60.21,
            nominal_rail_section_area_m2=.007670,display_profile_area_m2=_polygon_area(_RAIL_PROFILE),
            rail_display_profile_qualified=False,rail_contact_model_qualified=False,
            source_bogie_stock_parts=30,source_bogie_count=1,source_bogie_axles=2,source_bogie_wheels=4,
            source_bogie_new_wheel_diameter_m=.76,source_bogie_wheelbase_m=2.1,
            proposed_bearing_housings=4,proposed_bearing_retention_fasteners=16,
            proposed_bearing_housings_installed=False,
            proposed_caliper_envelopes=4,proposed_caliper_retention_fasteners=8,
            separate_press_process_sample_wheelsets=1,press_capacity_N=None,
            source_wheel_centres_m=1.495,reference_rail_centres_m=1.507,
            installation_inventory_complete=False,qualified_braking_capacity_N=None,
            supplier_or_process_approved=False,production_shifts_per_day=2,hours_per_shift=8),
        assumptions=[
            'Scene is a proposed fabrication-floor layout. Rigid translations retain source component dimensions; repeated work samples are not additional installed vehicle stock.',
            'Source wheel centre spacing1.495m is retained exactly. Its tread/contact relationship to1.507m rail centres needs a proper wheel-profile and flange-clearance model.',
            'The sampled rail silhouette is a filtered raster-derived display envelope. Its nominal bounding dimensions and16.5mm straight web are referenced to manufacturer data; its area is reported separately from the76.70cm2 nominal quantity basis.',
            'Rounded rail/contact tolerances, cant, thermal fastening strategy, welding burn-off, fatigue, NDT acceptance and delivered rail grades remain unqualified.',
            'Rail panels are12m jig examples, not a selected transported or thermally locked panel length. Site rail installation and welded-rail stress management require their own method.',
            'Welding machine, copper clamp envelopes, press, proposed bearing/caliper interfaces and all hoses/fasteners are illustrative dimensional proposals; no machine capacity or process approval follows.',
            'Brake/suspension/axlebox stock remains incomplete. The unlocated bogie allowance is not converted to zero or counted a second time.',
            'Proposed bearing cartridges are parked on the repair bench: the source sideframes have no qualified axlebox openings or bearing interfaces. They are not falsely inserted through solid frame stock.',
            'Finite transport/lift/tool-access and removal sweeps have not been checked; datum jigs, inspection paths and accessible parked modules illustrate the intended sequence only.'],
        manufacturing_steps=[
            'Purchase traceable standard rolled rail and wheel/axle stock; retain actual material origin and certificates.',
            'Inspect rail profile and straightness; cut and prepare ends with explicit weld and trimming allowances.',
            'Use a qualified flash-butt weld process where required; finish the running surface and inspect the weld under an approved NDT procedure.',
            'Set rail pads, plates and fasteners on a surveyed jig; verify gauge, alignment and fastening process before route installation.',
            'Machine and inspect wheel/axle fits; record wheelset press force/displacement and bearing fit-up.',
            'Assemble passive bogie frames, independent brakes and service lines; inspect retention, clearance and repair access before qualification.'],
        reference_context={**_context(record),
            'manufacturing_layout_is_operating_installation':False,
            'rail_supplier_and_process_selected':False},**FLAGS)


def generate(root):
    root=Path(root)
    raw=(root/EVALUATION).read_bytes()
    record=json.loads(gzip.decompress(raw))
    result=dict(schema='osr-visual-family/1',family='fabrication',
        assemblies=[_vehicle(record),_shop(record)],sources=[EVALUATION,PRODUCER],
        source_sha256={EVALUATION:sha256(raw).hexdigest(),PRODUCER:sha256(Path(__file__).read_bytes()).hexdigest()},
        assumptions=['Source stock and proposed fabrication/process envelopes have separate identity, quantity and evidence scopes.'],
        references=[dict(title='60E1 technical profile, voestalpine',url=RAIL_DRAWING,
            use='Nominal geometry and curved display silhouette; factual profile dimensions only, not a released manufacturer drawing'),
            dict(title='European standard rail profile table, ArcelorMittal',url=RAIL_TABLE,
            use='60E1 nominal dimensions,76.70cm2 section and60.21kg/m mass')],**FLAGS)
    for assembly in result['assemblies']:
        ids=[p['id'] for p in assembly['entities']]
        if len(ids)!=len(set(ids)) or len(ids)>3000:raise ValueError('Bounded unique visual entity inventory required')
    return result


# Tessellated, symmetric DISPLAY envelope derived from the raster-only technical
# section. This is not an exact rail-contact or rolling-tolerance representation.
_RAIL_PROFILE = [
    [0.0000000000, 0.0000000000],
    [-0.0197033898, -0.0002118227],
    [-0.0241525424, -0.0019064039],
    [-0.0290254237, -0.0036009852],
    [-0.0314618644, -0.0052955665],
    [-0.0330508475, -0.0069901478],
    [-0.0341101695, -0.0086847291],
    [-0.0349576271, -0.0103793103],
    [-0.0351694915, -0.0120738916],
    [-0.0353813559, -0.0137684729],
    [-0.0360000000, -0.0143000000],
    [-0.0358050847, -0.0154630542],
    [-0.0359110169, -0.0171576355],
    [-0.0360169492, -0.0188522167],
    [-0.0361228814, -0.0205467980],
    [-0.0361228814, -0.0222413793],
    [-0.0362288136, -0.0239359606],
    [-0.0363347458, -0.0256305419],
    [-0.0364406780, -0.0273251232],
    [-0.0365466102, -0.0290197044],
    [-0.0365466102, -0.0307142857],
    [-0.0367584746, -0.0324088670],
    [-0.0367584746, -0.0341034483],
    [-0.0367584746, -0.0357980296],
    [-0.0353813559, -0.0374926108],
    [-0.0312500000, -0.0391871921],
    [-0.0266949153, -0.0408817734],
    [-0.0218220339, -0.0425763547],
    [-0.0173728814, -0.0442709360],
    [-0.0133474576, -0.0459655172],
    [-0.0123940678, -0.0476600985],
    [-0.0119703390, -0.0493546798],
    [-0.0114406780, -0.0510492611],
    [-0.0110169492, -0.0527438424],
    [-0.0106991525, -0.0544384236],
    [-0.0102754237, -0.0561330049],
    [-0.0099576271, -0.0578275862],
    [-0.0096398305, -0.0595221675],
    [-0.0094279661, -0.0612167488],
    [-0.0091101695, -0.0629113300],
    [-0.0088983051, -0.0646059113],
    [-0.0086864407, -0.0663004926],
    [-0.0084745763, -0.0679950739],
    [-0.0084745763, -0.0696896552],
    [-0.0082627119, -0.0713842365],
    [-0.0082627119, -0.0730788177],
    [-0.0080508475, -0.0747733990],
    [-0.0080508475, -0.0764679803],
    [-0.0080508475, -0.0781625616],
    [-0.0080508475, -0.0802807882],
    [-0.0082500000, -0.0819753695],
    [-0.0082500000, -0.0836699507],
    [-0.0082500000, -0.0853645320],
    [-0.0082500000, -0.0870591133],
    [-0.0082500000, -0.0887536946],
    [-0.0082500000, -0.0904482759],
    [-0.0082500000, -0.0921428571],
    [-0.0082500000, -0.0938374384],
    [-0.0082500000, -0.0955320197],
    [-0.0082500000, -0.0972266010],
    [-0.0082500000, -0.0989211823],
    [-0.0082500000, -0.1006157635],
    [-0.0082500000, -0.1023103448],
    [-0.0082500000, -0.1040049261],
    [-0.0082500000, -0.1056995074],
    [-0.0082500000, -0.1073940887],
    [-0.0080508475, -0.1090886700],
    [-0.0080508475, -0.1107832512],
    [-0.0080508475, -0.1126896552],
    [-0.0080508475, -0.1143842365],
    [-0.0080508475, -0.1160788177],
    [-0.0082627119, -0.1177733990],
    [-0.0082627119, -0.1194679803],
    [-0.0084745763, -0.1211625616],
    [-0.0084745763, -0.1228571429],
    [-0.0086864407, -0.1245517241],
    [-0.0088983051, -0.1262463054],
    [-0.0091101695, -0.1279408867],
    [-0.0093220339, -0.1296354680],
    [-0.0096398305, -0.1313300493],
    [-0.0099576271, -0.1330246305],
    [-0.0102754237, -0.1347192118],
    [-0.0105932203, -0.1364137931],
    [-0.0109110169, -0.1381083744],
    [-0.0112288136, -0.1398029557],
    [-0.0118644068, -0.1414975369],
    [-0.0123940678, -0.1431921182],
    [-0.0131355932, -0.1448866995],
    [-0.0161016949, -0.1465812808],
    [-0.0207627119, -0.1482758621],
    [-0.0256355932, -0.1499704433],
    [-0.0300847458, -0.1516650246],
    [-0.0347457627, -0.1533596059],
    [-0.0396186441, -0.1550541872],
    [-0.0435381356, -0.1567487685],
    [-0.0471398305, -0.1584433498],
    [-0.0677966102, -0.1601379310],
    [-0.0733050847, -0.1618325123],
    [-0.0746822034, -0.1635270936],
    [-0.0747881356, -0.1652216749],
    [-0.0747881356, -0.1669162562],
    [-0.0747881356, -0.1686108374],
    [-0.0747881356, -0.1703054187],
    [-0.0739406780, -0.1713645320],
    [-0.0750000000, -0.1720000000],
    [0.0750000000, -0.1720000000],
    [0.0739406780, -0.1713645320],
    [0.0747881356, -0.1703054187],
    [0.0747881356, -0.1686108374],
    [0.0747881356, -0.1669162562],
    [0.0747881356, -0.1652216749],
    [0.0746822034, -0.1635270936],
    [0.0733050847, -0.1618325123],
    [0.0677966102, -0.1601379310],
    [0.0471398305, -0.1584433498],
    [0.0435381356, -0.1567487685],
    [0.0396186441, -0.1550541872],
    [0.0347457627, -0.1533596059],
    [0.0300847458, -0.1516650246],
    [0.0256355932, -0.1499704433],
    [0.0207627119, -0.1482758621],
    [0.0161016949, -0.1465812808],
    [0.0131355932, -0.1448866995],
    [0.0123940678, -0.1431921182],
    [0.0118644068, -0.1414975369],
    [0.0112288136, -0.1398029557],
    [0.0109110169, -0.1381083744],
    [0.0105932203, -0.1364137931],
    [0.0102754237, -0.1347192118],
    [0.0099576271, -0.1330246305],
    [0.0096398305, -0.1313300493],
    [0.0093220339, -0.1296354680],
    [0.0091101695, -0.1279408867],
    [0.0088983051, -0.1262463054],
    [0.0086864407, -0.1245517241],
    [0.0084745763, -0.1228571429],
    [0.0084745763, -0.1211625616],
    [0.0082627119, -0.1194679803],
    [0.0082627119, -0.1177733990],
    [0.0080508475, -0.1160788177],
    [0.0080508475, -0.1143842365],
    [0.0080508475, -0.1126896552],
    [0.0080508475, -0.1107832512],
    [0.0080508475, -0.1090886700],
    [0.0082500000, -0.1073940887],
    [0.0082500000, -0.1056995074],
    [0.0082500000, -0.1040049261],
    [0.0082500000, -0.1023103448],
    [0.0082500000, -0.1006157635],
    [0.0082500000, -0.0989211823],
    [0.0082500000, -0.0972266010],
    [0.0082500000, -0.0955320197],
    [0.0082500000, -0.0938374384],
    [0.0082500000, -0.0921428571],
    [0.0082500000, -0.0904482759],
    [0.0082500000, -0.0887536946],
    [0.0082500000, -0.0870591133],
    [0.0082500000, -0.0853645320],
    [0.0082500000, -0.0836699507],
    [0.0082500000, -0.0819753695],
    [0.0080508475, -0.0802807882],
    [0.0080508475, -0.0781625616],
    [0.0080508475, -0.0764679803],
    [0.0080508475, -0.0747733990],
    [0.0082627119, -0.0730788177],
    [0.0082627119, -0.0713842365],
    [0.0084745763, -0.0696896552],
    [0.0084745763, -0.0679950739],
    [0.0086864407, -0.0663004926],
    [0.0088983051, -0.0646059113],
    [0.0091101695, -0.0629113300],
    [0.0094279661, -0.0612167488],
    [0.0096398305, -0.0595221675],
    [0.0099576271, -0.0578275862],
    [0.0102754237, -0.0561330049],
    [0.0106991525, -0.0544384236],
    [0.0110169492, -0.0527438424],
    [0.0114406780, -0.0510492611],
    [0.0119703390, -0.0493546798],
    [0.0123940678, -0.0476600985],
    [0.0133474576, -0.0459655172],
    [0.0173728814, -0.0442709360],
    [0.0218220339, -0.0425763547],
    [0.0266949153, -0.0408817734],
    [0.0312500000, -0.0391871921],
    [0.0353813559, -0.0374926108],
    [0.0367584746, -0.0357980296],
    [0.0367584746, -0.0341034483],
    [0.0367584746, -0.0324088670],
    [0.0365466102, -0.0307142857],
    [0.0365466102, -0.0290197044],
    [0.0364406780, -0.0273251232],
    [0.0363347458, -0.0256305419],
    [0.0362288136, -0.0239359606],
    [0.0361228814, -0.0222413793],
    [0.0361228814, -0.0205467980],
    [0.0360169492, -0.0188522167],
    [0.0359110169, -0.0171576355],
    [0.0358050847, -0.0154630542],
    [0.0360000000, -0.0143000000],
    [0.0353813559, -0.0137684729],
    [0.0351694915, -0.0120738916],
    [0.0349576271, -0.0103793103],
    [0.0341101695, -0.0086847291],
    [0.0330508475, -0.0069901478],
    [0.0314618644, -0.0052955665],
    [0.0290254237, -0.0036009852],
    [0.0241525424, -0.0019064039],
    [0.0197033898, -0.0002118227],
]
