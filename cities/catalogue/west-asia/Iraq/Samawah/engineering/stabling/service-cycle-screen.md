# Continuous service-cycle stabling screen

Operating screen: **FAIL** after **2 complete service days**. Physical/deployment release: **open**.

Holding/charging/restart behavior: **PASS**. Two-train station capacity: **FAIL**. A behavior pass does not override excess station occupancy.

| After service day | Parked trains / stations | Largest queue | Outside selected stabling locations | Directions restarting within 60 s | Minimum night SoC | Beyond reference platform berths | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 108 / 20 | 18 | 0 | 34 / 34 | 24.2% | 63 | FAIL |
| 2 | 108 / 20 | 19 | 0 | 34 / 34 | 22.2% | 63 | FAIL |

## Two-train station capacity

| Day | Station | Parked trainsets | Allowed | Excess |
|---|---|---:|---:|---:|
| 1 | line-1-0274-0515-s003012 | 3 | 2 | 1 |
| 1 | line-1-0351-0524-s004627 | 5 | 2 | 3 |
| 1 | line-1-0436-0475-s007631 | 3 | 2 | 1 |
| 1 | line-1-0493-0475-s009151 | 5 | 2 | 3 |
| 1 | line-1-0581-0418-s012247 | 7 | 2 | 5 |
| 1 | line-1-0704-0377-s015761 | 11 | 2 | 9 |
| 1 | line-1-0985-0109-s025566 | 18 | 2 | 16 |
| 1 | line-2-0275-0378-s012812 | 3 | 2 | 1 |
| 1 | line-2-0337-0443-s010631 | 4 | 2 | 2 |
| 1 | line-2-0400-0417-s008456 | 5 | 2 | 3 |
| 1 | line-2-0493-0475-s005930 | 6 | 2 | 4 |
| 1 | line-2-0604-0513-s003028 | 7 | 2 | 5 |
| 1 | line-2-0700-0586-s000000 | 3 | 2 | 1 |
| 1 | line-3-0455-0592-s003014 | 6 | 2 | 4 |
| 1 | line-3-0459-0690-s000000 | 3 | 2 | 1 |
| 1 | line-3-0471-0521-s004727 | 6 | 2 | 4 |
| 1 | line-3-0493-0352-s009079 | 4 | 2 | 2 |
| 1 | line-3-0493-0475-s006126 | 6 | 2 | 4 |
| 2 | line-1-0351-0524-s004627 | 3 | 2 | 1 |
| 2 | line-1-0436-0475-s007631 | 3 | 2 | 1 |
| 2 | line-1-0493-0475-s009151 | 4 | 2 | 2 |
| 2 | line-1-0581-0418-s012247 | 10 | 2 | 8 |
| 2 | line-1-0704-0377-s015761 | 11 | 2 | 9 |
| 2 | line-1-0985-0109-s025566 | 19 | 2 | 17 |
| 2 | line-2-0275-0378-s012812 | 3 | 2 | 1 |
| 2 | line-2-0337-0443-s010631 | 4 | 2 | 2 |
| 2 | line-2-0400-0417-s008456 | 6 | 2 | 4 |
| 2 | line-2-0493-0475-s005930 | 4 | 2 | 2 |
| 2 | line-2-0604-0513-s003028 | 8 | 2 | 6 |
| 2 | line-2-0700-0586-s000000 | 3 | 2 | 1 |
| 2 | line-3-0455-0592-s003014 | 6 | 2 | 4 |
| 2 | line-3-0459-0690-s000000 | 3 | 2 | 1 |
| 2 | line-3-0471-0521-s004727 | 6 | 2 | 4 |
| 2 | line-3-0493-0352-s009079 | 4 | 2 | 2 |
| 2 | line-3-0493-0475-s006126 | 6 | 2 | 4 |

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
