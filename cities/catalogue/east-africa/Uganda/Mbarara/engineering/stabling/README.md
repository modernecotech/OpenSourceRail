# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 118 at depots = 150 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0522-0784-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0262-0243-s000000 | line-2 | declared-depot | 32 | 1,904.0 | 6 |
| line-3-0129-0892-s024020 | line-3 | declared-depot | 62 | 3,689.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0522-0784-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0574-0656-s003026 | station | forward | revenue | 1 |
| line-1 | line-1-0574-0656-s003026 | station | reverse | revenue | 1 |
| line-1 | line-1-0614-0556-s005404 | station | forward | revenue | 1 |
| line-1 | line-1-0614-0556-s005404 | station | reverse | revenue | 1 |
| line-1 | line-1-0655-0455-s007799 | station | forward | revenue | 1 |
| line-1 | line-1-0655-0455-s007799 | station | reverse | revenue | 1 |
| line-1 | line-1-0696-0354-s010182 | station | reverse | revenue | 2 |
| line-2 | line-2-0262-0243-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0360-0365-s003510 | station | forward | revenue | 1 |
| line-2 | line-2-0360-0365-s003510 | station | reverse | revenue | 1 |
| line-2 | line-2-0458-0487-s007007 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0487-s007007 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0592-s010026 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0592-s010026 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0697-s013033 | station | reverse | revenue | 2 |
| line-3 | line-3-0129-0892-s024020 | station | reverse | revenue | 2 |
| line-3 | line-3-0456-0667-s014629 | station | forward | revenue | 1 |
| line-3 | line-3-0456-0667-s014629 | station | reverse | revenue | 1 |
| line-3 | line-3-0563-0569-s011337 | station | forward | revenue | 1 |
| line-3 | line-3-0563-0569-s011337 | station | reverse | revenue | 1 |
| line-3 | line-3-0606-0530-s010013 | station | forward | revenue | 1 |
| line-3 | line-3-0606-0530-s010013 | station | reverse | revenue | 1 |
| line-3 | line-3-0705-0439-s007010 | station | forward | revenue | 1 |
| line-3 | line-3-0705-0439-s007010 | station | reverse | revenue | 1 |
| line-3 | line-3-0954-0263-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0522-0784-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0522-0784-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0522-0784-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0262-0243-s000000 | depot | — | revenue | 28 |
| line-2 | line-2-0262-0243-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0262-0243-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0129-0892-s024020 | depot | — | revenue | 55 |
| line-3 | line-3-0129-0892-s024020 | depot | — | spare | 6 |
| line-3 | line-3-0129-0892-s024020 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbarara-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **150 trainsets at 16 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **135 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **118 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0522-0784-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0574-0656-s003026 | forward | revenue | 4 | pending |
| line-1 | line-1-0574-0656-s003026 | reverse | revenue | 4 | pending |
| line-1 | line-1-0614-0556-s005404 | forward | revenue | 4 | pending |
| line-1 | line-1-0614-0556-s005404 | reverse | revenue | 4 | pending |
| line-1 | line-1-0655-0455-s007799 | forward | revenue | 4 | pending |
| line-1 | line-1-0655-0455-s007799 | reverse | revenue | 3 | pending |
| line-1 | line-1-0696-0354-s010182 | reverse | revenue | 3 | pending |
| line-1 | line-1-0655-0455-s007799 | reverse | spare | 1 | pending |
| line-1 | line-1-0696-0354-s010182 | reverse | spare | 1 | pending |
| line-1 | line-1-0522-0784-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0574-0656-s003026 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0360-0365-s003510 | forward | revenue | 5 | pending |
| line-2 | line-2-0360-0365-s003510 | reverse | revenue | 5 | pending |
| line-2 | line-2-0458-0487-s007007 | forward | revenue | 5 | pending |
| line-2 | line-2-0458-0487-s007007 | reverse | revenue | 5 | pending |
| line-2 | line-2-0542-0592-s010026 | forward | revenue | 5 | pending |
| line-2 | line-2-0542-0592-s010026 | reverse | revenue | 4 | pending |
| line-2 | line-2-0626-0697-s013033 | reverse | revenue | 4 | pending |
| line-2 | line-2-0542-0592-s010026 | reverse | spare | 1 | pending |
| line-2 | line-2-0626-0697-s013033 | reverse | spare | 1 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0360-0365-s003510 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0705-0439-s007010 | forward | revenue | 7 | pending |
| line-3 | line-3-0705-0439-s007010 | reverse | revenue | 7 | pending |
| line-3 | line-3-0606-0530-s010013 | forward | revenue | 7 | pending |
| line-3 | line-3-0606-0530-s010013 | reverse | revenue | 7 | pending |
| line-3 | line-3-0563-0569-s011337 | forward | revenue | 7 | pending |
| line-3 | line-3-0563-0569-s011337 | reverse | revenue | 7 | pending |
| line-3 | line-3-0456-0667-s014629 | forward | revenue | 6 | pending |
| line-3 | line-3-0456-0667-s014629 | reverse | revenue | 6 | pending |
| line-3 | line-3-0129-0892-s024020 | reverse | revenue | 6 | pending |
| line-3 | line-3-0456-0667-s014629 | forward | spare | 1 | pending |
| line-3 | line-3-0456-0667-s014629 | reverse | spare | 1 | pending |
| line-3 | line-3-0129-0892-s024020 | reverse | spare | 1 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0705-0439-s007010 | forward | spare | 1 | pending |
| line-3 | line-3-0705-0439-s007010 | reverse | spare | 1 | pending |
| line-3 | line-3-0606-0530-s010013 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**110 trainsets exceed the reference platform envelope**, requiring **6,545.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0522-0784-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0574-0656-s003026 | 9 | 2 | 7 | 416.5 |
| line-1-0614-0556-s005404 | 8 | 4 | 4 | 238.0 |
| line-1-0655-0455-s007799 | 8 | 2 | 6 | 357.0 |
| line-1-0696-0354-s010182 | 4 | 2 | 2 | 119.0 |
| line-2-0262-0243-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0360-0365-s003510 | 11 | 2 | 9 | 535.5 |
| line-2-0458-0487-s007007 | 10 | 2 | 8 | 476.0 |
| line-2-0542-0592-s010026 | 10 | 4 | 6 | 357.0 |
| line-2-0626-0697-s013033 | 5 | 2 | 3 | 178.5 |
| line-3-0129-0892-s024020 | 7 | 2 | 5 | 297.5 |
| line-3-0456-0667-s014629 | 14 | 2 | 12 | 714.0 |
| line-3-0563-0569-s011337 | 14 | 4 | 10 | 595.0 |
| line-3-0606-0530-s010013 | 15 | 4 | 11 | 654.5 |
| line-3-0705-0439-s007010 | 16 | 2 | 14 | 833.0 |
| line-3-0954-0263-s000000 | 8 | 2 | 6 | 357.0 |

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
