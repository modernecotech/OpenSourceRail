"""Bounded, source-bound publication for the v0.5 primary study."""
from hashlib import sha256
from html import escape
from dataclasses import dataclass
import importlib
import json
import gzip
import os
from pathlib import Path
import platform
import tempfile

from . import model,transition,geometry,field,media,optimisation,evacuation,system_development,reference_assembly,iteration,station,station_structure,station_protocol,station_native,moving_train,system_campaign,closure,manufactured_native,corridor,booster_kit,booster_native,interchange_hubs,line_capacity,hub_access,qualification,assembled_body,shared_hub_layout,body_stiffness,stopped_recovery
from . import drive_design

OUTPUT = model.ROOT / 'docs/design-engine/ferrite-maglev/reference'
EXPECTED={'result.json','index.html','guidebeam-sections.svg','duty-energy.svg','systems-register.json.gz','interface-definition.json.gz','civil-bay-definition.json.gz','field-study.json.gz','field-study.png','optimisation-study.json.gz','evacuation-study.json.gz','evacuation-envelope.svg'}


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def section_svg(result):
    """Dimension the current concrete box section."""
    b=result['inputs']['civil']['narrow_box_screen']
    w=b['outer_width_m'];h=b['outer_depth_m'];tw=b['web_thickness_m'];tf=b['flange_thickness_m']
    area=w*h-(w-2*tw)*(h-2*tf)
    inertia=(w*h**3-(w-2*tw)*(h-2*tf)**3)/12
    scale=min(230/w,270/h);x=80;y=85
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450" role="img" aria-label="Current concrete guidebeam section"><rect width="1000" height="450" fill="#f1f5f9"/><g font-family="sans-serif" fill="#14283d"><text x="25" y="36" font-size="23">Current guidebeam concrete section — provisional</text><rect x="{x}" y="{y}" width="{w*scale}" height="{h*scale}" fill="#087f78"/><rect x="{x+tw*scale}" y="{y+tf*scale}" width="{(w-2*tw)*scale}" height="{(h-2*tf)*scale}" fill="#f1f5f9"/><text x="400" y="130" font-size="20">Width {w:g} m · depth {h:g} m</text><text x="400" y="175" font-size="18">Concrete area {area:.6f} m²</text><text x="400" y="215" font-size="18">Vertical second moment {inertia:.6f} m⁴</text><text x="25" y="405" font-size="16">Reaction iron, joints, prestress and reinforcement are additional scope. Structural acceptance remains open.</text></g></svg>'
    return svg.encode()


def energy_svg(result):
    c=result['inputs'];p=c['power'];d=result['station_powered']['battery']
    rows=[]
    for i,capacity in enumerate((20,30,40)):
        usable=capacity*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low'])
        y=130+i*90
        rows.append(f'<text x="25" y="{y}">{capacity} kWh gross/car</text><rect x="280" y="{y-25}" width="{usable*30}" height="35" fill="#087f78"/><text x="{295+usable*30}" y="{y}">{usable:.1f} kWh EOL/window</text>')
    needed=d['cycle_consumption_kwh_per_car']+d['protected_services_reserve_kwh_per_car']
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="430" viewBox="0 0 1100 430"><rect width="1100" height="430" fill="#f1f5f9"/><g font-family="sans-serif" fill="#172c42"><text x="25" y="35" font-size="24">Services storage budget; main traction is supplied at stations</text><text x="25" y="70">20/30/40 kWh cases, 80% EOL, 60% SOC window; corrected run/disconnected-dwell energy</text>'+''.join(rows)+f'<line x1="{280+needed*30}" x2="{280+needed*30}" y1="90" y2="350" stroke="#a72a34" stroke-width="3"/><text x="25" y="400">Red line: {needed:.2f} kWh cycle plus assumed 10-minute hot reserve; emergency mission and charge acceptance remain open.</text></g></svg>').encode()


def money(value):
    return 'unpriced' if value is None else f'${value:,.0f}'


def render(result):
    from . import interchange_hubs
    hubs=interchange_hubs.read_summary()
    hub_study=json.loads(gzip.decompress((interchange_hubs.OUTPUT/'study.json.gz').read_bytes()))
    hub_conflicts=sum(len(row['spacing_conflicts']) for row in hub_study['baseline']['line_screens'])
    hub_native_view=('<img src="../shared-hub-layout/overview.png" alt="Reopened native shared-station solids with declared vertical display exaggeration">'
                     if result.get('closure_studies',{}).get('shared_hub_layout',{}).get('native_present') else '')
    st=result['station_powered'];tr=st['trajectory'];charge=st['charging'];traffic=st['traffic'];struct=result['station_structure']
    current=result['selected_configuration']['configuration']['civil']
    corridor_rows=''.join(f'<tr><td>{escape(mode)}</td><td>{screen["distance_m"]:g} m</td><td>{screen["runtime_s"]:g} s</td><td>{screen["service_energy"]["battery_kwh_per_car"]:g} kWh/car</td><td>{screen["service_energy"]["charger_kw_per_car"]:g} kW/car</td><td>{screen["service_energy"]["dwell_s"]:g} s</td><td>{screen["headway_lower_bound_s"]:.2f} s; capacity hold</td></tr>' for mode,screen in result['corridor_powered']['operations'].items())
    moving=json.loads(gzip.decompress((moving_train.OUTPUT/'result.json.gz').read_bytes()))
    run=moving['moving_run']
    dossier=json.loads(gzip.decompress((closure.OUTPUT/'dossier.json.gz').read_bytes()))
    campaign=json.loads(gzip.decompress((system_campaign.OUTPUT/'result.json.gz').read_bytes()))
    reserve=dossier['primary_frame_families']['reserve_allocation']
    footing=dossier['foundation_cost_delta']
    adaptive=json.loads((iteration.OUTPUT/'recommendation.json').read_text())
    selected=escape(adaptive['candidate_id'] or 'none; mandatory confirmation held')
    cost_rows=''.join(f'<tr><td>{r["scenario"]}</td><td>{money(r["train_usd"])}</td><td>{money(r["civil_usd_dual_km"])}</td></tr>' for r in result['cost_cases'] if r['ferrite_kg_car']==3000 and r['battery_kwh_car']==30)
    requirement_rows=''.join(f'<tr><td>{r["id"]}</td><td>{escape(r["requirement"])}</td><td>Open</td></tr>' for r in result['applicable_requirements']['requirements'])
    gate_rows=''.join(f'<li>{g["id"]}: {escape(g["name"])} — OPEN</li>' for g in result['gates'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenSourceRail {model.RELEASE_VERSION} — fixed-zone ferrite-maglev development</title>
<style>body{{font:17px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#172c42;background:#f9fbfd}}h1{{font-size:36px;line-height:1.15}}h2{{margin-top:36px}}.banner{{background:#e3f4f0;padding:20px;border-left:5px solid #087f78}}table{{display:block;overflow-x:auto;border-collapse:collapse;width:100%;font-size:15px}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #cad5df}}img{{width:100%;height:auto}}code{{background:#e9eef3;padding:3px;overflow-wrap:anywhere}}a{{color:#006b67}}</style>
<p>PRIMARY DEVELOPMENT · v{model.RELEASE_VERSION}</p><h1>Ferrite-maglev on independent fixed lines</h1>
<div class="banner">Six 17 m GFRP body studies, onboard ferrite PM-biased active support/guidance, station LSM launch/receiving braking, selected midway accelerator zones and coasting elsewhere. Junctions transfer passengers between fixed lines, without train-routing switches. Accepted engineering and physical releases: <strong>0</strong>. The published v0.5.1 configuration is retained as an identified comparison.</div>
<p><a href="result.json">Current configuration, calculations and requirements</a> · <a href="manifest.json">Sources and payload receipt</a> · <a href="systems-register.json.gz">Systems responsibility register</a></p>
<h2>Connected Baghdad digital pilot</h2>
<p><a href="../pilot-delivery/README.md">Product, engineering, delivery and lifecycle evidence</a> connects the equipment ledger, coupled actuator experiment, segmented launch options, full pilot-line operation, procurement/construction cash and native serial business workflow. Accounted equipment exceeds historical mass targets. Failed original removal paths, counted redesigns and unresolved design gates remain visible.</p>
<p><a href="../pilot-product/README.md">Controlled product</a> · <a href="../pilot-actuators/README.md">Actuator simulation</a> · <a href="../launch-optimisation/README.md">Launch search</a> · <a href="../pilot-corridor/README.md">Pilot access/service/finance</a> · <a href="../delivery-schedule/README.md">Resource delivery</a> · <a href="../pilot-lifecycle/README.md">Native lifecycle</a> · <a href="../assurance-profiles/README.md">Executed profiles</a> · <a href="../capability-migration/README.md">v0.4 migration</a></p>
<p>All development profiles executed against current sources: <strong>{result['closure_studies']['connected_pilot']['digital_profiles_executed']}</strong>. Mass targets closed: <strong>{result['closure_studies']['connected_pilot']['mass_targets_closed']}</strong>. Physical and manufacturing gates remain open.</p>
<p>Retained rejected experiment: <a href="../pilot-actuators-rejected-120turn/README.md">120-turn coupled run, failure receipt and exact sources</a> · <a href="../pilot-variant-failures/50faefb04c5f2872c05e342a0e1a65c1fbe56fc01b5b7392085f0b488c7ea999-failed/README.md">matched failed-candidate costs and finance</a>. Later candidates preserve this history.</p>
<h2>Wider-stop urban and suburban operating corridors</h2>
<p>Urban passenger stops target at least {result['operating_strategy']['urban_minimum_stop_spacing_m']/1000:g} km spacing and about {result['operating_strategy']['urban_target_stop_spacing_m']/1000:g} km on average. Suburban stops target {result['operating_strategy']['suburban_minimum_stop_spacing_m']/1000:g}–{result['operating_strategy']['suburban_maximum_stop_spacing_m']/1000:g} km with finite midway acceleration where required. Junctions are passenger transfers between independent fixed lines, without physical train-routing switches. Close retained transfers remain visible spacing/access exceptions. Straight alignments require actual land, utility, grade, clearance and evacuation checks.</p>
<p><a href="../corridor/README.md">Longer corridor model and limits</a> · <a href="../corridor/result.json.gz">Separate trajectories, installed zones, services, capacity and actual Rust fault evidence</a> · <a href="../corridor/manifest.json">Corridor source receipt</a></p>
<img src="../corridor/overview.svg" alt="Separate urban and suburban fixed-zone corridor studies with open operating and hardware gates">
<img src="../corridor/urban-overview.png" alt="Exact urban-profile six-car numerical motion with declared visual amplification"><img src="../corridor/suburban-overview.png" alt="Exact suburban-profile six-car numerical motion including the midway accelerator">
<p><a href="../corridor/urban-motion.mp4">Calculated urban-profile video</a> · <a href="../corridor/suburban-motion.mp4">Calculated suburban-profile video</a>. These use retained numerical motion, with declared visual amplification; ideal-force and physical qualification limits remain explicit.</p>
<table><tr><th>Profile</th><th>Distance</th><th>Run</th><th>Services pack</th><th>Charger input</th><th>Dwell</th><th>Whole-leg headway lower bound</th></tr>{corridor_rows}</table>
<p>The 5 km/300 s AW3 faster comparison retains AW0/AW2 failures under the common speed cap. Current operating cases use 350 m station zones; midpoint booster extent is the union of all three load envelopes and is separately priced.
The new longer-leg studies are separate from the retained 1 km benchmarks below. Motor overlap/current/voltage, services reserve and resource headway must pass for each exact profile. A trajectory or isolated replay does not establish sectioned multi-train protection, retained capacity, geometric confirmation or hardware qualification. City plans retain any shortfall and every unqualified operating design.</p>
<h2>Retained 1 km station launch, coast, arrival and charging benchmark</h2>
<p>The retained flat {tr['inputs']['distance_m']:g} m study uses {tr['inputs']['runtime_s']:g} s, a {tr['inputs']['train_mass_kg']/1000:g} t loaded six-car train, assumed drag, {tr['inputs']['acceleration_m_s2']:g} m/s² launch acceleration and {tr['inputs']['jerk_m_s3']:g} m/s³ jerk. Its {tr['peak_traction_input_kw']/1000:.3f} MW peak traction input and {tr['launch_input_kwh']:.3f} kWh launch input use assumed 85% conversion. Coasting has zero commanded propulsion. Magnetic force/current/voltage/thermal maps and six-car phase registration remain open.</p>
<p>The supplied 90 s/0.8 m/s²/190 s case remains a separate authored benchmark, with a 1.20 MW loss-free charging requirement. The two charts below belong to that benchmark packet, rather than the updated primary run. <a href="../station-powered/README.md">Benchmark scope</a> · <a href="../station-powered/result.json.gz">Trajectories, overlap, gradients, power and procurement targets</a> · <a href="../station-powered/manifest.json">Execution/source receipt</a></p>
<img src="../station-powered/overview.svg" alt="Authored 90 second station launch coast and arrival benchmark"><img src="../station-powered/power.svg" alt="Authored station traction and services power benchmark">
<p>At 45 s connected charging in 60 s dwell, the current services battery supplies the {tr['inputs']['runtime_s']:g} s run plus {charge['disconnected_dwell_s']:g} s disconnected dwell. Replacing {charge['replacement_kwh_per_train']:.2f} kWh/train requires {charge['connected_interface_kw_per_train']/1000:.2f} MW converted output including direct connected services, or {charge['connected_input_kw_per_train']/1000:.3f} MW source input at {charge['charging_efficiency_assumption']*100:g}% assumed efficiency. The current candidate is {charge['candidate_input_kw_per_train']/1000:.2f} MW/train input (240 kW/car); pack charging is {charge['battery_charge_c_rate']:.2f}C. The 30 kWh/car pack retains EOL/SOC/reserve sensitivities rather than a qualified battery selection. Station resistor braking must remain available without another energy consumer.</p>
<p>Protected-zone planning minimum is {traffic['planning_minimum_headway_s']:.2f} s; the {traffic['scheduled_headway_s']:g} s target gives {traffic['normal_passengers_per_hour_direction']:,.0f} normal passengers/hour/direction. City schedules use their actual leg/dwell bounds; selected headways and retained capacity targets are explicit, with proposed stops and terminal motor zones. Grade/speed/overlap failures, stalled-train recovery and receiver failure after launch remain explicit holds. A station cannot restart a distant stationary train without a recovery method.</p>
<h2>GFRP body and manufactured civil-product studies</h2>
<p>The retained 30 kWh budget is14.2 t/car tare, including a5.2 t equipped body,3 t ferrite and an existing1.8 t growth reserve. The primary detail dossier uses the50 kWh reference: {dossier['primary_mass_case']['tare_kg_per_car']/1000:.1f} t tare/{dossier['primary_mass_case']['car_mass_kg']/1000:.1f} t AW3 per car, with the battery increase included once. It charges {reserve['frame_overrun_kg']:.1f} kg/car frame overrun and {reserve['separately_proposed_emergency_kg']:.1f} kg/car exact heavier-case emergency proposal against the retained reserve, leaving {reserve['remaining_before_other_system_growth_kg']:.1f} kg/car before other growth. Four doors/car are used consistently in the configuration, panel takeoff, platform interfaces and evacuation count. Laminate/core properties, distributed hardpoints, joints, fire, crash, fatigue and complete measured mass/CG/inertia remain unqualified.</p>
<p><a href="../station-structure/result.json">Body takeoffs, core substitutions, beam/support families and production bottlenecks</a> · <a href="../station-structure/manifest.json">Reproducibility receipt</a> · <a href="../station-native/model.FCStd">GFRP/civil FreeCAD</a> · <a href="../station-native/model.step.gz">Compressed STEP</a> · <a href="../station-native/native-cad.json">Actual native reopening/solid checks</a></p>
<img src="../station-structure/comparison.svg" alt="Quantity based GFRP and civil product comparisons"><img src="../station-native/overview.png" alt="Actual partial GFRP panel stock and hollow-column civil product material geometry">
<p><a href="../station-native/assembly-visibility.mp4">GFRP/civil assembly visibility video</a>. Developed panel stock and material-region assemblies omit unsized detail; final-position visibility is not motion, collision, deployment or lifting simulation.</p>
<p>The current box uses {current['span_m']:g} m spans and {current['width_m']:.2f} × {current['depth_m']:.2f} m outer dimensions, {current['web_m']*1000:g} mm webs, {current['flange_m']*1000:g} mm flanges and explicit end infills. The supplied 25 m × 1.80 m civil case remains a comparative quantity/cost benchmark. Hollow 1.35/0.95 m columns and 5.4 m³ caps replace placeholder solids. Shallow, shaft and pile-group foundations remain conditional on ground and loads. Thin walls need actual cover/strand/shear/connection and manufacturing detail; native geometry does not prove strength or magnetic-gap motion.</p>
<p>The authored document's rounded no-walkway priced-scope target is about $3.313 million/two-direction route-km. Actual native end-infill quantities are priced separately from rounded budgets. Most proposed savings come from support and production procurement targets, including $22,000/support. The 56.25 route-m/planned-workday bottleneck is an unmeasured two-shift production objective, with cure, connection, lift and survey acceptance holds. The selected deeper guidebeam, terminal civil work, station electrical equipment and conditional foundation increment require current city quantities. This benchmark is not their installed cost. Walkway deletion remains unapproved.</p>
<h2>Retained 1 km moving six-car numerical benchmark</h2>
<p><a href="../moving-train/README.md">Moving model and limits</a> · <a href="../moving-train/result.json.gz">Actual six-car results, failed comparisons, controls and traces</a> · <a href="../moving-train/manifest.json">Exact source/build/media receipt</a> · <a href="../moving-train/moving-train.mp4">Calculated moving-train video</a></p>
<img src="../moving-train/overview.png" alt="Calculated moving six-car positions on repeated flexible spans, with declared vertical amplification">
<p>The retained component-benchmark candidate executes {run['completed_moving_steps']:,} actual Rust moving steps over {run['executed_duration_s']:g} s. Six separate rigid-car states couple to repeated flexible vertical spans and a longitudinal spring/damper chain. Physical numerical gaps span {run['minimum_gap_m']*1000:.3f}–{run['maximum_gap_m']*1000:.3f} mm; peak pair force is {run['peak_coupler_force_n']/1000:.3f} kN, and indexing spread is {run['maximum_magnetic_phase_spread_degrees']:.3f} electrical degrees. Reduced stiffness and signed sensor-bias confirmations, independent moving-load/work/refinement controls and rejected comparisons remain recorded. These are ideal-force calculations: real shared-field phase/current feasibility, normal/thrust coupling, flexible bodies, lateral/soil/contact response and physical timing remain open. The video uses recorded motion and declared vertical/pitch amplification; it is not an assembled-clearance or physical validation.</p>
<h2>Manufactured details and structural load paths</h2>
<p><a href="../manufactured-dossier/README.md">Specifications, margins and missing tests</a> · <a href="../manufactured-dossier/dossier.json.gz">Full manufactured design dossier</a> · <a href="../manufactured-dossier/detail-definition.json">Connection material definition</a> · <a href="../manufactured-native/model.FCStd">Native detail FreeCAD</a> · <a href="../manufactured-native/model.step.gz">Native detail STEP</a> · <a href="../manufactured-native/native-cad.json">Actual export/reopening receipt</a> · <a href="../manufactured-native/assembly-visibility.mp4">Detail visibility video</a></p>
<img src="../manufactured-native/overview.png" alt="Partial counted primary frame stock and body, coupler, stator and bearing connection candidates">
<p>The dossier counts {dossier['primary_frame_families']['defined_member_piece_count']} primary/opening frame members, supported panel alternatives, local patches and joints, guided high-stiffness couplers, stator cassette mounts and fixed/guided bearings. Prestress/handling cases retain failed end details and a reduced-bond candidate. Emergency forces are allocated by actual pad positions and span anchorage, rather than an assumed percentage. The conditional footing change adds {footing['quantity_basis']['extra_concrete_m3']:.1f} m³ concrete per support plus separately counted reinforcement and earthworks, at an unquoted {money(footing['incremental_support_allowance_usd'])} incremental target. This is an assumed-ground proposal, not accepted foundation selection. Local clamp, bond/fastener, strand/end-zone, fatigue/crash, complete equipment and manufacturing tolerances remain qualification gates. Partial untrimmed stock geometry has no assembled interference authority.</p>
<h2>Retained 1 km integrated Rust ownership and station-control benchmark</h2>
<p><a href="../system-campaign/README.md">Campaign scope</a> · <a href="../system-campaign/result.json.gz">Protected resources, motor checks and emergency/recovery sizing</a> · <a href="../system-campaign/executed.json.gz">Actual command/input/output records</a> · <a href="../system-campaign/manifest.json">Source receipt</a></p>
<img src="../system-campaign/overview.svg" alt="Actual Rust station and resource campaign outcomes with virtual full-tail clearance">
<p>{len(campaign['cases'])} actual Rust cases compose protected launch/receiving ownership with incoming movement, dwell and committed departure. Receiver, sensor, drive, resistor, stale, phase and commitment negative cases preserve support and disable physical outputs. Equivalent scalar electrical constants enforce air-gap power balance without a measured motor map. Virtual detectors and one local controller do not implement cross-controller handover. Independent friction-brake and station-winch proposals expose force, delay, heat energy, clamp/load path, battery reserve, cable reach and anchors. Safe modulation, friction/fade, heat transfer, curved access and full physical stopping/recovery remain open.</p>
<h2>Located booster hardware and independently equipped rescue nodes</h2>
<p><a href="../booster-kit/README.md">Material quantities, recovery alternatives and QA</a> · <a href="../booster-kit/result.json.gz">Full kit calculations</a> · <a href="../booster-kit/definition.json">Partial kit material definition</a> · <a href="../booster-native/model.FCStd">Booster/rescue FreeCAD</a> · <a href="../booster-native/model.step.gz">Booster/rescue STEP</a> · <a href="../booster-native/native-cad.json">Actual native checks</a> · <a href="../booster-native/assembly-visibility.mp4">Booster/rescue stock visibility video</a></p>
<img src="../booster-kit/overview.svg" alt="Calculated recovery alternatives across rescue-node spacing, towing speed and battery capacity"><img src="../booster-native/overview.png" alt="Defined fixed-booster mount and rescue portal drum anchor and foundation material regions">
<p>The kit counts2.5 m face cassettes,12.5 m electrical sections, mount stock/bolts, cabinets and pads separately from ordinary route civil work. Spatial fixed-bearing reactions and equivalent I²R duty are explicit interfaces; magnetic normal forces, winding/core/cooling and a qualified thermal network remain open. Recovery compares independently accessible nodes at intervals up to 1 km with midpoint-only facilities,0.5/1 m/s towing and30/50/60 kWh services packs. Rope, termination factors, annular drum/shaft, portal, anchors, conditional standalone foundation and rated drive/power targets are counted. The failing midpoint-only30 kWh slow-winch case remains recorded. Co-location with a station, booster or pier earns no automatic access, foundation or cost credit. Cable deployment, actual essential loads, certified winch/rope/brakes, ground, evacuation and physical rescue acceptance remain open. Native stock visibility is not an assembled clearance or full system demonstration.</p>
<h2>Finite magnets and force evidence</h2><p>Equal-volume conventional, segmented, finite-orientation and iron-backed seeds retain block identities and magnetization vectors. The reproduced Rehberg–Blümler ring controls establish an air-core analytical benchmark; no ring percentage is credited as railway lift or material saving. Native exposed pole area differs from the 12 m² ideal screen. Shared support/thrust, saturation, hot force/cold demagnetization, losses and real effective area require 3D calculation and rig correlation.</p>
<img src="field-study.png" alt="Two-dimensional magnetic coupon equation study, with unconverged force mesh"><p><a href="field-study.json.gz">Full two-dimensional grids and numerical controls</a>. Coupon force refinement is unconverged; no physical lift credit is allowed.</p>
<h2>Durable Rust station launch control</h2><p>Offline tests exercise atomic corridor/receiving-berth/overlap reservation, pre-launch expiry, post-launch commitment, receiver faults, restart, replay and complete-tail-clearance requirements. Committed ownership survives permission expiry. The local conflict domain is bounded to 32 resources and one controller; this is not a distributed citywide authority. Fresh readiness/clearance inputs are synthetic assertions, not commissioned sensors. SBC supervision, deterministic MCU loops and independent trips remain separate obligations.</p>
<p><a href="../station-protocol/replay.json">Actual Rust station control replay</a> · <a href="../station-protocol/executed-tests.txt.gz">Actual compiler/replay/protocol test commands and output</a> · <a href="../station-protocol/manifest.json">Source and execution receipt</a>. Every physical output remains disabled. Scalar motor constants are unmeasured; no hardware timing or real current map is established.</p>
<h2>Adaptive mechanical, civil and station-control search</h2><p><a href="../iterative/README.md">Generation scope</a> · <a href="../iterative/recommendation.json">Confirmed research recommendation</a> · <a href="../iterative/result.json.gz">Variants, ancestry, actual Rust/beam traces and station confirmations</a>. Exact candidate <code>{selected}</code> is preferred only within evaluated bounds and declared weights. Proposals vary body/equipment allocations, beam geometry, gains, runtime, winding length and acceleration; failed mandatory confirmation disqualifies the revision. Reference and city defaults are not automatically promoted.</p><img src="../iterative/progress.svg" alt="Observed bounded adaptive design generation progress">
<h2>Whole-system comparison scorecards</h2><p><a href="optimisation-study.json.gz">All indexed vehicle/beam comparisons</a>. Complete installed cost, total manufactured mass, supplier-origin content and accepted erection time remain unknown. Body and magnetic equipment allocations are targets; services/HVAC energy is not automatically reduced with body mass. Station traction is accounted separately from the services pack.</p>
<table><tr><th>Scenario</th><th>Repeat six-car allowance</th><th>Ordinary viaduct with fallback access</th></tr>{cost_rows}</table>
<p>These are quantity/process assumptions without supplier quotations. First-pilot, station buildings, actual electrical ratings and utility reinforcement, terminal/depot/recovery, land/air rights, development/factory capital, evacuation, EPC, tax/finance and lifecycle omissions remain open. City bills separately price eight scopes: fleet, ordinary elevated civil, terminal civil, station electrical targets, a conditional footing increment, booster electrical plant, booster mount stock and independent rescue kits. None is a complete railway price. No proven localisation percentage is claimed.</p>
<h2>Native magnetic interface and fallback civil bay</h2><p>The partial interface retains exact cartridge/fastener material regions and hybrid floor load paths; it is not a complete equipped GFRP train. Reaction iron, bearings, connections, capture, tolerances and reinforcement remain necessary.</p>
<p><a href="../native/interface/model.FCStd">Interface FreeCAD</a> · <a href="../native/interface/model.step.gz">Interface STEP</a> · <a href="../native/civil-bay/model.FCStd">Civil FreeCAD</a> · <a href="../native/civil-bay/model.step.gz">Civil STEP</a> · <a href="../native/interface/native-cad.json">Native receipt</a></p>
<img src="../native/interface/overview.png" alt="Current partial magnetic interface and hybrid GFRP floor"><img src="../native/interface/cartridge-detail.png" alt="Ferrite cartridge retainer fastener and winding-envelope detail"><img src="../native/civil-bay/overview.png" alt="Current balanced beams hollow supports and fallback walkway material regions"><img src="guidebeam-sections.svg" alt="Current selected guidebeam section dimensions"><img src="duty-energy.svg" alt="Services battery charging sensitivity with main traction supplied at stations">
<p><a href="../native/interface/assembly-visibility.mp4">Interface visibility video</a> · <a href="../native/civil-bay/assembly-visibility.mp4">Civil visibility video</a>. These CAD videos show final-position visibility; the separate moving-train video uses calculated motion.</p>
<h2>Beam-only evacuation target</h2><p><a href="evacuation-study.json.gz">Full evacuation studies and outstanding evidence</a> · <a href="../beam-only/model.FCStd">Beam-only FreeCAD</a> · <a href="../beam-only/model.step.gz">Beam-only STEP</a> · <a href="../beam-only/manifest.json">Native receipt</a>. Continuous walkway removal depends on an accepted all-stop evacuation/recovery solution. The vertical spiral chute remains a candidate; fabric/deployment/assistance, ground exit, fire, wind and safe landing over roads/water/roofs are unresolved. No net system saving is released from gross deleted material.</p>
<img src="../beam-only/overview.png" alt="Beam-only research geometry with necessary iron and hollow supports"><img src="evacuation-envelope.svg" alt="Illustrative inclined and vertical controlled-descent evacuation envelopes">
<h2>Entry, supports and vertical replay</h2><p><a href="../system-development/entry/model.FCStd">Entry FreeCAD</a> · <a href="../system-development/entry/model.step.gz">Entry STEP</a> · <a href="../system-development/compact-support/model.FCStd">Support FreeCAD</a> · <a href="../system-development/study.json.gz">Entry/support sensitivity evidence</a> · <a href="../system-development/entry-material-list.csv">Partial entry materials</a> · <a href="../system-development/support-demands.csv">Support demands</a> · <a href="../system-development/software-replay.json">Advisory egress Rust replay</a> · <a href="../system-development/native-derived-coupling.json">Native-derived vertical replay</a> · <a href="../system-development/manifest.json">Source receipt</a></p>
<img src="../system-development/entry/overview.png" alt="Partial empty chute cassette and extended doorway entry"><img src="../system-development/compact-support/overview.png" alt="Hollow support quantity sensitivity with unqualified foundation">
<p><a href="../system-development/entry/assembly-visibility.mp4">Entry visibility video</a> · <a href="../system-development/compact-support/assembly-visibility.mp4">Support visibility video</a>. Support demand screens do not establish capacity. Extended entry hardware is not a selected travel-stowable chute.</p>
<p><a href="../coupled/result.json">Actual Rust/vertical-beam replay</a> · <a href="../coupled/receipt.json">Compiler and source receipt</a>. This retained demonstration is one stationary rigid car with three body modes and ideal instantaneous force channels. The new moving six-car study is separate; flexible bodies, actual shared magnetic maps, soil/joints/contact and physical correlation remain open in both.</p>
<h2>Six-car Baghdad station and all-city planning</h2><p><a href="../baghdad-reference/station/model.FCStd">Partial station FreeCAD</a> · <a href="../baghdad-reference/station/model.step.gz">Station STEP</a> · <a href="../baghdad-reference/study.json">Station quantities and emergency-energy sensitivities</a> · <a href="../baghdad-reference/requirements.json">Current applicability register</a> · <a href="../baghdad-reference/station/assembly-visibility.mp4">Station visibility video</a></p>
<img src="../baghdad-reference/station/overview.png" alt="Six-car Baghdad partial floor frames and flush island-platform lift">
<p>Six 17 m bodies total 102 m; assumed coupling gaps give 104.5 m. Four doors/car, magnetic-arm clearances and bridge-plate requirements share the current configuration. Full station supports/stairs/services and equipment remain unqualified. <a href="../../../../engineering/ferrite_maglev/city-index.md">All 266 city packages</a> now locate proposed operating stops on mapped polylines, retain access assignments, retain passenger-transfer spacing conflicts, locate booster/rescue assets and report source versus operating counts, capacity shortfalls, headway, fleet, battery duty and eight-term bills. Sectioned protection and accessible transfer hubs remain unqualified; no train switches are inferred. Their flat motion/capacity screens do not approve sites, grades, curved magnetic phase/guidance or land. Any unresolved capacity/trajectory case remains visible.</p>
<h2>Baghdad interchange alternatives — unselected</h2>
<p>The default Baghdad reference remains {hubs['baseline_stops']} proposed stops with {hub_conflicts} spacing conflicts. <a href="../interchange-hubs/README.md">Interchange investigation and limits</a> · <a href="../interchange-hubs/study.json.gz">Complete alternatives and source evidence</a> · <a href="../interchange-hubs/manifest.json">Receipt</a>.</p>
<img src="../interchange-hubs/overview.svg" alt="Unchanged Baghdad guideways and extended passenger links, with a separate unselected shared-site guideway concept">
<p>{hubs['unique_pairs']} pairs produce {hubs['placement_variants']} extended-transfer placements and {hubs['network_alternatives']} bounded network alternatives, including rejected extent controls. Original cross-line boarding platforms remain in the unchanged-guideway options. Grouping station IDs does not remove their physical walks; cross-line transfers may require both connector arms. The focused {escape(hubs['focused_investigation']['id'])} midpoint case has about {hubs['focused_investigation']['maximum_reference_access_arm_m']:.0f} m maximum reference access arm and {hubs['focused_investigation']['unique_reference_connector_m']:.0f} m unique connector. Its partial electrical target allowance is not a quote or complete economic break-even.</p>
<p>Separate coordinated shared-site concepts physically draw the involved fixed lines through a common location. They change guideway geometry: old civil classifications and prices are not reused. The original concept leaves station tangents, levels, structures and internal walks undefined; its100 m compact walk remains a sensitivity assumption and {hubs['compact_hubs_proved']} compact layouts are proved by that packet. The separate geometry study below develops fitted alternatives and actual paths. No alternative is selected, no train-routing switches are introduced, and access/flow/lift resilience, shade, rests, fire/evacuation, land and full lifecycle cost remain open.</p>
<h2>Work to close the remaining points</h2>
<p><a href="../qualification/README.md">Requirement-specific qualification tasks and test protocols</a> · <a href="../qualification/manifest.json">Qualification source receipt</a>. The task graph distinguishes executable development studies, supplier and site records, physical rig measurements and independent acceptance. A prepared procedure or synthetic record does not close a physical requirement.</p>
<p><a href="../line-capacity/README.md">Sectioned multi-train capacity prototype</a> · <a href="../line-capacity/manifest.json">Capacity source and execution receipt</a>. Progressive reservations use actual local Rust ownership and conservative stopping envelopes. Delayed clearance, stale observations, obstruction, rollback and unavailable braking are separate controls. This is an additional bounded study; current city headways and capacity holds are retained.</p>
<img src="../line-capacity/overview.svg" alt="Bounded multi-train reservation studies and adverse controls, without operational acceptance">
<p><a href="../hub-access/README.md">Interchange access, structures and passenger-flow alternatives</a> · <a href="../hub-access/manifest.json">Access source receipt</a>. Connector modules and supports, access gradients, rests, lifts, passenger pulses and outage cases are counted explicitly. Reference loads and flow assumptions require local qualification; no connector or compact shared-site hub is selected.</p>
<img src="../hub-access/overview.svg" alt="Provisional connector structure and accessible passenger-flow alternatives with open site and structural gates">
<h2>Stopped controller recovery</h2>
<p><a href="../stopped-recovery/README.md">Recovery protocol and limits</a> · <a href="../stopped-recovery/study.json.gz">Actual inputs, checkpoints and event transcripts</a> · <a href="../stopped-recovery/manifest.json">Source receipt</a>. A separately pinned model and policy, fresh whole-consist evidence at declared berths and a fenced new epoch are required. Reconciliation is atomic across all resources; old contracts stay retired and fresh prepare/commit is mandatory. Every retained replay is re-executed during verification. Moving restart, cross-controller handover, authenticated installed persistence and physical detector/timing qualification remain open.</p>
<img src="../stopped-recovery/overview.svg" alt="Actual local stopped-recovery cases and atomic adverse rejections; no physical release">
<h2>Assembled structural material regions</h2>
<p><a href="../assembled-body/README.md">Assembled body, load-path revisions and limits</a> · <a href="../assembled-body/model.FCStd">Native structural assembly</a> · <a href="../assembled-body/model.step.gz">Compressed STEP</a> · <a href="../assembled-body/mass-properties.json">Geometry-derived partial mass and inertia</a> · <a href="../assembled-body/cut-list.csv">Counted cut list</a> · <a href="../assembled-body/legacy-collision-control.json">Retained incompatible-layout control</a> · <a href="../assembled-body/manifest.json">Source receipt</a>.</p>
<p>Joined structural stock, panels, hardpoints and cartridge interfaces are placed as defined material regions. The former crosshead/guidebeam interference and incompatible bolt arrangement remain negative controls. Revised arms and fasteners carry their actual geometry, loads and counted mass. Native mass and inertia use declared densities; omitted equipment and unqualified material/joint behavior prevent an equipped-vehicle or manufacturing claim. Body and joint compliance are separate from the retained rigid-car numerical plant.</p>
<img src="../assembled-body/overview.png" alt="Native candidate assembled structural body and declared interfaces"><img src="../assembled-body/frame-cutaway.png" alt="Structural members and revised load paths with panels cut away"><img src="../assembled-body/six-car.png" alt="Six repetitions of the defined structural candidate, with omitted equipment explicit">
<p><a href="../assembled-body/assembly-visibility.mp4">Structural assembly visibility video</a>. A staged visibility sequence does not qualify a movement path, tooling, lifting or manufacturing process.</p>
<h2>Active support and station launch construction</h2>
<p><a href="../drive-construction/README.md">Control responsibilities, coil construction and launch design</a> · <a href="../drive-construction/bom.csv">Counted purchasing BOM</a> · <a href="../drive-construction/winding-schedule.csv">Phase/slot winding schedule</a> · <a href="../drive-construction/connections.csv">Electrical interface schedule</a> · <a href="../drive-construction/study.json.gz">Quantities, R/L/voltage, thermal and braking screens</a> · <a href="../drive-construction/execution.json.gz">Actual Rust current/commutation execution</a> · <a href="../drive-construction/manifest.json">Source receipt</a>.</p>
<p>Ferrite provides bias; measured-gap support and guidance require active coil current. The SBC supervises allocation, while proposed local MCU loops and independent hardware protection control power. The counted candidate has 432 physical coils and 288 bipolar current circuits per six-car train. A separate 350 m station LSM winding/direction uses four custom converters and 560 face cassettes per two-direction station. A compact 50-turn support coil passes declared depth/packing screens; the larger pack and lower-turn current failures remain retained. High station current, voltage and braking duties remain visible. These calculations and 17 executable coupon/adverse cases do not replace the ideal-force moving plant or qualify hardware.</p>
<img src="../drive-construction/architecture.svg" alt="Separate onboard active support and local current control versus wayside LSM launch and receive"><img src="../drive-construction/construction.svg" alt="Dimensioned compact support winding and launch cassette construction; complete winding and magnetic fit remain open">
<h2>Longitudinal stock alternatives after the stiffness hold</h2>
<p><a href="../body-stiffness/README.md">Exact drilled-stock alternatives and unchanged confirmation criteria</a> · <a href="../body-stiffness/study.json.gz">Full mass, compliance and moving-run comparison</a> · <a href="../body-stiffness/manifest.json">Source and execution receipt</a>. The GFRP sensitivity retains its phase-limit failure. Alternative steel spines keep the same outer envelope, count changed wall cuts and longer crush spacers, and add every incremental material kilogram to the full retained AW3 mass. Their actual Rust runs retain the existing phase/gap/force criteria. This tests a bounded repair idea; thin-wall joints, welds, thermal behavior, shell/frame participation and the heavier load cases remain separate requirements. No alternative is adopted as the equipped body or city default.</p>
<img src="../body-stiffness/overview.svg" alt="Actual full-mass longitudinal stock alternatives with unchanged phase limits and unresolved joint acceptance">
<h2>Fitted shared-hub station geometry</h2>
<p><a href="../shared-hub-layout/README.md">Station tangents, transitions and computed passenger routes</a> · <a href="../shared-hub-layout/geometry.json">Explicit geometric units</a> · <a href="../shared-hub-layout/manifest.json">Source receipt</a>. The study accounts for both directions' finite powered zones, full train and boarding-door extents, transition curvature and actual circulation obstacles. Invalid through-line constructions remain rejected controls; terminal alternatives require explicit turnback geometry. New station/guideway/access quantities receive no former civil price credit. Land, structures, magnetic curve behavior, services and operation remain unqualified, and no hub is selected.</p>
<img src="../shared-hub-layout/overview.svg" alt="Fitted and rejected shared-hub geometric alternatives"><img src="../shared-hub-layout/station-plan.svg" alt="Station train, door, platform and access geometry with explicit limits">
{hub_native_view}
<h2>Acceptance gates</h2><ul>{gate_rows}</ul><details><summary>{len(result['applicable_requirements']['requirements'])} applicable requirements, including all 100 supplied specification items — acceptance remains open</summary><table>{requirement_rows}</table></details></html>'''.encode()


@dataclass(frozen=True)
class _VerifiedConnectedPilot:
    """Operation-local verified bytes; never retained between operations."""
    summary_json: bytes
    manifest_sha256: tuple


def _connected_pilot_manifests():
    from . import pilot_release
    modules=[importlib.import_module('engineering.ferrite_maglev.'+name)
             for _,name,_ in pilot_release.COMPONENTS]
    return {(module.OUTPUT/'manifest.json').relative_to(model.ROOT).as_posix():
            sha256((module.OUTPUT/'manifest.json').read_bytes()).hexdigest()
            for module in [*modules,pilot_release]}


def _verify_connected_pilot():
    from . import pilot_release
    before=_connected_pilot_manifests()
    summary=pilot_release.read_summary()
    if before!=_connected_pilot_manifests():
        raise ValueError('connected pilot receipts changed while verifying')
    return _VerifiedConnectedPilot(encoded(summary),tuple(sorted(before.items())))


def _check_connected_pilot(context):
    if (not isinstance(context,_VerifiedConnectedPilot)
            or dict(context.manifest_sha256)!=_connected_pilot_manifests()):
        raise ValueError('connected pilot receipts changed after verification')
    return json.loads(context.summary_json)


def closure_studies(*, _pilot=None):
    context=_verify_connected_pilot() if _pilot is None else _pilot
    _check_connected_pilot(context)
    result=dict(line_capacity=line_capacity.read_summary(),hub_access=hub_access.read_summary(),
                qualification=qualification.read_summary(),assembled_body=assembled_body.read_summary(),
                shared_hub_layout=shared_hub_layout.read_summary(),body_stiffness=body_stiffness.read_summary(),
                stopped_recovery=stopped_recovery.read_summary(),drive_construction=drive_design.read_summary(),
                connected_pilot=_check_connected_pilot(context))
    return result

def payload():
    before=model.sources();result=model.build()
    pilot=_verify_connected_pilot()
    result['source_sha256']=before
    result['runtime']=runtime()
    result['retained_evidence']=external_evidence(_pilot=pilot)
    result['closure_studies']=closure_studies(_pilot=pilot)
    numerical=field.study()
    files={'result.json':encoded(result),'index.html':render(result),
            'guidebeam-sections.svg':section_svg(result),'duty-energy.svg':energy_svg(result),
            'systems-register.json.gz':gzip.compress(encoded(transition.build()),mtime=0),
            'interface-definition.json.gz':gzip.compress(encoded(geometry.interface()),mtime=0),
            'civil-bay-definition.json.gz':gzip.compress(encoded(geometry.civil_bay()),mtime=0),
            'optimisation-study.json.gz':gzip.compress(encoded(optimisation.study()),mtime=0),
            'evacuation-study.json.gz':gzip.compress(encoded(evacuation.study()),mtime=0),
            'evacuation-envelope.svg':evacuation.envelope_svg(evacuation.study()),
            'field-study.json.gz':gzip.compress(encoded(numerical),mtime=0),'field-study.png':media.field_image(numerical)}
    if before!=model.sources():raise ValueError('sources changed while calculating')
    return files


def runtime():
    import scipy,numpy,matplotlib
    return dict(python=platform.python_version(),scipy=scipy.__version__,numpy=numpy.__version__,matplotlib=matplotlib.__version__)


def external_evidence(*, _pilot=None):
    from . import coupled,cities
    context=_verify_connected_pilot() if _pilot is None else _pilot
    _check_connected_pilot(context)
    iteration.verify();station.verify();station_structure.verify();station_protocol.verify();station_native.verify()
    moving_train.verify();system_campaign.verify();closure.verify();manufactured_native.verify()
    corridor.verify();booster_kit.verify();booster_native.verify();interchange_hubs.verify()
    line_capacity.verify();hub_access.verify();qualification.verify()
    assembled_body.verify();shared_hub_layout.verify();body_stiffness.verify();stopped_recovery.verify()
    drive_design.verify()
    base=model.ROOT/'docs/design-engine/ferrite-maglev'
    geometry.verify_native(base/'native');coupled.verify(base/'coupled');evacuation.verify_native(base/'beam-only')
    system_development.verify(base/'system-development')
    reference_assembly.verify(base/'baghdad-reference')
    catalogue=cities.verify_index()
    if not catalogue['current']:raise ValueError('city catalogue inputs/outputs changed: '+str(catalogue['errors'][:3]))
    result={p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in (base/'native/manifest.json',base/'coupled/receipt.json',base/'beam-only/manifest.json',base/'system-development/manifest.json',base/'baghdad-reference/manifest.json',base/'iterative/manifest.json',base/'station-powered/manifest.json',base/'station-structure/manifest.json',base/'station-protocol/manifest.json',base/'station-native/manifest.json',base/'moving-train/manifest.json',base/'system-campaign/manifest.json',base/'manufactured-dossier/manifest.json',base/'manufactured-native/manifest.json',base/'corridor/manifest.json',base/'booster-kit/manifest.json',base/'booster-native/manifest.json',base/'interchange-hubs/manifest.json',base/'line-capacity/manifest.json',base/'hub-access/manifest.json',base/'qualification/manifest.json',base/'assembled-body/manifest.json',base/'shared-hub-layout/manifest.json',base/'body-stiffness/manifest.json',base/'stopped-recovery/manifest.json',base/'drive-construction/manifest.json')}
    _check_connected_pilot(context)
    result.update(dict(context.manifest_sha256))
    return result


def publish(output=OUTPUT, *, check=False):
    output=Path(output).resolve();files=payload()
    manifest=dict(schema='osr-primary-infrastructure-publication/1',version=model.RELEASE_VERSION,family='ferrite-pm-maglev-study',
                  source_sha256=model.sources(),files_sha256={name:sha256(data).hexdigest() for name,data in files.items()},**model.FLAGS)
    files['manifest.json']=encoded(manifest)
    if check:
        verify(output)
        for name,data in files.items():
            if (output/name).read_bytes()!=data:raise ValueError('generated primary study is stale: '+name)
    else:
        if output.exists() and any(output.iterdir()) and not (output/'manifest.json').is_file():
            raise ValueError('nonempty output is not an owned primary publication')
        output.mkdir(parents=True,exist_ok=True)
        for name,data in files.items():
            fd,temporary=tempfile.mkstemp(prefix='.maglev-',dir=output)
            try:
                with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
                os.replace(temporary,output/name)
            finally:
                if Path(temporary).exists():Path(temporary).unlink()
    return manifest


def verify(output=OUTPUT):
    output=Path(output).resolve();m=json.loads((output/'manifest.json').read_text())
    if m['schema']!='osr-primary-infrastructure-publication/1' or m['family']!='ferrite-pm-maglev-study':
        raise ValueError('not a primary maglev publication')
    if m['source_sha256']!=model.sources():raise ValueError('primary study sources changed')
    expected=EXPECTED
    if {p.name for p in output.iterdir()} != expected|{'manifest.json'}:
        raise ValueError('unexpected files in primary publication')
    if set(m['files_sha256'])!=expected:raise ValueError('exact bounded publication inventory required')
    for name,digest in m['files_sha256'].items():
        if (output/name).is_symlink() or sha256((output/name).read_bytes()).hexdigest()!=digest:raise ValueError('publication file differs: '+name)
    r=json.loads((output/'result.json').read_text())
    if r['source_sha256']!=m['source_sha256'] or r['family']!=m['family']:raise ValueError('result identity differs')
    if any(o.get(k) is not False for o in (m,r) for k in model.FLAGS):raise ValueError('study asserted a release')
    pilot=_verify_connected_pilot()
    if r.get('retained_evidence')!=external_evidence(_pilot=pilot):raise ValueError('retained native/coupled evidence differs')
    if r.get('closure_studies')!=closure_studies(_pilot=pilot):raise ValueError('closure studies differ')
    if m['source_sha256']!=model.sources():raise ValueError('primary study sources changed while verifying')
    return m
