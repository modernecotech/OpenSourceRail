# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 91 at depots = 121 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0526-0296-s016491 | line-1 | declared-depot | 41 | 2,439.5 | 8 |
| line-2-0405-0445-s000000 | line-2 | declared-depot | 14 | 833.0 | 3 |
| line-3-1040-0281-s000000 | line-3 | declared-depot | 36 | 2,142.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0526-0296-s016491 | station | reverse | revenue | 2 |
| line-1 | line-1-0550-0420-s013812 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0420-s013812 | station | reverse | revenue | 1 |
| line-1 | line-1-0575-0544-s011125 | station | forward | revenue | 1 |
| line-1 | line-1-0575-0544-s011125 | station | reverse | revenue | 1 |
| line-1 | line-1-0593-0639-s009065 | station | forward | revenue | 1 |
| line-1 | line-1-0593-0639-s009065 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0734-s007007 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0734-s007007 | station | reverse | revenue | 1 |
| line-1 | line-1-0637-1074-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0405-0445-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0450-0601-s003516 | station | forward | revenue | 1 |
| line-2 | line-2-0450-0601-s003516 | station | reverse | revenue | 1 |
| line-2 | line-2-0483-0717-s006133 | station | reverse | revenue | 2 |
| line-3 | line-3-0425-0612-s015253 | station | reverse | revenue | 2 |
| line-3 | line-3-0450-0601-s014662 | station | forward | revenue | 1 |
| line-3 | line-3-0450-0601-s014662 | station | reverse | revenue | 1 |
| line-3 | line-3-0575-0544-s011631 | station | forward | revenue | 1 |
| line-3 | line-3-0575-0544-s011631 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0513-s010019 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0513-s010019 | station | reverse | revenue | 1 |
| line-3 | line-3-0765-0457-s007005 | station | forward | revenue | 1 |
| line-3 | line-3-0765-0457-s007005 | station | reverse | revenue | 1 |
| line-3 | line-3-1040-0281-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0526-0296-s016491 | depot | — | revenue | 36 |
| line-1 | line-1-0526-0296-s016491 | depot | — | spare | 4 |
| line-1 | line-1-0526-0296-s016491 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0405-0445-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0405-0445-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0405-0445-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1040-0281-s000000 | depot | — | revenue | 31 |
| line-3 | line-3-1040-0281-s000000 | depot | — | spare | 4 |
| line-3 | line-3-1040-0281-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/taiz-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **121 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **109 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **91 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0637-1074-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0612-0734-s007007 | forward | revenue | 5 | pending |
| line-1 | line-1-0612-0734-s007007 | reverse | revenue | 5 | pending |
| line-1 | line-1-0593-0639-s009065 | forward | revenue | 5 | pending |
| line-1 | line-1-0593-0639-s009065 | reverse | revenue | 5 | pending |
| line-1 | line-1-0575-0544-s011125 | forward | revenue | 5 | pending |
| line-1 | line-1-0575-0544-s011125 | reverse | revenue | 5 | pending |
| line-1 | line-1-0550-0420-s013812 | forward | revenue | 5 | pending |
| line-1 | line-1-0550-0420-s013812 | reverse | revenue | 4 | pending |
| line-1 | line-1-0526-0296-s016491 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0420-s013812 | reverse | spare | 1 | pending |
| line-1 | line-1-0526-0296-s016491 | reverse | spare | 1 | pending |
| line-1 | line-1-0637-1074-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0734-s007007 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0734-s007007 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0405-0445-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0450-0601-s003516 | forward | revenue | 5 | pending |
| line-2 | line-2-0450-0601-s003516 | reverse | revenue | 4 | pending |
| line-2 | line-2-0483-0717-s006133 | reverse | revenue | 4 | pending |
| line-2 | line-2-0450-0601-s003516 | reverse | spare | 1 | pending |
| line-2 | line-2-0483-0717-s006133 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1040-0281-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0765-0457-s007005 | forward | revenue | 5 | pending |
| line-3 | line-3-0765-0457-s007005 | reverse | revenue | 5 | pending |
| line-3 | line-3-0641-0513-s010019 | forward | revenue | 4 | pending |
| line-3 | line-3-0641-0513-s010019 | reverse | revenue | 4 | pending |
| line-3 | line-3-0575-0544-s011631 | forward | revenue | 4 | pending |
| line-3 | line-3-0575-0544-s011631 | reverse | revenue | 4 | pending |
| line-3 | line-3-0450-0601-s014662 | forward | revenue | 4 | pending |
| line-3 | line-3-0450-0601-s014662 | reverse | revenue | 4 | pending |
| line-3 | line-3-0425-0612-s015253 | reverse | revenue | 4 | pending |
| line-3 | line-3-0641-0513-s010019 | forward | spare | 1 | pending |
| line-3 | line-3-0641-0513-s010019 | reverse | spare | 1 | pending |
| line-3 | line-3-0575-0544-s011631 | forward | spare | 1 | pending |
| line-3 | line-3-0575-0544-s011631 | reverse | spare | 1 | pending |
| line-3 | line-3-0450-0601-s014662 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**83 trainsets exceed the reference platform envelope**, requiring **4,938.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0526-0296-s016491 | 5 | 2 | 3 | 178.5 |
| line-1-0550-0420-s013812 | 10 | 2 | 8 | 476.0 |
| line-1-0575-0544-s011125 | 10 | 4 | 6 | 357.0 |
| line-1-0593-0639-s009065 | 10 | 2 | 8 | 476.0 |
| line-1-0612-0734-s007007 | 12 | 2 | 10 | 595.0 |
| line-1-0637-1074-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0405-0445-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0450-0601-s003516 | 10 | 4 | 6 | 357.0 |
| line-2-0483-0717-s006133 | 5 | 2 | 3 | 178.5 |
| line-3-0425-0612-s015253 | 4 | 2 | 2 | 119.0 |
| line-3-0450-0601-s014662 | 9 | 4 | 5 | 297.5 |
| line-3-0575-0544-s011631 | 10 | 4 | 6 | 357.0 |
| line-3-0641-0513-s010019 | 10 | 2 | 8 | 476.0 |
| line-3-0765-0457-s007005 | 10 | 2 | 8 | 476.0 |
| line-3-1040-0281-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Taiz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
