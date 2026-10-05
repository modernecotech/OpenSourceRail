# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 98 at depots = 128 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0529-0080-s000000 | line-1 | declared-depot | 32 | 1,904.0 | 6 |
| line-2-0628-0393-s000000 | line-2 | declared-depot | 30 | 1,785.0 | 6 |
| line-3-0480-0367-s015229 | line-3 | declared-depot | 36 | 2,142.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0529-0080-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0532-0339-s005453 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0339-s005453 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0483-s008469 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0483-s008469 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0550-s009867 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0550-s009867 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0716-s013339 | station | reverse | revenue | 2 |
| line-2 | line-2-0294-0806-s011917 | station | reverse | revenue | 2 |
| line-2 | line-2-0458-0603-s006054 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0603-s006054 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0498-s003027 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0498-s003027 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0393-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0367-s015229 | station | reverse | revenue | 2 |
| line-3 | line-3-0508-0462-s013086 | station | forward | revenue | 1 |
| line-3 | line-3-0508-0462-s013086 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0557-s010934 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0557-s010934 | station | reverse | revenue | 1 |
| line-3 | line-3-0562-0644-s008975 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0644-s008975 | station | reverse | revenue | 1 |
| line-3 | line-3-0588-0730-s007016 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0730-s007016 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-1029-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0529-0080-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0529-0080-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0529-0080-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0628-0393-s000000 | depot | — | revenue | 26 |
| line-2 | line-2-0628-0393-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0628-0393-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0480-0367-s015229 | depot | — | revenue | 31 |
| line-3 | line-3-0480-0367-s015229 | depot | — | spare | 4 |
| line-3 | line-3-0480-0367-s015229 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/raqqa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **128 trainsets at 15 stations**; largest initial station queue **13**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **115 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0529-0080-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0339-s005453 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0339-s005453 | reverse | revenue | 5 | pending |
| line-1 | line-1-0547-0483-s008469 | forward | revenue | 5 | pending |
| line-1 | line-1-0547-0483-s008469 | reverse | revenue | 5 | pending |
| line-1 | line-1-0554-0550-s009867 | forward | revenue | 5 | pending |
| line-1 | line-1-0554-0550-s009867 | reverse | revenue | 4 | pending |
| line-1 | line-1-0571-0716-s013339 | reverse | revenue | 4 | pending |
| line-1 | line-1-0554-0550-s009867 | reverse | spare | 1 | pending |
| line-1 | line-1-0571-0716-s013339 | reverse | spare | 1 | pending |
| line-1 | line-1-0529-0080-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0532-0339-s005453 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0628-0393-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0543-0498-s003027 | forward | revenue | 6 | pending |
| line-2 | line-2-0543-0498-s003027 | reverse | revenue | 6 | pending |
| line-2 | line-2-0458-0603-s006054 | forward | revenue | 6 | pending |
| line-2 | line-2-0458-0603-s006054 | reverse | revenue | 5 | pending |
| line-2 | line-2-0294-0806-s011917 | reverse | revenue | 5 | pending |
| line-2 | line-2-0458-0603-s006054 | reverse | spare | 1 | pending |
| line-2 | line-2-0294-0806-s011917 | reverse | spare | 1 | pending |
| line-2 | line-2-0628-0393-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0543-0498-s003027 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0591-1029-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0588-0730-s007016 | forward | revenue | 5 | pending |
| line-3 | line-3-0588-0730-s007016 | reverse | revenue | 5 | pending |
| line-3 | line-3-0562-0644-s008975 | forward | revenue | 4 | pending |
| line-3 | line-3-0562-0644-s008975 | reverse | revenue | 4 | pending |
| line-3 | line-3-0537-0557-s010934 | forward | revenue | 4 | pending |
| line-3 | line-3-0537-0557-s010934 | reverse | revenue | 4 | pending |
| line-3 | line-3-0508-0462-s013086 | forward | revenue | 4 | pending |
| line-3 | line-3-0508-0462-s013086 | reverse | revenue | 4 | pending |
| line-3 | line-3-0480-0367-s015229 | reverse | revenue | 4 | pending |
| line-3 | line-3-0562-0644-s008975 | forward | spare | 1 | pending |
| line-3 | line-3-0562-0644-s008975 | reverse | spare | 1 | pending |
| line-3 | line-3-0537-0557-s010934 | forward | spare | 1 | pending |
| line-3 | line-3-0537-0557-s010934 | reverse | spare | 1 | pending |
| line-3 | line-3-0508-0462-s013086 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**88 trainsets exceed the reference platform envelope**, requiring **5,236.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0529-0080-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0532-0339-s005453 | 11 | 2 | 9 | 535.5 |
| line-1-0547-0483-s008469 | 10 | 4 | 6 | 357.0 |
| line-1-0554-0550-s009867 | 10 | 4 | 6 | 357.0 |
| line-1-0571-0716-s013339 | 5 | 2 | 3 | 178.5 |
| line-2-0294-0806-s011917 | 6 | 2 | 4 | 238.0 |
| line-2-0458-0603-s006054 | 12 | 2 | 10 | 595.0 |
| line-2-0543-0498-s003027 | 13 | 4 | 9 | 535.5 |
| line-2-0628-0393-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0480-0367-s015229 | 4 | 2 | 2 | 119.0 |
| line-3-0508-0462-s013086 | 9 | 2 | 7 | 416.5 |
| line-3-0537-0557-s010934 | 10 | 4 | 6 | 357.0 |
| line-3-0562-0644-s008975 | 10 | 2 | 8 | 476.0 |
| line-3-0588-0730-s007016 | 10 | 4 | 6 | 357.0 |
| line-3-0591-1029-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Raqqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
