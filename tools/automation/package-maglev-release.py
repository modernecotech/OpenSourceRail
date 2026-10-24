#!/usr/bin/env python3
"""Package verified, committed digital studies; never authorise physical release."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import delivery,iteration,model,release_bundle


def body_evidence_paths():
    """Select a current sensitivity; historical assurance directories stay intact."""
    from engineering.ferrite_maglev import assembled_body,moving_train,body_stiffness
    def checksum(path):
        if (path.resolve()!=path or path.is_symlink() or not path.is_file()
                or path.stat().st_size>release_bundle.MAX_MEMBER):
            raise ValueError('bounded ordinary body evidence required')
        value=sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
        return value.hexdigest()
    current={**moving_train.sources(),**assembled_body.sources(),**body_stiffness.sources()}
    candidates=sorted((ROOT/'engineering/assurance').glob('*/body-axial-receipt.json'))
    if len(candidates)>100:raise ValueError('bounded body evidence inventory required')
    selected=[]
    for candidate in candidates:
        checksum(candidate)
        value=json.loads(candidate.read_bytes())
        original=value.get('original_driver_path','build/body-axial-sensitivity/run.py')
        release_bundle.safe(original)
        if not original.startswith('build/') or not original.endswith('/run.py') or original in current:
            raise ValueError('owned ignored body driver path required')
        driver_hash=value.get('files_sha256',{}).get('run.py')
        if value.get('source_sha256')=={**current,original:driver_hash}:
            selected.append((candidate,original))
    if not selected:raise ValueError('no current body sensitivity; rerun it without overwriting historical assurance')
    receipt_path,original=selected[-1]
    base=receipt_path.parent
    checksum(receipt_path)
    receipt=json.loads(receipt_path.read_bytes())
    expected={'run.py','summary.json','reference-100MN.json.gz','gross-series.json.gz','drilled-series.json.gz'}
    if (receipt.get('schema')!='osr-body-axial-sensitivity-receipt/1'
            or set(receipt.get('files_sha256',{}))!=expected
            or any(receipt.get(k) is not False for k in (*model.FLAGS,'accepted_body_or_plant','city_default_changed'))):
        raise ValueError('body evidence scope or inventory differs')
    values={receipt_path.relative_to(ROOT).as_posix()}
    for name,expected_hash in receipt['files_sha256'].items():
        path=base/('body-axial-'+name)
        if checksum(path)!=expected_hash:raise ValueError('body evidence checksum differs')
        values.add(path.relative_to(ROOT).as_posix())
    instructions=base/'body-axial-reproduction.txt'
    checksum(instructions)
    values.add(instructions.relative_to(ROOT).as_posix())
    expected_sources={**current,original:receipt['files_sha256']['run.py']}
    if receipt.get('source_sha256')!=expected_sources:raise ValueError('body evidence sources stale')
    # The original ignored execution path maps to the byte-identical audit copy;
    # every other source remains at its original committed repository path.
    for name,expected_hash in expected_sources.items():
        release_bundle.safe(name)
        if name==original:continue
        if checksum(ROOT/name)!=expected_hash:raise ValueError('body evidence input changed')
        values.add(name)
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--shard-payload-mib',type=int,default=256,
                        help='Raw member payload per archive part (64–512 MiB)')
    parser.add_argument('--verify-bundle',action='store_true',
                        help='Verify an existing multipart bundle without native tools')
    parser.add_argument('--expected-manifest-sha256',
                        help='Trusted manifest digest for offline bundle verification')
    args=parser.parse_args()
    if args.verify_bundle:
        print(json.dumps(release_bundle.verify(args.output,expected_manifest_sha256=args.expected_manifest_sha256),indent=2));return
    if args.expected_manifest_sha256:
        parser.error('--expected-manifest-sha256 requires --verify-bundle')
    if not 64<=args.shard_payload_mib<=512:
        parser.error('--shard-payload-mib must be between64 and512')
    manifest=delivery.verify();iteration.verify()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=subprocess.check_output(['git','ls-tree','-rz','--full-tree','HEAD'],cwd=ROOT)
    tracked={}
    for item in raw.split(b'\0'):
        if item:
            meta,name=item.split(b'\t',1);mode,kind,digest=meta.split()
            if kind==b'blob' and mode in (b'100644',b'100755'):tracked[name.decode()]=digest.decode()
    paths=set(manifest['source_sha256'])
    paths.update(('README.md','LICENSE.md','OpenSourceRail-Book.pdf','docs/ARCHITECTURE.md','docs/ROADMAP.md',
                  'engineering/ferrite_maglev/README.md','engineering/ferrite_maglev/city-index.md',
                  'tools/automation/package-maglev-release.py','tools/automation/osr-python','tools/automation/retain-pilot-ui.py',
                  'docs/first-adoptable-product.md','docs/releases/v0.5.2.md',
                  'tools/automation/tests/verify-maglev-workbench.mjs','tools/automation/tests/verify-maglev-v05.mjs',
                  'engineering/ferrite_maglev/observer-prototype/README.md'))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'LICENSES').rglob('*') if p.is_file())
    paths.update(body_evidence_paths())
    for folder in ('reference','native','beam-only','system-development','baghdad-reference','coupled','iterative','station-powered','station-structure','station-protocol','station-native','moving-train','system-campaign','manufactured-dossier','manufactured-native','corridor','booster-kit','booster-native','interchange-hubs','line-capacity','hub-access','qualification','assembled-body','shared-hub-layout','body-stiffness','stopped-recovery','drive-construction','pilot-product','pilot-actuators',
                   'launch-optimisation','delivery-schedule','pilot-corridor','pilot-variants','pilot-lifecycle',
                   'assurance-profiles','capability-migration','pilot-delivery','candidate-native','candidate-magnetics','candidate-structures','full-dynamics','candidate-manufacturing','candidate-lifecycle','bim-field','operations-crosscheck','planning-platform','planning-ui','system-detailed'):
        packet=ROOT/'docs/design-engine/ferrite-maglev'/folder
        paths.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        for receipt in [*packet.rglob('manifest.json'),*packet.rglob('receipt.json')]:
            value=json.loads(receipt.read_text())
            for key in ('source_sha256','sources_sha256'):
                paths.update(value.get(key,{}))
    # Histories remain historical; their earlier source hashes are not rebound
    # to current files. The current profile packet identifies eligible executions.
    for name in ('engineering/assurance/v052-pilot-profiles',
                 'engineering/assurance/v052-pilot-lifecycle-native','engineering/assurance/v053-candidate-lifecycle-native','engineering/assurance/v052-pilot-ui',
                 'engineering/assurance/v052-pilot-body-axial','engineering/assurance/v053-detailed-body-axial',
                 'engineering/assurance/v053-magnetic-redesign-bounds','engineering/assurance/v053-propulsion-redesign-screen',
                 'engineering/assurance/v052-pilot-actuator-crosscheck',
                 'docs/design-engine/ferrite-maglev/pilot-actuators-rejected-120turn',
                 'docs/design-engine/ferrite-maglev/pilot-actuators-python-observer-baseline',
                 'docs/design-engine/ferrite-maglev/pilot-variant-failures'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/name).rglob('*') if p.is_file())
    result=release_bundle.publish(ROOT,args.output,paths,tracked,version=model.RELEASE_VERSION,
        commit=commit,source_sha256=manifest['source_sha256'],
        shard_limit=args.shard_payload_mib*1024*1024)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
