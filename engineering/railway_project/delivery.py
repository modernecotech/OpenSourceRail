"""Mapped records to an unapproved manufacturing-planning proposal.

The business protocol retains its historical field name ``study_id``. Here it
identifies an explicit mapped delivery context, never a synthetic closure study.
This compiler performs no geometry, solver, native-receipt or business execution.
"""
from collections import Counter
from copy import deepcopy
from math import ceil, fsum, isclose
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.pilot_delivery import model
from engineering.pilot_delivery import FLAGS
from engineering.design_search.model_cost import SCOPES
from engineering.station_pair.lifecycle import OWNER_SCOPES, _cases
from .civil import sealed, source_union
from .cost import GROUPS
from . import part_accounts

PRODUCER = 'engineering/railway_project/delivery.py'
DEPENDENCIES = ('engineering/railway_project/cost.py', 'engineering/station_pair/lifecycle.py',
                'engineering/design_search/model_cost.py', part_accounts.PRODUCER)
SCHEMAS = ('osr-mapped-railway-project-bundle/1', 'osr-vehicle-installation/1',
           'osr-project-civil-evaluation/1', 'osr-project-station-interfaces/1',
           'osr-station-track-spread-evaluation/1', 'osr-project-network-service/1',
           'osr-mapped-project-economics/1')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _unique(rows, key, label):
    values = {r[key]: r for r in rows}
    _require(len(values) == len(rows), 'Duplicate '+label)
    return values


def _validate(bundle, body, civil, station, tracks, service, cost, root):
    packets = (bundle, body, civil, station, tracks, service, cost)
    for packet, schema in zip(packets, SCHEMAS):
        sealed(packet)
        _require(packet.get('schema') == schema, 'Expected exact mapped record: '+schema)
        _require(bool(packet.get('source_sha256')), 'Explicit mapped source epoch required')
    for packet in packets[:5]:
        _require(packet['candidate_id'] == identity(packet['physical_definition']), 'Physical candidate differs')
    p = bundle['physical_definition']
    expected = dict(schema='osr-mapped-railway-project-physical/1', body_candidate_id=body['candidate_id'],
        alignment_candidate_id=civil['alignment_candidate_id'], civil_layout_candidate_id=civil['candidate_id'],
        station_geometry_candidate_id=station['candidate_id'], station_track_geometry_candidate_id=tracks['candidate_id'])
    _require(p == expected, 'Mixed mapped physical components')
    for key, packet in (('body_evaluation_id', body), ('civil_evaluation_id', civil),
                        ('station_evaluation_id', station), ('station_track_evaluation_id', tracks)):
        _require(bundle.get(key) == packet['evaluation_id'], 'Mixed mapped evaluation: '+key)
    for packet in (civil, station):
        _require(packet.get('body_evaluation_id') == body['evaluation_id'] and
                 packet.get('vehicle_candidate_id', packet.get('body_candidate_id')) == body['candidate_id'],
                 'Mixed installed body or mass revision')
    for packet in (civil, station, tracks):
        _require(packet['alignment_candidate_id'] == p['alignment_candidate_id'] and
                 packet['alignment_evaluation_id'] == bundle['alignment_evaluation_id'], 'Mixed mapped alignment')
        _require(packet['physical_definition']['alignment_candidate_id'] == p['alignment_candidate_id'], 'Mixed physical mapped alignment')
    _require(tracks['station_candidate_id'] == station['candidate_id'] and
             tracks['station_evaluation_id'] == station['evaluation_id'] and
             tracks['physical_definition']['station_geometry_candidate_id'] == station['candidate_id'], 'Mixed station track revision')
    _require(tracks['physical_definition']['running_track_centres_y_m'] == civil['physical_definition']['track_centres_y_m'] and
             tracks['physical_definition']['station_track_centres_y_m'] == station['physical_definition']['track_centres_y_m'],
             'Mixed running or station rail datums')
    track = body['policy']['track_interface']
    _require(all(track[k] == v for k, v in civil['physical_definition']['span_geometry']['track_interface'].items()), 'Mixed wheel/rail interface')
    own = body.get('compact_drive_contract', {}).get('mass_ownership', {})
    _require(own.get('all_new_drive_components_in_body_BOM') is True and
             own.get('additional_external_drive_mass_kg') == 0 and own.get('remaining_unknown_mass_positive') is True,
             'Explicit in-BOM drive and positive reserve ownership required')
    parts = _unique(body['parts'], 'id', 'body part')
    _unique(body['materials'], 'id', 'body material')
    projected = _unique(body['physical_definition'].get('parts', body['physical_definition'].get('proposed_components', [])), 'id', 'physical part')
    _require(set(projected) == set(parts), 'Complete physical part projection required')
    for pid, projection in projected.items():
        _require(all(parts[pid].get(k) == v for k, v in projection.items()), 'Part differs from physical projection: '+pid)
    for name, count in (('vendor-motor', 24), ('inverter', 24), ('integration-reserve', 6)):
        part = parts.get('compact-drive/'+name, {})
        _require(part.get('quantity_per_train') == count, 'Counted in-BOM drive quantity differs: '+name)
        model.ranges(part['mass_each_kg']); model.ranges(part['direct_cost_each_usd'])
    projected_patterns = _unique(body['physical_definition']['occurrence_patterns'], 'id', 'physical pattern')
    patterns = _unique(body['patterns'], 'id', 'body pattern')
    _require(set(projected_patterns) == set(patterns), 'Complete physical occurrence projection required')
    for pid, projection in projected_patterns.items():
        _require(all(patterns[pid].get(k) == v for k, v in projection.items()), 'Occurrence differs from physical projection')
    model.ranges(body['policy']['evaluation']['unlocated_installation_reserve_kg'])
    fleet = service['total_trainsets']
    _require(all(type(service[k]) is int and service[k] > 0 for k in ('active_trainsets','spare_trainsets','total_trainsets')) and
             fleet == service['active_trainsets']+service['spare_trainsets'], 'Explicit reconciled project fleet required')
    for packet in (service, cost):
        _require(packet['candidate_id'] == bundle['candidate_id'] and packet['bundle_evaluation_id'] == bundle['evaluation_id'], 'Mixed project service or cost')
    _require(all(cost[k] == packet['evaluation_id'] for k, packet in
                 (('body_evaluation_id',body),('civil_evaluation_id',civil),('service_evaluation_id',service))), 'Mixed cost evaluation inputs')
    _require(cost['additional_legacy_drive_charge_usd'] == 0 and cost['zero_is_exact_in_BOM_ownership'] is True,
             'Legacy external drive charge is forbidden for in-BOM equipment')
    core, full = cost['core'], cost['full_scope']
    for packet, schema in ((core,'osr-station-pair-cost/1'),(full,'osr-station-pair-lifecycle/1')):
        sealed(packet)
        _require(packet.get('schema') == schema and bool(packet.get('source_sha256')), 'Exact source-bound project cost record required')
        _require(packet['candidate_id'] == bundle['candidate_id'] and packet['body_candidate_id'] == body['candidate_id'] and
                 packet['body_bundle_id'] == body['parent_bundle_id'] and packet['mass_evaluation_id'] == body['evaluation_id'], 'Mixed cost body/mass ownership')
        _require(all(packet['service'][k] == service[k] for k in ('headway_s','active_trainsets','spare_trainsets','total_trainsets')), 'Mixed cost fleet or headway')
    _require(full['input_cost_evaluation_id'] == core['evaluation_id'], 'Mixed lifecycle core')
    _require(len(full['required_cost_scopes']) == len(SCOPES) and set(full['required_cost_scopes']) == set(SCOPES), 'All fourteen cost scopes required')
    owners = _unique(core['accounts'], 'owner', 'project cost owner')
    _require(set(owners) == set(OWNER_SCOPES)|{'rolling-stock-delivered'}, 'Complete disjoint project cost owners required')
    for account in owners.values():
        model.positive(account['quantity'], 'cost owner quantity'); model.ranges(account['cost_usd'])
    _require(owners['rolling-stock-delivered']['quantity'] == fleet, 'Rolling stock account differs from counted fleet')
    for case in model.CASES:
        _require(isclose(owners['rolling-stock-delivered']['cost_usd'][case], fleet*cost['delivered_train_unit_usd'][case], rel_tol=1e-10), 'Delivered train price owner differs')
    _require(isinstance(full['methods'], list) and bool(full['methods']), 'At least one lifecycle cost method required')
    _unique(full['methods'], 'method', 'cost method')
    for method in full['methods']:
        _require(set(method['scope_totals_usd']) == set(SCOPES), 'Missing method cost scope')
        for amounts in (method['installed_capital_usd'],method['whole_life_NPV_usd'],*method['scope_totals_usd'].values()):
            _cases(amounts, 'mapped cost', nullable=True)
    route = civil['physical_definition']['station_centre_to_centre_route_m']; bays = civil['physical_definition']['bays']
    q = civil['quantities']; span = civil['physical_definition']['standard_span_m']
    model.positive(route,'mapped route'); model.positive(span,'standard span')
    _require(type(bays) is int and bays == ceil(route/span) and q['beams'] == 2*bays and q['shared_bents'] == bays+1 and
             isclose(q['nominal_span_track_m'],2*bays*span) and isclose(q['main_running_track_m'],2*route), 'Mapped civil quantities do not reconcile')
    _require(isclose(service['route_m'],route) and isclose(cost['route_m'],route) and isclose(full['route_km']*1000,route), 'Mapped route length differs')
    tq = tracks['quantities']; sq = station['quantities']
    _require(isclose(tq['total_track_m'],2*route+tq['terminal_extension_track_m']+tq['spread_additional_track_m']) and
             isclose(tq['total_rail_m'],2*tq['total_track_m']) and sq['stations'] == len(station['physical_definition']['stations']) and
             sq['boarding_faces'] == 2*sq['stations'], 'Mapped station/track quantities do not reconcile')
    _require(isclose(cost['additional_terminal_and_spread_track_m'],tq['total_track_m']-q['nominal_span_track_m']), 'Mapped cost track credit differs')
    _require(isclose(cost['standard_bay_credit_track_m'],q['nominal_span_track_m']-2*route), 'Mapped standard bay credit differs')
    civil_accounts = _unique(civil['cost']['accounts'], 'owner', 'mapped civil account')
    _require(set(civil_accounts) == {n for group in GROUPS.values() for n in group}, 'Complete mapped civil account owners required')
    extras = _unique(full['extra_accounts'], 'owner', 'extra project cost owner')
    _require(not (set(extras)&set(owners)), 'Extra cost account duplicates a core owner')
    for account in full['extra_accounts']:
        _require(account['candidate_id'] == bundle['candidate_id'] and account['scope'] in SCOPES, 'Mixed extra cost owner')
        model.positive(account['quantity'], 'extra cost quantity'); model.ranges(account['cost_usd'])
    sources = source_union(*packets, core, full, root=root)
    sources.update(model.sources(root))
    sources.update({p:digest(Path(root)/p) for p in (PRODUCER,*DEPENDENCIES)})
    return dict(sorted(sources.items()))


def compile_proposal(bundle, body, civil, station, tracks, service, cost, *, root=ROOT, policy=None, account_contract=None):
    """Return proposal/1 and its typed mapped context, without external execution."""
    root = Path(root); sources = _validate(bundle,body,civil,station,tracks,service,cost,root)
    policy = deepcopy(policy if policy is not None else json.loads((root/model.POLICY).read_bytes()))
    _require(policy.get('schema') == 'osr-pilot-delivery-policy/1' and policy.get('automatic_bulk_discount') is False, 'Explicit non-discount delivery policy required')
    _require(policy.get('controlled_cycle_times_available') is False and policy.get('actual_crew_count') is None,
             'Unmeasured planning policy cannot claim controlled times or actual crews')
    for value in policy.values():
        if isinstance(value,dict): model.ranges(value)
    fleet = service['total_trainsets']
    part_ledger = None if account_contract is None else part_accounts.compile_accounts(
        body,account_contract,fleet,cost_evaluation_id=cost['core']['evaluation_id'])
    context = dict(schema='osr-mapped-project-delivery-context/1',candidate_id=bundle['candidate_id'],
        inputs={name:packet['evaluation_id'] for name,packet in zip(('bundle','body','civil','station','tracks','service','cost'),(bundle,body,civil,station,tracks,service,cost))},
        source_sha256=sources,part_accounts_evaluation_id=None if part_ledger is None else part_ledger['evaluation_id'],
        scope='Mapped project manufacturing-planning context; not a closure study or native execution receipt',**FLAGS)
    context['context_id'] = identity(context)
    binding = dict(candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],study_id=context['context_id'],
        engineering_revision=body['evaluation_id'],body_candidate_id=body['candidate_id'],source_body_bundle_id=body['parent_bundle_id'],
        installed_component_candidate_id=body['candidate_id'],installed_mass_evaluation_id=body['evaluation_id'],
        civil_candidate_id=civil['candidate_id'],civil_evaluation_id=civil['evaluation_id'],service_evaluation_id=service['evaluation_id'],
        cost_evaluation_id=cost['core']['evaluation_id'],lifecycle_evaluation_id=cost['full_scope']['evaluation_id'])
    planning = body if part_ledger is None else part_accounts.planning_body(body,part_ledger)
    items, occurrences, tasks, materials = model._parts(planning,binding,fleet,policy)
    if part_ledger is not None:
        by_part = {r['part_id']:r for r in part_ledger['rows']}
        for item in items:
            item['part_account'] = deepcopy(by_part[item['id']])
            mapped_cost = item['part_account']['project_direct_cost_usd']
            if mapped_cost is not None:
                _require(all(isclose(mapped_cost[c],fleet*item['counted_direct_parts_process_usd_per_train'][c],rel_tol=1e-10,abs_tol=1e-6)
                             for c in model.CASES), 'Part conversion differs from counted delivery cost')
            for reason in item['part_account']['holds']:
                tasks.append(model._task(binding,'hold/part-account/'+item['id']+'/'+identity(reason),
                    'part-account-review',item['id'],'Resolve the explicit source unit, make/buy, stock and price coverage contract',[reason]))
    for case in model.CASES:
        _require(isclose(fsum(p['counted_pattern_mass_kg_per_train'][case] for p in items),body['nominal_part_mass_kg'][case],rel_tol=1e-10), 'Body counted stock mass does not reconcile')
    assemblies, extra_tasks = model._assemblies(body,binding,fleet,policy); tasks += extra_tasks
    external = []
    def held(kind, subject, reason):
        tasks.append(model._task(binding,'hold/'+kind+'/'+subject,kind,subject,'Review actual definitions and controlled evidence before release',[reason]))
    reserve = body['policy']['evaluation']['unlocated_installation_reserve_kg']
    external.append(dict(id='body/unlocated-installation-reserve',identities=binding,quantity_per_train=1,quantity_project=fleet,
        mass_kg_per_train=deepcopy(reserve),geometry=None,validated_person_h=None,provisional_person_h=None,
        ownership='Existing positive body mass/cost reserve; not a second external BOP or drive addition',additional_to_body=False,additive_procurement=False))
    held('reserve-detail','body/unlocated-installation-reserve','Locate and detail existing positive reserve without double-counting it')
    accounts = [('cost-owner/', a) for a in cost['core']['accounts']]
    accounts += [('extra-cost-owner/', a) for a in cost['full_scope']['extra_accounts']]
    _unique(cost['full_scope']['extra_accounts'], 'owner', 'extra project cost owner')
    for prefix, account in accounts:
        if account['owner']=='rolling-stock-delivered': continue
        model.positive(account['quantity'], 'external cost owner quantity')
        model.ranges(account['cost_usd'])
        external.append(dict(id=prefix+account['owner'],identities=binding,source_account=deepcopy(account),
            quantity_project=account['quantity'],quantity_per_train=None,unit=account['unit'],geometry=None,mass_kg=None,
            validated_person_h=None,provisional_person_h=None,additive_procurement=False,additional_to_body=False,
            ownership='Non-additive existing project account; not an ordered part or installed geometry',procurement_status='planning-only'))
        held('procurement-detail',prefix+account['owner'],'Existing positive account needs equipment, geometry, supplier, UOM and qualified process evidence')
    civil_rows = []
    for account in civil['cost']['accounts']:
        model.positive(account['quantity'],'mapped civil account quantity')
        model.ranges(account['cost_usd'])
        civil_rows.append(dict(id=account['owner'],identities=binding,source_account=deepcopy(account),quantity_project=account['quantity'],unit=account['unit'],
            quantity_basis='Actual mapped civil account; non-additive requirement, not a finished part',source_evaluation_id=civil['evaluation_id'],
            additive_mass_or_cost_ledger=False,geometry=None,material_specification=deepcopy(civil['physical_definition']['span_geometry'].get('material_specification')),
            provisional_person_h=None,validated_person_h=None,controlled_drawing_reference=None))
        held('civil-detail',account['owner'],'Mapped quantities retain bearing/joint/foundation/erection and site design holds; no inherited FEM or release')
    held('station-detail','stations-and-tracks','Station spreading, platforms, accessibility, utilities, terminal geometry and turnback routes need detailed assemblies')
    held('business-review','ERP-conversion','Controlled drawing/inspection/routing and authenticated review required; no Item, order, serial or safety command is created')
    views = []
    for method in cost['full_scope']['methods']:
        views.append(dict(identities=binding,**{k:deepcopy(method[k]) for k in ('method','scope_totals_usd','installed_capital_usd','whole_life_NPV_usd','site_specific_prices_verified')}))
    for scope in cost['full_scope']['required_cost_scopes']:
        tasks.append(model._task(binding,'review/scope/'+scope,'cost-scope-review',scope,'Review existing cost scope and unknowns; decomposition adds no second price'))
    unknown = [p['id'] for p in items if p['capacity']['provisional_person_h'] is None]
    known = {c:fsum(p['capacity']['provisional_person_h'][c] for p in items if p['capacity']['provisional_person_h'] is not None)+fsum(a['provisional_person_h'][c] for a in assemblies) for c in model.CASES}
    material_requirements = [dict(id=m['id'],identities=binding,counted_body_mass_kg_project={c:fleet*fsum(p['counted_pattern_mass_kg_per_train'][c] for p in items if p['material_id']==m['id']) for c in model.CASES},
        procurement_stock_mass_kg=None,basis='Counted body stock only; raw-material yield and purchased-package allocation unresolved') for m in materials]
    tasks.sort(key=lambda t:t['id'])
    result = dict(schema='osr-pilot-delivery-proposal/1',identities=binding,delivery_context=context,part_accounts=part_ledger,status='DRAFT',docstatus=0,
        planning_selection=dict(purpose='Mapped manufacturing planning only',selected_service_evaluation_id=service['evaluation_id'],selection_id=identity(dict(identities=binding,purpose='manufacturing-planning-review'))),
        source_sha256=sources,policy=policy,policy_id=identity(policy),materials=deepcopy(materials),material_requirements=material_requirements,
        items=items,occurrence_patterns=occurrences,assembly_routes=assemblies,external_inventory=external,civil_requirements=civil_rows,
        construction_route=dict(identities=binding,source_evaluation_id=civil['evaluation_id'],mapped_quantities=deepcopy(civil['quantities']),station_quantities=deepcopy(station['quantities']),track_quantities=deepcopy(tracks['quantities']),
            erection_sequence=None,handling=None,temporary_works=None,lifting=None,hours=None,capacity=None,construction_release=False,hold='Controlled site-specific construction, lifting and temporary works plan required'),
        tasks=tasks,cost_views=views,assembly_revision_proposals=deepcopy({k:v for k,v in body['assembly_plans'].items() if k!='plans'}),
        retired_source_routes=deepcopy([r for r in body['assembly_plans']['plans'] if r['assembly_id'] not in {p['assembly_id'] for p in items}]),
        capacity=dict(provisional_vehicle_person_h=None if unknown else known,known_provisional_vehicle_person_h_subtotal=known,part_process_hours_complete=not unknown,
            unknown_part_process_hour_ids=unknown,validated_vehicle_person_h=None,equivalent_16h_resource_days=None,actual_crew_count=None,calendar_duration_days=None,external_and_civil_hours_unknown=True,
            basis='Part and assembly proxies only. External equipment, station/civil processes, yields, curing, labour capacity and critical path remain unknown.'),
        execution_mapping_draft=dict(identities=binding,review_reference=None,engineering_sha256=None,status='held',automatic_order_release=False,
            items=[dict(component_type_id=p['component_definition_id'],source_part_id=p['id'],erp_item_code=None,
                uom=p['unit'] if part_ledger is None else p['part_account']['target_unit'],
                inspection_reference=None,drawing_reference=None,production_bom=None,
                conversion_rule=None if part_ledger is None else deepcopy(p['part_account']['conversion'])) for p in items]),
        manufacturing_drawings_complete=False,qualified_factory_route=False,measured_installed_mass=False,
        limitations=[*model.LIMITATIONS,'Mapped context replaces the study field only at the protocol boundary; no historical study or installed-drive reserve is fabricated.',*cost['limitations'],*civil.get('holds',[]),*station.get('holds',[]),*tracks.get('holds',[])],**FLAGS)
    result['summary'] = dict(component_types=len(items),occurrence_patterns=len(occurrences),body_occurrences_per_train=sum(p['quantity_per_train'] for p in items),body_occurrences_project=sum(p['quantity_project'] for p in items),
        project_trainsets=fleet,assembly_types=len(assemblies),source_routes_with_missing_parts=sum(bool(a['source_route_unresolved_part_ids']) for a in assemblies),external_inventory_owners=len(external),civil_requirement_types=len(civil_rows),
        cost_scopes=len(SCOPES),task_status_counts=dict(Counter(t['status'] for t in tasks)),make_buy_counts=dict(Counter(p['make_buy'] for p in items)),direct_part_process_usd_per_train=deepcopy(body['direct_parts_process_usd']),
        unknown_process_time_types=len(unknown),part_account_mapping_complete=part_ledger is not None and part_ledger['all_source_parts_mapped'],
        engineering_release_held=True,ERP_mapping_ready=False)
    model.seal(result,'proposal_id'); model.validate_proposal(result)
    return result
