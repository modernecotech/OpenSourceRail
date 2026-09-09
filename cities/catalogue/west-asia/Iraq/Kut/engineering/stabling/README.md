# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **101 trainsets at 16 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **90 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0432-0235-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0484-0323-s002226 | forward | revenue | 5 | pending |
| line-1 | line-1-0484-0323-s002226 | reverse | revenue | 5 | pending |
| line-1 | line-1-0563-0402-s004460 | forward | revenue | 4 | pending |
| line-1 | line-1-0563-0402-s004460 | reverse | revenue | 4 | pending |
| line-1 | line-1-0559-0540-s007746 | forward | revenue | 4 | pending |
| line-1 | line-1-0559-0540-s007746 | reverse | revenue | 4 | pending |
| line-1 | line-1-0643-0608-s010494 | forward | revenue | 4 | pending |
| line-1 | line-1-0643-0608-s010494 | reverse | revenue | 4 | pending |
| line-1 | line-1-1038-0979-s022368 | reverse | revenue | 4 | pending |
| line-1 | line-1-0563-0402-s004460 | forward | spare | 1 | pending |
| line-1 | line-1-0563-0402-s004460 | reverse | spare | 1 | pending |
| line-1 | line-1-0559-0540-s007746 | forward | spare | 1 | pending |
| line-1 | line-1-0559-0540-s007746 | reverse | spare | 1 | pending |
| line-1 | line-1-0643-0608-s010494 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0399-0481-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0476-0540-s002029 | forward | revenue | 3 | pending |
| line-2 | line-2-0476-0540-s002029 | reverse | revenue | 3 | pending |
| line-2 | line-2-0559-0540-s004070 | forward | revenue | 3 | pending |
| line-2 | line-2-0559-0540-s004070 | reverse | revenue | 2 | pending |
| line-2 | line-2-0629-0472-s006033 | forward | revenue | 2 | pending |
| line-2 | line-2-0629-0472-s006033 | reverse | revenue | 2 | pending |
| line-2 | line-2-0742-0465-s009399 | reverse | revenue | 2 | pending |
| line-2 | line-2-0559-0540-s004070 | reverse | spare | 1 | pending |
| line-2 | line-2-0629-0472-s006033 | forward | spare | 1 | pending |
| line-2 | line-2-0629-0472-s006033 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0717-0891-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0663-s006860 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0663-s006860 | reverse | revenue | 4 | pending |
| line-3 | line-3-0559-0540-s009668 | forward | revenue | 3 | pending |
| line-3 | line-3-0559-0540-s009668 | reverse | revenue | 3 | pending |
| line-3 | line-3-0491-0463-s012158 | forward | revenue | 3 | pending |
| line-3 | line-3-0491-0463-s012158 | reverse | revenue | 3 | pending |
| line-3 | line-3-0403-0375-s014647 | reverse | revenue | 3 | pending |
| line-3 | line-3-0559-0540-s009668 | forward | spare | 1 | pending |
| line-3 | line-3-0559-0540-s009668 | reverse | spare | 1 | pending |
| line-3 | line-3-0491-0463-s012158 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**63 trainsets exceed the reference platform envelope**, requiring **3,748.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0432-0235-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0484-0323-s002226 | 10 | 2 | 8 | 476.0 |
| line-1-0559-0540-s007746 | 10 | 4 | 6 | 357.0 |
| line-1-0563-0402-s004460 | 10 | 2 | 8 | 476.0 |
| line-1-0643-0608-s010494 | 9 | 2 | 7 | 416.5 |
| line-1-1038-0979-s022368 | 4 | 2 | 2 | 119.0 |
| line-2-0399-0481-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0476-0540-s002029 | 6 | 2 | 4 | 238.0 |
| line-2-0559-0540-s004070 | 6 | 4 | 2 | 119.0 |
| line-2-0629-0472-s006033 | 6 | 2 | 4 | 238.0 |
| line-2-0742-0465-s009399 | 2 | 2 | 0 | 0.0 |
| line-3-0403-0375-s014647 | 3 | 2 | 1 | 59.5 |
| line-3-0491-0463-s012158 | 7 | 2 | 5 | 297.5 |
| line-3-0549-0663-s006860 | 8 | 2 | 6 | 357.0 |
| line-3-0559-0540-s009668 | 8 | 4 | 4 | 238.0 |
| line-3-0717-0891-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Kut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
