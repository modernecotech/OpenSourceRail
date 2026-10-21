"""Bounded, source-bound publication for the v0.5 primary study."""
from hashlib import sha256
from html import escape
import json
import gzip
import os
from pathlib import Path
import platform
import tempfile

from . import model,transition,geometry,field,media,optimisation,evacuation,system_development,reference_assembly,iteration,station,station_structure,station_protocol,station_native

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
    from . import station_structure
    st=result['station_powered'];tr=st['trajectory'];charge=st['charging'];traffic=st['traffic'];struct=result['station_structure']
    adaptive=json.loads((iteration.OUTPUT/'recommendation.json').read_text())
    selected=escape(adaptive['candidate_id'] or 'none; mandatory confirmation held')
    cost_rows=''.join(f'<tr><td>{r["scenario"]}</td><td>{money(r["train_usd"])}</td><td>{money(r["civil_usd_dual_km"])}</td></tr>' for r in result['cost_cases'] if r['ferrite_kg_car']==3000 and r['battery_kwh_car']==30)
    requirement_rows=''.join(f'<tr><td>{r["id"]}</td><td>{escape(r["requirement"])}</td><td>Open</td></tr>' for r in result['applicable_requirements']['requirements'])
    gate_rows=''.join(f'<li>{g["id"]}: {escape(g["name"])} — OPEN</li>' for g in result['gates'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenSourceRail {model.RELEASE_VERSION} — station-powered ferrite-maglev development</title>
<style>body{{font:17px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#172c42;background:#f9fbfd}}h1{{font-size:36px;line-height:1.15}}h2{{margin-top:36px}}.banner{{background:#e3f4f0;padding:20px;border-left:5px solid #087f78}}table{{display:block;overflow-x:auto;border-collapse:collapse;width:100%;font-size:15px}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #cad5df}}img{{width:100%;height:auto}}code{{background:#e9eef3;padding:3px;overflow-wrap:anywhere}}a{{color:#006b67}}</style>
<p>PRIMARY DEVELOPMENT · v{model.RELEASE_VERSION}</p><h1>Ferrite-maglev, powered from station zones</h1>
<div class="banner">Six 17 m GFRP body studies, onboard ferrite PM-biased active support/guidance, station LSM launch/receiving braking and propulsion-unpowered interstation coasting. Accepted engineering and physical releases: <strong>0</strong>. The published v0.5.1 configuration is retained as an identified comparison.</div>
<p><a href="result.json">Current configuration, calculations and requirements</a> · <a href="manifest.json">Sources and payload receipt</a> · <a href="systems-register.json.gz">Systems responsibility register</a></p>
<h2>Station launch, coast, arrival and charging</h2>
<p>The flat 1 km, 90 s reference uses a 157.2 t loaded six-car train, assumed drag, 0.8 m/s² acceleration/deceleration and 0.6 m/s³ jerk. Its {tr['peak_traction_input_kw']/1000:.3f} MW peak traction input and {tr['launch_input_kwh']:.3f} kWh launch input use assumed 85% conversion. Coasting has zero commanded propulsion. Magnetic force/current/voltage/thermal maps and six-car phase registration remain open.</p>
<p><a href="../station-powered/README.md">Study scope</a> · <a href="../station-powered/result.json.gz">Trajectories, overlap, gradients, power and procurement targets</a> · <a href="../station-powered/manifest.json">Execution/source receipt</a></p>
<img src="../station-powered/overview.svg" alt="Executed jerk-limited station launch coast and arrival histories"><img src="../station-powered/power.svg" alt="Calculated station traction and services power histories">
<p>At 45 s connected charging in 60 s dwell, the services battery supplies the 90 s run plus 15 s disconnected dwell. Replacing {charge['replacement_kwh_per_train']:.2f} kWh/train requires {charge['connected_interface_kw_per_train']/1000:.2f} MW including direct connected services, before losses; pack charging is {charge['battery_charge_c_rate']:.2f}C. The 30 kWh/car pack retains EOL/SOC/reserve sensitivities rather than a qualified battery selection. Station resistor braking must remain available without another energy consumer.</p>
<p>Protected-zone planning minimum is {traffic['planning_minimum_headway_s']:.2f} s; the 190 s reference gives {traffic['normal_passengers_per_hour_direction']:,.0f} normal passengers/hour/direction. City schedules use their actual leg/dwell bounds; source three-minute figures are not silently retained. Grade/speed/overlap failures, stalled-train recovery and receiver failure after launch remain explicit holds. A station cannot restart a distant stationary train without a recovery method.</p>
<h2>GFRP body and complete civil-product study</h2>
<p>The central 14.2 t/car tare budget includes a 5.2 t equipped body, 3 t ferrite and 1.8 t growth reserve. Four doors/car, rather than six, are used consistently in the configuration, panel takeoff, platform interfaces and evacuation count. Laminate/core properties, distributed hardpoints, joints, fire, crash, fatigue and complete measured mass/CG/inertia remain unqualified.</p>
<p><a href="../station-structure/result.json">Body takeoffs, core substitutions, beam/support families and production bottlenecks</a> · <a href="../station-structure/manifest.json">Reproducibility receipt</a> · <a href="../station-native/model.FCStd">GFRP/civil FreeCAD</a> · <a href="../station-native/model.step.gz">Compressed STEP</a> · <a href="../station-native/native-cad.json">Actual native reopening/solid checks</a></p>
<img src="../station-structure/comparison.svg" alt="Quantity based GFRP and civil product comparisons"><img src="../station-native/overview.png" alt="Actual partial GFRP panel stock and hollow-column civil product material geometry">
<p><a href="../station-native/assembly-visibility.mp4">GFRP/civil assembly visibility video</a>. Developed panel stock and material-region assemblies omit unsized detail; final-position visibility is not motion, collision, deployment or lifting simulation.</p>
<p>The 25 m balanced box uses 0.80 × 1.80 m outer dimensions, 100 mm webs, 150 mm flanges and explicit end infills. Hollow 1.35/0.95 m columns and 5.4 m³ caps replace placeholder solids. Shallow, shaft and pile-group foundations remain conditional on ground and loads. Thin walls need actual cover/strand/shear/connection and manufacturing detail; native geometry does not prove strength or magnetic-gap motion.</p>
<p>The document's rounded no-walkway priced-scope target is about $3.313 million/two-direction route-km. Actual native end-infill quantities are priced separately from rounded budgets. Most proposed savings come from support and production procurement targets, including $22,000/support. The 56.25 route-m/planned-workday bottleneck is an unmeasured two-shift production objective, with cure, connection, lift and survey acceptance holds. Station electrical equipment is additional. Walkway deletion remains unapproved.</p>
<h2>Finite magnets and force evidence</h2><p>Equal-volume conventional, segmented, finite-orientation and iron-backed seeds retain block identities and magnetization vectors. The reproduced Rehberg–Blümler ring controls establish an air-core analytical benchmark; no ring percentage is credited as railway lift or material saving. Native exposed pole area differs from the 12 m² ideal screen. Shared support/thrust, saturation, hot force/cold demagnetization, losses and real effective area require 3D calculation and rig correlation.</p>
<img src="field-study.png" alt="Two-dimensional magnetic coupon equation study, with unconverged force mesh"><p><a href="field-study.json.gz">Full two-dimensional grids and numerical controls</a>. Coupon force refinement is unconverged; no physical lift credit is allowed.</p>
<h2>Durable Rust station launch control</h2><p>Offline tests exercise atomic corridor/receiving-berth/overlap reservation, pre-launch expiry, post-launch commitment, receiver faults, restart, replay and complete-tail-clearance requirements. Committed ownership survives permission expiry. The local conflict domain is bounded to 32 resources and one controller; this is not a distributed citywide authority. Fresh readiness/clearance inputs are synthetic assertions, not commissioned sensors. SBC supervision, deterministic MCU loops and independent trips remain separate obligations.</p>
<p><a href="../station-protocol/replay.json">Actual Rust station control replay</a> · <a href="../station-protocol/executed-tests.txt.gz">Actual compiler/replay/protocol test commands and output</a> · <a href="../station-protocol/manifest.json">Source and execution receipt</a>. Every physical output remains disabled. Scalar motor constants are unmeasured; no hardware timing or real current map is established.</p>
<h2>Adaptive mechanical, civil and station-control search</h2><p><a href="../iterative/README.md">Generation scope</a> · <a href="../iterative/recommendation.json">Confirmed research recommendation</a> · <a href="../iterative/result.json.gz">Variants, ancestry, actual Rust/beam traces and station confirmations</a>. Exact candidate <code>{selected}</code> is preferred only within evaluated bounds and declared weights. Proposals vary body/equipment allocations, beam geometry, gains, runtime, winding length and acceleration; failed mandatory confirmation disqualifies the revision. Reference and city defaults are not automatically promoted.</p><img src="../iterative/progress.svg" alt="Observed bounded adaptive design generation progress">
<h2>Whole-system comparison scorecards</h2><p><a href="optimisation-study.json.gz">All indexed vehicle/beam comparisons</a>. Complete installed cost, total manufactured mass, supplier-origin content and accepted erection time remain unknown. Body and magnetic equipment allocations are targets; services/HVAC energy is not automatically reduced with body mass. Station traction is accounted separately from the services pack.</p>
<table><tr><th>Scenario</th><th>Repeat six-car allowance</th><th>Ordinary viaduct with fallback access</th></tr>{cost_rows}</table>
<p>These are quantity/process assumptions without supplier quotations. First-pilot, station buildings, actual electrical ratings and utility reinforcement, terminal/depot/recovery, land/air rights, development/factory capital, evacuation, EPC, tax/finance and lifecycle omissions remain open. City bills show station electrical targets as a separate priced scope; neither subtotal is a complete railway price. No proven localisation percentage is claimed.</p>
<h2>Native magnetic interface and fallback civil bay</h2><p>The partial interface retains exact cartridge/fastener material regions and hybrid floor load paths; it is not a complete equipped GFRP train. Reaction iron, bearings, connections, capture, tolerances and reinforcement remain necessary.</p>
<p><a href="../native/interface/model.FCStd">Interface FreeCAD</a> · <a href="../native/interface/model.step.gz">Interface STEP</a> · <a href="../native/civil-bay/model.FCStd">Civil FreeCAD</a> · <a href="../native/civil-bay/model.step.gz">Civil STEP</a> · <a href="../native/interface/native-cad.json">Native receipt</a></p>
<img src="../native/interface/overview.png" alt="Current partial magnetic interface and hybrid GFRP floor"><img src="../native/interface/cartridge-detail.png" alt="Ferrite cartridge retainer fastener and winding-envelope detail"><img src="../native/civil-bay/overview.png" alt="Current balanced beams hollow supports and fallback walkway material regions"><img src="guidebeam-sections.svg" alt="Current selected guidebeam section dimensions"><img src="duty-energy.svg" alt="Services battery charging sensitivity with main traction supplied at stations">
<p><a href="../native/interface/assembly-visibility.mp4">Interface visibility video</a> · <a href="../native/civil-bay/assembly-visibility.mp4">Civil visibility video</a>. All videos show final-position sequences only.</p>
<h2>Beam-only evacuation target</h2><p><a href="evacuation-study.json.gz">Full evacuation studies and outstanding evidence</a> · <a href="../beam-only/model.FCStd">Beam-only FreeCAD</a> · <a href="../beam-only/model.step.gz">Beam-only STEP</a> · <a href="../beam-only/manifest.json">Native receipt</a>. Continuous walkway removal depends on an accepted all-stop evacuation/recovery solution. The vertical spiral chute remains a candidate; fabric/deployment/assistance, ground exit, fire, wind and safe landing over roads/water/roofs are unresolved. No net system saving is released from gross deleted material.</p>
<img src="../beam-only/overview.png" alt="Beam-only research geometry with necessary iron and hollow supports"><img src="evacuation-envelope.svg" alt="Illustrative inclined and vertical controlled-descent evacuation envelopes">
<h2>Entry, supports and vertical replay</h2><p><a href="../system-development/entry/model.FCStd">Entry FreeCAD</a> · <a href="../system-development/entry/model.step.gz">Entry STEP</a> · <a href="../system-development/compact-support/model.FCStd">Support FreeCAD</a> · <a href="../system-development/study.json.gz">Entry/support sensitivity evidence</a> · <a href="../system-development/entry-material-list.csv">Partial entry materials</a> · <a href="../system-development/support-demands.csv">Support demands</a> · <a href="../system-development/software-replay.json">Advisory egress Rust replay</a> · <a href="../system-development/native-derived-coupling.json">Native-derived vertical replay</a> · <a href="../system-development/manifest.json">Source receipt</a></p>
<img src="../system-development/entry/overview.png" alt="Partial empty chute cassette and extended doorway entry"><img src="../system-development/compact-support/overview.png" alt="Hollow support quantity sensitivity with unqualified foundation">
<p><a href="../system-development/entry/assembly-visibility.mp4">Entry visibility video</a> · <a href="../system-development/compact-support/assembly-visibility.mp4">Support visibility video</a>. Support demand screens do not establish capacity. Extended entry hardware is not a selected travel-stowable chute.</p>
<p><a href="../coupled/result.json">Actual Rust/vertical-beam replay</a> · <a href="../coupled/receipt.json">Compiler and source receipt</a>. The current coupled demonstration is one stationary rigid car with three body modes and ideal instantaneous force channels. It is separate from the six-car longitudinal trajectory; a complete moving six-car/flexible-body/guideway/soil/magnetic coupled model remains open.</p>
<h2>Six-car Baghdad station and all-city planning</h2><p><a href="../baghdad-reference/station/model.FCStd">Partial station FreeCAD</a> · <a href="../baghdad-reference/station/model.step.gz">Station STEP</a> · <a href="../baghdad-reference/study.json">Station quantities and emergency-energy sensitivities</a> · <a href="../baghdad-reference/requirements.json">Current applicability register</a> · <a href="../baghdad-reference/station/assembly-visibility.mp4">Station visibility video</a></p>
<img src="../baghdad-reference/station/overview.png" alt="Six-car Baghdad partial floor frames and flush island-platform lift">
<p>Six 17 m bodies total 102 m; assumed coupling gaps give 104.5 m. Four doors/car, magnetic-arm clearances and bridge-plate requirements share the current configuration. Full station supports/stairs/services and equipment remain unqualified. <a href="../../../../engineering/ferrite_maglev/city-index.md">All 266 city packages</a> regenerate service batteries, station-resource headways, fleet and partial civil/electrical bills from mapped inputs. Coasting failures and terminal/recovery requirements remain visible rather than restoring onboard main traction.</p>
<h2>Acceptance gates</h2><ul>{gate_rows}</ul><details><summary>{len(result['applicable_requirements']['requirements'])} applicable requirements, including all 100 supplied specification items — acceptance remains open</summary><table>{requirement_rows}</table></details></html>'''.encode()

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
    iteration.verify();station.verify();station_structure.verify();station_protocol.verify();station_native.verify()
    base=model.ROOT/'docs/design-engine/ferrite-maglev'
    geometry.verify_native(base/'native');coupled.verify(base/'coupled');evacuation.verify_native(base/'beam-only')
    system_development.verify(base/'system-development')
    reference_assembly.verify(base/'baghdad-reference')
    catalogue=cities.verify_index()
    if not catalogue['current']:raise ValueError('city catalogue inputs/outputs changed: '+str(catalogue['errors'][:3]))
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in (base/'native/manifest.json',base/'coupled/receipt.json',base/'beam-only/manifest.json',base/'system-development/manifest.json',base/'baghdad-reference/manifest.json',base/'iterative/manifest.json',base/'station-powered/manifest.json',base/'station-structure/manifest.json',base/'station-protocol/manifest.json',base/'station-native/manifest.json')}


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
