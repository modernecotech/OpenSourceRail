# Station and depot overnight allocation

Plan: **34 trainsets at stations + 76 at depots = 110 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0800-0524-s021320 | 76 | 4,522.0 | 17 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0065-1050-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0313-0830-s007005 | station | forward | revenue | 1 |
| line-1 | line-1-0313-0830-s007005 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0716-s010022 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0716-s010022 | station | reverse | revenue | 1 |
| line-1 | line-1-0498-0606-s013041 | station | forward | revenue | 1 |
| line-1 | line-1-0498-0606-s013041 | station | reverse | revenue | 1 |
| line-1 | line-1-0557-0557-s014731 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0557-s014731 | station | reverse | revenue | 1 |
| line-1 | line-1-0668-0523-s017657 | station | forward | revenue | 1 |
| line-1 | line-1-0668-0523-s017657 | station | reverse | revenue | 1 |
| line-1 | line-1-0800-0524-s021320 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0786-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0510-0661-s003022 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0661-s003022 | station | reverse | revenue | 1 |
| line-2 | line-2-0557-0557-s005787 | station | forward | revenue | 1 |
| line-2 | line-2-0557-0557-s005787 | station | reverse | revenue | 1 |
| line-2 | line-2-0632-0473-s008650 | station | forward | revenue | 1 |
| line-2 | line-2-0632-0473-s008650 | station | reverse | revenue | 1 |
| line-2 | line-2-0722-0306-s012736 | station | forward | revenue | 1 |
| line-2 | line-2-0722-0306-s012736 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0111-s016813 | station | reverse | revenue | 2 |
| line-3 | line-3-0555-0587-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0621-0596-s003018 | station | forward | revenue | 1 |
| line-3 | line-3-0621-0596-s003018 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0709-s006038 | station | forward | revenue | 1 |
| line-3 | line-3-0698-0709-s006038 | station | reverse | revenue | 1 |
| line-3 | line-3-0901-0910-s012319 | station | reverse | revenue | 2 |
| line-1 | line-1-0800-0524-s021320 | depot | — | revenue | 28 |
| line-1 | line-1-0800-0524-s021320 | depot | — | spare | 4 |
| line-1 | line-1-0800-0524-s021320 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0800-0524-s021320 | depot | — | revenue | 20 |
| line-2 | line-1-0800-0524-s021320 | depot | — | spare | 3 |
| line-2 | line-1-0800-0524-s021320 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0800-0524-s021320 | depot | — | revenue | 16 |
| line-3 | line-1-0800-0524-s021320 | depot | — | spare | 2 |
| line-3 | line-1-0800-0524-s021320 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (24 trains), line-3 (19 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **110 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **98 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **76 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0065-1050-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0313-0830-s007005 | forward | revenue | 4 | pending |
| line-1 | line-1-0313-0830-s007005 | reverse | revenue | 4 | pending |
| line-1 | line-1-0402-0716-s010022 | forward | revenue | 4 | pending |
| line-1 | line-1-0402-0716-s010022 | reverse | revenue | 4 | pending |
| line-1 | line-1-0498-0606-s013041 | forward | revenue | 4 | pending |
| line-1 | line-1-0498-0606-s013041 | reverse | revenue | 3 | pending |
| line-1 | line-1-0557-0557-s014731 | forward | revenue | 3 | pending |
| line-1 | line-1-0557-0557-s014731 | reverse | revenue | 3 | pending |
| line-1 | line-1-0668-0523-s017657 | forward | revenue | 3 | pending |
| line-1 | line-1-0668-0523-s017657 | reverse | revenue | 3 | pending |
| line-1 | line-1-0800-0524-s021320 | reverse | revenue | 3 | pending |
| line-1 | line-1-0498-0606-s013041 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0557-s014731 | forward | spare | 1 | pending |
| line-1 | line-1-0557-0557-s014731 | reverse | spare | 1 | pending |
| line-1 | line-1-0668-0523-s017657 | forward | spare | 1 | pending |
| line-1 | line-1-0668-0523-s017657 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0510-0661-s003022 | forward | revenue | 4 | pending |
| line-2 | line-2-0510-0661-s003022 | reverse | revenue | 3 | pending |
| line-2 | line-2-0557-0557-s005787 | forward | revenue | 3 | pending |
| line-2 | line-2-0557-0557-s005787 | reverse | revenue | 3 | pending |
| line-2 | line-2-0632-0473-s008650 | forward | revenue | 3 | pending |
| line-2 | line-2-0632-0473-s008650 | reverse | revenue | 3 | pending |
| line-2 | line-2-0722-0306-s012736 | forward | revenue | 3 | pending |
| line-2 | line-2-0722-0306-s012736 | reverse | revenue | 3 | pending |
| line-2 | line-2-0742-0111-s016813 | reverse | revenue | 3 | pending |
| line-2 | line-2-0510-0661-s003022 | reverse | spare | 1 | pending |
| line-2 | line-2-0557-0557-s005787 | forward | spare | 1 | pending |
| line-2 | line-2-0557-0557-s005787 | reverse | spare | 1 | pending |
| line-2 | line-2-0632-0473-s008650 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0555-0587-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0621-0596-s003018 | forward | revenue | 4 | pending |
| line-3 | line-3-0621-0596-s003018 | reverse | revenue | 4 | pending |
| line-3 | line-3-0698-0709-s006038 | forward | revenue | 4 | pending |
| line-3 | line-3-0698-0709-s006038 | reverse | revenue | 4 | pending |
| line-3 | line-3-0901-0910-s012319 | reverse | revenue | 4 | pending |
| line-3 | line-3-0555-0587-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0621-0596-s003018 | forward | spare | 1 | pending |
| line-3 | line-3-0621-0596-s003018 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**72 trainsets exceed the reference platform envelope**, requiring **4,284.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0065-1050-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0313-0830-s007005 | 8 | 2 | 6 | 357.0 |
| line-1-0402-0716-s010022 | 8 | 2 | 6 | 357.0 |
| line-1-0498-0606-s013041 | 8 | 2 | 6 | 357.0 |
| line-1-0557-0557-s014731 | 8 | 4 | 4 | 238.0 |
| line-1-0668-0523-s017657 | 8 | 2 | 6 | 357.0 |
| line-1-0800-0524-s021320 | 3 | 2 | 1 | 59.5 |
| line-2-0447-0786-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0510-0661-s003022 | 8 | 2 | 6 | 357.0 |
| line-2-0557-0557-s005787 | 8 | 4 | 4 | 238.0 |
| line-2-0632-0473-s008650 | 7 | 2 | 5 | 297.5 |
| line-2-0722-0306-s012736 | 6 | 2 | 4 | 238.0 |
| line-2-0742-0111-s016813 | 3 | 2 | 1 | 59.5 |
| line-3-0555-0587-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0621-0596-s003018 | 10 | 2 | 8 | 476.0 |
| line-3-0698-0709-s006038 | 8 | 2 | 6 | 357.0 |
| line-3-0901-0910-s012319 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Benguela/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
