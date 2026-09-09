# Station and depot overnight allocation

Plan: **44 trainsets at stations + 78 at depots = 122 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0540-0838-s020428 | 78 | 4,641.0 | 19 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0539-0432-s008415 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0432-s008415 | station | reverse | revenue | 1 |
| line-1 | line-1-0564-0233-s013017 | station | forward | revenue | 1 |
| line-1 | line-1-0564-0233-s013017 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0376-s009996 | station | forward | revenue | 1 |
| line-1 | line-1-0566-0376-s009996 | station | reverse | revenue | 1 |
| line-1 | line-1-0584-0017-s018536 | station | reverse | revenue | 2 |
| line-1 | line-1-0588-0118-s015762 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0118-s015762 | station | reverse | revenue | 1 |
| line-1 | line-1-0595-0461-s006984 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0461-s006984 | station | reverse | revenue | 1 |
| line-1 | line-1-0651-0583-s003970 | station | forward | revenue | 1 |
| line-1 | line-1-0651-0583-s003970 | station | reverse | revenue | 1 |
| line-1 | line-1-0682-0744-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0515-0486-s009049 | station | forward | revenue | 1 |
| line-2 | line-2-0515-0486-s009049 | station | reverse | revenue | 1 |
| line-2 | line-2-0523-0228-s003005 | station | forward | revenue | 1 |
| line-2 | line-2-0523-0228-s003005 | station | reverse | revenue | 1 |
| line-2 | line-2-0530-0094-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0533-0854-s018320 | station | reverse | revenue | 2 |
| line-2 | line-2-0539-0432-s007556 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0432-s007556 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0366-s006029 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0366-s006029 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0667-s013673 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0667-s013673 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0432-s010654 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0432-s010654 | station | reverse | revenue | 1 |
| line-3 | line-3-0540-0838-s020428 | station | reverse | revenue | 2 |
| line-3 | line-3-0599-0530-s013111 | station | forward | revenue | 1 |
| line-3 | line-3-0599-0530-s013111 | station | reverse | revenue | 1 |
| line-3 | line-3-0599-0652-s015551 | station | forward | revenue | 1 |
| line-3 | line-3-0599-0652-s015551 | station | reverse | revenue | 1 |
| line-3 | line-3-0617-0353-s007711 | station | forward | revenue | 1 |
| line-3 | line-3-0617-0353-s007711 | station | reverse | revenue | 1 |
| line-3 | line-3-0638-0211-s004697 | station | forward | revenue | 1 |
| line-3 | line-3-0638-0211-s004697 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0007-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0540-0838-s020428 | depot | — | revenue | 20 |
| line-1 | line-3-0540-0838-s020428 | depot | — | spare | 3 |
| line-1 | line-3-0540-0838-s020428 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0540-0838-s020428 | depot | — | revenue | 22 |
| line-2 | line-3-0540-0838-s020428 | depot | — | spare | 3 |
| line-2 | line-3-0540-0838-s020428 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0540-0838-s020428 | depot | — | revenue | 24 |
| line-3 | line-3-0540-0838-s020428 | depot | — | spare | 3 |
| line-3 | line-3-0540-0838-s020428 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (24 trains), line-2 (26 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **122 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **110 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **78 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0682-0744-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0651-0583-s003970 | forward | revenue | 3 | pending |
| line-1 | line-1-0651-0583-s003970 | reverse | revenue | 3 | pending |
| line-1 | line-1-0595-0461-s006984 | forward | revenue | 3 | pending |
| line-1 | line-1-0595-0461-s006984 | reverse | revenue | 3 | pending |
| line-1 | line-1-0539-0432-s008415 | forward | revenue | 3 | pending |
| line-1 | line-1-0539-0432-s008415 | reverse | revenue | 3 | pending |
| line-1 | line-1-0566-0376-s009996 | forward | revenue | 3 | pending |
| line-1 | line-1-0566-0376-s009996 | reverse | revenue | 2 | pending |
| line-1 | line-1-0564-0233-s013017 | forward | revenue | 2 | pending |
| line-1 | line-1-0564-0233-s013017 | reverse | revenue | 2 | pending |
| line-1 | line-1-0588-0118-s015762 | forward | revenue | 2 | pending |
| line-1 | line-1-0588-0118-s015762 | reverse | revenue | 2 | pending |
| line-1 | line-1-0584-0017-s018536 | reverse | revenue | 2 | pending |
| line-1 | line-1-0566-0376-s009996 | reverse | spare | 1 | pending |
| line-1 | line-1-0564-0233-s013017 | forward | spare | 1 | pending |
| line-1 | line-1-0564-0233-s013017 | reverse | spare | 1 | pending |
| line-1 | line-1-0588-0118-s015762 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0523-0228-s003005 | forward | revenue | 3 | pending |
| line-2 | line-2-0523-0228-s003005 | reverse | revenue | 3 | pending |
| line-2 | line-2-0542-0366-s006029 | forward | revenue | 3 | pending |
| line-2 | line-2-0542-0366-s006029 | reverse | revenue | 3 | pending |
| line-2 | line-2-0539-0432-s007556 | forward | revenue | 3 | pending |
| line-2 | line-2-0539-0432-s007556 | reverse | revenue | 3 | pending |
| line-2 | line-2-0515-0486-s009049 | forward | revenue | 3 | pending |
| line-2 | line-2-0515-0486-s009049 | reverse | revenue | 3 | pending |
| line-2 | line-2-0543-0667-s013673 | forward | revenue | 3 | pending |
| line-2 | line-2-0543-0667-s013673 | reverse | revenue | 3 | pending |
| line-2 | line-2-0533-0854-s018320 | reverse | revenue | 3 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0523-0228-s003005 | forward | spare | 1 | pending |
| line-2 | line-2-0523-0228-s003005 | reverse | spare | 1 | pending |
| line-2 | line-2-0542-0366-s006029 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0658-0007-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0638-0211-s004697 | forward | revenue | 4 | pending |
| line-3 | line-3-0638-0211-s004697 | reverse | revenue | 3 | pending |
| line-3 | line-3-0617-0353-s007711 | forward | revenue | 3 | pending |
| line-3 | line-3-0617-0353-s007711 | reverse | revenue | 3 | pending |
| line-3 | line-3-0539-0432-s010654 | forward | revenue | 3 | pending |
| line-3 | line-3-0539-0432-s010654 | reverse | revenue | 3 | pending |
| line-3 | line-3-0599-0530-s013111 | forward | revenue | 3 | pending |
| line-3 | line-3-0599-0530-s013111 | reverse | revenue | 3 | pending |
| line-3 | line-3-0599-0652-s015551 | forward | revenue | 3 | pending |
| line-3 | line-3-0599-0652-s015551 | reverse | revenue | 3 | pending |
| line-3 | line-3-0540-0838-s020428 | reverse | revenue | 3 | pending |
| line-3 | line-3-0638-0211-s004697 | reverse | spare | 1 | pending |
| line-3 | line-3-0617-0353-s007711 | forward | spare | 1 | pending |
| line-3 | line-3-0617-0353-s007711 | reverse | spare | 1 | pending |
| line-3 | line-3-0539-0432-s010654 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**68 trainsets exceed the reference platform envelope**, requiring **4,046.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0539-0432-s008415 | 6 | 4 | 2 | 119.0 |
| line-1-0564-0233-s013017 | 6 | 2 | 4 | 238.0 |
| line-1-0566-0376-s009996 | 6 | 4 | 2 | 119.0 |
| line-1-0584-0017-s018536 | 2 | 2 | 0 | 0.0 |
| line-1-0588-0118-s015762 | 5 | 2 | 3 | 178.5 |
| line-1-0595-0461-s006984 | 6 | 2 | 4 | 238.0 |
| line-1-0651-0583-s003970 | 6 | 2 | 4 | 238.0 |
| line-1-0682-0744-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0515-0486-s009049 | 6 | 2 | 4 | 238.0 |
| line-2-0523-0228-s003005 | 8 | 2 | 6 | 357.0 |
| line-2-0530-0094-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0533-0854-s018320 | 3 | 2 | 1 | 59.5 |
| line-2-0539-0432-s007556 | 6 | 4 | 2 | 119.0 |
| line-2-0542-0366-s006029 | 7 | 4 | 3 | 178.5 |
| line-2-0543-0667-s013673 | 6 | 2 | 4 | 238.0 |
| line-3-0539-0432-s010654 | 7 | 4 | 3 | 178.5 |
| line-3-0540-0838-s020428 | 3 | 2 | 1 | 59.5 |
| line-3-0599-0530-s013111 | 6 | 2 | 4 | 238.0 |
| line-3-0599-0652-s015551 | 6 | 2 | 4 | 238.0 |
| line-3-0617-0353-s007711 | 8 | 2 | 6 | 357.0 |
| line-3-0638-0211-s004697 | 8 | 2 | 6 | 357.0 |
| line-3-0658-0007-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Duhok/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
