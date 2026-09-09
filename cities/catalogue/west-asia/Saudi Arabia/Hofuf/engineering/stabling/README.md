# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **163 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0104-0286-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0305-0364-s005618 | forward | revenue | 4 | pending |
| line-1 | line-1-0305-0364-s005618 | reverse | revenue | 4 | pending |
| line-1 | line-1-0379-0503-s009613 | forward | revenue | 4 | pending |
| line-1 | line-1-0379-0503-s009613 | reverse | revenue | 4 | pending |
| line-1 | line-1-0515-0501-s012617 | forward | revenue | 4 | pending |
| line-1 | line-1-0515-0501-s012617 | reverse | revenue | 3 | pending |
| line-1 | line-1-0574-0569-s015014 | forward | revenue | 3 | pending |
| line-1 | line-1-0574-0569-s015014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0721-0594-s018645 | forward | revenue | 3 | pending |
| line-1 | line-1-0721-0594-s018645 | reverse | revenue | 3 | pending |
| line-1 | line-1-0853-0624-s021649 | forward | revenue | 3 | pending |
| line-1 | line-1-0853-0624-s021649 | reverse | revenue | 3 | pending |
| line-1 | line-1-1021-0661-s025878 | reverse | revenue | 3 | pending |
| line-1 | line-1-0515-0501-s012617 | reverse | spare | 1 | pending |
| line-1 | line-1-0574-0569-s015014 | forward | spare | 1 | pending |
| line-1 | line-1-0574-0569-s015014 | reverse | spare | 1 | pending |
| line-1 | line-1-0721-0594-s018645 | forward | spare | 1 | pending |
| line-1 | line-1-0721-0594-s018645 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0988-0288-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0913-0374-s003000 | forward | revenue | 4 | pending |
| line-2 | line-2-0913-0374-s003000 | reverse | revenue | 4 | pending |
| line-2 | line-2-0819-0457-s006006 | forward | revenue | 4 | pending |
| line-2 | line-2-0819-0457-s006006 | reverse | revenue | 3 | pending |
| line-2 | line-2-0693-0479-s008977 | forward | revenue | 3 | pending |
| line-2 | line-2-0693-0479-s008977 | reverse | revenue | 3 | pending |
| line-2 | line-2-0615-0536-s011979 | forward | revenue | 3 | pending |
| line-2 | line-2-0615-0536-s011979 | reverse | revenue | 3 | pending |
| line-2 | line-2-0574-0569-s013483 | forward | revenue | 3 | pending |
| line-2 | line-2-0574-0569-s013483 | reverse | revenue | 3 | pending |
| line-2 | line-2-0564-0626-s014989 | forward | revenue | 3 | pending |
| line-2 | line-2-0564-0626-s014989 | reverse | revenue | 3 | pending |
| line-2 | line-2-0422-0895-s021874 | forward | revenue | 3 | pending |
| line-2 | line-2-0422-0895-s021874 | reverse | revenue | 3 | pending |
| line-2 | line-2-0316-1070-s026721 | reverse | revenue | 3 | pending |
| line-2 | line-2-0819-0457-s006006 | reverse | spare | 1 | pending |
| line-2 | line-2-0693-0479-s008977 | forward | spare | 1 | pending |
| line-2 | line-2-0693-0479-s008977 | reverse | spare | 1 | pending |
| line-2 | line-2-0615-0536-s011979 | forward | spare | 1 | pending |
| line-2 | line-2-0615-0536-s011979 | reverse | spare | 1 | pending |
| line-2 | line-2-0574-0569-s013483 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0018-0425-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0198-0475-s004769 | forward | revenue | 3 | pending |
| line-3 | line-3-0198-0475-s004769 | reverse | revenue | 3 | pending |
| line-3 | line-3-0311-0521-s007788 | forward | revenue | 3 | pending |
| line-3 | line-3-0311-0521-s007788 | reverse | revenue | 3 | pending |
| line-3 | line-3-0415-0548-s010795 | forward | revenue | 3 | pending |
| line-3 | line-3-0415-0548-s010795 | reverse | revenue | 3 | pending |
| line-3 | line-3-0495-0577-s012795 | forward | revenue | 3 | pending |
| line-3 | line-3-0495-0577-s012795 | reverse | revenue | 3 | pending |
| line-3 | line-3-0574-0569-s014772 | forward | revenue | 3 | pending |
| line-3 | line-3-0574-0569-s014772 | reverse | revenue | 3 | pending |
| line-3 | line-3-0630-0614-s016810 | forward | revenue | 3 | pending |
| line-3 | line-3-0630-0614-s016810 | reverse | revenue | 3 | pending |
| line-3 | line-3-0741-0678-s019835 | forward | revenue | 3 | pending |
| line-3 | line-3-0741-0678-s019835 | reverse | revenue | 3 | pending |
| line-3 | line-3-0973-0739-s025254 | reverse | revenue | 2 | pending |
| line-3 | line-3-0973-0739-s025254 | reverse | spare | 1 | pending |
| line-3 | line-3-0018-0425-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0198-0475-s004769 | forward | spare | 1 | pending |
| line-3 | line-3-0198-0475-s004769 | reverse | spare | 1 | pending |
| line-3 | line-3-0311-0521-s007788 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**105 trainsets exceed the reference platform envelope**, requiring **6,247.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0104-0286-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0305-0364-s005618 | 8 | 2 | 6 | 357.0 |
| line-1-0379-0503-s009613 | 8 | 2 | 6 | 357.0 |
| line-1-0515-0501-s012617 | 8 | 2 | 6 | 357.0 |
| line-1-0574-0569-s015014 | 8 | 4 | 4 | 238.0 |
| line-1-0721-0594-s018645 | 8 | 2 | 6 | 357.0 |
| line-1-0853-0624-s021649 | 6 | 2 | 4 | 238.0 |
| line-1-1021-0661-s025878 | 3 | 2 | 1 | 59.5 |
| line-2-0316-1070-s026721 | 3 | 2 | 1 | 59.5 |
| line-2-0422-0895-s021874 | 6 | 2 | 4 | 238.0 |
| line-2-0564-0626-s014989 | 6 | 2 | 4 | 238.0 |
| line-2-0574-0569-s013483 | 7 | 4 | 3 | 178.5 |
| line-2-0615-0536-s011979 | 8 | 2 | 6 | 357.0 |
| line-2-0693-0479-s008977 | 8 | 2 | 6 | 357.0 |
| line-2-0819-0457-s006006 | 8 | 2 | 6 | 357.0 |
| line-2-0913-0374-s003000 | 8 | 2 | 6 | 357.0 |
| line-2-0988-0288-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0018-0425-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0198-0475-s004769 | 8 | 2 | 6 | 357.0 |
| line-3-0311-0521-s007788 | 7 | 2 | 5 | 297.5 |
| line-3-0415-0548-s010795 | 6 | 2 | 4 | 238.0 |
| line-3-0495-0577-s012795 | 6 | 2 | 4 | 238.0 |
| line-3-0574-0569-s014772 | 6 | 4 | 2 | 119.0 |
| line-3-0630-0614-s016810 | 6 | 2 | 4 | 238.0 |
| line-3-0741-0678-s019835 | 6 | 2 | 4 | 238.0 |
| line-3-0973-0739-s025254 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Hofuf/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
