# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 53 at depots = 97 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0582-0682-s008071 | line-1 | declared-depot | 15 | 892.5 | 4 |
| line-2-0612-0583-s000000 | line-2 | declared-depot | 12 | 714.0 | 4 |
| line-3-0535-0485-s000000 | line-3 | declared-depot | 10 | 595.0 | 3 |
| line-4-0559-0615-s000000 | line-4 | declared-depot | 10 | 595.0 | 3 |
| line-5-0560-0616-s000000 | line-5 | declared-depot | 6 | 357.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0464-0332-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0501-0442-s002542 | station | forward | revenue | 1 |
| line-1 | line-1-0501-0442-s002542 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0446-s002650 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0446-s002650 | station | reverse | revenue | 1 |
| line-1 | line-1-0522-0505-s003987 | station | forward | revenue | 1 |
| line-1 | line-1-0522-0505-s003987 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0615-s006529 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0615-s006529 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0682-s008071 | station | reverse | revenue | 2 |
| line-2 | line-2-0471-0405-s005091 | station | reverse | revenue | 2 |
| line-2 | line-2-0501-0442-s004009 | station | forward | revenue | 1 |
| line-2 | line-2-0501-0442-s004009 | station | reverse | revenue | 1 |
| line-2 | line-2-0503-0446-s003912 | station | forward | revenue | 1 |
| line-2 | line-2-0503-0446-s003912 | station | reverse | revenue | 1 |
| line-2 | line-2-0535-0485-s002785 | station | forward | revenue | 1 |
| line-2 | line-2-0535-0485-s002785 | station | reverse | revenue | 1 |
| line-2 | line-2-0572-0533-s001437 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0533-s001437 | station | reverse | revenue | 1 |
| line-2 | line-2-0612-0583-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0535-0485-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0588-0439-s001441 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0439-s001441 | station | reverse | revenue | 1 |
| line-3 | line-3-0663-0439-s002941 | station | forward | revenue | 1 |
| line-3 | line-3-0663-0439-s002941 | station | reverse | revenue | 1 |
| line-3 | line-3-0688-0514-s004648 | station | reverse | revenue | 2 |
| line-4 | line-4-0489-0637-s001582 | station | forward | revenue | 1 |
| line-4 | line-4-0489-0637-s001582 | station | reverse | revenue | 1 |
| line-4 | line-4-0489-0712-s003082 | station | forward | revenue | 1 |
| line-4 | line-4-0489-0712-s003082 | station | reverse | revenue | 1 |
| line-4 | line-4-0559-0615-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0563-0788-s005215 | station | reverse | revenue | 2 |
| line-5 | line-5-0560-0616-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0662-0662-s002454 | station | reverse | revenue | 2 |
| line-1 | line-1-0582-0682-s008071 | depot | — | revenue | 12 |
| line-1 | line-1-0582-0682-s008071 | depot | — | spare | 2 |
| line-1 | line-1-0582-0682-s008071 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0612-0583-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0612-0583-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0612-0583-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0535-0485-s000000 | depot | — | revenue | 8 |
| line-3 | line-3-0535-0485-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0535-0485-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0559-0615-s000000 | depot | — | revenue | 8 |
| line-4 | line-4-0559-0615-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0559-0615-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0560-0616-s000000 | depot | — | revenue | 4 |
| line-5 | line-5-0560-0616-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0560-0616-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/malanje-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **97 trainsets at 22 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **85 revenue, 7 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **53 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0464-0332-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0501-0442-s002542 | forward | revenue | 3 | pending |
| line-1 | line-1-0501-0442-s002542 | reverse | revenue | 3 | pending |
| line-1 | line-1-0503-0446-s002650 | forward | revenue | 3 | pending |
| line-1 | line-1-0503-0446-s002650 | reverse | revenue | 2 | pending |
| line-1 | line-1-0522-0505-s003987 | forward | revenue | 2 | pending |
| line-1 | line-1-0522-0505-s003987 | reverse | revenue | 2 | pending |
| line-1 | line-1-0559-0615-s006529 | forward | revenue | 2 | pending |
| line-1 | line-1-0559-0615-s006529 | reverse | revenue | 2 | pending |
| line-1 | line-1-0582-0682-s008071 | reverse | revenue | 2 | pending |
| line-1 | line-1-0503-0446-s002650 | reverse | spare | 1 | pending |
| line-1 | line-1-0522-0505-s003987 | forward | spare | 1 | pending |
| line-1 | line-1-0522-0505-s003987 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0612-0583-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0572-0533-s001437 | forward | revenue | 2 | pending |
| line-2 | line-2-0572-0533-s001437 | reverse | revenue | 2 | pending |
| line-2 | line-2-0535-0485-s002785 | forward | revenue | 2 | pending |
| line-2 | line-2-0535-0485-s002785 | reverse | revenue | 2 | pending |
| line-2 | line-2-0503-0446-s003912 | forward | revenue | 2 | pending |
| line-2 | line-2-0503-0446-s003912 | reverse | revenue | 2 | pending |
| line-2 | line-2-0501-0442-s004009 | forward | revenue | 2 | pending |
| line-2 | line-2-0501-0442-s004009 | reverse | revenue | 2 | pending |
| line-2 | line-2-0471-0405-s005091 | reverse | revenue | 2 | pending |
| line-2 | line-2-0572-0533-s001437 | forward | spare | 1 | pending |
| line-2 | line-2-0572-0533-s001437 | reverse | spare | 1 | pending |
| line-2 | line-2-0535-0485-s002785 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0535-0485-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0588-0439-s001441 | forward | revenue | 3 | pending |
| line-3 | line-3-0588-0439-s001441 | reverse | revenue | 3 | pending |
| line-3 | line-3-0663-0439-s002941 | forward | revenue | 3 | pending |
| line-3 | line-3-0663-0439-s002941 | reverse | revenue | 2 | pending |
| line-3 | line-3-0688-0514-s004648 | reverse | revenue | 2 | pending |
| line-3 | line-3-0663-0439-s002941 | reverse | spare | 1 | pending |
| line-3 | line-3-0688-0514-s004648 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0559-0615-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0489-0637-s001582 | forward | revenue | 3 | pending |
| line-4 | line-4-0489-0637-s001582 | reverse | revenue | 3 | pending |
| line-4 | line-4-0489-0712-s003082 | forward | revenue | 3 | pending |
| line-4 | line-4-0489-0712-s003082 | reverse | revenue | 2 | pending |
| line-4 | line-4-0563-0788-s005215 | reverse | revenue | 2 | pending |
| line-4 | line-4-0489-0712-s003082 | reverse | spare | 1 | pending |
| line-4 | line-4-0563-0788-s005215 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0560-0616-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0662-0662-s002454 | reverse | revenue | 4 | pending |
| line-5 | line-5-0560-0616-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0662-0662-s002454 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **2,320.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0464-0332-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0501-0442-s002542 | 6 | 4 | 2 | 119.0 |
| line-1-0503-0446-s002650 | 6 | 4 | 2 | 119.0 |
| line-1-0522-0505-s003987 | 6 | 4 | 2 | 119.0 |
| line-1-0559-0615-s006529 | 4 | 4 | 0 | 0.0 |
| line-1-0582-0682-s008071 | 2 | 2 | 0 | 0.0 |
| line-2-0471-0405-s005091 | 2 | 2 | 0 | 0.0 |
| line-2-0501-0442-s004009 | 4 | 4 | 0 | 0.0 |
| line-2-0503-0446-s003912 | 4 | 4 | 0 | 0.0 |
| line-2-0535-0485-s002785 | 5 | 4 | 1 | 59.5 |
| line-2-0572-0533-s001437 | 6 | 2 | 4 | 238.0 |
| line-2-0612-0583-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0535-0485-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0588-0439-s001441 | 6 | 2 | 4 | 238.0 |
| line-3-0663-0439-s002941 | 6 | 2 | 4 | 238.0 |
| line-3-0688-0514-s004648 | 3 | 2 | 1 | 59.5 |
| line-4-0489-0637-s001582 | 6 | 2 | 4 | 238.0 |
| line-4-0489-0712-s003082 | 6 | 2 | 4 | 238.0 |
| line-4-0559-0615-s000000 | 3 | 2 | 1 | 59.5 |
| line-4-0563-0788-s005215 | 3 | 2 | 1 | 59.5 |
| line-5-0560-0616-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0662-0662-s002454 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Malanje/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
