# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 8 at depots = 46 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0319-0148-s000000 | line-1 | declared-depot | 3 | 147.0 | 3 |
| line-2-0593-0351-s000000 | line-2 | declared-depot | 2 | 98.0 | 2 |
| line-3-0744-0445-s010159 | line-3 | declared-depot | 3 | 147.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0319-0148-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0531-0372-s006916 | station | reverse | revenue | 2 |
| line-1 | line-1-planning-infill-s001383 | station | forward | revenue | 1 |
| line-1 | line-1-planning-infill-s001383 | station | reverse | revenue | 1 |
| line-1 | line-1-planning-infill-s002766 | station | forward | revenue | 1 |
| line-1 | line-1-planning-infill-s002766 | station | reverse | revenue | 1 |
| line-1 | line-1-planning-infill-s004149 | station | forward | revenue | 1 |
| line-1 | line-1-planning-infill-s004149 | station | reverse | revenue | 1 |
| line-1 | line-1-planning-infill-s005533 | station | forward | revenue | 1 |
| line-1 | line-1-planning-infill-s005533 | station | reverse | revenue | 1 |
| line-2 | line-2-0474-0480-s003906 | station | reverse | revenue | 2 |
| line-2 | line-2-0593-0351-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-planning-infill-s001302 | station | forward | revenue | 1 |
| line-2 | line-2-planning-infill-s001302 | station | reverse | revenue | 1 |
| line-2 | line-2-planning-infill-s002604 | station | forward | revenue | 1 |
| line-2 | line-2-planning-infill-s002604 | station | reverse | revenue | 1 |
| line-3 | line-3-0340-0286-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0497-0346-s003684 | station | forward | revenue | 1 |
| line-3 | line-3-0497-0346-s003684 | station | reverse | revenue | 1 |
| line-3 | line-3-0744-0445-s010159 | station | reverse | revenue | 2 |
| line-3 | line-3-planning-infill-s001228 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s001228 | station | reverse | revenue | 1 |
| line-3 | line-3-planning-infill-s002456 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s002456 | station | reverse | revenue | 1 |
| line-3 | line-3-planning-infill-s004979 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s004979 | station | reverse | revenue | 1 |
| line-3 | line-3-planning-infill-s006274 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s006274 | station | reverse | revenue | 1 |
| line-3 | line-3-planning-infill-s007569 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s007569 | station | reverse | revenue | 1 |
| line-3 | line-3-planning-infill-s008864 | station | forward | revenue | 1 |
| line-3 | line-3-planning-infill-s008864 | station | reverse | revenue | 1 |
| line-1 | line-1-0319-0148-s000000 | depot | — | revenue | 1 |
| line-1 | line-1-0319-0148-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0319-0148-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0593-0351-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0593-0351-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0744-0445-s010159 | depot | — | revenue | 1 |
| line-3 | line-3-0744-0445-s010159 | depot | — | spare | 1 |
| line-3 | line-3-0744-0445-s010159 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/soyo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **46 trainsets at 19 stations**; largest initial station queue **4**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **40 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **8 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **6 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0319-0148-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-planning-infill-s001383 | forward | revenue | 2 | pending |
| line-1 | line-1-planning-infill-s001383 | reverse | revenue | 2 | pending |
| line-1 | line-1-planning-infill-s002766 | forward | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s002766 | reverse | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s004149 | forward | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s004149 | reverse | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s005533 | forward | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s005533 | reverse | revenue | 1 | pending |
| line-1 | line-1-0531-0372-s006916 | reverse | revenue | 1 | pending |
| line-1 | line-1-planning-infill-s002766 | forward | spare | 1 | pending |
| line-1 | line-1-planning-infill-s002766 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0593-0351-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-planning-infill-s001302 | forward | revenue | 2 | pending |
| line-2 | line-2-planning-infill-s001302 | reverse | revenue | 1 | pending |
| line-2 | line-2-planning-infill-s002604 | forward | revenue | 1 | pending |
| line-2 | line-2-planning-infill-s002604 | reverse | revenue | 1 | pending |
| line-2 | line-2-0474-0480-s003906 | reverse | revenue | 1 | pending |
| line-2 | line-2-planning-infill-s001302 | reverse | spare | 1 | pending |
| line-2 | line-2-planning-infill-s002604 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-planning-infill-s001228 | forward | revenue | 2 | pending |
| line-3 | line-3-planning-infill-s001228 | reverse | revenue | 2 | pending |
| line-3 | line-3-planning-infill-s002456 | forward | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s002456 | reverse | revenue | 1 | pending |
| line-3 | line-3-0497-0346-s003684 | forward | revenue | 1 | pending |
| line-3 | line-3-0497-0346-s003684 | reverse | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s004979 | forward | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s004979 | reverse | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s006274 | forward | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s006274 | reverse | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s007569 | forward | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s007569 | reverse | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s008864 | forward | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s008864 | reverse | revenue | 1 | pending |
| line-3 | line-3-0744-0445-s010159 | reverse | revenue | 1 | pending |
| line-3 | line-3-planning-infill-s002456 | forward | spare | 1 | pending |
| line-3 | line-3-planning-infill-s002456 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**9 trainsets exceed the reference platform envelope**, requiring **441.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0319-0148-s000000 | 2 | 2 | 0 | 0.0 |
| line-1-0531-0372-s006916 | 1 | 2 | 0 | 0.0 |
| line-1-planning-infill-s001383 | 4 | 2 | 2 | 98.0 |
| line-1-planning-infill-s002766 | 4 | 2 | 2 | 98.0 |
| line-1-planning-infill-s004149 | 2 | 2 | 0 | 0.0 |
| line-1-planning-infill-s005533 | 2 | 4 | 0 | 0.0 |
| line-2-0474-0480-s003906 | 1 | 2 | 0 | 0.0 |
| line-2-0593-0351-s000000 | 2 | 2 | 0 | 0.0 |
| line-2-planning-infill-s001302 | 4 | 4 | 0 | 0.0 |
| line-2-planning-infill-s002604 | 3 | 2 | 1 | 49.0 |
| line-3-0340-0286-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0497-0346-s003684 | 2 | 4 | 0 | 0.0 |
| line-3-0744-0445-s010159 | 1 | 2 | 0 | 0.0 |
| line-3-planning-infill-s001228 | 4 | 2 | 2 | 98.0 |
| line-3-planning-infill-s002456 | 4 | 2 | 2 | 98.0 |
| line-3-planning-infill-s004979 | 2 | 4 | 0 | 0.0 |
| line-3-planning-infill-s006274 | 2 | 2 | 0 | 0.0 |
| line-3-planning-infill-s007569 | 2 | 2 | 0 | 0.0 |
| line-3-planning-infill-s008864 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Soyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
