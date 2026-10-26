"""Twelve source-bound seat/door component fixtures, separate from vehicle mass.

Loads, supports and deflection screens are research hypotheses, not rail
standards. Passing these simple elastic fixtures does not qualify a component.
"""
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
SCHEMA='osr-seat-door-component-fixtures/1'
FLAGS=dict(engineering_accepted=False,physical_validation=False,physical_accepted=False,
           configuration_adopted=False,manufacturing_release=False,physical_release=False,
           installed_mass_closed=False)
SOURCE_FILES=('engineering/vehicle_optimisation/equipment.py',
              'engineering/ferrite_maglev/closure.toml',
              'engineering/ferrite_maglev/station-structure.toml')
CORE_URL='https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-sep-2025-rev25-si.pdf'
HYDRO_URL='https://www.hydro.com/globalassets/01-products--services/extruded-profiles/americas/ena-resources/alloy-data-sheets/hydro_2019_data_sheet_6005a_revise_1.pdf'
OPERATOR_URL='https://transitworld.wabtec.com/media/es2-datasheet'


def _identity(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _stock(name,volume,density,quantity=1,**extra):
    return dict(id=name,quantity=quantity,volume_m3_each=volume,density_kg_m3=density,
                mass_kg=volume*density*quantity,**extra)


def rhs(width,depth,wall):
    if not all(math.isfinite(v) and v>0 for v in (width,depth,wall)) or 2*wall>=min(width,depth):
        raise ValueError('positive RHS dimensions and nonempty bore required')
    area=width*depth-(width-2*wall)*(depth-2*wall)
    moment=(width*depth**3-(width-2*wall)*(depth-2*wall)**3)/12
    return dict(area_m2=area,I_m4=moment,Z_m3=2*moment/depth)


def _materials(root):
    a=tomllib.loads((root/SOURCE_FILES[1]).read_text())
    # Existing project constants are study values, not a laminate certificate.
    mechanics=a['mechanics'] if 'mechanics' in a else a['materials']
    return dict(gfrp_E_Pa=mechanics['gfrp_longitudinal_e_pa'],
                gfrp_strength_Pa=mechanics['gfrp_strength_pa'],
                aluminium_E_Pa=69e9,aluminium_proof_Pa=240e6,
                gfrp_density_kg_m3=1900.,aluminium_density_kg_m3=2700.,
                core_density_kg_m3=80.,core_G_Pa=23e6,core_shear_strength_Pa=.95e6,
                factor_on_material_strength_hypothesis=1.5,
                source_scope='GFRP project constants; Al properties inherited from equipment.py producer reference; H80 minimum room-temperature table values',
                references=[dict(url=CORE_URL,version='September2025 revision25 SI',
                                 use='H80 density80kg/m3; minimum shear modulus23MPa and shear strength0.95MPa, measured at23C; hot/wet/fire behaviour unqualified'),
                            dict(url=HYDRO_URL,use='Existing project6061-T6 proof-strength reference240MPa; exact extrusion thickness/temper, joints and heat-affected zones need qualification')])


def pan_fixture(*,width,span,face,core,load,young,core_G=23e6):
    """Simply supported uniformly loaded strip; core normal stiffness omitted."""
    if not all(math.isfinite(v) and v>0 for v in (width,span,face,load,young)) or core<0:
        raise ValueError('finite positive pan dimensions/load/modulus required')
    thickness=face if core==0 else core+2*face
    inertia=width*thickness**3/12 if core==0 else width*(thickness**3-core**3)/12
    moment=load*span/8
    bending=5*load*span**3/(384*young*inertia)
    shear=0. if core==0 else load*span/(8*core_G*width*core)
    return dict(load_N=load,span_m=span,width_m=width,total_depth_m=thickness,
                face_I_m4=inertia,face_stress_Pa=moment*thickness/2/inertia,
                core_shear_Pa=None if core==0 else load/(2*width*core),
                bending_deflection_m=bending,shear_deflection_m=shear,
                total_deflection_m=bending+shear,
                small_deflection_domain=(bending+shear)/span<=.02,
                support_hypothesis='Simply supported at front/back; full-area uniform vertical load. Contact indentation and backrest loads excluded')


def beam_fixture(*,width,depth,wall,span,total_load,young=69e9):
    """Two equal rails carry a conservative central force, half on each rail."""
    if not all(math.isfinite(v) and v>0 for v in (span,total_load,young)):
        raise ValueError('positive finite beam span, load and modulus required')
    section=rhs(width,depth,wall)
    per_rail=total_load/2
    return dict(section=section,span_m=span,total_load_N=total_load,rails=2,
                stress_Pa=per_rail*span/(4*section['Z_m3']),
                deflection_m=per_rail*span**3/(48*young*section['I_m4']),
                support_hypothesis='Two simply supported cross-car rails; total bench load split equally, concentrated at rail midspan')


def _finish(v,sources):
    v.update(schema=SCHEMA,source_sha256=sources,execution='completed',
             evidence_maturity='analytical-component-fixture',physical_acceptance='hold',
             installed_mass_kg=None,applied_to_composed_vehicle=False,
             fixture_temperature_C=23.,hot_weather_qualified=False,**FLAGS)
    v['component_id']=_identity(v['physical_definition'])
    v['evaluation_id']=_identity(v)
    return v


def _bench(panel,depth,m,sources):
    kind,face,core=panel
    pair_width=.94; seat_width=.45; seat_depth=.48; back_height=.60
    material_width=2*seat_width if core==0 else pair_width
    # The negative control preserves the inherited2mm material construction;
    # this counted two-place support fixture is a new interface, not a stock
    # removal or a changed layout.py seat allowance.
    rows=[_stock('pan/skins',material_width*seat_depth*(face if core==0 else 2*face),1900.),
          _stock('back/skins',material_width*back_height*(face if core==0 else 2*face),1900.)]
    perimeter=2*(pair_width+seat_depth)+2*(pair_width+back_height)
    if core:
        rows += [_stock('pan-back/H80-core',pair_width*(seat_depth+back_height)*core,80.),
                 _stock('panel/GFRP-edge-closure',perimeter*(core+2*face)*.001,1900.),
                 _stock('panel/bond',2*pair_width*(seat_depth+back_height)*.0002,1200.)]
    section=rhs(.03,depth,.002)
    rows += [_stock('support/Al-RHS-rails',section['area_m2']*pair_width,2700.,2),
             _stock('support/Al-RHS-legs',section['area_m2']*.42,2700.,4),
             _stock('back/Al-RHS-uprights',rhs(.03,.03,.002)['area_m2']*.65,2700.,2),
             _stock('mount/Al-footplates',.08*.06*.004,2700.,4),
             _stock('mount/M8-fastener-stock',math.pi*(.008/2)**2*.05+math.pi*(.014/2)**2*.01,7850.,16),
             _stock('pan/foam-pad',material_width*seat_depth*.03,50.)]
    # Two separate pans in the thin control, one continuous pair-bench pan
    # in the sandwich proposals, with the same1.5kN per seated place.
    pan=pan_fixture(width=seat_width if core==0 else pair_width,span=seat_depth,
                    face=face,core=core,load=1500. if core==0 else 3000.,young=m['gfrp_E_Pa'])
    beam=beam_fixture(width=.03,depth=depth,wall=.002,span=pair_width,total_load=3000.)
    total_deflection=pan['total_deflection_m']+beam['deflection_m']
    checks=dict(pan_face_stress=pan['face_stress_Pa']<=m['gfrp_strength_Pa']/1.5,
                core_shear=True if core==0 else pan['core_shear_Pa']<=m['core_shear_strength_Pa']/1.5,
                rail_elastic_stress=beam['stress_Pa']<=m['aluminium_proof_Pa']/1.5,
                combined_research_deflection=total_deflection<=.005,
                pan_small_deflection_domain=pan['small_deflection_domain'])
    physical=dict(component='two-place-bench',panel=kind,pan_face_each_or_monolithic_m=face,
                  core_m=core,pan_width_m=material_width,seat_modules_m=[.47,.47],
                  clear_pan_per_place_m=.45,pan_depth_m=seat_depth,back_height_m=back_height,
                  support_RHS_m=[.03,depth,.002],rail_span_m=pair_width,
                  leg_count=4,leg_height_m=.42,stock_parts=rows)
    return _finish(dict(component='bench',name=f'{kind} on30x{depth*1000:g}x2mm Al rails',
        mass_basis='per two-place bench/pair-seat fixture',counted_mass_kg=math.fsum(r['mass_kg'] for r in rows),
        stock_parts=rows,physical_definition=physical,necessary_screen='pass' if all(checks.values()) else 'fail',
        fixture_checks=checks,fixtures=dict(pan=pan,rails=beam,total_vertical_deflection_m=total_deflection),
        research_load_N_per_place=1500.,research_deflection_limit_m=.005,
        load_is_rail_standard=False,numerical_validity='valid-linear-fixture' if pan['small_deflection_domain'] else 'outside-linear-pan-domain',
        negative_control=core==0,materials=m,
        comparison_scope='Two occupied places; backrest/leg/anchor stock counted but only pan and transverse rails screened. No material substitution applied to installed layout or800kg interior account.',
        unknown=['Leg-frame eccentricity, buckling, bracing, weld/bolt strength and body anchorage',
                 'Backrest, restraint, fatigue, crash, fire, hot/wet laminate/core behaviour and local indentation',
                 'Actual seat/back contours, upholstery, assembly access and matching carrier/body interfaces']),sources)


def _door(kind,skin,core,edge_wall,m,sources):
    # One opening contains two0.7x2.1m leaves with one0.5m2 window per leaf.
    width=.7;height=2.1;window_area=.5;opaque=width*height-window_area
    edge_depth=core # Cold-formed/extruded edge envelope is a new detail.
    edge=rhs(.03,edge_depth,edge_wall)
    rows=[_stock('door/Al-skins',2*opaque*skin,2700.,2),
          _stock('door/H80-core',opaque*core,80.,2),
          _stock('door/Al-edge-RHS',edge['area_m2']*2*(width+height),2700.,2),
          _stock('door/seals',2*(1.4+height)*.0001,1200.),
          _stock('door/bond',2*opaque*.0004,1200.),
          _stock('door/M8-stock-fasteners',math.pi*(.008/2)**2*.05+math.pi*(.014/2)**2*.01,7850.,8,
                 purpose='Proposed leaf-edge retention; operator-package fasteners are not duplicated')]
    # A deliberately declared whole-leaf strip fixture transfers uniform1kPa
    # pressure to top/bottom supports. Its central1m window leaves0.2m of
    # sandwich breadth; no glass stiffness is credited. The retained outer
    # RHS edges contribute EI. This is not the actual hanger/guide system.
    pressure=1000.;load_per_length=pressure*width;young=m['aluminium_E_Pa']
    total_depth=core+2*skin
    def inertia(breadth):
        return breadth*(total_depth**3-core**3)/12+2*edge['I_m4']
    full_I=inertia(width);window_I=inertia(width-.5)
    half=height/2;window_start=(height-1.)/2
    def primitive(z): return height*z**3/3-z**4/4
    bending=load_per_length/2/young*(primitive(window_start)/full_I+
              (primitive(half)-primitive(window_start))/window_I)
    def shear_primitive(z): return height*z/2-z*z/2
    shear=load_per_length/(m['core_G_Pa']*core)*(shear_primitive(window_start)/width+
              (shear_primitive(half)-shear_primitive(window_start))/(width-.5))
    total=bending+shear;moment=load_per_length*height**2/8
    face_stress=moment*total_depth/2/window_I
    core_shear=max(load_per_length*height/(2*width*core),
                   load_per_length*(half-window_start)/((width-.5)*core))
    checks=dict(face_and_edge_stress=face_stress<=m['aluminium_proof_Pa']/1.5,
                core_shear=core_shear<=m['core_shear_strength_Pa']/1.5,
                research_deflection=total<=.010,linear_domain=total/height<=.02)
    physical=dict(component='two-leaf-door',leaf_size_m=[width,height],leaves=2,
                  window_size_m=[.5,1.],window_void_m2_each=.5,
                  skin_each_m=skin,core_m=core,edge_RHS_m=[.03,edge_depth,edge_wall],stock_parts=rows,
                  operator_reference_mass_kg=41.,operator_reference_width_m=1.3,proposed_clear_width_m=1.4)
    baseline_opaque=2*opaque*2*.0008*2700+2*opaque*.025*80+2*rhs(.03,.025,.002)['area_m2']*2*(width+height)*2700+2*(1.4+height)*.0001*1200+2*opaque*.0004*1200
    known=math.fsum(p['mass_kg'] for p in rows)
    return _finish(dict(component='door',name=kind,mass_basis='per1.4m two-leaf opening; glazing excluded, operator reference separate',
        counted_mass_kg=known,stock_parts=rows,physical_definition=physical,
        supplier_operator_reference_mass_kg=41.,material_plus_operator_reference_kg=known+41.,
        operator_source=dict(url=OPERATOR_URL,existing_project_source=SOURCE_FILES[0],
                             reference='ES2 operator27kg +hanger14kg at1300mm; proposed1400mm integration unqualified'),
        retained_reference_leaf_stock_per_door_kg=baseline_opaque,
        reference_scope='Matches original Al0.8mm/25mm core/30x25x2mm edge opaque stock before adding explicit common fastener stock. No original allocation is removed again.',
        necessary_screen='pass' if all(checks.values()) else 'fail',fixture_checks=checks,
        fixture=dict(pressure_Pa=pressure,span_m=height,full_panel_I_m4=full_I,window_ligament_I_m4=window_I,
                     bending_deflection_m=bending,core_shear_deflection_m=shear,total_deflection_m=total,
                     maximum_face_stress_Pa=face_stress,core_shear_Pa=core_shear,
                     support='Simply supported top/bottom;0.5x1m central window interrupts sandwich; no pane stiffness credit',
                     limit_m=.010,limit_is_rail_standard=False),
        numerical_validity='valid-linear-fixture' if checks['linear_domain'] else 'outside-linear-fixture-domain',
        materials=m,comparison_scope='Current leaf-stock construction plus two deeper-core/lightened-edge alternatives; no change to composed mass or41kg operator reference',
        unknown=['Actual hanger/roller/guide loads and window-frame/racking load path; uniform fixture pressure is not route wind qualification',
                 'Leaf depth, track recess, seals, latches, anti-trap, emergency egress and operator compatibility',
                 'Fire, fatigue, impact, corrosion, coating and hot/wet bond/core properties',
                 'Glazing/retention owned separately; no pane mass or stiffness credit here']),sources)


def options(*,root=ROOT):
    root=Path(root)
    sources={name:sha256((root/name).read_bytes()).hexdigest() for name in SOURCE_FILES}
    sources['engineering/comfort_options/seats_doors.py']=sha256(Path(__file__).read_bytes()).hexdigest()
    m=_materials(root)
    panels=[('GFRP2mm-negative-control',.002,0.),('GFRP1mm-H80-20mm',.001,.020),
            ('GFRP0.8mm-H80-30mm',.0008,.030)]
    benches=[_bench(panel,depth,m,sources) for panel in panels for depth in (.030,.040,.050)]
    doors=[_door(kind,skin,core,wall,m,sources) for kind,skin,core,wall in (
           ('Retained Al0.8mm/core25mm/edge2mm',.0008,.025,.002),
           ('Al0.6mm/core35mm/edge1.5mm',.0006,.035,.0015),
           ('Al0.5mm/core40mm/edge1.2mm',.0005,.040,.0012))]
    return benches+doors


def validate(value,*,root=ROOT):
    expected=next((r for r in options(root=root) if r['component_id']==value.get('component_id')),None)
    if expected is None or value!=expected:
        raise ValueError('component identity, source, mass or fixture result differs')
    return True
