# Station and depot overnight allocation

Plan: **34 trainsets at stations + 49 at depots = 83 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0450-0180-s015425 | 49 | 2,401.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0296-0125-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0372-0368-s006097 | station | forward | revenue | 1 |
| line-1 | line-1-0372-0368-s006097 | station | reverse | revenue | 1 |
| line-1 | line-1-0376-0243-s003023 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0243-s003023 | station | reverse | revenue | 1 |
| line-1 | line-1-0455-0478-s009843 | station | forward | revenue | 1 |
| line-1 | line-1-0455-0478-s009843 | station | reverse | revenue | 1 |
| line-1 | line-1-0477-0623-s013606 | station | reverse | revenue | 2 |
| line-2 | line-2-0086-0716-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0147-0574-s003616 | station | forward | revenue | 1 |
| line-2 | line-2-0147-0574-s003616 | station | reverse | revenue | 1 |
| line-2 | line-2-0258-0485-s006620 | station | forward | revenue | 1 |
| line-2 | line-2-0258-0485-s006620 | station | reverse | revenue | 1 |
| line-2 | line-2-0326-0424-s008532 | station | forward | revenue | 1 |
| line-2 | line-2-0326-0424-s008532 | station | reverse | revenue | 1 |
| line-2 | line-2-0372-0368-s010466 | station | forward | revenue | 1 |
| line-2 | line-2-0372-0368-s010466 | station | reverse | revenue | 1 |
| line-2 | line-2-0427-0289-s012939 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0289-s012939 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0180-s015425 | station | reverse | revenue | 2 |
| line-3 | line-3-0181-0288-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0288-0352-s003006 | station | forward | revenue | 1 |
| line-3 | line-3-0288-0352-s003006 | station | reverse | revenue | 1 |
| line-3 | line-3-0372-0368-s005086 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0368-s005086 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0364-s007639 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0364-s007639 | station | reverse | revenue | 1 |
| line-3 | line-3-0702-0427-s013132 | station | reverse | revenue | 2 |
| line-1 | line-2-0450-0180-s015425 | depot | — | revenue | 14 |
| line-1 | line-2-0450-0180-s015425 | depot | — | spare | 2 |
| line-1 | line-2-0450-0180-s015425 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0450-0180-s015425 | depot | — | revenue | 13 |
| line-2 | line-2-0450-0180-s015425 | depot | — | spare | 2 |
| line-2 | line-2-0450-0180-s015425 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0450-0180-s015425 | depot | — | revenue | 13 |
| line-3 | line-2-0450-0180-s015425 | depot | — | spare | 2 |
| line-3 | line-2-0450-0180-s015425 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (17 trains), line-3 (16 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **83 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **74 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **49 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0296-0125-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0376-0243-s003023 | forward | revenue | 3 | pending |
| line-1 | line-1-0376-0243-s003023 | reverse | revenue | 3 | pending |
| line-1 | line-1-0372-0368-s006097 | forward | revenue | 3 | pending |
| line-1 | line-1-0372-0368-s006097 | reverse | revenue | 3 | pending |
| line-1 | line-1-0455-0478-s009843 | forward | revenue | 3 | pending |
| line-1 | line-1-0455-0478-s009843 | reverse | revenue | 3 | pending |
| line-1 | line-1-0477-0623-s013606 | reverse | revenue | 3 | pending |
| line-1 | line-1-0296-0125-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0376-0243-s003023 | forward | spare | 1 | pending |
| line-1 | line-1-0376-0243-s003023 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0086-0716-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | forward | revenue | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | reverse | revenue | 3 | pending |
| line-2 | line-2-0258-0485-s006620 | forward | revenue | 2 | pending |
| line-2 | line-2-0258-0485-s006620 | reverse | revenue | 2 | pending |
| line-2 | line-2-0326-0424-s008532 | forward | revenue | 2 | pending |
| line-2 | line-2-0326-0424-s008532 | reverse | revenue | 2 | pending |
| line-2 | line-2-0372-0368-s010466 | forward | revenue | 2 | pending |
| line-2 | line-2-0372-0368-s010466 | reverse | revenue | 2 | pending |
| line-2 | line-2-0427-0289-s012939 | forward | revenue | 2 | pending |
| line-2 | line-2-0427-0289-s012939 | reverse | revenue | 2 | pending |
| line-2 | line-2-0450-0180-s015425 | reverse | revenue | 2 | pending |
| line-2 | line-2-0258-0485-s006620 | forward | spare | 1 | pending |
| line-2 | line-2-0258-0485-s006620 | reverse | spare | 1 | pending |
| line-2 | line-2-0326-0424-s008532 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0181-0288-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0288-0352-s003006 | forward | revenue | 3 | pending |
| line-3 | line-3-0288-0352-s003006 | reverse | revenue | 3 | pending |
| line-3 | line-3-0372-0368-s005086 | forward | revenue | 3 | pending |
| line-3 | line-3-0372-0368-s005086 | reverse | revenue | 3 | pending |
| line-3 | line-3-0477-0364-s007639 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0364-s007639 | reverse | revenue | 3 | pending |
| line-3 | line-3-0702-0427-s013132 | reverse | revenue | 2 | pending |
| line-3 | line-3-0702-0427-s013132 | reverse | spare | 1 | pending |
| line-3 | line-3-0181-0288-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0288-0352-s003006 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**43 trainsets exceed the reference platform envelope**, requiring **2,107.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0296-0125-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0372-0368-s006097 | 6 | 4 | 2 | 98.0 |
| line-1-0376-0243-s003023 | 8 | 2 | 6 | 294.0 |
| line-1-0455-0478-s009843 | 6 | 2 | 4 | 196.0 |
| line-1-0477-0623-s013606 | 3 | 2 | 1 | 49.0 |
| line-2-0086-0716-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0147-0574-s003616 | 6 | 2 | 4 | 196.0 |
| line-2-0258-0485-s006620 | 6 | 2 | 4 | 196.0 |
| line-2-0326-0424-s008532 | 5 | 2 | 3 | 147.0 |
| line-2-0372-0368-s010466 | 4 | 4 | 0 | 0.0 |
| line-2-0427-0289-s012939 | 4 | 2 | 2 | 98.0 |
| line-2-0450-0180-s015425 | 2 | 2 | 0 | 0.0 |
| line-3-0181-0288-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0288-0352-s003006 | 7 | 2 | 5 | 245.0 |
| line-3-0372-0368-s005086 | 6 | 4 | 2 | 98.0 |
| line-3-0477-0364-s007639 | 6 | 2 | 4 | 196.0 |
| line-3-0702-0427-s013132 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kakamega/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
