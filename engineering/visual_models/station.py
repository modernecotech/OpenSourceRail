"""Source-linked station research layouts, not released mechanism drawings.

The hydraulic G3 control supplies the energy and motion requirements. Equipment,
connections, station rail bearers and maintenance envelopes below are explicit
visual design hypotheses. No source case budget or physical approval transfers
into this new layout. All dimensions are metres.
"""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from math import pi, sqrt, sin, cos
from pathlib import Path

SCENARIO = 'G3-hydraulic-c10-v60-r10-continuous-total-force-rear'
REFERENCE = 'docs/design-engine/station-regenerative-launch/reference.json'
EVALUATION = 'docs/design-engine/current/evaluation.json.gz'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    selected_reference_changed=False, movement_authority=False)
PROPOSED = 'Explicit visual-layout hypothesis; sizing, strength and qualification remain open'


class Scene:
    def __init__(self, name, title, subtitle, context):
        self.value = dict(id=name, title=title, subtitle=subtitle, entities=[], labels=[],
            camera={}, metrics={}, assumptions=[], reference_context=deepcopy(context), **FLAGS)
        self.ids = set()

    def entity(self, name, shape, at, material, group, *, basis='proposed-envelope', source=PROPOSED, **kw):
        if name in self.ids:
            raise ValueError('Repeated entity: '+name)
        self.ids.add(name)
        item = dict(id=name, shape=shape, at_m=list(at), material=material,
                    group=group, basis=basis, source=source, **kw)
        self.value['entities'].append(item)
        return item

    def box(self, name, at, size, material='steel', group='structure', **kw):
        return self.entity(name, 'box', at, material, group, size_m=list(size), **kw)

    def cyl(self, name, at, radius, length, axis=(0,0,1), material='steel', group='drive', **kw):
        return self.entity(name, 'cylinder', at, material, group,
                           radius_m=radius, length_m=length, axis=list(axis), **kw)

    def tube(self, name, at, radius, inner, length, axis=(0,0,1), material='steel', group='drive', **kw):
        return self.entity(name, 'tube', at, material, group, radius_m=radius,
                           inner_radius_m=inner, length_m=length, axis=list(axis), **kw)

    def pipe(self, name, path, radius=.018, material='red', group='hydraulics', **kw):
        # path_m already contains absolute scene coordinates; the object must
        # retain an identity translation so CAD/render backends do not shift it twice.
        return self.entity(name, 'pipe', (0,0,0), material, group,
                           path_m=[list(p) for p in path], radius_m=radius, **kw)

    def sphere(self, name, at, radius, material='teal', group='storage', **kw):
        return self.entity(name, 'sphere', at, material, group, radius_m=radius, **kw)

    def label(self, text, anchor, side, order):
        if len(text)>45:
            raise ValueError('Callout too long: '+text)
        self.value['labels'].append(dict(text=text, anchor_m=list(anchor), side=side, order=order))

    def finish(self):
        counts = Counter(e['group'] for e in self.value['entities'])
        self.value['metrics']['modelled_entity_count'] = len(self.value['entities'])
        self.value['metrics']['entities_by_subsystem'] = dict(sorted(counts.items()))
        self.value['metrics']['shown_bolt_assembly_count'] = sum(e['id'].endswith('/shank') for e in self.value['entities'])
        self.value['metrics']['shown_positive_parking_pin_count'] = sum(e['id'].endswith('/positive-parking-pin') for e in self.value['entities'])
        self.value['metrics']['shown_fixed_wiring_route_count'] = sum(e['group']=='fixed-wiring-envelopes' for e in self.value['entities'])
        self.value['metrics']['complete_fastener_or_joint_inventory'] = False
        self.value['metrics']['rated_fastener_bearing_or_stop_capacity'] = None
        self.value['metrics']['complete_installed_mass_kg'] = None
        self.value['metrics']['complete_installed_price'] = None
        self.value['metrics']['geometry_is_qualified_installation'] = False
        self.value['metrics']['coordinate_frame'] = 'x forward, y left, z up; rail running surface z=0'
        return self.value


def _bolt(scene, name, at, diameter=.026, grip=.07, group='fasteners'):
    """A visible shank and head; no bolt grade/preload is implied."""
    scene.cyl(name+'/shank', at, diameter/2, grip, material='dark_steel', group=group)
    scene.cyl(name+'/head', (at[0],at[1],at[2]+grip), diameter*.9, diameter*.6,
              material='steel', group=group)


def _rail(scene, name, x, length, centre):
    src = 'engineering/station_rail/civil.py and bim.py; 60E1 nominal envelope, contact radii omitted'
    for part, y, z, width, height in [('foot',centre-.075,-.172,.150,.016),
            ('web',centre-.00825,-.156,.0165,.105),('head',centre-.036,-.051,.072,.051)]:
        scene.box(name+'/'+part,(x,y,z),(length,width,height), 'steel','running-rails',
                  basis='derived-layout',source=src)


def _track(scene, x, length, *, detailed=False, pedestals=False):
    """Raised proposed station rail seats keep machinery above intact concrete."""
    _rail(scene,'running-rail/left',x,length,.7535)
    _rail(scene,'running-rail/right',x,length,-.7535)
    scene.box('station-deck/envelope',(x,-1.,-1.8),(length,2.,1.4),'concrete','station-structure',
              source='Proposed intact station box/deck: 2.0m width, 1.4m depth, top -0.40m; source section dimensions only, no inherited resistance')
    # The station elevation is a NEW interface, not a slot cut through the
    # source180mm flange. Rail-seat pedestals bridge -0.40 to -0.172m.
    pitch = .6 if detailed else 5.
    n = int(length/pitch)+1
    for i in range(n):
        xx = x+min(length-.12,i*pitch)
        for side in (-1,1):
            centre=side*.7535
            scene.box(f'rail-seat/{side}/{i}',(xx,centre-.15,-.4),(.24,.30,.228),
                      'concrete','rail-seats',source='Proposed228mm cast-in station rail seat; anchorage/tendon conflicts unresolved')
            if detailed:
                scene.box(f'baseplate/{side}/{i}',(xx+.01,centre-.11,-.19),(.22,.22,.018),
                          'dark_steel','rail-fastening')
                for sy in (-.10,.10):
                    _bolt(scene,f'anchor/{side}/{i}/{sy}',(xx+.12,centre+sy,-.25),.022,.07)
    if pedestals:
        for i in range(int(length/20)+1):
            xx=x+i*20
            scene.box(f'pier/{i}',(xx-.5,-.5,-8.),(1.,1.,5.7),'concrete','support-envelopes')
            scene.box(f'cap/{i}',(xx-.7,-1.4,-2.3),(1.4,2.8,.4),'concrete','support-envelopes')
            for yy in (-.65,.45):
                scene.box(f'bearing/{i}/{yy}',(xx-.3,yy,-1.9),(.6,.2,.1),'rubber','bearings')


def _channel(scene, prefix, x, length, centre, *, width=.20, detailed=False):
    # Two narrow guide bars and an open service tray; no solid block occupies
    # the carriage/cable swept volume. Rail running surfaces stay untouched.
    for sign in (-1,1):
        scene.box(prefix+f'/guide/{sign}',(x,centre+sign*width/2-.012,-.34),
                  (length,.024,.04),'steel','shuttle-guidance')
        scene.box(prefix+f'/wall/{sign}',(x,centre+sign*(width/2+.035)-.012,-.40),
                  (length,.024,.18),'dark_steel','guarded-service-channels')
    scene.box(prefix+'/floor',(x,centre-width/2-.05,-.40),(length,width+.1,.025),
              'dark_steel','guarded-service-channels')
    if detailed:
        for i in range(int(length/2)+1):
            for sign in (-1,1):
                _bolt(scene,prefix+f'/guide-fastener/{i}/{sign}',
                      (x+min(length-.1,i*2),centre+sign*(width/2+.035),-.38),.018,.055)


def _cart(scene, prefix, x, centre, *, raised=False, launch=False):
    width=.30 if launch else .16
    scene.box(prefix+'/chassis',(x-.35,centre-width/2,-.23),(.7,width,.07),
              'teal' if launch else 'orange','launch-shuttle' if launch else 'capture-carriages')
    scene.box(prefix+'/retracted-cover',(x-.30,centre-width/2,-.16),(.60,width,.05),
              'dark_steel','retention-and-guards')
    for dx in (-.23,.23):
        for sign in (-1,1):
            scene.cyl(prefix+f'/guide-wheel/{dx}/{sign}',(x+dx,centre+sign*width/2-.014,-.25),
                      .05,.028,(0,1,0),'steel','guide-wheels')
            scene.cyl(prefix+f'/guide-axle/{dx}/{sign}',(x+dx,centre+sign*width/2-.025,-.25),
                      .012,.05,(0,1,0),'dark_steel','guide-bearings')
    if raised:
        scene.box(prefix+'/telescoping-post',(x-.075,centre-.055,-.11),(.15,.11,.94),
                  'orange','deployed-coupling-posts')
        scene.box(prefix+'/compliant-shoe',(x-.11,centre-.10,.76),(.24,.20,.16),
                  'rubber','train-coupling-interfaces')
    else:
        scene.box(prefix+'/post-stowed',(x-.075,centre-.055,-.15),(.15,.11,.04),
                  'orange','stowed-coupling-posts')
    scene.cyl(prefix+'/positive-parking-pin',(x-.18,centre-width/2-.025,-.205),.013,
              width+.05,(0,1,0),'steel','mechanical-retention')
    scene.box(prefix+'/passive-ranging-target',(x-.06,centre-.04,-.108),(.12,.08,.008),
              'white','position-sensing')


def _train(scene, evaluation, front, *, count=6):
    v=evaluation['vehicle']['physical_definition']['vehicle']
    s=evaluation['vehicle']['physical_definition']['support']
    length=v['body_length_m'];width=v['body_width_m'];gap=v['coupling_gap_m']
    source=EVALUATION+' vehicle.physical_definition.vehicle/support; simplified envelope, not located-material CAD'
    for i in range(count):
        right=front-i*(length+gap);left=right-length;mid=(right+left)/2
        scene.box(f'train/car-{i}/underframe',(left,-1.18,.80),(length,2.36,.20),
                  'aluminium','vehicle-envelopes',source=source)
        scene.box(f'train/car-{i}/body',(left,-width/2,1.),(length,width,2.77),
                  'white','vehicle-envelopes',source=source)
        scene.box(f'train/car-{i}/roof',(left+.08,-1.25,3.77),(length-.16,2.5,.0369),
                  'aluminium','vehicle-envelopes',source=source)
        for side in (-1,1):
            for j,rel in enumerate((-6.9,-2.6,0.,2.6,6.9)):
                scene.box(f'train/car-{i}/window/{side}/{j}',(mid+rel-.73,side*(width/2+.008)-.009,1.96),
                          (1.46,.018,1.02),'glass','vehicle-envelopes',source='Proposed overview glazing positions; precise glazing is in source counted body')
            if side==1:
                for j,rel in enumerate((-4.5,4.5)):
                    scene.box(f'train/car-{i}/door/{j}',(mid+rel-.7,width/2+.012,1.),
                              (1.4,.022,2.1),'teal','passenger-doors',
                              source=EVALUATION+' vehicle.seating_layout door_centres_x_m/door_width_m/door_height_m; +y boarding side')
        for b,bx in enumerate(s['bogie_centres_x_m']):
            centre=mid+bx
            scene.box(f'train/car-{i}/bogie/{b}/frame',(centre-1.28,-1.0,.51),
                      (2.56,2.0,.22),'dark_steel','passive-bogie-frames',source=source)
            for ax,offset in enumerate((-.5*s['bogie_wheelbase_m'],.5*s['bogie_wheelbase_m'])):
                xx=centre+offset
                scene.cyl(f'train/car-{i}/bogie/{b}/axle/{ax}',(xx,-1.,.38),.075,2.,(0,1,0),
                          'dark_steel','passive-axles',source=source)
                for sign in (-1,1):
                    yy=sign*.7475-.065
                    scene.tube(f'train/car-{i}/bogie/{b}/wheel/{ax}/{sign}',(xx,yy,.38),
                               .38,.13,.13,(0,1,0),'steel','passive-wheels',source=source)
                    scene.cyl(f'train/car-{i}/bogie/{b}/hub/{ax}/{sign}',(xx,yy-.01,.38),
                              .13,.15,(0,1,0),'dark_steel','wheel-hubs',source=source)
                scene.cyl(f'train/car-{i}/brake-disc/{b}/{ax}',(xx,.18,.38),.24,.035,(0,1,0),
                          'steel','independent-brakes',source='Proposed disc/axle illustration only; actual brake sizing and degraded stopping unqualified')
                scene.box(f'train/car-{i}/brake-caliper/{b}/{ax}',(xx-.12,.14,.53),(.24,.12,.13),
                          'red','independent-brakes')
        if i<count-1:
            scene.cyl(f'train/coupler/{i}',(left-gap,0.,.84),.07,gap,(1,0,0),
                      'dark_steel','train-coupling-interfaces',source='Source0.5m inter-car gap; proposed coupler envelope and force path, rating unverified')
    return count*length+(count-1)*gap


def _accumulator_bank(scene, prefix, at, volume, *, detail=False):
    x,y,z=at;count=12;inner_r=.15;outer_r=.18
    straight=(volume/count-4*pi*inner_r**3/3)/(pi*inner_r**2)
    if straight<=0:raise ValueError('Accumulator cavity does not fit declared radius')
    source='Derived12 equal precharge-equivalent cavities from '+REFERENCE+' hydraulic sizing.internal_volume_m3; outer shell/head geometry is a packaging hypothesis'
    scene.box(prefix+'/skid',(x-.25,y-.25,z),(2.8,2.15,.16),'dark_steel','storage-skid')
    for ix in range(4):
        for iy in range(3):
            name=f'{prefix}/vessel/{ix}/{iy}';cx=x+ix*.70;cy=y+iy*.70;bottom=z+.44
            scene.cyl(name+'/barrel',(cx,cy,bottom),outer_r,straight,(0,0,1),'teal','pressure-vessel-envelopes',source=source)
            for k,zz in enumerate((bottom,bottom+straight)):
                scene.sphere(name+f'/domed-envelope/{k}',(cx,cy,zz),outer_r,'teal','pressure-vessel-envelopes',source=source)
            scene.cyl(name+'/neck',(cx,cy,bottom+straight+.14),.047,.15,(0,0,1),
                      'steel','storage-ports')
            scene.cyl(name+'/isolation-body',(cx,cy,bottom+straight+.27),.065,.10,(0,0,1),
                      'orange','vessel-isolation')
            scene.box(name+'/isolation-handle',(cx-.10,cy-.025,bottom+straight+.37),(.20,.05,.025),
                      'red','vessel-isolation')
            for sign in (-1,1):
                scene.box(name+f'/foot/{sign}',(cx+sign*.15-.03,cy-.13,z+.16),(.06,.26,.21),
                          'steel','vessel-retention')
            if detail:
                for dx in (-.18,.18):
                    _bolt(scene,name+f'/anchor/{dx}',(cx+dx,cy,z+.10),.020,.08)
                scene.pipe(name+'/branch',[(cx,cy,bottom+straight+.31),(cx,cy-.15,bottom+straight+.31),
                    (cx,cy-.15,z+.26),(cx,y-.20,z+.26)],.018,'red','storage-manifold')
    if detail:
        scene.pipe(prefix+'/header',[(x-.20,y-.20,z+.26),(x+2.3,y-.20,z+.26)],.032,'red','storage-manifold')
    return dict(vessel_count=count,precharge_equivalent_internal_volume_m3=volume,
        cavity_radius_m=inner_r,straight_cavity_length_m=straight,
        proposed_outer_radius_m=outer_r,wall_or_head_design_qualified=False,
        mass_from_geometry_kg=None,
        geometry_note='Overlapping capsule envelopes show exterior packaging only, not material shells or a pressure-vessel mass takeoff')


def _drum(scene,prefix,at,*,detail=False):
    x,y,z=at;group='capture-drive'
    scene.box(prefix+'/bed',(x-.62,y-.56,z), (1.24,1.12,.14),'dark_steel',group)
    scene.cyl(prefix+'/barrel',(x,y-.35,z+.70),.45,.70,(0,1,0),'orange',group)
    for sign in (-1,1):
        yy=y+sign*.38
        scene.cyl(prefix+f'/flange/{sign}',(x,yy-.02,z+.70),.49,.04,(0,1,0),'steel',group)
        scene.box(prefix+f'/bearing/{sign}',(x-.17,yy-.12,z+.14),(.34,.24,.56),'dark_steel','capture-bearings')
    scene.cyl(prefix+'/shaft',(x,y-.66,z+.70),.075,1.32,(0,1,0),'steel','drive-shafts')
    scene.cyl(prefix+'/one-way-clutch',(x,y-.67,z+.70),.19,.20,(0,1,0),'teal','overrunning-clutches')
    scene.box(prefix+'/gearbox',(x-.60,y-.67-1.12,z+.15),(1.2,1.12,1.0),'aluminium','force-transformer-envelopes',
              source='Illustrative enclosed10:1 equivalent force/travel transformer; actual gears, rack/reeving, shaft strength and pump speed-flow sizing unresolved')
    scene.cyl(prefix+'/variable-pump-envelope',(x,y-2.04,z+.68),.28,.40,(0,1,0),
              'teal','variable-displacement-pump-envelopes')
    scene.box(prefix+'/guard',(x-.63,y+.55,z+.14),(1.26,.045,1.12),'orange','retention-and-guards')
    scene.box(prefix+'/encoder',(x-.09,y+.69,z+.61),(.18,.12,.18),'dark_steel','position-sensing')
    if detail:
        for xx in (-.49,.49):
            for yy in (-.42,.42):
                _bolt(scene,prefix+f'/bed-bolt/{xx}/{yy}',(x+xx,y+yy,z+.04),.024,.09)


def _control_pack(scene,prefix,at,*,detail=True):
    x,y,z=at
    scene.box(prefix+'/power-control-cabinet',(x,y,z),(1.55,.65,1.80),'white','control-envelopes')
    for j in range(3):
        scene.box(prefix+f'/cabinet-door/{j}',(x+.03+j*.50,y-.018,z+.05),(.47,.025,1.68),
                  'dark_steel' if j==0 else 'aluminium','control-envelopes')
    scene.box(prefix+'/HMI',(x+.10,y-.042,z+1.15),(.29,.025,.25),'teal','control-envelopes')
    scene.cyl(prefix+'/emergency-stop',(x+.94,y-.07,z+1.15),.055,.04,(0,1,0),
              'red','protection-envelopes')
    scene.box(prefix+'/cooler',(x+1.85,y,z),(.90,.42,1.40),'dark_steel','cooling-envelopes')
    for i in range(12):
        scene.box(prefix+f'/cooler-fin/{i}',(x+1.90,y+.02+i*.031,z+.06),(.80,.010,1.28),
                  'aluminium','cooling-envelopes')
    for k in range(2):
        scene.cyl(prefix+f'/fan/{k}',(x+2.30,y-.075,z+.40+k*.60),.23,.08,(0,1,0),
                  'dark_steel','cooling-envelopes')
        scene.cyl(prefix+f'/fan-hub/{k}',(x+2.30,y-.095,z+.40+k*.60),.065,.09,(0,1,0),
                  'steel','cooling-envelopes')
    if detail:
        scene.pipe(prefix+'/LV-cable-route',[(x+.3,y+.45,z+.1),(x+.3,y+.8,z+.1),
            (x+3.0,y+.8,z+.1)],.022,'dark_steel','fixed-wiring-envelopes')


def _overview(evaluation,sample,context):
    r=sample['physics'];capture=r['capture'];front=capture['total_distance_m']
    v=evaluation['vehicle']['physical_definition']['vehicle']
    formation=v['cars']*v['body_length_m']+(v['cars']-1)*v['coupling_gap_m']
    rear=front-formation;travel=r['launch']['distance_m']+r['booster']['distance_m'];end=rear+travel
    scene=Scene('station-overview','Capture. Hold. Launch forward.',
        'Hydraulic G3 layout study: five staged arrestors, isolated storage and a shared launch/boost drive',context)
    _track(scene,-110.,390.,pedestals=True)
    _train(scene,evaluation,front)
    # Platform is on source +y boarding side. The mechanics remain in guarded
    # low-level channels between running rails; plant bay is on the opposite side.
    scene.box('platform/deck',(rear-.5,1.38,.73),(formation+1.,3.20,.27),'concrete','platform-envelope',
              source='Proposed +y platform at1.0m rail-relative level; 51mm nominal body-skin gap, accessible boarding not qualified')
    scene.box('platform/edge',(rear-.5,1.38,.995),(formation+1.,.20,.025),'orange','platform-envelope')
    for i in range(7):
        xx=rear+i*formation/6
        scene.box(f'canopy/post/{i}',(xx,4.20,1.),(.16,.16,3.20),'steel','canopy-envelope')
    scene.box('canopy/roof',(rear-.8,1.42,4.20),(formation+1.6,3.30,.14),'white','canopy-envelope')
    for side in (-1,1):
        _channel(scene,f'capture-channel/{side}',.4,70.5,side*.43,width=.16)
    _channel(scene,'launch-channel',rear-.50,travel+35.5,0.,width=.30)
    for i,stage in enumerate(capture['stages']):
        xx=stage['end_x_m']+.4
        for sign in (-1,1):
            _cart(scene,f'capture-stage/{i}/{sign}',xx,sign*.43,raised=i==4)
            # Discrete outboard drums are proposed packaging, not a native
            # force/torque or supplier map. Symmetric64kN contact shares are ideal.
            sx=stage['start_x_m']+1.5;sy=-2.8-sign*.70
            scene.box(f'capture-stage/{i}/{sign}/skid',(sx-.6,sy-.55,-.4),
                      (1.2,1.1,.16),'dark_steel','capture-drive')
            scene.cyl(f'capture-stage/{i}/{sign}/drum',(sx,sy-.3,.30),.45,.60,(0,1,0),
                      'orange','capture-drive')
            scene.box(f'capture-stage/{i}/{sign}/pump',(sx-.35,sy-.90,-.10),(.7,.40,.70),
                      'teal','variable-displacement-pump-envelopes')
        scene.pipe(f'capture-stage/{i}/common-pressure-line',[(xx,-3.8,-.15),(xx,-5.0,-.15),
            (48.,-5.0,-.15)],.025,'red','fixed-pressure-header')
    scene.box('capture-service-deck',(0.,-4.3,-.65),(72.,3.3,.25),'concrete','station-plant-support-envelopes')
    for i,xx in enumerate((10.,30.,50.,70.)):
        scene.box(f'plant-ledge/pier/{i}',(xx-.45,-3.45,-8.),(.9,.9,7.1),'concrete','station-plant-support-envelopes')
        scene.box(f'plant-ledge/cap/{i}',(xx-.60,-4.4,-.9),(1.2,3.5,.25),'concrete','station-plant-support-envelopes')
    scene.box('store-plant-deck',(46.8,-9.2,-.75),(11.,8.2,.35),'concrete','station-plant-support-envelopes')
    for i,xx in enumerate((48.,55.)):
        scene.box(f'store-bay/pier/{i}',(xx-.6,-7.8,-8.),(1.2,1.2,6.85),'concrete','station-plant-support-envelopes')
        scene.box(f'store-bay/cap/{i}',(xx-.8,-8.8,-1.15),(1.6,7.8,.4),'concrete','station-plant-support-envelopes')
    bank=_accumulator_bank(scene,'energy-store',(48.,-8.,-.40),r['sizing']['internal_volume_m3'])
    _control_pack(scene,'station-control',(54.,-8.,-.4),detail=False)
    _cart(scene,'rear-launcher',rear-.35,0.,raised=True,launch=True)
    scene.box('rear-launcher/load-spreader',(rear-.22,-.35,.76),(.22,.70,.16),'steel','train-coupling-interfaces')
    scene.box('launch-drive/support-deck',(rear-7.,-5.4,-.75),(6.,4.4,.35),'concrete','station-plant-support-envelopes')
    scene.box('launch-drive/support-pier',(rear-4.4,-3.9,-8.),(1.2,1.2,7.25),'concrete','station-plant-support-envelopes')
    scene.box('launch-drive/skid',(rear-6.,-4.8,-.4),(4.,2.7,.2),'dark_steel','launch-drive')
    scene.cyl('launch-drive/drum',(rear-4.,-3.2,.50),.55,1.0,(0,1,0),'orange','launch-drive')
    scene.box('launch-drive/hydraulic-motor',(rear-5.,-4.4,-.05),(1.20,.80,.90),'teal','launch-drive')
    scene.cyl('launch-drive/grid-motor',(rear-3.5,-4.5,.44),.45,1.4,(0,1,0),'aluminium','launch-drive')
    for yy in (-.10,.10):
        scene.pipe(f'launch-haul-cable/{yy}',[(rear-.4,yy,-.20),(end+35.,yy,-.20)],.014,'copper','launch-cables')
    # Thin scene-space strips represent travel regions, not a winding or rail.
    launch_front=front+r['launch']['distance_m'];boost_front=launch_front+r['booster']['distance_m']
    scene.box('travel-key/recovery',(front,-1.18,-.36),(r['launch']['distance_m'],.16,.025),
              'teal','motion-annotations',basis='derived-layout',source=REFERENCE+' launch.distance_m; reference-point motion only')
    scene.box('travel-key/grid-boost',(launch_front,-1.18,-.36),(r['booster']['distance_m'],.16,.025),
              'orange','motion-annotations',basis='derived-layout',source=REFERENCE+' booster.distance_m; not installed hardware length')
    scene.box('runout-key',(end,-.23,-.36),(35.,.46,.025),'red','motion-annotations')
    scene.label('Five controlled capture stages',(36.,-.43,-.10),'left',0)
    scene.label('Isolated hydraulic storage',(49.0,-7.,1.2),'left',1)
    scene.label('Independent train brakes remain required',(63.,.2,.45),'left',2)
    scene.label('Rear shuttle: recovered launch',(rear-.35,0.,.85),'right',0)
    scene.label('Optional grid assistance, same capstan',(rear-4.,-3.6,.6),'right',1)
    scene.label('Separate shuttle runout and return',(end+15.,0.,-.15),'right',2)
    scene.value['camera']=dict(direction=[2.8,-3.4,2.4],target_m=[85.,-1.,.3],ortho_scale_m=175.)
    scene.value['metrics']=dict(local_to_overview_translation_m=[0.,0.,0.],formation_length_m=formation,body_stock_sum_m=v['cars']*v['body_length_m'],
        source_coupling_gaps_m=v['coupling_gap_m'],cars=6,passive_bogies=12,passive_axles=24,passive_wheels=48,
        capture_reference_travel_m=70.5,recovered_launch_reference_travel_m=r['launch']['distance_m'],
        remaining_boost_reference_travel_m=r['booster']['distance_m'],target_speed_kmh=60.,
        proposed_shuttle_runout_m=35.,proposed_shuttle_deceleration_m_s2=5.,
        unoccupied_shuttle_kinematic_stop_lower_bound_m=(60/3.6)**2/(2*5.),
        nominal_retracted_top_m=-.11,source_passive_fin_bottom_m=.02,
        nominal_static_fin_to_retracted_hardware_gap_m=.13,station_deck_top_m=-.4,
        station_rail_seat_height_m=.228,**bank)
    scene.value['assumptions']=_assumptions()+[
        'Overview body/glazing are simplified envelopes; this is not the2482part located-material CAD or complete installed train.',
        'The six-car source formation is104.5m including five0.5m gaps. The point-mass profile does not prove full-train hardware contact coverage.',
        'Paired capture contacts at y±0.43m split the required128kN aggregate equally as an unproved load-sharing hypothesis.',
        'Capture-carriage cross-fading, independent release, stow and position proof are unresolved mechanical/control interfaces.',
        'The35m runout is an explicit unoccupied-cart planning envelope;5m/s² gives27.78m constant-deceleration lower bound before jerk, controller delay and margin. Actual trolley mass/brakes are unknown.',
        'Travel-colour strips are annotations. There is no selected installed winding, module count or powered hardware length.',
        'The proposed station deck/rail seat elevation does not inherit the reference20m box-beam resistance or installed cost.']
    return scene.finish()


def _storage(evaluation,sample,context):
    scene=Scene('arrestor-storage','Controlled capture and station energy storage',
        'Representative paired cable-drum stage and shared hydraulic bank; proposed equipment envelopes',context)
    _track(scene,0.,10.,detailed=True)
    scene.box('plant-floor/extension',(-1.,-8.3,-.65),(12.,7.3,.25),'concrete','station-plant-support-envelopes')
    for sign in (-1,1):
        _channel(scene,f'capture-channel/{sign}',0.,10.,sign*.43,width=.16,detailed=True)
        _cart(scene,f'capture-cart/{sign}',7.8,sign*.43,raised=True)
    # Paired forward receiver is ahead of all vehicle axles. The body is absent
    # in this machinery view; the drawing is a cropped station module.
    scene.box('train-front/receiver',(7.93,-.61,.77),(.15,1.22,.15),'steel','train-coupling-interfaces')
    for i,xx in enumerate((1.2,3.4)):
        _drum(scene,f'capture-converter/{i}',(xx,-2.7,-.4),detail=True)
        wrap=[(xx+.464*cos(pi-pi*j/12),-2.7,.30+.464*sin(pi-pi*j/12)) for j in range(13)]
        scene.pipe(f'capture-haul-leg/{i}',[(7.8,(-1 if i==0 else 1)*.43,-.20),
            (-.45,(-1 if i==0 else 1)*.43,-.20),(-.45,-2.7,-.20),
            (xx-.464,-2.7,-.20),*wrap,(xx+.464,-2.7,-.20)],.014,'copper','capture-cables')
        scene.pipe(f'capture-pump-supply/{i}',[(xx,-4.74,.28),(xx,-5.2,.28),
            (5.3,-5.2,.28),(5.3,-3.4,.28)],.025,'red','hydraulic-flexible-connection-envelopes')
        scene.pipe(f'capture-pump-return/{i}',[(xx+.25,-4.74,.17),(xx+.25,-5.5,.17),
            (8.9,-5.5,.17),(8.9,-4.2,.17)],.025,'teal','hydraulic-flexible-connection-envelopes')
    bank=_accumulator_bank(scene,'energy-store',(5.0,-3.5,-.40),sample['physics']['sizing']['internal_volume_m3'],detail=True)
    scene.box('return-reservoir',(8.4,-4.7,-.4),(1.35,1.0,.85),'white','return-reservoir-envelope')
    scene.cyl('return-reservoir/filter',(8.7,-4.2,.45),.10,.22,(0,0,1),'steel','filtration')
    # Two series closed energy-isolation valves, plus a separately retained
    # relief/dump path. These do not constitute a safety-rated circuit design.
    for i in range(2):
        scene.box(f'transfer-isolation/{i}',(5.0+i*.40,-4.3,.10),(.28,.28,.25),'orange','dual-transfer-isolation')
        scene.cyl(f'transfer-isolation/{i}/solenoid',(5.14+i*.40,-4.16,.35),.07,.16,
                  (0,0,1),'dark_steel','dual-transfer-isolation')
    scene.pipe('controlled-release-header',[(5.1,-3.7,-.14),(5.1,-4.16,.22),(6.0,-4.16,.22),
        (6.,-5.1,.22)],.035,'red','controlled-forward-transfer')
    scene.box('pressure-relief-and-dump',(7.9,-4.9,.04),(.33,.34,.32),'red','pressure-protection-envelope')
    scene.pipe('isolated-dump-return',[(8.05,-4.72,.20),(8.05,-4.30,.20),(8.50,-4.30,.20)],
               .026,'teal','pressure-protection-envelope')
    for i,x in enumerate((5.2,6.0)):
        scene.cyl(f'pressure-gauge/{i}/body',(x,-4.54,.66),.095,.06,(0,1,0),'steel','pressure-sensing')
        scene.cyl(f'pressure-gauge/{i}/face',(x,-4.555,.66),.080,.012,(0,1,0),'white','pressure-sensing')
        scene.cyl(f'pressure-gauge/{i}/stem',(x,-4.50,.35),.018,.30,(0,0,1),'steel','pressure-sensing')
    _control_pack(scene,'capture-control',(5.0,-7.1,-.40))
    # This access route is a thin floor marking, not a barrier credited for
    # personnel protection or an installation swept-envelope proof.
    for j,(x,y,L,W) in enumerate([(4.3,-6.0,6.0,.045),(4.3,-8.2,6.0,.045),
                    (4.3,-8.2,.045,2.2),(10.25,-8.2,.045,2.2)]):
        scene.box(f'maintenance-mark/{j}',(x,y,-.398),(L,W,.008),'orange','access-markings')
    scene.label('Paired capture contacts: ideal 64 kN each',(7.8,0.,.84),'left',0)
    scene.label('Drum, one-way clutch and transformer',(2.3,-3.8,.4),'left',1)
    scene.label('Shared 8.8 MJ useful storage hypothesis',(6.2,-2.9,1.4),'right',0)
    scene.label('Two series transfer-isolation valves',(5.5,-4.2,.35),'right',1)
    scene.label('Relief, return and cooling',(8.7,-4.6,.35),'right',2)
    scene.label('Control cabinet and position sensing',(5.7,-7.1,.8),'left',2)
    scene.value['camera']=dict(direction=[1.25,-1.85,1.45],target_m=[5.,-2.8,.45],ortho_scale_m=17.)
    source=sample['physics'];scene.value['metrics']=dict(**bank,
        local_to_overview_translation_m=[0.,0.,0.],source_front_body_pose_for_cropped_detail_m=7.4,
        source_case_effective_train_mass_kg=sample['input']['effective_mass_kg'],
        source_aggregate_peak_capture_force_N=source['capture']['required_peak_force_n'],
        paired_contact_force_sharing_hypothesis_N_each=source['capture']['required_peak_force_n']/2,
        equivalent_displacement_ratio=10.,aggregate_store_side_force_upper_bound_N=1280000.,
        source_first_stage_train_travel_m=source['capture']['stages'][0]['distance_m'],
        source_first_stage_store_equivalent_travel_m=source['capture']['stages'][0]['store_travel_m'],
        detail_track_cropped_length_m=10.,pressure_range_absolute_MPa=[12.,30.],
        precharge_absolute_MPa=10.,proposed_independent_transfer_isolation_valves=2,
        proposed_maintenance_walkway_width_m=1.0,store_design_pressure_verified=False,
        material_or_pressure_shell_mass_from_envelope=False,
        source_vessel_package_mass_hypothesis_kg=source['sizing']['active_mass_kg'],
        source_cycle_conversion_loss_J=source['storage']['capture_conversion_loss_j']+source['storage']['store_conversion_loss_j'],
        source_storage_conversion_plus_standing_heat_J=source['storage']['capture_conversion_loss_j']+source['storage']['store_conversion_loss_j']+source['storage']['standing_loss_j'],
        cooler_rated_duty_W=None)
    scene.value['assumptions']=_assumptions()+[
        'This view represents one paired capture stage plus the shared12-vessel store; the other four stage pairs are elsewhere along the overview.',
        'The10m track in this cropped view is not the30.4147m full first-stage capture stroke.',
        'The enclosed10:1 force/travel transformer is an ideal requirement representation. Actual reeving or gears, pump speed/displacement/flow, shaft and bearing capacities are not designed.',
        'Paired64kN train contacts imply an aggregate1.28MN equivalent store-side bound at ratio10; no energy is created and no storage capacity is reduced.',
        'Capsule overlaps are external visual envelopes. The exact1.122524m³ precharge-equivalent useful-window model is assigned across12 equal proposed cavities; this is not a certified vessel design or a material mass model.',
        'Individual vessel isolation, two series transfer valves and relief/return cooling are proposed interfaces, not a safety-rated hydraulic schematic.',
        'All pressure hoses remain station-side. Moving train/shuttle interfaces transmit mechanical force; no moving high-pressure hose to the vehicle is assumed.',
        'Actual guards, access covers, tool clearance, proof pressure, stored-energy maintenance isolation and removal/lifting plan require detailed design.']
    return scene.finish()


def _launcher(evaluation,sample,context):
    scene=Scene('launcher-booster','Recovered launch and controlled acceleration',
        'One rear guided shuttle; hydraulic recovery and optional electric boost share a guarded cable drive',context)
    _track(scene,0.,12.,detailed=True)
    scene.box('plant-floor/extension',(-2.,-6.3,-.65),(12.,5.3,.25),'concrete','station-plant-support-envelopes')
    _channel(scene,'shuttle-guide',0.,12.,0.,width=.30,detailed=True)
    _cart(scene,'launch-shuttle',3.05,0.,raised=True,launch=True)
    scene.box('vehicle-tail/receiver',(3.18,-.35,.76),(.22,.70,.17),'steel','train-coupling-interfaces')
    scene.box('vehicle-tail/underframe',(3.4,-1.18,.80),(6.6,2.36,.20),'aluminium','vehicle-cutaway-envelope')
    for y in (-1.20,1.15):
        scene.box(f'vehicle-tail/side/{y}',(3.4,y,1.),(6.6,.05,1.25),'white','vehicle-cutaway-envelope')
    # One source-located rear bogie within the cropped end structure.
    centre=3.4+2.1
    scene.box('rear-bogie/frame',(centre-1.28,-1.,.51),(2.56,2.,.22),'dark_steel','passive-running-gear')
    for ax,xx in enumerate((centre-1.05,centre+1.05)):
        scene.cyl(f'rear-bogie/axle/{ax}',(xx,-1.,.38),.075,2.,(0,1,0),'dark_steel','passive-running-gear')
        for sign in (-1,1):
            scene.tube(f'rear-bogie/wheel/{ax}/{sign}',(xx,sign*.7475-.065,.38),.38,.13,.13,
                       (0,1,0),'steel','passive-running-gear')
        scene.cyl(f'rear-bogie/brake-disc/{ax}',(xx,.18,.38),.24,.035,(0,1,0),'steel','independent-brakes')
        scene.box(f'rear-bogie/brake-caliper/{ax}',(xx-.12,.14,.53),(.24,.12,.13),'red','independent-brakes')
    # Adjacent fixed machinery is outside the vehicle swept width. Input and
    # return rope legs enter the low-level central tray through guarded idlers.
    scene.box('launch-powerpack/skid',(-1.7,-4.9,-.4),(4.6,3.0,.20),'dark_steel','launch-drive')
    scene.cyl('capstan/shaft',(.55,-4.65,.55),.095,2.65,(0,1,0),'steel','launch-drive')
    for i,y in enumerate((-3.45,-2.75)):
        scene.cyl(f'capstan/drum/{i}',(.55,y-.25,.55),.55,.50,(0,1,0),'orange','launch-drive')
        for sign in (-1,1):
            scene.cyl(f'capstan/flange/{i}/{sign}',(.55,y+sign*.27-.018,.55),.60,.036,
                      (0,1,0),'steel','launch-drive')
    for y in (-4.4,-2.1):
        scene.box(f'capstan/bearing/{y}',(.30,y-.12,-.2),(.50,.24,.76),'dark_steel','launch-bearings')
        for dx in (-.22,.22):_bolt(scene,f'capstan/bearing-anchor/{y}/{dx}',(.55+dx,y,-.3),.028,.1)
    scene.box('launch-powerpack/gearbox',(-1.1,-4.65,-.15),(1.2,1.05,1.2),'aluminium','launch-drive')
    scene.box('launch-powerpack/hydraulic-motor-bank',(-1.45,-3.50,-.15),(1.2,.75,.90),
              'teal','hydraulic-launch-motor-envelope')
    scene.cyl('launch-powerpack/grid-motor',(1.8,-4.65,.50),.45,1.65,(0,1,0),
              'aluminium','optional-grid-motor-envelope')
    for x in (1.35,1.5,1.65,1.80,1.95,2.10,2.25):
        scene.box(f'grid-motor/cooling-fin/{x}',(x,-4.50,.0),(.025,1.25,.9),
                  'steel','optional-grid-motor-envelope')
    scene.cyl('launch-powerpack/hydraulic-clutch',(.55,-4.50,.55),.22,.18,(0,1,0),
              'teal','controlled-drive-clutches')
    scene.cyl('launch-powerpack/spring-applied-shaft-brake',(.55,-2.05,.55),.28,.14,
              (0,1,0),'red','shaft-holding-and-fault-brake-envelope')
    scene.box('shaft-brake/caliper',(.32,-2.02,.65),(.45,.25,.28),'dark_steel','shaft-holding-and-fault-brake-envelope')
    scene.box('capstan/front-guard',(-.1,-1.88,-.4),(1.3,.05,1.65),'orange','retention-and-guards')
    for sign in (-1,1):
        yy=sign*.10
        groove=-3.45 if sign==-1 else -2.75
        wrap=[(.55+.564*cos(pi-pi*j/16),groove,.55+.564*sin(pi-pi*j/16)) for j in range(17)]
        scene.pipe(f'haul-circuit/{sign}/working-leg',[(3.05,yy,-.20),(-.35,yy,-.20),
            (-.35,groove,-.20),(-.014,groove,-.20),*wrap,(1.114,groove,-.20),
            (1.114,sign*.25,-.20),(11.5,sign*.25,-.20)],
                   .014,'copper','independent-haul-cable-circuits')
        scene.pipe(f'haul-circuit/{sign}/forward-working-leg',[(3.05,yy,-.20),(11.5,yy,-.20)],
                   .014,'copper','independent-haul-cable-circuits')
        turn=[(11.5+.075*cos(-sign*pi/2+sign*pi*j/12),
               sign*.175+.075*sin(-sign*pi/2+sign*pi*j/12),-.20) for j in range(13)]
        scene.pipe(f'haul-circuit/{sign}/end-turn',turn,.014,'copper','independent-haul-cable-circuits')
        scene.cyl(f'end-return-idler/{sign}',(11.5,sign*.175,-.25),.075,.10,(0,0,1),
                  'steel','return-idlers')
        scene.box(f'end-stop/{sign}',(11.75,yy-.08,-.40),(.18,.16,.28),'orange','proposed-mechanical-stops')
    scene.pipe('hydraulic-launch-feed',[(-1.0,-3.5,.25),(-1.0,-5.35,.25),(-1.0,-6.0,.25)],
               .035,'red','station-hydraulic-flexible-connections')
    scene.pipe('hydraulic-launch-return',[(-.55,-3.5,.15),(-.55,-5.60,.15),(-.55,-6.0,.15)],
               .035,'teal','station-hydraulic-flexible-connections')
    _control_pack(scene,'launch-control',(3.6,-5.7,-.40))
    for i,x in enumerate((.20,11.4)):
        scene.box(f'independent-position-reader/{i}',(x,-.42,-.1),(.13,.15,.20),
                  'dark_steel','position-sensing')
        scene.box(f'position-reader-base/{i}',(x-.04,-.46,-.4),(.21,.23,.30),
                  'steel','position-sensing')
    scene.pipe('fixed-encoder-LV-route',[(.2,-.42,-.30),(.2,-.60,-.30),
        (4.0,-.60,-.30),(4.,-5.1,-.30)],.018,'dark_steel','fixed-wiring-envelopes')
    scene.label('Retracting rear shoe: shown deployed',(3.05,0.,.83),'left',0)
    scene.label('Two guarded haul / return circuits',(.55,-3.1,.60),'left',1)
    scene.label('Recovered hydraulic drive',(-1.,-3.25,.30),'left',2)
    scene.label('Optional grid motor and VFD',(2.,-4.0,.65),'right',0)
    scene.label('Shaft brake, encoders and interlocks',(.55,-2.,.7),'right',1)
    scene.label('Independent vehicle braking remains',(5.5,.18,.50),'right',2)
    scene.value['camera']=dict(direction=[-1.3,-1.8,1.35],target_m=[4.,-1.8,.35],ortho_scale_m=17.5)
    r=sample['physics'];vehicle=evaluation['vehicle']['physical_definition']['vehicle']
    formation=vehicle['cars']*vehicle['body_length_m']+(vehicle['cars']-1)*vehicle['coupling_gap_m']
    scene.value['metrics']=dict(local_to_overview_translation_m=[r['capture']['total_distance_m']-formation-3.4,0.,0.],
        source_train_only_peak_thrust_N=160000.,
        source_recovered_launch_distance_m=r['launch']['distance_m'],
        source_remaining_boost_distance_m=r['booster']['distance_m'],
        source_launch_peak_mechanical_W=r['launch']['peak_mechanical_power_w'],
        source_boost_peak_source_W=r['booster']['peak_source_power_w'],
        source_rear_push_coupler_compression_upper_bound_N=max(-x for x in r['launch']['coupler_tension_n']),
        proposed_independent_haul_circuits=2,ideal_force_difference_per_circuit_N=80000.,
        proposed_main_capstan_radius_m=.55,required_aggregate_ideal_capstan_torque_Nm=88000.,
        proposed_unoccupied_runout_m=35.,cart_mass_kg=None,
        cart_inertia_and_cable_losses_included_in_source_requirement=False,
        detail_track_cropped_length_m=12.,nominal_retracted_hardware_to_fin_gap_m=.13,
        complete_cart_stop_or_return_model=False,actual_motor_ratings=None,
        driver_onboard=False,normal_service_onboard_traction_motor_count=0)
    scene.value['assumptions']=_assumptions()+[
        'This is a cropped12m drive/coupling detail, not the full172.284m reference-point acceleration path.',
        'The rear shoe is deployed only behind the tail in this pose. Before any vehicle overruns it, the shoe must be stowed and positively proved below the lowest moving equipment envelope.',
        'Two independent cable circuits are shown with ideal equal80kN force difference each. Pretension, rope elasticity, spooling, equalisation, break protection and fatigue are unresolved.',
        'The hydraulic motor-bank and electric motor/VFD are equipment envelopes; their actual ratings are unknown. The source2.785MW peak is a train-only requirement and excludes cart/cable inertia and newly modelled installation losses.',
        'Required rear compression reaches133.33kN in the ideal source model. Coupler buckling, train slack and attachment load paths remain unverified; front pull/distributed alternatives remain open.',
        'The source booster has no force distribution or available-force map. This drawing proposes a common cable drive but does not qualify its coupled dynamics or make it the selected solution.',
        'There are no moving high-voltage or hydraulic connections to the vehicle. Position readers/drive encoders and fixed LV routing are illustrative; safety integrity and independent position proof remain open.',
        'Source train stopping is independent of capture/launch. A failed, full, missed or inhibited recovery path must not remove service/emergency braking.',
        'The35m shuttle runout and subsequent guided return are separately reserved in the overview; actual cart brake, containment and reset proof remain open.']
    return scene.finish()


def _assumptions():
    return [
        'Geometry represents a research outline. It grants no selection, physical acceptance, manufacture release or movement authority.',
        'All equipment dimensions not explicitly source-linked are proposed packaging envelopes, not supplier products or completed fabricated components.',
        'The station deck top is proposed at -0.40m with228mm raised rail seats. Hardware is above intact deck, not inside an uncut source180mm concrete flange. This changed station structure needs its own anchorage, diaphragm, torsion, foundation and fatigue checks.',
        'Running rails are simplified60E1 dimensional envelopes at1.435m nominal gauge. The wheel/contact profile, tolerances, rail welds, wear and fastening qualification are not modelled.',
        'Retracted equipment top -0.11m lies130mm below the source+0.02m passive-fin bottom in the nominal straight/new-wheel pose only. Suspension, worn wheels, curves and failure sweeps are not qualified.',
        'Outboard plant has explicit proposed deck/ledge and pier envelopes. Their load paths, temporary works, seismic resistance, maintenance lifting and installed quantities are not engineered or inherited from the source box beam.',
        'Pressure-vessel heads, guards and route envelopes may overlap by construction. They are visual envelopes, not additive material volume or an installed mass/BOM closure.',
        'Fasteners, bearings, clutches, guide wheels, valves, wiring and cooling are represented, but their count/geometry does not establish load, fatigue, protection or thermal capacity.',
        'Installation sequence: qualify station supports/rail seats; install fixed trays/guides and guarded machinery; pressure-test and prove energy isolation; set train receivers; check end poses/sweeps; independently validate controls and emergency braking.',
        'Removal sequence: secure train and carrier, isolate/dump hazardous pressure, mechanically retain moving parts, remove guards using reserved access, sling each module, disconnect identified hoses/cables and lift to a separately planned laydown area.',
        'No original scenario installed-price estimate is inherited by this paired-contact, common-capstan visual layout. A candidate-specific installed BOM, cost and evidence record is required.']


def generate(root):
    root=Path(root)
    evaluation=json.loads(gzip.decompress((root/EVALUATION).read_bytes()))
    reference=json.loads((root/REFERENCE).read_bytes())
    sample=next(row for row in reference['content']['selected_samples'] if row['id']==SCENARIO)
    if sample['input']['effective_mass_kg']!=160000. or sample['physics']['sizing']['kind']!='hydraulic':
        raise ValueError('Exact hydraulic source control required')
    context=dict(source_scenario_id=SCENARIO,source_publication_id=reference['publication_id'],
        source_physics_evaluation_id=reference['producer_physics_evaluation_id'],
        reference_evaluation_id=evaluation['evaluation_id'],
        vehicle_reference_ids={k:evaluation[k] for k in ('candidate_id','body_candidate_id',
            'support_component_id','propulsion_component_id','selection_id')},
        visual_selection_purpose='Explain one mechanical research layout; not architecture selection',
        source_motion_is_point_mass=True,installation_candidate_adopted=False,**FLAGS)
    assemblies=[_overview(evaluation,sample,context),_storage(evaluation,sample,context),
                _launcher(evaluation,sample,context)]
    value=dict(schema='osr-visual-family/1',family='station',assemblies=assemblies,
        sources=[{'path':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest()}
            for name in (EVALUATION,REFERENCE,'engineering/station_energy/data/arrestor-scenario.json',
                         'engineering/station_rail/civil.py','engineering/station_rail/bim.py')],
        assumptions=_assumptions(),references=[],**FLAGS)
    value['visual_family_id']=hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
    return value
