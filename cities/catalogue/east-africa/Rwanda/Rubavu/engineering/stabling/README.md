# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 63 at depots = 95 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0294-0029-s000000 | line-1 | declared-depot | 13 | 637.0 | 4 |
| line-2-0253-0189-s015447 | line-2 | declared-depot | 20 | 980.0 | 5 |
| line-3-0205-0212-s000000 | line-3 | declared-depot | 18 | 882.0 | 4 |
| line-4-0420-0544-s000000 | line-4 | declared-depot | 12 | 588.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0255-0427-s011038 | station | reverse | revenue | 2 |
| line-1 | line-1-0287-0338-s008964 | station | forward | revenue | 1 |
| line-1 | line-1-0287-0338-s008964 | station | reverse | revenue | 1 |
| line-1 | line-1-0294-0029-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0312-0264-s007259 | station | forward | revenue | 1 |
| line-1 | line-1-0312-0264-s007259 | station | reverse | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | reverse | revenue | 1 |
| line-2 | line-2-0253-0189-s015447 | station | reverse | revenue | 2 |
| line-2 | line-2-0312-0264-s012588 | station | forward | revenue | 1 |
| line-2 | line-2-0312-0264-s012588 | station | reverse | revenue | 1 |
| line-2 | line-2-0446-0343-s007640 | station | forward | revenue | 1 |
| line-2 | line-2-0446-0343-s007640 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0402-s004630 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0402-s004630 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0450-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0205-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0287-0338-s003361 | station | forward | revenue | 1 |
| line-3 | line-3-0287-0338-s003361 | station | reverse | revenue | 1 |
| line-3 | line-3-0420-0544-s008878 | station | forward | revenue | 1 |
| line-3 | line-3-0420-0544-s008878 | station | reverse | revenue | 1 |
| line-3 | line-3-0492-0723-s013309 | station | reverse | revenue | 2 |
| line-4 | line-4-0139-0613-s007130 | station | reverse | revenue | 2 |
| line-4 | line-4-0420-0544-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0294-0029-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0294-0029-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0294-0029-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0253-0189-s015447 | depot | — | revenue | 17 |
| line-2 | line-2-0253-0189-s015447 | depot | — | spare | 2 |
| line-2 | line-2-0253-0189-s015447 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0205-0212-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0205-0212-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0205-0212-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0420-0544-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0420-0544-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0420-0544-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rubavu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **95 trainsets at 16 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **84 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **63 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0294-0029-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0312-0264-s007259 | forward | revenue | 3 | pending |
| line-1 | line-1-0312-0264-s007259 | reverse | revenue | 2 | pending |
| line-1 | line-1-0287-0338-s008964 | forward | revenue | 2 | pending |
| line-1 | line-1-0287-0338-s008964 | reverse | revenue | 2 | pending |
| line-1 | line-1-0255-0427-s011038 | reverse | revenue | 2 | pending |
| line-1 | line-1-0312-0264-s007259 | reverse | spare | 1 | pending |
| line-1 | line-1-0287-0338-s008964 | forward | spare | 1 | pending |
| line-1 | line-1-0287-0338-s008964 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0710-0450-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0552-0402-s004630 | forward | revenue | 4 | pending |
| line-2 | line-2-0552-0402-s004630 | reverse | revenue | 4 | pending |
| line-2 | line-2-0446-0343-s007640 | forward | revenue | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | reverse | revenue | 3 | pending |
| line-2 | line-2-0312-0264-s012588 | forward | revenue | 3 | pending |
| line-2 | line-2-0312-0264-s012588 | reverse | revenue | 3 | pending |
| line-2 | line-2-0253-0189-s015447 | reverse | revenue | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | forward | spare | 1 | pending |
| line-2 | line-2-0446-0343-s007640 | reverse | spare | 1 | pending |
| line-2 | line-2-0312-0264-s012588 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0287-0338-s003361 | forward | revenue | 4 | pending |
| line-3 | line-3-0287-0338-s003361 | reverse | revenue | 4 | pending |
| line-3 | line-3-0420-0544-s008878 | forward | revenue | 4 | pending |
| line-3 | line-3-0420-0544-s008878 | reverse | revenue | 4 | pending |
| line-3 | line-3-0492-0723-s013309 | reverse | revenue | 3 | pending |
| line-3 | line-3-0492-0723-s013309 | reverse | spare | 1 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0287-0338-s003361 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0420-0544-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0139-0613-s007130 | reverse | revenue | 7 | pending |
| line-4 | line-4-0420-0544-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0139-0613-s007130 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**53 trainsets exceed the reference platform envelope**, requiring **2,597.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0255-0427-s011038 | 2 | 2 | 0 | 0.0 |
| line-1-0287-0338-s008964 | 6 | 4 | 2 | 98.0 |
| line-1-0294-0029-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0312-0264-s007259 | 6 | 4 | 2 | 98.0 |
| line-1-0356-0080-s003014 | 6 | 2 | 4 | 196.0 |
| line-2-0253-0189-s015447 | 3 | 2 | 1 | 49.0 |
| line-2-0312-0264-s012588 | 7 | 4 | 3 | 147.0 |
| line-2-0446-0343-s007640 | 8 | 2 | 6 | 294.0 |
| line-2-0552-0402-s004630 | 8 | 2 | 6 | 294.0 |
| line-2-0710-0450-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0205-0212-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0287-0338-s003361 | 9 | 4 | 5 | 245.0 |
| line-3-0420-0544-s008878 | 8 | 4 | 4 | 196.0 |
| line-3-0492-0723-s013309 | 4 | 2 | 2 | 98.0 |
| line-4-0139-0613-s007130 | 8 | 2 | 6 | 294.0 |
| line-4-0420-0544-s000000 | 8 | 2 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Rubavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
