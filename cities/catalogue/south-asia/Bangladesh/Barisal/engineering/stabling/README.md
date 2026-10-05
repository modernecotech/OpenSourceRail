# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 139 at depots = 175 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0279-0389-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 7 |
| line-2-0447-0722-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0761-0860-s024670 | line-3 | declared-depot | 67 | 3,986.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0279-0389-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0367-0418-s002024 | station | forward | revenue | 1 |
| line-1 | line-1-0367-0418-s002024 | station | reverse | revenue | 1 |
| line-1 | line-1-0507-0464-s005216 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0464-s005216 | station | reverse | revenue | 1 |
| line-1 | line-1-0639-0507-s008236 | station | forward | revenue | 1 |
| line-1 | line-1-0639-0507-s008236 | station | reverse | revenue | 1 |
| line-1 | line-1-0755-0545-s010883 | station | forward | revenue | 1 |
| line-1 | line-1-0755-0545-s010883 | station | reverse | revenue | 1 |
| line-1 | line-1-0879-0586-s013726 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0722-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0576-0653-s003269 | station | forward | revenue | 1 |
| line-2 | line-2-0576-0653-s003269 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0595-s006028 | station | forward | revenue | 1 |
| line-2 | line-2-0687-0595-s006028 | station | reverse | revenue | 1 |
| line-2 | line-2-0755-0545-s007884 | station | forward | revenue | 1 |
| line-2 | line-2-0755-0545-s007884 | station | reverse | revenue | 1 |
| line-2 | line-2-0836-0498-s009893 | station | forward | revenue | 1 |
| line-2 | line-2-0836-0498-s009893 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0450-s016003 | station | reverse | revenue | 2 |
| line-3 | line-3-0078-0053-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0367-0418-s011395 | station | forward | revenue | 1 |
| line-3 | line-3-0367-0418-s011395 | station | reverse | revenue | 1 |
| line-3 | line-3-0412-0468-s012908 | station | forward | revenue | 1 |
| line-3 | line-3-0412-0468-s012908 | station | reverse | revenue | 1 |
| line-3 | line-3-0502-0569-s015943 | station | forward | revenue | 1 |
| line-3 | line-3-0502-0569-s015943 | station | reverse | revenue | 1 |
| line-3 | line-3-0576-0653-s018459 | station | forward | revenue | 1 |
| line-3 | line-3-0576-0653-s018459 | station | reverse | revenue | 1 |
| line-3 | line-3-0761-0860-s024670 | station | reverse | revenue | 2 |
| line-1 | line-1-0279-0389-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0279-0389-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0279-0389-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0447-0722-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0447-0722-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0447-0722-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0761-0860-s024670 | depot | — | revenue | 59 |
| line-3 | line-3-0761-0860-s024670 | depot | — | spare | 7 |
| line-3 | line-3-0761-0860-s024670 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/barisal-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **175 trainsets at 18 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **157 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **139 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0279-0389-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0418-s002024 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0418-s002024 | reverse | revenue | 4 | pending |
| line-1 | line-1-0507-0464-s005216 | forward | revenue | 4 | pending |
| line-1 | line-1-0507-0464-s005216 | reverse | revenue | 4 | pending |
| line-1 | line-1-0639-0507-s008236 | forward | revenue | 4 | pending |
| line-1 | line-1-0639-0507-s008236 | reverse | revenue | 4 | pending |
| line-1 | line-1-0755-0545-s010883 | forward | revenue | 4 | pending |
| line-1 | line-1-0755-0545-s010883 | reverse | revenue | 4 | pending |
| line-1 | line-1-0879-0586-s013726 | reverse | revenue | 4 | pending |
| line-1 | line-1-0279-0389-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0367-0418-s002024 | forward | spare | 1 | pending |
| line-1 | line-1-0367-0418-s002024 | reverse | spare | 1 | pending |
| line-1 | line-1-0507-0464-s005216 | forward | spare | 1 | pending |
| line-1 | line-1-0507-0464-s005216 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0447-0722-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0576-0653-s003269 | forward | revenue | 5 | pending |
| line-2 | line-2-0576-0653-s003269 | reverse | revenue | 5 | pending |
| line-2 | line-2-0687-0595-s006028 | forward | revenue | 5 | pending |
| line-2 | line-2-0687-0595-s006028 | reverse | revenue | 5 | pending |
| line-2 | line-2-0755-0545-s007884 | forward | revenue | 5 | pending |
| line-2 | line-2-0755-0545-s007884 | reverse | revenue | 4 | pending |
| line-2 | line-2-0836-0498-s009893 | forward | revenue | 4 | pending |
| line-2 | line-2-0836-0498-s009893 | reverse | revenue | 4 | pending |
| line-2 | line-2-1084-0450-s016003 | reverse | revenue | 4 | pending |
| line-2 | line-2-0755-0545-s007884 | reverse | spare | 1 | pending |
| line-2 | line-2-0836-0498-s009893 | forward | spare | 1 | pending |
| line-2 | line-2-0836-0498-s009893 | reverse | spare | 1 | pending |
| line-2 | line-2-1084-0450-s016003 | reverse | spare | 1 | pending |
| line-2 | line-2-0447-0722-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0367-0418-s011395 | forward | revenue | 7 | pending |
| line-3 | line-3-0367-0418-s011395 | reverse | revenue | 7 | pending |
| line-3 | line-3-0412-0468-s012908 | forward | revenue | 7 | pending |
| line-3 | line-3-0412-0468-s012908 | reverse | revenue | 7 | pending |
| line-3 | line-3-0502-0569-s015943 | forward | revenue | 7 | pending |
| line-3 | line-3-0502-0569-s015943 | reverse | revenue | 7 | pending |
| line-3 | line-3-0576-0653-s018459 | forward | revenue | 7 | pending |
| line-3 | line-3-0576-0653-s018459 | reverse | revenue | 7 | pending |
| line-3 | line-3-0761-0860-s024670 | reverse | revenue | 7 | pending |
| line-3 | line-3-0367-0418-s011395 | forward | spare | 1 | pending |
| line-3 | line-3-0367-0418-s011395 | reverse | spare | 1 | pending |
| line-3 | line-3-0412-0468-s012908 | forward | spare | 1 | pending |
| line-3 | line-3-0412-0468-s012908 | reverse | spare | 1 | pending |
| line-3 | line-3-0502-0569-s015943 | forward | spare | 1 | pending |
| line-3 | line-3-0502-0569-s015943 | reverse | spare | 1 | pending |
| line-3 | line-3-0576-0653-s018459 | forward | spare | 1 | pending |
| line-3 | line-3-0576-0653-s018459 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**127 trainsets exceed the reference platform envelope**, requiring **7,556.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0279-0389-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0367-0418-s002024 | 10 | 4 | 6 | 357.0 |
| line-1-0507-0464-s005216 | 10 | 2 | 8 | 476.0 |
| line-1-0639-0507-s008236 | 8 | 2 | 6 | 357.0 |
| line-1-0755-0545-s010883 | 8 | 4 | 4 | 238.0 |
| line-1-0879-0586-s013726 | 4 | 2 | 2 | 119.0 |
| line-2-0447-0722-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0576-0653-s003269 | 10 | 4 | 6 | 357.0 |
| line-2-0687-0595-s006028 | 10 | 2 | 8 | 476.0 |
| line-2-0755-0545-s007884 | 10 | 4 | 6 | 357.0 |
| line-2-0836-0498-s009893 | 10 | 2 | 8 | 476.0 |
| line-2-1084-0450-s016003 | 5 | 2 | 3 | 178.5 |
| line-3-0078-0053-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0367-0418-s011395 | 16 | 4 | 12 | 714.0 |
| line-3-0412-0468-s012908 | 16 | 2 | 14 | 833.0 |
| line-3-0502-0569-s015943 | 16 | 2 | 14 | 833.0 |
| line-3-0576-0653-s018459 | 16 | 4 | 12 | 714.0 |
| line-3-0761-0860-s024670 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Barisal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
