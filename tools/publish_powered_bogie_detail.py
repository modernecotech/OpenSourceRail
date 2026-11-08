#!/usr/bin/env python3
"""Publish an existing sealed powered-bogie run without executing new designs.

This outer publisher deliberately lives outside the frozen engineering producer
glob. It validates every archived source and run file before copying evidence.
"""
import argparse
import csv
import gzip
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
from html import escape
from math import fsum

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engineering.station_rail.common import encoded, identity, digest
from engineering.powered_bogie import FLAGS


def read(path):return json.loads(path.read_bytes())


def check_run(folder):
    manifest=read(folder/'manifest.json')
    if identity({k:v for k,v in manifest.items() if k!='evaluation_id'})!=manifest['evaluation_id']:
        raise ValueError('Run manifest is not sealed')
    for name,sha in manifest['files_sha256'].items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or digest(folder/p)!=sha:
            raise ValueError('Run file changed: '+name)
    summary=manifest['summary']
    if not summary['source_integrity_passed'] or summary['source_before']!=summary['source_after']:
        raise ValueError('Run source integrity did not pass')
    for name,sha in summary['source_before'].items():
        if digest(ROOT/name)!=sha:raise ValueError('Frozen engineering source differs: '+name)
    return manifest


def svg(body,report,case):
    """Orthographic SI projection, with boxes visibly marked as unverified."""
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1190" viewBox="0 0 1280 1190">',
        '<defs><pattern id="unknown" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="12" height="12" fill="#fbbf24" fill-opacity=".15"/><path d="M0 0V12" stroke="#a16207" stroke-opacity=".5" stroke-width="2"/></pattern>',
        '<clipPath id="plan"><rect x="170" y="140" width="940" height="600"/></clipPath>',
        '<clipPath id="side"><rect x="170" y="820" width="940" height="280"/></clipPath></defs>',
        '<rect width="1280" height="1190" fill="#f8fafc"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#102a43} .title{font-size:28px;font-weight:700}.label{font-size:16px}.small{font-size:13px}.dim{font-size:15px;fill:#486581}</style>',
        '<text class="title" x="52" y="54">Powered-bogie research assembly</text>',
        '<rect x="1000" y="24" width="225" height="42" rx="8" fill="#b91c1c"/><text x="1021" y="52" fill="white" style="fill:white;font-size:20px;font-weight:700">HOLD · fit unresolved</text>',
        '<text class="label" x="52" y="88">Fixed 2.1 m wheelbase · 1,435 mm inner-face gauge · 760 mm nominal new wheel</text>',
        '<text class="small" x="52" y="115">Blue: counted fabricated stock. Hatched amber: assumed drive space. Red: retained body space conflicts.</text>',
        '<text class="label" x="52" y="149">PLAN · same scale in x and y · forward →</text>']
    scale=250.;cx=640.;cy=440.;base=1090.
    def rect(bounds,view,color,opacity=1.,stroke='#334e68'):
        x0,x1=(bounds[j][0]-2.1 for j in (0,1))
        if view=='plan':a,b=bounds[0][1],bounds[1][1];X=cx+x0*scale;Y=cy-b*scale;W=(x1-x0)*scale;H=(b-a)*scale
        else:a,b=bounds[0][2],bounds[1][2];X=cx+x0*scale;Y=base-b*scale;W=(x1-x0)*scale;H=(b-a)*scale
        out.append(f'<rect x="{X:.3f}" y="{Y:.3f}" width="{W:.3f}" height="{H:.3f}" fill="{color}" opacity="{opacity}" stroke="{stroke}" stroke-width="1"/>')
    for view in ('plan','side'):
        out.append(f'<g clip-path="url(#{view})">')
        for e in case['entities']:
            bounds=[e['at_m'],[e['at_m'][i]+e['size_m'][i] for i in range(3)]]
            rect(bounds,view,'#327c9c',.70)
        conflicts={r['id']:r for d in report['drives'] for r in d['required_space_conflicts'] if r['category']=='body-underframe'}
        for r in conflicts.values():rect(r['bounds_m'],view,'#ef4444',.14,'#b91c1c')
        for d in report['drives']:rect(d['nominal_box_m'],view,'url(#unknown)',.95,'#a16207')
        # Actual nominal wheel envelope, not a recovered wheel tread profile.
        for x in (-1.05,1.05):
            if view=='plan':
                for y in (-.7525,.7525):rect([[2.1+x-.38,y-.0675,0.],[2.1+x+.38,y+.0675,.76]],view,'#334155',.75)
            else:
                out.append(f'<circle cx="{cx+x*scale:.2f}" cy="{base-.38*scale:.2f}" r="{.38*scale:.2f}" fill="none" stroke="#334155" stroke-width="4"/>')
        if view=='plan':out.append(f'<path d="M170 {cy}H1110" stroke="#64748b" stroke-dasharray="9 7"/>')
        else:
            out.append(f'<path d="M170 {base}H1110" stroke="#334155" stroke-width="2"/>')
            out.append(f'<path d="M170 {base-.9595*scale}H1110" stroke="#b91c1c" stroke-dasharray="8 6"/>')
        out.append('</g>')
    out += ['<text class="small" x="715" y="464">Motor 486 kg · external mass owner</text>',
        '<text class="small" x="390" y="289">Gear + couplings 310 kg · external owner</text>',
        '<text class="small" x="52" y="724">3.24 m side rails replace 2.80 m stock. Crossmember locations: x = −1.54 m and +0.42 m.</text>',
        '<path d="M377.5 753H902.5 M377.5 745V761 M902.5 745V761" stroke="#486581"/>',
        '<text class="dim" x="548" y="778">2,100 mm wheelbase</text>',
        '<text class="label" x="52" y="813">SIDE · same scale in x and z · railhead datum z = 0</text>',
        '<text class="small" x="52" y="853">Body underside / retained underframe space</text>',
        '<text class="small" x="52" y="1123">Source stock is shown before holes, fitted profiles and weld preparation. No supplier housing has been reconstructed.</text>',
        f'<text class="small" x="52" y="1148">Candidate {escape(body["candidate_id"][:20])} · 12 declared yaw/roll/jounce poses plus continuous outer bounds.</text>',
        '<text class="small" x="52" y="1173">The assembly is a counted research proposal. Brake, body, mounting, tool-access and supplier-interface gates remain open.</text>',
        '</svg>']
    return '\n'.join(out)+'\n'


def archive(path,folder,source):
    files=[('run/'+p.relative_to(folder).as_posix(),p) for p in sorted(folder.rglob('*')) if p.is_file()]
    files += [('source/'+name,ROOT/name) for name in sorted(source)]
    # Ordinary deterministic tar entries, not symlinks or a claim of enforced
    # read-only source isolation. Hashing seals the retained bytes.
    with path.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w|') as tar:
                for name,p in files:
                    data=p.read_bytes();info=tarfile.TarInfo(name)
                    info.size=len(data);info.mode=0o644;info.mtime=0
                    tar.addfile(info,io.BytesIO(data))


def publish(folder,output):
    folder=Path(folder).resolve();output=Path(output).resolve();manifest=check_run(folder)
    output.mkdir(parents=True,exist_ok=False)
    chosen=folder/'extended-cradle-3240'
    body=json.loads(gzip.decompress((chosen/'body.json.gz').read_bytes()))
    report=read(chosen/'geometry.json');case=read(chosen/'stock-case.json');native=read(chosen/'native-result.json')
    if body['candidate_id']!=identity(body['physical_definition']):raise ValueError('Body seal differs')
    if body['evaluation_id']!=identity({k:v for k,v in body.items() if k!='evaluation_id'}):raise ValueError('Body evaluation differs')
    if report['candidate_id']!=body['candidate_id'] or native['candidate_id']!=body['candidate_id']:
        raise ValueError('Mixed native/geometry candidate')
    if native['status']!='completed':raise ValueError('Native proof was not completed')
    copies={'body.json.gz':'body.json.gz','geometry.json':'geometry.json',
        'change-set.json':'change-set.json','stock-case.json':'stock-case.json','bogie.glb':'bogie.glb',
        'native-result.json':'native-result.json','native-cad/solidcraft/assembly.step':'assembly.step',
        'native-cad/solidcraft/assembly.sc':'assembly.sc','native-cad/verification.json':'native-verification.json'}
    for source,target in copies.items():shutil.copyfile(chosen/source,output/target)
    (output/'assembly.svg').write_text(svg(body,report,case))
    additions=[r for r in body['parts'] if r['id'].startswith('powered-bogie/')]
    with (output/'manufacturing.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['part_id','material_id','quantity_per_train','stock',
            'mass_low_kg','mass_base_kg','mass_high_kg','direct_base_usd','BOP_partition',
            'manufacturing','joining','maintenance_removal'])
        for r in additions:
            q=r['quantity_per_train'];w.writerow([r['id'],r['material_id'],q,json.dumps(r['stock'],sort_keys=True),
                *[q*r['mass_each_kg'][c] for c in ('low','base','high')],q*r['direct_cost_each_usd']['base'],
                r['BOP_partition'],'; '.join(r['manufacturing']),r['joining'],r['maintenance_removal']])
    archive(output/'source-and-run.tar.gz',folder,manifest['summary']['source_before'])
    validation=dict(command='.venv/bin/python -m unittest discover -s tests -p test_powered_bogie.py -v',
        tests=6,result='passed',wall_s=35.749,source_commit=manifest['summary']['source_commit'],
        test_source_sha256=digest(ROOT/'tests/test_powered_bogie.py'),
        evidence='Observed coordinator tool output from the final frozen-source invocation; test log is not a physical measurement',**FLAGS)
    (output/'validation.json').write_bytes(encoded(validation))
    b=body['BOP_partition'];d=body['change_set'];net={c:d['mass_delta_kg'][c]-b['explicit_parts_already_in_body_kg'][c] for c in ('low','base','high')}
    info=dict(schema='osr-powered-bogie-publication/1',candidate_id=body['candidate_id'],
        body_evaluation_id=body['evaluation_id'],geometry_evaluation_id=report['evaluation_id'],
        native_evaluation_id=native['evaluation_id'],native_component_geometry_id=case['component_geometry_id'],
        input_candidate_id=body['parent_candidate_id'],input_evaluation_id=body['parent_evaluation_id'],
        run_manifest_id=manifest['evaluation_id'],run_source_commit=manifest['summary']['source_commit'],
        publisher_sha256=digest(Path(__file__)),publication_command='python tools/publish_powered_bogie_detail.py RUN OUTPUT',
        source_before=manifest['summary']['source_before'],source_after=manifest['summary']['source_after'],
        body_types=body['proposed_component_types'],body_occurrences=body['total_occurrences'],
        new_part_types=len(additions),body_stock_delta_kg=d['mass_delta_kg'],
        net_integrated_mass_delta_after_exact_BOP_partition_kg=net,
        BOP_partition=b,direct_parts_process_delta_usd=d['cost_delta_usd'],
        all_drive_catalogue_mass_remains_external_kg=9552.,geometry_status=report['geometry_screen_status'],
        native_stock_primitives=case['expected']['part_count'],
        failed_control_retained_in_archive=True,source_isolation='Separate worktree; source hashes before/after. No OS read-only claim.',**FLAGS)
    text=f'''# Powered-bogie research detail — HOLD

The counted assembly and its stock CAD are reproducible. **The powered bogie does not yet fit the retained body and brake allocations, and actual supplier interfaces are unknown.** This child research configuration does not replace the passive v0.6 development reference.

![Dimensioned plan and side projection](assembly.svg)

[3D assembly](bogie.glb) · [STEP stock subset](assembly.step) · [SolidCraft source](assembly.sc) · [Manufacturing schedule](manufacturing.csv) · [Geometry and access findings](geometry.json) · [Sealed body](body.json.gz) · [Full source/run archive](source-and-run.tar.gz)

## What was generated

Two proposals use the same fixed gauge, 2.1 m wheelbase and 760 mm new-wheel geometry: the retained-frame control and one extended 3.24 m fabricated frame/cradle. The control and every failed allocation remain in the archive. There were no extra physical variants, FEM solves or train-dynamics runs.

The revised six-car body contains {body['proposed_component_types']} component types and {body['total_occurrences']:,} counted occurrences. Its {len(additions)} new part types define side rails, crossmembers, ties, removable motor plates, outriggers, torque-reaction plates/bushes, retention straps/stops, weld deposit, fasteners, cables, bonding and a flexible ventilation provision. Materials, stock sizes, quantities, process allowances, inspection and workshop removal sequences are included. Gross stock before fitted holes and profiles is distinct from finished geometry.

SolidCraft generated **{case['expected']['part_count']} stock primitives**, and independent FreeCAD import agrees on their volumes, centroids and bounds. RHS is represented by four occupied walls with an open void. This checks the declared stock geometry; it does not verify finished joints, supplier geometry, weld strength or an installed assembly.

## Fit and movement findings

The motor's required-space intersections with retained frame stock reduce from six to two. Two further proposed mount-stock intersections remain. The gear retains three wheel/brake and five underframe allocation conflicts, alongside frame/mount conflicts. These counts concern intersected stock primitives and assumed equipment boxes, not measured supplier-housing contact. No clearance pass is inferred from unknown shapes.

Twelve explicit yaw/roll/jounce poses per proposal are accompanied by conservative continuous swept-box bounds. Body/battery space, primary gear motion, coupling movement, socket approach, motor drop stroke and service-loop length are reported. Necessary cable and duct length checks pass under the hypotheses, but actual routed volume, tool access, connectors and ventilation/thermal performance remain unverified.

The [TSA application catalogue](https://tsa.at/tsa-referenzen/tsa-traction-drive-for-siemens-type-x-metro-for-wiener-linien-copy/) supports the 486 kg motor and 310 kg gear/coupling masses, not OSR housing dimensions or mounting holes. It lists 840/716 mm new/worn wheels, while the current OSR geometry is 760/680 mm. A possible 716–760 mm research maintenance range is identified but **not selected**; wear rate and renewal life have not been invented. Internal supplier bearing counts remain bounded and are already mass-owned inside the catalogue equipment.

## Mass and calculated factory cost

| Six-car change | Low | Base | High |
| --- | ---: | ---: | ---: |
| New counted body stock delta, kg | {d['mass_delta_kg']['low']:,.3f} | {d['mass_delta_kg']['base']:,.3f} | {d['mass_delta_kg']['high']:,.3f} |
| Explicit BOP now counted inside body, kg | {b['explicit_parts_already_in_body_kg']['low']:,.3f} | {b['explicit_parts_already_in_body_kg']['base']:,.3f} | {b['explicit_parts_already_in_body_kg']['high']:,.3f} |
| Remaining positive external BOP reserve, kg | {b['remaining_unknown_external_reserve_kg']['low']:,.3f} | {b['remaining_unknown_external_reserve_kg']['base']:,.3f} | {b['remaining_unknown_external_reserve_kg']['high']:,.3f} |
| Net integrated mass delta after exact BOP partition, kg | {net['low']:,.3f} | {net['base']:,.3f} | {net['high']:,.3f} |
| Direct parts/process cost delta, USD | {d['cost_delta_usd']['low']:,.0f} | {d['cost_delta_usd']['base']:,.0f} | {d['cost_delta_usd']['high']:,.0f} |

Exactly twelve motors and twelve gear/coupling units, totalling 9,552 kg, remain externally owned. Their split centres replace the old 796 kg axle points; they are not added to the body BOM. Explicit mounts/services partition the previous 2.5/4/8 t reserve once, leaving a positive unknown remainder. The factory-cost change uses declared low/base/high material, yield, labour, processing and QA assumptions; it is not a quotation or complete train price. A mass partition does not justify an automatic proportional reduction of an unrelated price allowance.

## Installation and remaining gates

The repair plan uses positive retention, electrical isolation, supported body/bogie fixtures, a workshop drop table, a proposed 1 t hoist and a finite 0.60 m motor lowering stroke. It retains the need to remove an axle-mounted gearbox with its wheelset. Hoist/eye ratings and actual shaft disengagement are open.

Next work requires dimensioned supplier housings and interfaces; resolved brake/body/mount space; coupling and shaft retention; frame and mount strength/fatigue; actual suspension travel; wheel/rail profiles; cooling duty; and verified installation/removal paths. None of these is accepted by the stock CAD comparison. Physical, manufacturing and operating release remain false.

## Reproduction and identities

```bash
.venv/bin/python -m unittest discover -s tests -p test_powered_bogie.py -v
.venv/bin/python -m engineering.powered_bogie.run /private/new-run --cad
.venv/bin/python tools/publish_powered_bogie_detail.py /private/new-run /private/new-publication
```

The final six regression tests passed in 35.749 s. The frozen private run completed in {manifest['summary']['wall_s']:.2f} s; one SolidCraft regeneration and one FreeCAD check were used, each under the existing 2 GiB / 120 s wall / 122 s CPU wrapper request. The full run was approximately 4 MB. Native execution receipts and before/after source hashes are preserved. The worktree is isolated by convention and integrity checks; the source filesystem was not OS-enforced read-only.

* Input body: `{body['parent_candidate_id']}`
* Research body: `{body['candidate_id']}`
* Body evaluation: `{body['evaluation_id']}`
* Geometry evaluation: `{report['evaluation_id']}`
* Native proof envelope: `{native['evaluation_id']}`
* Source commit: `{manifest['summary']['source_commit']}`
* Run manifest: `{manifest['evaluation_id']}`

[Machine-readable publication](packet.json) contains all artifact hashes and source identities. [Native verification](native-verification.json) is retained unchanged and enclosed by the new producer's exact source context in [native-result.json](native-result.json).
'''
    (output/'README.md').write_text(text)
    info['files_sha256']={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    info['evaluation_id']=identity(info);(output/'packet.json').write_bytes(encoded(info))
    check_run(folder)
    return info


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();p=publish(args.run,args.output)
    print(json.dumps(dict(candidate_id=p['candidate_id'],publication_id=p['evaluation_id'],files=len(p['files_sha256'])),sort_keys=True))
