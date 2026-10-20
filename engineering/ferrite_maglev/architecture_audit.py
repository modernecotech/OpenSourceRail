"""Fail current-source checks if retired vehicle identities or adapters reappear.

Git history and ignored local execution caches are outside the current source
inventory. Generated gzip evidence is inspected as well as plain source text.
"""
import gzip
from pathlib import Path
import re
import subprocess

# Split tokens keep the rule itself from becoming a published old design ref.
TOKENS=['light-'+'metro-3car','urban-'+'shuttle-1car','wheel-'+'rail-reference',
        'metro-'+'6car','L'+'M3','H'+'M47','buildable-'+'trainset','reference_'+'3car','osr_'+'mech']
PATTERN=re.compile('|'.join(re.escape(s) for s in TOKENS),re.I)
TEXT={'.py','.rs','.md','.toml','.json','.sh','.js','.mjs','.html','.yaml','.yml','.txt','.svg','.csv','.proto'}


def files(root):
    output=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root)
    return sorted({Path(root)/p.decode() for p in output.split(b'\0') if p and (Path(root)/p.decode()).is_file()})


def scan(paths):
    findings=[]
    for path in paths:
        path=Path(path)
        compressed_text=path.suffix=='.gz' and Path(path.stem).suffix.lower() in TEXT
        if not compressed_text and path.suffix.lower() not in TEXT and path.name not in {'osr','Cargo.lock'}:continue
        tokens=[s.lower().encode() for s in TOKENS]
        # ASCII identity tokens can be scanned in bounded byte blocks without
        # decoding gigabytes of numeric geospatial CSV or copying whole files.
        total=0;tail=b'';found=False
        opener=gzip.open if path.suffix=='.gz' else open
        with opener(path,'rb') as stream:
            while block:=stream.read(1024*1024):
                total+=len(block)
                if path.suffix=='.gz' and total>64*1024*1024:
                    raise ValueError('bounded evidence audit exceeded: '+str(path))
                lowered=(tail+block).lower()
                if any(token in lowered for token in tokens):found=True;break
                tail=block[-max(map(len,tokens)):]
        if found:findings.append(str(path))

    return findings


def verify(root):
    findings=scan(files(root))
    if findings:raise ValueError('retired vehicle references remain: '+', '.join(findings[:20]))
    return dict(current_only=True,checked_files=len(files(root)),physical_release=False)
