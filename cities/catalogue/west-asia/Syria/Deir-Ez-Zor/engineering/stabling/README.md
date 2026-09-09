# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **143 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0317-0298-s000000 | forward | 6 | pending |
| line-1 | line-1-0427-0403-s003692 | forward | 6 | pending |
| line-1 | line-1-0427-0403-s003692 | reverse | 6 | pending |
| line-1 | line-1-0492-0477-s005734 | forward | 6 | pending |
| line-1 | line-1-0492-0477-s005734 | reverse | 6 | pending |
| line-1 | line-1-0544-0551-s007781 | forward | 6 | pending |
| line-1 | line-1-0544-0551-s007781 | reverse | 6 | pending |
| line-1 | line-1-0664-0635-s011294 | forward | 6 | pending |
| line-1 | line-1-0664-0635-s011294 | reverse | 6 | pending |
| line-1 | line-1-0910-0952-s021694 | reverse | 5 | pending |
| line-2 | line-2-0173-0684-s000000 | forward | 5 | pending |
| line-2 | line-2-0396-0636-s005662 | forward | 5 | pending |
| line-2 | line-2-0396-0636-s005662 | reverse | 5 | pending |
| line-2 | line-2-0468-0565-s007690 | forward | 5 | pending |
| line-2 | line-2-0468-0565-s007690 | reverse | 5 | pending |
| line-2 | line-2-0544-0551-s009692 | forward | 5 | pending |
| line-2 | line-2-0544-0551-s009692 | reverse | 4 | pending |
| line-2 | line-2-0636-0421-s013379 | reverse | 4 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | 8 | pending |
| line-3 | line-3-0479-0670-s010030 | forward | 8 | pending |
| line-3 | line-3-0479-0670-s010030 | reverse | 8 | pending |
| line-3 | line-3-0544-0551-s013264 | forward | 8 | pending |
| line-3 | line-3-0544-0551-s013264 | reverse | 7 | pending |
| line-3 | line-3-0586-0425-s016293 | reverse | 7 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Deir-Ez-Zor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
