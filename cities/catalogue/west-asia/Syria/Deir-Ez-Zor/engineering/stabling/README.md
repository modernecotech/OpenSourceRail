# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **143 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **128 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0317-0298-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0427-0403-s003692 | forward | revenue | 6 | pending |
| line-1 | line-1-0427-0403-s003692 | reverse | revenue | 6 | pending |
| line-1 | line-1-0492-0477-s005734 | forward | revenue | 5 | pending |
| line-1 | line-1-0492-0477-s005734 | reverse | revenue | 5 | pending |
| line-1 | line-1-0544-0551-s007781 | forward | revenue | 5 | pending |
| line-1 | line-1-0544-0551-s007781 | reverse | revenue | 5 | pending |
| line-1 | line-1-0664-0635-s011294 | forward | revenue | 5 | pending |
| line-1 | line-1-0664-0635-s011294 | reverse | revenue | 5 | pending |
| line-1 | line-1-0910-0952-s021694 | reverse | revenue | 5 | pending |
| line-1 | line-1-0492-0477-s005734 | forward | spare | 1 | pending |
| line-1 | line-1-0492-0477-s005734 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0551-s007781 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0551-s007781 | reverse | spare | 1 | pending |
| line-1 | line-1-0664-0635-s011294 | forward | spare | 1 | pending |
| line-1 | line-1-0664-0635-s011294 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0173-0684-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0396-0636-s005662 | forward | revenue | 5 | pending |
| line-2 | line-2-0396-0636-s005662 | reverse | revenue | 4 | pending |
| line-2 | line-2-0468-0565-s007690 | forward | revenue | 4 | pending |
| line-2 | line-2-0468-0565-s007690 | reverse | revenue | 4 | pending |
| line-2 | line-2-0544-0551-s009692 | forward | revenue | 4 | pending |
| line-2 | line-2-0544-0551-s009692 | reverse | revenue | 4 | pending |
| line-2 | line-2-0636-0421-s013379 | reverse | revenue | 4 | pending |
| line-2 | line-2-0396-0636-s005662 | reverse | spare | 1 | pending |
| line-2 | line-2-0468-0565-s007690 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0565-s007690 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0551-s009692 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0479-0670-s010030 | forward | revenue | 7 | pending |
| line-3 | line-3-0479-0670-s010030 | reverse | revenue | 7 | pending |
| line-3 | line-3-0544-0551-s013264 | forward | revenue | 7 | pending |
| line-3 | line-3-0544-0551-s013264 | reverse | revenue | 7 | pending |
| line-3 | line-3-0586-0425-s016293 | reverse | revenue | 6 | pending |
| line-3 | line-3-0586-0425-s016293 | reverse | spare | 1 | pending |
| line-3 | line-3-0230-1062-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0479-0670-s010030 | forward | spare | 1 | pending |
| line-3 | line-3-0479-0670-s010030 | reverse | spare | 1 | pending |
| line-3 | line-3-0544-0551-s013264 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0317-0298-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0427-0403-s003692 | 12 | 2 | 10 | 595.0 |
| line-1-0492-0477-s005734 | 12 | 2 | 10 | 595.0 |
| line-1-0544-0551-s007781 | 12 | 4 | 8 | 476.0 |
| line-1-0664-0635-s011294 | 12 | 2 | 10 | 595.0 |
| line-1-0910-0952-s021694 | 5 | 2 | 3 | 178.5 |
| line-2-0173-0684-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0396-0636-s005662 | 10 | 2 | 8 | 476.0 |
| line-2-0468-0565-s007690 | 10 | 2 | 8 | 476.0 |
| line-2-0544-0551-s009692 | 9 | 4 | 5 | 297.5 |
| line-2-0636-0421-s013379 | 4 | 2 | 2 | 119.0 |
| line-3-0230-1062-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0479-0670-s010030 | 16 | 2 | 14 | 833.0 |
| line-3-0544-0551-s013264 | 15 | 4 | 11 | 654.5 |
| line-3-0586-0425-s016293 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Deir-Ez-Zor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
