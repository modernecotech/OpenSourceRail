# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **784 trainsets at 128 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **707 revenue, 68 spare, 9 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1887-2051-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-1773-1885-s004342 | forward | revenue | 4 | pending |
| line-1 | line-1-1773-1885-s004342 | reverse | revenue | 3 | pending |
| line-1 | line-1-1698-1782-s007024 | forward | revenue | 3 | pending |
| line-1 | line-1-1698-1782-s007024 | reverse | revenue | 3 | pending |
| line-1 | line-1-1623-1637-s010545 | forward | revenue | 3 | pending |
| line-1 | line-1-1623-1637-s010545 | reverse | revenue | 3 | pending |
| line-1 | line-1-1486-1594-s014048 | forward | revenue | 3 | pending |
| line-1 | line-1-1486-1594-s014048 | reverse | revenue | 3 | pending |
| line-1 | line-1-1458-1447-s018392 | forward | revenue | 3 | pending |
| line-1 | line-1-1458-1447-s018392 | reverse | revenue | 3 | pending |
| line-1 | line-1-1353-1355-s021394 | forward | revenue | 3 | pending |
| line-1 | line-1-1353-1355-s021394 | reverse | revenue | 3 | pending |
| line-1 | line-1-1236-1261-s024541 | forward | revenue | 3 | pending |
| line-1 | line-1-1236-1261-s024541 | reverse | revenue | 3 | pending |
| line-1 | line-1-1133-1167-s027443 | forward | revenue | 3 | pending |
| line-1 | line-1-1133-1167-s027443 | reverse | revenue | 3 | pending |
| line-1 | line-1-1050-1063-s030434 | forward | revenue | 3 | pending |
| line-1 | line-1-1050-1063-s030434 | reverse | revenue | 3 | pending |
| line-1 | line-1-0939-0992-s033434 | forward | revenue | 3 | pending |
| line-1 | line-1-0939-0992-s033434 | reverse | revenue | 3 | pending |
| line-1 | line-1-0866-0909-s036452 | forward | revenue | 3 | pending |
| line-1 | line-1-0866-0909-s036452 | reverse | revenue | 3 | pending |
| line-1 | line-1-0789-0824-s039469 | forward | revenue | 3 | pending |
| line-1 | line-1-0789-0824-s039469 | reverse | revenue | 3 | pending |
| line-1 | line-1-0759-0777-s040959 | forward | revenue | 3 | pending |
| line-1 | line-1-0759-0777-s040959 | reverse | revenue | 3 | pending |
| line-1 | line-1-0690-0594-s046489 | forward | revenue | 3 | pending |
| line-1 | line-1-0690-0594-s046489 | reverse | revenue | 3 | pending |
| line-1 | line-1-0325-0249-s058110 | reverse | revenue | 3 | pending |
| line-1 | line-1-1773-1885-s004342 | reverse | spare | 1 | pending |
| line-1 | line-1-1698-1782-s007024 | forward | spare | 1 | pending |
| line-1 | line-1-1698-1782-s007024 | reverse | spare | 1 | pending |
| line-1 | line-1-1623-1637-s010545 | forward | spare | 1 | pending |
| line-1 | line-1-1623-1637-s010545 | reverse | spare | 1 | pending |
| line-1 | line-1-1486-1594-s014048 | forward | spare | 1 | pending |
| line-1 | line-1-1486-1594-s014048 | reverse | spare | 1 | pending |
| line-1 | line-1-1458-1447-s018392 | forward | spare | 1 | pending |
| line-1 | line-1-1458-1447-s018392 | reverse | spare | 1 | pending |
| line-1 | line-1-1353-1355-s021394 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0680-0190-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0946-0594-s014028 | forward | revenue | 4 | pending |
| line-2 | line-2-0946-0594-s014028 | reverse | revenue | 4 | pending |
| line-2 | line-2-1000-0599-s015253 | forward | revenue | 4 | pending |
| line-2 | line-2-1000-0599-s015253 | reverse | revenue | 4 | pending |
| line-2 | line-2-1087-0716-s019213 | forward | revenue | 4 | pending |
| line-2 | line-2-1087-0716-s019213 | reverse | revenue | 4 | pending |
| line-2 | line-2-1177-0838-s022948 | forward | revenue | 4 | pending |
| line-2 | line-2-1177-0838-s022948 | reverse | revenue | 4 | pending |
| line-2 | line-2-1197-0912-s025237 | forward | revenue | 4 | pending |
| line-2 | line-2-1197-0912-s025237 | reverse | revenue | 4 | pending |
| line-2 | line-2-1288-0967-s027513 | forward | revenue | 4 | pending |
| line-2 | line-2-1288-0967-s027513 | reverse | revenue | 4 | pending |
| line-2 | line-2-1386-1057-s031033 | forward | revenue | 4 | pending |
| line-2 | line-2-1386-1057-s031033 | reverse | revenue | 4 | pending |
| line-2 | line-2-1483-1187-s034536 | forward | revenue | 4 | pending |
| line-2 | line-2-1483-1187-s034536 | reverse | revenue | 4 | pending |
| line-2 | line-2-1607-1416-s040176 | forward | revenue | 3 | pending |
| line-2 | line-2-1607-1416-s040176 | reverse | revenue | 3 | pending |
| line-2 | line-2-1746-1584-s045806 | reverse | revenue | 3 | pending |
| line-2 | line-2-1607-1416-s040176 | forward | spare | 1 | pending |
| line-2 | line-2-1607-1416-s040176 | reverse | spare | 1 | pending |
| line-2 | line-2-1746-1584-s045806 | reverse | spare | 1 | pending |
| line-2 | line-2-0680-0190-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0946-0594-s014028 | forward | spare | 1 | pending |
| line-2 | line-2-0946-0594-s014028 | reverse | spare | 1 | pending |
| line-2 | line-2-1000-0599-s015253 | forward | spare | 1 | pending |
| line-2 | line-2-1000-0599-s015253 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-2322-0251-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-1684-0768-s017540 | forward | revenue | 4 | pending |
| line-3 | line-3-1684-0768-s017540 | reverse | revenue | 4 | pending |
| line-3 | line-3-1539-0821-s021055 | forward | revenue | 4 | pending |
| line-3 | line-3-1539-0821-s021055 | reverse | revenue | 4 | pending |
| line-3 | line-3-1454-0827-s022805 | forward | revenue | 4 | pending |
| line-3 | line-3-1454-0827-s022805 | reverse | revenue | 4 | pending |
| line-3 | line-3-1262-0916-s028059 | forward | revenue | 4 | pending |
| line-3 | line-3-1262-0916-s028059 | reverse | revenue | 4 | pending |
| line-3 | line-3-1161-0996-s031069 | forward | revenue | 4 | pending |
| line-3 | line-3-1161-0996-s031069 | reverse | revenue | 4 | pending |
| line-3 | line-3-1054-1076-s034076 | forward | revenue | 4 | pending |
| line-3 | line-3-1054-1076-s034076 | reverse | revenue | 4 | pending |
| line-3 | line-3-0961-1180-s037083 | forward | revenue | 4 | pending |
| line-3 | line-3-0961-1180-s037083 | reverse | revenue | 4 | pending |
| line-3 | line-3-0836-1237-s040576 | forward | revenue | 4 | pending |
| line-3 | line-3-0836-1237-s040576 | reverse | revenue | 4 | pending |
| line-3 | line-3-0798-1376-s044091 | forward | revenue | 3 | pending |
| line-3 | line-3-0798-1376-s044091 | reverse | revenue | 3 | pending |
| line-3 | line-3-0671-1392-s048934 | forward | revenue | 3 | pending |
| line-3 | line-3-0671-1392-s048934 | reverse | revenue | 3 | pending |
| line-3 | line-3-0635-1421-s050340 | forward | revenue | 3 | pending |
| line-3 | line-3-0635-1421-s050340 | reverse | revenue | 3 | pending |
| line-3 | line-3-0642-1488-s051738 | forward | revenue | 3 | pending |
| line-3 | line-3-0642-1488-s051738 | reverse | revenue | 3 | pending |
| line-3 | line-3-0492-1526-s055088 | reverse | revenue | 3 | pending |
| line-3 | line-3-0798-1376-s044091 | forward | spare | 1 | pending |
| line-3 | line-3-0798-1376-s044091 | reverse | spare | 1 | pending |
| line-3 | line-3-0671-1392-s048934 | forward | spare | 1 | pending |
| line-3 | line-3-0671-1392-s048934 | reverse | spare | 1 | pending |
| line-3 | line-3-0635-1421-s050340 | forward | spare | 1 | pending |
| line-3 | line-3-0635-1421-s050340 | reverse | spare | 1 | pending |
| line-3 | line-3-0642-1488-s051738 | forward | spare | 1 | pending |
| line-3 | line-3-0642-1488-s051738 | reverse | spare | 1 | pending |
| line-3 | line-3-0492-1526-s055088 | reverse | spare | 1 | pending |
| line-3 | line-3-2322-0251-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-1066-0011-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-1089-0575-s012508 | forward | revenue | 4 | pending |
| line-4 | line-4-1089-0575-s012508 | reverse | revenue | 4 | pending |
| line-4 | line-4-1117-0610-s013947 | forward | revenue | 4 | pending |
| line-4 | line-4-1117-0610-s013947 | reverse | revenue | 4 | pending |
| line-4 | line-4-1016-0700-s017777 | forward | revenue | 4 | pending |
| line-4 | line-4-1016-0700-s017777 | reverse | revenue | 4 | pending |
| line-4 | line-4-1021-0806-s020133 | forward | revenue | 4 | pending |
| line-4 | line-4-1021-0806-s020133 | reverse | revenue | 4 | pending |
| line-4 | line-4-1020-0920-s022471 | forward | revenue | 4 | pending |
| line-4 | line-4-1020-0920-s022471 | reverse | revenue | 4 | pending |
| line-4 | line-4-1049-1038-s025474 | forward | revenue | 4 | pending |
| line-4 | line-4-1049-1038-s025474 | reverse | revenue | 4 | pending |
| line-4 | line-4-1081-1162-s028474 | forward | revenue | 3 | pending |
| line-4 | line-4-1081-1162-s028474 | reverse | revenue | 3 | pending |
| line-4 | line-4-1086-1279-s031487 | forward | revenue | 3 | pending |
| line-4 | line-4-1086-1279-s031487 | reverse | revenue | 3 | pending |
| line-4 | line-4-1067-1415-s034504 | forward | revenue | 3 | pending |
| line-4 | line-4-1067-1415-s034504 | reverse | revenue | 3 | pending |
| line-4 | line-4-1053-1573-s038011 | forward | revenue | 3 | pending |
| line-4 | line-4-1053-1573-s038011 | reverse | revenue | 3 | pending |
| line-4 | line-4-1128-1669-s041512 | forward | revenue | 3 | pending |
| line-4 | line-4-1128-1669-s041512 | reverse | revenue | 3 | pending |
| line-4 | line-4-1085-1926-s047058 | forward | revenue | 3 | pending |
| line-4 | line-4-1085-1926-s047058 | reverse | revenue | 3 | pending |
| line-4 | line-4-1069-2206-s052920 | reverse | revenue | 3 | pending |
| line-4 | line-4-1081-1162-s028474 | forward | spare | 1 | pending |
| line-4 | line-4-1081-1162-s028474 | reverse | spare | 1 | pending |
| line-4 | line-4-1086-1279-s031487 | forward | spare | 1 | pending |
| line-4 | line-4-1086-1279-s031487 | reverse | spare | 1 | pending |
| line-4 | line-4-1067-1415-s034504 | forward | spare | 1 | pending |
| line-4 | line-4-1067-1415-s034504 | reverse | spare | 1 | pending |
| line-4 | line-4-1053-1573-s038011 | forward | spare | 1 | pending |
| line-4 | line-4-1053-1573-s038011 | reverse | spare | 1 | pending |
| line-4 | line-4-1128-1669-s041512 | forward | spare | 1 | pending |
| line-4 | line-4-1128-1669-s041512 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0092-0824-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0477-0978-s010519 | forward | revenue | 3 | pending |
| line-5 | line-5-0477-0978-s010519 | reverse | revenue | 3 | pending |
| line-5 | line-5-0607-1005-s014019 | forward | revenue | 3 | pending |
| line-5 | line-5-0607-1005-s014019 | reverse | revenue | 3 | pending |
| line-5 | line-5-0683-0980-s015907 | forward | revenue | 3 | pending |
| line-5 | line-5-0683-0980-s015907 | reverse | revenue | 3 | pending |
| line-5 | line-5-0757-0981-s017994 | forward | revenue | 3 | pending |
| line-5 | line-5-0757-0981-s017994 | reverse | revenue | 3 | pending |
| line-5 | line-5-0829-1000-s020057 | forward | revenue | 3 | pending |
| line-5 | line-5-0829-1000-s020057 | reverse | revenue | 3 | pending |
| line-5 | line-5-0930-1026-s023062 | forward | revenue | 3 | pending |
| line-5 | line-5-0930-1026-s023062 | reverse | revenue | 3 | pending |
| line-5 | line-5-1012-1075-s025439 | forward | revenue | 3 | pending |
| line-5 | line-5-1012-1075-s025439 | reverse | revenue | 3 | pending |
| line-5 | line-5-1122-1077-s028446 | forward | revenue | 3 | pending |
| line-5 | line-5-1122-1077-s028446 | reverse | revenue | 3 | pending |
| line-5 | line-5-1183-1159-s031474 | forward | revenue | 3 | pending |
| line-5 | line-5-1183-1159-s031474 | reverse | revenue | 3 | pending |
| line-5 | line-5-1310-1217-s034494 | forward | revenue | 3 | pending |
| line-5 | line-5-1310-1217-s034494 | reverse | revenue | 3 | pending |
| line-5 | line-5-1446-1239-s037514 | forward | revenue | 3 | pending |
| line-5 | line-5-1446-1239-s037514 | reverse | revenue | 3 | pending |
| line-5 | line-5-1711-1271-s043123 | reverse | revenue | 3 | pending |
| line-5 | line-5-0477-0978-s010519 | forward | spare | 1 | pending |
| line-5 | line-5-0477-0978-s010519 | reverse | spare | 1 | pending |
| line-5 | line-5-0607-1005-s014019 | forward | spare | 1 | pending |
| line-5 | line-5-0607-1005-s014019 | reverse | spare | 1 | pending |
| line-5 | line-5-0683-0980-s015907 | forward | spare | 1 | pending |
| line-5 | line-5-0683-0980-s015907 | reverse | spare | 1 | pending |
| line-5 | line-5-0757-0981-s017994 | forward | spare | 1 | pending |
| line-5 | line-5-0757-0981-s017994 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0578-1225-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-0706-1155-s003561 | forward | revenue | 4 | pending |
| line-6 | line-6-0706-1155-s003561 | reverse | revenue | 4 | pending |
| line-6 | line-6-0830-1128-s007007 | forward | revenue | 4 | pending |
| line-6 | line-6-0830-1128-s007007 | reverse | revenue | 4 | pending |
| line-6 | line-6-0935-1132-s010008 | forward | revenue | 4 | pending |
| line-6 | line-6-0935-1132-s010008 | reverse | revenue | 4 | pending |
| line-6 | line-6-1010-1072-s012100 | forward | revenue | 4 | pending |
| line-6 | line-6-1010-1072-s012100 | reverse | revenue | 4 | pending |
| line-6 | line-6-1139-1043-s015121 | forward | revenue | 4 | pending |
| line-6 | line-6-1139-1043-s015121 | reverse | revenue | 4 | pending |
| line-6 | line-6-1213-0998-s017189 | forward | revenue | 4 | pending |
| line-6 | line-6-1213-0998-s017189 | reverse | revenue | 4 | pending |
| line-6 | line-6-1298-0951-s019279 | forward | revenue | 4 | pending |
| line-6 | line-6-1298-0951-s019279 | reverse | revenue | 4 | pending |
| line-6 | line-6-1423-0924-s022785 | forward | revenue | 3 | pending |
| line-6 | line-6-1423-0924-s022785 | reverse | revenue | 3 | pending |
| line-6 | line-6-1537-0888-s026284 | forward | revenue | 3 | pending |
| line-6 | line-6-1537-0888-s026284 | reverse | revenue | 3 | pending |
| line-6 | line-6-1677-0835-s029789 | forward | revenue | 3 | pending |
| line-6 | line-6-1677-0835-s029789 | reverse | revenue | 3 | pending |
| line-6 | line-6-2399-0681-s047232 | reverse | revenue | 3 | pending |
| line-6 | line-6-1423-0924-s022785 | forward | spare | 1 | pending |
| line-6 | line-6-1423-0924-s022785 | reverse | spare | 1 | pending |
| line-6 | line-6-1537-0888-s026284 | forward | spare | 1 | pending |
| line-6 | line-6-1537-0888-s026284 | reverse | spare | 1 | pending |
| line-6 | line-6-1677-0835-s029789 | forward | spare | 1 | pending |
| line-6 | line-6-1677-0835-s029789 | reverse | spare | 1 | pending |
| line-6 | line-6-2399-0681-s047232 | reverse | spare | 1 | pending |
| line-6 | line-6-0578-1225-s000000 | forward | spare | 1 | pending |
| line-6 | line-6-0706-1155-s003561 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-1333-0171-s000000 | forward | revenue | 4 | pending |
| line-7 | line-7-1170-0574-s011592 | forward | revenue | 4 | pending |
| line-7 | line-7-1170-0574-s011592 | reverse | revenue | 4 | pending |
| line-7 | line-7-1160-0671-s014028 | forward | revenue | 4 | pending |
| line-7 | line-7-1160-0671-s014028 | reverse | revenue | 4 | pending |
| line-7 | line-7-1206-0781-s017032 | forward | revenue | 4 | pending |
| line-7 | line-7-1206-0781-s017032 | reverse | revenue | 4 | pending |
| line-7 | line-7-1144-0923-s020385 | forward | revenue | 4 | pending |
| line-7 | line-7-1144-0923-s020385 | reverse | revenue | 4 | pending |
| line-7 | line-7-1067-1026-s023400 | forward | revenue | 4 | pending |
| line-7 | line-7-1067-1026-s023400 | reverse | revenue | 4 | pending |
| line-7 | line-7-1033-1153-s026410 | forward | revenue | 4 | pending |
| line-7 | line-7-1033-1153-s026410 | reverse | revenue | 4 | pending |
| line-7 | line-7-0989-1264-s029415 | forward | revenue | 4 | pending |
| line-7 | line-7-0989-1264-s029415 | reverse | revenue | 4 | pending |
| line-7 | line-7-0931-1355-s032422 | forward | revenue | 4 | pending |
| line-7 | line-7-0931-1355-s032422 | reverse | revenue | 4 | pending |
| line-7 | line-7-0934-1493-s035918 | forward | revenue | 4 | pending |
| line-7 | line-7-0934-1493-s035918 | reverse | revenue | 4 | pending |
| line-7 | line-7-0844-1600-s039434 | forward | revenue | 4 | pending |
| line-7 | line-7-0844-1600-s039434 | reverse | revenue | 4 | pending |
| line-7 | line-7-0818-1820-s044108 | forward | revenue | 3 | pending |
| line-7 | line-7-0818-1820-s044108 | reverse | revenue | 3 | pending |
| line-7 | line-7-0677-2304-s056905 | reverse | revenue | 3 | pending |
| line-7 | line-7-0818-1820-s044108 | forward | spare | 1 | pending |
| line-7 | line-7-0818-1820-s044108 | reverse | spare | 1 | pending |
| line-7 | line-7-0677-2304-s056905 | reverse | spare | 1 | pending |
| line-7 | line-7-1333-0171-s000000 | forward | spare | 1 | pending |
| line-7 | line-7-1170-0574-s011592 | forward | spare | 1 | pending |
| line-7 | line-7-1170-0574-s011592 | reverse | spare | 1 | pending |
| line-7 | line-7-1160-0671-s014028 | forward | spare | 1 | pending |
| line-7 | line-7-1160-0671-s014028 | reverse | spare | 1 | pending |
| line-7 | line-7-1206-0781-s017032 | forward | spare | 1 | pending |
| line-7 | line-7-1206-0781-s017032 | reverse | cold_reserve | 1 | pending |
| line-8 | line-8-1329-1654-s000000 | forward | revenue | 4 | pending |
| line-8 | line-8-1234-1574-s003008 | forward | revenue | 4 | pending |
| line-8 | line-8-1234-1574-s003008 | reverse | revenue | 4 | pending |
| line-8 | line-8-1137-1464-s006011 | forward | revenue | 4 | pending |
| line-8 | line-8-1137-1464-s006011 | reverse | revenue | 4 | pending |
| line-8 | line-8-1037-1359-s009022 | forward | revenue | 4 | pending |
| line-8 | line-8-1037-1359-s009022 | reverse | revenue | 4 | pending |
| line-8 | line-8-0935-1250-s012047 | forward | revenue | 4 | pending |
| line-8 | line-8-0935-1250-s012047 | reverse | revenue | 4 | pending |
| line-8 | line-8-0797-1126-s016088 | forward | revenue | 4 | pending |
| line-8 | line-8-0797-1126-s016088 | reverse | revenue | 4 | pending |
| line-8 | line-8-0683-0980-s020125 | forward | revenue | 4 | pending |
| line-8 | line-8-0683-0980-s020125 | reverse | revenue | 3 | pending |
| line-8 | line-8-0483-0766-s026085 | forward | revenue | 3 | pending |
| line-8 | line-8-0483-0766-s026085 | reverse | revenue | 3 | pending |
| line-8 | line-8-0172-0482-s036358 | reverse | revenue | 3 | pending |
| line-8 | line-8-0683-0980-s020125 | reverse | spare | 1 | pending |
| line-8 | line-8-0483-0766-s026085 | forward | spare | 1 | pending |
| line-8 | line-8-0483-0766-s026085 | reverse | spare | 1 | pending |
| line-8 | line-8-0172-0482-s036358 | reverse | spare | 1 | pending |
| line-8 | line-8-1329-1654-s000000 | forward | spare | 1 | pending |
| line-8 | line-8-1234-1574-s003008 | forward | spare | 1 | pending |
| line-8 | line-8-1234-1574-s003008 | reverse | cold_reserve | 1 | pending |
| line-9 | line-9-1077-0587-s000000 | forward | revenue | 1 | pending |
| line-9 | line-9-1077-0587-s000000 | reverse | revenue | 1 | pending |
| line-9 | line-9-1000-0599-s001639 | forward | revenue | 1 | pending |
| line-9 | line-9-1000-0599-s001639 | reverse | revenue | 1 | pending |
| line-9 | line-9-0852-0705-s007003 | forward | revenue | 1 | pending |
| line-9 | line-9-0852-0705-s007003 | reverse | revenue | 1 | pending |
| line-9 | line-9-0752-0777-s010404 | forward | revenue | 1 | pending |
| line-9 | line-9-0752-0777-s010404 | reverse | revenue | 1 | pending |
| line-9 | line-9-0701-0868-s012787 | forward | revenue | 1 | pending |
| line-9 | line-9-0701-0868-s012787 | reverse | revenue | 1 | pending |
| line-9 | line-9-0683-0980-s015176 | forward | revenue | 1 | pending |
| line-9 | line-9-0683-0980-s015176 | reverse | revenue | 1 | pending |
| line-9 | line-9-0678-1063-s017431 | forward | revenue | 1 | pending |
| line-9 | line-9-0678-1063-s017431 | reverse | revenue | 1 | pending |
| line-9 | line-9-0706-1155-s019991 | forward | revenue | 1 | pending |
| line-9 | line-9-0706-1155-s019991 | reverse | revenue | 1 | pending |
| line-9 | line-9-0673-1305-s024441 | forward | revenue | 1 | pending |
| line-9 | line-9-0673-1305-s024441 | reverse | revenue | 1 | pending |
| line-9 | line-9-0671-1392-s026706 | forward | revenue | 1 | pending |
| line-9 | line-9-0671-1392-s026706 | reverse | revenue | 1 | pending |
| line-9 | line-9-0656-1509-s030208 | forward | revenue | 1 | pending |
| line-9 | line-9-0656-1509-s030208 | reverse | revenue | 1 | pending |
| line-9 | line-9-0647-1566-s031456 | forward | revenue | 1 | pending |
| line-9 | line-9-0647-1566-s031456 | reverse | revenue | 1 | pending |
| line-9 | line-9-0811-1813-s038468 | forward | revenue | 1 | pending |
| line-9 | line-9-0952-1896-s041975 | forward | revenue | 1 | pending |
| line-9 | line-9-0952-1896-s041975 | reverse | revenue | 1 | pending |
| line-9 | line-9-1096-1923-s045493 | forward | revenue | 1 | pending |
| line-9 | line-9-1096-1923-s045493 | reverse | revenue | 1 | pending |
| line-9 | line-9-1260-1895-s049005 | forward | revenue | 1 | pending |
| line-9 | line-9-1260-1895-s049005 | reverse | revenue | 1 | pending |
| line-9 | line-9-1425-1881-s052504 | forward | revenue | 1 | pending |
| line-9 | line-9-1425-1881-s052504 | reverse | revenue | 1 | pending |
| line-9 | line-9-1773-1885-s061819 | forward | revenue | 1 | pending |
| line-9 | line-9-1773-1885-s061819 | reverse | revenue | 1 | pending |
| line-9 | line-9-1816-1198-s080536 | forward | revenue | 1 | pending |
| line-9 | line-9-1816-1198-s080536 | reverse | revenue | 1 | pending |
| line-9 | line-9-1740-1076-s084039 | forward | revenue | 1 | pending |
| line-9 | line-9-1740-1076-s084039 | reverse | revenue | 1 | pending |
| line-9 | line-9-1634-0996-s087548 | forward | revenue | 1 | pending |
| line-9 | line-9-1634-0996-s087548 | reverse | revenue | 1 | pending |
| line-9 | line-9-1536-0895-s090741 | forward | revenue | 1 | pending |
| line-9 | line-9-1536-0895-s090741 | reverse | revenue | 1 | pending |
| line-9 | line-9-1454-0827-s093562 | forward | revenue | 1 | pending |
| line-9 | line-9-1454-0827-s093562 | reverse | revenue | 1 | pending |
| line-9 | line-9-1383-0699-s097570 | forward | spare | 1 | pending |
| line-9 | line-9-1383-0699-s097570 | reverse | spare | 1 | pending |
| line-9 | line-9-1264-0604-s101562 | forward | spare | 1 | pending |
| line-9 | line-9-1264-0604-s101562 | reverse | spare | 1 | pending |
| line-9 | line-9-1170-0574-s103690 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**486 trainsets exceed the reference platform envelope**, requiring **58,806.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0325-0249-s058110 | 3 | 2 | 1 | 121.0 |
| line-1-0690-0594-s046489 | 6 | 2 | 4 | 484.0 |
| line-1-0759-0777-s040959 | 6 | 4 | 2 | 242.0 |
| line-1-0789-0824-s039469 | 6 | 2 | 4 | 484.0 |
| line-1-0866-0909-s036452 | 6 | 2 | 4 | 484.0 |
| line-1-0939-0992-s033434 | 6 | 2 | 4 | 484.0 |
| line-1-1050-1063-s030434 | 6 | 4 | 2 | 242.0 |
| line-1-1133-1167-s027443 | 6 | 2 | 4 | 484.0 |
| line-1-1236-1261-s024541 | 6 | 2 | 4 | 484.0 |
| line-1-1353-1355-s021394 | 7 | 2 | 5 | 605.0 |
| line-1-1458-1447-s018392 | 8 | 2 | 6 | 726.0 |
| line-1-1486-1594-s014048 | 8 | 2 | 6 | 726.0 |
| line-1-1623-1637-s010545 | 8 | 2 | 6 | 726.0 |
| line-1-1698-1782-s007024 | 8 | 2 | 6 | 726.0 |
| line-1-1773-1885-s004342 | 8 | 4 | 4 | 484.0 |
| line-1-1887-2051-s000000 | 4 | 2 | 2 | 242.0 |
| line-2-0680-0190-s000000 | 5 | 2 | 3 | 363.0 |
| line-2-0946-0594-s014028 | 10 | 2 | 8 | 968.0 |
| line-2-1000-0599-s015253 | 10 | 4 | 6 | 726.0 |
| line-2-1087-0716-s019213 | 8 | 2 | 6 | 726.0 |
| line-2-1177-0838-s022948 | 8 | 2 | 6 | 726.0 |
| line-2-1197-0912-s025237 | 8 | 2 | 6 | 726.0 |
| line-2-1288-0967-s027513 | 8 | 4 | 4 | 484.0 |
| line-2-1386-1057-s031033 | 8 | 2 | 6 | 726.0 |
| line-2-1483-1187-s034536 | 8 | 2 | 6 | 726.0 |
| line-2-1607-1416-s040176 | 8 | 2 | 6 | 726.0 |
| line-2-1746-1584-s045806 | 4 | 2 | 2 | 242.0 |
| line-3-0492-1526-s055088 | 4 | 2 | 2 | 242.0 |
| line-3-0635-1421-s050340 | 8 | 2 | 6 | 726.0 |
| line-3-0642-1488-s051738 | 8 | 4 | 4 | 484.0 |
| line-3-0671-1392-s048934 | 8 | 4 | 4 | 484.0 |
| line-3-0798-1376-s044091 | 8 | 2 | 6 | 726.0 |
| line-3-0836-1237-s040576 | 8 | 2 | 6 | 726.0 |
| line-3-0961-1180-s037083 | 8 | 2 | 6 | 726.0 |
| line-3-1054-1076-s034076 | 8 | 4 | 4 | 484.0 |
| line-3-1161-0996-s031069 | 8 | 2 | 6 | 726.0 |
| line-3-1262-0916-s028059 | 8 | 2 | 6 | 726.0 |
| line-3-1454-0827-s022805 | 8 | 4 | 4 | 484.0 |
| line-3-1539-0821-s021055 | 8 | 2 | 6 | 726.0 |
| line-3-1684-0768-s017540 | 8 | 2 | 6 | 726.0 |
| line-3-2322-0251-s000000 | 5 | 2 | 3 | 363.0 |
| line-4-1016-0700-s017777 | 8 | 2 | 6 | 726.0 |
| line-4-1020-0920-s022471 | 8 | 2 | 6 | 726.0 |
| line-4-1021-0806-s020133 | 8 | 2 | 6 | 726.0 |
| line-4-1049-1038-s025474 | 8 | 4 | 4 | 484.0 |
| line-4-1053-1573-s038011 | 8 | 2 | 6 | 726.0 |
| line-4-1066-0011-s000000 | 4 | 2 | 2 | 242.0 |
| line-4-1067-1415-s034504 | 8 | 2 | 6 | 726.0 |
| line-4-1069-2206-s052920 | 3 | 2 | 1 | 121.0 |
| line-4-1081-1162-s028474 | 8 | 2 | 6 | 726.0 |
| line-4-1085-1926-s047058 | 6 | 4 | 2 | 242.0 |
| line-4-1086-1279-s031487 | 8 | 2 | 6 | 726.0 |
| line-4-1089-0575-s012508 | 8 | 4 | 4 | 484.0 |
| line-4-1117-0610-s013947 | 8 | 2 | 6 | 726.0 |
| line-4-1128-1669-s041512 | 8 | 2 | 6 | 726.0 |
| line-5-0092-0824-s000000 | 4 | 2 | 2 | 242.0 |
| line-5-0477-0978-s010519 | 8 | 2 | 6 | 726.0 |
| line-5-0607-1005-s014019 | 8 | 2 | 6 | 726.0 |
| line-5-0683-0980-s015907 | 8 | 4 | 4 | 484.0 |
| line-5-0757-0981-s017994 | 8 | 2 | 6 | 726.0 |
| line-5-0829-1000-s020057 | 6 | 2 | 4 | 484.0 |
| line-5-0930-1026-s023062 | 6 | 2 | 4 | 484.0 |
| line-5-1012-1075-s025439 | 6 | 4 | 2 | 242.0 |
| line-5-1122-1077-s028446 | 6 | 2 | 4 | 484.0 |
| line-5-1183-1159-s031474 | 6 | 2 | 4 | 484.0 |
| line-5-1310-1217-s034494 | 6 | 2 | 4 | 484.0 |
| line-5-1446-1239-s037514 | 6 | 2 | 4 | 484.0 |
| line-5-1711-1271-s043123 | 3 | 2 | 1 | 121.0 |
| line-6-0578-1225-s000000 | 5 | 2 | 3 | 363.0 |
| line-6-0706-1155-s003561 | 9 | 4 | 5 | 605.0 |
| line-6-0830-1128-s007007 | 8 | 2 | 6 | 726.0 |
| line-6-0935-1132-s010008 | 8 | 2 | 6 | 726.0 |
| line-6-1010-1072-s012100 | 8 | 4 | 4 | 484.0 |
| line-6-1139-1043-s015121 | 8 | 2 | 6 | 726.0 |
| line-6-1213-0998-s017189 | 8 | 2 | 6 | 726.0 |
| line-6-1298-0951-s019279 | 8 | 4 | 4 | 484.0 |
| line-6-1423-0924-s022785 | 8 | 2 | 6 | 726.0 |
| line-6-1537-0888-s026284 | 8 | 4 | 4 | 484.0 |
| line-6-1677-0835-s029789 | 8 | 2 | 6 | 726.0 |
| line-6-2399-0681-s047232 | 4 | 2 | 2 | 242.0 |
| line-7-0677-2304-s056905 | 4 | 2 | 2 | 242.0 |
| line-7-0818-1820-s044108 | 8 | 4 | 4 | 484.0 |
| line-7-0844-1600-s039434 | 8 | 2 | 6 | 726.0 |
| line-7-0931-1355-s032422 | 8 | 2 | 6 | 726.0 |
| line-7-0934-1493-s035918 | 8 | 2 | 6 | 726.0 |
| line-7-0989-1264-s029415 | 8 | 2 | 6 | 726.0 |
| line-7-1033-1153-s026410 | 8 | 2 | 6 | 726.0 |
| line-7-1067-1026-s023400 | 8 | 4 | 4 | 484.0 |
| line-7-1144-0923-s020385 | 8 | 2 | 6 | 726.0 |
| line-7-1160-0671-s014028 | 10 | 2 | 8 | 968.0 |
| line-7-1170-0574-s011592 | 10 | 4 | 6 | 726.0 |
| line-7-1206-0781-s017032 | 10 | 2 | 8 | 968.0 |
| line-7-1333-0171-s000000 | 5 | 2 | 3 | 363.0 |
| line-8-0172-0482-s036358 | 4 | 2 | 2 | 242.0 |
| line-8-0483-0766-s026085 | 8 | 2 | 6 | 726.0 |
| line-8-0683-0980-s020125 | 8 | 4 | 4 | 484.0 |
| line-8-0797-1126-s016088 | 8 | 2 | 6 | 726.0 |
| line-8-0935-1250-s012047 | 8 | 2 | 6 | 726.0 |
| line-8-1037-1359-s009022 | 8 | 2 | 6 | 726.0 |
| line-8-1137-1464-s006011 | 8 | 2 | 6 | 726.0 |
| line-8-1234-1574-s003008 | 10 | 2 | 8 | 968.0 |
| line-8-1329-1654-s000000 | 5 | 2 | 3 | 363.0 |
| line-9-0647-1566-s031456 | 2 | 2 | 0 | 0.0 |
| line-9-0656-1509-s030208 | 2 | 4 | 0 | 0.0 |
| line-9-0671-1392-s026706 | 2 | 4 | 0 | 0.0 |
| line-9-0673-1305-s024441 | 2 | 2 | 0 | 0.0 |
| line-9-0678-1063-s017431 | 2 | 2 | 0 | 0.0 |
| line-9-0683-0980-s015176 | 2 | 4 | 0 | 0.0 |
| line-9-0701-0868-s012787 | 2 | 2 | 0 | 0.0 |
| line-9-0706-1155-s019991 | 2 | 4 | 0 | 0.0 |
| line-9-0752-0777-s010404 | 2 | 4 | 0 | 0.0 |
| line-9-0811-1813-s038468 | 1 | 4 | 0 | 0.0 |
| line-9-0852-0705-s007003 | 2 | 2 | 0 | 0.0 |
| line-9-0952-1896-s041975 | 2 | 2 | 0 | 0.0 |
| line-9-1000-0599-s001639 | 2 | 4 | 0 | 0.0 |
| line-9-1077-0587-s000000 | 2 | 4 | 0 | 0.0 |
| line-9-1096-1923-s045493 | 2 | 4 | 0 | 0.0 |
| line-9-1170-0574-s103690 | 1 | 4 | 0 | 0.0 |
| line-9-1260-1895-s049005 | 2 | 2 | 0 | 0.0 |
| line-9-1264-0604-s101562 | 2 | 2 | 0 | 0.0 |
| line-9-1383-0699-s097570 | 2 | 2 | 0 | 0.0 |
| line-9-1425-1881-s052504 | 2 | 2 | 0 | 0.0 |
| line-9-1454-0827-s093562 | 2 | 4 | 0 | 0.0 |
| line-9-1536-0895-s090741 | 2 | 4 | 0 | 0.0 |
| line-9-1634-0996-s087548 | 2 | 2 | 0 | 0.0 |
| line-9-1740-1076-s084039 | 2 | 2 | 0 | 0.0 |
| line-9-1773-1885-s061819 | 2 | 4 | 0 | 0.0 |
| line-9-1816-1198-s080536 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Baghdad/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
