# Station and depot overnight allocation

Plan: **30 trainsets at stations + 99 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0885-0164-s025052 | 99 | 5,890.5 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0457-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0549-0556-s002531 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0556-s002531 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0599-s004234 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0599-s004234 | station | reverse | revenue | 1 |
| line-1 | line-1-0630-0629-s005944 | station | forward | revenue | 1 |
| line-1 | line-1-0630-0629-s005944 | station | reverse | revenue | 1 |
| line-1 | line-1-0704-0697-s008058 | station | forward | revenue | 1 |
| line-1 | line-1-0704-0697-s008058 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0786-s010172 | station | reverse | revenue | 2 |
| line-2 | line-2-0181-1033-s018352 | station | reverse | revenue | 2 |
| line-2 | line-2-0549-0556-s005328 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0556-s005328 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0486-s003199 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0486-s003199 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0447-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0212-1034-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0503-0660-s010315 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0660-s010315 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0556-s012866 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0556-s012866 | station | reverse | revenue | 1 |
| line-3 | line-3-0732-0385-s019095 | station | forward | revenue | 1 |
| line-3 | line-3-0732-0385-s019095 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0164-s025052 | station | reverse | revenue | 2 |
| line-1 | line-3-0885-0164-s025052 | depot | — | revenue | 15 |
| line-1 | line-3-0885-0164-s025052 | depot | — | spare | 2 |
| line-1 | line-3-0885-0164-s025052 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0885-0164-s025052 | depot | — | revenue | 30 |
| line-2 | line-3-0885-0164-s025052 | depot | — | spare | 3 |
| line-2 | line-3-0885-0164-s025052 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0885-0164-s025052 | depot | — | revenue | 41 |
| line-3 | line-3-0885-0164-s025052 | depot | — | spare | 5 |
| line-3 | line-3-0885-0164-s025052 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (18 trains), line-2 (34 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 15 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **99 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0457-0559-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0556-s002531 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0556-s002531 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0599-s004234 | forward | revenue | 3 | pending |
| line-1 | line-1-0571-0599-s004234 | reverse | revenue | 3 | pending |
| line-1 | line-1-0630-0629-s005944 | forward | revenue | 3 | pending |
| line-1 | line-1-0630-0629-s005944 | reverse | revenue | 3 | pending |
| line-1 | line-1-0704-0697-s008058 | forward | revenue | 2 | pending |
| line-1 | line-1-0704-0697-s008058 | reverse | revenue | 2 | pending |
| line-1 | line-1-0717-0786-s010172 | reverse | revenue | 2 | pending |
| line-1 | line-1-0704-0697-s008058 | forward | spare | 1 | pending |
| line-1 | line-1-0704-0697-s008058 | reverse | spare | 1 | pending |
| line-1 | line-1-0717-0786-s010172 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0742-0447-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0604-0486-s003199 | forward | revenue | 7 | pending |
| line-2 | line-2-0604-0486-s003199 | reverse | revenue | 6 | pending |
| line-2 | line-2-0549-0556-s005328 | forward | revenue | 6 | pending |
| line-2 | line-2-0549-0556-s005328 | reverse | revenue | 6 | pending |
| line-2 | line-2-0181-1033-s018352 | reverse | revenue | 6 | pending |
| line-2 | line-2-0604-0486-s003199 | reverse | spare | 1 | pending |
| line-2 | line-2-0549-0556-s005328 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0556-s005328 | reverse | spare | 1 | pending |
| line-2 | line-2-0181-1033-s018352 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0503-0660-s010315 | forward | revenue | 7 | pending |
| line-3 | line-3-0503-0660-s010315 | reverse | revenue | 7 | pending |
| line-3 | line-3-0549-0556-s012866 | forward | revenue | 6 | pending |
| line-3 | line-3-0549-0556-s012866 | reverse | revenue | 6 | pending |
| line-3 | line-3-0732-0385-s019095 | forward | revenue | 6 | pending |
| line-3 | line-3-0732-0385-s019095 | reverse | revenue | 6 | pending |
| line-3 | line-3-0885-0164-s025052 | reverse | revenue | 6 | pending |
| line-3 | line-3-0549-0556-s012866 | forward | spare | 1 | pending |
| line-3 | line-3-0549-0556-s012866 | reverse | spare | 1 | pending |
| line-3 | line-3-0732-0385-s019095 | forward | spare | 1 | pending |
| line-3 | line-3-0732-0385-s019095 | reverse | spare | 1 | pending |
| line-3 | line-3-0885-0164-s025052 | reverse | spare | 1 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**93 trainsets exceed the reference platform envelope**, requiring **5,533.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0457-0559-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0549-0556-s002531 | 6 | 4 | 2 | 119.0 |
| line-1-0571-0599-s004234 | 6 | 2 | 4 | 238.0 |
| line-1-0630-0629-s005944 | 6 | 2 | 4 | 238.0 |
| line-1-0704-0697-s008058 | 6 | 2 | 4 | 238.0 |
| line-1-0717-0786-s010172 | 3 | 2 | 1 | 59.5 |
| line-2-0181-1033-s018352 | 7 | 2 | 5 | 297.5 |
| line-2-0549-0556-s005328 | 14 | 4 | 10 | 595.0 |
| line-2-0604-0486-s003199 | 14 | 2 | 12 | 714.0 |
| line-2-0742-0447-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0212-1034-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0503-0660-s010315 | 14 | 2 | 12 | 714.0 |
| line-3-0549-0556-s012866 | 14 | 4 | 10 | 595.0 |
| line-3-0732-0385-s019095 | 14 | 2 | 12 | 714.0 |
| line-3-0885-0164-s025052 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Rahim-Yar-Khan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
