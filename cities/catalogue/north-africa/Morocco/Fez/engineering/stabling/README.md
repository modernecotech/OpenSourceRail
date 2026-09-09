# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **128 trainsets at 44 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **115 revenue, 9 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0551-1076-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0556-1016-s001407 | forward | revenue | 2 | pending |
| line-1 | line-1-0556-1016-s001407 | reverse | revenue | 2 | pending |
| line-1 | line-1-0606-0967-s002895 | forward | revenue | 2 | pending |
| line-1 | line-1-0606-0967-s002895 | reverse | revenue | 2 | pending |
| line-1 | line-1-0669-0904-s006036 | forward | revenue | 2 | pending |
| line-1 | line-1-0669-0904-s006036 | reverse | revenue | 2 | pending |
| line-1 | line-1-0721-0853-s008008 | forward | revenue | 2 | pending |
| line-1 | line-1-0721-0853-s008008 | reverse | revenue | 2 | pending |
| line-1 | line-1-0796-0804-s010001 | forward | revenue | 2 | pending |
| line-1 | line-1-0796-0804-s010001 | reverse | revenue | 2 | pending |
| line-1 | line-1-0820-0748-s012038 | forward | revenue | 2 | pending |
| line-1 | line-1-0820-0748-s012038 | reverse | revenue | 2 | pending |
| line-1 | line-1-0895-0639-s015048 | forward | revenue | 2 | pending |
| line-1 | line-1-0895-0639-s015048 | reverse | revenue | 2 | pending |
| line-1 | line-1-1003-0527-s018698 | forward | revenue | 2 | pending |
| line-1 | line-1-1003-0527-s018698 | reverse | revenue | 2 | pending |
| line-1 | line-1-1061-0404-s022347 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-1076-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0556-1016-s001407 | forward | spare | 1 | pending |
| line-1 | line-1-0556-1016-s001407 | reverse | spare | 1 | pending |
| line-1 | line-1-0606-0967-s002895 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0716-0365-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0686-0532-s003771 | forward | revenue | 2 | pending |
| line-2 | line-2-0686-0532-s003771 | reverse | revenue | 2 | pending |
| line-2 | line-2-0765-0582-s005964 | forward | revenue | 2 | pending |
| line-2 | line-2-0765-0582-s005964 | reverse | revenue | 2 | pending |
| line-2 | line-2-0792-0644-s007901 | forward | revenue | 2 | pending |
| line-2 | line-2-0792-0644-s007901 | reverse | revenue | 2 | pending |
| line-2 | line-2-0723-0698-s009820 | forward | revenue | 2 | pending |
| line-2 | line-2-0723-0698-s009820 | reverse | revenue | 2 | pending |
| line-2 | line-2-0796-0804-s012994 | forward | revenue | 2 | pending |
| line-2 | line-2-0796-0804-s012994 | reverse | revenue | 2 | pending |
| line-2 | line-2-0807-0877-s015012 | forward | revenue | 2 | pending |
| line-2 | line-2-0807-0877-s015012 | reverse | revenue | 2 | pending |
| line-2 | line-2-0883-0957-s017669 | forward | revenue | 2 | pending |
| line-2 | line-2-0883-0957-s017669 | reverse | revenue | 2 | pending |
| line-2 | line-2-0848-1024-s020340 | reverse | revenue | 2 | pending |
| line-2 | line-2-0716-0365-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0686-0532-s003771 | forward | spare | 1 | pending |
| line-2 | line-2-0686-0532-s003771 | reverse | spare | 1 | pending |
| line-2 | line-2-0765-0582-s005964 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0689-1425-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0605-1114-s007017 | forward | revenue | 3 | pending |
| line-3 | line-3-0605-1114-s007017 | reverse | revenue | 3 | pending |
| line-3 | line-3-0607-0967-s010024 | forward | revenue | 3 | pending |
| line-3 | line-3-0607-0967-s010024 | reverse | revenue | 3 | pending |
| line-3 | line-3-0635-0853-s013050 | forward | revenue | 2 | pending |
| line-3 | line-3-0635-0853-s013050 | reverse | revenue | 2 | pending |
| line-3 | line-3-0655-0776-s014889 | forward | revenue | 2 | pending |
| line-3 | line-3-0655-0776-s014889 | reverse | revenue | 2 | pending |
| line-3 | line-3-0679-0683-s017080 | forward | revenue | 2 | pending |
| line-3 | line-3-0679-0683-s017080 | reverse | revenue | 2 | pending |
| line-3 | line-3-0643-0608-s019754 | reverse | revenue | 2 | pending |
| line-3 | line-3-0635-0853-s013050 | forward | spare | 1 | pending |
| line-3 | line-3-0635-0853-s013050 | reverse | spare | 1 | pending |
| line-3 | line-3-0655-0776-s014889 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0643-0608-s001627 | forward | revenue | 1 | pending |
| line-4 | line-4-0643-0608-s001627 | reverse | revenue | 1 | pending |
| line-4 | line-4-0720-0699-s004158 | reverse | revenue | 1 | pending |
| line-4 | line-4-0704-0759-s006021 | reverse | revenue | 1 | pending |
| line-4 | line-4-0655-0776-s007439 | reverse | revenue | 1 | pending |
| line-4 | line-4-0594-0817-s009034 | reverse | revenue | 1 | pending |
| line-4 | line-4-0526-0922-s012040 | forward | revenue | 1 | pending |
| line-4 | line-4-0528-1015-s015124 | forward | revenue | 1 | pending |
| line-4 | line-4-0607-0967-s017473 | forward | revenue | 1 | pending |
| line-4 | line-4-0688-0978-s019284 | forward | revenue | 1 | pending |
| line-4 | line-4-0767-0958-s022304 | forward | revenue | 1 | pending |
| line-4 | line-4-0767-0958-s022304 | reverse | revenue | 1 | pending |
| line-4 | line-4-0848-1024-s024906 | reverse | revenue | 1 | pending |
| line-4 | line-4-0918-0914-s028316 | reverse | revenue | 1 | pending |
| line-4 | line-4-0934-0821-s031320 | reverse | revenue | 1 | pending |
| line-4 | line-4-0840-0741-s034386 | reverse | revenue | 1 | pending |
| line-4 | line-4-0852-0619-s037342 | forward | revenue | 1 | pending |
| line-4 | line-4-0878-0459-s040852 | forward | revenue | 1 | pending |
| line-4 | line-4-0942-0350-s044347 | forward | spare | 1 | pending |
| line-4 | line-4-0686-0532-s051315 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**38 trainsets exceed the reference platform envelope**, requiring **3,230.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0551-1076-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0556-1016-s001407 | 6 | 4 | 2 | 170.0 |
| line-1-0606-0967-s002895 | 5 | 4 | 1 | 85.0 |
| line-1-0669-0904-s006036 | 4 | 2 | 2 | 170.0 |
| line-1-0721-0853-s008008 | 4 | 2 | 2 | 170.0 |
| line-1-0796-0804-s010001 | 4 | 4 | 0 | 0.0 |
| line-1-0820-0748-s012038 | 4 | 4 | 0 | 0.0 |
| line-1-0895-0639-s015048 | 4 | 2 | 2 | 170.0 |
| line-1-1003-0527-s018698 | 4 | 2 | 2 | 170.0 |
| line-1-1061-0404-s022347 | 2 | 2 | 0 | 0.0 |
| line-2-0686-0532-s003771 | 6 | 4 | 2 | 170.0 |
| line-2-0716-0365-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0723-0698-s009820 | 4 | 4 | 0 | 0.0 |
| line-2-0765-0582-s005964 | 5 | 2 | 3 | 255.0 |
| line-2-0792-0644-s007901 | 4 | 2 | 2 | 170.0 |
| line-2-0796-0804-s012994 | 4 | 4 | 0 | 0.0 |
| line-2-0807-0877-s015012 | 4 | 2 | 2 | 170.0 |
| line-2-0848-1024-s020340 | 2 | 2 | 0 | 0.0 |
| line-2-0883-0957-s017669 | 4 | 2 | 2 | 170.0 |
| line-3-0605-1114-s007017 | 6 | 2 | 4 | 340.0 |
| line-3-0607-0967-s010024 | 6 | 4 | 2 | 170.0 |
| line-3-0635-0853-s013050 | 6 | 2 | 4 | 340.0 |
| line-3-0643-0608-s019754 | 2 | 2 | 0 | 0.0 |
| line-3-0655-0776-s014889 | 5 | 4 | 1 | 85.0 |
| line-3-0679-0683-s017080 | 4 | 2 | 2 | 170.0 |
| line-3-0689-1425-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0526-0922-s012040 | 1 | 2 | 0 | 0.0 |
| line-4-0528-1015-s015124 | 1 | 4 | 0 | 0.0 |
| line-4-0594-0817-s009034 | 1 | 2 | 0 | 0.0 |
| line-4-0607-0967-s017473 | 1 | 4 | 0 | 0.0 |
| line-4-0643-0608-s001627 | 2 | 4 | 0 | 0.0 |
| line-4-0655-0776-s007439 | 1 | 4 | 0 | 0.0 |
| line-4-0686-0532-s051315 | 1 | 4 | 0 | 0.0 |
| line-4-0688-0978-s019284 | 1 | 2 | 0 | 0.0 |
| line-4-0704-0759-s006021 | 1 | 2 | 0 | 0.0 |
| line-4-0720-0699-s004158 | 1 | 4 | 0 | 0.0 |
| line-4-0767-0958-s022304 | 2 | 2 | 0 | 0.0 |
| line-4-0840-0741-s034386 | 1 | 4 | 0 | 0.0 |
| line-4-0848-1024-s024906 | 1 | 4 | 0 | 0.0 |
| line-4-0852-0619-s037342 | 1 | 2 | 0 | 0.0 |
| line-4-0878-0459-s040852 | 1 | 2 | 0 | 0.0 |
| line-4-0918-0914-s028316 | 1 | 2 | 0 | 0.0 |
| line-4-0934-0821-s031320 | 1 | 2 | 0 | 0.0 |
| line-4-0942-0350-s044347 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Fez/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
