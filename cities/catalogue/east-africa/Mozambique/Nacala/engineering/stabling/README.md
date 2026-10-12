# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 69 at depots = 113 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0533-0436-s000000 | line-1 | declared-depot | 11 | 539.0 | 3 |
| line-2-0394-0018-s026634 | line-2 | declared-depot | 37 | 1,813.0 | 8 |
| line-3-0258-0500-s000000 | line-3 | declared-depot | 11 | 539.0 | 4 |
| line-4-0612-0423-s000000 | line-4 | declared-depot | 10 | 490.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0069-0563-s010809 | station | reverse | revenue | 2 |
| line-1 | line-1-0253-0487-s006022 | station | forward | revenue | 1 |
| line-1 | line-1-0253-0487-s006022 | station | reverse | revenue | 1 |
| line-1 | line-1-0343-0471-s004090 | station | forward | revenue | 1 |
| line-1 | line-1-0343-0471-s004090 | station | reverse | revenue | 1 |
| line-1 | line-1-0433-0454-s002149 | station | forward | revenue | 1 |
| line-1 | line-1-0433-0454-s002149 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0436-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0390-0117-s024427 | station | forward | revenue | 1 |
| line-2 | line-2-0390-0117-s024427 | station | reverse | revenue | 1 |
| line-2 | line-2-0394-0018-s026634 | station | reverse | revenue | 2 |
| line-2 | line-2-0398-0359-s006017 | station | forward | revenue | 1 |
| line-2 | line-2-0398-0359-s006017 | station | reverse | revenue | 1 |
| line-2 | line-2-0433-0454-s001962 | station | forward | revenue | 1 |
| line-2 | line-2-0433-0454-s001962 | station | reverse | revenue | 1 |
| line-2 | line-2-0433-0461-s001822 | station | forward | revenue | 1 |
| line-2 | line-2-0433-0461-s001822 | station | reverse | revenue | 1 |
| line-2 | line-2-0437-0123-s022235 | station | forward | revenue | 1 |
| line-2 | line-2-0437-0123-s022235 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0518-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0542-0310-s009519 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0310-s009519 | station | reverse | revenue | 1 |
| line-3 | line-3-0258-0500-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0346-0480-s001926 | station | forward | revenue | 1 |
| line-3 | line-3-0346-0480-s001926 | station | reverse | revenue | 1 |
| line-3 | line-3-0433-0461-s003835 | station | forward | revenue | 1 |
| line-3 | line-3-0433-0461-s003835 | station | reverse | revenue | 1 |
| line-3 | line-3-0533-0438-s006025 | station | forward | revenue | 1 |
| line-3 | line-3-0533-0438-s006025 | station | reverse | revenue | 1 |
| line-3 | line-3-0612-0423-s007730 | station | forward | revenue | 1 |
| line-3 | line-3-0612-0423-s007730 | station | reverse | revenue | 1 |
| line-3 | line-3-0685-0451-s009668 | station | reverse | revenue | 2 |
| line-4 | line-4-0362-0562-s008105 | station | reverse | revenue | 2 |
| line-4 | line-4-0436-0534-s005930 | station | forward | revenue | 1 |
| line-4 | line-4-0436-0534-s005930 | station | reverse | revenue | 1 |
| line-4 | line-4-0612-0423-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0533-0436-s000000 | depot | — | revenue | 9 |
| line-1 | line-1-0533-0436-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0533-0436-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0394-0018-s026634 | depot | — | revenue | 32 |
| line-2 | line-2-0394-0018-s026634 | depot | — | spare | 4 |
| line-2 | line-2-0394-0018-s026634 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0258-0500-s000000 | depot | — | revenue | 8 |
| line-3 | line-3-0258-0500-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0258-0500-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0612-0423-s000000 | depot | — | revenue | 8 |
| line-4 | line-4-0612-0423-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0612-0423-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nacala-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **113 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **101 revenue, 8 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **69 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0533-0436-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0433-0454-s002149 | forward | revenue | 3 | pending |
| line-1 | line-1-0433-0454-s002149 | reverse | revenue | 3 | pending |
| line-1 | line-1-0343-0471-s004090 | forward | revenue | 2 | pending |
| line-1 | line-1-0343-0471-s004090 | reverse | revenue | 2 | pending |
| line-1 | line-1-0253-0487-s006022 | forward | revenue | 2 | pending |
| line-1 | line-1-0253-0487-s006022 | reverse | revenue | 2 | pending |
| line-1 | line-1-0069-0563-s010809 | reverse | revenue | 2 | pending |
| line-1 | line-1-0343-0471-s004090 | forward | spare | 1 | pending |
| line-1 | line-1-0343-0471-s004090 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0450-0518-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0433-0461-s001822 | forward | revenue | 4 | pending |
| line-2 | line-2-0433-0461-s001822 | reverse | revenue | 4 | pending |
| line-2 | line-2-0433-0454-s001962 | forward | revenue | 4 | pending |
| line-2 | line-2-0433-0454-s001962 | reverse | revenue | 4 | pending |
| line-2 | line-2-0398-0359-s006017 | forward | revenue | 4 | pending |
| line-2 | line-2-0398-0359-s006017 | reverse | revenue | 3 | pending |
| line-2 | line-2-0542-0310-s009519 | forward | revenue | 3 | pending |
| line-2 | line-2-0542-0310-s009519 | reverse | revenue | 3 | pending |
| line-2 | line-2-0437-0123-s022235 | forward | revenue | 3 | pending |
| line-2 | line-2-0437-0123-s022235 | reverse | revenue | 3 | pending |
| line-2 | line-2-0390-0117-s024427 | forward | revenue | 3 | pending |
| line-2 | line-2-0390-0117-s024427 | reverse | revenue | 3 | pending |
| line-2 | line-2-0394-0018-s026634 | reverse | revenue | 3 | pending |
| line-2 | line-2-0398-0359-s006017 | reverse | spare | 1 | pending |
| line-2 | line-2-0542-0310-s009519 | forward | spare | 1 | pending |
| line-2 | line-2-0542-0310-s009519 | reverse | spare | 1 | pending |
| line-2 | line-2-0437-0123-s022235 | forward | spare | 1 | pending |
| line-2 | line-2-0437-0123-s022235 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0258-0500-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0346-0480-s001926 | forward | revenue | 2 | pending |
| line-3 | line-3-0346-0480-s001926 | reverse | revenue | 2 | pending |
| line-3 | line-3-0433-0461-s003835 | forward | revenue | 2 | pending |
| line-3 | line-3-0433-0461-s003835 | reverse | revenue | 2 | pending |
| line-3 | line-3-0533-0438-s006025 | forward | revenue | 2 | pending |
| line-3 | line-3-0533-0438-s006025 | reverse | revenue | 2 | pending |
| line-3 | line-3-0612-0423-s007730 | forward | revenue | 2 | pending |
| line-3 | line-3-0612-0423-s007730 | reverse | revenue | 2 | pending |
| line-3 | line-3-0685-0451-s009668 | reverse | revenue | 2 | pending |
| line-3 | line-3-0258-0500-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0346-0480-s001926 | forward | spare | 1 | pending |
| line-3 | line-3-0346-0480-s001926 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0612-0423-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0436-0534-s005930 | forward | revenue | 4 | pending |
| line-4 | line-4-0436-0534-s005930 | reverse | revenue | 3 | pending |
| line-4 | line-4-0362-0562-s008105 | reverse | revenue | 3 | pending |
| line-4 | line-4-0436-0534-s005930 | reverse | spare | 1 | pending |
| line-4 | line-4-0362-0562-s008105 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,401.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0069-0563-s010809 | 2 | 2 | 0 | 0.0 |
| line-1-0253-0487-s006022 | 4 | 4 | 0 | 0.0 |
| line-1-0343-0471-s004090 | 6 | 4 | 2 | 98.0 |
| line-1-0433-0454-s002149 | 6 | 4 | 2 | 98.0 |
| line-1-0533-0436-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0390-0117-s024427 | 6 | 2 | 4 | 196.0 |
| line-2-0394-0018-s026634 | 3 | 2 | 1 | 49.0 |
| line-2-0398-0359-s006017 | 8 | 2 | 6 | 294.0 |
| line-2-0433-0454-s001962 | 8 | 4 | 4 | 196.0 |
| line-2-0433-0461-s001822 | 8 | 4 | 4 | 196.0 |
| line-2-0437-0123-s022235 | 8 | 2 | 6 | 294.0 |
| line-2-0450-0518-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0542-0310-s009519 | 8 | 2 | 6 | 294.0 |
| line-3-0258-0500-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0346-0480-s001926 | 6 | 4 | 2 | 98.0 |
| line-3-0433-0461-s003835 | 4 | 4 | 0 | 0.0 |
| line-3-0533-0438-s006025 | 4 | 4 | 0 | 0.0 |
| line-3-0612-0423-s007730 | 4 | 4 | 0 | 0.0 |
| line-3-0685-0451-s009668 | 2 | 2 | 0 | 0.0 |
| line-4-0362-0562-s008105 | 4 | 2 | 2 | 98.0 |
| line-4-0436-0534-s005930 | 8 | 4 | 4 | 196.0 |
| line-4-0612-0423-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nacala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
