# Simulation software coverage

`osr-sim` now executes the motion/safety stack and the buildable trainset's
door, auxiliary-power, HVAC, lighting, and onboard PIS controllers against the
same train state on every applicable tick. The result JSON contains separate
`onboard` and `vehicle_systems` evidence; auxiliary loads are already included
in the calibrated energy intensity and are not charged twice.

Coverage is deliberately narrower than “start every binary.” Back-office,
station, wayside, design-tool, and GUI processes need service-level harnesses,
not a fake vehicle tick. The machine-readable contract at
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
