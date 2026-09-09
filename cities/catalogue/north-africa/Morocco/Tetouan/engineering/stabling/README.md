# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **115 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0584-0314-s000000 | forward | 4 | pending |
| line-1 | line-1-0572-0444-s003014 | forward | 4 | pending |
| line-1 | line-1-0572-0444-s003014 | reverse | 4 | pending |
| line-1 | line-1-0545-0562-s006168 | forward | 4 | pending |
| line-1 | line-1-0545-0562-s006168 | reverse | 3 | pending |
| line-1 | line-1-0458-0648-s009043 | forward | 3 | pending |
| line-1 | line-1-0458-0648-s009043 | reverse | 3 | pending |
| line-1 | line-1-0434-0761-s012062 | forward | 3 | pending |
| line-1 | line-1-0434-0761-s012062 | reverse | 3 | pending |
| line-1 | line-1-0382-0878-s015616 | forward | 3 | pending |
| line-1 | line-1-0382-0878-s015616 | reverse | 3 | pending |
| line-1 | line-1-0316-0975-s018551 | reverse | 3 | pending |
| line-2 | line-2-0327-0929-s000000 | forward | 4 | pending |
| line-2 | line-2-0513-0729-s006355 | forward | 4 | pending |
| line-2 | line-2-0513-0729-s006355 | reverse | 4 | pending |
| line-2 | line-2-0538-0619-s009378 | forward | 4 | pending |
| line-2 | line-2-0538-0619-s009378 | reverse | 4 | pending |
| line-2 | line-2-0545-0562-s011717 | forward | 4 | pending |
| line-2 | line-2-0545-0562-s011717 | reverse | 3 | pending |
| line-2 | line-2-0610-0519-s013994 | forward | 3 | pending |
| line-2 | line-2-0610-0519-s013994 | reverse | 3 | pending |
| line-2 | line-2-0639-0434-s016299 | forward | 3 | pending |
| line-2 | line-2-0639-0434-s016299 | reverse | 3 | pending |
| line-2 | line-2-0747-0414-s018625 | forward | 3 | pending |
| line-2 | line-2-0747-0414-s018625 | reverse | 3 | pending |
| line-2 | line-2-0929-0303-s023236 | reverse | 3 | pending |
| line-3 | line-3-0393-0182-s000000 | forward | 5 | pending |
| line-3 | line-3-0528-0407-s005752 | forward | 5 | pending |
| line-3 | line-3-0528-0407-s005752 | reverse | 5 | pending |
| line-3 | line-3-0545-0562-s009021 | forward | 4 | pending |
| line-3 | line-3-0545-0562-s009021 | reverse | 4 | pending |
| line-3 | line-3-0631-0656-s012267 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Tetouan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
