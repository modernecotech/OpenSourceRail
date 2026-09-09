# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **169 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **152 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0451-0897-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0509-0792-s003019 | forward | revenue | 4 | pending |
| line-1 | line-1-0509-0792-s003019 | reverse | revenue | 4 | pending |
| line-1 | line-1-0454-0683-s006032 | forward | revenue | 4 | pending |
| line-1 | line-1-0454-0683-s006032 | reverse | revenue | 4 | pending |
| line-1 | line-1-0507-0620-s007927 | forward | revenue | 4 | pending |
| line-1 | line-1-0507-0620-s007927 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0563-s009837 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0563-s009837 | reverse | revenue | 4 | pending |
| line-1 | line-1-0588-0548-s012073 | forward | revenue | 4 | pending |
| line-1 | line-1-0588-0548-s012073 | reverse | revenue | 4 | pending |
| line-1 | line-1-0595-0438-s015074 | forward | revenue | 4 | pending |
| line-1 | line-1-0595-0438-s015074 | reverse | revenue | 4 | pending |
| line-1 | line-1-0708-0006-s026117 | reverse | revenue | 3 | pending |
| line-1 | line-1-0708-0006-s026117 | reverse | spare | 1 | pending |
| line-1 | line-1-0451-0897-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0509-0792-s003019 | forward | spare | 1 | pending |
| line-1 | line-1-0509-0792-s003019 | reverse | spare | 1 | pending |
| line-1 | line-1-0454-0683-s006032 | forward | spare | 1 | pending |
| line-1 | line-1-0454-0683-s006032 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0080-1074-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0394-0664-s013579 | forward | revenue | 6 | pending |
| line-2 | line-2-0394-0664-s013579 | reverse | revenue | 5 | pending |
| line-2 | line-2-0492-0585-s016581 | forward | revenue | 5 | pending |
| line-2 | line-2-0492-0585-s016581 | reverse | revenue | 5 | pending |
| line-2 | line-2-0550-0563-s018168 | forward | revenue | 5 | pending |
| line-2 | line-2-0550-0563-s018168 | reverse | revenue | 5 | pending |
| line-2 | line-2-0525-0465-s021123 | forward | revenue | 5 | pending |
| line-2 | line-2-0525-0465-s021123 | reverse | revenue | 5 | pending |
| line-2 | line-2-0512-0354-s024071 | reverse | revenue | 5 | pending |
| line-2 | line-2-0394-0664-s013579 | reverse | spare | 1 | pending |
| line-2 | line-2-0492-0585-s016581 | forward | spare | 1 | pending |
| line-2 | line-2-0492-0585-s016581 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0563-s018168 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0563-s018168 | reverse | spare | 1 | pending |
| line-2 | line-2-0525-0465-s021123 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0365-0456-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0462-0515-s003027 | forward | revenue | 5 | pending |
| line-3 | line-3-0462-0515-s003027 | reverse | revenue | 5 | pending |
| line-3 | line-3-0550-0563-s006156 | forward | revenue | 5 | pending |
| line-3 | line-3-0550-0563-s006156 | reverse | revenue | 5 | pending |
| line-3 | line-3-0614-0635-s008705 | forward | revenue | 4 | pending |
| line-3 | line-3-0614-0635-s008705 | reverse | revenue | 4 | pending |
| line-3 | line-3-0712-0714-s011714 | forward | revenue | 4 | pending |
| line-3 | line-3-0712-0714-s011714 | reverse | revenue | 4 | pending |
| line-3 | line-3-1025-0987-s020711 | reverse | revenue | 4 | pending |
| line-3 | line-3-0614-0635-s008705 | forward | spare | 1 | pending |
| line-3 | line-3-0614-0635-s008705 | reverse | spare | 1 | pending |
| line-3 | line-3-0712-0714-s011714 | forward | spare | 1 | pending |
| line-3 | line-3-0712-0714-s011714 | reverse | spare | 1 | pending |
| line-3 | line-3-1025-0987-s020711 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**123 trainsets exceed the reference platform envelope**, requiring **7,318.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0451-0897-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0454-0683-s006032 | 10 | 2 | 8 | 476.0 |
| line-1-0507-0620-s007927 | 8 | 2 | 6 | 357.0 |
| line-1-0509-0792-s003019 | 10 | 2 | 8 | 476.0 |
| line-1-0550-0563-s009837 | 8 | 4 | 4 | 238.0 |
| line-1-0588-0548-s012073 | 8 | 2 | 6 | 357.0 |
| line-1-0595-0438-s015074 | 8 | 2 | 6 | 357.0 |
| line-1-0708-0006-s026117 | 4 | 2 | 2 | 119.0 |
| line-2-0080-1074-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0394-0664-s013579 | 12 | 2 | 10 | 595.0 |
| line-2-0492-0585-s016581 | 12 | 2 | 10 | 595.0 |
| line-2-0512-0354-s024071 | 5 | 2 | 3 | 178.5 |
| line-2-0525-0465-s021123 | 11 | 2 | 9 | 535.5 |
| line-2-0550-0563-s018168 | 12 | 4 | 8 | 476.0 |
| line-3-0365-0456-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0462-0515-s003027 | 10 | 2 | 8 | 476.0 |
| line-3-0550-0563-s006156 | 10 | 4 | 6 | 357.0 |
| line-3-0614-0635-s008705 | 10 | 2 | 8 | 476.0 |
| line-3-0712-0714-s011714 | 10 | 2 | 8 | 476.0 |
| line-3-1025-0987-s020711 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/latin-america/Ecuador/Cuenca/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
