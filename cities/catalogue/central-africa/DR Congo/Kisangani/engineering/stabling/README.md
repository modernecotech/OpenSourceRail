# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **33 trainsets at stations + 25 at depots = 58 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0931-1133-s022215 | line-1 | declared-depot | 23 | 1,955.0 | 7 |
| line-2-0746-0719-s000559 | line-2 | declared-depot | 2 | 170.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0560-0244-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0650-0503-s007017 | station | forward | revenue | 1 |
| line-1 | line-1-0650-0503-s007017 | station | reverse | revenue | 1 |
| line-1 | line-1-0746-0719-s012226 | station | forward | revenue | 1 |
| line-1 | line-1-0746-0719-s012226 | station | reverse | revenue | 1 |
| line-1 | line-1-0800-0839-s015121 | station | forward | revenue | 1 |
| line-1 | line-1-0800-0839-s015121 | station | reverse | revenue | 1 |
| line-1 | line-1-0805-0849-s015374 | station | forward | revenue | 1 |
| line-1 | line-1-0805-0849-s015374 | station | reverse | revenue | 1 |
| line-1 | line-1-0806-0852-s015442 | station | forward | revenue | 1 |
| line-1 | line-1-0806-0852-s015442 | station | reverse | revenue | 1 |
| line-1 | line-1-0808-0857-s015559 | station | forward | revenue | 1 |
| line-1 | line-1-0808-0857-s015559 | station | reverse | revenue | 1 |
| line-1 | line-1-0809-0860-s015627 | station | forward | revenue | 1 |
| line-1 | line-1-0809-0860-s015627 | station | reverse | revenue | 1 |
| line-1 | line-1-0811-0864-s015723 | station | forward | revenue | 1 |
| line-1 | line-1-0811-0864-s015723 | station | reverse | revenue | 1 |
| line-1 | line-1-0812-0867-s015792 | station | forward | revenue | 1 |
| line-1 | line-1-0812-0867-s015792 | station | reverse | revenue | 1 |
| line-1 | line-1-0841-0930-s017327 | station | forward | revenue | 1 |
| line-1 | line-1-0841-0930-s017327 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s022215 | station | reverse | revenue | 2 |
| line-2 | line-2-0694-0819-s003014 | station | forward | revenue | 1 |
| line-2 | line-2-0723-0858-s004886 | station | forward | revenue | 1 |
| line-2 | line-2-0746-0719-s000559 | station | forward | revenue | 1 |
| line-2 | line-2-0800-0839-s006779 | station | forward | revenue | 1 |
| line-2 | line-2-0805-0849-s007032 | station | forward | revenue | 1 |
| line-2 | line-2-0806-0852-s007100 | station | forward | revenue | 1 |
| line-2 | line-2-0808-0857-s007217 | station | reverse | revenue | 1 |
| line-2 | line-2-0809-0860-s007285 | station | reverse | revenue | 1 |
| line-2 | line-2-0811-0864-s007382 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s022215 | depot | — | revenue | 18 |
| line-1 | line-1-0931-1133-s022215 | depot | — | spare | 4 |
| line-1 | line-1-0931-1133-s022215 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0746-0719-s000559 | depot | — | spare | 1 |
| line-2 | line-2-0746-0719-s000559 | depot | — | cold_reserve | 1 |

Native hybrid candidate unavailable: morning station allocation is incomplete.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **58 trainsets at 23 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **51 revenue, 5 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **12 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0560-0244-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0650-0503-s007017 | forward | revenue | 2 | pending |
| line-1 | line-1-0650-0503-s007017 | reverse | revenue | 2 | pending |
| line-1 | line-1-0746-0719-s012226 | forward | revenue | 2 | pending |
| line-1 | line-1-0746-0719-s012226 | reverse | revenue | 2 | pending |
| line-1 | line-1-0800-0839-s015121 | forward | revenue | 2 | pending |
| line-1 | line-1-0800-0839-s015121 | reverse | revenue | 2 | pending |
| line-1 | line-1-0805-0849-s015374 | forward | revenue | 2 | pending |
| line-1 | line-1-0805-0849-s015374 | reverse | revenue | 2 | pending |
| line-1 | line-1-0806-0852-s015442 | forward | revenue | 2 | pending |
| line-1 | line-1-0806-0852-s015442 | reverse | revenue | 2 | pending |
| line-1 | line-1-0808-0857-s015559 | forward | revenue | 2 | pending |
| line-1 | line-1-0808-0857-s015559 | reverse | revenue | 2 | pending |
| line-1 | line-1-0809-0860-s015627 | forward | revenue | 2 | pending |
| line-1 | line-1-0809-0860-s015627 | reverse | revenue | 2 | pending |
| line-1 | line-1-0811-0864-s015723 | forward | revenue | 2 | pending |
| line-1 | line-1-0811-0864-s015723 | reverse | revenue | 2 | pending |
| line-1 | line-1-0812-0867-s015792 | forward | revenue | 2 | pending |
| line-1 | line-1-0812-0867-s015792 | reverse | revenue | 2 | pending |
| line-1 | line-1-0841-0930-s017327 | forward | revenue | 2 | pending |
| line-1 | line-1-0841-0930-s017327 | reverse | revenue | 1 | pending |
| line-1 | line-1-0931-1133-s022215 | reverse | revenue | 1 | pending |
| line-1 | line-1-0841-0930-s017327 | reverse | spare | 1 | pending |
| line-1 | line-1-0931-1133-s022215 | reverse | spare | 1 | pending |
| line-1 | line-1-0560-0244-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0650-0503-s007017 | forward | spare | 1 | pending |
| line-1 | line-1-0650-0503-s007017 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0746-0719-s000559 | forward | revenue | 1 | pending |
| line-2 | line-2-0694-0819-s003014 | forward | revenue | 1 | pending |
| line-2 | line-2-0723-0858-s004886 | forward | revenue | 1 | pending |
| line-2 | line-2-0800-0839-s006779 | forward | revenue | 1 | pending |
| line-2 | line-2-0805-0849-s007032 | forward | revenue | 1 | pending |
| line-2 | line-2-0806-0852-s007100 | forward | revenue | 1 | pending |
| line-2 | line-2-0808-0857-s007217 | reverse | revenue | 1 | pending |
| line-2 | line-2-0809-0860-s007285 | reverse | revenue | 1 | pending |
| line-2 | line-2-0811-0864-s007382 | reverse | revenue | 1 | pending |
| line-2 | line-2-0812-0867-s007450 | reverse | spare | 1 | pending |
| line-2 | line-2-0850-0826-s009034 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**7 trainsets exceed the reference platform envelope**, requiring **595.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0560-0244-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0650-0503-s007017 | 6 | 2 | 4 | 340.0 |
| line-1-0746-0719-s012226 | 4 | 4 | 0 | 0.0 |
| line-1-0800-0839-s015121 | 4 | 4 | 0 | 0.0 |
| line-1-0805-0849-s015374 | 4 | 4 | 0 | 0.0 |
| line-1-0806-0852-s015442 | 4 | 4 | 0 | 0.0 |
| line-1-0808-0857-s015559 | 4 | 4 | 0 | 0.0 |
| line-1-0809-0860-s015627 | 4 | 4 | 0 | 0.0 |
| line-1-0811-0864-s015723 | 4 | 4 | 0 | 0.0 |
| line-1-0812-0867-s015792 | 4 | 4 | 0 | 0.0 |
| line-1-0841-0930-s017327 | 4 | 2 | 2 | 170.0 |
| line-1-0931-1133-s022215 | 2 | 2 | 0 | 0.0 |
| line-2-0694-0819-s003014 | 1 | 2 | 0 | 0.0 |
| line-2-0723-0858-s004886 | 1 | 2 | 0 | 0.0 |
| line-2-0746-0719-s000559 | 1 | 4 | 0 | 0.0 |
| line-2-0800-0839-s006779 | 1 | 4 | 0 | 0.0 |
| line-2-0805-0849-s007032 | 1 | 4 | 0 | 0.0 |
| line-2-0806-0852-s007100 | 1 | 4 | 0 | 0.0 |
| line-2-0808-0857-s007217 | 1 | 4 | 0 | 0.0 |
| line-2-0809-0860-s007285 | 1 | 4 | 0 | 0.0 |
| line-2-0811-0864-s007382 | 1 | 4 | 0 | 0.0 |
| line-2-0812-0867-s007450 | 1 | 4 | 0 | 0.0 |
| line-2-0850-0826-s009034 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kisangani/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
