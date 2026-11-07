"""Sourced shaft ratings and separately declared transmission/contact hypotheses.

These conditional ceilings are independently specified before motion is solved.
They are not measured force maps, VFD curves or automatic evaluator admission.
"""
from copy import deepcopy
from math import pi,sqrt
import json
from pathlib import Path
from engineering.station_rail.common import identity,digest
from . import ROOT,FLAGS

ABB='engineering/railway_progress/data/alternatives-sources.json'
TSA='engineering/design_search/data/tsa-type-x-drive-lead.json'
SOURCE='engineering/station_pair/profiles.py'


def build(bundle,distance_m,*,root=ROOT):
    root=Path(root)
    if bundle.get('candidate_id')!=identity(bundle['physical_definition']):
        raise ValueError('Exact parts physical candidate required')
    reference=bundle['physical_definition']['reference_interfaces']
    wheel_diameter=next(p for p in bundle['parts'] if p['id']=='running/wheel')['stock']['size_m'][0]
    radius=wheel_diameter/2
    abb=json.loads((root/ABB).read_bytes())['sources'];motor=abb[0]['facts'];rope=abb[1]['facts']['32mm']
    tsa=json.loads((root/TSA).read_bytes());rows=[]
    sources={ABB:digest(root/ABB),TSA:digest(root/TSA),SOURCE:digest(root/SOURCE)}
    for count in (6,12):
        for length in (200.,350.):
            ratio=5.;drum_radius=.96;ropes=2;eta=.92
            force=count*motor['rated_torque_Nm']*ratio/drum_radius*eta
            vmax=motor['rated_speed_rpm']*2*pi/60*drum_radius/ratio
            rope_length=2*length+2*pi*drum_radius
            external_mass=2500.+ropes*rope_length*rope['mass_kg_per_m']
            cap=ropes*(rope['minimum_breaking_force_N']*.85/5.-20000.)
            geometry=dict(motors=count,provisional_gear_ratio=ratio,drum_diameter_m=2*drum_radius,
                parallel_ropes=ropes,rope_diameter_m=.032,rope_loop_length_m_each=rope_length,
                powered_front_window_m=[0.,length],front_pull_interface=True,
                train_body_and_gap_length_m=105.25,passive_secondary_retained=True)
            row=dict(name=f'Cable / {count} motors / {length:g} m',family='cable',geometry=geometry,
                source_ids=[abb[0]['id'],abb[1]['id']],rated_force_ceiling_N=force,
                rated_mechanical_power_W=count*motor['shaft_power_W']*eta,maximum_model_speed_m_s=vmax,
                electrical_efficiency_hypothesis=motor['full_load_efficiency']*.97*eta,
                contact_force_hypothesis_N=cap,external_mass_kg=external_mass,external_resistance_N=2000.,
                onboard_added_mass_kg=dict(low=0.,base=0.,high=0.),
                inventory=[dict(id='station-reference-class-motor',quantity=count,location='per station departure lane',
                    catalogue_mass_each_kg=motor['catalogue_mass_kg'],source_id=abb[0]['id']),
                    dict(id='rope',quantity=ropes,length_m_each=rope_length,location='per station departure lane',
                    catalogue_mass_kg=ropes*rope_length*rope['mass_kg_per_m'],source_id=abb[1]['id']),
                    dict(id='return-tug',quantity=1,mass_hypothesis_kg=2500.,location='per station departure lane'),
                    dict(id='gear-drum-bearing-mounts',quantity=count,installed_mass_kg=None,location='per station departure lane'),
                    dict(id='guard-grip-tensioner-controls-cooling',quantity=1,installed_mass_kg=None,location='per station departure lane')],
                limitations=['Flat torque below the rated point requires an unreceived motor/inverter operating curve',
                    '5:1 transmission, efficiency, grip force, rope derating/preload/factor and external drag are hypotheses',
                    'Rope minimum breaking force is not working load or fatigue/termination/engagement qualification',
                    'Catalogue ambient and repeated-duty applicability at 50 C are not established',
                    'Detachable tug engagement, controlled release, return and rescue remain unvalidated'])
            rows.append(row)
    for count in (8,12):
        power=tsa['motor']['nominal_power_kW']*1000
        torque=power/(tsa['motor']['listed_speed_rpm']*2*pi/60)
        ratio=tsa['gearbox']['ratio'];eta=.95
        known=count*(tsa['motor']['listed_mass_kg']+tsa['gearbox']['listed_total_weight_including_couplings_kg'])
        rows.append(dict(name=f'Powered wheels / {count} driven axles',family='powered-wheel',
            geometry=dict(driven_axles=count,wheel_diameter_m=wheel_diameter,gear_ratio=ratio,
                powered_front_window_m=[0.,float(distance_m)],passive_secondary_retained=True,
                external_conductor_supply=True,traction_battery=False),source_ids=['tsa-type-x-public-lead'],
            rated_force_ceiling_N=count*torque*ratio/radius*eta,
            rated_mechanical_power_W=count*power*eta,
            electrical_efficiency_hypothesis=.90,
            maximum_model_speed_m_s=min(tsa['gearbox']['listed_max_vehicle_speed_km_h']/3.6,
                tsa['motor']['maximum_speed_rpm']*2*pi/60*radius/ratio),
            contact_force_hypothesis_N=None,external_mass_kg=0.,external_resistance_N=0.,
            onboard_added_mass_kg={k:known+r for k,r in [('low',2500.),('base',4000.),('high',8000.)]},
            inventory=[dict(id='traction-motor',quantity=count,catalogue_mass_each_kg=486.,location='train'),
                dict(id='gearbox-including-couplings',quantity=count,catalogue_mass_each_kg=310.,location='train'),
                dict(id='inverter-cooling-mounting-collector-reserve',quantity=1,location='train',
                    mass_hypothesis_kg=dict(low=2500.,base=4000.,high=8000.)),
                dict(id='conductor-protection-feeder',quantity=2*distance_m,unit='track-m',location='line')],
            limitations=['New driven running-gear configuration; actual axle loads, mounting and mass overlap are unresolved',
                'Rated torque is calculated from rated power/speed; starting torque is not used as continuous torque',
                'Constant torque/power interpolation, gearbox efficiency, inverter and thermal duty are hypotheses',
                'Driven-axle normal-load fraction is a study assumption, not a computed adhesion guarantee',
                'The 760 mm wheel is a modified application; proposed 680 mm worn diameter is below the source 716 mm minimum',
                'Conductor supply/protection, recovery and failure isolation require detailed design']))
    for family,name in [('compact-LIM','Compact LIM / 100 m bank'),('hybrid','Mechanical starter + compact LIM')]:
        rows.append(dict(name=name,family=family,geometry=dict(LIM_bank_length_m=100.,
            mechanical_starter=family=='hybrid',passive_secondary_retained=True),
            source_ids=[],rated_force_ceiling_N=None,rated_mechanical_power_W=None,
            maximum_model_speed_m_s=None,contact_force_hypothesis_N=None,external_mass_kg=None,
            onboard_added_mass_kg=None,inventory=[],
            limitations=['No candidate-specific admitted or conditional full force profile supplied',
                'A 100 m bank is one research geometry, not the mandatory reference',
                'Hybrid booster cannot inherit a required-force curve as available thrust']))
    for row in rows:
        physical=dict(schema='osr-station-pair-architecture/1',body_candidate_id=bundle['candidate_id'],
            family=row['family'],geometry=row['geometry'],station_spacing_m=distance_m,
            inventory=row['inventory'])
        row.update(candidate_id=identity(physical),physical_definition=physical,
            body_candidate_id=bundle['candidate_id'],body_bundle_id=bundle['bundle_id'],
            source_sha256=deepcopy(sources),evidence_maturity='conditional rating envelope; not admitted operating map',
            admitted_operating_map=False,**FLAGS)
    return rows


def force_profile(variant,*,mass_kg,case,adhesion,brief,grade=0.):
    if variant['rated_force_ceiling_N'] is None:return None
    fraction=brief['force_rating_fraction_hypothesis'][case]
    cap=variant['contact_force_hypothesis_N']
    if variant['family']=='powered-wheel':
        cap=adhesion*mass_kg*9.80665*variant['geometry']['driven_axles']/24/sqrt(1+grade**2)
    vmax=variant['maximum_model_speed_m_s']
    power=variant['rated_mechanical_power_W']*fraction
    ceiling=variant['rated_force_ceiling_N']*fraction
    speeds=[i*vmax/24 for i in range(24)]+[vmax]
    return dict(points=[dict(speed_m_s=v,force_n=min(ceiling,power/v) if v else ceiling) for v in speeds],
        windows_m=[variant['geometry']['powered_front_window_m']],maximum_speed_m_s=vmax,
        mechanical_power_w=power,electrical_efficiency=variant['electrical_efficiency_hypothesis'],
        grid_power_w=variant['rated_mechanical_power_W']/variant['electrical_efficiency_hypothesis'],
        contact_force_cap_n=cap,external_mass_kg=variant['external_mass_kg'],
        external_resistance_n=variant['external_resistance_N'])
