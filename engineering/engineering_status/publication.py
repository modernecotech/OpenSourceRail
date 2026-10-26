"""One current register from exact, independently checked research packages."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import tarfile
import tempfile

from engineering.design_search.storage import atomic_immutable
from . import ROOT,FLAGS
from .contracts import candidate,gate,identity,encoded,preflights,require_subject
from . import native,operations

BASE='docs/design-engine/halbach-scaling'
PARENT='4f59edd99dc6128b76d23233c85220f475b3e29d'
WORKBENCH='docs/workbench/trip/readiness'
OUTPUT='docs/design-engine/ferrite-maglev/engineering-readiness'
START='<!-- osr-current-engineering:start -->'
END='<!-- osr-current-engineering:end -->'


def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):return atomic_immutable(Path(path),encoded(value))


def retained(root):
    root=Path(root);folder=root/BASE;manifest=read(folder/'manifest.json')
    if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('larger-array receipt identity differs')
    for name,digest in manifest['source_sha256'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('retained comparison source differs: '+name)
    for name,digest in manifest['files_sha256'].items():
        if sha256((folder/name).read_bytes()).hexdigest()!=digest:raise ValueError('retained comparison payload differs: '+name)
    value=read(folder/'comparison.json')
    if value['study_id']!=manifest['study_id'] or value['study_id']!=identity({k:v for k,v in value.items() if k!='study_id'}):raise ValueError('retained study identity differs')
    return value


def _link(scope,subject,evaluation,path):return dict(scope=scope,**subject,evaluation_id=evaluation,path=path)


def _candidate(row,vehicle,suspension,thermal):
    composition=dict(candidate_id=row['composition_id'],body_candidate_id=row['body_candidate_id'],
        magnet_component_id=row['magnet_component_id'],name=row['recipe_id']+' / '+row['body_name'],
        recipe_id=row['recipe_id'],comparison_aw3_kg_per_car=row['comparison_aw3_kg_per_car'],
        comparison_empty_kg_per_car=row['comparison_empty_kg_per_car'],source_comparison_id=row['comparison_id'])
    body_link=_link('body',dict(body_candidate_id=composition['body_candidate_id']),row['comparison_id'],'larger-array-comparison')
    gates={k:gate(k,'unknown',reason) for k,reason in {
        'mass':'Complete installed equipment, positions, mass, centre of gravity and inertia remain unknown.',
        'suspension':'Local static samples do not establish converged 3D operating maps, load reserve or all force/moment derivatives.',
        'control':'No matched multiaxis closed-loop and power-loss response has been demonstrated.',
        'electrical':'Actual hot-weather HVAC capacity, converter ratings, repeated duty and complete services power remain unknown.',
        'structure':'Local member screens and a composite coupon do not establish an equipped body, joints, fatigue or flexible modes.',
        'civil':'The new magnetic geometry, force envelope, facing anchors and deformation are not a matching qualified civil design.',
        'operations':'No same-candidate physical 2 km journey, stopping/protection headway or accepted transfer layout exists.',
        'economics':'Installed costs and same-candidate vehicle, station, guideway, operating and financing scope remain incomplete.'}.items()}
    if row['known_member_failure']:
        gates['structure']=gate('structure','fail','The declared composition fails a necessary local member/load screen. Whole-body and physical qualification remain open.',
            evidence=[body_link],maturity='analytical-estimate',values={'source_comparison_id':row['comparison_id']})
    if row['nominal_hot_cooling_failure']:
        gates['electrical']=gate('electrical','fail','The declared HVAC quantity fails the retained nominal-capacity sizing scenario; actual 50°C output and full electrical duty remain unknown.',
            evidence=[body_link],maturity='analytical-estimate',values={'nominal_thermal_margins_kW':row['nominal_thermal_margins_kW']})
    inventory=next((v for v in vehicle['inventories'] if v['composition_id']==composition['candidate_id']),None)
    if inventory:
        require_subject(dict(candidate_id=inventory['composition_id']),composition,'composition')
        require_subject(inventory,composition,'body');require_subject(inventory,composition,'magnet')
        evidence=[_link('composition',dict(candidate_id=composition['candidate_id']),inventory['evaluation_id'],'equipped-inventory')]
        gates['mass']=gate('mass','unknown','Located material is counted separately from unlocated stock, supplier references, retained allocations and missing equipment. Full installed mass/CG/inertia remain unknown.',
            evidence=evidence,maturity='analytical-estimate',values=dict(located_material_kg=inventory['located_material_properties']['mass_kg'],
                accounted_tare_kg=inventory['comparison_empty_kg_per_car'],complete_installed_mass_kg=inventory['installed_empty_kg_per_car'],
                complete_CG_m=inventory['cg_m'],complete_inertia_kg_m2=inventory['inertia_kg_m2']))
    magnetic=next((c for c in suspension['comparisons'] if c['candidate_id']==composition['magnet_component_id']),None)
    if magnetic:
        evidence=[_link('magnet',dict(magnet_component_id=magnetic['candidate_id']),suspension['result_id'],'operating-point-campaign')]
        # A magnetic component calculation transfers as a component result only.
        # Current-gap reserve failures do not prove that every proposed gap fails.
        gates['suspension']=gate('suspension','unknown','Operating-point force/current and derivative samples are available. The proposed gap must still satisfy load and reserve with converged finite 3D maps and compatible installed mass.',
            evidence=evidence,maturity='analytical-estimate',values={'component_temperatures':magnetic['temperatures']})
    winding=thermal['support_winding']
    if winding['parent_composition_id']==composition['candidate_id']:
        require_subject(dict(candidate_id=winding['parent_composition_id']),composition,'composition')
        require_subject(dict(magnet_component_id=winding['candidate_id']),composition,'magnet')
        require_subject(dict(body_candidate_id=winding['parent_body_candidate_id']),composition,'body')
        if thermal['hvac']['parent_package_binding']['parent_body_candidate_id']!=composition['body_candidate_id']:
            raise ValueError('thermal package belongs to another body')
        gates['electrical']=gate('electrical','unknown','The exact five-unit package and winding stock are identified. Actual 50°C capacity/COP, fresh air, bus rating, heat rejection and controlled repeated duty remain unknown; generic passive revisions are separate physical proposals.',
            evidence=[_link('composition',dict(candidate_id=composition['candidate_id']),thermal['evaluation_id'],'thermal-and-winding-study')],
            maturity='analytical-estimate',values=dict(coil_15A_80C_W_per_module=winding['copper_DC_loss_15A_80C_W_per_module'],
                necessary_conductance_W_K_per_module=winding['necessary_conductance_for_80C_copper_50C_ambient_W_K_per_module'],
                actual_conductance_W_K=winding['actual_thermal_conductance_W_K'],actual_bus_voltage_V=winding['actual_drive_bus_voltage_V']))
    return candidate(composition,list(gates.values()))


def _domain_check(paths,root):
    from engineering.suspension_closure import study as magnetics
    from engineering.equipped_vehicle import report as equipped
    from engineering.thermal_closure import study as thermal
    magnetics.verify(paths['suspension'],root)
    equipped.verify(paths['vehicle'],root=root)
    thermal.verify(paths['thermal'],root)
    native.verify(paths['native'],root)
    if 'confirmation' in paths:
        from engineering.operating_confirmation import study as confirmation
        confirmation.verify(paths['confirmation'],root)


def sources(root,paths):
    root=Path(root).resolve();records={}
    for p in sorted(Path(__file__).parent.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.html','.css','.js','.toml'}:
            name='/'.join(p.parts[p.parts.index('engineering'):]);records[name]=sha256(p.read_bytes()).hexdigest()
    for name in (BASE+'/manifest.json',BASE+'/comparison.json',operations.CITY,operations.ACCESS,'.github/workflows/engineering-native.yml'):
        records[name]=sha256((root/name).read_bytes()).hexdigest()
    for directory in paths.values():
        manifest=read(Path(directory)/'manifest.json')
        for name,digest in manifest['source_sha256'].items():
            if name in records and records[name]!=digest:raise ValueError('mixed executing/retained source revisions: '+name)
            if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('domain source changed: '+name)
            records[name]=digest
    return dict(sorted(records.items()))


def assemble(root,paths):
    _domain_check(paths,root);base=retained(root)
    magnetics=read(Path(paths['suspension'])/'result.json');vehicle=read(Path(paths['vehicle'])/'summary.json')
    thermal=read(Path(paths['thermal'])/'result.json');methods=read(Path(paths['native'])/'result.json')
    records=[_candidate(r,vehicle,magnetics,thermal) for r in base['comparisons']]
    by_id={r['candidate_id']:r for r in records}
    if len(by_id)!=len(records):raise ValueError('unique complete composition inventory required')
    selected=[]
    for s in base['selection']['selected']:
        old=next(r for r in base['comparisons'] if r['comparison_id']==s['comparison_id'])
        selected.append(old['composition_id'])
    value=dict(schema='osr-current-engineering-register/1',campaign_parent_revision=PARENT,
        candidates=records,default_candidate_id=selected[0],selected_next_experiment_ids=selected,
        preflights_by_candidate={cid:preflights(by_id[cid]) for cid in selected},
        parent_larger_array_study_id=base['study_id'],source_sha256=sources(root,paths),
        native_methods=dict(evaluation_id=methods['evaluation_id'],rows=methods['rows'],
            method_campaign_passed=methods['method_campaign_passed'],scope=methods['scope']),
        magnetic_operating_campaign=dict(result_id=magnetics['result_id'],comparisons=magnetics['comparisons'],finite=magnetics['finite']),
        equipped_vehicle=vehicle,thermal=dict(evaluation_id=thermal['evaluation_id'],counts=thermal['counts'],
            readiness=thermal['readiness'],support_winding=thermal['support_winding'],
            passive_hypotheses_are_separate_vehicle_proposals=True),
        service_context=operations.study(root),
        gate_states=dict(Counter(g['state'] for r in records for g in r['gates'])),
        complete_operating_trains_demonstrated=0,physical_qualified_candidates=0,**FLAGS)
    if 'confirmation' in paths:value['operating_confirmation']=read(Path(paths['confirmation'])/'result.json')
    value['register_id']=identity(value);return value


def index(value):
    return dict(schema=value['schema'],register_id=value['register_id'],default_candidate_id=value['default_candidate_id'],
        candidates=[{k:r[k] for k in ('candidate_id','body_candidate_id','magnet_component_id','name','engineering_readiness')} for r in value['candidates']],**FLAGS)


def readme(v):
    native_rows=v['native_methods']['rows'];fields=v['magnetic_operating_campaign'];thermal=v['thermal'];service=v['service_context']
    lines=['# Current engineering readiness','',
        'OpenSourceRail develops simple, locally maintainable urban transport with high normal passenger throughput. This register joins the exact magnetic component, body revision and equipped comparison before assigning an engineering gate. All permanent magnets and support/guidance coils remain onboard; ordinary guideways remain concrete with passive steel facings.','',
        '**No complete equipped train, stable multiaxis hover or physically supported 2 km journey is established.** Numerical method success and component screens do not provide physical acceptance.','',
        '[Project introduction](../../../../README.md) · [Readiness Workbench](../../../workbench/trip/readiness/index.html) · [Candidate index](index.json) · [Compressed current register](status.json.gz) · [Source receipt](manifest.json) · [Research packages](artifacts.json)','',
        f"The register contains **{len(v['candidates'])} exact composed comparisons** and eight gates per configuration. The two next-experiment compositions each have eight explicit hover/journey/fault preflights. Failed and unknown prerequisites refuse motion without producing a fabricated trajectory. Source bindings, rather than an old overall review date, determine the current input revisions.",'',
        '## Operating magnetic experiment','',
        f"The matched campaign executes {len(fields['comparisons'])} material/layout comparisons at a common proposed operating gap. Detailed derivatives are focused on the 12-litre differential NdFeB assembly; the retained 6-litre control and counted 6-litre NdFeB + 6-litre ferrite hybrid have fewer sampled states. This is not a complete 3D force/current/loss map.",'',
        '| Configuration | Temperature °C | Nominal 2D Fz contours kN | Fixed-gap +2 t / 1.3 capacity screen |','|---|---:|---|---|']
    for c in fields['comparisons']:
        for t in c['temperatures']:
            f=t.get('nominal',{}).get('contour_Fz_N');force='unevaluated' if f is None else ' / '.join(f'{x/1000:.3f}' for x in f)
            state=t.get('sampled_fixed_gap_1_3_plus_2t_capacity_pass')
            lines.append(f"| {c['name']} | {t['temperature_C']:.0f} | {force} | {'pass' if state is True else 'fail' if state is False else 'unknown'} |")
    f=fields['finite'];p=f.get('point',{});forces=p.get('analysis',{}).get('air_contour_results',[])
    lines+=['',f"The coarser 3D operating attempt is **{f['execution_status']}** at 35.338 mm, 80°C and zero coil current. "+
        ('Its Fz contours are **'+' / '.join(f'{x["force_N"][2]/1000:.3f}' for x in forces)+' kN/module**.' if forces else 'It provides no finite-force credit.'),
        'Force-contour spread, mesh/domain refinement and finite current sources must be resolved before admission as an operating map. Lowering a proposed gap is a new evaluated state, not an automatic transfer of force.','',
        '## Equipped vehicle','',
        '| Body option | Located defined material kg | Accounted tare comparison kg | Complete installed mass / CG / inertia |','|---|---:|---:|---|']
    for r in v['equipped_vehicle']['inventories']:
        lines.append(f"| {r['body_name']} | {r['located_material_properties']['mass_kg']:.3f} | {r['comparison_empty_kg_per_car']:.3f} | unknown |")
    lines+=['','Every identified occurrence has structural-participation and fit/test/removal/repair fields. Material-region counts are not manufacturing part counts. Unlocated magnetic stock, supplier references, retained allocations and missing equipment do not acquire a uniform invented mass distribution. GFRP monocoque design variables are a separate unexecuted design space; they are not silently substituted for the selected reinforced frame.','',
        '## Hot-weather and electrical consequences','',
        f"The thermal study retains **{thermal['counts']['heat_load_scenarios']} heat-load scenarios**, **{thermal['counts']['nameplate_and_N_minus_one_comparisons']} normal/N−1 nominal-capacity comparisons**, and **{thermal['counts']['nominal_capacity_comparison_failures']} nominal-sizing failures**. Actual 50°C capacity, compressor COP/input, ventilation and complete services power remain unknown.",'',
        f"There are {thermal['counts']['hot_core_temperature_scenario_failures']} conditional dark-roof/core-temperature failures in the declared passive-feature scenarios. These feature proposals require a new complete composition; they do not automatically describe the selected car. Added insulation stock is counted, while coatings, heat recovery, mounts and integration remain unknown where unweighed.",'',
        f"At 15 A and 80°C the selected winding dissipates **{thermal['support_winding']['copper_DC_loss_15A_80C_W_per_module']:.3f} W/module**. Holding 80°C copper in 50°C ambient requires **{thermal['support_winding']['necessary_conductance_for_80C_copper_50C_ambient_W_K_per_module']:.3f} W/K/module** in the declared steady heat balance; actual conductance is unknown. Unconstrained RL voltage responses that leave ±15 A have no validated force or controller credit.",'',
        '## Service, access and economics','',
        f"The retained Baghdad planning inputs still have **{service['retained_lines_below_target']} of {len(service['retained_lines'])} lines** below 14,400 normal passengers/hour/direction. Six cars at 120 normal passengers/car require 180-second headway arithmetically; safe headway, actual force/braking and changed fleet/station quantities remain unqualified for the new train.",'',
        f"The new research policy limits horizontal transfers to 300 m and walking to 300 seconds, evaluated at both 1.0 and 0.6 m/s. The retained maximum is **{service['maximum_retained_horizontal_transfer_m']:.1f} m** and fails this comparison. Lifts, queues, waiting, weather and actual accessible-route approval are additional. No shortcut, hub realignment or city adoption is invented.",'',
        'The old city cost sensitivities and civil loads belong to their original planning configurations. They are not presented as the cost or civil design of these lighter research alternatives.','',
        '## Native numerical maintenance','',
        '| Method | Execution | Numerical screen |','|---|---|---|']
    lines += [f"| {r['method']} | {r['execution']} | {r['state']} |" for r in native_rows]
    lines += ['','The separate scheduled workflow requests a two-step 2 km ideal-force Chrono check, a manufactured nonlinear 3D GetDP mesh pair, and an actual CalculiX composite mesh pair. Native logs and failures are retained. The composite coupon checks a declared synthetic laminate; it does not establish equipped-car modes. The weekly schedule requests Tuesday 03:17 UTC on the default branch; hosted execution can be delayed. [Schedule semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).','',
        '## Next engineering programme','',
        '| Package | Required closure |','|---|---|',
        '| Suspension/control | Converged finite operating maps, material limits, multiaxis derivatives, actuator reserve and correlated module measurements |',
        '| Equipped vehicle | Located complete inventory, GFRP/metal joint load paths, full CG/inertia and validated equipped modes |',
        '| Electrical/thermal | Actual hot-weather supplier data, ventilation, bus/protection ratings and repeated current/cooling duty |',
        '| Journey/faults | Same-candidate empty/AW3 2 km travel and receiving/support-power-loss response |',
        '| Civil | Matching facing anchors, eccentric reactions, deflection, beams, piers, foundations and construction loads |',
        '| Service/access | Protected 180-second or explicit revised headway, dwell/fleet consequences and acceptable accessible transfers |',
        '| Economics | Same-configuration installed scope, energy, maintenance, origin, financing and supplier evidence |',
        '| Prototype | Weighed and instrumented magnetic/steel and structural articles with independent measurement and review |','',
        'Reproduce with `python -m engineering.engineering_status --help`. Domain commands and all numerical inputs/logs are indexed in the retained packages. Status JSON is compressed and indexed to keep ordinary documentation concise. No research publication closes physical qualification.','']
    confirmation=v.get('operating_confirmation')
    if confirmation:
        extra=['## Finite operating refinement','',
            '| Case | Gap mm | Fz contours kN | Mean AW3 support screen | +2 t / 1.3 reserve screen |','|---|---:|---|---|---|']
        for r in confirmation['comparisons']['operating_states']:
            observed=r['observed'];state=r.get('state')
            force='unevaluated' if observed is None else ' / '.join(f'{q/1000:.3f}' for q in observed['contour_Fz_N'])
            support='unknown' if observed is None else 'pass necessary sample' if observed['lower_contour_supports_mean_weight'] else 'fail sample'
            reserve='unknown' if observed is None else 'pass necessary sample' if observed['lower_contour_supports_1_3_plus_2t'] else 'fail sample'
            gap='unevaluated' if state is None else format(state['gap_m']*1000,'.3f')
            extra.append(f"| {r['case']} | {gap} | {force} | {support} | {reserve} |")
        extra+=['','These are fixed 80°C, zero-current component states. A single mesh refinement and denser face integration are separate diagnostics, not force/moment convergence. The scalar-potential formulation contains **no coil-current source**; nonzero-current requests are refused. A mean-weight sample pass cannot establish equilibrium, reserve, multiaxis stability or a current-controlled journey.','']
        at=lines.index('## Equipped vehicle');lines[at:at]=extra
    return '\n'.join(lines).encode()


def _archive(label,directory):
    data=io.BytesIO()
    with gzip.GzipFile(fileobj=data,mode='wb',mtime=0) as out:
        with tarfile.open(fileobj=out,mode='w') as archive:
            for p in sorted(Path(directory).rglob('*')):
                if p.is_symlink():raise ValueError('ordinary research files required')
                if p.is_file():
                    raw=p.read_bytes();item=tarfile.TarInfo(label+'/'+p.relative_to(directory).as_posix());item.size=len(raw);item.mode=0o644;item.mtime=0;archive.addfile(item,io.BytesIO(raw))
    raw=data.getvalue()
    if len(raw)>95*1024**2:raise ValueError('one research package exceeded Git file budget')
    return raw


def front_block(v,name):
    link='docs/design-engine/ferrite-maglev/engineering-readiness/README.md' if name=='README.md' else 'design-engine/ferrite-maglev/engineering-readiness/README.md'
    ui='docs/workbench/trip/readiness/index.html' if name=='README.md' else 'workbench/trip/readiness/index.html'
    return '\n'.join((START,f"The [current engineering readiness register]({link}) connects **{len(v['candidates'])} composed alternatives** to eight explicit evidence gates, equipped-stock accounting, operating-point magnetic studies and hot-weather duty. The [readiness Workbench]({ui}) shows the same generated records. Complete installed mass, stable multiaxis hover and a physically driven 2 km journey remain open; native-method passes do not qualify a train.",END))


def update_front(root,v,*,check=False):
    for name in ('README.md','docs/ROADMAP.md'):
        path=Path(root)/name;text=path.read_text();block=front_block(v,name)
        if START in text:
            if text.count(START)!=1 or text.count(END)!=1:raise ValueError('one generated current-status block required')
            new=text[:text.index(START)]+block+text[text.index(END)+len(END):]
        else:
            marker='## Current design and evidence' if name=='README.md' else '## Primary maglev closure queue'
            at=text.index(marker);new=text[:at]+block+'\n\n'+text[at:]
        if check:
            if new!=text:raise ValueError('current front-door readiness block differs: '+name)
        elif new!=text:path.write_text(new)


def publish(output,*,root=ROOT,suspension,vehicle,thermal,native_dir,confirmation=None):
    paths=dict(suspension=Path(suspension),vehicle=Path(vehicle),thermal=Path(thermal),native=Path(native_dir))
    if confirmation is not None:paths['confirmation']=Path(confirmation)
    before=sources(root,paths);v=assemble(root,paths);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    atomic_immutable(output/'status.json.gz',gzip.compress(encoded(v),mtime=0));write(output/'index.json',index(v))
    atomic_immutable(output/'README.md',readme(v));artifacts={}
    for name,directory in paths.items():
        raw=_archive(name,directory);filename=name+'-artifacts.tar.gz';atomic_immutable(output/filename,raw)
        artifacts[name]=dict(file=filename,sha256=sha256(raw).hexdigest(),bytes=len(raw))
    write(output/'artifacts.json',artifacts)
    ui=Path(root)/WORKBENCH;ui.mkdir(parents=True,exist_ok=True);web=Path(__file__).parent/'web'
    for name in ('index.html','app.js','app.css'):(ui/name).write_bytes((web/name).read_bytes())
    if sources(root,paths)!=before:raise ValueError('readiness sources changed during publication')
    manifest=dict(schema='osr-current-readiness-publication/1',register_id=v['register_id'],source_sha256=before,
        files_sha256=native.inventory(output,('manifest.json',)),
        workbench_files_sha256={WORKBENCH+'/'+name:sha256((ui/name).read_bytes()).hexdigest() for name in ('index.html','app.js','app.css')},**FLAGS)
    manifest['manifest_id']=identity(manifest);write(output/'manifest.json',manifest);update_front(root,v)
    return dict(current=True,register_id=v['register_id'],candidates=len(v['candidates']),gate_states=v['gate_states'],physical_accepted=False)


def verify(output,*,root=ROOT):
    from engineering.halbach_scaling.publication import _extract
    d=Path(output);m=read(d/'manifest.json')
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}) or m['files_sha256']!=native.inventory(d,('manifest.json',)):
        raise ValueError('readiness publication identity/payload differs')
    for name,digest in m['source_sha256'].items():
        if sha256((Path(root)/name).read_bytes()).hexdigest()!=digest:raise ValueError('readiness source changed: '+name)
    for name,digest in m['workbench_files_sha256'].items():
        if sha256((Path(root)/name).read_bytes()).hexdigest()!=digest:raise ValueError('readiness Workbench differs')
    with tempfile.TemporaryDirectory(prefix='osr-readiness-readback-') as temp:
        temp=Path(temp);artifacts=read(d/'artifacts.json')
        if set(artifacts) not in ({'suspension','vehicle','thermal','native'},{'suspension','vehicle','thermal','native','confirmation'}):raise ValueError('exact research package inventory required')
        for label,record in artifacts.items():
            if record['file']!=label+'-artifacts.tar.gz':raise ValueError('research package path differs')
            p=d/record['file']
            if p.stat().st_size!=record['bytes'] or sha256(p.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('research package identity differs')
            _extract(p,temp,label)
        paths={label:temp/label for label in artifacts};v=assemble(root,paths)
        if (m['source_sha256']!=sources(root,paths) or m['register_id']!=v['register_id']
                or (d/'status.json.gz').read_bytes()!=gzip.compress(encoded(v),mtime=0)
                or read(d/'index.json')!=index(v) or (d/'README.md').read_bytes()!=readme(v)):
            raise ValueError('readiness register does not reproduce exact derived records')
    for name in ('index.html','app.js','app.css'):
        if (Path(root)/WORKBENCH/name).read_bytes()!=(Path(__file__).parent/'web'/name).read_bytes():raise ValueError('Workbench does not reproduce source template')
    update_front(root,v,check=True)
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('readiness cannot provide physical acceptance')
    return dict(current=True,register_id=v['register_id'],candidates=len(v['candidates']),physical_accepted=False)
