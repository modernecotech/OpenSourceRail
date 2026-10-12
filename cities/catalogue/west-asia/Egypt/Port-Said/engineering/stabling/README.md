# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 68 at depots = 106 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0524-0309-s011319 | line-1 | declared-depot | 26 | 1,547.0 | 6 |
| line-2-0532-0606-s000000 | line-2 | declared-depot | 13 | 773.5 | 4 |
| line-3-0677-0677-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |
| line-4-0761-0608-s000000 | line-4 | declared-depot | 11 | 654.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0524-0309-s011319 | station | reverse | revenue | 2 |
| line-1 | line-1-0564-0542-s005119 | station | forward | revenue | 1 |
| line-1 | line-1-0564-0542-s005119 | station | reverse | revenue | 1 |
| line-1 | line-1-0581-0499-s006412 | station | forward | revenue | 1 |
| line-1 | line-1-0581-0499-s006412 | station | reverse | revenue | 1 |
| line-1 | line-1-0758-0609-s000177 | station | forward | revenue | 1 |
| line-1 | line-1-0758-0609-s000177 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0608-s000108 | station | forward | revenue | 1 |
| line-1 | line-1-0761-0608-s000108 | station | reverse | revenue | 1 |
| line-1 | line-1-0765-0610-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0532-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0558-0550-s001359 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0550-s001359 | station | reverse | revenue | 1 |
| line-2 | line-2-0559-0547-s001427 | station | forward | revenue | 1 |
| line-2 | line-2-0559-0547-s001427 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0500-s002565 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0500-s002565 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0359-s005985 | station | reverse | revenue | 2 |
| line-3 | line-3-0558-0550-s004032 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0550-s004032 | station | reverse | revenue | 1 |
| line-3 | line-3-0559-0547-s004169 | station | forward | revenue | 1 |
| line-3 | line-3-0559-0547-s004169 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0542-s004417 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0542-s004417 | station | reverse | revenue | 1 |
| line-3 | line-3-0670-0414-s008791 | station | reverse | revenue | 2 |
| line-3 | line-3-0677-0677-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0758-0609-s000125 | station | forward | revenue | 1 |
| line-4 | line-4-0758-0609-s000125 | station | reverse | revenue | 1 |
| line-4 | line-4-0761-0512-s005046 | station | reverse | revenue | 2 |
| line-4 | line-4-0761-0608-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0524-0309-s011319 | depot | — | revenue | 22 |
| line-1 | line-1-0524-0309-s011319 | depot | — | spare | 3 |
| line-1 | line-1-0524-0309-s011319 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0532-0606-s000000 | depot | — | revenue | 10 |
| line-2 | line-2-0532-0606-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0532-0606-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0677-0677-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0677-0677-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0677-0677-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0761-0608-s000000 | depot | — | revenue | 9 |
| line-4 | line-4-0761-0608-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0761-0608-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/port-said-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **106 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **94 revenue, 8 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0765-0610-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0761-0608-s000108 | forward | revenue | 4 | pending |
| line-1 | line-1-0761-0608-s000108 | reverse | revenue | 4 | pending |
| line-1 | line-1-0758-0609-s000177 | forward | revenue | 4 | pending |
| line-1 | line-1-0758-0609-s000177 | reverse | revenue | 3 | pending |
| line-1 | line-1-0564-0542-s005119 | forward | revenue | 3 | pending |
| line-1 | line-1-0564-0542-s005119 | reverse | revenue | 3 | pending |
| line-1 | line-1-0581-0499-s006412 | forward | revenue | 3 | pending |
| line-1 | line-1-0581-0499-s006412 | reverse | revenue | 3 | pending |
| line-1 | line-1-0524-0309-s011319 | reverse | revenue | 3 | pending |
| line-1 | line-1-0758-0609-s000177 | reverse | spare | 1 | pending |
| line-1 | line-1-0564-0542-s005119 | forward | spare | 1 | pending |
| line-1 | line-1-0564-0542-s005119 | reverse | spare | 1 | pending |
| line-1 | line-1-0581-0499-s006412 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0606-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0550-s001359 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0550-s001359 | reverse | revenue | 3 | pending |
| line-2 | line-2-0559-0547-s001427 | forward | revenue | 3 | pending |
| line-2 | line-2-0559-0547-s001427 | reverse | revenue | 2 | pending |
| line-2 | line-2-0580-0500-s002565 | forward | revenue | 2 | pending |
| line-2 | line-2-0580-0500-s002565 | reverse | revenue | 2 | pending |
| line-2 | line-2-0644-0359-s005985 | reverse | revenue | 2 | pending |
| line-2 | line-2-0559-0547-s001427 | reverse | spare | 1 | pending |
| line-2 | line-2-0580-0500-s002565 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0500-s002565 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0677-0677-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0558-0550-s004032 | forward | revenue | 3 | pending |
| line-3 | line-3-0558-0550-s004032 | reverse | revenue | 3 | pending |
| line-3 | line-3-0559-0547-s004169 | forward | revenue | 3 | pending |
| line-3 | line-3-0559-0547-s004169 | reverse | revenue | 3 | pending |
| line-3 | line-3-0567-0542-s004417 | forward | revenue | 3 | pending |
| line-3 | line-3-0567-0542-s004417 | reverse | revenue | 3 | pending |
| line-3 | line-3-0670-0414-s008791 | reverse | revenue | 3 | pending |
| line-3 | line-3-0558-0550-s004032 | forward | spare | 1 | pending |
| line-3 | line-3-0558-0550-s004032 | reverse | spare | 1 | pending |
| line-3 | line-3-0559-0547-s004169 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0761-0608-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0758-0609-s000125 | forward | revenue | 4 | pending |
| line-4 | line-4-0758-0609-s000125 | reverse | revenue | 4 | pending |
| line-4 | line-4-0761-0512-s005046 | reverse | revenue | 3 | pending |
| line-4 | line-4-0761-0512-s005046 | reverse | spare | 1 | pending |
| line-4 | line-4-0761-0608-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**46 trainsets exceed the reference platform envelope**, requiring **2,737.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0524-0309-s011319 | 3 | 2 | 1 | 59.5 |
| line-1-0564-0542-s005119 | 8 | 4 | 4 | 238.0 |
| line-1-0581-0499-s006412 | 7 | 4 | 3 | 178.5 |
| line-1-0758-0609-s000177 | 8 | 4 | 4 | 238.0 |
| line-1-0761-0608-s000108 | 8 | 4 | 4 | 238.0 |
| line-1-0765-0610-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0532-0606-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0558-0550-s001359 | 6 | 4 | 2 | 119.0 |
| line-2-0559-0547-s001427 | 6 | 4 | 2 | 119.0 |
| line-2-0580-0500-s002565 | 6 | 4 | 2 | 119.0 |
| line-2-0644-0359-s005985 | 2 | 2 | 0 | 0.0 |
| line-3-0558-0550-s004032 | 8 | 4 | 4 | 238.0 |
| line-3-0559-0547-s004169 | 7 | 4 | 3 | 178.5 |
| line-3-0567-0542-s004417 | 6 | 4 | 2 | 119.0 |
| line-3-0670-0414-s008791 | 3 | 2 | 1 | 59.5 |
| line-3-0677-0677-s000000 | 4 | 2 | 2 | 119.0 |
| line-4-0758-0609-s000125 | 8 | 4 | 4 | 238.0 |
| line-4-0761-0512-s005046 | 4 | 2 | 2 | 119.0 |
| line-4-0761-0608-s000000 | 5 | 2 | 3 | 178.5 |

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
