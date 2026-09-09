# Station and depot overnight allocation

Plan: **20 trainsets at stations + 29 at depots = 49 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0707-0423-s012342 | 29 | 1,421.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0381-0373-s003463 | station | forward | revenue | 1 |
| line-1 | line-1-0381-0373-s003463 | station | reverse | revenue | 1 |
| line-1 | line-1-0425-0237-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0463-0411-s006024 | station | forward | revenue | 1 |
| line-1 | line-1-0463-0411-s006024 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0423-s012342 | station | reverse | revenue | 2 |
| line-2 | line-2-0367-0469-s003929 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0373-s001575 | station | forward | revenue | 1 |
| line-2 | line-2-0381-0373-s001575 | station | reverse | revenue | 1 |
| line-2 | line-2-0418-0315-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0381-0373-s002852 | station | forward | revenue | 1 |
| line-3 | line-3-0381-0373-s002852 | station | reverse | revenue | 1 |
| line-3 | line-3-0391-0244-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0396-0442-s004879 | station | reverse | revenue | 2 |
| line-1 | line-1-0707-0423-s012342 | depot | — | revenue | 14 |
| line-1 | line-1-0707-0423-s012342 | depot | — | spare | 2 |
| line-1 | line-1-0707-0423-s012342 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0707-0423-s012342 | depot | — | revenue | 4 |
| line-2 | line-1-0707-0423-s012342 | depot | — | spare | 1 |
| line-2 | line-1-0707-0423-s012342 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0707-0423-s012342 | depot | — | revenue | 4 |
| line-3 | line-1-0707-0423-s012342 | depot | — | spare | 1 |
| line-3 | line-1-0707-0423-s012342 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (6 trains), line-3 (6 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **49 trainsets at 10 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **42 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **29 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0425-0237-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0381-0373-s003463 | forward | revenue | 4 | pending |
| line-1 | line-1-0381-0373-s003463 | reverse | revenue | 4 | pending |
| line-1 | line-1-0463-0411-s006024 | forward | revenue | 4 | pending |
| line-1 | line-1-0463-0411-s006024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0707-0423-s012342 | reverse | revenue | 3 | pending |
| line-1 | line-1-0463-0411-s006024 | reverse | spare | 1 | pending |
| line-1 | line-1-0707-0423-s012342 | reverse | spare | 1 | pending |
| line-1 | line-1-0425-0237-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0381-0373-s001575 | forward | revenue | 3 | pending |
| line-2 | line-2-0381-0373-s001575 | reverse | revenue | 2 | pending |
| line-2 | line-2-0367-0469-s003929 | reverse | revenue | 2 | pending |
| line-2 | line-2-0381-0373-s001575 | reverse | spare | 1 | pending |
| line-2 | line-2-0367-0469-s003929 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0391-0244-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0381-0373-s002852 | forward | revenue | 3 | pending |
| line-3 | line-3-0381-0373-s002852 | reverse | revenue | 2 | pending |
| line-3 | line-3-0396-0442-s004879 | reverse | revenue | 2 | pending |
| line-3 | line-3-0381-0373-s002852 | reverse | spare | 1 | pending |
| line-3 | line-3-0396-0442-s004879 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**23 trainsets exceed the reference platform envelope**, requiring **1,127.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0381-0373-s003463 | 8 | 4 | 4 | 196.0 |
| line-1-0425-0237-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0463-0411-s006024 | 8 | 2 | 6 | 294.0 |
| line-1-0707-0423-s012342 | 4 | 2 | 2 | 98.0 |
| line-2-0367-0469-s003929 | 3 | 2 | 1 | 49.0 |
| line-2-0381-0373-s001575 | 6 | 4 | 2 | 98.0 |
| line-2-0418-0315-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0381-0373-s002852 | 6 | 4 | 2 | 98.0 |
| line-3-0391-0244-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0396-0442-s004879 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tabora/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
