# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 70 at depots = 92 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0371-0993-s013266 | line-1 | declared-depot | 32 | 1,904.0 | 6 |
| line-2-0452-0423-s000000 | line-2 | declared-depot | 15 | 892.5 | 4 |
| line-3-0682-0473-s000000 | line-3 | declared-depot | 23 | 1,368.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0371-0993-s013266 | station | reverse | revenue | 2 |
| line-1 | line-1-0498-0800-s008143 | station | forward | revenue | 1 |
| line-1 | line-1-0498-0800-s008143 | station | reverse | revenue | 1 |
| line-1 | line-1-0622-0603-s003000 | station | forward | revenue | 1 |
| line-1 | line-1-0622-0603-s003000 | station | reverse | revenue | 1 |
| line-1 | line-1-0693-0490-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0400-0736-s006691 | station | reverse | revenue | 2 |
| line-2 | line-2-0417-0632-s004470 | station | forward | revenue | 1 |
| line-2 | line-2-0417-0632-s004470 | station | reverse | revenue | 1 |
| line-2 | line-2-0435-0527-s002221 | station | forward | revenue | 1 |
| line-2 | line-2-0435-0527-s002221 | station | reverse | revenue | 1 |
| line-2 | line-2-0452-0423-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0301-0356-s009265 | station | reverse | revenue | 2 |
| line-3 | line-3-0547-0470-s003013 | station | forward | revenue | 1 |
| line-3 | line-3-0547-0470-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0682-0473-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0371-0993-s013266 | depot | — | revenue | 28 |
| line-1 | line-1-0371-0993-s013266 | depot | — | spare | 3 |
| line-1 | line-1-0371-0993-s013266 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0452-0423-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0452-0423-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0452-0423-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0682-0473-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0682-0473-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0682-0473-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/latakia-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **92 trainsets at 11 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **70 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0693-0490-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0622-0603-s003000 | forward | revenue | 6 | pending |
| line-1 | line-1-0622-0603-s003000 | reverse | revenue | 6 | pending |
| line-1 | line-1-0498-0800-s008143 | forward | revenue | 6 | pending |
| line-1 | line-1-0498-0800-s008143 | reverse | revenue | 6 | pending |
| line-1 | line-1-0371-0993-s013266 | reverse | revenue | 6 | pending |
| line-1 | line-1-0693-0490-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0622-0603-s003000 | forward | spare | 1 | pending |
| line-1 | line-1-0622-0603-s003000 | reverse | spare | 1 | pending |
| line-1 | line-1-0498-0800-s008143 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0452-0423-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0435-0527-s002221 | forward | revenue | 4 | pending |
| line-2 | line-2-0435-0527-s002221 | reverse | revenue | 3 | pending |
| line-2 | line-2-0417-0632-s004470 | forward | revenue | 3 | pending |
| line-2 | line-2-0417-0632-s004470 | reverse | revenue | 3 | pending |
| line-2 | line-2-0400-0736-s006691 | reverse | revenue | 3 | pending |
| line-2 | line-2-0435-0527-s002221 | reverse | spare | 1 | pending |
| line-2 | line-2-0417-0632-s004470 | forward | spare | 1 | pending |
| line-2 | line-2-0417-0632-s004470 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0682-0473-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0547-0470-s003013 | forward | revenue | 7 | pending |
| line-3 | line-3-0547-0470-s003013 | reverse | revenue | 6 | pending |
| line-3 | line-3-0301-0356-s009265 | reverse | revenue | 6 | pending |
| line-3 | line-3-0547-0470-s003013 | reverse | spare | 1 | pending |
| line-3 | line-3-0301-0356-s009265 | reverse | spare | 1 | pending |
| line-3 | line-3-0682-0473-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**70 trainsets exceed the reference platform envelope**, requiring **4,165.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0371-0993-s013266 | 6 | 2 | 4 | 238.0 |
| line-1-0498-0800-s008143 | 13 | 2 | 11 | 654.5 |
| line-1-0622-0603-s003000 | 14 | 2 | 12 | 714.0 |
| line-1-0693-0490-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0400-0736-s006691 | 3 | 2 | 1 | 59.5 |
| line-2-0417-0632-s004470 | 8 | 2 | 6 | 357.0 |
| line-2-0435-0527-s002221 | 8 | 2 | 6 | 357.0 |
| line-2-0452-0423-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0301-0356-s009265 | 7 | 2 | 5 | 297.5 |
| line-3-0547-0470-s003013 | 14 | 2 | 12 | 714.0 |
| line-3-0682-0473-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Latakia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
