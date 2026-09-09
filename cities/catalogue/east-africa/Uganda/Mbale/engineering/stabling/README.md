# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **71 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **63 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0539-0355-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0333-s003009 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0333-s003009 | reverse | revenue | 3 | pending |
| line-1 | line-1-0307-0259-s007546 | forward | revenue | 3 | pending |
| line-1 | line-1-0307-0259-s007546 | reverse | revenue | 3 | pending |
| line-1 | line-1-0331-0344-s009495 | forward | revenue | 3 | pending |
| line-1 | line-1-0331-0344-s009495 | reverse | revenue | 3 | pending |
| line-1 | line-1-0255-0370-s011994 | forward | revenue | 2 | pending |
| line-1 | line-1-0255-0370-s011994 | reverse | revenue | 2 | pending |
| line-1 | line-1-0176-0341-s014506 | reverse | revenue | 2 | pending |
| line-1 | line-1-0255-0370-s011994 | forward | spare | 1 | pending |
| line-1 | line-1-0255-0370-s011994 | reverse | spare | 1 | pending |
| line-1 | line-1-0176-0341-s014506 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0075-0508-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0264-0427-s005234 | forward | revenue | 4 | pending |
| line-2 | line-2-0264-0427-s005234 | reverse | revenue | 4 | pending |
| line-2 | line-2-0362-0447-s008254 | forward | revenue | 4 | pending |
| line-2 | line-2-0362-0447-s008254 | reverse | revenue | 4 | pending |
| line-2 | line-2-0513-0369-s014439 | reverse | revenue | 4 | pending |
| line-2 | line-2-0264-0427-s005234 | forward | spare | 1 | pending |
| line-2 | line-2-0264-0427-s005234 | reverse | spare | 1 | pending |
| line-2 | line-2-0362-0447-s008254 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0318-0463-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0369-0375-s002512 | forward | revenue | 3 | pending |
| line-3 | line-3-0369-0375-s002512 | reverse | revenue | 3 | pending |
| line-3 | line-3-0290-0295-s005200 | reverse | revenue | 2 | pending |
| line-3 | line-3-0290-0295-s005200 | reverse | spare | 1 | pending |
| line-3 | line-3-0318-0463-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**45 trainsets exceed the reference platform envelope**, requiring **2,205.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0176-0341-s014506 | 3 | 2 | 1 | 49.0 |
| line-1-0255-0370-s011994 | 6 | 2 | 4 | 196.0 |
| line-1-0307-0259-s007546 | 6 | 2 | 4 | 196.0 |
| line-1-0331-0344-s009495 | 6 | 2 | 4 | 196.0 |
| line-1-0432-0333-s003009 | 6 | 2 | 4 | 196.0 |
| line-1-0539-0355-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0075-0508-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0264-0427-s005234 | 10 | 2 | 8 | 392.0 |
| line-2-0362-0447-s008254 | 9 | 2 | 7 | 343.0 |
| line-2-0513-0369-s014439 | 4 | 2 | 2 | 98.0 |
| line-3-0290-0295-s005200 | 3 | 2 | 1 | 49.0 |
| line-3-0318-0463-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0369-0375-s002512 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
