# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **54 trainsets at 11 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **47 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0273-0600-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0327-0472-s003007 | forward | revenue | 4 | pending |
| line-1 | line-1-0327-0472-s003007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0375-0375-s005392 | forward | revenue | 3 | pending |
| line-1 | line-1-0375-0375-s005392 | reverse | revenue | 3 | pending |
| line-1 | line-1-0363-0292-s008120 | forward | revenue | 3 | pending |
| line-1 | line-1-0363-0292-s008120 | reverse | revenue | 3 | pending |
| line-1 | line-1-0491-0047-s014174 | reverse | revenue | 3 | pending |
| line-1 | line-1-0327-0472-s003007 | reverse | spare | 1 | pending |
| line-1 | line-1-0375-0375-s005392 | forward | spare | 1 | pending |
| line-1 | line-1-0375-0375-s005392 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0465-0310-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0375-0375-s002425 | forward | revenue | 3 | pending |
| line-2 | line-2-0375-0375-s002425 | reverse | revenue | 3 | pending |
| line-2 | line-2-0283-0307-s005366 | reverse | revenue | 2 | pending |
| line-2 | line-2-0283-0307-s005366 | reverse | spare | 1 | pending |
| line-2 | line-2-0465-0310-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0454-0403-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0375-0375-s002107 | forward | revenue | 3 | pending |
| line-3 | line-3-0375-0375-s002107 | reverse | revenue | 2 | pending |
| line-3 | line-3-0258-0373-s004861 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0375-s002107 | reverse | spare | 1 | pending |
| line-3 | line-3-0258-0373-s004861 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**26 trainsets exceed the reference platform envelope**, requiring **1,274.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0273-0600-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0327-0472-s003007 | 8 | 2 | 6 | 294.0 |
| line-1-0363-0292-s008120 | 6 | 2 | 4 | 196.0 |
| line-1-0375-0375-s005392 | 8 | 4 | 4 | 196.0 |
| line-1-0491-0047-s014174 | 3 | 2 | 1 | 49.0 |
| line-2-0283-0307-s005366 | 3 | 2 | 1 | 49.0 |
| line-2-0375-0375-s002425 | 6 | 4 | 2 | 98.0 |
| line-2-0465-0310-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0258-0373-s004861 | 3 | 2 | 1 | 49.0 |
| line-3-0375-0375-s002107 | 6 | 4 | 2 | 98.0 |
| line-3-0454-0403-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Sayun/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
