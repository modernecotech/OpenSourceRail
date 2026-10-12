# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **46 trainsets at stations + 78 at depots = 124 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0549-0917-s015830 | line-1 | declared-depot | 35 | 2,082.5 | 8 |
| line-2-0451-0393-s000000 | line-2 | declared-depot | 18 | 1,071.0 | 4 |
| line-3-0527-0619-s000000 | line-3 | declared-depot | 14 | 833.0 | 4 |
| line-4-0618-0615-s000000 | line-4 | declared-depot | 11 | 654.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0549-0917-s015830 | station | reverse | revenue | 2 |
| line-1 | line-1-0550-0571-s006832 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0571-s006832 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0592-s007378 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0592-s007378 | station | reverse | revenue | 1 |
| line-1 | line-1-0577-0563-s006004 | station | forward | revenue | 1 |
| line-1 | line-1-0577-0563-s006004 | station | reverse | revenue | 1 |
| line-1 | line-1-0605-0530-s004887 | station | forward | revenue | 1 |
| line-1 | line-1-0605-0530-s004887 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0747-s011609 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0747-s011609 | station | reverse | revenue | 1 |
| line-1 | line-1-0608-0527-s004802 | station | forward | revenue | 1 |
| line-1 | line-1-0608-0527-s004802 | station | reverse | revenue | 1 |
| line-1 | line-1-0723-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0451-0393-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0550-0571-s005056 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0571-s005056 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0587-s005446 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0587-s005446 | station | reverse | revenue | 1 |
| line-2 | line-2-0618-0615-s007369 | station | forward | revenue | 1 |
| line-2 | line-2-0618-0615-s007369 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0611-s008623 | station | reverse | revenue | 2 |
| line-3 | line-3-0527-0619-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0551-0592-s000786 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0592-s000786 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0587-s000942 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0587-s000942 | station | reverse | revenue | 1 |
| line-3 | line-3-0577-0563-s001675 | station | forward | revenue | 1 |
| line-3 | line-3-0577-0563-s001675 | station | reverse | revenue | 1 |
| line-3 | line-3-0606-0529-s002665 | station | forward | revenue | 1 |
| line-3 | line-3-0606-0529-s002665 | station | reverse | revenue | 1 |
| line-3 | line-3-0608-0527-s002734 | station | forward | revenue | 1 |
| line-3 | line-3-0608-0527-s002734 | station | reverse | revenue | 1 |
| line-3 | line-3-0720-0400-s006553 | station | reverse | revenue | 2 |
| line-4 | line-4-0618-0615-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0688-0711-s003002 | station | forward | revenue | 1 |
| line-4 | line-4-0688-0711-s003002 | station | reverse | revenue | 1 |
| line-4 | line-4-0762-0737-s004721 | station | reverse | revenue | 2 |
| line-1 | line-1-0549-0917-s015830 | depot | — | revenue | 30 |
| line-1 | line-1-0549-0917-s015830 | depot | — | spare | 4 |
| line-1 | line-1-0549-0917-s015830 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0451-0393-s000000 | depot | — | revenue | 15 |
| line-2 | line-2-0451-0393-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0451-0393-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0527-0619-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0527-0619-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0527-0619-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0618-0615-s000000 | depot | — | revenue | 9 |
| line-4 | line-4-0618-0615-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0618-0615-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/uyo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **124 trainsets at 23 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 9 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **78 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0723-0394-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0608-0527-s004802 | forward | revenue | 4 | pending |
| line-1 | line-1-0608-0527-s004802 | reverse | revenue | 4 | pending |
| line-1 | line-1-0605-0530-s004887 | forward | revenue | 4 | pending |
| line-1 | line-1-0605-0530-s004887 | reverse | revenue | 3 | pending |
| line-1 | line-1-0577-0563-s006004 | forward | revenue | 3 | pending |
| line-1 | line-1-0577-0563-s006004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0571-s006832 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0571-s006832 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0592-s007378 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0592-s007378 | reverse | revenue | 3 | pending |
| line-1 | line-1-0606-0747-s011609 | forward | revenue | 3 | pending |
| line-1 | line-1-0606-0747-s011609 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0917-s015830 | reverse | revenue | 3 | pending |
| line-1 | line-1-0605-0530-s004887 | reverse | spare | 1 | pending |
| line-1 | line-1-0577-0563-s006004 | forward | spare | 1 | pending |
| line-1 | line-1-0577-0563-s006004 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0571-s006832 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0571-s006832 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0393-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0571-s005056 | forward | revenue | 3 | pending |
| line-2 | line-2-0550-0571-s005056 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0587-s005446 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0587-s005446 | reverse | revenue | 3 | pending |
| line-2 | line-2-0618-0615-s007369 | forward | revenue | 3 | pending |
| line-2 | line-2-0618-0615-s007369 | reverse | revenue | 3 | pending |
| line-2 | line-2-0671-0611-s008623 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0571-s005056 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0571-s005056 | reverse | spare | 1 | pending |
| line-2 | line-2-0555-0587-s005446 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0527-0619-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0592-s000786 | forward | revenue | 2 | pending |
| line-3 | line-3-0551-0592-s000786 | reverse | revenue | 2 | pending |
| line-3 | line-3-0555-0587-s000942 | forward | revenue | 2 | pending |
| line-3 | line-3-0555-0587-s000942 | reverse | revenue | 2 | pending |
| line-3 | line-3-0577-0563-s001675 | forward | revenue | 2 | pending |
| line-3 | line-3-0577-0563-s001675 | reverse | revenue | 2 | pending |
| line-3 | line-3-0606-0529-s002665 | forward | revenue | 2 | pending |
| line-3 | line-3-0606-0529-s002665 | reverse | revenue | 2 | pending |
| line-3 | line-3-0608-0527-s002734 | forward | revenue | 2 | pending |
| line-3 | line-3-0608-0527-s002734 | reverse | revenue | 2 | pending |
| line-3 | line-3-0720-0400-s006553 | reverse | revenue | 2 | pending |
| line-3 | line-3-0551-0592-s000786 | forward | spare | 1 | pending |
| line-3 | line-3-0551-0592-s000786 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0587-s000942 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0618-0615-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0688-0711-s003002 | forward | revenue | 4 | pending |
| line-4 | line-4-0688-0711-s003002 | reverse | revenue | 4 | pending |
| line-4 | line-4-0762-0737-s004721 | reverse | revenue | 3 | pending |
| line-4 | line-4-0762-0737-s004721 | reverse | spare | 1 | pending |
| line-4 | line-4-0618-0615-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**52 trainsets exceed the reference platform envelope**, requiring **3,094.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0549-0917-s015830 | 3 | 2 | 1 | 59.5 |
| line-1-0550-0571-s006832 | 8 | 4 | 4 | 238.0 |
| line-1-0551-0592-s007378 | 6 | 4 | 2 | 119.0 |
| line-1-0577-0563-s006004 | 8 | 4 | 4 | 238.0 |
| line-1-0605-0530-s004887 | 8 | 4 | 4 | 238.0 |
| line-1-0606-0747-s011609 | 6 | 2 | 4 | 238.0 |
| line-1-0608-0527-s004802 | 8 | 4 | 4 | 238.0 |
| line-1-0723-0394-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0451-0393-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0550-0571-s005056 | 8 | 4 | 4 | 238.0 |
| line-2-0555-0587-s005446 | 7 | 4 | 3 | 178.5 |
| line-2-0618-0615-s007369 | 6 | 4 | 2 | 119.0 |
| line-2-0671-0611-s008623 | 3 | 2 | 1 | 59.5 |
| line-3-0527-0619-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0551-0592-s000786 | 6 | 4 | 2 | 119.0 |
| line-3-0555-0587-s000942 | 5 | 4 | 1 | 59.5 |
| line-3-0577-0563-s001675 | 4 | 4 | 0 | 0.0 |
| line-3-0606-0529-s002665 | 4 | 4 | 0 | 0.0 |
| line-3-0608-0527-s002734 | 4 | 4 | 0 | 0.0 |
| line-3-0720-0400-s006553 | 2 | 2 | 0 | 0.0 |
| line-4-0618-0615-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0688-0711-s003002 | 8 | 2 | 6 | 357.0 |
| line-4-0762-0737-s004721 | 4 | 2 | 2 | 119.0 |

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
