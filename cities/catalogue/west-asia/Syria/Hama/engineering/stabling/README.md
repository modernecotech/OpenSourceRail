# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 97 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0708-0757-s017704 | line-1 | declared-depot | 42 | 2,499.0 | 8 |
| line-2-0768-0539-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0581-0072-s000000 | line-3 | declared-depot | 33 | 1,963.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0194-0142-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0409-0385-s007025 | station | forward | revenue | 1 |
| line-1 | line-1-0409-0385-s007025 | station | reverse | revenue | 1 |
| line-1 | line-1-0493-0490-s010044 | station | forward | revenue | 1 |
| line-1 | line-1-0493-0490-s010044 | station | reverse | revenue | 1 |
| line-1 | line-1-0546-0555-s011912 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0555-s011912 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0656-s014814 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0656-s014814 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s017704 | station | reverse | revenue | 2 |
| line-2 | line-2-0313-0629-s009846 | station | reverse | revenue | 2 |
| line-2 | line-2-0424-0607-s007443 | station | forward | revenue | 1 |
| line-2 | line-2-0424-0607-s007443 | station | reverse | revenue | 1 |
| line-2 | line-2-0534-0585-s005061 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0585-s005061 | station | reverse | revenue | 1 |
| line-2 | line-2-0645-0563-s002659 | station | forward | revenue | 1 |
| line-2 | line-2-0645-0563-s002659 | station | reverse | revenue | 1 |
| line-2 | line-2-0768-0539-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0581-0072-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0586-0750-s013789 | station | reverse | revenue | 2 |
| line-3 | line-3-0587-0643-s011641 | station | forward | revenue | 1 |
| line-3 | line-3-0587-0643-s011641 | station | reverse | revenue | 1 |
| line-3 | line-3-0588-0537-s009512 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0537-s009512 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0387-s006496 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0387-s006496 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s017704 | depot | — | revenue | 37 |
| line-1 | line-1-0708-0757-s017704 | depot | — | spare | 4 |
| line-1 | line-1-0708-0757-s017704 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0768-0539-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0768-0539-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0768-0539-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0581-0072-s000000 | depot | — | revenue | 29 |
| line-3 | line-3-0581-0072-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0581-0072-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hama-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **97 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0194-0142-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0409-0385-s007025 | forward | revenue | 5 | pending |
| line-1 | line-1-0409-0385-s007025 | reverse | revenue | 5 | pending |
| line-1 | line-1-0493-0490-s010044 | forward | revenue | 5 | pending |
| line-1 | line-1-0493-0490-s010044 | reverse | revenue | 5 | pending |
| line-1 | line-1-0546-0555-s011912 | forward | revenue | 5 | pending |
| line-1 | line-1-0546-0555-s011912 | reverse | revenue | 5 | pending |
| line-1 | line-1-0627-0656-s014814 | forward | revenue | 5 | pending |
| line-1 | line-1-0627-0656-s014814 | reverse | revenue | 5 | pending |
| line-1 | line-1-0708-0757-s017704 | reverse | revenue | 4 | pending |
| line-1 | line-1-0708-0757-s017704 | reverse | spare | 1 | pending |
| line-1 | line-1-0194-0142-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0409-0385-s007025 | forward | spare | 1 | pending |
| line-1 | line-1-0409-0385-s007025 | reverse | spare | 1 | pending |
| line-1 | line-1-0493-0490-s010044 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0768-0539-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0645-0563-s002659 | forward | revenue | 4 | pending |
| line-2 | line-2-0645-0563-s002659 | reverse | revenue | 4 | pending |
| line-2 | line-2-0534-0585-s005061 | forward | revenue | 4 | pending |
| line-2 | line-2-0534-0585-s005061 | reverse | revenue | 4 | pending |
| line-2 | line-2-0424-0607-s007443 | forward | revenue | 3 | pending |
| line-2 | line-2-0424-0607-s007443 | reverse | revenue | 3 | pending |
| line-2 | line-2-0313-0629-s009846 | reverse | revenue | 3 | pending |
| line-2 | line-2-0424-0607-s007443 | forward | spare | 1 | pending |
| line-2 | line-2-0424-0607-s007443 | reverse | spare | 1 | pending |
| line-2 | line-2-0313-0629-s009846 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0387-s006496 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0387-s006496 | reverse | revenue | 5 | pending |
| line-3 | line-3-0588-0537-s009512 | forward | revenue | 5 | pending |
| line-3 | line-3-0588-0537-s009512 | reverse | revenue | 5 | pending |
| line-3 | line-3-0587-0643-s011641 | forward | revenue | 5 | pending |
| line-3 | line-3-0587-0643-s011641 | reverse | revenue | 5 | pending |
| line-3 | line-3-0586-0750-s013789 | reverse | revenue | 4 | pending |
| line-3 | line-3-0586-0750-s013789 | reverse | spare | 1 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0387-s006496 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0387-s006496 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**93 trainsets exceed the reference platform envelope**, requiring **5,533.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0194-0142-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0409-0385-s007025 | 12 | 2 | 10 | 595.0 |
| line-1-0493-0490-s010044 | 11 | 2 | 9 | 535.5 |
| line-1-0546-0555-s011912 | 10 | 4 | 6 | 357.0 |
| line-1-0627-0656-s014814 | 10 | 2 | 8 | 476.0 |
| line-1-0708-0757-s017704 | 5 | 2 | 3 | 178.5 |
| line-2-0313-0629-s009846 | 4 | 2 | 2 | 119.0 |
| line-2-0424-0607-s007443 | 8 | 2 | 6 | 357.0 |
| line-2-0534-0585-s005061 | 8 | 4 | 4 | 238.0 |
| line-2-0645-0563-s002659 | 8 | 2 | 6 | 357.0 |
| line-2-0768-0539-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0581-0072-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0586-0750-s013789 | 5 | 2 | 3 | 178.5 |
| line-3-0587-0643-s011641 | 10 | 2 | 8 | 476.0 |
| line-3-0588-0537-s009512 | 10 | 2 | 8 | 476.0 |
| line-3-0590-0387-s006496 | 12 | 2 | 10 | 595.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Hama/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
