# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **190 trainsets at 57 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **170 revenue, 14 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0716-1070-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0694-1000-s001959 | forward | revenue | 2 | pending |
| line-1 | line-1-0694-1000-s001959 | reverse | revenue | 2 | pending |
| line-1 | line-1-0737-0920-s003927 | forward | revenue | 2 | pending |
| line-1 | line-1-0737-0920-s003927 | reverse | revenue | 2 | pending |
| line-1 | line-1-0735-0859-s005513 | forward | revenue | 2 | pending |
| line-1 | line-1-0735-0859-s005513 | reverse | revenue | 2 | pending |
| line-1 | line-1-0746-0801-s006847 | forward | revenue | 2 | pending |
| line-1 | line-1-0746-0801-s006847 | reverse | revenue | 2 | pending |
| line-1 | line-1-0735-0705-s009019 | forward | revenue | 2 | pending |
| line-1 | line-1-0735-0705-s009019 | reverse | revenue | 2 | pending |
| line-1 | line-1-0674-0634-s012037 | forward | revenue | 2 | pending |
| line-1 | line-1-0674-0634-s012037 | reverse | revenue | 2 | pending |
| line-1 | line-1-0625-0555-s014150 | forward | revenue | 2 | pending |
| line-1 | line-1-0625-0555-s014150 | reverse | revenue | 2 | pending |
| line-1 | line-1-0611-0455-s016266 | forward | revenue | 1 | pending |
| line-1 | line-1-0611-0455-s016266 | reverse | revenue | 1 | pending |
| line-1 | line-1-0643-0371-s018695 | reverse | revenue | 1 | pending |
| line-1 | line-1-0611-0455-s016266 | forward | spare | 1 | pending |
| line-1 | line-1-0611-0455-s016266 | reverse | spare | 1 | pending |
| line-1 | line-1-0643-0371-s018695 | reverse | spare | 1 | pending |
| line-1 | line-1-0716-1070-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1271-0603-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1057-0709-s006385 | forward | revenue | 3 | pending |
| line-2 | line-2-1057-0709-s006385 | reverse | revenue | 3 | pending |
| line-2 | line-2-1027-0818-s009386 | forward | revenue | 3 | pending |
| line-2 | line-2-1027-0818-s009386 | reverse | revenue | 3 | pending |
| line-2 | line-2-0919-0864-s012396 | forward | revenue | 2 | pending |
| line-2 | line-2-0919-0864-s012396 | reverse | revenue | 2 | pending |
| line-2 | line-2-0824-0946-s015398 | forward | revenue | 2 | pending |
| line-2 | line-2-0824-0946-s015398 | reverse | revenue | 2 | pending |
| line-2 | line-2-0729-1004-s018405 | forward | revenue | 2 | pending |
| line-2 | line-2-0729-1004-s018405 | reverse | revenue | 2 | pending |
| line-2 | line-2-0600-1077-s021727 | forward | revenue | 2 | pending |
| line-2 | line-2-0600-1077-s021727 | reverse | revenue | 2 | pending |
| line-2 | line-2-0507-1164-s024775 | forward | revenue | 2 | pending |
| line-2 | line-2-0507-1164-s024775 | reverse | revenue | 2 | pending |
| line-2 | line-2-0454-1127-s027173 | reverse | revenue | 2 | pending |
| line-2 | line-2-0919-0864-s012396 | forward | spare | 1 | pending |
| line-2 | line-2-0919-0864-s012396 | reverse | spare | 1 | pending |
| line-2 | line-2-0824-0946-s015398 | forward | spare | 1 | pending |
| line-2 | line-2-0824-0946-s015398 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0801-0385-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0801-0458-s001477 | forward | revenue | 2 | pending |
| line-3 | line-3-0801-0458-s001477 | reverse | revenue | 2 | pending |
| line-3 | line-3-0803-0530-s003016 | forward | revenue | 2 | pending |
| line-3 | line-3-0803-0530-s003016 | reverse | revenue | 2 | pending |
| line-3 | line-3-0791-0657-s006036 | forward | revenue | 2 | pending |
| line-3 | line-3-0791-0657-s006036 | reverse | revenue | 2 | pending |
| line-3 | line-3-0792-0747-s009054 | forward | revenue | 2 | pending |
| line-3 | line-3-0792-0747-s009054 | reverse | revenue | 2 | pending |
| line-3 | line-3-0797-0791-s010311 | forward | revenue | 2 | pending |
| line-3 | line-3-0797-0791-s010311 | reverse | revenue | 2 | pending |
| line-3 | line-3-0776-0869-s012078 | forward | revenue | 2 | pending |
| line-3 | line-3-0776-0869-s012078 | reverse | revenue | 1 | pending |
| line-3 | line-3-0815-0963-s014478 | reverse | revenue | 1 | pending |
| line-3 | line-3-0776-0869-s012078 | reverse | spare | 1 | pending |
| line-3 | line-3-0815-0963-s014478 | reverse | spare | 1 | pending |
| line-3 | line-3-0801-0385-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0992-0655-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0923-0686-s003017 | forward | revenue | 3 | pending |
| line-4 | line-4-0923-0686-s003017 | reverse | revenue | 3 | pending |
| line-4 | line-4-0805-0715-s006023 | forward | revenue | 3 | pending |
| line-4 | line-4-0805-0715-s006023 | reverse | revenue | 3 | pending |
| line-4 | line-4-0665-0724-s009030 | forward | revenue | 2 | pending |
| line-4 | line-4-0665-0724-s009030 | reverse | revenue | 2 | pending |
| line-4 | line-4-0393-0727-s014495 | forward | revenue | 2 | pending |
| line-4 | line-4-0393-0727-s014495 | reverse | revenue | 2 | pending |
| line-4 | line-4-0202-0702-s018572 | reverse | revenue | 2 | pending |
| line-4 | line-4-0665-0724-s009030 | forward | spare | 1 | pending |
| line-4 | line-4-0665-0724-s009030 | reverse | spare | 1 | pending |
| line-4 | line-4-0393-0727-s014495 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0221-0334-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0502-0502-s007012 | forward | revenue | 3 | pending |
| line-5 | line-5-0502-0502-s007012 | reverse | revenue | 3 | pending |
| line-5 | line-5-0553-0552-s008936 | forward | revenue | 3 | pending |
| line-5 | line-5-0553-0552-s008936 | reverse | revenue | 3 | pending |
| line-5 | line-5-0606-0623-s010995 | forward | revenue | 2 | pending |
| line-5 | line-5-0606-0623-s010995 | reverse | revenue | 2 | pending |
| line-5 | line-5-0689-0669-s013036 | forward | revenue | 2 | pending |
| line-5 | line-5-0689-0669-s013036 | reverse | revenue | 2 | pending |
| line-5 | line-5-0809-0719-s016051 | forward | revenue | 2 | pending |
| line-5 | line-5-0809-0719-s016051 | reverse | revenue | 2 | pending |
| line-5 | line-5-0926-0786-s019934 | reverse | revenue | 2 | pending |
| line-5 | line-5-0606-0623-s010995 | forward | spare | 1 | pending |
| line-5 | line-5-0606-0623-s010995 | reverse | spare | 1 | pending |
| line-5 | line-5-0689-0669-s013036 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0615-0442-s000000 | forward | revenue | 1 | pending |
| line-6 | line-6-0615-0442-s000000 | reverse | revenue | 1 | pending |
| line-6 | line-6-0553-0552-s002737 | forward | revenue | 1 | pending |
| line-6 | line-6-0393-0727-s007832 | forward | revenue | 1 | pending |
| line-6 | line-6-0393-0727-s007832 | reverse | revenue | 1 | pending |
| line-6 | line-6-0439-0966-s014004 | reverse | revenue | 1 | pending |
| line-6 | line-6-0454-1127-s017348 | forward | revenue | 1 | pending |
| line-6 | line-6-0507-1164-s019059 | forward | revenue | 1 | pending |
| line-6 | line-6-0507-1164-s019059 | reverse | revenue | 1 | pending |
| line-6 | line-6-0582-1059-s021792 | reverse | revenue | 1 | pending |
| line-6 | line-6-0624-0964-s024222 | forward | revenue | 1 | pending |
| line-6 | line-6-0716-0899-s026659 | forward | revenue | 1 | pending |
| line-6 | line-6-0716-0899-s026659 | reverse | revenue | 1 | pending |
| line-6 | line-6-0814-0805-s030254 | reverse | revenue | 1 | pending |
| line-6 | line-6-0926-0786-s033840 | forward | revenue | 1 | pending |
| line-6 | line-6-0992-0655-s037325 | forward | revenue | 1 | pending |
| line-6 | line-6-0992-0655-s037325 | reverse | revenue | 1 | pending |
| line-6 | line-6-1197-0449-s043289 | reverse | revenue | 1 | pending |
| line-6 | line-6-1081-0457-s046793 | forward | revenue | 1 | pending |
| line-6 | line-6-0934-0458-s050305 | forward | revenue | 1 | pending |
| line-6 | line-6-0934-0458-s050305 | reverse | spare | 1 | pending |
| line-6 | line-6-0784-0461-s053329 | reverse | spare | 1 | pending |
| line-6 | line-6-0663-0468-s056336 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**65 trainsets exceed the reference platform envelope**, requiring **5,525.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0611-0455-s016266 | 4 | 4 | 0 | 0.0 |
| line-1-0625-0555-s014150 | 4 | 2 | 2 | 170.0 |
| line-1-0643-0371-s018695 | 2 | 2 | 0 | 0.0 |
| line-1-0674-0634-s012037 | 4 | 2 | 2 | 170.0 |
| line-1-0694-1000-s001959 | 4 | 2 | 2 | 170.0 |
| line-1-0716-1070-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0735-0705-s009019 | 4 | 2 | 2 | 170.0 |
| line-1-0735-0859-s005513 | 4 | 2 | 2 | 170.0 |
| line-1-0737-0920-s003927 | 4 | 4 | 0 | 0.0 |
| line-1-0746-0801-s006847 | 4 | 2 | 2 | 170.0 |
| line-2-0454-1127-s027173 | 2 | 2 | 0 | 0.0 |
| line-2-0507-1164-s024775 | 4 | 4 | 0 | 0.0 |
| line-2-0600-1077-s021727 | 4 | 4 | 0 | 0.0 |
| line-2-0729-1004-s018405 | 4 | 2 | 2 | 170.0 |
| line-2-0824-0946-s015398 | 6 | 4 | 2 | 170.0 |
| line-2-0919-0864-s012396 | 6 | 2 | 4 | 340.0 |
| line-2-1027-0818-s009386 | 6 | 2 | 4 | 340.0 |
| line-2-1057-0709-s006385 | 6 | 2 | 4 | 340.0 |
| line-2-1271-0603-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0776-0869-s012078 | 4 | 2 | 2 | 170.0 |
| line-3-0791-0657-s006036 | 4 | 2 | 2 | 170.0 |
| line-3-0792-0747-s009054 | 4 | 2 | 2 | 170.0 |
| line-3-0797-0791-s010311 | 4 | 4 | 0 | 0.0 |
| line-3-0801-0385-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0801-0458-s001477 | 4 | 4 | 0 | 0.0 |
| line-3-0803-0530-s003016 | 4 | 2 | 2 | 170.0 |
| line-3-0815-0963-s014478 | 2 | 2 | 0 | 0.0 |
| line-4-0202-0702-s018572 | 2 | 2 | 0 | 0.0 |
| line-4-0393-0727-s014495 | 5 | 4 | 1 | 85.0 |
| line-4-0665-0724-s009030 | 6 | 2 | 4 | 340.0 |
| line-4-0805-0715-s006023 | 6 | 4 | 2 | 170.0 |
| line-4-0923-0686-s003017 | 6 | 2 | 4 | 340.0 |
| line-4-0992-0655-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-0221-0334-s000000 | 3 | 2 | 1 | 85.0 |
| line-5-0502-0502-s007012 | 6 | 2 | 4 | 340.0 |
| line-5-0553-0552-s008936 | 6 | 4 | 2 | 170.0 |
| line-5-0606-0623-s010995 | 6 | 2 | 4 | 340.0 |
| line-5-0689-0669-s013036 | 5 | 2 | 3 | 255.0 |
| line-5-0809-0719-s016051 | 4 | 4 | 0 | 0.0 |
| line-5-0926-0786-s019934 | 2 | 2 | 0 | 0.0 |
| line-6-0393-0727-s007832 | 2 | 4 | 0 | 0.0 |
| line-6-0439-0966-s014004 | 1 | 2 | 0 | 0.0 |
| line-6-0454-1127-s017348 | 1 | 4 | 0 | 0.0 |
| line-6-0507-1164-s019059 | 2 | 4 | 0 | 0.0 |
| line-6-0553-0552-s002737 | 1 | 4 | 0 | 0.0 |
| line-6-0582-1059-s021792 | 1 | 4 | 0 | 0.0 |
| line-6-0615-0442-s000000 | 2 | 4 | 0 | 0.0 |
| line-6-0624-0964-s024222 | 1 | 2 | 0 | 0.0 |
| line-6-0663-0468-s056336 | 1 | 2 | 0 | 0.0 |
| line-6-0716-0899-s026659 | 2 | 4 | 0 | 0.0 |
| line-6-0784-0461-s053329 | 1 | 4 | 0 | 0.0 |
| line-6-0814-0805-s030254 | 1 | 4 | 0 | 0.0 |
| line-6-0926-0786-s033840 | 1 | 4 | 0 | 0.0 |
| line-6-0934-0458-s050305 | 2 | 2 | 0 | 0.0 |
| line-6-0992-0655-s037325 | 2 | 4 | 0 | 0.0 |
| line-6-1081-0457-s046793 | 1 | 2 | 0 | 0.0 |
| line-6-1197-0449-s043289 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Mombasa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
