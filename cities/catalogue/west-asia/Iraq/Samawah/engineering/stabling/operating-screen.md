# Overnight operating comparison

Operating screen: **PASS**. Physical/deployment release: **open**.

| Case | Parked trainsets / stations at 05:29 | Largest station queue | 02:30–05:30 departures | All occupied stations restart within 60 s | Invariant violations |
|---|---:|---:|---:|---|---:|
| retained_endpoints | 108 / 6 | 27 | 4 | True | 0 |
| distributed_stations | 108 / 20 | 8 | 0 | True | 0 |

- Both cases start at 95% train SoC at 01:30; this is not a full-day energy-sizing or degraded-weather acceptance run.
- CSV phase/location/SoC are used; its nominal charging-power column is not treated as metered delivery.
- Station berths and crossovers remain abstract; physical track capacity, train health, maintenance routing and security are unverified.

Evidence and source hashes: [operating-screen.json](operating-screen.json). This is candidate evidence; the canonical city scenario and its acceptance results have not been replaced.
