"""Portable selected evidence for the bounded viaduct backend comparison.

Publishing first verifies the complete private execution packages. Public replay
checks the selected records, geometry readbacks, quantities and derived claims;
it neither repeats a native solve nor substitutes for the retained raw meshes.
"""
from copy import deepcopy
from pathlib import Path
import csv,io,json,shutil,struct
from math import isfinite
from engineering.station_rail.common import identity,digest
from . import native,viaduct_cases,viaduct_cad,viaduct_delivery,viaduct_workflow,viaduct_admission
from .cases import FLAGS

ROOT=Path(__file__).resolve().parents[3]
SOURCE='engineering/design_search/craft_backends/viaduct_publication.py'
OUTPUT='docs/design-engine/viaduct-backends'


def load(path):return json.loads(Path(path).read_bytes())


def sealed(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Selected record seal differs: '+key)
    viaduct_admission._unreleased(value)


def inventory(folder):
    folder=Path(folder)
    if any(p.is_symlink() for p in (folder,*folder.parents)) or any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('Ordinary publication files required')
    return {p.relative_to(folder).as_posix():digest(p) for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'manifest.json'}


def stl_bounds(path):
    """Native binary STL coordinates are millimetres, explicitly converted to SI."""
    data=Path(path).read_bytes()
    if len(data)<84:raise ValueError('Native binary STL required')
    count=struct.unpack_from('<I',data,80)[0]
    if not 0<count<=1000000 or len(data)!=84+50*count:raise ValueError('Bounded binary STL triangle coverage differs')
    vertices=[struct.unpack_from('<3f',data,84+50*i+12+12*j) for i in range(count) for j in range(3)]
    if any(not isfinite(c) for v in vertices for c in v):raise ValueError('Finite STL vertices required')
    return count,[[fn(v[k] for v in vertices)*.001 for k in range(3)] for fn in (min,max)]


def selected_numerics(folder,analysis):
    folder=Path(folder);result=load(folder/'result.json');request=load(folder/'request.json');spec=load(folder/'input.json')
    sealed(result,'result_id');sealed(request,'evaluation_id');sealed(spec,'input_id')
    if any(result[k]!=spec[k] or request[k]!=spec[k] for k in ('candidate_id','component_geometry_id','input_id')):
        raise ValueError('Selected FEM input identity differs')
    if analysis['evaluation_id']!=result['evaluation_id'] or analysis['input_id']!=spec['input_id']:
        raise ValueError('Selected workflow FEM identity differs')
    summary=viaduct_workflow.numerical_summary(result,folder)
    if 'resource_evaluation_id' in analysis:
        from . import viaduct_fem_resource
        resource=folder/'resource';r=load(resource/'result.json');q=load(resource/'request.json')
        sealed(r,'result_id');sealed(q,'evaluation_id')
        for key in ('candidate_id','component_geometry_id','input_id'):
            if r[key]!=result[key] or q[key]!=result[key]:raise ValueError('Resource revision mixed physical inputs')
        if (r['evaluation_id']!=analysis['resource_evaluation_id'] or q['evaluation_id']!=r['evaluation_id']
                or r['original_result_id']!=result['result_id'] or q['original_result_id']!=result['result_id']
                or r['execution']!=load(resource/'execution.json')):
            raise ValueError('Resource revision ancestry/execution differs')
        expected=viaduct_fem_resource.comparisons(r['fieldcraft'],result['levels']['coarse']['results']['fieldcraft'],result['levels']['fine']['results']['calculix'])
        if r['comparisons']!=expected:raise ValueError('Resource numerical comparisons differ')
        summary['original_numerical_screen_passed']=summary['numerical_screen_passed']
        summary['effective_fine_midspan_uz_m']=r['fieldcraft']['displacement_m'][2]
        summary['effective_refinement_relative']=expected['displacement_refinement_relative_change']
        effective=(expected['cross_solver_screen_passed'] and expected['displacement_refinement_screen_passed']
            and r['fieldcraft']['force_equilibrium_passed'] and r['fieldcraft']['moment_equilibrium_passed']
            and summary['levels']['coarse']['numerical_screen_passed'])
        comparison=analysis['summary']['resource_comparison']
        if (comparison['evaluation_id']!=r['evaluation_id'] or comparison['result_id']!=r['result_id']
                or comparison['resources']!=q['resources'] or comparison['state']!=r['state']
                or comparison['numerical_screen_passed'] is not effective or comparison['original_failed_evaluation_preserved'] is not True):
            raise ValueError('Resource workflow summary differs')
        summary['resource_comparison']=deepcopy(comparison);summary['numerical_screen_passed']=effective
    if summary!=analysis['summary']:raise ValueError('Selected numerical projection differs')
    return summary


def summary(workflow,cases):
    value=dict(schema='osr-viaduct-backend-public-summary/1',workflow_result_id=workflow['result_id'],
        case_count=len(cases),nominal_stock_regions=sum(len(c['entities']) for c in cases),
        numerical_comparisons=len(workflow['analyses']),
        numerically_screened_comparisons=sum(a['summary']['numerical_screen_passed'] is True for a in workflow['analyses'].values()),
        rows=workflow['rows'],outline_archive=workflow['outline_archive'],
        archive_scope=workflow['archive_scope'],default_backends_changed=False,integrated_selection=None,
        public_replay_scope='Selected source-bound records, exact per-body readbacks, quantities/cost ownership and derived numerical comparisons; not raw mesh/solver execution replay',
        raw_execution_packages_retained=True,complete_installed_bridge_design=False,**FLAGS)
    value['summary_id']=identity(value);return value


def table_csv(rows):
    fields=('case_id','candidate_id','component_geometry_id','nominal_stock_mass_kg','structural_factory_base_iqd','scoped_installed_base_iqd','cad_evaluation_id','delivery_evaluation_id','numerical_evaluation_id')
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fields,lineterminator='\n');writer.writeheader()
    for row in rows:writer.writerow({k:row[k] for k in fields})
    return out.getvalue()


def readme(value):
    lines=[]
    for row in value['rows']:
        name=row['case_id'];label=name.replace('--',' / ').replace('_',' ')
        lines.append(f"| [{label}](models/{name}/assembly.step) | {row['nominal_stock_mass_kg']/1000:.3f} | {row['structural_factory_base_iqd']/1e6:.3f} | {row['scoped_installed_base_iqd']/1e6:.3f} | [SC](models/{name}/assembly.sc) · [STL](models/{name}/assembly.stl) · [route](delivery/{name}.json) |")
    return '''# Twelve 20 m viaduct outlines: CAD, mechanics and manufacturing

Twelve canonical span geometries across six structural families now pass through
one optional SolidCraft → mechanical-analysis → manufacturing/cost workflow.
All twelve have exact STEP geometry independently measured in FreeCAD; two have
matched coarse/fine FieldCraft and CalculiX solid-element results. The selected
railway baseline and default providers are unchanged.

![Actual native box-span CAD](box.png)
![Actual native folded-plate CAD](folded-plate.png)

These are unmodified native CAD snapshots, without display offsets. The downloadable
models retain separate material regions. The model named `reference_box` is the
**54.720 t four-wall portfolio geometry**, not the selected **55.704 t six-part
beam with end diaphragms**. Neither number is complete installed bridge mass.

## Compare and download

![Nominal stock and scoped factory cost](mass-factory-cost.png)

| Family / parameter profile | Nominal stock, t | Structural factory, IQD m | Scoped installed, IQD m | Native model / production route |
|---|---:|---:|---:|---|
'''+ '\n'.join(lines)+'''

[Comparison CSV](comparison.csv) · [Same-candidate records](cases.json) ·
[Full comparison and evidence IDs](summary.json) · [Provider interfaces](../../../engineering/design_search/craft_backends/backend_api.py).

**Cost basis:** retained dated Iraqi observations and Class C process proxies;
these are not newly researched Chinese quotations or revised city prices.
Low/base/high costs, quantities, proposed manufactured groups, process routes,
ownership and remaining allowances are in each route record. Nominal CAD regions
are not purchased-component counts: the concrete families propose a cast span;
the hybrid proposes one deck and two girders.

The common base rail/fastener allowance alone is **IQD 52.084m** per 20 m span.
The base support/foundation/bearing reserve is another **IQD 20m**. These accounts
are separated from structural factory cost. Replace matching corridor budget
owners rather than adding these span totals to already-priced rail, foundation
or erection accounts. Missing complete installed costs and masses remain unknown.
A 100-use mould assumption does not prove a committed batch, removable mould,
curing capacity or production schedule. The surface-area proxy is not a mould drawing.

## Actual structural comparison

![Recorded coarse/fine FEM results](fem-deflection.png)

The box gives 11.8253 → 11.5231 mm downward midspan displacement (2.623% change);
the folded plate gives 19.0331 → 18.9079 mm (0.662% change). Both satisfy this
experiment's declared equilibrium, displacement-refinement and cross-solver
screens. Two mesh levels do not establish mesh independence or physical resistance.

The original **2 GiB fine box FieldCraft solve failed allocation**. Its receipt
remains held. The fine plotted FieldCraft result belongs to a **separate 3 GiB
resource evaluation**, with the original geometry, load, mesh and material.
The folded-plate pair completes within the original 2 GiB limit.

SolidCraft STEP is imported and fragmented using **Gmsh 4.14.1 / OpenCASCADE**,
then meshed with conformal straight-sided quadratic tetrahedra. The FieldCraft
native hexahedral meshing attempt on these shared prism faces remains a recorded
failed probe. This result does not imply that path was fixed or used successfully.
Node ordering is converted explicitly for each solver. Positive Jacobian checks
are not a complete element aspect-ratio or dihedral-quality assessment.

The research material is homogeneous, uncracked concrete, E = 35 GPa, ν = 0.2,
ρ = 2500 kg/m³, with perfect bonding. A shared crowd-control axle pose and
candidate self-weight/declared non-CAD mass are applied; these are not an exhaustive
moving-load envelope. Four axles at x = 5.3, 7.4, 10.0 and 12.1 m each carry
99.510 kN, including the dynamic factor once, through two rail patches.

Finite **bilateral** restrained patches at both ends introduce fixture stiffness
and tensile nodal reactions. They are not verified bearings or compression-only
contact. Actual bearing compliance/contact, rail/support connections, cracking,
reinforcement, prestress, fatigue, torsion, temporary stability and lifting remain
open. The box lifting reserve already exceeds a nominal 60 t crane control;
crane capacity must be established at the required radius with verified lift points.
Sampled nodal stresses and CalculiX integration-point maxima have different scopes;
no agreement of full stress fields is claimed. No structure is approved for construction.

## Reproduce, revise and retain alternatives

```bash
./osr design backends providers
./osr design backends viaduct plan
# A fresh immutable campaign; bounded native work is explicit:
./osr design backends viaduct run --execute --output /path/to/private/fresh-run
./osr design backends viaduct verify --output /path/to/private/fresh-run
# Portable checks of this selected public dossier; no CAD/FEM installation needed:
./osr design backends viaduct verify-publication
```

The CAD provider exposes generate, revise, validate and export; the analysis
provider prepares, meshes, solves and verifies; delivery recalculates quantities,
routings, costs and disabled business drafts from the same physical definition.
A revision records ancestry and its reason. Candidate, evaluation and selection
identities remain separate. Unknown FEM performance never receives a zero score.
The retained Pareto archive compares nominal mass and scoped factory cost only.

The tested pair remains **SolidCraft 0.30.1 / FieldCraft 0.7.5**. The newer format
compatibility boundary is documented in the [initial pilot](../craft-backends/README.md).
FreeCAD/CalculiX remain independent comparisons; Gmsh/GetDP, IfcOpenShell/Bonsai,
Chrono and SUMO retain their specialist routes. This extends the existing
[detailed launch shuttle](../launch-detail/README.md), not a second design platform.

The native CAD generation plus independent measurement used 13 processes and
6.615 s in this bounded cohort. Subsequent STL export and two snapshots used
three more processes. All 29 FEM-process attempts, including failed/earlier source
epochs, remain retained privately; no generic solver-throughput claim follows.
The successful box fine solve reports 1.24 GiB peak RSS under a 3 GiB per-process
address-space limit. Thread limits are requested through environment variables;
hard CPU affinity and aggregate-memory cgroups are not enforced.

Strict historical mesh/load replay uses the original `/usr/bin/python3` NumPy
2.5.3 context; the coordinator environment has NumPy 2.3.5. Substituting one changes
last-bit nodal load identities and is rejected. The adapter now records the
chosen interpreter and NumPy/BLAS/LAPACK artifacts before and after replay.
Later observations of the historical Gmsh binary are not recast as original
pre-execution pins. The public records preserve these distinctions.

`manifest.json` inventories this compact selection. Original receipts under
`evidence/` remain unchanged; their paths and full inventories describe the
retained private runs. Public verification checks selected readbacks and derived
claims. It does not replay the omitted meshes, solver checkpoints or logs, and
performs no fresh solve. The original plotting script retains its private-run paths as historical provenance.
The portable [replot helper](presentation/render-recorded-plots.py) reads only
adjacent [plot data](presentation/plot-data.json); run it with `--output` pointing
to a fresh directory. Both regenerated plots match the recorded PNG bytes in the
recorded Matplotlib environment. Data and receipts retain source evaluation IDs. No selected baseline, manufacturing release, movement
authority or physical acceptance is granted.

Next: resolve bearing/contact behavior, develop reinforcement/anchorage and
removable mould details, test lift/erection stages, and replace the dominant cost
proxies with current scoped sourcing and production-capacity evidence.
'''


def publish(state,evidence,output,*,root=ROOT):
    state=Path(state).resolve();evidence=Path(evidence).resolve();output=Path(output).absolute()
    if output.exists():raise ValueError('Fresh immutable public output required')
    verification=viaduct_workflow.verify(state,root=root)
    workflow=load(state/'result.json');request=load(state/'request.json');cases=request['cases']
    cad=Path(workflow['cad_source_path']);cm=load(cad/'manifest.json')
    output.mkdir(parents=True)
    def copy(source,relative):
        dest=output/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    for name in ('request.json','result.json','manifest.json'):copy(state/name,'evidence/workflow/'+name)
    native.write(output/'evidence/private-verification.json',verification)
    for name in ('request.json','manifest.json'):copy(cad/name,'evidence/cad/'+name)
    for case in cases:
        name=case['case_id'];folder=cad/name
        for file in ('case.json','request.json','commands.json','generated-measures.json','generate/results.json','generate/execution.json'):
            copy(folder/file,'evidence/cad/'+name+'/'+file)
        for suffix in ('sc','step'):copy(folder/('generate/assembly.'+suffix),'models/'+name+'/assembly.'+suffix)
        copy(cad/'freecad-reference'/name/'measurement.json','evidence/cad/freecad-reference/'+name+'/measurement.json')
        copy(state/'delivery'/(name+'.json'),'delivery/'+name+'.json')
        copy(evidence/'cad/stl-export01'/(name+'.stl'),'models/'+name+'/assembly.stl')
    for name in ('execution.json','resource.json'):copy(cad/'freecad-reference'/name,'evidence/cad/freecad-reference/'+name)
    for name,analysis in workflow['analyses'].items():
        folder=Path(analysis['source_path'])
        for file in ('input.json','request.json','result.json'):copy(folder/file,'evidence/fem/'+name+'/'+file)
        if 'resource_evaluation_id' in analysis:
            src=Path(analysis['summary']['resource_comparison']['source_path'])
            for file in ('request.json','result.json'):copy(src/file,'evidence/fem/'+name+'/resource/'+file)
            copy(src/'fieldcraft/execution.json','evidence/fem/'+name+'/resource/execution.json')
    for name in ('stl-export-request01.json','stl-export-result01.json'):copy(evidence/'cad'/name,'evidence/'+name)
    for name in ('manifest.json','plot-data.json','plot-script.py','mass-factory-cost.png','fem-deflection.png'):
        copy(evidence/'presentation'/name,'presentation/'+name if name in ('manifest.json','plot-data.json','plot-script.py') else name)
    copy(evidence/'presentation/render-recorded-plots.py','presentation/render-recorded-plots.py')
    for folder,name in (('reference_box','box.png'),('folded_plate','folded-plate.png')):
        copy(evidence/('cad/'+folder+'-snapshot01/assembly.png'),name)
    value=summary(workflow,cases);native.write(output/'summary.json',value);native.write(output/'cases.json',cases)
    (output/'comparison.csv').write_text(table_csv(value['rows']))
    (output/'README.md').write_text(readme(value))
    manifest=dict(schema='osr-viaduct-backend-publication/1',source_sha256={**request['source_sha256'],SOURCE:digest(Path(root)/SOURCE)},
        workflow_result_id=workflow['result_id'],summary_id=value['summary_id'],files_sha256=inventory(output),
        scope=value['public_replay_scope'],fresh_native_solve=False,complete_private_inventory_published=False,**FLAGS)
    manifest['manifest_id']=identity(manifest);native.write(output/'manifest.json',manifest)
    return verify(output,root=root)


def verify(output=None,*,root=ROOT):
    output=Path(root)/OUTPUT if output is None else Path(output)
    m=load(output/'manifest.json');sealed(m,'manifest_id')
    if m['files_sha256']!=inventory(output):raise ValueError('Public file coverage differs')
    for file in output.rglob('*.json'):viaduct_admission._unreleased(load(file))
    if any(digest(Path(root)/name)!=sha for name,sha in m['source_sha256'].items()):raise ValueError('Public source epoch differs')
    request=load(output/'evidence/workflow/request.json');workflow=load(output/'evidence/workflow/result.json')
    sealed(request,'request_id');sealed(workflow,'result_id')
    wm=load(output/'evidence/workflow/manifest.json');sealed(wm,'manifest_id')
    if (wm['request_id']!=request['request_id'] or wm['result_id']!=workflow['result_id']
            or any(digest(output/'evidence/workflow'/n)!=wm['files_sha256'][n] for n in ('request.json','result.json'))):
        raise ValueError('Selected original workflow receipt differs')
    expected_verification=dict(verified=True,fresh_native_solve=False,result_id=workflow['result_id'],manifest_id=wm['manifest_id'],**FLAGS)
    if load(output/'evidence/private-verification.json')!=expected_verification:
        raise ValueError('Selected private verification receipt differs')
    if m['source_sha256']!={**request['source_sha256'],SOURCE:digest(Path(root)/SOURCE)}:
        raise ValueError('Public source coverage differs')
    if workflow['request_id']!=request['request_id'] or workflow['result_id']!=m['workflow_result_id']:
        raise ValueError('Public workflow identity differs')
    cases=viaduct_cases.portfolio(root=root)
    if load(output/'cases.json')!=cases or request['cases']!=cases:raise ValueError('Public canonical cases differ')
    cm=load(output/'evidence/cad/manifest.json');cr=load(output/'evidence/cad/request.json');sealed(cm,'result_id');sealed(cr,'request_id')
    if ({c['case_id']:c for c in cr['cases']}!={c['case_id']:c for c in cases} or len(cr['cases'])!=len(cases)
            or cm['request_id']!=cr['request_id'] or workflow['cad_result_id']!=cm['result_id']):
        raise ValueError('Public CAD cohort identity differs')
    for file in ('execution.json','resource.json'):
        if digest(output/'evidence/cad/freecad-reference'/file)!=cm['artifact_sha256']['freecad-reference/'+file]:
            raise ValueError('Selected original reference execution differs')
    presentation=load(output/'presentation/manifest.json')
    for file in ('mass-factory-cost.png','fem-deflection.png'):
        if digest(output/file)!=presentation['artifact_sha256'][file]:raise ValueError('Plot provenance differs')
    for file in ('plot-data.json','plot-script.py'):
        if digest(output/'presentation'/file)!=presentation['artifact_sha256'][file]:raise ValueError('Plot data/script provenance differs')
    for family,file in (('reference_box','box.png'),('folded_plate','folded-plate.png')):
        if digest(output/file)!=presentation['unaltered_native_cad_image_sha256']['cad/'+family+'-snapshot01/assembly.png']:
            raise ValueError('Native CAD snapshot provenance differs')
    stl_request=load(output/'evidence/stl-export-request01.json');stl_result=load(output/'evidence/stl-export-result01.json')
    plot_data=load(output/'presentation/plot-data.json')
    if plot_data['cad_result_id']!=cm['result_id'] or plot_data['cad_request_id']!=cr['request_id']:
        raise ValueError('Plotted CAD evaluation differs')
    plotted={r['case_id']:r for r in plot_data['cad_cases']}
    if len(plotted)!=len(cases):raise ValueError('Plotted case coverage differs')
    context=viaduct_delivery.prepare(root);rows=[]
    for case in cases:
        name=case['case_id'];folder=output/'evidence/cad'/name;record=cm['cases'][name]
        for file in ('case.json','request.json','commands.json','generated-measures.json','generate/results.json','generate/execution.json'):
            if digest(folder/file)!=cm['artifact_sha256'][name+'/'+file]:raise ValueError('Selected original CAD artifact differs')
        if load(folder/'case.json')!=case:raise ValueError('Selected CAD physical case differs')
        measured=load(output/'evidence/cad/freecad-reference'/name/'measurement.json')
        if digest(output/'evidence/cad/freecad-reference'/name/'measurement.json')!=cm['artifact_sha256']['freecad-reference/'+name+'/measurement.json']:
            raise ValueError('Selected exact readback differs')
        if viaduct_cad.compare(case,measured,exact=True,associate=True)!=record['exact_step']:
            raise ValueError('Exact per-body CAD comparison differs')
        if viaduct_cad.compare(case,load(folder/'generated-measures.json'))!=record['diagnostic']:
            raise ValueError('Diagnostic CAD comparison differs')
        for suffix,key in (('sc','sc_sha256'),('step','step_sha256')):
            if digest(output/'models'/name/('assembly.'+suffix))!=record[key]:raise ValueError('Published native CAD differs')
        if record['evaluation_id']!=viaduct_cad.plan(case,root=root)['evaluation_id']:raise ValueError('Published CAD evaluation differs')
        stl=stl_result['case_checks'][name];inp=stl_request['case_inputs'][name]
        count,bounds=stl_bounds(output/'models'/name/'assembly.stl')
        if (stl['candidate_id']!=case['candidate_id'] or inp['candidate_id']!=case['candidate_id'] or inp['component_geometry_id']!=case['component_geometry_id']
                or inp['sc_sha256']!=record['sc_sha256'] or digest(output/'models'/name/'assembly.stl')!=stl['sha256']
                or count!=stl['triangle_count'] or bounds!=stl['bounds_m'] or stl['units']!='mm'):
            raise ValueError('Native STL identity, units or bounds differ')
        measures=case['expected']['part_measures'].values()
        canonical_bounds=[[fn(p['bounds_m'][side][axis] for p in measures) for axis in range(3)] for side,fn in ((0,min),(1,max))]
        error=max(abs(a-b) for x,y in zip(bounds,canonical_bounds) for a,b in zip(x,y))
        if stl['maximum_bbox_error_m']!=error or error>1e-5:
            raise ValueError('Native STL canonical bounding-box screen differs')
        delivery=viaduct_delivery.build(case['physical_definition'],context,root=root)
        if digest(output/'delivery'/(name+'.json'))!=wm['files_sha256']['delivery/'+name+'.json']:
            raise ValueError('Selected original delivery artifact differs')
        if load(output/'delivery'/(name+'.json'))!=delivery:raise ValueError('Public same-candidate delivery differs')
        point=plotted[name]
        expected_point=dict(case_id=name,candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],
            cad_evaluation_id=record['evaluation_id'],cost_evaluation_id=delivery['source_cost_evaluation_id'],
            family=case['family'],profile=case['profile'],nominal_stock_mass_kg=case['canonical_quantities']['total_nominal_stock_mass_kg'],
            structural_factory_base_iqd=delivery['cost']['cases']['base']['factory_gate_iqd'],
            rail_interface_base_iqd=delivery['cost']['cases']['base']['owned_accounts_iqd']['rail-and-fastener-interface'],
            scoped_installed_base_iqd=delivery['cost']['cases']['base']['scoped_installed_iqd'])
        if point!=expected_point:raise ValueError('Plotted material/cost point differs')
        analysis=workflow['analyses'].get(name)
        if analysis:
            selected_numerics(output/'evidence/fem'/name,analysis)
            raw=load(output/'evidence/fem'/name/'result.json')
            for file in ('input.json','request.json'):
                if digest(output/'evidence/fem'/name/file)!=raw['artifact_sha256'][file]:
                    raise ValueError('Selected original numerical artifact differs')
        rows.append(viaduct_workflow._row(case,delivery,record,analysis))
    plotted_fem=set()
    for point in plot_data['fem_cases']:
        name=point['family']+'--reference';folder=output/'evidence/fem'/name
        raw=load(folder/'result.json');resource=point['resource_memory_MiB']!=2048
        if resource:raw=load(folder/'resource/result.json')
        key=(name,point['level'],point['solver'],point['resource_memory_MiB'])
        if key in plotted_fem:raise ValueError('Duplicate plotted numerical point')
        plotted_fem.add(key)
        if any(point[k]!=raw[k] for k in ('candidate_id','evaluation_id','result_id')):raise ValueError('Plotted numerical identity differs')
        result=raw['fieldcraft'] if resource else raw['levels'][point['level']]['results'].get(point['solver'])
        expected_value=None if result is None else -result['displacement_m'][2]
        if point['vertical_deflection_m']!=expected_value:raise ValueError('Plotted numerical value differs')
    expected_points={(name,level,solver,2048) for name in workflow['analyses'] for level in ('coarse','fine') for solver in ('fieldcraft','calculix')}
    expected_points|={(name,'fine','fieldcraft',3072) for name,a in workflow['analyses'].items() if 'resource_evaluation_id' in a}
    if plotted_fem!=expected_points:raise ValueError('Plotted numerical coverage differs')
    if rows!=workflow['rows'] or workflow['outline_archive']!=viaduct_workflow.outline_archive(rows):raise ValueError('Public comparison rows/archive differ')
    value=summary(workflow,cases)
    if load(output/'summary.json')!=value or value['summary_id']!=m['summary_id']:
        raise ValueError('Public summary differs')
    if (output/'README.md').read_text()!=readme(value) or (output/'comparison.csv').read_text()!=table_csv(rows):raise ValueError('Public presentation differs')
    return dict(verified=True,manifest_id=m['manifest_id'],case_count=len(cases),numerical_comparisons=len(workflow['analyses']),
        scope=value['public_replay_scope'],fresh_native_solve=False,**FLAGS)
