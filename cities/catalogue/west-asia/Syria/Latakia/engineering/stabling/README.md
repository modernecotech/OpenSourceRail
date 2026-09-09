# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **93 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0693-0490-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0514-s003005 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0514-s003005 | reverse | revenue | 4 | pending |
| line-1 | line-1-0551-0553-s005665 | forward | revenue | 4 | pending |
| line-1 | line-1-0551-0553-s005665 | reverse | revenue | 4 | pending |
| line-1 | line-1-0537-0651-s009047 | forward | revenue | 3 | pending |
| line-1 | line-1-0537-0651-s009047 | reverse | revenue | 3 | pending |
| line-1 | line-1-0491-0817-s013635 | forward | revenue | 3 | pending |
| line-1 | line-1-0491-0817-s013635 | reverse | revenue | 3 | pending |
| line-1 | line-1-0371-0993-s018243 | reverse | revenue | 3 | pending |
| line-1 | line-1-0537-0651-s009047 | forward | spare | 1 | pending |
| line-1 | line-1-0537-0651-s009047 | reverse | spare | 1 | pending |
| line-1 | line-1-0491-0817-s013635 | forward | spare | 1 | pending |
| line-1 | line-1-0491-0817-s013635 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0452-0423-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0522-0520-s003004 | forward | revenue | 3 | pending |
| line-2 | line-2-0522-0520-s003004 | reverse | revenue | 3 | pending |
| line-2 | line-2-0551-0553-s004361 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0553-s004361 | reverse | revenue | 3 | pending |
| line-2 | line-2-0538-0601-s006016 | forward | revenue | 3 | pending |
| line-2 | line-2-0538-0601-s006016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0400-0736-s011465 | reverse | revenue | 2 | pending |
| line-2 | line-2-0400-0736-s011465 | reverse | spare | 1 | pending |
| line-2 | line-2-0452-0423-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0522-0520-s003004 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0682-0473-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0611-0492-s002060 | forward | revenue | 3 | pending |
| line-3 | line-3-0611-0492-s002060 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0553-s004130 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0553-s004130 | reverse | revenue | 3 | pending |
| line-3 | line-3-0499-0511-s006021 | forward | revenue | 2 | pending |
| line-3 | line-3-0499-0511-s006021 | reverse | revenue | 2 | pending |
| line-3 | line-3-0406-0435-s009581 | forward | revenue | 2 | pending |
| line-3 | line-3-0406-0435-s009581 | reverse | revenue | 2 | pending |
| line-3 | line-3-0301-0356-s013135 | reverse | revenue | 2 | pending |
| line-3 | line-3-0499-0511-s006021 | forward | spare | 1 | pending |
| line-3 | line-3-0499-0511-s006021 | reverse | spare | 1 | pending |
| line-3 | line-3-0406-0435-s009581 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,915.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0371-0993-s018243 | 3 | 2 | 1 | 59.5 |
| line-1-0491-0817-s013635 | 8 | 2 | 6 | 357.0 |
| line-1-0537-0651-s009047 | 8 | 2 | 6 | 357.0 |
| line-1-0551-0553-s005665 | 8 | 4 | 4 | 238.0 |
| line-1-0653-0514-s003005 | 8 | 2 | 6 | 357.0 |
| line-1-0693-0490-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0400-0736-s011465 | 3 | 2 | 1 | 59.5 |
| line-2-0452-0423-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0522-0520-s003004 | 7 | 4 | 3 | 178.5 |
| line-2-0538-0601-s006016 | 6 | 2 | 4 | 238.0 |
| line-2-0551-0553-s004361 | 6 | 4 | 2 | 119.0 |
| line-3-0301-0356-s013135 | 2 | 2 | 0 | 0.0 |
| line-3-0406-0435-s009581 | 5 | 2 | 3 | 178.5 |
| line-3-0499-0511-s006021 | 6 | 4 | 2 | 119.0 |
| line-3-0551-0553-s004130 | 6 | 4 | 2 | 119.0 |
| line-3-0611-0492-s002060 | 6 | 2 | 4 | 238.0 |
| line-3-0682-0473-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Latakia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
