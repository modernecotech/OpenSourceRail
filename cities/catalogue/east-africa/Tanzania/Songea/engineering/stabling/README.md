# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 32 at depots = 68 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0347-0350-s000000 | line-1 | declared-depot | 5 | 245.0 | 2 |
| line-2-0325-0358-s008107 | line-2 | declared-depot | 11 | 539.0 | 3 |
| line-3-0317-0259-s000000 | line-3 | declared-depot | 5 | 245.0 | 2 |
| line-4-0321-0299-s000000 | line-4 | declared-depot | 7 | 343.0 | 3 |
| line-5-0347-0350-s000000 | line-5 | declared-depot | 4 | 196.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0172-0388-s003827 | station | reverse | revenue | 2 |
| line-1 | line-1-0253-0370-s002057 | station | forward | revenue | 1 |
| line-1 | line-1-0253-0370-s002057 | station | reverse | revenue | 1 |
| line-1 | line-1-0325-0355-s000481 | station | forward | revenue | 1 |
| line-1 | line-1-0325-0355-s000481 | station | reverse | revenue | 1 |
| line-1 | line-1-0347-0350-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0317-0259-s006061 | station | forward | revenue | 1 |
| line-2 | line-2-0317-0259-s006061 | station | reverse | revenue | 1 |
| line-2 | line-2-0321-0299-s006894 | station | forward | revenue | 1 |
| line-2 | line-2-0321-0299-s006894 | station | reverse | revenue | 1 |
| line-2 | line-2-0325-0358-s008107 | station | reverse | revenue | 2 |
| line-2 | line-2-0364-0009-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0237-0287-s001832 | station | forward | revenue | 1 |
| line-3 | line-3-0237-0287-s001832 | station | reverse | revenue | 1 |
| line-3 | line-3-0253-0370-s003625 | station | reverse | revenue | 2 |
| line-3 | line-3-0317-0259-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0321-0299-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0339-0462-s005698 | station | reverse | revenue | 2 |
| line-4 | line-4-0375-0400-s004160 | station | forward | revenue | 1 |
| line-4 | line-4-0375-0400-s004160 | station | reverse | revenue | 1 |
| line-4 | line-4-0388-0288-s001431 | station | forward | revenue | 1 |
| line-4 | line-4-0388-0288-s001431 | station | reverse | revenue | 1 |
| line-5 | line-5-0347-0350-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0375-0400-s001232 | station | forward | revenue | 1 |
| line-5 | line-5-0375-0400-s001232 | station | reverse | revenue | 1 |
| line-5 | line-5-0412-0437-s002278 | station | reverse | revenue | 2 |
| line-1 | line-1-0347-0350-s000000 | depot | — | revenue | 3 |
| line-1 | line-1-0347-0350-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0347-0350-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0325-0358-s008107 | depot | — | revenue | 9 |
| line-2 | line-2-0325-0358-s008107 | depot | — | spare | 1 |
| line-2 | line-2-0325-0358-s008107 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0317-0259-s000000 | depot | — | revenue | 3 |
| line-3 | line-3-0317-0259-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0317-0259-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0321-0299-s000000 | depot | — | revenue | 5 |
| line-4 | line-4-0321-0299-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0321-0299-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0347-0350-s000000 | depot | — | revenue | 2 |
| line-5 | line-5-0347-0350-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0347-0350-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/songea-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **68 trainsets at 18 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **58 revenue, 5 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **32 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0347-0350-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0325-0355-s000481 | forward | revenue | 2 | pending |
| line-1 | line-1-0325-0355-s000481 | reverse | revenue | 2 | pending |
| line-1 | line-1-0253-0370-s002057 | forward | revenue | 2 | pending |
| line-1 | line-1-0253-0370-s002057 | reverse | revenue | 2 | pending |
| line-1 | line-1-0172-0388-s003827 | reverse | revenue | 1 | pending |
| line-1 | line-1-0172-0388-s003827 | reverse | spare | 1 | pending |
| line-1 | line-1-0347-0350-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0364-0009-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0317-0259-s006061 | forward | revenue | 3 | pending |
| line-2 | line-2-0317-0259-s006061 | reverse | revenue | 3 | pending |
| line-2 | line-2-0321-0299-s006894 | forward | revenue | 3 | pending |
| line-2 | line-2-0321-0299-s006894 | reverse | revenue | 3 | pending |
| line-2 | line-2-0325-0358-s008107 | reverse | revenue | 2 | pending |
| line-2 | line-2-0325-0358-s008107 | reverse | spare | 1 | pending |
| line-2 | line-2-0364-0009-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0317-0259-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0237-0287-s001832 | forward | revenue | 2 | pending |
| line-3 | line-3-0237-0287-s001832 | reverse | revenue | 2 | pending |
| line-3 | line-3-0253-0370-s003625 | reverse | revenue | 2 | pending |
| line-3 | line-3-0237-0287-s001832 | forward | spare | 1 | pending |
| line-3 | line-3-0237-0287-s001832 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0321-0299-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0388-0288-s001431 | forward | revenue | 2 | pending |
| line-4 | line-4-0388-0288-s001431 | reverse | revenue | 2 | pending |
| line-4 | line-4-0375-0400-s004160 | forward | revenue | 2 | pending |
| line-4 | line-4-0375-0400-s004160 | reverse | revenue | 2 | pending |
| line-4 | line-4-0339-0462-s005698 | reverse | revenue | 2 | pending |
| line-4 | line-4-0388-0288-s001431 | forward | spare | 1 | pending |
| line-4 | line-4-0388-0288-s001431 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0347-0350-s000000 | forward | revenue | 2 | pending |
| line-5 | line-5-0375-0400-s001232 | forward | revenue | 2 | pending |
| line-5 | line-5-0375-0400-s001232 | reverse | revenue | 2 | pending |
| line-5 | line-5-0412-0437-s002278 | reverse | revenue | 2 | pending |
| line-5 | line-5-0347-0350-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0375-0400-s001232 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**20 trainsets exceed the reference platform envelope**, requiring **980.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0172-0388-s003827 | 2 | 2 | 0 | 0.0 |
| line-1-0253-0370-s002057 | 4 | 4 | 0 | 0.0 |
| line-1-0325-0355-s000481 | 4 | 4 | 0 | 0.0 |
| line-1-0347-0350-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0317-0259-s006061 | 6 | 4 | 2 | 98.0 |
| line-2-0321-0299-s006894 | 6 | 4 | 2 | 98.0 |
| line-2-0325-0358-s008107 | 3 | 2 | 1 | 49.0 |
| line-2-0364-0009-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0237-0287-s001832 | 6 | 2 | 4 | 196.0 |
| line-3-0253-0370-s003625 | 2 | 2 | 0 | 0.0 |
| line-3-0317-0259-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0321-0299-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0339-0462-s005698 | 2 | 2 | 0 | 0.0 |
| line-4-0375-0400-s004160 | 4 | 4 | 0 | 0.0 |
| line-4-0388-0288-s001431 | 6 | 2 | 4 | 196.0 |
| line-5-0347-0350-s000000 | 3 | 2 | 1 | 49.0 |
| line-5-0375-0400-s001232 | 5 | 4 | 1 | 49.0 |
| line-5-0412-0437-s002278 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Songea/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
