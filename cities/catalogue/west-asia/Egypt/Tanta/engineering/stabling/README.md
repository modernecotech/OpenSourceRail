# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 180 at depots = 218 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0334-0571-s000000 | line-1 | declared-depot | 35 | 2,082.5 | 7 |
| line-2-0222-0124-s000000 | line-2 | declared-depot | 70 | 4,165.0 | 12 |
| line-3-0068-0951-s028372 | line-3 | declared-depot | 75 | 4,462.5 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0334-0571-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0458-0515-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0458-0515-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0507-0492-s004208 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0492-s004208 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0458-s006013 | station | forward | revenue | 1 |
| line-1 | line-1-0582-0458-s006013 | station | reverse | revenue | 1 |
| line-1 | line-1-0706-0402-s009004 | station | forward | revenue | 1 |
| line-1 | line-1-0706-0402-s009004 | station | reverse | revenue | 1 |
| line-1 | line-1-0950-0251-s015264 | station | reverse | revenue | 2 |
| line-2 | line-2-0222-0124-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0405-0352-s007013 | station | forward | revenue | 1 |
| line-2 | line-2-0405-0352-s007013 | station | reverse | revenue | 1 |
| line-2 | line-2-0507-0492-s010869 | station | forward | revenue | 1 |
| line-2 | line-2-0507-0492-s010869 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0545-s012334 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0545-s012334 | station | reverse | revenue | 1 |
| line-2 | line-2-0597-0615-s014262 | station | forward | revenue | 1 |
| line-2 | line-2-0597-0615-s014262 | station | reverse | revenue | 1 |
| line-2 | line-2-0648-0683-s016209 | station | forward | revenue | 1 |
| line-2 | line-2-0648-0683-s016209 | station | reverse | revenue | 1 |
| line-2 | line-2-0853-1088-s027026 | station | reverse | revenue | 2 |
| line-3 | line-3-0068-0951-s028372 | station | reverse | revenue | 2 |
| line-3 | line-3-0448-0633-s017048 | station | forward | revenue | 1 |
| line-3 | line-3-0448-0633-s017048 | station | reverse | revenue | 1 |
| line-3 | line-3-0546-0546-s014110 | station | forward | revenue | 1 |
| line-3 | line-3-0546-0546-s014110 | station | reverse | revenue | 1 |
| line-3 | line-3-0648-0454-s011026 | station | forward | revenue | 1 |
| line-3 | line-3-0648-0454-s011026 | station | reverse | revenue | 1 |
| line-3 | line-3-0706-0402-s009283 | station | forward | revenue | 1 |
| line-3 | line-3-0706-0402-s009283 | station | reverse | revenue | 1 |
| line-3 | line-3-1031-0151-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0334-0571-s000000 | depot | — | revenue | 30 |
| line-1 | line-1-0334-0571-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0334-0571-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0222-0124-s000000 | depot | — | revenue | 62 |
| line-2 | line-2-0222-0124-s000000 | depot | — | spare | 7 |
| line-2 | line-2-0222-0124-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0068-0951-s028372 | depot | — | revenue | 67 |
| line-3 | line-3-0068-0951-s028372 | depot | — | spare | 7 |
| line-3 | line-3-0068-0951-s028372 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tanta-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **218 trainsets at 19 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **197 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **180 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0334-0571-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0458-0515-s003002 | forward | revenue | 5 | pending |
| line-1 | line-1-0458-0515-s003002 | reverse | revenue | 4 | pending |
| line-1 | line-1-0507-0492-s004208 | forward | revenue | 4 | pending |
| line-1 | line-1-0507-0492-s004208 | reverse | revenue | 4 | pending |
| line-1 | line-1-0582-0458-s006013 | forward | revenue | 4 | pending |
| line-1 | line-1-0582-0458-s006013 | reverse | revenue | 4 | pending |
| line-1 | line-1-0706-0402-s009004 | forward | revenue | 4 | pending |
| line-1 | line-1-0706-0402-s009004 | reverse | revenue | 4 | pending |
| line-1 | line-1-0950-0251-s015264 | reverse | revenue | 4 | pending |
| line-1 | line-1-0458-0515-s003002 | reverse | spare | 1 | pending |
| line-1 | line-1-0507-0492-s004208 | forward | spare | 1 | pending |
| line-1 | line-1-0507-0492-s004208 | reverse | spare | 1 | pending |
| line-1 | line-1-0582-0458-s006013 | forward | spare | 1 | pending |
| line-1 | line-1-0582-0458-s006013 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0405-0352-s007013 | forward | revenue | 7 | pending |
| line-2 | line-2-0405-0352-s007013 | reverse | revenue | 7 | pending |
| line-2 | line-2-0507-0492-s010869 | forward | revenue | 7 | pending |
| line-2 | line-2-0507-0492-s010869 | reverse | revenue | 6 | pending |
| line-2 | line-2-0546-0545-s012334 | forward | revenue | 6 | pending |
| line-2 | line-2-0546-0545-s012334 | reverse | revenue | 6 | pending |
| line-2 | line-2-0597-0615-s014262 | forward | revenue | 6 | pending |
| line-2 | line-2-0597-0615-s014262 | reverse | revenue | 6 | pending |
| line-2 | line-2-0648-0683-s016209 | forward | revenue | 6 | pending |
| line-2 | line-2-0648-0683-s016209 | reverse | revenue | 6 | pending |
| line-2 | line-2-0853-1088-s027026 | reverse | revenue | 6 | pending |
| line-2 | line-2-0507-0492-s010869 | reverse | spare | 1 | pending |
| line-2 | line-2-0546-0545-s012334 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0545-s012334 | reverse | spare | 1 | pending |
| line-2 | line-2-0597-0615-s014262 | forward | spare | 1 | pending |
| line-2 | line-2-0597-0615-s014262 | reverse | spare | 1 | pending |
| line-2 | line-2-0648-0683-s016209 | forward | spare | 1 | pending |
| line-2 | line-2-0648-0683-s016209 | reverse | spare | 1 | pending |
| line-2 | line-2-0853-1088-s027026 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0706-0402-s009283 | forward | revenue | 8 | pending |
| line-3 | line-3-0706-0402-s009283 | reverse | revenue | 8 | pending |
| line-3 | line-3-0648-0454-s011026 | forward | revenue | 8 | pending |
| line-3 | line-3-0648-0454-s011026 | reverse | revenue | 8 | pending |
| line-3 | line-3-0546-0546-s014110 | forward | revenue | 8 | pending |
| line-3 | line-3-0546-0546-s014110 | reverse | revenue | 8 | pending |
| line-3 | line-3-0448-0633-s017048 | forward | revenue | 8 | pending |
| line-3 | line-3-0448-0633-s017048 | reverse | revenue | 8 | pending |
| line-3 | line-3-0068-0951-s028372 | reverse | revenue | 7 | pending |
| line-3 | line-3-0068-0951-s028372 | reverse | spare | 1 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0706-0402-s009283 | forward | spare | 1 | pending |
| line-3 | line-3-0706-0402-s009283 | reverse | spare | 1 | pending |
| line-3 | line-3-0648-0454-s011026 | forward | spare | 1 | pending |
| line-3 | line-3-0648-0454-s011026 | reverse | spare | 1 | pending |
| line-3 | line-3-0546-0546-s014110 | forward | spare | 1 | pending |
| line-3 | line-3-0546-0546-s014110 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**168 trainsets exceed the reference platform envelope**, requiring **9,996.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0334-0571-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0458-0515-s003002 | 10 | 2 | 8 | 476.0 |
| line-1-0507-0492-s004208 | 10 | 4 | 6 | 357.0 |
| line-1-0582-0458-s006013 | 10 | 2 | 8 | 476.0 |
| line-1-0706-0402-s009004 | 8 | 4 | 4 | 238.0 |
| line-1-0950-0251-s015264 | 4 | 2 | 2 | 119.0 |
| line-2-0222-0124-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0405-0352-s007013 | 14 | 2 | 12 | 714.0 |
| line-2-0507-0492-s010869 | 14 | 4 | 10 | 595.0 |
| line-2-0546-0545-s012334 | 14 | 4 | 10 | 595.0 |
| line-2-0597-0615-s014262 | 14 | 2 | 12 | 714.0 |
| line-2-0648-0683-s016209 | 14 | 2 | 12 | 714.0 |
| line-2-0853-1088-s027026 | 7 | 2 | 5 | 297.5 |
| line-3-0068-0951-s028372 | 8 | 2 | 6 | 357.0 |
| line-3-0448-0633-s017048 | 16 | 2 | 14 | 833.0 |
| line-3-0546-0546-s014110 | 18 | 4 | 14 | 833.0 |
| line-3-0648-0454-s011026 | 18 | 2 | 16 | 952.0 |
| line-3-0706-0402-s009283 | 18 | 4 | 14 | 833.0 |
| line-3-1031-0151-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Tanta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
