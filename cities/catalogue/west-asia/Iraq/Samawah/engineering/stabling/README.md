# Station and depot overnight allocation

Plan: **40 trainsets at stations + 68 at depots = 108 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0985-0109-s025566 | line-1 | declared-depot | 37 | 2,201.5 | 17 |
| line-2-0275-0378-s012812 | line-2 | storage-at-existing-powered-service-point | 16 | 952.0 | 0 |
| line-3-0484-0261-s012046 | line-3 | storage-at-existing-powered-service-point | 15 | 892.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0147-0558-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0274-0515-s003012 | station | forward | revenue | 1 |
| line-1 | line-1-0274-0515-s003012 | station | reverse | revenue | 1 |
| line-1 | line-1-0351-0524-s004627 | station | forward | revenue | 1 |
| line-1 | line-1-0351-0524-s004627 | station | reverse | revenue | 1 |
| line-1 | line-1-0436-0475-s007631 | station | forward | revenue | 1 |
| line-1 | line-1-0436-0475-s007631 | station | reverse | revenue | 1 |
| line-1 | line-1-0493-0475-s009151 | station | forward | revenue | 1 |
| line-1 | line-1-0493-0475-s009151 | station | reverse | revenue | 1 |
| line-1 | line-1-0581-0418-s012247 | station | forward | revenue | 1 |
| line-1 | line-1-0581-0418-s012247 | station | reverse | revenue | 1 |
| line-1 | line-1-0704-0377-s015761 | station | forward | revenue | 1 |
| line-1 | line-1-0704-0377-s015761 | station | reverse | revenue | 1 |
| line-1 | line-1-0985-0109-s025566 | station | reverse | revenue | 2 |
| line-2 | line-2-0275-0378-s012812 | station | reverse | revenue | 2 |
| line-2 | line-2-0337-0443-s010631 | station | forward | revenue | 1 |
| line-2 | line-2-0337-0443-s010631 | station | reverse | revenue | 1 |
| line-2 | line-2-0400-0417-s008456 | station | forward | revenue | 1 |
| line-2 | line-2-0400-0417-s008456 | station | reverse | revenue | 1 |
| line-2 | line-2-0493-0475-s005930 | station | forward | revenue | 1 |
| line-2 | line-2-0493-0475-s005930 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0513-s003028 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0513-s003028 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0586-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0455-0592-s003014 | station | forward | revenue | 1 |
| line-3 | line-3-0455-0592-s003014 | station | reverse | revenue | 1 |
| line-3 | line-3-0459-0690-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0471-0521-s004727 | station | forward | revenue | 1 |
| line-3 | line-3-0471-0521-s004727 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0261-s012046 | station | reverse | revenue | 2 |
| line-3 | line-3-0493-0352-s009079 | station | forward | revenue | 1 |
| line-3 | line-3-0493-0352-s009079 | station | reverse | revenue | 1 |
| line-3 | line-3-0493-0475-s006126 | station | forward | revenue | 1 |
| line-3 | line-3-0493-0475-s006126 | station | reverse | revenue | 1 |
| line-1 | line-1-0985-0109-s025566 | depot | — | revenue | 32 |
| line-1 | line-1-0985-0109-s025566 | depot | — | spare | 4 |
| line-1 | line-1-0985-0109-s025566 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0275-0378-s012812 | depot | — | revenue | 13 |
| line-2 | line-2-0275-0378-s012812 | depot | — | spare | 2 |
| line-2 | line-2-0275-0378-s012812 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0484-0261-s012046 | depot | — | revenue | 12 |
| line-3 | line-3-0484-0261-s012046 | depot | — | spare | 2 |
| line-3 | line-3-0484-0261-s012046 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/samawah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **108 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **97 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0147-0558-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0274-0515-s003012 | forward | revenue | 4 | pending |
| line-1 | line-1-0274-0515-s003012 | reverse | revenue | 4 | pending |
| line-1 | line-1-0351-0524-s004627 | forward | revenue | 4 | pending |
| line-1 | line-1-0351-0524-s004627 | reverse | revenue | 4 | pending |
| line-1 | line-1-0436-0475-s007631 | forward | revenue | 4 | pending |
| line-1 | line-1-0436-0475-s007631 | reverse | revenue | 3 | pending |
| line-1 | line-1-0493-0475-s009151 | forward | revenue | 3 | pending |
| line-1 | line-1-0493-0475-s009151 | reverse | revenue | 3 | pending |
| line-1 | line-1-0581-0418-s012247 | forward | revenue | 3 | pending |
| line-1 | line-1-0581-0418-s012247 | reverse | revenue | 3 | pending |
| line-1 | line-1-0704-0377-s015761 | forward | revenue | 3 | pending |
| line-1 | line-1-0704-0377-s015761 | reverse | revenue | 3 | pending |
| line-1 | line-1-0985-0109-s025566 | reverse | revenue | 3 | pending |
| line-1 | line-1-0436-0475-s007631 | reverse | spare | 1 | pending |
| line-1 | line-1-0493-0475-s009151 | forward | spare | 1 | pending |
| line-1 | line-1-0493-0475-s009151 | reverse | spare | 1 | pending |
| line-1 | line-1-0581-0418-s012247 | forward | spare | 1 | pending |
| line-1 | line-1-0581-0418-s012247 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0586-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0604-0513-s003028 | forward | revenue | 3 | pending |
| line-2 | line-2-0604-0513-s003028 | reverse | revenue | 3 | pending |
| line-2 | line-2-0493-0475-s005930 | forward | revenue | 3 | pending |
| line-2 | line-2-0493-0475-s005930 | reverse | revenue | 3 | pending |
| line-2 | line-2-0400-0417-s008456 | forward | revenue | 2 | pending |
| line-2 | line-2-0400-0417-s008456 | reverse | revenue | 2 | pending |
| line-2 | line-2-0337-0443-s010631 | forward | revenue | 2 | pending |
| line-2 | line-2-0337-0443-s010631 | reverse | revenue | 2 | pending |
| line-2 | line-2-0275-0378-s012812 | reverse | revenue | 2 | pending |
| line-2 | line-2-0400-0417-s008456 | forward | spare | 1 | pending |
| line-2 | line-2-0400-0417-s008456 | reverse | spare | 1 | pending |
| line-2 | line-2-0337-0443-s010631 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0459-0690-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0455-0592-s003014 | forward | revenue | 3 | pending |
| line-3 | line-3-0455-0592-s003014 | reverse | revenue | 3 | pending |
| line-3 | line-3-0471-0521-s004727 | forward | revenue | 3 | pending |
| line-3 | line-3-0471-0521-s004727 | reverse | revenue | 2 | pending |
| line-3 | line-3-0493-0475-s006126 | forward | revenue | 2 | pending |
| line-3 | line-3-0493-0475-s006126 | reverse | revenue | 2 | pending |
| line-3 | line-3-0493-0352-s009079 | forward | revenue | 2 | pending |
| line-3 | line-3-0493-0352-s009079 | reverse | revenue | 2 | pending |
| line-3 | line-3-0484-0261-s012046 | reverse | revenue | 2 | pending |
| line-3 | line-3-0471-0521-s004727 | reverse | spare | 1 | pending |
| line-3 | line-3-0493-0475-s006126 | forward | spare | 1 | pending |
| line-3 | line-3-0493-0475-s006126 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**62 trainsets exceed the reference platform envelope**, requiring **3,689.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0147-0558-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0274-0515-s003012 | 8 | 2 | 6 | 357.0 |
| line-1-0351-0524-s004627 | 8 | 2 | 6 | 357.0 |
| line-1-0436-0475-s007631 | 8 | 2 | 6 | 357.0 |
| line-1-0493-0475-s009151 | 8 | 4 | 4 | 238.0 |
| line-1-0581-0418-s012247 | 8 | 2 | 6 | 357.0 |
| line-1-0704-0377-s015761 | 6 | 2 | 4 | 238.0 |
| line-1-0985-0109-s025566 | 3 | 2 | 1 | 59.5 |
| line-2-0275-0378-s012812 | 2 | 2 | 0 | 0.0 |
| line-2-0337-0443-s010631 | 5 | 2 | 3 | 178.5 |
| line-2-0400-0417-s008456 | 6 | 2 | 4 | 238.0 |
| line-2-0493-0475-s005930 | 6 | 4 | 2 | 119.0 |
| line-2-0604-0513-s003028 | 6 | 2 | 4 | 238.0 |
| line-2-0700-0586-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0455-0592-s003014 | 6 | 2 | 4 | 238.0 |
| line-3-0459-0690-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0471-0521-s004727 | 6 | 2 | 4 | 238.0 |
| line-3-0484-0261-s012046 | 2 | 2 | 0 | 0.0 |
| line-3-0493-0352-s009079 | 4 | 2 | 2 | 119.0 |
| line-3-0493-0475-s006126 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
