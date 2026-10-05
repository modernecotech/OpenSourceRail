# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 99 at depots = 125 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0423-0728-s000000 | line-1 | declared-depot | 22 | 1,309.0 | 5 |
| line-2-0699-0615-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0486-1078-s020209 | line-3 | declared-depot | 53 | 3,153.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0423-0728-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0516-0631-s003003 | station | forward | revenue | 1 |
| line-1 | line-1-0516-0631-s003003 | station | reverse | revenue | 1 |
| line-1 | line-1-0609-0534-s006018 | station | forward | revenue | 1 |
| line-1 | line-1-0609-0534-s006018 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0431-s009207 | station | reverse | revenue | 2 |
| line-2 | line-2-0406-0262-s010284 | station | reverse | revenue | 2 |
| line-2 | line-2-0486-0359-s007459 | station | forward | revenue | 1 |
| line-2 | line-2-0486-0359-s007459 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0456-s004625 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0456-s004625 | station | reverse | revenue | 1 |
| line-2 | line-2-0613-0512-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0613-0512-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0699-0615-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0289-0190-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0410-0463-s006985 | station | forward | revenue | 1 |
| line-3 | line-3-0410-0463-s006985 | station | reverse | revenue | 1 |
| line-3 | line-3-0439-0601-s009986 | station | forward | revenue | 1 |
| line-3 | line-3-0439-0601-s009986 | station | reverse | revenue | 1 |
| line-3 | line-3-0486-1078-s020209 | station | reverse | revenue | 2 |
| line-1 | line-1-0423-0728-s000000 | depot | — | revenue | 19 |
| line-1 | line-1-0423-0728-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0423-0728-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0699-0615-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0699-0615-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0699-0615-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0486-1078-s020209 | depot | — | revenue | 47 |
| line-3 | line-3-0486-1078-s020209 | depot | — | spare | 5 |
| line-3 | line-3-0486-1078-s020209 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/herat-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **125 trainsets at 13 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **112 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **99 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0423-0728-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0516-0631-s003003 | forward | revenue | 5 | pending |
| line-1 | line-1-0516-0631-s003003 | reverse | revenue | 5 | pending |
| line-1 | line-1-0609-0534-s006018 | forward | revenue | 4 | pending |
| line-1 | line-1-0609-0534-s006018 | reverse | revenue | 4 | pending |
| line-1 | line-1-0707-0431-s009207 | reverse | revenue | 4 | pending |
| line-1 | line-1-0609-0534-s006018 | forward | spare | 1 | pending |
| line-1 | line-1-0609-0534-s006018 | reverse | spare | 1 | pending |
| line-1 | line-1-0707-0431-s009207 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0613-0512-s003018 | forward | revenue | 4 | pending |
| line-2 | line-2-0613-0512-s003018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0567-0456-s004625 | forward | revenue | 4 | pending |
| line-2 | line-2-0567-0456-s004625 | reverse | revenue | 4 | pending |
| line-2 | line-2-0486-0359-s007459 | forward | revenue | 4 | pending |
| line-2 | line-2-0486-0359-s007459 | reverse | revenue | 3 | pending |
| line-2 | line-2-0406-0262-s010284 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0359-s007459 | reverse | spare | 1 | pending |
| line-2 | line-2-0406-0262-s010284 | reverse | spare | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0613-0512-s003018 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | revenue | 10 | pending |
| line-3 | line-3-0410-0463-s006985 | forward | revenue | 9 | pending |
| line-3 | line-3-0410-0463-s006985 | reverse | revenue | 9 | pending |
| line-3 | line-3-0439-0601-s009986 | forward | revenue | 9 | pending |
| line-3 | line-3-0439-0601-s009986 | reverse | revenue | 9 | pending |
| line-3 | line-3-0486-1078-s020209 | reverse | revenue | 9 | pending |
| line-3 | line-3-0410-0463-s006985 | forward | spare | 1 | pending |
| line-3 | line-3-0410-0463-s006985 | reverse | spare | 1 | pending |
| line-3 | line-3-0439-0601-s009986 | forward | spare | 1 | pending |
| line-3 | line-3-0439-0601-s009986 | reverse | spare | 1 | pending |
| line-3 | line-3-0486-1078-s020209 | reverse | spare | 1 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0423-0728-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0516-0631-s003003 | 10 | 2 | 8 | 476.0 |
| line-1-0609-0534-s006018 | 10 | 4 | 6 | 357.0 |
| line-1-0707-0431-s009207 | 5 | 2 | 3 | 178.5 |
| line-2-0406-0262-s010284 | 4 | 2 | 2 | 119.0 |
| line-2-0486-0359-s007459 | 8 | 2 | 6 | 357.0 |
| line-2-0567-0456-s004625 | 8 | 2 | 6 | 357.0 |
| line-2-0613-0512-s003018 | 9 | 4 | 5 | 297.5 |
| line-2-0699-0615-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0289-0190-s000000 | 11 | 2 | 9 | 535.5 |
| line-3-0410-0463-s006985 | 20 | 2 | 18 | 1,071.0 |
| line-3-0439-0601-s009986 | 20 | 2 | 18 | 1,071.0 |
| line-3-0486-1078-s020209 | 10 | 2 | 8 | 476.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Herat/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
