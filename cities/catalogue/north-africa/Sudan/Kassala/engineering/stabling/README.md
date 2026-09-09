# Station and depot overnight allocation

Plan: **22 trainsets at stations + 30 at depots = 52 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0752-0316-s010315 | line-1 | declared-depot | 13 | 773.5 | 8 |
| line-2-0533-0358-s006111 | line-2 | storage-at-existing-powered-service-point | 7 | 416.5 | 0 |
| line-3-0718-0353-s007120 | line-3 | storage-at-existing-powered-service-point | 10 | 595.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0422-0537-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0552-0547-s003138 | station | forward | revenue | 1 |
| line-1 | line-1-0552-0547-s003138 | station | reverse | revenue | 1 |
| line-1 | line-1-0580-0467-s005022 | station | forward | revenue | 1 |
| line-1 | line-1-0580-0467-s005022 | station | reverse | revenue | 1 |
| line-1 | line-1-0752-0316-s010315 | station | reverse | revenue | 2 |
| line-2 | line-2-0533-0358-s006111 | station | reverse | revenue | 2 |
| line-2 | line-2-0551-0487-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0487-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0547-s001748 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0547-s001748 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0629-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0533-0566-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0624-0469-s003018 | station | forward | revenue | 1 |
| line-3 | line-3-0624-0469-s003018 | station | reverse | revenue | 1 |
| line-3 | line-3-0718-0353-s007120 | station | reverse | revenue | 2 |
| line-1 | line-1-0752-0316-s010315 | depot | — | revenue | 11 |
| line-1 | line-1-0752-0316-s010315 | depot | — | spare | 1 |
| line-1 | line-1-0752-0316-s010315 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0533-0358-s006111 | depot | — | revenue | 5 |
| line-2 | line-2-0533-0358-s006111 | depot | — | spare | 1 |
| line-2 | line-2-0533-0358-s006111 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0718-0353-s007120 | depot | — | revenue | 8 |
| line-3 | line-3-0718-0353-s007120 | depot | — | spare | 1 |
| line-3 | line-3-0718-0353-s007120 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kassala-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **52 trainsets at 11 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **46 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **30 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0422-0537-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0552-0547-s003138 | forward | revenue | 3 | pending |
| line-1 | line-1-0552-0547-s003138 | reverse | revenue | 3 | pending |
| line-1 | line-1-0580-0467-s005022 | forward | revenue | 3 | pending |
| line-1 | line-1-0580-0467-s005022 | reverse | revenue | 3 | pending |
| line-1 | line-1-0752-0316-s010315 | reverse | revenue | 3 | pending |
| line-1 | line-1-0552-0547-s003138 | forward | spare | 1 | pending |
| line-1 | line-1-0552-0547-s003138 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0561-0629-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0547-s001748 | forward | revenue | 2 | pending |
| line-2 | line-2-0552-0547-s001748 | reverse | revenue | 2 | pending |
| line-2 | line-2-0551-0487-s003006 | forward | revenue | 2 | pending |
| line-2 | line-2-0551-0487-s003006 | reverse | revenue | 2 | pending |
| line-2 | line-2-0533-0358-s006111 | reverse | revenue | 2 | pending |
| line-2 | line-2-0552-0547-s001748 | forward | spare | 1 | pending |
| line-2 | line-2-0552-0547-s001748 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0566-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0624-0469-s003018 | forward | revenue | 4 | pending |
| line-3 | line-3-0624-0469-s003018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0718-0353-s007120 | reverse | revenue | 3 | pending |
| line-3 | line-3-0624-0469-s003018 | reverse | spare | 1 | pending |
| line-3 | line-3-0718-0353-s007120 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**26 trainsets exceed the reference platform envelope**, requiring **1,547.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0422-0537-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0552-0547-s003138 | 8 | 4 | 4 | 238.0 |
| line-1-0580-0467-s005022 | 6 | 2 | 4 | 238.0 |
| line-1-0752-0316-s010315 | 3 | 2 | 1 | 59.5 |
| line-2-0533-0358-s006111 | 2 | 2 | 0 | 0.0 |
| line-2-0551-0487-s003006 | 4 | 2 | 2 | 119.0 |
| line-2-0552-0547-s001748 | 6 | 4 | 2 | 119.0 |
| line-2-0561-0629-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0533-0566-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0624-0469-s003018 | 8 | 2 | 6 | 357.0 |
| line-3-0718-0353-s007120 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Kassala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
