"""Three exact stock coupons paired with the retained N35UH rotating array."""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

from engineering.vehicle_optimisation import magnets
from engineering.passive_suspension import geometry
from . import FLAGS, ROOT

PROVENANCE = Path(__file__).with_name('data')/'provenance.json'
VARIANTS = {
    'slow-bias-gap12':dict(length_m=.05,bar_width_m=.04,bar_height_m=.02,columns=38,layers=10,
        gap_m=.012,pole_thickness_m=.04,voltage_V=144.,capacitance_F=.050,purpose='slow load/bias trim alongside the Halbach array',banks_per_car=1),
    'full-switch-gap12':dict(length_m=.05,bar_width_m=.04,bar_height_m=.02,columns=38,layers=10,
        gap_m=.012,pole_thickness_m=.04,voltage_V=144.,capacitance_F=.050,purpose='full EPM state switching comparison, not full Halbach cancellation',banks_per_car=24),
    'contact-cassette-coupon':dict(length_m=.03,bar_width_m=.01,bar_height_m=.01,columns=23,layers=10,
        gap_m=.0002,pole_thickness_m=.01,voltage_V=48.,capacitance_F=.050,purpose='contact cassette/parking coupon only; mechanical retraction and separate safety qualification missing',banks_per_car=None),
}


def encoded(value):
    return magnets.encoded(value)


def identity(value):
    return sha256(encoded(value)).hexdigest()


def material_sources(root=ROOT):
    source=json.loads(PROVENANCE.read_bytes())
    return dict(NdFeB=deepcopy(magnets.material_sources()['Arnold-N35UH']),
                AlNiCo=source['cast_alnico5'], magnetizing=source['magnetizing_guidance'],
                copper=geometry.material_table(root)['copper'], steel=geometry.material_table(root)['steel'],
                literature=source['literature'], physical_accepted=False)


def parent_halbach():
    # Same physical recipe as the retained half-volume/no-yoke refinement;
    # changing the label does not invent a new physical geometry or force map.
    return magnets._build(('N35-H8-half-no-yoke','planar-halbach','Arnold-N35UH',
                           dict(segments=8,magnet_volume_m3=.006)))


def _box(uid,size,at,material,density,role,**extra):
    return geometry._box(uid,size,at,material,density,'train',role,**extra)


def _build(name,root=ROOT):
    p=deepcopy(VARIANTS[name]);materials=material_sources(root);parent=parent_halbach()
    parts=deepcopy(parent['stock_parts']);added=[]
    x0=.57;w=p['bar_width_m'];h=p['bar_height_m'];length=p['length_m'];z0=-.075
    # Equal-length parallel bars share both endcaps. The common winding
    # surrounds both bars, matching the declared circuit, not three tilted PMs.
    spacing=.04;span=2*w+spacing;area=w*h
    for key,x,material,density in [('hard',x0,'Arnold-N35UH',materials['NdFeB']['density_kg_m3']),
                                   ('soft',x0+w+spacing,'EA-cast-Alnico5-typical',materials['AlNiCo']['density_kg_per_m3'])]:
        added.append(_box('epm/'+key,[w,length,h],[x,-length/2,z0],material,density,'parallel-EPM-magnet',
                          magnetization_axis=[0.,1.,0.],remanent_state='fixed-hard' if key=='hard' else 'unidentified-hysteretic-state'))
    pole=p['pole_thickness_m'];rho=materials['steel']['density_kg_m3']
    for side in (-1,1):
        y=-length/2-pole if side<0 else length/2
        added.append(_box('epm/endcap-'+str(side),[span,pole,h],[x0,y,z0],'steel',rho,'EPM-common-endcap'))
        legheight=-p['gap_m']-(z0+h)
        added.append(_box('epm/pole-leg-'+str(side),[span,pole,legheight],[x0,y,z0+h],'steel',rho,'EPM-rail-pole'))
    radial=.002;axial=.001;rpitch=.0028;apitch=.0013;clear=.001
    turns=p['columns']*p['layers'];coil=[]
    for layer in range(p['layers']):
        offset=clear+layer*rpitch
        xl=x0-offset-radial;xr=x0+span+offset+radial
        zb=z0-offset-radial;zt=z0+h+offset+radial
        for column in range(p['columns']):
            y=-p['columns']*apitch/2+column*apitch+(apitch-axial)/2
            uid=f'epm/pulse-coil/l{layer:02d}-t{column:02d}'
            for suffix,size,at in [('bottom',[xr-xl,axial,radial],[xl,y,zb]),
                    ('top',[xr-xl,axial,radial],[xl,y,zt-radial]),
                    ('left',[radial,axial,zt-zb-2*radial],[xl,y,zb+radial]),
                    ('right',[radial,axial,zt-zb-2*radial],[xr-radial,y,zb+radial])]:
                coil.append(_box(uid+'/'+suffix,size,at,'copper',materials['copper']['density_kg_m3'],'EPM-pulse-conductor'))
    added+=coil;parts+=added
    # This is passive test-facing extension, never onboard mass or a powered rail.
    maxx=max(q['at_m'][0]+q['size_m'][0] for q in added)
    extension=geometry._box('guideway/epm-coupon-extension',[maxx-.5+.01,.5,.035],[.5,-.25,0.],
                            'steel',rho,'guideway','passive-coupon-facing')
    parts.append(extension)
    copper_volume=math.fsum(q['volume_m3'] for q in coil);wire_area=radial*axial
    winding=dict(turns=turns,wire_area_m2=wire_area,wire_radial_m=radial,wire_axial_m=axial,
        layers=p['layers'],columns=p['columns'],radial_pitch_m=rpitch,axial_pitch_m=apitch,
        conductor_length_m=copper_volume/wire_area,copper_mass_kg=copper_volume*materials['copper']['density_kg_m3'],
        slot_fill=turns*wire_area/(length*p['layers']*rpitch),slot_fill_limit=.55,
        material_basis=materials['copper']['basis'],series_lead_driver_ESR_ohm=.03,
        inductance_H=None,inductance_sensitivity_H=[.0005,.005,.02],
        inductance_basis='Declared sensitivity values, not measured bounds containing the nonlinear circuit',
        pulse_duration_s=.020)
    unknown=deepcopy(parent['unknown_installed_inventory'])+[
        dict(id='epm/capacitor-bank',quantity=p['banks_per_car'],scope='per-car' if p['banks_per_car'] else 'installation-count-unknown',mass_kg=None,
             reason='Required C/V specified; package, ESR, ripple, life, containment and mass not selected'),
        dict(id='epm/H-bridge-selector-bus-protection',quantity=p['banks_per_car'],scope='per-car' if p['banks_per_car'] else 'installation-count-unknown',mass_kg=None,
             reason='Semiconductors, high-current selectors, fuse, clamp, charger and harness not counted'),
        dict(id='epm/retention-insulation-sensors',quantity=1,scope='per-module',mass_kg=None,
             reason='Cradle, adhesive, coatings, fasteners, insulation, calibrated state sensor and cooling are unsized')]
    train=[q for q in parts if q['group']=='train'];empty_floor=math.fsum(q['mass_kg'] for q in train)
    xmin=min(q['at_m'][0] for q in train);xmax=max(q['at_m'][0]+q['size_m'][0] for q in train)
    value=dict(schema='osr-epm-candidate/1',name=name,parent_magnet_id=parent['physical_id'],
        parent_bundle_sha256=parent['bundle_sha256'],parent_halbach=parent,parameters=p,
        units=dict(length='m',mass='kg',force='N',current='A'),
        frame=dict(handedness='right',x='travel',y='transverse-left',z='up'),
        architecture=dict(all_PM_and_coils='train',guideway='ordinary concrete with passive steel facing; no PM/powered suspension',
                          topology='equal-length parallel hard/soft EPM branches, common enveloping coil and two endcaps/pole legs',
                          fast_suspension_coil_required=True,existing_fast_coil_authority_qualified=False,
                          mechanical_parking_capture_and_door_locks_qualified=False,
                          contact_variant_can_travel=False if name=='contact-cassette-coupon' else None),
        materials=materials,stock_parts=parts,winding=winding,
        magnetic_circuit=dict(magnet_length_m=length,nd_area_m2=area,alnico_area_m2=area,pole_area_m2=span*pole,
                              gaps_m=[p['gap_m']]*2,steel_MMF_qualified=False,leakage_permeance_Wb_per_At=None,
                              internal_keeper_bridge_area_m2=pole*h,
                              ideal_zero_external_flux_Nd_shunt_B_T=materials['NdFeB']['br_20c_t']*area/(pole*h),
                              ideal_shunt_density_limit_T=1.5,
                              shunt_limit_basis='Declared conservative proxy necessary screen, not a certified steel limit; actual OFF state unknown',
                              hysteresis_loop=None,off_force_N=None,on_force_N=None),
        electrical=dict(capacitance_F=p['capacitance_F'],charge_voltage_V=p['voltage_V'],
                        stored_energy_J=.5*p['capacitance_F']*p['voltage_V']**2,
                        banks_per_car=p['banks_per_car'],pulse_circuits_per_reference_car=24,
                        scheduling='one module at a time' if p['banks_per_car']==1 else 'parallel comparison; installed circuit unqualified'),
        mass=dict(known_module_stock_kg=empty_floor,known_added_epm_stock_kg=math.fsum(q['mass_kg'] for q in added),
                  known_added_epm_stock_kg_per_reference_car=24*math.fsum(q['mass_kg'] for q in added),
                  installed_module_mass_kg=None,installed_car_mass_kg=None,complete_vehicle_AW3_kg=None,
                  pulse_hardware_mass_kg=None,unknowns_are_zero=False),
        packing=dict(reference_modules_per_car=24,banks=2,modules_per_bank=12,car_length_m=17.,
                     pitch_m=17/12,known_x_envelope_m=xmax-xmin,longitudinal_margin_m=17/12-(xmax-xmin),
                     installation_clearance_qualified=False),
        unknown_installed_inventory=unknown,parent_force_result_transferable=False,**FLAGS)
    physical=dict(parent_magnet_id=parent['physical_id'],
        parameters={k:v for k,v in p.items() if k!='purpose'},
        units=value['units'],frame=value['frame'],
        stock=[{k:q[k] for k in ('id','kind','size_m','at_m','material','group','role')} for q in parts],
        unknown_stock=[{k:q[k] for k in ('id','scope','quantity')} for q in unknown])
    value['candidate_id']=identity(physical)
    value['material_id']=identity(materials)
    value['bundle_sha256']=identity(value)
    return value


def candidates(root=ROOT):
    return [_build(name,root) for name in VARIANTS]


def validate(value,root=ROOT):
    name=value.get('name') if isinstance(value,dict) else None
    if name not in VARIANTS or value!=_build(name,root):
        raise ValueError('unsupported or modified EPM physical/material/mass bundle')
    return value


def field_geometry(value,root=ROOT):
    validate(value,root)
    raise ValueError('Finite-x paired EPM has no identified AlNiCo recoil/hysteresis law; fixed ±Br2D solves cannot prove switching or a rail force map')
