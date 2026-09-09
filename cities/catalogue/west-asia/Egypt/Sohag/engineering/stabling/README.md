# Station and depot overnight allocation

Plan: **28 trainsets at stations + 70 at depots = 98 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0493-0475-s009024 | line-1 | storage-at-existing-powered-service-point | 12 | 714.0 | 0 |
| line-2-1096-0417-s016706 | line-2 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |
| line-3-1014-1054-s018676 | line-3 | declared-depot | 31 | 1,844.5 | 15 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0493-0475-s009024 | station | reverse | revenue | 2 |
| line-1 | line-1-0499-0673-s003049 | station | forward | revenue | 1 |
| line-1 | line-1-0499-0673-s003049 | station | reverse | revenue | 1 |
| line-1 | line-1-0509-0798-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0559-0556-s006410 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0556-s006410 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0605-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0591-0566-s002100 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0566-s002100 | station | reverse | revenue | 1 |
| line-2 | line-2-0726-0575-s005101 | station | forward | revenue | 1 |
| line-2 | line-2-0726-0575-s005101 | station | reverse | revenue | 1 |
| line-2 | line-2-0761-0446-s008592 | station | forward | revenue | 1 |
| line-2 | line-2-0761-0446-s008592 | station | reverse | revenue | 1 |
| line-2 | line-2-1096-0417-s016706 | station | reverse | revenue | 2 |
| line-3 | line-3-0531-0609-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0559-0556-s001315 | station | forward | revenue | 1 |
| line-3 | line-3-0559-0556-s001315 | station | reverse | revenue | 1 |
| line-3 | line-3-0606-0545-s002665 | station | forward | revenue | 1 |
| line-3 | line-3-0606-0545-s002665 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0622-s005674 | station | forward | revenue | 1 |
| line-3 | line-3-0698-0622-s005674 | station | reverse | revenue | 1 |
| line-3 | line-3-1014-1054-s018676 | station | reverse | revenue | 2 |
| line-1 | line-1-0493-0475-s009024 | depot | — | revenue | 10 |
| line-1 | line-1-0493-0475-s009024 | depot | — | spare | 1 |
| line-1 | line-1-0493-0475-s009024 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1096-0417-s016706 | depot | — | revenue | 23 |
| line-2 | line-2-1096-0417-s016706 | depot | — | spare | 3 |
| line-2 | line-2-1096-0417-s016706 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1014-1054-s018676 | depot | — | revenue | 27 |
| line-3 | line-3-1014-1054-s018676 | depot | — | spare | 3 |
| line-3 | line-3-1014-1054-s018676 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sohag-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **98 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **88 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **70 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0509-0798-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0499-0673-s003049 | forward | revenue | 3 | pending |
| line-1 | line-1-0499-0673-s003049 | reverse | revenue | 3 | pending |
| line-1 | line-1-0559-0556-s006410 | forward | revenue | 3 | pending |
| line-1 | line-1-0559-0556-s006410 | reverse | revenue | 3 | pending |
| line-1 | line-1-0493-0475-s009024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0509-0798-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0499-0673-s003049 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0561-0605-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0591-0566-s002100 | forward | revenue | 4 | pending |
| line-2 | line-2-0591-0566-s002100 | reverse | revenue | 4 | pending |
| line-2 | line-2-0726-0575-s005101 | forward | revenue | 4 | pending |
| line-2 | line-2-0726-0575-s005101 | reverse | revenue | 4 | pending |
| line-2 | line-2-0761-0446-s008592 | forward | revenue | 4 | pending |
| line-2 | line-2-0761-0446-s008592 | reverse | revenue | 4 | pending |
| line-2 | line-2-1096-0417-s016706 | reverse | revenue | 4 | pending |
| line-2 | line-2-0591-0566-s002100 | forward | spare | 1 | pending |
| line-2 | line-2-0591-0566-s002100 | reverse | spare | 1 | pending |
| line-2 | line-2-0726-0575-s005101 | forward | spare | 1 | pending |
| line-2 | line-2-0726-0575-s005101 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0531-0609-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0559-0556-s001315 | forward | revenue | 5 | pending |
| line-3 | line-3-0559-0556-s001315 | reverse | revenue | 5 | pending |
| line-3 | line-3-0606-0545-s002665 | forward | revenue | 5 | pending |
| line-3 | line-3-0606-0545-s002665 | reverse | revenue | 5 | pending |
| line-3 | line-3-0698-0622-s005674 | forward | revenue | 4 | pending |
| line-3 | line-3-0698-0622-s005674 | reverse | revenue | 4 | pending |
| line-3 | line-3-1014-1054-s018676 | reverse | revenue | 4 | pending |
| line-3 | line-3-0698-0622-s005674 | forward | spare | 1 | pending |
| line-3 | line-3-0698-0622-s005674 | reverse | spare | 1 | pending |
| line-3 | line-3-1014-1054-s018676 | reverse | spare | 1 | pending |
| line-3 | line-3-0531-0609-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**62 trainsets exceed the reference platform envelope**, requiring **3,689.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0493-0475-s009024 | 3 | 2 | 1 | 59.5 |
| line-1-0499-0673-s003049 | 7 | 2 | 5 | 297.5 |
| line-1-0509-0798-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0559-0556-s006410 | 6 | 4 | 2 | 119.0 |
| line-2-0561-0605-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0591-0566-s002100 | 10 | 4 | 6 | 357.0 |
| line-2-0726-0575-s005101 | 10 | 2 | 8 | 476.0 |
| line-2-0761-0446-s008592 | 8 | 2 | 6 | 357.0 |
| line-2-1096-0417-s016706 | 4 | 2 | 2 | 119.0 |
| line-3-0531-0609-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0559-0556-s001315 | 10 | 4 | 6 | 357.0 |
| line-3-0606-0545-s002665 | 10 | 4 | 6 | 357.0 |
| line-3-0698-0622-s005674 | 10 | 2 | 8 | 476.0 |
| line-3-1014-1054-s018676 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Sohag/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
