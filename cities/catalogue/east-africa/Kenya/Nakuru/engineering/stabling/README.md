# Station and depot overnight allocation

Plan: **36 trainsets at stations + 80 at depots = 116 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-1065-0208-s021348 | 80 | 4,760.0 | 18 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0383-0392-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0458-0474-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0458-0474-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0507-0644-s009043 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0644-s009043 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0881-s014774 | station | reverse | revenue | 2 |
| line-1 | line-1-0542-0550-s006711 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0550-s006711 | station | reverse | revenue | 1 |
| line-2 | line-2-0381-0736-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0437-0636-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0437-0636-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0480-0572-s005074 | station | forward | revenue | 1 |
| line-2 | line-2-0480-0572-s005074 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0550-s007127 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0550-s007127 | station | reverse | revenue | 1 |
| line-2 | line-2-0615-0523-s009026 | station | forward | revenue | 1 |
| line-2 | line-2-0615-0523-s009026 | station | reverse | revenue | 1 |
| line-2 | line-2-0749-0422-s012543 | station | forward | revenue | 1 |
| line-2 | line-2-0749-0422-s012543 | station | reverse | revenue | 1 |
| line-2 | line-2-1065-0208-s021348 | station | reverse | revenue | 2 |
| line-3 | line-3-0542-0550-s009288 | station | forward | revenue | 1 |
| line-3 | line-3-0542-0550-s009288 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0644-s006880 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0644-s006880 | station | reverse | revenue | 1 |
| line-3 | line-3-0564-0202-s018141 | station | reverse | revenue | 2 |
| line-3 | line-3-0593-0338-s015181 | station | forward | revenue | 1 |
| line-3 | line-3-0593-0338-s015181 | station | reverse | revenue | 1 |
| line-3 | line-3-0602-0468-s012246 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0468-s012246 | station | reverse | revenue | 1 |
| line-3 | line-3-0651-0932-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-1065-0208-s021348 | depot | — | revenue | 17 |
| line-1 | line-2-1065-0208-s021348 | depot | — | spare | 2 |
| line-1 | line-2-1065-0208-s021348 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1065-0208-s021348 | depot | — | revenue | 28 |
| line-2 | line-2-1065-0208-s021348 | depot | — | spare | 4 |
| line-2 | line-2-1065-0208-s021348 | depot | — | cold_reserve | 1 |
| line-3 | line-2-1065-0208-s021348 | depot | — | revenue | 23 |
| line-3 | line-2-1065-0208-s021348 | depot | — | spare | 3 |
| line-3 | line-2-1065-0208-s021348 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (20 trains), line-3 (27 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **116 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **104 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **80 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0383-0392-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0458-0474-s003014 | forward | revenue | 4 | pending |
| line-1 | line-1-0458-0474-s003014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0542-0550-s006711 | forward | revenue | 3 | pending |
| line-1 | line-1-0542-0550-s006711 | reverse | revenue | 3 | pending |
| line-1 | line-1-0507-0644-s009043 | forward | revenue | 3 | pending |
| line-1 | line-1-0507-0644-s009043 | reverse | revenue | 3 | pending |
| line-1 | line-1-0531-0881-s014774 | reverse | revenue | 3 | pending |
| line-1 | line-1-0542-0550-s006711 | forward | spare | 1 | pending |
| line-1 | line-1-0542-0550-s006711 | reverse | spare | 1 | pending |
| line-1 | line-1-0507-0644-s009043 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0736-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0437-0636-s003010 | forward | revenue | 4 | pending |
| line-2 | line-2-0437-0636-s003010 | reverse | revenue | 4 | pending |
| line-2 | line-2-0480-0572-s005074 | forward | revenue | 4 | pending |
| line-2 | line-2-0480-0572-s005074 | reverse | revenue | 4 | pending |
| line-2 | line-2-0542-0550-s007127 | forward | revenue | 4 | pending |
| line-2 | line-2-0542-0550-s007127 | reverse | revenue | 3 | pending |
| line-2 | line-2-0615-0523-s009026 | forward | revenue | 3 | pending |
| line-2 | line-2-0615-0523-s009026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0749-0422-s012543 | forward | revenue | 3 | pending |
| line-2 | line-2-0749-0422-s012543 | reverse | revenue | 3 | pending |
| line-2 | line-2-1065-0208-s021348 | reverse | revenue | 3 | pending |
| line-2 | line-2-0542-0550-s007127 | reverse | spare | 1 | pending |
| line-2 | line-2-0615-0523-s009026 | forward | spare | 1 | pending |
| line-2 | line-2-0615-0523-s009026 | reverse | spare | 1 | pending |
| line-2 | line-2-0749-0422-s012543 | forward | spare | 1 | pending |
| line-2 | line-2-0749-0422-s012543 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0651-0932-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0561-0644-s006880 | forward | revenue | 4 | pending |
| line-3 | line-3-0561-0644-s006880 | reverse | revenue | 4 | pending |
| line-3 | line-3-0542-0550-s009288 | forward | revenue | 4 | pending |
| line-3 | line-3-0542-0550-s009288 | reverse | revenue | 4 | pending |
| line-3 | line-3-0602-0468-s012246 | forward | revenue | 3 | pending |
| line-3 | line-3-0602-0468-s012246 | reverse | revenue | 3 | pending |
| line-3 | line-3-0593-0338-s015181 | forward | revenue | 3 | pending |
| line-3 | line-3-0593-0338-s015181 | reverse | revenue | 3 | pending |
| line-3 | line-3-0564-0202-s018141 | reverse | revenue | 3 | pending |
| line-3 | line-3-0602-0468-s012246 | forward | spare | 1 | pending |
| line-3 | line-3-0602-0468-s012246 | reverse | spare | 1 | pending |
| line-3 | line-3-0593-0338-s015181 | forward | spare | 1 | pending |
| line-3 | line-3-0593-0338-s015181 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **4,403.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0383-0392-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0458-0474-s003014 | 8 | 2 | 6 | 357.0 |
| line-1-0507-0644-s009043 | 7 | 2 | 5 | 297.5 |
| line-1-0531-0881-s014774 | 3 | 2 | 1 | 59.5 |
| line-1-0542-0550-s006711 | 8 | 4 | 4 | 238.0 |
| line-2-0381-0736-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0437-0636-s003010 | 8 | 2 | 6 | 357.0 |
| line-2-0480-0572-s005074 | 8 | 2 | 6 | 357.0 |
| line-2-0542-0550-s007127 | 8 | 4 | 4 | 238.0 |
| line-2-0615-0523-s009026 | 8 | 2 | 6 | 357.0 |
| line-2-0749-0422-s012543 | 8 | 2 | 6 | 357.0 |
| line-2-1065-0208-s021348 | 3 | 2 | 1 | 59.5 |
| line-3-0542-0550-s009288 | 8 | 4 | 4 | 238.0 |
| line-3-0561-0644-s006880 | 8 | 2 | 6 | 357.0 |
| line-3-0564-0202-s018141 | 3 | 2 | 1 | 59.5 |
| line-3-0593-0338-s015181 | 8 | 2 | 6 | 357.0 |
| line-3-0602-0468-s012246 | 8 | 2 | 6 | 357.0 |
| line-3-0651-0932-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nakuru/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
