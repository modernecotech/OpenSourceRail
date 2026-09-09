# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **108 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **97 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

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
