# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **109 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **98 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0781-0662-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0654-0606-s003004 | forward | revenue | 4 | pending |
| line-1 | line-1-0654-0606-s003004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0555-s005808 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0555-s005808 | reverse | revenue | 3 | pending |
| line-1 | line-1-0408-0552-s009496 | forward | revenue | 3 | pending |
| line-1 | line-1-0408-0552-s009496 | reverse | revenue | 3 | pending |
| line-1 | line-1-0292-0628-s013161 | reverse | revenue | 3 | pending |
| line-1 | line-1-0654-0606-s003004 | reverse | spare | 1 | pending |
| line-1 | line-1-0551-0555-s005808 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0555-s005808 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0399-0719-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0483-0638-s003012 | forward | revenue | 3 | pending |
| line-2 | line-2-0483-0638-s003012 | reverse | revenue | 3 | pending |
| line-2 | line-2-0527-0595-s004624 | forward | revenue | 3 | pending |
| line-2 | line-2-0527-0595-s004624 | reverse | revenue | 3 | pending |
| line-2 | line-2-0551-0555-s005829 | forward | revenue | 2 | pending |
| line-2 | line-2-0551-0555-s005829 | reverse | revenue | 2 | pending |
| line-2 | line-2-0550-0485-s007646 | forward | revenue | 2 | pending |
| line-2 | line-2-0550-0485-s007646 | reverse | revenue | 2 | pending |
| line-2 | line-2-0536-0322-s013191 | reverse | revenue | 2 | pending |
| line-2 | line-2-0551-0555-s005829 | forward | spare | 1 | pending |
| line-2 | line-2-0551-0555-s005829 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0485-s007646 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0467-0764-s004228 | forward | revenue | 4 | pending |
| line-3 | line-3-0467-0764-s004228 | reverse | revenue | 4 | pending |
| line-3 | line-3-0531-0648-s007232 | forward | revenue | 4 | pending |
| line-3 | line-3-0531-0648-s007232 | reverse | revenue | 4 | pending |
| line-3 | line-3-0551-0555-s009420 | forward | revenue | 4 | pending |
| line-3 | line-3-0551-0555-s009420 | reverse | revenue | 4 | pending |
| line-3 | line-3-0624-0526-s011320 | forward | revenue | 4 | pending |
| line-3 | line-3-0624-0526-s011320 | reverse | revenue | 4 | pending |
| line-3 | line-3-0694-0520-s013248 | forward | revenue | 4 | pending |
| line-3 | line-3-0694-0520-s013248 | reverse | revenue | 4 | pending |
| line-3 | line-3-1100-0131-s025287 | reverse | revenue | 3 | pending |
| line-3 | line-3-1100-0131-s025287 | reverse | spare | 1 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0764-s004228 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0764-s004228 | reverse | spare | 1 | pending |
| line-3 | line-3-0531-0648-s007232 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0292-0628-s013161 | 3 | 2 | 1 | 59.5 |
| line-1-0408-0552-s009496 | 6 | 2 | 4 | 238.0 |
| line-1-0551-0555-s005808 | 8 | 4 | 4 | 238.0 |
| line-1-0654-0606-s003004 | 8 | 2 | 6 | 357.0 |
| line-1-0781-0662-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0399-0719-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0483-0638-s003012 | 6 | 2 | 4 | 238.0 |
| line-2-0527-0595-s004624 | 6 | 2 | 4 | 238.0 |
| line-2-0536-0322-s013191 | 2 | 2 | 0 | 0.0 |
| line-2-0550-0485-s007646 | 5 | 2 | 3 | 178.5 |
| line-2-0551-0555-s005829 | 6 | 4 | 2 | 119.0 |
| line-3-0405-0945-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0467-0764-s004228 | 10 | 2 | 8 | 476.0 |
| line-3-0531-0648-s007232 | 9 | 2 | 7 | 416.5 |
| line-3-0551-0555-s009420 | 8 | 4 | 4 | 238.0 |
| line-3-0624-0526-s011320 | 8 | 2 | 6 | 357.0 |
| line-3-0694-0520-s013248 | 8 | 2 | 6 | 357.0 |
| line-3-1100-0131-s025287 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mansoura-Eg/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
