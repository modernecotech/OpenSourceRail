# Station and depot overnight allocation

Plan: **40 trainsets at stations + 94 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0332-0209-s022602 | 94 | 5,593.0 | 21 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0308-0707-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0396-0636-s003184 | station | forward | revenue | 1 |
| line-1 | line-1-0396-0636-s003184 | station | reverse | revenue | 1 |
| line-1 | line-1-0517-0622-s005720 | station | forward | revenue | 1 |
| line-1 | line-1-0517-0622-s005720 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0556-s007502 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0556-s007502 | station | reverse | revenue | 1 |
| line-1 | line-1-0596-0515-s008742 | station | forward | revenue | 1 |
| line-1 | line-1-0596-0515-s008742 | station | reverse | revenue | 1 |
| line-1 | line-1-0729-0472-s011758 | station | forward | revenue | 1 |
| line-1 | line-1-0729-0472-s011758 | station | reverse | revenue | 1 |
| line-1 | line-1-1041-0391-s018669 | station | reverse | revenue | 2 |
| line-2 | line-2-0332-0209-s022602 | station | reverse | revenue | 2 |
| line-2 | line-2-0490-0470-s016073 | station | forward | revenue | 1 |
| line-2 | line-2-0490-0470-s016073 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0556-s013848 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0556-s013848 | station | reverse | revenue | 1 |
| line-2 | line-2-0592-0630-s011953 | station | forward | revenue | 1 |
| line-2 | line-2-0592-0630-s011953 | station | reverse | revenue | 1 |
| line-2 | line-2-0660-0682-s010045 | station | forward | revenue | 1 |
| line-2 | line-2-0660-0682-s010045 | station | reverse | revenue | 1 |
| line-2 | line-2-0722-0779-s007021 | station | forward | revenue | 1 |
| line-2 | line-2-0722-0779-s007021 | station | reverse | revenue | 1 |
| line-2 | line-2-0980-0964-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0424-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0511-0688-s003013 | station | forward | revenue | 1 |
| line-3 | line-3-0511-0688-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0617-s004632 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0617-s004632 | station | reverse | revenue | 1 |
| line-3 | line-3-0551-0556-s005985 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0556-s005985 | station | reverse | revenue | 1 |
| line-3 | line-3-0552-0474-s007633 | station | forward | revenue | 1 |
| line-3 | line-3-0552-0474-s007633 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0193-s014131 | station | reverse | revenue | 2 |
| line-1 | line-2-0332-0209-s022602 | depot | — | revenue | 27 |
| line-1 | line-2-0332-0209-s022602 | depot | — | spare | 4 |
| line-1 | line-2-0332-0209-s022602 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0209-s022602 | depot | — | revenue | 34 |
| line-2 | line-2-0332-0209-s022602 | depot | — | spare | 4 |
| line-2 | line-2-0332-0209-s022602 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0332-0209-s022602 | depot | — | revenue | 19 |
| line-3 | line-2-0332-0209-s022602 | depot | — | spare | 3 |
| line-3 | line-2-0332-0209-s022602 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (32 trains), line-3 (23 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 20 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **94 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0308-0707-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0396-0636-s003184 | forward | revenue | 4 | pending |
| line-1 | line-1-0396-0636-s003184 | reverse | revenue | 4 | pending |
| line-1 | line-1-0517-0622-s005720 | forward | revenue | 4 | pending |
| line-1 | line-1-0517-0622-s005720 | reverse | revenue | 4 | pending |
| line-1 | line-1-0551-0556-s007502 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0556-s007502 | reverse | revenue | 3 | pending |
| line-1 | line-1-0596-0515-s008742 | forward | revenue | 3 | pending |
| line-1 | line-1-0596-0515-s008742 | reverse | revenue | 3 | pending |
| line-1 | line-1-0729-0472-s011758 | forward | revenue | 3 | pending |
| line-1 | line-1-0729-0472-s011758 | reverse | revenue | 3 | pending |
| line-1 | line-1-1041-0391-s018669 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0556-s007502 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0556-s007502 | reverse | spare | 1 | pending |
| line-1 | line-1-0596-0515-s008742 | forward | spare | 1 | pending |
| line-1 | line-1-0596-0515-s008742 | reverse | spare | 1 | pending |
| line-1 | line-1-0729-0472-s011758 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0722-0779-s007021 | forward | revenue | 4 | pending |
| line-2 | line-2-0722-0779-s007021 | reverse | revenue | 4 | pending |
| line-2 | line-2-0660-0682-s010045 | forward | revenue | 4 | pending |
| line-2 | line-2-0660-0682-s010045 | reverse | revenue | 4 | pending |
| line-2 | line-2-0592-0630-s011953 | forward | revenue | 4 | pending |
| line-2 | line-2-0592-0630-s011953 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0556-s013848 | forward | revenue | 4 | pending |
| line-2 | line-2-0551-0556-s013848 | reverse | revenue | 4 | pending |
| line-2 | line-2-0490-0470-s016073 | forward | revenue | 4 | pending |
| line-2 | line-2-0490-0470-s016073 | reverse | revenue | 4 | pending |
| line-2 | line-2-0332-0209-s022602 | reverse | revenue | 4 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0722-0779-s007021 | forward | spare | 1 | pending |
| line-2 | line-2-0722-0779-s007021 | reverse | spare | 1 | pending |
| line-2 | line-2-0660-0682-s010045 | forward | spare | 1 | pending |
| line-2 | line-2-0660-0682-s010045 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0511-0688-s003013 | forward | revenue | 3 | pending |
| line-3 | line-3-0511-0688-s003013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0535-0617-s004632 | forward | revenue | 3 | pending |
| line-3 | line-3-0535-0617-s004632 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0556-s005985 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0556-s005985 | reverse | revenue | 3 | pending |
| line-3 | line-3-0552-0474-s007633 | forward | revenue | 3 | pending |
| line-3 | line-3-0552-0474-s007633 | reverse | revenue | 3 | pending |
| line-3 | line-3-0658-0193-s014131 | reverse | revenue | 3 | pending |
| line-3 | line-3-0511-0688-s003013 | forward | spare | 1 | pending |
| line-3 | line-3-0511-0688-s003013 | reverse | spare | 1 | pending |
| line-3 | line-3-0535-0617-s004632 | forward | spare | 1 | pending |
| line-3 | line-3-0535-0617-s004632 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**84 trainsets exceed the reference platform envelope**, requiring **4,998.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0308-0707-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0396-0636-s003184 | 8 | 2 | 6 | 357.0 |
| line-1-0517-0622-s005720 | 8 | 4 | 4 | 238.0 |
| line-1-0551-0556-s007502 | 8 | 4 | 4 | 238.0 |
| line-1-0596-0515-s008742 | 8 | 2 | 6 | 357.0 |
| line-1-0729-0472-s011758 | 7 | 2 | 5 | 297.5 |
| line-1-1041-0391-s018669 | 3 | 2 | 1 | 59.5 |
| line-2-0332-0209-s022602 | 4 | 2 | 2 | 119.0 |
| line-2-0490-0470-s016073 | 8 | 2 | 6 | 357.0 |
| line-2-0551-0556-s013848 | 8 | 4 | 4 | 238.0 |
| line-2-0592-0630-s011953 | 8 | 2 | 6 | 357.0 |
| line-2-0660-0682-s010045 | 10 | 2 | 8 | 476.0 |
| line-2-0722-0779-s007021 | 10 | 2 | 8 | 476.0 |
| line-2-0980-0964-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0424-0761-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0511-0688-s003013 | 8 | 2 | 6 | 357.0 |
| line-3-0535-0617-s004632 | 8 | 4 | 4 | 238.0 |
| line-3-0551-0556-s005985 | 6 | 4 | 2 | 119.0 |
| line-3-0552-0474-s007633 | 6 | 2 | 4 | 238.0 |
| line-3-0658-0193-s014131 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sialkot/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
