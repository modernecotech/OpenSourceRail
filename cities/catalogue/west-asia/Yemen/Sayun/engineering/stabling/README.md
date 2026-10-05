# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 27 at depots = 49 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0491-0047-s013053 | line-1 | declared-depot | 16 | 784.0 | 4 |
| line-2-0465-0310-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0454-0403-s000000 | line-3 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0273-0600-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0320-0468-s003065 | station | forward | revenue | 1 |
| line-1 | line-1-0320-0468-s003065 | station | reverse | revenue | 1 |
| line-1 | line-1-0350-0387-s004945 | station | forward | revenue | 1 |
| line-1 | line-1-0350-0387-s004945 | station | reverse | revenue | 1 |
| line-1 | line-1-0378-0309-s006737 | station | forward | revenue | 1 |
| line-1 | line-1-0378-0309-s006737 | station | reverse | revenue | 1 |
| line-1 | line-1-0491-0047-s013053 | station | reverse | revenue | 2 |
| line-2 | line-2-0283-0307-s003677 | station | reverse | revenue | 2 |
| line-2 | line-2-0378-0309-s001748 | station | forward | revenue | 1 |
| line-2 | line-2-0378-0309-s001748 | station | reverse | revenue | 1 |
| line-2 | line-2-0465-0310-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0258-0373-s004169 | station | reverse | revenue | 2 |
| line-3 | line-3-0350-0387-s002213 | station | forward | revenue | 1 |
| line-3 | line-3-0350-0387-s002213 | station | reverse | revenue | 1 |
| line-3 | line-3-0454-0403-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0491-0047-s013053 | depot | — | revenue | 13 |
| line-1 | line-1-0491-0047-s013053 | depot | — | spare | 2 |
| line-1 | line-1-0491-0047-s013053 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0465-0310-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0465-0310-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0465-0310-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0454-0403-s000000 | depot | — | revenue | 4 |
| line-3 | line-3-0454-0403-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0454-0403-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sayun-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **49 trainsets at 11 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **42 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **27 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0273-0600-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0320-0468-s003065 | forward | revenue | 3 | pending |
| line-1 | line-1-0320-0468-s003065 | reverse | revenue | 3 | pending |
| line-1 | line-1-0350-0387-s004945 | forward | revenue | 3 | pending |
| line-1 | line-1-0350-0387-s004945 | reverse | revenue | 3 | pending |
| line-1 | line-1-0378-0309-s006737 | forward | revenue | 3 | pending |
| line-1 | line-1-0378-0309-s006737 | reverse | revenue | 3 | pending |
| line-1 | line-1-0491-0047-s013053 | reverse | revenue | 2 | pending |
| line-1 | line-1-0491-0047-s013053 | reverse | spare | 1 | pending |
| line-1 | line-1-0273-0600-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0320-0468-s003065 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0465-0310-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0378-0309-s001748 | forward | revenue | 2 | pending |
| line-2 | line-2-0378-0309-s001748 | reverse | revenue | 2 | pending |
| line-2 | line-2-0283-0307-s003677 | reverse | revenue | 2 | pending |
| line-2 | line-2-0378-0309-s001748 | forward | spare | 1 | pending |
| line-2 | line-2-0378-0309-s001748 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0454-0403-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0350-0387-s002213 | forward | revenue | 3 | pending |
| line-3 | line-3-0350-0387-s002213 | reverse | revenue | 2 | pending |
| line-3 | line-3-0258-0373-s004169 | reverse | revenue | 2 | pending |
| line-3 | line-3-0350-0387-s002213 | reverse | spare | 1 | pending |
| line-3 | line-3-0258-0373-s004169 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**19 trainsets exceed the reference platform envelope**, requiring **931.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0273-0600-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0320-0468-s003065 | 7 | 2 | 5 | 245.0 |
| line-1-0350-0387-s004945 | 6 | 4 | 2 | 98.0 |
| line-1-0378-0309-s006737 | 6 | 4 | 2 | 98.0 |
| line-1-0491-0047-s013053 | 3 | 2 | 1 | 49.0 |
| line-2-0283-0307-s003677 | 2 | 2 | 0 | 0.0 |
| line-2-0378-0309-s001748 | 6 | 4 | 2 | 98.0 |
| line-2-0465-0310-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0258-0373-s004169 | 3 | 2 | 1 | 49.0 |
| line-3-0350-0387-s002213 | 6 | 4 | 2 | 98.0 |
| line-3-0454-0403-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Sayun/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
