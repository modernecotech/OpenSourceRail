# Station and depot overnight allocation

Plan: **32 trainsets at stations + 68 at depots = 100 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0461-0724-s016691 | 68 | 4,046.0 | 15 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0461-0724-s016691 | station | reverse | revenue | 2 |
| line-1 | line-1-0499-0632-s014484 | station | forward | revenue | 1 |
| line-1 | line-1-0499-0632-s014484 | station | reverse | revenue | 1 |
| line-1 | line-1-0552-0549-s012289 | station | forward | revenue | 1 |
| line-1 | line-1-0552-0549-s012289 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0491-s010018 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0491-s010018 | station | reverse | revenue | 1 |
| line-1 | line-1-0738-0445-s007010 | station | forward | revenue | 1 |
| line-1 | line-1-0738-0445-s007010 | station | reverse | revenue | 1 |
| line-1 | line-1-0962-0331-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0153-0365-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0412-0470-s007015 | station | forward | revenue | 1 |
| line-2 | line-2-0412-0470-s007015 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0549-s010701 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0549-s010701 | station | reverse | revenue | 1 |
| line-2 | line-2-0573-0608-s012786 | station | forward | revenue | 1 |
| line-2 | line-2-0573-0608-s012786 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0693-s014879 | station | reverse | revenue | 2 |
| line-3 | line-3-0547-0439-s013275 | station | reverse | revenue | 2 |
| line-3 | line-3-0552-0549-s010188 | station | forward | revenue | 1 |
| line-3 | line-3-0552-0549-s010188 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0626-s008548 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0626-s008548 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0720-s005541 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0720-s005541 | station | reverse | revenue | 1 |
| line-3 | line-3-0662-0893-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0461-0724-s016691 | depot | — | revenue | 21 |
| line-1 | line-1-0461-0724-s016691 | depot | — | spare | 3 |
| line-1 | line-1-0461-0724-s016691 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0461-0724-s016691 | depot | — | revenue | 20 |
| line-2 | line-1-0461-0724-s016691 | depot | — | spare | 3 |
| line-2 | line-1-0461-0724-s016691 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0461-0724-s016691 | depot | — | revenue | 16 |
| line-3 | line-1-0461-0724-s016691 | depot | — | spare | 2 |
| line-3 | line-1-0461-0724-s016691 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (24 trains), line-3 (19 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **100 trainsets at 16 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **89 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0962-0331-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0738-0445-s007010 | forward | revenue | 4 | pending |
| line-1 | line-1-0738-0445-s007010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0612-0491-s010018 | forward | revenue | 3 | pending |
| line-1 | line-1-0612-0491-s010018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0552-0549-s012289 | forward | revenue | 3 | pending |
| line-1 | line-1-0552-0549-s012289 | reverse | revenue | 3 | pending |
| line-1 | line-1-0499-0632-s014484 | forward | revenue | 3 | pending |
| line-1 | line-1-0499-0632-s014484 | reverse | revenue | 3 | pending |
| line-1 | line-1-0461-0724-s016691 | reverse | revenue | 3 | pending |
| line-1 | line-1-0612-0491-s010018 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0491-s010018 | reverse | spare | 1 | pending |
| line-1 | line-1-0552-0549-s012289 | forward | spare | 1 | pending |
| line-1 | line-1-0552-0549-s012289 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0153-0365-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0412-0470-s007015 | forward | revenue | 4 | pending |
| line-2 | line-2-0412-0470-s007015 | reverse | revenue | 4 | pending |
| line-2 | line-2-0552-0549-s010701 | forward | revenue | 4 | pending |
| line-2 | line-2-0552-0549-s010701 | reverse | revenue | 4 | pending |
| line-2 | line-2-0573-0608-s012786 | forward | revenue | 4 | pending |
| line-2 | line-2-0573-0608-s012786 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0693-s014879 | reverse | revenue | 3 | pending |
| line-2 | line-2-0573-0608-s012786 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0693-s014879 | reverse | spare | 1 | pending |
| line-2 | line-2-0153-0365-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0412-0470-s007015 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0662-0893-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0590-0720-s005541 | forward | revenue | 4 | pending |
| line-3 | line-3-0590-0720-s005541 | reverse | revenue | 3 | pending |
| line-3 | line-3-0554-0626-s008548 | forward | revenue | 3 | pending |
| line-3 | line-3-0554-0626-s008548 | reverse | revenue | 3 | pending |
| line-3 | line-3-0552-0549-s010188 | forward | revenue | 3 | pending |
| line-3 | line-3-0552-0549-s010188 | reverse | revenue | 3 | pending |
| line-3 | line-3-0547-0439-s013275 | reverse | revenue | 3 | pending |
| line-3 | line-3-0590-0720-s005541 | reverse | spare | 1 | pending |
| line-3 | line-3-0554-0626-s008548 | forward | spare | 1 | pending |
| line-3 | line-3-0554-0626-s008548 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**58 trainsets exceed the reference platform envelope**, requiring **3,451.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0461-0724-s016691 | 3 | 2 | 1 | 59.5 |
| line-1-0499-0632-s014484 | 6 | 2 | 4 | 238.0 |
| line-1-0552-0549-s012289 | 8 | 4 | 4 | 238.0 |
| line-1-0612-0491-s010018 | 8 | 2 | 6 | 357.0 |
| line-1-0738-0445-s007010 | 8 | 2 | 6 | 357.0 |
| line-1-0962-0331-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0153-0365-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0412-0470-s007015 | 9 | 2 | 7 | 416.5 |
| line-2-0552-0549-s010701 | 8 | 4 | 4 | 238.0 |
| line-2-0573-0608-s012786 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0693-s014879 | 4 | 2 | 2 | 119.0 |
| line-3-0547-0439-s013275 | 3 | 2 | 1 | 59.5 |
| line-3-0552-0549-s010188 | 6 | 4 | 2 | 119.0 |
| line-3-0554-0626-s008548 | 8 | 4 | 4 | 238.0 |
| line-3-0590-0720-s005541 | 8 | 2 | 6 | 357.0 |
| line-3-0662-0893-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Bahawalpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
