# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 38 at depots = 72 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0533-0545-s014230 | line-1 | declared-depot | 18 | 882.0 | 5 |
| line-2-0729-0464-s000000 | line-2 | declared-depot | 14 | 686.0 | 4 |
| line-3-0460-0535-s000000 | line-3 | declared-depot | 6 | 294.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0041-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0227-0160-s003016 | station | forward | revenue | 1 |
| line-1 | line-1-0227-0160-s003016 | station | reverse | revenue | 1 |
| line-1 | line-1-0313-0264-s006043 | station | forward | revenue | 1 |
| line-1 | line-1-0313-0264-s006043 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0372-s009175 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0372-s009175 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0472-s012105 | station | forward | revenue | 1 |
| line-1 | line-1-0486-0472-s012105 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0545-s014230 | station | reverse | revenue | 2 |
| line-2 | line-2-0242-0142-s013090 | station | reverse | revenue | 2 |
| line-2 | line-2-0391-0246-s009051 | station | forward | revenue | 1 |
| line-2 | line-2-0391-0246-s009051 | station | reverse | revenue | 1 |
| line-2 | line-2-0464-0297-s007075 | station | forward | revenue | 1 |
| line-2 | line-2-0464-0297-s007075 | station | reverse | revenue | 1 |
| line-2 | line-2-0537-0348-s005099 | station | forward | revenue | 1 |
| line-2 | line-2-0537-0348-s005099 | station | reverse | revenue | 1 |
| line-2 | line-2-0613-0402-s003026 | station | forward | revenue | 1 |
| line-2 | line-2-0613-0402-s003026 | station | reverse | revenue | 1 |
| line-2 | line-2-0729-0464-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0460-0535-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0486-0472-s001499 | station | forward | revenue | 1 |
| line-3 | line-3-0486-0472-s001499 | station | reverse | revenue | 1 |
| line-3 | line-3-0512-0408-s003006 | station | forward | revenue | 1 |
| line-3 | line-3-0512-0408-s003006 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0348-s004425 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0348-s004425 | station | reverse | revenue | 1 |
| line-3 | line-3-0552-0311-s005312 | station | reverse | revenue | 2 |
| line-1 | line-1-0533-0545-s014230 | depot | — | revenue | 15 |
| line-1 | line-1-0533-0545-s014230 | depot | — | spare | 2 |
| line-1 | line-1-0533-0545-s014230 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0729-0464-s000000 | depot | — | revenue | 11 |
| line-2 | line-2-0729-0464-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0729-0464-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0460-0535-s000000 | depot | — | revenue | 4 |
| line-3 | line-3-0460-0535-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0460-0535-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hurghada-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **72 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **64 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **38 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0155-0041-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0227-0160-s003016 | forward | revenue | 3 | pending |
| line-1 | line-1-0227-0160-s003016 | reverse | revenue | 3 | pending |
| line-1 | line-1-0313-0264-s006043 | forward | revenue | 3 | pending |
| line-1 | line-1-0313-0264-s006043 | reverse | revenue | 3 | pending |
| line-1 | line-1-0402-0372-s009175 | forward | revenue | 3 | pending |
| line-1 | line-1-0402-0372-s009175 | reverse | revenue | 3 | pending |
| line-1 | line-1-0486-0472-s012105 | forward | revenue | 2 | pending |
| line-1 | line-1-0486-0472-s012105 | reverse | revenue | 2 | pending |
| line-1 | line-1-0533-0545-s014230 | reverse | revenue | 2 | pending |
| line-1 | line-1-0486-0472-s012105 | forward | spare | 1 | pending |
| line-1 | line-1-0486-0472-s012105 | reverse | spare | 1 | pending |
| line-1 | line-1-0533-0545-s014230 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0729-0464-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0613-0402-s003026 | forward | revenue | 3 | pending |
| line-2 | line-2-0613-0402-s003026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0537-0348-s005099 | forward | revenue | 2 | pending |
| line-2 | line-2-0537-0348-s005099 | reverse | revenue | 2 | pending |
| line-2 | line-2-0464-0297-s007075 | forward | revenue | 2 | pending |
| line-2 | line-2-0464-0297-s007075 | reverse | revenue | 2 | pending |
| line-2 | line-2-0391-0246-s009051 | forward | revenue | 2 | pending |
| line-2 | line-2-0391-0246-s009051 | reverse | revenue | 2 | pending |
| line-2 | line-2-0242-0142-s013090 | reverse | revenue | 2 | pending |
| line-2 | line-2-0537-0348-s005099 | forward | spare | 1 | pending |
| line-2 | line-2-0537-0348-s005099 | reverse | spare | 1 | pending |
| line-2 | line-2-0464-0297-s007075 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0460-0535-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0486-0472-s001499 | forward | revenue | 2 | pending |
| line-3 | line-3-0486-0472-s001499 | reverse | revenue | 2 | pending |
| line-3 | line-3-0512-0408-s003006 | forward | revenue | 2 | pending |
| line-3 | line-3-0512-0408-s003006 | reverse | revenue | 2 | pending |
| line-3 | line-3-0537-0348-s004425 | forward | revenue | 2 | pending |
| line-3 | line-3-0537-0348-s004425 | reverse | revenue | 1 | pending |
| line-3 | line-3-0552-0311-s005312 | reverse | revenue | 1 | pending |
| line-3 | line-3-0537-0348-s004425 | reverse | spare | 1 | pending |
| line-3 | line-3-0552-0311-s005312 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,372.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0041-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0227-0160-s003016 | 6 | 4 | 2 | 98.0 |
| line-1-0313-0264-s006043 | 6 | 2 | 4 | 196.0 |
| line-1-0402-0372-s009175 | 6 | 2 | 4 | 196.0 |
| line-1-0486-0472-s012105 | 6 | 4 | 2 | 98.0 |
| line-1-0533-0545-s014230 | 3 | 2 | 1 | 49.0 |
| line-2-0242-0142-s013090 | 2 | 2 | 0 | 0.0 |
| line-2-0391-0246-s009051 | 4 | 2 | 2 | 98.0 |
| line-2-0464-0297-s007075 | 5 | 2 | 3 | 147.0 |
| line-2-0537-0348-s005099 | 6 | 4 | 2 | 98.0 |
| line-2-0613-0402-s003026 | 6 | 2 | 4 | 196.0 |
| line-2-0729-0464-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0460-0535-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0486-0472-s001499 | 4 | 4 | 0 | 0.0 |
| line-3-0512-0408-s003006 | 4 | 2 | 2 | 98.0 |
| line-3-0537-0348-s004425 | 4 | 4 | 0 | 0.0 |
| line-3-0552-0311-s005312 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Hurghada/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
