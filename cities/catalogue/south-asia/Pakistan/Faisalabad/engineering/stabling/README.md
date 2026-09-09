# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **252 trainsets at 57 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **227 revenue, 19 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0955-0272-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0873-0318-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0873-0318-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0801-0403-s005307 | forward | revenue | 3 | pending |
| line-1 | line-1-0801-0403-s005307 | reverse | revenue | 3 | pending |
| line-1 | line-1-0809-0489-s007631 | forward | revenue | 3 | pending |
| line-1 | line-1-0809-0489-s007631 | reverse | revenue | 3 | pending |
| line-1 | line-1-0770-0531-s009244 | forward | revenue | 3 | pending |
| line-1 | line-1-0770-0531-s009244 | reverse | revenue | 3 | pending |
| line-1 | line-1-0692-0578-s011472 | forward | revenue | 3 | pending |
| line-1 | line-1-0692-0578-s011472 | reverse | revenue | 3 | pending |
| line-1 | line-1-0645-0685-s014660 | forward | revenue | 3 | pending |
| line-1 | line-1-0645-0685-s014660 | reverse | revenue | 3 | pending |
| line-1 | line-1-0657-0810-s018276 | forward | revenue | 2 | pending |
| line-1 | line-1-0657-0810-s018276 | reverse | revenue | 2 | pending |
| line-1 | line-1-0525-0848-s021297 | forward | revenue | 2 | pending |
| line-1 | line-1-0525-0848-s021297 | reverse | revenue | 2 | pending |
| line-1 | line-1-0475-0907-s022892 | forward | revenue | 2 | pending |
| line-1 | line-1-0475-0907-s022892 | reverse | revenue | 2 | pending |
| line-1 | line-1-0297-1294-s032259 | reverse | revenue | 2 | pending |
| line-1 | line-1-0657-0810-s018276 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0810-s018276 | reverse | spare | 1 | pending |
| line-1 | line-1-0525-0848-s021297 | forward | spare | 1 | pending |
| line-1 | line-1-0525-0848-s021297 | reverse | spare | 1 | pending |
| line-1 | line-1-0475-0907-s022892 | forward | spare | 1 | pending |
| line-1 | line-1-0475-0907-s022892 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0495-0853-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0527-0768-s003027 | forward | revenue | 3 | pending |
| line-2 | line-2-0527-0768-s003027 | reverse | revenue | 3 | pending |
| line-2 | line-2-0609-0638-s006307 | forward | revenue | 3 | pending |
| line-2 | line-2-0609-0638-s006307 | reverse | revenue | 3 | pending |
| line-2 | line-2-0583-0556-s009033 | forward | revenue | 3 | pending |
| line-2 | line-2-0583-0556-s009033 | reverse | revenue | 3 | pending |
| line-2 | line-2-0663-0477-s012038 | forward | revenue | 3 | pending |
| line-2 | line-2-0663-0477-s012038 | reverse | revenue | 3 | pending |
| line-2 | line-2-0727-0377-s015058 | forward | revenue | 2 | pending |
| line-2 | line-2-0727-0377-s015058 | reverse | revenue | 2 | pending |
| line-2 | line-2-0746-0316-s016660 | forward | revenue | 2 | pending |
| line-2 | line-2-0746-0316-s016660 | reverse | revenue | 2 | pending |
| line-2 | line-2-0790-0092-s022907 | reverse | revenue | 2 | pending |
| line-2 | line-2-0727-0377-s015058 | forward | spare | 1 | pending |
| line-2 | line-2-0727-0377-s015058 | reverse | spare | 1 | pending |
| line-2 | line-2-0746-0316-s016660 | forward | spare | 1 | pending |
| line-2 | line-2-0746-0316-s016660 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0905-0962-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0863-0829-s003008 | forward | revenue | 3 | pending |
| line-3 | line-3-0863-0829-s003008 | reverse | revenue | 3 | pending |
| line-3 | line-3-0831-0692-s006013 | forward | revenue | 3 | pending |
| line-3 | line-3-0831-0692-s006013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0794-0652-s009034 | forward | revenue | 3 | pending |
| line-3 | line-3-0794-0652-s009034 | reverse | revenue | 3 | pending |
| line-3 | line-3-0759-0536-s012036 | forward | revenue | 3 | pending |
| line-3 | line-3-0759-0536-s012036 | reverse | revenue | 3 | pending |
| line-3 | line-3-0751-0424-s015062 | forward | revenue | 2 | pending |
| line-3 | line-3-0751-0424-s015062 | reverse | revenue | 2 | pending |
| line-3 | line-3-0686-0302-s018497 | forward | revenue | 2 | pending |
| line-3 | line-3-0686-0302-s018497 | reverse | revenue | 2 | pending |
| line-3 | line-3-0600-0121-s023068 | reverse | revenue | 2 | pending |
| line-3 | line-3-0751-0424-s015062 | forward | spare | 1 | pending |
| line-3 | line-3-0751-0424-s015062 | reverse | spare | 1 | pending |
| line-3 | line-3-0686-0302-s018497 | forward | spare | 1 | pending |
| line-3 | line-3-0686-0302-s018497 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0291-0369-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0462-0380-s003911 | forward | revenue | 3 | pending |
| line-4 | line-4-0462-0380-s003911 | reverse | revenue | 3 | pending |
| line-4 | line-4-0549-0466-s006920 | forward | revenue | 3 | pending |
| line-4 | line-4-0549-0466-s006920 | reverse | revenue | 3 | pending |
| line-4 | line-4-0623-0508-s008965 | forward | revenue | 3 | pending |
| line-4 | line-4-0623-0508-s008965 | reverse | revenue | 3 | pending |
| line-4 | line-4-0710-0521-s011018 | forward | revenue | 3 | pending |
| line-4 | line-4-0710-0521-s011018 | reverse | revenue | 3 | pending |
| line-4 | line-4-0788-0539-s012966 | forward | revenue | 2 | pending |
| line-4 | line-4-0788-0539-s012966 | reverse | revenue | 2 | pending |
| line-4 | line-4-0897-0587-s015979 | forward | revenue | 2 | pending |
| line-4 | line-4-0897-0587-s015979 | reverse | revenue | 2 | pending |
| line-4 | line-4-1172-0736-s022796 | reverse | revenue | 2 | pending |
| line-4 | line-4-0788-0539-s012966 | forward | spare | 1 | pending |
| line-4 | line-4-0788-0539-s012966 | reverse | spare | 1 | pending |
| line-4 | line-4-0897-0587-s015979 | forward | spare | 1 | pending |
| line-4 | line-4-0897-0587-s015979 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0403-0615-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0521-0585-s003072 | forward | revenue | 4 | pending |
| line-5 | line-5-0521-0585-s003072 | reverse | revenue | 3 | pending |
| line-5 | line-5-0572-0460-s006087 | forward | revenue | 3 | pending |
| line-5 | line-5-0572-0460-s006087 | reverse | revenue | 3 | pending |
| line-5 | line-5-0679-0391-s009104 | forward | revenue | 3 | pending |
| line-5 | line-5-0679-0391-s009104 | reverse | revenue | 3 | pending |
| line-5 | line-5-0799-0344-s012107 | forward | revenue | 3 | pending |
| line-5 | line-5-0799-0344-s012107 | reverse | revenue | 3 | pending |
| line-5 | line-5-0855-0360-s013359 | forward | revenue | 3 | pending |
| line-5 | line-5-0855-0360-s013359 | reverse | revenue | 3 | pending |
| line-5 | line-5-0933-0346-s015118 | forward | revenue | 3 | pending |
| line-5 | line-5-0933-0346-s015118 | reverse | revenue | 3 | pending |
| line-5 | line-5-1295-0129-s024748 | reverse | revenue | 3 | pending |
| line-5 | line-5-0521-0585-s003072 | reverse | spare | 1 | pending |
| line-5 | line-5-0572-0460-s006087 | forward | spare | 1 | pending |
| line-5 | line-5-0572-0460-s006087 | reverse | spare | 1 | pending |
| line-5 | line-5-0679-0391-s009104 | forward | spare | 1 | pending |
| line-5 | line-5-0679-0391-s009104 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0620-0341-s000000 | forward | revenue | 1 | pending |
| line-6 | line-6-0620-0341-s000000 | reverse | revenue | 1 | pending |
| line-6 | line-6-0589-0388-s002000 | forward | revenue | 1 | pending |
| line-6 | line-6-0512-0434-s004015 | forward | revenue | 1 | pending |
| line-6 | line-6-0512-0434-s004015 | reverse | revenue | 1 | pending |
| line-6 | line-6-0338-0543-s010031 | forward | revenue | 1 | pending |
| line-6 | line-6-0403-0615-s012009 | forward | revenue | 1 | pending |
| line-6 | line-6-0403-0615-s012009 | reverse | revenue | 1 | pending |
| line-6 | line-6-0495-0853-s022657 | forward | revenue | 1 | pending |
| line-6 | line-6-0574-0748-s025494 | forward | revenue | 1 | pending |
| line-6 | line-6-0574-0748-s025494 | reverse | revenue | 1 | pending |
| line-6 | line-6-0635-0632-s028510 | forward | revenue | 1 | pending |
| line-6 | line-6-0728-0501-s032050 | forward | revenue | 1 | pending |
| line-6 | line-6-0728-0501-s032050 | reverse | revenue | 1 | pending |
| line-6 | line-6-0790-0468-s033723 | forward | revenue | 1 | pending |
| line-6 | line-6-0852-0410-s035611 | forward | revenue | 1 | pending |
| line-6 | line-6-0852-0410-s035611 | reverse | revenue | 1 | pending |
| line-6 | line-6-0860-0338-s037495 | forward | revenue | 1 | pending |
| line-6 | line-6-0754-0309-s040589 | forward | revenue | 1 | pending |
| line-6 | line-6-0754-0309-s040589 | reverse | spare | 1 | pending |
| line-6 | line-6-0686-0302-s042262 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**121 trainsets exceed the reference platform envelope**, requiring **14,641.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-1294-s032259 | 2 | 2 | 0 | 0.0 |
| line-1-0475-0907-s022892 | 6 | 2 | 4 | 484.0 |
| line-1-0525-0848-s021297 | 6 | 2 | 4 | 484.0 |
| line-1-0645-0685-s014660 | 6 | 2 | 4 | 484.0 |
| line-1-0657-0810-s018276 | 6 | 2 | 4 | 484.0 |
| line-1-0692-0578-s011472 | 6 | 2 | 4 | 484.0 |
| line-1-0770-0531-s009244 | 6 | 4 | 2 | 242.0 |
| line-1-0801-0403-s005307 | 6 | 2 | 4 | 484.0 |
| line-1-0809-0489-s007631 | 6 | 4 | 2 | 242.0 |
| line-1-0873-0318-s003011 | 6 | 4 | 2 | 242.0 |
| line-1-0955-0272-s000000 | 3 | 2 | 1 | 121.0 |
| line-2-0495-0853-s000000 | 3 | 2 | 1 | 121.0 |
| line-2-0527-0768-s003027 | 6 | 2 | 4 | 484.0 |
| line-2-0583-0556-s009033 | 6 | 2 | 4 | 484.0 |
| line-2-0609-0638-s006307 | 6 | 4 | 2 | 242.0 |
| line-2-0663-0477-s012038 | 6 | 2 | 4 | 484.0 |
| line-2-0727-0377-s015058 | 6 | 2 | 4 | 484.0 |
| line-2-0746-0316-s016660 | 6 | 4 | 2 | 242.0 |
| line-2-0790-0092-s022907 | 2 | 2 | 0 | 0.0 |
| line-3-0600-0121-s023068 | 2 | 2 | 0 | 0.0 |
| line-3-0686-0302-s018497 | 6 | 4 | 2 | 242.0 |
| line-3-0751-0424-s015062 | 6 | 2 | 4 | 484.0 |
| line-3-0759-0536-s012036 | 6 | 4 | 2 | 242.0 |
| line-3-0794-0652-s009034 | 6 | 2 | 4 | 484.0 |
| line-3-0831-0692-s006013 | 6 | 2 | 4 | 484.0 |
| line-3-0863-0829-s003008 | 6 | 2 | 4 | 484.0 |
| line-3-0905-0962-s000000 | 3 | 2 | 1 | 121.0 |
| line-4-0291-0369-s000000 | 3 | 2 | 1 | 121.0 |
| line-4-0462-0380-s003911 | 6 | 2 | 4 | 484.0 |
| line-4-0549-0466-s006920 | 6 | 4 | 2 | 242.0 |
| line-4-0623-0508-s008965 | 6 | 2 | 4 | 484.0 |
| line-4-0710-0521-s011018 | 6 | 4 | 2 | 242.0 |
| line-4-0788-0539-s012966 | 6 | 4 | 2 | 242.0 |
| line-4-0897-0587-s015979 | 6 | 2 | 4 | 484.0 |
| line-4-1172-0736-s022796 | 2 | 2 | 0 | 0.0 |
| line-5-0403-0615-s000000 | 4 | 2 | 2 | 242.0 |
| line-5-0521-0585-s003072 | 8 | 2 | 6 | 726.0 |
| line-5-0572-0460-s006087 | 8 | 4 | 4 | 484.0 |
| line-5-0679-0391-s009104 | 8 | 2 | 6 | 726.0 |
| line-5-0799-0344-s012107 | 6 | 2 | 4 | 484.0 |
| line-5-0855-0360-s013359 | 6 | 4 | 2 | 242.0 |
| line-5-0933-0346-s015118 | 6 | 2 | 4 | 484.0 |
| line-5-1295-0129-s024748 | 3 | 2 | 1 | 121.0 |
| line-6-0338-0543-s010031 | 1 | 2 | 0 | 0.0 |
| line-6-0403-0615-s012009 | 2 | 4 | 0 | 0.0 |
| line-6-0495-0853-s022657 | 1 | 4 | 0 | 0.0 |
| line-6-0512-0434-s004015 | 2 | 2 | 0 | 0.0 |
| line-6-0574-0748-s025494 | 2 | 2 | 0 | 0.0 |
| line-6-0589-0388-s002000 | 1 | 2 | 0 | 0.0 |
| line-6-0620-0341-s000000 | 2 | 2 | 0 | 0.0 |
| line-6-0635-0632-s028510 | 1 | 4 | 0 | 0.0 |
| line-6-0686-0302-s042262 | 1 | 4 | 0 | 0.0 |
| line-6-0728-0501-s032050 | 2 | 4 | 0 | 0.0 |
| line-6-0754-0309-s040589 | 2 | 4 | 0 | 0.0 |
| line-6-0790-0468-s033723 | 1 | 4 | 0 | 0.0 |
| line-6-0852-0410-s035611 | 2 | 2 | 0 | 0.0 |
| line-6-0860-0338-s037495 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Faisalabad/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
