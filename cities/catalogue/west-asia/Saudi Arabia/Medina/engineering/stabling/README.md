# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **212 trainsets at 52 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **190 revenue, 16 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0485-0427-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0688-0691-s006962 | forward | revenue | 3 | pending |
| line-1 | line-1-0688-0691-s006962 | reverse | revenue | 3 | pending |
| line-1 | line-1-0757-0810-s009984 | forward | revenue | 3 | pending |
| line-1 | line-1-0757-0810-s009984 | reverse | revenue | 3 | pending |
| line-1 | line-1-0823-0815-s011704 | forward | revenue | 3 | pending |
| line-1 | line-1-0823-0815-s011704 | reverse | revenue | 3 | pending |
| line-1 | line-1-0828-0873-s012905 | forward | revenue | 3 | pending |
| line-1 | line-1-0828-0873-s012905 | reverse | revenue | 3 | pending |
| line-1 | line-1-0941-0927-s016002 | forward | revenue | 3 | pending |
| line-1 | line-1-0941-0927-s016002 | reverse | revenue | 3 | pending |
| line-1 | line-1-1062-0975-s019008 | forward | revenue | 3 | pending |
| line-1 | line-1-1062-0975-s019008 | reverse | revenue | 3 | pending |
| line-1 | line-1-1150-1060-s022011 | forward | revenue | 2 | pending |
| line-1 | line-1-1150-1060-s022011 | reverse | revenue | 2 | pending |
| line-1 | line-1-1244-1169-s025186 | forward | revenue | 2 | pending |
| line-1 | line-1-1244-1169-s025186 | reverse | revenue | 2 | pending |
| line-1 | line-1-1509-1385-s034203 | reverse | revenue | 2 | pending |
| line-1 | line-1-1150-1060-s022011 | forward | spare | 1 | pending |
| line-1 | line-1-1150-1060-s022011 | reverse | spare | 1 | pending |
| line-1 | line-1-1244-1169-s025186 | forward | spare | 1 | pending |
| line-1 | line-1-1244-1169-s025186 | reverse | spare | 1 | pending |
| line-1 | line-1-1509-1385-s034203 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1235-0549-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1148-0606-s002707 | forward | revenue | 2 | pending |
| line-2 | line-2-1148-0606-s002707 | reverse | revenue | 2 | pending |
| line-2 | line-2-1122-0691-s005081 | forward | revenue | 2 | pending |
| line-2 | line-2-1122-0691-s005081 | reverse | revenue | 2 | pending |
| line-2 | line-2-1045-0770-s008083 | forward | revenue | 2 | pending |
| line-2 | line-2-1045-0770-s008083 | reverse | revenue | 2 | pending |
| line-2 | line-2-0959-0856-s011090 | forward | revenue | 2 | pending |
| line-2 | line-2-0959-0856-s011090 | reverse | revenue | 2 | pending |
| line-2 | line-2-0942-0978-s014110 | forward | revenue | 2 | pending |
| line-2 | line-2-0942-0978-s014110 | reverse | revenue | 2 | pending |
| line-2 | line-2-0816-1062-s017372 | forward | revenue | 2 | pending |
| line-2 | line-2-0816-1062-s017372 | reverse | revenue | 2 | pending |
| line-2 | line-2-0747-1131-s019324 | forward | revenue | 2 | pending |
| line-2 | line-2-0747-1131-s019324 | reverse | revenue | 2 | pending |
| line-2 | line-2-0677-1193-s021254 | reverse | revenue | 2 | pending |
| line-2 | line-2-1148-0606-s002707 | forward | spare | 1 | pending |
| line-2 | line-2-1148-0606-s002707 | reverse | spare | 1 | pending |
| line-2 | line-2-1122-0691-s005081 | forward | spare | 1 | pending |
| line-2 | line-2-1122-0691-s005081 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0762-0521-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0869-0674-s004860 | forward | revenue | 3 | pending |
| line-3 | line-3-0869-0674-s004860 | reverse | revenue | 3 | pending |
| line-3 | line-3-0947-0734-s007230 | forward | revenue | 3 | pending |
| line-3 | line-3-0947-0734-s007230 | reverse | revenue | 3 | pending |
| line-3 | line-3-1073-0745-s010240 | forward | revenue | 3 | pending |
| line-3 | line-3-1073-0745-s010240 | reverse | revenue | 3 | pending |
| line-3 | line-3-1238-0935-s016483 | forward | revenue | 3 | pending |
| line-3 | line-3-1238-0935-s016483 | reverse | revenue | 3 | pending |
| line-3 | line-3-1406-1008-s020656 | reverse | revenue | 2 | pending |
| line-3 | line-3-1406-1008-s020656 | reverse | spare | 1 | pending |
| line-3 | line-3-0762-0521-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0869-0674-s004860 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0552-1137-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0682-0904-s006091 | forward | revenue | 3 | pending |
| line-4 | line-4-0682-0904-s006091 | reverse | revenue | 3 | pending |
| line-4 | line-4-0744-0785-s009095 | forward | revenue | 3 | pending |
| line-4 | line-4-0744-0785-s009095 | reverse | revenue | 3 | pending |
| line-4 | line-4-0818-0677-s012103 | forward | revenue | 2 | pending |
| line-4 | line-4-0818-0677-s012103 | reverse | revenue | 2 | pending |
| line-4 | line-4-0869-0654-s013358 | forward | revenue | 2 | pending |
| line-4 | line-4-0869-0654-s013358 | reverse | revenue | 2 | pending |
| line-4 | line-4-0995-0515-s017198 | forward | revenue | 2 | pending |
| line-4 | line-4-0995-0515-s017198 | reverse | revenue | 2 | pending |
| line-4 | line-4-0984-0329-s021026 | forward | revenue | 2 | pending |
| line-4 | line-4-0984-0329-s021026 | reverse | revenue | 2 | pending |
| line-4 | line-4-1079-0263-s024173 | reverse | revenue | 2 | pending |
| line-4 | line-4-0818-0677-s012103 | forward | spare | 1 | pending |
| line-4 | line-4-0818-0677-s012103 | reverse | spare | 1 | pending |
| line-4 | line-4-0869-0654-s013358 | forward | spare | 1 | pending |
| line-4 | line-4-0869-0654-s013358 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0623-0725-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0686-0844-s003007 | forward | revenue | 3 | pending |
| line-5 | line-5-0686-0844-s003007 | reverse | revenue | 3 | pending |
| line-5 | line-5-0726-0996-s006499 | forward | revenue | 3 | pending |
| line-5 | line-5-0726-0996-s006499 | reverse | revenue | 3 | pending |
| line-5 | line-5-0744-1164-s010008 | forward | revenue | 2 | pending |
| line-5 | line-5-0744-1164-s010008 | reverse | revenue | 2 | pending |
| line-5 | line-5-0815-1252-s012356 | forward | revenue | 2 | pending |
| line-5 | line-5-0815-1252-s012356 | reverse | revenue | 2 | pending |
| line-5 | line-5-0938-1459-s018738 | reverse | revenue | 2 | pending |
| line-5 | line-5-0744-1164-s010008 | forward | spare | 1 | pending |
| line-5 | line-5-0744-1164-s010008 | reverse | spare | 1 | pending |
| line-5 | line-5-0815-1252-s012356 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0805-1346-s000000 | forward | revenue | 1 | pending |
| line-6 | line-6-0805-1346-s000000 | reverse | revenue | 1 | pending |
| line-6 | line-6-1244-1170-s013075 | forward | revenue | 1 | pending |
| line-6 | line-6-1244-1170-s013075 | reverse | revenue | 1 | pending |
| line-6 | line-6-1252-1044-s015924 | forward | revenue | 1 | pending |
| line-6 | line-6-1252-1044-s015924 | reverse | revenue | 1 | pending |
| line-6 | line-6-1238-0935-s018746 | forward | revenue | 1 | pending |
| line-6 | line-6-1238-0935-s018746 | reverse | revenue | 1 | pending |
| line-6 | line-6-1184-0704-s024609 | forward | revenue | 1 | pending |
| line-6 | line-6-1184-0704-s024609 | reverse | revenue | 1 | pending |
| line-6 | line-6-1148-0606-s028172 | forward | revenue | 1 | pending |
| line-6 | line-6-1148-0606-s028172 | reverse | revenue | 1 | pending |
| line-6 | line-6-0984-0329-s035314 | reverse | revenue | 1 | pending |
| line-6 | line-6-0895-0565-s042087 | forward | revenue | 1 | pending |
| line-6 | line-6-0895-0565-s042087 | reverse | revenue | 1 | pending |
| line-6 | line-6-0863-0701-s045100 | forward | revenue | 1 | pending |
| line-6 | line-6-0863-0701-s045100 | reverse | revenue | 1 | pending |
| line-6 | line-6-0859-0806-s048119 | forward | revenue | 1 | pending |
| line-6 | line-6-0859-0806-s048119 | reverse | revenue | 1 | pending |
| line-6 | line-6-0828-0873-s049984 | forward | revenue | 1 | pending |
| line-6 | line-6-0828-0873-s049984 | reverse | revenue | 1 | pending |
| line-6 | line-6-0816-1062-s054162 | forward | spare | 1 | pending |
| line-6 | line-6-0816-1062-s054162 | reverse | spare | 1 | pending |
| line-6 | line-6-0815-1252-s058268 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**88 trainsets exceed the reference platform envelope**, requiring **7,480.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0485-0427-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0688-0691-s006962 | 6 | 2 | 4 | 340.0 |
| line-1-0757-0810-s009984 | 6 | 4 | 2 | 170.0 |
| line-1-0823-0815-s011704 | 6 | 2 | 4 | 340.0 |
| line-1-0828-0873-s012905 | 6 | 4 | 2 | 170.0 |
| line-1-0941-0927-s016002 | 6 | 2 | 4 | 340.0 |
| line-1-1062-0975-s019008 | 6 | 2 | 4 | 340.0 |
| line-1-1150-1060-s022011 | 6 | 2 | 4 | 340.0 |
| line-1-1244-1169-s025186 | 6 | 4 | 2 | 170.0 |
| line-1-1509-1385-s034203 | 3 | 2 | 1 | 85.0 |
| line-2-0677-1193-s021254 | 2 | 2 | 0 | 0.0 |
| line-2-0747-1131-s019324 | 4 | 2 | 2 | 170.0 |
| line-2-0816-1062-s017372 | 4 | 4 | 0 | 0.0 |
| line-2-0942-0978-s014110 | 4 | 2 | 2 | 170.0 |
| line-2-0959-0856-s011090 | 4 | 2 | 2 | 170.0 |
| line-2-1045-0770-s008083 | 4 | 2 | 2 | 170.0 |
| line-2-1122-0691-s005081 | 6 | 2 | 4 | 340.0 |
| line-2-1148-0606-s002707 | 6 | 4 | 2 | 170.0 |
| line-2-1235-0549-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0762-0521-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0869-0674-s004860 | 7 | 4 | 3 | 255.0 |
| line-3-0947-0734-s007230 | 6 | 2 | 4 | 340.0 |
| line-3-1073-0745-s010240 | 6 | 2 | 4 | 340.0 |
| line-3-1238-0935-s016483 | 6 | 4 | 2 | 170.0 |
| line-3-1406-1008-s020656 | 3 | 2 | 1 | 85.0 |
| line-4-0552-1137-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0682-0904-s006091 | 6 | 2 | 4 | 340.0 |
| line-4-0744-0785-s009095 | 6 | 4 | 2 | 170.0 |
| line-4-0818-0677-s012103 | 6 | 2 | 4 | 340.0 |
| line-4-0869-0654-s013358 | 6 | 4 | 2 | 170.0 |
| line-4-0984-0329-s021026 | 4 | 4 | 0 | 0.0 |
| line-4-0995-0515-s017198 | 4 | 2 | 2 | 170.0 |
| line-4-1079-0263-s024173 | 2 | 2 | 0 | 0.0 |
| line-5-0623-0725-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-0686-0844-s003007 | 6 | 2 | 4 | 340.0 |
| line-5-0726-0996-s006499 | 6 | 2 | 4 | 340.0 |
| line-5-0744-1164-s010008 | 6 | 2 | 4 | 340.0 |
| line-5-0815-1252-s012356 | 5 | 4 | 1 | 85.0 |
| line-5-0938-1459-s018738 | 2 | 2 | 0 | 0.0 |
| line-6-0805-1346-s000000 | 2 | 2 | 0 | 0.0 |
| line-6-0815-1252-s058268 | 1 | 4 | 0 | 0.0 |
| line-6-0816-1062-s054162 | 2 | 4 | 0 | 0.0 |
| line-6-0828-0873-s049984 | 2 | 4 | 0 | 0.0 |
| line-6-0859-0806-s048119 | 2 | 2 | 0 | 0.0 |
| line-6-0863-0701-s045100 | 2 | 4 | 0 | 0.0 |
| line-6-0895-0565-s042087 | 2 | 2 | 0 | 0.0 |
| line-6-0984-0329-s035314 | 1 | 4 | 0 | 0.0 |
| line-6-1148-0606-s028172 | 2 | 4 | 0 | 0.0 |
| line-6-1184-0704-s024609 | 2 | 2 | 0 | 0.0 |
| line-6-1238-0935-s018746 | 2 | 4 | 0 | 0.0 |
| line-6-1244-1170-s013075 | 2 | 4 | 0 | 0.0 |
| line-6-1252-1044-s015924 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Medina/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
