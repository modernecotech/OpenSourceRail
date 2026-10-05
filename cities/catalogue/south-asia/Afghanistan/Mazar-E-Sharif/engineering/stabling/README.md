# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 137 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0426-0909-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0809-0030-s024197 | line-2 | declared-depot | 61 | 3,629.5 | 11 |
| line-3-0801-0064-s000000 | line-3 | declared-depot | 48 | 2,856.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0426-0909-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0446-0747-s003499 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0747-s003499 | station | reverse | revenue | 1 |
| line-1 | line-1-0449-0573-s007004 | station | forward | revenue | 1 |
| line-1 | line-1-0449-0573-s007004 | station | reverse | revenue | 1 |
| line-1 | line-1-0451-0471-s009061 | station | forward | revenue | 1 |
| line-1 | line-1-0451-0471-s009061 | station | reverse | revenue | 1 |
| line-1 | line-1-0452-0368-s011129 | station | forward | revenue | 1 |
| line-1 | line-1-0452-0368-s011129 | station | reverse | revenue | 1 |
| line-1 | line-1-0454-0266-s013186 | station | reverse | revenue | 2 |
| line-2 | line-2-0528-0892-s003573 | station | forward | revenue | 1 |
| line-2 | line-2-0528-0892-s003573 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0988-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0591-0661-s008750 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0661-s008750 | station | reverse | revenue | 1 |
| line-2 | line-2-0630-0517-s011977 | station | forward | revenue | 1 |
| line-2 | line-2-0630-0517-s011977 | station | reverse | revenue | 1 |
| line-2 | line-2-0631-0514-s012045 | station | forward | revenue | 1 |
| line-2 | line-2-0631-0514-s012045 | station | reverse | revenue | 1 |
| line-2 | line-2-0809-0030-s024197 | station | reverse | revenue | 2 |
| line-2 | line-2-0810-0072-s023083 | station | forward | revenue | 1 |
| line-2 | line-2-0810-0072-s023083 | station | reverse | revenue | 1 |
| line-3 | line-3-0461-0845-s019782 | station | reverse | revenue | 2 |
| line-3 | line-3-0509-0752-s017478 | station | forward | revenue | 1 |
| line-3 | line-3-0509-0752-s017478 | station | reverse | revenue | 1 |
| line-3 | line-3-0571-0631-s014462 | station | forward | revenue | 1 |
| line-3 | line-3-0571-0631-s014462 | station | reverse | revenue | 1 |
| line-3 | line-3-0630-0517-s011599 | station | forward | revenue | 1 |
| line-3 | line-3-0630-0517-s011599 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0514-s011531 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0514-s011531 | station | reverse | revenue | 1 |
| line-3 | line-3-0801-0064-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0810-0072-s000258 | station | forward | revenue | 1 |
| line-3 | line-3-0810-0072-s000258 | station | reverse | revenue | 1 |
| line-1 | line-1-0426-0909-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0426-0909-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0426-0909-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0809-0030-s024197 | depot | — | revenue | 54 |
| line-2 | line-2-0809-0030-s024197 | depot | — | spare | 6 |
| line-2 | line-2-0809-0030-s024197 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0801-0064-s000000 | depot | — | revenue | 42 |
| line-3 | line-3-0801-0064-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0801-0064-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mazar-e-sharif-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **160 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **137 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0426-0909-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0446-0747-s003499 | forward | revenue | 4 | pending |
| line-1 | line-1-0446-0747-s003499 | reverse | revenue | 4 | pending |
| line-1 | line-1-0449-0573-s007004 | forward | revenue | 4 | pending |
| line-1 | line-1-0449-0573-s007004 | reverse | revenue | 4 | pending |
| line-1 | line-1-0451-0471-s009061 | forward | revenue | 4 | pending |
| line-1 | line-1-0451-0471-s009061 | reverse | revenue | 3 | pending |
| line-1 | line-1-0452-0368-s011129 | forward | revenue | 3 | pending |
| line-1 | line-1-0452-0368-s011129 | reverse | revenue | 3 | pending |
| line-1 | line-1-0454-0266-s013186 | reverse | revenue | 3 | pending |
| line-1 | line-1-0451-0471-s009061 | reverse | spare | 1 | pending |
| line-1 | line-1-0452-0368-s011129 | forward | spare | 1 | pending |
| line-1 | line-1-0452-0368-s011129 | reverse | spare | 1 | pending |
| line-1 | line-1-0454-0266-s013186 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0528-0892-s003573 | forward | revenue | 6 | pending |
| line-2 | line-2-0528-0892-s003573 | reverse | revenue | 6 | pending |
| line-2 | line-2-0591-0661-s008750 | forward | revenue | 6 | pending |
| line-2 | line-2-0591-0661-s008750 | reverse | revenue | 6 | pending |
| line-2 | line-2-0630-0517-s011977 | forward | revenue | 6 | pending |
| line-2 | line-2-0630-0517-s011977 | reverse | revenue | 6 | pending |
| line-2 | line-2-0631-0514-s012045 | forward | revenue | 6 | pending |
| line-2 | line-2-0631-0514-s012045 | reverse | revenue | 5 | pending |
| line-2 | line-2-0810-0072-s023083 | forward | revenue | 5 | pending |
| line-2 | line-2-0810-0072-s023083 | reverse | revenue | 5 | pending |
| line-2 | line-2-0809-0030-s024197 | reverse | revenue | 5 | pending |
| line-2 | line-2-0631-0514-s012045 | reverse | spare | 1 | pending |
| line-2 | line-2-0810-0072-s023083 | forward | spare | 1 | pending |
| line-2 | line-2-0810-0072-s023083 | reverse | spare | 1 | pending |
| line-2 | line-2-0809-0030-s024197 | reverse | spare | 1 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0892-s003573 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0892-s003573 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0801-0064-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0810-0072-s000258 | forward | revenue | 5 | pending |
| line-3 | line-3-0810-0072-s000258 | reverse | revenue | 5 | pending |
| line-3 | line-3-0631-0514-s011531 | forward | revenue | 5 | pending |
| line-3 | line-3-0631-0514-s011531 | reverse | revenue | 5 | pending |
| line-3 | line-3-0630-0517-s011599 | forward | revenue | 5 | pending |
| line-3 | line-3-0630-0517-s011599 | reverse | revenue | 5 | pending |
| line-3 | line-3-0571-0631-s014462 | forward | revenue | 5 | pending |
| line-3 | line-3-0571-0631-s014462 | reverse | revenue | 4 | pending |
| line-3 | line-3-0509-0752-s017478 | forward | revenue | 4 | pending |
| line-3 | line-3-0509-0752-s017478 | reverse | revenue | 4 | pending |
| line-3 | line-3-0461-0845-s019782 | reverse | revenue | 4 | pending |
| line-3 | line-3-0571-0631-s014462 | reverse | spare | 1 | pending |
| line-3 | line-3-0509-0752-s017478 | forward | spare | 1 | pending |
| line-3 | line-3-0509-0752-s017478 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0845-s019782 | reverse | spare | 1 | pending |
| line-3 | line-3-0801-0064-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0810-0072-s000258 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**125 trainsets exceed the reference platform envelope**, requiring **7,437.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0426-0909-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0446-0747-s003499 | 8 | 2 | 6 | 357.0 |
| line-1-0449-0573-s007004 | 8 | 2 | 6 | 357.0 |
| line-1-0451-0471-s009061 | 8 | 2 | 6 | 357.0 |
| line-1-0452-0368-s011129 | 8 | 2 | 6 | 357.0 |
| line-1-0454-0266-s013186 | 4 | 2 | 2 | 119.0 |
| line-2-0528-0892-s003573 | 14 | 2 | 12 | 714.0 |
| line-2-0569-0988-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0591-0661-s008750 | 12 | 2 | 10 | 595.0 |
| line-2-0630-0517-s011977 | 12 | 4 | 8 | 476.0 |
| line-2-0631-0514-s012045 | 12 | 4 | 8 | 476.0 |
| line-2-0809-0030-s024197 | 6 | 2 | 4 | 238.0 |
| line-2-0810-0072-s023083 | 12 | 4 | 8 | 476.0 |
| line-3-0461-0845-s019782 | 5 | 2 | 3 | 178.5 |
| line-3-0509-0752-s017478 | 10 | 2 | 8 | 476.0 |
| line-3-0571-0631-s014462 | 10 | 2 | 8 | 476.0 |
| line-3-0630-0517-s011599 | 10 | 4 | 6 | 357.0 |
| line-3-0631-0514-s011531 | 10 | 4 | 6 | 357.0 |
| line-3-0801-0064-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0810-0072-s000258 | 11 | 4 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Mazar-E-Sharif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
