# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **120 trainsets at 23 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0400-1089-s000000 | forward | 4 | pending |
| line-1 | line-1-0490-0810-s007023 | forward | 4 | pending |
| line-1 | line-1-0490-0810-s007023 | reverse | 4 | pending |
| line-1 | line-1-0556-0701-s010043 | forward | 4 | pending |
| line-1 | line-1-0556-0701-s010043 | reverse | 4 | pending |
| line-1 | line-1-0523-0598-s013069 | forward | 4 | pending |
| line-1 | line-1-0523-0598-s013069 | reverse | 3 | pending |
| line-1 | line-1-0543-0552-s015061 | forward | 3 | pending |
| line-1 | line-1-0543-0552-s015061 | reverse | 3 | pending |
| line-1 | line-1-0491-0520-s017070 | forward | 3 | pending |
| line-1 | line-1-0491-0520-s017070 | reverse | 3 | pending |
| line-1 | line-1-0432-0482-s019092 | forward | 3 | pending |
| line-1 | line-1-0432-0482-s019092 | reverse | 3 | pending |
| line-1 | line-1-0392-0381-s022051 | reverse | 3 | pending |
| line-2 | line-2-0869-0325-s000000 | forward | 3 | pending |
| line-2 | line-2-0693-0468-s004977 | forward | 3 | pending |
| line-2 | line-2-0693-0468-s004977 | reverse | 3 | pending |
| line-2 | line-2-0617-0519-s006919 | forward | 3 | pending |
| line-2 | line-2-0617-0519-s006919 | reverse | 3 | pending |
| line-2 | line-2-0543-0552-s008847 | forward | 3 | pending |
| line-2 | line-2-0543-0552-s008847 | reverse | 3 | pending |
| line-2 | line-2-0451-0579-s011279 | forward | 3 | pending |
| line-2 | line-2-0451-0579-s011279 | reverse | 3 | pending |
| line-2 | line-2-0388-0640-s013726 | forward | 3 | pending |
| line-2 | line-2-0388-0640-s013726 | reverse | 3 | pending |
| line-2 | line-2-0329-0733-s016169 | reverse | 3 | pending |
| line-3 | line-3-0885-0618-s000000 | forward | 3 | pending |
| line-3 | line-3-0711-0606-s003579 | forward | 3 | pending |
| line-3 | line-3-0711-0606-s003579 | reverse | 3 | pending |
| line-3 | line-3-0572-0591-s006583 | forward | 3 | pending |
| line-3 | line-3-0572-0591-s006583 | reverse | 3 | pending |
| line-3 | line-3-0543-0552-s007996 | forward | 3 | pending |
| line-3 | line-3-0543-0552-s007996 | reverse | 3 | pending |
| line-3 | line-3-0548-0496-s009584 | forward | 3 | pending |
| line-3 | line-3-0548-0496-s009584 | reverse | 2 | pending |
| line-3 | line-3-0449-0465-s012607 | forward | 2 | pending |
| line-3 | line-3-0449-0465-s012607 | reverse | 2 | pending |
| line-3 | line-3-0375-0462-s014711 | forward | 2 | pending |
| line-3 | line-3-0375-0462-s014711 | reverse | 2 | pending |
| line-3 | line-3-0357-0378-s016833 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Morogoro/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
