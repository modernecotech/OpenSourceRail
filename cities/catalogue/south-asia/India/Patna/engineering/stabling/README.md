# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **215 trainsets at 58 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **192 revenue, 17 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0284-1127-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0311-1047-s003003 | forward | revenue | 3 | pending |
| line-1 | line-1-0311-1047-s003003 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0912-s008307 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0912-s008307 | reverse | revenue | 3 | pending |
| line-1 | line-1-0569-0839-s010248 | forward | revenue | 3 | pending |
| line-1 | line-1-0569-0839-s010248 | reverse | revenue | 3 | pending |
| line-1 | line-1-0577-0746-s012174 | forward | revenue | 2 | pending |
| line-1 | line-1-0577-0746-s012174 | reverse | revenue | 2 | pending |
| line-1 | line-1-0657-0685-s014326 | forward | revenue | 2 | pending |
| line-1 | line-1-0657-0685-s014326 | reverse | revenue | 2 | pending |
| line-1 | line-1-0691-0621-s015987 | forward | revenue | 2 | pending |
| line-1 | line-1-0691-0621-s015987 | reverse | revenue | 2 | pending |
| line-1 | line-1-0681-0572-s017350 | forward | revenue | 2 | pending |
| line-1 | line-1-0681-0572-s017350 | reverse | revenue | 2 | pending |
| line-1 | line-1-0773-0431-s022363 | forward | revenue | 2 | pending |
| line-1 | line-1-0773-0431-s022363 | reverse | revenue | 2 | pending |
| line-1 | line-1-0924-0184-s031034 | reverse | revenue | 2 | pending |
| line-1 | line-1-0577-0746-s012174 | forward | spare | 1 | pending |
| line-1 | line-1-0577-0746-s012174 | reverse | spare | 1 | pending |
| line-1 | line-1-0657-0685-s014326 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0685-s014326 | reverse | spare | 1 | pending |
| line-1 | line-1-0691-0621-s015987 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1044-0888-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0919-0816-s003890 | forward | revenue | 3 | pending |
| line-2 | line-2-0919-0816-s003890 | reverse | revenue | 2 | pending |
| line-2 | line-2-0878-0788-s005198 | forward | revenue | 2 | pending |
| line-2 | line-2-0878-0788-s005198 | reverse | revenue | 2 | pending |
| line-2 | line-2-0737-0801-s008203 | forward | revenue | 2 | pending |
| line-2 | line-2-0737-0801-s008203 | reverse | revenue | 2 | pending |
| line-2 | line-2-0662-0772-s010154 | forward | revenue | 2 | pending |
| line-2 | line-2-0662-0772-s010154 | reverse | revenue | 2 | pending |
| line-2 | line-2-0577-0746-s012103 | forward | revenue | 2 | pending |
| line-2 | line-2-0577-0746-s012103 | reverse | revenue | 2 | pending |
| line-2 | line-2-0489-0686-s014419 | forward | revenue | 2 | pending |
| line-2 | line-2-0489-0686-s014419 | reverse | revenue | 2 | pending |
| line-2 | line-2-0279-0678-s019466 | reverse | revenue | 2 | pending |
| line-2 | line-2-0919-0816-s003890 | reverse | spare | 1 | pending |
| line-2 | line-2-0878-0788-s005198 | forward | spare | 1 | pending |
| line-2 | line-2-0878-0788-s005198 | reverse | spare | 1 | pending |
| line-2 | line-2-0737-0801-s008203 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0260-0786-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0393-0785-s003446 | forward | revenue | 3 | pending |
| line-3 | line-3-0393-0785-s003446 | reverse | revenue | 3 | pending |
| line-3 | line-3-0513-0844-s006453 | forward | revenue | 2 | pending |
| line-3 | line-3-0513-0844-s006453 | reverse | revenue | 2 | pending |
| line-3 | line-3-0647-0882-s009464 | forward | revenue | 2 | pending |
| line-3 | line-3-0647-0882-s009464 | reverse | revenue | 2 | pending |
| line-3 | line-3-0771-1008-s013649 | forward | revenue | 2 | pending |
| line-3 | line-3-0771-1008-s013649 | reverse | revenue | 2 | pending |
| line-3 | line-3-0847-1040-s016529 | forward | revenue | 2 | pending |
| line-3 | line-3-0847-1040-s016529 | reverse | revenue | 2 | pending |
| line-3 | line-3-0903-1037-s017938 | reverse | revenue | 2 | pending |
| line-3 | line-3-0513-0844-s006453 | forward | spare | 1 | pending |
| line-3 | line-3-0513-0844-s006453 | reverse | spare | 1 | pending |
| line-3 | line-3-0647-0882-s009464 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0075-1013-s000000 | forward | revenue | 2 | pending |
| line-4 | line-4-0189-1012-s002587 | forward | revenue | 2 | pending |
| line-4 | line-4-0189-1012-s002587 | reverse | revenue | 2 | pending |
| line-4 | line-4-0292-0933-s005301 | forward | revenue | 2 | pending |
| line-4 | line-4-0292-0933-s005301 | reverse | revenue | 2 | pending |
| line-4 | line-4-0405-0821-s008489 | forward | revenue | 2 | pending |
| line-4 | line-4-0405-0821-s008489 | reverse | revenue | 2 | pending |
| line-4 | line-4-0490-0781-s010520 | forward | revenue | 2 | pending |
| line-4 | line-4-0490-0781-s010520 | reverse | revenue | 2 | pending |
| line-4 | line-4-0577-0746-s012550 | forward | revenue | 2 | pending |
| line-4 | line-4-0577-0746-s012550 | reverse | revenue | 2 | pending |
| line-4 | line-4-0659-0736-s014505 | forward | revenue | 2 | pending |
| line-4 | line-4-0659-0736-s014505 | reverse | revenue | 2 | pending |
| line-4 | line-4-0780-0714-s017520 | forward | revenue | 2 | pending |
| line-4 | line-4-0780-0714-s017520 | reverse | revenue | 2 | pending |
| line-4 | line-4-0901-0653-s020633 | forward | revenue | 2 | pending |
| line-4 | line-4-0901-0653-s020633 | reverse | revenue | 2 | pending |
| line-4 | line-4-0920-0603-s022011 | reverse | revenue | 1 | pending |
| line-4 | line-4-0920-0603-s022011 | reverse | spare | 1 | pending |
| line-4 | line-4-0075-1013-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0189-1012-s002587 | forward | spare | 1 | pending |
| line-4 | line-4-0189-1012-s002587 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0849-0731-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0773-0662-s003010 | forward | revenue | 3 | pending |
| line-5 | line-5-0773-0662-s003010 | reverse | revenue | 3 | pending |
| line-5 | line-5-0754-0585-s004823 | forward | revenue | 3 | pending |
| line-5 | line-5-0754-0585-s004823 | reverse | revenue | 3 | pending |
| line-5 | line-5-0717-0542-s006030 | forward | revenue | 3 | pending |
| line-5 | line-5-0717-0542-s006030 | reverse | revenue | 3 | pending |
| line-5 | line-5-0577-0463-s009531 | forward | revenue | 3 | pending |
| line-5 | line-5-0577-0463-s009531 | reverse | revenue | 3 | pending |
| line-5 | line-5-0447-0414-s013032 | forward | revenue | 3 | pending |
| line-5 | line-5-0447-0414-s013032 | reverse | revenue | 3 | pending |
| line-5 | line-5-0018-0021-s026014 | reverse | revenue | 3 | pending |
| line-5 | line-5-0773-0662-s003010 | forward | spare | 1 | pending |
| line-5 | line-5-0773-0662-s003010 | reverse | spare | 1 | pending |
| line-5 | line-5-0754-0585-s004823 | forward | spare | 1 | pending |
| line-5 | line-5-0754-0585-s004823 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0189-1012-s002618 | forward | revenue | 1 | pending |
| line-6 | line-6-0189-1012-s002618 | reverse | revenue | 1 | pending |
| line-6 | line-6-0301-1055-s005304 | forward | revenue | 1 | pending |
| line-6 | line-6-0429-1121-s008821 | forward | revenue | 1 | pending |
| line-6 | line-6-0429-1121-s008821 | reverse | revenue | 1 | pending |
| line-6 | line-6-0585-1099-s012339 | forward | revenue | 1 | pending |
| line-6 | line-6-0767-1037-s016539 | forward | revenue | 1 | pending |
| line-6 | line-6-0767-1037-s016539 | reverse | revenue | 1 | pending |
| line-6 | line-6-0847-1040-s019430 | reverse | revenue | 1 | pending |
| line-6 | line-6-0913-0934-s022355 | forward | revenue | 1 | pending |
| line-6 | line-6-0913-0934-s022355 | reverse | revenue | 1 | pending |
| line-6 | line-6-0919-0816-s025717 | reverse | revenue | 1 | pending |
| line-6 | line-6-0901-0653-s029249 | forward | revenue | 1 | pending |
| line-6 | line-6-0850-0447-s035378 | forward | revenue | 1 | pending |
| line-6 | line-6-0850-0447-s035378 | reverse | revenue | 1 | pending |
| line-6 | line-6-0754-0584-s039368 | forward | revenue | 1 | pending |
| line-6 | line-6-0691-0621-s040963 | forward | revenue | 1 | pending |
| line-6 | line-6-0691-0621-s040963 | reverse | revenue | 1 | pending |
| line-6 | line-6-0558-0679-s044443 | reverse | revenue | 1 | pending |
| line-6 | line-6-0489-0686-s046063 | forward | revenue | 1 | pending |
| line-6 | line-6-0489-0686-s046063 | reverse | spare | 1 | pending |
| line-6 | line-6-0426-0702-s047456 | reverse | spare | 1 | pending |
| line-6 | line-6-0260-0786-s051542 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**84 trainsets exceed the reference platform envelope**, requiring **7,140.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0284-1127-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0311-1047-s003003 | 6 | 4 | 2 | 170.0 |
| line-1-0511-0912-s008307 | 6 | 2 | 4 | 340.0 |
| line-1-0569-0839-s010248 | 6 | 2 | 4 | 340.0 |
| line-1-0577-0746-s012174 | 6 | 4 | 2 | 170.0 |
| line-1-0657-0685-s014326 | 6 | 2 | 4 | 340.0 |
| line-1-0681-0572-s017350 | 4 | 2 | 2 | 170.0 |
| line-1-0691-0621-s015987 | 5 | 4 | 1 | 85.0 |
| line-1-0773-0431-s022363 | 4 | 2 | 2 | 170.0 |
| line-1-0924-0184-s031034 | 2 | 2 | 0 | 0.0 |
| line-2-0279-0678-s019466 | 2 | 2 | 0 | 0.0 |
| line-2-0489-0686-s014419 | 4 | 4 | 0 | 0.0 |
| line-2-0577-0746-s012103 | 4 | 4 | 0 | 0.0 |
| line-2-0662-0772-s010154 | 4 | 2 | 2 | 170.0 |
| line-2-0737-0801-s008203 | 5 | 2 | 3 | 255.0 |
| line-2-0878-0788-s005198 | 6 | 2 | 4 | 340.0 |
| line-2-0919-0816-s003890 | 6 | 4 | 2 | 170.0 |
| line-2-1044-0888-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0260-0786-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0393-0785-s003446 | 6 | 2 | 4 | 340.0 |
| line-3-0513-0844-s006453 | 6 | 2 | 4 | 340.0 |
| line-3-0647-0882-s009464 | 5 | 2 | 3 | 255.0 |
| line-3-0771-1008-s013649 | 4 | 4 | 0 | 0.0 |
| line-3-0847-1040-s016529 | 4 | 4 | 0 | 0.0 |
| line-3-0903-1037-s017938 | 2 | 2 | 0 | 0.0 |
| line-4-0075-1013-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0189-1012-s002587 | 6 | 4 | 2 | 170.0 |
| line-4-0292-0933-s005301 | 4 | 2 | 2 | 170.0 |
| line-4-0405-0821-s008489 | 4 | 2 | 2 | 170.0 |
| line-4-0490-0781-s010520 | 4 | 2 | 2 | 170.0 |
| line-4-0577-0746-s012550 | 4 | 4 | 0 | 0.0 |
| line-4-0659-0736-s014505 | 4 | 2 | 2 | 170.0 |
| line-4-0780-0714-s017520 | 4 | 2 | 2 | 170.0 |
| line-4-0901-0653-s020633 | 4 | 4 | 0 | 0.0 |
| line-4-0920-0603-s022011 | 2 | 2 | 0 | 0.0 |
| line-5-0018-0021-s026014 | 3 | 2 | 1 | 85.0 |
| line-5-0447-0414-s013032 | 6 | 2 | 4 | 340.0 |
| line-5-0577-0463-s009531 | 6 | 2 | 4 | 340.0 |
| line-5-0717-0542-s006030 | 6 | 2 | 4 | 340.0 |
| line-5-0754-0585-s004823 | 8 | 4 | 4 | 340.0 |
| line-5-0773-0662-s003010 | 8 | 2 | 6 | 510.0 |
| line-5-0849-0731-s000000 | 4 | 2 | 2 | 170.0 |
| line-6-0189-1012-s002618 | 2 | 4 | 0 | 0.0 |
| line-6-0260-0786-s051542 | 1 | 4 | 0 | 0.0 |
| line-6-0301-1055-s005304 | 1 | 4 | 0 | 0.0 |
| line-6-0426-0702-s047456 | 1 | 2 | 0 | 0.0 |
| line-6-0429-1121-s008821 | 2 | 2 | 0 | 0.0 |
| line-6-0489-0686-s046063 | 2 | 4 | 0 | 0.0 |
| line-6-0558-0679-s044443 | 1 | 2 | 0 | 0.0 |
| line-6-0585-1099-s012339 | 1 | 2 | 0 | 0.0 |
| line-6-0691-0621-s040963 | 2 | 4 | 0 | 0.0 |
| line-6-0754-0584-s039368 | 1 | 4 | 0 | 0.0 |
| line-6-0767-1037-s016539 | 2 | 4 | 0 | 0.0 |
| line-6-0847-1040-s019430 | 1 | 4 | 0 | 0.0 |
| line-6-0850-0447-s035378 | 2 | 2 | 0 | 0.0 |
| line-6-0901-0653-s029249 | 1 | 4 | 0 | 0.0 |
| line-6-0913-0934-s022355 | 2 | 2 | 0 | 0.0 |
| line-6-0919-0816-s025717 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/India/Patna/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
