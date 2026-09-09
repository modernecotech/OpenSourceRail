# Station and depot overnight allocation

Plan: **36 trainsets at stations + 74 at depots = 110 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0244-0147-s019613 | 74 | 4,403.0 | 17 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0244-0147-s019613 | station | reverse | revenue | 2 |
| line-1 | line-1-0433-0325-s013925 | station | forward | revenue | 1 |
| line-1 | line-1-0433-0325-s013925 | station | reverse | revenue | 1 |
| line-1 | line-1-0434-0492-s009012 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0492-s009012 | station | reverse | revenue | 1 |
| line-1 | line-1-0480-0391-s012029 | station | forward | revenue | 1 |
| line-1 | line-1-0480-0391-s012029 | station | reverse | revenue | 1 |
| line-1 | line-1-0514-0823-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0531-0681-s003004 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0681-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0542-0545-s006122 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0545-s006122 | station | reverse | revenue | 1 |
| line-2 | line-2-0250-0492-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0375-0555-s003372 | station | forward | revenue | 1 |
| line-2 | line-2-0375-0555-s003372 | station | reverse | revenue | 1 |
| line-2 | line-2-0481-0485-s006392 | station | forward | revenue | 1 |
| line-2 | line-2-0481-0485-s006392 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0545-s009491 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0545-s009491 | station | reverse | revenue | 1 |
| line-2 | line-2-0630-0515-s012030 | station | forward | revenue | 1 |
| line-2 | line-2-0630-0515-s012030 | station | reverse | revenue | 1 |
| line-2 | line-2-0702-0472-s014571 | station | reverse | revenue | 2 |
| line-3 | line-3-0223-0982-s017121 | station | reverse | revenue | 2 |
| line-3 | line-3-0458-0677-s009039 | station | forward | revenue | 1 |
| line-3 | line-3-0458-0677-s009039 | station | reverse | revenue | 1 |
| line-3 | line-3-0519-0441-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0519-0441-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0542-0545-s005466 | station | forward | revenue | 1 |
| line-3 | line-3-0542-0545-s005466 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0343-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0244-0147-s019613 | depot | — | revenue | 24 |
| line-1 | line-1-0244-0147-s019613 | depot | — | spare | 3 |
| line-1 | line-1-0244-0147-s019613 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0244-0147-s019613 | depot | — | revenue | 16 |
| line-2 | line-1-0244-0147-s019613 | depot | — | spare | 2 |
| line-2 | line-1-0244-0147-s019613 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0244-0147-s019613 | depot | — | revenue | 23 |
| line-3 | line-1-0244-0147-s019613 | depot | — | spare | 3 |
| line-3 | line-1-0244-0147-s019613 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (19 trains), line-3 (27 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **110 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **99 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **74 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0514-0823-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0531-0681-s003004 | forward | revenue | 4 | pending |
| line-1 | line-1-0531-0681-s003004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0542-0545-s006122 | forward | revenue | 3 | pending |
| line-1 | line-1-0542-0545-s006122 | reverse | revenue | 3 | pending |
| line-1 | line-1-0434-0492-s009012 | forward | revenue | 3 | pending |
| line-1 | line-1-0434-0492-s009012 | reverse | revenue | 3 | pending |
| line-1 | line-1-0480-0391-s012029 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0391-s012029 | reverse | revenue | 3 | pending |
| line-1 | line-1-0433-0325-s013925 | forward | revenue | 3 | pending |
| line-1 | line-1-0433-0325-s013925 | reverse | revenue | 3 | pending |
| line-1 | line-1-0244-0147-s019613 | reverse | revenue | 3 | pending |
| line-1 | line-1-0531-0681-s003004 | reverse | spare | 1 | pending |
| line-1 | line-1-0542-0545-s006122 | forward | spare | 1 | pending |
| line-1 | line-1-0542-0545-s006122 | reverse | spare | 1 | pending |
| line-1 | line-1-0434-0492-s009012 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0375-0555-s003372 | forward | revenue | 3 | pending |
| line-2 | line-2-0375-0555-s003372 | reverse | revenue | 3 | pending |
| line-2 | line-2-0481-0485-s006392 | forward | revenue | 3 | pending |
| line-2 | line-2-0481-0485-s006392 | reverse | revenue | 3 | pending |
| line-2 | line-2-0542-0545-s009491 | forward | revenue | 3 | pending |
| line-2 | line-2-0542-0545-s009491 | reverse | revenue | 3 | pending |
| line-2 | line-2-0630-0515-s012030 | forward | revenue | 3 | pending |
| line-2 | line-2-0630-0515-s012030 | reverse | revenue | 2 | pending |
| line-2 | line-2-0702-0472-s014571 | reverse | revenue | 2 | pending |
| line-2 | line-2-0630-0515-s012030 | reverse | spare | 1 | pending |
| line-2 | line-2-0702-0472-s014571 | reverse | spare | 1 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0519-0441-s003002 | forward | revenue | 4 | pending |
| line-3 | line-3-0519-0441-s003002 | reverse | revenue | 4 | pending |
| line-3 | line-3-0542-0545-s005466 | forward | revenue | 4 | pending |
| line-3 | line-3-0542-0545-s005466 | reverse | revenue | 4 | pending |
| line-3 | line-3-0458-0677-s009039 | forward | revenue | 4 | pending |
| line-3 | line-3-0458-0677-s009039 | reverse | revenue | 4 | pending |
| line-3 | line-3-0223-0982-s017121 | reverse | revenue | 4 | pending |
| line-3 | line-3-0519-0441-s003002 | forward | spare | 1 | pending |
| line-3 | line-3-0519-0441-s003002 | reverse | spare | 1 | pending |
| line-3 | line-3-0542-0545-s005466 | forward | spare | 1 | pending |
| line-3 | line-3-0542-0545-s005466 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**68 trainsets exceed the reference platform envelope**, requiring **4,046.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0244-0147-s019613 | 3 | 2 | 1 | 59.5 |
| line-1-0433-0325-s013925 | 6 | 2 | 4 | 238.0 |
| line-1-0434-0492-s009012 | 7 | 2 | 5 | 297.5 |
| line-1-0480-0391-s012029 | 6 | 2 | 4 | 238.0 |
| line-1-0514-0823-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0531-0681-s003004 | 8 | 2 | 6 | 357.0 |
| line-1-0542-0545-s006122 | 8 | 4 | 4 | 238.0 |
| line-2-0250-0492-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0375-0555-s003372 | 6 | 2 | 4 | 238.0 |
| line-2-0481-0485-s006392 | 6 | 2 | 4 | 238.0 |
| line-2-0542-0545-s009491 | 6 | 4 | 2 | 119.0 |
| line-2-0630-0515-s012030 | 6 | 2 | 4 | 238.0 |
| line-2-0702-0472-s014571 | 3 | 2 | 1 | 59.5 |
| line-3-0223-0982-s017121 | 4 | 2 | 2 | 119.0 |
| line-3-0458-0677-s009039 | 8 | 2 | 6 | 357.0 |
| line-3-0519-0441-s003002 | 10 | 2 | 8 | 476.0 |
| line-3-0542-0545-s005466 | 10 | 4 | 6 | 357.0 |
| line-3-0554-0343-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Polokwane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
