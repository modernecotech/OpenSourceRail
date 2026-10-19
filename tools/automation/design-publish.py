#!/usr/bin/env python3
"""Build, verify and periodically publish bounded native design-review packages."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.design_delivery import pipeline,automation
from engineering.continuous_design import service


def unit_text(workspace,qualification):
    def quote(value):return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    command=' '.join(map(quote,[sys.executable,Path(__file__).resolve(),'cycle','--workspace',Path(workspace).resolve(),'--repository',ROOT,'--qualification',Path(qualification).resolve(),'--push']))
    maintenance=' '.join(map(quote,[sys.executable,Path(__file__).resolve(),'maintain','--workspace',Path(workspace).resolve()]))
    return {'osr-design-publication.service':'[Unit]\nDescription=OpenSourceRail qualified design evidence publication\n\n[Service]\nType=oneshot\nExecStart='+command+'\nNice=15\nCPUQuota=150%\nMemoryMax=2G\nTasksMax=256\nTimeoutStartSec=30min\nUMask=0077\n',
        'osr-design-publication.timer':'[Unit]\nDescription=OpenSourceRail daily design evidence publication\n\n[Timer]\nOnCalendar=daily\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n',
        'osr-design-coverage.service':'[Unit]\nDescription=OpenSourceRail task family coverage\n\n[Service]\nType=oneshot\nExecStart='+maintenance+'\nTimeoutStartSec=2min\nMemoryMax=256M\n',
        'osr-design-coverage.timer':'[Unit]\nDescription=OpenSourceRail task family coverage cadence\n\n[Timer]\nOnBootSec=2min\nOnUnitActiveSec=15min\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('qualify','build','verify','cycle','install','maintain'))
    p.add_argument('--workspace',type=Path,default=service.DEFAULT);p.add_argument('--output',type=Path)
    p.add_argument('--package',type=Path);p.add_argument('--qualification',type=Path);p.add_argument('--repository',type=Path,default=ROOT)
    p.add_argument('--push',action='store_true');p.add_argument('--force',action='store_true');p.add_argument('--media',action='store_true');a=p.parse_args()
    if a.action=='qualify':
        if a.output is None:p.error('--output required')
        r=automation.qualify(a.output);print(json.dumps({k:r[k] for k in ('passed','log_sha256','source_commit')}));return
    if a.action=='maintain':r=automation.maintain(a.workspace)
    elif a.action=='verify':
        if a.package is None:p.error('--package required')
        r=pipeline.verify(a.package,media=a.media)
    else:
        if a.qualification is None:p.error('--qualification required')
        if a.action=='build':
            if a.output is None:p.error('--output required')
            r=pipeline.build(a.workspace,a.output,a.qualification);r={k:r[k] for k in ('schema','baseline','signature','design_complete')}
        elif a.action=='cycle':r=automation.cycle(a.workspace,a.repository,a.qualification,push=a.push,force=a.force)
        else:
            q=pipeline.core.read(a.qualification,maximum=20_000_000)
            if not q['passed'] or q['sources']!=pipeline.sources():raise ValueError('exact-source qualification required before scheduling')
            folder=Path.home()/'.config/systemd/user';folder.mkdir(parents=True,exist_ok=True)
            for name,body in unit_text(a.workspace,a.qualification).items():
                path=folder/name
                if path.exists() and 'Description=OpenSourceRail' not in path.read_text():raise ValueError('service unit belongs to another owner')
                path.write_text(body)
            subprocess.run(['systemctl','--user','daemon-reload'],check=True)
            subprocess.run(['systemctl','--user','enable','--now','osr-design-publication.timer','osr-design-coverage.timer'],check=True)
            r=dict(timer='osr-design-publication.timer',cadence='daily with confirmed-revision deduplication',push=True)
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
