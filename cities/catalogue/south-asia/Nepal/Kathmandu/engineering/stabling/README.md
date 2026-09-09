# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **244 trainsets at 62 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **218 revenue, 20 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0997-1195-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0810-1042-s005240 | forward | revenue | 4 | pending |
| line-1 | line-1-0810-1042-s005240 | reverse | revenue | 3 | pending |
| line-1 | line-1-0807-0895-s008287 | forward | revenue | 3 | pending |
| line-1 | line-1-0807-0895-s008287 | reverse | revenue | 3 | pending |
| line-1 | line-1-0724-0847-s011262 | forward | revenue | 3 | pending |
| line-1 | line-1-0724-0847-s011262 | reverse | revenue | 3 | pending |
| line-1 | line-1-0624-0807-s014270 | forward | revenue | 3 | pending |
| line-1 | line-1-0624-0807-s014270 | reverse | revenue | 3 | pending |
| line-1 | line-1-0582-0681-s017804 | forward | revenue | 3 | pending |
| line-1 | line-1-0582-0681-s017804 | reverse | revenue | 3 | pending |
| line-1 | line-1-0521-0633-s020292 | forward | revenue | 3 | pending |
| line-1 | line-1-0521-0633-s020292 | reverse | revenue | 3 | pending |
| line-1 | line-1-0432-0583-s023385 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0583-s023385 | reverse | revenue | 3 | pending |
| line-1 | line-1-0141-0110-s037446 | reverse | revenue | 3 | pending |
| line-1 | line-1-0810-1042-s005240 | reverse | spare | 1 | pending |
| line-1 | line-1-0807-0895-s008287 | forward | spare | 1 | pending |
| line-1 | line-1-0807-0895-s008287 | reverse | spare | 1 | pending |
| line-1 | line-1-0724-0847-s011262 | forward | spare | 1 | pending |
| line-1 | line-1-0724-0847-s011262 | reverse | spare | 1 | pending |
| line-1 | line-1-0624-0807-s014270 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1081-0122-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0833-0444-s010174 | forward | revenue | 3 | pending |
| line-2 | line-2-0833-0444-s010174 | reverse | revenue | 3 | pending |
| line-2 | line-2-0816-0501-s011505 | forward | revenue | 3 | pending |
| line-2 | line-2-0816-0501-s011505 | reverse | revenue | 3 | pending |
| line-2 | line-2-0779-0553-s013027 | forward | revenue | 3 | pending |
| line-2 | line-2-0779-0553-s013027 | reverse | revenue | 3 | pending |
| line-2 | line-2-0703-0632-s016046 | forward | revenue | 3 | pending |
| line-2 | line-2-0703-0632-s016046 | reverse | revenue | 2 | pending |
| line-2 | line-2-0668-0728-s019059 | forward | revenue | 2 | pending |
| line-2 | line-2-0668-0728-s019059 | reverse | revenue | 2 | pending |
| line-2 | line-2-0592-0779-s022080 | forward | revenue | 2 | pending |
| line-2 | line-2-0592-0779-s022080 | reverse | revenue | 2 | pending |
| line-2 | line-2-0503-0857-s025093 | forward | revenue | 2 | pending |
| line-2 | line-2-0503-0857-s025093 | reverse | revenue | 2 | pending |
| line-2 | line-2-0445-0975-s028918 | reverse | revenue | 2 | pending |
| line-2 | line-2-0703-0632-s016046 | reverse | spare | 1 | pending |
| line-2 | line-2-0668-0728-s019059 | forward | spare | 1 | pending |
| line-2 | line-2-0668-0728-s019059 | reverse | spare | 1 | pending |
| line-2 | line-2-0592-0779-s022080 | forward | spare | 1 | pending |
| line-2 | line-2-0592-0779-s022080 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0313-0742-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0425-0740-s003005 | forward | revenue | 3 | pending |
| line-3 | line-3-0425-0740-s003005 | reverse | revenue | 2 | pending |
| line-3 | line-3-0523-0684-s006020 | forward | revenue | 2 | pending |
| line-3 | line-3-0523-0684-s006020 | reverse | revenue | 2 | pending |
| line-3 | line-3-0582-0681-s007509 | forward | revenue | 2 | pending |
| line-3 | line-3-0582-0681-s007509 | reverse | revenue | 2 | pending |
| line-3 | line-3-0664-0657-s009526 | forward | revenue | 2 | pending |
| line-3 | line-3-0664-0657-s009526 | reverse | revenue | 2 | pending |
| line-3 | line-3-0739-0693-s011546 | forward | revenue | 2 | pending |
| line-3 | line-3-0739-0693-s011546 | reverse | revenue | 2 | pending |
| line-3 | line-3-0840-0756-s014556 | forward | revenue | 2 | pending |
| line-3 | line-3-0840-0756-s014556 | reverse | revenue | 2 | pending |
| line-3 | line-3-0942-0748-s020218 | reverse | revenue | 2 | pending |
| line-3 | line-3-0425-0740-s003005 | reverse | spare | 1 | pending |
| line-3 | line-3-0523-0684-s006020 | forward | spare | 1 | pending |
| line-3 | line-3-0523-0684-s006020 | reverse | spare | 1 | pending |
| line-3 | line-3-0582-0681-s007509 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0194-0595-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0292-0611-s002511 | forward | revenue | 3 | pending |
| line-4 | line-4-0292-0611-s002511 | reverse | revenue | 2 | pending |
| line-4 | line-4-0382-0592-s004837 | forward | revenue | 2 | pending |
| line-4 | line-4-0382-0592-s004837 | reverse | revenue | 2 | pending |
| line-4 | line-4-0462-0600-s007105 | forward | revenue | 2 | pending |
| line-4 | line-4-0462-0600-s007105 | reverse | revenue | 2 | pending |
| line-4 | line-4-0553-0533-s010301 | forward | revenue | 2 | pending |
| line-4 | line-4-0553-0533-s010301 | reverse | revenue | 2 | pending |
| line-4 | line-4-0683-0500-s013301 | forward | revenue | 2 | pending |
| line-4 | line-4-0683-0500-s013301 | reverse | revenue | 2 | pending |
| line-4 | line-4-0777-0449-s016321 | forward | revenue | 2 | pending |
| line-4 | line-4-0777-0449-s016321 | reverse | revenue | 2 | pending |
| line-4 | line-4-0840-0459-s017787 | forward | revenue | 2 | pending |
| line-4 | line-4-0840-0459-s017787 | reverse | revenue | 2 | pending |
| line-4 | line-4-1094-0420-s023329 | reverse | revenue | 2 | pending |
| line-4 | line-4-0292-0611-s002511 | reverse | spare | 1 | pending |
| line-4 | line-4-0382-0592-s004837 | forward | spare | 1 | pending |
| line-4 | line-4-0382-0592-s004837 | reverse | spare | 1 | pending |
| line-4 | line-4-0462-0600-s007105 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0700-1326-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0647-1030-s007458 | forward | revenue | 3 | pending |
| line-5 | line-5-0647-1030-s007458 | reverse | revenue | 3 | pending |
| line-5 | line-5-0664-0907-s010675 | forward | revenue | 3 | pending |
| line-5 | line-5-0664-0907-s010675 | reverse | revenue | 3 | pending |
| line-5 | line-5-0744-0816-s013686 | forward | revenue | 3 | pending |
| line-5 | line-5-0744-0816-s013686 | reverse | revenue | 3 | pending |
| line-5 | line-5-0736-0683-s016701 | forward | revenue | 3 | pending |
| line-5 | line-5-0736-0683-s016701 | reverse | revenue | 3 | pending |
| line-5 | line-5-0660-0601-s019706 | forward | revenue | 3 | pending |
| line-5 | line-5-0660-0601-s019706 | reverse | revenue | 3 | pending |
| line-5 | line-5-0627-0503-s022712 | forward | revenue | 3 | pending |
| line-5 | line-5-0627-0503-s022712 | reverse | revenue | 3 | pending |
| line-5 | line-5-0693-0359-s026497 | forward | revenue | 2 | pending |
| line-5 | line-5-0693-0359-s026497 | reverse | revenue | 2 | pending |
| line-5 | line-5-0669-0143-s031422 | reverse | revenue | 2 | pending |
| line-5 | line-5-0693-0359-s026497 | forward | spare | 1 | pending |
| line-5 | line-5-0693-0359-s026497 | reverse | spare | 1 | pending |
| line-5 | line-5-0669-0143-s031422 | reverse | spare | 1 | pending |
| line-5 | line-5-0700-1326-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0647-1030-s007458 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0550-0355-s000000 | forward | revenue | 1 | pending |
| line-6 | line-6-0550-0355-s000000 | reverse | revenue | 1 | pending |
| line-6 | line-6-0514-0472-s003007 | reverse | revenue | 1 | pending |
| line-6 | line-6-0459-0522-s005015 | reverse | revenue | 1 | pending |
| line-6 | line-6-0462-0600-s007034 | forward | revenue | 1 | pending |
| line-6 | line-6-0382-0567-s009073 | forward | revenue | 1 | pending |
| line-6 | line-6-0292-0611-s012193 | forward | revenue | 1 | pending |
| line-6 | line-6-0247-0830-s019559 | forward | revenue | 1 | pending |
| line-6 | line-6-0247-0830-s019559 | reverse | revenue | 1 | pending |
| line-6 | line-6-0369-0907-s023056 | reverse | revenue | 1 | pending |
| line-6 | line-6-0445-0975-s025151 | reverse | revenue | 1 | pending |
| line-6 | line-6-0647-1030-s030656 | forward | revenue | 1 | pending |
| line-6 | line-6-0741-0978-s033082 | forward | revenue | 1 | pending |
| line-6 | line-6-0807-0895-s035603 | forward | revenue | 1 | pending |
| line-6 | line-6-0942-0748-s040625 | forward | revenue | 1 | pending |
| line-6 | line-6-0942-0748-s040625 | reverse | revenue | 1 | pending |
| line-6 | line-6-0908-0631-s043858 | reverse | revenue | 1 | pending |
| line-6 | line-6-0837-0518-s047308 | reverse | revenue | 1 | pending |
| line-6 | line-6-0840-0459-s048662 | forward | revenue | 1 | pending |
| line-6 | line-6-0805-0418-s049877 | forward | spare | 1 | pending |
| line-6 | line-6-0693-0359-s052924 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**109 trainsets exceed the reference platform envelope**, requiring **9,265.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0141-0110-s037446 | 3 | 2 | 1 | 85.0 |
| line-1-0432-0583-s023385 | 6 | 2 | 4 | 340.0 |
| line-1-0521-0633-s020292 | 6 | 2 | 4 | 340.0 |
| line-1-0582-0681-s017804 | 6 | 4 | 2 | 170.0 |
| line-1-0624-0807-s014270 | 7 | 2 | 5 | 425.0 |
| line-1-0724-0847-s011262 | 8 | 2 | 6 | 510.0 |
| line-1-0807-0895-s008287 | 8 | 4 | 4 | 340.0 |
| line-1-0810-1042-s005240 | 8 | 2 | 6 | 510.0 |
| line-1-0997-1195-s000000 | 4 | 2 | 2 | 170.0 |
| line-2-0445-0975-s028918 | 2 | 2 | 0 | 0.0 |
| line-2-0503-0857-s025093 | 4 | 2 | 2 | 170.0 |
| line-2-0592-0779-s022080 | 6 | 2 | 4 | 340.0 |
| line-2-0668-0728-s019059 | 6 | 2 | 4 | 340.0 |
| line-2-0703-0632-s016046 | 6 | 2 | 4 | 340.0 |
| line-2-0779-0553-s013027 | 6 | 2 | 4 | 340.0 |
| line-2-0816-0501-s011505 | 6 | 4 | 2 | 170.0 |
| line-2-0833-0444-s010174 | 6 | 4 | 2 | 170.0 |
| line-2-1081-0122-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0313-0742-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0425-0740-s003005 | 6 | 2 | 4 | 340.0 |
| line-3-0523-0684-s006020 | 6 | 2 | 4 | 340.0 |
| line-3-0582-0681-s007509 | 5 | 4 | 1 | 85.0 |
| line-3-0664-0657-s009526 | 4 | 2 | 2 | 170.0 |
| line-3-0739-0693-s011546 | 4 | 4 | 0 | 0.0 |
| line-3-0840-0756-s014556 | 4 | 2 | 2 | 170.0 |
| line-3-0942-0748-s020218 | 2 | 2 | 0 | 0.0 |
| line-4-0194-0595-s000000 | 3 | 2 | 1 | 85.0 |
| line-4-0292-0611-s002511 | 6 | 4 | 2 | 170.0 |
| line-4-0382-0592-s004837 | 6 | 4 | 2 | 170.0 |
| line-4-0462-0600-s007105 | 5 | 4 | 1 | 85.0 |
| line-4-0553-0533-s010301 | 4 | 2 | 2 | 170.0 |
| line-4-0683-0500-s013301 | 4 | 2 | 2 | 170.0 |
| line-4-0777-0449-s016321 | 4 | 2 | 2 | 170.0 |
| line-4-0840-0459-s017787 | 4 | 4 | 0 | 0.0 |
| line-4-1094-0420-s023329 | 2 | 2 | 0 | 0.0 |
| line-5-0627-0503-s022712 | 6 | 2 | 4 | 340.0 |
| line-5-0647-1030-s007458 | 7 | 4 | 3 | 255.0 |
| line-5-0660-0601-s019706 | 6 | 2 | 4 | 340.0 |
| line-5-0664-0907-s010675 | 6 | 2 | 4 | 340.0 |
| line-5-0669-0143-s031422 | 3 | 2 | 1 | 85.0 |
| line-5-0693-0359-s026497 | 6 | 4 | 2 | 170.0 |
| line-5-0700-1326-s000000 | 4 | 2 | 2 | 170.0 |
| line-5-0736-0683-s016701 | 6 | 4 | 2 | 170.0 |
| line-5-0744-0816-s013686 | 6 | 2 | 4 | 340.0 |
| line-6-0247-0830-s019559 | 2 | 2 | 0 | 0.0 |
| line-6-0292-0611-s012193 | 1 | 4 | 0 | 0.0 |
| line-6-0369-0907-s023056 | 1 | 2 | 0 | 0.0 |
| line-6-0382-0567-s009073 | 1 | 4 | 0 | 0.0 |
| line-6-0445-0975-s025151 | 1 | 4 | 0 | 0.0 |
| line-6-0459-0522-s005015 | 1 | 2 | 0 | 0.0 |
| line-6-0462-0600-s007034 | 1 | 4 | 0 | 0.0 |
| line-6-0514-0472-s003007 | 1 | 2 | 0 | 0.0 |
| line-6-0550-0355-s000000 | 2 | 2 | 0 | 0.0 |
| line-6-0647-1030-s030656 | 1 | 4 | 0 | 0.0 |
| line-6-0693-0359-s052924 | 1 | 4 | 0 | 0.0 |
| line-6-0741-0978-s033082 | 1 | 2 | 0 | 0.0 |
| line-6-0805-0418-s049877 | 1 | 2 | 0 | 0.0 |
| line-6-0807-0895-s035603 | 1 | 4 | 0 | 0.0 |
| line-6-0837-0518-s047308 | 1 | 4 | 0 | 0.0 |
| line-6-0840-0459-s048662 | 1 | 4 | 0 | 0.0 |
| line-6-0908-0631-s043858 | 1 | 2 | 0 | 0.0 |
| line-6-0942-0748-s040625 | 2 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Kathmandu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
