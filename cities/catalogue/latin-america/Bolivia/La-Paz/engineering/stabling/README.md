# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **285 trainsets at 74 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **256 revenue, 23 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0094-1470-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0385-0981-s012836 | forward | revenue | 3 | pending |
| line-1 | line-1-0385-0981-s012836 | reverse | revenue | 3 | pending |
| line-1 | line-1-0481-0958-s015013 | forward | revenue | 3 | pending |
| line-1 | line-1-0481-0958-s015013 | reverse | revenue | 3 | pending |
| line-1 | line-1-0558-0927-s017021 | forward | revenue | 3 | pending |
| line-1 | line-1-0558-0927-s017021 | reverse | revenue | 3 | pending |
| line-1 | line-1-0576-0876-s018641 | forward | revenue | 3 | pending |
| line-1 | line-1-0576-0876-s018641 | reverse | revenue | 3 | pending |
| line-1 | line-1-0634-0777-s021653 | forward | revenue | 3 | pending |
| line-1 | line-1-0634-0777-s021653 | reverse | revenue | 3 | pending |
| line-1 | line-1-0748-0695-s024675 | forward | revenue | 3 | pending |
| line-1 | line-1-0748-0695-s024675 | reverse | revenue | 3 | pending |
| line-1 | line-1-0752-0589-s027696 | forward | revenue | 3 | pending |
| line-1 | line-1-0752-0589-s027696 | reverse | revenue | 2 | pending |
| line-1 | line-1-0861-0482-s030929 | forward | revenue | 2 | pending |
| line-1 | line-1-0861-0482-s030929 | reverse | revenue | 2 | pending |
| line-1 | line-1-0914-0402-s033718 | reverse | revenue | 2 | pending |
| line-1 | line-1-0752-0589-s027696 | reverse | spare | 1 | pending |
| line-1 | line-1-0861-0482-s030929 | forward | spare | 1 | pending |
| line-1 | line-1-0861-0482-s030929 | reverse | spare | 1 | pending |
| line-1 | line-1-0914-0402-s033718 | reverse | spare | 1 | pending |
| line-1 | line-1-0094-1470-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0385-0981-s012836 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0618-0177-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0678-0398-s005855 | forward | revenue | 3 | pending |
| line-2 | line-2-0678-0398-s005855 | reverse | revenue | 3 | pending |
| line-2 | line-2-0678-0511-s008867 | forward | revenue | 3 | pending |
| line-2 | line-2-0678-0511-s008867 | reverse | revenue | 2 | pending |
| line-2 | line-2-0667-0636-s011884 | forward | revenue | 2 | pending |
| line-2 | line-2-0667-0636-s011884 | reverse | revenue | 2 | pending |
| line-2 | line-2-0723-0757-s014897 | forward | revenue | 2 | pending |
| line-2 | line-2-0723-0757-s014897 | reverse | revenue | 2 | pending |
| line-2 | line-2-0689-0795-s017629 | forward | revenue | 2 | pending |
| line-2 | line-2-0689-0795-s017629 | reverse | revenue | 2 | pending |
| line-2 | line-2-0642-0855-s020332 | forward | revenue | 2 | pending |
| line-2 | line-2-0642-0855-s020332 | reverse | revenue | 2 | pending |
| line-2 | line-2-0673-0967-s023348 | forward | revenue | 2 | pending |
| line-2 | line-2-0673-0967-s023348 | reverse | revenue | 2 | pending |
| line-2 | line-2-0711-1049-s025414 | forward | revenue | 2 | pending |
| line-2 | line-2-0711-1049-s025414 | reverse | revenue | 2 | pending |
| line-2 | line-2-0786-1103-s027476 | forward | revenue | 2 | pending |
| line-2 | line-2-0786-1103-s027476 | reverse | revenue | 2 | pending |
| line-2 | line-2-0772-1191-s029385 | forward | revenue | 2 | pending |
| line-2 | line-2-0772-1191-s029385 | reverse | revenue | 2 | pending |
| line-2 | line-2-0780-1249-s030711 | forward | revenue | 2 | pending |
| line-2 | line-2-0780-1249-s030711 | reverse | revenue | 2 | pending |
| line-2 | line-2-0767-1497-s037195 | reverse | revenue | 2 | pending |
| line-2 | line-2-0678-0511-s008867 | reverse | spare | 1 | pending |
| line-2 | line-2-0667-0636-s011884 | forward | spare | 1 | pending |
| line-2 | line-2-0667-0636-s011884 | reverse | spare | 1 | pending |
| line-2 | line-2-0723-0757-s014897 | forward | spare | 1 | pending |
| line-2 | line-2-0723-0757-s014897 | reverse | spare | 1 | pending |
| line-2 | line-2-0689-0795-s017629 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0542-1152-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0587-1096-s002153 | forward | revenue | 3 | pending |
| line-3 | line-3-0587-1096-s002153 | reverse | revenue | 3 | pending |
| line-3 | line-3-0611-1030-s004087 | forward | revenue | 3 | pending |
| line-3 | line-3-0611-1030-s004087 | reverse | revenue | 3 | pending |
| line-3 | line-3-0643-0986-s006013 | forward | revenue | 3 | pending |
| line-3 | line-3-0643-0986-s006013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0727-0910-s009023 | forward | revenue | 3 | pending |
| line-3 | line-3-0727-0910-s009023 | reverse | revenue | 3 | pending |
| line-3 | line-3-0796-0813-s012047 | forward | revenue | 3 | pending |
| line-3 | line-3-0796-0813-s012047 | reverse | revenue | 3 | pending |
| line-3 | line-3-1016-0611-s018670 | forward | revenue | 3 | pending |
| line-3 | line-3-1016-0611-s018670 | reverse | revenue | 2 | pending |
| line-3 | line-3-1067-0556-s020863 | forward | revenue | 2 | pending |
| line-3 | line-3-1067-0556-s020863 | reverse | revenue | 2 | pending |
| line-3 | line-3-1334-0251-s030042 | reverse | revenue | 2 | pending |
| line-3 | line-3-1016-0611-s018670 | reverse | spare | 1 | pending |
| line-3 | line-3-1067-0556-s020863 | forward | spare | 1 | pending |
| line-3 | line-3-1067-0556-s020863 | reverse | spare | 1 | pending |
| line-3 | line-3-1334-0251-s030042 | reverse | spare | 1 | pending |
| line-3 | line-3-0542-1152-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-1271-1449-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0964-1158-s010014 | forward | revenue | 3 | pending |
| line-4 | line-4-0964-1158-s010014 | reverse | revenue | 3 | pending |
| line-4 | line-4-0852-0961-s015523 | forward | revenue | 3 | pending |
| line-4 | line-4-0852-0961-s015523 | reverse | revenue | 3 | pending |
| line-4 | line-4-0817-0905-s017015 | forward | revenue | 3 | pending |
| line-4 | line-4-0817-0905-s017015 | reverse | revenue | 3 | pending |
| line-4 | line-4-0755-0847-s018986 | forward | revenue | 3 | pending |
| line-4 | line-4-0755-0847-s018986 | reverse | revenue | 3 | pending |
| line-4 | line-4-0689-0795-s020979 | forward | revenue | 3 | pending |
| line-4 | line-4-0689-0795-s020979 | reverse | revenue | 3 | pending |
| line-4 | line-4-0598-0725-s024649 | forward | revenue | 3 | pending |
| line-4 | line-4-0598-0725-s024649 | reverse | revenue | 3 | pending |
| line-4 | line-4-0518-0645-s027651 | forward | revenue | 2 | pending |
| line-4 | line-4-0518-0645-s027651 | reverse | revenue | 2 | pending |
| line-4 | line-4-0433-0561-s030910 | forward | revenue | 2 | pending |
| line-4 | line-4-0433-0561-s030910 | reverse | revenue | 2 | pending |
| line-4 | line-4-0370-0471-s033347 | reverse | revenue | 2 | pending |
| line-4 | line-4-0518-0645-s027651 | forward | spare | 1 | pending |
| line-4 | line-4-0518-0645-s027651 | reverse | spare | 1 | pending |
| line-4 | line-4-0433-0561-s030910 | forward | spare | 1 | pending |
| line-4 | line-4-0433-0561-s030910 | reverse | spare | 1 | pending |
| line-4 | line-4-0370-0471-s033347 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-1251-0639-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-1087-0634-s003842 | forward | revenue | 3 | pending |
| line-5 | line-5-1087-0634-s003842 | reverse | revenue | 3 | pending |
| line-5 | line-5-1008-0663-s006246 | forward | revenue | 2 | pending |
| line-5 | line-5-1008-0663-s006246 | reverse | revenue | 2 | pending |
| line-5 | line-5-0845-0690-s010307 | forward | revenue | 2 | pending |
| line-5 | line-5-0845-0690-s010307 | reverse | revenue | 2 | pending |
| line-5 | line-5-0739-0773-s013312 | forward | revenue | 2 | pending |
| line-5 | line-5-0739-0773-s013312 | reverse | revenue | 2 | pending |
| line-5 | line-5-0689-0795-s014768 | forward | revenue | 2 | pending |
| line-5 | line-5-0689-0795-s014768 | reverse | revenue | 2 | pending |
| line-5 | line-5-0586-0763-s017939 | forward | revenue | 2 | pending |
| line-5 | line-5-0586-0763-s017939 | reverse | revenue | 2 | pending |
| line-5 | line-5-0490-0826-s020960 | forward | revenue | 2 | pending |
| line-5 | line-5-0490-0826-s020960 | reverse | revenue | 2 | pending |
| line-5 | line-5-0348-0791-s024430 | forward | revenue | 2 | pending |
| line-5 | line-5-0348-0791-s024430 | reverse | revenue | 2 | pending |
| line-5 | line-5-0222-0838-s027582 | reverse | revenue | 2 | pending |
| line-5 | line-5-1008-0663-s006246 | forward | spare | 1 | pending |
| line-5 | line-5-1008-0663-s006246 | reverse | spare | 1 | pending |
| line-5 | line-5-0845-0690-s010307 | forward | spare | 1 | pending |
| line-5 | line-5-0845-0690-s010307 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0677-0388-s000887 | forward | revenue | 1 | pending |
| line-6 | line-6-0677-0388-s000887 | reverse | revenue | 1 | pending |
| line-6 | line-6-0613-0464-s003024 | reverse | revenue | 1 | pending |
| line-6 | line-6-0506-0527-s006030 | reverse | revenue | 1 | pending |
| line-6 | line-6-0433-0561-s007870 | reverse | revenue | 1 | pending |
| line-6 | line-6-0348-0791-s014036 | forward | revenue | 1 | pending |
| line-6 | line-6-0374-0881-s016051 | forward | revenue | 1 | pending |
| line-6 | line-6-0385-0981-s018192 | forward | revenue | 1 | pending |
| line-6 | line-6-0459-1019-s020127 | forward | revenue | 1 | pending |
| line-6 | line-6-0459-1019-s020127 | reverse | revenue | 1 | pending |
| line-6 | line-6-0532-1056-s022078 | reverse | revenue | 1 | pending |
| line-6 | line-6-0587-1096-s023510 | reverse | revenue | 1 | pending |
| line-6 | line-6-0729-1222-s028848 | reverse | revenue | 1 | pending |
| line-6 | line-6-0780-1249-s030125 | forward | revenue | 1 | pending |
| line-6 | line-6-0817-1191-s031859 | forward | revenue | 1 | pending |
| line-6 | line-6-0801-1103-s033926 | forward | revenue | 1 | pending |
| line-6 | line-6-0851-0961-s037180 | forward | revenue | 1 | pending |
| line-6 | line-6-0851-0961-s037180 | reverse | revenue | 1 | pending |
| line-6 | line-6-0987-0782-s041887 | reverse | revenue | 1 | pending |
| line-6 | line-6-1038-0623-s045794 | reverse | revenue | 1 | pending |
| line-6 | line-6-1085-0562-s047909 | reverse | revenue | 1 | pending |
| line-6 | line-6-0993-0535-s051818 | forward | revenue | 1 | pending |
| line-6 | line-6-0922-0522-s053913 | forward | spare | 1 | pending |
| line-6 | line-6-0862-0482-s055988 | forward | spare | 1 | pending |
| line-6 | line-6-0833-0419-s057830 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**124 trainsets exceed the reference platform envelope**, requiring **10,540.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0094-1470-s000000 | 4 | 2 | 2 | 170.0 |
| line-1-0385-0981-s012836 | 7 | 4 | 3 | 255.0 |
| line-1-0481-0958-s015013 | 6 | 2 | 4 | 340.0 |
| line-1-0558-0927-s017021 | 6 | 2 | 4 | 340.0 |
| line-1-0576-0876-s018641 | 6 | 2 | 4 | 340.0 |
| line-1-0634-0777-s021653 | 6 | 2 | 4 | 340.0 |
| line-1-0748-0695-s024675 | 6 | 2 | 4 | 340.0 |
| line-1-0752-0589-s027696 | 6 | 2 | 4 | 340.0 |
| line-1-0861-0482-s030929 | 6 | 4 | 2 | 170.0 |
| line-1-0914-0402-s033718 | 3 | 2 | 1 | 85.0 |
| line-2-0618-0177-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0642-0855-s020332 | 4 | 2 | 2 | 170.0 |
| line-2-0667-0636-s011884 | 6 | 2 | 4 | 340.0 |
| line-2-0673-0967-s023348 | 4 | 2 | 2 | 170.0 |
| line-2-0678-0398-s005855 | 6 | 4 | 2 | 170.0 |
| line-2-0678-0511-s008867 | 6 | 2 | 4 | 340.0 |
| line-2-0689-0795-s017629 | 5 | 4 | 1 | 85.0 |
| line-2-0711-1049-s025414 | 4 | 2 | 2 | 170.0 |
| line-2-0723-0757-s014897 | 6 | 4 | 2 | 170.0 |
| line-2-0767-1497-s037195 | 2 | 2 | 0 | 0.0 |
| line-2-0772-1191-s029385 | 4 | 2 | 2 | 170.0 |
| line-2-0780-1249-s030711 | 4 | 4 | 0 | 0.0 |
| line-2-0786-1103-s027476 | 4 | 4 | 0 | 0.0 |
| line-3-0542-1152-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0587-1096-s002153 | 6 | 4 | 2 | 170.0 |
| line-3-0611-1030-s004087 | 6 | 2 | 4 | 340.0 |
| line-3-0643-0986-s006013 | 6 | 2 | 4 | 340.0 |
| line-3-0727-0910-s009023 | 6 | 2 | 4 | 340.0 |
| line-3-0796-0813-s012047 | 6 | 2 | 4 | 340.0 |
| line-3-1016-0611-s018670 | 6 | 4 | 2 | 170.0 |
| line-3-1067-0556-s020863 | 6 | 4 | 2 | 170.0 |
| line-3-1334-0251-s030042 | 3 | 2 | 1 | 85.0 |
| line-4-0370-0471-s033347 | 3 | 2 | 1 | 85.0 |
| line-4-0433-0561-s030910 | 6 | 4 | 2 | 170.0 |
| line-4-0518-0645-s027651 | 6 | 2 | 4 | 340.0 |
| line-4-0598-0725-s024649 | 6 | 2 | 4 | 340.0 |
| line-4-0689-0795-s020979 | 6 | 4 | 2 | 170.0 |
| line-4-0755-0847-s018986 | 6 | 2 | 4 | 340.0 |
| line-4-0817-0905-s017015 | 6 | 2 | 4 | 340.0 |
| line-4-0852-0961-s015523 | 6 | 4 | 2 | 170.0 |
| line-4-0964-1158-s010014 | 6 | 2 | 4 | 340.0 |
| line-4-1271-1449-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-0222-0838-s027582 | 2 | 2 | 0 | 0.0 |
| line-5-0348-0791-s024430 | 4 | 4 | 0 | 0.0 |
| line-5-0490-0826-s020960 | 4 | 2 | 2 | 170.0 |
| line-5-0586-0763-s017939 | 4 | 2 | 2 | 170.0 |
| line-5-0689-0795-s014768 | 4 | 4 | 0 | 0.0 |
| line-5-0739-0773-s013312 | 4 | 4 | 0 | 0.0 |
| line-5-0845-0690-s010307 | 6 | 2 | 4 | 340.0 |
| line-5-1008-0663-s006246 | 6 | 2 | 4 | 340.0 |
| line-5-1087-0634-s003842 | 6 | 2 | 4 | 340.0 |
| line-5-1251-0639-s000000 | 3 | 2 | 1 | 85.0 |
| line-6-0348-0791-s014036 | 1 | 4 | 0 | 0.0 |
| line-6-0374-0881-s016051 | 1 | 2 | 0 | 0.0 |
| line-6-0385-0981-s018192 | 1 | 4 | 0 | 0.0 |
| line-6-0433-0561-s007870 | 1 | 4 | 0 | 0.0 |
| line-6-0459-1019-s020127 | 2 | 2 | 0 | 0.0 |
| line-6-0506-0527-s006030 | 1 | 2 | 0 | 0.0 |
| line-6-0532-1056-s022078 | 1 | 2 | 0 | 0.0 |
| line-6-0587-1096-s023510 | 1 | 4 | 0 | 0.0 |
| line-6-0613-0464-s003024 | 1 | 2 | 0 | 0.0 |
| line-6-0677-0388-s000887 | 2 | 4 | 0 | 0.0 |
| line-6-0729-1222-s028848 | 1 | 2 | 0 | 0.0 |
| line-6-0780-1249-s030125 | 1 | 4 | 0 | 0.0 |
| line-6-0801-1103-s033926 | 1 | 4 | 0 | 0.0 |
| line-6-0817-1191-s031859 | 1 | 2 | 0 | 0.0 |
| line-6-0833-0419-s057830 | 1 | 2 | 0 | 0.0 |
| line-6-0851-0961-s037180 | 2 | 4 | 0 | 0.0 |
| line-6-0862-0482-s055988 | 1 | 4 | 0 | 0.0 |
| line-6-0922-0522-s053913 | 1 | 2 | 0 | 0.0 |
| line-6-0987-0782-s041887 | 1 | 2 | 0 | 0.0 |
| line-6-0993-0535-s051818 | 1 | 2 | 0 | 0.0 |
| line-6-1038-0623-s045794 | 1 | 4 | 0 | 0.0 |
| line-6-1085-0562-s047909 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/latin-america/Bolivia/La-Paz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
