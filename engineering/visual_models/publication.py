"""Publish compact, source-checked CAD and rendered communication models."""
import argparse
import gzip
import json
import shutil
import importlib
import sys
import tempfile
import types
import zipfile
from pathlib import Path
from . import core

ROOT=Path(__file__).resolve().parents[2]
WORKERS=('__main__.py','render_blender.py','cad_freecad.py','compose.py','publication.py')


def snapshot_replay(output,manifest):
    """Replay the published producer epoch, without silently adopting new inputs."""
    with tempfile.TemporaryDirectory(prefix='osr-model-replay-') as folder:
        folder=Path(folder)
        with zipfile.ZipFile(output/'source-snapshot.zip') as archive:
            if set(archive.namelist())!=set(manifest['source_sha256']):raise ValueError('Source snapshot coverage differs')
            for name,h in manifest['source_sha256'].items():
                if Path(name).is_absolute() or '..' in Path(name).parts or archive.getinfo(name).file_size>8*1024**2:
                    raise ValueError('Bounded repository source required')
                p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(name))
                if core.digest(p)!=h:raise ValueError('Source snapshot hash differs: '+name)
        name='_osr_visual_snapshot_'+manifest['publication_id'][:16]
        package=types.ModuleType(name);package.__path__=[str(folder/'engineering/visual_models')];sys.modules[name]=package
        try:
            frozen=importlib.import_module(name+'.core');actual,sources=frozen.collect(folder)
            guide=importlib.import_module(name+'.publication').introduction(actual)
        finally:
            for key in list(sys.modules):
                if key==name or key.startswith(name+'.'):del sys.modules[key]
    return actual,sources,guide


def _write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(core.encoded(value))


def introduction(assemblies):
    lines=['# Engineering models', '',
        '[Project introduction](../../README.md) · [Current engineering](../design-engine/current/README.md)', '',
        'These are parametric 3D assemblies rendered from the same explicit geometry that is exported to CAD. '
        'They explain the station mechanisms, construction and fabrication routes. Dimensions copied from the '
        'current vehicle and beam are distinguished from proposed equipment envelopes and shop tooling.', '',
        '**Use:** compare layouts, inspect parts and discuss manufacturing. These are outline communication '
        'models; they are not released drawings, a lifting plan, a pressure-vessel design or an operating system. '
        'The selected railway and its qualification status are unchanged.', '',
        '## Station capture, storage and launch', '',
        'The illustrated research layout uses five staged cable arrestors, a hydraulic energy store and a '
        'controlled rear launch shuttle driven by a common capstan. Stored energy supplies the first part of '
        'departure; an optional motor supplies the remaining acceleration. Independent train braking, energy '
        'isolation, mechanical retention, guards, sensing, wiring and maintenance access are shown separately.', '',
        'The source control uses a **160 t effective point mass**, arrival capture from **10 m/s** and a '
        '**60 km/h** departure study. Its calculated capture travel is **70.5 m**; recovered launch travel '
        'is **43.35 m**, followed by **128.94 m** of boosted travel. These are train-motion distances, not '
        'validated equipment lengths. The 8.8 MJ store requirement and proposed vessel envelopes do not '
        'establish pressure containment, installed storage mass or achievable performance. Neither this '
        'mechanism nor its speed is a mandatory design choice.', '',
        'The source six-car formation occupies **104.5 m**, including five 0.5 m coupling gaps. Local close-up '
        'coordinates are declared in each recipe. The launch view includes a separate proposed shuttle '
        'runout; coupling loads, cart disengagement, train compression, jerk and failure behaviour require analysis.', '',
        '## Construction and fabrication', '',
        '- **Whole-span crane erection:** surveyed supports and bearings, delivery trailer, crawler crane, '
        'spreader and temporary restraint. The source bare lifting stock is about **59.18 t**, excluding '
        'rigging and unresolved attachments. Crane capacity, working radius, ground bearing and temporary '
        'stability must be engineered for the site.',
        '- **Overhead gantry alternative:** deliver and lower the same 20 m span from a launching gantry. '
        'This is an alternative erection scheme; its steelwork, support reactions and launch sequence are proposals. The illustrated seats give a proposed 19.4 m bearing-centre spacing beneath 20 m stock; the source 20 m analytical result is not inherited by that layout.',
        '- **Precasting:** reusable outer forms, a proposed collapsible core, cage jig, two proposed tendon '
        'ducts and inspection specimens. The six disjoint source concrete solids total **22.2816 m³**. '
        'The core extraction, bar schedule, tendon/anchorage detailing, curing and release strength remain to be designed.',
        '- **Vehicle assembly:** all **2,482 located source parts** are preserved, including drilled floor '
        'panels. Their **9,131.80 kg** is located stock, not the complete car tare. Render-only explosion '
        'separates roof, seating, covers, doors and bogies; downloadable geometry retains source positions.',
        '- **Rails and running gear:** purchase standard rolled rail, then finish, join, inspect and fasten '
        'locally; assemble and inspect wheelsets, bearings and passive bogies. Tooling is proposed. The '
        '60E1 display contour follows a manufacturer drawing and nominal dimensions; its approximate area '
        'is not a qualified rolling/contact profile or a replacement for the nominal rail mass.', '',
        'An outline wheelset route is: receive traceable wheel/axle stock; finish and inspect interfaces; '
        'record the specified press-fit operation; inspect the assembled wheelset; mount bearings/axleboxes; '
        'then check the bogie and brake installation. [Lucchini’s production sequence](https://lucchinirs.com/divisions/railway-division/railway-products/wheelsets/) '
        'and [GHH-BONATRANS inspection and maintenance scope](https://www.ghhbonatrans.com/en/products-and-services/service/) '
        'provide industrial context. The displayed press, gauges and inspection positions are proposals, '
        'not qualified machines or process specifications. Two 8-hour factory/civil shifts remain planning '
        'inputs; a workstation picture does not establish cycle time or annual capacity.', '',
        '## Inspect and download', '',
        'STL opens in GitHub’s 3D viewer. GLB keeps colours and part metadata; FCStd is the native FreeCAD '
        'solid assembly grouped by subsystem, with part IDs and SI recipes. Display colours are separate '
        'from source material tags; neither is a material certificate. STEP is gzip-compressed: decompress before opening it in CAD. **GLB uses metres; '
        'STL, STEP and FCStd use millimetres.** No presentation explosion is applied to downloaded models.', '']
    for a in assemblies:
        name=a['id']
        lines += ['### '+a['title'],'',f"![{a['title']}: source geometry and proposed layout](images/{name}.webp)",'',
            f'[Rotate STL](models/{name}.stl) · [Coloured GLB](models/{name}.glb) · '
            f'[FreeCAD solids](models/{name}.FCStd) · [STEP solids (.gz)](models/{name}.step.gz) · '
            f'[Exact recipe (.json.gz)](definitions/{name}.json.gz)','']
    lines += ['## Sources, checks and reproduction','',
        'The [manifest](manifest.json) binds each visual-study identity to source files, geometry recipes, '
        'native execution receipts and output hashes. Visual-study identities are separate from physical '
        'candidate, selection and evaluation identities. The station mechanism is a new layout proposal; '
        'it does not inherit engineering acceptance or the installed price of its source motion example.', '',
        'The [source snapshot](source-snapshot.zip) preserves the exact producer and input epoch. Verification '
        'replays that snapshot and checks its vehicle geometry against the current reference. A price or '
        'unrelated evaluator update does not require rendering unchanged geometry again. Native workers '
        'are re-executed only when explicitly requested; stored receipts are not new physical evidence.', '',
        'FreeCAD exports were reopened as both FCStd and STEP. Every native shape was checked for validity '
        'and positive volume; source primitives were compared with analytical volumes. GLB was imported '
        'again to check all part IDs and bounds. Binary STL was read back to check scale and bounds. '
        'These are digital integrity checks, not structural, manufacturing or safety validation. Summed '
        'solid volumes include tooling and overlapping equipment envelopes and are not installed material takeoffs.', '',
        'Primary references: [FHWA prefabricated bridge assembly](https://www.fhwa.dot.gov/bridge/prefab/if09010/01a.cfm), '
        '[Caltrans construction guidance](https://dot.ca.gov/-/media/dot-media/programs/engineering/documents/structureconstruction/rcm/sc-rcm-compiled.pdf), '
        '[Freyssinet erection methods](https://www.freyssinet.com/solution/build/bridge-deck-construction/precast-segmental-erection/), '
        '[voestalpine 60E1 drawing](https://www.voestalpine.com/highperformancemetals/argentina/app/uploads/sites/264/2024/09/voestalpine-60E1.pdf) '
        'and [ArcelorMittal nominal rail data](https://rails.arcelormittal.com/profiles/transport-rails/european-standards/). '
        'They support the methods and reference dimensions; none approves these proposed assemblies.', '',
        'The editable generators are in [`engineering/visual_models/`](../../engineering/visual_models/). '
        'Blender 5.2 and FreeCAD 1.1 were used through their installed Flatpak applications. Pillow and '
        'Roboto fonts compose the callouts. Runs use four Blender CPU threads and one native CAD thread. '
        'Raw images, logs and intermediate source snapshots stay in ignored `build/` directories.', '',
        '```bash',
        'python -m engineering.visual_models definitions --output build/model-definitions',
        'python -m engineering.visual_models render --definitions build/model-definitions \\\n+  --assembly arrestor-storage --output build/model-run/render/arrestor-storage',
        'python -m engineering.visual_models cad --definitions build/model-definitions \\\n+  --assembly arrestor-storage --output build/model-run/cad/arrestor-storage',
        '# Repeat render and cad for the eight IDs in model-definitions/manifest.json.',
        'python -m engineering.visual_models.publication publish --definitions build/model-definitions \\\n+  --runs build/model-run --output build/model-publication',
        'python -m engineering.visual_models.publication verify --output build/model-publication',
        '```','',
        'Publishing requires fresh output paths and all eight completed runs. Native workers execute as '
        'ordinary user processes; source hashes and before/after checks detect drift, but are not an OS '
        'sandbox or independent authenticated measurements.', '']
    return '\n'.join(lines)


def publish(definitions,runs,output,root=ROOT):
    from .__main__ import selected
    root=Path(root);definitions=Path(definitions);runs=Path(runs);output=Path(output)
    if output.exists():raise ValueError('Fresh model publication directory required')
    d=json.loads((definitions/'manifest.json').read_bytes())
    assemblies=[selected(definitions,a['id']) for a in d['assemblies']]
    sources=dict(d['source_sha256'])
    sources.update({'engineering/visual_models/'+n:core.digest(root/'engineering/visual_models'/n) for n in WORKERS})
    # Validate every input before creating a reviewable publication.
    receipts={}
    for a in assemblies:
        ident=a['id'];receipts[ident]={}
        for kind,worker,receipt in (('render','render_blender.py','render.json'),('cad','cad_freecad.py','cad.json')):
            folder=runs/kind/ident;r=json.loads((folder/receipt).read_bytes())
            if r['visual_study_id']!=a['visual_study_id'] or r['input_sha256']!=core.digest(definitions/(ident+'.json')):
                raise ValueError('Native execution input differs: '+ident)
            if r['worker_source_sha256']!=sources['engineering/visual_models/'+worker]:
                raise ValueError('Native execution worker differs: '+ident)
            for name,h in r['files_sha256'].items():
                if core.digest(folder/name)!=h:raise ValueError('Executed asset changed: '+ident+'/'+name)
            if any(r.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release')):
                raise ValueError('Visual execution cannot promote physical acceptance')
            if kind=='render' and (r['render_width']<3000 or not r['glb_reopened'] or not r['stl_reopened'] or r['unmapped_materials']):
                raise ValueError('Final full-resolution, reopened mesh exports required')
            if kind=='cad' and (not r['all_native_shapes_valid'] or r['display_offsets_applied']):
                raise ValueError('Checked source-pose native CAD required')
            if kind=='cad' and (r['parts']!=len(a['entities']) or r.get('assembly_groups',0)<1):
                raise ValueError('Complete grouped native assembly required')
            if kind=='render' and r['glb_reopened_parts']!=len(a['entities']):
                raise ValueError('Complete reopened mesh assembly required')
            if kind=='render' and (folder/(ident+'.stl')).stat().st_size>=10_000_000:
                raise ValueError('Keep STL within GitHub interactive preview limit')
            receipts[ident][kind]=r
    output.mkdir(parents=True)
    with zipfile.ZipFile(output/'source-snapshot.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,h in sorted(sources.items()):
            if core.digest(root/name)!=h:raise ValueError('Source changed before snapshot: '+name)
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(item,(root/name).read_bytes(),compresslevel=9)
    from .compose import plate
    for a in assemblies:
        ident=a['id'];rdir=runs/'render'/ident;cdir=runs/'cad'/ident
        p=output/'definitions'/(ident+'.json.gz');p.parent.mkdir(exist_ok=True)
        p.write_bytes(gzip.compress(core.encoded(a),mtime=0))
        for ext,folder in (('glb',rdir),('stl',rdir),('FCStd',cdir)):
            p=output/'models'/(ident+'.'+ext);p.parent.mkdir(exist_ok=True);shutil.copyfile(folder/p.name,p)
        (output/'models'/(ident+'.step.gz')).write_bytes(gzip.compress((cdir/(ident+'.step')).read_bytes(),mtime=0))
        plate(a,rdir,output/'images'/(ident+'.webp'))
        _write(output/'checks'/(ident+'.json'),receipts[ident])
    (output/'README.md').write_text(introduction(assemblies))
    import PIL
    from .compose import FONT,BOLD
    m=dict(schema='osr-engineering-visual-publication/1',source_sha256=sources,
        assemblies=[dict(id=a['id'],title=a['title'],visual_study_id=a['visual_study_id'],parts=len(a['entities'])) for a in assemblies],
        files_sha256={p.relative_to(output).as_posix():core.digest(p) for p in sorted(output.rglob('*')) if p.is_file()},
        units=dict(glb='metres',stl='millimetres',step='millimetres',FCStd='millimetres'),
        composition=dict(pillow_version=PIL.__version__,font_sha256={str(p):core.digest(p) for p in (FONT,BOLD)}),**core.FLAGS)
    m['publication_id']=core.identity(m);_write(output/'manifest.json',m)
    return verify(output,root)


def verify(output,root=ROOT):
    output=Path(output);root=Path(root);m=json.loads((output/'manifest.json').read_bytes())
    if m['publication_id']!=core.identity({k:v for k,v in m.items() if k!='publication_id'}):raise ValueError('Visual publication identity differs')
    if any(m.get(k) is not False for k in core.FLAGS):raise ValueError('Visual publication cannot qualify hardware')
    changed=[name for name,h in m['source_sha256'].items() if not (root/name).is_file() or core.digest(root/name)!=h]
    files={p.relative_to(output).as_posix():core.digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if files!=m['files_sha256']:raise ValueError('Published visual files differ')
    actual,sources,guide=snapshot_replay(output,m)
    if any(m['source_sha256'].get(n)!=h for n,h in sources.items()):raise ValueError('Visual source coverage differs')
    expected=[dict(id=a['id'],title=a['title'],visual_study_id=a['visual_study_id'],parts=len(a['entities'])) for a in actual]
    if m['assemblies']!=expected:raise ValueError('Assembly coverage or identities differ')
    for a in actual:
        name=a['id'];p=output/'definitions'/(name+'.json.gz')
        if gzip.decompress(p.read_bytes())!=core.encoded(a):raise ValueError('Visual definition replay differs: '+name)
        r=json.loads((output/'checks'/(name+'.json')).read_bytes())
        for kind in ('render','cad'):
            if r[kind]['visual_study_id']!=a['visual_study_id']:raise ValueError('Native identity differs')
            worker='render_blender.py' if kind=='render' else 'cad_freecad.py'
            if r[kind]['worker_source_sha256']!=m['source_sha256']['engineering/visual_models/'+worker]:
                raise ValueError('Native worker source differs')
            if r[kind]['input_sha256']!=core.identity(a):raise ValueError('Native input differs')
            if any(r[kind].get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release')):
                raise ValueError('Native model cannot qualify hardware')
            for filename,h in r[kind]['files_sha256'].items():
                if filename=='raw.png':continue  # Retained privately; not a published deliverable.
                p=output/'models'/filename
                raw=gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()) if filename.endswith('.step') else p.read_bytes()
                from hashlib import sha256
                if sha256(raw).hexdigest()!=h:raise ValueError('Native exported bytes differ: '+filename)
    if (output/'README.md').read_text()!=guide:raise ValueError('Model guide differs')
    current=json.loads(gzip.decompress((root/'docs/design-engine/current/evaluation.json.gz').read_bytes()))
    with zipfile.ZipFile(output/'source-snapshot.zip') as archive:
        source=json.loads(gzip.decompress(archive.read('docs/design-engine/current/evaluation.json.gz')))
    # Costs/evaluation epochs may change; the illustrated physical stock may not.
    if current['vehicle']['geometry_parts']!=source['vehicle']['geometry_parts']:
        raise ValueError('Illustrated physical stock differs from current reference: vehicle')
    civil_keys=('family','span_m','section','diaphragm_definition','concrete_m3','concrete_mass_kg',
        'reinforcement_kg','prestress_strands','strand_area_m2','prestress_kg','prestress_anchorage_kg','prestress_reference')
    for key in civil_keys:
        if current['civil']['selected_reference'].get(key)!=source['civil']['selected_reference'].get(key):
            raise ValueError('Illustrated physical stock differs from current reference: civil/'+key)
    return dict(verified=True,assemblies=len(actual),parts=sum(len(a['entities']) for a in actual),publication_id=m['publication_id'],
        source_epoch_current=not changed,changed_current_sources=changed,reference_geometry_current=True,**core.FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('publish','verify'))
    p.add_argument('--definitions',type=Path);p.add_argument('--runs',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.action=='publish' and (not a.definitions or not a.runs):p.error('--definitions and --runs required')
    print(json.dumps(publish(a.definitions,a.runs,a.output) if a.action=='publish' else verify(a.output),sort_keys=True))


if __name__=='__main__':main()
