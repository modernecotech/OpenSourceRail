# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **222 trainsets at 53 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **200 revenue, 17 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0397-1020-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-1023-s004584 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-1023-s004584 | reverse | revenue | 3 | pending |
| line-1 | line-1-0723-1026-s007609 | forward | revenue | 3 | pending |
| line-1 | line-1-0723-1026-s007609 | reverse | revenue | 3 | pending |
| line-1 | line-1-0845-0981-s010619 | forward | revenue | 2 | pending |
| line-1 | line-1-0845-0981-s010619 | reverse | revenue | 2 | pending |
| line-1 | line-1-0905-0977-s011918 | forward | revenue | 2 | pending |
| line-1 | line-1-0905-0977-s011918 | reverse | revenue | 2 | pending |
| line-1 | line-1-0969-1002-s013634 | forward | revenue | 2 | pending |
| line-1 | line-1-0969-1002-s013634 | reverse | revenue | 2 | pending |
| line-1 | line-1-1032-1002-s014993 | forward | revenue | 2 | pending |
| line-1 | line-1-1032-1002-s014993 | reverse | revenue | 2 | pending |
| line-1 | line-1-1086-0950-s017084 | forward | revenue | 2 | pending |
| line-1 | line-1-1086-0950-s017084 | reverse | revenue | 2 | pending |
| line-1 | line-1-1172-0975-s019657 | forward | revenue | 2 | pending |
| line-1 | line-1-1172-0975-s019657 | reverse | revenue | 2 | pending |
| line-1 | line-1-1291-0926-s022672 | forward | revenue | 2 | pending |
| line-1 | line-1-1291-0926-s022672 | reverse | revenue | 2 | pending |
| line-1 | line-1-1375-0920-s024782 | forward | revenue | 2 | pending |
| line-1 | line-1-1375-0920-s024782 | reverse | revenue | 2 | pending |
| line-1 | line-1-1423-0973-s026869 | reverse | revenue | 2 | pending |
| line-1 | line-1-0845-0981-s010619 | forward | spare | 1 | pending |
| line-1 | line-1-0845-0981-s010619 | reverse | spare | 1 | pending |
| line-1 | line-1-0905-0977-s011918 | forward | spare | 1 | pending |
| line-1 | line-1-0905-0977-s011918 | reverse | spare | 1 | pending |
| line-1 | line-1-0969-1002-s013634 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0798-0780-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0859-0830-s002179 | forward | revenue | 3 | pending |
| line-2 | line-2-0859-0830-s002179 | reverse | revenue | 3 | pending |
| line-2 | line-2-0926-0863-s004342 | forward | revenue | 2 | pending |
| line-2 | line-2-0926-0863-s004342 | reverse | revenue | 2 | pending |
| line-2 | line-2-0935-0937-s006124 | forward | revenue | 2 | pending |
| line-2 | line-2-0935-0937-s006124 | reverse | revenue | 2 | pending |
| line-2 | line-2-0958-0963-s007364 | forward | revenue | 2 | pending |
| line-2 | line-2-0958-0963-s007364 | reverse | revenue | 2 | pending |
| line-2 | line-2-1033-1040-s010367 | forward | revenue | 2 | pending |
| line-2 | line-2-1033-1040-s010367 | reverse | revenue | 2 | pending |
| line-2 | line-2-1113-1082-s013372 | forward | revenue | 2 | pending |
| line-2 | line-2-1113-1082-s013372 | reverse | revenue | 2 | pending |
| line-2 | line-2-1137-1206-s016380 | forward | revenue | 2 | pending |
| line-2 | line-2-1137-1206-s016380 | reverse | revenue | 2 | pending |
| line-2 | line-2-1194-1194-s018034 | forward | revenue | 2 | pending |
| line-2 | line-2-1194-1194-s018034 | reverse | revenue | 2 | pending |
| line-2 | line-2-1206-1243-s019391 | forward | revenue | 2 | pending |
| line-2 | line-2-1206-1243-s019391 | reverse | revenue | 2 | pending |
| line-2 | line-2-1251-1295-s021747 | forward | revenue | 2 | pending |
| line-2 | line-2-1251-1295-s021747 | reverse | revenue | 2 | pending |
| line-2 | line-2-1281-1371-s024107 | reverse | revenue | 2 | pending |
| line-2 | line-2-0926-0863-s004342 | forward | spare | 1 | pending |
| line-2 | line-2-0926-0863-s004342 | reverse | spare | 1 | pending |
| line-2 | line-2-0935-0937-s006124 | forward | spare | 1 | pending |
| line-2 | line-2-0935-0937-s006124 | reverse | spare | 1 | pending |
| line-2 | line-2-0958-0963-s007364 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0921-1394-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0977-1283-s003018 | forward | revenue | 3 | pending |
| line-3 | line-3-0977-1283-s003018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0927-1216-s005002 | forward | revenue | 3 | pending |
| line-3 | line-3-0927-1216-s005002 | reverse | revenue | 3 | pending |
| line-3 | line-3-0947-1144-s006972 | forward | revenue | 2 | pending |
| line-3 | line-3-0947-1144-s006972 | reverse | revenue | 2 | pending |
| line-3 | line-3-0960-1083-s009023 | forward | revenue | 2 | pending |
| line-3 | line-3-0960-1083-s009023 | reverse | revenue | 2 | pending |
| line-3 | line-3-1017-0967-s012030 | forward | revenue | 2 | pending |
| line-3 | line-3-1017-0967-s012030 | reverse | revenue | 2 | pending |
| line-3 | line-3-1016-0839-s015263 | forward | revenue | 2 | pending |
| line-3 | line-3-1016-0839-s015263 | reverse | revenue | 2 | pending |
| line-3 | line-3-1052-0780-s017595 | forward | revenue | 2 | pending |
| line-3 | line-3-1052-0780-s017595 | reverse | revenue | 2 | pending |
| line-3 | line-3-1038-0655-s020433 | reverse | revenue | 2 | pending |
| line-3 | line-3-0947-1144-s006972 | forward | spare | 1 | pending |
| line-3 | line-3-0947-1144-s006972 | reverse | spare | 1 | pending |
| line-3 | line-3-0960-1083-s009023 | forward | spare | 1 | pending |
| line-3 | line-3-0960-1083-s009023 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1120-1298-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-1059-1183-s003019 | forward | revenue | 4 | pending |
| line-4 | line-4-1059-1183-s003019 | reverse | revenue | 4 | pending |
| line-4 | line-4-1055-1089-s005048 | forward | revenue | 4 | pending |
| line-4 | line-4-1055-1089-s005048 | reverse | revenue | 4 | pending |
| line-4 | line-4-1086-1007-s007046 | forward | revenue | 4 | pending |
| line-4 | line-4-1086-1007-s007046 | reverse | revenue | 4 | pending |
| line-4 | line-4-1071-0915-s009060 | forward | revenue | 4 | pending |
| line-4 | line-4-1071-0915-s009060 | reverse | revenue | 4 | pending |
| line-4 | line-4-1142-0811-s012067 | forward | revenue | 4 | pending |
| line-4 | line-4-1142-0811-s012067 | reverse | revenue | 4 | pending |
| line-4 | line-4-1140-0714-s014303 | forward | revenue | 3 | pending |
| line-4 | line-4-1140-0714-s014303 | reverse | revenue | 3 | pending |
| line-4 | line-4-1109-0108-s029722 | reverse | revenue | 3 | pending |
| line-4 | line-4-1140-0714-s014303 | forward | spare | 1 | pending |
| line-4 | line-4-1140-0714-s014303 | reverse | spare | 1 | pending |
| line-4 | line-4-1109-0108-s029722 | reverse | spare | 1 | pending |
| line-4 | line-4-1120-1298-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-1059-1183-s003019 | forward | spare | 1 | pending |
| line-4 | line-4-1059-1183-s003019 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-1052-0780-s000681 | forward | revenue | 1 | pending |
| line-5 | line-5-1052-0780-s000681 | reverse | revenue | 1 | pending |
| line-5 | line-5-0926-0863-s004093 | reverse | revenue | 1 | pending |
| line-5 | line-5-0904-0986-s007117 | forward | revenue | 1 | pending |
| line-5 | line-5-0883-1117-s010121 | forward | revenue | 1 | pending |
| line-5 | line-5-0883-1117-s010121 | reverse | revenue | 1 | pending |
| line-5 | line-5-0884-1211-s013130 | reverse | revenue | 1 | pending |
| line-5 | line-5-0947-1144-s015681 | forward | revenue | 1 | pending |
| line-5 | line-5-1027-1080-s018151 | forward | revenue | 1 | pending |
| line-5 | line-5-1027-1080-s018151 | reverse | revenue | 1 | pending |
| line-5 | line-5-1037-0979-s020321 | reverse | revenue | 1 | pending |
| line-5 | line-5-1072-0905-s022173 | forward | revenue | 1 | pending |
| line-5 | line-5-1155-0796-s025174 | forward | revenue | 1 | pending |
| line-5 | line-5-1155-0796-s025174 | reverse | revenue | 1 | pending |
| line-5 | line-5-1241-0722-s028188 | reverse | spare | 1 | pending |
| line-5 | line-5-1140-0714-s032192 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**104 trainsets exceed the reference platform envelope**, requiring **12,584.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0397-1020-s000000 | 3 | 2 | 1 | 121.0 |
| line-1-0592-1023-s004584 | 6 | 2 | 4 | 484.0 |
| line-1-0723-1026-s007609 | 6 | 2 | 4 | 484.0 |
| line-1-0845-0981-s010619 | 6 | 2 | 4 | 484.0 |
| line-1-0905-0977-s011918 | 6 | 4 | 2 | 242.0 |
| line-1-0969-1002-s013634 | 5 | 2 | 3 | 363.0 |
| line-1-1032-1002-s014993 | 4 | 4 | 0 | 0.0 |
| line-1-1086-0950-s017084 | 4 | 2 | 2 | 242.0 |
| line-1-1172-0975-s019657 | 4 | 2 | 2 | 242.0 |
| line-1-1291-0926-s022672 | 4 | 2 | 2 | 242.0 |
| line-1-1375-0920-s024782 | 4 | 2 | 2 | 242.0 |
| line-1-1423-0973-s026869 | 2 | 2 | 0 | 0.0 |
| line-2-0798-0780-s000000 | 3 | 2 | 1 | 121.0 |
| line-2-0859-0830-s002179 | 6 | 2 | 4 | 484.0 |
| line-2-0926-0863-s004342 | 6 | 4 | 2 | 242.0 |
| line-2-0935-0937-s006124 | 6 | 2 | 4 | 484.0 |
| line-2-0958-0963-s007364 | 5 | 2 | 3 | 363.0 |
| line-2-1033-1040-s010367 | 4 | 2 | 2 | 242.0 |
| line-2-1113-1082-s013372 | 4 | 2 | 2 | 242.0 |
| line-2-1137-1206-s016380 | 4 | 2 | 2 | 242.0 |
| line-2-1194-1194-s018034 | 4 | 2 | 2 | 242.0 |
| line-2-1206-1243-s019391 | 4 | 2 | 2 | 242.0 |
| line-2-1251-1295-s021747 | 4 | 2 | 2 | 242.0 |
| line-2-1281-1371-s024107 | 2 | 2 | 0 | 0.0 |
| line-3-0921-1394-s000000 | 3 | 2 | 1 | 121.0 |
| line-3-0927-1216-s005002 | 6 | 2 | 4 | 484.0 |
| line-3-0947-1144-s006972 | 6 | 4 | 2 | 242.0 |
| line-3-0960-1083-s009023 | 6 | 2 | 4 | 484.0 |
| line-3-0977-1283-s003018 | 6 | 2 | 4 | 484.0 |
| line-3-1016-0839-s015263 | 4 | 2 | 2 | 242.0 |
| line-3-1017-0967-s012030 | 4 | 4 | 0 | 0.0 |
| line-3-1038-0655-s020433 | 2 | 2 | 0 | 0.0 |
| line-3-1052-0780-s017595 | 4 | 4 | 0 | 0.0 |
| line-4-1055-1089-s005048 | 8 | 4 | 4 | 484.0 |
| line-4-1059-1183-s003019 | 10 | 2 | 8 | 968.0 |
| line-4-1071-0915-s009060 | 8 | 4 | 4 | 484.0 |
| line-4-1086-1007-s007046 | 8 | 2 | 6 | 726.0 |
| line-4-1109-0108-s029722 | 4 | 2 | 2 | 242.0 |
| line-4-1120-1298-s000000 | 5 | 2 | 3 | 363.0 |
| line-4-1140-0714-s014303 | 8 | 4 | 4 | 484.0 |
| line-4-1142-0811-s012067 | 8 | 4 | 4 | 484.0 |
| line-5-0883-1117-s010121 | 2 | 2 | 0 | 0.0 |
| line-5-0884-1211-s013130 | 1 | 2 | 0 | 0.0 |
| line-5-0904-0986-s007117 | 1 | 4 | 0 | 0.0 |
| line-5-0926-0863-s004093 | 1 | 4 | 0 | 0.0 |
| line-5-0947-1144-s015681 | 1 | 4 | 0 | 0.0 |
| line-5-1027-1080-s018151 | 2 | 4 | 0 | 0.0 |
| line-5-1037-0979-s020321 | 1 | 4 | 0 | 0.0 |
| line-5-1052-0780-s000681 | 2 | 4 | 0 | 0.0 |
| line-5-1072-0905-s022173 | 1 | 4 | 0 | 0.0 |
| line-5-1140-0714-s032192 | 1 | 4 | 0 | 0.0 |
| line-5-1155-0796-s025174 | 2 | 4 | 0 | 0.0 |
| line-5-1241-0722-s028188 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Ibadan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
