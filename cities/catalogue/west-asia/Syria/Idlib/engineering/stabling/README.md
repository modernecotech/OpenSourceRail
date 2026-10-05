# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 37 at depots = 59 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0461-0291-s011748 | line-1 | declared-depot | 15 | 735.0 | 4 |
| line-2-0321-0322-s000000 | line-2 | declared-depot | 10 | 490.0 | 3 |
| line-3-0232-0739-s000000 | line-3 | declared-depot | 12 | 588.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0116-0683-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0295-0475-s006248 | station | forward | revenue | 1 |
| line-1 | line-1-0295-0475-s006248 | station | reverse | revenue | 1 |
| line-1 | line-1-0379-0381-s009047 | station | forward | revenue | 1 |
| line-1 | line-1-0379-0381-s009047 | station | reverse | revenue | 1 |
| line-1 | line-1-0417-0339-s010307 | station | forward | revenue | 1 |
| line-1 | line-1-0417-0339-s010307 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0291-s011748 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0322-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0417-0339-s002061 | station | forward | revenue | 1 |
| line-2 | line-2-0417-0339-s002061 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0365-s007954 | station | reverse | revenue | 2 |
| line-3 | line-3-0232-0739-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0295-0475-s006030 | station | forward | revenue | 1 |
| line-3 | line-3-0295-0475-s006030 | station | reverse | revenue | 1 |
| line-3 | line-3-0325-0361-s008582 | station | reverse | revenue | 2 |
| line-1 | line-1-0461-0291-s011748 | depot | — | revenue | 12 |
| line-1 | line-1-0461-0291-s011748 | depot | — | spare | 2 |
| line-1 | line-1-0461-0291-s011748 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0321-0322-s000000 | depot | — | revenue | 8 |
| line-2 | line-2-0321-0322-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0321-0322-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0232-0739-s000000 | depot | — | revenue | 10 |
| line-3 | line-3-0232-0739-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0232-0739-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/idlib-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **59 trainsets at 11 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **52 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **37 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0116-0683-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0295-0475-s006248 | forward | revenue | 3 | pending |
| line-1 | line-1-0295-0475-s006248 | reverse | revenue | 3 | pending |
| line-1 | line-1-0379-0381-s009047 | forward | revenue | 3 | pending |
| line-1 | line-1-0379-0381-s009047 | reverse | revenue | 3 | pending |
| line-1 | line-1-0417-0339-s010307 | forward | revenue | 3 | pending |
| line-1 | line-1-0417-0339-s010307 | reverse | revenue | 2 | pending |
| line-1 | line-1-0461-0291-s011748 | reverse | revenue | 2 | pending |
| line-1 | line-1-0417-0339-s010307 | reverse | spare | 1 | pending |
| line-1 | line-1-0461-0291-s011748 | reverse | spare | 1 | pending |
| line-1 | line-1-0116-0683-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0417-0339-s002061 | forward | revenue | 4 | pending |
| line-2 | line-2-0417-0339-s002061 | reverse | revenue | 3 | pending |
| line-2 | line-2-0690-0365-s007954 | reverse | revenue | 3 | pending |
| line-2 | line-2-0417-0339-s002061 | reverse | spare | 1 | pending |
| line-2 | line-2-0690-0365-s007954 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0232-0739-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0295-0475-s006030 | forward | revenue | 4 | pending |
| line-3 | line-3-0295-0475-s006030 | reverse | revenue | 4 | pending |
| line-3 | line-3-0325-0361-s008582 | reverse | revenue | 4 | pending |
| line-3 | line-3-0232-0739-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0295-0475-s006030 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0116-0683-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0295-0475-s006248 | 6 | 4 | 2 | 98.0 |
| line-1-0379-0381-s009047 | 6 | 2 | 4 | 196.0 |
| line-1-0417-0339-s010307 | 6 | 4 | 2 | 98.0 |
| line-1-0461-0291-s011748 | 3 | 2 | 1 | 49.0 |
| line-2-0321-0322-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0417-0339-s002061 | 8 | 4 | 4 | 196.0 |
| line-2-0690-0365-s007954 | 4 | 2 | 2 | 98.0 |
| line-3-0232-0739-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0295-0475-s006030 | 9 | 4 | 5 | 245.0 |
| line-3-0325-0361-s008582 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Idlib/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
