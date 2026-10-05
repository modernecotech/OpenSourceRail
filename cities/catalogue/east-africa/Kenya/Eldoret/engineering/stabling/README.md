# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 139 at depots = 167 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0733-0710-s000000 | line-1 | declared-depot | 51 | 3,034.5 | 9 |
| line-2-0456-0775-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 6 |
| line-3-0601-0747-s020373 | line-3 | declared-depot | 55 | 3,272.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0160-0039-s020074 | station | reverse | revenue | 2 |
| line-1 | line-1-0446-0422-s009063 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0422-s009063 | station | reverse | revenue | 1 |
| line-1 | line-1-0562-0539-s005504 | station | forward | revenue | 1 |
| line-1 | line-1-0562-0539-s005504 | station | reverse | revenue | 1 |
| line-1 | line-1-0637-0614-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0637-0614-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0733-0710-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0456-0775-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0515-0653-s003011 | station | forward | revenue | 1 |
| line-2 | line-2-0515-0653-s003011 | station | reverse | revenue | 1 |
| line-2 | line-2-0560-0559-s005310 | station | forward | revenue | 1 |
| line-2 | line-2-0560-0559-s005310 | station | reverse | revenue | 1 |
| line-2 | line-2-0606-0464-s007650 | station | forward | revenue | 1 |
| line-2 | line-2-0606-0464-s007650 | station | reverse | revenue | 1 |
| line-2 | line-2-0730-0215-s013798 | station | reverse | revenue | 2 |
| line-3 | line-3-0056-0021-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0414-0520-s013803 | station | forward | revenue | 1 |
| line-3 | line-3-0414-0520-s013803 | station | reverse | revenue | 1 |
| line-3 | line-3-0499-0624-s016810 | station | forward | revenue | 1 |
| line-3 | line-3-0499-0624-s016810 | station | reverse | revenue | 1 |
| line-3 | line-3-0601-0747-s020373 | station | reverse | revenue | 2 |
| line-1 | line-1-0733-0710-s000000 | depot | — | revenue | 45 |
| line-1 | line-1-0733-0710-s000000 | depot | — | spare | 5 |
| line-1 | line-1-0733-0710-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0456-0775-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0456-0775-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0456-0775-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0601-0747-s020373 | depot | — | revenue | 49 |
| line-3 | line-3-0601-0747-s020373 | depot | — | spare | 5 |
| line-3 | line-3-0601-0747-s020373 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/eldoret-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **167 trainsets at 14 stations**; largest initial station queue **22**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **151 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **139 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0733-0710-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0637-0614-s003020 | forward | revenue | 7 | pending |
| line-1 | line-1-0637-0614-s003020 | reverse | revenue | 7 | pending |
| line-1 | line-1-0562-0539-s005504 | forward | revenue | 7 | pending |
| line-1 | line-1-0562-0539-s005504 | reverse | revenue | 7 | pending |
| line-1 | line-1-0446-0422-s009063 | forward | revenue | 7 | pending |
| line-1 | line-1-0446-0422-s009063 | reverse | revenue | 7 | pending |
| line-1 | line-1-0160-0039-s020074 | reverse | revenue | 6 | pending |
| line-1 | line-1-0160-0039-s020074 | reverse | spare | 1 | pending |
| line-1 | line-1-0733-0710-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0637-0614-s003020 | forward | spare | 1 | pending |
| line-1 | line-1-0637-0614-s003020 | reverse | spare | 1 | pending |
| line-1 | line-1-0562-0539-s005504 | forward | spare | 1 | pending |
| line-1 | line-1-0562-0539-s005504 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0456-0775-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0515-0653-s003011 | forward | revenue | 5 | pending |
| line-2 | line-2-0515-0653-s003011 | reverse | revenue | 5 | pending |
| line-2 | line-2-0560-0559-s005310 | forward | revenue | 5 | pending |
| line-2 | line-2-0560-0559-s005310 | reverse | revenue | 5 | pending |
| line-2 | line-2-0606-0464-s007650 | forward | revenue | 5 | pending |
| line-2 | line-2-0606-0464-s007650 | reverse | revenue | 5 | pending |
| line-2 | line-2-0730-0215-s013798 | reverse | revenue | 4 | pending |
| line-2 | line-2-0730-0215-s013798 | reverse | spare | 1 | pending |
| line-2 | line-2-0456-0775-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0515-0653-s003011 | forward | spare | 1 | pending |
| line-2 | line-2-0515-0653-s003011 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0056-0021-s000000 | forward | revenue | 10 | pending |
| line-3 | line-3-0414-0520-s013803 | forward | revenue | 10 | pending |
| line-3 | line-3-0414-0520-s013803 | reverse | revenue | 10 | pending |
| line-3 | line-3-0499-0624-s016810 | forward | revenue | 9 | pending |
| line-3 | line-3-0499-0624-s016810 | reverse | revenue | 9 | pending |
| line-3 | line-3-0601-0747-s020373 | reverse | revenue | 9 | pending |
| line-3 | line-3-0499-0624-s016810 | forward | spare | 1 | pending |
| line-3 | line-3-0499-0624-s016810 | reverse | spare | 1 | pending |
| line-3 | line-3-0601-0747-s020373 | reverse | spare | 1 | pending |
| line-3 | line-3-0056-0021-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0414-0520-s013803 | forward | spare | 1 | pending |
| line-3 | line-3-0414-0520-s013803 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**131 trainsets exceed the reference platform envelope**, requiring **7,794.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0160-0039-s020074 | 7 | 2 | 5 | 297.5 |
| line-1-0446-0422-s009063 | 14 | 2 | 12 | 714.0 |
| line-1-0562-0539-s005504 | 16 | 4 | 12 | 714.0 |
| line-1-0637-0614-s003020 | 16 | 2 | 14 | 833.0 |
| line-1-0733-0710-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0456-0775-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0515-0653-s003011 | 12 | 4 | 8 | 476.0 |
| line-2-0560-0559-s005310 | 10 | 4 | 6 | 357.0 |
| line-2-0606-0464-s007650 | 10 | 2 | 8 | 476.0 |
| line-2-0730-0215-s013798 | 5 | 2 | 3 | 178.5 |
| line-3-0056-0021-s000000 | 11 | 2 | 9 | 535.5 |
| line-3-0414-0520-s013803 | 22 | 2 | 20 | 1,190.0 |
| line-3-0499-0624-s016810 | 20 | 4 | 16 | 952.0 |
| line-3-0601-0747-s020373 | 10 | 2 | 8 | 476.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Eldoret/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
