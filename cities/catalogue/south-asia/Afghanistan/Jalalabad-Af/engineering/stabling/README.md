# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 98 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0798-0565-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0286-0151-s020048 | line-2 | declared-depot | 52 | 3,094.0 | 9 |
| line-3-0320-0781-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0399-0533-s008245 | station | reverse | revenue | 2 |
| line-1 | line-1-0497-0541-s006219 | station | forward | revenue | 1 |
| line-1 | line-1-0497-0541-s006219 | station | reverse | revenue | 1 |
| line-1 | line-1-0594-0549-s004213 | station | forward | revenue | 1 |
| line-1 | line-1-0594-0549-s004213 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0554-s002911 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0554-s002911 | station | reverse | revenue | 1 |
| line-1 | line-1-0798-0565-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0286-0151-s020048 | station | reverse | revenue | 2 |
| line-2 | line-2-0555-0481-s010172 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0481-s010172 | station | reverse | revenue | 1 |
| line-2 | line-2-0594-0549-s008430 | station | forward | revenue | 1 |
| line-2 | line-2-0594-0549-s008430 | station | reverse | revenue | 1 |
| line-2 | line-2-0614-0584-s007544 | station | forward | revenue | 1 |
| line-2 | line-2-0614-0584-s007544 | station | reverse | revenue | 1 |
| line-2 | line-2-0689-0716-s004151 | station | forward | revenue | 1 |
| line-2 | line-2-0689-0716-s004151 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0878-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0320-0781-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0495-0663-s004688 | station | forward | revenue | 1 |
| line-3 | line-3-0495-0663-s004688 | station | reverse | revenue | 1 |
| line-3 | line-3-0614-0584-s007904 | station | forward | revenue | 1 |
| line-3 | line-3-0614-0584-s007904 | station | reverse | revenue | 1 |
| line-3 | line-3-0657-0554-s009066 | station | forward | revenue | 1 |
| line-3 | line-3-0657-0554-s009066 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0482-s011943 | station | reverse | revenue | 2 |
| line-1 | line-1-0798-0565-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0798-0565-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0798-0565-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0286-0151-s020048 | depot | — | revenue | 46 |
| line-2 | line-2-0286-0151-s020048 | depot | — | spare | 5 |
| line-2 | line-2-0286-0151-s020048 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0320-0781-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0320-0781-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0320-0781-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jalalabad-af-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 16 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0798-0565-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0554-s002911 | forward | revenue | 3 | pending |
| line-1 | line-1-0657-0554-s002911 | reverse | revenue | 3 | pending |
| line-1 | line-1-0594-0549-s004213 | forward | revenue | 3 | pending |
| line-1 | line-1-0594-0549-s004213 | reverse | revenue | 3 | pending |
| line-1 | line-1-0497-0541-s006219 | forward | revenue | 3 | pending |
| line-1 | line-1-0497-0541-s006219 | reverse | revenue | 3 | pending |
| line-1 | line-1-0399-0533-s008245 | reverse | revenue | 3 | pending |
| line-1 | line-1-0657-0554-s002911 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0554-s002911 | reverse | spare | 1 | pending |
| line-1 | line-1-0594-0549-s004213 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0689-0716-s004151 | forward | revenue | 6 | pending |
| line-2 | line-2-0689-0716-s004151 | reverse | revenue | 6 | pending |
| line-2 | line-2-0614-0584-s007544 | forward | revenue | 6 | pending |
| line-2 | line-2-0614-0584-s007544 | reverse | revenue | 6 | pending |
| line-2 | line-2-0594-0549-s008430 | forward | revenue | 6 | pending |
| line-2 | line-2-0594-0549-s008430 | reverse | revenue | 6 | pending |
| line-2 | line-2-0555-0481-s010172 | forward | revenue | 6 | pending |
| line-2 | line-2-0555-0481-s010172 | reverse | revenue | 5 | pending |
| line-2 | line-2-0286-0151-s020048 | reverse | revenue | 5 | pending |
| line-2 | line-2-0555-0481-s010172 | reverse | spare | 1 | pending |
| line-2 | line-2-0286-0151-s020048 | reverse | spare | 1 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0689-0716-s004151 | forward | spare | 1 | pending |
| line-2 | line-2-0689-0716-s004151 | reverse | spare | 1 | pending |
| line-2 | line-2-0614-0584-s007544 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0320-0781-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0495-0663-s004688 | forward | revenue | 5 | pending |
| line-3 | line-3-0495-0663-s004688 | reverse | revenue | 4 | pending |
| line-3 | line-3-0614-0584-s007904 | forward | revenue | 4 | pending |
| line-3 | line-3-0614-0584-s007904 | reverse | revenue | 4 | pending |
| line-3 | line-3-0657-0554-s009066 | forward | revenue | 4 | pending |
| line-3 | line-3-0657-0554-s009066 | reverse | revenue | 4 | pending |
| line-3 | line-3-0764-0482-s011943 | reverse | revenue | 4 | pending |
| line-3 | line-3-0495-0663-s004688 | reverse | spare | 1 | pending |
| line-3 | line-3-0614-0584-s007904 | forward | spare | 1 | pending |
| line-3 | line-3-0614-0584-s007904 | reverse | spare | 1 | pending |
| line-3 | line-3-0657-0554-s009066 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0399-0533-s008245 | 3 | 2 | 1 | 59.5 |
| line-1-0497-0541-s006219 | 6 | 2 | 4 | 238.0 |
| line-1-0594-0549-s004213 | 7 | 4 | 3 | 178.5 |
| line-1-0657-0554-s002911 | 8 | 4 | 4 | 238.0 |
| line-1-0798-0565-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0286-0151-s020048 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0481-s010172 | 12 | 2 | 10 | 595.0 |
| line-2-0594-0549-s008430 | 12 | 4 | 8 | 476.0 |
| line-2-0614-0584-s007544 | 13 | 4 | 9 | 535.5 |
| line-2-0689-0716-s004151 | 14 | 2 | 12 | 714.0 |
| line-2-0782-0878-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0320-0781-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0495-0663-s004688 | 10 | 2 | 8 | 476.0 |
| line-3-0614-0584-s007904 | 10 | 4 | 6 | 357.0 |
| line-3-0657-0554-s009066 | 9 | 4 | 5 | 297.5 |
| line-3-0764-0482-s011943 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Jalalabad-Af/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
