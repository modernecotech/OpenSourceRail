# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 46 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0294-0029-s000000 | line-1 | declared-depot | 13 | 637.0 | 4 |
| line-2-0710-0450-s000000 | line-2 | declared-depot | 14 | 686.0 | 4 |
| line-3-0492-0723-s013309 | line-3 | declared-depot | 19 | 931.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0255-0427-s011038 | station | reverse | revenue | 2 |
| line-1 | line-1-0287-0338-s008964 | station | forward | revenue | 1 |
| line-1 | line-1-0287-0338-s008964 | station | reverse | revenue | 1 |
| line-1 | line-1-0294-0029-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0321-0238-s006664 | station | forward | revenue | 1 |
| line-1 | line-1-0321-0238-s006664 | station | reverse | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | reverse | revenue | 1 |
| line-2 | line-2-0253-0189-s012441 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0238-s010569 | station | forward | revenue | 1 |
| line-2 | line-2-0321-0238-s010569 | station | reverse | revenue | 1 |
| line-2 | line-2-0385-0285-s008795 | station | forward | revenue | 1 |
| line-2 | line-2-0385-0285-s008795 | station | reverse | revenue | 1 |
| line-2 | line-2-0493-0364-s005781 | station | forward | revenue | 1 |
| line-2 | line-2-0493-0364-s005781 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0406-s004168 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0406-s004168 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0450-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0205-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0287-0338-s003361 | station | forward | revenue | 1 |
| line-3 | line-3-0287-0338-s003361 | station | reverse | revenue | 1 |
| line-3 | line-3-0351-0437-s006026 | station | forward | revenue | 1 |
| line-3 | line-3-0351-0437-s006026 | station | reverse | revenue | 1 |
| line-3 | line-3-0492-0723-s013309 | station | reverse | revenue | 2 |
| line-1 | line-1-0294-0029-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0294-0029-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0294-0029-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0710-0450-s000000 | depot | — | revenue | 11 |
| line-2 | line-2-0710-0450-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0710-0450-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0492-0723-s013309 | depot | — | revenue | 16 |
| line-3 | line-3-0492-0723-s013309 | depot | — | spare | 2 |
| line-3 | line-3-0492-0723-s013309 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rubavu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 15 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **67 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0294-0029-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0321-0238-s006664 | forward | revenue | 3 | pending |
| line-1 | line-1-0321-0238-s006664 | reverse | revenue | 2 | pending |
| line-1 | line-1-0287-0338-s008964 | forward | revenue | 2 | pending |
| line-1 | line-1-0287-0338-s008964 | reverse | revenue | 2 | pending |
| line-1 | line-1-0255-0427-s011038 | reverse | revenue | 2 | pending |
| line-1 | line-1-0321-0238-s006664 | reverse | spare | 1 | pending |
| line-1 | line-1-0287-0338-s008964 | forward | spare | 1 | pending |
| line-1 | line-1-0287-0338-s008964 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0710-0450-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0406-s004168 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0406-s004168 | reverse | revenue | 3 | pending |
| line-2 | line-2-0493-0364-s005781 | forward | revenue | 2 | pending |
| line-2 | line-2-0493-0364-s005781 | reverse | revenue | 2 | pending |
| line-2 | line-2-0385-0285-s008795 | forward | revenue | 2 | pending |
| line-2 | line-2-0385-0285-s008795 | reverse | revenue | 2 | pending |
| line-2 | line-2-0321-0238-s010569 | forward | revenue | 2 | pending |
| line-2 | line-2-0321-0238-s010569 | reverse | revenue | 2 | pending |
| line-2 | line-2-0253-0189-s012441 | reverse | revenue | 2 | pending |
| line-2 | line-2-0493-0364-s005781 | forward | spare | 1 | pending |
| line-2 | line-2-0493-0364-s005781 | reverse | spare | 1 | pending |
| line-2 | line-2-0385-0285-s008795 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0287-0338-s003361 | forward | revenue | 4 | pending |
| line-3 | line-3-0287-0338-s003361 | reverse | revenue | 4 | pending |
| line-3 | line-3-0351-0437-s006026 | forward | revenue | 4 | pending |
| line-3 | line-3-0351-0437-s006026 | reverse | revenue | 4 | pending |
| line-3 | line-3-0492-0723-s013309 | reverse | revenue | 4 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0287-0338-s003361 | forward | spare | 1 | pending |
| line-3 | line-3-0287-0338-s003361 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**38 trainsets exceed the reference platform envelope**, requiring **1,862.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0255-0427-s011038 | 2 | 2 | 0 | 0.0 |
| line-1-0287-0338-s008964 | 6 | 4 | 2 | 98.0 |
| line-1-0294-0029-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0321-0238-s006664 | 6 | 4 | 2 | 98.0 |
| line-1-0356-0080-s003014 | 6 | 2 | 4 | 196.0 |
| line-2-0253-0189-s012441 | 2 | 2 | 0 | 0.0 |
| line-2-0321-0238-s010569 | 4 | 4 | 0 | 0.0 |
| line-2-0385-0285-s008795 | 5 | 2 | 3 | 147.0 |
| line-2-0493-0364-s005781 | 6 | 2 | 4 | 196.0 |
| line-2-0551-0406-s004168 | 6 | 2 | 4 | 196.0 |
| line-2-0710-0450-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0205-0212-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0287-0338-s003361 | 10 | 4 | 6 | 294.0 |
| line-3-0351-0437-s006026 | 8 | 2 | 6 | 294.0 |
| line-3-0492-0723-s013309 | 4 | 2 | 2 | 98.0 |

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
