# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 97 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0616-0026-s017667 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0742-0821-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 6 |
| line-3-0763-0381-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0346-0781-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0419-0624-s003815 | station | forward | revenue | 1 |
| line-1 | line-1-0419-0624-s003815 | station | reverse | revenue | 1 |
| line-1 | line-1-0476-0501-s006829 | station | forward | revenue | 1 |
| line-1 | line-1-0476-0501-s006829 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0378-s009843 | station | forward | revenue | 1 |
| line-1 | line-1-0533-0378-s009843 | station | reverse | revenue | 1 |
| line-1 | line-1-0591-0254-s012863 | station | forward | revenue | 1 |
| line-1 | line-1-0591-0254-s012863 | station | reverse | revenue | 1 |
| line-1 | line-1-0616-0026-s017667 | station | reverse | revenue | 2 |
| line-2 | line-2-0244-0440-s014054 | station | reverse | revenue | 2 |
| line-2 | line-2-0398-0558-s009727 | station | forward | revenue | 1 |
| line-2 | line-2-0398-0558-s009727 | station | reverse | revenue | 1 |
| line-2 | line-2-0505-0640-s006708 | station | forward | revenue | 1 |
| line-2 | line-2-0505-0640-s006708 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0721-s003694 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0721-s003694 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0821-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0465-0767-s010915 | station | reverse | revenue | 2 |
| line-3 | line-3-0531-0681-s008473 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0681-s008473 | station | reverse | revenue | 1 |
| line-3 | line-3-0599-0593-s006009 | station | forward | revenue | 1 |
| line-3 | line-3-0599-0593-s006009 | station | reverse | revenue | 1 |
| line-3 | line-3-0681-0488-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0681-0488-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0763-0381-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0616-0026-s017667 | depot | — | revenue | 35 |
| line-1 | line-1-0616-0026-s017667 | depot | — | spare | 4 |
| line-1 | line-1-0616-0026-s017667 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0742-0821-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0742-0821-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0742-0821-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0763-0381-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0763-0381-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0763-0381-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kandahar-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **97 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0346-0781-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0419-0624-s003815 | forward | revenue | 5 | pending |
| line-1 | line-1-0419-0624-s003815 | reverse | revenue | 5 | pending |
| line-1 | line-1-0476-0501-s006829 | forward | revenue | 5 | pending |
| line-1 | line-1-0476-0501-s006829 | reverse | revenue | 5 | pending |
| line-1 | line-1-0533-0378-s009843 | forward | revenue | 5 | pending |
| line-1 | line-1-0533-0378-s009843 | reverse | revenue | 5 | pending |
| line-1 | line-1-0591-0254-s012863 | forward | revenue | 4 | pending |
| line-1 | line-1-0591-0254-s012863 | reverse | revenue | 4 | pending |
| line-1 | line-1-0616-0026-s017667 | reverse | revenue | 4 | pending |
| line-1 | line-1-0591-0254-s012863 | forward | spare | 1 | pending |
| line-1 | line-1-0591-0254-s012863 | reverse | spare | 1 | pending |
| line-1 | line-1-0616-0026-s017667 | reverse | spare | 1 | pending |
| line-1 | line-1-0346-0781-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0419-0624-s003815 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0742-0821-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0611-0721-s003694 | forward | revenue | 5 | pending |
| line-2 | line-2-0611-0721-s003694 | reverse | revenue | 5 | pending |
| line-2 | line-2-0505-0640-s006708 | forward | revenue | 5 | pending |
| line-2 | line-2-0505-0640-s006708 | reverse | revenue | 5 | pending |
| line-2 | line-2-0398-0558-s009727 | forward | revenue | 5 | pending |
| line-2 | line-2-0398-0558-s009727 | reverse | revenue | 5 | pending |
| line-2 | line-2-0244-0440-s014054 | reverse | revenue | 4 | pending |
| line-2 | line-2-0244-0440-s014054 | reverse | spare | 1 | pending |
| line-2 | line-2-0742-0821-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0611-0721-s003694 | forward | spare | 1 | pending |
| line-2 | line-2-0611-0721-s003694 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0763-0381-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0681-0488-s003007 | forward | revenue | 4 | pending |
| line-3 | line-3-0681-0488-s003007 | reverse | revenue | 4 | pending |
| line-3 | line-3-0599-0593-s006009 | forward | revenue | 4 | pending |
| line-3 | line-3-0599-0593-s006009 | reverse | revenue | 4 | pending |
| line-3 | line-3-0531-0681-s008473 | forward | revenue | 4 | pending |
| line-3 | line-3-0531-0681-s008473 | reverse | revenue | 3 | pending |
| line-3 | line-3-0465-0767-s010915 | reverse | revenue | 3 | pending |
| line-3 | line-3-0531-0681-s008473 | reverse | spare | 1 | pending |
| line-3 | line-3-0465-0767-s010915 | reverse | spare | 1 | pending |
| line-3 | line-3-0763-0381-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0681-0488-s003007 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**97 trainsets exceed the reference platform envelope**, requiring **5,771.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0346-0781-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0419-0624-s003815 | 11 | 2 | 9 | 535.5 |
| line-1-0476-0501-s006829 | 10 | 2 | 8 | 476.0 |
| line-1-0533-0378-s009843 | 10 | 2 | 8 | 476.0 |
| line-1-0591-0254-s012863 | 10 | 2 | 8 | 476.0 |
| line-1-0616-0026-s017667 | 5 | 2 | 3 | 178.5 |
| line-2-0244-0440-s014054 | 5 | 2 | 3 | 178.5 |
| line-2-0398-0558-s009727 | 10 | 2 | 8 | 476.0 |
| line-2-0505-0640-s006708 | 10 | 2 | 8 | 476.0 |
| line-2-0611-0721-s003694 | 12 | 2 | 10 | 595.0 |
| line-2-0742-0821-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0465-0767-s010915 | 4 | 2 | 2 | 119.0 |
| line-3-0531-0681-s008473 | 8 | 2 | 6 | 357.0 |
| line-3-0599-0593-s006009 | 8 | 2 | 6 | 357.0 |
| line-3-0681-0488-s003007 | 9 | 2 | 7 | 416.5 |
| line-3-0763-0381-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Kandahar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
