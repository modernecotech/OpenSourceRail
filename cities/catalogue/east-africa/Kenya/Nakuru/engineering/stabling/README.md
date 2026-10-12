# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 158 at depots = 202 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0383-0392-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 5 |
| line-2-1065-0208-s022549 | line-2 | declared-depot | 56 | 3,332.0 | 10 |
| line-3-0651-0932-s000000 | line-3 | declared-depot | 46 | 2,737.0 | 8 |
| line-4-0533-0545-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0506-0773-s000000 | line-5 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0383-0392-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0446-0586-s004437 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0586-s004437 | station | reverse | revenue | 1 |
| line-1 | line-1-0506-0773-s008721 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0773-s008721 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0881-s011456 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0736-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0446-0586-s004478 | station | forward | revenue | 1 |
| line-2 | line-2-0446-0586-s004478 | station | reverse | revenue | 1 |
| line-2 | line-2-0533-0545-s007496 | station | forward | revenue | 1 |
| line-2 | line-2-0533-0545-s007496 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0555-s008090 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0555-s008090 | station | reverse | revenue | 1 |
| line-2 | line-2-0577-0561-s008618 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0561-s008618 | station | reverse | revenue | 1 |
| line-2 | line-2-0716-0452-s012337 | station | forward | revenue | 1 |
| line-2 | line-2-0716-0452-s012337 | station | reverse | revenue | 1 |
| line-2 | line-2-1065-0208-s022549 | station | reverse | revenue | 2 |
| line-3 | line-3-0556-0555-s009325 | station | forward | revenue | 1 |
| line-3 | line-3-0556-0555-s009325 | station | reverse | revenue | 1 |
| line-3 | line-3-0562-0826-s003513 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0826-s003513 | station | reverse | revenue | 1 |
| line-3 | line-3-0564-0202-s018468 | station | reverse | revenue | 2 |
| line-3 | line-3-0577-0561-s009854 | station | forward | revenue | 1 |
| line-3 | line-3-0577-0561-s009854 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0435-s013019 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0435-s013019 | station | reverse | revenue | 1 |
| line-3 | line-3-0651-0932-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0506-0390-s003682 | station | forward | revenue | 1 |
| line-4 | line-4-0506-0390-s003682 | station | reverse | revenue | 1 |
| line-4 | line-4-0533-0545-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0559-0339-s005986 | station | reverse | revenue | 2 |
| line-5 | line-5-0289-0715-s005796 | station | reverse | revenue | 2 |
| line-5 | line-5-0506-0773-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0383-0392-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0383-0392-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0383-0392-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1065-0208-s022549 | depot | — | revenue | 49 |
| line-2 | line-2-1065-0208-s022549 | depot | — | spare | 6 |
| line-2 | line-2-1065-0208-s022549 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0651-0932-s000000 | depot | — | revenue | 40 |
| line-3 | line-3-0651-0932-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0651-0932-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0533-0545-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0533-0545-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0533-0545-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0506-0773-s000000 | depot | — | revenue | 12 |
| line-5 | line-5-0506-0773-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0506-0773-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nakuru-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **202 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **181 revenue, 16 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **158 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0383-0392-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0446-0586-s004437 | forward | revenue | 6 | pending |
| line-1 | line-1-0446-0586-s004437 | reverse | revenue | 5 | pending |
| line-1 | line-1-0506-0773-s008721 | forward | revenue | 5 | pending |
| line-1 | line-1-0506-0773-s008721 | reverse | revenue | 5 | pending |
| line-1 | line-1-0531-0881-s011456 | reverse | revenue | 5 | pending |
| line-1 | line-1-0446-0586-s004437 | reverse | spare | 1 | pending |
| line-1 | line-1-0506-0773-s008721 | forward | spare | 1 | pending |
| line-1 | line-1-0506-0773-s008721 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0881-s011456 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0736-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0446-0586-s004478 | forward | revenue | 6 | pending |
| line-2 | line-2-0446-0586-s004478 | reverse | revenue | 6 | pending |
| line-2 | line-2-0533-0545-s007496 | forward | revenue | 5 | pending |
| line-2 | line-2-0533-0545-s007496 | reverse | revenue | 5 | pending |
| line-2 | line-2-0556-0555-s008090 | forward | revenue | 5 | pending |
| line-2 | line-2-0556-0555-s008090 | reverse | revenue | 5 | pending |
| line-2 | line-2-0577-0561-s008618 | forward | revenue | 5 | pending |
| line-2 | line-2-0577-0561-s008618 | reverse | revenue | 5 | pending |
| line-2 | line-2-0716-0452-s012337 | forward | revenue | 5 | pending |
| line-2 | line-2-0716-0452-s012337 | reverse | revenue | 5 | pending |
| line-2 | line-2-1065-0208-s022549 | reverse | revenue | 5 | pending |
| line-2 | line-2-0533-0545-s007496 | forward | spare | 1 | pending |
| line-2 | line-2-0533-0545-s007496 | reverse | spare | 1 | pending |
| line-2 | line-2-0556-0555-s008090 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0555-s008090 | reverse | spare | 1 | pending |
| line-2 | line-2-0577-0561-s008618 | forward | spare | 1 | pending |
| line-2 | line-2-0577-0561-s008618 | reverse | spare | 1 | pending |
| line-2 | line-2-0716-0452-s012337 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0651-0932-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0562-0826-s003513 | forward | revenue | 6 | pending |
| line-3 | line-3-0562-0826-s003513 | reverse | revenue | 5 | pending |
| line-3 | line-3-0556-0555-s009325 | forward | revenue | 5 | pending |
| line-3 | line-3-0556-0555-s009325 | reverse | revenue | 5 | pending |
| line-3 | line-3-0577-0561-s009854 | forward | revenue | 5 | pending |
| line-3 | line-3-0577-0561-s009854 | reverse | revenue | 5 | pending |
| line-3 | line-3-0607-0435-s013019 | forward | revenue | 5 | pending |
| line-3 | line-3-0607-0435-s013019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0564-0202-s018468 | reverse | revenue | 5 | pending |
| line-3 | line-3-0562-0826-s003513 | reverse | spare | 1 | pending |
| line-3 | line-3-0556-0555-s009325 | forward | spare | 1 | pending |
| line-3 | line-3-0556-0555-s009325 | reverse | spare | 1 | pending |
| line-3 | line-3-0577-0561-s009854 | forward | spare | 1 | pending |
| line-3 | line-3-0577-0561-s009854 | reverse | spare | 1 | pending |
| line-3 | line-3-0607-0435-s013019 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0533-0545-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0506-0390-s003682 | forward | revenue | 5 | pending |
| line-4 | line-4-0506-0390-s003682 | reverse | revenue | 4 | pending |
| line-4 | line-4-0559-0339-s005986 | reverse | revenue | 4 | pending |
| line-4 | line-4-0506-0390-s003682 | reverse | spare | 1 | pending |
| line-4 | line-4-0559-0339-s005986 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0506-0773-s000000 | forward | revenue | 8 | pending |
| line-5 | line-5-0289-0715-s005796 | reverse | revenue | 8 | pending |
| line-5 | line-5-0506-0773-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0289-0715-s005796 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**142 trainsets exceed the reference platform envelope**, requiring **8,449.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0383-0392-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0446-0586-s004437 | 12 | 4 | 8 | 476.0 |
| line-1-0506-0773-s008721 | 12 | 4 | 8 | 476.0 |
| line-1-0531-0881-s011456 | 6 | 2 | 4 | 238.0 |
| line-2-0381-0736-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0446-0586-s004478 | 12 | 4 | 8 | 476.0 |
| line-2-0533-0545-s007496 | 12 | 4 | 8 | 476.0 |
| line-2-0556-0555-s008090 | 12 | 4 | 8 | 476.0 |
| line-2-0577-0561-s008618 | 12 | 4 | 8 | 476.0 |
| line-2-0716-0452-s012337 | 11 | 2 | 9 | 535.5 |
| line-2-1065-0208-s022549 | 5 | 2 | 3 | 178.5 |
| line-3-0556-0555-s009325 | 12 | 4 | 8 | 476.0 |
| line-3-0562-0826-s003513 | 12 | 2 | 10 | 595.0 |
| line-3-0564-0202-s018468 | 5 | 2 | 3 | 178.5 |
| line-3-0577-0561-s009854 | 12 | 4 | 8 | 476.0 |
| line-3-0607-0435-s013019 | 11 | 2 | 9 | 535.5 |
| line-3-0651-0932-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0506-0390-s003682 | 10 | 2 | 8 | 476.0 |
| line-4-0533-0545-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0559-0339-s005986 | 5 | 2 | 3 | 178.5 |
| line-5-0289-0715-s005796 | 9 | 2 | 7 | 416.5 |
| line-5-0506-0773-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nakuru/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
