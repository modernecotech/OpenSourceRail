"""Research publication for named NdFeB arrays and lighter equipment scenarios."""
from copy import deepcopy
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import shutil

from engineering.design_search.contracts import FLAGS,encoded,identity
from engineering.factory_examples import native
from . import campaign, magnets


def sources():
    root=campaign.ROOT
    extra=[Path(__file__),Path(native.__file__),Path(native.__file__).with_name('models.py')]
    return campaign.sources()|{p.resolve().relative_to(root).as_posix():sha256(p.read_bytes()).hexdigest() for p in extra}


def section(value):
    """Actual transverse stock with rotating magnetisation arrows; no field art."""
    scale=1200.;ox=460.;oz=190.;items=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="390" viewBox="0 0 920 390">',
        '<rect width="920" height="390" fill="#f5f7fa"/>',
        '<defs><marker id="arrow" markerWidth="5" markerHeight="5" refX="3" refY="2" orient="auto"><path d="M0 0L4 2L0 4Z" fill="white"/></marker></defs>',
        '<g font-family="sans-serif" fill="#17324a">',
        '<text x="24" y="31" font-size="21">NdFeB transverse Halbach research coupon</text>',
        '<text x="24" y="58" font-size="14">Magnetisation rotates across the train; travel is out of the page</text>']
    for q in value['regions']:
        y0,y1,z0,z1=q['bounds_yz_m'];mat=q['material']
        colour='#657f92' if mat=='steel' else '#e29b35' if mat=='copper' else '#c0c8ce' if mat=='aluminium' else '#354e9b'
        x,y,w,h=ox+scale*y0,oz-scale*z1,scale*(y1-y0),scale*(z1-z0)
        items.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{colour}" stroke="#283a4c"><title>{escape(q["id"])}</title></rect>')
        by,bz=q.get('Br_y_T',0),q.get('Br_z_T',0);m=(by*by+bz*bz)**.5
        if m:
            length=min(w,h)*.34;cx,cy=x+w/2,y+h/2
            dx,dy=length*by/m,-length*bz/m
            items.append(f'<path d="M{cx-dx:.3f} {cy-dy:.3f}L{cx+dx:.3f} {cy+dy:.3f}" stroke="white" stroke-width="1.5" marker-end="url(#arrow)"/>')
    items += [f'<text x="24" y="296" font-size="15">{escape(value["sample_id"])} · {escape(value["grade_id"])} · 12 mm reference gap</text>',
        '<text x="24" y="322" font-size="14">Blue: actual rotating PM blocks · Orange: counted winding windows · Grey: passive facing/backing</text>',
        '<text x="24" y="348" font-size="13">One bank coupon. Matching concrete, retention, qualified winding and complete installed vehicle remain open.</text>',
        '<text x="24" y="373" font-size="13">Arrows show prescribed magnetisation; this is not a measured flux plot or an operating acceptance.</text>',
        '</g></svg>']
    return '\n'.join(items)+'\n'


def readme(summary,workers,body,climates,native_record):
    selected=summary['next_experiment']['selected_candidate_id']
    report=next(r for r in summary['comparisons'] if r['candidate_id']==selected)
    value=next(v for v in workers['values'].values() if v['physical_id']==report['magnet_id'])
    magnetic_rows=[]
    for name in ('F-iron-equal','N42-iron-equal','N42-H4','N42-H8','N35-H8','N35-H8-half-no-yoke','N35-H8-quarter-no-yoke'):
        row=next((r for r in workers['rows'] if r['sample_id']==name and r['gap_m']==.012 and r['temperature_C']==80. and r['execution_status']=='executed'),None)
        if row is None:continue
        v=workers['values'][name];raw=row['raw_result'];q=campaign.field_quality(v,raw)
        magnetic_rows.append(f'| {name} | {v["stock"]["train_known_mass_kg_per_car"]/1000:.3f} | {raw["F_z_N"]/1000:.3f} | {q["recoil_margin_A_per_m"]/1000:.1f} | {"usable point" if q["joint_point_usable"] else "held / failed screen"} |')
    frames='\n'.join(f'| {c["id"]} | {c["counted_material_mass_kg"]:,.1f} | {c["counted_material_mass_kg"]-c["removed_counted_frame_kg"]:+,.1f} |' for c in body['chassis'])
    al=next(c for c in body['chassis'] if c['id']=='6082-T6-deep-stringers')
    bounds=report['hot_support_bounds'];quality=report['hot_field_quality']
    specific=next(h for h in climates['candidates'] if h['id']=='bus-ul700-electric-two')
    authority=workers['refinements']['authority']
    loads={l['name']:l['total_kWthermal'] for l in climates['loads']}
    native_links=('[FreeCAD](native/model.FCStd) · [STEP](native/model.step) · [Actual reopen/volume receipt](native/native-cad.json)'
                  if native_record['execution_status']=='executed' else 'Native export explicitly not run.')
    return f'''# Neodymium Halbach arrays and lighter vehicle equipment

OpenSourceRail aims for simple construction, low whole-life cost and high passenger throughput. This campaign investigates **named neodymium grades, genuine rotating Halbach arrays, aluminium-extrusion frames and lighter HVAC/doors/windows** together. All permanent magnets and suspension/guidance coils stay on the train; ordinary concrete guidebeams carry passive steel facings. Station propulsion remains a separate interface.

**Research result: useful magnetic and mass-reduction leads; no integrated train adopted.** The study retains **14 magnetic geometries, 36 checked operating points and 98 composed vehicle alternatives**. Material, numerical, control, thermal and physical-qualification states remain separate. The six-car, 17 m case keeps120 normal/160 AW3 passengers per car, four1.4x2.1m doors and14,400 passengers/hour/direction at180-second headway.

[Project ethos](../../../README.md) · [Plan](plan.md) · [Complete comparison](summary.json) · [Magnetic worker](magnetic-worker.json) · [Bounded refinements](refinements.json) · [Aluminium/door/glazing study](equipment.json) · [HVAC heat and equipment study](HVAC.json) · [Integrity manifest](manifest.json)

![Actual rotating-array geometry](halbach-section.svg)

## Neodymium was a new matched comparison

The retained earlier Halbach implementations use ferrite in station-propulsion coupons; the previous passive-facing campaign used a three-piece tilted-pole perturbation. Neither supplies a named-grade NdFeB transverse comparison. The new4/8-segment arrays complete a full magnetic rotation across the vehicle, with equal-volume controls, smaller-volume revisions, iron-backed and no-yoke alternatives. Independent analytical/strong-side reversal tests check that the implementation is an actual Halbach arrangement.

Arnold N42SH and N35UH data distinguish published minimum remanence/coercivity from typical density and temperature coefficients. Named chemistry, density and source hashes are retained. The frozen field solver's legacy internal recoil branch name is`ferrite`; an explicit adapter supplies the actual NdFeB laws and creates no extra ferrite stock. Manufacturer curves and our linear-recoil interpolation do not replace batch measurements. [Material/source declarations](magnetic-worker.json).

| 12 mm,80°C comparison | Known support stock, t/car | Upward force,kN/module | Recoil screen margin,kA/m | Point disposition |
|---|---:|---:|---:|---|
{chr(10).join(magnetic_rows)}

The full N35UH eight-segment array has substantial capacity, but over-supports the unchanged-body mean load even at20mm in the cold sample. Capacity is not equilibrium. The smaller no-yoke proposal reduces PM volume from0.012 to0.006m³/module; its listed support stock is **{value['stock']['train_known_mass_kg_per_car']/1000:.3f}t/car**, including copper and aluminium backing. Coating, adhesive, retention, sensors, protection and complete cooling remain unknown. The separate retained propulsion band is still counted; a transverse support array does not substitute for the longitudinal station-motor field.

## Lighter complete-car comparisons

Only actual canonical support stock, exact frame IDs and eligible500kg door/500kg fixed-glazing/800kg HVAC ancestor allowances are replaced. The5.2t equipped-body aggregate and already-consumed frame budgets are never subtracted again. All other stock, propulsion, reserve and unlocated allocations stay. Hardware estimates and allocation substitutions are not weighed savings.

The declared next **magnetic experiment** uses`{report['sample_id']}` in the`{report['mode']}` comparison context. Its AW3 material/allocation scenario is **{report['comparison_aw3_mass_band_kg'][0]/1000:.3f}–{report['comparison_aw3_mass_band_kg'][1]/1000:.3f}t/car**, with the HVAC installation band included once. Complete installed mass, CG, inertia and cost remain unknown.

At80°C the sampled force is **{bounds[1]['force_N_per_module']/1000:.3f}kN/module** against **{bounds[1]['required_N_per_module']/1000:.3f}kN** at the upper mass scenario. The observed mesh/domain/air-contour force spread is **{quality['observed_force_variation_N']:.1f}N/module**. That variation prevents a marginal nominal ratio from becoming a robust reserve claim: support states at the low/high installation scenarios are **{bounds[0]['state']} / {bounds[1]['state']}**. This estimate also excludes physical material, installation and3D uncertainty.

## Aluminium extrusions are quantified

The comparison replaces260 exact old frame-stock IDs representing65 members, approximately **{al['removed_counted_frame_kg']:,.1f}kg/car**. Panels, magnetic collectors, existing hardpoints and separately counted fasteners remain. New profiles match declared section-stiffness screens and include130 end joints,520 M8 bolts/crush sleeves,260 gussets, isolation/bond material and24 load spreaders.

| Aluminium frame proposal | Counted stock,kg/car | Change from removed frame,kg/car |
|---|---:|---:|
{frames}

Aluminium's lower density does not guarantee a lighter equal-stiffness frame. These bounded proposals are heavier after the larger sections and joints are counted. The revised6082 spreader passes its scalar elastic screen; global body shear/torsion, bracing, compression, fatigue, weld/repair strength, interfaces and deep-profile clearances remain open. Composed roof loads are recalculated for the changed vehicle mass. Extrusion member positions preserve their own attachment datums. A broader structural redesign may still improve the outcome; this is not a proof that every aluminium chassis is heavier.

## HVAC, doors and windows can be redesigned

The lighter door/window takeoff retains all four openings and includes skins, cores, frames, seals, bonds, glass/PVB and supplier-reference operators. Mechanism weights41/46kg are not complete door weights or confirmed1.4m installations. Proposed solar-control6.76mm laminated glazing reduces material and solar-load scenarios; impact, fire, scratch, retention and emergency provisions remain unqualified. No polycarbonate saving is credited without an actual qualified construction.

Two current UL700EM electric-compressor bus packages total **{specific['package_hardware_mass_range_kg_per_car'][0]:g}kg** and66kW nominal thermal capacity. The explicit installation scenario is **469–624kg/car**, leaving a useful target below the inherited800kg allowance. Rail adaptation, full50°C capacity/power maps, fresh-air/filter pressure, failed-unit duty and possible recovery hardware remain unknown. Their400V AC supply also needs a counted compatible train supply; low-voltage auxiliary current is not compressor power.

At the retained indoor conditions and ventilation scenario, the one-car50°C AW2 load is **{loads['AW2-50C-clear']:.1f}kW thermal** with clear glazing, **{loads['AW2-50C-solar-control']:.1f}kW** with proposed solar-control glass and **{loads['AW2-50C-solar-control-recovery']:.1f}kW** with explicitly assumed recovery plus fan power. The humid AW3 closed stationary case reaches **{loads['AW3-50C-humid-closed-stationary']:.1f}kW**. Nominal cooling capacity, electrical input and ambient derating are different quantities. Passenger heat and fresh-air demand do not fall with structural mass; reducing ventilation receives no comfort/compliance credit.

## What is still blocking

The retained0.55 winding-fill screen is not met by the counted packs. The half-volume+20A experiment adds only **{authority['delta_F_z_N']:.1f}N/module**, while reaching **{authority['current_density_A_per_mm2']:g}A/mm²** and **{authority['DC_copper_power_W']:.1f}W/module** DC copper heat. It is a one-sided observation, not a validated derivative, controller or repeated thermal duty. A useful segmented/differential trim winding and its installation must be designed before motion credit.

Passive lateral alignment, roll/multisupport stability, fault handling and finite-end/joint magnetic drag remain unresolved. A matching concrete cross-section and attachment load path have not been generated; existing beam mass/capacity is not transferred. The ordinary guideway remains passive. No route/speed reduction or passenger-capacity cut is adopted to obtain a passing score.

The native package is **one selected magnetic coupon and same-length steel facing**, not a complete car, aluminium chassis or concrete beam. {native_links}

## Reproduce

Run the frozen magnetic worker with`magnets.study(output=...)` for32 checked points. Copy the tracked`engineering/vehicle_optimisation/recipes/refinement_recipe.py` into that private output directory and execute it for the three bounded refinements. Run`magnets.evaluate_reference(N35-H8,temperature_C=80,settings={{'steel_model':'nonlinear_repo_proxy'}})` for the remaining confirmation. Every raw input, source and operating point is retained here; production ingestion rejects relabelled temperatures/gaps, altered recipes and missing/duplicate coverage.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -q engineering/vehicle_optimisation/tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m engineering.vehicle_optimisation.campaign verify --output docs/design-engine/vehicle-optimisation
```

The verifier rebuilds the derived mass/thermal/structural reports and selections from the current sources and retained field primitives without rerunning FEM. Digital progress does not complete physical qualification. Campaign`{summary['campaign_id']}`; all adoption and engineering-release flags remain false.
'''


def publish(source,destination,*,export_native=True):
    source,destination=Path(source),Path(destination);before=sources();campaign.verify(source)
    if destination.exists():raise ValueError('Publish to a new owned directory')
    destination.mkdir(parents=True)
    for p in source.rglob('*'):
        if p.is_symlink():raise ValueError('Ordinary input files required')
        if p.is_file():
            target=destination/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    summary=json.loads((destination/'summary.json').read_bytes())
    workers=campaign.load_workers(destination/'magnetic-worker.json',destination/'refinements.json',destination/'nonlinear-confirmation.json')
    report=next(r for r in summary['comparisons'] if r['candidate_id']==summary['next_experiment']['selected_candidate_id'])
    value=next(v for v in workers['values'].values() if v['physical_id']==report['magnet_id'])
    definition=dict(id='OSR-NDFEB-'+report['candidate_id'][:12],candidate_id=report['candidate_id'],
        geometry_sha256=value['physical_id'],parts=deepcopy(value['stock_parts']),
        modelled_material_mass_kg=sum(p['mass_kg'] for p in value['stock_parts']),
        scope='One local selected magnet/control-winding/facing coupon; no complete vehicle/chassis/concrete or installed acceptance',
        retain_native_tessellation=True,interference_roles=[],**FLAGS)
    (destination/'native-definition.json').write_bytes(encoded(definition))
    receipt=dict(execution_status='not-run',**FLAGS)
    if export_native:
        result=native.generate(destination/'native-definition.json',destination/'native',campaign.ROOT)
        if not result['fcstd_reopened'] or not result['step_reopened']:raise ValueError('Native reopen evidence required')
        receipt=dict(execution_status='executed',receipt=result,**FLAGS)
    (destination/'native-execution.json').write_bytes(encoded(receipt))
    body=json.loads((destination/'equipment.json').read_bytes());climates=json.loads((destination/'HVAC.json').read_bytes())
    (destination/'halbach-section.svg').write_text(section(value))
    (destination/'README.md').write_text(readme(summary,workers,body,climates,receipt))
    (destination/'plan.md').write_text('''# Coordinated next design work

Keep one explicit magnetic/equipment/frame identity. Magnetics developed named NdFeB grades and full rotating transverse arrays; mechanical developed counted extrusions, joints, doors and glazing; thermal developed occupied HVAC duty and supplier-scope comparisons. The coordinator composes disjoint stock and inherited-budget replacements, including mass uncertainty, and publishes one source-bound package. Independent specialist review challenged raw operating-point labels, mass scope, member poses, physical-vs-model identity and payload consistency. Reviewers followed read-only instructions; no independent operating-system sandbox is asserted.

Next: revise and count segmented/differential control windings with a justified insulation/fill specification; map force/current/gap/lateral/roll and repeated hot duty; close installed retention/cooling/supply mass. Extend finite-length field and measured material/drag correlation. Compare actual extrusion/bracing/joint load paths and fullbody behaviour; qualify glazing/door fit and egress. Obtain50°C HVAC capacity/power/air-pressure maps, count rail supply/adaptation and recovery hardware, and test occupied stationary/door cycles. Only then compose matching concrete facings/anchors, complete mass/CG/inertia and coupled formation/route/fault trajectories. Existing576 physical tasks retain their own evidence requirements.
''')
    if sources()!=before:raise ValueError('Publication sources changed during native/render work')
    files={p.relative_to(destination).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(destination.rglob('*')) if p.is_file()}
    manifest=dict(schema='osr-ndfeb-lightweight-publication/1',source_sha256=before,files_sha256=files,
        campaign_id=summary['campaign_id'],candidate_id=report['candidate_id'],**FLAGS)
    manifest['publication_id']=identity(manifest);(destination/'manifest.json').write_bytes(encoded(manifest))
    return verify(destination)


def verify(output):
    output=Path(output);manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['publication_id']!=identity({k:v for k,v in manifest.items() if k!='publication_id'}) or manifest['source_sha256']!=sources():
        raise ValueError('Publication source/identity differs')
    if any(manifest.get(k) is not False for k in FLAGS):raise ValueError('Research cannot be accepted')
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if actual!=set(manifest['files_sha256']):raise ValueError('Publication inventory differs')
    for name,digest in manifest['files_sha256'].items():
        path=output/name
        if Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink() or sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Publication payload differs: '+name)
    campaign.verify(output)
    summary=json.loads((output/'summary.json').read_bytes());definition=json.loads((output/'native-definition.json').read_bytes())
    if manifest['campaign_id']!=summary['campaign_id'] or manifest['candidate_id']!=summary['next_experiment']['selected_candidate_id'] or definition['candidate_id']!=manifest['candidate_id']:
        raise ValueError('Mixed selected identities')
    workers=campaign.load_workers(output/'magnetic-worker.json',output/'refinements.json',output/'nonlinear-confirmation.json')
    report=next(r for r in summary['comparisons'] if r['candidate_id']==manifest['candidate_id'])
    value=next(v for v in workers['values'].values() if v['physical_id']==report['magnet_id'])
    if definition['parts']!=value['stock_parts']:raise ValueError('Native stock differs from selected geometry')
    execution=json.loads((output/'native-execution.json').read_bytes())
    if execution['execution_status']=='executed':
        receipt=json.loads((output/'native/native-cad.json').read_bytes())
        if receipt!=execution['receipt'] or receipt['input_sha256']!=sha256((output/'native-definition.json').read_bytes()).hexdigest():
            raise ValueError('Native receipt/input differs')
        for name,digest in receipt['files_sha256'].items():
            if sha256((output/'native'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Native file differs')
    return dict(verified=True,campaign_id=summary['campaign_id'],publication_id=manifest['publication_id'],**FLAGS)
