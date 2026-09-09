# Station and depot overnight allocation

Plan: **28 trainsets at stations + 35 at depots = 63 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0531-0372-s009357 | line-1 | storage-at-existing-powered-service-point | 10 | 490.0 | 0 |
| line-2-0474-0480-s008544 | line-2 | storage-at-existing-powered-service-point | 10 | 490.0 | 0 |
| line-3-0744-0445-s011517 | line-3 | declared-depot | 15 | 735.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0319-0148-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0325-0276-s003004 | station | forward | revenue | 1 |
| line-1 | line-1-0325-0276-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0381-0373-s005441 | station | forward | revenue | 1 |
| line-1 | line-1-0381-0373-s005441 | station | reverse | revenue | 1 |
| line-1 | line-1-0459-0399-s007406 | station | forward | revenue | 1 |
| line-1 | line-1-0459-0399-s007406 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0372-s009357 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0373-s005090 | station | forward | revenue | 1 |
| line-2 | line-2-0381-0373-s005090 | station | reverse | revenue | 1 |
| line-2 | line-2-0474-0480-s008544 | station | reverse | revenue | 2 |
| line-2 | line-2-0481-0364-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0481-0364-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0593-0351-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0340-0286-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0381-0373-s002233 | station | forward | revenue | 1 |
| line-3 | line-3-0381-0373-s002233 | station | reverse | revenue | 1 |
| line-3 | line-3-0455-0427-s004195 | station | forward | revenue | 1 |
| line-3 | line-3-0455-0427-s004195 | station | reverse | revenue | 1 |
| line-3 | line-3-0542-0405-s006167 | station | forward | revenue | 1 |
| line-3 | line-3-0542-0405-s006167 | station | reverse | revenue | 1 |
| line-3 | line-3-0744-0445-s011517 | station | reverse | revenue | 2 |
| line-1 | line-1-0531-0372-s009357 | depot | — | revenue | 8 |
| line-1 | line-1-0531-0372-s009357 | depot | — | spare | 1 |
| line-1 | line-1-0531-0372-s009357 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0474-0480-s008544 | depot | — | revenue | 8 |
| line-2 | line-2-0474-0480-s008544 | depot | — | spare | 1 |
| line-2 | line-2-0474-0480-s008544 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0744-0445-s011517 | depot | — | revenue | 12 |
| line-3 | line-3-0744-0445-s011517 | depot | — | spare | 2 |
| line-3 | line-3-0744-0445-s011517 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/soyo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **63 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **56 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **35 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0319-0148-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | forward | revenue | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | reverse | revenue | 2 | pending |
| line-1 | line-1-0381-0373-s005441 | forward | revenue | 2 | pending |
| line-1 | line-1-0381-0373-s005441 | reverse | revenue | 2 | pending |
| line-1 | line-1-0459-0399-s007406 | forward | revenue | 2 | pending |
| line-1 | line-1-0459-0399-s007406 | reverse | revenue | 2 | pending |
| line-1 | line-1-0531-0372-s009357 | reverse | revenue | 2 | pending |
| line-1 | line-1-0325-0276-s003004 | reverse | spare | 1 | pending |
| line-1 | line-1-0381-0373-s005441 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0593-0351-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0481-0364-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0481-0364-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0381-0373-s005090 | forward | revenue | 3 | pending |
| line-2 | line-2-0381-0373-s005090 | reverse | revenue | 2 | pending |
| line-2 | line-2-0474-0480-s008544 | reverse | revenue | 2 | pending |
| line-2 | line-2-0381-0373-s005090 | reverse | spare | 1 | pending |
| line-2 | line-2-0474-0480-s008544 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0381-0373-s002233 | forward | revenue | 3 | pending |
| line-3 | line-3-0381-0373-s002233 | reverse | revenue | 3 | pending |
| line-3 | line-3-0455-0427-s004195 | forward | revenue | 3 | pending |
| line-3 | line-3-0455-0427-s004195 | reverse | revenue | 3 | pending |
| line-3 | line-3-0542-0405-s006167 | forward | revenue | 3 | pending |
| line-3 | line-3-0542-0405-s006167 | reverse | revenue | 2 | pending |
| line-3 | line-3-0744-0445-s011517 | reverse | revenue | 2 | pending |
| line-3 | line-3-0542-0405-s006167 | reverse | spare | 1 | pending |
| line-3 | line-3-0744-0445-s011517 | reverse | spare | 1 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**23 trainsets exceed the reference platform envelope**, requiring **1,127.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0319-0148-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0325-0276-s003004 | 6 | 4 | 2 | 98.0 |
| line-1-0381-0373-s005441 | 5 | 4 | 1 | 49.0 |
| line-1-0459-0399-s007406 | 4 | 4 | 0 | 0.0 |
| line-1-0531-0372-s009357 | 2 | 2 | 0 | 0.0 |
| line-2-0381-0373-s005090 | 6 | 4 | 2 | 98.0 |
| line-2-0474-0480-s008544 | 3 | 2 | 1 | 49.0 |
| line-2-0481-0364-s003016 | 6 | 2 | 4 | 196.0 |
| line-2-0593-0351-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0340-0286-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0381-0373-s002233 | 6 | 4 | 2 | 98.0 |
| line-3-0455-0427-s004195 | 6 | 4 | 2 | 98.0 |
| line-3-0542-0405-s006167 | 6 | 2 | 4 | 196.0 |
| line-3-0744-0445-s011517 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Soyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
