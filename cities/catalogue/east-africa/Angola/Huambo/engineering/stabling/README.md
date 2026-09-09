# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **112 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0511-0215-s000000 | forward | 4 | pending |
| line-1 | line-1-0539-0388-s004796 | forward | 4 | pending |
| line-1 | line-1-0539-0388-s004796 | reverse | 4 | pending |
| line-1 | line-1-0523-0500-s007801 | forward | 4 | pending |
| line-1 | line-1-0523-0500-s007801 | reverse | 4 | pending |
| line-1 | line-1-0550-0556-s010080 | forward | 4 | pending |
| line-1 | line-1-0550-0556-s010080 | reverse | 4 | pending |
| line-1 | line-1-0534-0600-s011356 | forward | 3 | pending |
| line-1 | line-1-0534-0600-s011356 | reverse | 3 | pending |
| line-1 | line-1-0460-0664-s014369 | forward | 3 | pending |
| line-1 | line-1-0460-0664-s014369 | reverse | 3 | pending |
| line-1 | line-1-0411-0756-s016697 | forward | 3 | pending |
| line-1 | line-1-0411-0756-s016697 | reverse | 3 | pending |
| line-1 | line-1-0361-1048-s023668 | reverse | 3 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | 3 | pending |
| line-2 | line-2-0478-0698-s003016 | forward | 3 | pending |
| line-2 | line-2-0478-0698-s003016 | reverse | 3 | pending |
| line-2 | line-2-0568-0618-s006041 | forward | 3 | pending |
| line-2 | line-2-0568-0618-s006041 | reverse | 3 | pending |
| line-2 | line-2-0550-0556-s007868 | forward | 3 | pending |
| line-2 | line-2-0550-0556-s007868 | reverse | 3 | pending |
| line-2 | line-2-0603-0472-s010373 | forward | 3 | pending |
| line-2 | line-2-0603-0472-s010373 | reverse | 2 | pending |
| line-2 | line-2-0698-0421-s012883 | reverse | 2 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | 4 | pending |
| line-3 | line-3-0397-0590-s003013 | forward | 4 | pending |
| line-3 | line-3-0397-0590-s003013 | reverse | 4 | pending |
| line-3 | line-3-0474-0588-s005030 | forward | 4 | pending |
| line-3 | line-3-0474-0588-s005030 | reverse | 4 | pending |
| line-3 | line-3-0550-0556-s007044 | forward | 3 | pending |
| line-3 | line-3-0550-0556-s007044 | reverse | 3 | pending |
| line-3 | line-3-0630-0588-s009041 | forward | 3 | pending |
| line-3 | line-3-0630-0588-s009041 | reverse | 3 | pending |
| line-3 | line-3-0883-0735-s015872 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Huambo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
