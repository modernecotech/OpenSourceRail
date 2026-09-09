# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 19 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0535-0039-s000000 | forward | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | forward | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | reverse | 3 | pending |
| line-1 | line-1-0395-0276-s006008 | forward | 3 | pending |
| line-1 | line-1-0395-0276-s006008 | reverse | 3 | pending |
| line-1 | line-1-0380-0370-s008449 | forward | 3 | pending |
| line-1 | line-1-0380-0370-s008449 | reverse | 3 | pending |
| line-1 | line-1-0350-0476-s012022 | forward | 3 | pending |
| line-1 | line-1-0350-0476-s012022 | reverse | 3 | pending |
| line-1 | line-1-0392-0605-s014962 | reverse | 3 | pending |
| line-2 | line-2-0105-0497-s000000 | forward | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | forward | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | reverse | 3 | pending |
| line-2 | line-2-0306-0393-s005279 | forward | 3 | pending |
| line-2 | line-2-0306-0393-s005279 | reverse | 3 | pending |
| line-2 | line-2-0380-0370-s007313 | forward | 2 | pending |
| line-2 | line-2-0380-0370-s007313 | reverse | 2 | pending |
| line-2 | line-2-0445-0392-s009255 | forward | 2 | pending |
| line-2 | line-2-0445-0392-s009255 | reverse | 2 | pending |
| line-2 | line-2-0545-0386-s012078 | reverse | 2 | pending |
| line-3 | line-3-0133-0467-s000000 | forward | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | forward | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | reverse | 3 | pending |
| line-3 | line-3-0372-0336-s006451 | forward | 3 | pending |
| line-3 | line-3-0372-0336-s006451 | reverse | 3 | pending |
| line-3 | line-3-0380-0370-s007666 | forward | 2 | pending |
| line-3 | line-3-0380-0370-s007666 | reverse | 2 | pending |
| line-3 | line-3-0427-0322-s009462 | forward | 2 | pending |
| line-3 | line-3-0427-0322-s009462 | reverse | 2 | pending |
| line-3 | line-3-0457-0230-s011603 | forward | 2 | pending |
| line-3 | line-3-0457-0230-s011603 | reverse | 2 | pending |
| line-3 | line-3-0484-0136-s013763 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Namibe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
