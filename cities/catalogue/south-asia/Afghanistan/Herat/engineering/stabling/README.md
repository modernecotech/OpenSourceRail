# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 90 at depots = 124 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0423-0728-s000000 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0699-0615-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0486-1078-s020683 | line-3 | declared-depot | 47 | 2,796.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0423-0728-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0458-0692-s001127 | station | forward | revenue | 1 |
| line-1 | line-1-0458-0692-s001127 | station | reverse | revenue | 1 |
| line-1 | line-1-0516-0631-s003003 | station | forward | revenue | 1 |
| line-1 | line-1-0516-0631-s003003 | station | reverse | revenue | 1 |
| line-1 | line-1-0621-0521-s006401 | station | forward | revenue | 1 |
| line-1 | line-1-0621-0521-s006401 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0431-s009207 | station | reverse | revenue | 2 |
| line-2 | line-2-0406-0262-s010284 | station | reverse | revenue | 2 |
| line-2 | line-2-0486-0359-s007459 | station | forward | revenue | 1 |
| line-2 | line-2-0486-0359-s007459 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0456-s004625 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0456-s004625 | station | reverse | revenue | 1 |
| line-2 | line-2-0621-0521-s002749 | station | forward | revenue | 1 |
| line-2 | line-2-0621-0521-s002749 | station | reverse | revenue | 1 |
| line-2 | line-2-0699-0615-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0289-0190-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0374-0298-s003498 | station | forward | revenue | 1 |
| line-3 | line-3-0374-0298-s003498 | station | reverse | revenue | 1 |
| line-3 | line-3-0409-0459-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0409-0459-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0438-0597-s010020 | station | forward | revenue | 1 |
| line-3 | line-3-0438-0597-s010020 | station | reverse | revenue | 1 |
| line-3 | line-3-0458-0692-s012085 | station | forward | revenue | 1 |
| line-3 | line-3-0458-0692-s012085 | station | reverse | revenue | 1 |
| line-3 | line-3-0486-1078-s020683 | station | reverse | revenue | 2 |
| line-3 | line-3-0506-0887-s016395 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0887-s016395 | station | reverse | revenue | 1 |
| line-1 | line-1-0423-0728-s000000 | depot | — | revenue | 16 |
| line-1 | line-1-0423-0728-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0423-0728-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0699-0615-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0699-0615-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0699-0615-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0486-1078-s020683 | depot | — | revenue | 41 |
| line-3 | line-3-0486-1078-s020683 | depot | — | spare | 5 |
| line-3 | line-3-0486-1078-s020683 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/herat-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **124 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **90 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0423-0728-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0458-0692-s001127 | forward | revenue | 4 | pending |
| line-1 | line-1-0458-0692-s001127 | reverse | revenue | 3 | pending |
| line-1 | line-1-0516-0631-s003003 | forward | revenue | 3 | pending |
| line-1 | line-1-0516-0631-s003003 | reverse | revenue | 3 | pending |
| line-1 | line-1-0621-0521-s006401 | forward | revenue | 3 | pending |
| line-1 | line-1-0621-0521-s006401 | reverse | revenue | 3 | pending |
| line-1 | line-1-0707-0431-s009207 | reverse | revenue | 3 | pending |
| line-1 | line-1-0458-0692-s001127 | reverse | spare | 1 | pending |
| line-1 | line-1-0516-0631-s003003 | forward | spare | 1 | pending |
| line-1 | line-1-0516-0631-s003003 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0621-0521-s002749 | forward | revenue | 4 | pending |
| line-2 | line-2-0621-0521-s002749 | reverse | revenue | 4 | pending |
| line-2 | line-2-0567-0456-s004625 | forward | revenue | 4 | pending |
| line-2 | line-2-0567-0456-s004625 | reverse | revenue | 4 | pending |
| line-2 | line-2-0486-0359-s007459 | forward | revenue | 4 | pending |
| line-2 | line-2-0486-0359-s007459 | reverse | revenue | 3 | pending |
| line-2 | line-2-0406-0262-s010284 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0359-s007459 | reverse | spare | 1 | pending |
| line-2 | line-2-0406-0262-s010284 | reverse | spare | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0621-0521-s002749 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0374-0298-s003498 | forward | revenue | 5 | pending |
| line-3 | line-3-0374-0298-s003498 | reverse | revenue | 5 | pending |
| line-3 | line-3-0409-0459-s007019 | forward | revenue | 5 | pending |
| line-3 | line-3-0409-0459-s007019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0438-0597-s010020 | forward | revenue | 5 | pending |
| line-3 | line-3-0438-0597-s010020 | reverse | revenue | 5 | pending |
| line-3 | line-3-0458-0692-s012085 | forward | revenue | 4 | pending |
| line-3 | line-3-0458-0692-s012085 | reverse | revenue | 4 | pending |
| line-3 | line-3-0506-0887-s016395 | forward | revenue | 4 | pending |
| line-3 | line-3-0506-0887-s016395 | reverse | revenue | 4 | pending |
| line-3 | line-3-0486-1078-s020683 | reverse | revenue | 4 | pending |
| line-3 | line-3-0458-0692-s012085 | forward | spare | 1 | pending |
| line-3 | line-3-0458-0692-s012085 | reverse | spare | 1 | pending |
| line-3 | line-3-0506-0887-s016395 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0887-s016395 | reverse | spare | 1 | pending |
| line-3 | line-3-0486-1078-s020683 | reverse | spare | 1 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**82 trainsets exceed the reference platform envelope**, requiring **4,879.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0423-0728-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0458-0692-s001127 | 8 | 4 | 4 | 238.0 |
| line-1-0516-0631-s003003 | 8 | 2 | 6 | 357.0 |
| line-1-0621-0521-s006401 | 6 | 4 | 2 | 119.0 |
| line-1-0707-0431-s009207 | 3 | 2 | 1 | 59.5 |
| line-2-0406-0262-s010284 | 4 | 2 | 2 | 119.0 |
| line-2-0486-0359-s007459 | 8 | 2 | 6 | 357.0 |
| line-2-0567-0456-s004625 | 8 | 2 | 6 | 357.0 |
| line-2-0621-0521-s002749 | 9 | 4 | 5 | 297.5 |
| line-2-0699-0615-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0289-0190-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0374-0298-s003498 | 10 | 2 | 8 | 476.0 |
| line-3-0409-0459-s007019 | 10 | 2 | 8 | 476.0 |
| line-3-0438-0597-s010020 | 10 | 2 | 8 | 476.0 |
| line-3-0458-0692-s012085 | 10 | 4 | 6 | 357.0 |
| line-3-0486-1078-s020683 | 5 | 2 | 3 | 178.5 |
| line-3-0506-0887-s016395 | 10 | 2 | 8 | 476.0 |

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
