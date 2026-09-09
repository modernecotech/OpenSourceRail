# Station and depot overnight allocation

Plan: **42 trainsets at stations + 85 at depots = 127 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0252-0503-s019498 | line-1 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |
| line-2-0348-0748-s017472 | line-2 | storage-at-existing-powered-service-point | 21 | 1,249.5 | 0 |
| line-3-0198-0119-s023342 | line-3 | declared-depot | 37 | 2,201.5 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0252-0503-s019498 | station | reverse | revenue | 2 |
| line-1 | line-1-0476-0543-s014093 | station | forward | revenue | 1 |
| line-1 | line-1-0476-0543-s014093 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0547-s012389 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0547-s012389 | station | reverse | revenue | 1 |
| line-1 | line-1-0589-0510-s011086 | station | forward | revenue | 1 |
| line-1 | line-1-0589-0510-s011086 | station | reverse | revenue | 1 |
| line-1 | line-1-0706-0505-s008062 | station | forward | revenue | 1 |
| line-1 | line-1-0706-0505-s008062 | station | reverse | revenue | 1 |
| line-1 | line-1-0759-0518-s006445 | station | forward | revenue | 1 |
| line-1 | line-1-0759-0518-s006445 | station | reverse | revenue | 1 |
| line-1 | line-1-1049-0499-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0348-0748-s017472 | station | reverse | revenue | 2 |
| line-2 | line-2-0424-0665-s014768 | station | forward | revenue | 1 |
| line-2 | line-2-0424-0665-s014768 | station | reverse | revenue | 1 |
| line-2 | line-2-0529-0603-s012037 | station | forward | revenue | 1 |
| line-2 | line-2-0529-0603-s012037 | station | reverse | revenue | 1 |
| line-2 | line-2-0539-0476-s008047 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0476-s008047 | station | reverse | revenue | 1 |
| line-2 | line-2-0554-0547-s010065 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0547-s010065 | station | reverse | revenue | 1 |
| line-2 | line-2-0613-0432-s006019 | station | forward | revenue | 1 |
| line-2 | line-2-0613-0432-s006019 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0203-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0698-0331-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0698-0331-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0198-0119-s023342 | station | reverse | revenue | 2 |
| line-3 | line-3-0422-0472-s012970 | station | forward | revenue | 1 |
| line-3 | line-3-0422-0472-s012970 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0547-s009254 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0547-s009254 | station | reverse | revenue | 1 |
| line-3 | line-3-0614-0601-s006953 | station | forward | revenue | 1 |
| line-3 | line-3-0614-0601-s006953 | station | reverse | revenue | 1 |
| line-3 | line-3-0617-0695-s003946 | station | forward | revenue | 1 |
| line-3 | line-3-0617-0695-s003946 | station | reverse | revenue | 1 |
| line-3 | line-3-0638-0851-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0252-0503-s019498 | depot | — | revenue | 23 |
| line-1 | line-1-0252-0503-s019498 | depot | — | spare | 3 |
| line-1 | line-1-0252-0503-s019498 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0348-0748-s017472 | depot | — | revenue | 17 |
| line-2 | line-2-0348-0748-s017472 | depot | — | spare | 3 |
| line-2 | line-2-0348-0748-s017472 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0198-0119-s023342 | depot | — | revenue | 32 |
| line-3 | line-3-0198-0119-s023342 | depot | — | spare | 4 |
| line-3 | line-3-0198-0119-s023342 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hebron-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **127 trainsets at 21 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **114 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **85 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1049-0499-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0759-0518-s006445 | forward | revenue | 3 | pending |
| line-1 | line-1-0759-0518-s006445 | reverse | revenue | 3 | pending |
| line-1 | line-1-0706-0505-s008062 | forward | revenue | 3 | pending |
| line-1 | line-1-0706-0505-s008062 | reverse | revenue | 3 | pending |
| line-1 | line-1-0589-0510-s011086 | forward | revenue | 3 | pending |
| line-1 | line-1-0589-0510-s011086 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0547-s012389 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0547-s012389 | reverse | revenue | 3 | pending |
| line-1 | line-1-0476-0543-s014093 | forward | revenue | 3 | pending |
| line-1 | line-1-0476-0543-s014093 | reverse | revenue | 3 | pending |
| line-1 | line-1-0252-0503-s019498 | reverse | revenue | 3 | pending |
| line-1 | line-1-0759-0518-s006445 | forward | spare | 1 | pending |
| line-1 | line-1-0759-0518-s006445 | reverse | spare | 1 | pending |
| line-1 | line-1-0706-0505-s008062 | forward | spare | 1 | pending |
| line-1 | line-1-0706-0505-s008062 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0203-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0698-0331-s003013 | forward | revenue | 3 | pending |
| line-2 | line-2-0698-0331-s003013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0613-0432-s006019 | forward | revenue | 3 | pending |
| line-2 | line-2-0613-0432-s006019 | reverse | revenue | 3 | pending |
| line-2 | line-2-0539-0476-s008047 | forward | revenue | 2 | pending |
| line-2 | line-2-0539-0476-s008047 | reverse | revenue | 2 | pending |
| line-2 | line-2-0554-0547-s010065 | forward | revenue | 2 | pending |
| line-2 | line-2-0554-0547-s010065 | reverse | revenue | 2 | pending |
| line-2 | line-2-0529-0603-s012037 | forward | revenue | 2 | pending |
| line-2 | line-2-0529-0603-s012037 | reverse | revenue | 2 | pending |
| line-2 | line-2-0424-0665-s014768 | forward | revenue | 2 | pending |
| line-2 | line-2-0424-0665-s014768 | reverse | revenue | 2 | pending |
| line-2 | line-2-0348-0748-s017472 | reverse | revenue | 2 | pending |
| line-2 | line-2-0539-0476-s008047 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0476-s008047 | reverse | spare | 1 | pending |
| line-2 | line-2-0554-0547-s010065 | forward | spare | 1 | pending |
| line-2 | line-2-0554-0547-s010065 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0638-0851-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0617-0695-s003946 | forward | revenue | 5 | pending |
| line-3 | line-3-0617-0695-s003946 | reverse | revenue | 5 | pending |
| line-3 | line-3-0614-0601-s006953 | forward | revenue | 5 | pending |
| line-3 | line-3-0614-0601-s006953 | reverse | revenue | 4 | pending |
| line-3 | line-3-0554-0547-s009254 | forward | revenue | 4 | pending |
| line-3 | line-3-0554-0547-s009254 | reverse | revenue | 4 | pending |
| line-3 | line-3-0422-0472-s012970 | forward | revenue | 4 | pending |
| line-3 | line-3-0422-0472-s012970 | reverse | revenue | 4 | pending |
| line-3 | line-3-0198-0119-s023342 | reverse | revenue | 4 | pending |
| line-3 | line-3-0614-0601-s006953 | reverse | spare | 1 | pending |
| line-3 | line-3-0554-0547-s009254 | forward | spare | 1 | pending |
| line-3 | line-3-0554-0547-s009254 | reverse | spare | 1 | pending |
| line-3 | line-3-0422-0472-s012970 | forward | spare | 1 | pending |
| line-3 | line-3-0422-0472-s012970 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**79 trainsets exceed the reference platform envelope**, requiring **4,700.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0252-0503-s019498 | 3 | 2 | 1 | 59.5 |
| line-1-0476-0543-s014093 | 6 | 2 | 4 | 238.0 |
| line-1-0554-0547-s012389 | 6 | 4 | 2 | 119.0 |
| line-1-0589-0510-s011086 | 6 | 2 | 4 | 238.0 |
| line-1-0706-0505-s008062 | 8 | 2 | 6 | 357.0 |
| line-1-0759-0518-s006445 | 8 | 2 | 6 | 357.0 |
| line-1-1049-0499-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0348-0748-s017472 | 2 | 2 | 0 | 0.0 |
| line-2-0424-0665-s014768 | 4 | 2 | 2 | 119.0 |
| line-2-0529-0603-s012037 | 4 | 2 | 2 | 119.0 |
| line-2-0539-0476-s008047 | 6 | 2 | 4 | 238.0 |
| line-2-0554-0547-s010065 | 6 | 4 | 2 | 119.0 |
| line-2-0613-0432-s006019 | 6 | 2 | 4 | 238.0 |
| line-2-0695-0203-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0698-0331-s003013 | 6 | 2 | 4 | 238.0 |
| line-3-0198-0119-s023342 | 4 | 2 | 2 | 119.0 |
| line-3-0422-0472-s012970 | 10 | 2 | 8 | 476.0 |
| line-3-0554-0547-s009254 | 10 | 4 | 6 | 357.0 |
| line-3-0614-0601-s006953 | 10 | 2 | 8 | 476.0 |
| line-3-0617-0695-s003946 | 10 | 2 | 8 | 476.0 |
| line-3-0638-0851-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Hebron/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
