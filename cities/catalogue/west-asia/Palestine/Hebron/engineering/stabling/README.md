# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 123 at depots = 155 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1049-0499-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0695-0203-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 6 |
| line-3-0198-0119-s019333 | line-3 | declared-depot | 50 | 2,975.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0252-0503-s016939 | station | reverse | revenue | 2 |
| line-1 | line-1-0410-0507-s013746 | station | forward | revenue | 1 |
| line-1 | line-1-0410-0507-s013746 | station | reverse | revenue | 1 |
| line-1 | line-1-0501-0509-s011909 | station | forward | revenue | 1 |
| line-1 | line-1-0501-0509-s011909 | station | reverse | revenue | 1 |
| line-1 | line-1-0679-0513-s008304 | station | forward | revenue | 1 |
| line-1 | line-1-0679-0513-s008304 | station | reverse | revenue | 1 |
| line-1 | line-1-0759-0515-s006688 | station | forward | revenue | 1 |
| line-1 | line-1-0759-0515-s006688 | station | reverse | revenue | 1 |
| line-1 | line-1-1049-0499-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0348-0748-s014354 | station | reverse | revenue | 2 |
| line-2 | line-2-0457-0577-s009843 | station | forward | revenue | 1 |
| line-2 | line-2-0457-0577-s009843 | station | reverse | revenue | 1 |
| line-2 | line-2-0501-0509-s008048 | station | forward | revenue | 1 |
| line-2 | line-2-0501-0509-s008048 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0423-s005779 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0423-s005779 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0203-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0198-0119-s019333 | station | reverse | revenue | 2 |
| line-3 | line-3-0410-0507-s009261 | station | forward | revenue | 1 |
| line-3 | line-3-0410-0507-s009261 | station | reverse | revenue | 1 |
| line-3 | line-3-0457-0577-s007378 | station | forward | revenue | 1 |
| line-3 | line-3-0457-0577-s007378 | station | reverse | revenue | 1 |
| line-3 | line-3-0538-0700-s004059 | station | forward | revenue | 1 |
| line-3 | line-3-0538-0700-s004059 | station | reverse | revenue | 1 |
| line-3 | line-3-0638-0851-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1049-0499-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-1049-0499-s000000 | depot | — | spare | 4 |
| line-1 | line-1-1049-0499-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0203-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0695-0203-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0695-0203-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0198-0119-s019333 | depot | — | revenue | 44 |
| line-3 | line-3-0198-0119-s019333 | depot | — | spare | 5 |
| line-3 | line-3-0198-0119-s019333 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hebron-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **155 trainsets at 16 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **140 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **123 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1049-0499-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0759-0515-s006688 | forward | revenue | 5 | pending |
| line-1 | line-1-0759-0515-s006688 | reverse | revenue | 5 | pending |
| line-1 | line-1-0679-0513-s008304 | forward | revenue | 5 | pending |
| line-1 | line-1-0679-0513-s008304 | reverse | revenue | 5 | pending |
| line-1 | line-1-0501-0509-s011909 | forward | revenue | 5 | pending |
| line-1 | line-1-0501-0509-s011909 | reverse | revenue | 5 | pending |
| line-1 | line-1-0410-0507-s013746 | forward | revenue | 4 | pending |
| line-1 | line-1-0410-0507-s013746 | reverse | revenue | 4 | pending |
| line-1 | line-1-0252-0503-s016939 | reverse | revenue | 4 | pending |
| line-1 | line-1-0410-0507-s013746 | forward | spare | 1 | pending |
| line-1 | line-1-0410-0507-s013746 | reverse | spare | 1 | pending |
| line-1 | line-1-0252-0503-s016939 | reverse | spare | 1 | pending |
| line-1 | line-1-1049-0499-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0759-0515-s006688 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0203-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0556-0423-s005779 | forward | revenue | 5 | pending |
| line-2 | line-2-0556-0423-s005779 | reverse | revenue | 5 | pending |
| line-2 | line-2-0501-0509-s008048 | forward | revenue | 5 | pending |
| line-2 | line-2-0501-0509-s008048 | reverse | revenue | 5 | pending |
| line-2 | line-2-0457-0577-s009843 | forward | revenue | 5 | pending |
| line-2 | line-2-0457-0577-s009843 | reverse | revenue | 5 | pending |
| line-2 | line-2-0348-0748-s014354 | reverse | revenue | 4 | pending |
| line-2 | line-2-0348-0748-s014354 | reverse | spare | 1 | pending |
| line-2 | line-2-0695-0203-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0423-s005779 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0423-s005779 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0638-0851-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0538-0700-s004059 | forward | revenue | 7 | pending |
| line-3 | line-3-0538-0700-s004059 | reverse | revenue | 7 | pending |
| line-3 | line-3-0457-0577-s007378 | forward | revenue | 7 | pending |
| line-3 | line-3-0457-0577-s007378 | reverse | revenue | 7 | pending |
| line-3 | line-3-0410-0507-s009261 | forward | revenue | 7 | pending |
| line-3 | line-3-0410-0507-s009261 | reverse | revenue | 6 | pending |
| line-3 | line-3-0198-0119-s019333 | reverse | revenue | 6 | pending |
| line-3 | line-3-0410-0507-s009261 | reverse | spare | 1 | pending |
| line-3 | line-3-0198-0119-s019333 | reverse | spare | 1 | pending |
| line-3 | line-3-0638-0851-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0538-0700-s004059 | forward | spare | 1 | pending |
| line-3 | line-3-0538-0700-s004059 | reverse | spare | 1 | pending |
| line-3 | line-3-0457-0577-s007378 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**111 trainsets exceed the reference platform envelope**, requiring **6,604.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0252-0503-s016939 | 5 | 2 | 3 | 178.5 |
| line-1-0410-0507-s013746 | 10 | 4 | 6 | 357.0 |
| line-1-0501-0509-s011909 | 10 | 4 | 6 | 357.0 |
| line-1-0679-0513-s008304 | 10 | 2 | 8 | 476.0 |
| line-1-0759-0515-s006688 | 11 | 2 | 9 | 535.5 |
| line-1-1049-0499-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0348-0748-s014354 | 5 | 2 | 3 | 178.5 |
| line-2-0457-0577-s009843 | 10 | 4 | 6 | 357.0 |
| line-2-0501-0509-s008048 | 10 | 4 | 6 | 357.0 |
| line-2-0556-0423-s005779 | 12 | 2 | 10 | 595.0 |
| line-2-0695-0203-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0198-0119-s019333 | 7 | 2 | 5 | 297.5 |
| line-3-0410-0507-s009261 | 14 | 4 | 10 | 595.0 |
| line-3-0457-0577-s007378 | 15 | 4 | 11 | 654.5 |
| line-3-0538-0700-s004059 | 16 | 2 | 14 | 833.0 |
| line-3-0638-0851-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Hebron/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
