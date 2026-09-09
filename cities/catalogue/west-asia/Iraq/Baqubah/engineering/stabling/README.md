# Station and depot overnight allocation

Plan: **38 trainsets at stations + 92 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0395-0236-s015558 | line-1 | storage-at-existing-powered-service-point | 24 | 1,428.0 | 0 |
| line-2-0185-1002-s021939 | line-2 | storage-at-existing-powered-service-point | 34 | 2,023.0 | 0 |
| line-3-0927-0228-s023376 | line-3 | declared-depot | 34 | 2,023.0 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0395-0236-s015558 | station | reverse | revenue | 2 |
| line-1 | line-1-0490-0409-s009008 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0409-s009008 | station | reverse | revenue | 1 |
| line-1 | line-1-0558-0516-s005381 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0516-s005381 | station | reverse | revenue | 1 |
| line-1 | line-1-0664-0504-s003001 | station | forward | revenue | 1 |
| line-1 | line-1-0664-0504-s003001 | station | reverse | revenue | 1 |
| line-1 | line-1-0811-0508-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0185-1002-s021939 | station | reverse | revenue | 2 |
| line-2 | line-2-0493-0669-s012034 | station | forward | revenue | 1 |
| line-2 | line-2-0493-0669-s012034 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0516-s008324 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0516-s008324 | station | reverse | revenue | 1 |
| line-2 | line-2-0582-0422-s006024 | station | forward | revenue | 1 |
| line-2 | line-2-0582-0422-s006024 | station | reverse | revenue | 1 |
| line-2 | line-2-0640-0311-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0640-0311-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0711-0229-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0123-0580-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0379-0535-s007013 | station | forward | revenue | 1 |
| line-3 | line-3-0379-0535-s007013 | station | reverse | revenue | 1 |
| line-3 | line-3-0499-0473-s010013 | station | forward | revenue | 1 |
| line-3 | line-3-0499-0473-s010013 | station | reverse | revenue | 1 |
| line-3 | line-3-0558-0516-s011730 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0516-s011730 | station | reverse | revenue | 1 |
| line-3 | line-3-0603-0480-s013018 | station | forward | revenue | 1 |
| line-3 | line-3-0603-0480-s013018 | station | reverse | revenue | 1 |
| line-3 | line-3-0709-0428-s016024 | station | forward | revenue | 1 |
| line-3 | line-3-0709-0428-s016024 | station | reverse | revenue | 1 |
| line-3 | line-3-0733-0315-s018483 | station | forward | revenue | 1 |
| line-3 | line-3-0733-0315-s018483 | station | reverse | revenue | 1 |
| line-3 | line-3-0927-0228-s023376 | station | reverse | revenue | 2 |
| line-1 | line-1-0395-0236-s015558 | depot | — | revenue | 20 |
| line-1 | line-1-0395-0236-s015558 | depot | — | spare | 3 |
| line-1 | line-1-0395-0236-s015558 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0185-1002-s021939 | depot | — | revenue | 29 |
| line-2 | line-2-0185-1002-s021939 | depot | — | spare | 4 |
| line-2 | line-2-0185-1002-s021939 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0927-0228-s023376 | depot | — | revenue | 29 |
| line-3 | line-3-0927-0228-s023376 | depot | — | spare | 4 |
| line-3 | line-3-0927-0228-s023376 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/baqubah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **92 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0811-0508-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0664-0504-s003001 | forward | revenue | 4 | pending |
| line-1 | line-1-0664-0504-s003001 | reverse | revenue | 4 | pending |
| line-1 | line-1-0558-0516-s005381 | forward | revenue | 4 | pending |
| line-1 | line-1-0558-0516-s005381 | reverse | revenue | 4 | pending |
| line-1 | line-1-0490-0409-s009008 | forward | revenue | 4 | pending |
| line-1 | line-1-0490-0409-s009008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0395-0236-s015558 | reverse | revenue | 3 | pending |
| line-1 | line-1-0490-0409-s009008 | reverse | spare | 1 | pending |
| line-1 | line-1-0395-0236-s015558 | reverse | spare | 1 | pending |
| line-1 | line-1-0811-0508-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0664-0504-s003001 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0711-0229-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0640-0311-s003018 | forward | revenue | 4 | pending |
| line-2 | line-2-0640-0311-s003018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0582-0422-s006024 | forward | revenue | 4 | pending |
| line-2 | line-2-0582-0422-s006024 | reverse | revenue | 4 | pending |
| line-2 | line-2-0558-0516-s008324 | forward | revenue | 4 | pending |
| line-2 | line-2-0558-0516-s008324 | reverse | revenue | 4 | pending |
| line-2 | line-2-0493-0669-s012034 | forward | revenue | 4 | pending |
| line-2 | line-2-0493-0669-s012034 | reverse | revenue | 4 | pending |
| line-2 | line-2-0185-1002-s021939 | reverse | revenue | 4 | pending |
| line-2 | line-2-0640-0311-s003018 | forward | spare | 1 | pending |
| line-2 | line-2-0640-0311-s003018 | reverse | spare | 1 | pending |
| line-2 | line-2-0582-0422-s006024 | forward | spare | 1 | pending |
| line-2 | line-2-0582-0422-s006024 | reverse | spare | 1 | pending |
| line-2 | line-2-0558-0516-s008324 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0123-0580-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0379-0535-s007013 | forward | revenue | 4 | pending |
| line-3 | line-3-0379-0535-s007013 | reverse | revenue | 4 | pending |
| line-3 | line-3-0499-0473-s010013 | forward | revenue | 3 | pending |
| line-3 | line-3-0499-0473-s010013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0558-0516-s011730 | forward | revenue | 3 | pending |
| line-3 | line-3-0558-0516-s011730 | reverse | revenue | 3 | pending |
| line-3 | line-3-0603-0480-s013018 | forward | revenue | 3 | pending |
| line-3 | line-3-0603-0480-s013018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0709-0428-s016024 | forward | revenue | 3 | pending |
| line-3 | line-3-0709-0428-s016024 | reverse | revenue | 3 | pending |
| line-3 | line-3-0733-0315-s018483 | forward | revenue | 3 | pending |
| line-3 | line-3-0733-0315-s018483 | reverse | revenue | 3 | pending |
| line-3 | line-3-0927-0228-s023376 | reverse | revenue | 3 | pending |
| line-3 | line-3-0499-0473-s010013 | forward | spare | 1 | pending |
| line-3 | line-3-0499-0473-s010013 | reverse | spare | 1 | pending |
| line-3 | line-3-0558-0516-s011730 | forward | spare | 1 | pending |
| line-3 | line-3-0558-0516-s011730 | reverse | spare | 1 | pending |
| line-3 | line-3-0603-0480-s013018 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0395-0236-s015558 | 4 | 2 | 2 | 119.0 |
| line-1-0490-0409-s009008 | 8 | 2 | 6 | 357.0 |
| line-1-0558-0516-s005381 | 8 | 4 | 4 | 238.0 |
| line-1-0664-0504-s003001 | 9 | 2 | 7 | 416.5 |
| line-1-0811-0508-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0185-1002-s021939 | 4 | 2 | 2 | 119.0 |
| line-2-0493-0669-s012034 | 8 | 2 | 6 | 357.0 |
| line-2-0558-0516-s008324 | 9 | 4 | 5 | 297.5 |
| line-2-0582-0422-s006024 | 10 | 2 | 8 | 476.0 |
| line-2-0640-0311-s003018 | 10 | 2 | 8 | 476.0 |
| line-2-0711-0229-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0123-0580-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0379-0535-s007013 | 8 | 2 | 6 | 357.0 |
| line-3-0499-0473-s010013 | 8 | 2 | 6 | 357.0 |
| line-3-0558-0516-s011730 | 8 | 4 | 4 | 238.0 |
| line-3-0603-0480-s013018 | 7 | 2 | 5 | 297.5 |
| line-3-0709-0428-s016024 | 6 | 2 | 4 | 238.0 |
| line-3-0733-0315-s018483 | 6 | 2 | 4 | 238.0 |
| line-3-0927-0228-s023376 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Baqubah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
