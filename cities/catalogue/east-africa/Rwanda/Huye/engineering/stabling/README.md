# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0520-0272-s000000 | forward | 4 | pending |
| line-1 | line-1-0455-0352-s002279 | forward | 4 | pending |
| line-1 | line-1-0455-0352-s002279 | reverse | 4 | pending |
| line-1 | line-1-0381-0378-s004479 | forward | 4 | pending |
| line-1 | line-1-0381-0378-s004479 | reverse | 4 | pending |
| line-1 | line-1-0320-0444-s006898 | forward | 4 | pending |
| line-1 | line-1-0320-0444-s006898 | reverse | 4 | pending |
| line-1 | line-1-0008-0663-s015861 | reverse | 4 | pending |
| line-2 | line-2-0666-0617-s000000 | forward | 5 | pending |
| line-2 | line-2-0439-0495-s007022 | forward | 5 | pending |
| line-2 | line-2-0439-0495-s007022 | reverse | 5 | pending |
| line-2 | line-2-0381-0378-s010317 | forward | 5 | pending |
| line-2 | line-2-0381-0378-s010317 | reverse | 5 | pending |
| line-2 | line-2-0310-0231-s014020 | reverse | 4 | pending |
| line-3 | line-3-0005-0503-s000000 | forward | 4 | pending |
| line-3 | line-3-0195-0392-s007025 | forward | 4 | pending |
| line-3 | line-3-0195-0392-s007025 | reverse | 4 | pending |
| line-3 | line-3-0320-0372-s010029 | forward | 4 | pending |
| line-3 | line-3-0320-0372-s010029 | reverse | 4 | pending |
| line-3 | line-3-0381-0378-s011343 | forward | 4 | pending |
| line-3 | line-3-0381-0378-s011343 | reverse | 4 | pending |
| line-3 | line-3-0362-0236-s014769 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Huye/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
