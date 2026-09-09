# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **157 trainsets at 28 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0937-0722-s000000 | forward | 4 | pending |
| line-1 | line-1-0862-0631-s003005 | forward | 4 | pending |
| line-1 | line-1-0862-0631-s003005 | reverse | 4 | pending |
| line-1 | line-1-0729-0598-s006019 | forward | 3 | pending |
| line-1 | line-1-0729-0598-s006019 | reverse | 3 | pending |
| line-1 | line-1-0626-0564-s009021 | forward | 3 | pending |
| line-1 | line-1-0626-0564-s009021 | reverse | 3 | pending |
| line-1 | line-1-0520-0523-s011770 | forward | 3 | pending |
| line-1 | line-1-0520-0523-s011770 | reverse | 3 | pending |
| line-1 | line-1-0472-0416-s015038 | forward | 3 | pending |
| line-1 | line-1-0472-0416-s015038 | reverse | 3 | pending |
| line-1 | line-1-0354-0388-s018044 | forward | 3 | pending |
| line-1 | line-1-0354-0388-s018044 | reverse | 3 | pending |
| line-1 | line-1-0245-0280-s021560 | forward | 3 | pending |
| line-1 | line-1-0245-0280-s021560 | reverse | 3 | pending |
| line-1 | line-1-0159-0155-s025062 | forward | 3 | pending |
| line-1 | line-1-0159-0155-s025062 | reverse | 3 | pending |
| line-1 | line-1-0082-0069-s027444 | forward | 3 | pending |
| line-1 | line-1-0082-0069-s027444 | reverse | 3 | pending |
| line-1 | line-1-0033-0102-s029827 | reverse | 3 | pending |
| line-2 | line-2-0027-0123-s000000 | forward | 4 | pending |
| line-2 | line-2-0085-0245-s003000 | forward | 4 | pending |
| line-2 | line-2-0085-0245-s003000 | reverse | 4 | pending |
| line-2 | line-2-0259-0462-s009821 | forward | 4 | pending |
| line-2 | line-2-0259-0462-s009821 | reverse | 4 | pending |
| line-2 | line-2-0325-0568-s012825 | forward | 3 | pending |
| line-2 | line-2-0325-0568-s012825 | reverse | 3 | pending |
| line-2 | line-2-0382-0683-s015841 | forward | 3 | pending |
| line-2 | line-2-0382-0683-s015841 | reverse | 3 | pending |
| line-2 | line-2-0466-0749-s018127 | forward | 3 | pending |
| line-2 | line-2-0466-0749-s018127 | reverse | 3 | pending |
| line-2 | line-2-0516-0837-s020421 | forward | 3 | pending |
| line-2 | line-2-0516-0837-s020421 | reverse | 3 | pending |
| line-2 | line-2-0551-0928-s022719 | reverse | 3 | pending |
| line-3 | line-3-0976-0350-s000000 | forward | 3 | pending |
| line-3 | line-3-0821-0456-s004290 | forward | 3 | pending |
| line-3 | line-3-0821-0456-s004290 | reverse | 3 | pending |
| line-3 | line-3-0697-0392-s007301 | forward | 3 | pending |
| line-3 | line-3-0697-0392-s007301 | reverse | 3 | pending |
| line-3 | line-3-0589-0472-s010302 | forward | 3 | pending |
| line-3 | line-3-0589-0472-s010302 | reverse | 3 | pending |
| line-3 | line-3-0520-0523-s013151 | forward | 3 | pending |
| line-3 | line-3-0520-0523-s013151 | reverse | 3 | pending |
| line-3 | line-3-0422-0549-s016333 | forward | 3 | pending |
| line-3 | line-3-0422-0549-s016333 | reverse | 3 | pending |
| line-3 | line-3-0331-0582-s018495 | forward | 3 | pending |
| line-3 | line-3-0331-0582-s018495 | reverse | 3 | pending |
| line-3 | line-3-0230-0597-s020639 | forward | 3 | pending |
| line-3 | line-3-0230-0597-s020639 | reverse | 3 | pending |
| line-3 | line-3-0196-0662-s022793 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Narayanganj/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
