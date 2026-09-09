# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **96 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **86 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0726-0492-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0627-0492-s003006 | forward | revenue | 3 | pending |
| line-1 | line-1-0627-0492-s003006 | reverse | revenue | 3 | pending |
| line-1 | line-1-0542-0554-s005313 | forward | revenue | 3 | pending |
| line-1 | line-1-0542-0554-s005313 | reverse | revenue | 3 | pending |
| line-1 | line-1-0410-0471-s009032 | forward | revenue | 3 | pending |
| line-1 | line-1-0410-0471-s009032 | reverse | revenue | 3 | pending |
| line-1 | line-1-0318-0458-s012053 | forward | revenue | 3 | pending |
| line-1 | line-1-0318-0458-s012053 | reverse | revenue | 3 | pending |
| line-1 | line-1-0199-0416-s014781 | forward | revenue | 2 | pending |
| line-1 | line-1-0199-0416-s014781 | reverse | revenue | 2 | pending |
| line-1 | line-1-0096-0402-s017512 | reverse | revenue | 2 | pending |
| line-1 | line-1-0199-0416-s014781 | forward | spare | 1 | pending |
| line-1 | line-1-0199-0416-s014781 | reverse | spare | 1 | pending |
| line-1 | line-1-0096-0402-s017512 | reverse | spare | 1 | pending |
| line-1 | line-1-0726-0492-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0637-0296-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0610-0337-s001620 | forward | revenue | 3 | pending |
| line-2 | line-2-0610-0337-s001620 | reverse | revenue | 3 | pending |
| line-2 | line-2-0603-0444-s004632 | forward | revenue | 3 | pending |
| line-2 | line-2-0603-0444-s004632 | reverse | revenue | 2 | pending |
| line-2 | line-2-0542-0554-s007646 | forward | revenue | 2 | pending |
| line-2 | line-2-0542-0554-s007646 | reverse | revenue | 2 | pending |
| line-2 | line-2-0532-0653-s009917 | forward | revenue | 2 | pending |
| line-2 | line-2-0532-0653-s009917 | reverse | revenue | 2 | pending |
| line-2 | line-2-0473-0714-s012175 | reverse | revenue | 2 | pending |
| line-2 | line-2-0603-0444-s004632 | reverse | spare | 1 | pending |
| line-2 | line-2-0542-0554-s007646 | forward | spare | 1 | pending |
| line-2 | line-2-0542-0554-s007646 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0027-0206-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0169-0376-s005406 | forward | revenue | 4 | pending |
| line-3 | line-3-0169-0376-s005406 | reverse | revenue | 4 | pending |
| line-3 | line-3-0213-0482-s008415 | forward | revenue | 4 | pending |
| line-3 | line-3-0213-0482-s008415 | reverse | revenue | 4 | pending |
| line-3 | line-3-0314-0548-s011433 | forward | revenue | 3 | pending |
| line-3 | line-3-0314-0548-s011433 | reverse | revenue | 3 | pending |
| line-3 | line-3-0432-0677-s015136 | reverse | revenue | 3 | pending |
| line-3 | line-3-0314-0548-s011433 | forward | spare | 1 | pending |
| line-3 | line-3-0314-0548-s011433 | reverse | spare | 1 | pending |
| line-3 | line-3-0432-0677-s015136 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0096-0402-s017512 | 3 | 2 | 1 | 59.5 |
| line-1-0199-0416-s014781 | 6 | 2 | 4 | 238.0 |
| line-1-0318-0458-s012053 | 6 | 2 | 4 | 238.0 |
| line-1-0410-0471-s009032 | 6 | 2 | 4 | 238.0 |
| line-1-0542-0554-s005313 | 6 | 4 | 2 | 119.0 |
| line-1-0627-0492-s003006 | 6 | 2 | 4 | 238.0 |
| line-1-0726-0492-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0473-0714-s012175 | 2 | 2 | 0 | 0.0 |
| line-2-0532-0653-s009917 | 4 | 2 | 2 | 119.0 |
| line-2-0542-0554-s007646 | 6 | 4 | 2 | 119.0 |
| line-2-0603-0444-s004632 | 6 | 2 | 4 | 238.0 |
| line-2-0610-0337-s001620 | 6 | 2 | 4 | 238.0 |
| line-2-0637-0296-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0027-0206-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0169-0376-s005406 | 8 | 2 | 6 | 357.0 |
| line-3-0213-0482-s008415 | 8 | 2 | 6 | 357.0 |
| line-3-0314-0548-s011433 | 8 | 2 | 6 | 357.0 |
| line-3-0432-0677-s015136 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Beira/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
