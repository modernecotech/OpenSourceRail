# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **158 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0332-0510-s000000 | forward | 4 | pending |
| line-1 | line-1-0421-0541-s003019 | forward | 4 | pending |
| line-1 | line-1-0421-0541-s003019 | reverse | 4 | pending |
| line-1 | line-1-0496-0503-s005094 | forward | 4 | pending |
| line-1 | line-1-0496-0503-s005094 | reverse | 4 | pending |
| line-1 | line-1-0555-0548-s007179 | forward | 4 | pending |
| line-1 | line-1-0555-0548-s007179 | reverse | 4 | pending |
| line-1 | line-1-0617-0572-s009059 | forward | 3 | pending |
| line-1 | line-1-0617-0572-s009059 | reverse | 3 | pending |
| line-1 | line-1-0678-0485-s012080 | forward | 3 | pending |
| line-1 | line-1-0678-0485-s012080 | reverse | 3 | pending |
| line-1 | line-1-0790-0520-s015107 | forward | 3 | pending |
| line-1 | line-1-0790-0520-s015107 | reverse | 3 | pending |
| line-1 | line-1-1086-0483-s023031 | reverse | 3 | pending |
| line-2 | line-2-0248-0064-s000000 | forward | 4 | pending |
| line-2 | line-2-0393-0335-s007025 | forward | 4 | pending |
| line-2 | line-2-0393-0335-s007025 | reverse | 4 | pending |
| line-2 | line-2-0469-0412-s010046 | forward | 4 | pending |
| line-2 | line-2-0469-0412-s010046 | reverse | 4 | pending |
| line-2 | line-2-0567-0468-s013059 | forward | 4 | pending |
| line-2 | line-2-0567-0468-s013059 | reverse | 4 | pending |
| line-2 | line-2-0555-0548-s015770 | forward | 4 | pending |
| line-2 | line-2-0555-0548-s015770 | reverse | 4 | pending |
| line-2 | line-2-0513-0661-s018531 | forward | 4 | pending |
| line-2 | line-2-0513-0661-s018531 | reverse | 3 | pending |
| line-2 | line-2-0552-0766-s021289 | forward | 3 | pending |
| line-2 | line-2-0552-0766-s021289 | reverse | 3 | pending |
| line-2 | line-2-0581-0875-s024042 | reverse | 3 | pending |
| line-3 | line-3-0486-0828-s000000 | forward | 5 | pending |
| line-3 | line-3-0465-0671-s004019 | forward | 5 | pending |
| line-3 | line-3-0465-0671-s004019 | reverse | 5 | pending |
| line-3 | line-3-0508-0597-s006017 | forward | 5 | pending |
| line-3 | line-3-0508-0597-s006017 | reverse | 5 | pending |
| line-3 | line-3-0555-0548-s008022 | forward | 5 | pending |
| line-3 | line-3-0555-0548-s008022 | reverse | 5 | pending |
| line-3 | line-3-0602-0482-s010025 | forward | 5 | pending |
| line-3 | line-3-0602-0482-s010025 | reverse | 5 | pending |
| line-3 | line-3-0721-0400-s013527 | forward | 4 | pending |
| line-3 | line-3-0721-0400-s013527 | reverse | 4 | pending |
| line-3 | line-3-1046-0061-s026438 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bafoussam/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
