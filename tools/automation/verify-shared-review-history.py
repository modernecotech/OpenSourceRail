#!/usr/bin/env python3
"""Verify immutable published research evidence against its producing git commit.

This checks publication/code provenance, not current solver qualification or the
untracked bulk campaign outputs. A changed solver cannot silently reaccept it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def sha(data):return hashlib.sha256(data).hexdigest()


def git_file(commit,relative):
    p=Path(relative)
    if p.is_absolute() or '..' in p.parts:raise ValueError('history path must be repository-relative')
    return subprocess.check_output(['git','show',f'{commit}:{p.as_posix()}'],cwd=ROOT)


def verify(path,revision):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('published review must be inside the repository')
    commit=subprocess.check_output(['git','rev-parse','--verify','--end-of-options',revision+'^{commit}'],cwd=ROOT,text=True).strip()
    relative=path.relative_to(ROOT).as_posix();raw=path.read_bytes()
    if raw!=git_file(commit,relative):raise ValueError('published review changed from its producing commit')
    review=json.loads(raw);sources=review['sources_sha256']
    for name,digest in sources.items():
        if sha(git_file(commit,name))!=digest:raise ValueError('recorded source does not match the producing commit: '+name)
    publication=review.get('publication_sources_sha256',{})
    if 'publication_source_sha256' in review:
        publication={'tools/automation/export-shared-campaign-review.py':review['publication_source_sha256']}
    for name,digest in publication.items():
        if sha(git_file(commit,name))!=digest:raise ValueError('review publisher does not match its producing commit')
    if review.get('physical_validation') is not False or review.get('engineering_released') is not False:
        raise ValueError('this verifier handles unqualified research publications only')
    current=all((ROOT/name).is_file() and sha((ROOT/name).read_bytes())==digest for name,digest in sources.items())
    return dict(schema='osr-published-review-history/1',review_path=relative,review_sha256=sha(raw),
        producing_commit=commit,published_sources_verified=True,current_implementation_matches=current,
        source_count=len(sources),bulk_campaign_outputs_verified=False,solver_environment_reverified=False,
        current_solver_qualified=False,physical_validation=False,engineering_released=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('review',type=Path);p.add_argument('--revision',required=True)
    a=p.parse_args();print(json.dumps(verify(a.review,a.revision),indent=2,sort_keys=True))


if __name__=='__main__':main()
