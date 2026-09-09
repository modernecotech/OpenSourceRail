# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **312 trainsets at 82 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **281 revenue, 25 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1519-1491-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-1402-1367-s003508 | forward | revenue | 3 | pending |
| line-1 | line-1-1402-1367-s003508 | reverse | revenue | 3 | pending |
| line-1 | line-1-1254-1326-s007007 | forward | revenue | 2 | pending |
| line-1 | line-1-1254-1326-s007007 | reverse | revenue | 2 | pending |
| line-1 | line-1-1176-1230-s010569 | forward | revenue | 2 | pending |
| line-1 | line-1-1176-1230-s010569 | reverse | revenue | 2 | pending |
| line-1 | line-1-1059-1216-s013025 | forward | revenue | 2 | pending |
| line-1 | line-1-1059-1216-s013025 | reverse | revenue | 2 | pending |
| line-1 | line-1-1015-1184-s014264 | forward | revenue | 2 | pending |
| line-1 | line-1-1015-1184-s014264 | reverse | revenue | 2 | pending |
| line-1 | line-1-0976-1139-s016037 | forward | revenue | 2 | pending |
| line-1 | line-1-0976-1139-s016037 | reverse | revenue | 2 | pending |
| line-1 | line-1-0900-1071-s019045 | forward | revenue | 2 | pending |
| line-1 | line-1-0900-1071-s019045 | reverse | revenue | 2 | pending |
| line-1 | line-1-0831-0981-s022048 | forward | revenue | 2 | pending |
| line-1 | line-1-0831-0981-s022048 | reverse | revenue | 2 | pending |
| line-1 | line-1-0738-0935-s025070 | forward | revenue | 2 | pending |
| line-1 | line-1-0738-0935-s025070 | reverse | revenue | 2 | pending |
| line-1 | line-1-0662-0868-s028076 | forward | revenue | 2 | pending |
| line-1 | line-1-0662-0868-s028076 | reverse | revenue | 2 | pending |
| line-1 | line-1-0632-0781-s031076 | forward | revenue | 2 | pending |
| line-1 | line-1-0632-0781-s031076 | reverse | revenue | 2 | pending |
| line-1 | line-1-0536-0732-s034085 | forward | revenue | 2 | pending |
| line-1 | line-1-0536-0732-s034085 | reverse | revenue | 2 | pending |
| line-1 | line-1-0467-0640-s037263 | forward | revenue | 2 | pending |
| line-1 | line-1-0467-0640-s037263 | reverse | revenue | 2 | pending |
| line-1 | line-1-0395-0623-s039463 | reverse | revenue | 2 | pending |
| line-1 | line-1-1254-1326-s007007 | forward | spare | 1 | pending |
| line-1 | line-1-1254-1326-s007007 | reverse | spare | 1 | pending |
| line-1 | line-1-1176-1230-s010569 | forward | spare | 1 | pending |
| line-1 | line-1-1176-1230-s010569 | reverse | spare | 1 | pending |
| line-1 | line-1-1059-1216-s013025 | forward | spare | 1 | pending |
| line-1 | line-1-1059-1216-s013025 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0481-1224-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0617-1129-s005265 | forward | revenue | 3 | pending |
| line-2 | line-2-0617-1129-s005265 | reverse | revenue | 3 | pending |
| line-2 | line-2-0704-1020-s008267 | forward | revenue | 3 | pending |
| line-2 | line-2-0704-1020-s008267 | reverse | revenue | 3 | pending |
| line-2 | line-2-0809-0937-s011285 | forward | revenue | 3 | pending |
| line-2 | line-2-0809-0937-s011285 | reverse | revenue | 3 | pending |
| line-2 | line-2-0835-0839-s013873 | forward | revenue | 3 | pending |
| line-2 | line-2-0835-0839-s013873 | reverse | revenue | 3 | pending |
| line-2 | line-2-0895-0786-s016040 | forward | revenue | 3 | pending |
| line-2 | line-2-0895-0786-s016040 | reverse | revenue | 3 | pending |
| line-2 | line-2-0982-0751-s019044 | forward | revenue | 3 | pending |
| line-2 | line-2-0982-0751-s019044 | reverse | revenue | 3 | pending |
| line-2 | line-2-1091-0691-s022059 | forward | revenue | 3 | pending |
| line-2 | line-2-1091-0691-s022059 | reverse | revenue | 3 | pending |
| line-2 | line-2-1204-0604-s025074 | forward | revenue | 3 | pending |
| line-2 | line-2-1204-0604-s025074 | reverse | revenue | 2 | pending |
| line-2 | line-2-1570-0333-s035831 | reverse | revenue | 2 | pending |
| line-2 | line-2-1204-0604-s025074 | reverse | spare | 1 | pending |
| line-2 | line-2-1570-0333-s035831 | reverse | spare | 1 | pending |
| line-2 | line-2-0481-1224-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0617-1129-s005265 | forward | spare | 1 | pending |
| line-2 | line-2-0617-1129-s005265 | reverse | spare | 1 | pending |
| line-2 | line-2-0704-1020-s008267 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0156-0750-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0308-0776-s003702 | forward | revenue | 3 | pending |
| line-3 | line-3-0308-0776-s003702 | reverse | revenue | 3 | pending |
| line-3 | line-3-0425-0829-s007007 | forward | revenue | 3 | pending |
| line-3 | line-3-0425-0829-s007007 | reverse | revenue | 3 | pending |
| line-3 | line-3-0529-0880-s010027 | forward | revenue | 3 | pending |
| line-3 | line-3-0529-0880-s010027 | reverse | revenue | 3 | pending |
| line-3 | line-3-0601-0929-s013044 | forward | revenue | 2 | pending |
| line-3 | line-3-0601-0929-s013044 | reverse | revenue | 2 | pending |
| line-3 | line-3-0724-0940-s016051 | forward | revenue | 2 | pending |
| line-3 | line-3-0724-0940-s016051 | reverse | revenue | 2 | pending |
| line-3 | line-3-0855-0956-s019068 | forward | revenue | 2 | pending |
| line-3 | line-3-0855-0956-s019068 | reverse | revenue | 2 | pending |
| line-3 | line-3-0970-1040-s022076 | forward | revenue | 2 | pending |
| line-3 | line-3-0970-1040-s022076 | reverse | revenue | 2 | pending |
| line-3 | line-3-1055-0980-s025088 | forward | revenue | 2 | pending |
| line-3 | line-3-1055-0980-s025088 | reverse | revenue | 2 | pending |
| line-3 | line-3-1163-1020-s028097 | forward | revenue | 2 | pending |
| line-3 | line-3-1163-1020-s028097 | reverse | revenue | 2 | pending |
| line-3 | line-3-1260-1050-s030454 | forward | revenue | 2 | pending |
| line-3 | line-3-1260-1050-s030454 | reverse | revenue | 2 | pending |
| line-3 | line-3-1301-1108-s032318 | forward | revenue | 2 | pending |
| line-3 | line-3-1301-1108-s032318 | reverse | revenue | 2 | pending |
| line-3 | line-3-1579-1180-s039299 | reverse | revenue | 2 | pending |
| line-3 | line-3-0601-0929-s013044 | forward | spare | 1 | pending |
| line-3 | line-3-0601-0929-s013044 | reverse | spare | 1 | pending |
| line-3 | line-3-0724-0940-s016051 | forward | spare | 1 | pending |
| line-3 | line-3-0724-0940-s016051 | reverse | spare | 1 | pending |
| line-3 | line-3-0855-0956-s019068 | forward | spare | 1 | pending |
| line-3 | line-3-0855-0956-s019068 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0763-0341-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0799-0445-s005640 | forward | revenue | 3 | pending |
| line-4 | line-4-0799-0445-s005640 | reverse | revenue | 3 | pending |
| line-4 | line-4-0798-0591-s008647 | forward | revenue | 3 | pending |
| line-4 | line-4-0798-0591-s008647 | reverse | revenue | 3 | pending |
| line-4 | line-4-0819-0732-s011674 | forward | revenue | 3 | pending |
| line-4 | line-4-0819-0732-s011674 | reverse | revenue | 3 | pending |
| line-4 | line-4-0835-0839-s014114 | forward | revenue | 2 | pending |
| line-4 | line-4-0835-0839-s014114 | reverse | revenue | 2 | pending |
| line-4 | line-4-0839-0930-s016567 | forward | revenue | 2 | pending |
| line-4 | line-4-0839-0930-s016567 | reverse | revenue | 2 | pending |
| line-4 | line-4-0835-1068-s019575 | forward | revenue | 2 | pending |
| line-4 | line-4-0835-1068-s019575 | reverse | revenue | 2 | pending |
| line-4 | line-4-0873-1125-s021641 | forward | revenue | 2 | pending |
| line-4 | line-4-0873-1125-s021641 | reverse | revenue | 2 | pending |
| line-4 | line-4-0866-1205-s023717 | forward | revenue | 2 | pending |
| line-4 | line-4-0866-1205-s023717 | reverse | revenue | 2 | pending |
| line-4 | line-4-0920-1385-s028320 | forward | revenue | 2 | pending |
| line-4 | line-4-0920-1385-s028320 | reverse | revenue | 2 | pending |
| line-4 | line-4-0908-1567-s032931 | reverse | revenue | 2 | pending |
| line-4 | line-4-0835-0839-s014114 | forward | spare | 1 | pending |
| line-4 | line-4-0835-0839-s014114 | reverse | spare | 1 | pending |
| line-4 | line-4-0839-0930-s016567 | forward | spare | 1 | pending |
| line-4 | line-4-0839-0930-s016567 | reverse | spare | 1 | pending |
| line-4 | line-4-0835-1068-s019575 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-1141-1487-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-1157-1320-s004188 | forward | revenue | 3 | pending |
| line-5 | line-5-1157-1320-s004188 | reverse | revenue | 3 | pending |
| line-5 | line-5-1138-1252-s006101 | forward | revenue | 3 | pending |
| line-5 | line-5-1138-1252-s006101 | reverse | revenue | 3 | pending |
| line-5 | line-5-1135-1161-s008012 | forward | revenue | 2 | pending |
| line-5 | line-5-1135-1161-s008012 | reverse | revenue | 2 | pending |
| line-5 | line-5-1082-1080-s010250 | forward | revenue | 2 | pending |
| line-5 | line-5-1082-1080-s010250 | reverse | revenue | 2 | pending |
| line-5 | line-5-1067-0948-s013253 | forward | revenue | 2 | pending |
| line-5 | line-5-1067-0948-s013253 | reverse | revenue | 2 | pending |
| line-5 | line-5-1041-0810-s016278 | forward | revenue | 2 | pending |
| line-5 | line-5-1041-0810-s016278 | reverse | revenue | 2 | pending |
| line-5 | line-5-1012-0675-s019281 | forward | revenue | 2 | pending |
| line-5 | line-5-1012-0675-s019281 | reverse | revenue | 2 | pending |
| line-5 | line-5-0929-0468-s025058 | reverse | revenue | 2 | pending |
| line-5 | line-5-1135-1161-s008012 | forward | spare | 1 | pending |
| line-5 | line-5-1135-1161-s008012 | reverse | spare | 1 | pending |
| line-5 | line-5-1082-1080-s010250 | forward | spare | 1 | pending |
| line-5 | line-5-1082-1080-s010250 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0763-0341-s000577 | forward | revenue | 1 | pending |
| line-6 | line-6-0763-0341-s000577 | reverse | revenue | 1 | pending |
| line-6 | line-6-0710-0438-s003175 | forward | revenue | 1 | pending |
| line-6 | line-6-0615-0508-s006674 | forward | revenue | 1 | pending |
| line-6 | line-6-0615-0508-s006674 | reverse | revenue | 1 | pending |
| line-6 | line-6-0545-0607-s010191 | forward | revenue | 1 | pending |
| line-6 | line-6-0481-0614-s011654 | forward | revenue | 1 | pending |
| line-6 | line-6-0481-0614-s011654 | reverse | revenue | 1 | pending |
| line-6 | line-6-0395-0623-s014237 | forward | revenue | 1 | pending |
| line-6 | line-6-0361-0728-s017206 | forward | revenue | 1 | pending |
| line-6 | line-6-0361-0728-s017206 | reverse | revenue | 1 | pending |
| line-6 | line-6-0308-0776-s019159 | reverse | revenue | 1 | pending |
| line-6 | line-6-0359-0951-s024213 | forward | revenue | 1 | pending |
| line-6 | line-6-0359-0951-s024213 | reverse | revenue | 1 | pending |
| line-6 | line-6-0481-1224-s034058 | reverse | revenue | 1 | pending |
| line-6 | line-6-0644-1188-s037890 | forward | revenue | 1 | pending |
| line-6 | line-6-0644-1188-s037890 | reverse | revenue | 1 | pending |
| line-6 | line-6-0866-1205-s043436 | reverse | revenue | 1 | pending |
| line-6 | line-6-0971-1187-s046183 | forward | revenue | 1 | pending |
| line-6 | line-6-1015-1184-s047599 | forward | revenue | 1 | pending |
| line-6 | line-6-1015-1184-s047599 | reverse | revenue | 1 | pending |
| line-6 | line-6-1190-1209-s051340 | forward | revenue | 1 | pending |
| line-6 | line-6-1267-1175-s053714 | forward | revenue | 1 | pending |
| line-6 | line-6-1267-1175-s053714 | reverse | revenue | 1 | pending |
| line-6 | line-6-1301-1108-s055615 | forward | revenue | 1 | pending |
| line-6 | line-6-1277-1032-s059160 | forward | revenue | 1 | pending |
| line-6 | line-6-1277-1032-s059160 | reverse | revenue | 1 | pending |
| line-6 | line-6-1259-0976-s060543 | reverse | revenue | 1 | pending |
| line-6 | line-6-1194-0681-s067045 | forward | revenue | 1 | pending |
| line-6 | line-6-1194-0681-s067045 | reverse | revenue | 1 | pending |
| line-6 | line-6-1212-0596-s069126 | reverse | revenue | 1 | pending |
| line-6 | line-6-1077-0489-s074060 | forward | spare | 1 | pending |
| line-6 | line-6-1077-0489-s074060 | reverse | spare | 1 | pending |
| line-6 | line-6-0985-0425-s077568 | reverse | spare | 1 | pending |
| line-6 | line-6-0864-0366-s081065 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**123 trainsets exceed the reference platform envelope**, requiring **10,455.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0395-0623-s039463 | 2 | 2 | 0 | 0.0 |
| line-1-0467-0640-s037263 | 4 | 4 | 0 | 0.0 |
| line-1-0536-0732-s034085 | 4 | 2 | 2 | 170.0 |
| line-1-0632-0781-s031076 | 4 | 2 | 2 | 170.0 |
| line-1-0662-0868-s028076 | 4 | 2 | 2 | 170.0 |
| line-1-0738-0935-s025070 | 4 | 4 | 0 | 0.0 |
| line-1-0831-0981-s022048 | 4 | 4 | 0 | 0.0 |
| line-1-0900-1071-s019045 | 4 | 2 | 2 | 170.0 |
| line-1-0976-1139-s016037 | 4 | 2 | 2 | 170.0 |
| line-1-1015-1184-s014264 | 4 | 4 | 0 | 0.0 |
| line-1-1059-1216-s013025 | 6 | 2 | 4 | 340.0 |
| line-1-1176-1230-s010569 | 6 | 4 | 2 | 170.0 |
| line-1-1254-1326-s007007 | 6 | 2 | 4 | 340.0 |
| line-1-1402-1367-s003508 | 6 | 2 | 4 | 340.0 |
| line-1-1519-1491-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0481-1224-s000000 | 4 | 2 | 2 | 170.0 |
| line-2-0617-1129-s005265 | 8 | 2 | 6 | 510.0 |
| line-2-0704-1020-s008267 | 7 | 2 | 5 | 425.0 |
| line-2-0809-0937-s011285 | 6 | 4 | 2 | 170.0 |
| line-2-0835-0839-s013873 | 6 | 4 | 2 | 170.0 |
| line-2-0895-0786-s016040 | 6 | 2 | 4 | 340.0 |
| line-2-0982-0751-s019044 | 6 | 2 | 4 | 340.0 |
| line-2-1091-0691-s022059 | 6 | 2 | 4 | 340.0 |
| line-2-1204-0604-s025074 | 6 | 4 | 2 | 170.0 |
| line-2-1570-0333-s035831 | 3 | 2 | 1 | 85.0 |
| line-3-0156-0750-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0308-0776-s003702 | 6 | 4 | 2 | 170.0 |
| line-3-0425-0829-s007007 | 6 | 2 | 4 | 340.0 |
| line-3-0529-0880-s010027 | 6 | 2 | 4 | 340.0 |
| line-3-0601-0929-s013044 | 6 | 2 | 4 | 340.0 |
| line-3-0724-0940-s016051 | 6 | 4 | 2 | 170.0 |
| line-3-0855-0956-s019068 | 6 | 4 | 2 | 170.0 |
| line-3-0970-1040-s022076 | 4 | 2 | 2 | 170.0 |
| line-3-1055-0980-s025088 | 4 | 4 | 0 | 0.0 |
| line-3-1163-1020-s028097 | 4 | 2 | 2 | 170.0 |
| line-3-1260-1050-s030454 | 4 | 4 | 0 | 0.0 |
| line-3-1301-1108-s032318 | 4 | 4 | 0 | 0.0 |
| line-3-1579-1180-s039299 | 2 | 2 | 0 | 0.0 |
| line-4-0763-0341-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0798-0591-s008647 | 6 | 2 | 4 | 340.0 |
| line-4-0799-0445-s005640 | 6 | 2 | 4 | 340.0 |
| line-4-0819-0732-s011674 | 6 | 2 | 4 | 340.0 |
| line-4-0835-0839-s014114 | 6 | 4 | 2 | 170.0 |
| line-4-0835-1068-s019575 | 5 | 2 | 3 | 255.0 |
| line-4-0839-0930-s016567 | 6 | 4 | 2 | 170.0 |
| line-4-0866-1205-s023717 | 4 | 4 | 0 | 0.0 |
| line-4-0873-1125-s021641 | 4 | 2 | 2 | 170.0 |
| line-4-0908-1567-s032931 | 2 | 2 | 0 | 0.0 |
| line-4-0920-1385-s028320 | 4 | 2 | 2 | 170.0 |
| line-5-0929-0468-s025058 | 2 | 2 | 0 | 0.0 |
| line-5-1012-0675-s019281 | 4 | 2 | 2 | 170.0 |
| line-5-1041-0810-s016278 | 4 | 2 | 2 | 170.0 |
| line-5-1067-0948-s013253 | 4 | 4 | 0 | 0.0 |
| line-5-1082-1080-s010250 | 6 | 2 | 4 | 340.0 |
| line-5-1135-1161-s008012 | 6 | 4 | 2 | 170.0 |
| line-5-1138-1252-s006101 | 6 | 2 | 4 | 340.0 |
| line-5-1141-1487-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-1157-1320-s004188 | 6 | 2 | 4 | 340.0 |
| line-6-0308-0776-s019159 | 1 | 4 | 0 | 0.0 |
| line-6-0359-0951-s024213 | 2 | 2 | 0 | 0.0 |
| line-6-0361-0728-s017206 | 2 | 2 | 0 | 0.0 |
| line-6-0395-0623-s014237 | 1 | 4 | 0 | 0.0 |
| line-6-0481-0614-s011654 | 2 | 4 | 0 | 0.0 |
| line-6-0481-1224-s034058 | 1 | 4 | 0 | 0.0 |
| line-6-0545-0607-s010191 | 1 | 2 | 0 | 0.0 |
| line-6-0615-0508-s006674 | 2 | 2 | 0 | 0.0 |
| line-6-0644-1188-s037890 | 2 | 2 | 0 | 0.0 |
| line-6-0710-0438-s003175 | 1 | 2 | 0 | 0.0 |
| line-6-0763-0341-s000577 | 2 | 4 | 0 | 0.0 |
| line-6-0864-0366-s081065 | 1 | 2 | 0 | 0.0 |
| line-6-0866-1205-s043436 | 1 | 4 | 0 | 0.0 |
| line-6-0971-1187-s046183 | 1 | 2 | 0 | 0.0 |
| line-6-0985-0425-s077568 | 1 | 2 | 0 | 0.0 |
| line-6-1015-1184-s047599 | 2 | 4 | 0 | 0.0 |
| line-6-1077-0489-s074060 | 2 | 2 | 0 | 0.0 |
| line-6-1190-1209-s051340 | 1 | 4 | 0 | 0.0 |
| line-6-1194-0681-s067045 | 2 | 2 | 0 | 0.0 |
| line-6-1212-0596-s069126 | 1 | 4 | 0 | 0.0 |
| line-6-1259-0976-s060543 | 1 | 2 | 0 | 0.0 |
| line-6-1267-1175-s053714 | 2 | 2 | 0 | 0.0 |
| line-6-1277-1032-s059160 | 2 | 4 | 0 | 0.0 |
| line-6-1301-1108-s055615 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Omdurman/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
