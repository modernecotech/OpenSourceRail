# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **172 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0914-1037-s000000 | forward | 5 | pending |
| line-1 | line-1-0831-0909-s003666 | forward | 5 | pending |
| line-1 | line-1-0831-0909-s003666 | reverse | 5 | pending |
| line-1 | line-1-0707-0819-s007187 | forward | 5 | pending |
| line-1 | line-1-0707-0819-s007187 | reverse | 5 | pending |
| line-1 | line-1-0640-0735-s010694 | forward | 5 | pending |
| line-1 | line-1-0640-0735-s010694 | reverse | 5 | pending |
| line-1 | line-1-0572-0613-s013697 | forward | 4 | pending |
| line-1 | line-1-0572-0613-s013697 | reverse | 4 | pending |
| line-1 | line-1-0561-0569-s014899 | forward | 4 | pending |
| line-1 | line-1-0561-0569-s014899 | reverse | 4 | pending |
| line-1 | line-1-0481-0473-s018319 | forward | 4 | pending |
| line-1 | line-1-0481-0473-s018319 | reverse | 4 | pending |
| line-1 | line-1-0215-0118-s029940 | reverse | 4 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | 4 | pending |
| line-2 | line-2-0359-0514-s003014 | forward | 4 | pending |
| line-2 | line-2-0359-0514-s003014 | reverse | 4 | pending |
| line-2 | line-2-0472-0540-s006022 | forward | 4 | pending |
| line-2 | line-2-0472-0540-s006022 | reverse | 4 | pending |
| line-2 | line-2-0561-0569-s009213 | forward | 4 | pending |
| line-2 | line-2-0561-0569-s009213 | reverse | 4 | pending |
| line-2 | line-2-0612-0683-s012043 | forward | 4 | pending |
| line-2 | line-2-0612-0683-s012043 | reverse | 4 | pending |
| line-2 | line-2-0772-0824-s016976 | forward | 3 | pending |
| line-2 | line-2-0772-0824-s016976 | reverse | 3 | pending |
| line-2 | line-2-0806-0953-s019987 | forward | 3 | pending |
| line-2 | line-2-0806-0953-s019987 | reverse | 3 | pending |
| line-2 | line-2-0894-1095-s023828 | reverse | 3 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | 5 | pending |
| line-3 | line-3-0477-0389-s004837 | forward | 5 | pending |
| line-3 | line-3-0477-0389-s004837 | reverse | 4 | pending |
| line-3 | line-3-0567-0481-s007854 | forward | 4 | pending |
| line-3 | line-3-0567-0481-s007854 | reverse | 4 | pending |
| line-3 | line-3-0561-0569-s010839 | forward | 4 | pending |
| line-3 | line-3-0561-0569-s010839 | reverse | 4 | pending |
| line-3 | line-3-0618-0684-s013796 | forward | 4 | pending |
| line-3 | line-3-0618-0684-s013796 | reverse | 4 | pending |
| line-3 | line-3-0753-0780-s017303 | forward | 4 | pending |
| line-3 | line-3-0753-0780-s017303 | reverse | 4 | pending |
| line-3 | line-3-0871-0894-s020812 | forward | 4 | pending |
| line-3 | line-3-0871-0894-s020812 | reverse | 4 | pending |
| line-3 | line-3-1082-1083-s027433 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Pokhara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
