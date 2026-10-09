# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 46 at depots = 78 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0524-0309-s008649 | line-1 | declared-depot | 16 | 952.0 | 4 |
| line-2-0532-0606-s000000 | line-2 | declared-depot | 13 | 773.5 | 3 |
| line-3-0683-0658-s000000 | line-3 | declared-depot | 10 | 595.0 | 3 |
| line-4-0578-0376-s000000 | line-4 | declared-depot | 7 | 416.5 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0524-0309-s008649 | station | reverse | revenue | 2 |
| line-1 | line-1-0578-0376-s006721 | station | forward | revenue | 1 |
| line-1 | line-1-0578-0376-s006721 | station | reverse | revenue | 1 |
| line-1 | line-1-0616-0422-s005393 | station | forward | revenue | 1 |
| line-1 | line-1-0616-0422-s005393 | station | reverse | revenue | 1 |
| line-1 | line-1-0674-0493-s003305 | station | forward | revenue | 1 |
| line-1 | line-1-0674-0493-s003305 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0547-s001751 | station | forward | revenue | 1 |
| line-1 | line-1-0717-0547-s001751 | station | reverse | revenue | 1 |
| line-1 | line-1-0767-0608-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0532-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0577-0507-s002400 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0507-s002400 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0422-s004470 | station | forward | revenue | 1 |
| line-2 | line-2-0616-0422-s004470 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0359-s005985 | station | reverse | revenue | 2 |
| line-3 | line-3-0670-0414-s004988 | station | reverse | revenue | 2 |
| line-3 | line-3-0674-0493-s003375 | station | forward | revenue | 1 |
| line-3 | line-3-0674-0493-s003375 | station | reverse | revenue | 1 |
| line-3 | line-3-0679-0590-s001393 | station | forward | revenue | 1 |
| line-3 | line-3-0679-0590-s001393 | station | reverse | revenue | 1 |
| line-3 | line-3-0683-0658-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0514-0488-s002805 | station | reverse | revenue | 2 |
| line-4 | line-4-0578-0376-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0524-0309-s008649 | depot | — | revenue | 13 |
| line-1 | line-1-0524-0309-s008649 | depot | — | spare | 2 |
| line-1 | line-1-0524-0309-s008649 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0532-0606-s000000 | depot | — | revenue | 11 |
| line-2 | line-2-0532-0606-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0532-0606-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0683-0658-s000000 | depot | — | revenue | 8 |
| line-3 | line-3-0683-0658-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0683-0658-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0578-0376-s000000 | depot | — | revenue | 5 |
| line-4 | line-4-0578-0376-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0578-0376-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/port-said-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **78 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **69 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0767-0608-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0717-0547-s001751 | forward | revenue | 3 | pending |
| line-1 | line-1-0717-0547-s001751 | reverse | revenue | 3 | pending |
| line-1 | line-1-0674-0493-s003305 | forward | revenue | 3 | pending |
| line-1 | line-1-0674-0493-s003305 | reverse | revenue | 3 | pending |
| line-1 | line-1-0616-0422-s005393 | forward | revenue | 2 | pending |
| line-1 | line-1-0616-0422-s005393 | reverse | revenue | 2 | pending |
| line-1 | line-1-0578-0376-s006721 | forward | revenue | 2 | pending |
| line-1 | line-1-0578-0376-s006721 | reverse | revenue | 2 | pending |
| line-1 | line-1-0524-0309-s008649 | reverse | revenue | 2 | pending |
| line-1 | line-1-0616-0422-s005393 | forward | spare | 1 | pending |
| line-1 | line-1-0616-0422-s005393 | reverse | spare | 1 | pending |
| line-1 | line-1-0578-0376-s006721 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0606-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0577-0507-s002400 | forward | revenue | 3 | pending |
| line-2 | line-2-0577-0507-s002400 | reverse | revenue | 3 | pending |
| line-2 | line-2-0616-0422-s004470 | forward | revenue | 3 | pending |
| line-2 | line-2-0616-0422-s004470 | reverse | revenue | 3 | pending |
| line-2 | line-2-0644-0359-s005985 | reverse | revenue | 3 | pending |
| line-2 | line-2-0577-0507-s002400 | forward | spare | 1 | pending |
| line-2 | line-2-0577-0507-s002400 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0683-0658-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0679-0590-s001393 | forward | revenue | 3 | pending |
| line-3 | line-3-0679-0590-s001393 | reverse | revenue | 3 | pending |
| line-3 | line-3-0674-0493-s003375 | forward | revenue | 3 | pending |
| line-3 | line-3-0674-0493-s003375 | reverse | revenue | 2 | pending |
| line-3 | line-3-0670-0414-s004988 | reverse | revenue | 2 | pending |
| line-3 | line-3-0674-0493-s003375 | reverse | spare | 1 | pending |
| line-3 | line-3-0670-0414-s004988 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0578-0376-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0514-0488-s002805 | reverse | revenue | 4 | pending |
| line-4 | line-4-0514-0488-s002805 | reverse | spare | 1 | pending |
| line-4 | line-4-0578-0376-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **2,142.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0524-0309-s008649 | 2 | 2 | 0 | 0.0 |
| line-1-0578-0376-s006721 | 5 | 4 | 1 | 59.5 |
| line-1-0616-0422-s005393 | 6 | 4 | 2 | 119.0 |
| line-1-0674-0493-s003305 | 6 | 4 | 2 | 119.0 |
| line-1-0717-0547-s001751 | 6 | 2 | 4 | 238.0 |
| line-1-0767-0608-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0532-0606-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0577-0507-s002400 | 8 | 2 | 6 | 357.0 |
| line-2-0616-0422-s004470 | 6 | 4 | 2 | 119.0 |
| line-2-0644-0359-s005985 | 3 | 2 | 1 | 59.5 |
| line-3-0670-0414-s004988 | 3 | 2 | 1 | 59.5 |
| line-3-0674-0493-s003375 | 6 | 4 | 2 | 119.0 |
| line-3-0679-0590-s001393 | 6 | 2 | 4 | 238.0 |
| line-3-0683-0658-s000000 | 3 | 2 | 1 | 59.5 |
| line-4-0514-0488-s002805 | 5 | 2 | 3 | 178.5 |
| line-4-0578-0376-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Port-Said/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
