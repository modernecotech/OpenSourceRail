"""Publish actual CAD pixels and native FEM data without changing a design.

Render jobs stay private and immutable. This small public packet retains their
recipes, receipts and exact image hashes; the FEM export can be replotted offline.
"""
from pathlib import Path
import argparse
import gzip
import json
import shutil
import subprocess
import tempfile

from PIL import Image
from . import cad, fem
from .compose import plate

ROOT = Path(__file__).resolve().parents[2]
DEST = 'docs/assets/engineering-gallery-v06'
SOURCES = ('tools/engineering_gallery/cad.py', 'tools/engineering_gallery/blender.py',
           'tools/engineering_gallery/compose.py', 'tools/engineering_gallery/fem.py',
           'tools/engineering_gallery/publication.py')
CARDS = {
    'vehicle-car0': ('Located vehicle · one-car cutaway', 'Source-defined stock, fitout and equipment envelopes',
        'Roof and near-side wall hidden for inspection · proposed installation',
        'docs/design-engine/reconciled-pilot-bogie-detail/README.md'),
    'bogie-cradle': ('Bogie frame & drive cradle', 'Native SolidCraft · 34 gross-stock solids',
        'Supplier housings and completed joints unresolved · fit HOLD',
        'docs/design-engine/powered-bogie-detail/README.md'),
    'launch-assembly': ('Controlled launch · shuttle assembly', 'Native SolidCraft · bored clevis, open RHS and guide wheels',
        '122 material regions · guards ghosted to expose the mechanism',
        'docs/design-engine/launch-detail/README.md'),
    'launch-clevis': ('Launch coupling · pin & clevis', 'Native SolidCraft · subassembly detail',
        'Bored ears, pin and retainers · surrounding stock ghosted',
        'docs/design-engine/launch-detail/README.md'),
    'civil-assembly': ('Viaduct · proposed installed assembly', 'Two tracks · match-cast segments, bearings, piers and footings',
        '265 located entities · separate from the continuous bonded FEM model',
        'docs/design-engine/reconciled-pilot-bogie-detail/README.md'),
}


def dump(path, value):
    Path(path).write_bytes(fem.encoded(value))


def sealed(value):
    return dict(value, evaluation_id=cad.identity(value))


def inventory(folder):
    folder=Path(folder);entries={}
    for p in sorted(folder.rglob('*')):
        if p.is_symlink(): raise ValueError('Gallery artifacts must be ordinary files/directories')
        if p.is_file() and p != folder/'manifest.json':
            entries[str(p.relative_to(folder))]=dict(bytes=p.stat().st_size,sha256=cad.digest(p))
    return entries


def _gzip_copy(source, target):
    with Path(source).open('rb') as inp, Path(target).open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as out:
            shutil.copyfileobj(inp, out)


def _cad_record(run, root, *, name=None, image='raw.png'):
    run = Path(run)
    result_file=run/'result.json'
    if not result_file.exists(): result_file=run/'image-record.json'
    recipe, result = cad.read(run/'recipe.json'), cad.read(result_file)
    cad.validate(recipe, root)
    fem.check_seal(result)
    expected = {r['id']: r for r in cad.recipes(root)}
    if recipe['id'] != name or recipe != expected.get(name):
        raise ValueError('Render recipe/name differs from declared view')
    for key, value in cad.FLAGS.items():
        if result.get(key) is not value: raise ValueError('Render cannot confer acceptance')
    held=result.get('schema')=='osr-engineering-gallery-held-image/1'
    if held:
        # A known completed image survives a failed supervisor/result writer.
        # Never relabel that execution as completed or its missing usage as zero.
        audit=cad.read(run/'failure-audit.json')
        if audit['audit_id'] != cad.identity({k:v for k,v in audit.items() if k!='audit_id'}): raise ValueError('Held audit changed')
        geometry=cad.read(run/'geometry.json');scene=cad.read(run/'scene.json')
        log=(run/'stdout.log').read_text()
        if (name!='vehicle-car0' or result['execution']!='held' or result['exit_code'] is not None or
                result['failure']!='runtime-budget' or result.get('image_complete') is not True or
                result['failure_audit_sha256']!=cad.digest(run/'failure-audit.json') or
                result['geometry_sha256']!=cad.digest(run/'geometry.json') or
                audit['retained_image_sha256']!=result['image_sha256'] or
                audit['retained_geometry_sha256']!=result['geometry_sha256'] or
                audit['supervisor_timeout_s']!=600 or audit['supervisor_usage_bytes']!=0 or
                not audit['result_json_absent'] or not audit['source_unchanged'] or
                audit['execution']!='held' or audit['candidate_id']!=recipe['candidate_id'] or
                audit['recipe_id']!=recipe['recipe_id'] or
                geometry['candidate_id']!=recipe['candidate_id'] or geometry['recipe_id']!=recipe['recipe_id'] or
                scene['candidate_id']!=recipe['candidate_id'] or scene['recipe_id']!=recipe['recipe_id'] or
                geometry['source_geometry_resized'] or geometry['triangles']>scene['maximum_triangles'] or
                'Saved:' not in log or 'raw.png' not in log or 'Blender quit' not in log):
            raise ValueError('Unknown held-image failure contract')
        for key in cad.FLAGS:
            if audit.get(key) is not False: raise ValueError('Held render cannot confer acceptance')
    elif result['execution']!='completed' or result['exit_code']!=0:
        raise ValueError('Incomplete CAD render')
    if (result['candidate_id'] != recipe['candidate_id'] or result['recipe_id'] != recipe['recipe_id'] or
            result['image_sha256'] != cad.digest(run/image) or not result['source_unchanged']):
        raise ValueError('Incomplete or mixed CAD render')
    if Image.open(run/image).size != (3000,1900):
        raise ValueError('Final-resolution CAD image required')
    return recipe, result


def publish(selection, output, *, root=ROOT):
    """Compose verified saved images, retaining any explicit execution holds."""
    root, output = Path(root), Path(output)
    if output.exists():
        raise ValueError('Publish to a fresh directory, then review/replace explicitly')
    if set(selection['cad']) != set(CARDS):
        raise ValueError('Five explicit assembly/subassembly jobs required')
    checked = {name: _cad_record(run, root, name=name) for name, run in selection['cad'].items()}
    froot = Path(selection['fem']); handoff_file = selection.get('fem_handoff','handoff-v2.json')
    handoff = cad.read(froot/handoff_file); fem.check_seal(handoff)
    for name, record in handoff['files'].items():
        p = froot/name
        if p.stat().st_size != record['bytes'] or cad.digest(p) != record['sha256']:
            raise ValueError('FEM handoff changed: '+name)
    output.mkdir(parents=True)
    records = {}
    for name, (recipe, result) in checked.items():
        run = Path(selection['cad'][name]); evidence = output/'evidence'/name; evidence.mkdir(parents=True)
        for file in ('recipe.json','result.json','image-record.json','failure-audit.json','request.json','scene.json','geometry.json','usage.json','stdout.log','stderr.log'):
            if (run/file).is_file(): shutil.copyfile(run/file, evidence/file)
        shutil.copyfile(run/'raw.png', evidence/'native.png')
        title, subtitle, footer, link = CARDS[name]
        layout = plate(run/'raw.png', output/(name+'.webp'), title=title, subtitle=subtitle, footer=footer)
        records[name] = dict(candidate_id=recipe['candidate_id'], recipe_id=recipe['recipe_id'],
            render_evaluation_id=result['evaluation_id'], source_evaluation_id=recipe['input_evaluation_id'],
            image=name+'.webp', raw_image='evidence/'+name+'/native.png', dossier=link,
            caption=recipe['caption'], layout=layout, observed_usage=result['usage'],
            render_execution=result['execution'],render_failure=result['failure'],
            observed_memory_target_met=result['observed_memory_target_met'],wall_s=result['wall_s'], **cad.FLAGS)
        if result['execution']=='held':
            records[name]['caption']+=' Complete saved image retained from a held 600-second render; runtime and observed memory targets missed, supervisor usage unavailable.'
        records[name]['camera_units']=('Native SolidCraft target/distance: millimetres; yaw/pitch/FOV: radians'
            if recipe['kind']=='native' else 'Source geometry: metres; direction is dimensionless')
    evidence = output/'evidence'/'civil-fem'; evidence.mkdir(parents=True)
    execution = froot/'fieldcraft-request-v1'
    for file in ('request.json','result.json','commands.json','postprocess-rejection-01.json'):
        shutil.copyfile(execution/file, evidence/file)
    for file in ('stdin.jsonl','stdout.jsonl','stderr.txt','usage.json','execution.json'):
        if (execution/'execution'/file).is_file(): shutil.copyfile(execution/'execution'/file,evidence/file)
    shutil.copyfile(froot/handoff_file, evidence/'handoff.json')
    shutil.copyfile(froot/handoff['final_image'], evidence/'native-field.png')
    shutil.copyfile((froot/handoff['final_image']).with_suffix('.json'),evidence/'figure.json')
    shutil.copyfile(froot/'civil-fieldcraft-field-v2.json.gz',evidence/'field.json.gz')
    _gzip_copy(execution/'execution'/'field.vtu',evidence/'field.vtu.gz')
    _gzip_copy(execution/'inputs'/'mesh.json',evidence/'mesh.json.gz')
    Image.open(evidence/'native-field.png').convert('RGB').save(output/'civil-fem.webp',format='WEBP',quality=94,method=6)
    records['civil-fem'] = dict(candidate_id=handoff['candidate_id'], source_evaluation_id=handoff['civil_evaluation_id'],
        native_result_id=handoff['validated_result_id'], image='civil-fem.webp',
        raw_image='evidence/civil-fem/native-field.png', dossier='docs/design-engine/reconciled-pilot-bogie-detail/README.md',
        caption='FieldCraft full native displacement field; 100× deformed shape, millimetre legend. Continuous gross elastic beam, normal-base load and ideal bearing lines; not the segmented assembly analysis.',
        deformation_scale=100, **fem.FLAGS)
    manifest = sealed(dict(schema='osr-readme-engineering-gallery/1',
        purpose='Multi-candidate presentation; no shared installed-architecture selection',
        producer_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        source_sha256={name:cad.digest(root/name) for name in SOURCES}, cards=records,
        retained_failures='Earlier render attempts and native postprocessing rejection remain in private run evidence; rejection copied here.',
        files=inventory(output), **fem.FLAGS))
    dump(output/'manifest.json',manifest)
    return verify(output,root=root)


def _materialize(folder, output):
    evidence = Path(folder)/'evidence'/'civil-fem'; output = Path(output)
    (output/'inputs').mkdir();(output/'execution').mkdir()
    for source, target in [('mesh.json.gz','inputs/mesh.json'),('field.vtu.gz','execution/field.vtu')]:
        if not (evidence/source).is_file() or (evidence/source).is_symlink(): raise ValueError('Ordinary compressed field required')
        with gzip.open(evidence/source,'rb') as inp,(output/target).open('wb') as out:
            count=0
            while block:=inp.read(1024*1024):
                count+=len(block)
                if count>64*1024**2: raise ValueError('Expanded native artifact exceeds original 64 MiB file budget')
                out.write(block)
    shutil.copyfile(evidence/'result.json',output/'result.json')


def verify(folder, *, root=ROOT):
    folder, root = Path(folder), Path(root)
    manifest=cad.read(folder/'manifest.json');fem.check_seal(manifest)
    if inventory(folder) != manifest['files']: raise ValueError('Gallery bytes or inventory changed')
    if set(manifest['cards']) != set(CARDS)|{'civil-fem'}: raise ValueError('Gallery card inventory changed')
    for key, value in fem.FLAGS.items():
        if manifest.get(key) is not value: raise ValueError('Gallery cannot confer acceptance')
    if set(manifest['source_sha256']) != set(SOURCES): raise ValueError('Producer source inventory changed')
    for name, digest in manifest['source_sha256'].items():
        if cad.digest(root/name) != digest: raise ValueError('Gallery producer source changed: '+name)
    for name in CARDS:
        record = manifest['cards'][name]; evidence=folder/'evidence'/name
        recipe, result = _cad_record(evidence,root,name=name,image='native.png')
        if (recipe['candidate_id'] != record['candidate_id'] or recipe['recipe_id'] != record['recipe_id'] or
                recipe['input_evaluation_id'] != record['source_evaluation_id'] or
                result['candidate_id'] != record['candidate_id'] or result['recipe_id'] != record['recipe_id'] or
                result['evaluation_id'] != record['render_evaluation_id'] or result['image_sha256'] != cad.digest(evidence/'native.png') or
                result['execution']!=record['render_execution'] or result['failure']!=record['render_failure'] or
                result['usage']!=record['observed_usage'] or result['wall_s']!=record['wall_s'] or
                result['observed_memory_target_met']!=record['observed_memory_target_met']):
            raise ValueError('Mixed gallery candidate or render')
    for record in manifest['cards'].values():
        if Image.open(folder/record['image']).size != (3000,1900): raise ValueError('Gallery dimensions changed')
        for key in cad.FLAGS:
            if record.get(key) is not False: raise ValueError('Image cannot confer acceptance')
    evidence=folder/'evidence'/'civil-fem'
    field=cad.read(evidence/'field.json.gz');fem.check_seal(field)
    request=cad.read(evidence/'request.json');fem.check_seal(request)
    result=cad.read(evidence/'result.json');fem.check_seal(result)
    figure=cad.read(evidence/'figure.json');fem.check_seal(figure)
    handoff=cad.read(evidence/'handoff.json');fem.check_seal(handoff)
    for leaf in (field,request,result,figure,handoff):
        for key,value in fem.FLAGS.items():
            if leaf.get(key) is not value: raise ValueError('FEM evidence cannot confer acceptance')
    if (result['execution']['execution'] != 'executed' or result['execution']['returncode'] != 0 or
            not result['source_unchanged'] or not result['native_mesh_byte_identical']):
        raise ValueError('FEM replay did not complete with unchanged source/mesh')
    if (request['expected'] != fem.EXPECTED or result['request_id'] != request['evaluation_id'] or
            field['request_id'] != request['evaluation_id'] or figure['request_id'] != request['evaluation_id'] or
            field['native_result_id'] != result['evaluation_id'] or
            manifest['cards']['civil-fem']['native_result_id'] != result['evaluation_id'] or
            handoff['validated_result_id'] != result['evaluation_id'] or
            field['tool_pin'] != request['tool_pin'] or
            field['native_mesh_bin_sha256'] != result['native_mesh_bin_sha256'] or
            figure['figure_sha256'] != cad.digest(evidence/'native-field.png') or
            figure['field_sha256'] != result['full_field_sha256'] or
            field['native_vtu_sha256'] != result['full_field_sha256'] or
            figure['deformation_scale'] != 100 or figure['legend_units'] != 'mm'):
        raise ValueError('FEM evidence links differ')
    if (field['candidate_id'] != manifest['cards']['civil-fem']['candidate_id'] or
            field['civil_evaluation_id'] != manifest['cards']['civil-fem']['source_evaluation_id'] or
            field['candidate_id']!=fem.EXPECTED['candidate_id'] or
            field['civil_evaluation_id']!=fem.EXPECTED['civil_evaluation_id'] or
            field['source_report_id']!=fem.EXPECTED['report_id'] or
            handoff['candidate_id']!=fem.EXPECTED['candidate_id'] or
            handoff['civil_evaluation_id']!=fem.EXPECTED['civil_evaluation_id']):
        raise ValueError('Mixed FEM candidate')
    with tempfile.TemporaryDirectory(prefix='osr-gallery-verify-') as temporary:
        _materialize(folder,temporary)
        native=fem.read_vtu(Path(temporary)/'execution/field.vtu')
        result=cad.read(Path(temporary)/'result.json');fem.check_seal(result)
        if cad.digest(Path(temporary)/'execution/field.vtu') != result['full_field_sha256']: raise ValueError('Native field changed')
        mesh=cad.read(Path(temporary)/'inputs/mesh.json')
        if cad.digest(Path(temporary)/'inputs/mesh.json') != request['mesh_sha256']: raise ValueError('Requested mesh changed')
        validity=fem.validate_field(native,mesh,expected_probe=(fem.EXPECTED['probe_xyz_m'],fem.EXPECTED['probe_U_m']))
        import numpy as np
        if (not np.array_equal(native['displacement'],field['displacement_m']) or
                not np.array_equal(native['von_mises'],field['nodal_von_mises_Pa']) or
                not np.array_equal(native['points'],field['points_vtu_ascii_m']) or
                not np.array_equal([mesh['nodes'][str(n)] for n in field['node_labels']],field['points_m']) or
                native['node_label'].tolist() != field['node_labels']): raise ValueError('Compact field changed')
        if field['exterior_triangles_node_labels'] != [list(t) for t in fem.exterior_triangles(mesh)]: raise ValueError('Quadratic surface changed')
    return dict(current=True,evaluation_id=manifest['evaluation_id'],cards=len(manifest['cards']),
        native_nodes=validity['nodes'],native_cells=validity['cells'],physical_accepted=False)


def replot(folder, output, *, root=ROOT):
    verify(folder,root=root)
    with tempfile.TemporaryDirectory(prefix='osr-gallery-plot-') as temporary:
        _materialize(folder,temporary)
        return fem.plot(temporary,Path(output))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('publish');a.add_argument('selection',type=Path);a.add_argument('output',type=Path)
    a=s.add_parser('verify');a.add_argument('folder',type=Path,nargs='?',default=ROOT/DEST)
    a=s.add_parser('replot');a.add_argument('folder',type=Path);a.add_argument('output',type=Path)
    a=p.parse_args()
    value=(publish(cad.read(a.selection),a.output,root=a.root) if a.action=='publish' else
           replot(a.folder,a.output,root=a.root) if a.action=='replot' else verify(a.folder,root=a.root))
    print(json.dumps(value,sort_keys=True))


if __name__ == '__main__':main()
