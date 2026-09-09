# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **504 trainsets at 88 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **454 revenue, 41 spare, 9 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1358-0772-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-1269-0868-s003508 | forward | revenue | 3 | pending |
| line-1 | line-1-1269-0868-s003508 | reverse | revenue | 3 | pending |
| line-1 | line-1-1155-0814-s007003 | forward | revenue | 3 | pending |
| line-1 | line-1-1155-0814-s007003 | reverse | revenue | 3 | pending |
| line-1 | line-1-1018-0843-s010007 | forward | revenue | 3 | pending |
| line-1 | line-1-1018-0843-s010007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0909-0919-s013050 | forward | revenue | 3 | pending |
| line-1 | line-1-0909-0919-s013050 | reverse | revenue | 3 | pending |
| line-1 | line-1-0862-0887-s015112 | forward | revenue | 3 | pending |
| line-1 | line-1-0862-0887-s015112 | reverse | revenue | 3 | pending |
| line-1 | line-1-0787-0961-s018133 | forward | revenue | 3 | pending |
| line-1 | line-1-0787-0961-s018133 | reverse | revenue | 3 | pending |
| line-1 | line-1-0710-1055-s021158 | forward | revenue | 3 | pending |
| line-1 | line-1-0710-1055-s021158 | reverse | revenue | 3 | pending |
| line-1 | line-1-0590-1069-s024177 | forward | revenue | 3 | pending |
| line-1 | line-1-0590-1069-s024177 | reverse | revenue | 3 | pending |
| line-1 | line-1-0385-1112-s029678 | forward | revenue | 3 | pending |
| line-1 | line-1-0385-1112-s029678 | reverse | revenue | 3 | pending |
| line-1 | line-1-0173-1201-s035411 | reverse | revenue | 2 | pending |
| line-1 | line-1-0173-1201-s035411 | reverse | spare | 1 | pending |
| line-1 | line-1-1358-0772-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-1269-0868-s003508 | forward | spare | 1 | pending |
| line-1 | line-1-1269-0868-s003508 | reverse | spare | 1 | pending |
| line-1 | line-1-1155-0814-s007003 | forward | spare | 1 | pending |
| line-1 | line-1-1155-0814-s007003 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1142-1146-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-1039-1072-s003016 | forward | revenue | 4 | pending |
| line-2 | line-2-1039-1072-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0955-0979-s006031 | forward | revenue | 3 | pending |
| line-2 | line-2-0955-0979-s006031 | reverse | revenue | 3 | pending |
| line-2 | line-2-0909-0919-s008165 | forward | revenue | 3 | pending |
| line-2 | line-2-0909-0919-s008165 | reverse | revenue | 3 | pending |
| line-2 | line-2-0869-0847-s010119 | forward | revenue | 3 | pending |
| line-2 | line-2-0869-0847-s010119 | reverse | revenue | 3 | pending |
| line-2 | line-2-0804-0839-s012068 | forward | revenue | 3 | pending |
| line-2 | line-2-0804-0839-s012068 | reverse | revenue | 3 | pending |
| line-2 | line-2-0601-0691-s018846 | forward | revenue | 3 | pending |
| line-2 | line-2-0601-0691-s018846 | reverse | revenue | 3 | pending |
| line-2 | line-2-0508-0679-s021091 | forward | revenue | 3 | pending |
| line-2 | line-2-0508-0679-s021091 | reverse | revenue | 3 | pending |
| line-2 | line-2-0277-0467-s029354 | reverse | revenue | 3 | pending |
| line-2 | line-2-1039-1072-s003016 | reverse | spare | 1 | pending |
| line-2 | line-2-0955-0979-s006031 | forward | spare | 1 | pending |
| line-2 | line-2-0955-0979-s006031 | reverse | spare | 1 | pending |
| line-2 | line-2-0909-0919-s008165 | forward | spare | 1 | pending |
| line-2 | line-2-0909-0919-s008165 | reverse | spare | 1 | pending |
| line-2 | line-2-0869-0847-s010119 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1135-0045-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-1029-0434-s010250 | forward | revenue | 3 | pending |
| line-3 | line-3-1029-0434-s010250 | reverse | revenue | 3 | pending |
| line-3 | line-3-1037-0602-s014036 | forward | revenue | 3 | pending |
| line-3 | line-3-1037-0602-s014036 | reverse | revenue | 3 | pending |
| line-3 | line-3-0987-0713-s017050 | forward | revenue | 3 | pending |
| line-3 | line-3-0987-0713-s017050 | reverse | revenue | 3 | pending |
| line-3 | line-3-0889-0802-s020055 | forward | revenue | 3 | pending |
| line-3 | line-3-0889-0802-s020055 | reverse | revenue | 3 | pending |
| line-3 | line-3-0909-0919-s023468 | forward | revenue | 3 | pending |
| line-3 | line-3-0909-0919-s023468 | reverse | revenue | 3 | pending |
| line-3 | line-3-0873-0941-s024685 | forward | revenue | 3 | pending |
| line-3 | line-3-0873-0941-s024685 | reverse | revenue | 3 | pending |
| line-3 | line-3-0799-1036-s027687 | forward | revenue | 3 | pending |
| line-3 | line-3-0799-1036-s027687 | reverse | revenue | 3 | pending |
| line-3 | line-3-0805-1111-s029846 | forward | revenue | 3 | pending |
| line-3 | line-3-0805-1111-s029846 | reverse | revenue | 3 | pending |
| line-3 | line-3-0734-1177-s032011 | forward | revenue | 3 | pending |
| line-3 | line-3-0734-1177-s032011 | reverse | revenue | 3 | pending |
| line-3 | line-3-0746-1266-s034181 | reverse | revenue | 3 | pending |
| line-3 | line-3-1029-0434-s010250 | forward | spare | 1 | pending |
| line-3 | line-3-1029-0434-s010250 | reverse | spare | 1 | pending |
| line-3 | line-3-1037-0602-s014036 | forward | spare | 1 | pending |
| line-3 | line-3-1037-0602-s014036 | reverse | spare | 1 | pending |
| line-3 | line-3-0987-0713-s017050 | forward | spare | 1 | pending |
| line-3 | line-3-0987-0713-s017050 | reverse | spare | 1 | pending |
| line-3 | line-3-0889-0802-s020055 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0816-1332-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0841-1172-s003842 | forward | revenue | 3 | pending |
| line-4 | line-4-0841-1172-s003842 | reverse | revenue | 3 | pending |
| line-4 | line-4-0954-1120-s006858 | forward | revenue | 3 | pending |
| line-4 | line-4-0954-1120-s006858 | reverse | revenue | 3 | pending |
| line-4 | line-4-1001-1002-s009880 | forward | revenue | 3 | pending |
| line-4 | line-4-1001-1002-s009880 | reverse | revenue | 3 | pending |
| line-4 | line-4-1043-0893-s012896 | forward | revenue | 3 | pending |
| line-4 | line-4-1043-0893-s012896 | reverse | revenue | 3 | pending |
| line-4 | line-4-1059-0777-s015896 | forward | revenue | 3 | pending |
| line-4 | line-4-1059-0777-s015896 | reverse | revenue | 3 | pending |
| line-4 | line-4-1170-0530-s022373 | forward | revenue | 3 | pending |
| line-4 | line-4-1170-0530-s022373 | reverse | revenue | 3 | pending |
| line-4 | line-4-1215-0384-s025701 | reverse | revenue | 3 | pending |
| line-4 | line-4-0841-1172-s003842 | forward | spare | 1 | pending |
| line-4 | line-4-0841-1172-s003842 | reverse | spare | 1 | pending |
| line-4 | line-4-0954-1120-s006858 | forward | spare | 1 | pending |
| line-4 | line-4-0954-1120-s006858 | reverse | spare | 1 | pending |
| line-4 | line-4-1001-1002-s009880 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0597-0856-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0720-0904-s003016 | forward | revenue | 4 | pending |
| line-5 | line-5-0720-0904-s003016 | reverse | revenue | 4 | pending |
| line-5 | line-5-0841-0908-s005804 | forward | revenue | 4 | pending |
| line-5 | line-5-0841-0908-s005804 | reverse | revenue | 4 | pending |
| line-5 | line-5-0909-0919-s008390 | forward | revenue | 3 | pending |
| line-5 | line-5-0909-0919-s008390 | reverse | revenue | 3 | pending |
| line-5 | line-5-1049-0911-s011807 | forward | revenue | 3 | pending |
| line-5 | line-5-1049-0911-s011807 | reverse | revenue | 3 | pending |
| line-5 | line-5-1182-0923-s015312 | forward | revenue | 3 | pending |
| line-5 | line-5-1182-0923-s015312 | reverse | revenue | 3 | pending |
| line-5 | line-5-1347-0945-s018811 | forward | revenue | 3 | pending |
| line-5 | line-5-1347-0945-s018811 | reverse | revenue | 3 | pending |
| line-5 | line-5-1796-1080-s029230 | reverse | revenue | 3 | pending |
| line-5 | line-5-0909-0919-s008390 | forward | spare | 1 | pending |
| line-5 | line-5-0909-0919-s008390 | reverse | spare | 1 | pending |
| line-5 | line-5-1049-0911-s011807 | forward | spare | 1 | pending |
| line-5 | line-5-1049-0911-s011807 | reverse | spare | 1 | pending |
| line-5 | line-5-1182-0923-s015312 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-1067-1638-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-1029-1312-s007668 | forward | revenue | 4 | pending |
| line-6 | line-6-1029-1312-s007668 | reverse | revenue | 4 | pending |
| line-6 | line-6-0918-1168-s012344 | forward | revenue | 4 | pending |
| line-6 | line-6-0918-1168-s012344 | reverse | revenue | 4 | pending |
| line-6 | line-6-0871-1060-s015348 | forward | revenue | 4 | pending |
| line-6 | line-6-0871-1060-s015348 | reverse | revenue | 4 | pending |
| line-6 | line-6-0880-0953-s018351 | forward | revenue | 4 | pending |
| line-6 | line-6-0880-0953-s018351 | reverse | revenue | 4 | pending |
| line-6 | line-6-0861-0888-s019957 | forward | revenue | 4 | pending |
| line-6 | line-6-0861-0888-s019957 | reverse | revenue | 4 | pending |
| line-6 | line-6-0853-0762-s022965 | forward | revenue | 3 | pending |
| line-6 | line-6-0853-0762-s022965 | reverse | revenue | 3 | pending |
| line-6 | line-6-0707-0497-s029531 | forward | revenue | 3 | pending |
| line-6 | line-6-0707-0497-s029531 | reverse | revenue | 3 | pending |
| line-6 | line-6-0642-0265-s035454 | reverse | revenue | 3 | pending |
| line-6 | line-6-0853-0762-s022965 | forward | spare | 1 | pending |
| line-6 | line-6-0853-0762-s022965 | reverse | spare | 1 | pending |
| line-6 | line-6-0707-0497-s029531 | forward | spare | 1 | pending |
| line-6 | line-6-0707-0497-s029531 | reverse | spare | 1 | pending |
| line-6 | line-6-0642-0265-s035454 | reverse | spare | 1 | pending |
| line-6 | line-6-1067-1638-s000000 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-0871-0514-s000000 | forward | revenue | 4 | pending |
| line-7 | line-7-0844-0649-s003002 | forward | revenue | 4 | pending |
| line-7 | line-7-0844-0649-s003002 | reverse | revenue | 4 | pending |
| line-7 | line-7-0796-0767-s006020 | forward | revenue | 4 | pending |
| line-7 | line-7-0796-0767-s006020 | reverse | revenue | 4 | pending |
| line-7 | line-7-0693-0834-s009040 | forward | revenue | 4 | pending |
| line-7 | line-7-0693-0834-s009040 | reverse | revenue | 4 | pending |
| line-7 | line-7-0650-0941-s012048 | forward | revenue | 4 | pending |
| line-7 | line-7-0650-0941-s012048 | reverse | revenue | 4 | pending |
| line-7 | line-7-0568-1052-s015061 | forward | revenue | 4 | pending |
| line-7 | line-7-0568-1052-s015061 | reverse | revenue | 4 | pending |
| line-7 | line-7-0518-1203-s019193 | forward | revenue | 4 | pending |
| line-7 | line-7-0518-1203-s019193 | reverse | revenue | 4 | pending |
| line-7 | line-7-0335-1662-s032343 | reverse | revenue | 3 | pending |
| line-7 | line-7-0335-1662-s032343 | reverse | spare | 1 | pending |
| line-7 | line-7-0871-0514-s000000 | forward | spare | 1 | pending |
| line-7 | line-7-0844-0649-s003002 | forward | spare | 1 | pending |
| line-7 | line-7-0844-0649-s003002 | reverse | spare | 1 | pending |
| line-7 | line-7-0796-0767-s006020 | forward | spare | 1 | pending |
| line-7 | line-7-0796-0767-s006020 | reverse | cold_reserve | 1 | pending |
| line-8 | line-8-1281-1151-s000000 | forward | revenue | 4 | pending |
| line-8 | line-8-1219-1148-s001381 | forward | revenue | 4 | pending |
| line-8 | line-8-1219-1148-s001381 | reverse | revenue | 4 | pending |
| line-8 | line-8-1158-0968-s005978 | forward | revenue | 4 | pending |
| line-8 | line-8-1158-0968-s005978 | reverse | revenue | 4 | pending |
| line-8 | line-8-1080-0870-s008995 | forward | revenue | 4 | pending |
| line-8 | line-8-1080-0870-s008995 | reverse | revenue | 3 | pending |
| line-8 | line-8-0960-0803-s012013 | forward | revenue | 3 | pending |
| line-8 | line-8-0960-0803-s012013 | reverse | revenue | 3 | pending |
| line-8 | line-8-0876-0715-s015030 | forward | revenue | 3 | pending |
| line-8 | line-8-0876-0715-s015030 | reverse | revenue | 3 | pending |
| line-8 | line-8-0725-0478-s021344 | forward | revenue | 3 | pending |
| line-8 | line-8-0725-0478-s021344 | reverse | revenue | 3 | pending |
| line-8 | line-8-0429-0242-s029503 | reverse | revenue | 3 | pending |
| line-8 | line-8-1080-0870-s008995 | reverse | spare | 1 | pending |
| line-8 | line-8-0960-0803-s012013 | forward | spare | 1 | pending |
| line-8 | line-8-0960-0803-s012013 | reverse | spare | 1 | pending |
| line-8 | line-8-0876-0715-s015030 | forward | spare | 1 | pending |
| line-8 | line-8-0876-0715-s015030 | reverse | cold_reserve | 1 | pending |
| line-9 | line-9-0653-0546-s000000 | forward | revenue | 1 | pending |
| line-9 | line-9-0653-0546-s000000 | reverse | revenue | 1 | pending |
| line-9 | line-9-0508-0679-s004276 | forward | revenue | 1 | pending |
| line-9 | line-9-0508-0679-s004276 | reverse | revenue | 1 | pending |
| line-9 | line-9-0459-0786-s007005 | forward | revenue | 1 | pending |
| line-9 | line-9-0459-0786-s007005 | reverse | revenue | 1 | pending |
| line-9 | line-9-0412-0944-s010953 | forward | revenue | 1 | pending |
| line-9 | line-9-0412-0944-s010953 | reverse | revenue | 1 | pending |
| line-9 | line-9-0385-1112-s014917 | forward | revenue | 1 | pending |
| line-9 | line-9-0385-1112-s014917 | reverse | revenue | 1 | pending |
| line-9 | line-9-0518-1203-s018376 | forward | revenue | 1 | pending |
| line-9 | line-9-0518-1203-s018376 | reverse | revenue | 1 | pending |
| line-9 | line-9-0629-1258-s021051 | forward | revenue | 1 | pending |
| line-9 | line-9-0629-1258-s021051 | reverse | revenue | 1 | pending |
| line-9 | line-9-0975-1352-s035103 | forward | revenue | 1 | pending |
| line-9 | line-9-0975-1352-s035103 | reverse | revenue | 1 | pending |
| line-9 | line-9-1029-1312-s036514 | forward | revenue | 1 | pending |
| line-9 | line-9-1029-1312-s036514 | reverse | revenue | 1 | pending |
| line-9 | line-9-1219-1148-s042287 | forward | revenue | 1 | pending |
| line-9 | line-9-1219-1148-s042287 | reverse | revenue | 1 | pending |
| line-9 | line-9-1358-0945-s047533 | forward | revenue | 1 | pending |
| line-9 | line-9-1358-0945-s047533 | reverse | revenue | 1 | pending |
| line-9 | line-9-1361-0866-s049138 | forward | revenue | 1 | pending |
| line-9 | line-9-1361-0866-s049138 | reverse | revenue | 1 | pending |
| line-9 | line-9-1358-0772-s051176 | forward | revenue | 1 | pending |
| line-9 | line-9-1358-0772-s051176 | reverse | revenue | 1 | pending |
| line-9 | line-9-1170-0530-s060618 | forward | revenue | 1 | pending |
| line-9 | line-9-1170-0530-s060618 | reverse | revenue | 1 | pending |
| line-9 | line-9-1029-0434-s064269 | forward | revenue | 1 | pending |
| line-9 | line-9-1029-0434-s064269 | reverse | revenue | 1 | pending |
| line-9 | line-9-0707-0496-s071838 | forward | revenue | 1 | pending |
| line-9 | line-9-0707-0496-s071838 | reverse | revenue | 1 | pending |
| line-9 | line-9-0653-0546-s000000 | forward | spare | 1 | pending |
| line-9 | line-9-0653-0546-s000000 | reverse | spare | 1 | pending |
| line-9 | line-9-0508-0679-s004276 | forward | spare | 1 | pending |
| line-9 | line-9-0508-0679-s004276 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**280 trainsets exceed the reference platform envelope**, requiring **33,880.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0173-1201-s035411 | 3 | 2 | 1 | 121.0 |
| line-1-0385-1112-s029678 | 6 | 4 | 2 | 242.0 |
| line-1-0590-1069-s024177 | 6 | 4 | 2 | 242.0 |
| line-1-0710-1055-s021158 | 6 | 2 | 4 | 484.0 |
| line-1-0787-0961-s018133 | 6 | 2 | 4 | 484.0 |
| line-1-0862-0887-s015112 | 6 | 4 | 2 | 242.0 |
| line-1-0909-0919-s013050 | 6 | 4 | 2 | 242.0 |
| line-1-1018-0843-s010007 | 6 | 2 | 4 | 484.0 |
| line-1-1155-0814-s007003 | 8 | 2 | 6 | 726.0 |
| line-1-1269-0868-s003508 | 8 | 2 | 6 | 726.0 |
| line-1-1358-0772-s000000 | 4 | 2 | 2 | 242.0 |
| line-2-0277-0467-s029354 | 3 | 2 | 1 | 121.0 |
| line-2-0508-0679-s021091 | 6 | 4 | 2 | 242.0 |
| line-2-0601-0691-s018846 | 6 | 2 | 4 | 484.0 |
| line-2-0804-0839-s012068 | 6 | 2 | 4 | 484.0 |
| line-2-0869-0847-s010119 | 7 | 2 | 5 | 605.0 |
| line-2-0909-0919-s008165 | 8 | 4 | 4 | 484.0 |
| line-2-0955-0979-s006031 | 8 | 2 | 6 | 726.0 |
| line-2-1039-1072-s003016 | 8 | 2 | 6 | 726.0 |
| line-2-1142-1146-s000000 | 4 | 2 | 2 | 242.0 |
| line-3-0734-1177-s032011 | 6 | 2 | 4 | 484.0 |
| line-3-0746-1266-s034181 | 3 | 2 | 1 | 121.0 |
| line-3-0799-1036-s027687 | 6 | 2 | 4 | 484.0 |
| line-3-0805-1111-s029846 | 6 | 2 | 4 | 484.0 |
| line-3-0873-0941-s024685 | 6 | 4 | 2 | 242.0 |
| line-3-0889-0802-s020055 | 7 | 2 | 5 | 605.0 |
| line-3-0909-0919-s023468 | 6 | 4 | 2 | 242.0 |
| line-3-0987-0713-s017050 | 8 | 2 | 6 | 726.0 |
| line-3-1029-0434-s010250 | 8 | 4 | 4 | 484.0 |
| line-3-1037-0602-s014036 | 8 | 2 | 6 | 726.0 |
| line-3-1135-0045-s000000 | 4 | 2 | 2 | 242.0 |
| line-4-0816-1332-s000000 | 4 | 2 | 2 | 242.0 |
| line-4-0841-1172-s003842 | 8 | 2 | 6 | 726.0 |
| line-4-0954-1120-s006858 | 8 | 2 | 6 | 726.0 |
| line-4-1001-1002-s009880 | 7 | 2 | 5 | 605.0 |
| line-4-1043-0893-s012896 | 6 | 4 | 2 | 242.0 |
| line-4-1059-0777-s015896 | 6 | 2 | 4 | 484.0 |
| line-4-1170-0530-s022373 | 6 | 4 | 2 | 242.0 |
| line-4-1215-0384-s025701 | 3 | 2 | 1 | 121.0 |
| line-5-0597-0856-s000000 | 4 | 2 | 2 | 242.0 |
| line-5-0720-0904-s003016 | 8 | 2 | 6 | 726.0 |
| line-5-0841-0908-s005804 | 8 | 4 | 4 | 484.0 |
| line-5-0909-0919-s008390 | 8 | 4 | 4 | 484.0 |
| line-5-1049-0911-s011807 | 8 | 4 | 4 | 484.0 |
| line-5-1182-0923-s015312 | 7 | 2 | 5 | 605.0 |
| line-5-1347-0945-s018811 | 6 | 4 | 2 | 242.0 |
| line-5-1796-1080-s029230 | 3 | 2 | 1 | 121.0 |
| line-6-0642-0265-s035454 | 4 | 2 | 2 | 242.0 |
| line-6-0707-0497-s029531 | 8 | 4 | 4 | 484.0 |
| line-6-0853-0762-s022965 | 8 | 2 | 6 | 726.0 |
| line-6-0861-0888-s019957 | 8 | 4 | 4 | 484.0 |
| line-6-0871-1060-s015348 | 8 | 2 | 6 | 726.0 |
| line-6-0880-0953-s018351 | 8 | 4 | 4 | 484.0 |
| line-6-0918-1168-s012344 | 8 | 2 | 6 | 726.0 |
| line-6-1029-1312-s007668 | 8 | 4 | 4 | 484.0 |
| line-6-1067-1638-s000000 | 5 | 2 | 3 | 363.0 |
| line-7-0335-1662-s032343 | 4 | 2 | 2 | 242.0 |
| line-7-0518-1203-s019193 | 8 | 4 | 4 | 484.0 |
| line-7-0568-1052-s015061 | 8 | 4 | 4 | 484.0 |
| line-7-0650-0941-s012048 | 8 | 2 | 6 | 726.0 |
| line-7-0693-0834-s009040 | 8 | 2 | 6 | 726.0 |
| line-7-0796-0767-s006020 | 10 | 2 | 8 | 968.0 |
| line-7-0844-0649-s003002 | 10 | 2 | 8 | 968.0 |
| line-7-0871-0514-s000000 | 5 | 2 | 3 | 363.0 |
| line-8-0429-0242-s029503 | 3 | 2 | 1 | 121.0 |
| line-8-0725-0478-s021344 | 6 | 4 | 2 | 242.0 |
| line-8-0876-0715-s015030 | 8 | 2 | 6 | 726.0 |
| line-8-0960-0803-s012013 | 8 | 2 | 6 | 726.0 |
| line-8-1080-0870-s008995 | 8 | 2 | 6 | 726.0 |
| line-8-1158-0968-s005978 | 8 | 2 | 6 | 726.0 |
| line-8-1219-1148-s001381 | 8 | 4 | 4 | 484.0 |
| line-8-1281-1151-s000000 | 4 | 2 | 2 | 242.0 |
| line-9-0385-1112-s014917 | 2 | 4 | 0 | 0.0 |
| line-9-0412-0944-s010953 | 2 | 2 | 0 | 0.0 |
| line-9-0459-0786-s007005 | 2 | 2 | 0 | 0.0 |
| line-9-0508-0679-s004276 | 4 | 4 | 0 | 0.0 |
| line-9-0518-1203-s018376 | 2 | 4 | 0 | 0.0 |
| line-9-0629-1258-s021051 | 2 | 2 | 0 | 0.0 |
| line-9-0653-0546-s000000 | 4 | 2 | 2 | 242.0 |
| line-9-0707-0496-s071838 | 2 | 4 | 0 | 0.0 |
| line-9-0975-1352-s035103 | 2 | 2 | 0 | 0.0 |
| line-9-1029-0434-s064269 | 2 | 4 | 0 | 0.0 |
| line-9-1029-1312-s036514 | 2 | 4 | 0 | 0.0 |
| line-9-1170-0530-s060618 | 2 | 4 | 0 | 0.0 |
| line-9-1219-1148-s042287 | 2 | 4 | 0 | 0.0 |
| line-9-1358-0772-s051176 | 2 | 4 | 0 | 0.0 |
| line-9-1358-0945-s047533 | 2 | 4 | 0 | 0.0 |
| line-9-1361-0866-s049138 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Madagascar/Antananarivo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
