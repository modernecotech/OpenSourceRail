# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 137 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1131-0749-s024556 | line-1 | declared-depot | 64 | 3,808.0 | 11 |
| line-2-0709-0317-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0667-0658-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |
| line-4-0543-0520-s000000 | line-4 | declared-depot | 10 | 595.0 | 2 |
| line-5-0666-0343-s000000 | line-5 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0313-0285-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0477-0455-s005689 | station | forward | revenue | 1 |
| line-1 | line-1-0477-0455-s005689 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0520-s007960 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0520-s007960 | station | reverse | revenue | 1 |
| line-1 | line-1-0625-0511-s010165 | station | forward | revenue | 1 |
| line-1 | line-1-0625-0511-s010165 | station | reverse | revenue | 1 |
| line-1 | line-1-0699-0538-s012188 | station | forward | revenue | 1 |
| line-1 | line-1-0699-0538-s012188 | station | reverse | revenue | 1 |
| line-1 | line-1-1131-0749-s024556 | station | reverse | revenue | 2 |
| line-2 | line-2-0329-0543-s009847 | station | reverse | revenue | 2 |
| line-2 | line-2-0477-0455-s006018 | station | forward | revenue | 1 |
| line-2 | line-2-0477-0455-s006018 | station | reverse | revenue | 1 |
| line-2 | line-2-0592-0386-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0592-0386-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0666-0343-s001111 | station | forward | revenue | 1 |
| line-2 | line-2-0666-0343-s001111 | station | reverse | revenue | 1 |
| line-2 | line-2-0709-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0539-0186-s010547 | station | reverse | revenue | 2 |
| line-3 | line-3-0590-0388-s006073 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0388-s006073 | station | reverse | revenue | 1 |
| line-3 | line-3-0625-0511-s003300 | station | forward | revenue | 1 |
| line-3 | line-3-0625-0511-s003300 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0658-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0407-0598-s004214 | station | reverse | revenue | 2 |
| line-4 | line-4-0543-0520-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0666-0343-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0686-0563-s006105 | station | reverse | revenue | 2 |
| line-5 | line-5-0699-0538-s005485 | station | forward | revenue | 1 |
| line-5 | line-5-0699-0538-s005485 | station | reverse | revenue | 1 |
| line-1 | line-1-1131-0749-s024556 | depot | — | revenue | 57 |
| line-1 | line-1-1131-0749-s024556 | depot | — | spare | 6 |
| line-1 | line-1-1131-0749-s024556 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0709-0317-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0709-0317-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0709-0317-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0667-0658-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0667-0658-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0667-0658-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0543-0520-s000000 | depot | — | revenue | 8 |
| line-4 | line-4-0543-0520-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0543-0520-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0666-0343-s000000 | depot | — | revenue | 12 |
| line-5 | line-5-0666-0343-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0666-0343-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/amarah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 20 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 13 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **137 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0313-0285-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0477-0455-s005689 | forward | revenue | 7 | pending |
| line-1 | line-1-0477-0455-s005689 | reverse | revenue | 7 | pending |
| line-1 | line-1-0543-0520-s007960 | forward | revenue | 7 | pending |
| line-1 | line-1-0543-0520-s007960 | reverse | revenue | 7 | pending |
| line-1 | line-1-0625-0511-s010165 | forward | revenue | 7 | pending |
| line-1 | line-1-0625-0511-s010165 | reverse | revenue | 7 | pending |
| line-1 | line-1-0699-0538-s012188 | forward | revenue | 7 | pending |
| line-1 | line-1-0699-0538-s012188 | reverse | revenue | 7 | pending |
| line-1 | line-1-1131-0749-s024556 | reverse | revenue | 6 | pending |
| line-1 | line-1-1131-0749-s024556 | reverse | spare | 1 | pending |
| line-1 | line-1-0313-0285-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0477-0455-s005689 | forward | spare | 1 | pending |
| line-1 | line-1-0477-0455-s005689 | reverse | spare | 1 | pending |
| line-1 | line-1-0543-0520-s007960 | forward | spare | 1 | pending |
| line-1 | line-1-0543-0520-s007960 | reverse | spare | 1 | pending |
| line-1 | line-1-0625-0511-s010165 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0709-0317-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0666-0343-s001111 | forward | revenue | 4 | pending |
| line-2 | line-2-0666-0343-s001111 | reverse | revenue | 4 | pending |
| line-2 | line-2-0592-0386-s003017 | forward | revenue | 4 | pending |
| line-2 | line-2-0592-0386-s003017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0477-0455-s006018 | forward | revenue | 3 | pending |
| line-2 | line-2-0477-0455-s006018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0329-0543-s009847 | reverse | revenue | 3 | pending |
| line-2 | line-2-0477-0455-s006018 | forward | spare | 1 | pending |
| line-2 | line-2-0477-0455-s006018 | reverse | spare | 1 | pending |
| line-2 | line-2-0329-0543-s009847 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0625-0511-s003300 | forward | revenue | 5 | pending |
| line-3 | line-3-0625-0511-s003300 | reverse | revenue | 5 | pending |
| line-3 | line-3-0590-0388-s006073 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0388-s006073 | reverse | revenue | 5 | pending |
| line-3 | line-3-0539-0186-s010547 | reverse | revenue | 5 | pending |
| line-3 | line-3-0625-0511-s003300 | forward | spare | 1 | pending |
| line-3 | line-3-0625-0511-s003300 | reverse | spare | 1 | pending |
| line-3 | line-3-0590-0388-s006073 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0388-s006073 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0543-0520-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0407-0598-s004214 | reverse | revenue | 6 | pending |
| line-4 | line-4-0543-0520-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0407-0598-s004214 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0666-0343-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-0699-0538-s005485 | forward | revenue | 5 | pending |
| line-5 | line-5-0699-0538-s005485 | reverse | revenue | 4 | pending |
| line-5 | line-5-0686-0563-s006105 | reverse | revenue | 4 | pending |
| line-5 | line-5-0699-0538-s005485 | reverse | spare | 1 | pending |
| line-5 | line-5-0686-0563-s006105 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**117 trainsets exceed the reference platform envelope**, requiring **6,961.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0313-0285-s000000 | 8 | 2 | 6 | 357.0 |
| line-1-0477-0455-s005689 | 16 | 4 | 12 | 714.0 |
| line-1-0543-0520-s007960 | 16 | 4 | 12 | 714.0 |
| line-1-0625-0511-s010165 | 15 | 4 | 11 | 654.5 |
| line-1-0699-0538-s012188 | 14 | 4 | 10 | 595.0 |
| line-1-1131-0749-s024556 | 7 | 2 | 5 | 297.5 |
| line-2-0329-0543-s009847 | 4 | 2 | 2 | 119.0 |
| line-2-0477-0455-s006018 | 8 | 4 | 4 | 238.0 |
| line-2-0592-0386-s003017 | 8 | 4 | 4 | 238.0 |
| line-2-0666-0343-s001111 | 8 | 4 | 4 | 238.0 |
| line-2-0709-0317-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0539-0186-s010547 | 5 | 2 | 3 | 178.5 |
| line-3-0590-0388-s006073 | 12 | 4 | 8 | 476.0 |
| line-3-0625-0511-s003300 | 12 | 4 | 8 | 476.0 |
| line-3-0667-0658-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0407-0598-s004214 | 7 | 2 | 5 | 297.5 |
| line-4-0543-0520-s000000 | 7 | 2 | 5 | 297.5 |
| line-5-0666-0343-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0686-0563-s006105 | 5 | 2 | 3 | 178.5 |
| line-5-0699-0538-s005485 | 10 | 4 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Amarah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
