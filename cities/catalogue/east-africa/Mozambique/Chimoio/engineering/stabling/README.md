# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 68 at depots = 92 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0756-0267-s017600 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0487-0999-s000000 | line-2 | declared-depot | 29 | 1,725.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0469-1000-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0476-0990-s000270 | station | forward | revenue | 1 |
| line-1 | line-1-0476-0990-s000270 | station | reverse | revenue | 1 |
| line-1 | line-1-0575-0714-s007020 | station | forward | revenue | 1 |
| line-1 | line-1-0575-0714-s007020 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0587-s010026 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0587-s010026 | station | reverse | revenue | 1 |
| line-1 | line-1-0659-0507-s011914 | station | forward | revenue | 1 |
| line-1 | line-1-0659-0507-s011914 | station | reverse | revenue | 1 |
| line-1 | line-1-0692-0426-s013819 | station | forward | revenue | 1 |
| line-1 | line-1-0692-0426-s013819 | station | reverse | revenue | 1 |
| line-1 | line-1-0756-0267-s017600 | station | reverse | revenue | 2 |
| line-2 | line-2-0476-0990-s000295 | station | forward | revenue | 1 |
| line-2 | line-2-0476-0990-s000295 | station | reverse | revenue | 1 |
| line-2 | line-2-0487-0999-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0499-0679-s007015 | station | forward | revenue | 1 |
| line-2 | line-2-0499-0679-s007015 | station | reverse | revenue | 1 |
| line-2 | line-2-0520-0537-s010029 | station | forward | revenue | 1 |
| line-2 | line-2-0520-0537-s010029 | station | reverse | revenue | 1 |
| line-2 | line-2-0538-0417-s012590 | station | reverse | revenue | 2 |
| line-1 | line-1-0756-0267-s017600 | depot | — | revenue | 34 |
| line-1 | line-1-0756-0267-s017600 | depot | — | spare | 4 |
| line-1 | line-1-0756-0267-s017600 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0487-0999-s000000 | depot | — | revenue | 25 |
| line-2 | line-2-0487-0999-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0487-0999-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/chimoio-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **92 trainsets at 12 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 7 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0469-1000-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0476-0990-s000270 | forward | revenue | 4 | pending |
| line-1 | line-1-0476-0990-s000270 | reverse | revenue | 4 | pending |
| line-1 | line-1-0575-0714-s007020 | forward | revenue | 4 | pending |
| line-1 | line-1-0575-0714-s007020 | reverse | revenue | 4 | pending |
| line-1 | line-1-0627-0587-s010026 | forward | revenue | 4 | pending |
| line-1 | line-1-0627-0587-s010026 | reverse | revenue | 4 | pending |
| line-1 | line-1-0659-0507-s011914 | forward | revenue | 4 | pending |
| line-1 | line-1-0659-0507-s011914 | reverse | revenue | 4 | pending |
| line-1 | line-1-0692-0426-s013819 | forward | revenue | 4 | pending |
| line-1 | line-1-0692-0426-s013819 | reverse | revenue | 4 | pending |
| line-1 | line-1-0756-0267-s017600 | reverse | revenue | 4 | pending |
| line-1 | line-1-0469-1000-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0476-0990-s000270 | forward | spare | 1 | pending |
| line-1 | line-1-0476-0990-s000270 | reverse | spare | 1 | pending |
| line-1 | line-1-0575-0714-s007020 | forward | spare | 1 | pending |
| line-1 | line-1-0575-0714-s007020 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0487-0999-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0476-0990-s000295 | forward | revenue | 5 | pending |
| line-2 | line-2-0476-0990-s000295 | reverse | revenue | 5 | pending |
| line-2 | line-2-0499-0679-s007015 | forward | revenue | 4 | pending |
| line-2 | line-2-0499-0679-s007015 | reverse | revenue | 4 | pending |
| line-2 | line-2-0520-0537-s010029 | forward | revenue | 4 | pending |
| line-2 | line-2-0520-0537-s010029 | reverse | revenue | 4 | pending |
| line-2 | line-2-0538-0417-s012590 | reverse | revenue | 4 | pending |
| line-2 | line-2-0499-0679-s007015 | forward | spare | 1 | pending |
| line-2 | line-2-0499-0679-s007015 | reverse | spare | 1 | pending |
| line-2 | line-2-0520-0537-s010029 | forward | spare | 1 | pending |
| line-2 | line-2-0520-0537-s010029 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**64 trainsets exceed the reference platform envelope**, requiring **3,808.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0469-1000-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0476-0990-s000270 | 10 | 4 | 6 | 357.0 |
| line-1-0575-0714-s007020 | 10 | 2 | 8 | 476.0 |
| line-1-0627-0587-s010026 | 8 | 2 | 6 | 357.0 |
| line-1-0659-0507-s011914 | 8 | 2 | 6 | 357.0 |
| line-1-0692-0426-s013819 | 8 | 2 | 6 | 357.0 |
| line-1-0756-0267-s017600 | 4 | 2 | 2 | 119.0 |
| line-2-0476-0990-s000295 | 10 | 4 | 6 | 357.0 |
| line-2-0487-0999-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0499-0679-s007015 | 10 | 2 | 8 | 476.0 |
| line-2-0520-0537-s010029 | 10 | 2 | 8 | 476.0 |
| line-2-0538-0417-s012590 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Chimoio/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
