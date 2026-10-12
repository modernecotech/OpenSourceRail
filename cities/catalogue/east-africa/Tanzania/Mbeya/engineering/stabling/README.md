# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 142 at depots = 182 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0448-0937-s000000 | line-1 | declared-depot | 38 | 2,261.0 | 7 |
| line-2-0708-0058-s024728 | line-2 | declared-depot | 60 | 3,570.0 | 11 |
| line-3-0451-0402-s000000 | line-3 | declared-depot | 16 | 952.0 | 4 |
| line-4-0556-0539-s000000 | line-4 | declared-depot | 16 | 952.0 | 3 |
| line-5-0474-0906-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0448-0937-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0474-0906-s000906 | station | forward | revenue | 1 |
| line-1 | line-1-0474-0906-s000906 | station | reverse | revenue | 1 |
| line-1 | line-1-0605-0618-s007903 | station | forward | revenue | 1 |
| line-1 | line-1-0605-0618-s007903 | station | reverse | revenue | 1 |
| line-1 | line-1-0674-0444-s011990 | station | forward | revenue | 1 |
| line-1 | line-1-0674-0444-s011990 | station | reverse | revenue | 1 |
| line-1 | line-1-0733-0298-s015469 | station | reverse | revenue | 2 |
| line-2 | line-2-0555-0422-s014153 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0422-s014153 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0539-s011336 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0539-s011336 | station | reverse | revenue | 1 |
| line-2 | line-2-0605-0618-s008670 | station | forward | revenue | 1 |
| line-2 | line-2-0605-0618-s008670 | station | reverse | revenue | 1 |
| line-2 | line-2-0609-0917-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0626-0680-s006954 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0680-s006954 | station | reverse | revenue | 1 |
| line-2 | line-2-0646-0266-s019005 | station | forward | revenue | 1 |
| line-2 | line-2-0646-0266-s019005 | station | reverse | revenue | 1 |
| line-2 | line-2-0708-0058-s024728 | station | reverse | revenue | 2 |
| line-3 | line-3-0451-0402-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0555-0422-s002246 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0422-s002246 | station | reverse | revenue | 1 |
| line-3 | line-3-0674-0444-s004808 | station | forward | revenue | 1 |
| line-3 | line-3-0674-0444-s004808 | station | reverse | revenue | 1 |
| line-3 | line-3-0781-0464-s007114 | station | reverse | revenue | 2 |
| line-4 | line-4-0388-0537-s005996 | station | reverse | revenue | 2 |
| line-4 | line-4-0556-0539-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0474-0906-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0587-1036-s004541 | station | reverse | revenue | 2 |
| line-1 | line-1-0448-0937-s000000 | depot | — | revenue | 33 |
| line-1 | line-1-0448-0937-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0448-0937-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0708-0058-s024728 | depot | — | revenue | 53 |
| line-2 | line-2-0708-0058-s024728 | depot | — | spare | 6 |
| line-2 | line-2-0708-0058-s024728 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0451-0402-s000000 | depot | — | revenue | 13 |
| line-3 | line-3-0451-0402-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0451-0402-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0556-0539-s000000 | depot | — | revenue | 14 |
| line-4 | line-4-0556-0539-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0556-0539-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0474-0906-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0474-0906-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0474-0906-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbeya-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **182 trainsets at 20 stations**; largest initial station queue **13**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **142 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0448-0937-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0474-0906-s000906 | forward | revenue | 6 | pending |
| line-1 | line-1-0474-0906-s000906 | reverse | revenue | 6 | pending |
| line-1 | line-1-0605-0618-s007903 | forward | revenue | 5 | pending |
| line-1 | line-1-0605-0618-s007903 | reverse | revenue | 5 | pending |
| line-1 | line-1-0674-0444-s011990 | forward | revenue | 5 | pending |
| line-1 | line-1-0674-0444-s011990 | reverse | revenue | 5 | pending |
| line-1 | line-1-0733-0298-s015469 | reverse | revenue | 5 | pending |
| line-1 | line-1-0605-0618-s007903 | forward | spare | 1 | pending |
| line-1 | line-1-0605-0618-s007903 | reverse | spare | 1 | pending |
| line-1 | line-1-0674-0444-s011990 | forward | spare | 1 | pending |
| line-1 | line-1-0674-0444-s011990 | reverse | spare | 1 | pending |
| line-1 | line-1-0733-0298-s015469 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0626-0680-s006954 | forward | revenue | 6 | pending |
| line-2 | line-2-0626-0680-s006954 | reverse | revenue | 6 | pending |
| line-2 | line-2-0605-0618-s008670 | forward | revenue | 6 | pending |
| line-2 | line-2-0605-0618-s008670 | reverse | revenue | 6 | pending |
| line-2 | line-2-0556-0539-s011336 | forward | revenue | 6 | pending |
| line-2 | line-2-0556-0539-s011336 | reverse | revenue | 6 | pending |
| line-2 | line-2-0555-0422-s014153 | forward | revenue | 5 | pending |
| line-2 | line-2-0555-0422-s014153 | reverse | revenue | 5 | pending |
| line-2 | line-2-0646-0266-s019005 | forward | revenue | 5 | pending |
| line-2 | line-2-0646-0266-s019005 | reverse | revenue | 5 | pending |
| line-2 | line-2-0708-0058-s024728 | reverse | revenue | 5 | pending |
| line-2 | line-2-0555-0422-s014153 | forward | spare | 1 | pending |
| line-2 | line-2-0555-0422-s014153 | reverse | spare | 1 | pending |
| line-2 | line-2-0646-0266-s019005 | forward | spare | 1 | pending |
| line-2 | line-2-0646-0266-s019005 | reverse | spare | 1 | pending |
| line-2 | line-2-0708-0058-s024728 | reverse | spare | 1 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0680-s006954 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0451-0402-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0555-0422-s002246 | forward | revenue | 4 | pending |
| line-3 | line-3-0555-0422-s002246 | reverse | revenue | 4 | pending |
| line-3 | line-3-0674-0444-s004808 | forward | revenue | 3 | pending |
| line-3 | line-3-0674-0444-s004808 | reverse | revenue | 3 | pending |
| line-3 | line-3-0781-0464-s007114 | reverse | revenue | 3 | pending |
| line-3 | line-3-0674-0444-s004808 | forward | spare | 1 | pending |
| line-3 | line-3-0674-0444-s004808 | reverse | spare | 1 | pending |
| line-3 | line-3-0781-0464-s007114 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0556-0539-s000000 | forward | revenue | 9 | pending |
| line-4 | line-4-0388-0537-s005996 | reverse | revenue | 9 | pending |
| line-4 | line-4-0556-0539-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0388-0537-s005996 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0474-0906-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0587-1036-s004541 | reverse | revenue | 7 | pending |
| line-5 | line-5-0474-0906-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0587-1036-s004541 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**126 trainsets exceed the reference platform envelope**, requiring **7,497.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0448-0937-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0474-0906-s000906 | 12 | 4 | 8 | 476.0 |
| line-1-0605-0618-s007903 | 12 | 4 | 8 | 476.0 |
| line-1-0674-0444-s011990 | 12 | 4 | 8 | 476.0 |
| line-1-0733-0298-s015469 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0422-s014153 | 12 | 4 | 8 | 476.0 |
| line-2-0556-0539-s011336 | 12 | 4 | 8 | 476.0 |
| line-2-0605-0618-s008670 | 12 | 4 | 8 | 476.0 |
| line-2-0609-0917-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0626-0680-s006954 | 13 | 2 | 11 | 654.5 |
| line-2-0646-0266-s019005 | 12 | 2 | 10 | 595.0 |
| line-2-0708-0058-s024728 | 6 | 2 | 4 | 238.0 |
| line-3-0451-0402-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0555-0422-s002246 | 8 | 4 | 4 | 238.0 |
| line-3-0674-0444-s004808 | 8 | 4 | 4 | 238.0 |
| line-3-0781-0464-s007114 | 4 | 2 | 2 | 119.0 |
| line-4-0388-0537-s005996 | 10 | 2 | 8 | 476.0 |
| line-4-0556-0539-s000000 | 10 | 2 | 8 | 476.0 |
| line-5-0474-0906-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0587-1036-s004541 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Mbeya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
