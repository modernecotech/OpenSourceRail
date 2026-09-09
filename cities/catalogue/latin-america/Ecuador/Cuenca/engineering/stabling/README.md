# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **169 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0451-0897-s000000 | forward | 5 | pending |
| line-1 | line-1-0509-0792-s003019 | forward | 5 | pending |
| line-1 | line-1-0509-0792-s003019 | reverse | 5 | pending |
| line-1 | line-1-0454-0683-s006032 | forward | 5 | pending |
| line-1 | line-1-0454-0683-s006032 | reverse | 5 | pending |
| line-1 | line-1-0507-0620-s007927 | forward | 4 | pending |
| line-1 | line-1-0507-0620-s007927 | reverse | 4 | pending |
| line-1 | line-1-0550-0563-s009837 | forward | 4 | pending |
| line-1 | line-1-0550-0563-s009837 | reverse | 4 | pending |
| line-1 | line-1-0588-0548-s012073 | forward | 4 | pending |
| line-1 | line-1-0588-0548-s012073 | reverse | 4 | pending |
| line-1 | line-1-0595-0438-s015074 | forward | 4 | pending |
| line-1 | line-1-0595-0438-s015074 | reverse | 4 | pending |
| line-1 | line-1-0708-0006-s026117 | reverse | 4 | pending |
| line-2 | line-2-0080-1074-s000000 | forward | 6 | pending |
| line-2 | line-2-0394-0664-s013579 | forward | 6 | pending |
| line-2 | line-2-0394-0664-s013579 | reverse | 6 | pending |
| line-2 | line-2-0492-0585-s016581 | forward | 6 | pending |
| line-2 | line-2-0492-0585-s016581 | reverse | 6 | pending |
| line-2 | line-2-0550-0563-s018168 | forward | 6 | pending |
| line-2 | line-2-0550-0563-s018168 | reverse | 6 | pending |
| line-2 | line-2-0525-0465-s021123 | forward | 6 | pending |
| line-2 | line-2-0525-0465-s021123 | reverse | 5 | pending |
| line-2 | line-2-0512-0354-s024071 | reverse | 5 | pending |
| line-3 | line-3-0365-0456-s000000 | forward | 5 | pending |
| line-3 | line-3-0462-0515-s003027 | forward | 5 | pending |
| line-3 | line-3-0462-0515-s003027 | reverse | 5 | pending |
| line-3 | line-3-0550-0563-s006156 | forward | 5 | pending |
| line-3 | line-3-0550-0563-s006156 | reverse | 5 | pending |
| line-3 | line-3-0614-0635-s008705 | forward | 5 | pending |
| line-3 | line-3-0614-0635-s008705 | reverse | 5 | pending |
| line-3 | line-3-0712-0714-s011714 | forward | 5 | pending |
| line-3 | line-3-0712-0714-s011714 | reverse | 5 | pending |
| line-3 | line-3-1025-0987-s020711 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/latin-america/Ecuador/Cuenca/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
