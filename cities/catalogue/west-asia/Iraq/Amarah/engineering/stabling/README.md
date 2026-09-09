# Station and depot overnight allocation

Plan: **34 trainsets at stations + 67 at depots = 101 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-1131-0749-s021569 | 67 | 3,986.5 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0313-0285-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0415-0371-s003008 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0371-s003008 | station | reverse | revenue | 1 |
| line-1 | line-1-0499-0487-s006024 | station | forward | revenue | 1 |
| line-1 | line-1-0499-0487-s006024 | station | reverse | revenue | 1 |
| line-1 | line-1-0584-0534-s008187 | station | forward | revenue | 1 |
| line-1 | line-1-0584-0534-s008187 | station | reverse | revenue | 1 |
| line-1 | line-1-0665-0508-s010112 | station | forward | revenue | 1 |
| line-1 | line-1-0665-0508-s010112 | station | reverse | revenue | 1 |
| line-1 | line-1-0734-0557-s012026 | station | forward | revenue | 1 |
| line-1 | line-1-0734-0557-s012026 | station | reverse | revenue | 1 |
| line-1 | line-1-1131-0749-s021569 | station | reverse | revenue | 2 |
| line-2 | line-2-0329-0543-s013016 | station | reverse | revenue | 2 |
| line-2 | line-2-0410-0512-s011023 | station | forward | revenue | 1 |
| line-2 | line-2-0410-0512-s011023 | station | reverse | revenue | 1 |
| line-2 | line-2-0475-0544-s009031 | station | forward | revenue | 1 |
| line-2 | line-2-0475-0544-s009031 | station | reverse | revenue | 1 |
| line-2 | line-2-0584-0534-s006602 | station | forward | revenue | 1 |
| line-2 | line-2-0584-0534-s006602 | station | reverse | revenue | 1 |
| line-2 | line-2-0678-0455-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0678-0455-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0709-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0522-0453-s006039 | station | forward | revenue | 1 |
| line-3 | line-3-0522-0453-s006039 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0186-s012012 | station | reverse | revenue | 2 |
| line-3 | line-3-0584-0534-s003530 | station | forward | revenue | 1 |
| line-3 | line-3-0584-0534-s003530 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0658-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1131-0749-s021569 | depot | — | revenue | 28 |
| line-1 | line-1-1131-0749-s021569 | depot | — | spare | 4 |
| line-1 | line-1-1131-0749-s021569 | depot | — | cold_reserve | 1 |
| line-2 | line-1-1131-0749-s021569 | depot | — | revenue | 13 |
| line-2 | line-1-1131-0749-s021569 | depot | — | spare | 2 |
| line-2 | line-1-1131-0749-s021569 | depot | — | cold_reserve | 1 |
| line-3 | line-1-1131-0749-s021569 | depot | — | revenue | 15 |
| line-3 | line-1-1131-0749-s021569 | depot | — | spare | 2 |
| line-3 | line-1-1131-0749-s021569 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (16 trains), line-3 (18 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **101 trainsets at 17 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **90 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **67 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0313-0285-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0415-0371-s003008 | forward | revenue | 4 | pending |
| line-1 | line-1-0415-0371-s003008 | reverse | revenue | 4 | pending |
| line-1 | line-1-0499-0487-s006024 | forward | revenue | 4 | pending |
| line-1 | line-1-0499-0487-s006024 | reverse | revenue | 4 | pending |
| line-1 | line-1-0584-0534-s008187 | forward | revenue | 4 | pending |
| line-1 | line-1-0584-0534-s008187 | reverse | revenue | 3 | pending |
| line-1 | line-1-0665-0508-s010112 | forward | revenue | 3 | pending |
| line-1 | line-1-0665-0508-s010112 | reverse | revenue | 3 | pending |
| line-1 | line-1-0734-0557-s012026 | forward | revenue | 3 | pending |
| line-1 | line-1-0734-0557-s012026 | reverse | revenue | 3 | pending |
| line-1 | line-1-1131-0749-s021569 | reverse | revenue | 3 | pending |
| line-1 | line-1-0584-0534-s008187 | reverse | spare | 1 | pending |
| line-1 | line-1-0665-0508-s010112 | forward | spare | 1 | pending |
| line-1 | line-1-0665-0508-s010112 | reverse | spare | 1 | pending |
| line-1 | line-1-0734-0557-s012026 | forward | spare | 1 | pending |
| line-1 | line-1-0734-0557-s012026 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0709-0317-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0678-0455-s003017 | forward | revenue | 3 | pending |
| line-2 | line-2-0678-0455-s003017 | reverse | revenue | 3 | pending |
| line-2 | line-2-0584-0534-s006602 | forward | revenue | 3 | pending |
| line-2 | line-2-0584-0534-s006602 | reverse | revenue | 3 | pending |
| line-2 | line-2-0475-0544-s009031 | forward | revenue | 2 | pending |
| line-2 | line-2-0475-0544-s009031 | reverse | revenue | 2 | pending |
| line-2 | line-2-0410-0512-s011023 | forward | revenue | 2 | pending |
| line-2 | line-2-0410-0512-s011023 | reverse | revenue | 2 | pending |
| line-2 | line-2-0329-0543-s013016 | reverse | revenue | 2 | pending |
| line-2 | line-2-0475-0544-s009031 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0544-s009031 | reverse | spare | 1 | pending |
| line-2 | line-2-0410-0512-s011023 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0584-0534-s003530 | forward | revenue | 4 | pending |
| line-3 | line-3-0584-0534-s003530 | reverse | revenue | 4 | pending |
| line-3 | line-3-0522-0453-s006039 | forward | revenue | 4 | pending |
| line-3 | line-3-0522-0453-s006039 | reverse | revenue | 4 | pending |
| line-3 | line-3-0539-0186-s012012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0539-0186-s012012 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0584-0534-s003530 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**61 trainsets exceed the reference platform envelope**, requiring **3,629.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0313-0285-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0415-0371-s003008 | 8 | 2 | 6 | 357.0 |
| line-1-0499-0487-s006024 | 8 | 2 | 6 | 357.0 |
| line-1-0584-0534-s008187 | 8 | 4 | 4 | 238.0 |
| line-1-0665-0508-s010112 | 8 | 2 | 6 | 357.0 |
| line-1-0734-0557-s012026 | 8 | 2 | 6 | 357.0 |
| line-1-1131-0749-s021569 | 3 | 2 | 1 | 59.5 |
| line-2-0329-0543-s013016 | 2 | 2 | 0 | 0.0 |
| line-2-0410-0512-s011023 | 5 | 2 | 3 | 178.5 |
| line-2-0475-0544-s009031 | 6 | 2 | 4 | 238.0 |
| line-2-0584-0534-s006602 | 6 | 4 | 2 | 119.0 |
| line-2-0678-0455-s003017 | 6 | 2 | 4 | 238.0 |
| line-2-0709-0317-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0522-0453-s006039 | 8 | 2 | 6 | 357.0 |
| line-3-0539-0186-s012012 | 4 | 2 | 2 | 119.0 |
| line-3-0584-0534-s003530 | 9 | 4 | 5 | 297.5 |
| line-3-0667-0658-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Amarah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
