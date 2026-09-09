# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **163 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0104-0286-s000000 | forward | 4 | pending |
| line-1 | line-1-0305-0364-s005618 | forward | 4 | pending |
| line-1 | line-1-0305-0364-s005618 | reverse | 4 | pending |
| line-1 | line-1-0379-0503-s009613 | forward | 4 | pending |
| line-1 | line-1-0379-0503-s009613 | reverse | 4 | pending |
| line-1 | line-1-0515-0501-s012617 | forward | 4 | pending |
| line-1 | line-1-0515-0501-s012617 | reverse | 4 | pending |
| line-1 | line-1-0574-0569-s015014 | forward | 4 | pending |
| line-1 | line-1-0574-0569-s015014 | reverse | 4 | pending |
| line-1 | line-1-0721-0594-s018645 | forward | 4 | pending |
| line-1 | line-1-0721-0594-s018645 | reverse | 4 | pending |
| line-1 | line-1-0853-0624-s021649 | forward | 3 | pending |
| line-1 | line-1-0853-0624-s021649 | reverse | 3 | pending |
| line-1 | line-1-1021-0661-s025878 | reverse | 3 | pending |
| line-2 | line-2-0988-0288-s000000 | forward | 4 | pending |
| line-2 | line-2-0913-0374-s003000 | forward | 4 | pending |
| line-2 | line-2-0913-0374-s003000 | reverse | 4 | pending |
| line-2 | line-2-0819-0457-s006006 | forward | 4 | pending |
| line-2 | line-2-0819-0457-s006006 | reverse | 4 | pending |
| line-2 | line-2-0693-0479-s008977 | forward | 4 | pending |
| line-2 | line-2-0693-0479-s008977 | reverse | 4 | pending |
| line-2 | line-2-0615-0536-s011979 | forward | 4 | pending |
| line-2 | line-2-0615-0536-s011979 | reverse | 4 | pending |
| line-2 | line-2-0574-0569-s013483 | forward | 4 | pending |
| line-2 | line-2-0574-0569-s013483 | reverse | 3 | pending |
| line-2 | line-2-0564-0626-s014989 | forward | 3 | pending |
| line-2 | line-2-0564-0626-s014989 | reverse | 3 | pending |
| line-2 | line-2-0422-0895-s021874 | forward | 3 | pending |
| line-2 | line-2-0422-0895-s021874 | reverse | 3 | pending |
| line-2 | line-2-0316-1070-s026721 | reverse | 3 | pending |
| line-3 | line-3-0018-0425-s000000 | forward | 4 | pending |
| line-3 | line-3-0198-0475-s004769 | forward | 4 | pending |
| line-3 | line-3-0198-0475-s004769 | reverse | 4 | pending |
| line-3 | line-3-0311-0521-s007788 | forward | 4 | pending |
| line-3 | line-3-0311-0521-s007788 | reverse | 3 | pending |
| line-3 | line-3-0415-0548-s010795 | forward | 3 | pending |
| line-3 | line-3-0415-0548-s010795 | reverse | 3 | pending |
| line-3 | line-3-0495-0577-s012795 | forward | 3 | pending |
| line-3 | line-3-0495-0577-s012795 | reverse | 3 | pending |
| line-3 | line-3-0574-0569-s014772 | forward | 3 | pending |
| line-3 | line-3-0574-0569-s014772 | reverse | 3 | pending |
| line-3 | line-3-0630-0614-s016810 | forward | 3 | pending |
| line-3 | line-3-0630-0614-s016810 | reverse | 3 | pending |
| line-3 | line-3-0741-0678-s019835 | forward | 3 | pending |
| line-3 | line-3-0741-0678-s019835 | reverse | 3 | pending |
| line-3 | line-3-0973-0739-s025254 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Hofuf/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
