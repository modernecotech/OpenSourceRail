"""Linked industrialisation screens; accepted designs and supply remain external.

The same support graph determines bogie count, static axle loading and civil
demand. Unknown supplier masses never become an automatic weight or cost saving.
"""
from datetime import datetime
import math

from osr_mech.provenance import stable_sum


def nonnegative(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(label + ' must be finite and non-negative')
    return value


def vehicle_support_graph(bodies, bogies):
    """Two-support static bodies; suspended/more complex bodies need a new model."""
    lookup={b['id']:b for b in bogies}
    if len(lookup)!=len(bogies) or not lookup:raise ValueError('distinct bogie identities required')
    if len({b['id'] for b in bodies})!=len(bodies) or not bodies:raise ValueError('distinct body identities required')
    reactions={key:0. for key in lookup};unknown=False;body_mass=0.
    for bogie in bogies:
        if bogie.get('mass_kg') is None:unknown=True
        else:reactions[bogie['id']]+=nonnegative(bogie['mass_kg'],'bogie mass')*9.81/1000
        if type(bogie['axles']) is not int or bogie['axles']<1:raise ValueError('positive axle count required')
        if not math.isfinite(bogie['x_m']):raise ValueError('finite support position required')
    for body in bodies:
        support=body['support_bogies']
        if len(support)!=2 or len(set(support))!=2 or not set(support)<=lookup.keys():
            raise ValueError('each body needs two distinct identified supports; suspended sections require independent substantiation')
        a,b=sorted(support,key=lambda key:lookup[key]['x_m']);left,right=lookup[a]['x_m'],lookup[b]['x_m']
        cg=body['cg_x_m']
        if not math.isfinite(cg) or not left<=cg<=right or right<=left:raise ValueError('body CG must lie between its supports')
        if body.get('supported_mass_kg') is None:unknown=True;continue
        mass=nonnegative(body['supported_mass_kg'],'supported body mass');body_mass+=mass
        weight=mass*9.81/1000
        reactions[a]+=weight*(right-cg)/(right-left);reactions[b]+=weight*(cg-left)/(right-left)
    axle_pattern=[]
    for bogie in bogies:
        positions=bogie['axle_offsets_m']
        if len(positions)!=bogie['axles'] or len(set(positions))!=len(positions) or any(not math.isfinite(x) for x in positions):
            raise ValueError('every axle needs a distinct finite offset')
        for index,offset in enumerate(positions):
            axle_pattern.append(dict(id=bogie['id']+'-axle-'+str(index+1),bogie=bogie['id'],x_m=bogie['x_m']+offset,
                static_load_kn=None if unknown else reactions[bogie['id']]/bogie['axles']))
    total=None if unknown else body_mass+stable_sum(b['mass_kg'] for b in bogies)
    return dict(body_count=len(bodies),bogie_count=len(bogies),axle_count=len(axle_pattern),
        bogie_reactions_kn=None if unknown else reactions,axle_pattern=sorted(axle_pattern,key=lambda x:x['x_m']),
        total_mass_kg=total,load_balance_passed=None if unknown else math.isclose(stable_sum(reactions.values()),total*9.81/1000,rel_tol=1e-12),
        articulation_changes_bogie_count_automatically=False,engineering_accepted=False,
        limitations='two-support static load distribution; equal axle sharing is assumed; dynamic, fatigue, crash, lateral and pitch/roll/yaw loads remain separate')


def moving_axle_screen(pattern, span_m, step_m=.25):
    """Simply supported vertical axle-demand envelope, with no capacity decision."""
    if span_m not in (20.,25.) or step_m<=0 or not math.isfinite(step_m):raise ValueError('catalogue span and positive finite step required')
    if not pattern or any(p['static_load_kn'] is None for p in pattern):
        return dict(span_m=span_m,maximum_support_reaction_kn=None,maximum_live_moment_knm=None,loading_accepted=False)
    x_min=min(p['x_m'] for p in pattern);length=max(p['x_m'] for p in pattern)-x_min
    max_reaction=max_moment=0.
    for i in range(math.ceil((length+span_m)/step_m)+1):
        origin=-length+i*step_m
        loads=[(origin+p['x_m']-x_min,nonnegative(p['static_load_kn'],'axle load')) for p in pattern]
        loads=[(x,w) for x,w in loads if 0<=x<=span_m]
        reaction_a=stable_sum(w*(span_m-x)/span_m for x,w in loads)
        reaction_b=stable_sum(w*x/span_m for x,w in loads)
        max_reaction=max(max_reaction,reaction_a,reaction_b)
        for x,_ in loads:
            moment=reaction_a*x-stable_sum(w*(x-y) for y,w in loads if y<x)
            max_moment=max(max_moment,moment)
    return dict(span_m=span_m,maximum_support_reaction_kn=max_reaction,maximum_live_moment_knm=max_moment,
        step_m=step_m,tracks_loaded=1,dynamic_augmentation=None,dead_load_included=False,capacity_accepted=False,
        loading_accepted=False,basis='sampled static moving axle demand on one beam; not a structural design or launcher loading check')


def production_balance(config, rate, *, independent_fronts, span_m=25.):
    nonnegative(rate,'bay rate')
    launchers=config['launchers'];active=min(launchers,independent_fronts)
    if type(launchers) is not int or launchers<1 or type(independent_fronts) is not int or independent_fronts<1:
        raise ValueError('positive integer launchers and fronts required')
    if span_m not in (20.,25.):raise ValueError('ordinary catalogue span required')
    bays=active*rate;beams=2*bays
    availability=config['casting_position_availability'];yield_fraction=config['first_pass_yield']
    if not 0<availability<=1 or not 0<yield_fraction<=1:raise ValueError('casting availability/yield must be in (0,1]')
    occupation=nonnegative(config['mould_occupation_hours'],'mould occupation')
    capacities=config['accepted_capacities_per_working_day'];unknown=[];limits={}
    for key in ('released_foundations','accepted_piers','accepted_beams','transported_beams','erected_bays','accepted_completed_bays'):
        value=capacities[key]
        if value is None:unknown.append(key)
        else:limits[key]=nonnegative(value,key)/(2 if key in ('accepted_beams','transported_beams') else 1)
    qualified_rate=None if unknown else min(bays,*limits.values())
    return dict(active_launchers=active,spare_launchers=launchers-active,shifts_day=config['shifts_day'],
        illustrative_bays_per_working_day=bays,illustrative_beams_per_working_day=beams,
        illustrative_running_metres_per_working_day=bays*span_m,
        steady_state_new_support_positions_per_working_day=bays,end_supports_and_exceptions_included=False,
        casting_positions=math.ceil(beams*occupation/24/(availability*yield_fraction)),
        mould_occupation_hours=occupation,positions_are_not_separate_long_line_beds=True,
        buffer_beams=math.ceil(beams*nonnegative(config['buffer_working_days'],'buffer days')),
        accepted_chain_bays_per_working_day=qualified_rate,missing_accepted_capacity=unknown,
        limiting_known_stages=[key for key,value in limits.items() if value==min(limits.values())] if limits else [],
        rate_is_site_productivity_commitment=False,railway_opening_rate=None)


SUPPORT_EVIDENCE=('survey_position','utility_clearance','ground_basis','foundation_design','access_plan',
                  'traffic_arrangement','inspection_plan','connection_and_release_strength','launcher_stage_loading')


def support_packet_check(packet, revision):
    if not packet.get('support_id') or packet.get('revision')!=revision:raise ValueError('support packet identity/revision mismatch')
    missing=[key for key in SUPPORT_EVIDENCE if not packet.get('evidence',{}).get(key)]
    return dict(support_id=packet['support_id'],revision=revision,missing_evidence=missing,
        packet_complete=not missing,ready_for_authority_review=not missing,
        foundation_mobilisation_authorised=False,launcher_support_released=False,
        authority_verified_by_generator=False)


def installed_cost_comparison(scopes, alternatives):
    result=[]
    for alternative in alternatives:
        cash=alternative.get('scope_costs_usd',{});unknown=[key for key in scopes if cash.get(key) is None]
        for key,value in cash.items():
            if key not in scopes:raise ValueError('uncontrolled installed-cost scope')
            if value is not None:nonnegative(value,key)
        if alternative.get('tooling_in_repeat_unit_price') and cash.get('fixtures-metrology-welding-NDT-test-equipment'):
            raise ValueError('tooling amortised in repeat price cannot also be project capital')
        result.append(dict(id=alternative['id'],known_scoped_cash_usd=stable_sum(v for v in cash.values() if v is not None),
            unknown_scopes=unknown,complete_installed_cost_usd=None if unknown else stable_sum(cash.values()),
            measured_accepted_supports_week=alternative.get('measured_accepted_supports_week'),adopted=False))
    return result


def disruption_metrics(events, accepted_bay_ids):
    """Union closures by lane/access/site so overlapping bookings count once."""
    accepted=set(accepted_bay_ids);groups={};seen=set()
    for event in events:
        if event['id'] in seen:raise ValueError('duplicate closure event identity')
        seen.add(event['id'])
        if event['bay_id'] not in accepted:raise ValueError('disruption must bind to an accepted completed bay')
        a=datetime.fromisoformat(event['start_at']);b=datetime.fromisoformat(event['finish_at'])
        if a.tzinfo is None or b.tzinfo is None or b<=a:raise ValueError('aware positive closure window required')
        key=(event['kind'],event['resource_id']);groups.setdefault(key,[]).append((a.timestamp(),b.timestamp()))
    hours={kind:0. for kind in ('lane','access','worksite')};interruptions=0
    for (kind,_),intervals in groups.items():
        if kind not in hours:raise ValueError('unknown disruption kind')
        merged=[]
        for a,b in sorted(intervals):
            if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
            else:merged.append([a,b])
        hours[kind]+=stable_sum(b-a for a,b in merged)/3600
        if kind=='access':interruptions+=len(merged)
    return dict(accepted_completed_bays=len(accepted),lane_hours_closed=hours['lane'] if events else None,
        lane_hours_closed_per_accepted_bay=hours['lane']/len(accepted) if events and accepted else None,
        access_interruptions=interruptions if events else None,access_interruption_hours=hours['access'] if events else None,
        access_interruptions_per_accepted_bay=interruptions/len(accepted) if events and accepted else None,
        worksite_occupation_days_per_accepted_bay=hours['worksite']/24/len(accepted) if events and accepted else None,
        observations_entered=bool(events),traffic_below_active_lifts_permitted=False)


def service_finance_gate(rows):
    """Delivered vehicles and civil work cannot manufacture paid journeys."""
    months=[];seen=set()
    for row in rows:
        key=(row['line'],row['month'])
        if key in seen:raise ValueError('duplicate line/month service record')
        seen.add(key)
        required=nonnegative(row['required_trainsets'],'required trainsets')
        delivered=nonnegative(row['commissioned_trainsets'],'commissioned trainsets')
        if required<=0:raise ValueError('positive required trainsets')
        scheduled=nonnegative(row['scheduled_train_km'],'scheduled kilometres');served=nonnegative(row['served_train_km'],'served kilometres')
        ready=all(row.get(key) for key in ('civil_handover_record','station_and_special_structure_record','systems_and_energy_acceptance_record',
                  'rolling_stock_commissioning_record','operating_acceptance_record','paid_journey_evidence'))
        qualified=ready and row.get('review_accepted') is True
        receipts=None
        if qualified:
            receipts=nonnegative(row['unique_paid_journeys'],'unique paid journeys')*nonnegative(row['fare_iqd'],'fare')*nonnegative(row['collection_fraction'],'collection fraction')
            if row['collection_fraction']>1:raise ValueError('collection fraction exceeds one')
            if receipts>0 and (delivered<=0 or served<=0):raise ValueError('fare receipts require commissioned vehicles and delivered service')
        months.append(dict(line=row['line'],month=row['month'],fleet_readiness_fraction=min(1.,delivered/required),
            delivered_service_fraction=min(1.,served/scheduled) if scheduled else None,
            finance_receipts_iqd=receipts,received_review_complete=qualified,finance_adoption_authorised=False))
    return dict(line_months=months,construction_completion_is_revenue_opening=False,
        transfers_create_additional_paid_journeys=False,baseline_finance_replaced=False,
        revised_financing_usd=None,additional_elevation_economically_accepted=False,
        missing_evidence='scope-priced installed costs, accepted openings, commissioned train service, unique paid journeys, collection, operating costs and funding terms' if not rows else None)


def elevation_reference(additional_m, at_grade_usd_km, elevated_usd_km):
    """Marginal reference allowance, never a complete price or adopted benefit."""
    nonnegative(additional_m,'additional elevated length')
    nonnegative(at_grade_usd_km,'at-grade reference rate');nonnegative(elevated_usd_km,'elevated reference rate')
    return dict(additional_elevated_m=additional_m,
        marginal_reference_civil_allowance_usd=additional_m/1000*(elevated_usd_km-at_grade_usd_km),
        complete_incremental_installed_cost_usd=None,avoided_disruption_value_usd=None,
        incremental_qualified_service_receipts_iqd=None,discounted_net_benefit_usd=None,
        new_pier_and_span_layout_required=True,economic_selection_accepted=False,
        missing_scope=['actual foundations and utilities','stations transitions and special structures','grid charging and systems',
            'vehicle first articles and deliveries','installed erection credit and logistics','land permits tax escalation risk','OPEX renewal financing and qualified paid journeys'])
