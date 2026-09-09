# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **57 trainsets at 13 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **50 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0530-0342-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0449-0371-s002061 | forward | revenue | 2 | pending |
| line-1 | line-1-0449-0371-s002061 | reverse | revenue | 2 | pending |
| line-1 | line-1-0374-0375-s004109 | forward | revenue | 2 | pending |
| line-1 | line-1-0374-0375-s004109 | reverse | revenue | 2 | pending |
| line-1 | line-1-0365-0303-s006173 | forward | revenue | 2 | pending |
| line-1 | line-1-0365-0303-s006173 | reverse | revenue | 2 | pending |
| line-1 | line-1-0318-0258-s008245 | reverse | revenue | 2 | pending |
| line-1 | line-1-0449-0371-s002061 | forward | spare | 1 | pending |
| line-1 | line-1-0449-0371-s002061 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0644-0475-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0408-0437-s005715 | forward | revenue | 3 | pending |
| line-2 | line-2-0408-0437-s005715 | reverse | revenue | 3 | pending |
| line-2 | line-2-0374-0375-s007350 | forward | revenue | 3 | pending |
| line-2 | line-2-0374-0375-s007350 | reverse | revenue | 3 | pending |
| line-2 | line-2-0278-0389-s009874 | forward | revenue | 3 | pending |
| line-2 | line-2-0278-0389-s009874 | reverse | revenue | 3 | pending |
| line-2 | line-2-0210-0463-s012395 | reverse | revenue | 2 | pending |
| line-2 | line-2-0210-0463-s012395 | reverse | spare | 1 | pending |
| line-2 | line-2-0644-0475-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0408-0437-s005715 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0330-0343-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0375-s001415 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0375-s001415 | reverse | revenue | 2 | pending |
| line-3 | line-3-0454-0260-s004710 | reverse | revenue | 2 | pending |
| line-3 | line-3-0374-0375-s001415 | reverse | spare | 1 | pending |
| line-3 | line-3-0454-0260-s004710 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**25 trainsets exceed the reference platform envelope**, requiring **1,225.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0318-0258-s008245 | 2 | 2 | 0 | 0.0 |
| line-1-0365-0303-s006173 | 4 | 2 | 2 | 98.0 |
| line-1-0374-0375-s004109 | 4 | 4 | 0 | 0.0 |
| line-1-0449-0371-s002061 | 6 | 2 | 4 | 196.0 |
| line-1-0530-0342-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0210-0463-s012395 | 3 | 2 | 1 | 49.0 |
| line-2-0278-0389-s009874 | 6 | 2 | 4 | 196.0 |
| line-2-0374-0375-s007350 | 6 | 4 | 2 | 98.0 |
| line-2-0408-0437-s005715 | 7 | 2 | 5 | 245.0 |
| line-2-0644-0475-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0330-0343-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0374-0375-s001415 | 6 | 4 | 2 | 98.0 |
| line-3-0454-0260-s004710 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Garissa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
