# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 54 at depots = 88 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0300-0176-s000000 | line-1 | declared-depot | 12 | 588.0 | 3 |
| line-2-0732-0367-s014386 | line-2 | declared-depot | 19 | 931.0 | 4 |
| line-3-0345-0134-s000000 | line-3 | declared-depot | 15 | 735.0 | 4 |
| line-4-0411-0475-s000000 | line-4 | declared-depot | 8 | 392.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0266-0580-s008385 | station | reverse | revenue | 2 |
| line-1 | line-1-0285-0360-s003816 | station | forward | revenue | 1 |
| line-1 | line-1-0285-0360-s003816 | station | reverse | revenue | 1 |
| line-1 | line-1-0300-0176-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0164-0368-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0285-0360-s003109 | station | forward | revenue | 1 |
| line-2 | line-2-0285-0360-s003109 | station | reverse | revenue | 1 |
| line-2 | line-2-0374-0373-s005414 | station | forward | revenue | 1 |
| line-2 | line-2-0374-0373-s005414 | station | reverse | revenue | 1 |
| line-2 | line-2-0539-0385-s009906 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0385-s009906 | station | reverse | revenue | 1 |
| line-2 | line-2-0732-0367-s014386 | station | reverse | revenue | 2 |
| line-3 | line-3-0345-0134-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0374-0375-s005676 | station | forward | revenue | 1 |
| line-3 | line-3-0374-0375-s005676 | station | reverse | revenue | 1 |
| line-3 | line-3-0408-0470-s007996 | station | forward | revenue | 1 |
| line-3 | line-3-0408-0470-s007996 | station | reverse | revenue | 1 |
| line-3 | line-3-0411-0475-s008133 | station | forward | revenue | 1 |
| line-3 | line-3-0411-0475-s008133 | station | reverse | revenue | 1 |
| line-3 | line-3-0471-0564-s011448 | station | reverse | revenue | 2 |
| line-4 | line-4-0371-0561-s003607 | station | forward | revenue | 1 |
| line-4 | line-4-0371-0561-s003607 | station | reverse | revenue | 1 |
| line-4 | line-4-0389-0635-s006350 | station | reverse | revenue | 2 |
| line-4 | line-4-0408-0470-s000165 | station | forward | revenue | 1 |
| line-4 | line-4-0408-0470-s000165 | station | reverse | revenue | 1 |
| line-4 | line-4-0411-0475-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0300-0176-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0300-0176-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0300-0176-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0732-0367-s014386 | depot | — | revenue | 16 |
| line-2 | line-2-0732-0367-s014386 | depot | — | spare | 2 |
| line-2 | line-2-0732-0367-s014386 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0345-0134-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0345-0134-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0345-0134-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0411-0475-s000000 | depot | — | revenue | 6 |
| line-4 | line-4-0411-0475-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0411-0475-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nelspruit-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **88 trainsets at 17 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **78 revenue, 6 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **54 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0300-0176-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0285-0360-s003816 | forward | revenue | 4 | pending |
| line-1 | line-1-0285-0360-s003816 | reverse | revenue | 4 | pending |
| line-1 | line-1-0266-0580-s008385 | reverse | revenue | 4 | pending |
| line-1 | line-1-0300-0176-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0285-0360-s003816 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0164-0368-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0285-0360-s003109 | forward | revenue | 4 | pending |
| line-2 | line-2-0285-0360-s003109 | reverse | revenue | 3 | pending |
| line-2 | line-2-0374-0373-s005414 | forward | revenue | 3 | pending |
| line-2 | line-2-0374-0373-s005414 | reverse | revenue | 3 | pending |
| line-2 | line-2-0539-0385-s009906 | forward | revenue | 3 | pending |
| line-2 | line-2-0539-0385-s009906 | reverse | revenue | 3 | pending |
| line-2 | line-2-0732-0367-s014386 | reverse | revenue | 3 | pending |
| line-2 | line-2-0285-0360-s003109 | reverse | spare | 1 | pending |
| line-2 | line-2-0374-0373-s005414 | forward | spare | 1 | pending |
| line-2 | line-2-0374-0373-s005414 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0345-0134-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0375-s005676 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0375-s005676 | reverse | revenue | 3 | pending |
| line-3 | line-3-0408-0470-s007996 | forward | revenue | 3 | pending |
| line-3 | line-3-0408-0470-s007996 | reverse | revenue | 3 | pending |
| line-3 | line-3-0411-0475-s008133 | forward | revenue | 3 | pending |
| line-3 | line-3-0411-0475-s008133 | reverse | revenue | 2 | pending |
| line-3 | line-3-0471-0564-s011448 | reverse | revenue | 2 | pending |
| line-3 | line-3-0411-0475-s008133 | reverse | spare | 1 | pending |
| line-3 | line-3-0471-0564-s011448 | reverse | spare | 1 | pending |
| line-3 | line-3-0345-0134-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0411-0475-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0408-0470-s000165 | forward | revenue | 3 | pending |
| line-4 | line-4-0408-0470-s000165 | reverse | revenue | 2 | pending |
| line-4 | line-4-0371-0561-s003607 | forward | revenue | 2 | pending |
| line-4 | line-4-0371-0561-s003607 | reverse | revenue | 2 | pending |
| line-4 | line-4-0389-0635-s006350 | reverse | revenue | 2 | pending |
| line-4 | line-4-0408-0470-s000165 | reverse | spare | 1 | pending |
| line-4 | line-4-0371-0561-s003607 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **1,960.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0266-0580-s008385 | 4 | 2 | 2 | 98.0 |
| line-1-0285-0360-s003816 | 9 | 4 | 5 | 245.0 |
| line-1-0300-0176-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0164-0368-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0285-0360-s003109 | 8 | 4 | 4 | 196.0 |
| line-2-0374-0373-s005414 | 8 | 4 | 4 | 196.0 |
| line-2-0539-0385-s009906 | 6 | 2 | 4 | 196.0 |
| line-2-0732-0367-s014386 | 3 | 2 | 1 | 49.0 |
| line-3-0345-0134-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0374-0375-s005676 | 6 | 4 | 2 | 98.0 |
| line-3-0408-0470-s007996 | 6 | 4 | 2 | 98.0 |
| line-3-0411-0475-s008133 | 6 | 4 | 2 | 98.0 |
| line-3-0471-0564-s011448 | 3 | 2 | 1 | 49.0 |
| line-4-0371-0561-s003607 | 5 | 2 | 3 | 147.0 |
| line-4-0389-0635-s006350 | 2 | 2 | 0 | 0.0 |
| line-4-0408-0470-s000165 | 6 | 4 | 2 | 98.0 |
| line-4-0411-0475-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Nelspruit/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
