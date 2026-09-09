# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **358 trainsets at 62 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **323 revenue, 28 spare, 7 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0008-0203-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0649-0615-s017949 | forward | revenue | 5 | pending |
| line-1 | line-1-0649-0615-s017949 | reverse | revenue | 5 | pending |
| line-1 | line-1-0729-0715-s020958 | forward | revenue | 5 | pending |
| line-1 | line-1-0729-0715-s020958 | reverse | revenue | 5 | pending |
| line-1 | line-1-0856-0751-s023958 | forward | revenue | 5 | pending |
| line-1 | line-1-0856-0751-s023958 | reverse | revenue | 5 | pending |
| line-1 | line-1-0926-0838-s026972 | forward | revenue | 5 | pending |
| line-1 | line-1-0926-0838-s026972 | reverse | revenue | 5 | pending |
| line-1 | line-1-1013-0902-s030044 | forward | revenue | 5 | pending |
| line-1 | line-1-1013-0902-s030044 | reverse | revenue | 5 | pending |
| line-1 | line-1-1181-1028-s036275 | forward | revenue | 5 | pending |
| line-1 | line-1-1181-1028-s036275 | reverse | revenue | 5 | pending |
| line-1 | line-1-1395-1093-s041473 | reverse | revenue | 4 | pending |
| line-1 | line-1-1395-1093-s041473 | reverse | spare | 1 | pending |
| line-1 | line-1-0008-0203-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0649-0615-s017949 | forward | spare | 1 | pending |
| line-1 | line-1-0649-0615-s017949 | reverse | spare | 1 | pending |
| line-1 | line-1-0729-0715-s020958 | forward | spare | 1 | pending |
| line-1 | line-1-0729-0715-s020958 | reverse | spare | 1 | pending |
| line-1 | line-1-0856-0751-s023958 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0467-0820-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0579-0833-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0579-0833-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0700-0865-s006024 | forward | revenue | 3 | pending |
| line-2 | line-2-0700-0865-s006024 | reverse | revenue | 3 | pending |
| line-2 | line-2-0790-0920-s008858 | forward | revenue | 3 | pending |
| line-2 | line-2-0790-0920-s008858 | reverse | revenue | 3 | pending |
| line-2 | line-2-0912-0945-s012040 | forward | revenue | 3 | pending |
| line-2 | line-2-0912-0945-s012040 | reverse | revenue | 3 | pending |
| line-2 | line-2-1032-1018-s015057 | forward | revenue | 3 | pending |
| line-2 | line-2-1032-1018-s015057 | reverse | revenue | 3 | pending |
| line-2 | line-2-1220-1138-s020950 | reverse | revenue | 3 | pending |
| line-2 | line-2-0579-0833-s003016 | forward | spare | 1 | pending |
| line-2 | line-2-0579-0833-s003016 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0865-s006024 | forward | spare | 1 | pending |
| line-2 | line-2-0700-0865-s006024 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0547-0553-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0594-0648-s002741 | forward | revenue | 3 | pending |
| line-3 | line-3-0594-0648-s002741 | reverse | revenue | 3 | pending |
| line-3 | line-3-0673-0759-s006662 | forward | revenue | 3 | pending |
| line-3 | line-3-0673-0759-s006662 | reverse | revenue | 3 | pending |
| line-3 | line-3-0752-0843-s009676 | forward | revenue | 3 | pending |
| line-3 | line-3-0752-0843-s009676 | reverse | revenue | 3 | pending |
| line-3 | line-3-0839-0846-s011625 | forward | revenue | 3 | pending |
| line-3 | line-3-0839-0846-s011625 | reverse | revenue | 3 | pending |
| line-3 | line-3-0830-0926-s013562 | forward | revenue | 3 | pending |
| line-3 | line-3-0830-0926-s013562 | reverse | revenue | 3 | pending |
| line-3 | line-3-0867-0996-s015441 | forward | revenue | 3 | pending |
| line-3 | line-3-0867-0996-s015441 | reverse | revenue | 3 | pending |
| line-3 | line-3-0919-1150-s018952 | forward | revenue | 3 | pending |
| line-3 | line-3-0919-1150-s018952 | reverse | revenue | 3 | pending |
| line-3 | line-3-1005-1290-s022465 | forward | revenue | 3 | pending |
| line-3 | line-3-1005-1290-s022465 | reverse | revenue | 3 | pending |
| line-3 | line-3-1262-1632-s032034 | reverse | revenue | 3 | pending |
| line-3 | line-3-0594-0648-s002741 | forward | spare | 1 | pending |
| line-3 | line-3-0594-0648-s002741 | reverse | spare | 1 | pending |
| line-3 | line-3-0673-0759-s006662 | forward | spare | 1 | pending |
| line-3 | line-3-0673-0759-s006662 | reverse | spare | 1 | pending |
| line-3 | line-3-0752-0843-s009676 | forward | spare | 1 | pending |
| line-3 | line-3-0752-0843-s009676 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1254-0792-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-1141-0799-s003016 | forward | revenue | 3 | pending |
| line-4 | line-4-1141-0799-s003016 | reverse | revenue | 3 | pending |
| line-4 | line-4-1002-0826-s006020 | forward | revenue | 3 | pending |
| line-4 | line-4-1002-0826-s006020 | reverse | revenue | 3 | pending |
| line-4 | line-4-0887-0889-s009034 | forward | revenue | 3 | pending |
| line-4 | line-4-0887-0889-s009034 | reverse | revenue | 3 | pending |
| line-4 | line-4-0833-0927-s010558 | forward | revenue | 2 | pending |
| line-4 | line-4-0833-0927-s010558 | reverse | revenue | 2 | pending |
| line-4 | line-4-0782-0963-s012050 | forward | revenue | 2 | pending |
| line-4 | line-4-0782-0963-s012050 | reverse | revenue | 2 | pending |
| line-4 | line-4-0724-0946-s013991 | forward | revenue | 2 | pending |
| line-4 | line-4-0724-0946-s013991 | reverse | revenue | 2 | pending |
| line-4 | line-4-0608-0975-s016686 | forward | revenue | 2 | pending |
| line-4 | line-4-0608-0975-s016686 | reverse | revenue | 2 | pending |
| line-4 | line-4-0508-1008-s019380 | forward | revenue | 2 | pending |
| line-4 | line-4-0508-1008-s019380 | reverse | revenue | 2 | pending |
| line-4 | line-4-0298-1042-s024743 | reverse | revenue | 2 | pending |
| line-4 | line-4-0833-0927-s010558 | forward | spare | 1 | pending |
| line-4 | line-4-0833-0927-s010558 | reverse | spare | 1 | pending |
| line-4 | line-4-0782-0963-s012050 | forward | spare | 1 | pending |
| line-4 | line-4-0782-0963-s012050 | reverse | spare | 1 | pending |
| line-4 | line-4-0724-0946-s013991 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0645-1513-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-0638-1217-s007014 | forward | revenue | 4 | pending |
| line-5 | line-5-0638-1217-s007014 | reverse | revenue | 4 | pending |
| line-5 | line-5-0669-1048-s010651 | forward | revenue | 4 | pending |
| line-5 | line-5-0669-1048-s010651 | reverse | revenue | 4 | pending |
| line-5 | line-5-0722-0917-s014035 | forward | revenue | 4 | pending |
| line-5 | line-5-0722-0917-s014035 | reverse | revenue | 4 | pending |
| line-5 | line-5-0724-0788-s016665 | forward | revenue | 4 | pending |
| line-5 | line-5-0724-0788-s016665 | reverse | revenue | 4 | pending |
| line-5 | line-5-0777-0687-s019675 | forward | revenue | 4 | pending |
| line-5 | line-5-0777-0687-s019675 | reverse | revenue | 4 | pending |
| line-5 | line-5-0853-0510-s024348 | forward | revenue | 4 | pending |
| line-5 | line-5-0853-0510-s024348 | reverse | revenue | 4 | pending |
| line-5 | line-5-0890-0164-s033849 | reverse | revenue | 4 | pending |
| line-5 | line-5-0638-1217-s007014 | forward | spare | 1 | pending |
| line-5 | line-5-0638-1217-s007014 | reverse | spare | 1 | pending |
| line-5 | line-5-0669-1048-s010651 | forward | spare | 1 | pending |
| line-5 | line-5-0669-1048-s010651 | reverse | spare | 1 | pending |
| line-5 | line-5-0722-0917-s014035 | forward | spare | 1 | pending |
| line-5 | line-5-0722-0917-s014035 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0722-0039-s000000 | forward | revenue | 4 | pending |
| line-6 | line-6-0851-0476-s010277 | forward | revenue | 4 | pending |
| line-6 | line-6-0851-0476-s010277 | reverse | revenue | 4 | pending |
| line-6 | line-6-0883-0613-s013960 | forward | revenue | 4 | pending |
| line-6 | line-6-0883-0613-s013960 | reverse | revenue | 4 | pending |
| line-6 | line-6-0938-0724-s016979 | forward | revenue | 4 | pending |
| line-6 | line-6-0938-0724-s016979 | reverse | revenue | 4 | pending |
| line-6 | line-6-0957-0812-s018953 | forward | revenue | 3 | pending |
| line-6 | line-6-0957-0812-s018953 | reverse | revenue | 3 | pending |
| line-6 | line-6-0955-0906-s020944 | reverse | revenue | 3 | pending |
| line-6 | line-6-0957-0812-s018953 | forward | spare | 1 | pending |
| line-6 | line-6-0957-0812-s018953 | reverse | spare | 1 | pending |
| line-6 | line-6-0955-0906-s020944 | reverse | spare | 1 | pending |
| line-6 | line-6-0722-0039-s000000 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-0342-0856-s000000 | forward | revenue | 1 | pending |
| line-7 | line-7-0342-0856-s000000 | reverse | revenue | 1 | pending |
| line-7 | line-7-0468-0916-s007020 | forward | revenue | 1 | pending |
| line-7 | line-7-0468-0916-s007020 | reverse | revenue | 1 | pending |
| line-7 | line-7-0600-0920-s010026 | forward | revenue | 1 | pending |
| line-7 | line-7-0600-0920-s010026 | reverse | revenue | 1 | pending |
| line-7 | line-7-0722-0917-s012888 | forward | revenue | 1 | pending |
| line-7 | line-7-0722-0917-s012888 | reverse | revenue | 1 | pending |
| line-7 | line-7-0790-0920-s014367 | forward | revenue | 1 | pending |
| line-7 | line-7-0790-0920-s014367 | reverse | revenue | 1 | pending |
| line-7 | line-7-0854-0952-s016042 | forward | revenue | 1 | pending |
| line-7 | line-7-0854-0952-s016042 | reverse | revenue | 1 | pending |
| line-7 | line-7-0982-1006-s019050 | forward | revenue | 1 | pending |
| line-7 | line-7-0982-1006-s019050 | reverse | revenue | 1 | pending |
| line-7 | line-7-1099-0999-s022065 | forward | revenue | 1 | pending |
| line-7 | line-7-1099-0999-s022065 | reverse | revenue | 1 | pending |
| line-7 | line-7-1181-1028-s023945 | forward | revenue | 1 | pending |
| line-7 | line-7-1181-1028-s023945 | reverse | revenue | 1 | pending |
| line-7 | line-7-1162-0809-s030285 | forward | revenue | 1 | pending |
| line-7 | line-7-1162-0809-s030285 | reverse | revenue | 1 | pending |
| line-7 | line-7-1086-0578-s036115 | forward | revenue | 1 | pending |
| line-7 | line-7-1086-0578-s036115 | reverse | revenue | 1 | pending |
| line-7 | line-7-0836-0492-s044224 | forward | revenue | 1 | pending |
| line-7 | line-7-0836-0492-s044224 | reverse | revenue | 1 | pending |
| line-7 | line-7-0619-0664-s050784 | forward | revenue | 1 | pending |
| line-7 | line-7-0619-0664-s050784 | reverse | spare | 1 | pending |
| line-7 | line-7-0342-0856-s000000 | forward | spare | 1 | pending |
| line-7 | line-7-0342-0856-s000000 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**214 trainsets exceed the reference platform envelope**, requiring **25,894.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0008-0203-s000000 | 6 | 2 | 4 | 484.0 |
| line-1-0649-0615-s017949 | 12 | 2 | 10 | 1,210.0 |
| line-1-0729-0715-s020958 | 12 | 2 | 10 | 1,210.0 |
| line-1-0856-0751-s023958 | 11 | 2 | 9 | 1,089.0 |
| line-1-0926-0838-s026972 | 10 | 2 | 8 | 968.0 |
| line-1-1013-0902-s030044 | 10 | 2 | 8 | 968.0 |
| line-1-1181-1028-s036275 | 10 | 4 | 6 | 726.0 |
| line-1-1395-1093-s041473 | 5 | 2 | 3 | 363.0 |
| line-2-0467-0820-s000000 | 4 | 2 | 2 | 242.0 |
| line-2-0579-0833-s003016 | 8 | 2 | 6 | 726.0 |
| line-2-0700-0865-s006024 | 8 | 2 | 6 | 726.0 |
| line-2-0790-0920-s008858 | 6 | 4 | 2 | 242.0 |
| line-2-0912-0945-s012040 | 6 | 2 | 4 | 484.0 |
| line-2-1032-1018-s015057 | 6 | 2 | 4 | 484.0 |
| line-2-1220-1138-s020950 | 3 | 2 | 1 | 121.0 |
| line-3-0547-0553-s000000 | 4 | 2 | 2 | 242.0 |
| line-3-0594-0648-s002741 | 8 | 4 | 4 | 484.0 |
| line-3-0673-0759-s006662 | 8 | 2 | 6 | 726.0 |
| line-3-0752-0843-s009676 | 8 | 2 | 6 | 726.0 |
| line-3-0830-0926-s013562 | 6 | 4 | 2 | 242.0 |
| line-3-0839-0846-s011625 | 6 | 2 | 4 | 484.0 |
| line-3-0867-0996-s015441 | 6 | 2 | 4 | 484.0 |
| line-3-0919-1150-s018952 | 6 | 2 | 4 | 484.0 |
| line-3-1005-1290-s022465 | 6 | 2 | 4 | 484.0 |
| line-3-1262-1632-s032034 | 3 | 2 | 1 | 121.0 |
| line-4-0298-1042-s024743 | 2 | 2 | 0 | 0.0 |
| line-4-0508-1008-s019380 | 4 | 2 | 2 | 242.0 |
| line-4-0608-0975-s016686 | 4 | 2 | 2 | 242.0 |
| line-4-0724-0946-s013991 | 5 | 4 | 1 | 121.0 |
| line-4-0782-0963-s012050 | 6 | 2 | 4 | 484.0 |
| line-4-0833-0927-s010558 | 6 | 4 | 2 | 242.0 |
| line-4-0887-0889-s009034 | 6 | 2 | 4 | 484.0 |
| line-4-1002-0826-s006020 | 6 | 2 | 4 | 484.0 |
| line-4-1141-0799-s003016 | 6 | 4 | 2 | 242.0 |
| line-4-1254-0792-s000000 | 3 | 2 | 1 | 121.0 |
| line-5-0638-1217-s007014 | 10 | 2 | 8 | 968.0 |
| line-5-0645-1513-s000000 | 5 | 2 | 3 | 363.0 |
| line-5-0669-1048-s010651 | 10 | 2 | 8 | 968.0 |
| line-5-0722-0917-s014035 | 10 | 4 | 6 | 726.0 |
| line-5-0724-0788-s016665 | 8 | 2 | 6 | 726.0 |
| line-5-0777-0687-s019675 | 8 | 2 | 6 | 726.0 |
| line-5-0853-0510-s024348 | 8 | 4 | 4 | 484.0 |
| line-5-0890-0164-s033849 | 4 | 2 | 2 | 242.0 |
| line-6-0722-0039-s000000 | 5 | 2 | 3 | 363.0 |
| line-6-0851-0476-s010277 | 8 | 4 | 4 | 484.0 |
| line-6-0883-0613-s013960 | 8 | 2 | 6 | 726.0 |
| line-6-0938-0724-s016979 | 8 | 2 | 6 | 726.0 |
| line-6-0955-0906-s020944 | 4 | 2 | 2 | 242.0 |
| line-6-0957-0812-s018953 | 8 | 2 | 6 | 726.0 |
| line-7-0342-0856-s000000 | 4 | 2 | 2 | 242.0 |
| line-7-0468-0916-s007020 | 2 | 2 | 0 | 0.0 |
| line-7-0600-0920-s010026 | 2 | 2 | 0 | 0.0 |
| line-7-0619-0664-s050784 | 2 | 4 | 0 | 0.0 |
| line-7-0722-0917-s012888 | 2 | 4 | 0 | 0.0 |
| line-7-0790-0920-s014367 | 2 | 4 | 0 | 0.0 |
| line-7-0836-0492-s044224 | 2 | 4 | 0 | 0.0 |
| line-7-0854-0952-s016042 | 2 | 2 | 0 | 0.0 |
| line-7-0982-1006-s019050 | 2 | 2 | 0 | 0.0 |
| line-7-1086-0578-s036115 | 2 | 2 | 0 | 0.0 |
| line-7-1099-0999-s022065 | 2 | 2 | 0 | 0.0 |
| line-7-1162-0809-s030285 | 2 | 4 | 0 | 0.0 |
| line-7-1181-1028-s023945 | 2 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Sanaa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
