"""Re-evaluate a span from exact body loads, then count a mapped corridor.

No old1500m pilot cost, old motor mass or old beam FEM is imported. The existing
span method is retained as an independently identifiable analytical evaluation.
Its pilot route quantities and120s fatigue schedule are explicitly discarded.
"""
from copy import deepcopy
from math import ceil, fsum, isfinite, isclose
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from engineering.pilot_civil import design
from engineering.design_search import civil_shape_geometry
from .route import FLAGS

PRODUCER='engineering/railway_project/civil.py'
G=9.80665


def sealed(value, key='evaluation_id'):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Sealed same-candidate '+key+' required')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Research component cannot confer acceptance')
    return value


def source_union(*packets, root=ROOT):
    result={};base=Path(root).resolve()
    for packet in packets:
        for name,want in packet['source_sha256'].items():
            p=Path(name)
            if p.is_absolute() or '..' in p.parts or not (base/p).resolve().is_relative_to(base):
                raise ValueError('Ordinary in-root engineering source required')
            if name in result and result[name]!=want:
                raise ValueError('Mixed engineering source epochs: '+name)
            if digest(base/p)!=want:
                raise ValueError('Engineering source changed: '+name)
            result[name]=want
    result[PRODUCER]=digest(base/PRODUCER)
    return result


def axle_packet(body, *, line_equipment, root=ROOT):
    sealed(body)
    if body.get('schema')!='osr-vehicle-installation/1' or body['candidate_id']!=identity(body['physical_definition']):
        raise ValueError('Exact counted body physical definition required')
    ownership=body.get('compact_drive_contract',{}).get('mass_ownership',{})
    if ownership.get('all_new_drive_components_in_body_BOM') is not True or ownership.get('additional_external_drive_mass_kg')!=0:
        raise ValueError('Counted drive ownership required; no legacy drive addition')
    required={p+'-'+c for p in ('tare','normal','crowd-control') for c in ('low','base','high')}
    cases=body['mass_scenarios']
    if len(cases)!=9 or {r['name'] for r in cases}!=required:
        raise ValueError('Tare, normal and crowd structural load bounds required')
    rows=[]
    for row in cases:
        if len(row['axles'])!=24 or len({a['id'] for a in row['axles']})!=24:
            raise ValueError('24 unique located axle reactions required')
        mass=row['train_mass_kg'];cg=row['CG_m']
        if any(type(v) not in (int,float) or not isfinite(v) for v in (mass,*cg)) or mass<=0:
            raise ValueError('Finite mass and CG required')
        force=fsum(a['vertical_force_N'] for a in row['axles'])
        moment=fsum(a['vertical_force_N']*a['x_m'] for a in row['axles'])
        if abs(force-mass*G)>1e-7*mass*G or abs(moment-mass*G*cg[0])>1e-7*max(1.,mass*G*abs(cg[0])):
            raise ValueError('Body mass, CG and axle reactions do not conserve load')
        rows.append({k:deepcopy(row[k]) for k in ('name','train_mass_kg','axles','CG_m','lateral_acceleration_m_s2')})
    result=dict(schema='osr-pilot-axle-loads/1',candidate_id=body['candidate_id'],
        vehicle_candidate_id=body['candidate_id'],mass_evaluation_id=body['evaluation_id'],
        track_interface=deepcopy(body['policy']['track_interface']),load_cases=rows,
        line_equipment=deepcopy(line_equipment),source_sha256=source_union(body,root=root),
        external_drive_mass_added_kg=0.,zero_is_exact_already_counted_drive=True,
        scope='All nine located body load bounds, including existing reserves and24counted drives; no old9552kg append or inherited civil proof',
        installed_mass_complete=body['installed_mass_complete'],**FLAGS)
    result['evaluation_id']=identity(result)
    design.validate_train(result,root)
    return result


def physical_projection(span):
    """Explicit geometry/material specification; prices/proof/density are evaluations."""
    p=span['physical_definition'];stock=p['beam_stock'];rebar=p['reinforcement']
    bar_keys=('longitudinal_bars','longitudinal_cut_length_m','longitudinal_cut_pieces','longitudinal_total_m',
        'stirrup_count','stirrup_cut_length_m','stirrup_pitch_m','bar_bend_radius_m',
        'longitudinal_diameter_m','stirrup_diameter_m','cage_path_yz_m')
    value=dict(schema='osr-project-civil-span-geometry/1',
        beam_stock={k:deepcopy(stock[k]) for k in ('span_m','deck_width_m','coordinate_frame','cells')},
        material_specification=dict(concrete_strength_target_Pa=span['policy']['research_concrete_strength_Pa'],
            reinforcement='B500-class research specification',prestress='strand target specification from geometry and material policy'),
        reinforcement={k:deepcopy(rebar[k]) for k in bar_keys},prestress_geometry=deepcopy(p['prestress_geometry']),
        segment_count=p['segment_count'],
        segment_joint=None if p['segment_joint'] is None else {k:deepcopy(p['segment_joint'][k]) for k in ('at_x_m','method','closure_width_m')},
        bearing_layout=deepcopy(p['bearing_layout']),support_geometry=deepcopy(p['support_geometry']),
        drainage=deepcopy(p['drainage']),maintenance_walkway_width_m=p['maintenance_walkway']['width_m'],
        rail_interface={k:deepcopy(p['rail_interface'][k]) for k in ('rails','rail_kg_m','fastenings','anchors_per_set',
            'fastener_plate_size_m','rail_head_envelope_height_m','rail_foot_envelope_width_m','rail_web_envelope_width_m')},
        track_interface={k:deepcopy(p['rail_interface']['track_interface'][k]) for k in
            ('inner_face_gauge_m','nominal_rail_head_width_m','nominal_contact_centres_y_m','contact_datum')})
    conductor=p.get('wayside_conductor_and_supports')
    if conductor is not None:
        value['wayside_conductor_geometry']={k:deepcopy(conductor[k]) for k in ('cross_section_m2','lateral_offset_from_track_centre_m')}
    return value


def count_corridor(span, alignment, *, headway_s, operation_hours_day, operation_days_year, design_life_years, root=ROOT):
    sealed(span);sealed(alignment)
    if span.get('schema')!='osr-pilot-civil-evaluation/1' or alignment.get('schema')!='osr-station-straight-alignment/1':
        raise ValueError('Exact analytical span and designed mapped alignment required')
    if (span['civil_candidate_id']!=identity(span['physical_definition']) or
        alignment['candidate_id']!=identity(alignment['physical_definition'])):
        raise ValueError('Civil/alignment physical identity differs')
    stock=span['physical_definition']['beam_stock']
    if stock!=span['section']['physical']:
        raise ValueError('Analytical section and physical beam geometry differ')
    quantities=civil_shape_geometry.quantities(stock)
    if (not isclose(quantities['total_nominal_volume_m3'],span['quantities']['concrete_beam_m3'],rel_tol=1e-12)
        or not isclose(quantities['total_nominal_stock_mass_kg'],span['quantities']['nominal_concrete_mass_kg'],rel_tol=1e-12)):
        raise ValueError('Analytical span stock volume/mass differs from geometry')
    for name,value in dict(headway_s=headway_s,operation_hours_day=operation_hours_day,
        operation_days_year=operation_days_year,design_life_years=design_life_years).items():
        if type(value) not in (int,float) or not isfinite(value) or value<=0:
            raise ValueError('Explicit positive service/calendar input required: '+name)
    if operation_hours_day>24 or operation_days_year>366 or design_life_years>100:
        raise ValueError('Civil duty calendar outside declared research domain')
    length=alignment['route_m'];p=deepcopy(span['policy']);p['route_m']=length
    # Re-count physical quantities/rates, not old pilot dollars per kilometre.
    cost=design.estimate(span['quantities'],span['foundation'],span['physical_definition']['segment_count']==2,p)
    span_geometry=physical_projection(span);bays=ceil(length/p['span_m']);nominal=bays*p['span_m']
    physical=dict(schema='osr-project-civil-layout/1',span_geometry=span_geometry,
        alignment_candidate_id=alignment['candidate_id'],tracks=2,track_centres_y_m=deepcopy(p['track_centres_y_m']),
        bays=bays,standard_span_m=p['span_m'],shared_bent_chainages_m=[i*p['span_m'] for i in range(bays+1)],
        nominal_covered_route_m=nominal,station_centre_to_centre_route_m=length,
        final_standard_bay_overrun_m=nominal-length)
    cid=identity(physical)
    result=dict(schema='osr-project-civil-evaluation/1',candidate_id=cid,physical_definition=physical,
        vehicle_candidate_id=span['vehicle_candidate_id'],body_evaluation_id=span['mass_evaluation_id'],
        input_load_evaluation_id=span['input_load_evaluation_id'],span_evaluation_id=span['evaluation_id'],
        alignment_candidate_id=alignment['candidate_id'],alignment_evaluation_id=alignment['evaluation_id'],
        cost=cost,quantities=dict(beams=2*bays,shared_bents=bays+1,main_running_track_m=2*length,
            nominal_span_track_m=2*nominal,nominal_rail_stock_m=4*nominal,terminal_credit_track_m=2*(nominal-length)),
        service_duty=dict(headway_s=headway_s,passes_per_track_year=3600/headway_s*operation_hours_day*operation_days_year,
            full_axle_cycles_per_track=24*3600/headway_s*operation_hours_day*operation_days_year*design_life_years,
            design_life_years=design_life_years,fatigue_resistance_verified=False),
        source_sha256=source_union(span,alignment,root=root),
        old_pilot_cost_and_fatigue_schedule_imported=False,old_native_FEM_inherited=False,
        holds=['Analytical gross span checks retain all source bearing/joint/cracking/fatigue/erection limitations.',
               'Station buildings, platform supports, terminal/crossover structure and site utilities are separate positive project accounts.',
               'Final standard-bay overrun must credit the terminal structure/rail quantity ledger once; it is not extra free running length.',
               'Curved-route chord positions, rail offsets/cant, complete transverse loads and site foundations require installed design checks.'],**FLAGS)
    result['evaluation_id']=identity(result)
    return result
