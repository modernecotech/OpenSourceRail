# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 157 at depots = 199 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0244-0147-s021187 | line-1 | declared-depot | 52 | 3,094.0 | 10 |
| line-2-0250-0492-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 6 |
| line-3-0554-0343-s000000 | line-3 | declared-depot | 41 | 2,439.5 | 7 |
| line-4-0296-0217-s000000 | line-4 | declared-depot | 19 | 1,130.5 | 4 |
| line-5-0244-0147-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0244-0147-s021187 | station | reverse | revenue | 2 |
| line-1 | line-1-0296-0217-s018993 | station | forward | revenue | 1 |
| line-1 | line-1-0296-0217-s018993 | station | reverse | revenue | 1 |
| line-1 | line-1-0430-0490-s009884 | station | forward | revenue | 1 |
| line-1 | line-1-0430-0490-s009884 | station | reverse | revenue | 1 |
| line-1 | line-1-0431-0322-s015025 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0322-s015025 | station | reverse | revenue | 1 |
| line-1 | line-1-0468-0519-s008802 | station | forward | revenue | 1 |
| line-1 | line-1-0468-0519-s008802 | station | reverse | revenue | 1 |
| line-1 | line-1-0514-0823-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0529-0688-s003000 | station | forward | revenue | 1 |
| line-1 | line-1-0529-0688-s003000 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0545-s006613 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0545-s006613 | station | reverse | revenue | 1 |
| line-2 | line-2-0250-0492-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0430-0490-s005198 | station | forward | revenue | 1 |
| line-2 | line-2-0430-0490-s005198 | station | reverse | revenue | 1 |
| line-2 | line-2-0485-0486-s006466 | station | forward | revenue | 1 |
| line-2 | line-2-0485-0486-s006466 | station | reverse | revenue | 1 |
| line-2 | line-2-0562-0536-s009017 | station | forward | revenue | 1 |
| line-2 | line-2-0562-0536-s009017 | station | reverse | revenue | 1 |
| line-2 | line-2-0702-0472-s013622 | station | reverse | revenue | 2 |
| line-3 | line-3-0223-0982-s015850 | station | reverse | revenue | 2 |
| line-3 | line-3-0468-0519-s004350 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0519-s004350 | station | reverse | revenue | 1 |
| line-3 | line-3-0485-0486-s003531 | station | forward | revenue | 1 |
| line-3 | line-3-0485-0486-s003531 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0343-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0296-0217-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0437-0311-s006964 | station | reverse | revenue | 2 |
| line-5 | line-5-0062-0063-s004954 | station | reverse | revenue | 2 |
| line-5 | line-5-0244-0147-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0244-0147-s021187 | depot | — | revenue | 45 |
| line-1 | line-1-0244-0147-s021187 | depot | — | spare | 6 |
| line-1 | line-1-0244-0147-s021187 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0250-0492-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0250-0492-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0250-0492-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0554-0343-s000000 | depot | — | revenue | 36 |
| line-3 | line-3-0554-0343-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0554-0343-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0296-0217-s000000 | depot | — | revenue | 16 |
| line-4 | line-4-0296-0217-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0296-0217-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0244-0147-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0244-0147-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0244-0147-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/polokwane-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **199 trainsets at 21 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **178 revenue, 16 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **157 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0514-0823-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0529-0688-s003000 | forward | revenue | 5 | pending |
| line-1 | line-1-0529-0688-s003000 | reverse | revenue | 5 | pending |
| line-1 | line-1-0543-0545-s006613 | forward | revenue | 5 | pending |
| line-1 | line-1-0543-0545-s006613 | reverse | revenue | 5 | pending |
| line-1 | line-1-0468-0519-s008802 | forward | revenue | 4 | pending |
| line-1 | line-1-0468-0519-s008802 | reverse | revenue | 4 | pending |
| line-1 | line-1-0430-0490-s009884 | forward | revenue | 4 | pending |
| line-1 | line-1-0430-0490-s009884 | reverse | revenue | 4 | pending |
| line-1 | line-1-0431-0322-s015025 | forward | revenue | 4 | pending |
| line-1 | line-1-0431-0322-s015025 | reverse | revenue | 4 | pending |
| line-1 | line-1-0296-0217-s018993 | forward | revenue | 4 | pending |
| line-1 | line-1-0296-0217-s018993 | reverse | revenue | 4 | pending |
| line-1 | line-1-0244-0147-s021187 | reverse | revenue | 4 | pending |
| line-1 | line-1-0468-0519-s008802 | forward | spare | 1 | pending |
| line-1 | line-1-0468-0519-s008802 | reverse | spare | 1 | pending |
| line-1 | line-1-0430-0490-s009884 | forward | spare | 1 | pending |
| line-1 | line-1-0430-0490-s009884 | reverse | spare | 1 | pending |
| line-1 | line-1-0431-0322-s015025 | forward | spare | 1 | pending |
| line-1 | line-1-0431-0322-s015025 | reverse | spare | 1 | pending |
| line-1 | line-1-0296-0217-s018993 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0430-0490-s005198 | forward | revenue | 5 | pending |
| line-2 | line-2-0430-0490-s005198 | reverse | revenue | 5 | pending |
| line-2 | line-2-0485-0486-s006466 | forward | revenue | 5 | pending |
| line-2 | line-2-0485-0486-s006466 | reverse | revenue | 5 | pending |
| line-2 | line-2-0562-0536-s009017 | forward | revenue | 5 | pending |
| line-2 | line-2-0562-0536-s009017 | reverse | revenue | 5 | pending |
| line-2 | line-2-0702-0472-s013622 | reverse | revenue | 4 | pending |
| line-2 | line-2-0702-0472-s013622 | reverse | spare | 1 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0430-0490-s005198 | forward | spare | 1 | pending |
| line-2 | line-2-0430-0490-s005198 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0485-0486-s003531 | forward | revenue | 8 | pending |
| line-3 | line-3-0485-0486-s003531 | reverse | revenue | 7 | pending |
| line-3 | line-3-0468-0519-s004350 | forward | revenue | 7 | pending |
| line-3 | line-3-0468-0519-s004350 | reverse | revenue | 7 | pending |
| line-3 | line-3-0223-0982-s015850 | reverse | revenue | 7 | pending |
| line-3 | line-3-0485-0486-s003531 | reverse | spare | 1 | pending |
| line-3 | line-3-0468-0519-s004350 | forward | spare | 1 | pending |
| line-3 | line-3-0468-0519-s004350 | reverse | spare | 1 | pending |
| line-3 | line-3-0223-0982-s015850 | reverse | spare | 1 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0296-0217-s000000 | forward | revenue | 10 | pending |
| line-4 | line-4-0437-0311-s006964 | reverse | revenue | 10 | pending |
| line-4 | line-4-0296-0217-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0437-0311-s006964 | reverse | spare | 1 | pending |
| line-4 | line-4-0296-0217-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0244-0147-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0062-0063-s004954 | reverse | revenue | 7 | pending |
| line-5 | line-5-0244-0147-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0062-0063-s004954 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**137 trainsets exceed the reference platform envelope**, requiring **8,151.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0244-0147-s021187 | 4 | 2 | 2 | 119.0 |
| line-1-0296-0217-s018993 | 9 | 4 | 5 | 297.5 |
| line-1-0430-0490-s009884 | 10 | 4 | 6 | 357.0 |
| line-1-0431-0322-s015025 | 10 | 4 | 6 | 357.0 |
| line-1-0468-0519-s008802 | 10 | 4 | 6 | 357.0 |
| line-1-0514-0823-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0529-0688-s003000 | 10 | 2 | 8 | 476.0 |
| line-1-0543-0545-s006613 | 10 | 4 | 6 | 357.0 |
| line-2-0250-0492-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0430-0490-s005198 | 12 | 4 | 8 | 476.0 |
| line-2-0485-0486-s006466 | 10 | 4 | 6 | 357.0 |
| line-2-0562-0536-s009017 | 10 | 4 | 6 | 357.0 |
| line-2-0702-0472-s013622 | 5 | 2 | 3 | 178.5 |
| line-3-0223-0982-s015850 | 8 | 2 | 6 | 357.0 |
| line-3-0468-0519-s004350 | 16 | 4 | 12 | 714.0 |
| line-3-0485-0486-s003531 | 16 | 4 | 12 | 714.0 |
| line-3-0554-0343-s000000 | 9 | 2 | 7 | 416.5 |
| line-4-0296-0217-s000000 | 12 | 2 | 10 | 595.0 |
| line-4-0437-0311-s006964 | 11 | 2 | 9 | 535.5 |
| line-5-0062-0063-s004954 | 8 | 2 | 6 | 357.0 |
| line-5-0244-0147-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Polokwane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
