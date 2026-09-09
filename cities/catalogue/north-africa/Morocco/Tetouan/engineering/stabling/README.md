# Station and depot overnight allocation

Plan: **38 trainsets at stations + 77 at depots = 115 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0929-0303-s023236 | 77 | 4,581.5 | 18 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0316-0975-s018551 | station | reverse | revenue | 2 |
| line-1 | line-1-0382-0878-s015616 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0878-s015616 | station | reverse | revenue | 1 |
| line-1 | line-1-0434-0761-s012062 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0761-s012062 | station | reverse | revenue | 1 |
| line-1 | line-1-0458-0648-s009043 | station | forward | revenue | 1 |
| line-1 | line-1-0458-0648-s009043 | station | reverse | revenue | 1 |
| line-1 | line-1-0545-0562-s006168 | station | forward | revenue | 1 |
| line-1 | line-1-0545-0562-s006168 | station | reverse | revenue | 1 |
| line-1 | line-1-0572-0444-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0572-0444-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0584-0314-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0327-0929-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0513-0729-s006355 | station | forward | revenue | 1 |
| line-2 | line-2-0513-0729-s006355 | station | reverse | revenue | 1 |
| line-2 | line-2-0538-0619-s009378 | station | forward | revenue | 1 |
| line-2 | line-2-0538-0619-s009378 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0562-s011717 | station | forward | revenue | 1 |
| line-2 | line-2-0545-0562-s011717 | station | reverse | revenue | 1 |
| line-2 | line-2-0610-0519-s013994 | station | forward | revenue | 1 |
| line-2 | line-2-0610-0519-s013994 | station | reverse | revenue | 1 |
| line-2 | line-2-0639-0434-s016299 | station | forward | revenue | 1 |
| line-2 | line-2-0639-0434-s016299 | station | reverse | revenue | 1 |
| line-2 | line-2-0747-0414-s018625 | station | forward | revenue | 1 |
| line-2 | line-2-0747-0414-s018625 | station | reverse | revenue | 1 |
| line-2 | line-2-0929-0303-s023236 | station | reverse | revenue | 2 |
| line-3 | line-3-0393-0182-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0528-0407-s005752 | station | forward | revenue | 1 |
| line-3 | line-3-0528-0407-s005752 | station | reverse | revenue | 1 |
| line-3 | line-3-0545-0562-s009021 | station | forward | revenue | 1 |
| line-3 | line-3-0545-0562-s009021 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0656-s012267 | station | reverse | revenue | 2 |
| line-1 | line-2-0929-0303-s023236 | depot | — | revenue | 22 |
| line-1 | line-2-0929-0303-s023236 | depot | — | spare | 3 |
| line-1 | line-2-0929-0303-s023236 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0929-0303-s023236 | depot | — | revenue | 27 |
| line-2 | line-2-0929-0303-s023236 | depot | — | spare | 4 |
| line-2 | line-2-0929-0303-s023236 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0929-0303-s023236 | depot | — | revenue | 16 |
| line-3 | line-2-0929-0303-s023236 | depot | — | spare | 2 |
| line-3 | line-2-0929-0303-s023236 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (26 trains), line-3 (19 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **115 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **103 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **77 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0584-0314-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0572-0444-s003014 | forward | revenue | 3 | pending |
| line-1 | line-1-0572-0444-s003014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0562-s006168 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0562-s006168 | reverse | revenue | 3 | pending |
| line-1 | line-1-0458-0648-s009043 | forward | revenue | 3 | pending |
| line-1 | line-1-0458-0648-s009043 | reverse | revenue | 3 | pending |
| line-1 | line-1-0434-0761-s012062 | forward | revenue | 3 | pending |
| line-1 | line-1-0434-0761-s012062 | reverse | revenue | 3 | pending |
| line-1 | line-1-0382-0878-s015616 | forward | revenue | 3 | pending |
| line-1 | line-1-0382-0878-s015616 | reverse | revenue | 3 | pending |
| line-1 | line-1-0316-0975-s018551 | reverse | revenue | 3 | pending |
| line-1 | line-1-0584-0314-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0572-0444-s003014 | forward | spare | 1 | pending |
| line-1 | line-1-0572-0444-s003014 | reverse | spare | 1 | pending |
| line-1 | line-1-0545-0562-s006168 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0327-0929-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0513-0729-s006355 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0729-s006355 | reverse | revenue | 3 | pending |
| line-2 | line-2-0538-0619-s009378 | forward | revenue | 3 | pending |
| line-2 | line-2-0538-0619-s009378 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0562-s011717 | forward | revenue | 3 | pending |
| line-2 | line-2-0545-0562-s011717 | reverse | revenue | 3 | pending |
| line-2 | line-2-0610-0519-s013994 | forward | revenue | 3 | pending |
| line-2 | line-2-0610-0519-s013994 | reverse | revenue | 3 | pending |
| line-2 | line-2-0639-0434-s016299 | forward | revenue | 3 | pending |
| line-2 | line-2-0639-0434-s016299 | reverse | revenue | 3 | pending |
| line-2 | line-2-0747-0414-s018625 | forward | revenue | 3 | pending |
| line-2 | line-2-0747-0414-s018625 | reverse | revenue | 3 | pending |
| line-2 | line-2-0929-0303-s023236 | reverse | revenue | 3 | pending |
| line-2 | line-2-0513-0729-s006355 | forward | spare | 1 | pending |
| line-2 | line-2-0513-0729-s006355 | reverse | spare | 1 | pending |
| line-2 | line-2-0538-0619-s009378 | forward | spare | 1 | pending |
| line-2 | line-2-0538-0619-s009378 | reverse | spare | 1 | pending |
| line-2 | line-2-0545-0562-s011717 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0393-0182-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0528-0407-s005752 | forward | revenue | 4 | pending |
| line-3 | line-3-0528-0407-s005752 | reverse | revenue | 4 | pending |
| line-3 | line-3-0545-0562-s009021 | forward | revenue | 4 | pending |
| line-3 | line-3-0545-0562-s009021 | reverse | revenue | 4 | pending |
| line-3 | line-3-0631-0656-s012267 | reverse | revenue | 4 | pending |
| line-3 | line-3-0393-0182-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0528-0407-s005752 | forward | spare | 1 | pending |
| line-3 | line-3-0528-0407-s005752 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**71 trainsets exceed the reference platform envelope**, requiring **4,224.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0975-s018551 | 3 | 2 | 1 | 59.5 |
| line-1-0382-0878-s015616 | 6 | 2 | 4 | 238.0 |
| line-1-0434-0761-s012062 | 6 | 2 | 4 | 238.0 |
| line-1-0458-0648-s009043 | 6 | 2 | 4 | 238.0 |
| line-1-0545-0562-s006168 | 7 | 4 | 3 | 178.5 |
| line-1-0572-0444-s003014 | 8 | 2 | 6 | 357.0 |
| line-1-0584-0314-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0327-0929-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0513-0729-s006355 | 8 | 2 | 6 | 357.0 |
| line-2-0538-0619-s009378 | 8 | 2 | 6 | 357.0 |
| line-2-0545-0562-s011717 | 7 | 4 | 3 | 178.5 |
| line-2-0610-0519-s013994 | 6 | 2 | 4 | 238.0 |
| line-2-0639-0434-s016299 | 6 | 2 | 4 | 238.0 |
| line-2-0747-0414-s018625 | 6 | 2 | 4 | 238.0 |
| line-2-0929-0303-s023236 | 3 | 2 | 1 | 59.5 |
| line-3-0393-0182-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0528-0407-s005752 | 10 | 2 | 8 | 476.0 |
| line-3-0545-0562-s009021 | 8 | 4 | 4 | 238.0 |
| line-3-0631-0656-s012267 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Tetouan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
