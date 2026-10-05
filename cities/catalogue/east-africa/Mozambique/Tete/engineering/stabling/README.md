# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 84 at depots = 132 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0851-0539-s019149 | line-1 | declared-depot | 39 | 2,320.5 | 9 |
| line-2-0745-0787-s000000 | line-2 | declared-depot | 21 | 1,249.5 | 6 |
| line-3-0533-0514-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0416-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0448-0559-s005072 | station | forward | revenue | 1 |
| line-1 | line-1-0448-0559-s005072 | station | reverse | revenue | 1 |
| line-1 | line-1-0451-0562-s005156 | station | forward | revenue | 1 |
| line-1 | line-1-0451-0562-s005156 | station | reverse | revenue | 1 |
| line-1 | line-1-0468-0575-s005604 | station | forward | revenue | 1 |
| line-1 | line-1-0468-0575-s005604 | station | reverse | revenue | 1 |
| line-1 | line-1-0471-0577-s005681 | station | forward | revenue | 1 |
| line-1 | line-1-0471-0577-s005681 | station | reverse | revenue | 1 |
| line-1 | line-1-0480-0579-s005877 | station | forward | revenue | 1 |
| line-1 | line-1-0480-0579-s005877 | station | reverse | revenue | 1 |
| line-1 | line-1-0493-0460-s011288 | station | forward | revenue | 1 |
| line-1 | line-1-0493-0460-s011288 | station | reverse | revenue | 1 |
| line-1 | line-1-0524-0525-s008192 | station | forward | revenue | 1 |
| line-1 | line-1-0524-0525-s008192 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0479-s013257 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0479-s013257 | station | reverse | revenue | 1 |
| line-1 | line-1-0672-0499-s015214 | station | forward | revenue | 1 |
| line-1 | line-1-0672-0499-s015214 | station | reverse | revenue | 1 |
| line-1 | line-1-0851-0539-s019149 | station | reverse | revenue | 2 |
| line-2 | line-2-0329-0468-s011748 | station | reverse | revenue | 2 |
| line-2 | line-2-0448-0559-s008391 | station | forward | revenue | 1 |
| line-2 | line-2-0448-0559-s008391 | station | reverse | revenue | 1 |
| line-2 | line-2-0451-0562-s008306 | station | forward | revenue | 1 |
| line-2 | line-2-0451-0562-s008306 | station | reverse | revenue | 1 |
| line-2 | line-2-0468-0575-s007835 | station | forward | revenue | 1 |
| line-2 | line-2-0468-0575-s007835 | station | reverse | revenue | 1 |
| line-2 | line-2-0471-0577-s007759 | station | forward | revenue | 1 |
| line-2 | line-2-0471-0577-s007759 | station | reverse | revenue | 1 |
| line-2 | line-2-0477-0582-s007574 | station | forward | revenue | 1 |
| line-2 | line-2-0477-0582-s007574 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0652-s004990 | station | forward | revenue | 1 |
| line-2 | line-2-0569-0652-s004990 | station | reverse | revenue | 1 |
| line-2 | line-2-0745-0787-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0262-0845-s009650 | station | reverse | revenue | 2 |
| line-3 | line-3-0477-0582-s001988 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0582-s001988 | station | reverse | revenue | 1 |
| line-3 | line-3-0480-0579-s001891 | station | forward | revenue | 1 |
| line-3 | line-3-0480-0579-s001891 | station | reverse | revenue | 1 |
| line-3 | line-3-0524-0525-s000318 | station | forward | revenue | 1 |
| line-3 | line-3-0524-0525-s000318 | station | reverse | revenue | 1 |
| line-3 | line-3-0533-0514-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0851-0539-s019149 | depot | — | revenue | 33 |
| line-1 | line-1-0851-0539-s019149 | depot | — | spare | 5 |
| line-1 | line-1-0851-0539-s019149 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0745-0787-s000000 | depot | — | revenue | 17 |
| line-2 | line-2-0745-0787-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0745-0787-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0533-0514-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0533-0514-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0533-0514-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tete-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **132 trainsets at 24 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **118 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **84 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0297-0416-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0448-0559-s005072 | forward | revenue | 3 | pending |
| line-1 | line-1-0448-0559-s005072 | reverse | revenue | 3 | pending |
| line-1 | line-1-0451-0562-s005156 | forward | revenue | 3 | pending |
| line-1 | line-1-0451-0562-s005156 | reverse | revenue | 3 | pending |
| line-1 | line-1-0468-0575-s005604 | forward | revenue | 3 | pending |
| line-1 | line-1-0468-0575-s005604 | reverse | revenue | 3 | pending |
| line-1 | line-1-0471-0577-s005681 | forward | revenue | 3 | pending |
| line-1 | line-1-0471-0577-s005681 | reverse | revenue | 3 | pending |
| line-1 | line-1-0480-0579-s005877 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0579-s005877 | reverse | revenue | 3 | pending |
| line-1 | line-1-0524-0525-s008192 | forward | revenue | 3 | pending |
| line-1 | line-1-0524-0525-s008192 | reverse | revenue | 3 | pending |
| line-1 | line-1-0493-0460-s011288 | forward | revenue | 3 | pending |
| line-1 | line-1-0493-0460-s011288 | reverse | revenue | 3 | pending |
| line-1 | line-1-0583-0479-s013257 | forward | revenue | 2 | pending |
| line-1 | line-1-0583-0479-s013257 | reverse | revenue | 2 | pending |
| line-1 | line-1-0672-0499-s015214 | forward | revenue | 2 | pending |
| line-1 | line-1-0672-0499-s015214 | reverse | revenue | 2 | pending |
| line-1 | line-1-0851-0539-s019149 | reverse | revenue | 2 | pending |
| line-1 | line-1-0583-0479-s013257 | forward | spare | 1 | pending |
| line-1 | line-1-0583-0479-s013257 | reverse | spare | 1 | pending |
| line-1 | line-1-0672-0499-s015214 | forward | spare | 1 | pending |
| line-1 | line-1-0672-0499-s015214 | reverse | spare | 1 | pending |
| line-1 | line-1-0851-0539-s019149 | reverse | spare | 1 | pending |
| line-1 | line-1-0297-0416-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0745-0787-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0652-s004990 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0652-s004990 | reverse | revenue | 3 | pending |
| line-2 | line-2-0477-0582-s007574 | forward | revenue | 3 | pending |
| line-2 | line-2-0477-0582-s007574 | reverse | revenue | 3 | pending |
| line-2 | line-2-0471-0577-s007759 | forward | revenue | 2 | pending |
| line-2 | line-2-0471-0577-s007759 | reverse | revenue | 2 | pending |
| line-2 | line-2-0468-0575-s007835 | forward | revenue | 2 | pending |
| line-2 | line-2-0468-0575-s007835 | reverse | revenue | 2 | pending |
| line-2 | line-2-0451-0562-s008306 | forward | revenue | 2 | pending |
| line-2 | line-2-0451-0562-s008306 | reverse | revenue | 2 | pending |
| line-2 | line-2-0448-0559-s008391 | forward | revenue | 2 | pending |
| line-2 | line-2-0448-0559-s008391 | reverse | revenue | 2 | pending |
| line-2 | line-2-0329-0468-s011748 | reverse | revenue | 2 | pending |
| line-2 | line-2-0471-0577-s007759 | forward | spare | 1 | pending |
| line-2 | line-2-0471-0577-s007759 | reverse | spare | 1 | pending |
| line-2 | line-2-0468-0575-s007835 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0575-s007835 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0514-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0524-0525-s000318 | forward | revenue | 4 | pending |
| line-3 | line-3-0524-0525-s000318 | reverse | revenue | 4 | pending |
| line-3 | line-3-0480-0579-s001891 | forward | revenue | 4 | pending |
| line-3 | line-3-0480-0579-s001891 | reverse | revenue | 4 | pending |
| line-3 | line-3-0477-0582-s001988 | forward | revenue | 4 | pending |
| line-3 | line-3-0477-0582-s001988 | reverse | revenue | 3 | pending |
| line-3 | line-3-0262-0845-s009650 | reverse | revenue | 3 | pending |
| line-3 | line-3-0477-0582-s001988 | reverse | spare | 1 | pending |
| line-3 | line-3-0262-0845-s009650 | reverse | spare | 1 | pending |
| line-3 | line-3-0533-0514-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0524-0525-s000318 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0416-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0448-0559-s005072 | 6 | 4 | 2 | 119.0 |
| line-1-0451-0562-s005156 | 6 | 4 | 2 | 119.0 |
| line-1-0468-0575-s005604 | 6 | 4 | 2 | 119.0 |
| line-1-0471-0577-s005681 | 6 | 4 | 2 | 119.0 |
| line-1-0480-0579-s005877 | 6 | 4 | 2 | 119.0 |
| line-1-0493-0460-s011288 | 6 | 2 | 4 | 238.0 |
| line-1-0524-0525-s008192 | 6 | 4 | 2 | 119.0 |
| line-1-0583-0479-s013257 | 6 | 2 | 4 | 238.0 |
| line-1-0672-0499-s015214 | 6 | 2 | 4 | 238.0 |
| line-1-0851-0539-s019149 | 3 | 2 | 1 | 59.5 |
| line-2-0329-0468-s011748 | 2 | 2 | 0 | 0.0 |
| line-2-0448-0559-s008391 | 4 | 4 | 0 | 0.0 |
| line-2-0451-0562-s008306 | 4 | 4 | 0 | 0.0 |
| line-2-0468-0575-s007835 | 6 | 4 | 2 | 119.0 |
| line-2-0471-0577-s007759 | 6 | 4 | 2 | 119.0 |
| line-2-0477-0582-s007574 | 6 | 4 | 2 | 119.0 |
| line-2-0569-0652-s004990 | 6 | 2 | 4 | 238.0 |
| line-2-0745-0787-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0262-0845-s009650 | 4 | 2 | 2 | 119.0 |
| line-3-0477-0582-s001988 | 8 | 4 | 4 | 238.0 |
| line-3-0480-0579-s001891 | 8 | 4 | 4 | 238.0 |
| line-3-0524-0525-s000318 | 9 | 4 | 5 | 297.5 |
| line-3-0533-0514-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Tete/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
