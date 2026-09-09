# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **127 trainsets at 40 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **114 revenue, 9 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1275-0615-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0995-0669-s006470 | forward | revenue | 3 | pending |
| line-1 | line-1-0995-0669-s006470 | reverse | revenue | 2 | pending |
| line-1 | line-1-0975-0796-s009572 | forward | revenue | 2 | pending |
| line-1 | line-1-0975-0796-s009572 | reverse | revenue | 2 | pending |
| line-1 | line-1-0855-0802-s012589 | forward | revenue | 2 | pending |
| line-1 | line-1-0855-0802-s012589 | reverse | revenue | 2 | pending |
| line-1 | line-1-0799-0807-s014016 | forward | revenue | 2 | pending |
| line-1 | line-1-0799-0807-s014016 | reverse | revenue | 2 | pending |
| line-1 | line-1-0741-0830-s015605 | forward | revenue | 2 | pending |
| line-1 | line-1-0741-0830-s015605 | reverse | revenue | 2 | pending |
| line-1 | line-1-0681-0903-s018621 | forward | revenue | 2 | pending |
| line-1 | line-1-0681-0903-s018621 | reverse | revenue | 2 | pending |
| line-1 | line-1-0600-0949-s020890 | forward | revenue | 2 | pending |
| line-1 | line-1-0600-0949-s020890 | reverse | revenue | 2 | pending |
| line-1 | line-1-0507-0983-s023160 | forward | revenue | 2 | pending |
| line-1 | line-1-0507-0983-s023160 | reverse | revenue | 2 | pending |
| line-1 | line-1-0421-0987-s025431 | reverse | revenue | 2 | pending |
| line-1 | line-1-0995-0669-s006470 | reverse | spare | 1 | pending |
| line-1 | line-1-0975-0796-s009572 | forward | spare | 1 | pending |
| line-1 | line-1-0975-0796-s009572 | reverse | spare | 1 | pending |
| line-1 | line-1-0855-0802-s012589 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1119-0841-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1046-0844-s003011 | forward | revenue | 3 | pending |
| line-2 | line-2-1046-0844-s003011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0916-0893-s006028 | forward | revenue | 3 | pending |
| line-2 | line-2-0916-0893-s006028 | reverse | revenue | 3 | pending |
| line-2 | line-2-0875-0960-s008180 | forward | revenue | 3 | pending |
| line-2 | line-2-0875-0960-s008180 | reverse | revenue | 2 | pending |
| line-2 | line-2-0795-0985-s012378 | forward | revenue | 2 | pending |
| line-2 | line-2-0795-0985-s012378 | reverse | revenue | 2 | pending |
| line-2 | line-2-0742-1025-s013976 | forward | revenue | 2 | pending |
| line-2 | line-2-0742-1025-s013976 | reverse | revenue | 2 | pending |
| line-2 | line-2-0687-1108-s016369 | forward | revenue | 2 | pending |
| line-2 | line-2-0687-1108-s016369 | reverse | revenue | 2 | pending |
| line-2 | line-2-0590-1147-s018754 | forward | revenue | 2 | pending |
| line-2 | line-2-0590-1147-s018754 | reverse | revenue | 2 | pending |
| line-2 | line-2-0371-1395-s026740 | reverse | revenue | 2 | pending |
| line-2 | line-2-0875-0960-s008180 | reverse | spare | 1 | pending |
| line-2 | line-2-0795-0985-s012378 | forward | spare | 1 | pending |
| line-2 | line-2-0795-0985-s012378 | reverse | spare | 1 | pending |
| line-2 | line-2-0742-1025-s013976 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0939-0653-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0864-0683-s003012 | forward | revenue | 3 | pending |
| line-3 | line-3-0864-0683-s003012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0721-0694-s006029 | forward | revenue | 3 | pending |
| line-3 | line-3-0721-0694-s006029 | reverse | revenue | 3 | pending |
| line-3 | line-3-0407-0735-s012649 | forward | revenue | 2 | pending |
| line-3 | line-3-0407-0735-s012649 | reverse | revenue | 2 | pending |
| line-3 | line-3-0409-0805-s015386 | reverse | revenue | 2 | pending |
| line-3 | line-3-0407-0735-s012649 | forward | spare | 1 | pending |
| line-3 | line-3-0407-0735-s012649 | reverse | spare | 1 | pending |
| line-3 | line-3-0409-0805-s015386 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0419-0635-s000000 | forward | revenue | 1 | pending |
| line-4 | line-4-0419-0635-s000000 | reverse | revenue | 1 | pending |
| line-4 | line-4-0407-0735-s002206 | reverse | revenue | 1 | pending |
| line-4 | line-4-0409-0805-s003805 | reverse | revenue | 1 | pending |
| line-4 | line-4-0453-0932-s007006 | forward | revenue | 1 | pending |
| line-4 | line-4-0421-0987-s008400 | forward | revenue | 1 | pending |
| line-4 | line-4-0567-1136-s013959 | forward | revenue | 1 | pending |
| line-4 | line-4-0567-1136-s013959 | reverse | revenue | 1 | pending |
| line-4 | line-4-0662-1037-s017042 | reverse | revenue | 1 | pending |
| line-4 | line-4-0725-1006-s018731 | reverse | revenue | 1 | pending |
| line-4 | line-4-0795-0964-s020529 | forward | revenue | 1 | pending |
| line-4 | line-4-0861-0960-s022187 | forward | revenue | 1 | pending |
| line-4 | line-4-1017-0963-s026011 | forward | revenue | 1 | pending |
| line-4 | line-4-1017-0963-s026011 | reverse | revenue | 1 | pending |
| line-4 | line-4-1119-0841-s029859 | reverse | revenue | 1 | pending |
| line-4 | line-4-1189-0717-s036217 | reverse | revenue | 1 | pending |
| line-4 | line-4-0939-0653-s042372 | forward | revenue | 1 | pending |
| line-4 | line-4-0866-0649-s043866 | forward | spare | 1 | pending |
| line-4 | line-4-0716-0649-s046866 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**50 trainsets exceed the reference platform envelope**, requiring **4,250.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0421-0987-s025431 | 2 | 2 | 0 | 0.0 |
| line-1-0507-0983-s023160 | 4 | 2 | 2 | 170.0 |
| line-1-0600-0949-s020890 | 4 | 2 | 2 | 170.0 |
| line-1-0681-0903-s018621 | 4 | 2 | 2 | 170.0 |
| line-1-0741-0830-s015605 | 4 | 2 | 2 | 170.0 |
| line-1-0799-0807-s014016 | 4 | 2 | 2 | 170.0 |
| line-1-0855-0802-s012589 | 5 | 2 | 3 | 255.0 |
| line-1-0975-0796-s009572 | 6 | 2 | 4 | 340.0 |
| line-1-0995-0669-s006470 | 6 | 2 | 4 | 340.0 |
| line-1-1275-0615-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0371-1395-s026740 | 2 | 2 | 0 | 0.0 |
| line-2-0590-1147-s018754 | 4 | 4 | 0 | 0.0 |
| line-2-0687-1108-s016369 | 4 | 2 | 2 | 170.0 |
| line-2-0742-1025-s013976 | 5 | 4 | 1 | 85.0 |
| line-2-0795-0985-s012378 | 6 | 4 | 2 | 170.0 |
| line-2-0875-0960-s008180 | 6 | 4 | 2 | 170.0 |
| line-2-0916-0893-s006028 | 6 | 2 | 4 | 340.0 |
| line-2-1046-0844-s003011 | 6 | 2 | 4 | 340.0 |
| line-2-1119-0841-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0407-0735-s012649 | 6 | 4 | 2 | 170.0 |
| line-3-0409-0805-s015386 | 3 | 2 | 1 | 85.0 |
| line-3-0721-0694-s006029 | 6 | 2 | 4 | 340.0 |
| line-3-0864-0683-s003012 | 6 | 2 | 4 | 340.0 |
| line-3-0939-0653-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0407-0735-s002206 | 1 | 4 | 0 | 0.0 |
| line-4-0409-0805-s003805 | 1 | 4 | 0 | 0.0 |
| line-4-0419-0635-s000000 | 2 | 2 | 0 | 0.0 |
| line-4-0421-0987-s008400 | 1 | 4 | 0 | 0.0 |
| line-4-0453-0932-s007006 | 1 | 2 | 0 | 0.0 |
| line-4-0567-1136-s013959 | 2 | 4 | 0 | 0.0 |
| line-4-0662-1037-s017042 | 1 | 2 | 0 | 0.0 |
| line-4-0716-0649-s046866 | 1 | 2 | 0 | 0.0 |
| line-4-0725-1006-s018731 | 1 | 4 | 0 | 0.0 |
| line-4-0795-0964-s020529 | 1 | 4 | 0 | 0.0 |
| line-4-0861-0960-s022187 | 1 | 4 | 0 | 0.0 |
| line-4-0866-0649-s043866 | 1 | 2 | 0 | 0.0 |
| line-4-0939-0653-s042372 | 1 | 4 | 0 | 0.0 |
| line-4-1017-0963-s026011 | 2 | 2 | 0 | 0.0 |
| line-4-1119-0841-s029859 | 1 | 4 | 0 | 0.0 |
| line-4-1189-0717-s036217 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Quetta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
