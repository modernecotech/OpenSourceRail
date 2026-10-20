"""Bounded, source-bound publication for the v0.5 primary study."""
from hashlib import sha256
from html import escape
import json
import gzip
import os
from pathlib import Path
import platform
import tempfile

from . import model,transition,geometry,field,media,optimisation,evacuation

OUTPUT = model.ROOT / 'docs/design-engine/ferrite-maglev/reference'
EXPECTED={'result.json','index.html','guidebeam-sections.svg','duty-energy.svg','transition-register.json.gz','interface-definition.json.gz','civil-bay-definition.json.gz','field-study.json.gz','field-study.png','optimisation-study.json.gz','evacuation-study.json.gz','evacuation-envelope.svg'}


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def section_svg(result):
    b=result['inputs']['civil']['narrow_box_screen'];w=b['outer_width_m'];h=b['outer_depth_m'];tw=b['web_thickness_m'];tf=b['flange_thickness_m']
    scale=180;x=685;y=105
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="510" viewBox="0 0 1000 510" role="img" aria-label="Dimensioned concrete section comparison">
+<rect width="1000" height="510" fill="#f1f5f9"/><g font-family="sans-serif" fill="#14283d">
+<text x="25" y="36" font-size="23">v0.5 guidebeam section study — concrete envelopes only</text>
+<text x="25" y="64" font-size="15">Equal scale. No rail faces, reinforcement, prestress, brackets or acceptance inferred.</text>
+<path d="M35 105 h522 v39.6 h-104.85 v168.3 h-54 v-168.3 h-204.3 v168.3 h-54 v-168.3 h-104.85 Z" fill="#7d93a8"/>
+<text x="35" y="352" font-size="18">Retained wheel/rail comparator: 2.9 × 1.155 m</text>
+<text x="35" y="381" font-size="17">A = 1.199 m²; vertical I ≈ 0.1430 m⁴</text>
+<rect x="{x}" y="{y}" width="{w*scale}" height="{h*scale}" fill="#087f78"/>
+<rect x="{x+tw*scale}" y="{y+tf*scale}" width="{(w-2*tw)*scale}" height="{(h-2*tf)*scale}" fill="#f1f5f9"/>
+<text x="645" y="423" font-size="18">Primary box: {w} × {h} m</text>
+<text x="645" y="451" font-size="16">A = 0.660 m²; vertical I = 0.193624 m⁴</text>
+<text x="25" y="490" font-size="16">27 section/span combinations screened. Lateral/torsional, coupled-gap and strength acceptance: open.</text>
+</g></svg>'''.replace('\n+','\n').encode()


def energy_svg(result):
    rows=result['adverse_energy_cases'];maxkw=700
    bars=[]
    for i,r in enumerate(rows):
        y=110+95*i;label=f"Hot {r['requested_speed_kmh']} km/h; regen {'available' if r['regeneration_available'] else 'unavailable'}"
        bars.append(f'<text x="25" y="{y}" font-size="16">{label}</text><rect x="370" y="{y-22}" width="{r["balanced_charger_kw"]/maxkw*530}" height="33" fill="#087f78"/><text x="{380+r["balanced_charger_kw"]/maxkw*530}" y="{y+1}" font-size="16">{r["balanced_charger_kw"]:.1f} kW</text>')
    return ('''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="450" viewBox="0 0 1100 450" role="img" aria-label="Adverse cycle balanced charging requirements"><rect width="1100" height="450" fill="#f1f5f9"/><g fill="#14283d" font-family="sans-serif"><text x="25" y="36" font-size="23">Calculated charging duty per car — assumed level 1 km cycle</text><text x="25" y="67" font-size="15">Heaviest target AW3; 60 s dwell / 45 s effective charge; excludes additional conversion losses.</text>'''+''.join(bars)+f'<line x1="{370+600/maxkw*530}" x2="{370+600/maxkw*530}" y1="80" y2="345" stroke="#a72a34" stroke-width="3"/><text x="25" y="405" font-size="17">Red line: 600 kW charger candidate. These calculations do not validate motor efficiency or route operation.</text></g></svg>').encode()


def render(result):
    search=result['whole_system_optimisation'];best=search['minimum_indexed_allowance_candidate']
    best_text=f"${best['civil']['indexed_allowance_usd_dual_km']:,.0f}" if best else 'none; no candidate passes the numerical screens'
    costs=[r for r in result['cost_cases'] if r['ferrite_kg_car']==3000 and r['battery_kwh_car']==225]
    rows=''.join(f'<tr><td>{r["scenario"]}</td><td>${r["train_usd"]:,.0f}</td><td>${r["civil_usd_dual_km"]:,.0f}</td><td>${r["pilot_usd"]:,.0f}</td></tr>' for r in costs)
    targets=''.join(f'<tr><td>${r["magnetic_bundle_usd_train"]:,.0f}</td><td>${r["train_usd"]:,.0f}</td><td>{100*r["train_saving_fraction"]:.2f}%</td></tr>' for r in result['local_manufacture_cost_targets'])
    gates=''.join(f'<li>{g["id"]}: {escape(g["name"])} — OPEN</li>' for g in result['gates'])
    requirements=''.join(f'<tr><td>{r["id"]}</td><td>{escape(r["requirement"])}</td><td>Open</td></tr>' for r in result['requirements'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenSourceRail v0.5 — primary ferrite-maglev study</title>
+<style>body{{font:17px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#172c42;background:#f9fbfd}}h1{{font-size:38px;line-height:1.15}}h2{{margin-top:36px}}.banner{{background:#e3f4f0;padding:20px;border-left:5px solid #087f78}}table{{display:block;overflow-x:auto;border-collapse:collapse;width:100%;font-size:15px}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #cad5df}}img{{width:100%;height:auto}}code{{background:#e9eef3;padding:3px}}a{{color:#006b67}}.tag{{font-weight:700;color:#087f78}}</style>
+<p class="tag">PRIMARY DEVELOPMENT ARCHITECTURE · v0.5.0</p><h1>Ferrite-maglev, designed for local manufacture and repair</h1>
+<div class="banner">The project now develops fixed onboard magnetic modules, passive guidebeams and Rust controls on off-the-shelf SBCs. Architecture selection is complete; engineering, manufacturing and operational acceptance remain open. Accepted physical releases: <strong>0</strong>.</div>
+<p><a href="result.json">Full source-bound calculations, requirements and migration register</a> · <a href="manifest.json">Checksums and source receipt</a> · <a href="../../../../OpenSourceRail_Ferrite_Maglev_Rework_Specification.md">Supplied specification A</a></p>
+<h2>Elevated routes and whole-system simplification</h2><p>The default targets predominantly elevated mainlines (99% objective), with all ordinary sections proposed on viaducts. Straight tangents are preferred where building/air-rights, road/utility, wildlife/water, station-access and foundation evidence permit. Rings, terminal loops and necessary obstacle avoidance remain explicit. Current geography is retained; no automatic housing, road or wildlife clearance is claimed.</p>
+<p><a href="optimisation-study.json.gz">Complete bounded joint optimisation, quantities and Pareto observations</a>: {search['candidate_count']} civil/vehicle combinations, {search['numerical_screen_pass_count']} passing gross stiffness/bare-lift screens, {len(search['pareto_candidate_ids'])} Pareto observations. Lowest indexed ordinary twin-direction viaduct allowance: {best_text}/route-km; supplied base ${search['reference_ordinary_viaduct_usd_dual_km']:,.0f}. These unquoted targets omit project scope and have zero acceptance-eligible candidates.</p>
+<p>The search varies sections, span/support count, transport/handling and vehicle mass allocations together. Passenger capacity, battery storage, ferrite, emergency equipment and reserve are retained. Required doors, HVAC, sensing, cooling and protection remain. Scope without justified savings retains an allowance floor of ${search['unchanged_scope_floor_usd_dual_km']:,.0f}/route-km. Actual imported content, whole installed mass and lifecycle costs remain unknown. These analytical alternatives are separate configurations from the retained CAD and coupled replay.</p>
+<h2>Integrated beam and onboard evacuation target</h2><p>The target removes continuous external walkway cassettes from the ordinary running guideway. The current attraction-maglev still needs iron reaction faces, supports/foundations, joints and qualified mounts. The retained walkway kit is a comparator; its removal is <strong>not approved</strong>.</p>
+<p><a href="evacuation-study.json.gz">Onboard evacuation study and required evidence</a> · <a href="../beam-only/model.FCStd">Beam-only native CAD</a> · <a href="../beam-only/model.step.gz">Compressed STEP</a> · <a href="../beam-only/manifest.json">Native receipt</a>. The beam-only variant removes 20 walkway parts / 14,940 kg from the modelled 25 m bay. Supports and foundations are retained. This is gross deleted scope; new onboard mass, inspection/repacking, rescue/access and lifetime cost remain unknown.</p>
+<img src="../beam-only/overview.png" alt="Native beam-only candidate without continuous walkway, with necessary iron faces and supports retained"><img src="evacuation-envelope.svg" alt="Geometric comparison of an inclined slide and hypothetical vertical spiral chute">
+<p>Enclosed vertical controlled-descent chutes (spiral/cell variants) are the preferred unqualified research candidate; inclined slides remain a comparator. Chute envelopes at 8/12/20/30 m are illustrative, with diameter, stand-off and lateral sway assumed, not supplier limits. Building and marine supplier claims are recorded separately; their height ratings and throughput do not establish rail acceptance. Variable-height deployment, bottom stabilisation, blockage rescue and mounting loads remain open. No device is a universal sole escape route. At the illustrative 8 m height / 30° slope, slide length is 16 m and horizontal run is 13.86 m before landing clearance. Live roads, roofs, water and obstructed land reject that path. An inward-facing straight slide also intersects the adjacent beam in the retained geometry; equipped doors are not automatically usable exits. Accessible evacuation, fire, weather, partial exit failure, support power, responder access and safe landing at every stop position remain mandatory evidence. Aircraft or marine equipment approval does not establish railway approval.</p>
+<p>Another {search['beam_only_candidate_count']} no-walkway cases are retained for research; none enters reference champion/city-price selection. Extra evacuation equipment mass and lifetime cost are unknown, so gross civil avoidance is not counted as net system savings. For a non-fire breakdown with a tenable train, recovery to a station or qualified rescue transfer is the initial strategy.</p>
+<h2>Costed development scenarios</h2><p>Matched three-car / 675 kWh / 3 t ferrite per car. USD planning allowances; supplier quotes and feasibility remain open. Train, ordinary guideway and first pilot are separate scopes.</p>
+<table><tr><th>Scenario</th><th>Repeat train</th><th>Dual-route-km guideway</th><th>First pilot programme</th></tr>{rows}</table>
+<h2>Local-manufacture optimisation targets</h2><p>Only the magnetic hardware bundle changes here; every other base allowance is retained. These are budget targets, not achieved prices. Imported input costs and origins remain necessary to calculate localisation.</p>
+<table><tr><th>Bundle/train target</th><th>Repeat train</th><th>Saving against comparator</th></tr>{targets}</table><p>Local value-added percentage: <strong>unknown</strong>. Local assembly does not change imported material origin.</p>
+<h2>Guidebeam and duty calculations</h2><img src="guidebeam-sections.svg" alt="Concrete section comparison at equal scale"><img src="duty-energy.svg" alt="Calculated charging needs with regeneration available and unavailable">
+<p>Calculated hot 5% grade steady-speed ceiling under the stated 600 kW cap: {result['hot_5percent_grade_steady_speed_kmh']:.1f} km/h. Actual force/loss maps and route validation are open.</p>
+<h2>Whole-inventory transition</h2><p>{result['transition_inventory']['total_source_items']} authoritative items and 63 legacy packages have explicit dispositions, linked to 72 ferrite requirements and 11 new work packages. This completes migration coverage; accepted engineering items remain zero. <a href="transition-register.json.gz">Complete transition register, production obligations, gate plans and supplier requests</a>.</p>
+<h2>Native geometry and actual exported views</h2><p>The provisional interface contains {result['geometric_interface']['parts']} material solids, 24 cartridges and 4,560 stock block records. This partial model excludes cabin equipment, functional propulsion and capture details. The twin 25 m civil kit has unqualified foundation envelopes. CAD reopening and selected-role interferences are checked separately from strength, motion and production acceptance.</p>
+<p><a href="../native/interface/model.FCStd">Interface FreeCAD</a> · <a href="../native/interface/model.step.gz">Compressed STEP</a> · <a href="../native/civil-bay/model.FCStd">Civil FreeCAD</a> · <a href="../native/civil-bay/model.step.gz">Civil STEP</a> · <a href="../native/interface/native-cad.json">Native receipt</a></p>
+<img src="../native/interface/overview.png" alt="Actual native interface material-region geometry"><img src="../native/interface/cartridge-detail.png" alt="Recessed retainer cartridge with stock ferrite regions and unqualified fasteners"><img src="../native/civil-bay/overview.png" alt="Twin beam civil bay with unqualified support and foundation envelopes">
+<p><a href="../native/interface/assembly-visibility.mp4">Interface assembly visibility video</a> · <a href="../native/civil-bay/assembly-visibility.mp4">Civil assembly visibility video</a>. Final-position visibility illustrations; no motion trajectory, crane or installation safety simulation.</p>
+<h2>Field equations and materials</h2><img src="field-study.png" alt="Calculated two-dimensional magnetic coupon flux field"><p><a href="field-study.json.gz">Full grids, nonlinear iterations, residuals and sensitivities</a>. The independent sine-solution refinement control passes. Coupon force mesh refinement does <strong>not</strong> converge; no lift-capacity credit is allowed. Material laws are explicit hypotheses, with no supplier grade adopted.</p>
+<h2>Rust / SBC and two-way coupled development</h2><p><code>cargo run -p osr-maglev-control --example multimodule_replay</code> exercises 24 support modules and five controlled rigid-body modes, with faults and support-preserving stop. Longitudinal propulsion is unactuated. <code>./osr design coupled</code> runs actual Rust forces into a flexible beam and returns local deflections to the controller. This virtual study excludes torsion, moving trains, actual electromagnetic maps, contact and hardware timing. <a href="../coupled/result.json">Retained coupled results</a> · <a href="../coupled/receipt.json">Execution receipt</a>. Physical I/O, measured plant gains and target timing remain open.</p>
+<h2>City defaults</h2><p><a href="../../../../engineering/ferrite_maglev/city-index.md">All 266 primary maglev city packages</a> recompute formation, duty, fleet, charging and partial costs. <code>./osr city baghdad</code> and <code>./osr sim baghdad</code> use the new compiler and charging replay. Terminal loops are unlocated assumptions, and project totals remain unknown.</p>
+<h2>Acceptance gates</h2><ul>{gates}</ul><h2>Migration status</h2><p>Wheel/rail sources and existing city packages are retained as v0.4 comparators. City fleet/charging planning, partial native CAD, a nonlinear 2D coupon and 24-module flexible-beam co-simulation now execute. Complete vehicle/civil detail, measured field maps, hardware I/O and physical qualification remain open. Legacy tests are not transferred to this family.</p>
+<details><summary>{len(result['requirements'])} traced specification requirements — all acceptance remains open</summary><table>{requirements}</table></details></html>'''.replace('\n+','\n').encode()


def payload():
    before=model.sources();result=model.build()
    result['source_sha256']=before
    result['runtime']=runtime()
    result['retained_evidence']=external_evidence()
    numerical=field.study()
    files={'result.json':encoded(result),'index.html':render(result),
            'guidebeam-sections.svg':section_svg(result),'duty-energy.svg':energy_svg(result),
            'transition-register.json.gz':gzip.compress(encoded(transition.build()),mtime=0),
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
    base=model.ROOT/'docs/design-engine/ferrite-maglev'
    geometry.verify_native(base/'native');coupled.verify(base/'coupled');evacuation.verify_native(base/'beam-only')
    catalogue=cities.verify_index()
    if not catalogue['current']:raise ValueError('city catalogue inputs/outputs changed: '+str(catalogue['errors'][:3]))
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in (base/'native/manifest.json',base/'coupled/receipt.json',base/'beam-only/manifest.json')}


def publish(output=OUTPUT, *, check=False):
    output=Path(output).resolve();files=payload()
    manifest=dict(schema='osr-primary-infrastructure-publication/1',version='0.5.0',family='ferrite-pm-maglev-study',
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
    if set(m['files_sha256'])!=expected:raise ValueError('exact bounded publication inventory required')
    for name,digest in m['files_sha256'].items():
        if (output/name).is_symlink() or sha256((output/name).read_bytes()).hexdigest()!=digest:raise ValueError('publication file differs: '+name)
    r=json.loads((output/'result.json').read_text())
    if r['source_sha256']!=m['source_sha256'] or r['family']!=m['family']:raise ValueError('result identity differs')
    if any(o.get(k) is not False for o in (m,r) for k in model.FLAGS):raise ValueError('study asserted a release')
    if r.get('retained_evidence')!=external_evidence():raise ValueError('retained native/coupled evidence differs')
    return m
