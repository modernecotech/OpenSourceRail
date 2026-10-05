# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 131 at depots = 173 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0283-0726-s000000 | line-1 | declared-depot | 37 | 2,201.5 | 8 |
| line-2-0000-0301-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0729-0230-s021864 | line-3 | declared-depot | 55 | 3,272.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0283-0726-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0350-0609-s003024 | station | forward | revenue | 1 |
| line-1 | line-1-0350-0609-s003024 | station | reverse | revenue | 1 |
| line-1 | line-1-0416-0492-s006028 | station | forward | revenue | 1 |
| line-1 | line-1-0416-0492-s006028 | station | reverse | revenue | 1 |
| line-1 | line-1-0483-0375-s009028 | station | forward | revenue | 1 |
| line-1 | line-1-0483-0375-s009028 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0120-s015818 | station | reverse | revenue | 2 |
| line-1 | line-1-0560-0239-s012527 | station | forward | revenue | 1 |
| line-1 | line-1-0560-0239-s012527 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0176-s014185 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0176-s014185 | station | reverse | revenue | 1 |
| line-2 | line-2-0000-0301-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0134-0317-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0134-0317-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0245-0364-s005577 | station | forward | revenue | 1 |
| line-2 | line-2-0245-0364-s005577 | station | reverse | revenue | 1 |
| line-2 | line-2-0367-0379-s008141 | station | forward | revenue | 1 |
| line-2 | line-2-0367-0379-s008141 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0397-s011150 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0397-s011150 | station | reverse | revenue | 1 |
| line-2 | line-2-0653-0415-s014159 | station | forward | revenue | 1 |
| line-2 | line-2-0653-0415-s014159 | station | reverse | revenue | 1 |
| line-2 | line-2-0804-0434-s017337 | station | reverse | revenue | 2 |
| line-3 | line-3-0259-1031-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0349-0776-s007011 | station | forward | revenue | 1 |
| line-3 | line-3-0349-0776-s007011 | station | reverse | revenue | 1 |
| line-3 | line-3-0426-0665-s010033 | station | forward | revenue | 1 |
| line-3 | line-3-0426-0665-s010033 | station | reverse | revenue | 1 |
| line-3 | line-3-0522-0528-s013779 | station | forward | revenue | 1 |
| line-3 | line-3-0522-0528-s013779 | station | reverse | revenue | 1 |
| line-3 | line-3-0581-0443-s016073 | station | forward | revenue | 1 |
| line-3 | line-3-0581-0443-s016073 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0332-s019095 | station | forward | revenue | 1 |
| line-3 | line-3-0658-0332-s019095 | station | reverse | revenue | 1 |
| line-3 | line-3-0729-0230-s021864 | station | reverse | revenue | 2 |
| line-1 | line-1-0283-0726-s000000 | depot | — | revenue | 32 |
| line-1 | line-1-0283-0726-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0283-0726-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0000-0301-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0000-0301-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0000-0301-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0729-0230-s021864 | depot | — | revenue | 48 |
| line-3 | line-3-0729-0230-s021864 | depot | — | spare | 6 |
| line-3 | line-3-0729-0230-s021864 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tabuk-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **173 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **156 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **131 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0283-0726-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0609-s003024 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0609-s003024 | reverse | revenue | 4 | pending |
| line-1 | line-1-0416-0492-s006028 | forward | revenue | 4 | pending |
| line-1 | line-1-0416-0492-s006028 | reverse | revenue | 4 | pending |
| line-1 | line-1-0483-0375-s009028 | forward | revenue | 4 | pending |
| line-1 | line-1-0483-0375-s009028 | reverse | revenue | 4 | pending |
| line-1 | line-1-0560-0239-s012527 | forward | revenue | 4 | pending |
| line-1 | line-1-0560-0239-s012527 | reverse | revenue | 4 | pending |
| line-1 | line-1-0583-0176-s014185 | forward | revenue | 4 | pending |
| line-1 | line-1-0583-0176-s014185 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0120-s015818 | reverse | revenue | 3 | pending |
| line-1 | line-1-0583-0176-s014185 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0120-s015818 | reverse | spare | 1 | pending |
| line-1 | line-1-0283-0726-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0350-0609-s003024 | forward | spare | 1 | pending |
| line-1 | line-1-0350-0609-s003024 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0134-0317-s003010 | forward | revenue | 4 | pending |
| line-2 | line-2-0134-0317-s003010 | reverse | revenue | 4 | pending |
| line-2 | line-2-0245-0364-s005577 | forward | revenue | 4 | pending |
| line-2 | line-2-0245-0364-s005577 | reverse | revenue | 4 | pending |
| line-2 | line-2-0367-0379-s008141 | forward | revenue | 4 | pending |
| line-2 | line-2-0367-0379-s008141 | reverse | revenue | 4 | pending |
| line-2 | line-2-0510-0397-s011150 | forward | revenue | 4 | pending |
| line-2 | line-2-0510-0397-s011150 | reverse | revenue | 4 | pending |
| line-2 | line-2-0653-0415-s014159 | forward | revenue | 4 | pending |
| line-2 | line-2-0653-0415-s014159 | reverse | revenue | 4 | pending |
| line-2 | line-2-0804-0434-s017337 | reverse | revenue | 4 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003010 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003010 | reverse | spare | 1 | pending |
| line-2 | line-2-0245-0364-s005577 | forward | spare | 1 | pending |
| line-2 | line-2-0245-0364-s005577 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0259-1031-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0349-0776-s007011 | forward | revenue | 6 | pending |
| line-3 | line-3-0349-0776-s007011 | reverse | revenue | 5 | pending |
| line-3 | line-3-0426-0665-s010033 | forward | revenue | 5 | pending |
| line-3 | line-3-0426-0665-s010033 | reverse | revenue | 5 | pending |
| line-3 | line-3-0522-0528-s013779 | forward | revenue | 5 | pending |
| line-3 | line-3-0522-0528-s013779 | reverse | revenue | 5 | pending |
| line-3 | line-3-0581-0443-s016073 | forward | revenue | 5 | pending |
| line-3 | line-3-0581-0443-s016073 | reverse | revenue | 5 | pending |
| line-3 | line-3-0658-0332-s019095 | forward | revenue | 5 | pending |
| line-3 | line-3-0658-0332-s019095 | reverse | revenue | 5 | pending |
| line-3 | line-3-0729-0230-s021864 | reverse | revenue | 5 | pending |
| line-3 | line-3-0349-0776-s007011 | reverse | spare | 1 | pending |
| line-3 | line-3-0426-0665-s010033 | forward | spare | 1 | pending |
| line-3 | line-3-0426-0665-s010033 | reverse | spare | 1 | pending |
| line-3 | line-3-0522-0528-s013779 | forward | spare | 1 | pending |
| line-3 | line-3-0522-0528-s013779 | reverse | spare | 1 | pending |
| line-3 | line-3-0581-0443-s016073 | forward | spare | 1 | pending |
| line-3 | line-3-0581-0443-s016073 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**127 trainsets exceed the reference platform envelope**, requiring **7,556.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0283-0726-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0350-0609-s003024 | 10 | 2 | 8 | 476.0 |
| line-1-0416-0492-s006028 | 8 | 2 | 6 | 357.0 |
| line-1-0483-0375-s009028 | 8 | 4 | 4 | 238.0 |
| line-1-0548-0120-s015818 | 4 | 2 | 2 | 119.0 |
| line-1-0560-0239-s012527 | 8 | 2 | 6 | 357.0 |
| line-1-0583-0176-s014185 | 8 | 2 | 6 | 357.0 |
| line-2-0000-0301-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0134-0317-s003010 | 10 | 2 | 8 | 476.0 |
| line-2-0245-0364-s005577 | 10 | 2 | 8 | 476.0 |
| line-2-0367-0379-s008141 | 8 | 2 | 6 | 357.0 |
| line-2-0510-0397-s011150 | 8 | 4 | 4 | 238.0 |
| line-2-0653-0415-s014159 | 8 | 2 | 6 | 357.0 |
| line-2-0804-0434-s017337 | 4 | 2 | 2 | 119.0 |
| line-3-0259-1031-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0349-0776-s007011 | 12 | 2 | 10 | 595.0 |
| line-3-0426-0665-s010033 | 12 | 2 | 10 | 595.0 |
| line-3-0522-0528-s013779 | 12 | 2 | 10 | 595.0 |
| line-3-0581-0443-s016073 | 12 | 2 | 10 | 595.0 |
| line-3-0658-0332-s019095 | 10 | 2 | 8 | 476.0 |
| line-3-0729-0230-s021864 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Tabuk/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
