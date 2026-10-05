# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 119 at depots = 155 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0910-0952-s020624 | line-1 | declared-depot | 49 | 2,915.5 | 9 |
| line-2-0173-0684-s000000 | line-2 | declared-depot | 28 | 1,666.0 | 6 |
| line-3-0230-1062-s000000 | line-3 | declared-depot | 42 | 2,499.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0317-0298-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0424-0406-s003433 | station | forward | revenue | 1 |
| line-1 | line-1-0424-0406-s003433 | station | reverse | revenue | 1 |
| line-1 | line-1-0518-0502-s006448 | station | forward | revenue | 1 |
| line-1 | line-1-0518-0502-s006448 | station | reverse | revenue | 1 |
| line-1 | line-1-0538-0522-s007037 | station | forward | revenue | 1 |
| line-1 | line-1-0538-0522-s007037 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0586-s009062 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0586-s009062 | station | reverse | revenue | 1 |
| line-1 | line-1-0664-0650-s011086 | station | forward | revenue | 1 |
| line-1 | line-1-0664-0650-s011086 | station | reverse | revenue | 1 |
| line-1 | line-1-0910-0952-s020624 | station | reverse | revenue | 2 |
| line-2 | line-2-0173-0684-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0376-0607-s005630 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0607-s005630 | station | reverse | revenue | 1 |
| line-2 | line-2-0447-0556-s007613 | station | forward | revenue | 1 |
| line-2 | line-2-0447-0556-s007613 | station | reverse | revenue | 1 |
| line-2 | line-2-0520-0504-s009621 | station | forward | revenue | 1 |
| line-2 | line-2-0520-0504-s009621 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0475-s010752 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0475-s010752 | station | reverse | revenue | 1 |
| line-2 | line-2-0636-0421-s012804 | station | reverse | revenue | 2 |
| line-3 | line-3-0230-1062-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0469-0663-s010042 | station | forward | revenue | 1 |
| line-3 | line-3-0469-0663-s010042 | station | reverse | revenue | 1 |
| line-3 | line-3-0538-0522-s013516 | station | forward | revenue | 1 |
| line-3 | line-3-0538-0522-s013516 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0475-s014670 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0475-s014670 | station | reverse | revenue | 1 |
| line-3 | line-3-0586-0425-s015888 | station | reverse | revenue | 2 |
| line-1 | line-1-0910-0952-s020624 | depot | — | revenue | 43 |
| line-1 | line-1-0910-0952-s020624 | depot | — | spare | 5 |
| line-1 | line-1-0910-0952-s020624 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0173-0684-s000000 | depot | — | revenue | 24 |
| line-2 | line-2-0173-0684-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0173-0684-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0230-1062-s000000 | depot | — | revenue | 37 |
| line-3 | line-3-0230-1062-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0230-1062-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/deir-ez-zor-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **155 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **140 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **119 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0317-0298-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0424-0406-s003433 | forward | revenue | 5 | pending |
| line-1 | line-1-0424-0406-s003433 | reverse | revenue | 5 | pending |
| line-1 | line-1-0518-0502-s006448 | forward | revenue | 5 | pending |
| line-1 | line-1-0518-0502-s006448 | reverse | revenue | 5 | pending |
| line-1 | line-1-0538-0522-s007037 | forward | revenue | 5 | pending |
| line-1 | line-1-0538-0522-s007037 | reverse | revenue | 5 | pending |
| line-1 | line-1-0601-0586-s009062 | forward | revenue | 5 | pending |
| line-1 | line-1-0601-0586-s009062 | reverse | revenue | 5 | pending |
| line-1 | line-1-0664-0650-s011086 | forward | revenue | 4 | pending |
| line-1 | line-1-0664-0650-s011086 | reverse | revenue | 4 | pending |
| line-1 | line-1-0910-0952-s020624 | reverse | revenue | 4 | pending |
| line-1 | line-1-0664-0650-s011086 | forward | spare | 1 | pending |
| line-1 | line-1-0664-0650-s011086 | reverse | spare | 1 | pending |
| line-1 | line-1-0910-0952-s020624 | reverse | spare | 1 | pending |
| line-1 | line-1-0317-0298-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0406-s003433 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0406-s003433 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0173-0684-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0376-0607-s005630 | forward | revenue | 4 | pending |
| line-2 | line-2-0376-0607-s005630 | reverse | revenue | 4 | pending |
| line-2 | line-2-0447-0556-s007613 | forward | revenue | 4 | pending |
| line-2 | line-2-0447-0556-s007613 | reverse | revenue | 4 | pending |
| line-2 | line-2-0520-0504-s009621 | forward | revenue | 4 | pending |
| line-2 | line-2-0520-0504-s009621 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0475-s010752 | forward | revenue | 3 | pending |
| line-2 | line-2-0561-0475-s010752 | reverse | revenue | 3 | pending |
| line-2 | line-2-0636-0421-s012804 | reverse | revenue | 3 | pending |
| line-2 | line-2-0520-0504-s009621 | reverse | spare | 1 | pending |
| line-2 | line-2-0561-0475-s010752 | forward | spare | 1 | pending |
| line-2 | line-2-0561-0475-s010752 | reverse | spare | 1 | pending |
| line-2 | line-2-0636-0421-s012804 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0469-0663-s010042 | forward | revenue | 6 | pending |
| line-3 | line-3-0469-0663-s010042 | reverse | revenue | 6 | pending |
| line-3 | line-3-0538-0522-s013516 | forward | revenue | 6 | pending |
| line-3 | line-3-0538-0522-s013516 | reverse | revenue | 6 | pending |
| line-3 | line-3-0561-0475-s014670 | forward | revenue | 6 | pending |
| line-3 | line-3-0561-0475-s014670 | reverse | revenue | 6 | pending |
| line-3 | line-3-0586-0425-s015888 | reverse | revenue | 5 | pending |
| line-3 | line-3-0586-0425-s015888 | reverse | spare | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0469-0663-s010042 | forward | spare | 1 | pending |
| line-3 | line-3-0469-0663-s010042 | reverse | spare | 1 | pending |
| line-3 | line-3-0538-0522-s013516 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0317-0298-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0424-0406-s003433 | 12 | 2 | 10 | 595.0 |
| line-1-0518-0502-s006448 | 10 | 4 | 6 | 357.0 |
| line-1-0538-0522-s007037 | 10 | 4 | 6 | 357.0 |
| line-1-0601-0586-s009062 | 10 | 2 | 8 | 476.0 |
| line-1-0664-0650-s011086 | 10 | 2 | 8 | 476.0 |
| line-1-0910-0952-s020624 | 5 | 2 | 3 | 178.5 |
| line-2-0173-0684-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0376-0607-s005630 | 8 | 2 | 6 | 357.0 |
| line-2-0447-0556-s007613 | 8 | 2 | 6 | 357.0 |
| line-2-0520-0504-s009621 | 8 | 4 | 4 | 238.0 |
| line-2-0561-0475-s010752 | 8 | 4 | 4 | 238.0 |
| line-2-0636-0421-s012804 | 4 | 2 | 2 | 119.0 |
| line-3-0230-1062-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0469-0663-s010042 | 14 | 2 | 12 | 714.0 |
| line-3-0538-0522-s013516 | 13 | 4 | 9 | 535.5 |
| line-3-0561-0475-s014670 | 12 | 4 | 8 | 476.0 |
| line-3-0586-0425-s015888 | 6 | 2 | 4 | 238.0 |

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
