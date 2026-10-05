# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 58 at depots = 84 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0549-0917-s012054 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0451-0393-s000000 | line-2 | declared-depot | 15 | 892.5 | 4 |
| line-3-0527-0619-s000000 | line-3 | declared-depot | 15 | 892.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0549-0917-s012054 | station | reverse | revenue | 2 |
| line-1 | line-1-0627-0739-s007754 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0739-s007754 | station | reverse | revenue | 1 |
| line-1 | line-1-0653-0643-s005607 | station | forward | revenue | 1 |
| line-1 | line-1-0653-0643-s005607 | station | reverse | revenue | 1 |
| line-1 | line-1-0680-0547-s003451 | station | forward | revenue | 1 |
| line-1 | line-1-0680-0547-s003451 | station | reverse | revenue | 1 |
| line-1 | line-1-0723-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0451-0393-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0545-0487-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0545-0487-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0609-0550-s004976 | station | forward | revenue | 1 |
| line-2 | line-2-0609-0550-s004976 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0611-s006932 | station | reverse | revenue | 2 |
| line-3 | line-3-0527-0619-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0569-0571-s001413 | station | forward | revenue | 1 |
| line-3 | line-3-0569-0571-s001413 | station | reverse | revenue | 1 |
| line-3 | line-3-0616-0518-s003003 | station | forward | revenue | 1 |
| line-3 | line-3-0616-0518-s003003 | station | reverse | revenue | 1 |
| line-3 | line-3-0720-0400-s006553 | station | reverse | revenue | 2 |
| line-1 | line-1-0549-0917-s012054 | depot | — | revenue | 24 |
| line-1 | line-1-0549-0917-s012054 | depot | — | spare | 3 |
| line-1 | line-1-0549-0917-s012054 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0451-0393-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0451-0393-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0451-0393-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0527-0619-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0527-0619-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0527-0619-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/uyo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **84 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **74 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **58 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0723-0394-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0680-0547-s003451 | forward | revenue | 5 | pending |
| line-1 | line-1-0680-0547-s003451 | reverse | revenue | 4 | pending |
| line-1 | line-1-0653-0643-s005607 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0643-s005607 | reverse | revenue | 4 | pending |
| line-1 | line-1-0627-0739-s007754 | forward | revenue | 4 | pending |
| line-1 | line-1-0627-0739-s007754 | reverse | revenue | 4 | pending |
| line-1 | line-1-0549-0917-s012054 | reverse | revenue | 4 | pending |
| line-1 | line-1-0680-0547-s003451 | reverse | spare | 1 | pending |
| line-1 | line-1-0653-0643-s005607 | forward | spare | 1 | pending |
| line-1 | line-1-0653-0643-s005607 | reverse | spare | 1 | pending |
| line-1 | line-1-0627-0739-s007754 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0393-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0545-0487-s003010 | forward | revenue | 4 | pending |
| line-2 | line-2-0545-0487-s003010 | reverse | revenue | 3 | pending |
| line-2 | line-2-0609-0550-s004976 | forward | revenue | 3 | pending |
| line-2 | line-2-0609-0550-s004976 | reverse | revenue | 3 | pending |
| line-2 | line-2-0671-0611-s006932 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0487-s003010 | reverse | spare | 1 | pending |
| line-2 | line-2-0609-0550-s004976 | forward | spare | 1 | pending |
| line-2 | line-2-0609-0550-s004976 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0527-0619-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0569-0571-s001413 | forward | revenue | 4 | pending |
| line-3 | line-3-0569-0571-s001413 | reverse | revenue | 3 | pending |
| line-3 | line-3-0616-0518-s003003 | forward | revenue | 3 | pending |
| line-3 | line-3-0616-0518-s003003 | reverse | revenue | 3 | pending |
| line-3 | line-3-0720-0400-s006553 | reverse | revenue | 3 | pending |
| line-3 | line-3-0569-0571-s001413 | reverse | spare | 1 | pending |
| line-3 | line-3-0616-0518-s003003 | forward | spare | 1 | pending |
| line-3 | line-3-0616-0518-s003003 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**54 trainsets exceed the reference platform envelope**, requiring **3,213.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0549-0917-s012054 | 4 | 2 | 2 | 119.0 |
| line-1-0627-0739-s007754 | 9 | 2 | 7 | 416.5 |
| line-1-0653-0643-s005607 | 10 | 2 | 8 | 476.0 |
| line-1-0680-0547-s003451 | 10 | 2 | 8 | 476.0 |
| line-1-0723-0394-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0451-0393-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0545-0487-s003010 | 8 | 2 | 6 | 357.0 |
| line-2-0609-0550-s004976 | 8 | 4 | 4 | 238.0 |
| line-2-0671-0611-s006932 | 3 | 2 | 1 | 59.5 |
| line-3-0527-0619-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0569-0571-s001413 | 8 | 2 | 6 | 357.0 |
| line-3-0616-0518-s003003 | 8 | 4 | 4 | 238.0 |
| line-3-0720-0400-s006553 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Uyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
