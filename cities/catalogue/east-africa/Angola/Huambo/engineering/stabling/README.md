# Station and depot overnight allocation

Plan: **40 trainsets at stations + 72 at depots = 112 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0361-1048-s023668 | line-1 | declared-depot | 33 | 1,963.5 | 17 |
| line-2-0698-0421-s012883 | line-2 | storage-at-existing-powered-service-point | 16 | 952.0 | 0 |
| line-3-0883-0735-s015872 | line-3 | storage-at-existing-powered-service-point | 23 | 1,368.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0361-1048-s023668 | station | reverse | revenue | 2 |
| line-1 | line-1-0411-0756-s016697 | station | forward | revenue | 1 |
| line-1 | line-1-0411-0756-s016697 | station | reverse | revenue | 1 |
| line-1 | line-1-0460-0664-s014369 | station | forward | revenue | 1 |
| line-1 | line-1-0460-0664-s014369 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0215-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0523-0500-s007801 | station | forward | revenue | 1 |
| line-1 | line-1-0523-0500-s007801 | station | reverse | revenue | 1 |
| line-1 | line-1-0534-0600-s011356 | station | forward | revenue | 1 |
| line-1 | line-1-0534-0600-s011356 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0388-s004796 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0388-s004796 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0556-s010080 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0556-s010080 | station | reverse | revenue | 1 |
| line-2 | line-2-0478-0698-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0478-0698-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0486-0817-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0550-0556-s007868 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0556-s007868 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0618-s006041 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0618-s006041 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0472-s010373 | station | forward | revenue | 1 |
| line-2 | line-2-0603-0472-s010373 | station | reverse | revenue | 1 |
| line-2 | line-2-0698-0421-s012883 | station | reverse | revenue | 2 |
| line-3 | line-3-0267-0585-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0397-0590-s003013 | station | forward | revenue | 1 |
| line-3 | line-3-0397-0590-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0474-0588-s005030 | station | forward | revenue | 1 |
| line-3 | line-3-0474-0588-s005030 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0556-s007044 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0556-s007044 | station | reverse | revenue | 1 |
| line-3 | line-3-0630-0588-s009041 | station | forward | revenue | 1 |
| line-3 | line-3-0630-0588-s009041 | station | reverse | revenue | 1 |
| line-3 | line-3-0883-0735-s015872 | station | reverse | revenue | 2 |
| line-1 | line-1-0361-1048-s023668 | depot | — | revenue | 28 |
| line-1 | line-1-0361-1048-s023668 | depot | — | spare | 4 |
| line-1 | line-1-0361-1048-s023668 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0698-0421-s012883 | depot | — | revenue | 13 |
| line-2 | line-2-0698-0421-s012883 | depot | — | spare | 2 |
| line-2 | line-2-0698-0421-s012883 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0883-0735-s015872 | depot | — | revenue | 19 |
| line-3 | line-3-0883-0735-s015872 | depot | — | spare | 3 |
| line-3 | line-3-0883-0735-s015872 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/huambo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **112 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **100 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **72 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0511-0215-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0388-s004796 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0388-s004796 | reverse | revenue | 3 | pending |
| line-1 | line-1-0523-0500-s007801 | forward | revenue | 3 | pending |
| line-1 | line-1-0523-0500-s007801 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0556-s010080 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0556-s010080 | reverse | revenue | 3 | pending |
| line-1 | line-1-0534-0600-s011356 | forward | revenue | 3 | pending |
| line-1 | line-1-0534-0600-s011356 | reverse | revenue | 3 | pending |
| line-1 | line-1-0460-0664-s014369 | forward | revenue | 3 | pending |
| line-1 | line-1-0460-0664-s014369 | reverse | revenue | 3 | pending |
| line-1 | line-1-0411-0756-s016697 | forward | revenue | 3 | pending |
| line-1 | line-1-0411-0756-s016697 | reverse | revenue | 3 | pending |
| line-1 | line-1-0361-1048-s023668 | reverse | revenue | 3 | pending |
| line-1 | line-1-0539-0388-s004796 | reverse | spare | 1 | pending |
| line-1 | line-1-0523-0500-s007801 | forward | spare | 1 | pending |
| line-1 | line-1-0523-0500-s007801 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0556-s010080 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0556-s010080 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0478-0698-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0478-0698-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0568-0618-s006041 | forward | revenue | 3 | pending |
| line-2 | line-2-0568-0618-s006041 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0556-s007868 | forward | revenue | 2 | pending |
| line-2 | line-2-0550-0556-s007868 | reverse | revenue | 2 | pending |
| line-2 | line-2-0603-0472-s010373 | forward | revenue | 2 | pending |
| line-2 | line-2-0603-0472-s010373 | reverse | revenue | 2 | pending |
| line-2 | line-2-0698-0421-s012883 | reverse | revenue | 2 | pending |
| line-2 | line-2-0550-0556-s007868 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0556-s007868 | reverse | spare | 1 | pending |
| line-2 | line-2-0603-0472-s010373 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0397-0590-s003013 | forward | revenue | 3 | pending |
| line-3 | line-3-0397-0590-s003013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0474-0588-s005030 | forward | revenue | 3 | pending |
| line-3 | line-3-0474-0588-s005030 | reverse | revenue | 3 | pending |
| line-3 | line-3-0550-0556-s007044 | forward | revenue | 3 | pending |
| line-3 | line-3-0550-0556-s007044 | reverse | revenue | 3 | pending |
| line-3 | line-3-0630-0588-s009041 | forward | revenue | 3 | pending |
| line-3 | line-3-0630-0588-s009041 | reverse | revenue | 3 | pending |
| line-3 | line-3-0883-0735-s015872 | reverse | revenue | 3 | pending |
| line-3 | line-3-0397-0590-s003013 | forward | spare | 1 | pending |
| line-3 | line-3-0397-0590-s003013 | reverse | spare | 1 | pending |
| line-3 | line-3-0474-0588-s005030 | forward | spare | 1 | pending |
| line-3 | line-3-0474-0588-s005030 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**66 trainsets exceed the reference platform envelope**, requiring **3,927.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0361-1048-s023668 | 3 | 2 | 1 | 59.5 |
| line-1-0411-0756-s016697 | 6 | 2 | 4 | 238.0 |
| line-1-0460-0664-s014369 | 6 | 2 | 4 | 238.0 |
| line-1-0511-0215-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0523-0500-s007801 | 8 | 2 | 6 | 357.0 |
| line-1-0534-0600-s011356 | 6 | 2 | 4 | 238.0 |
| line-1-0539-0388-s004796 | 8 | 2 | 6 | 357.0 |
| line-1-0550-0556-s010080 | 8 | 4 | 4 | 238.0 |
| line-2-0478-0698-s003016 | 6 | 2 | 4 | 238.0 |
| line-2-0486-0817-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0550-0556-s007868 | 6 | 4 | 2 | 119.0 |
| line-2-0568-0618-s006041 | 6 | 2 | 4 | 238.0 |
| line-2-0603-0472-s010373 | 5 | 2 | 3 | 178.5 |
| line-2-0698-0421-s012883 | 2 | 2 | 0 | 0.0 |
| line-3-0267-0585-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0397-0590-s003013 | 8 | 2 | 6 | 357.0 |
| line-3-0474-0588-s005030 | 8 | 2 | 6 | 357.0 |
| line-3-0550-0556-s007044 | 6 | 4 | 2 | 119.0 |
| line-3-0630-0588-s009041 | 6 | 2 | 4 | 238.0 |
| line-3-0883-0735-s015872 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Huambo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
