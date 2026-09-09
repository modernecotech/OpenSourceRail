# Station and depot overnight allocation

Plan: **30 trainsets at stations + 46 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0420-0164-s014918 | 46 | 2,254.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0166-s012218 | station | reverse | revenue | 2 |
| line-1 | line-1-0386-0374-s006745 | station | forward | revenue | 1 |
| line-1 | line-1-0386-0374-s006745 | station | reverse | revenue | 1 |
| line-1 | line-1-0453-0393-s004609 | station | forward | revenue | 1 |
| line-1 | line-1-0453-0393-s004609 | station | reverse | revenue | 1 |
| line-1 | line-1-0499-0419-s003000 | station | forward | revenue | 1 |
| line-1 | line-1-0499-0419-s003000 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0491-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0386-0374-s002060 | station | forward | revenue | 1 |
| line-2 | line-2-0386-0374-s002060 | station | reverse | revenue | 1 |
| line-2 | line-2-0404-0455-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0471-0361-s004610 | station | forward | revenue | 1 |
| line-2 | line-2-0471-0361-s004610 | station | reverse | revenue | 1 |
| line-2 | line-2-0557-0335-s006890 | station | forward | revenue | 1 |
| line-2 | line-2-0557-0335-s006890 | station | reverse | revenue | 1 |
| line-2 | line-2-0638-0268-s009152 | station | reverse | revenue | 2 |
| line-3 | line-3-0386-0374-s010437 | station | forward | revenue | 1 |
| line-3 | line-3-0386-0374-s010437 | station | reverse | revenue | 1 |
| line-3 | line-3-0412-0273-s012672 | station | forward | revenue | 1 |
| line-3 | line-3-0412-0273-s012672 | station | reverse | revenue | 1 |
| line-3 | line-3-0420-0164-s014918 | station | reverse | revenue | 2 |
| line-3 | line-3-0428-0477-s006804 | station | forward | revenue | 1 |
| line-3 | line-3-0428-0477-s006804 | station | reverse | revenue | 1 |
| line-3 | line-3-0536-0748-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0420-0164-s014918 | depot | — | revenue | 13 |
| line-1 | line-3-0420-0164-s014918 | depot | — | spare | 2 |
| line-1 | line-3-0420-0164-s014918 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0420-0164-s014918 | depot | — | revenue | 8 |
| line-2 | line-3-0420-0164-s014918 | depot | — | spare | 1 |
| line-2 | line-3-0420-0164-s014918 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0420-0164-s014918 | depot | — | revenue | 17 |
| line-3 | line-3-0420-0164-s014918 | depot | — | spare | 2 |
| line-3 | line-3-0420-0164-s014918 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (16 trains), line-2 (10 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0565-0491-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0499-0419-s003000 | forward | revenue | 3 | pending |
| line-1 | line-1-0499-0419-s003000 | reverse | revenue | 3 | pending |
| line-1 | line-1-0453-0393-s004609 | forward | revenue | 3 | pending |
| line-1 | line-1-0453-0393-s004609 | reverse | revenue | 3 | pending |
| line-1 | line-1-0386-0374-s006745 | forward | revenue | 3 | pending |
| line-1 | line-1-0386-0374-s006745 | reverse | revenue | 3 | pending |
| line-1 | line-1-0297-0166-s012218 | reverse | revenue | 2 | pending |
| line-1 | line-1-0297-0166-s012218 | reverse | spare | 1 | pending |
| line-1 | line-1-0565-0491-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0499-0419-s003000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0404-0455-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0386-0374-s002060 | forward | revenue | 3 | pending |
| line-2 | line-2-0386-0374-s002060 | reverse | revenue | 2 | pending |
| line-2 | line-2-0471-0361-s004610 | forward | revenue | 2 | pending |
| line-2 | line-2-0471-0361-s004610 | reverse | revenue | 2 | pending |
| line-2 | line-2-0557-0335-s006890 | forward | revenue | 2 | pending |
| line-2 | line-2-0557-0335-s006890 | reverse | revenue | 2 | pending |
| line-2 | line-2-0638-0268-s009152 | reverse | revenue | 2 | pending |
| line-2 | line-2-0386-0374-s002060 | reverse | spare | 1 | pending |
| line-2 | line-2-0471-0361-s004610 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0536-0748-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0428-0477-s006804 | forward | revenue | 4 | pending |
| line-3 | line-3-0428-0477-s006804 | reverse | revenue | 4 | pending |
| line-3 | line-3-0386-0374-s010437 | forward | revenue | 3 | pending |
| line-3 | line-3-0386-0374-s010437 | reverse | revenue | 3 | pending |
| line-3 | line-3-0412-0273-s012672 | forward | revenue | 3 | pending |
| line-3 | line-3-0412-0273-s012672 | reverse | revenue | 3 | pending |
| line-3 | line-3-0420-0164-s014918 | reverse | revenue | 3 | pending |
| line-3 | line-3-0386-0374-s010437 | forward | spare | 1 | pending |
| line-3 | line-3-0386-0374-s010437 | reverse | spare | 1 | pending |
| line-3 | line-3-0412-0273-s012672 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **1,960.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0166-s012218 | 3 | 2 | 1 | 49.0 |
| line-1-0386-0374-s006745 | 6 | 4 | 2 | 98.0 |
| line-1-0453-0393-s004609 | 6 | 2 | 4 | 196.0 |
| line-1-0499-0419-s003000 | 7 | 2 | 5 | 245.0 |
| line-1-0565-0491-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0386-0374-s002060 | 6 | 4 | 2 | 98.0 |
| line-2-0404-0455-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0471-0361-s004610 | 5 | 2 | 3 | 147.0 |
| line-2-0557-0335-s006890 | 4 | 2 | 2 | 98.0 |
| line-2-0638-0268-s009152 | 2 | 2 | 0 | 0.0 |
| line-3-0386-0374-s010437 | 8 | 4 | 4 | 196.0 |
| line-3-0412-0273-s012672 | 7 | 2 | 5 | 245.0 |
| line-3-0420-0164-s014918 | 3 | 2 | 1 | 49.0 |
| line-3-0428-0477-s006804 | 8 | 2 | 6 | 294.0 |
| line-3-0536-0748-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Fort-Portal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
