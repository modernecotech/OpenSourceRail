# Overnight operating comparison

Operating screen: **PASS**. Physical/deployment release: **open**.

| Case | Parked trainsets / stations at 05:29 | Largest station queue | 02:30–05:30 departures | All occupied stations restart within 60 s | Planned directions starting within 60 s | Reserve departures | Invariant violations |
|---|---:|---:|---:|---|---:|---:|---:|
| retained_endpoints | 108 / 6 | 27 | 4 | True | 6 / 6 | 0 | 0 |
| distributed_stations | 108 / 20 | 8 | 0 | True | 34 / 34 | 0 | 0 |

## Planned direction departures

| Line | Station | Direction | Ready revenue trains at 05:29 | First departure delay s | Result |
|---|---|---|---:|---:|---|
| line-1 | line-1-0147-0558-s000000 | forward | 4 | 0 | PASS |
| line-1 | line-1-0274-0515-s003012 | forward | 4 | 0 | PASS |
| line-1 | line-1-0274-0515-s003012 | reverse | 4 | 0 | PASS |
| line-1 | line-1-0351-0524-s004627 | forward | 4 | 0 | PASS |
| line-1 | line-1-0351-0524-s004627 | reverse | 4 | 0 | PASS |
| line-1 | line-1-0436-0475-s007631 | forward | 4 | 0 | PASS |
| line-1 | line-1-0436-0475-s007631 | reverse | 3 | 0 | PASS |
| line-1 | line-1-0493-0475-s009151 | forward | 3 | 0 | PASS |
| line-1 | line-1-0493-0475-s009151 | reverse | 3 | 0 | PASS |
| line-1 | line-1-0581-0418-s012247 | forward | 3 | 0 | PASS |
| line-1 | line-1-0581-0418-s012247 | reverse | 3 | 0 | PASS |
| line-1 | line-1-0704-0377-s015761 | forward | 3 | 0 | PASS |
| line-1 | line-1-0704-0377-s015761 | reverse | 3 | 0 | PASS |
| line-1 | line-1-0985-0109-s025566 | reverse | 3 | 0 | PASS |
| line-2 | line-2-0275-0378-s012812 | reverse | 2 | 0 | PASS |
| line-2 | line-2-0337-0443-s010631 | forward | 2 | 0 | PASS |
| line-2 | line-2-0337-0443-s010631 | reverse | 2 | 0 | PASS |
| line-2 | line-2-0400-0417-s008456 | forward | 2 | 0 | PASS |
| line-2 | line-2-0400-0417-s008456 | reverse | 2 | 0 | PASS |
| line-2 | line-2-0493-0475-s005930 | forward | 3 | 0 | PASS |
| line-2 | line-2-0493-0475-s005930 | reverse | 3 | 0 | PASS |
| line-2 | line-2-0604-0513-s003028 | forward | 3 | 0 | PASS |
| line-2 | line-2-0604-0513-s003028 | reverse | 3 | 0 | PASS |
| line-2 | line-2-0700-0586-s000000 | forward | 3 | 0 | PASS |
| line-3 | line-3-0455-0592-s003014 | forward | 3 | 0 | PASS |
| line-3 | line-3-0455-0592-s003014 | reverse | 3 | 0 | PASS |
| line-3 | line-3-0459-0690-s000000 | forward | 3 | 0 | PASS |
| line-3 | line-3-0471-0521-s004727 | forward | 3 | 0 | PASS |
| line-3 | line-3-0471-0521-s004727 | reverse | 2 | 0 | PASS |
| line-3 | line-3-0484-0261-s012046 | reverse | 2 | 0 | PASS |
| line-3 | line-3-0493-0352-s009079 | forward | 2 | 0 | PASS |
| line-3 | line-3-0493-0352-s009079 | reverse | 2 | 0 | PASS |
| line-3 | line-3-0493-0475-s006126 | forward | 2 | 0 | PASS |
| line-3 | line-3-0493-0475-s006126 | reverse | 2 | 0 | PASS |

- Both cases start at 95% train SoC at 01:30; this is not a full-day energy-sizing or degraded-weather acceptance run.
- CSV phase/location/SoC are used; its nominal charging-power column is not treated as metered delivery.
- Candidate spares and cold reserves are held out of routine service; activation, defect routing and maintenance release remain unmodelled.
- Station berths and crossovers remain abstract; physical track capacity, train health, maintenance routing and security are unverified.

Evidence and source hashes: [operating-screen.json](operating-screen.json). This is candidate evidence; the canonical city scenario and its acceptance results have not been replaced.
