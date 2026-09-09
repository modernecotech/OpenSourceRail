# Station and depot overnight allocation

Plan: **48 trainsets at stations + 124 at depots = 172 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0215-0118-s029940 | 124 | 7,378.0 | 26 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0118-s029940 | station | reverse | revenue | 2 |
| line-1 | line-1-0481-0473-s018319 | station | forward | revenue | 1 |
| line-1 | line-1-0481-0473-s018319 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0569-s014899 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0569-s014899 | station | reverse | revenue | 1 |
| line-1 | line-1-0572-0613-s013697 | station | forward | revenue | 1 |
| line-1 | line-1-0572-0613-s013697 | station | reverse | revenue | 1 |
| line-1 | line-1-0640-0735-s010694 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0735-s010694 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0819-s007187 | station | forward | revenue | 1 |
| line-1 | line-1-0707-0819-s007187 | station | reverse | revenue | 1 |
| line-1 | line-1-0831-0909-s003666 | station | forward | revenue | 1 |
| line-1 | line-1-0831-0909-s003666 | station | reverse | revenue | 1 |
| line-1 | line-1-0914-1037-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0265-0473-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0359-0514-s003014 | station | forward | revenue | 1 |
| line-2 | line-2-0359-0514-s003014 | station | reverse | revenue | 1 |
| line-2 | line-2-0472-0540-s006022 | station | forward | revenue | 1 |
| line-2 | line-2-0472-0540-s006022 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0569-s009213 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0569-s009213 | station | reverse | revenue | 1 |
| line-2 | line-2-0612-0683-s012043 | station | forward | revenue | 1 |
| line-2 | line-2-0612-0683-s012043 | station | reverse | revenue | 1 |
| line-2 | line-2-0772-0824-s016976 | station | forward | revenue | 1 |
| line-2 | line-2-0772-0824-s016976 | station | reverse | revenue | 1 |
| line-2 | line-2-0806-0953-s019987 | station | forward | revenue | 1 |
| line-2 | line-2-0806-0953-s019987 | station | reverse | revenue | 1 |
| line-2 | line-2-0894-1095-s023828 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0477-0389-s004837 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0389-s004837 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0569-s010839 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0569-s010839 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0481-s007854 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0481-s007854 | station | reverse | revenue | 1 |
| line-3 | line-3-0618-0684-s013796 | station | forward | revenue | 1 |
| line-3 | line-3-0618-0684-s013796 | station | reverse | revenue | 1 |
| line-3 | line-3-0753-0780-s017303 | station | forward | revenue | 1 |
| line-3 | line-3-0753-0780-s017303 | station | reverse | revenue | 1 |
| line-3 | line-3-0871-0894-s020812 | station | forward | revenue | 1 |
| line-3 | line-3-0871-0894-s020812 | station | reverse | revenue | 1 |
| line-3 | line-3-1082-1083-s027433 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0118-s029940 | depot | — | revenue | 41 |
| line-1 | line-1-0215-0118-s029940 | depot | — | spare | 5 |
| line-1 | line-1-0215-0118-s029940 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0215-0118-s029940 | depot | — | revenue | 30 |
| line-2 | line-1-0215-0118-s029940 | depot | — | spare | 4 |
| line-2 | line-1-0215-0118-s029940 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0215-0118-s029940 | depot | — | revenue | 36 |
| line-3 | line-1-0215-0118-s029940 | depot | — | spare | 5 |
| line-3 | line-1-0215-0118-s029940 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (35 trains), line-3 (42 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **172 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **155 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **124 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0914-1037-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0831-0909-s003666 | forward | revenue | 4 | pending |
| line-1 | line-1-0831-0909-s003666 | reverse | revenue | 4 | pending |
| line-1 | line-1-0707-0819-s007187 | forward | revenue | 4 | pending |
| line-1 | line-1-0707-0819-s007187 | reverse | revenue | 4 | pending |
| line-1 | line-1-0640-0735-s010694 | forward | revenue | 4 | pending |
| line-1 | line-1-0640-0735-s010694 | reverse | revenue | 4 | pending |
| line-1 | line-1-0572-0613-s013697 | forward | revenue | 4 | pending |
| line-1 | line-1-0572-0613-s013697 | reverse | revenue | 4 | pending |
| line-1 | line-1-0561-0569-s014899 | forward | revenue | 4 | pending |
| line-1 | line-1-0561-0569-s014899 | reverse | revenue | 4 | pending |
| line-1 | line-1-0481-0473-s018319 | forward | revenue | 4 | pending |
| line-1 | line-1-0481-0473-s018319 | reverse | revenue | 4 | pending |
| line-1 | line-1-0215-0118-s029940 | reverse | revenue | 4 | pending |
| line-1 | line-1-0831-0909-s003666 | forward | spare | 1 | pending |
| line-1 | line-1-0831-0909-s003666 | reverse | spare | 1 | pending |
| line-1 | line-1-0707-0819-s007187 | forward | spare | 1 | pending |
| line-1 | line-1-0707-0819-s007187 | reverse | spare | 1 | pending |
| line-1 | line-1-0640-0735-s010694 | forward | spare | 1 | pending |
| line-1 | line-1-0640-0735-s010694 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0359-0514-s003014 | forward | revenue | 4 | pending |
| line-2 | line-2-0359-0514-s003014 | reverse | revenue | 4 | pending |
| line-2 | line-2-0472-0540-s006022 | forward | revenue | 4 | pending |
| line-2 | line-2-0472-0540-s006022 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0569-s009213 | forward | revenue | 3 | pending |
| line-2 | line-2-0561-0569-s009213 | reverse | revenue | 3 | pending |
| line-2 | line-2-0612-0683-s012043 | forward | revenue | 3 | pending |
| line-2 | line-2-0612-0683-s012043 | reverse | revenue | 3 | pending |
| line-2 | line-2-0772-0824-s016976 | forward | revenue | 3 | pending |
| line-2 | line-2-0772-0824-s016976 | reverse | revenue | 3 | pending |
| line-2 | line-2-0806-0953-s019987 | forward | revenue | 3 | pending |
| line-2 | line-2-0806-0953-s019987 | reverse | revenue | 3 | pending |
| line-2 | line-2-0894-1095-s023828 | reverse | revenue | 3 | pending |
| line-2 | line-2-0472-0540-s006022 | reverse | spare | 1 | pending |
| line-2 | line-2-0561-0569-s009213 | forward | spare | 1 | pending |
| line-2 | line-2-0561-0569-s009213 | reverse | spare | 1 | pending |
| line-2 | line-2-0612-0683-s012043 | forward | spare | 1 | pending |
| line-2 | line-2-0612-0683-s012043 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0477-0389-s004837 | forward | revenue | 4 | pending |
| line-3 | line-3-0477-0389-s004837 | reverse | revenue | 4 | pending |
| line-3 | line-3-0567-0481-s007854 | forward | revenue | 4 | pending |
| line-3 | line-3-0567-0481-s007854 | reverse | revenue | 4 | pending |
| line-3 | line-3-0561-0569-s010839 | forward | revenue | 4 | pending |
| line-3 | line-3-0561-0569-s010839 | reverse | revenue | 4 | pending |
| line-3 | line-3-0618-0684-s013796 | forward | revenue | 4 | pending |
| line-3 | line-3-0618-0684-s013796 | reverse | revenue | 4 | pending |
| line-3 | line-3-0753-0780-s017303 | forward | revenue | 4 | pending |
| line-3 | line-3-0753-0780-s017303 | reverse | revenue | 3 | pending |
| line-3 | line-3-0871-0894-s020812 | forward | revenue | 3 | pending |
| line-3 | line-3-0871-0894-s020812 | reverse | revenue | 3 | pending |
| line-3 | line-3-1082-1083-s027433 | reverse | revenue | 3 | pending |
| line-3 | line-3-0753-0780-s017303 | reverse | spare | 1 | pending |
| line-3 | line-3-0871-0894-s020812 | forward | spare | 1 | pending |
| line-3 | line-3-0871-0894-s020812 | reverse | spare | 1 | pending |
| line-3 | line-3-1082-1083-s027433 | reverse | spare | 1 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0477-0389-s004837 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**114 trainsets exceed the reference platform envelope**, requiring **6,783.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0118-s029940 | 4 | 2 | 2 | 119.0 |
| line-1-0481-0473-s018319 | 8 | 2 | 6 | 357.0 |
| line-1-0561-0569-s014899 | 8 | 4 | 4 | 238.0 |
| line-1-0572-0613-s013697 | 8 | 2 | 6 | 357.0 |
| line-1-0640-0735-s010694 | 10 | 2 | 8 | 476.0 |
| line-1-0707-0819-s007187 | 10 | 2 | 8 | 476.0 |
| line-1-0831-0909-s003666 | 10 | 2 | 8 | 476.0 |
| line-1-0914-1037-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0265-0473-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0359-0514-s003014 | 8 | 2 | 6 | 357.0 |
| line-2-0472-0540-s006022 | 8 | 2 | 6 | 357.0 |
| line-2-0561-0569-s009213 | 8 | 4 | 4 | 238.0 |
| line-2-0612-0683-s012043 | 8 | 4 | 4 | 238.0 |
| line-2-0772-0824-s016976 | 6 | 2 | 4 | 238.0 |
| line-2-0806-0953-s019987 | 6 | 2 | 4 | 238.0 |
| line-2-0894-1095-s023828 | 3 | 2 | 1 | 59.5 |
| line-3-0383-0212-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0477-0389-s004837 | 9 | 2 | 7 | 416.5 |
| line-3-0561-0569-s010839 | 8 | 4 | 4 | 238.0 |
| line-3-0567-0481-s007854 | 8 | 2 | 6 | 357.0 |
| line-3-0618-0684-s013796 | 8 | 4 | 4 | 238.0 |
| line-3-0753-0780-s017303 | 8 | 2 | 6 | 357.0 |
| line-3-0871-0894-s020812 | 8 | 2 | 6 | 357.0 |
| line-3-1082-1083-s027433 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Pokhara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
