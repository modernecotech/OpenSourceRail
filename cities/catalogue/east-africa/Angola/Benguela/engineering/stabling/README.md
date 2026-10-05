# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 114 at depots = 146 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0800-0524-s019689 | line-1 | declared-depot | 48 | 2,856.0 | 9 |
| line-2-0447-0786-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0555-0587-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0065-1050-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0332-0844-s007010 | station | forward | revenue | 1 |
| line-1 | line-1-0332-0844-s007010 | station | reverse | revenue | 1 |
| line-1 | line-1-0443-0768-s010012 | station | forward | revenue | 1 |
| line-1 | line-1-0443-0768-s010012 | station | reverse | revenue | 1 |
| line-1 | line-1-0581-0674-s013750 | station | forward | revenue | 1 |
| line-1 | line-1-0581-0674-s013750 | station | reverse | revenue | 1 |
| line-1 | line-1-0691-0598-s016755 | station | forward | revenue | 1 |
| line-1 | line-1-0691-0598-s016755 | station | reverse | revenue | 1 |
| line-1 | line-1-0800-0524-s019689 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0786-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0512-0663-s003022 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0663-s003022 | station | reverse | revenue | 1 |
| line-2 | line-2-0564-0563-s005535 | station | forward | revenue | 1 |
| line-2 | line-2-0564-0563-s005535 | station | reverse | revenue | 1 |
| line-2 | line-2-0620-0458-s008239 | station | forward | revenue | 1 |
| line-2 | line-2-0620-0458-s008239 | station | reverse | revenue | 1 |
| line-2 | line-2-0676-0352-s010929 | station | forward | revenue | 1 |
| line-2 | line-2-0676-0352-s010929 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0111-s016319 | station | reverse | revenue | 2 |
| line-3 | line-3-0555-0587-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0659-0672-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0659-0672-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0795-0782-s006919 | station | forward | revenue | 1 |
| line-3 | line-3-0795-0782-s006919 | station | reverse | revenue | 1 |
| line-3 | line-3-0901-0910-s010843 | station | reverse | revenue | 2 |
| line-1 | line-1-0800-0524-s019689 | depot | — | revenue | 42 |
| line-1 | line-1-0800-0524-s019689 | depot | — | spare | 5 |
| line-1 | line-1-0800-0524-s019689 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0447-0786-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0447-0786-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0447-0786-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0555-0587-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0555-0587-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0555-0587-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/benguela-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **146 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **131 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **114 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0065-1050-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0332-0844-s007010 | forward | revenue | 6 | pending |
| line-1 | line-1-0332-0844-s007010 | reverse | revenue | 6 | pending |
| line-1 | line-1-0443-0768-s010012 | forward | revenue | 6 | pending |
| line-1 | line-1-0443-0768-s010012 | reverse | revenue | 5 | pending |
| line-1 | line-1-0581-0674-s013750 | forward | revenue | 5 | pending |
| line-1 | line-1-0581-0674-s013750 | reverse | revenue | 5 | pending |
| line-1 | line-1-0691-0598-s016755 | forward | revenue | 5 | pending |
| line-1 | line-1-0691-0598-s016755 | reverse | revenue | 5 | pending |
| line-1 | line-1-0800-0524-s019689 | reverse | revenue | 5 | pending |
| line-1 | line-1-0443-0768-s010012 | reverse | spare | 1 | pending |
| line-1 | line-1-0581-0674-s013750 | forward | spare | 1 | pending |
| line-1 | line-1-0581-0674-s013750 | reverse | spare | 1 | pending |
| line-1 | line-1-0691-0598-s016755 | forward | spare | 1 | pending |
| line-1 | line-1-0691-0598-s016755 | reverse | spare | 1 | pending |
| line-1 | line-1-0800-0524-s019689 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0512-0663-s003022 | forward | revenue | 5 | pending |
| line-2 | line-2-0512-0663-s003022 | reverse | revenue | 5 | pending |
| line-2 | line-2-0564-0563-s005535 | forward | revenue | 5 | pending |
| line-2 | line-2-0564-0563-s005535 | reverse | revenue | 5 | pending |
| line-2 | line-2-0620-0458-s008239 | forward | revenue | 5 | pending |
| line-2 | line-2-0620-0458-s008239 | reverse | revenue | 4 | pending |
| line-2 | line-2-0676-0352-s010929 | forward | revenue | 4 | pending |
| line-2 | line-2-0676-0352-s010929 | reverse | revenue | 4 | pending |
| line-2 | line-2-0742-0111-s016319 | reverse | revenue | 4 | pending |
| line-2 | line-2-0620-0458-s008239 | reverse | spare | 1 | pending |
| line-2 | line-2-0676-0352-s010929 | forward | spare | 1 | pending |
| line-2 | line-2-0676-0352-s010929 | reverse | spare | 1 | pending |
| line-2 | line-2-0742-0111-s016319 | reverse | spare | 1 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0555-0587-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0659-0672-s003007 | forward | revenue | 5 | pending |
| line-3 | line-3-0659-0672-s003007 | reverse | revenue | 5 | pending |
| line-3 | line-3-0795-0782-s006919 | forward | revenue | 5 | pending |
| line-3 | line-3-0795-0782-s006919 | reverse | revenue | 5 | pending |
| line-3 | line-3-0901-0910-s010843 | reverse | revenue | 5 | pending |
| line-3 | line-3-0659-0672-s003007 | forward | spare | 1 | pending |
| line-3 | line-3-0659-0672-s003007 | reverse | spare | 1 | pending |
| line-3 | line-3-0795-0782-s006919 | forward | spare | 1 | pending |
| line-3 | line-3-0795-0782-s006919 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**110 trainsets exceed the reference platform envelope**, requiring **6,545.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0065-1050-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0332-0844-s007010 | 12 | 2 | 10 | 595.0 |
| line-1-0443-0768-s010012 | 12 | 4 | 8 | 476.0 |
| line-1-0581-0674-s013750 | 12 | 2 | 10 | 595.0 |
| line-1-0691-0598-s016755 | 12 | 2 | 10 | 595.0 |
| line-1-0800-0524-s019689 | 6 | 2 | 4 | 238.0 |
| line-2-0447-0786-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0512-0663-s003022 | 10 | 2 | 8 | 476.0 |
| line-2-0564-0563-s005535 | 10 | 4 | 6 | 357.0 |
| line-2-0620-0458-s008239 | 10 | 2 | 8 | 476.0 |
| line-2-0676-0352-s010929 | 10 | 2 | 8 | 476.0 |
| line-2-0742-0111-s016319 | 5 | 2 | 3 | 178.5 |
| line-3-0555-0587-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0659-0672-s003007 | 12 | 2 | 10 | 595.0 |
| line-3-0795-0782-s006919 | 12 | 2 | 10 | 595.0 |
| line-3-0901-0910-s010843 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Benguela/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
