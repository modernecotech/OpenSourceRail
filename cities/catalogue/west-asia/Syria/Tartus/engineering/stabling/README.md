# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **60 trainsets at 13 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **53 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0690-0486-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0512-0433-s004413 | forward | revenue | 3 | pending |
| line-1 | line-1-0512-0433-s004413 | reverse | revenue | 3 | pending |
| line-1 | line-1-0418-0412-s006467 | forward | revenue | 3 | pending |
| line-1 | line-1-0418-0412-s006467 | reverse | revenue | 3 | pending |
| line-1 | line-1-0378-0379-s008522 | forward | revenue | 3 | pending |
| line-1 | line-1-0378-0379-s008522 | reverse | revenue | 3 | pending |
| line-1 | line-1-0257-0324-s012179 | reverse | revenue | 2 | pending |
| line-1 | line-1-0257-0324-s012179 | reverse | spare | 1 | pending |
| line-1 | line-1-0690-0486-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0512-0433-s004413 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0506-0606-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0485-0487-s003009 | forward | revenue | 3 | pending |
| line-2 | line-2-0485-0487-s003009 | reverse | revenue | 3 | pending |
| line-2 | line-2-0368-0447-s006014 | forward | revenue | 2 | pending |
| line-2 | line-2-0368-0447-s006014 | reverse | revenue | 2 | pending |
| line-2 | line-2-0378-0379-s008154 | forward | revenue | 2 | pending |
| line-2 | line-2-0378-0379-s008154 | reverse | revenue | 2 | pending |
| line-2 | line-2-0297-0414-s010664 | reverse | revenue | 2 | pending |
| line-2 | line-2-0368-0447-s006014 | forward | spare | 1 | pending |
| line-2 | line-2-0368-0447-s006014 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0271-0453-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0378-0379-s003423 | forward | revenue | 3 | pending |
| line-3 | line-3-0378-0379-s003423 | reverse | revenue | 3 | pending |
| line-3 | line-3-0428-0348-s004984 | reverse | revenue | 2 | pending |
| line-3 | line-3-0428-0348-s004984 | reverse | spare | 1 | pending |
| line-3 | line-3-0271-0453-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,372.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0257-0324-s012179 | 3 | 2 | 1 | 49.0 |
| line-1-0378-0379-s008522 | 6 | 4 | 2 | 98.0 |
| line-1-0418-0412-s006467 | 6 | 2 | 4 | 196.0 |
| line-1-0512-0433-s004413 | 7 | 2 | 5 | 245.0 |
| line-1-0690-0486-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0297-0414-s010664 | 2 | 2 | 0 | 0.0 |
| line-2-0368-0447-s006014 | 6 | 2 | 4 | 196.0 |
| line-2-0378-0379-s008154 | 4 | 4 | 0 | 0.0 |
| line-2-0485-0487-s003009 | 6 | 2 | 4 | 196.0 |
| line-2-0506-0606-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0271-0453-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0378-0379-s003423 | 6 | 4 | 2 | 98.0 |
| line-3-0428-0348-s004984 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Tartus/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
