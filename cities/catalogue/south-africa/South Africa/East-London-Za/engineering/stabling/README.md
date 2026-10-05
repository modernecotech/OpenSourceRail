# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 141 at depots = 185 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0250-0950-s000000 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0576-0798-s000000 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0308-0981-s020966 | line-3 | declared-depot | 51 | 3,034.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0250-0950-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0297-0847-s003023 | station | forward | revenue | 1 |
| line-1 | line-1-0297-0847-s003023 | station | reverse | revenue | 1 |
| line-1 | line-1-0299-0845-s003091 | station | forward | revenue | 1 |
| line-1 | line-1-0299-0845-s003091 | station | reverse | revenue | 1 |
| line-1 | line-1-0398-0762-s006040 | station | forward | revenue | 1 |
| line-1 | line-1-0398-0762-s006040 | station | reverse | revenue | 1 |
| line-1 | line-1-0493-0681-s008904 | station | forward | revenue | 1 |
| line-1 | line-1-0493-0681-s008904 | station | reverse | revenue | 1 |
| line-1 | line-1-0598-0591-s012066 | station | forward | revenue | 1 |
| line-1 | line-1-0598-0591-s012066 | station | reverse | revenue | 1 |
| line-1 | line-1-0778-0438-s017461 | station | reverse | revenue | 2 |
| line-2 | line-2-0000-0177-s020745 | station | reverse | revenue | 2 |
| line-2 | line-2-0115-0208-s016995 | station | forward | revenue | 1 |
| line-2 | line-2-0115-0208-s016995 | station | reverse | revenue | 1 |
| line-2 | line-2-0239-0322-s013038 | station | forward | revenue | 1 |
| line-2 | line-2-0239-0322-s013038 | station | reverse | revenue | 1 |
| line-2 | line-2-0330-0450-s009537 | station | forward | revenue | 1 |
| line-2 | line-2-0330-0450-s009537 | station | reverse | revenue | 1 |
| line-2 | line-2-0420-0578-s006020 | station | forward | revenue | 1 |
| line-2 | line-2-0420-0578-s006020 | station | reverse | revenue | 1 |
| line-2 | line-2-0493-0681-s003203 | station | forward | revenue | 1 |
| line-2 | line-2-0493-0681-s003203 | station | reverse | revenue | 1 |
| line-2 | line-2-0576-0798-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0115-0208-s002726 | station | forward | revenue | 1 |
| line-3 | line-3-0115-0208-s002726 | station | reverse | revenue | 1 |
| line-3 | line-3-0139-0104-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0185-0361-s007027 | station | forward | revenue | 1 |
| line-3 | line-3-0185-0361-s007027 | station | reverse | revenue | 1 |
| line-3 | line-3-0216-0497-s010027 | station | forward | revenue | 1 |
| line-3 | line-3-0216-0497-s010027 | station | reverse | revenue | 1 |
| line-3 | line-3-0249-0634-s013040 | station | forward | revenue | 1 |
| line-3 | line-3-0249-0634-s013040 | station | reverse | revenue | 1 |
| line-3 | line-3-0281-0771-s016045 | station | forward | revenue | 1 |
| line-3 | line-3-0281-0771-s016045 | station | reverse | revenue | 1 |
| line-3 | line-3-0299-0846-s017718 | station | forward | revenue | 1 |
| line-3 | line-3-0299-0846-s017718 | station | reverse | revenue | 1 |
| line-3 | line-3-0308-0981-s020966 | station | reverse | revenue | 2 |
| line-1 | line-1-0250-0950-s000000 | depot | — | revenue | 34 |
| line-1 | line-1-0250-0950-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0250-0950-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0576-0798-s000000 | depot | — | revenue | 45 |
| line-2 | line-2-0576-0798-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0576-0798-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0308-0981-s020966 | depot | — | revenue | 44 |
| line-3 | line-3-0308-0981-s020966 | depot | — | spare | 6 |
| line-3 | line-3-0308-0981-s020966 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/east-london-za-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **185 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **167 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **141 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0250-0950-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0297-0847-s003023 | forward | revenue | 4 | pending |
| line-1 | line-1-0297-0847-s003023 | reverse | revenue | 4 | pending |
| line-1 | line-1-0299-0845-s003091 | forward | revenue | 4 | pending |
| line-1 | line-1-0299-0845-s003091 | reverse | revenue | 4 | pending |
| line-1 | line-1-0398-0762-s006040 | forward | revenue | 4 | pending |
| line-1 | line-1-0398-0762-s006040 | reverse | revenue | 4 | pending |
| line-1 | line-1-0493-0681-s008904 | forward | revenue | 4 | pending |
| line-1 | line-1-0493-0681-s008904 | reverse | revenue | 4 | pending |
| line-1 | line-1-0598-0591-s012066 | forward | revenue | 4 | pending |
| line-1 | line-1-0598-0591-s012066 | reverse | revenue | 4 | pending |
| line-1 | line-1-0778-0438-s017461 | reverse | revenue | 4 | pending |
| line-1 | line-1-0250-0950-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0297-0847-s003023 | forward | spare | 1 | pending |
| line-1 | line-1-0297-0847-s003023 | reverse | spare | 1 | pending |
| line-1 | line-1-0299-0845-s003091 | forward | spare | 1 | pending |
| line-1 | line-1-0299-0845-s003091 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0493-0681-s003203 | forward | revenue | 5 | pending |
| line-2 | line-2-0493-0681-s003203 | reverse | revenue | 5 | pending |
| line-2 | line-2-0420-0578-s006020 | forward | revenue | 5 | pending |
| line-2 | line-2-0420-0578-s006020 | reverse | revenue | 5 | pending |
| line-2 | line-2-0330-0450-s009537 | forward | revenue | 5 | pending |
| line-2 | line-2-0330-0450-s009537 | reverse | revenue | 5 | pending |
| line-2 | line-2-0239-0322-s013038 | forward | revenue | 5 | pending |
| line-2 | line-2-0239-0322-s013038 | reverse | revenue | 5 | pending |
| line-2 | line-2-0115-0208-s016995 | forward | revenue | 5 | pending |
| line-2 | line-2-0115-0208-s016995 | reverse | revenue | 5 | pending |
| line-2 | line-2-0000-0177-s020745 | reverse | revenue | 4 | pending |
| line-2 | line-2-0000-0177-s020745 | reverse | spare | 1 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0493-0681-s003203 | forward | spare | 1 | pending |
| line-2 | line-2-0493-0681-s003203 | reverse | spare | 1 | pending |
| line-2 | line-2-0420-0578-s006020 | forward | spare | 1 | pending |
| line-2 | line-2-0420-0578-s006020 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0115-0208-s002726 | forward | revenue | 5 | pending |
| line-3 | line-3-0115-0208-s002726 | reverse | revenue | 5 | pending |
| line-3 | line-3-0185-0361-s007027 | forward | revenue | 5 | pending |
| line-3 | line-3-0185-0361-s007027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0216-0497-s010027 | forward | revenue | 4 | pending |
| line-3 | line-3-0216-0497-s010027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0249-0634-s013040 | forward | revenue | 4 | pending |
| line-3 | line-3-0249-0634-s013040 | reverse | revenue | 4 | pending |
| line-3 | line-3-0281-0771-s016045 | forward | revenue | 4 | pending |
| line-3 | line-3-0281-0771-s016045 | reverse | revenue | 4 | pending |
| line-3 | line-3-0299-0846-s017718 | forward | revenue | 4 | pending |
| line-3 | line-3-0299-0846-s017718 | reverse | revenue | 4 | pending |
| line-3 | line-3-0308-0981-s020966 | reverse | revenue | 4 | pending |
| line-3 | line-3-0185-0361-s007027 | reverse | spare | 1 | pending |
| line-3 | line-3-0216-0497-s010027 | forward | spare | 1 | pending |
| line-3 | line-3-0216-0497-s010027 | reverse | spare | 1 | pending |
| line-3 | line-3-0249-0634-s013040 | forward | spare | 1 | pending |
| line-3 | line-3-0249-0634-s013040 | reverse | spare | 1 | pending |
| line-3 | line-3-0281-0771-s016045 | forward | spare | 1 | pending |
| line-3 | line-3-0281-0771-s016045 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**127 trainsets exceed the reference platform envelope**, requiring **7,556.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0250-0950-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0297-0847-s003023 | 10 | 4 | 6 | 357.0 |
| line-1-0299-0845-s003091 | 10 | 4 | 6 | 357.0 |
| line-1-0398-0762-s006040 | 8 | 2 | 6 | 357.0 |
| line-1-0493-0681-s008904 | 8 | 4 | 4 | 238.0 |
| line-1-0598-0591-s012066 | 8 | 2 | 6 | 357.0 |
| line-1-0778-0438-s017461 | 4 | 2 | 2 | 119.0 |
| line-2-0000-0177-s020745 | 5 | 2 | 3 | 178.5 |
| line-2-0115-0208-s016995 | 10 | 4 | 6 | 357.0 |
| line-2-0239-0322-s013038 | 10 | 2 | 8 | 476.0 |
| line-2-0330-0450-s009537 | 10 | 2 | 8 | 476.0 |
| line-2-0420-0578-s006020 | 12 | 2 | 10 | 595.0 |
| line-2-0493-0681-s003203 | 12 | 4 | 8 | 476.0 |
| line-2-0576-0798-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0115-0208-s002726 | 10 | 4 | 6 | 357.0 |
| line-3-0139-0104-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0185-0361-s007027 | 10 | 2 | 8 | 476.0 |
| line-3-0216-0497-s010027 | 10 | 2 | 8 | 476.0 |
| line-3-0249-0634-s013040 | 10 | 2 | 8 | 476.0 |
| line-3-0281-0771-s016045 | 10 | 2 | 8 | 476.0 |
| line-3-0299-0846-s017718 | 8 | 4 | 4 | 238.0 |
| line-3-0308-0981-s020966 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/East-London-Za/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
