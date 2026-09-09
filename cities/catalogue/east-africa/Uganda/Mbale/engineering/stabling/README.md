# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **71 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0539-0355-s000000 | forward | 3 | pending |
| line-1 | line-1-0432-0333-s003009 | forward | 3 | pending |
| line-1 | line-1-0432-0333-s003009 | reverse | 3 | pending |
| line-1 | line-1-0307-0259-s007546 | forward | 3 | pending |
| line-1 | line-1-0307-0259-s007546 | reverse | 3 | pending |
| line-1 | line-1-0331-0344-s009495 | forward | 3 | pending |
| line-1 | line-1-0331-0344-s009495 | reverse | 3 | pending |
| line-1 | line-1-0255-0370-s011994 | forward | 3 | pending |
| line-1 | line-1-0255-0370-s011994 | reverse | 3 | pending |
| line-1 | line-1-0176-0341-s014506 | reverse | 3 | pending |
| line-2 | line-2-0075-0508-s000000 | forward | 5 | pending |
| line-2 | line-2-0264-0427-s005234 | forward | 5 | pending |
| line-2 | line-2-0264-0427-s005234 | reverse | 5 | pending |
| line-2 | line-2-0362-0447-s008254 | forward | 5 | pending |
| line-2 | line-2-0362-0447-s008254 | reverse | 4 | pending |
| line-2 | line-2-0513-0369-s014439 | reverse | 4 | pending |
| line-3 | line-3-0318-0463-s000000 | forward | 4 | pending |
| line-3 | line-3-0369-0375-s002512 | forward | 3 | pending |
| line-3 | line-3-0369-0375-s002512 | reverse | 3 | pending |
| line-3 | line-3-0290-0295-s005200 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
