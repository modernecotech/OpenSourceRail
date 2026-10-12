# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 136 at depots = 178 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0400-1089-s000000 | line-1 | declared-depot | 35 | 2,082.5 | 7 |
| line-2-0869-0325-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0357-0378-s016510 | line-3 | declared-depot | 39 | 2,320.5 | 8 |
| line-4-0402-0586-s000000 | line-4 | declared-depot | 12 | 714.0 | 3 |
| line-5-0691-0459-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0392-0381-s015331 | station | reverse | revenue | 2 |
| line-1 | line-1-0395-0451-s013907 | station | forward | revenue | 1 |
| line-1 | line-1-0395-0451-s013907 | station | reverse | revenue | 1 |
| line-1 | line-1-0400-1089-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0402-0586-s011149 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0586-s011149 | station | reverse | revenue | 1 |
| line-1 | line-1-0407-0674-s009335 | station | forward | revenue | 1 |
| line-1 | line-1-0407-0674-s009335 | station | reverse | revenue | 1 |
| line-1 | line-1-0415-0834-s006069 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0834-s006069 | station | reverse | revenue | 1 |
| line-2 | line-2-0329-0733-s015141 | station | reverse | revenue | 2 |
| line-2 | line-2-0407-0674-s012986 | station | forward | revenue | 1 |
| line-2 | line-2-0407-0674-s012986 | station | reverse | revenue | 1 |
| line-2 | line-2-0549-0567-s008932 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0567-s008932 | station | reverse | revenue | 1 |
| line-2 | line-2-0691-0459-s004975 | station | forward | revenue | 1 |
| line-2 | line-2-0691-0459-s004975 | station | reverse | revenue | 1 |
| line-2 | line-2-0869-0325-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0357-0378-s016510 | station | reverse | revenue | 2 |
| line-3 | line-3-0395-0451-s013897 | station | forward | revenue | 1 |
| line-3 | line-3-0395-0451-s013897 | station | reverse | revenue | 1 |
| line-3 | line-3-0542-0484-s009608 | station | forward | revenue | 1 |
| line-3 | line-3-0542-0484-s009608 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0567-s007469 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0567-s007469 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0606-s003579 | station | forward | revenue | 1 |
| line-3 | line-3-0711-0606-s003579 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0618-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0237-0512-s004523 | station | reverse | revenue | 2 |
| line-4 | line-4-0402-0586-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0543-0483-s004874 | station | reverse | revenue | 2 |
| line-5 | line-5-0691-0459-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0400-1089-s000000 | depot | — | revenue | 30 |
| line-1 | line-1-0400-1089-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0400-1089-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0869-0325-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0869-0325-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0869-0325-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0357-0378-s016510 | depot | — | revenue | 34 |
| line-3 | line-3-0357-0378-s016510 | depot | — | spare | 4 |
| line-3 | line-3-0357-0378-s016510 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0402-0586-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0402-0586-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0402-0586-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0691-0459-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0691-0459-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0691-0459-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/morogoro-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **178 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **136 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1089-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0834-s006069 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0834-s006069 | reverse | revenue | 4 | pending |
| line-1 | line-1-0407-0674-s009335 | forward | revenue | 4 | pending |
| line-1 | line-1-0407-0674-s009335 | reverse | revenue | 4 | pending |
| line-1 | line-1-0402-0586-s011149 | forward | revenue | 4 | pending |
| line-1 | line-1-0402-0586-s011149 | reverse | revenue | 4 | pending |
| line-1 | line-1-0395-0451-s013907 | forward | revenue | 4 | pending |
| line-1 | line-1-0395-0451-s013907 | reverse | revenue | 4 | pending |
| line-1 | line-1-0392-0381-s015331 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0834-s006069 | reverse | spare | 1 | pending |
| line-1 | line-1-0407-0674-s009335 | forward | spare | 1 | pending |
| line-1 | line-1-0407-0674-s009335 | reverse | spare | 1 | pending |
| line-1 | line-1-0402-0586-s011149 | forward | spare | 1 | pending |
| line-1 | line-1-0402-0586-s011149 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0869-0325-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0691-0459-s004975 | forward | revenue | 6 | pending |
| line-2 | line-2-0691-0459-s004975 | reverse | revenue | 6 | pending |
| line-2 | line-2-0549-0567-s008932 | forward | revenue | 5 | pending |
| line-2 | line-2-0549-0567-s008932 | reverse | revenue | 5 | pending |
| line-2 | line-2-0407-0674-s012986 | forward | revenue | 5 | pending |
| line-2 | line-2-0407-0674-s012986 | reverse | revenue | 5 | pending |
| line-2 | line-2-0329-0733-s015141 | reverse | revenue | 5 | pending |
| line-2 | line-2-0549-0567-s008932 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0567-s008932 | reverse | spare | 1 | pending |
| line-2 | line-2-0407-0674-s012986 | forward | spare | 1 | pending |
| line-2 | line-2-0407-0674-s012986 | reverse | spare | 1 | pending |
| line-2 | line-2-0329-0733-s015141 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0885-0618-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0711-0606-s003579 | forward | revenue | 5 | pending |
| line-3 | line-3-0711-0606-s003579 | reverse | revenue | 5 | pending |
| line-3 | line-3-0549-0567-s007469 | forward | revenue | 5 | pending |
| line-3 | line-3-0549-0567-s007469 | reverse | revenue | 5 | pending |
| line-3 | line-3-0542-0484-s009608 | forward | revenue | 5 | pending |
| line-3 | line-3-0542-0484-s009608 | reverse | revenue | 4 | pending |
| line-3 | line-3-0395-0451-s013897 | forward | revenue | 4 | pending |
| line-3 | line-3-0395-0451-s013897 | reverse | revenue | 4 | pending |
| line-3 | line-3-0357-0378-s016510 | reverse | revenue | 4 | pending |
| line-3 | line-3-0542-0484-s009608 | reverse | spare | 1 | pending |
| line-3 | line-3-0395-0451-s013897 | forward | spare | 1 | pending |
| line-3 | line-3-0395-0451-s013897 | reverse | spare | 1 | pending |
| line-3 | line-3-0357-0378-s016510 | reverse | spare | 1 | pending |
| line-3 | line-3-0885-0618-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0402-0586-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0237-0512-s004523 | reverse | revenue | 7 | pending |
| line-4 | line-4-0402-0586-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0237-0512-s004523 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0691-0459-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0543-0483-s004874 | reverse | revenue | 7 | pending |
| line-5 | line-5-0691-0459-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0543-0483-s004874 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**118 trainsets exceed the reference platform envelope**, requiring **7,021.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0392-0381-s015331 | 4 | 2 | 2 | 119.0 |
| line-1-0395-0451-s013907 | 8 | 4 | 4 | 238.0 |
| line-1-0400-1089-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0402-0586-s011149 | 10 | 4 | 6 | 357.0 |
| line-1-0407-0674-s009335 | 10 | 4 | 6 | 357.0 |
| line-1-0415-0834-s006069 | 10 | 2 | 8 | 476.0 |
| line-2-0329-0733-s015141 | 6 | 2 | 4 | 238.0 |
| line-2-0407-0674-s012986 | 12 | 4 | 8 | 476.0 |
| line-2-0549-0567-s008932 | 12 | 4 | 8 | 476.0 |
| line-2-0691-0459-s004975 | 12 | 4 | 8 | 476.0 |
| line-2-0869-0325-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0357-0378-s016510 | 5 | 2 | 3 | 178.5 |
| line-3-0395-0451-s013897 | 10 | 4 | 6 | 357.0 |
| line-3-0542-0484-s009608 | 10 | 4 | 6 | 357.0 |
| line-3-0549-0567-s007469 | 10 | 4 | 6 | 357.0 |
| line-3-0711-0606-s003579 | 10 | 2 | 8 | 476.0 |
| line-3-0885-0618-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0237-0512-s004523 | 8 | 2 | 6 | 357.0 |
| line-4-0402-0586-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0543-0483-s004874 | 8 | 2 | 6 | 357.0 |
| line-5-0691-0459-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Morogoro/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
