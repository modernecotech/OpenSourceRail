# Station and depot overnight allocation

Plan: **46 trainsets at stations + 84 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0516-0125-s017716 | line-1 | storage-at-existing-powered-service-point | 21 | 1,249.5 | 0 |
| line-2-0605-0103-s021169 | line-2 | storage-at-existing-powered-service-point | 30 | 1,785.0 | 0 |
| line-3-0249-1022-s021180 | line-3 | declared-depot | 33 | 1,963.5 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0492-0306-s013315 | station | forward | revenue | 1 |
| line-1 | line-1-0492-0306-s013315 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0478-s009052 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0478-s009052 | station | reverse | revenue | 1 |
| line-1 | line-1-0516-0125-s017716 | station | reverse | revenue | 2 |
| line-1 | line-1-0519-0208-s015515 | station | forward | revenue | 1 |
| line-1 | line-1-0519-0208-s015515 | station | reverse | revenue | 1 |
| line-1 | line-1-0522-0385-s011103 | station | forward | revenue | 1 |
| line-1 | line-1-0522-0385-s011103 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0614-s005084 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0614-s005084 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0544-s007028 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0544-s007028 | station | reverse | revenue | 1 |
| line-1 | line-1-0573-0701-s003022 | station | forward | revenue | 1 |
| line-1 | line-1-0573-0701-s003022 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0820-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0556-0544-s007896 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0544-s007896 | station | reverse | revenue | 1 |
| line-2 | line-2-0588-0577-s006030 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0577-s006030 | station | reverse | revenue | 1 |
| line-2 | line-2-0598-0252-s016608 | station | forward | revenue | 1 |
| line-2 | line-2-0598-0252-s016608 | station | reverse | revenue | 1 |
| line-2 | line-2-0605-0103-s021169 | station | reverse | revenue | 2 |
| line-2 | line-2-0618-0407-s012037 | station | forward | revenue | 1 |
| line-2 | line-2-0618-0407-s012037 | station | reverse | revenue | 1 |
| line-2 | line-2-0619-0503-s009959 | station | forward | revenue | 1 |
| line-2 | line-2-0619-0503-s009959 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0685-s003012 | station | forward | revenue | 1 |
| line-2 | line-2-0644-0685-s003012 | station | reverse | revenue | 1 |
| line-2 | line-2-0724-0790-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0249-1022-s021180 | station | reverse | revenue | 2 |
| line-3 | line-3-0509-0586-s009778 | station | forward | revenue | 1 |
| line-3 | line-3-0509-0586-s009778 | station | reverse | revenue | 1 |
| line-3 | line-3-0556-0544-s008013 | station | forward | revenue | 1 |
| line-3 | line-3-0556-0544-s008013 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0494-s006777 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0494-s006777 | station | reverse | revenue | 1 |
| line-3 | line-3-0686-0455-s003767 | station | forward | revenue | 1 |
| line-3 | line-3-0686-0455-s003767 | station | reverse | revenue | 1 |
| line-3 | line-3-0754-0339-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0516-0125-s017716 | depot | — | revenue | 17 |
| line-1 | line-1-0516-0125-s017716 | depot | — | spare | 3 |
| line-1 | line-1-0516-0125-s017716 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0605-0103-s021169 | depot | — | revenue | 25 |
| line-2 | line-2-0605-0103-s021169 | depot | — | spare | 4 |
| line-2 | line-2-0605-0103-s021169 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0249-1022-s021180 | depot | — | revenue | 28 |
| line-3 | line-3-0249-1022-s021180 | depot | — | spare | 4 |
| line-3 | line-3-0249-1022-s021180 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kenitra-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **84 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0603-0820-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0573-0701-s003022 | forward | revenue | 3 | pending |
| line-1 | line-1-0573-0701-s003022 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0614-s005084 | forward | revenue | 2 | pending |
| line-1 | line-1-0555-0614-s005084 | reverse | revenue | 2 | pending |
| line-1 | line-1-0556-0544-s007028 | forward | revenue | 2 | pending |
| line-1 | line-1-0556-0544-s007028 | reverse | revenue | 2 | pending |
| line-1 | line-1-0503-0478-s009052 | forward | revenue | 2 | pending |
| line-1 | line-1-0503-0478-s009052 | reverse | revenue | 2 | pending |
| line-1 | line-1-0522-0385-s011103 | forward | revenue | 2 | pending |
| line-1 | line-1-0522-0385-s011103 | reverse | revenue | 2 | pending |
| line-1 | line-1-0492-0306-s013315 | forward | revenue | 2 | pending |
| line-1 | line-1-0492-0306-s013315 | reverse | revenue | 2 | pending |
| line-1 | line-1-0519-0208-s015515 | forward | revenue | 2 | pending |
| line-1 | line-1-0519-0208-s015515 | reverse | revenue | 2 | pending |
| line-1 | line-1-0516-0125-s017716 | reverse | revenue | 2 | pending |
| line-1 | line-1-0555-0614-s005084 | forward | spare | 1 | pending |
| line-1 | line-1-0555-0614-s005084 | reverse | spare | 1 | pending |
| line-1 | line-1-0556-0544-s007028 | forward | spare | 1 | pending |
| line-1 | line-1-0556-0544-s007028 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0724-0790-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0644-0685-s003012 | forward | revenue | 3 | pending |
| line-2 | line-2-0644-0685-s003012 | reverse | revenue | 3 | pending |
| line-2 | line-2-0588-0577-s006030 | forward | revenue | 3 | pending |
| line-2 | line-2-0588-0577-s006030 | reverse | revenue | 3 | pending |
| line-2 | line-2-0556-0544-s007896 | forward | revenue | 3 | pending |
| line-2 | line-2-0556-0544-s007896 | reverse | revenue | 3 | pending |
| line-2 | line-2-0619-0503-s009959 | forward | revenue | 3 | pending |
| line-2 | line-2-0619-0503-s009959 | reverse | revenue | 3 | pending |
| line-2 | line-2-0618-0407-s012037 | forward | revenue | 3 | pending |
| line-2 | line-2-0618-0407-s012037 | reverse | revenue | 3 | pending |
| line-2 | line-2-0598-0252-s016608 | forward | revenue | 3 | pending |
| line-2 | line-2-0598-0252-s016608 | reverse | revenue | 3 | pending |
| line-2 | line-2-0605-0103-s021169 | reverse | revenue | 2 | pending |
| line-2 | line-2-0605-0103-s021169 | reverse | spare | 1 | pending |
| line-2 | line-2-0724-0790-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0644-0685-s003012 | forward | spare | 1 | pending |
| line-2 | line-2-0644-0685-s003012 | reverse | spare | 1 | pending |
| line-2 | line-2-0588-0577-s006030 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0754-0339-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0686-0455-s003767 | forward | revenue | 4 | pending |
| line-3 | line-3-0686-0455-s003767 | reverse | revenue | 4 | pending |
| line-3 | line-3-0567-0494-s006777 | forward | revenue | 4 | pending |
| line-3 | line-3-0567-0494-s006777 | reverse | revenue | 4 | pending |
| line-3 | line-3-0556-0544-s008013 | forward | revenue | 4 | pending |
| line-3 | line-3-0556-0544-s008013 | reverse | revenue | 4 | pending |
| line-3 | line-3-0509-0586-s009778 | forward | revenue | 4 | pending |
| line-3 | line-3-0509-0586-s009778 | reverse | revenue | 4 | pending |
| line-3 | line-3-0249-1022-s021180 | reverse | revenue | 4 | pending |
| line-3 | line-3-0754-0339-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0686-0455-s003767 | forward | spare | 1 | pending |
| line-3 | line-3-0686-0455-s003767 | reverse | spare | 1 | pending |
| line-3 | line-3-0567-0494-s006777 | forward | spare | 1 | pending |
| line-3 | line-3-0567-0494-s006777 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**78 trainsets exceed the reference platform envelope**, requiring **4,641.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0492-0306-s013315 | 4 | 2 | 2 | 119.0 |
| line-1-0503-0478-s009052 | 4 | 2 | 2 | 119.0 |
| line-1-0516-0125-s017716 | 2 | 2 | 0 | 0.0 |
| line-1-0519-0208-s015515 | 4 | 2 | 2 | 119.0 |
| line-1-0522-0385-s011103 | 4 | 2 | 2 | 119.0 |
| line-1-0555-0614-s005084 | 6 | 2 | 4 | 238.0 |
| line-1-0556-0544-s007028 | 6 | 4 | 2 | 119.0 |
| line-1-0573-0701-s003022 | 6 | 2 | 4 | 238.0 |
| line-1-0603-0820-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0556-0544-s007896 | 6 | 4 | 2 | 119.0 |
| line-2-0588-0577-s006030 | 7 | 2 | 5 | 297.5 |
| line-2-0598-0252-s016608 | 6 | 2 | 4 | 238.0 |
| line-2-0605-0103-s021169 | 3 | 2 | 1 | 59.5 |
| line-2-0618-0407-s012037 | 6 | 2 | 4 | 238.0 |
| line-2-0619-0503-s009959 | 6 | 2 | 4 | 238.0 |
| line-2-0644-0685-s003012 | 8 | 2 | 6 | 357.0 |
| line-2-0724-0790-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0249-1022-s021180 | 4 | 2 | 2 | 119.0 |
| line-3-0509-0586-s009778 | 8 | 2 | 6 | 357.0 |
| line-3-0556-0544-s008013 | 8 | 4 | 4 | 238.0 |
| line-3-0567-0494-s006777 | 10 | 2 | 8 | 476.0 |
| line-3-0686-0455-s003767 | 10 | 2 | 8 | 476.0 |
| line-3-0754-0339-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Kenitra/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
