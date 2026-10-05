# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 107 at depots = 141 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0784-0410-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0449-0306-s023034 | line-2 | declared-depot | 61 | 3,629.5 | 11 |
| line-3-0393-0347-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0232-0603-s012768 | station | reverse | revenue | 2 |
| line-1 | line-1-0402-0544-s008844 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0544-s008844 | station | reverse | revenue | 1 |
| line-1 | line-1-0485-0515-s006932 | station | forward | revenue | 1 |
| line-1 | line-1-0485-0515-s006932 | station | reverse | revenue | 1 |
| line-1 | line-1-0568-0486-s004996 | station | forward | revenue | 1 |
| line-1 | line-1-0568-0486-s004996 | station | reverse | revenue | 1 |
| line-1 | line-1-0650-0457-s003081 | station | forward | revenue | 1 |
| line-1 | line-1-0650-0457-s003081 | station | reverse | revenue | 1 |
| line-1 | line-1-0784-0410-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0449-0306-s023034 | station | reverse | revenue | 2 |
| line-2 | line-2-0475-0506-s017781 | station | forward | revenue | 1 |
| line-2 | line-2-0475-0506-s017781 | station | reverse | revenue | 1 |
| line-2 | line-2-0505-0402-s020398 | station | forward | revenue | 1 |
| line-2 | line-2-0505-0402-s020398 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0486-s015151 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0486-s015151 | station | reverse | revenue | 1 |
| line-2 | line-2-0651-0610-s011819 | station | forward | revenue | 1 |
| line-2 | line-2-0651-0610-s011819 | station | reverse | revenue | 1 |
| line-2 | line-2-0906-1035-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0393-0347-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0398-0445-s002001 | station | forward | revenue | 1 |
| line-3 | line-3-0398-0445-s002001 | station | reverse | revenue | 1 |
| line-3 | line-3-0402-0544-s004015 | station | forward | revenue | 1 |
| line-3 | line-3-0402-0544-s004015 | station | reverse | revenue | 1 |
| line-3 | line-3-0407-0640-s005976 | station | forward | revenue | 1 |
| line-3 | line-3-0407-0640-s005976 | station | reverse | revenue | 1 |
| line-3 | line-3-0411-0736-s007929 | station | reverse | revenue | 2 |
| line-1 | line-1-0784-0410-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0784-0410-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0784-0410-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0449-0306-s023034 | depot | — | revenue | 54 |
| line-2 | line-2-0449-0306-s023034 | depot | — | spare | 6 |
| line-2 | line-2-0449-0306-s023034 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0393-0347-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0393-0347-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0393-0347-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kisumu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **141 trainsets at 17 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **127 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **107 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0784-0410-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0650-0457-s003081 | forward | revenue | 4 | pending |
| line-1 | line-1-0650-0457-s003081 | reverse | revenue | 4 | pending |
| line-1 | line-1-0568-0486-s004996 | forward | revenue | 4 | pending |
| line-1 | line-1-0568-0486-s004996 | reverse | revenue | 4 | pending |
| line-1 | line-1-0485-0515-s006932 | forward | revenue | 4 | pending |
| line-1 | line-1-0485-0515-s006932 | reverse | revenue | 3 | pending |
| line-1 | line-1-0402-0544-s008844 | forward | revenue | 3 | pending |
| line-1 | line-1-0402-0544-s008844 | reverse | revenue | 3 | pending |
| line-1 | line-1-0232-0603-s012768 | reverse | revenue | 3 | pending |
| line-1 | line-1-0485-0515-s006932 | reverse | spare | 1 | pending |
| line-1 | line-1-0402-0544-s008844 | forward | spare | 1 | pending |
| line-1 | line-1-0402-0544-s008844 | reverse | spare | 1 | pending |
| line-1 | line-1-0232-0603-s012768 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0651-0610-s011819 | forward | revenue | 7 | pending |
| line-2 | line-2-0651-0610-s011819 | reverse | revenue | 7 | pending |
| line-2 | line-2-0568-0486-s015151 | forward | revenue | 7 | pending |
| line-2 | line-2-0568-0486-s015151 | reverse | revenue | 7 | pending |
| line-2 | line-2-0475-0506-s017781 | forward | revenue | 7 | pending |
| line-2 | line-2-0475-0506-s017781 | reverse | revenue | 6 | pending |
| line-2 | line-2-0505-0402-s020398 | forward | revenue | 6 | pending |
| line-2 | line-2-0505-0402-s020398 | reverse | revenue | 6 | pending |
| line-2 | line-2-0449-0306-s023034 | reverse | revenue | 6 | pending |
| line-2 | line-2-0475-0506-s017781 | reverse | spare | 1 | pending |
| line-2 | line-2-0505-0402-s020398 | forward | spare | 1 | pending |
| line-2 | line-2-0505-0402-s020398 | reverse | spare | 1 | pending |
| line-2 | line-2-0449-0306-s023034 | reverse | spare | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0651-0610-s011819 | forward | spare | 1 | pending |
| line-2 | line-2-0651-0610-s011819 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0393-0347-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0398-0445-s002001 | forward | revenue | 3 | pending |
| line-3 | line-3-0398-0445-s002001 | reverse | revenue | 3 | pending |
| line-3 | line-3-0402-0544-s004015 | forward | revenue | 3 | pending |
| line-3 | line-3-0402-0544-s004015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0407-0640-s005976 | forward | revenue | 3 | pending |
| line-3 | line-3-0407-0640-s005976 | reverse | revenue | 3 | pending |
| line-3 | line-3-0411-0736-s007929 | reverse | revenue | 3 | pending |
| line-3 | line-3-0398-0445-s002001 | forward | spare | 1 | pending |
| line-3 | line-3-0398-0445-s002001 | reverse | spare | 1 | pending |
| line-3 | line-3-0402-0544-s004015 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0232-0603-s012768 | 4 | 2 | 2 | 119.0 |
| line-1-0402-0544-s008844 | 8 | 4 | 4 | 238.0 |
| line-1-0485-0515-s006932 | 8 | 4 | 4 | 238.0 |
| line-1-0568-0486-s004996 | 8 | 4 | 4 | 238.0 |
| line-1-0650-0457-s003081 | 8 | 2 | 6 | 357.0 |
| line-1-0784-0410-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0449-0306-s023034 | 7 | 2 | 5 | 297.5 |
| line-2-0475-0506-s017781 | 14 | 4 | 10 | 595.0 |
| line-2-0505-0402-s020398 | 14 | 2 | 12 | 714.0 |
| line-2-0568-0486-s015151 | 14 | 4 | 10 | 595.0 |
| line-2-0651-0610-s011819 | 16 | 2 | 14 | 833.0 |
| line-2-0906-1035-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0393-0347-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0398-0445-s002001 | 8 | 2 | 6 | 357.0 |
| line-3-0402-0544-s004015 | 7 | 4 | 3 | 178.5 |
| line-3-0407-0640-s005976 | 6 | 2 | 4 | 238.0 |
| line-3-0411-0736-s007929 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisumu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
