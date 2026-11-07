"""Explicit numerical replay runtimes, separate from native physical solves.

Different NumPy/LAPACK builds can change determinant rounding and therefore an
exact nodal-load identity. Replay uses the declared interpreter; no old receipt
or force value is rewritten to hide that difference.
"""
from pathlib import Path
import json,os,subprocess,sys

SOURCE='engineering/design_search/craft_backends/viaduct_replay.py'
ROOT=Path(__file__).resolve().parents[3]

WORKER=r'''
import hashlib,json,os,platform,subprocess,sys
from pathlib import Path
import numpy as np
from numpy._core import _multiarray_umath
from numpy.linalg import _umath_linalg
def context():
    paths={'python':Path(sys.executable).resolve(),'numpy_module':Path(np.__file__).resolve(),
        'numpy_core':Path(_multiarray_umath.__file__).resolve(),'numpy_linalg':Path(_umath_linalg.__file__).resolve()}
    for module in ('numpy_core','numpy_linalg'):
        text=subprocess.check_output(['/usr/bin/ldd',str(paths[module])],text=True)
        for line in text.splitlines():
            if ' => ' not in line:continue
            path=line.split(' => ',1)[1].split()[0]
            if path.startswith('/') and Path(path).is_file():paths['dependency/'+Path(path).name]=Path(path).resolve()
    def sha(path):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        return h.hexdigest()
    return dict(python=platform.python_version(),numpy=np.__version__,
        interpreter_entrypoint=str(Path(sys.executable).absolute()),interpreter_prefix=sys.prefix,
        artifacts={k:dict(path=str(p),sha256=sha(p)) for k,p in sorted(paths.items())},
        thread_environment={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS')},
        OS_sandbox_enforced=False,scope='Read-only replay task and file hashes; not an OS-enforced filesystem sandbox')
before=context();operation=sys.argv[1]
if operation=='observe':result=None
else:
    folder=Path(sys.argv[2]);spec=json.loads((folder/'input.json').read_bytes())
    if operation=='analysis':
        from engineering.design_search.craft_backends import viaduct_fem as f
    elif operation=='resource':
        from engineering.design_search.craft_backends import viaduct_fem_resource as f
    else:raise ValueError('Known read-only replay operation required')
    result=f.verify(folder,spec)
if before!=context():raise ValueError('Replay numerical libraries changed during verification')
print(json.dumps(dict(runtime=before,verification=result,operation=operation,fresh_native_solve=False),sort_keys=True))
'''


def invoke(operation='observe',folder=None,*,python=None,root=ROOT):
    # Keep the entrypoint: resolving a venv symlink would silently select the
    # system site-packages even when the interpreter binary is identical.
    executable=Path(sys.executable if python is None else python).absolute()
    allowed={Path(sys.executable).absolute(),Path('/usr/bin/python3').absolute()}
    if executable not in allowed or operation not in ('observe','analysis','resource'):
        raise ValueError('Explicit supported numerical replay runtime and operation required')
    args=[str(executable),'-c',WORKER,operation]
    if folder is not None:args.append(str(Path(folder).resolve()))
    env={**os.environ,'PYTHONPATH':str(Path(root).resolve()),'OPENBLAS_NUM_THREADS':'1',
        'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','RAYON_NUM_THREADS':'1'}
    value=subprocess.run(args,cwd=root,env=env,text=True,capture_output=True,timeout=120)
    if value.returncode:
        raise ValueError('Strict numerical replay failed: '+value.stderr[-5000:])
    return json.loads(value.stdout)
