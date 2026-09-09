# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **59 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **53 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0584-0390-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0468-0406-s003012 | forward | revenue | 3 | pending |
| line-1 | line-1-0468-0406-s003012 | reverse | revenue | 3 | pending |
| line-1 | line-1-0383-0377-s004992 | forward | revenue | 2 | pending |
| line-1 | line-1-0383-0377-s004992 | reverse | revenue | 2 | pending |
| line-1 | line-1-0298-0414-s007690 | forward | revenue | 2 | pending |
| line-1 | line-1-0298-0414-s007690 | reverse | revenue | 2 | pending |
| line-1 | line-1-0181-0377-s010370 | reverse | revenue | 2 | pending |
| line-1 | line-1-0383-0377-s004992 | forward | spare | 1 | pending |
| line-1 | line-1-0383-0377-s004992 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0280-0408-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0383-0377-s003485 | forward | revenue | 3 | pending |
| line-2 | line-2-0383-0377-s003485 | reverse | revenue | 3 | pending |
| line-2 | line-2-0482-0364-s006028 | forward | revenue | 2 | pending |
| line-2 | line-2-0482-0364-s006028 | reverse | revenue | 2 | pending |
| line-2 | line-2-0581-0385-s008222 | reverse | revenue | 2 | pending |
| line-2 | line-2-0482-0364-s006028 | forward | spare | 1 | pending |
| line-2 | line-2-0482-0364-s006028 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0693-0552-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0591-0446-s003242 | forward | revenue | 3 | pending |
| line-3 | line-3-0591-0446-s003242 | reverse | revenue | 3 | pending |
| line-3 | line-3-0462-0431-s006256 | forward | revenue | 2 | pending |
| line-3 | line-3-0462-0431-s006256 | reverse | revenue | 2 | pending |
| line-3 | line-3-0383-0377-s008530 | forward | revenue | 2 | pending |
| line-3 | line-3-0383-0377-s008530 | reverse | revenue | 2 | pending |
| line-3 | line-3-0336-0362-s010338 | reverse | revenue | 2 | pending |
| line-3 | line-3-0462-0431-s006256 | forward | spare | 1 | pending |
| line-3 | line-3-0462-0431-s006256 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**19 trainsets exceed the reference platform envelope**, requiring **931.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0181-0377-s010370 | 2 | 2 | 0 | 0.0 |
| line-1-0298-0414-s007690 | 4 | 4 | 0 | 0.0 |
| line-1-0383-0377-s004992 | 6 | 4 | 2 | 98.0 |
| line-1-0468-0406-s003012 | 6 | 4 | 2 | 98.0 |
| line-1-0584-0390-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0280-0408-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0383-0377-s003485 | 6 | 4 | 2 | 98.0 |
| line-2-0482-0364-s006028 | 6 | 2 | 4 | 196.0 |
| line-2-0581-0385-s008222 | 2 | 2 | 0 | 0.0 |
| line-3-0336-0362-s010338 | 2 | 2 | 0 | 0.0 |
| line-3-0383-0377-s008530 | 4 | 4 | 0 | 0.0 |
| line-3-0462-0431-s006256 | 6 | 4 | 2 | 98.0 |
| line-3-0591-0446-s003242 | 6 | 2 | 4 | 196.0 |
| line-3-0693-0552-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Lahij/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
