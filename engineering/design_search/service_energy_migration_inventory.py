"""Pinned, non-promoting inventory for the terminal-recharge source migration.

This inspects source archives and Git manifest bytes; it does not inspect packet
payloads, run evaluators, modify current publications, or establish acceptance.
Direct-source inspection is not a complete transitive dependency analysis.
The exact three pinned Git commits must already exist locally; no fetch occurs.
The real-data integration test skips when archives or commits are absent, so a
passing synthetic-only test run is not evidence of a completed real audit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from . import retained_source_epoch as old
from . import retained_service_energy_epoch as extra
from . import retained_packet_materialize as git_support

OLD_COMMIT='dad8c4bedb2361d3e621e9def312273167279027'
EXTRA_COMMIT='5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76'
FIX_COMMIT='be03a8436a7b5b307840514e05146f98b3ee2574'
OLD_ARCHIVE='478479a93642c464cc2be318bbc5b45b9c5c3fec2e9cecb02318d53bd4fb568e'
EXTRA_ARCHIVE='d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
EXTRA_PINS='91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050'
SOURCE='engineering/station_rail/electrical.py'
OLD_SHA='04d42d88bc900e81c1db42fe84edf53900ffdfcffcb3a8dee3aea95ef2af1353'
FIX_SHA='f3bbec25f413ace7093300373ad4006bcd6d66d423e288becbd1da297e1b4092'
REFERENCE='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
SELECTION='8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc'
FLAGS=(*old.FLAGS,'configuration_adopted','selected_reference_changed',
       'numerical_reexecuted','current_evaluator_admission','physical_equivalence_proven')
LINKED_EXTRA={'periodic-thermal-research/manifest.json','installed-mass-support/manifest.json'}
LINKED_NOT_COVERED=('architecture-reach-closure','civil-shape-portfolio','implicit-geometry-study',
                    'moving-lim-method','v06-design-space')
FOLLOWUP='retained-physical-followup-source-epoch/manifest.json'


def _fixed(old_sha,fix_sha,old_archive,extra_archive,extra_pins):
    if (old_sha,fix_sha,old_archive,extra_archive,extra_pins)!=(OLD_SHA,FIX_SHA,OLD_ARCHIVE,EXTRA_ARCHIVE,EXTRA_PINS):
        raise ValueError('Exact externally pinned source, archive and pins identities required')


def _read(path,limit=16*1024*1024):
    return extra._file_data(path,limit,materialize=True)[1]


def _archive(folder,expected,kind,pins):
    folder=old._ordinary(folder,directory=True)
    if {p.name for p in folder.iterdir()}!={'manifest.json','sources.tar.gz'}:
        raise ValueError('Exact source archive inventory required')
    raw=_read(folder/'manifest.json');m=old._json(raw)
    keys=old.METADATA_KEYS if kind=='old' else extra.META_KEYS
    if (set(m)!=keys or m.get('archive_id')!=expected or
        old._id({k:v for k,v in m.items() if k!='archive_id'})!=expected or
        m.get('reference_candidate_id')!=REFERENCE or
        any(m.get(k) is not False for k in FLAGS)):
        raise ValueError('Archive identity, reference or non-promotion differs')
    if kind=='old':
        old._pins(pins)
        if m.get('pinned_original_manifest_ids')!=pins or set(m.get('packets',{}))!=set(old.CATALOG):
            raise ValueError('Old archive manifest pins differ')
    else:
        extra._pins(pins,EXTRA_PINS)
        if (m.get('pins_id')!=EXTRA_PINS or m.get('selection_id')!=SELECTION or
            m.get('git_commit')!=EXTRA_COMMIT or set(m.get('records',{}))!=set(extra.CATALOG)):
            raise ValueError('Extra archive manifest pins or selection differ')
    source=m.get('original_source_sha256',{})
    if source.get(SOURCE)!=OLD_SHA:raise ValueError('Archived electrical source differs')
    if kind=='extra' and m.get('source_epoch_id')!=old._id(source):raise ValueError('Source epoch identity differs')
    blob=_read(folder/'sources.tar.gz',old.MAX_ARCHIVE_BYTES)
    if hashlib.sha256(blob).hexdigest()!=m.get('source_archive_sha256'):
        raise ValueError('Source archive bytes differ')
    old._check_archive(blob,source)
    # Re-read the signed metadata after source verification; packet trees are not read.
    if _read(folder/'manifest.json')!=raw:raise ValueError('Archive metadata changed during verification')
    return m


def _git(repo,commit,path):
    old._path(path)
    if commit not in (OLD_COMMIT,EXTRA_COMMIT,FIX_COMMIT):raise ValueError('Unpinned Git commit')
    env=git_support._environment()
    allowed={'GIT_NO_REPLACE_OBJECTS','GIT_NO_LAZY_FETCH','GIT_TERMINAL_PROMPT',
             'GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL','GIT_ATTR_NOSYSTEM','GIT_OPTIONAL_LOCKS'}
    for name in tuple(env):
        if name.startswith('GIT_') and name not in allowed:env.pop(name)
    env['PATH']=os.defpath
    executable=shutil.which('git',path=os.defpath)
    if not executable:raise ValueError('Local Git executable required')
    command=git_support._git();command[0]=executable
    try:
        size_result=subprocess.run([*command,'cat-file','-s',commit+':'+path],cwd=repo,env=env,
            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
        if size_result.returncode!=0 or len(size_result.stdout)>32 or not size_result.stdout.strip().isdigit():
            raise ValueError('Pinned Git blob size unavailable: '+commit+':'+path)
        size=int(size_result.stdout.strip())
        if size>16*1024*1024:raise ValueError('Git blob exceeds bound')
        result=subprocess.run([*command,'cat-file','blob',commit+':'+path],cwd=repo,env=env,
            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
        if result.returncode!=0 or len(result.stdout)!=size:
            raise ValueError('Pinned Git blob unavailable or changed: '+commit+':'+path)
        return result.stdout
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Pinned Git read exceeded timeout') from exc


def _record(name,raw,schema,identity_key,source_key,expected_id,expected_sha,archive_id,linked):
    if hashlib.sha256(raw).hexdigest()!=expected_sha:raise ValueError('Original manifest bytes differ: '+name)
    m=old._json(raw)
    if (m.get('schema')!=schema or m.get(identity_key)!=expected_id or
        old._id({k:v for k,v in m.items() if k!=identity_key})!=expected_id):
        raise ValueError('Original manifest identity differs: '+name)
    source=m.get(source_key)
    if not isinstance(source,dict):raise ValueError('Original source map absent: '+name)
    electrical=source.get(SOURCE)
    if electrical is not None and electrical!=OLD_SHA:raise ValueError('Conflicting electrical source epoch: '+name)
    special=name==FOLLOWUP
    return dict(manifest=name,manifest_id=expected_id,manifest_sha256=expected_sha,archive_id=archive_id,
        linked_current_publication=linked,original_electrical_sha256=electrical,
        retained_disposition='historical-only',
        disposition=('historical-only' if special or (electrical is None and not linked) else
                     'current-dependency-review-required' if electrical is None else 'current-regeneration-required'),
        dependency=('historical-wrapper-current-context' if special else 'direct-source' if electrical else 'no-direct-source-review-required'),
        packet_payload_verified=False,current_replay_completed=False)


def inventory(repo,old_folder,old_pins,extra_folder,extra_pins,*,old_sha,fix_sha,old_archive,extra_archive,expected_extra_pins):
    _fixed(old_sha,fix_sha,old_archive,extra_archive,expected_extra_pins)
    repo=old._ordinary(repo,directory=True)
    implementation_paths=(Path(__file__),Path(old.__file__),Path(extra.__file__),Path(git_support.__file__))
    implementation_hashes=[hashlib.sha256(_read(path)).hexdigest() for path in implementation_paths]
    op=old._json(_read(old_pins));ep=old._json(_read(extra_pins))
    om=_archive(old_folder,old_archive,'old',op);em=_archive(extra_folder,extra_archive,'extra',ep)
    for commit,want in ((OLD_COMMIT,OLD_SHA),(EXTRA_COMMIT,OLD_SHA),(FIX_COMMIT,FIX_SHA)):
        if hashlib.sha256(_git(repo,commit,SOURCE)).hexdigest()!=want:
            raise ValueError('Pinned electrical Git source differs: '+commit)
    rows=[]
    for name,(schema,source_key,_,identity_key,_) in sorted(old.CATALOG.items()):
        entry=om['packets'][name];path='docs/design-engine/'+name+'/manifest.json'
        rows.append(_record(name+'/manifest.json',_git(repo,OLD_COMMIT,path),schema,identity_key,source_key,
            op[name],entry['manifest_sha256'],old_archive,True))
    for name,(schema,identity_key,source_key,_) in sorted(extra.CATALOG.items()):
        entry=em['records'][name]
        if entry['manifest_id']!=ep['manifest_ids'][name] or entry['manifest_sha256']!=ep['manifest_sha256'][name]:
            raise ValueError('Extra record pins differ: '+name)
        rows.append(_record(name,_git(repo,EXTRA_COMMIT,'docs/design-engine/'+name),schema,identity_key,source_key,
            entry['manifest_id'],entry['manifest_sha256'],extra_archive,name in LINKED_EXTRA))
    if implementation_hashes!=[hashlib.sha256(_read(path)).hexdigest() for path in implementation_paths]:
        raise ValueError('Inventory implementation changed during execution')
    value=dict(schema='osr-service-energy-migration-inventory/1',reference_candidate_id=REFERENCE,selection_id=SELECTION,
        historical_commits=[OLD_COMMIT,EXTRA_COMMIT],corrected_commit=FIX_COMMIT,old_electrical_sha256=OLD_SHA,
        corrected_electrical_sha256=FIX_SHA,source_archive_ids=[OLD_ARCHIVE,EXTRA_ARCHIVE],extra_pins_id=EXTRA_PINS,
        archive_source_bytes_verified=True,git_manifest_bytes_verified=True,packet_payloads_verified=False,
        archive_materialization_verified=False,current_replay_completed=False,
        linked_publications_not_covered=[dict(publication=name,transitive_impact='unknown',direct_source_status='not-checked') for name in LINKED_NOT_COVERED],
        scope='Direct-source inventory is not full transitive dependency closure; no evaluator admission or physical acceptance',
        implementation_sha256=dict(zip((p.name for p in implementation_paths),implementation_hashes)),
        records=rows,**{k:False for k in FLAGS})
    value['inventory_id']=old._id(value)
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('repo','old-archive-directory','old-pins','extra-archive-directory','extra-pins',
                 'old-source-sha','corrected-source-sha','expected-old-archive-id','expected-extra-archive-id','expected-extra-pins-id'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args();result=inventory(Path(a.repo),Path(a.old_archive_directory),Path(a.old_pins),
        Path(a.extra_archive_directory),Path(a.extra_pins),old_sha=a.old_source_sha,fix_sha=a.corrected_source_sha,
        old_archive=a.expected_old_archive_id,extra_archive=a.expected_extra_archive_id,expected_extra_pins=a.expected_extra_pins_id)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
