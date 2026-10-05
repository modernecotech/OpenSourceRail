# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **18 trainsets at stations + 25 at depots = 43 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0931-1133-s021735 | line-1 | declared-depot | 23 | 1,955.0 | 5 |
| line-2-0758-0696-s000000 | line-2 | declared-depot | 2 | 170.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0560-0242-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0656-0516-s006848 | station | forward | revenue | 1 |
| line-1 | line-1-0656-0516-s006848 | station | reverse | revenue | 1 |
| line-1 | line-1-0746-0719-s011747 | station | forward | revenue | 1 |
| line-1 | line-1-0746-0719-s011747 | station | reverse | revenue | 1 |
| line-1 | line-1-0800-0839-s014641 | station | forward | revenue | 1 |
| line-1 | line-1-0800-0839-s014641 | station | reverse | revenue | 1 |
| line-1 | line-1-0841-0930-s016848 | station | forward | revenue | 1 |
| line-1 | line-1-0841-0930-s016848 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s021735 | station | reverse | revenue | 2 |
| line-2 | line-2-0694-0819-s003014 | station | reverse | revenue | 1 |
| line-2 | line-2-0723-0858-s004886 | station | forward | revenue | 1 |
| line-2 | line-2-0758-0696-s000000 | station | forward | revenue | 1 |
| line-2 | line-2-0758-0696-s000000 | station | reverse | revenue | 1 |
| line-2 | line-2-0800-0839-s006779 | station | forward | revenue | 1 |
| line-2 | line-2-0800-0839-s006779 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s021735 | depot | — | revenue | 19 |
| line-1 | line-1-0931-1133-s021735 | depot | — | spare | 3 |
| line-1 | line-1-0931-1133-s021735 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0758-0696-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0758-0696-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate unavailable: morning station allocation is incomplete.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **43 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **37 revenue, 4 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **19 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **6 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0560-0242-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0656-0516-s006848 | forward | revenue | 3 | pending |
| line-1 | line-1-0656-0516-s006848 | reverse | revenue | 3 | pending |
| line-1 | line-1-0746-0719-s011747 | forward | revenue | 3 | pending |
| line-1 | line-1-0746-0719-s011747 | reverse | revenue | 3 | pending |
| line-1 | line-1-0800-0839-s014641 | forward | revenue | 3 | pending |
| line-1 | line-1-0800-0839-s014641 | reverse | revenue | 3 | pending |
| line-1 | line-1-0841-0930-s016848 | forward | revenue | 3 | pending |
| line-1 | line-1-0841-0930-s016848 | reverse | revenue | 3 | pending |
| line-1 | line-1-0931-1133-s021735 | reverse | revenue | 3 | pending |
| line-1 | line-1-0656-0516-s006848 | forward | spare | 1 | pending |
| line-1 | line-1-0656-0516-s006848 | reverse | spare | 1 | pending |
| line-1 | line-1-0746-0719-s011747 | forward | spare | 1 | pending |
| line-1 | line-1-0746-0719-s011747 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0758-0696-s000000 | forward | revenue | 1 | pending |
| line-2 | line-2-0758-0696-s000000 | reverse | revenue | 1 | pending |
| line-2 | line-2-0694-0819-s003014 | reverse | revenue | 1 | pending |
| line-2 | line-2-0723-0858-s004886 | forward | revenue | 1 | pending |
| line-2 | line-2-0800-0839-s006779 | forward | revenue | 1 | pending |
| line-2 | line-2-0800-0839-s006779 | reverse | revenue | 1 | pending |
| line-2 | line-2-0863-0829-s009043 | reverse | spare | 1 | pending |
| line-2 | line-2-0837-0706-s012045 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**19 trainsets exceed the reference platform envelope**, requiring **1,615.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0560-0242-s000000 | 4 | 2 | 2 | 170.0 |
| line-1-0656-0516-s006848 | 8 | 2 | 6 | 510.0 |
| line-1-0746-0719-s011747 | 8 | 4 | 4 | 340.0 |
| line-1-0800-0839-s014641 | 6 | 4 | 2 | 170.0 |
| line-1-0841-0930-s016848 | 6 | 2 | 4 | 340.0 |
| line-1-0931-1133-s021735 | 3 | 2 | 1 | 85.0 |
| line-2-0694-0819-s003014 | 1 | 2 | 0 | 0.0 |
| line-2-0723-0858-s004886 | 1 | 2 | 0 | 0.0 |
| line-2-0758-0696-s000000 | 2 | 4 | 0 | 0.0 |
| line-2-0800-0839-s006779 | 2 | 4 | 0 | 0.0 |
| line-2-0837-0706-s012045 | 1 | 2 | 0 | 0.0 |
| line-2-0863-0829-s009043 | 1 | 2 | 0 | 0.0 |

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
