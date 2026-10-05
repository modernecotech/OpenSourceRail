# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 103 at depots = 133 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0985-0109-s022386 | line-1 | declared-depot | 61 | 3,629.5 | 10 |
| line-2-0700-0586-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0459-0690-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0147-0558-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0263-0486-s002936 | station | forward | revenue | 1 |
| line-1 | line-1-0263-0486-s002936 | station | reverse | revenue | 1 |
| line-1 | line-1-0394-0436-s006006 | station | forward | revenue | 1 |
| line-1 | line-1-0394-0436-s006006 | station | reverse | revenue | 1 |
| line-1 | line-1-0521-0387-s009010 | station | forward | revenue | 1 |
| line-1 | line-1-0521-0387-s009010 | station | reverse | revenue | 1 |
| line-1 | line-1-0985-0109-s022386 | station | reverse | revenue | 2 |
| line-2 | line-2-0275-0378-s010481 | station | reverse | revenue | 2 |
| line-2 | line-2-0378-0428-s007948 | station | forward | revenue | 1 |
| line-2 | line-2-0378-0428-s007948 | station | reverse | revenue | 1 |
| line-2 | line-2-0480-0478-s005424 | station | forward | revenue | 1 |
| line-2 | line-2-0480-0478-s005424 | station | reverse | revenue | 1 |
| line-2 | line-2-0577-0526-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0526-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0586-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0459-0690-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0468-0543-s003015 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0543-s003015 | station | reverse | revenue | 1 |
| line-3 | line-3-0472-0464-s004639 | station | forward | revenue | 1 |
| line-3 | line-3-0472-0464-s004639 | station | reverse | revenue | 1 |
| line-3 | line-3-0478-0363-s006709 | station | forward | revenue | 1 |
| line-3 | line-3-0478-0363-s006709 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0261-s008799 | station | reverse | revenue | 2 |
| line-1 | line-1-0985-0109-s022386 | depot | — | revenue | 54 |
| line-1 | line-1-0985-0109-s022386 | depot | — | spare | 6 |
| line-1 | line-1-0985-0109-s022386 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0700-0586-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0700-0586-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0700-0586-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0459-0690-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0459-0690-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0459-0690-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/samawah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **133 trainsets at 15 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **119 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **103 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0147-0558-s000000 | forward | revenue | 8 | pending |
| line-1 | line-1-0263-0486-s002936 | forward | revenue | 8 | pending |
| line-1 | line-1-0263-0486-s002936 | reverse | revenue | 8 | pending |
| line-1 | line-1-0394-0436-s006006 | forward | revenue | 8 | pending |
| line-1 | line-1-0394-0436-s006006 | reverse | revenue | 8 | pending |
| line-1 | line-1-0521-0387-s009010 | forward | revenue | 8 | pending |
| line-1 | line-1-0521-0387-s009010 | reverse | revenue | 8 | pending |
| line-1 | line-1-0985-0109-s022386 | reverse | revenue | 8 | pending |
| line-1 | line-1-0147-0558-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0263-0486-s002936 | forward | spare | 1 | pending |
| line-1 | line-1-0263-0486-s002936 | reverse | spare | 1 | pending |
| line-1 | line-1-0394-0436-s006006 | forward | spare | 1 | pending |
| line-1 | line-1-0394-0436-s006006 | reverse | spare | 1 | pending |
| line-1 | line-1-0521-0387-s009010 | forward | spare | 1 | pending |
| line-1 | line-1-0521-0387-s009010 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0586-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0577-0526-s003016 | forward | revenue | 4 | pending |
| line-2 | line-2-0577-0526-s003016 | reverse | revenue | 4 | pending |
| line-2 | line-2-0480-0478-s005424 | forward | revenue | 4 | pending |
| line-2 | line-2-0480-0478-s005424 | reverse | revenue | 4 | pending |
| line-2 | line-2-0378-0428-s007948 | forward | revenue | 4 | pending |
| line-2 | line-2-0378-0428-s007948 | reverse | revenue | 3 | pending |
| line-2 | line-2-0275-0378-s010481 | reverse | revenue | 3 | pending |
| line-2 | line-2-0378-0428-s007948 | reverse | spare | 1 | pending |
| line-2 | line-2-0275-0378-s010481 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0586-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0577-0526-s003016 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0459-0690-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0468-0543-s003015 | forward | revenue | 3 | pending |
| line-3 | line-3-0468-0543-s003015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0472-0464-s004639 | forward | revenue | 3 | pending |
| line-3 | line-3-0472-0464-s004639 | reverse | revenue | 3 | pending |
| line-3 | line-3-0478-0363-s006709 | forward | revenue | 3 | pending |
| line-3 | line-3-0478-0363-s006709 | reverse | revenue | 3 | pending |
| line-3 | line-3-0484-0261-s008799 | reverse | revenue | 3 | pending |
| line-3 | line-3-0468-0543-s003015 | forward | spare | 1 | pending |
| line-3 | line-3-0468-0543-s003015 | reverse | spare | 1 | pending |
| line-3 | line-3-0472-0464-s004639 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0147-0558-s000000 | 9 | 2 | 7 | 416.5 |
| line-1-0263-0486-s002936 | 18 | 2 | 16 | 952.0 |
| line-1-0394-0436-s006006 | 18 | 4 | 14 | 833.0 |
| line-1-0521-0387-s009010 | 18 | 2 | 16 | 952.0 |
| line-1-0985-0109-s022386 | 8 | 2 | 6 | 357.0 |
| line-2-0275-0378-s010481 | 4 | 2 | 2 | 119.0 |
| line-2-0378-0428-s007948 | 8 | 4 | 4 | 238.0 |
| line-2-0480-0478-s005424 | 8 | 4 | 4 | 238.0 |
| line-2-0577-0526-s003016 | 9 | 2 | 7 | 416.5 |
| line-2-0700-0586-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0459-0690-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0468-0543-s003015 | 8 | 2 | 6 | 357.0 |
| line-3-0472-0464-s004639 | 7 | 4 | 3 | 178.5 |
| line-3-0478-0363-s006709 | 6 | 2 | 4 | 238.0 |
| line-3-0484-0261-s008799 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
