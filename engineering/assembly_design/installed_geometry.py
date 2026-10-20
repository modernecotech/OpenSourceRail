"""Native solid interference study for the controlled cassette/body instances.

Direct numeric placement is explicitly provisional: the equipment/body datum,
passenger headroom, access, full services and maintenance envelopes are not
accepted. A zero common volume is never admission to system simulation.
"""
from pathlib import Path
import math
import shutil
import subprocess

from engineering.twin_workflow import core

SCHEMA='osr-installed-native-interference/1'
VOLUME_TOLERANCE_M3=1e-12
MAX_BOOLEAN_TESTS=20_000
HOLDS=[
    'Equipment and carbody frame datums are not reconciled; controlled local positions are used without an invented translation.',
    'Passenger headroom, maintenance/removal access and occupied-space compatibility are not verified.',
    'Mounts, trunk services, refrigeration geometry, loads, motion and flexible connections are not verified.',
]


def _candidate(candidate,cad):
    cad=Path(cad)
    ids=[p['id'] for p in candidate['contract']['parts']]
    if not ids or len(ids)!=len(set(ids)):raise ValueError('unique native part identities required')
    proof_path=cad.parent/'native-cad.json'
    proof=core.read(proof_path,maximum=10_000_000)
    digest=core.sha(cad)
    if proof.get('input_sha256')!=core.digest(candidate['contract']) or proof.get('files_sha256',{}).get(cad.name)!=digest:
        raise ValueError('native proof differs from exact contract or FCStd bytes')
    if not all(proof.get(k) is True for k in ('physical_ids_preserved','native_reopened','step_volume_reconciled')):
        raise ValueError('successful native correspondence proof required')
    if proof.get('manufacturing_unit_ids_preserved') is False:
        raise ValueError('native manufacturing identities differ')
    if any(candidate.get(k) is not False for k in core.FLAGS):raise ValueError('provisional candidate release flags required')
    return dict(candidate_revision=candidate['revision'],contract_sha256=core.digest(candidate['contract']),
        cad_sha256=digest,proof_sha256=core.sha(proof_path),part_ids=ids)


def _input(carbody_candidate,carbody_cad,cassette_candidate,cassette_cad,equipment):
    from osr_mech.family_definition import family_definition
    from . import installed_equipment
    layout=installed_equipment.layout()
    family=family_definition('metro-6car')
    payload={k:v for k,v in equipment.items() if k!='revision'}
    if (equipment.get('revision')!=core.digest(payload) or equipment.get('layout_sha256')!=core.sha(installed_equipment.DATA)
        or equipment.get('candidate_revision')!=cassette_candidate['revision']
        or equipment.get('car_count')!=family['car_count'] or equipment.get('counts')!=installed_equipment.counts()
        or equipment.get('architecture')!=layout['architecture']):
        raise ValueError('controlled exact equipment revision/layout required')
    parts=cassette_candidate['metadata']['cassette_installed_part_ids']
    all_ids={p['id'] for p in cassette_candidate['contract']['parts']}
    if not parts or len(parts)!=len(set(parts)) or not set(parts)<=all_ids or equipment.get('represented_part_ids')!=parts:
        raise ValueError('exact owned installed cassette part identities required')
    for key in core.FLAGS:
        if equipment.get(key) is not False:raise ValueError('equipment cannot assert release')
    expected_instances=[];expected_allocations=[];placements=[]
    rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
    for i,point in enumerate(layout['cassette_local_positions_m'],1):
        ids=[];body_ids=[]
        for car in family['cars']:
            identity=car['id']+'/service-cassette-'+str(i).zfill(2)
            ids.append(identity);body_ids.append(car['id'])
            allocation=dict(id=identity,body_id=car['id'],candidate_revision=cassette_candidate['revision'],
                translation_m=[point[0]+car['centre_x_m'],point[1],point[2]],rotation=rotation)
            expected_allocations.append(allocation)
            expected_instances.append(dict(**allocation,local_position_m=point))
        placements.append(dict(id='local-position-'+str(i).zfill(2),local_position_m=point,
            instance_ids=ids,body_ids=body_ids))
    actual=equipment.get('instances',[])
    if len(actual)!=len(expected_instances) or len({row.get('id') for row in actual})!=len(actual):
        raise ValueError('equipment instance identities/count differ')
    by_id={row['id']:row for row in actual}
    for row in expected_instances:
        if row['id'] not in by_id or any(by_id[row['id']].get(k)!=v for k,v in row.items()):
            raise ValueError('equipment placement differs from controlled local layout')
    allocations=equipment.get('allocations',[])
    if len(allocations)!=len(expected_allocations) or sorted(allocations,key=lambda r:r['id'])!=sorted(expected_allocations,key=lambda r:r['id']):
        raise ValueError('equipment allocations differ from controlled instances')
    return dict(schema=SCHEMA,source_sha256=core.sha(Path(__file__)),
        layout_sha256=core.sha(installed_equipment.DATA),family=family,
        carbody=_candidate(carbody_candidate,carbody_cad),cassette=_candidate(cassette_candidate,cassette_cad),
        equipment_revision=equipment['revision'],cassette_installed_part_ids=parts,
        excluded_cassette_part_ids=sorted(all_ids-set(parts)),placements=placements,
        volume_tolerance_m3=VOLUME_TOLERANCE_M3,max_boolean_tests=MAX_BOOLEAN_TESTS,
        placement_scope='The same reference carbody is compared with each controlled per-car cassette local placement; identical local geometry is solved once and mapped to every exact train instance. No z offset or frame reconciliation is assumed.',
        frame_alignment_verified=False,**core.FLAGS)


def _native(input_path,carbody_cad,cassette_cad,output):
    """Executed only inside FreeCAD; never saves or alters either source model."""
    import FreeCAD as App
    import Part
    data=core.read(input_path,maximum=20_000_000);output=Path(output)
    documents=[];tests=0
    class InvalidInput(ValueError):pass
    def load(path,key):
        path=Path(path)
        if core.sha(path)!=data[key]['cad_sha256'] or core.sha(path.parent/'native-cad.json')!=data[key]['proof_sha256']:
            raise InvalidInput('native input bytes changed before execution')
        doc=App.openDocument(str(path));documents.append(doc)
        rows=[obj for obj in doc.Objects if hasattr(obj,'PhysicalPartId')]
        if len(rows)!=len(data[key]['part_ids']) or {obj.PhysicalPartId for obj in rows}!=set(data[key]['part_ids']):
            raise InvalidInput('native physical identities differ')
        for obj in rows:
            if not hasattr(obj,'Shape') or obj.Shape.isNull() or not obj.Shape.isValid() or not obj.Shape.Solids:
                raise InvalidInput('invalid or nonsolid native physical shape')
        return {obj.PhysicalPartId:obj.Shape.copy() for obj in rows}
    def common(left,right):
        nonlocal tests
        tests+=1
        if tests>data['max_boolean_tests']:raise RuntimeError('bounded native boolean budget exceeded')
        shape=left.common(right)
        if not shape.isNull() and not shape.isValid():raise RuntimeError('native common result invalid')
        volume=float(shape.Volume)/1e9
        if not math.isfinite(volume) or volume<0:raise RuntimeError('invalid native intersection volume')
        return volume
    try:
        body=load(carbody_cad,'carbody');cassette=load(cassette_cad,'cassette')
        rows=[];violations=[]
        for placement in data['placements']:
            moved={}
            for identity in data['cassette_installed_part_ids']:
                shape=cassette[identity].copy()
                shape.translate(App.Vector(*(v*1000 for v in placement['local_position_m'])))
                moved[identity]=shape
            compound=Part.makeCompound(list(moved.values()))
            hits=[];compound_volume=0.
            for body_id,shape in body.items():
                if not shape.BoundBox.intersect(compound.BoundBox):continue
                volume=common(shape,compound)
                compound_volume+=volume
                if volume<=data['volume_tolerance_m3']:continue
                pairs=[]
                for cassette_id,part in moved.items():
                    if not shape.BoundBox.intersect(part.BoundBox):continue
                    pair_volume=common(shape,part)
                    if pair_volume>data['volume_tolerance_m3']:
                        pairs.append(dict(carbody_part_id=body_id,cassette_part_id=cassette_id,
                            intersection_volume_m3=pair_volume))
                # A positive compound result itself is a rejection even if its
                # tiny constituent intersections each fall below the threshold.
                hit=dict(carbody_part_id=body_id,intersection_volume_m3=volume,part_pairs=pairs)
                hits.append(hit)
                violations.append(dict(placement_id=placement['id'],instance_ids=placement['instance_ids'],**hit))
            rows.append(dict(**placement,intersection_volume_m3=compound_volume,interferences=hits))
        for path,key in ((carbody_cad,'carbody'),(cassette_cad,'cassette')):
            if core.sha(path)!=data[key]['cad_sha256'] or core.sha(Path(path).parent/'native-cad.json')!=data[key]['proof_sha256']:
                raise InvalidInput('native source bytes changed during execution')
        report=dict(schema=SCHEMA,input_sha256=core.sha(input_path),geometry_state='failed' if violations else 'passed',
            native_boolean_tests=tests,placements=rows,interferences=violations,
            interference_volume_m3=sum(row['intersection_volume_m3']*len(row['instance_ids']) for row in rows),
            volume_scope='Sum of per-carbody-part common volumes mapped to every cassette instance; intersections between overlapping body materials may be counted more than once. Not a material-removal or net occupied-volume calculation.',
            source_models_unchanged=True)
    except Exception as exc:
        report=dict(schema=SCHEMA,input_sha256=core.sha(input_path),geometry_state='failed' if isinstance(exc,InvalidInput) else 'hold',
            native_boolean_tests=tests,placements=[],interferences=[],interference_volume_m3=None,
            source_models_unchanged=False,error=str(exc))
    finally:
        for doc in documents:App.closeDocument(doc.Name)
    core.write(output/'native-interference.json',report)


def _result(data,raw,files,error=None):
    geometry=raw['geometry_state'] if raw else 'hold'
    report=dict(schema=SCHEMA,input_revision=core.digest(data),
        carbody_revision=data['carbody']['candidate_revision'],cassette_revision=data['cassette']['candidate_revision'],
        equipment_revision=data['equipment_revision'],geometry_state=geometry,
        state='failed' if geometry=='failed' else 'hold',admitted_for_system_simulation=False,
        frame_alignment_verified=False,holds=HOLDS,
        checked_instance_ids=[i for p in data['placements'] for i in p['instance_ids']],
        per_car_positions=len(data['placements']),train_instance_count=sum(len(p['instance_ids']) for p in data['placements']),
        installed_part_ids=data['cassette_installed_part_ids'],excluded_part_ids=data['excluded_cassette_part_ids'],
        interferences=raw.get('interferences',[]) if raw else [],
        interference_volume_m3=raw.get('interference_volume_m3') if raw else None,
        native_boolean_tests=raw.get('native_boolean_tests') if raw else None,
        native_error=raw.get('error') if raw else None,
        files_sha256=files,scope=data['placement_scope'],**core.FLAGS)
    if error:report['execution_error']=error
    report['revision']=core.digest(report)
    return report


def build(carbody_candidate,carbody_cad,cassette_candidate,cassette_cad,equipment,output):
    """Compare retained exact native solids; tool errors produce explicit holds."""
    data=_input(carbody_candidate,carbody_cad,cassette_candidate,cassette_cad,equipment)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    core.write(output/'input.json',data)
    script=output/'generate.py'
    script.write_text('import runpy,sys\nsys.path[:0]='+repr([str(core.ROOT)])+
        '\nrunpy.run_path('+repr(str(Path(__file__).resolve()))+')["_native"]('+
        ','.join(repr(str(Path(path).resolve())) for path in (output/'input.json',carbody_cad,cassette_cad,output))+')\n')
    error=None;raw=None
    try:
        binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
        command=[binary] if binary else ['flatpak','run','--filesystem='+str(core.ROOT),
            '--filesystem='+str(Path(carbody_cad).resolve().parent),'--filesystem='+str(Path(cassette_cad).resolve().parent),
            '--filesystem='+str(output.resolve()),'--command=FreeCADCmd','org.freecad.FreeCAD']
        with (output/'freecad.log').open('w') as stream:
            subprocess.run([*command,str(script)],stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=240)
        raw=core.read(output/'native-interference.json',maximum=20_000_000)
        if raw.get('input_sha256')!=core.sha(output/'input.json') or raw.get('geometry_state') not in {'passed','failed','hold'}:
            raise ValueError('native interference output identity/state differs')
        _validate_raw(data,raw)
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        error=str(exc);raw=None
    # FreeCAD may compile the owned launcher beside its retained source. This
    # reproducible interpreter cache is not raw solver evidence or a receipt
    # input; keep it out of portable publications.
    cache=output/'__pycache__'
    if cache.is_dir() and not cache.is_symlink():shutil.rmtree(cache)
    files={name:core.sha(output/name) for name in ('input.json','generate.py','freecad.log','native-interference.json') if (output/name).is_file()}
    report=_result(data,raw,files,error)
    core.write(output/'result.json',report)
    return report


def verify(carbody_candidate,carbody_cad,cassette_candidate,cassette_cad,equipment,output):
    """Check exact inputs, retained native output, hashes and conservative state."""
    output=Path(output)
    data=_input(carbody_candidate,carbody_cad,cassette_candidate,cassette_cad,equipment)
    if core.read(output/'input.json',maximum=20_000_000)!=data:raise ValueError('installed native input differs')
    report=core.read(output/'result.json',maximum=20_000_000)
    allowed={'input.json','generate.py','freecad.log','native-interference.json'}
    files=report.get('files_sha256',{})
    if not {'input.json','generate.py'}<=set(files) or not set(files)<=allowed:
        raise ValueError('installed native file membership differs')
    for name,digest in files.items():
        if not (output/name).is_file() or core.sha(output/name)!=digest:raise ValueError('installed native file hash differs')
    raw=core.read(output/'native-interference.json',maximum=20_000_000) if 'native-interference.json' in files else None
    if raw is not None and raw.get('input_sha256')!=core.sha(output/'input.json'):
        raise ValueError('native interference output belongs to another input')
    if raw is not None and not report.get('execution_error'):
        _validate_raw(data,raw)
    if report.get('execution_error'):raw=None
    expected=_result(data,raw,files,report.get('execution_error'))
    if report!=expected:raise ValueError('installed native result differs')
    return True


def _validate_raw(data,raw):
    state=raw.get('geometry_state')
    if state not in {'passed','failed','hold'}:raise ValueError('native geometry state invalid')
    if 'error' in raw:
        if state=='passed' or raw.get('interference_volume_m3') is not None:raise ValueError('native error cannot pass')
        return
    if raw.get('source_models_unchanged') is not True:raise ValueError('native source stability not verified')
    rows=raw.get('placements',[])
    if len(rows)!=len(data['placements']):raise ValueError('native placement count differs')
    violations=[];total=0.
    for expected,row in zip(data['placements'],rows):
        if any(row.get(k)!=v for k,v in expected.items()):raise ValueError('native placement identity differs')
        volume=row.get('intersection_volume_m3')
        if type(volume) not in (int,float) or not math.isfinite(volume) or volume<0:raise ValueError('native volume invalid')
        total+=volume*len(row['instance_ids'])
        for hit in row.get('interferences',[]):
            if hit.get('carbody_part_id') not in data['carbody']['part_ids']:raise ValueError('unknown carbody interference identity')
            if hit.get('intersection_volume_m3',0)<=data['volume_tolerance_m3']:raise ValueError('interference below declared tolerance')
            for pair in hit.get('part_pairs',[]):
                if pair.get('carbody_part_id')!=hit['carbody_part_id'] or pair.get('cassette_part_id') not in data['cassette_installed_part_ids']:
                    raise ValueError('unknown installed-part interference identity')
                v=pair.get('intersection_volume_m3')
                if type(v) not in (int,float) or not math.isfinite(v) or v<=data['volume_tolerance_m3']:
                    raise ValueError('native part intersection volume invalid')
            violations.append(dict(placement_id=row['id'],instance_ids=row['instance_ids'],**hit))
    if raw.get('interferences')!=violations or raw.get('interference_volume_m3')!=total:
        raise ValueError('native interference totals differ')
    if state!=('failed' if violations else 'passed'):raise ValueError('native failed interference promoted')
    tests=raw.get('native_boolean_tests')
    if type(tests) is not int or tests<0 or tests>MAX_BOOLEAN_TESTS:raise ValueError('native boolean count invalid')
