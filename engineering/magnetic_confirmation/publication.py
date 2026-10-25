"""Publish a verified retained run without rerunning a solver or changing history."""
import gzip
import io
import json
from pathlib import Path
import tarfile
from .runner import FLAGS,SCHEMA,encoded,file_hash,inventory,verify,write


def _archive(run_dir):
    output=io.BytesIO();total=0
    with gzip.GzipFile(fileobj=output,mode='wb',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w') as archive:
            for path in sorted(Path(run_dir).rglob('*')):
                if path.is_symlink():raise ValueError('ordinary retained archive members required')
                if not path.is_file():continue
                raw=path.read_bytes();total+=len(raw)
                if total>512*1024**2:raise ValueError('bounded retained run archive exceeded')
                item=tarfile.TarInfo('run/'+path.relative_to(run_dir).as_posix());item.size=len(raw);item.mode=0o644;item.mtime=0;archive.addfile(item,io.BytesIO(raw))
    return output.getvalue()


def publish(output,*,run_dir,root=None):
    run_dir=Path(run_dir);verification=verify(run_dir,root=root);result=json.loads((run_dir/'result.json').read_bytes());request=json.loads((run_dir/'request.json').read_bytes());output=Path(output)
    # A public packet is also immutable: use a fresh staging directory when refreshing.
    output.mkdir(parents=True,exist_ok=False)
    write(output/'study.json',result);write(output/'verification.json',verification)
    from engineering.design_search.storage import atomic_immutable
    atomic_immutable(output/'artifacts.tar.gz',_archive(run_dir))
    rows=['# Finite 3D magnetic continuation confirmation','',
        'This separate numerical study uses the unchanged finite 1 m N35UH Halbach coupon at 80°C and zero current. It preserves the physical source and isotropic 50 Hz steel proxy while correcting the low-field Newton tangent and ramping the PM source through ten warm-started load stages. The historical failed Newton and Picard attempts remain unchanged.','',
        '**No complete force map, stable hover, integrated candidate selection or physical material acceptance is established.** Complete λ = 1 convergence is necessary for sampled force credit; mesh, domain, air-contour and local demagnetisation uncertainty remain separate.','',
        '[Retained results](study.json) · [Independent read-back checks](verification.json) · [Exact inputs, mesh and logs](artifacts.tar.gz)','',
        '| Case | Numerical disposition | Full-source converged | Fz contours 1 / 2, N | Demag proxy margin, A/m |','|---|---|---|---|---|']
    for row in result['rows']:
        data=row.get('analysis',{});forces=data.get('air_contour_results',[]);force=' / '.join(f'{v["force_N"][2]:.6g}' for v in forces) if forces else 'unevaluated';margin=f'{data["demag_proxy_margin_A_per_m"]:.6g}' if 'demag_proxy_margin_A_per_m'in data else 'unevaluated';rows.append(f"| {row['case']} | {row['execution_status']} | {row.get('full_source_converged',False)} | {force} | {margin} |")
    rows+=['','## Numerical and physical scope','',
        'Each case has a 300-second complete worker deadline. Cases execute sequentially. The fine mesh changes the near/gap sizes at the same air boundary; the expanded case changes the air boundary with the fine local sizes. Domain refinement also changes the realised mesh and cannot isolate boundary error exactly. Two nested air contours integrate the Maxwell traction and moments about the source origin. The result JSON retains full vector/moment changes and symmetry residuals; no arbitrary acceptance threshold converts these diagnostics into a qualified map.','',
        'The low-field branch keeps exactly the original B(H) regularisation: below 1e-6 A/m its permeability is constant mu0 + 0.0025, so its derivative is that scalar times the identity. Componentwise central differences check the new tangent. This verifies differentiation, not the retained digitised 50 Hz steel curve as a measured DC/reversible law.','',
        'The PM demagnetisation screen uses element-centroid Hparallel and 80% of the temperature-adjusted minimum Hcj. It is neither a measured knee nor an irreversible-demagnetisation model; local peak convergence, steel temperature effects, finite guideway ends, real magnet joints, currents, motion/losses and repeated thermal duty remain unresolved.','',
        f"Vehicle source identity: `{result['candidate_id']}`. Magnetic component identity: `{result['magnet_component_id']}`. Source request: `{result['request_id']}`.",'',
        'Reproduce with `python -m engineering.magnetic_confirmation run --root <repository> --output <fresh-directory> --getdp <getdp-executable> --reuse-mesh-root <verified-original-mesh-directory>`. Verify with `python -m engineering.magnetic_confirmation verify --root <repository> --output <run-directory>`. Mesh reuse is optional and grants no previous solve credit.','']
    atomic_immutable(output/'README.md','\n'.join(rows).encode())
    manifest=dict(schema=SCHEMA,request_id=request['request_id'],source_sha256=request['source_sha256'],files_sha256=inventory(output,exclude=('manifest.json',)),**FLAGS);write(output/'manifest.json',manifest);return manifest
