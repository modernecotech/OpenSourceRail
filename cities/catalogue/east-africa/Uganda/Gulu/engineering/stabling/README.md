# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **139 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **125 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0724-0363-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0610-0471-s003666 | forward | revenue | 4 | pending |
| line-1 | line-1-0610-0471-s003666 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0553-s006122 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0553-s006122 | reverse | revenue | 4 | pending |
| line-1 | line-1-0495-0609-s008598 | forward | revenue | 4 | pending |
| line-1 | line-1-0495-0609-s008598 | reverse | revenue | 4 | pending |
| line-1 | line-1-0429-0827-s014944 | reverse | revenue | 4 | pending |
| line-1 | line-1-0724-0363-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0610-0471-s003666 | forward | spare | 1 | pending |
| line-1 | line-1-0610-0471-s003666 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0553-s006122 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1012-0957-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0665-0583-s012432 | forward | revenue | 8 | pending |
| line-2 | line-2-0665-0583-s012432 | reverse | revenue | 8 | pending |
| line-2 | line-2-0550-0553-s016052 | forward | revenue | 7 | pending |
| line-2 | line-2-0550-0553-s016052 | reverse | revenue | 7 | pending |
| line-2 | line-2-0510-0484-s018168 | forward | revenue | 7 | pending |
| line-2 | line-2-0510-0484-s018168 | reverse | revenue | 7 | pending |
| line-2 | line-2-0122-0216-s028691 | reverse | revenue | 7 | pending |
| line-2 | line-2-0550-0553-s016052 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0553-s016052 | reverse | spare | 1 | pending |
| line-2 | line-2-0510-0484-s018168 | forward | spare | 1 | pending |
| line-2 | line-2-0510-0484-s018168 | reverse | spare | 1 | pending |
| line-2 | line-2-0122-0216-s028691 | reverse | spare | 1 | pending |
| line-2 | line-2-1012-0957-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0550-0083-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0500-0368-s007009 | forward | revenue | 6 | pending |
| line-3 | line-3-0500-0368-s007009 | reverse | revenue | 6 | pending |
| line-3 | line-3-0429-0492-s010094 | forward | revenue | 6 | pending |
| line-3 | line-3-0429-0492-s010094 | reverse | revenue | 5 | pending |
| line-3 | line-3-0320-0751-s016424 | reverse | revenue | 5 | pending |
| line-3 | line-3-0429-0492-s010094 | reverse | spare | 1 | pending |
| line-3 | line-3-0320-0751-s016424 | reverse | spare | 1 | pending |
| line-3 | line-3-0550-0083-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0500-0368-s007009 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0429-0827-s014944 | 4 | 2 | 2 | 119.0 |
| line-1-0495-0609-s008598 | 8 | 2 | 6 | 357.0 |
| line-1-0550-0553-s006122 | 9 | 4 | 5 | 297.5 |
| line-1-0610-0471-s003666 | 10 | 2 | 8 | 476.0 |
| line-1-0724-0363-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0122-0216-s028691 | 8 | 2 | 6 | 357.0 |
| line-2-0510-0484-s018168 | 16 | 2 | 14 | 833.0 |
| line-2-0550-0553-s016052 | 16 | 4 | 12 | 714.0 |
| line-2-0665-0583-s012432 | 16 | 2 | 14 | 833.0 |
| line-2-1012-0957-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0320-0751-s016424 | 6 | 2 | 4 | 238.0 |
| line-3-0429-0492-s010094 | 12 | 2 | 10 | 595.0 |
| line-3-0500-0368-s007009 | 13 | 2 | 11 | 654.5 |
| line-3-0550-0083-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Gulu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
