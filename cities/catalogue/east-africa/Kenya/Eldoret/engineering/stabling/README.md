# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **163 trainsets at 17 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0733-0710-s000000 | forward | 7 | pending |
| line-1 | line-1-0655-0615-s003317 | forward | 7 | pending |
| line-1 | line-1-0655-0615-s003317 | reverse | 7 | pending |
| line-1 | line-1-0548-0553-s006188 | forward | 6 | pending |
| line-1 | line-1-0548-0553-s006188 | reverse | 6 | pending |
| line-1 | line-1-0470-0523-s009329 | forward | 6 | pending |
| line-1 | line-1-0470-0523-s009329 | reverse | 6 | pending |
| line-1 | line-1-0385-0435-s012332 | forward | 6 | pending |
| line-1 | line-1-0385-0435-s012332 | reverse | 6 | pending |
| line-1 | line-1-0160-0039-s022574 | reverse | 6 | pending |
| line-2 | line-2-0456-0775-s000000 | forward | 5 | pending |
| line-2 | line-2-0539-0664-s003007 | forward | 5 | pending |
| line-2 | line-2-0539-0664-s003007 | reverse | 5 | pending |
| line-2 | line-2-0548-0553-s005680 | forward | 5 | pending |
| line-2 | line-2-0548-0553-s005680 | reverse | 5 | pending |
| line-2 | line-2-0602-0481-s007635 | forward | 5 | pending |
| line-2 | line-2-0602-0481-s007635 | reverse | 5 | pending |
| line-2 | line-2-0730-0215-s014309 | reverse | 4 | pending |
| line-3 | line-3-0056-0021-s000000 | forward | 7 | pending |
| line-3 | line-3-0345-0410-s011200 | forward | 6 | pending |
| line-3 | line-3-0345-0410-s011200 | reverse | 6 | pending |
| line-3 | line-3-0480-0445-s014206 | forward | 6 | pending |
| line-3 | line-3-0480-0445-s014206 | reverse | 6 | pending |
| line-3 | line-3-0548-0553-s017061 | forward | 6 | pending |
| line-3 | line-3-0548-0553-s017061 | reverse | 6 | pending |
| line-3 | line-3-0580-0661-s019586 | forward | 6 | pending |
| line-3 | line-3-0580-0661-s019586 | reverse | 6 | pending |
| line-3 | line-3-0601-0747-s022099 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Eldoret/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
