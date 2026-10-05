# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 120 at depots = 158 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0976-0042-s000000 | line-1 | declared-depot | 45 | 2,677.5 | 9 |
| line-2-1038-0227-s019696 | line-2 | declared-depot | 46 | 2,737.0 | 9 |
| line-3-0961-0680-s000000 | line-3 | declared-depot | 29 | 1,725.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0619-0784-s018346 | station | reverse | revenue | 2 |
| line-1 | line-1-0669-0684-s015862 | station | forward | revenue | 1 |
| line-1 | line-1-0669-0684-s015862 | station | reverse | revenue | 1 |
| line-1 | line-1-0719-0584-s013389 | station | forward | revenue | 1 |
| line-1 | line-1-0719-0584-s013389 | station | reverse | revenue | 1 |
| line-1 | line-1-0780-0462-s010362 | station | forward | revenue | 1 |
| line-1 | line-1-0780-0462-s010362 | station | reverse | revenue | 1 |
| line-1 | line-1-0841-0341-s007354 | station | forward | revenue | 1 |
| line-1 | line-1-0841-0341-s007354 | station | reverse | revenue | 1 |
| line-1 | line-1-0936-0166-s003009 | station | forward | revenue | 1 |
| line-1 | line-1-0936-0166-s003009 | station | reverse | revenue | 1 |
| line-1 | line-1-0976-0042-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0617-0977-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0692-0881-s003496 | station | forward | revenue | 1 |
| line-2 | line-2-0692-0881-s003496 | station | reverse | revenue | 1 |
| line-2 | line-2-0750-0733-s007008 | station | forward | revenue | 1 |
| line-2 | line-2-0750-0733-s007008 | station | reverse | revenue | 1 |
| line-2 | line-2-0791-0645-s009167 | station | forward | revenue | 1 |
| line-2 | line-2-0791-0645-s009167 | station | reverse | revenue | 1 |
| line-2 | line-2-0833-0556-s011318 | station | forward | revenue | 1 |
| line-2 | line-2-0833-0556-s011318 | station | reverse | revenue | 1 |
| line-2 | line-2-0899-0413-s014807 | station | forward | revenue | 1 |
| line-2 | line-2-0899-0413-s014807 | station | reverse | revenue | 1 |
| line-2 | line-2-1038-0227-s019696 | station | reverse | revenue | 2 |
| line-3 | line-3-0356-0613-s012667 | station | reverse | revenue | 2 |
| line-3 | line-3-0530-0630-s009046 | station | forward | revenue | 1 |
| line-3 | line-3-0530-0630-s009046 | station | reverse | revenue | 1 |
| line-3 | line-3-0675-0643-s006027 | station | forward | revenue | 1 |
| line-3 | line-3-0675-0643-s006027 | station | reverse | revenue | 1 |
| line-3 | line-3-0820-0657-s003011 | station | forward | revenue | 1 |
| line-3 | line-3-0820-0657-s003011 | station | reverse | revenue | 1 |
| line-3 | line-3-0961-0680-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0976-0042-s000000 | depot | — | revenue | 39 |
| line-1 | line-1-0976-0042-s000000 | depot | — | spare | 5 |
| line-1 | line-1-0976-0042-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1038-0227-s019696 | depot | — | revenue | 40 |
| line-2 | line-2-1038-0227-s019696 | depot | — | spare | 5 |
| line-2 | line-2-1038-0227-s019696 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0961-0680-s000000 | depot | — | revenue | 25 |
| line-3 | line-3-0961-0680-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0961-0680-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/najran-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **158 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **142 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **120 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0976-0042-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0936-0166-s003009 | forward | revenue | 5 | pending |
| line-1 | line-1-0936-0166-s003009 | reverse | revenue | 5 | pending |
| line-1 | line-1-0841-0341-s007354 | forward | revenue | 5 | pending |
| line-1 | line-1-0841-0341-s007354 | reverse | revenue | 5 | pending |
| line-1 | line-1-0780-0462-s010362 | forward | revenue | 4 | pending |
| line-1 | line-1-0780-0462-s010362 | reverse | revenue | 4 | pending |
| line-1 | line-1-0719-0584-s013389 | forward | revenue | 4 | pending |
| line-1 | line-1-0719-0584-s013389 | reverse | revenue | 4 | pending |
| line-1 | line-1-0669-0684-s015862 | forward | revenue | 4 | pending |
| line-1 | line-1-0669-0684-s015862 | reverse | revenue | 4 | pending |
| line-1 | line-1-0619-0784-s018346 | reverse | revenue | 4 | pending |
| line-1 | line-1-0780-0462-s010362 | forward | spare | 1 | pending |
| line-1 | line-1-0780-0462-s010362 | reverse | spare | 1 | pending |
| line-1 | line-1-0719-0584-s013389 | forward | spare | 1 | pending |
| line-1 | line-1-0719-0584-s013389 | reverse | spare | 1 | pending |
| line-1 | line-1-0669-0684-s015862 | forward | spare | 1 | pending |
| line-1 | line-1-0669-0684-s015862 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0617-0977-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0692-0881-s003496 | forward | revenue | 5 | pending |
| line-2 | line-2-0692-0881-s003496 | reverse | revenue | 5 | pending |
| line-2 | line-2-0750-0733-s007008 | forward | revenue | 5 | pending |
| line-2 | line-2-0750-0733-s007008 | reverse | revenue | 5 | pending |
| line-2 | line-2-0791-0645-s009167 | forward | revenue | 5 | pending |
| line-2 | line-2-0791-0645-s009167 | reverse | revenue | 4 | pending |
| line-2 | line-2-0833-0556-s011318 | forward | revenue | 4 | pending |
| line-2 | line-2-0833-0556-s011318 | reverse | revenue | 4 | pending |
| line-2 | line-2-0899-0413-s014807 | forward | revenue | 4 | pending |
| line-2 | line-2-0899-0413-s014807 | reverse | revenue | 4 | pending |
| line-2 | line-2-1038-0227-s019696 | reverse | revenue | 4 | pending |
| line-2 | line-2-0791-0645-s009167 | reverse | spare | 1 | pending |
| line-2 | line-2-0833-0556-s011318 | forward | spare | 1 | pending |
| line-2 | line-2-0833-0556-s011318 | reverse | spare | 1 | pending |
| line-2 | line-2-0899-0413-s014807 | forward | spare | 1 | pending |
| line-2 | line-2-0899-0413-s014807 | reverse | spare | 1 | pending |
| line-2 | line-2-1038-0227-s019696 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0961-0680-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0820-0657-s003011 | forward | revenue | 5 | pending |
| line-3 | line-3-0820-0657-s003011 | reverse | revenue | 5 | pending |
| line-3 | line-3-0675-0643-s006027 | forward | revenue | 4 | pending |
| line-3 | line-3-0675-0643-s006027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0530-0630-s009046 | forward | revenue | 4 | pending |
| line-3 | line-3-0530-0630-s009046 | reverse | revenue | 4 | pending |
| line-3 | line-3-0356-0613-s012667 | reverse | revenue | 4 | pending |
| line-3 | line-3-0675-0643-s006027 | forward | spare | 1 | pending |
| line-3 | line-3-0675-0643-s006027 | reverse | spare | 1 | pending |
| line-3 | line-3-0530-0630-s009046 | forward | spare | 1 | pending |
| line-3 | line-3-0530-0630-s009046 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**116 trainsets exceed the reference platform envelope**, requiring **6,902.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0619-0784-s018346 | 4 | 2 | 2 | 119.0 |
| line-1-0669-0684-s015862 | 10 | 2 | 8 | 476.0 |
| line-1-0719-0584-s013389 | 10 | 2 | 8 | 476.0 |
| line-1-0780-0462-s010362 | 10 | 2 | 8 | 476.0 |
| line-1-0841-0341-s007354 | 10 | 2 | 8 | 476.0 |
| line-1-0936-0166-s003009 | 10 | 2 | 8 | 476.0 |
| line-1-0976-0042-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0617-0977-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0692-0881-s003496 | 10 | 2 | 8 | 476.0 |
| line-2-0750-0733-s007008 | 10 | 2 | 8 | 476.0 |
| line-2-0791-0645-s009167 | 10 | 4 | 6 | 357.0 |
| line-2-0833-0556-s011318 | 10 | 2 | 8 | 476.0 |
| line-2-0899-0413-s014807 | 10 | 2 | 8 | 476.0 |
| line-2-1038-0227-s019696 | 5 | 2 | 3 | 178.5 |
| line-3-0356-0613-s012667 | 4 | 2 | 2 | 119.0 |
| line-3-0530-0630-s009046 | 10 | 2 | 8 | 476.0 |
| line-3-0675-0643-s006027 | 10 | 2 | 8 | 476.0 |
| line-3-0820-0657-s003011 | 10 | 4 | 6 | 357.0 |
| line-3-0961-0680-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Najran/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
