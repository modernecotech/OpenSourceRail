# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **171 trainsets at 44 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **153 revenue, 13 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0533-0917-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0579-0961-s001885 | forward | revenue | 2 | pending |
| line-1 | line-1-0579-0961-s001885 | reverse | revenue | 2 | pending |
| line-1 | line-1-0654-0899-s003966 | forward | revenue | 2 | pending |
| line-1 | line-1-0654-0899-s003966 | reverse | revenue | 2 | pending |
| line-1 | line-1-0714-0858-s006041 | forward | revenue | 2 | pending |
| line-1 | line-1-0714-0858-s006041 | reverse | revenue | 2 | pending |
| line-1 | line-1-0774-0861-s007655 | forward | revenue | 2 | pending |
| line-1 | line-1-0774-0861-s007655 | reverse | revenue | 2 | pending |
| line-1 | line-1-0800-0806-s009545 | forward | revenue | 2 | pending |
| line-1 | line-1-0800-0806-s009545 | reverse | revenue | 2 | pending |
| line-1 | line-1-0818-0781-s010868 | forward | revenue | 2 | pending |
| line-1 | line-1-0818-0781-s010868 | reverse | revenue | 2 | pending |
| line-1 | line-1-0858-0684-s013376 | forward | revenue | 2 | pending |
| line-1 | line-1-0858-0684-s013376 | reverse | revenue | 2 | pending |
| line-1 | line-1-0961-0648-s015857 | forward | revenue | 1 | pending |
| line-1 | line-1-0961-0648-s015857 | reverse | revenue | 1 | pending |
| line-1 | line-1-1029-0587-s018366 | reverse | revenue | 1 | pending |
| line-1 | line-1-0961-0648-s015857 | forward | spare | 1 | pending |
| line-1 | line-1-0961-0648-s015857 | reverse | spare | 1 | pending |
| line-1 | line-1-1029-0587-s018366 | reverse | spare | 1 | pending |
| line-1 | line-1-0533-0917-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1498-0986-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-1171-0949-s007002 | forward | revenue | 3 | pending |
| line-2 | line-2-1171-0949-s007002 | reverse | revenue | 3 | pending |
| line-2 | line-2-1004-0863-s012888 | forward | revenue | 3 | pending |
| line-2 | line-2-1004-0863-s012888 | reverse | revenue | 3 | pending |
| line-2 | line-2-0915-0862-s015889 | forward | revenue | 3 | pending |
| line-2 | line-2-0915-0862-s015889 | reverse | revenue | 3 | pending |
| line-2 | line-2-0863-0850-s017663 | forward | revenue | 2 | pending |
| line-2 | line-2-0863-0850-s017663 | reverse | revenue | 2 | pending |
| line-2 | line-2-0800-0806-s019859 | forward | revenue | 2 | pending |
| line-2 | line-2-0800-0806-s019859 | reverse | revenue | 2 | pending |
| line-2 | line-2-0744-0755-s021898 | forward | revenue | 2 | pending |
| line-2 | line-2-0744-0755-s021898 | reverse | revenue | 2 | pending |
| line-2 | line-2-0604-0771-s025618 | forward | revenue | 2 | pending |
| line-2 | line-2-0604-0771-s025618 | reverse | revenue | 2 | pending |
| line-2 | line-2-0485-0794-s028387 | reverse | revenue | 2 | pending |
| line-2 | line-2-0863-0850-s017663 | forward | spare | 1 | pending |
| line-2 | line-2-0863-0850-s017663 | reverse | spare | 1 | pending |
| line-2 | line-2-0800-0806-s019859 | forward | spare | 1 | pending |
| line-2 | line-2-0800-0806-s019859 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0636-0695-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0662-0762-s004008 | forward | revenue | 4 | pending |
| line-3 | line-3-0662-0762-s004008 | reverse | revenue | 3 | pending |
| line-3 | line-3-0680-0846-s006012 | forward | revenue | 3 | pending |
| line-3 | line-3-0680-0846-s006012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0742-0945-s008726 | forward | revenue | 3 | pending |
| line-3 | line-3-0742-0945-s008726 | reverse | revenue | 3 | pending |
| line-3 | line-3-0866-0976-s012031 | forward | revenue | 3 | pending |
| line-3 | line-3-0866-0976-s012031 | reverse | revenue | 3 | pending |
| line-3 | line-3-0988-1075-s015552 | forward | revenue | 3 | pending |
| line-3 | line-3-0988-1075-s015552 | reverse | revenue | 3 | pending |
| line-3 | line-3-1244-1468-s026196 | reverse | revenue | 3 | pending |
| line-3 | line-3-0662-0762-s004008 | reverse | spare | 1 | pending |
| line-3 | line-3-0680-0846-s006012 | forward | spare | 1 | pending |
| line-3 | line-3-0680-0846-s006012 | reverse | spare | 1 | pending |
| line-3 | line-3-0742-0945-s008726 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0480-1452-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0807-1131-s010516 | forward | revenue | 4 | pending |
| line-4 | line-4-0807-1131-s010516 | reverse | revenue | 3 | pending |
| line-4 | line-4-0880-0995-s014032 | forward | revenue | 3 | pending |
| line-4 | line-4-0880-0995-s014032 | reverse | revenue | 3 | pending |
| line-4 | line-4-0948-0876-s017039 | forward | revenue | 3 | pending |
| line-4 | line-4-0948-0876-s017039 | reverse | revenue | 3 | pending |
| line-4 | line-4-0998-0777-s019433 | forward | revenue | 3 | pending |
| line-4 | line-4-0998-0777-s019433 | reverse | revenue | 3 | pending |
| line-4 | line-4-1063-0710-s021853 | reverse | revenue | 3 | pending |
| line-4 | line-4-0807-1131-s010516 | reverse | spare | 1 | pending |
| line-4 | line-4-0880-0995-s014032 | forward | spare | 1 | pending |
| line-4 | line-4-0880-0995-s014032 | reverse | spare | 1 | pending |
| line-4 | line-4-0948-0876-s017039 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0636-0695-s000748 | forward | revenue | 1 | pending |
| line-5 | line-5-0636-0695-s000748 | reverse | revenue | 1 | pending |
| line-5 | line-5-0604-0771-s002566 | reverse | revenue | 1 | pending |
| line-5 | line-5-0533-0917-s006168 | reverse | revenue | 1 | pending |
| line-5 | line-5-0564-0977-s008432 | reverse | revenue | 1 | pending |
| line-5 | line-5-0675-0982-s011060 | reverse | revenue | 1 | pending |
| line-5 | line-5-0755-0931-s014065 | reverse | revenue | 1 | pending |
| line-5 | line-5-0869-0879-s017205 | forward | revenue | 1 | pending |
| line-5 | line-5-0907-0851-s018671 | forward | revenue | 1 | pending |
| line-5 | line-5-0899-0794-s020073 | forward | revenue | 1 | pending |
| line-5 | line-5-0818-0781-s021818 | forward | revenue | 1 | pending |
| line-5 | line-5-0790-0749-s023075 | forward | spare | 1 | pending |
| line-5 | line-5-0696-0675-s026078 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **6,290.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0533-0917-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0579-0961-s001885 | 4 | 4 | 0 | 0.0 |
| line-1-0654-0899-s003966 | 4 | 2 | 2 | 170.0 |
| line-1-0714-0858-s006041 | 4 | 2 | 2 | 170.0 |
| line-1-0774-0861-s007655 | 4 | 2 | 2 | 170.0 |
| line-1-0800-0806-s009545 | 4 | 4 | 0 | 0.0 |
| line-1-0818-0781-s010868 | 4 | 4 | 0 | 0.0 |
| line-1-0858-0684-s013376 | 4 | 2 | 2 | 170.0 |
| line-1-0961-0648-s015857 | 4 | 2 | 2 | 170.0 |
| line-1-1029-0587-s018366 | 2 | 2 | 0 | 0.0 |
| line-2-0485-0794-s028387 | 2 | 2 | 0 | 0.0 |
| line-2-0604-0771-s025618 | 4 | 4 | 0 | 0.0 |
| line-2-0744-0755-s021898 | 4 | 2 | 2 | 170.0 |
| line-2-0800-0806-s019859 | 6 | 4 | 2 | 170.0 |
| line-2-0863-0850-s017663 | 6 | 4 | 2 | 170.0 |
| line-2-0915-0862-s015889 | 6 | 4 | 2 | 170.0 |
| line-2-1004-0863-s012888 | 6 | 2 | 4 | 340.0 |
| line-2-1171-0949-s007002 | 6 | 2 | 4 | 340.0 |
| line-2-1498-0986-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0636-0695-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0662-0762-s004008 | 8 | 2 | 6 | 510.0 |
| line-3-0680-0846-s006012 | 8 | 2 | 6 | 510.0 |
| line-3-0742-0945-s008726 | 7 | 4 | 3 | 255.0 |
| line-3-0866-0976-s012031 | 6 | 4 | 2 | 170.0 |
| line-3-0988-1075-s015552 | 6 | 2 | 4 | 340.0 |
| line-3-1244-1468-s026196 | 3 | 2 | 1 | 85.0 |
| line-4-0480-1452-s000000 | 4 | 2 | 2 | 170.0 |
| line-4-0807-1131-s010516 | 8 | 2 | 6 | 510.0 |
| line-4-0880-0995-s014032 | 8 | 4 | 4 | 340.0 |
| line-4-0948-0876-s017039 | 7 | 2 | 5 | 425.0 |
| line-4-0998-0777-s019433 | 6 | 2 | 4 | 340.0 |
| line-4-1063-0710-s021853 | 3 | 2 | 1 | 85.0 |
| line-5-0533-0917-s006168 | 1 | 4 | 0 | 0.0 |
| line-5-0564-0977-s008432 | 1 | 4 | 0 | 0.0 |
| line-5-0604-0771-s002566 | 1 | 4 | 0 | 0.0 |
| line-5-0636-0695-s000748 | 2 | 4 | 0 | 0.0 |
| line-5-0675-0982-s011060 | 1 | 2 | 0 | 0.0 |
| line-5-0696-0675-s026078 | 1 | 2 | 0 | 0.0 |
| line-5-0755-0931-s014065 | 1 | 4 | 0 | 0.0 |
| line-5-0790-0749-s023075 | 1 | 2 | 0 | 0.0 |
| line-5-0818-0781-s021818 | 1 | 4 | 0 | 0.0 |
| line-5-0869-0879-s017205 | 1 | 4 | 0 | 0.0 |
| line-5-0899-0794-s020073 | 1 | 2 | 0 | 0.0 |
| line-5-0907-0851-s018671 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Benin-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
