# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 68 at depots = 98 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0386-0735-s019721 | line-1 | declared-depot | 46 | 2,737.0 | 9 |
| line-2-0695-0574-s000000 | line-2 | declared-depot | 11 | 654.5 | 3 |
| line-3-0722-0711-s000000 | line-3 | declared-depot | 11 | 654.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0386-0735-s019721 | station | reverse | revenue | 2 |
| line-1 | line-1-0557-0569-s014350 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0569-s014350 | station | reverse | revenue | 1 |
| line-1 | line-1-0578-0629-s012947 | station | forward | revenue | 1 |
| line-1 | line-1-0578-0629-s012947 | station | reverse | revenue | 1 |
| line-1 | line-1-0656-0594-s009688 | station | forward | revenue | 1 |
| line-1 | line-1-0656-0594-s009688 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0581-s008757 | station | forward | revenue | 1 |
| line-1 | line-1-0694-0581-s008757 | station | reverse | revenue | 1 |
| line-1 | line-1-0767-0573-s006923 | station | forward | revenue | 1 |
| line-1 | line-1-0767-0573-s006923 | station | reverse | revenue | 1 |
| line-1 | line-1-1075-0511-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0668-0828-s005304 | station | reverse | revenue | 2 |
| line-2 | line-2-0687-0648-s001546 | station | forward | revenue | 1 |
| line-2 | line-2-0687-0648-s001546 | station | reverse | revenue | 1 |
| line-2 | line-2-0694-0581-s000148 | station | forward | revenue | 1 |
| line-2 | line-2-0694-0581-s000148 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0574-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0595-0487-s005720 | station | reverse | revenue | 2 |
| line-3 | line-3-0655-0593-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0655-0593-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0687-0648-s001597 | station | forward | revenue | 1 |
| line-3 | line-3-0687-0648-s001597 | station | reverse | revenue | 1 |
| line-3 | line-3-0722-0711-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0386-0735-s019721 | depot | — | revenue | 40 |
| line-1 | line-1-0386-0735-s019721 | depot | — | spare | 5 |
| line-1 | line-1-0386-0735-s019721 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0574-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0695-0574-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0695-0574-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0722-0711-s000000 | depot | — | revenue | 9 |
| line-3 | line-3-0722-0711-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0722-0711-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lobito-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **98 trainsets at 15 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **88 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1075-0511-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0767-0573-s006923 | forward | revenue | 5 | pending |
| line-1 | line-1-0767-0573-s006923 | reverse | revenue | 5 | pending |
| line-1 | line-1-0694-0581-s008757 | forward | revenue | 5 | pending |
| line-1 | line-1-0694-0581-s008757 | reverse | revenue | 5 | pending |
| line-1 | line-1-0656-0594-s009688 | forward | revenue | 5 | pending |
| line-1 | line-1-0656-0594-s009688 | reverse | revenue | 4 | pending |
| line-1 | line-1-0578-0629-s012947 | forward | revenue | 4 | pending |
| line-1 | line-1-0578-0629-s012947 | reverse | revenue | 4 | pending |
| line-1 | line-1-0557-0569-s014350 | forward | revenue | 4 | pending |
| line-1 | line-1-0557-0569-s014350 | reverse | revenue | 4 | pending |
| line-1 | line-1-0386-0735-s019721 | reverse | revenue | 4 | pending |
| line-1 | line-1-0656-0594-s009688 | reverse | spare | 1 | pending |
| line-1 | line-1-0578-0629-s012947 | forward | spare | 1 | pending |
| line-1 | line-1-0578-0629-s012947 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0569-s014350 | forward | spare | 1 | pending |
| line-1 | line-1-0557-0569-s014350 | reverse | spare | 1 | pending |
| line-1 | line-1-0386-0735-s019721 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0694-0581-s000148 | forward | revenue | 3 | pending |
| line-2 | line-2-0694-0581-s000148 | reverse | revenue | 3 | pending |
| line-2 | line-2-0687-0648-s001546 | forward | revenue | 3 | pending |
| line-2 | line-2-0687-0648-s001546 | reverse | revenue | 3 | pending |
| line-2 | line-2-0668-0828-s005304 | reverse | revenue | 2 | pending |
| line-2 | line-2-0668-0828-s005304 | reverse | spare | 1 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0687-0648-s001597 | forward | revenue | 3 | pending |
| line-3 | line-3-0687-0648-s001597 | reverse | revenue | 3 | pending |
| line-3 | line-3-0655-0593-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0655-0593-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0595-0487-s005720 | reverse | revenue | 2 | pending |
| line-3 | line-3-0595-0487-s005720 | reverse | spare | 1 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0386-0735-s019721 | 5 | 2 | 3 | 178.5 |
| line-1-0557-0569-s014350 | 10 | 2 | 8 | 476.0 |
| line-1-0578-0629-s012947 | 10 | 2 | 8 | 476.0 |
| line-1-0656-0594-s009688 | 10 | 4 | 6 | 357.0 |
| line-1-0694-0581-s008757 | 10 | 4 | 6 | 357.0 |
| line-1-0767-0573-s006923 | 10 | 2 | 8 | 476.0 |
| line-1-1075-0511-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0668-0828-s005304 | 3 | 2 | 1 | 59.5 |
| line-2-0687-0648-s001546 | 6 | 4 | 2 | 119.0 |
| line-2-0694-0581-s000148 | 6 | 4 | 2 | 119.0 |
| line-2-0695-0574-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0595-0487-s005720 | 3 | 2 | 1 | 59.5 |
| line-3-0655-0593-s003009 | 6 | 4 | 2 | 119.0 |
| line-3-0687-0648-s001597 | 6 | 4 | 2 | 119.0 |
| line-3-0722-0711-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lobito/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
