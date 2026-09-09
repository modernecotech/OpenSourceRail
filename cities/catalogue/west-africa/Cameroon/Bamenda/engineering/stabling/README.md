# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **111 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **100 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0276-1068-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0366-0784-s007010 | forward | revenue | 4 | pending |
| line-1 | line-1-0366-0784-s007010 | reverse | revenue | 3 | pending |
| line-1 | line-1-0469-0714-s010024 | forward | revenue | 3 | pending |
| line-1 | line-1-0469-0714-s010024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0523-0624-s013043 | forward | revenue | 3 | pending |
| line-1 | line-1-0523-0624-s013043 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0558-s014963 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0558-s014963 | reverse | revenue | 3 | pending |
| line-1 | line-1-0483-0470-s017438 | forward | revenue | 3 | pending |
| line-1 | line-1-0483-0470-s017438 | reverse | revenue | 3 | pending |
| line-1 | line-1-0492-0379-s019930 | reverse | revenue | 3 | pending |
| line-1 | line-1-0366-0784-s007010 | reverse | spare | 1 | pending |
| line-1 | line-1-0469-0714-s010024 | forward | spare | 1 | pending |
| line-1 | line-1-0469-0714-s010024 | reverse | spare | 1 | pending |
| line-1 | line-1-0523-0624-s013043 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0719-0761-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0619-0657-s003002 | forward | revenue | 3 | pending |
| line-2 | line-2-0619-0657-s003002 | reverse | revenue | 3 | pending |
| line-2 | line-2-0589-0601-s004968 | forward | revenue | 3 | pending |
| line-2 | line-2-0589-0601-s004968 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0558-s006916 | forward | revenue | 2 | pending |
| line-2 | line-2-0545-0558-s006916 | reverse | revenue | 2 | pending |
| line-2 | line-2-0453-0529-s009037 | forward | revenue | 2 | pending |
| line-2 | line-2-0453-0529-s009037 | reverse | revenue | 2 | pending |
| line-2 | line-2-0440-0416-s011743 | forward | revenue | 2 | pending |
| line-2 | line-2-0440-0416-s011743 | reverse | revenue | 2 | pending |
| line-2 | line-2-0381-0340-s014473 | forward | revenue | 2 | pending |
| line-2 | line-2-0381-0340-s014473 | reverse | revenue | 2 | pending |
| line-2 | line-2-0330-0248-s017181 | reverse | revenue | 2 | pending |
| line-2 | line-2-0545-0558-s006916 | forward | spare | 1 | pending |
| line-2 | line-2-0545-0558-s006916 | reverse | spare | 1 | pending |
| line-2 | line-2-0453-0529-s009037 | forward | spare | 1 | pending |
| line-2 | line-2-0453-0529-s009037 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0132-0345-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0341-0392-s005046 | forward | revenue | 3 | pending |
| line-3 | line-3-0341-0392-s005046 | reverse | revenue | 3 | pending |
| line-3 | line-3-0419-0476-s008048 | forward | revenue | 3 | pending |
| line-3 | line-3-0419-0476-s008048 | reverse | revenue | 3 | pending |
| line-3 | line-3-0487-0570-s011071 | forward | revenue | 3 | pending |
| line-3 | line-3-0487-0570-s011071 | reverse | revenue | 3 | pending |
| line-3 | line-3-0545-0558-s012491 | forward | revenue | 3 | pending |
| line-3 | line-3-0545-0558-s012491 | reverse | revenue | 3 | pending |
| line-3 | line-3-0593-0468-s015402 | reverse | revenue | 2 | pending |
| line-3 | line-3-0593-0468-s015402 | reverse | spare | 1 | pending |
| line-3 | line-3-0132-0345-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0341-0392-s005046 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**63 trainsets exceed the reference platform envelope**, requiring **3,748.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0276-1068-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0366-0784-s007010 | 8 | 2 | 6 | 357.0 |
| line-1-0469-0714-s010024 | 8 | 2 | 6 | 357.0 |
| line-1-0483-0470-s017438 | 6 | 2 | 4 | 238.0 |
| line-1-0492-0379-s019930 | 3 | 2 | 1 | 59.5 |
| line-1-0523-0624-s013043 | 7 | 2 | 5 | 297.5 |
| line-1-0545-0558-s014963 | 6 | 4 | 2 | 119.0 |
| line-2-0330-0248-s017181 | 2 | 2 | 0 | 0.0 |
| line-2-0381-0340-s014473 | 4 | 2 | 2 | 119.0 |
| line-2-0440-0416-s011743 | 4 | 2 | 2 | 119.0 |
| line-2-0453-0529-s009037 | 6 | 2 | 4 | 238.0 |
| line-2-0545-0558-s006916 | 6 | 4 | 2 | 119.0 |
| line-2-0589-0601-s004968 | 6 | 2 | 4 | 238.0 |
| line-2-0619-0657-s003002 | 6 | 2 | 4 | 238.0 |
| line-2-0719-0761-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0132-0345-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0341-0392-s005046 | 7 | 2 | 5 | 297.5 |
| line-3-0419-0476-s008048 | 6 | 2 | 4 | 238.0 |
| line-3-0487-0570-s011071 | 6 | 2 | 4 | 238.0 |
| line-3-0545-0558-s012491 | 6 | 4 | 2 | 119.0 |
| line-3-0593-0468-s015402 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bamenda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
