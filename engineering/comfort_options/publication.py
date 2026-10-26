"""Reproducible seat-led comfort research, preserving same-magnet limitations."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

from . import ROOT, PARENT_REVISION, FLAGS
from . import layout, glazing, systems, envelope, seats_doors

OUTPUT = 'docs/design-engine/ferrite-maglev/comfort-options'
WORKBENCH = 'docs/workbench/trip/readiness/comfort'


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _bindings(root, records):
    result = {}
    for record in records:
        for name, digest in record.get('source_sha256', {}).items():
            if name in result and result[name] != digest:
                raise ValueError('mixed source revisions: '+name)
            result[name] = digest
    for path in sorted((root/'engineering/comfort_options').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix in {'.py','.html','.js','.css'}:
            result[path.relative_to(root).as_posix()] = sha256(path.read_bytes()).hexdigest()
    for name in ('.github/workflows/comfort-options.yml', 'tools/automation/tests/verify-comfort-options.mjs'):
        result[name] = sha256((root/name).read_bytes()).hexdigest()
    for name, digest in result.items():
        path = root/name
        if path.is_symlink() or sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('source changed: '+name)
    return dict(sorted(result.items()))


def assemble(root=ROOT):
    root = Path(root).resolve()
    layouts = layout.family(root=root)
    # A bench-preserving default and a separate accessible-door-bay alternative.
    bench = layout.make_layout('one-sided-2', vestibule_length_m=1.8,
                               wheelchair_location='outer-ends', root=root)
    access = layout.make_layout('one-sided-2', vestibule_length_m=1.5, wheelchair_location='best-fit', root=root)
    reference = layout.make_layout('two-sided-2plus2', vestibule_length_m=1.5, wheelchair_location='best-fit', root=root)
    extra = layout.make_layout('one-sided-3', vestibule_length_m=1.5, wheelchair_location='best-fit', root=root)
    selected = [('door-bench-default', bench), ('wheelchair-door-bay-alternative', access),
                ('two-sided-seat-led-control', reference), ('three-door-comparison', extra)]
    all_layouts = {r['layout_id']:r for r in layouts+[r for _,r in selected]}
    windows = [g for doors in (2,3,4) for g in glazing.options(doors)]
    records = []
    for role, cabin in selected:
        for window in windows:
            if window['doors_total'] != cabin['doors_total']:
                continue
            # Retain thin-PC density control and stiffness-conscious PC alternative.
            if not (window['material']=='laminated-glass' or
                    (window['sheet_thickness_m']==.006 and window['partition']=='full') or
                    (window['sheet_thickness_m']==.012 and window['partition']=='sixths')):
                continue
            for units in (2,4,5):
                evaluated = systems.evaluate(cabin, window, root=root, hvac_units=units)
                records.append(dict(recipe=role, **evaluated))
    panels = envelope.options(root=root)
    for panel in panels:
        envelope.validate(panel, root=root)
    furniture = seats_doors.options(root=root)
    for component in furniture:
        seats_doors.validate(component, root=root)
    parent = systems.parent_evidence(root)
    source = _bindings(root, list(all_layouts.values())+records+panels+furniture+[parent])
    policy = dict(purpose='next component design and comfort/service comparison',
        rule='Retain door-bench and wheelchair-door-bay alternatives; compare glass, thin-PC control and subdivided thicker PC. Keep five HVAC references by default until hot-condition ratings exist.',
        integrated_candidate_selected=False, primary_recipe='door-bench-default',
        primary_HVAC_quantity=5, primary_glazing='retained glass reference; PC remains an unqualified alternative',
        capacity_is_derived_from_fitted_seating=True, standing_passengers_default=0,
        primary_layout_id=bench['layout_id'], alternative_layout_id=access['layout_id'])
    policy['selection_id'] = identity(policy)
    value = dict(schema='osr-seat-led-comfort-study/1', parent_revision=PARENT_REVISION,
        parent_composition_id=systems.PARENT_COMPOSITION_ID, parent_magnet_component_id=systems.MAGNET_ID,
        brief=dict(cars=6, car_length_m=17, exterior_width_m=2.65,
            seating='2+2 transverse seats; wall benches at door zones where wheelchair access permits',
            design_aim='Higher seated share and less crowding, with explicit reduced passenger capacity',
            ordinary_guideway='Concrete beam with passive steel facings; all permanent magnets and suspension control equipment onboard',
            comfort_is_qualified=False, retained_normal_reference_passengers_per_car=120,
            retained_credible_AW3_control_passengers_per_car=160, throughput_reference_pphpd=14400),
        budgets=dict(layout_family_variants=72, additional_explicit_layouts=len(all_layouts)-72,
            glazing_variants=33, coupled_comparisons_max=36, panel_variants_max=24,
            numerical_workers='Deterministic analytical layout, stock, plate and service screens',
            new_native_field_solves=0, reused_field_states='Only exact retained zero-current 80C PM samples; no force/current extrapolation'),
        layout_family_ids=[r['layout_id'] for r in layouts], layouts=list(all_layouts.values()),
        selected_layout_roles={role:r['layout_id'] for role,r in selected}, glazing=windows,
        envelope_options=panels, seating_door_options=furniture, comparisons=records, selection=policy,
        counts=dict(layout_family=dict(Counter(r['engineering_screen'] for r in layouts)),
                    coupled_comparisons=len(records), integrated_feasible=0),
        execution_plan=[
            dict(role='layout specialist', question='Fit2+2 rows and door benches with wheelchair access and minimal standing',
                 state='completed-analytical', outputs=['layout.py','selected layout SVGs'], acceptance='Necessary geometry only'),
            dict(role='glazing/envelope specialist', question='Count plastic windows, lightweight sandwich panels and aluminium interfaces',
                 state='completed-analytical', outputs=['glazing.py','envelope.py'], acceptance='Component fixtures; full installation unknown'),
            dict(role='systems specialist', question='Recompose exact stock, load, support samples, cooling and equal-service headway',
                 state='completed-analytical', outputs=['systems.py'], acceptance='No force extrapolation or installed-mass claim'),
            dict(role='seat/door specialist', question='Compare lighter assemblies under declared load fixtures',
                 state='completed-analytical', outputs=['seats_doors.py'], acceptance='No whole-body replacement credit'),
            dict(role='coordinator/verifier', question='Rebuild identities, challenge claims, integrate Workbench and reproduce results',
                 state='replay-required-for-verification', outputs=['publication.py','tests','Workbench'], acceptance='Physical release remains held'),
            dict(role='next engineering package', question='Create one matched equipped body, converged current maps and supplier hot-weather package',
                 state='open', outputs=[], acceptance='Required before hover/journey/operating selection')],
        structural_replacements_applied_to_composed_mass=False,
        structure_scope='Panel and aluminium-frame options remain component research. Existing magnetic hardpoints and design reactions are retained. No floor/roof/frame saving is credited before a matched equipped structural candidate exists.',
        source_sha256=source, **FLAGS)
    value['study_id'] = identity(value)
    return value


def summary(value):
    layouts={r['layout_id']:r for r in value['layouts']}
    windows={r['glazing_id']:r for r in value['glazing']}
    rows=[]
    for r in value['comparisons']:
        cabin=layouts[r['layout_id']]; window=windows[r['glazing_id']]
        cap=cabin['passenger_limit']
        load=next(c for c in r['support']['cases'] if c['passengers_total']==cap and c['unclosed_additional_mass_kg']==0)
        state=next(s for s in load['samples'] if s['gap_m']==.028)
        heat=[c['load']['total_kWthermal'] for c in r['thermal'] if c['passengers']==cap]
        rows.append(dict(candidate_id=r['candidate_id'], evaluation_id=r['evaluation_id'],
            role=r['recipe'], layout_id=cabin['layout_id'], glazing_id=window['glazing_id'],
            seats=cabin['seats_total'], benches=cabin['bench_seats'], wheelchair_places=2,
            cap=cap, standing=cabin['standing_passengers'], glazing=window['name'],
            HVAC_units=r['physical_definition']['HVAC']['units'],
            accounted_tare_kg=r['mass']['accounted_tare_kg_per_car'],
            accounted_loaded_kg=r['mass']['accounted_cap_loaded_kg_per_car'],
            capacity_at_180s_pphpd=r['service']['at_180_s_pphpd'],
            required_headway_s=r['service']['required_headway_s_arithmetic'],
            reserve_margin_28mm_N=state['smaller_sampled_contour_1_3_margin_N'],
            contour_spread_N=state['vertical_contour_spread_N'],
            heat_sensitivity_kW=[min(heat),max(heat)],
            stable_hover_established=False, complete_installed_mass_known=False,
            glazing_screen=window['evaluation']['engineering_screen'],
            glazing_fixed_panel_validity=sorted({f['fixed_panel']['numerical_validity'] for f in window['evaluation']['fixtures']})))
    return dict(study_id=value['study_id'], parent_revision=value['parent_revision'],
        selection=value['selection'], counts=value['counts'], comparisons=rows,
        layout_roles=value['selected_layout_roles'],
        component_options=[{k:r[k] for k in ('component','name','mass_basis','counted_mass_kg','necessary_screen')}
                           for r in value['envelope_options']+value['seating_door_options']], **FLAGS)


def readme(value):
    s=summary(value); primary=next(r for r in s['comparisons'] if r['role']=='door-bench-default' and r['HVAC_units']==5 and r['glazing'].startswith('Retained'))
    alternate=next(r for r in s['comparisons'] if r['role']=='wheelchair-door-bay-alternative' and r['HVAC_units']==5 and r['glazing'].startswith('Retained'))
    lines=['# Seat-led comfort and lightweight equipment options','',
        'OpenSourceRail investigates simple, locally maintainable trains on concrete beams with passive steel facings. Permanent magnets and suspension controls stay onboard; stations provide propulsion. This study tests a less crowded cabin concept with more seating, while showing its mass and passenger-throughput consequences. No comfort, structural or operating qualification is claimed.','',
        f"**Research default: {primary['seats']} fixed seats + two wheelchair users, zero standing = {primary['cap']} people/car.** The default is 2+2 seating with local access/post clearances: seven complete four-place rows and six two-place rows, plus four wall-bench seats. A declared 450 mm clear pan, 800 mm pitch and 650 mm aisle are retained. Wall benches occupy the opposite side of the two door zones; wheelchair bays use the end regions. These dimensions are hypotheses, not accessibility approval.",'',
        f"The alternative places wheelchair bays opposite the doors: {alternate['seats']} fixed seats + two wheelchair users = {alternate['cap']} people/car. Those two bays replace the door-zone benches. The wider-pan control fails the retained clear width; the 2.65 m exterior width is not usable interior width.",'',
        '## Complete-system comparison','',
        '| Layout with retained glass and five HVAC references | Capacity/car | Accounted tare | Accounted loaded | At 180 s | Headway for 14,400 pphpd |',
        '|---|---:|---:|---:|---:|---:|']
    for r in s['comparisons']:
        if r['HVAC_units']==5 and r['glazing'].startswith('Retained'):
            lines.append(f"| {r['role']} ({r['seats']} seats + 2 wheelchair users) | {r['cap']} | {r['accounted_tare_kg']/1000:.3f} t | {r['accounted_loaded_kg']/1000:.3f} t | {r['capacity_at_180s_pphpd']:,.0f} pphpd | {r['required_headway_s']:g} s |")
    lines += ['', 'These are accounted material/reference totals, not complete installed mass. The retained 800 kg interior account remains: identified seat stock resolves part of it, with no saving claimed for unlocated interior equipment. Wheelchair devices, luggage, remaining equipment, egress hardware, CG and full inertia remain unresolved. The 160-person crowd/control load is retained; a proposed cap does not physically enforce boarding limits.','',
        '## Lightweight parts: what was counted','',
        '- **Seats and benches:** 2 mm GFRP pan/back stock, foam pads, aluminium RHS supports and M8 fastener stock are counted. Bonds, seat restraints, load capacity, fire performance and complete installed joints remain open. Thin material takeoffs are not structurally validated seat assemblies.',
        '- **Doors:** two doors on one side replace four total doors. The ordinary platform already used two active doors, so normal boarding frontage is retained. Deleted openings receive counted opaque infill; the existing aperture frames remain. Platform side, terminal turnback, rescue access and emergency egress need a route-wide design.',
        '- **Windows:** 33 glazing cases compare the exact laminated-glass stock against coated rail-polycarbonate proposals, including retention, seals and subdividing mullions. Thin PC gives a density saving but may leave the linear plate model domain. A thicker, subdivided option can exceed the glass stock mass. Typical supplier material properties do not qualify the proposed window system.',
        '- **Floors, roof and aluminium chassis:** separate panel/member alternatives count material and added interfaces. Necessary bending/shear fixtures do not establish local passenger loads, complete body modes, fatigue, fire or hot-weather performance. Their prospective savings are not subtracted from the same-parent vehicle comparison.',
        '- **HVAC:** two, four and five package proposals carry their separate known hardware mass. The five-unit reference is retained for the main comparison. Thermal sensitivities preserve fresh-air supply per person and cover dry/humid 50°C cases. Actual supplier output, input power and N−1 performance at 50°C remain unknown.','',
        '## What this does to the suspension gap','',
        f"At 28 mm and 80°C the smaller retained PM force contour exceeds the default's 1.3× accounted load by {primary['reserve_margin_28mm_N']:,.0f} N/module, before unclosed extra mass. The two contour calculations still differ by {primary['contour_spread_N']:,.0f} N/module. Those samples are not confidence bounds and are not a converged force map.",'',
        'Lower payload improves arithmetic reserve, but at an unchanged attractive-PM gap can also cause excess upward force. A stable equilibrium, lateral restoring/damping behaviour, sufficient active-current authority, thermal duty and safe power-loss response remain unproved. No force at a new gap or current is invented. No new magnetic finite-element solve or physical journey was executed for this cabin study.','',
        '## Comfort and capacity must be presented together','',
        'The defensible description is **higher seated share and less crowding at a lower declared capacity**. Ride quality, accessibility and thermal comfort still require evidence. Matching the original throughput with shorter headways needs more departures, fleet, station power and a proven protected-arrival system; it is not established by the arithmetic. Alternatively, evaluate longer formations and their platforms as a separate specification. No city baseline or structural crowd load has been silently reduced.','',
        '## Evidence and next work','',
        f"Executed: 72 bounded layout variants ({value['counts']['layout_family']}), 33 glazing variants, {len(value['envelope_options'])} panel options, {len(value['seating_door_options'])} bench/door component fixtures and {len(value['comparisons'])} composed mass/support/thermal/service comparisons. Exact geometry, source hashes, failures and unknowns are retained in [the compressed study](study.json.gz). [Compact results](summary.json), [receipt](manifest.json) and [interactive comparison](../../../workbench/trip/readiness/comfort/) use the same study identity.",'',
        'Next: rebuild one equipped native body with actual seat/door/window positions; establish restraints and accessible swept paths; validate the hot-weather glazing/HVAC package; converge multiaxis magnetic/current maps; then qualify hover, faults and a same-candidate journey. Panel and frame changes require their own matched structural and magnetic interface evaluation.','',
        '[Door-bench default plan](door-bench-default.svg) · [Wheelchair-door-bay alternative](wheelchair-door-bay-alternative.svg)','',
        'Reproduce and verify from repository root:','',
        '```bash',
        'python -m engineering.comfort_options publish --output build/comfort-fresh',
        'python -m engineering.comfort_options verify --output build/comfort-fresh',
        'python -m pytest --import-mode=importlib -q engineering/comfort_options/tests',
        '```','', f"Parent revision: `{value['parent_revision']}`. Study: `{value['study_id']}`. All physical acceptance and release flags remain false.",'']
    components=['## Bounded component results','',
        'Masses below have different stated scopes. A necessary fixture pass is not a complete assembly pass. No component saving below is credited to the vehicle table above.','',
        '| Component option | Mass scope | Counted material/reference mass | Necessary fixture |',
        '|---|---|---:|---|']
    for r in value['envelope_options']+value['seating_door_options']:
        components.append(f"| {r['name']} | {r['mass_basis']} | {r['counted_mass_kg']:.2f} kg | {r['necessary_screen']} |")
    components += ['', 'Panel comparisons use declared continuous-section stiffness and local strip loads; tiled joint continuity and whole-body participation remain unknown. Bench loads and door-pressure fixtures are declared research hypotheses, not acceptance criteria. Source material URLs and temperature limitations are included with each record.','',
        'Primary material references: [coated rail polycarbonate](https://plaskolite.com/docs/default-source/pds/pds183_tuf_tg.pdf), [Divinycell H core](https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf) and [glass-epoxy plate comparator](https://www.hippe.de/en/products/detail/product/ep-gc-202-as). Their published coupon properties do not qualify the new assemblies.','']
    return '\n'.join(lines).replace('## What this does to the suspension gap', '\n'.join(components)+'\n## What this does to the suspension gap')


def payloads(value):
    files={'study.json.gz':gzip.compress(encoded(value), mtime=0),
           'summary.json':encoded(summary(value)), 'README.md':readme(value).encode()}
    by_id={r['layout_id']:r for r in value['layouts']}
    for role,lid in value['selected_layout_roles'].items():
        files[role+'.svg']=layout.render_svg(by_id[lid]).encode()
    manifest=dict(schema='osr-seat-led-comfort-publication/1', study_id=value['study_id'],
        source_sha256=value['source_sha256'],
        files_sha256={n:sha256(raw).hexdigest() for n,raw in files.items()}, **FLAGS)
    manifest['manifest_id']=identity(manifest)
    files['manifest.json']=encoded(manifest)
    return files


def ui_files(root, files):
    digest=sha256(files['summary.json']).hexdigest()
    return {name:(Path(root)/'engineering/comfort_options/web'/name).read_bytes().replace(
        b'__SUMMARY_SHA256__',digest.encode()) for name in ('index.html','app.js','app.css')}


def publish(output=OUTPUT, root=ROOT):
    root=Path(root).resolve(); output=Path(output).resolve()
    if output.exists():
        raise ValueError('fresh output directory required; keep previous runs')
    start=time.monotonic();value=assemble(root);files=payloads(value)
    output.mkdir(parents=True)
    for name,raw in files.items(): (output/name).write_bytes(raw)
    if output == root/OUTPUT:
        web=root/WORKBENCH;web.mkdir(parents=True, exist_ok=True)
        for name,raw in ui_files(root,files).items(): (web/name).write_bytes(raw)
    return dict(study_id=value['study_id'], elapsed_s=round(time.monotonic()-start,2), counts=value['counts'], **FLAGS)


def verify(output=OUTPUT, root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve()
    value=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))
    if value['study_id']!=identity({k:v for k,v in value.items() if k!='study_id'}):
        raise ValueError('study identity differs')
    # Deterministic replay rejects mixed source, forged geometry/margins or acceptance.
    expected=assemble(root)
    if value!=expected: raise ValueError('study differs from deterministic replay')
    files=payloads(expected)
    for name,raw in files.items():
        if (output/name).is_symlink() or (output/name).read_bytes()!=raw:
            raise ValueError('publication differs: '+name)
    if output==root/OUTPUT:
        for name,raw in ui_files(root,files).items():
            if (root/WORKBENCH/name).read_bytes()!=raw:raise ValueError('Workbench differs: '+name)
    return dict(verified=True,study_id=value['study_id'],comparisons=len(value['comparisons']),**FLAGS)
