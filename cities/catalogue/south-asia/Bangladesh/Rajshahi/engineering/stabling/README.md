# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 74 at depots = 104 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0540-0014-s017034 | line-1 | declared-depot | 41 | 2,439.5 | 8 |
| line-2-0616-0676-s000000 | line-2 | declared-depot | 11 | 654.5 | 3 |
| line-3-0185-0604-s000000 | line-3 | declared-depot | 22 | 1,309.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0535-0411-s007774 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0411-s007774 | station | reverse | revenue | 1 |
| line-1 | line-1-0540-0014-s017034 | station | reverse | revenue | 2 |
| line-1 | line-1-0546-0494-s006023 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0494-s006023 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0552-s004797 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0552-s004797 | station | reverse | revenue | 1 |
| line-1 | line-1-0569-0663-s002453 | station | forward | revenue | 1 |
| line-1 | line-1-0569-0663-s002453 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0779-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0372-0609-s005435 | station | reverse | revenue | 2 |
| line-2 | line-2-0470-0636-s003251 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0636-s003251 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0663-s001048 | station | forward | revenue | 1 |
| line-2 | line-2-0569-0663-s001048 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0676-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0185-0604-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0313-0518-s003507 | station | forward | revenue | 1 |
| line-3 | line-3-0313-0518-s003507 | station | reverse | revenue | 1 |
| line-3 | line-3-0454-0450-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0454-0450-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0411-s009021 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0411-s009021 | station | reverse | revenue | 1 |
| line-3 | line-3-0577-0391-s010073 | station | reverse | revenue | 2 |
| line-1 | line-1-0540-0014-s017034 | depot | — | revenue | 36 |
| line-1 | line-1-0540-0014-s017034 | depot | — | spare | 4 |
| line-1 | line-1-0540-0014-s017034 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0616-0676-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0616-0676-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0616-0676-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0185-0604-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0185-0604-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0185-0604-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rajshahi-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **104 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **94 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **74 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0585-0779-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0569-0663-s002453 | forward | revenue | 5 | pending |
| line-1 | line-1-0569-0663-s002453 | reverse | revenue | 5 | pending |
| line-1 | line-1-0554-0552-s004797 | forward | revenue | 5 | pending |
| line-1 | line-1-0554-0552-s004797 | reverse | revenue | 5 | pending |
| line-1 | line-1-0546-0494-s006023 | forward | revenue | 5 | pending |
| line-1 | line-1-0546-0494-s006023 | reverse | revenue | 5 | pending |
| line-1 | line-1-0535-0411-s007774 | forward | revenue | 5 | pending |
| line-1 | line-1-0535-0411-s007774 | reverse | revenue | 4 | pending |
| line-1 | line-1-0540-0014-s017034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0535-0411-s007774 | reverse | spare | 1 | pending |
| line-1 | line-1-0540-0014-s017034 | reverse | spare | 1 | pending |
| line-1 | line-1-0585-0779-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0569-0663-s002453 | forward | spare | 1 | pending |
| line-1 | line-1-0569-0663-s002453 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0663-s001048 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0663-s001048 | reverse | revenue | 3 | pending |
| line-2 | line-2-0470-0636-s003251 | forward | revenue | 3 | pending |
| line-2 | line-2-0470-0636-s003251 | reverse | revenue | 3 | pending |
| line-2 | line-2-0372-0609-s005435 | reverse | revenue | 2 | pending |
| line-2 | line-2-0372-0609-s005435 | reverse | spare | 1 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0313-0518-s003507 | forward | revenue | 4 | pending |
| line-3 | line-3-0313-0518-s003507 | reverse | revenue | 4 | pending |
| line-3 | line-3-0454-0450-s007019 | forward | revenue | 4 | pending |
| line-3 | line-3-0454-0450-s007019 | reverse | revenue | 4 | pending |
| line-3 | line-3-0535-0411-s009021 | forward | revenue | 3 | pending |
| line-3 | line-3-0535-0411-s009021 | reverse | revenue | 3 | pending |
| line-3 | line-3-0577-0391-s010073 | reverse | revenue | 3 | pending |
| line-3 | line-3-0535-0411-s009021 | forward | spare | 1 | pending |
| line-3 | line-3-0535-0411-s009021 | reverse | spare | 1 | pending |
| line-3 | line-3-0577-0391-s010073 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**66 trainsets exceed the reference platform envelope**, requiring **3,927.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0535-0411-s007774 | 10 | 4 | 6 | 357.0 |
| line-1-0540-0014-s017034 | 5 | 2 | 3 | 178.5 |
| line-1-0546-0494-s006023 | 10 | 2 | 8 | 476.0 |
| line-1-0554-0552-s004797 | 10 | 2 | 8 | 476.0 |
| line-1-0569-0663-s002453 | 12 | 4 | 8 | 476.0 |
| line-1-0585-0779-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0372-0609-s005435 | 3 | 2 | 1 | 59.5 |
| line-2-0470-0636-s003251 | 6 | 2 | 4 | 238.0 |
| line-2-0569-0663-s001048 | 6 | 4 | 2 | 119.0 |
| line-2-0616-0676-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0185-0604-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0313-0518-s003507 | 8 | 2 | 6 | 357.0 |
| line-3-0454-0450-s007019 | 8 | 2 | 6 | 357.0 |
| line-3-0535-0411-s009021 | 8 | 4 | 4 | 238.0 |
| line-3-0577-0391-s010073 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rajshahi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
