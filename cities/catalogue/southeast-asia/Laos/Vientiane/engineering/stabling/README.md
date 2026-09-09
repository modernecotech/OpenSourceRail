# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **155 trainsets at 26 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0216-1056-s000000 | forward | 3 | pending |
| line-1 | line-1-0290-0992-s003013 | forward | 3 | pending |
| line-1 | line-1-0290-0992-s003013 | reverse | 3 | pending |
| line-1 | line-1-0307-0865-s006020 | forward | 3 | pending |
| line-1 | line-1-0307-0865-s006020 | reverse | 3 | pending |
| line-1 | line-1-0428-0802-s009020 | forward | 3 | pending |
| line-1 | line-1-0428-0802-s009020 | reverse | 3 | pending |
| line-1 | line-1-0515-0722-s012701 | forward | 3 | pending |
| line-1 | line-1-0515-0722-s012701 | reverse | 3 | pending |
| line-1 | line-1-0561-0663-s014705 | forward | 3 | pending |
| line-1 | line-1-0561-0663-s014705 | reverse | 3 | pending |
| line-1 | line-1-0644-0663-s016695 | forward | 3 | pending |
| line-1 | line-1-0644-0663-s016695 | reverse | 3 | pending |
| line-1 | line-1-0755-0710-s019709 | forward | 3 | pending |
| line-1 | line-1-0755-0710-s019709 | reverse | 3 | pending |
| line-1 | line-1-0890-0663-s023314 | reverse | 3 | pending |
| line-2 | line-2-0101-0902-s000000 | forward | 3 | pending |
| line-2 | line-2-0235-0871-s003305 | forward | 3 | pending |
| line-2 | line-2-0235-0871-s003305 | reverse | 3 | pending |
| line-2 | line-2-0278-0771-s006312 | forward | 3 | pending |
| line-2 | line-2-0278-0771-s006312 | reverse | 3 | pending |
| line-2 | line-2-0390-0719-s009327 | forward | 3 | pending |
| line-2 | line-2-0390-0719-s009327 | reverse | 3 | pending |
| line-2 | line-2-0515-0722-s012340 | forward | 3 | pending |
| line-2 | line-2-0515-0722-s012340 | reverse | 3 | pending |
| line-2 | line-2-0545-0635-s015345 | forward | 3 | pending |
| line-2 | line-2-0545-0635-s015345 | reverse | 3 | pending |
| line-2 | line-2-0666-0579-s018367 | forward | 3 | pending |
| line-2 | line-2-0666-0579-s018367 | reverse | 3 | pending |
| line-2 | line-2-0706-0501-s020809 | forward | 3 | pending |
| line-2 | line-2-0706-0501-s020809 | reverse | 3 | pending |
| line-2 | line-2-0789-0457-s023245 | reverse | 3 | pending |
| line-3 | line-3-0197-0196-s000000 | forward | 5 | pending |
| line-3 | line-3-0397-0429-s007018 | forward | 5 | pending |
| line-3 | line-3-0397-0429-s007018 | reverse | 5 | pending |
| line-3 | line-3-0357-0543-s010038 | forward | 4 | pending |
| line-3 | line-3-0357-0543-s010038 | reverse | 4 | pending |
| line-3 | line-3-0457-0620-s013061 | forward | 4 | pending |
| line-3 | line-3-0457-0620-s013061 | reverse | 4 | pending |
| line-3 | line-3-0515-0722-s015986 | forward | 4 | pending |
| line-3 | line-3-0515-0722-s015986 | reverse | 4 | pending |
| line-3 | line-3-0637-0734-s019081 | forward | 4 | pending |
| line-3 | line-3-0637-0734-s019081 | reverse | 4 | pending |
| line-3 | line-3-0727-0834-s022085 | forward | 4 | pending |
| line-3 | line-3-0727-0834-s022085 | reverse | 4 | pending |
| line-3 | line-3-0905-0994-s027841 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/southeast-asia/Laos/Vientiane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
