# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 101 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0684-0936-s014580 | line-1 | declared-depot | 34 | 2,023.0 | 7 |
| line-2-0459-0399-s000000 | line-2 | declared-depot | 35 | 2,082.5 | 6 |
| line-3-0681-0604-s000000 | line-3 | declared-depot | 32 | 1,904.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0342-0395-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0431-0522-s003451 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0522-s003451 | station | reverse | revenue | 1 |
| line-1 | line-1-0496-0615-s006016 | station | forward | revenue | 1 |
| line-1 | line-1-0496-0615-s006016 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0747-s009605 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0747-s009605 | station | reverse | revenue | 1 |
| line-1 | line-1-0651-0838-s012088 | station | forward | revenue | 1 |
| line-1 | line-1-0651-0838-s012088 | station | reverse | revenue | 1 |
| line-1 | line-1-0684-0936-s014580 | station | reverse | revenue | 2 |
| line-2 | line-2-0323-1016-s014378 | station | reverse | revenue | 2 |
| line-2 | line-2-0368-0786-s008529 | station | forward | revenue | 1 |
| line-2 | line-2-0368-0786-s008529 | station | reverse | revenue | 1 |
| line-2 | line-2-0431-0522-s002698 | station | forward | revenue | 1 |
| line-2 | line-2-0431-0522-s002698 | station | reverse | revenue | 1 |
| line-2 | line-2-0459-0399-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0383-1021-s011991 | station | reverse | revenue | 2 |
| line-3 | line-3-0538-0823-s005858 | station | forward | revenue | 1 |
| line-3 | line-3-0538-0823-s005858 | station | reverse | revenue | 1 |
| line-3 | line-3-0588-0747-s003818 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0747-s003818 | station | reverse | revenue | 1 |
| line-3 | line-3-0681-0604-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0684-0936-s014580 | depot | — | revenue | 29 |
| line-1 | line-1-0684-0936-s014580 | depot | — | spare | 4 |
| line-1 | line-1-0684-0936-s014580 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0459-0399-s000000 | depot | — | revenue | 31 |
| line-2 | line-2-0459-0399-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0459-0399-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0681-0604-s000000 | depot | — | revenue | 28 |
| line-3 | line-3-0681-0604-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0681-0604-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/minya-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 14 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **101 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0342-0395-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0431-0522-s003451 | forward | revenue | 4 | pending |
| line-1 | line-1-0431-0522-s003451 | reverse | revenue | 4 | pending |
| line-1 | line-1-0496-0615-s006016 | forward | revenue | 4 | pending |
| line-1 | line-1-0496-0615-s006016 | reverse | revenue | 4 | pending |
| line-1 | line-1-0588-0747-s009605 | forward | revenue | 4 | pending |
| line-1 | line-1-0588-0747-s009605 | reverse | revenue | 4 | pending |
| line-1 | line-1-0651-0838-s012088 | forward | revenue | 4 | pending |
| line-1 | line-1-0651-0838-s012088 | reverse | revenue | 4 | pending |
| line-1 | line-1-0684-0936-s014580 | reverse | revenue | 4 | pending |
| line-1 | line-1-0431-0522-s003451 | forward | spare | 1 | pending |
| line-1 | line-1-0431-0522-s003451 | reverse | spare | 1 | pending |
| line-1 | line-1-0496-0615-s006016 | forward | spare | 1 | pending |
| line-1 | line-1-0496-0615-s006016 | reverse | spare | 1 | pending |
| line-1 | line-1-0588-0747-s009605 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0459-0399-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0431-0522-s002698 | forward | revenue | 7 | pending |
| line-2 | line-2-0431-0522-s002698 | reverse | revenue | 7 | pending |
| line-2 | line-2-0368-0786-s008529 | forward | revenue | 6 | pending |
| line-2 | line-2-0368-0786-s008529 | reverse | revenue | 6 | pending |
| line-2 | line-2-0323-1016-s014378 | reverse | revenue | 6 | pending |
| line-2 | line-2-0368-0786-s008529 | forward | spare | 1 | pending |
| line-2 | line-2-0368-0786-s008529 | reverse | spare | 1 | pending |
| line-2 | line-2-0323-1016-s014378 | reverse | spare | 1 | pending |
| line-2 | line-2-0459-0399-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0681-0604-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0588-0747-s003818 | forward | revenue | 6 | pending |
| line-3 | line-3-0588-0747-s003818 | reverse | revenue | 6 | pending |
| line-3 | line-3-0538-0823-s005858 | forward | revenue | 6 | pending |
| line-3 | line-3-0538-0823-s005858 | reverse | revenue | 6 | pending |
| line-3 | line-3-0383-1021-s011991 | reverse | revenue | 6 | pending |
| line-3 | line-3-0681-0604-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0588-0747-s003818 | forward | spare | 1 | pending |
| line-3 | line-3-0588-0747-s003818 | reverse | spare | 1 | pending |
| line-3 | line-3-0538-0823-s005858 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**93 trainsets exceed the reference platform envelope**, requiring **5,533.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0342-0395-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0431-0522-s003451 | 10 | 4 | 6 | 357.0 |
| line-1-0496-0615-s006016 | 10 | 2 | 8 | 476.0 |
| line-1-0588-0747-s009605 | 9 | 4 | 5 | 297.5 |
| line-1-0651-0838-s012088 | 8 | 2 | 6 | 357.0 |
| line-1-0684-0936-s014580 | 4 | 2 | 2 | 119.0 |
| line-2-0323-1016-s014378 | 7 | 2 | 5 | 297.5 |
| line-2-0368-0786-s008529 | 14 | 2 | 12 | 714.0 |
| line-2-0431-0522-s002698 | 14 | 4 | 10 | 595.0 |
| line-2-0459-0399-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0383-1021-s011991 | 6 | 2 | 4 | 238.0 |
| line-3-0538-0823-s005858 | 13 | 2 | 11 | 654.5 |
| line-3-0588-0747-s003818 | 14 | 4 | 10 | 595.0 |
| line-3-0681-0604-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Minya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
