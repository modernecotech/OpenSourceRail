# Simulation software coverage

`osr-sim` executes three connected layers against the same train state:

- `onboard`: odometry, ATP/ATO, BMS, traction, brake, obstacle, fire,
  derailment, and passenger assistance;
- `vehicle_systems`: doors, auxiliary power, HVAC, lighting, and onboard PIS;
- `embedded`: TCMS, event recording, hot-axle monitoring, CBM sampling, and
  T2G failover/store-and-forward.

Each layer emits deterministic result evidence. Auxiliary loads remain in the
calibrated energy intensity and are not charged twice.

Coverage is deliberately narrower than “start every binary.” Hardware
commissioning remains in `osr-selftest`; back-office, station, wayside, and
design processes need their own harnesses rather than a fake train tick. The
machine-readable contract at
`lib/simulation-component-coverage.toml` classifies every entry in
`deployment/components.toml` exactly once and fails if the inventory drifts.
`scenario_model` entries are aggregate substitutes, and `external_boundary`
entries remain explicit integration gaps rather than being reported as run.

Run the inventory check with:

```bash
python3 scripts/validate-simulation-components.py
```

To verify tick evidence as well:

```bash
cargo run -p osr-sim -- --config designs/west-asia/Iraq/Samawah/samawah.toml \
  --duration 3600 --status-every 0 --json-out /tmp/osr-result.json
python3 scripts/validate-simulation-components.py --result /tmp/osr-result.json
```

City acceptance additionally hashes the rolling-stock template, buildable
trainset manifest, and small-component standard. A stale or inconsistent
`[consist.systems]` block therefore fails regeneration evidence.
