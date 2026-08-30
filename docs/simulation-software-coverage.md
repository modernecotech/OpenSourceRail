# Simulation software coverage

`osr-sim` executes connected software layers against the same run state:

- `onboard`: odometry, ATP/ATO, BMS, traction, brake, obstacle, fire,
  derailment, passenger assistance, and regenerative-current arbitration. The
  arbiter's refusal output is converted into friction effort;
- `vehicle_systems`: doors, auxiliary power, HVAC, lighting, and onboard PIS;
- `embedded`: TCMS, event recording, hot-axle monitoring, CBM sampling, and
  bounded T2G failover/store-and-forward. A TCMS trip inhibits dispatch or
  section progress on the next deterministic control cycle;
- `infrastructure_systems`: PSD, station PIS and SCADA per station, plus
  intrusion detection per wayside section and consensus verdict transitions;
- `habd_systems`: real trackside hot-axle evaluation at explicit bidirectional
  route-book locations, with next-station warning speed limits, latched stops,
  and inspected authority resets;
- `balise_systems`: a stable topology-derived passive-balise registry, real
  sighting audit, and accepted absolute fixes delivered to onboard odometry;
- `fare_systems`: signed single-ride issuance through the real TVM, gate
  validation, and back-office ledger/fraud reconciliation at every station;
- `occ_systems`: real TCMS-report ingestion into the OCC fleet roster; a
  critical train alarm opens a line incident and holds new dispatches until
  the line has recovered, without stopping a train already in a section;
- `proto_systems`: each live position report crosses the deterministic
  track-state codec; the decoded section, timestamp, speed and SoC feed OCC,
  and acceptance rejects decode loss or semantic drift;
- `energy_sites`: the standalone site controller governs every integer-watt
  PV/storage/grid/pad split; per-call conservation is checked in result data;
- `wayside_asset_systems`: every declared point machine executes against
  dual normal-position sensors and gates departures at its station; each
  declared level crossing runs the warning/barrier state machine and blocks
  its sections until closed. Zero crossings is an explicit not-applicable
  result for grade-separated networks;
- `backend_systems`: radio-delivered CBM ingestion, work-order generation,
  bounded history, and analytics over retained metrics;
- `time_sync`: the IEEE 1588 slave state machine acquires and retains the
  shared deterministic clock used by timestamped controller traffic.
- `selftest_systems`: all five deployment roles run their real software
  known-answer suites before service; a failure holds every dispatch.

Each layer emits deterministic result evidence. Auxiliary loads remain in the
calibrated energy intensity and are not charged twice.

Coverage is deliberately narrower than “start every binary.” The simulator
runs `osr-selftest` software checks, but physical wiring, sensor, relay and
trust-anchor commissioning remains external evidence. The
machine-readable contract at
`lib/simulation-component-coverage.toml` classifies every entry in
`deployment/components.toml` exactly once and fails if the inventory drifts.
`scenario_model` entries would identify aggregate substitutes (none remain in
the current inventory); `external_boundary` entries would remain explicit
gaps (none remain in the current inventory).

Nominal OCC acceptance requires positive controller, telemetry and roster
evidence with no incident or dispatch hold left active. A degraded integration
test drives a TCMS emergency through the same core and verifies hold/release.

The HABD scenario contract follows the ERA infrastructure-register model:
detector existence, location, and direction are explicit route assets. A trip
remains latched until an identified inspection reset because the RSSB operating
rule requires the train to stop and be examined before further movement. See
the [ERA RINF application guide](https://rinf.data.era.europa.eu/era-vocabulary/rinf-appGuide/)
and [RSSB Rule Book module TW5](https://consultations.rssb.co.uk/_entity/sharepointdocumentlocation/c6cba4e0-f8d9-ed11-a7c7-000d3aba3a5f/2ab10dab-d681-4911-b881-cc99413f07b6?file=07+GERT8000_TW5+post+consultation.pdf).

Balise identifiers and positions are regenerated from directed section IDs.
Nominal acceptance requires every crossing opportunity to produce a
registry-validated odometry fix; missed or mismatched reports remain visible
fault-injection outcomes and are never accepted as fixes.

The fare workload uses one representative transaction per station-minute to
exercise software deterministically. Sales, grants, and ledger entries must
reconcile, but the workload is not used as passenger-demand or revenue
forecast evidence. `fare_token_tamper` exercises cryptographic denial and
repeated-probe fraud signalling.

Run the inventory check with:

```bash
python3 tools/automation/validate-simulation-components.py
```

To verify tick evidence as well:

```bash
cargo run -p osr-sim --bin osr-sim -- \
  --config cities/catalogue/west-asia/Iraq/Samawah/samawah.toml \
  --duration 3600 --status-every 0 --json-out /tmp/osr-result.json
python3 tools/automation/validate-simulation-components.py --result /tmp/osr-result.json
```

City acceptance additionally hashes the rolling-stock template, buildable
trainset manifest, and small-component standard. A stale or inconsistent
`[consist.systems]` block therefore fails regeneration evidence.
