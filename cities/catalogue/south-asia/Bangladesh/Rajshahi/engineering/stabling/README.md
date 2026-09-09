# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **93 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0585-0779-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0545-0671-s003019 | forward | revenue | 5 | pending |
| line-1 | line-1-0545-0671-s003019 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0553-s005482 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0553-s005482 | reverse | revenue | 4 | pending |
| line-1 | line-1-0529-0397-s009065 | forward | revenue | 4 | pending |
| line-1 | line-1-0529-0397-s009065 | reverse | revenue | 4 | pending |
| line-1 | line-1-0540-0014-s017955 | reverse | revenue | 4 | pending |
| line-1 | line-1-0545-0671-s003019 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0553-s005482 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0553-s005482 | reverse | spare | 1 | pending |
| line-1 | line-1-0529-0397-s009065 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0579-0588-s003006 | forward | revenue | 2 | pending |
| line-2 | line-2-0579-0588-s003006 | reverse | revenue | 2 | pending |
| line-2 | line-2-0550-0553-s004252 | forward | revenue | 2 | pending |
| line-2 | line-2-0550-0553-s004252 | reverse | revenue | 2 | pending |
| line-2 | line-2-0490-0568-s006010 | forward | revenue | 2 | pending |
| line-2 | line-2-0490-0568-s006010 | reverse | revenue | 2 | pending |
| line-2 | line-2-0454-0620-s008178 | forward | revenue | 2 | pending |
| line-2 | line-2-0454-0620-s008178 | reverse | revenue | 2 | pending |
| line-2 | line-2-0372-0609-s010334 | reverse | revenue | 2 | pending |
| line-2 | line-2-0579-0588-s003006 | forward | spare | 1 | pending |
| line-2 | line-2-0579-0588-s003006 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0553-s004252 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0361-0575-s004856 | forward | revenue | 3 | pending |
| line-3 | line-3-0361-0575-s004856 | reverse | revenue | 3 | pending |
| line-3 | line-3-0480-0563-s007879 | forward | revenue | 3 | pending |
| line-3 | line-3-0480-0563-s007879 | reverse | revenue | 3 | pending |
| line-3 | line-3-0550-0553-s009770 | forward | revenue | 3 | pending |
| line-3 | line-3-0550-0553-s009770 | reverse | revenue | 3 | pending |
| line-3 | line-3-0567-0472-s011934 | forward | revenue | 3 | pending |
| line-3 | line-3-0567-0472-s011934 | reverse | revenue | 2 | pending |
| line-3 | line-3-0577-0391-s014089 | reverse | revenue | 2 | pending |
| line-3 | line-3-0567-0472-s011934 | reverse | spare | 1 | pending |
| line-3 | line-3-0577-0391-s014089 | reverse | spare | 1 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,915.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0529-0397-s009065 | 9 | 2 | 7 | 416.5 |
| line-1-0540-0014-s017955 | 4 | 2 | 2 | 119.0 |
| line-1-0545-0671-s003019 | 10 | 2 | 8 | 476.0 |
| line-1-0550-0553-s005482 | 10 | 4 | 6 | 357.0 |
| line-1-0585-0779-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0372-0609-s010334 | 2 | 2 | 0 | 0.0 |
| line-2-0454-0620-s008178 | 4 | 2 | 2 | 119.0 |
| line-2-0490-0568-s006010 | 4 | 4 | 0 | 0.0 |
| line-2-0550-0553-s004252 | 5 | 4 | 1 | 59.5 |
| line-2-0579-0588-s003006 | 6 | 2 | 4 | 238.0 |
| line-2-0616-0676-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0185-0604-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0361-0575-s004856 | 6 | 2 | 4 | 238.0 |
| line-3-0480-0563-s007879 | 6 | 4 | 2 | 119.0 |
| line-3-0550-0553-s009770 | 6 | 4 | 2 | 119.0 |
| line-3-0567-0472-s011934 | 6 | 2 | 4 | 238.0 |
| line-3-0577-0391-s014089 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rajshahi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
