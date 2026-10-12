# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 41 at depots = 77 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0445-0352-s011118 | line-1 | declared-depot | 13 | 637.0 | 4 |
| line-2-0381-0463-s000000 | line-2 | declared-depot | 12 | 588.0 | 3 |
| line-3-0333-0446-s000000 | line-3 | declared-depot | 7 | 343.0 | 3 |
| line-4-0347-0289-s000000 | line-4 | declared-depot | 9 | 441.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0115-0301-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0258-0288-s003349 | station | forward | revenue | 1 |
| line-1 | line-1-0258-0288-s003349 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0372-s008662 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0372-s008662 | station | reverse | revenue | 1 |
| line-1 | line-1-0375-0370-s008742 | station | forward | revenue | 1 |
| line-1 | line-1-0375-0370-s008742 | station | reverse | revenue | 1 |
| line-1 | line-1-0380-0359-s009027 | station | forward | revenue | 1 |
| line-1 | line-1-0380-0359-s009027 | station | reverse | revenue | 1 |
| line-1 | line-1-0445-0352-s011118 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0463-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0451-0385-s002362 | station | forward | revenue | 1 |
| line-2 | line-2-0451-0385-s002362 | station | reverse | revenue | 1 |
| line-2 | line-2-0523-0306-s004715 | station | forward | revenue | 1 |
| line-2 | line-2-0523-0306-s004715 | station | reverse | revenue | 1 |
| line-2 | line-2-0679-0164-s009445 | station | reverse | revenue | 2 |
| line-3 | line-3-0295-0267-s006044 | station | reverse | revenue | 2 |
| line-3 | line-3-0333-0446-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0347-0289-s004623 | station | forward | revenue | 1 |
| line-3 | line-3-0347-0289-s004623 | station | reverse | revenue | 1 |
| line-3 | line-3-0373-0372-s002329 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0372-s002329 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0370-s002249 | station | forward | revenue | 1 |
| line-3 | line-3-0375-0370-s002249 | station | reverse | revenue | 1 |
| line-3 | line-3-0380-0359-s002682 | station | forward | revenue | 1 |
| line-3 | line-3-0380-0359-s002682 | station | reverse | revenue | 1 |
| line-4 | line-4-0347-0289-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0361-0037-s005810 | station | reverse | revenue | 2 |
| line-1 | line-1-0445-0352-s011118 | depot | — | revenue | 10 |
| line-1 | line-1-0445-0352-s011118 | depot | — | spare | 2 |
| line-1 | line-1-0445-0352-s011118 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0381-0463-s000000 | depot | — | revenue | 10 |
| line-2 | line-2-0381-0463-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0381-0463-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0333-0446-s000000 | depot | — | revenue | 5 |
| line-3 | line-3-0333-0446-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0333-0446-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0347-0289-s000000 | depot | — | revenue | 7 |
| line-4 | line-4-0347-0289-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0347-0289-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/dhamar-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **77 trainsets at 18 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **41 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0115-0301-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0258-0288-s003349 | forward | revenue | 3 | pending |
| line-1 | line-1-0258-0288-s003349 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0372-s008662 | forward | revenue | 2 | pending |
| line-1 | line-1-0373-0372-s008662 | reverse | revenue | 2 | pending |
| line-1 | line-1-0375-0370-s008742 | forward | revenue | 2 | pending |
| line-1 | line-1-0375-0370-s008742 | reverse | revenue | 2 | pending |
| line-1 | line-1-0380-0359-s009027 | forward | revenue | 2 | pending |
| line-1 | line-1-0380-0359-s009027 | reverse | revenue | 2 | pending |
| line-1 | line-1-0445-0352-s011118 | reverse | revenue | 2 | pending |
| line-1 | line-1-0258-0288-s003349 | reverse | spare | 1 | pending |
| line-1 | line-1-0373-0372-s008662 | forward | spare | 1 | pending |
| line-1 | line-1-0373-0372-s008662 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0451-0385-s002362 | forward | revenue | 3 | pending |
| line-2 | line-2-0451-0385-s002362 | reverse | revenue | 3 | pending |
| line-2 | line-2-0523-0306-s004715 | forward | revenue | 3 | pending |
| line-2 | line-2-0523-0306-s004715 | reverse | revenue | 3 | pending |
| line-2 | line-2-0679-0164-s009445 | reverse | revenue | 3 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0451-0385-s002362 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0375-0370-s002249 | forward | revenue | 2 | pending |
| line-3 | line-3-0375-0370-s002249 | reverse | revenue | 2 | pending |
| line-3 | line-3-0373-0372-s002329 | forward | revenue | 2 | pending |
| line-3 | line-3-0373-0372-s002329 | reverse | revenue | 2 | pending |
| line-3 | line-3-0380-0359-s002682 | forward | revenue | 2 | pending |
| line-3 | line-3-0380-0359-s002682 | reverse | revenue | 2 | pending |
| line-3 | line-3-0347-0289-s004623 | forward | revenue | 1 | pending |
| line-3 | line-3-0347-0289-s004623 | reverse | revenue | 1 | pending |
| line-3 | line-3-0295-0267-s006044 | reverse | revenue | 1 | pending |
| line-3 | line-3-0347-0289-s004623 | forward | spare | 1 | pending |
| line-3 | line-3-0347-0289-s004623 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0347-0289-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0361-0037-s005810 | reverse | revenue | 5 | pending |
| line-4 | line-4-0361-0037-s005810 | reverse | spare | 1 | pending |
| line-4 | line-4-0347-0289-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,372.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0115-0301-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0258-0288-s003349 | 6 | 2 | 4 | 196.0 |
| line-1-0373-0372-s008662 | 6 | 4 | 2 | 98.0 |
| line-1-0375-0370-s008742 | 4 | 4 | 0 | 0.0 |
| line-1-0380-0359-s009027 | 4 | 4 | 0 | 0.0 |
| line-1-0445-0352-s011118 | 2 | 2 | 0 | 0.0 |
| line-2-0381-0463-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0451-0385-s002362 | 7 | 2 | 5 | 245.0 |
| line-2-0523-0306-s004715 | 6 | 2 | 4 | 196.0 |
| line-2-0679-0164-s009445 | 3 | 2 | 1 | 49.0 |
| line-3-0295-0267-s006044 | 1 | 2 | 0 | 0.0 |
| line-3-0333-0446-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0347-0289-s004623 | 4 | 4 | 0 | 0.0 |
| line-3-0373-0372-s002329 | 4 | 4 | 0 | 0.0 |
| line-3-0375-0370-s002249 | 4 | 4 | 0 | 0.0 |
| line-3-0380-0359-s002682 | 4 | 4 | 0 | 0.0 |
| line-4-0347-0289-s000000 | 7 | 2 | 5 | 245.0 |
| line-4-0361-0037-s005810 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Dhamar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
