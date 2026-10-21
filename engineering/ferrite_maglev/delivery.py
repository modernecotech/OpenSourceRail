"""Bounded, source-bound publication for the v0.5 primary study."""
from hashlib import sha256
from html import escape
import json
import gzip
import os
from pathlib import Path
import platform
import tempfile

from . import model,transition,geometry,field,media,optimisation,evacuation,system_development,reference_assembly,iteration

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
    rows=result['adverse_energy_cases'];maxkw=700
    bars=[]
    for i,r in enumerate(rows):
        y=110+95*i;label=f"Hot {r['requested_speed_kmh']} km/h; regen {'available' if r['regeneration_available'] else 'unavailable'}"
        bars.append(f'<text x="25" y="{y}" font-size="16">{label}</text><rect x="370" y="{y-22}" width="{r["balanced_charger_kw"]/maxkw*530}" height="33" fill="#087f78"/><text x="{380+r["balanced_charger_kw"]/maxkw*530}" y="{y+1}" font-size="16">{r["balanced_charger_kw"]:.1f} kW</text>')
    return ('''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="450" viewBox="0 0 1100 450" role="img" aria-label="Adverse cycle balanced charging requirements"><rect width="1100" height="450" fill="#f1f5f9"/><g fill="#14283d" font-family="sans-serif"><text x="25" y="36" font-size="23">Calculated charging duty per car — assumed level 1 km cycle</text><text x="25" y="67" font-size="15">Heaviest target AW3; 60 s dwell / 45 s effective charge; excludes additional conversion losses.</text>'''+''.join(bars)+f'<line x1="{370+600/maxkw*530}" x2="{370+600/maxkw*530}" y1="80" y2="345" stroke="#a72a34" stroke-width="3"/><text x="25" y="405" font-size="17">Red line: 600 kW charger candidate. These calculations do not validate motor efficiency or route operation.</text></g></svg>').encode()


def money(value):
    return 'unpriced' if value is None else f'${value:,.0f}'


def render(result):
    adaptive=json.loads((iteration.OUTPUT/'recommendation.json').read_text())
    adaptive_id=escape(adaptive['candidate_id'] or 'none; confirmation held')
    search=result['whole_system_optimisation'];best=search['minimum_indexed_allowance_candidate']
    best_text=f"${best['civil']['indexed_allowance_usd_dual_km']:,.0f}" if best else 'none; no candidate passes the numerical screens'
    costs=[r for r in result['cost_cases'] if r['ferrite_kg_car']==3000 and r['battery_kwh_car']==225]
    rows=''.join(f'<tr><td>{r["scenario"]}</td><td>${r["train_usd"]:,.0f}</td><td>${r["civil_usd_dual_km"]:,.0f}</td><td>{money(r["pilot_usd"])}</td></tr>' for r in costs)
    targets=''.join(f'<tr><td>${r["magnetic_bundle_usd_train"]:,.0f}</td><td>${r["train_usd"]:,.0f}</td></tr>' for r in result['local_manufacture_cost_targets'])
    gates=''.join(f'<li>{g["id"]}: {escape(g["name"])} — OPEN</li>' for g in result['gates'])
    profile_rows=''.join(f'<tr><td>{escape(v["id"])}</td><td>{v["mass"]["tare_kg"]:,.0f} / {v["mass"]["aw3_kg"]:,.0f}</td><td>{v["matched_duty"]["hot_aw3_no_regen_cycle_kwh_per_car"]:.2f}</td><td>{v["matched_duty"]["balanced_charger_kw_per_car"]:.1f}</td><td>${v["repeat_reference_train_allowance_usd"]:,.0f}</td></tr>' for v in search['vehicle_profiles'])
    extrema=search['research_extrema']
    cost_id=escape(extrema['lowest_indexed_ordinary_allowance_candidate_id'] or 'none; no numerical pass')
    mass_id=escape(extrema['lowest_counted_concrete_mass_candidate_id'] or 'none; no numerical pass')
    requirements=''.join(f'<tr><td>{r["id"]}</td><td>{escape(r["requirement"])}</td><td>Open</td></tr>' for r in result['requirements'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenSourceRail v0.5 — primary ferrite-maglev study</title>
+<style>body{{font:17px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#172c42;background:#f9fbfd}}h1{{font-size:38px;line-height:1.15}}h2{{margin-top:36px}}.banner{{background:#e3f4f0;padding:20px;border-left:5px solid #087f78}}table{{display:block;overflow-x:auto;border-collapse:collapse;width:100%;font-size:15px}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #cad5df}}img{{width:100%;height:auto}}code{{background:#e9eef3;padding:3px;overflow-wrap:anywhere}}a{{color:#006b67}}.tag{{font-weight:700;color:#087f78}}</style>
+<p class="tag">PRIMARY DEVELOPMENT ARCHITECTURE · v{model.RELEASE_VERSION}</p><h1>Ferrite-maglev, designed for local manufacture and repair</h1>
+<div class="banner">The project now develops fixed onboard magnetic modules, passive guidebeams and Rust controls on off-the-shelf SBCs. Architecture selection is complete; engineering, manufacturing and operational acceptance remain open. Accepted physical releases: <strong>0</strong>.</div>
+<p><a href="result.json">Full source-bound calculations, requirements and systems register</a> · <a href="manifest.json">Checksums and source receipt</a></p>
+<h2>Elevated routes and whole-system simplification</h2><p>The default targets predominantly elevated mainlines (99% objective), with all ordinary sections proposed on viaducts. Straight tangents are preferred where building/air-rights, road/utility, wildlife/water, station-access and foundation evidence permit. Rings, terminal loops and necessary obstacle avoidance remain explicit. Current geography is retained; no automatic housing, road or wildlife clearance is claimed.</p>
+<p><a href="optimisation-study.json.gz">Complete bounded joint optimisation, quantities and Pareto observations</a>: {search['candidate_count']} civil/vehicle combinations, {search['numerical_screen_pass_count']} passing gross stiffness/bare-lift screens, {len(search['pareto_candidate_ids'])} Pareto observations. Lowest indexed ordinary twin-direction viaduct allowance: {best_text}/route-km; reference planning allowance ${search['reference_ordinary_viaduct_usd_dual_km']:,.0f}. These unquoted targets omit project scope and have zero acceptance-eligible candidates.</p>
+<p>The search varies sections, span/support count, transport/handling and vehicle mass allocations together. Passenger capacity, battery storage, ferrite, emergency equipment and reserve are retained. Required doors, HVAC, sensing, cooling and protection remain. Scope without justified savings retains an allowance floor of ${search['unchanged_scope_floor_usd_dual_km']:,.0f}/route-km. Actual imported content, whole installed mass and lifecycle costs remain unknown. These analytical alternatives are separate configurations from the retained CAD and coupled replay.</p>
+<h2>Adaptive mechanical, civil and Rust-control search</h2><p><a href="../iterative/README.md">Generation history and scope</a> · <a href="../iterative/recommendation.json">Confirmed research recommendation</a> · <a href="../iterative/result.json.gz">Full variants, ancestry, traces and holdout evidence</a> · <a href="../iterative/progress.svg">Progress chart</a>. Exact candidate <code>{adaptive_id}</code> is preferred within the evaluated research bounds and explicit weights. Nearby proposals depend on previous measured results; failed confirmation disqualifies the revision. Body/equipment reductions are unqualified mass allocations; complete manufactured geometry, field maps and whole-train acceptance remain open. The research recommendation does not automatically replace city or native reference configurations.</p>
+<h2>Whole-system comparison scorecards</h2><p>Lowest indexed ordinary-viaduct allowance: <code>{cost_id}</code>. Lowest counted concrete mass: <code>{mass_id}</code>. Fastest maglev construction: <strong>unknown</strong>; no qualified factory/erection schedule is present. These observations exclude held no-walkway cases and do not establish complete installed price, mass or delivery time.</p>
+<table><tr><th>Vehicle profile</th><th>Tare / AW3 kg per car</th><th>Hot no-regen kWh/car-cycle</th><th>Balanced charger kW/car</th><th>Indexed reference-formation allowance</th></tr>{profile_rows}</table>
+<p>All profiles use matched passenger/storage allocations and the same straight, level 1 km / 80 km/h-request cycle with fixed assumed drag, hotel demand and efficiencies. Actual magnetic force/loss maps and route acceptance are absent. Complete installed/factory-gate costs, shipment mass, factory/site labour, unique/moving parts, imported value, specialist dependence and repair/recovery times remain explicit unknowns in every candidate scorecard. New chute mass is unselected; no-walkway energy/charging are held. <a href="optimisation-study.json.gz">All candidate scorecards and coupling evidence</a>.</p>
+<h2>Integrated beam and onboard evacuation target</h2><p>The target removes continuous external walkway cassettes from the ordinary running guideway. The current attraction-maglev still needs iron reaction faces, supports/foundations, joints and qualified mounts. The optional walkway kit supplies an evacuation fallback; its removal is <strong>not approved</strong>.</p>
+<p><a href="evacuation-study.json.gz">Onboard evacuation study and required evidence</a> · <a href="../beam-only/model.FCStd">Beam-only native CAD</a> · <a href="../beam-only/model.step.gz">Compressed STEP</a> · <a href="../beam-only/manifest.json">Native receipt</a>. The beam-only variant removes 20 walkway parts / 14,940 kg from the modelled 25 m bay. Supports and foundations are retained. This is gross deleted scope; new onboard mass, inspection/repacking, rescue/access and lifetime cost remain unknown.</p>
+<img src="../beam-only/overview.png" alt="Native beam-only candidate without continuous walkway, with necessary iron faces and supports retained"><img src="evacuation-envelope.svg" alt="Geometric comparison of an inclined slide and hypothetical vertical spiral chute">
+<p>Enclosed vertical controlled-descent chutes (spiral/cell variants) are the preferred unqualified research candidate; inclined slides remain a comparator. Chute envelopes at 8/12/20/30 m are illustrative, with diameter, stand-off and lateral sway assumed, not supplier limits. Building and marine supplier claims are recorded separately; their height ratings and throughput do not establish rail acceptance. Axel Thoms explicitly lists monorail/gondola applications and mobile zippered outlets at different heights. These are manufacturer design leads; no named transport installation or unattended train configuration has been verified here. A discrete-outlet example fails at an intermediate 10 m ground height. Seven open installation requirements cover cassette, descent, height, structural entry, ground exit, lifecycle and driverless assistance. Variable-height deployment, bottom stabilisation, blockage rescue and mounting loads remain open. No device is a universal sole escape route. At the illustrative 8 m height / 30° slope, slide length is 16 m and horizontal run is 13.86 m before landing clearance. Live roads, roofs, water and obstructed land reject that path. An inward-facing straight slide also intersects the adjacent beam in the retained geometry; equipped doors are not automatically usable exits. Accessible evacuation, fire, weather, partial exit failure, support power, responder access and safe landing at every stop position remain mandatory evidence. Aircraft or marine equipment approval does not establish railway approval.</p>
+<p>Another {search['beam_only_candidate_count']} no-walkway cases are retained for research; none enters reference champion/city-price selection. Extra evacuation equipment mass and lifetime cost are unknown, so gross civil avoidance is not counted as net system savings. For a non-fire breakdown with a tenable train, recovery to a station or qualified rescue transfer is the initial strategy.</p>
+<h2>Linked mechanical, civil and software development</h2>
+<p>A 20-part doorway-frame, empty cassette shell and extended-entry concept now has native CAD and material quantities. Four stand-offs retain hardware mass/clearance tradeoffs. The 2 m example contains about 221 kg of modelled hardware before fabric, deployment mechanism, locks, attachment bolts or complete guards. It is not a selected or travel-stowable module.</p>
+<p><a href="../system-development/entry/model.FCStd">Entry FreeCAD</a> · <a href="../system-development/entry/model.step.gz">Entry STEP</a> · <a href="../system-development/entry-material-list.csv">Partial material list and dimensions</a> · <a href="../system-development/compact-support/model.FCStd">Compact support FreeCAD</a> · <a href="../system-development/study.json.gz">576 support-demand cases and entry variants</a> · <a href="../system-development/support-demands.csv">Demand CSV</a> · <a href="../system-development/software-replay.json">Actual Rust egress replays</a> · <a href="../system-development/native-derived-coupling.json">Native-derived beam/control replay</a> · <a href="../system-development/manifest.json">Source and execution receipt</a>.</p>
+<img src="../system-development/entry/overview.png" alt="Native doorway frame, empty cassette shell and extended entrance concept"><img src="../system-development/compact-support/overview.png" alt="Native reduced column and foundation-envelope research alternative with a narrower cap">
+<p><a href="../system-development/entry/assembly-visibility.mp4">Entry assembly visibility</a> · <a href="../system-development/compact-support/assembly-visibility.mp4">Support assembly visibility</a>. These show final-position parts, not deployment or erection motion.</p>
+<p>Column/foundation alternatives propagate gravity, self-weight and transverse eccentricity through both-train, one-train and one-beam erection cases. Negative linear footing pressure identifies an inadmissible full-contact assumption. Ground, lateral loads, capacity and stability remain open; no smaller foundation or erection-day saving is approved.</p>
+<p>The offline Rust egress state machine uses source-bound entry identity and calculated hypothetical clearance/height gates. Inward clashes, a missing 10 m outlet and road landing prevent a study deployment sequence. Readiness/security/assistance inputs remain synthetic. An egress stop can inhibit traction while the existing controller maintains valid support. No door, inflation or support actuation is enabled.</p>
+<p>A separate actual two-way Rust/beam replay now uses line mass recovered from native CAD volumes (about 1,950 kg/m), with the analytical reference section inertia. This stationary-car example adds the partial entry hardware for six hypothetical door units per car to the 27,750 kg baseline, retaining assumed inertias. Full chute mass, deployment, moving trains and actual magnetic force/loss maps remain absent. It does not validate the doorway design or the support alternatives.</p>
+<h2>Baghdad six-car reference assembly</h2><p>Six 17 m bodies (102 m total), assumed coupling and berthing allowances, a split island platform, a centred flush lift floor and the 2.96 m magnetic-arm envelope now share one revision. Native frames remain partial; the passenger gap requires a qualified bridge plate. Station quantities are unpriced. Pier-height families and emergency-energy studies keep missing loads and deployment power open.</p>
+<p><a href="../baghdad-reference/station/model.FCStd">Station FreeCAD</a> · <a href="../baghdad-reference/station/model.step.gz">Station STEP</a> · <a href="../baghdad-reference/station/assembly-visibility.mp4">Station visibility video</a> · <a href="../baghdad-reference/study.json">Quantities, pier heights and emergency energy</a> · <a href="../baghdad-reference/requirements.json">Versioned applicability register</a></p><img src="../baghdad-reference/station/overview.png" alt="Native six-car Baghdad partial floor frames, two guidebeams and centred island lift">
+<h2>Costed development scenarios</h2><p>Current six-car reference formation with matched per-car storage and ferrite allocations. USD quantity-and-process planning allowances; supplier quotes and feasibility remain open. Train, ordinary guideway and first pilot are separate scopes.</p>
+<table><tr><th>Scenario</th><th>Repeat train</th><th>Dual-route-km guideway</th><th>First pilot programme</th></tr>{rows}</table>
+<h2>Local-manufacture optimisation targets</h2><p>Only the magnetic hardware bundle changes here; every other base allowance is retained. These are budget targets, not achieved prices. Imported input costs and origins remain necessary to calculate localisation.</p>
+<table><tr><th>Bundle/train target</th><th>Repeat train</th></tr>{targets}</table><p>Local value-added percentage: <strong>unknown</strong>. Local assembly does not change imported material origin.</p>
+<h2>Guidebeam and duty calculations</h2><img src="guidebeam-sections.svg" alt="Concrete section comparison at equal scale"><img src="duty-energy.svg" alt="Calculated charging needs with regeneration available and unavailable">
+<p>Calculated hot 5% grade steady-speed ceiling under the stated 600 kW cap: {result['hot_5percent_grade_steady_speed_kmh']:.1f} km/h. Actual force/loss maps and route validation are open.</p>
+<h2>Current systems register</h2><p>{result['transition_inventory']['total_source_items']} controlled system items are allocated to {len(result['work_packages'])} work packages and {len(result['requirements'])} requirements. Allocation defines work; accepted engineering items remain zero. <a href="systems-register.json.gz">Systems register, production obligations, gate plans and supplier requests</a>.</p>
+<h2>Native geometry and actual exported views</h2><p>The provisional interface contains {result['geometric_interface']['parts']} material solids, 24 cartridges and 4,560 stock block records. This partial model excludes cabin equipment, functional propulsion and capture details. The twin 25 m civil kit has unqualified foundation envelopes. CAD reopening and selected-role interferences are checked separately from strength, motion and production acceptance.</p>
+<p><a href="../native/interface/model.FCStd">Interface FreeCAD</a> · <a href="../native/interface/model.step.gz">Compressed STEP</a> · <a href="../native/civil-bay/model.FCStd">Civil FreeCAD</a> · <a href="../native/civil-bay/model.step.gz">Civil STEP</a> · <a href="../native/interface/native-cad.json">Native receipt</a></p>
+<img src="../native/interface/overview.png" alt="Actual native interface material-region geometry"><img src="../native/interface/cartridge-detail.png" alt="Recessed retainer cartridge with stock ferrite regions and unqualified fasteners"><img src="../native/civil-bay/overview.png" alt="Twin beam civil bay with unqualified support and foundation envelopes">
+<p><a href="../native/interface/assembly-visibility.mp4">Interface assembly visibility video</a> · <a href="../native/civil-bay/assembly-visibility.mp4">Civil assembly visibility video</a>. Final-position visibility illustrations; no motion trajectory, crane or installation safety simulation.</p>
+<h2>Field equations and materials</h2><img src="field-study.png" alt="Calculated two-dimensional magnetic coupon flux field"><p><a href="field-study.json.gz">Full grids, nonlinear iterations, residuals and sensitivities</a>. The independent sine-solution refinement control passes. Coupon force mesh refinement does <strong>not</strong> converge; no lift-capacity credit is allowed. Material laws are explicit hypotheses, with no supplier grade adopted.</p>
+<h2>Rust / SBC and two-way coupled development</h2><p><code>cargo run -p osr-maglev-control --example multimodule_replay</code> exercises 24 support modules and five controlled rigid-body modes, with faults and support-preserving stop. Longitudinal propulsion is unactuated. <code>./osr design coupled</code> runs actual Rust forces into a flexible beam and returns local deflections to the controller. This virtual study excludes torsion, moving trains, actual electromagnetic maps, contact and hardware timing. <a href="../coupled/result.json">Retained coupled results</a> · <a href="../coupled/receipt.json">Execution receipt</a>. Physical I/O, measured plant gains and target timing remain open.</p>
+<h2>City defaults</h2><p><a href="../../../../engineering/ferrite_maglev/city-index.md">All 266 primary maglev city packages</a> recompute formation, duty, fleet, charging and partial costs. <code>./osr city baghdad</code> and <code>./osr sim baghdad</code> use the new compiler and charging replay. Terminal loops are unlocated assumptions, and project totals remain unknown.</p>
+<h2>Acceptance gates</h2><ul>{gates}</ul><h2>Design status</h2><p>City fleet/charging planning, partial native CAD, a nonlinear 2D coupon and 24-module flexible-beam co-simulation now execute. Complete vehicle/civil detail, measured field maps, hardware I/O and physical qualification remain open.</p>
+<details><summary>{len(result['requirements'])} traced specification requirements — all acceptance remains open</summary><table>{requirements}</table></details></html>'''.replace('\n+','\n').encode()


def payload():
    before=model.sources();result=model.build()
    result['source_sha256']=before
    result['runtime']=runtime()
    result['retained_evidence']=external_evidence()
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


def external_evidence():
    from . import coupled,cities
    iteration.verify()
    base=model.ROOT/'docs/design-engine/ferrite-maglev'
    geometry.verify_native(base/'native');coupled.verify(base/'coupled');evacuation.verify_native(base/'beam-only')
    system_development.verify(base/'system-development')
    reference_assembly.verify(base/'baghdad-reference')
    catalogue=cities.verify_index()
    if not catalogue['current']:raise ValueError('city catalogue inputs/outputs changed: '+str(catalogue['errors'][:3]))
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in (base/'native/manifest.json',base/'coupled/receipt.json',base/'beam-only/manifest.json',base/'system-development/manifest.json',base/'baghdad-reference/manifest.json',base/'iterative/manifest.json')}


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
    if r.get('retained_evidence')!=external_evidence():raise ValueError('retained native/coupled evidence differs')
    return m
