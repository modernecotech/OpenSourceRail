# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 48 at depots = 70 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0717-0503-s008168 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0451-0387-s000000 | line-2 | declared-depot | 15 | 892.5 | 4 |
| line-3-0591-0365-s000000 | line-3 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0329-0548-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0472-0531-s003013 | station | forward | revenue | 1 |
| line-1 | line-1-0472-0531-s003013 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0524-s004422 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0524-s004422 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0503-s008168 | station | reverse | revenue | 2 |
| line-2 | line-2-0451-0387-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0499-0468-s002088 | station | forward | revenue | 1 |
| line-2 | line-2-0499-0468-s002088 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0549-s004191 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0549-s004191 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0647-s006725 | station | reverse | revenue | 2 |
| line-3 | line-3-0428-0586-s006145 | station | reverse | revenue | 2 |
| line-3 | line-3-0511-0473-s003010 | station | forward | revenue | 1 |
| line-3 | line-3-0511-0473-s003010 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0365-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0717-0503-s008168 | depot | — | revenue | 16 |
| line-1 | line-1-0717-0503-s008168 | depot | — | spare | 2 |
| line-1 | line-1-0717-0503-s008168 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0451-0387-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0451-0387-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0451-0387-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0591-0365-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0591-0365-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0591-0365-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ngaoundere-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **70 trainsets at 11 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **62 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **48 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0329-0548-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0472-0531-s003013 | forward | revenue | 4 | pending |
| line-1 | line-1-0472-0531-s003013 | reverse | revenue | 4 | pending |
| line-1 | line-1-0539-0524-s004422 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0524-s004422 | reverse | revenue | 4 | pending |
| line-1 | line-1-0717-0503-s008168 | reverse | revenue | 4 | pending |
| line-1 | line-1-0329-0548-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0472-0531-s003013 | forward | spare | 1 | pending |
| line-1 | line-1-0472-0531-s003013 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0387-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0499-0468-s002088 | forward | revenue | 4 | pending |
| line-2 | line-2-0499-0468-s002088 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0549-s004191 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0549-s004191 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0647-s006725 | reverse | revenue | 3 | pending |
| line-2 | line-2-0499-0468-s002088 | reverse | spare | 1 | pending |
| line-2 | line-2-0546-0549-s004191 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0549-s004191 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0591-0365-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0511-0473-s003010 | forward | revenue | 5 | pending |
| line-3 | line-3-0511-0473-s003010 | reverse | revenue | 4 | pending |
| line-3 | line-3-0428-0586-s006145 | reverse | revenue | 4 | pending |
| line-3 | line-3-0511-0473-s003010 | reverse | spare | 1 | pending |
| line-3 | line-3-0428-0586-s006145 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **2,380.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0329-0548-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0472-0531-s003013 | 10 | 2 | 8 | 476.0 |
| line-1-0539-0524-s004422 | 8 | 4 | 4 | 238.0 |
| line-1-0717-0503-s008168 | 4 | 2 | 2 | 119.0 |
| line-2-0451-0387-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0499-0468-s002088 | 8 | 4 | 4 | 238.0 |
| line-2-0546-0549-s004191 | 8 | 4 | 4 | 238.0 |
| line-2-0604-0647-s006725 | 3 | 2 | 1 | 59.5 |
| line-3-0428-0586-s006145 | 5 | 2 | 3 | 178.5 |
| line-3-0511-0473-s003010 | 10 | 4 | 6 | 357.0 |
| line-3-0591-0365-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Ngaoundere/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
