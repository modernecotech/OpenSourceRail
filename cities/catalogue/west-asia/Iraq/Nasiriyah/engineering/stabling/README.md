# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 108 at depots = 136 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0286-0224-s025301 | line-1 | declared-depot | 67 | 3,986.5 | 11 |
| line-2-0375-0639-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0804-0635-s000000 | line-3 | declared-depot | 19 | 1,130.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0286-0224-s025301 | station | reverse | revenue | 2 |
| line-1 | line-1-0461-0407-s019341 | station | forward | revenue | 1 |
| line-1 | line-1-0461-0407-s019341 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0498-s016323 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0498-s016323 | station | reverse | revenue | 1 |
| line-1 | line-1-0632-0568-s014049 | station | forward | revenue | 1 |
| line-1 | line-1-0632-0568-s014049 | station | reverse | revenue | 1 |
| line-1 | line-1-0729-0659-s011038 | station | forward | revenue | 1 |
| line-1 | line-1-0729-0659-s011038 | station | reverse | revenue | 1 |
| line-1 | line-1-1075-0993-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0375-0639-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0460-0536-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0460-0536-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0432-s006017 | station | forward | revenue | 1 |
| line-2 | line-2-0545-0432-s006017 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0312-s009530 | station | reverse | revenue | 2 |
| line-3 | line-3-0636-0308-s008119 | station | reverse | revenue | 2 |
| line-3 | line-3-0689-0411-s005562 | station | forward | revenue | 1 |
| line-3 | line-3-0689-0411-s005562 | station | reverse | revenue | 1 |
| line-3 | line-3-0742-0514-s003016 | station | forward | revenue | 1 |
| line-3 | line-3-0742-0514-s003016 | station | reverse | revenue | 1 |
| line-3 | line-3-0804-0635-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0286-0224-s025301 | depot | — | revenue | 59 |
| line-1 | line-1-0286-0224-s025301 | depot | — | spare | 7 |
| line-1 | line-1-0286-0224-s025301 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0375-0639-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0375-0639-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0375-0639-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0804-0635-s000000 | depot | — | revenue | 16 |
| line-3 | line-3-0804-0635-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0804-0635-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nasiriyah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **136 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **122 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **108 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1075-0993-s000000 | forward | revenue | 8 | pending |
| line-1 | line-1-0729-0659-s011038 | forward | revenue | 7 | pending |
| line-1 | line-1-0729-0659-s011038 | reverse | revenue | 7 | pending |
| line-1 | line-1-0632-0568-s014049 | forward | revenue | 7 | pending |
| line-1 | line-1-0632-0568-s014049 | reverse | revenue | 7 | pending |
| line-1 | line-1-0559-0498-s016323 | forward | revenue | 7 | pending |
| line-1 | line-1-0559-0498-s016323 | reverse | revenue | 7 | pending |
| line-1 | line-1-0461-0407-s019341 | forward | revenue | 7 | pending |
| line-1 | line-1-0461-0407-s019341 | reverse | revenue | 7 | pending |
| line-1 | line-1-0286-0224-s025301 | reverse | revenue | 7 | pending |
| line-1 | line-1-0729-0659-s011038 | forward | spare | 1 | pending |
| line-1 | line-1-0729-0659-s011038 | reverse | spare | 1 | pending |
| line-1 | line-1-0632-0568-s014049 | forward | spare | 1 | pending |
| line-1 | line-1-0632-0568-s014049 | reverse | spare | 1 | pending |
| line-1 | line-1-0559-0498-s016323 | forward | spare | 1 | pending |
| line-1 | line-1-0559-0498-s016323 | reverse | spare | 1 | pending |
| line-1 | line-1-0461-0407-s019341 | forward | spare | 1 | pending |
| line-1 | line-1-0461-0407-s019341 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0375-0639-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0460-0536-s003010 | forward | revenue | 5 | pending |
| line-2 | line-2-0460-0536-s003010 | reverse | revenue | 5 | pending |
| line-2 | line-2-0545-0432-s006017 | forward | revenue | 4 | pending |
| line-2 | line-2-0545-0432-s006017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0644-0312-s009530 | reverse | revenue | 4 | pending |
| line-2 | line-2-0545-0432-s006017 | forward | spare | 1 | pending |
| line-2 | line-2-0545-0432-s006017 | reverse | spare | 1 | pending |
| line-2 | line-2-0644-0312-s009530 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0804-0635-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0742-0514-s003016 | forward | revenue | 4 | pending |
| line-3 | line-3-0742-0514-s003016 | reverse | revenue | 4 | pending |
| line-3 | line-3-0689-0411-s005562 | forward | revenue | 4 | pending |
| line-3 | line-3-0689-0411-s005562 | reverse | revenue | 4 | pending |
| line-3 | line-3-0636-0308-s008119 | reverse | revenue | 4 | pending |
| line-3 | line-3-0804-0635-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0742-0514-s003016 | forward | spare | 1 | pending |
| line-3 | line-3-0742-0514-s003016 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**108 trainsets exceed the reference platform envelope**, requiring **6,426.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0286-0224-s025301 | 7 | 2 | 5 | 297.5 |
| line-1-0461-0407-s019341 | 16 | 2 | 14 | 833.0 |
| line-1-0559-0498-s016323 | 16 | 2 | 14 | 833.0 |
| line-1-0632-0568-s014049 | 16 | 2 | 14 | 833.0 |
| line-1-0729-0659-s011038 | 16 | 2 | 14 | 833.0 |
| line-1-1075-0993-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0375-0639-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0460-0536-s003010 | 10 | 2 | 8 | 476.0 |
| line-2-0545-0432-s006017 | 10 | 2 | 8 | 476.0 |
| line-2-0644-0312-s009530 | 5 | 2 | 3 | 178.5 |
| line-3-0636-0308-s008119 | 4 | 2 | 2 | 119.0 |
| line-3-0689-0411-s005562 | 8 | 2 | 6 | 357.0 |
| line-3-0742-0514-s003016 | 10 | 2 | 8 | 476.0 |
| line-3-0804-0635-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Nasiriyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
