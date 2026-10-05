# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 37 at depots = 59 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0288-0520-s000000 | line-1 | declared-depot | 12 | 588.0 | 3 |
| line-2-0603-0266-s000000 | line-2 | declared-depot | 9 | 441.0 | 3 |
| line-3-0121-0078-s011595 | line-3 | declared-depot | 16 | 784.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0288-0520-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0315-0423-s002175 | station | forward | revenue | 1 |
| line-1 | line-1-0315-0423-s002175 | station | reverse | revenue | 1 |
| line-1 | line-1-0352-0289-s005185 | station | forward | revenue | 1 |
| line-1 | line-1-0352-0289-s005185 | station | reverse | revenue | 1 |
| line-1 | line-1-0371-0112-s009336 | station | reverse | revenue | 2 |
| line-2 | line-2-0431-0513-s006740 | station | reverse | revenue | 2 |
| line-2 | line-2-0523-0381-s003127 | station | forward | revenue | 1 |
| line-2 | line-2-0523-0381-s003127 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0266-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0121-0078-s011595 | station | reverse | revenue | 2 |
| line-3 | line-3-0263-0218-s007314 | station | forward | revenue | 1 |
| line-3 | line-3-0263-0218-s007314 | station | reverse | revenue | 1 |
| line-3 | line-3-0406-0346-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0406-0346-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0506-0435-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0288-0520-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0288-0520-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0288-0520-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0603-0266-s000000 | depot | — | revenue | 7 |
| line-2 | line-2-0603-0266-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0603-0266-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0121-0078-s011595 | depot | — | revenue | 13 |
| line-3 | line-3-0121-0078-s011595 | depot | — | spare | 2 |
| line-3 | line-3-0121-0078-s011595 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/masaka-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **59 trainsets at 11 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **52 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **37 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0288-0520-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0315-0423-s002175 | forward | revenue | 3 | pending |
| line-1 | line-1-0315-0423-s002175 | reverse | revenue | 3 | pending |
| line-1 | line-1-0352-0289-s005185 | forward | revenue | 3 | pending |
| line-1 | line-1-0352-0289-s005185 | reverse | revenue | 3 | pending |
| line-1 | line-1-0371-0112-s009336 | reverse | revenue | 3 | pending |
| line-1 | line-1-0288-0520-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0315-0423-s002175 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0603-0266-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0523-0381-s003127 | forward | revenue | 3 | pending |
| line-2 | line-2-0523-0381-s003127 | reverse | revenue | 3 | pending |
| line-2 | line-2-0431-0513-s006740 | reverse | revenue | 3 | pending |
| line-2 | line-2-0523-0381-s003127 | forward | spare | 1 | pending |
| line-2 | line-2-0523-0381-s003127 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0506-0435-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0406-0346-s003007 | forward | revenue | 4 | pending |
| line-3 | line-3-0406-0346-s003007 | reverse | revenue | 4 | pending |
| line-3 | line-3-0263-0218-s007314 | forward | revenue | 3 | pending |
| line-3 | line-3-0263-0218-s007314 | reverse | revenue | 3 | pending |
| line-3 | line-3-0121-0078-s011595 | reverse | revenue | 3 | pending |
| line-3 | line-3-0263-0218-s007314 | forward | spare | 1 | pending |
| line-3 | line-3-0263-0218-s007314 | reverse | spare | 1 | pending |
| line-3 | line-3-0121-0078-s011595 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**37 trainsets exceed the reference platform envelope**, requiring **1,813.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0288-0520-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0315-0423-s002175 | 7 | 2 | 5 | 245.0 |
| line-1-0352-0289-s005185 | 6 | 2 | 4 | 196.0 |
| line-1-0371-0112-s009336 | 3 | 2 | 1 | 49.0 |
| line-2-0431-0513-s006740 | 3 | 2 | 1 | 49.0 |
| line-2-0523-0381-s003127 | 8 | 2 | 6 | 294.0 |
| line-2-0603-0266-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0121-0078-s011595 | 4 | 2 | 2 | 98.0 |
| line-3-0263-0218-s007314 | 8 | 2 | 6 | 294.0 |
| line-3-0406-0346-s003007 | 8 | 2 | 6 | 294.0 |
| line-3-0506-0435-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Masaka/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
