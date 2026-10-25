"""Compile a source-bound research coupon and readable campaign evidence."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import shutil

from engineering.design_search.contracts import FLAGS, encoded, identity
from engineering.factory_examples import native
from . import campaign, geometry, fields, controls

REFERENCES = [
    dict(url='https://rosap.ntl.bts.gov/view/dot/16183/dot_16183_DS1.pdf',
         title='MagneMotion Urban Maglev final report, 2004',
         use='Architecture precedent for onboard PM bias, active gap regulation and lateral alignment/damping. Its prototype performance and wayside propulsion do not validate our FB9B geometry or finite station zones.'),
    dict(url='https://umt1998.tongji.edu.cn/en/article/doi/10.16037/j.1007-869x.20240770',
         title='Nonlinear hybrid suspension comparison, 2026',
         use='Gap stiffness/current sensitivity tradeoff; no transfer of forces, material properties or acceptance to this candidate.'),
    dict(url='https://backend.orbit.dtu.dk/ws/portalfiles/portal/236194050/09285330.pdf',
         title='Passive permanent magnetic bearing study, 2021',
         use='Stability and stiffness tradeoffs only. A NdFeB ring-bearing study is not a ferrite train/steel-facing benchmark.'),
    *controls.REFERENCES,
    dict(url=geometry.FHWA_TOLERANCES,title='FHWA prefabricated bridge fit-up',
         use='Common datums and deliberate fit-up allowance. Ordinary bridge tolerances are not approved magnetic-gap tolerances.'),
    dict(url=geometry.FHWA_BEARINGS,title='FHWA prefabricated bridge substructures',
         use='Simple bearing/installation possibilities; actual load, movement, anchorage and fatigue design remains required.'),
    dict(url=geometry.DLR_FLEXURES,title='Experimental flexure-hinge study',
         use='Manufacturing/fatigue sensitivity; our unsized multiaxis carrier receives no test qualification.'),
    dict(url='https://www.sciencedirect.com/science/article/pii/S030488532600507X',
         title='User-supplied homopolar paper link',access='Not retrieved; HTTP 403 and no independently established metadata',
         use='No numerical performance or evidence credit. Travel drag remains unknown.'),
]


def diagram(value):
    """A labelled local section derived directly from solved region rectangles."""
    colours={'steel':'#708799','ferrite':'#ba4254','copper':'#df9b3c'}
    scale=1100.;ox=470.;oz=225.
    items=['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="490" viewBox="0 0 940 490">',
           '<rect width="940" height="490" fill="#f5f7fa"/>',
           '<g font-family="sans-serif" fill="#17324a">',
           '<text x="30" y="36" font-size="22">Onboard magnets · passive steel facing</text>',
           '<text x="30" y="63" font-size="14">Local transverse section, one bank; travel direction is out of the page</text>',
           '<path d="M120 112H820V175H120Z" fill="#d5d9da" stroke="#818b91" stroke-dasharray="5 4"/>',
           '<text x="330" y="141" font-size="14">Concrete load path (schematic)</text>']
    for q in value['regions']:
        y0,y1,z0,z1=q['bounds_yz_m']
        items.append(f'<rect x="{ox+scale*y0:.3f}" y="{oz-scale*z1:.3f}" width="{scale*(y1-y0):.3f}" height="{scale*(z1-z0):.3f}" fill="{colours[q["material"]]}" stroke="#25384b" stroke-width="1"><title>{escape(q["id"])}</title></rect>')
    items += [f'<text x="30" y="398" font-size="15">Reference gap: {value["reference_gap_m"]*1000:g} mm · Facing width: {value["parameters"]["facing_width_m"]*1000:g} mm · Length: {value["length_x_m"]:g} m</text>',
              '<text x="30" y="424" font-size="14">Red: onboard ferrite · Orange: winding windows · Blue: steel facing / onboard yokes</text>',
              '<text x="30" y="449" font-size="13">Exact conductor legs and end turns are in the CAD/BOM. Anchors, retention and cooling are unresolved.</text>',
              '<text x="30" y="472" font-size="13">Research coupon. This drawing does not establish installed clearances, strength or stable operation.</text>',
              '</g></svg>']
    return '\n'.join(items)+'\n'


def readme(summary, native_record):
    rows=[]
    for report in summary['reports']:
        field=report['reference_field']
        lift='Refused' if field is None else f'{field["F_z_N"]:,.0f}'
        rows.append(f'| {report["sample_id"]} | {report["stock"]["train_known_mass_kg_per_car"]/1000:.3f} | {lift} | {report["support_reserve_floor_N_per_module"]:,.0f} | {report["reference_numerical_status"]} |')
    selected=summary['next_experiment']['selected_candidate_id']
    chosen=next((r for r in summary['reports'] if r['candidate_id']==selected),None)
    chosen_name=chosen['sample_id'] if chosen else 'None'
    candidate_link=f'[Candidate](candidates/{selected}.json)' if selected else 'No numerical selection'
    native_links='Native CAD was not executed; no substitute export is issued.'
    if native_record['execution_status']=='executed':
        native_links='[FreeCAD](native/model.FCStd) · [STEP](native/model.step) · [Native reopen/volume receipt](native/native-cad.json)'
    return f'''# Onboard magnets and passive steel facings

OpenSourceRail aims for simple construction, low whole-life cost and high passenger throughput. This study keeps all permanent magnets, suspension/guidance coils and their controls on the train. The ordinary guideway is a concrete beam with attached passive steel facings. Powered launch and receiving equipment belongs to separate station zones.

**Result: research progress; no integrated suspension or replacement train configuration adopted.** {summary['solved_physical_candidates']} physical proposals were executed through a new transverse finite-element evaluator, with counted stock, material-replacement mass feedback and explicit curve/attachment checks. The six-car, 17 m Baghdad context remains: 120 normal passengers per car, 14,400 passengers/hour/direction and 180-second headway.

[Project ethos](../../../README.md) · [Earlier carrier/beam interpretation](../design-search-interpretation.md)

[Machine-readable results](summary.json) · [Numerical method benchmarks](method-benchmarks.json) · [Publication integrity](manifest.json) · [Source and experiment plan](plan.md) · [References and applicability](references.json) · [BOM](bom.json) · [Assembly/measurement plan](assembly.json)

![Selected local magnetic coupon](section.svg)

## What was compared

A retains an unresolved separate-guidance reference. B asks whether the finite facing and onboard pole geometry provide useful shared alignment. C adds a counted onboard shunt winding. D adds counted compliant-carrier stock. Each has narrow/wide facing variants; a segmented-PM comparison and three B revisions investigate magnetisation, overlap, module length, pole area and ferrite thickness. Unknown installed equipment remains unknown, so these are stock comparisons rather than complete cost or vehicle-mass rankings.

| Sample | Known onboard stock, t/car | Reference lift, N/module | 1.3 AW3 material-floor demand, N/module | Numerical state |
|---|---:|---:|---:|---|
{chr(10).join(rows)}

The reference point is 12 mm gap, 20°C and zero coil current, for one local two-pole module on one facing bank. There are 24 such modules per car. The material floor replaces only the canonical counted support-module stock, retaining all other allocations and propulsion stock. Anchors, retention, wiring, protection and complete cooling/carrier equipment prevent a complete installed mass, CG, inertia or price from being claimed.

## Selection and limits

The declared policy selected **{chosen_name}** for a next experiment: {candidate_link}. It weighs reference support ratio and counted onboard stock, retaining Pareto alternatives. It does not minimise complete installed cost; that quantity is unknown. The independent integrated-selection gate selected **no candidate**. Selection is reproducible across these bounded samples, with no global optimum claim.

The field solves use an explicit provisional constant-permeability steel assumption, finite transverse width and infinite travel length. The same selected physical geometry also receives a retained nonlinear-material sensitivity calculation. Neither material hypothesis is a proven universal force bound. Mesh, boundary, contour and derivative checks have separate dispositions in the raw records. A numerically converged field is not a measured material model. Three-dimensional ends, joints, demagnetisation correlation, saturation, magnetic drag, eddy/hysteresis loss, roll, multiple supports and faults still need work. Longitudinal invariance in a 2D equation does not establish zero travel drag.

The map-bound control analysis is **{summary['controls']['execution_status']}**. Its exact disposition is in `summary.json`. A zero-current force balance, when present inside a valid map, still requires active stabilisation. Nonconverged or unresolved derivative maps receive no equilibrium or control credit. Checked point forces may bracket a necessary load balance over two sampled gaps; those intervals are reported separately and do not establish an equilibrium or stability. The centred map tangent is not a finite-displacement guidance demonstration; additional ±6 mm points at 50°C are retained separately. The material-temperature samples do not establish a repeated hot-weather thermal equilibrium. Zero mean current is not zero RMS heating. An added resistor winding cannot supply static stability; useful damping requires validated signed flux gradients, inductance, resistance and thermal duty. The C reference point has zero shunt current and receives no passive-damping credit.

## Manufacturing, route and next test

The simple steel-facing reference uses factory datums and static shim adjustment, with final survey after beam placement. Magnetic attraction loads the underside facings downward, through tensile attachments into the concrete. The attachment screen calculates demands and simple strip bending; anchor/concrete capacity and fatigue remain open. Capture, emergency braking and parking remain separate functions.

Short blocks attached to one rigid 17 m frame retain that frame's curve error. The D stock can only receive independent-carrier geometry credit if its required yaw and translation can actually be supplied. The 150/250/500/1,000 m radius cases are explicit route alternatives, not adopted changes to Baghdad. Lower speed or closer stations cannot repair inadequate stationary lift. Gravity assistance is a later route comparison and supplies no net energy on a return to the same elevation.

Next, correlate one representative onboard assembly against a finite steel-faced test section: lift, lateral/roll stiffness, coil authority, signed flux linkage, damping, drag and stationary hot-weather heat. Use the recorded datum, stock and measurement plan. No physical test has been executed by this campaign. Native coupon execution: **{native_record['execution_status']}**. {native_links}

The native export is one module and one same-length steel-facing coupon. It contains actual counted conductor legs/end turns and magnet blocks; it is not a complete train, concrete beam, carrier installation or manufacturing release.

## Reproduce

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m engineering.passive_suspension.campaign run --output build/passive-suspension/replay
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m engineering.passive_suspension.campaign verify --output build/passive-suspension/replay
.venv/bin/python -m pytest -q engineering/passive_suspension/tests
```

The immutable registry resumes only exact candidate, source, environment and settings identities. Use a fresh output directory after source/specification changes. Publication verifies source bindings and retained outputs; numerical execution and physical acceptance stay separate.

Campaign `{summary['campaign_id']}`. All engineering acceptance, adoption and physical-release flags remain false.
'''


def publish(source, destination, *, export_native=True):
    source,destination=Path(source),Path(destination)
    campaign.verify(source)
    if destination.exists():raise ValueError('Publish to a new owned directory')
    destination.mkdir(parents=True)
    for path in sorted(source.rglob('*')):
        if path.is_symlink():raise ValueError('Ordinary source artifacts required')
        if path.is_file():
            target=destination/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,target)
    summary=json.loads((source/'summary.json').read_bytes())
    selected=summary['next_experiment']['selected_candidate_id']
    if selected is None:raise ValueError('A defined next-experiment coupon is required')
    value=json.loads((destination/'geometry'/(selected+'.json')).read_bytes())
    definition=geometry.native_definition(value)
    definition['candidate_id']=selected
    (destination/'native-definition.json').write_bytes(encoded(definition))
    native_record=dict(execution_status='not-run',**FLAGS)
    if export_native:
        receipt=native.generate(destination/'native-definition.json',destination/'native',campaign.ROOT)
        if receipt.get('fcstd_reopened') is not True or receipt.get('step_reopened') is not True:
            raise ValueError('Native CAD must be actually reopened')
        native_record=dict(execution_status='executed',receipt=receipt,**FLAGS)
    (destination/'native-execution.json').write_bytes(encoded(native_record))
    bom=dict(candidate_id=selected,scope=definition['scope'],stock_parts=value['stock_parts'],
             stock_quantities=value['stock'],unknown_installed_inventory=value['unknown_installed_inventory'],
             installed_mass_kg=None,installed_cost=None,**FLAGS)
    (destination/'bom.json').write_bytes(encoded(bom))
    assembly=dict(candidate_id=selected,operations=[
        dict(id='facing-datum',action='Fixture and survey passive steel underside; adjust static shims after beam placement',
             depends_on=['anchor/concrete design','beam survey'], acceptance='held'),
        dict(id='module-build',action='Install magnet blocks, pole shoes, return yoke and insulated winding cassette',
             depends_on=['retention detail','insulation/leadout design','temperature limits'], acceptance='held'),
        dict(id='insert-and-capture',action='Define lifting, insertion and removal path with independent fixed retention',
             depends_on=['finite 3D envelope','capture loads','magnet attraction handling'],acceptance='held'),
        dict(id='bench-correlation',action='Measure force/torque, signed linked flux, coil R/L, temperatures, gaps and travel losses',
             depends_on=['calibrated instruments','approved fixture loads','authenticated material specimens'],acceptance='held')],
        datums=geometry.factory_datums(value),physical_tests_executed=False,**FLAGS)
    (destination/'assembly.json').write_bytes(encoded(assembly))
    (destination/'references.json').write_bytes(encoded(REFERENCES))
    (destination/'section.svg').write_text(diagram(value))
    (destination/'README.md').write_text(readme(summary,native_record))
    (destination/'plan.md').write_text('''# Bounded specialist campaign

The system coordinator composes physical candidates, sources, mass feedback, deterministic jobs and publication. Magnetics owns a transverse P1 finite-element evaluator, analytical fixtures and mesh/domain checks. Controls owns map-bound equilibria, finite-RL actuation, RMS heating and reciprocal shunt diagnostics. Mechanical owns exact stock, curve overlap, tensile facing attachments, compliant-mount bounds and assembly datums. A separate specialist reviews integration; only the coordinator publishes.

The four work packages are implemented and tested. Numerical workers evaluate ordinary samples without creating agent conversations for each solve. The campaign has at most 12 physical candidates, one sequential numerical worker, bounded mesh nodes and at most 1,000 map solves. Trials, refused geometry and unresolved derivatives remain visible. Interrupted completed evaluations are cached only by exact immutable identities. Shared source work was developed in separate Git worktrees.

Completed digital work does not complete the existing physical qualification programme. Next work is finite-length/solid-steel nonlinear correlation, complete installed equipment, multiaxis/multisupport control, stiffness/thermal/mass feedback, then full formation, route and fault confirmation. The representative bench test is planned and unexecuted; supplier/site/material evidence remains held. No unattended agent is authorised to alter acceptance or manufacturing release.
''')
    files={p.relative_to(destination).as_posix():sha256(p.read_bytes()).hexdigest()
           for p in sorted(destination.rglob('*')) if p.is_file()}
    manifest=dict(schema='osr-passive-suspension-publication/1',candidate_id=selected,
        campaign_id=summary['campaign_id'],source_sha256=summary['source_sha256'],files_sha256=files,**FLAGS)
    manifest['publication_id']=identity(manifest)
    (destination/'manifest.json').write_bytes(encoded(manifest))
    return verify(destination)


def verify(destination):
    destination=Path(destination)
    manifest=json.loads((destination/'manifest.json').read_bytes())
    if manifest['publication_id']!=identity({k:v for k,v in manifest.items() if k!='publication_id'}):
        raise ValueError('Publication manifest identity differs')
    if any(manifest.get(flag) is not False for flag in FLAGS):raise ValueError('Research cannot assert acceptance')
    actual={p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if actual!=set(manifest['files_sha256']):raise ValueError('Publication file set differs')
    for name,expected in manifest['files_sha256'].items():
        relative=Path(name);path=destination/relative
        if relative.is_absolute() or '..' in relative.parts or path.is_symlink() or sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Publication artifact differs: '+name)
    campaign.verify(destination)
    summary=json.loads((destination/'summary.json').read_bytes())
    if manifest['campaign_id']!=summary['campaign_id'] or manifest['candidate_id']!=summary['next_experiment']['selected_candidate_id']:
        raise ValueError('Publication selection/campaign differs')
    value=json.loads((destination/'geometry'/(manifest['candidate_id']+'.json')).read_bytes())
    expected_definition=geometry.native_definition(value)|dict(candidate_id=manifest['candidate_id'])
    if json.loads((destination/'native-definition.json').read_bytes())!=expected_definition:
        raise ValueError('Native coupon does not derive from selected physical geometry')
    execution=json.loads((destination/'native-execution.json').read_bytes())
    if execution['execution_status']=='executed':
        receipt=json.loads((destination/'native/native-cad.json').read_bytes())
        if receipt!=execution['receipt'] or receipt['input_sha256']!=sha256((destination/'native-definition.json').read_bytes()).hexdigest():
            raise ValueError('Native CAD does not match the selected coupon')
        for name,expected in receipt['files_sha256'].items():
            if sha256((destination/'native'/name).read_bytes()).hexdigest()!=expected:raise ValueError('Native export differs')
    return dict(verified=True,campaign_id=manifest['campaign_id'],publication_id=manifest['publication_id'],**FLAGS)
