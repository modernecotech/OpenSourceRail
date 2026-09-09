# Continuous service-cycle stabling screen

Operating screen: **PASS** after **2 complete service days**. Physical/deployment release: **open**.

| After service day | Parked trains / stations | Largest queue | Outside selected stabling locations | Directions restarting within 60 s | Minimum night SoC | Beyond reference platform berths | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 108 / 20 | 18 | 0 | 34 / 34 | 24.2% | 63 | PASS |
| 2 | 108 / 20 | 19 | 0 | 34 / 34 | 22.2% | 63 | PASS |

## Trains outside selected stabling locations

| After service day | Train | Line | Station | Role | SoC |
|---|---|---|---|---|---:|

Minimum train SoC over the complete run: **20.010%**. Charging demand and delivered/grid energy are recorded per site in the JSON evidence.

- Starts at 95% train SoC once; trains, site storage and positions are not reset between days.
- Nominal scenario weather and existing grid/charging quantities are retained; degraded-weather and electrical acceptance remain separate.
- Starting each planned direction does not establish every revenue train is serviceable or daytime headways are delivered.
- Reference platform comparisons use observed parked allocations; physical tracks, access and charger connections remain unverified.
- Low-SoC trains outside selected stabling locations require charging/recovery and evening placement review; reserves do not substitute automatically.
- Movement-authority sweeps can report unknown positions for station-held trains outside the interstation occupancy model; counts are retained, not certified as complete station interlocking evidence.

Reproduce with:

```bash
.venv/bin/python tools/automation/screen-stabling-cycles.py --design 'cities/catalogue/west-asia/Iraq/Samawah/design.toml' --days 2
```

Evidence and hashes: [service-cycle-screen.json](service-cycle-screen.json). A failed screen exits with status 1; it does not promote the candidate or change canonical acceptance.
