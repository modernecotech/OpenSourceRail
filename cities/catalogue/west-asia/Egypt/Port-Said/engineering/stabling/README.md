# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **20 trainsets at stations + 45 at depots = 65 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0524-0309-s008697 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0532-0606-s000000 | line-2 | declared-depot | 14 | 833.0 | 3 |
| line-3-0684-0677-s000000 | line-3 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0524-0309-s008697 | station | reverse | revenue | 2 |
| line-1 | line-1-0600-0402-s006020 | station | forward | revenue | 1 |
| line-1 | line-1-0600-0402-s006020 | station | reverse | revenue | 1 |
| line-1 | line-1-0683-0505-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0683-0505-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0768-0610-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0532-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0580-0500-s002565 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0500-s002565 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0359-s005985 | station | reverse | revenue | 2 |
| line-3 | line-3-0670-0414-s005376 | station | reverse | revenue | 2 |
| line-3 | line-3-0676-0530-s003006 | station | forward | revenue | 1 |
| line-3 | line-3-0676-0530-s003006 | station | reverse | revenue | 1 |
| line-3 | line-3-0684-0677-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0524-0309-s008697 | depot | — | revenue | 16 |
| line-1 | line-1-0524-0309-s008697 | depot | — | spare | 2 |
| line-1 | line-1-0524-0309-s008697 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0532-0606-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0532-0606-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0532-0606-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0684-0677-s000000 | depot | — | revenue | 10 |
| line-3 | line-3-0684-0677-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0684-0677-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/port-said-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **65 trainsets at 10 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **58 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **45 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0768-0610-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0683-0505-s003015 | forward | revenue | 4 | pending |
| line-1 | line-1-0683-0505-s003015 | reverse | revenue | 4 | pending |
| line-1 | line-1-0600-0402-s006020 | forward | revenue | 4 | pending |
| line-1 | line-1-0600-0402-s006020 | reverse | revenue | 4 | pending |
| line-1 | line-1-0524-0309-s008697 | reverse | revenue | 4 | pending |
| line-1 | line-1-0768-0610-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0683-0505-s003015 | forward | spare | 1 | pending |
| line-1 | line-1-0683-0505-s003015 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0606-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0580-0500-s002565 | forward | revenue | 5 | pending |
| line-2 | line-2-0580-0500-s002565 | reverse | revenue | 4 | pending |
| line-2 | line-2-0644-0359-s005985 | reverse | revenue | 4 | pending |
| line-2 | line-2-0580-0500-s002565 | reverse | spare | 1 | pending |
| line-2 | line-2-0644-0359-s005985 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0684-0677-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0676-0530-s003006 | forward | revenue | 4 | pending |
| line-3 | line-3-0676-0530-s003006 | reverse | revenue | 4 | pending |
| line-3 | line-3-0670-0414-s005376 | reverse | revenue | 4 | pending |
| line-3 | line-3-0684-0677-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0676-0530-s003006 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,439.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0524-0309-s008697 | 4 | 2 | 2 | 119.0 |
| line-1-0600-0402-s006020 | 8 | 2 | 6 | 357.0 |
| line-1-0683-0505-s003015 | 10 | 4 | 6 | 357.0 |
| line-1-0768-0610-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0532-0606-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0580-0500-s002565 | 10 | 2 | 8 | 476.0 |
| line-2-0644-0359-s005985 | 5 | 2 | 3 | 178.5 |
| line-3-0670-0414-s005376 | 4 | 2 | 2 | 119.0 |
| line-3-0676-0530-s003006 | 9 | 4 | 5 | 297.5 |
| line-3-0684-0677-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Port-Said/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
