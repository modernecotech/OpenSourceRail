# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0520-0272-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0455-0352-s002279 | forward | revenue | 4 | pending |
| line-1 | line-1-0455-0352-s002279 | reverse | revenue | 4 | pending |
| line-1 | line-1-0381-0378-s004479 | forward | revenue | 4 | pending |
| line-1 | line-1-0381-0378-s004479 | reverse | revenue | 4 | pending |
| line-1 | line-1-0320-0444-s006898 | forward | revenue | 3 | pending |
| line-1 | line-1-0320-0444-s006898 | reverse | revenue | 3 | pending |
| line-1 | line-1-0008-0663-s015861 | reverse | revenue | 3 | pending |
| line-1 | line-1-0320-0444-s006898 | forward | spare | 1 | pending |
| line-1 | line-1-0320-0444-s006898 | reverse | spare | 1 | pending |
| line-1 | line-1-0008-0663-s015861 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0666-0617-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0439-0495-s007022 | forward | revenue | 5 | pending |
| line-2 | line-2-0439-0495-s007022 | reverse | revenue | 4 | pending |
| line-2 | line-2-0381-0378-s010317 | forward | revenue | 4 | pending |
| line-2 | line-2-0381-0378-s010317 | reverse | revenue | 4 | pending |
| line-2 | line-2-0310-0231-s014020 | reverse | revenue | 4 | pending |
| line-2 | line-2-0439-0495-s007022 | reverse | spare | 1 | pending |
| line-2 | line-2-0381-0378-s010317 | forward | spare | 1 | pending |
| line-2 | line-2-0381-0378-s010317 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0005-0503-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0195-0392-s007025 | forward | revenue | 4 | pending |
| line-3 | line-3-0195-0392-s007025 | reverse | revenue | 4 | pending |
| line-3 | line-3-0320-0372-s010029 | forward | revenue | 4 | pending |
| line-3 | line-3-0320-0372-s010029 | reverse | revenue | 3 | pending |
| line-3 | line-3-0381-0378-s011343 | forward | revenue | 3 | pending |
| line-3 | line-3-0381-0378-s011343 | reverse | revenue | 3 | pending |
| line-3 | line-3-0362-0236-s014769 | reverse | revenue | 3 | pending |
| line-3 | line-3-0320-0372-s010029 | reverse | spare | 1 | pending |
| line-3 | line-3-0381-0378-s011343 | forward | spare | 1 | pending |
| line-3 | line-3-0381-0378-s011343 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**58 trainsets exceed the reference platform envelope**, requiring **2,842.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0008-0663-s015861 | 4 | 2 | 2 | 98.0 |
| line-1-0320-0444-s006898 | 8 | 2 | 6 | 294.0 |
| line-1-0381-0378-s004479 | 8 | 4 | 4 | 196.0 |
| line-1-0455-0352-s002279 | 8 | 2 | 6 | 294.0 |
| line-1-0520-0272-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0310-0231-s014020 | 4 | 2 | 2 | 98.0 |
| line-2-0381-0378-s010317 | 10 | 4 | 6 | 294.0 |
| line-2-0439-0495-s007022 | 10 | 2 | 8 | 392.0 |
| line-2-0666-0617-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0005-0503-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0195-0392-s007025 | 8 | 2 | 6 | 294.0 |
| line-3-0320-0372-s010029 | 8 | 2 | 6 | 294.0 |
| line-3-0362-0236-s014769 | 3 | 2 | 1 | 49.0 |
| line-3-0381-0378-s011343 | 8 | 4 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Huye/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
