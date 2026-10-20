# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 36 at depots = 70 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0530-0342-s000000 | line-1 | declared-depot | 9 | 441.0 | 3 |
| line-2-0210-0463-s011616 | line-2 | declared-depot | 15 | 735.0 | 4 |
| line-3-0330-0343-s000000 | line-3 | declared-depot | 6 | 294.0 | 2 |
| line-4-0372-0375-s000000 | line-4 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0318-0258-s008262 | station | reverse | revenue | 2 |
| line-1 | line-1-0348-0359-s004928 | station | forward | revenue | 1 |
| line-1 | line-1-0348-0359-s004928 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0375-s004146 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0375-s004146 | station | reverse | revenue | 1 |
| line-1 | line-1-0530-0342-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0210-0463-s011616 | station | reverse | revenue | 2 |
| line-2 | line-2-0278-0389-s009094 | station | forward | revenue | 1 |
| line-2 | line-2-0278-0389-s009094 | station | reverse | revenue | 1 |
| line-2 | line-2-0287-0389-s008914 | station | forward | revenue | 1 |
| line-2 | line-2-0287-0389-s008914 | station | reverse | revenue | 1 |
| line-2 | line-2-0525-0424-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0525-0424-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0475-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0330-0343-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0348-0359-s000613 | station | forward | revenue | 1 |
| line-3 | line-3-0348-0359-s000613 | station | reverse | revenue | 1 |
| line-3 | line-3-0373-0375-s001395 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0375-s001395 | station | reverse | revenue | 1 |
| line-3 | line-3-0454-0260-s004722 | station | reverse | revenue | 2 |
| line-4 | line-4-0239-0313-s004107 | station | reverse | revenue | 2 |
| line-4 | line-4-0278-0389-s002123 | station | forward | revenue | 1 |
| line-4 | line-4-0278-0389-s002123 | station | reverse | revenue | 1 |
| line-4 | line-4-0287-0389-s001943 | station | forward | revenue | 1 |
| line-4 | line-4-0287-0389-s001943 | station | reverse | revenue | 1 |
| line-4 | line-4-0372-0375-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0530-0342-s000000 | depot | — | revenue | 7 |
| line-1 | line-1-0530-0342-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0530-0342-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0210-0463-s011616 | depot | — | revenue | 12 |
| line-2 | line-2-0210-0463-s011616 | depot | — | spare | 2 |
| line-2 | line-2-0210-0463-s011616 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0330-0343-s000000 | depot | — | revenue | 4 |
| line-3 | line-3-0330-0343-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0330-0343-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0372-0375-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0372-0375-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0372-0375-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/garissa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **70 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **61 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **36 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0530-0342-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0373-0375-s004146 | forward | revenue | 3 | pending |
| line-1 | line-1-0373-0375-s004146 | reverse | revenue | 3 | pending |
| line-1 | line-1-0348-0359-s004928 | forward | revenue | 2 | pending |
| line-1 | line-1-0348-0359-s004928 | reverse | revenue | 2 | pending |
| line-1 | line-1-0318-0258-s008262 | reverse | revenue | 2 | pending |
| line-1 | line-1-0348-0359-s004928 | forward | spare | 1 | pending |
| line-1 | line-1-0348-0359-s004928 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0644-0475-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0525-0424-s003010 | forward | revenue | 3 | pending |
| line-2 | line-2-0525-0424-s003010 | reverse | revenue | 3 | pending |
| line-2 | line-2-0287-0389-s008914 | forward | revenue | 3 | pending |
| line-2 | line-2-0287-0389-s008914 | reverse | revenue | 3 | pending |
| line-2 | line-2-0278-0389-s009094 | forward | revenue | 3 | pending |
| line-2 | line-2-0278-0389-s009094 | reverse | revenue | 2 | pending |
| line-2 | line-2-0210-0463-s011616 | reverse | revenue | 2 | pending |
| line-2 | line-2-0278-0389-s009094 | reverse | spare | 1 | pending |
| line-2 | line-2-0210-0463-s011616 | reverse | spare | 1 | pending |
| line-2 | line-2-0644-0475-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0330-0343-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0348-0359-s000613 | forward | revenue | 2 | pending |
| line-3 | line-3-0348-0359-s000613 | reverse | revenue | 2 | pending |
| line-3 | line-3-0373-0375-s001395 | forward | revenue | 2 | pending |
| line-3 | line-3-0373-0375-s001395 | reverse | revenue | 2 | pending |
| line-3 | line-3-0454-0260-s004722 | reverse | revenue | 2 | pending |
| line-3 | line-3-0330-0343-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0348-0359-s000613 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0372-0375-s000000 | forward | revenue | 2 | pending |
| line-4 | line-4-0287-0389-s001943 | forward | revenue | 2 | pending |
| line-4 | line-4-0287-0389-s001943 | reverse | revenue | 2 | pending |
| line-4 | line-4-0278-0389-s002123 | forward | revenue | 2 | pending |
| line-4 | line-4-0278-0389-s002123 | reverse | revenue | 2 | pending |
| line-4 | line-4-0239-0313-s004107 | reverse | revenue | 2 | pending |
| line-4 | line-4-0372-0375-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0287-0389-s001943 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**20 trainsets exceed the reference platform envelope**, requiring **980.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0318-0258-s008262 | 2 | 2 | 0 | 0.0 |
| line-1-0348-0359-s004928 | 6 | 4 | 2 | 98.0 |
| line-1-0373-0375-s004146 | 6 | 4 | 2 | 98.0 |
| line-1-0530-0342-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0210-0463-s011616 | 3 | 2 | 1 | 49.0 |
| line-2-0278-0389-s009094 | 6 | 4 | 2 | 98.0 |
| line-2-0287-0389-s008914 | 6 | 4 | 2 | 98.0 |
| line-2-0525-0424-s003010 | 6 | 2 | 4 | 196.0 |
| line-2-0644-0475-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0330-0343-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0348-0359-s000613 | 5 | 4 | 1 | 49.0 |
| line-3-0373-0375-s001395 | 4 | 4 | 0 | 0.0 |
| line-3-0454-0260-s004722 | 2 | 2 | 0 | 0.0 |
| line-4-0239-0313-s004107 | 2 | 2 | 0 | 0.0 |
| line-4-0278-0389-s002123 | 4 | 4 | 0 | 0.0 |
| line-4-0287-0389-s001943 | 5 | 4 | 1 | 49.0 |
| line-4-0372-0375-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Garissa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
