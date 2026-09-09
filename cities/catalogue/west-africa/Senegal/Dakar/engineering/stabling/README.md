# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **330 trainsets at 78 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **297 revenue, 27 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0350-1820-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0444-1392-s011380 | forward | revenue | 3 | pending |
| line-1 | line-1-0444-1392-s011380 | reverse | revenue | 3 | pending |
| line-1 | line-1-0435-1259-s015556 | forward | revenue | 3 | pending |
| line-1 | line-1-0435-1259-s015556 | reverse | revenue | 3 | pending |
| line-1 | line-1-0531-1220-s017910 | forward | revenue | 3 | pending |
| line-1 | line-1-0531-1220-s017910 | reverse | revenue | 3 | pending |
| line-1 | line-1-0501-1096-s020917 | forward | revenue | 3 | pending |
| line-1 | line-1-0501-1096-s020917 | reverse | revenue | 3 | pending |
| line-1 | line-1-0542-0962-s023937 | forward | revenue | 3 | pending |
| line-1 | line-1-0542-0962-s023937 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0911-s025307 | forward | revenue | 3 | pending |
| line-1 | line-1-0571-0911-s025307 | reverse | revenue | 3 | pending |
| line-1 | line-1-0601-0855-s026938 | forward | revenue | 3 | pending |
| line-1 | line-1-0601-0855-s026938 | reverse | revenue | 3 | pending |
| line-1 | line-1-0632-0721-s029942 | forward | revenue | 3 | pending |
| line-1 | line-1-0632-0721-s029942 | reverse | revenue | 3 | pending |
| line-1 | line-1-0698-0601-s032963 | forward | revenue | 3 | pending |
| line-1 | line-1-0698-0601-s032963 | reverse | revenue | 3 | pending |
| line-1 | line-1-0675-0501-s035244 | forward | revenue | 3 | pending |
| line-1 | line-1-0675-0501-s035244 | reverse | revenue | 3 | pending |
| line-1 | line-1-0726-0423-s037790 | forward | revenue | 3 | pending |
| line-1 | line-1-0726-0423-s037790 | reverse | revenue | 3 | pending |
| line-1 | line-1-0696-0349-s040331 | reverse | revenue | 2 | pending |
| line-1 | line-1-0696-0349-s040331 | reverse | spare | 1 | pending |
| line-1 | line-1-0350-1820-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0444-1392-s011380 | forward | spare | 1 | pending |
| line-1 | line-1-0444-1392-s011380 | reverse | spare | 1 | pending |
| line-1 | line-1-0435-1259-s015556 | forward | spare | 1 | pending |
| line-1 | line-1-0435-1259-s015556 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-1220-s017910 | forward | spare | 1 | pending |
| line-1 | line-1-0531-1220-s017910 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0812-0380-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0823-0479-s003001 | forward | revenue | 3 | pending |
| line-2 | line-2-0823-0479-s003001 | reverse | revenue | 3 | pending |
| line-2 | line-2-0852-0527-s004522 | forward | revenue | 3 | pending |
| line-2 | line-2-0852-0527-s004522 | reverse | revenue | 3 | pending |
| line-2 | line-2-0756-0593-s007611 | forward | revenue | 3 | pending |
| line-2 | line-2-0756-0593-s007611 | reverse | revenue | 3 | pending |
| line-2 | line-2-0833-0685-s010865 | forward | revenue | 3 | pending |
| line-2 | line-2-0833-0685-s010865 | reverse | revenue | 3 | pending |
| line-2 | line-2-0756-0783-s013462 | forward | revenue | 3 | pending |
| line-2 | line-2-0756-0783-s013462 | reverse | revenue | 2 | pending |
| line-2 | line-2-0731-0923-s016470 | forward | revenue | 2 | pending |
| line-2 | line-2-0731-0923-s016470 | reverse | revenue | 2 | pending |
| line-2 | line-2-0727-1043-s018903 | forward | revenue | 2 | pending |
| line-2 | line-2-0727-1043-s018903 | reverse | revenue | 2 | pending |
| line-2 | line-2-0716-1322-s024574 | forward | revenue | 2 | pending |
| line-2 | line-2-0716-1322-s024574 | reverse | revenue | 2 | pending |
| line-2 | line-2-0716-1452-s027413 | forward | revenue | 2 | pending |
| line-2 | line-2-0716-1452-s027413 | reverse | revenue | 2 | pending |
| line-2 | line-2-0768-1504-s030260 | reverse | revenue | 2 | pending |
| line-2 | line-2-0756-0783-s013462 | reverse | spare | 1 | pending |
| line-2 | line-2-0731-0923-s016470 | forward | spare | 1 | pending |
| line-2 | line-2-0731-0923-s016470 | reverse | spare | 1 | pending |
| line-2 | line-2-0727-1043-s018903 | forward | spare | 1 | pending |
| line-2 | line-2-0727-1043-s018903 | reverse | spare | 1 | pending |
| line-2 | line-2-0716-1322-s024574 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0573-0432-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0586-0552-s003006 | forward | revenue | 3 | pending |
| line-3 | line-3-0586-0552-s003006 | reverse | revenue | 3 | pending |
| line-3 | line-3-0500-0650-s006021 | forward | revenue | 3 | pending |
| line-3 | line-3-0500-0650-s006021 | reverse | revenue | 3 | pending |
| line-3 | line-3-0469-0716-s007725 | forward | revenue | 3 | pending |
| line-3 | line-3-0469-0716-s007725 | reverse | revenue | 3 | pending |
| line-3 | line-3-0428-0787-s009508 | forward | revenue | 3 | pending |
| line-3 | line-3-0428-0787-s009508 | reverse | revenue | 3 | pending |
| line-3 | line-3-0427-0867-s011565 | forward | revenue | 2 | pending |
| line-3 | line-3-0427-0867-s011565 | reverse | revenue | 2 | pending |
| line-3 | line-3-0432-0930-s013357 | forward | revenue | 2 | pending |
| line-3 | line-3-0432-0930-s013357 | reverse | revenue | 2 | pending |
| line-3 | line-3-0434-1010-s015057 | forward | revenue | 2 | pending |
| line-3 | line-3-0434-1010-s015057 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-1111-s018079 | forward | revenue | 2 | pending |
| line-3 | line-3-0375-1111-s018079 | reverse | revenue | 2 | pending |
| line-3 | line-3-0401-1216-s020725 | forward | revenue | 2 | pending |
| line-3 | line-3-0401-1216-s020725 | reverse | revenue | 2 | pending |
| line-3 | line-3-0296-1411-s026016 | forward | revenue | 2 | pending |
| line-3 | line-3-0296-1411-s026016 | reverse | revenue | 2 | pending |
| line-3 | line-3-0223-1606-s031310 | reverse | revenue | 2 | pending |
| line-3 | line-3-0427-0867-s011565 | forward | spare | 1 | pending |
| line-3 | line-3-0427-0867-s011565 | reverse | spare | 1 | pending |
| line-3 | line-3-0432-0930-s013357 | forward | spare | 1 | pending |
| line-3 | line-3-0432-0930-s013357 | reverse | spare | 1 | pending |
| line-3 | line-3-0434-1010-s015057 | forward | spare | 1 | pending |
| line-3 | line-3-0434-1010-s015057 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0316-1152-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0397-1155-s003006 | forward | revenue | 3 | pending |
| line-4 | line-4-0397-1155-s003006 | reverse | revenue | 3 | pending |
| line-4 | line-4-0472-1081-s005178 | forward | revenue | 3 | pending |
| line-4 | line-4-0472-1081-s005178 | reverse | revenue | 3 | pending |
| line-4 | line-4-0479-0989-s007109 | forward | revenue | 3 | pending |
| line-4 | line-4-0479-0989-s007109 | reverse | revenue | 3 | pending |
| line-4 | line-4-0510-0905-s009046 | forward | revenue | 2 | pending |
| line-4 | line-4-0510-0905-s009046 | reverse | revenue | 2 | pending |
| line-4 | line-4-0571-0911-s011530 | forward | revenue | 2 | pending |
| line-4 | line-4-0571-0911-s011530 | reverse | revenue | 2 | pending |
| line-4 | line-4-0669-0800-s015078 | forward | revenue | 2 | pending |
| line-4 | line-4-0669-0800-s015078 | reverse | revenue | 2 | pending |
| line-4 | line-4-0812-0659-s019106 | forward | revenue | 2 | pending |
| line-4 | line-4-0812-0659-s019106 | reverse | revenue | 2 | pending |
| line-4 | line-4-0881-0552-s022561 | forward | revenue | 2 | pending |
| line-4 | line-4-0881-0552-s022561 | reverse | revenue | 2 | pending |
| line-4 | line-4-0902-0502-s024482 | forward | revenue | 2 | pending |
| line-4 | line-4-0902-0502-s024482 | reverse | revenue | 2 | pending |
| line-4 | line-4-0931-0450-s026397 | reverse | revenue | 2 | pending |
| line-4 | line-4-0510-0905-s009046 | forward | spare | 1 | pending |
| line-4 | line-4-0510-0905-s009046 | reverse | spare | 1 | pending |
| line-4 | line-4-0571-0911-s011530 | forward | spare | 1 | pending |
| line-4 | line-4-0571-0911-s011530 | reverse | spare | 1 | pending |
| line-4 | line-4-0669-0800-s015078 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0645-1815-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-0765-1386-s010525 | forward | revenue | 4 | pending |
| line-5 | line-5-0765-1386-s010525 | reverse | revenue | 4 | pending |
| line-5 | line-5-0765-1211-s014025 | forward | revenue | 4 | pending |
| line-5 | line-5-0765-1211-s014025 | reverse | revenue | 4 | pending |
| line-5 | line-5-0806-1053-s017525 | forward | revenue | 4 | pending |
| line-5 | line-5-0806-1053-s017525 | reverse | revenue | 4 | pending |
| line-5 | line-5-0852-0897-s021026 | forward | revenue | 4 | pending |
| line-5 | line-5-0852-0897-s021026 | reverse | revenue | 4 | pending |
| line-5 | line-5-0935-0750-s024654 | forward | revenue | 4 | pending |
| line-5 | line-5-0935-0750-s024654 | reverse | revenue | 4 | pending |
| line-5 | line-5-0993-0627-s028276 | reverse | revenue | 4 | pending |
| line-5 | line-5-0765-1386-s010525 | forward | spare | 1 | pending |
| line-5 | line-5-0765-1386-s010525 | reverse | spare | 1 | pending |
| line-5 | line-5-0765-1211-s014025 | forward | spare | 1 | pending |
| line-5 | line-5-0765-1211-s014025 | reverse | spare | 1 | pending |
| line-5 | line-5-0806-1053-s017525 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0498-0440-s000000 | forward | revenue | 1 | pending |
| line-6 | line-6-0498-0440-s000000 | reverse | revenue | 1 | pending |
| line-6 | line-6-0470-0569-s003007 | reverse | revenue | 1 | pending |
| line-6 | line-6-0439-0716-s006551 | forward | revenue | 1 | pending |
| line-6 | line-6-0428-0787-s008173 | forward | revenue | 1 | pending |
| line-6 | line-6-0446-0867-s010140 | forward | revenue | 1 | pending |
| line-6 | line-6-0446-0867-s010140 | reverse | revenue | 1 | pending |
| line-6 | line-6-0459-0952-s012030 | reverse | revenue | 1 | pending |
| line-6 | line-6-0472-1081-s014907 | forward | revenue | 1 | pending |
| line-6 | line-6-0452-1170-s016952 | forward | revenue | 1 | pending |
| line-6 | line-6-0423-1257-s018996 | forward | revenue | 1 | pending |
| line-6 | line-6-0423-1257-s018996 | reverse | revenue | 1 | pending |
| line-6 | line-6-0435-1304-s020253 | reverse | revenue | 1 | pending |
| line-6 | line-6-0451-1403-s022365 | forward | revenue | 1 | pending |
| line-6 | line-6-0521-1453-s025880 | forward | revenue | 1 | pending |
| line-6 | line-6-0580-1405-s029385 | forward | revenue | 1 | pending |
| line-6 | line-6-0580-1405-s029385 | reverse | revenue | 1 | pending |
| line-6 | line-6-0655-1241-s034907 | reverse | revenue | 1 | pending |
| line-6 | line-6-0673-1119-s037913 | forward | revenue | 1 | pending |
| line-6 | line-6-0727-1043-s040185 | forward | revenue | 1 | pending |
| line-6 | line-6-0759-0885-s043931 | forward | revenue | 1 | pending |
| line-6 | line-6-0759-0885-s043931 | reverse | revenue | 1 | pending |
| line-6 | line-6-0858-0686-s048732 | reverse | revenue | 1 | pending |
| line-6 | line-6-0913-0606-s050937 | forward | revenue | 1 | pending |
| line-6 | line-6-0937-0555-s053276 | forward | revenue | 1 | pending |
| line-6 | line-6-0852-0527-s055620 | forward | revenue | 1 | pending |
| line-6 | line-6-0852-0527-s055620 | reverse | revenue | 1 | pending |
| line-6 | line-6-0756-0512-s058584 | reverse | spare | 1 | pending |
| line-6 | line-6-0675-0501-s060491 | forward | spare | 1 | pending |
| line-6 | line-6-0573-0432-s063534 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**170 trainsets exceed the reference platform envelope**, requiring **20,570.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0350-1820-s000000 | 4 | 2 | 2 | 242.0 |
| line-1-0435-1259-s015556 | 8 | 4 | 4 | 484.0 |
| line-1-0444-1392-s011380 | 8 | 4 | 4 | 484.0 |
| line-1-0501-1096-s020917 | 6 | 2 | 4 | 484.0 |
| line-1-0531-1220-s017910 | 8 | 2 | 6 | 726.0 |
| line-1-0542-0962-s023937 | 6 | 2 | 4 | 484.0 |
| line-1-0571-0911-s025307 | 6 | 4 | 2 | 242.0 |
| line-1-0601-0855-s026938 | 6 | 2 | 4 | 484.0 |
| line-1-0632-0721-s029942 | 6 | 2 | 4 | 484.0 |
| line-1-0675-0501-s035244 | 6 | 4 | 2 | 242.0 |
| line-1-0696-0349-s040331 | 3 | 2 | 1 | 121.0 |
| line-1-0698-0601-s032963 | 6 | 2 | 4 | 484.0 |
| line-1-0726-0423-s037790 | 6 | 2 | 4 | 484.0 |
| line-2-0716-1322-s024574 | 5 | 2 | 3 | 363.0 |
| line-2-0716-1452-s027413 | 4 | 2 | 2 | 242.0 |
| line-2-0727-1043-s018903 | 6 | 4 | 2 | 242.0 |
| line-2-0731-0923-s016470 | 6 | 2 | 4 | 484.0 |
| line-2-0756-0593-s007611 | 6 | 2 | 4 | 484.0 |
| line-2-0756-0783-s013462 | 6 | 2 | 4 | 484.0 |
| line-2-0768-1504-s030260 | 2 | 2 | 0 | 0.0 |
| line-2-0812-0380-s000000 | 3 | 2 | 1 | 121.0 |
| line-2-0823-0479-s003001 | 6 | 2 | 4 | 484.0 |
| line-2-0833-0685-s010865 | 6 | 4 | 2 | 242.0 |
| line-2-0852-0527-s004522 | 6 | 4 | 2 | 242.0 |
| line-3-0223-1606-s031310 | 2 | 2 | 0 | 0.0 |
| line-3-0296-1411-s026016 | 4 | 2 | 2 | 242.0 |
| line-3-0375-1111-s018079 | 4 | 2 | 2 | 242.0 |
| line-3-0401-1216-s020725 | 4 | 2 | 2 | 242.0 |
| line-3-0427-0867-s011565 | 6 | 4 | 2 | 242.0 |
| line-3-0428-0787-s009508 | 6 | 4 | 2 | 242.0 |
| line-3-0432-0930-s013357 | 6 | 2 | 4 | 484.0 |
| line-3-0434-1010-s015057 | 6 | 2 | 4 | 484.0 |
| line-3-0469-0716-s007725 | 6 | 2 | 4 | 484.0 |
| line-3-0500-0650-s006021 | 6 | 2 | 4 | 484.0 |
| line-3-0573-0432-s000000 | 3 | 2 | 1 | 121.0 |
| line-3-0586-0552-s003006 | 6 | 2 | 4 | 484.0 |
| line-4-0316-1152-s000000 | 3 | 2 | 1 | 121.0 |
| line-4-0397-1155-s003006 | 6 | 2 | 4 | 484.0 |
| line-4-0472-1081-s005178 | 6 | 4 | 2 | 242.0 |
| line-4-0479-0989-s007109 | 6 | 2 | 4 | 484.0 |
| line-4-0510-0905-s009046 | 6 | 2 | 4 | 484.0 |
| line-4-0571-0911-s011530 | 6 | 4 | 2 | 242.0 |
| line-4-0669-0800-s015078 | 5 | 2 | 3 | 363.0 |
| line-4-0812-0659-s019106 | 4 | 2 | 2 | 242.0 |
| line-4-0881-0552-s022561 | 4 | 2 | 2 | 242.0 |
| line-4-0902-0502-s024482 | 4 | 2 | 2 | 242.0 |
| line-4-0931-0450-s026397 | 2 | 2 | 0 | 0.0 |
| line-5-0645-1815-s000000 | 5 | 2 | 3 | 363.0 |
| line-5-0765-1211-s014025 | 10 | 2 | 8 | 968.0 |
| line-5-0765-1386-s010525 | 10 | 2 | 8 | 968.0 |
| line-5-0806-1053-s017525 | 9 | 2 | 7 | 847.0 |
| line-5-0852-0897-s021026 | 8 | 2 | 6 | 726.0 |
| line-5-0935-0750-s024654 | 8 | 2 | 6 | 726.0 |
| line-5-0993-0627-s028276 | 4 | 2 | 2 | 242.0 |
| line-6-0423-1257-s018996 | 2 | 4 | 0 | 0.0 |
| line-6-0428-0787-s008173 | 1 | 4 | 0 | 0.0 |
| line-6-0435-1304-s020253 | 1 | 2 | 0 | 0.0 |
| line-6-0439-0716-s006551 | 1 | 2 | 0 | 0.0 |
| line-6-0446-0867-s010140 | 2 | 4 | 0 | 0.0 |
| line-6-0451-1403-s022365 | 1 | 4 | 0 | 0.0 |
| line-6-0452-1170-s016952 | 1 | 2 | 0 | 0.0 |
| line-6-0459-0952-s012030 | 1 | 2 | 0 | 0.0 |
| line-6-0470-0569-s003007 | 1 | 2 | 0 | 0.0 |
| line-6-0472-1081-s014907 | 1 | 4 | 0 | 0.0 |
| line-6-0498-0440-s000000 | 2 | 2 | 0 | 0.0 |
| line-6-0521-1453-s025880 | 1 | 2 | 0 | 0.0 |
| line-6-0573-0432-s063534 | 1 | 4 | 0 | 0.0 |
| line-6-0580-1405-s029385 | 2 | 2 | 0 | 0.0 |
| line-6-0655-1241-s034907 | 1 | 2 | 0 | 0.0 |
| line-6-0673-1119-s037913 | 1 | 2 | 0 | 0.0 |
| line-6-0675-0501-s060491 | 1 | 4 | 0 | 0.0 |
| line-6-0727-1043-s040185 | 1 | 4 | 0 | 0.0 |
| line-6-0756-0512-s058584 | 1 | 2 | 0 | 0.0 |
| line-6-0759-0885-s043931 | 2 | 2 | 0 | 0.0 |
| line-6-0852-0527-s055620 | 2 | 4 | 0 | 0.0 |
| line-6-0858-0686-s048732 | 1 | 4 | 0 | 0.0 |
| line-6-0913-0606-s050937 | 1 | 2 | 0 | 0.0 |
| line-6-0937-0555-s053276 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Senegal/Dakar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
