# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 90 at depots = 120 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0594-0760-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0785-0507-s015222 | line-2 | declared-depot | 35 | 2,082.5 | 7 |
| line-3-0698-0406-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0412-0263-s011635 | station | reverse | revenue | 2 |
| line-1 | line-1-0455-0381-s008872 | station | forward | revenue | 1 |
| line-1 | line-1-0455-0381-s008872 | station | reverse | revenue | 1 |
| line-1 | line-1-0500-0502-s006032 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0502-s006032 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0622-s003221 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0622-s003221 | station | reverse | revenue | 1 |
| line-1 | line-1-0594-0760-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0169-0808-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0307-0736-s003507 | station | forward | revenue | 1 |
| line-2 | line-2-0307-0736-s003507 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0668-s007000 | station | forward | revenue | 1 |
| line-2 | line-2-0450-0668-s007000 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0622-s009308 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0622-s009308 | station | reverse | revenue | 1 |
| line-2 | line-2-0666-0564-s012276 | station | forward | revenue | 1 |
| line-2 | line-2-0666-0564-s012276 | station | reverse | revenue | 1 |
| line-2 | line-2-0785-0507-s015222 | station | reverse | revenue | 2 |
| line-3 | line-3-0191-0361-s010591 | station | reverse | revenue | 2 |
| line-3 | line-3-0455-0381-s005079 | station | forward | revenue | 1 |
| line-3 | line-3-0455-0381-s005079 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0391-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0391-s003004 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0406-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0594-0760-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0594-0760-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0594-0760-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0785-0507-s015222 | depot | — | revenue | 30 |
| line-2 | line-2-0785-0507-s015222 | depot | — | spare | 4 |
| line-2 | line-2-0785-0507-s015222 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0698-0406-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0698-0406-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0698-0406-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rangpur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **120 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **107 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **90 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0594-0760-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0544-0622-s003221 | forward | revenue | 5 | pending |
| line-1 | line-1-0544-0622-s003221 | reverse | revenue | 4 | pending |
| line-1 | line-1-0500-0502-s006032 | forward | revenue | 4 | pending |
| line-1 | line-1-0500-0502-s006032 | reverse | revenue | 4 | pending |
| line-1 | line-1-0455-0381-s008872 | forward | revenue | 4 | pending |
| line-1 | line-1-0455-0381-s008872 | reverse | revenue | 4 | pending |
| line-1 | line-1-0412-0263-s011635 | reverse | revenue | 4 | pending |
| line-1 | line-1-0544-0622-s003221 | reverse | spare | 1 | pending |
| line-1 | line-1-0500-0502-s006032 | forward | spare | 1 | pending |
| line-1 | line-1-0500-0502-s006032 | reverse | spare | 1 | pending |
| line-1 | line-1-0455-0381-s008872 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0307-0736-s003507 | forward | revenue | 5 | pending |
| line-2 | line-2-0307-0736-s003507 | reverse | revenue | 4 | pending |
| line-2 | line-2-0450-0668-s007000 | forward | revenue | 4 | pending |
| line-2 | line-2-0450-0668-s007000 | reverse | revenue | 4 | pending |
| line-2 | line-2-0544-0622-s009308 | forward | revenue | 4 | pending |
| line-2 | line-2-0544-0622-s009308 | reverse | revenue | 4 | pending |
| line-2 | line-2-0666-0564-s012276 | forward | revenue | 4 | pending |
| line-2 | line-2-0666-0564-s012276 | reverse | revenue | 4 | pending |
| line-2 | line-2-0785-0507-s015222 | reverse | revenue | 4 | pending |
| line-2 | line-2-0307-0736-s003507 | reverse | spare | 1 | pending |
| line-2 | line-2-0450-0668-s007000 | forward | spare | 1 | pending |
| line-2 | line-2-0450-0668-s007000 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0622-s009308 | forward | spare | 1 | pending |
| line-2 | line-2-0544-0622-s009308 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0698-0406-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0554-0391-s003004 | forward | revenue | 5 | pending |
| line-3 | line-3-0554-0391-s003004 | reverse | revenue | 5 | pending |
| line-3 | line-3-0455-0381-s005079 | forward | revenue | 5 | pending |
| line-3 | line-3-0455-0381-s005079 | reverse | revenue | 5 | pending |
| line-3 | line-3-0191-0361-s010591 | reverse | revenue | 5 | pending |
| line-3 | line-3-0554-0391-s003004 | forward | spare | 1 | pending |
| line-3 | line-3-0554-0391-s003004 | reverse | spare | 1 | pending |
| line-3 | line-3-0455-0381-s005079 | forward | spare | 1 | pending |
| line-3 | line-3-0455-0381-s005079 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**82 trainsets exceed the reference platform envelope**, requiring **4,879.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0412-0263-s011635 | 4 | 2 | 2 | 119.0 |
| line-1-0455-0381-s008872 | 9 | 4 | 5 | 297.5 |
| line-1-0500-0502-s006032 | 10 | 2 | 8 | 476.0 |
| line-1-0544-0622-s003221 | 10 | 4 | 6 | 357.0 |
| line-1-0594-0760-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0169-0808-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0307-0736-s003507 | 10 | 2 | 8 | 476.0 |
| line-2-0450-0668-s007000 | 10 | 2 | 8 | 476.0 |
| line-2-0544-0622-s009308 | 10 | 4 | 6 | 357.0 |
| line-2-0666-0564-s012276 | 8 | 2 | 6 | 357.0 |
| line-2-0785-0507-s015222 | 4 | 2 | 2 | 119.0 |
| line-3-0191-0361-s010591 | 5 | 2 | 3 | 178.5 |
| line-3-0455-0381-s005079 | 12 | 4 | 8 | 476.0 |
| line-3-0554-0391-s003004 | 12 | 2 | 10 | 595.0 |
| line-3-0698-0406-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rangpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
