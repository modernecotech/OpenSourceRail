# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **146 trainsets at 27 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **131 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1016-0841-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0868-0745-s004866 | forward | revenue | 4 | pending |
| line-1 | line-1-0868-0745-s004866 | reverse | revenue | 4 | pending |
| line-1 | line-1-0780-0651-s007886 | forward | revenue | 4 | pending |
| line-1 | line-1-0780-0651-s007886 | reverse | revenue | 4 | pending |
| line-1 | line-1-0680-0558-s010891 | forward | revenue | 4 | pending |
| line-1 | line-1-0680-0558-s010891 | reverse | revenue | 3 | pending |
| line-1 | line-1-0564-0520-s013654 | forward | revenue | 3 | pending |
| line-1 | line-1-0564-0520-s013654 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0416-s016911 | forward | revenue | 3 | pending |
| line-1 | line-1-0543-0416-s016911 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0352-s018915 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0352-s018915 | reverse | revenue | 3 | pending |
| line-1 | line-1-0432-0240-s022459 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0240-s022459 | reverse | revenue | 3 | pending |
| line-1 | line-1-0230-0021-s029341 | reverse | revenue | 3 | pending |
| line-1 | line-1-0680-0558-s010891 | reverse | spare | 1 | pending |
| line-1 | line-1-0564-0520-s013654 | forward | spare | 1 | pending |
| line-1 | line-1-0564-0520-s013654 | reverse | spare | 1 | pending |
| line-1 | line-1-0543-0416-s016911 | forward | spare | 1 | pending |
| line-1 | line-1-0543-0416-s016911 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0352-s018915 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0301-0299-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0360-0341-s002085 | forward | revenue | 3 | pending |
| line-2 | line-2-0360-0341-s002085 | reverse | revenue | 3 | pending |
| line-2 | line-2-0443-0415-s005101 | forward | revenue | 3 | pending |
| line-2 | line-2-0443-0415-s005101 | reverse | revenue | 3 | pending |
| line-2 | line-2-0483-0509-s008121 | forward | revenue | 3 | pending |
| line-2 | line-2-0483-0509-s008121 | reverse | revenue | 3 | pending |
| line-2 | line-2-0564-0520-s010715 | forward | revenue | 3 | pending |
| line-2 | line-2-0564-0520-s010715 | reverse | revenue | 3 | pending |
| line-2 | line-2-0578-0643-s014156 | forward | revenue | 2 | pending |
| line-2 | line-2-0578-0643-s014156 | reverse | revenue | 2 | pending |
| line-2 | line-2-0675-0680-s016402 | forward | revenue | 2 | pending |
| line-2 | line-2-0675-0680-s016402 | reverse | revenue | 2 | pending |
| line-2 | line-2-0728-0757-s018651 | forward | revenue | 2 | pending |
| line-2 | line-2-0728-0757-s018651 | reverse | revenue | 2 | pending |
| line-2 | line-2-0718-0840-s020886 | reverse | revenue | 2 | pending |
| line-2 | line-2-0578-0643-s014156 | forward | spare | 1 | pending |
| line-2 | line-2-0578-0643-s014156 | reverse | spare | 1 | pending |
| line-2 | line-2-0675-0680-s016402 | forward | spare | 1 | pending |
| line-2 | line-2-0675-0680-s016402 | reverse | spare | 1 | pending |
| line-2 | line-2-0728-0757-s018651 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0938-0427-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0837-0439-s003018 | forward | revenue | 3 | pending |
| line-3 | line-3-0837-0439-s003018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0748-0486-s005655 | forward | revenue | 3 | pending |
| line-3 | line-3-0748-0486-s005655 | reverse | revenue | 2 | pending |
| line-3 | line-3-0639-0479-s008673 | forward | revenue | 2 | pending |
| line-3 | line-3-0639-0479-s008673 | reverse | revenue | 2 | pending |
| line-3 | line-3-0564-0520-s010812 | forward | revenue | 2 | pending |
| line-3 | line-3-0564-0520-s010812 | reverse | revenue | 2 | pending |
| line-3 | line-3-0493-0593-s012872 | forward | revenue | 2 | pending |
| line-3 | line-3-0493-0593-s012872 | reverse | revenue | 2 | pending |
| line-3 | line-3-0405-0560-s014922 | forward | revenue | 2 | pending |
| line-3 | line-3-0405-0560-s014922 | reverse | revenue | 2 | pending |
| line-3 | line-3-0315-0530-s016971 | forward | revenue | 2 | pending |
| line-3 | line-3-0315-0530-s016971 | reverse | revenue | 2 | pending |
| line-3 | line-3-0250-0578-s019019 | reverse | revenue | 2 | pending |
| line-3 | line-3-0748-0486-s005655 | reverse | spare | 1 | pending |
| line-3 | line-3-0639-0479-s008673 | forward | spare | 1 | pending |
| line-3 | line-3-0639-0479-s008673 | reverse | spare | 1 | pending |
| line-3 | line-3-0564-0520-s010812 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0230-0021-s029341 | 3 | 2 | 1 | 59.5 |
| line-1-0432-0240-s022459 | 6 | 2 | 4 | 238.0 |
| line-1-0511-0352-s018915 | 7 | 2 | 5 | 297.5 |
| line-1-0543-0416-s016911 | 8 | 2 | 6 | 357.0 |
| line-1-0564-0520-s013654 | 8 | 4 | 4 | 238.0 |
| line-1-0680-0558-s010891 | 8 | 2 | 6 | 357.0 |
| line-1-0780-0651-s007886 | 8 | 2 | 6 | 357.0 |
| line-1-0868-0745-s004866 | 8 | 2 | 6 | 357.0 |
| line-1-1016-0841-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0301-0299-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0360-0341-s002085 | 6 | 2 | 4 | 238.0 |
| line-2-0443-0415-s005101 | 6 | 2 | 4 | 238.0 |
| line-2-0483-0509-s008121 | 6 | 2 | 4 | 238.0 |
| line-2-0564-0520-s010715 | 6 | 4 | 2 | 119.0 |
| line-2-0578-0643-s014156 | 6 | 2 | 4 | 238.0 |
| line-2-0675-0680-s016402 | 6 | 2 | 4 | 238.0 |
| line-2-0718-0840-s020886 | 2 | 2 | 0 | 0.0 |
| line-2-0728-0757-s018651 | 5 | 2 | 3 | 178.5 |
| line-3-0250-0578-s019019 | 2 | 2 | 0 | 0.0 |
| line-3-0315-0530-s016971 | 4 | 2 | 2 | 119.0 |
| line-3-0405-0560-s014922 | 4 | 2 | 2 | 119.0 |
| line-3-0493-0593-s012872 | 4 | 2 | 2 | 119.0 |
| line-3-0564-0520-s010812 | 5 | 4 | 1 | 59.5 |
| line-3-0639-0479-s008673 | 6 | 2 | 4 | 238.0 |
| line-3-0748-0486-s005655 | 6 | 2 | 4 | 238.0 |
| line-3-0837-0439-s003018 | 6 | 2 | 4 | 238.0 |
| line-3-0938-0427-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Buraidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
