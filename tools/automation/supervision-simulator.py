#!/usr/bin/env python3
"""City-scoped telemetry from native Rust station, vehicle and wayside evaluators."""
import json
from pathlib import Path
import select
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.embedded import operating_measurements
from osr_integration.server import request_json


class EmbeddedBridge:
    def __init__(self):
        self.process = subprocess.Popen([str(ROOT / 'target/debug/examples/operating_bridge')],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill(); self.process.wait()
        self.process.stdin.close(); self.process.stdout.close()

    def evaluate(self, key, lighting, controls):
        data = dict(key=key, now_ns=time.monotonic_ns(), lighting_pct=round(lighting))
        for name in ['station_fault','battery_trip','aux_fault','cbm_service',
                     'points_detection_fault','crossing_motor_fault','faregate_denial']:
            value = controls.get(name, False)
            if type(value) is not bool:
                raise ValueError('Boolean simulation fixture required')
            data[name] = value
        self.process.stdin.write(json.dumps(data) + '\n'); self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], 5)[0]:
            raise TimeoutError('Embedded bridge did not reply')
        frame = json.loads(self.process.stdout.readline())
        if frame.get('key') != key or 'error' in frame:
            raise ValueError('Embedded bridge rejected frame')
        return operating_measurements(frame)


def main():
    config = json.loads((ROOT / 'var/supervision/integration.json').read_text())
    p = next(p for p in config['principals'] if p['role'] == 'controller' and p['subject'] == 'simulator')
    headers = {'Authorization': 'Bearer ' + p['token']}
    url = 'http://127.0.0.1:8092'
    lighting, bridge = {}, EmbeddedBridge()
    try:
        while True:
            try:
                controls = ROOT / 'var/supervision/simulator-control.json'
                control = json.loads(controls.read_text()) if controls.exists() else {}
                if control.get('disconnected'):
                    time.sleep(2); continue
                snapshots = {}
                for city in p['cities']:
                    local = {**control, **control.get('cities', {}).get(city, {})}
                    if local.get('disconnected'): continue
                    snapshot = request_json(url + f'/snapshot?city={city}&environment=simulation', headers=headers)
                    snapshots[city] = snapshot
                    values_by_site = {}
                    for a in snapshot['assets']:
                        key = city + '|' + a['site_id']
                        if key not in values_by_site:
                            values_by_site[key] = bridge.evaluate(key, lighting.get(key, 80), local)
                        values = values_by_site[key]
                        for name, m in a['measurements'].items():
                            fixtures = {'temperature_c': 35, 'energy_kwh': 1200, 'running_hours': 40, 'pump_running': 0}
                            value = values.get((a['equipment_type'], name), fixtures.get(name))
                            if a['equipment_type'] == 'charger' and name == 'temperature_c' and local.get('cooling_fault'):
                                value = 82
                            message = dict(city=city, environment='simulation', asset_id=a['asset_id'], measurement=name,
                                source_id='simulator', sequence=time.time_ns(), source_timestamp=datetime.now(timezone.utc).isoformat(),
                                unit=m['unit'], quality='valid' if value is not None else 'invalid', value=value)
                            request_json(url + '/telemetry', message, headers)
                for command in request_json(url + '/controller/commands', headers=headers):
                    city = command['city']; local = {**control, **control.get('cities', {}).get(city, {})}
                    assets = snapshots.get(city, {}).get('assets', [])
                    asset = next((a for a in assets if a['asset_id'] == command['asset_id']), None)
                    level = command.get('parameters', {}).get('level')
                    valid = asset and asset['equipment_type'] == 'facilities' and command['command'] == 'set_lighting' and type(level) in (int, float) and 20 <= level <= 100 and not local.get('local_remote_disabled')
                    effective = None
                    if valid:
                        key = city + '|' + asset['site_id']
                        effective = bridge.evaluate(key, level, local)[('facilities','lighting_pct')]
                        valid = effective == level
                    request_json(url + '/controller/result', dict(request_id=command['request_id'], state='accepted' if valid else 'rejected', result='OSR station evaluator and simulator local-enable gate checked'), headers)
                    if valid:
                        lighting[key] = level
                        request_json(url + '/controller/result', dict(request_id=command['request_id'], state='completed', result=f'Simulated OSR station output {effective}%'), headers)
            except (BrokenPipeError, TimeoutError):
                bridge.close(); bridge = EmbeddedBridge()
                print('Embedded simulation process restarted; controller state reset', flush=True)
            except Exception as exc:
                print('Simulation gateway waiting:', type(exc).__name__, flush=True)
            time.sleep(2)
    finally:
        bridge.close()


if __name__ == '__main__': main()
