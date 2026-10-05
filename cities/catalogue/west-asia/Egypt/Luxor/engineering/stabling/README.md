# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 113 at depots = 139 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0268-0383-s000000 | line-1 | declared-depot | 26 | 1,547.0 | 5 |
| line-2-0324-0669-s021837 | line-2 | declared-depot | 56 | 3,332.0 | 10 |
| line-3-0621-0862-s000000 | line-3 | declared-depot | 31 | 1,844.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0268-0383-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0549-0474-s006421 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0474-s006421 | station | reverse | revenue | 1 |
| line-1 | line-1-0712-0526-s010123 | station | reverse | revenue | 2 |
| line-2 | line-2-0324-0669-s021837 | station | reverse | revenue | 2 |
| line-2 | line-2-0427-0582-s018810 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0582-s018810 | station | reverse | revenue | 1 |
| line-2 | line-2-0490-0539-s017147 | station | forward | revenue | 1 |
| line-2 | line-2-0490-0539-s017147 | station | reverse | revenue | 1 |
| line-2 | line-2-0549-0474-s013425 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0474-s013425 | station | reverse | revenue | 1 |
| line-2 | line-2-0596-0439-s011670 | station | forward | revenue | 1 |
| line-2 | line-2-0596-0439-s011670 | station | reverse | revenue | 1 |
| line-2 | line-2-0953-0093-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0300-0398-s012607 | station | reverse | revenue | 2 |
| line-3 | line-3-0427-0582-s007594 | station | forward | revenue | 1 |
| line-3 | line-3-0427-0582-s007594 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0663-s005408 | station | forward | revenue | 1 |
| line-3 | line-3-0484-0663-s005408 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0862-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0268-0383-s000000 | depot | — | revenue | 23 |
| line-1 | line-1-0268-0383-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0268-0383-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0324-0669-s021837 | depot | — | revenue | 49 |
| line-2 | line-2-0324-0669-s021837 | depot | — | spare | 6 |
| line-2 | line-2-0324-0669-s021837 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0621-0862-s000000 | depot | — | revenue | 27 |
| line-3 | line-3-0621-0862-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0621-0862-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/luxor-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **139 trainsets at 13 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **125 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **113 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0268-0383-s000000 | forward | revenue | 8 | pending |
| line-1 | line-1-0549-0474-s006421 | forward | revenue | 7 | pending |
| line-1 | line-1-0549-0474-s006421 | reverse | revenue | 7 | pending |
| line-1 | line-1-0712-0526-s010123 | reverse | revenue | 7 | pending |
| line-1 | line-1-0549-0474-s006421 | forward | spare | 1 | pending |
| line-1 | line-1-0549-0474-s006421 | reverse | spare | 1 | pending |
| line-1 | line-1-0712-0526-s010123 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0953-0093-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0596-0439-s011670 | forward | revenue | 6 | pending |
| line-2 | line-2-0596-0439-s011670 | reverse | revenue | 6 | pending |
| line-2 | line-2-0549-0474-s013425 | forward | revenue | 6 | pending |
| line-2 | line-2-0549-0474-s013425 | reverse | revenue | 6 | pending |
| line-2 | line-2-0490-0539-s017147 | forward | revenue | 6 | pending |
| line-2 | line-2-0490-0539-s017147 | reverse | revenue | 6 | pending |
| line-2 | line-2-0427-0582-s018810 | forward | revenue | 6 | pending |
| line-2 | line-2-0427-0582-s018810 | reverse | revenue | 6 | pending |
| line-2 | line-2-0324-0669-s021837 | reverse | revenue | 6 | pending |
| line-2 | line-2-0596-0439-s011670 | forward | spare | 1 | pending |
| line-2 | line-2-0596-0439-s011670 | reverse | spare | 1 | pending |
| line-2 | line-2-0549-0474-s013425 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0474-s013425 | reverse | spare | 1 | pending |
| line-2 | line-2-0490-0539-s017147 | forward | spare | 1 | pending |
| line-2 | line-2-0490-0539-s017147 | reverse | spare | 1 | pending |
| line-2 | line-2-0427-0582-s018810 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0484-0663-s005408 | forward | revenue | 6 | pending |
| line-3 | line-3-0484-0663-s005408 | reverse | revenue | 6 | pending |
| line-3 | line-3-0427-0582-s007594 | forward | revenue | 6 | pending |
| line-3 | line-3-0427-0582-s007594 | reverse | revenue | 6 | pending |
| line-3 | line-3-0300-0398-s012607 | reverse | revenue | 5 | pending |
| line-3 | line-3-0300-0398-s012607 | reverse | spare | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0484-0663-s005408 | forward | spare | 1 | pending |
| line-3 | line-3-0484-0663-s005408 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**105 trainsets exceed the reference platform envelope**, requiring **6,247.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0268-0383-s000000 | 8 | 2 | 6 | 357.0 |
| line-1-0549-0474-s006421 | 16 | 4 | 12 | 714.0 |
| line-1-0712-0526-s010123 | 8 | 2 | 6 | 357.0 |
| line-2-0324-0669-s021837 | 6 | 2 | 4 | 238.0 |
| line-2-0427-0582-s018810 | 13 | 4 | 9 | 535.5 |
| line-2-0490-0539-s017147 | 14 | 2 | 12 | 714.0 |
| line-2-0549-0474-s013425 | 14 | 4 | 10 | 595.0 |
| line-2-0596-0439-s011670 | 14 | 2 | 12 | 714.0 |
| line-2-0953-0093-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0300-0398-s012607 | 6 | 2 | 4 | 238.0 |
| line-3-0427-0582-s007594 | 12 | 4 | 8 | 476.0 |
| line-3-0484-0663-s005408 | 14 | 2 | 12 | 714.0 |
| line-3-0621-0862-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Luxor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
