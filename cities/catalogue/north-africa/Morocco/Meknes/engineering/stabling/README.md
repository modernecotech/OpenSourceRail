# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **89 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0413-0831-s000000 | forward | 4 | pending |
| line-1 | line-1-0528-0695-s004699 | forward | 4 | pending |
| line-1 | line-1-0528-0695-s004699 | reverse | 4 | pending |
| line-1 | line-1-0554-0548-s008298 | forward | 4 | pending |
| line-1 | line-1-0554-0548-s008298 | reverse | 4 | pending |
| line-1 | line-1-0622-0498-s010717 | forward | 3 | pending |
| line-1 | line-1-0622-0498-s010717 | reverse | 3 | pending |
| line-1 | line-1-0658-0424-s013218 | forward | 3 | pending |
| line-1 | line-1-0658-0424-s013218 | reverse | 3 | pending |
| line-1 | line-1-0763-0392-s015726 | reverse | 3 | pending |
| line-2 | line-2-0324-0563-s000000 | forward | 4 | pending |
| line-2 | line-2-0440-0601-s003013 | forward | 4 | pending |
| line-2 | line-2-0440-0601-s003013 | reverse | 4 | pending |
| line-2 | line-2-0554-0548-s006728 | forward | 3 | pending |
| line-2 | line-2-0554-0548-s006728 | reverse | 3 | pending |
| line-2 | line-2-0627-0616-s009041 | forward | 3 | pending |
| line-2 | line-2-0627-0616-s009041 | reverse | 3 | pending |
| line-2 | line-2-0755-0613-s012219 | reverse | 3 | pending |
| line-3 | line-3-0769-0485-s000000 | forward | 3 | pending |
| line-3 | line-3-0686-0519-s003006 | forward | 3 | pending |
| line-3 | line-3-0686-0519-s003006 | reverse | 3 | pending |
| line-3 | line-3-0627-0572-s004966 | forward | 3 | pending |
| line-3 | line-3-0627-0572-s004966 | reverse | 3 | pending |
| line-3 | line-3-0554-0548-s006912 | forward | 3 | pending |
| line-3 | line-3-0554-0548-s006912 | reverse | 3 | pending |
| line-3 | line-3-0514-0476-s009039 | forward | 2 | pending |
| line-3 | line-3-0514-0476-s009039 | reverse | 2 | pending |
| line-3 | line-3-0436-0420-s011413 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Meknes/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
