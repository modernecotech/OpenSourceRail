# Station and depot overnight allocation

Plan: **34 trainsets at stations + 72 at depots = 106 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0113-0058-s021649 | 72 | 4,284.0 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0398-0570-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0491-0549-s002690 | station | forward | revenue | 1 |
| line-1 | line-1-0491-0549-s002690 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0551-s004791 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0551-s004791 | station | reverse | revenue | 1 |
| line-1 | line-1-0618-0564-s006756 | station | forward | revenue | 1 |
| line-1 | line-1-0618-0564-s006756 | station | reverse | revenue | 1 |
| line-1 | line-1-0654-0488-s008708 | station | forward | revenue | 1 |
| line-1 | line-1-0654-0488-s008708 | station | reverse | revenue | 1 |
| line-1 | line-1-0806-0339-s014618 | station | reverse | revenue | 2 |
| line-2 | line-2-0113-0058-s021649 | station | reverse | revenue | 2 |
| line-2 | line-2-0429-0379-s012541 | station | forward | revenue | 1 |
| line-2 | line-2-0429-0379-s012541 | station | reverse | revenue | 1 |
| line-2 | line-2-0538-0456-s009039 | station | forward | revenue | 1 |
| line-2 | line-2-0538-0456-s009039 | station | reverse | revenue | 1 |
| line-2 | line-2-0553-0551-s006198 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0551-s006198 | station | reverse | revenue | 1 |
| line-2 | line-2-0646-0515-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0646-0515-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0772-0532-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0379-0667-s013629 | station | reverse | revenue | 2 |
| line-3 | line-3-0491-0620-s011000 | station | forward | revenue | 1 |
| line-3 | line-3-0491-0620-s011000 | station | reverse | revenue | 1 |
| line-3 | line-3-0553-0551-s008371 | station | forward | revenue | 1 |
| line-3 | line-3-0553-0551-s008371 | station | reverse | revenue | 1 |
| line-3 | line-3-0678-0597-s004831 | station | forward | revenue | 1 |
| line-3 | line-3-0678-0597-s004831 | station | reverse | revenue | 1 |
| line-3 | line-3-0903-0571-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0113-0058-s021649 | depot | — | revenue | 16 |
| line-1 | line-2-0113-0058-s021649 | depot | — | spare | 2 |
| line-1 | line-2-0113-0058-s021649 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0113-0058-s021649 | depot | — | revenue | 29 |
| line-2 | line-2-0113-0058-s021649 | depot | — | spare | 4 |
| line-2 | line-2-0113-0058-s021649 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0113-0058-s021649 | depot | — | revenue | 16 |
| line-3 | line-2-0113-0058-s021649 | depot | — | spare | 2 |
| line-3 | line-2-0113-0058-s021649 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (19 trains), line-3 (19 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **106 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **95 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **72 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0398-0570-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0491-0549-s002690 | forward | revenue | 3 | pending |
| line-1 | line-1-0491-0549-s002690 | reverse | revenue | 3 | pending |
| line-1 | line-1-0553-0551-s004791 | forward | revenue | 3 | pending |
| line-1 | line-1-0553-0551-s004791 | reverse | revenue | 3 | pending |
| line-1 | line-1-0618-0564-s006756 | forward | revenue | 3 | pending |
| line-1 | line-1-0618-0564-s006756 | reverse | revenue | 3 | pending |
| line-1 | line-1-0654-0488-s008708 | forward | revenue | 3 | pending |
| line-1 | line-1-0654-0488-s008708 | reverse | revenue | 2 | pending |
| line-1 | line-1-0806-0339-s014618 | reverse | revenue | 2 | pending |
| line-1 | line-1-0654-0488-s008708 | reverse | spare | 1 | pending |
| line-1 | line-1-0806-0339-s014618 | reverse | spare | 1 | pending |
| line-1 | line-1-0398-0570-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0772-0532-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0646-0515-s003006 | forward | revenue | 4 | pending |
| line-2 | line-2-0646-0515-s003006 | reverse | revenue | 4 | pending |
| line-2 | line-2-0553-0551-s006198 | forward | revenue | 4 | pending |
| line-2 | line-2-0553-0551-s006198 | reverse | revenue | 4 | pending |
| line-2 | line-2-0538-0456-s009039 | forward | revenue | 4 | pending |
| line-2 | line-2-0538-0456-s009039 | reverse | revenue | 4 | pending |
| line-2 | line-2-0429-0379-s012541 | forward | revenue | 4 | pending |
| line-2 | line-2-0429-0379-s012541 | reverse | revenue | 4 | pending |
| line-2 | line-2-0113-0058-s021649 | reverse | revenue | 4 | pending |
| line-2 | line-2-0646-0515-s003006 | forward | spare | 1 | pending |
| line-2 | line-2-0646-0515-s003006 | reverse | spare | 1 | pending |
| line-2 | line-2-0553-0551-s006198 | forward | spare | 1 | pending |
| line-2 | line-2-0553-0551-s006198 | reverse | spare | 1 | pending |
| line-2 | line-2-0538-0456-s009039 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0903-0571-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0678-0597-s004831 | forward | revenue | 4 | pending |
| line-3 | line-3-0678-0597-s004831 | reverse | revenue | 3 | pending |
| line-3 | line-3-0553-0551-s008371 | forward | revenue | 3 | pending |
| line-3 | line-3-0553-0551-s008371 | reverse | revenue | 3 | pending |
| line-3 | line-3-0491-0620-s011000 | forward | revenue | 3 | pending |
| line-3 | line-3-0491-0620-s011000 | reverse | revenue | 3 | pending |
| line-3 | line-3-0379-0667-s013629 | reverse | revenue | 3 | pending |
| line-3 | line-3-0678-0597-s004831 | reverse | spare | 1 | pending |
| line-3 | line-3-0553-0551-s008371 | forward | spare | 1 | pending |
| line-3 | line-3-0553-0551-s008371 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**62 trainsets exceed the reference platform envelope**, requiring **3,689.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0398-0570-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0491-0549-s002690 | 6 | 2 | 4 | 238.0 |
| line-1-0553-0551-s004791 | 6 | 4 | 2 | 119.0 |
| line-1-0618-0564-s006756 | 6 | 2 | 4 | 238.0 |
| line-1-0654-0488-s008708 | 6 | 4 | 2 | 119.0 |
| line-1-0806-0339-s014618 | 3 | 2 | 1 | 59.5 |
| line-2-0113-0058-s021649 | 4 | 2 | 2 | 119.0 |
| line-2-0429-0379-s012541 | 8 | 2 | 6 | 357.0 |
| line-2-0538-0456-s009039 | 9 | 2 | 7 | 416.5 |
| line-2-0553-0551-s006198 | 10 | 4 | 6 | 357.0 |
| line-2-0646-0515-s003006 | 10 | 4 | 6 | 357.0 |
| line-2-0772-0532-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0379-0667-s013629 | 3 | 2 | 1 | 59.5 |
| line-3-0491-0620-s011000 | 6 | 2 | 4 | 238.0 |
| line-3-0553-0551-s008371 | 8 | 4 | 4 | 238.0 |
| line-3-0678-0597-s004831 | 8 | 2 | 6 | 357.0 |
| line-3-0903-0571-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Ibb/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
