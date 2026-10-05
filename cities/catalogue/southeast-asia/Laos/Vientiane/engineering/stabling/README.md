# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 146 at depots = 186 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0216-1056-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0101-0902-s000000 | line-2 | declared-depot | 45 | 2,677.5 | 9 |
| line-3-0905-0994-s024370 | line-3 | declared-depot | 61 | 3,629.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0216-1056-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0473-0901-s006670 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0901-s006670 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0831-s009691 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0831-s009691 | station | reverse | revenue | 1 |
| line-1 | line-1-0704-0761-s012696 | station | forward | revenue | 1 |
| line-1 | line-1-0704-0761-s012696 | station | reverse | revenue | 1 |
| line-1 | line-1-0799-0704-s015162 | station | forward | revenue | 1 |
| line-1 | line-1-0799-0704-s015162 | station | reverse | revenue | 1 |
| line-1 | line-1-0890-0663-s017616 | station | reverse | revenue | 2 |
| line-2 | line-2-0101-0902-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0233-0868-s003231 | station | forward | revenue | 1 |
| line-2 | line-2-0233-0868-s003231 | station | reverse | revenue | 1 |
| line-2 | line-2-0342-0787-s006235 | station | forward | revenue | 1 |
| line-2 | line-2-0342-0787-s006235 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0708-s009248 | station | forward | revenue | 1 |
| line-2 | line-2-0450-0708-s009248 | station | reverse | revenue | 1 |
| line-2 | line-2-0557-0628-s012250 | station | forward | revenue | 1 |
| line-2 | line-2-0557-0628-s012250 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0548-s015272 | station | forward | revenue | 1 |
| line-2 | line-2-0665-0548-s015272 | station | reverse | revenue | 1 |
| line-2 | line-2-0789-0457-s018694 | station | reverse | revenue | 2 |
| line-3 | line-3-0197-0196-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0420-0417-s007017 | station | forward | revenue | 1 |
| line-3 | line-3-0420-0417-s007017 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0570-s011299 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0570-s011299 | station | reverse | revenue | 1 |
| line-3 | line-3-0612-0673-s014301 | station | forward | revenue | 1 |
| line-3 | line-3-0612-0673-s014301 | station | reverse | revenue | 1 |
| line-3 | line-3-0693-0780-s017323 | station | forward | revenue | 1 |
| line-3 | line-3-0693-0780-s017323 | station | reverse | revenue | 1 |
| line-3 | line-3-0791-0910-s020841 | station | forward | revenue | 1 |
| line-3 | line-3-0791-0910-s020841 | station | reverse | revenue | 1 |
| line-3 | line-3-0905-0994-s024370 | station | reverse | revenue | 2 |
| line-1 | line-1-0216-1056-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-0216-1056-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0216-1056-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0101-0902-s000000 | depot | — | revenue | 39 |
| line-2 | line-2-0101-0902-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0101-0902-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0905-0994-s024370 | depot | — | revenue | 54 |
| line-3 | line-3-0905-0994-s024370 | depot | — | spare | 6 |
| line-3 | line-3-0905-0994-s024370 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/vientiane-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **186 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **168 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **146 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0216-1056-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0473-0901-s006670 | forward | revenue | 5 | pending |
| line-1 | line-1-0473-0901-s006670 | reverse | revenue | 5 | pending |
| line-1 | line-1-0588-0831-s009691 | forward | revenue | 5 | pending |
| line-1 | line-1-0588-0831-s009691 | reverse | revenue | 5 | pending |
| line-1 | line-1-0704-0761-s012696 | forward | revenue | 5 | pending |
| line-1 | line-1-0704-0761-s012696 | reverse | revenue | 5 | pending |
| line-1 | line-1-0799-0704-s015162 | forward | revenue | 4 | pending |
| line-1 | line-1-0799-0704-s015162 | reverse | revenue | 4 | pending |
| line-1 | line-1-0890-0663-s017616 | reverse | revenue | 4 | pending |
| line-1 | line-1-0799-0704-s015162 | forward | spare | 1 | pending |
| line-1 | line-1-0799-0704-s015162 | reverse | spare | 1 | pending |
| line-1 | line-1-0890-0663-s017616 | reverse | spare | 1 | pending |
| line-1 | line-1-0216-1056-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0473-0901-s006670 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0101-0902-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0233-0868-s003231 | forward | revenue | 5 | pending |
| line-2 | line-2-0233-0868-s003231 | reverse | revenue | 5 | pending |
| line-2 | line-2-0342-0787-s006235 | forward | revenue | 5 | pending |
| line-2 | line-2-0342-0787-s006235 | reverse | revenue | 5 | pending |
| line-2 | line-2-0450-0708-s009248 | forward | revenue | 4 | pending |
| line-2 | line-2-0450-0708-s009248 | reverse | revenue | 4 | pending |
| line-2 | line-2-0557-0628-s012250 | forward | revenue | 4 | pending |
| line-2 | line-2-0557-0628-s012250 | reverse | revenue | 4 | pending |
| line-2 | line-2-0665-0548-s015272 | forward | revenue | 4 | pending |
| line-2 | line-2-0665-0548-s015272 | reverse | revenue | 4 | pending |
| line-2 | line-2-0789-0457-s018694 | reverse | revenue | 4 | pending |
| line-2 | line-2-0450-0708-s009248 | forward | spare | 1 | pending |
| line-2 | line-2-0450-0708-s009248 | reverse | spare | 1 | pending |
| line-2 | line-2-0557-0628-s012250 | forward | spare | 1 | pending |
| line-2 | line-2-0557-0628-s012250 | reverse | spare | 1 | pending |
| line-2 | line-2-0665-0548-s015272 | forward | spare | 1 | pending |
| line-2 | line-2-0665-0548-s015272 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0197-0196-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0420-0417-s007017 | forward | revenue | 6 | pending |
| line-3 | line-3-0420-0417-s007017 | reverse | revenue | 6 | pending |
| line-3 | line-3-0535-0570-s011299 | forward | revenue | 6 | pending |
| line-3 | line-3-0535-0570-s011299 | reverse | revenue | 6 | pending |
| line-3 | line-3-0612-0673-s014301 | forward | revenue | 6 | pending |
| line-3 | line-3-0612-0673-s014301 | reverse | revenue | 6 | pending |
| line-3 | line-3-0693-0780-s017323 | forward | revenue | 6 | pending |
| line-3 | line-3-0693-0780-s017323 | reverse | revenue | 5 | pending |
| line-3 | line-3-0791-0910-s020841 | forward | revenue | 5 | pending |
| line-3 | line-3-0791-0910-s020841 | reverse | revenue | 5 | pending |
| line-3 | line-3-0905-0994-s024370 | reverse | revenue | 5 | pending |
| line-3 | line-3-0693-0780-s017323 | reverse | spare | 1 | pending |
| line-3 | line-3-0791-0910-s020841 | forward | spare | 1 | pending |
| line-3 | line-3-0791-0910-s020841 | reverse | spare | 1 | pending |
| line-3 | line-3-0905-0994-s024370 | reverse | spare | 1 | pending |
| line-3 | line-3-0197-0196-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0420-0417-s007017 | forward | spare | 1 | pending |
| line-3 | line-3-0420-0417-s007017 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**142 trainsets exceed the reference platform envelope**, requiring **8,449.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0216-1056-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0473-0901-s006670 | 11 | 2 | 9 | 535.5 |
| line-1-0588-0831-s009691 | 10 | 2 | 8 | 476.0 |
| line-1-0704-0761-s012696 | 10 | 4 | 6 | 357.0 |
| line-1-0799-0704-s015162 | 10 | 2 | 8 | 476.0 |
| line-1-0890-0663-s017616 | 5 | 2 | 3 | 178.5 |
| line-2-0101-0902-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0233-0868-s003231 | 10 | 2 | 8 | 476.0 |
| line-2-0342-0787-s006235 | 10 | 2 | 8 | 476.0 |
| line-2-0450-0708-s009248 | 10 | 2 | 8 | 476.0 |
| line-2-0557-0628-s012250 | 10 | 2 | 8 | 476.0 |
| line-2-0665-0548-s015272 | 10 | 2 | 8 | 476.0 |
| line-2-0789-0457-s018694 | 4 | 2 | 2 | 119.0 |
| line-3-0197-0196-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0420-0417-s007017 | 14 | 2 | 12 | 714.0 |
| line-3-0535-0570-s011299 | 12 | 2 | 10 | 595.0 |
| line-3-0612-0673-s014301 | 12 | 2 | 10 | 595.0 |
| line-3-0693-0780-s017323 | 12 | 4 | 8 | 476.0 |
| line-3-0791-0910-s020841 | 12 | 2 | 10 | 595.0 |
| line-3-0905-0994-s024370 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/southeast-asia/Laos/Vientiane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
