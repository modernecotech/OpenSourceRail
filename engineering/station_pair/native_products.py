"""Source-bound builds of the exact requested CLI, with immutable products.

A journey executable receipt cannot authenticate a neighbouring fleet/cycle
file. Select Cargo's explicit binary artifact and seal that file separately.
Compiler intermediates are a mutable cache; executed products and build logs
live in distinct immutable packets. Parent workers own CPU/memory budgets.
"""
from pathlib import Path
import fcntl,json,os,shutil,subprocess,time

from engineering.station_rail.common import digest,encoded,identity
from . import ROOT,native_bridge

PRODUCTS={'osr-journey':'src/main.rs','osr-station-cycle':'src/bin/osr-station-cycle.rs',
          'osr-station-fleet':'src/bin/osr-station-fleet.rs'}


def _aliases(state,packet,receipt):
    # Existing publication generators retain these generic filenames. They now
    # contain a receipt for the actual named product, with no implied journey
    # build or validation of an adjacent executable.
    (state/'native-build.json').write_bytes(encoded(receipt))
    (state/'native-build.log').write_bytes(b'Cargo artifact stream:\n'+
        (packet/'cargo.jsonl').read_bytes()+b'\nCargo diagnostics:\n'+(packet/'cargo.stderr.log').read_bytes())


def build(state,product,root=ROOT):
    if product not in PRODUCTS:raise ValueError('Known native CLI product required')
    root=Path(root).resolve();state=Path(state).resolve();state.mkdir(parents=True,exist_ok=True)
    source=native_bridge.sources(root)
    tools={name:subprocess.check_output([name,'--version'],cwd=root,text=True).strip() for name in ('cargo','rustc')}
    target=state/'native-product-target'
    command=['cargo','build','--manifest-path',str(root/native_bridge.NATIVE/'Cargo.toml'),
        '--release','--locked','--offline','--bin',product,'--message-format=json']
    settings=dict(CARGO_TARGET_DIR=str(target),CARGO_BUILD_JOBS='2',RUSTFLAGS='-C link-arg=-Wl,--threads=1')
    context=dict(product=product,source_sha256=source,tools=tools,command=command,
        producer_sha256=digest(__file__),build_environment=settings,working_directory=str(root),wall_timeout_s=180)
    packet=state/'native-products'/identity(context);receipt_path=packet/'receipt.json';binary=packet/product
    with (state/'native-product-build.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if receipt_path.is_file():
            r=json.loads(receipt_path.read_bytes())
            if (r.get('receipt_id')!=identity({k:v for k,v in r.items() if k!='receipt_id'}) or
                r.get('context')!=context or not binary.is_file() or binary.is_symlink() or
                r.get('binary_sha256')!=digest(binary) or native_bridge.sources(root)!=source or
                any(not (packet/n).is_file() or (packet/n).is_symlink() or digest(packet/n)!=h
                    for n,h in r.get('build_artifact_sha256',{}).items()) or
                set(r.get('build_artifact_sha256',{}))!={'cargo.jsonl','cargo.stderr.log','execution.json'}):
                raise ValueError('Native named-product cache changed; evidence retained: '+str(packet))
            _aliases(state,packet,r);return binary,r
        if packet.exists():raise ValueError('Interrupted native product build retained: '+str(packet))
        packet.mkdir(parents=True)
        # Never accept an unreceipted or stale neighbouring product. Removing
        # only this disposable cache output forces Cargo to relink the selected
        # CLI. All previous sealed products have independent copies/inodes.
        cached=target/'release'/product
        if cached.exists() or cached.is_symlink():cached.unlink()
        started=time.monotonic();failure=None;process=None
        with (packet/'cargo.jsonl').open('wb') as out,(packet/'cargo.stderr.log').open('wb') as err:
            try:process=subprocess.run(command,cwd=root,env=dict(os.environ,**settings),stdout=out,stderr=err,timeout=180)
            except (OSError,subprocess.TimeoutExpired) as exc:failure=str(exc)
        execution=dict(command=command,exit_code=None if process is None else process.returncode,
            failure=failure,wall_s=time.monotonic()-started)
        (packet/'execution.json').write_bytes(encoded(execution))
        if failure or process.returncode:raise ValueError('Native product build failed; retained '+str(packet))
        candidates=[]
        for line in (packet/'cargo.jsonl').read_text().splitlines():
            item=json.loads(line)
            if (item.get('reason')=='compiler-artifact' and item.get('target',{}).get('name')==product and
                item['target'].get('kind')==['bin'] and item.get('profile',{}).get('test') is False and
                item.get('manifest_path')==str(root/native_bridge.NATIVE/'Cargo.toml') and
                item['target'].get('src_path')==str(root/native_bridge.NATIVE/PRODUCTS[product]) and item.get('executable')):
                candidates.append(item)
        if len(candidates)!=1:raise ValueError('One exact non-test Cargo binary artifact required; logs retained')
        artifact=Path(candidates[0]['executable'])
        if (not artifact.is_file() or artifact.is_symlink() or not artifact.resolve().is_relative_to(target.resolve()) or
            native_bridge.sources(root)!=source or digest(__file__)!=context['producer_sha256']):
            raise ValueError('Native product source/artifact changed or escaped build target')
        shutil.copyfile(artifact,binary);binary.chmod(0o755)
        r=dict(schema='osr-named-native-product-build/1',product=product,source_sha256=source,tools=tools,
            command=command,build_jobs=2,link_threads=1,binary_sha256=digest(binary),
            context=context,cargo_artifact=candidates[0],
            build_artifact_sha256={n:digest(packet/n) for n in ('cargo.jsonl','cargo.stderr.log','execution.json')})
        r['receipt_id']=identity(r);receipt_path.write_bytes(encoded(r));_aliases(state,packet,r)
        return binary,r
