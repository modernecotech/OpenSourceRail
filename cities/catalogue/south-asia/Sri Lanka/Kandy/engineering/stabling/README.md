# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **178 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0600-1040-s000000 | forward | 5 | pending |
| line-1 | line-1-0612-0839-s005344 | forward | 4 | pending |
| line-1 | line-1-0612-0839-s005344 | reverse | 4 | pending |
| line-1 | line-1-0591-0723-s008466 | forward | 4 | pending |
| line-1 | line-1-0591-0723-s008466 | reverse | 4 | pending |
| line-1 | line-1-0549-0627-s011467 | forward | 4 | pending |
| line-1 | line-1-0549-0627-s011467 | reverse | 4 | pending |
| line-1 | line-1-0549-0555-s013405 | forward | 4 | pending |
| line-1 | line-1-0549-0555-s013405 | reverse | 4 | pending |
| line-1 | line-1-0533-0449-s016131 | forward | 4 | pending |
| line-1 | line-1-0533-0449-s016131 | reverse | 4 | pending |
| line-1 | line-1-0629-0395-s019290 | forward | 4 | pending |
| line-1 | line-1-0629-0395-s019290 | reverse | 4 | pending |
| line-1 | line-1-0672-0258-s023238 | forward | 4 | pending |
| line-1 | line-1-0672-0258-s023238 | reverse | 4 | pending |
| line-1 | line-1-0689-0101-s027176 | reverse | 4 | pending |
| line-2 | line-2-0897-0226-s000000 | forward | 5 | pending |
| line-2 | line-2-0773-0315-s004806 | forward | 5 | pending |
| line-2 | line-2-0773-0315-s004806 | reverse | 5 | pending |
| line-2 | line-2-0667-0492-s011057 | forward | 5 | pending |
| line-2 | line-2-0667-0492-s011057 | reverse | 5 | pending |
| line-2 | line-2-0549-0555-s014321 | forward | 5 | pending |
| line-2 | line-2-0549-0555-s014321 | reverse | 5 | pending |
| line-2 | line-2-0452-0599-s017078 | forward | 5 | pending |
| line-2 | line-2-0452-0599-s017078 | reverse | 5 | pending |
| line-2 | line-2-0361-0638-s020081 | forward | 5 | pending |
| line-2 | line-2-0361-0638-s020081 | reverse | 5 | pending |
| line-2 | line-2-0216-0821-s025533 | reverse | 4 | pending |
| line-3 | line-3-0669-0844-s000000 | forward | 6 | pending |
| line-3 | line-3-0616-0646-s005220 | forward | 6 | pending |
| line-3 | line-3-0616-0646-s005220 | reverse | 6 | pending |
| line-3 | line-3-0549-0555-s007781 | forward | 6 | pending |
| line-3 | line-3-0549-0555-s007781 | reverse | 5 | pending |
| line-3 | line-3-0464-0469-s010604 | forward | 5 | pending |
| line-3 | line-3-0464-0469-s010604 | reverse | 5 | pending |
| line-3 | line-3-0355-0504-s013631 | forward | 5 | pending |
| line-3 | line-3-0355-0504-s013631 | reverse | 5 | pending |
| line-3 | line-3-0048-0314-s022669 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Kandy/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
