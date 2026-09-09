# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **125 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0278-0667-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | reverse | revenue | 3 | pending |
| line-1 | line-1-0489-0616-s006026 | forward | revenue | 3 | pending |
| line-1 | line-1-0489-0616-s006026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0583-s007706 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0583-s007706 | reverse | revenue | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | forward | revenue | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | reverse | revenue | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | forward | revenue | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | reverse | revenue | 3 | pending |
| line-1 | line-1-1072-0471-s019474 | reverse | revenue | 3 | pending |
| line-1 | line-1-0367-0647-s003022 | reverse | spare | 1 | pending |
| line-1 | line-1-0489-0616-s006026 | forward | spare | 1 | pending |
| line-1 | line-1-0489-0616-s006026 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0583-s007706 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0032-0601-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0246-0611-s007011 | forward | revenue | 3 | pending |
| line-2 | line-2-0246-0611-s007011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0341-0536-s010016 | forward | revenue | 3 | pending |
| line-2 | line-2-0341-0536-s010016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0469-0531-s013026 | forward | revenue | 3 | pending |
| line-2 | line-2-0469-0531-s013026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | forward | revenue | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | reverse | revenue | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | forward | revenue | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | reverse | revenue | 3 | pending |
| line-2 | line-2-0687-0442-s018881 | reverse | revenue | 3 | pending |
| line-2 | line-2-0246-0611-s007011 | forward | spare | 1 | pending |
| line-2 | line-2-0246-0611-s007011 | reverse | spare | 1 | pending |
| line-2 | line-2-0341-0536-s010016 | forward | spare | 1 | pending |
| line-2 | line-2-0341-0536-s010016 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0598-0069-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | reverse | revenue | 3 | pending |
| line-3 | line-3-0563-0480-s010044 | forward | revenue | 3 | pending |
| line-3 | line-3-0563-0480-s010044 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0583-s012336 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0583-s012336 | reverse | revenue | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | forward | revenue | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | reverse | revenue | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | forward | revenue | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | reverse | revenue | 3 | pending |
| line-3 | line-3-0404-0807-s019508 | reverse | revenue | 3 | pending |
| line-3 | line-3-0597-0344-s007019 | reverse | spare | 1 | pending |
| line-3 | line-3-0563-0480-s010044 | forward | spare | 1 | pending |
| line-3 | line-3-0563-0480-s010044 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0583-s012336 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**79 trainsets exceed the reference platform envelope**, requiring **4,700.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0278-0667-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0367-0647-s003022 | 8 | 2 | 6 | 357.0 |
| line-1-0489-0616-s006026 | 8 | 2 | 6 | 357.0 |
| line-1-0555-0583-s007706 | 7 | 4 | 3 | 178.5 |
| line-1-0603-0599-s009034 | 6 | 2 | 4 | 238.0 |
| line-1-0730-0541-s012054 | 6 | 2 | 4 | 238.0 |
| line-1-1072-0471-s019474 | 3 | 2 | 1 | 59.5 |
| line-2-0032-0601-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0246-0611-s007011 | 8 | 2 | 6 | 357.0 |
| line-2-0341-0536-s010016 | 8 | 2 | 6 | 357.0 |
| line-2-0469-0531-s013026 | 6 | 2 | 4 | 238.0 |
| line-2-0561-0517-s014982 | 6 | 2 | 4 | 238.0 |
| line-2-0636-0491-s016920 | 6 | 2 | 4 | 238.0 |
| line-2-0687-0442-s018881 | 3 | 2 | 1 | 59.5 |
| line-3-0404-0807-s019508 | 3 | 2 | 1 | 59.5 |
| line-3-0433-0712-s017123 | 6 | 2 | 4 | 238.0 |
| line-3-0503-0654-s014732 | 6 | 2 | 4 | 238.0 |
| line-3-0555-0583-s012336 | 7 | 4 | 3 | 178.5 |
| line-3-0563-0480-s010044 | 8 | 2 | 6 | 357.0 |
| line-3-0597-0344-s007019 | 8 | 2 | 6 | 357.0 |
| line-3-0598-0069-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Hillah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
