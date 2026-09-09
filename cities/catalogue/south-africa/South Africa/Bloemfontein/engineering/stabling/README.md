# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **151 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1080-1059-s000000 | forward | 4 | pending |
| line-1 | line-1-0959-1016-s003005 | forward | 4 | pending |
| line-1 | line-1-0959-1016-s003005 | reverse | 4 | pending |
| line-1 | line-1-0877-0886-s007616 | forward | 4 | pending |
| line-1 | line-1-0877-0886-s007616 | reverse | 3 | pending |
| line-1 | line-1-0859-0814-s010631 | forward | 3 | pending |
| line-1 | line-1-0859-0814-s010631 | reverse | 3 | pending |
| line-1 | line-1-0755-0765-s013621 | forward | 3 | pending |
| line-1 | line-1-0755-0765-s013621 | reverse | 3 | pending |
| line-1 | line-1-0694-0758-s015238 | forward | 3 | pending |
| line-1 | line-1-0694-0758-s015238 | reverse | 3 | pending |
| line-1 | line-1-0650-0679-s017230 | forward | 3 | pending |
| line-1 | line-1-0650-0679-s017230 | reverse | 3 | pending |
| line-1 | line-1-0601-0608-s019200 | forward | 3 | pending |
| line-1 | line-1-0601-0608-s019200 | reverse | 3 | pending |
| line-1 | line-1-0521-0642-s021277 | forward | 3 | pending |
| line-1 | line-1-0521-0642-s021277 | reverse | 3 | pending |
| line-1 | line-1-0279-0546-s027348 | reverse | 3 | pending |
| line-2 | line-2-0231-0235-s000000 | forward | 4 | pending |
| line-2 | line-2-0447-0441-s006681 | forward | 4 | pending |
| line-2 | line-2-0447-0441-s006681 | reverse | 4 | pending |
| line-2 | line-2-0537-0554-s009698 | forward | 4 | pending |
| line-2 | line-2-0537-0554-s009698 | reverse | 4 | pending |
| line-2 | line-2-0601-0608-s011956 | forward | 3 | pending |
| line-2 | line-2-0601-0608-s011956 | reverse | 3 | pending |
| line-2 | line-2-0671-0575-s013843 | forward | 3 | pending |
| line-2 | line-2-0671-0575-s013843 | reverse | 3 | pending |
| line-2 | line-2-0697-0638-s015721 | forward | 3 | pending |
| line-2 | line-2-0697-0638-s015721 | reverse | 3 | pending |
| line-2 | line-2-0786-0640-s018724 | forward | 3 | pending |
| line-2 | line-2-0786-0640-s018724 | reverse | 3 | pending |
| line-2 | line-2-0887-0707-s021725 | forward | 3 | pending |
| line-2 | line-2-0887-0707-s021725 | reverse | 3 | pending |
| line-2 | line-2-0977-0745-s025897 | reverse | 3 | pending |
| line-3 | line-3-0483-0904-s000000 | forward | 4 | pending |
| line-3 | line-3-0541-0855-s003016 | forward | 4 | pending |
| line-3 | line-3-0541-0855-s003016 | reverse | 4 | pending |
| line-3 | line-3-0515-0724-s006028 | forward | 4 | pending |
| line-3 | line-3-0515-0724-s006028 | reverse | 3 | pending |
| line-3 | line-3-0521-0643-s008032 | forward | 3 | pending |
| line-3 | line-3-0521-0643-s008032 | reverse | 3 | pending |
| line-3 | line-3-0601-0608-s010044 | forward | 3 | pending |
| line-3 | line-3-0601-0608-s010044 | reverse | 3 | pending |
| line-3 | line-3-0641-0536-s012048 | forward | 3 | pending |
| line-3 | line-3-0641-0536-s012048 | reverse | 3 | pending |
| line-3 | line-3-0871-0509-s018854 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Bloemfontein/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
