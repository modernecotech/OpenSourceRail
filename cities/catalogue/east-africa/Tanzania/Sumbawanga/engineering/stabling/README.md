# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **40 trainsets at 10 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **34 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0318-0457-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0369-0375-s002479 | forward | revenue | 3 | pending |
| line-1 | line-1-0369-0375-s002479 | reverse | revenue | 2 | pending |
| line-1 | line-1-0300-0320-s004564 | forward | revenue | 2 | pending |
| line-1 | line-1-0300-0320-s004564 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0324-s006643 | reverse | revenue | 2 | pending |
| line-1 | line-1-0369-0375-s002479 | reverse | spare | 1 | pending |
| line-1 | line-1-0300-0320-s004564 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0375-s002392 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0375-s002392 | reverse | revenue | 3 | pending |
| line-2 | line-2-0270-0428-s005747 | reverse | revenue | 2 | pending |
| line-2 | line-2-0270-0428-s005747 | reverse | spare | 1 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0277-0363-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0345-0348-s001640 | forward | revenue | 2 | pending |
| line-3 | line-3-0345-0348-s001640 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0363-s003276 | reverse | revenue | 2 | pending |
| line-3 | line-3-0345-0348-s001640 | forward | spare | 1 | pending |
| line-3 | line-3-0345-0348-s001640 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**16 trainsets exceed the reference platform envelope**, requiring **784.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0324-s006643 | 2 | 2 | 0 | 0.0 |
| line-1-0300-0320-s004564 | 5 | 2 | 3 | 147.0 |
| line-1-0318-0457-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0369-0375-s002479 | 6 | 4 | 2 | 98.0 |
| line-2-0270-0428-s005747 | 3 | 2 | 1 | 49.0 |
| line-2-0369-0375-s002392 | 6 | 4 | 2 | 98.0 |
| line-2-0462-0393-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0277-0363-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0345-0348-s001640 | 6 | 2 | 4 | 196.0 |
| line-3-0375-0363-s003276 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Sumbawanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
