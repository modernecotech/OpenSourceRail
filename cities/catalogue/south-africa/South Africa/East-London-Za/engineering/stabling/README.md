# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **139 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0250-0950-s000000 | forward | 3 | pending |
| line-1 | line-1-0295-0853-s003002 | forward | 3 | pending |
| line-1 | line-1-0295-0853-s003002 | reverse | 3 | pending |
| line-1 | line-1-0409-0795-s006023 | forward | 3 | pending |
| line-1 | line-1-0409-0795-s006023 | reverse | 3 | pending |
| line-1 | line-1-0395-0730-s007970 | forward | 3 | pending |
| line-1 | line-1-0395-0730-s007970 | reverse | 3 | pending |
| line-1 | line-1-0411-0668-s010987 | forward | 3 | pending |
| line-1 | line-1-0411-0668-s010987 | reverse | 3 | pending |
| line-1 | line-1-0510-0567-s014588 | forward | 3 | pending |
| line-1 | line-1-0510-0567-s014588 | reverse | 3 | pending |
| line-1 | line-1-0587-0545-s017008 | forward | 3 | pending |
| line-1 | line-1-0587-0545-s017008 | reverse | 3 | pending |
| line-1 | line-1-0676-0516-s020018 | forward | 3 | pending |
| line-1 | line-1-0676-0516-s020018 | reverse | 3 | pending |
| line-1 | line-1-0778-0438-s023067 | reverse | 3 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | 4 | pending |
| line-2 | line-2-0548-0772-s001936 | forward | 4 | pending |
| line-2 | line-2-0548-0772-s001936 | reverse | 4 | pending |
| line-2 | line-2-0583-0691-s003846 | forward | 4 | pending |
| line-2 | line-2-0583-0691-s003846 | reverse | 4 | pending |
| line-2 | line-2-0510-0567-s007027 | forward | 4 | pending |
| line-2 | line-2-0510-0567-s007027 | reverse | 3 | pending |
| line-2 | line-2-0426-0496-s009866 | forward | 3 | pending |
| line-2 | line-2-0426-0496-s009866 | reverse | 3 | pending |
| line-2 | line-2-0294-0406-s013380 | forward | 3 | pending |
| line-2 | line-2-0294-0406-s013380 | reverse | 3 | pending |
| line-2 | line-2-0201-0299-s016881 | forward | 3 | pending |
| line-2 | line-2-0201-0299-s016881 | reverse | 3 | pending |
| line-2 | line-2-0000-0177-s023239 | reverse | 3 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | 5 | pending |
| line-3 | line-3-0185-0375-s006866 | forward | 5 | pending |
| line-3 | line-3-0185-0375-s006866 | reverse | 5 | pending |
| line-3 | line-3-0209-0502-s009877 | forward | 4 | pending |
| line-3 | line-3-0209-0502-s009877 | reverse | 4 | pending |
| line-3 | line-3-0225-0639-s012882 | forward | 4 | pending |
| line-3 | line-3-0225-0639-s012882 | reverse | 4 | pending |
| line-3 | line-3-0270-0761-s015892 | forward | 4 | pending |
| line-3 | line-3-0270-0761-s015892 | reverse | 4 | pending |
| line-3 | line-3-0308-0981-s021177 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/East-London-Za/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
