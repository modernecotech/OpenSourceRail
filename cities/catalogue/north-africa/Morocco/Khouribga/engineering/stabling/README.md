# Station and depot overnight allocation

Plan: **22 trainsets at stations + 24 at depots = 46 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0341-0544-s008892 | 24 | 1,176.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0341-0544-s008892 | station | reverse | revenue | 2 |
| line-1 | line-1-0377-0372-s004935 | station | forward | revenue | 1 |
| line-1 | line-1-0377-0372-s004935 | station | reverse | revenue | 1 |
| line-1 | line-1-0447-0347-s003008 | station | forward | revenue | 1 |
| line-1 | line-1-0447-0347-s003008 | station | reverse | revenue | 1 |
| line-1 | line-1-0558-0329-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0302-0386-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0377-0372-s001673 | station | forward | revenue | 1 |
| line-2 | line-2-0377-0372-s001673 | station | reverse | revenue | 1 |
| line-2 | line-2-0413-0308-s003686 | station | forward | revenue | 1 |
| line-2 | line-2-0413-0308-s003686 | station | reverse | revenue | 1 |
| line-2 | line-2-0494-0268-s005704 | station | reverse | revenue | 2 |
| line-3 | line-3-0310-0321-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0377-0372-s002060 | station | forward | revenue | 1 |
| line-3 | line-3-0377-0372-s002060 | station | reverse | revenue | 1 |
| line-3 | line-3-0463-0383-s004176 | station | reverse | revenue | 2 |
| line-1 | line-1-0341-0544-s008892 | depot | — | revenue | 9 |
| line-1 | line-1-0341-0544-s008892 | depot | — | spare | 1 |
| line-1 | line-1-0341-0544-s008892 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0341-0544-s008892 | depot | — | revenue | 5 |
| line-2 | line-1-0341-0544-s008892 | depot | — | spare | 1 |
| line-2 | line-1-0341-0544-s008892 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0341-0544-s008892 | depot | — | revenue | 4 |
| line-3 | line-1-0341-0544-s008892 | depot | — | spare | 1 |
| line-3 | line-1-0341-0544-s008892 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (7 trains), line-3 (6 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **46 trainsets at 11 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **40 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **24 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0558-0329-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0447-0347-s003008 | forward | revenue | 3 | pending |
| line-1 | line-1-0447-0347-s003008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0377-0372-s004935 | forward | revenue | 3 | pending |
| line-1 | line-1-0377-0372-s004935 | reverse | revenue | 3 | pending |
| line-1 | line-1-0341-0544-s008892 | reverse | revenue | 2 | pending |
| line-1 | line-1-0341-0544-s008892 | reverse | spare | 1 | pending |
| line-1 | line-1-0558-0329-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0302-0386-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0377-0372-s001673 | forward | revenue | 2 | pending |
| line-2 | line-2-0377-0372-s001673 | reverse | revenue | 2 | pending |
| line-2 | line-2-0413-0308-s003686 | forward | revenue | 2 | pending |
| line-2 | line-2-0413-0308-s003686 | reverse | revenue | 2 | pending |
| line-2 | line-2-0494-0268-s005704 | reverse | revenue | 2 | pending |
| line-2 | line-2-0377-0372-s001673 | forward | spare | 1 | pending |
| line-2 | line-2-0377-0372-s001673 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0310-0321-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0377-0372-s002060 | forward | revenue | 3 | pending |
| line-3 | line-3-0377-0372-s002060 | reverse | revenue | 2 | pending |
| line-3 | line-3-0463-0383-s004176 | reverse | revenue | 2 | pending |
| line-3 | line-3-0377-0372-s002060 | reverse | spare | 1 | pending |
| line-3 | line-3-0463-0383-s004176 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**18 trainsets exceed the reference platform envelope**, requiring **882.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0341-0544-s008892 | 3 | 2 | 1 | 49.0 |
| line-1-0377-0372-s004935 | 6 | 4 | 2 | 98.0 |
| line-1-0447-0347-s003008 | 6 | 2 | 4 | 196.0 |
| line-1-0558-0329-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0302-0386-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0377-0372-s001673 | 6 | 4 | 2 | 98.0 |
| line-2-0413-0308-s003686 | 4 | 2 | 2 | 98.0 |
| line-2-0494-0268-s005704 | 2 | 2 | 0 | 0.0 |
| line-3-0310-0321-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0377-0372-s002060 | 6 | 4 | 2 | 98.0 |
| line-3-0463-0383-s004176 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Khouribga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
