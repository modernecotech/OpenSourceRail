# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **69 trainsets at 16 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0288-0520-s000000 | forward | 3 | pending |
| line-1 | line-1-0349-0451-s002024 | forward | 3 | pending |
| line-1 | line-1-0349-0451-s002024 | reverse | 3 | pending |
| line-1 | line-1-0379-0373-s004059 | forward | 3 | pending |
| line-1 | line-1-0379-0373-s004059 | reverse | 2 | pending |
| line-1 | line-1-0391-0287-s006034 | forward | 2 | pending |
| line-1 | line-1-0391-0287-s006034 | reverse | 2 | pending |
| line-1 | line-1-0402-0196-s008078 | forward | 2 | pending |
| line-1 | line-1-0402-0196-s008078 | reverse | 2 | pending |
| line-1 | line-1-0371-0112-s010141 | reverse | 2 | pending |
| line-2 | line-2-0603-0266-s000000 | forward | 4 | pending |
| line-2 | line-2-0468-0325-s003622 | forward | 4 | pending |
| line-2 | line-2-0468-0325-s003622 | reverse | 3 | pending |
| line-2 | line-2-0379-0373-s006263 | forward | 3 | pending |
| line-2 | line-2-0379-0373-s006263 | reverse | 3 | pending |
| line-2 | line-2-0431-0513-s009823 | reverse | 3 | pending |
| line-3 | line-3-0506-0435-s000000 | forward | 3 | pending |
| line-3 | line-3-0450-0397-s001604 | forward | 3 | pending |
| line-3 | line-3-0450-0397-s001604 | reverse | 3 | pending |
| line-3 | line-3-0379-0373-s003284 | forward | 3 | pending |
| line-3 | line-3-0379-0373-s003284 | reverse | 3 | pending |
| line-3 | line-3-0334-0349-s004611 | forward | 2 | pending |
| line-3 | line-3-0334-0349-s004611 | reverse | 2 | pending |
| line-3 | line-3-0249-0212-s008353 | forward | 2 | pending |
| line-3 | line-3-0249-0212-s008353 | reverse | 2 | pending |
| line-3 | line-3-0121-0078-s012094 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Masaka/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
