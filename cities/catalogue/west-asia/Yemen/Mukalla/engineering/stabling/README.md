# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **152 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0857-0110-s000000 | forward | 4 | pending |
| line-1 | line-1-0834-0200-s003510 | forward | 4 | pending |
| line-1 | line-1-0834-0200-s003510 | reverse | 4 | pending |
| line-1 | line-1-0628-0446-s010218 | forward | 4 | pending |
| line-1 | line-1-0628-0446-s010218 | reverse | 4 | pending |
| line-1 | line-1-0611-0547-s012429 | forward | 4 | pending |
| line-1 | line-1-0611-0547-s012429 | reverse | 4 | pending |
| line-1 | line-1-0562-0538-s015240 | forward | 4 | pending |
| line-1 | line-1-0562-0538-s015240 | reverse | 4 | pending |
| line-1 | line-1-0503-0562-s017210 | forward | 4 | pending |
| line-1 | line-1-0503-0562-s017210 | reverse | 4 | pending |
| line-1 | line-1-0462-0618-s019192 | reverse | 4 | pending |
| line-2 | line-2-0668-0713-s000000 | forward | 7 | pending |
| line-2 | line-2-0656-0592-s003014 | forward | 7 | pending |
| line-2 | line-2-0656-0592-s003014 | reverse | 7 | pending |
| line-2 | line-2-0720-0444-s006504 | forward | 7 | pending |
| line-2 | line-2-0720-0444-s006504 | reverse | 6 | pending |
| line-2 | line-2-0946-0071-s016453 | reverse | 6 | pending |
| line-3 | line-3-0414-1035-s000000 | forward | 6 | pending |
| line-3 | line-3-0543-0764-s007019 | forward | 6 | pending |
| line-3 | line-3-0543-0764-s007019 | reverse | 6 | pending |
| line-3 | line-3-0543-0614-s010019 | forward | 6 | pending |
| line-3 | line-3-0543-0614-s010019 | reverse | 5 | pending |
| line-3 | line-3-0562-0538-s012389 | forward | 5 | pending |
| line-3 | line-3-0562-0538-s012389 | reverse | 5 | pending |
| line-3 | line-3-0591-0463-s014306 | forward | 5 | pending |
| line-3 | line-3-0591-0463-s014306 | reverse | 5 | pending |
| line-3 | line-3-0626-0382-s016216 | forward | 5 | pending |
| line-3 | line-3-0626-0382-s016216 | reverse | 5 | pending |
| line-3 | line-3-0888-0083-s025965 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Mukalla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
