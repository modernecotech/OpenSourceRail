# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **102 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0522-0784-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0656-s003018 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0656-s003018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0574-0595-s004635 | forward | revenue | 3 | pending |
| line-1 | line-1-0574-0595-s004635 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0555-s006277 | forward | revenue | 2 | pending |
| line-1 | line-1-0549-0555-s006277 | reverse | revenue | 2 | pending |
| line-1 | line-1-0545-0512-s007644 | forward | revenue | 2 | pending |
| line-1 | line-1-0545-0512-s007644 | reverse | revenue | 2 | pending |
| line-1 | line-1-0696-0354-s013231 | reverse | revenue | 2 | pending |
| line-1 | line-1-0549-0555-s006277 | forward | spare | 1 | pending |
| line-1 | line-1-0549-0555-s006277 | reverse | spare | 1 | pending |
| line-1 | line-1-0545-0512-s007644 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0427-s007013 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0427-s007013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0470-0513-s009087 | forward | revenue | 3 | pending |
| line-2 | line-2-0470-0513-s009087 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0555-s011169 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0555-s011169 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0608-s013122 | forward | revenue | 3 | pending |
| line-2 | line-2-0611-0608-s013122 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0697-s015059 | reverse | revenue | 2 | pending |
| line-2 | line-2-0626-0697-s015059 | reverse | spare | 1 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0456-0427-s007013 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0724-0466-s007007 | forward | revenue | 4 | pending |
| line-3 | line-3-0724-0466-s007007 | reverse | revenue | 4 | pending |
| line-3 | line-3-0613-0549-s010032 | forward | revenue | 4 | pending |
| line-3 | line-3-0613-0549-s010032 | reverse | revenue | 4 | pending |
| line-3 | line-3-0549-0555-s011849 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0555-s011849 | reverse | revenue | 4 | pending |
| line-3 | line-3-0492-0607-s013972 | forward | revenue | 4 | pending |
| line-3 | line-3-0492-0607-s013972 | reverse | revenue | 4 | pending |
| line-3 | line-3-0427-0681-s016119 | forward | revenue | 4 | pending |
| line-3 | line-3-0427-0681-s016119 | reverse | revenue | 4 | pending |
| line-3 | line-3-0129-0892-s024662 | reverse | revenue | 4 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0724-0466-s007007 | forward | spare | 1 | pending |
| line-3 | line-3-0724-0466-s007007 | reverse | spare | 1 | pending |
| line-3 | line-3-0613-0549-s010032 | forward | spare | 1 | pending |
| line-3 | line-3-0613-0549-s010032 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**69 trainsets exceed the reference platform envelope**, requiring **4,105.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0522-0784-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0545-0512-s007644 | 5 | 2 | 3 | 178.5 |
| line-1-0547-0656-s003018 | 6 | 2 | 4 | 238.0 |
| line-1-0549-0555-s006277 | 6 | 4 | 2 | 119.0 |
| line-1-0574-0595-s004635 | 6 | 2 | 4 | 238.0 |
| line-1-0696-0354-s013231 | 2 | 2 | 0 | 0.0 |
| line-2-0262-0243-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0456-0427-s007013 | 7 | 2 | 5 | 297.5 |
| line-2-0470-0513-s009087 | 6 | 2 | 4 | 238.0 |
| line-2-0549-0555-s011169 | 6 | 4 | 2 | 119.0 |
| line-2-0611-0608-s013122 | 6 | 2 | 4 | 238.0 |
| line-2-0626-0697-s015059 | 3 | 2 | 1 | 59.5 |
| line-3-0129-0892-s024662 | 4 | 2 | 2 | 119.0 |
| line-3-0427-0681-s016119 | 8 | 2 | 6 | 357.0 |
| line-3-0492-0607-s013972 | 8 | 2 | 6 | 357.0 |
| line-3-0549-0555-s011849 | 8 | 4 | 4 | 238.0 |
| line-3-0613-0549-s010032 | 10 | 2 | 8 | 476.0 |
| line-3-0724-0466-s007007 | 10 | 2 | 8 | 476.0 |
| line-3-0954-0263-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbarara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
