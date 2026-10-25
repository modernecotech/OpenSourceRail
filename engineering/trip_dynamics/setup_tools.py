"""Download exact solver bootstraps into an explicit private directory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tarfile
import urllib.request


def install(output):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    record = json.loads(Path(__file__).with_name('solver-environment.json').read_bytes())
    for key, filename, subfolder in [('getdp', 'getdp-3.5.0-Linux64c.tgz', ''),
                                     ('micromamba', 'micromamba-2.9.0-0.tar.bz2', 'micromamba')]:
        expected = record[key]; target = output/filename
        url = expected.get('reproduction_url', expected['url'])
        if not target.exists():
            request = urllib.request.Request(url, headers={'User-Agent':'OpenSourceRail-trip-toolchain/1'})
            temporary = target.with_suffix(target.suffix+'.pending')
            try:
                with urllib.request.urlopen(request, timeout=30) as response, temporary.open('xb') as stream:
                    count = 0
                    while True:
                        chunk = response.read(1024*1024)
                        if not chunk: break
                        count += len(chunk)
                        if count > expected['bytes']:
                            raise ValueError('solver archive exceeds its pinned byte count')
                        stream.write(chunk)
                if temporary.stat().st_size != expected['bytes'] or sha256(temporary.read_bytes()).hexdigest() != expected['sha256']:
                    raise ValueError('solver archive differs from its exact download pin')
                temporary.rename(target)
            finally:
                temporary.unlink(missing_ok=True)
        if target.is_symlink() or sha256(target.read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('existing private solver archive differs')
        destination = output/subfolder
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(target) as archive:
            archive.extractall(destination, filter='data')
    return dict(getdp=str(output/'getdp-3.5.0-Linux64/bin/getdp'),
                micromamba=str(output/'micromamba/bin/micromamba'), global_environment_modified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.output), indent=2))
