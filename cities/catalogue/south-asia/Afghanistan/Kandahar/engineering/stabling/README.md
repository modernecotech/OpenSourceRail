# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **101 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0346-0781-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0502-0681-s005071 | forward | revenue | 3 | pending |
| line-1 | line-1-0502-0681-s005071 | reverse | revenue | 3 | pending |
| line-1 | line-1-0505-0561-s008096 | forward | revenue | 3 | pending |
| line-1 | line-1-0505-0561-s008096 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0535-s010247 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0535-s010247 | reverse | revenue | 3 | pending |
| line-1 | line-1-0597-0505-s012184 | forward | revenue | 3 | pending |
| line-1 | line-1-0597-0505-s012184 | reverse | revenue | 3 | pending |
| line-1 | line-1-0590-0415-s014120 | forward | revenue | 3 | pending |
| line-1 | line-1-0590-0415-s014120 | reverse | revenue | 3 | pending |
| line-1 | line-1-0635-0372-s015737 | forward | revenue | 2 | pending |
| line-1 | line-1-0635-0372-s015737 | reverse | revenue | 2 | pending |
| line-1 | line-1-0630-0303-s017338 | forward | revenue | 2 | pending |
| line-1 | line-1-0630-0303-s017338 | reverse | revenue | 2 | pending |
| line-1 | line-1-0616-0026-s023124 | reverse | revenue | 2 | pending |
| line-1 | line-1-0635-0372-s015737 | forward | spare | 1 | pending |
| line-1 | line-1-0635-0372-s015737 | reverse | spare | 1 | pending |
| line-1 | line-1-0630-0303-s017338 | forward | spare | 1 | pending |
| line-1 | line-1-0630-0303-s017338 | reverse | spare | 1 | pending |
| line-1 | line-1-0616-0026-s023124 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0742-0821-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0669-0699-s003085 | forward | revenue | 3 | pending |
| line-2 | line-2-0669-0699-s003085 | reverse | revenue | 3 | pending |
| line-2 | line-2-0595-0599-s006088 | forward | revenue | 3 | pending |
| line-2 | line-2-0595-0599-s006088 | reverse | revenue | 3 | pending |
| line-2 | line-2-0554-0535-s008313 | forward | revenue | 3 | pending |
| line-2 | line-2-0554-0535-s008313 | reverse | revenue | 3 | pending |
| line-2 | line-2-0507-0487-s010226 | forward | revenue | 3 | pending |
| line-2 | line-2-0507-0487-s010226 | reverse | revenue | 2 | pending |
| line-2 | line-2-0431-0455-s012139 | forward | revenue | 2 | pending |
| line-2 | line-2-0431-0455-s012139 | reverse | revenue | 2 | pending |
| line-2 | line-2-0244-0440-s016493 | reverse | revenue | 2 | pending |
| line-2 | line-2-0507-0487-s010226 | reverse | spare | 1 | pending |
| line-2 | line-2-0431-0455-s012139 | forward | spare | 1 | pending |
| line-2 | line-2-0431-0455-s012139 | reverse | spare | 1 | pending |
| line-2 | line-2-0244-0440-s016493 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0763-0381-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0641-0431-s003016 | forward | revenue | 4 | pending |
| line-3 | line-3-0641-0431-s003016 | reverse | revenue | 3 | pending |
| line-3 | line-3-0592-0529-s006021 | forward | revenue | 3 | pending |
| line-3 | line-3-0592-0529-s006021 | reverse | revenue | 3 | pending |
| line-3 | line-3-0549-0637-s009040 | forward | revenue | 3 | pending |
| line-3 | line-3-0549-0637-s009040 | reverse | revenue | 3 | pending |
| line-3 | line-3-0464-0768-s013272 | reverse | revenue | 3 | pending |
| line-3 | line-3-0641-0431-s003016 | reverse | spare | 1 | pending |
| line-3 | line-3-0592-0529-s006021 | forward | spare | 1 | pending |
| line-3 | line-3-0592-0529-s006021 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**63 trainsets exceed the reference platform envelope**, requiring **3,748.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0346-0781-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0502-0681-s005071 | 6 | 2 | 4 | 238.0 |
| line-1-0505-0561-s008096 | 6 | 2 | 4 | 238.0 |
| line-1-0554-0535-s010247 | 6 | 4 | 2 | 119.0 |
| line-1-0590-0415-s014120 | 6 | 2 | 4 | 238.0 |
| line-1-0597-0505-s012184 | 6 | 4 | 2 | 119.0 |
| line-1-0616-0026-s023124 | 3 | 2 | 1 | 59.5 |
| line-1-0630-0303-s017338 | 6 | 2 | 4 | 238.0 |
| line-1-0635-0372-s015737 | 6 | 2 | 4 | 238.0 |
| line-2-0244-0440-s016493 | 3 | 2 | 1 | 59.5 |
| line-2-0431-0455-s012139 | 6 | 2 | 4 | 238.0 |
| line-2-0507-0487-s010226 | 6 | 2 | 4 | 238.0 |
| line-2-0554-0535-s008313 | 6 | 4 | 2 | 119.0 |
| line-2-0595-0599-s006088 | 6 | 2 | 4 | 238.0 |
| line-2-0669-0699-s003085 | 6 | 2 | 4 | 238.0 |
| line-2-0742-0821-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0464-0768-s013272 | 3 | 2 | 1 | 59.5 |
| line-3-0549-0637-s009040 | 6 | 2 | 4 | 238.0 |
| line-3-0592-0529-s006021 | 8 | 4 | 4 | 238.0 |
| line-3-0641-0431-s003016 | 8 | 2 | 6 | 357.0 |
| line-3-0763-0381-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Kandahar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
