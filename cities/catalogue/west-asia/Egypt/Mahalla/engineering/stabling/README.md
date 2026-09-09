# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **75 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0700-0463-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0639-0491-s001601 | forward | revenue | 3 | pending |
| line-1 | line-1-0639-0491-s001601 | reverse | revenue | 3 | pending |
| line-1 | line-1-0556-0555-s004018 | forward | revenue | 3 | pending |
| line-1 | line-1-0556-0555-s004018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0564-0711-s007621 | forward | revenue | 3 | pending |
| line-1 | line-1-0564-0711-s007621 | reverse | revenue | 3 | pending |
| line-1 | line-1-0594-0921-s012269 | reverse | revenue | 3 | pending |
| line-1 | line-1-0700-0463-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0639-0491-s001601 | forward | spare | 1 | pending |
| line-1 | line-1-0639-0491-s001601 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1091-0156-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0747-0479-s010791 | forward | revenue | 5 | pending |
| line-2 | line-2-0747-0479-s010791 | reverse | revenue | 5 | pending |
| line-2 | line-2-0659-0592-s013803 | forward | revenue | 5 | pending |
| line-2 | line-2-0659-0592-s013803 | reverse | revenue | 5 | pending |
| line-2 | line-2-0610-0680-s016225 | forward | revenue | 4 | pending |
| line-2 | line-2-0610-0680-s016225 | reverse | revenue | 4 | pending |
| line-2 | line-2-0574-0783-s018642 | reverse | revenue | 4 | pending |
| line-2 | line-2-0610-0680-s016225 | forward | spare | 1 | pending |
| line-2 | line-2-0610-0680-s016225 | reverse | spare | 1 | pending |
| line-2 | line-2-0574-0783-s018642 | reverse | spare | 1 | pending |
| line-2 | line-2-1091-0156-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0647-0470-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0575-0506-s001894 | forward | revenue | 3 | pending |
| line-3 | line-3-0575-0506-s001894 | reverse | revenue | 2 | pending |
| line-3 | line-3-0556-0555-s003790 | forward | revenue | 2 | pending |
| line-3 | line-3-0556-0555-s003790 | reverse | revenue | 2 | pending |
| line-3 | line-3-0505-0671-s007373 | reverse | revenue | 2 | pending |
| line-3 | line-3-0575-0506-s001894 | reverse | spare | 1 | pending |
| line-3 | line-3-0556-0555-s003790 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**50 trainsets exceed the reference platform envelope**, requiring **2,975.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0556-0555-s004018 | 6 | 4 | 2 | 119.0 |
| line-1-0564-0711-s007621 | 6 | 2 | 4 | 238.0 |
| line-1-0594-0921-s012269 | 3 | 2 | 1 | 59.5 |
| line-1-0639-0491-s001601 | 8 | 4 | 4 | 238.0 |
| line-1-0700-0463-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0574-0783-s018642 | 5 | 2 | 3 | 178.5 |
| line-2-0610-0680-s016225 | 10 | 2 | 8 | 476.0 |
| line-2-0659-0592-s013803 | 10 | 2 | 8 | 476.0 |
| line-2-0747-0479-s010791 | 10 | 2 | 8 | 476.0 |
| line-2-1091-0156-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0505-0671-s007373 | 2 | 2 | 0 | 0.0 |
| line-3-0556-0555-s003790 | 5 | 4 | 1 | 59.5 |
| line-3-0575-0506-s001894 | 6 | 2 | 4 | 238.0 |
| line-3-0647-0470-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mahalla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
