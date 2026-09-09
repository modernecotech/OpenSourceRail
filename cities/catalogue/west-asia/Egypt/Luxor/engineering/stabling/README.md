# Station and depot overnight allocation

Plan: **34 trainsets at stations + 77 at depots = 111 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0712-0526-s013238 | line-1 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-2-0324-0669-s020767 | line-2 | declared-depot | 34 | 2,023.0 | 17 |
| line-3-0300-0398-s016658 | line-3 | storage-at-existing-powered-service-point | 24 | 1,428.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0268-0383-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0405-0484-s004702 | station | forward | revenue | 1 |
| line-1 | line-1-0405-0484-s004702 | station | reverse | revenue | 1 |
| line-1 | line-1-0471-0539-s006674 | station | forward | revenue | 1 |
| line-1 | line-1-0471-0539-s006674 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0547-s008986 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0547-s008986 | station | reverse | revenue | 1 |
| line-1 | line-1-0712-0526-s013238 | station | reverse | revenue | 2 |
| line-2 | line-2-0324-0669-s020767 | station | reverse | revenue | 2 |
| line-2 | line-2-0411-0665-s018221 | station | forward | revenue | 1 |
| line-2 | line-2-0411-0665-s018221 | station | reverse | revenue | 1 |
| line-2 | line-2-0497-0579-s015672 | station | forward | revenue | 1 |
| line-2 | line-2-0497-0579-s015672 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0547-s013850 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0547-s013850 | station | reverse | revenue | 1 |
| line-2 | line-2-0588-0433-s011050 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0433-s011050 | station | reverse | revenue | 1 |
| line-2 | line-2-0954-0093-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0300-0398-s016658 | station | reverse | revenue | 2 |
| line-3 | line-3-0414-0479-s012992 | station | forward | revenue | 1 |
| line-3 | line-3-0414-0479-s012992 | station | reverse | revenue | 1 |
| line-3 | line-3-0490-0478-s011104 | station | forward | revenue | 1 |
| line-3 | line-3-0490-0478-s011104 | station | reverse | revenue | 1 |
| line-3 | line-3-0548-0547-s009220 | station | forward | revenue | 1 |
| line-3 | line-3-0548-0547-s009220 | station | reverse | revenue | 1 |
| line-3 | line-3-0589-0631-s006957 | station | forward | revenue | 1 |
| line-3 | line-3-0589-0631-s006957 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0862-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0712-0526-s013238 | depot | — | revenue | 16 |
| line-1 | line-1-0712-0526-s013238 | depot | — | spare | 2 |
| line-1 | line-1-0712-0526-s013238 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0324-0669-s020767 | depot | — | revenue | 29 |
| line-2 | line-2-0324-0669-s020767 | depot | — | spare | 4 |
| line-2 | line-2-0324-0669-s020767 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0300-0398-s016658 | depot | — | revenue | 20 |
| line-3 | line-3-0300-0398-s016658 | depot | — | spare | 3 |
| line-3 | line-3-0300-0398-s016658 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/luxor-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **111 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **99 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **77 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0268-0383-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | forward | revenue | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | reverse | revenue | 3 | pending |
| line-1 | line-1-0471-0539-s006674 | forward | revenue | 3 | pending |
| line-1 | line-1-0471-0539-s006674 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0547-s008986 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0547-s008986 | reverse | revenue | 3 | pending |
| line-1 | line-1-0712-0526-s013238 | reverse | revenue | 3 | pending |
| line-1 | line-1-0405-0484-s004702 | reverse | spare | 1 | pending |
| line-1 | line-1-0471-0539-s006674 | forward | spare | 1 | pending |
| line-1 | line-1-0471-0539-s006674 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0954-0093-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0588-0433-s011050 | forward | revenue | 4 | pending |
| line-2 | line-2-0588-0433-s011050 | reverse | revenue | 4 | pending |
| line-2 | line-2-0548-0547-s013850 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0547-s013850 | reverse | revenue | 4 | pending |
| line-2 | line-2-0497-0579-s015672 | forward | revenue | 4 | pending |
| line-2 | line-2-0497-0579-s015672 | reverse | revenue | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | forward | revenue | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | reverse | revenue | 4 | pending |
| line-2 | line-2-0324-0669-s020767 | reverse | revenue | 4 | pending |
| line-2 | line-2-0588-0433-s011050 | forward | spare | 1 | pending |
| line-2 | line-2-0588-0433-s011050 | reverse | spare | 1 | pending |
| line-2 | line-2-0548-0547-s013850 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0547-s013850 | reverse | spare | 1 | pending |
| line-2 | line-2-0497-0579-s015672 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | reverse | revenue | 3 | pending |
| line-3 | line-3-0548-0547-s009220 | forward | revenue | 3 | pending |
| line-3 | line-3-0548-0547-s009220 | reverse | revenue | 3 | pending |
| line-3 | line-3-0490-0478-s011104 | forward | revenue | 3 | pending |
| line-3 | line-3-0490-0478-s011104 | reverse | revenue | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | forward | revenue | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | reverse | revenue | 3 | pending |
| line-3 | line-3-0300-0398-s016658 | reverse | revenue | 3 | pending |
| line-3 | line-3-0589-0631-s006957 | reverse | spare | 1 | pending |
| line-3 | line-3-0548-0547-s009220 | forward | spare | 1 | pending |
| line-3 | line-3-0548-0547-s009220 | reverse | spare | 1 | pending |
| line-3 | line-3-0490-0478-s011104 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0268-0383-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0405-0484-s004702 | 8 | 4 | 4 | 238.0 |
| line-1-0471-0539-s006674 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0547-s008986 | 6 | 4 | 2 | 119.0 |
| line-1-0712-0526-s013238 | 3 | 2 | 1 | 59.5 |
| line-2-0324-0669-s020767 | 4 | 2 | 2 | 119.0 |
| line-2-0411-0665-s018221 | 8 | 2 | 6 | 357.0 |
| line-2-0497-0579-s015672 | 9 | 2 | 7 | 416.5 |
| line-2-0548-0547-s013850 | 10 | 4 | 6 | 357.0 |
| line-2-0588-0433-s011050 | 10 | 2 | 8 | 476.0 |
| line-2-0954-0093-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0300-0398-s016658 | 3 | 2 | 1 | 59.5 |
| line-3-0414-0479-s012992 | 6 | 4 | 2 | 119.0 |
| line-3-0490-0478-s011104 | 7 | 2 | 5 | 297.5 |
| line-3-0548-0547-s009220 | 8 | 4 | 4 | 238.0 |
| line-3-0589-0631-s006957 | 8 | 2 | 6 | 357.0 |
| line-3-0621-0862-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Luxor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
