# Station and depot overnight allocation

Plan: **30 trainsets at stations + 34 at depots = 64 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0717-0503-s012880 | 34 | 2,023.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0329-0548-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0400-0539-s003024 | station | forward | revenue | 1 |
| line-1 | line-1-0400-0539-s003024 | station | reverse | revenue | 1 |
| line-1 | line-1-0513-0509-s006033 | station | forward | revenue | 1 |
| line-1 | line-1-0513-0509-s006033 | station | reverse | revenue | 1 |
| line-1 | line-1-0546-0550-s007434 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0550-s007434 | station | reverse | revenue | 1 |
| line-1 | line-1-0602-0533-s009039 | station | forward | revenue | 1 |
| line-1 | line-1-0602-0533-s009039 | station | reverse | revenue | 1 |
| line-1 | line-1-0675-0553-s010949 | station | forward | revenue | 1 |
| line-1 | line-1-0675-0553-s010949 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0503-s012880 | station | reverse | revenue | 2 |
| line-2 | line-2-0451-0387-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0512-0450-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0450-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0550-s005998 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0550-s005998 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0647-s008649 | station | reverse | revenue | 2 |
| line-3 | line-3-0428-0586-s007849 | station | reverse | revenue | 2 |
| line-3 | line-3-0546-0550-s004530 | station | forward | revenue | 1 |
| line-3 | line-3-0546-0550-s004530 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0365-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0591-0499-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0591-0499-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0503-s012880 | depot | — | revenue | 10 |
| line-1 | line-1-0717-0503-s012880 | depot | — | spare | 2 |
| line-1 | line-1-0717-0503-s012880 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0717-0503-s012880 | depot | — | revenue | 9 |
| line-2 | line-1-0717-0503-s012880 | depot | — | spare | 1 |
| line-2 | line-1-0717-0503-s012880 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0717-0503-s012880 | depot | — | revenue | 8 |
| line-3 | line-1-0717-0503-s012880 | depot | — | spare | 1 |
| line-3 | line-1-0717-0503-s012880 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (11 trains), line-3 (10 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **64 trainsets at 15 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **57 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **34 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0329-0548-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0400-0539-s003024 | forward | revenue | 2 | pending |
| line-1 | line-1-0400-0539-s003024 | reverse | revenue | 2 | pending |
| line-1 | line-1-0513-0509-s006033 | forward | revenue | 2 | pending |
| line-1 | line-1-0513-0509-s006033 | reverse | revenue | 2 | pending |
| line-1 | line-1-0546-0550-s007434 | forward | revenue | 2 | pending |
| line-1 | line-1-0546-0550-s007434 | reverse | revenue | 2 | pending |
| line-1 | line-1-0602-0533-s009039 | forward | revenue | 2 | pending |
| line-1 | line-1-0602-0533-s009039 | reverse | revenue | 2 | pending |
| line-1 | line-1-0675-0553-s010949 | forward | revenue | 2 | pending |
| line-1 | line-1-0675-0553-s010949 | reverse | revenue | 2 | pending |
| line-1 | line-1-0717-0503-s012880 | reverse | revenue | 2 | pending |
| line-1 | line-1-0329-0548-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0400-0539-s003024 | forward | spare | 1 | pending |
| line-1 | line-1-0400-0539-s003024 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0387-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0512-0450-s003010 | forward | revenue | 3 | pending |
| line-2 | line-2-0512-0450-s003010 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0550-s005998 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0550-s005998 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0647-s008649 | reverse | revenue | 2 | pending |
| line-2 | line-2-0604-0647-s008649 | reverse | spare | 1 | pending |
| line-2 | line-2-0451-0387-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0591-0365-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0591-0499-s003004 | forward | revenue | 3 | pending |
| line-3 | line-3-0591-0499-s003004 | reverse | revenue | 3 | pending |
| line-3 | line-3-0546-0550-s004530 | forward | revenue | 3 | pending |
| line-3 | line-3-0546-0550-s004530 | reverse | revenue | 2 | pending |
| line-3 | line-3-0428-0586-s007849 | reverse | revenue | 2 | pending |
| line-3 | line-3-0546-0550-s004530 | reverse | spare | 1 | pending |
| line-3 | line-3-0428-0586-s007849 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,666.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0329-0548-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0400-0539-s003024 | 6 | 2 | 4 | 238.0 |
| line-1-0513-0509-s006033 | 4 | 2 | 2 | 119.0 |
| line-1-0546-0550-s007434 | 4 | 4 | 0 | 0.0 |
| line-1-0602-0533-s009039 | 4 | 2 | 2 | 119.0 |
| line-1-0675-0553-s010949 | 4 | 2 | 2 | 119.0 |
| line-1-0717-0503-s012880 | 2 | 2 | 0 | 0.0 |
| line-2-0451-0387-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0512-0450-s003010 | 6 | 2 | 4 | 238.0 |
| line-2-0546-0550-s005998 | 6 | 4 | 2 | 119.0 |
| line-2-0604-0647-s008649 | 3 | 2 | 1 | 59.5 |
| line-3-0428-0586-s007849 | 3 | 2 | 1 | 59.5 |
| line-3-0546-0550-s004530 | 6 | 4 | 2 | 119.0 |
| line-3-0591-0365-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0591-0499-s003004 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Ngaoundere/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
