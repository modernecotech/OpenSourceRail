# Station and depot overnight allocation

Plan: **24 trainsets at stations + 57 at depots = 81 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0851-0539-s014495 | line-1 | declared-depot | 20 | 1,190.0 | 13 |
| line-2-0329-0468-s012615 | line-2 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-3-0262-0845-s010756 | line-3 | storage-at-existing-powered-service-point | 18 | 1,071.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0416-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0354-0508-s002598 | station | forward | revenue | 1 |
| line-1 | line-1-0354-0508-s002598 | station | reverse | revenue | 1 |
| line-1 | line-1-0459-0541-s005195 | station | forward | revenue | 1 |
| line-1 | line-1-0459-0541-s005195 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0553-s007540 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0553-s007540 | station | reverse | revenue | 1 |
| line-1 | line-1-0851-0539-s014495 | station | reverse | revenue | 2 |
| line-2 | line-2-0329-0468-s012615 | station | reverse | revenue | 2 |
| line-2 | line-2-0548-0553-s007430 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0553-s007430 | station | reverse | revenue | 1 |
| line-2 | line-2-0589-0646-s005114 | station | forward | revenue | 1 |
| line-2 | line-2-0589-0646-s005114 | station | reverse | revenue | 1 |
| line-2 | line-2-0745-0787-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0262-0845-s010756 | station | reverse | revenue | 2 |
| line-3 | line-3-0485-0647-s003504 | station | forward | revenue | 1 |
| line-3 | line-3-0485-0647-s003504 | station | reverse | revenue | 1 |
| line-3 | line-3-0533-0514-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0851-0539-s014495 | depot | — | revenue | 17 |
| line-1 | line-1-0851-0539-s014495 | depot | — | spare | 2 |
| line-1 | line-1-0851-0539-s014495 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0329-0468-s012615 | depot | — | revenue | 16 |
| line-2 | line-2-0329-0468-s012615 | depot | — | spare | 2 |
| line-2 | line-2-0329-0468-s012615 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0262-0845-s010756 | depot | — | revenue | 15 |
| line-3 | line-3-0262-0845-s010756 | depot | — | spare | 2 |
| line-3 | line-3-0262-0845-s010756 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tete-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **81 trainsets at 12 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **72 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **57 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0297-0416-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0354-0508-s002598 | forward | revenue | 4 | pending |
| line-1 | line-1-0354-0508-s002598 | reverse | revenue | 4 | pending |
| line-1 | line-1-0459-0541-s005195 | forward | revenue | 3 | pending |
| line-1 | line-1-0459-0541-s005195 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0553-s007540 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0553-s007540 | reverse | revenue | 3 | pending |
| line-1 | line-1-0851-0539-s014495 | reverse | revenue | 3 | pending |
| line-1 | line-1-0459-0541-s005195 | forward | spare | 1 | pending |
| line-1 | line-1-0459-0541-s005195 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0553-s007540 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0745-0787-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0589-0646-s005114 | forward | revenue | 4 | pending |
| line-2 | line-2-0589-0646-s005114 | reverse | revenue | 4 | pending |
| line-2 | line-2-0548-0553-s007430 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0553-s007430 | reverse | revenue | 4 | pending |
| line-2 | line-2-0329-0468-s012615 | reverse | revenue | 4 | pending |
| line-2 | line-2-0745-0787-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0589-0646-s005114 | forward | spare | 1 | pending |
| line-2 | line-2-0589-0646-s005114 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0514-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0485-0647-s003504 | forward | revenue | 5 | pending |
| line-3 | line-3-0485-0647-s003504 | reverse | revenue | 5 | pending |
| line-3 | line-3-0262-0845-s010756 | reverse | revenue | 5 | pending |
| line-3 | line-3-0485-0647-s003504 | forward | spare | 1 | pending |
| line-3 | line-3-0485-0647-s003504 | reverse | spare | 1 | pending |
| line-3 | line-3-0262-0845-s010756 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**53 trainsets exceed the reference platform envelope**, requiring **3,153.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0416-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0354-0508-s002598 | 8 | 2 | 6 | 357.0 |
| line-1-0459-0541-s005195 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0553-s007540 | 7 | 4 | 3 | 178.5 |
| line-1-0851-0539-s014495 | 3 | 2 | 1 | 59.5 |
| line-2-0329-0468-s012615 | 4 | 2 | 2 | 119.0 |
| line-2-0548-0553-s007430 | 8 | 4 | 4 | 238.0 |
| line-2-0589-0646-s005114 | 10 | 2 | 8 | 476.0 |
| line-2-0745-0787-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0262-0845-s010756 | 6 | 2 | 4 | 238.0 |
| line-3-0485-0647-s003504 | 12 | 2 | 10 | 595.0 |
| line-3-0533-0514-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Tete/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
