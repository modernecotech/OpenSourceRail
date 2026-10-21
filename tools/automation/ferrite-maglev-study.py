#!/usr/bin/env python3
"""OpenSourceRail v0.5 primary infrastructure study; physical release stays gated."""
import argparse
import json
from pathlib import Path
import sys
import subprocess

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engineering.ferrite_maglev import model,delivery


def units(output):
    def arg(value):
        return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    entry=model.ROOT/'tools/automation/ferrite-maglev-study.py'
    return {
        'osr-primary-infrastructure.service':
            '[Unit]\nDescription=OpenSourceRail v0.5 primary infrastructure study refresh\n'
            '[Service]\nType=oneshot\nWorkingDirectory='+str(model.ROOT).replace('%','%%')+'\n'
            'ExecStart='+arg(sys.executable)+' '+arg(entry)+' cycle --output '+arg(output)+'\n'
            'TimeoutStartSec=3600\nUMask=0077\n',
        'osr-primary-infrastructure.timer':
            '[Unit]\nDescription=OpenSourceRail v0.5 source-change study refresh\n'
            '[Timer]\nOnBootSec=2min\nOnUnitActiveSec=15min\nPersistent=true\n'
            'Unit=osr-primary-infrastructure.service\n[Install]\nWantedBy=timers.target\n'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',nargs='?',default='run',choices=('run','verify','check','status','readiness','release-check','cycle','build','install','native','coupled','catalogue','evacuation-native','system','iterate','station','structure','protocol'))
    parser.add_argument('--output',type=Path,default=delivery.OUTPUT)
    args=parser.parse_args()
    if args.action=='install':
        model.load()
        output=Path.home()/'.local/state/opensourcerail/ferrite-maglev/latest'
        folder=Path.home()/'.config/systemd/user';folder.mkdir(parents=True,exist_ok=True)
        for name,text in units(output).items():
            path=folder/name
            if path.exists() and 'Description=OpenSourceRail v0.5' not in path.read_text():
                raise ValueError('unit is owned by another application')
            path.write_text(text)
        subprocess.run(['systemctl','--user','daemon-reload'],check=True)
        subprocess.run(['systemctl','--user','enable','--now','osr-primary-infrastructure.timer'],check=True)
        subprocess.run(['systemctl','--user','start','osr-primary-infrastructure.service'],check=True)
        result=dict(timer='osr-primary-infrastructure.timer',report=str(output/'index.html'),
                    mode='restartable dependency build on source change; missing evaluators and physical acceptance remain open')
    elif args.action in {'cycle','build'}:
        from engineering.ferrite_maglev import workflow
        result=workflow.run(args.output)
    elif args.action=='catalogue':
        from engineering.ferrite_maglev import cities
        result=cities.generate_all()
        result=cities.verify_index()
    elif args.action=='native':
        from engineering.ferrite_maglev import geometry,media
        output=model.ROOT/'docs/design-engine/ferrite-maglev/native'
        geometry.publish_native(output)
        for folder in ('interface','civil-bay'):media.native_views(output/folder)
        result=geometry.seal_native(output)
    elif args.action=='evacuation-native':
        from engineering.ferrite_maglev import evacuation
        result=evacuation.publish_native(model.ROOT/'docs/design-engine/ferrite-maglev/beam-only')
    elif args.action=='system':
        from engineering.ferrite_maglev import system_development
        result=system_development.publish()
    elif args.action in {'station','structure','protocol'}:
        from engineering.ferrite_maglev import station,station_structure,station_protocol
        result={'station':station,'structure':station_structure,'protocol':station_protocol}[args.action].publish()
    elif args.action=='iterate':
        from engineering.ferrite_maglev import iteration
        result=iteration.publish()
    elif args.action=='coupled':
        from engineering.ferrite_maglev import coupled
        result=coupled.publish(model.ROOT/'docs/design-engine/ferrite-maglev/coupled')
    elif args.action=='readiness':
        delivery.verify(args.output)
        retained=json.loads((args.output/'result.json').read_text())
        result=dict(family=retained['family'],source_current=True,scope='Primary maglev digital studies; no engineering/physical release',
            accepted_physical_releases=0,open_requirements=len(retained['applicable_requirements']['requirements']),
            core_open_requirements=len(retained['requirements']),
            evacuation_open_requirements=7,specification_open_requirements=len(retained['source_specification']['requirements']),gates=retained['gates'],
            transition_inventory=retained['transition_inventory'],**model.FLAGS)
    elif args.action=='status':
        from engineering.ferrite_maglev import transition,requirements,cities
        _,c,_=model.load()
        register=transition.build()
        result=dict(version=model.RELEASE_VERSION,family=c['metadata']['family'],primary_development=True,
                    gates='G0–G5 open',city_packages=len(list((cities.ROOT/'cities/catalogue').glob('*/*/*/city.json'))),
                    propulsion_architecture=c['architecture']['primary_costed_propulsion'],
                    city_method='Current station-powered maglev configurations and quantity/process cost inputs; geography and passenger targets remain provisional.',
                    system_inventory=register['inventory_counts'],
                    open_requirements=len(requirements.register()['requirements']),
                    accepted_engineering_items=register['accepted_item_count'],**model.FLAGS)
    elif args.action=='release-check':
        model.load()
        print(json.dumps(dict(release_allowed=False,reason='No authenticated magnetic/vehicle/civil/hardware acceptance adapter',
                              required_gates=['G'+str(i) for i in range(6)]),indent=2));return 3
    else:
        manifest=delivery.verify(args.output) if args.action=='verify' else delivery.publish(args.output,check=args.action=='check')
        result=dict(version=manifest['version'],family=manifest['family'],action=args.action,
                    output=str(args.output),files=len(manifest['files_sha256']),**model.FLAGS)
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,FileNotFoundError,subprocess.CalledProcessError) as exc:
        print('Primary infrastructure study held: '+str(exc),file=sys.stderr);sys.exit(2)
