# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **221 trainsets at 54 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **198 revenue, 18 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0884-0147-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0890-0302-s003630 | forward | revenue | 3 | pending |
| line-1 | line-1-0890-0302-s003630 | reverse | revenue | 3 | pending |
| line-1 | line-1-0898-0389-s005486 | forward | revenue | 3 | pending |
| line-1 | line-1-0898-0389-s005486 | reverse | revenue | 3 | pending |
| line-1 | line-1-0902-0492-s007579 | forward | revenue | 2 | pending |
| line-1 | line-1-0902-0492-s007579 | reverse | revenue | 2 | pending |
| line-1 | line-1-0875-0568-s009660 | forward | revenue | 2 | pending |
| line-1 | line-1-0875-0568-s009660 | reverse | revenue | 2 | pending |
| line-1 | line-1-0858-0707-s012687 | forward | revenue | 2 | pending |
| line-1 | line-1-0858-0707-s012687 | reverse | revenue | 2 | pending |
| line-1 | line-1-0806-0800-s015204 | forward | revenue | 2 | pending |
| line-1 | line-1-0806-0800-s015204 | reverse | revenue | 2 | pending |
| line-1 | line-1-0858-0899-s018729 | forward | revenue | 2 | pending |
| line-1 | line-1-0858-0899-s018729 | reverse | revenue | 2 | pending |
| line-1 | line-1-0791-1020-s021737 | forward | revenue | 2 | pending |
| line-1 | line-1-0791-1020-s021737 | reverse | revenue | 2 | pending |
| line-1 | line-1-0782-1167-s024752 | forward | revenue | 2 | pending |
| line-1 | line-1-0782-1167-s024752 | reverse | revenue | 2 | pending |
| line-1 | line-1-0779-1508-s031774 | reverse | revenue | 2 | pending |
| line-1 | line-1-0902-0492-s007579 | forward | spare | 1 | pending |
| line-1 | line-1-0902-0492-s007579 | reverse | spare | 1 | pending |
| line-1 | line-1-0875-0568-s009660 | forward | spare | 1 | pending |
| line-1 | line-1-0875-0568-s009660 | reverse | spare | 1 | pending |
| line-1 | line-1-0858-0707-s012687 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1343-0019-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-1054-0393-s011169 | forward | revenue | 4 | pending |
| line-2 | line-2-1054-0393-s011169 | reverse | revenue | 3 | pending |
| line-2 | line-2-0966-0458-s013954 | forward | revenue | 3 | pending |
| line-2 | line-2-0966-0458-s013954 | reverse | revenue | 3 | pending |
| line-2 | line-2-0908-0574-s016968 | forward | revenue | 3 | pending |
| line-2 | line-2-0908-0574-s016968 | reverse | revenue | 3 | pending |
| line-2 | line-2-0821-0636-s019979 | forward | revenue | 3 | pending |
| line-2 | line-2-0821-0636-s019979 | reverse | revenue | 3 | pending |
| line-2 | line-2-0800-0724-s022985 | forward | revenue | 3 | pending |
| line-2 | line-2-0800-0724-s022985 | reverse | revenue | 3 | pending |
| line-2 | line-2-0703-0794-s026011 | forward | revenue | 3 | pending |
| line-2 | line-2-0703-0794-s026011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0573-0995-s031539 | reverse | revenue | 3 | pending |
| line-2 | line-2-1054-0393-s011169 | reverse | spare | 1 | pending |
| line-2 | line-2-0966-0458-s013954 | forward | spare | 1 | pending |
| line-2 | line-2-0966-0458-s013954 | reverse | spare | 1 | pending |
| line-2 | line-2-0908-0574-s016968 | forward | spare | 1 | pending |
| line-2 | line-2-0908-0574-s016968 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0032-0221-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0506-0578-s014037 | forward | revenue | 3 | pending |
| line-3 | line-3-0506-0578-s014037 | reverse | revenue | 3 | pending |
| line-3 | line-3-0577-0686-s016982 | forward | revenue | 3 | pending |
| line-3 | line-3-0577-0686-s016982 | reverse | revenue | 3 | pending |
| line-3 | line-3-0649-0743-s019230 | forward | revenue | 3 | pending |
| line-3 | line-3-0649-0743-s019230 | reverse | revenue | 3 | pending |
| line-3 | line-3-0748-0813-s022245 | forward | revenue | 3 | pending |
| line-3 | line-3-0748-0813-s022245 | reverse | revenue | 3 | pending |
| line-3 | line-3-0783-0912-s025262 | forward | revenue | 3 | pending |
| line-3 | line-3-0783-0912-s025262 | reverse | revenue | 3 | pending |
| line-3 | line-3-0885-0963-s028262 | forward | revenue | 3 | pending |
| line-3 | line-3-0885-0963-s028262 | reverse | revenue | 3 | pending |
| line-3 | line-3-0932-0996-s030468 | forward | revenue | 3 | pending |
| line-3 | line-3-0932-0996-s030468 | reverse | revenue | 3 | pending |
| line-3 | line-3-0951-1063-s032663 | forward | revenue | 3 | pending |
| line-3 | line-3-0951-1063-s032663 | reverse | revenue | 2 | pending |
| line-3 | line-3-1034-1100-s034857 | reverse | revenue | 2 | pending |
| line-3 | line-3-0951-1063-s032663 | reverse | spare | 1 | pending |
| line-3 | line-3-1034-1100-s034857 | reverse | spare | 1 | pending |
| line-3 | line-3-0032-0221-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0578-s014037 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0578-s014037 | reverse | spare | 1 | pending |
| line-3 | line-3-0577-0686-s016982 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0608-1134-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0676-1129-s002740 | forward | revenue | 3 | pending |
| line-4 | line-4-0676-1129-s002740 | reverse | revenue | 3 | pending |
| line-4 | line-4-0721-1052-s004724 | forward | revenue | 2 | pending |
| line-4 | line-4-0721-1052-s004724 | reverse | revenue | 2 | pending |
| line-4 | line-4-0758-0976-s006726 | forward | revenue | 2 | pending |
| line-4 | line-4-0758-0976-s006726 | reverse | revenue | 2 | pending |
| line-4 | line-4-0876-0917-s009727 | forward | revenue | 2 | pending |
| line-4 | line-4-0876-0917-s009727 | reverse | revenue | 2 | pending |
| line-4 | line-4-0941-0821-s012732 | forward | revenue | 2 | pending |
| line-4 | line-4-0941-0821-s012732 | reverse | revenue | 2 | pending |
| line-4 | line-4-1059-0742-s015746 | forward | revenue | 2 | pending |
| line-4 | line-4-1059-0742-s015746 | reverse | revenue | 2 | pending |
| line-4 | line-4-1237-0628-s020251 | forward | revenue | 2 | pending |
| line-4 | line-4-1237-0628-s020251 | reverse | revenue | 2 | pending |
| line-4 | line-4-1342-0511-s023726 | reverse | revenue | 2 | pending |
| line-4 | line-4-0721-1052-s004724 | forward | spare | 1 | pending |
| line-4 | line-4-0721-1052-s004724 | reverse | spare | 1 | pending |
| line-4 | line-4-0758-0976-s006726 | forward | spare | 1 | pending |
| line-4 | line-4-0758-0976-s006726 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0744-0309-s000000 | forward | revenue | 1 | pending |
| line-5 | line-5-0744-0309-s000000 | reverse | revenue | 1 | pending |
| line-5 | line-5-0641-0409-s003505 | forward | revenue | 1 | pending |
| line-5 | line-5-0641-0409-s003505 | reverse | revenue | 1 | pending |
| line-5 | line-5-0604-0541-s007018 | reverse | revenue | 1 | pending |
| line-5 | line-5-0577-0686-s010159 | forward | revenue | 1 | pending |
| line-5 | line-5-0577-0686-s010159 | reverse | revenue | 1 | pending |
| line-5 | line-5-0488-0843-s014036 | forward | revenue | 1 | pending |
| line-5 | line-5-0433-0985-s017530 | forward | revenue | 1 | pending |
| line-5 | line-5-0433-0985-s017530 | reverse | revenue | 1 | pending |
| line-5 | line-5-0608-1134-s023479 | forward | revenue | 1 | pending |
| line-5 | line-5-0676-1129-s025013 | forward | revenue | 1 | pending |
| line-5 | line-5-0676-1129-s025013 | reverse | revenue | 1 | pending |
| line-5 | line-5-0728-1154-s026724 | forward | revenue | 1 | pending |
| line-5 | line-5-0728-1154-s026724 | reverse | revenue | 1 | pending |
| line-5 | line-5-0781-1188-s028351 | reverse | revenue | 1 | pending |
| line-5 | line-5-1034-1100-s034886 | forward | revenue | 1 | pending |
| line-5 | line-5-1034-1100-s034886 | reverse | revenue | 1 | pending |
| line-5 | line-5-1181-0953-s040744 | reverse | revenue | 1 | pending |
| line-5 | line-5-1237-0628-s051327 | forward | revenue | 1 | pending |
| line-5 | line-5-1237-0628-s051327 | reverse | revenue | 1 | pending |
| line-5 | line-5-1116-0505-s054789 | forward | revenue | 1 | pending |
| line-5 | line-5-1045-0385-s057813 | forward | spare | 1 | pending |
| line-5 | line-5-1045-0385-s057813 | reverse | spare | 1 | pending |
| line-5 | line-5-0907-0389-s060823 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**104 trainsets exceed the reference platform envelope**, requiring **8,840.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0779-1508-s031774 | 2 | 2 | 0 | 0.0 |
| line-1-0782-1167-s024752 | 4 | 4 | 0 | 0.0 |
| line-1-0791-1020-s021737 | 4 | 2 | 2 | 170.0 |
| line-1-0806-0800-s015204 | 4 | 2 | 2 | 170.0 |
| line-1-0858-0707-s012687 | 5 | 2 | 3 | 255.0 |
| line-1-0858-0899-s018729 | 4 | 4 | 0 | 0.0 |
| line-1-0875-0568-s009660 | 6 | 2 | 4 | 340.0 |
| line-1-0884-0147-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0890-0302-s003630 | 6 | 2 | 4 | 340.0 |
| line-1-0898-0389-s005486 | 6 | 4 | 2 | 170.0 |
| line-1-0902-0492-s007579 | 6 | 2 | 4 | 340.0 |
| line-2-0573-0995-s031539 | 3 | 2 | 1 | 85.0 |
| line-2-0703-0794-s026011 | 6 | 2 | 4 | 340.0 |
| line-2-0800-0724-s022985 | 6 | 2 | 4 | 340.0 |
| line-2-0821-0636-s019979 | 6 | 2 | 4 | 340.0 |
| line-2-0908-0574-s016968 | 8 | 2 | 6 | 510.0 |
| line-2-0966-0458-s013954 | 8 | 2 | 6 | 510.0 |
| line-2-1054-0393-s011169 | 8 | 4 | 4 | 340.0 |
| line-2-1343-0019-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0032-0221-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0506-0578-s014037 | 8 | 2 | 6 | 510.0 |
| line-3-0577-0686-s016982 | 7 | 4 | 3 | 255.0 |
| line-3-0649-0743-s019230 | 6 | 2 | 4 | 340.0 |
| line-3-0748-0813-s022245 | 6 | 2 | 4 | 340.0 |
| line-3-0783-0912-s025262 | 6 | 2 | 4 | 340.0 |
| line-3-0885-0963-s028262 | 6 | 2 | 4 | 340.0 |
| line-3-0932-0996-s030468 | 6 | 2 | 4 | 340.0 |
| line-3-0951-1063-s032663 | 6 | 2 | 4 | 340.0 |
| line-3-1034-1100-s034857 | 3 | 2 | 1 | 85.0 |
| line-4-0608-1134-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0676-1129-s002740 | 6 | 4 | 2 | 170.0 |
| line-4-0721-1052-s004724 | 6 | 2 | 4 | 340.0 |
| line-4-0758-0976-s006726 | 6 | 2 | 4 | 340.0 |
| line-4-0876-0917-s009727 | 4 | 4 | 0 | 0.0 |
| line-4-0941-0821-s012732 | 4 | 2 | 2 | 170.0 |
| line-4-1059-0742-s015746 | 4 | 2 | 2 | 170.0 |
| line-4-1237-0628-s020251 | 4 | 4 | 0 | 0.0 |
| line-4-1342-0511-s023726 | 2 | 2 | 0 | 0.0 |
| line-5-0433-0985-s017530 | 2 | 2 | 0 | 0.0 |
| line-5-0488-0843-s014036 | 1 | 2 | 0 | 0.0 |
| line-5-0577-0686-s010159 | 2 | 4 | 0 | 0.0 |
| line-5-0604-0541-s007018 | 1 | 2 | 0 | 0.0 |
| line-5-0608-1134-s023479 | 1 | 4 | 0 | 0.0 |
| line-5-0641-0409-s003505 | 2 | 2 | 0 | 0.0 |
| line-5-0676-1129-s025013 | 2 | 4 | 0 | 0.0 |
| line-5-0728-1154-s026724 | 2 | 2 | 0 | 0.0 |
| line-5-0744-0309-s000000 | 2 | 2 | 0 | 0.0 |
| line-5-0781-1188-s028351 | 1 | 4 | 0 | 0.0 |
| line-5-0907-0389-s060823 | 1 | 4 | 0 | 0.0 |
| line-5-1034-1100-s034886 | 2 | 4 | 0 | 0.0 |
| line-5-1045-0385-s057813 | 2 | 4 | 0 | 0.0 |
| line-5-1116-0505-s054789 | 1 | 2 | 0 | 0.0 |
| line-5-1181-0953-s040744 | 1 | 2 | 0 | 0.0 |
| line-5-1237-0628-s051327 | 2 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Peshawar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
