# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 14 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0723-0394-s000000 | forward | 4 | pending |
| line-1 | line-1-0612-0513-s004472 | forward | 4 | pending |
| line-1 | line-1-0612-0513-s004472 | reverse | 4 | pending |
| line-1 | line-1-0552-0554-s006754 | forward | 4 | pending |
| line-1 | line-1-0552-0554-s006754 | reverse | 4 | pending |
| line-1 | line-1-0557-0650-s009110 | forward | 3 | pending |
| line-1 | line-1-0557-0650-s009110 | reverse | 3 | pending |
| line-1 | line-1-0606-0725-s011475 | forward | 3 | pending |
| line-1 | line-1-0606-0725-s011475 | reverse | 3 | pending |
| line-1 | line-1-0549-0917-s016203 | reverse | 3 | pending |
| line-2 | line-2-0451-0393-s000000 | forward | 3 | pending |
| line-2 | line-2-0515-0488-s003003 | forward | 3 | pending |
| line-2 | line-2-0515-0488-s003003 | reverse | 3 | pending |
| line-2 | line-2-0552-0554-s005451 | forward | 3 | pending |
| line-2 | line-2-0552-0554-s005451 | reverse | 3 | pending |
| line-2 | line-2-0590-0601-s007459 | forward | 3 | pending |
| line-2 | line-2-0590-0601-s007459 | reverse | 3 | pending |
| line-2 | line-2-0671-0611-s009469 | reverse | 2 | pending |
| line-3 | line-3-0527-0619-s000000 | forward | 5 | pending |
| line-3 | line-3-0552-0554-s001818 | forward | 5 | pending |
| line-3 | line-3-0552-0554-s001818 | reverse | 4 | pending |
| line-3 | line-3-0720-0400-s008357 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Uyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
