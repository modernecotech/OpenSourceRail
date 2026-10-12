# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 160 at depots = 196 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0660-0667-s000000 | line-1 | declared-depot | 16 | 952.0 | 4 |
| line-2-0565-0462-s000000 | line-2 | declared-depot | 47 | 2,796.5 | 8 |
| line-3-0480-0214-s026355 | line-3 | declared-depot | 68 | 4,046.0 | 11 |
| line-4-0435-0662-s000000 | line-4 | declared-depot | 29 | 1,725.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0415-0467-s007049 | station | reverse | revenue | 2 |
| line-1 | line-1-0511-0545-s004295 | station | forward | revenue | 1 |
| line-1 | line-1-0511-0545-s004295 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0568-s003500 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0568-s003500 | station | reverse | revenue | 1 |
| line-1 | line-1-0660-0667-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0070-1066-s017868 | station | reverse | revenue | 2 |
| line-2 | line-2-0435-0662-s005335 | station | forward | revenue | 1 |
| line-2 | line-2-0435-0662-s005335 | station | reverse | revenue | 1 |
| line-2 | line-2-0511-0545-s002213 | station | forward | revenue | 1 |
| line-2 | line-2-0511-0545-s002213 | station | reverse | revenue | 1 |
| line-2 | line-2-0534-0511-s001284 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0511-s001284 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0462-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0214-s026355 | station | reverse | revenue | 2 |
| line-3 | line-3-0510-0431-s020367 | station | forward | revenue | 1 |
| line-3 | line-3-0510-0431-s020367 | station | reverse | revenue | 1 |
| line-3 | line-3-0534-0511-s018018 | station | forward | revenue | 1 |
| line-3 | line-3-0534-0511-s018018 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0568-s016484 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0568-s016484 | station | reverse | revenue | 1 |
| line-3 | line-3-0615-0671-s012963 | station | forward | revenue | 1 |
| line-3 | line-3-0615-0671-s012963 | station | reverse | revenue | 1 |
| line-3 | line-3-1023-1006-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0062-0386-s010420 | station | reverse | revenue | 2 |
| line-4 | line-4-0364-0611-s001882 | station | forward | revenue | 1 |
| line-4 | line-4-0364-0611-s001882 | station | reverse | revenue | 1 |
| line-4 | line-4-0435-0662-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0660-0667-s000000 | depot | — | revenue | 13 |
| line-1 | line-1-0660-0667-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0660-0667-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0565-0462-s000000 | depot | — | revenue | 41 |
| line-2 | line-2-0565-0462-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0565-0462-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0480-0214-s026355 | depot | — | revenue | 60 |
| line-3 | line-3-0480-0214-s026355 | depot | — | spare | 7 |
| line-3 | line-3-0480-0214-s026355 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0435-0662-s000000 | depot | — | revenue | 25 |
| line-4 | line-4-0435-0662-s000000 | depot | — | spare | 3 |
| line-4 | line-4-0435-0662-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/asyut-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **196 trainsets at 18 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **175 revenue, 17 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **160 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0660-0667-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0568-s003500 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0568-s003500 | reverse | revenue | 4 | pending |
| line-1 | line-1-0511-0545-s004295 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0545-s004295 | reverse | revenue | 3 | pending |
| line-1 | line-1-0415-0467-s007049 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0545-s004295 | forward | spare | 1 | pending |
| line-1 | line-1-0511-0545-s004295 | reverse | spare | 1 | pending |
| line-1 | line-1-0415-0467-s007049 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0534-0511-s001284 | forward | revenue | 7 | pending |
| line-2 | line-2-0534-0511-s001284 | reverse | revenue | 7 | pending |
| line-2 | line-2-0511-0545-s002213 | forward | revenue | 6 | pending |
| line-2 | line-2-0511-0545-s002213 | reverse | revenue | 6 | pending |
| line-2 | line-2-0435-0662-s005335 | forward | revenue | 6 | pending |
| line-2 | line-2-0435-0662-s005335 | reverse | revenue | 6 | pending |
| line-2 | line-2-0070-1066-s017868 | reverse | revenue | 6 | pending |
| line-2 | line-2-0511-0545-s002213 | forward | spare | 1 | pending |
| line-2 | line-2-0511-0545-s002213 | reverse | spare | 1 | pending |
| line-2 | line-2-0435-0662-s005335 | forward | spare | 1 | pending |
| line-2 | line-2-0435-0662-s005335 | reverse | spare | 1 | pending |
| line-2 | line-2-0070-1066-s017868 | reverse | spare | 1 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0615-0671-s012963 | forward | revenue | 8 | pending |
| line-3 | line-3-0615-0671-s012963 | reverse | revenue | 7 | pending |
| line-3 | line-3-0539-0568-s016484 | forward | revenue | 7 | pending |
| line-3 | line-3-0539-0568-s016484 | reverse | revenue | 7 | pending |
| line-3 | line-3-0534-0511-s018018 | forward | revenue | 7 | pending |
| line-3 | line-3-0534-0511-s018018 | reverse | revenue | 7 | pending |
| line-3 | line-3-0510-0431-s020367 | forward | revenue | 7 | pending |
| line-3 | line-3-0510-0431-s020367 | reverse | revenue | 7 | pending |
| line-3 | line-3-0480-0214-s026355 | reverse | revenue | 7 | pending |
| line-3 | line-3-0615-0671-s012963 | reverse | spare | 1 | pending |
| line-3 | line-3-0539-0568-s016484 | forward | spare | 1 | pending |
| line-3 | line-3-0539-0568-s016484 | reverse | spare | 1 | pending |
| line-3 | line-3-0534-0511-s018018 | forward | spare | 1 | pending |
| line-3 | line-3-0534-0511-s018018 | reverse | spare | 1 | pending |
| line-3 | line-3-0510-0431-s020367 | forward | spare | 1 | pending |
| line-3 | line-3-0510-0431-s020367 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0214-s026355 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0435-0662-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0364-0611-s001882 | forward | revenue | 8 | pending |
| line-4 | line-4-0364-0611-s001882 | reverse | revenue | 8 | pending |
| line-4 | line-4-0062-0386-s010420 | reverse | revenue | 7 | pending |
| line-4 | line-4-0062-0386-s010420 | reverse | spare | 1 | pending |
| line-4 | line-4-0435-0662-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0364-0611-s001882 | forward | spare | 1 | pending |
| line-4 | line-4-0364-0611-s001882 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**146 trainsets exceed the reference platform envelope**, requiring **8,687.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0415-0467-s007049 | 4 | 2 | 2 | 119.0 |
| line-1-0511-0545-s004295 | 8 | 4 | 4 | 238.0 |
| line-1-0539-0568-s003500 | 8 | 4 | 4 | 238.0 |
| line-1-0660-0667-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0070-1066-s017868 | 7 | 2 | 5 | 297.5 |
| line-2-0435-0662-s005335 | 14 | 4 | 10 | 595.0 |
| line-2-0511-0545-s002213 | 14 | 4 | 10 | 595.0 |
| line-2-0534-0511-s001284 | 14 | 4 | 10 | 595.0 |
| line-2-0565-0462-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0480-0214-s026355 | 8 | 2 | 6 | 357.0 |
| line-3-0510-0431-s020367 | 16 | 2 | 14 | 833.0 |
| line-3-0534-0511-s018018 | 16 | 4 | 12 | 714.0 |
| line-3-0539-0568-s016484 | 16 | 4 | 12 | 714.0 |
| line-3-0615-0671-s012963 | 16 | 2 | 14 | 833.0 |
| line-3-1023-1006-s000000 | 8 | 2 | 6 | 357.0 |
| line-4-0062-0386-s010420 | 8 | 2 | 6 | 357.0 |
| line-4-0364-0611-s001882 | 18 | 2 | 16 | 952.0 |
| line-4-0435-0662-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Asyut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
