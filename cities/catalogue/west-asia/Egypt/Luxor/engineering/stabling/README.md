# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **111 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **99 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0268-0383-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | forward | revenue | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | reverse | revenue | 3 | pending |
| line-1 | line-1-0471-0539-s006674 | forward | revenue | 3 | pending |
| line-1 | line-1-0471-0539-s006674 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0547-s008986 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0547-s008986 | reverse | revenue | 3 | pending |
| line-1 | line-1-0712-0526-s013238 | reverse | revenue | 3 | pending |
| line-1 | line-1-0405-0484-s004702 | reverse | spare | 1 | pending |
| line-1 | line-1-0471-0539-s006674 | forward | spare | 1 | pending |
| line-1 | line-1-0471-0539-s006674 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0954-0093-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0588-0433-s011050 | forward | revenue | 4 | pending |
| line-2 | line-2-0588-0433-s011050 | reverse | revenue | 4 | pending |
| line-2 | line-2-0548-0547-s013850 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0547-s013850 | reverse | revenue | 4 | pending |
| line-2 | line-2-0497-0579-s015672 | forward | revenue | 4 | pending |
| line-2 | line-2-0497-0579-s015672 | reverse | revenue | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | forward | revenue | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | reverse | revenue | 4 | pending |
| line-2 | line-2-0324-0669-s020767 | reverse | revenue | 4 | pending |
| line-2 | line-2-0588-0433-s011050 | forward | spare | 1 | pending |
| line-2 | line-2-0588-0433-s011050 | reverse | spare | 1 | pending |
| line-2 | line-2-0548-0547-s013850 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0547-s013850 | reverse | spare | 1 | pending |
| line-2 | line-2-0497-0579-s015672 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | reverse | revenue | 3 | pending |
| line-3 | line-3-0548-0547-s009220 | forward | revenue | 3 | pending |
| line-3 | line-3-0548-0547-s009220 | reverse | revenue | 3 | pending |
| line-3 | line-3-0490-0478-s011104 | forward | revenue | 3 | pending |
| line-3 | line-3-0490-0478-s011104 | reverse | revenue | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | forward | revenue | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | reverse | revenue | 3 | pending |
| line-3 | line-3-0300-0398-s016658 | reverse | revenue | 3 | pending |
| line-3 | line-3-0589-0631-s006957 | reverse | spare | 1 | pending |
| line-3 | line-3-0548-0547-s009220 | forward | spare | 1 | pending |
| line-3 | line-3-0548-0547-s009220 | reverse | spare | 1 | pending |
| line-3 | line-3-0490-0478-s011104 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0268-0383-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0405-0484-s004702 | 8 | 4 | 4 | 238.0 |
| line-1-0471-0539-s006674 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0547-s008986 | 6 | 4 | 2 | 119.0 |
| line-1-0712-0526-s013238 | 3 | 2 | 1 | 59.5 |
| line-2-0324-0669-s020767 | 4 | 2 | 2 | 119.0 |
| line-2-0411-0665-s018221 | 8 | 2 | 6 | 357.0 |
| line-2-0497-0579-s015672 | 9 | 2 | 7 | 416.5 |
| line-2-0548-0547-s013850 | 10 | 4 | 6 | 357.0 |
| line-2-0588-0433-s011050 | 10 | 2 | 8 | 476.0 |
| line-2-0954-0093-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0300-0398-s016658 | 3 | 2 | 1 | 59.5 |
| line-3-0414-0479-s012992 | 6 | 4 | 2 | 119.0 |
| line-3-0490-0478-s011104 | 7 | 2 | 5 | 297.5 |
| line-3-0548-0547-s009220 | 8 | 4 | 4 | 238.0 |
| line-3-0589-0631-s006957 | 8 | 2 | 6 | 357.0 |
| line-3-0621-0862-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Luxor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
