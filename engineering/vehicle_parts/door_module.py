"""Counted door-operator manufacturing proposal from a canonical vehicle child.

No installed transforms, mating dimensions, passing inspections or qualification
limits are inferred from stock dimensions or general process proposals.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
from engineering.station_rail.common import digest,identity
from engineering.vehicle_parts import catalogue,FLAGS
from engineering.design_search.craft_backends import solidcraft

PRODUCER='engineering/vehicle_parts/door_module.py'
_LOADED_SHA=digest(__file__)
ASSEMBLIES=('body/door-opening','services/door-electrical')
REPRESENTATIVE='body/door-header-backplate'
CASES=('low','base','high')


def _verify_bundle(bundle):
    if bundle.get('schema')!='osr-vehicle-manufacturing-bundle/1':
        raise ValueError('Canonical vehicle manufacturing bundle required')
    content={k:v for k,v in bundle.items() if k not in ('evaluation_id','bundle_id')}
    if bundle.get('evaluation_id')!=identity(content) or bundle.get('bundle_id')!=identity(dict(candidate_id=bundle['candidate_id'],evaluation_id=bundle['evaluation_id'])):
        raise ValueError('Sealed canonical manufacturing bundle required')
    if bundle['candidate_id']!=identity(bundle['physical_definition']):
        raise ValueError('Physical manufacturing identity differs')
    if any(bundle.get(k) is not False for k in FLAGS):
        raise ValueError('Unreleased manufacturing child required')
    if bundle['physical_definition']['parent_candidate_id']!=bundle['parent_candidate_id']:
        raise ValueError('Physical ancestry differs')
    materials={m['id']:m for m in bundle['materials']}
    projection=sorted((catalogue.component_projection(p,materials[p['material_id']]) for p in bundle['parts']),key=lambda p:p['id'])
    if projection!=bundle['physical_definition']['parts']:
        raise ValueError('Counted BOM differs from physical part definitions')
    if bundle['candidate_id']==bundle['parent_candidate_id']:
        raise ValueError('Manufacturing child must retain distinct ancestry')


def compile_module(bundle):
    _verify_bundle(bundle)
    assemblies={a['id']:a for a in bundle['assemblies'] if a['id'] in ASSEMBLIES}
    if set(assemblies)!=set(ASSEMBLIES) or any(a['quantity_per_train']!=12 for a in assemblies.values()):
        raise ValueError('Matched twelve mechanical/electrical door assemblies required')
    materials={m['id']:m for m in bundle['materials']}
    rows=[]
    for part in bundle['parts']:
        if part['assembly_id'] not in ASSEMBLIES:continue
        quantity=part['quantity_per_assembly']
        if (part.get('candidate_id')!=bundle['candidate_id'] or type(quantity) is not int or quantity<1
            or part['quantity_per_train']!=12*quantity
            or part['component_definition_id']!=identity(catalogue.component_projection(part,materials[part['material_id']]))):
            raise ValueError('Mixed candidate, component definition or expanded count')
        row=deepcopy(part)
        row['quantity_per_opening']=quantity
        row['installed_transform_m']=None
        row['inspection_plan']=[dict(criterion=x,approved_limit=None,observed_result=None,status='requires-controlled-limit-and-inspection') for x in part['inspection']]
        row['maintenance_plan']=dict(source_removal=part['maintenance_removal'],interval=None,
            interval_basis='Requires measured wear/duty and supplier limitations',replacement_verified=False)
        rows.append(row)
    if len({r['id'] for r in rows})!=len(rows) or any(not any(r['assembly_id']==a for r in rows) for a in ASSEMBLIES):
        raise ValueError('Complete unique owned mechanical/electrical leaves required')
    representative=next(r for r in rows if r['id']==REPRESENTATIVE)
    if representative['stock'].get('kind')!='box':raise ValueError('Representative explicit box stock required')
    # This origin defines a stock-blank coordinate frame, never an installed pose.
    stock_case=dict(case_id='door-operator-header-stock-blank',candidate_id=bundle['candidate_id'],
        source_evaluation_id=bundle['evaluation_id'],source_selection_id=bundle['parent_selection_id'],
        component_geometry_id=identity(dict(component_definition_id=representative['component_definition_id'],
            stock=representative['stock'],frame='blank-local corner, not installed')),
        entities=[dict(id=REPRESENTATIVE+'/stock-blank',shape='box',at_m=[0.,0.,0.],
            size_m=representative['stock']['size_m'],material=representative['material_id'])],
        materials={representative['material_id']:materials[representative['material_id']]},**FLAGS)
    script=solidcraft.script_for(stock_case)
    quantities={a:dict(assemblies_per_train=12,assemblies_per_opening=1,
        distinct_parts=sum(r['assembly_id']==a for r in rows),
        pieces_per_opening=sum(r['quantity_per_opening'] for r in rows if r['assembly_id']==a),
        pieces_per_train=sum(r['quantity_per_train'] for r in rows if r['assembly_id']==a)) for a in ASSEMBLIES}
    nominal={}
    for case in CASES:
        known=[r['quantity_per_opening']*r['mass_each_kg'][case] for r in rows if r['mass_each_kg'][case] is not None]
        unknown=[r['id'] for r in rows if r['mass_each_kg'][case] is None]
        nominal[case]=dict(known_subtotal_kg_per_opening=fsum(known),known_subtotal_kg_per_train=12*fsum(known),unknown_part_ids=unknown,
            complete_nominal_kg_per_opening=None if unknown else fsum(known),
            complete_nominal_kg_per_train=None if unknown else 12*fsum(known),
            basis='Declared gross stock and engineering allowances, not net installed mass')
    evidence=[
        dict(id='mating-dimensions',needed='Controlled header/guide/motor/leaf mating dimensions, datums and hole coordinates',affects=['drawings','assembly','CAD','QA']),
        dict(id='installed-placement',needed='Car-local transforms, mount load paths, adjacent service/tool/removal envelopes',affects=['installed-CAD','mass-properties','removal']),
        dict(id='functional-tolerances',needed='Derived bearing/guide fits, tolerance stack and weld/distortion limits; source general tolerances remain proposals',affects=['drawings','machining','QA']),
        dict(id='motion-clearance',needed='Finite door sweep with seals, 1.4x2.1m clear opening, platform/loading gauge and crush-gap limits',affects=['door-motion','accessibility','installation']),
        dict(id='force-duty',needed='Operator torque, belt/retention loads, current/thermal duty, manual-release force and degraded operation measurements',affects=['mechanics','electrical','QA','maintenance']),
        dict(id='safety-functions',needed='Independent obstruction/closed/locked/interlock verification, wiring/protection and isolation definitions',affects=['controls','QA','installation']),
        dict(id='process-qualification',needed='Material/finish/fire records, joining procedure, fastener retention and qualified inspection limits',affects=['manufacture','QA']),
        dict(id='service-life',needed='Supplier/rig wear-cycle evidence and access/removal trials to establish maintenance intervals',affects=['maintenance','replacement']),
    ]
    value=dict(schema='osr-door-module-proposal/1',candidate_id=bundle['candidate_id'],
        parent_candidate_id=bundle['parent_candidate_id'],source_bundle_id=bundle['bundle_id'],
        source_evaluation_id=bundle['evaluation_id'],parent_selection_id=bundle['parent_selection_id'],
        title='Mechanical door operator and separately owned electrical interface',
        opening_count_per_train=12,parts=rows,assembly_quantities=quantities,nominal_mass=nominal,
        installed_mass_kg_per_opening=None,installed_mass_kg_per_train=None,installed_CG_m=None,
        assembly_routes=[deepcopy(assemblies[a]) for a in ASSEMBLIES],
        tooling=sorted({tool for a in assemblies.values() for step in a['assembly_steps'] for tool in step['tools']}),
        representative_stock=dict(part_id=REPRESENTATIVE,component_definition_id=representative['component_definition_id'],
            units='m',dimensions_m=deepcopy(representative['stock']['size_m']),
            drawing_data=dict(frame='blank-local corner origin',dimensions_m=deepcopy(representative['stock']['size_m']),
                hole_coordinates_m=None,mating_datums=None,approved_tolerances=None,drawing_release=False),
            geometry_request=stock_case,solidcraft_commands=script,
            native_executed=False,installed_placement_verified=False,stock_only=True),
        excluded_scope=[dict(assembly_id='body/door-leaf',quantity_per_opening=2,reason='Separate owned leaf assembly; not counted inside operator'),
            dict(assembly_id='body/door-window',quantity_per_opening=2,reason='Separate glazing assembly ownership; not counted inside operator')],
        scope_limits=['Operator stock recipe and electrical interface are not a complete installed doorway',
            'Reference city fleet, vehicle cost and delivery outcomes are not inherited by this manufacturing child'],
        unresolved_inputs=evidence,fleet=None,city_cost=None,whole_life_cost=None,
        source_sha256={**bundle['source_sha256'],PRODUCER:_LOADED_SHA,
            solidcraft.__name__.replace('.','/')+'.py':digest(solidcraft.__file__)},**FLAGS)
    value['module_id']=identity(value)
    return value


def build(root=catalogue.ROOT):
    root=Path(root)
    if digest(root/PRODUCER)!=_LOADED_SHA:raise ValueError('Loaded door compiler changed; restart its caller')
    return compile_module(catalogue.build(root=root))
