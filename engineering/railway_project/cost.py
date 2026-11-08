"""Mapped-project quantities into the existing fourteen-scope cost interface.

Rates remain declared research inputs. Motors, gears, inverters and integration
reserves are already in the new body BOM: no legacy twelve-drive purchase or
9,552 kg equipment addition is permitted. Unknown service energy retains an
unknown full NPV. Supplier confirmation and physical release are separate.
"""
from math import ceil,fsum,isclose,isfinite
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity
from engineering.station_pair import economics,lifecycle
from .civil import sealed,source_union
from .route import FLAGS

CASES=('low','base','high')
PRODUCER='engineering/railway_project/cost.py'
EXTRA='engineering/railway_closure/cost-policy.json'
SUPPLY='engineering/railway_closure/supply-policy.json'
GROUPS={
    'civil-beam-factory':('civil/precast-factory','civil/segment-joints','civil/ducts-grout-chairs-endzone'),
    'shared-pier-foundation-bearings':('civil/shared-pier-foundation','civil/bearings','civil/inspection-walkway-guard','civil/drainage'),
    'beam-transport-and-erection':('civil/transport','civil/erection','civil/temporary-props'),
    'running-rails':('civil/rails',),
    'running-rail-fastenings':('civil/fastening-steel','civil/fastening-clips-pads-nuts-washers')}


def _positive(value,name):
    if type(value) not in (int,float) or not isfinite(value) or value<=0:
        raise ValueError('Explicit positive project cost input required: '+name)
    return value


def energy_operating_context(brief):
    """Annualization/load context, excluding tariffs and financial discounting.

    Changing this projection requires a fresh cheap annualization record. It
    need not rerun unchanged native trajectories, geometry or structural solves.
    """
    names=('operation_hours_day','operation_days_year','hotel_W_per_car_hypothesis',
           'hotel_charge_efficiency_hypothesis')
    result={name:float(_positive(brief.get(name),name)) for name in names}
    if (result['operation_hours_day']>24 or result['operation_days_year']>366 or
        result['hotel_charge_efficiency_hypothesis']>1):
        raise ValueError('Bounded calendar and hotel/charging context required')
    return dict(schema='osr-project-energy-operating-context/1',**result)


def evaluate(bundle,body,civil,station,tracks,service,brief,*,
             turnout_units,station_peak_input_kw,paid_staff_cases,energy=None,root=ROOT):
    """Price one explicit research layout, retaining unresolved design accounts.

    service is a sealed osr-project-network-service/1 packet. Its active/reserve
    counts can be a planning result; only a completed native service and matching
    energy packet may annualize active-fleet plus station electricity. Reserve
    conditioning and depot electricity are added by lifecycle exactly once.
    This accounting adapter is not a native-receipt authenticator: its caller
    must verify the source-bound service package before supplying it.
    turnout_units and station_peak_input_kw are explicit sizing hypotheses,
    never inferred equipment certification or an installed terminal route.
    """
    for packet in (bundle,body,civil,station,tracks,service):sealed(packet)
    if energy is not None:sealed(energy)
    if any(p['candidate_id']!=identity(p['physical_definition']) for p in (bundle,body,civil,station,tracks)):
        raise ValueError('Project physical identity differs')
    if (bundle.get('schema')!='osr-mapped-railway-project-bundle/1' or
        service.get('schema')!='osr-project-network-service/1' or
        service['candidate_id']!=bundle['candidate_id'] or service['bundle_evaluation_id']!=bundle['evaluation_id']):
        raise ValueError('Exact mapped project service required')
    pdef=bundle['physical_definition']
    links=(('body_candidate_id',body),('civil_layout_candidate_id',civil),
           ('station_geometry_candidate_id',station),('station_track_geometry_candidate_id',tracks))
    if any(pdef.get(k)!=v['candidate_id'] for k,v in links):
        raise ValueError('Mixed physical project cost components')
    evals=(('body_evaluation_id',body),('civil_evaluation_id',civil),
           ('station_evaluation_id',station),('station_track_evaluation_id',tracks))
    if any(bundle.get(k)!=v['evaluation_id'] for k,v in evals):
        raise ValueError('Mixed mass, civil or station cost revision')
    if body['policy']['layout']['cars']!=6:
        raise ValueError('This lifecycle adapter supports six-car inputs; other formations require a distinct hotel/renewal evaluator')
    own=body['compact_drive_contract']['mass_ownership']
    if own.get('all_new_drive_components_in_body_BOM') is not True or own.get('additional_external_drive_mass_kg')!=0:
        raise ValueError('Exact in-BOM drive ownership required')
    parts={p['id']:p for p in body['parts']}
    if len(parts)!=len(body['parts']):raise ValueError('Duplicate body part price owner')
    for name,count in (('vendor-motor',24),('inverter',24),('integration-reserve',6)):
        row=parts.get('compact-drive/'+name,{})
        if row.get('quantity_per_train')!=count:
            raise ValueError('Complete counted drive equipment and positive reserves required')
        lifecycle._cases(row['direct_cost_each_usd'],name,positive=True)
    fleet=service['total_trainsets'];active=service['active_trainsets'];spare=service['spare_trainsets']
    if any(type(v) is not int or v<=0 for v in (fleet,active,spare)) or active+spare!=fleet:
        raise ValueError('Explicit reconciled active and spare fleet required')
    h=_positive(service['headway_s'],'headway')
    route=_positive(civil['physical_definition']['station_centre_to_centre_route_m'],'mapped route')
    total_track=_positive(tracks['quantities']['total_track_m'],'actual spread/terminal tracks')
    if not isclose(service['route_m'],route,rel_tol=1e-12):
        raise ValueError('Service and civil mapped lengths differ')
    if type(turnout_units) is not int or turnout_units<=0:
        raise ValueError('Counted or explicitly proposed positive terminal switch provision required')
    peak=_positive(station_peak_input_kw,'station feed sizing')
    lifecycle._cases(paid_staff_cases,'paid staff',positive=True)
    pinned=source_union(bundle,body,civil,station,tracks,service,*(() if energy is None else (energy,)),root=root)
    root=Path(root);rates=json.loads((root/economics.POLICY).read_bytes())
    extra=json.loads((root/EXTRA).read_bytes());supply=json.loads((root/SUPPLY).read_bytes())
    if rates.get('automatic_bulk_discount') is not False or extra.get('automatic_bulk_discount') is not False:
        raise ValueError('No unsupported blanket bulk discount')
    pinned.update({n:digest(root/n) for n in (PRODUCER,economics.POLICY,EXTRA,SUPPLY)})
    pinned.update(lifecycle.sources(root))
    n=len(station['physical_definition']['stations']);rows=[]
    def add(owner,quantity,unit,amounts,basis):
        lifecycle._cases(amounts,owner,positive=True)
        rows.append(dict(owner=owner,quantity=quantity,unit=unit,cost_usd=amounts,basis=basis))
    def rate(owner,q,unit,key,basis):
        add(owner,q,unit,{c:q*rates[key][i] for i,c in enumerate(CASES)},basis)
    source_rows=civil['cost']['accounts'];indexed={r['owner']:r for r in source_rows}
    if len(indexed)!=len(source_rows) or set(indexed)!={k for g in GROUPS.values() for k in g}:
        raise ValueError('Each civil account owner must be assigned exactly once')
    for owner,names in GROUPS.items():
        add(owner,1.,'mapped civil account group',{c:fsum(indexed[k]['cost_usd'][c] for k in names) for c in CASES},
            'Actual mapped bay/support quantities from '+civil['evaluation_id']+'; standalone civil contingency excluded')
    # Existing final standard-bay overrun already contains rails and structure.
    # Credit it before adding the physical terminal and spread track lengths.
    added_track=total_track-civil['quantities']['nominal_span_track_m']
    if added_track<0:
        raise ValueError('Mapped track ledger would duplicate/cross a negative standard-bay credit')
    for owner,key,q in (('running-rails','rail_usd_kg',2*added_track*rates['rail_kg_per_m']),
                        ('running-rail-fastenings','fastening_set_usd',ceil(2*added_track/rates['fastening_pitch_m']))):
        row=next(r for r in rows if r['owner']==owner)
        for i,c in enumerate(CASES):row['cost_usd'][c]+=q*rates[key][i]
        row['basis']+='; terminal and spread stock minus counted standard-bay overrun once'
    vehicle={}
    for i,c in enumerate(CASES):
        counted=fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in body['parts'])
        if not isclose(counted,body['direct_parts_process_usd'][c],rel_tol=1e-10):
            raise ValueError('Body direct part/process subtotal does not reconcile')
        reserve=_positive(body['policy']['evaluation']['unlocated_installation_reserve_kg'][c],'unlocated installation reserve')
        direct=counted+reserve*rates['uncatalogued_installation_usd_per_reserved_kg'][i]
        final=rates['train_final_assembly_h'][i]*rates['fabrication_loaded_wage_usd_h'][i]+rates['train_whole_vehicle_test_allowance_usd'][i]
        vehicle[c]=(direct+final)*(1+rates['train_delivery_and_spares_fraction'][i])
    add('rolling-stock-delivered',fleet,'six-car trainsets',{c:fleet*vehicle[c] for c in CASES},
        'All counted source parts/process, drives and explicit BOP reserves once, distinct positive unlocated reserve, final assembly/test and delivery/spares. No legacy drive package appended.')
    rate('station-civil-accessibility',n,'stations','station_civil_accessibility_usd',
        'Declared platform floor, roof, lifts/access/egress and building provision per station; excludes track-carrying beams, transverse widening caps and track foundations owned separately. Detailed design remains provisional.')
    add('station-common-grid-feed',n,'station feed provisions',
        {c:n*max(rates['station_common_grid_feed_usd'][i],supply['substation_fixed_usd_cases'][i]+peak*supply['substation_usd_peak_kw_cases'][i]) for i,c in enumerate(CASES)},
        'Explicit '+str(peak)+' kW per station sizing hypothesis, fixed plus per-kW connection. Actual sag/thermal/protection and concurrency capability remain unverified.')
    rate('station-hotel-battery-chargers',n,'station charger provisions','station_hotel_charger_usd','Positive backup charger and maintenance provision, separate from onboard converter cost')
    rate('signalling-protection-turnbacks',1,'project system provision','signals_communications_protection_turnbacks_usd','Explicit project protection/interlocking provision; not an authority or verified terminal route')
    rate('depot-tools-utilities',1,'project facility provision','depot_tools_utilities_usd','Repair depot and ordinary tools; factory setup separate')
    rate('wayside-propulsion',total_track,'conductor track-m','conductor_supply_protection_usd_track_m','Actual running, spread and terminal track counted once; current collection/ampacity and protection remain open')
    running_owners=set(GROUPS)
    methods=[]
    for method,key in (('purchased-custom-outline','purchased_custom_vehicle_setup_usd'),('local-assembly-factory','local_assembly_factory_setup_usd')):
        capitals={};components={};annual={}
        for i,c in enumerate(CASES):
            direct=fsum(r['cost_usd'][c] for r in rows);setup=rates[key][i]
            integration=(direct+setup)*rates['design_integration_verification_fraction'][i]
            contingency=(direct+setup+integration)*rates['contingency_fraction'][i]
            capitals[c]=direct+setup+integration+contingency
            components[c]=dict(direct_accounts=direct,one_campaign_setup=setup,integration_verification=integration,contingency=contingency)
            maintenance=fleet*vehicle[c]*rates['vehicle_annual_maintenance_fraction'][i]
            maintenance+=fsum(r['cost_usd'][c] for r in rows if r['owner'] in running_owners)*rates['civil_annual_maintenance_fraction'][i]
            maintenance+=next(r['cost_usd'][c] for r in rows if r['owner']=='wayside-propulsion')*rates['propulsion_annual_maintenance_fraction'][i]
            annual[c]=dict(energy_usd=None,maintenance_usd=maintenance,staff_usd=paid_staff_cases[c]*rates['loaded_staff_usd_year'][i])
        methods.append(dict(method=method,installed_capital_usd=capitals,
            capital_per_route_km_usd={c:capitals[c]/(route/1000) for c in CASES},capital_components=components,annual_operating=annual))
    core=dict(schema='osr-station-pair-cost/1',candidate_id=bundle['candidate_id'],
        body_candidate_id=body['candidate_id'],body_bundle_id=body['parent_bundle_id'],
        mass_evaluation_id=body['evaluation_id'],journey_evaluation_id=None if energy is None else energy['evaluation_id'],
        accounts=rows,methods=methods,source_sha256=pinned,
        service=dict(headway_s=h,active_trainsets=active,spare_trainsets=spare,total_trainsets=fleet,
            planning_capacity_pphpd=service['planning_capacity_pphpd'],operating_timetable_verified=False),**lifecycle.FLAGS)
    core['evaluation_id']=identity(core)
    additions=[]
    # The narrow span's basic structural cost is already owned above. These are
    # positive *additional* widening/terminal allowances, not reused FEM proof.
    spread_track=tracks['quantities']['station_plateau_track_m']+2*tracks['quantities']['transition_pairs']*tracks['physical_definition']['transition_length_m']
    for owner,q,key in (('station-widening-additional-supports',spread_track,'terminal_structure_usd_extra_track_m'),
                         ('beyond-standard-bays-terminal-supports',added_track,'terminal_structure_usd_extra_track_m'),
                         ('proposed-terminal-switch-units',turnout_units,'turnout_installed_usd_unit')):
        row=dict(candidate_id=bundle['candidate_id'],owner=owner,scope='construction',quantity=q,
            unit='unit' if owner.endswith('units') else 'track-m',cost_usd={c:q*extra[key][i] for i,c in enumerate(CASES)},
            basis='Explicit positive extra scope reserve; no inherited narrow running-span capacity, manufacture or terminal-route approval',
            renewal_class='station-mechanical' if owner.endswith('units') else 'site')
        row['account_id']=identity(row);additions.append(row)
    energy_context=None
    if energy is not None:
        sealed(energy)
        native_id=service.get('native_network_evaluation_id','')
        context=energy_operating_context(brief)
        if (energy.get('schema')!='osr-project-service-energy/1' or energy['candidate_id']!=bundle['candidate_id'] or
            energy['service_evaluation_id']!=service['evaluation_id'] or not service['native_service_complete'] or
            not isinstance(native_id,str) or len(native_id)!=64 or any(c not in '0123456789abcdef' for c in native_id) or
            energy.get('native_network_evaluation_id')!=native_id or
            energy.get('scope')!='active-fleet-and-all-stations-excluding-reserve-and-depot'):
            raise ValueError('Exact completed native service and disjoint energy scope required')
        if (service.get('energy_operating_context')!=context or energy.get('energy_operating_context')!=context):
            raise ValueError('Annual energy and service operating context differs from cost brief')
        lifecycle._cases(energy['annual_grid_kwh'],'annual energy',positive=True)
        energy_context=dict(schema='osr-station-pair-lifecycle-energy/1',candidate_id=bundle['candidate_id'],
            input_cost_evaluation_id=core['evaluation_id'],source_evaluation_id=energy['evaluation_id'],service_fulfilled=True,
            annual_energy_usd={c:energy['annual_grid_kwh'][c]*brief['tariff_usd_kwh'][c] for c in CASES},basis=energy['basis'])
        energy_context['evaluation_id']=identity(energy_context)
    full=lifecycle.evaluate(core,brief,extra_accounts=additions,energy_context=energy_context,root=root)
    result=dict(schema='osr-mapped-project-economics/1',candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],
        body_evaluation_id=body['evaluation_id'],civil_evaluation_id=civil['evaluation_id'],service_evaluation_id=service['evaluation_id'],
        core=core,full_scope=full,delivered_train_unit_usd=vehicle,route_m=route,
        standard_bay_credit_track_m=civil['quantities']['nominal_span_track_m']-2*route,
        additional_terminal_and_spread_track_m=added_track,additional_legacy_drive_charge_usd=0.,
        zero_is_exact_in_BOM_ownership=True,station_peak_input_kw_hypothesis=peak,
        station_widening_and_turnback_detailed=False,source_sha256=pinned,
        required_energy_operating_context=energy_operating_context(brief),
        limitations=['Calculated source rates are research assumptions, not current supplier offers; no further blanket bulk discount.',
            'Factory setup is allocated once per project order; future unrelated orders do not subsidize this estimate.',
            'Positive widened-station, terminal, depot, utility and land accounts still require detailed design.',
            'Financing, taxes, customs, exchange-rate risk and non-fare revenue require a separate project-finance layer.',
            'No annual service electricity or full NPV is supplied for an incomplete/unsupported native service.'],**FLAGS)
    result['evaluation_id']=identity(result)
    return result
