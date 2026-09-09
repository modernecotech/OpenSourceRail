# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **119 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **107 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0445-0353-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | forward | revenue | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | reverse | revenue | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | forward | revenue | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | reverse | revenue | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | reverse | revenue | 2 | pending |
| line-1 | line-1-0593-0842-s013502 | forward | revenue | 2 | pending |
| line-1 | line-1-0593-0842-s013502 | reverse | revenue | 2 | pending |
| line-1 | line-1-0647-0895-s015818 | reverse | revenue | 2 | pending |
| line-1 | line-1-0592-0728-s011164 | reverse | spare | 1 | pending |
| line-1 | line-1-0593-0842-s013502 | forward | spare | 1 | pending |
| line-1 | line-1-0593-0842-s013502 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0895-s015818 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | forward | revenue | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | reverse | revenue | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | forward | revenue | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | reverse | revenue | 4 | pending |
| line-2 | line-2-0581-0543-s008757 | forward | revenue | 3 | pending |
| line-2 | line-2-0581-0543-s008757 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0560-s010016 | forward | revenue | 3 | pending |
| line-2 | line-2-0545-0560-s010016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0597-s011764 | forward | revenue | 3 | pending |
| line-2 | line-2-0486-0597-s011764 | reverse | revenue | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | forward | revenue | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | reverse | revenue | 3 | pending |
| line-2 | line-2-0145-0992-s024048 | reverse | revenue | 3 | pending |
| line-2 | line-2-0581-0543-s008757 | forward | spare | 1 | pending |
| line-2 | line-2-0581-0543-s008757 | reverse | spare | 1 | pending |
| line-2 | line-2-0545-0560-s010016 | forward | spare | 1 | pending |
| line-2 | line-2-0545-0560-s010016 | reverse | spare | 1 | pending |
| line-2 | line-2-0486-0597-s011764 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0574-0441-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0574-0441-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | forward | revenue | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | reverse | revenue | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | forward | revenue | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | reverse | revenue | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | forward | revenue | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | reverse | revenue | 2 | pending |
| line-3 | line-3-0725-0794-s013896 | reverse | revenue | 2 | pending |
| line-3 | line-3-0654-0714-s011212 | reverse | spare | 1 | pending |
| line-3 | line-3-0725-0794-s013896 | reverse | spare | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0445-0353-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0460-0463-s003013 | 6 | 2 | 4 | 238.0 |
| line-1-0545-0560-s006308 | 6 | 4 | 2 | 119.0 |
| line-1-0592-0728-s011164 | 6 | 2 | 4 | 238.0 |
| line-1-0593-0842-s013502 | 6 | 2 | 4 | 238.0 |
| line-1-0612-0623-s008849 | 6 | 4 | 2 | 119.0 |
| line-1-0647-0895-s015818 | 3 | 2 | 1 | 59.5 |
| line-2-0145-0992-s024048 | 3 | 2 | 1 | 59.5 |
| line-2-0396-0679-s014764 | 6 | 2 | 4 | 238.0 |
| line-2-0486-0597-s011764 | 7 | 2 | 5 | 297.5 |
| line-2-0545-0560-s010016 | 8 | 4 | 4 | 238.0 |
| line-2-0581-0543-s008757 | 8 | 2 | 6 | 357.0 |
| line-2-0623-0464-s006292 | 8 | 2 | 6 | 357.0 |
| line-2-0713-0491-s003267 | 8 | 2 | 6 | 357.0 |
| line-2-0818-0385-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0533-0317-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0545-0560-s005830 | 6 | 4 | 2 | 119.0 |
| line-3-0574-0441-s003009 | 6 | 2 | 4 | 238.0 |
| line-3-0633-0604-s008528 | 6 | 4 | 2 | 119.0 |
| line-3-0654-0714-s011212 | 6 | 2 | 4 | 238.0 |
| line-3-0725-0794-s013896 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lubango/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
