# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **125 trainsets at 24 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0237-0086-s000000 | forward | 3 | pending |
| line-1 | line-1-0339-0312-s006062 | forward | 3 | pending |
| line-1 | line-1-0339-0312-s006062 | reverse | 3 | pending |
| line-1 | line-1-0425-0412-s009080 | forward | 3 | pending |
| line-1 | line-1-0425-0412-s009080 | reverse | 3 | pending |
| line-1 | line-1-0507-0409-s012094 | forward | 3 | pending |
| line-1 | line-1-0507-0409-s012094 | reverse | 3 | pending |
| line-1 | line-1-0535-0494-s014144 | forward | 3 | pending |
| line-1 | line-1-0535-0494-s014144 | reverse | 3 | pending |
| line-1 | line-1-0543-0556-s016183 | forward | 3 | pending |
| line-1 | line-1-0543-0556-s016183 | reverse | 3 | pending |
| line-1 | line-1-0597-0601-s018112 | forward | 3 | pending |
| line-1 | line-1-0597-0601-s018112 | reverse | 3 | pending |
| line-1 | line-1-0644-0690-s021115 | forward | 3 | pending |
| line-1 | line-1-0644-0690-s021115 | reverse | 3 | pending |
| line-1 | line-1-0681-0770-s023146 | reverse | 3 | pending |
| line-2 | line-2-0948-0862-s000000 | forward | 3 | pending |
| line-2 | line-2-0846-0854-s003512 | forward | 3 | pending |
| line-2 | line-2-0846-0854-s003512 | reverse | 3 | pending |
| line-2 | line-2-0737-0802-s007020 | forward | 3 | pending |
| line-2 | line-2-0737-0802-s007020 | reverse | 3 | pending |
| line-2 | line-2-0681-0771-s008628 | forward | 3 | pending |
| line-2 | line-2-0681-0771-s008628 | reverse | 3 | pending |
| line-2 | line-2-0580-0733-s011631 | forward | 3 | pending |
| line-2 | line-2-0580-0733-s011631 | reverse | 3 | pending |
| line-2 | line-2-0525-0661-s013871 | forward | 3 | pending |
| line-2 | line-2-0525-0661-s013871 | reverse | 3 | pending |
| line-2 | line-2-0406-0630-s016897 | forward | 3 | pending |
| line-2 | line-2-0406-0630-s016897 | reverse | 3 | pending |
| line-2 | line-2-0319-0639-s019967 | reverse | 2 | pending |
| line-3 | line-3-0430-0815-s000000 | forward | 3 | pending |
| line-3 | line-3-0480-0707-s003003 | forward | 3 | pending |
| line-3 | line-3-0480-0707-s003003 | reverse | 3 | pending |
| line-3 | line-3-0513-0642-s004605 | forward | 3 | pending |
| line-3 | line-3-0513-0642-s004605 | reverse | 3 | pending |
| line-3 | line-3-0543-0556-s006997 | forward | 3 | pending |
| line-3 | line-3-0543-0556-s006997 | reverse | 3 | pending |
| line-3 | line-3-0545-0423-s010632 | forward | 3 | pending |
| line-3 | line-3-0545-0423-s010632 | reverse | 3 | pending |
| line-3 | line-3-0488-0304-s013639 | forward | 3 | pending |
| line-3 | line-3-0488-0304-s013639 | reverse | 3 | pending |
| line-3 | line-3-0392-0261-s016813 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Goma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
