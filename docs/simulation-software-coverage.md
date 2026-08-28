# Simulation software coverage

`osr-sim` executes four connected layers against the same run state:

- `onboard`: odometry, ATP/ATO, BMS, traction, brake, obstacle, fire,
  derailment, and passenger assistance;
- `vehicle_systems`: doors, auxiliary power, HVAC, lighting, and onboard PIS;
- `embedded`: TCMS, event recording, hot-axle monitoring, CBM sampling, and
  T2G failover/store-and-forward;
- `infrastructure_systems`: PSD, station PIS and SCADA per station, plus
  intrusion detection per wayside section and consensus verdict transitions.

Each layer emits deterministic result evidence. Auxiliary loads remain in the
calibrated energy intensity and are not charged twice.

Coverage is deliberately narrower than “start every binary.” Hardware
commissioning remains in `osr-selftest`; back-office, unconfigured asset
controllers, and design processes need their own harnesses. The
machine-readable contract at
`lib/simulation-component-coverage.toml` classifies every entry in
`deployment/components.toml` exactly once and fails if the inventory drifts.
`scenario_model` entries are aggregate substitutes; `external_boundary`
entries remain explicit gaps.

Run the inventory check with:

```bash
python3 scripts/validate-simulation-components.py
```

To verify tick evidence as well:

```bash
cargo run -p osr-sim --bin osr-sim -- \
  --config designs/west-asia/Iraq/Samawah/samawah.toml \
  --duration 3600 --status-every 0 --json-out /tmp/osr-result.json
python3 scripts/validate-simulation-components.py --result /tmp/osr-result.json
```

City acceptance additionally hashes the rolling-stock template, buildable
trainset manifest, and small-component standard. A stale or inconsistent
`[consist.systems]` block therefore fails regeneration evidence.
