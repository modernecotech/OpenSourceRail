"""Human-readable service results and a plot of the actual analytical profile.

Formatting only. This module is deliberately outside the native protection
source set: changing a label cannot invalidate an executed Rust method fixture.
"""
import math

from .service import position_at


def _number(value,digits=1):
    if value is None:return 'unknown'
    return f'{value:,.{digits}f}'.rstrip('0').rstrip('.') if digits else f'{value:,.0f}'


def markdown(value):
    """Detailed, scoped comparison for embedding in the matched design README."""
    chosen=value['selected_scenario'];p=chosen['profile'];z=value['selected_station']
    cap=value['service'];fleet=value['fleet'];proposal=fleet['max2000m_spacing_alternative']
    lines=[
        '**A 120-second nominal service is a viable next software/resource prototype under the declared assumptions. Physical operation is not yet qualified.** Six cars carry 276 people at the proposed cap, giving **8,280 passengers/hour/direction**. The regular-interval mean wait is 60 seconds for unsaturated, uniformly arriving demand; denied boarding and service disruption can increase it.','',
        '### Motion and station design basis','',
        f"The selected {p['distance_m']/1000:g} km case launches at **{p['peak_speed_m_s']*3.6:g} km/h**, coasts without propulsion and enters braking at **{p['arrival_speed_before_braking_m_s']*3.6:.1f} km/h**. Motion takes **{p['runtime_s']:.1f} seconds** before the 35-second dwell. Acceleration is 0.4 m/s² and service deceleration 0.6 m/s²; jerk, grades, flexible-body motion and measured force/current maps are not included.",'',
        '![Analytical unpowered-coasting speed and front-position profile; a following departure starts at 120 seconds](service-profile.svg)','',
        'A leg taking longer than 120 seconds does not itself rule out two-minute departures. Trains can follow through separately protected resources. Reserving the whole interstation leg for one train would impose a different, longer interval. The receiving platform, tail clearance, stopping authority and powered section allocations still have to be available.','',
        '| Retained-drag comparison | Launch | Enter braking | Moving time | Smallest full-engagement station library option |',
        '|---|---:|---:|---:|---:|']
    for distance in (1000.,1500.,2000.):
        r=next(s for s in value['scenarios'] if s['inputs']['distance_m']==distance
               and s['inputs']['speed_cap_m_s']==p['speed_cap_m_s']
               and s['inputs']['dwell_s']==35 and s['inputs']['constant_drag_N_per_car']==1000)
        q=r['profile'];passing=[s for s in r['motor_zone_options'] if s['geometry_full_engagement'] and s['nominal_resource_screen']=='pass']
        length=min((s['length_m'] for s in passing),default=None)
        lines.append(f"| {distance/1000:g} km | {q['peak_speed_m_s']*3.6:g} km/h | {_number(None if q['arrival_speed_before_braking_m_s'] is None else q['arrival_speed_before_braking_m_s']*3.6)} km/h | {_number(q['runtime_s'])} s | {_number(length,0)} m |")
    lines += ['',
        f"The chosen station uses **one shared {z['length_m']:g} m winding per direction**, spanning {z['start_m']:.1f} m to +{z['end_m']:.1f} m relative to the stopped train nose. This is not an independent 450 m launch winding plus a second 450 m receiving winding. The 104.5 m formation and each 12 m car propulsion band are included in the overlap calculation. Two directions require {z['installed_direction_metres']:g} direction-metres, or {z['installed_motor_face_metres']:g} motor-face-metres with two faces per direction.",'',
        f"The proposed routing has **{z['sections_per_direction']} separately addressed 12.5 m sections per direction and two independent train phase/current branches per direction**. A departing train and a receiving train may use different sections only when ownership, phase, current capacity and isolation permit it. One current/phase command cannot simply serve two differently positioned trains. Real switching, protection, bus ratings, thermal duty and bank-failure isolation remain unqualified.",'',
        'Shorter interstation legs can produce faster arrivals and require more receiving length. The station library therefore retains 350/450/600 m choices; a 450 m design fitted to the 2 km case is not automatically sufficient at every shorter stop. The full city proposal counts its different winding lengths separately.','',
        '### Coasting and resistance uncertainty','',
        'The coast solves `dv/dt = -(C + Q v²)/m`, using the actual candidate comparison mass. It does not keep speed constant while claiming the motors are off. The campaign contains 144 primary combinations: 1/1.5/2 km spacing, 10/12/15/20 m/s launch caps, 30/35/45/60 second dwells, and 250/500/1,000 N per-car constant-resistance hypotheses; `Q = 1.8 N/(m/s)²` per car. These are resistance scenarios, not measured magnetic-drag data.','',
        f"**{sum(s['profile']['runtime_s'] is None for s in value['scenarios'])} cases coast to rest before reaching the receiving station.** In particular, 12 m/s cannot complete 2 km under the retained 1,000 N/car hypothesis. The selected 15 m/s case reaches the station, with {p['coast_distance_m']:.1f} m of unpowered coast. At fixed speed and a fixed force-drag hypothesis, reducing train mass also reduces stored kinetic energy; a lighter train need not coast farther.",'',
        f"Calculated mechanical energy per six-car leg is {p['launch_mechanical_kWh_per_train']:.2f} kWh supplied during launch and at most {p['theoretically_recoverable_mechanical_kWh_per_train']:.2f} kWh recoverable during receiving. These exclude actual inverter/converter losses and passenger-services electricity. No supplier electrical-efficiency or regenerative grid-acceptance claim follows from them.",'',
        '### Station occupancy, dwell and disruption','',
        f"With one exclusive lease for the entire winding, the selected nominal station interval is {z['whole_zone_exclusive_minimum_interval_s']:.2f} seconds: only {z['whole_zone_exclusive_120_s_margin_s']:.2f} seconds remain at a 120-second target. With separately addressed sections and the platform checked independently, the largest nominal occupancy is {z['minimum_nominal_resource_interval_s']:.2f} seconds, leaving {z['nominal_120_s_margin_s']:.2f} seconds. This improvement requires the additional section/phase hardware and verified releases.",'',
        '| Resource architecture | First-train dwell extension | Minimum gap in the prescribed timetable | Result |',
        '|---|---:|---:|---|']
    for r in value['station_resource_campaign']:
        label='Addressed sections + platform' if r['architecture']=='section-addressed' else 'One exclusive whole winding'
        state='No resource conflict in the declared event model' if r['screen']=='pass' else 'Conflict: hold/recovery required'
        lines.append(f"| {label} | +{r['delay_first_dwell_s']:g} s | {r['minimum_resource_gap_s']:.2f} s | {state} |")
    lines += ['',
        'The event model follows three trains through three arrivals each and releases a resource after the complete train tail clears it. A 15-second dwell extension fits the addressed-section proposal; a 60-second extension does not. These checks are a finite timing experiment, not a guarantee that every departure remains exactly 120 seconds apart.','',
        '**Recovery cannot be an arbitrary time shift of a coasting train.** Before a departure is committed, dispatch can propose holding at a powered platform and retiming following departures, subject to fresh authority. A train already coasting may have to brake within its owned authority. Restarting it then requires a qualified powered holding/restart location or a located rescue system. The retained-authority Rust braking fixture demonstrates the declared stopping-method response; it does not establish a physical restart or restoration of two-minute service after that disruption.','',
        'The separate native packet checks the existing progressive protection implementation with actual Rust execution. Its detector, integrity and independent-brake readiness assertions are synthetic, and its healthy-gap fixture remains 6–8 mm. Those virtual inputs do not establish the new NdFeB suspension response. Guaranteed brake curves, support-power loss, receiving-power loss, latency and installed phase/current handoff remain operating gates.','',
        '### Passenger capacity and formation alternatives','',
        'The selected six-car comfort proposal is explicitly below the former 14,400 pphpd comparison. At 120 seconds, 10 comfort cars still fall short; 11 cars exceed that arithmetic target. Longer formations need their own platforms, winding overlap, fleet, evacuation and civil design. None silently replaces the six-car proposal.','',
        '| Cars | People/train | Capacity at 120 s | Formation length assumption |',
        '|---:|---:|---:|---:|']
    for f in cap['formation_alternatives']:
        lines.append(f"| {f['cars']} | {f['people_per_train']} | {f['capacity_pphpd']:,.0f} pphpd | {f['formation_length_assumption_m']:.1f} m |")
    lines += ['',
        '### Baghdad fleet and station consequences','',
        f"The retained city plan contains {fleet['retained_total_trainsets']} trainsets. Under the selected launch speed and retained resistance hypothesis, **{fleet['lines_with_unreachable_mainline_events']} of 14 lines have at least one mainline event that cannot reach the next stop**. Their revised retained-stop fleet is unknown, rather than being assigned zero or an invented journey time.",'',
        f"An explicit alternative splits longer events into passenger-stop intervals no longer than 2 km. It gives **{proposal['total_trainsets']:,} trainsets and {proposal['additional_passenger_station_sites']} additional proposed line-stop sites**, with a 12% operating-spare hypothesis and one cold reserve per line. New sites are fractions along retained stop pairs, not surveyed or adopted station locations. The terminal-loop timings are inherited and still need qualification for this train. Existing city maps, stops and headways remain unchanged.",'',
        '| Line | Retained trainsets | Retained-stop result | ≤2km added-stop alternative | Additional proposed sites |',
        '|---|---:|---|---:|---:|']
    for r in fleet['lines']:
        old='Unreachable event(s)' if r['proposed_total_trainsets'] is None else str(r['proposed_total_trainsets'])+' trainsets'
        alt=r['max2000m_stop_spacing_alternative']
        lines.append(f"| {r['line']} | {r['retained_total_trainsets']} | {old} | {alt['total_trainsets']} | {alt['additional_passenger_station_sites']} |")
    counts=proposal['winding_library_counts_per_mainline_circuit']
    lines += ['',
        f"The added-stop alternative requires {counts['450']} × 450 m and {counts['600']} × 600 m directional mainline windings ({proposal['total_required_direction_winding_m_per_mainline_circuit']:,.0f} direction-metres). Terminal service windings are additional. These quantities expose the infrastructure consequence of the service proposal; they are not a priced or physically approved network.",'',
        '### Cost comparison','',
        '**Low unit trainset cost remains an objective, not an established price.** At the same circuit time, changing 180-second service to 120 seconds requires 1.5 times as many active trainsets before rounding and reserves. Unit trainset price would need to fall to two-thirds of the comparison price just to keep fleet purchase cost unchanged.','',
        f"The actual city scenario also changes travel time, stops and reserves. Its {proposal['total_trainsets']:,}-versus-{fleet['retained_total_trainsets']} fleet comparison requires a unit trainset price no more than **{100*proposal['unit_trainset_price_ratio_for_equal_fleet_capex']:.1f}%** of the retained planning price to keep fleet purchase cost level. That excludes the new stations, longer windings, chargers, depot, staff, maintenance, energy, renewals and financing. Actual vehicle prices and complete CAPEX/OPEX remain unknown. No total-system saving is claimed.",'',
        f"Service evaluation: `{value['evaluation_id']}`. Candidate: `{value['candidate_id']}`. The station and scenario identities are retained separately. Physical operating release remains false.",'']
    return '\n'.join(lines)


def render_profile_svg(value):
    """Plot the selected drag-coast solution; no decorative or invented trace."""
    p=value['selected_scenario']['profile'];T=p['runtime_s']
    ta=p['acceleration_duration_s'];tb=T-p['braking_duration_s']
    width,height=1120,770;left,right=88.,1060.;span=right-left
    vmax=max(16.,p['peak_speed_m_s']*1.08)
    x=lambda t:left+span*t/T
    ys=lambda v:325.-220.*v/vmax
    yp=lambda distance:650.-205.*distance/p['distance_m']
    times=sorted(set([0.,T,ta,tb,120.]+[T*k/500 for k in range(501)]))
    speed=' '.join(f'{x(t):.3f},{ys(position_at(p,t)["speed_m_s"]):.3f}' for t in times)
    lead=' '.join(f'{x(t):.3f},{yp(position_at(p,t)["position_m"]):.3f}' for t in times)
    follow=' '.join(f'{x(t):.3f},{yp(position_at(p,t-120)["position_m"]):.3f}' for t in times if t>=120)
    result=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Two-minute dispatch during an analytical unpowered-coasting leg</title>',
        '<desc id="desc">Speed and front position from the selected flat-route analytical model. The following train launches at 120 seconds while the first is still travelling. This is not a levitated-train or safety simulation.</desc>',
        '<style>text{font-family:system-ui,sans-serif;fill:#243c48;font-size:15px}.small{font-size:13px}.title{font-size:23px;font-weight:700}.axis {stroke:#647985;stroke-width:1.3}.grid{stroke:#dce5e9;stroke-width:1}.lead{stroke:#096a8a;stroke-width:3;fill:none}.following{stroke:#b96a12;stroke-width:2.7;fill:none}.dispatch{stroke:#79539d;stroke-width:1.5;stroke-dasharray:6 5}</style>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        '<text class="title" x="35" y="35">A two-minute departure interval can overlap a longer journey</text>',
        f'<text x="35" y="62">Selected analytical case: {p["distance_m"]/1000:g} km · {T:.1f}s moving · {p["peak_speed_m_s"]*3.6:g} km/h launch · unpowered coast</text>']
    for begins,ends,color,label in ((0,ta,'#d9edf1','Launch'),(ta,tb,'#f1f5f7','Coast'),(tb,T,'#f9e9d3','Brake')):
        result.append(f'<rect x="{x(begins):.3f}" y="90" width="{x(ends)-x(begins):.3f}" height="235" fill="{color}"/>')
        center=x(begins)+85 if label=='Coast' else (x(begins)+x(ends))/2
        if ends-begins>6:result.append(f'<text class="small" text-anchor="middle" x="{center:.3f}" y="108">{label}</text>')
    for velocity in range(0,math.ceil(vmax),5):
        y=ys(velocity);result.extend((f'<line class="grid" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>',f'<text text-anchor="end" x="75" y="{y+5:.3f}">{velocity}</text>'))
    for distance in range(0,round(p['distance_m'])+1,500):
        y=yp(distance);result.extend((f'<line class="grid" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>',f'<text text-anchor="end" x="75" y="{y+5:.3f}">{distance:,}</text>'))
    for tick in [0,60,120,180,T]:
        xt=x(tick)
        result.extend((f'<line class="grid" x1="{xt:.3f}" y1="110" x2="{xt:.3f}" y2="325"/>',f'<line class="grid" x1="{xt:.3f}" y1="445" x2="{xt:.3f}" y2="650"/>',
            f'<text text-anchor="middle" x="{xt:.3f}" y="347">{tick:.0f}</text>',f'<text text-anchor="middle" x="{xt:.3f}" y="673">{tick:.0f}</text>'))
    result.extend((f'<line class="axis" x1="{left}" y1="325" x2="{right}" y2="325"/>',
        f'<line class="axis" x1="{left}" y1="110" x2="{left}" y2="325"/>',
        f'<line class="axis" x1="{left}" y1="650" x2="{right}" y2="650"/>',
        f'<line class="axis" x1="{left}" y1="445" x2="{left}" y2="650"/>',
        f'<polyline class="lead" points="{speed}"/>',f'<polyline class="lead" points="{lead}"/>',f'<polyline class="following" points="{follow}"/>',
        f'<line class="dispatch" x1="{x(120):.3f}" y1="85" x2="{x(120):.3f}" y2="682"/>',
        f'<text class="small" x="{x(120)+8:.3f}" y="385">120 s: following train departs</text>',
        '<text x="15" y="86">m/s</text>','<text x="15" y="427">metres</text>',
        '<text text-anchor="middle" x="574" y="706">Seconds since first launch</text>',
        '<text x="90" y="416" style="fill:#096a8a">Blue: first train</text>','<text x="310" y="416" style="fill:#b96a12">Orange: following train front</text>',
        '<text class="small" x="35" y="739">Flat route; declared drag and braking hypotheses. Gaps, levitation, force/current maps and flexible motion are not simulated.</text>',
        '<text class="small" x="35" y="759">Front-position traces do not prove safe separation. Protection, tail clearance and fault stopping require their separate evidence.</text>',
        '</svg>'))
    return '\n'.join(result)+'\n'
