#!/usr/bin/env python3
"""Restore the native SQL backup into a new network-isolated disposable database.

Public output is counts/hashes only. No source database/container is a restore
destination; the temporary container and local SQL copy are always removed.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
APP=ROOT/'deployment/erpnext/apps/osr_erpnext'
sys.path.insert(0,str(APP))
from osr_erpnext.delivery_admin import snapshot_queries

def run(args,**kwargs):return subprocess.run(args,check=True,capture_output=True,**kwargs)

def verify(backup_path,expected,*,image='mariadb:10.6.25'):
    raw=gzip.decompress(Path(backup_path).read_bytes())
    name='osr-baghdad-restore-'+uuid.uuid4().hex[:12]
    result=dict(schema='baghdad-native-sql-restore/1',backup_sha256=hashlib.sha256(Path(backup_path).read_bytes()).hexdigest(),
        source_database_modified=False,network='none',passed=False,removed=False,operational_release=False)
    try:
        run(['docker','image','inspect',image]) # Never fetch or run an unknown image implicitly.
        run(['docker','run','--detach','--name',name,'--network','none','--memory','1g',
            '--tmpfs','/var/lib/mysql:rw,size=768m','--tmpfs','/tmp:rw,size=128m',
            '--env','MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1',image])
        for _ in range(90):
            ping=subprocess.run(['docker','exec',name,'healthcheck.sh','--connect','--innodb_initialized'],capture_output=True)
            if ping.returncode==0:break
            time.sleep(.5)
        else:raise RuntimeError('Disposable restore database did not initialise')
        run(['docker','exec',name,'mariadb','--user=root','--execute','CREATE DATABASE restored CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'])
        run(['docker','exec','-i',name,'mariadb','--user=root','restored'],input=raw)
        records={}
        for key,query in snapshot_queries().items():
            output=run(['docker','exec',name,'mariadb','--user=root','--batch','--raw','--skip-column-names','restored','--execute',query]).stdout
            records[key]=dict(count=len(output.splitlines()),sha256=hashlib.sha256(output).hexdigest())
        result.update(records=records,passed=records==expected['records'],scope='SQL data/schema/roles/file inventory hashes; not full file decryption or production RTO/RPO')
        if not result['passed']:raise ValueError('Isolated restored native fingerprints differ')
    finally:
        cleanup=subprocess.run(['docker','rm','--force','--volumes',name],capture_output=True)
        result['removed']=cleanup.returncode==0
    return result

def main():
    os.umask(0o077);parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup',type=Path,required=True);parser.add_argument('--expected',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    result=verify(args.backup,json.loads(args.expected.read_text()))
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(result,indent=2)+'\n');args.receipt.chmod(0o600)
    if not result['removed']:raise RuntimeError('Disposable restore cleanup failed')
    print('Native SQL restore: matched six data/permission/schema fingerprints; isolated temporary database removed')

if __name__=='__main__':main()
