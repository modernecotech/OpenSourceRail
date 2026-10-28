"""Materialize sparse wayside hardware and a disjoint stock/account ledger."""
from copy import deepcopy
from math import ceil
from pathlib import Path

from engineering.station_rail import ROOT, vehicle, civil
from engineering.station_rail.common import identity, digest
from engineering.design_search import design_grammar as grammar, system_body
from engineering.design_search import railway_bundle, station_accelerators, capabilities
from . import FLAGS
from . import propulsion

PRODUCER = 'engineering/railway_twin/model.py'
FAMILIES = ('gfrp_semimonocoque', 'aluminium_frame', 'aluminium_stressed_skin')


def body(family, root=ROOT):
    if family not in FAMILIES:
        raise ValueError('Explicit supported structural family required')
    parents = grammar.initial_candidates()
    if family == 'gfrp_semimonocoque':
        return parents[1]
    parent = parents[0 if family == 'aluminium_frame' else 2]
    return system_body.build(parent, topology=family, root=root)


def materialize(family='gfrp_semimonocoque', distance_m=2000., root=ROOT):
    root = Path(root)
    if type(distance_m) not in (int, float) or distance_m not in (1500., 2000.):
        raise ValueError('This experiment covers explicit 1500/2000 m interstation cells')
    candidate_body = body(family, root)
    motor = propulsion.materialize()
    bundle = railway_bundle.materialize(candidate_body, family='P1',
        motor_parameters=motor['parameters'], root=root)
    selected_civil = railway_bundle.assess_civil(bundle)['alternatives'][0]
    parent_id = bundle['bundle_id']
    priority = station_accelerators.specification(root)
    layout = next(r for r in priority['layouts'] if r['name'] == priority['priority']['lead_layout'])
    contact = station_accelerators._geometry(layout, 500., 104.5)
    case = bundle['architecture_case']
    physical = case['physical_definition']
    physical['route'] = dict(station_spacing_m=float(distance_m), tracks=1,
        scope='One directional interstation cell; return line, termini, depot and city remain additional design scope',
        counted_guideway_start_m=-120., counted_guideway_end_m=float(distance_m),
        actual_site_and_gradient_profile=None)
    physical['wayside'] = dict(motor_family='single-fin-double-sided-LIM',
        reference_motor_definition_id=bundle['propulsion_component_id'],
        primary_layout_name=layout['name'], primary_geometry_id=contact['physical_geometry_id'],
        sparse_geometry_id=contact['physical_geometry_id'], sparse_contact_evaluation_id=contact['geometry_result_id'],
        bank_starts_from_initial_nose_m=[x - 104.5 for x in layout['starts_m']],
        bank_length_m=layout['bank_length_m'],
        installed_linear_track_intervals_per_leg_m=[[x - 104.5, x - 104.5 + layout['bank_length_m']] for x in layout['starts_m']],
        primary_face_count=2 * len(layout['starts_m']),
        summed_bank_length_m=contact['summed_bank_length_m'],
        summed_primary_face_length_m=contact['primary_face_length_sum_m'],
        berth_nose_chainage_m=0., primary_stock_geometry_scope='Steel and equivalent-volume copper only; mounts, cabinet, wiring and cooling unresolved',
        receiving='Independent friction braking hypothesis; no receiving thrust or regeneration credited',
        station_energy_buffer=None, converter_and_feeder_definition=None,
        conductor_supply_track_m=0.)
    # Actual section/tendon stock is part of physical identity, not a result label.
    physical['guideway']['physical_civil_component_id'] = selected_civil['physical_civil_component_id']
    physical['guideway']['crowd_control_tendon_strands'] = selected_civil['prestress_strands']
    candidate_id = identity(physical)
    case.update(candidate_id=candidate_id, parent_case_ids=[case['case_id']],
                generation=case['generation'] + 1,
                commanded_power_windows_m=deepcopy(contact['required_launch_contact_union_m']))
    case['capability_composition'] = capabilities.composition('P1', candidate_id, case['requirement_revision'])
    case['case_id'] = identity({k:v for k,v in case.items() if k != 'case_id'})
    bundle.update(candidate_id=candidate_id, bundle_id=candidate_id, parent_bundle_id=parent_id,
        revision_reason='Materialize five short 20 m wayside banks, proposed 40-period motor, explicit friction receiving and one-cell route',
        sparse_primary_geometry_id=contact['physical_geometry_id'])
    bundle['brake_definition']['candidate_id'] = candidate_id
    brake = bundle['brake_definition']
    brake['brake_definition_id'] = identity({k:v for k,v in brake.items() if k != 'brake_definition_id'})
    bundle['source_sha256'].update({PRODUCER:digest(root / PRODUCER),
        'engineering/railway_twin/propulsion.py':digest(root / 'engineering/railway_twin/propulsion.py'),
        station_accelerators.SPEC:digest(root / station_accelerators.SPEC)})
    bundle['definition_id'] = identity({k:v for k,v in bundle.items() if k != 'definition_id'})
    railway_bundle.validate(bundle)
    return dict(body=candidate_body, bundle=bundle, contact_geometry=contact,
                propulsion=motor, selected_civil=selected_civil)


def _box(name, at, size, rho, material):
    volume = size[0] * size[1] * size[2]
    return dict(id=name, kind='box', at_m=list(at), size_m=list(size),
        volume_m3=volume, mass_kg=volume * rho, density_kg_m3=rho, material=material)


def civil_parts(selected):
    """Disjoint section walls and end diaphragms, matching the analytical stock."""
    d = selected['section']['dimensions']
    width, height, wall, flange = (d[k] for k in ('outer_width_m','depth_m','wall_m','flange_m'))
    span = selected['span_m']
    # Rail top is0; beam top is below the proposed rail/head assembly allowance.
    ztop = -.172
    rows = [_box('bottom', [0,-width/2,ztop-height], [span,width,flange],2500.,'concrete-hypothesis'),
            _box('top', [0,-width/2,ztop-flange], [span,width,flange],2500.,'concrete-hypothesis')]
    for side in (-1,1):
        y = -width/2 if side < 0 else width/2-wall
        rows.append(_box('wall/'+str(side), [0,y,ztop-height+flange],
                         [span,wall,height-2*flange],2500.,'concrete-hypothesis'))
    diaphragm = selected['diaphragm_definition']
    for i in range(diaphragm['quantity']):
        x = i * (span-diaphragm['thickness_m']) / max(1,diaphragm['quantity']-1)
        rows.append(_box('diaphragm/'+str(i), [x,-diaphragm['clear_width_m']/2,ztop-height+flange],
            [diaphragm['thickness_m'],diaphragm['clear_width_m'],diaphragm['height_m']],2500.,'concrete-hypothesis'))
    return rows


def ledger(model, inventory, root=ROOT):
    """Every known solid and residual account exactly once in its declared scope."""
    body, bundle = model['body'], model['bundle']
    candidate = bundle['candidate_id']
    reference = vehicle.build(root)
    occurrences, accounts = [], []
    component_by_stock = {c['occurrence_id']:c['component_definition_id'] for c in body['components']}

    def solid(name, part, translation, system, definition=None):
        occurrences.append(dict(id=name, component_definition_id=definition or identity(part),
            system=system, translation_m=list(translation), geometry=deepcopy(part),
            scope='equivalent-volume-stock' if part.get('geometry_status') == 'equivalent-volume-stock' else 'nominal-stock',
            mass_kg=part['mass_kg']))

    def account(name, mass, system, definition, reason):
        if mass is not None and mass < -1e-7:
            raise ValueError('Located stock exceeds retained account: ' + name)
        accounts.append(dict(id=name, candidate_id=candidate, component_definition_id=definition,
            system=system, accounted_mass_kg=None if mass is None else max(0.,mass),
            geometry=None, installed_CG_m=None, installed_inertia_kg_m2=None,
            price_USD=None, status='unlocated-or-unresolved', basis=reason))

    retained_parts = {
        'passive-bogie-pair':[p for p in reference['geometry_parts'] if p['id'].startswith('bogie/')],
        'passive-secondary':[p for p in reference['geometry_parts'] if p['id'].startswith('station-secondary/')]}
    for car in range(6):
        prefix, pose = 'car/'+str(car)+'/', [-8.5 - 17.5 * car,0.,0.]
        for part in body['parts']:
            solid(prefix+part['id'], part, pose, 'vehicle/body', component_by_stock[part['id']])
        for row in inventory['engineering_BOM']:
            if row['scope'] == 'retained-unlocated-reference-account':
                parts = retained_parts.get(row['id'], [])
                for part in parts:
                    solid(prefix+part['id'],part,pose,'vehicle/'+row['id'])
                located = sum(p['mass_kg'] for p in parts)
                remaining = None if row['accounted_mass_kg'] is None else row['accounted_mass_kg']-located
                account(prefix+row['id']+'/residual',remaining,'vehicle/'+row['id'],row['component_definition_id'],
                    'Retained account less explicitly depicted stock; no extra mass, location or completeness inferred')
            elif row.get('geometry') is None:
                account(prefix+row['id'],row.get('accounted_mass_kg'),'vehicle/joints-and-unresolved',
                        row.get('component_definition_id'),row['scope'])
    banks = bundle['architecture_case']['physical_definition']['wayside']['bank_starts_from_initial_nose_m']
    for bank, start in enumerate(banks):
        for part in model['propulsion']['wayside_stock']:
            solid('bank/'+str(bank)+'/'+part['id'],part,[start,0.,0.],'wayside/primary')
        for requirement in ('mounts-and-restraint','inverter-protection-feeder','cooling-and-services','isolation-and-maintenance-access'):
            account('bank/'+str(bank)+'/'+requirement,None,'wayside/installation',None,requirement)
    selected = model['selected_civil']
    distance = bundle['architecture_case']['physical_definition']['route']['station_spacing_m']
    guideway_start = bundle['architecture_case']['physical_definition']['route']['counted_guideway_start_m']
    spans = ceil((distance-guideway_start)/selected['span_m'])
    if abs(spans*selected['span_m']-(distance-guideway_start))>1e-9:
        raise ValueError('End-span design required for a nonintegral route length')
    for span in range(spans):
        start = guideway_start + span*selected['span_m']
        for part in civil_parts(selected):
            solid('span/'+str(span)+'/'+part['id'],part,[start,0.,0.],'civil/concrete')
        for side in (-1,1):
            # Equal-area stock rectangle counts rail mass, not the60E1 profile or clearance.
            width = civil.RAIL_KG_M/7850/.172
            rail = _box('rail/'+str(side), [0,side*.7175-width/2,-.172],
                [selected['span_m'],width,.172],7850.,'60E1-mass-equivalent')
            rail['geometry_status'] = 'equivalent-volume-stock'
            solid('span/'+str(span)+'/'+rail['id'],rail,[start,0.,0.],'civil/rails')
        for key in ('direct_fastener_kg','reinforcement_kg','prestress_kg','prestress_anchorage_kg'):
            account('span/'+str(span)+'/'+key,selected[key],'civil/unlocated-stock',None,
                    'Analytical allowance/stock; detailed fabrication and installed coordinates unresolved')
    for requirement in ('bearings','piers-headstocks','foundations-ground-site','station-platform-access-evacuation',
                        'drainage-containment-walkways','utility-power-room-and-grid','depot-rescue-tow-interfaces'):
        account('infrastructure/'+requirement,None,'civil/installation',None,requirement)
    scene = dict(schema='osr-railway-twin-scene/1',candidate_id=candidate,
                 occurrences=occurrences,complete_installed_geometry=False,**FLAGS)
    value = dict(schema='osr-railway-twin-ledger/1',candidate_id=candidate,
        body_candidate_id=body['candidate_id'],scene=scene,unlocated_accounts=accounts,
        scope='One six-car formation and one directional interstation cell; stock solids can overlap at unresolved joints, copper and rail profiles are equal-volume stock',
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,**FLAGS)
    value['ledger_id'] = identity(value)
    return value
