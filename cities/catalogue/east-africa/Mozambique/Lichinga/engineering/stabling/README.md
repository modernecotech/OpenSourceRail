# Station and depot overnight allocation

Plan: **16 trainsets at stations + 18 at depots = 34 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0373-0475-s008726 | 18 | 882.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0159-0472-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0287-0456-s003007 | station | forward | revenue | 1 |
| line-1 | line-1-0287-0456-s003007 | station | reverse | revenue | 1 |
| line-1 | line-1-0324-0406-s004685 | station | forward | revenue | 1 |
| line-1 | line-1-0324-0406-s004685 | station | reverse | revenue | 1 |
| line-1 | line-1-0367-0381-s006109 | station | forward | revenue | 1 |
| line-1 | line-1-0367-0381-s006109 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0475-s008726 | station | reverse | revenue | 2 |
| line-2 | line-2-0227-0358-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0306-0456-s006213 | station | reverse | revenue | 2 |
| line-2 | line-2-0367-0381-s003742 | station | forward | revenue | 1 |
| line-2 | line-2-0367-0381-s003742 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0475-s008726 | depot | — | revenue | 8 |
| line-1 | line-1-0373-0475-s008726 | depot | — | spare | 1 |
| line-1 | line-1-0373-0475-s008726 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0373-0475-s008726 | depot | — | revenue | 6 |
| line-2 | line-1-0373-0475-s008726 | depot | — | spare | 1 |
| line-2 | line-1-0373-0475-s008726 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (8 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **34 trainsets at 8 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **30 revenue, 2 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **16 positions**; **18 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **7 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0159-0472-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0287-0456-s003007 | forward | revenue | 3 | pending |
| line-1 | line-1-0287-0456-s003007 | reverse | revenue | 2 | pending |
| line-1 | line-1-0324-0406-s004685 | forward | revenue | 2 | pending |
| line-1 | line-1-0324-0406-s004685 | reverse | revenue | 2 | pending |
| line-1 | line-1-0367-0381-s006109 | forward | revenue | 2 | pending |
| line-1 | line-1-0367-0381-s006109 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0475-s008726 | reverse | revenue | 2 | pending |
| line-1 | line-1-0287-0456-s003007 | reverse | spare | 1 | pending |
| line-1 | line-1-0324-0406-s004685 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0227-0358-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0367-0381-s003742 | forward | revenue | 3 | pending |
| line-2 | line-2-0367-0381-s003742 | reverse | revenue | 3 | pending |
| line-2 | line-2-0306-0456-s006213 | reverse | revenue | 3 | pending |
| line-2 | line-2-0227-0358-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0367-0381-s003742 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**12 trainsets exceed the reference platform envelope**, requiring **588.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0159-0472-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0287-0456-s003007 | 6 | 4 | 2 | 98.0 |
| line-1-0324-0406-s004685 | 5 | 2 | 3 | 147.0 |
| line-1-0367-0381-s006109 | 4 | 4 | 0 | 0.0 |
| line-1-0373-0475-s008726 | 2 | 2 | 0 | 0.0 |
| line-2-0227-0358-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0306-0456-s006213 | 3 | 2 | 1 | 49.0 |
| line-2-0367-0381-s003742 | 7 | 4 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Lichinga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
