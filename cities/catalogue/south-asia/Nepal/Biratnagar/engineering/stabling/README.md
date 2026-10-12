# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 47 at depots = 71 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0059-0424-s013390 | line-1 | declared-depot | 19 | 931.0 | 4 |
| line-2-0547-0484-s000000 | line-2 | declared-depot | 6 | 294.0 | 2 |
| line-3-0439-0080-s000000 | line-3 | declared-depot | 13 | 637.0 | 3 |
| line-4-0371-0125-s000000 | line-4 | declared-depot | 9 | 441.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0059-0424-s013390 | station | reverse | revenue | 2 |
| line-1 | line-1-0171-0406-s010935 | station | forward | revenue | 1 |
| line-1 | line-1-0171-0406-s010935 | station | reverse | revenue | 1 |
| line-1 | line-1-0371-0379-s005999 | station | forward | revenue | 1 |
| line-1 | line-1-0371-0379-s005999 | station | reverse | revenue | 1 |
| line-1 | line-1-0632-0366-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0339-0471-s004279 | station | reverse | revenue | 2 |
| line-2 | line-2-0547-0484-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0242-0424-s010908 | station | reverse | revenue | 2 |
| line-3 | line-3-0370-0377-s007530 | station | forward | revenue | 1 |
| line-3 | line-3-0370-0377-s007530 | station | reverse | revenue | 1 |
| line-3 | line-3-0371-0125-s001733 | station | forward | revenue | 1 |
| line-3 | line-3-0371-0125-s001733 | station | reverse | revenue | 1 |
| line-3 | line-3-0439-0080-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0183-0197-s005738 | station | reverse | revenue | 2 |
| line-4 | line-4-0371-0125-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0059-0424-s013390 | depot | — | revenue | 16 |
| line-1 | line-1-0059-0424-s013390 | depot | — | spare | 2 |
| line-1 | line-1-0059-0424-s013390 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0547-0484-s000000 | depot | — | revenue | 4 |
| line-2 | line-2-0547-0484-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0547-0484-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0439-0080-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0439-0080-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0439-0080-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0371-0125-s000000 | depot | — | revenue | 7 |
| line-4 | line-4-0371-0125-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0371-0125-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/biratnagar-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **71 trainsets at 12 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **62 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **47 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0632-0366-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0371-0379-s005999 | forward | revenue | 4 | pending |
| line-1 | line-1-0371-0379-s005999 | reverse | revenue | 4 | pending |
| line-1 | line-1-0171-0406-s010935 | forward | revenue | 4 | pending |
| line-1 | line-1-0171-0406-s010935 | reverse | revenue | 4 | pending |
| line-1 | line-1-0059-0424-s013390 | reverse | revenue | 4 | pending |
| line-1 | line-1-0632-0366-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0371-0379-s005999 | forward | spare | 1 | pending |
| line-1 | line-1-0371-0379-s005999 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0547-0484-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0339-0471-s004279 | reverse | revenue | 4 | pending |
| line-2 | line-2-0547-0484-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0339-0471-s004279 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0439-0080-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0371-0125-s001733 | forward | revenue | 3 | pending |
| line-3 | line-3-0371-0125-s001733 | reverse | revenue | 3 | pending |
| line-3 | line-3-0370-0377-s007530 | forward | revenue | 3 | pending |
| line-3 | line-3-0370-0377-s007530 | reverse | revenue | 3 | pending |
| line-3 | line-3-0242-0424-s010908 | reverse | revenue | 3 | pending |
| line-3 | line-3-0371-0125-s001733 | forward | spare | 1 | pending |
| line-3 | line-3-0371-0125-s001733 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0371-0125-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0183-0197-s005738 | reverse | revenue | 5 | pending |
| line-4 | line-4-0183-0197-s005738 | reverse | spare | 1 | pending |
| line-4 | line-4-0371-0125-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,009.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0059-0424-s013390 | 4 | 2 | 2 | 98.0 |
| line-1-0171-0406-s010935 | 8 | 2 | 6 | 294.0 |
| line-1-0371-0379-s005999 | 10 | 4 | 6 | 294.0 |
| line-1-0632-0366-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0339-0471-s004279 | 5 | 2 | 3 | 147.0 |
| line-2-0547-0484-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0242-0424-s010908 | 3 | 2 | 1 | 49.0 |
| line-3-0370-0377-s007530 | 6 | 4 | 2 | 98.0 |
| line-3-0371-0125-s001733 | 8 | 4 | 4 | 196.0 |
| line-3-0439-0080-s000000 | 4 | 2 | 2 | 98.0 |
| line-4-0183-0197-s005738 | 6 | 2 | 4 | 196.0 |
| line-4-0371-0125-s000000 | 7 | 2 | 5 | 245.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Biratnagar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
