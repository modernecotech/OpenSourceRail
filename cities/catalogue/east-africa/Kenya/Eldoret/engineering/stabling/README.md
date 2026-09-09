# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **163 trainsets at 17 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0733-0710-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0655-0615-s003317 | forward | revenue | 6 | pending |
| line-1 | line-1-0655-0615-s003317 | reverse | revenue | 6 | pending |
| line-1 | line-1-0548-0553-s006188 | forward | revenue | 6 | pending |
| line-1 | line-1-0548-0553-s006188 | reverse | revenue | 6 | pending |
| line-1 | line-1-0470-0523-s009329 | forward | revenue | 6 | pending |
| line-1 | line-1-0470-0523-s009329 | reverse | revenue | 6 | pending |
| line-1 | line-1-0385-0435-s012332 | forward | revenue | 5 | pending |
| line-1 | line-1-0385-0435-s012332 | reverse | revenue | 5 | pending |
| line-1 | line-1-0160-0039-s022574 | reverse | revenue | 5 | pending |
| line-1 | line-1-0385-0435-s012332 | forward | spare | 1 | pending |
| line-1 | line-1-0385-0435-s012332 | reverse | spare | 1 | pending |
| line-1 | line-1-0160-0039-s022574 | reverse | spare | 1 | pending |
| line-1 | line-1-0733-0710-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0655-0615-s003317 | forward | spare | 1 | pending |
| line-1 | line-1-0655-0615-s003317 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0456-0775-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0539-0664-s003007 | forward | revenue | 5 | pending |
| line-2 | line-2-0539-0664-s003007 | reverse | revenue | 5 | pending |
| line-2 | line-2-0548-0553-s005680 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0553-s005680 | reverse | revenue | 4 | pending |
| line-2 | line-2-0602-0481-s007635 | forward | revenue | 4 | pending |
| line-2 | line-2-0602-0481-s007635 | reverse | revenue | 4 | pending |
| line-2 | line-2-0730-0215-s014309 | reverse | revenue | 4 | pending |
| line-2 | line-2-0548-0553-s005680 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0553-s005680 | reverse | spare | 1 | pending |
| line-2 | line-2-0602-0481-s007635 | forward | spare | 1 | pending |
| line-2 | line-2-0602-0481-s007635 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0056-0021-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0345-0410-s011200 | forward | revenue | 6 | pending |
| line-3 | line-3-0345-0410-s011200 | reverse | revenue | 6 | pending |
| line-3 | line-3-0480-0445-s014206 | forward | revenue | 6 | pending |
| line-3 | line-3-0480-0445-s014206 | reverse | revenue | 6 | pending |
| line-3 | line-3-0548-0553-s017061 | forward | revenue | 5 | pending |
| line-3 | line-3-0548-0553-s017061 | reverse | revenue | 5 | pending |
| line-3 | line-3-0580-0661-s019586 | forward | revenue | 5 | pending |
| line-3 | line-3-0580-0661-s019586 | reverse | revenue | 5 | pending |
| line-3 | line-3-0601-0747-s022099 | reverse | revenue | 5 | pending |
| line-3 | line-3-0548-0553-s017061 | forward | spare | 1 | pending |
| line-3 | line-3-0548-0553-s017061 | reverse | spare | 1 | pending |
| line-3 | line-3-0580-0661-s019586 | forward | spare | 1 | pending |
| line-3 | line-3-0580-0661-s019586 | reverse | spare | 1 | pending |
| line-3 | line-3-0601-0747-s022099 | reverse | spare | 1 | pending |
| line-3 | line-3-0056-0021-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**123 trainsets exceed the reference platform envelope**, requiring **7,318.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0160-0039-s022574 | 6 | 2 | 4 | 238.0 |
| line-1-0385-0435-s012332 | 12 | 2 | 10 | 595.0 |
| line-1-0470-0523-s009329 | 12 | 2 | 10 | 595.0 |
| line-1-0548-0553-s006188 | 12 | 4 | 8 | 476.0 |
| line-1-0655-0615-s003317 | 14 | 2 | 12 | 714.0 |
| line-1-0733-0710-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0456-0775-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0539-0664-s003007 | 10 | 2 | 8 | 476.0 |
| line-2-0548-0553-s005680 | 10 | 4 | 6 | 357.0 |
| line-2-0602-0481-s007635 | 10 | 2 | 8 | 476.0 |
| line-2-0730-0215-s014309 | 4 | 2 | 2 | 119.0 |
| line-3-0056-0021-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0345-0410-s011200 | 12 | 2 | 10 | 595.0 |
| line-3-0480-0445-s014206 | 12 | 2 | 10 | 595.0 |
| line-3-0548-0553-s017061 | 12 | 4 | 8 | 476.0 |
| line-3-0580-0661-s019586 | 12 | 2 | 10 | 595.0 |
| line-3-0601-0747-s022099 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Eldoret/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
