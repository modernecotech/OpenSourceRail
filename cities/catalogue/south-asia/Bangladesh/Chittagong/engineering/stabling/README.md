# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **517 trainsets at 88 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **465 revenue, 44 spare, 8 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1737-1246-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-1633-1148-s003516 | forward | revenue | 4 | pending |
| line-1 | line-1-1633-1148-s003516 | reverse | revenue | 4 | pending |
| line-1 | line-1-1470-1129-s007017 | forward | revenue | 4 | pending |
| line-1 | line-1-1470-1129-s007017 | reverse | revenue | 4 | pending |
| line-1 | line-1-1340-1133-s010027 | forward | revenue | 4 | pending |
| line-1 | line-1-1340-1133-s010027 | reverse | revenue | 4 | pending |
| line-1 | line-1-1218-1113-s013032 | forward | revenue | 4 | pending |
| line-1 | line-1-1218-1113-s013032 | reverse | revenue | 4 | pending |
| line-1 | line-1-1081-1091-s016037 | forward | revenue | 4 | pending |
| line-1 | line-1-1081-1091-s016037 | reverse | revenue | 4 | pending |
| line-1 | line-1-0971-1030-s019063 | forward | revenue | 4 | pending |
| line-1 | line-1-0971-1030-s019063 | reverse | revenue | 4 | pending |
| line-1 | line-1-0837-0998-s022075 | forward | revenue | 4 | pending |
| line-1 | line-1-0837-0998-s022075 | reverse | revenue | 4 | pending |
| line-1 | line-1-0704-0958-s025578 | forward | revenue | 4 | pending |
| line-1 | line-1-0704-0958-s025578 | reverse | revenue | 3 | pending |
| line-1 | line-1-0045-0697-s041910 | reverse | revenue | 3 | pending |
| line-1 | line-1-0704-0958-s025578 | reverse | spare | 1 | pending |
| line-1 | line-1-0045-0697-s041910 | reverse | spare | 1 | pending |
| line-1 | line-1-1737-1246-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-1633-1148-s003516 | forward | spare | 1 | pending |
| line-1 | line-1-1633-1148-s003516 | reverse | spare | 1 | pending |
| line-1 | line-1-1470-1129-s007017 | forward | spare | 1 | pending |
| line-1 | line-1-1470-1129-s007017 | reverse | spare | 1 | pending |
| line-1 | line-1-1340-1133-s010027 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1714-1318-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1653-1296-s002656 | forward | revenue | 3 | pending |
| line-2 | line-2-1653-1296-s002656 | reverse | revenue | 3 | pending |
| line-2 | line-2-1488-1297-s006096 | forward | revenue | 3 | pending |
| line-2 | line-2-1488-1297-s006096 | reverse | revenue | 3 | pending |
| line-2 | line-2-1435-1322-s007623 | forward | revenue | 3 | pending |
| line-2 | line-2-1435-1322-s007623 | reverse | revenue | 3 | pending |
| line-2 | line-2-1395-1373-s009111 | forward | revenue | 2 | pending |
| line-2 | line-2-1395-1373-s009111 | reverse | revenue | 2 | pending |
| line-2 | line-2-1301-1375-s012128 | forward | revenue | 2 | pending |
| line-2 | line-2-1301-1375-s012128 | reverse | revenue | 2 | pending |
| line-2 | line-2-1189-1399-s015148 | forward | revenue | 2 | pending |
| line-2 | line-2-1189-1399-s015148 | reverse | revenue | 2 | pending |
| line-2 | line-2-1079-1356-s018150 | forward | revenue | 2 | pending |
| line-2 | line-2-1079-1356-s018150 | reverse | revenue | 2 | pending |
| line-2 | line-2-0976-1327-s021167 | forward | revenue | 2 | pending |
| line-2 | line-2-0976-1327-s021167 | reverse | revenue | 2 | pending |
| line-2 | line-2-0915-1367-s023120 | forward | revenue | 2 | pending |
| line-2 | line-2-0915-1367-s023120 | reverse | revenue | 2 | pending |
| line-2 | line-2-0831-1358-s025080 | forward | revenue | 2 | pending |
| line-2 | line-2-0831-1358-s025080 | reverse | revenue | 2 | pending |
| line-2 | line-2-0679-1422-s028984 | reverse | revenue | 2 | pending |
| line-2 | line-2-1395-1373-s009111 | forward | spare | 1 | pending |
| line-2 | line-2-1395-1373-s009111 | reverse | spare | 1 | pending |
| line-2 | line-2-1301-1375-s012128 | forward | spare | 1 | pending |
| line-2 | line-2-1301-1375-s012128 | reverse | spare | 1 | pending |
| line-2 | line-2-1189-1399-s015148 | forward | spare | 1 | pending |
| line-2 | line-2-1189-1399-s015148 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0371-1207-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0599-1332-s005789 | forward | revenue | 4 | pending |
| line-3 | line-3-0599-1332-s005789 | reverse | revenue | 4 | pending |
| line-3 | line-3-0648-1357-s007004 | forward | revenue | 4 | pending |
| line-3 | line-3-0648-1357-s007004 | reverse | revenue | 4 | pending |
| line-3 | line-3-0789-1416-s010499 | forward | revenue | 4 | pending |
| line-3 | line-3-0789-1416-s010499 | reverse | revenue | 4 | pending |
| line-3 | line-3-0947-1451-s014010 | forward | revenue | 4 | pending |
| line-3 | line-3-0947-1451-s014010 | reverse | revenue | 4 | pending |
| line-3 | line-3-1074-1491-s017759 | forward | revenue | 4 | pending |
| line-3 | line-3-1074-1491-s017759 | reverse | revenue | 4 | pending |
| line-3 | line-3-1137-1487-s020777 | forward | revenue | 4 | pending |
| line-3 | line-3-1137-1487-s020777 | reverse | revenue | 4 | pending |
| line-3 | line-3-1217-1561-s023787 | forward | revenue | 4 | pending |
| line-3 | line-3-1217-1561-s023787 | reverse | revenue | 3 | pending |
| line-3 | line-3-1331-1560-s026795 | forward | revenue | 3 | pending |
| line-3 | line-3-1331-1560-s026795 | reverse | revenue | 3 | pending |
| line-3 | line-3-1536-1633-s031679 | forward | revenue | 3 | pending |
| line-3 | line-3-1536-1633-s031679 | reverse | revenue | 3 | pending |
| line-3 | line-3-1624-1621-s033804 | forward | revenue | 3 | pending |
| line-3 | line-3-1624-1621-s033804 | reverse | revenue | 3 | pending |
| line-3 | line-3-2205-1847-s047618 | reverse | revenue | 3 | pending |
| line-3 | line-3-1217-1561-s023787 | reverse | spare | 1 | pending |
| line-3 | line-3-1331-1560-s026795 | forward | spare | 1 | pending |
| line-3 | line-3-1331-1560-s026795 | reverse | spare | 1 | pending |
| line-3 | line-3-1536-1633-s031679 | forward | spare | 1 | pending |
| line-3 | line-3-1536-1633-s031679 | reverse | spare | 1 | pending |
| line-3 | line-3-1624-1621-s033804 | forward | spare | 1 | pending |
| line-3 | line-3-1624-1621-s033804 | reverse | spare | 1 | pending |
| line-3 | line-3-2205-1847-s047618 | reverse | spare | 1 | pending |
| line-3 | line-3-0371-1207-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0617-2159-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0959-1741-s012286 | forward | revenue | 4 | pending |
| line-4 | line-4-0959-1741-s012286 | reverse | revenue | 4 | pending |
| line-4 | line-4-0983-1678-s014040 | forward | revenue | 4 | pending |
| line-4 | line-4-0983-1678-s014040 | reverse | revenue | 4 | pending |
| line-4 | line-4-1074-1491-s018925 | forward | revenue | 4 | pending |
| line-4 | line-4-1074-1491-s018925 | reverse | revenue | 4 | pending |
| line-4 | line-4-1163-1398-s021940 | forward | revenue | 3 | pending |
| line-4 | line-4-1163-1398-s021940 | reverse | revenue | 3 | pending |
| line-4 | line-4-1251-1309-s025137 | forward | revenue | 3 | pending |
| line-4 | line-4-1251-1309-s025137 | reverse | revenue | 3 | pending |
| line-4 | line-4-1337-1294-s027972 | forward | revenue | 3 | pending |
| line-4 | line-4-1337-1294-s027972 | reverse | revenue | 3 | pending |
| line-4 | line-4-1397-1259-s030507 | forward | revenue | 3 | pending |
| line-4 | line-4-1397-1259-s030507 | reverse | revenue | 3 | pending |
| line-4 | line-4-1410-1170-s033320 | reverse | revenue | 3 | pending |
| line-4 | line-4-1163-1398-s021940 | forward | spare | 1 | pending |
| line-4 | line-4-1163-1398-s021940 | reverse | spare | 1 | pending |
| line-4 | line-4-1251-1309-s025137 | forward | spare | 1 | pending |
| line-4 | line-4-1251-1309-s025137 | reverse | spare | 1 | pending |
| line-4 | line-4-1337-1294-s027972 | forward | spare | 1 | pending |
| line-4 | line-4-1337-1294-s027972 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-1359-1166-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-1269-1226-s003008 | forward | revenue | 5 | pending |
| line-5 | line-5-1269-1226-s003008 | reverse | revenue | 5 | pending |
| line-5 | line-5-1182-1246-s006031 | forward | revenue | 5 | pending |
| line-5 | line-5-1182-1246-s006031 | reverse | revenue | 5 | pending |
| line-5 | line-5-1048-1274-s009042 | forward | revenue | 5 | pending |
| line-5 | line-5-1048-1274-s009042 | reverse | revenue | 5 | pending |
| line-5 | line-5-0960-1370-s012059 | forward | revenue | 4 | pending |
| line-5 | line-5-0960-1370-s012059 | reverse | revenue | 4 | pending |
| line-5 | line-5-0773-1507-s017747 | forward | revenue | 4 | pending |
| line-5 | line-5-0773-1507-s017747 | reverse | revenue | 4 | pending |
| line-5 | line-5-0707-1508-s019076 | forward | revenue | 4 | pending |
| line-5 | line-5-0707-1508-s019076 | reverse | revenue | 4 | pending |
| line-5 | line-5-0210-1918-s035819 | reverse | revenue | 4 | pending |
| line-5 | line-5-0960-1370-s012059 | forward | spare | 1 | pending |
| line-5 | line-5-0960-1370-s012059 | reverse | spare | 1 | pending |
| line-5 | line-5-0773-1507-s017747 | forward | spare | 1 | pending |
| line-5 | line-5-0773-1507-s017747 | reverse | spare | 1 | pending |
| line-5 | line-5-0707-1508-s019076 | forward | spare | 1 | pending |
| line-5 | line-5-0707-1508-s019076 | reverse | spare | 1 | pending |
| line-5 | line-5-0210-1918-s035819 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-1096-1139-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-1175-1241-s003186 | forward | revenue | 4 | pending |
| line-6 | line-6-1175-1241-s003186 | reverse | revenue | 4 | pending |
| line-6 | line-6-1174-1364-s006033 | forward | revenue | 4 | pending |
| line-6 | line-6-1174-1364-s006033 | reverse | revenue | 4 | pending |
| line-6 | line-6-1198-1433-s007645 | forward | revenue | 4 | pending |
| line-6 | line-6-1198-1433-s007645 | reverse | revenue | 4 | pending |
| line-6 | line-6-1233-1535-s010653 | forward | revenue | 4 | pending |
| line-6 | line-6-1233-1535-s010653 | reverse | revenue | 4 | pending |
| line-6 | line-6-1299-1618-s014170 | forward | revenue | 4 | pending |
| line-6 | line-6-1299-1618-s014170 | reverse | revenue | 4 | pending |
| line-6 | line-6-1355-1741-s017668 | forward | revenue | 3 | pending |
| line-6 | line-6-1355-1741-s017668 | reverse | revenue | 3 | pending |
| line-6 | line-6-1529-2226-s029926 | reverse | revenue | 3 | pending |
| line-6 | line-6-1355-1741-s017668 | forward | spare | 1 | pending |
| line-6 | line-6-1355-1741-s017668 | reverse | spare | 1 | pending |
| line-6 | line-6-1529-2226-s029926 | reverse | spare | 1 | pending |
| line-6 | line-6-1096-1139-s000000 | forward | spare | 1 | pending |
| line-6 | line-6-1175-1241-s003186 | forward | spare | 1 | pending |
| line-6 | line-6-1175-1241-s003186 | reverse | cold_reserve | 1 | pending |
| line-7 | line-7-1201-1087-s000000 | forward | revenue | 5 | pending |
| line-7 | line-7-1203-1204-s002995 | forward | revenue | 5 | pending |
| line-7 | line-7-1203-1204-s002995 | reverse | revenue | 5 | pending |
| line-7 | line-7-1336-1233-s006035 | forward | revenue | 5 | pending |
| line-7 | line-7-1336-1233-s006035 | reverse | revenue | 5 | pending |
| line-7 | line-7-1364-1334-s008452 | forward | revenue | 5 | pending |
| line-7 | line-7-1364-1334-s008452 | reverse | revenue | 5 | pending |
| line-7 | line-7-1391-1457-s012062 | forward | revenue | 5 | pending |
| line-7 | line-7-1391-1457-s012062 | reverse | revenue | 4 | pending |
| line-7 | line-7-1541-1606-s016859 | forward | revenue | 4 | pending |
| line-7 | line-7-1541-1606-s016859 | reverse | revenue | 4 | pending |
| line-7 | line-7-1628-1659-s019085 | forward | revenue | 4 | pending |
| line-7 | line-7-1628-1659-s019085 | reverse | revenue | 4 | pending |
| line-7 | line-7-2014-2377-s037034 | reverse | revenue | 4 | pending |
| line-7 | line-7-1391-1457-s012062 | reverse | spare | 1 | pending |
| line-7 | line-7-1541-1606-s016859 | forward | spare | 1 | pending |
| line-7 | line-7-1541-1606-s016859 | reverse | spare | 1 | pending |
| line-7 | line-7-1628-1659-s019085 | forward | spare | 1 | pending |
| line-7 | line-7-1628-1659-s019085 | reverse | spare | 1 | pending |
| line-7 | line-7-2014-2377-s037034 | reverse | spare | 1 | pending |
| line-7 | line-7-1201-1087-s000000 | forward | cold_reserve | 1 | pending |
| line-8 | line-8-0586-1192-s000000 | forward | revenue | 1 | pending |
| line-8 | line-8-0586-1192-s000000 | reverse | revenue | 1 | pending |
| line-8 | line-8-0599-1332-s004070 | forward | revenue | 1 | pending |
| line-8 | line-8-0599-1332-s004070 | reverse | revenue | 1 | pending |
| line-8 | line-8-0679-1422-s006873 | reverse | revenue | 1 | pending |
| line-8 | line-8-0773-1507-s009743 | forward | revenue | 1 | pending |
| line-8 | line-8-0773-1507-s009743 | reverse | revenue | 1 | pending |
| line-8 | line-8-0901-1661-s014036 | reverse | revenue | 1 | pending |
| line-8 | line-8-0959-1741-s016304 | forward | revenue | 1 | pending |
| line-8 | line-8-0959-1741-s016304 | reverse | revenue | 1 | pending |
| line-8 | line-8-1131-1886-s021039 | reverse | revenue | 1 | pending |
| line-8 | line-8-1355-1753-s027020 | forward | revenue | 1 | pending |
| line-8 | line-8-1355-1753-s027020 | reverse | revenue | 1 | pending |
| line-8 | line-8-1536-1633-s032528 | reverse | revenue | 1 | pending |
| line-8 | line-8-1591-1530-s035055 | forward | revenue | 1 | pending |
| line-8 | line-8-1591-1530-s035055 | reverse | revenue | 1 | pending |
| line-8 | line-8-1714-1318-s041760 | reverse | revenue | 1 | pending |
| line-8 | line-8-1653-1296-s043212 | forward | revenue | 1 | pending |
| line-8 | line-8-1653-1296-s043212 | reverse | revenue | 1 | pending |
| line-8 | line-8-1502-1269-s046472 | forward | revenue | 1 | pending |
| line-8 | line-8-1398-1284-s049393 | forward | revenue | 1 | pending |
| line-8 | line-8-1398-1284-s049393 | reverse | revenue | 1 | pending |
| line-8 | line-8-1364-1334-s050825 | forward | revenue | 1 | pending |
| line-8 | line-8-1304-1358-s052518 | forward | revenue | 1 | pending |
| line-8 | line-8-1304-1358-s052518 | reverse | revenue | 1 | pending |
| line-8 | line-8-1251-1309-s054219 | forward | revenue | 1 | pending |
| line-8 | line-8-1195-1247-s056085 | forward | revenue | 1 | pending |
| line-8 | line-8-1195-1247-s056085 | reverse | revenue | 1 | pending |
| line-8 | line-8-1088-1218-s058543 | forward | revenue | 1 | pending |
| line-8 | line-8-0932-1191-s062051 | forward | spare | 1 | pending |
| line-8 | line-8-0932-1191-s062051 | reverse | spare | 1 | pending |
| line-8 | line-8-0763-1188-s065556 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**317 trainsets exceed the reference platform envelope**, requiring **38,357.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0045-0697-s041910 | 4 | 2 | 2 | 242.0 |
| line-1-0704-0958-s025578 | 8 | 2 | 6 | 726.0 |
| line-1-0837-0998-s022075 | 8 | 2 | 6 | 726.0 |
| line-1-0971-1030-s019063 | 8 | 2 | 6 | 726.0 |
| line-1-1081-1091-s016037 | 8 | 2 | 6 | 726.0 |
| line-1-1218-1113-s013032 | 8 | 2 | 6 | 726.0 |
| line-1-1340-1133-s010027 | 9 | 2 | 7 | 847.0 |
| line-1-1470-1129-s007017 | 10 | 2 | 8 | 968.0 |
| line-1-1633-1148-s003516 | 10 | 2 | 8 | 968.0 |
| line-1-1737-1246-s000000 | 5 | 2 | 3 | 363.0 |
| line-2-0679-1422-s028984 | 2 | 2 | 0 | 0.0 |
| line-2-0831-1358-s025080 | 4 | 2 | 2 | 242.0 |
| line-2-0915-1367-s023120 | 4 | 2 | 2 | 242.0 |
| line-2-0976-1327-s021167 | 4 | 2 | 2 | 242.0 |
| line-2-1079-1356-s018150 | 4 | 2 | 2 | 242.0 |
| line-2-1189-1399-s015148 | 6 | 4 | 2 | 242.0 |
| line-2-1301-1375-s012128 | 6 | 4 | 2 | 242.0 |
| line-2-1395-1373-s009111 | 6 | 2 | 4 | 484.0 |
| line-2-1435-1322-s007623 | 6 | 2 | 4 | 484.0 |
| line-2-1488-1297-s006096 | 6 | 2 | 4 | 484.0 |
| line-2-1653-1296-s002656 | 6 | 4 | 2 | 242.0 |
| line-2-1714-1318-s000000 | 3 | 2 | 1 | 121.0 |
| line-3-0371-1207-s000000 | 5 | 2 | 3 | 363.0 |
| line-3-0599-1332-s005789 | 8 | 4 | 4 | 484.0 |
| line-3-0648-1357-s007004 | 8 | 2 | 6 | 726.0 |
| line-3-0789-1416-s010499 | 8 | 2 | 6 | 726.0 |
| line-3-0947-1451-s014010 | 8 | 2 | 6 | 726.0 |
| line-3-1074-1491-s017759 | 8 | 4 | 4 | 484.0 |
| line-3-1137-1487-s020777 | 8 | 2 | 6 | 726.0 |
| line-3-1217-1561-s023787 | 8 | 2 | 6 | 726.0 |
| line-3-1331-1560-s026795 | 8 | 2 | 6 | 726.0 |
| line-3-1536-1633-s031679 | 8 | 4 | 4 | 484.0 |
| line-3-1624-1621-s033804 | 8 | 2 | 6 | 726.0 |
| line-3-2205-1847-s047618 | 4 | 2 | 2 | 242.0 |
| line-4-0617-2159-s000000 | 4 | 2 | 2 | 242.0 |
| line-4-0959-1741-s012286 | 8 | 4 | 4 | 484.0 |
| line-4-0983-1678-s014040 | 8 | 2 | 6 | 726.0 |
| line-4-1074-1491-s018925 | 8 | 4 | 4 | 484.0 |
| line-4-1163-1398-s021940 | 8 | 4 | 4 | 484.0 |
| line-4-1251-1309-s025137 | 8 | 4 | 4 | 484.0 |
| line-4-1337-1294-s027972 | 8 | 2 | 6 | 726.0 |
| line-4-1397-1259-s030507 | 6 | 4 | 2 | 242.0 |
| line-4-1410-1170-s033320 | 3 | 2 | 1 | 121.0 |
| line-5-0210-1918-s035819 | 5 | 2 | 3 | 363.0 |
| line-5-0707-1508-s019076 | 10 | 2 | 8 | 968.0 |
| line-5-0773-1507-s017747 | 10 | 4 | 6 | 726.0 |
| line-5-0960-1370-s012059 | 10 | 2 | 8 | 968.0 |
| line-5-1048-1274-s009042 | 10 | 2 | 8 | 968.0 |
| line-5-1182-1246-s006031 | 10 | 4 | 6 | 726.0 |
| line-5-1269-1226-s003008 | 10 | 2 | 8 | 968.0 |
| line-5-1359-1166-s000000 | 5 | 2 | 3 | 363.0 |
| line-6-1096-1139-s000000 | 5 | 2 | 3 | 363.0 |
| line-6-1174-1364-s006033 | 8 | 2 | 6 | 726.0 |
| line-6-1175-1241-s003186 | 10 | 4 | 6 | 726.0 |
| line-6-1198-1433-s007645 | 8 | 2 | 6 | 726.0 |
| line-6-1233-1535-s010653 | 8 | 2 | 6 | 726.0 |
| line-6-1299-1618-s014170 | 8 | 2 | 6 | 726.0 |
| line-6-1355-1741-s017668 | 8 | 4 | 4 | 484.0 |
| line-6-1529-2226-s029926 | 4 | 2 | 2 | 242.0 |
| line-7-1201-1087-s000000 | 6 | 2 | 4 | 484.0 |
| line-7-1203-1204-s002995 | 10 | 2 | 8 | 968.0 |
| line-7-1336-1233-s006035 | 10 | 2 | 8 | 968.0 |
| line-7-1364-1334-s008452 | 10 | 4 | 6 | 726.0 |
| line-7-1391-1457-s012062 | 10 | 2 | 8 | 968.0 |
| line-7-1541-1606-s016859 | 10 | 4 | 6 | 726.0 |
| line-7-1628-1659-s019085 | 10 | 2 | 8 | 968.0 |
| line-7-2014-2377-s037034 | 5 | 2 | 3 | 363.0 |
| line-8-0586-1192-s000000 | 2 | 2 | 0 | 0.0 |
| line-8-0599-1332-s004070 | 2 | 4 | 0 | 0.0 |
| line-8-0679-1422-s006873 | 1 | 4 | 0 | 0.0 |
| line-8-0763-1188-s065556 | 1 | 2 | 0 | 0.0 |
| line-8-0773-1507-s009743 | 2 | 4 | 0 | 0.0 |
| line-8-0901-1661-s014036 | 1 | 2 | 0 | 0.0 |
| line-8-0932-1191-s062051 | 2 | 2 | 0 | 0.0 |
| line-8-0959-1741-s016304 | 2 | 4 | 0 | 0.0 |
| line-8-1088-1218-s058543 | 1 | 2 | 0 | 0.0 |
| line-8-1131-1886-s021039 | 1 | 2 | 0 | 0.0 |
| line-8-1195-1247-s056085 | 2 | 4 | 0 | 0.0 |
| line-8-1251-1309-s054219 | 1 | 4 | 0 | 0.0 |
| line-8-1304-1358-s052518 | 2 | 4 | 0 | 0.0 |
| line-8-1355-1753-s027020 | 2 | 4 | 0 | 0.0 |
| line-8-1364-1334-s050825 | 1 | 4 | 0 | 0.0 |
| line-8-1398-1284-s049393 | 2 | 4 | 0 | 0.0 |
| line-8-1502-1269-s046472 | 1 | 2 | 0 | 0.0 |
| line-8-1536-1633-s032528 | 1 | 4 | 0 | 0.0 |
| line-8-1591-1530-s035055 | 2 | 2 | 0 | 0.0 |
| line-8-1653-1296-s043212 | 2 | 4 | 0 | 0.0 |
| line-8-1714-1318-s041760 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Chittagong/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
