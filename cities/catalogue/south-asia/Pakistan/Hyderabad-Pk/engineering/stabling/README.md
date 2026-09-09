# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **216 trainsets at 55 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **193 revenue, 17 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0668-1087-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0677-0942-s004220 | forward | revenue | 3 | pending |
| line-1 | line-1-0677-0942-s004220 | reverse | revenue | 3 | pending |
| line-1 | line-1-0761-0860-s007230 | forward | revenue | 2 | pending |
| line-1 | line-1-0761-0860-s007230 | reverse | revenue | 2 | pending |
| line-1 | line-1-0787-0814-s008916 | forward | revenue | 2 | pending |
| line-1 | line-1-0787-0814-s008916 | reverse | revenue | 2 | pending |
| line-1 | line-1-0873-0750-s012185 | forward | revenue | 2 | pending |
| line-1 | line-1-0873-0750-s012185 | reverse | revenue | 2 | pending |
| line-1 | line-1-0884-0617-s015201 | forward | revenue | 2 | pending |
| line-1 | line-1-0884-0617-s015201 | reverse | revenue | 2 | pending |
| line-1 | line-1-0962-0549-s018478 | reverse | revenue | 2 | pending |
| line-1 | line-1-0761-0860-s007230 | forward | spare | 1 | pending |
| line-1 | line-1-0761-0860-s007230 | reverse | spare | 1 | pending |
| line-1 | line-1-0787-0814-s008916 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0643-0351-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0640-0416-s002909 | forward | revenue | 3 | pending |
| line-2 | line-2-0640-0416-s002909 | reverse | revenue | 3 | pending |
| line-2 | line-2-0734-0564-s007011 | forward | revenue | 2 | pending |
| line-2 | line-2-0734-0564-s007011 | reverse | revenue | 2 | pending |
| line-2 | line-2-0728-0674-s010012 | forward | revenue | 2 | pending |
| line-2 | line-2-0728-0674-s010012 | reverse | revenue | 2 | pending |
| line-2 | line-2-0711-0783-s013020 | forward | revenue | 2 | pending |
| line-2 | line-2-0711-0783-s013020 | reverse | revenue | 2 | pending |
| line-2 | line-2-0787-0814-s014830 | forward | revenue | 2 | pending |
| line-2 | line-2-0787-0814-s014830 | reverse | revenue | 2 | pending |
| line-2 | line-2-0868-0908-s017802 | forward | revenue | 2 | pending |
| line-2 | line-2-0868-0908-s017802 | reverse | revenue | 2 | pending |
| line-2 | line-2-0925-1015-s020778 | reverse | revenue | 2 | pending |
| line-2 | line-2-0734-0564-s007011 | forward | spare | 1 | pending |
| line-2 | line-2-0734-0564-s007011 | reverse | spare | 1 | pending |
| line-2 | line-2-0728-0674-s010012 | forward | spare | 1 | pending |
| line-2 | line-2-0728-0674-s010012 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1157-0800-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-1036-0847-s003634 | forward | revenue | 3 | pending |
| line-3 | line-3-1036-0847-s003634 | reverse | revenue | 3 | pending |
| line-3 | line-3-0918-0812-s006648 | forward | revenue | 3 | pending |
| line-3 | line-3-0918-0812-s006648 | reverse | revenue | 2 | pending |
| line-3 | line-3-0837-0915-s009674 | forward | revenue | 2 | pending |
| line-3 | line-3-0837-0915-s009674 | reverse | revenue | 2 | pending |
| line-3 | line-3-0724-0962-s012696 | forward | revenue | 2 | pending |
| line-3 | line-3-0724-0962-s012696 | reverse | revenue | 2 | pending |
| line-3 | line-3-0636-0916-s014955 | forward | revenue | 2 | pending |
| line-3 | line-3-0636-0916-s014955 | reverse | revenue | 2 | pending |
| line-3 | line-3-0479-0923-s019452 | reverse | revenue | 2 | pending |
| line-3 | line-3-0918-0812-s006648 | reverse | spare | 1 | pending |
| line-3 | line-3-0837-0915-s009674 | forward | spare | 1 | pending |
| line-3 | line-3-0837-0915-s009674 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1224-1063-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0970-0973-s005912 | forward | revenue | 3 | pending |
| line-4 | line-4-0970-0973-s005912 | reverse | revenue | 3 | pending |
| line-4 | line-4-0871-0860-s009016 | forward | revenue | 3 | pending |
| line-4 | line-4-0871-0860-s009016 | reverse | revenue | 3 | pending |
| line-4 | line-4-0807-0840-s010636 | forward | revenue | 3 | pending |
| line-4 | line-4-0807-0840-s010636 | reverse | revenue | 3 | pending |
| line-4 | line-4-0693-0802-s013656 | forward | revenue | 3 | pending |
| line-4 | line-4-0693-0802-s013656 | reverse | revenue | 3 | pending |
| line-4 | line-4-0612-0705-s016672 | forward | revenue | 3 | pending |
| line-4 | line-4-0612-0705-s016672 | reverse | revenue | 3 | pending |
| line-4 | line-4-0563-0673-s017941 | forward | revenue | 3 | pending |
| line-4 | line-4-0563-0673-s017941 | reverse | revenue | 3 | pending |
| line-4 | line-4-0089-0541-s029367 | reverse | revenue | 2 | pending |
| line-4 | line-4-0089-0541-s029367 | reverse | spare | 1 | pending |
| line-4 | line-4-1224-1063-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0970-0973-s005912 | forward | spare | 1 | pending |
| line-4 | line-4-0970-0973-s005912 | reverse | spare | 1 | pending |
| line-4 | line-4-0871-0860-s009016 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0726-0313-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0780-0374-s002153 | forward | revenue | 3 | pending |
| line-5 | line-5-0780-0374-s002153 | reverse | revenue | 3 | pending |
| line-5 | line-5-0786-0583-s007024 | forward | revenue | 3 | pending |
| line-5 | line-5-0786-0583-s007024 | reverse | revenue | 3 | pending |
| line-5 | line-5-0830-0705-s010050 | forward | revenue | 3 | pending |
| line-5 | line-5-0830-0705-s010050 | reverse | revenue | 3 | pending |
| line-5 | line-5-0770-0774-s012379 | forward | revenue | 3 | pending |
| line-5 | line-5-0770-0774-s012379 | reverse | revenue | 3 | pending |
| line-5 | line-5-0787-0853-s014680 | forward | revenue | 3 | pending |
| line-5 | line-5-0787-0853-s014680 | reverse | revenue | 3 | pending |
| line-5 | line-5-0815-0982-s017688 | forward | revenue | 3 | pending |
| line-5 | line-5-0815-0982-s017688 | reverse | revenue | 3 | pending |
| line-5 | line-5-0832-1071-s020024 | forward | revenue | 2 | pending |
| line-5 | line-5-0832-1071-s020024 | reverse | revenue | 2 | pending |
| line-5 | line-5-0884-1598-s031646 | reverse | revenue | 2 | pending |
| line-5 | line-5-0832-1071-s020024 | forward | spare | 1 | pending |
| line-5 | line-5-0832-1071-s020024 | reverse | spare | 1 | pending |
| line-5 | line-5-0884-1598-s031646 | reverse | spare | 1 | pending |
| line-5 | line-5-0726-0313-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0780-0374-s002153 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0643-0351-s000723 | forward | revenue | 1 | pending |
| line-6 | line-6-0643-0351-s000723 | reverse | revenue | 1 | pending |
| line-6 | line-6-0640-0416-s002097 | forward | revenue | 1 | pending |
| line-6 | line-6-0544-0594-s007018 | forward | revenue | 1 | pending |
| line-6 | line-6-0544-0594-s007018 | reverse | revenue | 1 | pending |
| line-6 | line-6-0563-0673-s008772 | forward | revenue | 1 | pending |
| line-6 | line-6-0479-0923-s014682 | forward | revenue | 1 | pending |
| line-6 | line-6-0479-0923-s014682 | reverse | revenue | 1 | pending |
| line-6 | line-6-0523-1050-s018500 | forward | revenue | 1 | pending |
| line-6 | line-6-0668-1087-s022320 | forward | revenue | 1 | pending |
| line-6 | line-6-0668-1087-s022320 | reverse | revenue | 1 | pending |
| line-6 | line-6-0772-1141-s028054 | forward | revenue | 1 | pending |
| line-6 | line-6-0832-1071-s030080 | forward | revenue | 1 | pending |
| line-6 | line-6-0832-1071-s030080 | reverse | revenue | 1 | pending |
| line-6 | line-6-0925-1015-s032514 | forward | revenue | 1 | pending |
| line-6 | line-6-0980-0964-s034037 | forward | revenue | 1 | pending |
| line-6 | line-6-0980-0964-s034037 | reverse | revenue | 1 | pending |
| line-6 | line-6-1157-0800-s042190 | forward | revenue | 1 | pending |
| line-6 | line-6-1063-0555-s048080 | forward | revenue | 1 | pending |
| line-6 | line-6-1063-0555-s048080 | reverse | revenue | 1 | pending |
| line-6 | line-6-0991-0427-s051587 | forward | revenue | 1 | pending |
| line-6 | line-6-0792-0352-s056378 | forward | spare | 1 | pending |
| line-6 | line-6-0792-0352-s056378 | reverse | spare | 1 | pending |
| line-6 | line-6-0726-0313-s058597 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**90 trainsets exceed the reference platform envelope**, requiring **7,650.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0668-1087-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0677-0942-s004220 | 6 | 2 | 4 | 340.0 |
| line-1-0761-0860-s007230 | 6 | 4 | 2 | 170.0 |
| line-1-0787-0814-s008916 | 5 | 4 | 1 | 85.0 |
| line-1-0873-0750-s012185 | 4 | 2 | 2 | 170.0 |
| line-1-0884-0617-s015201 | 4 | 2 | 2 | 170.0 |
| line-1-0962-0549-s018478 | 2 | 2 | 0 | 0.0 |
| line-2-0640-0416-s002909 | 6 | 4 | 2 | 170.0 |
| line-2-0643-0351-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0711-0783-s013020 | 4 | 4 | 0 | 0.0 |
| line-2-0728-0674-s010012 | 6 | 2 | 4 | 340.0 |
| line-2-0734-0564-s007011 | 6 | 2 | 4 | 340.0 |
| line-2-0787-0814-s014830 | 4 | 4 | 0 | 0.0 |
| line-2-0868-0908-s017802 | 4 | 2 | 2 | 170.0 |
| line-2-0925-1015-s020778 | 2 | 2 | 0 | 0.0 |
| line-3-0479-0923-s019452 | 2 | 2 | 0 | 0.0 |
| line-3-0636-0916-s014955 | 4 | 2 | 2 | 170.0 |
| line-3-0724-0962-s012696 | 4 | 2 | 2 | 170.0 |
| line-3-0837-0915-s009674 | 6 | 2 | 4 | 340.0 |
| line-3-0918-0812-s006648 | 6 | 2 | 4 | 340.0 |
| line-3-1036-0847-s003634 | 6 | 2 | 4 | 340.0 |
| line-3-1157-0800-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0089-0541-s029367 | 3 | 2 | 1 | 85.0 |
| line-4-0563-0673-s017941 | 6 | 4 | 2 | 170.0 |
| line-4-0612-0705-s016672 | 6 | 2 | 4 | 340.0 |
| line-4-0693-0802-s013656 | 6 | 4 | 2 | 170.0 |
| line-4-0807-0840-s010636 | 6 | 4 | 2 | 170.0 |
| line-4-0871-0860-s009016 | 7 | 2 | 5 | 425.0 |
| line-4-0970-0973-s005912 | 8 | 4 | 4 | 340.0 |
| line-4-1224-1063-s000000 | 4 | 2 | 2 | 170.0 |
| line-5-0726-0313-s000000 | 4 | 2 | 2 | 170.0 |
| line-5-0770-0774-s012379 | 6 | 2 | 4 | 340.0 |
| line-5-0780-0374-s002153 | 7 | 4 | 3 | 255.0 |
| line-5-0786-0583-s007024 | 6 | 2 | 4 | 340.0 |
| line-5-0787-0853-s014680 | 6 | 4 | 2 | 170.0 |
| line-5-0815-0982-s017688 | 6 | 2 | 4 | 340.0 |
| line-5-0830-0705-s010050 | 6 | 2 | 4 | 340.0 |
| line-5-0832-1071-s020024 | 6 | 4 | 2 | 170.0 |
| line-5-0884-1598-s031646 | 3 | 2 | 1 | 85.0 |
| line-6-0479-0923-s014682 | 2 | 4 | 0 | 0.0 |
| line-6-0523-1050-s018500 | 1 | 2 | 0 | 0.0 |
| line-6-0544-0594-s007018 | 2 | 2 | 0 | 0.0 |
| line-6-0563-0673-s008772 | 1 | 4 | 0 | 0.0 |
| line-6-0640-0416-s002097 | 1 | 4 | 0 | 0.0 |
| line-6-0643-0351-s000723 | 2 | 4 | 0 | 0.0 |
| line-6-0668-1087-s022320 | 2 | 4 | 0 | 0.0 |
| line-6-0726-0313-s058597 | 1 | 4 | 0 | 0.0 |
| line-6-0772-1141-s028054 | 1 | 2 | 0 | 0.0 |
| line-6-0792-0352-s056378 | 2 | 4 | 0 | 0.0 |
| line-6-0832-1071-s030080 | 2 | 4 | 0 | 0.0 |
| line-6-0925-1015-s032514 | 1 | 4 | 0 | 0.0 |
| line-6-0980-0964-s034037 | 2 | 4 | 0 | 0.0 |
| line-6-0991-0427-s051587 | 1 | 2 | 0 | 0.0 |
| line-6-1063-0555-s048080 | 2 | 2 | 0 | 0.0 |
| line-6-1157-0800-s042190 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Hyderabad-Pk/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
