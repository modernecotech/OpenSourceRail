# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **190 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0146-0238-s000000 | forward | 7 | pending |
| line-1 | line-1-0358-0434-s007012 | forward | 7 | pending |
| line-1 | line-1-0358-0434-s007012 | reverse | 7 | pending |
| line-1 | line-1-0477-0472-s010023 | forward | 7 | pending |
| line-1 | line-1-0477-0472-s010023 | reverse | 7 | pending |
| line-1 | line-1-0565-0561-s012840 | forward | 7 | pending |
| line-1 | line-1-0565-0561-s012840 | reverse | 6 | pending |
| line-1 | line-1-0683-0594-s016455 | forward | 6 | pending |
| line-1 | line-1-0683-0594-s016455 | reverse | 6 | pending |
| line-1 | line-1-0970-0805-s025735 | forward | 6 | pending |
| line-1 | line-1-0970-0805-s025735 | reverse | 6 | pending |
| line-1 | line-1-1066-0823-s028462 | reverse | 6 | pending |
| line-2 | line-2-0695-0946-s000000 | forward | 5 | pending |
| line-2 | line-2-0610-0671-s007026 | forward | 5 | pending |
| line-2 | line-2-0610-0671-s007026 | reverse | 5 | pending |
| line-2 | line-2-0543-0610-s010033 | forward | 5 | pending |
| line-2 | line-2-0543-0610-s010033 | reverse | 5 | pending |
| line-2 | line-2-0565-0561-s011588 | forward | 5 | pending |
| line-2 | line-2-0565-0561-s011588 | reverse | 4 | pending |
| line-2 | line-2-0577-0501-s013039 | forward | 4 | pending |
| line-2 | line-2-0577-0501-s013039 | reverse | 4 | pending |
| line-2 | line-2-0475-0427-s015934 | forward | 4 | pending |
| line-2 | line-2-0475-0427-s015934 | reverse | 4 | pending |
| line-2 | line-2-0365-0369-s018823 | reverse | 4 | pending |
| line-3 | line-3-0912-0331-s000000 | forward | 6 | pending |
| line-3 | line-3-0635-0464-s006912 | forward | 6 | pending |
| line-3 | line-3-0635-0464-s006912 | reverse | 6 | pending |
| line-3 | line-3-0565-0561-s010076 | forward | 6 | pending |
| line-3 | line-3-0565-0561-s010076 | reverse | 6 | pending |
| line-3 | line-3-0484-0619-s012934 | forward | 6 | pending |
| line-3 | line-3-0484-0619-s012934 | reverse | 6 | pending |
| line-3 | line-3-0409-0773-s017204 | forward | 6 | pending |
| line-3 | line-3-0409-0773-s017204 | reverse | 5 | pending |
| line-3 | line-3-0244-0849-s021464 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Fayoum/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
