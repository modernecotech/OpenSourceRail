"""Generate a separate, source-bound comparison without replacing old evidence."""
import gzip
import io
import json
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import tempfile
from pathlib import PurePosixPath
from hashlib import sha256

from engineering.design_search.storage import atomic_immutable
from . import FLAGS,ROOT
from .common import encoded,identity,write,inventory,source_snapshot,unaccepted
from . import candidates,vehicles,coupling,screen,operating,finite


def environment():
    import numpy,scipy
    return dict(python=sys.version,platform=platform.platform(),numpy=numpy.__version__,scipy=scipy.__version__)


def compare(transverse,root=ROOT,*,operating_dir=None):
    screen.verify(transverse,root)
    raw=json.loads((Path(transverse)/'result.json').read_bytes())
    mags=candidates.candidates(root);bodies=vehicles.variants(root)
    additional=list(raw['authority_rows'])
    operating_id=None
    if operating_dir is not None:
        operating.verify(operating_dir,root=root)
        op=json.loads((Path(operating_dir)/'result.json').read_bytes());operating_id=op['request_id']
        additional.extend(r['result'] for r in op['rows'])
    rows=coupling.comparison_rows(mags,bodies,raw['rows'],root=root,additional_field_rows=additional)
    selection=coupling.select_experiments(mags,bodies,rows)
    return dict(schema='osr-halbach-scaling-comparison/1',screen_id=raw['screen_id'],magnetic_candidates=mags,
                vehicle_candidates=bodies,comparisons=rows,selection=selection,environment=environment(),
                load_profile_request_id=operating_id,source_sha256=source_snapshot(root),**FLAGS)


def _archive(paths):
    stream=io.BytesIO();size=0
    with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w') as archive:
            for label,directory in paths.items():
                for path in sorted(Path(directory).rglob('*')):
                    if path.is_symlink():raise ValueError('ordinary retained run files required')
                    if not path.is_file():continue
                    raw=path.read_bytes();size+=len(raw)
                    if size>768*1024**2:raise ValueError('retained campaign exceeded archive budget')
                    item=tarfile.TarInfo(label+'/'+path.relative_to(directory).as_posix());item.size=len(raw);item.mode=0o644;item.mtime=0
                    archive.addfile(item,io.BytesIO(raw))
    return stream.getvalue()


def _plot(value):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    seen=set();colours={};palette=plt.get_cmap('tab10')
    for r in value['comparisons']:
        if r['body_name']!='retained-frame/retained-equipment' or r['force_point'] is None:continue
        m=next(m for m in value['magnetic_candidates'] if m['physical_id']==r['magnet_component_id'])
        family=m['winding_definition']['layout'] if m['winding_definition']['layout']=='differential' else f"{m['parameters']['periods']} period / {m['parameters']['segments']} segments"+(' / yoke' if m['parameters']['yoke_m'] else '')
        label=family if family not in seen else None;seen.add(family)
        if family not in colours:colours[family]=palette(len(colours)%10)
        axes[0].scatter(m['stock']['magnet_volume_m3_per_module']*1000,r['force_point']['force_N']/1000,label=label,color=colours[family],marker='o' if r['force_point']['point_screen'] else 'x')
    axes[0].set(xlabel='PM volume per 1 m module (litres)',ylabel='Minimum 2D contour lift (kN)',title='80°C, 12 mm, zero current; infinite travel length')
    axes[0].legend(fontsize=7)
    for p in value.get('gap_profiles',[]):
        if p['temperature_C']!=80:continue
        label=next(m['recipe_id'] for m in value['magnetic_candidates'] if m['physical_id']==p['candidate_id'])
        axes[1].plot([q['gap_m']*1000 for q in p['points']],[None if q['force_N'] is None else q['force_N']/1000 for q in p['points']],'o-',label=label)
        for load in p['loads']:
            axes[1].axhline(load['mean_weight_N_per_module']/1000,linestyle='--',alpha=.5,label=label+' '+load['load_case'])
    axes[1].set(xlabel='Exploratory magnetic gap (mm)',ylabel='Lift or mean weight (kN/module)',title='Capacity and zero-current crossing are separate')
    axes[1].legend(fontsize=6)
    fig.suptitle('Research comparisons; no stable hover or installed vehicle qualification',fontsize=11)
    output=io.BytesIO();fig.savefig(output,format='png',dpi=140,metadata={'Software':'OpenSourceRail Halbach scaling'});plt.close(fig);return output.getvalue()


def _readme(v):
    by_m={m['physical_id']:m for m in v['magnetic_candidates']};by_b={b['candidate_id']:b for b in v['vehicle_candidates']};by_c={r['comparison_id']:r for r in v['comparisons']}
    lines=['# Larger Halbach arrays and lighter rolling stock','',
      'OpenSourceRail compares larger onboard neodymium arrays, alternative magnetic layouts and lighter vehicle equipment together. The six-car, 17 m context retains 120 normal / 160 AW3 passengers per car, four 1.4 × 2.1 m doors and the 14,400 passengers/hour/direction requirement. Ordinary guideways remain concrete with passive steel facings; all permanent magnets and support/guidance coils stay onboard.','',
      '**These are engineering research calculations. No replacement train, complete installed mass, stable hover or physical qualification is established.**','',
      '[Project introduction](../../../README.md) · [Complete comparison](comparison.json) · [Gap and temperature profiles](operating.json) · [Finite 3D results](finite.json) · [Source receipt](manifest.json) · [Exact run inputs, meshes and logs](artifacts.json)','',
      '## Executed scope','',
      f"The frozen transverse campaign contains **{v['counts']['physical_geometries']} physical geometries**, **{v['counts']['transverse_field_solves_started']} started field solves**, and **{len(v['comparisons'])} composed magnetic/body comparisons**. The operating profile requests {v['counts']['operating_new_points_requested']} additional points; completed and interrupted records remain explicit. Three-dimensional and postprocess-only diagnostics have their own identities and are never counted as extra physical designs.",'',
      'PM volume grows from the 0.006 m³ control to 0.012, 0.018 and 0.024 m³ per 1 m module. Width, four/eight/sixteen segments, one/two periods, back iron and split differential windings are compared against the same 0.50 × 0.035 m passive facing. Every added magnet, copper conductor and backing/yoke is counted. No proportional-force scaling substitutes for a field solve.','',
      'The old uniform-coil control remains as a failed winding-fill example. New packs use declared spacing/insulation geometry; insulation mass and qualification remain unknown. Differential coils use opposite winding senses around phase-shifted half-arrays, with an explicitly counted central slot and end turns. Signed ±15 A trials retain the original 3.75 A/mm² continuous conductor screen. I²R is reported, but cooling and fast-control qualification remain open.','',
      '![Executed magnetic and gap comparisons](comparison.png)','',
      '## Selected next experiments','',
      'Selection is for the next experiment only. It favours the smallest counted PM volume meeting 1.3 AW3 support in the +2 tonne unclosed-mass sensitivity, requires local member checks at the largest observed magnetic force, rejects known nominal hot-cooling failures, then compares lower accounted mass and fewer PM pieces. Unknown or failed local members cannot win through a fallback. Unknown cost, global body/brace strength, thermal derating and actual installation never become zero.','',
      '| Purpose | Magnetic recipe | Body/equipment option | Accounted AW3 t/car | Hot 12 mm 2D lift kN/module | +2 t / 1.3 support demand kN/module |','|---|---|---|---:|---:|---:|']
    for selected in v['selection']['selected']:
        r=by_c[selected['comparison_id']];m=by_m[selected['magnet_component_id']];b=by_b[selected['body_candidate_id']]
        f=r['force_point'];lines.append(f"| {selected['purpose']} | {m['recipe_id']} | {b['name']} | {r['comparison_aw3_kg_per_car']/1000:.3f} | {f['force_N']/1000:.3f} | {r['support_sensitivities'][2]['required_force_N_per_module']/1000:.3f} |")
    lines+=['','The 0/1/2/3 tonne values are **additional unknown-mass sensitivities**, not actual equipment, confidence bounds or a completed vehicle inventory. The mass figure is an accounted retained-allocation/material comparison. It is not a rigorous bound on the actual installed train.','',
      '## Lighter body and equipment consequences','',
      'The deep six-cell 6082 extrusion frame counts every wall/web, 130 member-end connections, 520 bolts, spreaders and isolation material. It replaces only the 260 exact old frame-stock IDs; panels, collectors, hardpoints and other equipment remain. The compact alternative is retained as a stiffness failure. Larger arrays also overload the original lightweight roof/spreader at small gaps: reinforcement is counted separately, with 40/70 kN per-module design hypotheses. These are observed-load comparisons, not proven bounds on faults or unsampled currents/gaps. Local section/roof/spreader screens do not establish global body, joints, fatigue or bracing; the unbraced 17 m Euler case remains a failed sensitivity.','',
      '| Body option | Counted frame kg/car | Removed stock kg/car | Necessary member disposition |','|---|---:|---:|---|']
    seen_frames=set()
    for b in v['vehicle_candidates']:
        f=b['frame']
        if f and f['frame_id'] not in seen_frames:
            seen_frames.add(f['frame_id']);force=f.get('design_force_N_per_module')
            checked=vehicles.structure_screen(f,35000,magnetic_force_N_per_module=force)
            reference='1.3 × 35 t mean weight' if force is None else f'{force/1000:.0f} kN/module hypothesis'
            lines.append(f"| {b['name'].split('/')[0]} | {f['counted_material_mass_kg']:.2f} | {f['removed_counted_frame_kg']:.2f} | {reference}: {'pass local screens; global held' if checked['member_level_necessary_pass'] else 'fail stiffness/member screen'} |")
    lines+=['','Lighter door leaves and solar-control glazing retain the passenger openings and disjoint old door/window removal accounts. Passenger heat and fresh-air loads do not fall with structural mass. The two- and three-UL700 controls fail the severe humid 60-second door-load scenario even against nominal capacity. The five-unit proposal counts 960 kg and 165 kW nominal thermal capacity; its real 50°C rating, electrical input, roof fit, ventilation and installation remain unqualified. Old two-unit installation bands are not transferred to five units.','',
      '## Operating gap and control','',
      'A larger array can over-support an empty vehicle at 12 mm. The 12/28/44/60 mm, 20/80°C profiles therefore compare mean weight crossings separately from the 1.3 reserve screen. A sampled crossing is neither a solved stable equilibrium nor an accepted operating gap. Larger gap travel has boarding-height, sensor, curve, capture and support-arm consequences that remain unresolved. Log-interpolated proposed states receive no force credit until the separate finite solve evaluates them. Reinforcing the body changes proposed gaps; the table below preserves the actual evaluated component poses and reports their force/load residuals against the revised mass rather than relabelling them as newly solved poses.','',
      'The 1.3 reserve comparison above uses the **12 mm capacity sample**. It does not establish actuator reserve at the larger proposed operating gap. Signed-current samples, lateral/yaw stiffness, damping, voltage reserve, repeated heating, mechanical gap travel and fault control still need to agree in one operating envelope.','',
      '## Finite 3D confirmation','',
      '| Case | Gap mm | Numerical disposition | Full source | Fz contour 1 / 2 kN |','|---|---:|---|---|---|']
    for row in v['finite']['rows']:
        a=row.get('analysis',{});forces=a.get('air_contour_results',[])
        force=' / '.join(f'{f["force_N"][2]/1000:.3f}' for f in forces) if forces else 'unevaluated'
        lines.append(f"| {row['case']} | {row['gap_m']*1000:.3f} | {row['execution_status']} | {row.get('full_source_converged',False)} | {force} |")
    lines+=['','| Case | Actual / currently proposed gap mm | Fz minus revised mean AW3 weight kN, contours 1 / 2 | Minimum Fz minus +2 t / 1.3 demand kN |','|---|---:|---|---:|']
    for state in v['finite_plan']:
        residuals=state['finite_minus_mean_weight_N']
        reserve=state['minimum_finite_minus_plus_2t_reserve_N']
        lines.append(f"| {state['case']} | {state['gap_m']*1000:.3f} / {state['current_proposed_gap_m']*1000:.3f} | "+
            ('unevaluated' if residuals is None else ' / '.join(f'{q/1000:+.3f}' for q in residuals))+' | '+
            ('unevaluated' if reserve is None else f'{reserve/1000:+.3f}')+' |')
    lines+=['','| Selected composition | Largest sampled absolute force kN/module | Local member screen at that load and +2 t mean reserve |','|---|---:|---|']
    for selected in v['selection']['selected']:
        r=by_c[selected['comparison_id']]
        lines.append(f"| {selected['purpose']} | {r['sampled_peak_magnetic_load']['observed_absolute_Fz_N_per_module']/1000:.3f} | {'pass necessary checks; global held' if r['sampled_peak_structure']['member_level_necessary_pass'] else 'fail'} |")
    lines+=['','The finite solver includes all magnetic steel in the declared component, including onboard back iron, with exact material-volume and closed-domain checks. Nearby vehicle joints, reinforcement, wiring, body deformation and the assembled field interaction remain unevaluated. Pose, candidate and evaluation identities remain distinct. The 80°C / zero-current continuation must reach full source before numerical force credit. Mesh, material, contour, local peak and current-map uncertainty remain separate. The steel curve is the retained unvalidated isotropic 50 Hz proxy, not a measured DC or temperature-dependent law.','',
      'Postprocess-only checks on the previous converged solution increase face quadrature density without rerunning its field solve. Those diagnostics can separate sampling effects from field-mesh error; they do not make the original candidate or new candidates qualified. [Quadrature diagnostics](quadrature.json).','',
      'Reproduce with `python -m engineering.halbach_scaling --help`. Stages use immutable fresh directories, bounded ordinary workers and explicit source/solver IDs. Independent differentiation, analytical field/force, geometry/accounting, source/tamper and interruption fixtures accompany the implementation. All accepted physical configurations remain unchanged.','']
    return '\n'.join(lines).encode()


def publish(output,*,transverse,operating_dir,finite_dir,quadrature_dir,root=ROOT):
    before=source_snapshot(root);value=compare(transverse,root,operating_dir=operating_dir)
    operating.verify(operating_dir,root=root);op=json.loads((Path(operating_dir)/'result.json').read_bytes())
    selected_ids=[r['magnet_component_id'] for r in value['selection']['selected']]
    op_request=json.loads((Path(operating_dir)/'request.json').read_bytes())
    if [b['physical_id'] for b in op_request['bundles']]!=selected_ids:raise ValueError('operating candidates differ from declared selection')
    profiles=coupling.gap_profiles(op,value['selection'],value['comparisons']);plan=coupling.finite_plan(value['magnetic_candidates'],value['selection'],value['comparisons'],profiles)
    finite.verify(finite_dir,root);fin=json.loads((Path(finite_dir)/'result.json').read_bytes());fr=json.loads((Path(finite_dir)/'request.json').read_bytes())
    states=coupling.evaluated_finite_states(fr,fin,plan,value['selection'],value['comparisons'],profiles)
    finite.verify(quadrature_dir,root);quad=json.loads((Path(quadrature_dir)/'result.json').read_bytes())
    raw=json.loads((Path(transverse)/'result.json').read_bytes())
    value.update(gap_profiles=profiles,finite=fin,finite_plan=states,next_gap_proposals=plan,counts=dict(physical_geometries=len(value['magnetic_candidates']),
        transverse_field_solves_started=raw['counts']['field_solves_started'],operating_new_points_requested=op['new_field_points'],
        finite_cases=len(fin['rows']),finite_full_source=sum(r.get('full_source_converged',False) for r in fin['rows'])))
    value['study_id']=identity(value);unaccepted(value)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    write(output/'comparison.json',value);write(output/'operating.json',op);write(output/'finite.json',fin);write(output/'quadrature.json',quad)
    atomic_immutable(output/'comparison.png',_plot(value));atomic_immutable(output/'README.md',_readme(value))
    archives={}
    for name,directory in dict(transverse=transverse,operating=operating_dir,finite=finite_dir,quadrature=quadrature_dir).items():
        filename=name+'-artifacts.tar.gz';raw_archive=_archive({name:directory})
        if len(raw_archive)>95*1024**2:raise ValueError('one bounded archive exceeded repository size budget')
        atomic_immutable(output/filename,raw_archive);archives[name]=dict(file=filename,sha256=sha256(raw_archive).hexdigest(),bytes=len(raw_archive))
    write(output/'artifacts.json',archives)
    if source_snapshot(root)!=before:raise ValueError('publication sources changed')
    manifest=dict(schema='osr-halbach-scaling-publication/1',study_id=value['study_id'],source_sha256=before,
                  files_sha256=inventory(output,('manifest.json',)),**FLAGS);manifest['manifest_id']=identity(manifest);write(output/'manifest.json',manifest)
    return manifest


def verify_publication(output,root=ROOT):
    d=Path(output);m=json.loads((d/'manifest.json').read_bytes());unaccepted(m)
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}) or m['source_sha256']!=source_snapshot(root):raise ValueError('publication identity/source differs')
    if m['files_sha256']!=inventory(d,('manifest.json',)):raise ValueError('publication payload differs')
    v=json.loads((d/'comparison.json').read_bytes());unaccepted(v)
    if v['study_id']!=identity({k:x for k,x in v.items() if k!='study_id'}) or m['study_id']!=v['study_id']:raise ValueError('study identity differs')
    if (d/'README.md').read_bytes()!=_readme(v):raise ValueError('report text differs')
    # Reconstruct every stage and derived output from a bounded ordinary archive;
    # no solver is rerun and resealing a fabricated mass/force cannot admit it.
    with tempfile.TemporaryDirectory(prefix='osr-halbach-readback-') as temporary:
        target=Path(temporary);archives=json.loads((d/'artifacts.json').read_bytes())
        if set(archives)!={'transverse','operating','finite','quadrature'}:raise ValueError('exact stage archives required')
        for label,record in archives.items():
            if record['file']!=label+'-artifacts.tar.gz':raise ValueError('archive path differs')
            path=d/record['file']
            if sha256(path.read_bytes()).hexdigest()!=record['sha256'] or path.stat().st_size!=record['bytes']:raise ValueError('archive identity differs')
            _extract(path,target,label)
        fresh=target/'publication'
        publish(fresh,transverse=target/'transverse',operating_dir=target/'operating',finite_dir=target/'finite',quadrature_dir=target/'quadrature',root=root)
        if inventory(fresh)!=inventory(d):raise ValueError('fresh derived publication differs')
    return dict(current=True,study_id=m['study_id'],physical_accepted=False)


def _extract(path,target,label):
    size=0;names=set()
    with tarfile.open(path,'r:gz') as archive:
        for member in archive:
            name=PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or '..' in name.parts or '\\' in member.name
                    or name.as_posix()!=member.name or not name.parts or name.parts[0]!=label
                    or member.name in names or not 0<=member.size<=128*1024**2):raise ValueError('ordinary bounded archive members required')
            names.add(member.name);size+=member.size
            if size>768*1024**2 or len(names)>5000:raise ValueError('archive extraction budget exceeded')
            destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True)
            with archive.extractfile(member) as source:atomic_immutable(destination,source.read())
