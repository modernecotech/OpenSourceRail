# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 87 at depots = 117 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0747-0629-s015772 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0527-0431-s000000 | line-2 | declared-depot | 19 | 1,130.5 | 4 |
| line-3-0354-0190-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0078-0386-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0364-0502-s007002 | station | forward | revenue | 1 |
| line-1 | line-1-0364-0502-s007002 | station | reverse | revenue | 1 |
| line-1 | line-1-0454-0532-s009062 | station | forward | revenue | 1 |
| line-1 | line-1-0454-0532-s009062 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0562-s011111 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0562-s011111 | station | reverse | revenue | 1 |
| line-1 | line-1-0646-0595-s013447 | station | forward | revenue | 1 |
| line-1 | line-1-0646-0595-s013447 | station | reverse | revenue | 1 |
| line-1 | line-1-0747-0629-s015772 | station | reverse | revenue | 2 |
| line-2 | line-2-0527-0431-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0556-0557-s002784 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0557-s002784 | station | reverse | revenue | 1 |
| line-2 | line-2-0587-0688-s005660 | station | forward | revenue | 1 |
| line-2 | line-2-0587-0688-s005660 | station | reverse | revenue | 1 |
| line-2 | line-2-0617-0819-s008552 | station | reverse | revenue | 2 |
| line-3 | line-3-0354-0190-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0406-0344-s003511 | station | forward | revenue | 1 |
| line-3 | line-3-0406-0344-s003511 | station | reverse | revenue | 1 |
| line-3 | line-3-0435-0507-s007011 | station | forward | revenue | 1 |
| line-3 | line-3-0435-0507-s007011 | station | reverse | revenue | 1 |
| line-3 | line-3-0456-0627-s009585 | station | forward | revenue | 1 |
| line-3 | line-3-0456-0627-s009585 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0747-s012159 | station | reverse | revenue | 2 |
| line-1 | line-1-0747-0629-s015772 | depot | — | revenue | 35 |
| line-1 | line-1-0747-0629-s015772 | depot | — | spare | 4 |
| line-1 | line-1-0747-0629-s015772 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0527-0431-s000000 | depot | — | revenue | 16 |
| line-2 | line-2-0527-0431-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0527-0431-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0190-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0354-0190-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0354-0190-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/zagazig-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **117 trainsets at 15 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **105 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **87 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0078-0386-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0364-0502-s007002 | forward | revenue | 5 | pending |
| line-1 | line-1-0364-0502-s007002 | reverse | revenue | 5 | pending |
| line-1 | line-1-0454-0532-s009062 | forward | revenue | 5 | pending |
| line-1 | line-1-0454-0532-s009062 | reverse | revenue | 5 | pending |
| line-1 | line-1-0544-0562-s011111 | forward | revenue | 5 | pending |
| line-1 | line-1-0544-0562-s011111 | reverse | revenue | 5 | pending |
| line-1 | line-1-0646-0595-s013447 | forward | revenue | 4 | pending |
| line-1 | line-1-0646-0595-s013447 | reverse | revenue | 4 | pending |
| line-1 | line-1-0747-0629-s015772 | reverse | revenue | 4 | pending |
| line-1 | line-1-0646-0595-s013447 | forward | spare | 1 | pending |
| line-1 | line-1-0646-0595-s013447 | reverse | spare | 1 | pending |
| line-1 | line-1-0747-0629-s015772 | reverse | spare | 1 | pending |
| line-1 | line-1-0078-0386-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0364-0502-s007002 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0527-0431-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0556-0557-s002784 | forward | revenue | 4 | pending |
| line-2 | line-2-0556-0557-s002784 | reverse | revenue | 4 | pending |
| line-2 | line-2-0587-0688-s005660 | forward | revenue | 4 | pending |
| line-2 | line-2-0587-0688-s005660 | reverse | revenue | 4 | pending |
| line-2 | line-2-0617-0819-s008552 | reverse | revenue | 4 | pending |
| line-2 | line-2-0527-0431-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0557-s002784 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0557-s002784 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0190-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0406-0344-s003511 | forward | revenue | 5 | pending |
| line-3 | line-3-0406-0344-s003511 | reverse | revenue | 4 | pending |
| line-3 | line-3-0435-0507-s007011 | forward | revenue | 4 | pending |
| line-3 | line-3-0435-0507-s007011 | reverse | revenue | 4 | pending |
| line-3 | line-3-0456-0627-s009585 | forward | revenue | 4 | pending |
| line-3 | line-3-0456-0627-s009585 | reverse | revenue | 4 | pending |
| line-3 | line-3-0477-0747-s012159 | reverse | revenue | 4 | pending |
| line-3 | line-3-0406-0344-s003511 | reverse | spare | 1 | pending |
| line-3 | line-3-0435-0507-s007011 | forward | spare | 1 | pending |
| line-3 | line-3-0435-0507-s007011 | reverse | spare | 1 | pending |
| line-3 | line-3-0456-0627-s009585 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**79 trainsets exceed the reference platform envelope**, requiring **4,700.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0078-0386-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0364-0502-s007002 | 11 | 2 | 9 | 535.5 |
| line-1-0454-0532-s009062 | 10 | 4 | 6 | 357.0 |
| line-1-0544-0562-s011111 | 10 | 4 | 6 | 357.0 |
| line-1-0646-0595-s013447 | 10 | 2 | 8 | 476.0 |
| line-1-0747-0629-s015772 | 5 | 2 | 3 | 178.5 |
| line-2-0527-0431-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0556-0557-s002784 | 10 | 4 | 6 | 357.0 |
| line-2-0587-0688-s005660 | 8 | 2 | 6 | 357.0 |
| line-2-0617-0819-s008552 | 4 | 2 | 2 | 119.0 |
| line-3-0354-0190-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0406-0344-s003511 | 10 | 2 | 8 | 476.0 |
| line-3-0435-0507-s007011 | 10 | 4 | 6 | 357.0 |
| line-3-0456-0627-s009585 | 9 | 2 | 7 | 416.5 |
| line-3-0477-0747-s012159 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Zagazig/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
