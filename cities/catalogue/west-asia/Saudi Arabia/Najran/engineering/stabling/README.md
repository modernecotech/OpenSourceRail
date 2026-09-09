# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **120 trainsets at 20 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **108 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0976-0042-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0939-0161-s003005 | forward | revenue | 3 | pending |
| line-1 | line-1-0939-0161-s003005 | reverse | revenue | 3 | pending |
| line-1 | line-1-0828-0332-s007603 | forward | revenue | 3 | pending |
| line-1 | line-1-0828-0332-s007603 | reverse | revenue | 3 | pending |
| line-1 | line-1-0773-0380-s009217 | forward | revenue | 3 | pending |
| line-1 | line-1-0773-0380-s009217 | reverse | revenue | 3 | pending |
| line-1 | line-1-0709-0472-s012226 | forward | revenue | 3 | pending |
| line-1 | line-1-0709-0472-s012226 | reverse | revenue | 3 | pending |
| line-1 | line-1-0605-0531-s015102 | forward | revenue | 3 | pending |
| line-1 | line-1-0605-0531-s015102 | reverse | revenue | 3 | pending |
| line-1 | line-1-0633-0647-s018258 | forward | revenue | 3 | pending |
| line-1 | line-1-0633-0647-s018258 | reverse | revenue | 3 | pending |
| line-1 | line-1-0619-0784-s021399 | reverse | revenue | 2 | pending |
| line-1 | line-1-0619-0784-s021399 | reverse | spare | 1 | pending |
| line-1 | line-1-0976-0042-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0939-0161-s003005 | forward | spare | 1 | pending |
| line-1 | line-1-0939-0161-s003005 | reverse | spare | 1 | pending |
| line-1 | line-1-0828-0332-s007603 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0617-0977-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0687-0838-s004487 | forward | revenue | 4 | pending |
| line-2 | line-2-0687-0838-s004487 | reverse | revenue | 4 | pending |
| line-2 | line-2-0700-0707-s007491 | forward | revenue | 4 | pending |
| line-2 | line-2-0700-0707-s007491 | reverse | revenue | 4 | pending |
| line-2 | line-2-0767-0585-s010498 | forward | revenue | 4 | pending |
| line-2 | line-2-0767-0585-s010498 | reverse | revenue | 4 | pending |
| line-2 | line-2-0834-0468-s013509 | forward | revenue | 4 | pending |
| line-2 | line-2-0834-0468-s013509 | reverse | revenue | 3 | pending |
| line-2 | line-2-1038-0227-s020031 | reverse | revenue | 3 | pending |
| line-2 | line-2-0834-0468-s013509 | reverse | spare | 1 | pending |
| line-2 | line-2-1038-0227-s020031 | reverse | spare | 1 | pending |
| line-2 | line-2-0617-0977-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0687-0838-s004487 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0961-0680-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0845-0596-s003016 | forward | revenue | 3 | pending |
| line-3 | line-3-0845-0596-s003016 | reverse | revenue | 3 | pending |
| line-3 | line-3-0715-0547-s006022 | forward | revenue | 3 | pending |
| line-3 | line-3-0715-0547-s006022 | reverse | revenue | 3 | pending |
| line-3 | line-3-0605-0531-s008489 | forward | revenue | 3 | pending |
| line-3 | line-3-0605-0531-s008489 | reverse | revenue | 3 | pending |
| line-3 | line-3-0487-0584-s012023 | forward | revenue | 3 | pending |
| line-3 | line-3-0487-0584-s012023 | reverse | revenue | 3 | pending |
| line-3 | line-3-0356-0613-s015276 | reverse | revenue | 2 | pending |
| line-3 | line-3-0356-0613-s015276 | reverse | spare | 1 | pending |
| line-3 | line-3-0961-0680-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0845-0596-s003016 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**76 trainsets exceed the reference platform envelope**, requiring **4,522.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0605-0531-s015102 | 6 | 4 | 2 | 119.0 |
| line-1-0619-0784-s021399 | 3 | 2 | 1 | 59.5 |
| line-1-0633-0647-s018258 | 6 | 2 | 4 | 238.0 |
| line-1-0709-0472-s012226 | 6 | 2 | 4 | 238.0 |
| line-1-0773-0380-s009217 | 6 | 2 | 4 | 238.0 |
| line-1-0828-0332-s007603 | 7 | 2 | 5 | 297.5 |
| line-1-0939-0161-s003005 | 8 | 2 | 6 | 357.0 |
| line-1-0976-0042-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0617-0977-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0687-0838-s004487 | 9 | 2 | 7 | 416.5 |
| line-2-0700-0707-s007491 | 8 | 2 | 6 | 357.0 |
| line-2-0767-0585-s010498 | 8 | 2 | 6 | 357.0 |
| line-2-0834-0468-s013509 | 8 | 2 | 6 | 357.0 |
| line-2-1038-0227-s020031 | 4 | 2 | 2 | 119.0 |
| line-3-0356-0613-s015276 | 3 | 2 | 1 | 59.5 |
| line-3-0487-0584-s012023 | 6 | 2 | 4 | 238.0 |
| line-3-0605-0531-s008489 | 6 | 4 | 2 | 119.0 |
| line-3-0715-0547-s006022 | 6 | 2 | 4 | 238.0 |
| line-3-0845-0596-s003016 | 7 | 2 | 5 | 297.5 |
| line-3-0961-0680-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Najran/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
