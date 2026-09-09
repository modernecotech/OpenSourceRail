# Station and depot overnight allocation

Plan: **36 trainsets at stations + 111 at depots = 147 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0286-0224-s029156 | 111 | 6,604.5 | 23 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0286-0224-s029156 | station | reverse | revenue | 2 |
| line-1 | line-1-0435-0467-s022198 | station | forward | revenue | 1 |
| line-1 | line-1-0435-0467-s022198 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0516-s019190 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0516-s019190 | station | reverse | revenue | 1 |
| line-1 | line-1-0560-0589-s017356 | station | forward | revenue | 1 |
| line-1 | line-1-0560-0589-s017356 | station | reverse | revenue | 1 |
| line-1 | line-1-0630-0577-s015263 | station | forward | revenue | 1 |
| line-1 | line-1-0630-0577-s015263 | station | reverse | revenue | 1 |
| line-1 | line-1-0649-0674-s013165 | station | forward | revenue | 1 |
| line-1 | line-1-0649-0674-s013165 | station | reverse | revenue | 1 |
| line-1 | line-1-1075-0993-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0375-0639-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0505-0594-s003020 | station | forward | revenue | 1 |
| line-2 | line-2-0505-0594-s003020 | station | reverse | revenue | 1 |
| line-2 | line-2-0520-0535-s006032 | station | forward | revenue | 1 |
| line-2 | line-2-0520-0535-s006032 | station | reverse | revenue | 1 |
| line-2 | line-2-0560-0589-s004334 | station | forward | revenue | 1 |
| line-2 | line-2-0560-0589-s004334 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0383-s010639 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0383-s010639 | station | reverse | revenue | 1 |
| line-2 | line-2-0576-0495-s007636 | station | forward | revenue | 1 |
| line-2 | line-2-0576-0495-s007636 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0312-s014031 | station | reverse | revenue | 2 |
| line-3 | line-3-0636-0308-s007932 | station | reverse | revenue | 2 |
| line-3 | line-3-0648-0426-s005472 | station | forward | revenue | 1 |
| line-3 | line-3-0648-0426-s005472 | station | reverse | revenue | 1 |
| line-3 | line-3-0697-0528-s003026 | station | forward | revenue | 1 |
| line-3 | line-3-0697-0528-s003026 | station | reverse | revenue | 1 |
| line-3 | line-3-0804-0635-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0286-0224-s029156 | depot | — | revenue | 60 |
| line-1 | line-1-0286-0224-s029156 | depot | — | spare | 7 |
| line-1 | line-1-0286-0224-s029156 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0286-0224-s029156 | depot | — | revenue | 23 |
| line-2 | line-1-0286-0224-s029156 | depot | — | spare | 3 |
| line-2 | line-1-0286-0224-s029156 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0286-0224-s029156 | depot | — | revenue | 13 |
| line-3 | line-1-0286-0224-s029156 | depot | — | spare | 2 |
| line-3 | line-1-0286-0224-s029156 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (27 trains), line-3 (16 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **147 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **132 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **111 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1075-0993-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0649-0674-s013165 | forward | revenue | 7 | pending |
| line-1 | line-1-0649-0674-s013165 | reverse | revenue | 6 | pending |
| line-1 | line-1-0630-0577-s015263 | forward | revenue | 6 | pending |
| line-1 | line-1-0630-0577-s015263 | reverse | revenue | 6 | pending |
| line-1 | line-1-0560-0589-s017356 | forward | revenue | 6 | pending |
| line-1 | line-1-0560-0589-s017356 | reverse | revenue | 6 | pending |
| line-1 | line-1-0554-0516-s019190 | forward | revenue | 6 | pending |
| line-1 | line-1-0554-0516-s019190 | reverse | revenue | 6 | pending |
| line-1 | line-1-0435-0467-s022198 | forward | revenue | 6 | pending |
| line-1 | line-1-0435-0467-s022198 | reverse | revenue | 6 | pending |
| line-1 | line-1-0286-0224-s029156 | reverse | revenue | 6 | pending |
| line-1 | line-1-0649-0674-s013165 | reverse | spare | 1 | pending |
| line-1 | line-1-0630-0577-s015263 | forward | spare | 1 | pending |
| line-1 | line-1-0630-0577-s015263 | reverse | spare | 1 | pending |
| line-1 | line-1-0560-0589-s017356 | forward | spare | 1 | pending |
| line-1 | line-1-0560-0589-s017356 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0516-s019190 | forward | spare | 1 | pending |
| line-1 | line-1-0554-0516-s019190 | reverse | spare | 1 | pending |
| line-1 | line-1-0435-0467-s022198 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0375-0639-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0505-0594-s003020 | forward | revenue | 3 | pending |
| line-2 | line-2-0505-0594-s003020 | reverse | revenue | 3 | pending |
| line-2 | line-2-0560-0589-s004334 | forward | revenue | 3 | pending |
| line-2 | line-2-0560-0589-s004334 | reverse | revenue | 3 | pending |
| line-2 | line-2-0520-0535-s006032 | forward | revenue | 3 | pending |
| line-2 | line-2-0520-0535-s006032 | reverse | revenue | 3 | pending |
| line-2 | line-2-0576-0495-s007636 | forward | revenue | 3 | pending |
| line-2 | line-2-0576-0495-s007636 | reverse | revenue | 3 | pending |
| line-2 | line-2-0568-0383-s010639 | forward | revenue | 3 | pending |
| line-2 | line-2-0568-0383-s010639 | reverse | revenue | 3 | pending |
| line-2 | line-2-0644-0312-s014031 | reverse | revenue | 3 | pending |
| line-2 | line-2-0505-0594-s003020 | forward | spare | 1 | pending |
| line-2 | line-2-0505-0594-s003020 | reverse | spare | 1 | pending |
| line-2 | line-2-0560-0589-s004334 | forward | spare | 1 | pending |
| line-2 | line-2-0560-0589-s004334 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0804-0635-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0697-0528-s003026 | forward | revenue | 4 | pending |
| line-3 | line-3-0697-0528-s003026 | reverse | revenue | 4 | pending |
| line-3 | line-3-0648-0426-s005472 | forward | revenue | 3 | pending |
| line-3 | line-3-0648-0426-s005472 | reverse | revenue | 3 | pending |
| line-3 | line-3-0636-0308-s007932 | reverse | revenue | 3 | pending |
| line-3 | line-3-0648-0426-s005472 | forward | spare | 1 | pending |
| line-3 | line-3-0648-0426-s005472 | reverse | spare | 1 | pending |
| line-3 | line-3-0636-0308-s007932 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**103 trainsets exceed the reference platform envelope**, requiring **6,128.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0286-0224-s029156 | 6 | 2 | 4 | 238.0 |
| line-1-0435-0467-s022198 | 13 | 2 | 11 | 654.5 |
| line-1-0554-0516-s019190 | 14 | 4 | 10 | 595.0 |
| line-1-0560-0589-s017356 | 14 | 4 | 10 | 595.0 |
| line-1-0630-0577-s015263 | 14 | 2 | 12 | 714.0 |
| line-1-0649-0674-s013165 | 14 | 2 | 12 | 714.0 |
| line-1-1075-0993-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0375-0639-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0505-0594-s003020 | 8 | 2 | 6 | 357.0 |
| line-2-0520-0535-s006032 | 6 | 2 | 4 | 238.0 |
| line-2-0560-0589-s004334 | 8 | 4 | 4 | 238.0 |
| line-2-0568-0383-s010639 | 6 | 2 | 4 | 238.0 |
| line-2-0576-0495-s007636 | 6 | 4 | 2 | 119.0 |
| line-2-0644-0312-s014031 | 3 | 2 | 1 | 59.5 |
| line-3-0636-0308-s007932 | 4 | 2 | 2 | 119.0 |
| line-3-0648-0426-s005472 | 8 | 2 | 6 | 357.0 |
| line-3-0697-0528-s003026 | 8 | 2 | 6 | 357.0 |
| line-3-0804-0635-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Nasiriyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
