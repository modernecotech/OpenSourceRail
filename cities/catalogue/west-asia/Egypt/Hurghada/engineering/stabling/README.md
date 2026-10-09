# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 43 at depots = 91 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0533-0545-s014230 | line-1 | declared-depot | 16 | 784.0 | 5 |
| line-2-0729-0464-s000000 | line-2 | declared-depot | 14 | 686.0 | 4 |
| line-3-0460-0535-s000000 | line-3 | declared-depot | 7 | 343.0 | 3 |
| line-4-0451-0431-s000000 | line-4 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0041-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0208-0138-s002396 | station | forward | revenue | 1 |
| line-1 | line-1-0208-0138-s002396 | station | reverse | revenue | 1 |
| line-1 | line-1-0255-0194-s004010 | station | forward | revenue | 1 |
| line-1 | line-1-0255-0194-s004010 | station | reverse | revenue | 1 |
| line-1 | line-1-0300-0249-s005600 | station | forward | revenue | 1 |
| line-1 | line-1-0300-0249-s005600 | station | reverse | revenue | 1 |
| line-1 | line-1-0358-0319-s007645 | station | forward | revenue | 1 |
| line-1 | line-1-0358-0319-s007645 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0372-s009175 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0372-s009175 | station | reverse | revenue | 1 |
| line-1 | line-1-0451-0431-s010901 | station | forward | revenue | 1 |
| line-1 | line-1-0451-0431-s010901 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0472-s012105 | station | forward | revenue | 1 |
| line-1 | line-1-0486-0472-s012105 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0545-s014230 | station | reverse | revenue | 2 |
| line-2 | line-2-0242-0142-s013090 | station | reverse | revenue | 2 |
| line-2 | line-2-0341-0211-s010388 | station | forward | revenue | 1 |
| line-2 | line-2-0341-0211-s010388 | station | reverse | revenue | 1 |
| line-2 | line-2-0400-0252-s008810 | station | forward | revenue | 1 |
| line-2 | line-2-0400-0252-s008810 | station | reverse | revenue | 1 |
| line-2 | line-2-0459-0294-s007200 | station | forward | revenue | 1 |
| line-2 | line-2-0459-0294-s007200 | station | reverse | revenue | 1 |
| line-2 | line-2-0537-0348-s005099 | station | forward | revenue | 1 |
| line-2 | line-2-0537-0348-s005099 | station | reverse | revenue | 1 |
| line-2 | line-2-0639-0414-s002395 | station | forward | revenue | 1 |
| line-2 | line-2-0639-0414-s002395 | station | reverse | revenue | 1 |
| line-2 | line-2-0729-0464-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0460-0535-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0486-0472-s001499 | station | forward | revenue | 1 |
| line-3 | line-3-0486-0472-s001499 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0348-s004425 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0348-s004425 | station | reverse | revenue | 1 |
| line-3 | line-3-0552-0311-s005312 | station | reverse | revenue | 2 |
| line-4 | line-4-0354-0391-s002921 | station | forward | revenue | 1 |
| line-4 | line-4-0354-0391-s002921 | station | reverse | revenue | 1 |
| line-4 | line-4-0358-0319-s004394 | station | forward | revenue | 1 |
| line-4 | line-4-0358-0319-s004394 | station | reverse | revenue | 1 |
| line-4 | line-4-0365-0312-s004592 | station | reverse | revenue | 2 |
| line-4 | line-4-0451-0431-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0533-0545-s014230 | depot | — | revenue | 12 |
| line-1 | line-1-0533-0545-s014230 | depot | — | spare | 3 |
| line-1 | line-1-0533-0545-s014230 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0729-0464-s000000 | depot | — | revenue | 11 |
| line-2 | line-2-0729-0464-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0729-0464-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0460-0535-s000000 | depot | — | revenue | 5 |
| line-3 | line-3-0460-0535-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0460-0535-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0451-0431-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0451-0431-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0451-0431-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hurghada-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **91 trainsets at 24 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **80 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **43 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0155-0041-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0208-0138-s002396 | forward | revenue | 2 | pending |
| line-1 | line-1-0208-0138-s002396 | reverse | revenue | 2 | pending |
| line-1 | line-1-0255-0194-s004010 | forward | revenue | 2 | pending |
| line-1 | line-1-0255-0194-s004010 | reverse | revenue | 2 | pending |
| line-1 | line-1-0300-0249-s005600 | forward | revenue | 2 | pending |
| line-1 | line-1-0300-0249-s005600 | reverse | revenue | 2 | pending |
| line-1 | line-1-0358-0319-s007645 | forward | revenue | 2 | pending |
| line-1 | line-1-0358-0319-s007645 | reverse | revenue | 2 | pending |
| line-1 | line-1-0402-0372-s009175 | forward | revenue | 2 | pending |
| line-1 | line-1-0402-0372-s009175 | reverse | revenue | 2 | pending |
| line-1 | line-1-0451-0431-s010901 | forward | revenue | 2 | pending |
| line-1 | line-1-0451-0431-s010901 | reverse | revenue | 2 | pending |
| line-1 | line-1-0486-0472-s012105 | forward | revenue | 2 | pending |
| line-1 | line-1-0486-0472-s012105 | reverse | revenue | 1 | pending |
| line-1 | line-1-0533-0545-s014230 | reverse | revenue | 1 | pending |
| line-1 | line-1-0486-0472-s012105 | reverse | spare | 1 | pending |
| line-1 | line-1-0533-0545-s014230 | reverse | spare | 1 | pending |
| line-1 | line-1-0155-0041-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0208-0138-s002396 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0729-0464-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0639-0414-s002395 | forward | revenue | 2 | pending |
| line-2 | line-2-0639-0414-s002395 | reverse | revenue | 2 | pending |
| line-2 | line-2-0537-0348-s005099 | forward | revenue | 2 | pending |
| line-2 | line-2-0537-0348-s005099 | reverse | revenue | 2 | pending |
| line-2 | line-2-0459-0294-s007200 | forward | revenue | 2 | pending |
| line-2 | line-2-0459-0294-s007200 | reverse | revenue | 2 | pending |
| line-2 | line-2-0400-0252-s008810 | forward | revenue | 2 | pending |
| line-2 | line-2-0400-0252-s008810 | reverse | revenue | 2 | pending |
| line-2 | line-2-0341-0211-s010388 | forward | revenue | 2 | pending |
| line-2 | line-2-0341-0211-s010388 | reverse | revenue | 2 | pending |
| line-2 | line-2-0242-0142-s013090 | reverse | revenue | 2 | pending |
| line-2 | line-2-0639-0414-s002395 | forward | spare | 1 | pending |
| line-2 | line-2-0639-0414-s002395 | reverse | spare | 1 | pending |
| line-2 | line-2-0537-0348-s005099 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0460-0535-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0486-0472-s001499 | forward | revenue | 2 | pending |
| line-3 | line-3-0486-0472-s001499 | reverse | revenue | 2 | pending |
| line-3 | line-3-0537-0348-s004425 | forward | revenue | 2 | pending |
| line-3 | line-3-0537-0348-s004425 | reverse | revenue | 2 | pending |
| line-3 | line-3-0552-0311-s005312 | reverse | revenue | 2 | pending |
| line-3 | line-3-0486-0472-s001499 | forward | spare | 1 | pending |
| line-3 | line-3-0486-0472-s001499 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0451-0431-s000000 | forward | revenue | 2 | pending |
| line-4 | line-4-0354-0391-s002921 | forward | revenue | 2 | pending |
| line-4 | line-4-0354-0391-s002921 | reverse | revenue | 2 | pending |
| line-4 | line-4-0358-0319-s004394 | forward | revenue | 2 | pending |
| line-4 | line-4-0358-0319-s004394 | reverse | revenue | 2 | pending |
| line-4 | line-4-0365-0312-s004592 | reverse | revenue | 2 | pending |
| line-4 | line-4-0451-0431-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0354-0391-s002921 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0041-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0208-0138-s002396 | 5 | 2 | 3 | 147.0 |
| line-1-0255-0194-s004010 | 4 | 2 | 2 | 98.0 |
| line-1-0300-0249-s005600 | 4 | 2 | 2 | 98.0 |
| line-1-0358-0319-s007645 | 4 | 4 | 0 | 0.0 |
| line-1-0402-0372-s009175 | 4 | 2 | 2 | 98.0 |
| line-1-0451-0431-s010901 | 4 | 4 | 0 | 0.0 |
| line-1-0486-0472-s012105 | 4 | 4 | 0 | 0.0 |
| line-1-0533-0545-s014230 | 2 | 2 | 0 | 0.0 |
| line-2-0242-0142-s013090 | 2 | 2 | 0 | 0.0 |
| line-2-0341-0211-s010388 | 4 | 2 | 2 | 98.0 |
| line-2-0400-0252-s008810 | 4 | 2 | 2 | 98.0 |
| line-2-0459-0294-s007200 | 4 | 2 | 2 | 98.0 |
| line-2-0537-0348-s005099 | 5 | 4 | 1 | 49.0 |
| line-2-0639-0414-s002395 | 6 | 2 | 4 | 196.0 |
| line-2-0729-0464-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0460-0535-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0486-0472-s001499 | 6 | 4 | 2 | 98.0 |
| line-3-0537-0348-s004425 | 4 | 4 | 0 | 0.0 |
| line-3-0552-0311-s005312 | 2 | 2 | 0 | 0.0 |
| line-4-0354-0391-s002921 | 5 | 2 | 3 | 147.0 |
| line-4-0358-0319-s004394 | 4 | 4 | 0 | 0.0 |
| line-4-0365-0312-s004592 | 2 | 2 | 0 | 0.0 |
| line-4-0451-0431-s000000 | 3 | 2 | 1 | 49.0 |

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
