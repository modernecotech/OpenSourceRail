# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0538-0267-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | forward | revenue | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | reverse | revenue | 3 | pending |
| line-1 | line-1-0384-0396-s005220 | forward | revenue | 2 | pending |
| line-1 | line-1-0384-0396-s005220 | reverse | revenue | 2 | pending |
| line-1 | line-1-0429-0465-s007719 | forward | revenue | 2 | pending |
| line-1 | line-1-0429-0465-s007719 | reverse | revenue | 2 | pending |
| line-1 | line-1-0440-0568-s010031 | forward | revenue | 2 | pending |
| line-1 | line-1-0440-0568-s010031 | reverse | revenue | 2 | pending |
| line-1 | line-1-0406-0668-s012325 | reverse | revenue | 2 | pending |
| line-1 | line-1-0384-0396-s005220 | forward | spare | 1 | pending |
| line-1 | line-1-0384-0396-s005220 | reverse | spare | 1 | pending |
| line-1 | line-1-0429-0465-s007719 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0511-0559-s004314 | forward | revenue | 3 | pending |
| line-2 | line-2-0511-0559-s004314 | reverse | revenue | 3 | pending |
| line-2 | line-2-0411-0495-s007332 | forward | revenue | 3 | pending |
| line-2 | line-2-0411-0495-s007332 | reverse | revenue | 3 | pending |
| line-2 | line-2-0384-0396-s010681 | forward | revenue | 3 | pending |
| line-2 | line-2-0384-0396-s010681 | reverse | revenue | 3 | pending |
| line-2 | line-2-0298-0391-s012702 | forward | revenue | 2 | pending |
| line-2 | line-2-0298-0391-s012702 | reverse | revenue | 2 | pending |
| line-2 | line-2-0217-0397-s014734 | reverse | revenue | 2 | pending |
| line-2 | line-2-0298-0391-s012702 | forward | spare | 1 | pending |
| line-2 | line-2-0298-0391-s012702 | reverse | spare | 1 | pending |
| line-2 | line-2-0217-0397-s014734 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0271-0514-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0342-0432-s003016 | forward | revenue | 3 | pending |
| line-3 | line-3-0342-0432-s003016 | reverse | revenue | 2 | pending |
| line-3 | line-3-0384-0396-s004354 | forward | revenue | 2 | pending |
| line-3 | line-3-0384-0396-s004354 | reverse | revenue | 2 | pending |
| line-3 | line-3-0469-0419-s006620 | forward | revenue | 2 | pending |
| line-3 | line-3-0469-0419-s006620 | reverse | revenue | 2 | pending |
| line-3 | line-3-0557-0472-s008869 | reverse | revenue | 2 | pending |
| line-3 | line-3-0342-0432-s003016 | reverse | spare | 1 | pending |
| line-3 | line-3-0384-0396-s004354 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **1,764.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0384-0396-s005220 | 6 | 4 | 2 | 98.0 |
| line-1-0406-0668-s012325 | 2 | 2 | 0 | 0.0 |
| line-1-0429-0465-s007719 | 5 | 2 | 3 | 147.0 |
| line-1-0440-0568-s010031 | 4 | 2 | 2 | 98.0 |
| line-1-0456-0328-s003020 | 6 | 2 | 4 | 196.0 |
| line-1-0538-0267-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0217-0397-s014734 | 3 | 2 | 1 | 49.0 |
| line-2-0298-0391-s012702 | 6 | 2 | 4 | 196.0 |
| line-2-0384-0396-s010681 | 6 | 4 | 2 | 98.0 |
| line-2-0411-0495-s007332 | 6 | 2 | 4 | 196.0 |
| line-2-0511-0559-s004314 | 6 | 2 | 4 | 196.0 |
| line-2-0550-0738-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0271-0514-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0342-0432-s003016 | 6 | 2 | 4 | 196.0 |
| line-3-0384-0396-s004354 | 5 | 4 | 1 | 49.0 |
| line-3-0469-0419-s006620 | 4 | 2 | 2 | 98.0 |
| line-3-0557-0472-s008869 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Kigoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
