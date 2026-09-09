# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **232 trainsets at 63 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **208 revenue, 19 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1060-1370-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0970-1176-s004974 | forward | revenue | 3 | pending |
| line-1 | line-1-0970-1176-s004974 | reverse | revenue | 3 | pending |
| line-1 | line-1-0849-1086-s008198 | forward | revenue | 3 | pending |
| line-1 | line-1-0849-1086-s008198 | reverse | revenue | 3 | pending |
| line-1 | line-1-0823-1001-s010130 | forward | revenue | 3 | pending |
| line-1 | line-1-0823-1001-s010130 | reverse | revenue | 3 | pending |
| line-1 | line-1-0739-0896-s013136 | forward | revenue | 3 | pending |
| line-1 | line-1-0739-0896-s013136 | reverse | revenue | 3 | pending |
| line-1 | line-1-0767-0777-s016155 | forward | revenue | 3 | pending |
| line-1 | line-1-0767-0777-s016155 | reverse | revenue | 3 | pending |
| line-1 | line-1-0688-0701-s019163 | forward | revenue | 3 | pending |
| line-1 | line-1-0688-0701-s019163 | reverse | revenue | 3 | pending |
| line-1 | line-1-0629-0609-s022167 | forward | revenue | 3 | pending |
| line-1 | line-1-0629-0609-s022167 | reverse | revenue | 2 | pending |
| line-1 | line-1-0557-0642-s024262 | forward | revenue | 2 | pending |
| line-1 | line-1-0557-0642-s024262 | reverse | revenue | 2 | pending |
| line-1 | line-1-0513-0515-s027166 | forward | revenue | 2 | pending |
| line-1 | line-1-0513-0515-s027166 | reverse | revenue | 2 | pending |
| line-1 | line-1-0280-0052-s038661 | reverse | revenue | 2 | pending |
| line-1 | line-1-0629-0609-s022167 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0642-s024262 | forward | spare | 1 | pending |
| line-1 | line-1-0557-0642-s024262 | reverse | spare | 1 | pending |
| line-1 | line-1-0513-0515-s027166 | forward | spare | 1 | pending |
| line-1 | line-1-0513-0515-s027166 | reverse | spare | 1 | pending |
| line-1 | line-1-0280-0052-s038661 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0435-1266-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0504-1119-s003512 | forward | revenue | 3 | pending |
| line-2 | line-2-0504-1119-s003512 | reverse | revenue | 2 | pending |
| line-2 | line-2-0623-1078-s007011 | forward | revenue | 2 | pending |
| line-2 | line-2-0623-1078-s007011 | reverse | revenue | 2 | pending |
| line-2 | line-2-0689-0987-s010014 | forward | revenue | 2 | pending |
| line-2 | line-2-0689-0987-s010014 | reverse | revenue | 2 | pending |
| line-2 | line-2-0739-0957-s011342 | forward | revenue | 2 | pending |
| line-2 | line-2-0739-0957-s011342 | reverse | revenue | 2 | pending |
| line-2 | line-2-0790-0959-s013016 | forward | revenue | 2 | pending |
| line-2 | line-2-0790-0959-s013016 | reverse | revenue | 2 | pending |
| line-2 | line-2-0856-0856-s016041 | forward | revenue | 2 | pending |
| line-2 | line-2-0856-0856-s016041 | reverse | revenue | 2 | pending |
| line-2 | line-2-0918-0733-s019050 | forward | revenue | 2 | pending |
| line-2 | line-2-0918-0733-s019050 | reverse | revenue | 2 | pending |
| line-2 | line-2-1025-0642-s022061 | forward | revenue | 2 | pending |
| line-2 | line-2-1025-0642-s022061 | reverse | revenue | 2 | pending |
| line-2 | line-2-1100-0652-s023710 | forward | revenue | 2 | pending |
| line-2 | line-2-1100-0652-s023710 | reverse | revenue | 2 | pending |
| line-2 | line-2-1161-0515-s028687 | reverse | revenue | 2 | pending |
| line-2 | line-2-0504-1119-s003512 | reverse | spare | 1 | pending |
| line-2 | line-2-0623-1078-s007011 | forward | spare | 1 | pending |
| line-2 | line-2-0623-1078-s007011 | reverse | spare | 1 | pending |
| line-2 | line-2-0689-0987-s010014 | forward | spare | 1 | pending |
| line-2 | line-2-0689-0987-s010014 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1224-0755-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-1145-0748-s001804 | forward | revenue | 3 | pending |
| line-3 | line-3-1145-0748-s001804 | reverse | revenue | 3 | pending |
| line-3 | line-3-1105-0784-s003007 | forward | revenue | 3 | pending |
| line-3 | line-3-1105-0784-s003007 | reverse | revenue | 2 | pending |
| line-3 | line-3-0978-0833-s006015 | forward | revenue | 2 | pending |
| line-3 | line-3-0978-0833-s006015 | reverse | revenue | 2 | pending |
| line-3 | line-3-0857-0781-s009027 | forward | revenue | 2 | pending |
| line-3 | line-3-0857-0781-s009027 | reverse | revenue | 2 | pending |
| line-3 | line-3-0802-0786-s010514 | forward | revenue | 2 | pending |
| line-3 | line-3-0802-0786-s010514 | reverse | revenue | 2 | pending |
| line-3 | line-3-0741-0770-s012031 | forward | revenue | 2 | pending |
| line-3 | line-3-0741-0770-s012031 | reverse | revenue | 2 | pending |
| line-3 | line-3-0674-0789-s014097 | forward | revenue | 2 | pending |
| line-3 | line-3-0674-0789-s014097 | reverse | revenue | 2 | pending |
| line-3 | line-3-0611-0819-s016178 | forward | revenue | 2 | pending |
| line-3 | line-3-0611-0819-s016178 | reverse | revenue | 2 | pending |
| line-3 | line-3-0576-0897-s018057 | forward | revenue | 2 | pending |
| line-3 | line-3-0576-0897-s018057 | reverse | revenue | 2 | pending |
| line-3 | line-3-0059-0992-s029896 | reverse | revenue | 2 | pending |
| line-3 | line-3-1105-0784-s003007 | reverse | spare | 1 | pending |
| line-3 | line-3-0978-0833-s006015 | forward | spare | 1 | pending |
| line-3 | line-3-0978-0833-s006015 | reverse | spare | 1 | pending |
| line-3 | line-3-0857-0781-s009027 | forward | spare | 1 | pending |
| line-3 | line-3-0857-0781-s009027 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1211-0997-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-1122-0947-s003260 | forward | revenue | 3 | pending |
| line-4 | line-4-1122-0947-s003260 | reverse | revenue | 3 | pending |
| line-4 | line-4-0955-0938-s006785 | forward | revenue | 3 | pending |
| line-4 | line-4-0955-0938-s006785 | reverse | revenue | 3 | pending |
| line-4 | line-4-0813-0924-s009786 | forward | revenue | 3 | pending |
| line-4 | line-4-0813-0924-s009786 | reverse | revenue | 3 | pending |
| line-4 | line-4-0690-0858-s012793 | forward | revenue | 3 | pending |
| line-4 | line-4-0690-0858-s012793 | reverse | revenue | 3 | pending |
| line-4 | line-4-0617-0854-s014560 | forward | revenue | 3 | pending |
| line-4 | line-4-0617-0854-s014560 | reverse | revenue | 3 | pending |
| line-4 | line-4-0581-0821-s015809 | forward | revenue | 3 | pending |
| line-4 | line-4-0581-0821-s015809 | reverse | revenue | 3 | pending |
| line-4 | line-4-0442-0785-s019309 | forward | revenue | 2 | pending |
| line-4 | line-4-0442-0785-s019309 | reverse | revenue | 2 | pending |
| line-4 | line-4-0029-0596-s030613 | reverse | revenue | 2 | pending |
| line-4 | line-4-0442-0785-s019309 | forward | spare | 1 | pending |
| line-4 | line-4-0442-0785-s019309 | reverse | spare | 1 | pending |
| line-4 | line-4-0029-0596-s030613 | reverse | spare | 1 | pending |
| line-4 | line-4-1211-0997-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-1122-0947-s003260 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0454-0551-s000000 | forward | revenue | 1 | pending |
| line-5 | line-5-0454-0551-s000000 | reverse | revenue | 1 | pending |
| line-5 | line-5-0545-0646-s003208 | reverse | revenue | 1 | pending |
| line-5 | line-5-0569-0759-s006017 | forward | revenue | 1 | pending |
| line-5 | line-5-0611-0819-s007577 | forward | revenue | 1 | pending |
| line-5 | line-5-0625-0881-s009039 | forward | revenue | 1 | pending |
| line-5 | line-5-0625-0881-s009039 | reverse | revenue | 1 | pending |
| line-5 | line-5-0739-0957-s012188 | reverse | revenue | 1 | pending |
| line-5 | line-5-0824-1088-s015739 | forward | revenue | 1 | pending |
| line-5 | line-5-0878-1134-s017608 | forward | revenue | 1 | pending |
| line-5 | line-5-0936-1200-s019573 | forward | revenue | 1 | pending |
| line-5 | line-5-0936-1200-s019573 | reverse | revenue | 1 | pending |
| line-5 | line-5-0962-1180-s021552 | reverse | revenue | 1 | pending |
| line-5 | line-5-1150-1079-s026387 | reverse | revenue | 1 | pending |
| line-5 | line-5-1122-0947-s030980 | forward | revenue | 1 | pending |
| line-5 | line-5-1186-0856-s033389 | forward | revenue | 1 | pending |
| line-5 | line-5-1186-0856-s033389 | reverse | revenue | 1 | pending |
| line-5 | line-5-1136-0729-s036393 | reverse | revenue | 1 | pending |
| line-5 | line-5-1100-0652-s038682 | reverse | revenue | 1 | pending |
| line-5 | line-5-1081-0581-s041025 | forward | revenue | 1 | pending |
| line-5 | line-5-1161-0515-s043418 | forward | revenue | 1 | pending |
| line-5 | line-5-1161-0515-s043418 | reverse | revenue | 1 | pending |
| line-5 | line-5-0897-0393-s055038 | reverse | revenue | 1 | pending |
| line-5 | line-5-0800-0433-s057411 | reverse | spare | 1 | pending |
| line-5 | line-5-0696-0446-s059798 | forward | spare | 1 | pending |
| line-5 | line-5-0513-0515-s064046 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**98 trainsets exceed the reference platform envelope**, requiring **8,330.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0280-0052-s038661 | 3 | 2 | 1 | 85.0 |
| line-1-0513-0515-s027166 | 6 | 4 | 2 | 170.0 |
| line-1-0557-0642-s024262 | 6 | 4 | 2 | 170.0 |
| line-1-0629-0609-s022167 | 6 | 2 | 4 | 340.0 |
| line-1-0688-0701-s019163 | 6 | 2 | 4 | 340.0 |
| line-1-0739-0896-s013136 | 6 | 2 | 4 | 340.0 |
| line-1-0767-0777-s016155 | 6 | 4 | 2 | 170.0 |
| line-1-0823-1001-s010130 | 6 | 2 | 4 | 340.0 |
| line-1-0849-1086-s008198 | 6 | 4 | 2 | 170.0 |
| line-1-0970-1176-s004974 | 6 | 4 | 2 | 170.0 |
| line-1-1060-1370-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0435-1266-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0504-1119-s003512 | 6 | 2 | 4 | 340.0 |
| line-2-0623-1078-s007011 | 6 | 2 | 4 | 340.0 |
| line-2-0689-0987-s010014 | 6 | 2 | 4 | 340.0 |
| line-2-0739-0957-s011342 | 4 | 4 | 0 | 0.0 |
| line-2-0790-0959-s013016 | 4 | 2 | 2 | 170.0 |
| line-2-0856-0856-s016041 | 4 | 2 | 2 | 170.0 |
| line-2-0918-0733-s019050 | 4 | 2 | 2 | 170.0 |
| line-2-1025-0642-s022061 | 4 | 2 | 2 | 170.0 |
| line-2-1100-0652-s023710 | 4 | 4 | 0 | 0.0 |
| line-2-1161-0515-s028687 | 2 | 2 | 0 | 0.0 |
| line-3-0059-0992-s029896 | 2 | 2 | 0 | 0.0 |
| line-3-0576-0897-s018057 | 4 | 2 | 2 | 170.0 |
| line-3-0611-0819-s016178 | 4 | 4 | 0 | 0.0 |
| line-3-0674-0789-s014097 | 4 | 2 | 2 | 170.0 |
| line-3-0741-0770-s012031 | 4 | 4 | 0 | 0.0 |
| line-3-0802-0786-s010514 | 4 | 2 | 2 | 170.0 |
| line-3-0857-0781-s009027 | 6 | 2 | 4 | 340.0 |
| line-3-0978-0833-s006015 | 6 | 2 | 4 | 340.0 |
| line-3-1105-0784-s003007 | 6 | 2 | 4 | 340.0 |
| line-3-1145-0748-s001804 | 6 | 4 | 2 | 170.0 |
| line-3-1224-0755-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0029-0596-s030613 | 3 | 2 | 1 | 85.0 |
| line-4-0442-0785-s019309 | 6 | 2 | 4 | 340.0 |
| line-4-0581-0821-s015809 | 6 | 2 | 4 | 340.0 |
| line-4-0617-0854-s014560 | 6 | 4 | 2 | 170.0 |
| line-4-0690-0858-s012793 | 6 | 2 | 4 | 340.0 |
| line-4-0813-0924-s009786 | 6 | 2 | 4 | 340.0 |
| line-4-0955-0938-s006785 | 6 | 2 | 4 | 340.0 |
| line-4-1122-0947-s003260 | 7 | 4 | 3 | 255.0 |
| line-4-1211-0997-s000000 | 4 | 2 | 2 | 170.0 |
| line-5-0454-0551-s000000 | 2 | 2 | 0 | 0.0 |
| line-5-0513-0515-s064046 | 1 | 4 | 0 | 0.0 |
| line-5-0545-0646-s003208 | 1 | 4 | 0 | 0.0 |
| line-5-0569-0759-s006017 | 1 | 2 | 0 | 0.0 |
| line-5-0611-0819-s007577 | 1 | 4 | 0 | 0.0 |
| line-5-0625-0881-s009039 | 2 | 4 | 0 | 0.0 |
| line-5-0696-0446-s059798 | 1 | 2 | 0 | 0.0 |
| line-5-0739-0957-s012188 | 1 | 4 | 0 | 0.0 |
| line-5-0800-0433-s057411 | 1 | 2 | 0 | 0.0 |
| line-5-0824-1088-s015739 | 1 | 4 | 0 | 0.0 |
| line-5-0878-1134-s017608 | 1 | 2 | 0 | 0.0 |
| line-5-0897-0393-s055038 | 1 | 2 | 0 | 0.0 |
| line-5-0936-1200-s019573 | 2 | 2 | 0 | 0.0 |
| line-5-0962-1180-s021552 | 1 | 4 | 0 | 0.0 |
| line-5-1081-0581-s041025 | 1 | 2 | 0 | 0.0 |
| line-5-1100-0652-s038682 | 1 | 4 | 0 | 0.0 |
| line-5-1122-0947-s030980 | 1 | 4 | 0 | 0.0 |
| line-5-1136-0729-s036393 | 1 | 4 | 0 | 0.0 |
| line-5-1150-1079-s026387 | 1 | 2 | 0 | 0.0 |
| line-5-1161-0515-s043418 | 2 | 4 | 0 | 0.0 |
| line-5-1186-0856-s033389 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Port-Harcourt/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
