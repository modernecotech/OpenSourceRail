# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 104 at depots = 142 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0748-0658-s017846 | line-1 | declared-depot | 43 | 2,558.5 | 9 |
| line-2-0532-0204-s000000 | line-2 | declared-depot | 26 | 1,547.0 | 6 |
| line-3-0868-0951-s000000 | line-3 | declared-depot | 35 | 2,082.5 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0015-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0414-0292-s006740 | station | forward | revenue | 1 |
| line-1 | line-1-0414-0292-s006740 | station | reverse | revenue | 1 |
| line-1 | line-1-0472-0355-s008680 | station | forward | revenue | 1 |
| line-1 | line-1-0472-0355-s008680 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0420-s010633 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0420-s010633 | station | reverse | revenue | 1 |
| line-1 | line-1-0596-0491-s012778 | station | forward | revenue | 1 |
| line-1 | line-1-0596-0491-s012778 | station | reverse | revenue | 1 |
| line-1 | line-1-0670-0572-s015257 | station | forward | revenue | 1 |
| line-1 | line-1-0670-0572-s015257 | station | reverse | revenue | 1 |
| line-1 | line-1-0744-0654-s017721 | station | forward | revenue | 1 |
| line-1 | line-1-0744-0654-s017721 | station | reverse | revenue | 1 |
| line-1 | line-1-0748-0658-s017846 | station | reverse | revenue | 2 |
| line-2 | line-2-0524-0761-s011308 | station | reverse | revenue | 2 |
| line-2 | line-2-0526-0648-s009031 | station | forward | revenue | 1 |
| line-2 | line-2-0526-0648-s009031 | station | reverse | revenue | 1 |
| line-2 | line-2-0530-0506-s006158 | station | forward | revenue | 1 |
| line-2 | line-2-0530-0506-s006158 | station | reverse | revenue | 1 |
| line-2 | line-2-0531-0420-s004430 | station | forward | revenue | 1 |
| line-2 | line-2-0531-0420-s004430 | station | reverse | revenue | 1 |
| line-2 | line-2-0532-0204-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0533-0350-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0533-0350-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0616-0325-s014722 | station | reverse | revenue | 2 |
| line-3 | line-3-0649-0410-s012713 | station | forward | revenue | 1 |
| line-3 | line-3-0649-0410-s012713 | station | reverse | revenue | 1 |
| line-3 | line-3-0682-0495-s010716 | station | forward | revenue | 1 |
| line-3 | line-3-0682-0495-s010716 | station | reverse | revenue | 1 |
| line-3 | line-3-0744-0654-s006976 | station | forward | revenue | 1 |
| line-3 | line-3-0744-0654-s006976 | station | reverse | revenue | 1 |
| line-3 | line-3-0868-0951-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0748-0658-s017846 | depot | — | revenue | 37 |
| line-1 | line-1-0748-0658-s017846 | depot | — | spare | 5 |
| line-1 | line-1-0748-0658-s017846 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0532-0204-s000000 | depot | — | revenue | 22 |
| line-2 | line-2-0532-0204-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0532-0204-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0868-0951-s000000 | depot | — | revenue | 30 |
| line-3 | line-3-0868-0951-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0868-0951-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fallujah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **142 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **127 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **104 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0297-0015-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0414-0292-s006740 | forward | revenue | 4 | pending |
| line-1 | line-1-0414-0292-s006740 | reverse | revenue | 4 | pending |
| line-1 | line-1-0472-0355-s008680 | forward | revenue | 4 | pending |
| line-1 | line-1-0472-0355-s008680 | reverse | revenue | 4 | pending |
| line-1 | line-1-0531-0420-s010633 | forward | revenue | 4 | pending |
| line-1 | line-1-0531-0420-s010633 | reverse | revenue | 4 | pending |
| line-1 | line-1-0596-0491-s012778 | forward | revenue | 4 | pending |
| line-1 | line-1-0596-0491-s012778 | reverse | revenue | 4 | pending |
| line-1 | line-1-0670-0572-s015257 | forward | revenue | 4 | pending |
| line-1 | line-1-0670-0572-s015257 | reverse | revenue | 4 | pending |
| line-1 | line-1-0744-0654-s017721 | forward | revenue | 3 | pending |
| line-1 | line-1-0744-0654-s017721 | reverse | revenue | 3 | pending |
| line-1 | line-1-0748-0658-s017846 | reverse | revenue | 3 | pending |
| line-1 | line-1-0744-0654-s017721 | forward | spare | 1 | pending |
| line-1 | line-1-0744-0654-s017721 | reverse | spare | 1 | pending |
| line-1 | line-1-0748-0658-s017846 | reverse | spare | 1 | pending |
| line-1 | line-1-0297-0015-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0414-0292-s006740 | forward | spare | 1 | pending |
| line-1 | line-1-0414-0292-s006740 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0204-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0533-0350-s003013 | forward | revenue | 4 | pending |
| line-2 | line-2-0533-0350-s003013 | reverse | revenue | 4 | pending |
| line-2 | line-2-0531-0420-s004430 | forward | revenue | 4 | pending |
| line-2 | line-2-0531-0420-s004430 | reverse | revenue | 3 | pending |
| line-2 | line-2-0530-0506-s006158 | forward | revenue | 3 | pending |
| line-2 | line-2-0530-0506-s006158 | reverse | revenue | 3 | pending |
| line-2 | line-2-0526-0648-s009031 | forward | revenue | 3 | pending |
| line-2 | line-2-0526-0648-s009031 | reverse | revenue | 3 | pending |
| line-2 | line-2-0524-0761-s011308 | reverse | revenue | 3 | pending |
| line-2 | line-2-0531-0420-s004430 | reverse | spare | 1 | pending |
| line-2 | line-2-0530-0506-s006158 | forward | spare | 1 | pending |
| line-2 | line-2-0530-0506-s006158 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0648-s009031 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0744-0654-s006976 | forward | revenue | 5 | pending |
| line-3 | line-3-0744-0654-s006976 | reverse | revenue | 5 | pending |
| line-3 | line-3-0682-0495-s010716 | forward | revenue | 5 | pending |
| line-3 | line-3-0682-0495-s010716 | reverse | revenue | 5 | pending |
| line-3 | line-3-0649-0410-s012713 | forward | revenue | 5 | pending |
| line-3 | line-3-0649-0410-s012713 | reverse | revenue | 5 | pending |
| line-3 | line-3-0616-0325-s014722 | reverse | revenue | 5 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0744-0654-s006976 | forward | spare | 1 | pending |
| line-3 | line-3-0744-0654-s006976 | reverse | spare | 1 | pending |
| line-3 | line-3-0682-0495-s010716 | forward | spare | 1 | pending |
| line-3 | line-3-0682-0495-s010716 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**96 trainsets exceed the reference platform envelope**, requiring **5,712.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0015-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0414-0292-s006740 | 10 | 2 | 8 | 476.0 |
| line-1-0472-0355-s008680 | 8 | 2 | 6 | 357.0 |
| line-1-0531-0420-s010633 | 8 | 4 | 4 | 238.0 |
| line-1-0596-0491-s012778 | 8 | 2 | 6 | 357.0 |
| line-1-0670-0572-s015257 | 8 | 2 | 6 | 357.0 |
| line-1-0744-0654-s017721 | 8 | 4 | 4 | 238.0 |
| line-1-0748-0658-s017846 | 4 | 2 | 2 | 119.0 |
| line-2-0524-0761-s011308 | 3 | 2 | 1 | 59.5 |
| line-2-0526-0648-s009031 | 7 | 2 | 5 | 297.5 |
| line-2-0530-0506-s006158 | 8 | 2 | 6 | 357.0 |
| line-2-0531-0420-s004430 | 8 | 4 | 4 | 238.0 |
| line-2-0532-0204-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0533-0350-s003013 | 8 | 2 | 6 | 357.0 |
| line-3-0616-0325-s014722 | 5 | 2 | 3 | 178.5 |
| line-3-0649-0410-s012713 | 10 | 2 | 8 | 476.0 |
| line-3-0682-0495-s010716 | 12 | 2 | 10 | 595.0 |
| line-3-0744-0654-s006976 | 12 | 4 | 8 | 476.0 |
| line-3-0868-0951-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Fallujah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
