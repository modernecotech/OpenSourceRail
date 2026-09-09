# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **450 trainsets at 78 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **407 revenue, 36 spare, 7 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1783-1156-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-1743-1217-s003501 | forward | revenue | 4 | pending |
| line-1 | line-1-1743-1217-s003501 | reverse | revenue | 4 | pending |
| line-1 | line-1-1649-1110-s007001 | forward | revenue | 4 | pending |
| line-1 | line-1-1649-1110-s007001 | reverse | revenue | 4 | pending |
| line-1 | line-1-1533-1162-s010012 | forward | revenue | 4 | pending |
| line-1 | line-1-1533-1162-s010012 | reverse | revenue | 4 | pending |
| line-1 | line-1-1412-1120-s013028 | forward | revenue | 4 | pending |
| line-1 | line-1-1412-1120-s013028 | reverse | revenue | 4 | pending |
| line-1 | line-1-1290-1051-s016051 | forward | revenue | 4 | pending |
| line-1 | line-1-1290-1051-s016051 | reverse | revenue | 4 | pending |
| line-1 | line-1-1179-1006-s019070 | forward | revenue | 4 | pending |
| line-1 | line-1-1179-1006-s019070 | reverse | revenue | 4 | pending |
| line-1 | line-1-1075-1051-s022074 | forward | revenue | 4 | pending |
| line-1 | line-1-1075-1051-s022074 | reverse | revenue | 4 | pending |
| line-1 | line-1-0907-1014-s026073 | forward | revenue | 3 | pending |
| line-1 | line-1-0907-1014-s026073 | reverse | revenue | 3 | pending |
| line-1 | line-1-0731-0965-s030074 | forward | revenue | 3 | pending |
| line-1 | line-1-0731-0965-s030074 | reverse | revenue | 3 | pending |
| line-1 | line-1-0080-0724-s045164 | reverse | revenue | 3 | pending |
| line-1 | line-1-0907-1014-s026073 | forward | spare | 1 | pending |
| line-1 | line-1-0907-1014-s026073 | reverse | spare | 1 | pending |
| line-1 | line-1-0731-0965-s030074 | forward | spare | 1 | pending |
| line-1 | line-1-0731-0965-s030074 | reverse | spare | 1 | pending |
| line-1 | line-1-0080-0724-s045164 | reverse | spare | 1 | pending |
| line-1 | line-1-1783-1156-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-1743-1217-s003501 | forward | spare | 1 | pending |
| line-1 | line-1-1743-1217-s003501 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1620-1366-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1526-1311-s003022 | forward | revenue | 3 | pending |
| line-2 | line-2-1526-1311-s003022 | reverse | revenue | 3 | pending |
| line-2 | line-2-1416-1341-s006050 | forward | revenue | 3 | pending |
| line-2 | line-2-1416-1341-s006050 | reverse | revenue | 3 | pending |
| line-2 | line-2-1358-1332-s007661 | forward | revenue | 3 | pending |
| line-2 | line-2-1358-1332-s007661 | reverse | revenue | 3 | pending |
| line-2 | line-2-1247-1274-s010668 | forward | revenue | 2 | pending |
| line-2 | line-2-1247-1274-s010668 | reverse | revenue | 2 | pending |
| line-2 | line-2-1136-1208-s013671 | forward | revenue | 2 | pending |
| line-2 | line-2-1136-1208-s013671 | reverse | revenue | 2 | pending |
| line-2 | line-2-1076-1184-s015070 | forward | revenue | 2 | pending |
| line-2 | line-2-1076-1184-s015070 | reverse | revenue | 2 | pending |
| line-2 | line-2-0839-1170-s020211 | reverse | revenue | 2 | pending |
| line-2 | line-2-1247-1274-s010668 | forward | spare | 1 | pending |
| line-2 | line-2-1247-1274-s010668 | reverse | spare | 1 | pending |
| line-2 | line-2-1136-1208-s013671 | forward | spare | 1 | pending |
| line-2 | line-2-1136-1208-s013671 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1713-2270-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-1546-1613-s015159 | forward | revenue | 5 | pending |
| line-3 | line-3-1546-1613-s015159 | reverse | revenue | 5 | pending |
| line-3 | line-3-1428-1443-s020026 | forward | revenue | 5 | pending |
| line-3 | line-3-1428-1443-s020026 | reverse | revenue | 5 | pending |
| line-3 | line-3-1341-1372-s022761 | forward | revenue | 5 | pending |
| line-3 | line-3-1341-1372-s022761 | reverse | revenue | 5 | pending |
| line-3 | line-3-1380-1257-s025762 | forward | revenue | 4 | pending |
| line-3 | line-3-1380-1257-s025762 | reverse | revenue | 4 | pending |
| line-3 | line-3-1312-1166-s028769 | forward | revenue | 4 | pending |
| line-3 | line-3-1312-1166-s028769 | reverse | revenue | 4 | pending |
| line-3 | line-3-1327-1053-s031779 | forward | revenue | 4 | pending |
| line-3 | line-3-1327-1053-s031779 | reverse | revenue | 4 | pending |
| line-3 | line-3-1254-0968-s034799 | forward | revenue | 4 | pending |
| line-3 | line-3-1254-0968-s034799 | reverse | revenue | 4 | pending |
| line-3 | line-3-1251-0809-s039851 | forward | revenue | 4 | pending |
| line-3 | line-3-1251-0809-s039851 | reverse | revenue | 4 | pending |
| line-3 | line-3-1128-0589-s046101 | reverse | revenue | 4 | pending |
| line-3 | line-3-1380-1257-s025762 | forward | spare | 1 | pending |
| line-3 | line-3-1380-1257-s025762 | reverse | spare | 1 | pending |
| line-3 | line-3-1312-1166-s028769 | forward | spare | 1 | pending |
| line-3 | line-3-1312-1166-s028769 | reverse | spare | 1 | pending |
| line-3 | line-3-1327-1053-s031779 | forward | spare | 1 | pending |
| line-3 | line-3-1327-1053-s031779 | reverse | spare | 1 | pending |
| line-3 | line-3-1254-0968-s034799 | forward | spare | 1 | pending |
| line-3 | line-3-1254-0968-s034799 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1070-0777-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-1053-0889-s003316 | forward | revenue | 4 | pending |
| line-4 | line-4-1053-0889-s003316 | reverse | revenue | 4 | pending |
| line-4 | line-4-1099-0982-s006020 | forward | revenue | 4 | pending |
| line-4 | line-4-1099-0982-s006020 | reverse | revenue | 4 | pending |
| line-4 | line-4-1161-1092-s009026 | forward | revenue | 4 | pending |
| line-4 | line-4-1161-1092-s009026 | reverse | revenue | 4 | pending |
| line-4 | line-4-1183-1215-s012034 | forward | revenue | 4 | pending |
| line-4 | line-4-1183-1215-s012034 | reverse | revenue | 4 | pending |
| line-4 | line-4-1239-1344-s015542 | forward | revenue | 4 | pending |
| line-4 | line-4-1239-1344-s015542 | reverse | revenue | 4 | pending |
| line-4 | line-4-1266-1454-s018048 | forward | revenue | 3 | pending |
| line-4 | line-4-1266-1454-s018048 | reverse | revenue | 3 | pending |
| line-4 | line-4-1307-1612-s021548 | forward | revenue | 3 | pending |
| line-4 | line-4-1307-1612-s021548 | reverse | revenue | 3 | pending |
| line-4 | line-4-1341-1773-s025049 | forward | revenue | 3 | pending |
| line-4 | line-4-1341-1773-s025049 | reverse | revenue | 3 | pending |
| line-4 | line-4-1405-2361-s037340 | reverse | revenue | 3 | pending |
| line-4 | line-4-1266-1454-s018048 | forward | spare | 1 | pending |
| line-4 | line-4-1266-1454-s018048 | reverse | spare | 1 | pending |
| line-4 | line-4-1307-1612-s021548 | forward | spare | 1 | pending |
| line-4 | line-4-1307-1612-s021548 | reverse | spare | 1 | pending |
| line-4 | line-4-1341-1773-s025049 | forward | spare | 1 | pending |
| line-4 | line-4-1341-1773-s025049 | reverse | spare | 1 | pending |
| line-4 | line-4-1405-2361-s037340 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-2152-0348-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-1865-0778-s014021 | forward | revenue | 4 | pending |
| line-5 | line-5-1865-0778-s014021 | reverse | revenue | 4 | pending |
| line-5 | line-5-1673-1022-s020595 | forward | revenue | 4 | pending |
| line-5 | line-5-1673-1022-s020595 | reverse | revenue | 4 | pending |
| line-5 | line-5-1595-1071-s024565 | forward | revenue | 4 | pending |
| line-5 | line-5-1595-1071-s024565 | reverse | revenue | 4 | pending |
| line-5 | line-5-1502-1121-s027566 | forward | revenue | 4 | pending |
| line-5 | line-5-1502-1121-s027566 | reverse | revenue | 4 | pending |
| line-5 | line-5-1461-1240-s030591 | forward | revenue | 4 | pending |
| line-5 | line-5-1461-1240-s030591 | reverse | revenue | 4 | pending |
| line-5 | line-5-1368-1349-s033553 | forward | revenue | 4 | pending |
| line-5 | line-5-1368-1349-s033553 | reverse | revenue | 4 | pending |
| line-5 | line-5-1317-1409-s035187 | forward | revenue | 4 | pending |
| line-5 | line-5-1317-1409-s035187 | reverse | revenue | 4 | pending |
| line-5 | line-5-1260-1495-s037535 | forward | revenue | 3 | pending |
| line-5 | line-5-1260-1495-s037535 | reverse | revenue | 3 | pending |
| line-5 | line-5-1179-1578-s039866 | reverse | revenue | 3 | pending |
| line-5 | line-5-1260-1495-s037535 | forward | spare | 1 | pending |
| line-5 | line-5-1260-1495-s037535 | reverse | spare | 1 | pending |
| line-5 | line-5-1179-1578-s039866 | reverse | spare | 1 | pending |
| line-5 | line-5-2152-0348-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-1865-0778-s014021 | forward | spare | 1 | pending |
| line-5 | line-5-1865-0778-s014021 | reverse | spare | 1 | pending |
| line-5 | line-5-1673-1022-s020595 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-1003-0997-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-1118-0924-s003490 | forward | revenue | 3 | pending |
| line-6 | line-6-1118-0924-s003490 | reverse | revenue | 3 | pending |
| line-6 | line-6-1235-0922-s007005 | forward | revenue | 3 | pending |
| line-6 | line-6-1235-0922-s007005 | reverse | revenue | 3 | pending |
| line-6 | line-6-1368-0956-s010508 | forward | revenue | 3 | pending |
| line-6 | line-6-1368-0956-s010508 | reverse | revenue | 3 | pending |
| line-6 | line-6-1500-0853-s014018 | forward | revenue | 3 | pending |
| line-6 | line-6-1500-0853-s014018 | reverse | revenue | 3 | pending |
| line-6 | line-6-1638-0766-s017511 | forward | revenue | 3 | pending |
| line-6 | line-6-1638-0766-s017511 | reverse | revenue | 3 | pending |
| line-6 | line-6-1867-0766-s022091 | forward | revenue | 3 | pending |
| line-6 | line-6-1867-0766-s022091 | reverse | revenue | 3 | pending |
| line-6 | line-6-2004-0723-s025954 | forward | revenue | 3 | pending |
| line-6 | line-6-2004-0723-s025954 | reverse | revenue | 3 | pending |
| line-6 | line-6-2118-0683-s029836 | reverse | revenue | 3 | pending |
| line-6 | line-6-1118-0924-s003490 | forward | spare | 1 | pending |
| line-6 | line-6-1118-0924-s003490 | reverse | spare | 1 | pending |
| line-6 | line-6-1235-0922-s007005 | forward | spare | 1 | pending |
| line-6 | line-6-1235-0922-s007005 | reverse | spare | 1 | pending |
| line-6 | line-6-1368-0956-s010508 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-0731-0954-s000000 | forward | revenue | 1 | pending |
| line-7 | line-7-0731-0954-s000000 | reverse | revenue | 1 | pending |
| line-7 | line-7-0856-1018-s003511 | forward | revenue | 1 | pending |
| line-7 | line-7-0856-1018-s003511 | reverse | revenue | 1 | pending |
| line-7 | line-7-0995-1097-s007028 | forward | revenue | 1 | pending |
| line-7 | line-7-0995-1097-s007028 | reverse | revenue | 1 | pending |
| line-7 | line-7-1076-1184-s009579 | forward | revenue | 1 | pending |
| line-7 | line-7-1076-1184-s009579 | reverse | revenue | 1 | pending |
| line-7 | line-7-1169-1301-s013056 | forward | revenue | 1 | pending |
| line-7 | line-7-1169-1301-s013056 | reverse | revenue | 1 | pending |
| line-7 | line-7-1239-1344-s015152 | forward | revenue | 1 | pending |
| line-7 | line-7-1239-1344-s015152 | reverse | revenue | 1 | pending |
| line-7 | line-7-1317-1409-s017962 | forward | revenue | 1 | pending |
| line-7 | line-7-1317-1409-s017962 | reverse | revenue | 1 | pending |
| line-7 | line-7-1430-1469-s020975 | forward | revenue | 1 | pending |
| line-7 | line-7-1430-1469-s020975 | reverse | revenue | 1 | pending |
| line-7 | line-7-1570-1597-s026091 | forward | revenue | 1 | pending |
| line-7 | line-7-1570-1597-s026091 | reverse | revenue | 1 | pending |
| line-7 | line-7-1758-1787-s033093 | forward | revenue | 1 | pending |
| line-7 | line-7-1758-1787-s033093 | reverse | revenue | 1 | pending |
| line-7 | line-7-1726-1516-s040106 | forward | revenue | 1 | pending |
| line-7 | line-7-1726-1516-s040106 | reverse | revenue | 1 | pending |
| line-7 | line-7-1749-1350-s043617 | forward | revenue | 1 | pending |
| line-7 | line-7-1749-1350-s043617 | reverse | revenue | 1 | pending |
| line-7 | line-7-1825-1217-s047113 | forward | revenue | 1 | pending |
| line-7 | line-7-1825-1217-s047113 | reverse | revenue | 1 | pending |
| line-7 | line-7-1783-1156-s048681 | forward | revenue | 1 | pending |
| line-7 | line-7-1783-1156-s048681 | reverse | revenue | 1 | pending |
| line-7 | line-7-1867-0766-s057984 | forward | revenue | 1 | pending |
| line-7 | line-7-1867-0766-s057984 | reverse | revenue | 1 | pending |
| line-7 | line-7-1638-0736-s064473 | forward | revenue | 1 | pending |
| line-7 | line-7-1638-0736-s064473 | reverse | revenue | 1 | pending |
| line-7 | line-7-1481-0703-s068144 | forward | revenue | 1 | pending |
| line-7 | line-7-1481-0703-s068144 | reverse | revenue | 1 | pending |
| line-7 | line-7-1251-0809-s074062 | forward | revenue | 1 | pending |
| line-7 | line-7-1251-0809-s074062 | reverse | spare | 1 | pending |
| line-7 | line-7-1053-0889-s078884 | forward | spare | 1 | pending |
| line-7 | line-7-1053-0889-s078884 | reverse | spare | 1 | pending |
| line-7 | line-7-0803-0946-s085345 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**269 trainsets exceed the reference platform envelope**, requiring **32,549.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0080-0724-s045164 | 4 | 2 | 2 | 242.0 |
| line-1-0731-0965-s030074 | 8 | 4 | 4 | 484.0 |
| line-1-0907-1014-s026073 | 8 | 2 | 6 | 726.0 |
| line-1-1075-1051-s022074 | 8 | 2 | 6 | 726.0 |
| line-1-1179-1006-s019070 | 8 | 2 | 6 | 726.0 |
| line-1-1290-1051-s016051 | 8 | 2 | 6 | 726.0 |
| line-1-1412-1120-s013028 | 8 | 2 | 6 | 726.0 |
| line-1-1533-1162-s010012 | 8 | 2 | 6 | 726.0 |
| line-1-1649-1110-s007001 | 8 | 2 | 6 | 726.0 |
| line-1-1743-1217-s003501 | 10 | 2 | 8 | 968.0 |
| line-1-1783-1156-s000000 | 5 | 2 | 3 | 363.0 |
| line-2-0839-1170-s020211 | 2 | 2 | 0 | 0.0 |
| line-2-1076-1184-s015070 | 4 | 4 | 0 | 0.0 |
| line-2-1136-1208-s013671 | 6 | 2 | 4 | 484.0 |
| line-2-1247-1274-s010668 | 6 | 2 | 4 | 484.0 |
| line-2-1358-1332-s007661 | 6 | 4 | 2 | 242.0 |
| line-2-1416-1341-s006050 | 6 | 2 | 4 | 484.0 |
| line-2-1526-1311-s003022 | 6 | 2 | 4 | 484.0 |
| line-2-1620-1366-s000000 | 3 | 2 | 1 | 121.0 |
| line-3-1128-0589-s046101 | 4 | 2 | 2 | 242.0 |
| line-3-1251-0809-s039851 | 8 | 4 | 4 | 484.0 |
| line-3-1254-0968-s034799 | 10 | 2 | 8 | 968.0 |
| line-3-1312-1166-s028769 | 10 | 2 | 8 | 968.0 |
| line-3-1327-1053-s031779 | 10 | 2 | 8 | 968.0 |
| line-3-1341-1372-s022761 | 10 | 2 | 8 | 968.0 |
| line-3-1380-1257-s025762 | 10 | 2 | 8 | 968.0 |
| line-3-1428-1443-s020026 | 10 | 4 | 6 | 726.0 |
| line-3-1546-1613-s015159 | 10 | 4 | 6 | 726.0 |
| line-3-1713-2270-s000000 | 5 | 2 | 3 | 363.0 |
| line-4-1053-0889-s003316 | 8 | 4 | 4 | 484.0 |
| line-4-1070-0777-s000000 | 4 | 2 | 2 | 242.0 |
| line-4-1099-0982-s006020 | 8 | 2 | 6 | 726.0 |
| line-4-1161-1092-s009026 | 8 | 2 | 6 | 726.0 |
| line-4-1183-1215-s012034 | 8 | 2 | 6 | 726.0 |
| line-4-1239-1344-s015542 | 8 | 4 | 4 | 484.0 |
| line-4-1266-1454-s018048 | 8 | 2 | 6 | 726.0 |
| line-4-1307-1612-s021548 | 8 | 2 | 6 | 726.0 |
| line-4-1341-1773-s025049 | 8 | 2 | 6 | 726.0 |
| line-4-1405-2361-s037340 | 4 | 2 | 2 | 242.0 |
| line-5-1179-1578-s039866 | 4 | 2 | 2 | 242.0 |
| line-5-1260-1495-s037535 | 8 | 2 | 6 | 726.0 |
| line-5-1317-1409-s035187 | 8 | 4 | 4 | 484.0 |
| line-5-1368-1349-s033553 | 8 | 4 | 4 | 484.0 |
| line-5-1461-1240-s030591 | 8 | 2 | 6 | 726.0 |
| line-5-1502-1121-s027566 | 8 | 2 | 6 | 726.0 |
| line-5-1595-1071-s024565 | 8 | 2 | 6 | 726.0 |
| line-5-1673-1022-s020595 | 9 | 2 | 7 | 847.0 |
| line-5-1865-0778-s014021 | 10 | 4 | 6 | 726.0 |
| line-5-2152-0348-s000000 | 5 | 2 | 3 | 363.0 |
| line-6-1003-0997-s000000 | 4 | 2 | 2 | 242.0 |
| line-6-1118-0924-s003490 | 8 | 2 | 6 | 726.0 |
| line-6-1235-0922-s007005 | 8 | 2 | 6 | 726.0 |
| line-6-1368-0956-s010508 | 7 | 2 | 5 | 605.0 |
| line-6-1500-0853-s014018 | 6 | 2 | 4 | 484.0 |
| line-6-1638-0766-s017511 | 6 | 4 | 2 | 242.0 |
| line-6-1867-0766-s022091 | 6 | 4 | 2 | 242.0 |
| line-6-2004-0723-s025954 | 6 | 2 | 4 | 484.0 |
| line-6-2118-0683-s029836 | 3 | 2 | 1 | 121.0 |
| line-7-0731-0954-s000000 | 2 | 4 | 0 | 0.0 |
| line-7-0803-0946-s085345 | 1 | 2 | 0 | 0.0 |
| line-7-0856-1018-s003511 | 2 | 2 | 0 | 0.0 |
| line-7-0995-1097-s007028 | 2 | 2 | 0 | 0.0 |
| line-7-1053-0889-s078884 | 2 | 4 | 0 | 0.0 |
| line-7-1076-1184-s009579 | 2 | 4 | 0 | 0.0 |
| line-7-1169-1301-s013056 | 2 | 2 | 0 | 0.0 |
| line-7-1239-1344-s015152 | 2 | 4 | 0 | 0.0 |
| line-7-1251-0809-s074062 | 2 | 4 | 0 | 0.0 |
| line-7-1317-1409-s017962 | 2 | 4 | 0 | 0.0 |
| line-7-1430-1469-s020975 | 2 | 4 | 0 | 0.0 |
| line-7-1481-0703-s068144 | 2 | 2 | 0 | 0.0 |
| line-7-1570-1597-s026091 | 2 | 4 | 0 | 0.0 |
| line-7-1638-0736-s064473 | 2 | 4 | 0 | 0.0 |
| line-7-1726-1516-s040106 | 2 | 2 | 0 | 0.0 |
| line-7-1749-1350-s043617 | 2 | 2 | 0 | 0.0 |
| line-7-1758-1787-s033093 | 2 | 2 | 0 | 0.0 |
| line-7-1783-1156-s048681 | 2 | 4 | 0 | 0.0 |
| line-7-1825-1217-s047113 | 2 | 2 | 0 | 0.0 |
| line-7-1867-0766-s057984 | 2 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Basra/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
