# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 131 at depots = 163 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0308-0707-s000000 | line-1 | declared-depot | 44 | 2,618.0 | 8 |
| line-2-0332-0209-s022153 | line-2 | declared-depot | 55 | 3,272.5 | 10 |
| line-3-0424-0761-s000000 | line-3 | declared-depot | 32 | 1,904.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0308-0707-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0434-0653-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0653-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0515-0618-s004959 | station | forward | revenue | 1 |
| line-1 | line-1-0515-0618-s004959 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0564-s007970 | station | forward | revenue | 1 |
| line-1 | line-1-0642-0564-s007970 | station | reverse | revenue | 1 |
| line-1 | line-1-1041-0391-s017456 | station | reverse | revenue | 2 |
| line-2 | line-2-0332-0209-s022153 | station | reverse | revenue | 2 |
| line-2 | line-2-0502-0423-s016057 | station | forward | revenue | 1 |
| line-2 | line-2-0502-0423-s016057 | station | reverse | revenue | 1 |
| line-2 | line-2-0586-0527-s013047 | station | forward | revenue | 1 |
| line-2 | line-2-0586-0527-s013047 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0631-s010028 | station | forward | revenue | 1 |
| line-2 | line-2-0671-0631-s010028 | station | reverse | revenue | 1 |
| line-2 | line-2-0755-0734-s007026 | station | forward | revenue | 1 |
| line-2 | line-2-0755-0734-s007026 | station | reverse | revenue | 1 |
| line-2 | line-2-0980-0964-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0424-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0473-0633-s003001 | station | forward | revenue | 1 |
| line-3 | line-3-0473-0633-s003001 | station | reverse | revenue | 1 |
| line-3 | line-3-0499-0564-s004620 | station | forward | revenue | 1 |
| line-3 | line-3-0499-0564-s004620 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0436-s007641 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0436-s007641 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0193-s013463 | station | reverse | revenue | 2 |
| line-1 | line-1-0308-0707-s000000 | depot | — | revenue | 39 |
| line-1 | line-1-0308-0707-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0308-0707-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0209-s022153 | depot | — | revenue | 48 |
| line-2 | line-2-0332-0209-s022153 | depot | — | spare | 6 |
| line-2 | line-2-0332-0209-s022153 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0424-0761-s000000 | depot | — | revenue | 28 |
| line-3 | line-3-0424-0761-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0424-0761-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sialkot-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **163 trainsets at 16 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **131 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0308-0707-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0434-0653-s003014 | forward | revenue | 6 | pending |
| line-1 | line-1-0434-0653-s003014 | reverse | revenue | 6 | pending |
| line-1 | line-1-0515-0618-s004959 | forward | revenue | 6 | pending |
| line-1 | line-1-0515-0618-s004959 | reverse | revenue | 6 | pending |
| line-1 | line-1-0642-0564-s007970 | forward | revenue | 6 | pending |
| line-1 | line-1-0642-0564-s007970 | reverse | revenue | 6 | pending |
| line-1 | line-1-1041-0391-s017456 | reverse | revenue | 6 | pending |
| line-1 | line-1-0434-0653-s003014 | forward | spare | 1 | pending |
| line-1 | line-1-0434-0653-s003014 | reverse | spare | 1 | pending |
| line-1 | line-1-0515-0618-s004959 | forward | spare | 1 | pending |
| line-1 | line-1-0515-0618-s004959 | reverse | spare | 1 | pending |
| line-1 | line-1-0642-0564-s007970 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0755-0734-s007026 | forward | revenue | 6 | pending |
| line-2 | line-2-0755-0734-s007026 | reverse | revenue | 6 | pending |
| line-2 | line-2-0671-0631-s010028 | forward | revenue | 6 | pending |
| line-2 | line-2-0671-0631-s010028 | reverse | revenue | 6 | pending |
| line-2 | line-2-0586-0527-s013047 | forward | revenue | 6 | pending |
| line-2 | line-2-0586-0527-s013047 | reverse | revenue | 6 | pending |
| line-2 | line-2-0502-0423-s016057 | forward | revenue | 6 | pending |
| line-2 | line-2-0502-0423-s016057 | reverse | revenue | 6 | pending |
| line-2 | line-2-0332-0209-s022153 | reverse | revenue | 6 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0755-0734-s007026 | forward | spare | 1 | pending |
| line-2 | line-2-0755-0734-s007026 | reverse | spare | 1 | pending |
| line-2 | line-2-0671-0631-s010028 | forward | spare | 1 | pending |
| line-2 | line-2-0671-0631-s010028 | reverse | spare | 1 | pending |
| line-2 | line-2-0586-0527-s013047 | forward | spare | 1 | pending |
| line-2 | line-2-0586-0527-s013047 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0473-0633-s003001 | forward | revenue | 5 | pending |
| line-3 | line-3-0473-0633-s003001 | reverse | revenue | 5 | pending |
| line-3 | line-3-0499-0564-s004620 | forward | revenue | 5 | pending |
| line-3 | line-3-0499-0564-s004620 | reverse | revenue | 5 | pending |
| line-3 | line-3-0549-0436-s007641 | forward | revenue | 5 | pending |
| line-3 | line-3-0549-0436-s007641 | reverse | revenue | 4 | pending |
| line-3 | line-3-0658-0193-s013463 | reverse | revenue | 4 | pending |
| line-3 | line-3-0549-0436-s007641 | reverse | spare | 1 | pending |
| line-3 | line-3-0658-0193-s013463 | reverse | spare | 1 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0473-0633-s003001 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**131 trainsets exceed the reference platform envelope**, requiring **7,794.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0308-0707-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0434-0653-s003014 | 14 | 2 | 12 | 714.0 |
| line-1-0515-0618-s004959 | 14 | 2 | 12 | 714.0 |
| line-1-0642-0564-s007970 | 13 | 2 | 11 | 654.5 |
| line-1-1041-0391-s017456 | 6 | 2 | 4 | 238.0 |
| line-2-0332-0209-s022153 | 6 | 2 | 4 | 238.0 |
| line-2-0502-0423-s016057 | 12 | 2 | 10 | 595.0 |
| line-2-0586-0527-s013047 | 14 | 2 | 12 | 714.0 |
| line-2-0671-0631-s010028 | 14 | 2 | 12 | 714.0 |
| line-2-0755-0734-s007026 | 14 | 2 | 12 | 714.0 |
| line-2-0980-0964-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0424-0761-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0473-0633-s003001 | 11 | 2 | 9 | 535.5 |
| line-3-0499-0564-s004620 | 10 | 2 | 8 | 476.0 |
| line-3-0549-0436-s007641 | 10 | 2 | 8 | 476.0 |
| line-3-0658-0193-s013463 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sialkot/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
