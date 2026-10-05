# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 142 at depots = 172 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0724-0363-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0122-0216-s026064 | line-2 | declared-depot | 70 | 4,165.0 | 12 |
| line-3-0550-0083-s000000 | line-3 | declared-depot | 44 | 2,618.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0429-0827-s012274 | station | reverse | revenue | 2 |
| line-1 | line-1-0495-0723-s009507 | station | forward | revenue | 1 |
| line-1 | line-1-0495-0723-s009507 | station | reverse | revenue | 1 |
| line-1 | line-1-0563-0617-s006730 | station | forward | revenue | 1 |
| line-1 | line-1-0563-0617-s006730 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0492-s003447 | station | forward | revenue | 1 |
| line-1 | line-1-0642-0492-s003447 | station | reverse | revenue | 1 |
| line-1 | line-1-0724-0363-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0122-0216-s026064 | station | reverse | revenue | 2 |
| line-2 | line-2-0435-0503-s016904 | station | forward | revenue | 1 |
| line-2 | line-2-0435-0503-s016904 | station | reverse | revenue | 1 |
| line-2 | line-2-0498-0560-s014970 | station | forward | revenue | 1 |
| line-2 | line-2-0498-0560-s014970 | station | reverse | revenue | 1 |
| line-2 | line-2-0563-0617-s013034 | station | forward | revenue | 1 |
| line-2 | line-2-0563-0617-s013034 | station | reverse | revenue | 1 |
| line-2 | line-2-0639-0685-s010739 | station | forward | revenue | 1 |
| line-2 | line-2-0639-0685-s010739 | station | reverse | revenue | 1 |
| line-2 | line-2-1012-0957-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0320-0751-s016375 | station | reverse | revenue | 2 |
| line-3 | line-3-0435-0503-s010328 | station | forward | revenue | 1 |
| line-3 | line-3-0435-0503-s010328 | station | reverse | revenue | 1 |
| line-3 | line-3-0498-0366-s007001 | station | forward | revenue | 1 |
| line-3 | line-3-0498-0366-s007001 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0083-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0724-0363-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0724-0363-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0724-0363-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0122-0216-s026064 | depot | — | revenue | 62 |
| line-2 | line-2-0122-0216-s026064 | depot | — | spare | 7 |
| line-2 | line-2-0122-0216-s026064 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0550-0083-s000000 | depot | — | revenue | 39 |
| line-3 | line-3-0550-0083-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0550-0083-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/gulu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **172 trainsets at 15 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **155 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **142 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0724-0363-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0642-0492-s003447 | forward | revenue | 5 | pending |
| line-1 | line-1-0642-0492-s003447 | reverse | revenue | 4 | pending |
| line-1 | line-1-0563-0617-s006730 | forward | revenue | 4 | pending |
| line-1 | line-1-0563-0617-s006730 | reverse | revenue | 4 | pending |
| line-1 | line-1-0495-0723-s009507 | forward | revenue | 4 | pending |
| line-1 | line-1-0495-0723-s009507 | reverse | revenue | 4 | pending |
| line-1 | line-1-0429-0827-s012274 | reverse | revenue | 4 | pending |
| line-1 | line-1-0642-0492-s003447 | reverse | spare | 1 | pending |
| line-1 | line-1-0563-0617-s006730 | forward | spare | 1 | pending |
| line-1 | line-1-0563-0617-s006730 | reverse | spare | 1 | pending |
| line-1 | line-1-0495-0723-s009507 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1012-0957-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0639-0685-s010739 | forward | revenue | 8 | pending |
| line-2 | line-2-0639-0685-s010739 | reverse | revenue | 8 | pending |
| line-2 | line-2-0563-0617-s013034 | forward | revenue | 8 | pending |
| line-2 | line-2-0563-0617-s013034 | reverse | revenue | 7 | pending |
| line-2 | line-2-0498-0560-s014970 | forward | revenue | 7 | pending |
| line-2 | line-2-0498-0560-s014970 | reverse | revenue | 7 | pending |
| line-2 | line-2-0435-0503-s016904 | forward | revenue | 7 | pending |
| line-2 | line-2-0435-0503-s016904 | reverse | revenue | 7 | pending |
| line-2 | line-2-0122-0216-s026064 | reverse | revenue | 7 | pending |
| line-2 | line-2-0563-0617-s013034 | reverse | spare | 1 | pending |
| line-2 | line-2-0498-0560-s014970 | forward | spare | 1 | pending |
| line-2 | line-2-0498-0560-s014970 | reverse | spare | 1 | pending |
| line-2 | line-2-0435-0503-s016904 | forward | spare | 1 | pending |
| line-2 | line-2-0435-0503-s016904 | reverse | spare | 1 | pending |
| line-2 | line-2-0122-0216-s026064 | reverse | spare | 1 | pending |
| line-2 | line-2-1012-0957-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0639-0685-s010739 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0550-0083-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0498-0366-s007001 | forward | revenue | 8 | pending |
| line-3 | line-3-0498-0366-s007001 | reverse | revenue | 8 | pending |
| line-3 | line-3-0435-0503-s010328 | forward | revenue | 8 | pending |
| line-3 | line-3-0435-0503-s010328 | reverse | revenue | 8 | pending |
| line-3 | line-3-0320-0751-s016375 | reverse | revenue | 7 | pending |
| line-3 | line-3-0320-0751-s016375 | reverse | spare | 1 | pending |
| line-3 | line-3-0550-0083-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0498-0366-s007001 | forward | spare | 1 | pending |
| line-3 | line-3-0498-0366-s007001 | reverse | spare | 1 | pending |
| line-3 | line-3-0435-0503-s010328 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**134 trainsets exceed the reference platform envelope**, requiring **7,973.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0429-0827-s012274 | 4 | 2 | 2 | 119.0 |
| line-1-0495-0723-s009507 | 9 | 2 | 7 | 416.5 |
| line-1-0563-0617-s006730 | 10 | 4 | 6 | 357.0 |
| line-1-0642-0492-s003447 | 10 | 2 | 8 | 476.0 |
| line-1-0724-0363-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0122-0216-s026064 | 8 | 2 | 6 | 357.0 |
| line-2-0435-0503-s016904 | 16 | 4 | 12 | 714.0 |
| line-2-0498-0560-s014970 | 16 | 2 | 14 | 833.0 |
| line-2-0563-0617-s013034 | 16 | 4 | 12 | 714.0 |
| line-2-0639-0685-s010739 | 17 | 2 | 15 | 892.5 |
| line-2-1012-0957-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0320-0751-s016375 | 8 | 2 | 6 | 357.0 |
| line-3-0435-0503-s010328 | 17 | 4 | 13 | 773.5 |
| line-3-0498-0366-s007001 | 18 | 2 | 16 | 952.0 |
| line-3-0550-0083-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Gulu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
