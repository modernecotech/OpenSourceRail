# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **106 trainsets at 17 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0428-1076-s000000 | forward | 4 | pending |
| line-1 | line-1-0516-0762-s007009 | forward | 3 | pending |
| line-1 | line-1-0516-0762-s007009 | reverse | 3 | pending |
| line-1 | line-1-0567-0633-s010012 | forward | 3 | pending |
| line-1 | line-1-0567-0633-s010012 | reverse | 3 | pending |
| line-1 | line-1-0555-0556-s011952 | forward | 3 | pending |
| line-1 | line-1-0555-0556-s011952 | reverse | 3 | pending |
| line-1 | line-1-0536-0476-s014010 | forward | 3 | pending |
| line-1 | line-1-0536-0476-s014010 | reverse | 3 | pending |
| line-1 | line-1-0587-0404-s016057 | forward | 3 | pending |
| line-1 | line-1-0587-0404-s016057 | reverse | 3 | pending |
| line-1 | line-1-0532-0335-s018386 | forward | 3 | pending |
| line-1 | line-1-0532-0335-s018386 | reverse | 3 | pending |
| line-1 | line-1-0588-0273-s020690 | reverse | 3 | pending |
| line-2 | line-2-0363-0499-s000000 | forward | 4 | pending |
| line-2 | line-2-0468-0556-s003002 | forward | 4 | pending |
| line-2 | line-2-0468-0556-s003002 | reverse | 4 | pending |
| line-2 | line-2-0555-0556-s005417 | forward | 3 | pending |
| line-2 | line-2-0555-0556-s005417 | reverse | 3 | pending |
| line-2 | line-2-0615-0436-s009024 | forward | 3 | pending |
| line-2 | line-2-0615-0436-s009024 | reverse | 3 | pending |
| line-2 | line-2-0738-0390-s012729 | reverse | 3 | pending |
| line-3 | line-3-0717-0651-s000000 | forward | 6 | pending |
| line-3 | line-3-0697-0571-s003016 | forward | 6 | pending |
| line-3 | line-3-0697-0571-s003016 | reverse | 6 | pending |
| line-3 | line-3-0768-0382-s007964 | forward | 6 | pending |
| line-3 | line-3-0768-0382-s007964 | reverse | 6 | pending |
| line-3 | line-3-0796-0040-s016430 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Diwaniyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
