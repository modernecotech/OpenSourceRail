# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **20 trainsets at 5 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **18 revenue, 1 spare, 1 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0355-0117-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0348-0250-s003434 | forward | revenue | 3 | pending |
| line-1 | line-1-0348-0250-s003434 | reverse | revenue | 2 | pending |
| line-1 | line-1-0366-0325-s005369 | forward | revenue | 2 | pending |
| line-1 | line-1-0366-0325-s005369 | reverse | revenue | 2 | pending |
| line-1 | line-1-0377-0369-s007314 | forward | revenue | 2 | pending |
| line-1 | line-1-0377-0369-s007314 | reverse | revenue | 2 | pending |
| line-1 | line-1-0442-0432-s009610 | reverse | revenue | 2 | pending |
| line-1 | line-1-0348-0250-s003434 | reverse | spare | 1 | pending |
| line-1 | line-1-0366-0325-s005369 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**10 trainsets exceed the reference platform envelope**, requiring **490.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0348-0250-s003434 | 6 | 2 | 4 | 196.0 |
| line-1-0355-0117-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0366-0325-s005369 | 5 | 2 | 3 | 147.0 |
| line-1-0377-0369-s007314 | 4 | 2 | 2 | 98.0 |
| line-1-0442-0432-s009610 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Edea/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
