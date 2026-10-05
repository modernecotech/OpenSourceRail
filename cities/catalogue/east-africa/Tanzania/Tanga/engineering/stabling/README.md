# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 88 at depots = 132 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1000-0588-s017697 | line-1 | declared-depot | 41 | 2,439.5 | 8 |
| line-2-0603-0186-s000000 | line-2 | declared-depot | 27 | 1,606.5 | 6 |
| line-3-0376-0685-s000000 | line-3 | declared-depot | 20 | 1,190.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0364-0285-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0441-0350-s002289 | station | forward | revenue | 1 |
| line-1 | line-1-0441-0350-s002289 | station | reverse | revenue | 1 |
| line-1 | line-1-0513-0411-s004349 | station | forward | revenue | 1 |
| line-1 | line-1-0513-0411-s004349 | station | reverse | revenue | 1 |
| line-1 | line-1-0577-0465-s006232 | station | forward | revenue | 1 |
| line-1 | line-1-0577-0465-s006232 | station | reverse | revenue | 1 |
| line-1 | line-1-0773-0581-s011977 | station | forward | revenue | 1 |
| line-1 | line-1-0773-0581-s011977 | station | reverse | revenue | 1 |
| line-1 | line-1-1000-0588-s017697 | station | reverse | revenue | 2 |
| line-2 | line-2-0356-0657-s013143 | station | reverse | revenue | 2 |
| line-2 | line-2-0383-0649-s012525 | station | forward | revenue | 1 |
| line-2 | line-2-0383-0649-s012525 | station | reverse | revenue | 1 |
| line-2 | line-2-0411-0589-s011011 | station | forward | revenue | 1 |
| line-2 | line-2-0411-0589-s011011 | station | reverse | revenue | 1 |
| line-2 | line-2-0434-0535-s009668 | station | forward | revenue | 1 |
| line-2 | line-2-0434-0535-s009668 | station | reverse | revenue | 1 |
| line-2 | line-2-0435-0552-s010073 | station | forward | revenue | 1 |
| line-2 | line-2-0435-0552-s010073 | station | reverse | revenue | 1 |
| line-2 | line-2-0466-0483-s008292 | station | forward | revenue | 1 |
| line-2 | line-2-0466-0483-s008292 | station | reverse | revenue | 1 |
| line-2 | line-2-0513-0411-s006434 | station | forward | revenue | 1 |
| line-2 | line-2-0513-0411-s006434 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0186-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0376-0685-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0383-0649-s000778 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0649-s000778 | station | reverse | revenue | 1 |
| line-3 | line-3-0411-0589-s002292 | station | forward | revenue | 1 |
| line-3 | line-3-0411-0589-s002292 | station | reverse | revenue | 1 |
| line-3 | line-3-0422-0445-s005656 | station | forward | revenue | 1 |
| line-3 | line-3-0422-0445-s005656 | station | reverse | revenue | 1 |
| line-3 | line-3-0434-0535-s003596 | station | forward | revenue | 1 |
| line-3 | line-3-0434-0535-s003596 | station | reverse | revenue | 1 |
| line-3 | line-3-0435-0552-s003231 | station | forward | revenue | 1 |
| line-3 | line-3-0435-0552-s003231 | station | reverse | revenue | 1 |
| line-3 | line-3-0441-0350-s007725 | station | forward | revenue | 1 |
| line-3 | line-3-0441-0350-s007725 | station | reverse | revenue | 1 |
| line-3 | line-3-0461-0244-s010011 | station | reverse | revenue | 2 |
| line-1 | line-1-1000-0588-s017697 | depot | — | revenue | 36 |
| line-1 | line-1-1000-0588-s017697 | depot | — | spare | 4 |
| line-1 | line-1-1000-0588-s017697 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0603-0186-s000000 | depot | — | revenue | 23 |
| line-2 | line-2-0603-0186-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0603-0186-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0376-0685-s000000 | depot | — | revenue | 16 |
| line-3 | line-3-0376-0685-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0376-0685-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tanga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **132 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **119 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **88 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0364-0285-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0441-0350-s002289 | forward | revenue | 5 | pending |
| line-1 | line-1-0441-0350-s002289 | reverse | revenue | 5 | pending |
| line-1 | line-1-0513-0411-s004349 | forward | revenue | 5 | pending |
| line-1 | line-1-0513-0411-s004349 | reverse | revenue | 5 | pending |
| line-1 | line-1-0577-0465-s006232 | forward | revenue | 5 | pending |
| line-1 | line-1-0577-0465-s006232 | reverse | revenue | 5 | pending |
| line-1 | line-1-0773-0581-s011977 | forward | revenue | 5 | pending |
| line-1 | line-1-0773-0581-s011977 | reverse | revenue | 4 | pending |
| line-1 | line-1-1000-0588-s017697 | reverse | revenue | 4 | pending |
| line-1 | line-1-0773-0581-s011977 | reverse | spare | 1 | pending |
| line-1 | line-1-1000-0588-s017697 | reverse | spare | 1 | pending |
| line-1 | line-1-0364-0285-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0441-0350-s002289 | forward | spare | 1 | pending |
| line-1 | line-1-0441-0350-s002289 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0603-0186-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0411-s006434 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0411-s006434 | reverse | revenue | 3 | pending |
| line-2 | line-2-0466-0483-s008292 | forward | revenue | 3 | pending |
| line-2 | line-2-0466-0483-s008292 | reverse | revenue | 3 | pending |
| line-2 | line-2-0434-0535-s009668 | forward | revenue | 3 | pending |
| line-2 | line-2-0434-0535-s009668 | reverse | revenue | 3 | pending |
| line-2 | line-2-0435-0552-s010073 | forward | revenue | 3 | pending |
| line-2 | line-2-0435-0552-s010073 | reverse | revenue | 3 | pending |
| line-2 | line-2-0411-0589-s011011 | forward | revenue | 3 | pending |
| line-2 | line-2-0411-0589-s011011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0383-0649-s012525 | forward | revenue | 2 | pending |
| line-2 | line-2-0383-0649-s012525 | reverse | revenue | 2 | pending |
| line-2 | line-2-0356-0657-s013143 | reverse | revenue | 2 | pending |
| line-2 | line-2-0383-0649-s012525 | forward | spare | 1 | pending |
| line-2 | line-2-0383-0649-s012525 | reverse | spare | 1 | pending |
| line-2 | line-2-0356-0657-s013143 | reverse | spare | 1 | pending |
| line-2 | line-2-0603-0186-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0376-0685-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0383-0649-s000778 | forward | revenue | 3 | pending |
| line-3 | line-3-0383-0649-s000778 | reverse | revenue | 3 | pending |
| line-3 | line-3-0411-0589-s002292 | forward | revenue | 3 | pending |
| line-3 | line-3-0411-0589-s002292 | reverse | revenue | 2 | pending |
| line-3 | line-3-0435-0552-s003231 | forward | revenue | 2 | pending |
| line-3 | line-3-0435-0552-s003231 | reverse | revenue | 2 | pending |
| line-3 | line-3-0434-0535-s003596 | forward | revenue | 2 | pending |
| line-3 | line-3-0434-0535-s003596 | reverse | revenue | 2 | pending |
| line-3 | line-3-0422-0445-s005656 | forward | revenue | 2 | pending |
| line-3 | line-3-0422-0445-s005656 | reverse | revenue | 2 | pending |
| line-3 | line-3-0441-0350-s007725 | forward | revenue | 2 | pending |
| line-3 | line-3-0441-0350-s007725 | reverse | revenue | 2 | pending |
| line-3 | line-3-0461-0244-s010011 | reverse | revenue | 2 | pending |
| line-3 | line-3-0411-0589-s002292 | reverse | spare | 1 | pending |
| line-3 | line-3-0435-0552-s003231 | forward | spare | 1 | pending |
| line-3 | line-3-0435-0552-s003231 | reverse | spare | 1 | pending |
| line-3 | line-3-0434-0535-s003596 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**64 trainsets exceed the reference platform envelope**, requiring **3,808.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0364-0285-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0441-0350-s002289 | 12 | 4 | 8 | 476.0 |
| line-1-0513-0411-s004349 | 10 | 4 | 6 | 357.0 |
| line-1-0577-0465-s006232 | 10 | 2 | 8 | 476.0 |
| line-1-0773-0581-s011977 | 10 | 2 | 8 | 476.0 |
| line-1-1000-0588-s017697 | 5 | 2 | 3 | 178.5 |
| line-2-0356-0657-s013143 | 3 | 2 | 1 | 59.5 |
| line-2-0383-0649-s012525 | 6 | 4 | 2 | 119.0 |
| line-2-0411-0589-s011011 | 6 | 4 | 2 | 119.0 |
| line-2-0434-0535-s009668 | 6 | 4 | 2 | 119.0 |
| line-2-0435-0552-s010073 | 6 | 4 | 2 | 119.0 |
| line-2-0466-0483-s008292 | 6 | 2 | 4 | 238.0 |
| line-2-0513-0411-s006434 | 6 | 4 | 2 | 119.0 |
| line-2-0603-0186-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0376-0685-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0383-0649-s000778 | 6 | 4 | 2 | 119.0 |
| line-3-0411-0589-s002292 | 6 | 4 | 2 | 119.0 |
| line-3-0422-0445-s005656 | 4 | 2 | 2 | 119.0 |
| line-3-0434-0535-s003596 | 5 | 4 | 1 | 59.5 |
| line-3-0435-0552-s003231 | 6 | 4 | 2 | 119.0 |
| line-3-0441-0350-s007725 | 4 | 4 | 0 | 0.0 |
| line-3-0461-0244-s010011 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
