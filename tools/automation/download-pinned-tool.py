#!/usr/bin/env python3
"""Fetch unchanged official tool bytes through bounded, verified endpoints.

GitHub's browser release route and asset API can fail independently. Both routes
below name the same immutable asset; exact size and SHA-256 must pass before a
download is published for installation. No credential is sent to either route.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time

PINS = {
    'freecad': dict(version='1.1.4', repository='FreeCAD/FreeCAD', tag='1.1.4',
        asset='FreeCAD_1.1.4-Linux-x86_64-py311.AppImage', asset_id=595913165,
        bytes=820812280, sha256='f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434'),
    'kani': dict(version='0.67.0', repository='model-checking/kani', tag='kani-0.67.0',
        asset='kani-0.67.0-x86_64-unknown-linux-gnu.tar.gz', asset_id=341228062,
        bytes=143387767, sha256='3b5f7afd3b51603ee720db7bc1bc4fe46b5a4f5d36daad9939c4b4c658b51ac0'),
}
MAX_ATTEMPTS = 3
ATTEMPT_WALL_S = 180
RETRY_DELAY_S = 5
MIN_FREE_BYTES = 1024**3


def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024**2): h.update(block)
    return h.hexdigest()


def write(path,value):
    with Path(path).open('x') as out: out.write(json.dumps(value,sort_keys=True,indent=2)+'\n')


def ordinary(path):
    path=Path(path).absolute()
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Tool paths must not traverse symlinks')
    return path


def valid(path,pin):
    return path.is_file() and path.stat().st_size==pin['bytes'] and digest(path)==pin['sha256']


def limits(maximum):
    resource.setrlimit(resource.RLIMIT_FSIZE,(maximum,maximum))
    resource.setrlimit(resource.RLIMIT_CPU,(60,61))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))


def download(tool,output,*,runner=subprocess.run,sleep=time.sleep):
    pin=PINS[tool];output=ordinary(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        if not valid(output,pin): raise ValueError('Existing cached tool bytes differ; refusing replacement')
        return dict(tool=tool,pin=pin,cached=True,archive=str(output),physical_accepted=False)
    attempts=ordinary(output.with_name(output.name+'.attempts'))
    attempts.mkdir(exist_ok=False)
    api=f"https://api.github.com/repos/{pin['repository']}/releases/assets/{pin['asset_id']}"
    browser=f"https://github.com/{pin['repository']}/releases/download/{pin['tag']}/{pin['asset']}"
    history=[];received=0
    for index,url in enumerate((api,browser,api),1):
        if received+pin['bytes']>2*pin['bytes']:
            raise RuntimeError('Download retry byte budget exhausted; attempts retained')
        if shutil.disk_usage(output.parent).free < pin['bytes']+MIN_FREE_BYTES:
            raise RuntimeError('Insufficient disk reserve for bounded tool download')
        partial=attempts/f'attempt-{index:02d}.part';log=attempts/f'attempt-{index:02d}.stderr.log'
        # --disable must be first: an inherited .curlrc must not add credentials,
        # alternate URLs, unbounded retries or TLS-verification bypasses.
        command=['curl','--disable','--proto','=https','--proto-redir','=https','--fail','--location',
            '--silent','--show-error','--retry','0','--connect-timeout','20',
            '--max-time',str(ATTEMPT_WALL_S),'--max-filesize',str(pin['bytes']),
            '--header','Accept: application/octet-stream','--header','Cache-Control: no-cache',
            '--output',str(partial),url]
        started=time.monotonic()
        with log.open('xb') as stderr:
            try:
                result=runner(command,stdout=subprocess.DEVNULL,stderr=stderr,
                    timeout=ATTEMPT_WALL_S+5,preexec_fn=lambda:limits(pin['bytes']))
                returncode=result.returncode;failure=None
            except subprocess.TimeoutExpired:
                returncode=None;failure='supervisor-timeout'
        ordinary(partial)
        size=partial.stat().st_size if partial.exists() else 0
        received+=size
        record=dict(attempt=index,url=url,returncode=returncode,failure=failure,
            wall_s=time.monotonic()-started,bytes=size,
            sha256=digest(partial) if partial.exists() else None,
            stderr_sha256=digest(log),maximum_attempt_wall_s=ATTEMPT_WALL_S)
        write(attempts/f'attempt-{index:02d}.json',record);history.append(record)
        if returncode==0:
            if not valid(partial,pin): raise ValueError('Pinned size/SHA256 mismatch; installation refused, bytes retained')
            if output.exists(): raise ValueError('Tool output appeared during download')
            partial.rename(output)
            receipt=dict(schema='osr-pinned-tool-download/1',tool=tool,pin=pin,cached=False,
                archive=str(output),attempts=history,received_bytes=received,
                maximum_received_bytes=2*pin['bytes'],maximum_attempts=MAX_ATTEMPTS,
                endpoint_order=['official asset API','official browser download','official asset API'],
                downloader_sha256=digest(__file__),credentials_sent=False,
                scope='Verified tool archive only; installation/native tests remain separate',physical_accepted=False)
            write(output.with_name(output.name+'.download.json'),receipt)
            return receipt
        if index<MAX_ATTEMPTS:sleep(RETRY_DELAY_S)
    raise RuntimeError('Pinned tool unavailable after three bounded attempts; all logs retained')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('tool',choices=sorted(PINS))
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    print(json.dumps(download(args.tool,args.output),sort_keys=True))
