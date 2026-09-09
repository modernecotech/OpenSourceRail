# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **111 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0276-1068-s000000 | forward | 4 | pending |
| line-1 | line-1-0366-0784-s007010 | forward | 4 | pending |
| line-1 | line-1-0366-0784-s007010 | reverse | 4 | pending |
| line-1 | line-1-0469-0714-s010024 | forward | 4 | pending |
| line-1 | line-1-0469-0714-s010024 | reverse | 4 | pending |
| line-1 | line-1-0523-0624-s013043 | forward | 4 | pending |
| line-1 | line-1-0523-0624-s013043 | reverse | 3 | pending |
| line-1 | line-1-0545-0558-s014963 | forward | 3 | pending |
| line-1 | line-1-0545-0558-s014963 | reverse | 3 | pending |
| line-1 | line-1-0483-0470-s017438 | forward | 3 | pending |
| line-1 | line-1-0483-0470-s017438 | reverse | 3 | pending |
| line-1 | line-1-0492-0379-s019930 | reverse | 3 | pending |
| line-2 | line-2-0719-0761-s000000 | forward | 3 | pending |
| line-2 | line-2-0619-0657-s003002 | forward | 3 | pending |
| line-2 | line-2-0619-0657-s003002 | reverse | 3 | pending |
| line-2 | line-2-0589-0601-s004968 | forward | 3 | pending |
| line-2 | line-2-0589-0601-s004968 | reverse | 3 | pending |
| line-2 | line-2-0545-0558-s006916 | forward | 3 | pending |
| line-2 | line-2-0545-0558-s006916 | reverse | 3 | pending |
| line-2 | line-2-0453-0529-s009037 | forward | 3 | pending |
| line-2 | line-2-0453-0529-s009037 | reverse | 3 | pending |
| line-2 | line-2-0440-0416-s011743 | forward | 2 | pending |
| line-2 | line-2-0440-0416-s011743 | reverse | 2 | pending |
| line-2 | line-2-0381-0340-s014473 | forward | 2 | pending |
| line-2 | line-2-0381-0340-s014473 | reverse | 2 | pending |
| line-2 | line-2-0330-0248-s017181 | reverse | 2 | pending |
| line-3 | line-3-0132-0345-s000000 | forward | 4 | pending |
| line-3 | line-3-0341-0392-s005046 | forward | 4 | pending |
| line-3 | line-3-0341-0392-s005046 | reverse | 3 | pending |
| line-3 | line-3-0419-0476-s008048 | forward | 3 | pending |
| line-3 | line-3-0419-0476-s008048 | reverse | 3 | pending |
| line-3 | line-3-0487-0570-s011071 | forward | 3 | pending |
| line-3 | line-3-0487-0570-s011071 | reverse | 3 | pending |
| line-3 | line-3-0545-0558-s012491 | forward | 3 | pending |
| line-3 | line-3-0545-0558-s012491 | reverse | 3 | pending |
| line-3 | line-3-0593-0468-s015402 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bamenda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
