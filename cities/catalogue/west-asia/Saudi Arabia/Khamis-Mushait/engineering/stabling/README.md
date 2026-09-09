# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **217 trainsets at 25 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **195 revenue, 19 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1093-0994-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0902-0838-s005711 | forward | revenue | 5 | pending |
| line-1 | line-1-0902-0838-s005711 | reverse | revenue | 5 | pending |
| line-1 | line-1-0783-0768-s009656 | forward | revenue | 5 | pending |
| line-1 | line-1-0783-0768-s009656 | reverse | revenue | 5 | pending |
| line-1 | line-1-0753-0643-s012656 | forward | revenue | 5 | pending |
| line-1 | line-1-0753-0643-s012656 | reverse | revenue | 4 | pending |
| line-1 | line-1-0640-0560-s015674 | forward | revenue | 4 | pending |
| line-1 | line-1-0640-0560-s015674 | reverse | revenue | 4 | pending |
| line-1 | line-1-0558-0544-s017967 | forward | revenue | 4 | pending |
| line-1 | line-1-0558-0544-s017967 | reverse | revenue | 4 | pending |
| line-1 | line-1-0500-0469-s020426 | forward | revenue | 4 | pending |
| line-1 | line-1-0500-0469-s020426 | reverse | revenue | 4 | pending |
| line-1 | line-1-0398-0392-s023444 | forward | revenue | 4 | pending |
| line-1 | line-1-0398-0392-s023444 | reverse | revenue | 4 | pending |
| line-1 | line-1-0215-0272-s029101 | reverse | revenue | 4 | pending |
| line-1 | line-1-0753-0643-s012656 | reverse | spare | 1 | pending |
| line-1 | line-1-0640-0560-s015674 | forward | spare | 1 | pending |
| line-1 | line-1-0640-0560-s015674 | reverse | spare | 1 | pending |
| line-1 | line-1-0558-0544-s017967 | forward | spare | 1 | pending |
| line-1 | line-1-0558-0544-s017967 | reverse | spare | 1 | pending |
| line-1 | line-1-0500-0469-s020426 | forward | spare | 1 | pending |
| line-1 | line-1-0500-0469-s020426 | reverse | spare | 1 | pending |
| line-1 | line-1-0398-0392-s023444 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0761-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004323 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004323 | reverse | revenue | 5 | pending |
| line-2 | line-2-0786-0557-s007519 | forward | revenue | 5 | pending |
| line-2 | line-2-0786-0557-s007519 | reverse | revenue | 5 | pending |
| line-2 | line-2-0698-0471-s010912 | forward | revenue | 5 | pending |
| line-2 | line-2-0698-0471-s010912 | reverse | revenue | 5 | pending |
| line-2 | line-2-0573-0413-s013916 | forward | revenue | 5 | pending |
| line-2 | line-2-0573-0413-s013916 | reverse | revenue | 5 | pending |
| line-2 | line-2-0520-0326-s016926 | forward | revenue | 5 | pending |
| line-2 | line-2-0520-0326-s016926 | reverse | revenue | 5 | pending |
| line-2 | line-2-0284-0038-s025542 | reverse | revenue | 5 | pending |
| line-2 | line-2-0834-0685-s004323 | reverse | spare | 1 | pending |
| line-2 | line-2-0786-0557-s007519 | forward | spare | 1 | pending |
| line-2 | line-2-0786-0557-s007519 | reverse | spare | 1 | pending |
| line-2 | line-2-0698-0471-s010912 | forward | spare | 1 | pending |
| line-2 | line-2-0698-0471-s010912 | reverse | spare | 1 | pending |
| line-2 | line-2-0573-0413-s013916 | forward | spare | 1 | pending |
| line-2 | line-2-0573-0413-s013916 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0315-0464-s003009 | forward | revenue | 4 | pending |
| line-3 | line-3-0315-0464-s003009 | reverse | revenue | 4 | pending |
| line-3 | line-3-0423-0552-s006015 | forward | revenue | 4 | pending |
| line-3 | line-3-0423-0552-s006015 | reverse | revenue | 4 | pending |
| line-3 | line-3-0507-0584-s008065 | forward | revenue | 4 | pending |
| line-3 | line-3-0507-0584-s008065 | reverse | revenue | 4 | pending |
| line-3 | line-3-0558-0544-s010119 | forward | revenue | 4 | pending |
| line-3 | line-3-0558-0544-s010119 | reverse | revenue | 4 | pending |
| line-3 | line-3-0636-0634-s013660 | forward | revenue | 4 | pending |
| line-3 | line-3-0636-0634-s013660 | reverse | revenue | 4 | pending |
| line-3 | line-3-0711-0748-s017179 | forward | revenue | 4 | pending |
| line-3 | line-3-0711-0748-s017179 | reverse | revenue | 4 | pending |
| line-3 | line-3-0834-0853-s020673 | forward | revenue | 4 | pending |
| line-3 | line-3-0834-0853-s020673 | reverse | revenue | 4 | pending |
| line-3 | line-3-1002-1014-s026523 | reverse | revenue | 3 | pending |
| line-3 | line-3-1002-1014-s026523 | reverse | spare | 1 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0315-0464-s003009 | forward | spare | 1 | pending |
| line-3 | line-3-0315-0464-s003009 | reverse | spare | 1 | pending |
| line-3 | line-3-0423-0552-s006015 | forward | spare | 1 | pending |
| line-3 | line-3-0423-0552-s006015 | reverse | spare | 1 | pending |
| line-3 | line-3-0507-0584-s008065 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**163 trainsets exceed the reference platform envelope**, requiring **9,698.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0272-s029101 | 4 | 2 | 2 | 119.0 |
| line-1-0398-0392-s023444 | 9 | 2 | 7 | 416.5 |
| line-1-0500-0469-s020426 | 10 | 2 | 8 | 476.0 |
| line-1-0558-0544-s017967 | 10 | 4 | 6 | 357.0 |
| line-1-0640-0560-s015674 | 10 | 2 | 8 | 476.0 |
| line-1-0753-0643-s012656 | 10 | 2 | 8 | 476.0 |
| line-1-0783-0768-s009656 | 10 | 2 | 8 | 476.0 |
| line-1-0902-0838-s005711 | 10 | 2 | 8 | 476.0 |
| line-1-1093-0994-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0284-0038-s025542 | 5 | 2 | 3 | 178.5 |
| line-2-0520-0326-s016926 | 10 | 2 | 8 | 476.0 |
| line-2-0573-0413-s013916 | 12 | 2 | 10 | 595.0 |
| line-2-0698-0471-s010912 | 12 | 2 | 10 | 595.0 |
| line-2-0786-0557-s007519 | 12 | 2 | 10 | 595.0 |
| line-2-0834-0685-s004323 | 12 | 2 | 10 | 595.0 |
| line-2-0980-0761-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0198-0413-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0315-0464-s003009 | 10 | 2 | 8 | 476.0 |
| line-3-0423-0552-s006015 | 10 | 2 | 8 | 476.0 |
| line-3-0507-0584-s008065 | 9 | 2 | 7 | 416.5 |
| line-3-0558-0544-s010119 | 8 | 4 | 4 | 238.0 |
| line-3-0636-0634-s013660 | 8 | 2 | 6 | 357.0 |
| line-3-0711-0748-s017179 | 8 | 2 | 6 | 357.0 |
| line-3-0834-0853-s020673 | 8 | 2 | 6 | 357.0 |
| line-3-1002-1014-s026523 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Khamis-Mushait/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
