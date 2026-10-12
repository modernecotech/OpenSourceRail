# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 31 at depots = 65 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0707-0423-s012342 | line-1 | declared-depot | 14 | 686.0 | 4 |
| line-2-0418-0315-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0391-0244-s000000 | line-3 | declared-depot | 5 | 245.0 | 3 |
| line-4-0418-0315-s000000 | line-4 | declared-depot | 7 | 343.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0392-0280-s001361 | station | forward | revenue | 1 |
| line-1 | line-1-0392-0280-s001361 | station | reverse | revenue | 1 |
| line-1 | line-1-0394-0351-s004079 | station | forward | revenue | 1 |
| line-1 | line-1-0394-0351-s004079 | station | reverse | revenue | 1 |
| line-1 | line-1-0406-0351-s004352 | station | forward | revenue | 1 |
| line-1 | line-1-0406-0351-s004352 | station | reverse | revenue | 1 |
| line-1 | line-1-0425-0237-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0463-0411-s006024 | station | forward | revenue | 1 |
| line-1 | line-1-0463-0411-s006024 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0423-s012342 | station | reverse | revenue | 2 |
| line-2 | line-2-0367-0469-s003538 | station | reverse | revenue | 2 |
| line-2 | line-2-0395-0383-s001562 | station | forward | revenue | 1 |
| line-2 | line-2-0395-0383-s001562 | station | reverse | revenue | 1 |
| line-2 | line-2-0406-0351-s000831 | station | forward | revenue | 1 |
| line-2 | line-2-0406-0351-s000831 | station | reverse | revenue | 1 |
| line-2 | line-2-0418-0315-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0391-0244-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0392-0280-s000728 | station | forward | revenue | 1 |
| line-3 | line-3-0392-0280-s000728 | station | reverse | revenue | 1 |
| line-3 | line-3-0394-0351-s002177 | station | forward | revenue | 1 |
| line-3 | line-3-0394-0351-s002177 | station | reverse | revenue | 1 |
| line-3 | line-3-0395-0383-s002825 | station | forward | revenue | 1 |
| line-3 | line-3-0395-0383-s002825 | station | reverse | revenue | 1 |
| line-3 | line-3-0396-0442-s004013 | station | reverse | revenue | 2 |
| line-4 | line-4-0418-0315-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0511-0238-s004952 | station | reverse | revenue | 2 |
| line-1 | line-1-0707-0423-s012342 | depot | — | revenue | 11 |
| line-1 | line-1-0707-0423-s012342 | depot | — | spare | 2 |
| line-1 | line-1-0707-0423-s012342 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0418-0315-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0418-0315-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0418-0315-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0391-0244-s000000 | depot | — | revenue | 3 |
| line-3 | line-3-0391-0244-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0391-0244-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0418-0315-s000000 | depot | — | revenue | 5 |
| line-4 | line-4-0418-0315-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0418-0315-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tabora-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **65 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **56 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **31 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0425-0237-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0392-0280-s001361 | forward | revenue | 3 | pending |
| line-1 | line-1-0392-0280-s001361 | reverse | revenue | 3 | pending |
| line-1 | line-1-0394-0351-s004079 | forward | revenue | 2 | pending |
| line-1 | line-1-0394-0351-s004079 | reverse | revenue | 2 | pending |
| line-1 | line-1-0406-0351-s004352 | forward | revenue | 2 | pending |
| line-1 | line-1-0406-0351-s004352 | reverse | revenue | 2 | pending |
| line-1 | line-1-0463-0411-s006024 | forward | revenue | 2 | pending |
| line-1 | line-1-0463-0411-s006024 | reverse | revenue | 2 | pending |
| line-1 | line-1-0707-0423-s012342 | reverse | revenue | 2 | pending |
| line-1 | line-1-0394-0351-s004079 | forward | spare | 1 | pending |
| line-1 | line-1-0394-0351-s004079 | reverse | spare | 1 | pending |
| line-1 | line-1-0406-0351-s004352 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0406-0351-s000831 | forward | revenue | 2 | pending |
| line-2 | line-2-0406-0351-s000831 | reverse | revenue | 2 | pending |
| line-2 | line-2-0395-0383-s001562 | forward | revenue | 2 | pending |
| line-2 | line-2-0395-0383-s001562 | reverse | revenue | 2 | pending |
| line-2 | line-2-0367-0469-s003538 | reverse | revenue | 1 | pending |
| line-2 | line-2-0367-0469-s003538 | reverse | spare | 1 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0391-0244-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0392-0280-s000728 | forward | revenue | 2 | pending |
| line-3 | line-3-0392-0280-s000728 | reverse | revenue | 2 | pending |
| line-3 | line-3-0394-0351-s002177 | forward | revenue | 2 | pending |
| line-3 | line-3-0394-0351-s002177 | reverse | revenue | 2 | pending |
| line-3 | line-3-0395-0383-s002825 | forward | revenue | 1 | pending |
| line-3 | line-3-0395-0383-s002825 | reverse | revenue | 1 | pending |
| line-3 | line-3-0396-0442-s004013 | reverse | revenue | 1 | pending |
| line-3 | line-3-0395-0383-s002825 | forward | spare | 1 | pending |
| line-3 | line-3-0395-0383-s002825 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0418-0315-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0511-0238-s004952 | reverse | revenue | 4 | pending |
| line-4 | line-4-0511-0238-s004952 | reverse | spare | 1 | pending |
| line-4 | line-4-0418-0315-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**16 trainsets exceed the reference platform envelope**, requiring **784.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0392-0280-s001361 | 6 | 4 | 2 | 98.0 |
| line-1-0394-0351-s004079 | 6 | 4 | 2 | 98.0 |
| line-1-0406-0351-s004352 | 5 | 4 | 1 | 49.0 |
| line-1-0425-0237-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0463-0411-s006024 | 4 | 2 | 2 | 98.0 |
| line-1-0707-0423-s012342 | 2 | 2 | 0 | 0.0 |
| line-2-0367-0469-s003538 | 2 | 2 | 0 | 0.0 |
| line-2-0395-0383-s001562 | 4 | 4 | 0 | 0.0 |
| line-2-0406-0351-s000831 | 4 | 4 | 0 | 0.0 |
| line-2-0418-0315-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0391-0244-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0392-0280-s000728 | 4 | 4 | 0 | 0.0 |
| line-3-0394-0351-s002177 | 4 | 4 | 0 | 0.0 |
| line-3-0395-0383-s002825 | 4 | 4 | 0 | 0.0 |
| line-3-0396-0442-s004013 | 1 | 2 | 0 | 0.0 |
| line-4-0418-0315-s000000 | 6 | 2 | 4 | 196.0 |
| line-4-0511-0238-s004952 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tabora/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
