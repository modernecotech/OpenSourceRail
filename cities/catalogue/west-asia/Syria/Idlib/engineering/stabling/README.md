# Station and depot overnight allocation

Plan: **22 trainsets at stations + 45 at depots = 67 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0461-0291-s012357 | line-1 | declared-depot | 18 | 882.0 | 11 |
| line-2-0690-0365-s008858 | line-2 | storage-at-existing-powered-service-point | 12 | 588.0 | 0 |
| line-3-0325-0361-s010737 | line-3 | storage-at-existing-powered-service-point | 15 | 735.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0116-0683-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0322-0465-s007014 | station | forward | revenue | 1 |
| line-1 | line-1-0322-0465-s007014 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0378-s009327 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0378-s009327 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0291-s012357 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0322-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0373-0378-s002122 | station | forward | revenue | 1 |
| line-2 | line-2-0373-0378-s002122 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0365-s008858 | station | reverse | revenue | 2 |
| line-3 | line-3-0232-0739-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0325-0361-s010737 | station | reverse | revenue | 2 |
| line-3 | line-3-0373-0378-s009232 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0378-s009232 | station | reverse | revenue | 1 |
| line-3 | line-3-0381-0471-s007008 | station | forward | revenue | 1 |
| line-3 | line-3-0381-0471-s007008 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0291-s012357 | depot | — | revenue | 15 |
| line-1 | line-1-0461-0291-s012357 | depot | — | spare | 2 |
| line-1 | line-1-0461-0291-s012357 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0690-0365-s008858 | depot | — | revenue | 10 |
| line-2 | line-2-0690-0365-s008858 | depot | — | spare | 1 |
| line-2 | line-2-0690-0365-s008858 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0325-0361-s010737 | depot | — | revenue | 12 |
| line-3 | line-3-0325-0361-s010737 | depot | — | spare | 2 |
| line-3 | line-3-0325-0361-s010737 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/idlib-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **67 trainsets at 11 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **59 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **45 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0116-0683-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0322-0465-s007014 | forward | revenue | 4 | pending |
| line-1 | line-1-0322-0465-s007014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0373-0378-s009327 | forward | revenue | 4 | pending |
| line-1 | line-1-0373-0378-s009327 | reverse | revenue | 4 | pending |
| line-1 | line-1-0461-0291-s012357 | reverse | revenue | 3 | pending |
| line-1 | line-1-0461-0291-s012357 | reverse | spare | 1 | pending |
| line-1 | line-1-0116-0683-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0322-0465-s007014 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0373-0378-s002122 | forward | revenue | 4 | pending |
| line-2 | line-2-0373-0378-s002122 | reverse | revenue | 4 | pending |
| line-2 | line-2-0690-0365-s008858 | reverse | revenue | 4 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0373-0378-s002122 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0232-0739-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0381-0471-s007008 | forward | revenue | 4 | pending |
| line-3 | line-3-0381-0471-s007008 | reverse | revenue | 3 | pending |
| line-3 | line-3-0373-0378-s009232 | forward | revenue | 3 | pending |
| line-3 | line-3-0373-0378-s009232 | reverse | revenue | 3 | pending |
| line-3 | line-3-0325-0361-s010737 | reverse | revenue | 3 | pending |
| line-3 | line-3-0381-0471-s007008 | reverse | spare | 1 | pending |
| line-3 | line-3-0373-0378-s009232 | forward | spare | 1 | pending |
| line-3 | line-3-0373-0378-s009232 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **1,911.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0116-0683-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0322-0465-s007014 | 9 | 2 | 7 | 343.0 |
| line-1-0373-0378-s009327 | 8 | 4 | 4 | 196.0 |
| line-1-0461-0291-s012357 | 4 | 2 | 2 | 98.0 |
| line-2-0321-0322-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0373-0378-s002122 | 9 | 4 | 5 | 245.0 |
| line-2-0690-0365-s008858 | 4 | 2 | 2 | 98.0 |
| line-3-0232-0739-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0325-0361-s010737 | 3 | 2 | 1 | 49.0 |
| line-3-0373-0378-s009232 | 8 | 4 | 4 | 196.0 |
| line-3-0381-0471-s007008 | 8 | 2 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Idlib/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
