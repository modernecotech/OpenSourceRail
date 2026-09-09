# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **90 trainsets at 14 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0782-0630-s000000 | forward | 6 | pending |
| line-1 | line-1-0683-0576-s003011 | forward | 6 | pending |
| line-1 | line-1-0683-0576-s003011 | reverse | 5 | pending |
| line-1 | line-1-0550-0551-s006258 | forward | 5 | pending |
| line-1 | line-1-0550-0551-s006258 | reverse | 5 | pending |
| line-1 | line-1-0468-0579-s009044 | forward | 5 | pending |
| line-1 | line-1-0468-0579-s009044 | reverse | 5 | pending |
| line-1 | line-1-0051-0779-s020226 | reverse | 5 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | 4 | pending |
| line-2 | line-2-0655-0372-s003843 | forward | 4 | pending |
| line-2 | line-2-0655-0372-s003843 | reverse | 4 | pending |
| line-2 | line-2-0556-0466-s006851 | forward | 3 | pending |
| line-2 | line-2-0556-0466-s006851 | reverse | 3 | pending |
| line-2 | line-2-0550-0551-s009106 | forward | 3 | pending |
| line-2 | line-2-0550-0551-s009106 | reverse | 3 | pending |
| line-2 | line-2-0550-0694-s012837 | reverse | 3 | pending |
| line-3 | line-3-0771-0652-s000000 | forward | 4 | pending |
| line-3 | line-3-0645-0645-s003015 | forward | 4 | pending |
| line-3 | line-3-0645-0645-s003015 | reverse | 4 | pending |
| line-3 | line-3-0550-0551-s005933 | forward | 3 | pending |
| line-3 | line-3-0550-0551-s005933 | reverse | 3 | pending |
| line-3 | line-3-0482-0431-s009479 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Kumba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
