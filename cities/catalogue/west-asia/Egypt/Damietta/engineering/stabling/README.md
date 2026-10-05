# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 166 at depots = 208 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0076-0559-s000000 | line-1 | declared-depot | 51 | 3,034.5 | 10 |
| line-2-0747-0635-s000000 | line-2 | declared-depot | 42 | 2,499.0 | 8 |
| line-3-0013-0648-s027252 | line-3 | declared-depot | 73 | 4,343.5 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0076-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0132-0577-s002424 | station | forward | revenue | 1 |
| line-1 | line-1-0132-0577-s002424 | station | reverse | revenue | 1 |
| line-1 | line-1-0334-0557-s007149 | station | forward | revenue | 1 |
| line-1 | line-1-0334-0557-s007149 | station | reverse | revenue | 1 |
| line-1 | line-1-0473-0530-s010152 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0530-s010152 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0519-s011424 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0519-s011424 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0500-s013481 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0500-s013481 | station | reverse | revenue | 1 |
| line-1 | line-1-0738-0478-s015883 | station | forward | revenue | 1 |
| line-1 | line-1-0738-0478-s015883 | station | reverse | revenue | 1 |
| line-1 | line-1-0850-0457-s018297 | station | forward | revenue | 1 |
| line-1 | line-1-0850-0457-s018297 | station | reverse | revenue | 1 |
| line-1 | line-1-1043-0345-s023097 | station | reverse | revenue | 2 |
| line-2 | line-2-0356-0019-s017755 | station | reverse | revenue | 2 |
| line-2 | line-2-0503-0360-s008259 | station | forward | revenue | 1 |
| line-2 | line-2-0503-0360-s008259 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0434-s006042 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0434-s006042 | station | reverse | revenue | 1 |
| line-2 | line-2-0627-0500-s004057 | station | forward | revenue | 1 |
| line-2 | line-2-0627-0500-s004057 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0567-s002033 | station | forward | revenue | 1 |
| line-2 | line-2-0687-0567-s002033 | station | reverse | revenue | 1 |
| line-2 | line-2-0747-0635-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0013-0648-s027252 | station | reverse | revenue | 2 |
| line-3 | line-3-0132-0577-s023733 | station | forward | revenue | 1 |
| line-3 | line-3-0132-0577-s023733 | station | reverse | revenue | 1 |
| line-3 | line-3-0164-0502-s021617 | station | forward | revenue | 1 |
| line-3 | line-3-0164-0502-s021617 | station | reverse | revenue | 1 |
| line-3 | line-3-0418-0399-s015496 | station | forward | revenue | 1 |
| line-3 | line-3-0418-0399-s015496 | station | reverse | revenue | 1 |
| line-3 | line-3-0503-0360-s013473 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0360-s013473 | station | reverse | revenue | 1 |
| line-3 | line-3-0997-0136-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0076-0559-s000000 | depot | — | revenue | 44 |
| line-1 | line-1-0076-0559-s000000 | depot | — | spare | 6 |
| line-1 | line-1-0076-0559-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0747-0635-s000000 | depot | — | revenue | 37 |
| line-2 | line-2-0747-0635-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0747-0635-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0013-0648-s027252 | depot | — | revenue | 65 |
| line-3 | line-3-0013-0648-s027252 | depot | — | spare | 7 |
| line-3 | line-3-0013-0648-s027252 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damietta-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **208 trainsets at 21 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **188 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **166 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0076-0559-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0132-0577-s002424 | forward | revenue | 4 | pending |
| line-1 | line-1-0132-0577-s002424 | reverse | revenue | 4 | pending |
| line-1 | line-1-0334-0557-s007149 | forward | revenue | 4 | pending |
| line-1 | line-1-0334-0557-s007149 | reverse | revenue | 4 | pending |
| line-1 | line-1-0473-0530-s010152 | forward | revenue | 4 | pending |
| line-1 | line-1-0473-0530-s010152 | reverse | revenue | 4 | pending |
| line-1 | line-1-0532-0519-s011424 | forward | revenue | 4 | pending |
| line-1 | line-1-0532-0519-s011424 | reverse | revenue | 4 | pending |
| line-1 | line-1-0627-0500-s013481 | forward | revenue | 4 | pending |
| line-1 | line-1-0627-0500-s013481 | reverse | revenue | 4 | pending |
| line-1 | line-1-0738-0478-s015883 | forward | revenue | 4 | pending |
| line-1 | line-1-0738-0478-s015883 | reverse | revenue | 4 | pending |
| line-1 | line-1-0850-0457-s018297 | forward | revenue | 4 | pending |
| line-1 | line-1-0850-0457-s018297 | reverse | revenue | 3 | pending |
| line-1 | line-1-1043-0345-s023097 | reverse | revenue | 3 | pending |
| line-1 | line-1-0850-0457-s018297 | reverse | spare | 1 | pending |
| line-1 | line-1-1043-0345-s023097 | reverse | spare | 1 | pending |
| line-1 | line-1-0076-0559-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0132-0577-s002424 | forward | spare | 1 | pending |
| line-1 | line-1-0132-0577-s002424 | reverse | spare | 1 | pending |
| line-1 | line-1-0334-0557-s007149 | forward | spare | 1 | pending |
| line-1 | line-1-0334-0557-s007149 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0687-0567-s002033 | forward | revenue | 5 | pending |
| line-2 | line-2-0687-0567-s002033 | reverse | revenue | 5 | pending |
| line-2 | line-2-0627-0500-s004057 | forward | revenue | 5 | pending |
| line-2 | line-2-0627-0500-s004057 | reverse | revenue | 5 | pending |
| line-2 | line-2-0568-0434-s006042 | forward | revenue | 5 | pending |
| line-2 | line-2-0568-0434-s006042 | reverse | revenue | 5 | pending |
| line-2 | line-2-0503-0360-s008259 | forward | revenue | 5 | pending |
| line-2 | line-2-0503-0360-s008259 | reverse | revenue | 5 | pending |
| line-2 | line-2-0356-0019-s017755 | reverse | revenue | 4 | pending |
| line-2 | line-2-0356-0019-s017755 | reverse | spare | 1 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0687-0567-s002033 | forward | spare | 1 | pending |
| line-2 | line-2-0687-0567-s002033 | reverse | spare | 1 | pending |
| line-2 | line-2-0627-0500-s004057 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0503-0360-s013473 | forward | revenue | 8 | pending |
| line-3 | line-3-0503-0360-s013473 | reverse | revenue | 8 | pending |
| line-3 | line-3-0418-0399-s015496 | forward | revenue | 8 | pending |
| line-3 | line-3-0418-0399-s015496 | reverse | revenue | 8 | pending |
| line-3 | line-3-0164-0502-s021617 | forward | revenue | 8 | pending |
| line-3 | line-3-0164-0502-s021617 | reverse | revenue | 8 | pending |
| line-3 | line-3-0132-0577-s023733 | forward | revenue | 7 | pending |
| line-3 | line-3-0132-0577-s023733 | reverse | revenue | 7 | pending |
| line-3 | line-3-0013-0648-s027252 | reverse | revenue | 7 | pending |
| line-3 | line-3-0132-0577-s023733 | forward | spare | 1 | pending |
| line-3 | line-3-0132-0577-s023733 | reverse | spare | 1 | pending |
| line-3 | line-3-0013-0648-s027252 | reverse | spare | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0503-0360-s013473 | forward | spare | 1 | pending |
| line-3 | line-3-0503-0360-s013473 | reverse | spare | 1 | pending |
| line-3 | line-3-0418-0399-s015496 | forward | spare | 1 | pending |
| line-3 | line-3-0418-0399-s015496 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**154 trainsets exceed the reference platform envelope**, requiring **9,163.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0076-0559-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0132-0577-s002424 | 10 | 4 | 6 | 357.0 |
| line-1-0334-0557-s007149 | 10 | 2 | 8 | 476.0 |
| line-1-0473-0530-s010152 | 8 | 2 | 6 | 357.0 |
| line-1-0532-0519-s011424 | 8 | 2 | 6 | 357.0 |
| line-1-0627-0500-s013481 | 8 | 4 | 4 | 238.0 |
| line-1-0738-0478-s015883 | 8 | 2 | 6 | 357.0 |
| line-1-0850-0457-s018297 | 8 | 2 | 6 | 357.0 |
| line-1-1043-0345-s023097 | 4 | 2 | 2 | 119.0 |
| line-2-0356-0019-s017755 | 5 | 2 | 3 | 178.5 |
| line-2-0503-0360-s008259 | 10 | 4 | 6 | 357.0 |
| line-2-0568-0434-s006042 | 10 | 2 | 8 | 476.0 |
| line-2-0627-0500-s004057 | 11 | 4 | 7 | 416.5 |
| line-2-0687-0567-s002033 | 12 | 2 | 10 | 595.0 |
| line-2-0747-0635-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0013-0648-s027252 | 8 | 2 | 6 | 357.0 |
| line-3-0132-0577-s023733 | 16 | 4 | 12 | 714.0 |
| line-3-0164-0502-s021617 | 16 | 2 | 14 | 833.0 |
| line-3-0418-0399-s015496 | 18 | 2 | 16 | 952.0 |
| line-3-0503-0360-s013473 | 18 | 4 | 14 | 833.0 |
| line-3-0997-0136-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damietta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
