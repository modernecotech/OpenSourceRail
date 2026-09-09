# Station and depot overnight allocation

Plan: **34 trainsets at stations + 47 at depots = 81 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0069-0563-s014494 | 47 | 2,303.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0069-0563-s014494 | station | reverse | revenue | 2 |
| line-1 | line-1-0182-0512-s011235 | station | forward | revenue | 1 |
| line-1 | line-1-0182-0512-s011235 | station | reverse | revenue | 1 |
| line-1 | line-1-0279-0441-s008217 | station | forward | revenue | 1 |
| line-1 | line-1-0279-0441-s008217 | station | reverse | revenue | 1 |
| line-1 | line-1-0375-0385-s005026 | station | forward | revenue | 1 |
| line-1 | line-1-0375-0385-s005026 | station | reverse | revenue | 1 |
| line-1 | line-1-0450-0376-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0450-0376-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0436-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0375-0385-s004254 | station | forward | revenue | 1 |
| line-2 | line-2-0375-0385-s004254 | station | reverse | revenue | 1 |
| line-2 | line-2-0387-0109-s010150 | station | forward | revenue | 1 |
| line-2 | line-2-0387-0109-s010150 | station | reverse | revenue | 1 |
| line-2 | line-2-0389-0203-s008176 | station | forward | revenue | 1 |
| line-2 | line-2-0389-0203-s008176 | station | reverse | revenue | 1 |
| line-2 | line-2-0394-0018-s012111 | station | reverse | revenue | 2 |
| line-2 | line-2-0394-0437-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0394-0437-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0518-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0258-0500-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0360-0442-s003000 | station | forward | revenue | 1 |
| line-3 | line-3-0360-0442-s003000 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0385-s004376 | station | forward | revenue | 1 |
| line-3 | line-3-0375-0385-s004376 | station | reverse | revenue | 1 |
| line-3 | line-3-0502-0457-s007676 | station | forward | revenue | 1 |
| line-3 | line-3-0502-0457-s007676 | station | reverse | revenue | 1 |
| line-3 | line-3-0685-0451-s012362 | station | reverse | revenue | 2 |
| line-1 | line-1-0069-0563-s014494 | depot | — | revenue | 15 |
| line-1 | line-1-0069-0563-s014494 | depot | — | spare | 2 |
| line-1 | line-1-0069-0563-s014494 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0069-0563-s014494 | depot | — | revenue | 10 |
| line-2 | line-1-0069-0563-s014494 | depot | — | spare | 2 |
| line-2 | line-1-0069-0563-s014494 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0069-0563-s014494 | depot | — | revenue | 13 |
| line-3 | line-1-0069-0563-s014494 | depot | — | spare | 2 |
| line-3 | line-1-0069-0563-s014494 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (16 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **81 trainsets at 17 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **72 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **47 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0533-0436-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0450-0376-s003020 | forward | revenue | 3 | pending |
| line-1 | line-1-0450-0376-s003020 | reverse | revenue | 3 | pending |
| line-1 | line-1-0375-0385-s005026 | forward | revenue | 3 | pending |
| line-1 | line-1-0375-0385-s005026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0279-0441-s008217 | forward | revenue | 3 | pending |
| line-1 | line-1-0279-0441-s008217 | reverse | revenue | 3 | pending |
| line-1 | line-1-0182-0512-s011235 | forward | revenue | 2 | pending |
| line-1 | line-1-0182-0512-s011235 | reverse | revenue | 2 | pending |
| line-1 | line-1-0069-0563-s014494 | reverse | revenue | 2 | pending |
| line-1 | line-1-0182-0512-s011235 | forward | spare | 1 | pending |
| line-1 | line-1-0182-0512-s011235 | reverse | spare | 1 | pending |
| line-1 | line-1-0069-0563-s014494 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0450-0518-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0394-0437-s003017 | forward | revenue | 3 | pending |
| line-2 | line-2-0394-0437-s003017 | reverse | revenue | 2 | pending |
| line-2 | line-2-0375-0385-s004254 | forward | revenue | 2 | pending |
| line-2 | line-2-0375-0385-s004254 | reverse | revenue | 2 | pending |
| line-2 | line-2-0389-0203-s008176 | forward | revenue | 2 | pending |
| line-2 | line-2-0389-0203-s008176 | reverse | revenue | 2 | pending |
| line-2 | line-2-0387-0109-s010150 | forward | revenue | 2 | pending |
| line-2 | line-2-0387-0109-s010150 | reverse | revenue | 2 | pending |
| line-2 | line-2-0394-0018-s012111 | reverse | revenue | 2 | pending |
| line-2 | line-2-0394-0437-s003017 | reverse | spare | 1 | pending |
| line-2 | line-2-0375-0385-s004254 | forward | spare | 1 | pending |
| line-2 | line-2-0375-0385-s004254 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0258-0500-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0360-0442-s003000 | forward | revenue | 3 | pending |
| line-3 | line-3-0360-0442-s003000 | reverse | revenue | 3 | pending |
| line-3 | line-3-0375-0385-s004376 | forward | revenue | 3 | pending |
| line-3 | line-3-0375-0385-s004376 | reverse | revenue | 3 | pending |
| line-3 | line-3-0502-0457-s007676 | forward | revenue | 3 | pending |
| line-3 | line-3-0502-0457-s007676 | reverse | revenue | 3 | pending |
| line-3 | line-3-0685-0451-s012362 | reverse | revenue | 2 | pending |
| line-3 | line-3-0685-0451-s012362 | reverse | spare | 1 | pending |
| line-3 | line-3-0258-0500-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0360-0442-s003000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,009.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0069-0563-s014494 | 3 | 2 | 1 | 49.0 |
| line-1-0182-0512-s011235 | 6 | 2 | 4 | 196.0 |
| line-1-0279-0441-s008217 | 6 | 2 | 4 | 196.0 |
| line-1-0375-0385-s005026 | 6 | 4 | 2 | 98.0 |
| line-1-0450-0376-s003020 | 6 | 2 | 4 | 196.0 |
| line-1-0533-0436-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0375-0385-s004254 | 6 | 4 | 2 | 98.0 |
| line-2-0387-0109-s010150 | 4 | 2 | 2 | 98.0 |
| line-2-0389-0203-s008176 | 4 | 2 | 2 | 98.0 |
| line-2-0394-0018-s012111 | 2 | 2 | 0 | 0.0 |
| line-2-0394-0437-s003017 | 6 | 2 | 4 | 196.0 |
| line-2-0450-0518-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0258-0500-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0360-0442-s003000 | 7 | 2 | 5 | 245.0 |
| line-3-0375-0385-s004376 | 6 | 4 | 2 | 98.0 |
| line-3-0502-0457-s007676 | 6 | 2 | 4 | 196.0 |
| line-3-0685-0451-s012362 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nacala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
