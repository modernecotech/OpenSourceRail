# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 105 at depots = 137 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0430-0223-s000000 | line-1 | declared-depot | 38 | 2,261.0 | 7 |
| line-2-0513-0710-s016631 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0358-0684-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0430-0223-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0493-0407-s004237 | station | forward | revenue | 1 |
| line-1 | line-1-0493-0407-s004237 | station | reverse | revenue | 1 |
| line-1 | line-1-0541-0546-s007450 | station | forward | revenue | 1 |
| line-1 | line-1-0541-0546-s007450 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0632-s009430 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0632-s009430 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0900-s015567 | station | reverse | revenue | 2 |
| line-2 | line-2-0513-0710-s016631 | station | reverse | revenue | 2 |
| line-2 | line-2-0571-0632-s014368 | station | forward | revenue | 1 |
| line-2 | line-2-0571-0632-s014368 | station | reverse | revenue | 1 |
| line-2 | line-2-0609-0580-s012861 | station | forward | revenue | 1 |
| line-2 | line-2-0609-0580-s012861 | station | reverse | revenue | 1 |
| line-2 | line-2-0686-0477-s009858 | station | forward | revenue | 1 |
| line-2 | line-2-0686-0477-s009858 | station | reverse | revenue | 1 |
| line-2 | line-2-0763-0373-s006848 | station | forward | revenue | 1 |
| line-2 | line-2-0763-0373-s006848 | station | reverse | revenue | 1 |
| line-2 | line-2-0923-0150-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0358-0684-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0449-0584-s003023 | station | forward | revenue | 1 |
| line-3 | line-3-0449-0584-s003023 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0485-s006018 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0485-s006018 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0385-s009062 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0385-s009062 | station | reverse | revenue | 1 |
| line-3 | line-3-0708-0301-s011614 | station | reverse | revenue | 2 |
| line-1 | line-1-0430-0223-s000000 | depot | — | revenue | 33 |
| line-1 | line-1-0430-0223-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0430-0223-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0513-0710-s016631 | depot | — | revenue | 34 |
| line-2 | line-2-0513-0710-s016631 | depot | — | spare | 4 |
| line-2 | line-2-0513-0710-s016631 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0358-0684-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0358-0684-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0358-0684-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/comilla-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **137 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **123 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **105 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0430-0223-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0493-0407-s004237 | forward | revenue | 6 | pending |
| line-1 | line-1-0493-0407-s004237 | reverse | revenue | 6 | pending |
| line-1 | line-1-0541-0546-s007450 | forward | revenue | 5 | pending |
| line-1 | line-1-0541-0546-s007450 | reverse | revenue | 5 | pending |
| line-1 | line-1-0571-0632-s009430 | forward | revenue | 5 | pending |
| line-1 | line-1-0571-0632-s009430 | reverse | revenue | 5 | pending |
| line-1 | line-1-0647-0900-s015567 | reverse | revenue | 5 | pending |
| line-1 | line-1-0541-0546-s007450 | forward | spare | 1 | pending |
| line-1 | line-1-0541-0546-s007450 | reverse | spare | 1 | pending |
| line-1 | line-1-0571-0632-s009430 | forward | spare | 1 | pending |
| line-1 | line-1-0571-0632-s009430 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0900-s015567 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0923-0150-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0763-0373-s006848 | forward | revenue | 5 | pending |
| line-2 | line-2-0763-0373-s006848 | reverse | revenue | 5 | pending |
| line-2 | line-2-0686-0477-s009858 | forward | revenue | 5 | pending |
| line-2 | line-2-0686-0477-s009858 | reverse | revenue | 5 | pending |
| line-2 | line-2-0609-0580-s012861 | forward | revenue | 5 | pending |
| line-2 | line-2-0609-0580-s012861 | reverse | revenue | 4 | pending |
| line-2 | line-2-0571-0632-s014368 | forward | revenue | 4 | pending |
| line-2 | line-2-0571-0632-s014368 | reverse | revenue | 4 | pending |
| line-2 | line-2-0513-0710-s016631 | reverse | revenue | 4 | pending |
| line-2 | line-2-0609-0580-s012861 | reverse | spare | 1 | pending |
| line-2 | line-2-0571-0632-s014368 | forward | spare | 1 | pending |
| line-2 | line-2-0571-0632-s014368 | reverse | spare | 1 | pending |
| line-2 | line-2-0513-0710-s016631 | reverse | spare | 1 | pending |
| line-2 | line-2-0923-0150-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0358-0684-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0449-0584-s003023 | forward | revenue | 5 | pending |
| line-3 | line-3-0449-0584-s003023 | reverse | revenue | 4 | pending |
| line-3 | line-3-0539-0485-s006018 | forward | revenue | 4 | pending |
| line-3 | line-3-0539-0485-s006018 | reverse | revenue | 4 | pending |
| line-3 | line-3-0631-0385-s009062 | forward | revenue | 4 | pending |
| line-3 | line-3-0631-0385-s009062 | reverse | revenue | 4 | pending |
| line-3 | line-3-0708-0301-s011614 | reverse | revenue | 4 | pending |
| line-3 | line-3-0449-0584-s003023 | reverse | spare | 1 | pending |
| line-3 | line-3-0539-0485-s006018 | forward | spare | 1 | pending |
| line-3 | line-3-0539-0485-s006018 | reverse | spare | 1 | pending |
| line-3 | line-3-0631-0385-s009062 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**101 trainsets exceed the reference platform envelope**, requiring **6,009.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0430-0223-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0493-0407-s004237 | 12 | 2 | 10 | 595.0 |
| line-1-0541-0546-s007450 | 12 | 2 | 10 | 595.0 |
| line-1-0571-0632-s009430 | 12 | 4 | 8 | 476.0 |
| line-1-0647-0900-s015567 | 6 | 2 | 4 | 238.0 |
| line-2-0513-0710-s016631 | 5 | 2 | 3 | 178.5 |
| line-2-0571-0632-s014368 | 10 | 4 | 6 | 357.0 |
| line-2-0609-0580-s012861 | 10 | 2 | 8 | 476.0 |
| line-2-0686-0477-s009858 | 10 | 2 | 8 | 476.0 |
| line-2-0763-0373-s006848 | 10 | 2 | 8 | 476.0 |
| line-2-0923-0150-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0358-0684-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0449-0584-s003023 | 10 | 2 | 8 | 476.0 |
| line-3-0539-0485-s006018 | 10 | 2 | 8 | 476.0 |
| line-3-0631-0385-s009062 | 9 | 2 | 7 | 416.5 |
| line-3-0708-0301-s011614 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Comilla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
