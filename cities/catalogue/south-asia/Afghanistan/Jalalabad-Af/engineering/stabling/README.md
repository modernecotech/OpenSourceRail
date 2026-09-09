# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **112 trainsets at 16 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0798-0565-s000000 | forward | 4 | pending |
| line-1 | line-1-0691-0599-s004454 | forward | 4 | pending |
| line-1 | line-1-0691-0599-s004454 | reverse | 4 | pending |
| line-1 | line-1-0601-0598-s006362 | forward | 4 | pending |
| line-1 | line-1-0601-0598-s006362 | reverse | 4 | pending |
| line-1 | line-1-0552-0553-s008251 | forward | 3 | pending |
| line-1 | line-1-0552-0553-s008251 | reverse | 3 | pending |
| line-1 | line-1-0399-0533-s011848 | reverse | 3 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | 5 | pending |
| line-2 | line-2-0673-0733-s003998 | forward | 5 | pending |
| line-2 | line-2-0673-0733-s003998 | reverse | 5 | pending |
| line-2 | line-2-0574-0641-s007022 | forward | 5 | pending |
| line-2 | line-2-0574-0641-s007022 | reverse | 5 | pending |
| line-2 | line-2-0552-0553-s009163 | forward | 5 | pending |
| line-2 | line-2-0552-0553-s009163 | reverse | 5 | pending |
| line-2 | line-2-0460-0316-s015062 | forward | 5 | pending |
| line-2 | line-2-0460-0316-s015062 | reverse | 5 | pending |
| line-2 | line-2-0286-0151-s020965 | reverse | 4 | pending |
| line-3 | line-3-0320-0781-s000000 | forward | 5 | pending |
| line-3 | line-3-0437-0609-s004940 | forward | 5 | pending |
| line-3 | line-3-0437-0609-s004940 | reverse | 4 | pending |
| line-3 | line-3-0552-0553-s008134 | forward | 4 | pending |
| line-3 | line-3-0552-0553-s008134 | reverse | 4 | pending |
| line-3 | line-3-0651-0543-s010969 | forward | 4 | pending |
| line-3 | line-3-0651-0543-s010969 | reverse | 4 | pending |
| line-3 | line-3-0764-0482-s014179 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Jalalabad-Af/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
