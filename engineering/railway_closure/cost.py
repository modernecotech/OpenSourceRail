"""Reconciled installed-vehicle/civil/service costs in the existing 14 scopes.

The legacy lifecycle format is reused as an account interface. No old journey,
civil load result, fleet size or old vehicle total is inherited.
"""
from copy import deepcopy
from math import ceil, fsum
from pathlib import Path
import json
from engineering.station_pair import coordinator as pair, economics, lifecycle
from engineering.station_cycle import design
from engineering.station_rail.common import identity, digest
from . import ROOT, FLAGS
from .bundle import combine
from .electrical import supply_screen

CASES=('low','base','high')
POLICY='engineering/railway_closure/cost-policy.json'


def _sealed(v):
    if v.get('evaluation_id')!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):
        raise ValueError('Sealed input required')


def evaluate(body,installed,civil,service,*,energy=None,root=ROOT):
    """Energy may remain unknown; it is never converted to a zero-price scope.

    energy, when supplied, is sealed and contains candidate_id, service_fulfilled,
    annual_grid_kwh={low,base,high}, and basis. Only a fulfilled, independently
    replayed timetable may supply annual electricity for a full NPV.
    """
    for v in (body,installed,civil,service):_sealed(v)
    canonical=combine(installed,civil);cid=canonical['candidate_id'];root=Path(root)
    if (body['candidate_id']!=installed['vehicle_candidate_id']
        or body['evaluation_id']!=installed['body_evaluation_id']
        or service['candidate_id']!=cid):
        raise ValueError('Mixed body, civil or service candidate in cost ledger')
    if energy is not None:
        _sealed(energy)
        if (energy.get('schema')!='osr-railway-closure-service-energy/1'
            or energy['candidate_id']!=cid or not energy['service_fulfilled']
            or energy.get('service_evaluation_id')!=service['evaluation_id']
            or len(energy.get('native_fleet_evaluation_id',''))!=64
            or not service['planned_service_complete']):
            raise ValueError('Failed or mixed service cannot annualize electricity')
    brief=json.loads((root/pair.BRIEF).read_bytes())
    p=json.loads((root/economics.POLICY).read_bytes());extra_p=json.loads((root/POLICY).read_bytes())
    if extra_p.get('automatic_bulk_discount') is not False:
        raise ValueError('No unsubstantiated discount multiplier')
    geometry=installed['terminal_geometry'];total_track=geometry['track_quantities']['total_track_m']
    route=1500.;fleet=service['total_trainsets'];active=service['active_trainsets'];h=service['headway_s']
    rows=[]
    def add(owner,quantity,unit,amounts,basis):
        rows.append(dict(owner=owner,quantity=quantity,unit=unit,cost_usd=dict(amounts),basis=basis))
    # Replace all old civil accounts with exact new quantities, never add both.
    groups={
        'civil-beam-factory':('civil/precast-factory','civil/segment-joints','civil/ducts-grout-chairs-endzone'),
        'shared-pier-foundation-bearings':('civil/shared-pier-foundation','civil/bearings','civil/inspection-walkway-guard','civil/drainage'),
        'beam-transport-and-erection':('civil/transport','civil/erection','civil/temporary-props'),
        'running-rails':('civil/rails',),
        'running-rail-fastenings':('civil/fastening-steel','civil/fastening-clips-pads-nuts-washers')}
    civil_rows={r['owner']:r for r in civil['cost']['accounts']}
    if set(civil_rows)!={name for names in groups.values() for name in names}:
        raise ValueError('Every new civil owner must be assigned exactly once')
    for owner,names in groups.items():
        add(owner,1.,'candidate-bound civil account group',
            {c:fsum(civil_rows[n]['cost_usd'][c] for n in names) for c in CASES},
            'Replaces old pilot scope with civil evaluation '+civil['evaluation_id']+'; owners '+', '.join(names)+'; its standalone contingency is excluded here')
    # Rail and fastening additions are explicit; elevated terminal structure is
    # a separate positive allowance and does not inherit the running-span FEM.
    extra_track=total_track-2*route
    for owner,key,quantity in (('running-rails','rail_usd_kg',2*extra_track*p['rail_kg_per_m']),
                               ('running-rail-fastenings','fastening_set_usd',ceil(2*extra_track/p['fastening_pitch_m']))):
        target=next(r for r in rows if r['owner']==owner)
        for i,c in enumerate(CASES):target['cost_usd'][c]+=quantity*p[key][i]
        target['basis']+='; plus counted terminal/pocket/crossover rail and fastening quantities'
    vehicle={}
    v=installed['variant']
    for i,c in enumerate(CASES):
        reserve=body['policy']['evaluation']['unlocated_installation_reserve_kg'][c]
        direct=body['direct_parts_process_usd'][c]+reserve*p['uncatalogued_installation_usd_per_reserved_kg'][i]
        final=p['train_final_assembly_h'][i]*p['fabrication_loaded_wage_usd_h'][i]+p['train_whole_vehicle_test_allowance_usd'][i]
        drive=12*p['powered_axle_drive_unit_usd'][i]+p['train_traction_inverter_collector_cooling_usd'][i]
        # DC/DC is a declared partition, not a second charge for the same drive BOP.
        remaining=p['train_traction_inverter_collector_cooling_usd'][i]-6*extra_p['continuous_auxiliary_converter_per_car_usd'][i]
        if remaining<=0:raise ValueError('Auxiliary partition consumes the whole drive allowance')
        vehicle[c]=(direct+final+drive)*(1+p['train_delivery_and_spares_fraction'][i])
    add('rolling-stock-delivered',fleet,'six-car trainsets',{c:fleet*vehicle[c] for c in CASES},
        'New counted body direct parts/process + positive installation reserve + final assembly/test + 12 drive units + BOP (including six auxiliary DC/DC partitions) + delivery/spares once; recovery fittings separate')
    def rate(owner,q,unit,key,basis):add(owner,q,unit,{c:q*p[key][i] for i,c in enumerate(CASES)},basis)
    rate('station-civil-accessibility',2,'stations','station_civil_accessibility_usd','Two 125m proposed stations, access/lifts/egress allowances; actual site design open')
    # Price the same installed feed limit in faults and nominal runs; a favourable
    # observed trajectory cannot silently downsize the candidate's hardware.
    peak=v['grid_power_limit_W_per_train']
    supply=supply_screen(peak,active,h,root=root)
    add('station-common-grid-feed',2,'dual-end feeds',
        {c:2*max(p['station_common_grid_feed_usd'][i],supply['rows'][i]['station_feed_cost_usd']) for i,c in enumerate(CASES)},
        'Positive feed reserve sized to conservative two-moving-train plus all active hot hotel peak; fixed connection + declared USD/kW. Voltage/current/protection and converter maps remain unverified')
    rate('station-hotel-battery-chargers',2,'installations','station_hotel_charger_usd','Retained positive backup/maintenance charger provision; continuous auxiliary feed does not make charging equipment free')
    rate('signalling-protection-turnbacks',1,'system','signals_communications_protection_turnbacks_usd','Independent braking/protection retained, terminal/interlocking interface provision; no authority granted')
    rate('depot-tools-utilities',1,'pilot facility','depot_tools_utilities_usd','Repair/spares/depot premises and utilities separate from production setup')
    rate('wayside-propulsion',total_track,'conductor track-m','conductor_supply_protection_usd_track_m','Full terminal and running-track conductor included; actual ampacity/insulation remains open')
    usage=dict(headway_s=h,active_trainsets=active,spare_trainsets=service['spare_trainsets'],total_trainsets=fleet,
               planning_capacity_pphpd=service['planning_capacity_pphpd'],operating_timetable_verified=False,
               native_fleet_replay_id=None if energy is None else energy['evaluation_id'])
    methods=[];hours=brief['operation_hours_day']*brief['operation_days_year']
    for mode,key in (('purchased-custom-outline','purchased_custom_vehicle_setup_usd'),('local-assembly-factory','local_assembly_factory_setup_usd')):
        capital={};components={};annual={}
        for i,c in enumerate(CASES):
            direct=fsum(r['cost_usd'][c] for r in rows);setup=p[key][i]
            integration=(direct+setup)*p['design_integration_verification_fraction'][i]
            contingency=(direct+setup+integration)*p['contingency_fraction'][i]
            capital[c]=direct+setup+integration+contingency
            components[c]=dict(direct_accounts=direct,one_campaign_setup=setup,integration_verification=integration,contingency=contingency)
            running=fsum(r['cost_usd'][c] for r in rows if r['owner'].startswith(('civil','shared','running','beam-transport')))
            maintenance=fleet*vehicle[c]*p['vehicle_annual_maintenance_fraction'][i]+running*p['civil_annual_maintenance_fraction'][i]
            maintenance+=next(r['cost_usd'][c] for r in rows if r['owner']=='wayside-propulsion')*p['propulsion_annual_maintenance_fraction'][i]
            annual[c]=dict(energy_usd=None,maintenance_usd=maintenance,
                           staff_usd=p['paid_operating_maintenance_staff'][i]*p['loaded_staff_usd_year'][i])
        methods.append(dict(method=mode,installed_capital_usd=capital,
                            capital_per_route_km_usd={c:capital[c]/1.5 for c in CASES},
                            capital_components=components,annual_operating=annual))
    sources={POLICY:digest(root/POLICY),'engineering/railway_closure/cost.py':digest(root/'engineering/railway_closure/cost.py'),
             economics.POLICY:digest(root/economics.POLICY)}
    core=dict(schema='osr-station-pair-cost/1',candidate_id=cid,body_candidate_id=body['candidate_id'],
              body_bundle_id=body['parent_bundle_id'],mass_evaluation_id=installed['evaluation_id'],
              journey_evaluation_id=None if energy is None else energy['evaluation_id'],
              service=usage,accounts=rows,methods=methods,source_sha256=sources,**lifecycle.FLAGS)
    core['evaluation_id']=identity(core)
    extras=[]
    if installed['recovery_design']['recovery_hardware']:
        d=deepcopy(installed['recovery_design']);d['variant']['candidate_id']=cid
        extras+=design.added_accounts(d,core,design.policy(root))
    def extra(owner,scope,amounts,basis,renewal_class='site'):
        row=dict(candidate_id=cid,owner=owner,scope=scope,quantity=1.,unit='pilot terminal package',cost_usd=amounts,basis=basis,renewal_class=renewal_class)
        row['account_id']=identity(row);extras.append(row)
    extra('terminal-extra-supports','construction',{c:extra_track*extra_p['terminal_structure_usd_extra_track_m'][i] for i,c in enumerate(CASES)},
          'Additional counted pocket/crossover/platform track structure; positive structural allowance, no inherited running-span capacity')
    extra('terminal-four-turnouts','construction',{c:geometry['turnout_switch_units']*extra_p['turnout_installed_usd_unit'][i] for i,c in enumerate(CASES)},
          'Four counted turnout/switch installations separate from track stock and signalling; full package renewed conservatively as mechanical equipment, no permanent-civil exemption',renewal_class='station-mechanical')
    context=dict(schema='osr-station-pair-lifecycle-energy/1',candidate_id=cid,input_cost_evaluation_id=core['evaluation_id'],
                 source_evaluation_id=service['evaluation_id'] if energy is None else energy['evaluation_id'],
                 service_fulfilled=energy is not None,
                 annual_energy_usd={c:None if energy is None else energy['annual_grid_kwh'][c]*brief['tariff_usd_kwh'][c] for c in CASES},
                 basis='Unknown until causal counted-fleet duty closes; no free recovery credit' if energy is None else energy['basis'])
    context['evaluation_id']=identity(context)
    result=lifecycle.evaluate(core,brief,extra_accounts=extras,energy_context=context,root=root)
    return dict(core=core,full_scope=result,train_delivered_unit_usd=vehicle,
                canonical_bundle=canonical,
                supply_screen=supply,
                civil_cost_evaluation_id=civil['evaluation_id'],terminal_extra_track_m=extra_track,
                installed_mass_evaluation_id=installed['evaluation_id'],**FLAGS)
