# Station and depot overnight allocation

Plan: **38 trainsets at stations + 77 at depots = 115 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0232-0603-s017091 | line-1 | storage-at-existing-powered-service-point | 21 | 1,249.5 | 0 |
| line-2-0449-0306-s023627 | line-2 | declared-depot | 40 | 2,380.0 | 18 |
| line-3-0411-0736-s012742 | line-3 | storage-at-existing-powered-service-point | 16 | 952.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0232-0603-s017091 | station | reverse | revenue | 2 |
| line-1 | line-1-0347-0630-s014345 | station | forward | revenue | 1 |
| line-1 | line-1-0347-0630-s014345 | station | reverse | revenue | 1 |
| line-1 | line-1-0423-0544-s011609 | station | forward | revenue | 1 |
| line-1 | line-1-0423-0544-s011609 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0591-s008868 | station | forward | revenue | 1 |
| line-1 | line-1-0486-0591-s008868 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0556-s007242 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0556-s007242 | station | reverse | revenue | 1 |
| line-1 | line-1-0568-0505-s005859 | station | forward | revenue | 1 |
| line-1 | line-1-0568-0505-s005859 | station | reverse | revenue | 1 |
| line-1 | line-1-0655-0460-s003378 | station | forward | revenue | 1 |
| line-1 | line-1-0655-0460-s003378 | station | reverse | revenue | 1 |
| line-1 | line-1-0784-0410-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0449-0306-s023627 | station | reverse | revenue | 2 |
| line-2 | line-2-0504-0502-s018077 | station | forward | revenue | 1 |
| line-2 | line-2-0504-0502-s018077 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0556-s015219 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0556-s015219 | station | reverse | revenue | 1 |
| line-2 | line-2-0638-0635-s012053 | station | forward | revenue | 1 |
| line-2 | line-2-0638-0635-s012053 | station | reverse | revenue | 1 |
| line-2 | line-2-0906-1035-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0393-0347-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0411-0736-s012742 | station | reverse | revenue | 2 |
| line-3 | line-3-0434-0658-s010869 | station | forward | revenue | 1 |
| line-3 | line-3-0434-0658-s010869 | station | reverse | revenue | 1 |
| line-3 | line-3-0438-0474-s003018 | station | forward | revenue | 1 |
| line-3 | line-3-0438-0474-s003018 | station | reverse | revenue | 1 |
| line-3 | line-3-0497-0630-s008970 | station | forward | revenue | 1 |
| line-3 | line-3-0497-0630-s008970 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0556-s006413 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0556-s006413 | station | reverse | revenue | 1 |
| line-1 | line-1-0232-0603-s017091 | depot | — | revenue | 17 |
| line-1 | line-1-0232-0603-s017091 | depot | — | spare | 3 |
| line-1 | line-1-0232-0603-s017091 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0449-0306-s023627 | depot | — | revenue | 35 |
| line-2 | line-2-0449-0306-s023627 | depot | — | spare | 4 |
| line-2 | line-2-0449-0306-s023627 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0411-0736-s012742 | depot | — | revenue | 13 |
| line-3 | line-3-0411-0736-s012742 | depot | — | spare | 2 |
| line-3 | line-3-0411-0736-s012742 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kisumu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **115 trainsets at 19 stations**; largest initial station queue **13**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **103 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **77 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0784-0410-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0655-0460-s003378 | forward | revenue | 3 | pending |
| line-1 | line-1-0655-0460-s003378 | reverse | revenue | 3 | pending |
| line-1 | line-1-0568-0505-s005859 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0505-s005859 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0556-s007242 | forward | revenue | 2 | pending |
| line-1 | line-1-0543-0556-s007242 | reverse | revenue | 2 | pending |
| line-1 | line-1-0486-0591-s008868 | forward | revenue | 2 | pending |
| line-1 | line-1-0486-0591-s008868 | reverse | revenue | 2 | pending |
| line-1 | line-1-0423-0544-s011609 | forward | revenue | 2 | pending |
| line-1 | line-1-0423-0544-s011609 | reverse | revenue | 2 | pending |
| line-1 | line-1-0347-0630-s014345 | forward | revenue | 2 | pending |
| line-1 | line-1-0347-0630-s014345 | reverse | revenue | 2 | pending |
| line-1 | line-1-0232-0603-s017091 | reverse | revenue | 2 | pending |
| line-1 | line-1-0543-0556-s007242 | forward | spare | 1 | pending |
| line-1 | line-1-0543-0556-s007242 | reverse | spare | 1 | pending |
| line-1 | line-1-0486-0591-s008868 | forward | spare | 1 | pending |
| line-1 | line-1-0486-0591-s008868 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0638-0635-s012053 | forward | revenue | 6 | pending |
| line-2 | line-2-0638-0635-s012053 | reverse | revenue | 6 | pending |
| line-2 | line-2-0543-0556-s015219 | forward | revenue | 6 | pending |
| line-2 | line-2-0543-0556-s015219 | reverse | revenue | 6 | pending |
| line-2 | line-2-0504-0502-s018077 | forward | revenue | 5 | pending |
| line-2 | line-2-0504-0502-s018077 | reverse | revenue | 5 | pending |
| line-2 | line-2-0449-0306-s023627 | reverse | revenue | 5 | pending |
| line-2 | line-2-0504-0502-s018077 | forward | spare | 1 | pending |
| line-2 | line-2-0504-0502-s018077 | reverse | spare | 1 | pending |
| line-2 | line-2-0449-0306-s023627 | reverse | spare | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0638-0635-s012053 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0393-0347-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0438-0474-s003018 | forward | revenue | 3 | pending |
| line-3 | line-3-0438-0474-s003018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0543-0556-s006413 | forward | revenue | 3 | pending |
| line-3 | line-3-0543-0556-s006413 | reverse | revenue | 3 | pending |
| line-3 | line-3-0497-0630-s008970 | forward | revenue | 2 | pending |
| line-3 | line-3-0497-0630-s008970 | reverse | revenue | 2 | pending |
| line-3 | line-3-0434-0658-s010869 | forward | revenue | 2 | pending |
| line-3 | line-3-0434-0658-s010869 | reverse | revenue | 2 | pending |
| line-3 | line-3-0411-0736-s012742 | reverse | revenue | 2 | pending |
| line-3 | line-3-0497-0630-s008970 | forward | spare | 1 | pending |
| line-3 | line-3-0497-0630-s008970 | reverse | spare | 1 | pending |
| line-3 | line-3-0434-0658-s010869 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**71 trainsets exceed the reference platform envelope**, requiring **4,224.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0232-0603-s017091 | 2 | 2 | 0 | 0.0 |
| line-1-0347-0630-s014345 | 4 | 2 | 2 | 119.0 |
| line-1-0423-0544-s011609 | 4 | 2 | 2 | 119.0 |
| line-1-0486-0591-s008868 | 6 | 2 | 4 | 238.0 |
| line-1-0543-0556-s007242 | 6 | 4 | 2 | 119.0 |
| line-1-0568-0505-s005859 | 6 | 2 | 4 | 238.0 |
| line-1-0655-0460-s003378 | 6 | 2 | 4 | 238.0 |
| line-1-0784-0410-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0449-0306-s023627 | 6 | 2 | 4 | 238.0 |
| line-2-0504-0502-s018077 | 12 | 2 | 10 | 595.0 |
| line-2-0543-0556-s015219 | 12 | 4 | 8 | 476.0 |
| line-2-0638-0635-s012053 | 13 | 2 | 11 | 654.5 |
| line-2-0906-1035-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0393-0347-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0411-0736-s012742 | 2 | 2 | 0 | 0.0 |
| line-3-0434-0658-s010869 | 5 | 2 | 3 | 178.5 |
| line-3-0438-0474-s003018 | 6 | 2 | 4 | 238.0 |
| line-3-0497-0630-s008970 | 6 | 2 | 4 | 238.0 |
| line-3-0543-0556-s006413 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisumu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
