# Station and depot overnight allocation

Plan: **34 trainsets at stations + 69 at depots = 103 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0731-0566-s009382 | line-1 | storage-at-existing-powered-service-point | 13 | 773.5 | 0 |
| line-2-0526-0378-s018262 | line-2 | storage-at-existing-powered-service-point | 28 | 1,666.0 | 0 |
| line-3-0354-0950-s019775 | line-3 | declared-depot | 28 | 1,666.0 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0370-0539-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0484-0544-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0544-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0549-0552-s005079 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0552-s005079 | station | reverse | revenue | 1 |
| line-1 | line-1-0643-0586-s007241 | station | forward | revenue | 1 |
| line-1 | line-1-0643-0586-s007241 | station | reverse | revenue | 1 |
| line-1 | line-1-0731-0566-s009382 | station | reverse | revenue | 2 |
| line-2 | line-2-0526-0378-s018262 | station | reverse | revenue | 2 |
| line-2 | line-2-0549-0552-s013208 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0552-s013208 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0473-s015787 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0473-s015787 | station | reverse | revenue | 1 |
| line-2 | line-2-0585-0663-s010140 | station | forward | revenue | 1 |
| line-2 | line-2-0585-0663-s010140 | station | reverse | revenue | 1 |
| line-2 | line-2-0631-0792-s007005 | station | forward | revenue | 1 |
| line-2 | line-2-0631-0792-s007005 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-1100-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0950-s019775 | station | reverse | revenue | 2 |
| line-3 | line-3-0472-0788-s015557 | station | forward | revenue | 1 |
| line-3 | line-3-0472-0788-s015557 | station | reverse | revenue | 1 |
| line-3 | line-3-0533-0623-s011338 | station | forward | revenue | 1 |
| line-3 | line-3-0533-0623-s011338 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0552-s008988 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0552-s008988 | station | reverse | revenue | 1 |
| line-3 | line-3-0596-0457-s006305 | station | forward | revenue | 1 |
| line-3 | line-3-0596-0457-s006305 | station | reverse | revenue | 1 |
| line-3 | line-3-0740-0226-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0731-0566-s009382 | depot | — | revenue | 10 |
| line-1 | line-1-0731-0566-s009382 | depot | — | spare | 2 |
| line-1 | line-1-0731-0566-s009382 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0526-0378-s018262 | depot | — | revenue | 24 |
| line-2 | line-2-0526-0378-s018262 | depot | — | spare | 3 |
| line-2 | line-2-0526-0378-s018262 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0950-s019775 | depot | — | revenue | 24 |
| line-3 | line-3-0354-0950-s019775 | depot | — | spare | 3 |
| line-3 | line-3-0354-0950-s019775 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damanhur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **103 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **92 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **69 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0370-0539-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0484-0544-s003019 | forward | revenue | 3 | pending |
| line-1 | line-1-0484-0544-s003019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0552-s005079 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0552-s005079 | reverse | revenue | 2 | pending |
| line-1 | line-1-0643-0586-s007241 | forward | revenue | 2 | pending |
| line-1 | line-1-0643-0586-s007241 | reverse | revenue | 2 | pending |
| line-1 | line-1-0731-0566-s009382 | reverse | revenue | 2 | pending |
| line-1 | line-1-0549-0552-s005079 | reverse | spare | 1 | pending |
| line-1 | line-1-0643-0586-s007241 | forward | spare | 1 | pending |
| line-1 | line-1-0643-0586-s007241 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0631-0792-s007005 | forward | revenue | 4 | pending |
| line-2 | line-2-0631-0792-s007005 | reverse | revenue | 4 | pending |
| line-2 | line-2-0585-0663-s010140 | forward | revenue | 4 | pending |
| line-2 | line-2-0585-0663-s010140 | reverse | revenue | 4 | pending |
| line-2 | line-2-0549-0552-s013208 | forward | revenue | 4 | pending |
| line-2 | line-2-0549-0552-s013208 | reverse | revenue | 3 | pending |
| line-2 | line-2-0558-0473-s015787 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0473-s015787 | reverse | revenue | 3 | pending |
| line-2 | line-2-0526-0378-s018262 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0552-s013208 | reverse | spare | 1 | pending |
| line-2 | line-2-0558-0473-s015787 | forward | spare | 1 | pending |
| line-2 | line-2-0558-0473-s015787 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0378-s018262 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0740-0226-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0596-0457-s006305 | forward | revenue | 4 | pending |
| line-3 | line-3-0596-0457-s006305 | reverse | revenue | 4 | pending |
| line-3 | line-3-0549-0552-s008988 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0552-s008988 | reverse | revenue | 4 | pending |
| line-3 | line-3-0533-0623-s011338 | forward | revenue | 4 | pending |
| line-3 | line-3-0533-0623-s011338 | reverse | revenue | 3 | pending |
| line-3 | line-3-0472-0788-s015557 | forward | revenue | 3 | pending |
| line-3 | line-3-0472-0788-s015557 | reverse | revenue | 3 | pending |
| line-3 | line-3-0354-0950-s019775 | reverse | revenue | 3 | pending |
| line-3 | line-3-0533-0623-s011338 | reverse | spare | 1 | pending |
| line-3 | line-3-0472-0788-s015557 | forward | spare | 1 | pending |
| line-3 | line-3-0472-0788-s015557 | reverse | spare | 1 | pending |
| line-3 | line-3-0354-0950-s019775 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**63 trainsets exceed the reference platform envelope**, requiring **3,748.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0370-0539-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0484-0544-s003019 | 6 | 2 | 4 | 238.0 |
| line-1-0549-0552-s005079 | 6 | 4 | 2 | 119.0 |
| line-1-0643-0586-s007241 | 6 | 2 | 4 | 238.0 |
| line-1-0731-0566-s009382 | 2 | 2 | 0 | 0.0 |
| line-2-0526-0378-s018262 | 4 | 2 | 2 | 119.0 |
| line-2-0549-0552-s013208 | 8 | 4 | 4 | 238.0 |
| line-2-0558-0473-s015787 | 8 | 2 | 6 | 357.0 |
| line-2-0585-0663-s010140 | 8 | 2 | 6 | 357.0 |
| line-2-0631-0792-s007005 | 8 | 2 | 6 | 357.0 |
| line-2-0647-1100-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0354-0950-s019775 | 4 | 2 | 2 | 119.0 |
| line-3-0472-0788-s015557 | 8 | 2 | 6 | 357.0 |
| line-3-0533-0623-s011338 | 8 | 2 | 6 | 357.0 |
| line-3-0549-0552-s008988 | 8 | 4 | 4 | 238.0 |
| line-3-0596-0457-s006305 | 8 | 2 | 6 | 357.0 |
| line-3-0740-0226-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damanhur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
