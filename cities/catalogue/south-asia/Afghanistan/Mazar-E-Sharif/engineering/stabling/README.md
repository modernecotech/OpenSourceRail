# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 136 at depots = 170 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0426-0909-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 6 |
| line-2-0809-0030-s023005 | line-2 | declared-depot | 60 | 3,570.0 | 10 |
| line-3-0801-0064-s000000 | line-3 | declared-depot | 48 | 2,856.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0426-0909-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0446-0747-s003499 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0747-s003499 | station | reverse | revenue | 1 |
| line-1 | line-1-0449-0573-s007004 | station | forward | revenue | 1 |
| line-1 | line-1-0449-0573-s007004 | station | reverse | revenue | 1 |
| line-1 | line-1-0451-0471-s009061 | station | forward | revenue | 1 |
| line-1 | line-1-0451-0471-s009061 | station | reverse | revenue | 1 |
| line-1 | line-1-0452-0368-s011129 | station | forward | revenue | 1 |
| line-1 | line-1-0452-0368-s011129 | station | reverse | revenue | 1 |
| line-1 | line-1-0454-0266-s013186 | station | reverse | revenue | 2 |
| line-2 | line-2-0528-0892-s003130 | station | forward | revenue | 1 |
| line-2 | line-2-0528-0892-s003130 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0988-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0591-0661-s008277 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0661-s008277 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0527-s011287 | station | forward | revenue | 1 |
| line-2 | line-2-0628-0527-s011287 | station | reverse | revenue | 1 |
| line-2 | line-2-0809-0030-s023005 | station | reverse | revenue | 2 |
| line-3 | line-3-0461-0845-s019385 | station | reverse | revenue | 2 |
| line-3 | line-3-0509-0752-s017080 | station | forward | revenue | 1 |
| line-3 | line-3-0509-0752-s017080 | station | reverse | revenue | 1 |
| line-3 | line-3-0571-0631-s014065 | station | forward | revenue | 1 |
| line-3 | line-3-0571-0631-s014065 | station | reverse | revenue | 1 |
| line-3 | line-3-0633-0510-s011037 | station | forward | revenue | 1 |
| line-3 | line-3-0633-0510-s011037 | station | reverse | revenue | 1 |
| line-3 | line-3-0716-0349-s007013 | station | forward | revenue | 1 |
| line-3 | line-3-0716-0349-s007013 | station | reverse | revenue | 1 |
| line-3 | line-3-0801-0064-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0426-0909-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0426-0909-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0426-0909-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0809-0030-s023005 | depot | — | revenue | 53 |
| line-2 | line-2-0809-0030-s023005 | depot | — | spare | 6 |
| line-2 | line-2-0809-0030-s023005 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0801-0064-s000000 | depot | — | revenue | 42 |
| line-3 | line-3-0801-0064-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0801-0064-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mazar-e-sharif-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **170 trainsets at 17 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **153 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **136 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0426-0909-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0446-0747-s003499 | forward | revenue | 4 | pending |
| line-1 | line-1-0446-0747-s003499 | reverse | revenue | 4 | pending |
| line-1 | line-1-0449-0573-s007004 | forward | revenue | 4 | pending |
| line-1 | line-1-0449-0573-s007004 | reverse | revenue | 4 | pending |
| line-1 | line-1-0451-0471-s009061 | forward | revenue | 4 | pending |
| line-1 | line-1-0451-0471-s009061 | reverse | revenue | 3 | pending |
| line-1 | line-1-0452-0368-s011129 | forward | revenue | 3 | pending |
| line-1 | line-1-0452-0368-s011129 | reverse | revenue | 3 | pending |
| line-1 | line-1-0454-0266-s013186 | reverse | revenue | 3 | pending |
| line-1 | line-1-0451-0471-s009061 | reverse | spare | 1 | pending |
| line-1 | line-1-0452-0368-s011129 | forward | spare | 1 | pending |
| line-1 | line-1-0452-0368-s011129 | reverse | spare | 1 | pending |
| line-1 | line-1-0454-0266-s013186 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0528-0892-s003130 | forward | revenue | 8 | pending |
| line-2 | line-2-0528-0892-s003130 | reverse | revenue | 8 | pending |
| line-2 | line-2-0591-0661-s008277 | forward | revenue | 8 | pending |
| line-2 | line-2-0591-0661-s008277 | reverse | revenue | 8 | pending |
| line-2 | line-2-0628-0527-s011287 | forward | revenue | 8 | pending |
| line-2 | line-2-0628-0527-s011287 | reverse | revenue | 8 | pending |
| line-2 | line-2-0809-0030-s023005 | reverse | revenue | 7 | pending |
| line-2 | line-2-0809-0030-s023005 | reverse | spare | 1 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0892-s003130 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0892-s003130 | reverse | spare | 1 | pending |
| line-2 | line-2-0591-0661-s008277 | forward | spare | 1 | pending |
| line-2 | line-2-0591-0661-s008277 | reverse | spare | 1 | pending |
| line-2 | line-2-0628-0527-s011287 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0801-0064-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0716-0349-s007013 | forward | revenue | 6 | pending |
| line-3 | line-3-0716-0349-s007013 | reverse | revenue | 6 | pending |
| line-3 | line-3-0633-0510-s011037 | forward | revenue | 6 | pending |
| line-3 | line-3-0633-0510-s011037 | reverse | revenue | 5 | pending |
| line-3 | line-3-0571-0631-s014065 | forward | revenue | 5 | pending |
| line-3 | line-3-0571-0631-s014065 | reverse | revenue | 5 | pending |
| line-3 | line-3-0509-0752-s017080 | forward | revenue | 5 | pending |
| line-3 | line-3-0509-0752-s017080 | reverse | revenue | 5 | pending |
| line-3 | line-3-0461-0845-s019385 | reverse | revenue | 5 | pending |
| line-3 | line-3-0633-0510-s011037 | reverse | spare | 1 | pending |
| line-3 | line-3-0571-0631-s014065 | forward | spare | 1 | pending |
| line-3 | line-3-0571-0631-s014065 | reverse | spare | 1 | pending |
| line-3 | line-3-0509-0752-s017080 | forward | spare | 1 | pending |
| line-3 | line-3-0509-0752-s017080 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0845-s019385 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**132 trainsets exceed the reference platform envelope**, requiring **7,854.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0426-0909-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0446-0747-s003499 | 8 | 2 | 6 | 357.0 |
| line-1-0449-0573-s007004 | 8 | 2 | 6 | 357.0 |
| line-1-0451-0471-s009061 | 8 | 2 | 6 | 357.0 |
| line-1-0452-0368-s011129 | 8 | 2 | 6 | 357.0 |
| line-1-0454-0266-s013186 | 4 | 2 | 2 | 119.0 |
| line-2-0528-0892-s003130 | 18 | 2 | 16 | 952.0 |
| line-2-0569-0988-s000000 | 9 | 2 | 7 | 416.5 |
| line-2-0591-0661-s008277 | 18 | 2 | 16 | 952.0 |
| line-2-0628-0527-s011287 | 17 | 4 | 13 | 773.5 |
| line-2-0809-0030-s023005 | 8 | 2 | 6 | 357.0 |
| line-3-0461-0845-s019385 | 6 | 2 | 4 | 238.0 |
| line-3-0509-0752-s017080 | 12 | 2 | 10 | 595.0 |
| line-3-0571-0631-s014065 | 12 | 2 | 10 | 595.0 |
| line-3-0633-0510-s011037 | 12 | 4 | 8 | 476.0 |
| line-3-0716-0349-s007013 | 12 | 2 | 10 | 595.0 |
| line-3-0801-0064-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Mazar-E-Sharif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
