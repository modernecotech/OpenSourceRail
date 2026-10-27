#!/usr/bin/env python3
"""Two bounded moving-component controls, never an operating force-map run."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.design_search import design_grammar, railway_bundle, moving_lim
from engineering.station_rail.common import encoded, identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Fresh control run directory required')
    args.output.mkdir(parents=True)
    body = design_grammar.initial_candidates()[0]
    bundle = railway_bundle.materialize(body)
    rows = []
    for name, voltage in [('zero-voltage', 0.), ('finite-entry', 2.)]:
        request = moving_lim.request(bundle, voltage_peak_V=voltage, steps=8, dt_s=.002, mesh_m=.04)
        result = moving_lim.run(request, args.output / name)
        moving_lim.verify(args.output / name)
        rows.append(dict(name=name, request_id=request['request_id'], result=result))
    zero = rows[0]['result']
    zero_rows = zero.get('trace', [])
    zero_fields = ('thrust_N','normal_force_N','magnetic_energy_J','secondary_Joule_W','primary_copper_W')
    zero_control = bool(zero_rows) and all(abs(row[field]) <= 1e-10 for row in zero_rows for field in zero_fields)
    zero_control = zero_control and all(abs(i) <= 1e-10 for row in zero_rows for i in row['path_currents_A'])
    # Package execution/domain failures remain visible. These runs cannot waive
    # independent convergence, thermal, finite-height or high-speed obligations.
    report = dict(schema='osr-moving-component-controls/1', cases=rows, zero_excitation_control_passed=zero_control,
                  maximum_component_jobs=2, maximum_seconds_per_job=90, memory_bytes_per_job=2*1024**3,
                  operating_map_admitted=False, physical_accepted=False,
                  scope='Daily low-voltage and zero-excitation method controls only; no validated service capability')
    report['evaluation_id'] = identity(report)
    (args.output / 'summary.json').write_bytes(encoded(report))
    print(json.dumps(dict(evaluation_id=report['evaluation_id'], executions=[r['result']['execution'] for r in rows],
                          operating_map_admitted=False), sort_keys=True))
    return 0 if zero_control and all(r['result']['execution']=='completed' for r in rows) else 3


if __name__ == '__main__':
    raise SystemExit(main())
