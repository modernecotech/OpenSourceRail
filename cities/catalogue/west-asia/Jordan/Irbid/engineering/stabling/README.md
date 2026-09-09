# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **107 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **96 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0840-0623-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0736-0627-s003572 | forward | revenue | 3 | pending |
| line-1 | line-1-0736-0627-s003572 | reverse | revenue | 3 | pending |
| line-1 | line-1-0673-0623-s005189 | forward | revenue | 3 | pending |
| line-1 | line-1-0673-0623-s005189 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0553-s008515 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0553-s008515 | reverse | revenue | 3 | pending |
| line-1 | line-1-0471-0526-s010965 | forward | revenue | 3 | pending |
| line-1 | line-1-0471-0526-s010965 | reverse | revenue | 2 | pending |
| line-1 | line-1-0402-0548-s013405 | forward | revenue | 2 | pending |
| line-1 | line-1-0402-0548-s013405 | reverse | revenue | 2 | pending |
| line-1 | line-1-0312-0567-s015842 | reverse | revenue | 2 | pending |
| line-1 | line-1-0471-0526-s010965 | reverse | spare | 1 | pending |
| line-1 | line-1-0402-0548-s013405 | forward | spare | 1 | pending |
| line-1 | line-1-0402-0548-s013405 | reverse | spare | 1 | pending |
| line-1 | line-1-0312-0567-s015842 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0620-0704-s003010 | forward | revenue | 3 | pending |
| line-2 | line-2-0620-0704-s003010 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0613-s006026 | forward | revenue | 3 | pending |
| line-2 | line-2-0545-0613-s006026 | reverse | revenue | 2 | pending |
| line-2 | line-2-0555-0553-s007527 | forward | revenue | 2 | pending |
| line-2 | line-2-0555-0553-s007527 | reverse | revenue | 2 | pending |
| line-2 | line-2-0578-0475-s009669 | forward | revenue | 2 | pending |
| line-2 | line-2-0578-0475-s009669 | reverse | revenue | 2 | pending |
| line-2 | line-2-0577-0389-s011828 | forward | revenue | 2 | pending |
| line-2 | line-2-0577-0389-s011828 | reverse | revenue | 2 | pending |
| line-2 | line-2-0634-0323-s013970 | reverse | revenue | 2 | pending |
| line-2 | line-2-0545-0613-s006026 | reverse | spare | 1 | pending |
| line-2 | line-2-0555-0553-s007527 | forward | spare | 1 | pending |
| line-2 | line-2-0555-0553-s007527 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0453-0614-s003006 | forward | revenue | 3 | pending |
| line-3 | line-3-0453-0614-s003006 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0553-s005777 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0553-s005777 | reverse | revenue | 3 | pending |
| line-3 | line-3-0635-0506-s009037 | forward | revenue | 3 | pending |
| line-3 | line-3-0635-0506-s009037 | reverse | revenue | 3 | pending |
| line-3 | line-3-0712-0447-s011502 | forward | revenue | 3 | pending |
| line-3 | line-3-0712-0447-s011502 | reverse | revenue | 3 | pending |
| line-3 | line-3-0808-0447-s013947 | forward | revenue | 3 | pending |
| line-3 | line-3-0808-0447-s013947 | reverse | revenue | 3 | pending |
| line-3 | line-3-0944-0336-s018870 | reverse | revenue | 3 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0453-0614-s003006 | forward | spare | 1 | pending |
| line-3 | line-3-0453-0614-s003006 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0553-s005777 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**59 trainsets exceed the reference platform envelope**, requiring **3,510.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0312-0567-s015842 | 3 | 2 | 1 | 59.5 |
| line-1-0402-0548-s013405 | 6 | 2 | 4 | 238.0 |
| line-1-0471-0526-s010965 | 6 | 2 | 4 | 238.0 |
| line-1-0555-0553-s008515 | 6 | 4 | 2 | 119.0 |
| line-1-0673-0623-s005189 | 6 | 2 | 4 | 238.0 |
| line-1-0736-0627-s003572 | 6 | 2 | 4 | 238.0 |
| line-1-0840-0623-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0545-0613-s006026 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0553-s007527 | 6 | 4 | 2 | 119.0 |
| line-2-0577-0389-s011828 | 4 | 2 | 2 | 119.0 |
| line-2-0578-0475-s009669 | 4 | 2 | 2 | 119.0 |
| line-2-0620-0704-s003010 | 6 | 2 | 4 | 238.0 |
| line-2-0634-0323-s013970 | 2 | 2 | 0 | 0.0 |
| line-2-0700-0815-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0351-0708-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0453-0614-s003006 | 8 | 2 | 6 | 357.0 |
| line-3-0555-0553-s005777 | 7 | 4 | 3 | 178.5 |
| line-3-0635-0506-s009037 | 6 | 2 | 4 | 238.0 |
| line-3-0712-0447-s011502 | 6 | 2 | 4 | 238.0 |
| line-3-0808-0447-s013947 | 6 | 2 | 4 | 238.0 |
| line-3-0944-0336-s018870 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Irbid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
