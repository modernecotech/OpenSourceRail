# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **83 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1075-0511-s000000 | forward | 4 | pending |
| line-1 | line-1-0770-0521-s006315 | forward | 4 | pending |
| line-1 | line-1-0770-0521-s006315 | reverse | 4 | pending |
| line-1 | line-1-0630-0522-s009317 | forward | 4 | pending |
| line-1 | line-1-0630-0522-s009317 | reverse | 3 | pending |
| line-1 | line-1-0565-0552-s012200 | forward | 3 | pending |
| line-1 | line-1-0565-0552-s012200 | reverse | 3 | pending |
| line-1 | line-1-0505-0592-s014231 | forward | 3 | pending |
| line-1 | line-1-0505-0592-s014231 | reverse | 3 | pending |
| line-1 | line-1-0446-0663-s016266 | forward | 3 | pending |
| line-1 | line-1-0446-0663-s016266 | reverse | 3 | pending |
| line-1 | line-1-0386-0735-s018290 | reverse | 3 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | 5 | pending |
| line-2 | line-2-0565-0552-s003689 | forward | 4 | pending |
| line-2 | line-2-0565-0552-s003689 | reverse | 4 | pending |
| line-2 | line-2-0601-0621-s006014 | forward | 4 | pending |
| line-2 | line-2-0601-0621-s006014 | reverse | 4 | pending |
| line-2 | line-2-0668-0828-s011646 | reverse | 4 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | 3 | pending |
| line-3 | line-3-0658-0610-s003020 | forward | 3 | pending |
| line-3 | line-3-0658-0610-s003020 | reverse | 3 | pending |
| line-3 | line-3-0565-0552-s006096 | forward | 3 | pending |
| line-3 | line-3-0565-0552-s006096 | reverse | 3 | pending |
| line-3 | line-3-0595-0487-s008120 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lobito/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
