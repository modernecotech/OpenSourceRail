# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 149 at depots = 189 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0689-0101-s020992 | line-1 | declared-depot | 51 | 3,034.5 | 9 |
| line-2-0897-0226-s000000 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0669-0844-s000000 | line-3 | declared-depot | 47 | 2,796.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0595-0777-s006194 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0777-s006194 | station | reverse | revenue | 1 |
| line-1 | line-1-0600-1040-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0614-0652-s008851 | station | forward | revenue | 1 |
| line-1 | line-1-0614-0652-s008851 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0562-s010767 | station | forward | revenue | 1 |
| line-1 | line-1-0628-0562-s010767 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0471-s012703 | station | forward | revenue | 1 |
| line-1 | line-1-0642-0471-s012703 | station | reverse | revenue | 1 |
| line-1 | line-1-0658-0370-s014856 | station | forward | revenue | 1 |
| line-1 | line-1-0658-0370-s014856 | station | reverse | revenue | 1 |
| line-1 | line-1-0689-0101-s020992 | station | reverse | revenue | 2 |
| line-2 | line-2-0216-0821-s020927 | station | reverse | revenue | 2 |
| line-2 | line-2-0441-0636-s014324 | station | forward | revenue | 1 |
| line-2 | line-2-0441-0636-s014324 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0550-s011254 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0550-s011254 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0506-s009689 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0506-s009689 | station | reverse | revenue | 1 |
| line-2 | line-2-0642-0471-s008445 | station | forward | revenue | 1 |
| line-2 | line-2-0642-0471-s008445 | station | reverse | revenue | 1 |
| line-2 | line-2-0756-0377-s005082 | station | forward | revenue | 1 |
| line-2 | line-2-0756-0377-s005082 | station | reverse | revenue | 1 |
| line-2 | line-2-0897-0226-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0048-0314-s018594 | station | reverse | revenue | 2 |
| line-3 | line-3-0337-0544-s010051 | station | forward | revenue | 1 |
| line-3 | line-3-0337-0544-s010051 | station | reverse | revenue | 1 |
| line-3 | line-3-0439-0637-s006947 | station | forward | revenue | 1 |
| line-3 | line-3-0439-0637-s006947 | station | reverse | revenue | 1 |
| line-3 | line-3-0536-0724-s004017 | station | forward | revenue | 1 |
| line-3 | line-3-0536-0724-s004017 | station | reverse | revenue | 1 |
| line-3 | line-3-0595-0777-s002222 | station | forward | revenue | 1 |
| line-3 | line-3-0595-0777-s002222 | station | reverse | revenue | 1 |
| line-3 | line-3-0669-0844-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0689-0101-s020992 | depot | — | revenue | 45 |
| line-1 | line-1-0689-0101-s020992 | depot | — | spare | 5 |
| line-1 | line-1-0689-0101-s020992 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0897-0226-s000000 | depot | — | revenue | 45 |
| line-2 | line-2-0897-0226-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0897-0226-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0669-0844-s000000 | depot | — | revenue | 41 |
| line-3 | line-3-0669-0844-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0669-0844-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kandy-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **189 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **171 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **149 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0600-1040-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0595-0777-s006194 | forward | revenue | 5 | pending |
| line-1 | line-1-0595-0777-s006194 | reverse | revenue | 5 | pending |
| line-1 | line-1-0614-0652-s008851 | forward | revenue | 5 | pending |
| line-1 | line-1-0614-0652-s008851 | reverse | revenue | 5 | pending |
| line-1 | line-1-0628-0562-s010767 | forward | revenue | 5 | pending |
| line-1 | line-1-0628-0562-s010767 | reverse | revenue | 5 | pending |
| line-1 | line-1-0642-0471-s012703 | forward | revenue | 5 | pending |
| line-1 | line-1-0642-0471-s012703 | reverse | revenue | 5 | pending |
| line-1 | line-1-0658-0370-s014856 | forward | revenue | 5 | pending |
| line-1 | line-1-0658-0370-s014856 | reverse | revenue | 5 | pending |
| line-1 | line-1-0689-0101-s020992 | reverse | revenue | 4 | pending |
| line-1 | line-1-0689-0101-s020992 | reverse | spare | 1 | pending |
| line-1 | line-1-0600-1040-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0595-0777-s006194 | forward | spare | 1 | pending |
| line-1 | line-1-0595-0777-s006194 | reverse | spare | 1 | pending |
| line-1 | line-1-0614-0652-s008851 | forward | spare | 1 | pending |
| line-1 | line-1-0614-0652-s008851 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0377-s005082 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0377-s005082 | reverse | revenue | 5 | pending |
| line-2 | line-2-0642-0471-s008445 | forward | revenue | 5 | pending |
| line-2 | line-2-0642-0471-s008445 | reverse | revenue | 5 | pending |
| line-2 | line-2-0599-0506-s009689 | forward | revenue | 5 | pending |
| line-2 | line-2-0599-0506-s009689 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0550-s011254 | forward | revenue | 5 | pending |
| line-2 | line-2-0546-0550-s011254 | reverse | revenue | 5 | pending |
| line-2 | line-2-0441-0636-s014324 | forward | revenue | 5 | pending |
| line-2 | line-2-0441-0636-s014324 | reverse | revenue | 5 | pending |
| line-2 | line-2-0216-0821-s020927 | reverse | revenue | 4 | pending |
| line-2 | line-2-0216-0821-s020927 | reverse | spare | 1 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0377-s005082 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0377-s005082 | reverse | spare | 1 | pending |
| line-2 | line-2-0642-0471-s008445 | forward | spare | 1 | pending |
| line-2 | line-2-0642-0471-s008445 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0669-0844-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0595-0777-s002222 | forward | revenue | 6 | pending |
| line-3 | line-3-0595-0777-s002222 | reverse | revenue | 6 | pending |
| line-3 | line-3-0536-0724-s004017 | forward | revenue | 5 | pending |
| line-3 | line-3-0536-0724-s004017 | reverse | revenue | 5 | pending |
| line-3 | line-3-0439-0637-s006947 | forward | revenue | 5 | pending |
| line-3 | line-3-0439-0637-s006947 | reverse | revenue | 5 | pending |
| line-3 | line-3-0337-0544-s010051 | forward | revenue | 5 | pending |
| line-3 | line-3-0337-0544-s010051 | reverse | revenue | 5 | pending |
| line-3 | line-3-0048-0314-s018594 | reverse | revenue | 5 | pending |
| line-3 | line-3-0536-0724-s004017 | forward | spare | 1 | pending |
| line-3 | line-3-0536-0724-s004017 | reverse | spare | 1 | pending |
| line-3 | line-3-0439-0637-s006947 | forward | spare | 1 | pending |
| line-3 | line-3-0439-0637-s006947 | reverse | spare | 1 | pending |
| line-3 | line-3-0337-0544-s010051 | forward | spare | 1 | pending |
| line-3 | line-3-0337-0544-s010051 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**137 trainsets exceed the reference platform envelope**, requiring **8,151.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0595-0777-s006194 | 12 | 4 | 8 | 476.0 |
| line-1-0600-1040-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0614-0652-s008851 | 12 | 2 | 10 | 595.0 |
| line-1-0628-0562-s010767 | 10 | 2 | 8 | 476.0 |
| line-1-0642-0471-s012703 | 10 | 4 | 6 | 357.0 |
| line-1-0658-0370-s014856 | 10 | 2 | 8 | 476.0 |
| line-1-0689-0101-s020992 | 5 | 2 | 3 | 178.5 |
| line-2-0216-0821-s020927 | 5 | 2 | 3 | 178.5 |
| line-2-0441-0636-s014324 | 10 | 4 | 6 | 357.0 |
| line-2-0546-0550-s011254 | 10 | 2 | 8 | 476.0 |
| line-2-0599-0506-s009689 | 10 | 2 | 8 | 476.0 |
| line-2-0642-0471-s008445 | 12 | 4 | 8 | 476.0 |
| line-2-0756-0377-s005082 | 12 | 2 | 10 | 595.0 |
| line-2-0897-0226-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0048-0314-s018594 | 5 | 2 | 3 | 178.5 |
| line-3-0337-0544-s010051 | 12 | 2 | 10 | 595.0 |
| line-3-0439-0637-s006947 | 12 | 4 | 8 | 476.0 |
| line-3-0536-0724-s004017 | 12 | 2 | 10 | 595.0 |
| line-3-0595-0777-s002222 | 12 | 4 | 8 | 476.0 |
| line-3-0669-0844-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Kandy/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
