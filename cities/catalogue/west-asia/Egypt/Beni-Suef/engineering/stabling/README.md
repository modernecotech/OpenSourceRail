# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **87 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0863-0492-s000000 | forward | 3 | pending |
| line-1 | line-1-0763-0503-s003005 | forward | 3 | pending |
| line-1 | line-1-0763-0503-s003005 | reverse | 3 | pending |
| line-1 | line-1-0677-0589-s006011 | forward | 3 | pending |
| line-1 | line-1-0677-0589-s006011 | reverse | 3 | pending |
| line-1 | line-1-0563-0557-s009370 | forward | 3 | pending |
| line-1 | line-1-0563-0557-s009370 | reverse | 3 | pending |
| line-1 | line-1-0572-0645-s012039 | forward | 3 | pending |
| line-1 | line-1-0572-0645-s012039 | reverse | 3 | pending |
| line-1 | line-1-0535-0739-s014436 | forward | 3 | pending |
| line-1 | line-1-0535-0739-s014436 | reverse | 3 | pending |
| line-1 | line-1-0485-0820-s016810 | reverse | 3 | pending |
| line-2 | line-2-0365-0585-s000000 | forward | 3 | pending |
| line-2 | line-2-0456-0571-s002175 | forward | 3 | pending |
| line-2 | line-2-0456-0571-s002175 | reverse | 3 | pending |
| line-2 | line-2-0563-0557-s005110 | forward | 3 | pending |
| line-2 | line-2-0563-0557-s005110 | reverse | 3 | pending |
| line-2 | line-2-0617-0523-s008192 | forward | 3 | pending |
| line-2 | line-2-0617-0523-s008192 | reverse | 3 | pending |
| line-2 | line-2-0741-0466-s011194 | forward | 3 | pending |
| line-2 | line-2-0741-0466-s011194 | reverse | 3 | pending |
| line-2 | line-2-0815-0443-s013638 | reverse | 3 | pending |
| line-3 | line-3-0514-0433-s000000 | forward | 4 | pending |
| line-3 | line-3-0563-0557-s003724 | forward | 4 | pending |
| line-3 | line-3-0563-0557-s003724 | reverse | 4 | pending |
| line-3 | line-3-0639-0620-s006034 | forward | 3 | pending |
| line-3 | line-3-0639-0620-s006034 | reverse | 3 | pending |
| line-3 | line-3-0667-0751-s009502 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Beni-Suef/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
