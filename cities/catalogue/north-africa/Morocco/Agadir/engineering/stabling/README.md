# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **172 trainsets at 30 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **155 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1093-1079-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0939-0927-s004761 | forward | revenue | 3 | pending |
| line-1 | line-1-0939-0927-s004761 | reverse | revenue | 3 | pending |
| line-1 | line-1-0895-0863-s006650 | forward | revenue | 3 | pending |
| line-1 | line-1-0895-0863-s006650 | reverse | revenue | 3 | pending |
| line-1 | line-1-0794-0863-s009656 | forward | revenue | 3 | pending |
| line-1 | line-1-0794-0863-s009656 | reverse | revenue | 3 | pending |
| line-1 | line-1-0758-0727-s012674 | forward | revenue | 3 | pending |
| line-1 | line-1-0758-0727-s012674 | reverse | revenue | 3 | pending |
| line-1 | line-1-0668-0636-s015702 | forward | revenue | 3 | pending |
| line-1 | line-1-0668-0636-s015702 | reverse | revenue | 3 | pending |
| line-1 | line-1-0618-0642-s017317 | forward | revenue | 2 | pending |
| line-1 | line-1-0618-0642-s017317 | reverse | revenue | 2 | pending |
| line-1 | line-1-0575-0579-s019225 | forward | revenue | 2 | pending |
| line-1 | line-1-0575-0579-s019225 | reverse | revenue | 2 | pending |
| line-1 | line-1-0536-0536-s021283 | forward | revenue | 2 | pending |
| line-1 | line-1-0536-0536-s021283 | reverse | revenue | 2 | pending |
| line-1 | line-1-0554-0448-s023342 | forward | revenue | 2 | pending |
| line-1 | line-1-0554-0448-s023342 | reverse | revenue | 2 | pending |
| line-1 | line-1-0513-0343-s025953 | forward | revenue | 2 | pending |
| line-1 | line-1-0513-0343-s025953 | reverse | revenue | 2 | pending |
| line-1 | line-1-0435-0260-s028576 | reverse | revenue | 2 | pending |
| line-1 | line-1-0618-0642-s017317 | forward | spare | 1 | pending |
| line-1 | line-1-0618-0642-s017317 | reverse | spare | 1 | pending |
| line-1 | line-1-0575-0579-s019225 | forward | spare | 1 | pending |
| line-1 | line-1-0575-0579-s019225 | reverse | spare | 1 | pending |
| line-1 | line-1-0536-0536-s021283 | forward | spare | 1 | pending |
| line-1 | line-1-0536-0536-s021283 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0137-0141-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0363-0283-s005743 | forward | revenue | 3 | pending |
| line-2 | line-2-0363-0283-s005743 | reverse | revenue | 3 | pending |
| line-2 | line-2-0463-0384-s008761 | forward | revenue | 3 | pending |
| line-2 | line-2-0463-0384-s008761 | reverse | revenue | 3 | pending |
| line-2 | line-2-0569-0490-s011782 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0490-s011782 | reverse | revenue | 3 | pending |
| line-2 | line-2-0575-0579-s014269 | forward | revenue | 3 | pending |
| line-2 | line-2-0575-0579-s014269 | reverse | revenue | 3 | pending |
| line-2 | line-2-0601-0692-s017805 | forward | revenue | 3 | pending |
| line-2 | line-2-0601-0692-s017805 | reverse | revenue | 3 | pending |
| line-2 | line-2-0679-0778-s020818 | forward | revenue | 3 | pending |
| line-2 | line-2-0679-0778-s020818 | reverse | revenue | 3 | pending |
| line-2 | line-2-0704-0892-s023350 | forward | revenue | 3 | pending |
| line-2 | line-2-0704-0892-s023350 | reverse | revenue | 3 | pending |
| line-2 | line-2-0790-0952-s025865 | reverse | revenue | 3 | pending |
| line-2 | line-2-0137-0141-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0363-0283-s005743 | forward | spare | 1 | pending |
| line-2 | line-2-0363-0283-s005743 | reverse | spare | 1 | pending |
| line-2 | line-2-0463-0384-s008761 | forward | spare | 1 | pending |
| line-2 | line-2-0463-0384-s008761 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1061-0928-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0979-0869-s003008 | forward | revenue | 4 | pending |
| line-3 | line-3-0979-0869-s003008 | reverse | revenue | 4 | pending |
| line-3 | line-3-0879-0836-s005801 | forward | revenue | 4 | pending |
| line-3 | line-3-0879-0836-s005801 | reverse | revenue | 3 | pending |
| line-3 | line-3-0772-0880-s008809 | forward | revenue | 3 | pending |
| line-3 | line-3-0772-0880-s008809 | reverse | revenue | 3 | pending |
| line-3 | line-3-0703-0778-s011818 | forward | revenue | 3 | pending |
| line-3 | line-3-0703-0778-s011818 | reverse | revenue | 3 | pending |
| line-3 | line-3-0585-0762-s014842 | forward | revenue | 3 | pending |
| line-3 | line-3-0585-0762-s014842 | reverse | revenue | 3 | pending |
| line-3 | line-3-0475-0709-s017858 | forward | revenue | 3 | pending |
| line-3 | line-3-0475-0709-s017858 | reverse | revenue | 3 | pending |
| line-3 | line-3-0367-0641-s020880 | forward | revenue | 3 | pending |
| line-3 | line-3-0367-0641-s020880 | reverse | revenue | 3 | pending |
| line-3 | line-3-0104-0580-s027049 | reverse | revenue | 3 | pending |
| line-3 | line-3-0879-0836-s005801 | reverse | spare | 1 | pending |
| line-3 | line-3-0772-0880-s008809 | forward | spare | 1 | pending |
| line-3 | line-3-0772-0880-s008809 | reverse | spare | 1 | pending |
| line-3 | line-3-0703-0778-s011818 | forward | spare | 1 | pending |
| line-3 | line-3-0703-0778-s011818 | reverse | spare | 1 | pending |
| line-3 | line-3-0585-0762-s014842 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**100 trainsets exceed the reference platform envelope**, requiring **5,950.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0435-0260-s028576 | 2 | 2 | 0 | 0.0 |
| line-1-0513-0343-s025953 | 4 | 2 | 2 | 119.0 |
| line-1-0536-0536-s021283 | 6 | 2 | 4 | 238.0 |
| line-1-0554-0448-s023342 | 4 | 2 | 2 | 119.0 |
| line-1-0575-0579-s019225 | 6 | 4 | 2 | 119.0 |
| line-1-0618-0642-s017317 | 6 | 2 | 4 | 238.0 |
| line-1-0668-0636-s015702 | 6 | 2 | 4 | 238.0 |
| line-1-0758-0727-s012674 | 6 | 2 | 4 | 238.0 |
| line-1-0794-0863-s009656 | 6 | 4 | 2 | 119.0 |
| line-1-0895-0863-s006650 | 6 | 2 | 4 | 238.0 |
| line-1-0939-0927-s004761 | 6 | 2 | 4 | 238.0 |
| line-1-1093-1079-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0137-0141-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0363-0283-s005743 | 8 | 2 | 6 | 357.0 |
| line-2-0463-0384-s008761 | 8 | 2 | 6 | 357.0 |
| line-2-0569-0490-s011782 | 6 | 2 | 4 | 238.0 |
| line-2-0575-0579-s014269 | 6 | 4 | 2 | 119.0 |
| line-2-0601-0692-s017805 | 6 | 2 | 4 | 238.0 |
| line-2-0679-0778-s020818 | 6 | 4 | 2 | 119.0 |
| line-2-0704-0892-s023350 | 6 | 2 | 4 | 238.0 |
| line-2-0790-0952-s025865 | 3 | 2 | 1 | 59.5 |
| line-3-0104-0580-s027049 | 3 | 2 | 1 | 59.5 |
| line-3-0367-0641-s020880 | 6 | 2 | 4 | 238.0 |
| line-3-0475-0709-s017858 | 6 | 2 | 4 | 238.0 |
| line-3-0585-0762-s014842 | 7 | 2 | 5 | 297.5 |
| line-3-0703-0778-s011818 | 8 | 4 | 4 | 238.0 |
| line-3-0772-0880-s008809 | 8 | 4 | 4 | 238.0 |
| line-3-0879-0836-s005801 | 8 | 2 | 6 | 357.0 |
| line-3-0979-0869-s003008 | 8 | 2 | 6 | 357.0 |
| line-3-1061-0928-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Agadir/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
