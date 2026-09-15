#!/usr/bin/env python3
"""Station pilot driven by the existing Rust energy evaluator and explicit sensor fixtures."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.embedded import energy_measurements
from osr_integration.server import request_json


def main():
    config = json.loads((ROOT / 'var/supervision/integration.json').read_text())
    p = next(p for p in config['principals'] if p['role'] == 'controller' and p['subject'] == 'simulator')
    headers = {'Authorization': 'Bearer ' + p['token']}
    url = 'http://127.0.0.1:8092'
    binary = ROOT / 'target/debug/examples/supervision'
    lighting = {}
    while True:
        try:
            controls = ROOT / 'var/supervision/simulator-control.json'
            control = json.loads(controls.read_text()) if controls.exists() else {}
            # Communication-loss fixture: stop sending values without pretending healthy.
            if control.get('disconnected'):
                time.sleep(2); continue
            frame = json.loads(subprocess.check_output([str(binary)], text=True))
            values = energy_measurements(frame)
            now = time.time(); seq = time.time_ns()
            for city in p['cities']:
                snapshot = request_json(url + f'/snapshot?city={city}&environment=simulation', headers=headers)
                for a in snapshot['assets']:
                    for name, m in a['measurements'].items():
                        kind = a['equipment_type']
                        defaults = {'temperature_c': 35, 'energy_kwh': 1200, 'running_hours': 40, 'lighting_pct': lighting.get(a['asset_id'], 80), 'pump_running': 0}
                        value = values.get((kind, name), defaults.get(name, 0))
                        if kind == 'charger' and name == 'temperature_c' and control.get('cooling_fault'):
                            value = 82
                        message = dict(city=city, environment='simulation', asset_id=a['asset_id'], measurement=name, source_id='simulator',
                                       sequence=seq, source_timestamp=datetime.fromtimestamp(now, timezone.utc).isoformat(), unit=m['unit'], quality='valid', value=value)
                        request_json(url + '/telemetry', message, headers)
            for command in request_json(url + '/controller/commands', headers=headers):
                # Controller owns final bounds, local-enable checks and measured result.
                level = command.get('parameters', {}).get('level')
                valid = command['command'] == 'set_lighting' and isinstance(level, (int, float)) and 20 <= level <= 100 and not control.get('local_remote_disabled')
                request_json(url + '/controller/result', dict(request_id=command['request_id'], state='accepted' if valid else 'rejected', result='Simulator local limits and remote enable checked'), headers)
                if valid:
                    lighting[command['asset_id']] = level
                    request_json(url + '/controller/result', dict(request_id=command['request_id'], state='completed', result=f'Simulated lighting feedback {level}%'), headers)
        except Exception as exc:
            print('Simulation gateway waiting:', type(exc).__name__, flush=True)
        time.sleep(2)


if __name__ == '__main__': main()
