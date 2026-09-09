# Station and depot overnight allocation

Plan: **28 trainsets at stations + 56 at depots = 84 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0913-0374-s016951 | 56 | 3,332.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0432-0620-s006014 | station | forward | revenue | 1 |
| line-1 | line-1-0432-0620-s006014 | station | reverse | revenue | 1 |
| line-1 | line-1-0462-0834-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0480-0727-s003012 | station | forward | revenue | 1 |
| line-1 | line-1-0480-0727-s003012 | station | reverse | revenue | 1 |
| line-1 | line-1-0481-0553-s007866 | station | forward | revenue | 1 |
| line-1 | line-1-0481-0553-s007866 | station | reverse | revenue | 1 |
| line-1 | line-1-0570-0514-s010019 | station | forward | revenue | 1 |
| line-1 | line-1-0570-0514-s010019 | station | reverse | revenue | 1 |
| line-1 | line-1-0641-0492-s012147 | station | reverse | revenue | 2 |
| line-2 | line-2-0510-0774-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0546-0660-s003008 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0660-s003008 | station | reverse | revenue | 1 |
| line-2 | line-2-0640-0584-s006014 | station | forward | revenue | 1 |
| line-2 | line-2-0640-0584-s006014 | station | reverse | revenue | 1 |
| line-2 | line-2-0913-0374-s016951 | station | reverse | revenue | 2 |
| line-3 | line-3-0403-0652-s009737 | station | reverse | revenue | 2 |
| line-3 | line-3-0481-0553-s006701 | station | forward | revenue | 1 |
| line-3 | line-3-0481-0553-s006701 | station | reverse | revenue | 1 |
| line-3 | line-3-0581-0615-s003012 | station | forward | revenue | 1 |
| line-3 | line-3-0581-0615-s003012 | station | reverse | revenue | 1 |
| line-3 | line-3-0680-0673-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0913-0374-s016951 | depot | — | revenue | 12 |
| line-1 | line-2-0913-0374-s016951 | depot | — | spare | 2 |
| line-1 | line-2-0913-0374-s016951 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0913-0374-s016951 | depot | — | revenue | 24 |
| line-2 | line-2-0913-0374-s016951 | depot | — | spare | 3 |
| line-2 | line-2-0913-0374-s016951 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0913-0374-s016951 | depot | — | revenue | 11 |
| line-3 | line-2-0913-0374-s016951 | depot | — | spare | 1 |
| line-3 | line-2-0913-0374-s016951 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (15 trains), line-3 (13 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **75 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **56 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0462-0834-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0727-s003012 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0727-s003012 | reverse | revenue | 3 | pending |
| line-1 | line-1-0432-0620-s006014 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0620-s006014 | reverse | revenue | 2 | pending |
| line-1 | line-1-0481-0553-s007866 | forward | revenue | 2 | pending |
| line-1 | line-1-0481-0553-s007866 | reverse | revenue | 2 | pending |
| line-1 | line-1-0570-0514-s010019 | forward | revenue | 2 | pending |
| line-1 | line-1-0570-0514-s010019 | reverse | revenue | 2 | pending |
| line-1 | line-1-0641-0492-s012147 | reverse | revenue | 2 | pending |
| line-1 | line-1-0432-0620-s006014 | reverse | spare | 1 | pending |
| line-1 | line-1-0481-0553-s007866 | forward | spare | 1 | pending |
| line-1 | line-1-0481-0553-s007866 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0510-0774-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0546-0660-s003008 | forward | revenue | 6 | pending |
| line-2 | line-2-0546-0660-s003008 | reverse | revenue | 5 | pending |
| line-2 | line-2-0640-0584-s006014 | forward | revenue | 5 | pending |
| line-2 | line-2-0640-0584-s006014 | reverse | revenue | 5 | pending |
| line-2 | line-2-0913-0374-s016951 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0660-s003008 | reverse | spare | 1 | pending |
| line-2 | line-2-0640-0584-s006014 | forward | spare | 1 | pending |
| line-2 | line-2-0640-0584-s006014 | reverse | spare | 1 | pending |
| line-2 | line-2-0913-0374-s016951 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0680-0673-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0581-0615-s003012 | forward | revenue | 3 | pending |
| line-3 | line-3-0581-0615-s003012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0481-0553-s006701 | forward | revenue | 3 | pending |
| line-3 | line-3-0481-0553-s006701 | reverse | revenue | 3 | pending |
| line-3 | line-3-0403-0652-s009737 | reverse | revenue | 3 | pending |
| line-3 | line-3-0581-0615-s003012 | forward | spare | 1 | pending |
| line-3 | line-3-0581-0615-s003012 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**52 trainsets exceed the reference platform envelope**, requiring **3,094.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0432-0620-s006014 | 6 | 2 | 4 | 238.0 |
| line-1-0462-0834-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0480-0727-s003012 | 6 | 2 | 4 | 238.0 |
| line-1-0481-0553-s007866 | 6 | 4 | 2 | 119.0 |
| line-1-0570-0514-s010019 | 4 | 2 | 2 | 119.0 |
| line-1-0641-0492-s012147 | 2 | 2 | 0 | 0.0 |
| line-2-0510-0774-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0546-0660-s003008 | 12 | 2 | 10 | 595.0 |
| line-2-0640-0584-s006014 | 12 | 2 | 10 | 595.0 |
| line-2-0913-0374-s016951 | 6 | 2 | 4 | 238.0 |
| line-3-0403-0652-s009737 | 3 | 2 | 1 | 59.5 |
| line-3-0481-0553-s006701 | 6 | 4 | 2 | 119.0 |
| line-3-0581-0615-s003012 | 8 | 2 | 6 | 357.0 |
| line-3-0680-0673-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Gaza-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
