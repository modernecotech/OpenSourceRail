# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 100 at depots = 132 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0492-0379-s015978 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0719-0761-s000000 | line-2 | declared-depot | 34 | 2,023.0 | 7 |
| line-3-0132-0345-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0276-1068-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0288-0914-s003491 | station | forward | revenue | 1 |
| line-1 | line-1-0288-0914-s003491 | station | reverse | revenue | 1 |
| line-1 | line-1-0351-0764-s007016 | station | forward | revenue | 1 |
| line-1 | line-1-0351-0764-s007016 | station | reverse | revenue | 1 |
| line-1 | line-1-0398-0635-s010021 | station | forward | revenue | 1 |
| line-1 | line-1-0398-0635-s010021 | station | reverse | revenue | 1 |
| line-1 | line-1-0446-0506-s013034 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0506-s013034 | station | reverse | revenue | 1 |
| line-1 | line-1-0492-0379-s015978 | station | reverse | revenue | 2 |
| line-2 | line-2-0330-0248-s014396 | station | reverse | revenue | 2 |
| line-2 | line-2-0402-0343-s011724 | station | forward | revenue | 1 |
| line-2 | line-2-0402-0343-s011724 | station | reverse | revenue | 1 |
| line-2 | line-2-0475-0439-s009047 | station | forward | revenue | 1 |
| line-2 | line-2-0475-0439-s009047 | station | reverse | revenue | 1 |
| line-2 | line-2-0557-0548-s005942 | station | forward | revenue | 1 |
| line-2 | line-2-0557-0548-s005942 | station | reverse | revenue | 1 |
| line-2 | line-2-0637-0653-s003027 | station | forward | revenue | 1 |
| line-2 | line-2-0637-0653-s003027 | station | reverse | revenue | 1 |
| line-2 | line-2-0719-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0132-0345-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0331-0406-s004690 | station | forward | revenue | 1 |
| line-3 | line-3-0331-0406-s004690 | station | reverse | revenue | 1 |
| line-3 | line-3-0466-0438-s007690 | station | forward | revenue | 1 |
| line-3 | line-3-0466-0438-s007690 | station | reverse | revenue | 1 |
| line-3 | line-3-0593-0468-s010479 | station | reverse | revenue | 2 |
| line-1 | line-1-0492-0379-s015978 | depot | — | revenue | 34 |
| line-1 | line-1-0492-0379-s015978 | depot | — | spare | 4 |
| line-1 | line-1-0492-0379-s015978 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0719-0761-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0719-0761-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0719-0761-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0132-0345-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0132-0345-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0132-0345-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bamenda-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **132 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **118 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **100 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0276-1068-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0288-0914-s003491 | forward | revenue | 5 | pending |
| line-1 | line-1-0288-0914-s003491 | reverse | revenue | 5 | pending |
| line-1 | line-1-0351-0764-s007016 | forward | revenue | 5 | pending |
| line-1 | line-1-0351-0764-s007016 | reverse | revenue | 5 | pending |
| line-1 | line-1-0398-0635-s010021 | forward | revenue | 5 | pending |
| line-1 | line-1-0398-0635-s010021 | reverse | revenue | 4 | pending |
| line-1 | line-1-0446-0506-s013034 | forward | revenue | 4 | pending |
| line-1 | line-1-0446-0506-s013034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0492-0379-s015978 | reverse | revenue | 4 | pending |
| line-1 | line-1-0398-0635-s010021 | reverse | spare | 1 | pending |
| line-1 | line-1-0446-0506-s013034 | forward | spare | 1 | pending |
| line-1 | line-1-0446-0506-s013034 | reverse | spare | 1 | pending |
| line-1 | line-1-0492-0379-s015978 | reverse | spare | 1 | pending |
| line-1 | line-1-0276-1068-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0719-0761-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0637-0653-s003027 | forward | revenue | 4 | pending |
| line-2 | line-2-0637-0653-s003027 | reverse | revenue | 4 | pending |
| line-2 | line-2-0557-0548-s005942 | forward | revenue | 4 | pending |
| line-2 | line-2-0557-0548-s005942 | reverse | revenue | 4 | pending |
| line-2 | line-2-0475-0439-s009047 | forward | revenue | 4 | pending |
| line-2 | line-2-0475-0439-s009047 | reverse | revenue | 4 | pending |
| line-2 | line-2-0402-0343-s011724 | forward | revenue | 4 | pending |
| line-2 | line-2-0402-0343-s011724 | reverse | revenue | 4 | pending |
| line-2 | line-2-0330-0248-s014396 | reverse | revenue | 4 | pending |
| line-2 | line-2-0637-0653-s003027 | forward | spare | 1 | pending |
| line-2 | line-2-0637-0653-s003027 | reverse | spare | 1 | pending |
| line-2 | line-2-0557-0548-s005942 | forward | spare | 1 | pending |
| line-2 | line-2-0557-0548-s005942 | reverse | spare | 1 | pending |
| line-2 | line-2-0475-0439-s009047 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0132-0345-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0331-0406-s004690 | forward | revenue | 5 | pending |
| line-3 | line-3-0331-0406-s004690 | reverse | revenue | 5 | pending |
| line-3 | line-3-0466-0438-s007690 | forward | revenue | 5 | pending |
| line-3 | line-3-0466-0438-s007690 | reverse | revenue | 5 | pending |
| line-3 | line-3-0593-0468-s010479 | reverse | revenue | 5 | pending |
| line-3 | line-3-0331-0406-s004690 | forward | spare | 1 | pending |
| line-3 | line-3-0331-0406-s004690 | reverse | spare | 1 | pending |
| line-3 | line-3-0466-0438-s007690 | forward | spare | 1 | pending |
| line-3 | line-3-0466-0438-s007690 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**96 trainsets exceed the reference platform envelope**, requiring **5,712.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0276-1068-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0288-0914-s003491 | 10 | 2 | 8 | 476.0 |
| line-1-0351-0764-s007016 | 10 | 2 | 8 | 476.0 |
| line-1-0398-0635-s010021 | 10 | 2 | 8 | 476.0 |
| line-1-0446-0506-s013034 | 10 | 2 | 8 | 476.0 |
| line-1-0492-0379-s015978 | 5 | 2 | 3 | 178.5 |
| line-2-0330-0248-s014396 | 4 | 2 | 2 | 119.0 |
| line-2-0402-0343-s011724 | 8 | 2 | 6 | 357.0 |
| line-2-0475-0439-s009047 | 9 | 4 | 5 | 297.5 |
| line-2-0557-0548-s005942 | 10 | 2 | 8 | 476.0 |
| line-2-0637-0653-s003027 | 10 | 2 | 8 | 476.0 |
| line-2-0719-0761-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0132-0345-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0331-0406-s004690 | 12 | 2 | 10 | 595.0 |
| line-3-0466-0438-s007690 | 12 | 4 | 8 | 476.0 |
| line-3-0593-0468-s010479 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bamenda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
