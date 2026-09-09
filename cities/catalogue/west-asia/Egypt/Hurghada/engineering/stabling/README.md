# Station and depot overnight allocation

Plan: **34 trainsets at stations + 46 at depots = 80 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0553-0553-s014455 | line-1 | storage-at-existing-powered-service-point | 18 | 882.0 | 0 |
| line-2-0242-0142-s015180 | line-2 | declared-depot | 18 | 882.0 | 12 |
| line-3-0552-0311-s009332 | line-3 | storage-at-existing-powered-service-point | 10 | 490.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0041-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0228-0160-s003013 | station | forward | revenue | 1 |
| line-1 | line-1-0228-0160-s003013 | station | reverse | revenue | 1 |
| line-1 | line-1-0316-0272-s006017 | station | forward | revenue | 1 |
| line-1 | line-1-0316-0272-s006017 | station | reverse | revenue | 1 |
| line-1 | line-1-0395-0376-s009125 | station | forward | revenue | 1 |
| line-1 | line-1-0395-0376-s009125 | station | reverse | revenue | 1 |
| line-1 | line-1-0476-0468-s011960 | station | forward | revenue | 1 |
| line-1 | line-1-0476-0468-s011960 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0553-s014455 | station | reverse | revenue | 2 |
| line-2 | line-2-0242-0142-s015180 | station | reverse | revenue | 2 |
| line-2 | line-2-0344-0267-s011708 | station | forward | revenue | 1 |
| line-2 | line-2-0344-0267-s011708 | station | reverse | revenue | 1 |
| line-2 | line-2-0395-0376-s008759 | station | forward | revenue | 1 |
| line-2 | line-2-0395-0376-s008759 | station | reverse | revenue | 1 |
| line-2 | line-2-0483-0386-s006012 | station | forward | revenue | 1 |
| line-2 | line-2-0483-0386-s006012 | station | reverse | revenue | 1 |
| line-2 | line-2-0612-0409-s003009 | station | forward | revenue | 1 |
| line-2 | line-2-0612-0409-s003009 | station | reverse | revenue | 1 |
| line-2 | line-2-0729-0464-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0386-0435-s003027 | station | forward | revenue | 1 |
| line-3 | line-3-0386-0435-s003027 | station | reverse | revenue | 1 |
| line-3 | line-3-0395-0376-s004630 | station | forward | revenue | 1 |
| line-3 | line-3-0395-0376-s004630 | station | reverse | revenue | 1 |
| line-3 | line-3-0460-0535-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0462-0323-s006986 | station | forward | revenue | 1 |
| line-3 | line-3-0462-0323-s006986 | station | reverse | revenue | 1 |
| line-3 | line-3-0552-0311-s009332 | station | reverse | revenue | 2 |
| line-1 | line-1-0553-0553-s014455 | depot | — | revenue | 15 |
| line-1 | line-1-0553-0553-s014455 | depot | — | spare | 2 |
| line-1 | line-1-0553-0553-s014455 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0242-0142-s015180 | depot | — | revenue | 15 |
| line-2 | line-2-0242-0142-s015180 | depot | — | spare | 2 |
| line-2 | line-2-0242-0142-s015180 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0552-0311-s009332 | depot | — | revenue | 8 |
| line-3 | line-3-0552-0311-s009332 | depot | — | spare | 1 |
| line-3 | line-3-0552-0311-s009332 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hurghada-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **80 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **72 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0155-0041-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0228-0160-s003013 | forward | revenue | 3 | pending |
| line-1 | line-1-0228-0160-s003013 | reverse | revenue | 3 | pending |
| line-1 | line-1-0316-0272-s006017 | forward | revenue | 3 | pending |
| line-1 | line-1-0316-0272-s006017 | reverse | revenue | 3 | pending |
| line-1 | line-1-0395-0376-s009125 | forward | revenue | 3 | pending |
| line-1 | line-1-0395-0376-s009125 | reverse | revenue | 3 | pending |
| line-1 | line-1-0476-0468-s011960 | forward | revenue | 2 | pending |
| line-1 | line-1-0476-0468-s011960 | reverse | revenue | 2 | pending |
| line-1 | line-1-0553-0553-s014455 | reverse | revenue | 2 | pending |
| line-1 | line-1-0476-0468-s011960 | forward | spare | 1 | pending |
| line-1 | line-1-0476-0468-s011960 | reverse | spare | 1 | pending |
| line-1 | line-1-0553-0553-s014455 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0729-0464-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0612-0409-s003009 | forward | revenue | 3 | pending |
| line-2 | line-2-0612-0409-s003009 | reverse | revenue | 3 | pending |
| line-2 | line-2-0483-0386-s006012 | forward | revenue | 3 | pending |
| line-2 | line-2-0483-0386-s006012 | reverse | revenue | 3 | pending |
| line-2 | line-2-0395-0376-s008759 | forward | revenue | 3 | pending |
| line-2 | line-2-0395-0376-s008759 | reverse | revenue | 3 | pending |
| line-2 | line-2-0344-0267-s011708 | forward | revenue | 2 | pending |
| line-2 | line-2-0344-0267-s011708 | reverse | revenue | 2 | pending |
| line-2 | line-2-0242-0142-s015180 | reverse | revenue | 2 | pending |
| line-2 | line-2-0344-0267-s011708 | forward | spare | 1 | pending |
| line-2 | line-2-0344-0267-s011708 | reverse | spare | 1 | pending |
| line-2 | line-2-0242-0142-s015180 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0460-0535-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0386-0435-s003027 | forward | revenue | 3 | pending |
| line-3 | line-3-0386-0435-s003027 | reverse | revenue | 2 | pending |
| line-3 | line-3-0395-0376-s004630 | forward | revenue | 2 | pending |
| line-3 | line-3-0395-0376-s004630 | reverse | revenue | 2 | pending |
| line-3 | line-3-0462-0323-s006986 | forward | revenue | 2 | pending |
| line-3 | line-3-0462-0323-s006986 | reverse | revenue | 2 | pending |
| line-3 | line-3-0552-0311-s009332 | reverse | revenue | 2 | pending |
| line-3 | line-3-0386-0435-s003027 | reverse | spare | 1 | pending |
| line-3 | line-3-0395-0376-s004630 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**34 trainsets exceed the reference platform envelope**, requiring **1,666.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0041-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0228-0160-s003013 | 6 | 4 | 2 | 98.0 |
| line-1-0316-0272-s006017 | 6 | 4 | 2 | 98.0 |
| line-1-0395-0376-s009125 | 6 | 4 | 2 | 98.0 |
| line-1-0476-0468-s011960 | 6 | 2 | 4 | 196.0 |
| line-1-0553-0553-s014455 | 3 | 2 | 1 | 49.0 |
| line-2-0242-0142-s015180 | 3 | 2 | 1 | 49.0 |
| line-2-0344-0267-s011708 | 6 | 4 | 2 | 98.0 |
| line-2-0395-0376-s008759 | 6 | 4 | 2 | 98.0 |
| line-2-0483-0386-s006012 | 6 | 2 | 4 | 196.0 |
| line-2-0612-0409-s003009 | 6 | 2 | 4 | 196.0 |
| line-2-0729-0464-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0386-0435-s003027 | 6 | 2 | 4 | 196.0 |
| line-3-0395-0376-s004630 | 5 | 4 | 1 | 49.0 |
| line-3-0460-0535-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0462-0323-s006986 | 4 | 2 | 2 | 98.0 |
| line-3-0552-0311-s009332 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Hurghada/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
