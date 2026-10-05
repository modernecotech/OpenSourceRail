# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 89 at depots = 115 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0420-0384-s000000 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0571-0334-s000000 | line-2 | declared-depot | 19 | 1,130.5 | 4 |
| line-3-0762-0506-s018506 | line-3 | declared-depot | 51 | 3,034.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0420-0384-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0517-0479-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0517-0479-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0568-0530-s004650 | station | forward | revenue | 1 |
| line-1 | line-1-0568-0530-s004650 | station | reverse | revenue | 1 |
| line-1 | line-1-0639-0600-s006907 | station | forward | revenue | 1 |
| line-1 | line-1-0639-0600-s006907 | station | reverse | revenue | 1 |
| line-1 | line-1-0712-0672-s009187 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0711-s008661 | station | reverse | revenue | 2 |
| line-2 | line-2-0488-0588-s005838 | station | forward | revenue | 1 |
| line-2 | line-2-0488-0588-s005838 | station | reverse | revenue | 1 |
| line-2 | line-2-0528-0466-s003020 | station | forward | revenue | 1 |
| line-2 | line-2-0528-0466-s003020 | station | reverse | revenue | 1 |
| line-2 | line-2-0571-0334-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0164-1077-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0567-0674-s012757 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0674-s012757 | station | reverse | revenue | 1 |
| line-3 | line-3-0664-0590-s015627 | station | forward | revenue | 1 |
| line-3 | line-3-0664-0590-s015627 | station | reverse | revenue | 1 |
| line-3 | line-3-0762-0506-s018506 | station | reverse | revenue | 2 |
| line-1 | line-1-0420-0384-s000000 | depot | — | revenue | 16 |
| line-1 | line-1-0420-0384-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0420-0384-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0571-0334-s000000 | depot | — | revenue | 16 |
| line-2 | line-2-0571-0334-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0571-0334-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0762-0506-s018506 | depot | — | revenue | 45 |
| line-3 | line-3-0762-0506-s018506 | depot | — | spare | 5 |
| line-3 | line-3-0762-0506-s018506 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mymensingh-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **115 trainsets at 13 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **103 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **89 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0420-0384-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0517-0479-s003020 | forward | revenue | 4 | pending |
| line-1 | line-1-0517-0479-s003020 | reverse | revenue | 3 | pending |
| line-1 | line-1-0568-0530-s004650 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0530-s004650 | reverse | revenue | 3 | pending |
| line-1 | line-1-0639-0600-s006907 | forward | revenue | 3 | pending |
| line-1 | line-1-0639-0600-s006907 | reverse | revenue | 3 | pending |
| line-1 | line-1-0712-0672-s009187 | reverse | revenue | 3 | pending |
| line-1 | line-1-0517-0479-s003020 | reverse | spare | 1 | pending |
| line-1 | line-1-0568-0530-s004650 | forward | spare | 1 | pending |
| line-1 | line-1-0568-0530-s004650 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0571-0334-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0528-0466-s003020 | forward | revenue | 4 | pending |
| line-2 | line-2-0528-0466-s003020 | reverse | revenue | 4 | pending |
| line-2 | line-2-0488-0588-s005838 | forward | revenue | 4 | pending |
| line-2 | line-2-0488-0588-s005838 | reverse | revenue | 4 | pending |
| line-2 | line-2-0447-0711-s008661 | reverse | revenue | 4 | pending |
| line-2 | line-2-0571-0334-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0466-s003020 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0466-s003020 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0164-1077-s000000 | forward | revenue | 9 | pending |
| line-3 | line-3-0567-0674-s012757 | forward | revenue | 9 | pending |
| line-3 | line-3-0567-0674-s012757 | reverse | revenue | 9 | pending |
| line-3 | line-3-0664-0590-s015627 | forward | revenue | 9 | pending |
| line-3 | line-3-0664-0590-s015627 | reverse | revenue | 9 | pending |
| line-3 | line-3-0762-0506-s018506 | reverse | revenue | 8 | pending |
| line-3 | line-3-0762-0506-s018506 | reverse | spare | 1 | pending |
| line-3 | line-3-0164-1077-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0567-0674-s012757 | forward | spare | 1 | pending |
| line-3 | line-3-0567-0674-s012757 | reverse | spare | 1 | pending |
| line-3 | line-3-0664-0590-s015627 | forward | spare | 1 | pending |
| line-3 | line-3-0664-0590-s015627 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**81 trainsets exceed the reference platform envelope**, requiring **4,819.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0420-0384-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0517-0479-s003020 | 8 | 4 | 4 | 238.0 |
| line-1-0568-0530-s004650 | 8 | 2 | 6 | 357.0 |
| line-1-0639-0600-s006907 | 6 | 4 | 2 | 119.0 |
| line-1-0712-0672-s009187 | 3 | 2 | 1 | 59.5 |
| line-2-0447-0711-s008661 | 4 | 2 | 2 | 119.0 |
| line-2-0488-0588-s005838 | 8 | 2 | 6 | 357.0 |
| line-2-0528-0466-s003020 | 10 | 4 | 6 | 357.0 |
| line-2-0571-0334-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0164-1077-s000000 | 10 | 2 | 8 | 476.0 |
| line-3-0567-0674-s012757 | 20 | 2 | 18 | 1,071.0 |
| line-3-0664-0590-s015627 | 20 | 4 | 16 | 952.0 |
| line-3-0762-0506-s018506 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Mymensingh/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
