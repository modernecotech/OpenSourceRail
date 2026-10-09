# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 21 at depots = 43 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0373-0475-s004317 | line-1 | declared-depot | 6 | 294.0 | 2 |
| line-2-0227-0358-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0255-0392-s000000 | line-3 | declared-depot | 6 | 294.0 | 2 |
| line-4-0373-0475-s000000 | line-4 | declared-depot | 4 | 196.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0159-0472-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0278-0474-s002408 | station | forward | revenue | 1 |
| line-1 | line-1-0278-0474-s002408 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0475-s004317 | station | reverse | revenue | 2 |
| line-2 | line-2-0227-0358-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0255-0392-s000982 | station | forward | revenue | 1 |
| line-2 | line-2-0255-0392-s000982 | station | reverse | revenue | 1 |
| line-2 | line-2-0306-0456-s002825 | station | reverse | revenue | 2 |
| line-3 | line-3-0255-0392-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0367-0388-s002671 | station | forward | revenue | 1 |
| line-3 | line-3-0367-0388-s002671 | station | reverse | revenue | 1 |
| line-3 | line-3-0438-0413-s004298 | station | reverse | revenue | 2 |
| line-4 | line-4-0373-0475-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0462-0512-s002087 | station | reverse | revenue | 2 |
| line-1 | line-1-0373-0475-s004317 | depot | — | revenue | 4 |
| line-1 | line-1-0373-0475-s004317 | depot | — | spare | 1 |
| line-1 | line-1-0373-0475-s004317 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0227-0358-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0227-0358-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0227-0358-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0255-0392-s000000 | depot | — | revenue | 4 |
| line-3 | line-3-0255-0392-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0255-0392-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0373-0475-s000000 | depot | — | revenue | 2 |
| line-4 | line-4-0373-0475-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0373-0475-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lichinga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **43 trainsets at 11 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **35 revenue, 4 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **21 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0159-0472-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0278-0474-s002408 | forward | revenue | 3 | pending |
| line-1 | line-1-0278-0474-s002408 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0475-s004317 | reverse | revenue | 2 | pending |
| line-1 | line-1-0278-0474-s002408 | reverse | spare | 1 | pending |
| line-1 | line-1-0373-0475-s004317 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0227-0358-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0255-0392-s000982 | forward | revenue | 2 | pending |
| line-2 | line-2-0255-0392-s000982 | reverse | revenue | 2 | pending |
| line-2 | line-2-0306-0456-s002825 | reverse | revenue | 2 | pending |
| line-2 | line-2-0255-0392-s000982 | forward | spare | 1 | pending |
| line-2 | line-2-0255-0392-s000982 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0255-0392-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0367-0388-s002671 | forward | revenue | 3 | pending |
| line-3 | line-3-0367-0388-s002671 | reverse | revenue | 2 | pending |
| line-3 | line-3-0438-0413-s004298 | reverse | revenue | 2 | pending |
| line-3 | line-3-0367-0388-s002671 | reverse | spare | 1 | pending |
| line-3 | line-3-0438-0413-s004298 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0373-0475-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0462-0512-s002087 | reverse | revenue | 3 | pending |
| line-4 | line-4-0373-0475-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0462-0512-s002087 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**19 trainsets exceed the reference platform envelope**, requiring **931.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0159-0472-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0278-0474-s002408 | 6 | 2 | 4 | 196.0 |
| line-1-0373-0475-s004317 | 3 | 2 | 1 | 49.0 |
| line-2-0227-0358-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0255-0392-s000982 | 6 | 4 | 2 | 98.0 |
| line-2-0306-0456-s002825 | 2 | 2 | 0 | 0.0 |
| line-3-0255-0392-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0367-0388-s002671 | 6 | 2 | 4 | 196.0 |
| line-3-0438-0413-s004298 | 3 | 2 | 1 | 49.0 |
| line-4-0373-0475-s000000 | 4 | 2 | 2 | 98.0 |
| line-4-0462-0512-s002087 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Lichinga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
