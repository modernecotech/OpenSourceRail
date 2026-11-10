# Replaying the Samawah comparison packet

The full packet is stored as a compressed archive to avoid keeping its 97 MB of
expanded JSON artifacts in the repository. It extracts to
`current-source-attempt-08/` and includes the root manifest, route-generation
record, four complete city-study records and all source-bound artifacts.

```sh
mkdir -p /tmp/osr-samawah-packet
tar -xzf current-source-attempt-08.tar.gz -C /tmp/osr-samawah-packet
```

From the extraction directory, verify all 83 files against the root manifest:

```sh
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path('/tmp/osr-samawah-packet/current-source-attempt-08')
manifest = json.loads((root / 'manifest.json').read_text())
assert manifest['file_count'] == 83
for relative, expected in manifest['files_sha256'].items():
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'hash mismatch: {relative}')
print(f"verified {manifest['file_count']} files; packet {manifest['manifest_id']}")
PY
```

This verifies artifact integrity. The recorded `replay_verified` fields describe
replay checks performed by the city-study workflow; exact cached study outputs
were reused during packet assembly. This archive does not claim that the four
city calculations were freshly recomputed during packaging.
