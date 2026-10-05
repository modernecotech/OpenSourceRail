# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 122 at depots = 162 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0603-0820-s000000 | line-1 | declared-depot | 35 | 2,082.5 | 8 |
| line-2-0724-0790-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0249-1022-s019099 | line-3 | declared-depot | 48 | 2,856.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0516-0125-s015136 | station | reverse | revenue | 2 |
| line-1 | line-1-0519-0199-s013116 | station | forward | revenue | 1 |
| line-1 | line-1-0519-0199-s013116 | station | reverse | revenue | 1 |
| line-1 | line-1-0530-0296-s011085 | station | forward | revenue | 1 |
| line-1 | line-1-0530-0296-s011085 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0392-s009049 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0392-s009049 | station | reverse | revenue | 1 |
| line-1 | line-1-0557-0488-s007021 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0488-s007021 | station | reverse | revenue | 1 |
| line-1 | line-1-0570-0583-s005013 | station | forward | revenue | 1 |
| line-1 | line-1-0570-0583-s005013 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0678-s003006 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0678-s003006 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0820-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0587-0274-s011514 | station | forward | revenue | 1 |
| line-2 | line-2-0587-0274-s011514 | station | reverse | revenue | 1 |
| line-2 | line-2-0605-0103-s016280 | station | reverse | revenue | 2 |
| line-2 | line-2-0615-0381-s009130 | station | forward | revenue | 1 |
| line-2 | line-2-0615-0381-s009130 | station | reverse | revenue | 1 |
| line-2 | line-2-0643-0487-s006766 | station | forward | revenue | 1 |
| line-2 | line-2-0643-0487-s006766 | station | reverse | revenue | 1 |
| line-2 | line-2-0682-0631-s003551 | station | forward | revenue | 1 |
| line-2 | line-2-0682-0631-s003551 | station | reverse | revenue | 1 |
| line-2 | line-2-0724-0790-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0249-1022-s019099 | station | reverse | revenue | 2 |
| line-3 | line-3-0461-0726-s010917 | station | forward | revenue | 1 |
| line-3 | line-3-0461-0726-s010917 | station | reverse | revenue | 1 |
| line-3 | line-3-0517-0653-s008888 | station | forward | revenue | 1 |
| line-3 | line-3-0517-0653-s008888 | station | reverse | revenue | 1 |
| line-3 | line-3-0570-0583-s006838 | station | forward | revenue | 1 |
| line-3 | line-3-0570-0583-s006838 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0487-s004137 | station | forward | revenue | 1 |
| line-3 | line-3-0643-0487-s004137 | station | reverse | revenue | 1 |
| line-3 | line-3-0754-0339-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0603-0820-s000000 | depot | — | revenue | 30 |
| line-1 | line-1-0603-0820-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0603-0820-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0724-0790-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0724-0790-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0724-0790-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0249-1022-s019099 | depot | — | revenue | 42 |
| line-3 | line-3-0249-1022-s019099 | depot | — | spare | 5 |
| line-3 | line-3-0249-1022-s019099 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kenitra-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **162 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **146 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **122 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0603-0820-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0583-0678-s003006 | forward | revenue | 4 | pending |
| line-1 | line-1-0583-0678-s003006 | reverse | revenue | 4 | pending |
| line-1 | line-1-0570-0583-s005013 | forward | revenue | 4 | pending |
| line-1 | line-1-0570-0583-s005013 | reverse | revenue | 3 | pending |
| line-1 | line-1-0557-0488-s007021 | forward | revenue | 3 | pending |
| line-1 | line-1-0557-0488-s007021 | reverse | revenue | 3 | pending |
| line-1 | line-1-0544-0392-s009049 | forward | revenue | 3 | pending |
| line-1 | line-1-0544-0392-s009049 | reverse | revenue | 3 | pending |
| line-1 | line-1-0530-0296-s011085 | forward | revenue | 3 | pending |
| line-1 | line-1-0530-0296-s011085 | reverse | revenue | 3 | pending |
| line-1 | line-1-0519-0199-s013116 | forward | revenue | 3 | pending |
| line-1 | line-1-0519-0199-s013116 | reverse | revenue | 3 | pending |
| line-1 | line-1-0516-0125-s015136 | reverse | revenue | 3 | pending |
| line-1 | line-1-0570-0583-s005013 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0488-s007021 | forward | spare | 1 | pending |
| line-1 | line-1-0557-0488-s007021 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0392-s009049 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0392-s009049 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0724-0790-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0682-0631-s003551 | forward | revenue | 5 | pending |
| line-2 | line-2-0682-0631-s003551 | reverse | revenue | 5 | pending |
| line-2 | line-2-0643-0487-s006766 | forward | revenue | 5 | pending |
| line-2 | line-2-0643-0487-s006766 | reverse | revenue | 5 | pending |
| line-2 | line-2-0615-0381-s009130 | forward | revenue | 5 | pending |
| line-2 | line-2-0615-0381-s009130 | reverse | revenue | 4 | pending |
| line-2 | line-2-0587-0274-s011514 | forward | revenue | 4 | pending |
| line-2 | line-2-0587-0274-s011514 | reverse | revenue | 4 | pending |
| line-2 | line-2-0605-0103-s016280 | reverse | revenue | 4 | pending |
| line-2 | line-2-0615-0381-s009130 | reverse | spare | 1 | pending |
| line-2 | line-2-0587-0274-s011514 | forward | spare | 1 | pending |
| line-2 | line-2-0587-0274-s011514 | reverse | spare | 1 | pending |
| line-2 | line-2-0605-0103-s016280 | reverse | spare | 1 | pending |
| line-2 | line-2-0724-0790-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0754-0339-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0643-0487-s004137 | forward | revenue | 6 | pending |
| line-3 | line-3-0643-0487-s004137 | reverse | revenue | 6 | pending |
| line-3 | line-3-0570-0583-s006838 | forward | revenue | 6 | pending |
| line-3 | line-3-0570-0583-s006838 | reverse | revenue | 5 | pending |
| line-3 | line-3-0517-0653-s008888 | forward | revenue | 5 | pending |
| line-3 | line-3-0517-0653-s008888 | reverse | revenue | 5 | pending |
| line-3 | line-3-0461-0726-s010917 | forward | revenue | 5 | pending |
| line-3 | line-3-0461-0726-s010917 | reverse | revenue | 5 | pending |
| line-3 | line-3-0249-1022-s019099 | reverse | revenue | 5 | pending |
| line-3 | line-3-0570-0583-s006838 | reverse | spare | 1 | pending |
| line-3 | line-3-0517-0653-s008888 | forward | spare | 1 | pending |
| line-3 | line-3-0517-0653-s008888 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0726-s010917 | forward | spare | 1 | pending |
| line-3 | line-3-0461-0726-s010917 | reverse | spare | 1 | pending |
| line-3 | line-3-0249-1022-s019099 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**114 trainsets exceed the reference platform envelope**, requiring **6,783.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0516-0125-s015136 | 3 | 2 | 1 | 59.5 |
| line-1-0519-0199-s013116 | 6 | 2 | 4 | 238.0 |
| line-1-0530-0296-s011085 | 6 | 2 | 4 | 238.0 |
| line-1-0544-0392-s009049 | 8 | 2 | 6 | 357.0 |
| line-1-0557-0488-s007021 | 8 | 2 | 6 | 357.0 |
| line-1-0570-0583-s005013 | 8 | 4 | 4 | 238.0 |
| line-1-0583-0678-s003006 | 8 | 2 | 6 | 357.0 |
| line-1-0603-0820-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0587-0274-s011514 | 10 | 2 | 8 | 476.0 |
| line-2-0605-0103-s016280 | 5 | 2 | 3 | 178.5 |
| line-2-0615-0381-s009130 | 10 | 2 | 8 | 476.0 |
| line-2-0643-0487-s006766 | 10 | 4 | 6 | 357.0 |
| line-2-0682-0631-s003551 | 10 | 2 | 8 | 476.0 |
| line-2-0724-0790-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0249-1022-s019099 | 6 | 2 | 4 | 238.0 |
| line-3-0461-0726-s010917 | 12 | 2 | 10 | 595.0 |
| line-3-0517-0653-s008888 | 12 | 2 | 10 | 595.0 |
| line-3-0570-0583-s006838 | 12 | 4 | 8 | 476.0 |
| line-3-0643-0487-s004137 | 12 | 4 | 8 | 476.0 |
| line-3-0754-0339-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Kenitra/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
