"""Equal-context, installed-inventory panel screens, without release authority.

All beam models assume perfect attachment/composite action and ideal simple
supports. These are sensitivity hypotheses, never joint or railway acceptance.
The retained laminate study is an input; its outputs and qualification stay intact.
"""
from copy import deepcopy
import csv
from hashlib import sha256
import io
import itertools
import json
import math
from pathlib import Path
import sys

from engineering.twin_workflow import core

ROOT = core.ROOT
sys.path.insert(0, str(ROOT / 'design/component-catalogue/src'))
from osr_mech.rolling_stock import composite_panels as panel

CONFIG = ROOT / 'engineering/panel_materials/config/benchmark.json'
BASELINE = ROOT / 'engineering/composite_panels/config/development.json'
SOURCES = ROOT / 'engineering/panel_materials/config/sources.json'
OUTPUT = ROOT / 'engineering/panel_materials/reference'
ROUTES = ('stiffened-aluminium', 'aluminium-sandwich', 'gfrp-sandwich')
OPEN = [
    'approved aerodynamic, impact and service load envelope',
    'exact alloy/temper or laminate/core/bond/finish/liner material stack',
    'local buckling, face wrinkling, strength, debonding and damage tolerance',
    'joint stiffness/slip, galvanic isolation, thermal movement and mount allowables',
    'clip-loss retention, vibration/fatigue, sealing and aged pressure tests',
    'complete-stack railway fire requirement set, hazard level and tests',
    'roof PV heat soak and temperature-qualified core/bond/finish/seals',
    'aperture/end-detail coordination and native geometry reconstruction',
    'supplier quotes, measured labour/rejects/throughput and replacement trials',
]


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('positive finite ' + name + ' required')
    return value


def validate(config):
    if config['schema'] != 'osr-panel-material-benchmark/1' or config['reference_route'] != ROUTES[0]:
        raise ValueError('unknown benchmark or reference route')
    for key in ('pressure_pa', 'deflection_limit_m', 'thermal_resistance_review_m2k_w',
                'support_pitch_limit_m', 'width_m', 'side_height_m', 'roof_chord_m', 'liner_mass_kg_m2'):
        positive(config[key], key)
    crown = config['roof_crown_m']
    if isinstance(crown, bool) or not isinstance(crown, (int, float)) or not math.isfinite(crown) or not 0 <= crown < config['roof_chord_m']/2:
        raise ValueError('bounded nonnegative roof crown required')
    for key in ('side_temperature_c', 'roof_temperature_c'):
        if isinstance(config[key], bool) or not isinstance(config[key], (int, float)) or not math.isfinite(config[key]):
            raise ValueError('finite temperature required')
    for key, value in config['aluminium'].items():
        if key != 'basis': positive(value, key)
    for key, value in config['hat'].items(): positive(value, key)
    for values in config['sweep'].values():
        if not values: raise ValueError('empty sweep')
        for value in values: positive(value, 'sweep value')
    for factor in (config['gfrp_stiffness_sensitivity_factor'], config['core_shear_sensitivity_factor'], config['aluminium']['stiffness_sensitivity_factor']):
        if not 0 < positive(factor, 'sensitivity factor') <= 1:
            raise ValueError('sensitivity factor exceeds one')
    # Commercial values are deliberately not consumed by this physical screen.
    # Quotes require exact candidate identity/scope and a separate verifier.
    if any(value is not None for value in config['commercial'].values()):
        raise ValueError('commercial inputs need a separately verified quotation/cost adapter')


def section_properties(rectangles):
    """Exact sum of disjoint rectangular areas, centroid and parallel-axis I."""
    for width, depth, z in rectangles:
        positive(width, 'rectangle width'); positive(depth, 'rectangle depth')
        if not math.isfinite(z): raise ValueError('finite rectangle centroid required')
    area = math.fsum(w*t for w, t, z in rectangles)
    centre = math.fsum(w*t*z for w, t, z in rectangles)/area
    inertia = math.fsum(w*t**3/12 + w*t*(z-centre)**2 for w, t, z in rectangles)
    return dict(area_m2=area, centroid_z_m=centre, inertia_m4=inertia)


def hat_section(pitch, skin, depth, hat):
    for value in (pitch, skin, depth): positive(value, 'hat dimension')
    wall, crown, foot = hat['wall_m'], hat['crown_width_m'], hat['foot_width_each_m']
    if crown+2*wall+2*foot >= pitch:
        raise ValueError('hat feet overlap adjacent tributary strip')
    # Ideal sharp-corner folded hat, flat skin at z=0..skin. Webs and crown
    # meet at boundaries; feet lie outboard of webs on top of the face sheet.
    rectangles = [(pitch, skin, skin/2), (wall, depth, skin+depth/2),
                  (wall, depth, skin+depth/2), (crown, wall, skin+depth+wall/2),
                  (foot, wall, skin+wall/2), (foot, wall, skin+wall/2)]
    return section_properties(rectangles)


def beam_deflection(pressure, span, stiffness):
    for value in (pressure, span, stiffness): positive(value, 'beam input')
    return 5*pressure*span**4/(384*stiffness)


def context(config, baseline, kind):
    if kind not in ('side', 'roof'): raise ValueError('unknown panel location')
    width = config['width_m']
    chord = config['side_height_m'] if kind == 'side' else config['roof_chord_m']
    crown = 0 if kind == 'side' else config['roof_crown_m']
    length = panel.roof_arc(chord, crown)['arc_length_m']
    network = panel.support_network(baseline, width, length, config['support_pitch_limit_m'])
    definition = dict(kind=kind, width_m=width, chord_m=chord, crown_m=crown,
        developed_length_m=length, panel_area_m2=width*length,
        pressure_pa=config['pressure_pa'], support_network=network,
        ideal_simple_span_m=network['actual_max_pitch_m'],
        deflection_limit_m=config['deflection_limit_m'],
        thermal_resistance_review_m2k_w=config['thermal_resistance_review_m2k_w'],
        temperature_c=config[kind+'_temperature_c'],
        interface_status='Common proposed outer surface and rail/clip sites; depth, mounts, edge overhang and tolerance compatibility unqualified',
        hardware_basis='Common steel rails/brackets/fasteners, clips, independent retention, seals; route-specific load introduction remains proposed',
        structural_frame_excluded=True, equipment_loads_to_frame=True,
        roof_scope='Developed-coordinate strip; no curvature stiffness, roof-equipment or worker load credit')
    return dict(**definition, revision=core.digest(definition))


def candidate(config, baseline, ctx, route, variables):
    if route not in ROUTES: raise ValueError('unknown panel material route')
    if ctx != context(config, baseline, ctx.get('kind')):
        raise ValueError('exact source-bound panel context required')
    c = deepcopy(baseline)
    density = variables.get('core_density_kg_m3', 80)
    c['core'] = panel.coupled_core(c, density)
    width, length, area = ctx['width_m'], ctx['developed_length_m'], ctx['panel_area_m2']
    network = ctx['support_network']; count = network['panel_attachment_count']
    pressure, span = ctx['pressure_pa'], ctx['ideal_simple_span_m']
    metal = config['aluminium']; hat = config['hat']
    if route == 'stiffened-aluminium':
        skin, depth = variables['sheet_m'], variables['hat_depth_m']
        n = math.ceil(width/positive(variables['hat_pitch_limit_m'], 'hat pitch'))
        pitch = width/n
        props = hat_section(pitch, skin, depth, hat)
        ei = metal['young_pa']*props['inertia_m4']*metal['stiffness_sensitivity_factor']
        global_deflection = beam_deflection(pressure*pitch, span, ei)
        local_deflection = beam_deflection(pressure, pitch, metal['young_pa']*skin**3/12*metal['stiffness_sensitivity_factor'])
        delta = global_deflection+local_deflection
        hat_area = props['area_m2']-pitch*skin
        # Ideal mitered perimeter returns, no corner overlap or bend-arc credit.
        return_volume = 2*(width+length)*hat['edge_return_m']*skin
        foam_volume = area*depth-hat_area*n*length
        if foam_volume <= 0: raise ValueError('hat assembly consumes insulation volume')
        masses = dict(face=area*skin*metal['density_kg_m3'],
            hats=hat_area*n*length*metal['density_kg_m3'],
            edge_returns=return_volume*metal['density_kg_m3'],
            insulation=foam_volume*c['core']['density_kg_m3'],
            stiffener_joints=n*length*hat['joint_mass_kg_per_m'],
            backing_plates=count*.025*.05*.003*metal['density_kg_m3'])
        masses.update({k: v for k, v in common_hardware(c, area, width, length, count).items()})
        # Perfect thermal contact at the two webs gives a parallel-path screen.
        # Perimeter/mount bridges remain unresolved for all three routes.
        fraction = 2*hat['wall_m']/pitch
        rfoam = skin/metal['thermal_conductivity_w_mk']+depth/c['core']['thermal_conductivity_w_mk']
        rweb = (skin+depth)/metal['thermal_conductivity_w_mk']
        thermal = 1/((1-fraction)/rfoam+fraction/rweb)
        model = dict(section=props, hat_count=n, actual_hat_pitch_m=pitch,
            hat_stations_x_m=[(i+.5)*pitch for i in range(n)],
            global_beam_deflection_m=global_deflection, local_skin_deflection_m=local_deflection,
            total_deflection_m=delta, core_shear_deflection_m=0,
            stiffness_credit='Perfectly attached full-width face plus hats; unqualified effective width, local buckling, shear deformation and fastener slip',
            depth_m=skin+depth+hat['wall_m'],
            geometry_basis='Ideal sharp-corner strip lengths; bend radii, bend allowance and edge/hat junctions need native manufacturing drawings')
        process = ['cut and deburr blanks', 'form edge returns and hat sections', 'roll roof curvature if needed',
                   'assemble hats with proposed mechanical joints', 'corrosion/isolation treatment',
                   'fit insulation, liner, backing plates and common mount/seal kit', 'master-frame fit and inspect']
    else:
        skin, depth = variables['skin_m'], variables['core_m']
        if route == 'aluminium-sandwich':
            c['glass'].update(density_kg_m3=metal['density_kg_m3'], thermal_conductivity_w_mk=metal['thermal_conductivity_w_mk'])
        # Same solid edge-land, potting and mount quantities for each sandwich.
        q = panel.panel_quantities(c, width, length, skin, depth, insert_count=count)
        masses = dict(q['mass_kg'])
        masses['skins_and_solid_edge_lands'] = masses.pop('glass')
        thermal = q['thermal_resistance_m2k_w']
        if route == 'gfrp-sandwich':
            abd = panel.laminate_abd(panel.balanced_skin(skin), depth, c['bond']['thickness_m_each'], c['glass'])
            response = panel.strip_response(abd, pressure, span, depth, c['core']['minimum_shear_pa'],
                stiffness_factor=config['gfrp_stiffness_sensitivity_factor'], shear_factor=config['core_shear_sensitivity_factor'])
            bending, shear = response['bending_deflection_m'], response['shear_deflection_m']
        else:
            arm = depth/2+c['bond']['thickness_m_each']+skin/2
            stiffness = metal['young_pa']*2*(skin**3/12+skin*arm**2)*metal['stiffness_sensitivity_factor']
            bending = beam_deflection(pressure, span, stiffness)
            shear = pressure*span**2/(8*c['core']['minimum_shear_pa']*depth*config['core_shear_sensitivity_factor'])
        delta = bending+shear
        model = dict(bending_deflection_m=bending, core_shear_deflection_m=shear, total_deflection_m=delta,
            maximum_core_shear_stress_pa=pressure*span/(2*depth),
            depth_m=2*skin+depth+2*c['bond']['thickness_m_each'],
            stiffness_credit='Perfectly bonded skins and core; no edge-land, curvature or membrane stiffness credit',
            geometry_basis='Developed flat mass/strip screen; curved offset layers and insert locations require native reconstruction')
        process = (['prepare metal skins and solid edge closures', 'prepare and pretreat bond surfaces', 'bond skins/core/lands/inserts in fixture',
                    'control cure and inspect bonds'] if route == 'aluminium-sandwich' else
                   ['prepare mould and fibre/core kits', 'lay up skins and solid lands, locate inserts',
                    'infuse and cure to a supplier-controlled schedule', 'trim, seal cut edges and inspect bonds'])
        process += ['fit liner and common mount/seal kit', 'master-frame fit and inspect']
    masses['liner'] = area*config['liner_mass_kg_m2']
    masses['support_rails_brackets_fasteners'] = network['mass_kg']
    if any(not math.isfinite(m) or m < 0 for m in masses.values()): raise ValueError('invalid mass inventory')
    checks = dict(deflection_surrogate=delta <= ctx['deflection_limit_m'],
        small_deflection=delta/span <= .01,
        core_continuous_temperature=ctx['temperature_c'] <= c['core']['continuous_max_temperature_c'],
        conduction_review=thermal >= ctx['thermal_resistance_review_m2k_w'])
    definition = dict(context_revision=ctx['revision'], route=route, variables=variables,
        config_sha256=core.digest(config), baseline_sha256=core.digest(baseline))
    return dict(id=core.digest(definition), **definition, kind=ctx['kind'],
        mass_components_kg=masses, installed_mass_kg=math.fsum(masses.values()),
        installed_mass_kg_m2=math.fsum(masses.values())/area,
        model=model, conduction_resistance_screen_m2k_w=thermal,
        thermal_scope='Conduction-only local section; perimeter/mount bridges, convection, solar/PV heat and complete service temperature remain unqualified',
        core_grade=c['core'], screening_checks=checks, conditional_screen_pass=all(checks.values()),
        mandatory_engineering_checks={name: None for name in OPEN},
        installed_cost_usd=None, factory_hours=None, annual_good_panels=None, replacement_minutes=None,
        process=process, engineering_eligible=False, **core.FLAGS)


def common_hardware(c, area, width, length, count):
    return dict(finish=area*c['finish']['thickness_m']*c['finish']['density_kg_m3'],
        clips=count*c['hardware']['clip_mass_kg_each'], retainer=c['hardware']['retainer_mass_kg'],
        seal=2*(width+length)*c['hardware']['seal_mass_kg_per_m'])


def generate_cases(config, baseline):
    validate(config)
    contexts = [context(config, baseline, kind) for kind in ('side', 'roof')]
    cases = []; grid = config['sweep']
    for ctx in contexts:
        for sheet, depth, pitch in itertools.product(grid['sheet_m'], grid['hat_depth_m'], grid['hat_pitch_limit_m']):
            cases.append(candidate(config, baseline, ctx, ROUTES[0], dict(sheet_m=sheet, hat_depth_m=depth, hat_pitch_limit_m=pitch)))
        for route, skin, depth, density in itertools.product(ROUTES[1:], grid['sandwich_skin_m'], grid['sandwich_core_m'], grid['core_density_kg_m3']):
            cases.append(candidate(config, baseline, ctx, route, dict(skin_m=skin, core_m=depth, core_density_kg_m3=density)))
    return contexts, cases


def representatives(cases):
    rows = []
    for kind, route in itertools.product(('side', 'roof'), ROUTES):
        peers = [c for c in cases if c['kind'] == kind and c['route'] == route]
        passing = [c for c in peers if c['conditional_screen_pass']]
        # A failure representative is explicitly diagnostic, never a fallback pass.
        selected = min(passing, key=lambda c: (c['installed_mass_kg'], c['id'])) if passing else min(peers, key=lambda c: (c['model']['total_deflection_m'], c['id']))
        rows.append(dict(candidate_id=selected['id'], kind=kind, route=route,
            selection='lowest installed mass meeting four provisional screens' if passing else 'diagnostic lowest deflection; no candidate meets all four screens',
            screening_pass=bool(passing), engineering_eligible=False))
    return rows


def diagram(contexts):
    # Geometry-derived developed view, not a rendered native solid or animation.
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="530" viewBox="0 0 1100 530">',
        '<rect width="1100" height="530" fill="#f8fafc"/>',
        '<g font-family="sans-serif" fill="#24394b"><text x="25" y="30" font-size="22">Common proposed panel interface — developed view</text>',
        '<text x="25" y="55">Same outer footprint, rail stations and clip sites for all three routes; mounts remain unqualified.</text>']
    for index, ctx in enumerate(contexts):
        x, y, scale = 65+index*510, 100, 95
        w, h = ctx['width_m']*scale, ctx['developed_length_m']*scale
        elements += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#d8e7ed" stroke="#203647"/>',
            f'<text x="{x+130}" y="{y+25}">{ctx["kind"]}: {ctx["width_m"]*1000:.0f} mm wide</text>',
            f'<text x="{x+130}" y="{y+50}">{ctx["developed_length_m"]*1000:.1f} mm developed</text>',
            f'<text x="{x+130}" y="{y+75}">Crown {ctx["crown_m"]*1000:.0f} mm; no stiffness credit</text>']
        for rail in ctx['support_network']['rails']:
            ry = y+rail['station_m']*scale
            elements.append(f'<path d="M{x},{ry} h{w}" stroke="#426e88" stroke-width="4"/>')
        for a, b in ctx['support_network']['panel_attachment_sites_m']:
            elements.append(f'<circle cx="{x+a*scale}" cy="{y+b*scale}" r="3.5" fill="#af542c"/>')
    elements += ['<text x="25" y="475">Each route includes its own skin/core or hats, edges, mounts, seals, finish, liner and common supports.</text>',
        '<text x="25" y="500">Reference dimensions are provisional. Roof equipment and primary carbody loads bypass these replaceable panels.</text></g></svg>']
    return '\n'.join(elements).encode()


def report(config, cases, reps):
    by_id = {c['id']: c for c in cases}
    rows = ['# Replaceable body-panel material benchmark', '',
        'Aluminium is the reference hypothesis for straightforward removable panels. GFRP remains an alternative for curved ends, fairings and roofs. Primary carbody structure is a separate design decision.', '',
        f'{len(cases)} generated side/roof hypotheses compare stiffened aluminium, aluminium sandwich and GFRP sandwich. **No engineering-eligible or released design is selected.** This standalone reproducible benchmark does not change the adopted train BOM, price, mass or the qualified background runner.', '',
        '![Proposed common panel interface](interface.svg)', '',
        '[All candidate definitions/results](candidates.json) · [Comparison CSV](comparison.csv) · [Common interface contexts](contexts.json) · [Summary](summary.json) · [Prepared RFQ](rfq.json) · [Sources and British manufacturing shortlist](../config/sources.json)', '',
        '| Location | Route | Installed kg | Deflection mm | Conduction R m²K/W | Four provisional screens |',
        '|---|---|---:|---:|---:|---|']
    for rep in reps:
        c = by_id[rep['candidate_id']]
        rows.append(f'| {c["kind"]} | {c["route"]} | {c["installed_mass_kg"]:.2f} | {c["model"]["total_deflection_m"]*1000:.2f} | {c["conduction_resistance_screen_m2k_w"]:.3f} | {"Conditional pass" if rep["screening_pass"] else "Fails; diagnostic only"} |')
    rows += ['',
        'For each location/route, the table shows minimum installed mass meeting the four provisional screens; if none does, it shows the lowest-deflection diagnostic. Candidate IDs and exact selection reasons are in summary.json. A failed diagnostic is never promoted.', '',
        f'All routes use the same developed footprint, proposed rails/clip sites, actual rail span, {config["pressure_pa"]/1000:g} kPa editable pressure and {config["deflection_limit_m"]*1000:g} mm deflection screen. These are research assumptions, not approved railway loads or acceptance limits. Roof curvature earns no membrane stiffness. Solid bays are screened; door/window cutouts and compound-curved ends need their own matched generators. The historical 144-module three-car inventory is not a six-car quantity or a new mass estimate.', '',
        'Installed inventory includes skins, core/insulation, solid edge closures or returns, hats where used, potting/inserts or backing plates, clips, independent retention, seals, finish, a common provisional liner allowance and the same actual steel rails/brackets/fasteners. The parent structural frame and equipment are excluded equally. Folded returns use ideal mitered strip lengths; bend allowances and mount geometry need manufacturing CAD. Complete rail fire performance of the liner and entire stack remains unknown.', '',
        'The folded-sheet screen adds local skin bending between hats to global face/hat strip bending. Full face effectiveness, perfect hat attachment and simple supports are ideal assumptions; fastener slip, shear deformation, local buckling, joints, strength and fatigue remain open. Sandwich screens assume perfect bonds; laminate ABD is retained for GFRP. Sensitivity factors are deliberately material-specific and uncalibrated, not measured hot/wet or temperature allowables.', '',
        f'Conduction is screened separately from bending against an editable {config["thermal_resistance_review_m2k_w"]:g} m²K/W review threshold. Aluminium webs and solid aluminium edge lands introduce thermal paths; a light metal panel can therefore fail the shared conduction screen. These are deliberately simple metal details, not optimised thermally broken aluminium constructions. No cost or assembly-speed superiority follows from these results. The inherited H60/H80/H100 cores have a 70°C continuous-temperature datum; the roof hypothesis is {config["roof_temperature_c"]:g}°C. Every generated candidate retains its own temperature result. Higher-temperature stacks must be added with full coupled properties and fire/bond evidence rather than deleting a failed screen.', '',
        'British manufacture is prioritised case by case: Esprit Photon 5G for a quoted metal-cutting configuration; Blackman & White Genesis-Z/Genesis-V for fibre/core kit preparation. Their manufacturers state UK manufacture; that is not proof of every component origin, Iraqi support or process fitness. A brake/rolling machine, cure/infusion cell and trim/extraction cell remain unselected. Tiderock is a rail-composite technical partner enquiry, not a panel approval. The side bay exceeds a 3 m table before trim margins; confirm a larger bed or qualified indexed operation. No supplier has been contacted.', '',
        'The RFQ requires identical issued interfaces/quantities and complete installed scope: material, labour, tooling, cure/energy, scrap/rework, fixtures, qualification, maintenance and replacement. Annual volume, good output per shift, local labour, tooling amortisation, price and replacement time are unknown and remain null. Use first-article coupons, joint/insert specimens and pressure/heat/fire/retention rigs to replace assumptions before any cost winner or installed release.', '',
        'Run `.venv/bin/python tools/automation/panel-material-study.py`; use `--check` to reproduce source/output hashes. Existing native GFRP CAD and plate studies remain separate evidence and do not confirm these new metal candidates. Integrating this adapter into the uninterrupted qualified runner requires native reconstruction, adverse controls and a new exact-source qualification epoch.', '',
        'Primary technical sources: [Hydro rail extrusions](https://www.hydro.com/gb/global/aluminium/products/extruded-profiles/aluminium-extrusions-in-use/modern-trains-and-rail/), [Composites UK process selection](https://compositesuk.co.uk/composite-materials/processes/), [Tiderock rail](https://tiderockcomposites.com/rail/), [Esprit Photon 5G](https://espritautomation.com/photon-5g/), [Blackman & White manufacture](https://blackmanandwhite.com/about-us/), [BSI railway fire scope](https://landingpage.bsigroup.com/LandingPage/Undated?UPI=000000000030334174). Core values come from the source-hashed supplier-grade records in the existing development config, with no project calibration claimed.', '']
    return '\n'.join(rows).encode()


def build():
    config, baseline = core.read(CONFIG), core.read(BASELINE)
    sources = core.read(SOURCES)
    contexts, cases = generate_cases(config, baseline)
    reps = representatives(cases)
    outputs = {'contexts.json': core.encoded(contexts), 'candidates.json': core.encoded(cases),
        'interface.svg': diagram(contexts), 'README.md': report(config, cases, reps)}
    outputs['summary.json'] = core.encoded(dict(schema='osr-panel-material-results/1', candidate_count=len(cases),
        reference_route=config['reference_route'], representatives=reps,
        conditional_pass_count=sum(c['conditional_screen_pass'] for c in cases),
        engineering_eligible_count=0, selected_released_design=None,
        adopted_train_mass_or_bom_changed=False, qualified_runner_changed=False,
        scope='Matched-footprint analytical strip and inventory study; not native CAD, physical tests or complete railway acceptance', **core.FLAGS))
    table = io.StringIO()
    fields = ['candidate_id', 'context_revision', 'kind', 'route', 'installed_mass_kg', 'installed_mass_kg_m2',
              'deflection_mm', 'conduction_resistance_m2k_w', 'conditional_screen_pass', 'installed_cost_usd', 'engineering_eligible']
    writer = csv.DictWriter(table, fieldnames=fields, lineterminator='\n'); writer.writeheader()
    for c in cases:
        writer.writerow(dict(candidate_id=c['id'], context_revision=c['context_revision'], kind=c['kind'], route=c['route'],
            installed_mass_kg=c['installed_mass_kg'], installed_mass_kg_m2=c['installed_mass_kg_m2'],
            deflection_mm=c['model']['total_deflection_m']*1000, conduction_resistance_m2k_w=c['conduction_resistance_screen_m2k_w'],
            conditional_screen_pass=c['conditional_screen_pass'], installed_cost_usd=None, engineering_eligible=False))
    outputs['comparison.csv'] = table.getvalue().encode()
    outputs['rfq.json'] = core.encoded(dict(schema='osr-panel-material-rfq/1', state='prepared-not-sent',
        reference_candidate_ids=[r['candidate_id'] for r in reps], context_revisions=[c['revision'] for c in contexts],
        quantity_per_year=None, actual_quote=False, supplier_cases=sources['supplier_cases'],
        required_scope=['issued panel/interface drawings and exact candidate revision', 'all installed materials, mounts, seals, finish and liner',
            'factory rails/brackets/fasteners and assembly fixtures', 'tooling, first articles and qualification programme',
            'labour, energy, cure, trim, inspection and measured good output per shift', 'scrap/rework and warranty',
            'currency, date, validity, lead time and annual volume', 'repair, timed replacement and spare kits',
            'machine origin and UK economic activity; Baghdad export/installation/training/service support'],
        required_evidence=OPEN, purchase_approved=False, **core.FLAGS))
    dependencies = [CONFIG, BASELINE, SOURCES, Path(__file__), Path(__file__).with_name('__init__.py'),
        ROOT/'tools/automation/panel-material-study.py', ROOT/'engineering/twin_workflow/core.py',
        ROOT/'engineering/analysis/tests/test_panel_materials.py',
        ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/composite_panels.py',
        *[ROOT/'design/component-catalogue/src/osr_mech'/name for name in
          ('__init__.py', 'section_contract.py', 'automated_geometry.py', 'provenance.py',
           'engineering_definition.py', 'family_definition.py', 'vehicle_mass_properties.py',
           'schema_validation.py', 'industrialisation.py')]]
    outputs['manifest.json'] = core.encoded(dict(schema='osr-panel-material-manifest/1',
        sources_sha256={p.relative_to(ROOT).as_posix(): core.sha(p) for p in dependencies},
        outputs_sha256={name: sha256(data).hexdigest() for name, data in outputs.items()}, **core.FLAGS))
    return outputs


def publish(folder=OUTPUT, check=False):
    outputs = build(); folder = Path(folder)
    if not check: folder.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        path = folder/name
        if check:
            if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
                raise ValueError('stale panel material artifact: ' + name)
        else:
            if path.is_symlink(): raise ValueError('refusing symlink output')
            path.write_bytes(data)
    return json.loads(outputs['summary.json'])
