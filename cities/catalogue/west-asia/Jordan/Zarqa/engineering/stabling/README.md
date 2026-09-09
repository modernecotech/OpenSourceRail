# Station and depot overnight allocation

Plan: **40 trainsets at stations + 187 at depots = 227 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-1067-0037-s029681 | 187 | 11,126.5 | 35 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-1028-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0461-0731-s007010 | station | forward | revenue | 1 |
| line-1 | line-1-0461-0731-s007010 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0616-s010034 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0616-s010034 | station | reverse | revenue | 1 |
| line-1 | line-1-0576-0536-s012500 | station | forward | revenue | 1 |
| line-1 | line-1-0576-0536-s012500 | station | reverse | revenue | 1 |
| line-1 | line-1-0703-0488-s016055 | station | forward | revenue | 1 |
| line-1 | line-1-0703-0488-s016055 | station | reverse | revenue | 1 |
| line-1 | line-1-0810-0381-s019081 | station | forward | revenue | 1 |
| line-1 | line-1-0810-0381-s019081 | station | reverse | revenue | 1 |
| line-1 | line-1-1067-0037-s029681 | station | reverse | revenue | 2 |
| line-2 | line-2-0192-0706-s027863 | station | reverse | revenue | 2 |
| line-2 | line-2-0410-0650-s022055 | station | forward | revenue | 1 |
| line-2 | line-2-0410-0650-s022055 | station | reverse | revenue | 1 |
| line-2 | line-2-0477-0542-s019054 | station | forward | revenue | 1 |
| line-2 | line-2-0477-0542-s019054 | station | reverse | revenue | 1 |
| line-2 | line-2-0576-0536-s016381 | station | forward | revenue | 1 |
| line-2 | line-2-0576-0536-s016381 | station | reverse | revenue | 1 |
| line-2 | line-2-0670-0442-s013039 | station | forward | revenue | 1 |
| line-2 | line-2-0670-0442-s013039 | station | reverse | revenue | 1 |
| line-2 | line-2-0777-0335-s010012 | station | forward | revenue | 1 |
| line-2 | line-2-0777-0335-s010012 | station | reverse | revenue | 1 |
| line-2 | line-2-0857-0222-s007007 | station | forward | revenue | 1 |
| line-2 | line-2-0857-0222-s007007 | station | reverse | revenue | 1 |
| line-2 | line-2-1078-0047-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0360-0400-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0467-0450-s003026 | station | forward | revenue | 1 |
| line-3 | line-3-0467-0450-s003026 | station | reverse | revenue | 1 |
| line-3 | line-3-0576-0536-s006216 | station | forward | revenue | 1 |
| line-3 | line-3-0576-0536-s006216 | station | reverse | revenue | 1 |
| line-3 | line-3-0618-0641-s009034 | station | forward | revenue | 1 |
| line-3 | line-3-0618-0641-s009034 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0864-s014992 | station | reverse | revenue | 2 |
| line-1 | line-1-1067-0037-s029681 | depot | — | revenue | 70 |
| line-1 | line-1-1067-0037-s029681 | depot | — | spare | 8 |
| line-1 | line-1-1067-0037-s029681 | depot | — | cold_reserve | 1 |
| line-2 | line-1-1067-0037-s029681 | depot | — | revenue | 62 |
| line-2 | line-1-1067-0037-s029681 | depot | — | spare | 7 |
| line-2 | line-1-1067-0037-s029681 | depot | — | cold_reserve | 1 |
| line-3 | line-1-1067-0037-s029681 | depot | — | revenue | 33 |
| line-3 | line-1-1067-0037-s029681 | depot | — | spare | 4 |
| line-3 | line-1-1067-0037-s029681 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (70 trains), line-3 (38 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **227 trainsets at 20 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **205 revenue, 19 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **187 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1028-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0461-0731-s007010 | forward | revenue | 7 | pending |
| line-1 | line-1-0461-0731-s007010 | reverse | revenue | 7 | pending |
| line-1 | line-1-0535-0616-s010034 | forward | revenue | 7 | pending |
| line-1 | line-1-0535-0616-s010034 | reverse | revenue | 7 | pending |
| line-1 | line-1-0576-0536-s012500 | forward | revenue | 7 | pending |
| line-1 | line-1-0576-0536-s012500 | reverse | revenue | 7 | pending |
| line-1 | line-1-0703-0488-s016055 | forward | revenue | 7 | pending |
| line-1 | line-1-0703-0488-s016055 | reverse | revenue | 7 | pending |
| line-1 | line-1-0810-0381-s019081 | forward | revenue | 7 | pending |
| line-1 | line-1-0810-0381-s019081 | reverse | revenue | 7 | pending |
| line-1 | line-1-1067-0037-s029681 | reverse | revenue | 7 | pending |
| line-1 | line-1-0400-1028-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0461-0731-s007010 | forward | spare | 1 | pending |
| line-1 | line-1-0461-0731-s007010 | reverse | spare | 1 | pending |
| line-1 | line-1-0535-0616-s010034 | forward | spare | 1 | pending |
| line-1 | line-1-0535-0616-s010034 | reverse | spare | 1 | pending |
| line-1 | line-1-0576-0536-s012500 | forward | spare | 1 | pending |
| line-1 | line-1-0576-0536-s012500 | reverse | spare | 1 | pending |
| line-1 | line-1-0703-0488-s016055 | forward | spare | 1 | pending |
| line-1 | line-1-0703-0488-s016055 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1078-0047-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0857-0222-s007007 | forward | revenue | 6 | pending |
| line-2 | line-2-0857-0222-s007007 | reverse | revenue | 6 | pending |
| line-2 | line-2-0777-0335-s010012 | forward | revenue | 6 | pending |
| line-2 | line-2-0777-0335-s010012 | reverse | revenue | 6 | pending |
| line-2 | line-2-0670-0442-s013039 | forward | revenue | 6 | pending |
| line-2 | line-2-0670-0442-s013039 | reverse | revenue | 6 | pending |
| line-2 | line-2-0576-0536-s016381 | forward | revenue | 6 | pending |
| line-2 | line-2-0576-0536-s016381 | reverse | revenue | 5 | pending |
| line-2 | line-2-0477-0542-s019054 | forward | revenue | 5 | pending |
| line-2 | line-2-0477-0542-s019054 | reverse | revenue | 5 | pending |
| line-2 | line-2-0410-0650-s022055 | forward | revenue | 5 | pending |
| line-2 | line-2-0410-0650-s022055 | reverse | revenue | 5 | pending |
| line-2 | line-2-0192-0706-s027863 | reverse | revenue | 5 | pending |
| line-2 | line-2-0576-0536-s016381 | reverse | spare | 1 | pending |
| line-2 | line-2-0477-0542-s019054 | forward | spare | 1 | pending |
| line-2 | line-2-0477-0542-s019054 | reverse | spare | 1 | pending |
| line-2 | line-2-0410-0650-s022055 | forward | spare | 1 | pending |
| line-2 | line-2-0410-0650-s022055 | reverse | spare | 1 | pending |
| line-2 | line-2-0192-0706-s027863 | reverse | spare | 1 | pending |
| line-2 | line-2-1078-0047-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0857-0222-s007007 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0360-0400-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0467-0450-s003026 | forward | revenue | 6 | pending |
| line-3 | line-3-0467-0450-s003026 | reverse | revenue | 6 | pending |
| line-3 | line-3-0576-0536-s006216 | forward | revenue | 5 | pending |
| line-3 | line-3-0576-0536-s006216 | reverse | revenue | 5 | pending |
| line-3 | line-3-0618-0641-s009034 | forward | revenue | 5 | pending |
| line-3 | line-3-0618-0641-s009034 | reverse | revenue | 5 | pending |
| line-3 | line-3-0626-0864-s014992 | reverse | revenue | 5 | pending |
| line-3 | line-3-0576-0536-s006216 | forward | spare | 1 | pending |
| line-3 | line-3-0576-0536-s006216 | reverse | spare | 1 | pending |
| line-3 | line-3-0618-0641-s009034 | forward | spare | 1 | pending |
| line-3 | line-3-0618-0641-s009034 | reverse | spare | 1 | pending |
| line-3 | line-3-0626-0864-s014992 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**181 trainsets exceed the reference platform envelope**, requiring **10,769.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-1028-s000000 | 8 | 2 | 6 | 357.0 |
| line-1-0461-0731-s007010 | 16 | 2 | 14 | 833.0 |
| line-1-0535-0616-s010034 | 16 | 2 | 14 | 833.0 |
| line-1-0576-0536-s012500 | 16 | 4 | 12 | 714.0 |
| line-1-0703-0488-s016055 | 16 | 2 | 14 | 833.0 |
| line-1-0810-0381-s019081 | 14 | 2 | 12 | 714.0 |
| line-1-1067-0037-s029681 | 7 | 2 | 5 | 297.5 |
| line-2-0192-0706-s027863 | 6 | 2 | 4 | 238.0 |
| line-2-0410-0650-s022055 | 12 | 2 | 10 | 595.0 |
| line-2-0477-0542-s019054 | 12 | 2 | 10 | 595.0 |
| line-2-0576-0536-s016381 | 12 | 4 | 8 | 476.0 |
| line-2-0670-0442-s013039 | 12 | 2 | 10 | 595.0 |
| line-2-0777-0335-s010012 | 12 | 2 | 10 | 595.0 |
| line-2-0857-0222-s007007 | 13 | 2 | 11 | 654.5 |
| line-2-1078-0047-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0360-0400-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0467-0450-s003026 | 12 | 2 | 10 | 595.0 |
| line-3-0576-0536-s006216 | 12 | 4 | 8 | 476.0 |
| line-3-0618-0641-s009034 | 12 | 2 | 10 | 595.0 |
| line-3-0626-0864-s014992 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Zarqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
