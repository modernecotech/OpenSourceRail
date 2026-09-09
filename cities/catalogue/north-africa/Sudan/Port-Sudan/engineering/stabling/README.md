# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 15 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0362-0552-s000000 | forward | 3 | pending |
| line-1 | line-1-0457-0581-s003006 | forward | 3 | pending |
| line-1 | line-1-0457-0581-s003006 | reverse | 3 | pending |
| line-1 | line-1-0549-0550-s005560 | forward | 3 | pending |
| line-1 | line-1-0549-0550-s005560 | reverse | 3 | pending |
| line-1 | line-1-0646-0565-s007685 | forward | 3 | pending |
| line-1 | line-1-0646-0565-s007685 | reverse | 3 | pending |
| line-1 | line-1-0770-0523-s010586 | forward | 3 | pending |
| line-1 | line-1-0770-0523-s010586 | reverse | 3 | pending |
| line-1 | line-1-0902-0530-s013478 | reverse | 3 | pending |
| line-2 | line-2-0443-0413-s000000 | forward | 4 | pending |
| line-2 | line-2-0515-0479-s003009 | forward | 4 | pending |
| line-2 | line-2-0515-0479-s003009 | reverse | 3 | pending |
| line-2 | line-2-0549-0550-s005256 | forward | 3 | pending |
| line-2 | line-2-0549-0550-s005256 | reverse | 3 | pending |
| line-2 | line-2-0627-0505-s007851 | forward | 3 | pending |
| line-2 | line-2-0627-0505-s007851 | reverse | 3 | pending |
| line-2 | line-2-0777-0508-s011295 | reverse | 3 | pending |
| line-3 | line-3-0489-0673-s000000 | forward | 4 | pending |
| line-3 | line-3-0549-0550-s003425 | forward | 4 | pending |
| line-3 | line-3-0549-0550-s003425 | reverse | 3 | pending |
| line-3 | line-3-0617-0589-s005735 | forward | 3 | pending |
| line-3 | line-3-0617-0589-s005735 | reverse | 3 | pending |
| line-3 | line-3-0761-0556-s009113 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Port-Sudan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
