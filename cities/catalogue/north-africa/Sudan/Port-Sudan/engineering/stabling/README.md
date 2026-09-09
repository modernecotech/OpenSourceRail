# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 15 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0362-0552-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0457-0581-s003006 | forward | revenue | 3 | pending |
| line-1 | line-1-0457-0581-s003006 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0550-s005560 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0550-s005560 | reverse | revenue | 3 | pending |
| line-1 | line-1-0646-0565-s007685 | forward | revenue | 3 | pending |
| line-1 | line-1-0646-0565-s007685 | reverse | revenue | 3 | pending |
| line-1 | line-1-0770-0523-s010586 | forward | revenue | 2 | pending |
| line-1 | line-1-0770-0523-s010586 | reverse | revenue | 2 | pending |
| line-1 | line-1-0902-0530-s013478 | reverse | revenue | 2 | pending |
| line-1 | line-1-0770-0523-s010586 | forward | spare | 1 | pending |
| line-1 | line-1-0770-0523-s010586 | reverse | spare | 1 | pending |
| line-1 | line-1-0902-0530-s013478 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0443-0413-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0515-0479-s003009 | forward | revenue | 3 | pending |
| line-2 | line-2-0515-0479-s003009 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0550-s005256 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0550-s005256 | reverse | revenue | 3 | pending |
| line-2 | line-2-0627-0505-s007851 | forward | revenue | 3 | pending |
| line-2 | line-2-0627-0505-s007851 | reverse | revenue | 3 | pending |
| line-2 | line-2-0777-0508-s011295 | reverse | revenue | 2 | pending |
| line-2 | line-2-0777-0508-s011295 | reverse | spare | 1 | pending |
| line-2 | line-2-0443-0413-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0515-0479-s003009 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0489-0673-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0549-0550-s003425 | forward | revenue | 3 | pending |
| line-3 | line-3-0549-0550-s003425 | reverse | revenue | 3 | pending |
| line-3 | line-3-0617-0589-s005735 | forward | revenue | 3 | pending |
| line-3 | line-3-0617-0589-s005735 | reverse | revenue | 3 | pending |
| line-3 | line-3-0761-0556-s009113 | reverse | revenue | 3 | pending |
| line-3 | line-3-0489-0673-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0549-0550-s003425 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**38 trainsets exceed the reference platform envelope**, requiring **2,261.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0362-0552-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0457-0581-s003006 | 6 | 2 | 4 | 238.0 |
| line-1-0549-0550-s005560 | 6 | 4 | 2 | 119.0 |
| line-1-0646-0565-s007685 | 6 | 2 | 4 | 238.0 |
| line-1-0770-0523-s010586 | 6 | 4 | 2 | 119.0 |
| line-1-0902-0530-s013478 | 3 | 2 | 1 | 59.5 |
| line-2-0443-0413-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0515-0479-s003009 | 7 | 2 | 5 | 297.5 |
| line-2-0549-0550-s005256 | 6 | 4 | 2 | 119.0 |
| line-2-0627-0505-s007851 | 6 | 2 | 4 | 238.0 |
| line-2-0777-0508-s011295 | 3 | 2 | 1 | 59.5 |
| line-3-0489-0673-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0549-0550-s003425 | 7 | 4 | 3 | 178.5 |
| line-3-0617-0589-s005735 | 6 | 2 | 4 | 238.0 |
| line-3-0761-0556-s009113 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Port-Sudan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
