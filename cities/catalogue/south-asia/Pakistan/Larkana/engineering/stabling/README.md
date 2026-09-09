# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **79 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **71 revenue, 6 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0944-0310-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0652-0430-s007008 | forward | revenue | 3 | pending |
| line-1 | line-1-0652-0430-s007008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0502-s009815 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0502-s009815 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0552-s011105 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0552-s011105 | reverse | revenue | 3 | pending |
| line-1 | line-1-0489-0555-s012815 | forward | revenue | 3 | pending |
| line-1 | line-1-0489-0555-s012815 | reverse | revenue | 3 | pending |
| line-1 | line-1-0420-0615-s015243 | forward | revenue | 3 | pending |
| line-1 | line-1-0420-0615-s015243 | reverse | revenue | 3 | pending |
| line-1 | line-1-0323-0675-s017680 | forward | revenue | 3 | pending |
| line-1 | line-1-0323-0675-s017680 | reverse | revenue | 3 | pending |
| line-1 | line-1-0223-0854-s022548 | reverse | revenue | 3 | pending |
| line-1 | line-1-0652-0430-s007008 | forward | spare | 1 | pending |
| line-1 | line-1-0652-0430-s007008 | reverse | spare | 1 | pending |
| line-1 | line-1-0545-0502-s009815 | forward | spare | 1 | pending |
| line-1 | line-1-0545-0502-s009815 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0552-s011105 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0599-0582-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0552-s001269 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0552-s001269 | reverse | revenue | 4 | pending |
| line-2 | line-2-0477-0525-s003012 | forward | revenue | 4 | pending |
| line-2 | line-2-0477-0525-s003012 | reverse | revenue | 3 | pending |
| line-2 | line-2-0386-0600-s006019 | forward | revenue | 3 | pending |
| line-2 | line-2-0386-0600-s006019 | reverse | revenue | 3 | pending |
| line-2 | line-2-0029-0740-s014417 | reverse | revenue | 3 | pending |
| line-2 | line-2-0477-0525-s003012 | reverse | spare | 1 | pending |
| line-2 | line-2-0386-0600-s006019 | forward | spare | 1 | pending |
| line-2 | line-2-0386-0600-s006019 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,915.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0223-0854-s022548 | 3 | 2 | 1 | 59.5 |
| line-1-0323-0675-s017680 | 6 | 2 | 4 | 238.0 |
| line-1-0420-0615-s015243 | 6 | 2 | 4 | 238.0 |
| line-1-0489-0555-s012815 | 6 | 2 | 4 | 238.0 |
| line-1-0545-0502-s009815 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0552-s011105 | 7 | 4 | 3 | 178.5 |
| line-1-0652-0430-s007008 | 8 | 2 | 6 | 357.0 |
| line-1-0944-0310-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0029-0740-s014417 | 3 | 2 | 1 | 59.5 |
| line-2-0386-0600-s006019 | 8 | 2 | 6 | 357.0 |
| line-2-0477-0525-s003012 | 8 | 2 | 6 | 357.0 |
| line-2-0548-0552-s001269 | 8 | 4 | 4 | 238.0 |
| line-2-0599-0582-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Larkana/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
