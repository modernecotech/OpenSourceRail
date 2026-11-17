import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from engineering.outline import city_workflow

START = time.monotonic()
output = Path(__file__).resolve().parent / 'artifacts'
manifest = city_workflow.verify(output, root=ROOT, replay=True)
record = {
    'command': 'python3 build/v07-ethos/samawah-current-20261117-a/verify.py',
    'source_payload_and_exact_replay_verified': True,
    'manifest_id': manifest['manifest_id'],
    'evaluation_id': manifest['evaluation_id'],
    'wall_s': time.monotonic() - START,
    'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    'physical_accepted': False,
}
(output.parent / 'verification.json').write_text(json.dumps(record, sort_keys=True, indent=2)+'\n')
print(json.dumps(record, sort_keys=True))
