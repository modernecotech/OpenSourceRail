# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **255 trainsets at 69 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **230 revenue, 20 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1235-1603-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-1137-1475-s003540 | forward | revenue | 3 | pending |
| line-1 | line-1-1137-1475-s003540 | reverse | revenue | 3 | pending |
| line-1 | line-1-1128-1364-s006085 | forward | revenue | 3 | pending |
| line-1 | line-1-1128-1364-s006085 | reverse | revenue | 3 | pending |
| line-1 | line-1-1126-1303-s007354 | forward | revenue | 3 | pending |
| line-1 | line-1-1126-1303-s007354 | reverse | revenue | 3 | pending |
| line-1 | line-1-1107-1206-s009452 | forward | revenue | 2 | pending |
| line-1 | line-1-1107-1206-s009452 | reverse | revenue | 2 | pending |
| line-1 | line-1-1075-1114-s011569 | forward | revenue | 2 | pending |
| line-1 | line-1-1075-1114-s011569 | reverse | revenue | 2 | pending |
| line-1 | line-1-1017-1007-s014595 | forward | revenue | 2 | pending |
| line-1 | line-1-1017-1007-s014595 | reverse | revenue | 2 | pending |
| line-1 | line-1-0975-0889-s017607 | forward | revenue | 2 | pending |
| line-1 | line-1-0975-0889-s017607 | reverse | revenue | 2 | pending |
| line-1 | line-1-1015-0761-s020626 | forward | revenue | 2 | pending |
| line-1 | line-1-1015-0761-s020626 | reverse | revenue | 2 | pending |
| line-1 | line-1-0932-0700-s023634 | forward | revenue | 2 | pending |
| line-1 | line-1-0932-0700-s023634 | reverse | revenue | 2 | pending |
| line-1 | line-1-0892-0545-s027115 | forward | revenue | 2 | pending |
| line-1 | line-1-0892-0545-s027115 | reverse | revenue | 2 | pending |
| line-1 | line-1-0749-0148-s036957 | reverse | revenue | 2 | pending |
| line-1 | line-1-1107-1206-s009452 | forward | spare | 1 | pending |
| line-1 | line-1-1107-1206-s009452 | reverse | spare | 1 | pending |
| line-1 | line-1-1075-1114-s011569 | forward | spare | 1 | pending |
| line-1 | line-1-1075-1114-s011569 | reverse | spare | 1 | pending |
| line-1 | line-1-1017-1007-s014595 | forward | spare | 1 | pending |
| line-1 | line-1-1017-1007-s014595 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1514-0979-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-1414-1038-s002878 | forward | revenue | 2 | pending |
| line-2 | line-2-1414-1038-s002878 | reverse | revenue | 2 | pending |
| line-2 | line-2-1275-1052-s006274 | forward | revenue | 2 | pending |
| line-2 | line-2-1275-1052-s006274 | reverse | revenue | 2 | pending |
| line-2 | line-2-1153-1054-s009276 | forward | revenue | 2 | pending |
| line-2 | line-2-1153-1054-s009276 | reverse | revenue | 2 | pending |
| line-2 | line-2-1026-1025-s012285 | forward | revenue | 2 | pending |
| line-2 | line-2-1026-1025-s012285 | reverse | revenue | 2 | pending |
| line-2 | line-2-0958-1035-s013893 | forward | revenue | 2 | pending |
| line-2 | line-2-0958-1035-s013893 | reverse | revenue | 2 | pending |
| line-2 | line-2-0944-1030-s015507 | forward | revenue | 2 | pending |
| line-2 | line-2-0944-1030-s015507 | reverse | revenue | 2 | pending |
| line-2 | line-2-0887-1014-s017269 | forward | revenue | 2 | pending |
| line-2 | line-2-0887-1014-s017269 | reverse | revenue | 2 | pending |
| line-2 | line-2-0839-1013-s018533 | forward | revenue | 2 | pending |
| line-2 | line-2-0839-1013-s018533 | reverse | revenue | 2 | pending |
| line-2 | line-2-0752-1030-s021534 | forward | revenue | 2 | pending |
| line-2 | line-2-0752-1030-s021534 | reverse | revenue | 2 | pending |
| line-2 | line-2-0643-1095-s024545 | forward | revenue | 2 | pending |
| line-2 | line-2-0643-1095-s024545 | reverse | revenue | 2 | pending |
| line-2 | line-2-0523-1113-s027564 | forward | revenue | 2 | pending |
| line-2 | line-2-0523-1113-s027564 | reverse | revenue | 2 | pending |
| line-2 | line-2-0370-1072-s031210 | reverse | revenue | 1 | pending |
| line-2 | line-2-0370-1072-s031210 | reverse | spare | 1 | pending |
| line-2 | line-2-1514-0979-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-1414-1038-s002878 | forward | spare | 1 | pending |
| line-2 | line-2-1414-1038-s002878 | reverse | spare | 1 | pending |
| line-2 | line-2-1275-1052-s006274 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1203-0078-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-1003-0618-s012745 | forward | revenue | 3 | pending |
| line-3 | line-3-1003-0618-s012745 | reverse | revenue | 3 | pending |
| line-3 | line-3-0968-0667-s014015 | forward | revenue | 3 | pending |
| line-3 | line-3-0968-0667-s014015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0881-0747-s017021 | forward | revenue | 3 | pending |
| line-3 | line-3-0881-0747-s017021 | reverse | revenue | 3 | pending |
| line-3 | line-3-0895-0878-s020024 | forward | revenue | 3 | pending |
| line-3 | line-3-0895-0878-s020024 | reverse | revenue | 3 | pending |
| line-3 | line-3-0838-0964-s023042 | forward | revenue | 3 | pending |
| line-3 | line-3-0838-0964-s023042 | reverse | revenue | 3 | pending |
| line-3 | line-3-0736-1005-s026056 | forward | revenue | 3 | pending |
| line-3 | line-3-0736-1005-s026056 | reverse | revenue | 3 | pending |
| line-3 | line-3-0751-1127-s029058 | forward | revenue | 3 | pending |
| line-3 | line-3-0751-1127-s029058 | reverse | revenue | 3 | pending |
| line-3 | line-3-0683-1378-s034923 | forward | revenue | 3 | pending |
| line-3 | line-3-0683-1378-s034923 | reverse | revenue | 3 | pending |
| line-3 | line-3-0632-1475-s037285 | forward | revenue | 3 | pending |
| line-3 | line-3-0632-1475-s037285 | reverse | revenue | 2 | pending |
| line-3 | line-3-0505-1671-s042461 | reverse | revenue | 2 | pending |
| line-3 | line-3-0632-1475-s037285 | reverse | spare | 1 | pending |
| line-3 | line-3-0505-1671-s042461 | reverse | spare | 1 | pending |
| line-3 | line-3-1203-0078-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-1003-0618-s012745 | forward | spare | 1 | pending |
| line-3 | line-3-1003-0618-s012745 | reverse | spare | 1 | pending |
| line-3 | line-3-0968-0667-s014015 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-1296-1249-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-1199-1211-s004198 | forward | revenue | 3 | pending |
| line-4 | line-4-1199-1211-s004198 | reverse | revenue | 3 | pending |
| line-4 | line-4-1174-1113-s007309 | forward | revenue | 3 | pending |
| line-4 | line-4-1174-1113-s007309 | reverse | revenue | 3 | pending |
| line-4 | line-4-1059-1046-s010316 | forward | revenue | 3 | pending |
| line-4 | line-4-1059-1046-s010316 | reverse | revenue | 3 | pending |
| line-4 | line-4-0997-1002-s011932 | forward | revenue | 2 | pending |
| line-4 | line-4-0997-1002-s011932 | reverse | revenue | 2 | pending |
| line-4 | line-4-0899-0932-s014938 | forward | revenue | 2 | pending |
| line-4 | line-4-0899-0932-s014938 | reverse | revenue | 2 | pending |
| line-4 | line-4-0802-0862-s017940 | forward | revenue | 2 | pending |
| line-4 | line-4-0802-0862-s017940 | reverse | revenue | 2 | pending |
| line-4 | line-4-0759-0749-s020948 | forward | revenue | 2 | pending |
| line-4 | line-4-0759-0749-s020948 | reverse | revenue | 2 | pending |
| line-4 | line-4-0651-0743-s023191 | forward | revenue | 2 | pending |
| line-4 | line-4-0651-0743-s023191 | reverse | revenue | 2 | pending |
| line-4 | line-4-0676-0663-s025166 | forward | revenue | 2 | pending |
| line-4 | line-4-0676-0663-s025166 | reverse | revenue | 2 | pending |
| line-4 | line-4-0349-0436-s033880 | reverse | revenue | 2 | pending |
| line-4 | line-4-0997-1002-s011932 | forward | spare | 1 | pending |
| line-4 | line-4-0997-1002-s011932 | reverse | spare | 1 | pending |
| line-4 | line-4-0899-0932-s014938 | forward | spare | 1 | pending |
| line-4 | line-4-0899-0932-s014938 | reverse | spare | 1 | pending |
| line-4 | line-4-0802-0862-s017940 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0862-0502-s000000 | forward | revenue | 1 | pending |
| line-5 | line-5-0862-0502-s000000 | reverse | revenue | 1 | pending |
| line-5 | line-5-0745-0563-s003020 | forward | revenue | 1 | pending |
| line-5 | line-5-0698-0675-s006005 | forward | revenue | 1 | pending |
| line-5 | line-5-0698-0675-s006005 | reverse | revenue | 1 | pending |
| line-5 | line-5-0651-0743-s007755 | reverse | revenue | 1 | pending |
| line-5 | line-5-0593-0820-s010043 | forward | revenue | 1 | pending |
| line-5 | line-5-0455-0967-s014154 | forward | revenue | 1 | pending |
| line-5 | line-5-0455-0967-s014154 | reverse | revenue | 1 | pending |
| line-5 | line-5-0370-1072-s018274 | reverse | revenue | 1 | pending |
| line-5 | line-5-0525-1264-s023751 | forward | revenue | 1 | pending |
| line-5 | line-5-0512-1405-s027300 | forward | revenue | 1 | pending |
| line-5 | line-5-0512-1405-s027300 | reverse | revenue | 1 | pending |
| line-5 | line-5-0632-1475-s030862 | reverse | revenue | 1 | pending |
| line-5 | line-5-0901-1525-s037757 | forward | revenue | 1 | pending |
| line-5 | line-5-1128-1364-s043875 | forward | revenue | 1 | pending |
| line-5 | line-5-1128-1364-s043875 | reverse | revenue | 1 | pending |
| line-5 | line-5-1296-1249-s048334 | forward | revenue | 1 | pending |
| line-5 | line-5-1365-1265-s049847 | forward | revenue | 1 | pending |
| line-5 | line-5-1365-1265-s049847 | reverse | revenue | 1 | pending |
| line-5 | line-5-1370-1168-s053356 | reverse | revenue | 1 | pending |
| line-5 | line-5-1409-1019-s056866 | forward | revenue | 1 | pending |
| line-5 | line-5-1367-0945-s060376 | forward | revenue | 1 | pending |
| line-5 | line-5-1367-0945-s060376 | reverse | revenue | 1 | pending |
| line-5 | line-5-1274-0825-s063874 | reverse | revenue | 1 | pending |
| line-5 | line-5-1127-0757-s067378 | forward | revenue | 1 | pending |
| line-5 | line-5-1058-0664-s070889 | forward | revenue | 1 | pending |
| line-5 | line-5-1058-0664-s070889 | reverse | spare | 1 | pending |
| line-5 | line-5-1003-0618-s072428 | reverse | spare | 1 | pending |
| line-5 | line-5-0892-0545-s075303 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **9,095.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0749-0148-s036957 | 2 | 2 | 0 | 0.0 |
| line-1-0892-0545-s027115 | 4 | 4 | 0 | 0.0 |
| line-1-0932-0700-s023634 | 4 | 2 | 2 | 170.0 |
| line-1-0975-0889-s017607 | 4 | 2 | 2 | 170.0 |
| line-1-1015-0761-s020626 | 4 | 2 | 2 | 170.0 |
| line-1-1017-1007-s014595 | 6 | 4 | 2 | 170.0 |
| line-1-1075-1114-s011569 | 6 | 2 | 4 | 340.0 |
| line-1-1107-1206-s009452 | 6 | 2 | 4 | 340.0 |
| line-1-1126-1303-s007354 | 6 | 2 | 4 | 340.0 |
| line-1-1128-1364-s006085 | 6 | 4 | 2 | 170.0 |
| line-1-1137-1475-s003540 | 6 | 2 | 4 | 340.0 |
| line-1-1235-1603-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0370-1072-s031210 | 2 | 2 | 0 | 0.0 |
| line-2-0523-1113-s027564 | 4 | 2 | 2 | 170.0 |
| line-2-0643-1095-s024545 | 4 | 2 | 2 | 170.0 |
| line-2-0752-1030-s021534 | 4 | 4 | 0 | 0.0 |
| line-2-0839-1013-s018533 | 4 | 2 | 2 | 170.0 |
| line-2-0887-1014-s017269 | 4 | 2 | 2 | 170.0 |
| line-2-0944-1030-s015507 | 4 | 2 | 2 | 170.0 |
| line-2-0958-1035-s013893 | 4 | 2 | 2 | 170.0 |
| line-2-1026-1025-s012285 | 4 | 4 | 0 | 0.0 |
| line-2-1153-1054-s009276 | 4 | 2 | 2 | 170.0 |
| line-2-1275-1052-s006274 | 5 | 2 | 3 | 255.0 |
| line-2-1414-1038-s002878 | 6 | 4 | 2 | 170.0 |
| line-2-1514-0979-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0505-1671-s042461 | 3 | 2 | 1 | 85.0 |
| line-3-0632-1475-s037285 | 6 | 4 | 2 | 170.0 |
| line-3-0683-1378-s034923 | 6 | 2 | 4 | 340.0 |
| line-3-0736-1005-s026056 | 6 | 4 | 2 | 170.0 |
| line-3-0751-1127-s029058 | 6 | 2 | 4 | 340.0 |
| line-3-0838-0964-s023042 | 6 | 2 | 4 | 340.0 |
| line-3-0881-0747-s017021 | 6 | 2 | 4 | 340.0 |
| line-3-0895-0878-s020024 | 6 | 2 | 4 | 340.0 |
| line-3-0968-0667-s014015 | 7 | 2 | 5 | 425.0 |
| line-3-1003-0618-s012745 | 8 | 4 | 4 | 340.0 |
| line-3-1203-0078-s000000 | 4 | 2 | 2 | 170.0 |
| line-4-0349-0436-s033880 | 2 | 2 | 0 | 0.0 |
| line-4-0651-0743-s023191 | 4 | 4 | 0 | 0.0 |
| line-4-0676-0663-s025166 | 4 | 4 | 0 | 0.0 |
| line-4-0759-0749-s020948 | 4 | 2 | 2 | 170.0 |
| line-4-0802-0862-s017940 | 5 | 2 | 3 | 255.0 |
| line-4-0899-0932-s014938 | 6 | 2 | 4 | 340.0 |
| line-4-0997-1002-s011932 | 6 | 4 | 2 | 170.0 |
| line-4-1059-1046-s010316 | 6 | 2 | 4 | 340.0 |
| line-4-1174-1113-s007309 | 6 | 2 | 4 | 340.0 |
| line-4-1199-1211-s004198 | 6 | 2 | 4 | 340.0 |
| line-4-1296-1249-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-0370-1072-s018274 | 1 | 4 | 0 | 0.0 |
| line-5-0455-0967-s014154 | 2 | 2 | 0 | 0.0 |
| line-5-0512-1405-s027300 | 2 | 2 | 0 | 0.0 |
| line-5-0525-1264-s023751 | 1 | 2 | 0 | 0.0 |
| line-5-0593-0820-s010043 | 1 | 2 | 0 | 0.0 |
| line-5-0632-1475-s030862 | 1 | 4 | 0 | 0.0 |
| line-5-0651-0743-s007755 | 1 | 4 | 0 | 0.0 |
| line-5-0698-0675-s006005 | 2 | 4 | 0 | 0.0 |
| line-5-0745-0563-s003020 | 1 | 2 | 0 | 0.0 |
| line-5-0862-0502-s000000 | 2 | 2 | 0 | 0.0 |
| line-5-0892-0545-s075303 | 1 | 4 | 0 | 0.0 |
| line-5-0901-1525-s037757 | 1 | 2 | 0 | 0.0 |
| line-5-1003-0618-s072428 | 1 | 4 | 0 | 0.0 |
| line-5-1058-0664-s070889 | 2 | 2 | 0 | 0.0 |
| line-5-1127-0757-s067378 | 1 | 2 | 0 | 0.0 |
| line-5-1128-1364-s043875 | 2 | 4 | 0 | 0.0 |
| line-5-1274-0825-s063874 | 1 | 2 | 0 | 0.0 |
| line-5-1296-1249-s048334 | 1 | 4 | 0 | 0.0 |
| line-5-1365-1265-s049847 | 2 | 2 | 0 | 0.0 |
| line-5-1367-0945-s060376 | 2 | 2 | 0 | 0.0 |
| line-5-1370-1168-s053356 | 1 | 2 | 0 | 0.0 |
| line-5-1409-1019-s056866 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Tunisia/Tunis/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
