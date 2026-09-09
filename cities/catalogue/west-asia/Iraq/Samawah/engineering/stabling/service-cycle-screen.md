# Continuous service-cycle stabling screen

Operating screen: **FAIL** after **2 complete service days**. Physical/deployment release: **open**.

| After service day | Parked trains / stations | Largest queue | Outside selected stabling locations | Directions restarting within 60 s | Minimum night SoC | Beyond reference platform berths | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 108 / 21 | 20 | 6 | 34 / 34 | 21.3% | 63 | FAIL |
| 2 | 108 / 21 | 13 | 10 | 34 / 34 | 20.5% | 62 | FAIL |

## Trains outside selected stabling locations

| After service day | Train | Line | Station | Role | SoC |
|---|---|---|---|---|---:|
| 1 | T30 | line-1 | line-1-0814-0268-s019260 | revenue | 26.7% |
| 1 | T33 | line-1 | line-1-0814-0268-s019260 | revenue | 21.3% |
| 1 | T34 | line-1 | line-1-0814-0268-s019260 | revenue | 23.1% |
| 1 | T35 | line-1 | line-1-0814-0268-s019260 | revenue | 23.8% |
| 1 | T38 | line-1 | line-1-0814-0268-s019260 | revenue | 27.5% |
| 1 | T39 | line-1 | line-1-0814-0268-s019260 | revenue | 27.2% |
| 2 | T21 | line-1 | line-1-0814-0268-s019260 | revenue | 21.4% |
| 2 | T22 | line-1 | line-1-0814-0268-s019260 | revenue | 23.3% |
| 2 | T23 | line-1 | line-1-0814-0268-s019260 | revenue | 27.1% |
| 2 | T24 | line-1 | line-1-0814-0268-s019260 | revenue | 22.1% |
| 2 | T30 | line-1 | line-1-0814-0268-s019260 | revenue | 21.6% |
| 2 | T31 | line-1 | line-1-0814-0268-s019260 | revenue | 20.5% |
| 2 | T32 | line-1 | line-1-0814-0268-s019260 | revenue | 22.4% |
| 2 | T36 | line-1 | line-1-0814-0268-s019260 | revenue | 22.9% |
| 2 | T37 | line-1 | line-1-0814-0268-s019260 | revenue | 22.1% |
| 2 | T42 | line-1 | line-1-0814-0268-s019260 | revenue | 24.1% |

Minimum train SoC over the complete run: **20.009%**. Charging demand and delivered/grid energy are recorded per site in the JSON evidence.

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
