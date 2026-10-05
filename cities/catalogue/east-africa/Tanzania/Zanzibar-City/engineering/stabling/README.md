# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 102 at depots = 128 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0178-0650-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 6 |
| line-2-0531-0458-s000000 | line-2 | declared-depot | 27 | 1,606.5 | 5 |
| line-3-0434-0670-s015727 | line-3 | declared-depot | 42 | 2,499.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0178-0650-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0415-0608-s005542 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0608-s005542 | station | reverse | revenue | 1 |
| line-1 | line-1-0586-0596-s009055 | station | forward | revenue | 1 |
| line-1 | line-1-0586-0596-s009055 | station | reverse | revenue | 1 |
| line-1 | line-1-0706-0587-s011536 | station | forward | revenue | 1 |
| line-1 | line-1-0706-0587-s011536 | station | reverse | revenue | 1 |
| line-1 | line-1-0826-0578-s014010 | station | reverse | revenue | 2 |
| line-2 | line-2-0531-0458-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0586-0596-s003359 | station | forward | revenue | 1 |
| line-2 | line-2-0586-0596-s003359 | station | reverse | revenue | 1 |
| line-2 | line-2-0637-0708-s006095 | station | forward | revenue | 1 |
| line-2 | line-2-0637-0708-s006095 | station | reverse | revenue | 1 |
| line-2 | line-2-0712-0922-s011297 | station | reverse | revenue | 2 |
| line-3 | line-3-0434-0670-s015727 | station | reverse | revenue | 2 |
| line-3 | line-3-0536-0689-s013530 | station | forward | revenue | 1 |
| line-3 | line-3-0536-0689-s013530 | station | reverse | revenue | 1 |
| line-3 | line-3-0637-0708-s011352 | station | forward | revenue | 1 |
| line-3 | line-3-0637-0708-s011352 | station | reverse | revenue | 1 |
| line-3 | line-3-1069-0872-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0178-0650-s000000 | depot | — | revenue | 29 |
| line-1 | line-1-0178-0650-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0178-0650-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0531-0458-s000000 | depot | — | revenue | 23 |
| line-2 | line-2-0531-0458-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0531-0458-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0434-0670-s015727 | depot | — | revenue | 37 |
| line-3 | line-3-0434-0670-s015727 | depot | — | spare | 4 |
| line-3 | line-3-0434-0670-s015727 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/zanzibar-city-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **128 trainsets at 13 stations**; largest initial station queue **17**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **115 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **102 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0178-0650-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0608-s005542 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0608-s005542 | reverse | revenue | 5 | pending |
| line-1 | line-1-0586-0596-s009055 | forward | revenue | 5 | pending |
| line-1 | line-1-0586-0596-s009055 | reverse | revenue | 5 | pending |
| line-1 | line-1-0706-0587-s011536 | forward | revenue | 5 | pending |
| line-1 | line-1-0706-0587-s011536 | reverse | revenue | 5 | pending |
| line-1 | line-1-0826-0578-s014010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0826-0578-s014010 | reverse | spare | 1 | pending |
| line-1 | line-1-0178-0650-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0608-s005542 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0608-s005542 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0531-0458-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0586-0596-s003359 | forward | revenue | 5 | pending |
| line-2 | line-2-0586-0596-s003359 | reverse | revenue | 5 | pending |
| line-2 | line-2-0637-0708-s006095 | forward | revenue | 5 | pending |
| line-2 | line-2-0637-0708-s006095 | reverse | revenue | 5 | pending |
| line-2 | line-2-0712-0922-s011297 | reverse | revenue | 5 | pending |
| line-2 | line-2-0586-0596-s003359 | forward | spare | 1 | pending |
| line-2 | line-2-0586-0596-s003359 | reverse | spare | 1 | pending |
| line-2 | line-2-0637-0708-s006095 | forward | spare | 1 | pending |
| line-2 | line-2-0637-0708-s006095 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0637-0708-s011352 | forward | revenue | 8 | pending |
| line-3 | line-3-0637-0708-s011352 | reverse | revenue | 8 | pending |
| line-3 | line-3-0536-0689-s013530 | forward | revenue | 7 | pending |
| line-3 | line-3-0536-0689-s013530 | reverse | revenue | 7 | pending |
| line-3 | line-3-0434-0670-s015727 | reverse | revenue | 7 | pending |
| line-3 | line-3-0536-0689-s013530 | forward | spare | 1 | pending |
| line-3 | line-3-0536-0689-s013530 | reverse | spare | 1 | pending |
| line-3 | line-3-0434-0670-s015727 | reverse | spare | 1 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0637-0708-s011352 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**94 trainsets exceed the reference platform envelope**, requiring **5,593.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0178-0650-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0415-0608-s005542 | 12 | 2 | 10 | 595.0 |
| line-1-0586-0596-s009055 | 10 | 4 | 6 | 357.0 |
| line-1-0706-0587-s011536 | 10 | 2 | 8 | 476.0 |
| line-1-0826-0578-s014010 | 5 | 2 | 3 | 178.5 |
| line-2-0531-0458-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0586-0596-s003359 | 12 | 4 | 8 | 476.0 |
| line-2-0637-0708-s006095 | 12 | 4 | 8 | 476.0 |
| line-2-0712-0922-s011297 | 5 | 2 | 3 | 178.5 |
| line-3-0434-0670-s015727 | 8 | 2 | 6 | 357.0 |
| line-3-0536-0689-s013530 | 16 | 2 | 14 | 833.0 |
| line-3-0637-0708-s011352 | 17 | 4 | 13 | 773.5 |
| line-3-1069-0872-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Zanzibar-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
