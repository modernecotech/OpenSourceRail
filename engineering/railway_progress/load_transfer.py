"""Same-trajectory sampled wheel/drive loads on actual simple-span locations."""
from math import fsum,floor
from . import identity,digest,FLAGS


def evaluate(bundle,civil,alternative,journeys,*,dynamic_factor=1.3):
    for value,key in ((bundle,'definition_id'),(civil,'evaluation_id'),(alternative,'evaluation_id')):
        if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Exact coupled load input identities required')
    if civil['candidate_id']!=bundle['candidate_id'] or alternative['candidate_id']!=bundle['progress_architecture']['alternative_candidate_id']:
        raise ValueError('Load transfer requires exactly the composed physical cell')
    if type(dynamic_factor) not in (float,int) or not 1<=dynamic_factor<=2:raise ValueError('Explicit bounded dynamic-factor hypothesis required')
    beams=sorted([p for p in civil['stock'] if p['role']=='guideway-beam'],key=lambda p:p['at_m'][0])
    start=beams[0]['at_m'][0];L=20.;n=len(beams);maximum=[0.]*(n+1);horizontal=[0.]*(n+1);moments=[0.]*n
    residual=0.;points=0;outside=0;case_rows=[]
    for row in journeys:
        result=row['result']
        if result['candidate_id']!=bundle['candidate_id'] or result['alternative_candidate_id']!=alternative['candidate_id']:
            raise ValueError('Journey loads use another cell or launch revision')
        if result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Exact journey output required')
        if not result.get('trajectory'):
            case_rows.append(dict(name=row['name'],candidate_id=bundle['candidate_id'],journey_evaluation_id=result['evaluation_id'],
                execution=result['execution'],sampled_peak_live_support_reaction_N=None,sampled_states=0,
                force_balance_checked=False,out_of_generated_guideway_states=0,complete_trajectory_load_coverage=False,
                reason='No executed trajectory; failed/held context retained without inventing motion or zero loads'))
            continue
        weight=result['translating_train_mass_kg']*9.80665*dynamic_factor/24
        offsets=[r['offset_behind_leading_nose_m'] for r in bundle['route_axle_offsets_from_leading_nose_m']]
        if len(offsets)!=24:raise ValueError('Exactly24 located unpowered axles required')
        case_peak=0.;case_outside=0
        for step in result['trajectory']:
            if any(not start<=step['front_m']-off<=start+n*L for off in offsets):
                outside+=1;case_outside+=1;continue
            reactions=[0.]*(n+1);local={};assigned=0.;hreact=[0.]*(n+1)
            for off in offsets:
                x=step['front_m']-off;i=min(n-1,int(floor((x-start)/L)))
                if i<0 or i>=n or not start<=x<=start+n*L:raise ValueError('Wheel position outside generated guideway')
                u=x-(start+i*L);left=weight*(L-u)/L;right=weight-left
                reactions[i]+=left;reactions[i+1]+=right;assigned+=weight;local.setdefault(i,[]).append((u,weight))
            for i,loads in local.items():
                Ra=fsum(F*(L-u)/L for u,F in loads)
                m=max([0.]+[Ra*z-fsum(F*max(0.,z-u) for u,F in loads) for z,F in loads])
                moments[i]=max(moments[i],m)
            # Friction brakes act at counted wheel/rail locations. The proposed
            # mechanical drive acts at its finite engaged wayside contacts.
            for off in offsets:
                x=step['front_m']-off;i=min(n-1,int(floor((x-start)/L)));u=x-(start+i*L);F=step['brake_N']/24
                hreact[i]+=F*(L-u)/L;hreact[i+1]+=F*u/L
            model=alternative['conditional_force_model'];contacts=[]
            if model and model['kind'].startswith('pinch'):
                for bank,index,x in model['positions']:
                    if bank in result['scenario']['failed_banks']:continue
                    if any(a+step['front_m']-104.5<=x<=b+step['front_m']-104.5 for a,b in model['train_drive_segments_m']):contacts.append(x)
            elif model and step['traction_N']>0:contacts=[0.]
            if contacts:
                for x in contacts:
                    i=min(n-1,int(floor((x-start)/L)));u=x-(start+i*L);F=step['traction_N']/len(contacts)
                    hreact[i]+=F*(L-u)/L;hreact[i+1]+=F*u/L
            for i,R in enumerate(reactions):maximum[i]=max(maximum[i],R);horizontal[i]=max(horizontal[i],hreact[i]);case_peak=max(case_peak,R)
            residual=max(residual,abs(fsum(reactions)-assigned));points+=1
        case_rows.append(dict(name=row['name'],candidate_id=bundle['candidate_id'],journey_evaluation_id=result['evaluation_id'],
            sampled_peak_live_support_reaction_N=case_peak,force_balance_checked=True,
            out_of_generated_guideway_states=case_outside,complete_trajectory_load_coverage=case_outside==0))
    total=[civil['guideway_known_support_reactions_N'][i]+maximum[i] for i in range(n+1)]
    value=dict(schema='osr-sampled-coupled-civil-loads/1',candidate_id=bundle['candidate_id'],alternative_candidate_id=alternative['candidate_id'],
        source_sha256={'engineering/railway_progress/load_transfer.py':digest(__file__)},
        scenarios=case_rows,sampled_states=points,out_of_generated_guideway_states=outside,dynamic_factor_hypothesis=dynamic_factor,
        support_positions_m=[start+i*L for i in range(n+1)],sampled_live_support_envelope_N=maximum,
        sampled_known_dead_plus_live_envelope_N=total,sampled_longitudinal_force_envelope_N=horizontal,
        sampled_live_span_moment_envelope_Nm=moments,maximum_vertical_balance_residual_N=residual,
        unknown_installed_dead_weights=civil['unknown_plant_mass_items'],
        actual_wheel_rail_dynamics_validated=False,qualified_span_capacity_Nm=None,qualified_foundation_pressure_Pa=None,
        limitations=['Simple-span/equal-static-axle and1.3dynamic hypotheses; sampled maxima are not continuous validated envelopes',
            'Exact reaction positions follow generated wheel/plant coordinates; support and attachment stiffness/CG/load sharing remain unqualified',
            'Opposed clamp frame loads, torsion, lateral wind/seismic, bearings/foundations, fatigue and site geotechnics need their own models'],**FLAGS)
    value['evaluation_id']=identity(value);return value
