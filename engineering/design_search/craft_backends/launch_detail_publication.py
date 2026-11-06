"""Publish selected existing launch CAD/FEM evidence; never execute a solver.

Native results keep their original seals and evaluation contexts. The compact
public package is a selection, not the complete private execution inventory.
"""
from copy import deepcopy
from pathlib import Path
import argparse,csv,io,json,shutil
from . import native,identity
from . import launch_assembly as assembly,launch_component_fem as fem

ROOT=Path(__file__).resolve().parents[3]
SOURCE='engineering/design_search/craft_backends/launch_detail_publication.py'
DATA='engineering/outline/data/china-supply-20261104.json'
OUTPUT='docs/design-engine/launch-detail'
FLAGS=assembly.FLAGS
CASES=('low','base','high')


def _sealed(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Record seal differs: '+key)


def reconcile(cad_record,fem_record):
    """Require exact physical/interface agreement, retaining a documented advisory label difference."""
    assembly.validate(cad_record);_sealed(fem_record,'assembly_definition_id')
    for key in ('candidate_id','component_geometry_id','physical_definition','component_geometry','fem_interface'):
        if cad_record.get(key)!=fem_record.get(key):raise ValueError('Mixed CAD/FEM '+key)
    a,b=deepcopy(cad_record),deepcopy(fem_record)
    for record in (a,b):
        record.pop('assembly_definition_id');record.get('necessary_screens',{}).pop('screening_factor_basis',None)
    if a!=b:raise ValueError('Undeclared evaluation-context difference')
    return dict(physical_geometry_identical=True,load_interface_identical=True,
        cad_assembly_definition_id=cad_record['assembly_definition_id'],fem_assembly_definition_id=fem_record['assembly_definition_id'],
        retained_context_difference='CAD record adds an advisory explanation of the research load multiplier; original FEM snapshot remains unchanged',
        source_records_rewritten=False)


def sources(root=ROOT):
    root=Path(root)
    return {SOURCE:native.digest(__file__),DATA:native.digest(root/DATA),
        assembly.SOURCE:native.digest(assembly.__file__),fem.SOURCE:native.digest(fem.__file__),
        'engineering/design_search/craft_backends/native.py':native.digest(native.__file__),
        'engineering/design_search/craft_backends/tools.json':native.digest(native.LOCK)}


def costing(value,data,quantity=1):
    """Bounded factory estimate from dated proxy stock prices, not a quotation."""
    assembly.validate(value);_sealed(data,'dataset_id')
    if type(quantity) is not int or not 1<=quantity<=100000:raise ValueError('Committed batch quantity1..100000 required')
    observations={r['id']:r for r in data['observations']}
    ids={'steel':'cn-nbs-20261021-31-q235-plate','bronze_proxy':'cn-nbs-20261021-31-copper-1'}
    fx=data['fx_reference']['quote_per_base']
    if fx<=0:raise ValueError('Positive declared CNY/USD reference required')
    for key in ids.values():
        row=observations[key]
        if row['advertised_price']['currency']!='CNY' or row['advertised_price']['unit']!='metric_tonne':raise ValueError('Explicit source price units required')
    raw={kind:observations[oid]['advertised_price']['low']/1000/fx for kind,oid in ids.items()}
    masses={m:sum(value['part_measures'][p['id']]['nominal_material_mass_kg'] for p in value['entities'] if p['material']==m) for m in value['materials']}
    hours={'frame-cut-jig-weld':[3.,6.,12.],'clevis-bore-fit':[1.5,3.,6.],
           'wheels-axles-bushes-collars':[4.,8.,16.],'fastener-finish':[.5,1.,2.],
           'guards-finish':[1.,2.,4.],'assembly-dimensional-function-QA':[2.,4.,8.]}
    assumptions=dict(steel_grade_form_premium_usd_per_kg=[.30,.80,2.],
        bronze_tin_alloy_stock_conversion_premium_usd_per_kg=[3.,7.,15.],
        imported_stock_landing_usd_per_kg=[.15,.35,.80],steel_cut_yield=[.98,.92,.84],bronze_cut_yield=[.90,.75,.60],
        loaded_labour_usd_per_h=[5.,9.,16.],machine_cash_hours=[4.,8.,16.],machine_cash_usd_per_h=[8.,15.,30.],
        dimensional_material_and_weld_QA_usd_each=[50.,150.,500.],factory_overhead_fraction=[.10,.20,.35],
        one_batch_fixture_tooling_usd=[200.,600.,1800.],process_labour_hours_per_unit=hours)
    cases={}
    for i,name in enumerate(CASES):
        steel=masses[assembly.STEEL]/assumptions['steel_cut_yield'][i]*(raw['steel']+assumptions['steel_grade_form_premium_usd_per_kg'][i]+assumptions['imported_stock_landing_usd_per_kg'][i])
        bronze=masses[assembly.BRONZE]/assumptions['bronze_cut_yield'][i]*(raw['bronze_proxy']+assumptions['bronze_tin_alloy_stock_conversion_premium_usd_per_kg'][i]+assumptions['imported_stock_landing_usd_per_kg'][i])
        labour_hours=sum(h[i] for h in hours.values());labour=labour_hours*assumptions['loaded_labour_usd_per_h'][i]
        machine=assumptions['machine_cash_hours'][i]*assumptions['machine_cash_usd_per_h'][i]
        qa=assumptions['dimensional_material_and_weld_QA_usd_each'][i]
        direct=steel+bronze+labour+machine+qa;overhead=direct*assumptions['factory_overhead_fraction'][i]
        tooling=assumptions['one_batch_fixture_tooling_usd'][i]/quantity
        cases[name]=dict(steel_stock_usd=steel,bronze_proxy_stock_usd=bronze,labour_hours=labour_hours,labour_usd=labour,
            machine_cash_usd=machine,QA_usd=qa,overhead_usd=overhead,fixture_allocation_usd=tooling,
            factory_usd_per_shuttle=direct+overhead+tooling,committed_batch_factory_usd=(direct+overhead)*quantity+assumptions['one_batch_fixture_tooling_usd'][i])
    result=dict(schema='osr-launch-detail-factory-estimate/1',candidate_id=value['candidate_id'],currency='USD',
        nominal_component_count=value['manufacturing']['nominal_component_count'],nominal_material_region_count=len(value['entities']),
        source_dataset_id=data['dataset_id'],source_observation_ids=ids,source_FX_id=data['fx_reference']['id'],
        stock_proxy_floor_usd_per_kg=raw,nominal_material_masses_kg=masses,committed_quantity=quantity,assumptions=assumptions,cases=cases,
        estimate_class='Calculated Class C factory-gate component estimate; not a supplier quote or installed station cost',
        no_additional_bulk_discount=True,fixed_fixture_counted_once=True,procurement_approved=False,
        price_basis='Dated China wholesale commodity observations; Q235 is only a floor proxy for proposed certified steel. Copper is only a floor proxy for bearing bronze, with explicit tin/alloy/stock-conversion additions.',
        machine_basis='Cash operating proxy including energy/consumables; no duplicated plant capital recovery. Fixture is allocated once after one overhead uplift.',
        exclusions=['Actuator and storage, cables/capstans or hydraulics, complete guideway/station installation',
            'Production-line buildings, financed plant capacity, freight of completed shuttle, duties/tax not in stock landing',
            'Prototype proof/qualification, fatigue/contact testing, supplier grade/fit validation and lifecycle maintenance',
            'Measured labour/routing calibration and unresolved sensor/wiring/grease/weld-detail procurement'],**FLAGS)
    result['cost_estimate_id']=identity(result);return result


def _csv(value):
    fields=('part_id','subassembly','material','stock','quantity','nominal_volume_m3','nominal_mass_kg','tolerances')
    s=io.StringIO(newline='');w=csv.DictWriter(s,fields,lineterminator='\n');w.writeheader()
    for row in value['manufacturing']['bom']:w.writerow({k:row.get(k) for k in fields})
    return s.getvalue()


def summary(cad,fe,contexts,cost,ce):
    levels={}
    for name,row in fe['levels'].items():
        fc=row['fieldcraft'];ccx=row['calculix']
        levels[name]=dict(elements=fc['elements'],nodes=fc['node_count'],
            forward_bore_displacement_m=fc['displacement_at_forward_bore_m'][0],
            sampled_bore_peak_von_mises_Pa=fc['sampled_bore_peak_von_mises_Pa'],
            calculix_global_integration_point_peak_Pa=ccx['integration_point_peak_von_mises_Pa'],
            cross_solver_displacement_relative_difference=row['cross_solver_displacement_relative_difference'],
            force_equilibrium_relative_residual=fc['force_equilibrium_relative_residual'])
    result=dict(schema='osr-launch-detail-dossier-summary/1',candidate_id=cad['candidate_id'],component_geometry_id=cad['component_geometry_id'],
        material_region_count=len(cad['entities']),counted_components=cad['manufacturing']['nominal_component_count'],
        nominal_material_mass_kg=cad['nominal_located_material_mass_kg'],provisional_installed_mass_bound_kg=cad['installed_mass_bound_kg'],
        evaluation_contexts=contexts,load_requirements=cad['requirements'],pin_ear_necessary_screens=cad['necessary_screens'],
        fem_analytical=fe['analytical'],fem_levels=levels,refinement=fe['refinement'],
        cad_checks={name:dict(occurrences=row['occurrences'],exact_brep=row['exact_brep'],native_names_preserved=row['native_names_preserved'],maximum_relative_volume_error=max(p['relative_volume_error'] for p in row['parts'])) for name,row in ce['checks'].items()},
        fem_scope='One ear under80kN distributed half-bore load and rigid-root hypothesis; not the whole shuttle or a contact/weld model',
        unresolved=fe['unresolved']+cad['engineering_holds'],factory_estimate=cost,
        fresh_native_solver_executed=False,physical_design_selected=False,**FLAGS)
    result['summary_id']=identity(result);return result


def readme(value):
    c=value['factory_estimate'];lo,base,hi=[c['cases'][x]['factory_usd_per_shuttle'] for x in CASES]
    return f'''# Detailed station launch shuttle — research assembly

This dossier connects actual parametric CAD, a counted assembly and part-level
factory estimate to a matched structural analysis. It is a separate research
candidate, not an installed propulsion selection or passenger-operating approval.

![Actual dimensioned launch shuttle CAD](assembly.png)

Actual generated CAD: the side guards are shown at 18% opacity to reveal the
running and capture rollers. No exploded/display offsets change part positions.
[Native SolidCraft design](assembly.sc) · [STEP assembly](assembly.step) ·
[Assembly and interfaces](assembly.json) · [Material-region BOM](bom.csv) ·
[Component BOM and routings](manufacturing.json) · [Cost assumptions](factory-cost.json).

## What is detailed

The {value['material_region_count']} material bodies represent {value['counted_components']}
counted nominal components: real hollow frame sections, bored clevis ears and
backplate, a 60 mm pin, positive end caps, separate retaining screws, bushes,
running/capture wheels, axles, crush sleeves, spacers, washers, studs and guards.
Head/shank CAD regions do not become duplicate purchased screws. Frame and
analysis coordinates and rigid transforms are explicit. Finite travel, tool and
removal envelopes, jacking/unloading order, lift-fixture hold, wiring allowance,
fit assumptions, welding routes and inspection operations remain in the assembly.

Nominal located stock mass is **{value['nominal_material_mass_kg']:.2f} kg**.
The **{value['provisional_installed_mass_bound_kg'][0]:.2f}–{value['provisional_installed_mass_bound_kg'][1]:.2f} kg**
component allowance is provisional: threads, fillets, welds, grease, sensors and
flexible wiring are not a complete measured installation. The actuator and
energy store are outside this component scope.

## Engineering feedback changed the design

The previous 40 mm pin had a 2.2–3.4 kNm simply-supported bending envelope under
the 160 kN research requirement. Its nominal 350–541 MPa bending stress could exceed
the declared 355 MPa material proxy even before combining shear. Its valid CAD and
ear calculations remain previous-candidate evidence; it was not approved.

The current candidate uses a 60 mm pin and 220 × 160 × 25 mm ears. The 160 kN load is a
**requirement** from 160,000 kg × 1 m/s², not measured available thrust. Speed and
powered length are unselected. The pin's conservative non-coincident combined
stress envelope is about 123–173 MPa before impact/contact/concentration/fatigue
allowances. The 1.5 multiplier is a revisable research screen, not a railway
proof-test prescription or approved allowable.

![Bore stress samples on the actual ear model](clevis-bore-stress.png)

Native .sc and STEP reopening retain source body names. Independent FreeCAD
reimport loses them to generic product labels; exact volume/centroid/bounds
correspondence is retained separately and does not claim native name retention.

The FEM model evaluates **one ear with 80 kN**, distributed radial half-bore
traction, a rigid root and an uncertified isotropic material hypothesis. Coarse
and fine meshes contain 256 and 1,024 quadratic hex20 elements. FieldCraft and
CalculiX agree in displacement to their printed precision. Two-mesh displacement
change is 0.175%; sampled bore-stress change is 0.902%. These sensitivities do not
establish general mesh independence or physical validation. FieldCraft's sampled
nodal bore stress and CalculiX's global integration-point maximum are different
quantities and must not be treated as matching stress fields.

[Compact numerical results](summary.json) · [Original FEM result seal](fem-evidence.json)

## Calculated factory cost

| One shuttle, committed batch of {c['committed_quantity']} | Low | Base | High |
|---|---:|---:|---:|
| Calculated factory USD/unit | ${lo:,.0f} | ${base:,.0f} | ${hi:,.0f} |

This is a Class C component estimate. It uses dated China commodity proxy floors
plus explicit grade/form or bronze alloy/stock-conversion premiums, cut yield,
landing, 12/24/48 labour-hours, machine cash costs, QA and one overhead uplift.
One batch fixture is counted once; already-wholesale prices receive no extra
blanket discount. Copper is not presented as a bronze quote, nor Q235 as
qualified S355. Labour and process rates are declared estimates. No supplier
quotation, complete factory investment or station installed/lifecycle price is
claimed. The whole actuator, storage, guideway and installation are excluded.

## Open evidence and independent checking

Actual pin contact/clearance/friction, cap bending and thread engagement, weld
and deck flexibility, bolt preload/slip, bearing PV/wear, guideway retention,
fatigue/load reversal, materials, train compression dynamics, jerk, repeated duty,
controls and independent braking remain open. No native tool establishes release.

The CAD and FEM records retain distinct assembly-definition IDs because an
advisory explanation was added after the FEM input snapshot. The complete
physical definitions and load interfaces are identical; both original sealed
records are retained. No old receipt or solver input is patched.

Generate a fresh selected package from existing immutable executions:

```bash
python -m engineering.design_search.craft_backends.launch_detail_publication publish --evidence /path/to/city-cost-and-detail-20261106 --output /path/to/fresh-dossier
python -m engineering.design_search.craft_backends.launch_detail_publication verify --output /path/to/dossier
```

Publication verifies private native evidence before copying selected artifacts.
Public verification checks this selected package and numerical/identity consistency;
it is not a new solve or a replay of every private output. Full immutable logs,
meshes and native outputs remain identified by hashes in the evidence manifests.

Candidate: `{value['candidate_id']}`  
Clevis geometry: `{value['component_geometry_id']}`
'''


def publish(evidence,output=None,*,root=ROOT,quantity=1):
    root=Path(root);evidence=Path(evidence).resolve();output=Path(output or root/OUTPUT).resolve()
    if output.exists():raise ValueError('Fresh dossier directory required; existing evidence is never overwritten')
    cad=assembly.build();fem_source=json.loads((evidence/'mechanical/assembly-contract-r3.json').read_bytes())
    contexts=reconcile(cad,fem_source)
    cv=assembly.verify(evidence/'mechanical/native-r3');fv=fem.verify(evidence/'fem/r3-run01',fem_source)
    if cv['candidate_id']!=cad['candidate_id'] or fv['candidate_id']!=cad['candidate_id']:raise ValueError('Mixed native evidence candidate')
    fe=json.loads((evidence/'fem/r3-run01/result.json').read_bytes())
    cost=costing(cad,json.loads((root/DATA).read_bytes()),quantity)
    ce=json.loads((evidence/'mechanical/native-r3/result.json').read_bytes())
    value=summary(cad,fe,contexts,cost,ce)
    files={'assembly.sc':'mechanical/native-r3/generate/assembly.sc','assembly.step':'mechanical/native-r3/generate/assembly.step',
        'assembly.png':'mechanical/render-r3-cpu01/assembly.png','clevis-bore-stress.png':'fem/r3-bore-stress-samples.png',
        'cad-evidence.json':'mechanical/native-r3/result.json','cad-request.json':'mechanical/native-r3/request.json',
        'fem-evidence.json':'fem/r3-run01/result.json','fem-request.json':'fem/r3-run01/request.json','fem-input.json':'fem/r3-run01/input.json',
        'fem-source-assembly.json':'mechanical/assembly-contract-r3.json','snapshot-request.json':'mechanical/render-r3-cpu01/request.json',
        'snapshot-result.json':'mechanical/render-r3-cpu01/result.json'}
    if sum((evidence/name).stat().st_size for name in files.values())>5*1024**2:raise ValueError('Selected assets exceed5MiB budget')
    output.mkdir(parents=True)
    for name,relative in files.items():
        src=evidence/relative
        if not src.is_file() or src.is_symlink():raise ValueError('Ordinary immutable selected artifact required')
        shutil.copyfile(src,output/name)
    for name,data in [('assembly.json',cad),('manufacturing.json',cad['manufacturing']),('factory-cost.json',cost),('summary.json',value)]:native.write(output/name,data)
    (output/'bom.csv').write_text(_csv(cad));(output/'README.md').write_text(readme(value))
    manifest=dict(schema='osr-launch-detail-publication/1',candidate_id=cad['candidate_id'],component_geometry_id=cad['component_geometry_id'],
        source_sha256=sources(root),native_verification=dict(cad=cv,fem=fv),
        raw_evidence_identity=dict(cad_result_id=cv['evaluation_id'],fem_result_id=fv['result_id']),
        selected_asset_source_sha256={name:native.digest(evidence/relative) for name,relative in files.items()},
        files_sha256={p.name:native.digest(p) for p in sorted(output.iterdir()) if p.is_file()},
        package_scope='Selected actual CAD and compact evidence only; full immutable private native inventory is not copied',
        total_selected_bytes=sum(p.stat().st_size for p in output.iterdir() if p.is_file()),**FLAGS)
    manifest['manifest_id']=identity(manifest);native.write(output/'manifest.json',manifest)
    return manifest


def verify(output=None,*,root=ROOT):
    root=Path(root);output=Path(output or root/OUTPUT)
    m=json.loads((output/'manifest.json').read_bytes());_sealed(m,'manifest_id')
    if m['source_sha256']!=sources(root):raise ValueError('Dossier source epoch differs')
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('Research dossier cannot grant acceptance')
    actual={p.name:native.digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('Selected artifact inventory differs')
    for name,sha in m['selected_asset_source_sha256'].items():
        if actual.get(name)!=sha:raise ValueError('Copied original evidence differs')
    cad=json.loads((output/'assembly.json').read_bytes());old=json.loads((output/'fem-source-assembly.json').read_bytes());contexts=reconcile(cad,old)
    for v in (cad,old):
        if v['candidate_id']!=m['candidate_id'] or v['component_geometry_id']!=m['component_geometry_id']:raise ValueError('Mixed dossier physical identity')
    fe=json.loads((output/'fem-evidence.json').read_bytes());_sealed(fe,'result_id')
    spec=fem.from_assembly(old)
    if json.loads((output/'fem-input.json').read_bytes())!=spec:raise ValueError('Public FEM input differs')
    fr=json.loads((output/'fem-request.json').read_bytes());_sealed(fr,'evaluation_id')
    if fr['input_sha256']!=identity(spec) or fe['evaluation_id']!=fr['evaluation_id']:raise ValueError('FEM evaluation binding differs')
    if fe['analytical']!=fem.analytical(spec) or fe['refinement']!=fem.compare_refinement(fe['levels']):raise ValueError('FEM numerical summary differs')
    cr=json.loads((output/'cad-request.json').read_bytes());_sealed(cr,'evaluation_request_id')
    ce=json.loads((output/'cad-evidence.json').read_bytes());_sealed(ce,'evaluation_id')
    if cr['assembly']!=cad or ce['evaluation_request_id']!=cr['evaluation_request_id']:raise ValueError('CAD evaluation binding differs')
    for record in (ce,fe,fr):
        for key in ('candidate_id','component_geometry_id'):
            if record.get(key)!=cad[key]:raise ValueError('Mixed selected CAD/FEM '+key)
        if any(record.get(key,False) is not False for key in FLAGS):raise ValueError('Native evidence cannot grant release')
    if ce['native_geometry_comparison_passed'] is not True or not all(row['comparison_passed'] for row in ce['checks'].values()):
        raise ValueError('Actual CAD comparison did not pass')
    snapshot=json.loads((output/'snapshot-request.json').read_bytes());sr=json.loads((output/'snapshot-result.json').read_bytes())
    if snapshot['candidate_id']!=cad['candidate_id'] or snapshot['input_sha256']!=actual['assembly.sc'] or sr['png_sha256']!=actual['assembly.png']:
        raise ValueError('CAD image geometry or candidate differs')
    cost=costing(cad,json.loads((root/DATA).read_bytes()),json.loads((output/'factory-cost.json').read_bytes())['committed_quantity'])
    value=summary(cad,fe,contexts,cost,ce)
    if (json.loads((output/'factory-cost.json').read_bytes())!=cost or json.loads((output/'summary.json').read_bytes())!=value
        or json.loads((output/'manufacturing.json').read_bytes())!=cad['manufacturing']
        or (output/'bom.csv').read_text()!=_csv(cad) or (output/'README.md').read_text()!=readme(value)):
        raise ValueError('Recomputed dossier, quantities or cost differs')
    return dict(verified=True,manifest_id=m['manifest_id'],candidate_id=m['candidate_id'],
        selected_package_only=True,fresh_native_solve=False,**FLAGS)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('publish','verify'))
    p.add_argument('--evidence',type=Path);p.add_argument('--output',type=Path,default=ROOT/OUTPUT);p.add_argument('--quantity',type=int,default=1)
    a=p.parse_args(argv)
    if a.command=='publish':
        if a.evidence is None:p.error('publish requires existing immutable --evidence directory')
        result=publish(a.evidence,a.output,quantity=a.quantity)
    else:result=verify(a.output)
    print(json.dumps({k:result[k] for k in ('candidate_id','manifest_id') if k in result}));return 0


if __name__=='__main__':raise SystemExit(main())
