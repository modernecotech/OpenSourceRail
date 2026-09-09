# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **146 trainsets at 27 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1016-0841-s000000 | forward | 4 | pending |
| line-1 | line-1-0868-0745-s004866 | forward | 4 | pending |
| line-1 | line-1-0868-0745-s004866 | reverse | 4 | pending |
| line-1 | line-1-0780-0651-s007886 | forward | 4 | pending |
| line-1 | line-1-0780-0651-s007886 | reverse | 4 | pending |
| line-1 | line-1-0680-0558-s010891 | forward | 4 | pending |
| line-1 | line-1-0680-0558-s010891 | reverse | 4 | pending |
| line-1 | line-1-0564-0520-s013654 | forward | 4 | pending |
| line-1 | line-1-0564-0520-s013654 | reverse | 4 | pending |
| line-1 | line-1-0543-0416-s016911 | forward | 4 | pending |
| line-1 | line-1-0543-0416-s016911 | reverse | 4 | pending |
| line-1 | line-1-0511-0352-s018915 | forward | 4 | pending |
| line-1 | line-1-0511-0352-s018915 | reverse | 3 | pending |
| line-1 | line-1-0432-0240-s022459 | forward | 3 | pending |
| line-1 | line-1-0432-0240-s022459 | reverse | 3 | pending |
| line-1 | line-1-0230-0021-s029341 | reverse | 3 | pending |
| line-2 | line-2-0301-0299-s000000 | forward | 3 | pending |
| line-2 | line-2-0360-0341-s002085 | forward | 3 | pending |
| line-2 | line-2-0360-0341-s002085 | reverse | 3 | pending |
| line-2 | line-2-0443-0415-s005101 | forward | 3 | pending |
| line-2 | line-2-0443-0415-s005101 | reverse | 3 | pending |
| line-2 | line-2-0483-0509-s008121 | forward | 3 | pending |
| line-2 | line-2-0483-0509-s008121 | reverse | 3 | pending |
| line-2 | line-2-0564-0520-s010715 | forward | 3 | pending |
| line-2 | line-2-0564-0520-s010715 | reverse | 3 | pending |
| line-2 | line-2-0578-0643-s014156 | forward | 3 | pending |
| line-2 | line-2-0578-0643-s014156 | reverse | 3 | pending |
| line-2 | line-2-0675-0680-s016402 | forward | 3 | pending |
| line-2 | line-2-0675-0680-s016402 | reverse | 3 | pending |
| line-2 | line-2-0728-0757-s018651 | forward | 3 | pending |
| line-2 | line-2-0728-0757-s018651 | reverse | 2 | pending |
| line-2 | line-2-0718-0840-s020886 | reverse | 2 | pending |
| line-3 | line-3-0938-0427-s000000 | forward | 3 | pending |
| line-3 | line-3-0837-0439-s003018 | forward | 3 | pending |
| line-3 | line-3-0837-0439-s003018 | reverse | 3 | pending |
| line-3 | line-3-0748-0486-s005655 | forward | 3 | pending |
| line-3 | line-3-0748-0486-s005655 | reverse | 3 | pending |
| line-3 | line-3-0639-0479-s008673 | forward | 3 | pending |
| line-3 | line-3-0639-0479-s008673 | reverse | 3 | pending |
| line-3 | line-3-0564-0520-s010812 | forward | 3 | pending |
| line-3 | line-3-0564-0520-s010812 | reverse | 2 | pending |
| line-3 | line-3-0493-0593-s012872 | forward | 2 | pending |
| line-3 | line-3-0493-0593-s012872 | reverse | 2 | pending |
| line-3 | line-3-0405-0560-s014922 | forward | 2 | pending |
| line-3 | line-3-0405-0560-s014922 | reverse | 2 | pending |
| line-3 | line-3-0315-0530-s016971 | forward | 2 | pending |
| line-3 | line-3-0315-0530-s016971 | reverse | 2 | pending |
| line-3 | line-3-0250-0578-s019019 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Buraidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
