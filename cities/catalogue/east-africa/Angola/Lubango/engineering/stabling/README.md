# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 112 at depots = 138 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0445-0353-s000000 | line-1 | declared-depot | 34 | 2,023.0 | 6 |
| line-2-0145-0992-s020058 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0533-0317-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0445-0353-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0484-0487-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0487-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0645-s006585 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0645-s006585 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0895-s013415 | station | reverse | revenue | 2 |
| line-2 | line-2-0145-0992-s020058 | station | reverse | revenue | 2 |
| line-2 | line-2-0531-0645-s008661 | station | forward | revenue | 1 |
| line-2 | line-2-0531-0645-s008661 | station | reverse | revenue | 1 |
| line-2 | line-2-0629-0556-s005712 | station | forward | revenue | 1 |
| line-2 | line-2-0629-0556-s005712 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0482-s003233 | station | forward | revenue | 1 |
| line-2 | line-2-0710-0482-s003233 | station | reverse | revenue | 1 |
| line-2 | line-2-0818-0385-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0533-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0584-0444-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0584-0444-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0629-0556-s005669 | station | forward | revenue | 1 |
| line-3 | line-3-0629-0556-s005669 | station | reverse | revenue | 1 |
| line-3 | line-3-0725-0794-s011318 | station | reverse | revenue | 2 |
| line-1 | line-1-0445-0353-s000000 | depot | — | revenue | 30 |
| line-1 | line-1-0445-0353-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0445-0353-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0145-0992-s020058 | depot | — | revenue | 45 |
| line-2 | line-2-0145-0992-s020058 | depot | — | spare | 5 |
| line-2 | line-2-0145-0992-s020058 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0533-0317-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0533-0317-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0533-0317-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lubango-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **138 trainsets at 13 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **124 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **112 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0445-0353-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0484-0487-s003015 | forward | revenue | 7 | pending |
| line-1 | line-1-0484-0487-s003015 | reverse | revenue | 6 | pending |
| line-1 | line-1-0531-0645-s006585 | forward | revenue | 6 | pending |
| line-1 | line-1-0531-0645-s006585 | reverse | revenue | 6 | pending |
| line-1 | line-1-0647-0895-s013415 | reverse | revenue | 6 | pending |
| line-1 | line-1-0484-0487-s003015 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0645-s006585 | forward | spare | 1 | pending |
| line-1 | line-1-0531-0645-s006585 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0895-s013415 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0710-0482-s003233 | forward | revenue | 7 | pending |
| line-2 | line-2-0710-0482-s003233 | reverse | revenue | 7 | pending |
| line-2 | line-2-0629-0556-s005712 | forward | revenue | 7 | pending |
| line-2 | line-2-0629-0556-s005712 | reverse | revenue | 7 | pending |
| line-2 | line-2-0531-0645-s008661 | forward | revenue | 7 | pending |
| line-2 | line-2-0531-0645-s008661 | reverse | revenue | 7 | pending |
| line-2 | line-2-0145-0992-s020058 | reverse | revenue | 6 | pending |
| line-2 | line-2-0145-0992-s020058 | reverse | spare | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0710-0482-s003233 | forward | spare | 1 | pending |
| line-2 | line-2-0710-0482-s003233 | reverse | spare | 1 | pending |
| line-2 | line-2-0629-0556-s005712 | forward | spare | 1 | pending |
| line-2 | line-2-0629-0556-s005712 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0584-0444-s003009 | forward | revenue | 5 | pending |
| line-3 | line-3-0584-0444-s003009 | reverse | revenue | 5 | pending |
| line-3 | line-3-0629-0556-s005669 | forward | revenue | 5 | pending |
| line-3 | line-3-0629-0556-s005669 | reverse | revenue | 5 | pending |
| line-3 | line-3-0725-0794-s011318 | reverse | revenue | 5 | pending |
| line-3 | line-3-0584-0444-s003009 | forward | spare | 1 | pending |
| line-3 | line-3-0584-0444-s003009 | reverse | spare | 1 | pending |
| line-3 | line-3-0629-0556-s005669 | forward | spare | 1 | pending |
| line-3 | line-3-0629-0556-s005669 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**104 trainsets exceed the reference platform envelope**, requiring **6,188.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0445-0353-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0484-0487-s003015 | 14 | 2 | 12 | 714.0 |
| line-1-0531-0645-s006585 | 14 | 4 | 10 | 595.0 |
| line-1-0647-0895-s013415 | 7 | 2 | 5 | 297.5 |
| line-2-0145-0992-s020058 | 7 | 2 | 5 | 297.5 |
| line-2-0531-0645-s008661 | 14 | 4 | 10 | 595.0 |
| line-2-0629-0556-s005712 | 16 | 4 | 12 | 714.0 |
| line-2-0710-0482-s003233 | 16 | 2 | 14 | 833.0 |
| line-2-0818-0385-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0533-0317-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0584-0444-s003009 | 12 | 2 | 10 | 595.0 |
| line-3-0629-0556-s005669 | 12 | 4 | 8 | 476.0 |
| line-3-0725-0794-s011318 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lubango/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
