# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **87 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0517-0336-s000000 | forward | 3 | pending |
| line-1 | line-1-0568-0338-s001954 | forward | 3 | pending |
| line-1 | line-1-0568-0338-s001954 | reverse | 3 | pending |
| line-1 | line-1-0563-0423-s003928 | forward | 3 | pending |
| line-1 | line-1-0563-0423-s003928 | reverse | 3 | pending |
| line-1 | line-1-0592-0495-s006007 | forward | 3 | pending |
| line-1 | line-1-0592-0495-s006007 | reverse | 2 | pending |
| line-1 | line-1-0614-0565-s008069 | forward | 2 | pending |
| line-1 | line-1-0614-0565-s008069 | reverse | 2 | pending |
| line-1 | line-1-0669-0645-s010737 | forward | 2 | pending |
| line-1 | line-1-0669-0645-s010737 | reverse | 2 | pending |
| line-1 | line-1-0761-0719-s013401 | reverse | 2 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | forward | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | reverse | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | forward | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | reverse | 3 | pending |
| line-2 | line-2-0614-0565-s007472 | forward | 3 | pending |
| line-2 | line-2-0614-0565-s007472 | reverse | 3 | pending |
| line-2 | line-2-0529-0610-s009613 | forward | 2 | pending |
| line-2 | line-2-0529-0610-s009613 | reverse | 2 | pending |
| line-2 | line-2-0476-0688-s011760 | reverse | 2 | pending |
| line-3 | line-3-0276-0370-s000000 | forward | 4 | pending |
| line-3 | line-3-0473-0484-s005686 | forward | 4 | pending |
| line-3 | line-3-0473-0484-s005686 | reverse | 4 | pending |
| line-3 | line-3-0542-0523-s007703 | forward | 4 | pending |
| line-3 | line-3-0542-0523-s007703 | reverse | 4 | pending |
| line-3 | line-3-0614-0565-s009710 | forward | 4 | pending |
| line-3 | line-3-0614-0565-s009710 | reverse | 3 | pending |
| line-3 | line-3-0643-0792-s014803 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Homs/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
