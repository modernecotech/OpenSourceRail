# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 125 at depots = 155 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0910-0952-s020624 | line-1 | declared-depot | 53 | 3,153.5 | 9 |
| line-2-0173-0684-s000000 | line-2 | declared-depot | 29 | 1,725.5 | 6 |
| line-3-0230-1062-s000000 | line-3 | declared-depot | 43 | 2,558.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0317-0298-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0424-0406-s003433 | station | forward | revenue | 1 |
| line-1 | line-1-0424-0406-s003433 | station | reverse | revenue | 1 |
| line-1 | line-1-0490-0473-s005519 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0473-s005519 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0539-s007580 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0539-s007580 | station | reverse | revenue | 1 |
| line-1 | line-1-0664-0650-s011086 | station | forward | revenue | 1 |
| line-1 | line-1-0664-0650-s011086 | station | reverse | revenue | 1 |
| line-1 | line-1-0910-0952-s020624 | station | reverse | revenue | 2 |
| line-2 | line-2-0173-0684-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0376-0607-s005630 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0607-s005630 | station | reverse | revenue | 1 |
| line-2 | line-2-0484-0530-s008639 | station | forward | revenue | 1 |
| line-2 | line-2-0484-0530-s008639 | station | reverse | revenue | 1 |
| line-2 | line-2-0560-0476-s010712 | station | forward | revenue | 1 |
| line-2 | line-2-0560-0476-s010712 | station | reverse | revenue | 1 |
| line-2 | line-2-0636-0421-s012804 | station | reverse | revenue | 2 |
| line-3 | line-3-0230-1062-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0469-0663-s010042 | station | forward | revenue | 1 |
| line-3 | line-3-0469-0663-s010042 | station | reverse | revenue | 1 |
| line-3 | line-3-0530-0540-s013089 | station | forward | revenue | 1 |
| line-3 | line-3-0530-0540-s013089 | station | reverse | revenue | 1 |
| line-3 | line-3-0586-0425-s015888 | station | reverse | revenue | 2 |
| line-1 | line-1-0910-0952-s020624 | depot | — | revenue | 47 |
| line-1 | line-1-0910-0952-s020624 | depot | — | spare | 5 |
| line-1 | line-1-0910-0952-s020624 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0173-0684-s000000 | depot | — | revenue | 25 |
| line-2 | line-2-0173-0684-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0173-0684-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0230-1062-s000000 | depot | — | revenue | 38 |
| line-3 | line-3-0230-1062-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0230-1062-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/deir-ez-zor-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **155 trainsets at 15 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **140 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **125 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0317-0298-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0424-0406-s003433 | forward | revenue | 6 | pending |
| line-1 | line-1-0424-0406-s003433 | reverse | revenue | 6 | pending |
| line-1 | line-1-0490-0473-s005519 | forward | revenue | 6 | pending |
| line-1 | line-1-0490-0473-s005519 | reverse | revenue | 6 | pending |
| line-1 | line-1-0554-0539-s007580 | forward | revenue | 6 | pending |
| line-1 | line-1-0554-0539-s007580 | reverse | revenue | 6 | pending |
| line-1 | line-1-0664-0650-s011086 | forward | revenue | 6 | pending |
| line-1 | line-1-0664-0650-s011086 | reverse | revenue | 6 | pending |
| line-1 | line-1-0910-0952-s020624 | reverse | revenue | 5 | pending |
| line-1 | line-1-0910-0952-s020624 | reverse | spare | 1 | pending |
| line-1 | line-1-0317-0298-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0406-s003433 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0406-s003433 | reverse | spare | 1 | pending |
| line-1 | line-1-0490-0473-s005519 | forward | spare | 1 | pending |
| line-1 | line-1-0490-0473-s005519 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0173-0684-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0376-0607-s005630 | forward | revenue | 5 | pending |
| line-2 | line-2-0376-0607-s005630 | reverse | revenue | 5 | pending |
| line-2 | line-2-0484-0530-s008639 | forward | revenue | 4 | pending |
| line-2 | line-2-0484-0530-s008639 | reverse | revenue | 4 | pending |
| line-2 | line-2-0560-0476-s010712 | forward | revenue | 4 | pending |
| line-2 | line-2-0560-0476-s010712 | reverse | revenue | 4 | pending |
| line-2 | line-2-0636-0421-s012804 | reverse | revenue | 4 | pending |
| line-2 | line-2-0484-0530-s008639 | forward | spare | 1 | pending |
| line-2 | line-2-0484-0530-s008639 | reverse | spare | 1 | pending |
| line-2 | line-2-0560-0476-s010712 | forward | spare | 1 | pending |
| line-2 | line-2-0560-0476-s010712 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0469-0663-s010042 | forward | revenue | 8 | pending |
| line-3 | line-3-0469-0663-s010042 | reverse | revenue | 8 | pending |
| line-3 | line-3-0530-0540-s013089 | forward | revenue | 8 | pending |
| line-3 | line-3-0530-0540-s013089 | reverse | revenue | 7 | pending |
| line-3 | line-3-0586-0425-s015888 | reverse | revenue | 7 | pending |
| line-3 | line-3-0530-0540-s013089 | reverse | spare | 1 | pending |
| line-3 | line-3-0586-0425-s015888 | reverse | spare | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0469-0663-s010042 | forward | spare | 1 | pending |
| line-3 | line-3-0469-0663-s010042 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**121 trainsets exceed the reference platform envelope**, requiring **7,199.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0317-0298-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0424-0406-s003433 | 14 | 2 | 12 | 714.0 |
| line-1-0490-0473-s005519 | 14 | 2 | 12 | 714.0 |
| line-1-0554-0539-s007580 | 12 | 4 | 8 | 476.0 |
| line-1-0664-0650-s011086 | 12 | 2 | 10 | 595.0 |
| line-1-0910-0952-s020624 | 6 | 2 | 4 | 238.0 |
| line-2-0173-0684-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0376-0607-s005630 | 10 | 2 | 8 | 476.0 |
| line-2-0484-0530-s008639 | 10 | 2 | 8 | 476.0 |
| line-2-0560-0476-s010712 | 10 | 2 | 8 | 476.0 |
| line-2-0636-0421-s012804 | 4 | 2 | 2 | 119.0 |
| line-3-0230-1062-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0469-0663-s010042 | 18 | 2 | 16 | 952.0 |
| line-3-0530-0540-s013089 | 16 | 4 | 12 | 714.0 |
| line-3-0586-0425-s015888 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Deir-Ez-Zor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
