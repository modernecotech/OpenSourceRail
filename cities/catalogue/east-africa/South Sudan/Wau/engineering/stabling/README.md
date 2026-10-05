# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **20 trainsets at stations + 20 at depots = 40 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0486-0395-s006627 | line-1 | declared-depot | 8 | 392.0 | 2 |
| line-2-0075-0290-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |
| line-3-0368-0370-s000000 | line-3 | declared-depot | 4 | 196.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0239-0231-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0351-0306-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0351-0306-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0395-s006627 | station | reverse | revenue | 2 |
| line-2 | line-2-0075-0290-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0237-0326-s003618 | station | forward | revenue | 1 |
| line-2 | line-2-0237-0326-s003618 | station | reverse | revenue | 1 |
| line-2 | line-2-0339-0344-s005807 | station | forward | revenue | 1 |
| line-2 | line-2-0339-0344-s005807 | station | reverse | revenue | 1 |
| line-2 | line-2-0376-0351-s006605 | station | reverse | revenue | 2 |
| line-3 | line-3-0301-0309-s002033 | station | reverse | revenue | 2 |
| line-3 | line-3-0339-0344-s000877 | station | forward | revenue | 1 |
| line-3 | line-3-0339-0344-s000877 | station | reverse | revenue | 1 |
| line-3 | line-3-0368-0370-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0486-0395-s006627 | depot | — | revenue | 6 |
| line-1 | line-1-0486-0395-s006627 | depot | — | spare | 1 |
| line-1 | line-1-0486-0395-s006627 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0075-0290-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0075-0290-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0075-0290-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0368-0370-s000000 | depot | — | revenue | 2 |
| line-3 | line-3-0368-0370-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0368-0370-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/waw-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **40 trainsets at 10 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **34 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **20 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0239-0231-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0351-0306-s003014 | forward | revenue | 3 | pending |
| line-1 | line-1-0351-0306-s003014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0486-0395-s006627 | reverse | revenue | 3 | pending |
| line-1 | line-1-0239-0231-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0351-0306-s003014 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0075-0290-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0237-0326-s003618 | forward | revenue | 3 | pending |
| line-2 | line-2-0237-0326-s003618 | reverse | revenue | 2 | pending |
| line-2 | line-2-0339-0344-s005807 | forward | revenue | 2 | pending |
| line-2 | line-2-0339-0344-s005807 | reverse | revenue | 2 | pending |
| line-2 | line-2-0376-0351-s006605 | reverse | revenue | 2 | pending |
| line-2 | line-2-0237-0326-s003618 | reverse | spare | 1 | pending |
| line-2 | line-2-0339-0344-s005807 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0368-0370-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0339-0344-s000877 | forward | revenue | 2 | pending |
| line-3 | line-3-0339-0344-s000877 | reverse | revenue | 2 | pending |
| line-3 | line-3-0301-0309-s002033 | reverse | revenue | 2 | pending |
| line-3 | line-3-0368-0370-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0339-0344-s000877 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**16 trainsets exceed the reference platform envelope**, requiring **784.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0239-0231-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0351-0306-s003014 | 7 | 2 | 5 | 245.0 |
| line-1-0486-0395-s006627 | 3 | 2 | 1 | 49.0 |
| line-2-0075-0290-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0237-0326-s003618 | 6 | 2 | 4 | 196.0 |
| line-2-0339-0344-s005807 | 5 | 4 | 1 | 49.0 |
| line-2-0376-0351-s006605 | 2 | 2 | 0 | 0.0 |
| line-3-0301-0309-s002033 | 2 | 2 | 0 | 0.0 |
| line-3-0339-0344-s000877 | 5 | 4 | 1 | 49.0 |
| line-3-0368-0370-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/South Sudan/Wau/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
