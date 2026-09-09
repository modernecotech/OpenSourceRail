# Station and depot overnight allocation

Plan: **26 trainsets at stations + 31 at depots = 57 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0318-0258-s008245 | line-1 | storage-at-existing-powered-service-point | 9 | 441.0 | 0 |
| line-2-0210-0463-s012395 | line-2 | declared-depot | 16 | 784.0 | 9 |
| line-3-0454-0260-s004710 | line-3 | storage-at-existing-powered-service-point | 6 | 294.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0318-0258-s008245 | station | reverse | revenue | 2 |
| line-1 | line-1-0365-0303-s006173 | station | forward | revenue | 1 |
| line-1 | line-1-0365-0303-s006173 | station | reverse | revenue | 1 |
| line-1 | line-1-0374-0375-s004109 | station | forward | revenue | 1 |
| line-1 | line-1-0374-0375-s004109 | station | reverse | revenue | 1 |
| line-1 | line-1-0449-0371-s002061 | station | forward | revenue | 1 |
| line-1 | line-1-0449-0371-s002061 | station | reverse | revenue | 1 |
| line-1 | line-1-0530-0342-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0210-0463-s012395 | station | reverse | revenue | 2 |
| line-2 | line-2-0278-0389-s009874 | station | forward | revenue | 1 |
| line-2 | line-2-0278-0389-s009874 | station | reverse | revenue | 1 |
| line-2 | line-2-0374-0375-s007350 | station | forward | revenue | 1 |
| line-2 | line-2-0374-0375-s007350 | station | reverse | revenue | 1 |
| line-2 | line-2-0408-0437-s005715 | station | forward | revenue | 1 |
| line-2 | line-2-0408-0437-s005715 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0475-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0330-0343-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0374-0375-s001415 | station | forward | revenue | 1 |
| line-3 | line-3-0374-0375-s001415 | station | reverse | revenue | 1 |
| line-3 | line-3-0454-0260-s004710 | station | reverse | revenue | 2 |
| line-1 | line-1-0318-0258-s008245 | depot | — | revenue | 7 |
| line-1 | line-1-0318-0258-s008245 | depot | — | spare | 1 |
| line-1 | line-1-0318-0258-s008245 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0210-0463-s012395 | depot | — | revenue | 13 |
| line-2 | line-2-0210-0463-s012395 | depot | — | spare | 2 |
| line-2 | line-2-0210-0463-s012395 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0454-0260-s004710 | depot | — | revenue | 4 |
| line-3 | line-3-0454-0260-s004710 | depot | — | spare | 1 |
| line-3 | line-3-0454-0260-s004710 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/garissa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **57 trainsets at 13 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **50 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **31 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

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
