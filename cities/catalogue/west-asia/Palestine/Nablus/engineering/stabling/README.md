# Station and depot overnight allocation

Plan: **36 trainsets at stations + 138 at depots = 174 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0071-0128-s028312 | 138 | 8,211.0 | 27 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0528-0122-s020455 | station | reverse | revenue | 2 |
| line-1 | line-1-0534-0459-s010651 | station | forward | revenue | 1 |
| line-1 | line-1-0534-0459-s010651 | station | reverse | revenue | 1 |
| line-1 | line-1-0541-0831-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0548-0557-s007130 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0557-s007130 | station | reverse | revenue | 1 |
| line-1 | line-1-0577-0633-s005066 | station | forward | revenue | 1 |
| line-1 | line-1-0577-0633-s005066 | station | reverse | revenue | 1 |
| line-1 | line-1-0578-0720-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0578-0720-s003005 | station | reverse | revenue | 1 |
| line-2 | line-2-0071-0128-s028312 | station | reverse | revenue | 2 |
| line-2 | line-2-0387-0440-s016842 | station | forward | revenue | 1 |
| line-2 | line-2-0387-0440-s016842 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0551-s013336 | station | forward | revenue | 1 |
| line-2 | line-2-0462-0551-s013336 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0557-s010828 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0557-s010828 | station | reverse | revenue | 1 |
| line-2 | line-2-0621-0635-s007918 | station | forward | revenue | 1 |
| line-2 | line-2-0621-0635-s007918 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0776-s004913 | station | forward | revenue | 1 |
| line-2 | line-2-0628-0776-s004913 | station | reverse | revenue | 1 |
| line-2 | line-2-0783-0930-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0065-1031-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0423-0670-s014038 | station | forward | revenue | 1 |
| line-3 | line-3-0423-0670-s014038 | station | reverse | revenue | 1 |
| line-3 | line-3-0511-0653-s017089 | station | forward | revenue | 1 |
| line-3 | line-3-0511-0653-s017089 | station | reverse | revenue | 1 |
| line-3 | line-3-0548-0557-s019585 | station | forward | revenue | 1 |
| line-3 | line-3-0548-0557-s019585 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0454-s022961 | station | reverse | revenue | 2 |
| line-1 | line-2-0071-0128-s028312 | depot | — | revenue | 33 |
| line-1 | line-2-0071-0128-s028312 | depot | — | spare | 4 |
| line-1 | line-2-0071-0128-s028312 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0071-0128-s028312 | depot | — | revenue | 46 |
| line-2 | line-2-0071-0128-s028312 | depot | — | spare | 6 |
| line-2 | line-2-0071-0128-s028312 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0071-0128-s028312 | depot | — | revenue | 41 |
| line-3 | line-2-0071-0128-s028312 | depot | — | spare | 5 |
| line-3 | line-2-0071-0128-s028312 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (38 trains), line-3 (47 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **174 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **156 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **138 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0541-0831-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0578-0720-s003005 | forward | revenue | 5 | pending |
| line-1 | line-1-0578-0720-s003005 | reverse | revenue | 5 | pending |
| line-1 | line-1-0577-0633-s005066 | forward | revenue | 5 | pending |
| line-1 | line-1-0577-0633-s005066 | reverse | revenue | 5 | pending |
| line-1 | line-1-0548-0557-s007130 | forward | revenue | 4 | pending |
| line-1 | line-1-0548-0557-s007130 | reverse | revenue | 4 | pending |
| line-1 | line-1-0534-0459-s010651 | forward | revenue | 4 | pending |
| line-1 | line-1-0534-0459-s010651 | reverse | revenue | 4 | pending |
| line-1 | line-1-0528-0122-s020455 | reverse | revenue | 4 | pending |
| line-1 | line-1-0548-0557-s007130 | forward | spare | 1 | pending |
| line-1 | line-1-0548-0557-s007130 | reverse | spare | 1 | pending |
| line-1 | line-1-0534-0459-s010651 | forward | spare | 1 | pending |
| line-1 | line-1-0534-0459-s010651 | reverse | spare | 1 | pending |
| line-1 | line-1-0528-0122-s020455 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0783-0930-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0628-0776-s004913 | forward | revenue | 5 | pending |
| line-2 | line-2-0628-0776-s004913 | reverse | revenue | 5 | pending |
| line-2 | line-2-0621-0635-s007918 | forward | revenue | 5 | pending |
| line-2 | line-2-0621-0635-s007918 | reverse | revenue | 5 | pending |
| line-2 | line-2-0548-0557-s010828 | forward | revenue | 5 | pending |
| line-2 | line-2-0548-0557-s010828 | reverse | revenue | 5 | pending |
| line-2 | line-2-0462-0551-s013336 | forward | revenue | 5 | pending |
| line-2 | line-2-0462-0551-s013336 | reverse | revenue | 5 | pending |
| line-2 | line-2-0387-0440-s016842 | forward | revenue | 5 | pending |
| line-2 | line-2-0387-0440-s016842 | reverse | revenue | 5 | pending |
| line-2 | line-2-0071-0128-s028312 | reverse | revenue | 5 | pending |
| line-2 | line-2-0783-0930-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0628-0776-s004913 | forward | spare | 1 | pending |
| line-2 | line-2-0628-0776-s004913 | reverse | spare | 1 | pending |
| line-2 | line-2-0621-0635-s007918 | forward | spare | 1 | pending |
| line-2 | line-2-0621-0635-s007918 | reverse | spare | 1 | pending |
| line-2 | line-2-0548-0557-s010828 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0557-s010828 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0065-1031-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0423-0670-s014038 | forward | revenue | 7 | pending |
| line-3 | line-3-0423-0670-s014038 | reverse | revenue | 7 | pending |
| line-3 | line-3-0511-0653-s017089 | forward | revenue | 6 | pending |
| line-3 | line-3-0511-0653-s017089 | reverse | revenue | 6 | pending |
| line-3 | line-3-0548-0557-s019585 | forward | revenue | 6 | pending |
| line-3 | line-3-0548-0557-s019585 | reverse | revenue | 6 | pending |
| line-3 | line-3-0667-0454-s022961 | reverse | revenue | 6 | pending |
| line-3 | line-3-0511-0653-s017089 | forward | spare | 1 | pending |
| line-3 | line-3-0511-0653-s017089 | reverse | spare | 1 | pending |
| line-3 | line-3-0548-0557-s019585 | forward | spare | 1 | pending |
| line-3 | line-3-0548-0557-s019585 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0454-s022961 | reverse | spare | 1 | pending |
| line-3 | line-3-0065-1031-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**132 trainsets exceed the reference platform envelope**, requiring **7,854.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0528-0122-s020455 | 5 | 2 | 3 | 178.5 |
| line-1-0534-0459-s010651 | 10 | 2 | 8 | 476.0 |
| line-1-0541-0831-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0548-0557-s007130 | 10 | 4 | 6 | 357.0 |
| line-1-0577-0633-s005066 | 10 | 2 | 8 | 476.0 |
| line-1-0578-0720-s003005 | 10 | 2 | 8 | 476.0 |
| line-2-0071-0128-s028312 | 5 | 2 | 3 | 178.5 |
| line-2-0387-0440-s016842 | 10 | 2 | 8 | 476.0 |
| line-2-0462-0551-s013336 | 10 | 2 | 8 | 476.0 |
| line-2-0548-0557-s010828 | 12 | 4 | 8 | 476.0 |
| line-2-0621-0635-s007918 | 12 | 2 | 10 | 595.0 |
| line-2-0628-0776-s004913 | 12 | 2 | 10 | 595.0 |
| line-2-0783-0930-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0065-1031-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0423-0670-s014038 | 14 | 2 | 12 | 714.0 |
| line-3-0511-0653-s017089 | 14 | 2 | 12 | 714.0 |
| line-3-0548-0557-s019585 | 14 | 4 | 10 | 595.0 |
| line-3-0667-0454-s022961 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Nablus/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
