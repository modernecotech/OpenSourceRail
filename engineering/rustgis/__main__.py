"""Export exact selected city outlines to native, portable RustGIS projects."""
import argparse
import json
import os
import subprocess
import zipfile
import time
import shutil
from pathlib import Path
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded
from . import adapter


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'export', 'open', 'verify', 'audit','export-study','import','reprice','verify-revision'))
    parser.add_argument('--city', help='Published city slug, for example baghdad')
    parser.add_argument('--all', action='store_true', help='Export every registered city')
    parser.add_argument('--output', type=Path, help='Cache root, or exact cache directory for verify')
    parser.add_argument('--preview', action='store_true', help='Native PNG preview for one city')
    parser.add_argument('--study', help='Verified local city-study job id for iterative native editing')
    parser.add_argument('--packet-id', help='Exact displayed city packet identity')
    parser.add_argument('--project',type=Path,help='Edited native .rgis file (embedded WGS84 data only)')
    parser.add_argument('--actor',help='Named planning author')
    parser.add_argument('--reason',help='Reason for the native geometry/service revision')
    parser.add_argument('--data-crs',help='Explicit native data CRS; supported EPSG:4326')
    args = parser.parse_args(argv)
    if args.action == 'install':
        from .install import install
        result = install()
    elif args.action=='verify-revision':
        from .revision import verify_import
        if args.output is None:parser.error('verify-revision requires --output IMPORT_DIRECTORY')
        result=verify_import(args.output,root=root)
    elif args.action=='export-study':
        if not args.study:parser.error('export-study requires --study JOB_ID')
        result=adapter.export_study(args.study,root=root,output=args.output,preview=args.preview)
    elif args.action in ('import','reprice'):
        from . import revision
        from engineering.outline.city_jobs import CityStudyService
        if not all((args.city,args.packet_id,args.project,args.actor,args.reason,args.data_crs)):
            parser.error('import/reprice requires --city --packet-id --project --actor --reason --data-crs')
        if not args.project.is_file() or args.project.is_symlink() or args.project.stat().st_size>revision.MAX_PROJECT:
            parser.error('bounded ordinary native project required')
        if args.output is not None and args.output.exists():parser.error('Choose a fresh --output evidence directory')
        service=CityStudyService(root)
        try:
            result=revision.import_project(args.project.read_bytes(),args.city,args.packet_id,actor=args.actor,
                reason=args.reason,data_crs=args.data_crs,root=root,study_id=args.study,service=service)
            job=result['job'];deadline=time.monotonic()+150
            while job and job['state']=='running' and time.monotonic()<deadline:
                time.sleep(.5);job=service.status(job['job_id'])
            if args.output is not None:
                shutil.copytree(Path(root)/'build/rustgis-imports'/result['import_id'],args.output)
            result=dict(import_id=result['import_id'],execution=result['execution'],job=job,
                retained_input=str(Path(root)/'build/rustgis-imports'/result['import_id']),**revision.FLAGS)
            if job and job['state']!='completed':raise ValueError('Retained native revision job did not complete: '+str(job))
        finally:service.close()
    elif args.action == 'verify':
        if args.output is None:parser.error('verify requires --output CACHE_DIRECTORY')
        result = adapter.verify(args.output, root=root)
    elif args.action == 'audit':
        result = dict(tool=adapter.lock_record(), executable=str(adapter.executable()),
                      cache=str(adapter.cache_root()), qgis_required=False)
    else:
        if bool(args.city) == args.all:parser.error('Choose --city SLUG or --all')
        if args.action == 'open' and args.all:parser.error('Open one city at a time')
        if args.all and args.preview:parser.error('Use --preview with one city to bound rendering')
        context = adapter.inputs(root)
        slugs = sorted(context[-1]) if args.all else [args.city]
        rows = []
        for slug in slugs:
            result = adapter.export(slug, root=root, context=context, output=args.output, preview=args.preview)
            rows.append(result);print(json.dumps(result, sort_keys=True), flush=True)
        result = dict(schema='osr-rustgis-campaign/1', completed_cities=len(rows), cities=rows,
            total_archive_bytes=sum(r['bytes'] for r in rows), all_native_reopened=True,
            railway_calculations_changed=False)
        output = args.output or adapter.cache_root();output.mkdir(parents=True, exist_ok=True)
        (output/('catalogue.json' if args.all else args.city+'-export.json')).write_bytes(encoded(result))
        if args.action == 'open':
            archive = Path(rows[0]['archive'])
            home = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))
            editable = home/'opensourcerail/gis'/args.city/rows[0]['manifest_id']
            if not editable.exists():
                editable.mkdir(parents=True)
                with zipfile.ZipFile(archive) as z:
                    for name in z.namelist():
                        adapter._local(editable, name)
                    z.extractall(editable)
            app = adapter.executable().with_name('rustgis')
            if adapter.digest(app) != adapter.lock_record()['executables_sha256']['rustgis']:
                raise ValueError('Pinned desktop RustGIS checksum differs')
            with (editable/'desktop.log').open('ab') as log:
                child = subprocess.Popen([str(app), str(editable/(args.city+'.rgis'))], cwd=editable,
                    stdout=log, stderr=log, start_new_session=True)
            result = dict(opened_project=str(editable/(args.city+'.rgis')), process_id=child.pid,
                original_archive_preserved=True, existing_edits_preserved=True)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':main()
