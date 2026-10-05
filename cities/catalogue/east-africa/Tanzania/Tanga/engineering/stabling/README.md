# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 90 at depots = 120 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0930-0771-s016565 | line-1 | declared-depot | 39 | 2,320.5 | 7 |
| line-2-0603-0186-s000000 | line-2 | declared-depot | 29 | 1,725.5 | 6 |
| line-3-0376-0685-s000000 | line-3 | declared-depot | 22 | 1,309.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0364-0285-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0473-0377-s003212 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0377-s003212 | station | reverse | revenue | 1 |
| line-1 | line-1-0577-0465-s006232 | station | forward | revenue | 1 |
| line-1 | line-1-0577-0465-s006232 | station | reverse | revenue | 1 |
| line-1 | line-1-0752-0613-s011403 | station | forward | revenue | 1 |
| line-1 | line-1-0752-0613-s011403 | station | reverse | revenue | 1 |
| line-1 | line-1-0930-0771-s016565 | station | reverse | revenue | 2 |
| line-2 | line-2-0356-0657-s012906 | station | reverse | revenue | 2 |
| line-2 | line-2-0412-0568-s010592 | station | forward | revenue | 1 |
| line-2 | line-2-0412-0568-s010592 | station | reverse | revenue | 1 |
| line-2 | line-2-0466-0483-s008292 | station | forward | revenue | 1 |
| line-2 | line-2-0466-0483-s008292 | station | reverse | revenue | 1 |
| line-2 | line-2-0540-0367-s005266 | station | forward | revenue | 1 |
| line-2 | line-2-0540-0367-s005266 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0186-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0376-0685-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0546-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0546-s003004 | station | reverse | revenue | 1 |
| line-3 | line-3-0422-0445-s005193 | station | forward | revenue | 1 |
| line-3 | line-3-0422-0445-s005193 | station | reverse | revenue | 1 |
| line-3 | line-3-0442-0345-s007370 | station | forward | revenue | 1 |
| line-3 | line-3-0442-0345-s007370 | station | reverse | revenue | 1 |
| line-3 | line-3-0461-0244-s009548 | station | reverse | revenue | 2 |
| line-1 | line-1-0930-0771-s016565 | depot | — | revenue | 34 |
| line-1 | line-1-0930-0771-s016565 | depot | — | spare | 4 |
| line-1 | line-1-0930-0771-s016565 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0603-0186-s000000 | depot | — | revenue | 25 |
| line-2 | line-2-0603-0186-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0603-0186-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0376-0685-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0376-0685-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0376-0685-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tanga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **120 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **108 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **90 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0364-0285-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0473-0377-s003212 | forward | revenue | 6 | pending |
| line-1 | line-1-0473-0377-s003212 | reverse | revenue | 6 | pending |
| line-1 | line-1-0577-0465-s006232 | forward | revenue | 6 | pending |
| line-1 | line-1-0577-0465-s006232 | reverse | revenue | 5 | pending |
| line-1 | line-1-0752-0613-s011403 | forward | revenue | 5 | pending |
| line-1 | line-1-0752-0613-s011403 | reverse | revenue | 5 | pending |
| line-1 | line-1-0930-0771-s016565 | reverse | revenue | 5 | pending |
| line-1 | line-1-0577-0465-s006232 | reverse | spare | 1 | pending |
| line-1 | line-1-0752-0613-s011403 | forward | spare | 1 | pending |
| line-1 | line-1-0752-0613-s011403 | reverse | spare | 1 | pending |
| line-1 | line-1-0930-0771-s016565 | reverse | spare | 1 | pending |
| line-1 | line-1-0364-0285-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0603-0186-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0540-0367-s005266 | forward | revenue | 5 | pending |
| line-2 | line-2-0540-0367-s005266 | reverse | revenue | 5 | pending |
| line-2 | line-2-0466-0483-s008292 | forward | revenue | 4 | pending |
| line-2 | line-2-0466-0483-s008292 | reverse | revenue | 4 | pending |
| line-2 | line-2-0412-0568-s010592 | forward | revenue | 4 | pending |
| line-2 | line-2-0412-0568-s010592 | reverse | revenue | 4 | pending |
| line-2 | line-2-0356-0657-s012906 | reverse | revenue | 4 | pending |
| line-2 | line-2-0466-0483-s008292 | forward | spare | 1 | pending |
| line-2 | line-2-0466-0483-s008292 | reverse | spare | 1 | pending |
| line-2 | line-2-0412-0568-s010592 | forward | spare | 1 | pending |
| line-2 | line-2-0412-0568-s010592 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0376-0685-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0403-0546-s003004 | forward | revenue | 4 | pending |
| line-3 | line-3-0403-0546-s003004 | reverse | revenue | 4 | pending |
| line-3 | line-3-0422-0445-s005193 | forward | revenue | 4 | pending |
| line-3 | line-3-0422-0445-s005193 | reverse | revenue | 4 | pending |
| line-3 | line-3-0442-0345-s007370 | forward | revenue | 3 | pending |
| line-3 | line-3-0442-0345-s007370 | reverse | revenue | 3 | pending |
| line-3 | line-3-0461-0244-s009548 | reverse | revenue | 3 | pending |
| line-3 | line-3-0442-0345-s007370 | forward | spare | 1 | pending |
| line-3 | line-3-0442-0345-s007370 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0244-s009548 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0364-0285-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0473-0377-s003212 | 12 | 2 | 10 | 595.0 |
| line-1-0577-0465-s006232 | 12 | 2 | 10 | 595.0 |
| line-1-0752-0613-s011403 | 12 | 2 | 10 | 595.0 |
| line-1-0930-0771-s016565 | 6 | 2 | 4 | 238.0 |
| line-2-0356-0657-s012906 | 4 | 2 | 2 | 119.0 |
| line-2-0412-0568-s010592 | 10 | 4 | 6 | 357.0 |
| line-2-0466-0483-s008292 | 10 | 2 | 8 | 476.0 |
| line-2-0540-0367-s005266 | 10 | 2 | 8 | 476.0 |
| line-2-0603-0186-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0376-0685-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0403-0546-s003004 | 8 | 4 | 4 | 238.0 |
| line-3-0422-0445-s005193 | 8 | 2 | 6 | 357.0 |
| line-3-0442-0345-s007370 | 8 | 2 | 6 | 357.0 |
| line-3-0461-0244-s009548 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
