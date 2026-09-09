# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **109 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0781-0662-s000000 | forward | 4 | pending |
| line-1 | line-1-0654-0606-s003004 | forward | 4 | pending |
| line-1 | line-1-0654-0606-s003004 | reverse | 4 | pending |
| line-1 | line-1-0551-0555-s005808 | forward | 4 | pending |
| line-1 | line-1-0551-0555-s005808 | reverse | 4 | pending |
| line-1 | line-1-0408-0552-s009496 | forward | 3 | pending |
| line-1 | line-1-0408-0552-s009496 | reverse | 3 | pending |
| line-1 | line-1-0292-0628-s013161 | reverse | 3 | pending |
| line-2 | line-2-0399-0719-s000000 | forward | 3 | pending |
| line-2 | line-2-0483-0638-s003012 | forward | 3 | pending |
| line-2 | line-2-0483-0638-s003012 | reverse | 3 | pending |
| line-2 | line-2-0527-0595-s004624 | forward | 3 | pending |
| line-2 | line-2-0527-0595-s004624 | reverse | 3 | pending |
| line-2 | line-2-0551-0555-s005829 | forward | 3 | pending |
| line-2 | line-2-0551-0555-s005829 | reverse | 3 | pending |
| line-2 | line-2-0550-0485-s007646 | forward | 3 | pending |
| line-2 | line-2-0550-0485-s007646 | reverse | 2 | pending |
| line-2 | line-2-0536-0322-s013191 | reverse | 2 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | 5 | pending |
| line-3 | line-3-0467-0764-s004228 | forward | 5 | pending |
| line-3 | line-3-0467-0764-s004228 | reverse | 5 | pending |
| line-3 | line-3-0531-0648-s007232 | forward | 5 | pending |
| line-3 | line-3-0531-0648-s007232 | reverse | 4 | pending |
| line-3 | line-3-0551-0555-s009420 | forward | 4 | pending |
| line-3 | line-3-0551-0555-s009420 | reverse | 4 | pending |
| line-3 | line-3-0624-0526-s011320 | forward | 4 | pending |
| line-3 | line-3-0624-0526-s011320 | reverse | 4 | pending |
| line-3 | line-3-0694-0520-s013248 | forward | 4 | pending |
| line-3 | line-3-0694-0520-s013248 | reverse | 4 | pending |
| line-3 | line-3-1100-0131-s025287 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mansoura-Eg/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
