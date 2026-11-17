import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from engineering.performance import disk_reservation

HERE = Path(__file__).resolve().parent
COMMAND = [
    sys.executable, '-m', 'engineering.outline.city_worker',
    '--request', str(HERE / 'request.json'),
    '--output', str(HERE / 'artifacts'),
    '--root', str(ROOT),
]
START = time.monotonic()
MAX_RSS = 0
with disk_reservation(ROOT, HERE, 'samawah-current-city-replay', 128 * 1024**2):
    with (HERE / 'worker.log').open('wb') as log:
        process = subprocess.Popen(COMMAND, cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT,
                                   env={**os.environ, 'OMP_NUM_THREADS': '1',
                                        'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'})
        while process.poll() is None:
            stat = Path(f'/proc/{process.pid}/status')
            if stat.exists():
                for line in stat.read_text().splitlines():
                    if line.startswith('VmRSS:'):
                        MAX_RSS = max(MAX_RSS, int(line.split()[1]) * 1024)
                        break
            if MAX_RSS > 1024**3 or time.monotonic() - START > 180:
                process.kill()
                break
            time.sleep(.1)
        code = process.wait()
    artifact_bytes = sum(p.stat().st_size for p in (HERE / 'artifacts').rglob('*') if p.is_file()) if (HERE / 'artifacts').exists() else 0
    record = dict(command=COMMAND, exit_code=code, wall_s=time.monotonic()-START,
                  max_observed_rss_bytes=MAX_RSS, artifact_bytes=artifact_bytes,
                  limits=dict(wall_s=180, rss_bytes=1024**3, output_bytes=100*1024**2))
    (HERE / 'execution.json').write_text(json.dumps(record, sort_keys=True, indent=2)+'\n')
    print(json.dumps(record, sort_keys=True))
    if artifact_bytes > 100*1024**2:
        raise SystemExit('Output exceeded 100 MiB budget')
    raise SystemExit(code)
