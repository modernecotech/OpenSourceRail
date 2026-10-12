# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 143 at depots = 185 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0886-0587-s022409 | line-1 | declared-depot | 57 | 3,391.5 | 10 |
| line-2-0217-0514-s000000 | line-2 | declared-depot | 32 | 1,904.0 | 6 |
| line-3-0338-0806-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |
| line-4-0257-0645-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0695-0624-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0125-0723-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0257-0645-s004007 | station | forward | revenue | 1 |
| line-1 | line-1-0257-0645-s004007 | station | reverse | revenue | 1 |
| line-1 | line-1-0360-0652-s007622 | station | forward | revenue | 1 |
| line-1 | line-1-0360-0652-s007622 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0588-s013001 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0588-s013001 | station | reverse | revenue | 1 |
| line-1 | line-1-0695-0624-s017611 | station | forward | revenue | 1 |
| line-1 | line-1-0695-0624-s017611 | station | reverse | revenue | 1 |
| line-1 | line-1-0886-0587-s022409 | station | reverse | revenue | 2 |
| line-2 | line-2-0217-0514-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0338-0554-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0338-0554-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0527-0573-s007117 | station | forward | revenue | 1 |
| line-2 | line-2-0527-0573-s007117 | station | reverse | revenue | 1 |
| line-2 | line-2-0686-0505-s011162 | station | forward | revenue | 1 |
| line-2 | line-2-0686-0505-s011162 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0526-s013305 | station | reverse | revenue | 2 |
| line-3 | line-3-0338-0806-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0747-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0747-s003004 | station | reverse | revenue | 1 |
| line-3 | line-3-0516-0735-s006014 | station | forward | revenue | 1 |
| line-3 | line-3-0516-0735-s006014 | station | reverse | revenue | 1 |
| line-3 | line-3-0650-0711-s009026 | station | forward | revenue | 1 |
| line-3 | line-3-0650-0711-s009026 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0754-s011594 | station | reverse | revenue | 2 |
| line-4 | line-4-0062-0487-s006244 | station | reverse | revenue | 2 |
| line-4 | line-4-0137-0512-s004406 | station | forward | revenue | 1 |
| line-4 | line-4-0137-0512-s004406 | station | reverse | revenue | 1 |
| line-4 | line-4-0257-0645-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0695-0624-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0862-0739-s004837 | station | reverse | revenue | 2 |
| line-1 | line-1-0886-0587-s022409 | depot | — | revenue | 50 |
| line-1 | line-1-0886-0587-s022409 | depot | — | spare | 6 |
| line-1 | line-1-0886-0587-s022409 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0217-0514-s000000 | depot | — | revenue | 28 |
| line-2 | line-2-0217-0514-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0217-0514-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0338-0806-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0338-0806-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0338-0806-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0257-0645-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0257-0645-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0257-0645-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0695-0624-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0695-0624-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0695-0624-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jos-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **185 trainsets at 21 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **166 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **143 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0125-0723-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0257-0645-s004007 | forward | revenue | 7 | pending |
| line-1 | line-1-0257-0645-s004007 | reverse | revenue | 6 | pending |
| line-1 | line-1-0360-0652-s007622 | forward | revenue | 6 | pending |
| line-1 | line-1-0360-0652-s007622 | reverse | revenue | 6 | pending |
| line-1 | line-1-0535-0588-s013001 | forward | revenue | 6 | pending |
| line-1 | line-1-0535-0588-s013001 | reverse | revenue | 6 | pending |
| line-1 | line-1-0695-0624-s017611 | forward | revenue | 6 | pending |
| line-1 | line-1-0695-0624-s017611 | reverse | revenue | 6 | pending |
| line-1 | line-1-0886-0587-s022409 | reverse | revenue | 6 | pending |
| line-1 | line-1-0257-0645-s004007 | reverse | spare | 1 | pending |
| line-1 | line-1-0360-0652-s007622 | forward | spare | 1 | pending |
| line-1 | line-1-0360-0652-s007622 | reverse | spare | 1 | pending |
| line-1 | line-1-0535-0588-s013001 | forward | spare | 1 | pending |
| line-1 | line-1-0535-0588-s013001 | reverse | spare | 1 | pending |
| line-1 | line-1-0695-0624-s017611 | forward | spare | 1 | pending |
| line-1 | line-1-0695-0624-s017611 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0217-0514-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0338-0554-s003016 | forward | revenue | 5 | pending |
| line-2 | line-2-0338-0554-s003016 | reverse | revenue | 5 | pending |
| line-2 | line-2-0527-0573-s007117 | forward | revenue | 5 | pending |
| line-2 | line-2-0527-0573-s007117 | reverse | revenue | 5 | pending |
| line-2 | line-2-0686-0505-s011162 | forward | revenue | 5 | pending |
| line-2 | line-2-0686-0505-s011162 | reverse | revenue | 4 | pending |
| line-2 | line-2-0782-0526-s013305 | reverse | revenue | 4 | pending |
| line-2 | line-2-0686-0505-s011162 | reverse | spare | 1 | pending |
| line-2 | line-2-0782-0526-s013305 | reverse | spare | 1 | pending |
| line-2 | line-2-0217-0514-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0338-0554-s003016 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0338-0806-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0403-0747-s003004 | forward | revenue | 5 | pending |
| line-3 | line-3-0403-0747-s003004 | reverse | revenue | 4 | pending |
| line-3 | line-3-0516-0735-s006014 | forward | revenue | 4 | pending |
| line-3 | line-3-0516-0735-s006014 | reverse | revenue | 4 | pending |
| line-3 | line-3-0650-0711-s009026 | forward | revenue | 4 | pending |
| line-3 | line-3-0650-0711-s009026 | reverse | revenue | 4 | pending |
| line-3 | line-3-0711-0754-s011594 | reverse | revenue | 4 | pending |
| line-3 | line-3-0403-0747-s003004 | reverse | spare | 1 | pending |
| line-3 | line-3-0516-0735-s006014 | forward | spare | 1 | pending |
| line-3 | line-3-0516-0735-s006014 | reverse | spare | 1 | pending |
| line-3 | line-3-0650-0711-s009026 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0257-0645-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0137-0512-s004406 | forward | revenue | 5 | pending |
| line-4 | line-4-0137-0512-s004406 | reverse | revenue | 4 | pending |
| line-4 | line-4-0062-0487-s006244 | reverse | revenue | 4 | pending |
| line-4 | line-4-0137-0512-s004406 | reverse | spare | 1 | pending |
| line-4 | line-4-0062-0487-s006244 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0695-0624-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0862-0739-s004837 | reverse | revenue | 7 | pending |
| line-5 | line-5-0695-0624-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0862-0739-s004837 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**135 trainsets exceed the reference platform envelope**, requiring **8,032.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0125-0723-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0257-0645-s004007 | 14 | 4 | 10 | 595.0 |
| line-1-0360-0652-s007622 | 14 | 2 | 12 | 714.0 |
| line-1-0535-0588-s013001 | 14 | 4 | 10 | 595.0 |
| line-1-0695-0624-s017611 | 14 | 4 | 10 | 595.0 |
| line-1-0886-0587-s022409 | 6 | 2 | 4 | 238.0 |
| line-2-0217-0514-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0338-0554-s003016 | 11 | 2 | 9 | 535.5 |
| line-2-0527-0573-s007117 | 10 | 4 | 6 | 357.0 |
| line-2-0686-0505-s011162 | 10 | 2 | 8 | 476.0 |
| line-2-0782-0526-s013305 | 5 | 2 | 3 | 178.5 |
| line-3-0338-0806-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0403-0747-s003004 | 10 | 2 | 8 | 476.0 |
| line-3-0516-0735-s006014 | 10 | 2 | 8 | 476.0 |
| line-3-0650-0711-s009026 | 9 | 2 | 7 | 416.5 |
| line-3-0711-0754-s011594 | 4 | 2 | 2 | 119.0 |
| line-4-0062-0487-s006244 | 5 | 2 | 3 | 178.5 |
| line-4-0137-0512-s004406 | 10 | 2 | 8 | 476.0 |
| line-4-0257-0645-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0695-0624-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0862-0739-s004837 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Jos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
