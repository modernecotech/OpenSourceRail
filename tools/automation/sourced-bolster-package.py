#!/usr/bin/env python3
"""Bounded publication transport; current tracked helper owns semantic replay.

Archived source is retained as inert evidence. Neither hashes nor semantic
replay grant physical, manufacturing or operating acceptance.
"""
import argparse,gzip,hashlib,importlib.util,io,json,os,re,stat,subprocess,sys,tarfile,tempfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[2]
PRODUCER='tools/automation/sourced-bolster-package.py'
HELPER='tools/automation/sourced-bolster-cell.py'
ARCHIVE='bolster-cell.tar.gz'
DESCRIPTOR='bolster-cell.json'
MAX_FILES=64
MAX_RAW=512*1024**2
MAX_COMPRESSED=128*1024**2
MAX_JSON=4*1024**2
BUFFER=1024**2
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)
NEIGHBOURS={'README.md','structural-methods.json','structural-methods.tar.gz'}
FIELDS={'schema','archive_path','archive_sha256','archive_bytes','raw_payload_bytes','files','package_id','candidate_id','body_candidate_id','evaluation_id',
        'helper_path','helper_sha256','producer_path','producer_sha256','source_sha256','semantic_verification','verification_scope','publication_id',*FLAGS}


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return hashlib.sha256(encoded(v)).hexdigest()
def _hash(v):return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None
def _size(v,maximum):return type(v) is int and 0<=v<=maximum

def _name(name):
    if not isinstance(name,str) or not 1<=len(name)<=200 or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._/-]*',name):raise ValueError('Ordinary relative member name required')
    path=PurePosixPath(name)
    if path.is_absolute() or any(p in ('','.','..') for p in path.parts) or path.as_posix()!=name:raise ValueError('Noncanonical archive path')
    return name


def _folder(path):
    path=Path(os.path.abspath(path))
    for p in (path,*path.parents):
        if p.is_symlink():raise ValueError('Symlink folder or ancestor refused')
    if not path.is_dir():raise ValueError('Existing ordinary folder required')
    return path


def _file(path,maximum):
    path=Path(path);before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size>maximum:raise ValueError('Bounded ordinary file required')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0));stream=os.fdopen(fd,'rb');actual=os.fstat(stream.fileno())
    if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(actual.st_dev,actual.st_ino,actual.st_size,actual.st_mtime_ns):stream.close();raise ValueError('Input changed while opening')
    return stream,before


def _digest(path,maximum=MAX_RAW):
    stream,before=_file(path,maximum);h=hashlib.sha256()
    with stream:
        while block:=stream.read(BUFFER):h.update(block)
        after=os.fstat(stream.fileno())
    current=Path(path).lstat()
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns) or before.st_mtime_ns!=current.st_mtime_ns:raise ValueError('Input changed while hashing')
    return h.hexdigest(),before.st_size


def _pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('Duplicate JSON key')
        d[k]=v
    return d


def _json(path):
    stream,_=_file(path,MAX_JSON)
    with stream:raw=stream.read(MAX_JSON+1)
    if len(raw)>MAX_JSON:raise ValueError('JSON size exceeded')
    v=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    if not isinstance(v,dict):raise ValueError('JSON object required')
    return v


def _unaccepted(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in FLAGS or k in ('physical_journey_completed','configuration_adopted','design_complete','physical_release'):
                if x is not False:raise ValueError('Publication cannot grant acceptance')
            _unaccepted(x)
    elif isinstance(v,list):
        for x in v:_unaccepted(x)


def inventory(folder):
    folder=_folder(folder);files={};directories=set()
    for p in sorted(folder.rglob('*')):
        if p.is_symlink():raise ValueError('Symlink payload refused')
        if p.is_dir():directories.add(p.relative_to(folder).as_posix());continue
        name=_name(p.relative_to(folder).as_posix());sha,size=_digest(p)
        files[name]=dict(bytes=size,sha256=sha)
        if len(files)>MAX_FILES or sum(x['bytes'] for x in files.values())>MAX_RAW:raise ValueError('Payload budget exceeded')
    if not files:raise ValueError('Nonempty closed payload required')
    parents={p.as_posix() for name in files for p in PurePosixPath(name).parents if p.as_posix()!='.'}
    if directories!=parents:raise ValueError('Unknown/empty payload directory')
    return files


def _core(folder,files):
    m=_json(Path(folder)/'manifest.json');_unaccepted(m)
    if m.get('schema')!='osr-bolster-cell-package/1' or m.get('execution')!='completed' or m.get('package_id')!=identity({k:v for k,v in m.items() if k!='package_id'}):raise ValueError('Exact completed cell manifest required')
    if m.get('files')!={k:v for k,v in files.items() if k!='manifest.json'}:raise ValueError('Cell folder closure differs')
    if any(m.get(k) is not False for k in FLAGS) or m.get('selection_purpose')!='next-experiment-only' or m.get('revised_body_ifc_exported_and_reopened') is not True:raise ValueError('Unreleased IFC-reopened research cell required')
    for k in ('candidate_id','body_candidate_id','evaluation_id','helper_sha256'):
        if not _hash(m.get(k)):raise ValueError('Canonical cell identity required')
    if not isinstance(m.get('source_sha256'),dict) or not m['source_sha256']:raise ValueError('Core sources required')
    for name,value in m['source_sha256'].items():_name(name);assert_hash(value)
    return m


def assert_hash(value):
    if not _hash(value):raise ValueError('Canonical SHA256 required')


def _helper(root):
    root=_folder(root)
    for name in (HELPER,PRODUCER):
        path=root/name
        if path.is_symlink() or not path.is_file():raise ValueError('Current fixed repository producer required')
        tracked=subprocess.run(['git','ls-files','--error-unmatch','--',name],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if tracked.returncode:raise ValueError('Stage current repository helper/producer before publication: '+name)
    if _digest(root/PRODUCER)[0]!=_digest(__file__)[0]:raise ValueError('Executing publication producer differs')
    spec=importlib.util.spec_from_file_location('osr_current_bolster_cell_'+_digest(root/HELPER)[0],root/HELPER)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    if Path(helper.__file__).resolve()!=root/HELPER or helper.PRODUCER!=HELPER:raise ValueError('Fixed trusted helper path differs')
    return helper


def _report(r,package_id):
    expected={'verified','package_id','execution','semantic_replay_executed','cases','journeys','selection_purpose',*FLAGS}
    if not isinstance(r,dict) or set(r)!=expected or r.get('verified') is not True or r.get('package_id')!=package_id or r.get('execution')!='completed' or r.get('semantic_replay_executed') is not True or type(r.get('cases')) is not int or r['cases']!=1 or type(r.get('journeys')) is not int or r['journeys']!=9 or r.get('selection_purpose')!='next-experiment-only':raise ValueError('Exact current-helper nine-journey replay required')
    _unaccepted(r)


def create_archive(folder,path,files):
    """Deterministic ordinary-file archive; caller supplies closed inventory."""
    folder=_folder(folder);path=Path(path)
    if inventory(folder)!=files:raise ValueError('Input closure changed')
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT) as tar:
                for name,item in sorted(files.items()):
                    _name(name);info=tarfile.TarInfo(name);info.size=item['bytes'];info.mode=0o644;info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
                    stream,_=_file(folder/name,MAX_RAW)
                    with stream:tar.addfile(info,stream)
        if raw.tell()>MAX_COMPRESSED:raise ValueError('Compressed archive budget exceeded')
    if inventory(folder)!=files:raise ValueError('Input mutated during archive creation')
    return _digest(path,MAX_COMPRESSED)


class _Limited:
    def __init__(self,stream,limit):self.stream=stream;self.limit=limit;self.count=0
    def read(self,size=-1):
        remaining=self.limit-self.count
        if size<0 or size>remaining+1:size=remaining+1
        raw=self.stream.read(size);self.count+=len(raw)
        if self.count>self.limit:raise ValueError('Decompressed archive budget exceeded')
        return raw


def extract_archive(path,destination,files):
    """Bounded stream extraction into a fresh private folder; never extracts links."""
    if not isinstance(files,dict) or not 1<=len(files)<=MAX_FILES:raise ValueError('Bounded inventory required')
    for name,item in files.items():
        _name(name)
        if not isinstance(item,dict) or set(item)!={'bytes','sha256'} or not _size(item['bytes'],MAX_RAW):raise ValueError('Strict payload row required')
        assert_hash(item['sha256'])
    if sum(i['bytes'] for i in files.values())>MAX_RAW:raise ValueError('Raw payload budget exceeded')
    out=Path(destination)
    if out.exists() or out.is_symlink():raise ValueError('Fresh extraction directory required')
    out.mkdir(mode=0o700);seen=set();total=0;stream,_=_file(path,MAX_COMPRESSED)
    with stream,gzip.GzipFile(fileobj=stream,mode='rb') as gz:
        limited=_Limited(gz,MAX_RAW+MAX_FILES*1024+10240)
        with tarfile.open(fileobj=limited,mode='r|') as tar:
            for member in tar:
                name=_name(member.name)
                if name in seen or name not in files or not member.isfile() or member.issym() or member.islnk() or member.pax_headers:raise ValueError('Unknown, duplicate or nonordinary tar member')
                if member.uid or member.gid or member.mtime or member.mode!=0o644 or member.uname or member.gname:raise ValueError('Noncanonical tar metadata')
                if member.size!=files[name]['bytes']:raise ValueError('Member length differs')
                seen.add(name);total+=member.size
                if len(seen)>MAX_FILES or total>MAX_RAW:raise ValueError('Archive budget exceeded')
                target=out/name;target.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();count=0
                with tar.extractfile(member) as src,target.open('xb') as dst:
                    while block:=src.read(BUFFER):count+=len(block);h.update(block);dst.write(block)
                if count!=member.size or h.hexdigest()!=files[name]['sha256']:raise ValueError('Extracted payload identity differs')
        while block:=limited.read(BUFFER):
            if any(block):raise ValueError('Unexpected trailing archive payload')
    if seen!=set(files) or inventory(out)!=files:raise ValueError('Extracted inventory closure differs')
    return out


def descriptor(value):
    if not isinstance(value,dict) or set(value)!=FIELDS or value.get('schema')!='osr-sourced-bolster-cell-publication/1' or value.get('archive_path')!=ARCHIVE or value.get('helper_path')!=HELPER or value.get('producer_path')!=PRODUCER:raise ValueError('Exact publication descriptor required')
    _unaccepted(value)
    if any(value[k] is not False for k in FLAGS) or value.get('publication_id')!=identity({k:v for k,v in value.items() if k!='publication_id'}):raise ValueError('Publication identity/flags differ')
    for key in ('archive_sha256','package_id','candidate_id','body_candidate_id','evaluation_id','helper_sha256','producer_sha256'):assert_hash(value[key])
    if not _size(value['archive_bytes'],MAX_COMPRESSED) or not value['archive_bytes'] or not _size(value['raw_payload_bytes'],MAX_RAW):raise ValueError('Publication budget exceeded')
    rows=value['files']
    if not isinstance(rows,dict) or not 1<=len(rows)<=MAX_FILES or 'manifest.json' not in rows:raise ValueError('Closed bounded file inventory required')
    for name,item in rows.items():
        _name(name)
        if not isinstance(item,dict) or set(item)!={'bytes','sha256'} or not _size(item['bytes'],MAX_RAW):raise ValueError('Exact payload row required')
        assert_hash(item['sha256'])
    if sum(item['bytes'] for item in rows.values())!=value['raw_payload_bytes']:raise ValueError('Raw payload total differs')
    if not isinstance(value['source_sha256'],dict) or not value['source_sha256']:raise ValueError('Source bindings required')
    for name,sha in value['source_sha256'].items():_name(name);assert_hash(sha)
    _report(value['semantic_verification'],value['package_id'])
    if value['verification_scope']!='current-code-nine-journey-replay-and-IFC-reopen;native-recorded-integrity-only':raise ValueError('Unsupported verification scope')
    return value


def _publication_folder(path):
    folder=_folder(path)
    if any(p.name not in NEIGHBOURS|{ARCHIVE,DESCRIPTOR} or p.is_symlink() or not p.is_file() for p in folder.iterdir()):raise ValueError('Unknown publication directory entry')
    return folder


def publish(folder,output,*,root=ROOT):
    folder=_folder(folder);candidate_output=Path(os.path.abspath(output))
    if candidate_output==folder or folder in candidate_output.parents:raise ValueError('Publication must not mutate immutable cell folder')
    helper=_helper(root);files=inventory(folder);core=_core(folder,files)
    report=helper.verify(folder,root=root,replay=True);_report(report,core['package_id'])
    if inventory(folder)!=files:raise ValueError('Semantic verification mutated immutable input')
    output=Path(output)
    if not output.exists():output.mkdir(parents=True)
    output=_publication_folder(output)
    if any((output/name).exists() for name in (ARCHIVE,DESCRIPTOR)):raise ValueError('Existing cell publication must be preserved')
    with tempfile.TemporaryDirectory(prefix='.bolster-publication-',dir=output.parent) as temp:
        stage=Path(temp);sha,size=create_archive(folder,stage/ARCHIVE,files)
        value=dict(schema='osr-sourced-bolster-cell-publication/1',archive_path=ARCHIVE,archive_sha256=sha,archive_bytes=size,
            raw_payload_bytes=sum(i['bytes'] for i in files.values()),files=files,package_id=core['package_id'],candidate_id=core['candidate_id'],body_candidate_id=core['body_candidate_id'],evaluation_id=core['evaluation_id'],
            helper_path=HELPER,helper_sha256=_digest(Path(root)/HELPER)[0],producer_path=PRODUCER,producer_sha256=_digest(Path(root)/PRODUCER)[0],source_sha256=core['source_sha256'],
            semantic_verification=report,verification_scope='current-code-nine-journey-replay-and-IFC-reopen;native-recorded-integrity-only',**FLAGS)
        if value['helper_sha256']!=core['helper_sha256']:raise ValueError('Current helper differs from original cell')
        value['publication_id']=identity(value);descriptor(value);(stage/DESCRIPTOR).write_bytes(encoded(value))
        for name in (ARCHIVE,DESCRIPTOR):os.replace(stage/name,output/name)
    return value


def verify_publication(output,*,root=ROOT):
    output=_publication_folder(output);value=descriptor(_json(output/DESCRIPTOR));helper=_helper(root)
    if _digest(Path(root)/HELPER)[0]!=value['helper_sha256'] or _digest(Path(root)/PRODUCER)[0]!=value['producer_sha256']:raise ValueError('Current publication/helper sources differ')
    if _digest(output/ARCHIVE,MAX_COMPRESSED)!=(value['archive_sha256'],value['archive_bytes']):raise ValueError('Publication archive hash/size differs')
    with tempfile.TemporaryDirectory(prefix='osr-bolster-publication-') as temp:
        folder=extract_archive(output/ARCHIVE,Path(temp)/'cell',value['files']);core=_core(folder,value['files'])
        if any(core[key]!=value[key] for key in ('package_id','candidate_id','body_candidate_id','evaluation_id','source_sha256','helper_sha256')):raise ValueError('Descriptor rebound from actual cell')
        actual=helper.verify(folder,root=root,replay=True);_report(actual,value['package_id'])
        if encoded(actual)!=encoded(value['semantic_verification']):raise ValueError('Current semantic replay differs')
        if inventory(folder)!=value['files']:raise ValueError('Replay mutated extracted evidence')
    return dict(verified=True,publication_id=value['publication_id'],package_id=value['package_id'],semantic_replay_executed=True,journeys=9,native_fresh_solve_executed=False,**FLAGS)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('publish');p.add_argument('folder',type=Path);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('verify-publication');p.add_argument('output',type=Path)
    args=parser.parse_args()
    try:result=publish(args.folder,args.output,root=args.root) if args.command=='publish' else verify_publication(args.output,root=args.root)
    except (ValueError,OSError,tarfile.TarError,EOFError) as err:parser.exit(2,str(err)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))
if __name__=='__main__':main()
