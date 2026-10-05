# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 136 at depots = 174 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0155-0354-s021506 | line-1 | declared-depot | 53 | 3,153.5 | 10 |
| line-2-0832-0082-s000000 | line-2 | declared-depot | 48 | 2,856.0 | 9 |
| line-3-0156-0494-s000000 | line-3 | declared-depot | 35 | 2,082.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0354-s021506 | station | reverse | revenue | 2 |
| line-1 | line-1-0272-0377-s018533 | station | forward | revenue | 1 |
| line-1 | line-1-0272-0377-s018533 | station | reverse | revenue | 1 |
| line-1 | line-1-0400-0424-s015537 | station | forward | revenue | 1 |
| line-1 | line-1-0400-0424-s015537 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0472-s012519 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0472-s012519 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0493-s011205 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0493-s011205 | station | reverse | revenue | 1 |
| line-1 | line-1-0679-0527-s009103 | station | forward | revenue | 1 |
| line-1 | line-1-0679-0527-s009103 | station | reverse | revenue | 1 |
| line-1 | line-1-0769-0560-s007007 | station | forward | revenue | 1 |
| line-1 | line-1-0769-0560-s007007 | station | reverse | revenue | 1 |
| line-1 | line-1-1040-0603-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0391-0788-s019601 | station | reverse | revenue | 2 |
| line-2 | line-2-0468-0674-s016478 | station | forward | revenue | 1 |
| line-2 | line-2-0468-0674-s016478 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0540-s012911 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0540-s012911 | station | reverse | revenue | 1 |
| line-2 | line-2-0588-0493-s011624 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0493-s011624 | station | reverse | revenue | 1 |
| line-2 | line-2-0627-0434-s010015 | station | forward | revenue | 1 |
| line-2 | line-2-0627-0434-s010015 | station | reverse | revenue | 1 |
| line-2 | line-2-0702-0322-s007014 | station | forward | revenue | 1 |
| line-2 | line-2-0702-0322-s007014 | station | reverse | revenue | 1 |
| line-2 | line-2-0832-0082-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0156-0494-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0336-0605-s005393 | station | forward | revenue | 1 |
| line-3 | line-3-0336-0605-s005393 | station | reverse | revenue | 1 |
| line-3 | line-3-0468-0674-s008673 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0674-s008673 | station | reverse | revenue | 1 |
| line-3 | line-3-0701-0794-s014505 | station | reverse | revenue | 2 |
| line-1 | line-1-0155-0354-s021506 | depot | — | revenue | 46 |
| line-1 | line-1-0155-0354-s021506 | depot | — | spare | 6 |
| line-1 | line-1-0155-0354-s021506 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0832-0082-s000000 | depot | — | revenue | 42 |
| line-2 | line-2-0832-0082-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0832-0082-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0156-0494-s000000 | depot | — | revenue | 31 |
| line-3 | line-3-0156-0494-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0156-0494-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hail-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **174 trainsets at 19 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **157 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **136 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1040-0603-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0769-0560-s007007 | forward | revenue | 5 | pending |
| line-1 | line-1-0769-0560-s007007 | reverse | revenue | 5 | pending |
| line-1 | line-1-0679-0527-s009103 | forward | revenue | 5 | pending |
| line-1 | line-1-0679-0527-s009103 | reverse | revenue | 5 | pending |
| line-1 | line-1-0588-0493-s011205 | forward | revenue | 5 | pending |
| line-1 | line-1-0588-0493-s011205 | reverse | revenue | 4 | pending |
| line-1 | line-1-0531-0472-s012519 | forward | revenue | 4 | pending |
| line-1 | line-1-0531-0472-s012519 | reverse | revenue | 4 | pending |
| line-1 | line-1-0400-0424-s015537 | forward | revenue | 4 | pending |
| line-1 | line-1-0400-0424-s015537 | reverse | revenue | 4 | pending |
| line-1 | line-1-0272-0377-s018533 | forward | revenue | 4 | pending |
| line-1 | line-1-0272-0377-s018533 | reverse | revenue | 4 | pending |
| line-1 | line-1-0155-0354-s021506 | reverse | revenue | 4 | pending |
| line-1 | line-1-0588-0493-s011205 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0472-s012519 | forward | spare | 1 | pending |
| line-1 | line-1-0531-0472-s012519 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-0424-s015537 | forward | spare | 1 | pending |
| line-1 | line-1-0400-0424-s015537 | reverse | spare | 1 | pending |
| line-1 | line-1-0272-0377-s018533 | forward | spare | 1 | pending |
| line-1 | line-1-0272-0377-s018533 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0832-0082-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0702-0322-s007014 | forward | revenue | 5 | pending |
| line-2 | line-2-0702-0322-s007014 | reverse | revenue | 5 | pending |
| line-2 | line-2-0627-0434-s010015 | forward | revenue | 5 | pending |
| line-2 | line-2-0627-0434-s010015 | reverse | revenue | 5 | pending |
| line-2 | line-2-0588-0493-s011624 | forward | revenue | 5 | pending |
| line-2 | line-2-0588-0493-s011624 | reverse | revenue | 5 | pending |
| line-2 | line-2-0556-0540-s012911 | forward | revenue | 5 | pending |
| line-2 | line-2-0556-0540-s012911 | reverse | revenue | 4 | pending |
| line-2 | line-2-0468-0674-s016478 | forward | revenue | 4 | pending |
| line-2 | line-2-0468-0674-s016478 | reverse | revenue | 4 | pending |
| line-2 | line-2-0391-0788-s019601 | reverse | revenue | 4 | pending |
| line-2 | line-2-0556-0540-s012911 | reverse | spare | 1 | pending |
| line-2 | line-2-0468-0674-s016478 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0674-s016478 | reverse | spare | 1 | pending |
| line-2 | line-2-0391-0788-s019601 | reverse | spare | 1 | pending |
| line-2 | line-2-0832-0082-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0702-0322-s007014 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0336-0605-s005393 | forward | revenue | 7 | pending |
| line-3 | line-3-0336-0605-s005393 | reverse | revenue | 7 | pending |
| line-3 | line-3-0468-0674-s008673 | forward | revenue | 6 | pending |
| line-3 | line-3-0468-0674-s008673 | reverse | revenue | 6 | pending |
| line-3 | line-3-0701-0794-s014505 | reverse | revenue | 6 | pending |
| line-3 | line-3-0468-0674-s008673 | forward | spare | 1 | pending |
| line-3 | line-3-0468-0674-s008673 | reverse | spare | 1 | pending |
| line-3 | line-3-0701-0794-s014505 | reverse | spare | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**128 trainsets exceed the reference platform envelope**, requiring **7,616.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0354-s021506 | 4 | 2 | 2 | 119.0 |
| line-1-0272-0377-s018533 | 10 | 2 | 8 | 476.0 |
| line-1-0400-0424-s015537 | 10 | 2 | 8 | 476.0 |
| line-1-0531-0472-s012519 | 10 | 2 | 8 | 476.0 |
| line-1-0588-0493-s011205 | 10 | 4 | 6 | 357.0 |
| line-1-0679-0527-s009103 | 10 | 2 | 8 | 476.0 |
| line-1-0769-0560-s007007 | 10 | 2 | 8 | 476.0 |
| line-1-1040-0603-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0391-0788-s019601 | 5 | 2 | 3 | 178.5 |
| line-2-0468-0674-s016478 | 10 | 4 | 6 | 357.0 |
| line-2-0556-0540-s012911 | 10 | 2 | 8 | 476.0 |
| line-2-0588-0493-s011624 | 10 | 4 | 6 | 357.0 |
| line-2-0627-0434-s010015 | 10 | 2 | 8 | 476.0 |
| line-2-0702-0322-s007014 | 11 | 2 | 9 | 535.5 |
| line-2-0832-0082-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0156-0494-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0336-0605-s005393 | 14 | 2 | 12 | 714.0 |
| line-3-0468-0674-s008673 | 14 | 4 | 10 | 595.0 |
| line-3-0701-0794-s014505 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Hail/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
