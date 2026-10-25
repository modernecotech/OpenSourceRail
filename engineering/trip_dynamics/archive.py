"""Read-only bounded verification of the retained nonlinear coupon attempts."""
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import tarfile


def verify_magnetic_archive(path, *, root=None):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32*1024**2:
        raise ValueError('bounded ordinary magnetic archive required')
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        if len(members) > 128 or len(set(names)) != len(names) or sum(m.size for m in members) > 64*1024**2:
            raise ValueError('magnetic archive exceeds its decoded/file budget')
        for m in members:
            p = PurePosixPath(m.name)
            if not m.isfile() or p.is_absolute() or '..' in p.parts or p.as_posix() != m.name or m.size > 32*1024**2:
                raise ValueError('ordinary relative archive members required')
        def raw(name):
            return archive.extractfile(name).read()
        value = json.loads(raw('magnetic-fixture-artifacts.json'))
        if value.get('schema') != 'osr-trip-magnetic-fixture-artifacts/1':
            raise ValueError('magnetic artifact receipt schema differs')
        expected = value['files_sha256']
        if set(names) != set(expected) | {'magnetic-fixture-artifacts.json', 'tools/getdp-download.json'}:
            raise ValueError('magnetic archive inventory differs')
        for name, digest in expected.items():
            if sha256(raw(name)).hexdigest() != digest:
                raise ValueError('magnetic archive member differs: '+name)
        if sha256(raw('tools/getdp-download.json')).hexdigest() != value['getdp_download_record_sha256']:
            raise ValueError('magnetic solver download record differs')
        if value.get('physical_accepted') is not False or value.get('force_map_generated') is not False:
            raise ValueError('unconverged archive cannot assert acceptance or a usable force map')
        fixture = Path(__file__).parent/'fixtures/magnetics'
        for name, digest in value['new_recipe_source_sha256'].items():
            if PurePosixPath(name).name != name or sha256((fixture/name).read_bytes()).hexdigest() != digest:
                raise ValueError('current coupon recipe differs: '+name)
        finite = value['finite_candidate']
        if finite.get('force_map_generated') is not False or any(a.get('force_credit') is not False for a in finite['attempts']):
            raise ValueError('failed finite coupon acquired force credit')
        if root is not None:
            root = Path(root).resolve()
            for name, digest in finite['source_sha256'].items():
                p = root/name
                if not p.resolve().is_relative_to(root) or p.is_symlink() or sha256(p.read_bytes()).hexdigest() != digest:
                    raise ValueError('finite coupon input no longer matches published candidate')
        from .fixtures.magnetics.finite_coupon import formulation
        recorded = json.loads(raw('finite-coupon3d-v2/receipt.json'))
        for method, count, folder in [('newton', 60, 'coarse'), ('picard', 80, 'coarse-picard')]:
            replay = formulation(recorded['source']['value'], recorded['rows'][0]['mesh'],
                                 recorded['contours_m'], method=method, max_iterations=count)
            if replay.encode() != raw('finite-coupon3d-v2/'+folder+'/coupon.pro'):
                raise ValueError('retained solver input differs from its explicit replay recipe')
    return dict(schema='osr-magnetic-archive-verification/1', archive_sha256=sha256(path.read_bytes()).hexdigest(),
                files=len(members), decoded_bytes=sum(m.size for m in members),
                member_hashes_current=True, replayed_solver_inputs=True,
                manufactured_method_pass=value['manufactured_fixture']['passed'],
                finite_candidate=finite, historical_limitations=value['setup_failure'],
                physical_accepted=False, force_map_generated=False)
