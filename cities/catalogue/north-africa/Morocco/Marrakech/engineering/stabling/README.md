# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **255 trainsets at 46 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **229 revenue, 20 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0666-0472-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0721-0519-s001640 | forward | revenue | 4 | pending |
| line-1 | line-1-0721-0519-s001640 | reverse | revenue | 3 | pending |
| line-1 | line-1-0806-0577-s004001 | forward | revenue | 3 | pending |
| line-1 | line-1-0806-0577-s004001 | reverse | revenue | 3 | pending |
| line-1 | line-1-0812-0702-s007025 | forward | revenue | 3 | pending |
| line-1 | line-1-0812-0702-s007025 | reverse | revenue | 3 | pending |
| line-1 | line-1-0934-0766-s010042 | forward | revenue | 3 | pending |
| line-1 | line-1-0934-0766-s010042 | reverse | revenue | 3 | pending |
| line-1 | line-1-0957-0873-s013056 | forward | revenue | 3 | pending |
| line-1 | line-1-0957-0873-s013056 | reverse | revenue | 3 | pending |
| line-1 | line-1-1016-1010-s016558 | forward | revenue | 3 | pending |
| line-1 | line-1-1016-1010-s016558 | reverse | revenue | 3 | pending |
| line-1 | line-1-1414-1431-s029160 | reverse | revenue | 3 | pending |
| line-1 | line-1-0721-0519-s001640 | reverse | spare | 1 | pending |
| line-1 | line-1-0806-0577-s004001 | forward | spare | 1 | pending |
| line-1 | line-1-0806-0577-s004001 | reverse | spare | 1 | pending |
| line-1 | line-1-0812-0702-s007025 | forward | spare | 1 | pending |
| line-1 | line-1-0812-0702-s007025 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0176-1241-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0412-0971-s008163 | forward | revenue | 3 | pending |
| line-2 | line-2-0412-0971-s008163 | reverse | revenue | 3 | pending |
| line-2 | line-2-0632-0850-s014020 | forward | revenue | 3 | pending |
| line-2 | line-2-0632-0850-s014020 | reverse | revenue | 3 | pending |
| line-2 | line-2-0709-0814-s016056 | forward | revenue | 3 | pending |
| line-2 | line-2-0709-0814-s016056 | reverse | revenue | 3 | pending |
| line-2 | line-2-0739-0727-s018092 | forward | revenue | 3 | pending |
| line-2 | line-2-0739-0727-s018092 | reverse | revenue | 3 | pending |
| line-2 | line-2-0810-0681-s020024 | forward | revenue | 3 | pending |
| line-2 | line-2-0810-0681-s020024 | reverse | revenue | 3 | pending |
| line-2 | line-2-0927-0656-s023607 | forward | revenue | 3 | pending |
| line-2 | line-2-0927-0656-s023607 | reverse | revenue | 3 | pending |
| line-2 | line-2-0992-0531-s027205 | reverse | revenue | 2 | pending |
| line-2 | line-2-0992-0531-s027205 | reverse | spare | 1 | pending |
| line-2 | line-2-0176-1241-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0412-0971-s008163 | forward | spare | 1 | pending |
| line-2 | line-2-0412-0971-s008163 | reverse | spare | 1 | pending |
| line-2 | line-2-0632-0850-s014020 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0821-0410-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0812-0515-s006009 | forward | revenue | 3 | pending |
| line-3 | line-3-0812-0515-s006009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0835-0594-s007859 | forward | revenue | 3 | pending |
| line-3 | line-3-0835-0594-s007859 | reverse | revenue | 3 | pending |
| line-3 | line-3-0812-0726-s010872 | forward | revenue | 3 | pending |
| line-3 | line-3-0812-0726-s010872 | reverse | revenue | 3 | pending |
| line-3 | line-3-0802-0796-s012808 | forward | revenue | 3 | pending |
| line-3 | line-3-0802-0796-s012808 | reverse | revenue | 3 | pending |
| line-3 | line-3-0699-1073-s019487 | forward | revenue | 3 | pending |
| line-3 | line-3-0699-1073-s019487 | reverse | revenue | 3 | pending |
| line-3 | line-3-0712-1395-s026429 | reverse | revenue | 3 | pending |
| line-3 | line-3-0812-0515-s006009 | forward | spare | 1 | pending |
| line-3 | line-3-0812-0515-s006009 | reverse | spare | 1 | pending |
| line-3 | line-3-0835-0594-s007859 | forward | spare | 1 | pending |
| line-3 | line-3-0835-0594-s007859 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-1429-0421-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0997-0632-s010703 | forward | revenue | 4 | pending |
| line-4 | line-4-0997-0632-s010703 | reverse | revenue | 4 | pending |
| line-4 | line-4-0853-0615-s014296 | forward | revenue | 4 | pending |
| line-4 | line-4-0853-0615-s014296 | reverse | revenue | 4 | pending |
| line-4 | line-4-0729-0623-s017088 | forward | revenue | 4 | pending |
| line-4 | line-4-0729-0623-s017088 | reverse | revenue | 4 | pending |
| line-4 | line-4-0615-0673-s020318 | forward | revenue | 4 | pending |
| line-4 | line-4-0615-0673-s020318 | reverse | revenue | 4 | pending |
| line-4 | line-4-0365-0834-s027223 | reverse | revenue | 4 | pending |
| line-4 | line-4-1429-0421-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0997-0632-s010703 | forward | spare | 1 | pending |
| line-4 | line-4-0997-0632-s010703 | reverse | spare | 1 | pending |
| line-4 | line-4-0853-0615-s014296 | forward | spare | 1 | pending |
| line-4 | line-4-0853-0615-s014296 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-1330-0747-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-1054-0656-s007010 | forward | revenue | 5 | pending |
| line-5 | line-5-1054-0656-s007010 | reverse | revenue | 5 | pending |
| line-5 | line-5-0952-0575-s010540 | forward | revenue | 5 | pending |
| line-5 | line-5-0952-0575-s010540 | reverse | revenue | 5 | pending |
| line-5 | line-5-0840-0496-s014043 | forward | revenue | 5 | pending |
| line-5 | line-5-0840-0496-s014043 | reverse | revenue | 5 | pending |
| line-5 | line-5-0630-0432-s020384 | forward | revenue | 5 | pending |
| line-5 | line-5-0630-0432-s020384 | reverse | revenue | 5 | pending |
| line-5 | line-5-0102-0195-s034036 | reverse | revenue | 4 | pending |
| line-5 | line-5-0102-0195-s034036 | reverse | spare | 1 | pending |
| line-5 | line-5-1330-0747-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-1054-0656-s007010 | forward | spare | 1 | pending |
| line-5 | line-5-1054-0656-s007010 | reverse | spare | 1 | pending |
| line-5 | line-5-0952-0575-s010540 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0721-0519-s002704 | forward | revenue | 1 | pending |
| line-6 | line-6-0721-0519-s002704 | reverse | revenue | 1 | pending |
| line-6 | line-6-0528-0572-s007003 | forward | revenue | 1 | pending |
| line-6 | line-6-0528-0572-s007003 | reverse | revenue | 1 | pending |
| line-6 | line-6-0365-0834-s016576 | forward | revenue | 1 | pending |
| line-6 | line-6-0365-0834-s016576 | reverse | revenue | 1 | pending |
| line-6 | line-6-0413-0965-s021009 | forward | revenue | 1 | pending |
| line-6 | line-6-0413-0965-s021009 | reverse | revenue | 1 | pending |
| line-6 | line-6-0563-0757-s027406 | forward | revenue | 1 | pending |
| line-6 | line-6-0563-0757-s027406 | reverse | revenue | 1 | pending |
| line-6 | line-6-0661-0759-s029614 | reverse | revenue | 1 | pending |
| line-6 | line-6-0723-0703-s031814 | forward | revenue | 1 | pending |
| line-6 | line-6-0723-0703-s031814 | reverse | revenue | 1 | pending |
| line-6 | line-6-0728-0635-s033426 | forward | revenue | 1 | pending |
| line-6 | line-6-0728-0635-s033426 | reverse | revenue | 1 | pending |
| line-6 | line-6-0766-0564-s035675 | forward | revenue | 1 | pending |
| line-6 | line-6-0766-0564-s035675 | reverse | revenue | 1 | pending |
| line-6 | line-6-0840-0496-s037934 | forward | revenue | 1 | pending |
| line-6 | line-6-0840-0496-s037934 | reverse | spare | 1 | pending |
| line-6 | line-6-0821-0410-s048793 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**141 trainsets exceed the reference platform envelope**, requiring **11,985.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0666-0472-s000000 | 4 | 2 | 2 | 170.0 |
| line-1-0721-0519-s001640 | 8 | 4 | 4 | 340.0 |
| line-1-0806-0577-s004001 | 8 | 4 | 4 | 340.0 |
| line-1-0812-0702-s007025 | 8 | 4 | 4 | 340.0 |
| line-1-0934-0766-s010042 | 6 | 2 | 4 | 340.0 |
| line-1-0957-0873-s013056 | 6 | 2 | 4 | 340.0 |
| line-1-1016-1010-s016558 | 6 | 2 | 4 | 340.0 |
| line-1-1414-1431-s029160 | 3 | 2 | 1 | 85.0 |
| line-2-0176-1241-s000000 | 4 | 2 | 2 | 170.0 |
| line-2-0412-0971-s008163 | 8 | 4 | 4 | 340.0 |
| line-2-0632-0850-s014020 | 7 | 2 | 5 | 425.0 |
| line-2-0709-0814-s016056 | 6 | 2 | 4 | 340.0 |
| line-2-0739-0727-s018092 | 6 | 4 | 2 | 170.0 |
| line-2-0810-0681-s020024 | 6 | 4 | 2 | 170.0 |
| line-2-0927-0656-s023607 | 6 | 2 | 4 | 340.0 |
| line-2-0992-0531-s027205 | 3 | 2 | 1 | 85.0 |
| line-3-0699-1073-s019487 | 6 | 2 | 4 | 340.0 |
| line-3-0712-1395-s026429 | 3 | 2 | 1 | 85.0 |
| line-3-0802-0796-s012808 | 6 | 2 | 4 | 340.0 |
| line-3-0812-0515-s006009 | 8 | 4 | 4 | 340.0 |
| line-3-0812-0726-s010872 | 6 | 4 | 2 | 170.0 |
| line-3-0821-0410-s000000 | 4 | 2 | 2 | 170.0 |
| line-3-0835-0594-s007859 | 8 | 4 | 4 | 340.0 |
| line-4-0365-0834-s027223 | 4 | 2 | 2 | 170.0 |
| line-4-0615-0673-s020318 | 8 | 2 | 6 | 510.0 |
| line-4-0729-0623-s017088 | 8 | 4 | 4 | 340.0 |
| line-4-0853-0615-s014296 | 10 | 4 | 6 | 510.0 |
| line-4-0997-0632-s010703 | 10 | 2 | 8 | 680.0 |
| line-4-1429-0421-s000000 | 5 | 2 | 3 | 255.0 |
| line-5-0102-0195-s034036 | 5 | 2 | 3 | 255.0 |
| line-5-0630-0432-s020384 | 10 | 2 | 8 | 680.0 |
| line-5-0840-0496-s014043 | 10 | 4 | 6 | 510.0 |
| line-5-0952-0575-s010540 | 11 | 2 | 9 | 765.0 |
| line-5-1054-0656-s007010 | 12 | 2 | 10 | 850.0 |
| line-5-1330-0747-s000000 | 6 | 2 | 4 | 340.0 |
| line-6-0365-0834-s016576 | 2 | 4 | 0 | 0.0 |
| line-6-0413-0965-s021009 | 2 | 4 | 0 | 0.0 |
| line-6-0528-0572-s007003 | 2 | 2 | 0 | 0.0 |
| line-6-0563-0757-s027406 | 2 | 2 | 0 | 0.0 |
| line-6-0661-0759-s029614 | 1 | 2 | 0 | 0.0 |
| line-6-0721-0519-s002704 | 2 | 4 | 0 | 0.0 |
| line-6-0723-0703-s031814 | 2 | 4 | 0 | 0.0 |
| line-6-0728-0635-s033426 | 2 | 4 | 0 | 0.0 |
| line-6-0766-0564-s035675 | 2 | 2 | 0 | 0.0 |
| line-6-0821-0410-s048793 | 1 | 4 | 0 | 0.0 |
| line-6-0840-0496-s037934 | 2 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Marrakech/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
