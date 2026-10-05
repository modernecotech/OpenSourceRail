# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 48 at depots = 74 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0717-0503-s008168 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0451-0387-s000000 | line-2 | declared-depot | 15 | 892.5 | 4 |
| line-3-0591-0365-s000000 | line-3 | declared-depot | 15 | 892.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0329-0548-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0468-0532-s002924 | station | forward | revenue | 1 |
| line-1 | line-1-0468-0532-s002924 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0524-s004282 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0524-s004282 | station | reverse | revenue | 1 |
| line-1 | line-1-0625-0514-s006225 | station | forward | revenue | 1 |
| line-1 | line-1-0625-0514-s006225 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0503-s008168 | station | reverse | revenue | 2 |
| line-2 | line-2-0451-0387-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0506-0480-s002398 | station | forward | revenue | 1 |
| line-2 | line-2-0506-0480-s002398 | station | reverse | revenue | 1 |
| line-2 | line-2-0532-0524-s003552 | station | forward | revenue | 1 |
| line-2 | line-2-0532-0524-s003552 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0647-s006725 | station | reverse | revenue | 2 |
| line-3 | line-3-0428-0586-s006145 | station | reverse | revenue | 2 |
| line-3 | line-3-0468-0532-s004617 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0532-s004617 | station | reverse | revenue | 1 |
| line-3 | line-3-0506-0480-s003203 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0480-s003203 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0365-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0717-0503-s008168 | depot | — | revenue | 15 |
| line-1 | line-1-0717-0503-s008168 | depot | — | spare | 2 |
| line-1 | line-1-0717-0503-s008168 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0451-0387-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0451-0387-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0451-0387-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0591-0365-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0591-0365-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0591-0365-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ngaoundere-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **74 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **48 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0329-0548-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0468-0532-s002924 | forward | revenue | 3 | pending |
| line-1 | line-1-0468-0532-s002924 | reverse | revenue | 3 | pending |
| line-1 | line-1-0532-0524-s004282 | forward | revenue | 3 | pending |
| line-1 | line-1-0532-0524-s004282 | reverse | revenue | 3 | pending |
| line-1 | line-1-0625-0514-s006225 | forward | revenue | 3 | pending |
| line-1 | line-1-0625-0514-s006225 | reverse | revenue | 3 | pending |
| line-1 | line-1-0717-0503-s008168 | reverse | revenue | 3 | pending |
| line-1 | line-1-0468-0532-s002924 | forward | spare | 1 | pending |
| line-1 | line-1-0468-0532-s002924 | reverse | spare | 1 | pending |
| line-1 | line-1-0532-0524-s004282 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0387-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0506-0480-s002398 | forward | revenue | 4 | pending |
| line-2 | line-2-0506-0480-s002398 | reverse | revenue | 3 | pending |
| line-2 | line-2-0532-0524-s003552 | forward | revenue | 3 | pending |
| line-2 | line-2-0532-0524-s003552 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0647-s006725 | reverse | revenue | 3 | pending |
| line-2 | line-2-0506-0480-s002398 | reverse | spare | 1 | pending |
| line-2 | line-2-0532-0524-s003552 | forward | spare | 1 | pending |
| line-2 | line-2-0532-0524-s003552 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0591-0365-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0506-0480-s003203 | forward | revenue | 4 | pending |
| line-3 | line-3-0506-0480-s003203 | reverse | revenue | 3 | pending |
| line-3 | line-3-0468-0532-s004617 | forward | revenue | 3 | pending |
| line-3 | line-3-0468-0532-s004617 | reverse | revenue | 3 | pending |
| line-3 | line-3-0428-0586-s006145 | reverse | revenue | 3 | pending |
| line-3 | line-3-0506-0480-s003203 | reverse | spare | 1 | pending |
| line-3 | line-3-0468-0532-s004617 | forward | spare | 1 | pending |
| line-3 | line-3-0468-0532-s004617 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **2,142.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0329-0548-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0468-0532-s002924 | 8 | 4 | 4 | 238.0 |
| line-1-0532-0524-s004282 | 7 | 4 | 3 | 178.5 |
| line-1-0625-0514-s006225 | 6 | 2 | 4 | 238.0 |
| line-1-0717-0503-s008168 | 3 | 2 | 1 | 59.5 |
| line-2-0451-0387-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0506-0480-s002398 | 8 | 4 | 4 | 238.0 |
| line-2-0532-0524-s003552 | 8 | 4 | 4 | 238.0 |
| line-2-0604-0647-s006725 | 3 | 2 | 1 | 59.5 |
| line-3-0428-0586-s006145 | 3 | 2 | 1 | 59.5 |
| line-3-0468-0532-s004617 | 8 | 4 | 4 | 238.0 |
| line-3-0506-0480-s003203 | 8 | 4 | 4 | 238.0 |
| line-3-0591-0365-s000000 | 4 | 2 | 2 | 119.0 |

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
