# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **110 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0514-0823-s000000 | forward | 4 | pending |
| line-1 | line-1-0531-0681-s003004 | forward | 4 | pending |
| line-1 | line-1-0531-0681-s003004 | reverse | 4 | pending |
| line-1 | line-1-0542-0545-s006122 | forward | 4 | pending |
| line-1 | line-1-0542-0545-s006122 | reverse | 4 | pending |
| line-1 | line-1-0434-0492-s009012 | forward | 4 | pending |
| line-1 | line-1-0434-0492-s009012 | reverse | 3 | pending |
| line-1 | line-1-0480-0391-s012029 | forward | 3 | pending |
| line-1 | line-1-0480-0391-s012029 | reverse | 3 | pending |
| line-1 | line-1-0433-0325-s013925 | forward | 3 | pending |
| line-1 | line-1-0433-0325-s013925 | reverse | 3 | pending |
| line-1 | line-1-0244-0147-s019613 | reverse | 3 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | 4 | pending |
| line-2 | line-2-0375-0555-s003372 | forward | 3 | pending |
| line-2 | line-2-0375-0555-s003372 | reverse | 3 | pending |
| line-2 | line-2-0481-0485-s006392 | forward | 3 | pending |
| line-2 | line-2-0481-0485-s006392 | reverse | 3 | pending |
| line-2 | line-2-0542-0545-s009491 | forward | 3 | pending |
| line-2 | line-2-0542-0545-s009491 | reverse | 3 | pending |
| line-2 | line-2-0630-0515-s012030 | forward | 3 | pending |
| line-2 | line-2-0630-0515-s012030 | reverse | 3 | pending |
| line-2 | line-2-0702-0472-s014571 | reverse | 3 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | 5 | pending |
| line-3 | line-3-0519-0441-s003002 | forward | 5 | pending |
| line-3 | line-3-0519-0441-s003002 | reverse | 5 | pending |
| line-3 | line-3-0542-0545-s005466 | forward | 5 | pending |
| line-3 | line-3-0542-0545-s005466 | reverse | 5 | pending |
| line-3 | line-3-0458-0677-s009039 | forward | 4 | pending |
| line-3 | line-3-0458-0677-s009039 | reverse | 4 | pending |
| line-3 | line-3-0223-0982-s017121 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Polokwane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
