# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **127 trainsets at 40 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1275-0615-s000000 | forward | 3 | pending |
| line-1 | line-1-0995-0669-s006470 | forward | 3 | pending |
| line-1 | line-1-0995-0669-s006470 | reverse | 3 | pending |
| line-1 | line-1-0975-0796-s009572 | forward | 3 | pending |
| line-1 | line-1-0975-0796-s009572 | reverse | 3 | pending |
| line-1 | line-1-0855-0802-s012589 | forward | 3 | pending |
| line-1 | line-1-0855-0802-s012589 | reverse | 2 | pending |
| line-1 | line-1-0799-0807-s014016 | forward | 2 | pending |
| line-1 | line-1-0799-0807-s014016 | reverse | 2 | pending |
| line-1 | line-1-0741-0830-s015605 | forward | 2 | pending |
| line-1 | line-1-0741-0830-s015605 | reverse | 2 | pending |
| line-1 | line-1-0681-0903-s018621 | forward | 2 | pending |
| line-1 | line-1-0681-0903-s018621 | reverse | 2 | pending |
| line-1 | line-1-0600-0949-s020890 | forward | 2 | pending |
| line-1 | line-1-0600-0949-s020890 | reverse | 2 | pending |
| line-1 | line-1-0507-0983-s023160 | forward | 2 | pending |
| line-1 | line-1-0507-0983-s023160 | reverse | 2 | pending |
| line-1 | line-1-0421-0987-s025431 | reverse | 2 | pending |
| line-2 | line-2-1119-0841-s000000 | forward | 3 | pending |
| line-2 | line-2-1046-0844-s003011 | forward | 3 | pending |
| line-2 | line-2-1046-0844-s003011 | reverse | 3 | pending |
| line-2 | line-2-0916-0893-s006028 | forward | 3 | pending |
| line-2 | line-2-0916-0893-s006028 | reverse | 3 | pending |
| line-2 | line-2-0875-0960-s008180 | forward | 3 | pending |
| line-2 | line-2-0875-0960-s008180 | reverse | 3 | pending |
| line-2 | line-2-0795-0985-s012378 | forward | 3 | pending |
| line-2 | line-2-0795-0985-s012378 | reverse | 3 | pending |
| line-2 | line-2-0742-1025-s013976 | forward | 3 | pending |
| line-2 | line-2-0742-1025-s013976 | reverse | 2 | pending |
| line-2 | line-2-0687-1108-s016369 | forward | 2 | pending |
| line-2 | line-2-0687-1108-s016369 | reverse | 2 | pending |
| line-2 | line-2-0590-1147-s018754 | forward | 2 | pending |
| line-2 | line-2-0590-1147-s018754 | reverse | 2 | pending |
| line-2 | line-2-0371-1395-s026740 | reverse | 2 | pending |
| line-3 | line-3-0939-0653-s000000 | forward | 3 | pending |
| line-3 | line-3-0864-0683-s003012 | forward | 3 | pending |
| line-3 | line-3-0864-0683-s003012 | reverse | 3 | pending |
| line-3 | line-3-0721-0694-s006029 | forward | 3 | pending |
| line-3 | line-3-0721-0694-s006029 | reverse | 3 | pending |
| line-3 | line-3-0407-0735-s012649 | forward | 3 | pending |
| line-3 | line-3-0407-0735-s012649 | reverse | 3 | pending |
| line-3 | line-3-0409-0805-s015386 | reverse | 3 | pending |
| line-4 | line-4-0419-0635-s000000 | forward | 1 | pending |
| line-4 | line-4-0419-0635-s000000 | reverse | 1 | pending |
| line-4 | line-4-0407-0735-s002206 | reverse | 1 | pending |
| line-4 | line-4-0409-0805-s003805 | reverse | 1 | pending |
| line-4 | line-4-0453-0932-s007006 | forward | 1 | pending |
| line-4 | line-4-0421-0987-s008400 | forward | 1 | pending |
| line-4 | line-4-0567-1136-s013959 | forward | 1 | pending |
| line-4 | line-4-0567-1136-s013959 | reverse | 1 | pending |
| line-4 | line-4-0662-1037-s017042 | reverse | 1 | pending |
| line-4 | line-4-0725-1006-s018731 | reverse | 1 | pending |
| line-4 | line-4-0795-0964-s020529 | forward | 1 | pending |
| line-4 | line-4-0861-0960-s022187 | forward | 1 | pending |
| line-4 | line-4-1017-0963-s026011 | forward | 1 | pending |
| line-4 | line-4-1017-0963-s026011 | reverse | 1 | pending |
| line-4 | line-4-1119-0841-s029859 | reverse | 1 | pending |
| line-4 | line-4-1189-0717-s036217 | reverse | 1 | pending |
| line-4 | line-4-0939-0653-s042372 | forward | 1 | pending |
| line-4 | line-4-0866-0649-s043866 | forward | 1 | pending |
| line-4 | line-4-0716-0649-s046866 | forward | 1 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Quetta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
