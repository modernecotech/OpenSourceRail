# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 149 at depots = 181 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0332-0510-s000000 | line-1 | declared-depot | 44 | 2,618.0 | 8 |
| line-2-0250-0062-s000000 | line-2 | declared-depot | 47 | 2,796.5 | 9 |
| line-3-1046-0061-s021993 | line-3 | declared-depot | 58 | 3,451.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0332-0510-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0477-0497-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0477-0497-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0621-0483-s006027 | station | forward | revenue | 1 |
| line-1 | line-1-0621-0483-s006027 | station | reverse | revenue | 1 |
| line-1 | line-1-1086-0483-s016328 | station | reverse | revenue | 2 |
| line-2 | line-2-0250-0062-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0362-0364-s007012 | station | forward | revenue | 1 |
| line-2 | line-2-0362-0364-s007012 | station | reverse | revenue | 1 |
| line-2 | line-2-0416-0490-s010026 | station | forward | revenue | 1 |
| line-2 | line-2-0416-0490-s010026 | station | reverse | revenue | 1 |
| line-2 | line-2-0470-0616-s013028 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0616-s013028 | station | reverse | revenue | 1 |
| line-2 | line-2-0507-0702-s015078 | station | forward | revenue | 1 |
| line-2 | line-2-0507-0702-s015078 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0789-s017137 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0789-s017137 | station | reverse | revenue | 1 |
| line-2 | line-2-0581-0875-s019198 | station | reverse | revenue | 2 |
| line-3 | line-3-0486-0828-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0559-0714-s003025 | station | forward | revenue | 1 |
| line-3 | line-3-0559-0714-s003025 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0601-s006034 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0601-s006034 | station | reverse | revenue | 1 |
| line-3 | line-3-0716-0467-s009524 | station | forward | revenue | 1 |
| line-3 | line-3-0716-0467-s009524 | station | reverse | revenue | 1 |
| line-3 | line-3-1046-0061-s021993 | station | reverse | revenue | 2 |
| line-1 | line-1-0332-0510-s000000 | depot | — | revenue | 39 |
| line-1 | line-1-0332-0510-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0332-0510-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0250-0062-s000000 | depot | — | revenue | 41 |
| line-2 | line-2-0250-0062-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0250-0062-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1046-0061-s021993 | depot | — | revenue | 51 |
| line-3 | line-3-1046-0061-s021993 | depot | — | spare | 6 |
| line-3 | line-3-1046-0061-s021993 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bafoussam-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **181 trainsets at 16 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **149 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0332-0510-s000000 | forward | revenue | 8 | pending |
| line-1 | line-1-0477-0497-s003019 | forward | revenue | 8 | pending |
| line-1 | line-1-0477-0497-s003019 | reverse | revenue | 8 | pending |
| line-1 | line-1-0621-0483-s006027 | forward | revenue | 8 | pending |
| line-1 | line-1-0621-0483-s006027 | reverse | revenue | 8 | pending |
| line-1 | line-1-1086-0483-s016328 | reverse | revenue | 7 | pending |
| line-1 | line-1-1086-0483-s016328 | reverse | spare | 1 | pending |
| line-1 | line-1-0332-0510-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0477-0497-s003019 | forward | spare | 1 | pending |
| line-1 | line-1-0477-0497-s003019 | reverse | spare | 1 | pending |
| line-1 | line-1-0621-0483-s006027 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0250-0062-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0362-0364-s007012 | forward | revenue | 5 | pending |
| line-2 | line-2-0362-0364-s007012 | reverse | revenue | 5 | pending |
| line-2 | line-2-0416-0490-s010026 | forward | revenue | 5 | pending |
| line-2 | line-2-0416-0490-s010026 | reverse | revenue | 5 | pending |
| line-2 | line-2-0470-0616-s013028 | forward | revenue | 5 | pending |
| line-2 | line-2-0470-0616-s013028 | reverse | revenue | 5 | pending |
| line-2 | line-2-0507-0702-s015078 | forward | revenue | 4 | pending |
| line-2 | line-2-0507-0702-s015078 | reverse | revenue | 4 | pending |
| line-2 | line-2-0544-0789-s017137 | forward | revenue | 4 | pending |
| line-2 | line-2-0544-0789-s017137 | reverse | revenue | 4 | pending |
| line-2 | line-2-0581-0875-s019198 | reverse | revenue | 4 | pending |
| line-2 | line-2-0507-0702-s015078 | forward | spare | 1 | pending |
| line-2 | line-2-0507-0702-s015078 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0789-s017137 | forward | spare | 1 | pending |
| line-2 | line-2-0544-0789-s017137 | reverse | spare | 1 | pending |
| line-2 | line-2-0581-0875-s019198 | reverse | spare | 1 | pending |
| line-2 | line-2-0250-0062-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0486-0828-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0559-0714-s003025 | forward | revenue | 8 | pending |
| line-3 | line-3-0559-0714-s003025 | reverse | revenue | 8 | pending |
| line-3 | line-3-0631-0601-s006034 | forward | revenue | 8 | pending |
| line-3 | line-3-0631-0601-s006034 | reverse | revenue | 8 | pending |
| line-3 | line-3-0716-0467-s009524 | forward | revenue | 7 | pending |
| line-3 | line-3-0716-0467-s009524 | reverse | revenue | 7 | pending |
| line-3 | line-3-1046-0061-s021993 | reverse | revenue | 7 | pending |
| line-3 | line-3-0716-0467-s009524 | forward | spare | 1 | pending |
| line-3 | line-3-0716-0467-s009524 | reverse | spare | 1 | pending |
| line-3 | line-3-1046-0061-s021993 | reverse | spare | 1 | pending |
| line-3 | line-3-0486-0828-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0559-0714-s003025 | forward | spare | 1 | pending |
| line-3 | line-3-0559-0714-s003025 | reverse | spare | 1 | pending |
| line-3 | line-3-0631-0601-s006034 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**149 trainsets exceed the reference platform envelope**, requiring **8,865.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0332-0510-s000000 | 9 | 2 | 7 | 416.5 |
| line-1-0477-0497-s003019 | 18 | 2 | 16 | 952.0 |
| line-1-0621-0483-s006027 | 17 | 2 | 15 | 892.5 |
| line-1-1086-0483-s016328 | 8 | 2 | 6 | 357.0 |
| line-2-0250-0062-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0362-0364-s007012 | 10 | 2 | 8 | 476.0 |
| line-2-0416-0490-s010026 | 10 | 2 | 8 | 476.0 |
| line-2-0470-0616-s013028 | 10 | 2 | 8 | 476.0 |
| line-2-0507-0702-s015078 | 10 | 2 | 8 | 476.0 |
| line-2-0544-0789-s017137 | 10 | 2 | 8 | 476.0 |
| line-2-0581-0875-s019198 | 5 | 2 | 3 | 178.5 |
| line-3-0486-0828-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0559-0714-s003025 | 18 | 2 | 16 | 952.0 |
| line-3-0631-0601-s006034 | 17 | 2 | 15 | 892.5 |
| line-3-0716-0467-s009524 | 16 | 2 | 14 | 833.0 |
| line-3-1046-0061-s021993 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bafoussam/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
