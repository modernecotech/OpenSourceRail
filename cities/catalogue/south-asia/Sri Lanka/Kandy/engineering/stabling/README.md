# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 155 at depots = 195 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0689-0101-s022168 | line-1 | declared-depot | 54 | 3,213.0 | 10 |
| line-2-0897-0226-s000000 | line-2 | declared-depot | 53 | 3,153.5 | 10 |
| line-3-0669-0844-s000000 | line-3 | declared-depot | 48 | 2,856.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0595-0777-s006836 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0777-s006836 | station | reverse | revenue | 1 |
| line-1 | line-1-0600-1040-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0614-0652-s009493 | station | forward | revenue | 1 |
| line-1 | line-1-0614-0652-s009493 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0562-s011409 | station | forward | revenue | 1 |
| line-1 | line-1-0628-0562-s011409 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0471-s013345 | station | forward | revenue | 1 |
| line-1 | line-1-0642-0471-s013345 | station | reverse | revenue | 1 |
| line-1 | line-1-0658-0370-s015498 | station | forward | revenue | 1 |
| line-1 | line-1-0658-0370-s015498 | station | reverse | revenue | 1 |
| line-1 | line-1-0689-0101-s022168 | station | reverse | revenue | 2 |
| line-2 | line-2-0216-0821-s021340 | station | reverse | revenue | 2 |
| line-2 | line-2-0441-0636-s014722 | station | forward | revenue | 1 |
| line-2 | line-2-0441-0636-s014722 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0550-s011651 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0550-s011651 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0506-s010086 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0506-s010086 | station | reverse | revenue | 1 |
| line-2 | line-2-0642-0471-s008843 | station | forward | revenue | 1 |
| line-2 | line-2-0642-0471-s008843 | station | reverse | revenue | 1 |
| line-2 | line-2-0756-0377-s005479 | station | forward | revenue | 1 |
| line-2 | line-2-0756-0377-s005479 | station | reverse | revenue | 1 |
| line-2 | line-2-0897-0226-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0048-0314-s019373 | station | reverse | revenue | 2 |
| line-3 | line-3-0337-0544-s010051 | station | forward | revenue | 1 |
| line-3 | line-3-0337-0544-s010051 | station | reverse | revenue | 1 |
| line-3 | line-3-0439-0637-s006947 | station | forward | revenue | 1 |
| line-3 | line-3-0439-0637-s006947 | station | reverse | revenue | 1 |
| line-3 | line-3-0536-0724-s004017 | station | forward | revenue | 1 |
| line-3 | line-3-0536-0724-s004017 | station | reverse | revenue | 1 |
| line-3 | line-3-0595-0777-s002222 | station | forward | revenue | 1 |
| line-3 | line-3-0595-0777-s002222 | station | reverse | revenue | 1 |
| line-3 | line-3-0669-0844-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0689-0101-s022168 | depot | — | revenue | 47 |
| line-1 | line-1-0689-0101-s022168 | depot | — | spare | 6 |
| line-1 | line-1-0689-0101-s022168 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0897-0226-s000000 | depot | — | revenue | 46 |
| line-2 | line-2-0897-0226-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0897-0226-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0669-0844-s000000 | depot | — | revenue | 42 |
| line-3 | line-3-0669-0844-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0669-0844-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kandy-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **195 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **175 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **155 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0600-1040-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0595-0777-s006836 | forward | revenue | 5 | pending |
| line-1 | line-1-0595-0777-s006836 | reverse | revenue | 5 | pending |
| line-1 | line-1-0614-0652-s009493 | forward | revenue | 5 | pending |
| line-1 | line-1-0614-0652-s009493 | reverse | revenue | 5 | pending |
| line-1 | line-1-0628-0562-s011409 | forward | revenue | 5 | pending |
| line-1 | line-1-0628-0562-s011409 | reverse | revenue | 5 | pending |
| line-1 | line-1-0642-0471-s013345 | forward | revenue | 5 | pending |
| line-1 | line-1-0642-0471-s013345 | reverse | revenue | 5 | pending |
| line-1 | line-1-0658-0370-s015498 | forward | revenue | 5 | pending |
| line-1 | line-1-0658-0370-s015498 | reverse | revenue | 5 | pending |
| line-1 | line-1-0689-0101-s022168 | reverse | revenue | 5 | pending |
| line-1 | line-1-0595-0777-s006836 | forward | spare | 1 | pending |
| line-1 | line-1-0595-0777-s006836 | reverse | spare | 1 | pending |
| line-1 | line-1-0614-0652-s009493 | forward | spare | 1 | pending |
| line-1 | line-1-0614-0652-s009493 | reverse | spare | 1 | pending |
| line-1 | line-1-0628-0562-s011409 | forward | spare | 1 | pending |
| line-1 | line-1-0628-0562-s011409 | reverse | spare | 1 | pending |
| line-1 | line-1-0642-0471-s013345 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0377-s005479 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0377-s005479 | reverse | revenue | 5 | pending |
| line-2 | line-2-0642-0471-s008843 | forward | revenue | 5 | pending |
| line-2 | line-2-0642-0471-s008843 | reverse | revenue | 5 | pending |
| line-2 | line-2-0599-0506-s010086 | forward | revenue | 5 | pending |
| line-2 | line-2-0599-0506-s010086 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0550-s011651 | forward | revenue | 5 | pending |
| line-2 | line-2-0546-0550-s011651 | reverse | revenue | 5 | pending |
| line-2 | line-2-0441-0636-s014722 | forward | revenue | 5 | pending |
| line-2 | line-2-0441-0636-s014722 | reverse | revenue | 5 | pending |
| line-2 | line-2-0216-0821-s021340 | reverse | revenue | 5 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0377-s005479 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0377-s005479 | reverse | spare | 1 | pending |
| line-2 | line-2-0642-0471-s008843 | forward | spare | 1 | pending |
| line-2 | line-2-0642-0471-s008843 | reverse | spare | 1 | pending |
| line-2 | line-2-0599-0506-s010086 | forward | spare | 1 | pending |
| line-2 | line-2-0599-0506-s010086 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0669-0844-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0595-0777-s002222 | forward | revenue | 6 | pending |
| line-3 | line-3-0595-0777-s002222 | reverse | revenue | 6 | pending |
| line-3 | line-3-0536-0724-s004017 | forward | revenue | 6 | pending |
| line-3 | line-3-0536-0724-s004017 | reverse | revenue | 5 | pending |
| line-3 | line-3-0439-0637-s006947 | forward | revenue | 5 | pending |
| line-3 | line-3-0439-0637-s006947 | reverse | revenue | 5 | pending |
| line-3 | line-3-0337-0544-s010051 | forward | revenue | 5 | pending |
| line-3 | line-3-0337-0544-s010051 | reverse | revenue | 5 | pending |
| line-3 | line-3-0048-0314-s019373 | reverse | revenue | 5 | pending |
| line-3 | line-3-0536-0724-s004017 | reverse | spare | 1 | pending |
| line-3 | line-3-0439-0637-s006947 | forward | spare | 1 | pending |
| line-3 | line-3-0439-0637-s006947 | reverse | spare | 1 | pending |
| line-3 | line-3-0337-0544-s010051 | forward | spare | 1 | pending |
| line-3 | line-3-0337-0544-s010051 | reverse | spare | 1 | pending |
| line-3 | line-3-0048-0314-s019373 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**143 trainsets exceed the reference platform envelope**, requiring **8,508.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0595-0777-s006836 | 12 | 4 | 8 | 476.0 |
| line-1-0600-1040-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0614-0652-s009493 | 12 | 2 | 10 | 595.0 |
| line-1-0628-0562-s011409 | 12 | 2 | 10 | 595.0 |
| line-1-0642-0471-s013345 | 11 | 4 | 7 | 416.5 |
| line-1-0658-0370-s015498 | 10 | 2 | 8 | 476.0 |
| line-1-0689-0101-s022168 | 5 | 2 | 3 | 178.5 |
| line-2-0216-0821-s021340 | 5 | 2 | 3 | 178.5 |
| line-2-0441-0636-s014722 | 10 | 4 | 6 | 357.0 |
| line-2-0546-0550-s011651 | 10 | 2 | 8 | 476.0 |
| line-2-0599-0506-s010086 | 12 | 2 | 10 | 595.0 |
| line-2-0642-0471-s008843 | 12 | 4 | 8 | 476.0 |
| line-2-0756-0377-s005479 | 12 | 2 | 10 | 595.0 |
| line-2-0897-0226-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0048-0314-s019373 | 6 | 2 | 4 | 238.0 |
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
