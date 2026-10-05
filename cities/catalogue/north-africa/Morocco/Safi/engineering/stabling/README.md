# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 83 at depots = 111 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0400-0426-s017961 | line-1 | declared-depot | 47 | 2,796.5 | 8 |
| line-2-0398-0611-s000000 | line-2 | declared-depot | 18 | 1,071.0 | 4 |
| line-3-0543-0652-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-0426-s017961 | station | reverse | revenue | 2 |
| line-1 | line-1-0465-0496-s015799 | station | forward | revenue | 1 |
| line-1 | line-1-0465-0496-s015799 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0568-s013617 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0568-s013617 | station | reverse | revenue | 1 |
| line-1 | line-1-0640-0686-s010023 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0686-s010023 | station | reverse | revenue | 1 |
| line-1 | line-1-0929-1021-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0398-0611-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0489-0582-s002095 | station | forward | revenue | 1 |
| line-2 | line-2-0489-0582-s002095 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0560-s003629 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0560-s003629 | station | reverse | revenue | 1 |
| line-2 | line-2-0659-0527-s005974 | station | forward | revenue | 1 |
| line-2 | line-2-0659-0527-s005974 | station | reverse | revenue | 1 |
| line-2 | line-2-0760-0495-s008295 | station | reverse | revenue | 2 |
| line-3 | line-3-0543-0652-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0658-0583-s003012 | station | forward | revenue | 1 |
| line-3 | line-3-0658-0583-s003012 | station | reverse | revenue | 1 |
| line-3 | line-3-0747-0529-s005322 | station | forward | revenue | 1 |
| line-3 | line-3-0747-0529-s005322 | station | reverse | revenue | 1 |
| line-3 | line-3-0835-0476-s007626 | station | reverse | revenue | 2 |
| line-1 | line-1-0400-0426-s017961 | depot | — | revenue | 41 |
| line-1 | line-1-0400-0426-s017961 | depot | — | spare | 5 |
| line-1 | line-1-0400-0426-s017961 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0398-0611-s000000 | depot | — | revenue | 15 |
| line-2 | line-2-0398-0611-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0398-0611-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0543-0652-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0543-0652-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0543-0652-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/safi-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **111 trainsets at 14 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **99 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **83 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0929-1021-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0640-0686-s010023 | forward | revenue | 7 | pending |
| line-1 | line-1-0640-0686-s010023 | reverse | revenue | 7 | pending |
| line-1 | line-1-0532-0568-s013617 | forward | revenue | 6 | pending |
| line-1 | line-1-0532-0568-s013617 | reverse | revenue | 6 | pending |
| line-1 | line-1-0465-0496-s015799 | forward | revenue | 6 | pending |
| line-1 | line-1-0465-0496-s015799 | reverse | revenue | 6 | pending |
| line-1 | line-1-0400-0426-s017961 | reverse | revenue | 6 | pending |
| line-1 | line-1-0532-0568-s013617 | forward | spare | 1 | pending |
| line-1 | line-1-0532-0568-s013617 | reverse | spare | 1 | pending |
| line-1 | line-1-0465-0496-s015799 | forward | spare | 1 | pending |
| line-1 | line-1-0465-0496-s015799 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-0426-s017961 | reverse | spare | 1 | pending |
| line-1 | line-1-0929-1021-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0398-0611-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0489-0582-s002095 | forward | revenue | 3 | pending |
| line-2 | line-2-0489-0582-s002095 | reverse | revenue | 3 | pending |
| line-2 | line-2-0556-0560-s003629 | forward | revenue | 3 | pending |
| line-2 | line-2-0556-0560-s003629 | reverse | revenue | 3 | pending |
| line-2 | line-2-0659-0527-s005974 | forward | revenue | 3 | pending |
| line-2 | line-2-0659-0527-s005974 | reverse | revenue | 3 | pending |
| line-2 | line-2-0760-0495-s008295 | reverse | revenue | 3 | pending |
| line-2 | line-2-0489-0582-s002095 | forward | spare | 1 | pending |
| line-2 | line-2-0489-0582-s002095 | reverse | spare | 1 | pending |
| line-2 | line-2-0556-0560-s003629 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0658-0583-s003012 | forward | revenue | 4 | pending |
| line-3 | line-3-0658-0583-s003012 | reverse | revenue | 4 | pending |
| line-3 | line-3-0747-0529-s005322 | forward | revenue | 4 | pending |
| line-3 | line-3-0747-0529-s005322 | reverse | revenue | 4 | pending |
| line-3 | line-3-0835-0476-s007626 | reverse | revenue | 3 | pending |
| line-3 | line-3-0835-0476-s007626 | reverse | spare | 1 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0658-0583-s003012 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**79 trainsets exceed the reference platform envelope**, requiring **4,700.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-0426-s017961 | 7 | 2 | 5 | 297.5 |
| line-1-0465-0496-s015799 | 14 | 2 | 12 | 714.0 |
| line-1-0532-0568-s013617 | 14 | 4 | 10 | 595.0 |
| line-1-0640-0686-s010023 | 14 | 2 | 12 | 714.0 |
| line-1-0929-1021-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0398-0611-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0489-0582-s002095 | 8 | 2 | 6 | 357.0 |
| line-2-0556-0560-s003629 | 7 | 4 | 3 | 178.5 |
| line-2-0659-0527-s005974 | 6 | 2 | 4 | 238.0 |
| line-2-0760-0495-s008295 | 3 | 2 | 1 | 59.5 |
| line-3-0543-0652-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0658-0583-s003012 | 9 | 2 | 7 | 416.5 |
| line-3-0747-0529-s005322 | 8 | 2 | 6 | 357.0 |
| line-3-0835-0476-s007626 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Safi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
