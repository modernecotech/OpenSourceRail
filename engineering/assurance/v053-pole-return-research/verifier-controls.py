"""Non-numerical archive-integrity rejection controls in disposable copied trees."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,tempfile
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('research_verify',BASE/'archive/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reseal(root):
    p=root/'manifest.json';m=json.loads(p.read_bytes())
    m['files_sha256']={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file() and p!=root/'manifest.json'}
    p.chmod(0o644);p.write_text(json.dumps(m))
def manifest(root,update):
    p=root/'manifest.json';m=json.loads(p.read_bytes());update(m);p.chmod(0o644);p.write_text(json.dumps(m))
def write(root,name,data):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():p.chmod(0o644)
    p.write_text(data)
def test(name,mutate,rejected=True):
    with tempfile.TemporaryDirectory(prefix='verifier-test-',dir=BASE) as temporary:
        root=Path(temporary)/'archive';shutil.copytree(BASE/'archive',root)
        target=mutate(root) or root
        try:v.verify_archive(target)
        except (ValueError,OSError) as error:
            if not rejected:raise
            records.append(dict(test=name,state='rejected',reason=str(error)));return
        if rejected:raise AssertionError('tampering accepted: '+name)
        records.append(dict(test=name,state='accepted'))

test('valid-current-archive',lambda r:None,False)
test('unexpected-schema',lambda r:manifest(r,lambda m:m.update(schema='unexpected/9')))
test('unlisted-nested-manifest',lambda r:write(r,'evidence/manifest.json','{}'))
def listed(root):write(root,'evidence/manifest.json','{}');reseal(root)
test('listed-nested-manifest-is-hashed',listed,False)
def tampered_nested(root):listed(root);write(root,'evidence/manifest.json','{"tampered":true}')
test('listed-nested-manifest-tamper',tampered_nested)
def symlink_member(root):
    p=root/'README.md';p.unlink();p.symlink_to(BASE/'README.md')
test('symlink-member',symlink_member)
def symlink_directory(root):
    shutil.rmtree(root/'inputs');(root/'inputs').symlink_to(BASE/'archive/inputs',target_is_directory=True)
test('symlink-directory',symlink_directory)
def symlink_root(root):
    link=root.parent/'link';link.symlink_to(root,target_is_directory=True);return link
test('symlink-archive-root',symlink_root)
def symlink_ancestor(root):
    link=root.parent/'parent-link';link.symlink_to(root.parent,target_is_directory=True);return link/'archive'
test('symlink-ancestor',symlink_ancestor)
def fifo(root):os.mkfifo(root/'evidence/fifo')
test('special-fifo-member',fifo)
def too_big(root):
    with (root/'evidence/oversized').open('wb') as f:f.truncate(v.MAX_MEMBER_BYTES+1)
test('individual-byte-limit',too_big)
def total(root):
    for i in range(4):
        with (root/f'evidence/large-{i}').open('wb') as f:f.truncate(v.MAX_MEMBER_BYTES)
test('total-byte-limit',total)
def too_many(root):
    for i in range(v.MAX_MEMBERS):(root/f'evidence/extra-{i}').touch()
test('member-count-limit',too_many)
def dirs(root):
    for i in range(v.MAX_DIRECTORIES):(root/f'empty-{i}').mkdir()
test('directory-count-limit',dirs)
def depth(root):
    p=root
    for i in range(v.MAX_DEPTH):p=p/'nested';p.mkdir()
test('directory-depth-limit',depth)
test('negative-raw-size',lambda r:manifest(r,lambda m:m['raw_records']['results.json'].update(raw_bytes=-1)))
test('boolean-raw-size',lambda r:manifest(r,lambda m:m['raw_records']['results.json'].update(raw_bytes=True)))
test('oversized-raw-size',lambda r:manifest(r,lambda m:m['raw_records']['results.json'].update(raw_bytes=v.MAX_RAW_BYTES+1)))
test('unsafe-raw-path',lambda r:manifest(r,lambda m:m['raw_records']['results.json'].update(path='../outside')))
test('invalid-hash',lambda r:manifest(r,lambda m:m['files_sha256'].update({'README.md':'x'*64})))
test('release-claim',lambda r:manifest(r,lambda m:m.update(manufacturing_release=True)))
test('duplicate-json-key',lambda r:write(r,'manifest.json','{"schema":"a","schema":"b"}'))
test('nonfinite-json-number',lambda r:write(r,'manifest.json','{"schema":"osr-portable-pole-return-research/1","bad":NaN}'))
test('overflow-json-number',lambda r:manifest(r,lambda m:m.update(bad=1e999)))
for name in ('','.', '..','a/../b','/absolute','a\\b','a//b','./a','a\x00b','a\nb'):
    try:v.safe(name)
    except ValueError:records.append(dict(test='unsafe-name-'+repr(name),state='rejected'))
    else:raise AssertionError('unsafe name accepted: '+repr(name))
report=dict(schema='osr-portable-verifier-hardening-tests/1',checks=len(records),passed=True,checks_detail=records,numerical_experiments_added=False)
(BASE/'verifier-hardening-tests.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps(dict(passed=True,checks=len(records),numerical_experiments_added=False)))
