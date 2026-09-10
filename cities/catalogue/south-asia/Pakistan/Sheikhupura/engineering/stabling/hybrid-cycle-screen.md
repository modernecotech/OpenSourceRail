# Line-local station/depot service-cycle screen

Operating screen: **PASS** after 2 complete service days. Physical release remains open.

| Day | Station / depot trains | Correct homes | Capacity | Station launch directions within 60 s | Passenger departures after closing | Empty returns 02:30–05:30 | Depot revenue departures in first 30 min |
|---|---:|---|---|---:|---:|---:|---:|
| 1 | 18 / 19 | True | True | 14 / 14 | 0 | 0 | 6 |
| 2 | 18 / 19 | True | True | 14 / 14 | 0 | 0 | 6 |

Minimum train SoC across the run: 56.114%. Reserve departures: 0.

Exact misplaced train IDs, allocations, direction delays and source/raw-output hashes are in [hybrid-cycle-screen.json](hybrid-cycle-screen.json).

- Yard geometry and berthing remain abstract node operations.
- Reserve comparison allows 0.001 percentage point numerical tolerance, matching the city validator; the raw minimum is retained.
- Nominal energy inputs are retained; this does not close electrical or daytime headway acceptance.
- Empty returns may continue after passenger service closes; movements after 02:30 are reported.
- Depot departures during the first 30 minutes are reported, not required for all depot revenue stock.

```bash
.venv/bin/python tools/automation/screen-hybrid-stabling.py --design 'cities/catalogue/south-asia/Pakistan/Sheikhupura/design.toml' --days 2
```
