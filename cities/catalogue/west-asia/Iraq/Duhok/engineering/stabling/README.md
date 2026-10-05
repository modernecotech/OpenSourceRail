# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 122 at depots = 162 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0682-0744-s000000 | line-1 | declared-depot | 38 | 2,261.0 | 8 |
| line-2-0530-0094-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 8 |
| line-3-0540-0838-s018431 | line-3 | declared-depot | 46 | 2,737.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0584-0017-s016578 | station | reverse | revenue | 2 |
| line-1 | line-1-0587-0205-s011989 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0205-s011989 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0106-s014296 | station | forward | revenue | 1 |
| line-1 | line-1-0603-0106-s014296 | station | reverse | revenue | 1 |
| line-1 | line-1-0613-0345-s008974 | station | forward | revenue | 1 |
| line-1 | line-1-0613-0345-s008974 | station | reverse | revenue | 1 |
| line-1 | line-1-0639-0485-s005958 | station | forward | revenue | 1 |
| line-1 | line-1-0639-0485-s005958 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0582-s003869 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0582-s003869 | station | reverse | revenue | 1 |
| line-1 | line-1-0682-0744-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0525-0227-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0525-0227-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0530-0094-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0533-0854-s016597 | station | reverse | revenue | 2 |
| line-2 | line-2-0536-0373-s006013 | station | forward | revenue | 1 |
| line-2 | line-2-0536-0373-s006013 | station | reverse | revenue | 1 |
| line-2 | line-2-0540-0432-s007226 | station | forward | revenue | 1 |
| line-2 | line-2-0540-0432-s007226 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0519-s009016 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0519-s009016 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0702-s012800 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0702-s012800 | station | reverse | revenue | 1 |
| line-3 | line-3-0540-0838-s018431 | station | reverse | revenue | 2 |
| line-3 | line-3-0599-0690-s014374 | station | forward | revenue | 1 |
| line-3 | line-3-0599-0690-s014374 | station | reverse | revenue | 1 |
| line-3 | line-3-0611-0492-s010314 | station | forward | revenue | 1 |
| line-3 | line-3-0611-0492-s010314 | station | reverse | revenue | 1 |
| line-3 | line-3-0620-0345-s007300 | station | forward | revenue | 1 |
| line-3 | line-3-0620-0345-s007300 | station | reverse | revenue | 1 |
| line-3 | line-3-0629-0198-s004285 | station | forward | revenue | 1 |
| line-3 | line-3-0629-0198-s004285 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0007-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0682-0744-s000000 | depot | — | revenue | 33 |
| line-1 | line-1-0682-0744-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0682-0744-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0530-0094-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0530-0094-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0530-0094-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0540-0838-s018431 | depot | — | revenue | 40 |
| line-3 | line-3-0540-0838-s018431 | depot | — | spare | 5 |
| line-3 | line-3-0540-0838-s018431 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/duhok-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **162 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **146 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **122 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0682-0744-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0582-s003869 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0582-s003869 | reverse | revenue | 4 | pending |
| line-1 | line-1-0639-0485-s005958 | forward | revenue | 4 | pending |
| line-1 | line-1-0639-0485-s005958 | reverse | revenue | 4 | pending |
| line-1 | line-1-0613-0345-s008974 | forward | revenue | 4 | pending |
| line-1 | line-1-0613-0345-s008974 | reverse | revenue | 4 | pending |
| line-1 | line-1-0587-0205-s011989 | forward | revenue | 4 | pending |
| line-1 | line-1-0587-0205-s011989 | reverse | revenue | 4 | pending |
| line-1 | line-1-0603-0106-s014296 | forward | revenue | 4 | pending |
| line-1 | line-1-0603-0106-s014296 | reverse | revenue | 4 | pending |
| line-1 | line-1-0584-0017-s016578 | reverse | revenue | 3 | pending |
| line-1 | line-1-0584-0017-s016578 | reverse | spare | 1 | pending |
| line-1 | line-1-0682-0744-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0582-s003869 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0582-s003869 | reverse | spare | 1 | pending |
| line-1 | line-1-0639-0485-s005958 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0525-0227-s003002 | forward | revenue | 4 | pending |
| line-2 | line-2-0525-0227-s003002 | reverse | revenue | 4 | pending |
| line-2 | line-2-0536-0373-s006013 | forward | revenue | 4 | pending |
| line-2 | line-2-0536-0373-s006013 | reverse | revenue | 4 | pending |
| line-2 | line-2-0540-0432-s007226 | forward | revenue | 4 | pending |
| line-2 | line-2-0540-0432-s007226 | reverse | revenue | 4 | pending |
| line-2 | line-2-0546-0519-s009016 | forward | revenue | 4 | pending |
| line-2 | line-2-0546-0519-s009016 | reverse | revenue | 4 | pending |
| line-2 | line-2-0561-0702-s012800 | forward | revenue | 4 | pending |
| line-2 | line-2-0561-0702-s012800 | reverse | revenue | 4 | pending |
| line-2 | line-2-0533-0854-s016597 | reverse | revenue | 3 | pending |
| line-2 | line-2-0533-0854-s016597 | reverse | spare | 1 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0525-0227-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0525-0227-s003002 | reverse | spare | 1 | pending |
| line-2 | line-2-0536-0373-s006013 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0658-0007-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0629-0198-s004285 | forward | revenue | 6 | pending |
| line-3 | line-3-0629-0198-s004285 | reverse | revenue | 5 | pending |
| line-3 | line-3-0620-0345-s007300 | forward | revenue | 5 | pending |
| line-3 | line-3-0620-0345-s007300 | reverse | revenue | 5 | pending |
| line-3 | line-3-0611-0492-s010314 | forward | revenue | 5 | pending |
| line-3 | line-3-0611-0492-s010314 | reverse | revenue | 5 | pending |
| line-3 | line-3-0599-0690-s014374 | forward | revenue | 5 | pending |
| line-3 | line-3-0599-0690-s014374 | reverse | revenue | 5 | pending |
| line-3 | line-3-0540-0838-s018431 | reverse | revenue | 5 | pending |
| line-3 | line-3-0629-0198-s004285 | reverse | spare | 1 | pending |
| line-3 | line-3-0620-0345-s007300 | forward | spare | 1 | pending |
| line-3 | line-3-0620-0345-s007300 | reverse | spare | 1 | pending |
| line-3 | line-3-0611-0492-s010314 | forward | spare | 1 | pending |
| line-3 | line-3-0611-0492-s010314 | reverse | spare | 1 | pending |
| line-3 | line-3-0599-0690-s014374 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**114 trainsets exceed the reference platform envelope**, requiring **6,783.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0584-0017-s016578 | 4 | 2 | 2 | 119.0 |
| line-1-0587-0205-s011989 | 8 | 2 | 6 | 357.0 |
| line-1-0603-0106-s014296 | 8 | 2 | 6 | 357.0 |
| line-1-0613-0345-s008974 | 8 | 4 | 4 | 238.0 |
| line-1-0639-0485-s005958 | 9 | 4 | 5 | 297.5 |
| line-1-0657-0582-s003869 | 10 | 2 | 8 | 476.0 |
| line-1-0682-0744-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0525-0227-s003002 | 10 | 2 | 8 | 476.0 |
| line-2-0530-0094-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0533-0854-s016597 | 4 | 2 | 2 | 119.0 |
| line-2-0536-0373-s006013 | 9 | 2 | 7 | 416.5 |
| line-2-0540-0432-s007226 | 8 | 2 | 6 | 357.0 |
| line-2-0546-0519-s009016 | 8 | 2 | 6 | 357.0 |
| line-2-0561-0702-s012800 | 8 | 2 | 6 | 357.0 |
| line-3-0540-0838-s018431 | 5 | 2 | 3 | 178.5 |
| line-3-0599-0690-s014374 | 11 | 2 | 9 | 535.5 |
| line-3-0611-0492-s010314 | 12 | 4 | 8 | 476.0 |
| line-3-0620-0345-s007300 | 12 | 4 | 8 | 476.0 |
| line-3-0629-0198-s004285 | 12 | 2 | 10 | 595.0 |
| line-3-0658-0007-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Duhok/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
