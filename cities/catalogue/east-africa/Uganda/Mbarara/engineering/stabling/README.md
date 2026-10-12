# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 154 at depots = 202 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0522-0784-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0262-0243-s000000 | line-2 | declared-depot | 28 | 1,666.0 | 6 |
| line-3-0129-0892-s026719 | line-3 | declared-depot | 70 | 4,165.0 | 12 |
| line-4-0689-0491-s000000 | line-4 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0522-0784-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0542-0690-s002263 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0690-s002263 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0574-s005664 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0574-s005664 | station | reverse | revenue | 1 |
| line-1 | line-1-0558-0613-s004072 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0613-s004072 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0429-s010465 | station | forward | revenue | 1 |
| line-1 | line-1-0647-0429-s010465 | station | reverse | revenue | 1 |
| line-1 | line-1-0696-0354-s012871 | station | reverse | revenue | 2 |
| line-2 | line-2-0262-0243-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0360-0365-s003510 | station | forward | revenue | 1 |
| line-2 | line-2-0360-0365-s003510 | station | reverse | revenue | 1 |
| line-2 | line-2-0537-0585-s009833 | station | forward | revenue | 1 |
| line-2 | line-2-0537-0585-s009833 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0613-s010625 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0613-s010625 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0678-s012493 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0678-s012493 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0697-s013033 | station | reverse | revenue | 2 |
| line-3 | line-3-0129-0892-s026719 | station | reverse | revenue | 2 |
| line-3 | line-3-0456-0638-s016054 | station | forward | revenue | 1 |
| line-3 | line-3-0456-0638-s016054 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0585-s013300 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0585-s013300 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0574-s012983 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0574-s012983 | station | reverse | revenue | 1 |
| line-3 | line-3-0689-0491-s008526 | station | forward | revenue | 1 |
| line-3 | line-3-0689-0491-s008526 | station | reverse | revenue | 1 |
| line-3 | line-3-0734-0445-s007008 | station | forward | revenue | 1 |
| line-3 | line-3-0734-0445-s007008 | station | reverse | revenue | 1 |
| line-3 | line-3-0954-0263-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0538-0688-s011952 | station | reverse | revenue | 2 |
| line-4 | line-4-0542-0690-s011856 | station | forward | revenue | 1 |
| line-4 | line-4-0542-0690-s011856 | station | reverse | revenue | 1 |
| line-4 | line-4-0611-0678-s009250 | station | forward | revenue | 1 |
| line-4 | line-4-0611-0678-s009250 | station | reverse | revenue | 1 |
| line-4 | line-4-0662-0613-s006867 | station | forward | revenue | 1 |
| line-4 | line-4-0662-0613-s006867 | station | reverse | revenue | 1 |
| line-4 | line-4-0689-0491-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0522-0784-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0522-0784-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0522-0784-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0262-0243-s000000 | depot | — | revenue | 24 |
| line-2 | line-2-0262-0243-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0262-0243-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0129-0892-s026719 | depot | — | revenue | 62 |
| line-3 | line-3-0129-0892-s026719 | depot | — | spare | 7 |
| line-3 | line-3-0129-0892-s026719 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0689-0491-s000000 | depot | — | revenue | 24 |
| line-4 | line-4-0689-0491-s000000 | depot | — | spare | 3 |
| line-4 | line-4-0689-0491-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbarara-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **202 trainsets at 24 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **182 revenue, 16 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **154 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0522-0784-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0690-s002263 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0690-s002263 | reverse | revenue | 4 | pending |
| line-1 | line-1-0558-0613-s004072 | forward | revenue | 4 | pending |
| line-1 | line-1-0558-0613-s004072 | reverse | revenue | 4 | pending |
| line-1 | line-1-0543-0574-s005664 | forward | revenue | 4 | pending |
| line-1 | line-1-0543-0574-s005664 | reverse | revenue | 3 | pending |
| line-1 | line-1-0647-0429-s010465 | forward | revenue | 3 | pending |
| line-1 | line-1-0647-0429-s010465 | reverse | revenue | 3 | pending |
| line-1 | line-1-0696-0354-s012871 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0574-s005664 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0429-s010465 | forward | spare | 1 | pending |
| line-1 | line-1-0647-0429-s010465 | reverse | spare | 1 | pending |
| line-1 | line-1-0696-0354-s012871 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0360-0365-s003510 | forward | revenue | 4 | pending |
| line-2 | line-2-0360-0365-s003510 | reverse | revenue | 4 | pending |
| line-2 | line-2-0537-0585-s009833 | forward | revenue | 4 | pending |
| line-2 | line-2-0537-0585-s009833 | reverse | revenue | 4 | pending |
| line-2 | line-2-0558-0613-s010625 | forward | revenue | 4 | pending |
| line-2 | line-2-0558-0613-s010625 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0678-s012493 | forward | revenue | 3 | pending |
| line-2 | line-2-0611-0678-s012493 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0697-s013033 | reverse | revenue | 3 | pending |
| line-2 | line-2-0558-0613-s010625 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0678-s012493 | forward | spare | 1 | pending |
| line-2 | line-2-0611-0678-s012493 | reverse | spare | 1 | pending |
| line-2 | line-2-0626-0697-s013033 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0734-0445-s007008 | forward | revenue | 7 | pending |
| line-3 | line-3-0734-0445-s007008 | reverse | revenue | 7 | pending |
| line-3 | line-3-0689-0491-s008526 | forward | revenue | 7 | pending |
| line-3 | line-3-0689-0491-s008526 | reverse | revenue | 6 | pending |
| line-3 | line-3-0543-0574-s012983 | forward | revenue | 6 | pending |
| line-3 | line-3-0543-0574-s012983 | reverse | revenue | 6 | pending |
| line-3 | line-3-0537-0585-s013300 | forward | revenue | 6 | pending |
| line-3 | line-3-0537-0585-s013300 | reverse | revenue | 6 | pending |
| line-3 | line-3-0456-0638-s016054 | forward | revenue | 6 | pending |
| line-3 | line-3-0456-0638-s016054 | reverse | revenue | 6 | pending |
| line-3 | line-3-0129-0892-s026719 | reverse | revenue | 6 | pending |
| line-3 | line-3-0689-0491-s008526 | reverse | spare | 1 | pending |
| line-3 | line-3-0543-0574-s012983 | forward | spare | 1 | pending |
| line-3 | line-3-0543-0574-s012983 | reverse | spare | 1 | pending |
| line-3 | line-3-0537-0585-s013300 | forward | spare | 1 | pending |
| line-3 | line-3-0537-0585-s013300 | reverse | spare | 1 | pending |
| line-3 | line-3-0456-0638-s016054 | forward | spare | 1 | pending |
| line-3 | line-3-0456-0638-s016054 | reverse | spare | 1 | pending |
| line-3 | line-3-0129-0892-s026719 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0689-0491-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0662-0613-s006867 | forward | revenue | 5 | pending |
| line-4 | line-4-0662-0613-s006867 | reverse | revenue | 4 | pending |
| line-4 | line-4-0611-0678-s009250 | forward | revenue | 4 | pending |
| line-4 | line-4-0611-0678-s009250 | reverse | revenue | 4 | pending |
| line-4 | line-4-0542-0690-s011856 | forward | revenue | 4 | pending |
| line-4 | line-4-0542-0690-s011856 | reverse | revenue | 4 | pending |
| line-4 | line-4-0538-0688-s011952 | reverse | revenue | 4 | pending |
| line-4 | line-4-0662-0613-s006867 | reverse | spare | 1 | pending |
| line-4 | line-4-0611-0678-s009250 | forward | spare | 1 | pending |
| line-4 | line-4-0611-0678-s009250 | reverse | spare | 1 | pending |
| line-4 | line-4-0542-0690-s011856 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**132 trainsets exceed the reference platform envelope**, requiring **7,854.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0522-0784-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0542-0690-s002263 | 8 | 4 | 4 | 238.0 |
| line-1-0543-0574-s005664 | 8 | 4 | 4 | 238.0 |
| line-1-0558-0613-s004072 | 8 | 4 | 4 | 238.0 |
| line-1-0647-0429-s010465 | 8 | 2 | 6 | 357.0 |
| line-1-0696-0354-s012871 | 4 | 2 | 2 | 119.0 |
| line-2-0262-0243-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0360-0365-s003510 | 8 | 2 | 6 | 357.0 |
| line-2-0537-0585-s009833 | 8 | 4 | 4 | 238.0 |
| line-2-0558-0613-s010625 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0678-s012493 | 8 | 4 | 4 | 238.0 |
| line-2-0626-0697-s013033 | 4 | 2 | 2 | 119.0 |
| line-3-0129-0892-s026719 | 7 | 2 | 5 | 297.5 |
| line-3-0456-0638-s016054 | 14 | 2 | 12 | 714.0 |
| line-3-0537-0585-s013300 | 14 | 4 | 10 | 595.0 |
| line-3-0543-0574-s012983 | 14 | 4 | 10 | 595.0 |
| line-3-0689-0491-s008526 | 14 | 4 | 10 | 595.0 |
| line-3-0734-0445-s007008 | 14 | 2 | 12 | 714.0 |
| line-3-0954-0263-s000000 | 7 | 2 | 5 | 297.5 |
| line-4-0538-0688-s011952 | 4 | 2 | 2 | 119.0 |
| line-4-0542-0690-s011856 | 9 | 4 | 5 | 297.5 |
| line-4-0611-0678-s009250 | 10 | 4 | 6 | 357.0 |
| line-4-0662-0613-s006867 | 10 | 2 | 8 | 476.0 |
| line-4-0689-0491-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbarara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
