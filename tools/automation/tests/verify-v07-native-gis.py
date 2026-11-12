"""Bounded real native GIS cycle. Prepared by GIS worker; execute after root admission."""
import argparse
from copy import deepcopy
import hashlib,json,os,resource,shutil,subprocess,sys,time,zipfile
from pathlib import Path

def edit_station(project,base,stop,kind,point_at):
    """Change one actual native station, with source proxies kept consistent."""
    project=deepcopy(project)
    line=next(x for x in base['lines'] if x['id']=='line-1')
    station=next(x for x in line['stops'] if x['id']==stop)
    if kind=='station-move':
        chainage=station['chainage_m']+1.
        point=point_at(line['coordinates'],chainage)
        values={'chainage_m':chainage,'lon':point[0],'lat':point[1]}
    elif kind=='dwell':values={'dwell_s':station['dwell_s']+1.}
    else:raise ValueError('Known bounded native edit required')
    targets=[layer['dataset'] for m in project['maps'] for layer in m['layers'] if layer['name']=='stations']
    targets.extend(table for table in project.get('tables',[]) if table['name']=='stations')
    matches=[]
    for dataset in targets:
        fields=[f['name'] for f in dataset['fields']]
        for feature in dataset['features']:
            if feature['attrs'][fields.index('id')]=={'Text':stop}:
                for field,value in values.items():feature['attrs'][fields.index(field)]={'Float':float(value)}
                if kind=='station-move':feature['geometry']={'Point':{'x':point[0],'y':point[1]}}
                matches.append(feature)
    if len(matches)!=1:raise ValueError('Expected exact midpoint stop once in the native export')
    return project,dict(kind=kind,stop=stop,values=values)


def validate_edit(request,base,stop,kind,change):
    """Require unchanged alignment and all other station fields."""
    edits=request['edit_bundle']['edits']
    if len(edits)!=1:raise ValueError('Exactly one native station revision required')
    edit=edits[0];line=next(x for x in base['lines'] if x['id']=='line-1')
    if edit['kind']!='replace-line-geometry' or edit['coordinates']!=line['coordinates']:
        raise ValueError('Station-only edit must preserve alignment coordinates')
    expected=[{k:x[k] for k in ('id','chainage_m','dwell_s')} for x in line['stops']]
    actual=deepcopy(edit['stops'])
    selected=next(x for x in expected if x['id']==stop)
    if kind=='dwell':selected['dwell_s']+=1.
    elif kind=='station-move':
        moved=next(x for x in actual if x['id']==stop)
        if abs(moved['chainage_m']-change['values']['chainage_m'])>.02:
            raise ValueError('Native station move did not preserve requested chainage')
        selected['chainage_m']=moved['chainage_m']
    else:raise ValueError('Known bounded native edit required')
    if actual!=expected:raise ValueError('Only the chosen station field may change')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--study-store',type=Path,required=True)
    p.add_argument('--study',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stop',default='line-1-midpoint-s009339');args=p.parse_args(argv)
    root=args.root.resolve();out=args.output.absolute()
    assert not out.exists(),'Use a fresh output; preserve previous attempts'
    assert not out.resolve().is_relative_to(root),'External output required'
    out.parent.mkdir(parents=True,exist_ok=True)
    assert shutil.disk_usage(out.parent).free>=20*1024**3+512*1024**2,'20 GiB reserve plus 512 MiB run reservation required'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=root).strip(),'Clean source required'
    out.mkdir();os.environ['XDG_CACHE_HOME']=str(out/'cache')
    os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
    sys.path.insert(0,str(root))
    from engineering.rustgis import adapter,revision
    from engineering.outline.city_jobs import CityStudyService
    from engineering.station_rail.common import encoded,identity
    def allocated_payload(folder):
        return sum(f.stat().st_size for f in Path(folder).rglob('*') if f.is_file())
    prior_store_bytes=allocated_payload(args.study_store)
    start=time.monotonic();native_calls=[];original_native=adapter.native

    def budget():
        assert time.monotonic()-start<=600,'Native cycle total wall budget exhausted'
        assert shutil.disk_usage(out).free>=20*1024**3,'Host disk reserve exhausted'
        size=allocated_payload(out)+max(0,allocated_payload(args.study_store)-prior_store_bytes)
        assert size<=512*1024**2,'Native cycle output budget exceeded'

    def measured_native(arguments,directory,label):
        budget();assert len(native_calls)<8,'Native execution budget exhausted'
        native_calls.append(dict(directory=str(directory),label=label))
        value=original_native(arguments,directory,label);budget();return value

    adapter.native=measured_native
    service=None;steps=[]
    try:
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
        tool=adapter.lock_record();adapter.executable() # checksum admission, no install/download
        service=CityStudyService(root,store=args.study_store)
        current=args.study
        for index in range(3):
            budget()
            result=adapter.export_study(current,root=root,service=service)
            assert result.get('verified') is True
            with zipfile.ZipFile(result['archive']) as z:
                manifest=json.loads(z.read('manifest.json'));raw=z.read(manifest['project'])
            packet,_,originals,_,_,binding=adapter.study_input(current,root=root,service=service)
            if steps:assert binding['reference_candidate_ids']==steps[0]['binding']['reference_candidate_ids']
            step=dict(study=current,export=result,packet_id=packet['packet_id'],binding=binding)
            steps.append(step)
            if index==2:break
            base=json.loads(originals['sources/planning.json'])
            from engineering.development_baseline import planning
            kind='station-move' if index==0 else 'dwell'
            project,change=edit_station(json.loads(raw),base,args.stop,kind,planning._point_at)
            edited=encoded(project);(out/f'edit-{index+1}.rgis').write_bytes(edited)
            reason='Bounded native midpoint '+kind+' sensitivity'
            request,check=revision.build_request(edited,raw,base,binding,actor='v07-native-cycle',
                reason=reason,data_crs='EPSG:4326')
            validate_edit(request,base,args.stop,kind,change)
            assert not check['no_op'] and check['changed_lines']==['line-1']
            # The edit is programmatic .rgis data, not a GUI interaction. Prove
            # the actual native reader can reopen it before canonical import.
            native_check_dir=out/f'edited-reopen-{index+1}';native_check_dir.mkdir()
            station_file=native_check_dir/'stations.geojson'
            edited_native=adapter.native(['run','--no-plugins','--project',str(out/f'edit-{index+1}.rgis'),
                *adapter._cmd('share.exportLayer',layer='stations',path=str(station_file))],
                native_check_dir,'edited-reopen')
            decoded=revision.decode(edited,data_crs='EPSG:4326')['stations']
            expected=[dict(feature,properties={k:v for k,v in feature['properties'].items() if k!=adapter.INDEX})
                for feature in sorted(decoded['features'],key=lambda x:x['properties'][adapter.INDEX])]
            edited_roundtrip=adapter.check_roundtrip({'features':expected},json.loads(station_file.read_bytes()))
            record=revision.import_project(edited,'samawah',packet['packet_id'],actor='v07-native-cycle',
                reason=reason,data_crs='EPSG:4326',
                root=root,study_id=current,service=service,store=out/'imports')
            verified=revision.verify_import(out/'imports'/record['import_id'],root=root)
            assert verified['verified'] and record['canonical_request_id']==identity(request)
            job=record['job'];deadline=time.monotonic()+150
            while job['state']=='running' and time.monotonic()<deadline:
                time.sleep(.25);job=service.status(job['job_id']);budget()
            assert job['state']=='completed',job
            step.update(edit=change,edited_native_reopen=edited_native,edited_station_roundtrip=edited_roundtrip,import_record=record,import_verification=verified,completed_job=job)
            current=job['job_id']
        assert len(steps)==3 and len({x['study'] for x in steps})==3
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==source,'Source revision changed during native run'
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=root).strip(),'Source checkout changed during native run'
        report=dict(schema='osr-v07-native-gis-cycle/1',source_commit=source,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tool=tool,steps=steps,
            native_calls=native_calls,total_wall_s=time.monotonic()-start,
            maximum_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            actual_isolation='Existing adapter prlimit CPU/address-space and subprocess timeout; no aggregate filesystem quota or added OS sandbox',
            physical_accepted=False,result='pass-for-native-two-edit-Samawah-cycle')
        (out/'report.json').write_bytes(encoded(report));print(json.dumps({'result':report['result'],'native_calls':len(native_calls),'output':str(out)}))
    except BaseException as exc:
        (out/'failure.json').write_bytes(encoded(dict(error=type(exc).__name__+': '+str(exc),
            steps=steps,native_calls=native_calls,total_wall_s=time.monotonic()-start,physical_accepted=False)))
        raise
    finally:
        if service is not None:service.close()


if __name__=='__main__':main()
