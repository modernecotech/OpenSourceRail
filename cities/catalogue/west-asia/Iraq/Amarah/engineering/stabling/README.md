# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 98 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1131-0749-s020458 | line-1 | declared-depot | 52 | 3,094.0 | 9 |
| line-2-0709-0317-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0667-0658-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0313-0285-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0431-0353-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0353-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0421-s006006 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0421-s006006 | station | reverse | revenue | 1 |
| line-1 | line-1-0664-0488-s009006 | station | forward | revenue | 1 |
| line-1 | line-1-0664-0488-s009006 | station | reverse | revenue | 1 |
| line-1 | line-1-0782-0556-s012023 | station | forward | revenue | 1 |
| line-1 | line-1-0782-0556-s012023 | station | reverse | revenue | 1 |
| line-1 | line-1-1131-0749-s020458 | station | reverse | revenue | 2 |
| line-2 | line-2-0329-0543-s009847 | station | reverse | revenue | 2 |
| line-2 | line-2-0404-0499-s007924 | station | forward | revenue | 1 |
| line-2 | line-2-0404-0499-s007924 | station | reverse | revenue | 1 |
| line-2 | line-2-0477-0455-s006018 | station | forward | revenue | 1 |
| line-2 | line-2-0477-0455-s006018 | station | reverse | revenue | 1 |
| line-2 | line-2-0592-0386-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0592-0386-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0709-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0539-0186-s010547 | station | reverse | revenue | 2 |
| line-3 | line-3-0565-0300-s008040 | station | forward | revenue | 1 |
| line-3 | line-3-0565-0300-s008040 | station | reverse | revenue | 1 |
| line-3 | line-3-0597-0412-s005523 | station | forward | revenue | 1 |
| line-3 | line-3-0597-0412-s005523 | station | reverse | revenue | 1 |
| line-3 | line-3-0629-0524-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0629-0524-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0658-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1131-0749-s020458 | depot | — | revenue | 46 |
| line-1 | line-1-1131-0749-s020458 | depot | — | spare | 5 |
| line-1 | line-1-1131-0749-s020458 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0709-0317-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0709-0317-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0709-0317-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0667-0658-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0667-0658-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0667-0658-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/amarah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 16 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0313-0285-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0431-0353-s003005 | forward | revenue | 6 | pending |
| line-1 | line-1-0431-0353-s003005 | reverse | revenue | 6 | pending |
| line-1 | line-1-0547-0421-s006006 | forward | revenue | 6 | pending |
| line-1 | line-1-0547-0421-s006006 | reverse | revenue | 6 | pending |
| line-1 | line-1-0664-0488-s009006 | forward | revenue | 6 | pending |
| line-1 | line-1-0664-0488-s009006 | reverse | revenue | 6 | pending |
| line-1 | line-1-0782-0556-s012023 | forward | revenue | 6 | pending |
| line-1 | line-1-0782-0556-s012023 | reverse | revenue | 5 | pending |
| line-1 | line-1-1131-0749-s020458 | reverse | revenue | 5 | pending |
| line-1 | line-1-0782-0556-s012023 | reverse | spare | 1 | pending |
| line-1 | line-1-1131-0749-s020458 | reverse | spare | 1 | pending |
| line-1 | line-1-0313-0285-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0431-0353-s003005 | forward | spare | 1 | pending |
| line-1 | line-1-0431-0353-s003005 | reverse | spare | 1 | pending |
| line-1 | line-1-0547-0421-s006006 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0709-0317-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0592-0386-s003017 | forward | revenue | 4 | pending |
| line-2 | line-2-0592-0386-s003017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0477-0455-s006018 | forward | revenue | 4 | pending |
| line-2 | line-2-0477-0455-s006018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0404-0499-s007924 | forward | revenue | 3 | pending |
| line-2 | line-2-0404-0499-s007924 | reverse | revenue | 3 | pending |
| line-2 | line-2-0329-0543-s009847 | reverse | revenue | 3 | pending |
| line-2 | line-2-0404-0499-s007924 | forward | spare | 1 | pending |
| line-2 | line-2-0404-0499-s007924 | reverse | spare | 1 | pending |
| line-2 | line-2-0329-0543-s009847 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0629-0524-s003007 | forward | revenue | 4 | pending |
| line-3 | line-3-0629-0524-s003007 | reverse | revenue | 4 | pending |
| line-3 | line-3-0597-0412-s005523 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0412-s005523 | reverse | revenue | 4 | pending |
| line-3 | line-3-0565-0300-s008040 | forward | revenue | 4 | pending |
| line-3 | line-3-0565-0300-s008040 | reverse | revenue | 3 | pending |
| line-3 | line-3-0539-0186-s010547 | reverse | revenue | 3 | pending |
| line-3 | line-3-0565-0300-s008040 | reverse | spare | 1 | pending |
| line-3 | line-3-0539-0186-s010547 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0629-0524-s003007 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**94 trainsets exceed the reference platform envelope**, requiring **5,593.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0313-0285-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0431-0353-s003005 | 14 | 2 | 12 | 714.0 |
| line-1-0547-0421-s006006 | 13 | 2 | 11 | 654.5 |
| line-1-0664-0488-s009006 | 12 | 2 | 10 | 595.0 |
| line-1-0782-0556-s012023 | 12 | 2 | 10 | 595.0 |
| line-1-1131-0749-s020458 | 6 | 2 | 4 | 238.0 |
| line-2-0329-0543-s009847 | 4 | 2 | 2 | 119.0 |
| line-2-0404-0499-s007924 | 8 | 2 | 6 | 357.0 |
| line-2-0477-0455-s006018 | 8 | 2 | 6 | 357.0 |
| line-2-0592-0386-s003017 | 8 | 4 | 4 | 238.0 |
| line-2-0709-0317-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0539-0186-s010547 | 4 | 2 | 2 | 119.0 |
| line-3-0565-0300-s008040 | 8 | 2 | 6 | 357.0 |
| line-3-0597-0412-s005523 | 8 | 4 | 4 | 238.0 |
| line-3-0629-0524-s003007 | 9 | 2 | 7 | 416.5 |
| line-3-0667-0658-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Amarah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
