# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **350 trainsets at 78 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **316 revenue, 27 spare, 7 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0477-1068-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0974-s003000 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0974-s003000 | reverse | revenue | 3 | pending |
| line-1 | line-1-0661-0900-s006004 | forward | revenue | 3 | pending |
| line-1 | line-1-0661-0900-s006004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0702-0775-s009016 | forward | revenue | 3 | pending |
| line-1 | line-1-0702-0775-s009016 | reverse | revenue | 2 | pending |
| line-1 | line-1-0702-0642-s012028 | forward | revenue | 2 | pending |
| line-1 | line-1-0702-0642-s012028 | reverse | revenue | 2 | pending |
| line-1 | line-1-0815-0651-s015030 | forward | revenue | 2 | pending |
| line-1 | line-1-0815-0651-s015030 | reverse | revenue | 2 | pending |
| line-1 | line-1-0876-0624-s016811 | forward | revenue | 2 | pending |
| line-1 | line-1-0876-0624-s016811 | reverse | revenue | 2 | pending |
| line-1 | line-1-0905-0581-s018033 | forward | revenue | 2 | pending |
| line-1 | line-1-0905-0581-s018033 | reverse | revenue | 2 | pending |
| line-1 | line-1-0934-0522-s019651 | forward | revenue | 2 | pending |
| line-1 | line-1-0934-0522-s019651 | reverse | revenue | 2 | pending |
| line-1 | line-1-0916-0414-s022657 | forward | revenue | 2 | pending |
| line-1 | line-1-0916-0414-s022657 | reverse | revenue | 2 | pending |
| line-1 | line-1-0957-0321-s025148 | forward | revenue | 2 | pending |
| line-1 | line-1-0957-0321-s025148 | reverse | revenue | 2 | pending |
| line-1 | line-1-1060-0308-s027360 | forward | revenue | 2 | pending |
| line-1 | line-1-1060-0308-s027360 | reverse | revenue | 2 | pending |
| line-1 | line-1-1095-0224-s029570 | reverse | revenue | 2 | pending |
| line-1 | line-1-0702-0775-s009016 | reverse | spare | 1 | pending |
| line-1 | line-1-0702-0642-s012028 | forward | spare | 1 | pending |
| line-1 | line-1-0702-0642-s012028 | reverse | spare | 1 | pending |
| line-1 | line-1-0815-0651-s015030 | forward | spare | 1 | pending |
| line-1 | line-1-0815-0651-s015030 | reverse | spare | 1 | pending |
| line-1 | line-1-0876-0624-s016811 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1175-1030-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1092-0903-s004107 | forward | revenue | 3 | pending |
| line-2 | line-2-1092-0903-s004107 | reverse | revenue | 3 | pending |
| line-2 | line-2-0959-0895-s007657 | forward | revenue | 3 | pending |
| line-2 | line-2-0959-0895-s007657 | reverse | revenue | 3 | pending |
| line-2 | line-2-0936-0837-s009132 | forward | revenue | 3 | pending |
| line-2 | line-2-0936-0837-s009132 | reverse | revenue | 3 | pending |
| line-2 | line-2-0891-0760-s011167 | forward | revenue | 3 | pending |
| line-2 | line-2-0891-0760-s011167 | reverse | revenue | 3 | pending |
| line-2 | line-2-0866-0695-s013143 | forward | revenue | 3 | pending |
| line-2 | line-2-0866-0695-s013143 | reverse | revenue | 3 | pending |
| line-2 | line-2-0780-0640-s016152 | forward | revenue | 3 | pending |
| line-2 | line-2-0780-0640-s016152 | reverse | revenue | 3 | pending |
| line-2 | line-2-0749-0494-s019845 | forward | revenue | 3 | pending |
| line-2 | line-2-0749-0494-s019845 | reverse | revenue | 3 | pending |
| line-2 | line-2-0710-0380-s022854 | forward | revenue | 3 | pending |
| line-2 | line-2-0710-0380-s022854 | reverse | revenue | 3 | pending |
| line-2 | line-2-0652-0349-s025862 | forward | revenue | 3 | pending |
| line-2 | line-2-0652-0349-s025862 | reverse | revenue | 3 | pending |
| line-2 | line-2-0487-0134-s033687 | reverse | revenue | 2 | pending |
| line-2 | line-2-0487-0134-s033687 | reverse | spare | 1 | pending |
| line-2 | line-2-1175-1030-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-1092-0903-s004107 | forward | spare | 1 | pending |
| line-2 | line-2-1092-0903-s004107 | reverse | spare | 1 | pending |
| line-2 | line-2-0959-0895-s007657 | forward | spare | 1 | pending |
| line-2 | line-2-0959-0895-s007657 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0934-0177-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0933-0293-s002524 | forward | revenue | 3 | pending |
| line-3 | line-3-0933-0293-s002524 | reverse | revenue | 3 | pending |
| line-3 | line-3-0805-0357-s006745 | forward | revenue | 3 | pending |
| line-3 | line-3-0805-0357-s006745 | reverse | revenue | 3 | pending |
| line-3 | line-3-0819-0446-s009300 | forward | revenue | 3 | pending |
| line-3 | line-3-0819-0446-s009300 | reverse | revenue | 3 | pending |
| line-3 | line-3-0792-0506-s011247 | forward | revenue | 2 | pending |
| line-3 | line-3-0792-0506-s011247 | reverse | revenue | 2 | pending |
| line-3 | line-3-0711-0537-s013171 | forward | revenue | 2 | pending |
| line-3 | line-3-0711-0537-s013171 | reverse | revenue | 2 | pending |
| line-3 | line-3-0669-0626-s015623 | forward | revenue | 2 | pending |
| line-3 | line-3-0669-0626-s015623 | reverse | revenue | 2 | pending |
| line-3 | line-3-0594-0695-s018077 | forward | revenue | 2 | pending |
| line-3 | line-3-0594-0695-s018077 | reverse | revenue | 2 | pending |
| line-3 | line-3-0517-0872-s022992 | reverse | revenue | 2 | pending |
| line-3 | line-3-0792-0506-s011247 | forward | spare | 1 | pending |
| line-3 | line-3-0792-0506-s011247 | reverse | spare | 1 | pending |
| line-3 | line-3-0711-0537-s013171 | forward | spare | 1 | pending |
| line-3 | line-3-0711-0537-s013171 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1312-0202-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-1144-0417-s006376 | forward | revenue | 3 | pending |
| line-4 | line-4-1144-0417-s006376 | reverse | revenue | 3 | pending |
| line-4 | line-4-1097-0528-s009396 | forward | revenue | 3 | pending |
| line-4 | line-4-1097-0528-s009396 | reverse | revenue | 3 | pending |
| line-4 | line-4-1043-0649-s012407 | forward | revenue | 3 | pending |
| line-4 | line-4-1043-0649-s012407 | reverse | revenue | 3 | pending |
| line-4 | line-4-1054-0794-s015414 | forward | revenue | 3 | pending |
| line-4 | line-4-1054-0794-s015414 | reverse | revenue | 3 | pending |
| line-4 | line-4-1011-0894-s018424 | forward | revenue | 2 | pending |
| line-4 | line-4-1011-0894-s018424 | reverse | revenue | 2 | pending |
| line-4 | line-4-0952-0924-s020137 | forward | revenue | 2 | pending |
| line-4 | line-4-0952-0924-s020137 | reverse | revenue | 2 | pending |
| line-4 | line-4-0895-0932-s021445 | forward | revenue | 2 | pending |
| line-4 | line-4-0895-0932-s021445 | reverse | revenue | 2 | pending |
| line-4 | line-4-0867-1020-s023540 | forward | revenue | 2 | pending |
| line-4 | line-4-0867-1020-s023540 | reverse | revenue | 2 | pending |
| line-4 | line-4-0871-1123-s025650 | forward | revenue | 2 | pending |
| line-4 | line-4-0871-1123-s025650 | reverse | revenue | 2 | pending |
| line-4 | line-4-0792-1249-s029843 | reverse | revenue | 2 | pending |
| line-4 | line-4-1011-0894-s018424 | forward | spare | 1 | pending |
| line-4 | line-4-1011-0894-s018424 | reverse | spare | 1 | pending |
| line-4 | line-4-0952-0924-s020137 | forward | spare | 1 | pending |
| line-4 | line-4-0952-0924-s020137 | reverse | spare | 1 | pending |
| line-4 | line-4-0895-0932-s021445 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0688-0221-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0746-0316-s002609 | forward | revenue | 3 | pending |
| line-5 | line-5-0746-0316-s002609 | reverse | revenue | 3 | pending |
| line-5 | line-5-0750-0475-s006037 | forward | revenue | 3 | pending |
| line-5 | line-5-0750-0475-s006037 | reverse | revenue | 3 | pending |
| line-5 | line-5-0739-0618-s009038 | forward | revenue | 3 | pending |
| line-5 | line-5-0739-0618-s009038 | reverse | revenue | 3 | pending |
| line-5 | line-5-0800-0761-s012576 | forward | revenue | 3 | pending |
| line-5 | line-5-0800-0761-s012576 | reverse | revenue | 3 | pending |
| line-5 | line-5-0864-0836-s015050 | forward | revenue | 3 | pending |
| line-5 | line-5-0864-0836-s015050 | reverse | revenue | 3 | pending |
| line-5 | line-5-0905-0962-s018072 | forward | revenue | 3 | pending |
| line-5 | line-5-0905-0962-s018072 | reverse | revenue | 3 | pending |
| line-5 | line-5-0938-1107-s021571 | forward | revenue | 3 | pending |
| line-5 | line-5-0938-1107-s021571 | reverse | revenue | 3 | pending |
| line-5 | line-5-0973-1248-s025085 | forward | revenue | 3 | pending |
| line-5 | line-5-0973-1248-s025085 | reverse | revenue | 3 | pending |
| line-5 | line-5-1016-1511-s030804 | reverse | revenue | 2 | pending |
| line-5 | line-5-1016-1511-s030804 | reverse | spare | 1 | pending |
| line-5 | line-5-0688-0221-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0746-0316-s002609 | forward | spare | 1 | pending |
| line-5 | line-5-0746-0316-s002609 | reverse | spare | 1 | pending |
| line-5 | line-5-0750-0475-s006037 | forward | spare | 1 | pending |
| line-5 | line-5-0750-0475-s006037 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-1185-1306-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-1060-1237-s004779 | forward | revenue | 3 | pending |
| line-6 | line-6-1060-1237-s004779 | reverse | revenue | 3 | pending |
| line-6 | line-6-1010-1167-s007004 | forward | revenue | 3 | pending |
| line-6 | line-6-1010-1167-s007004 | reverse | revenue | 3 | pending |
| line-6 | line-6-0942-0963-s011758 | forward | revenue | 3 | pending |
| line-6 | line-6-0942-0963-s011758 | reverse | revenue | 3 | pending |
| line-6 | line-6-0806-0963-s014776 | forward | revenue | 3 | pending |
| line-6 | line-6-0806-0963-s014776 | reverse | revenue | 3 | pending |
| line-6 | line-6-0719-0881-s017777 | forward | revenue | 3 | pending |
| line-6 | line-6-0719-0881-s017777 | reverse | revenue | 3 | pending |
| line-6 | line-6-0664-0757-s020771 | reverse | revenue | 3 | pending |
| line-6 | line-6-1060-1237-s004779 | forward | spare | 1 | pending |
| line-6 | line-6-1060-1237-s004779 | reverse | spare | 1 | pending |
| line-6 | line-6-1010-1167-s007004 | forward | spare | 1 | pending |
| line-6 | line-6-1010-1167-s007004 | reverse | cold_reserve | 1 | pending |
| line-7 | line-7-0736-0328-s000000 | forward | revenue | 1 | pending |
| line-7 | line-7-0736-0328-s000000 | reverse | revenue | 1 | pending |
| line-7 | line-7-0819-0446-s003287 | forward | revenue | 1 | pending |
| line-7 | line-7-0819-0446-s003287 | reverse | revenue | 1 | pending |
| line-7 | line-7-0848-0489-s005652 | forward | revenue | 1 | pending |
| line-7 | line-7-0876-0624-s009044 | forward | revenue | 1 | pending |
| line-7 | line-7-0876-0624-s009044 | reverse | revenue | 1 | pending |
| line-7 | line-7-0899-0734-s011676 | forward | revenue | 1 | pending |
| line-7 | line-7-0899-0734-s011676 | reverse | revenue | 1 | pending |
| line-7 | line-7-0885-0816-s013548 | forward | revenue | 1 | pending |
| line-7 | line-7-0946-0908-s015980 | forward | revenue | 1 | pending |
| line-7 | line-7-0946-0908-s015980 | reverse | revenue | 1 | pending |
| line-7 | line-7-1032-1146-s021709 | forward | revenue | 1 | pending |
| line-7 | line-7-1032-1146-s021709 | reverse | revenue | 1 | pending |
| line-7 | line-7-1060-1237-s024997 | reverse | revenue | 1 | pending |
| line-7 | line-7-1134-1094-s028721 | forward | revenue | 1 | pending |
| line-7 | line-7-1134-1094-s028721 | reverse | revenue | 1 | pending |
| line-7 | line-7-1175-1030-s030728 | forward | revenue | 1 | pending |
| line-7 | line-7-1175-1030-s030728 | reverse | revenue | 1 | pending |
| line-7 | line-7-1226-0830-s035726 | reverse | revenue | 1 | pending |
| line-7 | line-7-1237-0559-s042751 | forward | revenue | 1 | pending |
| line-7 | line-7-1237-0559-s042751 | reverse | revenue | 1 | pending |
| line-7 | line-7-1189-0389-s046919 | forward | revenue | 1 | pending |
| line-7 | line-7-1189-0389-s046919 | reverse | revenue | 1 | pending |
| line-7 | line-7-1144-0417-s048478 | reverse | revenue | 1 | pending |
| line-7 | line-7-1066-0381-s051485 | forward | spare | 1 | pending |
| line-7 | line-7-1066-0381-s051485 | reverse | spare | 1 | pending |
| line-7 | line-7-0933-0293-s055597 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**176 trainsets exceed the reference platform envelope**, requiring **21,296.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0477-1068-s000000 | 3 | 2 | 1 | 121.0 |
| line-1-0551-0974-s003000 | 6 | 2 | 4 | 484.0 |
| line-1-0661-0900-s006004 | 6 | 2 | 4 | 484.0 |
| line-1-0702-0642-s012028 | 6 | 2 | 4 | 484.0 |
| line-1-0702-0775-s009016 | 6 | 2 | 4 | 484.0 |
| line-1-0815-0651-s015030 | 6 | 2 | 4 | 484.0 |
| line-1-0876-0624-s016811 | 5 | 4 | 1 | 121.0 |
| line-1-0905-0581-s018033 | 4 | 2 | 2 | 242.0 |
| line-1-0916-0414-s022657 | 4 | 2 | 2 | 242.0 |
| line-1-0934-0522-s019651 | 4 | 2 | 2 | 242.0 |
| line-1-0957-0321-s025148 | 4 | 2 | 2 | 242.0 |
| line-1-1060-0308-s027360 | 4 | 2 | 2 | 242.0 |
| line-1-1095-0224-s029570 | 2 | 2 | 0 | 0.0 |
| line-2-0487-0134-s033687 | 3 | 2 | 1 | 121.0 |
| line-2-0652-0349-s025862 | 6 | 2 | 4 | 484.0 |
| line-2-0710-0380-s022854 | 6 | 2 | 4 | 484.0 |
| line-2-0749-0494-s019845 | 6 | 4 | 2 | 242.0 |
| line-2-0780-0640-s016152 | 6 | 2 | 4 | 484.0 |
| line-2-0866-0695-s013143 | 6 | 2 | 4 | 484.0 |
| line-2-0891-0760-s011167 | 6 | 4 | 2 | 242.0 |
| line-2-0936-0837-s009132 | 6 | 2 | 4 | 484.0 |
| line-2-0959-0895-s007657 | 8 | 4 | 4 | 484.0 |
| line-2-1092-0903-s004107 | 8 | 2 | 6 | 726.0 |
| line-2-1175-1030-s000000 | 4 | 2 | 2 | 242.0 |
| line-3-0517-0872-s022992 | 2 | 2 | 0 | 0.0 |
| line-3-0594-0695-s018077 | 4 | 2 | 2 | 242.0 |
| line-3-0669-0626-s015623 | 4 | 2 | 2 | 242.0 |
| line-3-0711-0537-s013171 | 6 | 2 | 4 | 484.0 |
| line-3-0792-0506-s011247 | 6 | 2 | 4 | 484.0 |
| line-3-0805-0357-s006745 | 6 | 2 | 4 | 484.0 |
| line-3-0819-0446-s009300 | 6 | 4 | 2 | 242.0 |
| line-3-0933-0293-s002524 | 6 | 4 | 2 | 242.0 |
| line-3-0934-0177-s000000 | 3 | 2 | 1 | 121.0 |
| line-4-0792-1249-s029843 | 2 | 2 | 0 | 0.0 |
| line-4-0867-1020-s023540 | 4 | 2 | 2 | 242.0 |
| line-4-0871-1123-s025650 | 4 | 2 | 2 | 242.0 |
| line-4-0895-0932-s021445 | 5 | 2 | 3 | 363.0 |
| line-4-0952-0924-s020137 | 6 | 4 | 2 | 242.0 |
| line-4-1011-0894-s018424 | 6 | 2 | 4 | 484.0 |
| line-4-1043-0649-s012407 | 6 | 2 | 4 | 484.0 |
| line-4-1054-0794-s015414 | 6 | 2 | 4 | 484.0 |
| line-4-1097-0528-s009396 | 6 | 2 | 4 | 484.0 |
| line-4-1144-0417-s006376 | 6 | 4 | 2 | 242.0 |
| line-4-1312-0202-s000000 | 3 | 2 | 1 | 121.0 |
| line-5-0688-0221-s000000 | 4 | 2 | 2 | 242.0 |
| line-5-0739-0618-s009038 | 6 | 2 | 4 | 484.0 |
| line-5-0746-0316-s002609 | 8 | 4 | 4 | 484.0 |
| line-5-0750-0475-s006037 | 8 | 4 | 4 | 484.0 |
| line-5-0800-0761-s012576 | 6 | 2 | 4 | 484.0 |
| line-5-0864-0836-s015050 | 6 | 4 | 2 | 242.0 |
| line-5-0905-0962-s018072 | 6 | 2 | 4 | 484.0 |
| line-5-0938-1107-s021571 | 6 | 2 | 4 | 484.0 |
| line-5-0973-1248-s025085 | 6 | 2 | 4 | 484.0 |
| line-5-1016-1511-s030804 | 3 | 2 | 1 | 121.0 |
| line-6-0664-0757-s020771 | 3 | 2 | 1 | 121.0 |
| line-6-0719-0881-s017777 | 6 | 2 | 4 | 484.0 |
| line-6-0806-0963-s014776 | 6 | 2 | 4 | 484.0 |
| line-6-0942-0963-s011758 | 6 | 2 | 4 | 484.0 |
| line-6-1010-1167-s007004 | 8 | 2 | 6 | 726.0 |
| line-6-1060-1237-s004779 | 8 | 4 | 4 | 484.0 |
| line-6-1185-1306-s000000 | 4 | 2 | 2 | 242.0 |
| line-7-0736-0328-s000000 | 2 | 4 | 0 | 0.0 |
| line-7-0819-0446-s003287 | 2 | 4 | 0 | 0.0 |
| line-7-0848-0489-s005652 | 1 | 2 | 0 | 0.0 |
| line-7-0876-0624-s009044 | 2 | 4 | 0 | 0.0 |
| line-7-0885-0816-s013548 | 1 | 4 | 0 | 0.0 |
| line-7-0899-0734-s011676 | 2 | 4 | 0 | 0.0 |
| line-7-0933-0293-s055597 | 1 | 4 | 0 | 0.0 |
| line-7-0946-0908-s015980 | 2 | 4 | 0 | 0.0 |
| line-7-1032-1146-s021709 | 2 | 2 | 0 | 0.0 |
| line-7-1060-1237-s024997 | 1 | 4 | 0 | 0.0 |
| line-7-1066-0381-s051485 | 2 | 2 | 0 | 0.0 |
| line-7-1134-1094-s028721 | 2 | 2 | 0 | 0.0 |
| line-7-1144-0417-s048478 | 1 | 4 | 0 | 0.0 |
| line-7-1175-1030-s030728 | 2 | 4 | 0 | 0.0 |
| line-7-1189-0389-s046919 | 2 | 2 | 0 | 0.0 |
| line-7-1226-0830-s035726 | 1 | 2 | 0 | 0.0 |
| line-7-1237-0559-s042751 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Kabul/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
