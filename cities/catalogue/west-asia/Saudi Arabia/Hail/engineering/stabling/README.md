# Station and depot overnight allocation

Plan: **42 trainsets at stations + 91 at depots = 133 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0155-0354-s025289 | 91 | 5,414.5 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0155-0354-s025289 | station | reverse | revenue | 2 |
| line-1 | line-1-0231-0400-s022729 | station | forward | revenue | 1 |
| line-1 | line-1-0231-0400-s022729 | station | reverse | revenue | 1 |
| line-1 | line-1-0297-0456-s020179 | station | forward | revenue | 1 |
| line-1 | line-1-0297-0456-s020179 | station | reverse | revenue | 1 |
| line-1 | line-1-0410-0422-s017638 | station | forward | revenue | 1 |
| line-1 | line-1-0410-0422-s017638 | station | reverse | revenue | 1 |
| line-1 | line-1-0519-0476-s014621 | station | forward | revenue | 1 |
| line-1 | line-1-0519-0476-s014621 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0534-s013041 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0534-s013041 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0590-s010015 | station | forward | revenue | 1 |
| line-1 | line-1-0647-0590-s010015 | station | reverse | revenue | 1 |
| line-1 | line-1-0746-0621-s007003 | station | forward | revenue | 1 |
| line-1 | line-1-0746-0621-s007003 | station | reverse | revenue | 1 |
| line-1 | line-1-1040-0603-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0391-0788-s021900 | station | reverse | revenue | 2 |
| line-2 | line-2-0430-0695-s019179 | station | forward | revenue | 1 |
| line-2 | line-2-0430-0695-s019179 | station | reverse | revenue | 1 |
| line-2 | line-2-0487-0596-s016054 | station | forward | revenue | 1 |
| line-2 | line-2-0487-0596-s016054 | station | reverse | revenue | 1 |
| line-2 | line-2-0547-0534-s014317 | station | forward | revenue | 1 |
| line-2 | line-2-0547-0534-s014317 | station | reverse | revenue | 1 |
| line-2 | line-2-0596-0512-s013034 | station | forward | revenue | 1 |
| line-2 | line-2-0596-0512-s013034 | station | reverse | revenue | 1 |
| line-2 | line-2-0622-0424-s010031 | station | forward | revenue | 1 |
| line-2 | line-2-0622-0424-s010031 | station | reverse | revenue | 1 |
| line-2 | line-2-0650-0318-s007025 | station | forward | revenue | 1 |
| line-2 | line-2-0650-0318-s007025 | station | reverse | revenue | 1 |
| line-2 | line-2-0832-0082-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0156-0494-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0361-0574-s006444 | station | forward | revenue | 1 |
| line-3 | line-3-0361-0574-s006444 | station | reverse | revenue | 1 |
| line-3 | line-3-0475-0661-s009760 | station | forward | revenue | 1 |
| line-3 | line-3-0475-0661-s009760 | station | reverse | revenue | 1 |
| line-3 | line-3-0701-0794-s015926 | station | reverse | revenue | 2 |
| line-1 | line-1-0155-0354-s025289 | depot | — | revenue | 30 |
| line-1 | line-1-0155-0354-s025289 | depot | — | spare | 4 |
| line-1 | line-1-0155-0354-s025289 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0155-0354-s025289 | depot | — | revenue | 27 |
| line-2 | line-1-0155-0354-s025289 | depot | — | spare | 4 |
| line-2 | line-1-0155-0354-s025289 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0155-0354-s025289 | depot | — | revenue | 21 |
| line-3 | line-1-0155-0354-s025289 | depot | — | spare | 2 |
| line-3 | line-1-0155-0354-s025289 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (32 trains), line-3 (24 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **133 trainsets at 21 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **91 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1040-0603-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0746-0621-s007003 | forward | revenue | 3 | pending |
| line-1 | line-1-0746-0621-s007003 | reverse | revenue | 3 | pending |
| line-1 | line-1-0647-0590-s010015 | forward | revenue | 3 | pending |
| line-1 | line-1-0647-0590-s010015 | reverse | revenue | 3 | pending |
| line-1 | line-1-0547-0534-s013041 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0534-s013041 | reverse | revenue | 3 | pending |
| line-1 | line-1-0519-0476-s014621 | forward | revenue | 3 | pending |
| line-1 | line-1-0519-0476-s014621 | reverse | revenue | 3 | pending |
| line-1 | line-1-0410-0422-s017638 | forward | revenue | 3 | pending |
| line-1 | line-1-0410-0422-s017638 | reverse | revenue | 3 | pending |
| line-1 | line-1-0297-0456-s020179 | forward | revenue | 3 | pending |
| line-1 | line-1-0297-0456-s020179 | reverse | revenue | 3 | pending |
| line-1 | line-1-0231-0400-s022729 | forward | revenue | 3 | pending |
| line-1 | line-1-0231-0400-s022729 | reverse | revenue | 3 | pending |
| line-1 | line-1-0155-0354-s025289 | reverse | revenue | 3 | pending |
| line-1 | line-1-1040-0603-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0746-0621-s007003 | forward | spare | 1 | pending |
| line-1 | line-1-0746-0621-s007003 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0590-s010015 | forward | spare | 1 | pending |
| line-1 | line-1-0647-0590-s010015 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0832-0082-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0650-0318-s007025 | forward | revenue | 3 | pending |
| line-2 | line-2-0650-0318-s007025 | reverse | revenue | 3 | pending |
| line-2 | line-2-0622-0424-s010031 | forward | revenue | 3 | pending |
| line-2 | line-2-0622-0424-s010031 | reverse | revenue | 3 | pending |
| line-2 | line-2-0596-0512-s013034 | forward | revenue | 3 | pending |
| line-2 | line-2-0596-0512-s013034 | reverse | revenue | 3 | pending |
| line-2 | line-2-0547-0534-s014317 | forward | revenue | 3 | pending |
| line-2 | line-2-0547-0534-s014317 | reverse | revenue | 3 | pending |
| line-2 | line-2-0487-0596-s016054 | forward | revenue | 3 | pending |
| line-2 | line-2-0487-0596-s016054 | reverse | revenue | 3 | pending |
| line-2 | line-2-0430-0695-s019179 | forward | revenue | 3 | pending |
| line-2 | line-2-0430-0695-s019179 | reverse | revenue | 3 | pending |
| line-2 | line-2-0391-0788-s021900 | reverse | revenue | 3 | pending |
| line-2 | line-2-0650-0318-s007025 | forward | spare | 1 | pending |
| line-2 | line-2-0650-0318-s007025 | reverse | spare | 1 | pending |
| line-2 | line-2-0622-0424-s010031 | forward | spare | 1 | pending |
| line-2 | line-2-0622-0424-s010031 | reverse | spare | 1 | pending |
| line-2 | line-2-0596-0512-s013034 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0361-0574-s006444 | forward | revenue | 5 | pending |
| line-3 | line-3-0361-0574-s006444 | reverse | revenue | 5 | pending |
| line-3 | line-3-0475-0661-s009760 | forward | revenue | 5 | pending |
| line-3 | line-3-0475-0661-s009760 | reverse | revenue | 5 | pending |
| line-3 | line-3-0701-0794-s015926 | reverse | revenue | 4 | pending |
| line-3 | line-3-0701-0794-s015926 | reverse | spare | 1 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0361-0574-s006444 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**87 trainsets exceed the reference platform envelope**, requiring **5,176.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0155-0354-s025289 | 3 | 2 | 1 | 59.5 |
| line-1-0231-0400-s022729 | 6 | 2 | 4 | 238.0 |
| line-1-0297-0456-s020179 | 6 | 2 | 4 | 238.0 |
| line-1-0410-0422-s017638 | 6 | 2 | 4 | 238.0 |
| line-1-0519-0476-s014621 | 6 | 2 | 4 | 238.0 |
| line-1-0547-0534-s013041 | 6 | 4 | 2 | 119.0 |
| line-1-0647-0590-s010015 | 8 | 2 | 6 | 357.0 |
| line-1-0746-0621-s007003 | 8 | 2 | 6 | 357.0 |
| line-1-1040-0603-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0391-0788-s021900 | 3 | 2 | 1 | 59.5 |
| line-2-0430-0695-s019179 | 6 | 2 | 4 | 238.0 |
| line-2-0487-0596-s016054 | 6 | 2 | 4 | 238.0 |
| line-2-0547-0534-s014317 | 6 | 4 | 2 | 119.0 |
| line-2-0596-0512-s013034 | 7 | 2 | 5 | 297.5 |
| line-2-0622-0424-s010031 | 8 | 2 | 6 | 357.0 |
| line-2-0650-0318-s007025 | 8 | 2 | 6 | 357.0 |
| line-2-0832-0082-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0156-0494-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0361-0574-s006444 | 11 | 2 | 9 | 535.5 |
| line-3-0475-0661-s009760 | 10 | 2 | 8 | 476.0 |
| line-3-0701-0794-s015926 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Hail/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
