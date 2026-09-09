# Station and depot overnight allocation

Plan: **30 trainsets at stations + 132 at depots = 162 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0480-0214-s024352 | 132 | 7,854.0 | 25 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0415-0467-s007643 | station | reverse | revenue | 2 |
| line-1 | line-1-0539-0559-s003931 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0559-s003931 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0623-s001974 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0623-s001974 | station | reverse | revenue | 1 |
| line-1 | line-1-0660-0667-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0070-1066-s019747 | station | reverse | revenue | 2 |
| line-2 | line-2-0451-0605-s004952 | station | forward | revenue | 1 |
| line-2 | line-2-0451-0605-s004952 | station | reverse | revenue | 1 |
| line-2 | line-2-0458-0734-s008451 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0734-s008451 | station | reverse | revenue | 1 |
| line-2 | line-2-0539-0559-s002524 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0559-s002524 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0462-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0214-s024352 | station | reverse | revenue | 2 |
| line-3 | line-3-0533-0470-s018058 | station | forward | revenue | 1 |
| line-3 | line-3-0533-0470-s018058 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0559-s015806 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0559-s015806 | station | reverse | revenue | 1 |
| line-3 | line-3-0556-0621-s013918 | station | forward | revenue | 1 |
| line-3 | line-3-0556-0621-s013918 | station | reverse | revenue | 1 |
| line-3 | line-3-0623-0679-s012022 | station | forward | revenue | 1 |
| line-3 | line-3-0623-0679-s012022 | station | reverse | revenue | 1 |
| line-3 | line-3-1023-1006-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0480-0214-s024352 | depot | — | revenue | 15 |
| line-1 | line-3-0480-0214-s024352 | depot | — | spare | 2 |
| line-1 | line-3-0480-0214-s024352 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0480-0214-s024352 | depot | — | revenue | 46 |
| line-2 | line-3-0480-0214-s024352 | depot | — | spare | 5 |
| line-2 | line-3-0480-0214-s024352 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0480-0214-s024352 | depot | — | revenue | 55 |
| line-3 | line-3-0480-0214-s024352 | depot | — | spare | 6 |
| line-3 | line-3-0480-0214-s024352 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (18 trains), line-2 (52 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **162 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **146 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **132 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0660-0667-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0606-0623-s001974 | forward | revenue | 4 | pending |
| line-1 | line-1-0606-0623-s001974 | reverse | revenue | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0467-s007643 | reverse | revenue | 3 | pending |
| line-1 | line-1-0415-0467-s007643 | reverse | spare | 1 | pending |
| line-1 | line-1-0660-0667-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0606-0623-s001974 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0539-0559-s002524 | forward | revenue | 7 | pending |
| line-2 | line-2-0539-0559-s002524 | reverse | revenue | 7 | pending |
| line-2 | line-2-0451-0605-s004952 | forward | revenue | 7 | pending |
| line-2 | line-2-0451-0605-s004952 | reverse | revenue | 7 | pending |
| line-2 | line-2-0458-0734-s008451 | forward | revenue | 7 | pending |
| line-2 | line-2-0458-0734-s008451 | reverse | revenue | 7 | pending |
| line-2 | line-2-0070-1066-s019747 | reverse | revenue | 7 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0559-s002524 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0559-s002524 | reverse | spare | 1 | pending |
| line-2 | line-2-0451-0605-s004952 | forward | spare | 1 | pending |
| line-2 | line-2-0451-0605-s004952 | reverse | spare | 1 | pending |
| line-2 | line-2-0458-0734-s008451 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0623-0679-s012022 | forward | revenue | 7 | pending |
| line-3 | line-3-0623-0679-s012022 | reverse | revenue | 7 | pending |
| line-3 | line-3-0556-0621-s013918 | forward | revenue | 7 | pending |
| line-3 | line-3-0556-0621-s013918 | reverse | revenue | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | forward | revenue | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | reverse | revenue | 7 | pending |
| line-3 | line-3-0533-0470-s018058 | forward | revenue | 6 | pending |
| line-3 | line-3-0533-0470-s018058 | reverse | revenue | 6 | pending |
| line-3 | line-3-0480-0214-s024352 | reverse | revenue | 6 | pending |
| line-3 | line-3-0533-0470-s018058 | forward | spare | 1 | pending |
| line-3 | line-3-0533-0470-s018058 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0214-s024352 | reverse | spare | 1 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0679-s012022 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0679-s012022 | reverse | spare | 1 | pending |
| line-3 | line-3-0556-0621-s013918 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**124 trainsets exceed the reference platform envelope**, requiring **7,378.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0415-0467-s007643 | 4 | 2 | 2 | 119.0 |
| line-1-0539-0559-s003931 | 8 | 4 | 4 | 238.0 |
| line-1-0606-0623-s001974 | 9 | 2 | 7 | 416.5 |
| line-1-0660-0667-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0070-1066-s019747 | 7 | 2 | 5 | 297.5 |
| line-2-0451-0605-s004952 | 16 | 2 | 14 | 833.0 |
| line-2-0458-0734-s008451 | 15 | 2 | 13 | 773.5 |
| line-2-0539-0559-s002524 | 16 | 4 | 12 | 714.0 |
| line-2-0565-0462-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0480-0214-s024352 | 7 | 2 | 5 | 297.5 |
| line-3-0533-0470-s018058 | 14 | 4 | 10 | 595.0 |
| line-3-0539-0559-s015806 | 14 | 4 | 10 | 595.0 |
| line-3-0556-0621-s013918 | 15 | 2 | 13 | 773.5 |
| line-3-0623-0679-s012022 | 16 | 2 | 14 | 833.0 |
| line-3-1023-1006-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Asyut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
