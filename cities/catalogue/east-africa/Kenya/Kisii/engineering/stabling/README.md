# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **16 trainsets at stations + 26 at depots = 42 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0433-0474-s000000 | line-1 | declared-depot | 9 | 441.0 | 3 |
| line-2-0226-0282-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0375-0406-s008508 | line-3 | declared-depot | 12 | 588.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0274-0217-s006738 | station | reverse | revenue | 2 |
| line-1 | line-1-0370-0371-s002687 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0371-s002687 | station | reverse | revenue | 1 |
| line-1 | line-1-0433-0474-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0226-0282-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0369-0293-s002951 | station | reverse | revenue | 2 |
| line-3 | line-3-0027-0326-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0253-0355-s005587 | station | forward | revenue | 1 |
| line-3 | line-3-0253-0355-s005587 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0406-s008508 | station | reverse | revenue | 2 |
| line-1 | line-1-0433-0474-s000000 | depot | — | revenue | 7 |
| line-1 | line-1-0433-0474-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0433-0474-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0226-0282-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0226-0282-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0226-0282-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0375-0406-s008508 | depot | — | revenue | 10 |
| line-3 | line-3-0375-0406-s008508 | depot | — | spare | 1 |
| line-3 | line-3-0375-0406-s008508 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kisii-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **42 trainsets at 8 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **36 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **16 positions**; **26 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0433-0474-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0370-0371-s002687 | forward | revenue | 3 | pending |
| line-1 | line-1-0370-0371-s002687 | reverse | revenue | 3 | pending |
| line-1 | line-1-0274-0217-s006738 | reverse | revenue | 3 | pending |
| line-1 | line-1-0370-0371-s002687 | forward | spare | 1 | pending |
| line-1 | line-1-0370-0371-s002687 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0226-0282-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0369-0293-s002951 | reverse | revenue | 3 | pending |
| line-2 | line-2-0369-0293-s002951 | reverse | spare | 1 | pending |
| line-2 | line-2-0226-0282-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0027-0326-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0253-0355-s005587 | forward | revenue | 4 | pending |
| line-3 | line-3-0253-0355-s005587 | reverse | revenue | 4 | pending |
| line-3 | line-3-0375-0406-s008508 | reverse | revenue | 4 | pending |
| line-3 | line-3-0027-0326-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0253-0355-s005587 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**26 trainsets exceed the reference platform envelope**, requiring **1,274.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0274-0217-s006738 | 3 | 2 | 1 | 49.0 |
| line-1-0370-0371-s002687 | 8 | 2 | 6 | 294.0 |
| line-1-0433-0474-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0226-0282-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0369-0293-s002951 | 4 | 2 | 2 | 98.0 |
| line-3-0027-0326-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0253-0355-s005587 | 9 | 2 | 7 | 343.0 |
| line-3-0375-0406-s008508 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisii/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
