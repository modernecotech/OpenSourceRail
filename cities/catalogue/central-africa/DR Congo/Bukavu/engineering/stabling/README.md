# Station and depot overnight allocation

Plan: **44 trainsets at stations + 86 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0642-0400-s018281 | line-1 | storage-at-existing-powered-service-point | 26 | 1,547.0 | 0 |
| line-2-0859-1060-s023646 | line-2 | declared-depot | 33 | 1,963.5 | 20 |
| line-3-0104-0927-s019448 | line-3 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0325-0925-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0394-0764-s006028 | station | forward | revenue | 1 |
| line-1 | line-1-0394-0764-s006028 | station | reverse | revenue | 1 |
| line-1 | line-1-0420-0849-s003025 | station | forward | revenue | 1 |
| line-1 | line-1-0420-0849-s003025 | station | reverse | revenue | 1 |
| line-1 | line-1-0462-0658-s009029 | station | forward | revenue | 1 |
| line-1 | line-1-0462-0658-s009029 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0577-s011949 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0577-s011949 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0527-s014584 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0527-s014584 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0400-s018281 | station | reverse | revenue | 2 |
| line-2 | line-2-0309-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0406-0459-s003020 | station | forward | revenue | 1 |
| line-2 | line-2-0406-0459-s003020 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0571-s006039 | station | forward | revenue | 1 |
| line-2 | line-2-0479-0571-s006039 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0577-s008540 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0577-s008540 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0637-s010426 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0637-s010426 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0700-s012308 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0700-s012308 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0848-s016063 | station | forward | revenue | 1 |
| line-2 | line-2-0710-0848-s016063 | station | reverse | revenue | 1 |
| line-2 | line-2-0859-1060-s023646 | station | reverse | revenue | 2 |
| line-3 | line-3-0104-0927-s019448 | station | reverse | revenue | 2 |
| line-3 | line-3-0223-0834-s015632 | station | forward | revenue | 1 |
| line-3 | line-3-0223-0834-s015632 | station | reverse | revenue | 1 |
| line-3 | line-3-0341-0799-s012632 | station | forward | revenue | 1 |
| line-3 | line-3-0341-0799-s012632 | station | reverse | revenue | 1 |
| line-3 | line-3-0426-0662-s009053 | station | forward | revenue | 1 |
| line-3 | line-3-0426-0662-s009053 | station | reverse | revenue | 1 |
| line-3 | line-3-0544-0577-s005469 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0577-s005469 | station | reverse | revenue | 1 |
| line-3 | line-3-0644-0598-s003011 | station | forward | revenue | 1 |
| line-3 | line-3-0644-0598-s003011 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0574-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0642-0400-s018281 | depot | — | revenue | 22 |
| line-1 | line-1-0642-0400-s018281 | depot | — | spare | 3 |
| line-1 | line-1-0642-0400-s018281 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0859-1060-s023646 | depot | — | revenue | 28 |
| line-2 | line-2-0859-1060-s023646 | depot | — | spare | 4 |
| line-2 | line-2-0859-1060-s023646 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0104-0927-s019448 | depot | — | revenue | 23 |
| line-3 | line-3-0104-0927-s019448 | depot | — | spare | 3 |
| line-3 | line-3-0104-0927-s019448 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bukavu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **86 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0325-0925-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0420-0849-s003025 | forward | revenue | 3 | pending |
| line-1 | line-1-0420-0849-s003025 | reverse | revenue | 3 | pending |
| line-1 | line-1-0394-0764-s006028 | forward | revenue | 3 | pending |
| line-1 | line-1-0394-0764-s006028 | reverse | revenue | 3 | pending |
| line-1 | line-1-0462-0658-s009029 | forward | revenue | 3 | pending |
| line-1 | line-1-0462-0658-s009029 | reverse | revenue | 3 | pending |
| line-1 | line-1-0544-0577-s011949 | forward | revenue | 3 | pending |
| line-1 | line-1-0544-0577-s011949 | reverse | revenue | 3 | pending |
| line-1 | line-1-0606-0527-s014584 | forward | revenue | 3 | pending |
| line-1 | line-1-0606-0527-s014584 | reverse | revenue | 3 | pending |
| line-1 | line-1-0642-0400-s018281 | reverse | revenue | 3 | pending |
| line-1 | line-1-0325-0925-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0420-0849-s003025 | forward | spare | 1 | pending |
| line-1 | line-1-0420-0849-s003025 | reverse | spare | 1 | pending |
| line-1 | line-1-0394-0764-s006028 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0309-0394-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0406-0459-s003020 | forward | revenue | 4 | pending |
| line-2 | line-2-0406-0459-s003020 | reverse | revenue | 3 | pending |
| line-2 | line-2-0479-0571-s006039 | forward | revenue | 3 | pending |
| line-2 | line-2-0479-0571-s006039 | reverse | revenue | 3 | pending |
| line-2 | line-2-0544-0577-s008540 | forward | revenue | 3 | pending |
| line-2 | line-2-0544-0577-s008540 | reverse | revenue | 3 | pending |
| line-2 | line-2-0565-0637-s010426 | forward | revenue | 3 | pending |
| line-2 | line-2-0565-0637-s010426 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0700-s012308 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0700-s012308 | reverse | revenue | 3 | pending |
| line-2 | line-2-0710-0848-s016063 | forward | revenue | 3 | pending |
| line-2 | line-2-0710-0848-s016063 | reverse | revenue | 3 | pending |
| line-2 | line-2-0859-1060-s023646 | reverse | revenue | 3 | pending |
| line-2 | line-2-0406-0459-s003020 | reverse | spare | 1 | pending |
| line-2 | line-2-0479-0571-s006039 | forward | spare | 1 | pending |
| line-2 | line-2-0479-0571-s006039 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0577-s008540 | forward | spare | 1 | pending |
| line-2 | line-2-0544-0577-s008540 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0644-0598-s003011 | forward | revenue | 3 | pending |
| line-3 | line-3-0644-0598-s003011 | reverse | revenue | 3 | pending |
| line-3 | line-3-0544-0577-s005469 | forward | revenue | 3 | pending |
| line-3 | line-3-0544-0577-s005469 | reverse | revenue | 3 | pending |
| line-3 | line-3-0426-0662-s009053 | forward | revenue | 3 | pending |
| line-3 | line-3-0426-0662-s009053 | reverse | revenue | 3 | pending |
| line-3 | line-3-0341-0799-s012632 | forward | revenue | 3 | pending |
| line-3 | line-3-0341-0799-s012632 | reverse | revenue | 3 | pending |
| line-3 | line-3-0223-0834-s015632 | forward | revenue | 3 | pending |
| line-3 | line-3-0223-0834-s015632 | reverse | revenue | 3 | pending |
| line-3 | line-3-0104-0927-s019448 | reverse | revenue | 3 | pending |
| line-3 | line-3-0644-0598-s003011 | forward | spare | 1 | pending |
| line-3 | line-3-0644-0598-s003011 | reverse | spare | 1 | pending |
| line-3 | line-3-0544-0577-s005469 | forward | spare | 1 | pending |
| line-3 | line-3-0544-0577-s005469 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**80 trainsets exceed the reference platform envelope**, requiring **4,760.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0325-0925-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0394-0764-s006028 | 7 | 2 | 5 | 297.5 |
| line-1-0420-0849-s003025 | 8 | 2 | 6 | 357.0 |
| line-1-0462-0658-s009029 | 6 | 2 | 4 | 238.0 |
| line-1-0544-0577-s011949 | 6 | 4 | 2 | 119.0 |
| line-1-0606-0527-s014584 | 6 | 2 | 4 | 238.0 |
| line-1-0642-0400-s018281 | 3 | 2 | 1 | 59.5 |
| line-2-0309-0394-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0406-0459-s003020 | 8 | 2 | 6 | 357.0 |
| line-2-0479-0571-s006039 | 8 | 2 | 6 | 357.0 |
| line-2-0544-0577-s008540 | 8 | 4 | 4 | 238.0 |
| line-2-0565-0637-s010426 | 6 | 2 | 4 | 238.0 |
| line-2-0626-0700-s012308 | 6 | 2 | 4 | 238.0 |
| line-2-0710-0848-s016063 | 6 | 2 | 4 | 238.0 |
| line-2-0859-1060-s023646 | 3 | 2 | 1 | 59.5 |
| line-3-0104-0927-s019448 | 3 | 2 | 1 | 59.5 |
| line-3-0223-0834-s015632 | 6 | 2 | 4 | 238.0 |
| line-3-0341-0799-s012632 | 6 | 2 | 4 | 238.0 |
| line-3-0426-0662-s009053 | 6 | 2 | 4 | 238.0 |
| line-3-0544-0577-s005469 | 8 | 4 | 4 | 238.0 |
| line-3-0644-0598-s003011 | 8 | 2 | 6 | 357.0 |
| line-3-0764-0574-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Bukavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
