# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 137 at depots = 171 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0155-0354-s020788 | line-1 | declared-depot | 54 | 3,213.0 | 10 |
| line-2-0832-0082-s000000 | line-2 | declared-depot | 48 | 2,856.0 | 9 |
| line-3-0156-0494-s000000 | line-3 | declared-depot | 35 | 2,082.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0354-s020788 | station | reverse | revenue | 2 |
| line-1 | line-1-0277-0379-s017927 | station | forward | revenue | 1 |
| line-1 | line-1-0277-0379-s017927 | station | reverse | revenue | 1 |
| line-1 | line-1-0400-0424-s015048 | station | forward | revenue | 1 |
| line-1 | line-1-0400-0424-s015048 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0472-s012030 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0472-s012030 | station | reverse | revenue | 1 |
| line-1 | line-1-0618-0504-s010025 | station | forward | revenue | 1 |
| line-1 | line-1-0618-0504-s010025 | station | reverse | revenue | 1 |
| line-1 | line-1-0748-0552-s007016 | station | forward | revenue | 1 |
| line-1 | line-1-0748-0552-s007016 | station | reverse | revenue | 1 |
| line-1 | line-1-1040-0603-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0391-0788-s019158 | station | reverse | revenue | 2 |
| line-2 | line-2-0467-0674-s016049 | station | forward | revenue | 1 |
| line-2 | line-2-0467-0674-s016049 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0540-s012468 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0540-s012468 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0451-s010027 | station | forward | revenue | 1 |
| line-2 | line-2-0616-0451-s010027 | station | reverse | revenue | 1 |
| line-2 | line-2-0691-0339-s007013 | station | forward | revenue | 1 |
| line-2 | line-2-0691-0339-s007013 | station | reverse | revenue | 1 |
| line-2 | line-2-0832-0082-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0156-0494-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0336-0605-s005393 | station | forward | revenue | 1 |
| line-3 | line-3-0336-0605-s005393 | station | reverse | revenue | 1 |
| line-3 | line-3-0459-0669-s008465 | station | forward | revenue | 1 |
| line-3 | line-3-0459-0669-s008465 | station | reverse | revenue | 1 |
| line-3 | line-3-0701-0794-s014505 | station | reverse | revenue | 2 |
| line-1 | line-1-0155-0354-s020788 | depot | — | revenue | 47 |
| line-1 | line-1-0155-0354-s020788 | depot | — | spare | 6 |
| line-1 | line-1-0155-0354-s020788 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0832-0082-s000000 | depot | — | revenue | 42 |
| line-2 | line-2-0832-0082-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0832-0082-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0156-0494-s000000 | depot | — | revenue | 31 |
| line-3 | line-3-0156-0494-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0156-0494-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hail-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **171 trainsets at 17 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **154 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **137 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1040-0603-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0748-0552-s007016 | forward | revenue | 5 | pending |
| line-1 | line-1-0748-0552-s007016 | reverse | revenue | 5 | pending |
| line-1 | line-1-0618-0504-s010025 | forward | revenue | 5 | pending |
| line-1 | line-1-0618-0504-s010025 | reverse | revenue | 5 | pending |
| line-1 | line-1-0531-0472-s012030 | forward | revenue | 5 | pending |
| line-1 | line-1-0531-0472-s012030 | reverse | revenue | 5 | pending |
| line-1 | line-1-0400-0424-s015048 | forward | revenue | 5 | pending |
| line-1 | line-1-0400-0424-s015048 | reverse | revenue | 5 | pending |
| line-1 | line-1-0277-0379-s017927 | forward | revenue | 5 | pending |
| line-1 | line-1-0277-0379-s017927 | reverse | revenue | 5 | pending |
| line-1 | line-1-0155-0354-s020788 | reverse | revenue | 5 | pending |
| line-1 | line-1-0748-0552-s007016 | forward | spare | 1 | pending |
| line-1 | line-1-0748-0552-s007016 | reverse | spare | 1 | pending |
| line-1 | line-1-0618-0504-s010025 | forward | spare | 1 | pending |
| line-1 | line-1-0618-0504-s010025 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0472-s012030 | forward | spare | 1 | pending |
| line-1 | line-1-0531-0472-s012030 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-0424-s015048 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0832-0082-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0691-0339-s007013 | forward | revenue | 6 | pending |
| line-2 | line-2-0691-0339-s007013 | reverse | revenue | 6 | pending |
| line-2 | line-2-0616-0451-s010027 | forward | revenue | 6 | pending |
| line-2 | line-2-0616-0451-s010027 | reverse | revenue | 5 | pending |
| line-2 | line-2-0556-0540-s012468 | forward | revenue | 5 | pending |
| line-2 | line-2-0556-0540-s012468 | reverse | revenue | 5 | pending |
| line-2 | line-2-0467-0674-s016049 | forward | revenue | 5 | pending |
| line-2 | line-2-0467-0674-s016049 | reverse | revenue | 5 | pending |
| line-2 | line-2-0391-0788-s019158 | reverse | revenue | 5 | pending |
| line-2 | line-2-0616-0451-s010027 | reverse | spare | 1 | pending |
| line-2 | line-2-0556-0540-s012468 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0540-s012468 | reverse | spare | 1 | pending |
| line-2 | line-2-0467-0674-s016049 | forward | spare | 1 | pending |
| line-2 | line-2-0467-0674-s016049 | reverse | spare | 1 | pending |
| line-2 | line-2-0391-0788-s019158 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0336-0605-s005393 | forward | revenue | 7 | pending |
| line-3 | line-3-0336-0605-s005393 | reverse | revenue | 7 | pending |
| line-3 | line-3-0459-0669-s008465 | forward | revenue | 6 | pending |
| line-3 | line-3-0459-0669-s008465 | reverse | revenue | 6 | pending |
| line-3 | line-3-0701-0794-s014505 | reverse | revenue | 6 | pending |
| line-3 | line-3-0459-0669-s008465 | forward | spare | 1 | pending |
| line-3 | line-3-0459-0669-s008465 | reverse | spare | 1 | pending |
| line-3 | line-3-0701-0794-s014505 | reverse | spare | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**133 trainsets exceed the reference platform envelope**, requiring **7,913.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0354-s020788 | 5 | 2 | 3 | 178.5 |
| line-1-0277-0379-s017927 | 10 | 2 | 8 | 476.0 |
| line-1-0400-0424-s015048 | 11 | 2 | 9 | 535.5 |
| line-1-0531-0472-s012030 | 12 | 2 | 10 | 595.0 |
| line-1-0618-0504-s010025 | 12 | 2 | 10 | 595.0 |
| line-1-0748-0552-s007016 | 12 | 2 | 10 | 595.0 |
| line-1-1040-0603-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0391-0788-s019158 | 6 | 2 | 4 | 238.0 |
| line-2-0467-0674-s016049 | 12 | 4 | 8 | 476.0 |
| line-2-0556-0540-s012468 | 12 | 2 | 10 | 595.0 |
| line-2-0616-0451-s010027 | 12 | 2 | 10 | 595.0 |
| line-2-0691-0339-s007013 | 12 | 2 | 10 | 595.0 |
| line-2-0832-0082-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0156-0494-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0336-0605-s005393 | 14 | 2 | 12 | 714.0 |
| line-3-0459-0669-s008465 | 14 | 4 | 10 | 595.0 |
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
