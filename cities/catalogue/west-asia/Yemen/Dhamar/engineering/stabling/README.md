# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **50 trainsets at stations + 60 at depots = 110 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0115-0301-s000000 | line-1 | declared-depot | 8 | 392.0 | 3 |
| line-2-0679-0164-s009445 | line-2 | declared-depot | 15 | 735.0 | 4 |
| line-3-0333-0446-s000000 | line-3 | declared-depot | 5 | 245.0 | 2 |
| line-4-0367-0335-s000000 | line-4 | declared-depot | 4 | 196.0 | 2 |
| line-5-0381-0463-s000000 | line-5 | declared-depot | 4 | 196.0 | 2 |
| line-6-0214-0301-s000000 | line-6 | declared-depot | 7 | 343.0 | 2 |
| line-7-0366-0334-s000000 | line-7 | declared-depot | 9 | 441.0 | 3 |
| line-8-0497-0335-s000000 | line-8 | declared-depot | 8 | 392.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0115-0301-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0214-0301-s002240 | station | forward | revenue | 1 |
| line-1 | line-1-0214-0301-s002240 | station | reverse | revenue | 1 |
| line-1 | line-1-0306-0321-s004246 | station | forward | revenue | 1 |
| line-1 | line-1-0306-0321-s004246 | station | reverse | revenue | 1 |
| line-1 | line-1-0368-0335-s005602 | station | forward | revenue | 1 |
| line-1 | line-1-0368-0335-s005602 | station | reverse | revenue | 1 |
| line-1 | line-1-0445-0352-s007294 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0463-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0452-0384-s002391 | station | forward | revenue | 1 |
| line-2 | line-2-0452-0384-s002391 | station | reverse | revenue | 1 |
| line-2 | line-2-0497-0335-s003861 | station | forward | revenue | 1 |
| line-2 | line-2-0497-0335-s003861 | station | reverse | revenue | 1 |
| line-2 | line-2-0679-0164-s009445 | station | reverse | revenue | 2 |
| line-3 | line-3-0295-0267-s003895 | station | reverse | revenue | 2 |
| line-3 | line-3-0306-0321-s002724 | station | forward | revenue | 1 |
| line-3 | line-3-0306-0321-s002724 | station | reverse | revenue | 1 |
| line-3 | line-3-0322-0392-s001171 | station | forward | revenue | 1 |
| line-3 | line-3-0322-0392-s001171 | station | reverse | revenue | 1 |
| line-3 | line-3-0333-0446-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0288-0392-s002310 | station | reverse | revenue | 2 |
| line-4 | line-4-0322-0392-s001630 | station | forward | revenue | 1 |
| line-4 | line-4-0322-0392-s001630 | station | reverse | revenue | 1 |
| line-4 | line-4-0367-0335-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0381-0463-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0432-0561-s002382 | station | reverse | revenue | 2 |
| line-6 | line-6-0062-0440-s004192 | station | reverse | revenue | 2 |
| line-6 | line-6-0214-0301-s000000 | station | forward | revenue | 2 |
| line-7 | line-7-0361-0037-s006230 | station | reverse | revenue | 2 |
| line-7 | line-7-0366-0334-s000000 | station | forward | revenue | 2 |
| line-7 | line-7-0381-0267-s001464 | station | forward | revenue | 1 |
| line-7 | line-7-0381-0267-s001464 | station | reverse | revenue | 1 |
| line-8 | line-8-0497-0335-s000000 | station | forward | revenue | 2 |
| line-8 | line-8-0696-0391-s004467 | station | reverse | revenue | 2 |
| line-1 | line-1-0115-0301-s000000 | depot | — | revenue | 6 |
| line-1 | line-1-0115-0301-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0115-0301-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0679-0164-s009445 | depot | — | revenue | 12 |
| line-2 | line-2-0679-0164-s009445 | depot | — | spare | 2 |
| line-2 | line-2-0679-0164-s009445 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0333-0446-s000000 | depot | — | revenue | 3 |
| line-3 | line-3-0333-0446-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0333-0446-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0367-0335-s000000 | depot | — | revenue | 2 |
| line-4 | line-4-0367-0335-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0367-0335-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0381-0463-s000000 | depot | — | revenue | 2 |
| line-5 | line-5-0381-0463-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0381-0463-s000000 | depot | — | cold_reserve | 1 |
| line-6 | line-6-0214-0301-s000000 | depot | — | revenue | 5 |
| line-6 | line-6-0214-0301-s000000 | depot | — | spare | 1 |
| line-6 | line-6-0214-0301-s000000 | depot | — | cold_reserve | 1 |
| line-7 | line-7-0366-0334-s000000 | depot | — | revenue | 7 |
| line-7 | line-7-0366-0334-s000000 | depot | — | spare | 1 |
| line-7 | line-7-0366-0334-s000000 | depot | — | cold_reserve | 1 |
| line-8 | line-8-0497-0335-s000000 | depot | — | revenue | 6 |
| line-8 | line-8-0497-0335-s000000 | depot | — | spare | 1 |
| line-8 | line-8-0497-0335-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/dhamar-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **110 trainsets at 25 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **93 revenue, 9 spare, 8 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **60 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0115-0301-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0214-0301-s002240 | forward | revenue | 2 | pending |
| line-1 | line-1-0214-0301-s002240 | reverse | revenue | 2 | pending |
| line-1 | line-1-0306-0321-s004246 | forward | revenue | 2 | pending |
| line-1 | line-1-0306-0321-s004246 | reverse | revenue | 2 | pending |
| line-1 | line-1-0368-0335-s005602 | forward | revenue | 2 | pending |
| line-1 | line-1-0368-0335-s005602 | reverse | revenue | 2 | pending |
| line-1 | line-1-0445-0352-s007294 | reverse | revenue | 2 | pending |
| line-1 | line-1-0115-0301-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0214-0301-s002240 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0452-0384-s002391 | forward | revenue | 4 | pending |
| line-2 | line-2-0452-0384-s002391 | reverse | revenue | 3 | pending |
| line-2 | line-2-0497-0335-s003861 | forward | revenue | 3 | pending |
| line-2 | line-2-0497-0335-s003861 | reverse | revenue | 3 | pending |
| line-2 | line-2-0679-0164-s009445 | reverse | revenue | 3 | pending |
| line-2 | line-2-0452-0384-s002391 | reverse | spare | 1 | pending |
| line-2 | line-2-0497-0335-s003861 | forward | spare | 1 | pending |
| line-2 | line-2-0497-0335-s003861 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0322-0392-s001171 | forward | revenue | 2 | pending |
| line-3 | line-3-0322-0392-s001171 | reverse | revenue | 2 | pending |
| line-3 | line-3-0306-0321-s002724 | forward | revenue | 2 | pending |
| line-3 | line-3-0306-0321-s002724 | reverse | revenue | 2 | pending |
| line-3 | line-3-0295-0267-s003895 | reverse | revenue | 1 | pending |
| line-3 | line-3-0295-0267-s003895 | reverse | spare | 1 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0367-0335-s000000 | forward | revenue | 2 | pending |
| line-4 | line-4-0322-0392-s001630 | forward | revenue | 2 | pending |
| line-4 | line-4-0322-0392-s001630 | reverse | revenue | 2 | pending |
| line-4 | line-4-0288-0392-s002310 | reverse | revenue | 2 | pending |
| line-4 | line-4-0367-0335-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0322-0392-s001630 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0381-0463-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0432-0561-s002382 | reverse | revenue | 3 | pending |
| line-5 | line-5-0381-0463-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0432-0561-s002382 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0214-0301-s000000 | forward | revenue | 5 | pending |
| line-6 | line-6-0062-0440-s004192 | reverse | revenue | 4 | pending |
| line-6 | line-6-0062-0440-s004192 | reverse | spare | 1 | pending |
| line-6 | line-6-0214-0301-s000000 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-0366-0334-s000000 | forward | revenue | 4 | pending |
| line-7 | line-7-0381-0267-s001464 | forward | revenue | 3 | pending |
| line-7 | line-7-0381-0267-s001464 | reverse | revenue | 3 | pending |
| line-7 | line-7-0361-0037-s006230 | reverse | revenue | 3 | pending |
| line-7 | line-7-0381-0267-s001464 | forward | spare | 1 | pending |
| line-7 | line-7-0381-0267-s001464 | reverse | cold_reserve | 1 | pending |
| line-8 | line-8-0497-0335-s000000 | forward | revenue | 5 | pending |
| line-8 | line-8-0696-0391-s004467 | reverse | revenue | 5 | pending |
| line-8 | line-8-0497-0335-s000000 | forward | spare | 1 | pending |
| line-8 | line-8-0696-0391-s004467 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**46 trainsets exceed the reference platform envelope**, requiring **2,254.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0115-0301-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0214-0301-s002240 | 5 | 4 | 1 | 49.0 |
| line-1-0306-0321-s004246 | 4 | 4 | 0 | 0.0 |
| line-1-0368-0335-s005602 | 4 | 4 | 0 | 0.0 |
| line-1-0445-0352-s007294 | 2 | 2 | 0 | 0.0 |
| line-2-0381-0463-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0452-0384-s002391 | 8 | 2 | 6 | 294.0 |
| line-2-0497-0335-s003861 | 8 | 4 | 4 | 196.0 |
| line-2-0679-0164-s009445 | 3 | 2 | 1 | 49.0 |
| line-3-0295-0267-s003895 | 2 | 2 | 0 | 0.0 |
| line-3-0306-0321-s002724 | 4 | 4 | 0 | 0.0 |
| line-3-0322-0392-s001171 | 4 | 4 | 0 | 0.0 |
| line-3-0333-0446-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0288-0392-s002310 | 2 | 2 | 0 | 0.0 |
| line-4-0322-0392-s001630 | 5 | 4 | 1 | 49.0 |
| line-4-0367-0335-s000000 | 3 | 2 | 1 | 49.0 |
| line-5-0381-0463-s000000 | 4 | 2 | 2 | 98.0 |
| line-5-0432-0561-s002382 | 4 | 2 | 2 | 98.0 |
| line-6-0062-0440-s004192 | 5 | 2 | 3 | 147.0 |
| line-6-0214-0301-s000000 | 6 | 2 | 4 | 196.0 |
| line-7-0361-0037-s006230 | 3 | 2 | 1 | 49.0 |
| line-7-0366-0334-s000000 | 4 | 2 | 2 | 98.0 |
| line-7-0381-0267-s001464 | 8 | 2 | 6 | 294.0 |
| line-8-0497-0335-s000000 | 6 | 2 | 4 | 196.0 |
| line-8-0696-0391-s004467 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Dhamar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
