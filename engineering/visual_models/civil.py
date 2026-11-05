"""Source-dimensioned precast beam and proposed manufacturing/erection layouts.

The six concrete solids reproduce the selected box-beam stock. Plant, support,
reinforcement routing and temporary works are illustrative engineering envelopes;
they are not a lifting plan, pressure/rating certificate or construction release.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from math import ceil, pi, sqrt
from pathlib import Path

PRODUCER = 'engineering/visual_models/civil.py'
RECORD = 'docs/design-engine/current/evaluation.json.gz'
BIM = 'engineering/station_rail/bim.py'
CIVIL = 'engineering/station_rail/civil.py'
SOURCE = RECORD + '#/civil/selected_reference'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
REFERENCES = [
    dict(title='FHWA: Prefabricated Bridge Elements and Systems connection details',
         url='https://www.fhwa.dot.gov/bridge/prefab/if09010/01a.cfm',
         scope='Assembly plans, fit-up jigs, lifting hardware and temporary support; not acceptance of this design.'),
    dict(title='Caltrans: Reinforced Concrete Construction Manual, Chapter 8',
         url='https://dot.ca.gov/-/media/dot-media/programs/engineering/documents/structureconstruction/rcm/sc-rcm-compiled.pdf',
         scope='Precast girder transport, lifting and temporary bracing guidance; site-specific engineering remains necessary.'),
    dict(title='Freyssinet: Precast segmental erection methods',
         url='https://www.freyssinet.com/solution/build/bridge-deck-construction/precast-segmental-erection/',
         scope='Industry examples of gantry and precast-beam erection; the proposed whole-span gantry is a separate layout hypothesis.'),
]


def _entity(rows, name, shape, material, group, basis, source, at=(0, 0, 0), **kw):
    value = dict(id=name, shape=shape, material=material, group=group, basis=basis,
                 source=source, at_m=list(at), render_offset_m=[0., 0., 0.], **kw)
    rows.append(value)
    return value


def _box(rows, name, at, size, material='steel', group='temporary-works',
         basis='proposed-envelope', source='Explicit illustrative layout dimensions', **kw):
    return _entity(rows, name, 'box', material, group, basis, source, at,
                   size_m=list(size), **kw)


def _cyl(rows, name, at, radius, length, axis=(0, 0, 1), material='steel',
         group='temporary-works', basis='proposed-envelope',
         source='Explicit illustrative layout dimensions', **kw):
    return _entity(rows, name, 'cylinder', material, group, basis, source, at,
                   radius_m=radius, length_m=length, axis=list(axis), **kw)


def _link(rows, name, start, end, radius=.04, material='orange', group='temporary-works',
          basis='proposed-envelope', source='Explicit illustrative member centreline'):
    vector = [b-a for a, b in zip(start, end)]
    length = sqrt(sum(v*v for v in vector))
    return _cyl(rows, name, start, radius, length, [v/length for v in vector],
                material, group, basis, source)


def _pipe(rows, name, path, radius, material='steel', group='tooling',
          basis='illustrative-tooling', source='Proposed route envelope; not a qualified connection'):
    return _entity(rows, name, 'pipe', material, group, basis, source,
                   path_m=[list(p) for p in path], radius_m=radius)


def _label(text, anchor, side, order):
    return dict(text=text, anchor_m=list(anchor), side=side, order=order)


def _beam(rows, prefix, s, x=0., y=0., top=-.192, explode=False):
    """Disjoint source concrete stock with an explicitly derived assembly placement."""
    d = s['section']['dimensions'];L=s['span_m'];B=d['outer_width_m'];H=d['depth_m']
    wall=d['wall_m'];flange=d['flange_m'];dia=s['diaphragm_definition']
    pieces = [
        ('bottom', (x, y-B/2, top-H), (L, B, flange)),
        ('top', (x, y-B/2, top-flange), (L, B, flange)),
        ('near-web', (x, y-B/2, top-H+flange), (L, wall, H-2*flange)),
        ('far-web', (x, y+B/2-wall, top-H+flange), (L, wall, H-2*flange)),
    ]
    for i in range(dia['quantity']):
        dx=0. if i==0 else L-dia['thickness_m']
        pieces.append((f'diaphragm-{i}',(x+dx,y-dia['clear_width_m']/2,top-H+flange),
                       (dia['thickness_m'],dia['clear_width_m'],dia['height_m'])))
    volume=0.
    for name, at, size in pieces:
        obj=_box(rows,prefix+'-'+name,at,size,'concrete',prefix,'source-geometry',
                 SOURCE+'/section and diaphragm_definition; stock translated for the stated assembly datum')
        volume+=size[0]*size[1]*size[2]
        if explode and name=='top':obj['render_offset_m']=[0.,0.,2.6]
        if explode and name=='near-web':obj['render_offset_m']=[0.,-.72,0.]
    if abs(volume-s['concrete_m3'])>1e-8:
        raise ValueError('Visual concrete stock does not reproduce selected beam volume')
    return volume


def _rails(rows, prefix, L, x=0., y=0., head=0.):
    """Equivalent-area 60E1 blocks, with the canonical width/height and mass."""
    foot, hwid, tfoot, hhead = .15, .072, .016, .040
    hweb=.172-tfoot-hhead;web=(60.21/7850.-foot*tfoot-hwid*hhead)/hweb
    for sign in (-1,1):
        centre=y+sign*.7535
        for name,at,size in (
            ('foot',(x,centre-foot/2,head-.172),(L,foot,tfoot)),
            ('web',(x,centre-web/2,head-.172+tfoot),(L,web,hweb)),
            ('head',(x,centre-hwid/2,head-hhead),(L,hwid,hhead))):
            _box(rows,f'{prefix}-{sign}-{name}',at,size,'steel','installed-rails',
                 'source-geometry',BIM+'#parts: equivalent-area 60E1 blocks, no contact fillets')
        count=ceil(L/.6)+1
        for i in range(count):
            at=x+.15+(L-.30)*i/(count-1)
            _box(rows,f'{prefix}-{sign}-pad-{i}',(at-.10,centre-.12,head-.192),
                 (.20,.24,.008),'rubber','rail-fastenings','derived-layout',
                 'Source fastener count; proposed 150mm end margin and pad envelope')
            _box(rows,f'{prefix}-{sign}-plate-{i}',(at-.10,centre-.12,head-.184),
                 (.20,.24,.012),'dark_steel','rail-fastenings','proposed-envelope',
                 'Proposed baseplate envelope; source 8kg/set remains an accounting allowance')
            for j in (-1,1):
                _cyl(rows,f'{prefix}-{sign}-anchor-{i}-{j}',
                     (at+j*.055,centre+j*.10,head-.304),.010,.145,
                     material='steel',group='rail-fastenings',basis='proposed-envelope',
                     source='Two anchors/set from source count; dimensions and embedment unqualified')
                _box(rows,f'{prefix}-{sign}-clip-{i}-{j}',
                     (at-.025,centre+j*.075-.010,head-.156),(.05,.020,.025),
                     'orange','rail-fastenings','proposed-envelope','Replaceable clip envelope; not a released rail fastening')


def _supports(rows, positions):
    # Reference railhead is0. Bearing seat and pier geometry are layout hypotheses.
    cap_top=-1.792;positions=list(positions)
    for i,x in enumerate(positions):
        _box(rows,f'foundation-{i}',(x-2.,-2.,-10.65),(4.,4.,.80),
             'concrete','proposed-substructure','proposed-envelope',
             'Exposed 4x4x0.8m footing envelope; not site-specific geotechnical design')
        _box(rows,f'pier-{i}',(x-.60,-.75,-9.85),(1.2,1.5,7.358),
             'concrete','proposed-substructure','proposed-envelope',
             'Pier envelope; reactions, lateral/seismic stability and reinforcement unresolved')
        _box(rows,f'headstock-{i}',(x-.9,-2.1,cap_top-.70),(1.8,4.2,.70),
             'concrete','proposed-substructure','proposed-envelope',
             'Headstock envelope including possible temporary-plant bearing positions; not verified')
        # Each beam has its own seats fully inside its stock ends. Interior
        # caps carry two pairs; end caps only the inward pair. This changes
        # the proposed support spacing, not any source analytical result.
        offsets=([-.30] if i>0 else [])+([.30] if i<len(positions)-1 else [])
        for k,offset in enumerate(offsets):
            for j,y in enumerate((-.65,.65)):
                _box(rows,f'bearing-{i}-{k}-{j}',(x+offset-.20,y-.16,cap_top),(.40,.32,.20),
                     'rubber','bearings','proposed-envelope',
                     'Separate per-beam bearing envelope, centres0.30m inside stock ends; no accepted bearing schedule, capacity or source-analysis inheritance')
    _box(rows,'working-surface',(-7.,-16.,-10.85),(56.,30.,.20),
         'ground','site-context','proposed-envelope',
         'Visual working-plane/exposed-foundation datum, not surveyed ground or a crane-bearing design')


def _access(rows, x0, length, y=1.35, top=-.15, prefix='access'):
    _box(rows,prefix+'-deck',(x0,y-.25,top-.12),(length,.50,.12),
         'steel','temporary-access','proposed-envelope','Proposed protected erection access; load/cantilever design pending')
    for side in (-1,1):
        yy=y+side*.25
        for i in range(ceil(length/2)+1):
            xx=x0+length*i/ceil(length/2)
            _cyl(rows,f'{prefix}-post-{side}-{i}',(xx,yy,top),.022,1.1,
                 material='orange',group='temporary-access')
        for z in (.55,1.10):
            _link(rows,f'{prefix}-rail-{side}-{z}',(x0,yy,top+z),(x0+length,yy,top+z),
                  .018,'orange','temporary-access')


def _braces(rows, x, prefix, inward):
    # Both sides connect the headstock to the existing span, not the empty bay.
    # Bracket overlap communicates attachment only; anchors/capacity are not designed.
    for sign in (-1,1):
        _link(rows,f'{prefix}-brace-{sign}',(x+inward*.75,sign*1.5,-1.80),
              (x+inward*2.5,sign*.93,-.25),.035,'orange','temporary-bracing')
        _box(rows,f'{prefix}-bracket-{sign}',(x+inward*2.5-.13,sign*.93-.13,-.30),
             (.26,.26,.12),'steel','temporary-bracing')


def _lifting_frame(rows, x, y, beam_top, frame_z, hook_z, prefix='lift'):
    # Four vertical slings to two longitudinal lift stations at0.2L/0.8L.
    for side in (-1,1):
        yy=y+side*.83
        _link(rows,f'{prefix}-long-chord-{side}',(x+4,yy,frame_z),
              (x+16,yy,frame_z),.10,'orange','lifting-frame')
    for xx in (4.,10.,16.):
        _link(rows,f'{prefix}-cross-{xx}',(x+xx,y-.83,frame_z),
              (x+xx,y+.83,frame_z),.085,'orange','lifting-frame')
    for i,xx in enumerate((4.,16.)):
        for j,side in enumerate((-1,1)):
            yy=y+side*.83
            _link(rows,f'{prefix}-sling-{i}-{j}',(x+xx,yy,frame_z),
                  (x+xx,yy,beam_top+.08),.028,'dark_steel','rigging')
            _box(rows,f'{prefix}-pick-shoe-{i}-{j}',(x+xx-.17,yy-.08,beam_top),
                 (.34,.16,.08),'orange','proposed-lift-interfaces','proposed-envelope',
                 'Illustrative lift shoe position at0.2L/0.8L near webs; concrete breakout and anchors not designed')
            _link(rows,f'{prefix}-upper-sling-{i}-{j}',(x+10,y,hook_z),
                  (x+xx,yy,frame_z),.027,'dark_steel','rigging')
    _box(rows,prefix+'-hook-block',(x+9.76,y-.20,hook_z),(.48,.40,.70),
         'dark_steel','rigging')


def _lattice(rows, name, start, end, width, depth, bays=6, material='orange'):
    # Lattice box with vertical faces and x/y-independent local axes.
    delta=[b-a for a,b in zip(start,end)];length=sqrt(sum(v*v for v in delta))
    u=[v/length for v in delta]
    lateral=[1.,0.,0.] if abs(u[0])<.8 else [0.,1.,0.]
    norm=[u[1]*lateral[2]-u[2]*lateral[1],u[2]*lateral[0]-u[0]*lateral[2],u[0]*lateral[1]-u[1]*lateral[0]]
    nlen=sqrt(sum(v*v for v in norm));normal=[v/nlen for v in norm]
    def point(t,a,b):return [start[k]+t*delta[k]+a*width/2*lateral[k]+b*depth/2*normal[k] for k in range(3)]
    for a in (-1,1):
        for b in (-1,1):_link(rows,f'{name}-chord-{a}-{b}',point(0,a,b),point(1,a,b),.085,material,'erection-plant')
    for i in range(bays):
        t0=i/bays;t1=(i+1)/bays
        for side in (-1,1):
            _link(rows,f'{name}-web-a-{i}-{side}',point(t0,side,-1),point(t1,side,1),.035,material,'erection-plant')
            _link(rows,f'{name}-web-b-{i}-{side}',point(t0,-1,side),point(t1,1,side),.035,material,'erection-plant')
    return point


def _metrics(s, route):
    lift=sum(s[k] for k in ('concrete_mass_kg','reinforcement_kg','prestress_kg','prestress_anchorage_kg'))
    weight=lift*9.80665;L=s['span_m'];q=weight/L;a=.2*L
    return dict(selected_beam_family=s['family'],span_m=L,
        source_stock_length_m=L,source_analytical_span_m=L,
        proposed_bearing_centre_spacing_m=L-.60,
        source_analytical_results_apply_to_proposed_bearing_layout=False,
        source_concrete_volume_m3=s['concrete_m3'],source_beam_width_m=s['section']['dimensions']['outer_width_m'],
        source_beam_depth_m=s['section']['depth_m'],proposed_pad_thickness_m=.008,
        proposed_baseplate_thickness_m=.012,derived_installed_concrete_top_m=-.192,source_strand_count=s['prestress_strands'],
        source_reinforcement_allowance_kg=s['reinforcement_kg'],counted_bare_beam_stock_kg=lift,
        excluded_from_lift=['running rails','direct fasteners','actual rigging','unresolved lifting attachments'],
        source_counted_installed_span_stock_kg=s['total_counted_span_mass_kg'],
        source_minimum_hook_capacity_kg_hypothesis=s['construction']['minimum_crane_hook_capacity_kg_hypothesis'],
        source_hook_allowance_fraction_hypothesis=s['construction']['rigging_fraction_hypothesis'],
        actual_crane_capacity_at_radius_kg=None,actual_rigging_mass_kg=None,
        illustrative_lift=dict(lift_station_x_m=[a,L-a],equal_station_reaction_N=weight/2,
            equal_four_point_vertical_share_N=weight/4,
            overhang_hogging_Nm=q*a*a/2,between_pick_sagging_Nm=q*L*L/8-q*a*L/2,
            scope='Uniform counted stock, static symmetric vertical lift only; sling angles, dynamics, connections and lateral stability unresolved'),
        source_load_case=s['load_case'],source_deflection_upper_bound_m=s['deflection_upper_bound_m'],
        source_analytical_engineering_screen=s['engineering_screen'],
        foundation_envelope_m=[4.,4.,.8],foundation_reinforcement_or_soil_verified=False,
        construction_route=route,production_shifts_per_day=2,civil_shifts_per_day=2,
        erection_cycle_h=None,factory_cycle_h=None,route_installed_cost=None,
        crane_ground_bearing_verified=False,temporary_stability_verified=False,
        relative_rail_vehicle_stator_clearance_verified=False,complete_installed_mass=False,
        **FLAGS)


def _context(record,s):
    keys=('candidate_id','body_candidate_id','support_component_id','propulsion_component_id','selection_id','evaluation_id')
    return dict(reference_candidate_ids={k:record[k] for k in keys},
        civil_component_id=record['civil']['civil_component_id'],civil_alternative_id=s['alternative_id'],
        scope='Selected20m concrete stock with separate proposed construction/tooling envelopes',
        geometry_adopted=False,**FLAGS)


def _common_assumptions():
    return [
        'The six concrete stock shapes reproduce source dimensions and volume. Installed concrete is translated20mm below the canonical no-fastener BIM datum to fit the explicitly proposed8mm pad and12mm baseplate stack beneath railhead0. Plant, foundations, bearings, access and lifting interfaces are proposed envelopes.',
        'Each20m stock beam has proposed bearing centres0.30m inside its ends, giving19.4m bearing-centre spacing. Interior headstocks carry separate seats for adjacent beams. This is not an accepted bearing schedule. Source20m analytical stress/deflection results have not been recalculated for, and do not establish performance of, this proposed seating geometry.',
        'The59.183272t counted bare beam excludes rail, fasteners, actual rigging and unresolved attachments. The source25percent hook allowance is a planning hypothesis, not a crane rating.',
        'Lift points at0.2L/0.8L are visual layout hypotheses. Concrete release strength, prestress transfer, anchor breakout, shear, torsion, lateral roll stability, wind and dynamic lifting are not verified.',
        'Ground-level working plane exposes footings for clarity. No soil survey, utility clearance, bearing, settlement, seismic, uplift or actual foundation quantities are established.',
        'Track is installed only on the completed supported span. Actual60E1 contact radii, rail cant, joints, fastening stiffness and anchorage qualification remain open.',
        'Moving-load and deflection figures belong to the existing analytical source case. Relative rail, vehicle and station-stator deformation, torsion and interface gaps need coupled checks.',
        'Two8hour shifts are planning inputs. No factory or erection cycle time, workforce capacity or installed-cost advantage is established by the illustration.',
    ]


def _crane(record,s):
    rows=[];L=s['span_m'];_supports(rows,(0.,L,2*L))
    _beam(rows,'installed-beam',s);_rails(rows,'installed-rail',L);_access(rows,0.,L)
    _braces(rows,0.,'seated-end-0',1);_braces(rows,L,'seated-end-1',-1)
    x=L;top=3.0;_beam(rows,'suspended-beam',s,x=x,top=top)
    _lifting_frame(rows,x,0.,top,5.6,9.0)
    # Crawler tracks run alongy and rest on a visible proposed working mat.
    _box(rows,'crane-working-mat',(25.,-14.,-10.65),(10.,8.,.20),'wood','crane-working-pad')
    for i,xx in enumerate((27.4,32.0)):
        _box(rows,f'crawler-track-{i}',(xx,-13.,-10.45),(1.25,6.0,.85),'dark_steel','crawler')
        for j in range(16):
            _box(rows,f'crawler-shoe-{i}-{j}',(xx-.03,-13.+j*6/16,-10.47),(1.31,.12,.12),
                 'steel','crawler')
        for j in range(5):
            _cyl(rows,f'crawler-wheel-{i}-{j}',(xx,-12.45+j*1.10,-10.0),.32,1.25,(1,0,0),'steel','crawler')
    _box(rows,'crawler-centre-frame',(28.3,-11.8,-9.6),(4.1,4.7,.50),'teal','crawler')
    _cyl(rows,'crawler-slew-bearing',(30.,-9.7,-9.1),1.25,.35,material='dark_steel',group='crawler')
    _box(rows,'crane-machinery-house',(28.1,-12.,-8.75),(3.5,3.4,1.75),'teal','crawler')
    _box(rows,'crane-counterweight',(28.0,-13.2,-8.7),(4.0,1.25,1.65),'dark_steel','crawler')
    _box(rows,'crane-cab',(26.9,-9.8,-8.6),(1.3,1.5,1.75),'white','crawler')
    _box(rows,'crane-cab-glazing',(26.86,-9.65,-8.24),(.04,1.16,.96),'glass','crawler')
    _lattice(rows,'crane-lattice-boom',(30.,-8.8,-8.0),(30.,0.,11.0),1.8,1.5,8)
    _link(rows,'main-hoist-rope',(30.,0.,11.0),(30.,0.,9.70),.028,'dark_steel','rigging')
    _link(rows,'boom-backstay-a',(30.,-11.9,-7.2),(29.1,0.,11.0),.025,'steel','rigging')
    _link(rows,'boom-backstay-b',(30.,-11.9,-7.2),(30.9,0.,11.0),.025,'steel','rigging')
    # Separate delivered rails await installation after the newspan is seated.
    _rails_stock(rows,25.,4.6,-9.0)
    return dict(id='viaduct-crane',title='Precast span erection',
        subtitle='20m whole-span lift; rails fitted after seating and temporary restraint',
        entities=rows,labels=[
            _label('20 m counted beam stock /59.2 t',(30.,0.,3.),'right',0),
            _label('Proposed four-point lifting frame',(30.,0.,5.6),'right',1),
            _label('Crane chart at radius still required',(30.,-9.7,-7.5),'left',0),
            _label('Bearings and temporary restraint',(20.,.65,-1.55),'left',1),
            _label('Rails installed after erection',(9.,-.7535,0.),'right',2),
            _label('Footings shown exposed /site design open',(40.,0.,-9.8),'left',2)],
        camera=dict(direction=[1.,-1.35,.80],target_m=[20.,-1.8,-.3],ortho_scale_m=49.),
        metrics=_metrics(s,'ground crawler crane'),assumptions=_common_assumptions()+[
            'Crane is an unbranded geometric envelope, not a selected or rated machine. Backstay, counterweight and mats have not been sized.',
            'The completed span has70fastener sets and140anchors. Proposed150mm end offsets retain a maximum pitch below0.6m; edge distances and fastening design remain unqualified.'],
        reference_context=_context(record,s))


def _rails_stock(rows,x,y,z):
    for j in range(3):
        xx=x+j*7
        _box(rows,f'rail-stock-support-{x}-{j}',(xx-.25,y-.65,z-.422),(.50,1.30,.25),
             'wood','delivered-rail-stock')
        for sign in (-1,1):
            _box(rows,f'rail-stock-leg-{x}-{j}-{sign}',(xx-.09,y+sign*.50-.09,-10.65),
                 (.18,.18,z-.422+10.65),'wood','delivered-rail-stock')
        _link(rows,f'rail-stock-rack-brace-{x}-{j}',(xx,y-.50,-10.60),
              (xx,y+.50,z-.422),.022,'steel','delivered-rail-stock')
    _rails_plain(rows,'delivered-stock',20.,x,y,z)


def _rails_plain(rows,prefix,L,x,y,head):
    # Two equivalent-area reference rails, no mounted fasteners on delivered stock.
    foot,hwid,tfoot,hhead=.15,.072,.016,.040
    hweb=.172-tfoot-hhead;web=(60.21/7850.-foot*tfoot-hwid*hhead)/hweb
    for sign in (-1,1):
        c=y+sign*.22
        for name,at,size in (
            ('foot',(x,c-foot/2,head-.172),(L,foot,tfoot)),
            ('web',(x,c-web/2,head-.172+tfoot),(L,web,hweb)),
            ('head',(x,c-hwid/2,head-hhead),(L,hwid,hhead))):
            _box(rows,f'{prefix}-{sign}-{name}',at,size,'steel','delivered-rail-stock',
                 'source-geometry',BIM+'#parts: equivalent-area rail; delivered stock spacing is proposed')


def _delivery_trolley(rows):
    """Empty proposed rail carrier; no carrying capacity or stage-load approval."""
    for sign in (-1,1):
        _box(rows,f'delivery-long-frame-{sign}',(.8,sign*.53-.07,.55),
             (16.4,.14,.22),'dark_steel','delivery-trolley','proposed-envelope',
             'Empty proposed beam carrier on completed rails; loaded axle/bridge capacity unresolved')
    for i,x in enumerate((2.,6.,12.,16.)):
        _cyl(rows,f'delivery-axle-{i}',(x,-.90,.30),.042,1.8,(0,1,0),
             'steel','delivery-trolley','proposed-envelope')
        for sign in (-1,1):
            _cyl(rows,f'delivery-wheel-{i}-{sign}',(x,sign*.7535-.075,.30),.30,.15,
                 (0,1,0),'dark_steel','delivery-trolley','proposed-envelope',
                 'Illustrative steel wheel envelope at reference rail centres; actual contact/profile not qualified')
            _box(rows,f'delivery-spring-{i}-{sign}',(x-.12,sign*.53-.10,.40),
                 (.24,.20,.15),'steel','delivery-trolley')
        _box(rows,f'delivery-cross-frame-{i}',(x-.08,-.66,.55),(.16,1.32,.22),
             'dark_steel','delivery-trolley')
    for i,x in enumerate((4.,14.)):
        _box(rows,f'delivery-load-saddle-{i}',(x-.30,-.95,.77),(.60,1.9,.15),
             'wood','delivery-trolley','proposed-envelope',
             'Empty proposed loading saddle; transport supports and dynamic restraint require design')


def _gantry(record,s):
    rows=[];L=s['span_m'];_supports(rows,(0.,L,2*L))
    _beam(rows,'installed-beam',s);_rails(rows,'installed-rail',L);_access(rows,0.,L)
    _braces(rows,L,'seated-end',-1)
    _beam(rows,'suspended-beam',s,x=L,top=2.45)
    _delivery_trolley(rows)
    for sign in (-1,1):
        yy=sign*1.7
        _lattice(rows,f'gantry-main-{sign}',(-4.,yy,4.8),(44.,yy,4.8),.55,1.40,12,'teal')
        for i,xx in enumerate((0.,L,2*L)):
            _box(rows,f'gantry-foot-{sign}-{i}',(xx-.38,yy-.30,-1.792),(.76,.60,.20),
                 'steel','gantry-temporary-support')
            _box(rows,f'gantry-leg-{sign}-{i}',(xx-.20,yy-.20,-1.592),(.40,.40,5.692),
                 'orange','gantry-temporary-support')
            _link(rows,f'gantry-knee-{sign}-{i}',(xx,yy,3.1),(xx,yy-sign*.60,4.1),
                  .07,'orange','gantry-temporary-support')
    for i,xx in enumerate((0.,L,2*L)):
        _box(rows,f'gantry-portal-{i}',(xx-.25,-2.0,4.0),(.50,4.,.35),
             'orange','gantry-temporary-support')
    for i,xx in enumerate((L+4.,L+16.)):
        _box(rows,f'hoist-transverse-trolley-{i}',(xx-.50,-2.0,5.62),(1.0,4.0,.45),
             'orange','travelling-hoists')
        _box(rows,f'hoist-drive-{i}',(xx-.45,-.38,6.07),(.90,.76,.50),'dark_steel','travelling-hoists')
        for sign in (-1,1):
            _cyl(rows,f'hoist-wheel-{i}-{sign}',(xx,sign*1.7-.12,5.6),.20,.24,(0,1,0),
                 'steel','travelling-hoists')
            _link(rows,f'hoist-vertical-{i}-{sign}',(xx,sign*.72,5.60),
                  (xx,sign*.72,2.55),.025,'dark_steel','rigging')
            _box(rows,f'gantry-lift-shoe-{i}-{sign}',(xx-.16,sign*.72-.08,2.45),
                 (.32,.16,.10),'orange','proposed-lift-interfaces')
    return dict(id='viaduct-gantry',title='Alternative: overhead launching gantry',
        subtitle='The same20m beam; temporary pier/gantry reactions require their own design',
        entities=rows,labels=[
            _label('Two travelling hoists /bare beam',(30.,0.,2.45),'right',0),
            _label('Reusable overhead erection plant',(28.,-1.7,4.8),'left',0),
            _label('Temporary reactions enter headstocks',(40.,1.7,-1.57),'right',1),
            _label('Deck delivery /plant load check required',(10.,0.,.75),'left',1),
            _label('Completed span then rail installation',(9.,-.7535,0.),'left',2),
            _label('Site-specific foundations remain open',(0.,0.,-9.8),'right',2)],
        camera=dict(direction=[1.,-1.3,.8],target_m=[20.,0.,-.1],ortho_scale_m=49.),
        metrics=_metrics(s,'overhead whole-span launching gantry'),
        assumptions=_common_assumptions()+[
            'The gantry is an alternative to the ground crane, not additional mandatory plant. Its whole-span lift is separate from segmental balanced-cantilever construction.',
            'Three paired temporary support stations, portal knees and travelling hoists are proposed geometry. Pier-head local stress, gantry dead load, uplift, lateral stability and launching stages need independent checks.',
            'An empty rail delivery trolley indicates supply from the completed deck. Beam transport, trolley axle loads, gantry travel and combined temporary loading on the completed span have not been verified.',
            'No crane/gantry capital cost or cycle-time advantage is assigned. Repeated spans may amortise plant; actual access, mobilisation and production rates determine the comparison.'],
        reference_context=_context(record,s))


def _fabrication(record,s):
    rows=[];L=s['span_m'];d=s['section']['dimensions'];top=-.172
    _box(rows,'factory-floor',(-3.,-7.0,-2.25),(26.,14.,.20),'ground','factory-context',
         'proposed-envelope','Illustrative local precast workstation, not factory capacity or surveyed layout')
    _box(rows,'casting-bed',(-.5,-1.45,-2.05),(21.,2.9,.30),'dark_steel','reusable-formwork',
         'illustrative-tooling','Proposed reusable casting bed; stiffness, datum and foundation design pending')
    _box(rows,'base-form-skin',(0.,-1.05,-1.612),(L,2.1,.04),'teal','reusable-formwork',
         'illustrative-tooling','Proposed base-form skin supports source beam underside; flatness and release process unqualified')
    for sign in (-1,1):
        _box(rows,f'base-form-support-rail-{sign}',(0.,sign*.65-.08,-1.75),
             (L,.16,.138),'dark_steel','reusable-formwork','illustrative-tooling')
    for side in (-1,1):
        yy=side*2.4
        _box(rows,f'open-side-form-{side}',(0.,yy-.055,top-d['depth_m']),
             (L,.11,d['depth_m']),'teal','reusable-formwork','illustrative-tooling',
             'Reusable steel side-form shown opened; rib sizes and stripping route are proposed')
        for i in range(11):
            _box(rows,f'form-rib-{side}-{i}',(i*2-.04,yy-.18,top-d['depth_m']),
                 (.08,.36,d['depth_m']),'teal','reusable-formwork','illustrative-tooling')
        for i in range(4):
            _box(rows,f'opened-form-support-{side}-{i}',(1.+i*6-.15,yy-.5,-2.05),
                 (.30,1.,.478),'dark_steel','reusable-formwork','illustrative-tooling',
                 'Proposed stable stands under opened side-forms; tooling stability and handling method unqualified')
    _beam(rows,'reference-beam',s,top=top,explode=True)
    # A segmented collapsible core is a proposal, not a proved stripping method.
    for i in range(4):
        length=(L-.30)/4-.03;x=.15+i*(L-.30)/4
        obj=_box(rows,f'collapsible-core-envelope-{i}',(x,-.805,top-d['depth_m']+d['flange_m']),
                 (length,1.61,1.01),'aluminium','void-former','illustrative-tooling',
                 'Proposed collapsible core tooling envelope; extraction through end openings is not demonstrated')
        obj['render_offset_m']=[0.,0.,1.20]
    # Two13-strand web bundles represent all26 analytical strands. Their duct
    # diameter, packing, route and anchor block are proposed detailing choices.
    r=sqrt(.00014/pi);emax=s['prestress_reference']['parabolic_eccentricity_max_m']
    centroid=top-d['depth_m']/2
    for side in (-1,1):
        centre_y=side*(d['outer_width_m']/2-d['wall_m']/2)
        path=[(L*i/20,centre_y,centroid-emax*4*(i/20)*(1-i/20)) for i in range(21)]
        obj=_pipe(rows,f'proposed-13strand-web-duct-{side}',path,.0525,'orange','tendon-ducts',
                  source='Two proposed web ducts grouping26 source strands; diameter/cover/anchorage not designed')
        obj['render_offset_m']=[0.,-.72 if side<0 else 0.,0.]
        # Individual equivalent metal-area strand routes shown in companion jig,
        # avoiding a false claim that pipe-envelope volume is installed metal.
        for j in range(13):
            dy=(j%4-1.5)*.016;dz=(j//4-1)*.016
            route=[(px,py+dy+3.5,pz+dz) for px,py,pz in path]
            _pipe(rows,f'jig-strand-{side}-{j}',route,r,'steel','strand-layout',
                  source=SOURCE+'/prestress_strands and strand_area_m2; equivalent metal area only, not strand surface/contact; grouping/routed length proposed')
        for end in (0.,L):
            _box(rows,f'proposed-anchor-{side}-{end}',(end-.065,centre_y-.105,centroid-.105),
                 (.13,.21,.21),'dark_steel','anchorages','illustrative-tooling',
                 'Proposed bundle anchorage envelope; source anchorage mass is a separate accounting quantity')
    # Schematic cage in a separate jig. This does not claim the full2.674t
    # reinforcement allowance has been geometrically scheduled.
    cage_y=3.5
    for yy in (-.89,.89):
        for zz in (top-.12,top-.50,top-.90,top-1.28):
            _link(rows,f'cage-long-{yy}-{zz}',(.10,cage_y+yy,zz),(L-.10,cage_y+yy,zz),
                  .008,'dark_steel','schematic-reinforcement','illustrative-tooling',
                  'Illustrative longitudinal bars; grade/diameter/spacing and full bar bending schedule unresolved')
    for i in range(21):
        x=.20+(L-.40)*i/20
        _pipe(rows,f'cage-stirrup-{i}',[(x,cage_y-.89,top-.12),(x,cage_y+.89,top-.12),
                    (x,cage_y+.89,top-1.28),(x,cage_y-.89,top-1.28),(x,cage_y-.89,top-.12)],
              .007,'dark_steel','schematic-reinforcement',
              source='Illustrative closed ties, not a released shear/torsion reinforcement design')
    for i in range(5):
        x=1.+i*4.5
        _box(rows,f'cage-jig-trestle-{i}',(x-.15,cage_y-1.2,-2.05),(.30,2.4,.590),
             'teal','reinforcement-jig','illustrative-tooling')
    _box(rows,'curing-cover-rack',(1.,-5.4,-2.05),(5.0,1.0,.65),'white','curing-and-QA',
         'illustrative-tooling','Curing-cover envelope; actual mix, temperature, moisture and release-strength programme required')
    _box(rows,'inspection-datum-bench',(13.,-5.3,-2.05),(3.,1.,.85),'teal','curing-and-QA',
         'illustrative-tooling','Dimensional inspection bench; calibration and acceptance limits unresolved')
    for i in range(3):
        _cyl(rows,f'concrete-test-sample-{i}',(13.4+i*.5,-4.8,-1.2),.075,.30,
             material='concrete',group='curing-and-QA',basis='illustrative-tooling',
             source='Illustrative test specimens only; no concrete strength measurement is supplied')
    metrics=_metrics(s,'local reusable-formwork precasting; proposed web tendons')
    metrics.update(source_concrete_solids=6,illustrated_tendon_bundles=2,
        source_strands_per_proposed_bundle=s['prestress_strands']//2,
        reinforcement_cage_geometrically_complete=False,
        actual_mould_cycle_time_h=None,void_former_extraction_demonstrated=False,
        rendering_is_exploded=True,
        source_analytical_strand_length_m=s['prestress_strands']*L,
        proposed_routed_strand_length_m=s['prestress_strands']*sum(sqrt((L/20)**2+
            (emax*4*((i+1)/20)*(1-(i+1)/20)-emax*4*(i/20)*(1-i/20))**2) for i in range(20)))
    return dict(id='precast-fabrication',title='Local precast fabrication',
        subtitle='Exploded stock, reusable outer forms and proposed tendon/inspection workflow',
        entities=rows,labels=[
            _label('Reusable outer formwork /opened',(8.,-2.4,-.7),'left',0),
            _label('Source box section /22.2816 m3',(14.,0.,-1.48),'right',0),
            _label('Collapsible core /extraction unresolved',(11.,0.,1.0),'right',1),
            _label('26 strands /two proposed web ducts',(7.,3.5,-1.1),'right',2),
            _label('Cage jig /bar schedule still required',(16.,3.5,-.6),'left',1),
            _label('Curing, release strength and QA',(14.0,-4.8,-1.1),'left',2)],
        camera=dict(direction=[1.,-1.3,1.0],target_m=[10.,.6,-.05],ortho_scale_m=28.),
        metrics=metrics,assumptions=_common_assumptions()+[
            'Fabrication uses the canonical stock reference datum. Roof and near web receive explicit render-only offsets for the exploded view; tooling/core envelopes are a proposed fabrication layout. The workshop datum is not a surveyed operating railhead.',
            'A collapsible four-module core is shown as a tooling envelope. Its collapse, extraction clearance, concrete finish and safe access have not been designed; it must not be treated as a resolved moulding route.',
            'The source specifies26strands by analytical area and straight span length, not a complete tendon layout. Two13strand web ducts, their105mm envelope diameter and anchor positions are proposed. Routed strand length is reported separately and exceeds the simple source length allowance.',
            'The adjacent cage is schematic. It does not geometrically close the source120kg/m3 reinforcement allowance or supply cover, development length, local anchorage, lifting or torsion detailing.',
            'Concrete test specimens are illustrative. No material test result, curing cycle, stripping strength, prestress-transfer acceptance or factory quality certificate is implied.'],
        reference_context=_context(record,s))


def generate(root):
    root=Path(root)
    raw=(root/RECORD).read_bytes();record=json.loads(gzip.decompress(raw));s=record['civil']['selected_reference']
    if s['family']!='box-beam' or s['span_m']!=20.:
        raise ValueError('Explicit selected20m box-beam source required; do not mix civil candidates')
    if s['prestress_strands']!=26 or s['diaphragm_definition']['quantity']!=2:
        raise ValueError('Selected strand/diaphragm recipe changed; re-audit fabrication visual')
    assemblies=[_crane(record,s),_gantry(record,s),_fabrication(record,s)]
    for assembly in assemblies:
        ids=[e['id'] for e in assembly['entities']]
        if len(ids)!=len(set(ids)) or len(ids)>1000:raise ValueError('Unique bounded civil scene entities required')
    return dict(schema='osr-visual-family/1',family='civil',assemblies=assemblies,
        sources=[RECORD,BIM,CIVIL,PRODUCER],source_record_sha256=sha256(raw).hexdigest(),
        assumptions=['Alternative proposed erection methods reuse the same selected20m beam; none is a construction or operating release.'],
        references=deepcopy(REFERENCES),**FLAGS)
