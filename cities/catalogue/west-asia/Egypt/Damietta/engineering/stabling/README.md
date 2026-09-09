# Station and depot overnight allocation

Plan: **46 trainsets at stations + 110 at depots = 156 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0013-0648-s026780 | 110 | 6,545.0 | 24 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0076-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0335-0563-s006987 | station | forward | revenue | 1 |
| line-1 | line-1-0335-0563-s006987 | station | reverse | revenue | 1 |
| line-1 | line-1-0474-0540-s009991 | station | forward | revenue | 1 |
| line-1 | line-1-0474-0540-s009991 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0546-s011327 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0546-s011327 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0548-s012996 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0548-s012996 | station | reverse | revenue | 1 |
| line-1 | line-1-0726-0512-s016004 | station | forward | revenue | 1 |
| line-1 | line-1-0726-0512-s016004 | station | reverse | revenue | 1 |
| line-1 | line-1-0880-0438-s020048 | station | forward | revenue | 1 |
| line-1 | line-1-0880-0438-s020048 | station | reverse | revenue | 1 |
| line-1 | line-1-1043-0345-s024079 | station | reverse | revenue | 2 |
| line-2 | line-2-0356-0019-s022637 | station | reverse | revenue | 2 |
| line-2 | line-2-0376-0240-s017344 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0240-s017344 | station | reverse | revenue | 1 |
| line-2 | line-2-0481-0472-s009040 | station | forward | revenue | 1 |
| line-2 | line-2-0481-0472-s009040 | station | reverse | revenue | 1 |
| line-2 | line-2-0534-0370-s012060 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0370-s012060 | station | reverse | revenue | 1 |
| line-2 | line-2-0535-0546-s006148 | station | forward | revenue | 1 |
| line-2 | line-2-0535-0546-s006148 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0599-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0599-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0747-0635-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0013-0648-s026780 | station | reverse | revenue | 2 |
| line-3 | line-3-0134-0574-s023660 | station | forward | revenue | 1 |
| line-3 | line-3-0134-0574-s023660 | station | reverse | revenue | 1 |
| line-3 | line-3-0223-0491-s020642 | station | forward | revenue | 1 |
| line-3 | line-3-0223-0491-s020642 | station | reverse | revenue | 1 |
| line-3 | line-3-0359-0407-s017120 | station | forward | revenue | 1 |
| line-3 | line-3-0359-0407-s017120 | station | reverse | revenue | 1 |
| line-3 | line-3-0526-0387-s013615 | station | forward | revenue | 1 |
| line-3 | line-3-0526-0387-s013615 | station | reverse | revenue | 1 |
| line-3 | line-3-0637-0360-s010604 | station | forward | revenue | 1 |
| line-3 | line-3-0637-0360-s010604 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0262-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0764-0262-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0997-0136-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0013-0648-s026780 | depot | — | revenue | 30 |
| line-1 | line-3-0013-0648-s026780 | depot | — | spare | 4 |
| line-1 | line-3-0013-0648-s026780 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0013-0648-s026780 | depot | — | revenue | 28 |
| line-2 | line-3-0013-0648-s026780 | depot | — | spare | 4 |
| line-2 | line-3-0013-0648-s026780 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0013-0648-s026780 | depot | — | revenue | 36 |
| line-3 | line-3-0013-0648-s026780 | depot | — | spare | 5 |
| line-3 | line-3-0013-0648-s026780 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (35 trains), line-2 (33 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **156 trainsets at 23 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **140 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **110 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0076-0559-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0335-0563-s006987 | forward | revenue | 4 | pending |
| line-1 | line-1-0335-0563-s006987 | reverse | revenue | 4 | pending |
| line-1 | line-1-0474-0540-s009991 | forward | revenue | 4 | pending |
| line-1 | line-1-0474-0540-s009991 | reverse | revenue | 3 | pending |
| line-1 | line-1-0535-0546-s011327 | forward | revenue | 3 | pending |
| line-1 | line-1-0535-0546-s011327 | reverse | revenue | 3 | pending |
| line-1 | line-1-0606-0548-s012996 | forward | revenue | 3 | pending |
| line-1 | line-1-0606-0548-s012996 | reverse | revenue | 3 | pending |
| line-1 | line-1-0726-0512-s016004 | forward | revenue | 3 | pending |
| line-1 | line-1-0726-0512-s016004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0880-0438-s020048 | forward | revenue | 3 | pending |
| line-1 | line-1-0880-0438-s020048 | reverse | revenue | 3 | pending |
| line-1 | line-1-1043-0345-s024079 | reverse | revenue | 3 | pending |
| line-1 | line-1-0474-0540-s009991 | reverse | spare | 1 | pending |
| line-1 | line-1-0535-0546-s011327 | forward | spare | 1 | pending |
| line-1 | line-1-0535-0546-s011327 | reverse | spare | 1 | pending |
| line-1 | line-1-0606-0548-s012996 | forward | spare | 1 | pending |
| line-1 | line-1-0606-0548-s012996 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0611-0599-s003018 | forward | revenue | 4 | pending |
| line-2 | line-2-0611-0599-s003018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0535-0546-s006148 | forward | revenue | 4 | pending |
| line-2 | line-2-0535-0546-s006148 | reverse | revenue | 4 | pending |
| line-2 | line-2-0481-0472-s009040 | forward | revenue | 4 | pending |
| line-2 | line-2-0481-0472-s009040 | reverse | revenue | 3 | pending |
| line-2 | line-2-0534-0370-s012060 | forward | revenue | 3 | pending |
| line-2 | line-2-0534-0370-s012060 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0240-s017344 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0240-s017344 | reverse | revenue | 3 | pending |
| line-2 | line-2-0356-0019-s022637 | reverse | revenue | 3 | pending |
| line-2 | line-2-0481-0472-s009040 | reverse | spare | 1 | pending |
| line-2 | line-2-0534-0370-s012060 | forward | spare | 1 | pending |
| line-2 | line-2-0534-0370-s012060 | reverse | spare | 1 | pending |
| line-2 | line-2-0376-0240-s017344 | forward | spare | 1 | pending |
| line-2 | line-2-0376-0240-s017344 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0764-0262-s007019 | forward | revenue | 4 | pending |
| line-3 | line-3-0764-0262-s007019 | reverse | revenue | 4 | pending |
| line-3 | line-3-0637-0360-s010604 | forward | revenue | 4 | pending |
| line-3 | line-3-0637-0360-s010604 | reverse | revenue | 4 | pending |
| line-3 | line-3-0526-0387-s013615 | forward | revenue | 4 | pending |
| line-3 | line-3-0526-0387-s013615 | reverse | revenue | 4 | pending |
| line-3 | line-3-0359-0407-s017120 | forward | revenue | 4 | pending |
| line-3 | line-3-0359-0407-s017120 | reverse | revenue | 4 | pending |
| line-3 | line-3-0223-0491-s020642 | forward | revenue | 4 | pending |
| line-3 | line-3-0223-0491-s020642 | reverse | revenue | 3 | pending |
| line-3 | line-3-0134-0574-s023660 | forward | revenue | 3 | pending |
| line-3 | line-3-0134-0574-s023660 | reverse | revenue | 3 | pending |
| line-3 | line-3-0013-0648-s026780 | reverse | revenue | 3 | pending |
| line-3 | line-3-0223-0491-s020642 | reverse | spare | 1 | pending |
| line-3 | line-3-0134-0574-s023660 | forward | spare | 1 | pending |
| line-3 | line-3-0134-0574-s023660 | reverse | spare | 1 | pending |
| line-3 | line-3-0013-0648-s026780 | reverse | spare | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0764-0262-s007019 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**102 trainsets exceed the reference platform envelope**, requiring **6,069.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0076-0559-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0335-0563-s006987 | 8 | 2 | 6 | 357.0 |
| line-1-0474-0540-s009991 | 8 | 2 | 6 | 357.0 |
| line-1-0535-0546-s011327 | 8 | 4 | 4 | 238.0 |
| line-1-0606-0548-s012996 | 8 | 2 | 6 | 357.0 |
| line-1-0726-0512-s016004 | 6 | 2 | 4 | 238.0 |
| line-1-0880-0438-s020048 | 6 | 2 | 4 | 238.0 |
| line-1-1043-0345-s024079 | 3 | 2 | 1 | 59.5 |
| line-2-0356-0019-s022637 | 3 | 2 | 1 | 59.5 |
| line-2-0376-0240-s017344 | 8 | 2 | 6 | 357.0 |
| line-2-0481-0472-s009040 | 8 | 2 | 6 | 357.0 |
| line-2-0534-0370-s012060 | 8 | 4 | 4 | 238.0 |
| line-2-0535-0546-s006148 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0599-s003018 | 8 | 2 | 6 | 357.0 |
| line-2-0747-0635-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0013-0648-s026780 | 4 | 2 | 2 | 119.0 |
| line-3-0134-0574-s023660 | 8 | 2 | 6 | 357.0 |
| line-3-0223-0491-s020642 | 8 | 2 | 6 | 357.0 |
| line-3-0359-0407-s017120 | 8 | 2 | 6 | 357.0 |
| line-3-0526-0387-s013615 | 8 | 4 | 4 | 238.0 |
| line-3-0637-0360-s010604 | 8 | 2 | 6 | 357.0 |
| line-3-0764-0262-s007019 | 9 | 2 | 7 | 416.5 |
| line-3-0997-0136-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damietta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
