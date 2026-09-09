# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **80 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **71 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0300-0176-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0303-0283-s003017 | forward | revenue | 3 | pending |
| line-1 | line-1-0303-0283-s003017 | reverse | revenue | 3 | pending |
| line-1 | line-1-0374-0372-s006118 | forward | revenue | 2 | pending |
| line-1 | line-1-0374-0372-s006118 | reverse | revenue | 2 | pending |
| line-1 | line-1-0314-0427-s008352 | forward | revenue | 2 | pending |
| line-1 | line-1-0314-0427-s008352 | reverse | revenue | 2 | pending |
| line-1 | line-1-0339-0524-s010599 | forward | revenue | 2 | pending |
| line-1 | line-1-0339-0524-s010599 | reverse | revenue | 2 | pending |
| line-1 | line-1-0266-0580-s012842 | reverse | revenue | 2 | pending |
| line-1 | line-1-0374-0372-s006118 | forward | spare | 1 | pending |
| line-1 | line-1-0374-0372-s006118 | reverse | spare | 1 | pending |
| line-1 | line-1-0314-0427-s008352 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0164-0368-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0282-0357-s003025 | forward | revenue | 3 | pending |
| line-2 | line-2-0282-0357-s003025 | reverse | revenue | 3 | pending |
| line-2 | line-2-0374-0372-s005434 | forward | revenue | 3 | pending |
| line-2 | line-2-0374-0372-s005434 | reverse | revenue | 3 | pending |
| line-2 | line-2-0466-0345-s007682 | forward | revenue | 3 | pending |
| line-2 | line-2-0466-0345-s007682 | reverse | revenue | 3 | pending |
| line-2 | line-2-0538-0385-s009926 | forward | revenue | 2 | pending |
| line-2 | line-2-0538-0385-s009926 | reverse | revenue | 2 | pending |
| line-2 | line-2-0732-0367-s014426 | reverse | revenue | 2 | pending |
| line-2 | line-2-0538-0385-s009926 | forward | spare | 1 | pending |
| line-2 | line-2-0538-0385-s009926 | reverse | spare | 1 | pending |
| line-2 | line-2-0732-0367-s014426 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0345-0134-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0382-0263-s003019 | forward | revenue | 4 | pending |
| line-3 | line-3-0382-0263-s003019 | reverse | revenue | 4 | pending |
| line-3 | line-3-0374-0372-s005613 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0372-s005613 | reverse | revenue | 3 | pending |
| line-3 | line-3-0471-0564-s011431 | reverse | revenue | 3 | pending |
| line-3 | line-3-0374-0372-s005613 | forward | spare | 1 | pending |
| line-3 | line-3-0374-0372-s005613 | reverse | spare | 1 | pending |
| line-3 | line-3-0471-0564-s011431 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**42 trainsets exceed the reference platform envelope**, requiring **2,058.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0266-0580-s012842 | 2 | 2 | 0 | 0.0 |
| line-1-0300-0176-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0303-0283-s003017 | 6 | 2 | 4 | 196.0 |
| line-1-0314-0427-s008352 | 5 | 2 | 3 | 147.0 |
| line-1-0339-0524-s010599 | 4 | 2 | 2 | 98.0 |
| line-1-0374-0372-s006118 | 6 | 4 | 2 | 98.0 |
| line-2-0164-0368-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0282-0357-s003025 | 6 | 2 | 4 | 196.0 |
| line-2-0374-0372-s005434 | 6 | 4 | 2 | 98.0 |
| line-2-0466-0345-s007682 | 6 | 2 | 4 | 196.0 |
| line-2-0538-0385-s009926 | 6 | 2 | 4 | 196.0 |
| line-2-0732-0367-s014426 | 3 | 2 | 1 | 49.0 |
| line-3-0345-0134-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0374-0372-s005613 | 8 | 4 | 4 | 196.0 |
| line-3-0382-0263-s003019 | 8 | 2 | 6 | 294.0 |
| line-3-0471-0564-s011431 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Nelspruit/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
