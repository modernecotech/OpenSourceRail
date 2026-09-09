# Station and depot overnight allocation

Plan: **44 trainsets at stations + 134 at depots = 178 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0689-0101-s027176 | line-1 | declared-depot | 47 | 2,796.5 | 27 |
| line-2-0216-0821-s025533 | line-2 | storage-at-existing-powered-service-point | 45 | 2,677.5 | 0 |
| line-3-0048-0314-s022669 | line-3 | storage-at-existing-powered-service-point | 42 | 2,499.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0533-0449-s016131 | station | forward | revenue | 1 |
| line-1 | line-1-0533-0449-s016131 | station | reverse | revenue | 1 |
| line-1 | line-1-0549-0555-s013405 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0555-s013405 | station | reverse | revenue | 1 |
| line-1 | line-1-0549-0627-s011467 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0627-s011467 | station | reverse | revenue | 1 |
| line-1 | line-1-0591-0723-s008466 | station | forward | revenue | 1 |
| line-1 | line-1-0591-0723-s008466 | station | reverse | revenue | 1 |
| line-1 | line-1-0600-1040-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0612-0839-s005344 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0839-s005344 | station | reverse | revenue | 1 |
| line-1 | line-1-0629-0395-s019290 | station | forward | revenue | 1 |
| line-1 | line-1-0629-0395-s019290 | station | reverse | revenue | 1 |
| line-1 | line-1-0672-0258-s023238 | station | forward | revenue | 1 |
| line-1 | line-1-0672-0258-s023238 | station | reverse | revenue | 1 |
| line-1 | line-1-0689-0101-s027176 | station | reverse | revenue | 2 |
| line-2 | line-2-0216-0821-s025533 | station | reverse | revenue | 2 |
| line-2 | line-2-0361-0638-s020081 | station | forward | revenue | 1 |
| line-2 | line-2-0361-0638-s020081 | station | reverse | revenue | 1 |
| line-2 | line-2-0452-0599-s017078 | station | forward | revenue | 1 |
| line-2 | line-2-0452-0599-s017078 | station | reverse | revenue | 1 |
| line-2 | line-2-0549-0555-s014321 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0555-s014321 | station | reverse | revenue | 1 |
| line-2 | line-2-0667-0492-s011057 | station | forward | revenue | 1 |
| line-2 | line-2-0667-0492-s011057 | station | reverse | revenue | 1 |
| line-2 | line-2-0773-0315-s004806 | station | forward | revenue | 1 |
| line-2 | line-2-0773-0315-s004806 | station | reverse | revenue | 1 |
| line-2 | line-2-0897-0226-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0048-0314-s022669 | station | reverse | revenue | 2 |
| line-3 | line-3-0355-0504-s013631 | station | forward | revenue | 1 |
| line-3 | line-3-0355-0504-s013631 | station | reverse | revenue | 1 |
| line-3 | line-3-0464-0469-s010604 | station | forward | revenue | 1 |
| line-3 | line-3-0464-0469-s010604 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0555-s007781 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0555-s007781 | station | reverse | revenue | 1 |
| line-3 | line-3-0616-0646-s005220 | station | forward | revenue | 1 |
| line-3 | line-3-0616-0646-s005220 | station | reverse | revenue | 1 |
| line-3 | line-3-0669-0844-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0689-0101-s027176 | depot | — | revenue | 41 |
| line-1 | line-1-0689-0101-s027176 | depot | — | spare | 5 |
| line-1 | line-1-0689-0101-s027176 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0216-0821-s025533 | depot | — | revenue | 39 |
| line-2 | line-2-0216-0821-s025533 | depot | — | spare | 5 |
| line-2 | line-2-0216-0821-s025533 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0048-0314-s022669 | depot | — | revenue | 37 |
| line-3 | line-3-0048-0314-s022669 | depot | — | spare | 4 |
| line-3 | line-3-0048-0314-s022669 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kandy-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **178 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **161 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **134 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0600-1040-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0612-0839-s005344 | forward | revenue | 4 | pending |
| line-1 | line-1-0612-0839-s005344 | reverse | revenue | 4 | pending |
| line-1 | line-1-0591-0723-s008466 | forward | revenue | 4 | pending |
| line-1 | line-1-0591-0723-s008466 | reverse | revenue | 4 | pending |
| line-1 | line-1-0549-0627-s011467 | forward | revenue | 4 | pending |
| line-1 | line-1-0549-0627-s011467 | reverse | revenue | 4 | pending |
| line-1 | line-1-0549-0555-s013405 | forward | revenue | 4 | pending |
| line-1 | line-1-0549-0555-s013405 | reverse | revenue | 4 | pending |
| line-1 | line-1-0533-0449-s016131 | forward | revenue | 4 | pending |
| line-1 | line-1-0533-0449-s016131 | reverse | revenue | 4 | pending |
| line-1 | line-1-0629-0395-s019290 | forward | revenue | 3 | pending |
| line-1 | line-1-0629-0395-s019290 | reverse | revenue | 3 | pending |
| line-1 | line-1-0672-0258-s023238 | forward | revenue | 3 | pending |
| line-1 | line-1-0672-0258-s023238 | reverse | revenue | 3 | pending |
| line-1 | line-1-0689-0101-s027176 | reverse | revenue | 3 | pending |
| line-1 | line-1-0629-0395-s019290 | forward | spare | 1 | pending |
| line-1 | line-1-0629-0395-s019290 | reverse | spare | 1 | pending |
| line-1 | line-1-0672-0258-s023238 | forward | spare | 1 | pending |
| line-1 | line-1-0672-0258-s023238 | reverse | spare | 1 | pending |
| line-1 | line-1-0689-0101-s027176 | reverse | spare | 1 | pending |
| line-1 | line-1-0600-1040-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0773-0315-s004806 | forward | revenue | 5 | pending |
| line-2 | line-2-0773-0315-s004806 | reverse | revenue | 5 | pending |
| line-2 | line-2-0667-0492-s011057 | forward | revenue | 5 | pending |
| line-2 | line-2-0667-0492-s011057 | reverse | revenue | 5 | pending |
| line-2 | line-2-0549-0555-s014321 | forward | revenue | 4 | pending |
| line-2 | line-2-0549-0555-s014321 | reverse | revenue | 4 | pending |
| line-2 | line-2-0452-0599-s017078 | forward | revenue | 4 | pending |
| line-2 | line-2-0452-0599-s017078 | reverse | revenue | 4 | pending |
| line-2 | line-2-0361-0638-s020081 | forward | revenue | 4 | pending |
| line-2 | line-2-0361-0638-s020081 | reverse | revenue | 4 | pending |
| line-2 | line-2-0216-0821-s025533 | reverse | revenue | 4 | pending |
| line-2 | line-2-0549-0555-s014321 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0555-s014321 | reverse | spare | 1 | pending |
| line-2 | line-2-0452-0599-s017078 | forward | spare | 1 | pending |
| line-2 | line-2-0452-0599-s017078 | reverse | spare | 1 | pending |
| line-2 | line-2-0361-0638-s020081 | forward | spare | 1 | pending |
| line-2 | line-2-0361-0638-s020081 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0669-0844-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0616-0646-s005220 | forward | revenue | 5 | pending |
| line-3 | line-3-0616-0646-s005220 | reverse | revenue | 5 | pending |
| line-3 | line-3-0549-0555-s007781 | forward | revenue | 5 | pending |
| line-3 | line-3-0549-0555-s007781 | reverse | revenue | 5 | pending |
| line-3 | line-3-0464-0469-s010604 | forward | revenue | 5 | pending |
| line-3 | line-3-0464-0469-s010604 | reverse | revenue | 5 | pending |
| line-3 | line-3-0355-0504-s013631 | forward | revenue | 5 | pending |
| line-3 | line-3-0355-0504-s013631 | reverse | revenue | 5 | pending |
| line-3 | line-3-0048-0314-s022669 | reverse | revenue | 4 | pending |
| line-3 | line-3-0048-0314-s022669 | reverse | spare | 1 | pending |
| line-3 | line-3-0669-0844-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0616-0646-s005220 | forward | spare | 1 | pending |
| line-3 | line-3-0616-0646-s005220 | reverse | spare | 1 | pending |
| line-3 | line-3-0549-0555-s007781 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**128 trainsets exceed the reference platform envelope**, requiring **7,616.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0533-0449-s016131 | 8 | 2 | 6 | 357.0 |
| line-1-0549-0555-s013405 | 8 | 4 | 4 | 238.0 |
| line-1-0549-0627-s011467 | 8 | 2 | 6 | 357.0 |
| line-1-0591-0723-s008466 | 8 | 2 | 6 | 357.0 |
| line-1-0600-1040-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0612-0839-s005344 | 8 | 2 | 6 | 357.0 |
| line-1-0629-0395-s019290 | 8 | 2 | 6 | 357.0 |
| line-1-0672-0258-s023238 | 8 | 2 | 6 | 357.0 |
| line-1-0689-0101-s027176 | 4 | 2 | 2 | 119.0 |
| line-2-0216-0821-s025533 | 4 | 2 | 2 | 119.0 |
| line-2-0361-0638-s020081 | 10 | 2 | 8 | 476.0 |
| line-2-0452-0599-s017078 | 10 | 2 | 8 | 476.0 |
| line-2-0549-0555-s014321 | 10 | 4 | 6 | 357.0 |
| line-2-0667-0492-s011057 | 10 | 2 | 8 | 476.0 |
| line-2-0773-0315-s004806 | 10 | 2 | 8 | 476.0 |
| line-2-0897-0226-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0048-0314-s022669 | 5 | 2 | 3 | 178.5 |
| line-3-0355-0504-s013631 | 10 | 2 | 8 | 476.0 |
| line-3-0464-0469-s010604 | 10 | 2 | 8 | 476.0 |
| line-3-0549-0555-s007781 | 11 | 4 | 7 | 416.5 |
| line-3-0616-0646-s005220 | 12 | 2 | 10 | 595.0 |
| line-3-0669-0844-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Kandy/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
